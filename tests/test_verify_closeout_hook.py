"""Behavioral tests for .claude/hooks/verify_closeout_complete.py (Sprint 4
Task A, F27).

The hook had no test beyond registration. It runs here as a real
subprocess against a throwaway repository (repo_override + branch_override
in the payload, which the hook already supports), so the checks below
exercise the same code path Claude Code invokes -- never this repository's
own sprint_status.json.

Under the 2026-09-19 re-homing (Backlog Refinement is Sprint N's Phase 1 on
Sprint N's branch), sprint_status.json advances to N at the carry-forward
cut, so the hook's "number == branch" rule and
tests/test_sprint_documents.py's "plan doc from Phase 3" rule agree by
construction. These tests pin both directions of the hook: allow when the
file is current, block when it is stale.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "verify_closeout_complete.py"

CLAIM = "Close-out is complete: both merges landed, the branch is cut, refinement is done."
NO_CLAIM = "Task B is in progress; two rules remain."


def _scratch_repo(tmp_path: Path, status: dict, sprint_docs: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".claude").mkdir(parents=True)
    (repo / "docs" / "sprints").mkdir(parents=True)
    (repo / ".claude" / "sprint_status.json").write_text(json.dumps(status), encoding="utf-8")
    for name in sprint_docs:
        (repo / "docs" / "sprints" / name).write_text("x" * 500, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def _run_hook(repo: Path, branch: str, message: str) -> subprocess.CompletedProcess:
    payload = {"repo_override": str(repo), "branch_override": branch, "last_assistant_message": message}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)


def _status(number: int, **over) -> dict:
    base = {"current_sprint": {"number": number, "status": "phase_1_refinement", "plan_doc": None,
                               "pr": None, "plan_approved": False, "github_issues": []},
            "last_completed_sprint": {"number": number - 1}}
    base["current_sprint"].update(over)
    return base


def test_allows_a_current_status_file_at_the_between_sprints_moment(tmp_path):
    """Sprint 5's branch, status already advanced to 5 in phase_1: the exact
    state Task A's re-homing prescribes. Must NOT block."""
    repo = _scratch_repo(tmp_path, _status(5), ["SPRINT_4_PLAN.md", "SPRINT_4_RETROSPECTIVE.md", "SPRINT_4_SUMMARY.md"])
    proc = _run_hook(repo, "feature/20260101_Sprint_5", CLAIM)
    assert proc.returncode == 0, proc.stderr


def test_blocks_a_stale_sprint_number(tmp_path):
    """Sprint 5's branch but the status file still says 4: the stale-file
    failure the hook exists for (and the state Sprints 1-3 closed out in
    before the re-homing)."""
    repo = _scratch_repo(tmp_path, _status(4), ["SPRINT_4_PLAN.md", "SPRINT_4_RETROSPECTIVE.md", "SPRINT_4_SUMMARY.md"])
    proc = _run_hook(repo, "feature/20260101_Sprint_5", CLAIM)
    assert proc.returncode == 2
    assert "current_sprint.number is 4" in proc.stderr and "Sprint 5" in proc.stderr


def test_blocks_when_previous_summary_is_missing_but_retrospective_exists(tmp_path):
    repo = _scratch_repo(tmp_path, _status(5), ["SPRINT_4_PLAN.md", "SPRINT_4_RETROSPECTIVE.md"])
    proc = _run_hook(repo, "feature/20260101_Sprint_5", CLAIM)
    assert proc.returncode == 2
    assert "SPRINT_4_SUMMARY.md is missing" in proc.stderr


def test_blocks_when_plan_approved_without_a_pr(tmp_path):
    repo = _scratch_repo(tmp_path, _status(5, status="phase_4_execution", plan_approved=True, pr=None), ["SPRINT_4_PLAN.md", "SPRINT_4_RETROSPECTIVE.md", "SPRINT_4_SUMMARY.md"])
    proc = _run_hook(repo, "feature/20260101_Sprint_5", CLAIM)
    assert proc.returncode == 2
    assert "current_sprint.pr is null" in proc.stderr


def test_does_not_fire_without_a_completion_claim(tmp_path):
    """A stale file with NO completion claim in the message is not this
    hook's job (it fires only on a claim the artifacts contradict)."""
    repo = _scratch_repo(tmp_path, _status(4), ["SPRINT_4_PLAN.md", "SPRINT_4_RETROSPECTIVE.md", "SPRINT_4_SUMMARY.md"])
    proc = _run_hook(repo, "feature/20260101_Sprint_5", NO_CLAIM)
    assert proc.returncode == 0


@pytest.mark.parametrize("branch", ["main", "develop", "feature/no-sprint-here"])
def test_does_not_fire_off_a_sprint_branch(tmp_path, branch):
    repo = _scratch_repo(tmp_path, _status(4), ["SPRINT_4_PLAN.md"])
    proc = _run_hook(repo, branch, CLAIM)
    assert proc.returncode == 0
