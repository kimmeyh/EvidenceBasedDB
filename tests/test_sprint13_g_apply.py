"""Sprint 13 Task G (F113): two guards of scripts/sprint13_g_reading.py, from
the fresh-eyes review of 6d8dec7. Neither opens the real store here.
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

from store.grading import high_grades

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("sprint13_g_reading", ROOT / "scripts" / "sprint13_g_reading.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_an_edit_under_an_id_that_id_fix_moves_is_refused(monkeypatch):
    """verify() looks an edit up under the stored id, so a VALUE_REPLACE under
    the reader's id would be written without its basis check. Proven to
    fail, 2026-10-26: with the check's tables emptied, the moved edit was
    not named."""
    g = _script()
    monkeypatch.setattr(g, "ID_FIX", {"x": "src-x"})
    monkeypatch.setattr(g, "VALUE_REPLACE", {"x": "a replaced value"})
    assert g.edits_under_moved_ids() == ["x"]
    monkeypatch.setattr(g, "VALUE_REPLACE", {"src-x": "a replaced value"})
    assert g.edits_under_moved_ids() == []


def test_a_graded_confirmed_row_the_apply_does_not_write_must_already_hold_its_grade(monkeypatch):
    """A confirmed stored assertion graded in a review but not in REQUOTE is
    never rewritten, so its stored certainty must already be the review's
    grade. Proven to fail, 2026-10-26: on a copy of the live store, with one
    such row's certainty changed, the check named it; before the change it
    named nothing."""
    g = _script()
    paper = {"existing": [{"id": "kept-high", "verdict": "confirmed"}, {"id": "kept-low", "verdict": "confirmed"},
                          {"id": "rewritten", "verdict": "narrowed"}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g1", paper)])
    monkeypatch.setattr(g, "HIGH", high_grades({"kept-high": ("proved result", "quoted with its conditions"),
                                                "rewritten": ("proved result", "quoted with its conditions")}))
    monkeypatch.setattr(g, "THEORY_LOW", {"kept-low": "cut in the quote"})
    monkeypatch.setattr(g, "REQUOTE", {})
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, certainty TEXT)")
    want_high = g.grade("kept-high", g.HIGH, otherwise=g.low_grade("authors' claim"))[0]
    want_low = g.low_grade("theoretical result", "cut in the quote")[0]
    conn.executemany("INSERT INTO records VALUES (?, ?)", [("kept-high", want_high), ("kept-low", want_low),
                                                           ("rewritten", want_low)])
    assert g.grades_not_written(conn) == []
    conn.execute("UPDATE records SET certainty = ? WHERE id = 'kept-high'", (want_low,))
    conn.execute("UPDATE records SET certainty = ? WHERE id = 'kept-low'", (want_high,))
    assert [p.split(":")[0] for p in g.grades_not_written(conn)] == ["kept-high", "kept-low"]
    monkeypatch.setattr(g, "REQUOTE", {"kept-high": "rebuilt", "kept-low": "rebuilt"})
    assert g.grades_not_written(conn) == []
