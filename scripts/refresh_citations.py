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
from store.ingest import PaperRecord, validate_paper  # noqa: E402

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
                # Route by KIND, not by "not arxiv, therefore a DOI". Sprint 4
                # Task G added a third kind (github) and this line kept sending
                # it to fetch_doi, so every repository record reported ERROR
                # with a message telling the operator to re-record it as
                # hand-transcribed (Copilot review of PR #30, 2026-09-22).
                # citations.fetch() dispatches on the kind and raises for an
                # unknown one, so a fourth kind cannot repeat this silently.
                md = citations.fetch(kind, ident, fetcher)
        except Exception as ex:  # noqa: BLE001
            entry.update(status="ERROR", error=str(ex), kind=kind, ident=ident)
            out.append(entry)
            continue
        rendered = citations.render_citation(md)
        provider = md.extra.get("provider") or {"arxiv": "arXiv", "github": "GitHub"}.get(kind, "Crossref/DataCite")
        if kind == "arxiv" and provider != "arXiv":
            provider = f"{provider} (arXiv API refused)"
        # A provider record with no title is an incomplete PROVIDER record, not
        # a difference in the store, and it renders as a citation with an empty
        # quoted title. Classing it DIFFERS let apply() skip it silently while
        # main() reported success (PR #30 review, 2026-09-22). It is an ERROR:
        # the run could not answer the question it was asked.
        if not md.title.strip():
            entry.update(status="ERROR", kind=kind, ident=ident, provider=provider,
                         error=(f"{provider} returned a record with no title for {kind}:{ident}; "
                                "refusing to write a citation with an empty title"))
            out.append(entry)
            continue
        status = "SAME" if rendered == r["provenance"] and md.title == r["value"] else "DIFFERS"
        # A FALLBACK provider can carry LESS than the primary one: DataCite's
        # record for an arXiv DOI has no journal reference, so when arXiv
        # refuses, the re-render drops "Science Advances 9, 45 (2023)" that a
        # previous arXiv-sourced run had captured. Proposing that as a change
        # would quietly trade a richer citation for a poorer one, every time
        # arXiv rate-limits. Report it as POORER and leave the row alone
        # (PR #30 review round, 2026-09-22).
        if status == "DIFFERS" and md.extra.get("provider") == "DataCite" and kind == "arxiv":
            stored_wo = (r["provenance"] or "").replace(md.journal_ref, "") if md.journal_ref else r["provenance"]
            if rendered != stored_wo and _is_subset_of(rendered, r["provenance"]):
                status = "POORER"
                entry["note"] = (f"the fallback provider ({provider}) returned less than the stored citation "
                                 "carries; the store keeps the richer one")
        entry.update(kind=kind, ident=ident, fetched_citation=rendered, fetched_title=md.title, provider=provider,
                     status=status)
        out.append(entry)
    return out


def _is_subset_of(fetched: str, stored: str) -> bool:
    """Every comma-separated element of the fetched citation also appears in
    the stored one: the fetched string says nothing new, only less."""
    if not stored:
        return False
    return all(part.strip() in stored for part in fetched.split(", ") if part.strip())


def _validated(conn, e: dict, citation: str, title: str) -> None:
    """Every row this script writes goes through the SAME door insert_paper
    uses (QUALITY_STANDARDS.md: "Reuse the ingestion path; do not hand-roll a
    second one that happens to look similar"). Added 2026-09-22, PR #30
    review: apply() wrote `records` directly and skipped every validate_paper
    rule, so a provider title containing "NOTE:" or "recorded once" could
    write a citation the door would refuse on the next pass -- a row no
    script could then fix.
    """
    row = conn.execute(
        "SELECT p.tier, p.access, p.disposition, p.evidence, p.mined_by, p.checked_against_source, "
        "(SELECT context_id FROM record_contexts c WHERE c.record_id = ? LIMIT 1) AS context "
        "FROM paper_fields p WHERE p.record_id = ?", (e["id"], e["id"])).fetchone()
    if row is None:
        raise ValueError(f"paper {e['id']!r} has no paper_fields row")
    validate_paper(PaperRecord(
        id=e["id"], tier=row["tier"], access=row["access"], disposition=row["disposition"],
        context=row["context"] or "", value=title, citation=citation, citation_origin="api",
        # The citation being validated came from the API moments ago in review().
        citation_source="api",
        evidence=row["evidence"], mined_by=row["mined_by"],
        checked_against_source=row["checked_against_source"],
        updated=date.today().isoformat(), updated_reason="validation probe",
        applicability=[(r["context_id"], r["rationale"]) for r in conn.execute(
            "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (e["id"],))],
    ))


def apply(conn, report: list[dict], today: str | None = None) -> int:
    """DECIDE, THEN WRITE: every row is validated before any row is written,
    so a refusal on the last row cannot leave the first ones changed."""
    today = today or date.today().isoformat()
    pending = [e for e in report if e["status"] == "DIFFERS"]
    for e in pending:
        _validated(conn, e, e["fetched_citation"], e["fetched_title"])
    n = 0
    for e in pending:
        reason = (f"{today}: citation and title re-derived from {e['kind']}:{e['ident']} via {e['provider']} "
                  f"(scripts/refresh_citations.py); previous citation: {e['stored_citation'][:160]}")
        # APPEND-ONLY. updated_reason is the row's own account of why it looks
        # the way it does; the date-gated form of this line destroyed 44
        # records' history in Task C (PR #30 review finding 1). Guarded by
        # tests/test_updated_reason_is_append_only.py.
        existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (e["id"],)).fetchone()[0] or ""
        if existing:
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
            if e["status"] in ("DIFFERS", "POORER"):
                line += f"\n         stored : {e['stored_citation'][:140]}\n         fetched: {e['fetched_citation'][:140]}"
                if e["fetched_title"] != e["stored_value"]:
                    line += f"\n         title  : {e['fetched_title'][:140]}"
                if e.get("note"):
                    line += f"\n         note   : {e['note']}"
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
        # EXPLICIT transaction. Python's legacy sqlite3 mode happens to wrap
        # these UPDATEs today, so an exception before commit() unwinds them --
        # but that is an accident of the default, and the same default is what
        # made a SAVEPOINT commit per entry in Sprint 3. State it instead.
        conn.execute("BEGIN")
        try:
            n = apply(conn, report)
        except Exception:
            conn.execute("ROLLBACK")
            raise
        conn.execute("COMMIT")
        regenerate(conn, EXPORT_DIR)
        errors = [e for e in report if e["status"] == "ERROR"]
        print(f"applied {n} update(s); export regenerated")
        if errors:
            print(f"warning: {len(errors)} paper(s) could not be resolved and were NOT updated: "
                  + ", ".join(e["id"] for e in errors), file=sys.stderr)
            return 1
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
