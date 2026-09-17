"""PreToolUse hook blocking `git stash` (carry-forward protection).

Converted 2026-09-14 from block-carry-forward-stash.ps1 (itself ported
2026-09-02 from spamfilter-multi, Sprint 2 retro disposition). Enforces
workflow 6.6 and ADR-0004: NEVER stash to carry forward; create the branch,
then COMMIT.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_stash in the command (team-lead-sanctioned only).
Matches INVOCATIONS, not text: quoted strings and heredoc bodies are
stripped before matching (spamfilter F130-S51 false-positive lesson).
"""
from __future__ import annotations

import json
import re
import sys

HEREDOC_BODY = re.compile(
    r"(?s)<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?.*?^\s*\1\s*$", re.MULTILINE
)
HERESTRING_BODY = re.compile(r"(?s)@'.*?'@")
SINGLE_QUOTED = re.compile(r"'[^']*'")
DOUBLE_QUOTED = re.compile(r'"[^"]*"')


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
    if "allow_stash" in cmd:
        return 0

    # Strip data regions (heredocs, quoted spans) so docs ABOUT stash do not trip it.
    scan = cmd
    scan = HEREDOC_BODY.sub(" ", scan)
    scan = HERESTRING_BODY.sub(" ", scan)
    scan = SINGLE_QUOTED.sub(" ", scan)
    scan = DOUBLE_QUOTED.sub(" ", scan)

    if re.search(r"git\s+stash\s+(list|show)\b", scan):
        return 0

    if re.search(r"git\s+stash\b", scan):
        print(
            "[BLOCKED] git stash is disallowed (workflow 6.6 carry-forward rule; ADR-0004).\n"
            "\n"
            "Use the DETERMINISTIC flow instead:\n"
            "  1. Create the next branch:  git checkout -b <next-branch>\n"
            "  2. COMMIT the uncommitted files on that branch -- the working tree follows\n"
            "     a checkout -b; stashing is never needed for carry-forward.\n"
            "\n"
            "Recovery for a mis-cut branch is cherry-pick, never stash. If the team lead\n"
            "has sanctioned a genuine non-carry-forward stash, re-run with the literal\n"
            "token allow_stash in the command.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
