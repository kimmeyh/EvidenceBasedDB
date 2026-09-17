"""Stop hook blocking a turn that CLAIMS sprint/phase close-out completion
while machine-checkable artifacts contradict it.

Converted 2026-09-14 from verify-closeout-complete.ps1 (itself ported
2026-09-02 from spamfilter-multi, Sprint 50 escape lesson), adapted to this
repo's sprint_status schema (current_sprint.pr, updated) and doc paths.

Fires ONLY when the final assistant message claims close-out completion AND
an artifact contradicts it. Checks: sprint_status currency and sprint
number; PR recorded once plan_approved; previous sprint SUMMARY exists
(three-doc rule); uncommitted 0* team-lead files; open sprint-labeled issues
AFTER the sprint PR merged (post-merge precondition -- spamfilter Sprint 51
false-positive lesson).

Exit 0 = allow stop. Exit 2 = block with guidance.
Bypass: branch name containing allow_stop_hook_bypass.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CLAIM_PATTERNS = [
    r"(?i)\b(the\s+)?(sprint|phase\s*[78]|close[- ]?out|post[- ]?merge)\s+(work\s+|process\s+)?(is|was)\s+(now\s+)?(fully\s+|genuinely\s+)?(complete|closed|done|finished)\b",
    r"(?i)\bclose[- ]?out\b[^.\n]{0,40}\b(is|was)\s+(now\s+)?(complete|done|finished)\b",
    r"(?i)\ball\s+(the\s+)?(post[- ]?merge|checklist|close[- ]?out)\s+(items|steps)\b[^.\n]{0,40}\b(are\s+)?(now\s+)?(complete|done)\b",
    r"(?i)\bready\s+for\s+(the\s+)?next\s+sprint\b",
    r"(?i)\bsprint\s+\d+\s+is\s+(fully\s+)?(closed|complete)\b",
]
MID_SPRINT_PATTERNS = [
    r"(?i)\b(task|tier|sub[- ]?task)\s+\w+\b[^.\n]{0,40}\b(blocked|in progress|not started|remaining|pending)\b",
    r"(?i)\bstopping criterion\s*\d",
    r"(?i)\b(is|remains)\s+blocked\b",
    r"(?i)\bstill\s+(executing|in\s+flight|running)\b",
]
BRANCH_PATTERN = re.compile(r"^feature/\d+_Sprint_(\d+)")


def _run(args: list[str], cwd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=15
        )
        return proc.returncode, proc.stdout
    except Exception:
        return 1, ""


def main() -> int:
    raw = sys.stdin.read()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    cwd = str(payload.get("cwd") or Path.cwd())
    if payload.get("repo_override"):
        cwd = str(payload["repo_override"])

    last_message = ""
    try:
        if payload.get("last_assistant_message"):
            last_message = str(payload["last_assistant_message"])
        elif payload.get("messages"):
            assistant_msgs = [
                m for m in payload["messages"] if m.get("role") == "assistant"
            ]
            if assistant_msgs:
                last_message = str(assistant_msgs[-1].get("content", ""))
    except Exception:
        last_message = ""
    if not last_message:
        return 0

    # Gate 1: sprint feature branch only.
    branch_override = payload.get("branch_override")
    if branch_override:
        branch = str(branch_override).strip()
    else:
        _, out = _run(["git", "-C", cwd, "branch", "--show-current"], cwd)
        branch = out.strip()
    if not branch:
        return 0
    if "allow_stop_hook_bypass" in branch:
        return 0
    branch_match = BRANCH_PATTERN.match(branch)
    if not branch_match:
        return 0
    sprint_num = int(branch_match.group(1))

    # Gate 2: does the message CLAIM close-out completion? (narrow, anchored)
    claims = any(re.search(pat, last_message) for pat in CLAIM_PATTERNS)
    if claims:
        if any(re.search(pat, last_message) for pat in MID_SPRINT_PATTERNS):
            claims = False
    if not claims:
        return 0

    # Gate 3: machine-checkable artifacts.
    violations: list[str] = []
    status = None

    status_path = Path(cwd) / ".claude" / "sprint_status.json"
    if not status_path.exists():
        violations.append(".claude/sprint_status.json is MISSING.")
    else:
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            status_sprint = int(status["current_sprint"]["number"])
            if status_sprint != sprint_num:
                violations.append(
                    f".claude/sprint_status.json current_sprint.number is {status_sprint} "
                    f"but the branch is Sprint {sprint_num} -- stale state file misleads "
                    "the next session."
                )
        except Exception:
            violations.append(".claude/sprint_status.json is not valid JSON.")

    # PR recorded once plan approved (workflow 3.3.1; precondition per spamfilter F170).
    if status and isinstance(status.get("current_sprint"), dict):
        current_sprint = status["current_sprint"]
        if current_sprint.get("plan_approved") is True:
            pr_num = current_sprint.get("pr")
            if pr_num is None or str(pr_num) == "":
                violations.append(
                    "plan_approved is true but current_sprint.pr is null -- "
                    "workflow 3.3.1 requires the draft PR recorded."
                )

    # Uncommitted 0* team-lead working files at close-out (commit neutrally, never read).
    _, dirty = _run(["git", "-C", cwd, "status", "--porcelain", "--", "0*"], cwd)
    if dirty.strip():
        names = ", ".join(
            re.sub(r"^..\s*", "", line).strip()
            for line in dirty.splitlines()
            if line.strip()
        )
        violations.append(
            f"Uncommitted team-lead 0* working file(s): {names}. Commit with a "
            "neutral message (never read them)."
        )

    # Previous sprint SUMMARY (three-doc rule, workflow 3.2.1).
    prev_sprint = sprint_num - 1
    if prev_sprint > 0:
        prev_summary = Path(cwd) / "docs" / "sprints" / f"SPRINT_{prev_sprint}_SUMMARY.md"
        prev_retro = Path(cwd) / "docs" / "sprints" / f"SPRINT_{prev_sprint}_RETROSPECTIVE.md"
        if prev_retro.exists() and not prev_summary.exists():
            violations.append(
                f"docs/sprints/SPRINT_{prev_sprint}_SUMMARY.md is missing "
                "(three-doc rule, workflow 3.2.1)."
            )

    # Open sprint issues -- POST-MERGE precondition only.
    pr_merged = False
    rc, pr_json_raw = _run(
        ["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "state,mergedAt"],
        cwd,
    )
    if rc == 0 and pr_json_raw.strip():
        try:
            for pr in json.loads(pr_json_raw):
                if pr.get("state") == "MERGED" or pr.get("mergedAt"):
                    pr_merged = True
        except (json.JSONDecodeError, ValueError):
            pass
    if pr_merged:
        rc, gh_out = _run(
            ["gh", "issue", "list", "--label", "sprint", "--state", "open", "--json", "number"],
            cwd,
        )
        if rc == 0 and gh_out.strip():
            try:
                open_issues = json.loads(gh_out)
                if open_issues:
                    nums = ", ".join(f"#{i['number']}" for i in open_issues)
                    violations.append(
                        f"Sprint PR MERGED but sprint-labeled issues still OPEN: {nums} "
                        "('Closes #N' does not fire on feature->develop merges; close "
                        "manually, workflow 2.3)."
                    )
            except (json.JSONDecodeError, ValueError):
                pass

    if not violations:
        return 0

    violation_lines = "\n".join(f"  - {v}" for v in violations)
    print(
        "[BLOCKED by verify-closeout-complete hook]\n"
        "\n"
        "The final message claims close-out completion, but these artifacts contradict it:\n"
        "\n"
        f"{violation_lines}\n"
        "\n"
        "Open docs/SPRINT_CHECKLIST.md, walk the close-out section line by line, and fix\n"
        "each violation. Verify by CHECKING the artifact, not by recalling. Do not\n"
        "re-assert completion until every item is verified done.\n"
        "\n"
        "Bypass (only if a violation is genuinely not applicable): rename the branch to\n"
        "include allow_stop_hook_bypass, or state explicitly which item does not apply and why.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
