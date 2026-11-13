"""Tests for .claude/hooks/block_env_secret_reads.py and the `.gitignore`
rule for `.env` (Sprint 17, F144, plan Q1: the team lead keeps the API key in
`.env` at the repository root).

The hook is run as a subprocess with synthetic PreToolUse payloads, exactly
as Claude Code invokes it.

Proven red 2026-11-07: with `return f"{tool} on the secret file ..."` changed
to `return None` (an INJECTED edit), `test_reading_the_secret_file_is_blocked`
failed; with the `.env` line removed from `.gitignore` (INJECTED),
`test_git_ignores_the_secret_file` failed; with NAME's lookbehind removed
(INJECTED), `test_lookalike_names_are_not_blocked` failed on
`settings.env` (the first version claimed `.venv` would catch it; it cannot,
since `.venv` holds no `.env`, and the injection passed, so `settings.env`
was added). Each restored and green.

Fresh-eyes review of the hook, 2026-11-07, found three gaps, each now
covered and proven red the same day: with `re.IGNORECASE` removed and the
`.lower()` in `_is_env_file` removed (INJECTED), the `.ENV` and `.Env` cases
failed; with the LOADER check removed (INJECTED), the three loader cases
failed; with `and TEXT_COMMANDS.match(command)` removed (INJECTED), the two
`allow_env_mention` cases on `cat` failed. Each restored and green.

Security review the same day: a token honored on `git commit` still passed
`git commit ... && cat .env`, so the token is gone; the trailing-dot shell
form and `dotenv run` and `python -m dotenv` are now blocked. Proven red: with
a token check `if "allow_env_mention" in command: return None` put back
(INJECTED), the two cases that carry the token failed; with the trailing-dot part removed from NAME
(INJECTED), `type .env.` failed. Each restored and green.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_env_secret_reads.py"
SECRET = str(ROOT / ".env")


def _run(tool: str, args: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps({"tool_name": tool, "tool_input": args}),
                          capture_output=True, text=True)


@pytest.mark.parametrize("tool,args", [
    ("Read", {"file_path": SECRET}),
    ("Read", {"file_path": ".env"}),
    ("Edit", {"file_path": SECRET, "old_string": "a", "new_string": "b"}),
    ("Write", {"file_path": SECRET, "content": "x"}),
    ("Grep", {"pattern": "KEY", "path": SECRET}),
    ("Grep", {"pattern": "KEY", "glob": ".env"}),
    ("Bash", {"command": "cat .env"}),
    ("Bash", {"command": "git add -f .env"}),
    ("PowerShell", {"command": "Get-Content D:\\Data\\Harold\\github\\EvidenceBasedDB\\.env"}),
    # Fresh-eyes review 2026-11-07: Windows opens the same file for each of these.
    ("Read", {"file_path": str(ROOT / ".ENV")}),
    ("Read", {"file_path": str(ROOT / ".env.")}),
    ("Read", {"file_path": str(ROOT / ".env::$DATA")}),
    ("MultiEdit", {"file_path": SECRET, "edits": []}),
    ("Bash", {"command": "cat .Env"}),
    # The loaders find the file without naming it, and print the key.
    ("Bash", {"command": 'python -c "from dotenv import dotenv_values; print(dotenv_values())"'}),
    ("PowerShell", {"command": "python -c 'import dotenv; dotenv.load_dotenv(); import os'"}),
    ("Bash", {"command": "dotenv list"}),
    ("Bash", {"command": "dotenv run -- printenv"}),
    ("Bash", {"command": "python -X utf8 -m dotenv list"}),
    ("Bash", {"command": "type .env."}),
    # No bypass token: the old one passed these (fresh-eyes and security reviews, 2026-11-07).
    ("Bash", {"command": "cat .env # allow_env_mention"}),
    ("Bash", {"command": "git commit -m 'x' && cat .env # allow_env_mention"}),
    ("Bash", {"command": "git commit -m 'ignore .env'"}),
])
def test_reading_the_secret_file_is_blocked(tool, args):
    proc = _run(tool, args)
    assert proc.returncode == 2, (tool, args, proc.stderr)
    assert "block_env_secret_reads" in proc.stderr


@pytest.mark.parametrize("tool,args", [
    ("Bash", {"command": "ls .venv ocr-venv"}),
    ("Bash", {"command": "uv pip install python-dotenv"}),
    ("Bash", {"command": "cat .env.example .envrc"}),
    ("Bash", {"command": "cat settings.env"}),
    ("Read", {"file_path": str(ROOT / "scripts" / "batch_read.py")}),
    ("Glob", {"pattern": "*.env"}),
    ("Bash", {"command": "python scripts/batch_read.py --dry-run"}),
])
def test_lookalike_names_are_not_blocked(tool, args):
    proc = _run(tool, args)
    assert proc.returncode == 0, (tool, args, proc.stderr)


@pytest.mark.parametrize("command", [
    "git commit -F ../commit_message.txt",
    "gh pr edit 174 --body-file ../pr_body.md",
    "uv pip install --system python-dotenv==1.1.0",
    "python scripts/batch_read.py status",
])
def test_a_mention_by_a_message_file_passes(command):
    """The way to name the file in a commit or a PR body: the text is in a file, never in the command."""
    proc = _run("Bash", {"command": command})
    assert proc.returncode == 0, proc.stderr


def test_the_block_message_names_no_bypass():
    """The first message told a blocked agent to add a token, on any command (fresh-eyes review 2026-11-07)."""
    proc = _run("Bash", {"command": "cat .env"})
    assert proc.returncode == 2 and "allow_" not in proc.stderr and "-F" in proc.stderr, proc.stderr


def test_malformed_payload_fails_open():
    proc = subprocess.run([sys.executable, str(HOOK)], input="{{{", capture_output=True, text=True)
    assert proc.returncode == 0


def test_git_ignores_the_secret_file():
    proc = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT)
    assert proc.returncode == 0, ".gitignore must name .env so the key is never staged"
