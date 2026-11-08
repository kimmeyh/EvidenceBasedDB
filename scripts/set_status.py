#!/usr/bin/env python3
"""F142 part 4 (Sprint 17 Task C): one step sets both status fields of `.claude/sprint_status.json`.

The file holds the status twice: the top-level `status` and `current_sprint.status`. The status footer reads
`current_sprint.status`, the Stop hooks read either, and Sprint 16 set only one at Phase 5.3, so it needed a second
commit (8d16500) to make the footer show the true phase. This script writes both from one argument, and appends an
optional note to `current_sprint.note`; `tests/test_set_status.py` also fails when the committed file's two fields
differ.

    python scripts/set_status.py "Phase 5.3 Manual Validation" [--note "what happened"]

A status must start "Phase n.n " (the footer's phase depth is n.n, never n.n.n).
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / ".claude" / "sprint_status.json"
FORM = re.compile(r"Phase \d+\.\d+ \S[^\n]*")  # the whole status, one line (fresh-eyes review of f79714b)


def set_status(status: str, note: str | None = None, path: Path = STATUS) -> dict:
    if not FORM.fullmatch(status):
        raise ValueError(f"a status starts 'Phase n.n <name>': {status!r}")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = status
    data["current_sprint"]["status"] = status
    if note:
        old = data["current_sprint"].get("note") or ""
        data["current_sprint"]["note"] = f"{old} | {note}" if old else note
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, suffix=".partial", delete=False) as out:
        json.dump(data, out, indent=2, ensure_ascii=False)
        out.write("\n")
    try:
        Path(out.name).replace(path)
    finally:  # a failed replace (the file held open on Windows) leaves no .partial file in the tree
        Path(out.name).unlink(missing_ok=True)
    return data


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    note = None
    if "--note" in args:
        i = args.index("--note")
        if i + 1 >= len(args) or not args[i + 1].strip():
            print("REFUSED: --note needs its text")
            return 2
        note = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        set_status(args[0], note)
    except ValueError as e:
        print(f"REFUSED: {e}")
        return 1
    print(f"status set (both fields): {args[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
