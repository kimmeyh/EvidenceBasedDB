"""Sprint 15 Task M (F130): Phase 2's Sprint 30 results, and F166 repointed,
at PR #74 (INTAKE_WORKFLOW.md section 66). The documents and run files are
read from the sibling repository at a named commit, which CI does not have,
so the source tests are live_store."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f130", ROOT / "scripts" / "sprint15_f130_phase2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _all(f130):
    return [a for items in f130.ASSERTIONS.values() for a in items]


def test_contexts_tags_and_no_links():
    """Section 43's rule: `ml` for a classical method on a simulator (F169),
    `hsbc-2026` for the project's own lanes and Experiment 3. ADR-0004 A8
    (b): no stored claim states the same fact whole, so nothing is linked."""
    f130 = _script()
    assert {a.id for a in _all(f130) if a.context == "ml"} == {"f169-lightgbm-bins-plugin-passes-f108-rule"}
    assert {a.context for a in _all(f130)} == {"ml", "hsbc-2026"}
    assert not [a.id for a in _all(f130) if a.supports or a.contradicts]
    assert all(a.evidence_tag == "SIM" for a in _all(f130))
    assert len(_all(f130)) == 9 and set(f130.ASSERTIONS) == set(f130.RECORDS)


def test_each_reason_names_what_it_bears_on():
    f130 = _script()
    reasons = {a.id: a.certainty_reasons for a in _all(f130)}
    for aid, bears in (("f174-ieee-lightgbm-leads-four-pairs-reliable", "f152-ieee-cis-trees-beat-logistic-lightgbm-leads"),
                       ("f174-ieee-lightgbm-leads-four-pairs-reliable", "han-ieee-cis-best-test-scores-random-split"),
                       ("f174-ieee-cvqboost-proxy-scores-heavily-tied", "f166-ulb-cvqboost-proxy-largest-train-test-gap"),
                       ("f176-below-greedy-on-3-of-6-by-tiny-gains", "f160-exp3-room-check-passes-on-ieee-cis"),
                       ("f169-lightgbm-bins-plugin-passes-f108-rule", "f108-no-ceiling-method-recovered-known-ceiling"),
                       ("f170-ulb-missed-by-all-frauds-sit-among-legitimate-rows",
                        "f154-no-stored-model-better-on-a-ulb-subset"),
                       ("f169-lightgbm-bins-plugin-passes-f108-rule", "f114-calibrated-plugin-misses-known-ceiling"),
                       ("f171-ieee-missed-by-all-share-not-shown-smaller",
                        "f170-ulb-missed-by-all-frauds-sit-among-legitimate-rows")):
        assert bears in reasons[aid], aid


def test_the_f120_apply_keeps_a_later_repoint():
    """F120's apply rewrote F166's evidence to its 6242b8a form whenever it
    differed, which would undo this repoint. Proven to fail by injection,
    2026-11-04: with the "re-read whole on" guard removed from F120's
    apply_changes, the apply on a store holding F130's evidence logged
    "evidence hsbc-qfraud-phase2-f166-sprint29-ulb-algorithms"."""
    f130 = _script()
    f120 = f130.f120
    assert "re-read whole on" in f130.f166_repointed()["evidence"]
    assert "re-read whole on" not in f120.set_entry()["evidence"]
    assert "re-read whole on" not in f120.results_entry()["evidence"]
    src = (ROOT / "scripts" / "sprint14_f120_phase2.py").read_text(encoding="utf-8")
    assert 'and "re-read whole on" not in row[0]' in src


@pytest.mark.live_store
def test_every_quote_and_figure_is_in_its_documents_at_the_commit(live_conn):
    """Every new quote with its value, and every stored F166 quote, at
    COMMIT. Proven to fail by injection, 2026-11-04: with F170's "16.2%"
    changed to "16.3%" in its value, require_verbatim refused the entry."""
    f130 = _script()
    assert f130.check_hashes() == []
    checked, confirmed = f130.verify_all(live_conn)
    assert len(checked) == 9 and len(confirmed) == 4


@pytest.mark.live_store
def test_the_headline_figures_match_the_run_files():
    """Proven to fail by injection, 2026-11-04: with F176's expected 3
    instances below greedy changed to 4, it failed."""
    f130 = _script()
    run = {k: json.loads(f130.blob(path)) for k, (path, _) in f130.RESULTS.items()}
    a = run["f174"]["analysis"]
    assert a["order_by_mean_test_auprc"] == ["lightgbm", "hgb", "catboost", "xgboost", "proxy", "svm", "logreg"]
    per = a["per_algorithm"]
    assert {k: round(v["auprc"]["mean"], 4) for k, v in per.items()} == {
        "lightgbm": 0.5785, "hgb": 0.5211, "catboost": 0.5114, "xgboost": 0.4960, "proxy": 0.4862, "svm": 0.3612,
        "logreg": 0.3564}
    gaps = {k: round(v["train_test_auprc_gap"]["mean"], 4) for k, v in per.items()}
    # every gap the value maps to an algorithm, since the quote check reads the eight documents joined (fresh-eyes
    # review: two swapped gap quotes would still be verbatim)
    assert gaps == {"proxy": 0.3771, "lightgbm": 0.2947, "xgboost": 0.3169, "hgb": 0.1861, "catboost": 0.1846,
                    "logreg": 0.0465, "svm": 0.0363}
    assert max(gaps, key=gaps.get) == "proxy"
    assert [p["reading"] for p in a["adjacent_pairs"]] == ["above", "no reliable difference", "above",
                                                           "no reliable difference", "above", "above"]
    below = [r for r in run["f176"]["rows"]
             if min(m["objective"] for m in r["methods"].values()) < r["methods"]["greedy"]["objective"] - 1e-6]
    assert sorted(f"{r['seed']}/{r['instance']}" for r in below) == ["42/free", "42/mid", "43/free"]
    assert (len(run["f176"]["check"]["cases"]), len(run["f176"]["check"]["fires_on"]),
            len(run["f176"]["check"]["search_missed"])) == (26, 4, 3)
    s = run["f169"]["summary"]
    assert s["passes"] == {"hgb_no_es": True, "lgbm_bins": True} and s["deciding_arm"] == "none"
    u = run["f170"]["ulb"]
    assert u["distinct"] == {"missed": 36, "caught": 370, "mixed": 12}
    p = u["primary"]
    assert (p["missed_median"], p["caught_median"], round(p["caught_share_majority_legit"], 3)) == (1.0, 0.1, 0.162)
    assert p["p"] < 1e-20 and p["rejects"] and run["f170"]["simulator_check"]["rejects"]
    fold = run["f171_budgets"]["ieee"]["per_fold"][0]["recorded_0.5"]
    assert (fold["alerts_per_family"], fold["frauds"], fold["capacity_floor"]) == (427, 2962, 1254)


@pytest.mark.live_store
def test_every_record_named_as_borne_on_exists(live_conn):
    f130 = _script()
    named = {i for a in _all(f130)
             for i in re.findall(r"\b((?:f1\d\d|han)-[a-z0-9-]+[a-z0-9])\b", a.certainty_reasons)}
    named -= {a.id for a in _all(f130)}
    assert len(named) >= 6
    assert [i for i in sorted(named) if not live_conn.execute("SELECT 1 FROM records WHERE id = ?", (i,)).fetchone()] == []


@pytest.mark.live_store
def test_the_store_holds_f130_and_a_second_apply_writes_nothing(live_conn, live_copy):
    """After the apply: each record and assertion, F166 repointed with its
    first read kept, every Phase 2 record F130 wrote passes the local-file
    check, and a second apply (F130's and F120's) writes nothing. The
    stored row is compared as a tuple: the first live run (2026-11-04)
    compared a sqlite3.Row, which never equals a tuple. Proven to fail by
    injection, 2026-11-04: with the expected value given one extra
    character, it named f174-ieee-lightgbm-leads-four-pairs-reliable."""
    from store import connect
    from store.recheck import check_local
    f130 = _script()
    for key, items in f130.ASSERTIONS.items():
        for a in items:
            assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                     (f130.RECORDS[key][0], a.id)).fetchone(), a.id
            # the stored value is the script's, so a correction after the apply cannot sit unwritten
            assert tuple(live_conn.execute("SELECT value, certainty_reasons FROM records WHERE id = ?",
                                           (a.id,)).fetchone()) == (a.value, a.certainty_reasons), a.id
    row = live_conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                            (f130.F166_ID,)).fetchone()
    want = f130.f166_repointed()
    assert tuple(row) == (want["access"], want["evidence"], want["checked_against_source"])
    assert f130.f120.BLOBS["comparison"][1] in row[1]  # the first read's blob kept
    for rid in [f130.RECORDS[k][0] for k in f130.RECORDS] + [f130.F166_ID]:
        access, evidence = live_conn.execute("SELECT access, evidence FROM paper_fields WHERE record_id = ?",
                                             (rid,)).fetchone()
        status, note = check_local(access, evidence)
        assert status == "local copy present (SHA-256 unchanged)", (rid, status, note)
    conn = connect(live_copy)
    try:
        assert f130.apply_changes(conn) == []
        assert f130.f120.apply_changes(conn) == []
    finally:
        conn.close()


@pytest.mark.live_store
def test_a_later_repoint_of_f166_is_kept(live_copy):
    """A rerun moves F166 only from F120's 6242b8a form or its own commit,
    never back from a later repoint (fresh-eyes review). Proven to fail by
    injection, 2026-11-04: with the commit condition removed from the
    repoint, the apply logged "repoint" over the later access."""
    from store import connect
    f130 = _script()
    later = "D:\\later | https://github.com/kimmeyh/hsbc-qfraud-phase2/blob/feedbeef/docs/x.md"
    conn = connect(live_copy)
    try:
        conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (later, f130.F166_ID))
        log = f130.apply_changes(conn)
        assert not [x for x in log if x.startswith("repoint")]
        assert conn.execute("SELECT access FROM paper_fields WHERE record_id = ?",
                            (f130.F166_ID,)).fetchone()[0] == later
    finally:
        conn.rollback()
        conn.close()
