"""Sprint 13 Task G (F113): the guards of scripts/full_read_apply.py (named
sprint13_g_reading.py until Sprint 14 retrospective Q5; this file was
test_sprint13_g_apply.py), first from the fresh-eyes review of 6d8dec7. The
live_store tests share one copy of the store and one apply (Q6).
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

from store.grading import high_grades

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("full_read_apply", ROOT / "scripts" / "full_read_apply.py")
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


def test_an_edited_figure_reading_keeps_its_figure_exemption(monkeypatch):
    """A sign-off's value_replace on a value read from a figure is checked
    with the same "about N" exemption as the value itself (Sprint 15 Manual
    Validation apply, 2026-11-04: five edited figure readings were refused).
    The edit check itself still refuses the numbers when no figure exemption
    is given (verify's quote check refuses a non-figure value first, so that
    half calls the edit check directly; fresh-eyes review). Proven to fail,
    2026-11-04: with read_from_page dropped from the edit check, verify()
    refused the figure reading."""
    g = _script()
    value = "Read from Figure 1: the runtime is about 25 hours at about 200 parameters."

    def paper(from_figure: bool) -> dict:
        return {"record_id": "src", "file": "src.pdf", "assertions": [{
            "id_suggestion": "x", "value": "the reader's value", "anchor": "p.1", "quotes": ["Figure 1 shows the runtime grows"],
            "context": "qml", "claim_type": "positive", "result_type": "measured", "from_figure": from_figure}]}

    monkeypatch.setattr(g, "source_text", lambda _: "Figure 1 shows the runtime grows with the parameters.")
    monkeypatch.setattr(g, "VALUE_REPLACE", {"x": value})
    monkeypatch.setattr(g, "load_groups", lambda: [("g1", paper(True))])
    [(a, _, _, _)] = g.verify()
    assert a.value == value
    quotes, text = ["Figure 1 shows the runtime grows"], "Figure 1 shows the runtime grows with the parameters."
    with pytest.raises(ValueError, match="the edited value states (25, 200|200, 25),"):
        g.require_edit_basis("x", value, quotes, text)
    g.require_edit_basis("x", value, quotes, text, read_from_page=g.read_from_figure(value))


@pytest.mark.live_store
def test_a_confirmed_row_rebuilt_for_its_grade_keeps_its_other_fields(monkeypatch, live_copy):
    """A confirmed stored entry rebuilt to change its grade (REQUOTE) keeps its
    stored fidelity, claim type and search scope: no review item names them.
    Sprint 15 Manual Validation trial, 2026-11-04: six regraded rows went from
    "scoped" to "exact" and three from "absence" to "positive". Proven to
    fail by injection, 2026-11-04: with the "confirmed" block removed from
    apply_changes, the fidelity written was "exact"."""
    from dataclasses import replace
    from store import connect
    from store.quotes import Verified
    g = _script()
    aid = "gsa-role-of-qpu"
    conn = connect(live_copy)
    try:
        before = conn.execute("SELECT r.fidelity, f.claim_type, f.search_scope FROM records r JOIN assertion_fields f "
                              "ON f.record_id = r.id WHERE r.id = ?", (aid,)).fetchone()
        assert before[0] != "exact" and before[1] != "positive"
        row = conn.execute("SELECT value, provenance, certainty_reasons FROM records WHERE id = ?", (aid,)).fetchone()
        cc = conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?", (aid,)).fetchone()[0]
        ctx = conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (aid,)).fetchone()[0]
        a = g.AssertionRecord(id=aid, value=row[0], provenance=row[1], citation_context=cc, evidence_tag="N/A",
                              context=ctx, certainty="low", certainty_reasons="regraded LOW in a test",
                              fidelity="exact", derivation="extracted", claim_type="positive", search_scope=None,
                              updated="2026-12-01", updated_reason=f"2026-12-01 (a test): {g.FULL_READ_MARK}: regraded")
        p = {"existing": [{"id": aid, "verdict": "confirmed"}]}
        monkeypatch.setattr(g, "verify", lambda conn=None: [(a, "src", p, Verified(aid, cc, row[0]))])
        monkeypatch.setattr(g, "load_groups", lambda: [])
        monkeypatch.setattr(g, "write_anchor_moves", lambda c, refused=None: [])
        g.apply_changes(conn)
        after = conn.execute("SELECT r.certainty, r.fidelity, f.claim_type, f.search_scope FROM records r JOIN "
                             "assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (aid,)).fetchone()
        assert tuple(after) == ("low", *before)
    finally:
        conn.rollback()
        conn.close()


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
    assert not g.is_mine(g.SUBAGENT_READER, task_f)
    assert not g.is_mine("Claude", f.COORDINATOR_DETAIL)
    assert g.is_mine(g.SUBAGENT_READER, g.read_detail("g001", {"record_id": "x", "read_extent": "full"}))
    assert g.is_mine("Claude", g.COORDINATOR_DETAIL)


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
        assert [x.split()[0] for x in g.write_reads(conn, rid, day, detail, "full")] == ["read", "read"]
        rows = {tuple(r) for r in conn.execute("SELECT extent, detail FROM paper_reads WHERE record_id = ? AND read_on = ?",
                                               (rid, day))}
        assert rows == {("subagent", task_f), ("partial", f.COORDINATOR_DETAIL), ("full", detail),
                        ("partial", g.COORDINATOR_DETAIL)}
        assert g.write_reads(conn, rid, day, detail, "full") == []
    finally:
        conn.close()


def test_a_whole_read_is_stored_full_and_an_earlier_subagent_row_is_moved(synthetic_store):
    """Team lead, Sprint 13 Manual Validation Q7 = 2 (2026-10-28): Task G's whole-paper reads are `full`, as F113's
    acceptance says; a read with a named exception is `partial`; the g001 to g042 rows first written as `subagent`
    are moved, not left beside the new ones. Proven to fail, 2026-10-28: with read_extent answering 'subagent', as
    before, the stored extent was 'subagent'."""
    from store import connect
    g = _script()
    day, rid = "2026-10-25", "alpha-2024-first-paper"
    assert g.read_extent({"record_id": rid, "read_extent": "full"}) == "full"
    assert g.read_extent({"record_id": rid, "read_extent": "partial"}) == "partial"
    detail = g.read_detail("g001", {"record_id": rid, "read_extent": "full"})
    conn = connect(synthetic_store)
    try:
        conn.execute("INSERT INTO paper_reads (record_id, reader, read_on, extent, detail) VALUES (?, ?, ?, ?, ?)",
                     (rid, g.SUBAGENT_READER, day, "subagent", detail))
        log = g.write_reads(conn, rid, day, detail, g.read_extent({"record_id": rid, "read_extent": "full"}))
        assert [x.split()[0] for x in log] == ["update", "read"]
        assert {tuple(r) for r in conn.execute("SELECT extent FROM paper_reads WHERE record_id = ? AND reader = ? "
                                               "AND read_on = ?", (rid, g.SUBAGENT_READER, day))} == {("full",)}
    finally:
        conn.close()


CLOUD_TAG = "Sprint 14 Task E, F117 (F114 cloud read)"
CLOUD_READER = "Claude Sonnet 5.5 (F114 cloud session)"


def test_a_cloud_group_reads_under_its_own_tag_and_reader(synthetic_store, monkeypatch):
    """Sprint 14 Task E (F117): F114's groups were read in cloud sessions and entered in Sprint 14, so a read row
    in Task G's wording would misstate its provenance. Proven to fail by injection, 2026-10-30: with read_detail
    writing Task G's wording for every group, the detail held "Sprint 13 Task G"; with reader() answering the
    subagent's name for every group, the detail named the subagent."""
    from store import connect
    g = _script()
    monkeypatch.setattr(g, "GROUP_TAG", {"g050": CLOUD_TAG})
    monkeypatch.setattr(g, "GROUP_READER", {"g050": CLOUD_READER})
    monkeypatch.setattr(g, "RECORD_READER", {"beta-2023-unrecorded": "Claude (F114 cloud session; model not recorded)"})
    day, rid = "2026-10-30", "alpha-2024-first-paper"
    detail = g.read_detail("g050", {"record_id": rid, "read_extent": "full"})
    assert CLOUD_TAG in detail and CLOUD_READER in detail and g.TAG not in detail
    assert g.reader("g050", rid) == CLOUD_READER
    assert g.reader("g050", "beta-2023-unrecorded").endswith("model not recorded)")
    assert g.reader("g001", rid) == g.SUBAGENT_READER and g.tag("g001") == g.TAG
    assert g.is_mine(CLOUD_READER, detail)
    conn = connect(synthetic_store)
    try:
        log = g.write_reads(conn, rid, day, detail, "full", g.reader("g050", rid))
        assert log == [f"read   {rid} [{CLOUD_READER}, full]", f"read   {rid} [Claude, partial]"]
        assert g.write_reads(conn, rid, day, detail, "full", g.reader("g050", rid)) == []
    finally:
        conn.close()


