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
    # review of 57107f1: anchor and context fixes are keyed the same way
    monkeypatch.setattr(g, "ANCHOR_FIX", {"x": "p.3"})
    monkeypatch.setattr(g, "CONTEXT_FIX", {"x": "ml"})
    assert g.edits_under_moved_ids() == ["x"]


def test_an_edit_under_the_stored_id_of_a_moved_assertion_is_written(monkeypatch):
    """Review of 9c79048: record() read an edit under the reader's id while the
    guard told the coordinator to name it under the stored id, so the edit was
    dropped and the reader's value written. Proven to fail, 2026-10-26: with
    record() reading the reader's id, the value was the reader's."""
    g = _script()
    paper = {"record_id": "src", "assertions": [{
        "id_suggestion": "x", "value": "the reader's value", "anchor": "p.1", "quotes": ["a quote"],
        "context": "qml", "claim_type": "positive", "result_type": "theoretical"}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g1", paper)])
    monkeypatch.setattr(g, "HIGH", high_grades({"x": ("proved result", "quoted with its conditions")}))
    monkeypatch.setattr(g, "ID_FIX", {"x": "src-x"})
    monkeypatch.setattr(g, "VALUE_REPLACE", {"src-x": "the coordinator's value"})
    monkeypatch.setattr(g, "EXTRA_QUOTES", {"src-x": ["an added quote"]})
    monkeypatch.setattr(g, "ANCHOR_FIX", {"src-x": "p.3"})
    monkeypatch.setattr(g, "CONTEXT_FIX", {"src-x": "ml"})
    [(_, rec, _, _)] = g.assertions()
    assert (rec.id, rec.value) == ("src-x", "the coordinator's value")
    assert "an added quote" in rec.citation_context
    # review of 57107f1: the anchor and context fixes were still read under the reader's id
    assert (rec.provenance, rec.context) == ("src, p.3", "ml")


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


def _task_f():
    """Task G's script, Task F's, and a subagent read detail in Task F's own wording."""
    spec = importlib.util.spec_from_file_location("sprint13_reading", ROOT / "scripts" / "sprint13_reading.py")
    f = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f)
    return _script(), f, f.read_detail("b07", {"partial_detail": "Abstract, introduction and Section 2", "record_id": "x"})


def test_a_read_row_another_script_wrote_on_the_same_day_is_not_taken_for_this_one():
    """Full suite after the g001 to g042 apply, 2026-10-27: Task F (F112) read 57 of these papers on 2026-10-25,
    a Task G review day, under the same reader names, and the apply rewrote Task F's 114 rows as its own. Task F's
    wording is taken from its script, so a change there turns this red. Proven to fail, 2026-10-28: with is_mine
    answering True for every row, as the key match did, the Task F rows were taken."""
    g, f, task_f = _task_f()
    assert not g.is_mine("subagent", task_f)
    assert not g.is_mine("partial", f.COORDINATOR_DETAIL)
    assert g.is_mine("subagent", g.read_detail("g001", {"record_id": "x", "read_extent": "full"}))
    assert g.is_mine("partial", g.COORDINATOR_DETAIL)


def test_the_apply_adds_its_reads_beside_another_scripts_and_leaves_them_alone(synthetic_store):
    """Fresh-eyes review of 5e10948: the test above checks is_mine alone, so the apply could stop calling it and
    stay green. This one drives the apply's read writer. Proven to fail, 2026-10-28: with write_reads building its
    rows without is_mine, the first call logged 'update' twice, rewriting Task F's rows."""
    from store import connect
    g, f, task_f = _task_f()
    day, rid = "2026-10-25", "alpha-2024-first-paper"
    conn = connect(synthetic_store)
    try:
        for extent, det in (("subagent", task_f), ("partial", f.COORDINATOR_DETAIL)):
            conn.execute("INSERT INTO paper_reads (record_id, reader, read_on, extent, detail) VALUES (?, ?, ?, ?, ?)",
                         (rid, g.SUBAGENT_READER if extent == "subagent" else "Claude", day, extent, det))
        detail = g.read_detail("g001", {"record_id": rid, "read_extent": "full"})
        assert [x.split()[0] for x in g.write_reads(conn, rid, day, detail)] == ["read", "read"]
        rows = {r[0] for r in conn.execute("SELECT detail FROM paper_reads WHERE record_id = ? AND read_on = ?",
                                           (rid, day))}
        assert rows == {task_f, f.COORDINATOR_DETAIL, detail, g.COORDINATOR_DETAIL}
        assert g.write_reads(conn, rid, day, detail) == []
    finally:
        conn.close()
