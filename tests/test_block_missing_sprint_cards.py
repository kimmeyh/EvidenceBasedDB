"""Behavioral tests for .claude/hooks/block_missing_sprint_cards.py (Sprint 4
Task I, F16): no task commit before Phase 3.3.1's issues and draft PR exist.

Every case runs the real hook as a subprocess with a programmatically built
JSON payload (QUALITY_STANDARDS.md amendment 2026-09-16: never a shell
pipe), against a scratch repository in tmp_path via repo_override -- never
this repository's own sprint_status.json, which at the time of writing has
pr 30 and eleven issues and would make every block case vacuous.

WHAT THESE TESTS WOULD NOT CATCH: a sprint_status.json whose `pr` or
`github_issues` values are recorded but WRONG (a stale PR number, issues
from the previous sprint) -- the hook checks presence, not correctness --
and a commit issued through a tool the Bash|PowerShell matcher does not
cover.

Verified by injection, 2026-09-19: inserting `return 0` as the first
statement of main() in block_missing_sprint_cards.py turned 9 of 19 tests
red: test_blocks_a_commit_when_the_pr_is_null,
test_blocks_a_commit_when_github_issues_is_empty,
test_blocks_a_commit_when_both_fields_are_absent, the three
test_blocks_the_other_commit_spellings cases and
test_powershell_tool_name_is_handled_the_same_way (returncode 0 != 2), plus
both test_fails_open_with_a_warning_* cases, which assert the WARNING on
stderr that a silenced hook never prints. Restoring the file (diff against
the backup empty) returned the module to 19 passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_missing_sprint_cards.py"

COMMIT = 'git commit -m "Task C: F16 hook (#33)"'


def _repo(tmp_path: Path, status: dict | str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".claude").mkdir(parents=True)
    if isinstance(status, dict):
        (repo / ".claude" / "sprint_status.json").write_text(json.dumps(status), encoding="utf-8")
    elif isinstance(status, str):
        (repo / ".claude" / "sprint_status.json").write_text(status, encoding="utf-8")
    return repo


def _status(**over) -> dict:
    base = {
        "current_sprint": {
            "number": 4,
            "status": "phase_4_execution",
            "plan_approved": True,
            "pr": 30,
            "github_issues": [31, 32, 33],
        }
    }
    base["current_sprint"].update(over)
    for key in [k for k, v in over.items() if v is ...]:
        del base["current_sprint"][key]
    return base


def _run(repo: Path, command: str, tool_name: str = "Bash") -> subprocess.CompletedProcess:
    payload = {"tool_name": tool_name, "tool_input": {"command": command}, "repo_override": str(repo)}
    return subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True
    )


def test_allows_a_commit_when_both_deliverables_are_recorded(tmp_path):
    proc = _run(_repo(tmp_path, _status()), COMMIT)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ""


def test_blocks_a_commit_when_the_pr_is_null(tmp_path):
    proc = _run(_repo(tmp_path, _status(pr=None)), COMMIT)
    assert proc.returncode == 2
    assert "pr is null or missing" in proc.stderr
    assert "3.3.1" in proc.stderr


def test_blocks_a_commit_when_github_issues_is_empty(tmp_path):
    proc = _run(_repo(tmp_path, _status(github_issues=[])), COMMIT)
    assert proc.returncode == 2
    assert "github_issues is empty or missing" in proc.stderr


def test_blocks_a_commit_when_both_fields_are_absent(tmp_path):
    proc = _run(_repo(tmp_path, _status(pr=..., github_issues=...)), COMMIT)
    assert proc.returncode == 2
    assert "pr is null or missing" in proc.stderr
    assert "github_issues is empty or missing" in proc.stderr


def test_allows_a_commit_before_plan_approval(tmp_path):
    """Phase 1-3 commits (refinement, plan drafting) predate the deliverables."""
    proc = _run(_repo(tmp_path, _status(plan_approved=False, pr=None, github_issues=[])), COMMIT)
    assert proc.returncode == 0


@pytest.mark.parametrize("command", [
    "git status",
    "git log --oneline -5",
    'echo "git commit is blocked until the cards exist"',
    "cat <<'EOF'\ngit commit -m x\nEOF",
    "grep -n 'git commit' docs/SPRINT_EXECUTION_WORKFLOW.md",
])
def test_allows_commands_that_only_mention_a_commit(tmp_path, command):
    proc = _run(_repo(tmp_path, _status(pr=None)), command)
    assert proc.returncode == 0, f"{command!r} was blocked: {proc.stderr}"


@pytest.mark.parametrize("command", [
    'git -C /some/where commit -m "x"',
    'git -c user.name=x commit -m "x"',
    "git add -A && git commit -F msg.txt",
])
def test_blocks_the_other_commit_spellings(tmp_path, command):
    proc = _run(_repo(tmp_path, _status(pr=None)), command)
    assert proc.returncode == 2, command


def test_bypass_token_allows_the_commit(tmp_path):
    proc = _run(_repo(tmp_path, _status(pr=None)), COMMIT + "  # allow_missing_cards")
    assert proc.returncode == 0


def test_fails_open_with_a_warning_when_the_status_file_is_missing(tmp_path):
    proc = _run(_repo(tmp_path, None), COMMIT)
    assert proc.returncode == 0
    assert "WARNING" in proc.stderr and "not found" in proc.stderr


def test_fails_open_with_a_warning_when_the_status_file_is_not_json(tmp_path):
    proc = _run(_repo(tmp_path, "{this is not json"), COMMIT)
    assert proc.returncode == 0
    assert "WARNING" in proc.stderr and "unreadable" in proc.stderr


def test_powershell_tool_name_is_handled_the_same_way(tmp_path):
    proc = _run(_repo(tmp_path, _status(pr=None)), COMMIT, tool_name="PowerShell")
    assert proc.returncode == 2


def test_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input="not valid json {{{", capture_output=True, text=True
    )
    assert proc.returncode == 0


def test_empty_payload_fails_open():
    proc = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True)
    assert proc.returncode == 0


MAP = {"A": 31, "B": 32, "C": 33}


def test_blocks_a_commit_naming_the_wrong_issue_for_its_task_regression(tmp_path):
    """Sprint 6 retrospective I3: "Task H (#63)" landed for #62. Proven to
    fail by injection: with check_task_issue_numbers returning 0 at once,
    this commit was allowed."""
    proc = _run(_repo(tmp_path, _status(task_issues=MAP)), 'git commit -m "Task B (#33): wrong number"')
    assert proc.returncode == 2
    assert "Task B is #32" in proc.stderr


def test_allows_matching_task_numbers_and_several_tasks(tmp_path):
    repo = _repo(tmp_path, _status(task_issues=MAP))
    assert _run(repo, 'git commit -m "Tasks A (#31) and C (#33) complete"').returncode == 0
    assert _run(repo, 'git commit -m "Task B review fixes (#32)"').returncode == 0


def test_no_map_means_no_number_check(tmp_path):
    proc = _run(_repo(tmp_path, _status()), 'git commit -m "Task B (#99)"')
    assert proc.returncode == 0
