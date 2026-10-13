#!/usr/bin/env python3
"""Sprint 8 Task F (F61): mine the Massoli et al. survey's curated paper list.

The list is `allPapers.md` in github.com/fvmassoli/survey-quantum-computation,
the companion of arXiv:2107.03313 ("A Leap among Quantum Computing and
Quantum Neural Networks: A Survey", already in the store as
`massoli-2022-leap-among-quantum-computing-quantum`). Its last commit is
2022-02-10, so the list is static. Each entry is an HTML <details> block:
the authors, a link, the title, the venue, topic tags, and a BibTeX record.

Order of work (master plan F61):
  1. Duplicates first: an entry is IN THE STORE when its arXiv id, its DOI,
     or its normalized title (with the first author's surname in the
     record's citation) matches a record.
  2. The rest get an identifier: the arXiv id from the link or the BibTeX
     record; else a DOI from the BibTeX record or the link; else a Crossref
     title search, accepted only on an exact normalized-title match.
  3. Entries with an identifier go through the door (`scripts/intake.py`)
     at `seen`, `found_via` naming the list, the section, the year and the
     entry's topic tags. Entries with none are REFUSED with the reason.
  4. The list's repository is entered (kind repo) and linked to the survey
     as `dataset-of`.
No PDF is fetched. IEEE entries enter by DOI (Crossref); their PDFs need
the team lead's account and are never fetched (F61 card).

ARXIV: the door's paced fetcher, 18 s apart, inside F52's cap. DRY-RUN BY
DEFAULT (the dry run resolves identifiers, which sends requests); `--apply`
takes a verified backup first. `--list <file>` reads a saved copy of
allPapers.md instead of fetching it. `--out <file>` writes the
classification as JSON.
"""
from __future__ import annotations

import base64
import html
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_source_link, append_updated_reason  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-12"
TAG = "Sprint 8 Task F, F61"
REPO = "fvmassoli/survey-quantum-computation"
SURVEY = "massoli-2022-leap-among-quantum-computing-quantum"
ROUTE = f"Massoli et al. survey list (github.com/{REPO}, allPapers.md)"
QML_TAGS = ("neural", "machine learning", "perceptron", "classification", "learning", "classifier", "kernel")

_ENTRY = re.compile(r"<details><summary>(.*?)</summary><pre><code>(.*?)</code></pre></details>", re.DOTALL)
_SECTION = re.compile(r"^# (Surveys|Papers)\s*$", re.MULTILINE)
_YEAR = re.compile(r"^### (\d{4})\s*$", re.MULTILINE)
_LINK = re.compile(r"<a href=([^\s>]+)>\s*(.*?)\s*</a>", re.DOTALL)
_AUTHORS = re.compile(r"^\s*\[([^\]]+)\]")
_VENUE = re.compile(r"</b>\s*<i>(.*?)</i>", re.DOTALL)
_TAGS = re.compile(r"<code><[bi]>[\[(](.*?)[\])]</[bi]></code>")
_FIELD = re.compile(r"^\s*(\w+)\s*=\s*\{+(.*?)\}+\s*,?\s*$", re.MULTILINE)
_ARXIV_ID = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:\s*)(\d{4}\.\d{4,5}|[a-z-]+/\d{7})(?:v\d+)?", re.IGNORECASE)
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>{}]+)", re.IGNORECASE)


def norm(title: str) -> str:
    """Lowercase letters and digits only: punctuation, case and spacing differ between lists."""
    return re.sub(r"[^a-z0-9]", "", html.unescape(title).lower())


def parse(md: str) -> list[dict]:
    """Every entry with its section, year, authors, link, title, venue, tags and BibTeX fields."""
    marks = sorted([(m.start(), "section", m.group(1)) for m in _SECTION.finditer(md)]
                   + [(m.start(), "year", m.group(1)) for m in _YEAR.finditer(md)])
    out = []
    for m in _ENTRY.finditer(md):
        section = year = ""
        for pos, kind, val in marks:
            if pos > m.start():
                break
            if kind == "section":
                section, year = val, ""
            else:
                year = val
        summary, bib = m.group(1), m.group(2)
        link = _LINK.search(summary)
        fields = {k.lower(): " ".join(v.split()) for k, v in _FIELD.findall(bib)}
        authors = _AUTHORS.search(summary)
        venue = _VENUE.search(summary)
        out.append({
            "section": section, "year": year,
            "authors": authors.group(1).strip() if authors else "",
            "link": link.group(1).strip() if link else "",
            "title": html.unescape(re.sub(r"\s+", " ", link.group(2))).strip().rstrip(".") if link else "",
            "venue": html.unescape(venue.group(1)).strip().rstrip(".") if venue else "",
            "tags": _TAGS.findall(summary),
            "bib": fields,
            "summary": html.unescape(re.sub(r"<[^>]+>", "", summary)).strip(),
        })
    return out


