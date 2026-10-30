"""Sprint 14 Task A (F119): Brighindi's PHI-OMEGA paper, posts, images and
code (INTAKE_WORKFLOW.md section 54). The sources are local files outside
the repository, which CI does not have, so the source and store tests are
live_store."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f119", ROOT / "scripts" / "sprint14_f119_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_only_definitions_setup_absence_and_stated_limits_are_graded_up():
    """The paper's claims stay the author's; HIGH only on a basis the source
    itself settles. Proven to fail by injection, 2026-10-30: with the
    central claim added to HIGH as a "proved result", this test named it."""
    f119 = _script()
    graded_up = {a.id for _, a in f119.ASSERTIONS if a.certainty == "high"}
    assert graded_up == set(f119.HIGH) == {
        "phi-omega-paper-defines-three-axioms-and-a-fail-closed-gate",
        "phi-omega-paper-stress-test-setup",
        "phi-omega-paper-gives-no-proof-for-its-closure-claim",
        "phi-infinity-stress-test-not-reproducible-and-no-immunity-inferred",
        "m-omnia-validation-claims-no-empirically-verified-result",
        "phi-infinity-runtime-calls-the-closure-a-hypothesis-and-the-test-no-general-proof",
    }
    by_id = {a.id: a for _, a in f119.ASSERTIONS}
    for aid in ("phi-omega-paper-control-corrupts-at-cycle-16", "phi-infinity-stress-test-counts-20-commits-80-rejections"):
        assert by_id[aid].evidence_tag == "SIM", aid
    assert by_id["phi-omega-paper-gives-no-proof-for-its-closure-claim"].claim_type == "absence"
    assert by_id["phi-omega-paper-gives-no-proof-for-its-closure-claim"].search_scope
    assert all(a.context == "ml" for _, a in f119.ASSERTIONS)


@pytest.mark.live_store
def test_every_quote_and_figure_is_in_its_source():
    """Every quote is checked against each file its assertion quotes,
    including the repository's words in a paper-yielded value (SPLIT).
    Proven to fail by injection, 2026-10-30: with the stress test's
    "Passo 16" quoted as "Passo 17", require_verbatim refused the entry;
    and with "sono metriche diverse" checked against the paper alone, it
    refused the Figure 1 assertion."""
    f119 = _script()
    assert len(f119.verify_all()) == 12


@pytest.mark.live_store
def test_the_store_holds_f119_and_a_second_apply_writes_nothing(live_conn, live_copy):
    """Proven to fail by injection, 2026-10-30: with the status-note
    assertion's id changed in the script, its yield was missing."""
    from store import connect
    f119 = _script()
    for key, a in f119.ASSERTIONS:
        assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                 (f119.TEXTS[key][1], a.id)).fetchone(), a.id
    links = live_conn.execute("SELECT from_assertion_id, to_assertion_id, relation FROM assertion_relations "
                              "WHERE from_assertion_id IN (%s)" % ",".join("?" * len(f119.ASSERTIONS)),
                              [a.id for _, a in f119.ASSERTIONS]).fetchall()
    central = "phi-omega-paper-claims-closure-makes-structural-failure-impossible"
    stress = "phi-infinity-stress-test-not-reproducible-and-no-immunity-inferred"
    assert {tuple(r) for r in links} == {
        (stress, "phi-omega-paper-claims-full-reproducibility", "contradicts"),
        (stress, central, "contradicts"),
    }
    for rid, (_, detail) in f119.READ_CORRECTIONS.items():
        rows = live_conn.execute("SELECT detail FROM paper_reads WHERE record_id = ?", (rid,)).fetchall()
        assert [r[0] for r in rows] == [f119.read_detail(rid, detail)], rid
        assert detail in live_conn.execute("SELECT checked_against_source FROM paper_fields WHERE record_id = ?",
                                           (rid,)).fetchone()[0], rid
    for rid in f119.ENTRIES:
        assert tuple(live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()) \
            == ("read",), rid
    conn = connect(live_copy)
    try:
        assert f119.apply_changes(conn, True) == []
    finally:
        conn.close()


@pytest.mark.live_store
def test_the_first_read_rows_and_the_withdrawn_link_are_corrected(live_copy):
    """The first apply's read rows and the withdrawn link, put back on a copy
    of the store, are corrected by the apply, once. Proven to fail by
    injection, 2026-10-30: with the correct_reads call removed from
    apply_changes, the first rows stayed; with withdraw_links removed, the
    link stayed."""
    from store import connect
    f119 = _script()
    conn = connect(live_copy)
    try:
        for rid, (first, detail) in f119.READ_CORRECTIONS.items():
            conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND detail = ?",
                         (first, rid, f119.read_detail(rid, detail)))
        from_id, to_id, relation, _ = f119.WITHDRAWN[0]
        conn.execute("INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES (?, ?, ?)",
                     (from_id, to_id, relation))
        assert len(f119.apply_changes(conn, True)) == 3
        for rid, (first, detail) in f119.READ_CORRECTIONS.items():
            rows = [r[0] for r in conn.execute("SELECT detail FROM paper_reads WHERE record_id = ?", (rid,))]
            assert rows == [f119.read_detail(rid, detail)], rid
        assert not conn.execute("SELECT 1 FROM assertion_relations WHERE from_assertion_id = ? AND to_assertion_id = ?",
                                (from_id, to_id)).fetchone()
        assert f119.apply_changes(conn, True) == []
    finally:
        conn.close()