LOCAL_TAG = "Sprint 14 Task F, F114 (local read)"


def test_a_local_read_in_a_cloud_group_carries_its_own_tag(monkeypatch):
    """Sprint 14 Task F (review of 1cb63bb): abbas, read locally in g079, a group otherwise read in the cloud, would
    have carried "F114 cloud read" and "a first-pass cloud session" in its provenance. Proven to fail by injection,
    2026-10-30: with tag() ignoring RECORD_TAG, the local read's detail held the cloud tag; with first_pass() keyed
    on GROUP_TAG as before, a wholly local group's read named a cloud session; with RECORD_TAG's values left out of
    is_mine, abbas's read row was not taken for this script's (the test held LOCAL_TAG in GROUP_TAG too until the
    review of 11d443a, so that injection passed)."""
    g = _script()
    monkeypatch.setattr(g, "GROUP_TAG", {"g079": CLOUD_TAG, "g104": LOCAL_TAG})
    monkeypatch.setattr(g, "RECORD_TAG", {"abbas": LOCAL_TAG})
    detail = g.read_detail("g079", {"record_id": "abbas", "read_extent": "full"})
    assert LOCAL_TAG in detail and CLOUD_TAG not in detail
    assert g.tag("g079", "other") == CLOUD_TAG and g.first_pass("g079", "other") == "cloud session"
    assert g.first_pass("g079", "abbas") == "subagent" and g.first_pass("g104", "x") == "subagent"
    assert g.first_pass("g001", "x") == "subagent"
    monkeypatch.setattr(g, "GROUP_TAG", {"g079": CLOUD_TAG})  # abbas's tag held only per record (review of 11d443a)
    assert g.is_mine("Claude Sonnet 5.5", detail)


def test_a_record_marked_unread_is_left_out_of_its_group(tmp_path, monkeypatch):
    """Sprint 14 Task E: udaru-2025-qml-credit-risk (page images only) stays unread, so its group g076 holds four
    reader entries for five ledger records. The first load, before the mark, is the proof that the mark is what
    lets the group through: without it the group is refused as differing from the ledger."""
    import json
    import pytest
    g = _script()
    ledger = {"groups": {"g076": {"records": [{"record_id": r} for r in ("a", "b", "u")]}}}
    monkeypatch.setattr(g, "ledger", lambda: ledger)
    monkeypatch.setattr(g, "ONLY", ["g076"])
    monkeypatch.setattr(g, "READS_DIR", tmp_path)
    (tmp_path / "group_g076.json").write_text(json.dumps({"papers": [{"record_id": "a"}, {"record_id": "b"}]}),
                                              encoding="utf-8")
    with pytest.raises(ValueError, match="differ from the ledger"):
        g.load_groups()
    monkeypatch.setattr(g, "UNREAD", {"g076": {"u": "page images only"}})
    assert [p["record_id"] for _, p in g.load_groups()] == ["a", "b"]


