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
from store.ingest import (  # noqa: E402
    AssertionRecord,
    PaperRecord,
    insert_assertion,
    insert_paper,
    set_tier,
    validate_paper,
)


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


def test_insert_paper_creates_the_record_and_its_paper_fields(db):
    paper = PaperRecord(
        id="p1", tier="seen", citation_origin="api", citation="Cite, 2026", access="arXiv:0000.00000",
        disposition="why it matters", context="method", value="a paper",
        updated="2026-09-15", updated_reason="test",
    )
    insert_paper(db, paper)
    db.commit()

    record = db.execute("SELECT class FROM records WHERE id = 'p1'").fetchone()
    assert record["class"] == "paper"

    fields = db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()
    assert fields["tier"] == "seen"
    # The citation lives once, in the spine (Sprint 4 Task B, F25 B4).
    assert db.execute("SELECT provenance FROM records WHERE id = 'p1'").fetchone()["provenance"] == "Cite, 2026"

    contexts = {r["context_id"] for r in db.execute("SELECT context_id FROM record_contexts WHERE record_id = 'p1'")}
    assert contexts == {"method"}


def test_insert_paper_writes_applicability_rows(db):
    paper = PaperRecord(
        id="p1", tier="screened", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        applicability=[("qc", "bears on quantum computing -- fixture"), ("method", "also methodology -- fixture")],
    )
    insert_paper(db, paper)
    db.commit()

    rows = {
        (r["context_id"], r["rationale"])
        for r in db.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = 'p1'")
    }
    assert rows == {("qc", "bears on quantum computing -- fixture"), ("method", "also methodology -- fixture")}


def test_insert_assertion_links_to_its_yielding_paper(db):
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        checked_against_source="2026-09-15, test fixture",
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


def test_insert_assertion_writes_units_rounding_and_citation_context(db):
    """Regression test for Copilot PR #1 review finding 2: citation_context
    was accepted by the dataclass and populated by a real ingestion script
    but had no column anywhere and was silently dropped."""
    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="source", evidence_tag="N/A",
        context="world", units="AUPRC", rounding="4 decimal places",
        citation_context='"the exact sentence making the claim"',
        updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    fields = db.execute(
        "SELECT units, rounding, citation_context FROM assertion_fields WHERE record_id = 'a1'"
    ).fetchone()
    assert fields["units"] == "AUPRC"
    assert fields["rounding"] == "4 decimal places"
    assert fields["citation_context"] == '"the exact sentence making the claim"'


def test_insert_assertion_does_not_write_assertion_fields_when_all_optional_fields_are_none(db):
    """An assertion with no units/rounding/citation_context gets no
    assertion_fields row at all -- there is no reason to carry an
    all-NULL row for the common case."""
    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="source", evidence_tag="N/A",
        context="world", updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    row = db.execute("SELECT * FROM assertion_fields WHERE record_id = 'a1'").fetchone()
    assert row is None


def test_insert_assertion_writes_documents_without_requiring_assertion_fields(db):
    """Regression test for Copilot PR #1 review finding 1:
    assertion_documents previously referenced assertion_fields(record_id),
    forcing an assertion_fields row (units/rounding) to exist before any
    document citation could be attached. An assertion with ONLY a document
    and no units/rounding/citation_context must still be able to record it."""
    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="source", evidence_tag="N/A",
        context="world", documents=["docs/paper/appendix.md"],
        updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    assert db.execute("SELECT * FROM assertion_fields WHERE record_id = 'a1'").fetchone() is None
    documents = [r["document"] for r in db.execute("SELECT document FROM assertion_documents WHERE record_id = 'a1'")]
    assert documents == ["docs/paper/appendix.md"]


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


def test_validate_paper_rejects_read_tier_with_no_checked_against_source():
    """F6 finding 2 (PR #1 review): schema.sql's own comment documents
    checked_against_source as REQUIRED at tier='read', "enforced at the
    application layer" -- but no such enforcement existed. insert_paper()
    accepted any tier/checked_against_source combination unchecked."""
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    )
    with pytest.raises(ValueError, match="checked_against_source"):
        validate_paper(paper)


