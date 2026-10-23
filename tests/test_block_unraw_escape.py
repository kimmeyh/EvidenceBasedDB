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
    # Edge-case pass, 2026-10-13
    "echo x >| store/x.py",
    "python scripts/view.py 2> store/x.py",
    "exec 3> scripts/x.py",
    "printf x | tee -a log.txt store/x.py",
    "printf x | tee --append store/x.py",
    "dd if=/dev/zero of=store/x.py count=1",
    "cp /tmp/x.py store/recheck.py",
    "mv C:/Users/kimme/x.py scripts/view.py",
    "Copy-Item C:/tmp/x.py -Destination store/recheck.py",
    "awk -i inplace '{print}' store/x.py",
    "ruby -pi -e 'gsub(/a/, \"b\")' store/x.py",
    "sed -i'' 's/a/b/' store/x.py",
    "find store -name '*.py' -exec sed -i 's/a/b/' {} +",
    "git ls-files '*.py' | xargs sed -i 's/a/b/'",
    "sed -i 's/a/b/' .github/workflows/ci.yml",
    "sed -i 's/a/b/' pytest.ini",
    "sed -i 's/a/b/' STORE/X.PY",
    "[IO.File]::WriteAllText('store/x.py', 'x')",
    "[System.IO.File]::AppendAllLines('scripts/x.py', $lines)",
    "New-Item store/x.py -ItemType File -Value 'x'",
    "Set-Content -Path 'store/x.py' -Value 'x'",
    "echo x > 'store/x.py'",
    "cd /tmp && cd /d/Data/Harold/github/EvidenceBasedDB && sed -i 's/a/b/' store/x.py",
    "git commit -m 'allow_shell_code_edit is named here' && sed -i 's/a/b/' store/x.py",
    "sed -i 's/a/b/;s/c/d/' store/x.py",
    # PR #77 review, 2026-10-13
    "bash <<EOF\nsed -i s/a/b/ store/recheck.py\nEOF",
    "truncate -s0 store/x.py",
])
def test_blocks_a_shell_edit_of_a_repository_code_file(command):
    """Proven to fail by injection, 2026-10-13: with _shell_edits_code
    returning [], every case passed (exit 0) and this test went red. The
    fresh-eyes review's cases (here and in the allowed list below) each
    failed against the hook as committed in 6a260ce, run the same day. Of
    the edge-case pass's cases (both lists), 26 failed against the hook as
    committed in 91f508b; the rest guard behavior it already had."""
    proc = run(command)
    assert proc.returncode == 2, command
    assert "editing a repository code file" in proc.stderr


@pytest.mark.parametrize("command", [
    "sed -n 1,40p scripts/view.py",                       # reading
    "grep -n def store/recheck.py > /tmp/defs.txt",         # redirect onto a text file
    "python -m pytest -q > C:/Users/kimme/AppData/Local/Temp/pt.log 2>&1",
    "cat > /tmp/scratch.py <<'EOF'\nprint(1)\nEOF",        # a scratch file outside the repository
    "git commit -q -F - <<'EOF'\nfix: no more sed -i on scripts/x.py; > store/y.py\nEOF",  # a message is data
    # Fresh-eyes review, 2026-10-13: everyday commands the first version blocked
    "Get-Content a.txt | Out-File log.txt; python scripts/view.py",
    "Out-File -FilePath log.txt -InputObject (python store/recheck.py)",
    "Set-Content -Path notes.txt -Value 'see store/x.py'",
    'git commit -m "hook: blocks echo > store/x.py"',
    "cd C:/Users/kimme/AppData/Local/Temp && sed -i 's/a/b/' scratch.py",
    "python -m pytest -q 2>&1 | tee pt.log",
    # Edge-case pass, 2026-10-13
    "python -m pytest -q > pt.log 2>&1; echo exit=$?",
    "cp store/recheck.py C:/Users/kimme/AppData/Local/Temp/x.py",  # copying code out
    "cp CHANGELOG.md /tmp/c.md",
    "perl -Mstrict -ne 'print if /def /' store/recheck.py",
    "awk '{print $1}' store/recheck.py",
    "sed -n 's/a/b/p' store/recheck.py",
    "grep -c 'x > y' store/recheck.py",
    "python -c \"print(1 if 2 > 1 else 0)\" scripts/view.py",
    "gh api repos/o/r/pulls/1/comments/2/replies -f body='Fixed: sed -i on store/x.py is now blocked; > store/y.py too'",
    "git commit -q -F - <<'EOF'\nfix: tee store/x.py and cp a.py store/b.py are blocked\nEOF",
    "git commit -m @'\nfix: Set-Content store/x.py is blocked\n'@",
    "# sed -i 's/a/b/' store/x.py\necho done",
    "git checkout -- store/recheck.py",
    "x => store/recheck.py",
])
def test_allows_reads_scratch_files_and_messages(command):
    proc = run(command)
    assert proc.returncode == 0, f"{command}\n{proc.stderr}"


