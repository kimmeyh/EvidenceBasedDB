"""Sprint 13 Task E (F108): Phase 2's later Sprint 28 work at 9cbe5ba
(INTAKE_WORKFLOW.md section 50). The documents are read from the sibling
repository at a named commit, which CI does not have, so the source tests
are live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f108", ROOT / "scripts" / "sprint13_f108_phase2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_correction_changes_only_what_phase2_changed():
    """Each corrected value differs from F102's, and keeps its id, context,
    certainty and source. Proven to fail by injection, 2026-10-25: with
    the F111 range left at "0.829" in the corrected value, the F111 entry
    was named."""
    f108 = _script()
    old = {a.id: a for _, a in f108.f102.ASSERTIONS}
    assert len(f108.CORRECTED) == 3
    for _, a in f108.CORRECTED:
        o = old[a.id]
        assert a.value != o.value and a.citation_context != o.citation_context, a.id
        assert (a.context, a.certainty, a.provenance) == (o.context, o.certainty, o.provenance), a.id
        assert "9cbe5ba" in a.certainty_reasons and "10086da" not in a.certainty_reasons, a.id
    v = {a.id: a.value for _, a in f108.CORRECTED}
    assert "timer's resolution)" not in v["f110-proxy-solve-flat-paper-2s-not-like-for-like"]
    assert "4% to 14%" in v["f114-calibrated-plugin-misses-known-ceiling"]
    assert "0.829" not in v["f111-cvqboost-knn-lane-below-published-value-under-loke-protocol"]


def test_f162_names_what_it_bears_on():
    """The links themselves are checked against the store in the live test."""
    f108 = _script()
    reasons = " ".join(a.certainty_reasons for a in f108.F162)
    for aid in ("dirac3-matches-classical-proxy-in-pocket-spectra-b4",
                "cvqboost-in-segment-edge-negative-on-device-spectra-b4",
                "cvqboost-device-below-classical-bar-spectra-b4",
                "fourier-wall-incomplete-bar-manufactures-advantage"):
        assert aid in reasons, aid
    assert all(a.context == "hsbc-2026" and a.evidence_tag == "SIM" for a in f108.F162)


@pytest.mark.live_store
def test_every_quote_and_figure_is_in_its_document_at_9cbe5ba():
    """Proven to fail by injection, 2026-10-25: with the F111 quote's
    "0.828" put back to "0.829", require_verbatim refused the F111 entry."""
    f108 = _script()
    for key, (_, sha) in f108.BLOBS.items():
        assert hashlib.sha256(f108.source_bytes(key)).hexdigest() == sha, key
    assert len(f108.verify_all()) == 5


@pytest.mark.live_store
def test_the_store_holds_f162_and_a_second_apply_writes_nothing(live_conn, live_copy):
    from store import connect
    f108 = _script()
    for a in f108.F162:
        assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                 (f108.F162_ID, a.id)).fetchone(), a.id
    assert not live_conn.execute("SELECT 1 FROM assertion_relations WHERE from_assertion_id LIKE 'f162-%' OR "
                                 "to_assertion_id LIKE 'f162-%'").fetchone()
    # The fresh-eyes review of 88bd065: each corrected value's paper points at the blob its quotes are read in.
    for key, _ in f108.CORRECTED:
        rid = f108.f102.src_id(key)
        row = live_conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                                (rid,)).fetchone()
        want = f108.repointed(key)
        assert tuple(row) == (want["access"], want["evidence"], want["checked_against_source"]), rid
        assert f108.BLOBS[key][1] in row[1] and "9cbe5ba" in row[0], rid
    conn = connect(live_copy)
    try:
        assert f108.apply_changes(conn) == []
    finally:
        conn.close()
