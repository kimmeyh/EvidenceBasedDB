"""Sprint 14 retrospective Q7 (INTAKE_WORKFLOW.md section 59): one period, not two, before "NOT upgraded"."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from store.grading import low_grade
from store.ingest import FORMAT_ONLY_MARK, FULL_READ_MARK, last_change

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("q7", ROOT / "scripts" / "sprint14_q7_doubled_period.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_why_that_ends_in_a_period_gives_one_period():
    """Proven to fail by injection, 2026-10-31: with low_grade joining the why as before, the reason ended
    ".. NOT upgraded"."""
    _, reason = low_grade("theoretical result", "the proof is a sketch.")
    assert reason.endswith("the proof is a sketch. NOT upgraded")
    _, reason = low_grade("theoretical result", "as in Smith et al.")
    assert reason.endswith("as in Smith et al. NOT upgraded")
    assert low_grade("theoretical result", "no period")[1].endswith("no period. NOT upgraded")


def test_the_last_change_skips_a_format_only_note():
    """A format-only note must not take a full read's ownership of a record away: the sync's same-day guard and the
    reading tests ask for the last change. Proven to fail by injection, 2026-10-31: with last_change taking the last
    note as it stands, the format note was returned."""
    full = f"2026-10-31 (x): {FULL_READ_MARK}: confirmed from p"
    fmt = f"2026-10-31 (Sprint 14 retrospective Q7): {FORMAT_ONLY_MARK} a doubled period made single"
    assert last_change(f"older | {full} | {fmt}") == full
    assert last_change(f"older | {fmt} | {full}") == full
    assert last_change(f"{fmt}") == ""
    assert last_change(None) == ""


def test_a_format_note_leaves_a_full_read_as_it_was_for_the_sync_guard(synthetic_store):
    """Fresh-eyes review of 7b2179f: the format note moved `updated` to 2026-10-31, so a corrected sign-off dated on
    its 2026-10-30 review day fell under the guard's date branch and was dropped without a word (365 live rows).
    Proven to fail by injection, 2026-10-31: with the guard reading `updated` as before, the correction returned []."""
    from dataclasses import replace
    from store import connect
    from store.ingest import append_updated_reason, sync_assertion
    from tests.test_quotes_and_sync import _stored
    conn = connect(synthetic_store)
    try:
        full = replace(_stored(conn), value="the value from the whole paper")
        assert "value" in sync_assertion(conn, full, f"2026-10-30 (x): {FULL_READ_MARK}: corrected", "2026-10-30")
        append_updated_reason(conn, "claim-one", f"2026-10-31 (Q7): {FORMAT_ONLY_MARK} a period", "2026-10-31")
        older = replace(full, value="an older script's value")
        assert sync_assertion(conn, older, "2026-10-30 (an older script): entered", "2026-10-30") == []
        fixed = replace(full, value="the corrected sign-off's value")
        assert sync_assertion(conn, fixed, f"2026-10-30 (x): {FULL_READ_MARK}: corrected again",
                              "2026-10-30") == ["value"]
        assert sync_assertion(conn, older, "2026-10-25 (an older script): entered", "2026-10-25") == []
        assert conn.execute("SELECT value FROM records WHERE id = 'claim-one'").fetchone()[0] == fixed.value
    finally:
        conn.close()


def test_the_store_fix_changes_the_doubled_period_and_nothing_else(synthetic_store):
    """Proven to fail by injection, 2026-10-31: with the replace written as ". NOT upgraded" to ".. NOT upgraded"
    swapped, the fixed reason kept its doubled period."""
    from store import connect
    q7 = _script()
    conn = connect(synthetic_store)
    try:
        rid = conn.execute("SELECT id FROM records ORDER BY id LIMIT 1").fetchone()[0]
        before = "Started LOW: a theoretical result: a sketch.. NOT upgraded"
        conn.execute("UPDATE records SET certainty_reasons = ?, updated_reason = 'first' WHERE id = ?", (before, rid))
        assert [tuple(r) for r in q7.doubled(conn)] == [(rid, before)]
        assert q7.apply_changes(conn) == [f"fixed {rid}"]
        reasons, updated, note = conn.execute("SELECT certainty_reasons, updated, updated_reason FROM records "
                                              "WHERE id = ?", (rid,)).fetchone()
        assert reasons == "Started LOW: a theoretical result: a sketch. NOT upgraded"
        assert (updated, note) == (q7.TODAY, f"first | {q7.NOTE}")
        assert FORMAT_ONLY_MARK in q7.NOTE
        assert q7.doubled(conn) == [] and q7.apply_changes(conn) == []
        # fresh-eyes review of 7b2179f: an ellipsis is the why's own text, not a doubled period
        conn.execute("UPDATE records SET certainty_reasons = ? WHERE id = ?",
                     ("Started LOW: a theoretical result: and so on... NOT upgraded", rid))
        assert q7.doubled(conn) == []
    finally:
        conn.close()


@pytest.mark.live_store
def test_no_stored_reason_holds_a_doubled_period(live_conn):
    """Proven to fail, 2026-10-31: before the apply, 900 records held it. An ellipsis is a why's own text."""
    q7 = _script()
    rows = [r[0] for r in live_conn.execute(
        "SELECT id, certainty_reasons FROM records WHERE instr(certainty_reasons, '.. NOT upgraded') > 0")
        if q7.DOUBLED.search(r[1])]
    assert rows == [], f"{len(rows)} records, first {rows[:5]}"
