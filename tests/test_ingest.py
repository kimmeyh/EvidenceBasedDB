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
from store.export import export_class  # noqa: E402
from store.ingest import (  # noqa: E402
    AssertionRecord,
    PaperRecord,
    add_read,
    insert_assertion,
    insert_paper,
    record_probe,
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
        id="p1", tier="seen", citation_origin="api", citation="Cite, 2026", citation_source="replay",
        access="arXiv:0000.00000",
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
        id="p1", tier="screened", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
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
        id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        checked_against_source="2026-09-15, test fixture", reads=[("test", "2026-09-15", "full", "")],
    )
    insert_paper(db, paper)

    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="p1, p1", evidence_tag="N/A", derivation="extracted",
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
        evidence_tag="PROJ", context="world", updated="2026-09-15", updated_reason="test", derivation="project",
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
        id="a1", value="a claim", provenance="source", evidence_tag="N/A", derivation="extracted",
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


def test_insert_assertion_writes_assertion_fields_with_only_the_required_fields(db):
    """Since ADR-0004 A6 (Sprint 6 Task E) every assertion has an
    assertion_fields row, because `derivation` and `claim_type` are
    required. Until then an assertion with no units/rounding/
    citation_context got no row at all. The three optional fields stay
    NULL, and the export still omits them."""
    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="source", evidence_tag="N/A", derivation="extracted",
        context="world", updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    row = db.execute("SELECT * FROM assertion_fields WHERE record_id = 'a1'").fetchone()
    assert (row["units"], row["rounding"], row["citation_context"]) == (None, None, None)
    assert (row["derivation"], row["claim_type"], row["search_scope"]) == ("extracted", "positive", None)
    exported = export_class(db, "assertion")[0]
    assert not {"units", "rounding", "citation_context", "search_scope"} & set(exported)
    assert (exported["derivation"], exported["claim_type"]) == ("extracted", "positive")


def test_insert_assertion_writes_documents_without_requiring_assertion_fields(db):
    """Regression test for Copilot PR #1 review finding 1:
    assertion_documents previously referenced assertion_fields(record_id),
    forcing an assertion_fields row (units/rounding) to exist before any
    document citation could be attached. An assertion with ONLY a document
    and no units/rounding/citation_context must still be able to record it."""
    assertion = AssertionRecord(
        id="a1", value="a claim", provenance="source", evidence_tag="N/A", derivation="extracted",
        context="world", documents=["docs/paper/appendix.md"],
        updated="2026-09-15", updated_reason="test",
    )
    insert_assertion(db, assertion)
    db.commit()

    fields = db.execute("SELECT units, rounding, citation_context FROM assertion_fields WHERE record_id = 'a1'").fetchone()
    assert tuple(fields) == (None, None, None)
    documents =[r["document"] for r in db.execute("SELECT document FROM assertion_documents WHERE record_id = 'a1'")]
    assert documents == ["docs/paper/appendix.md"]


def test_insert_assertion_writes_supports_and_contradicts(db):
    for rid in ("a1", "a2", "a3"):
        insert_assertion(
            db,
            AssertionRecord(
                id=rid, value=f"claim {rid}", provenance="source", evidence_tag="N/A", derivation="extracted",
                context="world", updated="2026-09-15", updated_reason="test",
            ),
        )
    db.commit()

    db.execute("DELETE FROM assertion_relations")  # clear, then re-insert with real links
    insert_assertion(
        db,
        AssertionRecord(
            id="a4", value="claim a4", provenance="source", evidence_tag="N/A", derivation="extracted",
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
        id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
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
            id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
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
        id="p1", tier="seen", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        applicability=[("method", "fixture rationale -- test")],
    ))
    add_read(db, "p1", "test", "2026-09-19", "full")  # the read_extent gate passes; this rule is next
    with pytest.raises(ValueError, match="checked_against_source"):
        set_tier(db, "p1", "read")
    tier = db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"]
    assert tier == "seen", "a refused promotion must leave the row unchanged"


def test_set_tier_promotes_to_read_when_checked_against_source_is_supplied(db):
    insert_paper(db, PaperRecord(
        id="p1", tier="screened", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        applicability=[("method", "fixture rationale -- test")],
    ))
    add_read(db, "p1", "test", "2026-09-19", "full")
    set_tier(db, "p1", "read", checked_against_source="2026-09-19, test, read in full")
    row = db.execute("SELECT tier, checked_against_source FROM paper_fields WHERE record_id = 'p1'").fetchone()
    assert (row["tier"], row["checked_against_source"]) == ("read", "2026-09-19, test, read in full")


