#!/usr/bin/env python3
"""Sprint 15 Manual Validation: the team lead's decisions that change stored
rows outside a group review (INTAKE_WORKFLOW.md section 67).

Team lead, 2026-11-04, answering the hand-over:
  - Q2 = 1: the 10 LOW grades F129 found resting only on a textbook fact
    (`manifests/sprint15_f129_proposals.json` `propose_high`) are set HIGH,
    each on the basis the proposal names.
  - Q4: g144's two absence items are MODERATE ("Make both MEDIUM, as the
    reviewer graded them, because neither paper states the absence
    itself"). The store spells MEDIUM `moderate`. The review enters them at
    the reviewer's LOW; this script raises them one level.
  - Q6 = 2: dell-anna-2025's qng-study-scope-toy-model moves from context
    `method` to `qc`.
Q1's 36 certainty changes went through the group reviews' escalation files,
not here; Q3 = 2 keeps dees-2023's five LOWs, so nothing is written for it.

Each change sets only the named column and appends a note naming the
decision. DRY RUN BY DEFAULT; `--apply` takes a verified backup first.
Idempotent: a second apply finds nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import BASES  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
# The day it is applied (the decisions are of 2026-11-04). A later day than the reviews' 2026-11-04 is what keeps a
# rerun of full_read_apply.py off these rows: sync_assertion refuses a sync dated before a row's last change.
TODAY = "2026-11-05"
TAG = "Sprint 15 Manual Validation"
F129 = ROOT / "manifests" / "sprint15_f129_proposals.json"
ABSENCE = ("gilfuster-no-experiments", "giordano-no-hardware-run-scope")
CONTEXT_MOVE = ("qng-study-scope-toy-model", "method", "qc")


def f129_targets() -> dict[str, tuple[str, str]]:
    """id -> (basis, why) for each proposed HIGH; the basis is the proposal's "Basis: <basis>." (one proposal adds a
    sentence after it)."""
    out = {}
    for aid, why in json.loads(F129.read_text(encoding="utf-8"))["propose_high"].items():
        m = re.search(r"Basis: ([a-z ]+)\.", why)
        if not m or m.group(1) not in BASES:
            raise ValueError(f"{aid}: the proposal names no basis in {sorted(BASES)}")
        out[aid] = (m.group(1), why.strip())
    return out


def planned(conn) -> list[tuple[str, str, str, str]]:
    """(id, column, new value, note) for each change the store does not yet hold."""
    out = []
    for aid, (basis, why) in f129_targets().items():
        row = conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?", (aid,)).fetchone()
        if row is None:
            raise ValueError(f"{aid}: not in the store")
        if row[0] != "high":
            reasons = (f"{row[1]} UPGRADED to HIGH on {basis}, the team lead's decision at {TAG} (Q2), {TODAY}: it "
                       f"rests only on a textbook fact, which F117's cross-group rule does not count as a reason for "
                       f"LOW (F129). {why}")
            out.append((aid, "high", reasons, f"{TODAY} ({TAG}, Q2 = 1, F129): LOW to HIGH on {basis}"))
    for aid in ABSENCE:
        row = conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?", (aid,)).fetchone()
        if row is None:
            raise ValueError(f"{aid}: not in the store; apply g144's review first")
        if row[0] != "moderate":
            reasons = (f"{row[1]} Set MODERATE, the team lead's decision at {TAG} (Q4), {TODAY}: neither paper "
                       f"states the absence itself; the full read found none (an absence claim stands on its search, "
                       f"ADR-0004 decision Q5)")
            out.append((aid, "moderate", reasons, f"{TODAY} ({TAG}, Q4): {row[0].upper()} to MODERATE"))
    aid, old, new = CONTEXT_MOVE
    have = {r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (aid,))}
    if old in have:
        out.append((aid, "context", new, f"{TODAY} ({TAG}, Q6 = 2): context {old} to {new}, as its full reader read it"))
    elif new not in have:
        raise ValueError(f"{aid}: holds neither {old} nor {new}")
    return out


def apply_changes(conn) -> list[str]:
    log = []
    for aid, column, value, note in planned(conn):
        if column == "context":
            conn.execute("UPDATE record_contexts SET context_id = ? WHERE record_id = ? AND context_id = ?",
                         (value, aid, CONTEXT_MOVE[1]))
        else:
            conn.execute("UPDATE records SET certainty = ?, certainty_reasons = ? WHERE id = ?", (column, value, aid))
        append_updated_reason(conn, aid, note, TODAY)
        log.append(f"{column:8} {aid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    if "--apply" not in args:
        try:
            rows = planned(conn)
        finally:
            conn.close()
        for aid, column, _, note in rows:
            print(f"would set {column:8} {aid}  [{note}]")
        print(f"{len(rows)} changes. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    conn.close()
    backup_before_write(DB_PATH, "Sprint 15 Manual Validation decisions")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log) if log else "nothing to write")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
