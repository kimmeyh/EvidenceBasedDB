#!/usr/bin/env python3
"""Sprint 8 Phase 7, team-lead decision 2026-10-13: remove the record
`hsbc-dirac3-allocation-1681-after-sizing-probes`.

Team lead: "The reference to how many qpu seconds are remaining is not
valuable to the DB and should be removed." The record (Sprint 6 Task G)
stated a QPU balance: 3,000 Dirac-3 seconds granted on 2026-09-09, less two
draws, leaving 1,681. A balance changes with every run and every grant (QCi
added seconds on 2026-10-09), so it was already stale; the account itself
answers it, so the store holds no copy (CLAUDE.md: determinate facts are
computed, never stored). Nothing links to it but its own child rows.

Follows scripts/sprint5_remove_weak_identity.py: DRY RUN BY DEFAULT;
`--apply` takes a verified backup (F30), deletes the record's one
`paper_yields` row and then the record (its other child rows cascade), and
checks foreign keys. Sprint 6's script no longer carries the
assertion, so a re-run does not re-add it. The id is never reused.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
RECORD_ID = "hsbc-dirac3-allocation-1681-after-sizing-probes"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    conn = connect(DB_PATH)
    try:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (RECORD_ID,)).fetchone() is None:
            print(f"{RECORD_ID}: not in the store; nothing to do")
            return 0
        linked = conn.execute("SELECT COUNT(*) FROM assertion_relations WHERE from_assertion_id = ? "
                              "OR to_assertion_id = ?", (RECORD_ID, RECORD_ID)).fetchone()[0]
        if linked:
            print(f"refusing: {RECORD_ID} has {linked} assertion relation(s)", file=sys.stderr)
            return 1
        print(f"REMOVE {RECORD_ID}")
        if not apply:
            print("PLANNED (dry run; nothing written). Re-run with --apply.")
            return 0
    finally:
        conn.close()
    backup_before_write(DB_PATH, "remove qpu balance --apply")
    conn = connect(DB_PATH)
    conn.isolation_level = None  # the explicit BEGIN/COMMIT/ROLLBACK below own the transaction
    try:
        conn.execute("BEGIN")
        # paper_yields.assertion_id does not cascade (the schema makes
        # removing a yielded assertion explicit), so its yield goes first.
        conn.execute("DELETE FROM paper_yields WHERE assertion_id = ?", (RECORD_ID,))
        conn.execute("DELETE FROM records WHERE id = ?", (RECORD_ID,))
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            conn.execute("ROLLBACK")
            print(f"NOT APPLIED: foreign_key_check {fk}", file=sys.stderr)
            return 1
        conn.execute("COMMIT")
    finally:
        conn.close()
    print(f"deleted {RECORD_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