def _screened(db) -> None:
    insert_paper(db, PaperRecord(
        id="p1", tier="screened", citation_origin="api", citation="Cite", citation_source="replay",
        access="arXiv:0000.00001", disposition="why", context="method", value="a paper",
        updated="2026-10-03", updated_reason="test", applicability=[("method", "fixture rationale -- test")],
    ))


@pytest.mark.parametrize("extent", ["grep", "subagent", "summary", "abstract", "html-render"])
def test_set_tier_read_refuses_a_read_that_does_not_qualify_regression(db, extent):
    """ADR-0005 A4 (c), decisions Q3 and Q7 (Sprint 6 Task E): `read` needs
    a 'full' or 'partial' read. One case per refused extent: grep,
    subagent and summary as the plan requires, abstract and html-render
    as A4 adds. Proven to fail by injection: with the read_extent gate
    removed from set_tier, all five promotions went through and every case
    went red."""
    _screened(db)
    add_read(db, "p1", "Claude", "2026-10-03", extent)
    with pytest.raises(ValueError, match="read_extent"):
        set_tier(db, "p1", "read", checked_against_source="2026-10-03, Claude")
    assert db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"] == "screened"


def test_set_tier_read_refuses_when_no_read_is_recorded(db):
    _screened(db)
    with pytest.raises(ValueError, match="not recorded"):
        set_tier(db, "p1", "read", checked_against_source="2026-10-03, Claude")


def test_set_tier_read_accepts_a_named_partial_read_beside_a_subagent(db):
    """Sprint 5's pilot shape: a subagent extracted, the lead checked named pages."""
    _screened(db)
    add_read(db, "p1", "read-only agent", "2026-10-03", "subagent")
    add_read(db, "p1", "Claude", "2026-10-03", "partial", "pp.3-5, Table 2")
    set_tier(db, "p1", "read", checked_against_source="2026-10-03, Claude, pp.3-5 directly")
    assert db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"] == "read"


def test_set_tier_read_needs_the_qualifying_read_by_the_reader_who_checks(db):
    """Fresh-eyes review, 2026-10-03: A4 (c) binds the read to the reader
    who sets checked_against_source. Another reader's partial row does not
    carry Claude's promotion."""
    _screened(db)
    add_read(db, "p1", "agent-x", "2026-10-03", "partial", "pp.1-2")
    with pytest.raises(ValueError, match="reader named"):
        set_tier(db, "p1", "read", checked_against_source="2026-10-03, Claude, pp.1-2 directly")
    set_tier(db, "p1", "read", checked_against_source="2026-10-03, agent-x, pp.1-2 directly")


def test_insert_at_read_holds_the_same_gate_regression(db):
    """Fresh-eyes review, 2026-10-03: the gate lived only in set_tier, so
    `intake --tier read` inserted a read paper with no read recorded.
    Proven to fail by injection: before validate_paper carried the check,
    the first insert below went through."""
    base = dict(id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay",
                access="arXiv:0000.00001", disposition="why", context="method", value="a paper",
                updated="2026-10-03", updated_reason="test", checked_against_source="2026-10-03, Claude, p.2",
                applicability=[("method", "fixture rationale -- test")])
    with pytest.raises(ValueError, match="read_extent"):
        insert_paper(db, PaperRecord(**base))
    insert_paper(db, PaperRecord(**base, reads=[("Claude", "2026-10-03", "partial", "p.2")]))


def test_metadata_provider_is_the_doors_statement(db):
    """A caller-set provider is refused unless the citation is a replay or
    the door's own derivation."""
    base = dict(id="p1", tier="seen", citation_origin="hand", citation="Cite (hand-transcribed from p.1)",
                hand_transcribed_from="p.1", access=__file__, disposition="why", context="method",
                value="a paper", updated="2026-10-03", updated_reason="test")
    with pytest.raises(ValueError, match="metadata_provider"):
        validate_paper(PaperRecord(**base, metadata_provider="Crossref"))
    validate_paper(PaperRecord(**{**base, "citation_origin": "api", "access": "arXiv:0000.00001",
                                  "citation": "Cite", "citation_source": "replay", "hand_transcribed_from": None},
                               metadata_provider="arXiv"))


