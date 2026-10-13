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
The escape check inspects only commands that run python.

Also blocks, on any command, a shell edit of a repository code file
(`sed -i`, `perl -i`, a redirect or `tee`, PowerShell Set-Content and its
kin onto a .py or .sql file; Sprint 8 retrospective I5). Bypass: the
literal token allow_shell_code_edit.
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

# A REAL drive-letter path: a SINGLE letter, a colon, a backslash, a letter.
# The leading letter must not be part of a longer word.
#
# Sprint 4 retrospective improvement 5. The previous pattern was
# `[A-Za-z]:\\[A-Za-z]`, which matches any letter-colon-backslash-letter, so
# ordinary prose ending in a colon before an escape matched on its last
# letter: "CITATION.cff:\n" matched as `f:\n`, "        if found:\n" as
# `d:\n`. Two legitimate commands carrying no Windows path at all were
# blocked that way in Sprint 4, and the block is mechanical, so there was no
# way past it except the bypass token. Diagnosed 2026-09-22 by printing the
# literal the hook flagged in each case, after two wrong guesses about the
# cause (a quote-boundary bug, then a segment-scoping bug); the evidence is
# what narrowed it, not the reasoning about it.
DRIVE_PATH = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\[A-Za-z]")


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


# Sprint 5 retrospective improvement 2 (2026-09-25): the same class, one step
# on. Python source written THROUGH a Python string inside a shell command
# (`p='scripts/x.py'; s=open(p).read(); ...; open(p,'w').write(s)`) passes
# every escape through two interpreters. Sprint 5 broke files that way three
# times: a "\\n" meant for the target file became a real line break and left
# an unterminated string literal, found only when the file failed to parse.
# The Edit and Write tools take code verbatim and cannot do this.
PY_FILE_LITERAL = re.compile(r"""['"][^'"\n]*\.py['"]""")
WRITES_FILE = re.compile(r"""open\([^)]*['"]w['"]|\.write_text\(|\.write\(""")


def _writes_python_source(cmd: str) -> bool:
    return bool(PY_FILE_LITERAL.search(cmd) and WRITES_FILE.search(cmd))


# Sprint 8 retrospective I5 (2026-10-13): the same class, without Python.
# Two code lines were changed with `sed -i` in Sprint 8, against the rule
# that code files change only through Edit and Write (which show the change
# and take the text verbatim). The rule existed and was broken once, so it
# is now mechanical: an in-place `sed`/`perl`, a shell redirect or `tee`, or
# a PowerShell Set-Content/Add-Content/Out-File onto a repository .py or
# .sql file is blocked. Data is not scanned: heredoc bodies (a commit
# message, a script fed to python) and the quoted text of a -m, --message,
# --body, --title or --notes argument. A scratch file outside the
# repository is not blocked, nor is a relative path after a `cd` to a
# directory outside it.
#
# Fresh-eyes review of 2026-10-13 (seven shapes, each now in the tests): a
# `<<<` here-string opened a heredoc that never closed and hid every later
# line; sed after `xargs`, `env` or `bash -c "` escaped; `-0pi` escaped;
# `1>` and `&>` escaped; Set-Content's span ran past `;` and `|` onto a
# later .py; a `git commit -m` message was scanned; a `cd` out of the
# repository was ignored.
HEREDOC_START = re.compile(r"(?<!<)<<(?!<)-?\s*['\"]?([A-Za-z_]\w*)['\"]?")
IN_PLACE_TOOL = re.compile(r"(?:^|[;&|(\"'`]|\b(?:xargs|env|sudo|exec|command)\s+(?:-\S+\s+|\S+=\S*\s+)*)\s*"
                           r"(?:sed|perl)\s(?P<rest>.*)")
IN_PLACE_FLAG = re.compile(r"(?:^|\s)(?:-[A-Za-z0-9]*i[A-Za-z0-9.]*|--in-place\S*)(?=\s|$)")
CODE_PATH = r"""['"]?(?P<path>[^\s'"<>|;&]+\.(?:py|sql))['"]?(?=$|[\s;&|)])"""
CODE_ARG = re.compile(r"(?:^|\s)" + CODE_PATH)
_PS_WRITE = r"\b(?:Set-Content|Add-Content|Out-File)\b"
_PS_PATH = r"-(?:Path|FilePath|LiteralPath)(?:\s+|:)"
# The target of a PowerShell write is its first positional argument or its
# -Path value, never any .py named later on the line.
REDIRECT_ONTO = re.compile(r"(?:(?<![0-9>])[1&]?>>?|\btee\s+(?:-a\s+)?|"
                           rf"{_PS_WRITE}(?:\s+{_PS_PATH})?\s|{_PS_WRITE}[^\n;|&]*?\s{_PS_PATH})\s*" + CODE_PATH)
