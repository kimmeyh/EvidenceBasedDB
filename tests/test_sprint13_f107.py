"""Sprint 13 Task A (F107): the ".;" joins out of paper evidence, and the LOW
reasons of theoretical results named. INTAKE_WORKFLOW.md section 48."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_join_pattern_keeps_an_ellipsis_and_an_abbreviation():
    joins = _load("sprint13_f107_joins")
    assert joins.JOIN.sub("; ", "not reported.; Local copy x") == "not reported; Local copy x"
    assert joins.JOIN.sub("; ", "the title ...; Local copy x") == "the title ...; Local copy x"
    assert joins.JOIN.sub("; ", "Quantum Computing Inc.; Stevens") == "Quantum Computing Inc.; Stevens"


def test_a_theoretical_low_names_its_cause_not_an_empirical_result():
    """Proven to fail by injection, 2026-10-25: with the THEORY_LOW branch
    removed from certainty(), this test named all 5."""
    s12 = _load("sprint12_reading")
    assert len(s12.THEORY_LOW) == 5 and not set(s12.THEORY_LOW) & (set(s12.HIGH) | s12.FIELD_STATEMENTS)
    got = {a.id: a for _, a, _, _ in s12.assertions("G") if a.id in s12.THEORY_LOW}
    assert set(got) == set(s12.THEORY_LOW)
    bad = [i for i, a in got.items() if a.certainty != "low" or not a.certainty_reasons.startswith(s12.THEORY)
           or s12.THEORY_LOW[i] not in a.certainty_reasons]
    assert not bad, bad


@pytest.mark.live_store
def test_no_paper_evidence_holds_a_join(live_conn):
    """Proven to fail by injection, 2026-10-25: on the backup taken before
    the apply, this test named the 16 records."""
    joins = _load("sprint13_f107_joins")
    bad = [rid for rid, ev in live_conn.execute("SELECT record_id, evidence FROM paper_fields WHERE evidence LIKE "
                                                "'%.;%'") if joins.JOIN.search(ev)]
    assert not bad, bad


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    joins = _load("sprint13_f107_joins")
    conn = connect(live_copy)
    try:
        assert joins.apply_changes(conn) == ["nothing to correct"]
    finally:
        conn.close()
