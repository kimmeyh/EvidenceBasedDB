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


# ---- Sprint 5 retrospective improvement 2 (2026-09-25): no .py rewriting through python-in-shell

SPRINT5_BREAKER = (
    "cd /repo && cat > /tmp/mf3.py <<'PYEOF'\n"
    "p='scripts/sprint5_bibliography_manifest.py'\n"
    "s=open(p,encoding='utf-8').read()\n"
    "s=s.replace('a', 'b')\n"
    "open(p,'w',encoding='utf-8',newline='\n').write(s)\n"
    "PYEOF\n"
    "python /tmp/mf3.py"
)


def test_blocks_python_rewriting_a_py_file_regression():
    """The shape that broke three files in Sprint 5. Proven to fail by
    injection: with _writes_python_source returning False, this command
    passes (exit 0) and the assert goes red."""
    proc = run(SPRINT5_BREAKER)
    assert proc.returncode == 2, proc.stderr
    assert "rewriting a .py file" in proc.stderr


@pytest.mark.parametrize("command", [
    # a python heredoc editing a prose file (CHANGELOG) stays allowed
    "python - <<'PYEOF'\np='CHANGELOG.md'\ns=open(p,encoding='utf-8').read()\nopen(p,'w',encoding='utf-8').write(s)\nPYEOF",
    # running a script, or the test suite, writes nothing through a string
    "python scripts/intake.py --manifest m.json --apply",
    "python -m pytest -q tests/test_ingest.py",
    # reading a .py file is fine
    "python -c \"print(open('scripts/view.py').read()[:10])\"",
])
def test_allows_non_code_writes_and_plain_runs(command):
    assert run(command).returncode == 0


def test_python_writes_code_bypass_token():
    assert run(SPRINT5_BREAKER + " # allow_python_writes_code").returncode == 0


# ---- Sprint 8 retrospective I5 (2026-10-13): no shell edits of repository code files

@pytest.mark.parametrize("command", [
    "sed -i 's/old/new/' scripts/sprint8_f60_manifest_check.py",  # the Sprint 8 shape
    "cd /d/Data/Harold/github/EvidenceBasedDB && sed -i.bak -e 's/a/b/' store/recheck.py",
    "perl -pi -e 's/a/b/' tests/test_recheck.py",
    "git show HEAD:store/ingest.py > store/ingest.py",
    "echo 'x = 1' >> scripts/view.py",
    "printf 'x' | tee store/schema.sql",
    "cat > scripts/new.py <<'EOF'\nprint(1)\nEOF",
    "Set-Content -Path scripts/view.py -Value 'x'",
    "sed -i 's/a/b/' D:/Data/Harold/github/EvidenceBasedDB/store/recheck.py",
    # Fresh-eyes review, 2026-10-13: shapes that escaped the first version
    "cat <<< 'a'\nsed -i 's/a/b/' store/x.py",
    "git ls-files store | xargs sed -i 's/a/b/' store/recheck.py",
    "bash -c \"sed -i 's/a/b/' store/x.py\"",
    "env sed -i 's/a/b/' store/x.py",
    "perl -0pi -e 's/a/b/' store/x.py",
    "echo x 1> store/x.py",
    "echo x &> store/x.py",
    "cd /d/Data/Harold/github/EvidenceBasedDB && sed -i 's/a/b/' store/x.py",
    "Set-Content -Value 'x' -Path scripts/view.py",
    "Out-File -Encoding utf8 -FilePath store/a.py",
    "Set-Content scripts/view.py 'x'",
])
def test_blocks_a_shell_edit_of_a_repository_code_file(command):
    """Proven to fail by injection, 2026-10-13: with _shell_edits_code
    returning [], every case passed (exit 0) and this test went red. The
    fresh-eyes review's cases (here and in the allowed list below) each
    failed against the hook as committed in 6a260ce, run the same day."""
    proc = run(command)
    assert proc.returncode == 2, command
    assert "editing a repository code file" in proc.stderr


@pytest.mark.parametrize("command", [
    "sed -n 1,40p scripts/view.py",                       # reading
    "grep -n def store/recheck.py > /tmp/defs.txt",         # redirect onto a text file
    "python -m pytest -q > C:/Users/kimme/AppData/Local/Temp/pt.log 2>&1",
    "cat > /tmp/scratch.py <<'EOF'\nprint(1)\nEOF",        # a scratch file outside the repository
    "git commit -q -F - <<'EOF'\nfix: no more sed -i on scripts/x.py; > store/y.py\nEOF",  # a message is data
    "sed -i 's/a/b/' CHANGELOG.md",                        # prose, not code
    # Fresh-eyes review, 2026-10-13: everyday commands the first version blocked
    "Get-Content a.txt | Out-File log.txt; python scripts/view.py",
    "Out-File -FilePath log.txt -InputObject (python store/recheck.py)",
    "Set-Content -Path notes.txt -Value 'see store/x.py'",
    'git commit -m "hook: blocks echo > store/x.py"',
    "cd C:/Users/kimme/AppData/Local/Temp && sed -i 's/a/b/' scratch.py",
    "python -m pytest -q 2>&1 | tee pt.log",
])
def test_allows_reads_scratch_files_and_messages(command):
    proc = run(command)
    assert proc.returncode == 0, f"{command}\n{proc.stderr}"


def test_shell_code_edit_bypass_token():
    assert run("git show HEAD:store/ingest.py > store/ingest.py  # allow_shell_code_edit").returncode == 0
