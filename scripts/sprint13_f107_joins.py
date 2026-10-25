#!/usr/bin/env python3
"""Sprint 13 Task A (F107), part 1: the ".;" joins out of paper evidence.
INTAKE_WORKFLOW.md section 48.

When a script appended "; Local copy ..." to evidence text that already
ended in a full stop, the record kept ".;". Sprint 12 Task A corrected the
papers its own apply had touched (`sprint12_f101_corrections.py`, JOIN) and
left 13 more, written by F48 and F97; on 2026-10-25 the store holds 16 in
`paper_fields.evidence`, every one before "Local copy". Each is read in the
dry run before it is written. The full stop is dropped and the separator
kept, as Sprint 12 did.

Two ".;" outside that field are the source's own text and stay: a
`paper_reads` detail that quotes an arXiv title ending "..." and a
`paper_probes` affiliation list after "Quantum Computing Inc.".

Part 2 of the task (the LOW reasons) is in `sprint12_reading.py`, whose
live test compares the store with that script.

DRY RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-25"
NOTE = f"{TODAY} (Sprint 13 Task A, F107): the \".;\" join before the local-copy note corrected (INTAKE_WORKFLOW.md section 48)"
# A sentence's full stop with an appended note after it; "..." and an
# abbreviation such as "Inc." are not matched.
JOIN = re.compile(r"(?<=[a-z0-9)\]])\.; (?=Local copy)")


def joined(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(record id, stored evidence, corrected evidence) for every paper with a join."""
    out = []
    for rid, evidence in conn.execute("SELECT record_id, evidence FROM paper_fields WHERE evidence LIKE '%.;%' "
                                      "ORDER BY record_id"):
        fixed = JOIN.sub("; ", evidence)
        if fixed != evidence:
            out.append((rid, evidence, fixed))
    return out


def apply_changes(conn: sqlite3.Connection) -> list[str]:
    log = []
    for rid, _, fixed in joined(conn):
        conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?", (fixed, rid))
        append_updated_reason(conn, rid, NOTE, TODAY)
        log.append(f"joined {rid}")
    return log or ["nothing to correct"]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    if "--apply" not in args:
        try:
            rows = joined(conn)
            for rid, old, _ in rows:
                at = old.index(".; Local copy")
                print(f"{rid}: ...{old[max(0, at - 60):at + 14]}...")
            print(f"{len(rows)} to correct. DRY RUN: nothing written. Re-run with --apply.")
        finally:
            conn.close()
        return 0
    conn.close()
    backup_before_write(DB_PATH, "F107 the .; joins")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
