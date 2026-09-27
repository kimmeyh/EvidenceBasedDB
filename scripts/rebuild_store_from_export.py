#!/usr/bin/env python3
"""Rebuild the store from the committed export (Sprint 5 Task A, F30 part 1).

The missing recovery path: regenerate_export.py goes store -> export, and
until now nothing went the other way. See store/rebuild.py.

Dry run by default (QUALITY_STANDARDS.md): rebuilds into a throwaway
store, regenerates its export, and reports whether it is byte-identical
to export/. Nothing in the repository or the store changes.

--apply writes a NEW store at store/evidence.db, and only if none exists
there. Replacing an existing store is restore_store.py's job, which backs
the current store up first; this script never overwrites one.

--no-local-path-check skips the one door rule that depends on the machine
(a hand-origin paper's local file exists here). Use it on a machine
without D:/Data/Harold/EvidenceBasedDB; the rebuilt records are the same.

Usage: python scripts/rebuild_store_from_export.py [--apply] [--no-local-path-check]
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.rebuild import compare_exports, rebuild, rebuild_and_compare  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check_local = "--no-local-path-check" not in args
    if "--apply" not in args:
        diffs = rebuild_and_compare(EXPORT_DIR, check_local_paths=check_local)
        if diffs:
            print(f"FAIL: a store rebuilt from {EXPORT_DIR} regenerates a DIFFERENT export: {diffs}")
            return 1
        print(f"OK: a store rebuilt from {EXPORT_DIR} regenerates it byte-identically.")
        print("PLANNED (dry run; nothing written). Re-run with --apply to write store/evidence.db.")
        return 0
    if DB_PATH.exists():
        print(f"error: {DB_PATH} exists. This script never overwrites a store; "
              "use scripts/restore_store.py, which backs the current one up first.", file=sys.stderr)
        return 1
    conn = rebuild(EXPORT_DIR, DB_PATH, check_local_paths=check_local)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            regenerate(conn, tmp)
            diffs = compare_exports(EXPORT_DIR, tmp)
    finally:
        conn.close()
    if diffs:
        DB_PATH.unlink()
        print(f"FAIL: rebuilt store regenerates a different export ({diffs}); store removed.", file=sys.stderr)
        return 1
    print(f"WROTE {DB_PATH}; its regenerated export is byte-identical to {EXPORT_DIR}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
