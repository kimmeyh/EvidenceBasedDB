#!/usr/bin/env python3
"""Sprint 5 Task F (F5 sub-part 2): every paper each QCi-affiliated person co-authored.

Input: the 18 people in docs/research/2026-09-24_F5_qci_affiliated_people.md,
each verified from a paper's own author and affiliation lines (Task E).

Search order (team lead, 2026-09-16): arXiv, then DOI registries, then
Google Scholar.
  - arXiv's API is asked first, one request per person, paced. It refused
    a sustained paced run from this client on 2026-09-23 and 2026-09-24
    (HTTP 429); when it does, DataCite's index of arXiv's own DOIs
    (client arxiv.content) answers the same question with full author lists.
  - Crossref, for journal papers with no arXiv record; its author query is
    fuzzy, so only exact family-plus-given matches are kept.
  - Google Scholar is NOT queried: no public API, and its robots.txt
    disallows /scholar. A person left with many unresolved hits is named
    for a manual check instead.

Disambiguation, written down BEFORE any hit was read (the research doc):
a hit is P's when (1, seed) it also carries another of the 18, or (2,
network) it shares at least two co-authors other than P with P's accepted
hits, iterated to a fixed point. Everything else is UNRESOLVED, reported
with counts, and not downloaded.

Dry run by default: writes the report JSON only. --apply downloads the
accepted arXiv papers, one at a time and paced, to
D:/Data/Harold/EvidenceBasedDB/QCiAuthorsPapers/<person>/ (team lead, Q6),
skipping any paper already in the store or already on disk anywhere under
the material directory. A paper accepted for two people is downloaded once,
under the first.

Usage: python scripts/sprint5_qci_authors.py --report <out.json> [--apply]
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_bibliography as bib  # noqa: E402
from store import citations  # noqa: E402

OUT_DIR = bib.MATERIAL / "QCiAuthorsPapers"
PEOPLE = [  # (given, family) exactly as printed; Task E
    ("Babak", "Emami"), ("Wesley", "Dyk"), ("David", "Haycraft"), ("Carrie", "Spear"), ("Lac", "Nguyen"),
    ("Nicholas", "Chancellor"), ("Mohammad-Ali", "Miri"), ("Uchenna", "Chukwu"), ("Yu-Ping", "Huang"),
    ("R. Joseph", "Rupert"), ("Sam", "Wu"), ("Nick", "Vrahoretis"), ("Irwin", "Huang"),
    ("Milan", "Begliarbekov"), ("Pranav", "Mahamuni"), ("Cesar", "Martinez-Delgado"),
    ("Joel Russell", "Huffman"), ("Yong Meng", "Sua"),
]
ML_CATS = {"cs.LG", "stat.ML", "cs.AI", "cs.NE"}
DATACITE = "https://api.datacite.org/dois"
CROSSREF = "https://api.crossref.org/works"


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def name_key(given: str, family: str) -> tuple[str, str]:
    """(family, first given initial), accent- and case-folded."""
    fam = re.sub(r"[^a-z]", "", _ascii(family))
    g = re.sub(r"[^a-z]", "", _ascii(given.split()[0] if given.split() else ""))
    return fam, g[:1]


# Family names too common for an initial to identify anyone (Task E notes).
COMMON_FAMILIES = {"huang", "wu", "nguyen"}


def _first_given(given: str) -> str:
    tok = given.replace(".", " ").split()
    return re.sub(r"[^a-z]", "", _ascii(tok[0])) if tok else ""


def is_person(given: str, family: str, person: tuple[str, str]) -> bool:
    """Is (given, family) as a source prints it the printed person?

    Family must match exactly (accent- and case-folded, hyphens dropped).
    The first given name must match in full (Yu-Ping == Yuping). A bare
    initial or a prefix (Nick / Nicholas) is accepted ONLY for a family
    name not in COMMON_FAMILIES: "Huang, Y." identifies nobody."""
    pg, pf = person
    if re.sub(r"[^a-z]", "", _ascii(family)) != re.sub(r"[^a-z]", "", _ascii(pf)):
        return False
    a, b = _first_given(pg), _first_given(given)
    if not a or not b:
        return False
    if a == b:
        return True
    if re.sub(r"[^a-z]", "", _ascii(pf)) in COMMON_FAMILIES:
        return False
    if b in NICKNAMES.get(a, ()) or a in NICKNAMES.get(b, ()):
        return True
    return (len(b) == 1 and a[0] == b) or a.startswith(b) or b.startswith(a)


# Printed short forms whose long form is not a prefix of them (Nick /
# Nicholas: "nick" is not a prefix of "nicholas").
NICKNAMES = {"nick": {"nicholas", "nicolas"}}


def names_other_qci_person(hit: dict, person: tuple[str, str]) -> bool:
    """Seed rule: the hit's author list carries ANOTHER of the 18."""
    return any(is_person(g, f, p) for g, f in hit["authors"] for p in PEOPLE if p != person)


