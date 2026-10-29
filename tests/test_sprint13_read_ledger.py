"""Sprint 13's read ledger: no record is read twice (team lead, 2026-10-21:
"no 2 'read's should impact the same record").

`manifests/sprint13_read_ledger.json` gives every record Task F reads to
exactly one group. These tests fail if a record is held twice (in two
groups, or in a group and in `no_copy`), if a reader's file holds a record
its group does not, if the ledger and the slice disagree, or if a no-copy
record has no reason of its own.

Proven to fail by injection, 2026-10-25: with the first slice record
added to `no_copy` in a copy of the ledger, test_no_record_is_held_twice
went red; with one no-copy reason set back to Sprint 11's one reason for
all ("no free copy known to OpenAlex, or the fetch failed (section 32)"),
test_every_no_copy_record_says_why went red. Both restored. Once
group_g01.json existed, with g02's first paper appended to it,
test_every_reader_file_holds_only_its_groups_records named that paper.
Restored.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "manifests" / "sprint13_read_ledger.json"
SLICE = ROOT / "manifests" / "sprint13_f112_slice.json"
READS = ROOT / "manifests" / "sprint13_reads"

_spec = importlib.util.spec_from_file_location("ledger13", ROOT / "scripts" / "sprint13_read_ledger.py")
ledger_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger_mod)


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_no_record_is_held_twice():
    assert ledger_mod.ledger11.duplicates(_ledger()) == []


def test_the_ledger_holds_exactly_the_slice():
    led = _ledger()
    held = {r["record_id"] for g in led["groups"].values() for r in g["records"]} | set(led["no_copy"])
    assert held == {r["record_id"] for r in json.loads(SLICE.read_text(encoding="utf-8"))["slice"]}


def test_every_no_copy_record_says_why():
    generic = "no free copy known to OpenAlex, or the fetch failed"
    bad = [rid for rid, why in _ledger()["no_copy"].items() if generic in why]
    assert not bad, bad


def test_every_reader_file_holds_only_its_groups_records():
    groups = _ledger()["groups"]
    for path in sorted(READS.glob("group_*.json")) if READS.exists() else []:
        name = path.stem.removeprefix("group_")
        assert name in groups, f"{path.name} names no ledger group"
        allowed = {r["record_id"] for r in groups[name]["records"]}
        got = {p["record_id"] for p in json.loads(path.read_text(encoding="utf-8"))["papers"]}
        assert got <= allowed, f"{path.name} holds records outside its group: {sorted(got - allowed)}"


def test_groups_stay_small_enough_for_one_reader():
    for name, g in _ledger()["groups"].items():
        assert g["task"] == "F", name
        assert 0 < len(g["records"]) <= ledger_mod.ledger11.GROUP_SIZE, name
