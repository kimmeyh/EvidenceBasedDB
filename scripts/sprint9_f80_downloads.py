#!/usr/bin/env python3
"""Sprint 9 Task G (F80): free copies of the slice's papers that have no local PDF.

For each record in `manifests/sprint9_f80_slice.json` stored by journal DOI
with no local copy, OpenAlex gives the arXiv version (key in the
Authorization header only); the PDF comes from arXiv through the door's paced
fetcher (18 s apart, inside F52's cap) into
D:\\Data\\Harold\\EvidenceBasedDB\\Papers\\ (outside git), named
YYYY-MM_Author_Title.pdf from the arXiv id and the store's title. Only free
copies: a record with no arXiv version is listed, never fetched elsewhere.
An existing file is never overwritten. Each saved file's first page must name
the arXiv id. DRY-RUN BY DEFAULT; `--apply` downloads.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, recheck, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("dc", Path(__file__).with_name("discover_candidates.py"))
dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dc)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
SLICE = ROOT / "manifests" / "sprint9_f80_slice.json"


def needs_copy(conn) -> list[tuple[str, str, str]]:
    """(record id, DOI, title) for slice records stored by DOI with no local copy."""
    data = json.loads(SLICE.read_text(encoding="utf-8"))
    out = []
    for rid in data["slice_1"] + [r["record_id"] for r in data["slice_2"]]:
        access, title = conn.execute("SELECT p.access, r.value FROM paper_fields p JOIN records r ON r.id = "
                                     "p.record_id WHERE p.record_id = ?", (rid,)).fetchone()
        if any(Path(p).exists() for p in recheck.local_paths(access)):
            continue
        parsed = citations.parse_access(access)
        if parsed and parsed[0] == "doi":
            out.append((rid, parsed[1], title))
    return out


# OpenAlex does not link this review to its arXiv version (2026-10-15); the
# first-page stamp check below confirms the id when the file arrives.
ARXIV_OVERRIDE = {"10.1088/1361-6633/aab406": "1709.02779"}


def arxiv_for(doi: str, key: str | None) -> str | None:
    if doi.lower() in ARXIV_OVERRIDE:
        return ARXIV_OVERRIDE[doi.lower()]
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")
    headers = {"User-Agent": "curl/8.0", "Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
        return dc.arxiv_of(json.loads(resp.read()))


def file_name(rid: str, arxiv: str, title: str) -> str:
    yymm = arxiv.split(".")[0]
    surname = rid.split("-")[0].capitalize()
    words = re.sub(r"[^A-Za-z0-9 ]", " ", title).split()[:9]
    return f"20{yymm[:2]}-{yymm[2:]}_{surname}_{'-'.join(words)}.pdf"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        todo = needs_copy(conn)
    finally:
        conn.close()
    key, fetcher, failed = dc.openalex_key(), citations.PacedFetcher(), 0
    for rid, doi, title in todo:
        arxiv = arxiv_for(doi, key)
        if not arxiv:
            print(f"no arXiv version known to OpenAlex: {rid} ({doi})")
            continue
        target = PAPERS / file_name(rid, arxiv, title)
        if target.exists():
            print(f"exists  {target.name}")
            continue
        if "--apply" not in args:
            print(f"planned {rid}: arXiv:{arxiv} -> {target.name}")
            continue
        try:
            data = fetcher(f"https://arxiv.org/pdf/{arxiv}", "application/pdf")
        except Exception as ex:  # noqa: BLE001 -- reported; the others still run
            print(f"FAILED  {rid}: {type(ex).__name__}: {ex}")
            failed += 1
            continue
        if not data.startswith(b"%PDF"):
            print(f"FAILED  {rid}: not a PDF")
            failed += 1
            continue
        target.write_bytes(data)
        first = subprocess.run(["pdftotext", "-l", "1", str(target), "-"], capture_output=True).stdout.decode(
            "utf-8", "replace")
        stamp = "stamp ok" if arxiv in first else "NO STAMP: check the first page by hand"
        print(f"saved   {target.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes  {stamp}")
    print("APPLIED" if "--apply" in args else "DRY RUN: nothing downloaded. Re-run with --apply.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
