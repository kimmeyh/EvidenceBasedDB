#!/usr/bin/env python3
"""Sprint 13 Task G (F113): where each group stands, computed from the files, so any session can pick up the work.

Team lead, 2026-10-26: "make future agent runs setup to not loose anything if
we cross current or weekly session limits and can re-start them so that they
know what was done and what was not done". A reader saves each finished paper
and its notes on a long paper in its scratch folder (the reader prompt's
"Progress and restart"); this script reads those files, the reader files and
the reviews, and the store's reads, and stores nothing of its own (CLAUDE.md:
determinate facts are computed).

A group is, by the last step it has reached:
- applied: every record has its Task G read in the store;
- reviewed: the coordinator's review is in manifests/sprint13_g_reviews;
- read: the reader's group file is written;
- reading: the scratch folder holds saved papers or notes (k of n done, and the page reached);
- started: the scratch folder exists, with nothing saved (a reader on the prompt before 2026-10-26, or one
  stopped before its first save);
- not started.

Read-only. Usage:
  python scripts/sprint13_g_status.py            one line per group not yet applied, then the counts
  python scripts/sprint13_g_status.py --all      every group
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
REVIEWS = ROOT / "manifests" / "sprint13_g_reviews"
WORK = Path(r"C:\Users\kimme\AppData\Local\Temp\claude\D--Data-Harold-github-EvidenceBasedDB\s13g")
TAG = "Sprint 13 Task G, F113"


def applied_records() -> set[str]:
    """Records whose Task G first-pass read is in the store (full_read_apply.read_detail names the tag)."""
    if not DB_PATH.exists():
        return set()
    with connect(DB_PATH) as conn:
        return {r[0] for r in conn.execute("SELECT record_id FROM paper_reads WHERE detail LIKE ?", (f"%{TAG}, group %",))}


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


def state(g: str, records: list[str], applied: set[str]) -> tuple[str, str]:
    if records and set(records) <= applied:
        return "applied", ""
    if (REVIEWS / f"{g}.json").exists():
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
    groups = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]
    applied = applied_records()
    counts = Counter()
    for g, body in groups.items():
        name, detail = state(g, [r["record_id"] for r in body["records"]], applied)
        counts[name] += 1
        if "--all" in args or name not in ("applied", "not started"):
            print(f"{g}  {name}" + (f"  ({detail})" if detail else ""))
    print(", ".join(f"{n} {k}" for k, n in counts.most_common()) + f"; {len(groups)} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
