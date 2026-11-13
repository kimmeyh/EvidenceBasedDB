"""PreToolUse hook blocking a second working folder for this repository.

Sprint 17 retrospective i1 = a (team lead, 2026-11-10). In Sprint 17 a session
created `D:\\Data\\Harold\\github\\EvidenceBasedDB-sprint17` with
`git worktree add`, without asking. Git cannot check out one branch in two
folders, so the main folder could not switch branches; the status footer read
the wrong folder; and combining the two (q24) cost two merges, a CHANGELOG
conflict and a second Manual Validation hand-over. All work stays in
`D:\\Data\\Harold\\github\\EvidenceBasedDB` unless the team lead approves
another folder.

Blocks `git worktree add` in a shell command (Bash or PowerShell), and Claude
Code's own EnterWorktree tool. `git worktree list`, `remove` and `prune` stay
allowed: they inspect or undo, never create.

Exit 0 = allow. Exit 2 = block; stderr is fed back to Claude.

No bypass token. Fresh-eyes review, 2026-11-10: a token honored anywhere in the
command was honored in a comment too, the same flaw that removed the token from
block_env_secret_reads.py. When the team lead approves a second folder, they
run the command themselves with the `!` prefix; hooks fire only on Claude's
tool calls.

Conservative by design (same review): quoted text is NOT stripped, because a
stray apostrophe ("it's") paired quotes across the command and hid a real add.
Only quote characters and line continuations are removed, so `git -C "a b"`,
`& 'C:\\...\\git.exe'` and `git \\<newline> worktree add` still match. The cost
is a false block on a command that merely mentions the words, such as a commit
message given with -m; give such a message with -F from a file. Heredoc bodies
are removed from the line AFTER the opener, so the opener line is still checked.

A malformed payload is allowed (fail open), as in the other hooks here: the
harness always sends JSON, and a crash would block every command.
"""
from __future__ import annotations

import json
import re
import sys

# The body only: from the newline after `<<WORD ...` through the delimiter line. The opener line stays.
HEREDOC_BODY = re.compile(r"(<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?[^\n]*)\n.*?^\s*\2\s*$", re.S | re.M)
HERESTRING_BODY = re.compile(r"@(['\"])\s*\n.*?^\1@", re.S | re.M)
CONTINUATION = re.compile(r"[\\`]\r?\n")
# git or git.exe, any options or paths on the same command, then `worktree add`.
WORKTREE_ADD = re.compile(r"\bgit(?:\.exe)?\b[^\n;&|]*?\bworktree\s+add\b", re.I)

MESSAGE = (
    "[BLOCKED] A second working folder for this repository needs the team lead's approval first\n"
    "(Sprint 17 retrospective i1 = a).\n"
    "\n"
    "Work in D:\\Data\\Harold\\github\\EvidenceBasedDB on the sprint branch. Another branch there\n"
    "is a `git checkout` away; commit first, never stash.\n"
    "\n"
    "In Sprint 17 a worktree made without asking split the work over two folders: the main\n"
    "folder could not switch branches, the status footer read the wrong folder, and combining\n"
    "them cost two merges and a second Manual Validation hand-over.\n"
    "\n"
    "There is no bypass. If the team lead approves a second folder, they run the command\n"
    "themselves with the ! prefix. A commit message that only mentions the words: use -F <file>."
)


def scan_text(cmd: str) -> str:
    """The command as checked: heredoc bodies removed, continuations joined, quote characters dropped."""
    scan = HEREDOC_BODY.sub(lambda m: m.group(1), cmd)
    scan = HERESTRING_BODY.sub(" ", scan)
    scan = CONTINUATION.sub(" ", scan)
    return scan.replace("'", "").replace('"', "")


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        return 0  # fail open on a malformed payload (see the docstring)
    if not isinstance(payload, dict):
        return 0
    if payload.get("tool_name") == "EnterWorktree":
        print(MESSAGE, file=sys.stderr)
        return 2
    tool_input = payload.get("tool_input")
    cmd = str(tool_input.get("command") or "") if isinstance(tool_input, dict) else ""
    if cmd.strip() and WORKTREE_ADD.search(scan_text(cmd)):
        print(MESSAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
