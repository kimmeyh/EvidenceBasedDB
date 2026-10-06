"""Schema tests for the Evidence Based DB store (Sprint 1 Task B).

Per this repository's guard-discipline standard (CLAUDE.md "Don't claim a
guard works because the suite is green. Prove it FAILS"): every constraint
tested here has a companion assertion that the constraint actually rejects
the violation it exists to catch, not merely that a valid row is accepted.
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import connect, create_store, script_paths  # noqa: E402


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


def test_create_store_builds_all_tables(db):
    tables = {
        row["name"]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    expected = {
        "contexts",
        "records",
        "record_contexts",
        "prerequisites",
        "assertion_fields",
        "assertion_documents",
        "acronym_fields",
        "term_fields",
        "term_see_also",
        "paper_fields",
        "paper_applicability",
        "paper_yields",
        "assertion_relations",
    }
    assert expected <= tables


def test_pilot_and_domain_scale_contexts_are_seeded(db):
    """create_store seeds schema.sql's three pilot contexts (hsbc-2026,
    world, method) AND seed_contexts.sql's domain-scale additions (Sprint 1
    Task D, team lead 2026-09-15: the domain-scale set confirmed needed by
    end of Sprint 1). See tests/test_contexts.py for the full domain-scale
    context test suite; this test only guards that create_store applies
    both scripts."""
    ids = {row["id"] for row in db.execute("SELECT id FROM contexts")}
    assert ids == {
        "hsbc-2026", "world", "method",
        "ml", "qc", "qml",
        "platform:dirac-3", "platform:braket", "platform:classiq",
    }


def test_create_store_refuses_to_overwrite_existing_file(tmp_path):
    db_path = tmp_path / "existing.db"
    create_store(db_path).close()
    with pytest.raises(FileExistsError):
        create_store(db_path)


def test_foreign_keys_are_enabled_on_connect(db):
    row = db.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1


# ---------------------------------------------------------------------
# class CHECK constraint: valid values accepted, invalid rejected.
# ---------------------------------------------------------------------


def _insert_minimal_record(conn, record_id="r1", record_class="term", evidence_tag="N/A"):
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES (?, ?, 'a value', 'a source', ?, '2026-09-15', 'created')",
        (record_id, record_class, evidence_tag),
    )


def test_class_accepts_all_four_documented_values(db):
    for i, cls in enumerate(["assertion", "acronym", "term", "paper"]):
        _insert_minimal_record(db, record_id=f"r{i}", record_class=cls)
    db.commit()
    assert db.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 4


def test_class_rejects_a_value_outside_the_four(db):
    """Proves the CHECK constraint is live, not merely present in the DDL."""
    with pytest.raises(sqlite3.IntegrityError):
        _insert_minimal_record(db, record_class="glossary-entry")


def test_evidence_tag_rejects_a_value_outside_the_four(db):
    with pytest.raises(sqlite3.IntegrityError):
        _insert_minimal_record(db, evidence_tag="MEASURED")


def test_certainty_rejects_a_percentage(db):
    """ADR-0004 amendment A2: confidence-as-percentage was replaced by
    certainty as one of four GRADE levels. A numeric value must be rejected,
    not silently accepted as a fifth level."""
    _insert_minimal_record(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE records SET certainty = '72%' WHERE id = 'r1'")


def test_certainty_accepts_the_four_grade_levels(db):
    for level in ("high", "moderate", "low", "very-low"):
        _insert_minimal_record(db, record_id=f"cert-{level}")
    db.commit()
    for level in ("high", "moderate", "low", "very-low"):
        db.execute(
            "UPDATE records SET certainty = ? WHERE id = ?", (level, f"cert-{level}")
        )
    db.commit()


def test_reading_level_rejects_below_8(db):
    _insert_minimal_record(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE records SET reading_level = 7 WHERE id = 'r1'")


def test_reading_level_rejects_above_20(db):
    _insert_minimal_record(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE records SET reading_level = 21 WHERE id = 'r1'")


def test_reading_level_accepts_the_phd_ceiling(db):
    _insert_minimal_record(db)
    db.execute("UPDATE records SET reading_level = 20 WHERE id = 'r1'")
    db.commit()


# ---------------------------------------------------------------------
# Foreign keys: proven to actually block an orphan, not just declared.
# ---------------------------------------------------------------------


def test_record_contexts_rejects_an_unknown_context(db):
    _insert_minimal_record(db)
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', 'no-such-context')"
        )


def test_record_contexts_accepts_a_pilot_context(db):
    _insert_minimal_record(db)
    db.commit()
    db.execute("INSERT INTO record_contexts (record_id, context_id) VALUES ('r1', 'world')")
    db.commit()


def test_prerequisites_rejects_self_reference(db):
    """A record cannot be its own prerequisite -- the escalation ladder's
    rungs must form a DAG, and a self-loop is the smallest possible cycle."""
    _insert_minimal_record(db)
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO prerequisites (record_id, prerequisite_id) VALUES ('r1', 'r1')"
        )


def test_assertion_relations_rejects_self_reference(db):
    _insert_minimal_record(db, record_id="a1", record_class="assertion")
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) "
            "VALUES ('a1', 'a1', 'supports')"
        )


def test_assertion_relations_rejects_a_relation_outside_the_two_named(db):
    _insert_minimal_record(db, record_id="a1", record_class="assertion")
    _insert_minimal_record(db, record_id="a2", record_class="assertion")
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) "
            "VALUES ('a1', 'a2', 'mentions')"
        )


def test_assertion_relations_accepts_supports_and_contradicts(db):
    _insert_minimal_record(db, record_id="a1", record_class="assertion")
    _insert_minimal_record(db, record_id="a2", record_class="assertion")
    _insert_minimal_record(db, record_id="a3", record_class="assertion")
    db.commit()
    db.execute(
        "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES ('a1', 'a2', 'supports')"
    )
    db.execute(
        "INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES ('a1', 'a3', 'contradicts')"
    )
    db.commit()


def test_paper_fields_rejects_a_tier_outside_the_three_named(db):
    _insert_minimal_record(db, record_id="p1", record_class="paper")
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO paper_fields (record_id, tier, access, disposition) "
            "VALUES ('p1', 'skimmed', 'access', 'why')"
        )


def test_paper_fields_accepts_the_three_named_tiers(db):
    """'read' carries checked_against_source because the Sprint 4 Task B
    CHECK (decision Q2) refuses a read-tier row without it; the tier
    itself is what this test is about."""
    for i, tier in enumerate(["seen", "screened", "read"]):
        rid = f"p{i}"
        _insert_minimal_record(db, record_id=rid, record_class="paper")
        db.execute(
            "INSERT INTO paper_fields (record_id, tier, access, disposition, checked_against_source) "
            "VALUES (?, ?, 'access', 'why', ?)",
            (rid, tier, "never" if tier == "read" else None),
        )
    db.commit()


def test_paper_fields_checked_against_source_accepts_the_literal_never(db):
    """ADR-0005 section 2: 'never' is a valid, meaningful value distinct
    from NULL -- it is a statement someone made, not an absence."""
    _insert_minimal_record(db, record_id="p1", record_class="paper")
    db.execute(
        "INSERT INTO paper_fields (record_id, tier, access, disposition, checked_against_source) "
        "VALUES ('p1', 'seen', 'access', 'why', 'never')"
    )
    db.commit()
    row = db.execute(
        "SELECT checked_against_source FROM paper_fields WHERE record_id = 'p1'"
    ).fetchone()
    assert row["checked_against_source"] == "never"


def test_paper_fields_has_no_citation_column(db):
    """Sprint 4 Task B (F25 B4, Q2 = drop): the citation lives once, in
    records.provenance."""
    cols = [r["name"] for r in db.execute("PRAGMA table_info(paper_fields)")]
    assert "citation" not in cols
    assert cols == ["record_id", "tier", "access", "disposition", "evidence", "mined_by", "checked_against_source",
                    "metadata_provider", "coi"]  # the last two: ADR-0005 A4, Sprint 6 Task E


def test_paper_fields_check_rejects_read_tier_without_checked_against_source(db):
    """The read-tier rule now holds at the column, not only in
    validate_paper()/set_tier(): a raw INSERT or UPDATE cannot make a
    'read' row with NULL checked_against_source (Copilot PR #20 review,
    landed with the Sprint 4 Task B rebuild)."""
    _insert_minimal_record(db, record_id="p1", record_class="paper")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO paper_fields (record_id, tier, access, disposition) VALUES ('p1', 'read', 'access', 'why')"
        )
    db.execute("INSERT INTO paper_fields (record_id, tier, access, disposition) VALUES ('p1', 'seen', 'access', 'why')")
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE paper_fields SET tier = 'read' WHERE record_id = 'p1'")
    db.execute("UPDATE paper_fields SET tier = 'read', checked_against_source = 'never' WHERE record_id = 'p1'")
    db.commit()


def test_script_paths_derives_db_and_export_paths_from_repo_root():
    """F6 finding 5 (PR #1 review): ROOT/DB_PATH/EXPORT_DIR resolution was
    copy-pasted near-identically across every ingestion/correction script.
    A fake script path two directories under a synthetic repo root proves
    the function resolves relative to ITS ARGUMENT, not to this test
    file's own location, which is the exact bug a hardcoded parents[N]
    depth could introduce silently."""
    fake_script = Path("/some/repo/scripts/whatever_ingest.py")
    root, db_path, export_dir = script_paths(str(fake_script))
    # .resolve() prefixes the current drive on Windows, so compare parts
    # rather than full equality against a rootless POSIX-style path.
    assert root.parts[-2:] == ("some", "repo")
    assert db_path.parts[-3:] == ("repo", "store", "evidence.db")
    assert export_dir.parts[-2:] == ("repo", "export")


def test_script_paths_matches_this_repository_layout():
    """The real store/evidence.db and export/ directories must actually
    exist at the paths this function derives for a script under THIS
    repository's scripts/ directory -- not just at some synthetic path."""
    real_script = Path(__file__).resolve().parents[1] / "scripts" / "view.py"
    root, db_path, export_dir = script_paths(str(real_script))
    assert (root / "CLAUDE.md").exists()
    assert db_path.parent.name == "store"
    assert export_dir.name == "export"
