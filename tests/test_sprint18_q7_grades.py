"""Sprint 18 Manual Validation q7 = a (team lead, 2026-11-22; `scripts/sprint18_q7_grades.py`, INTAKE_WORKFLOW.md
section 81): both of g361's device temperatures are LOW, each naming the contradiction. The papers and the store
live outside the repository, so the plan check is live_store."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("q7", ROOT / "scripts" / "sprint18_q7_grades.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _script()


def test_the_note_is_a_manual_validation_decision_so_a_reapply_of_g361_cannot_write_high_back():
    """`sync_assertion` refuses a write dated before a row's latest Manual Validation decision note. Proven red
    2026-11-22: with the note's "(Sprint 18 Manual Validation, q7 = a)" changed to "(Sprint 18 q7 = a)" (INJECTED),
    this test failed."""
    assert G.NOTE.startswith(f"{G.TODAY} (Sprint 18 Manual Validation, q7 = a)")
    assert G.DECIDED == {"certainty", "certainty_reasons"}


@pytest.mark.live_store
def test_both_temperatures_are_low_and_each_names_the_other():
    """Proven red 2026-11-22: with the 20 mK item left out of IDS (INJECTED), the first assertion failed; with the
    17 mK item's why naming no other item (INJECTED), the last one did."""
    texts: dict[str, str] = {}
    with G.connect(G.DB_PATH) as conn:
        plan = {rid: G.wanted(conn, rid, texts)[0] for rid in G.IDS}
    assert set(plan) == {G.T20, G.T17}
    for rid, other in ((G.T20, G.T17), (G.T17, G.T20)):
        a = plan[rid]
        assert a.certainty == "low" and a.certainty_reasons.startswith("Started LOW: the authors' own claim")
        assert "the paper contradicts itself" in a.certainty_reasons and other in a.certainty_reasons
