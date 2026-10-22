"""F92 (Sprint 11 Task C): QCi's answers of 2026-10-20 and 2026-10-21,
entered as vendor statements. Every quote is in its email as filed in
Phase 2's `docs/qci_package/` (read only), every number in a value is in
that assertion's own quotes, the files are the ones read, and the only
relation is the one ADR-0004 A8 (b) allows. All tests here read the local
Phase 2 folder, so all are live_store (CI has none)."""
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
    spec = importlib.util.spec_from_file_location("f92", ROOT / "scripts" / "sprint11_f92_qci_answers.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_emails_are_the_ones_read():
    f92 = _script()
    for src, (name, sha) in f92.FILES.items():
        assert hashlib.sha256(f92.source_bytes(src)).hexdigest() == sha, name


def test_every_quote_is_in_its_own_email():
    """Proven to fail by injection, 2026-10-22: with the 954-levels quote
    changed to "955 levels", this test named
    qci-email-dirac3s-integer-solver-954-levels and
    qci-email-dirac3-integer-solver-954-levels. Restored."""
    f92 = _script()
    texts = {src: _plain(f92.source_text(src)) for src in f92.FILES}
    bad, checked = [], 0
    for src, a in f92.ASSERTIONS:
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in texts[src]:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 25


def test_every_number_in_a_value_is_in_its_own_quotes():
    """Stricter than the whole email: a figure must be in the quotes the
    assertion carries. A number inside a record id ("bounded-0-to-16")
    follows a letter and a hyphen and is skipped, as is the 2 of the
    project name "Phase 2". Proven to fail by
    injection, 2026-10-22: with "9980" in the 9980 value changed to "9,980",
    this test named qci-email-dirac3s-integer-levels-9980-planned. Restored."""
    f92 = _script()
    missing = []
    for _, a in f92.ASSERTIONS:
        quoted = " ".join(_plain(q) for q in _QUOTE.findall(a.citation_context))
        for num in re.findall(r"(?<![\w.,])(?<![A-Za-z]-)(?<!Phase )\d+(?:[.,]\d+)?", a.value):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", quoted):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_no_relation_and_the_withdrawn_link_is_gone(live_conn):
    """ADR-0004 A8 (b): no answer confirms a stored claim whole and none
    makes one impossible, so every bearing is named in the value, not
    linked. The first apply's supports link (resolution answer to
    dirac3s-analog-resolution-about-200-to-1) failed that test at the
    fresh-eyes review, 2026-10-22, and is withdrawn. Proven to fail by
    injection, 2026-10-22: before the withdrawal ran, the store half of
    this test named the link."""
    f92 = _script()
    assert not [a.id for _, a in f92.ASSERTIONS if a.supports or a.contradicts]
    rows = live_conn.execute("SELECT from_assertion_id, to_assertion_id FROM assertion_relations "
                             "WHERE from_assertion_id LIKE 'qci-email-%' OR to_assertion_id LIKE 'qci-email-%'"
                             ).fetchall()
    assert not rows, rows


def test_hedges_and_plans_are_low_and_the_unit_gap_is_kept():
    """The card: A4's "I assume" kept; 9980 a stated plan, not a capability;
    954's unit not stated. Proven to fail by injection, 2026-10-22: with the
    hedged 16-levels answer set to moderate, this test named it. Restored."""
    f92 = _script()
    a = {x.id: x for _, x in f92.ASSERTIONS}
    for low in ("qci-email-dirac3s-integer-limit-16-levels-hedged", "qci-email-dirac3s-integer-levels-9980-planned",
                "qci-email-dirac3s-raw-values-not-yet-on-cloud", "qci-email-dirac3s-to-replace-dirac3-names-distinct"):
        assert a[low].certainty == "low", low
    for lev in ("qci-email-dirac3s-integer-solver-954-levels", "qci-email-dirac3-integer-solver-954-levels"):
        assert "not stated" in a[lev].value and "not stated" in a[lev].units, lev
    assert "plan" in a["qci-email-dirac3s-integer-levels-9980-planned"].value


def test_values_name_roles_not_people():
    f92 = _script()
    names = ("Charlotte", "Brown", "Wes", "Dyk")
    bad = [a.id for _, a in f92.ASSERTIONS if any(n in a.value for n in names)]
    assert not bad, bad


def test_no_stored_assertion_is_rewritten():
    """The card: a newer statement is related to stored claims, never
    written over them. Every id this script writes is its own."""
    f92 = _script()
    ids = [a.id for _, a in f92.ASSERTIONS]
    assert all(i.startswith("qci-email-") for i in ids), ids
    assert len(ids) == len(set(ids))


def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    f92 = _script()
    bad = []
    for _, a in f92.ASSERTIONS:
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, r.evidence_tag, f.citation_context "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.evidence_tag,
                                     a.citation_context) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad
    for entry in f92.SOURCES:
        evidence = live_conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?",
                                     (entry["id"],)).fetchone()[0]
        assert f92.FILES[entry["id"]][1] in evidence, entry["id"]
