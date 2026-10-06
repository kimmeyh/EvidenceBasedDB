#!/usr/bin/env python3
"""Migration: drop `paper_fields.citation`, add the read-tier CHECK
(Sprint 4 Task B, F25 B4, decisions Q1/Q2 of 2026-09-19).

Why: `paper_fields.citation` was a byte-identical copy of
`records.provenance` on 46 of 46 papers -- this project's founding defect
reproduced inside every row -- and since Sprint 3 nothing read it. The
read-tier rule (ADR-0005 section 2: `checked_against_source` required at
tier 'read') gains a table-level CHECK alongside the application-layer
check, per the Copilot PR #20 correction.

SQLite cannot DROP a column that participates in the way this one does
nor ADD a table CHECK in place, so this is the documented rebuild: create
the new table, copy, drop, rename, recreate the index, run
foreign_key_check. Tables that reference paper_fields(record_id)
(paper_applicability, paper_yields) keep working because the FK names the
table, and the rename restores that name.

DRY-RUN BY DEFAULT (QUALITY_STANDARDS.md): prints the plan and exits.
`--apply` performs the rebuild in one transaction, then regenerates the
export and reports whether it changed byte-for-byte (it should not: the
export never read the dropped column).

Usage:
    python scripts/migrate_paper_fields_drop_citation.py          # plan only
    python scripts/migrate_paper_fields_drop_citation.py --apply  # rebuild
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

NEW_TABLE_SQL = """
CREATE TABLE paper_fields_new (
    record_id               TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    tier                    TEXT NOT NULL CHECK (tier IN ('seen', 'screened', 'read')),
    access                  TEXT NOT NULL,
    disposition             TEXT NOT NULL,
    evidence                TEXT,
    mined_by                TEXT,
    checked_against_source  TEXT,
    CHECK (tier <> 'read' OR checked_against_source IS NOT NULL)
)
"""


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]


def _export_hash() -> str:
    h = hashlib.sha256()
    for name in sorted(p.name for p in EXPORT_DIR.glob("*.json")):
        h.update(name.encode()); h.update((EXPORT_DIR / name).read_bytes())
    return h.hexdigest()


def plan(conn: sqlite3.Connection) -> dict:
    cols = _columns(conn, "paper_fields")
    rows = conn.execute("SELECT COUNT(*) FROM paper_fields").fetchone()[0]
    diverged = conn.execute(
        "SELECT COUNT(*) FROM paper_fields p JOIN records r ON r.id = p.record_id WHERE p.citation <> r.provenance"
    ).fetchone()[0] if "citation" in cols else 0
    read_without_cas = conn.execute(
        "SELECT COUNT(*) FROM paper_fields WHERE tier = 'read' AND checked_against_source IS NULL"
    ).fetchone()[0]
    return {"columns_before": cols, "rows": rows, "citation_diverges_from_provenance": diverged,
            "read_rows_that_would_violate_check": read_without_cas, "already_migrated": "citation" not in cols}


def apply(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("BEGIN")
        conn.execute(NEW_TABLE_SQL)
        conn.execute(
            "INSERT INTO paper_fields_new (record_id, tier, access, disposition, evidence, mined_by, checked_against_source) "
            "SELECT record_id, tier, access, disposition, evidence, mined_by, checked_against_source FROM paper_fields"
        )
        conn.execute("DROP TABLE paper_fields")
        conn.execute("ALTER TABLE paper_fields_new RENAME TO paper_fields")
        conn.execute("CREATE INDEX idx_paper_fields_tier ON paper_fields(tier)")
        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise RuntimeError(f"foreign_key_check reported {len(problems)} problem(s); rolled back")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        p = plan(conn)
        print(f"paper_fields columns now: {p['columns_before']}")
        print(f"rows: {p['rows']}; citation <> provenance on {p['citation_diverges_from_provenance']} row(s); "
              f"read-tier rows that would violate the CHECK: {p['read_rows_that_would_violate_check']}")
        if p["already_migrated"]:
            print("already migrated: no `citation` column present. Nothing to do.")
            return 0
        if p["citation_diverges_from_provenance"]:
            print("error: some paper_fields.citation values differ from records.provenance; "
                  "dropping the column would lose information. Reconcile first.", file=sys.stderr)
            return 1
        if p["read_rows_that_would_violate_check"]:
            print("error: read-tier rows with NULL checked_against_source would violate the new CHECK.", file=sys.stderr)
            return 1
        if not do_apply:
            print("\nPLANNED (dry run): rebuild paper_fields without `citation`, with the read-tier CHECK, "
                  "then regenerate export/. Re-run with --apply to perform it.")
            return 0
        before = _export_hash()
        apply(conn)
        if "metadata_provider" not in _columns(conn, "paper_fields"):
            # Migrations run in order. The export code is current, so a store
            # this old cannot be exported until the later migrations run
            # (Sprint 6 Task E, 2026-10-03).
            print("applied. export NOT regenerated: run scripts/migrate_sprint6_reference_fields.py --apply next")
            return 0
        regenerate(conn, EXPORT_DIR)
        after = _export_hash()
        print(f"applied. paper_fields columns now: {_columns(conn, 'paper_fields')}")
        print("export/ byte-identical before and after: " + ("YES" if before == after else "NO -- inspect git diff export/"))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
