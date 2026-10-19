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
import time
import unicodedata
import urllib.error
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
SELECT = ("id,doi,title,publication_year,publication_date,cited_by_count,open_access,abstract_inverted_index,"
           "primary_location,locations,primary_topic,type,authorships")
S2 = "https://api.semanticscholar.org/graph/v1/paper/"
S2_FIELDS = "title,year,citationCount,externalIds,openAccessPdf"
S2_INTERVAL_S = 1.1  # Semantic Scholar's keyless rate is about 1 request per second
# Sprint 9 Task J (team lead, plan Q8 = 1): citations per year, cross-checked
# against Semantic Scholar, with a bonus for a match to a store context.
CONTEXT_BONUS = 1.5
CONTEXT_TERMS = {
    "hsbc-2026": ("fraud", "credit card", "card transaction"),
    # Anchored: plain "dirac" matched the Dirac equation, and "braket" would
    # match bra-ket notation (Task J review).
    "platform": ("dirac-3", "dirac-1", "dirac 3", "quantum computing inc", "entropy computing", "entropy quantum",
                 "coherent ising", "quantum annealing", "amazon braket", "classiq"),
    "qml": ("quantum machine learning", "quantum neural", "quantum kernel", "variational quantum"),
}
# A stream's own context earns no bonus inside it: every fraud record matched
# hsbc-2026 and 57 of 59 qml records matched qml, so the bonus ranked nothing.
STREAM_CONTEXT = {"fraud": "hsbc-2026", "qml": "qml"}
UNCHECKED_SHOWN = 10  # per stream, listed apart so a refusal cannot hide a paper
S2_SECOND_PASS_PAUSE_S = 60.0
DISAGREE_RATIO = 2.0  # OpenAlex and Semantic Scholar counts further apart than this are flagged
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
# F87 (Sprint 10 Task J): off-topic kinds the team lead excluded at Sprint 9
# Manual Validation (Q4 = 1, 13 records), dropped before ranking by
# OpenAlex primary topic, plus one title rule. Each topic was checked against
# the Sprint 9 pool: none drops a record the team lead accepted. A record
# that shares its topic with an accepted one is NOT filterable this way and
# stays for review (the single-photon platform paper in qml; the black-hole
# paper in tensor, beside an accepted holography paper). Dropped records are
# listed in the review, never silently removed.
OFF_TOPIC_TOPICS = {
    "ml": {"Computational Physics and Python Applications",  # SciPy, NumPy: software libraries
           "Data Analysis with R",                            # the Tidyverse
           "Metaheuristic Optimization Algorithms Research"},  # Grey Wolf and kin
    "qml": {"Quantum and electron transport phenomena",       # spin-qubit hardware
            "Brain Tumor Detection and Classification"},
    "tensor": {"Machine Learning in Materials Science",       # interatomic potentials
               "Physics of Superconductivity and Magnetism",
               "Probability and Statistical Research"},        # 1969 density estimation
    "fraud": set(),
}
# "Machine Learning and Algorithms" was dropped from tensor after the Task J
# review: it is a generic topic a tensor-network learning paper could carry,
# so "Learning with Pseudo-Ensembles" stays for review instead.
OFF_TOPIC_TITLE = {"tensor": re.compile(r"^Codebase release\b", re.IGNORECASE)}  # a release note of a held library
# A topic match is overridden by a learning term in the title (Task J review):
# the Python-applications topic also tags "Scikit-learn: Machine Learning in
# Python" and "Automatic differentiation in PyTorch", which the team lead
# never excluded.
OFF_TOPIC_KEEP_TITLE = {"ml": re.compile(r"learn|neural|deep|pytorch|tensorflow|differentiation", re.IGNORECASE)}


def off_topic(c: dict) -> str | None:
    """Why a candidate is dropped before ranking, or None."""
    topic = c.get("topic") or ""
    keep = OFF_TOPIC_KEEP_TITLE.get(c["stream"])
    if topic in OFF_TOPIC_TOPICS.get(c["stream"], set()) and not (keep and keep.search(c.get("title") or "")):
        return f"topic: {topic}"
    rule = OFF_TOPIC_TITLE.get(c["stream"])
    if rule and rule.search(c.get("title") or ""):
        return "title: a software release note"
    return None


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
        "date": work.get("publication_date") or str(year),
        "first_author": first_author(work),
        "type": work.get("type"),
    }


