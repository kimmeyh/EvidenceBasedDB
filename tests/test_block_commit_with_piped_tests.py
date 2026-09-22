"""The commit-with-piped-tests hook (Sprint 4 retrospective improvement 1).

Real subprocess against the real hook, one payload per case, as
tests/test_mutation_lock.py does.

Proven by injection 2026-09-22: with the EATS_EXIT_CODE check disabled the
allow-cases went red (everything was blocked); with the GIT_COMMIT check
disabled test_allows_piped_tests_without_a_commit went red.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_commit_with_piped_tests.py"

THE_REAL_MISTAKE = (
    "cd /d/repo && python -m pytest -q --no-header | tail -1 && git add -A && "
    "git commit -q -m 'Sprint 4 Task X'"
)


def run(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, encoding="utf-8")


def test_blocks_the_exact_command_that_committed_a_red_suite():
    proc = run(THE_REAL_MISTAKE)
    assert proc.returncode == 2
    assert "exit code a pipe discarded" in proc.stderr
    assert "pytest -q > /tmp/suite.txt" in proc.stderr, "the message must show the fix"


@pytest.mark.parametrize("command", [
    "pytest -q | tail -1 && git commit -m x",
    "python -m pytest tests/ | grep -v PASS && git add -A && git commit -m x",
    "python3.12 -m pytest -q 2>&1 | head -5 && git commit -am x",
    "npm test | tail && git commit -m x",
])
def test_blocks_every_shape_of_the_same_mistake(command):
    assert run(command).returncode == 2


@pytest.mark.parametrize("command", [
    # The two correct forms.
    "pytest -q > /tmp/s.txt 2>&1; rc=$?; tail -1 /tmp/s.txt; test $rc -eq 0 && git commit -m x",
    "python -m pytest -q && git add -A && git commit -m x",
    # A test run with no commit: not this hook's business.
    "python -m pytest -q | tail -1",
    # A commit with no test run at all.
    "git add -A && git commit -m 'docs: fix a typo'",
    # `||` is a fallback, not a pipe: the left side's status is not discarded.
    "python -m pytest -q || echo failed; git commit -m x",
    # The pipe is BEFORE the test runner, so the runner's own status survives.
    "cat manifest.txt | head -3; python -m pytest -q && git commit -m x",
])
def test_allows_commands_whose_exit_code_survives(command):
    proc = run(command)
    assert proc.returncode == 0, proc.stderr


def test_allows_piped_tests_without_a_commit():
    assert run("python -m pytest -q | tail -1 && echo done").returncode == 0


def test_a_commit_message_mentioning_the_pattern_is_not_a_match():
    """Quoted text and heredoc bodies are stripped before matching, so a
    commit message describing this very defect does not trip the hook."""
    command = (
        "git commit -q -F - <<'EOF'\n"
        "Fix the CI gate\n\n"
        "A command of the form `pytest -q | tail -1 && git commit` discards the\n"
        "runner's exit code and commits a red suite.\n"
        "EOF"
    )
    proc = run(command)
    assert proc.returncode == 0, proc.stderr


def test_bypass_token_allows_it():
    assert run(THE_REAL_MISTAKE + " allow_piped_test_commit").returncode == 0


def test_malformed_payload_fails_open():
    proc = subprocess.run([sys.executable, str(HOOK)], input="not json",
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
