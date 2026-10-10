#!/usr/bin/env python3
"""Rebuild a store from a dump (Sprint 5 Task A, F30 part 1; reworked by
Sprint 7 Task B, F58, under ADR-0004 A7).

Since A7 there is no committed export: a dump is written on demand
(`scripts/regenerate_export.py --out <dir>`), and this script rebuilds a
store from one. The store's own recovery path is its verified backups
(`scripts/restore_store.py`); this is the second path, from a dump.

Dry run by default (QUALITY_STANDARDS.md): rebuilds into a throwaway store,
dumps it again, and reports whether the dump is byte-identical to the one
it came from. Nothing changes.

--apply writes a NEW store at the store location (store.store_dir()), and
only if none exists there. Replacing an existing store is restore_store.py's
job, which backs the current store up first; this script never overwrites.

--no-local-path-check skips the one door rule that depends on the machine
(a hand-origin paper's local file exists here).

Usage: python scripts/rebuild_store_from_export.py --from <dir> [--apply] [--no-local-path-check]
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

ROOT, DB_PATH, _ = script_paths(__file__)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--from" not in args or args.index("--from") + 1 >= len(args):
        print(__doc__, file=sys.stderr)
        return 2
    source = Path(args[args.index("--from") + 1])
    check_local = "--no-local-path-check" not in args
    if "--apply" not in args:
        diffs = rebuild_and_compare(source, check_local_paths=check_local)
        if diffs:
            print(f"FAIL: a store rebuilt from {source} dumps a DIFFERENT export: {diffs}")
            return 1
        print(f"OK: a store rebuilt from {source} dumps it byte-identically.")
        print(f"PLANNED (dry run; nothing written). Re-run with --apply to write {DB_PATH}.")
        return 0
    if DB_PATH.exists():
        print(f"error: {DB_PATH} exists. This script never overwrites a store; "
              "use scripts/restore_store.py, which backs the current one up first.", file=sys.stderr)
        return 1
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = rebuild(source, DB_PATH, check_local_paths=check_local)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            regenerate(conn, tmp)
            diffs = compare_exports(source, tmp)
    finally:
        conn.close()
    if diffs:
        DB_PATH.unlink()
        print(f"FAIL: rebuilt store dumps a different export ({diffs}); store removed.", file=sys.stderr)
        return 1
    print(f"WROTE {DB_PATH}; its dump is byte-identical to {source}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
