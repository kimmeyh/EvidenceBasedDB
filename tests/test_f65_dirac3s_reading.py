"""F65 with F63 (Sprint 8 Task C): every Dirac-3S and F63 assertion quotes
a source read directly, the quote is in that source's local copy, the two
systems sit in separate contexts (ADR-0004 A8), and every Dirac-3 assertion
present before the task is classed against the Dirac-3S guide."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _text  # noqa: E402

pytestmark = pytest.mark.live_store

CLASSES = {"confirmed", "confirmed in part", "changed", "superseded", "not addressed"}


def _script():
    spec = importlib.util.spec_from_file_location("f65", ROOT / "scripts" / "sprint8_f65_dirac3s_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_quote_is_in_a_yielding_source(live_conn):
    """Proven to fail by injection, 2026-10-12: with one digit of the
    9,980-variable row changed in the stored citation_context of a copy,
    this test named dirac3s-variable-ceiling-by-configuration."""
    f65 = _script()
    checked = 0
    for assertion, yielded_by in f65.ASSERTIONS:
        row = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                (assertion.id,)).fetchone()
        assert row, f"{assertion.id}: not in the store"
        quotes = _QUOTE.findall(row[0])
        assert quotes, f"{assertion.id}: no quote found"
        texts = [_text(f65.LOCAL[r]) for r in yielded_by]
        for q in quotes:
            assert any(q in t for t in texts), f"{assertion.id}: not verbatim in its sources: {q[:70]}"
            checked += 1
    assert checked >= 30


def test_the_two_systems_are_separate_contexts(live_conn):
    f65 = _script()
    for assertion, _ in f65.ASSERTIONS:
        got = {r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                               (assertion.id,))}
        assert got == {assertion.context}, assertion.id
        if assertion.id.startswith("dirac3s-"):
            assert assertion.context == "platform:dirac-3s", assertion.id
    assert live_conn.execute("SELECT 1 FROM contexts WHERE id = 'platform:dirac-3s'").fetchone()


def test_every_prior_dirac3_assertion_is_classed(live_conn):
    """Proven to fail by injection, 2026-10-12: with one entry removed from
    CLASSED, this test named the Dirac-3 assertion left unclassed."""
    f65 = _script()
    new = {a.id for a, _ in f65.ASSERTIONS}
    live = {r[0] for r in live_conn.execute(
        "SELECT r.id FROM records r JOIN record_contexts c ON c.record_id = r.id "
        "WHERE r.class = 'assertion' AND c.context_id = 'platform:dirac-3'")} - new
    assert set(f65.CLASSED) == live, (
        f"unclassed: {live - set(f65.CLASSED)}; gone: {set(f65.CLASSED) - live}. A new Dirac-3 assertion is classed "
        "against the Dirac-3S guide when it is entered")
    for rid, (cls, by) in f65.CLASSED.items():
        assert cls in CLASSES, rid
        assert by or cls != "confirmed", f"{rid}: confirmed with no Dirac-3S assertion behind it"
        if by:
            assert by in new, f"{rid}: classed by an unknown assertion {by}"


def test_supports_links_only_where_the_whole_claim_is_confirmed(live_conn):
    """ADR-0004 A8 (b): a `supports` link from a Dirac-3S assertion goes only
    to a Dirac-3 assertion classed `confirmed`, and every `confirmed` pair
    has its link. Proven to fail by injection, 2026-10-12: with the FPGA
    pair's link deleted from a copy of the store, this test named it."""
    f65 = _script()
    confirmed_by = {by: rid for rid, (cls, by) in f65.CLASSED.items() if cls == "confirmed"}
    for assertion, _ in f65.ASSERTIONS:
        if not assertion.id.startswith("dirac3s-"):
            continue
        stored = {r[0] for r in live_conn.execute(
            "SELECT to_assertion_id FROM assertion_relations WHERE from_assertion_id = ? AND relation = 'supports'",
            (assertion.id,))}
        assert stored == set(assertion.supports), assertion.id
        for target in stored:
            assert confirmed_by.get(assertion.id) == target, f"{assertion.id} -> {target} is not a confirmed pair"
    for by, rid in confirmed_by.items():
        assert live_conn.execute("SELECT 1 FROM assertion_relations WHERE from_assertion_id = ? AND "
                                 "to_assertion_id = ? AND relation = 'supports'", (by, rid)).fetchone(), \
            f"{rid} is classed confirmed by {by}, but no supports link records it"


def test_the_guide_is_read_in_full_with_its_hash(live_conn):
    f65 = _script()
    tier, evidence = live_conn.execute("SELECT tier, evidence FROM paper_fields WHERE record_id = ?",
                                       (f65.D3S,)).fetchone()
    assert tier == "read" and f65.D3S_SHA256 in evidence
    assert live_conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND extent = 'full' AND read_on = ?",
                             (f65.D3S, f65.TODAY)).fetchone()
    assert f65.sha256_of(f65.D3S_FILE) == f65.D3S_SHA256


def test_an_admission_upgrade_needs_the_team_leads_decision(live_conn):
    """Plan risk table: the admission-against-interest upgrades are Class 2,
    decided by the team lead at Manual Validation, never by the task. An
    upgraded candidate must name that decision in its reasons."""
    f65 = _script()
    assert f65.UPGRADES_APPROVED <= set(f65.CANDIDATE_UPGRADES)
    for rid in f65.CANDIDATE_UPGRADES:
        certainty, reasons = live_conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?",
                                               (rid,)).fetchone()
        assert (certainty == "high") == (rid in f65.UPGRADES_APPROVED), f"{rid}: {certainty} in the store"
        if certainty != "moderate" or re.search(r"UPGRADED", reasons):
            assert "team lead" in reasons and "Manual Validation" in reasons, \
                f"{rid}: upgraded without the team lead's recorded decision"


def test_an_approved_upgrade_is_applied_and_a_later_apply_keeps_it(live_copy):
    """The sync in apply_changes compares certainty as well as the text, so
    an approved upgrade reaches the store and a re-run neither repeats nor
    reverts it. Proven to fail by injection, 2026-10-13: with the sync's
    UPDATE no longer setting certainty (as it stood at Task C), the
    approved record stayed moderate."""
    from store import connect
    f65 = _script()
    rid = "dirac3s-not-an-exact-solver"
    entered = next(a for a, _ in f65.ASSERTIONS if a.id == rid)
    conn = connect(live_copy)
    try:
        assert f"exists {rid}" in f65.apply_changes(conn), "the store differs from the script"
        # Back to the state before Q7 was answered, then apply again.
        conn.execute("UPDATE records SET certainty = ?, certainty_reasons = ? WHERE id = ?",
                     (entered.certainty, entered.certainty_reasons, rid))
        assert f"upgrade {rid} [high]" in f65.apply_changes(conn)
        certainty, reasons = conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?",
                                          (rid,)).fetchone()
        assert certainty == "high" and "team lead" in reasons and "Manual Validation" in reasons
        assert f"exists {rid}" in f65.apply_changes(conn)
    finally:
        conn.close()
