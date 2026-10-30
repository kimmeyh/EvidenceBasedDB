"""Sprint 14 Task D (F120): Phase 2's Sprint 29 results at 6242b8a
(INTAKE_WORKFLOW.md section 56). The documents and run files are read from
the sibling repository at a named commit, which CI does not have, so the
source tests are live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f120", ROOT / "scripts" / "sprint14_f120_phase2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_correction_changes_only_the_ratios_phase2_recomputed():
    """Proven to fail by injection, 2026-10-30: with the corrected value's
    "1.119" put back to "1.118", the first assert named it."""
    f120 = _script()
    assert len(f120.CORRECTED) == 1
    a = f120.CORRECTED[0]
    old = next(x for x in f120.f93.ASSERTIONS if x.id == a.id)
    assert "1.053 to 1.119" in a.value and "1.118:" not in a.value
    assert "1.106, 1.116 and 1.119" in a.citation_context
    assert (a.context, a.certainty, a.provenance, a.evidence_tag) == (old.context, old.certainty, old.provenance,
                                                                      old.evidence_tag)
    assert "6242b8a" in a.certainty_reasons and "infers" in a.value


def test_contexts_and_no_links():
    """Section 43's rule: `ml` for a classical method on a public data set or
    a simulator, `hsbc-2026` for the project's own lanes. ADR-0004 A8 (b):
    nothing here confirms or excludes a stored claim whole."""
    f120 = _script()
    ctx = {a.id: a.context for a in f120.F166 + f120.RES}
    assert {i for i, c in ctx.items() if c == "ml"} == {
        "f166-ulb-tuning-chose-unweighted-linear-and-l2-hgb", "f156-henze-penrose-bound-fails-on-f108-simulator",
        "f158-per-type-cascade-below-one-model-on-simulator"}
    assert not [a.id for a in f120.F166 + f120.RES if a.supports or a.contradicts]
    assert all(a.evidence_tag == "SIM" for a in f120.F166 + f120.RES)


def test_each_reason_names_what_it_bears_on():
    f120 = _script()
    reasons = {a.id: a.certainty_reasons for a in f120.F166 + f120.RES}
    for aid, bears in (("f166-ulb-tuned-boosting-leads-proxy-fifth", "f151-cvqboost-proxy-below-stable-hgb-on-ulb"),
                       ("f156-henze-penrose-bound-fails-on-f108-simulator",
                        "f108-no-ceiling-method-recovered-known-ceiling"),
                       ("f160-exp3-room-check-passes-on-ieee-cis",
                        "f153-learner-selection-formulation-fails-its-falsifier"),
                       ("f159-parallel-pool-build-equals-serial-and-is-faster",
                        "f110-cvqboost-pool-build-grows-faster-than-rows")):
        assert bears in reasons[aid], aid


@pytest.mark.live_store
def test_every_quote_and_figure_is_in_its_documents_at_6242b8a():
    """Proven to fail by injection, 2026-10-30: with the F158 quote's
    "-0.126" changed to "-0.127", require_verbatim refused the entry."""
    f120 = _script()
    assert f120.check_hashes() == []
    assert len(f120.verify_all()) == 10


@pytest.mark.live_store
def test_the_headline_figures_match_the_run_files():
    """The validation record was corrected twice on Phase 2's review, so its
    figures are checked against the run files themselves. Proven to fail by
    injection, 2026-10-30: with the F156 check's 2 changed to 3, it failed."""
    f120 = _script()
    run = {k: json.loads(f120.blob(path)) for k, (path, _) in f120.RESULTS.items()}
    s = run["f156"]["summary"]
    assert (s["contains"], s["narrow"], s["n_seeds"], s["passes"]) == (2, 0, 5, False)
    assert run["f156"]["subsample"] == 60000
    p = run["f158"]["summary"]["primary_cascade_minus_single"]
    t = p["t_interval"]
    assert (round(t["mean"], 3), round(t["low"], 3), round(t["high"], 3), p["reading"]) == (-0.069, -0.126, -0.013,
                                                                                           "below")
    assert run["f158"]["summary"]["secondary_shuffled_minus_single"]["reading"] == "below"
    step3 = run["f158"]["step3_ulb_missed_by_all"]
    assert (step3["rows_missed"], step3["rows_missed"] + step3["rows_caught"]) == (106, 950)
    ieee = run["f160"]["ieee"]
    gaps = [next(x["gap_to_floor"] for x in r["sweep"] if x["lam_mult"] == ieee["ridge_choice"]["lam_mult"])
            for r in ieee["rows"]]
    assert len(gaps) == 6 and min(gaps) >= 0.096 and round(max(gaps), 4) == 0.0985
    assert ieee["design_fails"] is False and run["f160"]["control"]["design_fails"] is False
    full = run["f159"]["analysis"]["1.0"]
    assert (round(full["serial_s"], 1), full["speedup"]["16"], round(full["serial_s"] / full["speedup"]["32"], 1)) == (
        730.3, 11.24, 45.8)
    assert run["f159"]["analysis"]["all_equal"] is True


@pytest.mark.live_store
def test_the_store_holds_f120_and_a_second_apply_writes_nothing(live_conn, live_copy):
    from store import connect
    f120 = _script()
    for src, group in ((f120.SET_ID, f120.F166), (f120.RES_ID, f120.RES)):
        for a in group:
            assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                     (src, a.id)).fetchone(), a.id
    a = f120.CORRECTED[0]
    assert live_conn.execute("SELECT value FROM records WHERE id = ?", (a.id,)).fetchone()[0] == a.value
    for key in f120.REREAD:
        rid = f120.REREAD[key][0]
        row = live_conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                                (rid,)).fetchone()
        want = f120.repointed(key)
        assert tuple(row) == (want["access"], want["evidence"], want["checked_against_source"]), rid
        assert f120.REREAD[key][5] in row[1], rid  # the earlier read's blob kept
    conn = connect(live_copy)
    try:
        assert f120.apply_changes(conn) == []
    finally:
        conn.close()