def test_validate_paper_rejects_read_tier_with_blank_checked_against_source():
    """Copilot PR #20 review (2026-09-19): an empty or whitespace-only
    string previously satisfied the read-tier rule, letting the required
    field be effectively missing while passing validation."""
    for blank in ("", "   ", "\t\n"):
        paper = PaperRecord(
            id="p1", tier="read", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
            context="method", value="a paper", updated="2026-09-15", updated_reason="test",
            checked_against_source=blank,
        )
        with pytest.raises(ValueError, match="blank"):
            validate_paper(paper)


def test_set_tier_refuses_read_without_checked_against_source(db):
    """PR #20 review (2026-09-19): validate_paper() ran on insert only; a
    raw UPDATE to tier='read' bypassed it. set_tier() is the one sanctioned
    tier writer and applies the same rule against the row's existing value."""
    insert_paper(db, PaperRecord(
        id="p1", tier="seen", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    ))
    with pytest.raises(ValueError, match="checked_against_source"):
        set_tier(db, "p1", "read")
    tier = db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"]
    assert tier == "seen", "a refused promotion must leave the row unchanged"


def test_set_tier_promotes_to_read_when_checked_against_source_is_supplied(db):
    insert_paper(db, PaperRecord(
        id="p1", tier="screened", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    ))
    set_tier(db, "p1", "read", checked_against_source="2026-09-19, test, read in full")
    row = db.execute("SELECT tier, checked_against_source FROM paper_fields WHERE record_id = 'p1'").fetchone()
    assert (row["tier"], row["checked_against_source"]) == ("read", "2026-09-19, test, read in full")


def test_set_tier_to_screened_needs_nothing_extra(db):
    insert_paper(db, PaperRecord(
        id="p1", tier="seen", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    ))
    set_tier(db, "p1", "screened")
    assert db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"] == "screened"


def _api_paper(**over) -> PaperRecord:
    base = dict(id="p1", tier="seen", access="arXiv:0000.00001", disposition="why",
                context="method", value="a paper", citation="Cite", citation_origin="api",
                updated="2026-09-15", updated_reason="test")
    base.update(over)
    return PaperRecord(**base)


def test_door_refuses_an_undeclared_citation_origin():
    with pytest.raises(ValueError, match="citation_origin must be declared"):
        validate_paper(_api_paper(citation_origin=""))


def test_door_refuses_api_origin_without_a_resolvable_id():
    with pytest.raises(ValueError, match="no arXiv id or DOI"):
        validate_paper(_api_paper(access="local file, no DOI/arXiv id"))


def test_door_refuses_hand_typing_when_the_id_resolves(tmp_path):
    """The F10 defect class, refused at the door: a citation typed by hand
    for a paper whose arXiv id would have given the true one."""
    with pytest.raises(ValueError, match="hand-typing a citation for it"):
        validate_paper(_api_paper(citation_origin="hand", hand_transcribed_from="cover",
                                  citation="Cite (hand-transcribed from cover)"))


def test_door_hand_origin_requires_page_marker_and_real_path(tmp_path):
    pdf = tmp_path / "vendor.pdf"
    pdf.write_bytes(b"%PDF")
    good = _api_paper(citation_origin="hand", access=str(pdf), hand_transcribed_from="cover",
                      citation='Vendor, "Doc" (hand-transcribed from cover)')
    validate_paper(good)  # must not raise
    # "<path> | <url>" keeps an id-less web page (PMLR, an institutional
    # repository) beside the file; the path still has to exist.
    validate_paper(_api_paper(citation_origin="hand", access=f"{pdf} | https://proceedings.mlr.press/v25/neven12/",
                              hand_transcribed_from="cover", citation='Vendor, "Doc" (hand-transcribed from cover)'))
    with pytest.raises(ValueError, match="not an existing local path"):
        validate_paper(_api_paper(citation_origin="hand", access=f"{tmp_path / 'missing.pdf'} | https://example.org/",
                                  hand_transcribed_from="cover", citation='Vendor, "Doc" (hand-transcribed from cover)'))
    with pytest.raises(ValueError, match="requires hand_transcribed_from"):
        validate_paper(_api_paper(citation_origin="hand", access=str(pdf), citation="x (hand-transcribed from cover)"))
    with pytest.raises(ValueError, match="say so visibly"):
        validate_paper(_api_paper(citation_origin="hand", access=str(pdf), hand_transcribed_from="cover", citation="Vendor, Doc"))
    with pytest.raises(ValueError, match="not an existing local path"):
        validate_paper(_api_paper(citation_origin="hand", access="local file, no DOI/arXiv id",
                                  hand_transcribed_from="cover", citation="x (hand-transcribed from cover)"))


