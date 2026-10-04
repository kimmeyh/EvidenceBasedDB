#!/usr/bin/env python3
"""Attach the verified QMLPapers repository notes to their papers (Sprint 6
Task K, F35; INTAKE_WORKFLOW section 9).

Each `QMLPapers/Repos/*_repo.md` note names a repository, the owning
paper's arXiv id, and quotes the sentence in the paper that announces the
release. The note is local evidence, not the record: the repository enters
through the door's GitHub path (`scripts/intake.py`), and a `code-of`
source link (ADR-0005 A4 field 6) ties it to the paper, carrying the quoted
sentence. Removing the link never touches either record.

Set GITHUB_TOKEN (for example from `gh auth token`) first: unauthenticated,
GitHub allows 60 requests an hour. The token is read by store/citations.py
and never printed.

DRY-RUN BY DEFAULT: resolves every note and reports what it would do.
`--apply` takes a verified backup, then writes per note (repository record
if absent, then the link) and commits each, so a stop loses nothing.

    python scripts/link_code_repositories.py
    python scripts/link_code_repositories.py --apply
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import add_found_via, add_source_link, insert_paper  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
REPOS = Path(r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\Repos")
_ARXIV = re.compile(r"\*\*arXiv:\*\*\s*\[(\d{4}\.\d{4,5})\]")
_REPO = re.compile(r"\*\*Repository:\*\*\s*\[([^\]]+)\]")
_QUOTE = re.compile(r"## Where the link appears\s*\n((?:>.*\n?)+)")


def read_note(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    a, r, q = _ARXIV.search(text), _REPO.search(text), _QUOTE.search(text)
    if not (a and r and q):
        return None
    # The GitHub pattern directly, not parse_access: a repository named
    # "arXiv-2502.18361-..." would otherwise be read as an arXiv id.
    gh = citations._GITHUB.search(r.group(1))
    quote = " ".join(line.lstrip("> ").strip() for line in q.group(1).splitlines()).strip()
    return {"note": path.name, "arxiv": a.group(1), "repo_url": r.group(1),
            "repo": f"{gh.group(1)}/{gh.group(2)}" if gh and r.group(1).rstrip("/").endswith(gh.group(2)) else None,
            "evidence": quote}


def paper_for(conn, arxiv_id: str) -> str | None:
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields WHERE access LIKE ?", (f"%{arxiv_id}%",)):
        parsed = citations.parse_access(access)
        if parsed == ("arxiv", arxiv_id):
            return rid
    return None


def repo_record(conn, owner_name: str) -> str | None:
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields WHERE access LIKE ?",
                                    (f"%github.com/{owner_name}%",)):
        parsed = citations.parse_access(access)
        if parsed and parsed[0] == "github" and parsed[1].lower() == owner_name.lower():
            return rid
    return None


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    print(f"GitHub token present: {citations.github_token() is not None}")
    today = date.today().isoformat()
    if apply:
        backup_before_write(DB_PATH, "link code repositories")
    conn = connect(DB_PATH)
    counts = {"linked": 0, "new repo records": 0, "already linked": 0}
    problems: list[str] = []
    try:
        for path in sorted(REPOS.glob("*_repo.md")):
            note = read_note(path)
            if note is None or note["repo"] is None:
                problems.append(f"{path.name}: note unreadable or not a GitHub repository")
                continue
            paper = paper_for(conn, note["arxiv"])
            if paper is None:
                problems.append(f"{path.name}: paper arXiv:{note['arxiv']} is not in the store")
                continue
            existing = repo_record(conn, note["repo"])
            if existing and conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = "
                                         "'code-of'", (existing, paper)).fetchone():
                counts["already linked"] += 1
                continue
            route = f"QMLPapers/Repos/{path.name}"
            if existing is None:
                try:
                    record = intake.build_record({
                        "access": f"https://github.com/{note['repo']}", "kind": "repo", "context": "qml",
                        "disposition": f"Code repository: released with {paper} (arXiv:{note['arxiv']}), per the "
                                       "paper's own sentence; not yet screened",
                        "found_via": route, "cited_as": note["repo_url"]}, today=today)
                except (ValueError, LookupError, OSError) as ex:
                    problems.append(f"{path.name}: {note['repo']} did not resolve ({str(ex)[:120]})")
                    continue
                existing = record.id
                # GitHub answers with the CANONICAL owner/name, so two notes
                # with different URLs (a rename, a redirect, a case change) can
                # derive the same record id (Task K re-run, 2026-10-04).
                if conn.execute("SELECT 1 FROM records WHERE id = ?", (existing,)).fetchone():
                    if apply and not conn.execute("SELECT 1 FROM paper_found_via WHERE record_id = ? AND route = ?",
                                                  (existing, route)).fetchone():
                        add_found_via(conn, existing, route, note["repo_url"])
                    if conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = "
                                    "'code-of'", (existing, paper)).fetchone():
                        counts["already linked"] += 1
                        continue
                else:
                    if apply:
                        insert_paper(conn, record)
                    counts["new repo records"] += 1
            elif apply and not conn.execute("SELECT 1 FROM paper_found_via WHERE record_id = ? AND route = ?",
                                            (existing, route)).fetchone():
                add_found_via(conn, existing, route, note["repo_url"])
            if existing == paper:
                problems.append(f"{path.name}: {note['repo']} resolves to the paper's own record {paper}; not linked")
                continue
            if apply:
                add_source_link(conn, existing, paper, "code-of", note["evidence"])
                conn.commit()
            counts["linked"] += 1
            print(f"{'LINK' if apply else 'PLAN'} {existing} code-of {paper}")
        for p in problems:
            print("REPORT", p)
        print(f"\n{counts}; reported {len(problems)}")
        if apply:
            regenerate(conn, EXPORT_DIR)
            print("APPLIED; export regenerated")
        else:
            print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
