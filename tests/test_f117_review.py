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


def test_a_split_review_is_merged_from_its_parts_and_a_double_decision_is_refused(review):
    """F142 part 3 (Sprint 17 Task C): a proof appendix over 30 pages is split across reviewers by page from the
    start, each writing `decisions/<g>.pN.json`. Sprint 16: Monaco's 70-page supplement was graded from statements,
    and two fresh reviewers then changed 13 of 94 decisions. Proven red 2026-11-07: with `decisions_of` reading only
    `<g>.json` (INJECTED), the parted group raised FileNotFoundError; with the duplicate check removed (INJECTED), an
    item decided in two parts kept the later decision silently."""
    folder = review.REVIEW / "decisions"
    items = list(GOOD.items())
    (folder / "g050.p1.json").write_text(json.dumps(dict(items[:2])), encoding="utf-8")
    (folder / "g050.p2.json").write_text(json.dumps(dict(items[2:])), encoding="utf-8")
    out = review.finalize("g050", "2026-11-07", review.STORED)
    assert out["theory_low"] == {"sketch": "a sketch, not a proof"} and "thm" in out["graded_high"]

    (folder / "g050.p2.json").write_text(json.dumps(dict(items[1:])), encoding="utf-8")  # "sketch" in both parts
    with pytest.raises(ValueError, match="decided in two parts"):
        review.finalize("g050", "2026-11-07", review.STORED)

    (folder / "g050.p2.json").write_text(json.dumps(dict(items[2:])), encoding="utf-8")
    _decide(review, GOOD)  # the whole file as well as the parts
    with pytest.raises(ValueError, match="keep one form"):
        review.finalize("g050", "2026-11-07", review.STORED)


def test_a_re_entry_group_is_finalized_without_a_ledger_entry(review, monkeypatch):
    """F125 (Sprint 15 Task C): g050-r1 re-enters a record g050 left for the next release; it has no ledger entry,
    and the builder's NEXT_RELEASE mark on its record is its parent's, not its own. Proven to fail by injection,
    2026-11-01: with the re-entry branch removed, finalize raised KeyError on the ledger; with the parent's marks
    used for a re-entry group, its read record was listed unread."""
    group = (review.READS_DIR / "group_g050.json").read_text(encoding="utf-8")
    (review.READS_DIR / "group_g050-r1.json").write_text(group, encoding="utf-8")
    (review.REVIEW / "decisions" / "g050-r1.json").write_text(json.dumps(GOOD), encoding="utf-8")
    monkeypatch.setattr(review.build, "UNREAD", {"u": "no text", "p1": review.build.NEXT_RELEASE})
    monkeypatch.setattr(review.build, "reentry_briefs", lambda: {"g050-r1": (["p1"], {})})
    out = review.finalize("g050-r1", "2026-11-01", review.STORED)
    assert "unread" not in out
    # review of 34034bd: a record the re-entry brief leaves unread is named unread in its review
    monkeypatch.setattr(review.build, "reentry_briefs", lambda: {"g050-r1": (["p1", "u"], {"u": "no text, still"})})
    assert review.finalize("g050-r1", "2026-11-01", review.STORED)["unread"] == {"u": "no text, still"}
    assert out["graded_high"]["thm"] == ["proved result", "Theorem 1, proved in Appendix A"]


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


def test_a_sprint15_read_names_sprint15s_prompt(review, monkeypatch):
    """Sprint 15 Task H: g062-r1 was first finalized naming Sprint 14's tag and prompt. A read that carries
    figure_count (Sprint 15's prompt requires it) names Sprint 15's. Proven to fail by injection, 2026-11-01: with
    every local read given Sprint 14's tag, the Sprint 15 group named Sprint 14's prompt."""
    _decide(review, GOOD)
    monkeypatch.setattr(review.build, "local_file", lambda rid: Path(f"{rid}.json"))
    path = review.READS_DIR / "group_g050.json"
    group = json.loads(path.read_text(encoding="utf-8"))
    for p in group["papers"]:
        p["figure_count"] = 0
    path.write_text(json.dumps(group), encoding="utf-8")
    out = review.finalize("g050", "2026-11-01", review.STORED)
    assert (out["tag"], out["reader"]) == (review.S15_TAG, review.S15_READER)
    assert "sprint15_f114_reads" in out["reader"]
    # a group mixing a Sprint 14 and a Sprint 15 local read names each read's own
    group["papers"].append({"record_id": "p2", "assertions": [], "existing": []})
    path.write_text(json.dumps(group), encoding="utf-8")
    out = review.finalize("g050", "2026-11-01", review.STORED)
    assert out["tags"]["p2"] == review.LOCAL_TAG and out["readers"]["p2"] == review.LOCAL_READER
    assert {out["tags"][r] for r in out["tags"] if r != "p2"} == {review.S15_TAG}


