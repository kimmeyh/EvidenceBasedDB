"""Sprint 2 Task C (F4 part 3): the seminal QBoost paper, found already
present in the seed directory during Task C's spot-check against the
source PDFs and confirmed intentional by the team lead.

Regression test for Task C's own finding: the seed directory is not a
fixed snapshot from Sprint 1 -- additions happen over time and are
expected, not a scope-change alarm each time. This test guards the one
addition Task C actually applied, so it cannot silently disappear from
the store.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_EXPORT = ROOT / "export" / "papers.json"


def _papers() -> list[dict]:
    return json.loads(PAPERS_EXPORT.read_text(encoding="utf-8"))


def test_qboost_paper_is_present_at_screened_tier():
    papers = _papers()
    qboost = next(
        (p for p in papers if p["id"] == "neven-2012-qboost-adiabatic-quantum-optimization"),
        None,
    )
    assert qboost is not None, "the QBoost paper (Neven et al. 2012) is missing from the store"
    assert qboost["tier"] == "screened"


def test_qboost_paper_has_applicability_in_qml_and_qc():
    papers = _papers()
    qboost = next(p for p in papers if p["id"] == "neven-2012-qboost-adiabatic-quantum-optimization")
    contexts = {e["context"] for e in qboost["applicability"]}
    # Sprint 4 Task F (F25 D4, 2026-09-19): `ml` added deliberately, not
    # loosened -- QBoost is a boosting framework for large-scale binary
    # classifiers (p.1 abstract; keywords "machine learning, supervised
    # learning, boosting"); `qc` kept because no platform context exists
    # for D-Wave (qc-subsumption rule, docs/INTAKE_WORKFLOW.md section 8).
    assert contexts == {"qml", "qc", "ml"}


def test_seed_set_now_holds_at_least_46_distinct_papers():
    """Sprint 1 Task F loaded 44 distinct records (46 original seed files
    minus 2 exact duplicates). Sprint 2 Task C added one more (the
    QBoost paper), for 45 distinct SEED-SET records. The Lenat/Marcus
    paper (Task E's dry run, not part of the seed set) makes 46 paper
    records in the store overall.

    LOWER BOUND, not an exact count (code review finding, 2026-09-18): the
    seed directory is not a fixed snapshot -- CLAUDE.md and Task C's own
    finding both state additions happen over time and are expected. An
    exact `== 46` assertion would fail CI on the very next expected
    addition, which is the opposite of what this regression test should
    guard: the QBoost addition staying present, not the total staying
    frozen."""
    papers = _papers()
    assert len(papers) >= 46
