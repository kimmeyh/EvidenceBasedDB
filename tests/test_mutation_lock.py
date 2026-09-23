"""Behavioral tests for the F17 mutation-lock pair (Sprint 4 Task I):
.claude/hooks/mutation_lock.py (the CLI) and
.claude/hooks/block_commit_during_mutation.py (the PreToolUse gate).

Every gate case runs the real hook as a subprocess with a programmatically
built JSON payload (QUALITY_STANDARDS.md amendment 2026-09-16: never a
shell pipe), against a scratch repository in tmp_path via repo_override.
The lock file under test is written BY THE TEST (fresh, stale by
timestamp, dead pid, corrupt), so the gate's staleness rules are exercised
directly rather than through the CLI; the CLI has its own cases. Nothing
here touches this repository's own .claude/mutation.lock.

WHAT THESE TESTS WOULD NOT CATCH: the Windows branch of pid_alive (these
run on POSIX; on Windows the ctypes path is exercised only by live use),
and a mutation committed WITHOUT the lock having been taken -- the lock is
advisory, and the discipline of taking it before an injection is still a
convention.

Verified by injection, 2026-09-19: inserting `return 0` as the first
statement of main() in block_commit_during_mutation.py turned 8 of 22 tests
red (re-run after the CLI ordering test was added): the four block-direction
gate cases
(test_gate_blocks_a_commit_while_a_fresh_lock_is_held,
test_gate_blocks_a_fresh_lock_bound_to_a_live_pid,
test_gate_keeps_a_lock_just_inside_the_age_limit,
test_cli_take_writes_the_lock_the_gate_then_blocks_on and
test_cli_take_with_pid_binds_the_lock_to_that_process; returncode 0 != 2)
AND the three stale-removal cases (by timestamp, by dead pid, corrupt),
which assert the stderr warning and `not lock.exists()`: an allow that
leaves the stale file in place is a switched-off gate, not a working one,
and the assertions tell the two apart. Restoring the file (diff against
the backup empty) returned the module to 22 passed. The CLI ordering test
has its own injection record in its docstring.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / ".claude" / "hooks" / "block_commit_during_mutation.py"
CLI = ROOT / ".claude" / "hooks" / "mutation_lock.py"

COMMIT = 'git commit -m "restore guard after injection"'


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".claude").mkdir(parents=True)
    return repo


def _lock(repo: Path) -> Path:
    return repo / ".claude" / "mutation.lock"


def _now_iso(delta: timedelta = timedelta()) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat(timespec="seconds")


def _write_lock(repo: Path, taken: str, pid, reason: str = "test") -> Path:
    path = _lock(repo)
    path.write_text(json.dumps({"taken": taken, "pid": pid, "reason": reason}), encoding="utf-8")
    return path


def _dead_pid() -> int:
    """A pid that belonged to a process which has already exited."""
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def _gate(repo: Path, command: str) -> subprocess.CompletedProcess:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "repo_override": str(repo)}
    return subprocess.run(
        [sys.executable, str(GATE)], input=json.dumps(payload), capture_output=True, text=True
    )


def _cli(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args, "--repo", str(repo)], capture_output=True, text=True
    )


# ---- the gate -------------------------------------------------------------

def test_gate_allows_a_commit_when_no_lock_exists(tmp_path):
    proc = _gate(_repo(tmp_path), COMMIT)
    assert proc.returncode == 0 and proc.stderr == ""


def test_gate_blocks_a_commit_while_a_fresh_lock_is_held(tmp_path):
    """A lock the CLI would write: fresh timestamp, null pid (age-only)."""
    repo = _repo(tmp_path)
    lock = _write_lock(repo, _now_iso(), None, ".claude/hooks/block_ask_user_question.py injection")
    proc = _gate(repo, COMMIT)
    assert proc.returncode == 2
    assert "mutation lock is held" in proc.stderr
    assert "block_ask_user_question.py injection" in proc.stderr
    assert "mutation_lock.py release" in proc.stderr
    assert lock.exists(), "a live lock must not be removed by the gate"


def test_gate_blocks_a_fresh_lock_bound_to_a_live_pid(tmp_path):
    repo = _repo(tmp_path)
    _write_lock(repo, _now_iso(), os.getpid())
    assert _gate(repo, COMMIT).returncode == 2


def test_gate_removes_a_stale_lock_by_timestamp_and_allows(tmp_path):
    repo = _repo(tmp_path)
    lock = _write_lock(repo, _now_iso(-timedelta(hours=4, minutes=1)), os.getpid())
    proc = _gate(repo, COMMIT)
    assert proc.returncode == 0
    assert "stale mutation lock" in proc.stderr and "old" in proc.stderr
    assert not lock.exists()


def test_gate_removes_a_stale_lock_by_dead_pid_and_allows(tmp_path):
    repo = _repo(tmp_path)
    lock = _write_lock(repo, _now_iso(), _dead_pid())
    proc = _gate(repo, COMMIT)
    assert proc.returncode == 0
    assert "is not alive" in proc.stderr
    assert not lock.exists()


def test_gate_removes_a_corrupt_lock_and_allows(tmp_path):
    repo = _repo(tmp_path)
    lock = _lock(repo)
    lock.write_text("not json", encoding="utf-8")
    proc = _gate(repo, COMMIT)
    assert proc.returncode == 0
    assert "cannot be parsed" in proc.stderr
    assert not lock.exists()


def test_gate_keeps_a_lock_just_inside_the_age_limit(tmp_path):
    repo = _repo(tmp_path)
    lock = _write_lock(repo, _now_iso(-timedelta(hours=3, minutes=50)), None)
    assert _gate(repo, COMMIT).returncode == 2
    assert lock.exists()


@pytest.mark.parametrize("command", [
    "git status",
    "python -m pytest -q",
    'echo "git commit later"',
    "cat <<'EOF'\ngit commit -m x\nEOF",
])
def test_gate_ignores_commands_that_are_not_a_commit(tmp_path, command):
    repo = _repo(tmp_path)
    _write_lock(repo, _now_iso(), None)
    proc = _gate(repo, command)
    assert proc.returncode == 0, f"{command!r} was blocked: {proc.stderr}"


def test_gate_bypass_token_allows_the_commit(tmp_path):
    repo = _repo(tmp_path)
    _write_lock(repo, _now_iso(), None)
    assert _gate(repo, COMMIT + " # allow_commit_during_mutation").returncode == 0


def test_gate_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(GATE)], input="not valid json {{{", capture_output=True, text=True
    )
    assert proc.returncode == 0


# ---- the CLI --------------------------------------------------------------

def test_cli_take_writes_the_lock_the_gate_then_blocks_on(tmp_path):
    """End to end: a CLI-taken lock (a subprocess that has exited) must still
    block, which is why the CLI writes a null pid rather than its own."""
    repo = _repo(tmp_path)
    proc = _cli(repo, "take", ".claude/hooks/block_ask_user_question.py", "injection")
    assert proc.returncode == 0, proc.stderr
    record = json.loads(_lock(repo).read_text(encoding="utf-8"))
    assert record["reason"] == ".claude/hooks/block_ask_user_question.py injection"
    assert record["pid"] is None
    datetime.fromisoformat(record["taken"])
    assert _gate(repo, COMMIT).returncode == 2


def test_cli_take_with_pid_binds_the_lock_to_that_process(tmp_path):
    repo = _repo(tmp_path)
    assert _cli(repo, "take", "bound", "--pid", str(os.getpid())).returncode == 0
    assert json.loads(_lock(repo).read_text(encoding="utf-8"))["pid"] == os.getpid()
    assert _gate(repo, COMMIT).returncode == 2


def test_cli_take_accepts_options_before_the_reason(tmp_path):
    """`take --repo <dir> some reason` must work, not only `take some reason
    --repo <dir>`. Coordinator live-fire finding, 2026-09-19: with
    parse_args, argparse consumed an empty nargs="*" reason before --repo
    and then rejected the trailing words with exit 2. The _cli helper above
    appends --repo LAST, which is why the other CLI tests never saw it.

    Verified by injection, 2026-09-19: switching mutation_lock.py back to
    parser.parse_args(argv) fails this test (exit 2, "unrecognized
    arguments: some reason", no lock written); restoring
    parse_intermixed_args passes it.
    """
    repo = _repo(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(CLI), "take", "--repo", str(repo), "some", "reason"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert _lock(repo).exists()
    assert json.loads(_lock(repo).read_text(encoding="utf-8"))["reason"] == "some reason"


def test_cli_take_refuses_a_second_take_while_held(tmp_path):
    repo = _repo(tmp_path)
    assert _cli(repo, "take", "first").returncode == 0
    proc = _cli(repo, "take", "second")
    assert proc.returncode == 1
    assert "already held" in proc.stderr
    assert json.loads(_lock(repo).read_text(encoding="utf-8"))["reason"] == "first"


def test_cli_take_requires_a_reason(tmp_path):
    repo = _repo(tmp_path)
    assert _cli(repo, "take").returncode == 2
    assert not _lock(repo).exists()


def test_cli_release_removes_the_lock_and_the_gate_allows(tmp_path):
    repo = _repo(tmp_path)
    _cli(repo, "take", "x")
    proc = _cli(repo, "release")
    assert proc.returncode == 0 and "released" in proc.stdout
    assert not _lock(repo).exists()
    assert _gate(repo, COMMIT).returncode == 0


def test_cli_release_without_a_lock_is_a_no_op(tmp_path):
    proc = _cli(_repo(tmp_path), "release")
    assert proc.returncode == 0 and "no mutation lock" in proc.stdout


def test_cli_status_reports_presence_by_exit_code(tmp_path):
    repo = _repo(tmp_path)
    assert _cli(repo, "status").returncode == 1
    _cli(repo, "take", "why")
    proc = _cli(repo, "status")
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["reason"] == "why"


def test_the_lock_file_is_gitignored():
    """The lock lives in the repository and must never be committed."""
    patterns = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".claude/*.lock" in patterns
