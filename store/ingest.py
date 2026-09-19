"""Ingestion helpers for paper and assertion records (Sprint 1 Task E/F).

ADR-0005 section 2b2: a paper is a source of assertions, not a record in
itself. Ingesting a paper means writing one paper record plus one or more
assertion records it yields, linked through paper_yields. This module is
the reusable path Task E proves out on one paper and Task F runs 46 times.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field, replace
from pathlib import Path

from store import citations

HAND_MARKER = "hand-transcribed from"

# Audit trail belongs in updated_reason/evidence, never inside a citation
# string (F10 review: loke's 700-character correction narrative, the
# kordzanganeh arXiv-id note, two duplicate-file notes all lived in
# `citation`, which is why the field could not be machine-validated).
_AUDIT_MARKERS = ("CORRECTED", "NOTE:", "verified against", "recorded once", "identically-content")
_TIER_IN_TEXT = re.compile(r"\b(seen|screened|read)[- ]tier\b|\btier\s*[:=]?\s*'?(seen|screened|read)\b", re.IGNORECASE)
_ANCHOR = re.compile(r"\s--\s\S")


@dataclass
class PaperRecord:
    """One paper as it enters the store.

    Sprint 4 Task B (F25 C1-C3) changed the contract: `citation` is no
    longer a free-text input. Declare `citation_origin`:

    - "api": `access` carries an arXiv id or DOI; leave `citation` None and
      `insert_paper()` derives the citation AND the title (`value`) from
      the source of record via store.citations. A pre-rendered citation
      may be supplied (fixtures, replays) and is trusted as api-origin;
      scripts/refresh_citations.py is the periodic check that it still
      matches the API.
    - "hand": `access` carries NO resolvable id (a vendor PDF, a report).
      Then `hand_transcribed_from` names where the eye read it ("cover",
      "p.1 byline"), `citation` must say so visibly (HAND_MARKER), and
      `access` must be an existing local path -- never the bare words
      "local file".

    `value` is the paper's TITLE (ADR-0004 section 3: value is "what it
    is"); it used to be a third copy of the citation string.
    """
    id: str
    tier: str  # 'seen' | 'screened' | 'read'
    access: str
    disposition: str
    context: str  # primary context id, also inserted into record_contexts
    value: str = ""  # title; filled from the resolver when citation_origin == "api"
    citation: str | None = None
    citation_origin: str = ""  # "api" | "hand" -- must be declared explicitly
    hand_transcribed_from: str | None = None
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


def validate_paper(paper: PaperRecord) -> None:
    """Enforce ADR-0005 section 2's rule that checked_against_source is
    set at tier 'read'. Fixed 2026-09-18 (F6 finding 2, PR #1 review):
    schema.sql's comment promised an application-layer check that did not
    exist -- insert_paper() accepted any tier/checked_against_source
    combination unchecked.

    Why here and not in the schema: the rule IS expressible as a table-
    level CHECK in SQLite (`CHECK (tier != 'read' OR checked_against_source
    IS NOT NULL)` -- corrected 2026-09-19, Copilot PR #20 review; an earlier
    version of this docstring and of schema.sql's comment wrongly said a
    trigger was needed). Since Sprint 4 Task B (2026-09-19) the CHECK is in
    schema.sql and was applied to the live store by
    scripts/migrate_paper_fields_drop_citation.py. This application-layer
    check stays as well because a CHECK cannot reject a blank string or
    explain what to do instead; belt and braces is correct for the field
    ADR-0005 calls the read-tier gate.

    'never' is a valid, meaningful value (a statement someone made) and
    satisfies this check. None AND blank/whitespace-only both fail it
    (Copilot PR #20 review, 2026-09-19: an empty string previously passed,
    letting the required field be effectively missing).
    """
    value = paper.checked_against_source
    if paper.tier == "read" and (value is None or not value.strip()):
        raise ValueError(
            f"paper {paper.id!r} is tier='read' but checked_against_source is "
            f"{'not set' if value is None else 'blank'}. ADR-0005 section 2 requires "
            "it at this tier -- use the literal string 'never' if that is genuinely "
            "the intended value, not None or an empty string."
        )

    # --- Sprint 4 Task B (F25 C1/C2): the door's rules. Each has a failing test. ---
    pid = paper.id
    resolvable = citations.parse_access(paper.access)
    if paper.citation_origin not in ("api", "hand"):
        raise ValueError(
            f"paper {pid!r}: citation_origin must be declared as 'api' or 'hand' "
            f"(got {paper.citation_origin!r}). ADR-0005 section 2: citations are pulled "
            "from an API, never hand-typed; a hand transcription is the explicit exception."
        )
    if paper.citation_origin == "api" and resolvable is None:
        raise ValueError(
            f"paper {pid!r}: citation_origin='api' but access {paper.access!r} carries no "
            "arXiv id or DOI. Give a resolvable id, or declare citation_origin='hand' with "
            "hand_transcribed_from and a real local path."
        )
    if paper.citation_origin == "hand":
        if resolvable is not None:
            raise ValueError(
                f"paper {pid!r}: access {paper.access!r} carries a resolvable id "
                f"({resolvable[0]} {resolvable[1]}); hand-typing a citation for it is exactly "
                "the defect F10 found four times. Use citation_origin='api'."
            )
        if not (paper.hand_transcribed_from or "").strip():
            raise ValueError(f"paper {pid!r}: citation_origin='hand' requires hand_transcribed_from (e.g. 'cover', 'p.1 byline').")
        if not paper.citation or HAND_MARKER not in paper.citation:
            raise ValueError(
                f"paper {pid!r}: a hand-transcribed citation must say so visibly -- include "
                f"'{HAND_MARKER} <page>' in the citation string."
            )
        if not Path(paper.access).exists():
            raise ValueError(
                f"paper {pid!r}: access {paper.access!r} is not an existing local path. "
                "ADR-0005 section 3: access is a DOI, an arXiv id, or a local path outside "
                "version control -- never the bare words 'local file'."
            )
    if paper.citation and any(marker.lower() in paper.citation.lower() for marker in _AUDIT_MARKERS):
        raise ValueError(
            f"paper {pid!r}: citation carries audit-trail text ({', '.join(m for m in _AUDIT_MARKERS if m.lower() in paper.citation.lower())}). "
            "Corrections and notes belong in updated_reason or evidence, not in the citation."
        )
    # The title is the record's value. An api-origin paper whose citation is
    # still None gets both from the API in derive_citation(); every other
    # shape must arrive with the title already filled in.
    to_be_derived = paper.citation_origin == "api" and paper.citation is None
    if not to_be_derived and not (paper.value or "").strip():
        raise ValueError(
            f"paper {pid!r}: value (the title) is empty. A paper record's value is its title; "
            "for citation_origin='api' leave citation=None and the door fills both from the API."
        )
    if "\n" in paper.disposition or "\r" in paper.disposition:
        raise ValueError(f"paper {pid!r}: disposition must be one line (ADR-0005 section 2).")
    if _TIER_IN_TEXT.search(paper.disposition):
        raise ValueError(
            f"paper {pid!r}: disposition names a tier; the `tier` column is the resolver "
            "and a second copy in prose is the drift this store exists against."
        )
    for context_id, rationale in paper.applicability:
        if not _ANCHOR.search(rationale or ""):
            raise ValueError(
                f"paper {pid!r}: applicability rationale for {context_id!r} has no source anchor. "
                "End it with ' -- <where you read it>' (e.g. ' -- p.1 keywords', "
                "' -- arXiv affiliation block'); a rationale that cannot say where its value "
                "came from is the defect this whole system exists against."
            )


def set_tier(
    conn: sqlite3.Connection,
    record_id: str,
    tier: str,
    checked_against_source: str | None = None,
) -> None:
    """The ONLY sanctioned way to change a paper's tier after insert.

    PR #20 review (2026-09-19): validate_paper() ran on insert only, and the
    one other tier writer in the repository (ingest_seed_set.py's promotion
    UPDATE) bypassed it entirely. Harmless today because that UPDATE only
    ever sets 'screened', but the next promotion to 'read' would have
    reintroduced exactly the gap F6 finding 2 closed, with no test to catch
    it. Route every tier change through here so the read-tier rule holds
    at the column, not at one call site; the schema-level CHECK lands with
    F25 B4's table rebuild.

    If `checked_against_source` is given it is written alongside the tier;
    otherwise the row's existing value is what the rule is checked against.
    """
    row = conn.execute(
        "SELECT checked_against_source FROM paper_fields WHERE record_id = ?", (record_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"paper {record_id!r} has no paper_fields row")
    effective = checked_against_source if checked_against_source is not None else row["checked_against_source"]
    if tier == "read" and (effective is None or not effective.strip()):
        raise ValueError(
            f"cannot set paper {record_id!r} to tier='read': checked_against_source is "
            f"{'not set' if effective is None else 'blank'}. ADR-0005 section 2 requires it "
            "at this tier -- pass checked_against_source (the literal 'never' is valid)."
        )
    if checked_against_source is not None:
        conn.execute(
            "UPDATE paper_fields SET tier = ?, checked_against_source = ? WHERE record_id = ?",
            (tier, checked_against_source, record_id),
        )
    else:
        conn.execute("UPDATE paper_fields SET tier = ? WHERE record_id = ?", (tier, record_id))


def derive_citation(paper: PaperRecord, fetcher: citations.Fetcher | None = None) -> PaperRecord:
    """For an api-origin paper with no citation yet: fetch the source of
    record and fill `citation` and `value` (title). Returns a new record;
    the input is not mutated. No-op when a citation is already present."""
    if paper.citation_origin != "api" or paper.citation is not None:
        return paper
    md, rendered = citations.resolve(paper.access, fetcher=fetcher)
    return replace(paper, citation=rendered, value=paper.value or md.title)


def insert_paper(
    conn: sqlite3.Connection,
    paper: PaperRecord,
    fetcher: citations.Fetcher | None = None,
) -> PaperRecord:
    """The ONLY way a paper enters the store. Derives the citation from the
    source of record for api-origin papers (unless one was supplied), then
    validates every rule, then writes. Returns the record as written.
    `paper_fields.citation` no longer exists (Sprint 4 Task B, F25 B4/Q2):
    the citation lives once, in records.provenance, and the export reads it
    from there."""
    paper = derive_citation(paper, fetcher)
    validate_paper(paper)
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
        "INSERT INTO paper_fields (record_id, tier, access, disposition, evidence, mined_by, checked_against_source) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (paper.id, paper.tier, paper.access, paper.disposition, paper.evidence, paper.mined_by, paper.checked_against_source),
    )
    for context_id, rationale in paper.applicability:
        conn.execute(
            "INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
            (paper.id, context_id, rationale),
        )
    return paper


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
