#!/usr/bin/env python3
"""Migration: the `cites` source-link type (ADR-0005 A10, Sprint 9 Task H,
F55; team lead, plan Q5 = 1).

SQLite cannot change a CHECK in place, so `source_links` is rebuilt from
store/schema.sql's own statement (the migrated store cannot drift from a
fresh one), every row copied, and the `to_id` index added. One transaction;
`PRAGMA foreign_key_check` before the commit.

DRY-RUN BY DEFAULT: prints the plan. `--apply` takes a verified backup
first (F30). Idempotent: a store that already allows `cites` and has the
index is left alone.

Usage:
    python scripts/migrate_sprint9_cites_link_type.py          # plan only
    python scripts/migrate_sprint9_cites_link_type.py --apply  # migrate
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import SCHEMA_PATH, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
INDEX = "idx_source_links_to"


def schema_statement(pattern: str) -> str:
    """A statement from schema.sql, verbatim, by a regex anchored at line start."""
    m = re.search(pattern, SCHEMA_PATH.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        raise LookupError(f"schema.sql has no statement matching {pattern!r}")
    return m.group(0)


def plan(conn: sqlite3.Connection) -> dict:
    sql = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'source_links'").fetchone()
    if not sql:
        raise SystemExit("the store has no source_links table: run the Sprint 6 migration first")
    needs_table = "'cites'" not in sql[0]
    needs_index = not conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?",
                                   (INDEX,)).fetchone()
    rows = conn.execute("SELECT count(*) FROM source_links").fetchone()[0]
    return {"needs_table": needs_table, "needs_index": needs_index, "rows": rows,
            "already_migrated": not (needs_table or needs_index)}


def apply(conn: sqlite3.Connection) -> None:
    p = plan(conn)
    if p["already_migrated"]:
        raise SystemExit("already migrated: nothing is missing")
    conn.execute("PRAGMA foreign_keys = OFF")  # the table rebuild below; re-checked before commit
    conn.execute("BEGIN")
    try:
        if p["needs_table"]:
            create = schema_statement(r"^CREATE TABLE source_links \(.*?^\);")
            conn.execute(create.replace("CREATE TABLE source_links", "CREATE TABLE source_links_new", 1))
            conn.execute("INSERT INTO source_links_new (from_id, to_id, link_type, evidence) "
                         "SELECT from_id, to_id, link_type, evidence FROM source_links")
            conn.execute("DROP TABLE source_links")
            conn.execute("ALTER TABLE source_links_new RENAME TO source_links")
        conn.execute(schema_statement(rf"^CREATE INDEX {INDEX} ON source_links\(to_id\);"))
        copied = conn.execute("SELECT count(*) FROM source_links").fetchone()[0]
        if copied != p["rows"]:
            raise RuntimeError(f"source_links had {p['rows']} rows and now has {copied}")
        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise RuntimeError(f"foreign_key_check failed: {[tuple(r) for r in problems]}")
        conn.commit()
    except BaseException:
        conn.rollback()  # nothing written; never rely on close() to discard it
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not DB_PATH.exists():  # connect() would create an empty store here
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    conn.isolation_level = None  # explicit BEGIN/COMMIT around the table rebuild
    try:
        p = plan(conn)
        if p["already_migrated"]:
            print("already migrated: nothing to do")
            return 0
        print(f"source_links rebuilt with 'cites': {p['needs_table']} ({p['rows']} rows copied); "
              f"index {INDEX} added: {p['needs_index']}")
        if "--apply" not in args:
            print("DRY RUN: nothing written. Re-run with --apply.")
            return 0
        backup_before_write(DB_PATH, "sprint9 cites link type migration")
        apply(conn)
        print("APPLIED")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
