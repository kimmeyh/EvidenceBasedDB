"""PreToolUse hook blocking a carry-forward branch cut from develop/main.

Converted 2026-09-14 from block-branch-from-develop.ps1 (written 2026-09-08
after Claude cut feature/20260909_Sprint_10 with
`git checkout -b feature/20260909_Sprint_10 origin/develop` during the
Sprint 9 close-out). Enforces the OTHER half of workflow 6.6: the next
sprint branch is cut FROM THE CURRENT FEATURE BRANCH, never from develop
after the merge.

No commits were lost that time -- the merge had already carried everything
and the uncommitted work followed the checkout -- so the violation was
invisible in the outcome and was caught only by re-reading 6.6. That is
exactly the failure a hook should catch: the rule's stated harm (losing
uncommitted work) does not appear every time it is broken, so a clean
result is not evidence the flow was right.

ALLOWED (the prescribed flow):   git checkout -b feature/<date>_Sprint_<N+1>
BLOCKED (what went wrong):       git checkout -b <name> origin/develop

A bare `checkout -b` inherits HEAD, which on a just-merged feature branch is
the correct start point. Only an EXPLICIT develop/main start point is
blocked.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_branch_from_base (team-lead-sanctioned only),
for the legitimate case of starting genuinely new work off develop that is
not a sprint carry-forward.

FOUR bypasses found in review of PR #58 against the PowerShell original, all
carried forward into this port:
  1. an option between the name and the base must not be captured as the
     base -- `--track origin/develop`, `--no-track origin/develop` and
     `switch -c -t` must all still be caught as cutting from develop.
  2. quoting the branch name must not blank the span before operands are
     read -- heredoc/prose stripping runs BEFORE operand extraction, and
     quoted operands are read from the STRIPPED text, not blanked further.
  3. every match in the command must be inspected, not just the first, so
     `git checkout -b tmp HEAD && git checkout -b feature/x origin/develop`
     catches the second invocation.
  4. once every match is inspected, the operand pattern must not swallow a
     `&&` separator as if it were an operand -- commands are split on
     separators FIRST, then matched per segment.
"""
from __future__ import annotations

import json
import re
import sys

HEREDOC_BODY = re.compile(
    r"(?s)<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?.*?^\s*\1\s*$", re.MULTILINE
)
HERESTRING_BODY = re.compile(r"(?s)@'.*?'@")
SEGMENT_SPLIT = re.compile(r"\s*(?:&&|\|\||;|\||\r?\n)\s*")
CHECKOUT_INVOCATION = re.compile(
    r"(?:git\s+checkout\s+(?:-b|-B)|git\s+switch\s+(?:-c|-C))((?:\s+\S+)+)"
)
BASE_IS_PROTECTED = re.compile(r"^(?:[A-Za-z0-9_.-]+/)?(?:develop|main|master)$")


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
    if "allow_branch_from_base" in cmd:
        return 0

    # Heredoc BODIES are removed first (a commit message describing the rule
    # must not trip it). Quoted spans are NOT blanked here, because a quoted
    # branch name is an operand this hook has to read.
    hd = HEREDOC_BODY.sub(" ", cmd)
    hd = HERESTRING_BODY.sub(" ", hd)
    segments = SEGMENT_SPLIT.split(hd)

    for seg in segments:
        m = CHECKOUT_INVOCATION.search(seg)
        if not m:
            continue

        operands = m.group(1).strip().split()
        # Drop option tokens; strip surrounding quotes; what remains is <name> <base>.
        positional = [
            re.sub(r"^[\"']+|[\"']+$", "", tok)
            for tok in operands
            if not tok.startswith("-")
        ]
        positional = [tok for tok in positional if tok != ""]
        if len(positional) < 2:
            continue

        new_branch, base = positional[0], positional[1]

        if BASE_IS_PROTECTED.match(base):
            print(
                f"[BLOCKED] Carry-forward branch cut from '{base}' (workflow 6.6; ADR-0004).\n"
                "\n"
                '6.6 is explicit: on merge notification, create the next sprint branch FROM THE\n'
                'CURRENT FEATURE BRANCH, and "never branch from develop after the merge".\n'
                "\n"
                "Use:\n"
                f"  git checkout -b {new_branch}\n"
                "  (bare -- no start point; the working tree and HEAD both follow)\n"
                "\n"
                "WHY THIS IS BLOCKED EVEN WHEN IT SEEMS TO WORK: cutting from develop drops any\n"
                "uncommitted work and any feature-branch commit the merge did not carry. When\n"
                "the merge HAS carried everything, the result looks identical to the correct\n"
                "flow, so a clean git status is not evidence the cut was right. That is how\n"
                "this slipped through at the Sprint 9 close-out.\n"
                "\n"
                "Recovery for a branch already mis-cut is cherry-pick onto a correctly-cut\n"
                "branch, never stash.\n"
                "\n"
                "WORK APPROVED DURING AN OPEN SPRINT goes on the sprint branch, not a branch off\n"
                f"{base}, unless the team lead asked for a separate PR (Sprint 8 retrospective I6:\n"
                "the F66 branch off develop conflicted with the sprint PR in the CHANGELOG and\n"
                "needed a branch merge to untangle).\n"
                "\n"
                f"If this is genuinely new work off {base}, NOT a sprint carry-forward, and either\n"
                "no sprint is open or the team lead asked for a separate PR, re-run with the\n"
                "literal token allow_branch_from_base in the command.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
