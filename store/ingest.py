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


class _DerivedByDoor:
    """The mark `derive_citation` puts on a citation IT fetched.

    A sentinel OBJECT, not a string, so a caller cannot write the value by
    hand. `validate_paper` accepts a caller-supplied api-origin citation
    only when it carries this exact object (compared by identity) or the
    caller declares REPLAY out loud.

    PR #30 round-2 review, 2026-09-23: the previous marker was the string
    "api", which any caller could type, so the rule refused an OMISSION but
    not a FABRICATION -- a fabricated citation on a resolvable id was
    accepted with no network call by changing one string literal to the
    value that reads as more legitimate. A marker the caller can forge is
    not a marker.
    """

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover -- diagnostics only
        return "<derived by the door from the source of record>"


DERIVED_BY_DOOR = _DerivedByDoor()
REPLAY = "replay"  # the caller's declared exception: a fixture, a historical one-off

# Audit trail belongs in updated_reason/evidence, never inside a citation
# string (F10 review: loke's 700-character correction narrative, the
# kordzanganeh arXiv-id note, two duplicate-file notes all lived in
# `citation`, which is why the field could not be machine-validated).
_AUDIT_MARKERS = ("CORRECTED", "NOTE:", "verified against", "recorded once", "identically-content")
_TIER_IN_TEXT = re.compile(
    r"\b(seen|screened|read)[- ]tier\b"                       # "seen tier", "read-tier"
    r"|\btier\s*[:=]?\s*'?(seen|screened|read)\b"              # "tier: screened"
    r"|\b(seen|screened|read)(/(seen|screened|read))?[- ]candidate\b",  # "screened/read candidate"
    re.IGNORECASE,
)
_ACCESS_URL_SEP = " | "  # hand-origin access: "<existing local path> | <https URL>"
_ANCHOR = re.compile(r"\s--\s\S")


