#!/usr/bin/env python3
r"""Sprint 18 Task D (F114, 30 papers): the new ledger groups and the local readers' briefs.

The 30, in the plan's order (Sprint 18 plan, Task D), fixed by id here:

- 4 new papers, one ledger group each (q20 = a's one-paper shape), named by `sprint13_g_ledger.new_groups`
  (F149, Task A: above the highest gNNN, so g510 onward today):
  - Huang 2023, the PDF the team lead saved into Papers on 2026-11-07. It is the stored record
    `huang-2023-noise-resilient-single-pixel-compressive` (at `seen`, access a Research Square DOI), so it is linked,
    not entered: the read's apply adds the file to `access` with its SHA-256, as for every ledger download
    (INTAKE_WORKFLOW.md section 55);
  - the 3 papers Roadmap-to-QML added at 7113ded1df, entered by `scripts/sprint18_f114_roadmap.py`
    (`manifests/sprint18_f114_roadmap.json`); each file is read from its record's `access`.
- 26 from the ledger, from the first group not yet read in full: g296's 3 records Sprint 17 left (its first 2 were
  read in Task E; g296's brief is that task's, so these 3 go in the re-entry brief `g296-r1`, F125's form), then g349 to g371, one paper each (q20 = a's split). g297 to g329 are superseded; g335 to g347
  hold F144's Batch API reads, not applied, and are not this task's.

Sprint 16's exclusions (a directory source, a saved web page with no article, a book) remove none of these 26: each
is one PDF (checked 2026-11-21).

    python scripts/sprint18_f114_local.py           # what would be written
    python scripts/sprint18_f114_local.py --write   # the new groups into the ledger, then the briefs (a brief handed
                                                    # to a reader is never rewritten; a second --write adds nothing)
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
TOTAL = 30
HUANG = ("huang-2023-noise-resilient-single-pixel-compressive",
         r"D:\Data\Harold\EvidenceBasedDB\Papers\2023_Huang_Noise-Resilient-Single-Pixel-Compressive-Sensing-with-Single-Photon.pdf")
ROADMAP = ROOT / "manifests" / "sprint18_f114_roadmap.json"
FROM_LEDGER = {"g296": ("andriyash-2017-can-quantum-monte-carlo-simulate",
                        "arrieta-2019-explainable-artificial-intelligence-xai-concepts",
                        "arute-2020-hartree-fock-superconducting-qubit-quantum"),
               **{f"g{n}": None for n in range(349, 372)}}  # None: the one-paper group's only record


def new_papers(conn) -> list[dict]:
    m = json.loads(ROADMAP.read_text(encoding="utf-8"))
    rows = [{"record_id": HUANG[0], "file": HUANG[1]}]
    rows += [{"record_id": e["record_id"], "file": s16.local_file(conn, e["record_id"])} for e in m["entered"]]
    return rows


def placed(L: dict, rid: str) -> str | None:
    """The ledger group that holds `rid` now, or None."""
    return next((g for g, v in L.items() if any(r["record_id"] == rid for r in v["records"])), None)


def plan(L: dict, conn) -> dict[str, list[dict]]:
    """group -> its brief's records ({record_id, file}). A new paper already placed by an earlier --write keeps its
    group; one not yet placed gets a new group from `new_groups` (on a copy, so a dry run changes nothing)."""
    out: dict[str, list[dict]] = {}
    work = {g: {"records": list(v["records"])} for g, v in L.items()}
    for row in new_papers(conn):
        g = placed(work, row["record_id"])
        if g is None:
            g = g_ledger.new_groups(work, [row])[0]
        out[g] = [row]
    for g, rids in FROM_LEDGER.items():
        recs = L[g]["records"]
        if rids is None:
            if len(recs) != 1:
                raise ValueError(f"{g}: expected one record, found {len(recs)}")
            out[g] = list(recs)
            continue
        where = {r["record_id"]: r for r in recs}
        missing = [r for r in rids if r not in where]
        if missing:
            raise ValueError(f"{g}: not in its ledger group: {missing}")
        out[f"{g}-r1"] = [where[r] for r in rids]  # g296's own brief is Sprint 17's (its first 2): a re-entry brief
    return out


def check(groups: dict[str, list[dict]], conn) -> list[str]:
    rids = [r["record_id"] for rs in groups.values() for r in rs]
    bad = []
    if len(rids) != TOTAL:
        bad.append(f"the briefs hold {len(rids)} papers, not {TOTAL}")
    if len(rids) != len(set(rids)):
        bad.append("a record is planned twice")
    missing = [r["file"] for rs in groups.values() for r in rs if not Path(r["file"]).is_file()]
    if missing:
        bad.append(f"no local file: {missing}")
    full = [rid for rid in rids if conn.execute(
        "SELECT 1 FROM paper_reads WHERE record_id = ? AND extent = 'full'", (rid,)).fetchone()]
    if full:
        bad.append(f"already read in full: {full}")
    return bad


def main(argv: list[str]) -> int:
    write = "--write" in argv
    L = s16.ledger()
    with connect(DB_PATH) as conn:
        groups = plan(L, conn)
        bad = check(groups, conn)
        if bad:
            print("\n".join(bad))
            return 1
        added = {g: recs for g, recs in groups.items() if g not in L and not g.endswith("-r1")}
        for g in added:
            print(f"{'add' if write else 'would add'} {g} to the ledger: {added[g][0]['record_id']}")
        if write and added:
            full = json.loads(LEDGER.read_text(encoding="utf-8"))
            for g, recs in added.items():
                full["groups"][g] = {"records": recs}
            held = [r["record_id"] for v in full["groups"].values() for r in v["records"]]
            if len(held) != len(set(held)):
                raise ValueError("a record would be held twice; nothing written")
            LEDGER.write_text(json.dumps(full, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        for g, recs in groups.items():
            path = LOCAL / "briefs" / f"{g}.json"
            if path.exists() and [r["record_id"] for r in json.loads(path.read_text(encoding="utf-8"))["records"]] \
                    != [r["record_id"] for r in recs]:
                raise ValueError(f"{path.name} holds other records than this plan; look again")
            print(f"{'exists' if path.exists() else 'write' if write else 'would write'} {path.name}: "
                  f"{len(recs)}: {', '.join(r['record_id'][:45] for r in recs)}")
            if write and not path.exists():
                brief = {"group": g, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(
                    conn, r["record_id"])} for r in recs]}
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{TOTAL} papers in {len(groups)} groups")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
