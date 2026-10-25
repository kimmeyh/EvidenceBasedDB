"""Team lead, 2026-10-25, at Sprint 13 Manual Validation (Q4): "keep how the
paper does them and then put in parenthasses the more common name for them so
that we can query the database and still find all occurances of R2, R
squared". store.common_names adds the common name after the paper's own
spelling; store.ingest applies it on every insert and sync, so a value
entered later carries it too."""
from __future__ import annotations

import re

import pytest

from store.common_names import COMMON_NAMES, with_common_names


def test_the_paper_spelling_stays_and_the_common_name_follows_once():
    assert with_common_names("a predictive R2 above 0.64") == "a predictive R2 (R squared) above 0.64"
    assert with_common_names("the D2-sampling step") == "the D2-sampling (D squared sampling) step"
    once = with_common_names("a predictive R2 above 0.64")
    assert with_common_names(once) == once, "a second pass adds the name again"
    assert with_common_names("the R2-norm and DR2 stay") == "the R2-norm and DR2 stay"


@pytest.mark.live_store
def test_every_stored_value_with_a_paper_spelling_carries_its_common_name(live_conn):
    """Proven to fail, 2026-10-25: run against the live store before the
    Q4 apply (its first backup), this test named the 18 values (17 with
    R2, 1 with D2-sampling)."""
    values = live_conn.execute("SELECT id, value FROM records WHERE class = 'assertion'").fetchall()
    bare = []
    for rid, value in values:
        for pattern, common in COMMON_NAMES:
            if re.search(pattern + rf"(?! \({re.escape(common)}\))", value):
                bare.append(rid)
    assert bare == [], f"values with no common name: {bare}"
