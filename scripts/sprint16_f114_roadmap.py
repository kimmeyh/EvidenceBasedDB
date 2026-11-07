#!/usr/bin/env python3
"""Sprint 16 Task F (F114, F98 folded in): Roadmap-to-QML from ea6f42a7c0 (Sprint 14's release, F123) to COMMIT,
matched to the store; the papers it links for the first time entered at `seen`, each with its free copy.
INTAKE_WORKFLOW.md section 72.

The machinery is F104's (`scripts/sprint12_f104_roadmap.py`), loaded and pointed at this release's commit, copy
folder, manifest and tag, as Sprint 14's release did (`scripts/sprint14_f123_roadmap.py`). What differs:

- A route on a held paper only for a newly linked one (as F123).
- A Quantum journal link (a DOI 10.22331/q-...) new since PREVIOUS is entered through the door by its DOI, with the
  journal's free PDF (Quantum is open access), unless the store holds a paper of the same title (its arXiv preprint,
  say). Every other non-arXiv link the store does not hold is carried, as before.

    python scripts/sprint16_f114_roadmap.py --fetch   # the list's files, then metadata and PDFs, paced
    python scripts/sprint16_f114_roadmap.py           # dry run: writes the manifest; nothing written to the store
    python scripts/sprint16_f114_roadmap.py --apply   # verified backup first
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("f104", Path(__file__).with_name("sprint12_f104_roadmap.py"))
f104 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f104)

ROOT, DB_PATH = f104.ROOT, f104.DB_PATH
PREVIOUS = "ea6f42a7c063586ecdb0b9cf4c0ab37a33eccead"
PREVIOUS_DIR = f104.COPY_DIR.with_name(f"Roadmap-to-QML_{PREVIOUS[:10]}")
TODAY = "2026-11-06"
TAG = "Sprint 16 Task F, F114"
COMMIT = "399b022651366f0a4e7037ad3226cd7fe94e636f"
MANIFEST = ROOT / "manifests" / "sprint16_f114_roadmap.json"

f104.TODAY, f104.TAG, f104.COMMIT, f104.MANIFEST = TODAY, TAG, COMMIT, MANIFEST
f104.COPY_DIR = PREVIOUS_DIR.with_name(f"Roadmap-to-QML_{COMMIT[:10]}")
f104.API_CACHE = f104.COPY_DIR / "arxiv_api"
f104.FOUND_VIA = f"Roadmap-to-QML ({f104.REPO}) at commit {COMMIT[:10]}"

_QUANTUM = re.compile(r"^10\.22331/(q-\d{4}-\d{2}-\d{2}-\d+)$")
_entry, _route_held = f104.entry, f104.route_held


class CachedFetcher(f104.CachedFetcher):
    """F104's fetcher, with Crossref's answers kept on disk too, so a dry run and an apply send no request."""

    def __call__(self, url: str, accept: str) -> bytes:
        if not url.startswith(citations.CROSSREF_API):
            return super().__call__(url, accept)
        cached = f104.API_CACHE / f"{hashlib.sha256(url.encode()).hexdigest()[:24]}.bin"
        if cached.exists():
            return cached.read_bytes()
        data = self.paced(url, accept)
        f104.API_CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
        return data


def at(folder: Path, fn):
    """fn() with F104 reading the list's copy in `folder`."""
    current = f104.COPY_DIR
    f104.COPY_DIR = folder
    try:
        return fn()
    finally:
        f104.COPY_DIR = current


def links() -> dict[str, tuple[str, str]]:
    """Every link's URL -> (the first file that links it, the link's text), in the copy F104 reads now."""
    out: dict[str, tuple[str, str]] = {}
    for name in f104.FILES:
        for label, url in f104._LINK.findall(f104.text_of(name)):
            out.setdefault(url, (name, " ".join(label.split())))
    return out


def newly_linked() -> dict[str, tuple[str, str]]:
    before = at(PREVIOUS_DIR, f104.listed)
    return {i: w for i, w in f104.listed().items() if i not in before}


def new_quantum(conn) -> list[dict]:
    """The Quantum journal papers the list links for the first time since PREVIOUS that the store does not hold."""
    before = set(at(PREVIOUS_DIR, links))
    held = f104.held_dois(f104.held_text(conn))
    out, seen = [], set()
    for url, (name, label) in links().items():
        doi = f104.url_doi(url) if url not in before and not f104._NOT_A_PAPER.search(url) else None
        m = _QUANTUM.match(doi or "")
        if m and doi not in held and doi not in seen:
            seen.add(doi)
            out.append({"doi": doi, "q": m.group(1), "file": name, "label": label, "url": url})
    return out


def quantum_file(q: str) -> Path | None:
    hits = sorted(p for p in f104.PAPERS.glob(f"*_{q}.pdf"))
    return hits[0] if hits else None


def quantum_name(q: str, md) -> str:
    surname = re.sub(r"[^A-Za-z]", "", (md.authors[0].split(",")[0] if md.authors else "Unattributed"))
    words = re.sub(r"[^A-Za-z0-9 ]", " ", md.title).split()[:9]
    return f"{q[2:6]}-{q[7:9]}_{surname}_{'-'.join(words)}_{q}.pdf"