def test_a_sprint16_group_names_sprint16s_prompt(review, monkeypatch):
    """Sprint 16 Task F: its reads carry figure_count as Sprint 15's do, so a Sprint 16 group is named by its group.
    Proven to fail by injection, 2026-11-06: with S16_GROUPS ignored in `finalize`, the group named Sprint 15's
    prompt."""
    _decide(review, GOOD)
    monkeypatch.setattr(review.build, "local_file", lambda rid: Path(f"{rid}.json"))
    monkeypatch.setattr(review, "S16_GROUPS", ("g050",))
    path = review.READS_DIR / "group_g050.json"
    group = json.loads(path.read_text(encoding="utf-8"))
    for p in group["papers"]:
        p["figure_count"] = 0
    path.write_text(json.dumps(group), encoding="utf-8")
    out = review.finalize("g050", "2026-11-06", review.STORED)
    assert (out["tag"], out["reader"]) == (review.S16_TAG, review.S16_READER)
    assert "sprint16_f114_reads" in out["reader"]


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


ADDED = {"record_id": "p1", "why": "split from narrow, the team lead's decision",
         "assertion": {"value": "the second half", "anchor": "p.4", "quotes": ["the second half, as quoted"],
                       "result_type": "setup", "claim_type": "positive", "context": "qml", "kind": "shown",
                       "certainty_suggestion": "low"}}
PAPER_TEXT = "the first half, then the second half, as quoted in Section 4"


def test_a_split_is_a_sign_off_add_and_the_read_file_is_never_edited(review, monkeypatch):
    """F142 part 2 (Sprint 17 Task C): Sprint 16 split `he-simulation-scope` (MV Q1 = 3) by editing the reader's
    read file by hand (db2abe3). A split is now a `value_replace` on the old assertion plus an `add` in the sign-off:
    the added assertion is always an item to decide (a LOW suggestion too: fresh-eyes review of 2580ce2), the review
    file carries the table for the applier, and the read file stays as the reader wrote it. Proven red 2026-11-07:
    with `papers` not merging the sign-off (INJECTED), the added item was missing (KeyError); with "add" left out of
    SIGNOFF_TABLES (INJECTED), finalize refused the table; with the held-id check removed (INJECTED), an add under a
    stored id passed; with the "new-added" branch removed (INJECTED), the LOW add was no item."""
    monkeypatch.setattr(review, "plain_text", lambda path: PAPER_TEXT)
    read = (review.READS_DIR / "group_g050.json").read_text(encoding="utf-8")
    so = review.REVIEW / "signoff"
    so.mkdir()
    (so / "g050.json").write_text(json.dumps({"value_replace": {"narrow": "the first half"},
                                              "add": {"narrow-2": ADDED}}), encoding="utf-8")
    assert {i["id"]: i["kind"] for i in review.items("g050", review.STORED)}["narrow-2"] == "new-added"
    _decide(review, GOOD)
    with pytest.raises(ValueError, match=r"no decision for \['narrow-2'\]"):
        review.finalize("g050", "2026-11-07", review.STORED)
    _decide(review, {**GOOD, "narrow-2": {"decision": "high", "basis": "setup", "why": "Section 4 states it"}})
    out = review.finalize("g050", "2026-11-07", review.STORED)
    assert out["add"] == {"narrow-2": ADDED} and out["value_replace"] == {"narrow": "the first half"}
    assert out["graded_high"]["narrow-2"] == ["setup", "Section 4 states it"]
    assert (review.READS_DIR / "group_g050.json").read_text(encoding="utf-8") == read

    for bad, match in (({"st-lo": ADDED}, "already holds"), ({"x": {**ADDED, "record_id": "p9"}}, "not a paper"),
                       ({"x": {**ADDED, "why": " "}}, "no why"),
                       ({"x": {**ADDED, "assertion": {**ADDED["assertion"], "quotes": []}}}, r"missing \['quotes'\]"),
                       ({"x": {**ADDED, "assertion": {**ADDED["assertion"], "result_type": "measurement"}}},
                        "result_type 'measurement' is not one of")):
        (so / "g050.json").write_text(json.dumps({"add": bad}), encoding="utf-8")
        with pytest.raises(ValueError, match=match):
            review.papers("g050")


