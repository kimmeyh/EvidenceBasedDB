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
    """Review of the F114 launcher (2026-10-26): `git checkout -- inbox` restores the index copy, so a staged
    text survived it; a plain commit takes whatever is staged; and a session given the wrong inbox read the wrong
    paper. Proven to fail, 2026-10-26: with the prompt's restore line put back to `git checkout --`, the test went
    red; the same with the commit pathspec removed."""
    prompt = (ROOT / "manifests" / "f114_cloud" / "READER_PROMPT.md").read_text(encoding="utf-8")
    assert "git restore --source=HEAD --staged --worktree -- manifests/f114_cloud/inbox/" in prompt
    assert "git checkout -- manifests/f114_cloud/inbox/" not in prompt
    assert 'git commit -m "..." -- manifests/f114_cloud/results/RECORD/' in prompt
    assert "git diff --cached --name-only" in prompt and "whose `record_id` is RECORD" in prompt


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
