"""Tests for the domain-scale contexts (Sprint 1 Task D).

ADR-0004 section 3b names contexts as the partitioning mechanism, never
tags, and is explicit that `qml` is "the intersection, which is NOT the
union" of `ml` and `qc`. These tests exercise that a record can claim `qml`
independently of `ml` and `qc` -- the schema must not silently derive `qml`
membership from the other two, which would collapse the distinction the
ADR insists on.
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import create_store  # noqa: E402


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


DOMAIN_SCALE_CONTEXTS = {
    "hsbc-2026",
    "world",
    "method",
    "ml",
    "qc",
    "qml",
    "platform:dirac-3",
    "platform:braket",
    "platform:classiq",
    "platform:dirac-3s",  # ADR-0004 A8, 2026-10-12
}


def test_all_domain_scale_contexts_are_seeded(db):
    ids = {row["id"] for row in db.execute("SELECT id FROM contexts")}
    assert ids == DOMAIN_SCALE_CONTEXTS


def test_every_seeded_context_has_a_description(db):
    rows = db.execute("SELECT id, description FROM contexts").fetchall()
    empty = [r["id"] for r in rows if not r["description"] or not r["description"].strip()]
    assert not empty, f"contexts with no description: {empty}"


def test_a_record_can_claim_qml_without_claiming_ml_or_qc(db):
    """The independence ADR-0004 section 3b insists on: qml is not derived
    from ml union qc, and the schema must not enforce any such derivation."""
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('r1', 'term', 'a qml-specific fact', 'a source', 'N/A', '2026-09-15', 'created')"
    )
    db.execute("INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', 'qml')")
    db.commit()

    claimed = {
        row["context_id"]
        for row in db.execute("SELECT context_id FROM record_contexts WHERE record_id = 'r1'")
    }
    assert claimed == {"qml"}


def test_a_record_can_claim_multiple_contexts_including_a_platform(db):
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('r1', 'assertion', 'device limit is 949 variables', 'a source', 'PROJ', '2026-09-15', 'created')"
    )
    for ctx in ("qc", "platform:dirac-3"):
        db.execute("INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', ?)", (ctx,))
    db.commit()

    claimed = {
        row["context_id"]
        for row in db.execute("SELECT context_id FROM record_contexts WHERE record_id = 'r1'")
    }
    assert claimed == {"qc", "platform:dirac-3"}


def test_claiming_an_unnamed_platform_context_is_rejected_until_added(db):
    """ADR-0004 section 3b: platform:ibm-q, platform:ionq etc. are 'as
    needed' and deliberately NOT seeded speculatively. A record cannot
    claim one until it is added as a real context -- the foreign key is
    what enforces 'add only when an assertion genuinely needs it'."""
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('r1', 'term', 'a fact', 'a source', 'N/A', '2026-09-15', 'created')"
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', 'platform:ibm-q')"
        )


def test_seeding_twice_does_not_duplicate_or_error(tmp_path):
    """seed_contexts.sql uses INSERT OR IGNORE specifically so it is safe
    to apply to an already-seeded store (create_store calls it once, but a
    future re-application must not be a foot-gun)."""
    from store import SEED_CONTEXTS_PATH

    db_path = tmp_path / "test.db"
    conn = create_store(db_path)
    conn.executescript(SEED_CONTEXTS_PATH.read_text(encoding="utf-8"))
    conn.commit()

    ids = [row["id"] for row in conn.execute("SELECT id FROM contexts")]
    assert len(ids) == len(set(ids)) == len(DOMAIN_SCALE_CONTEXTS)
    conn.close()
