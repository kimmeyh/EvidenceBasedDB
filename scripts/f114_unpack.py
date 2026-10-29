#!/usr/bin/env python3
"""F114: a cloud reader saves the brief and the paper's text from its own message.

The coordinator sends them as a follow-up message (`scripts/f114_cloud.py`), never through git: a session
started from GitHub can push its result, and the text stays out of every commit (ADR-0005 section 3). The
message is in the session's own transcript, so this copies it out exactly, form feeds included, where the
session's reading of it would not.

Usage: python3 scripts/f114_unpack.py RECORD      writes /tmp/f114/brief.json and /tmp/f114/paper.txt
Exits 1, saying why, when no message holds both markers or the brief is not RECORD's.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BRIEF = "=== BRIEF ===\n"
TEXT = "\n=== PAPER TEXT ===\n"
OUT = Path("/tmp/f114")


def texts(entry: dict) -> list[str]:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return [content]
    return [b.get("text", "") for b in content or [] if isinstance(b, dict)]


def find(home: Path) -> str | None:
    """The newest user message holding both markers, in the newest transcript first."""
    for f in sorted(home.glob(".claude/projects/**/*.jsonl"), key=os.path.getmtime, reverse=True):
        for line in reversed(f.read_text(encoding="utf-8", errors="replace").splitlines()):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") == "user":
                for t in texts(entry):
                    if BRIEF in t and TEXT in t:
                        return t
    return None


def main(argv: list[str]) -> int:
    rid = argv[0]
    message = find(Path.home())
    if message is None:
        print("no message holds the brief and the paper's text")
        return 1
    brief_part, text = message.split(BRIEF, 1)[1].split(TEXT, 1)
    brief = json.loads(brief_part)
    if [r["record_id"] for r in brief["records"]] != [rid]:
        print(f"the brief is for {[r['record_id'] for r in brief['records']]}, not {rid}")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "brief.json").write_text(json.dumps(brief, indent=1), encoding="utf-8")
    (OUT / "paper.txt").write_text(text, encoding="utf-8")
    print(f"saved {OUT / 'brief.json'} and {OUT / 'paper.txt'}: {len(text)} characters, "
          f"{text.count(chr(12))} page breaks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
