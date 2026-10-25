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
    """The fresh-eyes review of 6c6f0ac: the first pattern missed a join
    after a capital, "%" or a quote mark. Proven to fail by injection,
    2026-10-25: with the first pattern, `(?<=[a-z0-9)\\]])`, put back, this
    test failed on "AUC.;"."""
    joins = _load("sprint13_f107_joins")
    for end in ("not reported", "AUC", "5%", 'the "x"'):
        assert joins.JOIN.sub("; ", f"{end}.; Local copy x") == f"{end}; Local copy x", end
    assert joins.JOIN.sub("; ", "the title ...; Local copy x") == "the title ...; Local copy x"
    assert joins.JOIN.sub("; ", "Quantum Computing Inc.; Stevens") == "Quantum Computing Inc.; Stevens"


def test_a_theoretical_low_names_its_cause_not_an_empirical_result():
    """Proven to fail by injection, 2026-10-25: with the THEORY_LOW branch
    removed from certainty(), this test named all 5 (Task A). Task F's I2
    added 29 more and moved the text to store.grading.low_grade; the
    reasons begin with its "theoretical result" text."""
    from store.grading import LOW_BASES
    s12 = _load("sprint12_reading")
    first5 = ("larson-convergence-proved", "swaptest-qnn-two-layer-equivalent", "ld-daqc-unit-overlap-epsilon",
              "tree-unitarity-tradeoff-butterfly-velocity", "qcc-bounds-bures-entanglement-distance")
    assert set(first5) <= set(s12.THEORY_LOW) and len(s12.THEORY_LOW) == 34
    assert not set(s12.THEORY_LOW) & (set(s12.HIGH) | s12.FIELD_STATEMENTS)
    got = {a.id: a for t in ("F", "G") for _, a, _, _ in s12.assertions(t) if a.id in s12.THEORY_LOW}
    assert set(got) == set(s12.THEORY_LOW)
    start = f"Started LOW: {LOW_BASES['theoretical result']}: "
    bad = [i for i, a in got.items() if a.certainty != "low" or not a.certainty_reasons.startswith(start)
           or s12.THEORY_LOW[i] not in a.certainty_reasons]
    assert not bad, bad


@pytest.mark.live_store
def test_no_stored_text_holds_a_join(live_conn):
    """Every text column of the paper and assertion tables, not only
    `paper_fields.evidence` (the fresh-eyes review of 6c6f0ac). Proven to
    fail by injection, 2026-10-25: on the backup taken before the apply,
    this test named the 16 records."""
    joins = _load("sprint13_f107_joins")
    bad = []
    for table, key in (("paper_fields", "record_id"), ("paper_reads", "record_id"), ("paper_probes", "record_id"),
                       ("records", "id"), ("assertion_fields", "record_id")):
        for _, col, kind, *_ in live_conn.execute(f"PRAGMA table_info({table})"):
            if kind.upper() not in ("TEXT", ""):
                continue
            bad += [f"{table}.{col}: {rid}" for rid, v in live_conn.execute(
                f"SELECT {key}, {col} FROM {table} WHERE {col} LIKE '%.; Local copy%'") if joins.JOIN.search(v)]
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
