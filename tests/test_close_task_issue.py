"""scripts/close_task_issue.py resolves the issue from the task letter
(Sprint 6 retrospective I3). No network: only the lookup is tested."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("close_task_issue", ROOT / "scripts" / "close_task_issue.py")
close_task_issue = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(close_task_issue)


def _status(tmp_path: Path, mapping: dict) -> Path:
    p = tmp_path / "sprint_status.json"
    p.write_text(json.dumps({"current_sprint": {"task_issues": mapping}}), encoding="utf-8")
    return p


def test_the_letter_gives_the_recorded_number(tmp_path):
    p = _status(tmp_path, {"G": 61, "H": 62, "I": 63})
    assert close_task_issue.issue_for("h", p) == 62
    assert close_task_issue.issue_for("I", p) == 63


def test_an_unknown_letter_is_refused(tmp_path):
    with pytest.raises(KeyError, match="no issue"):
        close_task_issue.issue_for("Z", _status(tmp_path, {"A": 55}))


def test_the_live_status_maps_every_issue_once():
    current = json.loads((ROOT / ".claude" / "sprint_status.json").read_text(encoding="utf-8"))["current_sprint"]
    mapping = current.get("task_issues")
    if mapping:
        assert sorted(mapping.values()) == sorted(current["github_issues"])