def _json(url: str) -> dict:
    return json.loads(bib._get(url, "application/json"))


def datacite_hits(given: str, family: str) -> list[dict]:
    """Query by family name, filter by is_person. For a COMMON family the
    family-name result set runs to tens of thousands and the 10-page cap
    below truncated it (first run, 2026-09-24: "Huang" returned a sample,
    not Yu-Ping Huang's papers), so those ALSO query the full printed name
    and its hyphen-free form, and the two result sets are united: the
    full-name query reaches past the cap (Yu-Ping Huang: 75 hits against
    48 from the capped family query), and keeping the family query costs
    nothing for the records it does reach."""
    fam = re.sub(r"[^a-z]", "", _ascii(family))
    queries = [f'creators.familyName:"{family}"']
    if fam in COMMON_FAMILIES:
        forms = {f'"{family}, {given}"', f'"{family}, {given.replace("-", "")}"'}
        queries.append("creators.name:(" + " OR ".join(sorted(forms)) + ")")
    hits: list[dict] = []
    seen: set[str] = set()
    for q in queries:
        for h in _datacite_query(q, given, family):
            if h["id"] not in seen:
                seen.add(h["id"])
                hits.append(h)
    return hits


def _datacite_query(q: str, given: str, family: str) -> list[dict]:
    hits, page = [], 1
    while True:
        url = (f"{DATACITE}?client-id=arxiv.content&page[size]=500&page[number]={page}&query="
               + urllib.parse.quote(q))
        data = _json(url)
        for d in data["data"]:
            a = d["attributes"]
            creators = [(c.get("givenName") or "", c.get("familyName") or c.get("name", "").split(",")[0])
                        for c in a.get("creators", [])]
            if not any(is_person(g, f, (given, family)) for g, f in creators):
                continue
            ident = a["doi"].lower().removeprefix("10.48550/arxiv.")
            cats = {m.group(1) for s in a.get("subjects", []) if s.get("subjectScheme") == "arXiv"
                    for m in [re.search(r"\(([a-z\-]+(?:\.[A-Za-z\-]+)?)\)", s.get("subject", ""))] if m}
            abstract = next((d.get("description", "") for d in a.get("descriptions", [])
                             if d.get("descriptionType") == "Abstract"), "")
            hits.append({"id": f"arXiv:{ident}", "title": (a.get("titles") or [{}])[0].get("title", ""),
                         "year": a.get("publicationYear"), "authors": creators, "cats": sorted(cats),
                         "abstract": " ".join(abstract.split()), "source": "DataCite (arXiv DOIs)"})
        if page >= (data["meta"].get("totalPages") or 1) or page >= 10:
            break
        page += 1
    return hits


def crossref_hits(given: str, family: str) -> list[dict]:
    url = (f"{CROSSREF}?rows=200&select=DOI,title,author,issued,type,abstract&query.author="
           + urllib.parse.quote(f"{given} {family}"))
    out = []
    for it in _json(url)["message"]["items"]:
        creators = [(a.get("given", ""), a.get("family", "")) for a in it.get("author", [])]
        if not any(is_person(g, f, (given, family)) for g, f in creators):
            continue
        if it["DOI"].lower().startswith("10.48550/"):
            continue
        year = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        abstract = re.sub(r"<[^>]+>", " ", it.get("abstract", ""))  # Crossref abstracts are JATS XML
        out.append({"id": f"DOI:{it['DOI']}", "title": (it.get("title") or [""])[0], "year": year,
                    "authors": creators, "cats": [], "abstract": " ".join(abstract.split()), "source": "Crossref"})
    return out


