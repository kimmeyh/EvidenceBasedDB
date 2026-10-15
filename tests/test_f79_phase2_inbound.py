"""F79 (Sprint 9 Task A): the first Phase 2 result entered by the inbound
path. Every quote is in Phase 2's result document as stored at the pinned
commit, read through `git show`, never through Phase 2's working tree, which
an active repository moves; the record names the commit it was read at."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain  # noqa: E402


def _script():
    spec = importlib.util.spec_from_file_location("f79", ROOT / "scripts" / "sprint9_f79_phase2_b4_b5_inbound.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.live_store
def test_every_quote_is_in_the_document_at_the_pinned_commit(live_conn):
    """Proven to fail by injection, 2026-10-15: with COMMIT set to Phase 2's
    b76f2d6 (before the in-pocket table was added in a57bd8f), this test
    named dirac3-matches-classical-proxy-in-pocket-spectra-b4. Restored and
    green again."""
    f79 = _script()
    text = _plain(f79.source_text())
    checked = 0
    for assertion in f79.ASSERTIONS:
        row = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                (assertion.id,)).fetchone()
        assert row, f"{assertion.id}: not in the store"
        quotes = _QUOTE.findall(row[0])
        assert quotes, f"{assertion.id}: no quote found"
        for q in quotes:
            assert q in text, f"{assertion.id}: not verbatim at commit {f79.COMMIT[:7]}: {q[:70]}"
            checked += 1
    assert checked >= 9


@pytest.mark.live_store
def test_the_record_names_the_commit_it_was_read_at(live_conn):
    """The inbound rule (INTAKE_WORKFLOW.md section 19): a Phase 2 result's
    provenance names the repository, the commit and the file."""
    f79 = _script()
    citation, evidence = live_conn.execute(
        "SELECT r.provenance, p.evidence FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?",
        (f79.SRC,)).fetchone()
    for needed in ("hsbc-qfraud-phase2", "139fa13", "docs/B4_B5_HARDWARE_RESULT.md"):
        assert needed in citation, needed
    assert f79.SHA256 in evidence


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f79 = _script()
    conn = connect(live_copy)
    try:
        log = f79.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
