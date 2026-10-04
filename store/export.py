"""Deterministic text export of the store (Sprint 1 Task C).

ADR-0004 section 2: "A deterministic text export (JSON or Markdown per
record class) regenerated from it and committed... The export is
generated, never hand-edited." This is the artifact; the SQLite store is a
build output.

Determinism requirements, load-bearing for the "diff is reviewable" goal
ADR-0004 states: records are emitted in a fixed sort order (by id), object
keys are emitted in a fixed order (not dict insertion order, which can vary
by query plan), and every file ends with exactly one trailing newline.

Query shape (Sprint 4 Task D, F26, 2026-09-19): ONE query per related table
per class, grouped in Python, instead of two to five SELECTs per record.
PR #1 review finding 4 named the per-record shape; Sprint 3 Task B left it
deliberately (premature at 54 records: 275 statements in a few
milliseconds); Sprint 4 batched it ahead of the ~1,200-paper arrival so
regeneration cost stops growing with record count. The acceptance test is
byte-identity of the export before and after -- the determinism property
is the thing at risk in a query rewrite, and every per-record ORDER BY
below survives as the trailing ORDER BY key of its batched query.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

from store.resolvers import certainty_caps


def _copy_nonnull(record: dict, row: sqlite3.Row, *columns: str) -> None:
    """Copy each named column from `row` into `record` under the same key,
    but only if the value is not NULL (F6 finding 6, PR #1 review: every
    `_export_*` function repeated this "if not None: record[k] = row[k]"
    shape once per optional field). A NULL column means "not yet filled,"
    which the export omits entirely rather than emitting `null` -- distinct
    from a field like `paper_fields.checked_against_source = 'never'`,
    which IS a real value and is copied like any other non-NULL one."""
    for column in columns:
        if row[column] is not None:
            record[column] = row[column]


def _child_list(conn: sqlite3.Connection, query: str, params: tuple, key: str) -> list[str]:
    """Run a one-column child-table query, ordered by the caller's own SQL,
    and return the flat list of values. F6 finding 6 extracted this shape
    from five per-record call sites; since F26 the export itself goes
    through `_grouped` (one query per table per class) and this helper
    stays for callers that genuinely want one record's children."""
    return [r[key] for r in conn.execute(query, params)]


def _grouped(
    conn: sqlite3.Connection,
    query: str,
    params: tuple,
    key: str,
    value: str | None = None,
) -> dict[str, list]:
    """Run ONE child-table query for a whole class and group its rows by
    `key` (the record id) in Python, preserving the query's own row order
    within each group. With `value` set, each group is a flat list of that
    column (the `_child_list` shape); otherwise each group is the list of
    full rows. The query's ORDER BY must lead with `key` and then the
    per-record sort the export promises, so grouping keeps exactly the
    order the old per-record queries produced."""
    out: dict[str, list] = defaultdict(list)
    for r in conn.execute(query, params):
        out[r[key]].append(r[value] if value is not None else r)
    return out


def _spine(row: sqlite3.Row, contexts: dict[str, list], prerequisites: dict[str, list]) -> dict:
    record_id = row["id"]
    spine = {
        "id": record_id,
        "class": row["class"],
        "value": row["value"],
        "provenance": row["provenance"],
        "evidence_tag": row["evidence_tag"],
        "contexts": contexts.get(record_id, []),
    }
    if row["certainty"] is not None:
        spine["certainty"] = row["certainty"]
    if row["certainty_reasons"] is not None:
        spine["certainty_reasons"] = row["certainty_reasons"]
    if row["fidelity"] is not None:
        spine["fidelity"] = row["fidelity"]
    if row["reading_level"] is not None:
        spine["reading_level"] = row["reading_level"]
    prereqs = prerequisites.get(record_id, [])
    if prereqs:
        spine["prerequisites"] = prereqs
    spine["updated"] = row["updated"]
    spine["updated_reason"] = row["updated_reason"]
    return spine


def _fields_by_record(conn: sqlite3.Connection, table: str, columns: str, record_class: str) -> dict[str, sqlite3.Row]:
    """One query for the class-specific field table of a whole class."""
    rows = conn.execute(
        f"SELECT f.record_id, {columns} FROM {table} f "
        "JOIN records r ON r.id = f.record_id WHERE r.class = ?",
        (record_class,),
    )
    return {r["record_id"]: r for r in rows}


