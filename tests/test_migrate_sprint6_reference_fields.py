"""Tests for scripts/migrate_sprint6_reference_fields.py (Sprint 6 Task E).

Builds a PRE-migration store under tmp (today's schema with the A6/A4
additions taken back out), then runs the real script. Added after the
fresh-eyes review (2026-10-03) found the script covered only by one chained
return code. No network.
"""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, create_store  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

SCRIPT = ROOT / "scripts" / "migrate_sprint6_reference_fields.py"
OLD_ASSERTION_FIELDS = """CREATE TABLE assertion_fields (
    record_id TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    units TEXT, rounding TEXT, citation_context TEXT)"""


def _old_store(path: Path) -> None:
    conn = create_store(path)
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in ("paper_found_via", "paper_reads", "paper_probes", "source_links", "assertion_fields"):
        conn.execute(f"DROP TABLE {table}")
    conn.execute(OLD_ASSERTION_FIELDS)
    conn.execute("ALTER TABLE paper_fields DROP COLUMN metadata_provider")
    conn.execute("ALTER TABLE paper_fields DROP COLUMN coi")
    conn.execute("PRAGMA foreign_keys = ON")
    for rid, prov in (("a-read", "p1, p.2"), ("learning-x", "synthesis of the assertions that support it"),
                      ("cyc-context-count", "lenat, p.3")):
        conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
                     "VALUES (?, 'assertion', 'v', ?, 'N/A', '2026-09-01', 'seeded')", (rid, prov))
        conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, 'method')", (rid,))
    conn.execute("INSERT INTO assertion_fields (record_id, units) VALUES ('a-read', 'AUPRC')")
    conn.commit()
    conn.close()


@pytest.fixture
def mig(tmp_path, monkeypatch):
    db = tmp_path / "evidence.db"
    _old_store(db)
    spec = importlib.util.spec_from_file_location("mig6", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "DB_PATH", db)
    monkeypatch.setattr(mod, "EXPORT_DIR", tmp_path / "export")
    monkeypatch.setattr(mod, "backup_before_write",
                        lambda path, reason: backup_before_write(path, reason, tmp_path / "backups"))
    # The fixture's classification names only the one cyc id it seeds.
    monkeypatch.setattr(mod, "VENDOR_SELF_CLAIMS", {"cyc-context-count": "fixture"})
    return mod, db


def _schema(db: Path) -> dict[str, list[tuple]]:
    conn = sqlite3.connect(db)
    try:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        return {t: [tuple(r[1:]) for r in conn.execute(f"PRAGMA table_info({t})")] for t in tables}
    finally:
        conn.close()


def test_dry_run_writes_nothing(mig):
    mod, db = mig
    before = db.read_bytes()
    assert mod.main([]) == 0
    assert db.read_bytes() == before


def test_apply_matches_a_fresh_store_and_back_fills(mig, tmp_path):
    mod, db = mig
    assert mod.main(["--apply"]) == 0
    fresh = tmp_path / "fresh.db"
    create_store(fresh).close()
    assert _schema(db) == _schema(fresh)
    conn = connect(db)
    try:
        rows = {r["record_id"]: (r["derivation"], r["claim_type"], r["units"]) for r in
                conn.execute("SELECT record_id, derivation, claim_type, units FROM assertion_fields")}
        reason = conn.execute("SELECT updated_reason FROM records WHERE id = 'a-read'").fetchone()[0]
    finally:
        conn.close()
    assert rows == {"a-read": ("project", "positive", "AUPRC"),
                    "learning-x": ("synthesized", "positive", None),
                    "cyc-context-count": ("project", "vendor-self-claim", None)}
    assert reason.startswith("seeded | ") and "derivation project" in reason


def test_second_apply_is_a_no_op(mig):
    mod, db = mig
    assert mod.main(["--apply"]) == 0
    before = db.read_bytes()
    assert mod.main(["--apply"]) == 0
    assert db.read_bytes() == before


def test_a_failure_midway_is_rolled_back_on_the_open_connection_regression(mig, monkeypatch):
    """The last CREATE TABLE raises after the assertion_fields rebuild and
    the column additions have run. apply() must roll back itself: the check
    reads the SAME connection before it is closed, because closing also
    discards an open transaction and would hide a missing rollback. Proven
    to fail by injection: with apply()'s rollback replaced by `pass`, this
    connection still saw `derivation` and the test went red (the first
    version of this test went through main() and stayed green)."""
    mod, db = mig
    real = mod.schema_statement

    def broken(table):
        if table == "source_links":
            raise RuntimeError("injected")
        return real(table)

    monkeypatch.setattr(mod, "schema_statement", broken)
    conn = connect(db)
    conn.isolation_level = None
    try:
        with pytest.raises(RuntimeError, match="injected"):
            mod.apply(conn, "2026-10-03")
        assert not conn.in_transaction
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(assertion_fields)")]
        assert "derivation" not in cols
    finally:
        conn.close()
