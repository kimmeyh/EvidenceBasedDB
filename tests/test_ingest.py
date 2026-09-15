"""Tests for store/ingest.py (Sprint 1 Task E).

ADR-0005 section 2b2: a paper is a source of assertions. These tests
exercise the reusable insert_paper/insert_assertion path Task E proves out
on one paper and Task F will run 46 times.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import create_store  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper  # noqa: E402


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


def test_insert_paper_creates_the_record_and_its_paper_fields(db):
    paper = PaperRecord(
        id="p1", tier="seen", citation="Cite, 2026", access="arXiv:0000.00000",
        disposition="why it matters", context="method", value="a paper",
        updated="2026-09-15", updated_reason="test",
    )
    insert_paper(db, paper)
    db.commit()

    record = db.execute("SELECT class FROM records WHERE id = 'p1'").fetchone()
    assert record["class"] == "paper"

    fields = db.execute("SELECT tier, citation FROM paper_fields WHERE record_id = 'p1'").fetchone()
    assert fields["tier"] == "seen"
    assert fields["citation"] == "Cite, 2026"

    contexts = {r["context_id"] for r in db.execute("SELECT context_id FROM record_contexts WHERE record_id = 'p1'")}
    assert contexts == {"method"}


def test_insert_paper_writes_applicability_rows(db):
    paper = PaperRecord(
        id="p1", tier="screened", citation="Cite", access="arXiv:1", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        applicability=[("qc", "bears on quantum computing"), ("method", "also methodology")],
    )
    insert_paper(db, paper)
    db.commit()

    rows = {
        (r["context_id"], r["rationale"])
        for r in db.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = 'p1'")
    }
    assert rows == {("qc", "bears on quantum computing"), ("method", "also methodology")}


def test_insert_assertion_links_to_its_yielding_paper(db):
    paper = PaperRecord(
        id="p1", tier="read", citation="Cite", access="arXiv:1", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    )
    insert_paper(db, paper)

    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="p1, p1", evidence_tag="N/A",
        context="method", updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion, yielded_by="p1")
    db.commit()

    yields = [r["assertion_id"] for r in db.execute("SELECT assertion_id FROM paper_yields WHERE paper_id = 'p1'")]
    assert yields == ["a1"]


def test_insert_assertion_without_a_yielding_paper_still_works(db):
    """Not every assertion need come from a paper -- ADR-0004 predates
    ADR-0005 and assertions can have other provenance (a results.json row,
    a direct measurement)."""
    assertion = AssertionRecord(
        id="a1", value="a world fact", provenance="direct measurement",
        evidence_tag="PROJ", context="world", updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    yields = db.execute("SELECT * FROM paper_yields WHERE assertion_id = 'a1'").fetchall()
    assert yields == []
    record = db.execute("SELECT class FROM records WHERE id = 'a1'").fetchone()
    assert record["class"] == "assertion"


def test_insert_assertion_writes_supports_and_contradicts(db):
    for rid in ("a1", "a2", "a3"):
        insert_assertion(
            db,
            AssertionRecord(
                id=rid, value=f"claim {rid}", provenance="source", evidence_tag="N/A",
                context="world", updated="2026-09-15", updated_reason="test",
            ),
        )
    db.commit()

    db.execute("DELETE FROM assertion_relations")  # clear, then re-insert with real links
    insert_assertion(
        db,
        AssertionRecord(
            id="a4", value="claim a4", provenance="source", evidence_tag="N/A",
            context="world", supports=["a1"], contradicts=["a2"],
            updated="2026-09-15", updated_reason="test",
        ),
    )
    db.commit()

    relations = {
        (r["to_assertion_id"], r["relation"])
        for r in db.execute("SELECT to_assertion_id, relation FROM assertion_relations WHERE from_assertion_id = 'a4'")
    }
    assert relations == {("a1", "supports"), ("a2", "contradicts")}
