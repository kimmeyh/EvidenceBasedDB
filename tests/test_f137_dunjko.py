"""F137 (Sprint 16 Task E, team lead Q6 = 1): the two Dunjko records are one paper, held as one record."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from store import recheck

ROOT = Path(__file__).resolve().parents[1]
OLD = "dunjko-2017-machine-learning-artificial-intelligence-quantum"
NEW = "dunjko-2018-machine-learning-amp-artificial-intelligence"


def _apply():
    spec = importlib.util.spec_from_file_location("full_read_apply", ROOT / "scripts" / "full_read_apply.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_merged_records_rows_are_held_by_the_record_it_merged_into(monkeypatch):
    """g131's reader file still names dunjko-2017; its rows are entered, checked and owned under dunjko-2018.
    Proven to fail by injection, 2026-11-06: with `holder` returning the record itself, the row's provenance and its
    owner named dunjko-2017."""
    apply = _apply()
    paper = {"record_id": OLD, "existing": [], "assertions": [{
        "id_suggestion": "dunjko-test-row", "value": "Learning is hard", "anchor": "V.A.2, p.52",
        "quotes": ["learning is hard"], "claim_type": "positive", "result_type": "claim", "context": "qml"}]}
    monkeypatch.setattr(apply, "load_groups", lambda: [("g131", paper)])
    [(g, rec, owner, _)] = apply.assertions()
    assert owner == NEW and rec.provenance == f"{NEW}, V.A.2, p.52"
    assert apply.holder(NEW) == NEW and apply.holder("other-record") == "other-record"


def test_a_merged_record_is_never_set_back_to_read():
    """A rerun of g131 or of Sprint 11's task G leaves dunjko-2017 closed at seen: both appliers ask the same
    `store.merges.promotes`. Proven to fail by injection, 2026-11-06: with the MERGED_INTO condition removed from
    `promotes`, dunjko-2017 at seen was promoted (fresh-eyes review of Task E)."""
    apply = _apply()
    spec = importlib.util.spec_from_file_location("sprint11_reading", ROOT / "scripts" / "sprint11_reading.py")
    s11 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s11)
    for module in (apply, s11):
        assert not module.promotes(OLD, "seen") and module.holder(OLD) == NEW
        assert module.promotes(NEW, "seen") and module.promotes("other-record", "screened")
        assert not module.promotes("other-record", "read")


@pytest.mark.live_store
def test_the_dunjko_records_are_one(live_conn):
    """Proven to fail before the merge was applied, 2026-11-06: dunjko-2017 held 69 assertions at tier read."""
    tier, disposition = live_conn.execute("SELECT tier, disposition FROM paper_fields WHERE record_id = ?",
                                          (OLD,)).fetchone()
    assert tier == "seen" and disposition.startswith(f"Duplicate of {NEW}")
    assert not live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ?", (OLD,)).fetchone()
    assert not live_conn.execute("SELECT 1 FROM records WHERE class = 'assertion' AND provenance LIKE ?",
                                 (f"{OLD},%",)).fetchone()
    assert live_conn.execute("SELECT COUNT(*) FROM paper_yields WHERE paper_id = ?", (NEW,)).fetchone()[0] >= 73
    assert live_conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND "
                             "link_type = 'superseded-by'", (OLD, NEW)).fetchone()
    access, evidence = live_conn.execute("SELECT access, evidence FROM paper_fields WHERE record_id = ?",
                                         (NEW,)).fetchone()
    assert access.startswith("DOI:10.1088/1361-6633/aab406 | arXiv:1709.02779 | ")
    for rid in (OLD, NEW):  # the local-file check passes for both
        acc, ev = live_conn.execute("SELECT access, evidence FROM paper_fields WHERE record_id = ?",
                                    (rid,)).fetchone()
        assert recheck.check_local(acc, ev)[0] == "local copy present (SHA-256 unchanged)", (rid, acc)
