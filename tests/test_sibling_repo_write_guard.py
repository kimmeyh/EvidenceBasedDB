"""Tests for .claude/hooks/block_sibling_repo_writes.py (Sprint 1, added
2026-09-15).

Team lead: this repository's sessions must not write into spamfilter-multi
or hsbc-quantum-fraud-2026 -- reading either for research stays fine, but a
write, edit, or write-shaped shell command targeting either repository (or
their Claude Code memory directories) must be blocked.

Per this repository's guard-discipline standard, every case below is
exercised directly against the hook subprocess with a controlled JSON
payload, which is also how a prior hook bug in this same file family was
actually caught: a shell-quoting artifact in an ad-hoc smoke test produced
a false negative that this direct-subprocess pattern does not reproduce.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "block_sibling_repo_writes.py"


def _run(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_write_to_hsbc_repo_is_blocked():
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\CLAUDE.md"},
    }
    assert _run(payload).returncode == 2


def test_write_to_spamfilter_repo_is_blocked():
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": r"D:\Data\Harold\github\spamfilter-multi\docs\foo.md"},
    }
    assert _run(payload).returncode == 2


def test_edit_to_hsbc_memory_directory_is_blocked():
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-hsbc-quantum-fraud-2026\memory\foo.md"
        },
    }
    assert _run(payload).returncode == 2


def test_write_to_this_repository_is_allowed():
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": r"D:\Data\Harold\github\EvidenceBasedDB\docs\foo.md"},
    }
    assert _run(payload).returncode == 0


def test_write_to_this_repository_memory_directory_is_allowed():
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-EvidenceBasedDB\memory\foo.md"
        },
    }
    assert _run(payload).returncode == 0


def test_bash_read_only_command_referencing_a_guarded_path_is_allowed():
    """Reading stays fine -- the instruction was 'do not write', not 'do
    not touch'. A cat/grep/git-log mentioning a guarded path must pass."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": r'cat "D:\Data\Harold\github\hsbc-quantum-fraud-2026\CLAUDE.md"'},
    }
    assert _run(payload).returncode == 0


def test_bash_git_commit_inside_hsbc_repo_is_blocked():
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": r'cd "D:/Data/Harold/github/hsbc-quantum-fraud-2026" && git commit -m x'
        },
    }
    assert _run(payload).returncode == 2


def test_bash_rm_inside_spamfilter_repo_is_blocked():
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "rm D:/Data/Harold/github/spamfilter-multi/foo.txt"},
    }
    assert _run(payload).returncode == 2


def test_bash_command_unrelated_to_guarded_paths_is_allowed():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
    assert _run(payload).returncode == 0


def test_bypass_token_allows_a_write_to_a_guarded_path():
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\CLAUDE.md allow_sibling_repo_write"
        },
    }
    assert _run(payload).returncode == 0


def test_notebook_edit_to_a_guarded_path_is_blocked():
    payload = {
        "tool_name": "NotebookEdit",
        "tool_input": {"notebook_path": r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\analysis.ipynb"},
    }
    assert _run(payload).returncode == 2


def test_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input="not json", capture_output=True, text=True
    )
    assert proc.returncode == 0
