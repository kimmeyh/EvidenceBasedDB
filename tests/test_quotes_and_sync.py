"""Sprint 9 retrospective I3 and I4 (2026-10-17): the one quote normalizer
and check (store/quotes.py), and the one assertion sync that compares every
field (store.ingest.sync_assertion).

Proven to fail by injection, 2026-10-17:
- with the NFKC line removed from `quotes.plain`, the ligature and
  micro-sign cases of test_plain_folds_compatibility_forms went red (2 of
  15). The en-space and no-break-space cases stayed green: Python's `\\s`
  already matches both, so whitespace collapsing covers them without NFKC;
- with "citation_context" removed from `_SYNC_FIELD_COLUMNS`, every sync
  test (7) and the f78 live-copy drift test went red with "does not know
  where these AssertionRecord fields are stored" -- the Task E gap, now
  refused on the first call instead of passing silently.
Each restored, green. Review of 3a455ce, injected 2026-10-18: with "units"
moved from `_SYNC_FIELD_COLUMNS` to `_SYNC_NOT_COMPARED`, the coverage test
and the units case went red; with the context DELETE removed, the context
test went red. Restored, green.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, ingest, quotes  # noqa: E402
from store.ingest import AssertionRecord, sync_assertion  # noqa: E402


@pytest.mark.parametrize("source, quote", [
    ("an eﬃcient and eﬀective ﬂow", "an efficient and effective flow"),  # ligatures
    ("Theorem 1 (Chen)", "Theorem 1 (Chen)"),  # en space, Chen 2025
    ("about 5 dB", "about 5 dB"),  # no-break space
    ("pulses of 1 µs", "pulses of 1 μs"),  # micro sign and Greek mu
    ("the “qudit,” and it’s", "the \"qudit,\" and it's"),  # typographic quotes
    ("a sentence that\n12\ncrosses a page", "a sentence that crosses a page"),  # page number line
])
def test_plain_folds_compatibility_forms(source, quote):
    assert quotes.plain(quote) in quotes.plain(source)


def test_require_verbatim_refuses_a_missing_quote_and_a_bare_context():
    text = quotes.plain("The bound holds for any prior distribution.")
    quotes.require_verbatim("ok", '"holds for any prior" (p.1)', text)
    with pytest.raises(ValueError, match="not verbatim"):
        quotes.require_verbatim("bad", '"holds for every prior" (p.1)', text)
    with pytest.raises(ValueError, match="no quote"):
        quotes.require_verbatim("bare", "p.1, no quote at all", text)


def _stored(conn) -> AssertionRecord:
    """claim-one as conftest's synthetic store writes it."""
    return AssertionRecord(
        id="claim-one", value="value of claim-one", provenance="alpha-2024-first-paper, p.1", evidence_tag="N/A",
        context="qml", certainty="low", certainty_reasons="fixture", derivation="extracted",
        citation_context='"a quoted sentence" (p.1)', updated="2026-10-06", updated_reason="fixture")


def test_sync_writes_nothing_when_the_record_matches(synthetic_store):
    conn = connect(synthetic_store)
    try:
        assert sync_assertion(conn, _stored(conn), "note", "2026-10-17") == []
        assert conn.execute("SELECT updated FROM records WHERE id = 'claim-one'").fetchone()[0] == "2026-10-06"
    finally:
        conn.close()


# One corrected value per compared column. test_every_compared_column_is_tested
# fails when a column is added to, or moved out of, the compared groups
# without a case here (review of 3a455ce: moving a field into
# _SYNC_NOT_COMPARED turned nothing red, and only 5 of 13 were tested).
CHANGES = {
    "value": "a corrected value",
    "provenance": "alpha-2024-first-paper, p.2",
    "evidence_tag": "SIM",
    "certainty": "moderate",
    "certainty_reasons": "corrected reasons",
    "fidelity": "exact",
    "reading_level": 14,
    "units": "percent",
    "rounding": "two decimals",
    "citation_context": '"a corrected sentence" (p.2)',
    "derivation": "project",
    "claim_type": "vendor-self-claim",
    "search_scope": "arXiv listing, 2026-10-17",
}


def test_every_compared_column_is_tested_and_only_history_is_not_compared():
    assert set(CHANGES) == set(ingest._SYNC_RECORD_COLUMNS + ingest._SYNC_FIELD_COLUMNS)
    assert ingest._SYNC_NOT_COMPARED == ("id", "updated", "updated_reason")


