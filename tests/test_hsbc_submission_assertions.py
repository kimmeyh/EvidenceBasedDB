"""Sprint 2 Task B (F4 part 2): spot-check the store against the HSBC
submission's own determinations.

Before this task, the store held ZERO assertions related to the HSBC
fraud-detection work -- Task E's dry run only ingested the Lenat/Marcus
methodology paper, so Task B (as originally scoped, "spot-check the
store's assertions against what the HSBC submission itself determined")
had nothing to check. Team lead, 2026-09-17: extract real HSBC assertions
first, then check them.

ADR-0004's own motivating case names B1's variable count as a documented
figure-provenance defect (F52): "B1's variable count read 78 in three
places and 91 in two, in the same submission." This ingests the
CORRECTED figure (91) with the wrong one (78) retained as a
`contradicts`-linked record, so the correction is checkable in the store
itself, not only in prose -- which is the entire argument ADR-0004 makes
for building this store in the first place.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# Real data, read from a dump of the live store (ADR-0004 A7: no committed
# export). The whole module is live_store: it fails locally without the
# store and is deselected on CI.
pytestmark = pytest.mark.live_store
_DUMP: dict = {}


@pytest.fixture(autouse=True)
def _dump(live_export):
    _DUMP["dir"] = live_export


def _assertions() -> list[dict]:
    return json.loads((_DUMP["dir"] / "assertions.json").read_text(encoding="utf-8"))


def test_b1_variable_count_assertion_carries_the_corrected_value():
    assertions = _assertions()
    b1 = next(a for a in assertions if a["id"] == "hsbc-b1-variable-count")
    assert "91" in b1["value"]
    assert "78" not in b1["value"].split("not")[0]  # the corrected claim itself does not assert 78


def test_b1_variable_count_assertion_contradicts_the_wrong_value():
    """The documented defect (78) is retained as its own record, linked
    via `contradicts`, so the correction is a checkable relation in the
    store rather than a claim resting on prose alone -- ADR-0005 section
    2f's whole argument for the contradicts field."""
    assertions = _assertions()
    b1 = next(a for a in assertions if a["id"] == "hsbc-b1-variable-count")
    assert b1.get("contradicts") == ["hsbc-b1-variable-count-wrong-78"]

    wrong = next(a for a in assertions if a["id"] == "hsbc-b1-variable-count-wrong-78")
    assert "78" in wrong["value"]
    assert wrong["certainty"] == "very-low"


def test_b1_variable_count_provenance_names_the_real_source_document():
    assertions = _assertions()
    b1 = next(a for a in assertions if a["id"] == "hsbc-b1-variable-count")
    assert "PREREGISTRATION.md" in b1["provenance"]
    assert "A25" in b1["provenance"] or "A30" in b1["provenance"]


def test_b1_variable_count_certainty_is_high_not_assumed():
    """Certainty is HIGH because two independent internal review passes
    (A25, then A30 five days later) reached the same corrected figure --
    this must be stated in certainty_reasons, not just asserted as a
    bare 'high' with no audit trail (ADR-0004 section 3's whole argument
    for certainty_reasons over a bare confidence number)."""
    assertions = _assertions()
    b1 = next(a for a in assertions if a["id"] == "hsbc-b1-variable-count")
    assert b1["certainty"] == "high"
    assert b1.get("certainty_reasons"), "certainty is set with no certainty_reasons"
    assert "A25" in b1["certainty_reasons"] and "A30" in b1["certainty_reasons"]


def test_the_store_now_holds_at_least_one_hsbc_2026_context_assertion():
    """Regression test for the Task B scope gap itself: before this task,
    zero assertions carried the hsbc-2026 context, so there was nothing
    for a 'validate against the HSBC submission' task to check. This
    guards against that gap silently reopening."""
    assertions = _assertions()
    hsbc_context_assertions = [
        a for a in assertions
        if "hsbc-2026" in a.get("contexts", [])
    ]
    assert hsbc_context_assertions, "no assertion carries the hsbc-2026 context -- Task B's scope gap has reopened"
