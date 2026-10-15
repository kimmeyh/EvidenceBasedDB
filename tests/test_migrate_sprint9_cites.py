"""Tests for the `cites` link type (ADR-0005 A10, Sprint 9 Task H, F55):
scripts/migrate_sprint9_cites_link_type.py run against a PRE-migration
store (today's synthetic store with the old CHECK put back), the door's
LINK_TYPES kept equal to the schema's, and store.links read from both ends.
No network."""
from __future__ import annotations

import importlib.util
import re
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import SCHEMA_PATH, connect  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import LINK_TYPES, add_source_link  # noqa: E402
from store.links import links_of  # noqa: E402
from tests.conftest import build_synthetic_store  # noqa: E402

SCRIPT = ROOT / "scripts" / "migrate_sprint9_cites_link_type.py"
OLD_SOURCE_LINKS = """CREATE TABLE source_links (
    from_id   TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    to_id     TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    link_type TEXT NOT NULL CHECK (link_type IN ('code-of', 'dataset-of', 'version-of', 'superseded-by', 'responds-to')),
    evidence  TEXT NOT NULL CHECK (trim(evidence) <> ''),
    PRIMARY KEY (from_id, to_id, link_type),
    CHECK (from_id != to_id)
)"""
CITE = ("alpha-2024-first-paper", "beta-2025-second-paper", "cites", "fixture reference list")


def _old_store(db: Path) -> None:
    build_synthetic_store(db)
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = OFF")
    rows = conn.execute("SELECT from_id, to_id, link_type, evidence FROM source_links").fetchall()
    conn.execute("DROP TABLE source_links")
    conn.execute(OLD_SOURCE_LINKS)
    conn.executemany("INSERT INTO source_links VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()


@pytest.fixture
def mig(tmp_path, monkeypatch):
    db = tmp_path / "evidence.db"
    _old_store(db)
    spec = importlib.util.spec_from_file_location("mig9", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "DB_PATH", db)
    monkeypatch.setattr(mod, "backup_before_write",
                        lambda path, reason: backup_before_write(path, reason, tmp_path / "backups"))
    return mod, db


def test_the_old_store_refuses_cites(mig):
    """The fixture really is pre-migration: without this, every test below
    could pass against a store that never needed migrating."""
    _, db = mig
    conn = sqlite3.connect(db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO source_links VALUES (?, ?, ?, ?)", CITE)
    conn.close()


def test_migration_keeps_every_row_and_allows_cites(mig):
    """Proven to fail by injection, 2026-10-15: with the rebuild's INSERT ...
    SELECT removed from apply(), the row-count guard raised and nothing was
    committed; with the schema.sql CHECK left without 'cites', the cites
    insert below raised IntegrityError."""
    mod, db = mig
    before = sqlite3.connect(db).execute("SELECT * FROM source_links ORDER BY 1, 2, 3").fetchall()
    assert before
    assert mod.main(["--apply"]) == 0
    conn = connect(db)
    try:
        assert [tuple(r) for r in conn.execute("SELECT * FROM source_links ORDER BY 1, 2, 3")] == before
        add_source_link(conn, *CITE)
        conn.commit()
        assert conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?",
                            (mod.INDEX,)).fetchone()
        assert not conn.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        conn.close()


def test_a_second_run_changes_nothing(mig, capsys):
    mod, db = mig
    assert mod.main(["--apply"]) == 0
    capsys.readouterr()
    assert mod.main(["--apply"]) == 0
    assert "already migrated" in capsys.readouterr().out


def test_a_dry_run_writes_nothing(mig):
    mod, db = mig
    assert mod.main([]) == 0
    sql = sqlite3.connect(db).execute("SELECT sql FROM sqlite_master WHERE name = 'source_links'").fetchone()[0]
    assert "'cites'" not in sql


def test_the_door_and_the_schema_allow_the_same_link_types():
    """Proven to fail by injection, 2026-10-15: with 'cites' dropped from
    LINK_TYPES only, this test named the difference."""
    m = re.search(r"link_type TEXT NOT NULL CHECK \(link_type IN \((.*?)\)\)",
                  SCHEMA_PATH.read_text(encoding="utf-8"), re.S)
    in_schema = set(re.findall(r"'([a-z-]+)'", m.group(1)))
    assert in_schema == set(LINK_TYPES), in_schema ^ set(LINK_TYPES)


def test_a_link_reads_from_both_ends(synthetic_store):
    conn = connect(synthetic_store)
    try:
        add_source_link(conn, *CITE)
        conn.commit()
        citing = links_of(conn, CITE[0], "cites")
        cited = links_of(conn, CITE[1], "cites")
    finally:
        conn.close()
    assert citing == {"out": [{"type": "cites", "other": CITE[1], "evidence": CITE[3]}], "in": []}
    assert cited == {"out": [], "in": [{"type": "cites", "other": CITE[0], "evidence": CITE[3]}]}
