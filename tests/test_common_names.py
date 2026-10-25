"""Team lead, 2026-10-25, at Sprint 13 Manual Validation (Q4): "keep how the
paper does them and then put in parenthasses the more common name for them so
that we can query the database and still find all occurances of R2, R
squared". store.common_names adds the common name after the paper's own
spelling; store.ingest applies it on every insert and sync, so a value
entered later carries it too.

The fresh-eyes review of ce95e82 found that a bare "R2" is also a label in
the active consumer's documents ("R2: exact weight below t", "research R2",
"R1, R2, R4"), which the first rule glossed as R squared, and that
"R-squared", "R^2", "R²" and "R2-score" were missed."""
from __future__ import annotations

import pytest

from store.common_names import bare, with_common_names


def test_the_paper_spelling_stays_and_the_common_name_follows_once():
    assert with_common_names("a predictive R2 above 0.64") == "a predictive R2 (R squared) above 0.64"
    assert with_common_names("the D2-sampling step") == "the D2-sampling (D squared sampling) step"
    once = with_common_names("a predictive R2 above 0.64")
    assert with_common_names(once) == once, "a second pass adds the name again"
    assert with_common_names("the R2-norm and DR2 stay") == "the R2-norm and DR2 stay"


@pytest.mark.parametrize("label", [
    "rule R2 of the protocol",
    "R2: exact weight below t",
    "research R2 asks whether",
    "R1, R2, R4, R7-R10",
])
def test_a_label_named_R2_is_never_glossed(label):
    """Proven to fail, 2026-10-25: on ce95e82's rule each of these gained
    "(R squared)"."""
    assert with_common_names(label) == label


@pytest.mark.parametrize("value, glossed", [
    ("an R-squared value of 0.9959", "an R-squared (R squared) value of 0.9959"),
    ("R^2 = 0.9", "R^2 (R squared) = 0.9"),
    ("R² of 0.8", "R² (R squared) of 0.8"),
    ("the R2-score is 0.7", "the R2-score (R squared) is 0.7"),
    ("the saturated R2 value drops", "the saturated R2 (R squared) value drops"),
    ("score the learned model by R2 on a test set", "score the learned model by R2 (R squared) on a test set"),
])
def test_every_spelling_of_the_statistic_gains_the_name(value, glossed):
    """Proven to fail, 2026-10-25: on ce95e82's rule the first four were
    left without the common name."""
    assert with_common_names(value) == glossed
    assert with_common_names(glossed) == glossed
    assert bare(glossed) == []


@pytest.mark.live_store
def test_every_stored_value_with_a_paper_spelling_carries_its_common_name(live_conn):
    """Proven to fail, 2026-10-25: run against the live store before the
    Q4 apply (its first backup), this test named the 18 values (17 with
    R2, 1 with D2-sampling); after the review's widening, and before its
    apply, it named otgonbaatar-cp-decomposition-hsi ("R-squared")."""
    values = live_conn.execute("SELECT id, value FROM records WHERE class = 'assertion'").fetchall()
    missing = [rid for rid, value in values if bare(value)]
    assert missing == [], f"values with no common name: {missing}"
