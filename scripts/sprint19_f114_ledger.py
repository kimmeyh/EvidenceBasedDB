#!/usr/bin/env python3
"""Sprint 19 Task D step 1: every readable paper no ledger group holds joins F114's ledger, one paper per group.

Team lead, 2026-11-25: q1 (F57's papers and the papers read only in part join F114's ledger) and "Add the 306 to
F114 list before updating the combined list with re-calculated priorities using the F114 method." The papers are
`reading_list.to_add`'s, computed from the store: `never read` first (F57's), then `read in part`, each by record
id. Each group is named by `sprint13_g_ledger.new_groups`, called once per paper (it packs GROUP_SIZE papers into
a group otherwise). A record's `file` is its local copy, or "" when it has none yet; a brief resolves the copy when
it is written (`sprint16_f114_local.local_file`), after the free-copy fetch.

Dry run by default; --write saves the ledger. A second --write adds nothing: a record the ledger holds, in a live
group or a superseded one, is never added again.

Usage:
  python scripts/sprint19_f114_ledger.py [--write]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import reading_list as rl  # noqa: E402
import sprint13_g_ledger as g_ledger  # noqa: E402


def held(L: dict) -> set[str]:
    return ({r["record_id"] for recs in rl.ledger_groups(L).values() for r in recs}
            | {r["record_id"] for v in L["groups"].values() if v.get("superseded")
               for r in v["superseded"].get("records", [])})


def add(L: dict, P: dict[str, dict]) -> list[tuple[str, str, str]]:
    """(group, record id, why) for each paper added to `L` in place."""
    out = []
    for why, rids in rl.to_add(P, held(L)).items():
        for rid in rids:
            g = g_ledger.new_groups(L["groups"], [{"record_id": rid, "file": rl.local_copy(P[rid]["access"])}])[0]
            out.append((g, rid, why))
    return out


def fill(L: dict, P: dict[str, dict]) -> list[tuple[str, str, str]]:
    """(group, record id, file) for each live ledger record whose `file` is "" and which now has a local copy (a
    fetch since, or a copy `add` did not yet see); `L` is changed in place."""
    out = []
    for g, recs in rl.ledger_groups(L).items():
        for r in recs:
            if not r.get("file") and r["record_id"] in P and (f := rl.local_copy(P[r["record_id"]]["access"])):
                r["file"] = f
                out.append((g, r["record_id"], f))
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    L = json.loads(rl.LEDGER.read_text(encoding="utf-8"))
    with rl.read_only() as conn:
        P = rl.papers(conn)
    added = add(L, P)
    filled = fill(L, P)
    print(f"{len(filled)} records{' given' if '--write' in args else ' to be given'} their local copy as `file`")
    by = {}
    for _, _, why in added:
        by[why] = by.get(why, 0) + 1
    for g, rid, why in added[:3] + added[-3:]:
        print(f"{'add' if '--write' in args else 'would add'} {g}: {rid} ({why})")
    print(f"{len(added)} papers{' added' if '--write' in args else ' to add'}: {by}; "
          f"{sum(1 for _, rid, _ in added if not rl.local_copy(P[rid]['access']))} with no local copy yet")
    ids = [r["record_id"] for recs in rl.ledger_groups(L).values() for r in recs]
    if len(ids) != len(set(ids)):
        raise ValueError("a record would be held twice; nothing written")
    if "--write" in args and (added or filled):
        rl.LEDGER.write_text(json.dumps(L, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {rl.LEDGER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
