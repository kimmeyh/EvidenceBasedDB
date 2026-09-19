"""Deterministic text export of the store (Sprint 1 Task C).

ADR-0004 section 2: "A deterministic text export (JSON or Markdown per
record class) regenerated from it and committed... The export is
generated, never hand-edited." This is the artifact; the SQLite store is a
build output.

Determinism requirements, load-bearing for the "diff is reviewable" goal
ADR-0004 states: records are emitted in a fixed sort order (by id), object
keys are emitted in a fixed order (not dict insertion order, which can vary
by query plan), and every file ends with exactly one trailing newline.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


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
    and return the flat list of values. F6 finding 6: `_record_contexts`,
    `_record_prerequisites`, and the documents/see_also/yields queries in
    the `_export_*` functions below all repeated this exact "query one
    column, list-comprehend the rows" shape."""
    return [r[key] for r in conn.execute(query, params)]


def _record_contexts(conn: sqlite3.Connection, record_id: str) -> list[str]:
    return _child_list(
        conn,
        "SELECT context_id FROM record_contexts WHERE record_id = ? ORDER BY context_id",
        (record_id,),
        "context_id",
    )


def _record_prerequisites(conn: sqlite3.Connection, record_id: str) -> list[str]:
    return _child_list(
        conn,
        "SELECT prerequisite_id FROM prerequisites WHERE record_id = ? ORDER BY prerequisite_id",
        (record_id,),
        "prerequisite_id",
    )


def _spine(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    record_id = row["id"]
    spine = {
        "id": record_id,
        "class": row["class"],
        "value": row["value"],
        "provenance": row["provenance"],
        "evidence_tag": row["evidence_tag"],
        "contexts": _record_contexts(conn, record_id),
    }
    if row["certainty"] is not None:
        spine["certainty"] = row["certainty"]
    if row["certainty_reasons"] is not None:
        spine["certainty_reasons"] = row["certainty_reasons"]
    if row["fidelity"] is not None:
        spine["fidelity"] = row["fidelity"]
    if row["reading_level"] is not None:
        spine["reading_level"] = row["reading_level"]
    prerequisites = _record_prerequisites(conn, record_id)
    if prerequisites:
        spine["prerequisites"] = prerequisites
    spine["updated"] = row["updated"]
    spine["updated_reason"] = row["updated_reason"]
    return spine


def _export_assertion(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    record = _spine(conn, row)
    fields = conn.execute(
        "SELECT units, rounding, citation_context FROM assertion_fields WHERE record_id = ?",
        (row["id"],),
    ).fetchone()
    if fields is not None:
        _copy_nonnull(record, fields, "units", "rounding", "citation_context")

    documents = _child_list(
        conn,
        "SELECT document FROM assertion_documents WHERE record_id = ? ORDER BY document",
        (row["id"],),
        "document",
    )
    if documents:
        record["documents"] = documents

    relations = conn.execute(
        "SELECT to_assertion_id, relation FROM assertion_relations "
        "WHERE from_assertion_id = ? ORDER BY relation, to_assertion_id",
        (row["id"],),
    )
    supports, contradicts = [], []
    for r in relations:
        (supports if r["relation"] == "supports" else contradicts).append(r["to_assertion_id"])
    if supports:
        record["supports"] = supports
    if contradicts:
        record["contradicts"] = contradicts
    return record


def _export_acronym(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    record = _spine(conn, row)
    fields = conn.execute(
        "SELECT expansion, plain_definition, visual FROM acronym_fields WHERE record_id = ?",
        (row["id"],),
    ).fetchone()
    if fields is not None:
        record["expansion"] = fields["expansion"]
        record["plain_definition"] = fields["plain_definition"]
        _copy_nonnull(record, fields, "visual")
    return record


def _export_term(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    record = _spine(conn, row)
    fields = conn.execute(
        "SELECT plain_definition, visual FROM term_fields WHERE record_id = ?",
        (row["id"],),
    ).fetchone()
    if fields is not None:
        record["plain_definition"] = fields["plain_definition"]
        _copy_nonnull(record, fields, "visual")

    see_also = _child_list(
        conn,
        "SELECT see_also_id FROM term_see_also WHERE record_id = ? ORDER BY see_also_id",
        (row["id"],),
        "see_also_id",
    )
    if see_also:
        record["see_also"] = see_also
    return record


def _export_paper(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    record = _spine(conn, row)
    fields = conn.execute(
        "SELECT tier, access, disposition, evidence, mined_by, checked_against_source "
        "FROM paper_fields WHERE record_id = ?",
        (row["id"],),
    ).fetchone()
    if fields is not None:
        record["tier"] = fields["tier"]
        # `citation` is `records.provenance` (already in the spine above),
        # never `paper_fields.citation` -- PR #1 review (F6 finding 1): a
        # paper's citation and its provenance are the SAME string,
        # insert_paper() writes it into both columns, and CLAUDE.md's own
        # standing rule against restating one value in more than one place
        # applies exactly here. `paper_fields.citation` stays a NOT NULL
        # schema column (dropping it is a table rebuild, out of this
        # sprint's scope) but the export no longer reads it as a second
        # source of truth.
        record["citation"] = record["provenance"]
        record["access"] = fields["access"]
        record["disposition"] = fields["disposition"]
        _copy_nonnull(record, fields, "evidence", "mined_by", "checked_against_source")

    applicability_rows = [
        {"context": r["context_id"], "rationale": r["rationale"]}
        for r in conn.execute(
            "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ? ORDER BY context_id",
            (row["id"],),
        )
    ]
    if applicability_rows:
        record["applicability"] = applicability_rows

    yields_ = _child_list(
        conn,
        "SELECT assertion_id FROM paper_yields WHERE paper_id = ? ORDER BY assertion_id",
        (row["id"],),
        "assertion_id",
    )
    if yields_:
        record["yields"] = yields_
    return record


_EXPORTERS = {
    "assertion": _export_assertion,
    "acronym": _export_acronym,
    "term": _export_term,
    "paper": _export_paper,
}


def export_class(conn: sqlite3.Connection, record_class: str) -> list[dict]:
    """Export every record of one class, sorted by id for a stable diff."""
    exporter = _EXPORTERS[record_class]
    rows = conn.execute(
        "SELECT * FROM records WHERE class = ? ORDER BY id", (record_class,)
    )
    return [exporter(conn, row) for row in rows]


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
