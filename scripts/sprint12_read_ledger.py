#!/usr/bin/env python3
"""Sprint 12: the one read ledger for Tasks E, F and G (F103, F104, F105).

Sprint 11's ledger (`scripts/sprint11_read_ledger.py`) pointed at this
sprint's files: one record, one group, one first-pass reader; at most 5
readers at once, in waves; a record with no local copy goes to `no_copy`
with its reason, never to a reader. `tests/test_sprint12_read_ledger.py`
fails if any record is held twice.

New this sprint: `read_by_coordinator`. Task E's three pages were read in
full by the coordinator before the ledger existed (a change from the plan,
which put the ledger first); they are entered here so no group can take
them again.

Usage:
  python scripts/sprint12_read_ledger.py --task E
      records Task E's pages as read by the coordinator
  python scripts/sprint12_read_ledger.py --task F --records <json file>
  python scripts/sprint12_read_ledger.py --task G --download-log <file>
Writes `manifests/sprint12_read_ledger.json`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("ledger11", Path(__file__).with_name("sprint11_read_ledger.py"))
ledger11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger11)

_spec = importlib.util.spec_from_file_location("f103", Path(__file__).with_name("sprint12_f103_intake.py"))
f103 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f103)

ROOT = ledger11.ROOT
ledger11.LEDGER = LEDGER = ROOT / "manifests" / "sprint12_read_ledger.json"
ledger11.SLICE = ROOT / "manifests" / "sprint12_f105_slice.json"
_load11 = ledger11.load
_held11 = ledger11.held
_duplicates11 = ledger11.duplicates


def load() -> dict:
    ledger = _load11()
    ledger.setdefault("read_by_coordinator", {})
    return ledger


def held(ledger: dict) -> set[str]:
    return _held11(ledger) | set(ledger.get("read_by_coordinator", {}))


def duplicates(ledger: dict) -> list[str]:
    """Sprint 11's duplicates, and any coordinator record also in a group or in no_copy."""
    in_groups = {r["record_id"] for g in ledger["groups"].values() for r in g["records"]}
    return _duplicates11(ledger) + [rid for rid in ledger.get("read_by_coordinator", {})
                                    if rid in in_groups or rid in ledger["no_copy"]]


ledger11.held = held


F104 = ROOT / "manifests" / "sprint12_f104_roadmap.json"
WITHDRAWN = {"mahroo-2023-trainable-variational-quantum-multiblock-admm":
             "no local copy: withdrawn on arXiv (2303.16318, abstract page read 2026-10-23); INTAKE_WORKFLOW.md "
             "section 46"}


def task_f() -> int:
    """Task F's entered records from its manifest: those with a copy into groups, the rest to no_copy."""
    ledger = load()
    rows, missing = [], {}
    for e in json.loads(F104.read_text(encoding="utf-8"))["entered"]:
        if e["local_copy"]:
            rows.append({"record_id": e["record_id"], "file": (ledger11.PAPERS / e["local_copy"]).as_posix()})
        else:
            missing[e["record_id"]] = WITHDRAWN.get(e["record_id"], "no local copy: the fetch failed (section 46)")
    clash = sorted(set(missing) & held(ledger))
    if clash:
        raise SystemExit(f"refused: already in the ledger: {clash}")
    n = ledger11.add_groups(ledger, "F", rows)
    ledger["no_copy"].update(missing)
    assert not duplicates(ledger)
    LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"task F: {len(rows)} records in groups up to g{n:02d}; no copy: {len(missing)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    task = args[args.index("--task") + 1]
    if task == "F":
        return task_f()
    if task != "E":
        ledger11.load = load
        ledger11.duplicates = duplicates
        return ledger11.main(args)
    ledger = load()
    rows = {s["id"]: f"Task E (F103): read in full by the coordinator, {f103.TODAY} (INTAKE_WORKFLOW.md section 44)"
            for s in f103.SOURCES.values()}
    clash = sorted(set(rows) & held(ledger))
    if clash:
        raise SystemExit(f"refused: already in the ledger: {clash}")
    ledger["read_by_coordinator"].update(rows)
    assert not duplicates(ledger)
    LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"task E: {len(rows)} records read by the coordinator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
