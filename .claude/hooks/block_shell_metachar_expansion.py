"""Block shell metacharacters inside a Python string that Bash will expand
before Python ever sees it (F48, Sprint 11 retrospective improvement 4).

Converted 2026-09-14 from block-shell-metachar-expansion.ps1.

The sibling hook block_unraw_escape.py catches Windows path escapes in
non-raw PYTHON strings. It does not catch SHELL metacharacters, and those
are worse, because bash rewrites the command BEFORE python is invoked.

Two constructs do this inside a double-quoted or unquoted span:

    `...`        command substitution, backticks
    $(...)       command substitution
    ${...}       parameter expansion

OBSERVED IN SPRINT 11. Backticks inside a Python string in a Bash command
were expanded as command substitution. Bash executed a source file as shell,
and the backticked filenames were silently DELETED from a master-plan line.
The edit reported success. The damage was only visible on inspection, and it
was found by reading the file, not by any test.

That is the defect signature worth blocking: the command succeeds, the
output looks plausible, and the wrong thing happened. A crash would have
been kinder.

IT FIRED TWICE DURING SPRINT 14 PLANNING, correctly, while writing inline
Python that referenced a backslash. Both times the fix was to write the
script to a file instead of threading it through a shell string.

THE FIX IS ALWAYS ONE OF THREE:
  1. Write the script to a .py file and run it. Best for anything non-trivial
  2. Use a SINGLE-QUOTED heredoc, which suppresses all expansion:
         python - <<'PYEOF'    (note the quotes around PYEOF)
  3. Escape the metacharacter for the shell, if it is genuinely wanted

Exit 0 = allow. Exit 2 = block; stderr is fed back to Claude.
Bypass: the literal token allow_shell_metachar, for the rare case where the
expansion is deliberate.

Deliberately NARROW. It inspects only commands that invoke python, and only
spans that bash would actually expand. A single-quoted heredoc is exempt
because it is the recommended fix, and blocking the fix would make the hook
worse than useless -- the mistake the escape hook's first version made.
"""
from __future__ import annotations

import json
import re
import sys

SINGLE_QUOTED_HEREDOC = re.compile(r"<<\s*'[A-Za-z_][A-Za-z0-9_]*'")

# PER-LINE anchoring, not per-command. Testing the WHOLE command for a python
# invocation and then scanning every line blocks correct commands: a
# multi-line block whose last line runs python (flagging backticks in an
# unrelated earlier echo), and a command with no python at all, because the
# word appeared inside echoed prose. python must sit at a COMMAND POSITION:
# line start, or just after a separator (; && || |) or an opening paren,
# optionally behind a path like .venv/Scripts/ or /usr/bin/. A bare
# word-match blocks
#     echo "backticks `here` but no python invocation"
# because the word appeared in the echoed prose. A hook that blocks a
# sentence mentioning python is a hook that gets switched off.
INVOKES = re.compile(
    r"(?:^|[;&|(]|&&|\|\|)\s*(?:[^\s;&|()]*[/\\])?python[0-9.]*(?:\.exe)?(?:\s|$)"
)
BACKTICK_SUB = re.compile(r"`[^`]+`")
DOLLAR_PAREN_SUB = re.compile(r"\$\([^)]*\)")
DOLLAR_BRACE_EXPANSION = re.compile(r"\$\{[^}]*\}")


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
    if "allow_shell_metachar" in cmd:
        return 0

    # A SINGLE-QUOTED heredoc suppresses every expansion below, and it is the
    # fix this hook recommends. Exempt it, or the hook blocks its own advice.
    if SINGLE_QUOTED_HEREDOC.search(cmd):
        return 0

    bad: list[str] = []

    for line in cmd.split("\n"):
        t = line.strip()
        if t.startswith("#"):
            continue
        if not INVOKES.search(line):
            continue

        if BACKTICK_SUB.search(line):
            bad.append("`...` command substitution")
        if DOLLAR_PAREN_SUB.search(line):
            bad.append("$(...) command substitution")
        if DOLLAR_BRACE_EXPANSION.search(line):
            bad.append("${...} parameter expansion")

    if not bad:
        return 0

    seen: list[str] = []
    for item in bad:
        if item not in seen:
            seen.append(item)
    sample = "\n    ".join(seen[:3])

    # Sprint 9 retrospective I5: ${PIPESTATUS[...]} was blocked here in
    # Sprints 8 and 9 alike, each time while gating a commit on pytest. Show
    # the prescribed form first, so the right command is the first one seen.
    if "PIPESTATUS" in cmd:
        print(
            "[BLOCKED] ${PIPESTATUS[...]} in a python command. To gate on a test\n"
            "result, capture the exit code without a pipe (Sprint 9 retrospective I5):\n"
            "\n"
            "    python -m pytest -q > <log file> 2>&1; rc=$?; tail -3 <log file>; echo rc=$rc\n"
            "\n"
            "Never pipe pytest into tail or grep before reading $?: the pipe's exit\n"
            "code is the last command's, not pytest's (block_commit_with_piped_tests.py).\n",
            file=sys.stderr,
        )

    print(
        "[BLOCKED] Shell metacharacter in a python command; bash expands it BEFORE\n"
        "python runs (F48, Sprint 11 retrospective improvement 4).\n"
        "\n"
        "Found:\n"
        f"    {sample}\n"
        "\n"
        "Why this is blocked and not merely warned: in Sprint 11 backticks inside a\n"
        "Python string were expanded as command substitution. Bash executed a source\n"
        "file as shell and SILENTLY DELETED the backticked filenames from a master-plan\n"
        "line. The command reported success and the damage was only visible on\n"
        "inspection. A crash would have been kinder than a plausible-looking wrong\n"
        "result.\n"
        "\n"
        "FIX, in order of preference:\n"
        "\n"
        "  1. Write the script to a .py file and run it. Best for anything non-trivial,\n"
        "     and it makes the script reviewable and re-runnable.\n"
        "\n"
        "  2. Use a SINGLE-QUOTED heredoc, which suppresses every expansion:\n"
        "\n"
        "         python - <<'PYEOF'\n"
        "         ...your code...\n"
        "         PYEOF\n"
        "\n"
        "     The quotes around PYEOF are the whole point. Without them bash expands\n"
        "     the body.\n"
        "\n"
        "  3. Escape it for the shell, if the expansion is genuinely intended.\n"
        "\n"
        "If the expansion IS deliberate, re-run with the literal token\n"
        "allow_shell_metachar in the command.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