def test_an_assertion_the_sign_off_adds_is_entered_and_checked_without_editing_the_read(tmp_path, monkeypatch):
    """F142 part 2 (Sprint 17 Task C): Sprint 16 split `he-simulation-scope` by editing the reader's read file by hand
    (db2abe3). The review's `add` table now carries the new assertion; load_groups merges it, the read file is
    unchanged, its history says the sign-off added it, and its quote is checked against the paper like a reader's.
    Proven red 2026-11-07: with load_groups not merging ADD (INJECTED), the added assertion was missing; with the
    sign-off's history line replaced by the reader's (INJECTED), "added at the coordinator's sign-off" was missing."""
    import json
    g = _script()
    monkeypatch.setattr(g, "ledger", lambda: {"groups": {"g076": {"records": [{"record_id": "a"}]}}})
    monkeypatch.setattr(g, "ONLY", ["g076"])
    monkeypatch.setattr(g, "READS_DIR", tmp_path)
    read = {"papers": [{"record_id": "a", "file": "a.pdf", "assertions": [], "existing": []}]}
    (tmp_path / "group_g076.json").write_text(json.dumps(read), encoding="utf-8")
    added = {"value": "The authors use only 100 samples per class for training and testing.", "anchor": "p.11",
             "quotes": ["only 100 samples per class are used"], "context": "qml", "claim_type": "positive",
             "result_type": "setup", "kind": "shown"}
    monkeypatch.setattr(g, "ADD", {"g076": {"x-split": {"record_id": "a", "why": "split, team lead Q1 = 3",
                                                        "assertion": added}}})
    [(_, p)] = g.load_groups()
    assert [a["id_suggestion"] for a in p["assertions"]] == ["x-split"]
    assert json.loads((tmp_path / "group_g076.json").read_text(encoding="utf-8")) == read

    monkeypatch.setattr(g, "source_text", lambda _: "To simulate scarcity, only 100 samples per class are used.")
    [(a, _, _, _)] = g.verify()
    # the decision and who made it reach the store (fresh-eyes review of 2580ce2: only a fixed phrase did)
    assert a.id == "x-split" and "added at the coordinator's sign-off (split, team lead Q1 = 3)" in a.updated_reason
    monkeypatch.setattr(g, "source_text", lambda _: "No such sentence in this paper.")
    with pytest.raises(ValueError, match="x-split"):
        g.verify()


def test_an_apply_that_rewrites_a_read_row_is_rolled_back_unless_named(synthetic_store, monkeypatch):
    """Sprint 13 retrospective I1 (team lead, 2026-10-28): the trial log's 114 'update read' lines went unquestioned
    and the real apply rewrote Task F's rows. Proven to fail, 2026-10-28: with commit_apply committing whatever
    apply_changes logged, the moved row stayed 'full' and nothing was raised."""
    import pytest
    from store import connect
    g = _script()
    day, rid = "2026-10-25", "alpha-2024-first-paper"
    detail = g.read_detail("g001", {"record_id": rid, "read_extent": "full"})
    monkeypatch.setattr(g, "apply_changes", lambda conn: g.write_reads(conn, rid, day, detail, "full"))
    conn = connect(synthetic_store)
    try:
        conn.execute("INSERT INTO paper_reads (record_id, reader, read_on, extent, detail) VALUES (?, ?, ?, ?, ?)",
                     (rid, g.SUBAGENT_READER, day, "subagent", detail))
        conn.commit()
        extents = "SELECT extent FROM paper_reads WHERE record_id = ? AND reader = ? AND read_on = ?"
        with pytest.raises(g.ReadRowsRewritten, match="1 read rows would be rewritten"):
            g.commit_apply(conn, update_reads=False)
        assert {tuple(r) for r in conn.execute(extents, (rid, g.SUBAGENT_READER, day))} == {("subagent",)}
        assert not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND reader = 'Claude' AND read_on = ?",
                                (rid, day)).fetchone()
        assert [x.split()[0] for x in g.commit_apply(conn, update_reads=True)] == ["update", "read"]
        assert {tuple(r) for r in conn.execute(extents, (rid, g.SUBAGENT_READER, day))} == {("full",)}
        assert g.commit_apply(conn, update_reads=False) == []  # a second apply writes nothing
        # review of c978e50: an assertion whose id begins "read" is not a read row
        monkeypatch.setattr(g, "apply_changes", lambda conn: ["update readout-2024-x [value]"])
        assert g.commit_apply(conn, update_reads=False) == ["update readout-2024-x [value]"]
    finally:
        conn.close()


def test_a_paper_refused_earlier_gets_no_new_assertion_unless_the_reversal_is_named(monkeypatch):
    """Review of b185729: 10 papers an earlier read refused as bearing on no context were entered because F114's
    reader chose a context, and no review said so. Proven to fail by injection, 2026-10-30: with the refusal check
    removed, the refused paper passed; with REENTER not consulted, the named reversal was still refused; with the
    stored-id check removed, a re-apply of entered assertions was refused."""
    g = _script()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, updated_reason TEXT)")
    conn.executemany("INSERT INTO records VALUES (?, ?)", [
        ("old", "2026-10-23 (Sprint 12 Task G, F105): read at first pass and NOT entered: no context"),
        ("fresh", "2026-10-20: added"), ("entered", "")])
    paper = {"record_id": "old", "assertions": [{"id_suggestion": "x"}]}
    monkeypatch.setattr(g, "DROP", {})
    monkeypatch.setattr(g, "REENTER", {})
    assert g.refused_without_reversal(conn, paper)
    assert not g.refused_without_reversal(conn, {"record_id": "fresh", "assertions": [{"id_suggestion": "x"}]})
    assert not g.refused_without_reversal(conn, {"record_id": "old", "assertions": [{"id_suggestion": "entered"}]})
    monkeypatch.setattr(g, "DROP", {"x": "waits for the team lead"})
    assert not g.refused_without_reversal(conn, paper)
    monkeypatch.setattr(g, "DROP", {})
    monkeypatch.setattr(g, "REENTER", {"old": "the team lead's decision"})
    assert not g.refused_without_reversal(conn, paper)


REFUSAL = "2026-10-15 (Sprint 9 Task G, F80): read at first pass and NOT entered: no Dirac-1 context"
REVERSAL = ("2026-10-18 (Sprint 10 Task F, F84): read and entered under platform:dirac-1; Sprint 9's refusal (no "
            "Dirac-1 context) no longer applies")


