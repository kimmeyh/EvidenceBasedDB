"""Sprint 15 Manual Validation: the team lead's decisions written by
`scripts/sprint15_mv_decisions.py` (INTAKE_WORKFLOW.md section 67)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("mv15", ROOT / "scripts" / "sprint15_mv_decisions.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_f129_proposal_names_its_basis():
    """Q2 = 1 sets each proposal HIGH on the basis it names; a proposal with
    no basis in store.grading.BASES stops the script."""
    from store.grading import BASES
    targets = _script().f129_targets()
    assert len(targets) == 10
    assert {b for b, _ in targets.values()} <= set(BASES)


@pytest.mark.live_store
def test_the_store_holds_each_decision_and_a_second_run_writes_nothing(live_conn):
    mv = _script()
    for aid in mv.f129_targets():
        assert live_conn.execute("SELECT certainty FROM records WHERE id = ?", (aid,)).fetchone()[0] == "high", aid
    for aid in mv.ABSENCE:
        assert live_conn.execute("SELECT certainty FROM records WHERE id = ?", (aid,)).fetchone()[0] == "moderate", aid
    aid, old, new = mv.CONTEXT_MOVE
    assert {r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (aid,))} \
        == {new}
    assert mv.planned(live_conn) == []


@pytest.mark.live_store
def test_a_rerun_of_the_full_read_applier_keeps_each_decision(live_copy):
    """The applier still holds these rows at their reviews' grades (LOW). Its
    sync is refused because each decision is dated after the review. Proven
    to fail, 2026-11-05: on a store copy with gilfuster-no-experiments'
    decision redated 2026-11-04 (g144's review day), the applier's sync
    changed its certainty and reasons back to LOW. The script was first
    applied dated 2026-11-04; the store was restored from the backup it
    took and the script re-run dated 2026-11-05."""
    from store import connect
    from store.ingest import sync_assertion
    spec = importlib.util.spec_from_file_location("fra", ROOT / "scripts" / "full_read_apply.py")
    fra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fra)
    mv = _script()
    ids = set(mv.f129_targets()) | set(mv.ABSENCE)
    rows = [a for _, a, _, _ in fra.assertions() if a.id in ids]
    assert len(rows) == 12
    conn = connect(live_copy)
    try:
        for a in rows:
            assert sync_assertion(conn, a, a.updated_reason, a.updated) == [], a.id
        assert mv.planned(conn) == []
    finally:
        conn.rollback()
        conn.close()


@pytest.mark.live_store
def test_a_later_review_of_the_row_keeps_the_team_leads_grade(monkeypatch, live_copy):
    """The date guard alone would let a review dated after the decision write
    the review's LOW back (fresh-eyes review, 2026-11-05). The applier keeps a
    grade whose reasons carry TEAM_LEAD_GRADE unless the review's reasons
    carry it too. Proven to fail by injection, 2026-11-05: with that rule
    removed, the row went back to LOW."""
    from dataclasses import replace
    from store import connect
    from store.quotes import Verified
    spec = importlib.util.spec_from_file_location("fra", ROOT / "scripts" / "full_read_apply.py")
    fra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fra)
    aid = _script().ABSENCE[0]
    [(_, a, rid, p)] = [x for x in fra.assertions() if x[1].id == aid]
    a = replace(a, updated="2026-12-01", updated_reason=f"2026-12-01 (a later review): {fra.FULL_READ_MARK}: regraded")
    monkeypatch.setattr(fra, "verify", lambda conn=None: [(a, rid, p, Verified(aid, a.citation_context, a.value))])
    monkeypatch.setattr(fra, "load_groups", lambda: [])
    monkeypatch.setattr(fra, "write_anchor_moves", lambda c, refused=None: [])
    conn = connect(live_copy)
    try:
        fra.apply_changes(conn)
        assert conn.execute("SELECT certainty FROM records WHERE id = ?", (aid,)).fetchone()[0] == "moderate"
    finally:
        conn.rollback()
        conn.close()


@pytest.mark.live_store
def test_a_decision_the_store_lost_is_written_again(live_copy):
    """Proven to fail the other way by construction: with one F129 row put
    back to LOW and one absence item to LOW on a store copy, the script
    plans exactly those two, and a run after writes nothing."""
    from store import connect
    mv = _script()
    first = next(iter(mv.f129_targets()))
    conn = connect(live_copy)
    try:
        conn.execute("UPDATE records SET certainty = 'low' WHERE id IN (?, ?)", (first, mv.ABSENCE[0]))
        assert sorted(x[0] for x in mv.planned(conn)) == sorted([first, mv.ABSENCE[0]])
        assert len(mv.apply_changes(conn)) == 2
        assert mv.planned(conn) == []
    finally:
        conn.rollback()
        conn.close()
