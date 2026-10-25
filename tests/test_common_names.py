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

import re

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
    "Cloudflare R2 storage costs below $0.01",
    "In R2, accuracy was 0.9",
    "R1 and R2 exceed 0.5",
    "constraint R2 holds",
    "R2 = R1 + 0.5",
    "a map from R^2 to R",
])
def test_a_label_named_R2_is_never_glossed(label):
    """Proven to fail, 2026-10-25: on ce95e82's rule the first four gained
    "(R squared)"; on 8c869cc's 40-character window the next five did."""
    assert with_common_names(label) == label


# Each label carries a statistic beside it, so only its label guard keeps it bare.
GUARDED = [
    ("rule R2 above 0.5", "_LABEL_BEFORE"),
    ("Table R2 values", "_LABEL_BEFORE"),
    ("region R2 above 3.5 ms", "_LABEL_BEFORE"),
    ("R1, R2 = 0.3", "_LABEL_BEFORE"),
    ("the best R2, R3 pair", "_LABEL_AFTER"),
    ("the best R2 and R3 pair", "_LABEL_AFTER"),
]


@pytest.mark.parametrize("label, guard", GUARDED)
def test_a_label_beside_a_statistic_is_kept_bare_by_its_guard(label, guard, monkeypatch):
    """The review of 8c869cc found that three of the four label cases above
    stayed bare with both label guards removed, so they guarded nothing.
    Each case here is bare with its guard and glossed without it: the test
    removes the guard itself, so it stays proven red."""
    from store import common_names
    assert with_common_names(label) == label
    monkeypatch.setattr(common_names, guard, re.compile(r"(?!)"))
    assert with_common_names(label) != label, f"{label!r} stays bare without {guard}: it does not test it"


@pytest.mark.parametrize("value, glossed", [
    ("an R-squared value of 0.9959", "an R-squared (R squared) value of 0.9959"),
    ("R^2 = 0.9", "R^2 (R squared) = 0.9"),
    ("R² of 0.8", "R² (R squared) of 0.8"),
    ("the R2-score is 0.7", "the R2-score (R squared) is 0.7"),
    ("the saturated R2 value drops", "the saturated R2 (R squared) value drops"),
    ("score the learned model by R2 on a test set", "score the learned model by R2 (R squared) on a test set"),
    ("MSE 0.1; R2: 0.93", "MSE 0.1; R2 (R squared): 0.93"),
    ("r-squared 0.8", "r-squared (R squared) 0.8"),
    ("R2-scores were 0.4", "R2-scores (R squared) were 0.4"),
    ("R2_score 0.4", "R2_score (R squared) 0.4"),
    ("coefficient of determination 0.8", "coefficient of determination (R squared) 0.8"),
    ("D² sampling", "D² sampling (D squared sampling)"),
])
def test_every_spelling_of_the_statistic_gains_the_name(value, glossed):
    """Proven to fail, 2026-10-25: on ce95e82's rule the first four were
    left without the common name; on 8c869cc's rule the last six were."""
    assert with_common_names(value) == glossed
    assert with_common_names(glossed) == glossed
    assert bare(glossed) == []


@pytest.mark.parametrize("value, glossed", [
    ("R^2_adj = 0.9", "R^2_adj (R squared) = 0.9"),
    ("R²adj 0.8", "R²adj (R squared) 0.8"),
    ("$R^2$ = 0.9", "$R^2$ (R squared) = 0.9"),
])
def test_the_name_follows_the_whole_token(value, glossed):
    """The review of 8c869cc found the name inserted inside a token ("R^2
    (R squared)_adj"), which breaks a search for the paper's own token.
    Proven to fail, 2026-10-25: on 8c869cc's rule each was split."""
    assert with_common_names(value) == glossed


@pytest.mark.live_store
def test_every_stored_value_with_a_paper_spelling_carries_its_common_name(live_conn):
    """Proven to fail, 2026-10-25: run against the live store before the
    Q4 apply (its first backup), this test named the 18 values (17 with
    R2, 1 with D2-sampling); after the review's widening, and before its
    apply, it named otgonbaatar-cp-decomposition-hsi ("R-squared")."""
    values = live_conn.execute("SELECT id, value FROM records WHERE class = 'assertion'").fetchall()
    missing = [rid for rid, value in values if bare(value)]
    assert missing == [], f"values with no common name: {missing}"
