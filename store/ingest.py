"""Ingestion helpers for paper and assertion records (Sprint 1 Task E/F).

ADR-0005 section 2b2: a paper is a source of assertions, not a record in
itself. Ingesting a paper means writing one paper record plus one or more
assertion records it yields, linked through paper_yields. This module is
the reusable path Task E proves out on one paper and Task F runs 46 times.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field


@dataclass
class PaperRecord:
    id: str
    tier: str  # 'seen' | 'screened' | 'read'
    citation: str
    access: str
    disposition: str
    context: str  # primary context id, also inserted into record_contexts
    value: str  # the records.value field -- a one-line description of the paper
    evidence_tag: str = "N/A"
    evidence: str | None = None
    mined_by: str | None = None
    checked_against_source: str | None = None
    updated: str = ""
    updated_reason: str = ""
    applicability: list[tuple[str, str]] = field(default_factory=list)  # (context_id, rationale)


@dataclass
class AssertionRecord:
    id: str
    value: str
    provenance: str
    evidence_tag: str
    context: str
    citation_context: str | None = None
    units: str | None = None
    rounding: str | None = None
    documents: list[str] = field(default_factory=list)
    certainty: str | None = None
    certainty_reasons: str | None = None
    fidelity: str | None = None
    reading_level: int | None = None
    supports: list[str] = field(default_factory=list)
    contradicts: list[str] = field(default_factory=list)
    updated: str = ""
    updated_reason: str = ""


def insert_paper(conn: sqlite3.Connection, paper: PaperRecord) -> None:
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES (?, 'paper', ?, ?, ?, ?, ?)",
        (paper.id, paper.value, paper.citation, paper.evidence_tag, paper.updated, paper.updated_reason),
    )
    conn.execute(
        "INSERT INTO record_contexts (record_id, context_id) VALUES (?, ?)",
        (paper.id, paper.context),
    )
    conn.execute(
        "INSERT INTO paper_fields (record_id, tier, citation, access, disposition, evidence, mined_by, checked_against_source) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (paper.id, paper.tier, paper.citation, paper.access, paper.disposition, paper.evidence, paper.mined_by, paper.checked_against_source),
    )
    for context_id, rationale in paper.applicability:
        conn.execute(
            "INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
            (paper.id, context_id, rationale),
        )


def insert_assertion(conn: sqlite3.Connection, assertion: AssertionRecord, yielded_by: str | None = None) -> None:
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, certainty, certainty_reasons, "
        "fidelity, reading_level, updated, updated_reason) "
        "VALUES (?, 'assertion', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            assertion.id, assertion.value, assertion.provenance, assertion.evidence_tag,
            assertion.certainty, assertion.certainty_reasons, assertion.fidelity,
            assertion.reading_level, assertion.updated, assertion.updated_reason,
        ),
    )
    conn.execute(
        "INSERT INTO record_contexts (record_id, context_id) VALUES (?, ?)",
        (assertion.id, assertion.context),
    )
    # assertion_fields is written whenever ANY of its optional fields is
    # set, not unconditionally -- an assertion with no units/rounding/
    # citation_context has no reason to carry an all-NULL row. Fixed
    # 2026-09-16 (Copilot PR #1 review): this row previously was never
    # written at all, which meant assertion_documents (originally keyed to
    # assertion_fields, now to records directly) had no row to key against
    # even when it didn't need one, and citation_context had nowhere to go.
    if assertion.units is not None or assertion.rounding is not None or assertion.citation_context is not None:
        conn.execute(
            "INSERT INTO assertion_fields (record_id, units, rounding, citation_context) VALUES (?, ?, ?, ?)",
            (assertion.id, assertion.units, assertion.rounding, assertion.citation_context),
        )
    for document in assertion.documents:
        conn.execute(
            "INSERT INTO assertion_documents (record_id, document) VALUES (?, ?)",
            (assertion.id, document),
        )
    if yielded_by is not None:
        conn.execute(
            "INSERT INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)",
            (yielded_by, assertion.id),
        )
    for target in assertion.supports:
        conn.execute(
            "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES (?, ?, 'supports')",
            (assertion.id, target),
        )
    for target in assertion.contradicts:
        conn.execute(
            "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES (?, ?, 'contradicts')",
            (assertion.id, target),
        )
