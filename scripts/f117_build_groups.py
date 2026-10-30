#!/usr/bin/env python3
"""Sprint 14 Task E (F117): F114's cloud results, one file per paper, assembled into the group reader files the
applier reads (`manifests/sprint13_g_reads/group_<g>.json`, as Task G's were).

Each paper's entry is copied as its cloud session wrote it, in ledger order, with one change: 22 results name a new
assertion's id `id` instead of `id_suggestion` (the reader prompt's key), so `id` is renamed; where both are given
they must agree. A group is built only when every record of it has a result or is marked unread by the team lead
(UNREAD below); an existing group file is never overwritten.

    python scripts/f117_build_groups.py            # list what would be built
    python scripts/f117_build_groups.py --write    # write the group files
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("f114_cloud", ROOT / "scripts" / "f114_cloud.py")
cloud = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cloud)

READS_DIR = ROOT / "manifests" / "sprint13_g_reads"
# Left out of its group, unread. Only the team lead's mark: abbas-2020-power-quantum-neural-networks is never
# launched in the cloud again (f114_cloud.UNREAD) but is read by Task F, so its group g079 waits for that read.
UNREAD = {"udaru-2025-qml-credit-risk": cloud.UNREAD["udaru-2025-qml-credit-risk"]}


def entry(rid: str) -> dict:
    papers = json.loads((cloud.WORK / "results" / f"{rid}.json").read_text(encoding="utf-8"))["papers"]
    if [p["record_id"] for p in papers] != [rid]:
        raise ValueError(f"{rid}: its result holds {[p['record_id'] for p in papers]}")
    p = papers[0]
    for a in p.get("assertions", []):
        if "id" in a:
            if a.setdefault("id_suggestion", a["id"]) != a["id"]:
                raise ValueError(f"{rid}: an assertion names two ids, {a['id']} and {a['id_suggestion']}")
            del a["id"]
    return p


def buildable(exclude: set[str] = frozenset()) -> dict[str, list[str]]:
    """group -> its records with a result, for every group from FIRST_GROUP whose records all have a result or
    are unread; groups in `exclude` are left out."""
    have = {p.stem for p in (cloud.WORK / "results").glob("*.json")}
    out = {}
    for g, v in sorted(json.loads(cloud.LEDGER.read_text(encoding="utf-8"))["groups"].items()):
        if g < cloud.FIRST_GROUP or g in exclude:
            continue
        rids = [r["record_id"] for r in v["records"]]
        if all(r in have or r in UNREAD for r in rids) and any(r in have for r in rids):
            out[g] = [r for r in rids if r in have]
    return out


def main(argv: list[str]) -> int:
    groups = buildable()
    for g, rids in groups.items():
        path = READS_DIR / f"group_{g}.json"
        if path.exists():
            print(f"exists {path.name}")
            continue
        if "--write" in argv:
            path.write_text(json.dumps({"papers": [entry(r) for r in rids]}, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"{'wrote' if '--write' in argv else 'would write'} {path.name} ({len(rids)} records)")
    print(f"{len(groups)} groups, {sum(map(len, groups.values()))} records")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
