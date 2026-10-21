#!/usr/bin/env python3
"""Sprint 10 Task I (F89, the F57 release for Sprint 10): select 74 records.

F57's order: `hsbc-2026`, then the Dirac platforms, then `qml`. On
2026-10-18 no record under `hsbc-2026` or `platform:dirac-3s` is at `seen`
or `screened`, and every one under `platform:dirac-3` or `platform:dirac-1`
was screened by F80 or entered by F84. So the release is the 74 most-cited
`qml` records at `seen` or `screened` that have NO read row yet (a record
F80 screened and refused keeps its reason and is not re-read). The nine
Dirac-1 records do not count toward the 74 (plan Q3 = 1).

Counts come from OpenAlex exactly as F80's slice took them
(`scripts/sprint9_f80_slice.py`: batches of 50 DOIs, arXiv records by their
DataCite DOI, a second pass by a probed journal DOI; the key only in the
Authorization header, never logged). Writes
`manifests/sprint10_f89_slice.json`, a record of what this sprint chose,
not a store field. `--dry-run` sends nothing.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80slice", Path(__file__).with_name("sprint9_f80_slice.py"))
f80slice = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80slice)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OUT = ROOT / "manifests" / "sprint10_f89_slice.json"
SIZE = 74
EARLIER = ("hsbc-2026", "platform:dirac-3", "platform:dirac-3s", "platform:dirac-1")


def counts(conn) -> dict[str, int]:
    """The F57 count, refreshed: all records at seen or screened, and those never read."""
    total = conn.execute("SELECT COUNT(*) FROM paper_fields WHERE tier IN ('seen', 'screened')").fetchone()[0]
    never = conn.execute("SELECT COUNT(*) FROM paper_fields p WHERE tier IN ('seen', 'screened') AND NOT EXISTS "
                         "(SELECT 1 FROM paper_reads r WHERE r.record_id = p.record_id)").fetchone()[0]
    earlier = conn.execute(
        "SELECT COUNT(DISTINCT p.record_id) FROM paper_fields p JOIN record_contexts x ON x.record_id = p.record_id "
        f"WHERE p.tier IN ('seen', 'screened') AND x.context_id IN ({','.join('?' * len(EARLIER))}) AND NOT EXISTS "
        "(SELECT 1 FROM paper_reads r WHERE r.record_id = p.record_id)", EARLIER).fetchone()[0]
    return {"seen_or_screened": total, "never_read": never, "unread_under_earlier_contexts": earlier}


def candidates(conn) -> dict[str, str]:
    read = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_reads")}
    return f80slice.qml_candidates(conn, read)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        before = counts(conn)
        cands = candidates(conn)
    finally:
        conn.close()
    print(f"counts {before}; qml candidates with an identifier and no read: {len(cands)}")
    if before["unread_under_earlier_contexts"]:
        print("records under an earlier context are unread: F57's order takes them first; not handled here")
        return 1
    if "--dry-run" in args:
        return 0
    key = f80slice.dc.openalex_key()
    first = f80slice.fetch_counts(sorted(set(cands.values())), key)
    found = {rid: (first[d], "OpenAlex") for rid, d in cands.items() if d in first}
    conn = connect(DB_PATH)
    try:
        journal = {rid: v.lower() for rid, v in conn.execute(
            "SELECT record_id, value FROM paper_probes WHERE field = 'version_of'")
            if rid in cands and rid not in found and not v.lower().startswith("10.48550/")}
    finally:
        conn.close()
    second = f80slice.fetch_counts(sorted(set(journal.values())), key)
    found.update({rid: (second[d], "OpenAlex (journal DOI)") for rid, d in journal.items() if d in second})
    ranked = sorted(((n, rid, src) for rid, (n, src) in found.items()), key=lambda t: (-t[0], t[1]))
    top = ranked[:SIZE]
    OUT.write_text(json.dumps({
        "selected_on": date.today().isoformat(),
        "rule": ("F57 release for Sprint 10 (F89): the 74 most-cited qml records at seen or screened with no read "
                 "row; nothing unread remains under hsbc-2026 or the Dirac platforms; the nine Dirac-1 records "
                 "(F84) do not count (plan Q3 = 1)"),
        "counts_before": before,
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
