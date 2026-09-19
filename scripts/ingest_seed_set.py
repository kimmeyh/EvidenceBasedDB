#!/usr/bin/env python3
"""Sprint 1 Task F: load the 46-paper seed set at `seen`.

Reads paper metadata from scripts/seed_set_metadata.json, the hand-authored
seed file. Since Sprint 4 Tasks B/C (F25 C1, 2026-09-19) that file carries
only what the door accepts: for an entry whose `access` is an arXiv id or
DOI, `citation_origin: "api"` and NO citation -- insert_paper() derives the
citation and the title from the source of record; for an entry with no
resolvable id, `citation_origin: "hand"`, a `title`, a `citation` ending
in "(hand-transcribed from <page>)", `transcribed_from`, and an `access`
that is the real local path (optionally " | <url>"). tests/
test_seed_set_metadata.py guards that shape. The original generator
(scripts/generate_seed_set_metadata.py, hand-authored Python dicts
transcribed from each PDF in Sprint 1) was retired in Task C: it was the
"old door" through which hand-typed citations would have re-entered.
To add a paper, append an entry here and run this script; the door checks
it. ADR-0004's standing rule is that every assertion originates in a
source with provenance, and a citation guessed from a filename would be
exactly the defect class this system exists against.

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
from store.citations import PacedFetcher, parse_access  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import PaperRecord, insert_paper, set_tier  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

# Network for api-origin entries; tests inject a fake. Paced for arXiv.
FETCHER = PacedFetcher()
METADATA_PATH = ROOT / "scripts" / "seed_set_metadata.json"

UPDATED = "2026-09-16"
UPDATED_REASON = "Sprint 1 Task F: 46-paper seed set loaded at seen tier"


def main() -> int:
    promote = "--promote" in sys.argv

    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    if not METADATA_PATH.exists():
        print(f"error: {METADATA_PATH} does not exist.", file=sys.stderr)
        return 1

    entries = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    conn = connect(DB_PATH)

    # ALL-OR-NOTHING (PR #20 review, 2026-09-19, superseding the Sprint 3
    # Task B savepoint design). The savepoint version claimed to isolate a
    # bad entry "without needing a full COMMIT per row" -- but Python's
    # sqlite3 in its default legacy transaction mode opens an implicit
    # transaction only before INSERT/UPDATE/DELETE, never before SAVEPOINT,
    # so each entry's savepoint opened its OWN transaction and RELEASE of
    # that outermost savepoint was a commit. Proven by the reviewer with a
    # second connection seeing the row before any commit() call. The real
    # consequence: on a bad entry at position N, entries 0..N-1 were already
    # durable and regenerate() never ran, so store and export/ silently
    # diverged -- the exact "stale export" defect class Phase 5 of the
    # workflow names.
    #
    # The contract is now: one transaction, opened implicitly by the first
    # write; any failure rolls back EVERY entry, names the failing entry and
    # position, and leaves both store and export/ exactly as they were. The
    # durable write (commit, then regenerate) happens only after the last
    # decision that could fail -- QUALITY_STANDARDS.md "decide, then write".
    inserted, skipped, promoted = 0, 0, 0
    position = -1
    record_id = "<no id>"
    try:
        for position, entry in enumerate(entries):
            record_id = entry.get("id", "<no id>")
            if "id" not in entry:
                raise KeyError("entry has no 'id' field")
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
                    set_tier(conn, record_id, "screened")
                    promoted += 1
            else:
                tier = "screened" if (promote and entry.get("promote")) else "seen"
                # Sprint 4 Task B (F25 C1): the metadata file no longer supplies
                # citations. An entry whose access carries an arXiv id or DOI is
                # api-origin and its citation and title come from the source of
                # record at insert time; anything else must declare itself
                # hand-transcribed with the page it was read from and a real
                # local path. insert_paper() refuses everything in between.
                origin = "api" if parse_access(entry["access"]) else "hand"
                paper = PaperRecord(
                    id=record_id,
                    tier=tier,
                    access=entry["access"],
                    disposition=entry["disposition"],
                    context=entry["context"],
                    value=entry.get("title", ""),
                    citation=None if origin == "api" else entry.get("citation"),
                    citation_origin=origin,
                    hand_transcribed_from=entry.get("transcribed_from"),
                    evidence_tag="N/A",
                    updated=UPDATED,
                    updated_reason=UPDATED_REASON,
                )
                insert_paper(conn, paper, fetcher=FETCHER)
                inserted += 1
    except Exception as e:
        conn.rollback()
        conn.close()
        raise RuntimeError(
            f"failed on seed-set entry {record_id!r} (position {position}): {e}. "
            "Nothing was written: every entry in this run was rolled back and "
            "export/ was not regenerated."
        ) from e

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
