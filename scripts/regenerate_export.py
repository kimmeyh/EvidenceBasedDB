#!/usr/bin/env python3
"""Write an ON-DEMAND dump of the store (Sprint 1 Task C; reworked by
Sprint 7 Task B, F58, under ADR-0004 A7).

Until 2026-10-06 this regenerated the committed export, which ADR-0004
section 2 called the artifact. A7 retired that export: the store, outside
the repository, is the record, and a dump is written only when asked, to a
folder outside the repository (store.export.regenerate refuses one inside).

Usage: python scripts/regenerate_export.py --out <dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--out" not in args or args.index("--out") + 1 >= len(args):
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(args[args.index("--out") + 1])
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        regenerate(conn, out)
    finally:
        conn.close()
    print(f"Wrote a dump of {DB_PATH} to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
