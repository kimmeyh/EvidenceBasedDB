"""F114 cloud readers: the inbox never carries a paper into a commit, and the
checker's --text mode checks quotes against the text a cloud session was given.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "manifests" / "f114_cloud" / "inbox"


def test_the_inbox_placeholders_are_empty():
    """scripts/f114_cloud.py fills the inbox only for one launch and restores
    it; a paper's text left there would be committed (ADR-0005 section 3).
    Proven to fail, 2026-10-26: with a line of text appended to paper.txt,
    the test went red."""
    assert json.loads((INBOX / "brief.json").read_text(encoding="utf-8")) == {}
    text = (INBOX / "paper.txt").read_text(encoding="utf-8")
    assert text.startswith("Placeholder.") and len(text.splitlines()) == 1, "the inbox holds a paper's text"


def test_the_reader_prompt_keeps_the_text_out_of_every_commit():
    """Review of the F114 launcher (2026-10-26): a plain commit takes whatever is staged, and a session given the
    wrong paper read it. The text now arrives by message and is saved outside the repository. Proven to fail,
    2026-10-26: with the commit pathspec removed from the prompt, the test went red; the same with the unpack step
    removed."""
    prompt = (ROOT / "manifests" / "f114_cloud" / "READER_PROMPT.md").read_text(encoding="utf-8")
    assert "python3 scripts/f114_unpack.py RECORD" in prompt
    assert "manifests/f114_cloud/inbox/" not in prompt.split("---", 1)[1]
    assert 'git commit -m "..." -- manifests/f114_cloud/results/RECORD/' in prompt
    assert "git diff --cached --name-only" in prompt


def _unpack(tmp_path: Path, monkeypatch, message: str, rid: str) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    import f114_unpack
    home = tmp_path / "home"
    log = home / ".claude" / "projects" / "-home-user-repo" / "s.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text("\n".join(json.dumps(e) for e in [
        {"type": "user", "message": {"role": "user", "content": "Reply with the one word waiting."}},
        {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": message}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}},
    ]), encoding="utf-8")
    monkeypatch.setattr(f114_unpack.Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr(f114_unpack, "OUT", tmp_path / "out")
    return f114_unpack.main([rid])


def test_unpack_saves_the_text_exactly_as_sent(tmp_path, monkeypatch):
    """The session saves its paper from its own transcript, page breaks included, and only for RECORD. Proven to
    fail, 2026-10-26: with unpack's split on the text marker dropped (the whole message saved as the text), the
    first assertion went red; with the record check removed, the second did."""
    text = "Page one.\fPage two, with a minus sign \u2212 and a line\nbreak."
    brief = {"group": "g043", "records": [{"record_id": "r", "file": "D:\\r.pdf", "stored_assertions": []}]}
    message = f"Read the prompt. RECORD is r.\n=== BRIEF ===\n{json.dumps(brief)}\n=== PAPER TEXT ===\n{text}"
    assert _unpack(tmp_path, monkeypatch, message, "r") == 0
    assert (tmp_path / "out" / "paper.txt").read_text(encoding="utf-8") == text
    assert _unpack(tmp_path / "other", monkeypatch, message, "not-r") == 1


def _check(tmp_path: Path, quote: str) -> subprocess.CompletedProcess:
    paper = tmp_path / "paper.txt"
    paper.write_text("The authors prove that the bound holds for every n at least two.\f", encoding="utf-8")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({"group": "g043", "records": [
        {"record_id": "r", "file": "D:\\nowhere\\r.pdf", "stored_assertions": []}]}), encoding="utf-8")
    entry = {"record_id": "r", "file": "D:\\nowhere\\r.pdf", "read_extent": "full", "not_read": "",
             "bears_on_context": "qml", "existing": [], "assertions": [{
                 "id_suggestion": "a", "value": "The authors prove the bound holds.", "anchor": "p.1",
                 "quotes": [quote], "kind": "shown", "claim_type": "positive", "context": "qml",
                 "certainty_suggestion": "low", "result_type": "theoretical"}]}
    done = tmp_path / "r.json"
    done.write_text(json.dumps({"papers": [entry]}), encoding="utf-8")
    return subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts" / "sprint13_g_check.py"), str(done),
                           str(brief), "--partial", "--text", str(paper)], capture_output=True, text=True)


def test_the_checker_reads_the_given_text_instead_of_the_pdf(tmp_path):
    """A cloud session has the text, not the PDF. Proven to fail, 2026-10-26:
    without --text handling the check reported "file not found" for the
    brief's local path, and a quote missing from the text passed nowhere."""
    ok = _check(tmp_path, "the bound holds for every n at least two")
    assert ok.stdout.strip().endswith("0 problems"), ok.stdout
    bad = _check(tmp_path, "the bound holds for no n at all")
    assert not bad.stdout.strip().endswith("0 problems"), bad.stdout


def test_the_launcher_takes_task_gs_groups_only(tmp_path, monkeypatch):
    """Sprint 14 Task F (review of 1cb63bb): ledger group g330 holds Task C's 4 papers, read locally, and has no
    cloud brief, so records() raised on it and `launch` and `run` crashed. Proven to fail by injection, 2026-10-30:
    with LAST_GROUP removed from records(), it raised FileNotFoundError on g330's brief."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("f114_cloud", ROOT / "scripts" / "f114_cloud.py")
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {g: {} for g in ("g042", "g043", "g329", "g330")}}), encoding="utf-8")
    (tmp_path / "briefs").mkdir()
    for g in ("g043", "g329"):
        (tmp_path / "briefs" / f"{g}.json").write_text(json.dumps({"records": [{"record_id": g}]}), encoding="utf-8")
    monkeypatch.setattr(c, "LEDGER", ledger)
    monkeypatch.setattr(c, "BRIEFS", tmp_path / "briefs")
    assert [g for g, _ in c.records()] == ["g043", "g329"]
