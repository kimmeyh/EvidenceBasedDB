"""Sprint 2 Task D (F76): guard the shared vocabulary between ADR-0004 and
ADR-0005.

ADR-0005 section 2d deliberately points `applicability` at ADR-0004's own
context list rather than carrying its own enumeration -- "two lists naming
the same things is how the consumer repository's B1 variable count came
to read differently across documents." That was the right call, but
nothing previously enforced that the ADRs' stated list and the database's
actual `contexts` table stay in agreement. This test closes that gap.

Verified by injection: adding a context to the database that neither ADR
names (or removing one both ADRs name from the database) makes
test_database_contexts_match_adr_0004s_stated_list fail, naming the
mismatch.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import create_store  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ADR_0004 = ROOT / "docs" / "adr" / "0004-evidence-based-db.md"
ADR_0005 = ROOT / "docs" / "adr" / "0005-reference-library.md"

# The table ADR-0004 section 3b uses to state its domain-scale context
# list (the CURRENT set, not the "Pilot contexts" table earlier in the
# same document, which is deliberately smaller and explicitly labeled as
# history -- see the ADR's own "the domain-scale set is larger and is
# listed in the scope correction above").
_DOMAIN_SCALE_TABLE_HEADER = "| Context | Holds |"
_CONTEXT_ID_IN_TABLE_ROW = re.compile(r"^\|\s*`([a-z0-9:_-]+)`")


def _contexts_in_adr_0004_domain_scale_table() -> set[str]:
    """Parses ADR-0004's OWN domain-scale context table rather than
    hardcoding the expected list here -- a hardcoded list in the test
    would not catch the ADR's own text drifting from what the test
    expects, only the database drifting from a copy of the ADR.

    Excludes the ADR's own "as needed" placeholder row (currently
    `platform:ibm-q`, `platform:ionq`, ... | As needed): this row
    documents a NAMING PATTERN for future platform contexts, not a
    concrete context that should already be seeded -- Task D (Sprint 1)
    deliberately did not seed platform:ibm-q, and
    tests/test_contexts.py::test_claiming_an_unnamed_platform_context_is_
    rejected_until_added proves the schema rejects it until a real need
    adds it. A row whose "Holds" column is literally "As needed" is
    excluded on that basis rather than by hardcoding the specific id, so
    a future addition of another "as needed" row is excluded the same
    way without editing this parser again."""
    text = ADR_0004.read_text(encoding="utf-8")
    header_index = text.index(_DOMAIN_SCALE_TABLE_HEADER)
    # The domain-scale table is the FIRST such table after the "3b.
    # Contexts, not tags" section header; the "Pilot contexts" table
    # earlier in the document uses a three-column header
    # ("| Context | Holds | Example |") and is skipped by matching the
    # exact two-column header string above.
    table_text = text[header_index:]
    end = table_text.find("\n\n", 1)
    table_text = table_text[:end] if end != -1 else table_text
    ids = set()
    for line in table_text.splitlines():
        if "as needed" in line.lower():
            continue
        m = _CONTEXT_ID_IN_TABLE_ROW.match(line)
        if m:
            ids.add(m.group(1))
    return ids


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


def test_adr_0004_domain_scale_table_is_parseable_and_nonempty():
    """Sanity check on the parser itself, independent of the database --
    if this fails, the OTHER test in this file is meaningless (it would
    compare the database against an empty set and pass for the wrong
    reason)."""
    ids = _contexts_in_adr_0004_domain_scale_table()
    assert ids, "parsed zero context ids from ADR-0004's domain-scale table; the parser or the table format has drifted"
    # A known, stable subset that must appear in ANY correct parse of the
    # current table, so a parser regression that silently returns a
    # partial or wrong set is still caught even if it returns SOME ids.
    assert {"world", "qc", "qml", "hsbc-2026"} <= ids


def test_database_contexts_match_adr_0004s_stated_list(db):
    adr_ids = _contexts_in_adr_0004_domain_scale_table()
    db_ids = {row["id"] for row in db.execute("SELECT id FROM contexts")}
    assert db_ids == adr_ids, (
        f"database contexts and ADR-0004's domain-scale table have diverged. "
        f"In database but not ADR-0004: {db_ids - adr_ids}. "
        f"In ADR-0004 but not database: {adr_ids - db_ids}."
    )


def test_adr_0005_points_at_adr_0004s_context_list_rather_than_its_own():
    """ADR-0005 section 2d's own decision: applicability names context ids
    from ADR-0004's list, not a separate enumeration. This guards against
    someone adding a second, independent context list to ADR-0005 in a
    future edit -- exactly the duplication that produced the consumer
    repository's B1 variable-count drift (78 in three documents, 91 in
    two).

    CORRECTED (code review finding, 2026-09-18): the original version of
    this test only checked that the substring "ADR-0004" appeared
    somewhere in the file, which is true of routine cross-references and
    proved nothing about whether a second context table existed.
    Confirmed vacuous by injection: adding a full independent context
    table to ADR-0005 still left the substring present, so the test could
    not have failed on the exact defect its own docstring names.

    This version looks for the SAME two-column domain-scale header ADR-0004
    uses (`| Context | Holds |`), not the generic table-row pattern -- a
    first attempt at this fix matched ANY backtick-quoted table cell
    anywhere in the file, which false-failed against ADR-0005's own
    legitimate three-column "initial contexts" history table
    (`| Context | Holds | Example |`, its own pre-domain-scale record, kept
    deliberately per this repository's "revisions are recorded as dated
    amendments, never edits in place"). The two-column header is the
    specific shape a duplicated domain-scale enumeration would use, since
    that is what ADR-0004's own table looks like.
    """
    text = ADR_0005.read_text(encoding="utf-8")
    # Exact LINE match, not substring containment: the two-column header
    # "| Context | Holds |" is a textual prefix of the three-column header
    # "| Context | Holds | Example |", so `in` on the raw text would
    # false-positive on ADR-0005's own legitimate three-column history
    # table (see the docstring above).
    lines = {line.strip() for line in text.splitlines()}
    assert _DOMAIN_SCALE_TABLE_HEADER not in lines, (
        f"ADR-0005 contains a table with ADR-0004's own domain-scale header "
        f"({_DOMAIN_SCALE_TABLE_HEADER!r}). Section 2d's own decision is that "
        "applicability names context ids from ADR-0004's list, not a "
        "separate enumeration -- a second list here is exactly the "
        "duplication that produced the consumer repository's B1 "
        "variable-count drift."
    )
    assert "ADR-0004" in text, (
        "ADR-0005 no longer references ADR-0004 by name at all; the "
        "cross-reference this ADR's design depends on is missing."
    )


def test_a_record_naming_an_undefined_context_is_rejected(db):
    """The mechanism that makes 'ADRs and database agree' enforceable at
    write time, not just checkable after the fact: a context the ADR does
    not name cannot be claimed by a record, because it was never seeded
    (schema.sql's foreign key on record_contexts.context_id)."""
    import sqlite3

    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('r1', 'term', 'a fact', 'a source', 'N/A', '2026-09-17', 'created')"
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', 'platform:not-a-real-platform')"
        )