def arxiv_first(given: str, family: str) -> tuple[list[dict], str]:
    """Ask arXiv's API first (the card's order). On refusal, say so; the
    DataCite index of arXiv DOIs is then the arXiv source."""
    url = f"{citations.ARXIV_API}?max_results=300&search_query=" + urllib.parse.quote(f'au:"{given} {family}"')
    try:
        body = citations.default_fetcher(url, "application/atom+xml")
    except urllib.error.HTTPError as ex:
        return [], f"arXiv API refused (HTTP {ex.code}); DataCite used"
    out = []
    for md in citations.parse_arxiv_atom(body):
        creators = [(a.split(",", 1)[1].strip() if "," in a else "", a.split(",", 1)[0]) for a in md.authors]
        if not any(is_person(g, f, (given, family)) for g, f in creators):
            continue
        out.append({"id": f"arXiv:{md.ident}", "title": md.title, "year": md.year, "authors": creators,
                    "cats": [], "source": "arXiv API"})
    return out, "arXiv API answered"


def _others(hit: dict, me: tuple[str, str]) -> set[tuple[str, str]]:
    return {name_key(g, f) for g, f in hit["authors"]} - {me}


def disambiguate(person: tuple[str, str], hits: list[dict]) -> tuple[list[dict], list[dict]]:
    me = name_key(*person)
    accepted, pending = [], []
    for h in hits:
        if names_other_qci_person(h, person):
            accepted.append({**h, "rule": "seed"})
        else:
            pending.append(h)
    changed = True
    while changed:
        changed = False
        network = [k for a in accepted for k in _others(a, me)]
        counts: dict = {}
        for k in network:
            counts[k] = counts.get(k, 0) + 1
        known = set(counts)
        for h in list(pending):
            if len(_others(h, me) & known) >= 2:
                accepted.append({**h, "rule": "network"})
                pending.remove(h)
                changed = True
    return accepted, pending


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _ascii(t))


def context_for(hit: dict) -> str:
    """docs/INTAKE_WORKFLOW.md section 12, written before the search."""
    cats = set(hit.get("cats") or [])
    if not cats:
        return "qc"
    q = any(c.startswith("quant-ph") for c in cats)
    m = bool(cats & ML_CATS)
    return "qml" if q and m else "qc" if q else "ml" if m else "world"


def search(pause_s: float = 1.0) -> dict:
    report = {}
    last_arxiv = 0.0
    for given, family in PEOPLE:
        wait = citations.ARXIV_MIN_INTERVAL_S - (time.monotonic() - last_arxiv)
        if wait > 0:
            time.sleep(wait)
        ax, ax_note = arxiv_first(given, family)
        last_arxiv = time.monotonic()
        dc = datacite_hits(given, family)
        time.sleep(pause_s)
        cr = crossref_hits(given, family)
        time.sleep(pause_s)
        # arXiv-API and DataCite hits are the same records; key by id, then
        # drop journal versions of papers already found on arXiv (by title).
        by_id = {h["id"]: h for h in ax}
        for h in dc:
            by_id[h["id"]] = {**by_id.get(h["id"], {}), **h} if h["id"] in by_id else h
        arxiv_titles = {_norm_title(h["title"]) for h in by_id.values()}
        for h in cr:
            if _norm_title(h["title"]) not in arxiv_titles:
                by_id.setdefault(h["id"], h)
        accepted, unresolved = disambiguate((given, family), list(by_id.values()))
        name = f"{given} {family}"
        report[name] = {
            "arxiv_api": ax_note, "hits": len(by_id), "accepted": sorted(accepted, key=lambda h: h["id"]),
            "unresolved_count": len(unresolved),
            "unresolved_sample": [f"{h['id']} {h['title'][:70]}" for h in unresolved[:10]],
            # Every unresolved hit, with its abstract, for the team lead's
            # revised Q1 (topic screening, 2026-09-25).
            "unresolved": sorted(unresolved, key=lambda h: h["id"]),
        }
        print(f"{name:24s} hits {len(by_id):4d}  accepted {len(accepted):4d} "
              f"(seed {sum(a['rule'] == 'seed' for a in accepted)}, network {sum(a['rule'] == 'network' for a in accepted)})"
              f"  unresolved {len(unresolved):4d}  [{ax_note}]")
    return report