def doi_from_link(link: str) -> str:
    """A DOI the link carries: doi.org, /doi/, /article/ paths, or a nature.com article."""
    link = urllib.parse.unquote(link)
    m = re.search(r"nature\.com/articles/([^/?#\s]+)", link, re.IGNORECASE)
    if m and not m.group(1).startswith("10."):
        return "10.1038/" + re.sub(r"\.pdf+$", "", m.group(1), flags=re.IGNORECASE)
    m = re.search(r"quantum-journal\.org/(?:papers|views)/(q[v]?-\d{4}-\d{2}-\d{2}-\d+)", link, re.IGNORECASE)
    if m:
        return f"10.22331/{m.group(1)}"  # Quantum's DOIs repeat the paper's slug
    m = _DOI.search(link)
    if not m:
        return ""
    doi = re.split(r"[?&#]", m.group(1))[0]               # a query string is not part of the DOI
    doi = re.sub(r"\.pdf+$", "", doi, flags=re.IGNORECASE)  # a file suffix on the link ("Nature10012.pdff")
    doi = re.sub(r"/(meta|abstract|full|pdf|fulltext|epdf)$", "", doi.rstrip("./"))
    return doi


def identifiers(entry: dict) -> tuple[str, str]:
    """(arxiv id, doi) from the entry itself, either possibly ''."""
    bib = entry["bib"]
    text = " ".join([entry["link"], bib.get("journal", ""), bib.get("eprint", ""), bib.get("url", ""),
                     bib.get("note", ""), bib.get("archiveprefix", "")])
    a = _ARXIV_ID.search(text)
    arxiv = a.group(1) if a else ""
    if not arxiv and bib.get("eprint") and re.fullmatch(r"\d{4}\.\d{4,5}", bib["eprint"]):
        arxiv = bib["eprint"]
    doi = bib.get("doi", "").strip() or doi_from_link(entry["link"]) or doi_from_link(bib.get("url", ""))
    return arxiv, doi.rstrip(".")


def store_index(conn) -> dict:
    idx = {"arxiv": {}, "doi": {}, "title": {}}
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields"):
        parsed = citations.parse_access(access)
        if parsed and parsed[0] == "arxiv":
            idx["arxiv"][parsed[1].lower()] = rid
        elif parsed and parsed[0] == "doi":
            idx["doi"][parsed[1].lower()] = rid
    for rid, value in conn.execute("SELECT record_id, value FROM paper_probes WHERE field = 'version_of'"):
        idx["doi"].setdefault(value.lower(), rid)
    for rid, title, prov in conn.execute("SELECT id, value, provenance FROM records WHERE class = 'paper'"):
        idx["title"].setdefault(norm(title), []).append((rid, prov or ""))
    return idx


def first_surname(entry: dict) -> str:
    author = entry["bib"].get("author", "").split(" and ")[0]
    surname = author.split(",")[0] if "," in author else (author.split() or [""])[-1]
    return norm(surname)


def match(entry: dict, arxiv: str, doi: str, idx: dict) -> tuple[str, str]:
    """(record id, how) when the entry is already in the store, else ('', '')."""
    if arxiv and arxiv.lower() in idx["arxiv"]:
        return idx["arxiv"][arxiv.lower()], f"arXiv id {arxiv}"
    if doi and doi.lower() in idx["doi"]:
        return idx["doi"][doi.lower()], f"DOI {doi}"
    surname = first_surname(entry)
    for rid, prov in idx["title"].get(norm(entry["title"]), []):
        if not surname or surname in norm(prov):
            return rid, "normalized title and first author"
    return "", ""


def crossref_doi(title: str, fetcher) -> str:
    """A DOI from a Crossref bibliographic search, only on an exact normalized-title match."""
    url = (citations.CROSSREF_API.rstrip("/") + "?rows=3&select=DOI,title&query.bibliographic="
           + urllib.parse.quote(title))
    items = json.loads(fetcher(url, "application/json"))["message"]["items"]
    for item in items:
        if any(norm(t) == norm(title) for t in item.get("title", [])):
            return item["DOI"]
    return ""


def context_of(entry: dict) -> str:
    tags = " ".join(entry["tags"]).lower()
    return "qml" if any(t in tags for t in QML_TAGS) else "qc"


def entry_for(e: dict, access: str) -> dict:
    tags = ", ".join(t for t in e["tags"])
    return {
        "access": access, "context": context_of(e), "tier": "seen",
        "found_via": f"{ROUTE}, {e['section']} {e['year']}; tags: {tags}",
        "cited_as": e["summary"],
        "disposition": f"From the Massoli et al. survey's curated list ({e['section']}, {e['year']}); not yet screened",
        "updated_reason": f"{TODAY}: added by scripts/sprint8_f61_massoli_list.py ({TAG})",
    }


