#!/usr/bin/env python3
"""Sprint 5 Task C (F31 part 2): the intake manifest for the HSBC Phase 2 bibliography.

Reads the same parse and download plan as scripts/sprint5_bibliography.py
and writes a JSON manifest for `scripts/intake.py --manifest`. Writes
nothing to the store: the manifest is reviewed through intake.py's own dry
run before `--apply` (docs/INTAKE_WORKFLOW.md section 6).

Context per section was written down BEFORE this code, in
docs/INTAKE_WORKFLOW.md section 11 (2026-09-24); SECTION_CONTEXT and
TAG_CONTEXT below transcribe it.

DOIs: used when written in the entry; when derivable from a publisher URL
by the publisher's own scheme (Nature, Quantum, Zenodo) and CONFIRMED
against the entry's title on Crossref; or when Crossref returns an exact
normalized title match. Never guessed. Everything else with a saved local
copy becomes a hand-origin record whose citation says it was transcribed.

Usage: python scripts/sprint5_bibliography_manifest.py --bib <BIBLIOGRAPHY.md> --meta <cache.json> --out <manifest.json>
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_bibliography as bib  # noqa: E402

SECTION_CONTEXT = {1: "qml", 2: "qml", 3: "qml", 4: "qml", 5: "world", 6: "qml", 7: "platform:dirac-3",
                   8: "platform:dirac-3", 9: "qml", 10: "ml", 11: "ml", 12: "ml", 13: "qc", 14: "hsbc-2026",
                   15: "hsbc-2026"}
TAG_CONTEXT = {"FW-3": "method", "EN-6": "qc", "DS-5": "qc", "QC-3": "qc", "TN-4": "qc", "CE-22": "world",
               "CE-23": "world", "GP-1": "platform:braket", "GP-2": "platform:braket", "GP-3": "platform:braket",
               "GP-5": "platform:classiq", "GP-6": "platform:classiq", "GP-7": "platform:classiq"}
URL_DOI = [(re.compile(r"nature\.com/articles/(s\d{5}-\d{3}-\d{5}-\w)"), "10.1038/{}"),
           (re.compile(r"quantum-journal\.org/papers/(q-\d{4}-\d{2}-\d{2}-\d+)"), "10.22331/{}"),
           (re.compile(r"zenodo\.org/records/(\d+)"), "10.5281/zenodo.{}")]
# Entries in paper sections that are not papers (a blog, news, vendor pages).
REFERENCE_TAGS = {"EX-2", "EX-5", "QC-2", "QC-6", "QC-7", "IC-3", "CL-1", "CE-14"}
NO_SEARCH_SECTIONS = {13, 14, 15}
# The publishing organization for pages that name no person, by host.
ORGANIZATION = {"amazon": "Amazon Web Services", "quantumcomputinginc": "Quantum Computing Inc.",
                "classiq": "Classiq Technologies", "thequantuminsider": "The Quantum Insider",
                "quantumcomputingcost": "Quantum Computing Cost", "postquantum": "PostQuantum.com",
                "nvidia": "NVIDIA", "ctfassets": "Quantum Computing Inc.", "quantumfrontiers": "Quantum Frontiers"}


def _authors(e: bib.Entry) -> str:
    """The entry's authors; for an entry with no (year), the text before its title."""
    if e.authors:
        return e.authors
    after_tag = e.text.split("\n>")[0].split("**", 2)[2]
    m = re.match(r"\s*([^*]+?)\s*\*", after_tag, re.S)
    return " ".join(m.group(1).split()).rstrip(" .") if m else ""


def context_for(e: bib.Entry) -> str:
    return TAG_CONTEXT.get(e.tag) or SECTION_CONTEXT[e.section]


def disposition_for(e: bib.Entry, kind: str) -> str:
    prefix = {"reference": "Reference: ", "repo": "Code repository: "}.get(kind, "")
    return f"{prefix}Bulk intake 2026-09 from the HSBC Phase 2 bibliography [{e.tag}] ({e.section_name}); not yet screened"


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", bib._ascii(t).lower())