def _export_assertions(conn: sqlite3.Connection, rows: list[sqlite3.Row], contexts, prerequisites) -> list[dict]:
    fields = _fields_by_record(
        conn, "assertion_fields",
        "f.units, f.rounding, f.citation_context, f.derivation, f.claim_type, f.search_scope", "assertion")
    caps = certainty_caps(conn)
    documents = _grouped(
        conn,
        "SELECT d.record_id, d.document FROM assertion_documents d "
        "JOIN records r ON r.id = d.record_id WHERE r.class = 'assertion' "
        "ORDER BY d.record_id, d.document",
        (), "record_id", "document",
    )
    relations = _grouped(
        conn,
        "SELECT a.from_assertion_id AS record_id, a.to_assertion_id, a.relation FROM assertion_relations a "
        "JOIN records r ON r.id = a.from_assertion_id WHERE r.class = 'assertion' "
        "ORDER BY a.from_assertion_id, a.relation, a.to_assertion_id",
        (), "record_id",
    )
    out = []
    for row in rows:
        record = _spine(row, contexts, prerequisites)
        f = fields.get(row["id"])
        if f is not None:
            _copy_nonnull(record, f, "units", "rounding", "citation_context")
        docs = documents.get(row["id"], [])
        if docs:
            record["documents"] = docs
        supports, contradicts = [], []
        for rel in relations.get(row["id"], []):
            (supports if rel["relation"] == "supports" else contradicts).append(rel["to_assertion_id"])
        if supports:
            record["supports"] = supports
        if contradicts:
            record["contradicts"] = contradicts
        if f is not None:
            # ADR-0004 A6 (Sprint 6 Task E).
            _copy_nonnull(record, f, "derivation", "claim_type", "search_scope")
        if row["id"] in caps:
            # DERIVED keys (A6 (e)): computed here from stored facts on every
            # export; store/rebuild.py knows them and never writes them back.
            record["certainty_cap"], record["certainty_cap_reason"] = caps[row["id"]]
        out.append(record)
    return out


def _export_acronyms(conn: sqlite3.Connection, rows: list[sqlite3.Row], contexts, prerequisites) -> list[dict]:
    fields = _fields_by_record(conn, "acronym_fields", "f.expansion, f.plain_definition, f.visual", "acronym")
    out = []
    for row in rows:
        record = _spine(row, contexts, prerequisites)
        f = fields.get(row["id"])
        if f is not None:
            record["expansion"] = f["expansion"]
            record["plain_definition"] = f["plain_definition"]
            _copy_nonnull(record, f, "visual")
        out.append(record)
    return out


def _export_terms(conn: sqlite3.Connection, rows: list[sqlite3.Row], contexts, prerequisites) -> list[dict]:
    fields = _fields_by_record(conn, "term_fields", "f.plain_definition, f.visual", "term")
    see_also = _grouped(
        conn,
        "SELECT s.record_id, s.see_also_id FROM term_see_also s "
        "JOIN records r ON r.id = s.record_id WHERE r.class = 'term' "
        "ORDER BY s.record_id, s.see_also_id",
        (), "record_id", "see_also_id",
    )
    out = []
    for row in rows:
        record = _spine(row, contexts, prerequisites)
        f = fields.get(row["id"])
        if f is not None:
            record["plain_definition"] = f["plain_definition"]
            _copy_nonnull(record, f, "visual")
        links = see_also.get(row["id"], [])
        if links:
            record["see_also"] = links
        out.append(record)
    return out


