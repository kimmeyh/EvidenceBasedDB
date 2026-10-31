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
    monkeypatch.setattr(r.build, "local_file", lambda rid: None)
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


def test_a_local_read_names_task_fs_reader(review, monkeypatch):
    """Sprint 14 Task F: a group read wholly by local readers takes F's tag and reader; in a group that mixes cloud and
    local reads, each local record names the local reader and F's tag (review of 1cb63bb: the group's cloud tag went
    into a local read's provenance). Proven to fail by injection, 2026-10-30: with the local check removed from
    finalize, the wholly local group kept the cloud session's reader; with `tags` left out, the mixed group had none."""
    _decide(review, GOOD)
    monkeypatch.setattr(review.build, "local_file", lambda rid: Path(f"{rid}.json"))
    out = review.finalize("g050", "2026-10-30", review.STORED)
    assert (out["tag"], out["reader"]) == (review.LOCAL_TAG, review.LOCAL_READER)
    assert "readers" not in out and "tags" not in out
    path = review.READS_DIR / "group_g050.json"
    group = json.loads(path.read_text(encoding="utf-8"))
    group["papers"].append({"record_id": "p2", "assertions": [], "existing": []})
    path.write_text(json.dumps(group), encoding="utf-8")
    monkeypatch.setattr(review.build, "local_file", lambda rid: Path("p1.json") if rid == "p1" else None)
    out = review.finalize("g050", "2026-10-30", review.STORED)
    assert (out["tag"], out["reader"]) == (review.TAG, review.READER)
    assert out["readers"] == {"p1": review.LOCAL_READER}
    assert out["tags"] == {"p1": review.LOCAL_TAG}


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


def test_a_moderate_change_waits_and_a_settlement_is_checked(review):
    """Review of 46d088d: a stored MODERATE went to LOW unasked (only HIGH and LOW were checked); a settlement was
    taken as written ("HIGH" or a typo passed); the team lead could not keep a stored HIGH, having no way to name its
    basis; each settlement must be the item's own. Proven to fail by injection, 2026-10-30: with the old
    `was in ("high", "low")` test, nothing waited for "narrow"; with `_settled` returning its input, "HIGH" passed;
    with every item reading the first settlement, "st-hi" took "narrow"'s low."""
    stored = {**review.STORED, "narrow": "moderate"}
    _decide(review, {**GOOD, "narrow": {"decision": "accept", "grade": "low", "why": "a measured result"}})
    with pytest.raises(ValueError, match="1 certainty changes"):
        review.finalize("g050", "2026-10-30", stored)
    esc = review.REVIEW / "escalations" / "g050.json"
    esc.write_text(json.dumps({"narrow": "HIGH"}), encoding="utf-8")
    with pytest.raises(ValueError, match="settled decision"):
        review.finalize("g050", "2026-10-30", stored)
    _decide(review, {**GOOD, "st-hi": {"decision": "low", "why": "an interpretation"},
                     "narrow": {"decision": "accept", "grade": "low", "why": "a measured result"}})
    esc.write_text(json.dumps({"narrow": "low", "st-hi": ["high", "setup", "Section 2 states the setup"]}),
                   encoding="utf-8")
    out = review.finalize("g050", "2026-10-30", stored)
    assert out["graded_high"]["st-hi"] == ["setup", "kept HIGH at the team lead's decision: Section 2 states the setup"]
    assert "narrow" not in out["graded_high"] and "st-hi" not in out["requote"]
    esc.write_text(json.dumps({"narrow": "low", "st-hi": "low", "nobody": "low"}), encoding="utf-8")
    with pytest.raises(ValueError, match="settled decisions for no item"):
        review.finalize("g050", "2026-10-30", stored)


def test_a_vendor_claim_is_never_high_and_stray_decisions_are_refused(review):
    """Review of de1efff: 10 signed HIGHs on vendors' own claims would have been written LOW without a word; a
    decision for no item was ignored. Proven to fail by injection, 2026-10-30: with the vendor check removed from
    _grade, the HIGH passed; with the stray check removed, the extra decision passed."""
    path = review.READS_DIR / "group_g050.json"
    group = json.loads(path.read_text(encoding="utf-8"))
    group["papers"][0]["assertions"][0]["claim_type"] = "vendor-self-claim"
    path.write_text(json.dumps(group), encoding="utf-8")
    _decide(review, GOOD)
    with pytest.raises(ValueError, match="vendor's own claim"):
        review.finalize("g050", "2026-10-30", review.STORED)
    _decide(review, {**GOOD, "thm": {"decision": "low", "why": "a vendor's own claim"}, "nobody": GOOD["sketch"]})
    with pytest.raises(ValueError, match="decisions for no item"):
        review.finalize("g050", "2026-10-30", review.STORED)


