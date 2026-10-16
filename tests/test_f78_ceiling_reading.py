"""F78 (Sprint 9 Task E): the ceiling-estimation group read and entered.

Every quote is verbatim in its local copy, every number in a paper's value
appears in that paper, the coordinator's drops and edits are applied (no
reader inference about fraud survives in a value), every CE record is at
`read` or carries the reason it is not, and each read carries a qualifying
coordinator row beside the subagent's."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain, _text  # noqa: E402


def _script():
    spec = importlib.util.spec_from_file_location("f78", ROOT / "scripts" / "sprint9_f78_ceiling_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _source_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() in (".pdf", ".html", ".htm"):
        return _text(path)
    raw = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix.lower() == ".ipynb":
        raw = "\n".join("".join(c.get("source", [])) for c in json.loads(raw)["cells"])
    return _plain(raw)


def _quote_sources(f78) -> dict[str, str]:
    """assertion id -> the file its quotes come from."""
    out = {}
    for g, p in f78.load_groups():
        for a in p["assertions"]:
            out[a["id_suggestion"]] = (a.get("quote_file") or p["file"]).split(" (")[0]
    return out


@pytest.mark.live_store
def test_every_quote_is_in_its_local_copy(live_conn):
    """Proven to fail by injection, 2026-10-15: with the extracted Butt text
    altered ("0.451 for strategic" made "0.415 for strategic") before the
    comparison, this test named butt-0451-is-strategic-n2-only."""
    f78 = _script()
    sources, cache, checked = _quote_sources(f78), {}, 0
    for _, a, _ in f78.assertions():
        stored = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                   (a.id,)).fetchone()
        assert stored, f"{a.id}: not in the store"
        src = sources[a.id]
        text = cache.setdefault(src, _source_text(src))
        for q in _QUOTE.findall(stored[0]):
            assert _plain(q) in text, f"{a.id}: not verbatim in {src}: {q[:70]}"
            checked += 1
    assert checked >= 250


def test_every_number_in_a_paper_value_is_in_the_paper():
    """Task A's review rule, applied here: a figure outside every quote must
    still be in the source. Repositories are excluded (their values name
    code, not figures). Proven to fail by injection, 2026-10-15: with Butt's
    edited value saying 0.4941 instead of 0.494, this test named
    butt-table4-n1-achieved-exceeds-ceiling. (Restoring Boyd's reader value
    "0.31" did NOT turn it red: that figure appears elsewhere in Boyd's text.
    The check proves a figure is in the source, not that it means what the
    value says.)"""
    f78 = _script()
    sources, cache = _quote_sources(f78), {}
    missing = []
    for _, a, rid in f78.assertions():
        if rid in f78.REPOS:
            continue
        text = cache.setdefault(sources[a.id], _source_text(sources[a.id]))
        for num in re.findall(r"(?<!\d)\.?\d+(?:[.,]\d+)?", a.value):
            lead = "" if num.startswith(".") else r"(?<![\d.])"
            if not re.search(rf"{lead}{re.escape(num)}(?!\d)", text):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_no_reader_inference_survives_in_a_value():
    """The coordinator cut every sentence the readers marked as their own
    inference. LIMIT (review, 2026-10-15): this catches only inferences that
    label themselves; unlabeled "so" or "therefore" conclusions were found by
    the fresh-eyes review and cut by hand (REMOVE). Proven to fail by
    injection, 2026-10-15: with the REMOVE
    entry for wheat-samples-per-class-for-5pct-range deleted, its value
    kept "(that last remark is an inference...)" and this test named it."""
    f78 = _script()
    bad = [a.id for _, a, _ in f78.assertions()
           if re.search(r"reader'?s? (inference|consequence)|an inference, not in|check against the PDF", a.value)]
    assert not bad, bad
    ids = {a.id for _, a, _ in f78.assertions()}
    assert not ids & set(f78.DROPPED)


@pytest.mark.live_store
def test_every_ce_record_is_read_or_says_why_not(live_conn):
    f78 = _script()
    rows = live_conn.execute("SELECT p.record_id, p.tier, r.updated_reason FROM paper_fields p JOIN records r "
                             "ON r.id = p.record_id WHERE p.disposition LIKE '%[CE-%'").fetchall()
    assert len(rows) == 31
    for rid, tier, reason in rows:
        if tier != "read":
            assert rid in f78.CLOSED and "hand-download list" in (reason or ""), f"{rid}: {tier}, no reason"
            if rid in f78.NOT_OBTAINABLE:
                assert "not obtainable" in reason, f"{rid}: the Q6 = 1 reason is missing"
    # Chen 2025 arrived 2026-10-16 and is read; Han and Verdu is the one left.
    assert set(f78.CLOSED) == set(f78.NOT_OBTAINABLE) == {"te-sun-1994-generalizing-fano-inequality"}


@pytest.mark.live_store
def test_coordinator_assertions_quote_their_source_verbatim(live_conn):
    """Q6 = 1: Scarlett's (108) entered by the coordinator, with no reader
    manifest behind it. Proven to fail by injection, 2026-10-16: with
    "non-uniform case" changed to "nonuniform case" in the script's quote,
    this test named scarlett-fano-data-processing-form-holds-for-any-prior
    (the store no longer matched the script). LIMIT: that injection stops at
    the first check; the verbatim check below it is the same comparison the
    reader-quote test uses, proven there."""
    f78 = _script()
    path = live_conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (f78.SCARLETT,)).fetchone()[0]
    local = next(s.strip() for s in path.split("|") if s.strip().lower().endswith(".pdf"))
    text = _source_text(local)
    for a in f78.COORDINATOR_ASSERTIONS:
        stored = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                   (a.id,)).fetchone()
        assert stored and stored[0] == a.citation_context, f"{a.id}: not in the store as the script sets it"
        quotes = _QUOTE.findall(a.citation_context)
        assert len(quotes) == 5
        for q in quotes:
            assert _plain(q) in text, f"{a.id}: not verbatim: {q[:70]}"


@pytest.mark.live_store
def test_each_read_has_a_coordinator_row_beside_the_subagent_row(live_conn):
    """ADR-0005 A4: a subagent's report alone does not qualify. Proven to
    fail by injection, 2026-10-15: with the query made to hide Boyd's Claude
    rows, this test named boyd-2012-unachievable-region-precision-recall-space."""
    f78 = _script()
    for _, p in f78.load_groups():
        rid = f78.RECORD_ID.get(p["record_id"], p["record_id"])
        readers = {(r[0], r[1]) for r in live_conn.execute(
            "SELECT reader, extent FROM paper_reads WHERE record_id = ?", (rid,))}
        assert (f78.SUBAGENT_READER, "subagent") in readers, rid
        assert any(r == "Claude" and e in ("full", "partial") for r, e in readers), rid


def test_every_ceiling_fact_has_a_disposition():
    f78 = _script()
    # F-702 is excluded at the source: synthesis, not an extracted fact.
    assert set(f78.FACT_DISPOSITIONS) == ({f"F-70{i}" for i in range(1, 10)} | {"F-710"}) - {"F-702"}
    ids = {a.id for _, a, _ in f78.assertions()}
    for fact, (verdict, named, why) in f78.FACT_DISPOSITIONS.items():
        assert why, fact
        if verdict.startswith("entered"):
            assert set(named) <= ids, (fact, set(named) - ids)


@pytest.mark.live_store
def test_the_answer_document_cites_only_assertions_in_the_store(live_conn):
    """docs/research/ceilings-ml-and-optimization.md names store assertions
    as its evidence; a misspelled or missing id would cite nothing. Proven
    to fail by injection, 2026-10-15: with one cited id misspelled in a copy
    of the document's text, this test named it."""
    doc = (ROOT / "docs" / "research" / "ceilings-ml-and-optimization.md").read_text(encoding="utf-8")
    cited = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9.]+){2,})`", doc))
    cited = {c for c in cited if not c.endswith(".py") and not c.endswith(".md")}
    assert len(cited) >= 50
    missing = sorted(c for c in cited if not live_conn.execute(
        "SELECT 1 FROM records WHERE id = ? AND class = 'assertion'", (c,)).fetchone())
    assert not missing, missing


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f78 = _script()
    conn = connect(live_copy)
    try:
        log = f78.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