@pytest.mark.parametrize("command", [
    "py -c \"p = 'D:\\Data\\new.txt'\"",
    "python - <<'PYEOF'\nopen('store/schema.sql','w').write('x')\nPYEOF",
])
def test_the_python_checks_cover_the_launcher_and_sql(command):
    """PR #77 review: the `py` launcher was not read as python, and a python
    write onto a .sql file was not read as a code write. Proven to fail,
    2026-10-13: both commands passed (exit 0) against the hook as committed
    in 301ea4c."""
    assert run(command).returncode == 2, command


@pytest.mark.parametrize("command", [
    "sed -n 1,5p store/recheck.py; grep -i foo README.md",
    "sed -n 221,260p .claude/hooks/block_unraw_escape.py; echo ---; grep -n -i def store/recheck.py | head",
    "sed -n 1,5p store/recheck.py && perl -i -pe 's/a/b/' /tmp/notes.txt",  # outside: I4 blocks a repo file
    "awk '{print}' store/recheck.py | grep -i x",
    # Task A review, 2026-10-18: still blocked after 021d2a8
    'bash -c "sed -n 1p store/x.py" | grep -i foo',
    'bash -c "sed -n 1,5p store/x.py"; grep -i y z',
    "sed -n /don\\'t/p store/x.py | grep -i y",
    # Third security review: a path found inside an editor's or copy's own
    # text was placed against the `cd`s by its offset in that text, not on
    # the line; after a `cd` out of the repository these are scratch files
    "cd /d/Data/Harold/github/EvidenceBasedDB && cd /tmp && sed -i s/a/b/ x.py",
    "cd /d/Data/Harold/github/EvidenceBasedDB && cd /tmp && cp a.txt b.py",
    "cd /d/Data/Harold/github/EvidenceBasedDB && cd /tmp && echo x | tee b.py",
])
def test_a_read_followed_by_another_commands_i_flag_is_allowed(command):
    """F81 (Sprint 10 Task A): the in-place flag search ran past `;`, `&&`
    and `|`, so a later command's `-i` made a read of a code file look like
    `sed -i`. Reproduced live at planning, 2026-10-18. Proven to fail by
    injection, 2026-10-18: with _own_command returning `rest` whole, the
    first three cases were blocked (exit 2). The awk case passed even then
    (awk needs `inplace` to count); it guards that rule against the cut."""
    proc = run(command)
    assert proc.returncode == 0, f"{command}\n{proc.stderr}"


