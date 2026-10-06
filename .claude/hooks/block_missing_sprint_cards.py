"""PreToolUse hook blocking a task commit before Phase 3.3.1's two
deliverables exist (Sprint 4 Task I, F16).

SPRINT_EXECUTION_WORKFLOW.md Phase 3.3.1 produces a GitHub issue per task
AND a draft PR together, and records both in .claude/sprint_status.json
(`github_issues`, `pr`). Nothing stopped a task commit from landing before
either existed. Modeled on spamfilter-multi's `require-sprint-cards.ps1`
(read-only source, 2026-09-18 survey), which was written after six task
commits landed with no cards and nobody noticed until Phase 7; adapted to
this repository's own field name (`pr`, not `pr_number`).

Blocks a `git commit` when current_sprint.plan_approved is true but
`github_issues` is empty or missing, or `pr` is null or missing. Before
approval there is nothing to require. A missing or unparseable status file
FAILS OPEN with a one-line warning on stderr: a broken state file is a
defect to report, not a reason to freeze every commit.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_missing_cards in the command.
Matches INVOCATIONS, not text: quoted strings and heredoc bodies are
stripped before matching, as block_carry_forward_stash.py does. Payload key
repo_override lets tests point the hook at a scratch repository.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEREDOC_BODY = re.compile(
    r"(?s)<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?.*?^\s*\1\s*$", re.MULTILINE
)
HERESTRING_BODY = re.compile(r"(?s)@'.*?'@")
SINGLE_QUOTED = re.compile(r"'[^']*'")
DOUBLE_QUOTED = re.compile(r'"[^"]*"')
GIT_COMMIT = re.compile(r"\bgit\s+(?:(?:-C|-c)\s+\S+\s+)*commit\b")

BYPASS_TOKEN = "allow_missing_cards"


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _command(payload: dict) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict) and tool_input.get("command"):
        return str(tool_input["command"])
    if payload.get("command"):
        return str(payload["command"])
    return ""


def is_git_commit(cmd: str) -> bool:
    scan = HEREDOC_BODY.sub(" ", cmd)
    scan = HERESTRING_BODY.sub(" ", scan)
    scan = SINGLE_QUOTED.sub(" ", scan)
    scan = DOUBLE_QUOTED.sub(" ", scan)
    return bool(GIT_COMMIT.search(scan))


# Sprint 6 retrospective I3 (2026-10-05): two Sprint 6 commit subjects named
# the wrong issue ("Task H (#63)" for #62; "G (#62)" for #61). The numbers
# were typed from memory; the map in sprint_status.json is the source.
TASK_REF = re.compile(r"\bTasks?\s+([A-Z])\b[^()\n]{0,60}?\(#(\d+)\)")
MISMATCH_BYPASS = "allow_task_issue_mismatch"


def check_task_issue_numbers(cmd: str, current: dict) -> int:
    """Block a commit whose message names "Task X (#N)" when the sprint's
    task_issues map says X is a different issue. Reads the RAW command,
    since the subject lives inside the quoted message. Without a map there
    is nothing to check (fail open)."""
    mapping = current.get("task_issues")
    if not isinstance(mapping, dict) or MISMATCH_BYPASS in cmd:
        return 0
    wrong = [f"Task {letter} (#{num}): the map says Task {letter} is #{mapping[letter]}"
             for letter, num in TASK_REF.findall(cmd)
             if letter in mapping and str(mapping[letter]) != num]
    if not wrong:
        return 0
    print(
        "[BLOCKED by block_missing_sprint_cards hook: task issue number]\n\n"
        + "\n".join(f"  - {w}" for w in wrong)
        + "\n\nThe task-to-issue map is current_sprint.task_issues in .claude/sprint_status.json.\n"
        "Use the number it gives (scripts/close_task_issue.py <letter> resolves it too).\n"
        f"Bypass (team-lead-sanctioned only): the literal token {MISMATCH_BYPASS}.",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    try:
        payload = _read_payload()
        cmd = _command(payload)
    except Exception:
        return 0  # fail open on malformed payload

    if not cmd or not cmd.strip():
        return 0
    if BYPASS_TOKEN in cmd:
        return 0
    if not is_git_commit(cmd):
        return 0

    cwd = str(payload.get("repo_override") or payload.get("cwd") or Path.cwd())
    status_path = Path(cwd) / ".claude" / "sprint_status.json"
    if not status_path.exists():
        print(
            f"[WARNING block_missing_sprint_cards] {status_path} not found; "
            "allowing the commit unchecked.",
            file=sys.stderr,
        )
        return 0
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        current = status["current_sprint"]
        if not isinstance(current, dict):
            raise ValueError("current_sprint is not an object")
    except Exception as exc:
        print(
            f"[WARNING block_missing_sprint_cards] {status_path} unreadable "
            f"({exc.__class__.__name__}); allowing the commit unchecked.",
            file=sys.stderr,
        )
        return 0

    if current.get("plan_approved") is not True:
        return 0

    missing: list[str] = []
    issues = current.get("github_issues")
    if not isinstance(issues, list) or not issues:
        missing.append("github_issues is empty or missing (one issue per task)")
    pr = current.get("pr")
    if pr is None or str(pr).strip() == "":
        missing.append("pr is null or missing (the draft PR)")
    if not missing:
        return check_task_issue_numbers(cmd, current)

    lines = "\n".join(f"  - {m}" for m in missing)
    print(
        "[BLOCKED by block_missing_sprint_cards hook]\n"
        "\n"
        "current_sprint.plan_approved is true but Phase 3.3.1's deliverables are\n"
        "not recorded in .claude/sprint_status.json:\n"
        "\n"
        f"{lines}\n"
        "\n"
        "Phase 3.3.1 (SPRINT_EXECUTION_WORKFLOW.md) creates a GitHub issue per\n"
        "task and the DRAFT PR together, before any task commit. Create whichever\n"
        "is missing, record its number(s) in sprint_status.json, then commit.\n"
        "\n"
        "Bypass (team-lead-sanctioned only): include the literal token\n"
        f"{BYPASS_TOKEN} in the command.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