def quantum_pdf_url(q: str) -> str:
    return f"https://quantum-journal.org/papers/{q}/pdf/"


def fetch_quantum(items: list[dict], fetcher) -> int:
    failed = 0
    for it in items:
        if quantum_file(it["q"]):
            print(f"exists  {it['doi']}  {quantum_file(it['q']).name}")
            continue
        try:
            md, _ = citations.resolve(f"DOI:{it['doi']}", fetcher=fetcher)
            data = fetcher(quantum_pdf_url(it["q"]), "application/pdf")
        except (OSError, LookupError) as ex:  # reported, and the others still run (as F104's fetch_papers)
            print(f"FAILED  {it['doi']}: {type(ex).__name__}: {ex}")
            failed += 1
            continue
        if not data.startswith(b"%PDF"):
            print(f"FAILED  {it['doi']}: not a PDF")
            failed += 1
            continue
        target = f104.PAPERS / quantum_name(it["q"], md)
        target.write_bytes(data)
        print(f"saved   {it['doi']}  {target.name}  SHA-256 {hashlib.sha256(data).hexdigest()}")
    return failed


def entry(ident: str, where: tuple[str, str]) -> dict:
    out = _entry(ident, where)
    out["updated_reason"] = f"{TODAY}: added by scripts/sprint16_f114_roadmap.py ({TAG})"
    return out


def quantum_entry(it: dict) -> dict:
    path = quantum_file(it["q"])
    return {"access": f"DOI:{it['doi']}" + (f" | {path}" if path else ""), "context": "qml",
            "disposition": f"Listed in Roadmap-to-QML ({it['file']}); not yet read",
            "found_via": f"{f104.FOUND_VIA}, {it['file']}", "cited_as": it["label"] or it["url"],
            "evidence": (f"Local copy {path.name}, SHA-256 {hashlib.sha256(path.read_bytes()).hexdigest()}, "
                         f"fetched {TODAY} from {quantum_pdf_url(it['q'])} (Quantum, open access)") if path else None,
            "updated_reason": f"{TODAY}: added by scripts/sprint16_f114_roadmap.py ({TAG})"}


def route_held(conn, apply: bool, everything: dict, ids: list[str], bad: dict) -> tuple[int, list[str]]:
    new = newly_linked()
    return _route_held(conn, apply, {i: w for i, w in everything.items() if i in new}, ids, bad)


f104.entry, f104.route_held = entry, route_held


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    fetcher = CachedFetcher()
    if "--fetch" in args:
        f104.fetch_list()
        with connect(DB_PATH) as conn:
            ids, quantum = f104.new_ids(conn), new_quantum(conn)
        print(f"{len(ids)} new arXiv ids; {len(quantum)} new Quantum papers")
        return 1 if f104.fetch_papers(ids, fetcher) + fetch_quantum(quantum, fetcher) else 0
    missing = [n for n in f104.FILES if not f104.copy_of(n).exists()]
    if missing:
        print("missing list copies (run --fetch): " + ", ".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F114 Roadmap-to-QML release")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        quantum = new_quantum(conn)  # before the arXiv entries change what the store holds
        log, manifest = f104.apply_changes(conn, apply, fetcher)
        q_entered = []
        for it in quantum:
            record = f104.intake.build_record(quantum_entry(it), fetcher=fetcher, today=TODAY)
            same = conn.execute("SELECT id FROM records WHERE class = 'paper' AND lower(value) = ?",
                                (record.value.lower(),)).fetchone()
            if same:  # a Quantum paper often has an arXiv preprint the store may hold (F137's lesson)
                raise ValueError(f"{it['doi']}: the store holds {same[0]} with the same title; merge, do not enter")
            if apply:
                insert_paper(conn, record)
            q_entered.append({"doi": it["doi"], "record_id": record.id, "listed_in": it["file"],
                              "local_copy": quantum_file(it["q"]).name if quantum_file(it["q"]) else None})
            log.append(f"paper  {record.id} [seen]  {record.value[:70]}")
        manifest["previous_commit"] = PREVIOUS
        manifest["newly_linked_since_previous"] = sorted(newly_linked())
        manifest["quantum_entered"] = q_entered
        manifest["carried_to_next_release"] = [c for c in manifest["carried_to_next_release"]
                                               if c["doi"] not in {q["doi"] for q in quantum}]
        if apply:
            conn.commit()
    finally:
        conn.close()
    # As F104's: a later run that enters nothing keeps what the earlier apply recorded.
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    if old and not manifest["arxiv_ids_new"] and not q_entered:
        manifest["entered"], manifest["arxiv_ids_new"] = old["entered"], old["arxiv_ids_new"]
        manifest["quantum_entered"] = old["quantum_entered"]
    if old.get("routes_added_to_held_papers") and not manifest["routes_added_to_held_papers"]:
        manifest["routes_added_to_held_papers"] = old["routes_added_to_held_papers"]
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(log) or "nothing to enter")
    print(f"listed {manifest['arxiv_ids_listed']} arXiv ids; newly linked {len(manifest['newly_linked_since_previous'])}; "
          f"new this run {len(log)} entries; carried {len(manifest['carried_to_next_release'])} other links; "
          f"manifest {MANIFEST.relative_to(ROOT)}")
    print("APPLIED" if apply else "DRY RUN: nothing written to the store. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
