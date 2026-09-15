#!/usr/bin/env python3
"""Sprint 1 Task E: ingest the Lenat/Marcus paper end to end.

This is the premise falsifier ADR-0004/ADR-0005 name: a single record with
a real clock on it, run BEFORE Task F commits to loading 46 papers. The
record content below is copied verbatim from ADR-0005 section 2b, "The
first record, as it would be written" -- it is not re-drafted here, since
re-deriving it would measure drafting time, not adjudication time.

Usage: python scripts/ingest_lenat_marcus.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper  # noqa: E402

DB_PATH = ROOT / "store" / "evidence.db"
EXPORT_DIR = ROOT / "export"

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

    # heuristics-over-general-reasoning is cited by cyc-general-prover-disabled's
    # `supports` above but is not itself one of the five yields ADR-0005 names.
    # Insert it as a minimal placeholder so the foreign key resolves, flagged
    # for real drafting later -- this is exactly the kind of gap Task E exists
    # to surface before Task F scales to 46 papers.
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('heuristics-over-general-reasoning', 'assertion', "
        "'PLACEHOLDER: Cyc favours many narrow heuristic-level reasoners over one general prover -- not fully drafted, surfaced by Task E', "
        "'lenat-marcus-2023-trustworthy-ai', 'N/A', ?, ?)",
        (UPDATED, "Task E placeholder: referenced by cyc-general-prover-disabled's supports link but not itself one of ADR-0005's five named yields"),
    )
    conn.execute(
        "INSERT INTO record_contexts (record_id, context_id) VALUES ('heuristics-over-general-reasoning', 'method')"
    )

    for assertion in yields:
        insert_assertion(conn, assertion, yielded_by=paper.id)

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print(f"Ingested {paper.id} plus {len(yields)} assertions (and one placeholder). Export regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
