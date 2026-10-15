#!/usr/bin/env python3
"""Sprint 2 Task G (F3): an easy, CLI-startable way to view DB content.

Three modes, per the team lead's own request: view by context (title of
every item in that context), view by paper (all data related to the
paper), view by assertion (all applicable data). No server, no web UI --
a `sqlite3`-backed read tool over store/evidence.db directly, output as
plain text or `--json` for scripting. A dashboard is not warranted at
this scale (QUALITY_STANDARDS.md "no speculative abstraction").

Usage:
    python scripts/view.py contexts                    # list all contexts with counts
    python scripts/view.py contexts <context-id>        # list records in one context
    python scripts/view.py paper <paper-id>              # full paper record + its yields
    python scripts/view.py assertion <assertion-id>      # full assertion + its relations
    (add --json to any command for machine-readable output)
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, resolvers, script_paths  # noqa: E402

# Windows consoles commonly default to cp1252, which cannot encode most
# citation text (accents, math symbols). Reconfigure stdout to UTF-8 so
# output does not depend on -- or crash on -- the host console's codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_, DB_PATH, _ = script_paths(__file__)


def _record_title(conn, record_id: str) -> str:
    row = conn.execute("SELECT value FROM records WHERE id = ?", (record_id,)).fetchone()
    return row["value"] if row else "(record not found)"


def cmd_contexts_list(conn) -> dict:
    """`view.py contexts` -- every context with a count of records claiming
    it, via record_contexts (covers every class) plus paper_applicability
    (papers' plural applicability, not just their single primary context --
    the exact undercount F4/Task A corrected)."""
    rows = conn.execute(
        """
        SELECT c.id, c.description,
            (SELECT COUNT(*) FROM record_contexts rc WHERE rc.context_id = c.id) AS direct_count,
            (SELECT COUNT(*) FROM paper_applicability pa WHERE pa.context_id = c.id) AS applicability_count
        FROM contexts c
        ORDER BY c.id
        """
    ).fetchall()
    return {
        "contexts": [
            {
                "id": r["id"],
                "description": r["description"],
                "direct_count": r["direct_count"],
                "applicability_count": r["applicability_count"],
            }
            for r in rows
        ]
    }


def cmd_contexts_detail(conn, context_id: str) -> dict:
    """`view.py contexts <id>` -- every record's id and one-line title
    filed under that context, whether via record_contexts (any class) or
    paper_applicability (a paper that bears on this context beyond its
    single primary one)."""
    exists = conn.execute("SELECT id FROM contexts WHERE id = ?", (context_id,)).fetchone()
    if not exists:
        return {"error": f"no such context: {context_id!r}"}

    direct = conn.execute(
        """
        SELECT r.id, r.class, r.value
        FROM record_contexts rc
        JOIN records r ON r.id = rc.record_id
        WHERE rc.context_id = ?
        ORDER BY r.class, r.id
        """,
        (context_id,),
    ).fetchall()

    applicability = conn.execute(
        """
        SELECT r.id, r.value, pa.rationale
        FROM paper_applicability pa
        JOIN records r ON r.id = pa.record_id
        WHERE pa.context_id = ?
          AND pa.record_id NOT IN (SELECT record_id FROM record_contexts WHERE context_id = ?)
        ORDER BY r.id
        """,
        # Exclude papers already listed directly: the section is "beyond its
        # single primary one" and printed "(not primary context)", but listed
        # primary-context papers a second time (team lead's Manual Validation
        # run, 2026-09-25).
        (context_id, context_id),
    ).fetchall()

    return {
        "context": context_id,
        "records": [{"id": r["id"], "class": r["class"], "value": r["value"]} for r in direct],
        "papers_via_applicability": [
            {"id": r["id"], "value": r["value"], "rationale": r["rationale"]} for r in applicability
        ],
    }


def _schedule(schedule: tuple) -> dict:
    """The re-check schedule as JSON values: section an int, dates ISO or
    None (None for the next date means due now)."""
    section, last, nxt = schedule
    return {"section": section, "last_check": last.isoformat() if last else None,
            "next_recheck": nxt.isoformat() if nxt else None}


def cmd_paper(conn, paper_id: str) -> dict:
    """`view.py paper <id>` -- the full paper record plus every assertion
    it yields, each with ITS full fields, not just ids."""
    paper = conn.execute("SELECT * FROM records WHERE id = ? AND class = 'paper'", (paper_id,)).fetchone()
    if not paper:
        return {"error": f"no paper record: {paper_id!r}"}
    fields = conn.execute("SELECT * FROM paper_fields WHERE record_id = ?", (paper_id,)).fetchone()
    if fields is None:
        # A paper record with no paper_fields row is a broken schema
        # invariant, not a paper with unknown tier -- report it rather than
        # render tier/access/disposition as None (PR #20 review, 2026-09-19).
        return {"error": f"paper record {paper_id!r} has no paper_fields row (schema invariant broken)"}

    applicability = conn.execute(
        "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ? ORDER BY context_id",
        (paper_id,),
    ).fetchall()

    yield_ids = [
        r["assertion_id"]
        for r in conn.execute(
            "SELECT assertion_id FROM paper_yields WHERE paper_id = ? ORDER BY assertion_id", (paper_id,)
        )
    ]
    yields = [cmd_assertion(conn, aid) for aid in yield_ids]

    return {
        "id": paper["id"],
        "value": paper["value"],
        "provenance": paper["provenance"],
        "tier": fields["tier"] if fields else None,
        # citation == provenance for a paper record (F6 finding 1); read
        # from provenance, never paper_fields.citation, so this tool does
        # not become a second place the redundancy could silently drift.
        "citation": paper["provenance"],
        "access": fields["access"] if fields else None,
        "disposition": fields["disposition"] if fields else None,
        "checked_against_source": fields["checked_against_source"] if fields else None,
        "applicability": [{"context": r["context_id"], "rationale": r["rationale"]} for r in applicability],
        # ADR-0005 A7 (F64): computed on every view, never stored.
        # A paper with no date to start from is due now (PR #77 review: it
        # showed the string "None").
        "recheck": _schedule(recheck.schedule(conn, paper_id)),
        "yields": yields,
    }


def cmd_assertion(conn, assertion_id: str) -> dict:
    """`view.py assertion <id>` -- the full assertion record plus its
    supports/contradicts relations resolved to the OTHER assertion's
    value (not just the bare id), and which paper (if any) yields it."""
    record = conn.execute(
        "SELECT * FROM records WHERE id = ? AND class = 'assertion'", (assertion_id,)
    ).fetchone()
    if not record:
        return {"error": f"no assertion record: {assertion_id!r}"}
    fields = conn.execute("SELECT * FROM assertion_fields WHERE record_id = ?", (assertion_id,)).fetchone()

    documents = [
        r["document"]
        for r in conn.execute(
            "SELECT document FROM assertion_documents WHERE record_id = ? ORDER BY document", (assertion_id,)
        )
    ]

    relations = conn.execute(
        "SELECT to_assertion_id, relation FROM assertion_relations WHERE from_assertion_id = ? "
        "ORDER BY relation, to_assertion_id",
        (assertion_id,),
    ).fetchall()
    supports = [
        {"id": r["to_assertion_id"], "value": _record_title(conn, r["to_assertion_id"])}
        for r in relations
        if r["relation"] == "supports"
    ]
    contradicts = [
        {"id": r["to_assertion_id"], "value": _record_title(conn, r["to_assertion_id"])}
        for r in relations
        if r["relation"] == "contradicts"
    ]

    yielding_paper = conn.execute(
        "SELECT paper_id FROM paper_yields WHERE assertion_id = ?", (assertion_id,)
    ).fetchone()
    # ADR-0004 A9 (F56): computed on every view, never stored; it never
    # changes the certainty above it.
    corr = resolvers.corroboration(conn).get(assertion_id, {"by": [], "not_counted": []})

    return {
        "id": record["id"],
        "value": record["value"],
        "provenance": record["provenance"],
        "evidence_tag": record["evidence_tag"],
        "certainty": record["certainty"],
        "certainty_reasons": record["certainty_reasons"],
        "corroborated_by": [{"id": y, "why": why} for y, why in corr["by"]],
        "supporters_not_counted": [{"id": y, "why": why} for y, why in corr["not_counted"]],
        "fidelity": record["fidelity"],
        "reading_level": record["reading_level"],
        "units": fields["units"] if fields else None,
        "rounding": fields["rounding"] if fields else None,
        "citation_context": fields["citation_context"] if fields else None,
        "documents": documents,
        "supports": supports,
        "contradicts": contradicts,
        "yielded_by_paper": yielding_paper["paper_id"] if yielding_paper else None,
    }


def _print_text(data: dict, mode: str) -> None:
    if "error" in data:
        print(f"error: {data['error']}", file=sys.stderr)
        return

    if mode == "contexts_list":
        for c in data["contexts"]:
            print(f"{c['id']:20s} direct={c['direct_count']:3d}  applicability={c['applicability_count']:3d}  {c['description']}")

    elif mode == "contexts_detail":
        print(f"Context: {data['context']}")
        print(f"\n{len(data['records'])} record(s) directly in this context:")
        for r in data["records"]:
            print(f"  [{r['class']:9s}] {r['id']:50s} {r['value'][:80]}")
        if data["papers_via_applicability"]:
            print(f"\n{len(data['papers_via_applicability'])} paper(s) via applicability (not primary context):")
            for r in data["papers_via_applicability"]:
                print(f"  {r['id']:50s} {r['rationale']}")

    elif mode == "paper":
        print(f"Paper: {data['id']}")
        print(f"  Value:      {data['value']}")
        print(f"  Tier:       {data['tier']}")
        print(f"  Citation:   {data['citation']}")
        print(f"  Access:     {data['access']}")
        print(f"  Disposition: {data['disposition']}")
        print(f"  Checked against source: {data['checked_against_source']}")
        rc = data["recheck"]
        print(f"  Re-check:   section {rc['section']} of 24; last checked {rc['last_check'] or 'never'}; "
              f"next re-check {rc['next_recheck'] or 'now'}")
        if data["applicability"]:
            print("  Applicability:")
            for a in data["applicability"]:
                print(f"    - {a['context']}: {a['rationale']}")
        if data["yields"]:
            print(f"  Yields ({len(data['yields'])} assertion(s)):")
            for y in data["yields"]:
                if "error" in y:
                    print(f"    - {y['error']}")
                else:
                    print(f"    - [{y['id']}] {y['value'][:100]}")

    elif mode == "assertion":
        print(f"Assertion: {data['id']}")
        print(f"  Value:      {data['value']}")
        print(f"  Provenance: {data['provenance']}")
        print(f"  Evidence tag: {data['evidence_tag']}")
        print(f"  Certainty:  {data['certainty']}  ({data['certainty_reasons']})")
        if data["corroborated_by"]:
            print("  Corroborated (computed; the stored certainty is unchanged until an assessor decides):")
            for c in data["corroborated_by"]:
                print(f"    - by [{c['id']}]: {c['why']}")
        if data["supporters_not_counted"]:
            print("  Supporters not counted as corroboration:")
            for c in data["supporters_not_counted"]:
                print(f"    - [{c['id']}]: {c['why']}")
        print(f"  Fidelity:   {data['fidelity']}   Reading level: {data['reading_level']}")
        if data["units"] or data["rounding"]:
            print(f"  Units: {data['units']}  Rounding: {data['rounding']}")
        if data["citation_context"]:
            print(f"  Citation context: {data['citation_context']}")
        if data["documents"]:
            print(f"  Documents: {', '.join(data['documents'])}")
        if data["yielded_by_paper"]:
            print(f"  Yielded by paper: {data['yielded_by_paper']}")
        if data["supports"]:
            print("  Supports:")
            for s in data["supports"]:
                print(f"    - [{s['id']}] {s['value'][:100]}")
        if data["contradicts"]:
            print("  Contradicts:")
            for c in data["contradicts"]:
                print(f"    - [{c['id']}] {c['value'][:100]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="View Evidence Based DB content from the CLI.")
    parser.add_argument("mode", choices=["contexts", "paper", "assertion"])
    parser.add_argument("id", nargs="?", default=None, help="record/context id (omit for 'contexts' to list all)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="output machine-readable JSON")
    args = parser.parse_args()

    if args.mode in ("paper", "assertion") and args.id is None:
        print(f"error: '{args.mode}' mode requires an id", file=sys.stderr)
        return 1

    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1

    try:
        conn = connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"error: could not open {DB_PATH}: {e}", file=sys.stderr)
        return 1

    try:
        if args.mode == "contexts" and args.id is None:
            data, text_mode = cmd_contexts_list(conn), "contexts_list"
        elif args.mode == "contexts":
            data, text_mode = cmd_contexts_detail(conn, args.id), "contexts_detail"
        elif args.mode == "paper":
            data, text_mode = cmd_paper(conn, args.id), "paper"
        elif args.mode == "assertion":
            data, text_mode = cmd_assertion(conn, args.id), "assertion"
        else:
            parser.error(f"unknown mode: {args.mode}")
            return 1
    except sqlite3.Error as e:
        print(f"error: could not read {DB_PATH}: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    if args.as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        _print_text(data, text_mode)

    # A paper whose yielded assertion cannot be resolved carries the error
    # nested under "yields"; that is still a failed lookup and must not exit
    # 0 under --json (PR #20 review, 2026-09-19).
    nested_errors = any("error" in y for y in data.get("yields", []))
    return 1 if ("error" in data or nested_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
