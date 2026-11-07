"""Sprint 16 Task H (F51): the CVQBoost findings record and its seven assertions (INTAKE_WORKFLOW.md section 74). The
document lives outside the repository, so every test here is live_store."""
from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("h16", ROOT / "scripts" / "sprint16_f51_cvqboost.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _script()


@pytest.mark.live_store
def test_every_quote_and_figure_is_in_the_document_and_a_wrong_figure_is_refused(monkeypatch):
    """Proven not vacuous, 2026-11-06: with 0.8391 changed to 0.8392 in a value, the check refused it."""
    assert H.check_copies() == []
    assert len(H.verify()) == 7
    a = H.ASSERTIONS[3]
    monkeypatch.setattr(H, "ASSERTIONS", [dataclasses.replace(a, value=a.value.replace("0.8391", "0.8392"))])
    with pytest.raises(ValueError, match="0.8392"):
        H.verify()


def test_each_assertion_is_a_measured_result_held_by_the_record():
    """Single runs on one seed: each LOW, "measured result" (plan Task H). No person is named as the author."""
    assert {a.certainty for a in H.ASSERTIONS} == {"low"}
    assert all("an empirical result from one study" in a.certainty_reasons for a in H.ASSERTIONS)
    assert all(a.provenance.startswith(f"{H.RID}, ") for a in H.ASSERTIONS)
    for field in ("id", "citation", "cited_as", "disposition", "title", "transcribed_from", "checked_against_source"):
        assert "kimmey" not in H.ENTRY[field].lower(), field  # the access path's file name is a label (evidence says so)
    assert "collector's label, not an attribution" in H.ENTRY["evidence"]
    assert all("NOT upgraded" in a.certainty_reasons and "single" in a.certainty_reasons for a in H.ASSERTIONS)


@pytest.mark.live_store
def test_the_record_and_its_seven_assertions_are_held(live_conn):
    """Proven to fail before the apply, 2026-11-06: the record did not exist. The seventh (Manual Validation Q2 = 1)
    names B4 and F162 in its certainty reason and is linked to neither (script docstring); proven to fail by
    injection, 2026-11-06: with F162's id taken out of the seventh's note, the reason check went red."""
    tier, disposition = live_conn.execute("SELECT tier, disposition FROM paper_fields WHERE record_id = ?",
                                          (H.RID,)).fetchone()
    assert tier == "read" and disposition.startswith("Reference:")
    yields = {r[0] for r in live_conn.execute("SELECT assertion_id FROM paper_yields WHERE paper_id = ?", (H.RID,))}
    assert yields == {a.id for a in H.ASSERTIONS}
    contexts = {r[0] for r in live_conn.execute("SELECT context_id FROM paper_applicability WHERE record_id = ?",
                                                (H.RID,))}
    assert contexts == {"platform:dirac-3", "method"}
    ids = [a.id for a in H.ASSERTIONS]
    marks = ",".join("?" * len(ids))
    win = next(a for a in H.ASSERTIONS if a.id == "cvqboost-tuned-in-segment-wins-single-run")
    assert H.B4 in win.certainty_reasons and H.F162 in win.certainty_reasons
    assert not live_conn.execute(  # B4 and F162 are linked to none of the seven (section 74)
        f"SELECT 1 FROM assertion_relations WHERE (from_assertion_id IN (?, ?) AND to_assertion_id IN ({marks})) OR "
        f"(to_assertion_id IN (?, ?) AND from_assertion_id IN ({marks}))",
        (H.B4, H.F162, *ids, H.B4, H.F162, *ids)).fetchone()
    for a in H.ASSERTIONS:  # the store holds the script's current text
        assert tuple(live_conn.execute("SELECT value, certainty_reasons FROM records WHERE id = ?",
                                       (a.id,)).fetchone()) == (a.value, a.certainty_reasons), a.id


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        assert all(line.startswith("exists") for line in H.apply_changes(conn))
    finally:
        conn.close()
