"""Sprint 12's read ledger: no record is read twice (team lead, 2026-10-21:
"no 2 'read's should impact the same record").

`manifests/sprint12_read_ledger.json` gives every record Tasks F and G
read to exactly one group, and lists Task E's pages as read by the
coordinator. These tests fail if a record is held twice (in two groups, in
a group and in `no_copy`, or in a group and among the coordinator's), if a
reader's file holds a record its group does not, or if the ledger's
refusal to add a held record is lost.

Proven to fail by injection, 2026-10-23: with the coordinator check
removed from `duplicates()`,
test_a_coordinator_record_in_a_group_is_a_duplicate went red; with
`ledger11.held = held` commented out,
test_the_ledger_refuses_a_record_the_coordinator_read went red. Both
restored. The two tests carried from Sprint 11 were proven there.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "manifests" / "sprint12_read_ledger.json"
READS = ROOT / "manifests" / "sprint12_reads"

_spec = importlib.util.spec_from_file_location("ledger12", ROOT / "scripts" / "sprint12_read_ledger.py")
ledger_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger_mod)


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_no_record_is_held_twice():
    assert ledger_mod.duplicates(_ledger()) == []


def test_a_coordinator_record_in_a_group_is_a_duplicate():
    d = {"groups": {"g01": {"task": "G", "records": [{"record_id": "x", "file": "f"}]}}, "no_copy": {},
         "read_by_coordinator": {"x": "Task E"}}
    assert ledger_mod.duplicates(d) == ["x"]


def test_task_e_pages_are_the_coordinators():
    assert set(_ledger()["read_by_coordinator"]) == {s["id"] for s in ledger_mod.f103.SOURCES.values()}


def test_every_reader_file_holds_only_its_groups_records():
    groups = _ledger()["groups"]
    for path in sorted(READS.glob("group_*.json")) if READS.exists() else []:
        name = path.stem.removeprefix("group_")
        assert name in groups, f"{path.name} names no ledger group"
        allowed = {r["record_id"] for r in groups[name]["records"]}
        got = {p["record_id"] for p in json.loads(path.read_text(encoding="utf-8"))["papers"]}
        assert got <= allowed, f"{path.name} holds records outside its group: {sorted(got - allowed)}"


def test_the_ledger_refuses_a_record_the_coordinator_read():
    d = {"groups": {}, "no_copy": {}, "read_by_coordinator": {"x": "Task E"}}
    with pytest.raises(SystemExit):
        ledger_mod.ledger11.add_groups(d, "G", [{"record_id": "x", "file": "f"}])


def test_groups_name_a_task_and_stay_small_enough_for_one_reader():
    for name, g in _ledger()["groups"].items():
        assert g["task"] in ("F", "G"), name
        assert 0 < len(g["records"]) <= ledger_mod.ledger11.GROUP_SIZE, name
