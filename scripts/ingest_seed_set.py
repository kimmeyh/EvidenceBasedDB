#!/usr/bin/env python3
"""Sprint 1 Task F: load the 46-paper seed set at `seen`.

Reads paper metadata from scripts/seed_set_metadata.json (generated
separately by extracting real bibliographic data from each PDF's own
content -- ADR-0004's standing rule is that every assertion originates in
a source with provenance, and a citation guessed from a filename would be
exactly the defect class this system exists against).

Loads every entry at `seen` tier. Promotion to `screened` for a
variety-chosen subset of ~20 is a separate, later step (this script's
--promote flag), not automatic, so the variety selection is a deliberate
choice rather than "however this script happened to order the list."

Usage:
    python scripts/ingest_seed_set.py              # load all at seen
    python scripts/ingest_seed_set.py --promote     # also promote the
                                                     # variety-selected subset
                                                     # named in the metadata
                                                     # file's "promote" field
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import PaperRecord, insert_paper  # noqa: E402

DB_PATH = ROOT / "store" / "evidence.db"
EXPORT_DIR = ROOT / "export"
METADATA_PATH = ROOT / "scripts" / "seed_set_metadata.json"

UPDATED = "2026-09-16"
UPDATED_REASON = "Sprint 1 Task F: 46-paper seed set loaded at seen tier"


def main() -> int:
    promote = "--promote" in sys.argv

    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    if not METADATA_PATH.exists():
        print(f"error: {METADATA_PATH} does not exist. Generate it first.", file=sys.stderr)
        return 1

    entries = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    conn = connect(DB_PATH)

    inserted, skipped = 0, 0
    for entry in entries:
        record_id = entry["id"]
        existing = conn.execute("SELECT id FROM records WHERE id = ?", (record_id,)).fetchone()
        if existing:
            skipped += 1
            continue

        tier = "screened" if (promote and entry.get("promote")) else "seen"
        paper = PaperRecord(
            id=record_id,
            tier=tier,
            citation=entry["citation"],
            access=entry["access"],
            disposition=entry["disposition"],
            context=entry["context"],
            value=entry["citation"],
            evidence_tag="N/A",
            updated=UPDATED,
            updated_reason=UPDATED_REASON,
        )
        insert_paper(conn, paper)
        inserted += 1

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print(f"Inserted {inserted} paper records ({skipped} already present, skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
