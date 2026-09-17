#!/usr/bin/env python3
"""Regenerate the committed export from store/evidence.db (Sprint 1 Task C).

Run after any change to the store's data. The export is the artifact
(ADR-0004 section 2); this script is how it gets regenerated rather than
hand-edited.

Usage: python scripts/regenerate_export.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402

DB_PATH = ROOT / "store" / "evidence.db"
EXPORT_DIR = ROOT / "export"


def main() -> int:
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist. Run store.create_store() first.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    regenerate(conn, EXPORT_DIR)
    conn.close()
    print(f"Regenerated export at {EXPORT_DIR} from {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
