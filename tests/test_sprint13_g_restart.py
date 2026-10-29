"""Sprint 13 Task G (F113), team lead 2026-10-26: "make future agent runs
setup to not loose anything if we cross current or weekly session limits and
can re-start them so that they know what was done and what was not done".

A reader saves each finished paper alone and checks it with `--partial`
(scripts/sprint13_g_check.py); scripts/sprint13_g_status.py computes where
each group stands from those files. Neither opens the real store here.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_one_saved_paper_passes_the_check_with_partial_and_not_without(tmp_path, capsys):
    """Proven to fail, 2026-10-26: with the --partial test removed from the
    check, the saved paper was refused for the record it does not hold."""
    check = _load("sprint13_g_check")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({"records": [{"record_id": "a", "file": "x.pdf"}, {"record_id": "b", "file": "y.pdf"}]}))
    done = tmp_path / "a.json"
    done.write_text(json.dumps({"papers": [{"record_id": "a", "file": str(tmp_path / "missing.pdf")}]}))
    check.main([str(done), str(brief), "--partial"])
    out = capsys.readouterr().out
    assert "no entry" not in out and "file not found" in out
    check.main([str(done), str(brief)])
    assert "b: no entry for this record" in capsys.readouterr().out
    other = tmp_path / "c.json"
    other.write_text(json.dumps({"papers": [{"record_id": "c", "file": str(tmp_path / "missing.pdf")}]}))
    check.main([str(other), str(brief), "--partial"])
    assert "c: not a record of this brief" in capsys.readouterr().out


def test_the_status_of_a_group_comes_from_its_files(tmp_path, monkeypatch):
    """Each state from the files that make it. Proven to fail, 2026-10-26:
    with the done\\ count removed from `reading`, the group with two saved
    papers was reported with 0 of 3 saved."""
    status = _load("sprint13_g_status")
    work, reviews = tmp_path / "s13g", tmp_path / "reviews"
    (work / "reads").mkdir(parents=True)
    reviews.mkdir()
    monkeypatch.setattr(status, "WORK", work)
    monkeypatch.setattr(status, "REVIEWS", reviews)
    records = ["r1", "r2", "r3"]
    assert status.state("g1", records, set()) == ("not started", "")
    (work / "tmp_g1").mkdir()
    assert status.state("g1", records, set()) == ("started", "nothing saved")
    (work / "tmp_g1" / "done").mkdir()
    (work / "tmp_g1" / "partial").mkdir()
    for r in ("r1", "r2"):
        (work / "tmp_g1" / "done" / f"{r}.json").write_text("{}")
    (work / "tmp_g1" / "partial" / "r3.json").write_text("{}")
    (work / "tmp_g1" / "progress.json").write_text(json.dumps({"record_id": "r3", "pages": 40, "last_page_read": 20}))
    assert status.state("g1", records, set()) == ("reading", "2 of 3 papers saved; r3 at page 20 of 40")
    (work / "reads" / "group_g1.json").write_text("{}")
    assert status.state("g1", records, set()) == ("read", "")
    (reviews / "g1.json").write_text("{}")
    assert status.state("g1", records, set()) == ("reviewed", "")
    assert status.state("g1", records, {"r1", "r2"}) == ("reviewed", ""), "one record not yet applied"
    assert status.state("g1", records, set(records)) == ("applied", "")
