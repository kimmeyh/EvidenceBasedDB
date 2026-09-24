#!/usr/bin/env python3
"""Restore store/evidence.db from a backup (Sprint 5 Task A, F30 part 3).

A restore is a script with a test, not a documented gesture.

Dry run by default: verifies the backup (integrity_check) and prints what
the restore would change -- the backup's record counts per class against
the current store's. Nothing is written.

--apply: backs the CURRENT store up first (so a restore is itself
reversible), then copies the backup into store/evidence.db with SQLite's
backup API, then checks the restored store's integrity and counts. The
export is NOT regenerated automatically: compare it first
(`python scripts/regenerate_export.py`, then `git diff export/`), because
a restore that silently rewrites the committed artifact would hide what
changed.

Usage:
  python scripts/restore_store.py --list
  python scripts/restore_store.py <backup.db> [--apply]
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402
from store.backup import (  # noqa: E402
    _class_counts, backup_before_write, default_backups_dir, parse_name, verify_backup,
)

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)


def _counts(path: Path) -> dict[str, int]:
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        return _class_counts(conn)
    finally:
        conn.close()


def restore(backup: Path, db_path: Path) -> None:
    """Copy `backup` over `db_path` with the backup API and verify the result."""
    expected = _counts(backup)
    verify_backup(backup, expected)
    src = sqlite3.connect(f"file:{backup.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(db_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    verify_backup(db_path, expected)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--list" in args:
        for p in sorted(default_backups_dir(DB_PATH).glob("evidence-*.db")):
            if parse_name(p):
                print(f"{p.name}  {_counts(p)}")
        return 0
    positional = [a for a in args if not a.startswith("--")]
    if len(positional) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    backup = Path(positional[0])
    if not backup.is_absolute() and not backup.exists():
        backup = default_backups_dir(DB_PATH) / backup
    if not backup.exists():
        print(f"error: {backup} does not exist", file=sys.stderr)
        return 1
    target = _counts(backup)
    verify_backup(backup, target)
    current = _counts(DB_PATH) if DB_PATH.exists() else {}
    print(f"backup  : {backup.name}  {target}  (integrity ok)")
    print(f"current : {DB_PATH.name}  {current}")
    if "--apply" not in args:
        print("PLANNED (dry run; nothing written). Re-run with --apply to restore.")
        return 0
    if DB_PATH.exists():
        backup_before_write(DB_PATH, "before restore")
    restore(backup, DB_PATH)
    print(f"RESTORED {DB_PATH} from {backup.name}; verified. Regenerate and diff the export before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
