"""Sprint 13 Task F (F112): the first-pass reads entered through
`scripts/sprint13_reading.py`. Every quote is verbatim in its source and
parses as a quote, every figure in a value is in that assertion's own quotes,
HIGH is exactly the coordinator's `high_grades` and carries its named basis
(INTAKE_WORKFLOW.md section 45), never a cited or vendor claim, every LOW
names its reason and a reader's "theoretical" or "field" the coordinator did
not follow is named with why (section 49), every name in the coordinator's
tables is an assertion a reader returned, the reads and the no-copy list
partition the slice, the store holds what the script says, and a second
apply writes nothing. No record read twice is `test_sprint13_read_ledger.py`."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.common_names import with_common_names  # noqa: E402
from store.grading import BASES, theory_words  # noqa: E402
from store.quotes import (QUOTE, plain, source_text, stray_quote_marks, unquoted_figures,  # noqa: E402
                          unsupported_by_basis)

HALVES = ("1", "2")


def _script():
    spec = importlib.util.spec_from_file_location("s13", ROOT / "scripts" / "sprint13_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _raw(s13) -> dict:
    return {a["id_suggestion"]: a for h in HALVES for _, p in s13.load_groups(h) for a in p["assertions"]}


def _all(s13):
    return [a for h in HALVES for _, a, _, _ in s13.assertions(h)]


def test_every_quote_parses_as_a_quote():
    s13 = _script()
    bad = [a.id for a in _all(s13) if stray_quote_marks(a.citation_context)]
    assert not bad, bad


def test_every_figure_in_a_value_is_in_its_own_quotes():
    s13 = _script()
    bad = {a.id: n for a in _all(s13) if (n := unquoted_figures(a.value, a.citation_context))}
    assert not bad, bad


# An exponent the text layer printed flat: "O(N 2)" for N^2, "O(n3)", "10−13" for 10^-13, "ε−1". A
# lower-case letter and digit only inside O(...): the fresh-eyes review of f782e53 found "(H2)" and "(B0)"
# flagged, a molecule and a field. "R2" and "D2-sampling" are left: each is the field's usual flat spelling of
# a name (R squared, D squared sampling), not a figure. A decimal before N or n is a base printed without its
# exponent, "1.46N" for 1.46 to the N (fresh-eyes review of ce2412e); "2D", "97K" and "STO-3G" are names and
# sizes, so the branch stays that narrow.
GARBLED = re.compile(r"O\([^)]*\w \d|O\([^)]*[a-z]\d+(\.\d+)?\)|\b\d+−\d+\b|[A-Za-zε]−1\b|\bN \d\b|\b\d+\.\d+[Nn]\b")


def test_no_value_carries_a_figure_the_text_layer_garbled():
    """The figure check cannot see these: the garble is the same in the quote
    and the value, so "every figure in its quotes" passes (fresh-eyes review
    of cec6020 found 12 stored). Proven to fail by injection, 2026-10-25: with
    the simplex-4-algorithm replacement removed, "O(n2.455)" came back and
    this test went red. Again after the ce2412e review, in memory: with the
    qaoa-qmf-best-empirical-scaling replacement removed, "1.46N" went red."""
    s13 = _script()
    bad = {a.id: m.group(0) for a in _all(s13) if (m := GARBLED.search(a.value))}
    assert not bad, bad


def test_every_high_grade_is_one_the_coordinator_named_with_its_basis():
    s13 = _script()
    raw = _raw(s13)
    kept = _all(s13)
    high = {a.id: a for a in kept if a.certainty == "high"}
    assert set(high) == set(s13.HIGH) & set(raw)
    assert all(s13.HIGH[aid].basis in BASES for aid in high)
    # The reason text is built from the basis, and certainty() grades a vendor claim before HIGH is consulted, so
    # neither is checked here: a check that cannot fail is not a guard (fresh-eyes review of ce2412e). Proven to
    # fail by injection, 2026-10-25, in memory: the cited sai-cited-5g-ids-accuracy added to HIGH went red.
    assert not [i for i in high if raw[i]["kind"] == "cited"]
    moderate = {a.id for a in kept if a.certainty == "moderate"}
    assert moderate == s13.VENDOR_DESCRIPTIONS & set(raw)


def test_no_id_is_both_high_and_named_low():
    """certainty() consults HIGH before THEORY_LOW, so an id in both is HIGH,
    silently; MEASURED_DESPITE names a result kept LOW as measured, which a
    HIGH contradicts (fresh-eyes reviews of ce2412e and 6cfc137). Proven
    to fail by injection, 2026-10-25, in memory: scala-lazy-regime-limit (in
    HIGH) added to THEORY_LOW went red, and to MEASURED_DESPITE went red."""
    s13 = _script()
    assert not set(s13.HIGH) & (set(s13.THEORY_LOW) | set(s13.MEASURED_DESPITE))


def test_every_low_names_its_reason():
    s13 = _script()
    # A vendor's result starts MODERATE and is downgraded one level (store.grading's "vendor claim"). Proven to
    # fail by injection, 2026-10-25: a non-vendor id sent down the vendor branch went red.
    bad = [a.id for a in _all(s13) if a.certainty == "low" and not (
        a.certainty_reasons.startswith("Started MODERATE: vendor") and "DOWNGRADED one level" in a.certainty_reasons
        if a.claim_type == "vendor-self-claim" else a.certainty_reasons.startswith("Started LOW: "))]
    assert not bad, bad


def test_a_theoretical_or_field_reading_the_coordinator_did_not_follow_is_named():
    """A reader's `result_type` is a suggestion, never applied; but where it
    says "theoretical" or "field", or the words name a proof or a bound, and
    the stored reason is "an empirical result", the coordinator names the
    case with why."""
    s13 = _script()
    raw = _raw(s13)
    bad = {}
    for a in _all(s13):
        r = raw[a.id]
        if a.certainty_reasons == s13.EMPIRICAL and a.id not in s13.MEASURED_DESPITE and (
                r.get("result_type") == "theoretical" or theory_words(f"{a.value} {a.citation_context}")):
            bad[a.id] = "theoretical"
        if r.get("result_type") == "field" and a.id not in s13.FIELD_STATEMENTS and a.id not in s13.NOT_FIELD:
            bad[a.id] = "field"
    assert not bad, bad
    assert not set(s13.MEASURED_DESPITE) & set(s13.THEORY_LOW)
    assert not set(s13.NOT_FIELD) & s13.FIELD_STATEMENTS
    assert all(why.strip() for why in (*s13.MEASURED_DESPITE.values(), *s13.NOT_FIELD.values(),
                                       *s13.THEORY_LOW.values()))


def test_a_statement_about_the_field_is_low_and_says_so():
    s13 = _script()
    assert not s13.FIELD_STATEMENTS & set(s13.HIGH)
    got = {a.id: a for a in _all(s13) if a.id in s13.FIELD_STATEMENTS}
    assert set(got) == s13.FIELD_STATEMENTS
    assert not [i for i, a in got.items() if a.certainty != "low" or a.certainty_reasons != s13.FIELD]


def test_every_replaced_value_states_only_signs_its_quotes_hold():
    s13 = _script()
    bad = {a.id: n for a in _all(s13)
           if a.id in s13.VALUE_REPLACE and (n := unsupported_by_basis(a.value, QUOTE.findall(a.citation_context)))}
    assert not bad, bad


def test_every_name_in_the_coordinator_tables_is_an_assertion():
    """A misspelled id in a table does nothing, silently."""
    s13 = _script()
    ids = set(_raw(s13))
    for name in ("HIGH", "VENDOR_DESCRIPTIONS", "FIELD_STATEMENTS", "NOT_FIELD", "THEORY_LOW", "MEASURED_DESPITE",
                 "VALUE_REPLACE", "EXTRA_QUOTES", "QUOTE_EDITS", "CONTEXT_FIX", "ANCHOR_FIX", "DROP"):
        unknown = set(getattr(s13, name)) - ids
        assert not unknown, f"{name}: {sorted(unknown)}"


def test_no_coordinator_table_holds_a_key_twice():
    """A dict literal keeps the last of two equal keys, silently: g03 and g42
    both returned "review-scope", and one decision would have overwritten the
    other."""
    import ast
    from collections import Counter
    tree = ast.parse((ROOT / "scripts" / "sprint13_reading.py").read_text(encoding="utf-8"))
    bad = []
    for node in ast.walk(tree):
        keys = node.keys if isinstance(node, ast.Dict) else node.elts if isinstance(node, ast.Set) else []
        counts = Counter(k.value for k in keys if isinstance(k, ast.Constant))
        bad += [f"line {node.lineno}: {k}" for k, n in counts.items() if n > 1]
    assert not bad, bad


def test_a_full_read_that_lists_its_parts_is_not_entered_as_the_whole_source():
    """Readers marked "full" for reads they then listed as a few sections; a
    note that says the whole paper was read is not such a list. Proven to fail
    by injection, 2026-10-25: with the whole-paper branch of read_detail
    disabled, "Whole paper" was entered as a list and this test went red."""
    s13 = _script()
    listed = s13.read_detail("g01", {"read_extent": "full", "partial_detail": "abstract, conclusion"})
    assert "the whole source" not in listed and "abstract, conclusion" in listed
    assert "the whole source" in s13.read_detail("g01", {"read_extent": "full"})
    # A note that says the whole paper was read is not a list of parts (fresh-eyes review of cec6020).
    for whole in ("Whole paper", "Read the full paper (7 pages).", "Main text read in full; no supplement",
                  "Abstract through conclusion, including limitations"):
        assert "the whole source" in s13.read_detail("g01", {"read_extent": "full", "partial_detail": whole}), whole
    assert "in part: methods" in s13.read_detail("g01", {"read_extent": "partial", "partial_detail": "methods"})


def test_the_reads_and_the_no_copy_list_partition_the_slice():
    s13 = _script()
    slice_ids = {r["record_id"] for r in json.loads(
        (ROOT / "manifests" / "sprint13_f112_slice.json").read_text(encoding="utf-8"))["slice"]}
    read_ids = [p["record_id"] for h in HALVES for _, p in s13.load_groups(h)]
    missing = set(s13.no_copy("1")) | set(s13.no_copy("2"))
    assert len(read_ids) == len(set(read_ids)) == 795
    assert set(read_ids) | missing == slice_ids and not set(read_ids) & missing
    assert len(slice_ids) == 806 and len(missing) == 11


def test_a_reader_file_outside_its_group_is_refused(monkeypatch):
    """No two reads touch one record (team lead, 2026-10-21)."""
    s13 = _script()
    led = s13.ledger()
    g = s13.groups_of("1")[0]
    led["groups"][g]["records"] = led["groups"][g]["records"][1:]
    monkeypatch.setattr(s13, "ledger", lambda: led)
    with pytest.raises(ValueError, match="differ from the ledger"):
        s13.load_groups("1")


@pytest.mark.live_store
@pytest.mark.parametrize("half", HALVES)
def test_every_quote_is_in_its_source(half):
    s13 = _script()
    cache, bad, checked = {}, [], 0
    for _, a, _, p in s13.assertions(half):
        text = cache.setdefault(p["file"], plain(source_text(p["file"])))
        for q in QUOTE.findall(a.citation_context):
            if plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 100


@pytest.mark.live_store
@pytest.mark.parametrize("half", HALVES)
def test_each_read_is_qualified_and_the_store_matches_the_script(live_conn, half):
    s13 = _script()
    for _, p in s13.load_groups(half):
        rid = p["record_id"]
        rows = {(r[0], r[1]) for r in live_conn.execute("SELECT reader, extent FROM paper_reads WHERE record_id = ?",
                                                        (rid,))}
        assert (s13.SUBAGENT_READER, "subagent") in rows, rid
        if [a for a in p["assertions"] if a["id_suggestion"] not in s13.DROP]:
            assert ("Claude", "partial") in rows, rid
            assert live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?",
                                     (rid,)).fetchone()[0] == "read", rid
    bad = []
    for _, a, _, _ in s13.assertions(half):
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (with_common_names(a.value), a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


@pytest.mark.live_store
def test_the_store_holds_no_assertion_the_script_no_longer_makes(live_conn):
    """The row-by-row check above starts from the script, so a row the script
    stopped producing would pass it (fresh-eyes review of ce2412e). Proven to
    fail by injection, 2026-10-25, in memory: with scala-lazy-regime-limit
    left out of the script's assertions, this test went red naming it."""
    s13 = _script()
    stored = {r[0] for r in live_conn.execute("SELECT id FROM records WHERE updated_reason LIKE ?",
                                               (f"%({s13.TAG}): extracted from %",))}
    assert stored == {a.id for a in _all(s13)}, sorted(stored ^ {a.id for a in _all(s13)})[:20]


@pytest.mark.live_store
def test_no_copy_records_keep_their_tier_with_the_reason(live_conn):
    s13 = _script()
    for rid in s13.no_copy("1"):
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        reason, = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
        assert tier != "read", rid
        assert s13.TAG in reason and "NOT read" in reason, rid


@pytest.mark.live_store
@pytest.mark.parametrize("half", HALVES)
def test_a_second_apply_writes_nothing(live_copy, half):
    from store import connect
    s13 = _script()
    conn = connect(live_copy)
    try:
        log = s13.apply_changes(conn, half)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
