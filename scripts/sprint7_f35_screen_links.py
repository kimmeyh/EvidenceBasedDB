#!/usr/bin/env python3
"""F35's held-back repository candidates, screened (Sprint 7 Task E, the
optional slice of F54's card "unless time allows").

`QMLPapers\\Repos\\REVIEW.md` held 218 repository URLs the Sprint 6
extractor would not link on its own: 78 scored >= 0. A screening pass
(Sonnet 5.5 subagent, 2026-10-06, read-only) classified those 78 into
`scripts/sprint7_f35_screen.json`: 42 own (40 distinct), 26 third-party,
10 unsure. Each "own" row was then checked independently: the repository
resolves on GitHub (40 of 40), and the quoted sentence is in the paper's
own PDF (40 of 40, pdftotext, punctuation-insensitive).

Linked here: every "own" row with a link type, as `code-of` or
`dataset-of`, carrying the paper's own sentence and how it was found.
Held back, reported: third-party (not this paper's code), unsure (no
sentence announces the repository, or it does not resolve), and one
survey's paper list (neither code nor data).

DRY-RUN BY DEFAULT. `--apply` takes a verified backup, then writes per row
and commits each.

    python scripts/sprint7_f35_screen_links.py
    python scripts/sprint7_f35_screen_links.py --apply
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_found_via, add_source_link, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("link_code_repositories",
                                               Path(__file__).with_name("link_code_repositories.py"))
linker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(linker)
intake = linker.intake

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
SCREEN = Path(__file__).with_name("sprint7_f35_screen.json")
ROUTE = "QMLPapers/Repos/REVIEW.md"
HOW = ("held back by the Sprint 6 extractor (QMLPapers/Repos/REVIEW.md); screened 2026-10-06: the paper's own "
       "sentence announces it, the repository resolves on GitHub")


def rows_to_link(rows: list[dict]) -> list[dict]:
    """'own' rows with a repository and a link type, each pair once."""
    out, seen = [], set()
    for row in rows:
        key = (row["arxiv"], (row["repo"] or "").lower())
        if row["verdict"] == "own" and row["repo"] and row["link_type"] and row["sentence"] and key not in seen:
            seen.add(key)
            out.append(row)
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    rows = json.loads(SCREEN.read_text(encoding="utf-8"))
    print("screen verdicts:", dict(Counter(r["verdict"] for r in rows)))
    today = date.today().isoformat()
    if apply:
        backup_before_write(DB_PATH, "F35 screened repository links")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")  # Task C's probe run writes meanwhile
    counts = Counter()
    try:
        for row in rows_to_link(rows):
            paper = linker.paper_for(conn, row["arxiv"])
            if paper is None:
                print(f"REPORT arXiv:{row['arxiv']}: the paper is not in the store")
                counts["paper not in store"] += 1
                continue
            existing = linker.repo_record(conn, row["repo"])
            if existing is None:
                try:
                    record = intake.build_record({
                        "access": f"https://github.com/{row['repo']}", "kind": "repo", "context": "qml",
                        "disposition": f"Code repository: released with {paper} (arXiv:{row['arxiv']}), per the "
                                       "paper's own sentence; not yet screened",
                        "found_via": ROUTE, "cited_as": row["candidate"]}, today=today)
                except (ValueError, LookupError, OSError) as ex:
                    print(f"FAILED {row['repo']}: did not resolve ({str(ex)[:160]})")
                    counts["failed"] += 1
                    continue
                existing = record.id
                if conn.execute("SELECT 1 FROM records WHERE id = ?", (existing,)).fetchone() is None:
                    if apply:
                        insert_paper(conn, record)
                    counts["new records"] += 1
            elif apply and not conn.execute("SELECT 1 FROM paper_found_via WHERE record_id = ? AND route = ?",
                                            (existing, ROUTE)).fetchone():
                add_found_via(conn, existing, ROUTE, row["candidate"])
            if existing == paper:
                print(f"REPORT {row['repo']} resolves to the paper's own record {paper}; not linked")
                counts["self"] += 1
                continue
            if conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = ?",
                            (existing, paper, row["link_type"])).fetchone():
                counts["already linked"] += 1
                continue
            if apply:
                add_source_link(conn, existing, paper, row["link_type"],
                                f"{row['sentence']} [How found (Sprint 7 F35 screen): {HOW}.]")
                conn.commit()
            counts["linked"] += 1
            print(f"{'LINK' if apply else 'PLAN'} {existing} {row['link_type']} {paper}")
        for row in rows:
            if row["verdict"] == "unsure" or (row["verdict"] == "own" and not row["link_type"]):
                print(f"HELD {row['arxiv']} {row['candidate']}: {row['why']}")
        print(f"\n{dict(counts)}")
        print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
        return 1 if counts["failed"] else 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
