"""F46 (Sprint 9 Task F): the 20 remaining pending facts checked against their
primary sources. Every quote is verbatim, every figure in a value is in its
source (absence claims excepted), every fact has a disposition with a reason,
the absence claim carries its search scope, and each read has a qualifying
coordinator row beside the subagent's."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain, _text  # noqa: E402

FACTS = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008", "F-402", "F-501", "F-502",
         "F-503", "F-504", "F-601", "F-602", "F-603", "F-604", "F-605", "F-606", "F-607"}


def _script():
    spec = importlib.util.spec_from_file_location("f46", ROOT / "scripts" / "sprint9_f46_pending_facts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _files(f46) -> dict[str, str]:
    return {p["record_id"]: p["file"] for _, p in f46.load_groups()}


@pytest.mark.live_store
def test_every_quote_is_in_its_local_copy(live_conn):
    """Proven to fail by injection, 2026-10-15: with Faryad's extracted text
    altered ("dimension count." made "dimension cost.") before the
    comparison, this test named faryad-state-prep-omega-2n-dimension-count.
    (Emptying QUOTE_FIX did NOT turn it red: the test reads the stored
    quotes, which the script had already fixed.)"""
    f46 = _script()
    files, cache, checked = _files(f46), {}, 0
    for _, a, rid in f46.assertions():
        stored = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                   (a.id,)).fetchone()
        assert stored, f"{a.id}: not in the store"
        text = cache.setdefault(rid, _text(files[rid]))
        for q in _QUOTE.findall(stored[0]):
            assert _plain(q) in text, f"{a.id}: not verbatim: {q[:70]}"
            checked += 1
    assert checked >= 70


def test_every_number_in_a_value_is_in_its_source():
    """Absence claims are excepted: their point is that a figure is absent.
    Proven to fail by injection, 2026-10-15: with the REMOVE entry that
    restates 86400 as 24*60*60 deleted, ieee-cis-uid-from-card1-addr1-d1 was
    named."""
    f46 = _script()
    files, cache, missing = _files(f46), {}, []
    for _, a, rid in f46.assertions():
        if a.claim_type == "absence":
            continue
        text = cache.setdefault(rid, _text(files[rid]))
        for num in re.findall(r"(?<!\d)\.?\d+(?:[.,]\d+)?", a.value):
            lead = "" if num.startswith(".") else r"(?<![\d.])"
            if not re.search(rf"{lead}{re.escape(num)}(?!\d)", text):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_every_fact_has_a_disposition_and_the_absence_has_its_scope():
    f46 = _script()
    assert set(f46.FACT_DISPOSITIONS) == FACTS
    ids = {a.id for _, a, _ in f46.assertions()}
    for fact, (verdict, named, why) in f46.FACT_DISPOSITIONS.items():
        assert why, fact
        if verdict.startswith("entered") and "Task E" not in verdict:
            assert set(named) <= ids, (fact, set(named) - ids)
    absences = [a for _, a, _ in f46.assertions() if a.claim_type == "absence"]
    assert absences and all((a.search_scope or "").strip() for a in absences)


@pytest.mark.live_store
def test_merged_and_task_e_facts_point_at_stored_assertions(live_conn):
    f46 = _script()
    for fact, (verdict, named, _) in f46.FACT_DISPOSITIONS.items():
        if verdict == "merged" or "Task E" in verdict:
            for n in named:
                assert live_conn.execute("SELECT 1 FROM records WHERE id = ? AND class = 'assertion'",
                                         (n,)).fetchone(), (fact, n)


@pytest.mark.live_store
def test_each_read_has_a_coordinator_row_beside_the_subagent_row(live_conn):
    f46 = _script()
    for _, p in f46.load_groups():
        rows = {(r[0], r[1]) for r in live_conn.execute(
            "SELECT reader, extent FROM paper_reads WHERE record_id = ?", (p["record_id"],))}
        assert (f46.SUBAGENT_READER, "subagent") in rows, p["record_id"]
        assert ("Claude", "partial") in rows, p["record_id"]


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f46 = _script()
    conn = connect(live_copy)
    try:
        log = f46.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
