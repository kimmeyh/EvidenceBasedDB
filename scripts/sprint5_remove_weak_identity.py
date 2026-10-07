#!/usr/bin/env python3
"""Sprint 5 Manual Validation, team-lead decision Q8 (2026-09-25): remove
the three topic-screened papers weakest on authorship.

They passed the QML/ML topic screen (revised Q1) but are the least likely
to be by the QCi person whose name matched: an MRI-reconstruction paper and
a dental deep-learning paper under "Yu-Ping Huang" (a common family name),
and a human-motion-generation paper under "Sam Wu". Nothing yields from
them. The two downloaded PDFs are removed with them; the screen script
lists all three in REJECTED so a re-run does not re-admit them.

Follows scripts/sprint4_remove_pere_placeholder.py: DRY RUN BY DEFAULT;
`--apply` takes a verified backup (F30), deletes the records (child rows
cascade), checks foreign keys, regenerates export/. Ids are never reused.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
ACCESS = ["arXiv:2405.02958", "DOI:10.1101/2021.05.04.21256502", "arXiv:2603.15546"]
PDF_ROOT = Path(r"D:\Data\Harold\EvidenceBasedDB\QCiAuthorsPapers")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    conn = connect(DB_PATH)
    try:
        ids = []
        for acc in ACCESS:
            row = conn.execute("SELECT record_id FROM paper_fields WHERE lower(access) = lower(?)", (acc,)).fetchone()
            if row is None:
                print(f"{acc}: not in the store; nothing to do")
                continue
            if conn.execute("SELECT COUNT(*) FROM paper_yields WHERE paper_id = ?", (row[0],)).fetchone()[0]:
                print(f"refusing: {row[0]} yields assertions", file=sys.stderr)
                return 1
            ids.append(row[0])
            print(f"REMOVE {row[0]} ({acc})")
        pdfs = [p for p in PDF_ROOT.rglob("*.pdf") if any(a[6:] in p.name for a in ACCESS if a.startswith("arXiv:"))]
        for p in pdfs:
            print(f"REMOVE file {p}")
        if not apply:
            print("PLANNED (dry run; nothing written). Re-run with --apply.")
            return 0
    finally:
        conn.close()
    backup_before_write(DB_PATH, "remove weak identity --apply")
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        for rid in ids:
            conn.execute("DELETE FROM records WHERE id = ?", (rid,))
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            conn.execute("ROLLBACK")
            print(f"NOT APPLIED: foreign_key_check {fk}", file=sys.stderr)
            return 1
        conn.execute("COMMIT")
    finally:
        conn.close()
    for p in pdfs:
        p.unlink()
    print(f"deleted {len(ids)} records and {len(pdfs)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
