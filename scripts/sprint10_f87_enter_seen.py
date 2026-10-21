#!/usr/bin/env python3
"""Sprint 10 Task J (F87), Manual Validation Q4 = 2 and Q6: the live
re-run's discovery candidates enter the store at `seen`.

Team lead, 2026-10-19, on the eight proposed exclusions: "do these better
fit in ml and can be switched there" (FCHL revisited; the alchemical
representation paper, both qml stream) "the others can be excluded - this
answers q6." So every candidate in the four top lists of
`f62_review_2026-10-19.md` enters, except the six named off-topic and the
two Sprint 9 exclusions the filters could not catch (OFF_TOPIC, each pinned
to its title so a re-ranked file cannot shift the cut). The two switched
papers enter under `ml`, not the qml stream's context.

The door, the access rule and the title check are Sprint 9's
(`sprint9_f62_enter_seen.py`): the door derives id, title and citation
from the identifier; a candidate whose door title is not its own is
REFUSED and listed, never entered; one the store now holds is skipped.
New here: the review file also saves the records the F87 filters dropped,
so the top lists skip them as `discover_candidates.main` did.

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
access_of = _load("sprint9_f62_enter_seen").access_of

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-19"
TAG = "Sprint 10 Task J, F87"
REVIEW = Path(r"D:\Data\Harold\EvidenceBasedDB\discovery\f62_review_2026-10-19.json")
REVIEW_MD = REVIEW.with_suffix(".md")
TOP = 25
STREAMS = ("ml", "qml", "tensor", "fraud")

# (stream, rank) -> the title's start. The first two are Sprint 9's Q4 = 1
# exclusions, back at the top because they were never entered; the rest are
# the team lead's Q6 exclusions.
OFF_TOPIC = {
    ("qml", 1): "A versatile single-photon-based", ("tensor", 1): "Complexity, action, and black holes",
    ("ml", 18): "QuPath", ("ml", 24): "Sensitivity and False Alarm Rate of a Fall Sensor",
    ("qml", 16): "The shift to 6G communications",
    ("tensor", 7): "A Compare-Aggregate Model", ("tensor", 11): "Logic Tensor Networks",
    ("tensor", 12): "Circuit complexity in fermionic field theory",
}
# Team lead's Q6: classical ML on molecules, switched from the qml stream to ml.
SWITCHED_TO_ML = {("qml", 17): "FCHL revisited", ("qml", 23): "Alchemical and structural distribution"}
STREAM_DEFAULT = {"ml": "ml", "qml": "qml", "tensor": "qc", "fraud": "ml"}
CONTEXT_BY_RANK = {
    **{k: "ml" for k in SWITCHED_TO_ML},
    # qml stream: quantum simulation, chemistry, solvers and platforms, not learning
    **{("qml", r): "qc" for r in (2, 4, 5, 7, 8, 12, 13, 14, 15, 18, 19, 20, 21, 22, 24)},
    # tensor stream: learning and decomposition methods (as Sprint 9), and physics
    **{("tensor", r): "ml" for r in (2, 3, 4, 8, 9, 13)},
    **{("tensor", r): "world" for r in (6, 10, 15, 16, 18, 20, 21, 22, 23, 24, 25)},
}


def top_lists(rows: list[dict]) -> dict[str, list[dict]]:
    """The review's top lists, as discover_candidates.main cut them: per
    stream, in file order (already ranked), checked counts only and not
    dropped as off-topic, first TOP."""
    return {s: [c for c in rows if c["stream"] == s and not c.get("dropped")
                and c.get("citation_check", "unchecked") != "unchecked"][:TOP] for s in STREAMS}


def _pinned(table: dict, stream: str, rank: int, c: dict) -> bool:
    start = table.get((stream, rank))
    if start is not None and not c["title"].startswith(start):
        raise ValueError(f"{stream} rank {rank} is {c['title']!r}, not the pinned {start!r}")
    return start is not None


def chosen(top: dict[str, list[dict]]) -> list[tuple[str, int, dict]]:
    out = []
    for stream, rows in top.items():
        for rank, c in enumerate(rows, 1):
            _pinned(SWITCHED_TO_ML, stream, rank, c)
            if not _pinned(OFF_TOPIC, stream, rank, c):
                out.append((stream, rank, c))
    return out


# Refused by the title check on 2026-10-19's first apply: each arXiv preprint
# carries a title other than the published paper's (qml 5's preprint is
# "Robust determination of molecular spectra on a quantum processor"; the
# TASI lectures' is "... the Emergence of the Bulk in AdS/CFT"). Same works;
# these enter by the journal DOI, whose title the check then compares.
BY_DOI = {("qml", 5), ("qml", 22), ("qml", 23), ("tensor", 19), ("tensor", 25)}


def entry_for(stream: str, rank: int, c: dict) -> dict:
    ctx = CONTEXT_BY_RANK.get((stream, rank), STREAM_DEFAULT[stream])
    moved = "; switched to ml by the team lead (Q6)" if (stream, rank) in SWITCHED_TO_ML else ""
    return {
        "access": access_of(c, (stream, rank) in BY_DOI), "context": ctx, "tier": "seen",
        "disposition": (f"Bulk intake 2026-10 from F87 discovery re-run, {stream} stream rank {rank}{moved} "
                        f"({c['rank_cites']} citations, {c['rank_year']}); not yet screened"),
        "found_via": f"F62 discovery review {TODAY} ({REVIEW_MD}), {stream} stream rank {rank}",
        "cited_as": c["title"],
        "updated_reason": f"{TODAY}: added by scripts/sprint10_f87_enter_seen.py ({TAG}; team lead Q4 = 2 and "
                          "Q6 at Manual Validation)",
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
    backup_before_write(DB_PATH, "F87 discovery re-run candidates at seen (MV Q4 = 2, Q6)")
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