def test_a_refusal_a_later_note_reversed_does_not_refuse_a_new_read(monkeypatch):
    """F127 (Sprint 15 Task E), from the review of 4d969d9: the refusal guard matched a refusal anywhere in a record's
    history, so 9 QCI Dirac papers whose Sprint 9 refusal Sprint 10 reversed were refused at any new read. Only a
    refusal no later note reverses refuses now; a refusal after the reversal still does. Proven to fail, 2026-11-01,
    run before the change: the reversed record was refused."""
    g = _script()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, updated_reason TEXT)")
    conn.executemany("INSERT INTO records VALUES (?, ?)", [
        ("rev", f"{REFUSAL} | {REVERSAL}"),
        ("again", f"{REFUSAL} | {REVERSAL} | 2026-10-30 (Sprint 14 Task E, F117): read whole at first pass and NOT "
                  "entered: off topic")])
    monkeypatch.setattr(g, "DROP", {})
    monkeypatch.setattr(g, "REENTER", {})
    assert not g.refused_without_reversal(conn, {"record_id": "rev", "assertions": [{"id_suggestion": "x"}]})
    assert g.refused_without_reversal(conn, {"record_id": "again", "assertions": [{"id_suggestion": "x"}]})
    # review of the uncommitted D and E: a reversal that quotes the refusal's words reverses it; proven to fail by
    # injection, 2026-11-01: with reversals counted as refusals, "quoted" was refused
    conn.execute("INSERT INTO records VALUES (?, ?)", ("quoted", f"{REFUSAL} | 2026-10-18: the note 'read at first "
                                                                 "pass and NOT entered' is a refusal that no longer "
                                                                 "applies"))
    assert not g.refused_without_reversal(conn, {"record_id": "quoted", "assertions": [{"id_suggestion": "x"}]})


def test_the_clash_check_reads_a_record_id_as_a_whole_token():
    """F127 (Sprint 15 Task E), from the review of cecf20d: the applier's clash check matched the owner in the stored
    provenance with NOT LIKE %owner%, so an id that begins another's (...-assessment and ...-assessment-appendix-b)
    counted as the same source, and an id ending in a digit matched inside one that goes on with a dot. Proven to
    fail, 2026-11-01, run before the change: held_by_another did not exist; by injection, with the dot guard removed,
    v-2.5's assertion counted as v-2's."""
    g = _script()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, provenance TEXT)")
    conn.execute("CREATE TABLE assertion_fields (record_id TEXT)")
    rows = [("a1", "rand-2022-x-assessment-appendix-b, p.3"), ("a2", "rand-2022-x-assessment, p.4"),
            ("a3", "drawn from v-2."), ("a4", "v-2.5, p.1")]
    conn.executemany("INSERT INTO records VALUES (?, ?)", rows)
    conn.executemany("INSERT INTO assertion_fields VALUES (?)", [(r,) for r, _ in rows])
    assert g.held_by_another(conn, "a1", "rand-2022-x-assessment")
    assert not g.held_by_another(conn, "a2", "rand-2022-x-assessment")
    assert not g.held_by_another(conn, "a3", "v-2")
    assert g.held_by_another(conn, "a4", "v-2")
    assert not g.held_by_another(conn, "new", "v-2")
    assert not g.held_by_another(conn, "a2", "RAND-2022-X-Assessment")  # as LIKE did, case is ignored


def test_a_refusal_note_names_the_sign_off_drop_over_the_readers_why_not(monkeypatch):
    """Review of 4d969d9: where the reader wrote a `why_not`, it won over the sign-off drop, so 6 notes on dropped
    papers said where the assertions were entered and never named the team lead's decision. Proven to fail by
    injection, 2026-10-30: with `why_not` preferred again, the reader's text came back."""
    g = _script()
    monkeypatch.setattr(g, "DROP", {"x": "waits for the team lead", "y": "waits for the team lead"})
    paper = {"why_not": "entered under qc as the nearest label",
             "assertions": [{"id_suggestion": "x"}, {"id_suggestion": "y"}]}
    assert g.refusal_reason(paper) == "waits for the team lead"
    assert g.refusal_reason({"why_not": "off topic", "assertions": []}) == "off topic"


# The stored contexts an earlier intake chose, set on the shared copy and taken out of CONTEXT_FIX for its apply.
KEPT_CONTEXTS = {"dirac3-stratification-falls-short-ballin-2026": "platform:dirac-3",
                 "abbas-effective-dimension-generalisation-bound": "qml"}
DARJI = "darji-2024-robust-super-resolution-classifier-nonlinear"
_APPLIED: dict = {}


