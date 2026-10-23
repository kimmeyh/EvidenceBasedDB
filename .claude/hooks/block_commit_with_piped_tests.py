"""PreToolUse hook blocking a `git commit` chained after a test run whose
exit code a pipe has discarded (Sprint 4 retrospective improvement 1).

WHAT HAPPENED, 2026-09-20: a command of the shape

    python -m pytest -q ... | tail -1 && git add -A && git commit ...

committed two ADR amendments with the suite RED. `tail` succeeded, so `&&`
saw success; pytest's exit code was thrown away by the pipe. The failure
was a CHANGELOG guard that had just started failing for an unrelated
reason, and the commit landed anyway. Nothing in the transcript looked
wrong: the printed line said "1 failed, 360 passed" and scrolled past.

THE RULE: a commit gated on tests must be gated on the TEST RUNNER'S exit
code, never on the last command of a pipeline.

    # blocked
    pytest -q | tail -1 && git commit -m ...

    # correct, either way
    pytest -q > /tmp/suite.txt 2>&1; rc=$?; tail -1 /tmp/suite.txt
    test $rc -eq 0 && git commit -m ...

    pytest -q && git commit -m ...        # no pipe, exit code intact

Only blocks when ALL THREE hold in one command: a test-runner invocation,
that invocation piped into something, and a `git commit` later in the same
command. A commit with no test run, a test run with no commit, and a
piped test run that does not commit are all untouched.

SECOND CHECK (Sprint 11 retrospective I2, 2026-10-23): a commit of a tree
whose recorded suite verdict is FAILED or INVALID. `scripts/run_suite.py`
records the verdict and the git tree id it ran on in
.claude/suite_verdict.json; when the working tree now is that tree, and
the verdict was not PASSED, the commit is refused. Sprint 11 called a red
suite passed by reading scrolling output, and ran a suite with an
injection still in the code. No verdict, or a verdict for another tree,
allows the commit: when a full suite must precede a commit is F100's
decision, not this hook's.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_piped_test_commit (the pipe check),
allow_red_suite_commit (the verdict check).
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BYPASS_TOKEN = "allow_piped_test_commit"
RED_SUITE_BYPASS = "allow_red_suite_commit"

# Strip heredoc bodies and quoted strings before matching, so a commit
# MESSAGE that talks about pytest and pipes is not itself a match. Same
# treatment as block_commit_during_mutation.py.
HEREDOC_BODY = re.compile(
    r"(?s)<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?.*?^\s*\1\s*$", re.MULTILINE
)
HERESTRING_BODY = re.compile(r"(?s)@'.*?'@")
SINGLE_QUOTED = re.compile(r"'[^']*'")
DOUBLE_QUOTED = re.compile(r'"[^"]*"')

GIT_COMMIT = re.compile(r"\bgit\s+(?:(?:-C|-c)\s+\S+\s+)*commit\b")
# A test-runner invocation: pytest directly, or through python -m.
TEST_RUN = re.compile(r"(?:\bpytest\b|\bpython[0-9.]*(?:\.exe)?\s+-m\s+pytest\b|\bnpm\s+(?:run\s+)?test\b)")
# The pipe that eats the exit code. `|&` and `||` are NOT this: `||` is a
# fallback operator and does not discard the left side's status.
EATS_EXIT_CODE = re.compile(r"\|(?!\|)")


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _command(payload: dict) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict) and tool_input.get("command"):
        return str(tool_input["command"])
    if payload.get("command"):
        return str(payload["command"])
    return ""


def _strip_literals(cmd: str) -> str:
    for pattern in (HEREDOC_BODY, HERESTRING_BODY, SINGLE_QUOTED, DOUBLE_QUOTED):
        cmd = pattern.sub(" ", cmd)
    return cmd


def _piped_test_segments(cmd: str) -> list[tuple[int, str]]:
    """(offset, segment) for each segment where a test run is piped onward.

    Split on the operators that START a new command with its own exit
    status (&&, ||, ;, newline). Within one segment, a `|` after a test
    runner means the segment's status is the pipeline's last command. The
    offset is the segment's position in the original string, so the caller
    can tell whether the piped run comes BEFORE the commit it would gate.
    """
    # TRUE offsets, from a capturing split that hands back the separators.
    #
    # The first version estimated with `pos += len(seg) + 2`, correct for
    # `&&` and `||` but one too many for `;` and a newline. The drift
    # accumulated, and once it exceeded the distance from the piped test to
    # the commit, the ordering comparison inverted and the hook ALLOWED the
    # exact mistake it exists to stop. Measured 2026-09-23 (PR #30 round-2
    # audit): blocked at 19 preceding newline-separated lines, allowed at
    # 20. A 20-line Bash block is an ordinary command here, so this was live.
    #
    # A false negative in a guard is worse than the false positive it
    # replaced: the false positive was visible and arguable, this was
    # silent. "Only relative order is used" was the flawed premise --
    # relative order was derived from an absolute offset that drifted.
    out = []
    parts = re.split(r"(&&|\|\||;|\n)", cmd)
    pos = 0
    for i in range(0, len(parts), 2):
        seg = parts[i]
        m = TEST_RUN.search(seg)
        if m and EATS_EXIT_CODE.search(seg[m.end():]):
            out.append((pos, seg.strip()))
        pos += len(seg) + (len(parts[i + 1]) if i + 1 < len(parts) else 0)
    return out


def _red_verdict(payload: dict) -> dict | None:
    """The recorded verdict, when it is not PASSED and the working tree now
    is the tree it ran on. None on anything missing: fail open."""
    try:
        cwd = payload.get("cwd") or os.getcwd()
        top = Path(subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True,
                                  text=True, check=True).stdout.strip())
        record = json.loads((top / ".claude" / "suite_verdict.json").read_text(encoding="utf-8"))
        if record.get("verdict") == "PASSED":
            return None
        spec = importlib.util.spec_from_file_location("run_suite", top / "scripts" / "run_suite.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        tree = runner.working_tree(top)
        return record if tree in (record.get("tree"), record.get("tree_after")) else None
    except Exception:  # noqa: BLE001 -- no verdict, no git, no runner: allow
        return None


def main() -> int:
    try:
        payload = _read_payload()
        cmd = _command(payload)
    except Exception:  # noqa: BLE001 -- fail open on a malformed payload
        return 0

    if not cmd.strip():
        return 0

    stripped = _strip_literals(cmd)
    commit = GIT_COMMIT.search(stripped)
    if not commit:
        return 0

    if RED_SUITE_BYPASS not in cmd and (red := _red_verdict(payload)):
        print(
            f"[BLOCKED] `git commit` of a tree whose suite verdict is {red.get('verdict')}\n"
            "(Sprint 11 retrospective I2).\n"
            "\n"
            f"Recorded by scripts/run_suite.py at {red.get('finished')}: {red.get('summary')}, "
            f"rc={red.get('rc')}.\n"
            "The working tree now is the tree that run checked"
            + (" (or its tree after the run; files changed during it)" if red.get("verdict") == "INVALID" else "")
            + ".\n"
            "\n"
            "FIX: correct the failure, then `python scripts/run_suite.py`, and commit\n"
            "once it prints SUITE PASSED. If this commit genuinely does not depend on\n"
            "that run, re-run with the literal token allow_red_suite_commit.",
            file=sys.stderr,
        )
        return 2

    if BYPASS_TOKEN in cmd:
        return 0

    # ORDER MATTERS: only a piped test run BEFORE the commit can pretend to
    # gate it. `git commit -m x && pytest -q | tail` is an ordinary workflow
    # -- commit, then run the suite and read the tail -- and the commit's
    # status cannot depend on a pipeline downstream of it. Blocking that was
    # a false positive (PR #30 review, 2026-09-22), the same over-match class
    # this sprint had just fixed in block_unraw_escape.py.
    piped = [(off, seg) for off, seg in _piped_test_segments(stripped) if off < commit.start()]
    if not piped:
        return 0

    sample = "\n    ".join(seg[:100] for _, seg in piped[:2])
    print(
        "[BLOCKED] `git commit` gated on a test run whose exit code a pipe discarded\n"
        "(Sprint 4 retrospective improvement 1).\n"
        "\n"
        "Found:\n"
        f"    {sample}\n"
        "\n"
        "A pipeline's exit status is its LAST command's. `pytest | tail` succeeds\n"
        "whenever tail succeeds, so `&& git commit` commits a red suite. This happened\n"
        "on 2026-09-20: two ADR amendments were committed with one test failing, and\n"
        "the printed summary line scrolled past unread.\n"
        "\n"
        "FIX, either form:\n"
        "    pytest -q > /tmp/suite.txt 2>&1; rc=$?; tail -1 /tmp/suite.txt\n"
        "    test $rc -eq 0 && git add -A && git commit -m ...\n"
        "\n"
        "    pytest -q && git add -A && git commit -m ...   # no pipe, status intact\n"
        "\n"
        "If the commit genuinely does not depend on that test run, re-run with the\n"
        "literal token allow_piped_test_commit in the command.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