_PARTICLES = {"da", "dal", "de", "del", "della", "der", "di", "du", "la", "le", "van", "von", "dos", "das", "ter"}


def first_author(work: dict) -> str:
    """The first author's family name, with its particles ("Dal Pozzolo"),
    for the hand-download file name."""
    for a in work.get("authorships") or []:
        parts = ((a.get("author") or {}).get("display_name") or "").split()
        if parts:
            i = len(parts) - 1
            while i > 1 and parts[i - 1].lower() in _PARTICLES:
                i -= 1
            return " ".join(parts[i:])
    return "Unknown"


S2_BACKOFF_S = (5.0, 15.0, 30.0)  # waits after a 429 before each retry (first run: 52 of 192 refused)


def s2_check(c: dict, fetch=None, sleep=time.sleep) -> dict:
    """Semantic Scholar's view of a candidate: citation count, year, arXiv id
    and free PDF. By DOI, then by arXiv id when the DOI is not found (an
    OpenAlex record under a wrong DOI). A 429 is retried after S2_BACKOFF_S;
    a refusal that persists leaves it unchecked, never guessed."""
    idents = []
    if c.get("doi") and "10.48550" not in c["doi"].lower():
        idents.append(f"DOI:{c['doi']}")
    if c.get("arxiv"):
        idents.append(f"ARXIV:{c['arxiv']}")
    if not idents:
        return {"s2_status": "no identifier"}
    fetch = fetch or (lambda u: urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "curl/8.0"}), timeout=30).read())
    status = "not found"
    for ident in idents:
        url = S2 + urllib.parse.quote(ident, safe=":/") + "?fields=" + S2_FIELDS
        d = None
        for wait in (*S2_BACKOFF_S, None):
            try:
                d = json.loads(fetch(url))
                break
            except urllib.error.HTTPError as err:
                if err.code == 429 and wait is not None:
                    sleep(wait)
                    continue
                if err.code != 404:
                    return {"s2_status": f"unchecked (HTTP {err.code})"}
                break
            except (OSError, ValueError) as err:
                return {"s2_status": f"unchecked ({type(err).__name__})"}
        if d is None:
            continue
        # The answer must be the same paper (Task J review: a 2026 record came
        # back as a 2021 work with 9 citations, and its count won).
        if not same_title(c.get("title") or "", d.get("title") or ""):
            status = f"mismatch (Semantic Scholar's {ident} is \"{(d.get('title') or '')[:80]}\")"
            continue
        return {"s2_status": "answered", "s2_matched_by": ident, "s2_cites": d.get("citationCount"),
                "s2_year": d.get("year"), "s2_arxiv": (d.get("externalIds") or {}).get("ArXiv"),
                "s2_pdf": (d.get("openAccessPdf") or {}).get("url") or None}
    return {"s2_status": status}


def same_title(a: str, b: str) -> bool:
    """Equal after normalizing, or one is the other plus a subtitle."""
    x, y = norm_title(a), norm_title(b)
    if not x or not y:
        return False
    short, long_ = sorted((x, y), key=len)
    return x == y or (len(short) >= 20 and long_.startswith(short))


def context_matches(c: dict) -> list[str]:
    text = f"{c.get('title') or ''} {c.get('abstract') or ''}".lower()
    return [ctx for ctx, terms in CONTEXT_TERMS.items() if any(t in text for t in terms)]


