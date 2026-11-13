"""Sprint 17 Manual Validation q29 = b and q31 = a (team lead, 2026-11-10; `scripts/sprint17_q29_q31_grades.py`,
INTAKE_WORKFLOW.md section 76). The papers and the store live outside the repository, so the plan check is
live_store."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("q29", ROOT / "scripts" / "sprint17_q29_q31_grades.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _script()


def test_the_decisions_date_is_after_q23s_so_q23s_script_cannot_write_the_grades_back():
    """`sync_assertion` refuses a write dated before a row's latest Manual Validation decision; q23's script is dated
    2026-11-09, so its re-run keeps these grades. Proven red 2026-11-10: with TODAY set to 2026-11-09 (INJECTED), this
    test failed."""
    assert G.TODAY > G.q23.TODAY
    assert G.NOTE.startswith(f"{G.TODAY} (Sprint 17 Manual Validation, q29 = b and q31 = a)")


@pytest.mark.live_store
def test_albash_is_high_as_a_stated_limit_and_pere_stays_low_with_its_why():
    """Proven red 2026-11-10: with Albash given low_grade("field statement") again (INJECTED), the first assertion
    failed; with PERE_WHY left out of the Pere reason (INJECTED), the last one did."""
    texts: dict[str, str] = {}
    with G.connect(G.DB_PATH) as conn:
        plan = {rid: G.wanted(conn, rid, texts)[0] for rid in G.IDS}
    albash, pere = plan[G.ALBASH], plan[G.PERE]
    assert albash.certainty == "high" and "the paper's own stated limit (Section III.A.2, footnote 16" in \
        albash.certainty_reasons
    assert pere.certainty == "low" and pere.certainty_reasons.startswith("Started LOW: the authors' own claim")
    assert "a limit the authors state on their own null result" in pere.certainty_reasons
