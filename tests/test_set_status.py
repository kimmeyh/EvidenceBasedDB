"""F142 part 4 (Sprint 17 Task C): the two status fields of `.claude/sprint_status.json` never differ.

Sprint 16 set only the top-level `status` at Phase 5.3, and the footer, which reads `current_sprint.status`, showed
the old phase until a second commit (8d16500). `scripts/set_status.py` writes both; the last test fails when the
committed file's fields differ, whatever wrote them.

Proven red 2026-11-07: with `set_status` writing only the top-level field (INJECTED), the first test failed; with the
committed file's `current_sprint.status` changed by hand (INJECTED), the last test failed. Each restored and green.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("set_status", ROOT / "scripts" / "set_status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _status_file(tmp_path: Path) -> Path:
    p = tmp_path / "sprint_status.json"
    p.write_text(json.dumps({"current_sprint": {"number": 99, "status": "Phase 4.1 Execution", "note": "start"},
                             "status": "Phase 4.1 Execution"}), encoding="utf-8")
    return p


def test_one_step_sets_both_fields_and_appends_the_note(tmp_path):
    p = _status_file(tmp_path)
    _script().set_status("Phase 5.3 Manual Validation", "handed over", path=p)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["status"] == data["current_sprint"]["status"] == "Phase 5.3 Manual Validation"
    assert data["current_sprint"]["note"] == "start | handed over"
    assert not list(tmp_path.glob("*.partial"))


@pytest.mark.parametrize("bad", ["Manual Validation", "Phase 5.3.1 Manual Validation", "Phase 5 Validation"])
def test_a_status_that_is_not_phase_n_n_is_refused_and_nothing_is_written(tmp_path, bad):
    p = _status_file(tmp_path)
    before = p.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        _script().set_status(bad, path=p)
    assert p.read_text(encoding="utf-8") == before


def test_the_committed_status_fields_agree():
    data = json.loads((ROOT / ".claude" / "sprint_status.json").read_text(encoding="utf-8"))
    assert data["status"] == data["current_sprint"]["status"], (
        "status and current_sprint.status differ; set both with python scripts/set_status.py")