def test_the_coordinators_sign_off_is_merged_on_every_finalize(review):
    """A re-finalize must not lose the coordinator's sign-off edits. Proven to fail by injection, 2026-10-30: with
    _merge_signoff not called, the value_replace was missing; with the id check removed, an edit for an id outside
    the group passed."""
    _decide(review, GOOD)
    so = review.REVIEW / "signoff"
    so.mkdir()
    (so / "g050.json").write_text(json.dumps({"value_replace": {"thm": "the corrected value"},
                                              "requote": {"st-lo": "anchor moved"}}), encoding="utf-8")
    out = review.finalize("g050", "2026-10-30", review.STORED)
    assert out["value_replace"] == {"thm": "the corrected value"} and out["requote"] == {"st-lo": "anchor moved"}
    (so / "g050.json").write_text(json.dumps({"value_replace": {"elsewhere": "v"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="not in the group"):
        review.finalize("g050", "2026-10-30", review.STORED)
    (so / "g050.json").write_text(json.dumps({"regrade_high": {"thm": "x"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="does not read"):
        review.finalize("g050", "2026-10-30", review.STORED)


def test_a_reentry_names_a_paper_of_the_group(review):
    """Review of b185729: a paper refused at an earlier read enters only where the review names it in `reenter`,
    keyed by record id. Proven to fail by injection, 2026-10-30: with the reenter table checked against assertion
    ids, the record id was refused."""
    _decide(review, GOOD)
    so = review.REVIEW / "signoff"
    so.mkdir()
    (so / "g050.json").write_text(json.dumps({"reenter": {"p1": "the team lead's decision"}}), encoding="utf-8")
    assert review.finalize("g050", "2026-10-30", review.STORED)["reenter"] == {"p1": "the team lead's decision"}
    (so / "g050.json").write_text(json.dumps({"reenter": {"thm": "x"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="not in the group"):
        review.finalize("g050", "2026-10-30", review.STORED)


def _retype(review, aid: str, **fields) -> None:
    path = review.READS_DIR / "group_g050.json"
    group = json.loads(path.read_text(encoding="utf-8"))
    for p in group["papers"]:
        for a in p["assertions"] + p["existing"]:
            if a.get("id", a.get("id_suggestion")) == aid:
                a.update(fields)
    path.write_text(json.dumps(group), encoding="utf-8")


def test_a_settled_low_names_its_cause_and_a_settled_high_is_never_a_vendors(review):
    """Review of aabdd49: a LOW settled against a HIGH proposal kept the reviewer's case for HIGH as its cause; a
    settled HIGH on a vendor's own claim passed finalize and failed only at the apply. Proven to fail by injection,
    2026-10-30: with the proposed-HIGH check removed, a bare "low" passed; with the settled vendor check removed, the
    HIGH passed."""
    _retype(review, "narrow", result_type="theoretical")
    stored = {**review.STORED, "narrow": "low"}
    _decide(review, GOOD)
    esc = review.REVIEW / "escalations" / "g050.json"
    esc.parent.mkdir()
    esc.write_text(json.dumps({"narrow": "low"}), encoding="utf-8")
    with pytest.raises(ValueError, match="names its cause"):
        review.finalize("g050", "2026-10-30", stored)
    esc.write_text(json.dumps({"narrow": ["low", "only sketched in Section 5"]}), encoding="utf-8")
    out = review.finalize("g050", "2026-10-30", stored)
    assert out["theory_low"]["narrow"] == "only sketched in Section 5" and "narrow" not in out["graded_high"]
    _retype(review, "st-hi", claim_type="vendor-self-claim")
    _decide(review, {**GOOD, "st-hi": {"decision": "low", "why": "a vendor's own claim"}})
    esc.write_text(json.dumps({"narrow": ["low", "sketched"], "st-hi": ["high", "setup", "x"]}), encoding="utf-8")
    with pytest.raises(ValueError, match="settled HIGH, but a vendor's own claim"):
        review.finalize("g050", "2026-10-30", stored)


def test_a_sign_off_the_applier_would_ignore_or_could_not_enter_is_refused(review):
    """Review of aabdd49: a sign-off requote rewrote a stored MODERATE as LOW unasked; a drop of a stored id, a
    requote of a changed entry and an edit on an id not written were ignored by the applier without a word; a blank
    entry settled LOW reached the apply. Proven to fail by injection, 2026-10-30: with each check in _check_written
    removed in turn, its case passed."""
    _decide(review, GOOD)
    so = review.REVIEW / "signoff"
    so.mkdir()
    cases = [({"requote": {"st-lo": "fuller quotes"}}, {**review.STORED, "st-lo": "moderate"}, "rewrites stored"),
             ({"drop": {"st-lo": "x"}}, review.STORED, "not a new assertion"),
             ({"requote": {"narrow": "x"}}, review.STORED, "not a confirmed stored entry"),
             ({"value_replace": {"st-lo": "v2"}}, review.STORED, "does not write")]
    for edits, stored, match in cases:
        (so / "g050.json").write_text(json.dumps(edits), encoding="utf-8")
        with pytest.raises(ValueError, match=match):
            review.finalize("g050", "2026-10-30", stored)
    (so / "g050.json").unlink()
    _retype(review, "st-hi", value="")
    _decide(review, {**GOOD, "st-hi": {"decision": "low", "why": "an interpretation"}})
    esc = review.REVIEW / "escalations" / "g050.json"
    esc.parent.mkdir()
    esc.write_text(json.dumps({"st-hi": "low"}), encoding="utf-8")
    with pytest.raises(ValueError, match="no value"):
        review.finalize("g050", "2026-10-30", review.STORED)
    (so / "g050.json").write_text(json.dumps({"value_replace": {"st-hi": "the value"}}), encoding="utf-8")
    assert review.finalize("g050", "2026-10-30", review.STORED)["requote"]["st-hi"].startswith("regraded LOW")
