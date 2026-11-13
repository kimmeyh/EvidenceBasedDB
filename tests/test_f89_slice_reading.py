"""F89 (Sprint 10 Task I, the F57 release for Sprint 10): the 74-record slice
read and entered. Every quote is verbatim in its source, every figure in a
value is in its source, no vendor claim is HIGH and no empirical or cited
claim is above LOW, the reads and the no-copy list partition the slice, the
refused record and the no-copy records stay `seen` with their reason, each
entered read has a coordinator row beside the subagent's, and a second
apply writes nothing."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.ingest import FULL_READ_MARK  # noqa: E402
from store.quotes import QUOTE, plain, source_text  # noqa: E402


def _script():
    spec = importlib.util.spec_from_file_location("f89", ROOT / "scripts" / "sprint10_f89_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.live_store
def test_every_quote_is_in_its_source():
    """Proven to fail by injection, 2026-10-18: with the em-dash QUOTE_EDITS
    entry for qrnn-outclassed-by-classical-rnns removed, this test named it."""
    f89 = _script()
    cache, bad, checked = {}, [], 0
    for _, a, _, p in f89.assertions():
        if p["file"] not in cache:  # F140 q6: source_text is already plain; built once per file, not per assertion
            cache[p["file"]] = source_text(p["file"])
        text = cache[p["file"]]
        for q in QUOTE.findall(a.citation_context):
            if plain(q) not in text:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 300


@pytest.mark.live_store
def test_every_figure_in_a_value_is_in_its_source():
    """Proven to fail by injection, 2026-10-18: with Grossi's "0.78" made
    "0.7812" in the group_r4.json value, this test named
    fraud-qsvm-feature-selection-vs-classical-features. LIMIT: a wrong figure
    that appears elsewhere in the paper passes (the first injection, 0.79,
    did); the coordinator's read is what checks attribution."""
    f89 = _script()
    cache, missing = {}, []
    for _, a, _, p in f89.assertions():
        if p["file"] not in cache:  # F140 q6, as above
            cache[p["file"]] = re.sub(r"(\d), (\d{3})(?!\d)", r"\1,\2", source_text(p["file"]))
        text = cache[p["file"]]
        for num in re.findall(r"(?<![\w.])(?<![A-Za-z]-)\d+(?:\.\d+)?", a.value):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", text):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_grades_follow_the_mapping():
    """No vendor claim is HIGH; a cited claim and an empirical result are
    LOW; HIGH only for a proof or the paper's own scope or limits. Proven to
    fail by injection, 2026-10-18: with certainty() returning the reader's
    suggestion for cited-high claims, this test named the cited-high ones."""
    f89 = _script()
    raw = {a["id_suggestion"]: a for _, p in f89.load_groups() for a in p["assertions"]}
    wrong = []
    for _, a, _, _ in f89.assertions():
        r = raw[a.id]
        if r["claim_type"] == "vendor-self-claim" and a.certainty == "high":
            wrong.append(a.id)
        if r["kind"] == "cited" and a.certainty != "low":
            wrong.append(a.id)
        if r["kind"] == "shown" and r["certainty_suggestion"] != "high" and a.certainty != "low":
            wrong.append(a.id)
    assert not wrong, wrong
    assert {a.id for _, a, _, _ in f89.assertions() if a.certainty == "moderate"} == f89.VENDOR_DESCRIPTIONS


def test_every_high_grade_is_one_the_coordinator_named():
    """Task I review (2026-10-18): the first version passed the reader's
    "high" through for every shown or claimed assertion, and the grade test
    never looked at HIGH. Now HIGH is exactly HIGH_REVIEWED, none of it
    cited or vendor, and the three the review downgraded are LOW. Proven to
    fail by injection, 2026-10-18: with aiforscience-hamiltonian-exponential-size
    added back to HIGH_REVIEWED, this test named it."""
    f89 = _script()
    raw = {a["id_suggestion"]: a for _, p in f89.load_groups() for a in p["assertions"]}
    high = {a.id for _, a, _, _ in f89.assertions() if a.certainty == "high"}
    assert high == f89.HIGH_REVIEWED
    assert not [i for i in high if raw[i]["kind"] == "cited" or raw[i]["claim_type"] == "vendor-self-claim"]
    assert not high & {"aiforscience-hamiltonian-exponential-size", "martin-tensor-network-gradient-variance-vs-distance",
                       "martin-qttn-qmera-recommended-over-qmps", "zuchongzhi-vqe-f2-above-chemical-accuracy"}


def test_the_reads_and_the_no_copy_list_partition_the_slice():
    f89 = _script()
    slice_ids = {r["record_id"] for r in json.loads(
        (ROOT / "manifests" / "sprint10_f89_slice.json").read_text(encoding="utf-8"))["slice"]}
    read_ids = {p["record_id"] for _, p in f89.load_groups()}
    assert len(slice_ids) == 74
    assert read_ids | set(f89.NO_COPY) == slice_ids and not read_ids & set(f89.NO_COPY)
    assert set(f89.REFUSE) <= read_ids


def test_the_coordinator_corrections_hold():
    """The coordinator's read: the QGNN's two AUCs are different curves, and
    Aimeur's MST bound is stated as the page prints it."""
    f89 = _script()
    v = {a.id: a.value for _, a, _, _ in f89.assertions()}
    assert "a ROC curve" in v["qgnn-pr-auc-085"]
    assert "Theta(n^(3/2))" in v["aimeur-mst-quantum-optimal-n32"]
    # Task I review: the source's complexity and threshold, not the reader's
    assert "polylogarithmic" not in v["carleman-quadratic-ode-exponential-improvement-in-T"]
    assert "T^2 q poly" in v["carleman-quadratic-ode-exponential-improvement-in-T"]
    assert "square root of 2" in v["quadratic-ode-lower-bound-strong-nonlinearity"]
    assert "readout errors" not in v["zuchongzhi-vqe-processor-insufficient-for-larger-molecules"]
    assert "kaur-vacancies-62-percent-phd" not in v


@pytest.mark.live_store
def test_refused_and_no_copy_records_stay_seen_with_the_reason(live_conn):
    f89 = _script()
    for rid in list(f89.REFUSE) + list(f89.NO_COPY):
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        reason, = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
        assert tier == "seen", rid
        assert "Sprint 10 Task I, F89" in reason and "NOT" in reason, rid


@pytest.mark.live_store
def test_each_read_is_qualified_and_the_store_matches_the_script(live_conn):
    f89 = _script()
    for _, p in f89.kept_groups():
        rid = p["record_id"]
        rows = {(r[0], r[1]) for r in live_conn.execute("SELECT reader, extent FROM paper_reads WHERE record_id = ?",
                                                        (rid,))}
        assert (f89.SUBAGENT_READER, "subagent") in rows and ("Claude", "partial") in rows, rid
        assert live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] == "read"
    bad = []
    for _, a, _, _ in f89.assertions():
        if FULL_READ_MARK in (live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (a.id,)).fetchone()
                              or ("",))[0]:
            continue  # re-read in full by Sprint 13 Task G or F114 (Sprint 14), whose own tests check it
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f89 = _script()
    conn = connect(live_copy)
    try:
        log = f89.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
