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
