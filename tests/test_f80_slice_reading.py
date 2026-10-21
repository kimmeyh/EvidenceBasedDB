"""F80 (Sprint 9 Task G): the 76-record slice read and entered. Every quote is
verbatim in its source, every figure in a value is in its source, no vendor
claim about its own product is graded HIGH, the eleven refused records stay
`seen` with their reason and yield nothing, and each entered read has a
qualifying coordinator row beside the subagent's."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain, _text  # noqa: E402


def _load(spec):
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _script():
    return _load(importlib.util.spec_from_file_location("f80", ROOT / "scripts" / "sprint9_f80_reading.py"))


def _source_text(f80, paper: dict, a: dict | None = None) -> str:
    """The text an assertion's quotes were taken from, as the quote check compares it."""
    if paper["record_id"] == "qci-package-eqc-models":
        meta = json.loads(f80.EQC_FILES[0].read_text(encoding="utf-8"))
        desc = meta.get("description") or meta.get("info", {}).get("description") or ""
        version = meta.get("version") or meta.get("info", {}).get("version") or ""
        with zipfile.ZipFile(f80.EQC_FILES[1]) as z:
            mods = "\n".join(z.read(n).decode("utf-8", "replace") for n in z.namelist() if n.endswith(".py"))
        return _plain(f"version {version}\n{desc}\n{mods}")
    path = f80.source_file(paper, a)
    if Path(path).suffix.lower() in (".pdf", ".html", ".htm"):
        return _text(path)
    return _plain(Path(path).read_text(encoding="utf-8", errors="replace"))


def _by_id(f80) -> dict[str, tuple[dict, dict]]:
    return {a["id_suggestion"]: (p, a) for _, p in f80.kept_groups() for a in p["assertions"]}


@pytest.mark.live_store
def test_every_quote_is_in_its_source():
    """Reads the script's quotes, not the stored ones, so a quote changed in
    the reads manifest is caught before it is applied.
    Proven to fail by injection, 2026-10-15: with "highly competitive" made
    "very competitive" in a group_q2.json quote, this test named
    blekos-qaoa-general-advantage-open-question."""
    f80 = _script()
    by_id, cache, checked, bad = _by_id(f80), {}, 0, []
    for _, a, rid in f80.assertions():
        paper, raw = by_id[a.id]
        key = (rid, raw.get("quote_file"))
        text = cache.setdefault(key, _source_text(f80, paper, raw))
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 400


@pytest.mark.live_store
def test_every_number_in_a_value_is_in_its_source():
    """A dotted version (5.0.0) is one number. pdftotext splits a thousands
    group after its comma ("284, 807"), so that space is closed first.
    Proven to fail by injection, 2026-10-15: with the VALUE_EDITS entry that
    restates the portfolio dates in the page's words deleted, this test named
    dirac3-portfolio-255-monthly-problems-21y (01, 01, 03)."""
    f80 = _script()
    by_id, cache, missing = _by_id(f80), {}, []
    for _, a, rid in f80.assertions():
        if a.claim_type == "absence":
            continue
        paper, raw = by_id[a.id]
        text = cache.setdefault((rid, raw.get("quote_file")), re.sub(
            r"(\d), (\d{3})(?!\d)", r"\1,\2", _source_text(f80, paper, raw)))
        for num in re.findall(r"(?<!\d)\.?\d+(?:[.,]\d+)*", a.value):
            lead = "" if num.startswith(".") else r"(?<![\d.])"
            if not re.search(rf"{lead}{re.escape(num)}(?!\d)", text):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_no_vendor_claim_about_its_own_product_is_high():
    """Proven to fail by injection, 2026-10-15: with certainty() returning
    "high" for a vendor's description of its product, this test named
    eqc-models-dirac3-cloud-solvers."""
    f80 = _script()
    vendor = [a for _, a, _ in f80.assertions() if a.claim_type == "vendor-self-claim"]
    assert vendor
    assert all(a.certainty in ("moderate", "low") for a in vendor), [a.id for a in vendor if a.certainty == "high"]