def score(c: dict, today: date) -> dict:
    """The Q8 rubric, computed every run and never stored: citations per year
    since publication (Semantic Scholar's count and the earlier year when it
    answered), times CONTEXT_BONUS when a store context matches."""
    cites, year = c["cited_by"], c["year"]
    check = "unchecked"
    if c.get("s2_status") == "answered" and c.get("s2_cites") is not None:
        s2 = c["s2_cites"]
        lo, hi = sorted((max(1, cites), max(1, s2)))
        check = "agree" if hi / lo <= DISAGREE_RATIO else f"DISAGREE (OpenAlex {cites}, Semantic Scholar {s2})"
        cites = s2
        if c.get("s2_year"):
            year = min(year, c["s2_year"])
    cpy = cites / max(1, today.year - year + 1)
    ctxs = context_matches(c)
    bonus = [x for x in ctxs if x != STREAM_CONTEXT.get(c.get("stream"))]
    return {"rank_cites": cites, "rank_year": year, "citation_check": check, "contexts": ctxs,
            "bonus_contexts": bonus, "score": round(cpy * (CONTEXT_BONUS if bonus else 1.0), 1)}


def rank_key(c: dict) -> tuple[bool, float]:
    """Checked counts first, then by score. An OpenAlex count Semantic Scholar
    could not confirm is listed, labeled, after every checked one: the
    review run's first ml entry was a 2026 record with 45,780 OpenAlex
    citations that Semantic Scholar does not know."""
    return (c["citation_check"] == "unchecked", -c["score"])


def collapse_duplicates(cands: list[dict]) -> tuple[list[dict], int]:
    """One candidate per normalized title in a stream, keeping the most cited
    (OpenAlex merges and splits records; Sprint 7 pilot finding)."""
    best: dict[tuple[str, str], dict] = {}
    for c in cands:
        k = (c["stream"], norm_title(c["title"]))
        if k not in best or (c.get("s2_cites") or c["cited_by"]) > (best[k].get("s2_cites") or best[k]["cited_by"]):
            best[k] = c
    return list(best.values()), len(cands) - len(best)


def free_copy(c: dict) -> str | None:
    arx = c.get("arxiv") or c.get("s2_arxiv")
    return f"arXiv:{arx}" if arx else (c.get("oa_url") or c.get("s2_pdf"))


