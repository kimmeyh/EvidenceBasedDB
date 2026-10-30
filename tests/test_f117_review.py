"""Sprint 14 Task E (F117): a group's review decisions turned into the applier's review file."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def review(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("f117_review", ROOT / "scripts" / "f117_review.py")
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    reads = tmp_path / "reads"
    reads.mkdir()
    (reads / "group_g050.json").write_text(json.dumps({"papers": [{
        "record_id": "p1",
        "assertions": [
            {"id_suggestion": "thm", "certainty_suggestion": "high", "result_type": "theoretical", "value": "v"},
            {"id_suggestion": "sim", "certainty_suggestion": "low", "result_type": "measured", "value": "v"},
            {"id_suggestion": "sketch", "certainty_suggestion": "low", "result_type": "theoretical", "value": "v"}],
        "existing": [
            {"id": "st-hi", "verdict": "confirmed", "result_type": "setup", "value": "v"},
            {"id": "st-lo", "verdict": "confirmed", "result_type": "measured", "value": "v"},
            {"id": "narrow", "verdict": "narrowed", "result_type": "measured", "value": "v"}]}]}), encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {"g050": {"records": [{"record_id": "p1"}, {"record_id": "u"}]}}}),
                      encoding="utf-8")
    monkeypatch.setattr(r, "READS_DIR", reads)
    monkeypatch.setattr(r, "REVIEW", tmp_path / "review")
    monkeypatch.setattr(r.build.cloud, "LEDGER", ledger)
    monkeypatch.setattr(r.build, "UNREAD", {"u": "no text"})
    (tmp_path / "review" / "decisions").mkdir(parents=True)
    r.STORED = {"st-hi": "high", "st-lo": "low", "narrow": "high"}
    r.TEXT = {"st-hi": ("the stored value", "\"the stored quote\" (Section 2)")}
    monkeypatch.setattr(r, "stored_text", lambda ids: r.TEXT)
    return r


def _decide(r, decisions: dict) -> None:
    (r.REVIEW / "decisions" / "g050.json").write_text(json.dumps(decisions), encoding="utf-8")


GOOD = {"thm": {"decision": "high", "basis": "proved result", "why": "Theorem 1, proved in Appendix A"},
        "sketch": {"decision": "low", "why": "a sketch, not a proof"},
        "st-hi": {"decision": "high", "basis": "setup", "why": "Section 2 states it"},
        "narrow": {"decision": "accept", "grade": "high", "basis": "stated limit", "why": "Section 5 states it"}}


def test_items_are_the_decisions_a_group_needs(review):
    """Proven to fail by injection, 2026-10-30: with stored-high items left out, `st-hi` was missing."""
    its = {i["id"]: i["kind"] for i in review.items("g050", review.STORED)}
    assert its == {"thm": "new-high", "sketch": "new-theory", "st-hi": "stored-high", "narrow": "changed"}


def test_a_stored_item_carries_the_stored_value_and_quotes(review):
    """g043's pilot: a confirmed entry may carry no value, so the reviewer saw a blank stored HIGH. Proven to fail by
    injection, 2026-10-30: with `shown` left out of the stored-high item, its stored_value was missing."""
    its = {i["id"]: i for i in review.items("g050", review.STORED)}
    assert its["st-hi"]["stored_value"] == "the stored value"
    assert its["st-hi"]["stored_quotes"].startswith('"the stored quote"')
    assert its["narrow"]["stored_value"] == ""


def test_finalize_writes_the_applier_tables(review):
    _decide(review, GOOD)
    out = review.finalize("g050", "2026-10-30", review.STORED)
    assert out["graded_high"] == {"thm": ["proved result", "Theorem 1, proved in Appendix A"],
                                  "st-hi": ["setup", "Section 2 states it"],
                                  "narrow": ["stated limit", "Section 5 states it"]}
    assert out["theory_low"] == {"sketch": "a sketch, not a proof"}
    assert out["unread"] == {"u": "no text"}
    assert (out["tag"], out["reader"]) == (review.TAG, review.READER)


def test_a_missing_or_malformed_decision_is_refused(review):
    """Proven to fail by injection, 2026-10-30: with the basis check removed, a HIGH on "measured result" passed."""
    _decide(review, {k: v for k, v in GOOD.items() if k != "sketch"})
    with pytest.raises(ValueError, match="no decision"):
        review.finalize("g050", "2026-10-30", review.STORED)
    _decide(review, {**GOOD, "thm": {"decision": "high", "basis": "measured result", "why": "x"}})
    with pytest.raises(ValueError, match="basis"):
        review.finalize("g050", "2026-10-30", review.STORED)
    _decide(review, {**GOOD, "sketch": {"decision": "low", "why": " "}})
    with pytest.raises(ValueError, match="why"):
        review.finalize("g050", "2026-10-30", review.STORED)


def test_a_certainty_change_waits_for_the_team_lead(review):
    """F117's card: the team lead decides any certainty level a review changes. Proven to fail by injection,
    2026-10-30: with the escalation skipped, the stored HIGH went to LOW in the review file unasked."""
    _decide(review, {**GOOD, "st-hi": {"decision": "low", "why": "the passage is an interpretation"},
                     "narrow": {"decision": "accept", "grade": "low", "why": "a measured result"}})
    with pytest.raises(ValueError, match="2 certainty changes wait for the team lead"):
        review.finalize("g050", "2026-10-30", review.STORED)
    pending = json.loads((review.REVIEW / "escalations" / "g050.pending.json").read_text(encoding="utf-8"))
    assert set(pending) == {"st-hi", "narrow"}
    (review.REVIEW / "escalations" / "g050.json").write_text(json.dumps({"st-hi": "low", "narrow": "low"}),
                                                              encoding="utf-8")
    out = review.finalize("g050", "2026-10-30", review.STORED)
    assert "st-hi" not in out["graded_high"] and out["requote"]["st-hi"].startswith("regraded LOW")
    assert "narrow" not in out["graded_high"]
