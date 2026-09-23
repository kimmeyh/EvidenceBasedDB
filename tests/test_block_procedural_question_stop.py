"""Behavioral tests for .claude/hooks/block_procedural_question_stop.py
(Sprint 4 Task I, F15): the auto-advance-window Stop hook.

Every case runs the real hook as a subprocess with a programmatically built
JSON payload (QUALITY_STANDARDS.md amendment 2026-09-16: never a shell
pipe), against a scratch repository built in tmp_path via repo_override and
branch_override -- never this repository's own sprint_status.json.

FIXTURE SET. BLOCK_MESSAGES and ALLOW_MESSAGES are this repository's own
near-violations and legitimate stops, in the shape the master plan's F15
card asked for (an EvidenceBasedDB-specific set, not the source
repository's). The block side is the auto-advance failure class this
repository already lived through with AskUserQuestion in Sprint 2; the
allow side is every sanctioned stop shape from SPRINT_STOPPING_CRITERIA.md
and SPRINT_EXECUTION_WORKFLOW.md.

WHAT THESE TESTS WOULD NOT CATCH: a procedural question phrased outside the
fixture vocabulary (the hook is pattern-based, so "Thoughts?" ending a
paragraph is caught but "Awaiting your go-ahead." with no question mark is
not), and a message that names a criterion it does not actually meet -- the
hook checks that a criterion is CITED, not that it applies.

Verified by injection, 2026-09-19: inserting `return 0` as the first
statement of main() in block_procedural_question_stop.py turned 12 of 34
tests red (returncode 0 != 2): all ten BLOCK_MESSAGES cases of
test_blocks_a_procedural_question_inside_the_window,
test_blocks_when_the_final_paragraph_is_a_numbered_list_after_a_question
and test_reads_the_messages_list_when_last_assistant_message_is_absent.
The 22 allow-direction cases stayed green, as they must under a hook that
allows everything. Restoring the file (diff against the backup empty)
returned the module to 34 passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_procedural_question_stop.py"

SPRINT_BRANCH = "feature/20260919_Sprint_4"

# Inside the window, each of these must BLOCK: a procedural question at a
# task or phase boundary, with no criterion cited.
BLOCK_MESSAGES = [
    # 1. the plain confirm-the-next-task question
    "Task B is complete and the suite is green (236 passed).\n\n"
    "Shall I proceed to Task C?",
    # 2. asking whether to proceed, as a yes/no numbered list with no Class named
    "Task B is done. Next up is Task C (the F16 hook).\n\n"
    "Should I proceed?\n\n1. Yes\n2. No",
    # 3. "want me to"
    "The F16 hook is written and its tests pass.\n\n"
    "Do you want me to register it in settings.json now?",
    # 4. shall I close the issue
    "PR body updated with Task A's evidence.\n\nShall I close the issue?",
    # 5. bare "Next:" with nothing after it
    "Tasks A and B are committed.\n\nNext:",
    # 6. let me know if
    "Task D's migration ran clean on the 46 papers.\n\n"
    "Let me know if you want me to continue with D3.",
    # 7. ready to proceed
    "Everything for Task E is staged and green. Ready to proceed to Task F.",
    # 8. would you like
    "The three hooks are registered.\n\n"
    "Would you like me to run the full suite before moving on?",
    # 9. a rhetorical-looking but still procedural final question
    "The export regenerated identically.\n\nOK to commit?",
    # 10. phase boundary rather than task boundary
    "All Phase 4 tasks are complete.\n\nShould I go ahead and start Phase 5 now?",
]

# Inside the window, each of these must ALLOW: a named criterion, a
# sanctioned stop shape, or a plain status line with no question at all.
ALLOW_MESSAGES = [
    # 1. Criterion 2 BLOCKED report
    "STOP: Criterion 2 BLOCKED\n"
    "Status: Tasks A-C done; Task D blocked\n"
    "Reason: the Crossref API returns 403 through the proxy after three attempts\n"
    "Action taken: documented in #34\n"
    "Next steps: needs the proxy allowlist updated\n"
    "Team-lead decision needed: which path?",
    # 2. Class 3 numbered decision
    "This would change scope: Task G's true size is 2x the estimate. "
    "Class 3 decision, Criterion 3.\n\n"
    "1. Reduce elsewhere\n2. Extend the sprint\n3. Defer Task G",
    # 3. Phase 5 validation handover
    "Manual Validation plan for Sprint 4. Walk each item and reply with the "
    "number of any that fails:\n\n"
    "1. Run pytest -q\n2. Open export/papers.md\n3. Check the three hooks fire\n\n"
    "Let me know if any item fails.",
    # 4. mid-sprint status line stating the next action in one sentence
    "Task B is complete and green. Next: Task C, implementing the F16 hook.",
    # 5. Stopping criterion N, spelled long
    "Stopping criterion 4 applies: the migration exposed a defect in the "
    "existing anchor convention. Fixing now with a regression test.\n\n"
    "Should I also backlog the wider audit?",
    # 6. blocked precondition phrasing
    "Task F cannot start: blocked precondition, the ADR-0005 amendment "
    "is not yet approved. Continuing with Task H meanwhile. Approve?",
    # 7. Class 1 design decision
    "This would change an ACCEPTED ADR's spine: Class 1 decision. "
    "Should I proceed?\n\n1. Yes, as a dated amendment\n2. No",
    # 8. a report ending in a statement, not a question
    "All eleven tasks are complete; the suite is green; the PR body is "
    "updated. Handing over for Phase 5.",
    # 9. Criterion 7, precedence case
    "Criterion 7: a committed record's provenance is invalidated. Stopping "
    "and waiting; two alternatives below.\n\n1. Amend\n2. Re-export",
    # 10. the word BLOCKED alone marks a sanctioned stop
    "Task I is BLOCKED on a decision only the team lead can make. "
    "Continuing with Task J. Which reason wording do you prefer?",
]


def _scratch_repo(tmp_path: Path, status: dict | None, plan_doc: bool = True) -> Path:
    repo = tmp_path / "repo"
    (repo / ".claude").mkdir(parents=True)
    (repo / "docs" / "sprints").mkdir(parents=True)
    if status is not None:
        (repo / ".claude" / "sprint_status.json").write_text(json.dumps(status), encoding="utf-8")
    if plan_doc:
        (repo / "docs" / "sprints" / "SPRINT_4_PLAN.md").write_text("plan", encoding="utf-8")
    return repo


def _status(**over) -> dict:
    base = {
        "current_sprint": {
            "number": 4,
            "branch": SPRINT_BRANCH,
            "status": "phase_4_execution",
            "plan_doc": "docs/sprints/SPRINT_4_PLAN.md",
            "pr": 30,
            "plan_approved": True,
            "github_issues": [31, 32],
        }
    }
    base["current_sprint"].update(over)
    return base


def _run_hook(repo: Path, branch: str, message: str) -> subprocess.CompletedProcess:
    payload = {
        "repo_override": str(repo),
        "branch_override": branch,
        "last_assistant_message": message,
    }
    return subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True
    )


@pytest.mark.parametrize("message", BLOCK_MESSAGES)
def test_blocks_a_procedural_question_inside_the_window(tmp_path, message):
    repo = _scratch_repo(tmp_path, _status())
    proc = _run_hook(repo, SPRINT_BRANCH, message)
    assert proc.returncode == 2, f"expected block for {message!r}: {proc.stderr}"
    assert "auto-advance window" in proc.stderr
    assert "SPRINT_STOPPING_CRITERIA" in proc.stderr


@pytest.mark.parametrize("message", ALLOW_MESSAGES)
def test_allows_a_sanctioned_stop_inside_the_window(tmp_path, message):
    repo = _scratch_repo(tmp_path, _status())
    proc = _run_hook(repo, SPRINT_BRANCH, message)
    assert proc.returncode == 0, f"expected allow for {message!r}: {proc.stderr}"


def test_blocks_when_the_final_paragraph_is_a_numbered_list_after_a_question(tmp_path):
    """The question sits one paragraph above the "1. Yes 2. No" list; the
    hook must read past the list to find it."""
    repo = _scratch_repo(tmp_path, _status())
    proc = _run_hook(repo, SPRINT_BRANCH, "Task B done.\n\nProceed to Task C?\n\n1. Yes\n2. No")
    assert proc.returncode == 2


def test_allows_the_same_question_before_plan_approval(tmp_path):
    """Before 3.7 approval, asking is REQUIRED (Invariant 1)."""
    repo = _scratch_repo(tmp_path, _status(plan_approved=False, status="phase_3_planning", pr=None))
    proc = _run_hook(repo, SPRINT_BRANCH, BLOCK_MESSAGES[0])
    assert proc.returncode == 0


@pytest.mark.parametrize("phase", ["phase_5_validation", "phase_7_retrospective_complete", "phase_1_refinement"])
def test_allows_the_same_question_outside_phase_4(tmp_path, phase):
    """From validation onward, asking is CORRECT (Invariant 1)."""
    repo = _scratch_repo(tmp_path, _status(status=phase))
    proc = _run_hook(repo, SPRINT_BRANCH, BLOCK_MESSAGES[0])
    assert proc.returncode == 0


def test_allows_when_the_plan_doc_is_missing(tmp_path):
    repo = _scratch_repo(tmp_path, _status(), plan_doc=False)
    proc = _run_hook(repo, SPRINT_BRANCH, BLOCK_MESSAGES[0])
    assert proc.returncode == 0


def test_allows_when_sprint_status_is_missing_or_unreadable(tmp_path):
    repo = _scratch_repo(tmp_path, None)
    assert _run_hook(repo, SPRINT_BRANCH, BLOCK_MESSAGES[0]).returncode == 0
    (repo / ".claude" / "sprint_status.json").write_text("{not json", encoding="utf-8")
    assert _run_hook(repo, SPRINT_BRANCH, BLOCK_MESSAGES[0]).returncode == 0


@pytest.mark.parametrize("branch", ["main", "develop", "feature/no-sprint-here"])
def test_does_not_fire_off_a_sprint_branch(tmp_path, branch):
    repo = _scratch_repo(tmp_path, _status())
    proc = _run_hook(repo, branch, BLOCK_MESSAGES[0])
    assert proc.returncode == 0


def test_bypass_token_in_the_branch_name_allows_the_stop(tmp_path):
    repo = _scratch_repo(tmp_path, _status())
    proc = _run_hook(repo, "feature/20260919_Sprint_4_allow_stop_hook_bypass", BLOCK_MESSAGES[0])
    assert proc.returncode == 0


def test_reads_the_messages_list_when_last_assistant_message_is_absent(tmp_path):
    repo = _scratch_repo(tmp_path, _status())
    payload = {
        "repo_override": str(repo),
        "branch_override": SPRINT_BRANCH,
        "messages": [
            {"role": "user", "content": "go"},
            {"role": "assistant", "content": BLOCK_MESSAGES[0]},
        ],
    }
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True
    )
    assert proc.returncode == 2


def test_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input="not valid json {{{", capture_output=True, text=True
    )
    assert proc.returncode == 0


def test_empty_message_fails_open(tmp_path):
    repo = _scratch_repo(tmp_path, _status())
    assert _run_hook(repo, SPRINT_BRANCH, "").returncode == 0
