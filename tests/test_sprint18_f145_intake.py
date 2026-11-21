"""F145 (Sprint 18 Task E): qubit-lab.ch's Evidence page, `scripts/sprint18_f145_intake.py`, INTAKE_WORKFLOW.md
section 80.

Proven to fail by injection, 2026-11-21, each restored (a grep for INJECTED in the script finds nothing):
- `LOW_VENDOR` set to `low_grade("measured result")`: test_every_assertion_is_a_vendor_claim_with_the_stores_one_
  vendor_reason went red;
- `A` refusing only a `certainty` of its own (`if "certainty" in kw:  # INJECTED`): test_a_grade_of_its_own_is_refused
  went red (a certainty_reasons of its own passed);
- `differs` leaving out the context check: test_differs_names_each_field_that_differs_and_nothing_when_the_same went
  red;
- QL-ST-006's "11 of 42" changed to "11 of 43" in the value: test_every_quote_is_verbatim_in_the_saved_page_with_the_
  values_figures and test_the_store_holds_the_source_and_each_assertion_as_the_script_states_it went red.
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sprint18_f145_intake.py"


def _mod():
    spec = importlib.util.spec_from_file_location("f145", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _store(mod, rows):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id, class, value, provenance, evidence_tag, certainty, certainty_reasons, "
                 "fidelity)")
    conn.execute("CREATE TABLE assertion_fields (record_id, citation_context, derivation, claim_type)")
    conn.execute("CREATE TABLE record_contexts (record_id, context_id)")
    for a in rows:
        conn.execute("INSERT INTO records VALUES (?, 'assertion', ?, ?, ?, ?, ?, ?)",
                     (a.id, mod.with_common_names(a.value), a.provenance, a.evidence_tag, a.certainty,
                      a.certainty_reasons, a.fidelity))
        conn.execute("INSERT INTO assertion_fields VALUES (?, ?, ?, ?)",
                     (a.id, a.citation_context, a.derivation, a.claim_type))
        conn.execute("INSERT INTO record_contexts VALUES (?, ?)", (a.id, a.context))
    return conn


def test_every_assertion_is_a_vendor_claim_with_the_stores_one_vendor_reason():
    mod = _mod()
    from store.grading import VENDOR_LOW
    assert len(mod.ASSERTIONS) == 16
    assert len({a.id for a in mod.ASSERTIONS}) == 16
    for a in mod.ASSERTIONS:
        assert (a.claim_type, a.certainty, a.certainty_reasons) == ("vendor-self-claim", "low", VENDOR_LOW), a.id
        assert a.provenance.startswith(mod.SOURCE_ID + ", "), a.id


def test_a_grade_of_its_own_is_refused():
    mod = _mod()
    for extra in ({"certainty": "high"}, {"certainty_reasons": "Started LOW: mine"}):
        with pytest.raises(ValueError, match="fixed vendor LOW"):
            mod.A(id="x", context="qml", value="v", provenance="p", quotes=["q" * 20], **extra)


def test_differs_names_each_field_that_differs_and_nothing_when_the_same():
    mod = _mod()
    a, b = mod.ASSERTIONS[0], mod.ASSERTIONS[1]
    conn = _store(mod, [a])
    assert mod.differs(conn, a) == set()
    assert mod.differs(conn, b) is None
    conn.execute("UPDATE records SET value = value || ' (edited)', fidelity = 'other' WHERE id = ?", (a.id,))
    conn.execute("UPDATE record_contexts SET context_id = 'world' WHERE record_id = ?", (a.id,))
    assert mod.differs(conn, a) == {"value", "fidelity", "context"}


def test_each_decided_correction_names_only_fields_a_review_decided():
    mod = _mod()
    ids = {a.id for a in mod.ASSERTIONS}
    for aid, fields in mod.DECIDED.items():
        assert aid in ids, aid
        assert fields and fields <= set(mod._FIELDS) | {"context"}, aid


@pytest.mark.live_store
def test_every_quote_is_verbatim_in_the_saved_page_with_the_values_figures():
    mod = _mod()
    assert len(mod.verify_all()) == 16


@pytest.mark.live_store
def test_the_store_holds_the_source_and_each_assertion_as_the_script_states_it(live_conn):
    """A record whose last change came from a later script (a decided correction elsewhere) is that script's to
    match; every other is compared field by field. Read-only, through the live fixture."""
    mod = _mod()
    assert mod.source_differs(live_conn) == set()
    wrong = []
    for a in mod.ASSERTIONS:
        reason = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (a.id,)).fetchone()
        assert reason is not None, a.id
        if mod.TAG in reason[0].rsplit(" | ", 1)[-1] and mod.differs(live_conn, a):
            wrong.append(a.id)
    assert wrong == []
