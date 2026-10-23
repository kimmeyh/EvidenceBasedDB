#!/usr/bin/env python3
"""Sprint 12 Task F (F104, F98's first release): Christophe Pere's
Roadmap-to-QML at its commit, matched to the store; its new arXiv papers
entered at `seen`. INTAKE_WORKFLOW.md section 46.

The list (github.com/Christophe-pere/Roadmap-to-QML) is read at COMMIT, the
head recorded at planning (pushed 2026-10-20). Its markdown files are saved
under `References\\` (outside git) as the copy this release read. Every
arXiv id they link, in the year files, `Workforce.md`, `Reviews/` and the
README, is matched to the store by the ids its records' `access`,
`evidence` and provenance hold; the new ones enter through the door
(`scripts/intake.py`) at `seen` under `qml`, each naming the file that
lists it. Their free PDFs are fetched by the one paced fetcher; reading is
G's machinery, through the shared ledger.

Links that are not arXiv are matched by the DOI in the URL where it has
one; those not in the store are listed in the manifest and carried to the
next F98 release (the card allows a large first release; this one was
sized to the arXiv ids at planning).

arXiv answers are cached on disk beside the list's copy, so the dry run and
the apply reuse the metadata `--fetch` asked for: the arXiv budget (F52's
cap) is shared with G's downloads.

    python scripts/sprint12_f104_roadmap.py --fetch   # the list's files, then arXiv metadata and PDFs, 18 s apart
    python scripts/sprint12_f104_roadmap.py           # dry run: writes the manifest; nothing written to the store
    python scripts/sprint12_f104_roadmap.py --apply   # verified backup first
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_found_via, append_updated_reason, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
TAG = "Sprint 12 Task F, F104"
REPO = "Christophe-pere/Roadmap-to-QML"
COMMIT = "a239747648fa20e32426dae2a004515b44cdf85c"
FILES = ("2007-2017/2007-2017.md", "2018/2018.md", "2019/2019.md", "2020/2020.md", "2021/2021.md", "2022/2022.md",
         "2023/2023.md", "2024/2024.md", "2025/2025.md", "2026/2026.md", "Workforce.md", "Reviews/Reviews.md",
         "README.md")
COPY_DIR = Path(r"D:\Data\Harold\EvidenceBasedDB\References") / f"Roadmap-to-QML_{COMMIT[:10]}"
API_CACHE = COPY_DIR / "arxiv_api"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
MANIFEST = ROOT / "manifests" / "sprint12_f104_roadmap.json"
FOUND_VIA = f"Roadmap-to-QML ({REPO}) at commit {COMMIT[:10]}"

_ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
# Not after a digit, nor after "digit.", so a DOI's tail is not read as an id, but the DOI form
# 10.48550/arXiv.2301.01234 is (fresh-eyes review of f99139e).
_HELD_ARXIV = re.compile(r"(?<!\d)(?<!\d\.)(\d{4}\.\d{4,5})(?!\d)")
_DOI = re.compile(r"10\.\d{4,9}/[^\s|;,()\"']+")
_LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")
_NOT_A_PAPER = re.compile(r"arxiv\.org|github\.com|gitlab\.com|scirate\.com|airtable\.com|youtube\.com|youtu\.be", re.I)


class CachedFetcher:
    """The paced fetcher, with arXiv and DataCite metadata answers kept on
    disk: a dry run and an apply after `--fetch` send no request."""

    def __init__(self):
        self.paced = citations.PacedFetcher()

    def __call__(self, url: str, accept: str) -> bytes:
        if not url.startswith((citations.ARXIV_API, citations.DATACITE_API)):
            return self.paced(url, accept)
        cached = API_CACHE / f"{hashlib.sha256(url.encode()).hexdigest()[:24]}.bin"
        if cached.exists():
            return cached.read_bytes()
        data = self.paced(url, accept)
        API_CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
        return data


def copy_of(name: str) -> Path:
    return COPY_DIR / Path(name)


def fetch_list() -> None:
    for name in FILES:
        path = copy_of(name)
        if path.exists():
            print(f"exists  {name}")
            continue
        url = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{name}"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "EvidenceBasedDB"}),
                                    timeout=60) as resp:
            data = resp.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"saved   {name}  SHA-256 {hashlib.sha256(data).hexdigest()}")


def text_of(name: str) -> str:
    return copy_of(name).read_text(encoding="utf-8", errors="replace")


def listed() -> dict[str, tuple[str, str]]:
    """arXiv id -> (the first file that links it, the link's text)."""
    out: dict[str, tuple[str, str]] = {}
    for name in FILES:
        text = text_of(name)
        for label, url in _LINK.findall(text):
            for ident in _ARXIV.findall(url):
                out.setdefault(ident, (name, " ".join(label.split())))
        for ident in _ARXIV.findall(text):  # a bare URL with no link text
            out.setdefault(ident, (name, ""))
    return out


def url_doi(url: str) -> str | None:
    m = re.search(r"(10\.\d{4,9}/[^?#\s]+)", url)
    if m:
        return re.sub(r"(\.pdf|/meta|/abstract|/full)$", "", m.group(1)).lower()
    # Only Nature's current article ids (s41586-...) are their DOI suffix; a legacy id such as
    # npjqi201523 is not (its DOI is dotted), so it is matched by its URL instead.
    m = re.search(r"nature\.com/articles/(s[0-9a-z.\-]+?)(?:\.pdf)?$", url)
    if m:
        return f"10.1038/{m.group(1)}".lower()
    m = re.search(r"pubs\.rsc\.org/\S*/([a-z]\d[a-z]{2}\d{5}[a-z])$", url, re.I)
    if m:
        return f"10.1039/{m.group(1)}".lower()
    m = re.search(r"quantum-journal\.org/papers/(q-[\d-]+)/?", url)
    return f"10.22331/{m.group(1)}".lower() if m else None


def held_text(conn) -> str:
    return " ".join(f"{a or ''} {e or ''} {p or ''}".lower() for a, e, p in conn.execute(
        "SELECT f.access, f.evidence, r.provenance FROM paper_fields f JOIN records r ON r.id = f.record_id"))


def held_dois(held: str) -> set[str]:
    return {d.rstrip(".") for d in _DOI.findall(held)}


def carried(held: str) -> list[dict]:
    """The non-arXiv links whose DOI the store does not hold, or that carry
    none: carried to the next release."""
    dois = held_dois(held)
    out, seen = [], set()
    for name in FILES:
        for label, url in _LINK.findall(text_of(name)):
            if _NOT_A_PAPER.search(url):
                continue
            doi = url_doi(url)
            key = doi or url
            if key in seen or (doi and doi in dois):
                continue
            seen.add(key)
            out.append({"file": name, "label": " ".join(label.split()), "url": url, "doi": doi})
    return out


def arxiv_file(ident: str) -> Path | None:
    hits = sorted(p for p in PAPERS.glob("*.pdf") if re.search(rf"(?<![\d.]){re.escape(ident)}(?:v\d+)?\.pdf$",
                                                               p.name))
    return hits[0] if hits else None


def arxiv_name(ident: str, md) -> str:
    surname = re.sub(r"[^A-Za-z]", "", (md.authors[0].split(",")[0] if md.authors else "Unattributed"))
    words = re.sub(r"[^A-Za-z0-9 ]", " ", md.title).split()[:9]
    return f"20{ident[:2]}-{ident[2:4]}_{surname}_{'-'.join(words)}_{ident}.pdf"


def malformed(ident: str) -> bool:
    """An id from 2015 on has five digits after the dot; the list's link
    for Asfaw et al. 2021 reads 2108.0131 for 2108.01311."""
    return int(ident[:4]) >= 1501 and len(ident.split(".")[1]) == 4


def split_ids(conn) -> tuple[list[str], dict[str, list[str]]]:
    """(the new ids, {each malformed id: the held ids it is a prefix of})."""
    held = set(_HELD_ARXIV.findall(held_text(conn)))
    bad = {i: sorted(h for h in held if h.startswith(i)) for i in listed() if malformed(i)}
    return sorted(i for i in listed() if i not in held and i not in bad), bad


def new_ids(conn) -> list[str]:
    return split_ids(conn)[0]


def fetch_papers(ids: list[str], fetcher: CachedFetcher) -> int:
    failed = 0
    todo = [i for i in ids if arxiv_file(i) is None]
    if not todo:
        return 0
    citations.assume_recent_arxiv_request()  # a run started right after another waits the full interval
    meta = citations.fetch_arxiv_batch(todo, fetcher)
    for ident in todo:
        md = meta.get(ident)
        if md is None:
            print(f"FAILED  arXiv:{ident}: no metadata")
            failed += 1
            continue
        try:
            data = fetcher(f"https://arxiv.org/pdf/{ident}", "application/pdf")
        except OSError as ex:  # an HTTP error included; reported, and the others still run
            print(f"FAILED  arXiv:{ident}: {type(ex).__name__}: {ex}")
            failed += 1
            continue
        if not data.startswith(b"%PDF"):
            print(f"FAILED  arXiv:{ident}: not a PDF")
            failed += 1
            continue
        target = PAPERS / arxiv_name(ident, md)
        target.write_bytes(data)
        first = subprocess.run(["pdftotext", "-l", "1", str(target), "-"], capture_output=True).stdout.decode(
            "utf-8", "replace")
        print(f"saved   arXiv:{ident}  {target.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  "
              f"{'stamp ok' if ident in first else 'NO STAMP: check by hand'}")
    return failed


def entry(ident: str, where: tuple[str, str]) -> dict:
    name, label = where
    path = arxiv_file(ident)
    return {"access": f"arXiv:{ident}" + (f" | {path}" if path else ""), "context": "qml",
            "disposition": f"Listed in Roadmap-to-QML ({name}); not yet read",
            "found_via": f"{FOUND_VIA}, {name}", "cited_as": label or f"arxiv.org/abs/{ident}",
            "evidence": (f"Local copy {path.name}, SHA-256 {hashlib.sha256(path.read_bytes()).hexdigest()}, "
                         f"fetched {TODAY} (paced fetcher)") if path else None,
            "updated_reason": f"{TODAY}: added by scripts/sprint12_f104_roadmap.py ({TAG})"}


def holders(conn) -> dict[str, list[str]]:
    """arXiv id -> the records whose access holds it."""
    out: dict[str, list[str]] = {}
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields"):
        for ident in set(_HELD_ARXIV.findall(access or "")):
            out.setdefault(ident, []).append(rid)
    return out


def route_held(conn, apply: bool, everything: dict, ids: list[str], bad: dict) -> tuple[int, list[str]]:
    """A found_via route on each held paper the list links, as the earlier list release did
    (scripts/qmlpapers_manifest.py, add_routes): the match is recorded on the record (fresh-eyes
    review of f99139e). Returns (routes added, listed ids no record's access holds)."""
    have = {r[0] for r in conn.execute("SELECT record_id FROM paper_found_via WHERE route LIKE ?",
                                       (f"{FOUND_VIA}%",))}
    hold, n, unplaced = holders(conn), 0, []
    for ident, (name, label) in sorted(everything.items()):
        if ident in ids:
            continue
        rids = [rid for i in (bad[ident] if ident in bad else [ident]) for rid in hold.get(i, [])]
        if not rids:
            unplaced.append(ident)
        for rid in sorted(set(rids) - have):
            if apply:
                add_found_via(conn, rid, f"{FOUND_VIA}, {name}", label or f"arxiv.org/abs/{ident}")
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}): also listed in Roadmap-to-QML ({name})", TODAY)
            have.add(rid)
            n += 1
    return n, unplaced