def _ascii_words(text: str) -> list[str]:
    """Words for a file name: accents dropped, hyphens inside a word kept
    ("Human-level", not "Humanlevel")."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return [w.strip("-") for w in re.sub(r"[^A-Za-z0-9 -]", "", plain).split() if w.strip("-")]


def is_book(c: dict) -> bool:
    return (c.get("type") or "") in ("book", "monograph", "edited-book")


def target_folder(c: dict) -> str:
    return "Books" if is_book(c) else "Papers"


def target_name(c: dict) -> str:
    """The folder's convention: Papers `YYYY-MM_Author_Title-words.pdf`;
    Books `Book - Title - Publisher Year.pdf` (Task J review: a Springer
    book was routed as a paper)."""
    if is_book(c):
        return f"Book - {' '.join(_ascii_words(c['title']))} - {' '.join(_ascii_words(c.get('publisher') or ''))} " \
               f"{c['year']}.pdf".replace("  ", " ")
    author = "-".join(_ascii_words(c["first_author"])) or "Unknown"
    return f"{(c.get('date') or str(c['year']))[:7]}_{author}_{'-'.join(_ascii_words(c['title'])[:8])}.pdf"


def free_copy_search(c: dict) -> str:
    """Every place a free copy was looked for, and what each said."""
    return (f"OpenAlex arXiv location: {c.get('arxiv') or 'none'}; OpenAlex open-access URL: {c.get('oa_url') or 'none'}; "
            f"Semantic Scholar arXiv id: {c.get('s2_arxiv') or 'none'}; Semantic Scholar open PDF: "
            f"{c.get('s2_pdf') or 'none'} ({c.get('s2_status', 'not asked')})")


def render_review(top: dict[str, list[dict]], counts: dict, today: date,
                  unchecked: dict[str, list[dict]] | None = None,
                  dropped: dict[str, list[dict]] | None = None) -> str:
    unchecked, dropped = unchecked or {}, dropped or {}
    lines = [f"# F62 candidates for review, {today.isoformat()}", "",
             "Sprint 9 Task J. Every count is a snapshot as of this date. Score = citations per year since "
             f"publication (Semantic Scholar's count where it answered for the same title), times {CONTEXT_BONUS} "
             "when the title or abstract matches a store context (hsbc-2026, a platform, qml) other than the "
             "stream's own. Candidates whose count Semantic Scholar could not check are listed apart, after "
             "each stream's top list. Computed, never stored. Nothing here is in the store: a paper you choose "
             "enters through the door at `seen`.", ""]
    for stream, c in counts.items():
        lines.append(f"- **{stream}**: {c['fetched']} fetched; {c['held']} already in the store; {c['dupes']} "
                     f"duplicate titles collapsed; {c['checked']} asked of Semantic Scholar "
                     f"({c['answered']} answered for the same title, {c.get('mismatch', 0)} answered with a "
                     f"different paper, {c['disagree']} disagree); top {len(top[stream])} listed; "
                     f"{c['no_copy']} of those with no free copy")
    for stream, rows in top.items():
        lines += ["", f"## {stream}", ""]
        for i, c in enumerate(rows, 1):
            lines.append(f"{i}. **{c['title']}** ({c['rank_year']}; {c['venue'] or 'venue unknown'}). Score "
                         f"{c['score']}; {c['rank_cites']} citations; check: {c['citation_check']}; contexts: "
                         f"{', '.join(c['contexts']) or 'none'}. DOI {c['doi'] or 'none'}. Copy: "
                         f"{free_copy(c) or 'NONE: by hand'}.")
            if c["abstract"]:
                lines.append(f"   Abstract: {c['abstract'][:600]}{'...' if len(c['abstract']) > 600 else ''}")
        if unchecked.get(stream):
            lines += ["", f"### {stream}: count not confirmed by Semantic Scholar (listed so a refusal cannot "
                          "hide a paper)", ""]
            for c in unchecked[stream]:
                lines.append(f"- **{c['title']}** ({c['rank_year']}). OpenAlex {c['rank_cites']} citations; "
                             f"{c.get('s2_status', 'not asked')}. DOI {c['doi'] or 'none'}. Copy: "
                             f"{free_copy(c) or 'NONE: by hand'}.")
        if dropped.get(stream):
            lines += ["", f"### {stream}: dropped as off-topic before ranking (F87)", ""]
            for c in dropped[stream]:
                lines.append(f"- {c['title']} ({c['rank_year'] if 'rank_year' in c else c.get('year')}): "
                             f"{c['dropped']}")
    return "\n".join(lines) + "\n"


def render_hand_list(top: dict[str, list[dict]], today: date) -> str:
    lines = [f"# F62 hand-download list, {today.isoformat()}", "",
             "Candidates in the review lists with no free copy found. Download by hand into the target folder "
             "under `D:\\Data\\Harold\\EvidenceBasedDB\\`, under the target name, only if you choose the paper "
             "and only where your access allows. Never around a paywall.", ""]
    n = 0
    for stream, rows in top.items():
        for i, c in enumerate(rows, 1):
            if free_copy(c):
                continue
            n += 1
            lines += [f"{n}. **{c['title']}** ({stream} rank {i}, score {c['score']})",
                      f"   - DOI: {c['doi'] or 'none'}; publisher link: "
                      f"{'https://doi.org/' + c['doi'] if c['doi'] else 'none'}",
                      f"   - Why: {stream} stream rank {i}; contexts {', '.join(c['contexts']) or 'none'}",
                      f"   - Target: {target_folder(c)}\\{target_name(c)}",
                      f"   - Free-copy search: {free_copy_search(c)}"]
    if not n:
        lines.append("None: every listed candidate has a free copy.")
    return "\n".join(lines) + "\n"


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


class DropAuthOnHostChange(urllib.request.HTTPRedirectHandler):
    """urllib copies every header onto a redirect, the key included, to any
    host (Task J review). A redirect off OpenAlex's host goes without it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(req.full_url).hostname:
            new.remove_header("Authorization")
        return new


_OPENER = urllib.request.build_opener(DropAuthOnHostChange)


def fetch_stream(stream: str, per: int, key: str | None, opener=None) -> list[dict]:
    opener = opener or _OPENER.open
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


def _arg(args: list[str], name: str, default: int) -> int:
    return int(args[args.index(name) + 1]) if name in args else default


