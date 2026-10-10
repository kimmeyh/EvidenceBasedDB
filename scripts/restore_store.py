#!/usr/bin/env python3
"""Restore the store's evidence.db from a backup (Sprint 5 Task A, F30 part 3).
The store is at store.store_dir() since ADR-0004 A7, outside the repository.

A restore is a script with a test, not a documented gesture.

Dry run by default: verifies the backup (integrity_check) and prints what
the restore would change -- the backup's record counts per class against
the current store's. Nothing is written.

--apply: backs the CURRENT store up first (so a restore is itself
reversible), then copies the backup into the store with SQLite's backup
API, then checks the restored store's integrity and counts. No export is
committed since ADR-0004 A7; to see what a restore changed, dump before and
after with `python scripts/regenerate_export.py --out <dir>` and compare.

Usage:
  python scripts/restore_store.py --list
  python scripts/restore_store.py <backup.db> [--apply]
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402
from store.backup import (  # noqa: E402
    BackupVerificationError, _class_counts, backup_before_write, current_sprint, default_backups_dir, parse_name,
    verify_backup,
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
    try:
        current = _counts(DB_PATH) if DB_PATH.exists() else {}
    except sqlite3.DatabaseError as ex:
        current = f"UNREADABLE ({ex})"
    print(f"backup  : {backup.name}  {target}  (integrity ok)")
    print(f"current : {DB_PATH.name}  {current}")
    if "--apply" not in args:
        print("PLANNED (dry run; nothing written). Re-run with --apply to restore.")
        return 0
    if DB_PATH.exists():
        # The backup being restored is protected from this call's own prune
        # (fresh-eyes review, 2026-09-24: an old backup could be deleted by
        # the prune inside backup_before_write before restore() opened it).
        try:
            backup_before_write(DB_PATH, "before restore", protect=(backup,))
        except (BackupVerificationError, sqlite3.DatabaseError) as ex:
            # A corrupt live store is the main reason to restore, and it
            # cannot pass verification (same review). Keep it, byte for
            # byte and named as unverified, then restore into a fresh file.
            aside = default_backups_dir(DB_PATH) / (
                f"evidence-{datetime.now().strftime('%Y%m%dT%H%M%S%f')}-sprint{current_sprint()}-"
                "unverified-live-store-before-restore.db")
            aside.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(DB_PATH), aside)
            print(f"live store failed verification ({ex}); moved aside UNVERIFIED to {aside}")
    restore(backup, DB_PATH)
    print(f"RESTORED {DB_PATH} from {backup.name}; verified. To see what changed, dump before and after with "
          "scripts/regenerate_export.py --out <dir> and compare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
