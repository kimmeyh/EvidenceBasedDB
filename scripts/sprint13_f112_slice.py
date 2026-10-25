#!/usr/bin/env python3
"""Sprint 13 Task F (F112, the F57 release for Sprint 13): every readable
`qml` record, in citation order.

Plan Q1 = 1 (team lead, 2026-10-25): all of them, not 800. F57's order
(relevance, team lead 2026-10-21): `hsbc-2026`, then the Dirac platforms,
then `qml`; nothing is unread under the earlier contexts (refreshed here).
The candidates are every `qml` record at `seen` or `screened` with no read
row, counted by OpenAlex exactly as F89, F96 and F105 counted them
(`scripts/sprint10_f89_slice.py`), most cited first, so a stop inside the
task cuts the least cited. Records OpenAlex does not count come last, by
id: the release reads them too.

Left out: the records of the three earlier slices still unread, which had
no free copy (Sprint 10's F89, Sprint 11's F96, Sprint 12's F105; reading
them waits on a copy, F90 and the hand-download list). The ledger
(`manifests/sprint13_read_ledger.json`) is the final word on who reads
what.

Writes `manifests/sprint13_f112_slice.json`. `--dry-run` sends nothing.
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
OUT = ROOT / "manifests" / "sprint13_f112_slice.json"
EARLIER = (ROOT / "manifests" / "sprint10_f89_slice.json", ROOT / "manifests" / "sprint11_f96_slice.json",
           ROOT / "manifests" / "sprint12_f105_slice.json")


def no_free_copy_earlier(conn) -> set[str]:
    """The earlier slices' records still with no read row: each release
    found no free copy for them."""
    read = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_reads")}
    return {row["record_id"] for path in EARLIER
            for row in json.loads(path.read_text(encoding="utf-8"))["slice"]} - read


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        before = f89slice.counts(conn)
        unreadable = no_free_copy_earlier(conn)
        cands = {rid: d for rid, d in f89slice.candidates(conn).items() if rid not in unreadable}
    finally:
        conn.close()
    print(f"counts {before}; left out with no free copy: {len(unreadable)}; qml candidates: {len(cands)}")
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
    uncounted = sorted(set(cands) - set(found))
    rows = ([{"record_id": rid, "cited_by_count": n, "source": src} for n, rid, src in ranked]
            + [{"record_id": rid, "cited_by_count": None, "source": "not counted"} for rid in uncounted])
    OUT.write_text(json.dumps({
        "selected_on": date.today().isoformat(),
        "rule": ("F57 release for Sprint 13 (F112): every qml record at seen or screened with no read row (plan "
                 "Q1 = 1), most cited first by OpenAlex, uncounted records last by id; nothing unread remains under "
                 "hsbc-2026 or the Dirac platforms; the earlier slices' no-copy records left out"),
        "counts_before": before,
        "no_free_copy_in_earlier_slices_left_out": sorted(unreadable),
        "slice": rows,
        "qml_candidates": len(cands), "counted": len(ranked),
        "counted_by": {src: sum(1 for *_, s in ranked if s == src) for src in ("OpenAlex", "OpenAlex (journal DOI)")},
        "not_counted": len(uncounted),
    }, indent=1) + "\n", encoding="utf-8")
    print(f"slice {len(rows)}: counted {len(ranked)} ({ranked[0][0]} to {ranked[-1][0]} citations), "
          f"not counted {len(uncounted)}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