def crossref_find(e: bib.Entry) -> tuple[str, str] | None:
    """(DOI, note) when Crossref returns the entry's exact normalized title AND
    its year within one AND, if the entry names authors, its first author's
    family name. Title alone is not a key: on 2026-09-24 an exact-title match
    for [IN-3] (Howard et al., Nature 2014) returned a 2015 conference item
    with the same title."""
    if not e.title:
        return None
    url = ("https://api.crossref.org/works?rows=10&select=DOI,title,issued,author,container-title&query.bibliographic="
           + urllib.parse.quote(e.title))
    try:
        items = json.loads(bib._get(url, "application/json"))["message"]["items"]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return None
    first = _norm(re.split(r"[,.&]| et al", e.authors)[0].split()[-1]) if e.authors.strip() else ""
    head = _norm(e.text.split("\n>")[0])
    candidates = []
    for it in items:
        if _norm((it.get("title") or [""])[0]) != _norm(e.title):
            continue
        year = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        if e.year and (year is None or abs(int(year) - int(e.year)) > 1):
            continue
        families = [_norm(a.get("family", "")) for a in it.get("author", [])]
        if first and first not in families:
            continue
        venue = (it.get("container-title") or [""])[0]
        # Same authors and title can exist twice (Howard et al.: a Nature
        # article and a one-page ISMVL talk abstract). Prefer the venue the
        # entry names, then the exact year.
        score = (3 if venue and _norm(venue) in head else 0) + (2 if e.year and str(year) == e.year else 0)
        candidates.append((score, it["DOI"], year))
    if not candidates:
        return None
    candidates.sort(key=lambda c: -c[0])
    score, doi, year = candidates[0]
    note = "" if not e.year or str(year) == e.year else f"; registry year {year}, bibliography says {e.year}"
    if len(candidates) > 1:
        note += f"; chose over {', '.join(c[1] for c in candidates[1:])} by venue and year"
    return doi, note


def registry_title(doi: str) -> str | None:
    """The title the DOI's own registry gives (Crossref, then DataCite)."""
    for url in ("https://api.crossref.org/works/" + urllib.parse.quote(doi),
                "https://api.datacite.org/dois/" + urllib.parse.quote(doi)):
        try:
            data = json.loads(bib._get(url, "application/json"))
        except (urllib.error.URLError, OSError, ValueError):
            continue
        try:
            return data["message"]["title"][0] if "message" in data else data["data"]["attributes"]["titles"][0]["title"]
        except (KeyError, IndexError, TypeError):
            continue
    return None


def _page_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    return " ".join(_html.unescape(m.group(1)).split()) if m else ""


def _ref_id(title: str, year: str, source: str) -> str:
    site = bib._site(source) if source.startswith("http") else "resonance-alliance"
    return re.sub(r"-+", "-", f"{site}-{year or 'nd'}-{bib._words(title, 5)}".lower())


