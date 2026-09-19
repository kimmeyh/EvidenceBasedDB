"""The Evidence Based DB store: SQLite as the store of record.

ADR-0004 section 2: SQLite first, with a deterministic text export
regenerated from it (store/export.py, Task C). The store is a build
output; the export is the artifact.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_CONTEXTS_PATH = Path(__file__).parent / "seed_contexts.sql"


def script_paths(script_file: str) -> tuple[Path, Path, Path]:
    """(ROOT, DB_PATH, EXPORT_DIR) for a script under scripts/, given its
    own __file__.

    F6 finding 5 (PR #1 review): `ROOT = Path(__file__).resolve().parents[1]`,
    `DB_PATH = ROOT / "store" / "evidence.db"`, and `EXPORT_DIR = ROOT /
    "export"` were copy-pasted near-identically across every ingestion/
    correction script. This collapses that computation to one place.

    Callers still assign the results to their OWN module-level ROOT/
    DB_PATH/EXPORT_DIR names (not import this function's return value by
    reference) -- several tests monkeypatch a loaded script module's
    `mod.DB_PATH`/`mod.EXPORT_DIR` attributes directly, which only works
    if each script still owns its own reassignable module-level name.
    `sys.path.insert(0, str(ROOT))` and the `from store import ...` lines
    stay in each script too: they must run BEFORE this function (part of
    `store`) can be imported at all, so folding them in here would be
    circular.
    """
    root = Path(script_file).resolve().parents[1]
    return root, root / "store" / "evidence.db", root / "export"


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open a connection with foreign keys enabled.

    SQLite disables foreign-key enforcement by default, per connection --
    forgetting this makes every REFERENCES clause in schema.sql decorative.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_store(db_path: str | Path) -> sqlite3.Connection:
    """Create a new store at db_path from schema.sql and return an open connection.

    Raises if db_path already exists, so this never silently overwrites a
    populated store -- rebuild from the committed export instead of calling
    this on an existing file.
    """
    db_path = Path(db_path)
    if db_path.exists():
        raise FileExistsError(
            f"{db_path} already exists. create_store() never overwrites a "
            "store; delete it explicitly first if that is genuinely intended."
        )
    conn = connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.executescript(SEED_CONTEXTS_PATH.read_text(encoding="utf-8"))
    conn.commit()
    return conn
