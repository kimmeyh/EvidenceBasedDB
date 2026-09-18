"""Sprint 2 Task A (F4 part 1): every seed-set paper's applicability is
re-derived from real content, not left at Task F's single-context default.

ADR-0005 section 2d defines `applicability` (screened-tier, plural,
"context ids it bears on, plus a sentence saying why") as deliberately
separate from `context` (seen-tier, singular). Sprint 1 Task F set every
paper's `context` but never populated `paper_applicability` -- 44 of 45
papers had an empty applicability array. This guards against that
regressing, and against the two specific judgment calls this task
resolved being silently reverted.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_EXPORT = ROOT / "export" / "papers.json"


def _papers() -> list[dict]:
    return json.loads(PAPERS_EXPORT.read_text(encoding="utf-8"))


def test_almost_every_paper_has_real_applicability():
    """Only the one genuinely empty seed file (0 bytes, no content to
    derive applicability from) may lack applicability. Every other paper
    must have at least one real context claimed."""
    papers = _papers()
    without = [p["id"] for p in papers if not p.get("applicability")]
    assert without == ["pere-qml-github-repo-empty"], (
        f"papers with no applicability: {without}. Only the empty seed "
        "file should lack it -- if a real paper shows up here, its "
        "applicability regressed."
    )


def test_every_applicability_entry_has_a_real_rationale():
    """A context claimed with no rationale is padding, not applicability
    -- ADR-0005 section 2d requires 'a sentence saying why' for each."""
    papers = _papers()
    unrationalized = []
    for p in papers:
        for entry in p.get("applicability", []):
            if not entry.get("rationale") or not entry["rationale"].strip():
                unrationalized.append((p["id"], entry.get("context")))
    assert not unrationalized, f"applicability entries with no rationale: {unrationalized}"


def test_loke_paper_spans_qml_and_platform_dirac_3():
    """Regression test for the specific judgment call this task resolved
    by reading the paper's own page 1 keywords: 'Quantum Machine Learning
    (QML), CVQBoost, ... Dirac-3'. The SMU CVQBoosting paper is not just a
    platform-specific paper; it is also genuinely a QML paper."""
    papers = _papers()
    loke = next(p for p in papers if p["id"] == "loke-2026-cvqboosting-fraud-detection-smu")
    contexts = {e["context"] for e in loke["applicability"]}
    assert contexts == {"platform:dirac-3", "qml"}


def test_emami_paper_confirms_qci_affiliation_in_its_rationale():
    """The one paper in the seed set with confirmed QCi-employee authors
    (verified against the arXiv affiliation block, not assumed from
    subject matter alone) -- directly relevant input for F5's future
    QCi-author identification work."""
    papers = _papers()
    emami = next(p for p in papers if p["id"] == "emami-2025-financial-fraud-entropy-computing-qci")
    contexts = {e["context"] for e in emami["applicability"]}
    assert "platform:dirac-3" in contexts
    dirac_entry = next(e for e in emami["applicability"] if e["context"] == "platform:dirac-3")
    assert "QCi" in dirac_entry["rationale"]


def test_dwave_ebook_was_not_reclassified_as_a_book():
    """Regression test for the OTHER judgment call this task resolved:
    dwave-2023-operational-excellence-ebook is vendor marketing
    collateral (same class as the three standalone D-Wave case-story
    files already in the seed set), not book-class content like
    freericks-2026. It must still carry a normal paper-shaped
    applicability entry, not be excluded the way the Freericks book is."""
    papers = _papers()
    dwave_ebook = next(p for p in papers if p["id"] == "dwave-2023-operational-excellence-ebook")
    assert dwave_ebook["applicability"], (
        "dwave-2023-operational-excellence-ebook has no applicability -- "
        "if it was reclassified as a book/class-mismatch, this test "
        "should be updated to reflect that deliberate decision rather "
        "than silently pass"
    )
    assert dwave_ebook["applicability"][0]["context"] == "qc"


def test_freericks_book_still_correctly_excluded_from_normal_paper_shape():
    """The actual book (an academic textbook, not vendor marketing)
    keeps its class-mismatch disposition from Task F; this task's
    applicability re-derivation did not silently promote it to a normal
    paper."""
    papers = _papers()
    freericks = next(p for p in papers if p["id"] == "freericks-2026-quantum-mechanics-done-right-book")
    assert "book" in freericks["disposition"].lower()
    assert "out of scope" in freericks["disposition"].lower()
