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

Idempotent and safe to run as two separate passes -- `python scripts/
ingest_seed_set.py` today, `python scripts/ingest_seed_set.py --promote`
later -- an already-present row that is flagged for promotion is
promoted in place rather than skipped (fixed 2026-09-16, Claude PR #1
review: promotion previously only happened on the SAME run that inserted
the row, so a later `--promote` run against an already-seeded store
promoted nothing).

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import PaperRecord, insert_paper  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
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

    inserted, skipped, promoted = 0, 0, 0
    for position, entry in enumerate(entries):
        record_id = entry["id"]
        # Per-entry SAVEPOINT (F6 finding 3, PR #1 review): the whole loop
        # previously shared one commit at the end, so a mid-loop FK
        # violation aborted the run with an unhandled traceback naming no
        # offending record -- a bad entry at position 30 of 46 gave no clue
        # which entry, without editing the script to add a print. A
        # savepoint per entry both isolates a bad entry's partial writes
        # (RELEASE only on success) and lets the error message name the
        # entry that failed, without needing a full COMMIT per row (SQLite
        # savepoints are cheap; a real commit per row here would be 46x the
        # fsync cost for no correctness benefit at this scale).
        #
        # The savepoint name uses the loop POSITION, not inserted/skipped
        # counters -- an earlier version used `inserted + skipped`, which
        # is read again at RELEASE time after `inserted` may have just
        # been incremented inside the try block, so SAVEPOINT and RELEASE
        # named two DIFFERENT savepoints and RELEASE failed with "no such
        # savepoint". A stable per-iteration value avoids that class of
        # bug entirely.
        savepoint = f"entry_{position}"
        conn.execute(f"SAVEPOINT {savepoint}")
        try:
            existing = conn.execute(
                "SELECT p.tier FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?",
                (record_id,),
            ).fetchone()
            if existing:
                skipped += 1
                # Promotion must still run on an already-present row (fixed
                # 2026-09-16, Claude PR #1 review finding 2): the original
                # code skipped promotion entirely whenever a row already
                # existed, so `ingest_seed_set.py` then `ingest_seed_set.py
                # --promote` -- the exact two-run sequence this script's own
                # docstring describes -- could never promote anything, since
                # every row was already present by the second run.
                if promote and entry.get("promote") and existing["tier"] == "seen":
                    conn.execute(
                        "UPDATE paper_fields SET tier = 'screened' WHERE record_id = ?",
                        (record_id,),
                    )
                    promoted += 1
            else:
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
        except Exception as e:
            conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            raise RuntimeError(f"failed on seed-set entry {record_id!r} (position {position}): {e}") from e
        else:
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print(
        f"Inserted {inserted} paper records ({skipped} already present, "
        f"{promoted} of those promoted to screened)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
