"""F93 (Sprint 11 Task D): Phase 2's F108 ceiling validation, entered by
the inbound path. Every quote and every figure is in the document as
committed at the pinned commit, read through `git show`, never through
Phase 2's working tree. Markdown bold (`**`) is dropped before the
comparison, as each quote that crosses it says. All tests here read the
local Phase 2 repository, so all are live_store (CI has none)."""
from __future__ import annotations

import hashlib
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
    spec = importlib.util.spec_from_file_location("f93", ROOT / "scripts" / "sprint11_f93_f108_ceiling.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_document_is_the_one_read():
    f93 = _script()
    assert hashlib.sha256(f93.source_bytes()).hexdigest() == f93.SHA256


def test_every_quote_is_in_the_document_at_the_pinned_commit():
    """Proven to fail by injection, 2026-10-22: with COMMIT set to Phase 2's
    288eb2c (the document's first version, before Phase 2's fresh-eyes
    review), this test named f108-no-ceiling-method-recovered-known-ceiling
    and f108-hgb-plugin-overstates-bayes-error-5-to-12-percent, among
    others. Restored."""
    f93 = _script()
    text, bad, checked = _plain(f93.source_text().replace("**", "")), [], 0
    for a in f93.ASSERTIONS:
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 20


def test_every_number_in_a_value_is_in_its_own_quotes():
    """A number inside a record id follows a letter and a hyphen and is
    skipped, as is the 2 of "Phase 2". Proven to fail by injection,
    2026-10-22: with "0.87 on seed 43" changed to "0.9 on seed 43" in the
    AUPRC-floor value (the Reading section's rounded figure, not in that
    assertion's quotes), this test named it. Restored."""
    f93 = _script()
    missing = []
    for a in f93.ASSERTIONS:
        quoted = " ".join(_plain(q) for q in _QUOTE.findall(a.citation_context))
        for num in re.findall(r"(?<![\w.,])(?<![A-Za-z]-)(?<!Phase )\d+(?:[.,]\d+)?", a.value):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", quoted):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_phase_2s_own_limits_are_carried():
    """Phase 2 says the pass rule was read after the run, the plug-in's gap
    is inferred to be the model's, and the HGB cause and its transfer to
    real data are unverified; a value that dropped any of them would claim
    more than the source. Proven to fail by injection, 2026-10-22: with
    "read after the run" cut from the verdict, this test named it.
    Restored."""
    f93 = _script()
    v = {a.id: a.value for a in f93.ASSERTIONS}
    assert "read after the run" in v["f108-no-ceiling-method-recovered-known-ceiling"]
    assert "One simulator, five seeds" in v["f108-no-ceiling-method-recovered-known-ceiling"]
    assert "infers" in v["f108-hgb-plugin-overstates-bayes-error-5-to-12-percent"]
    assert "not verified" in v["f108-default-hgb-misses-rare-sharp-threshold"]
    assert "unverified" in v["f108-default-hgb-misses-rare-sharp-threshold"]
    assert {a.certainty for a in f93.ASSERTIONS if a.id == "f108-no-ceiling-method-recovered-known-ceiling"} == {
        "moderate"}


def test_no_relation_is_linked():
    """ADR-0004 A8 (b): the learning-curve result confirms only the
    per-model half of ding-floor-c-is-model-and-config-specific, so the
    value names it instead of a link."""
    f93 = _script()
    assert not [a.id for a in f93.ASSERTIONS if a.supports or a.contradicts]


def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    """Sprint 14 (F120) corrected one value at Phase 2 commit 6242b8a; the
    store holds that script's text for it, and this one's for the rest."""
    f93 = _script()
    spec = importlib.util.spec_from_file_location("f120", ROOT / "scripts" / "sprint14_f120_phase2.py")
    f120 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f120)
    current = {a.id: a for a in f93.ASSERTIONS} | {a.id: a for a in f120.CORRECTED}
    bad = []
    for a in current.values():
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, r.evidence_tag, f.citation_context "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.evidence_tag,
                                     a.citation_context) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad
    citation, evidence = live_conn.execute(
        "SELECT r.provenance, p.evidence FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?",
        (f93.SRC,)).fetchone()
    for needed in ("hsbc-qfraud-phase2", "eef3349", "docs/phase2/F108_CEILING_VALIDATION.md", "Sprint 27 Task K"):
        assert needed in citation, needed
    assert f93.SHA256 in evidence
