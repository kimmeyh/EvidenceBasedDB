"""Sprint 14 Task E (F117): F114's per-paper cloud results assembled into group reader files."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _build(tmp_path: Path, monkeypatch, results: dict[str, list[dict]]):
    spec = importlib.util.spec_from_file_location("f117_build_groups", ROOT / "scripts" / "f117_build_groups.py")
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    work = tmp_path / "work"
    (work / "results").mkdir(parents=True)
    for rid, assertions in results.items():
        (work / "results" / f"{rid}.json").write_text(json.dumps({"papers": [{"record_id": rid, "assertions": assertions}]}),
                                                      encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {
        "g001": {"records": [{"record_id": "old"}]},
        "g076": {"records": [{"record_id": r} for r in ("a", "u")]},
        "g079": {"records": [{"record_id": r} for r in ("b", "abbas")]},
        "g080": {"records": [{"record_id": r} for r in ("c", "d")]}}}), encoding="utf-8")
    monkeypatch.setattr(b.cloud, "WORK", work)
    monkeypatch.setattr(b.cloud, "LEDGER", ledger)
    monkeypatch.setattr(b.cloud, "FIRST_GROUP", "g043")
    monkeypatch.setattr(b, "UNREAD", {"u": "page images only"})
    monkeypatch.setattr(b, "READS_DIR", tmp_path / "reads")
    (tmp_path / "reads").mkdir()
    return b


def test_only_whole_groups_are_built_and_ids_are_renamed(tmp_path, monkeypatch):
    """A group is built when every record has a result or the team lead's unread mark; a record only set aside from
    the cloud (abbas, read by Task F) holds its group back. Proven to fail by injection, 2026-10-30: with the build
    counting f114_cloud.UNREAD (which holds abbas) as unread, g079 was built; with the rename removed, the entry kept
    `id`."""
    b = _build(tmp_path, monkeypatch, {"a": [{"id": "x1"}], "b": [], "c": [{"id_suggestion": "y"}],
                                       "d": [{"id": "z", "id_suggestion": "z"}], "old": []})
    monkeypatch.setattr(b.cloud, "UNREAD", {"u": "page images only", "abbas": "set aside from the cloud"})
    assert b.buildable() == {"g076": ["a"], "g080": ["c", "d"]}
    assert b.main(["--write"]) == 0
    g076 = json.loads((tmp_path / "reads" / "group_g076.json").read_text(encoding="utf-8"))
    assert g076 == {"papers": [{"record_id": "a", "assertions": [{"id_suggestion": "x1"}]}]}
    g080 = json.loads((tmp_path / "reads" / "group_g080.json").read_text(encoding="utf-8"))
    assert [a for p in g080["papers"] for a in p["assertions"]] == [{"id_suggestion": "y"}, {"id_suggestion": "z"}]
    (tmp_path / "reads" / "group_g080.json").write_text("kept", encoding="utf-8")
    b.main(["--write"])
    assert (tmp_path / "reads" / "group_g080.json").read_text(encoding="utf-8") == "kept"


def test_two_different_ids_on_one_assertion_are_refused(tmp_path, monkeypatch):
    b = _build(tmp_path, monkeypatch, {"c": [{"id": "one", "id_suggestion": "two"}], "d": []})
    with pytest.raises(ValueError, match="two ids"):
        b.entry("c")
