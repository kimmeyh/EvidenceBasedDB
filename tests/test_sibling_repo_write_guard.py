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

import pytest

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


def test_writes_into_phase2_and_its_memory_directory_are_blocked():
    """F79 (Sprint 9 Task A, 2026-10-15). Team lead, 2026-10-14: the two
    repositories read each other freely and never write to each other.

    Verified by injection, 2026-10-15: deleting the hsbc-qfraud-phase2
    repository line from GUARDED_ROOTS let the Write case through (exit 0,
    test red); deleting the project-directory line instead let the memory
    Edit case through (test red). Each restored and green again."""
    write = {
        "tool_name": "Write",
        "tool_input": {"file_path": r"D:\Data\Harold\github\hsbc-qfraud-phase2\docs\NOTE.md"},
    }
    commit = {
        "tool_name": "Bash",
        "tool_input": {"command": 'cd "D:/Data/Harold/github/hsbc-qfraud-phase2" && git commit -m x'},
    }
    memory = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-hsbc-qfraud-phase2\memory\x.md"
        },
    }
    for payload in (write, commit, memory):
        assert _run(payload).returncode == 2, payload


P2 = "D:/Data/Harold/github/hsbc-qfraud-phase2"


@pytest.mark.parametrize("command", [
    f'git -C "{P2}" commit -am x',
    f"git -C {P2} push",
    f'git -C "{P2}" checkout -- docs/x.md',
    f"cd {P2}; git restore docs/x.md",
    f"cd {P2} && git stash",
    rf'Remove-Item "D:\Data\Harold\github\hsbc-qfraud-phase2\x.md"',
    rf'Copy-Item a.md "D:\Data\Harold\github\hsbc-qfraud-phase2\x.md"',
    f"echo x | tee {P2}/x.md",
    f"sed -i 's/a/b/' {P2}/x.md",
    # Git is fail-closed: any subcommand outside the read list blocks,
    # whatever global options come first (automated security review).
    f'git --no-pager -C "{P2}" commit -m x',
    f"git -C {P2} pull",
    f"git -C {P2} config user.name x",
    f"git -C {P2} update-ref HEAD abc",
    f"git -c core.x=y -C {P2} revert HEAD",
    # A read subcommand that writes through an option, and git after a quote
    # or backtick (second security review, 2026-10-15).
    f"git -C {P2} log --output={P2}/x.txt",
    f"git -C {P2} -c core.pager=evil log",
    f"git -C {P2} grep --open-files-in-pager=vi x",
    f'"git" -C {P2} commit -m x',
    f"echo `git -C {P2} commit -m x`",
])
def test_write_forms_into_phase2_are_blocked(command):
    """Sprint 9 Task A review (2026-10-15): each of these returned exit 0.
    `git -C <phase2> <write>` matters most, because INTAKE_WORKFLOW.md
    section 19 reads Phase 2 with `git -C`.

    Verified by injection, 2026-10-15: with Remove-Item, Copy-Item, tee and
    sed -i removed from the verbs, those four went red; with _git_writes
    made to return False, every git case went red. Restored and green
    again. (An earlier injection, against the first, denylist version of
    the git check, removed its `-C` option group and turned the git -C
    cases red.) Second security review, same day: with the writing-option
    check disabled, the --output and --open-files-in-pager cases went red;
    with _GIT_CALL back to whitespace-only boundaries, the quoted and
    backticked git cases went red. Restored and green again."""
    assert _run({"tool_name": "Bash", "tool_input": {"command": command}}).returncode == 2, command


@pytest.mark.parametrize("command", [
    f'git -C "{P2}" show 139fa13:docs/B4_B5_HARDWARE_RESULT.md',
    f"git -C {P2} log --oneline -3",
    f"git --no-pager -C {P2} diff HEAD~1 -- docs",
    f'git -C "{P2}" rev-parse HEAD && git status --short',
    f"sed -n 1,20p {P2}/CLAUDE.md",
])
def test_read_forms_of_phase2_stay_allowed(command):
    """Known over-block, accepted by the hook's design (module docstring): a
    read whose pattern is a bare write verb, such as `grep tee <phase2
    file>`, is blocked; quote the pattern or use the Grep tool."""
    assert _run({"tool_name": "Bash", "tool_input": {"command": command}}).returncode == 0, command


