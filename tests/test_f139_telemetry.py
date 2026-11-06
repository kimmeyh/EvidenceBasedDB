"""F139 (Sprint 16 Task B): the per-group telemetry file and the page-render cache. Neither opens the store or a
real PDF here."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(ROOT / "scripts"))


def test_an_unmeasured_field_is_unknown_never_zero(tmp_path):
    """Proven to fail by injection, 2026-11-06: with `_sum` returning 0 for no values, the unmeasured reviewer and
    quote-check fields read 0; with a step's count summed when any part was unknown, the total read a number."""
    t = _load("read_telemetry")
    brief = {"records": [{"record_id": "a", "file": "a.pdf"}, {"record_id": "b", "file": "b.html"}]}
    t.start("g9", brief, tmp_path, pages=lambda f: 12)
    t.agent("g9", "reader", "task1", 300000, 40.0, folder=tmp_path)
    total = t.totals(t.load("g9", tmp_path))
    assert total["papers"] == 2
    assert total["pages"] == "unknown"  # the HTML page has no page count, so the sum is not known
    assert total["reader_tokens"] == 300000
    assert total["reviewer_tokens"] == "unknown" and total["reviewer_minutes"] == "unknown"
    assert total["quote_checks"] == "unknown" and total["applies"] == "unknown"
    assert t.per_page(total)["reader_tokens"] == "unknown"


def test_a_repeated_notice_replaces_and_steps_add_up(tmp_path):
    """A resumed agent's notice repeats its total tokens, so it replaces the first; each step's counts add.
    Proven to fail by injection, 2026-11-06: with the agents keyed by a new entry per notice, the tokens doubled;
    with `step` writing a file for a group that had none, the Sprint 15 group gained one."""
    t = _load("read_telemetry")
    t.start("g9", {"records": [{"record_id": "a", "file": "a.pdf"}]}, tmp_path, pages=lambda f: 10)
    t.agent("g9", "reader", "task1", 200000, 30.0, folder=tmp_path)
    t.agent("g9", "reader", "task1", 250000, 45.0, "resumed once", folder=tmp_path)
    t.agent("g9", "reviewer", "task2", 100000, 12.0, folder=tmp_path)
    t.step("g9", "check", tmp_path, quote_checks=40, cache_misses=2)
    t.step("g9", "check", tmp_path, quote_checks=40, cache_misses=0)
    t.step("g9", "apply", tmp_path, quote_checks=40, assertions_written=38)
    total = t.totals(t.load("g9", tmp_path))
    assert (total["reader_tokens"], total["reader_minutes"], total["reviewer_tokens"]) == (250000, 45.0, 100000)
    assert (total["quote_checks"], total["cache_misses"], total["assertions_written"], total["applies"]) == (
        120, 2, 38, 1)
    assert t.per_page(total)["reader_tokens"] == 25000.0
    assert t.step("g001", "check", tmp_path, quote_checks=5) is None
    assert not (tmp_path / "g001.json").exists()
    with pytest.raises(ValueError):
        t.step("g9", "read again", tmp_path)
    with pytest.raises(ValueError):
        t.step("g9", "check", tmp_path, tokens=5)


def test_only_live_writes_count_as_written(tmp_path):
    """A trial writes to a copy, and a second apply (or another group's) writes nothing to this group: neither is
    written or an apply. Sprint 16 Task F, g333: the report showed 1030 written for 515 and 2 applies for 1. Proven
    to fail by injection, 2026-11-06: with totals summing every step's assertions_written and counting every apply
    step, it gave 1030 and 2."""
    t = _load("read_telemetry")
    t.start("g9", {"records": [{"record_id": "a", "file": "a.pdf"}]}, tmp_path, pages=lambda f: 10)
    t.step("g9", "trial", tmp_path, quote_checks=515, assertions_written=515)
    t.step("g9", "apply", tmp_path, quote_checks=515, assertions_written=515)
    t.step("g9", "trial", tmp_path, quote_checks=0, assertions_written=0)
    t.step("g9", "apply", tmp_path, quote_checks=0, assertions_written=0)
    total = t.totals(t.load("g9", tmp_path))
    assert (total["quote_checks"], total["assertions_written"], total["applies"]) == (1030, 515, 1)


def test_the_check_and_the_apply_record_their_steps(tmp_path, monkeypatch):
    """The reader check with --telemetry adds its quote checks and cache misses to the group named by its brief; the
    applier adds each group's checked assertions, as assertions written at a trial or an apply. Proven to fail by
    injection, 2026-11-06: with the checker's count taken before the papers were checked, quote_checks read 0; with
    the applier recording writes at a dry run, the dry run step held assertions_written."""
    from store import quotes
    monkeypatch.setattr(quotes, "CACHE_MISSES", type(quotes.CACHE_MISSES)())  # a fresh count, whatever ran before
    t = _load("read_telemetry")
    monkeypatch.setenv(t.FOLDER_ENV, str(tmp_path / "telemetry"))
    t.start("g9", {"records": []}, pages=lambda f: 1)
    check = _load("sprint13_g_check")
    text = tmp_path / "text.txt"
    text.write_text("the accuracy rises with the qubit count as Figure 3 shows.", encoding="utf-8")
    brief = tmp_path / "g9.json"
    brief.write_text(json.dumps({"records": [{"record_id": "r", "file": "x.pdf", "stored_assertions": []}]}),
                     encoding="utf-8")
    data = tmp_path / "group_g9.json"
    data.write_text(json.dumps({"papers": [{"record_id": "r", "file": "x.pdf", "read_extent": "full",
                                            "bears_on_context": True, "assertions": [
                                                {"id_suggestion": "n1", "value": "the accuracy rises",
                                                 "anchor": "p.1", "quotes": ["the accuracy rises with the qubit"]},
                                                {"id_suggestion": "n2", "value": "Figure 3",
                                                 "anchor": "p.1", "quotes": ["as Figure 3 shows"]}]}]}),
                    encoding="utf-8")
    check.main([str(data), str(brief), "--text", str(text), "--telemetry"])
    apply = _load("full_read_apply")
    apply.CHECKED_BY_GROUP.update({"g9": 3, "g001": 2})
    assert apply.record_telemetry("dry run") == ["g9"]  # g001 has no telemetry file, so is not measured
    assert apply.record_telemetry("apply") == ["g9"]
    steps = t.load("g9")["steps"]
    assert [(s["step"], s["quote_checks"], s.get("assertions_written")) for s in steps] == [
        ("check", 2, None), ("dry run", 3, None), ("apply", 3, 3)]
    assert steps[0]["cache_misses"] == 0  # the text came from a file, not an extraction


