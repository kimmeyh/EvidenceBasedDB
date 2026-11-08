#!/usr/bin/env python3
r"""Sprint 17 Task E (F114, 10 papers): the local readers' briefs. INTAKE_WORKFLOW.md section 76.

The 10, fixed by id at the task start (Sprint 17 plan, Task E) and written to F144's exclusion list
(`manifests/sprint17_f144_batch/exclude.json`, on F144's branch), so F144 never selects them:

- g348, a new ledger group: the 2 PDFs the team lead saved into Papers on 2026-11-07, entered through the door by
  `manifests/sprint17_f114_new.json` (Sar et al., IEEE Access 2026; PSI's web article on the Aaronson-Ambainis
  conjecture). g335 to g347 are F144's ledger groups on its own branch, so Task E's new group is g348;
- g230's Pere v2 (team lead q3 = a, 2026-11-07: Pere v2 is one of Task E's 8 ledger papers);
- g295, all 5, the first group not yet read in full (g069's and g072's saved web pages hold the site's menus, not the
  article, Sprint 15; the OpenCyc and ds3lab sources are directories);
- g296's first 2, in ledger order.

A ledger group's records left out of its brief are left for a later release (`f117_build_groups.local_unread`).
Christophe Pere's list is unchanged since 399b022651 (checked 2026-11-07), so it adds no paper.

    python scripts/sprint17_f114_local.py           # what would be written
    python scripts/sprint17_f114_local.py --write   # g348 into the ledger and the four briefs (a brief handed to a
                                                    # reader is never rewritten)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
_spec = importlib.util.spec_from_file_location("g_ledger", ROOT / "scripts" / "sprint13_g_ledger.py")
g_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g_ledger)
_spec = importlib.util.spec_from_file_location("s16", ROOT / "scripts" / "sprint16_f114_local.py")
s16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s16)

LEDGER = g_ledger.LEDGER
LOCAL = s16.LOCAL
NEW_GROUP = "g348"
NEW = ("sar-2026-quantum-machine-learning-medical-image", "psi-2026-proof-aaronson-ambainis-conjecture")
FROM_LEDGER = {
    "g230": ("pere-2025-data-complexity-threshold-between-classical",),
    "g295": ("abrams-1999-quantum-algorithm-providing-exponential-speed",
             "aharonov-2005-adiabatic-quantum-computation-equivalent-standard",
             "ajagekar-2019-quantum-computing-energy-systems-optimization",
             "alarfaj-2022-credit-card-fraud-detection-state", "albash-2018-adiabatic-quantum-computation"),
    "g296": ("altshuler-2010-anderson-localization-makes-adiabatic-quantum",
             "amaro-2022-filtering-variational-quantum-algorithms-combinatorial"),
}


def plan(L: dict, conn) -> dict[str, list[dict]]:
    """group -> its brief's records, each {record_id, file}: the new papers' files from their access, the ledger
    papers' from the ledger."""
    out = {NEW_GROUP: [{"record_id": rid, "file": s16.local_file(conn, rid)} for rid in NEW]}
    for g, rids in FROM_LEDGER.items():
        where = {r["record_id"]: r for r in L[g]["records"]}
        missing = [r for r in rids if r not in where]
        if missing:
            raise ValueError(f"{g}: not in its ledger group: {missing}")
        out[g] = [where[r] for r in rids]
    return out


def check(groups: dict[str, list[dict]], L: dict) -> list[str]:
    rids = [r["record_id"] for rs in groups.values() for r in rs]
    bad = []
    if len(rids) != 10:
        bad.append(f"the briefs hold {len(rids)} papers, not 10")
    if len(rids) != len(set(rids)):
        bad.append("a record is planned twice")
    elsewhere = sorted({r["record_id"] for g, v in L.items() if g != NEW_GROUP for r in v["records"]} & set(NEW))
    if elsewhere:
        bad.append(f"a new paper is already in another ledger group: {elsewhere}")
    missing = [r["file"] for rs in groups.values() for r in rs if not Path(r["file"]).is_file()]
    if missing:
        bad.append(f"no local file: {missing}")
    return bad


def main(argv: list[str]) -> int:
    write = "--write" in argv
    L = s16.ledger()
    with connect(DB_PATH) as conn:
        groups = plan(L, conn)
        bad = check(groups, L)
        if bad:
            print("\n".join(bad))
            return 1
        if NEW_GROUP in L:
            if L[NEW_GROUP]["records"] != groups[NEW_GROUP]:
                raise ValueError(f"{NEW_GROUP} is in the ledger with other records; look again")
        else:
            print(f"{'add' if write else 'would add'} {NEW_GROUP} to the ledger")
            if write:
                full = json.loads(LEDGER.read_text(encoding="utf-8"))
                full["groups"][NEW_GROUP] = {"records": groups[NEW_GROUP]}
                LEDGER.write_text(json.dumps(full, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        for g, recs in groups.items():
            path = LOCAL / "briefs" / f"{g}.json"
            if path.exists() and [r["record_id"] for r in json.loads(path.read_text(encoding="utf-8"))["records"]] \
                    != [r["record_id"] for r in recs]:
                raise ValueError(f"{path.name} holds other records than this plan; look again")
            print(f"{'exists' if path.exists() else 'write' if write else 'would write'} {path.name}: "
                  f"{len(recs)} records: {', '.join(r['record_id'][:40] for r in recs)}")
            if write and not path.exists():
                brief = {"group": g, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(
                    conn, r["record_id"])} for r in recs]}
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"10 papers in {len(groups)} groups")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
