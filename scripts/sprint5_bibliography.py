#!/usr/bin/env python3
"""Sprint 5 Tasks B and C (F31): the HSBC Phase 2 bibliography, downloaded and planned for intake.

Source: BIBLIOGRAPHY.md, written 2026-09-22/23 by a Claude research session
for the consumer repository's Phase 2, in a claude.ai scratch workspace
that is not durable. `--apply` first preserves it under
D:/Data/Harold/EvidenceBasedDB/References/ (the durable copy every record
from it points back to), then downloads.

Placement (team lead, Q1 = 2, 2026-09-24: merge into the existing folders):
  - arXiv papers from the quantum sections (1-10, and [GP-4]) go to
    QMLPapers/<year>/ under that folder's own filename convention
    `<Authors>_<Year>_<Title>__<arXiv id>.pdf`;
  - arXiv papers from the classical sections (11 and 12) go to Papers/
    under INTAKE_WORKFLOW.md section 3's `<YYYY-MM>_<first-author>_<short-title>.pdf`;
  - web, vendor, news and challenge pages go to References/, saved as the
    page's HTML (section 4: the local copy preserves what the source may
    not keep live); direct PDF links are saved as PDF.
  - The folders' existing manifest.tsv files are NOT edited (plan, Q1).
Nothing is fetched twice: an arXiv id already in the store, or already on
disk anywhere under the material directory (by id in the filename), is
pointed at, not downloaded. GitHub repositories are api-origin records
and are not cloned. Anything that cannot be fetched is written to
References/2026-09_HSBC-Phase2-bibliography_needs-manual-download.txt
with its reason, never dropped.

arXiv traffic is SERIAL and paced (plan pre-flight: a probe that
overlapped a paced batch earned HTTP 429): metadata through
store.citations.fetch_arxiv_batch, PDFs one at a time ARXIV_MIN_INTERVAL_S
apart, never concurrently with anything else.

Usage:
  python scripts/sprint5_bibliography.py plan  --bib <BIBLIOGRAPHY.md> --meta <cache.json>
  python scripts/sprint5_bibliography.py plan  --bib ... --meta ... --apply     (download)
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import citations, connect, script_paths  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
MATERIAL = Path(r"D:\Data\Harold\EvidenceBasedDB")
REFERENCES = MATERIAL / "References"
PRESERVED_NAME = "2026-09_HSBC-Phase2-research_BIBLIOGRAPHY.md"
MANUAL_LIST = REFERENCES / "2026-09_HSBC-Phase2-bibliography_needs-manual-download.txt"
CONSUMER_DOCS = Path(r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\docs")  # READ-ONLY (CLAUDE.md)
QUANTUM_SECTIONS = set(range(1, 11))
CLASSICAL_SECTIONS = {11, 12}
WEB_INTERVAL_S = 1.0

_ENTRY = re.compile(r"\n(?=\*\*\[[A-Z]{2}-\d+\]\*\*)")
_SECTION = re.compile(r"^## (\d+)\. (.+)$", re.M)
_ARXIV = re.compile(r"(?:arXiv:|arxiv\.org/(?:abs|pdf|html)/)(\d{4}\.\d{4,5})")
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s)>\]]+)")
_URL = re.compile(r"https?://[^\s)>\]]+")


@dataclass
class Entry:
    tag: str
    section: int
    section_name: str
    authors: str
    year: str
    title: str
    arxiv: list[str]
    dois: list[str]
    urls: list[str]
    local_docs: list[str]
    note: str
    text: str = field(repr=False)


def _clean_url(u: str) -> str:
    return u.rstrip(".,;")


def parse(bib_text: str) -> list[Entry]:
    sections = [(m.start(), int(m.group(1)), m.group(2).strip()) for m in _SECTION.finditer(bib_text)]
    out = []
    for chunk in _ENTRY.split(bib_text):
        if not chunk.startswith("**["):
            continue
        body = chunk.split("\n---")[0].split("\n## ")[0].strip()
        pos = bib_text.index(body)
        sec = [s for s in sections if s[0] < pos][-1]
        tag = re.match(r"\*\*\[([A-Z]{2}-\d+)\]\*\*", body).group(1)
        head = body.split("\n>")[0]
        after_tag = head.split("**", 2)[2]
        t = re.search(r"\*(.+?)\*", after_tag, re.S)
        title = " ".join(t.group(1).split()).rstrip(".") if t else ""
        y = re.search(r"\((\d{4})(?:-\d{4})?\)", after_tag)
        authors = " ".join(after_tag[: y.start()].split()).strip(" .") if y else ""
        note = " ".join(line.lstrip("> ").strip() for line in body.splitlines() if line.startswith(">"))
        urls = [_clean_url(u) for u in _URL.findall(head)]
        dois = []
        for d in _DOI.findall(head):
            d = d.rstrip(".,;/")
            if d not in dois:
                dois.append(d)
        out.append(Entry(
            tag=tag, section=sec[1], section_name=sec[2], authors=authors, year=y.group(1) if y else "",
            title=title, arxiv=list(dict.fromkeys(_ARXIV.findall(head))), dois=dois, urls=urls,
            local_docs=re.findall(r"`(docs/[^`]+\.pdf)`", head), note=note, text=body,
        ))
    return out


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def _words(title: str, n: int) -> str:
    w = re.findall(r"[A-Za-z0-9]+", _ascii(title))
    return "-".join(w[:n])


def _family(author: str) -> str:
    return re.sub(r"[^A-Za-z-]", "", _ascii(author.split(",")[0]).replace(" ", "-"))


def arxiv_year(ident: str) -> int:
    yy = int(ident[:2])
    return 2000 + yy


def qml_folder(ident: str) -> Path:
    year = arxiv_year(ident)
    return MATERIAL / "QMLPapers" / ("2007-2017" if year <= 2017 else str(year))


def qml_filename(md: citations.Metadata) -> str:
    fams = [_family(a) for a in md.authors] or ["Unknown"]
    who = fams[0] if len(fams) == 1 else (f"{fams[0]}-{fams[1]}" if len(fams) == 2 else f"{fams[0]}-et-al.")
    return f"{who}_{arxiv_year(md.ident)}_{_words(md.title, 10)}__{md.ident}.pdf"


def papers_filename(md: citations.Metadata) -> str:
    ym = f"{arxiv_year(md.ident)}-{md.ident[2:4]}"
    fam = _family(md.authors[0]) if md.authors else "Unknown"
    return f"{ym}_{fam}_{_words(md.title, 8)}.pdf"


def disk_index() -> dict[str, Path]:
    """arXiv id -> an existing file whose name carries it, anywhere under MATERIAL."""
    idx: dict[str, Path] = {}
    for p in MATERIAL.rglob("*"):
        if p.is_file():
            for m in re.finditer(r"(\d{4}\.\d{4,5})", p.name):
                idx.setdefault(m.group(1), p)
    return idx


def store_arxiv_ids() -> dict[str, str]:
    conn = connect(DB_PATH)
    try:
        out = {}
        for row in conn.execute("SELECT record_id, access FROM paper_fields"):
            parsed = citations.parse_access(row["access"])
            if parsed and parsed[0] == "arxiv":
                out[parsed[1]] = row["record_id"]
        return out
    finally:
        conn.close()


def _site(url: str) -> str:
    host = re.sub(r"^www\.", "", url.split("/")[2])
    return host.split(".")[0] if host.count(".") <= 1 else host.split(".")[-2]


def web_filename(e: Entry, url: str, i: int) -> str:
    ext = ".pdf" if url.lower().split("?")[0].endswith(".pdf") else ".html"
    title = e.title or e.note or e.tag
    suffix = f"-{i + 1}" if i else ""
    return f"{e.year or '2026'}_{e.tag}_{_site(url)}_{_words(title, 7)}{suffix}{ext}"


@dataclass
class Action:
    tag: str
    kind: str          # arxiv-download | arxiv-present | arxiv-in-store | web | pdf | copy | repo | manual
    source: str
    target: str
    reason: str = ""


MANUAL = {  # known before any request, from the bibliography's own caveats
    "QF-10": "paywalled (bibliography: 'Paywalled, abstract only'); Digital Finance, Springer",
    "QC-8": "no link or DOI in the bibliography; Scientific Reports, June 2026 (bibliography: paywalled)",
    "FW-3": "no link in the bibliography (Kaggle datasets 'announced via LinkedIn'); only the UCI source pages are named",
}


# Entries with no arXiv id that are nonetheless already store records,
# verified by title, venue and year against the record (2026-09-24).
KNOWN_IN_STORE = {"QC-9": "neven-2012-qboost-adiabatic-quantum-optimization"}


def plan(entries: list[Entry], meta: dict[str, citations.Metadata]) -> list[Action]:
    on_disk = disk_index()
    in_store = store_arxiv_ids()
    actions: list[Action] = []
    for e in entries:
        if e.tag in KNOWN_IN_STORE:
            actions.append(Action(e.tag, "in-store", (e.urls or [""])[0], KNOWN_IN_STORE[e.tag], "already a store record"))
            continue
        if e.tag in MANUAL:
            actions.append(Action(e.tag, "manual", (e.urls or [""])[0], "", MANUAL[e.tag]))
            continue
        if e.arxiv:
            ident = e.arxiv[0]
            if ident in in_store:
                actions.append(Action(e.tag, "arxiv-in-store", ident, in_store[ident], "already a store record"))
            elif ident in on_disk:
                actions.append(Action(e.tag, "arxiv-present", ident, str(on_disk[ident]), "already on disk"))
            else:
                md = meta[ident]
                if e.section in CLASSICAL_SECTIONS:
                    target = MATERIAL / "Papers" / papers_filename(md)
                else:
                    target = qml_folder(ident) / qml_filename(md)
                actions.append(Action(e.tag, "arxiv-download", f"https://arxiv.org/pdf/{ident}", str(target)))
            continue
        if e.local_docs:
            for doc in e.local_docs:
                src = CONSUMER_DOCS / Path(doc).name
                actions.append(Action(e.tag, "copy", str(src), str(REFERENCES / src.name)))
            continue
        urls = [u for u in e.urls if "github.com" not in u]
        if not urls and any("github.com" in u for u in e.urls):
            actions.append(Action(e.tag, "repo", e.urls[0], "", "api-origin repository record; not cloned"))
            continue
        for i, u in enumerate(urls):
            kind = "pdf" if u.lower().split("?")[0].endswith(".pdf") else "web"
            actions.append(Action(e.tag, kind, u, str(REFERENCES / web_filename(e, u, i))))
    return actions


def _get(url: str, accept: str = "*/*") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": citations.USER_AGENT, "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


MIN_VISIBLE_WORDS = 50  # below this a saved page is a shell, not the content


def visible_words(data: bytes) -> int:
    text = data.decode("utf-8", errors="replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    return len(re.sub(r"<[^>]+>", " ", text).split())


def _meta_refresh(data: bytes, base: str) -> str | None:
    m = re.search(rb'http-equiv="Refresh"\s+content="\d+;\s*url=([^"]+)"', data, re.I)
    return urllib.parse.urljoin(base, m.group(1).decode()) if m else None


def execute(actions: list[Action], bib_path: Path) -> list[Action]:
    REFERENCES.mkdir(parents=True, exist_ok=True)
    preserved = REFERENCES / PRESERVED_NAME
    if not preserved.exists():
        shutil.copy2(bib_path, preserved)
        print(f"PRESERVED {preserved}")
    manual: list[Action] = [a for a in actions if a.kind == "manual"]
    last_arxiv = 0.0
    for a in actions:
        if a.kind not in ("arxiv-download", "web", "pdf", "copy"):
            continue
        target = Path(a.target)
        if target.exists():
            if a.kind == "web" and visible_words(target.read_bytes()) < MIN_VISIBLE_WORDS:
                target.unlink()
                print(f"HOLLOW   {a.tag} {target.name} removed; re-fetching")
            else:
                print(f"PRESENT  {a.tag} {target.name}")
                continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if a.kind == "copy":
                shutil.copy2(a.source, target)
            else:
                if a.kind == "arxiv-download":
                    wait = citations.ARXIV_MIN_INTERVAL_S - (time.monotonic() - last_arxiv)
                    if wait > 0:
                        time.sleep(wait)
                data = _get(a.source)
                if a.kind == "arxiv-download":
                    last_arxiv = time.monotonic()
                else:
                    time.sleep(WEB_INTERVAL_S)
                if a.kind in ("arxiv-download", "pdf") and not data.startswith(b"%PDF"):
                    raise ValueError("response is not a PDF")
                if a.kind == "web" and visible_words(data) < MIN_VISIBLE_WORDS:
                    # Found 2026-09-24: four publisher pages saved as a 3,038-byte bot
                    # challenge, a Kaggle page as a JavaScript shell, a handbook as a
                    # one-line redirect. A shell saved as "the local copy" is a silent failure.
                    nxt = _meta_refresh(data, a.source)
                    if nxt:
                        time.sleep(WEB_INTERVAL_S)
                        data = _get(nxt)
                    if visible_words(data) < MIN_VISIBLE_WORDS:
                        raise ValueError(f"no content ({visible_words(data)} visible words: bot challenge or JavaScript-only page)")
                target.write_bytes(data)
            print(f"SAVED    {a.tag} {target}  ({target.stat().st_size} B)")
        except (urllib.error.URLError, OSError, ValueError, TimeoutError) as ex:
            reason = f"HTTP {ex.code}" if isinstance(ex, urllib.error.HTTPError) else str(ex)[:120]
            print(f"FAILED   {a.tag} {a.source}: {reason}")
            manual.append(Action(a.tag, "manual", a.source, a.target, reason))
    lines = ["# HSBC Phase 2 bibliography: items that need a manual download (Sprint 5 Task B, F31)",
             "# tag<TAB>source<TAB>reason"]
    lines += [f"{m.tag}\t{m.source}\t{m.reason}" for m in manual]
    MANUAL_LIST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {MANUAL_LIST} ({len(manual)} items)")
    return manual


def load_meta(entries: list[Entry], cache: Path) -> dict[str, citations.Metadata]:
    have: dict[str, citations.Metadata] = {}
    if cache.exists():
        have = {k: citations.Metadata(**v) for k, v in json.loads(cache.read_text(encoding="utf-8")).items()}
    need = [e.arxiv[0] for e in entries if e.arxiv and e.arxiv[0] not in have]
    if need:
        print(f"fetching arXiv metadata for {len(need)} id(s), serial, {citations.ARXIV_MIN_INTERVAL_S:.0f} s apart")
        have.update(citations.fetch_arxiv_batch(need))
        cache.write_text(json.dumps({k: asdict(v) for k, v in have.items()}, indent=1), encoding="utf-8")
    return have


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    def opt(name):
        return args[args.index(name) + 1] if name in args else None
    bib, cache = Path(opt("--bib")), Path(opt("--meta"))
    entries = parse(bib.read_text(encoding="utf-8"))
    meta = load_meta(entries, cache)
    actions = plan(entries, meta)
    counts: dict[str, int] = {}
    for a in actions:
        counts[a.kind] = counts.get(a.kind, 0) + 1
        print(f"{a.kind:15s} {a.tag:6s} {a.source[:70]:70s} -> {Path(a.target).name if a.target else a.reason}")
    print(f"\n{len(entries)} entries, {len(actions)} actions: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if "--apply" not in args:
        print("PLANNED (dry run; nothing downloaded). Re-run with --apply.")
        return 0
    manual = execute(actions, bib)
    print(f"done; {len(manual)} item(s) on the manual-download list")
    return 0


if __name__ == "__main__":
    sys.exit(main())
