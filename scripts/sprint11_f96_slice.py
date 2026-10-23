#!/usr/bin/env python3
"""Sprint 11 Task G (F96, the F57 release for Sprint 11): select 200 records.

F57's order (relevance, team lead 2026-10-21: "switch back to the relavance
ranking"): `hsbc-2026`, then the Dirac platforms, then `qml`. Nothing is
unread under the earlier contexts (Sprint 10 Task I, refreshed here), so the
release is the 200 most-cited `qml` records at `seen` or `screened` with no
read row, counted by OpenAlex exactly as F89 counted them
(`scripts/sprint10_f89_slice.py`).

Records Tasks E and F read are left out (plan Q1 = 1: theirs come on top of
the 200, and no record is read twice): every record whose arXiv id appears in
the name of a PDF in `Papers\\` that no record's `access` names, and the
records of the team lead's list (`F97_ARXIV`). The ledger
(`manifests/sprint11_read_ledger.json`) is the final word on who reads what.

Writes `manifests/sprint11_f96_slice.json`. `--dry-run` sends nothing.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402

_spec = importlib.util.spec_from_file_location("f89slice", Path(__file__).with_name("sprint10_f89_slice.py"))
f89slice = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f89slice)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OUT = ROOT / "manifests" / "sprint11_f96_slice.json"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
SIZE = 200
# The team lead's list for Task F (F97 card, 2026-10-21).
F97_ARXIV = ("2610.24426", "2509.16410", "2610.10629", "2610.00841", "2509.03505", "2609.17488")
_ARXIV_IN_NAME = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?!\d)")


def unnamed_pdfs(conn) -> list[str]:
    """PDF names in Papers\\ that no record's access names (F95 step 1)."""
    access = " ".join(a or "" for (a,) in conn.execute("SELECT access FROM paper_fields")).lower()
    return sorted(f for f in os.listdir(PAPERS) if f.lower().endswith(".pdf")
                  and f.lower() not in access and os.path.splitext(f)[0].lower() not in access)


def task_f_records(conn) -> set[str]:
    """Record ids Task F reads: arXiv ids in unnamed PDF names, and the team lead's list."""
    ids = set(F97_ARXIV)
    for name in unnamed_pdfs(conn):
        ids.update(_ARXIV_IN_NAME.findall(name))
    out = set()
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields"):
        parsed = citations.parse_access(access or "")
        if parsed and parsed[0] == "arxiv" and parsed[1].split("v")[0] in ids:
            out.add(rid)
    return out


def no_free_copy_last_release(conn) -> set[str]:
    """F89's slice records still with no read row: Sprint 10 found no free
    copy for them (F90's eight, waiting on the team lead's downloads, and the
    retracted Valdez 2023). Ranking them again would spend slots on papers
    that cannot be read; F95 reads F90's once they are in Papers\\."""
    f89 = json.loads((ROOT / "manifests" / "sprint10_f89_slice.json").read_text(encoding="utf-8"))["slice"]
    read = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_reads")}
    return {row["record_id"] for row in f89} - read


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        before = f89slice.counts(conn)
        held = task_f_records(conn)
        unreadable = no_free_copy_last_release(conn)
        print(f"left out as unreadable since Sprint 10: {len(unreadable)}")
        cands = {rid: d for rid, d in f89slice.candidates(conn).items() if rid not in held | unreadable}
    finally:
        conn.close()
    print(f"counts {before}; Task F holds {len(held)}; qml candidates left: {len(cands)}")
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
        "rule": ("F57 release for Sprint 11 (F96): the 200 most-cited qml records at seen or screened with no read "
                 "row, by relevance (team lead 2026-10-21); nothing unread remains under hsbc-2026 or the Dirac "
                 "platforms; Task F's records left out (plan Q1 = 1)"),
        "counts_before": before,
        "task_f_records_left_out": sorted(held),
        "no_free_copy_since_sprint_10_left_out": sorted(unreadable),
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
