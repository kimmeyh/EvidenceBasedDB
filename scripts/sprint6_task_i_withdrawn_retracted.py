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


def _http_status(url: str) -> int | None:
    """The HTTP status a reader gets at `url`, or None if unreachable."""
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": citations.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as err:
        return err.code
    except (urllib.error.URLError, TimeoutError):
        return None


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
    # Paced by the process-wide arXiv clock (store/citations.py, I1).
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
    fetcher = citations.PacedFetcher()  # the process-wide clock paces it (I1)
    try:
        for ident, folder, successor in WITHDRAWN:
            try:
                got = _arxiv_entry(ident, fetcher)
            except Exception as ex:  # noqa: BLE001 -- a withdrawal shows only in arXiv's record; report, never guess
                print(f"REPORT arXiv:{ident}: arXiv did not answer ({str(ex)[:80]}); nothing written. "
                      "DataCite cannot show a withdrawal, so this id waits for arXiv")
                continue
            if got is None:
                print(f"REPORT arXiv:{ident}: arXiv returned no entry; nothing written")
                continue
            comment = got[0]
            # The source of truth for a withdrawal is arXiv's own signature, as
            # F33 verified on 2026-09-18: /abs answers 200 and /pdf 404. The
            # comment carries the stated REASON and often never says
            # "withdrawn" ("This a duplicated upload by mistake"). Paced like
            # every arXiv request (6 s).
            # Through the run's pacer, so the NEXT arXiv request is also
            # measured from this one (Sprint 6 Phase 5 review).
            fetcher.wait_for(f"https://arxiv.org/pdf/{ident}")
            pdf_status = _http_status(f"https://arxiv.org/pdf/{ident}")
            withdrawn = pdf_status == 404 or "withdraw" in comment.lower()
            route = f"{QML}/{folder}/failed-downloads.txt"
            rid = enter(conn, {
                "access": f"arXiv:{ident}", "context": "qml",
                # The Lin duplicate and its replacement share first author,
                # year and title, so the derived ids collide; the withdrawn
                # copy carries its own arXiv number instead.
                **({"id": "lin-2023-implementing-arbitrary-quantum-operations-2304-05672"}
                   if ident == "2304.05672" else {}),
                "disposition": "Withdrawn by its authors on arXiv; kept as a record so it is never cited as live "
                               "evidence (F33)",
                "evidence": f"arXiv comment, read {today}: \"{comment}\". arxiv.org/pdf/{ident} answered HTTP {pdf_status} on {today}; the API still returns the /abs record.",
                "found_via": route}, today, apply)
            print(f"{'WRITE' if apply else 'PLAN '} {rid}: pdf HTTP {pdf_status}; withdrawn={withdrawn}; comment: {comment[:100]}")
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
                # Idempotent on re-run: source_links' key is (from, to, type).
                if apply and not conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND "
                                              "link_type = 'superseded-by'", (rid, srid)).fetchone():
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
            print("APPLIED")
        else:
            print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