@pytest.mark.parametrize("command", [
    "sed -n 1p a.txt; sed -i 's/a/b/' store/x.py",
    "grep -i x README.md && sed -i 's/a/b/' store/x.py",
    "sed -i 's/a/b/; s/c/d/' store/x.py",
    "sed -i 's|a|b|' store/x.py",
    "perl -pi -e 's/a/b/ && 1' store/x.py",
    # Task A review, 2026-10-18 (fresh-eyes and security review): each
    # passed against 021d2a8, cut before its file
    'sed -i "s/\\"/;/" store/x.py',
    "sed -i s/a\\;b/c/ store/x.py",
    "sed -i s/a/\\&/ store/x.py",
    "sed -i s/a/b/ 2>&1 store/x.py",
    "perl -pi -e s/a/b/ 2>&1 store/x.py",
    "sed -i s/a/$(echo b|tr b c)/ store/x.py",
    "sed -i s/a/`echo b|tr b c`/ store/x.py",
    # A shape the cut does not model (process substitution) is caught by
    # the fail-closed search of the whole line
    "sed -i s/a/b/ <(echo|cat) store/x.py",
    # Second security review: a quote closed mid-word continues the word
    "bash -c \"sed \"'-i s/a/b/ store/x.py'",
    # Third security review: quotes inside the file name or the awk keyword
    "sed -i s/a/b/ store/x'.py'",
    'sed -i s/a/b/ "store/x".py',
    "awk -i in\"place\" '{}' store/x.py",
])
def test_an_in_place_edit_after_or_with_a_separator_is_still_blocked(command):
    """F81's other half: the cut at a separator must not free a real edit.
    A separator inside the quoted script does not cut the command before
    its file. Proven to fail by injection, 2026-10-18: with _own_command
    cutting at every separator, quoted or not, the third to fifth cases
    passed (exit 0). A second: with the tool search back to one
    non-overlapping `finditer`, the first case passed, because the first
    `sed`'s text ran to the end of the line and hid the second `sed`.
    Task A review, 2026-10-18: the seven review cases each passed (exit 0)
    against the hook as committed in 021d2a8, and the three read cases
    added to the allowed test were each blocked there (run with a copy of
    that version). With the fail-closed whole-line search removed, the
    process-substitution case passed. Restored. Known cost of failing
    closed: an in-place edit of a text file followed on the same line by a
    command naming a code file (`sed -i ... a.txt; cat store/x.py`) is
    blocked; the bypass token covers it. Second security review, the same
    day: `bash -c "sed "'-i ...'` passed against 10f7741 (a quote closed
    mid-word was taken as the end of the command, and the quote before
    `-i` hid the flag). Proven by two injections: with either the
    word-end check or the quote strip before the flag search removed, that
    case passed. Restored. Third security review: the three quote-in-name
    cases passed against 6690c39 and against the hook before Task A (an
    older gap); every check now reads the text with quotes removed. That
    change broke the existing `cd /tmp && cd <repository> && sed -i`
    case, which exposed an older offset bug in keep(); fixed, and the
    three `cd`-out cases in the allowed test were each blocked at
    6690c39."""
    proc = run(command)
    assert proc.returncode == 2, command


# ---- Sprint 11 retrospective I4 (2026-10-23): the Edit tool for every in-place edit,
# and a search pattern that names sed is data

@pytest.mark.parametrize("command", [
    "sed -i 's/a/b/' CHANGELOG.md",  # allowed before I4: prose
    "sed -i 's/a/b/' .claude/sprint_status.json",
    "perl -pi -e 's/a/b/' docs/INTAKE_WORKFLOW.md",
    "sed -i.bak 's/a/b/' .gitignore",
    "grep -n x a.txt; sed -i 's/a/b/' docs/x.md",
    # a quote that runs is still a command
    'bash -c "sed -i s/a/b/ docs/x.md"',
    'grep x "$(sed -i s/a/b/ store/x.py)"',
    'xargs "sed" -i s/a/b/ store/x.py',
])
def test_an_in_place_edit_of_any_repository_file_is_blocked(command):
    """Proven to fail by injection, 2026-10-23: with ANY_ARG back to the
    code-only CODE_ARG, the six non-code cases passed (exit 0)."""
    proc = run(command)
    assert proc.returncode == 2, command
    assert "Edit tool" in proc.stderr


@pytest.mark.parametrize("command", [
    # the command blocked live on 2026-10-23, a read of two sibling files
    'grep -n -i -B2 -A6 "sed -i" docs/x.md | head -60; diff <(sed -n 1,400p a.py) '
    "/d/Data/Harold/github/EvidenceBasedDB/.claude/hooks/block_unraw_escape.py | head -40",
    'grep -rn "sed -i" .claude/hooks/block_unraw_escape.py',
    'rg "sed -i s/a/b/" store/x.py',
    'git log --grep "sed -i" -- store/x.py',
    'git grep -n "perl -pi" store/x.py',
    "cd C:/Users/kimme/AppData/Local/Temp && sed -i 's/a/b/' notes.md",  # outside the repository
])
def test_a_search_pattern_naming_sed_is_not_an_edit(command):
    """Proven to fail by injection, 2026-10-23: with _searched_pattern()
    returning False, the first five cases were blocked (exit 2). The first
    is the shape blocked live that day."""
    proc = run(command)
    assert proc.returncode == 0, f"{command}\n{proc.stderr}"


def test_shell_code_edit_bypass_token():
    assert run("git show HEAD:store/ingest.py > store/ingest.py  # allow_shell_code_edit").returncode == 0
