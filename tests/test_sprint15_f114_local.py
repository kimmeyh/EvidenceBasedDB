"""Sprint 15 Task H: the 100 papers' briefs (scripts/sprint15_f114_local.py). The real ledger and store are not
opened here."""
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


def test_the_plan_re_enters_the_unread_then_takes_ledger_order_past_a_directory(tmp_path, monkeypatch):
    """Re-entry groups first, holding exactly what each review left unread; then ledger order from FIRST, with a
    directory source (a code repository) left for a later release and the count kept. Proven to fail by injection,
    2026-11-01: with the is_dir test removed, the repository was planned and check() refused it as no local file."""
    local = _load("sprint15_f114_local")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "g001.json").write_text(json.dumps({"unread": {"u1": "why"}}))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF")
    repo = tmp_path / "repo"
    repo.mkdir()
    ledger = {"g001": {"records": [{"record_id": "u1", "file": str(pdf)}]},
              "g002": {"records": [{"record_id": "a", "file": str(pdf)}, {"record_id": "r", "file": str(repo)},
                                   {"record_id": "b", "file": str(pdf)}]},
              "g003": {"records": [{"record_id": "c", "file": str(pdf)}, {"record_id": "d", "file": str(pdf)}]}}
    monkeypatch.setattr(local, "REVIEWS_DIR", reviews)
    monkeypatch.setattr(local, "REENTER", ("g001",))
    monkeypatch.setattr(local, "FIRST", "g002")
    monkeypatch.setattr(local, "TOTAL", 4)
    groups, later = local.plan(ledger)
    assert {g: [r["record_id"] for r in rs] for g, rs in groups.items()} == {"g001-r1": ["u1"], "g002": ["a", "b"],
                                                                             "g003": ["c"]}
    assert later == ["r"]
    assert local.check(groups) == []


def test_task_i_takes_ledger_order_from_its_first_group_and_never_js_groups(tmp_path):
    """Task I (F133): no re-entry groups, ledger order from its first group, a directory left for later, stopping at
    its total, and never a record of Task J's groups, which follow H's in the ledger. Proven to fail by injection,
    2026-11-02: with the J bound removed from plan(), g331's record was planned."""
    local = _load("sprint15_f114_local")
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF")
    repo = tmp_path / "repo"
    repo.mkdir()
    ledger = {"g133": {"records": [{"record_id": "h", "file": str(pdf)}]},
              "g134": {"records": [{"record_id": "a", "file": str(pdf)}, {"record_id": "r", "file": str(repo)}]},
              "g135": {"records": [{"record_id": "b", "file": str(pdf)}]},
              "g331": {"records": [{"record_id": "j", "file": str(pdf)}]}}
    groups, later = local.plan(ledger, "g134", 3, ())
    assert {g: [r["record_id"] for r in rs] for g, rs in groups.items()} == {"g134": ["a"], "g135": ["b"]}
    assert later == ["r"]
    assert local.check(groups, 3) == ["the briefs hold 2 papers, not 3"]
    groups, _ = local.plan(ledger, "g134", 1, ())
    assert local.check(groups, 1) == []


def test_a_task_j_record_needs_a_local_file_and_a_store_row(tmp_path, monkeypatch):
    """Fresh-eyes review, 2026-11-02: j_records took the first access part ending ".pdf", which could be a URL, and
    an unknown record gave a bare TypeError. Proven to fail by injection, 2026-11-02: with the is_file test removed,
    the URL was taken as the file."""
    import sqlite3
    local = _load("sprint15_f114_local")
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF")
    manifest = tmp_path / "f128.json"
    manifest.write_text(json.dumps({"entered": [{"record_id": "web"}, {"record_id": "here"}]}))
    monkeypatch.setattr(local, "F128", manifest)
    monkeypatch.setattr(local, "FARYAD", "here")
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE paper_fields (record_id TEXT, access TEXT)")
    conn.executemany("INSERT INTO paper_fields VALUES (?, ?)",
                     [("web", "https://example.org/a.pdf"), ("here", f"arXiv:1 | {pdf}")])
    try:
        local.j_records(conn)
    except ValueError as e:
        assert "web: no local file" in str(e)
    else:
        raise AssertionError("a URL ending .pdf was taken as a local file")
    conn.execute("UPDATE paper_fields SET record_id = 'gone' WHERE record_id = 'web'")
    try:
        local.j_records(conn)
    except ValueError as e:
        assert "web: no paper record" in str(e)
    else:
        raise AssertionError("an unknown record was not refused")


def test_task_js_groups_are_added_once_after_the_last_group_and_never_over_a_held_record(tmp_path, monkeypatch):
    """Task J's records go into the ledger as g331 (five) and g332 (the rest), once: a second run reads them back,
    a ledger holding only one of them or already past g330 is refused, and so is a record another group holds.
    Proven to fail by injection, 2026-11-02: with the held-record test removed, the third case added the groups."""
    local = _load("sprint15_f114_local")
    recs = [{"record_id": f"j{i}", "file": "x.pdf"} for i in range(9)]
    monkeypatch.setattr(local, "j_records", lambda conn: recs)
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"groups": {"g330": {"records": [{"record_id": "z"}]}}}))
    monkeypatch.setattr(local, "LEDGER", path)
    groups = local.add_j_groups({"g330": {"records": [{"record_id": "z"}]}}, None, write=True)
    assert {g: [r["record_id"] for r in rs] for g, rs in groups.items()} == {
        "g331": ["j0", "j1", "j2", "j3", "j4"], "g332": ["j5", "j6", "j7", "j8"]}
    written = json.loads(path.read_text())["groups"]
    assert local.add_j_groups(written, None, write=True) == groups
    for bad in ({"g330": {"records": []}, "g331": {"records": []}},
                {"g333": {"records": []}},
                {"g330": {"records": [{"record_id": "j3"}]}}):
        try:
            local.add_j_groups(bad, None, write=False)
        except ValueError:
            continue
        raise AssertionError(f"{sorted(bad)} was not refused")
