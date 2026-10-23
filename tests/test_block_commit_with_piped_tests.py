"""The commit-with-piped-tests hook (Sprint 4 retrospective improvement 1).

Real subprocess against the real hook, one payload per case, as
tests/test_mutation_lock.py does.

Proven by injection 2026-09-22: with the EATS_EXIT_CODE check disabled the
allow-cases went red (everything was blocked); with the GIT_COMMIT check
disabled test_allows_piped_tests_without_a_commit went red.
"""
from __future__ import annotations

import json
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_commit_with_piped_tests.py"

THE_REAL_MISTAKE = (
    "cd /d/repo && python -m pytest -q --no-header | tail -1 && git add -A && "
    "git commit -q -m 'Sprint 4 Task X'"
)


def run(command: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    # Outside any repository by default, so a verdict this desk recorded
    # (the second check) cannot change the pipe check's results.
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command},
                          "cwd": str(cwd or Path(tempfile.gettempdir()))})
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


@pytest.mark.parametrize("command", [
    "git add -A && git commit -m x && pytest -q | tail -3",
    "git commit -m msg && pytest -q | tail -1",
])
def test_allows_a_commit_that_precedes_the_piped_test_run(command):
    """ORDER MATTERS. A commit already made cannot be gated on a pipeline
    that runs after it: "commit, then run the suite and read the tail" is an
    ordinary workflow. Blocking it was a false positive (Copilot/Claude
    review of PR #30, 2026-09-22) of exactly the over-match class this
    sprint had just fixed in block_unraw_escape.py."""
    proc = run(command)
    assert proc.returncode == 0, proc.stderr


@pytest.mark.parametrize("n", [5, 19, 20, 25, 40, 100])
def test_a_long_command_does_not_escape_the_gate(n):
    """Offset drift: the first version estimated each segment's position with
    `len(seg) + 2`, correct for `&&` but one too many for `;` and a newline.
    The error accumulated until the ordering comparison inverted and the hook
    ALLOWED the exact mistake it exists to stop -- measured 2026-09-23, blocked
    at 19 preceding lines and allowed at 20. A 20-line Bash block is an
    ordinary command here, so this was live.

    A false negative in a guard is worse than the false positive it replaced:
    the false positive was visible and arguable; this was silent.
    """
    command = "\n".join(["git status --short"] * n + ["pytest -q | tail -5", "git commit -m x"])
    assert run(command).returncode == 2, f"escaped the gate with {n} preceding lines"


@pytest.mark.parametrize("n", [25, 60])
def test_many_semicolons_do_not_escape_the_gate(n):
    command = " ; ".join(["echo a"] * n) + " ; pytest -q | tail && git commit -m x"
    assert run(command).returncode == 2


@pytest.mark.parametrize("n", [5, 30])
def test_a_long_command_that_commits_first_is_still_allowed(n):
    """The fix must not reintroduce the false positive at length."""
    command = "\n".join(["git status --short"] * n + ["git commit -m x", "pytest -q | tail -5"])
    assert run(command).returncode == 0


# ------------------------------------------------------------------ Sprint 11 I2: the recorded verdict

def _runner():
    spec = importlib.util.spec_from_file_location("run_suite", ROOT / "scripts" / "run_suite.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def repo(tmp_path):
    """A small repository with the runner in it, as the hook finds it."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "scripts").mkdir()
    shutil.copyfile(ROOT / "scripts" / "run_suite.py", tmp_path / "scripts" / "run_suite.py")
    # As the real .gitignore: the hook's import of the runner writes __pycache__.
    (tmp_path / ".gitignore").write_text(".claude/suite_verdict.json\nignored.txt\n__pycache__/\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    (tmp_path / ".claude").mkdir()
    return tmp_path


def _record(repo: Path, verdict: str, tree: str, tree_after: str | None = None) -> None:
    (repo / ".claude" / "suite_verdict.json").write_text(json.dumps(
        {"verdict": verdict, "rc": 0 if verdict == "PASSED" else 1, "tree": tree, "tree_after": tree_after or tree,
         "summary": "1 failed, 9 passed", "finished": "2026-10-23T10:00:00"}), encoding="utf-8")


def test_the_tree_id_sees_untracked_files_ignores_ignored_ones_and_leaves_the_index_alone(repo):
    tree = _runner().working_tree(repo)
    (repo / "ignored.txt").write_text("x", encoding="utf-8")
    assert _runner().working_tree(repo) == tree
    (repo / "new_test.py").write_text("y = 2\n", encoding="utf-8")
    assert _runner().working_tree(repo) != tree
    staged = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--name-only"], capture_output=True,
                            text=True, check=True).stdout
    assert staged == ""


def test_the_verdict_comes_from_the_exit_code_and_a_still_tree():
    v = _runner().verdict
    assert (v(0, "t1", "t1"), v(1, "t1", "t1"), v(0, "t1", "t2"), v(1, "t1", "t2")) == (
        "PASSED", "FAILED", "INVALID", "INVALID")


@pytest.mark.parametrize("verdict", ["FAILED", "INVALID"])
def test_a_commit_of_the_tree_a_red_or_invalid_run_checked_is_blocked(repo, verdict):
    """Proven to fail by injection, 2026-10-23: with _red_verdict() returning
    None, both cases were allowed and went red."""
    _record(repo, verdict, _runner().working_tree(repo))
    result = run("git add -A && git commit -m x", cwd=repo)
    assert result.returncode == 2
    assert f"suite verdict is {verdict}" in result.stderr


def test_an_invalid_run_blocks_its_tree_after_the_run_too(repo):
    """Proven to fail by the same injection, 2026-10-23."""
    _record(repo, "INVALID", "0" * 40, _runner().working_tree(repo))
    assert run("git commit -m x", cwd=repo).returncode == 2


@pytest.mark.parametrize("case", ["passed", "another tree", "no verdict", "bypass", "no commit"])
def test_the_verdict_check_allows_everything_else(repo, case):
    tree = _runner().working_tree(repo)
    command = "git commit -m x"
    if case == "passed":
        _record(repo, "PASSED", tree)
    elif case == "another tree":
        _record(repo, "FAILED", tree)
        (repo / "a.py").write_text("x = 2  # the fix\n", encoding="utf-8")
    elif case == "bypass":
        _record(repo, "FAILED", tree)
        command += "  # allow_red_suite_commit"
    elif case == "no commit":
        _record(repo, "FAILED", tree)
        command = "git status --short"
    assert run(command, cwd=repo).returncode == 0
