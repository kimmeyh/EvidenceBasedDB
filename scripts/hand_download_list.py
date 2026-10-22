#!/usr/bin/env python3
"""The hand-download list, computed from the store (intake section 39).

Team lead, 2026-10-22 (Sprint 11 Manual Validation, Q2): "Keep an on going
list of these in relative priority order". The list is a determinate fact,
so it is computed, never kept by hand. A record is on it when its updated
reason puts it on the hand-download list (and not "NOT for the
hand-download list"), it is not `read`, and its `access` names no local
copy. A file linked from `Papers\\`, or a read, takes it off.

Priority order: first the records named for a question the team lead set
(selected outside a ranked F57 release, so they carry no count), then the
rest by the OpenAlex citation count recorded when F57's relevance ranking
selected them (`manifests/*_slice.json`), highest first. PRIORITY_FIRST
moves a record to the top when the team lead asks for it sooner.

    python scripts/hand_download_list.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
# Record ids the team lead moved to the top, in their order (none yet).
PRIORITY_FIRST: tuple[str, ...] = ()

_ON = re.compile(r"hand-download list", re.I)
_OFF = re.compile(r"NOT for the hand-download list")


def on_list(reason: str | None) -> str | None:
    """The newest reason segment naming the list, or None when the newest
    one takes the record off it (or none names it)."""
    segs = [s.strip() for s in (reason or "").split(" | ") if _ON.search(s)]
    if not segs or _OFF.search(segs[-1]):
        return None
    return segs[-1]


def slice_counts(manifests: Path) -> dict[str, int]:
    """OpenAlex counts recorded by every F57 release's slice manifest."""
    out: dict[str, int] = {}
    for path in sorted(manifests.glob("*_slice.json")):
        for row in json.loads(path.read_text(encoding="utf-8")).get("slice", []):
            out[row["record_id"]] = row["cited_by_count"]
    return out


def ranked(conn, counts: dict[str, int]) -> list[dict]:
    rows = conn.execute("SELECT r.id, r.provenance, r.updated_reason, p.tier, p.access FROM records r "
                        "JOIN paper_fields p ON p.record_id = r.id WHERE r.updated_reason LIKE '%hand-download%'")
    items = []
    for rid, provenance, reason, tier, access in rows:
        why = on_list(reason)
        if why is None or tier == "read" or recheck.local_paths(access or ""):
            continue
        items.append({"id": rid, "citation": provenance, "access": access, "why": why,
                      "cited_by_count": counts.get(rid)})

    def key(item):
        rid, n = item["id"], item["cited_by_count"]
        first = PRIORITY_FIRST.index(rid) if rid in PRIORITY_FIRST else len(PRIORITY_FIRST)
        return (first, n is not None, -(n or 0), rid)
    return sorted(items, key=key)


def main(argv: list[str] | None = None) -> int:
    conn = connect(DB_PATH)
    try:
        items = ranked(conn, slice_counts(ROOT / "manifests"))
    finally:
        conn.close()
    print(f"Hand-download list: {len(items)} records, highest priority first. Save each into {PAPERS}\\")
    for i, item in enumerate(items, 1):
        n = item["cited_by_count"]
        rank = "named for a question" if n is None else f"{n} citations (OpenAlex, at selection)"
        print(f"{i:>3}. {item['citation']}")
        print(f"     {item['access']}; {rank}")
        print(f"     {item['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
