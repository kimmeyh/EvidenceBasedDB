#!/usr/bin/env python3
r"""Sprint 14 Task F (F114 at 50 papers, Q1 = 2): the local readers' briefs, C's ledger group, and Boyd's resume.

F's 50 papers (plan, Q1 = 2): abbas-2020-power-quantum-neural-networks (g079), the completion of
boyd-2004-convex-optimization (g103), then the next 48 records in ledger order from g103 with no cloud result
(g103 to g113). Task C's 4 new papers (F123, INTAKE_WORKFLOW.md section 57) are read beside them as ledger group
NEW_GROUP. Each group's brief lists only the papers its local reader reads (the reader prompt is
`manifests/sprint14_f114_reads/READER_PROMPT.md`), with the record's stored assertions as the store holds them now.

Boyd's cloud read was labeled full and sampled the book (the team lead kept it unread, 2026-10-27). Its entry goes in
the reader's `partial\` folder, never `done\` (a `done\` file is never read again), with `last_page_read` 0: the
reader reads every page from the first, keeping the cloud read's assertions as a start and checking each on its page.

    python scripts/sprint14_f114_local.py           # what would be written
    python scripts/sprint14_f114_local.py --write   # the ledger group, the briefs and Boyd's seed
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
_spec = importlib.util.spec_from_file_location("g_ledger", ROOT / "scripts" / "sprint13_g_ledger.py")
g_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g_ledger)

LEDGER = g_ledger.LEDGER
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114")
LOCAL = WORK / "local"
F123 = ROOT / "manifests" / "sprint14_f123_roadmap.json"
NEW_GROUP = "g330"
ABBAS = "abbas-2020-power-quantum-neural-networks"
BOYD = "boyd-2004-convex-optimization"
# The next 48 in ledger order from g103 with no cloud result: the plan's first and last.
FIRST, LAST = "bucher-2024-towards-robust-benchmarking-quantum-optimization", \
    "chen-2026-photonic-quantum-enhanced-knowledge-distillation"
BOYD_NOTE = ("Seeded from F114's cloud read (work\\f114\\results), which was labeled full and sampled the book; the team "
             "lead kept it unread (2026-10-27). Read every page from page 1. Keep each of its verdicts and assertions "
             "only after checking it on its page; add what it missed.")


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def cloud_results() -> set[str]:
    return {p.stem for p in (WORK / "results").glob("*.json")}


def new_group_records() -> list[dict]:
    """Task C's 4 entered papers, each with the local file its access names."""
    out = []
    for e in json.loads(F123.read_text(encoding="utf-8"))["entered"]:
        out.append({"record_id": e["record_id"],
                    "file": str(Path(r"D:\Data\Harold\EvidenceBasedDB\Papers") / e["local_copy"])})
    return out


def plan(L: dict) -> dict[str, list[dict]]:
    """group -> the records its local reader reads, in ledger order."""
    have = cloud_results() - {BOYD}  # Boyd's cloud read is not taken as a read
    order = [(g, r) for g, v in sorted(L["groups"].items()) for r in v["records"]]
    out: dict[str, list[dict]] = {}
    for g, r in order:
        if r["record_id"] == ABBAS:
            out.setdefault(g, []).append(r)
    started = False
    for g, r in order:
        if g < "g103":
            continue
        rid = r["record_id"]
        started = started or rid in (BOYD, FIRST)
        if started and (rid == BOYD or rid not in have):
            out.setdefault(g, []).append(r)
        if rid == LAST:
            break
    if NEW_GROUP in L["groups"]:
        out[NEW_GROUP] = L["groups"][NEW_GROUP]["records"]
    return out


def check(groups: dict[str, list[dict]]) -> list[str]:
    rids = [r["record_id"] for rs in groups.values() for r in rs]
    f = [r for g, rs in groups.items() if g != NEW_GROUP for r in rs]
    bad = []
    if len(f) != 50:
        bad.append(f"F holds {len(f)} papers, not 50")
    if len(rids) != len(set(rids)):
        bad.append("a record is planned twice")
    missing = [r["file"] for rs in groups.values() for r in rs if not Path(r["file"]).exists()]
    if missing:
        bad.append(f"no local file: {missing}")
    return bad


def boyd_seed() -> tuple[dict, dict]:
    entry = json.loads((WORK / "results" / f"{BOYD}.json").read_text(encoding="utf-8"))["papers"][0]
    entry = {**entry, "read_extent": "partial", "not_read": "every page, from page 1 (see progress.json)"}
    progress = {"record_id": BOYD, "pages": entry["pages"], "last_page_read": 0, "text_file": "", "note": BOYD_NOTE}
    return entry, progress


def main(argv: list[str]) -> int:
    write = "--write" in argv
    L = ledger()
    if NEW_GROUP not in L["groups"]:
        held = {r["record_id"] for v in L["groups"].values() for r in v["records"]}
        recs = new_group_records()
        if any(r["record_id"] in held for r in recs):
            print("a Task C record is already in the ledger; nothing written")
            return 1
        if sorted(L["groups"])[-1] >= NEW_GROUP:
            print(f"the ledger already reaches {sorted(L['groups'])[-1]}; nothing written")
            return 1
        L["groups"][NEW_GROUP] = {"records": recs}
        print(f"{'add' if write else 'would add'} {NEW_GROUP}: {[r['record_id'] for r in recs]}")
        if write:
            LEDGER.write_text(json.dumps(L, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    groups = plan(L)
    bad = check(groups)
    if bad:
        print("\n".join(bad))
        return 1
    with connect(DB_PATH) as conn:
        for g, recs in groups.items():
            path = LOCAL / "briefs" / f"{g}.json"
            brief = {"group": g, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(conn, r["record_id"])}
                                             for r in recs]}
            print(f"{'exists' if path.exists() else 'write' if write else 'would write'} {path.name}: "
                  f"{len(recs)} records")
            if write and not path.exists():  # a brief handed to a reader is never rewritten
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    g = next(g for g, recs in groups.items() if any(r["record_id"] == BOYD for r in recs))
    tmp = LOCAL / f"tmp_{g}"
    if not (tmp / "progress.json").exists() and not (tmp / "done" / f"{BOYD}.json").exists():
        entry, progress = boyd_seed()
        print(f"{'seed' if write else 'would seed'} {BOYD} in tmp_{g}\\partial ({len(entry['assertions'])} assertions "
              f"kept as a start, last_page_read 0)")
        if write:
            (tmp / "partial").mkdir(parents=True, exist_ok=True)
            (tmp / "partial" / f"{BOYD}.json").write_text(json.dumps(entry, indent=1, ensure_ascii=False) + "\n",
                                                         encoding="utf-8")
            (tmp / "progress.json").write_text(json.dumps(progress, indent=1) + "\n", encoding="utf-8")
    print(f"{sum(len(r) for g, r in groups.items() if g != NEW_GROUP)} F papers in "
          f"{len([g for g in groups if g != NEW_GROUP])} groups; {NEW_GROUP} holds Task C's "
          f"{len(groups.get(NEW_GROUP, []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
