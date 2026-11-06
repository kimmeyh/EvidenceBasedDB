#!/usr/bin/env python3
r"""Sprint 16 Task F (F114, 20 papers): the local readers' briefs. INTAKE_WORKFLOW.md sections 72 and 73.

The 20, in the plan's order (Q1 = 1, Q2 = 2):

- g333 and g334, two new ledger groups after g332: the 6 papers new on Roadmap-to-QML at 399b022651
  (`manifests/sprint16_f114_roadmap.json`) and the team lead's 2 named papers (`manifests/sprint16_f57_named.json`);
- then 12 from the ledger, from the first group not yet read in full: the records reviewed groups left unread that
  have a file to read, each in a re-entry group `<g>-r1` (F125), then ledger order from g155.

Left out, each with why:
- a record whose source is a directory (an OpenCyc release, a code repository): the quote check and the applier read
  one file per source (as Sprint 15's briefs, `scripts/sprint15_f114_local.py`);
- g069's and g072's unread records: the saved web page holds the site's menus and footer, not the article;
- a book (F114's card, Q7): read under F138. None falls in these 12.

    python scripts/sprint16_f114_local.py           # what would be written
    python scripts/sprint16_f114_local.py --write   # the ledger groups and the briefs (a brief handed to a reader is
                                                    # never rewritten)
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

LEDGER = g_ledger.LEDGER
REVIEWS_DIR = ROOT / "manifests" / "sprint13_g_reviews"
LOCAL = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local")
ROADMAP = ROOT / "manifests" / "sprint16_f114_roadmap.json"
NAMED = ("goes-2021-qboost-regression-problems-solving-partial",
         "wangy8205165-2026-quantum-neural-networks-theory-architectures")
NEW_GROUPS = ("g333", "g334")
LEDGER_TOTAL = 12
FIRST = "g155"  # g154's reviewed group read one record; its other four are a re-entry group
# Reviewed groups whose unread records have a file and no re-entry brief before Sprint 16 (found 2026-11-06). Left
# out: g069 and g072 (their unread saved web page holds the site's menus, not the article, Sprint 15) and g120, g121,
# g129 and g138 (their unread records are directories).
REENTER = ("g133", "g154")


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]


def local_file(conn, rid: str) -> str:
    row = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
    if row is None:
        raise ValueError(f"{rid}: no paper record in the store")
    local = [p.strip() for p in (row[0] or "").split("|")
             if p.strip().lower().endswith(".pdf") and Path(p.strip()).is_file()]
    if not local:
        raise ValueError(f"{rid}: no local file in its access")
    return local[0]


def new_records(conn) -> list[dict]:
    m = json.loads(ROADMAP.read_text(encoding="utf-8"))
    rids = [e["record_id"] for e in m["entered"]] + [e["record_id"] for e in m["quantum_entered"]] + list(NAMED)
    return [{"record_id": rid, "file": local_file(conn, rid)} for rid in rids]


def unread_reentries(L: dict) -> dict[str, list[dict]]:
    """REENTER's groups' unread records, each group as `<g>-r1`, all of them (f117_build_groups.reentry_briefs requires
    a re-entry brief to hold exactly what its predecessor's review left unread). A fixed list, as Sprint 15's: found
    afresh, a re-run would skip the groups whose briefs now exist and plan other records (fresh-eyes review)."""
    where = {r["record_id"]: r["file"] for v in L.values() for r in v["records"]}
    out = {}
    for g in REENTER:
        unread = json.loads((REVIEWS_DIR / f"{g}.json").read_text(encoding="utf-8")).get("unread") or {}
        out[f"{g}-r1"] = [{"record_id": rid, "file": where[rid]} for rid in unread]
    return out


def plan(L: dict, conn) -> tuple[dict[str, list[dict]], list[str]]:
    recs = new_records(conn)
    out: dict[str, list[dict]] = {NEW_GROUPS[0]: recs[:5], NEW_GROUPS[1]: recs[5:]}
    taken, later = 0, []
    for g, rs in unread_reentries(L).items():
        out[g] = rs
        taken += len(rs)
    for g in sorted(x for x in L if FIRST <= x < "g331"):
        if taken >= LEDGER_TOTAL:
            break
        for r in L[g]["records"]:
            if taken >= LEDGER_TOTAL:
                break
            if Path(r["file"]).is_dir():
                later.append(r["record_id"])
                continue
            out.setdefault(g, []).append(r)
            taken += 1
    return out, later


def check(groups: dict[str, list[dict]]) -> list[str]:
    rids = [r["record_id"] for rs in groups.values() for r in rs]
    bad = []
    if len(rids) != 20:
        bad.append(f"the briefs hold {len(rids)} papers, not 20")
    if len(rids) != len(set(rids)):
        bad.append("a record is planned twice")
    missing = [r["file"] for rs in groups.values() for r in rs if not Path(r["file"]).is_file()]
    if missing:
        bad.append(f"no local file: {missing}")
    return bad


def main(argv: list[str]) -> int:
    write = "--write" in argv
    L = ledger()
    with connect(DB_PATH) as conn:
        groups, later = plan(L, conn)
        bad = check(groups)
        if bad:
            print("\n".join(bad))
            return 1
        if any(g in L for g in NEW_GROUPS):
            if any(L.get(g, {}).get("records") != groups[g] for g in NEW_GROUPS):
                raise ValueError("g333 or g334 is in the ledger with other records; look again")
        else:
            print(f"{'add' if write else 'would add'} {', '.join(NEW_GROUPS)} to the ledger")
            if write:
                full = json.loads(LEDGER.read_text(encoding="utf-8"))
                full["groups"].update({g: {"records": groups[g]} for g in NEW_GROUPS})
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
    print(f"20 papers in {len(groups)} groups; a directory, not a file, left for a later release: {later}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
