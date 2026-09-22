#!/usr/bin/env python3
"""Sprint 1 Task E: ingest the Lenat/Marcus paper end to end.

This is the premise falsifier ADR-0004/ADR-0005 name: a single record with
a real clock on it, run BEFORE Task F commits to loading 46 papers. The
record content below is copied verbatim from ADR-0005 section 2b, "The
first record, as it would be written" -- it is not re-drafted here, since
re-deriving it would measure drafting time, not adjudication time.

Team-lead review, 2026-09-16, found one gap: cyc-general-prover-disabled's
`supports` link names heuristics-over-general-reasoning, which is not one
of the ADR's five listed `yields`. Drafted here from the paper's own
architecture description (p13-14, via docs/research/cyc-knowledge-
representation.md's prior mining of the primary source) rather than left
as a placeholder.

Usage: python scripts/ingest_lenat_marcus.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

UPDATED = "2026-09-15"
UPDATED_REASON = "Sprint 1 Task E: premise-falsifier dry run, one paper ingested end to end"


def main() -> int:
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1

    conn = connect(DB_PATH)

    existing = conn.execute(
        "SELECT id FROM records WHERE id = 'lenat-marcus-2023-trustworthy-ai'"
    ).fetchone()
    if existing:
        print("lenat-marcus-2023-trustworthy-ai already ingested; nothing to do.")
        conn.close()
        return 0

    paper = PaperRecord(
        id="lenat-marcus-2023-trustworthy-ai",
        tier="read",
        # Sprint 4 Task B: declared api-origin (arXiv:2308.04445 resolves); the
        # pre-rendered string below is the Sprint 1 transcription, kept so this
        # historical one-off stays reproducible offline. refresh_citations.py
        # is what verifies it against the API. This script early-returns on the
        # live store, where the record already exists.
        citation_origin="api",
        # A Sprint 1 transcription kept verbatim so this historical one-off
        # stays reproducible offline; refresh_citations.py is what checks it
        # against the API. Declared rather than silently trusted (PR #30 review).
        citation_source="replay",
        citation=(
            "Lenat, D. and Marcus, G., \"Getting from Generative AI to "
            "Trustworthy AI: What LLMs might learn from Cyc\", "
            "arXiv:2308.04445, 31 July 2023"
        ),
        access="arXiv:2308.04445",
        disposition=(
            "Methodology for this library. Mined in full for ADR-0004; it "
            "corrected two beliefs we had recorded"
        ),
        context="method",
        value="Getting from Generative AI to Trustworthy AI: What LLMs might learn from Cyc",
        evidence_tag="N/A",
        evidence="Position paper. No experiment, no measurement. All claims about Cyc are reported by its creator",
        mined_by="2026-09-13, Claude, pp. 1-16",
        checked_against_source="2026-09-13, Claude, read pp. 1-16 directly",
        updated=UPDATED,
        updated_reason=UPDATED_REASON,
        applicability=[("method", "Methodology for how this library builds and reasons")],
    )
    insert_paper(conn, paper)

    yields = [
        # Inserted FIRST: cyc-general-prover-disabled's `supports` link
        # below references this id, and the foreign key requires the
        # target row to exist before it is referenced.
        AssertionRecord(
            id="heuristics-over-general-reasoning",
            value=(
                "Cyc separates the epistemological problem (what the system "
                "knows, expressed in one expressive higher-order logic, CycL) "
                "from the heuristic problem (how to reason efficiently), and "
                "solves the second with many redundant, specialized "
                "Heuristic-Level reasoners rather than one general theorem "
                "prover operating on CycL directly -- 20 such reasoners in "
                "1989, over 1,100 by 2023"
            ),
            provenance="lenat-marcus-2023-trustworthy-ai, p13-14",
            evidence_tag="N/A",
            context="method",
            citation_context=(
                "\"Cyc also allows multiple redundant representations for "
                "each assertion, and in practice it uses multiple redundant, "
                "specialized reasoners -- Heuristic Level (HL) modules -- "
                "each of which is much faster than general theorem-proving "
                "when it applies.\""
            ),
            certainty="low",
            certainty_reasons=(
                "Started LOW -- position paper, first-author description of "
                "the author's own system's architecture, no independent "
                "verification possible. NOT upgraded: unlike footnote 9 "
                "(cyc-general-prover-disabled), this is the system working as "
                "intended and reported favourably, so the admission-against-"
                "interest upgrade does not apply. The reasoner COUNT (20 to "
                "1,100+) is the same self-reported, undefined-unit figure as "
                "cyc-hl-module-count and inherits its caveat"
            ),
            fidelity="exact",
            reading_level=11,
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
        AssertionRecord(
            id="cyc-general-prover-disabled",
            value=(
                "Cyc's general resolution theorem prover was switched off "
                "about a decade before 2023, after timing out on over a "
                "million consecutive queries where it was called as a last resort"
            ),
            provenance="lenat-marcus-2023-trustworthy-ai, p14 footnote 9",
            evidence_tag="N/A",
            context="method",
            citation_context='"we quietly turned the general theorem prover off, so it never gets called on!"',
            certainty="moderate",
            certainty_reasons=(
                "Started LOW -- position paper, first-author testimony about the "
                "author's own system, no independent verification possible. "
                "UPGRADED one level for admission against interest: this "
                "concedes that the system's most general component never "
                "worked, which is costly to disclose and therefore credible. "
                "NOT upgraded further: still unverifiable"
            ),
            fidelity="exact",
            reading_level=11,
            supports=["heuristics-over-general-reasoning"],
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
        AssertionRecord(
            id="cyc-hl-module-count",
            value="Cyc had 20 heuristic-level reasoners in 1989 and over 1,100 by 2023",
            provenance="lenat-marcus-2023-trustworthy-ai, p13",
            evidence_tag="N/A",
            context="method",
            certainty="low",
            certainty_reasons=(
                "Started LOW -- position paper. NOT upgraded: a round "
                "self-reported count with no definition of what counts as a "
                "module and no way to check it. Unlike footnote 9 this is "
                "favourable to the author, so the admission-against-interest "
                "upgrade does not apply"
            ),
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
        # Named in ADR-0005's yields list but not fully worked in the ADR's
        # example -- recorded with the minimal honest fields rather than
        # inventing certainty_reasons the ADR never stated.
        AssertionRecord(
            id="cyc-truth-values-four",
            value="Cyc carries four composite truth values, not five, correcting an earlier assumption in ADR-0004's own drafting",
            provenance="lenat-marcus-2023-trustworthy-ai",
            evidence_tag="N/A",
            context="method",
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
        AssertionRecord(
            id="cyc-no-numeric-confidence",
            value="Cyc carries no numeric confidence on assertions at all",
            provenance="lenat-marcus-2023-trustworthy-ai",
            evidence_tag="N/A",
            context="method",
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
        AssertionRecord(
            id="cyc-context-count",
            value="Cyc has approximately 10,000 named contexts, kept down by computing contexts (IntersectContexts) rather than reifying every combination",
            provenance="lenat-marcus-2023-trustworthy-ai, p15",
            evidence_tag="N/A",
            context="method",
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        ),
    ]

    for assertion in yields:
        insert_assertion(conn, assertion, yielded_by=paper.id)

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print(f"Ingested {paper.id} plus {len(yields)} assertions. Export regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
