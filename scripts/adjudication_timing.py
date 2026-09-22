#!/usr/bin/env python3
"""Run a timed adjudication session over a generated record packet
(Sprint 4 retrospective improvement 6; first used for F11 on 2026-09-21).

ADR-0004 names one number the whole design is constrained by: minutes of
team-lead adjudication per accepted record. Measuring it needs a clock the
team lead does not have to run by hand, so this script shows one record at
a time, stamps the interval between showing it and receiving the answer,
and appends to a JSON log that survives a session break.

    python scripts/adjudication_timing.py show 1
    python scripts/adjudication_timing.py done 1 "1 accept all, full protocol"
    python scripts/adjudication_timing.py status
    python scripts/adjudication_timing.py summary

`done` logs the answer and shows the next record in the same call, so the
gap between records is one command. The log is
`docs/sprints/<PACKET_STEM>_TIMING_LOG.json`, committed with the sprint.

WHAT THE INTERVAL INCLUDES, stated because the number is the deliverable:
it runs from the moment the record is printed to the moment the answer is
recorded, so it covers reading the packet entry, opening the source, the
judgment itself, and the presentation latency of whatever is driving the
session. It is a wall-clock cost of adjudication in this setting, not a
pure reading time. Report it that way.

PROTOCOL MODE MATTERS AS MUCH AS THE NUMBER. A run over records that have
already been corrected, with the prior review's findings printed under
each, measures CONFIRM-MODE review. A run where the source is opened
before the record is shown measures COLD adjudication. They are different
numbers and the log records which was run (`--mode`), because the first
F11 run produced 18/18 accept and that result means something different
under each mode.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = ROOT / "docs" / "sprints" / "SPRINT_4_F11_ADJUDICATION_PACKET.md"

SECTION = re.compile(r"^### (\d+)\. `([^`]+)`\n(.*?)(?=^### \d+\. |\Z)", re.M | re.S)


def log_path(packet: Path) -> Path:
    return packet.with_name(packet.stem.replace("_PACKET", "") + "_TIMING_LOG.json")


def sections(packet: Path) -> dict[int, tuple[str, str]]:
    """Numbered record sections, up to the timing sheet."""
    body = packet.read_text(encoding="utf-8").split("## Timing sheet")[0]
    return {int(m.group(1)): (m.group(2), m.group(3).strip()) for m in SECTION.finditer(body)}


def load(packet: Path) -> dict:
    p = log_path(packet)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"packet": packet.name, "mode": None, "started": None, "records": []}


def save(packet: Path, log: dict) -> None:
    log_path(packet).write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def show(packet: Path, n: int, log: dict | None = None, mode: str | None = None) -> int:
    secs = sections(packet)
    if n not in secs:
        print(f"no record {n}; the packet has {len(secs)} ({min(secs, default=0)} to {max(secs, default=0)})")
        return 1
    rid, body = secs[n]
    log = log if log is not None else load(packet)
    entry = next((e for e in log["records"] if e["n"] == n), None)
    if entry is None:
        entry = {"n": n, "id": rid, "start": now(), "end": None, "minutes": None, "answer": None}
        log["records"].append(entry)
        log["started"] = log["started"] or entry["start"]
        log["mode"] = log.get("mode") or mode or "confirm"
        save(packet, log)
    print(f"=== Record {n} of {len(secs)}: `{rid}`   (clock started {entry['start'][11:]})\n")
    print(body)
    return 0


def done(packet: Path, n: int, answer: str) -> int:
    log = load(packet)
    entry = next((e for e in log["records"] if e["n"] == n), None)
    if entry is None or not entry.get("start"):
        print(f"record {n} was never shown; run `show {n}` first", file=sys.stderr)
        return 1
    entry["end"] = now()
    entry["minutes"] = round(
        (datetime.fromisoformat(entry["end"]) - datetime.fromisoformat(entry["start"])).total_seconds() / 60, 1)
    entry["answer"] = answer
    save(packet, log)
    finished = [e for e in log["records"] if e["minutes"] is not None]
    total = sum(e["minutes"] for e in finished)
    print(f"logged record {n} `{entry['id']}`: {entry['minutes']} min "
          f"({entry['start'][11:]} to {entry['end'][11:]}); answer: {answer}")
    print(f"running total: {len(finished)} record(s), {total:.1f} min, {total / len(finished):.1f} min/record\n")
    return show(packet, n + 1, log)


def status(packet: Path) -> int:
    log = load(packet)
    if not log["records"]:
        print("nothing logged yet")
        return 0
    for e in log["records"]:
        mins = f"{e['minutes']:>5}" if e["minutes"] is not None else "     "
        print(f"{e['n']:2d} {e['id']:55s} {e['start'][11:]} -> {(e['end'] or '')[11:]:8s} {mins} {e['answer'] or ''}")
    return 0


def summary(packet: Path) -> int:
    log = load(packet)
    mins = sorted(e["minutes"] for e in log["records"] if e["minutes"] is not None)
    if not mins:
        print("nothing logged yet")
        return 0
    n = len(mins)
    median = mins[n // 2] if n % 2 else round((mins[n // 2 - 1] + mins[n // 2]) / 2, 2)
    print(f"packet     : {log['packet']}")
    print(f"mode       : {log.get('mode') or 'unrecorded'}")
    print(f"records    : {n}")
    print(f"total      : {sum(mins):.1f} min")
    print(f"per record : {sum(mins) / n:.2f} min (median {median}, range {min(mins)} to {max(mins)})")
    print(f"wall clock : {log['records'][0]['start']} -> {log['records'][-1]['end']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    packet = DEFAULT_PACKET
    if "--packet" in args:
        i = args.index("--packet")
        packet = Path(args[i + 1])
        del args[i:i + 2]
    mode = None
    if "--mode" in args:
        i = args.index("--mode")
        mode = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 2
    if not packet.exists():
        print(f"error: packet {packet} does not exist", file=sys.stderr)
        return 1

    cmd = args[0]
    if cmd == "show" and len(args) > 1:
        return show(packet, int(args[1]), mode=mode)
    if cmd == "done" and len(args) > 1:
        return done(packet, int(args[1]), args[2] if len(args) > 2 else "")
    if cmd == "status":
        return status(packet)
    if cmd == "summary":
        return summary(packet)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