@pytest.mark.parametrize("marker", ["CORRECTED 2026-09-16: ...", "NOTE: the seed filename truncates", "verified against the PDF", "recorded once", "Two identically-content files"])
def test_door_refuses_audit_trail_inside_the_citation(marker):
    with pytest.raises(ValueError, match="audit-trail"):
        validate_paper(_api_paper(citation=f"Cite, 2026. {marker}"))


def test_door_refuses_multiline_disposition_and_a_tier_named_in_prose():
    with pytest.raises(ValueError, match="one line"):
        validate_paper(_api_paper(disposition="line one\nline two"))
    with pytest.raises(ValueError, match="names a tier"):
        validate_paper(_api_paper(disposition="Recorded as seen tier with this disposition"))
    # The Sprint 1 phrasing on 8 of 46 live dispositions (Task C measurement):
    for phrase in ("genuine screened candidate", "Solid screened/read candidate", "near-certain read-tier candidate"):
        with pytest.raises(ValueError, match="names a tier"):
            validate_paper(_api_paper(disposition=f"Real paper; {phrase} at the checkpoint"))
    validate_paper(_api_paper(disposition="Read in full for ADR-0004; the candidate algorithm is QBoost"))  # plain words stay legal


def test_door_requires_a_source_anchor_on_every_applicability_rationale():
    with pytest.raises(ValueError, match="no source anchor"):
        validate_paper(_api_paper(applicability=[("qc", "bears on quantum computing")]))
    validate_paper(_api_paper(applicability=[("qc", "bears on quantum computing -- p.1 abstract")]))


def test_door_requires_a_title():
    with pytest.raises(ValueError, match="title"):
        validate_paper(_api_paper(value="   "))


def test_insert_paper_derives_citation_and_title_from_the_source_of_record(db):
    """The whole point of the door: an api-origin paper arrives with an id
    and nothing else; the citation and title come from the API (here a
    fixture fetcher), and the store's provenance is the rendered string."""
    from tests.test_citations import fake_fetcher  # noqa: PLC0415
    paper = PaperRecord(id="dupont", tier="seen", access="arXiv:2303.05509", disposition="why",
                        context="qc", citation_origin="api", updated="2026-09-19", updated_reason="test")
    written = insert_paper(db, paper, fetcher=fake_fetcher)
    db.commit()
    row = db.execute("SELECT value, provenance FROM records WHERE id='dupont'").fetchone()
    assert row["value"] == "Quantum-Enhanced Greedy Combinatorial Optimization Solver"
    assert row["provenance"].startswith('Dupont, M., Evert, B., "Quantum-Enhanced')
    assert written.citation == row["provenance"] and written.value == row["value"]


def test_validate_paper_accepts_read_tier_with_literal_never():
    """'never' is a valid, meaningful value distinct from None -- a
    statement someone made, not an unpopulated field (ADR-0005 section 2)."""
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        checked_against_source="never",
    )
    validate_paper(paper)  # must not raise


def test_validate_paper_does_not_require_checked_against_source_below_read():
    """seen/screened tiers correctly have no value yet -- only 'read'
    requires it (ADR-0005 section 2)."""
    for tier in ("seen", "screened"):
        paper = PaperRecord(
            id="p1", tier=tier, citation="Cite", citation_origin="api", access="arXiv:0000.00001",
            disposition="why", context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        )
        validate_paper(paper)  # must not raise


def test_insert_paper_calls_validate_paper(db):
    """The validator must actually run at the real insert path, not just
    exist as a standalone function nothing calls."""
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    )
    with pytest.raises(ValueError, match="checked_against_source"):
        insert_paper(db, paper)
