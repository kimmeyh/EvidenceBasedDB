#!/usr/bin/env python3
"""Sprint 12 Task G (F105, the F57 release for Sprint 12): select 400 records.

F57's order (relevance, team lead 2026-10-21): `hsbc-2026`, then the Dirac
platforms, then `qml`. Nothing is unread under the earlier contexts (the
plan's pre-flight, refreshed here), so the release is the 400 most-cited
`qml` records at `seen` or `screened` with no read row, counted by OpenAlex
exactly as F89 and F96 counted them (`scripts/sprint10_f89_slice.py`).

Left out (plan Q1 = 1: E's and F's records come on top of the 400, and no
record is read twice): the records F104 entered (its manifest), and the
records of the two earlier slices still unread, which had no free copy
(Sprint 10's F89 and Sprint 11's F96; reading them waits on a copy, F90 and
the hand-download list). E's records are under `qc`, not candidates. The
ledger (`manifests/sprint12_read_ledger.json`) is the final word on who
reads what.

Writes `manifests/sprint12_f105_slice.json`. `--dry-run` sends nothing.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("f89slice", Path(__file__).with_name("sprint10_f89_slice.py"))
f89slice = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f89slice)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OUT = ROOT / "manifests" / "sprint12_f105_slice.json"
F104 = ROOT / "manifests" / "sprint12_f104_roadmap.json"
EARLIER = (ROOT / "manifests" / "sprint10_f89_slice.json", ROOT / "manifests" / "sprint11_f96_slice.json")
SIZE = 400


def task_f_records() -> set[str]:
    return {e["record_id"] for e in json.loads(F104.read_text(encoding="utf-8"))["entered"]}


def no_free_copy_earlier(conn) -> set[str]:
    """The earlier slices' records still with no read row: each release
    found no free copy for them, so ranking them again spends slots on
    papers that cannot be read."""
    read = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_reads")}
    return {row["record_id"] for path in EARLIER
            for row in json.loads(path.read_text(encoding="utf-8"))["slice"]} - read


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    held = task_f_records()
    conn = connect(DB_PATH)
    try:
        before = f89slice.counts(conn)
        unreadable = no_free_copy_earlier(conn)
        cands = {rid: d for rid, d in f89slice.candidates(conn).items() if rid not in held | unreadable}
    finally:
        conn.close()
    print(f"counts {before}; Task F holds {len(held)}; left out with no free copy: {len(unreadable)}; "
          f"qml candidates left: {len(cands)}")
    if before["unread_under_earlier_contexts"]:
        print("records under an earlier context are unread: F57's order takes them first; not handled here")
        return 1
    if "--dry-run" in args:
        return 0
    key = f89slice.f80slice.dc.openalex_key()
    first = f89slice.f80slice.fetch_counts(sorted(set(cands.values())), key)
    found = {rid: (first[d], "OpenAlex") for rid, d in cands.items() if d in first}
    conn = connect(DB_PATH)
    try:
        journal = {rid: v.lower() for rid, v in conn.execute(
            "SELECT record_id, value FROM paper_probes WHERE field = 'version_of'")
            if rid in cands and rid not in found and not v.lower().startswith("10.48550/")}
    finally:
        conn.close()
    second = f89slice.f80slice.fetch_counts(sorted(set(journal.values())), key)
    found.update({rid: (second[d], "OpenAlex (journal DOI)") for rid, d in journal.items() if d in second})
    ranked = sorted(((n, rid, src) for rid, (n, src) in found.items()), key=lambda t: (-t[0], t[1]))
    top = ranked[:SIZE]
    OUT.write_text(json.dumps({
        "selected_on": date.today().isoformat(),
        "rule": ("F57 release for Sprint 12 (F105): the 400 most-cited qml records at seen or screened with no read "
                 "row, by relevance (team lead 2026-10-21); nothing unread remains under hsbc-2026 or the Dirac "
                 "platforms; Task F's records left out (plan Q1 = 1)"),
        "counts_before": before,
        "task_f_records_left_out": sorted(held),
        "no_free_copy_in_earlier_slices_left_out": sorted(unreadable),
        "slice": [{"record_id": rid, "cited_by_count": n, "source": src} for n, rid, src in top],
        "qml_candidates": len(cands), "counted": len(ranked),
        "counted_by": {src: sum(1 for *_, s in ranked if s == src) for src in ("OpenAlex", "OpenAlex (journal DOI)")},
        "not_counted": len(set(cands) - set(found)),
        "limit": ("records OpenAlex knows under neither their arXiv DOI nor a probed journal DOI are not ranked; "
                  "a highly cited one among them would be missed"),
    }, indent=1) + "\n", encoding="utf-8")
    print(f"counted {len(ranked)} of {len(cands)}; top {len(top)} from {top[0][0]} to {top[-1][0]} citations")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
