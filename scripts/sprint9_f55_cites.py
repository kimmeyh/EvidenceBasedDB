#!/usr/bin/env python3
"""Sprint 9 Task H (F55): `cites` links from Crossref reference lists
(ADR-0005 A10; team lead, plan Q5 = 1).

A `cites` link goes from the citing paper to the cited one, both in the
store. It is computed, never typed: each comes from one entry of the citing
paper's Crossref reference list, matched to a store record by DOI, or by an
arXiv id in an unstructured reference. The evidence names the list, the
date it was fetched and the entry that matched. Not a certainty input.

Which papers are asked: every DOI the store holds for a paper, from its
`access` field or from its `version_of` probe (the journal DOI an arXiv
record's probe found). arXiv's own DOIs (10.48550) are not asked: they are
DataCite's and carry no reference list. Which papers can be cited: the same
DOIs, plus arXiv's DOI and id for every arXiv record. Records that share
the citing DOI are versions of one paper and never link to each other.

Two steps:
  --fetch   serial Crossref requests, one per DOI, 1 s apart, with the
            plain User-Agent and no contact address; each answer is cached
            as JSON in <store dir>/crossref_references/ (outside git). A
            cached DOI is not asked again.
  (default) computes the links from the cache and prints the coverage.
  --apply   writes the links not yet stored (verified backup first).
Cached answers are the record of what Crossref said on the date fetched.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths, store_dir  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.citations import CROSSREF_API, _ARXIV_ID, _arxiv_ident, default_fetcher, parse_access  # noqa: E402
from store.ingest import add_source_link  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TAG = "Sprint 9 Task H, F55"
ARXIV_DOI_PREFIX = "10.48550/arxiv."
INTERVAL_S = 1.0


def cache_dir() -> Path:
    return store_dir() / "crossref_references"


def cache_file(doi: str, root: Path | None = None) -> Path:
    return (root or cache_dir()) / (urllib.parse.quote(doi, safe="") + ".json")


def store_identifiers(conn) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    """(citing: DOI -> records asked for it, by_doi: DOI -> records it names,
    by_arxiv: arXiv id -> records). DOIs lower-cased."""
    citing, by_doi, by_arxiv = defaultdict(set), defaultdict(set), defaultdict(set)
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields"):
        p = parse_access(access or "")
        if not p:
            continue
        if p[0] == "doi":
            doi = p[1].lower()
            by_doi[doi].add(rid)
            if not doi.startswith(ARXIV_DOI_PREFIX):
                citing[doi].add(rid)
        elif p[0] == "arxiv":
            by_arxiv[p[1]].add(rid)
            by_doi[ARXIV_DOI_PREFIX + p[1].lower()].add(rid)
    for rid, value in conn.execute("SELECT record_id, value FROM paper_probes WHERE field = 'version_of'"):
        doi = value.strip().lower()
        if doi.startswith("10."):
            by_doi[doi].add(rid)
            if not doi.startswith(ARXIV_DOI_PREFIX):
                citing[doi].add(rid)
    return dict(citing), dict(by_doi), dict(by_arxiv)


def fetch(dois: list[str], fetcher=default_fetcher, root: Path | None = None, today: str | None = None,
          sleep=time.sleep) -> dict[str, int]:
    """Ask Crossref for each uncached DOI, serially; cache every answer,
    a 404 included. Returns {"asked", "cached", "failed"}; a failure
    (anything but 200 or 404) is not cached, so a later run asks again."""
    root = root or cache_dir()
    root.mkdir(parents=True, exist_ok=True)
    today = today or date.today().isoformat()
    counts = {"asked": 0, "cached": 0, "failed": 0}
    for i, doi in enumerate(dois):
        path = cache_file(doi, root)
        if path.exists():
            counts["cached"] += 1
            continue
        if counts["asked"]:
            sleep(INTERVAL_S)
        counts["asked"] += 1
        try:
            body = json.loads(fetcher(CROSSREF_API + urllib.parse.quote(doi, safe="/()"), "application/json"))
            entry = {"doi": doi, "fetched_on": today, "status": 200,
                     "reference_count": body["message"].get("reference-count", 0),
                     "reference": body["message"].get("reference", [])}
        except urllib.error.HTTPError as err:
            if err.code != 404:
                counts["failed"] += 1
                print(f"  failed {doi}: HTTP {err.code}")
                continue
            entry = {"doi": doi, "fetched_on": today, "status": 404, "reference_count": 0, "reference": []}
        except (OSError, ValueError, KeyError) as err:
            counts["failed"] += 1
            print(f"  failed {doi}: {type(err).__name__}")
            continue
        path.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
        if (i + 1) % 50 == 0:
            print(f"  {i + 1} of {len(dois)}")
    return counts


def _match(ref: dict, by_doi: dict[str, set[str]], by_arxiv: dict[str, set[str]]) -> tuple[set[str], str]:
    """(store records this reference names, how it names them)."""
    doi = (ref.get("DOI") or "").strip().lower()
    if doi:
        return by_doi.get(doi, set()), f"DOI {doi}"
    text = " ".join(str(ref.get(k, "")) for k in ("unstructured", "journal-title", "volume-title"))
    if "arxiv" in text.lower():
        for m in _ARXIV_ID.finditer(text):
            ident = _arxiv_ident(m)[0]
            if ident in by_arxiv:
                return by_arxiv[ident], f"arXiv:{ident} in an unstructured reference"
    return set(), ""


def compute_links(citing: dict[str, set[str]], by_doi: dict[str, set[str]], by_arxiv: dict[str, set[str]],
                  root: Path | None = None) -> tuple[dict[tuple[str, str], str], dict[str, int]]:
    """({(from, to): evidence}, coverage counts) from the cached answers."""
    root = root or cache_dir()
    links: dict[tuple[str, str], str] = {}
    cov = {"dois_asked": len(citing), "answered": 0, "not_found": 0, "with_list": 0, "references": 0,
           "references_with_doi": 0, "references_matched": 0}
    for doi in sorted(citing):
        path = cache_file(doi, root)
        if not path.exists():
            continue
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry["status"] == 404:
            cov["not_found"] += 1
            continue
        cov["answered"] += 1
        refs = entry["reference"]
        if refs:
            cov["with_list"] += 1
        cov["references"] += len(refs)
        sources = citing[doi]
        for ref in refs:
            cov["references_with_doi"] += bool(ref.get("DOI"))
            targets, how = _match(ref, by_doi, by_arxiv)
            targets = targets - sources
            if targets:
                cov["references_matched"] += 1
            for src in sorted(sources):
                for dst in sorted(targets):
                    links.setdefault((src, dst), (
                        f"Crossref reference list of DOI {doi} (works API, fetched {entry['fetched_on']}) "
                        f"names {how} ({TAG})"))
    cov["links"] = len(links)
    cov["citing_records"] = len({s for s, _ in links})
    cov["cited_records"] = len({d for _, d in links})
    return links, cov


def apply_links(conn, links: dict[tuple[str, str], str]) -> list[str]:
    have = {(f, t) for f, t in conn.execute("SELECT from_id, to_id FROM source_links WHERE link_type = 'cites'")}
    log = []
    for (src, dst), evidence in sorted(links.items()):
        if (src, dst) in have:
            continue
        add_source_link(conn, src, dst, "cites", evidence)
        log.append(f"cites {src} -> {dst}")
    stale = sorted(have - set(links))
    if stale:
        log.append(f"{len(stale)} stored cites links not recomputed from the cache (left in place): {stale[:5]}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        citing, by_doi, by_arxiv = store_identifiers(conn)
        papers = conn.execute("SELECT count(*) FROM paper_fields").fetchone()[0]
        if "--fetch" in args:
            print(f"asking Crossref for {len(citing)} DOIs, {INTERVAL_S:.0f} s apart")
            print(fetch(sorted(citing)))
        links, cov = compute_links(citing, by_doi, by_arxiv)
        touched = {s for s, _ in links} | {d for _, d in links}
        print(f"coverage (snapshot, {date.today().isoformat()}): {cov}; papers in the store {papers}; "
              f"papers at either end of a link {len(touched)}")
        if "--apply" not in args:
            print("DRY RUN: nothing written. Re-run with --apply.")
            return 0
    finally:
        conn.close()
    backup_before_write(DB_PATH, "F55 cites links from Crossref reference lists")
    conn = connect(DB_PATH)
    try:
        log = apply_links(conn, links)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log[-20:]))
    print(f"{sum(line.startswith('cites ') for line in log)} links written. APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
