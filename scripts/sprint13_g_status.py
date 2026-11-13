#!/usr/bin/env python3
"""Sprint 13 Task G (F113): where each group stands, computed from the files, so any session can pick up the work.

Team lead, 2026-10-26: "make future agent runs setup to not loose anything if
we cross current or weekly session limits and can re-start them so that they
know what was done and what was not done". A reader saves each finished paper
and its notes on a long paper in its scratch folder (the reader prompt's
"Progress and restart"); this script reads those files, the reader files and
the reviews, and the store's reads, and stores nothing of its own (CLAUDE.md:
determinate facts are computed).

F125 (Sprint 15 Task C): the readers' scratch folders and group files are F114's local ones,
`work\\f114\\local\\` (Sprint 13's Temp folder was cleared after Sprint 13), and a group counts as applied
when each record has a read row naming its group, whatever the sprint's tag. A re-entry group ("g113-r1",
from a local brief) is listed after the ledger's groups.

A group is, by the last step it has reached:
- applied: every record has a read in the store that names the group;
- reviewed: the coordinator's review is in manifests/sprint13_g_reviews;
- read: the reader's group file is written;
- reading: the scratch folder holds saved papers or notes (k of n done, and the page reached);
- started: the scratch folder exists, with nothing saved (a reader on the prompt before 2026-10-26, or one
  stopped before its first save);
- not started;
- superseded: never started, and its papers moved to one-paper groups (q20 = a, 2026-11-09); the ledger's
  `superseded` note names each paper and its new group.

Read-only. Usage:
  python scripts/sprint13_g_status.py            one line per group not yet applied, then the counts
  python scripts/sprint13_g_status.py --all      every group
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
REVIEWS = ROOT / "manifests" / "sprint13_g_reviews"
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local")
GROUP = re.compile(r", group (g\d+(?:-r\d+)?)\)")  # full_read_apply.read_detail ends its tag with the group


def applied_records() -> set[tuple[str, str]]:
    """(group, record) for each first-pass read in the store that names its group (full_read_apply.read_detail)."""
    if not DB_PATH.exists():
        raise SystemExit(f"{DB_PATH}: no store, so no group can be called applied")
    with connect(DB_PATH) as conn:
        return {(m[1], r[0]) for r in conn.execute("SELECT record_id, detail FROM paper_reads WHERE detail LIKE "
                                                   "'%, group g%'") if (m := GROUP.search(r[1]))}


def reading(tmp: Path, records: list[str]) -> str:
    done = sorted(p.stem for p in (tmp / "done").glob("*.json")) if (tmp / "done").is_dir() else []
    partial = sorted(p.stem for p in (tmp / "partial").glob("*.json")) if (tmp / "partial").is_dir() else []
    if not done and not partial:
        return ""
    where = ""
    try:
        progress = json.loads((tmp / "progress.json").read_text(encoding="utf-8"))
        if progress.get("record_id") not in done:
            where = f"; {progress.get('record_id')} at page {progress.get('last_page_read')} of {progress.get('pages')}"
    except (OSError, ValueError):
        pass
    return f"{len([r for r in done if r in records])} of {len(records)} papers saved{where}"


def state(g: str, records: list[str], applied: set[tuple[str, str]],
          superseded: dict | None = None) -> tuple[str, str]:
    if superseded:  # q20 = a (2026-11-09): its papers moved to one-paper groups, which report for themselves
        moved = [r["moved_to"] for r in superseded["records"]]
        return "superseded", f"{len(moved)} papers moved to {moved[0]} to {moved[-1]}"
    if records and all((g, r) in applied for r in records):
        return "applied", ""
    if (REVIEWS / f"{g}.json").exists():
        unread = json.loads((REVIEWS / f"{g}.json").read_text(encoding="utf-8")).get("unread") or {}
        rest = [r for r in records if (g, r) not in applied]
        if len(rest) < len(records) and set(rest) <= set(unread):
            return "applied", f"{len(rest)} left unread"
        return "reviewed", ""
    if (WORK / "reads" / f"group_{g}.json").exists():
        return "read", ""
    tmp = WORK / f"tmp_{g}"
    if tmp.is_dir():
        far = reading(tmp, records)
        return ("reading", far) if far else ("started", "nothing saved")
    return "not started", ""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]
    groups = {g: [r["record_id"] for r in body["records"]] for g, body in ledger.items()}
    for brief in sorted((WORK / "briefs").glob("g*-r*.json")):
        groups[brief.stem] = [r["record_id"] for r in json.loads(brief.read_text(encoding="utf-8"))["records"]]
    applied = applied_records()
    counts = Counter()
    for g, records in groups.items():
        name, detail = state(g, records, applied, ledger.get(g, {}).get("superseded"))
        counts[name] += 1
        if "--all" in args or name not in ("applied", "not started", "superseded"):
            print(f"{g}  {name}" + (f"  ({detail})" if detail else ""))
    print(", ".join(f"{n} {k}" for k, n in counts.most_common()) + f"; {len(groups)} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
