"""Sprint 12 Tasks F and G (F104, F105): the first-pass reads entered through
`scripts/sprint12_reading.py`. Every quote is verbatim in its source and
parses as a quote, every figure in a value is in that assertion's own quotes,
HIGH is exactly the coordinator's `high_grades` and carries its named basis
(INTAKE_WORKFLOW.md section 45), never a cited or vendor claim, every name in
the coordinator's tables is an assertion a reader returned, the reads and the
no-copy list partition each task's records, the store holds what the script
says, and a second apply writes nothing. No record read twice is
`test_sprint12_read_ledger.py`."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.grading import BASES  # noqa: E402
from store.quotes import (QUOTE, plain, source_text, stray_quote_marks, unquoted_figures,  # noqa: E402
                          unsupported_by_basis)

TASKS = ("F", "G")


def _script():
    spec = importlib.util.spec_from_file_location("s12", ROOT / "scripts" / "sprint12_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _raw(s12, task: str) -> dict:
    return {a["id_suggestion"]: a for _, p in s12.load_groups(task) for a in p["assertions"]}


@pytest.mark.parametrize("task", TASKS)
def test_every_quote_parses_as_a_quote(task):
    """A quote mark that closes a quote early leaves text outside every
    parse, and the write path would check a fragment. Proven to fail by
    injection, 2026-10-23: with the first EXTRA_QUOTES entry for
    chernyavskiy-constant-shots ending `runs" (p.1) "shots`, this test named
    it. (A straight apostrophe, tried first, is not a quote mark and passes;
    a quote mark nested inside one parsed quote is allowed by design.)"""
    s12 = _script()
    bad = [a.id for _, a, _, _ in s12.assertions(task) if stray_quote_marks(a.citation_context)]
    assert not bad, bad


@pytest.mark.parametrize("task", TASKS)
def test_every_figure_in_a_value_is_in_its_own_quotes(task):
    """Proven to fail by injection, 2026-10-23: with the VALUE_REPLACE entry
    for coreset-limits removed, this test named it with '3' (the reader's
    "3-means")."""
    s12 = _script()
    bad = {a.id: n for _, a, _, _ in s12.assertions(task) if (n := unquoted_figures(a.value, a.citation_context))}
    assert not bad, bad


@pytest.mark.parametrize("task", TASKS)
def test_every_high_grade_is_one_the_coordinator_named_with_its_basis(task):
    """Proven to fail by injection, 2026-10-23: with certainty() returning
    "high" for a reader's "high" suggestion, this test failed for both
    tasks (the readers suggested HIGH for measured results the coordinator
    kept LOW, such as hoffmann-small-batch-limit)."""
    s12 = _script()
    raw = _raw(s12, task)
    kept = s12.assertions(task)
    high = {a.id: a for _, a, _, _ in kept if a.certainty == "high"}
    assert set(high) == set(s12.HIGH) & set(raw)
    for aid, a in high.items():
        assert s12.HIGH[aid].basis in BASES
        assert f"the paper's own {s12.HIGH[aid].basis}" in a.certainty_reasons, aid
    assert not [i for i in high if raw[i]["kind"] == "cited" or raw[i]["claim_type"] == "vendor-self-claim"]
    moderate = {a.id for _, a, _, _ in kept if a.certainty == "moderate"}
    assert moderate == s12.VENDOR_DESCRIPTIONS & set(raw)


def test_a_statement_about_the_field_is_low_and_says_so():
    """The fresh-eyes review of 5744e2d: 14 statements about the field, its
    devices or its literature were graded HIGH "stated limit", and the ones
    kept LOW stored "an empirical result" as the reason. Proven to fail by
    injection, 2026-10-23: with qcnn-scaling-limit put back in HIGH, this
    test named it."""
    s12 = _script()
    both = sorted(s12.FIELD_STATEMENTS & set(s12.HIGH))
    assert not both, both
    got = {a.id: a for t in TASKS for _, a, _, _ in s12.assertions(t) if a.id in s12.FIELD_STATEMENTS}
    assert set(got) == s12.FIELD_STATEMENTS
    assert not [i for i, a in got.items() if a.certainty != "low" or a.certainty_reasons != s12.FIELD], got


def test_a_measured_result_with_theory_words_is_one_the_coordinator_named():
    """Sprint 13 Task F, I2: a LOW that says "an empirical result" while
    its value or quotes name a theorem, a proof or an analytic count is
    either a theoretical result (THEORY_LOW, with its cause) or named in
    MEASURED_DESPITE with why. Proven to fail by injection, 2026-10-25:
    with approx-design-bound-tighter removed from THEORY_LOW, this test
    named it; with kernel-diminishing-returns removed from
    MEASURED_DESPITE, it named that. Both restored."""
    from store.grading import theory_words
    s12 = _script()
    bad = {a.id: w for t in TASKS for _, a, _, _ in s12.assertions(t)
           if a.certainty_reasons == s12.EMPIRICAL and a.id not in s12.MEASURED_DESPITE
           and (w := theory_words(f"{a.value} {a.citation_context}"))}
    assert not bad, bad
    assert not set(s12.MEASURED_DESPITE) & set(s12.THEORY_LOW)
    assert all(why.strip() for why in s12.MEASURED_DESPITE.values())


def test_every_replaced_value_states_only_signs_its_quotes_hold():
    """`require_edit_basis` runs this inside verify(), which needs the source
    text, so CI (live_store deselected) never reached it. The check needs
    only the quotes. Proven to fail by injection, 2026-10-23: with "c → ∞"
    written into dual-vqe-finite-c-estimate's replaced value (its quote stops
    before the sign), this test named the "∞" and no other test failed."""
    s12 = _script()
    bad = {a.id: n for t in TASKS for _, a, _, _ in s12.assertions(t)
           if a.id in s12.VALUE_REPLACE and (n := unsupported_by_basis(a.value, QUOTE.findall(a.citation_context)))}
    assert not bad, bad


def test_every_name_in_the_coordinator_tables_is_an_assertion():
    """A misspelled id in a table does nothing, silently: a HIGH not given,
    a value not replaced. Proven to fail by injection, 2026-10-23: with
    "coreset-limits" spelled "coreset-limit" in HIGH, this test named it."""
    s12 = _script()
    ids = set(_raw(s12, "F")) | set(_raw(s12, "G"))
    for name in ("HIGH", "VENDOR_DESCRIPTIONS", "FIELD_STATEMENTS", "THEORY_LOW", "MEASURED_DESPITE", "VALUE_REPLACE",
                 "EXTRA_QUOTES", "QUOTE_EDITS", "CONTEXT_FIX", "DROP"):
        unknown = set(getattr(s12, name)) - ids
        assert not unknown, f"{name}: {sorted(unknown)}"


def test_the_reads_and_the_no_copy_list_partition_each_task():
    s12 = _script()
    slice_ids = {r["record_id"] for r in json.loads(
        (ROOT / "manifests" / "sprint12_f105_slice.json").read_text(encoding="utf-8"))["slice"]}
    f_ids = s12.task_f_ids()
    for task, want, n_read in (("F", f_ids, 20), ("G", slice_ids, 393)):
        read_ids = {p["record_id"] for _, p in s12.load_groups(task)}
        missing = set(s12.no_copy(task))
        assert len(read_ids) == n_read, task
        assert read_ids | missing == want and not read_ids & missing, task
    assert len(slice_ids) == 400 and len(f_ids) == 21


def test_a_reader_file_outside_its_group_is_refused(monkeypatch):
    """No two reads touch one record (team lead, 2026-10-21)."""
    s12 = _script()
    led = s12.ledger()
    g = s12.groups_of("G")[0]
    led["groups"][g]["records"] = led["groups"][g]["records"][1:]
    monkeypatch.setattr(s12, "ledger", lambda: led)
    with pytest.raises(ValueError, match="differ from the ledger"):
        s12.load_groups("G")


def test_the_coordinator_corrections_hold():
    """Values the coordinator's read changed: a result, a number or a
    reader's inference that the quotes do not carry."""
    s12 = _script()
    v = {a.id: a.value for t in TASKS for _, a, _, _ in s12.assertions(t)}
    assert "3-means" not in v["coreset-limits"]
    # the fresh-eyes review of 5744e2d: a cut that dropped a definition's condition, a scope or an assumption
    assert "high probability" in v["gilfuster-trainability-definition"]
    assert "in this subsection" in v["yang-simulator-limit"]
    assert "GIOs" in v["aqnn-coherence-entanglement-no-help"]
    assert "cryptographic assumptions" in v["gilfuster-bp-trainable"]
    assert "exponential separations" not in v["qaoa-qa-limitation-smooth-angles"]
    assert "Fig." not in v["drl-agent-average-fidelities"]
    assert "Result 1.1" not in v["st-connectivity-subsumes-learning-graph-wdt"]
    assert "regime" not in v["qaoa-no-general-guarantee"]
    assert "theorem-20-separation" not in v
    assert "hoffmann-small-batch-limit" not in s12.HIGH


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_every_quote_is_in_its_source(task):
    """Proven to fail by injection, 2026-10-23: with the EXTRA_QUOTES entry
    for chernyavskiy-constant-shots changed from "AR=0.95" to "AR=0.90",
    this test named it."""
    s12 = _script()
    cache, bad, checked = {}, [], 0
    for _, a, _, p in s12.assertions(task):
        text = cache.setdefault(p["file"], plain(source_text(p["file"])))
        for q in QUOTE.findall(a.citation_context):
            if plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 100


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_each_read_is_qualified_and_the_store_matches_the_script(live_conn, task):
    s12 = _script()
    for _, p in s12.load_groups(task):
        rid = p["record_id"]
        rows = {(r[0], r[1]) for r in live_conn.execute("SELECT reader, extent FROM paper_reads WHERE record_id = ?",
                                                        (rid,))}
        assert (s12.SUBAGENT_READER, "subagent") in rows, rid
        if [a for a in p["assertions"] if a["id_suggestion"] not in s12.DROP]:
            assert ("Claude", "partial") in rows, rid
            assert live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?",
                                     (rid,)).fetchone()[0] == "read", rid
    bad = []
    for _, a, _, _ in s12.assertions(task):
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_no_copy_records_keep_their_tier_with_the_reason(live_conn, task):
    s12 = _script()
    for rid in s12.no_copy(task):
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        reason, = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
        assert tier != "read", rid
        assert s12.TAGS[task] in reason and "NOT read" in reason, rid


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_a_second_apply_writes_nothing(live_copy, task):
    from store import connect
    s12 = _script()
    conn = connect(live_copy)
    try:
        log = s12.apply_changes(conn, task)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
