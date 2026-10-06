"""Tests for scripts/migrate_paper_fields_drop_citation.py (Sprint 4 Task B,
F25 B4, decision Q2). Builds a PRE-migration store (old paper_fields shape
with a `citation` column) under tmp, then runs the real script dry and
applied. No network.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import connect, create_store  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "migrate_paper_fields_drop_citation.py"

OLD_PAPER_FIELDS = """
CREATE TABLE paper_fields (
    record_id TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    tier TEXT NOT NULL CHECK (tier IN ('seen', 'screened', 'read')),
    citation TEXT NOT NULL,
    access TEXT NOT NULL,
    disposition TEXT NOT NULL,
    evidence TEXT,
    mined_by TEXT,
    checked_against_source TEXT
)"""


@pytest.fixture
def old_store():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        export_dir = Path(tmp) / "export"
        conn = create_store(db_path)
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DROP INDEX IF EXISTS idx_paper_fields_tier")
        conn.execute("DROP TABLE paper_fields")
        conn.execute(OLD_PAPER_FIELDS)
        conn.execute("CREATE INDEX idx_paper_fields_tier ON paper_fields(tier)")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) VALUES "
                     "('p1', 'paper', 'Cite one', 'Cite one', 'N/A', '2026-09-16', 'seeded')")
        conn.execute("INSERT INTO paper_fields (record_id, tier, citation, access, disposition, checked_against_source) VALUES "
                     "('p1', 'read', 'Cite one', 'arXiv:0000.00001', 'd', 'never')")
        conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES ('p1', 'qc', 'r -- fixture')")
        conn.commit(); conn.close()
        yield db_path, export_dir


def _run(db_path: Path, export_dir: Path, args: list[str], script: Path = SCRIPT) -> subprocess.CompletedProcess:
    wrapper = (
        "import sys, importlib.util\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('mig', {str(script)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r}); mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        # A throwaway store: the verified backup goes beside it, not into store/backups.
        f"mod.__dict__.get('backup_before_write') and setattr(mod, 'backup_before_write', "
        f"lambda db, reason: __import__('store.backup', fromlist=['x']).backup_before_write("
        f"db, reason, Path({str(db_path.parent / 'backups')!r})))\n"
        f"raise SystemExit(mod.main({args!r}))\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True)


def _cols(db_path: Path) -> list[str]:
    conn = connect(db_path)
    try:
        return [r["name"] for r in conn.execute("PRAGMA table_info(paper_fields)")]
    finally:
        conn.close()


def test_dry_run_plans_and_changes_nothing(old_store):
    db_path, export_dir = old_store
    proc = _run(db_path, export_dir, [])
    assert proc.returncode == 0, proc.stderr
    assert "PLANNED (dry run)" in proc.stdout
    assert "citation" in _cols(db_path)
    assert not export_dir.exists()


def test_apply_drops_the_column_adds_the_check_and_keeps_dependents(old_store):
    db_path, export_dir = old_store
    proc = _run(db_path, export_dir, ["--apply"])
    assert proc.returncode == 0, proc.stderr
    assert "citation" not in _cols(db_path)
    conn = connect(db_path)
    try:
        ddl = conn.execute("SELECT sql FROM sqlite_master WHERE name='paper_fields'").fetchone()["sql"]
        assert "checked_against_source IS NOT NULL" in ddl
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("SELECT COUNT(*) FROM paper_applicability WHERE record_id='p1'").fetchone()[0] == 1
        assert conn.execute("SELECT name FROM sqlite_master WHERE name='idx_paper_fields_tier'").fetchone() is not None
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE paper_fields SET checked_against_source = NULL WHERE record_id='p1'")
    finally:
        conn.close()
    # Migrations run in order (Sprint 6 Task E, 2026-10-03): a store this old
    # is exported only after the Sprint 6 migration, which this chains.
    assert "export NOT regenerated" in proc.stdout and not export_dir.exists()
    later = _run(db_path, export_dir, ["--apply"], ROOT / "scripts" / "migrate_sprint6_reference_fields.py")
    assert later.returncode == 0, later.stderr
    assert (export_dir / "papers.json").exists()


def test_apply_is_idempotent(old_store):
    db_path, export_dir = old_store
    assert _run(db_path, export_dir, ["--apply"]).returncode == 0
    second = _run(db_path, export_dir, ["--apply"])
    assert second.returncode == 0 and "already migrated" in second.stdout
