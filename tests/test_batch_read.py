"""The four rules of scripts/batch_read.py (Sprint 17 Task B, F144), each from the team lead's brief of 2026-11-07:

1. "never send a record again once its result is saved" (and never while its batch is in flight);
2. "refuse to submit a batch whose estimated cost would take the total spent past a cap (default $95), and stop
   before 2026-11-18";
3. "read the key only ... never print it, and never write it to a file, log or commit";
4. results land in the pipeline's shape: the raw result, the reader group file in the work folder and its repository
   copy, the state entry; "a failing result is kept and flagged, never dropped".

No network, no store and no key: a fake client stands in for the API, and every path points into tmp_path.

Proven red 2026-11-07, each by its own INJECTED edit to scripts/batch_read.py, then restored and green:
- `unsendable` returning `in_flight(state)` only: test_a_saved_result_is_never_sent_again failed;
- the `today >= STOP` test in `refusal` changed to `today > STOP`: test_nothing_is_sent_on_or_after_the_stop_date
  failed; the cap test changed to `spent + estimate > cap + 100`: test_a_batch_past_the_cap_is_refused failed;
- `redact(str(ex), key)` changed to `str(ex)`: test_the_key_never_reaches_the_output_or_a_file failed;
- the raw-result write removed from `collect`: test_results_land_in_the_pipeline_shape_and_failures_are_kept failed.

The fresh-eyes review of 2026-11-07 added four guards, each proven red the same day by its own INJECTED edit:
- `refusal` given the forecast in place of the worst case: test_the_cap_is_tested_at_the_worst_case_not_the_forecast;
- the `pending` test in `refusal` turned off: test_an_interrupted_send_blocks_the_next_and_a_refused_send_leaves_nothing;
- `too_big` emptied: test_a_request_over_the_size_limit_is_refused;
- the already-saved test in `collect` turned off: test_a_retried_collection_costs_each_result_once (spent 2.0, not 1.0).

Team lead, Q3 = 1 (2026-11-07): an errored or expired paper is sent again, its first result kept. Proven red the same
day: `unsendable` counting every saved result (INJECTED), and the `earlier` append removed (INJECTED), each failed
test_an_errored_or_expired_paper_is_sent_again_and_its_first_result_kept.

Pilot, 2026-11-07: every page is attached, figure pages first. Proven red the same day: with the loop over the
figure pages only (INJECTED), test_every_page_is_attached_including_drawings_with_no_caption failed (5 of 23 pages).
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
KEY = "sk-ant-test-NOT-A-REAL-KEY-0123456789"


def _module():
    spec = importlib.util.spec_from_file_location("batch_read", ROOT / "scripts" / "batch_read.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeBatches:
    def __init__(self, fail: str = ""):
        self.created, self.fail = [], fail

    def create(self, betas, requests):
        if self.fail:
            raise RuntimeError(self.fail)
        self.created.append([r["custom_id"] for r in requests])
        return SimpleNamespace(id=f"msgbatch_{len(self.created)}")


def fake_factory(batches):
    return lambda key, workspace: SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(batches=batches)))


@pytest.fixture
def bm(tmp_path, monkeypatch):
    mod = _module()
    for name, path in (("WORK", tmp_path / "work"), ("LOCAL", tmp_path / "local"), ("REPO_READS", tmp_path / "reads"),
                       ("REPO_BRIEFS", tmp_path / "briefs"), ("LEDGER", tmp_path / "ledger.json"),
                       ("SLICE", tmp_path / "slice.json")):
        monkeypatch.setattr(mod, name, path)
    mod.LEDGER.write_text(json.dumps({"rule": "", "groups": {"g334": {"records": []}}}), encoding="utf-8")
    mod.SLICE.write_text(json.dumps({"slice": [{"record_id": r} for r in ("a-2020-x", "b-2021-y", "c-2022-z")]}),
                         encoding="utf-8")
    monkeypatch.setattr(mod, "connect", lambda path: contextlib.nullcontext(None))
    monkeypatch.setattr(mod, "_load", lambda name, file: SimpleNamespace(stored_assertions=lambda conn, rid: []))
    monkeypatch.setattr(mod, "paper_message", lambda g, brief, pdf: (
        [{"type": "text", "text": "x"}], {"pages": 10, "images": 2, "image_bytes": 1, "not_attached": [],
                                          "ocr_pages": [], "chars": 35_000}))
    monkeypatch.setattr(mod, "instructions", lambda g: "instructions")
    monkeypatch.setattr(mod, "api_key", lambda: (KEY, None))
    files = {r: {"path": str(tmp_path / f"{r}.pdf"), "why": "exists"} for r in ("a-2020-x", "b-2021-y", "c-2022-z")}
    mod.save_state({"batches": {}, "results": {}, "files": files, "spent": 0.0})
    return mod


def test_a_saved_result_is_never_sent_again(bm):
    state = bm.load_state()
    state["results"]["a-2020-x"] = {"group": "g335", "type": "succeeded"}
    state["batches"]["msgbatch_old"] = {"records": ["b-2021-y"], "groups": {"b-2021-y": "g336"}, "estimate": 0.1,
                                        "collected": False}
    bm.save_state(state)
    batches = FakeBatches()
    assert bm.submit(["--n", "5", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 0
    assert len(batches.created) == 1 and len(batches.created[0]) == 1  # c only
    assert bm.load_state()["batches"]["msgbatch_1"]["records"] == ["c-2022-z"]
    assert bm.submit(["--n", "5", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 0
    assert len(batches.created) == 1, "a record in flight was sent again"


def test_an_errored_or_expired_paper_is_sent_again_and_its_first_result_kept(bm):
    """Team lead, 2026-11-07, Q3 = 1: an errored or expired request is not billed and holds no read, so it is sent
    again; the first result stays in the state (`earlier`) and on disk."""
    state = bm.load_state()
    state["results"] = {"a-2020-x": {"group": "g335", "batch": "msgbatch_0", "type": "expired"},
                        "b-2021-y": {"group": "g336", "batch": "msgbatch_0", "type": "succeeded"}}
    bm.save_state(state)
    batches = FakeBatches()
    assert bm.submit(["--n", "5", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 0
    assert bm.load_state()["batches"]["msgbatch_1"]["records"] == ["a-2020-x", "c-2022-z"]
    (bm.WORK / "raw").mkdir(parents=True, exist_ok=True)
    (bm.WORK / "raw" / "a-2020-x.json").write_text("{}", encoding="utf-8")
    state = bm.load_state()
    result = {"custom_id": state["batches"]["msgbatch_1"]["groups"]["a-2020-x"],
              "result": {"type": "errored", "error": {"type": "api_error"}}}
    bm.collect(state, "msgbatch_1", [result])
    after = bm.load_state()
    assert after["earlier"][0]["type"] == "expired" and after["results"]["a-2020-x"]["type"] == "errored"
    assert (bm.WORK / "raw" / "a-2020-x.json").read_text(encoding="utf-8") == "{}"
    assert (bm.WORK / "raw" / "a-2020-x.msgbatch_1.json").is_file()


def test_nothing_is_sent_on_or_after_the_stop_date(bm, capsys):
    batches = FakeBatches()
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 18), fake_factory(batches)) == 1
    assert batches.created == [] and "REFUSED" in capsys.readouterr().out
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 17), fake_factory(batches)) == 0
    assert len(batches.created) == 1


def test_a_batch_past_the_cap_is_refused(bm, capsys):
    state = bm.load_state()
    state["spent"] = 94.95
    bm.save_state(state)
    batches = FakeBatches()
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 1
    assert batches.created == [] and "past the cap $95.00" in capsys.readouterr().out
    state["spent"] = 1.0
    bm.save_state(state)
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 0
    assert len(batches.created) == 1


def test_the_cap_is_tested_at_the_worst_case_not_the_forecast(bm, capsys):
    """Fresh-eyes review 2026-11-07: one request may write max_tokens of output (adaptive thinking is output), about
    $1.50, many times the forecast. At $94 spent, the forecast ($0.17) fits under $95; the worst case ($1.53) does
    not."""
    state = bm.load_state()
    state["spent"] = 94.0
    bm.save_state(state)
    batches = FakeBatches()
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 1
    assert batches.created == [] and "at worst" in capsys.readouterr().out


def test_an_interrupted_send_blocks_the_next_and_a_refused_send_leaves_nothing(bm, capsys):
    ledger_before = bm.LEDGER.read_text(encoding="utf-8")
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(FakeBatches(fail="400 bad"))) == 1
    after = bm.load_state()
    assert "pending" not in after and after["batches"] == {}
    assert bm.LEDGER.read_text(encoding="utf-8") == ledger_before, "a refused send must not hold ledger groups"
    after["pending"] = {"records": ["a-2020-x"], "groups": {"a-2020-x": "g335"}, "since": "x"}
    bm.save_state(after)
    batches = FakeBatches()
    assert bm.submit(["--n", "5", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 1
    assert batches.created == [] and "interrupted" in capsys.readouterr().out


def test_a_request_over_the_size_limit_is_refused(bm, monkeypatch, capsys):
    monkeypatch.setattr(bm, "MAX_REQUEST_BYTES", 100)
    batches = FakeBatches()
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 1
    assert batches.created == [] and "over 100 bytes" in capsys.readouterr().out


def test_a_retried_collection_costs_each_result_once(bm, monkeypatch):
    monkeypatch.setattr(bm, "check", lambda g: "passed: 0 problems")
    state = bm.load_state()
    state["batches"]["msgbatch_9"] = {"records": ["a-2020-x"], "groups": {"a-2020-x": "g335"}, "estimate": 1.0,
                                      "collected": False}
    bm.save_state(state)
    result = {"custom_id": "g335", "result": {"type": "succeeded", "message": {
        "content": [{"type": "text", "text": "{}"}], "usage": {"input_tokens": 1_000_000, "output_tokens": 0},
        "stop_reason": "end_turn"}}}

    def broken():
        yield result
        raise ConnectionError("the stream broke")

    with pytest.raises(ConnectionError):
        bm.collect(state, "msgbatch_9", broken())
    state = bm.load_state()
    bm.collect(state, "msgbatch_9", [result])
    after = bm.load_state()
    assert after["spent"] == pytest.approx(1.0) and after["batches"]["msgbatch_9"]["collected"] is True


@pytest.mark.live_store
def test_every_page_is_attached_including_drawings_with_no_caption():
    """Pilot, 2026-11-07: Kadowaki 1998's figures are vector drawings on pages 16 to 23, with no embedded image and no
    caption on the page, and a figure-pages-only rule attached none of them (the read came back partial). Every page
    is attached now, up to the request limits. Local: it renders a PDF in Papers."""
    mod = _module()
    pdf = mod.PAPERS / "1998_Kadowaki_Quantum-annealing-in-the-transverse-Ising-model.pdf"
    content, facts = mod.paper_message("g999", {"group": "g999", "records": []}, str(pdf))
    assert facts["pages"] == 23 and facts["images"] == 23 and facts["not_attached"] == [], facts
    labels = [b["text"] for b in content if b["type"] == "text" and b["text"].startswith("=== IMAGE OF PAGE")]
    assert "=== IMAGE OF PAGE 16 ===" in labels and len(labels) == 23


def test_the_key_never_reaches_the_output_or_a_file(bm, capsys, tmp_path):
    batches = FakeBatches(fail=f"401 invalid x-api-key {KEY}")
    assert bm.submit(["--n", "1", "--apply"], date(2026, 11, 7), fake_factory(batches)) == 1
    out = capsys.readouterr().out
    assert "FAILED to send" in out and KEY not in out and "<key>" in out
    assert not [p for p in tmp_path.rglob("*") if p.is_file() and KEY in p.read_text(encoding="utf-8", errors="replace")]


def test_results_land_in_the_pipeline_shape_and_failures_are_kept(bm, monkeypatch):
    monkeypatch.setattr(bm, "check", lambda g: "passed: 0 problems")
    state = bm.load_state()
    state["batches"]["msgbatch_9"] = {"records": ["a-2020-x", "b-2021-y", "c-2022-z"],
                                      "groups": {"a-2020-x": "g335", "b-2021-y": "g336", "c-2022-z": "g337"},
                                      "estimate": 1.0, "collected": False}
    bm.save_state(state)
    reply = {"papers": [{"record_id": "a-2020-x"}]}
    usage = {"input_tokens": 100_000, "output_tokens": 20_000}
    results = [
        {"custom_id": "g335", "result": {"type": "succeeded", "message": {
            "content": [{"type": "text", "text": json.dumps(reply)}], "usage": usage, "stop_reason": "end_turn"}}},
        {"custom_id": "g336", "result": {"type": "succeeded", "message": {
            "content": [{"type": "text", "text": "I could not finish."}], "usage": usage, "stop_reason": "end_turn"}}},
        {"custom_id": "g337", "result": {"type": "errored", "error": {"type": "invalid_request_error"}}},
    ]
    bm.collect(state, "msgbatch_9", results)
    after = bm.load_state()
    for rid in ("a-2020-x", "b-2021-y", "c-2022-z"):
        assert (bm.WORK / "raw" / f"{rid}.json").is_file(), rid
        assert rid in after["results"], f"{rid} dropped"
    for path in bm.group_files("g335"):
        assert json.loads(path.read_text(encoding="utf-8")) == reply
    assert after["results"]["a-2020-x"]["check"] == "passed: 0 problems"
    assert after["results"]["b-2021-y"]["check"].startswith("FLAGGED")
    assert after["results"]["c-2022-z"]["check"].startswith("FLAGGED")
    assert after["batches"]["msgbatch_9"]["collected"] is True
    assert after["spent"] == pytest.approx(2 * (0.1 + 0.1))


SELF_CHECK = ("List every digit string in its value", "Never name a label by its number in a value",
              "every number read by eye has \"about\"", "Each quote is on a page its anchor names",
              "a ligature (\"ﬁ\") stays a ligature")


def test_the_batch_prompt_makes_the_reader_check_each_assertion_before_it_replies():
    """Team lead, q2 (2026-11-07): "can't this be written into the prompt to check itself before returning?" The
    pilot's 49 check problems in 5 papers came from five causes; the prompt's last section names a pass for each.
    Proven red the same day: with the label rule's heading changed (INJECTED), this test named it."""
    text = (ROOT / "manifests" / "sprint17_f144_batch" / "READER_PROMPT.md").read_text(encoding="utf-8")
    section = " ".join(text[text.index("## Check before you finish"):].split())
    missing = [rule for rule in SELF_CHECK if rule not in section]
    assert missing == [], f"the batch prompt's self-check lacks: {missing}"
