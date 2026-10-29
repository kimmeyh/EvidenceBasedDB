#!/usr/bin/env python3
"""Sprint 13 Task G (F113): the one read ledger for the full re-read, and each group's brief.

The ledger rules of Sprints 11 to 13: one record, one group, one first-pass
reader, at most 5 readers at once. From `manifests/sprint13_g_slice.json`'s
`local` bucket (re-run the slice after the downloads, so a fetched copy
counts). Groups of 5 papers, since each paper is now read whole.

A re-run only appends: records the ledger already holds keep their group,
and an existing group's brief is never rewritten.

Order: first the records whose stored assertions hold a theoretical result
kept LOW for want of its statement (a full read can quote it), then the
records not yet at `read`, then the rest; by record id inside each.

The ledger (`manifests/sprint13_g_ledger.json`, committed) holds record ids
and files only. Each group's brief, with the record's stored assertions for
its reader to confirm or correct, is store content, so it is written to
WORK outside git, never committed (CLAUDE.md: git holds code and documents).

Usage:
  python scripts/sprint13_g_ledger.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
SLICE = ROOT / "manifests" / "sprint13_g_slice.json"
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
WORK = Path(r"C:\Users\kimme\AppData\Local\Temp\claude\D--Data-Harold-github-EvidenceBasedDB\s13g")
GROUP_SIZE = 5


def stored_assertions(conn, rid: str) -> list[dict]:
    rows = conn.execute(
        "SELECT r.id, r.value, f.citation_context, r.certainty, r.certainty_reasons, rc.context_id "
        "FROM paper_yields y JOIN records r ON r.id = y.assertion_id "
        "JOIN assertion_fields f ON f.record_id = r.id "
        "LEFT JOIN record_contexts rc ON rc.record_id = r.id "
        "WHERE y.paper_id = ? ORDER BY r.id", (rid,)).fetchall()
    seen, out = set(), []
    for aid, value, cc, certainty, reasons, context in rows:
        if aid in seen:
            continue
        seen.add(aid)
        out.append({"id": aid, "value": value, "quotes_and_anchors": cc, "certainty": certainty,
                    "certainty_reasons": reasons, "context": context})
    return out


def main(argv: list[str] | None = None) -> int:
    rows = [r for r in json.loads(SLICE.read_text(encoding="utf-8"))["slice"] if r["bucket"] == "local"]
    with connect(DB_PATH) as conn:
        stored = {r["record_id"]: stored_assertions(conn, r["record_id"]) for r in rows}

    def rank(r):
        theory = any("theoretical result" in (a["certainty_reasons"] or "") for a in stored[r["record_id"]])
        return (0 if theory else 1 if r["tier"] != "read" else 2, r["record_id"])

    # A ledger already handed to readers is only ever appended to (the fresh-eyes review of a3b8074): a re-run after
    # the downloads, or after reads land, must not renumber a group a reader file already answers.
    groups = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"] if LEDGER.exists() else {}
    already = {r["record_id"] for g in groups.values() for r in g["records"]}
    rows = sorted((r for r in rows if r["record_id"] not in already), key=rank)
    start = len(groups)
    new_names = []
    for i in range(0, len(rows), GROUP_SIZE):
        name = f"g{start + i // GROUP_SIZE + 1:03d}"
        groups[name] = {"records": [{"record_id": r["record_id"], "file": r["file"]} for r in rows[i:i + GROUP_SIZE]]}
        new_names.append(name)
    held = [r["record_id"] for g in groups.values() for r in g["records"]]
    if len(held) != len(set(held)):
        print("a record is held twice; nothing written")
        return 1
    LEDGER.write_text(json.dumps({"rule": "one record, one group, one reader; at most 5 readers at once (team lead "
                                          "2026-10-21); every paper read in full, no budget (team lead 2026-10-25)",
                                  "groups": groups}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (WORK / "briefs").mkdir(parents=True, exist_ok=True)
    (WORK / "reads").mkdir(parents=True, exist_ok=True)
    for name in new_names:  # an existing group's brief is never rewritten
        g = groups[name]
        brief = {"group": name, "records": [{**r, "stored_assertions": stored[r["record_id"]]} for r in g["records"]]}
        (WORK / "briefs" / f"{name}.json").write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
    first = sum(1 for r in rows if rank(r)[0] == 0)
    print(f"{len(rows)} records added in {len(new_names)} new groups of up to {GROUP_SIZE} ({first} with a theoretical "
          f"LOW first); {len(groups)} groups in all; briefs in {WORK / 'briefs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
