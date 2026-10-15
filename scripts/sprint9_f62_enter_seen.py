#!/usr/bin/env python3
"""Sprint 9 Task J (F62), Manual Validation Q4 = 1: the discovery candidates
enter the store at `seen`.

Team lead, 2026-10-15: "q4 1": every candidate in the four top-25 lists of
`f62_review_2026-10-15.md` enters, except the 13 named off-topic (OFF_TOPIC,
each pinned to its title so a re-ranked file cannot shift the cut).

Each goes through the door (`intake.build_record`), which derives the id,
title and citation from the identifier, never from OpenAlex. Access is the
arXiv id where OpenAlex or Semantic Scholar gave one (OpenAlex's DOI can be
a mirror's: "Attention Is All You Need" carries a preprint server's DOI),
the DOI otherwise. A candidate whose door title is not the candidate's title
(`same_title`) is REFUSED and listed, never entered: a wrong identifier
attaches a different paper with no error. A candidate the store now holds is
skipped.

The primary context is the stream's (fraud enters as `ml`: the HSBC context
holds the submission's own facts), with per-rank exceptions in
CONTEXT_BY_RANK where the stream's context is plainly wrong (quantum
chemistry in the qml stream, physics in the tensor stream). Screening
refines it; `seen` promises nothing more.

arXiv requests go through the door's paced fetcher (18 s apart, serial).
DRY-RUN BY DEFAULT (nothing fetched); `--apply` takes a verified backup,
fetches, checks and writes, one commit per paper.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import insert_paper  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


intake = _load("intake")
disc = _load("discover_candidates")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-15"
TAG = "Sprint 9 Task J, F62"
REVIEW = Path(r"D:\Data\Harold\EvidenceBasedDB\discovery\f62_review_2026-10-15.json")
REVIEW_MD = REVIEW.with_suffix(".md")
TOP = 25
STREAMS = ("ml", "qml", "tensor", "fraud")

# Team lead's Q4 = 1 exclusions: (stream, rank) -> the title's start.
OFF_TOPIC = {
    ("ml", 6): "SciPy 1.0", ("ml", 9): "Array programming with NumPy", ("ml", 12): "Welcome to the Tidyverse",
    ("ml", 23): "Grey Wolf Optimizer",
    ("qml", 5): "A versatile single-photon-based", ("qml", 6): "Quantum logic with spin qubits",
    ("qml", 15): "Brain tumor detection",
    ("tensor", 4): "The design space of E(3)-equivariant", ("tensor", 7): "Complexity, action, and black holes",
    ("tensor", 11): "Codebase release 0.3 for ITensor", ("tensor", 12): "Learning with Pseudo-Ensembles",
    ("tensor", 15): "Bilayer", ("tensor", 21): "Non-Parametric Estimation of a Multivariate",
}
STREAM_DEFAULT = {"ml": "ml", "qml": "qml", "tensor": "qc", "fraud": "ml"}
CONTEXT_BY_RANK = {
    # qml stream: quantum simulation and chemistry, not learning
    **{("qml", r): "qc" for r in (2, 3, 4, 7, 8, 10, 12, 16, 18, 20, 22, 25)},
    ("qml", 9): "ml",  # a classical deep network for the Schroedinger equation
    # tensor stream: learning and decomposition methods, and condensed-matter physics
    **{("tensor", r): "ml" for r in (8, 9, 18)},
    ("tensor", 6): "qml",
    **{("tensor", r): "world" for r in (2, 3, 5, 10, 13, 19, 20, 22, 23, 24, 25)},
}


def top_lists(rows: list[dict]) -> dict[str, list[dict]]:
    """The review's top lists, as discover_candidates.main cut them: per
    stream, in file order (already ranked), checked counts only, first TOP."""
    return {s: [c for c in rows if c["stream"] == s and c["citation_check"] != "unchecked"][:TOP] for s in STREAMS}


def chosen(top: dict[str, list[dict]]) -> list[tuple[str, int, dict]]:
    out = []
    for stream, rows in top.items():
        for rank, c in enumerate(rows, 1):
            start = OFF_TOPIC.get((stream, rank))
            if start is not None:
                if not c["title"].startswith(start):
                    raise ValueError(f"{stream} rank {rank} is {c['title']!r}, not the excluded {start!r}")
                continue
            out.append((stream, rank, c))
    return out


# Refused by the title check on 2026-10-15's first apply: each arXiv preprint
# carries a title other than the published paper's (nnU-Net's preprint is
# "Automated Design of Deep Learning Methods for Biomedical Image
# Segmentation"; qml 7's differs in spelling). Same works; these enter by the
# journal DOI, whose title the check then compares.
BY_DOI = {("ml", 20), ("qml", 7), ("qml", 18), ("tensor", 9), ("tensor", 20)}


def access_of(c: dict, by_doi: bool = False) -> str:
    arx = c.get("arxiv") or c.get("s2_arxiv")
    if by_doi and c.get("doi"):
        return f"DOI:{c['doi']}"
    if arx:
        return f"arXiv:{arx}"
    if c.get("doi"):
        return f"DOI:{c['doi']}"
    raise ValueError(f"{c['title']!r}: no identifier")


def entry_for(stream: str, rank: int, c: dict) -> dict:
    ctx = CONTEXT_BY_RANK.get((stream, rank), STREAM_DEFAULT[stream])
    return {
        "access": access_of(c, (stream, rank) in BY_DOI), "context": ctx, "tier": "seen",
        "disposition": (f"Bulk intake 2026-10 from F62 discovery, {stream} stream rank {rank} "
                        f"({c['rank_cites']} citations, {c['rank_year']}); not yet screened"),
        "found_via": f"F62 discovery review {TODAY} ({REVIEW_MD}), {stream} stream rank {rank}",
        "cited_as": c["title"],
        "updated_reason": f"{TODAY}: added by scripts/sprint9_f62_enter_seen.py ({TAG}; team lead Q4 = 1 at "
                          "Manual Validation)",
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    rows = json.loads(REVIEW.read_text(encoding="utf-8"))
    picks = chosen(top_lists(rows))
    conn = connect(DB_PATH)
    try:
        keys = disc.store_keys(conn)
    finally:
        conn.close()
    todo = []
    for stream, rank, c in picks:
        held = disc.held_by_store(c, keys)
        if held:
            print(f"held   {stream} {rank}: {c['title'][:70]} (by {held})")
            continue
        todo.append((stream, rank, c, entry_for(stream, rank, c)))
    print(f"{len(picks)} chosen; {len(todo)} to enter; "
          f"{sum(e['access'].startswith('arXiv') for *_, e in todo)} by arXiv (18 s apart)")
    if "--apply" not in args:
        for stream, rank, c, e in todo:
            print(f"plan   {stream} {rank} [{e['context']}] {e['access']}: {c['title'][:70]}")
        print("DRY RUN: nothing fetched or written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F62 discovery candidates at seen (MV Q4 = 1)")
    citations.assume_recent_arxiv_request()
    fetcher = citations.PacedFetcher()
    entered, refused = [], []
    for stream, rank, c, e in todo:
        try:
            paper = intake.build_record(e, fetcher=fetcher, today=TODAY)
        except Exception as exc:  # the door's refusal, or a fetch that failed
            refused.append(f"{stream} {rank}: {c['title'][:70]} -- door: {exc}")
            print(f"REFUSE {refused[-1]}", flush=True)
            continue
        if not disc.same_title(paper.value, c["title"]):
            refused.append(f"{stream} {rank}: {c['title'][:70]} -- {e['access']} resolves to {paper.value[:70]!r}")
            print(f"REFUSE {refused[-1]}", flush=True)
            continue
        conn = connect(DB_PATH)
        conn.execute("PRAGMA busy_timeout = 120000")
        try:
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (paper.id,)).fetchone():
                print(f"exists {paper.id}", flush=True)
                continue
            insert_paper(conn, paper)
            conn.commit()
        finally:
            conn.close()
        entered.append(paper.id)
        print(f"enter  {stream} {rank} [{e['context']}] {paper.id}", flush=True)
    print(f"\n{len(entered)} entered, {len(refused)} refused")
    for r in refused:
        print(f"  refused {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