def download(report: dict) -> list[str]:
    on_disk = bib.disk_index()
    in_store = bib.store_arxiv_ids()
    done: set[str] = set()
    failures, last = [], 0.0
    for person, r in report.items():
        folder = OUT_DIR / re.sub(r"[^A-Za-z0-9-]+", "-", person).strip("-")
        for h in r["accepted"]:
            if not h["id"].startswith("arXiv:"):
                continue
            ident = h["id"][6:]
            if ident in done or ident in in_store or ident in on_disk:
                continue
            md = citations.Metadata(kind="arxiv", ident=ident, title=h["title"],
                                    authors=[f"{f}, {g}" for g, f in h["authors"]], year=str(h["year"] or ""), date="")
            target = folder / bib.qml_filename(md)
            wait = citations.ARXIV_MIN_INTERVAL_S - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
            try:
                data = bib._get(f"https://arxiv.org/pdf/{ident}")
                last = time.monotonic()
                if not data.startswith(b"%PDF"):
                    raise ValueError("response is not a PDF")
                folder.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                done.add(ident)
                print(f"SAVED  {person}: {target.name}")
            except (urllib.error.URLError, OSError, ValueError) as ex:
                failures.append(f"{person}\t{h['id']}\t{ex}")
                print(f"FAILED {person}: {h['id']} {ex}")
    return failures


def manifest(report: dict) -> tuple[list[dict], list[str]]:
    """Accepted hits as intake entries (docs/INTAKE_WORKFLOW.md section 12),
    one per paper however many of the 18 co-authored it, skipping papers
    already in the store. Unresolved hits never enter."""
    in_store_arxiv = bib.store_arxiv_ids()
    from store import connect
    conn = connect(bib.DB_PATH)
    try:
        in_store_doi = {r[0].lower().removeprefix("doi:") for r in conn.execute(
            "SELECT access FROM paper_fields WHERE access LIKE 'DOI:%'")}
    finally:
        conn.close()
    out, notes, seen = [], [], set()
    for person, r in report.items():
        for h in r["accepted"]:
            key = h["id"].lower()
            if key in seen:
                continue
            seen.add(key)
            if h["id"].startswith("arXiv:") and h["id"][6:] in in_store_arxiv:
                notes.append(f"{h['id']} already a record ({in_store_arxiv[h['id'][6:]]})")
                continue
            if h["id"].startswith("DOI:") and h["id"][4:].lower() in in_store_doi:
                notes.append(f"{h['id']} already a record")
                continue
            derived = "" if h.get("cats") else ", context not derived: no arXiv categories"
            out.append({"access": h["id"], "context": context_for(h),
                        "disposition": f"Bulk intake 2026-09 from F5's QCi author search ({person}, {h['rule']}{derived}); "
                                       "not yet screened"})
    return out, notes


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    out = Path(args[args.index("--report") + 1])
    if out.exists() and "--research-again" not in args:
        report = json.loads(out.read_text(encoding="utf-8"))
        print(f"using existing report {out} (pass --research-again to search again)")
    else:
        report = search()
        out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if "--manifest-out" in args:
        entries, notes = manifest(report)
        Path(args[args.index("--manifest-out") + 1]).write_text(
            json.dumps(entries, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\n".join(notes))
        print(f"MANIFEST {len(entries)} entries")
    total = sum(len(r["accepted"]) for r in report.values())
    print(f"\n{len(report)} people, {total} accepted (before de-duplication across people)")
    if "--apply" not in args:
        print("PLANNED (dry run; nothing downloaded). Re-run with --apply.")
        return 0
    failures = download(report)
    (OUT_DIR / "download-failures.txt").write_text("\n".join(failures) + "\n", encoding="utf-8")
    print(f"done; {len(failures)} failure(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