@pytest.fixture
def applied_once(request, tmp_path_factory) -> dict:
    """One copy of the live store and one apply_changes, shared by the live-store tests below (Sprint 14
    retrospective Q6: each took 8 to 10 minutes for its own copy and apply). The one apply carries every test's patch:
    the sentinel refusal reason, and KEPT_CONTEXTS set on the copy and taken out of CONTEXT_FIX. Neither patch bears
    on what the other test reads. The tests read the result, a copy each; nothing writes to the store copy after."""
    from store import connect
    from tests.conftest import _live_db, _open_read_only
    db = _live_db(request)  # fails a test that is not marked live_store
    if not _APPLIED:
        target = tmp_path_factory.mktemp("applied_once") / "live_copy.db"
        src, dst = _open_read_only(db), sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        g = _script()
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(g, "refusal_reason", lambda p: "SENTINEL-REASON")
            mp.setattr(g, "CONTEXT_FIX", {k: v for k, v in g.CONTEXT_FIX.items() if k not in KEPT_CONTEXTS})
            conn = connect(target)
            try:
                for rid, ctx in KEPT_CONTEXTS.items():
                    conn.execute("UPDATE record_contexts SET context_id = ? WHERE record_id = ?", (ctx, rid))
                conn.commit()
                log = g.apply_changes(conn)
                _APPLIED.update(
                    log=tuple(log), verify=dict(g.LAST_VERIFY),
                    darji_note=conn.execute("SELECT updated_reason FROM records WHERE id = ?", (DARJI,)).fetchone()[0],
                    contexts={rid: [r[0] for r in conn.execute(
                        "SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))] for rid in KEPT_CONTEXTS})
            finally:
                conn.close()
    return {k: (dict(v) if isinstance(v, dict) else v) for k, v in _APPLIED.items()}


@pytest.mark.live_store
def test_the_apply_writes_its_refusal_notes_through_refusal_reason_and_nothing_else(applied_once):
    """Review of ed5ab01: the test above calls refusal_reason directly, so an inline reason at the call site would
    stay green. On a copy of the store, a sentinel reason must reach every refused paper's note, and a re-apply must
    write nothing else. Proven to fail by injection, 2026-10-30: with the call site reading `why_not` inline, the
    sentinel was absent from darji-2024's note; again on the shared apply (Q6), 2026-10-31."""
    assert applied_once["darji_note"].endswith("NOT entered: SENTINEL-REASON")
    assert [x for x in applied_once["log"] if not x.startswith(("exists", "refuse "))] == []


@pytest.mark.live_store
def test_a_re_apply_checks_no_quote_and_reads_no_source(applied_once):
    """F136 acceptance: a second apply of every applied group checks nothing (and, above, writes nothing). Sprint
    15's re-apply checked about 10,000 quotes, 23 minutes. Proven to fail by injection, 2026-11-06: with
    apply_changes calling verify() without its connection, every quote was checked again. Restored. Sprint 17 q23
    (2026-11-09): before `decided_later`, the rows corrected at Manual Validation were checked again (6 checked, the
    gate's failure)."""
    counts = applied_once["verify"]  # a Counter turned dict: a count of 0 may be absent
    assert counts.get("checked", 0) == 0, counts
    assert counts["sources read"] == 0
    assert counts["stored as written"] > 1000


@pytest.mark.live_store
def test_a_stored_assertion_keeps_its_context_against_the_readers_label(applied_once):
    """Sprint 14 suite after the 2026-10-31 apply: the reader's nearest-fit context replaced two stored contexts that
    no review decided, among them a `platform:dirac-3` (F65 classes every Dirac-3 assertion). On a copy of the store
    set to the contexts an earlier intake chose, an apply must leave them. The sign-off now restores both through
    `context_fix`, which would pass this test with no check at all (review of 0eddd23), so the apply takes them out of
    it. Proven to fail by injection, 2026-10-31: with the stored-context check removed from apply_changes, ballin-2026's
    assertion came back `qc`; again on the shared apply (Q6), 2026-10-31."""
    assert applied_once["contexts"] == {rid: [ctx] for rid, ctx in KEPT_CONTEXTS.items()}


def test_a_high_the_applier_would_not_write_and_an_empty_value_are_refused(monkeypatch):
    """Review of de1efff: a signed HIGH on a vendor's own claim was written LOW without a word, and a requoted
    confirmed entry with no value of its own would have blanked the stored value. Proven to fail by injection,
    2026-10-30: with the vendor check removed from certainty(), the record came back LOW; with the value check
    removed from record(), the record carried an empty value."""
    g = _script()
    base = {"value": "v", "anchor": "p.1", "quotes": ["a quote"], "context": "qml", "result_type": "setup"}
    paper = {"record_id": "src", "assertions": [{"id_suggestion": "vend", "claim_type": "vendor-self-claim", **base}],
             "existing": [{"id": "conf", "verdict": "confirmed", "claim_type": "positive", **base, "value": ""}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g1", paper)])
    monkeypatch.setattr(g, "HIGH", high_grades({"vend": ("definition", "the product's own definition")}))
    monkeypatch.setattr(g, "REQUOTE", {})
    with pytest.raises(ValueError, match="vendor's own claim"):
        g.assertions()
    monkeypatch.setattr(g, "HIGH", high_grades({}))
    monkeypatch.setattr(g, "REQUOTE", {"conf": "the anchor moved"})
    with pytest.raises(ValueError, match="no value to write"):
        g.assertions()


def test_an_ocr_quote_is_marked_and_an_image_files_high_is_corroborated():
    """F115 (Sprint 15 Task F) and the team lead's Q3 (2026-11-01): a quote found only in OCR text says "OCR" in its
    anchor; a claim from an image file outside a PDF is HIGH only with a named corroboration. Proven to fail by
    injection, 2026-11-01: with ocr_check emptied, both unmarked and uncorroborated assertions passed."""
    from types import SimpleNamespace
    g = _script()
    text = "a text layer sentence || OCR: words read from a page image"
    ok = SimpleNamespace(id="ok", certainty="high", certainty_reasons="Started HIGH: x",
                         citation_context='"a text layer sentence" (p.1); "words read from a page image" (p.3, OCR)')
    g.ocr_check(ok, "paper.pdf", text)
    bare = SimpleNamespace(**{**vars(ok), "id": "bare", "citation_context": '"words read from a page image" (p.3)'})
    with pytest.raises(ValueError, match="bare: quotes found only in OCR text"):
        g.ocr_check(bare, "paper.pdf", text)
    image = SimpleNamespace(id="img", certainty="high", certainty_reasons="Started HIGH: the slide says so",
                            citation_context='"words" (slide 2, OCR)')
    with pytest.raises(ValueError, match="img: a claim read from an image file is HIGH only"):
        g.ocr_check(image, "slide.png", "OCR: words")
    g.ocr_check(SimpleNamespace(**{**vars(image), "certainty_reasons": "Started HIGH: corroborated by smith-2024-x"}),
                "slide.png", "OCR: words")
    g.ocr_check(SimpleNamespace(**{**vars(image), "certainty": "moderate"}), "slide.png", "OCR: words")


def test_every_refusal_is_named_in_one_run(monkeypatch):
    """Sprint 14 retrospective Q4: a dry run named the first refusal, and each fix found the next. Proven to fail by
    injection, 2026-10-31: with assertions() raising at the first refused record, as before, only a1 was named; with
    verify() raising at the first failed quote check, only `ok`'s refusal was named."""
    from types import SimpleNamespace
    g = _script()
    paper = {"record_id": "p", "file": "f", "existing": [],
             "assertions": [{"id_suggestion": "a1"}, {"id_suggestion": "a2"}, {"id_suggestion": "ok"},
                            {"id_suggestion": "ok2"}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g050", paper)])

    def record(gg, rid, aid, a, why, sid=None):
        if aid in ("a1", "a2"):
            raise ValueError(f"{aid}: no value to write")
        return SimpleNamespace(id=aid, citation_context='"q" (p.1)', value="v")

    def verbatim(aid, *args, **kwargs):
        raise ValueError(f"{aid}: not verbatim in its source")

    monkeypatch.setattr(g, "record", record)
    monkeypatch.setattr(g, "source_text", lambda f: "q")
    monkeypatch.setattr(g, "require_verbatim", verbatim)
    monkeypatch.setattr(g, "validate_assertion", lambda a: None)
    with pytest.raises(ValueError) as e:
        g.verify()
    assert str(e.value).splitlines() == ["4 refused:", "a1: no value to write", "a2: no value to write",
                                         "ok: not verbatim in its source", "ok2: not verbatim in its source"]
    with pytest.raises(ValueError, match="a1"):
        g.assertions()  # without a list to name them in, the first refusal raises, as the apply needs


def test_only_a_new_or_changed_quote_is_checked(monkeypatch):
    """F136 (Sprint 16 Task A; team lead, 2026-11-05: "The quotes only need to be verified once per PDF, ever").
    The applier checked every quote of every reviewed group on each run, about 23 minutes for Sprint 15's 47 groups,
    though a row stored as it would write it gets no quote written. Now: a row stored with the same quotes and value
    is not checked and its source is not read; a new row and a changed quote are checked, and a bad one is still
    refused; so are a changed value and a row an earlier partial read stored (fresh-eyes review). Proven to fail by
    injection, 2026-11-06: with checked_when_stored returning None for every row, the unchanged row was checked and
    its source read; with it returning a check for every row, the changed quote that is not in its source was
    written unrefused; with the value comparison removed, "revalued" went unchecked; with the full-read condition
    removed, "partial" went unchecked. Restored."""
    from types import SimpleNamespace
    g = _script()
    full = f"2026-11-01 (g050): {g.FULL_READ_MARK}: entered"
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, class TEXT, value TEXT, provenance TEXT, updated_reason TEXT)")
    conn.execute("CREATE TABLE assertion_fields (record_id TEXT, citation_context TEXT)")
    for aid, value, why in (("same", "v", full), ("moved", "v", full), ("revalued", "old v", full),
                            ("partial", "v", "2026-10-01 (Sprint 12): from the abstract")):
        conn.execute("INSERT INTO records VALUES (?, 'assertion', ?, 'p, p.1', ?)", (aid, value, why))
        conn.execute("""INSERT INTO assertion_fields VALUES (?, '"q" (p.1)')""", (aid,))
    wanted = {"same": '"q" (p.1)', "moved": '"not in the source" (p.1)', "revalued": '"q" (p.1)',
              "partial": '"q" (p.1)', "new": '"q" (p.2)'}
    paper = {"record_id": "p", "file": "f", "existing": [], "assertions": [{"id_suggestion": i} for i in wanted]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g050", paper)])
    monkeypatch.setattr(g, "record", lambda gg, rid, aid, a, why, sid=None: SimpleNamespace(
        id=aid, citation_context=wanted[aid], value="v", certainty="low", certainty_reasons="", updated="2026-11-01"))
    reads: list = []
    monkeypatch.setattr(g, "source_text", lambda f: reads.append(f) or "the source holds q only")
    monkeypatch.setattr(g, "validate_assertion", lambda a: None)
    with pytest.raises(ValueError) as e:
        g.verify(conn)
    assert str(e.value).splitlines()[1:] == ["moved: not verbatim in its source: 'not in the source'"]
    assert (g.LAST_VERIFY["checked"], g.LAST_VERIFY["stored as written"], len(reads)) == (4, 1, 1)
    for aid in ("moved", "revalued", "partial"):
        del wanted[aid]
    paper["assertions"] = [{"id_suggestion": i} for i in wanted]
    reads.clear()
    conn.execute("INSERT INTO records VALUES ('new', 'assertion', 'v', 'p, p.2', ?)", (full,))
    conn.execute("""INSERT INTO assertion_fields VALUES ('new', '"q" (p.2)')""")  # as the first apply wrote it
    assert [a.id for a, _, _, _ in g.verify(conn)] == ["same", "new"]
    assert (g.LAST_VERIFY["checked"], g.LAST_VERIFY["sources read"], reads) == (0, 0, [])  # the rerun reads nothing


def _corrected_row(monkeypatch, decided: str):
    """A store holding one row 'fixed' with a Manual Validation decision dated `decided`, and a review entry for it
    dated 2026-11-01 whose quote is not in the source. Returns the script module and the store."""
    from types import SimpleNamespace
    g = _script()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, class TEXT, value TEXT, provenance TEXT, updated_reason TEXT)")
    conn.execute("CREATE TABLE assertion_fields (record_id TEXT, citation_context TEXT)")
    reason = (f"2026-10-29 (g050): {g.FULL_READ_MARK}: entered | "
              f"{decided} (Sprint 17 Manual Validation, q23 = a): x")
    conn.execute("INSERT INTO records VALUES ('fixed', 'assertion', 'v', 'p, p.1', ?)", (reason,))
    conn.execute("""INSERT INTO assertion_fields VALUES ('fixed', '"q" (p.1)')""")
    paper = {"record_id": "p", "file": "f", "existing": [], "assertions": [{"id_suggestion": "fixed"}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g050", paper)])
    monkeypatch.setattr(g, "record", lambda gg, rid, aid, a, why, sid=None: SimpleNamespace(
        id=aid, citation_context='"the review quote" (p.1)', value="v", certainty="low", certainty_reasons="",
        updated="2026-11-01"))
    monkeypatch.setattr(g, "source_text", lambda f: "the source holds q only")
    monkeypatch.setattr(g, "validate_assertion", lambda a: None)
    return g, conn


def test_a_row_the_team_lead_corrected_after_the_review_is_neither_checked_nor_written(monkeypatch):
    """Sprint 17 q23 (2026-11-09): a row corrected at Manual Validation after its review differs from the review, and
    the sync refuses to write it back (`sync_assertion`, `decided_day`); verify() must not check its quotes or hand it
    to the write, and the printed counts say it was kept. Proven to fail by injection, 2026-11-09: with
    `decided_later` returning False, the corrected row was checked, and its review quote, not in the source, was
    refused."""
    g, conn = _corrected_row(monkeypatch, "2026-11-09")
    assert g.verify(conn) == []
    assert (g.LAST_VERIFY["checked"], g.LAST_VERIFY["kept by a later decision"]) == (0, 1)
    assert "1 kept by a later decision" in g.verify_counts()


@pytest.mark.parametrize("decided", ["2026-11-01", "2026-10-30"])
def test_a_row_decided_on_or_before_the_review_day_is_still_checked(monkeypatch, decided):
    """The other side of the rule above, from the fresh-eyes review of 2026-11-09: the sync writes a row whose
    decision is not after the review day (`today < decided_day(reason)` is false), so verify() must still check it.
    Here the review quote is not in the source, so the check refuses it. Proven to fail by injection, 2026-11-09:
    with `decided_later` returning True, the row was skipped and nothing was refused."""
    g, conn = _corrected_row(monkeypatch, decided)
    with pytest.raises(ValueError):
        g.verify(conn)


def test_a_field_no_review_item_names_is_refused(synthetic_store, monkeypatch):
    """Sprint 14 retrospective Q2: the reader's context replaced two stored contexts that no review decided, and the
    trial on a copy did not show it. Until Sprint 18 every such field was a line of the apply's log, written anyway;
    F147 (Sprint 18 Task B) refuses it before it is written, through store.ingest.sync_decided_assertion, so the
    apply stops and names it. Proven to fail by injection, 2026-10-31 (as a log line): with decided_fields naming
    every field, no line was logged; with CONTEXT_FIX left out of it, the context the sign-off named was listed.
    Proven again, 2026-11-21: with apply_changes adding the value and the context to every decided set
    (`| {"value", "context"}  # INJECTED`), the first case did not raise and went red. Restored."""
    from dataclasses import make_dataclass
    from store import connect, ingest
    from store.ingest import UndecidedField
    g = _script()
    # A dataclass, not a namespace: the applier rebuilds a confirmed row with dataclasses.replace (Sprint 15 MV)
    row = make_dataclass("Row", ["id", "context", "updated_reason", "updated", ("fidelity", object, None),
                                 ("claim_type", object, None), ("search_scope", object, None),
                                 ("certainty", object, None), ("certainty_reasons", object, None)])
    a = row(id="claim-one", context="qml", updated_reason="n", updated="2026-10-31")
    paper = {"record_id": "p", "existing": [{"id": "claim-one", "verdict": "confirmed"}]}
    monkeypatch.setattr(g, "load_groups", lambda: [])
    monkeypatch.setattr(g, "verify", lambda conn=None: [(a, "p", paper, None)])
    monkeypatch.setattr(ingest, "sync_verified_assertion", lambda *args: ["value", "citation_context", "context"])
    monkeypatch.setattr(g, "REQUOTE", {"claim-one": "fuller quotes"})
    monkeypatch.setattr(g, "CONTEXT_FIX", {"claim-one": "qml"})
    conn = connect(synthetic_store)
    try:
        with pytest.raises(UndecidedField, match=r"1 stored assertions with a field no review decided:\n"
                                                 r"claim-one: no review decided value;"):
            g.apply_changes(conn)
        monkeypatch.setattr(g, "VALUE_REPLACE", {"claim-one": "v2"})
        assert g.apply_changes(conn) == ["update claim-one [value, citation_context, context]"]
        paper["existing"][0]["verdict"] = "corrected"
        monkeypatch.setattr(g, "CONTEXT_FIX", {})
        with pytest.raises(UndecidedField, match=r"claim-one: no review decided context;"):
            g.apply_changes(conn)
    finally:
        conn.close()


def test_an_anchor_fix_on_a_confirmed_stored_assertion_is_written(synthetic_store, monkeypatch):
    """F126 (Sprint 15 Task D): g104's review found muta-hardware-scope-photonic-gkp's passage on PDF p.8, stored as
    p.9; the reader's confirmed entry held no quotes, so REQUOTE had nothing to rebuild from, and an ANCHOR_FIX on a
    confirmed stored assertion was never written. It is now rebuilt from the stored row with only its anchor changed,
    each quote checked again, and a second apply writes nothing. Proven to fail, 2026-11-01, run before the change:
    write_anchor_moves did not exist, and nothing else wrote the anchor; by injection, with ANCHOR_FIX_ON ignored,
    the correction took the group's review day."""
    from store import connect
    g = _script()
    paper = {"record_id": "alpha-2024-first-paper", "file": "alpha.pdf",
             "existing": [{"id": "claim-two", "verdict": "confirmed", "quotes": [], "anchor": "", "value": ""}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g104", paper)])
    monkeypatch.setattr(g, "REVIEWED_ON", {"g104": "2026-11-01"})
    monkeypatch.setattr(g, "ANCHOR_FIX", {"claim-two": "Section V, p.8"})
    monkeypatch.setattr(g, "ANCHOR_FIX_ON", {"claim-two": "2026-11-02 (Sprint 15 Task D, F126)"})
    monkeypatch.setattr(g, "source_text", lambda f: "text with a quoted sentence in it")
    conn = connect(synthetic_store)
    try:
        before = tuple(conn.execute("SELECT value, certainty FROM records WHERE id = 'claim-two'").fetchone())
        assert g.write_anchor_moves(conn) == ["anchor claim-two [provenance, citation_context]"]
        row = conn.execute("SELECT r.provenance, f.citation_context, r.value, r.certainty FROM records r JOIN "
                           "assertion_fields f ON f.record_id = r.id WHERE r.id = 'claim-two'").fetchone()
        assert tuple(row[:2]) == ("alpha-2024-first-paper, Section V, p.8", '"a quoted sentence" (Section V, p.8)')
        assert tuple(row[2:]) == before
        # the correction carries its own day and task, not the group's review day (Sprint 14's g104)
        reason = conn.execute("SELECT updated, updated_reason FROM records WHERE id = 'claim-two'").fetchone()
        assert reason[0] == "2026-11-02"
        assert reason[1].split(" | ")[-1].startswith("2026-11-02 (Sprint 15 Task D, F126): ")
        assert g.write_anchor_moves(conn) == []  # a second apply writes nothing
        monkeypatch.setattr(g, "REQUOTE", {"claim-two": "rebuilt from the reader's quotes"})
        assert g.write_anchor_moves(conn) == []  # REQUOTE's rebuild carries the anchor instead
        monkeypatch.setattr(g, "REQUOTE", {})
        monkeypatch.setattr(g, "source_text", lambda f: "the passage is not here")
        monkeypatch.setattr(g, "ANCHOR_FIX", {"claim-two": "Section V, p.7"})
        with pytest.raises(ValueError, match="claim-two"):
            g.write_anchor_moves(conn)
        # quotes from two places are never collapsed onto one anchor (review of the uncommitted D and E)
        conn.execute("UPDATE assertion_fields SET citation_context = '\"a quoted\" (p.1); \"sentence\" (p.2)' "
                     "WHERE record_id = 'claim-two'")
        monkeypatch.setattr(g, "source_text", lambda f: "text with a quoted sentence in it")
        with pytest.raises(ValueError, match="2 anchors"):
            g.write_anchor_moves(conn)
        # an anchor with its own parentheses is still counted (fresh-eyes review, 2026-11-02: "[^)]*" missed it, so
        # two places read as one). Proven to fail by injection, 2026-11-02, with the old pattern restored.
        conn.execute("UPDATE assertion_fields SET citation_context = '\"a quoted\" (Section 2 (Methods), p.3); "
                     "\"sentence\" (Section 5, p.9)' WHERE record_id = 'claim-two'")
        with pytest.raises(ValueError, match="2 anchors"):
            g.write_anchor_moves(conn)
    finally:
        conn.close()


def test_an_anchor_fix_the_date_guard_would_skip_is_refused_not_dropped(synthetic_store, monkeypatch):
    """Fresh-eyes review, 2026-11-02: when the row changed after the fix's day, sync's date guard wrote nothing and
    the apply said nothing, while the dry run listed the move. Proven to fail by injection, 2026-11-02: with the
    after-sync comparison removed, write_anchor_moves returned [] and the stored anchor stayed p.9."""
    from store import connect
    g = _script()
    paper = {"record_id": "alpha-2024-first-paper", "file": "alpha.pdf",
             "existing": [{"id": "claim-two", "verdict": "confirmed", "quotes": [], "anchor": "", "value": ""}]}
    monkeypatch.setattr(g, "load_groups", lambda: [("g104", paper)])
    monkeypatch.setattr(g, "REVIEWED_ON", {"g104": "2026-11-01"})
    monkeypatch.setattr(g, "ANCHOR_FIX", {"claim-two": "Section V, p.8"})
    monkeypatch.setattr(g, "ANCHOR_FIX_ON", {"claim-two": "2026-11-02 (Sprint 15 Task D, F126)"})
    monkeypatch.setattr(g, "source_text", lambda f: "text with a quoted sentence in it")
    conn = connect(synthetic_store)
    try:
        # a full read changed the row after the fix's day, so sync's guard leaves it as it is
        conn.execute("UPDATE records SET updated = '2026-11-05', updated_reason = ? WHERE id = 'claim-two'",
                     (f"2026-11-05 (a later full read): {g.FULL_READ_MARK}: value confirmed",))
        with pytest.raises(ValueError, match="claim-two: anchor not written"):
            g.write_anchor_moves(conn)
    finally:
        conn.close()


def test_a_record_left_unread_is_entered_later_by_a_re_entry_group(tmp_path, monkeypatch):
    """F125 (Sprint 15 Task C): g113's review left three records unread for F114's next release, and its group file
    and review file are never rewritten, so nothing could enter them later. A re-entry group "g113-r1" holds exactly
    the records g113's review left unread, under its own group file and review; "g113-r2" holds what g113-r1 left.
    Proven to fail, 2026-11-01, run before the change: a re-entry group was refused as not in the ledger."""
    import json
    g = _script()
    ledger = {"groups": {"g113": {"records": [{"record_id": r} for r in ("a", "b", "c")]}}}
    monkeypatch.setattr(g, "ledger", lambda: ledger)
    monkeypatch.setattr(g, "READS_DIR", tmp_path)
    monkeypatch.setattr(g, "REVIEWED_ON", {"g113": "2026-10-31"})
    monkeypatch.setattr(g, "UNREAD", {"g113": {"b": "next release", "c": "next release"}})
    for name, rids in (("g113", ["a"]), ("g113-r1", ["b", "c"]), ("g113-r2", ["c"])):
        (tmp_path / f"group_{name}.json").write_text(json.dumps({"papers": [{"record_id": r} for r in rids]}),
                                                     encoding="utf-8")
    monkeypatch.setattr(g, "ONLY", ["g113", "g113-r1"])
    assert [(x, p["record_id"]) for x, p in g.load_groups()] == [("g113", "a"), ("g113-r1", "b"), ("g113-r1", "c")]
    # a re-entry group may hold only what its predecessor left unread, never a record entered there
    (tmp_path / "group_g113-r1.json").write_text(json.dumps({"papers": [{"record_id": r} for r in "abc"]}),
                                                 encoding="utf-8")
    with pytest.raises(ValueError, match="differ from the ledger"):
        g.load_groups()
    # the second re-entry takes what the first left unread, and only once the first is reviewed
    monkeypatch.setattr(g, "ONLY", ["g113-r2"])
    with pytest.raises(ValueError, match="g113-r1 has no review"):
        g.load_groups()
    monkeypatch.setattr(g, "REVIEWED_ON", {"g113": "2026-10-31", "g113-r1": "2026-11-02"})
    monkeypatch.setattr(g, "UNREAD", {"g113": {"b": "x", "c": "x"}, "g113-r1": {"c": "still unread"}})
    assert [p["record_id"] for _, p in g.load_groups()] == ["c"]
    monkeypatch.setattr(g, "ONLY", ["g999-r1"])
    with pytest.raises(ValueError, match="not in the ledger"):
        g.load_groups()
