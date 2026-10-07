#!/usr/bin/env python3
"""Find candidate papers worth evaluating, from OpenAlex metadata (F62
pilot, Sprint 7, team lead 2026-10-06, Q11 = 1 and 3).

READ-ONLY with respect to the store: it reads the store to drop papers we
already hold, and writes a report OUTSIDE the repository. Nothing enters
the store from here; a chosen paper goes through the door (scripts/intake.py)
by its DOI.

Streams (team lead: "the best of Machine Learning (ML) even if it is
unrelated to Quantum Computing and Credit Card Fraud and Fraud", and
"... and tensors"):
- ml: the most-cited works in OpenAlex's Artificial Intelligence and
  Computer Vision subfields since 2012
- qml, tensor, fraud: title-and-abstract searches

Each candidate carries what an evaluator needs and what the hand-download
list needs: abstract (OpenAlex), citations per year, open access status and
the free copy's URL, an arXiv id when OpenAlex knows one, the DOI and the
publisher. The rank is citations per year since publication, COMPUTED on
every run and never stored.

The OpenAlex key is read from OPENALEX_API_KEY (the process, then the
Windows user scope) and sent ONLY in the Authorization header, never in a
URL, so it cannot reach a log line or an exception message. Without a key
the run uses OpenAlex's keyless budget (about 100 searches a day; this run
spends one search per stream plus free filter calls).

    python scripts/discover_candidates.py --per-stream 25 --out <folder outside the repository>
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import script_paths  # noqa: E402
from store.export import REPO_ROOT  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OPENALEX = "https://api.openalex.org/works"
SELECT = ("id,doi,title,publication_year,cited_by_count,open_access,abstract_inverted_index,"
          "primary_location,locations,primary_topic,type")
STREAMS = {
    "ml": {"filter": "primary_topic.subfield.id:1702|1707,from_publication_date:2012-01-01,type:article|preprint",
           "sort": "cited_by_count:desc"},
    # The title-and-abstract FILTER, not `search`: the pilot's first run
    # (2026-10-06) used `search`, which matched a sentiment-analysis survey
    # for QML, YOLO for tensor networks and XGBoost for fraud.
    "qml": {"filter": 'title_and_abstract.search:"quantum machine learning"|"quantum neural network"|'
                      '"variational quantum"|"quantum kernel"', "sort": "cited_by_count:desc"},
    "tensor": {"filter": 'title_and_abstract.search:"tensor network"|"tensor networks"', "sort": "cited_by_count:desc"},
    # Fraud in the TITLE, an ML term in the abstract: with fraud anywhere in
    # the abstract, general surveys that name fraud as one example led.
    "fraud": {"filter": 'title.search:fraud,title_and_abstract.search:"machine learning"|"deep learning"|'
                        '"neural network"|"anomaly detection"', "sort": "cited_by_count:desc"},
}
_ARXIV_URL = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.IGNORECASE)
_ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})")


def openalex_key() -> str | None:
    """The key from the process environment, then (Windows) the user's
    persistent environment, so a key set with SetEnvironmentVariable(...,
    'User') works without restarting the shell. Never printed."""
    value = (os.environ.get("OPENALEX_API_KEY") or "").strip()
    if not value and os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                value = str(winreg.QueryValueEx(k, "OPENALEX_API_KEY")[0]).strip()
        except OSError:
            value = ""
    return value or None


def request_for(params: dict, key: str | None) -> urllib.request.Request:
    url = OPENALEX + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "curl/8.0", "Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"  # the header only: never in the URL
    return urllib.request.Request(url, headers=headers)


def abstract_text(inverted: dict | None) -> str:
    if not inverted:
        return ""
    words = sorted((pos, word) for word, positions in inverted.items() for pos in positions)
    return " ".join(word for _, word in words)


def norm_title(title: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_.lower())


def arxiv_of(work: dict) -> str | None:
    for loc in work.get("locations") or []:
        for url in (loc.get("landing_page_url") or "", loc.get("pdf_url") or ""):
            m = _ARXIV_URL.search(url)
            if m:
                return m.group(1)
    doi = (work.get("doi") or "").lower()
    if "10.48550/arxiv." in doi:
        return doi.rsplit("arxiv.", 1)[1]
    return None


def candidate(work: dict, stream: str, today: date) -> dict:
    year = work.get("publication_year") or today.year
    cites = work.get("cited_by_count") or 0
    oa = work.get("open_access") or {}
    src = ((work.get("primary_location") or {}).get("source") or {})
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    return {
        "stream": stream, "title": " ".join((work.get("title") or "").split()), "year": year,
        "doi": doi or None, "arxiv": arxiv_of(work), "openalex": work.get("id"),
        "venue": src.get("display_name"), "publisher": src.get("host_organization_name"),
        "cited_by": cites, "cites_per_year": round(cites / max(1, today.year - year + 1), 1),
        "oa_status": oa.get("oa_status"), "oa_url": oa.get("oa_url"),
        "topic": ((work.get("primary_topic") or {}).get("display_name")),
        "abstract": abstract_text(work.get("abstract_inverted_index")),
    }


def store_keys(conn) -> tuple[set, set, set]:
    """(DOIs, arXiv ids, normalized titles) the store already holds."""
    dois, arxivs = set(), set()
    for (access,) in conn.execute("SELECT access FROM paper_fields"):
        access = access or ""
        dois.update(d.lower().rstrip(".") for d in re.findall(r"10\.\d{4,9}/[^\s|]+", access))
        arxivs.update(_ARXIV_ID.findall(access) if "arxiv" in access.lower() else [])
    for (value,) in conn.execute("SELECT value FROM paper_probes WHERE field = 'version_of'"):
        dois.add(value.lower())
    titles = {norm_title(t) for (t,) in conn.execute("SELECT value FROM records WHERE class = 'paper'")}
    return dois, arxivs, titles


def held_by_store(c: dict, keys: tuple[set, set, set]) -> str | None:
    """Why the store already holds this candidate, or None."""
    dois, arxivs, titles = keys
    if c["doi"] and c["doi"].lower() in dois:
        return "doi"
    if c["arxiv"] and c["arxiv"] in arxivs:
        return "arxiv"
    if c["title"] and norm_title(c["title"]) in titles:
        return "title"
    return None


def fetch_stream(stream: str, per: int, key: str | None, opener=urllib.request.urlopen) -> list[dict]:
    spec = STREAMS[stream]
    params = {"per_page": per, "select": SELECT, "sort": spec["sort"]}
    if "filter" in spec:
        params["filter"] = spec["filter"]
    if "search" in spec:
        params["search"] = spec["search"]
    with opener(request_for(params, key), timeout=60) as resp:
        return json.loads(resp.read())["results"]


def render(cands: list[dict], counts: dict, today: date) -> str:
    lines = [f"# F62 discovery pilot, {today.isoformat()}", "",
             "Read-only pilot (Sprint 7, team lead Q11 = 1 and 3). Every count is a snapshot as of this date. "
             "Rank = citations per year since publication, computed, never stored. Nothing here is in the store.", ""]
    for stream, c in counts.items():
        lines.append(f"- **{stream}**: {c['fetched']} fetched; {c['held']} already in the store "
                     f"({c['held_by']}); {c['new']} new; abstract present on {c['abstract']} of {c['fetched']}; "
                     f"free copy on {c['free']} of {c['new']} new")
    for stream in counts:
        lines += ["", f"## {stream}", ""]
        rows = [c for c in cands if c["stream"] == stream and not c["held"]]
        for i, c in enumerate(sorted(rows, key=lambda r: -r["cites_per_year"]), 1):
            where = c["arxiv"] and f"arXiv:{c['arxiv']}" or c["oa_url"] or "NO FREE COPY: by hand"
            lines.append(f"{i}. **{c['title']}** ({c['year']}; {c['venue'] or 'venue unknown'}). "
                         f"{c['cites_per_year']}/yr, {c['cited_by']} citations. DOI {c['doi'] or 'none'}. "
                         f"Copy: {where}. Abstract: {'yes' if c['abstract'] else 'NO'}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    per = int(args[args.index("--per-stream") + 1]) if "--per-stream" in args else 25
    if "--out" not in args:
        print("error: --out <folder outside the repository> is required", file=sys.stderr)
        return 2
    out = Path(args[args.index("--out") + 1]).resolve()
    if out == REPO_ROOT or REPO_ROOT in out.parents:
        print(f"error: refusing to write inside the repository ({out})", file=sys.stderr)
        return 2
    key = openalex_key()
    print(f"OpenAlex key present: {key is not None}")
    today = date.today()
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        keys = store_keys(conn)
    finally:
        conn.close()
    cands, counts = [], {}
    for stream in STREAMS:
        works = fetch_stream(stream, per, key)
        rows = [candidate(w, stream, today) for w in works]
        held = [held_by_store(c, keys) for c in rows]
        for c, h in zip(rows, held):
            c["held"] = h
        new = [c for c in rows if not c["held"]]
        counts[stream] = {"fetched": len(rows), "held": sum(1 for h in held if h),
                          "held_by": ", ".join(f"{k} {v}" for k, v in sorted(
                              {k: held.count(k) for k in set(held) if k}.items())) or "none",
                          "new": len(new), "abstract": sum(1 for c in rows if c["abstract"]),
                          "free": sum(1 for c in new if c["arxiv"] or c["oa_url"])}
        cands += rows
        print(f"{stream}: {counts[stream]}")
    out.mkdir(parents=True, exist_ok=True)
    stem = f"f62_pilot_{today.isoformat()}"
    (out / f"{stem}.json").write_text(json.dumps(cands, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / f"{stem}.md").write_text(render(cands, counts, today), encoding="utf-8")
    print(f"wrote {out / (stem + '.md')} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
