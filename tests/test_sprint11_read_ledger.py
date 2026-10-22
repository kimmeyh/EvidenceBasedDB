"""Sprint 11's read ledger: no record is read twice (team lead, 2026-10-21:
"no 2 'read's should impact the same record").

`manifests/sprint11_read_ledger.json` gives every record Tasks E, F and G
read to exactly one group, and each group to one reader. These tests fail
if a record is in two groups (or in a group and in `no_copy`), if a reader's
file holds a record its group does not, or if the ledger's own refusal to
add a held record is lost.

Proven to fail by injection, 2026-10-22: copying g01's first record into
g02 turned test_no_record_is_in_two_groups red; adding a record from g02 to
a scratch reader file for g01 turned
test_every_reader_file_holds_only_its_groups_records red. Both restored.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "manifests" / "sprint11_read_ledger.json"
READS = ROOT / "manifests" / "sprint11_reads"

_spec = importlib.util.spec_from_file_location("ledger", ROOT / "scripts" / "sprint11_read_ledger.py")
ledger_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger_mod)


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_no_record_is_in_two_groups():
    assert ledger_mod.duplicates(_ledger()) == []


def test_every_reader_file_holds_only_its_groups_records():
    groups = _ledger()["groups"]
    for path in sorted(READS.glob("group_*.json")) if READS.exists() else []:
        name = path.stem.removeprefix("group_")
        assert name in groups, f"{path.name} names no ledger group"
        allowed = {r["record_id"] for r in groups[name]["records"]}
        got = {p["record_id"] for p in json.loads(path.read_text(encoding="utf-8"))["papers"]}
        assert got <= allowed, f"{path.name} holds records outside its group: {sorted(got - allowed)}"


def test_the_ledger_refuses_a_record_it_already_holds():
    d = {"groups": {"g01": {"task": "G", "records": [{"record_id": "x", "file": "f"}]}}, "no_copy": {}}
    with pytest.raises(SystemExit):
        ledger_mod.add_groups(d, "F", [{"record_id": "x", "file": "f"}])


def test_groups_name_a_task_and_stay_small_enough_for_one_reader():
    for name, g in _ledger()["groups"].items():
        assert g["task"] in ("E", "F", "G"), name
        assert 0 < len(g["records"]) <= ledger_mod.GROUP_SIZE, name
