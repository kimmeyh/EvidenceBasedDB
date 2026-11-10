"""Sprint 17 Manual Validation q20 = a: the unstarted ledger groups g297 to g329 split into one-paper groups
(`scripts/sprint17_q20_split.py`). The committed ledger is in the repository, so its checks run everywhere."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _load("q20", "sprint17_q20_split.py")


def _rec(rid: str) -> dict:
    return {"record_id": rid, "file": f"D:/papers/{rid}.pdf"}


def _groups() -> dict:
    return {"g296": {"records": [_rec("x")]},
            "g297": {"records": [_rec("a"), _rec("b")]},
            "g298": {"records": [_rec("c")]},
            "g330": {"records": [_rec("d")]}}


def test_each_paper_gets_its_own_group_and_the_old_group_keeps_a_dated_note_of_it():
    """Proven red 2026-11-09: with the note's records left out (INJECTED), the note was empty; with the old group's
    records kept (INJECTED), g297 still held "a" and "b"."""
    groups = _groups()
    moved = S.split(groups, set())
    assert [(g, r["record_id"], new) for g, r, new in moved] == [("g297", "a", "g331"), ("g297", "b", "g332"),
                                                                  ("g298", "c", "g333")]
    assert groups["g331"] == {"records": [_rec("a")]}
    assert groups["g297"]["records"] == []
    note = groups["g297"]["superseded"]
    assert note["decided"].startswith("2026-11-09 (Sprint 17 Manual Validation, q20 = a)")
    assert note["records"] == [{**_rec("a"), "moved_to": "g331"}, {**_rec("b"), "moved_to": "g332"}]
    assert groups["g296"] == {"records": [_rec("x")]} and groups["g330"] == {"records": [_rec("d")]}
    assert S.held_twice(groups) == []


def test_a_second_run_moves_nothing():
    """The q23 lesson (2026-11-09): a script run twice must not write twice. Proven red 2026-11-09: with the
    "superseded" skip removed (INJECTED), the second run replaced each old group's note with an empty one."""
    groups = _groups()
    S.split(groups, set())
    once = json.loads(json.dumps(groups))
    assert S.split(groups, set()) == []
    assert groups == once


def test_a_group_with_a_read_is_not_split():
    """Proven red 2026-11-09: with the applied check removed (INJECTED), g297 was split with "a" already read."""
    groups = _groups()
    with pytest.raises(ValueError, match="g297 has started"):
        S.split(groups, {("g297", "a")})


def test_the_committed_ledger_holds_each_record_in_one_group_and_each_note_points_at_its_group():
    """Guards the committed ledger after the split. Proven red 2026-11-09: with g349's record copied back into g297's
    records (INJECTED), the first assertion named it; with one note's moved_to changed to g999 (INJECTED), the second
    did."""
    groups = json.loads(S.LEDGER.read_text(encoding="utf-8"))["groups"]
    assert S.held_twice(groups) == []
    for g, body in groups.items():
        for r in body.get("superseded", {}).get("records", []):
            assert groups.get(r["moved_to"], {}).get("records") == [{"record_id": r["record_id"], "file": r["file"]}], \
                f"{g}: {r['record_id']} is not alone in {r['moved_to']}"


def test_a_group_with_a_review_a_reader_file_or_a_scratch_folder_is_not_split(tmp_path):
    """The fresh-eyes review of the split (2026-11-09): only the read check was tested. Proven red 2026-11-09: with
    `started` returning [] (INJECTED), each of the three groups was split."""
    from types import SimpleNamespace
    status = SimpleNamespace(REVIEWS=tmp_path / "reviews", WORK=tmp_path / "local")
    (tmp_path / "reviews").mkdir()
    (tmp_path / "local" / "reads").mkdir(parents=True)
    signs = {"a review": tmp_path / "reviews" / "g297.json",
             "a local reader file": tmp_path / "local" / "reads" / "group_g297.json",
             "a scratch folder": tmp_path / "local" / "tmp_g297"}
    for why, path in signs.items():
        path.mkdir() if why == "a scratch folder" else path.write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match=f"g297 has started \\({why}\\)"):
            S.split(_groups(), set(), status)
        path.rmdir() if why == "a scratch folder" else path.unlink()
    assert S.split(_groups(), set(), status)


def test_a_superseded_group_is_reported_as_superseded_and_its_papers_are_offered_in_their_new_groups(
        monkeypatch, tmp_path):
    """Proven red 2026-11-09: with the status script's superseded branch removed (INJECTED), g297 showed as "not
    started"; with f114_cloud's skip removed (INJECTED), the old brief's paper was offered again. The fresh-eyes
    review of the split found the moved papers offered by no reader: with the moved groups left out of
    `records()` (INJECTED), the new groups' papers were missing."""
    status = _load("g_status", "sprint13_g_status.py")
    groups = _groups()
    S.split(groups, set())
    assert status.state("g297", [], set(), groups["g297"].get("superseded")) == \
        ("superseded", "2 papers moved to g331 to g332")
    assert status.state("g296", ["x"], set(), groups["g296"].get("superseded"))[0] != "superseded"
    cloud = _load("f114_cloud", "f114_cloud.py")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": groups}), encoding="utf-8")
    briefs = tmp_path / "briefs"
    briefs.mkdir()
    for g in ("g296", "g297", "g298", "g330", "g331", "g332", "g333"):
        (briefs / f"{g}.json").write_text(json.dumps({"records": [{"record_id": f"brief-{g}"}]}), encoding="utf-8")
    monkeypatch.setattr(cloud, "LEDGER", ledger)
    monkeypatch.setattr(cloud, "BRIEFS", briefs)
    assert [(g, r["record_id"]) for g, r in cloud.records()] == [
        ("g296", "brief-g296"), ("g331", "brief-g331"), ("g332", "brief-g332"), ("g333", "brief-g333")]
