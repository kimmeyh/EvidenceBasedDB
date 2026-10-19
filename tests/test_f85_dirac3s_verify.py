"""F85 (Sprint 10 Task G): Phase 2's Dirac-3S verification, entered by the
inbound path. Every quote and every figure is in the document as committed
at the pinned commit, read through `git show`, never through Phase 2's
working tree. Markdown bold (`**`) is dropped from the document before the
comparison, as each quote that crosses it says. All tests here read the
local Phase 2 repository, so all are live_store (CI has none)."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain  # noqa: E402

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f85", ROOT / "scripts" / "sprint10_f85_dirac3s_verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _source(f85) -> str:
    return _plain(f85.source_text().replace("**", ""))


def test_the_document_is_the_one_read():
    import hashlib
    f85 = _script()
    assert hashlib.sha256(f85.source_bytes()).hexdigest() == f85.SHA256


def test_every_quote_is_in_the_document_at_the_pinned_commit():
    """Proven to fail by injection, 2026-10-18: with COMMIT set to Phase 2's
    3aa52f6 (the document's first version), this test named
    dirac3s-returned-b4-reference-optimum-two-seeds and
    dirac3s-returned-weights-finer-than-0005-step. (At c141a57, the card's
    commit, every quote is already present, so that commit cannot prove it.)
    Restored."""
    f85 = _script()
    text, bad, checked = _source(f85), [], 0
    for a in f85.ASSERTIONS:
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 14


def test_every_number_in_a_value_is_in_the_document():
    """Proven to fail by injection, 2026-10-18: with the guide's 0.420 s
    and 50 variables put back in the time-per-sample value (figures from
    another record, not this document), this test named it."""
    f85 = _script()
    text, missing = _source(f85), []
    for a in f85.ASSERTIONS:
        # A number inside a record id ("about-200-to-1", "dirac-3s") follows
        # a letter and a hyphen and is skipped; a range ("0.974-0.976") is not.
        for num in re.findall(r"(?<![\w.])(?<![A-Za-z]-)\d+(?:\.\d+)?", a.value):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", text):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_the_record_names_repository_commit_file_and_run(live_conn):
    """The inbound rule (INTAKE_WORKFLOW.md section 19)."""
    f85 = _script()
    citation, evidence = live_conn.execute(
        "SELECT r.provenance, p.evidence FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?",
        (f85.SRC,)).fetchone()
    for needed in ("hsbc-qfraud-phase2", "e126dbd", "docs/phase2/F142_DIRAC3S_VERIFY.md", "Sprint 26 Task D"):
        assert needed in citation, needed
    assert f85.SHA256 in evidence and "Sprint 26 Task D (F142)" in evidence
    for a in f85.ASSERTIONS:
        assert "Sprint 26 Task D (F142)" in a.provenance, a.id


def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    f85 = _script()
    bad = []
    for a in f85.ASSERTIONS:
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, r.evidence_tag, f.citation_context "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.evidence_tag,
                                     a.citation_context) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


def test_phase_2s_own_limits_are_carried():
    """Phase 2 says the twin is descriptive, not a test, and the cause of the
    fine weights unverified; a value that dropped either would claim more
    than the source. Proven to fail by injection, 2026-10-18: with
    "descriptive, not a test" cut from the first value, this test named it."""
    f85 = _script()
    v = {a.id: a.value for a in f85.ASSERTIONS}
    assert "descriptive, not a test" in v["dirac3s-returned-b4-reference-optimum-two-seeds"]
    assert "unverified" in v["dirac3s-returned-weights-finer-than-0005-step"]
    assert "not a rate for other schedules" in v["dirac3s-time-per-sample-schedule-2-by-size"]


def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f85 = _script()
    conn = connect(live_copy)
    try:
        log = f85.apply_changes(conn)
    finally:
        conn.close()
    assert all(line.startswith("exists") for line in log), log
