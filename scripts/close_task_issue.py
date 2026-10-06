#!/usr/bin/env python3
"""Close a sprint task's GitHub issue by its task LETTER (Sprint 6
retrospective I3, 2026-10-05).

In Sprint 6 an issue was closed by a number typed from memory, and it was
the wrong task's (#63, Task I, for #62, Task H). The number now comes from
`current_sprint.task_issues` in `.claude/sprint_status.json`, and the issue's
own title is shown before anything is closed.

    python scripts/close_task_issue.py H "Done in 39b179e"            # shows what it would close
    python scripts/close_task_issue.py H "Done in 39b179e" --apply    # closes it
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / ".claude" / "sprint_status.json"


def issue_for(letter: str, status_path: Path = STATUS) -> int:
    """The issue number recorded for task `letter`; raises if there is none."""
    current = json.loads(status_path.read_text(encoding="utf-8"))["current_sprint"]
    mapping = current.get("task_issues") or {}
    key = letter.strip().upper()
    if key not in mapping:
        raise KeyError(f"task {key!r} has no issue in current_sprint.task_issues ({sorted(mapping)})")
    return int(mapping[key])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    args = [a for a in args if a != "--apply"]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    letter, comment = args
    number = issue_for(letter)
    title = subprocess.run(["gh", "issue", "view", str(number), "--json", "title", "-q", ".title"],
                           capture_output=True, text=True, check=True).stdout.strip()
    print(f"Task {letter.upper()} -> #{number}: {title}")
    if not apply:
        print("DRY RUN: nothing closed. Re-run with --apply.")
        return 0
    subprocess.run(["gh", "issue", "close", str(number), "-c", comment], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