def test_the_sprint15_baseline_counts_each_agent_once(tmp_path):
    """The baseline keeps a resumed agent's last notice (its total), splits an agent that names two groups, leaves out
    a group no Sprint 15 agent read, and marks what Sprint 15 never counted "unknown". Proven to fail by injection,
    2026-11-06: with the first notice kept, g120's reader tokens read 100; with the split removed, both groups held
    the shared reviewer's whole 60; with the exclusion removed, g104 was in the baseline. Fresh-eyes review of Task
    B: a background command's notice before an agent's on one line lent the agent's usage to the command's id, so
    the agent counted twice; proven to fail by injection, 2026-11-06, with the whole-line pattern restored (g121's
    reader read 100). A failed agent's notice has no usage: counted beside the sum, never as 0."""
    t = _load("read_telemetry")

    def notice(task, name, tokens, ms, outcome="finished"):
        usage = f"<usage><subagent_tokens>{tokens}</subagent_tokens><duration_ms>{ms}</duration_ms></usage>"
        return (f"<task-notification><task-id>{task}</task-id><summary>Agent \"{name}\" {outcome}</summary>"
                f"{usage if tokens is not None else ''}</task-notification>")

    command = ("<task-notification><task-id>b1</task-id><summary>Background command \"x\" completed</summary>"
               "</task-notification>")
    transcript = tmp_path / "session.jsonl"
    transcript.write_text("\n".join(json.dumps({"content": c}) for c in [
        notice("a1", "Reader g120", 100, 60000), notice("a1", "Reader g120", 400, 120000),
        notice("a2", "Reviewer g120, g121", 60, 600000), command + notice("a3", "Reader g121", 50, 60000),
        notice("a3", "Reader g121", 50, 60000),  # the same notice again, on a line of its own
        notice("a5", "Reader g121", None, None, "failed"),
        notice("a4", "F114 local reader g104", 999, 60000)]), encoding="utf-8")
    work = tmp_path / "work"
    for g in ("g120", "g121", "g104"):
        (work / f"tmp_{g}").mkdir(parents=True)
        (work / f"tmp_{g}" / "p1.png").write_bytes(b"png")
        (work / "briefs").mkdir(exist_ok=True)
        (work / "briefs" / f"{g}.json").write_text(json.dumps({"records": [{"record_id": "r", "file": "r.pdf"}]}),
                                                  encoding="utf-8")
    found = t.baseline(transcript, work, pages=lambda f: 10)
    g = found["groups"]
    assert sorted(g) == ["g120", "g121"] and found[t.EXCLUDED] == ["g104"]
    assert (g["g120"]["reader_tokens"], g["g120"]["reader_minutes"]) == (400, 2.0)
    assert g["g120"]["reviewer_tokens"] == 30 and g["g121"]["reviewer_tokens"] == 30
    assert g["g120"]["images_rendered"] == 1 and g["g120"]["papers"] == [{"record_id": "r", "pages": 10}]
    assert g["g121"]["quote_checks"] == "unknown" and g["g121"]["assertions_written"] == "unknown"
    assert (g["g121"]["reader_tokens"], g["g121"]["reader_agents_without_usage"]) == (50, 1)
    assert g["g120"]["reader_agents_without_usage"] == 0


def test_a_page_is_rendered_once(tmp_path, monkeypatch):
    """Render once: the second ask for the same page, file and resolution is served from the cache; another
    resolution or a changed file renders again. Proven to fail by injection, 2026-11-06: with the cache lookup
    removed, the second ask rendered again; with the resolution left out of the key, the 220 dpi ask got the 100 dpi
    image."""
    r = _load("render_page")
    monkeypatch.setenv("EBDB_TEXT_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(r, "_tool", lambda: "tool")
    runs = []

    def fake_run(cmd, **kwargs):
        runs.append(cmd)
        Path(f"{cmd[-1]}.png").write_bytes(f"page {cmd[cmd.index('-f') + 1]} at {cmd[2]}".encode())

    monkeypatch.setattr(r.subprocess, "run", fake_run)
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF one")
    first = r.render(str(pdf), 3)
    assert r.render(str(pdf), 3) == first and len(runs) == 1
    assert first.read_bytes() == b"page 3 at 100"
    assert r.render(str(pdf), 3, 220).read_bytes() == b"page 3 at 220" and len(runs) == 2
    pdf.write_bytes(b"%PDF two")
    assert r.render(str(pdf), 3) != first and len(runs) == 3
    assert not list((tmp_path / "cache" / "pages").glob("tmp*"))  # no temporary folder left behind
