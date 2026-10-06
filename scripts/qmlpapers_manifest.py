#!/usr/bin/env python3
"""Generate the QMLPapers bulk-intake manifest (Sprint 6 Task J, F32;
INTAKE_WORKFLOW section 9: generated from the collection's own TSVs, never
authored by hand).

Reads `QMLPapers/<folder>/manifest.tsv` (outside version control) and the
store (read-only), and writes three files under `manifests/` (Q9):

- `qmlpapers_bulk.json`: one intake entry per arXiv row not already in the
  store: `access` arXiv:<id>, `context` qml, the section 9 disposition,
  `found_via` the TSV it came from, `cited_as` the collection's own title
  line. The title column is otherwise discarded: the door derives the title.
- `qmlpapers_sample.json`: up to 10 entries per folder, spread across each
  folder, for the Q8 dry run.
- `qmlpapers_routes_for_present.json`: rows whose paper is already in the
  store. They are not re-fetched; each gains this route as a second
  `found_via` row (applied by `--add-routes` below).

`NonArxiv/manifest.tsv` has no arXiv id. Its DOI rows join the bulk file
with `access` doi:<doi>; rows with no resolvable id are listed as needing
the hand path and are NOT written (a hand citation needs a transcription
from the document).

Exits non-zero on any arXiv row whose id is absent or malformed. Prints a
reconciliation of every row.

    python scripts/qmlpapers_manifest.py                 # generate and reconcile
    python scripts/qmlpapers_manifest.py --add-routes --apply
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import add_found_via, append_updated_reason  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
QML = Path(r"D:\Data\Harold\EvidenceBasedDB\QMLPapers")
OUT = ROOT / "manifests"
_ID = re.compile(r"^\d{4}\.\d{4,5}$")
MONTH = "2026-10"
SAMPLE_PER_FOLDER = 10


def disposition(folder: str) -> str:
    """INTAKE_WORKFLOW section 9's wording, verbatim."""
    return f"Bulk intake {MONTH} from QMLPapers/{folder}/manifest.tsv (a QML literature collection); not yet screened"


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def present_ids(conn) -> dict[str, str]:
    """{arXiv id or lowercased DOI: record id} for every paper in the store."""
    out = {}
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields"):
        parsed = citations.parse_access(access)
        if parsed and parsed[0] in ("arxiv", "doi"):
            out[parsed[1].lower()] = rid
    return out


def build(conn) -> tuple[list[dict], list[dict], list[str], list[str]]:
    present = present_ids(conn)
    entries, routes, bad, notes = [], [], [], []
    seen: dict[str, str] = {}
    for tsv in sorted(QML.glob("*/manifest.tsv")):
        folder = tsv.parent.name
        route = f"QMLPapers/{folder}/manifest.tsv"
        for n, row in enumerate(_rows(tsv), 2):
            title = " ".join((row.get("title") or "").split()) or None
            if folder == "NonArxiv":
                # Each URL on its own: joined, the string ends in ".pdf" and
                # parse_access rightly treats it as a document path.
                parsed = next((p for p in (citations.parse_access(row.get(k) or "") for k in ("source_url", "pdf_url"))
                               if p), None)
                if not parsed or parsed[0] != "doi":
                    notes.append(f"{route} line {n}: no DOI or arXiv id; needs the hand path ({row.get('file')})")
                    continue
                key, access = parsed[1].lower(), f"doi:{parsed[1]}"
            else:
                ident = (row.get("arxiv_id") or "").strip()
                if not _ID.match(ident):
                    bad.append(f"{route} line {n}: arxiv_id {ident!r} is absent or malformed")
                    continue
                key, access = ident.lower(), f"arXiv:{ident}"
            if key in seen:
                notes.append(f"{route} line {n}: {access} already listed from {seen[key]}; entered once")
                routes.append({"record_access": access, "route": route, "cited_as": title, "pending": True})
                continue
            seen[key] = route
            if key in present:
                routes.append({"record_id": present[key], "route": route, "cited_as": title})
                continue
            entries.append({"access": access, "context": "qml", "disposition": disposition(folder),
                            "found_via": route, **({"cited_as": title} if title else {})})
    return entries, routes, bad, notes


def sample(entries: list[dict]) -> list[dict]:
    by_folder: dict[str, list[dict]] = {}
    for e in entries:
        by_folder.setdefault(e["found_via"], []).append(e)
    out = []
    for group in by_folder.values():
        step = max(1, len(group) // SAMPLE_PER_FOLDER)
        out += group[::step][:SAMPLE_PER_FOLDER]
    return out


def add_routes(conn, routes: list[dict], today: str) -> int:
    """Second `found_via` rows for papers already in the store. A row whose
    record is identified only by access (a duplicate across TSVs) is
    resolved now, after the load."""
    present = present_ids(conn)
    have = {(r[0], r[1]) for r in conn.execute("SELECT record_id, route FROM paper_found_via")}
    n = 0
    for r in routes:
        rid = r.get("record_id") or present.get(citations.parse_access(r["record_access"])[1].lower())
        if rid is None or (rid, r["route"]) in have:
            continue
        add_found_via(conn, rid, r["route"], r.get("cited_as"))
        append_updated_reason(conn, rid, f"{today} (Sprint 6 Task J): also found via {r['route']}", today)
        have.add((rid, r["route"]))
        n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        if "--add-routes" in args:
            routes = json.loads((OUT / "qmlpapers_routes_for_present.json").read_text(encoding="utf-8"))
            if "--apply" not in args:
                print(f"DRY RUN: {len(routes)} route rows to consider. Re-run with --apply.")
                return 0
            backup_before_write(DB_PATH, "qmlpapers add routes")
            today = date.today().isoformat()
            n = add_routes(conn, routes, today)
            conn.commit()
            regenerate(conn, EXPORT_DIR)
            print(f"APPLIED: {n} found_via rows added; export regenerated")
            return 0
        entries, routes, bad, notes = build(conn)
    finally:
        conn.close()
    total = sum(len(_rows(t)) for t in QML.glob("*/manifest.tsv"))
    for line in notes:
        print("NOTE", line)
    for line in bad:
        print("BAD ", line)
    hand = sum(1 for x in notes if "hand path" in x)
    dup = sum(1 for x in notes if "entered once" in x)
    present = sum(1 for r in routes if not r.get("pending"))
    print(f"\nrows {total}: new entries {len(entries)}, already in the store {present}, duplicates across TSVs {dup}, "
          f"hand path {hand}, bad {len(bad)} (reconciles: {len(entries) + present + dup + hand + len(bad) == total})")
    if bad:
        return 1
    OUT.mkdir(exist_ok=True)
    for name, data in (("qmlpapers_bulk.json", entries), ("qmlpapers_sample.json", sample(entries)),
                       ("qmlpapers_routes_for_present.json", routes)):
        (OUT / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote manifests/qmlpapers_bulk.json ({len(entries)}), qmlpapers_sample.json ({len(sample(entries))}), "
          f"qmlpapers_routes_for_present.json ({len(routes)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