def test_partial_read_must_say_what_was_read(db):
    _screened(db)
    with pytest.raises(ValueError, match="partial"):
        add_read(db, "p1", "Claude", "2026-10-03", "partial")


def test_assertion_door_refuses_a_missing_derivation_and_an_unscoped_absence(db):
    """ADR-0004 A6 (a) and (f): derivation is the caller's statement, and
    an absence claim needs its search scope."""
    base = dict(id="a1", value="v", provenance="p", evidence_tag="N/A", context="world",
                updated="2026-10-03", updated_reason="test")
    with pytest.raises(ValueError, match="derivation"):
        insert_assertion(db, AssertionRecord(**base))
    with pytest.raises(ValueError, match="search_scope"):
        insert_assertion(db, AssertionRecord(**base, derivation="extracted", claim_type="absence"))
    insert_assertion(db, AssertionRecord(**base, derivation="extracted", claim_type="absence",
                                         search_scope="arXiv full text for 'fault tolerance', 2026-10-03"))


def test_probe_rows_follow_the_probe_rule(db):
    """ADR-0005 A4 (b): one row per computed field, the newer measurement
    replacing the older; a hand-recorded status names its anchor; the
    status vocabulary is the four Q1 values."""
    _screened(db)
    record_probe(db, "p1", "publication_status", "preprint", "arXiv", "2026-10-01")
    record_probe(db, "p1", "publication_status", "withdrawn", "arXiv", "2026-10-03")
    rows = db.execute("SELECT value, probed_on FROM paper_probes WHERE record_id = 'p1'").fetchall()
    assert [tuple(r) for r in rows] == [("withdrawn", "2026-10-03")]
    with pytest.raises(ValueError, match="anchor"):
        record_probe(db, "p1", "publication_status", "retracted", "hand", "2026-10-03")
    with pytest.raises(ValueError, match="publication_status"):
        record_probe(db, "p1", "publication_status", "superseded", "Crossref", "2026-10-03")


def test_set_tier_to_screened_requires_applicability_regression(db):
    """Sprint 5 retrospective improvement 1 (2026-09-25). This test was
    `test_set_tier_to_screened_needs_nothing_extra` and pinned the old
    contract; ADR-0005 Amendment A2 makes applicability `screened`'s
    obligation and the F28 pilot promoted six papers without it. Proven to
    fail by injection: removing the new check in set_tier() lets the first
    promotion through and this goes red. A refused promotion leaves the row
    unchanged; with a row written, the same promotion succeeds."""
    insert_paper(db, PaperRecord(
        id="p1", tier="seen", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    ))
    for tier in ("screened", "read"):
        with pytest.raises(ValueError, match="no applicability"):
            set_tier(db, "p1", tier, checked_against_source="x" if tier == "read" else None)
    assert db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"] == "seen"
    db.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES ('p1', 'method', 'why -- test')")
    set_tier(db, "p1", "screened")
    assert db.execute("SELECT tier FROM paper_fields WHERE record_id = 'p1'").fetchone()["tier"] == "screened"


def _api_paper(**over) -> PaperRecord:
    base = dict(id="p1", tier="seen", access="arXiv:0000.00001", disposition="why",
                context="method", value="a paper", citation="Cite", citation_origin="api",
                # A fixture replays a rendered citation instead of calling the API;
                # the door requires that exception to be declared (PR #30 review).
                citation_source="replay",
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


def test_a_title_word_that_holds_a_marker_is_not_audit_text():
    """Sprint 15 Task J: Babbush et al.'s "Focus beyond quadratic speedups for error-corrected quantum advantage"
    was refused as a "CORRECTED" note. Proven to fail by injection, 2026-11-01: with the substring match restored,
    the citation was refused."""
    validate_paper(_api_paper(citation='Babbush, R., "Focus beyond quadratic speedups for error-corrected quantum '
                                       'advantage," arXiv:2011.04149v2'))


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


def test_validate_paper_refuses_read_tier_with_literal_never():
    """'never' stays a valid value distinct from None for the
    checked_against_source rule (ADR-0005 section 2), but since ADR-0005 A4
    (c) `read` also needs a qualifying read by the reader named in it, and
    'never' names none. This test pinned acceptance until Sprint 6 Task E;
    no record in the store carried 'never' at any tier on 2026-10-03."""
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        checked_against_source="never",
    )
    with pytest.raises(ValueError, match="read_extent"):
        validate_paper(paper)