@pytest.mark.parametrize("column", sorted(CHANGES))
def test_sync_brings_every_field_to_the_script(synthetic_store, column):
    conn = connect(synthetic_store)
    try:
        wanted = replace(_stored(conn), **{column: CHANGES[column]})
        assert sync_assertion(conn, wanted, "2026-10-17 (test): corrected", "2026-10-17") == [column]
        table, key = (("assertion_fields", "record_id") if column in ingest._SYNC_FIELD_COLUMNS
                      else ("records", "id"))
        assert conn.execute(f"SELECT {column} FROM {table} WHERE {key} = 'claim-one'").fetchone()[0] == CHANGES[column]
        updated, reason = conn.execute("SELECT updated, updated_reason FROM records WHERE id = 'claim-one'").fetchone()
        assert updated == "2026-10-17" and reason.endswith(f"corrected (fields: {column})")
    finally:
        conn.close()


def test_sync_moves_a_claim_to_absence_with_its_search_scope(synthetic_store):
    """Sprint 13 Task G's trial apply, 2026-10-27: the sync wrote one column at a time, so a claim moving to
    'absence' broke the table's CHECK (an absence needs a search scope) on the claim_type step, before
    search_scope was written. Proven to fail by injection, 2026-10-27: with the one-statement UPDATE put back to
    one UPDATE per column, this test went red with "CHECK constraint failed"."""
    conn = connect(synthetic_store)
    try:
        wanted = replace(_stored(conn), claim_type="absence", search_scope="the paper's own text, as read")
        assert sorted(sync_assertion(conn, wanted, "note", "2026-10-27")) == ["claim_type", "search_scope"]
        assert tuple(conn.execute("SELECT claim_type, search_scope FROM assertion_fields WHERE record_id = 'claim-one'"
                                  ).fetchone()) == ("absence", "the paper's own text, as read")
    finally:
        conn.close()


def test_sync_adds_relations_and_documents_and_never_removes_them(synthetic_store):
    """claim-one's `supports` link to learning-fixture was written by
    another step (conftest, as F46's merges are in the store); a reading
    script's record does not name it, and the sync must keep it."""
    conn = connect(synthetic_store)
    try:
        wanted = replace(_stored(conn), contradicts=["claim-two"], documents=["docs/x.md"])
        assert sorted(sync_assertion(conn, wanted, "note", "2026-10-17")) == ["contradicts", "documents"]
        links = set(tuple(r) for r in conn.execute("SELECT to_assertion_id, relation FROM assertion_relations "
                                 "WHERE from_assertion_id = 'claim-one'"))
        assert links == {("learning-fixture", "supports"), ("claim-two", "contradicts")}
    finally:
        conn.close()


