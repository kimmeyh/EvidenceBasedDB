#!/usr/bin/env python3
"""Sprint 17 Manual Validation q20 = a (team lead, 2026-11-09): each paper of the unstarted ledger groups g297 to
g329 gets a one-paper group of its own, and the old group keeps a dated note of where each paper went.

Why: a 5-paper group is read by one reader in one sitting; a paper read alone is a smaller unit to start, stop and
restart, and the batch reader (F144) already makes one-paper groups.

Shape (design B, chosen 2026-11-09 so "one record, one group" stays true for every ledger reader): the old group's
`records` becomes empty, and its `superseded` note holds every record it held, each with its file and the group it
moved to. Nothing is deleted: the note keeps each id and file, and the old brief stays where it is. Each new group
gets a brief with the record's stored assertions as of the split (the old briefs hold them as of the ledger's
build), written outside git like every brief (CLAUDE.md: git holds code and documents).

A group is split only when nothing of it has started: no read row naming it, no reader file, no review, no scratch
folder. A group already split is left alone, so a second run writes nothing.

Dry run by default. Usage:
  python scripts/sprint17_q20_split.py            print the plan
  python scripts/sprint17_q20_split.py --write    write the ledger and the new briefs
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
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
BRIEFS = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\briefs")
FIRST, LAST = 297, 329
DECIDED = "2026-11-09 (Sprint 17 Manual Validation, q20 = a): one paper per group; this group was never started"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def old_groups(groups: dict) -> list[str]:
    return [g for n in range(FIRST, LAST + 1) if (g := f"g{n}") in groups]


def next_number(groups: dict) -> int:
    return max(int(m[1]) for g in groups if (m := re.match(r"g(\d+)$", g))) + 1


def started(g: str, status) -> list[str]:
    """Why group g counts as started, from the files the status script reads; empty when it never started."""
    why = []
    if (status.REVIEWS / f"{g}.json").exists():
        why.append("a review")
    if (ROOT / "manifests" / "sprint13_g_reads" / f"group_{g}.json").exists():
        why.append("a reader file")
    if (status.WORK / "reads" / f"group_{g}.json").exists():
        why.append("a local reader file")
    if (status.WORK / f"tmp_{g}").exists():
        why.append("a scratch folder")
    return why


def split(groups: dict, applied: set[tuple[str, str]], status=None) -> list[tuple[str, dict, str]]:
    """Change `groups` in place; return (old group, record, new group) for each record moved. A group already split
    is skipped; a group with any sign of a start is refused."""
    moved = []
    n = next_number(groups)
    for g in old_groups(groups):
        body = groups[g]
        if "superseded" in body:
            continue
        rids = [r["record_id"] for r in body["records"]]
        why = (started(g, status) if status else []) + [f"a read of {r}" for r in rids if (g, r) in applied]
        if why:
            raise ValueError(f"{g} has started ({', '.join(why)}); it is not split")
        note = []
        for r in body["records"]:
            new = f"g{n:03d}"
            n += 1
            groups[new] = {"records": [dict(r)]}
            note.append({**r, "moved_to": new})
            moved.append((g, r, new))
        groups[g] = {"records": [], "superseded": {"decided": DECIDED, "records": note}}
    return moved


def held_twice(groups: dict) -> list[str]:
    held = [r["record_id"] for v in groups.values() for r in v["records"]]
    return sorted({r for r in held if held.count(r) > 1})


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in args
    status = _load("g_status", "sprint13_g_status.py")
    g_ledger = _load("g_ledger", "sprint13_g_ledger.py")
    full = json.loads(LEDGER.read_text(encoding="utf-8"))
    moved = split(full["groups"], status.applied_records(), status)
    if not moved:
        print("nothing to split: every group from "
              f"g{FIRST} to g{LAST} is already split")
        return 0
    twice = held_twice(full["groups"])
    if twice:
        print(f"a record would be held twice: {twice}; nothing written")
        return 1
    for g, r, new in moved:
        print(f"{'move' if write else 'would move'} {r['record_id']}  {g} -> {new}")
    if write:
        with connect(DB_PATH) as conn:
            briefs = {new: {"group": new, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(
                conn, r["record_id"])}]} for _, r, new in moved}
        for new, brief in briefs.items():
            path = BRIEFS / f"{new}.json"
            if path.exists():
                raise ValueError(f"{path} exists; a new group's brief is never rewritten")
        for new, brief in briefs.items():
            (BRIEFS / f"{new}.json").write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
        LEDGER.write_text(json.dumps(full, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(moved)} papers {'moved' if write else 'to move'} from {len({g for g, _, _ in moved})} groups into "
          f"{moved[0][2]} to {moved[-1][2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