def test_validate_paper_does_not_require_checked_against_source_below_read():
    """seen/screened tiers correctly have no value yet -- only 'read'
    requires it (ADR-0005 section 2)."""
    for tier in ("seen", "screened"):
        paper = PaperRecord(
            id="p1", tier=tier, citation="Cite", citation_origin="api", citation_source="replay", access="arXiv:0000.00001",
            disposition="why", context="method", value="a paper", updated="2026-09-15", updated_reason="test",
        )
        validate_paper(paper)  # must not raise


def test_insert_paper_calls_validate_paper(db):
    """The validator must actually run at the real insert path, not just
    exist as a standalone function nothing calls."""
    paper = PaperRecord(
        id="p1", tier="read", citation_origin="api", citation="Cite", citation_source="replay", access="arXiv:0000.00001", disposition="why",
        context="method", value="a paper", updated="2026-09-15", updated_reason="test",
    )
    with pytest.raises(ValueError, match="checked_against_source"):
        insert_paper(db, paper)


def test_door_refuses_an_api_citation_the_caller_supplied_without_declaring_a_replay():
    """The escape hatch, closed (PR #30 review, 2026-09-22).

    Until this rule, an api-origin record with a resolvable access could
    carry ANY citation and title, accepted with no network call and no
    complaint -- exactly the dupont/kordzanganeh defect class the whole
    door exists to stop. A fixture or a historical replay is still allowed,
    but it must say so, so the exception is visible in the record and in
    the diff rather than indistinguishable from a derived citation.
    """
    with pytest.raises(ValueError, match="supplied by the caller"):
        validate_paper(PaperRecord(
            id="fake", tier="seen", access="arXiv:2303.05509", disposition="why",
            context="qml", value="A Totally Invented Title",
            citation='Nobody, N., "A Totally Invented Title," arXiv:9999.99999, 1999-01-01',
            citation_origin="api", updated="2026-09-22", updated_reason="probe"))


def test_the_door_marks_what_it_derived_so_a_replay_is_distinguishable(db):
    """derive_citation stamps citation_source='api' on what it fetched. That
    is what lets the rule above tell the door's own output from a caller's
    input without blocking the legitimate path."""
    from tests.test_citations import fake_fetcher  # noqa: PLC0415
    from store.ingest import derive_citation
    paper = PaperRecord(id="dupont", tier="seen", access="arXiv:2303.05509", disposition="why",
                        context="qml", citation_origin="api", updated="2026-09-22", updated_reason="test")
    derived = derive_citation(paper, fetcher=fake_fetcher)
    from store.ingest import DERIVED_BY_DOOR
    # Identity, not equality: the marker is a sentinel object precisely so a
    # caller cannot produce one (PR #30 round-2 review, 2026-09-23).
    assert derived.citation_source is DERIVED_BY_DOOR
    assert derived.citation.startswith('Dupont, M., Evert, B.,')
    validate_paper(derived)  # must not raise


def test_a_declared_replay_is_accepted():
    validate_paper(PaperRecord(
        id="lenat", tier="seen", access="arXiv:2308.04445", disposition="why",
        context="method", value="A Title", citation="A hand-kept Sprint 1 transcription",
        citation_origin="api", citation_source="replay",
        updated="2026-09-22", updated_reason="historical one-off"))


@pytest.mark.parametrize("declared", ["api", "trusted", "derived", "verified", "ok"])
def test_only_the_doors_marker_or_a_declared_replay_is_accepted(declared):
    """The allowed set is CLOSED, and "api" is not in it.

    Round-2 review, 2026-09-23: when the marker was the string "api", a
    caller could type it and the door accepted a fabricated citation with no
    network call -- the rule refused an omission but not a fabrication. The
    door's own marker is now a sentinel object a caller cannot write, and
    every plausible-sounding self-declaration is refused.
    """
    from store.ingest import DERIVED_BY_DOOR, REPLAY
    base = dict(id="fake", tier="seen", access="arXiv:2303.05509", disposition="why",
                context="qml", value="A Fabricated Title",
                citation='Nobody, N., "A Fabricated Title," arXiv:9999.99999, 1999',
                citation_origin="api", updated="2026-09-23", updated_reason="probe")
    with pytest.raises(ValueError, match="supplied by the caller"):
        validate_paper(PaperRecord(**base, citation_source=declared))
    # The two legitimate values still pass.
    validate_paper(PaperRecord(**base, citation_source=DERIVED_BY_DOOR))
    validate_paper(PaperRecord(**base, citation_source=REPLAY))