def main(argv: list[str] | None = None, s2_fetch=None, sleep=time.sleep) -> int:
    """The review run (Sprint 9 Task J): --fetch N per stream from OpenAlex,
    drop what the store holds, check the best --check against Semantic
    Scholar (paced), collapse duplicate titles, keep the --top per stream.
    `--pilot` keeps the Sprint 7 pilot's report."""
    args = list(sys.argv[1:] if argv is None else argv)
    if "--pilot" in args:
        return pilot_main(args)
    if "--out" not in args:
        print("error: --out <folder outside the repository> is required", file=sys.stderr)
        return 2
    out = Path(args[args.index("--out") + 1]).resolve()
    if out == REPO_ROOT or REPO_ROOT in out.parents:
        print(f"error: refusing to write inside the repository ({out})", file=sys.stderr)
        return 2
    per, n_check, n_top = _arg(args, "--fetch", 100), _arg(args, "--check", 50), _arg(args, "--top", 25)
    key = openalex_key()
    print(f"OpenAlex key present: {key is not None}")
    today = date.today()
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        keys = store_keys(conn)
    finally:
        conn.close()
    fetched, to_check = {}, []
    for stream in STREAMS:
        rows = [candidate(w, stream, today) for w in fetch_stream(stream, per, key)]
        for c in rows:
            c["held"] = held_by_store(c, keys)
            c["dropped"] = off_topic(c)
        new = [c for c in rows if not c["held"] and not c["dropped"]]
        new.sort(key=lambda c: -score(c, today)["score"])
        fetched[stream] = (rows, new)
        to_check += new[:n_check]
    asked = 0
    for c in to_check:
        if asked:
            sleep(S2_INTERVAL_S)
        asked += 1
        c.update(s2_check(c, s2_fetch, sleep))
    # A second pass for refusals after a pause (Task J review: 11 of the ml
    # stream's best-known papers stayed refused and fell below the cut).
    refused = [c for c in to_check if c["s2_status"].startswith("unchecked (HTTP 429")]
    if refused:
        sleep(S2_SECOND_PASS_PAUSE_S)
        for c in refused:
            sleep(S2_INTERVAL_S)
            c.update(s2_check(c, s2_fetch, sleep))
    top, unchecked, counts, everything, dropped = {}, {}, {}, [], {}
    for stream, (rows, new) in fetched.items():
        new, dupes = collapse_duplicates(new)
        for c in new:
            c.update(score(c, today))
        new.sort(key=rank_key)
        top[stream] = [c for c in new if c["citation_check"] != "unchecked"][:n_top]
        unchecked[stream] = [c for c in new if c["citation_check"] == "unchecked" and "s2_status" in c][
            :UNCHECKED_SHOWN]
        sent = [c for c in new if "s2_status" in c and c["s2_status"] != "no identifier"]
        dropped[stream] = [c for c in rows if not c["held"] and c["dropped"]]
        counts[stream] = {"fetched": len(rows), "held": len(rows) - len([c for c in rows if not c["held"]]),
                          "dropped": len(dropped[stream]), "dupes": dupes, "checked": len(sent),
                          "answered": sum(c["s2_status"] == "answered" for c in sent),
                          "mismatch": sum(c["s2_status"].startswith("mismatch") for c in sent),
                          "disagree": sum(c["citation_check"].startswith("DISAGREE") for c in sent),
                          "no_copy": sum(1 for c in top[stream] if not free_copy(c))}
        everything += new + dropped[stream]  # dropped ones too, so a later check can see them (Task J review)
        print(f"{stream}: {counts[stream]}")
    out.mkdir(parents=True, exist_ok=True)
    stem = f"f62_review_{today.isoformat()}"
    (out / f"{stem}.json").write_text(json.dumps(everything, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / f"{stem}.md").write_text(render_review(top, counts, today, unchecked, dropped), encoding="utf-8")
    (out / f"f62_hand_download_{today.isoformat()}.md").write_text(render_hand_list(top, today), encoding="utf-8")
    print(f"wrote {out / (stem + '.md')}, .json and the hand-download list")
    return 0


def pilot_main(args: list[str]) -> int:
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
