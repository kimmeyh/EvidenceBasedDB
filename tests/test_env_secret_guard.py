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


def test_a_mention_with_the_bypass_token_passes():
    proc = _run("Bash", {"command": "git commit -m 'ignore .env' # allow_env_mention"})
    assert proc.returncode == 0, proc.stderr


def test_malformed_payload_fails_open():
    proc = subprocess.run([sys.executable, str(HOOK)], input="{{{", capture_output=True, text=True)
    assert proc.returncode == 0


def test_git_ignores_the_secret_file():
    proc = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT)
    assert proc.returncode == 0, ".gitignore must name .env so the key is never staged"
