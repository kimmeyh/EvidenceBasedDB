#!/usr/bin/env python3
"""Back-fill the STORED ADR-0005 A4 fields from text the store already
holds (Sprint 6 Task F, F36 "re-processing existing papers").

Never guesses. Each value is transcribed from an existing field, and a
record whose text does not say is reported and left alone:

- `found_via` (field 1): from the disposition's or the history's own words
  ("Bulk intake ... HSBC Phase 2 bibliography [TAG]", "F5's QCi author
  search (<person>, <rule>)", "QCi site scrape", the Sprint 1 seed note,
  and five named one-offs).
- `cited_as` (field 8): for the bibliography route, the entry's citation
  paragraph from the preserved BIBLIOGRAPHY.md, verbatim (whitespace
  collapsed), without its reading note.
- `metadata_provider` (field 10): the LAST provider the history names
  ("metadata from DataCite", "via Crossref"); an api-origin record whose
  history names none gets the registry its access kind implies, and its
  updated_reason says it was inferred. A hand-origin record has none.
- `read_extent` (field 2), for the records already at `read` only: from
  `checked_against_source`, which names the reader, the date and the
  pages. A subagent's whole-paper extraction is its own row.

Judgment fields are QUEUED, never filled: `read_extent` for records below
`read`, and a disclosed `coi` for every record. The queue is printed, not
stored (it is a query).

DRY-RUN BY DEFAULT. `--apply` takes a verified backup first, writes in one
transaction, appends to every touched record's updated_reason, and
regenerates the export.

Usage:
    python scripts/backfill_reference_fields.py            # plan only
    python scripts/backfill_reference_fields.py --apply
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import add_found_via, add_read, append_updated_reason  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
BIBLIOGRAPHY = Path(r"D:\Data\Harold\EvidenceBasedDB\References\2026-09_HSBC-Phase2-research_BIBLIOGRAPHY.md")

# Routes the history states in prose rather than in a pattern; each quotes
# the phrase it rests on.
ONE_OFFS = {
    "lenat-marcus-2023-trustworthy-ai": ("Sprint 1 Task E premise-falsifier paper",
                                         "Sprint 1 Task E: premise-falsifier dry run"),
    "neven-2012-qboost-adiabatic-quantum-optimization": ("Sprint 2 Task C spot-check (seed directory)",
                                                         "added 2026-09-17 (Sprint 2 Task C spot-check)"),
    "mancilla-2026-linkedin-merlin-reproduces-18-qml-papers": ("F12 example 1 (Sprint 4 Task G)", "F12 example 1"),
    "notton-2026-merlin-discovery-engine-photonic-hybrid": ("F12 example 2 (Sprint 4 Task G)", "F12 example 2"),
    "merlinquantum-merlin-github-repo": ("F12 example 3 (Sprint 4 Task G)", "F12 example 3"),
}
_BIB_TAG = re.compile(r"HSBC Phase 2 bibliography \[([A-Z]+-\d+)\]")
_F5_AUTHOR = re.compile(r"F5's QCi author search \(([^,)]+), ([^,)]+)")
_F5_SITE = re.compile(r"QCi site scrape (\d{4}-\d{2}) \(F5 sub-part (\d)\), ([\w/-]+)")
_F5_PACKAGE = re.compile(r"QCi software package \S+ \(F5 sub-part (\d)\)")
# "Crossref/DataCite" first: refresh_citations.py wrote it when a DOI's
# provider was not recorded, and it must not be read as "Crossref".
_PROVIDER = re.compile(r"(?:metadata from|via) (Crossref/DataCite|DataCite|arXiv|Crossref|GitHub)\b")
_ENTRY = re.compile(r"^\*\*\[([A-Z]+-\d+)\]\*\*\s*(.*?)(?=^>|^\*\*\[|^---|^##|\Z)", re.S | re.M)


def bibliography_citations(path: Path = BIBLIOGRAPHY) -> dict[str, str]:
    """{tag: the entry's citation paragraph}, the reading note (`>` lines) excluded."""
    text = path.read_text(encoding="utf-8")
    return {m.group(1): " ".join(m.group(2).split()) for m in _ENTRY.finditer(text)}


def route_of(record_id: str, disposition: str, history: str) -> tuple[str, str] | None:
    """(route, the phrase it was read from), or None when the text does not say."""
    if record_id in ONE_OFFS:
        route, phrase = ONE_OFFS[record_id]
        return (route, phrase) if phrase in history or phrase in disposition else None
    if m := _BIB_TAG.search(disposition):
        return f"HSBC Phase 2 bibliography [{m.group(1)}]", m.group(0)
    if m := _F5_AUTHOR.search(disposition):
        return f"F5 QCi author search ({m.group(1)}, {m.group(2)})", m.group(0)
    if m := _F5_SITE.search(disposition):
        return f"F5 QCi site scrape {m.group(1)}, {m.group(3)}", m.group(0)
    if m := _F5_PACKAGE.search(disposition):
        return f"F5 QCi software packages (sub-part {m.group(1)})", m.group(0)
    if history.startswith("Sprint 1 Task F: 46-paper seed set"):
        return "Sprint 1 seed set (46 papers)", "Sprint 1 Task F: 46-paper seed set"
    return None


def provider_of(access: str, history: str) -> tuple[str | None, str]:
    named = _PROVIDER.findall(history)
    if named:
        return named[-1], "named in the record's history"
    parsed = citations.parse_access(access)
    if parsed is None:
        return None, "hand-origin: no registry"
    # A DOI is tried at Crossref, then DataCite, and which one answered was
    # not recorded before A4: say both, as refresh_citations.py does.
    return {"arxiv": "arXiv", "doi": "Crossref/DataCite", "github": "GitHub"}[parsed[0]], \
        f"inferred from the {parsed[0]} access id; the history names no provider"


_CAS = re.compile(r"^(\d{4}-\d{2}-\d{2}), (\w+), (.*)$")


def reads_of(checked: str) -> list[tuple[str, str, str, str]] | None:
    """`read_extent` rows transcribed from checked_against_source, or None
    if it does not name a date, a reader and what was read."""
    m = _CAS.match(checked or "")
    if not m:
        return None
    day, reader, rest = m.groups()
    rows = []
    direct, _, agent = rest.partition("; read-only agent")
    detail = re.sub(r"^read\s+", "", direct)
    detail = re.sub(r"\s+(checked )?directly", "", detail).strip()
    rows.append((reader, day, "partial", detail))
    if agent:
        rows.append(("read-only agent", day, "subagent", "verbatim quotes with pages, whole paper"))
    return rows


def plan(conn) -> dict:
    bib = bibliography_citations()
    have_routes = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_found_via")}
    have_reads = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_reads")}
    out = {"found_via": [], "provider": [], "reads": [], "unrouted": [], "unread": [], "missing_tags": []}
    for r in conn.execute("SELECT p.record_id AS id, p.tier, p.access, p.disposition, p.checked_against_source, "
                          "p.metadata_provider, r.updated_reason FROM paper_fields p "
                          "JOIN records r ON r.id = p.record_id ORDER BY p.record_id"):
        if r["id"] not in have_routes:
            got = route_of(r["id"], r["disposition"], r["updated_reason"])
            if got is None:
                out["unrouted"].append(r["id"])
            else:
                route, phrase = got
                cited = None
                if route.startswith("HSBC Phase 2 bibliography"):
                    tag = route[route.index("[") + 1:-1]
                    cited = bib.get(tag)
                    if cited is None:
                        out["missing_tags"].append((r["id"], tag))
                out["found_via"].append((r["id"], route, cited, phrase))
        if r["metadata_provider"] is None:
            provider, why = provider_of(r["access"], r["updated_reason"])
            if provider:
                out["provider"].append((r["id"], provider, why))
        if r["tier"] == "read" and r["id"] not in have_reads:
            rows = reads_of(r["checked_against_source"])
            (out["reads"].append((r["id"], rows)) if rows else out["unread"].append(r["id"]))
    out["coi_queue"] = conn.execute("SELECT COUNT(*) FROM paper_fields WHERE coi IS NULL").fetchone()[0]
    out["extent_queue"] = [r[0] for r in conn.execute(
        "SELECT record_id FROM paper_fields WHERE tier = 'screened' AND record_id NOT IN "
        "(SELECT record_id FROM paper_reads) ORDER BY record_id")]
    return out


def apply(conn, p: dict, today: str) -> None:
    notes: dict[str, list[str]] = {}
    for rid, route, cited, phrase in p["found_via"]:
        add_found_via(conn, rid, route, cited)
        notes.setdefault(rid, []).append(f"found_via '{route}' (from \"{phrase}\")"
                                         + ("; cited_as from the preserved BIBLIOGRAPHY.md" if cited else ""))
    for rid, provider, why in p["provider"]:
        conn.execute("UPDATE paper_fields SET metadata_provider = ? WHERE record_id = ?", (provider, rid))
        notes.setdefault(rid, []).append(f"metadata_provider {provider} ({why})")
    for rid, rows in p["reads"]:
        for row in rows:
            add_read(conn, rid, *row)
        notes.setdefault(rid, []).append(f"read_extent transcribed from checked_against_source ({len(rows)} row(s))")
    for rid, items in notes.items():
        append_updated_reason(conn, rid, f"{today}: Sprint 6 Task F back-fill (ADR-0005 A4): " + "; ".join(items), today)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not DB_PATH.exists():  # connect() would create an empty store here
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        p = plan(conn)
        routes: dict[str, int] = {}
        for _, route, _, _ in p["found_via"]:
            key = route.split(" [")[0].split(" (")[0]
            routes[key] = routes.get(key, 0) + 1
        providers: dict[str, int] = {}
        for _, provider, why in p["provider"]:
            k = f"{provider} ({'inferred' if why.startswith('inferred') else 'named'})"
            providers[k] = providers.get(k, 0) + 1
        print(f"found_via: {len(p['found_via'])} records {routes}; "
              f"cited_as {sum(1 for x in p['found_via'] if x[2])}; unrouted {len(p['unrouted'])} {p['unrouted']}")
        if p["missing_tags"]:
            print(f"bibliography tags with no entry: {p['missing_tags']}")
        print(f"metadata_provider: {len(p['provider'])} records {providers}")
        for rid, rows in p["reads"]:
            print(f"read_extent {rid}: {rows}")
        print(f"read records whose checked_against_source names no reader/date: {p['unread']}")
        print(f"QUEUED (judgment, not filled): disclosed coi on {p['coi_queue']} records; "
              f"read_extent on {len(p['extent_queue'])} screened records")
        if "--apply" not in args:
            print("\nDRY RUN: nothing written. Re-run with --apply.")
            return 0
        backup_before_write(DB_PATH, "sprint6 task F reference back-fill")
        today = date.today().isoformat()
        apply(conn, p, today)
        conn.commit()
        regenerate(conn, EXPORT_DIR)
        print("APPLIED; export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