@dataclass
class PaperRecord:
    """One paper as it enters the store.

    Sprint 4 Task B (F25 C1-C3) changed the contract: `citation` is no
    longer a free-text input. Declare `citation_origin`:

    - "api": `access` carries an arXiv id or DOI; leave `citation` None and
      `insert_paper()` derives the citation AND the title (`value`) from
      the source of record via store.citations.

      A pre-rendered citation may be supplied ONLY with
      `citation_source=REPLAY` naming why (a fixture, a historical one-off
      whose API response is not being re-fetched); what the door itself
      derived carries DERIVED_BY_DOOR, a sentinel a caller cannot write.
      PR #30 review, 2026-09-22: until then any api-origin record could
      carry an arbitrary citation and title with no network call and no
      complaint, which reinstates the exact defect class the door exists
      to stop -- a fabricated citation on a paper whose id would have
      given the true one.

      SCOPE, stated because the first version of this docstring overclaimed
      (round-2 review, 2026-09-23): `citation_source` lives on this
      dataclass only. It is NOT a column and NOT in the export, so a replay
      is visible in the CALLING SCRIPT's source, not in the shipped
      artifact. Persisting it is recorded as a Sprint 5 decision in
      docs/INTAKE_WORKFLOW.md.
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
    # How an api-origin record came to carry a rendered citation. The only
    # two accepted values are DERIVED_BY_DOOR -- a sentinel object that only
    # derive_citation can attach, so a caller cannot type it -- and the
    # literal REPLAY, the caller declaring a deliberate exception. Anything
    # else, including the default, means a caller supplied a citation it
    # should not have. See the class docstring and _DerivedByDoor.
    citation_source: object = ""
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


def append_updated_reason(conn, record_id: str, note: str, today: str) -> str:
    """Append `note` to a record's `updated_reason`. NEVER replace it.

    `updated_reason` is the row's own account of why it says what it says.
    ADR-0004 section 2 makes `export/` the artifact the whole review
    mechanism depends on, and CLAUDE.md: "A record that cannot say where its
    value came from is the defect this whole system exists against."

    WHY THIS FUNCTION EXISTS RATHER THAN A LINE IN EACH SCRIPT. Sprint 4's
    correction passes each spelled the join themselves, and three of them
    spelled it with an inverted ternary that kept the prior text only when
    the row had been touched the SAME DAY. That ran: prior `updated_reason`
    survived on 0 of 44 paper records; 43 lost "Sprint 1 Task F: 46-paper
    seed set loaded at seen tier". A guard that scanned the scripts' SOURCE
    for the bad phrasing was then defeated by three rewrites that destroy
    history while keeping the shape (PR #30 round-2 audit, 2026-09-23).

    One implementation, executed by
    tests/test_updated_reason_is_append_only.py against a real row, is the
    only form that guards the BEHAVIOR. Callers must not re-implement the
    join; the test asserts they do not.

    Returns the new value, for logging.
    """
    row = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (record_id,)).fetchone()
    if row is None:
        raise ValueError(f"record {record_id!r} does not exist")
    existing = (row[0] or "").strip()
    joined = f"{existing} | {note}" if existing else note
    conn.execute("UPDATE records SET updated = ?, updated_reason = ? WHERE id = ?",
                 (today, joined, record_id))
    return joined


def validate_paper(paper: PaperRecord, check_local_paths: bool = True) -> None:
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

    `check_local_paths=False` skips ONE rule: that a hand-origin record's
    local file exists on THIS machine. Every other rule still runs. It is
    a property of the machine, not of the record, and exists for
    store/rebuild.py (Sprint 5 Task A, F30): rebuilding the store from the
    committed export must work on a CI runner that has no
    D:/Data/Harold/EvidenceBasedDB. Intake never passes it.
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
        # "<path> | <url>" keeps a resolvable-but-id-less page (PMLR, an
        # institutional repository) beside the file; the path comes first
        # and must exist. A URL that carried a DOI or arXiv id would have
        # been caught by the resolvable-id rule above.
        local = paper.access.split(_ACCESS_URL_SEP, 1)[0]
        if check_local_paths and not Path(local).exists():
            raise ValueError(
                f"paper {pid!r}: access {paper.access!r} is not an existing local path. "
                "ADR-0005 section 3: access is a DOI, an arXiv id, or a local path outside "
                "version control -- never the bare words 'local file'. An id-less web page "
                f"may follow the path as '<path>{_ACCESS_URL_SEP}<url>'."
            )
    if paper.citation and any(marker.lower() in paper.citation.lower() for marker in _AUDIT_MARKERS):
        raise ValueError(
            f"paper {pid!r}: citation carries audit-trail text ({', '.join(m for m in _AUDIT_MARKERS if m.lower() in paper.citation.lower())}). "
            "Corrections and notes belong in updated_reason or evidence, not in the citation."
        )
    # An api-origin record must let the door derive its citation, unless it
    # explicitly declares itself a replay. Without this, a fabricated
    # citation and title on a resolvable id passed unchallenged and without
    # a network call -- the dupont/kordzanganeh defect class, reinstated
    # (PR #30 review, 2026-09-22).
    if (paper.citation_origin == "api" and paper.citation is not None
            and paper.citation_source is not DERIVED_BY_DOOR
            and paper.citation_source != REPLAY):
        raise ValueError(
            f"paper {pid!r}: citation_origin='api' with a citation supplied by the caller. Leave "
            "citation=None and the door derives it from the source of record. If this is a fixture "
            "or a historical one-off whose API response is deliberately not re-fetched, declare "
            "citation_source=REPLAY so the exception is visible in the record and in the diff. The "
            "door's own marker is a sentinel object a caller cannot write."
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
    # The sentinel records that the DOOR filled this in, which is what lets
    # validate_paper tell a derived citation from one a caller supplied. An
    # object rather than a string precisely so a caller cannot forge it
    # (PR #30 round-2 review, 2026-09-23).
    return replace(paper, citation=rendered, value=paper.value or md.title,
                   citation_source=DERIVED_BY_DOOR)


def insert_paper(
    conn: sqlite3.Connection,
    paper: PaperRecord,
    fetcher: citations.Fetcher | None = None,
    check_local_paths: bool = True,
) -> PaperRecord:
    """The ONLY way a paper enters the store. Derives the citation from the
    source of record for api-origin papers (unless one was supplied), then
    validates every rule, then writes. Returns the record as written.
    `paper_fields.citation` no longer exists (Sprint 4 Task B, F25 B4/Q2):
    the citation lives once, in records.provenance, and the export reads it
    from there."""
    paper = derive_citation(paper, fetcher)
    validate_paper(paper, check_local_paths=check_local_paths)
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