def test_vendor_descriptions_stay_moderate_and_vendor_results_are_low():
    """Review of 9f71f19: five descriptions carried a result's downgrade.
    Proven to fail by injection, 2026-10-15: with certainty() no longer
    consulting VENDOR_DESCRIPTIONS, this test named the descriptions."""
    f80 = _script()
    vendor = {a.id: a.certainty for _, a, _ in f80.assertions()
              if a.claim_type == "vendor-self-claim" and a.id not in f80.CERTAINTY_OVERRIDES}
    moderate = f80.VENDOR_DESCRIPTIONS | f80.UPGRADES_APPROVED
    wrong = [i for i, c in vendor.items() if c != ("moderate" if i in moderate else "low")]
    assert not wrong, wrong
    assert f80.VENDOR_DESCRIPTIONS <= set(vendor)


def test_approved_upgrades_rise_one_level_and_say_what_they_cost():
    """Sprint 9 Manual Validation Q3 = 1: the three admission-against-interest
    candidates go low -> moderate, each reason naming its cost and the
    decision. Proven to fail by injection, 2026-10-15: with UPGRADES_APPROVED
    emptied, the first assertion failed, listing the three candidate ids."""
    f80 = _script()
    got = {a.id: a for _, a, _ in f80.assertions() if a.id in f80.CANDIDATE_UPGRADES}
    assert set(got) == set(f80.CANDIDATE_UPGRADES) == f80.UPGRADES_APPROVED
    wrong = [i for i, a in got.items()
             if a.certainty != "moderate" or "costly to disclose" not in a.certainty_reasons
             or "Sprint 9 Manual Validation (Q3)" not in a.certainty_reasons]
    assert not wrong, wrong


@pytest.mark.live_store
def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    """Review of 9f71f19: a changed quote or context was never synced, and
    the quote test read the manifest, so the two could diverge.
    Proven to fail by injection, 2026-10-15: with one VALUE_EDITS
    replacement changed and not applied, this test named the assertion."""
    f80 = _script()
    bad = []
    for _, a, _ in f80.assertions():
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                               (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad
    for aid in f80.DROPPED:
        assert not live_conn.execute("SELECT 1 FROM records WHERE id = ?", (aid,)).fetchone(), aid
    for rid, coi in f80.COI.items():
        assert live_conn.execute("SELECT coi FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] == coi


def test_refused_records_yield_nothing_and_each_has_a_reason():
    """Proven to fail by injection, 2026-10-15: with kept_groups() no longer
    filtering REFUSE, this test named the refused records that then yielded."""
    f80 = _script()
    refused = {p["record_id"] for _, p in f80.load_groups()} & set(f80.REFUSE)
    assert refused == set(f80.REFUSE), set(f80.REFUSE) - refused
    assert all(r.strip() for r in f80.REFUSE.values())
    assert not {rid for _, _, rid in f80.assertions()} & refused


@pytest.mark.live_store
def test_refused_records_stay_seen_with_the_reason(live_conn):
    """Proven to fail by injection, 2026-10-15: with a read record
    (cao-2018-quantum-chemistry-age-quantum-computing) added to REFUSE, this
    test named it. From 2026-10-18 the nine Dirac-1 records are Sprint 10
    Task F's (F84, ADR-0004 A10): read and entered under platform:dirac-1,
    and checked by tests/test_f84_dirac1.py."""
    f80 = _script()
    f84 = importlib.util.spec_from_file_location("f84", ROOT / "scripts" / "sprint10_f84_dirac1.py")
    taken = set(_load(f84).NINE)
    for rid in set(f80.REFUSE) - taken:
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        reason, = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
        assert tier == "seen", rid
        assert "NOT entered" in reason, rid


@pytest.mark.live_store
def test_each_read_is_qualified_and_every_context_exists(live_conn):
    """Proven to fail by injection, 2026-10-15: with SUBAGENT_READER renamed,
    this test named resonance-alliance-2026-phase-1-submission-guidelines."""
    f80 = _script()
    contexts = {r[0] for r in live_conn.execute("SELECT id FROM contexts")}
    for _, p in f80.kept_groups():
        rid = p["record_id"]
        rows = {(r[0], r[1]) for r in live_conn.execute(
            "SELECT reader, extent FROM paper_reads WHERE record_id = ?", (rid,))}
        assert (f80.SUBAGENT_READER, "subagent") in rows, rid
        assert ("Claude", "partial") in rows, rid
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        assert tier == "read", rid
    assert {a.context for _, a, _ in f80.assertions()} <= contexts


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    """Proven to fail by injection, 2026-10-15: with one VALUE_EDITS
    replacement changed, the second apply logged
    'update wan-qnn-learns-teleportation-in-simulation'."""
    from store import connect
    f80 = _script()
    conn = connect(live_copy)
    try:
        log = f80.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