def apply_changes(conn, apply: bool, fetcher) -> tuple[list[str], dict]:
    everything = listed()
    held = held_text(conn)
    ids, bad = split_ids(conn)
    log, entered = [], []
    for ident in ids:
        record = intake.build_record(entry(ident, everything[ident]), fetcher=fetcher, today=TODAY)
        if apply:
            insert_paper(conn, record)
        entered.append({"arxiv": ident, "record_id": record.id, "listed_in": everything[ident][0],
                        "local_copy": arxiv_file(ident).name if arxiv_file(ident) else None})
        log.append(f"paper  {record.id} [seen]  {record.value[:70]}")
    routes, unplaced = route_held(conn, apply, everything, ids, bad)
    if routes:
        log.append(f"route  {routes} held papers: {FOUND_VIA}, <file>")
    if unplaced:
        log.append(f"UNPLACED {len(unplaced)} listed ids held only outside access: {unplaced[:5]}")
    later = carried(held)
    manifest = {
        "release": TAG, "read_on": TODAY, "repository": REPO, "commit": COMMIT,
        "files": {n: hashlib.sha256(copy_of(n).read_bytes()).hexdigest() for n in FILES},
        "arxiv_ids_listed": len(everything), "arxiv_ids_new": len(ids), "entered": entered,
        "malformed_links": [{"listed_as": i, "listed_in": everything[i][0], "label": everything[i][1],
                             "held_as": held_ids} for i, held_ids in sorted(bad.items())],
        "routes_added_to_held_papers": routes if apply else None,
        "carried_to_next_release": later,
        "carried_why": ("links that are not arXiv, matched by the DOI in the URL where it has one, and not in the "
                        "store; this release was sized to the arXiv ids at planning (plan Task F), and F98's next "
                        "release takes them"),
    }
    return log, manifest


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    fetcher = CachedFetcher()
    if "--fetch" in args:
        fetch_list()
        conn = connect(DB_PATH)
        try:
            ids = new_ids(conn)
        finally:
            conn.close()
        print(f"{len(ids)} new arXiv ids")
        return 1 if fetch_papers(ids, fetcher) else 0
    missing = [n for n in FILES if not copy_of(n).exists()]
    if missing:
        print("missing list copies (run --fetch): " + ", ".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F104 Roadmap-to-QML first release")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log, manifest = apply_changes(conn, apply, fetcher)
        if apply:
            conn.commit()
    finally:
        conn.close()
    # The release's record. A later run that enters nothing (or adds no route) keeps what the
    # earlier apply wrote for it, so the list of what was entered is never lost; the rest is refreshed.
    new_now = manifest["arxiv_ids_new"]
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    if old and not manifest["arxiv_ids_new"]:
        manifest["entered"], manifest["arxiv_ids_new"] = old["entered"], old["arxiv_ids_new"]
    if old.get("routes_added_to_held_papers") and not manifest["routes_added_to_held_papers"]:
        manifest["routes_added_to_held_papers"] = old["routes_added_to_held_papers"]
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(log) or "nothing to enter")
    print(f"listed {manifest['arxiv_ids_listed']} arXiv ids; new this run {new_now}; carried "
          f"{len(manifest['carried_to_next_release'])} other links; manifest {MANIFEST.relative_to(ROOT)}")
    print("APPLIED" if apply else "DRY RUN: nothing written to the store. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
