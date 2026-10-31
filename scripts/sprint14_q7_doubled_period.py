#!/usr/bin/env python3
"""Sprint 14 retrospective Q7: one period, not two, before "NOT upgraded".
INTAKE_WORKFLOW.md section 59.

`store.grading.low_grade` joined a LOW's why and the template's own
period, so a why that ended in a period gave ".. NOT upgraded" (900 stored
reasons as of 2026-10-31). `low_grade` now drops the why's own period;
this script makes the stored reasons match. It replaces the exact string
DOUBLED with SINGLE in `certainty_reasons` and nothing else. Each changed
record gets a note carrying FORMAT_ONLY_MARK, so the change does not take
a full read's ownership of the record away (`store.ingest.last_change`).

DRY RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent:
a second apply finds nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import FORMAT_ONLY_MARK, append_updated_reason  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-31"
DOUBLED = ".. NOT upgraded"
SINGLE = ". NOT upgraded"
NOTE = (f"{TODAY} (Sprint 14 retrospective Q7): {FORMAT_ONLY_MARK} a doubled period before \"NOT upgraded\" "
        "made single; INTAKE_WORKFLOW.md section 59")


def doubled(conn) -> list[tuple[str, str]]:
    """(id, certainty_reasons) of every record whose reason holds DOUBLED."""
    return conn.execute("SELECT id, certainty_reasons FROM records WHERE instr(certainty_reasons, ?) > 0 "
                        "ORDER BY id", (DOUBLED,)).fetchall()


def apply_changes(conn) -> list[str]:
    log = []
    for rid, reasons in doubled(conn):
        conn.execute("UPDATE records SET certainty_reasons = ? WHERE id = ?", (reasons.replace(DOUBLED, SINGLE), rid))
        append_updated_reason(conn, rid, NOTE, TODAY)
        log.append(f"fixed {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    if "--apply" not in args:
        try:
            rows = doubled(conn)
        finally:
            conn.close()
        for rid, _ in rows:
            print(f"would fix {rid}")
        print(f"{len(rows)} records. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    conn.close()
    backup_before_write(DB_PATH, "Q7 doubled period before NOT upgraded")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print(f"{len(log)} records fixed")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