def test_a_corrected_context_replaces_the_wrong_one(synthetic_store):
    """Review of 3a455ce: adding the corrected context beside the wrong one
    left the wrong one in place for good. Proven to fail by injection,
    2026-10-18: with the DELETE before the context INSERT removed, the
    stored contexts were {'qml', 'ml'} and this test went red."""
    conn = connect(synthetic_store)
    try:
        assert sync_assertion(conn, replace(_stored(conn), context="ml"), "note", "2026-10-18") == ["context"]
        stored = {r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = 'claim-one'")}
        assert stored == {"ml"}
    finally:
        conn.close()


def test_a_sync_dated_before_a_team_lead_decision_is_refused(synthetic_store):
    """Sprint 15 Manual Validation: a rerun of sprint12_reading.py (dated 2026-10-23) moved
    qng-study-scope-toy-model's context back from qc, the team lead's Q6 = 2, because the date guard held only
    full-read rows. A sync dated before the row's latest Manual Validation note is now refused; one dated on or
    after it goes through. Proven to fail by injection, 2026-11-05: with the decided_day check disabled, the older
    sync here returned ["context"], and sprint12_reading's second-apply test [G] on the live store went red."""
    conn = connect(synthetic_store)
    try:
        conn.execute("UPDATE records SET updated = '2026-11-05', updated_reason = updated_reason || ? "
                     "WHERE id = 'claim-one'", (" | 2026-11-05 (Sprint 15 Manual Validation, Q6 = 2): context",))
        assert ingest.decided_day(conn.execute("SELECT updated_reason FROM records WHERE id = 'claim-one'"
                                               ).fetchone()[0]) == "2026-11-05"
        assert sync_assertion(conn, replace(_stored(conn), context="ml"), "2026-10-23 (old): x", "2026-10-23") == []
        assert {r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = 'claim-one'")} \
            == {"qml"}
        assert sync_assertion(conn, replace(_stored(conn), context="ml"), "2026-11-05 (same day): x", "2026-11-05") \
            == ["context"]  # on the decision's own day it goes through (fresh-eyes review, the boundary)
        assert sync_assertion(conn, replace(_stored(conn), context="qml"), "2026-11-06 (later): x", "2026-11-06") \
            == ["context"]
    finally:
        conn.close()


def test_a_decision_named_in_a_note_body_is_found():
    """Fresh-eyes review, 2026-11-05: Sprint 8 and 9 wrote their grade decisions in the note's body, under a task
    header. Proven to fail by injection, 2026-11-05: with the body branch removed, decided_day returned ""."""
    history = ("2026-10-01 (Sprint 6 Task B): entered | 2026-10-13 (Sprint 8 Task C, F65 and F63): certainty "
               "UPGRADED to HIGH, the team lead's decision at Sprint 8 Manual Validation (Q7) | 2026-10-20 (x): note")
    assert ingest.decided_day(history) == "2026-10-13"
    assert ingest.decided_day("2026-10-01 (Sprint 6 Task B): entered") == ""
    assert ingest.decided_day(None) == ""


def test_a_field_with_no_storage_group_is_refused(synthetic_store, monkeypatch):
    """The Task E defect, by construction: a field left out of the groups."""
    monkeypatch.setattr(ingest, "_SYNC_FIELD_COLUMNS",
                        tuple(c for c in ingest._SYNC_FIELD_COLUMNS if c != "citation_context"))
    conn = connect(synthetic_store)
    try:
        with pytest.raises(TypeError, match="citation_context"):
            sync_assertion(conn, _stored(conn), "note", "2026-10-17")
    finally:
        conn.close()


def test_a_row_re_read_in_full_is_left_alone_by_an_older_script(synthetic_store):
    """Sprint 13 Task G (F113): once a whole-paper re-read has synced a row,
    an older reading script's sync (its second-apply test runs it again)
    must not put the partial read's value back; Task G's own next sync still
    goes through. Proven to fail, 2026-10-25: with the guard in
    sync_assertion removed, the older script's value replaced Task G's.

    Review of 0765e9a: the guard first asked only whether the note named the
    full read, so a LATER correction from any other script was refused too,
    and so was a row Task G only annotated. The test is now the date: older
    or same-day syncs are refused and leave the history as it was; a later
    one goes through. Proven to fail, 2026-10-26: with the date test removed
    from the guard, the later correction was refused.

    Review of 6d8dec7: a sync naming the full read skipped the date test, so
    Task G's next apply, which re-syncs every reviewed group at its review
    date, put an older value back over a later correction and moved
    `updated` back. A full-read sync dated before the row's last change is
    now refused too, once the row's history carries the full read.

    Review of 9c79048: the same-day refusal looked for the full read anywhere
    in the history, so a second correction on the day of a first was refused.
    It now asks whether the last change was the full read."""
    conn = connect(synthetic_store)
    try:
        older = _stored(conn)
        task_g = replace(older, value="the value from the whole paper")
        assert "value" in sync_assertion(conn, task_g, f"Sprint 13 Task G: {ingest.FULL_READ_MARK}", "2026-10-25")
        history = conn.execute("SELECT updated_reason FROM records WHERE id = 'claim-one'").fetchone()[0]
        for day in ("2026-10-23", "2026-10-25"):
            assert sync_assertion(conn, older, f"{day} (Sprint 12 reading): corrected", day) == []
        assert tuple(conn.execute("SELECT value, updated_reason FROM records WHERE id = 'claim-one'").fetchone()) == (
            task_g.value, history)
        again = replace(task_g, value="a corrected value from the whole paper")
        assert sync_assertion(conn, again, f"Sprint 13 Task G: {ingest.FULL_READ_MARK}", "2026-10-26") == ["value"]
        later = replace(again, value="a correction made after the full read")
        assert sync_assertion(conn, later, "2026-11-02 (Sprint 14): corrected", "2026-11-02") == ["value"]
        assert conn.execute("SELECT value FROM records WHERE id = 'claim-one'").fetchone()[0] == later.value
        # review of 6d8dec7: Task G's next apply re-syncs every reviewed group at its review date
        assert sync_assertion(conn, again, f"Sprint 13 Task G: {ingest.FULL_READ_MARK}", "2026-10-26") == []
        assert tuple(conn.execute("SELECT value, updated FROM records WHERE id = 'claim-one'").fetchone()) == (
            later.value, "2026-11-02")
        # review of 9c79048: a second correction on the day of a first is not a re-apply of the full read
        second = replace(later, value="a second correction the same day")
        assert sync_assertion(conn, second, "2026-11-02 (Sprint 14): corrected again", "2026-11-02") == ["value"]
    finally:
        conn.close()
