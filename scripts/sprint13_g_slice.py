#!/usr/bin/env python3
"""Sprint 13 Task G (F113): every paper record not yet read in full.

Team lead, 2026-10-25, at Manual Validation: "fully read all the papers that
are not marked 'read' and update all conclusions. That includes this sprints
551 adn 109 and any from prior runs." A record is read in full only when a
read says so and lists no parts:
- a `paper_reads` row of extent `full` (the coordinator's whole-paper read)
  whose detail names no part left out;
- a first-pass reader's file (manifests/*/group_*.json) that marked the
  paper `full` with no `partial_detail`, or with one that says the whole
  paper was read ("whole paper", "every page", "full paper", "entire")
  and names no exception ("except", "not read", "skimmed", "skipped").
A reader who marked `full` but listed sections (161 in Sprints 11 and 12,
121 in Sprint 13, before any correction) is not a full read: the store
entered many of those as "the whole source", and they are read again.

Each record lands in one bucket: `local` (a local copy, by
`store.recheck.local_pdf`, the manifests' reader files, or an arXiv id in a
file name), `fetch` (an arXiv id or a DOI the paced downloader may find a
free copy for), `github` (a code repository) or `none` (no copy, no id).
Read-only on the store. Writes `manifests/sprint13_g_slice.json`.

Usage:
  python scripts/sprint13_g_slice.py [--download-log <the downloads' output>]
"""
from __future__ import annotations

import glob
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import citations, connect, recheck, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
OUT = ROOT / "manifests" / "sprint13_g_slice.json"
LIBRARY = Path(r"D:\Data\Harold\EvidenceBasedDB")
WHOLE = re.compile(r"whole paper|whole source|every page|full paper|entire", re.I)
# A whole-paper note with an exception is not whole (the fresh-eyes review of a3b8074: "Whole paper read except
# related-work equations"; three e-mail reads marked full whose older thread was "not read").
PART = re.compile(r"\bexcept\b|not read|skimm|skipped", re.I)
ARXIV = re.compile(r"(\d{4}\.\d{4,5})")


def reader_files() -> tuple[dict[str, str], set[str]]:
    """Each record's file as a first-pass reader read it, and the records a
    reader read in full with no parts listed."""
    files, whole = {}, set()
    for f in sorted(glob.glob(str(ROOT / "manifests" / "*" / "group_*.json"))):
        for p in json.loads(Path(f).read_text(encoding="utf-8")).get("papers", []):
            rid = p.get("record_id")
            if not rid:
                continue
            if p.get("file"):
                files.setdefault(rid, p["file"])
            detail = (p.get("partial_detail") or "").strip()
            if p.get("read_extent") == "full" and (not detail or (WHOLE.search(detail) and not PART.search(detail))):
                whole.add(rid)
    return files, whole


def by_arxiv_id() -> dict[str, str]:
    out = {}
    for d in ("QMLPapers", "Papers", "QCiAuthorsPapers", "References", "Handoff-2026-10"):
        for p in glob.glob(str(LIBRARY / d / "**" / "*.pdf"), recursive=True):
            for m in ARXIV.findall(Path(p).name):
                out.setdefault(m, p)
    return out


def downloaded(log: Path | None) -> dict[str, str]:
    """Each record's copy saved by `sprint13_g_downloads.py`, from its log ("saved   <record>  <file name> ...");
    the saved names carry author and title, not the record id."""
    out = {}
    if log is None:
        return out
    for line in log.read_text(encoding="utf-8").splitlines():
        m = re.search(r"saved\s+(\S+)\s+(\S+\.pdf)\s", line)
        if m and (LIBRARY / "Papers" / m.group(2)).exists():
            out[m.group(1)] = str(LIBRARY / "Papers" / m.group(2))
    return out


def slice_rows(conn, log: Path | None = None) -> list[dict]:
    files, whole = reader_files()
    files.update(downloaded(log))
    whole |= {r for r, d in conn.execute("SELECT record_id, detail FROM paper_reads WHERE extent = 'full'")
              if not PART.search(d or "")}
    arxiv_files = by_arxiv_id()
    rows = []
    for rid, tier, access in conn.execute("SELECT record_id, tier, access FROM paper_fields ORDER BY record_id"):
        if rid in whole:
            continue
        access = access or ""
        parsed = citations.parse_access(access)
        local = recheck.local_pdf(access, parsed[1] if parsed else rid)
        if local is None:
            for p in recheck.local_paths(access):
                if Path(p).exists():
                    local = Path(p)
                    break
        if local is None and files.get(rid) and Path(files[rid]).exists():
            local = Path(files[rid])
        ax = ARXIV.search(access)
        if local is None and ax and ax.group(1) in arxiv_files:
            local = Path(arxiv_files[ax.group(1)])
        if local is not None:
            bucket = "local"
        elif "github.com" in access:
            bucket = "github"
        elif parsed:
            bucket = "fetch"
        else:
            bucket = "none"
        rows.append({"record_id": rid, "tier": tier, "bucket": bucket, "file": str(local) if local else None})
    return rows


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    log = Path(args[args.index("--download-log") + 1]) if "--download-log" in args else None
    with connect(DB_PATH) as conn:
        rows = slice_rows(conn, log)
        papers = conn.execute("SELECT count(*) FROM paper_fields").fetchone()[0]
    counts = Counter((r["tier"] == "read", r["bucket"]) for r in rows)
    out = {
        "selected_on": date.today().isoformat(),
        "rule": "Sprint 13 Task G (F113): every paper record not read in full (team lead 2026-10-25: \"fully "
                "read all the papers that are not marked 'read'\"); a reader's `full` that lists parts is not full",
        "counts": {"papers": papers, "not_full": len(rows),
                   **{f"{'read' if k[0] else 'not read'}|{k[1]}": v for k, v in sorted(counts.items())}},
        "slice": rows,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out["counts"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
