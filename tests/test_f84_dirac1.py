"""F84 (Sprint 10 Task F; ADR-0004 A10, team lead Q1 = 1): the nine
Dirac-1 records, retagged from platform:dirac-3 to platform:dirac-1 and
entered. Every quote is verbatim in its saved page, every figure a value
states is on that page, no record keeps platform:dirac-3, each is read
with a coordinator row and yields, and a second apply writes nothing."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain, _text  # noqa: E402


def _script():
    spec = importlib.util.spec_from_file_location("f84", ROOT / "scripts" / "sprint10_f84_dirac1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sources(f84) -> dict[str, str]:
    return {p["record_id"]: _text(p["file"]) for _, p in f84.papers()}


@pytest.mark.live_store
def test_every_quote_is_in_its_page():
    """Proven to fail by injection, 2026-10-18: with "about six minutes"
    made "about five minutes" in the BMW quote in group_j2.json, this test
    named qci-web-bmw-sensor-six-minutes (the store and second-apply tests
    went red too). Restored."""
    f84 = _script()
    text, bad, checked = _sources(f84), [], 0
    for a, rid in f84.assertions():
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in text[rid]:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked >= 27


@pytest.mark.live_store
def test_every_figure_in_a_value_is_on_its_page():
    """The read that found "64 binary variables", a figure the page never
    states. Proven to fail by injection, 2026-10-18: with that VALUE_EDITS
    entry removed, this test named dirac1-tsp-8-cities-qap-formulation (64).
    LIMIT (review of 9781f9f): a figure anywhere on the page passes, so a
    wrong figure that appears elsewhere on it (430 made 441) is not caught;
    the coordinator's read is what checks that."""
    f84 = _script()
    text, missing = _sources(f84), []
    for a, rid in f84.assertions():
        page = re.sub(r"(\d), (\d{3})(?!\d)", r"\1,\2", text[rid])
        for num in re.findall(r"(?<!\d)\.?\d+(?:[.,]\d+)*", a.value):
            lead = "" if num.startswith(".") else r"(?<![\d.])"
            if not re.search(rf"{lead}{re.escape(num)}(?!\d)", page):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_the_values_say_what_the_pages_say():
    """The coordinator's read, and the fresh-eyes review of 9781f9f that
    corrected it. Cut: "64 binary variables", a figure the TSP page never
    states. Kept, with its quote: the UAS page's own "better than O(n^3)"
    conclusion, which the first version cut as the reader's (a search for
    the word "cubic" missed the notation). Corrected: the portfolio run's
    dates (the backtest ran 2022-01-13 to 2022-12-30; 2020 to 2023 is the
    page's example) and the reader's "(modes)" gloss. Proven to fail by
    injection, 2026-10-18: with the TSP VALUE_EDITS entry removed, the 64
    check went red; with the portfolio entry removed, the date check did."""
    f84 = _script()
    values = {a.id: a.value for a, _ in f84.assertions()}
    assert "64 binary" not in values["dirac1-tsp-8-cities-qap-formulation"]
    uas = values["dirac1-uas-10364-vars-13852s-polynomial-claim"]
    assert "better than O(n^3)" in uas and "within polynomial time" in uas
    assert "backtest the page ran covers 2022-01-13 to 2022-12-30" in values["dirac1-portfolio-select-30-stocks-binary"]
    assert "(modes)" not in values["qci-web-eqc-30000-qubit-limit-estimate"]


_DESCRIPTIONS = {  # the tutorial's setup or scope, read 2026-10-18; held here, not read from the script
    "dirac1-pca-qubo-medicare-93-to-3", "dirac1-pca-not-np-hard-demo", "dirac1-feature-selection-10-of-93",
    "dirac1-graph-partition-two-small-graphs", "dirac1-portfolio-select-30-stocks-binary",
    "dirac1-tsp-8-cities-qap-formulation",
}


def test_vendor_descriptions_are_moderate_and_vendor_results_low():
    """No vendor claim about its own product is HIGH. The six descriptions
    are listed in this test, so emptying the script's set cannot also
    empty the expectation (fresh-eyes review of 9781f9f: the first version
    compared against the script's own set). Proven to fail by injection,
    2026-10-18: with the script's DESCRIPTIONS emptied, this test named
    the six."""
    f84 = _script()
    got = {a.id: a.certainty for a, _ in f84.assertions()}
    assert all(a.claim_type == "vendor-self-claim" for a, _ in f84.assertions())
    wrong = [i for i, c in got.items() if c != ("moderate" if i in _DESCRIPTIONS else "low")]
    assert not wrong, wrong
    assert len(_DESCRIPTIONS) == 6 and _DESCRIPTIONS <= set(got) and len(got) == 12


def _nine_problems(conn, nine) -> list[str]:
    out = []
    if not conn.execute("SELECT 1 FROM contexts WHERE id = 'platform:dirac-1'").fetchone():
        out.append("no platform:dirac-1 context")
    yields = {r[0] for r in conn.execute("SELECT paper_id FROM paper_yields")}
    for rid in nine:
        ctxs = [r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))]
        tier, = conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        readers = {(r[0], r[1]) for r in conn.execute("SELECT reader, extent FROM paper_reads WHERE record_id = ?",
                                                      (rid,))}
        if ctxs != ["platform:dirac-1"] or tier != "read" or rid not in yields or \
                ("Claude", "partial") not in readers or not any(e == "subagent" for _, e in readers):
            out.append(rid)
    return out


@pytest.mark.live_store
def test_the_nine_are_read_under_dirac_1_and_yield(live_conn):
    assert not _nine_problems(live_conn, _script().NINE)


@pytest.mark.live_store
def test_the_nine_check_names_a_record_still_tagged_dirac_3(live_copy):
    """The check above, proven able to fail: a copy of the store with
    platform:dirac-3 put back on one record is named."""
    from store import connect
    f84 = _script()
    conn = connect(live_copy)
    try:
        conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, 'platform:dirac-3')",
                     (f84.NINE[0],))
        assert _nine_problems(conn, f84.NINE) == [f84.NINE[0]]
    finally:
        conn.close()


@pytest.mark.live_store
def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    """Proven to fail by injection, 2026-10-18: with the TSP and UAS
    VALUE_EDITS entries removed and not applied, this test named both
    assertions, and the second-apply test logged their updates."""
    f84 = _script()
    bad = []
    for a, _ in f84.assertions():
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                               (a.id,))]
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context,
                                     a.claim_type) or ctx != [a.context]:
            bad.append(a.id)
    assert not bad, bad


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f84 = _script()
    conn = connect(live_copy)
    try:
        log = f84.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
