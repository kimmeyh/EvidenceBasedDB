"""Sprint 15 Task K (F124): Phase 2's F151, F153 and F154 repointed at develop af03165 (INTAKE_WORKFLOW.md section
62)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("f124", ROOT / "scripts" / "sprint15_f124_phase2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.live_store
def test_the_three_records_pass_the_local_file_check_and_keep_their_first_read(live_conn):
    """Proven to fail by injection, 2026-11-01: on the store before the apply (the verified backup), all three read
    "local copy changed"."""
    from store.recheck import check_local
    f124 = _script()
    for rid, _, _, _, _, old_sha, _ in f124.DOCS.values():
        access, evidence = live_conn.execute("SELECT access, evidence FROM paper_fields WHERE record_id = ?",
                                             (rid,)).fetchone()
        assert check_local(access, evidence) == ("local copy present (SHA-256 unchanged)", ""), rid
        assert old_sha in evidence and "10086da" in evidence, rid


@pytest.mark.live_store
def test_every_stored_quote_is_verbatim_at_af03165_and_a_second_apply_writes_nothing(live_conn, live_copy):
    from store import connect
    f124 = _script()
    assert f124.check_hashes() == []
    assert len(f124.verify_all(live_conn)) == 5
    conn = connect(live_copy)
    try:
        assert f124.apply_changes(conn) == []
    finally:
        conn.close()