def test_promotion_removes_not_yet_screened_regression(tmp_path):
    """Team lead, Sprint 5 Manual Validation Q7 (2026-09-25): bulk `seen`
    dispositions keep '; not yet screened' and the clause is removed at
    each promotion, by set_tier itself. Proven to fail by injection: the
    F28 pilot promoted six papers with set_tier before this existed and
    left the clause stale on all six."""
    import sqlite3 as _sq
    from store import create_store
    from store.ingest import NOT_YET_SCREENED, PaperRecord, insert_paper, set_tier
    conn = create_store(tmp_path / "t.db")
    local = tmp_path / "x.pdf"
    local.write_bytes(b"%PDF")
    for pid in ("p-promoted", "p-stays"):
        insert_paper(conn, PaperRecord(
            id=pid, tier="seen", access=str(local), context="method", value="T",
            disposition="Bulk intake 2026-09 from a test" + NOT_YET_SCREENED,
            citation="X, \"T,\" 2026 (hand-transcribed from cover)", citation_origin="hand",
            hand_transcribed_from="cover", updated="2026-09-25", updated_reason="t"))
    conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES "
                 "('p-promoted', 'method', 'fixture -- test')")
    set_tier(conn, "p-promoted", "screened")
    set_tier(conn, "p-stays", "seen")
    disp = dict(conn.execute("SELECT record_id, disposition FROM paper_fields"))
    assert disp["p-promoted"] == "Bulk intake 2026-09 from a test"
    assert disp["p-stays"].endswith(NOT_YET_SCREENED)
    reason = conn.execute("SELECT updated_reason FROM records WHERE id = 'p-promoted'").fetchone()[0]
    assert reason.startswith("t | ") and "not yet screened" in reason, "append-only, and says what changed"
    conn.close()


def test_hollow_saved_page_is_refused_at_the_door_regression(tmp_path):
    """Sprint 5 retrospective improvement 4 (2026-09-25): a hand-origin
    record whose saved .html copy is a shell (bot challenge, JavaScript
    app, redirect stub) is refused. Proven to fail by injection: the exact
    Sprint 5 redirect stub, and a bare page of 8 words, are refused; a page
    with real text passes; a PDF is not word-counted; the rebuild's
    check_local_paths=False skips it with the path check."""
    def rec(path):
        return PaperRecord(id="h1", tier="seen", access=f"{path} | https://example.org/p", context="method",
                           value="T", disposition="Reference: t", citation="X, \"T,\" 2026 (hand-transcribed from page)",
                           citation_origin="hand", hand_transcribed_from="page", updated="2026-09-25", updated_reason="t")
    stub = tmp_path / "stub.html"
    stub.write_text('<meta http-equiv="Refresh" content="0; url=Foreword.html" />', encoding="utf-8")
    shell = tmp_path / "shell.html"
    shell.write_text("<html><script>" + "x" * 5000 + "</script><body>1st Place Solution Part 2 Kaggle loading</body></html>",
                     encoding="utf-8")
    real = tmp_path / "real.html"
    real.write_text("<html><body><p>" + " ".join(["word"] * 60) + "</p></body></html>", encoding="utf-8")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 tiny")
    for hollow in (stub, shell):
        with pytest.raises(ValueError, match="visible words"):
            validate_paper(rec(hollow))
    validate_paper(rec(real))
    validate_paper(rec(pdf))
    validate_paper(rec(stub), check_local_paths=False)


def test_visible_words_keeps_text_between_scripts():
    """Copilot PR #43 review (2026-09-25) read the script-stripping pattern
    as greedy, spanning from the first <script> to the last </script> and
    removing the body text between them. It is lazy (`.*?`) and stops at
    the first closing tag; this pins the two-script case so the claim is
    checked, not argued. Proven to fail by injection: changing `.*?` to
    `.*` in visible_words() drops the count to 30."""
    from store.ingest import visible_words
    html = (b"<html><script>var a=1;</script><p>" + b" ".join([b"visible"] * 30)
            + b"</p><script>var b=2;</script><p>" + b" ".join([b"more"] * 30) + b"</p></html>")
    assert visible_words(html) == 60
