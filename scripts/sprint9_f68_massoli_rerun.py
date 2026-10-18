#!/usr/bin/env python3
"""Sprint 9 Task B (F68): the five Massoli entries the door refused on
2026-10-12, re-run through F61's own parsing and classification now that
`parse_access` reads old-style arXiv ids and DOIs with parentheses.

Only these five entries are processed, so no other entry is re-searched on
Crossref. F61's module is reused for `parse`, `identifiers`, `classify` and
`entry_for`; its date and tag are set to this task's, so each record says
when and why it entered. ARXIV: the door's paced fetcher, 18 s apart, inside
F52's cap (three requests). DRY-RUN BY DEFAULT; `--apply` takes a verified
backup first. `--list <file>` reads a saved copy of allPapers.md.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

_spec = importlib.util.spec_from_file_location("f61", Path(__file__).with_name("sprint8_f61_massoli_list.py"))
f61 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f61)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
f61.TODAY = "2026-10-15"
f61.TAG = "Sprint 9 Task B, F68"

REFUSED = {"quant-ph/0405098", "quant-ph/0107012", "quant-ph/0001106",
           "10.1016/s0020-0255(00)00055-4", "10.1016/0304-4149(89)90040-9"}


def the_five(entries: list[dict], idx: dict, fetcher) -> list[dict]:
    """The three old-style arXiv entries carry their ids in the list. The two
    DOIs came from F61's exact-title Crossref search (the entries carry
    none), so the entries with no identifier that are not in the store are
    searched again, as F61 did, and kept when the search returns one of them."""
    out = []
    for e in entries:
        arxiv, doi = f61.identifiers(e)
        if arxiv.lower() in REFUSED or doi.lower() in REFUSED:
            out.append(e)
        elif not arxiv and not doi and e["title"] and not f61.match(e, "", "", idx)[0]:
            try:
                found = f61.crossref_doi(e["title"], fetcher)
            except Exception as ex:  # noqa: BLE001 -- reported; the count check below stops the run
                print(f"  Crossref search failed for {e['title'][:60]!r} ({type(ex).__name__})")
                continue
            if found.lower() in REFUSED:
                out.append(e)
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    failures: list[str] = []
    try:
        fetcher = citations.PacedFetcher()
        idx = f61.store_index(conn)
        entries = the_five(f61.parse(f61.load_list(args)), idx, fetcher)
        print(f"{len(entries)} of the 5 refused entries found in the list")
        if len(entries) != len(REFUSED):
            print("expected 5; stopping")
            return 1
        f61.classify(entries, idx, fetcher)
        for e in entries:
            print(f"  {e['cls']:9} {e['record'] or '-'}  ({e['reason']})")
        to_enter = [e for e in entries if e["cls"] == "enter"]
        if apply:
            backup_before_write(DB_PATH, "F68 Massoli five re-run")
        done, skipped, failures = f61.intake.intake(conn, [f61.entry_for(e, e["record"]) for e in to_enter], apply,
                                                    f61.TODAY, fetcher)
        if apply:
            conn.commit()
        print(f"entered {done}, already present {skipped}, refused by the door {len(failures)}")
        for f in failures:
            print(f"  refused: {f}")
    finally:
        conn.close()
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
