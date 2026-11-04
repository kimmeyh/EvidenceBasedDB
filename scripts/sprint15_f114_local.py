#!/usr/bin/env python3
r"""Sprint 15 Task H (F114 at 100 papers): the local readers' briefs.

The 100 papers (plan, Task H): first the records reviewed groups left unread that have something to read, each in a
re-entry group `<g>-r1` (F125, Sprint 15 Task C): udaru-2025-qml-credit-risk (g076), mancilla-2026 (g062) and
qci-2026-entropy-computing-trade-magazine (g064), whose pages are images that OCR now reads (F115, Task F), and
g113's three chen-2026 records. Then ledger order from g114. Each brief lists the records its reader reads, with each
record's stored assertions as the store holds them now; the reader prompt is
`manifests/sprint15_f114_reads/READER_PROMPT.md`.

Left out, each with why:
- g069's and g072's unread records: the saved web page holds the site's menus and footer, not the article, so a
  re-entry group would have nothing to read (f117_build_groups.UNREAD);
- a record whose source is a directory (a code repository, such as GitHubRepos\feebee): the quote check and the
  applier read one file per source, so its quotes could not be checked. Its group's brief leaves it out, and the
  builder marks it for a later release, as Sprint 14 trimmed g113.

    python scripts/sprint15_f114_local.py           # what would be written
    python scripts/sprint15_f114_local.py --write   # the briefs (a brief handed to a reader is never rewritten)
    python scripts/sprint15_f114_local.py --task-i [--write]   # Task I's 100 (F133), ledger order from g134
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
TOTAL = 100
REENTER = ("g062", "g064", "g076", "g113")  # g069 and g072 left unread a web page that holds no article
FIRST = "g114"


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]


def files(L: dict) -> dict[str, str]:
    return {r["record_id"]: r["file"] for v in L.values() for r in v["records"]}


def plan(L: dict, first: str | None = None, total: int | None = None,
         reenter: tuple[str, ...] | None = None) -> tuple[dict[str, list[dict]], list[str]]:
    """(group -> the records its reader reads, in order; the records left for a later release because their source
    is a directory). Task H's release by default; Task I's is `plan(L, I_FIRST, I_TOTAL, ())`. Ledger groups past
    J's are never taken: they are another task's."""
    first, total = first or FIRST, total or TOTAL
    reenter = REENTER if reenter is None else reenter
    where = files(L)
    out: dict[str, list[dict]] = {}
    for g in reenter:
        unread = json.loads((REVIEWS_DIR / f"{g}.json").read_text(encoding="utf-8")).get("unread") or {}
        out[f"{g}-r1"] = [{"record_id": rid, "file": where[rid]} for rid in unread]
    taken = sum(len(v) for v in out.values())
    later = []
    for g in sorted(x for x in L if first <= x < J_GROUPS[0]):
        if taken >= total:
            break
        for r in L[g]["records"]:
            if taken >= total:
                break
            if Path(r["file"]).is_dir():
                later.append(r["record_id"])
                continue
            out.setdefault(g, []).append(r)
            taken += 1
    return out, later


def check(groups: dict[str, list[dict]], total: int | None = None) -> list[str]:
    total = total or TOTAL
    rids = [r["record_id"] for rs in groups.values() for r in rs]
    bad = []
    if len(rids) != total:
        bad.append(f"the briefs hold {len(rids)} papers, not {total}")
    if len(rids) != len(set(rids)):
        bad.append("a record is planned twice")
    missing = [r["file"] for rs in groups.values() for r in rs if not Path(r["file"]).is_file()]
    if missing:
        bad.append(f"no local file: {missing}")
    return bad


F128 = ROOT / "manifests" / "sprint15_f128_targets.json"
FARYAD = "faryad-2026-input-problem-permanent-bottleneck-quantum"  # stored, read in part (F128)
J_GROUPS = ("g331", "g332")


def j_records(conn) -> list[dict]:
    """Task J's papers (F128), read in addition to the 100: the 8 entered by sprint15_f128_targets.py, then Faryad,
    each with the local file its access names."""
    rids = [e["record_id"] for e in json.loads(F128.read_text(encoding="utf-8"))["entered"]] + [FARYAD]
    out = []
    for rid in rids:
        row = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        if row is None:
            raise ValueError(f"{rid}: no paper record in the store")
        # a local file, not a URL that ends ".pdf" (fresh-eyes review, 2026-11-02)
        local = [p.strip() for p in (row[0] or "").split("|")
                 if p.strip().lower().endswith(".pdf") and Path(p.strip()).is_file()]
        if not local:
            raise ValueError(f"{rid}: no local file in its access")
        out.append({"record_id": rid, "file": local[0]})
    return out


def add_j_groups(L: dict, conn, write: bool) -> dict[str, list[dict]]:
    """Task J's groups in the ledger after g330, five records each, added once."""
    if all(g in L for g in J_GROUPS):
        return {g: L[g]["records"] for g in J_GROUPS}
    if any(g in L for g in J_GROUPS) or sorted(L)[-1] >= J_GROUPS[0]:
        raise ValueError(f"the ledger already reaches {sorted(L)[-1]}; Task J's groups need a fresh look")
    recs = j_records(conn)
    held = {r["record_id"] for v in L.values() for r in v["records"]}
    if any(r["record_id"] in held for r in recs):
        raise ValueError("a Task J record is already in the ledger")
    groups = {g: recs[i * 5:(i + 1) * 5] for i, g in enumerate(J_GROUPS)}
    print(f"{'add' if write else 'would add'} {', '.join(f'{g} ({len(r)})' for g, r in groups.items())} to the ledger")
    if write:
        full = json.loads(LEDGER.read_text(encoding="utf-8"))
        full["groups"].update({g: {"records": r} for g, r in groups.items()})
        LEDGER.write_text(json.dumps(full, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return groups


# Task I (F133, the F57 release, plan Q2 = 2: 100 records). Every unread record with a local file is in the ledger
# past H's groups (snapshot as of 2026-11-02: the 355 unread records outside it have no local copy, and the plan's
# 11 local-only records are none of them), so I reads the next 100 in ledger order, read and reviewed as H's are.
I_FIRST = "g134"
I_TOTAL = 100


def main_task_i(write: bool) -> int:
    groups, later = plan(ledger(), I_FIRST, I_TOTAL, ())
    bad = check(groups, I_TOTAL)
    if bad:
        print("\n".join(bad))
        return 1
    with connect(DB_PATH) as conn:
        for g, recs in groups.items():
            path = LOCAL / "briefs" / f"{g}.json"
            print(f"{'exists' if path.exists() else 'write' if write else 'would write'} {path.name}: "
                  f"{len(recs)} records")
            if write and not path.exists():
                brief = {"group": g, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(
                    conn, r["record_id"])} for r in recs]}
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Task I: {I_TOTAL} papers in {len(groups)} groups, {min(groups)} to {max(groups)}; left for a later "
          f"release (a directory, not a file): {later}")
    return 0


def main(argv: list[str]) -> int:
    write = "--write" in argv
    if "--task-i" in argv:
        return main_task_i(write)
    groups, later = plan(ledger())
    bad = check(groups)
    if bad:
        print("\n".join(bad))
        return 1
    with connect(DB_PATH) as conn:
        groups.update(add_j_groups(ledger(), conn, write))
        for g, recs in groups.items():
            path = LOCAL / "briefs" / f"{g}.json"
            brief = {"group": g, "records": [{**r, "stored_assertions": g_ledger.stored_assertions(conn, r["record_id"])}
                                             for r in recs]}
            print(f"{'exists' if path.exists() else 'write' if write else 'would write'} {path.name}: "
                  f"{len(recs)} records")
            if write and not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    j = sum(len(groups[g]) for g in J_GROUPS)
    print(f"{sum(len(r) for r in groups.values()) - j} papers of the 100 and {j} of Task J's, in {len(groups)} "
          f"groups; left for a later release (a "
          f"directory, not a file): {later}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
