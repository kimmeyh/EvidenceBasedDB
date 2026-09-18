"""Tests for .claude/hooks/block_ask_user_question.py (Sprint 2 retrospective
improvement 2).

Guard-discipline standard (CLAUDE.md): a guard must be proven to fail before
it is trusted to pass. This runs the hook script itself as a subprocess with
synthetic PreToolUse payloads, exactly as Claude Code would invoke it, rather
than asserting on the hook's source text.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_ask_user_question.py"


def _run_hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_ask_user_question_is_blocked():
    proc = _run_hook({"tool_name": "AskUserQuestion", "tool_input": {"questions": []}})
    assert proc.returncode == 2
    assert "BLOCKED" in proc.stderr
    assert "AskUserQuestion" in proc.stderr


def test_other_tools_are_not_blocked():
    for tool_name in ("Read", "Write", "Edit", "Bash", "Task"):
        proc = _run_hook({"tool_name": tool_name, "tool_input": {}})
        assert proc.returncode == 0, f"{tool_name} was unexpectedly blocked: {proc.stderr}"


def test_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not valid json {{{",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0


def test_empty_payload_fails_open():
    proc = _run_hook({})
    assert proc.returncode == 0
