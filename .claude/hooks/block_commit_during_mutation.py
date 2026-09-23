"""PreToolUse hook blocking `git commit` while a mutation lock is held
(Sprint 4 Task I, F17, the gate).

The lock is taken by mutation_lock.py before a guard is deliberately broken
for an injection test and released after the restore. While it is held, the
working tree is wrong on purpose, and a commit would sweep the mutation up.
Modeled on spamfilter-multi's `block-commit-during-mutation.ps1` (read-only
source, 2026-09-18 survey); the mechanism is generic and needed only path
changes here.

STALENESS, so a crashed session cannot deadlock every future commit: a lock
is stale when its `taken` timestamp is older than 4 hours OR its `pid` is
an integer naming a process that is no longer alive. A null `pid` (what the
CLI writes, since no pid it can see outlives a Bash tool call; see
mutation_lock.py) skips the liveness check and the lock expires by age
alone. A stale lock is reported on stderr, REMOVED, and the commit is
ALLOWED. A lock that cannot be parsed is treated the same way.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_commit_during_mutation in the command.
Matches INVOCATIONS, not text: quoted strings and heredoc bodies are
stripped before matching, as block_carry_forward_stash.py does. Payload key
repo_override lets tests point the hook at a scratch repository.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HEREDOC_BODY = re.compile(
    r"(?s)<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?.*?^\s*\1\s*$", re.MULTILINE
)
HERESTRING_BODY = re.compile(r"(?s)@'.*?'@")
SINGLE_QUOTED = re.compile(r"'[^']*'")
DOUBLE_QUOTED = re.compile(r'"[^"]*"')
GIT_COMMIT = re.compile(r"\bgit\s+(?:(?:-C|-c)\s+\S+\s+)*commit\b")

BYPASS_TOKEN = "allow_commit_during_mutation"
LOCK_NAME = "mutation.lock"
MAX_AGE = timedelta(hours=4)


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


def is_git_commit(cmd: str) -> bool:
    scan = HEREDOC_BODY.sub(" ", cmd)
    scan = HERESTRING_BODY.sub(" ", scan)
    scan = SINGLE_QUOTED.sub(" ", scan)
    scan = DOUBLE_QUOTED.sub(" ", scan)
    return bool(GIT_COMMIT.search(scan))


def pid_alive(pid: int) -> bool:
    """True when the process exists. Unknown (no way to check) counts as
    alive, so an unverifiable lock still blocks until it ages out."""
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            process_query_limited_information = 0x1000
            handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
            if handle:
                still_active = 259
                exit_code = ctypes.c_ulong()
                alive = True
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    alive = exit_code.value == still_active
                kernel32.CloseHandle(handle)
                return alive
            error_access_denied = 5
            return kernel32.GetLastError() == error_access_denied
        except Exception:
            return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def staleness(record: dict) -> str | None:
    """A reason the lock is stale, or None when it is live."""
    try:
        taken = datetime.fromisoformat(str(record["taken"]))
    except Exception:
        return "its 'taken' timestamp is missing or unparseable"
    if taken.tzinfo is None:
        taken = taken.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - taken
    if age > MAX_AGE:
        return f"it is {age} old (limit {MAX_AGE})"
    pid = record.get("pid")
    if pid is None:
        return None  # age-only lock (CLI default); no process to check
    if isinstance(pid, bool) or not isinstance(pid, int):
        return f"its 'pid' {pid!r} is not an integer"
    if not pid_alive(pid):
        return f"pid {pid} is not alive"
    return None


def main() -> int:
    try:
        payload = _read_payload()
        cmd = _command(payload)
    except Exception:
        return 0  # fail open on malformed payload

    if not cmd or not cmd.strip():
        return 0
    if BYPASS_TOKEN in cmd:
        return 0
    if not is_git_commit(cmd):
        return 0

    cwd = str(payload.get("repo_override") or payload.get("cwd") or Path.cwd())
    lock = Path(cwd) / ".claude" / LOCK_NAME
    if not lock.exists():
        return 0

    try:
        record = json.loads(lock.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError("lock is not a JSON object")
        stale = staleness(record)
    except Exception as exc:
        record = {}
        stale = f"it cannot be parsed ({exc.__class__.__name__})"

    if stale:
        try:
            lock.unlink()
            removed = "removed"
        except OSError:
            removed = "could not be removed"
        print(
            f"[WARNING block_commit_during_mutation] stale mutation lock at {lock} "
            f"({stale}); {removed}, commit allowed. Record was: {json.dumps(record)}",
            file=sys.stderr,
        )
        return 0

    print(
        "[BLOCKED by block_commit_during_mutation hook]\n"
        "\n"
        f"A mutation lock is held at {lock}:\n"
        f"  taken:  {record.get('taken')}\n"
        f"  pid:    {record.get('pid')}\n"
        f"  reason: {record.get('reason')}\n"
        "\n"
        "The working tree is deliberately broken for an injection test (CLAUDE.md:\n"
        "\"break the thing it guards, watch it go red, then restore\"). Committing\n"
        "now would sweep the mutation up. Restore the guarded file, confirm the\n"
        "suite is green, then release the lock:\n"
        "\n"
        "  python .claude/hooks/mutation_lock.py release\n"
        "\n"
        "Bypass (team-lead-sanctioned only): include the literal token\n"
        f"{BYPASS_TOKEN} in the command.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
