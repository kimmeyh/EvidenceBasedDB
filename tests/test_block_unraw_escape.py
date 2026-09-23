"""The unraw-escape hook blocks raw Windows paths and nothing else
(Sprint 4 retrospective improvement 5).

Real subprocess against the real hook. The three false-positive cases are
the exact commands this hook blocked during Sprint 4; the true-positive
case is the defect it exists for.

Proven by injection 2026-09-22: restoring the old `[A-Za-z]:\\[A-Za-z]`
pattern (no leading word-boundary guard) turns
test_allows_prose_with_a_colon_before_an_escape red for both cases, and
removing the DRIVE_PATH check entirely turns
test_blocks_a_raw_windows_path_in_a_python_string red.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_unraw_escape.py"


def run(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, encoding="utf-8")


def test_blocks_a_raw_windows_path_in_a_python_string():
    """The defect the hook exists for: Python reads \\D as an invalid escape."""
    proc = run('python -c "p = \'D:\\Data\\Harold\\x.txt\'"')
    assert proc.returncode == 2
    assert "unescaped Windows path" in proc.stderr


@pytest.mark.parametrize("command,why", [
    ('python -c "print(\'CITATION.cff:\\n\' + body)"',
     "a filename ending in a colon before a newline escape: matched as f:\\n"),
    ("python - <<'PY'\ns = '        if found:\\n'\nPY",
     "generated Python source text: matched as d:\\n"),
])
def test_allows_prose_with_a_colon_before_an_escape(command, why):
    """Blocked in Sprint 4 although neither command contains a Windows path.

    The old pattern matched any letter-colon-backslash-letter, so the last
    letter of a word before `:\\n` looked like a drive letter.
    """
    proc = run(command)
    assert proc.returncode == 0, f"{why}\n{proc.stderr}"


@pytest.mark.parametrize("command", [
    "python -c \"p = r'D:\\Data\\Harold\\x.txt'\"",
    "python -c \"p = 'D:/Data/Harold/x.txt'\"",
    'python -c "p = \'D:\\\\Data\\\\Harold\\\\x.txt\'"',
])
def test_allows_every_correct_form(command):
    assert run(command).returncode == 0, run(command).stderr


def test_allows_a_command_that_does_not_run_python():
    assert run('powershell -File "C:\\Users\\kimme\\scripts\\footer.ps1"').returncode == 0


def test_bypass_token_allows_a_deliberate_escape():
    proc = run('python -c "p = \'D:\\Data\\x.txt\'" allow_unraw_escape')
    assert proc.returncode == 0


def test_malformed_payload_fails_open():
    proc = subprocess.run([sys.executable, str(HOOK)], input="not json",
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
