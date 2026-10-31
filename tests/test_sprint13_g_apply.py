"""Sprint 13 Task G (F113): two guards of scripts/sprint13_g_reading.py, from
the fresh-eyes review of 6d8dec7. Neither opens the real store here.
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

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


@pytest.mark.live_store
def test_the_apply_writes_its_refusal_notes_through_refusal_reason_and_nothing_else(monkeypatch, live_copy):
    """Review of ed5ab01: the test above calls refusal_reason directly, so an inline reason at the call site would
    stay green. On a copy of the store, a sentinel reason must reach every refused paper's note, and a re-apply must
    write nothing else. Proven to fail by injection, 2026-10-30: with the call site reading `why_not` inline, the
    sentinel was absent from darji-2024's note."""
    from store import connect
    g = _script()
    monkeypatch.setattr(g, "refusal_reason", lambda p: "SENTINEL-REASON")
    conn = connect(live_copy)
    try:
        log = g.apply_changes(conn)
        note = conn.execute("SELECT updated_reason FROM records WHERE id = ?",
                            ("darji-2024-robust-super-resolution-classifier-nonlinear",)).fetchone()[0]
    finally:
        conn.close()
    assert note.endswith("NOT entered: SENTINEL-REASON")
    assert [x for x in log if not x.startswith(("exists", "refuse "))] == []


@pytest.mark.live_store
def test_a_stored_assertion_keeps_its_context_against_the_readers_label(monkeypatch, live_copy):
    """Sprint 14 suite after the 2026-10-31 apply: the reader's nearest-fit context replaced two stored contexts that
    no review decided, among them a `platform:dirac-3` (F65 classes every Dirac-3 assertion). On a copy of the store
    set to the contexts an earlier intake chose, an apply must leave them. The sign-off now restores both through
    `context_fix`, which would pass this test with no check at all (review of 0eddd23), so the test takes them out of
    it. Proven to fail by injection, 2026-10-31: with the stored-context check removed from apply_changes, ballin-2026's
    assertion came back `qc`."""
    from store import connect
    g = _script()
    kept = {"dirac3-stratification-falls-short-ballin-2026": "platform:dirac-3",
            "abbas-effective-dimension-generalisation-bound": "qml"}
    monkeypatch.setattr(g, "CONTEXT_FIX", {k: v for k, v in g.CONTEXT_FIX.items() if k not in kept})
    conn = connect(live_copy)
    try:
        for rid, ctx in kept.items():
            conn.execute("UPDATE record_contexts SET context_id = ? WHERE record_id = ?", (ctx, rid))
        conn.commit()
        g.apply_changes(conn)
        got = {rid: [r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))]
               for rid in kept}
    finally:
        conn.close()
    assert got == {rid: [ctx] for rid, ctx in kept.items()}


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