def test_an_added_assertion_passes_the_readers_own_checks_at_finalize(review, monkeypatch):
    """Fresh-eyes review of 2580ce2: an add was checked only for non-empty fields, so a quote on another page than its
    anchor, or a HIGH suggestion with no basis, passed where a reader's would not. Finalize now runs the reader's
    checks (`sprint13_g_check.assertion_problems` and `page_problems`) on every add. Proven red 2026-11-07: with
    `text_problems` not called (INJECTED), the quote the paper never says passed finalize."""
    monkeypatch.setattr(review, "plain_text", lambda path: PAPER_TEXT)
    _decide(review, {**GOOD, "x": {"decision": "low", "why": "setup, not graded"}})
    so = review.REVIEW / "signoff"
    so.mkdir()
    cases = (({**ADDED["assertion"], "quotes": ["a sentence the paper never says"]}, "not verbatim|not found"),
             ({**ADDED["assertion"], "certainty_suggestion": "high"}, "needs high_basis"))
    for a, match in cases:
        (so / "g050.json").write_text(json.dumps({"add": {"x": {**ADDED, "assertion": a}}}), encoding="utf-8")
        with pytest.raises(ValueError, match=match):
            review.finalize("g050", "2026-11-07", review.STORED)
    (so / "g050.json").write_text(json.dumps({"add": {"x": ADDED}}), encoding="utf-8")
    monkeypatch.setattr(review.additions.reader, "page_problems", lambda tag, a, path, text: [f"{tag}: OFF PAGE"])
    with pytest.raises(ValueError, match="p1/x: OFF PAGE"):
        review.finalize("g050", "2026-11-07", review.STORED)


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


def _store(path: Path, rows: dict[str, tuple[str, str]]) -> Path:
    import sqlite3
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE records (id TEXT PRIMARY KEY, certainty TEXT, updated_reason TEXT)")
    conn.executemany("INSERT INTO records VALUES (?, ?, ?)", [(i, c, n) for i, (c, n) in rows.items()])
    conn.commit()
    conn.close()
    return path


def test_finalize_refuses_a_group_already_applied_unless_a_store_is_named(review, tmp_path, monkeypatch):
    """Sprint 14 retrospective Q3: finalize read the applied grades back as the stored ones after an apply (g079 and
    g094 were re-finalized against a pre-apply copy by hand). Proven to fail by injection, 2026-10-31: with the
    refusal in main removed, the applied store was finalized without a word."""
    _decide(review, GOOD)
    (review.REVIEW / "models.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(review, "REVIEWS_DIR", tmp_path / "reviews")
    (tmp_path / "reviews").mkdir()
    before = {"st-hi": ("high", ""), "st-lo": ("low", ""), "narrow": ("high", "")}
    full_read = f"2026-10-31 (x): {review.FULL_READ_MARK}: confirmed from p1; the paper read whole"
    for name, applied in (("new", {**before, "thm": ("high", "")}), ("noted", {**before, "narrow": ("low", full_read)})):
        monkeypatch.setattr(review, "DB_PATH", _store(tmp_path / f"{name}.db", applied))
        with pytest.raises(SystemExit, match="already applied"):
            review.main(["finalize", "g050", "2026-10-31"])
    pre = _store(tmp_path / "pre.db", before)  # DB_PATH is still an applied store; --store names another
    assert review.main(["finalize", "g050", "2026-10-31", "--store", str(pre)]) == 0
    written = json.loads((tmp_path / "reviews" / "g050.json").read_text(encoding="utf-8"))
    assert written["graded_high"]["narrow"] == ["stated limit", "Section 5 states it"]
    with pytest.raises(SystemExit, match="existing store file"):
        review.main(["finalize", "g050", "2026-10-31", "--store", str(tmp_path / "missing.db")])
    # review of 7b2179f: a new assertion is looked for under its id_fix id, and a dropped one not at all. Proven to
    # fail by injection, 2026-10-31: with applied() reading the raw suggestions, both cases answered wrongly.
    (review.REVIEW / "signoff").mkdir()
    (review.REVIEW / "signoff" / "g050.json").write_text(json.dumps(
        {"id_fix": {"thm": "thm-2"}, "drop": {"sim": "off topic"}}), encoding="utf-8")
    monkeypatch.setattr(review, "DB_PATH", _store(tmp_path / "fixed.db", {**before, "thm-2": ("high", "")}))
    assert review.applied("g050") == ["thm-2"]
    monkeypatch.setattr(review, "DB_PATH", _store(tmp_path / "other.db", {**before, "sim": ("low", ""), "thm": ("low", "")}))
    assert review.applied("g050") == []
