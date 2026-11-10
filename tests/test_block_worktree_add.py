"""Behavioral tests for .claude/hooks/block_worktree_add.py (Sprint 17 retrospective i1 = a, team lead 2026-11-10).

Runs the real hook as a subprocess with a JSON payload. The escape-route cases come from the fresh-eyes review of
2026-11-10 (an apostrophe pairing quotes across the command, the heredoc opener line erased, a bypass token honored in
a comment, `git -c`, `git.exe`, a quoted -C path, a line continuation), each of which the first version allowed.

Proven red 2026-11-10: with WORKTREE_ADD's pattern changed to match nothing (INJECTED), every shell case was allowed;
with the EnterWorktree branch removed (INJECTED), the tool case was allowed; with HEREDOC_BODY restored to strip from
`<<` (INJECTED), the heredoc-opener case was allowed and, with the heredoc strip removed (INJECTED), the heredoc-body
case was blocked. Each restored and green.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "block_worktree_add.py"


def _run(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)


@pytest.mark.parametrize("command", [
    "git worktree add ../EvidenceBasedDB-sprint17 feature/20261107_Sprint_17",
    "cd /d/Data/Harold/github/EvidenceBasedDB && git -C . worktree add -b x ../other",
    "echo \"it's\" && git worktree add ../x && echo 'x'",
    "echo don't; git worktree add ../x; echo it's",
    "cat <<EOF && git worktree add ../x\nbody\nEOF",
    "git worktree add ../x  # note: never allow_worktree_add",
    "git -c core.x=y worktree add ../x",
    "git --work-tree=. worktree add ../x",
    "git.exe worktree add ../x",
    "& 'C:\\Program Files\\Git\\cmd\\git.exe' worktree add ../x",
    "git -C \"D:/a b\" worktree add ../x",
    "git \\\n worktree add ../x",
    "GIT WORKTREE ADD ../x",
])
def test_a_shell_worktree_add_is_blocked(command):
    proc = _run({"tool_name": "Bash", "tool_input": {"command": command}})
    assert proc.returncode == 2, command
    assert "team lead's approval" in proc.stderr


def test_the_worktree_tool_is_blocked():
    proc = _run({"tool_name": "EnterWorktree", "tool_input": {}})
    assert proc.returncode == 2


@pytest.mark.parametrize("command", [
    "git worktree list",
    "git worktree remove ../EvidenceBasedDB-sprint17",
    "git worktree prune",
    "git commit -F msg.txt",
    "python - <<'EOF'\nprint('never run git worktree add without asking')\nEOF\ngit status",
])
def test_inspecting_removing_or_a_heredoc_body_is_allowed(command):
    proc = _run({"tool_name": "Bash", "tool_input": {"command": command}})
    assert proc.returncode == 0, proc.stderr
