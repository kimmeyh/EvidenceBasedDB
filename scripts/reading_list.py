#!/usr/bin/env python3
"""F114's one reading list (Sprint 19 Task D, F57 folded in; team lead q5 = b, q6 = a, q7 = a, 2026-11-25).

Every paper in F114's ledger not yet read in full, one line each: its group, contexts, citation count, what it
needs and where its copy is. Computed from the ledger and the store each time, so it is never kept by hand.

Order (q5 = b): F114's steps 1 to 3 first (new PDFs in `Papers\\`, new papers on Christophe Pere's list, papers the
team lead names; the `first` list of the ranking manifest, in its order), then F57's ranking across the whole list:
context (`hsbc-2026`, the Dirac platforms, `qml`, `qc`, `ml`, `world`, `method`), then the OpenAlex citation count
(most cited first; a paper with no count after every counted one), then the record id.

The counts are fetched once (`rank --write`) and saved in `manifests/sprint19_reading_ranking.json`, never in the
store. OpenAlex is asked first, in batches of 50 DOIs (an arXiv id as its DataCite DOI, 10.48550/arxiv.<id>), its key
in the request header only. An arXiv paper OpenAlex does not count is asked of Semantic Scholar's batch endpoint, as
`scripts/sprint9_f80_slice.py` did in Sprint 9 (OpenAlex then knew only 627 of 1,521 arXiv records). A paper neither
counts keeps `null`: no count is not a count of 0.

Usage:
  python scripts/reading_list.py [--top N]        the ranked list (read only: the store is opened read only)
  python scripts/reading_list.py rank [--write]   fetch the counts; --write saves the ranking manifest
  python scripts/reading_list.py check            the list's problems (a paper twice, a readable paper missing)

Read-only on the store. It never fetches a paper: copies are `scripts/sprint10_f89_downloads.py`'s.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import citations, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
RANKING = ROOT / "manifests" / "sprint19_reading_ranking.json"
UA = "EvidenceBasedDB-fetcher/1.0"
OPENALEX = "https://api.openalex.org/works"
S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=citationCount"
BATCH = 50
CONTEXT_ORDER = ("hsbc-2026", "platform:dirac", "qml", "qc", "ml", "world", "method")
GROUP = re.compile(r", group (g\d+(?:-r\d+)?)\)")  # full_read_apply.read_detail ends its tag with the group

# Paper records that are not read, each with its reason. A reason is required (an exclusion always says why).
NOT_TO_READ = {
    "freericks-2026-quantum-mechanics-done-right-book": "a book (F138, HOLD)",
    "schuld-2018-supervised-learning-quantum-computers": "a book (F138, HOLD)",
    "cichocki-2016-tensor-networks-dimensionality-reduction-large": "a book (F138, HOLD); ledger g382",
    "li-2020-quantum-deep-convolutional-neural-network": "F90 (HOLD): no free copy",
    "narayanan-2000-quantum-artificial-neural-network-architectures": "F90 (HOLD): no free copy",
    "aimeur-2006-machine-learning-quantum-world": "F90 (HOLD): no free copy",
    "ruan-2017-quantum-algorithm-k-nearest-neighbors": "F90 (HOLD): no free copy",
    "aimeur-2007-quantum-clustering-algorithms": "F90 (HOLD): no free copy",
    "duan-2020-survey-hhl-algorithm-theory-application": "F90 (HOLD): no free copy",
    "panella-2011-neural-networks-quantum-architecture-quantum": "F90 (HOLD): no free copy",
}


def read_only(db_path: Path = DB_PATH) -> sqlite3.Connection:
    if not Path(db_path).exists():
        raise FileNotFoundError(f"{db_path}: no store")
    return sqlite3.connect(f"{Path(db_path).as_uri()}?mode=ro", uri=True)


def ledger_groups(L: dict) -> dict[str, list[dict]]:
    """group -> its records, superseded groups left out (q20's split moved their records to one-paper groups)."""
    return {g: v.get("records", []) for g, v in L["groups"].items() if not v.get("superseded")}


def dead(disposition: str, title: str) -> bool:
    """Withdrawn or retracted: the store keeps the record so it is never cited as live evidence; a read buys nothing
    (`scripts/batch_read.py` `candidates`)."""
    return (disposition or "").startswith(("Withdrawn", "Retracted")) or (title or "").upper().startswith("RETRACTED")


def papers(conn) -> dict[str, dict]:
    """record id -> {access, tier, title, disposition, reads (set of extents), contexts}."""
    out = {rid: {"access": a or "", "tier": t, "title": v or "", "disposition": d or "", "reads": set(),
                 "groups_read": set(), "contexts": []}
           for rid, a, t, v, d in conn.execute(
               "SELECT f.record_id, f.access, f.tier, r.value, f.disposition FROM paper_fields f "
               "JOIN records r ON r.id = f.record_id")}
    for rid, extent, detail in conn.execute("SELECT record_id, extent, detail FROM paper_reads"):
        if rid in out:
            out[rid]["reads"].add(extent)
            if m := GROUP.search(detail or ""):
                out[rid]["groups_read"].add(m[1])
    for rid, ctx in conn.execute("SELECT record_id, context_id FROM record_contexts ORDER BY context_id"):
        if rid in out:
            out[rid]["contexts"].append(ctx)
    return out


def repository(p: dict) -> bool:
    a = p["access"].lower()
    return "github.com" in a and not any(x.strip().endswith(".pdf") for x in a.split("|"))


def readable(rid: str, p: dict) -> str | None:
    """None when the paper is one to read in full; else why not."""
    if "full" in p["reads"]:
        return "read in full"
    if repository(p):
        return "a GitHub repository"
    if dead(p["disposition"], p["title"]):
        return "withdrawn or retracted"
    if rid in NOT_TO_READ:
        return NOT_TO_READ[rid]
    return None


def to_add(P: dict[str, dict], held: set[str]) -> dict[str, list[str]]:
    """The readable papers no ledger group holds, by why (Sprint 19 Task D step 1, q1 and the team lead's "Add the
    306 to F114 list"): `never read` (no read row; F57's), and `read in part` (a read row, no full read: Sprints 9 to
    12, before the 2026-10-25 full-read rule; 3 of the planned 306 are GitHub repositories and are left out). A paper with neither an arXiv id, a DOI nor a local copy is left out:
    no copy can be found for it, and it is named by `check`."""
    out = {"never read": [], "read in part": []}
    for rid in sorted(P):
        p = P[rid]
        if rid in held or readable(rid, p):
            continue
        if not p["reads"]:
            if citations.parse_access(p["access"]) or local_copy(p["access"]):
                out["never read"].append(rid)
        else:  # a read row and no full read: 303 at `read`, and 2 at `seen` read by a subagent (2026-11-25)
            out["read in part"].append(rid)
    return out


def local_copy(access: str) -> str:
    """The first local file in `access`: a PDF first, then a saved page or any other text file
    (`store.quotes.source_text` reads each; the QCi site's pages and the HSBC submission's documents are such files)."""
    local = [x.strip() for x in (access or "").split("|") if re.match(r"[A-Za-z]:\\", x.strip())
             and Path(x.strip()).is_file()]
    if local:
        return next((x for x in local if x.lower().endswith(".pdf")), local[0])
    # A copy `access` does not name yet, found by its arXiv id (`store.recheck.local_pdf`, the fetcher's own
    # check): never fetched again (team lead, 2026-10-28). nguyen-2025 and huang-2025 are in QMLPapers\ so.
    from store import recheck
    parsed = citations.parse_access(access or "")
    return str(recheck.local_pdf(access or "", parsed[1]) or "") if parsed and parsed[0] == "arxiv" else ""


def doi_of(access: str) -> str | None:
    parsed = citations.parse_access(access or "")
    if not parsed:
        return None
    return f"10.48550/arxiv.{parsed[1]}".lower() if parsed[0] == "arxiv" else parsed[1].lower()


def arxiv_of(access: str) -> str | None:
    parsed = citations.parse_access(access or "")
    return parsed[1] if parsed and parsed[0] == "arxiv" else None


def context_rank(contexts: list[str]) -> int:
    ranks = [i for c in contexts for i, k in enumerate(CONTEXT_ORDER) if c == k or c.startswith(k + "-")]
    return min(ranks, default=len(CONTEXT_ORDER))


def needs(rid: str, p: dict, group: str, read_files: set[str]) -> str:
    """`read, not applied`: its group's reader file is written and the store holds no read of it that names the
    group (`scripts/sprint13_g_status.py`'s `applied`); F144's g335 to g347 among them."""
    if group in read_files and group not in p.get("groups_read", set()):
        return "read, not applied"
    return "read in part" if p["reads"] else "never read"


def copy_of(p: dict) -> str:
    local = local_copy(p["access"])
    if local:
        return f"local: {local}"
    if arxiv_of(p["access"]):
        return "arXiv: fetch"
    if doi_of(p["access"]):
        return "DOI: free copy if OpenAlex knows one, else hand download"
    return "none"


def group_read_files() -> set[str]:
    """Groups with a reader file not yet applied are named by `needs` only while a paper has no full read."""
    dirs = (ROOT / "manifests" / "sprint13_g_reads", Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local\reads"))
    return {f.stem.removeprefix("group_") for d in dirs if d.is_dir() for f in d.glob("group_g*.json")}


def rows(L: dict, P: dict[str, dict], ranking: dict | None = None, read_files: set[str] = frozenset()) -> list[dict]:
    """The ranked list: every ledger paper still to be read in full."""
    ranking = ranking or {}
    counts = ranking.get("counts", {})
    first = {rid: i for i, rid in enumerate(ranking.get("first", []))}
    out = []
    for g, recs in ledger_groups(L).items():
        for r in recs:
            rid = r["record_id"]
            p = P.get(rid)
            if p is None or readable(rid, p):
                continue
            c = counts.get(rid, {}).get("cited_by_count")
            out.append({"record_id": rid, "group": g, "contexts": p["contexts"], "cited_by_count": c,
                        "needs": needs(rid, p, g, read_files), "copy": copy_of(p)})
    return sorted(out, key=lambda x: (first.get(x["record_id"], len(first)), context_rank(x["contexts"]),
                                      x["cited_by_count"] is None, -(x["cited_by_count"] or 0), x["record_id"]))


def problems(L: dict, P: dict[str, dict], listed: list[dict]) -> list[str]:
    """A paper twice in the ledger's live groups or in the list; a readable paper the list leaves out."""
    out = []
    seen: dict[str, str] = {}
    for g, recs in ledger_groups(L).items():
        for r in recs:
            if r["record_id"] in seen:
                out.append(f"{r['record_id']}: in two ledger groups ({seen[r['record_id']]}, {g})")
            seen[r["record_id"]] = g
    ids = [x["record_id"] for x in listed]
    out += [f"{rid}: twice in the list" for rid in sorted({i for i in ids if ids.count(i) > 1})]
    missing = sorted(rid for rid, p in P.items() if not readable(rid, p) and rid not in set(ids))
    out += [f"{rid}: a paper to read in full, missing from the list" for rid in missing]
    return out


def _get(req, opener, tries: int = 6):
    for attempt in range(tries):
        try:
            with opener(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as err:
            if err.code != 429 or attempt == tries - 1:
                raise
            time.sleep(15.0 * (attempt + 1))


def openalex_counts(dois: list[str], key: str | None, opener=urllib.request.urlopen) -> dict[str, int]:
    out = {}
    for i in range(0, len(dois), BATCH):
        params = {"filter": "doi:" + "|".join(dois[i:i + BATCH]), "per-page": BATCH, "select": "doi,cited_by_count"}
        headers = {"User-Agent": UA, "Accept": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"  # the header only: never in the URL
        data = _get(urllib.request.Request(OPENALEX + "?" + urllib.parse.urlencode(params), headers=headers), opener)
        for work in data["results"]:
            doi = (work.get("doi") or "").lower().replace("https://doi.org/", "")
            out[doi] = int(work.get("cited_by_count") or 0)
        time.sleep(1.0)
    return out


def s2_counts(arxiv_ids: list[str], opener=urllib.request.urlopen) -> dict[str, int]:
    out = {}
    for i in range(0, len(arxiv_ids), 100):
        chunk = arxiv_ids[i:i + 100]
        req = urllib.request.Request(S2_BATCH, data=json.dumps({"ids": [f"arXiv:{a}" for a in chunk]}).encode(),
                                     method="POST", headers={"User-Agent": UA, "Content-Type": "application/json"})
        for ident, row in zip(chunk, _get(req, opener)):
            if row and row.get("citationCount") is not None:
                out[ident] = int(row["citationCount"])
        time.sleep(1.0)
    return out


def rank(args: list[str]) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from discover_candidates import openalex_key
    L = json.loads(LEDGER.read_text(encoding="utf-8"))
    with read_only() as conn:
        P = papers(conn)
    listed = rows(L, P)
    dois = {x["record_id"]: doi_of(P[x["record_id"]]["access"]) for x in listed}
    oa = openalex_counts(sorted({d for d in dois.values() if d}), openalex_key())
    arx = {rid: arxiv_of(P[rid]["access"]) for rid in dois}
    missed = sorted({a for rid, a in arx.items() if a and dois[rid] not in oa})
    s2 = s2_counts(missed) if missed else {}
    counts = {}
    for rid, d in dois.items():
        if d and d in oa:
            counts[rid] = {"cited_by_count": oa[d], "source": "openalex"}
        elif arx[rid] and arx[rid] in s2:
            counts[rid] = {"cited_by_count": s2[arx[rid]], "source": "semantic scholar"}
        else:
            counts[rid] = {"cited_by_count": None, "source": None}
    n = sum(1 for v in counts.values() if v["cited_by_count"] is not None)
    print(f"{len(counts)} papers; counted {n} (OpenAlex {sum(1 for v in counts.values() if v['source'] == 'openalex')},"
          f" Semantic Scholar {sum(1 for v in counts.values() if v['source'] == 'semantic scholar')}); "
          f"no count {len(counts) - n}")
    if "--write" in args:
        old = json.loads(RANKING.read_text(encoding="utf-8")) if RANKING.is_file() else {}
        RANKING.write_text(json.dumps({
            "counted_on": date.today().isoformat(),
            "rule": ("F114 with F57 folded in (Sprint 19, team lead q5 = b): `first` (F114 steps 1 to 3) in its "
                     "order, then context (hsbc-2026, the Dirac platforms, qml, qc, ml, world, method), then most "
                     "cited, no count last, then record id. Counts: OpenAlex by DOI (arXiv as 10.48550/arxiv.<id>), "
                     "then Semantic Scholar for arXiv papers OpenAlex does not count; null is no count, not 0. "
                     "A snapshot as of counted_on."),
            "first": old.get("first", []),
            "selected": old.get("selected", []),
            "counts": counts}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {RANKING.relative_to(ROOT)}")
    return 0


def load_ranking() -> dict:
    return json.loads(RANKING.read_text(encoding="utf-8")) if RANKING.is_file() else {}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["rank"]:
        return rank(args[1:])
    L = json.loads(LEDGER.read_text(encoding="utf-8"))
    with read_only() as conn:
        P = papers(conn)
    listed = rows(L, P, load_ranking(), group_read_files())
    if args[:1] == ["check"]:
        bad = problems(L, P, listed)
        print("\n".join(bad + [f"{len(bad)} problems; {len(listed)} papers in the list"]))
        return 1 if bad else 0
    top = int(args[args.index("--top") + 1]) if "--top" in args else len(listed)
    for i, x in enumerate(listed[:top], 1):
        print(f"{i}. {x['record_id']} | {x['group']} | {','.join(x['contexts']) or '-'} | "
              f"cited {x['cited_by_count'] if x['cited_by_count'] is not None else 'no count'} | {x['needs']} | "
              f"{x['copy']}")
    print(f"{len(listed)} papers to read in full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
