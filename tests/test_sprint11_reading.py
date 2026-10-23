"""Sprint 11 Tasks F and G (F97, F96): the first-pass reads entered through
`scripts/sprint11_reading.py`. Every quote is verbatim in its source and
parses as a quote, every figure in a value is in that assertion's own quotes,
HIGH is exactly the coordinator's HIGH_REVIEWED and never a cited or vendor
claim, every name in the coordinator's tables is an assertion a reader
returned, the reads and the no-copy list partition Task G's slice, the store
holds what the script says, and a second apply writes nothing."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import QUOTE, plain, source_text, stray_quote_marks, unquoted_figures  # noqa: E402

TASKS = ("F", "G")


def _script():
    spec = importlib.util.spec_from_file_location("s11", ROOT / "scripts" / "sprint11_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _raw(s11, task: str) -> dict:
    return {a["id_suggestion"]: a for _, p in s11.load_groups(task) for a in p["assertions"]}


@pytest.mark.parametrize("task", TASKS)
def test_every_quote_parses_as_a_quote(task):
    """A quote mark inside a quote or a label splits it, and the write path
    would check a fragment. Proven to fail by injection, 2026-10-22: with an
    added quote holding a quote mark on neumann-dqml-proposal, this test
    named it."""
    s11 = _script()
    bad = [a.id for _, a, _, _ in s11.assertions(task) if stray_quote_marks(a.citation_context)]
    assert not bad, bad


@pytest.mark.parametrize("task", TASKS)
def test_every_figure_in_a_value_is_in_its_own_quotes(task):
    """Stricter than F89's test: the figure must be in the assertion's own
    quotes, not anywhere in the paper. Proven to fail by injection,
    2026-10-22: with the VALUE_REPLACE entry for rydberg-fidelity-81-to-90
    removed, this test named it with '2' (the reader's "2D")."""
    s11 = _script()
    bad = {a.id: n for _, a, _, _ in s11.assertions(task) if (n := unquoted_figures(a.value, a.citation_context))}
    assert not bad, bad


@pytest.mark.parametrize("task", TASKS)
def test_every_high_grade_is_one_the_coordinator_named(task):
    """Proven to fail by injection, 2026-10-22: with certainty() also
    returning "high" for a reader's "high" suggestion, this test failed for
    both tasks."""
    s11 = _script()
    raw = _raw(s11, task)
    high = {a.id for _, a, _, _ in s11.assertions(task) if a.certainty == "high"}
    assert high == s11.HIGH_REVIEWED & set(raw)
    assert not [i for i in high if raw[i]["kind"] == "cited" or raw[i]["claim_type"] == "vendor-self-claim"]
    moderate = {a.id for _, a, _, _ in s11.assertions(task) if a.certainty == "moderate"}
    assert moderate == s11.VENDOR_DESCRIPTIONS & set(raw)
    assert not [a.id for _, a, _, _ in s11.assertions(task)
                if a.certainty == "low" and a.id in s11.HIGH_REVIEWED | s11.VENDOR_DESCRIPTIONS]


def test_every_name_in_the_coordinator_tables_is_an_assertion():
    """A misspelled id in a table does nothing, silently: a HIGH not given,
    a value not replaced. Proven to fail by injection, 2026-10-22: with
    "qudit-hardware-limit" spelled "qudit-hardware-limits" in HIGH_REVIEWED,
    this test named it."""
    s11 = _script()
    ids = set(_raw(s11, "F")) | set(_raw(s11, "G"))
    for name in ("HIGH_REVIEWED", "VENDOR_DESCRIPTIONS", "VALUE_REPLACE", "EXTRA_QUOTES", "QUOTE_EDITS",
                 "CONTEXT_FIX", "DROP"):
        unknown = set(getattr(s11, name)) - ids
        assert not unknown, f"{name}: {sorted(unknown)}"


def test_the_reads_and_the_no_copy_list_partition_task_g():
    s11 = _script()
    led = s11.ledger()
    slice_ids = {r["record_id"] for r in json.loads(
        (ROOT / "manifests" / "sprint11_f96_slice.json").read_text(encoding="utf-8"))["slice"]}
    read_ids = {p["record_id"] for _, p in s11.load_groups("G")}
    assert len(slice_ids) == 200 and len(read_ids) == 192
    assert read_ids | set(s11.NO_COPY) == slice_ids and not read_ids & set(s11.NO_COPY)
    assert set(s11.NO_COPY) == set(led["no_copy"])


def test_a_reader_file_outside_its_group_is_refused(monkeypatch):
    """No two reads touch one record (team lead, 2026-10-21)."""
    s11 = _script()
    led = s11.ledger()
    g = s11.groups_of("G")[0]
    led["groups"][g]["records"] = led["groups"][g]["records"][1:]
    monkeypatch.setattr(s11, "ledger", lambda: led)
    with pytest.raises(ValueError, match="differ from the ledger"):
        s11.load_groups("G")


def test_the_coordinator_corrections_hold():
    """Values the coordinator's read changed: reader inference that the
    quotes do not carry."""
    s11 = _script()
    v = {a.id: a.value for t in TASKS for _, a, _, _ in s11.assertions(t)}
    assert "IQM employees" not in v["ronkko-iqm-spark-description"]
    assert "2D" not in v["rydberg-fidelity-81-to-90"]
    assert "Figure 8" not in v["qvit-comparable-to-classical"]
    assert "IBM" not in v["qsvr-hardware-auc-050"]
    assert "linear connectivity" not in v["qcbm-linear-connectivity-no-swap"]
    assert "classical simulations" in v["benchmark-scope-simulation"]


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_every_quote_is_in_its_source(task):
    """Proven to fail by injection, 2026-10-22: with the EXTRA_QUOTES entry
    for slimqfl-mini-mnist-iid-setup changed from "(IID)" to "(non-IID)",
    this test named it."""
    s11 = _script()
    cache, bad, checked = {}, [], 0
    for _, a, _, p in s11.assertions(task):
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
    s11 = _script()
    for _, p in s11.load_groups(task):
        rid = p["record_id"]
        rows = {(r[0], r[1]) for r in live_conn.execute("SELECT reader, extent FROM paper_reads WHERE record_id = ?",
                                                        (rid,))}
        assert (s11.SUBAGENT_READER, "subagent") in rows, rid
        if [a for a in p["assertions"] if a["id_suggestion"] not in s11.DROP]:
            assert ("Claude", "partial") in rows, rid
            assert live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?",
                                     (rid,)).fetchone()[0] == "read", rid
    bad = []
    for _, a, _, _ in s11.assertions(task):
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


@pytest.mark.live_store
def test_no_copy_records_keep_their_tier_with_the_reason(live_conn):
    s11 = _script()
    for rid in s11.NO_COPY:
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        reason, = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
        assert tier != "read", rid
        assert "Sprint 11 Task G, F96" in reason and "NOT read" in reason, rid


@pytest.mark.live_store
@pytest.mark.parametrize("task", TASKS)
def test_a_second_apply_writes_nothing(live_copy, task):
    from store import connect
    s11 = _script()
    conn = connect(live_copy)
    try:
        log = s11.apply_changes(conn, task)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
