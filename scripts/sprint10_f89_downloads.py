#!/usr/bin/env python3
"""Sprint 10 Task I (F89): free copies of the slice's papers that have no local copy.

For each record in `manifests/sprint10_f89_slice.json` with no local copy
(`store.recheck.local_pdf`): an arXiv record's own id; a DOI record's arXiv
version from OpenAlex (key in the Authorization header only), else the
open-access PDF OpenAlex lists for it (`best_oa_location.pdf_url`, a legal
free copy the publisher or a repository serves). arXiv PDFs come through the
door's paced fetcher (18 s apart, inside F52's cap). Nothing is fetched from
anywhere else, and a paywalled paper is listed, never fetched. Saved into
D:\\Data\\Harold\\EvidenceBasedDB\\Papers\\ (outside git); an existing file
is never overwritten; an arXiv file's first page must name its id.
Each saved file's SHA-256 is printed for the reading script to record.
DRY-RUN BY DEFAULT; `--apply` downloads.
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

_spec = importlib.util.spec_from_file_location("f80dl", Path(__file__).with_name("sprint9_f80_downloads.py"))
f80dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80dl)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PAPERS = f80dl.PAPERS
SLICE = ROOT / "manifests" / "sprint10_f89_slice.json"


def needs_copy(conn) -> list[tuple[str, str, str, str]]:
    """(record id, kind, identifier, title) for slice records with no local copy."""
    out = []
    for row in json.loads(SLICE.read_text(encoding="utf-8"))["slice"]:
        rid = row["record_id"]
        access, title = conn.execute("SELECT p.access, r.value FROM paper_fields p JOIN records r ON r.id = "
                                     "p.record_id WHERE p.record_id = ?", (rid,)).fetchone()
        parsed = citations.parse_access(access or "")
        if recheck.local_pdf(access, parsed[1] if parsed else rid):
            continue
        if parsed:
            out.append((rid, parsed[0], parsed[1], title))
    return out


def openalex_work(doi: str, key: str | None) -> dict:
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")
    headers = {"User-Agent": "curl/8.0", "Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
        return json.loads(resp.read())


def file_name(rid: str, arxiv: str | None, year: str, title: str) -> str:
    surname = rid.split("-")[0].capitalize()
    words = re.sub(r"[^A-Za-z0-9 ]", " ", title).split()[:9]
    if arxiv and "/" in arxiv:  # old style, quant-ph/0107012: yymm after the slash
        yymm = arxiv.split("/")[1][:4]
        stamp = f"{'19' if yymm[:2] > '50' else '20'}{yymm[:2]}-{yymm[2:]}"
    elif arxiv:
        yymm = arxiv.split(".")[0]
        stamp = f"20{yymm[:2]}-{yymm[2:]}"
    else:
        stamp = year
    return f"{stamp}_{surname}_{'-'.join(words)}.pdf"


def plan(todo, key) -> list[tuple[str, str, str | None, str]]:
    """(record id, url, arXiv id or None, target name), and prints what cannot be fetched."""
    out = []
    for rid, kind, ident, title in todo:
        year = rid.split("-")[1] if rid.split("-")[1].isdigit() else "nd"
        if kind == "arxiv":
            out.append((rid, f"https://arxiv.org/pdf/{ident}", ident, file_name(rid, ident, year, title)))
            continue
        work = openalex_work(ident, key)
        arxiv = f80dl.dc.arxiv_of(work)
        if arxiv:
            out.append((rid, f"https://arxiv.org/pdf/{arxiv}", arxiv, file_name(rid, arxiv, year, title)))
            continue
        pdf = ((work.get("best_oa_location") or {}).get("pdf_url") or "").strip()
        if pdf:
            out.append((rid, pdf, None, file_name(rid, None, year, title)))
        else:
            status = (work.get("open_access") or {}).get("oa_status", "unknown")
            print(f"no free copy known to OpenAlex: {rid} ({ident}; oa_status {status})")
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        todo = needs_copy(conn)
    finally:
        conn.close()
    key, fetcher, failed = f80dl.dc.openalex_key(), citations.PacedFetcher(), 0
    for rid, url, arxiv, name in plan(todo, key):
        target = PAPERS / name
        if target.exists():
            print(f"exists  {target.name}")
            continue
        if "--apply" not in args:
            print(f"planned {rid}: {url} -> {target.name}")
            continue
        try:
            if arxiv:
                data = fetcher(url, "application/pdf")
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EvidenceBasedDB)"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
        except Exception as ex:  # noqa: BLE001 -- reported; the others still run
            print(f"FAILED  {rid}: {type(ex).__name__}: {ex}")
            failed += 1
            continue
        if not data.startswith(b"%PDF"):
            print(f"FAILED  {rid}: not a PDF ({url})")
            failed += 1
            continue
        target.write_bytes(data)
        first = subprocess.run(["pdftotext", "-l", "1", str(target), "-"], capture_output=True).stdout.decode(
            "utf-8", "replace")
        stamp = ("stamp ok" if arxiv in first else "NO STAMP: check the first page by hand") if arxiv else "open access"
        print(f"saved   {rid}  {target.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes  "
              f"{stamp}  from {url}")
    print("APPLIED" if "--apply" in args else "DRY RUN: nothing downloaded. Re-run with --apply.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
