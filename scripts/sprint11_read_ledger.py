#!/usr/bin/env python3
"""Sprint 11: the one read ledger for Tasks E, F and G (F91, F97, F96).

Team lead, 2026-10-21: "these can run by up to 5 agents ... no 2 'read's
should impact the same record." The ledger gives every record this sprint
reads to exactly one group, each group to one task, and each group one
first-pass reader. At most 5 readers run at once (the parallel-reading task
pattern, `.claude/model_assignment_heuristics.json`); the groups are read in
waves. `tests/test_sprint11_read_ledger.py` fails if any record is in two
groups, and each reading script refuses a reader file whose records are not
its group's.

Readers never fetch: every file named here is already local (fetched by the
one serial fetcher, `scripts/sprint11_f96_downloads.py`, or held before). A
record with no local copy goes to `no_copy` with its reason, never to a
reader.

Usage:
  python scripts/sprint11_read_ledger.py --task G --download-log <file>
      adds Task G's slice in groups of GROUP_SIZE (file paths from
      `store.recheck.local_pdf`, else from the download log's "saved" lines)
  python scripts/sprint11_read_ledger.py --task F --records <json file>
      adds Task F's records (a list of {"record_id", "file"}) in groups
Writes `manifests/sprint11_read_ledger.json`. Refuses to add a record that
any existing group already holds.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, recheck, script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
LEDGER = ROOT / "manifests" / "sprint11_read_ledger.json"
SLICE = ROOT / "manifests" / "sprint11_f96_slice.json"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
GROUP_SIZE = 8
MAX_PARALLEL = 5
_SAVED = re.compile(r"^saved\s+(\S+)\s+(.+?\.pdf)\s+SHA-256")


def load() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"rule": ("one record, one group, one reader; at most %d readers at once (team lead 2026-10-21)"
                     % MAX_PARALLEL), "groups": {}, "no_copy": {}}


def held(ledger: dict) -> set[str]:
    out = set(ledger["no_copy"])
    for g in ledger["groups"].values():
        out.update(r["record_id"] for r in g["records"])
    return out


def duplicates(ledger: dict) -> list[str]:
    """Record ids that appear more than once across groups and no_copy."""
    seen, dup = set(), []
    for g in ledger["groups"].values():
        for r in g["records"]:
            if r["record_id"] in seen:
                dup.append(r["record_id"])
            seen.add(r["record_id"])
    dup.extend(rid for rid in ledger["no_copy"] if rid in seen)
    return dup


def saved_files(log: Path) -> dict[str, Path]:
    out = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        m = _SAVED.match(line)
        if m:
            out[m.group(1)] = PAPERS / m.group(2)
    return out


def add_groups(ledger: dict, task: str, rows: list[dict]) -> int:
    taken = held(ledger)
    clash = [r["record_id"] for r in rows if r["record_id"] in taken]
    if clash:
        raise SystemExit(f"refused: {len(clash)} records already in the ledger, e.g. {clash[:3]}")
    n = len(ledger["groups"])
    for i in range(0, len(rows), GROUP_SIZE):
        n += 1
        ledger["groups"][f"g{n:02d}"] = {"task": task, "records": rows[i:i + GROUP_SIZE]}
    return n


def task_g_rows(log: Path | None) -> tuple[list[dict], dict[str, str]]:
    saved = saved_files(log) if log else {}
    slice_ids = [row["record_id"] for row in json.loads(SLICE.read_text(encoding="utf-8"))["slice"]]
    rows, missing = [], {}
    conn = connect(DB_PATH)
    try:
        for rid in slice_ids:
            access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
            parsed = citations.parse_access(access or "")
            path = recheck.local_pdf(access, parsed[1] if parsed else rid) or saved.get(rid)
            if path and Path(path).is_file():
                rows.append({"record_id": rid, "file": Path(path).as_posix()})
            else:
                missing[rid] = "no local copy: no free copy known to OpenAlex, or the fetch failed (section 32)"
    finally:
        conn.close()
    return rows, missing


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    task = args[args.index("--task") + 1]
    ledger = load()
    if task == "G":
        log = Path(args[args.index("--download-log") + 1]) if "--download-log" in args else None
        rows, missing = task_g_rows(log)
        ledger["no_copy"].update(missing)
    else:
        rows = json.loads(Path(args[args.index("--records") + 1]).read_text(encoding="utf-8"))
    n = add_groups(ledger, task, rows)
    assert not duplicates(ledger)
    LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"task {task}: {len(rows)} records in groups up to g{n:02d}; no copy: {len(ledger['no_copy'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
