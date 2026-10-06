#!/usr/bin/env python3
"""Migration: the ADR-0004 A6 and ADR-0005 A4 fields (Sprint 6 Task E,
F34/F36/F37/F47, decisions Q1-Q7 of 2026-10-03).

What it does, in one transaction:
- rebuilds `assertion_fields` with `derivation`, `claim_type` and
  `search_scope`, and gives EVERY assertion a row (A6 makes the first two
  required); `derivation` is back-filled by A6 (a)'s rule and `claim_type`
  by the hand classification below, each with its reason appended to the
  record's `updated_reason`;
- adds `paper_fields.metadata_provider` and `paper_fields.coi`;
- creates `paper_found_via`, `paper_reads`, `paper_probes`, `source_links`
  (empty here; Sprint 6 Task F back-fills them).

Every CREATE TABLE is read from store/schema.sql itself, so the migrated
store cannot drift from a fresh one.

DRY-RUN BY DEFAULT (QUALITY_STANDARDS.md): prints the plan and exits.
`--apply` takes a verified backup first (F30), then migrates, runs
`PRAGMA foreign_key_check`, commits and regenerates the export.

Usage:
    python scripts/migrate_sprint6_reference_fields.py          # plan only
    python scripts/migrate_sprint6_reference_fields.py --apply  # migrate
"""
from __future__ import annotations

import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import SCHEMA_PATH, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
NEW_TABLES = ("paper_found_via", "paper_reads", "paper_probes", "source_links")

# ADR-0004 A6 (f): the 23 assertions of 2026-10-03, classified one by one.
# Every one not named here is `positive`: it states a result, and it is not
# a vendor describing its own product. Reviewed at Manual Validation.
_CQI = "QCi authors benchmarking QCi's own CVQBoost on QCi's Dirac-3 (emami-2025; qci-2024-profiling is QCi's report)"
_CYC = "Lenat, Cycorp's founder, describing Cycorp's own system (lenat-marcus-2023)"
VENDOR_SELF_CLAIMS = {
    "cvqboost-vs-xgboost-auc-under-balancing": _CQI,
    "cvqboost-vs-xgboost-training-time-dirac3": _CQI,
    "cyc-context-count": _CYC,
    "cyc-general-prover-disabled": _CYC,
    "cyc-hl-module-count": _CYC,
    "cyc-no-numeric-confidence": _CYC,
    "cyc-truth-values-four": _CYC,
    "heuristics-over-general-reasoning": _CYC,
}


def schema_statement(table: str) -> str:
    """The CREATE TABLE statement for `table`, verbatim from schema.sql."""
    m = re.search(rf"^CREATE TABLE {table} \(.*?^\);", SCHEMA_PATH.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        raise LookupError(f"schema.sql has no CREATE TABLE {table}")
    return m.group(0)


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]


def derivation_of(conn: sqlite3.Connection, assertion_id: str, provenance: str) -> tuple[str, str]:
    """A6 (a)'s back-fill rule, in its order: synthesis first, then yields."""
    if provenance.startswith("synthesis of"):
        return "synthesized", "provenance begins 'synthesis of'"
    papers = [r[0] for r in conn.execute(
        "SELECT paper_id FROM paper_yields WHERE assertion_id = ? ORDER BY paper_id", (assertion_id,))]
    if papers:
        return "extracted", f"yielded by {', '.join(papers)}"
    return "project", "no paper yields it and it is not a synthesis; its provenance is this project's own document"


