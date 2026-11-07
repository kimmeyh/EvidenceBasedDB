"""F140 part 1 (Sprint 17 Task A): the test inventory (`docs/test_inventory.json`, written by
`scripts/test_inventory.py`) names every test file, and names no file that is gone.

Proven red 2026-11-07: with one row removed from the inventory (INJECTED), the first test named the missing file;
with a row for `tests/test_gone.py` added (INJECTED), the second named it. Each restored and green.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "test_inventory.json"


def _rows() -> set[str]:
    return {r["file"] for r in json.loads(INVENTORY.read_text(encoding="utf-8"))["rows"]}


def _files() -> set[str]:
    return {f"tests/{f.name}" for f in (ROOT / "tests").glob("test_*.py")}


def test_every_test_file_is_in_the_inventory():
    missing = sorted(_files() - _rows())
    assert missing == [], f"not in docs/test_inventory.json; run python scripts/test_inventory.py --write: {missing}"


def test_the_inventory_names_no_file_that_is_gone():
    gone = sorted(_rows() - _files())
    assert gone == [], f"docs/test_inventory.json names files that are gone: {gone}"
