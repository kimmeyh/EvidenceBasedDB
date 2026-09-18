#!/usr/bin/env python3
"""Sprint 2 Task B (F4 part 2): ingest a real HSBC-submission assertion so
Task B has something to actually spot-check against.

ADR-0004's own motivating case (section: "The problem, in the project's
own evidence") names B1's variable count as one of six documented figure-
provenance defects the consumer repository shipped: "B1's variable count
read 78 in three places and 91 in two, in the same submission" (F52). The
store held zero HSBC-derived assertions before this task -- Task E's dry
run only ingested the Lenat/Marcus methodology paper -- so there was
nothing for Task B to spot-check.

Ingests the CORRECTED assertion (91, not 78), sourced from the consumer
repository's own frozen preregistration amendments A25 and A30 (read-only,
per the 2026-09-15 standing rule), with the wrong value recorded as a
`contradicts`-linked assertion so the correction itself is checkable in
the store rather than only in prose.

Usage: python scripts/ingest_hsbc_b1_variable_count.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import AssertionRecord, insert_assertion  # noqa: E402

DB_PATH = ROOT / "store" / "evidence.db"
EXPORT_DIR = ROOT / "export"

UPDATED = "2026-09-17"
UPDATED_REASON = "Sprint 2 Task B: ingest a real HSBC-submission assertion so Task B has something to spot-check"

# Provenance: hsbc-quantum-fraud-2026/experiments/PREREGISTRATION.md,
# amendments A25 (2026-09-10) and A30 (2026-09-10). Read directly from the
# consumer repository's own frozen document, not from ADR-0004's summary
# table -- the summary names the DEFECT, the amendment log carries the
# CORRECTED figure and its derivation.
PREREG_PROVENANCE = (
    "hsbc-quantum-fraud-2026/experiments/PREREGISTRATION.md, amendments "
    "A25 and A30 (2026-09-10)"


)


def main() -> int:
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1

    conn = connect(DB_PATH)

    # This guard only covers the all-or-nothing case: a full prior run, or
    # none at all. It does NOT detect a partially-corrupted state (e.g. the
    # 'wrong' record manually deleted but this one left behind) -- a re-run
    # from that state hits a primary-key IntegrityError on the 'wrong'
    # insert below, which is the correct (loud) failure, not a silent one,
    # but "already ingested; nothing to do" would be a misleading message
    # to have printed on the way to it. Code review finding, 2026-09-18.
    if conn.execute("SELECT id FROM records WHERE id = 'hsbc-b1-variable-count'").fetchone():
        print("hsbc-b1-variable-count already ingested; nothing to do.")
        conn.close()
        return 0

    # The WRONG value, inserted first so the correct assertion can
    # `contradicts` it (the foreign key requires the target to exist).
    wrong = AssertionRecord(
        id="hsbc-b1-variable-count-wrong-78",
        value=(
            "B1's variable count is 78 -- WRONG, retained as a record of "
            "the defect, not a live claim. 78 is the SEQUENTIAL-build "
            "count belonging to the IEEE-CIS arm, imported into the B1/B2 "
            "comparison in error"
        ),
        provenance=PREREG_PROVENANCE,
        evidence_tag="N/A",
        context="hsbc-2026",
        certainty="very-low",
        certainty_reasons=(
            "Started at whatever level a submitted figure would carry, "
            "then DOWNGRADED to very-low: the consumer repository's own "
            "amendment log (A25 finding 1) states this number is wrong "
            "and names the exact mechanism -- a number imported from one "
            "context (IEEE-CIS sequential build) into another (B1/B2 "
            "comparison) -- 'the same defect class as A15'"
        ),
        updated=UPDATED,
        updated_reason=UPDATED_REASON,
    )
    insert_assertion(conn, wrong)

    correct = AssertionRecord(
        id="hsbc-b1-variable-count",
        value=(
            "B1's variable count is 91 (the full pair build at k=13), not "
            "78. The B2/B1 scale ratio is 9.2x, not 10.7x"
        ),
        provenance=PREREG_PROVENANCE,
        evidence_tag="PROJ",
        context="hsbc-2026",
        citation_context=(
            "\"B1's variable count read 78 in three places and 91 in two "
            "-- B1 ran the FULL pair build at k=13, which is 91; 78 is "
            "the SEQUENTIAL count and belongs to the IEEE-CIS arm, and "
            "the B2/B1 ratio is 9.2x not 10.7x.\""
        ),
        certainty="high",
        certainty_reasons=(
            "Started HIGH -- PROJ evidence tag, a value the consumer "
            "repository's own internal four-way review (A25) verified "
            "against the artifacts before correcting, then re-confirmed "
            "in a second, independent document-contradiction sweep (A30) "
            "five days later. NOT downgraded: two independent internal "
            "review passes reached the same corrected figure"
        ),
        fidelity="exact",
        reading_level=11,
        contradicts=["hsbc-b1-variable-count-wrong-78"],
        updated=UPDATED,
        updated_reason=UPDATED_REASON,
    )
    insert_assertion(conn, correct)

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print("Ingested hsbc-b1-variable-count (91, correct) and hsbc-b1-variable-count-wrong-78 (78, the documented defect). Export regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
