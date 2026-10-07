#!/usr/bin/env python3
"""Sprint 5 Manual Validation fix: the six pilot papers' dispositions.

Loaded at `seen` with the bulk disposition "...; not yet screened"
(docs/INTAKE_WORKFLOW.md sections 6 and 11), then promoted to `read` by the
F28 pilot. The clause went stale on promotion: a disposition that
restates tier state is the drift the tier column exists to prevent, and
the validator's tier-word check does not catch this phrasing. Found by the
team lead's `view.py paper kakavand-...` run, 2026-09-25.

This drops the stale clause from the six only. Whether to drop it from
every bulk record, and to catch the phrasing at the door, is the team
lead's decision (Manual Validation Q7).

DRY RUN BY DEFAULT; `--apply` takes a verified backup (F30), commits,
regenerates export/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-25"
STALE = "; not yet screened"
PILOT = ["2604.18837", "2309.11647", "2509.06873", "2201.08528", "2606.29720", "2401.06091"]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "pilot disposition fix --apply")
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        for arxiv in PILOT:
            row = conn.execute("SELECT record_id, tier, disposition FROM paper_fields WHERE access = ?",
                               (f"arXiv:{arxiv}",)).fetchone()
            if row["tier"] != "read" or not row["disposition"].endswith(STALE):
                raise SystemExit(f"{row['record_id']}: not in the expected state ({row['tier']!r}, {row['disposition']!r})")
            new = row["disposition"][: -len(STALE)]
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (new, row["record_id"]))
            append_updated_reason(conn, row["record_id"], f"{TODAY} (Sprint 5 Manual Validation): dropped the stale "
                                  f"'{STALE[2:]}' from the disposition after the F28 pilot promoted the paper to read",
                                  TODAY)
            print(f"FIX {row['record_id']}: {new}")
        if not apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; rolled back). Re-run with --apply.")
            return 0
        conn.execute("COMMIT")
        print("COMMITTED")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
