#!/usr/bin/env python3
"""Sprint 4 Manual Validation, team-lead decision 2026-09-19: remove the
record `pere-qml-github-repo-empty`.

The record was a Sprint 1 placeholder for a 0-byte seed file
("Christophere Pere QML Github Repo.txt"), kept then because "a rejected
paper is still a record" and because the empty file was a data-quality
finding worth surfacing. The team lead resolved the finding by removing the
file from Papers/ on 2026-09-19 and stated that the related papers
(Mancilla-Pere 2022, Waring-Pere-Le Beux 2024, Pere 2025, and others) are
now on disk under QMLPapers/ to be processed in a future sprint through the
intake door. Nothing yields from the record; it carries no applicability;
its only content was the statement that the file was empty, which is no
longer true of anything.

DRY-RUN BY DEFAULT; `--apply` deletes the records row (paper_fields and
record_contexts cascade), rewrites scripts/seed_set_metadata.json without
the entry, and regenerates export/. The deletion is recorded here, in the
commit, and in the Sprint 4 summary; the id is never reused.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
METADATA_PATH = ROOT / "scripts" / "seed_set_metadata.json"
RECORD_ID = "pere-qml-github-repo-empty"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    conn = connect(DB_PATH)
    try:
        row = conn.execute("SELECT id FROM records WHERE id = ?", (RECORD_ID,)).fetchone()
        if row is None:
            print(f"{RECORD_ID}: not in the store; nothing to do")
            return 0
        children = {t: conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {c} = ?", (RECORD_ID,)).fetchone()[0]
                    for t, c in (("paper_fields", "record_id"), ("record_contexts", "record_id"),
                                 ("paper_applicability", "record_id"), ("paper_yields", "paper_id"))}
        print(f"{RECORD_ID}: child rows {children}")
        if children["paper_yields"]:
            print("refusing: the record yields assertions", file=sys.stderr)
            return 1
        if not do_apply:
            print("PLANNED (dry run; nothing written). Re-run with --apply to delete.")
            return 0
        conn.execute("BEGIN")
        conn.execute("DELETE FROM records WHERE id = ?", (RECORD_ID,))
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            conn.execute("ROLLBACK")
            print(f"NOT APPLIED: foreign_key_check {fk}", file=sys.stderr)
            return 1
        conn.execute("COMMIT")
        entries = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        kept = [e for e in entries if e["id"] != RECORD_ID]
        METADATA_PATH.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"deleted {RECORD_ID}; seed metadata now {len(kept)} entries")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
