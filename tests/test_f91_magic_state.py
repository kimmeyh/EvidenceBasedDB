"""F91 (Sprint 11 Task E): the magic state cultivation paper, entered by
its DOI and read in its free preprint. Every quote is in the preprint as
saved, every digit string in a value is in its own quotes, and the
abstracts' difference ("at least") is carried. The preprint lives outside
the repository, so all tests here are live_store (CI has none)."""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import QUOTE, pdf_text, plain  # noqa: E402

pytestmark = pytest.mark.live_store

SHA256 = "642ec2da74acd1b4df2a37985378dbbff69702b8c1314b7ad4e34ea1fcd5c43b"
SRC = "rosenfeld-2026-magic-state-cultivation-superconducting-quantum"


def _script():
    spec = importlib.util.spec_from_file_location("f91", ROOT / "scripts" / "sprint11_f91_magic_state.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_preprint_is_the_one_read():
    f91 = _script()
    assert hashlib.sha256(f91.PDF.read_bytes()).hexdigest() == SHA256


def test_every_quote_is_in_the_preprint():
    """Proven to fail by injection, 2026-10-22: with "a factor of 40"
    changed to "a factor of 50" in the first quote, this test named
    msc-cultivation-cuts-t-state-error-about-40x. Restored."""
    f91 = _script()
    text, bad, checked = pdf_text(str(f91.PDF)), [], 0
    for a in f91.assertions(SRC):
        for q in QUOTE.findall(a.citation_context):
            if plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
        # A quote the pattern cannot parse is never checked (Sprint 11 Task D
        # finding): every pair of quote marks must be a parsed quote.
        assert a.citation_context.count('"') == 2 * len(QUOTE.findall(a.citation_context)), a.id
    assert not bad, bad
    assert checked >= 20


def test_every_number_in_a_value_is_in_its_own_quotes():
    """Digit strings only, hyphenated ones included ("distance-5"); a number
    written as a word ("seven") is not checked. Proven to fail by injection,
    2026-10-22: with 76(3)% changed to 75(3)% in the post-selection value,
    this test named it. Restored."""
    f91 = _script()
    missing = []
    for a in f91.assertions(SRC):
        quoted = " ".join(plain(q) for q in QUOTE.findall(a.citation_context))
        for num in re.findall(r"(?<![\w.,])\d+(?:[.,]\d+)?", plain(a.value)):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", quoted):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_the_abstracts_difference_is_carried():
    """The card: the published abstract says "at least" 0.9999(1); the
    preprint v1 abstract does not. The published wording is pinned by hand
    from Crossref's abstract for the DOI, read 2026-10-22; no test can
    re-read it. Both wordings must be in the value."""
    f91 = _script()
    text = pdf_text(str(f91.PDF))
    assert "a state fidelity of 0.9999(1)" in text and "at least 0.9999(1)" not in text
    v = {a.id: a.value for a in f91.assertions(SRC)}["msc-t-state-fidelity-bound-0-9999"]
    assert "at least 0.9999(1)" in v and "a state fidelity of 0.9999(1)" in v and "lower bound" in v


def test_the_store_holds_every_field_the_script_sets(live_conn):
    """Proven to fail by injection, 2026-10-22: with one character of the
    projection's certainty reasons changed in the script and not applied,
    this test named msc-projection-halving-noise-2e-5. Restored."""
    f91 = _script()
    cols = ("value", "certainty", "certainty_reasons", "provenance", "evidence_tag", "context", "derivation",
            "fidelity", "claim_type", "citation_context")
    bad = []
    for a in f91.assertions(SRC):
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, r.evidence_tag, c.context_id, "
            "f.derivation, r.fidelity, f.claim_type, f.citation_context FROM records r "
            "JOIN assertion_fields f ON f.record_id = r.id JOIN record_contexts c ON c.record_id = r.id "
            "WHERE r.id = ?", (a.id,)).fetchone()
        if not row or tuple(row) != tuple(getattr(a, k) for k in cols):
            bad.append(a.id)
    assert not bad, bad
    tier, access, disposition = live_conn.execute(
        "SELECT tier, access, disposition FROM paper_fields WHERE record_id = ?", (SRC,)).fetchone()
    assert tier == "read" and access.startswith("DOI:10.1126/science.aee7961")
    assert disposition == f91.ENTRY["disposition"]
    probe = live_conn.execute("SELECT value FROM paper_probes WHERE record_id = ? AND field = 'version_of'",
                              (SRC,)).fetchone()
    assert probe and probe[0] == "arXiv:2512.13908"
