#!/usr/bin/env python3
"""Keep local source paths honest (F48, Sprint 9 Task D).

A local `access` path breaks silently when a file moves (seen in the Cyc
work: three archives went to the Recycle Bin). This checks every record
whose `access` names a local path, with the same function the yearly
re-check uses (`store.recheck.check_local`), so the two never disagree:

  python scripts/check_local_sources.py
      Lists every local source that is missing, changed (SHA-256 differs),
      unreadable, or has no SHA-256 recorded. Writes nothing; exit 1 when a
      file is missing, changed or unreadable.

  python scripts/check_local_sources.py --record-hashes [--apply]
      For each local FILE present with no SHA-256 in its evidence, appends
      "Local copy SHA-256 <hex>" (with its size and today's date) and notes
      it in updated_reason. DRY-RUN BY DEFAULT; --apply takes a verified
      backup first. A folder has no single hash and is left as it is. A hash
      that differs is never overwritten: that is the finding this exists to
      report.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PROBLEMS = ("local copy missing", "local copy changed (SHA-256 differs)", "local copy unreadable")
NO_HASH = "local copy present (no SHA-256 recorded)"


def statuses(conn) -> list[tuple[str, str, str, str]]:
    """(record_id, first local path, status, note) for every local-access record."""
    out = []
    for rid, access, evidence in conn.execute("SELECT record_id, access, evidence FROM paper_fields ORDER BY record_id"):
        paths = recheck.local_paths(access or "")
        if paths:
            status, note = recheck.check_local(access, evidence)
            out.append((rid, paths[0], status, note))
    return out


def hash_note(path: Path, today: str) -> str:
    data = path.read_bytes()
    return f"Local copy SHA-256 {hashlib.sha256(data).hexdigest()}, {len(data):,} bytes, recorded {today} (F48)"


def record_hashes(conn, rows, today: str) -> list[str]:
    log = []
    for rid, path, status, _ in rows:
        if status != NO_HASH:
            continue
        note = hash_note(Path(path), today)
        old = conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
        conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?",
                     (f"{old.rstrip()}; {note}" if old and old.strip() else note, rid))
        append_updated_reason(conn, rid, f"{today} (Sprint 9 Task D, F48): local copy's SHA-256 recorded", today)
        log.append(f"hashed {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    today = date.today().isoformat()
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        rows = statuses(conn)
        counts: dict[str, int] = {}
        for rid, path, status, note in rows:
            counts[status] = counts.get(status, 0) + 1
            if status in PROBLEMS:
                print(f"{status.upper()}: {rid} ({note or path})")
        print(f"{len(rows)} local-access record(s): " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
        if "--record-hashes" in args:
            if "--apply" in args:
                backup_before_write(DB_PATH, "F48 local copy hashes")
                log = record_hashes(conn, rows, today)
                conn.commit()
                print(f"{len(log)} hash(es) recorded. APPLIED")
            else:
                print(f"{counts.get(NO_HASH, 0)} hash(es) would be recorded. DRY RUN: re-run with --apply.")
    finally:
        conn.close()
    return 1 if any(status in PROBLEMS for _, _, status, _ in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
