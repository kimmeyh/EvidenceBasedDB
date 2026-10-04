#!/usr/bin/env python3
"""Sprint 6 Task I (F33): the six author-withdrawn arXiv preprints and the
one retracted journal article, entered as first-class facts (ADR-0005 A4 (a)).

Each record enters through the door at `seen`, then carries:
- `publication_status` from its source of truth (arXiv's own record for a
  withdrawal; Crossref's retraction NOTICE for the retraction, found with
  the `updates:` filter because the article's own record does not say so);
- the stated reason, quoted from arXiv's comment or named by the notice, in
  `evidence`;
- `found_via`: the QMLPapers list it was found on (the six are in
  `failed-downloads.txt`, never in a `manifest.tsv`; the retraction is in
  `NonArxiv/not-openly-available.txt`);
- a `superseded-by` source link where the comment names the replacement
  (two of the six), the replacement entered first if it is not in the store.

DRY-RUN BY DEFAULT. `--apply` takes a verified backup and commits per record.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import add_source_link, insert_paper, record_probe  # noqa: E402
from store.probes import _arxiv_entry, probe_doi  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
QML = "QMLPapers"

# (arXiv id, folder whose failed-downloads.txt lists it, superseding arXiv id or None), from F33's card.
WITHDRAWN = [
    ("2308.08167", "2023", "2405.13351"),
    ("2304.05672", "2023", "2210.14450"),
    ("2409.10932", "2024", None),
    ("2403.17444", "2024", None),
    ("2410.03853", "2024", None),
    ("2503.23408", "2025", None),
]
RETRACTED_DOI = "10.1007/s00500-022-07037-4"


def present(conn, kind: str, ident: str) -> str | None:
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields WHERE access LIKE ?", (f"%{ident}%",)):
        if citations.parse_access(access) == (kind, ident):
            return rid
    return None


def enter(conn, entry: dict, today: str, apply: bool) -> str:
    """Insert through the door unless present; return the record id."""
    kind, ident = citations.parse_access(entry["access"])
    rid = present(conn, kind, ident)
    if rid:
        return rid
    record = intake.build_record(entry, fetcher=citations.PacedFetcher(), today=today)
    if apply:
        insert_paper(conn, record)
    return record.id


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    today = date.today().isoformat()
    if apply:
        backup_before_write(DB_PATH, "sprint6 task I withdrawn and retracted")
    conn = connect(DB_PATH)
    fetcher = citations.PacedFetcher()
    try:
        for ident, folder, successor in WITHDRAWN:
            got = _arxiv_entry(ident, fetcher)
            if got is None:
                print(f"REPORT arXiv:{ident}: arXiv returned no entry; nothing written")
                continue
            comment = got[0]
            withdrawn = "withdraw" in comment.lower()
            route = f"{QML}/{folder}/failed-downloads.txt"
            rid = enter(conn, {
                "access": f"arXiv:{ident}", "context": "qml",
                "disposition": "Withdrawn by its authors on arXiv; kept as a record so it is never cited as live "
                               "evidence (F33)",
                "evidence": f"arXiv comment, read {today}: \"{comment}\". The PDF returns HTTP 404; /abs returns 200.",
                "found_via": route}, today, apply)
            print(f"{'WRITE' if apply else 'PLAN '} {rid}: withdrawn={withdrawn}; comment: {comment[:140]}")
            if not withdrawn:
                print(f"REPORT {rid}: the comment does not say withdrawn; status NOT recorded")
                continue
            if apply:
                record_probe(conn, rid, "publication_status", "withdrawn", "arXiv", today)
            if successor:
                srid = enter(conn, {
                    "access": f"arXiv:{successor}", "context": "qml",
                    "disposition": f"Named as the replacement in the arXiv comment of withdrawn arXiv:{ident} (F33); "
                                   "not yet screened",
                    "found_via": f"F33: the arXiv comment of arXiv:{ident}"}, today, apply)
                if apply:
                    add_source_link(conn, rid, srid, "superseded-by", f"arXiv comment on {ident}: \"{comment}\"")
                print(f"      superseded-by {srid}")
            if apply:
                conn.commit()
        r = probe_doi("retracted", RETRACTED_DOI, fetcher)
        notice = next((n for n in r.notes if n.startswith("Crossref retraction notice")), None)
        rid = enter(conn, {
            "access": f"doi:{RETRACTED_DOI}", "context": "qml",
            "disposition": "Retracted by the journal; kept as a record so it is never cited as live evidence (F33)",
            "evidence": f"{notice or 'NO retraction notice found'} (Crossref works?filter=updates:{RETRACTED_DOI}, "
                        f"read {today}). The article's own Crossref record does not carry the retraction.",
            "found_via": f"{QML}/NonArxiv/not-openly-available.txt"}, today, apply)
        status = r.values.get("publication_status")
        print(f"{'WRITE' if apply else 'PLAN '} {rid}: status {status}; {notice}")
        if apply and status == "retracted":
            record_probe(conn, rid, "publication_status", "retracted", "Crossref", today)
        if apply:
            conn.commit()
            regenerate(conn, EXPORT_DIR)
            print("APPLIED; export regenerated")
        else:
            print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
