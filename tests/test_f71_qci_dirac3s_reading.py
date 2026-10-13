"""F71 (Sprint 8 Task G): every quote in the Dirac-3S release, benchmarking
review and product-page assertions is in its source's local copy; the
admission-against-interest candidates stay un-upgraded until the team lead
decides (Class 2); the site check's lists are computed, not hand-made."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _text  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.live_store
def test_every_quote_is_in_a_yielding_source(live_conn):
    """Proven to fail by injection, 2026-10-13: with one digit of the
    "7.56" Table 6 row changed in the stored citation_context of a copy,
    this test named dirac3s-all-optimal-headline-contradicted-by-own-table."""
    f71 = _load("sprint8_f71_qci_dirac3s_reading")
    checked = 0
    for assertion, yielded_by in f71.ASSERTIONS:
        row = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                (assertion.id,)).fetchone()
        assert row, f"{assertion.id}: not in the store"
        quotes = _QUOTE.findall(row[0])
        assert quotes, f"{assertion.id}: no quote found"
        texts = [_text(f71.LOCAL[r]) for r in yielded_by]
        for q in quotes:
            assert any(q in t for t in texts), f"{assertion.id}: not verbatim in its sources: {q[:70]}"
            checked += 1
    assert checked >= 20


@pytest.mark.live_store
def test_the_candidates_are_held_for_the_team_lead(live_conn):
    """Plan, Task G risks: an admission-against-interest upgrade is the team
    lead's decision; nothing in this task raises one."""
    f71 = _load("sprint8_f71_qci_dirac3s_reading")
    by_id = {a.id: a for a, _ in f71.ASSERTIONS}
    for rid in f71.CANDIDATE_UPGRADES:
        assert rid in by_id, rid
        certainty, reasons = live_conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?",
                                               (rid,)).fetchone()
        assert certainty == "moderate" and "UPGRADED" not in reasons, f"{rid}: {certainty}"


def test_the_site_check_separates_menu_changes_from_page_changes():
    """A difference found on half or more of the compared pages (the site's
    new "Benchmarking" menu entry) is not a page change. Proven to fail by
    injection, 2026-10-13: with site_wide returning an empty set, the
    menu-only page was counted as changed."""
    g = _load("sprint8_f71_qci_site_check")
    menu = g.word_changes("Home Lessons Qudits are levels", "Home Lessons Benchmarking Qudits are levels")
    real = g.word_changes("Introducing Dirac-3 949 Variables", "Introducing Dirac-3S 9,980 Variables")
    diffs = {"a": menu, "b": menu, "c": menu | real}
    chrome = g.site_wide(diffs)
    assert [u for u, d in diffs.items() if d - chrome] == ["c"]
