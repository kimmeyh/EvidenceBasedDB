#!/usr/bin/env python3
"""Sprint 9 Task G (F80): select the first read-for-claims slice.

Team lead, 2026-10-15 (plan Q7 = 2): the 26 records at `seen` or `screened`
under `hsbc-2026`, `platform:dirac-3` and `platform:dirac-3s` (none in the
ceiling group), plus the 50 most-cited `qml` records at `seen` or `screened`.
The store holds no citation counts, so they are fetched from OpenAlex:
batches of 50 identifiers per request (arXiv records by their DataCite DOI
10.48550/arXiv.<id>), the key only in the Authorization header
(`discover_candidates.request_for`), never logged. A record OpenAlex does
not know is reported with no count and is not ranked.

Writes `manifests/sprint9_f80_slice.json`: the selection, each record's count
and the date. That file records what this sprint chose; it is not a store
field (counts change, and the store never holds them). `--dry-run` lists
the slice-1 records and the number of qml candidates and sends nothing.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("dc", Path(__file__).with_name("discover_candidates.py"))
dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dc)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OUT = ROOT / "manifests" / "sprint9_f80_slice.json"
CONTEXTS = ("hsbc-2026", "platform:dirac-3", "platform:dirac-3s")
TOP_QML = 50
BATCH = 50


def slice_one(conn) -> list[str]:
    q = ("SELECT DISTINCT p.record_id FROM paper_fields p JOIN record_contexts x ON x.record_id = p.record_id "
         f"WHERE p.tier IN ('seen', 'screened') AND x.context_id IN ({','.join('?' * len(CONTEXTS))}) "
         "AND p.disposition NOT LIKE '%[CE-%' ORDER BY p.record_id")
    return [r[0] for r in conn.execute(q, CONTEXTS)]


def qml_candidates(conn, exclude: set[str]) -> dict[str, str]:
    """record id -> DOI (lower case) for every qml record at seen or screened
    with an arXiv id or a DOI."""
    out = {}
    for rid, access in conn.execute(
            "SELECT p.record_id, p.access FROM paper_fields p JOIN record_contexts x ON x.record_id = p.record_id "
            "WHERE x.context_id = 'qml' AND p.tier IN ('seen', 'screened') ORDER BY p.record_id"):
        if rid in exclude:
            continue
        parsed = citations.parse_access(access or "")
        if parsed and parsed[0] == "arxiv":
            out[rid] = f"10.48550/arxiv.{parsed[1]}".lower()
        elif parsed and parsed[0] == "doi":
            out[rid] = parsed[1].lower()
    return out


def fetch_counts(dois: list[str], key: str | None, opener=urllib.request.urlopen) -> dict[str, int]:
    counts = {}
    for i in range(0, len(dois), BATCH):
        chunk = dois[i:i + BATCH]
        params = {"filter": "doi:" + "|".join(chunk), "per-page": BATCH, "select": "doi,cited_by_count"}
        with opener(dc.request_for(params, key), timeout=60) as resp:
            for work in json.loads(resp.read())["results"]:
                doi = (work.get("doi") or "").lower().replace("https://doi.org/", "")
                counts[doi] = int(work.get("cited_by_count") or 0)
        time.sleep(1.0)  # OpenAlex asks for no more than 10 per second; one per second is ample
    return counts


S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=citationCount"


def fetch_s2_counts(arxiv_ids: list[str], opener=urllib.request.urlopen) -> dict[str, int]:
    """arXiv id -> citation count from Semantic Scholar's batch endpoint (no
    key; one request per second). OpenAlex knows only 627 of 1,521 records by
    their arXiv DOI (run of 2026-10-15), so the arXiv records it misses are
    counted here instead of being left out of the ranking."""
    counts = {}
    for i in range(0, len(arxiv_ids), 100):
        chunk = arxiv_ids[i:i + 100]
        body = json.dumps({"ids": [f"arXiv:{a}" for a in chunk]}).encode()
        req = urllib.request.Request(S2_BATCH, data=body, method="POST",
                                     headers={"User-Agent": "curl/8.0", "Content-Type": "application/json"})
        # The unauthenticated pool is shared and answers 429 under load
        # (2026-10-15: three in a row at 10 s); back off and grow the wait.
        for attempt in range(6):
            try:
                with opener(req, timeout=120) as resp:
                    rows = json.loads(resp.read())
                break
            except urllib.error.HTTPError as err:
                if err.code != 429 or attempt == 5:
                    raise
                time.sleep(15.0 * (attempt + 1))
        for ident, row in zip(chunk, rows):
            if row and row.get("citationCount") is not None:
                counts[ident] = int(row["citationCount"])
        time.sleep(1.5)
    return counts


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        first = slice_one(conn)
        cands = qml_candidates(conn, set(first))
    finally:
        conn.close()
    print(f"slice 1: {len(first)} records; qml candidates with an identifier: {len(cands)}")
    if "--dry-run" in args:
        return 0
    key = dc.openalex_key()
    counts = fetch_counts(sorted(set(cands.values())), key)
    found = {rid: (counts[d], "OpenAlex") for rid, d in cands.items() if d in counts}
    # Second pass: OpenAlex knows many arXiv papers only under their journal
    # DOI. The store's probes recorded that DOI (`version_of`) for 544
    # records; ask OpenAlex for those (2026-10-15: Semantic Scholar's
    # unauthenticated batch answered 429 to every attempt, so it is not used).
    conn = connect(DB_PATH)
    try:
        journal = {rid: v.lower() for rid, v in conn.execute(
            "SELECT record_id, value FROM paper_probes WHERE field = 'version_of'")
            if rid in cands and rid not in found and not v.lower().startswith("10.48550/")}
    finally:
        conn.close()
    second = fetch_counts(sorted(set(journal.values())), key)
    found.update({rid: (second[d], "OpenAlex (journal DOI)") for rid, d in journal.items() if d in second})
    s2 = {}
    ranked = sorted(((n, rid, src) for rid, (n, src) in found.items()), key=lambda t: (-t[0], t[1]))
    unknown = sorted(set(cands) - set(found))
    top = ranked[:TOP_QML]
    OUT.write_text(json.dumps({
        "selected_on": date.today().isoformat(),
        "rule": "plan Q7 = 2: slice 1 (consumer contexts) plus the 50 most-cited qml records at seen or screened",
        "slice_1": first,
        "slice_2": [{"record_id": rid, "cited_by_count": n, "source": src} for n, rid, src in top],
        "qml_candidates": len(cands), "counted": len(ranked),
        "counted_by": {src: sum(1 for *_, s in ranked if s == src)
                       for src in ("OpenAlex", "OpenAlex (journal DOI)")},
        "not_counted": len(unknown),
        "limit": ("records OpenAlex knows under neither their arXiv DOI nor a probed journal DOI are not ranked; "
                  "a highly cited one among them would be missed"),
    }, indent=1) + "\n", encoding="utf-8")
    print(f"counted {len(ranked)} of {len(cands)}; not counted {len(unknown)}; "
          f"top {len(top)} from {top[0][0]} to {top[-1][0]} citations")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
