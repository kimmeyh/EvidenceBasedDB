#!/usr/bin/env python3
"""F54's last item (Sprint 7 Task E): enter the paper whose PDF sits in
QMLPapers/2021 under the wrong name, and link its code.

`Asfaw-et-al._2021_Building-a-Quantum-Engineering-Undergraduate-Program__2108.0131.pdf`
begins "arXiv:2108.00131v2 [cs.LG]": Radhakrishnan, Stefanakis, Belkin and
Uhler, infinite-width neural networks for matrix completion. Its repository
note names `uhlerlab/ntk_matrix_` (the name broken at a line wrap; the note
quotes "https://github.com/uhlerlab/ntk_matrix_ completion"), which exists
as uhlerlab/ntk_matrix_completion. The manifest row's own paper (Asfaw et
al.) is F60.

ONE arXiv request (the door's paced fetcher), run in a pause of Task C's
capped probe run (Q8: E runs during C's pauses). DRY-RUN BY DEFAULT;
`--apply` takes a verified backup first.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_source_link, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("link_code_repositories",
                                               Path(__file__).with_name("link_code_repositories.py"))
linker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(linker)
intake = linker.intake

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
NOTE = "Asfaw-et-al._2021_Building-a-Quantum-Engineering-Undergraduate-Program__2108.0131_repo.md"
MANIFEST_ROUTE = "QMLPapers/2021/manifest.tsv"
HOW = ("the note's URL was broken at a line wrap (it quotes \"ntk_matrix_ completion\"); the owner's public "
       "repositories (GitHub API users/uhlerlab/repos, 2026-10-06) hold uhlerlab/ntk_matrix_completion")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    today = date.today().isoformat()
    note = (linker.REPOS / NOTE).read_text(encoding="utf-8")
    quote_m = linker._QUOTE.search(note)
    quote = " ".join(line.lstrip("> ").strip() for line in quote_m.group(1).splitlines()).strip()
    citations.assume_recent_arxiv_request()  # Task C's run may have asked arXiv recently
    fetcher = citations.PacedFetcher()
    paper = intake.build_record({
        "access": "arXiv:2108.00131", "context": "ml", "tier": "seen",
        "disposition": "Infinite-width neural networks (NTK) for matrix completion; its PDF was filed in "
                       "QMLPapers/2021 under the Asfaw et al. row with the id 2108.0131 (F60); not yet screened",
        "found_via": MANIFEST_ROUTE, "cited_as": "Asfaw-et-al._2021_..._2108.0131.pdf (the file's first page reads "
                                                 "arXiv:2108.00131v2)"}, fetcher=fetcher, today=today)
    repo = intake.build_record({
        "access": "https://github.com/uhlerlab/ntk_matrix_completion", "kind": "repo", "context": "ml",
        "disposition": f"Code repository: released with {paper.id} (arXiv:2108.00131), per the paper's own "
                       "sentence; not yet screened",
        "found_via": f"QMLPapers/Repos/{NOTE}", "cited_as": "https://github.com/uhlerlab/ntk_matrix_"},
        fetcher=fetcher, today=today)
    print(f"paper {paper.id}: {paper.citation}\nrepo  {repo.id}\nlink  {repo.id} code-of {paper.id}")
    if not apply:
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F54 enter 2108.00131")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        for record in (paper, repo):
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (record.id,)).fetchone() is None:
                insert_paper(conn, record)
        if not conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = 'code-of'",
                            (repo.id, paper.id)).fetchone():
            add_source_link(conn, repo.id, paper.id, "code-of", f"{quote} [How found (Sprint 7 F54): {HOW}.]")
        conn.commit()
    finally:
        conn.close()
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
