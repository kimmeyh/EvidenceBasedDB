"""Advisory mutation lock for guard-discipline injection tests (Sprint 4
Task I, F17, the lock tool).

CLAUDE.md: "Don't claim a guard works because the suite is green. Prove it
FAILS. Break the thing it guards, watch it go red, then restore." Between
the deliberate break and the restore the working tree is WRONG on purpose,
and nothing stopped a commit from sweeping the mutation up. The source
repository (spamfilter-multi, `mutation-lock.ps1`, read-only survey
2026-09-18) hit this twice in one sprint: "vigilance was not the missing
ingredient; a structural gate was."

Usage (from the repository root):
  python .claude/hooks/mutation_lock.py take <reason ...>
      writes .claude/mutation.lock as JSON {"taken", "pid", "reason"}. The
      reason is free text and should name what is being mutated, e.g.
      `take .claude/hooks/block_ask_user_question.py injection`.
  python .claude/hooks/mutation_lock.py release
      removes the lock.
  python .claude/hooks/mutation_lock.py status
      prints the lock (exit 0) or reports no lock (exit 1).

Options: --repo <path> chooses the repository root (default: the root this
script lives in); --lock-file <path> overrides the lock path outright.
Both exist so tests never touch this repository's own lock. --pid <N>
binds the lock to a long-lived process so the gate can expire it when
that process dies.

WHY "pid" IS NULL BY DEFAULT FROM THE CLI. The first version wrote
os.getpid(), and the live-fire smoke test (2026-09-19) showed the gate
reporting every CLI-taken lock stale on the very next commit: the CLI is
a subprocess that has already exited by then, so its pid is dead. Under
Claude Code's Bash tool every command runs in a fresh shell, so no pid the
CLI can see outlives the call. A null pid tells the gate to rely on the
4-hour age limit alone. The programmatic take() keeps os.getpid() as its
default for a long-lived caller (a test harness or a script that holds the
lock across its own run).

The gate that reads this file is block_commit_during_mutation.py. The lock
file is gitignored by the `.claude/*.lock` pattern.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LOCK_NAME = "mutation.lock"
DEFAULT_REPO = Path(__file__).resolve().parents[2]


def lock_path(repo: Path | None = None) -> Path:
    return (repo or DEFAULT_REPO) / ".claude" / LOCK_NAME


_SELF = object()


def take(path: Path, reason: str, pid: int | None | object = _SELF) -> dict:
    """Write the lock. pid defaults to this process; pass None for an
    age-only lock (what the CLI does, see the module docstring)."""
    record = {
        "taken": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pid": os.getpid() if pid is _SELF else pid,
        "reason": reason,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def release(path: Path) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False


def status(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError):
        return {"corrupt": True, "path": str(path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=("take", "release", "status"))
    parser.add_argument("reason", nargs="*", help="what is being mutated (take only)")
    parser.add_argument("--repo", type=Path, default=None)
    parser.add_argument("--lock-file", type=Path, default=None)
    parser.add_argument(
        "--pid", type=int, default=None,
        help="bind the lock to this long-lived process (default: none, age-only expiry)",
    )
    # parse_intermixed_args, not parse_args: with nargs="*" for the reason,
    # parse_args consumed an EMPTY reason before `--repo`, then rejected the
    # trailing words ("take --repo X injection on export.py" -> exit 2,
    # "unrecognized arguments"). Coordinator live-fire finding, 2026-09-19.
    args = parser.parse_intermixed_args(argv)

    path = args.lock_file or lock_path(args.repo)

    if args.action == "take":
        reason = " ".join(args.reason).strip()
        if not reason:
            parser.error("take needs a reason naming what is being mutated")
        if path.exists():
            existing = status(path)
            print(f"lock already held at {path}: {json.dumps(existing)}", file=sys.stderr)
            print("release it first, or let the gate report it stale.", file=sys.stderr)
            return 1
        record = take(path, reason, pid=args.pid)
        print(f"mutation lock taken at {path}: {json.dumps(record)}")
        return 0

    if args.action == "release":
        if release(path):
            print(f"mutation lock released: {path}")
        else:
            print(f"no mutation lock at {path}")
        return 0

    record = status(path)
    if record is None:
        print(f"no mutation lock at {path}")
        return 1
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
