#!/usr/bin/env python3
"""Recover the `updated_reason` history that Sprint 4 Task C destroyed
(PR #30 review finding 1, 2026-09-22).

WHAT HAPPENED. `_append_reason` in `scripts/sprint4_task_c_corrections.py`
carried an inverted ternary: it appended to the existing text only when the
row had already been touched the SAME DAY, and REPLACED it otherwise. The
normal case is a row carrying history from an earlier date, so the normal
case was destruction. The same shape was in Task F and Task H.

Measured against the committed exports: prior `updated_reason` survives on
0 of 44 records that had one. 43 lost "Sprint 1 Task F: 46-paper seed set
loaded at seen tier"; `lenat-marcus-2023-trustworthy-ai` lost the Task E
premise-falsifier note.

Why this is worth a repair script rather than a shrug: `updated_reason` is
the row's own account of why it says what it says, and ADR-0004 section 2
makes `export/` the artifact the whole review mechanism depends on. A
reader of the export today cannot tell these papers arrived in the Sprint 1
seed load. CLAUDE.md: "A record that cannot say where its value came from
is the defect this whole system exists against."

WHAT THIS DOES. Reads the last good `updated_reason` for each paper from
git (`develop:export/papers.json`), and PREPENDS it to the current value,
so the row reads oldest-first exactly as it would have had the bug never
existed. Records renamed this sprint are mapped; records created this
sprint are untouched (they have no prior history to recover).

DRY-RUN BY DEFAULT; `--apply` writes inside one transaction and
regenerates the export.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

# The source of truth for what was lost: the export as committed on develop,
# before the Sprint 4 branch ran.
SOURCE_REF = "develop:export/papers.json"

# Renamed in Task C (decision Q4); the history belongs to the new id.
RENAMES = {
    "rand-2023-pqc-critical-infrastructure-assessment": "rand-2022-pqc-critical-infrastructure-assessment",
    "rand-2023-pqc-critical-infrastructure-assessment-appendix-b": "rand-2022-pqc-critical-infrastructure-assessment-appendix-b",
}


def prior_reasons() -> dict[str, str]:
    raw = subprocess.run(["git", "show", SOURCE_REF], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8")
    if raw.returncode != 0:
        raise SystemExit(f"error: cannot read {SOURCE_REF}: {raw.stderr.strip()}")
    out = {}
    for rec in json.loads(raw.stdout):
        pid = RENAMES.get(rec["id"], rec["id"])
        reason = (rec.get("updated_reason") or "").strip()
        if reason:
            out[pid] = reason
    return out


def plan(conn) -> list[tuple[str, str, str]]:
    """(id, recovered_prefix, current) for every row missing its history."""
    prior = prior_reasons()
    todo = []
    for pid, old_reason in sorted(prior.items()):
        row = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()
        if row is None:
            continue  # deleted this sprint (the Pere placeholder)
        current = (row[0] or "").strip()
        if old_reason in current:
            continue  # history intact
        todo.append((pid, old_reason, current))
    return todo


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        todo = plan(conn)
        for pid, old_reason, current in todo:
            print(f"{pid}\n    recover: {old_reason[:88]}\n    before : {current[:88]}")
        print(f"\n{len(todo)} record(s) would have their prior updated_reason restored, prepended oldest-first")
        if not todo:
            print("nothing to recover")
            return 0
        if not do_apply:
            print("PLANNED (dry run; nothing written). Re-run with --apply to write.")
            return 0
        conn.execute("BEGIN")
        for pid, old_reason, current in todo:
            conn.execute("UPDATE records SET updated_reason = ? WHERE id = ?",
                         (f"{old_reason} | {current}" if current else old_reason, pid))
        # Verify inside the transaction, before committing.
        #
        # This block used to assert `old in f"{old} | {current}"`, which is
        # true by construction and could not fail -- a verification step that
        # cannot discriminate, which is the "a test that cannot fail is worse
        # than no test" rule applied outside a test file (PR #30 round-2
        # review, 2026-09-23). It now re-reads each row and checks two things
        # the write could actually get wrong: that the row CHANGED at all
        # (an UPDATE matching nothing is silent), and that the stored value
        # is exactly what was intended for THAT id -- catching a mismatched
        # pairing, which substring containment would not.
        bad = []
        for pid, old_reason, current in todo:
            row = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()
            got = (row[0] if row else None) or ""
            expected = f"{old_reason} | {current}" if current else old_reason
            if got != expected or got == current:
                bad.append(pid)
        if bad:
            conn.execute("ROLLBACK")
            print(f"NOT APPLIED: {len(bad)} row(s) did not verify: {bad}", file=sys.stderr)
            return 1
        conn.execute("COMMIT")
        regenerate(conn, EXPORT_DIR)
        print(f"recovered {len(todo)} record(s); export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