def _export_papers(conn: sqlite3.Connection, rows: list[sqlite3.Row], contexts, prerequisites) -> list[dict]:
    fields = _fields_by_record(
        conn, "paper_fields",
        "f.tier, f.access, f.disposition, f.evidence, f.mined_by, f.checked_against_source, "
        "f.metadata_provider, f.coi", "paper",
    )
    # ADR-0005 A4 (Sprint 6 Task E): the reference fields' child tables.
    found_via = _grouped(
        conn,
        "SELECT v.record_id, v.route, v.cited_as FROM paper_found_via v "
        "JOIN records r ON r.id = v.record_id WHERE r.class = 'paper' ORDER BY v.record_id, v.route",
        (), "record_id",
    )
    reads = _grouped(
        conn,
        "SELECT d.record_id, d.reader, d.read_on, d.extent, d.detail FROM paper_reads d "
        "JOIN records r ON r.id = d.record_id WHERE r.class = 'paper' "
        "ORDER BY d.record_id, d.read_on, d.reader, d.extent, d.detail",
        (), "record_id",
    )
    probes = _grouped(
        conn,
        "SELECT p.record_id, p.field, p.value, p.provider, p.probed_on, p.anchor FROM paper_probes p "
        "JOIN records r ON r.id = p.record_id WHERE r.class = 'paper' ORDER BY p.record_id, p.field",
        (), "record_id",
    )
    links = _grouped(
        conn,
        "SELECT s.from_id AS record_id, s.to_id, s.link_type, s.evidence FROM source_links s "
        "JOIN records r ON r.id = s.from_id WHERE r.class = 'paper' ORDER BY s.from_id, s.link_type, s.to_id",
        (), "record_id",
    )
    applicability = _grouped(
        conn,
        "SELECT a.record_id, a.context_id, a.rationale FROM paper_applicability a "
        "JOIN records r ON r.id = a.record_id WHERE r.class = 'paper' "
        "ORDER BY a.record_id, a.context_id",
        (), "record_id",
    )
    yields = _grouped(
        conn,
        "SELECT y.paper_id AS record_id, y.assertion_id FROM paper_yields y "
        "JOIN records r ON r.id = y.paper_id WHERE r.class = 'paper' "
        "ORDER BY y.paper_id, y.assertion_id",
        (), "record_id", "assertion_id",
    )
    out = []
    for row in rows:
        record = _spine(row, contexts, prerequisites)
        f = fields.get(row["id"])
        if f is not None:
            record["tier"] = f["tier"]
            # `citation` is `records.provenance` (already in the spine above).
            # PR #1 review (F6 finding 1) moved the export off the duplicate
            # column; Sprint 4 Task B (F25 B4 / Q2) then dropped
            # `paper_fields.citation` from the schema altogether, so the
            # citation now lives in exactly one place.
            record["citation"] = record["provenance"]
            record["access"] = f["access"]
            record["disposition"] = f["disposition"]
            _copy_nonnull(record, f, "evidence", "mined_by", "checked_against_source")
        app = applicability.get(row["id"], [])
        if app:
            record["applicability"] = [{"context": a["context_id"], "rationale": a["rationale"]} for a in app]
        y = yields.get(row["id"], [])
        if y:
            record["yields"] = y
        if f is not None:
            _copy_nonnull(record, f, "metadata_provider", "coi")
        fv = found_via.get(row["id"], [])
        if fv:
            record["found_via"] = [{"route": v["route"], **({"cited_as": v["cited_as"]} if v["cited_as"] is not None else {})}
                                   for v in fv]
        rd = reads.get(row["id"], [])
        if rd:
            record["read_extent"] = [{"reader": d["reader"], "read_on": d["read_on"], "extent": d["extent"],
                                      **({"detail": d["detail"]} if d["detail"] else {})} for d in rd]
        # Each computed field under its own name, as the probe's last result
        # (the probe rule): value, the provider that answered, and the date.
        for p in probes.get(row["id"], []):
            record[p["field"]] = {"value": p["value"], "provider": p["provider"], "probed_on": p["probed_on"],
                                  **({"anchor": p["anchor"]} if p["anchor"] is not None else {})}
        sl = links.get(row["id"], [])
        if sl:
            record["source_links"] = [{"type": s["link_type"], "to": s["to_id"], "evidence": s["evidence"]} for s in sl]
        out.append(record)
    return out


_EXPORTERS = {
    "assertion": _export_assertions,
    "acronym": _export_acronyms,
    "term": _export_terms,
    "paper": _export_papers,
}


def export_class(conn: sqlite3.Connection, record_class: str) -> list[dict]:
    """Export every record of one class, sorted by id for a stable diff.

    A fixed number of queries per class regardless of record count: the
    records themselves, the two spine child tables (contexts,
    prerequisites), then the class's own field table and child tables.
    """
    exporter = _EXPORTERS[record_class]
    rows = conn.execute(
        "SELECT * FROM records WHERE class = ? ORDER BY id", (record_class,)
    ).fetchall()
    contexts = _grouped(
        conn,
        "SELECT c.record_id, c.context_id FROM record_contexts c "
        "JOIN records r ON r.id = c.record_id WHERE r.class = ? "
        "ORDER BY c.record_id, c.context_id",
        (record_class,), "record_id", "context_id",
    )
    prerequisites = _grouped(
        conn,
        "SELECT p.record_id, p.prerequisite_id FROM prerequisites p "
        "JOIN records r ON r.id = p.record_id WHERE r.class = ? "
        "ORDER BY p.record_id, p.prerequisite_id",
        (record_class,), "record_id", "prerequisite_id",
    )
    return exporter(conn, rows, contexts, prerequisites)


def write_export(conn: sqlite3.Connection, export_dir: str | Path) -> None:
    """Regenerate the committed export: one JSON file per record class.

    Deterministic: fixed record order (by id), fixed key order (dict
    insertion order in each _export_* function, which is fixed by the code
    rather than by SQLite's iteration order), 2-space indent, and exactly
    one trailing newline per file so a re-run with no data change produces
    a byte-identical file and an empty diff.
    """
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    for record_class in ("assertion", "acronym", "term", "paper"):
        records = export_class(conn, record_class)
        path = export_dir / f"{record_class}s.json"
        text = json.dumps(records, indent=2, sort_keys=False, ensure_ascii=False)
        path.write_text(text + "\n", encoding="utf-8")


def write_contexts_export(conn: sqlite3.Connection, export_dir: str | Path) -> None:
    """Export the contexts table itself, since it is referenced but not a record class."""
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    rows = conn.execute("SELECT id, description FROM contexts ORDER BY id")
    contexts = [{"id": r["id"], "description": r["description"]} for r in rows]
    path = export_dir / "contexts.json"
    text = json.dumps(contexts, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


def regenerate(conn: sqlite3.Connection, export_dir: str | Path) -> None:
    """Regenerate the full export: contexts plus all four record classes."""
    write_contexts_export(conn, export_dir)
    write_export(conn, export_dir)
