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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect, script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
SLICE = ROOT / "manifests" / "sprint13_g_slice.json"
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
WORK = Path(r"C:\Users\kimme\AppData\Local\Temp\claude\D--Data-Harold-github-EvidenceBasedDB\s13g")
# The briefs moved out of Temp with F114's work folder (Sprint 14 Task E, 2026-10-30), where f114_cloud reads them.
BRIEFS = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\briefs")
GROUP_SIZE = 5


def highest_group_number(groups: dict) -> int:
    """The highest N among the ledger's gNNN names, 0 for an empty ledger (F149, Sprint 18 Task A).

    A new group is named from this plus one, never from the group count: with a gap (g001, g003), the count (2)
    would name the next group g003 and overwrite a group a reader already answers. `batch_read.next_group` uses
    the same max rule (it skips a non-gNNN name; this refuses one). A name that is not gNNN is refused rather than skipped, so a hand-named group cannot hide.
    """
    numbers = []
    for name in groups:
        m = re.fullmatch(r"g(\d+)", name)
        if not m:
            raise ValueError(f"a ledger group name is not gNNN: {name!r}")
        numbers.append(int(m[1]))
    return max(numbers, default=0)


def new_groups(groups: dict, rows: list[dict]) -> list[str]:
    """Add `rows` to `groups` in new groups of GROUP_SIZE, named above the highest gNNN; return the new names.

    `main()` names groups only through this function, so its test covers the line that names them (the fresh-eyes
    review of Task A: a test of `highest_group_number` alone stayed green with `main()` back on the count).
    """
    start = highest_group_number(groups)
    names = []
    for i in range(0, len(rows), GROUP_SIZE):
        name = f"g{start + i // GROUP_SIZE + 1:03d}"
        groups[name] = {"records": [{"record_id": r["record_id"], "file": r["file"]} for r in rows[i:i + GROUP_SIZE]]}
        names.append(name)
    return names


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
    new_names = new_groups(groups, rows)
    held = [r["record_id"] for g in groups.values() for r in g["records"]]
    if len(held) != len(set(held)):
        print("a record is held twice; nothing written")
        return 1
    LEDGER.write_text(json.dumps({"rule": "one record, one group, one reader; at most 5 readers at once (team lead "
                                          "2026-10-21); every paper read in full, no budget (team lead 2026-10-25)",
                                  "groups": groups}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    BRIEFS.mkdir(parents=True, exist_ok=True)
    (WORK / "reads").mkdir(parents=True, exist_ok=True)
    for name in new_names:  # an existing group's brief is never rewritten
        g = groups[name]
        brief = {"group": name, "records": [{**r, "stored_assertions": stored[r["record_id"]]} for r in g["records"]]}
        (BRIEFS / f"{name}.json").write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
    first = sum(1 for r in rows if rank(r)[0] == 0)
    print(f"{len(rows)} records added in {len(new_names)} new groups of up to {GROUP_SIZE} ({first} with a theoretical "
          f"LOW first); {len(groups)} groups in all; briefs in {BRIEFS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