def build_manifest(entries: list[bib.Entry], actions: list[bib.Action]) -> tuple[list[dict], list[str]]:
    by_tag: dict[str, list[bib.Action]] = {}
    for a in actions:
        by_tag.setdefault(a.tag, []).append(a)
    out: list[dict] = []
    notes: list[str] = []
    seen: set[str] = set()

    def add(entry: dict) -> None:
        key = entry["access"].lower()
        if key in seen:
            notes.append(f"duplicate within the bibliography, entered once: {entry['access']}")
            return
        seen.add(key)
        out.append(entry)

    for e in entries:
        acts = by_tag.get(e.tag, [])
        kinds = {a.kind for a in acts}
        ctx = context_for(e)
        if kinds & {"arxiv-in-store", "in-store"}:
            notes.append(f"[{e.tag}] already a store record; not re-entered")
            continue
        for u in e.urls:  # repositories: standalone entries and papers' "Code:" links
            m = re.match(r"https://github\.com/([^/\s]+/[^/#?\s]+)", u)
            if m:
                add({"access": f"https://github.com/{m.group(1).removesuffix('.git')}", "kind": "repo",
                     "context": ctx, "disposition": disposition_for(e, "repo")})
        if e.arxiv:
            add({"access": f"arXiv:{e.arxiv[0]}", "context": ctx, "disposition": disposition_for(e, "paper")})
            continue
        if "repo" in kinds:
            continue
        doi, how = (e.dois[0], "written in the bibliography") if e.dois else (None, "")
        if not doi:
            for rx, fmt in URL_DOI:
                hit = next((rx.search(u) for u in e.urls if rx.search(u)), None)
                if hit:
                    doi, how = fmt.format(hit.group(1)), "derived from the publisher URL"
                    break
            if doi:
                t = registry_title(doi)
                saved = next((Path(a.target) for a in acts if a.kind == "web" and Path(a.target).exists()), None)
                page = _page_title(saved) if saved else ""
                if t and _norm(t)[:30] != _norm(e.title)[:30] and _norm(page).startswith(_norm(t)[:30]):
                    # The bibliography paraphrased; the registry and the saved page agree.
                    notes.append(f"[{e.tag}] bibliography title {e.title!r} is not the work's title; "
                                 f"registry and saved page both give {t!r}")
                elif t is None or _norm(t)[:30] != _norm(e.title)[:30]:
                    notes.append(f"[{e.tag}] DOI {doi} ({how}) not confirmed by its registry title {t!r}; not used")
                    doi = None
                else:
                    how += ", confirmed by the registry title"
        if not doi and e.section not in NO_SEARCH_SECTIONS and e.tag not in REFERENCE_TAGS:
            found = crossref_find(e)
            if found:
                doi, how = found[0], "found on Crossref by exact title, year and first author" + found[1]
        if doi:
            notes.append(f"[{e.tag}] DOI {doi} ({how})")
            add({"access": f"DOI:{doi}", "context": ctx, "disposition": disposition_for(e, "paper")})
            continue
        if e.tag in bib.MANUAL:
            notes.append(f"[{e.tag}] not entered: {bib.MANUAL[e.tag]}")
            continue
        saved = [a for a in acts if a.kind in ("web", "pdf", "copy") and Path(a.target).exists()]
        if not saved:
            notes.append(f"[{e.tag}] no DOI and no saved local copy; not entered (manual-download list)")
            continue
        a = saved[0]
        url = a.source if a.kind != "copy" else ""
        kind = "paper" if (e.section not in NO_SEARCH_SECTIONS and e.tag not in REFERENCE_TAGS) else "reference"
        title = e.title or (_page_title(Path(a.target)) if a.target.endswith(".html") else "") or e.tag
        who = _authors(e) or ("Resonance Alliance Inc." if not url else ORGANIZATION.get(bib._site(url), bib._site(url)))
        where = ("the saved page's title bar and HSBC Phase 2 bibliography entry " + e.tag) if url else \
                ("the document's cover and HSBC Phase 2 bibliography entry " + e.tag)
        venue = re.sub(r"^www\.", "", url.split("/")[2]) if url else "2026 Global Quantum + AI Challenge document"
        add({"access": f"{a.target} | {url}" if url else a.target, "kind": kind, "id": _ref_id(title, e.year, url or "x"),
             "context": ctx, "title": title,
             "citation": f'{who}, "{title}," {venue}, {e.year or "n.d."} (hand-transcribed from {where})',
             "transcribed_from": where, "disposition": disposition_for(e, kind)})
    return out, notes


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    def opt(name):
        return args[args.index(name) + 1] if name in args else None
    entries = bib.parse(Path(opt("--bib")).read_text(encoding="utf-8"))
    meta = bib.load_meta(entries, Path(opt("--meta")))
    manifest, notes = build_manifest(entries, bib.plan(entries, meta))
    Path(opt("--out")).write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(notes))
    counts: dict[str, int] = {}
    for m in manifest:
        key = m.get("kind", "paper") + ("/arXiv" if m["access"].startswith("arXiv:") else "/DOI" if m["access"].startswith("DOI:") else "")
        counts[key] = counts.get(key, 0) + 1
    print(f"\nMANIFEST {len(manifest)} entries {counts} -> {opt('--out')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
