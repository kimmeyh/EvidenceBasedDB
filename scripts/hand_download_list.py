#!/usr/bin/env python3
"""The hand-download list, computed from the store (intake sections 39, 40).

Team lead, 2026-10-22 (Sprint 11 Manual Validation, Q2): "Keep an on going
list of these in relative priority order"; and later the same day: "include
the best practice naming suggestion for each of the papers and why we think
the paper is important. The list details need to be reproducible easily at
any time". The list is a determinate fact, so it is computed, never kept by
hand. A record is on it when its newest updated-reason segment naming the
list puts it there (not "NOT for the hand-download list"), it is not
`read`, and its `access` names no local copy. A file linked from
`Papers\\`, or a read, takes it off.

Priority order (section 40): (1) named for a question the team lead set;
(2) fraud, the active consumer's domain (`hsbc-2026`, or F62's fraud
stream); (3) `qml` or `qc`; (4) everything else. Within a group, by the
OpenAlex citation count recorded at selection, highest first (F57's slice
manifests, or F62's disposition). PRIORITY_FIRST moves a record to the top
when the team lead asks for it sooner.

Each entry names its target file under section 3's convention, as F62's
`discover_candidates.target_name` builds it.

    python scripts/hand_download_list.py
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("dc", Path(__file__).with_name("discover_candidates.py"))
dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dc)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
BASE = Path(r"D:\Data\Harold\EvidenceBasedDB")
# Record ids the team lead moved to the top, in their order (none yet).
PRIORITY_FIRST: tuple[str, ...] = ()
GROUPS = ("named for a question the team lead set", "fraud, the active consumer's domain", "QML or quantum computing",
          "other")
# What each selecting task was for, by its F#.
PURPOSE = {
    "F78": "the ceiling-estimation group, read in full for Phase 2's F108 question (Sprint 9 plan Q3 = 1)",
    "F89": "F57's relevance ranking: among the most-cited unread qml records (Sprint 10 release)",
    "F96": "F57's relevance ranking: among the 200 most-cited unread qml records (Sprint 11 release)",
    "Q3": "F62 discovery: ranked high in its stream, no free copy found",
}

_ON = re.compile(r"hand-download list", re.I)
_OFF = re.compile(r"NOT for the hand-download list")
_TASK = re.compile(r"\b(F\d+|Q3 = 1)\)")
_DATE = re.compile(r", (\d{4}(?:-\d{2}){0,2})$")
_CITES = re.compile(r"\((\d+) citations")
_STREAM = re.compile(r"(\w+) stream rank (\d+)")


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
            if row["cited_by_count"] is not None:  # an uncounted row never hides another slice's count
                out[row["record_id"]] = row["cited_by_count"]
    return out


def target(title: str, provenance: str, why: str) -> str:
    """Where the file goes and what it is called (intake section 3)."""
    date = (_DATE.search(provenance.strip()) or [None, ""])[1]
    author = provenance.split(",")[0].strip()
    c = {"title": title, "first_author": author, "date": date, "year": date[:4],
         "type": "book" if re.search(r"\bbook\b", why, re.I) else "article",
         "publisher": (re.search(r"selected for reading and NOT read: (?:a )?(\w+)", why) or [None, ""])[1]}
    return f"{dc.target_folder(c)}\\{dc.target_name(c)}"


def group(rid_contexts: set[str], disposition: str, why: str) -> int:
    if "F78" in why:
        return 0
    if "hsbc-2026" in rid_contexts or "fraud stream" in disposition:
        return 1
    if rid_contexts & {"qml", "qc"}:
        return 2
    return 3


def ranked(conn, counts: dict[str, int]) -> list[dict]:
    rows = conn.execute("SELECT r.id, r.value, r.provenance, r.updated_reason, p.tier, p.access, p.disposition "
                        "FROM records r JOIN paper_fields p ON p.record_id = r.id "
                        "WHERE r.updated_reason LIKE '%hand-download%'").fetchall()
    items = []
    for rid, title, provenance, reason, tier, access, disposition in rows:
        why = on_list(reason)
        if why is None or tier == "read" or recheck.local_paths(access or ""):
            continue
        contexts = {c for (c,) in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))}
        n = counts.get(rid)
        if n is None and (m := _CITES.search(disposition or "")):
            n = int(m.group(1))
        task = (_TASK.search(why) or [None, ""])[1].replace(" = 1", "")
        stream = _STREAM.search(disposition or "")
        items.append({
            "id": rid, "citation": provenance, "access": access, "no_copy": why, "cited_by_count": n,
            "group": group(contexts, disposition or "", why), "contexts": sorted(contexts),
            "target": target(title, provenance or "", why),
            "selected_by": PURPOSE.get(task, task or "not named") + (
                "" if not stream else f" ({stream.group(1)} stream, rank {stream.group(2)})" if task == "Q3"
                else f"; also ranked by F62 discovery ({stream.group(1)} stream, rank {stream.group(2)})"),
        })

    def key(item):
        rid = item["id"]
        first = PRIORITY_FIRST.index(rid) if rid in PRIORITY_FIRST else len(PRIORITY_FIRST)
        n = item["cited_by_count"]
        # A record no slice counted (Sprint 13's uncounted 389) comes after every counted one, not among the zeros.
        return (first, item["group"], n is None, -(n or 0), rid)
    return sorted(items, key=key)


def render(items: list[dict]) -> str:
    lines = [f"Hand-download list: {len(items)} records, highest priority first (computed from the store; "
             "intake sections 39 and 40).",
             f"Save each file under {BASE}\\ at its target path; F95's next release links and reads it.", ""]
    current = None
    for i, item in enumerate(items, 1):
        if item["group"] != current:
            current = item["group"]
            lines.append(f"-- {GROUPS[current]} --")
        n = item["cited_by_count"]
        cites = "no count recorded" if n is None else f"{n} citations (OpenAlex, at selection)"
        lines += [f"{i:>3}. {item['citation']}",
                  f"     Target: {item['target']}",
                  f"     Why it matters: {item['selected_by']}; contexts {', '.join(item['contexts']) or 'none'}; "
                  f"{cites}",
                  f"     No copy: {item['no_copy']}"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    conn = connect(DB_PATH)
    try:
        items = ranked(conn, slice_counts(ROOT / "manifests"))
    finally:
        conn.close()
    print(render(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
