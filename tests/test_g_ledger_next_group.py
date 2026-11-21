"""F149 (Sprint 18 Task A): the F114 ledger names a new group from the highest
group number plus one, never from the group count.

`scripts/sprint13_g_ledger.py` set `start = len(groups)`. With a gap in the
names (g001, g003) the count is 2, so the next group was named g003 and
replaced a group a reader already answers. These tests fail if the count
comes back, in the helper, in `new_groups`, or in `main()`.

Proven to fail by injection, 2026-11-20 and 2026-11-21, each restored:
- `highest_group_number` returning `len(groups)  # INJECTED`:
  test_a_gap_names_the_next_group_above_the_highest went red (2 against 3).
- the gNNN refusal replaced by `continue  # INJECTED`:
  test_a_name_that_is_not_gNNN_is_refused went red.
- `new_groups` starting at `len(groups)  # INJECTED`:
  test_new_groups_are_named_above_the_highest_and_keep_the_old went red
  (g003, g004 against g004, g005).
- `main()` naming groups by its own count loop again (`# INJECTED`), the
  fresh-eyes review's case: test_main_names_groups_only_through_new_groups
  went red.
A grep for INJECTED in the script finds nothing.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"

_spec = importlib.util.spec_from_file_location("g_ledger", ROOT / "scripts" / "sprint13_g_ledger.py")
g_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g_ledger)


def test_a_gap_names_the_next_group_above_the_highest():
    groups = {"g001": {"records": []}, "g003": {"records": []}}
    assert g_ledger.highest_group_number(groups) == 3


def test_new_groups_are_named_above_the_highest_and_keep_the_old():
    groups = {"g001": {"records": ["kept"]}, "g003": {"records": ["kept"]}}
    rows = [{"record_id": f"r{i}", "file": f"f{i}"} for i in range(6)]
    assert g_ledger.new_groups(groups, rows) == ["g004", "g005"]
    assert groups["g003"] == {"records": ["kept"]}
    assert [r["record_id"] for r in groups["g005"]["records"]] == ["r5"]


def test_main_names_groups_only_through_new_groups():
    src = (ROOT / "scripts" / "sprint13_g_ledger.py").read_text(encoding="utf-8")
    main_src = src[src.index("def main("):]
    assert "new_groups(groups, rows)" in main_src
    assert "len(groups) +" not in main_src and "start = len(groups)" not in main_src


def test_an_empty_ledger_starts_at_g001():
    assert g_ledger.highest_group_number({}) == 0


def test_a_name_that_is_not_gNNN_is_refused():
    with pytest.raises(ValueError, match="gNNN"):
        g_ledger.highest_group_number({"g001": {}, "extra": {}})


def test_the_committed_ledger_names_are_all_gNNN():
    groups = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]
    assert g_ledger.highest_group_number(groups) >= len(groups)
