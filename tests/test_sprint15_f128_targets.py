"""F128's manifest is the list j_records reads, so a dry run never writes it and an apply adds to it."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_only_an_apply_writes_the_manifest_and_it_keeps_what_an_earlier_apply_entered(tmp_path):
    """Fresh-eyes review, 2026-11-02: a dry run listed records the store did not hold, and a later apply replaced
    the list. Proven to fail by injection, 2026-11-03: with the apply test removed, the dry run wrote the manifest;
    with the earlier entries dropped, "a" was lost."""
    f128 = _load("sprint15_f128_targets")
    path = tmp_path / "manifest.json"
    first = [{"record_id": "a", "arxiv": "1"}, {"record_id": "b", "arxiv": "2"}]
    f128.record_entered(first, set(), apply=False, path=path)
    assert not path.exists()
    f128.record_entered(first, set(), apply=True, path=path)
    f128.record_entered([{"record_id": "b", "arxiv": "2v2"}, {"record_id": "c", "arxiv": "3"}], {"x"}, apply=True,
                        path=path)
    entered = json.loads(path.read_text(encoding="utf-8"))["entered"]
    assert [(e["record_id"], e["arxiv"]) for e in entered] == [("a", "1"), ("b", "2v2"), ("c", "3")]
