"""Behavioral tests for .claude/hooks/block_shell_metachar_expansion.py.

Sprint 9 retrospective I5: when the blocked expansion is ${PIPESTATUS[...]},
the block message leads with the prescribed exit-code form. Runs the real
hook as a subprocess with a JSON payload (never a shell pipe).

Proven to fail by injection, 2026-10-17: with the `if "PIPESTATUS" in cmd:`
block removed from the hook, test_pipestatus_block_leads_with_the_exit_code_form
went red (the message did not contain "rc=$?"); restored, green.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_shell_metachar_expansion.py"


def _run(command: str) -> subprocess.CompletedProcess:
    payload = {"tool_input": {"command": command}}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True)


def test_pipestatus_block_leads_with_the_exit_code_form():
    proc = _run('python -m pytest -q | tail -3; rc=${PIPESTATUS[0]}; echo $rc')
    assert proc.returncode == 2
    assert proc.stderr.startswith("[BLOCKED] ${PIPESTATUS")
    assert "rc=$?" in proc.stderr


def test_other_expansions_keep_the_general_message_only():
    proc = _run('python -c "print(\'${HOME}\')"')
    assert proc.returncode == 2
    assert "PIPESTATUS" not in proc.stderr
    assert "FIX, in order of preference" in proc.stderr


def test_the_prescribed_form_is_allowed():
    proc = _run("python -m pytest -q > log.txt 2>&1; rc=$?; tail -3 log.txt; echo rc=$rc")
    assert proc.returncode == 0, proc.stderr
