"""PreToolUse hook blocking Python string literals with a Windows path escape
outside a raw string. Sprint 10 retrospective improvement 1.

Converted 2026-09-14 from block-unraw-escape.ps1.

This failure has recurred five-plus times across sprints, twice in Sprint 10
alone. The shape is always the same: a heredoc'd Python snippet contains a
Windows path in a normal quoted string, e.g.

    p = 'D:\\Data\\Harold\\...'

Python reads \\D as an invalid escape (SyntaxWarning today, SyntaxError in a
future version) and \\x, \\u, \\N as hard errors. In Sprint 10 it produced a
silent wrong value once (a \\b became a backspace inside a JSON path, writing
the file to the wrong directory) and an outright crash twice.

A rule against it already exists and has not worked, because it depends on
remembering at the moment of writing. The sibling hooks (block-carry-forward-
stash, block-branch-from-develop) demonstrate that the mechanical check
succeeds where the remembered rule fails. This is the same treatment for the
same class of problem.

THE FIX IS ALWAYS THE SAME: prefix the literal with r, or use forward slashes.
Both are one keystroke.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_unraw_escape, for the rare case where the escape
is deliberate (writing an actual tab or newline into a path string).
Only inspects python heredocs, so shell strings and prose are untouched.
"""
from __future__ import annotations

import json
import re
import sys

# Anchor on an actual INVOCATION, not the bare substring. A bare substring
# test turns the scanner on for any command merely containing those letters:
# a path like C:/Python312/..., a filename test_python_paths.sh, `pip show
# python-dateutil`, or prose. During review of PR #58 it blocked a `gh api`
# call whose only Python content was example text inside the comment being
# posted.
PYTHON_INVOCATION = re.compile(r"(?:^|[\s;&|(])python[0-9.]*(?:\.exe)?(?:\s|$)")

# EXACT Python string prefixes only. A substring test over an [A-Za-z]*
# capture lets an adjacent identifier ending in r -- str'...', dir'...',
# ptr'...' -- silence the block.
VALID_PREFIX = re.compile(r"(?i)^(?:r|rb|br|rf|fr)$")
QUOTED_LITERAL = re.compile(r"(?P<prefix>[A-Za-z]*)(?P<q>['\"])(?P<body>[^'\"]*)(?P=q)")
DRIVE_PATH = re.compile(r"[A-Za-z]:\\[A-Za-z]")


def _read_command() -> str:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""

    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    if isinstance(tool_input, dict) and tool_input.get("command"):
        return str(tool_input["command"])
    if isinstance(payload, dict) and payload.get("command"):
        return str(payload["command"])
    return ""


def main() -> int:
    try:
        cmd = _read_command()
    except Exception:
        return 0  # fail open on malformed payload

    if not cmd or not cmd.strip():
        return 0
    if "allow_unraw_escape" in cmd:
        return 0

    # Only look at commands that actually run python.
    if not PYTHON_INVOCATION.search(cmd):
        return 0

    # Only a DRIVE-LETTER path is unambiguous enough to block on. Legitimate
    # newline and tab escapes, and raw strings, must pass untouched: a hook
    # that blocks the correct fix is worse than no hook.
    bad: list[str] = []

    for line in cmd.split("\n"):
        if line.strip().startswith("#"):
            continue

        for m in QUOTED_LITERAL.finditer(line):
            if VALID_PREFIX.match(m.group("prefix")):
                continue
            body = m.group("body")
            probe = body.replace("\\\\", "")
            if DRIVE_PATH.search(probe):
                bad.append(m.group(0))

    if bad:
        sample = "\n    ".join(bad[:3])
        print(
            "[BLOCKED] Python string with an unescaped Windows path (Sprint 10 retro item 1).\n"
            "\n"
            "Found:\n"
            f"    {sample}\n"
            "\n"
            "Python reads \\D, \\H, \\U as invalid escapes and \\b, \\x, \\n as real control\n"
            "characters, so this either warns, crashes, or -- worst -- silently produces the\n"
            "wrong value. In Sprint 10 a \\b inside a path became a backspace and wrote a\n"
            "file to the wrong directory; the JSON looked fine.\n"
            "\n"
            "FIX, one keystroke either way:\n"
            "    r'D:\\Data\\Harold\\...'      <- raw string, preferred\n"
            "    'D:/Data/Harold/...'       <- forward slashes work on Windows\n"
            "\n"
            "This has recurred five-plus times, twice in this sprint. The rule existed and\n"
            "did not hold, which is why it is now mechanical.\n"
            "\n"
            "If the escape is genuinely intended, re-run with the literal token\n"
            "allow_unraw_escape in the command.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