def load_list(args: list[str]) -> str:
    if "--list" in args:
        return Path(args[args.index("--list") + 1]).read_text(encoding="utf-8")
    raw = subprocess.run(["gh", "api", f"repos/{REPO}/contents/allPapers.md", "--jq", ".content"],
                         capture_output=True, check=True).stdout
    return base64.b64decode(raw).decode("utf-8")


def classify(entries: list[dict], idx: dict, fetcher, search=crossref_doi) -> list[dict]:
    """Each entry gets `cls` (in store / enter / refused), the record or access, and the reason."""
    seen_keys: dict[str, int] = {}
    for n, e in enumerate(entries):
        arxiv, doi = identifiers(e)
        rid, how = match(e, arxiv, doi, idx)
        key = (arxiv or doi or norm(e["title"])).lower()
        if key in seen_keys:
            e.update(cls="duplicate in the list", record="", reason=f"same as entry {seen_keys[key] + 1}")
            continue
        seen_keys[key] = n
        if rid:
            e.update(cls="in store", record=rid, reason=f"matched by {how}")
            continue
        if not arxiv and not doi and e["title"]:
            try:
                doi = search(e["title"], fetcher)
            except Exception as ex:  # noqa: BLE001 -- a failed search refuses this entry, with the reason
                e.update(cls="refused", record="", reason=f"Crossref title search failed ({type(ex).__name__})")
                continue
            if doi:
                rid, how = match(e, "", doi, idx)
                if rid:
                    e.update(cls="in store", record=rid, reason=f"matched by {how} (Crossref title search)")
                    continue
        if arxiv:
            e.update(cls="enter", record=f"arXiv:{arxiv}", reason="arXiv id from the entry")
        elif doi:
            e.update(cls="enter", record=f"DOI:{doi}", reason="DOI from the entry or an exact-title Crossref match")
        else:
            e.update(cls="refused", record="", reason="no arXiv id, no DOI, and no exact-title match on Crossref")
    return entries


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    entries = parse(load_list(args))
    print(f"{len(entries)} entries parsed")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        fetcher = citations.PacedFetcher()
        classify(entries, store_index(conn), fetcher)
        counts: dict[str, int] = {}
        for e in entries:
            counts[e["cls"]] = counts.get(e["cls"], 0) + 1
        print("by class: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        if apply:
            backup_before_write(DB_PATH, "F61 Massoli survey list")
        to_enter = [e for e in entries if e["cls"] == "enter"]
        done, skipped, failures = intake.intake(conn, [entry_for(e, e["record"]) for e in to_enter], apply, TODAY,
                                                fetcher)
        failed = {f.split(":", 1)[0] for f in failures}
        for e in to_enter:
            if any(e["record"].lower() in f.lower() for f in failed):
                e.update(cls="refused", reason="the door refused it: " + next(
                    f for f in failures if f.lower().startswith(e["record"].lower())).split(":", 2)[-1].strip())
        repo_entry = {"access": f"github.com/{REPO}", "kind": "repo", "context": "qml", "tier": "seen",
                      "found_via": "F61 card (master plan), 2026-10-06",
                      "disposition": ("Code repository: the curated paper list released with "
                                      f"{SURVEY} (arXiv:2107.03313); not yet screened"),
                      "updated_reason": f"{TODAY}: added by scripts/sprint8_f61_massoli_list.py ({TAG})"}
        intake.intake(conn, [repo_entry], apply, TODAY, fetcher)
        if apply:
            repo_id = conn.execute("SELECT record_id FROM paper_fields WHERE lower(access) LIKE ?",
                                   (f"%{REPO}%",)).fetchone()[0]
            if not conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ?",
                                (repo_id, SURVEY)).fetchone():
                add_source_link(conn, repo_id, SURVEY, "dataset-of",
                                "README: \"These articles represented the starting point for the paper [A Leap "
                                "among Quantum Computing and Quantum Neural Networks: A Survey]"
                                "(https://arxiv.org/abs/2107.03313)\" (read 2026-10-12)")
                append_updated_reason(conn, SURVEY, f"{TODAY} ({TAG}): its companion paper list linked "
                                      f"({repo_id}, dataset-of)", TODAY)
            conn.commit()
        print(f"entered {done}, already present {skipped}, refused by the door {len(failures)}")
        if "--out" in args:
            Path(args[args.index("--out") + 1]).write_text(
                json.dumps([{k: e[k] for k in ("section", "year", "authors", "title", "link", "cls", "record",
                                                "reason")} for e in entries], indent=1, ensure_ascii=False),
                encoding="utf-8")
    finally:
        conn.close()
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
