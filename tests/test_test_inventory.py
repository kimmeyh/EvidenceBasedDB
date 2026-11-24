"""F140 part 1 (Sprint 17 Task A): the test inventory (`docs/test_inventory.json`, written by
`scripts/test_inventory.py`) names every test file, names no file that is gone, and holds no computed field that
differs from what the script computes now (review of 5454ccb: "Determinate facts are COMPUTED, never stored", so a
stored copy is checked against its computation). Only the tests and seconds, a snapshot of one timed run, are not
compared.

Proven red 2026-11-07: with one row removed from the inventory (INJECTED), the first test named the missing file;
with a row for `tests/test_gone.py` added (INJECTED), the second named it; with one row's kind changed by hand
(INJECTED), the third named the row and the field. Each restored and green.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "test_inventory.json"


def _stored() -> dict[str, dict]:
    return {r["file"]: r for r in json.loads(INVENTORY.read_text(encoding="utf-8"))["rows"]}


def _files() -> set[str]:
    return {f"tests/{f.name}" for f in (ROOT / "tests").glob("test_*.py")}


def _script():
    spec = importlib.util.spec_from_file_location("test_inventory_script", ROOT / "scripts" / "test_inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_test_file_is_in_the_inventory():
    missing = sorted(_files() - set(_stored()))
    assert missing == [], f"not in docs/test_inventory.json; run python scripts/test_inventory.py --write: {missing}"


def test_the_inventory_names_no_file_that_is_gone():
    gone = sorted(set(_stored()) - _files())
    assert gone == [], f"docs/test_inventory.json names files that are gone: {gone}"


def test_every_computed_field_matches_its_computation():
    script = _script()
    stored = _stored()
    drift = [f"{row['file']}: {field}" for row in script.inventory() if row["file"] in stored
             for field in script.COMPUTED if stored[row["file"]].get(field) != row[field]]
    assert drift == [], f"stale; run python scripts/test_inventory.py --junit FILE --write: {drift}"


def test_a_write_without_junit_keeps_the_recorded_timings():
    """Sprint 18 retrospective i2: a file already listed keeps its tests and seconds, a new file has none, and the
    run the seconds came from is still named. Proven red 2026-11-23: with `keep_timings` returning without copying
    (INJECTED), this test named the lost seconds; restored and green."""
    script = _script()
    old = {"timings_from": "a timed run", "rows": [{"file": "tests/test_a.py", "tests": 3, "seconds": 1.5}]}
    rows = [{"file": "tests/test_a.py", "tests": None, "seconds": None},
            {"file": "tests/test_new.py", "tests": None, "seconds": None}]
    assert script.keep_timings(rows, old) == "a timed run"
    assert rows == [{"file": "tests/test_a.py", "tests": 3, "seconds": 1.5},
                    {"file": "tests/test_new.py", "tests": None, "seconds": None}], f"timings lost: {rows}"
