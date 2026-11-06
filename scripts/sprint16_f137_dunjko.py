#!/usr/bin/env python3
"""Sprint 16 Task E (F137): the two Dunjko records are one paper, held as one record (team lead, Q6 = 1, 2026-11-06).

dunjko-2017 is arXiv 1709.02779; dunjko-2018 is its journal version (DOI 10.1088/1361-6633/aab406, Reports on
Progress in Physics 81(7), 2018). Their local copies are one byte-identical PDF (SHA-256 7aa572f736a826a0...). So:

- dunjko-2018 keeps the paper and adds `arXiv:1709.02779` to its access, after its DOI (the DOI still resolves
  its citation: `citations.parse_access` takes a DOI first);
- each of dunjko-2017's assertions moves to dunjko-2018: its yield row, and its provenance's record id (the anchor
  and the pages are the same PDF's), each with a note in its updated_reason;
- each of dunjko-2017's found-via routes is copied to dunjko-2018 (a list that linked arXiv 1709.02779 found the
  paper dunjko-2018 now holds by that id);
- dunjko-2017 is closed as a duplicate: tier `seen` (as the Lin duplicate, F33), a disposition that names
  dunjko-2018, and a `superseded-by` source link. Its reads, applicability and found-via rows stay as its history.

`store.merges` names the merge, so the appliers that re-enter older reads (`scripts/full_read_apply.py` for g131,
`scripts/sprint11_reading.py` for task G) enter dunjko-2017's rows under dunjko-2018 and never promote it again.

    python scripts/sprint16_f137_dunjko.py           # dry run: what would change
    python scripts/sprint16_f137_dunjko.py --apply   # verified backup first
"""
from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_found_via, add_source_link, append_updated_reason, set_tier  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OLD = "dunjko-2017-machine-learning-artificial-intelligence-quantum"
NEW = "dunjko-2018-machine-learning-amp-artificial-intelligence"
ARXIV = "arXiv:1709.02779"
TAG = "Sprint 16 Task E, F137, team lead Q6 = 1"


def same_pdf(conn) -> str:
    """Both records' local copies hash the same, or the merge is refused (the plan's falsifier (d))."""
    hashes = set()
    for rid in (OLD, NEW):
        access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
        paths = recheck.local_paths(access)
        if not paths:
            raise ValueError(f"{rid}: no local copy to compare")
        hashes.add(hashlib.sha256(Path(paths[0]).read_bytes()).hexdigest())
    if len(hashes) != 1:
        raise ValueError(f"the two local copies differ ({sorted(h[:12] for h in hashes)}); ask Q6 again")
    return hashes.pop()


def merge(conn, today: str) -> list[str]:
    sha = same_pdf(conn)
    log = []
    access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (NEW,)).fetchone()[0]
    if ARXIV not in access:
        doi, sep, rest = access.partition(" | ")
        conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (f"{doi} | {ARXIV}{sep}{rest}", NEW))
        append_updated_reason(conn, NEW, f"{today} ({TAG}): {ARXIV} added to access; the preprint record {OLD} "
                              "is closed as its duplicate (one byte-identical PDF)", today)
        log.append(f"access {NEW} + {ARXIV}")
    moved = [r[0] for r in conn.execute("SELECT assertion_id FROM paper_yields WHERE paper_id = ? ORDER BY 1",
                                        (OLD,))]
    for aid in moved:
        prov = conn.execute("SELECT provenance FROM records WHERE id = ?", (aid,)).fetchone()[0] or ""
        if not prov.startswith(f"{OLD}, "):
            raise ValueError(f"{aid}: provenance {prov[:80]!r} does not name {OLD}")
        conn.execute("UPDATE paper_yields SET paper_id = ? WHERE paper_id = ? AND assertion_id = ?", (NEW, OLD, aid))
        conn.execute("UPDATE records SET provenance = ? WHERE id = ?", (NEW + prov[len(OLD):], aid))
        append_updated_reason(conn, aid, f"{today} ({TAG}): moved from {OLD}, the arXiv preprint, to {NEW}, its "
                              f"journal version (one paper, one PDF, SHA-256 {sha[:16]}); quotes, anchor and value "
                              "unchanged", today)
        log.append(f"moved  {aid}")
    have = {r[0] for r in conn.execute("SELECT route FROM paper_found_via WHERE record_id = ?", (NEW,))}
    for route, cited_as in conn.execute("SELECT route, cited_as FROM paper_found_via WHERE record_id = ? ORDER BY 1",
                                        (OLD,)).fetchall():
        if route not in have:  # the route found this paper by its arXiv id, which NEW's access now holds
            add_found_via(conn, NEW, route, cited_as)
            append_updated_reason(conn, NEW, f"{today} ({TAG}): found-via route {route!r} copied from {OLD}, the "
                                  "preprint record of this paper", today)
            log.append(f"route  {NEW} + {route[:60]}")
    stray = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'assertion' AND provenance LIKE ?",
                         (f"{OLD},%",)).fetchone()[0]
    if stray:  # an assertion that names OLD with no yield row would otherwise stay behind unseen
        raise ValueError(f"{stray} assertion(s) still name {OLD} in their provenance after the move")
    tier, disposition = conn.execute("SELECT tier, disposition FROM paper_fields WHERE record_id = ?",
                                     (OLD,)).fetchone()
    if tier != "seen" or not (disposition or "").startswith(f"Duplicate of {NEW}"):
        set_tier(conn, OLD, "seen")
        disposition = (f"Duplicate of {NEW}: the arXiv preprint (1709.02779) of the same paper, one PDF; its "
                       f"assertions moved there ({TAG}, {today})")
        conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (disposition, OLD))
        append_updated_reason(conn, OLD, f"{today} ({TAG}): closed as a duplicate of {NEW}; {len(moved)} "
                              "assertions moved there; tier set to seen", today)
        log.append(f"closed {OLD} -> seen")
    if not conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = 'superseded-by'",
                        (OLD, NEW)).fetchone():
        add_source_link(conn, OLD, NEW, "superseded-by",
                        f"one paper: arXiv 1709.02779 and DOI 10.1088/1361-6633/aab406 (Crossref: Reports on Progress "
                        f"in Physics 81(7), 2018, same authors and title); local copies byte-identical, SHA-256 "
                        f"{sha[:16]} ({TAG})")
        log.append(f"link   {OLD} superseded-by {NEW}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    today = date.today().isoformat()
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F137 Dunjko records merged")
    conn = connect(DB_PATH)
    try:
        log = merge(conn, today)
        if apply:
            conn.commit()
        else:
            conn.rollback()
    finally:
        conn.close()
    print("\n".join(log) or "nothing to change")
    moved = sum(1 for x in log if x.startswith("moved"))
    print(f"{moved} assertions moved; {'APPLIED' if apply else 'DRY RUN: nothing written. Re-run with --apply.'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
