#!/usr/bin/env python3
"""Re-derive every paper's citation from the source of record and DIFF it
against the store (Sprint 4 Task B, F25 C1; the mechanism F24 proposed).

For each paper whose `access` carries an arXiv id or DOI, fetch the
bibliographic record (store.citations), render the house-style citation,
and compare with `records.provenance`. Papers without a resolvable id are
listed as such -- those are the hand-transcribed exceptions and stay
human-owned.

DRY-RUN BY DEFAULT (QUALITY_STANDARDS.md): prints a per-paper report and
writes nothing. `--apply` updates `records.provenance` (the citation) and
`records.value` (the title) for every DIFFERS row, with a dated
`updated_reason` naming the provider, then regenerates the export. It never
touches papers it could not resolve, and it never auto-applies when the
fetched title is empty.

This is also the periodic check: run it each delivery cycle (Phase 1.3
design-doc currency) so a preprint that has since been published, or a
citation someone hand-edited, is caught then rather than by a reviewer a
year later.

Usage:
    python scripts/refresh_citations.py                 # report only
    python scripts/refresh_citations.py --ids a,b,c     # subset
    python scripts/refresh_citations.py --apply         # write DIFFERS rows
    python scripts/refresh_citations.py --json out.json # machine-readable report
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

# Injected in tests; the real run uses a paced network fetcher.
FETCHER = None


def review(conn, ids: list[str] | None = None, fetcher=None) -> list[dict]:
    fetcher = fetcher or FETCHER or citations.PacedFetcher()
    rows = conn.execute(
        "SELECT r.id, r.value, r.provenance, p.access FROM records r JOIN paper_fields p ON p.record_id = r.id "
        "WHERE r.class = 'paper' ORDER BY r.id"
    ).fetchall()
    out: list[dict] = []
    # Batch arXiv ids into one request (arXiv's id_list) to respect its pacing.
    wanted = [(r["id"], citations.parse_access(r["access"])) for r in rows if not ids or r["id"] in ids]
    arxiv_ids = [ident for _, parsed in wanted if parsed and parsed[0] == "arxiv" for ident in [parsed[1]]]
    arxiv_cache: dict[str, citations.Metadata] = {}
    if arxiv_ids:
        try:
            arxiv_cache = citations.fetch_arxiv_batch(arxiv_ids, fetcher)
        except Exception as ex:  # noqa: BLE001 -- reported per paper below
            arxiv_cache = {"__error__": ex}  # type: ignore[dict-item]
    by_id = {r["id"]: r for r in rows}
    for pid, parsed in wanted:
        r = by_id[pid]
        entry = {"id": pid, "access": r["access"], "stored_citation": r["provenance"], "stored_value": r["value"]}
        if parsed is None:
            entry.update(status="NO-ID")
            out.append(entry)
            continue
        kind, ident = parsed
        try:
            if kind == "arxiv":
                if "__error__" in arxiv_cache:
                    raise arxiv_cache["__error__"]  # type: ignore[misc]
                if ident not in arxiv_cache:
                    raise LookupError(f"arXiv {ident}: no entry returned")
                md = arxiv_cache[ident]
            else:
                md = citations.fetch_doi(ident, fetcher)
        except Exception as ex:  # noqa: BLE001
            entry.update(status="ERROR", error=str(ex), kind=kind, ident=ident)
            out.append(entry)
            continue
        rendered = citations.render_citation(md)
        provider = md.extra.get("provider") or ("arXiv" if kind == "arxiv" else "Crossref/DataCite")
        if kind == "arxiv" and provider != "arXiv":
            provider = f"{provider} (arXiv API refused)"
        entry.update(kind=kind, ident=ident, fetched_citation=rendered, fetched_title=md.title, provider=provider,
                     status="SAME" if rendered == r["provenance"] and md.title == r["value"] else "DIFFERS")
        out.append(entry)
    return out


def apply(conn, report: list[dict], today: str | None = None) -> int:
    today = today or date.today().isoformat()
    n = 0
    for e in report:
        if e["status"] != "DIFFERS" or not e.get("fetched_title"):
            continue
        reason = (f"{today}: citation and title re-derived from {e['kind']}:{e['ident']} via {e['provider']} "
                  f"(scripts/refresh_citations.py); previous citation: {e['stored_citation'][:160]}")
        # A same-day reason already on the row (another correction pass ran
        # first) is kept, not erased: updated_reason answers "why does this
        # row look the way it does today", and two answers are both true.
        existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (e["id"],)).fetchone()[0] or ""
        if existing.startswith(today):
            reason = f"{existing} | {reason}"
        conn.execute(
            "UPDATE records SET provenance = ?, value = ?, updated = ?, updated_reason = ? WHERE id = ?",
            (e["fetched_citation"], e["fetched_title"], today, reason, e["id"]),
        )
        n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    ids = None
    json_out = None
    for i, a in enumerate(args):
        if a == "--ids" and i + 1 < len(args):
            ids = [s.strip() for s in args[i + 1].split(",") if s.strip()]
        if a == "--json" and i + 1 < len(args):
            json_out = Path(args[i + 1])
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        report = review(conn, ids)
        counts = {}
        for e in report:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
            line = f"{e['status']:7s} {e['id']}"
            if e["status"] == "DIFFERS":
                line += f"\n         stored : {e['stored_citation'][:140]}\n         fetched: {e['fetched_citation'][:140]}"
                if e["fetched_title"] != e["stored_value"]:
                    line += f"\n         title  : {e['fetched_title'][:140]}"
            elif e["status"] == "ERROR":
                line += f"  ({e['error']})"
            print(line)
        print(f"\n{len(report)} paper(s): " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        if json_out:
            json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"report written to {json_out}")
        if not do_apply:
            print("PLANNED (dry run; re-run with --apply to write DIFFERS rows)")
            return 0
        n = apply(conn, report)
        conn.commit()
        regenerate(conn, EXPORT_DIR)
        print(f"applied {n} update(s); export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