@pytest.mark.parametrize("command", [
    f"git -C {P2} log --outp={P2}/x.txt",
    f"git -C {P2} log --out {P2}/x.txt",
    f"git -C {P2} grep --open x",
    f"git -C {P2} grep -nO x",
    f"git -C {P2} grep -iO x",
    # Second security review of the Task E fix: each passed at 6c37e83
    f"git -C {P2} grep -n -O x",
    f"git -C {P2} grep -LO x",
    f"git -C {P2} grep -GO x",
    f"git -C {P2} grep -3O x",
    f"git -C {P2} diff -M --output={P2}/x.txt",
    # Third security review: a long writing option after a value-taking flag
    f"git -C {P2} shortlog -n --output={P2}/x.txt",
    f"git -C {P2} log -S --outp={P2}/x.txt",
])
def test_accidental_option_forms_into_phase2_are_blocked(command):
    """F82 (Sprint 10 Task E, team lead Q2 = 1): forms a session could type
    by accident. Each passed (exit 0) against the hook as committed before
    this task (run 2026-10-18 with a copy of that version). Proven by
    injection, 2026-10-18: with _git_option_writes reduced to the old
    _GIT_WRITING_OPTION match, every case went red. Restored. The first
    version also blocked --ext-diff and --textconv; its review showed git
    runs those programs on a plain diff by default, so they were removed
    (module docstring). The second security review's five cases each
    passed at 6c37e83 (one shared list of value-taking options made -n,
    -L, -G and -M look like they took a value in grep and diff); proven by
    injection, 2026-10-18: with the grep entries removed from
    _GIT_SHORT_WITH_VALUE and _GIT_VALUE_WORD (so grep used the log list),
    -nO, -n -O, -LO and -GO passed, and the allowed `grep -e -Option` was
    blocked. Restored. (-3O and the diff case block under either list.)
    Third security review: the shortlog and `log -S --outp` cases passed
    at 08f5510; proven by injection, 2026-10-18: with the long-option
    exception removed from the value-word skip, both passed again."""
    assert _run({"tool_name": "Bash", "tool_input": {"command": command}}).returncode == 2, command


@pytest.mark.parametrize("command", [
    f"git -C {P2} diff --text HEAD~1 -- docs",
    f"git -C {P2} log --oneline --stat -3",
    f"git -C {P2} grep -n -i x",
    f"git -C {P2} show --no-ext-diff HEAD",
    # Task E review, 2026-10-18: each was blocked at 6cd9002
    f"git -C {P2} log -SOAuth",
    f"git -C {P2} log -GOne",
    f"git -C {P2} grep -e -Option",
    f"git -C {P2} log -p --output-indicator-new=+",
])
def test_read_options_that_look_like_writing_ones_stay_allowed(command):
    """`--no-ext-diff` turns the external program off; an O inside the
    value of -S, -G or -e is not -O; --output-indicator-new is not
    --output. The four review cases were each blocked at 6cd9002 (the
    --output-indicator case also before Task E). Proven by injection,
    2026-10-18: with the value-option stop removed from
    _short_cluster_has_o, the -SOAuth and -GOne cases were blocked; with
    the separate-value-word skip removed, the `-e -Option` case was
    blocked. Restored."""
    assert _run({"tool_name": "Bash", "tool_input": {"command": command}}).returncode == 0, command


def test_reading_phase2_stays_allowed():
    """The other half of F79: reads need no prompt and no bypass."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": 'git -C "D:/Data/Harold/github/hsbc-qfraud-phase2" log --oneline -1'
        },
    }
    assert _run(payload).returncode == 0


def test_malformed_payload_fails_open():
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input="not json", capture_output=True, text=True
    )
    assert proc.returncode == 0
