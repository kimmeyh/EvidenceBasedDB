"""The Evidence Based DB store: SQLite as the store of record.

ADR-0004 section 2 made the committed text export the artifact. Since
ADR-0004 A7 (2026-10-06) the store itself is the record, it lives outside
the repository, and its verified backups are the recovery path; the export
(store/export.py) is an on-demand dump only.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path, PureWindowsPath

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_CONTEXTS_PATH = Path(__file__).parent / "seed_contexts.sql"

# ADR-0004 A7 (Sprint 7 Task B, F58, 2026-10-06): the store and its backups
# live OUTSIDE every repository. One setting, read here and nowhere else:
# the default below, or the environment variable EBDB_STORE_DIR (tests and
# CI point it at a temporary folder).
DEFAULT_STORE_DIR = PureWindowsPath(r"D:\Data\Harold\EvidenceBasedDB\store")
STORE_DIR_ENV = "EBDB_STORE_DIR"


def _on_windows() -> bool:
    return os.name == "nt"  # a function, so tests can take either branch on any OS


def store_dir() -> Path:
    """The folder holding evidence.db and backups/ (ADR-0004 A7).

    The default is a Windows path. Off Windows, `Path(r"D:\\...")` is ONE
    relative segment and resolves inside the current folder, which is the
    repository on CI (Task B review, 2026-10-06: CI went red on exactly
    this). So off Windows the override is required, and its absence raises."""
    override = (os.environ.get(STORE_DIR_ENV) or "").strip()
    if override:
        return Path(override)
    if not _on_windows():
        raise RuntimeError(
            f"The default store folder {DEFAULT_STORE_DIR} is a Windows path. On this system set "
            f"{STORE_DIR_ENV} to the store folder (ADR-0004 A7); without it the path would resolve "
            "inside the current folder.")
    return Path(DEFAULT_STORE_DIR)


# F136 (Sprint 16 Task A): each PDF's text is extracted once, ever (team lead, 2026-11-05). The cache used to be
# `store_dir() / "text_cache"`, so a trial on a store copy (EBDB_STORE_DIR pointed elsewhere) found an empty cache
# and extracted all 894 PDFs again (Sprint 15, about 25 minutes). The cache now has one fixed folder that does NOT
# follow EBDB_STORE_DIR; only its own variable moves it.
TEXT_CACHE_ENV = "EBDB_TEXT_CACHE_DIR"
DEFAULT_DATA_DIR = DEFAULT_STORE_DIR.parent  # the non-repository data folder: Papers, Books, ocr-venv


def text_cache_dir() -> Path:
    """The one text cache every store and every store copy reads: EBDB_TEXT_CACHE_DIR, or the live store's
    `text_cache\\`. Off Windows without the variable it raises, as `store_dir` does, and the callers then simply do
    not use a cache."""
    override = (os.environ.get(TEXT_CACHE_ENV) or "").strip()
    if override:
        return Path(override)
    if not _on_windows():
        raise RuntimeError(f"No text cache off Windows unless {TEXT_CACHE_ENV} names one.")
    return Path(DEFAULT_STORE_DIR) / "text_cache"


class _NoCommittedExport:
    """What script_paths returns where EXPORT_DIR used to be.

    ADR-0004 A7 retired the committed export (Q1 = 2). A historical one-off
    that still calls `regenerate(conn, EXPORT_DIR)` must fail loudly rather
    than write an export into the repository; store.export.regenerate
    refuses this value with the reason. On-demand dumps name their folder:
    `scripts/regenerate_export.py --out <dir>`."""

    def __repr__(self) -> str:  # pragma: no cover -- diagnostics only
        return "<no committed export since ADR-0004 A7>"

    def __fspath__(self) -> str:
        raise RuntimeError(
            "There is no committed export since ADR-0004 A7 (2026-10-06). Write an on-demand dump "
            "with scripts/regenerate_export.py --out <dir outside the repository>.")


NO_COMMITTED_EXPORT = _NoCommittedExport()


def script_paths(script_file: str) -> tuple[Path, Path, object]:
    """(ROOT, DB_PATH, EXPORT_DIR) for a script under scripts/, given its
    own __file__. Since ADR-0004 A7, DB_PATH is under store_dir() (outside
    the repository) and EXPORT_DIR is NO_COMMITTED_EXPORT.

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
    return root, store_dir() / "evidence.db", NO_COMMITTED_EXPORT


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
    populated store -- restore a verified backup (scripts/restore_store.py)
    instead of calling this on an existing file.
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