def plan(conn: sqlite3.Connection) -> dict:
    """What is still missing, piece by piece, so a store migrated in part
    (or built by an older create_store and then an older migration)
    finishes the same way as a store migrated in one go."""
    needs_assertion_fields = "derivation" not in _columns(conn, "assertion_fields")
    paper_cols = _columns(conn, "paper_fields")
    missing_columns = [c for c in ("metadata_provider", "coi") if c not in paper_cols]
    missing_tables = [t for t in NEW_TABLES if not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (t,)).fetchone()]
    rows = []
    if needs_assertion_fields:
        for r in conn.execute("SELECT id, provenance FROM records WHERE class = 'assertion' ORDER BY id"):
            derivation, why = derivation_of(conn, r["id"], r["provenance"])
            claim = "vendor-self-claim" if r["id"] in VENDOR_SELF_CLAIMS else "positive"
            rows.append({"id": r["id"], "derivation": derivation, "derivation_why": why, "claim_type": claim,
                         "claim_why": VENDOR_SELF_CLAIMS.get(r["id"], "states a result; not a vendor describing its own product")})
    unknown = sorted(set(VENDOR_SELF_CLAIMS) - {r["id"] for r in rows}) if rows else []
    return {"already_migrated": not (needs_assertion_fields or missing_columns or missing_tables),
            "needs_assertion_fields": needs_assertion_fields, "missing_columns": missing_columns,
            "missing_tables": missing_tables, "assertions": rows, "classified_ids_not_in_store": unknown}


def apply(conn: sqlite3.Connection, today: str) -> None:
    p = plan(conn)
    if p["already_migrated"]:
        raise SystemExit("already migrated: nothing is missing")
    if p["classified_ids_not_in_store"]:
        raise SystemExit(f"classification names ids not in the store: {p['classified_ids_not_in_store']}")
    conn.execute("PRAGMA foreign_keys = OFF")  # the table rebuild below; re-checked before commit
    conn.execute("BEGIN")
    try:
        if p["needs_assertion_fields"]:
            _rebuild_assertion_fields(conn, p["assertions"], today)
        for column in p["missing_columns"]:
            conn.execute(f"ALTER TABLE paper_fields ADD COLUMN {column} TEXT")
        for table in p["missing_tables"]:
            conn.execute(schema_statement(table))
        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise RuntimeError(f"foreign_key_check failed: {[tuple(r) for r in problems]}")
        conn.commit()
    except BaseException:
        conn.rollback()  # nothing written; never rely on close() to discard it
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def _rebuild_assertion_fields(conn: sqlite3.Connection, assertions: list[dict], today: str) -> None:
    conn.execute(schema_statement("assertion_fields").replace("CREATE TABLE assertion_fields",
                                                              "CREATE TABLE assertion_fields_new", 1))
    for row in assertions:
        old = conn.execute("SELECT units, rounding, citation_context FROM assertion_fields WHERE record_id = ?",
                           (row["id"],)).fetchone()
        conn.execute(
            "INSERT INTO assertion_fields_new (record_id, units, rounding, citation_context, derivation, claim_type) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (row["id"], *(old if old else (None, None, None)), row["derivation"], row["claim_type"]))
        append_updated_reason(conn, row["id"], (
            f"{today}: Sprint 6 Task E migration (ADR-0004 A6): derivation {row['derivation']} "
            f"({row['derivation_why']}); claim_type {row['claim_type']} ({row['claim_why']})"), today)
    conn.execute("DROP TABLE assertion_fields")
    conn.execute("ALTER TABLE assertion_fields_new RENAME TO assertion_fields")


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
            print("already migrated: nothing is missing; nothing to do")
            return 0
        counts: dict[str, int] = {}
        for row in p["assertions"]:
            counts[row["derivation"]] = counts.get(row["derivation"], 0) + 1
            print(f"{row['id']}: derivation {row['derivation']} ({row['derivation_why']}); "
                  f"claim_type {row['claim_type']}")
        print(f"\n{len(p['assertions'])} assertions: {counts}; "
              f"vendor-self-claim {sum(r['claim_type'] == 'vendor-self-claim' for r in p['assertions'])}")
        print(f"assertion_fields rebuilt: {p['needs_assertion_fields']}; new paper_fields columns: "
              f"{p['missing_columns'] or 'none'}; new tables: {p['missing_tables'] or 'none'}")
        if "--apply" not in args:
            print("\nDRY RUN: nothing written. Re-run with --apply.")
            return 0
        backup_before_write(DB_PATH, "sprint6 reference fields migration")
        apply(conn, date.today().isoformat())
        conn.isolation_level = ""
        regenerate(conn, EXPORT_DIR)
        print("APPLIED; export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
