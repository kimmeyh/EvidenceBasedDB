"""Sprint 17 Manual Validation q23 = a: the 8 Task E corrections (`scripts/sprint17_q23_corrections.py`, INTAKE_WORKFLOW.md
section 76). The papers and the store live outside the repository, so the checks against them are live_store."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("q23", ROOT / "scripts" / "sprint17_q23_corrections.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _script()


def test_the_plan_names_the_eight_findings_once_each():
    assert len(Q.IDS) == 8 == len(set(Q.IDS))
    assert not set(Q.ADD_QUOTES) & set(Q.SET_QUOTES)


def test_an_added_quote_is_held_once_however_often_the_script_applies():
    """The first version appended on every apply, so a second apply wrote the quotes twice (2026-11-09). Proven not
    vacuous, 2026-11-09: with the take-out loop removed, the twice-applied text held each added quote three times."""
    stored = '"a" (p.1)'
    added = [Q.q("b", "p.2"), Q.q("c", "p.3")]
    once = Q.with_added(stored, added)
    assert once == '"a" (p.1); "b" (p.2); "c" (p.3)'
    assert Q.with_added(once, added) == once
    assert Q.with_added(f"{once}; {added[0]}; {added[1]}", added) == once


@pytest.mark.live_store
def test_every_corrected_assertion_passes_the_quote_check_and_a_quote_not_in_the_paper_is_refused(monkeypatch):
    """Proven not vacuous, 2026-11-09: with one added Sar quote changed to words the paper does not hold, the check
    refused it and no write was planned."""
    texts: dict[str, str] = {}
    with Q.connect(Q.DB_PATH) as conn:
        plan = {rid: Q.wanted(conn, rid, texts)[0] for rid in Q.IDS}
        assert plan[Q.ALBASH].certainty == "low" and "a statement about the field" in plan[Q.ALBASH].certainty_reasons
        assert plan[Q.PERE].value == Q.PERE_VALUE and plan[Q.PERE].certainty == "low"
        assert plan[Q.RANDOM].claim_type == "positive" and plan[Q.RANDOM].search_scope is None
        bad = dict(Q.ADD_QUOTES)
        bad["sar-vqc-components"] = [Q.q("Measurement: Here, qubits are kept as quantum bits", Q.VQC)]
        monkeypatch.setattr(Q, "ADD_QUOTES", bad)
        with pytest.raises(ValueError, match="sar-vqc-components"):
            Q.wanted(conn, "sar-vqc-components", texts)
