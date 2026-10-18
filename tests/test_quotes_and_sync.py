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