MESSAGE_ARG = re.compile(r"""(?:^|\s)(?:-m|--message|--body|--title|--notes)[\s=]+(?:"(?:[^"\\]|\\.)*"|'[^']*')""")
CD_TO = re.compile(r"""(?:^|[;&|(])\s*(?:cd|Set-Location|pushd)\s+['"]?([^\s'";&|]+)""")


def _without_heredoc_bodies(cmd: str) -> list[str]:
    lines, tag, body = [], None, []
    for line in cmd.split("\n"):
        if tag is not None:
            if line.strip() == tag:
                tag, body = None, []
            else:
                body.append(line)
            continue
        lines.append(line)
        m = HEREDOC_START.search(line)
        if m:
            tag = m.group(1)
    # A heredoc that never closes was not one (a quoted `<<` in prose, say):
    # its "body" is command text and is scanned.
    return lines + body


def _in_repository(path: str, outside_cwd: bool = False) -> bool:
    p = path.replace("\\", "/")
    if "CLAUDE_PROJECT_DIR" in p or "github/evidencebaseddb/" in p.lower().rstrip("/") + "/":
        return True
    return not outside_cwd and not re.match(r"^(?:[A-Za-z]:/|/|~|\$)", p)


def _shell_edits_code(cmd: str) -> list[str]:
    hits = []
    lines = [MESSAGE_ARG.sub(" ''", line) for line in _without_heredoc_bodies(cmd)]
    outside = any(not _in_repository(d) for line in lines for d in CD_TO.findall(line)
                  if re.match(r"^(?:[A-Za-z]:[\\/]|/|~)", d))
    for line in lines:
        tool = IN_PLACE_TOOL.search(line)
        if tool and IN_PLACE_FLAG.search(tool.group("rest")):
            hits += [m.group("path") for m in CODE_ARG.finditer(tool.group("rest"))
                     if _in_repository(m.group("path"), outside)]
        hits += [m.group("path") for m in REDIRECT_ONTO.finditer(line) if _in_repository(m.group("path"), outside)]
    return hits


def main() -> int:
    try:
        cmd = _read_command()
    except Exception:
        return 0  # fail open on malformed payload

    if not cmd or not cmd.strip():
        return 0

    runs_python = PYTHON_INVOCATION.search(cmd)

    if runs_python and "allow_python_writes_code" not in cmd and _writes_python_source(cmd):
        print(
            "[BLOCKED] Python code rewriting a .py file from inside a shell command\n"
            "(Sprint 5 retrospective improvement 2).\n"
            "\n"
            "Escapes pass through two interpreters here: a \"\\n\" meant for the target file\n"
            "becomes a real line break and leaves an unterminated string. Sprint 5 broke\n"
            "three files this way.\n"
            "\n"
            "FIX: change code files with the Edit tool (or Write for a new file); they take\n"
            "the text verbatim. Keep python heredocs for data and prose files.\n"
            "\n"
            "If a script genuinely must write a .py file, re-run with the literal token\n"
            "allow_python_writes_code in the command.",
            file=sys.stderr,
        )
        return 2

    edited = [] if "allow_shell_code_edit" in cmd else _shell_edits_code(cmd)
    if edited:
        print(
            "[BLOCKED] A shell command editing a repository code file (Sprint 8 retrospective I5):\n"
            f"    {', '.join(edited[:3])}\n"
            "\n"
            "Code files change only through the Edit tool (or Write for a new file), which\n"
            "shows the change and takes the text verbatim. Sprint 8 changed two code lines\n"
            "with sed -i against that rule. Reading with sed -n, cat or grep is fine.\n"
            "\n"
            "If a shell write to a code file is genuinely needed (restoring a file for a\n"
            "test injection, say), re-run with the literal token allow_shell_code_edit in\n"
            "the command.",
            file=sys.stderr,
        )
        return 2

    # The checks below look only at commands that actually run python.
    if not runs_python:
        return 0

    if "allow_unraw_escape" in cmd:
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
