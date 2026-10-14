"""Schema tests for the Evidence Based DB store (Sprint 1 Task B).

Per this repository's guard-discipline standard (CLAUDE.md "Don't claim a
guard works because the suite is green. Prove it FAILS"): every constraint
tested here has a companion assertion that the constraint actually rejects
the violation it exists to catch, not merely that a valid row is accepted.
"""
from __future__ import annotations

import os
import re
import sqlite3
import tempfile
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import store as store_pkg  # noqa: E402
from store import (  # noqa: E402
    DEFAULT_STORE_DIR, NO_COMMITTED_EXPORT, connect, create_store, script_paths, store_dir,
)
from store.backup import default_backups_dir  # noqa: E402


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
        "platform:dirac-3s",  # ADR-0004 A8, 2026-10-12
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


def test_script_paths_derives_the_root_from_its_argument(monkeypatch):
    """F6 finding 5 (PR #1 review): ROOT resolution was copy-pasted across
    every script. A fake script path two directories under a synthetic repo
    root proves the function resolves ROOT relative to ITS ARGUMENT."""
    monkeypatch.delenv("EBDB_STORE_DIR", raising=False)
    monkeypatch.setattr(store_pkg, "_on_windows", lambda: True)
    fake_script = Path("/some/repo/scripts/whatever_ingest.py")
    root, db_path, export_dir = script_paths(str(fake_script))
    assert root.parts[-2:] == ("some", "repo")
    assert db_path == Path(DEFAULT_STORE_DIR) / "evidence.db"
    assert export_dir is NO_COMMITTED_EXPORT


def test_every_default_store_path_is_outside_the_repository_regression(monkeypatch):
    """ADR-0004 A7 (a): no script writes data inside the repository. The
    default is an ABSOLUTE Windows path (a drive and a root), and on
    Windows it resolves outside this checkout.

    Proven to fail by injection: with DEFAULT_STORE_DIR set to the
    repository's own store/ folder (the layout before A7), the Windows
    assertion went red. Off Windows the default is refused outright; that
    branch is the next test (Task B review, 2026-10-06: CI on Linux
    resolved the default INSIDE the checkout)."""
    monkeypatch.delenv("EBDB_STORE_DIR", raising=False)
    assert DEFAULT_STORE_DIR.drive and DEFAULT_STORE_DIR.root, "the default must be absolute on Windows"
    if os.name != "nt":
        return  # the Windows default cannot be resolved here; the next test covers this system
    repo = Path(__file__).resolve().parents[1]
    root, db_path, _ = script_paths(str(repo / "scripts" / "view.py"))
    assert root == repo
    assert repo not in db_path.resolve().parents
    assert repo not in default_backups_dir(db_path).resolve().parents


def test_off_windows_the_default_store_is_refused_regression(monkeypatch):
    """Off Windows, Path(r"D:\\...") is one relative segment, so the default
    would put evidence.db inside the current folder (the checkout, on CI).
    store_dir() must refuse it and name the override. Runs on every OS by
    taking the non-Windows branch explicitly.

    Proven to fail by injection, 2026-10-06: with the `if not
    _on_windows(): raise` branch removed from store_dir, this went red
    (DID NOT RAISE)."""
    monkeypatch.delenv("EBDB_STORE_DIR", raising=False)
    monkeypatch.setattr(store_pkg, "_on_windows", lambda: False)
    with pytest.raises(RuntimeError, match="EBDB_STORE_DIR"):
        store_dir()
    with pytest.raises(RuntimeError, match="EBDB_STORE_DIR"):
        script_paths(__file__)


def test_no_script_regenerates_an_export_after_its_write_regression():
    """ADR-0004 A7 (b) retired the committed export. Seventeen historical
    scripts committed their write and only THEN called
    regenerate(conn, EXPORT_DIR), which raises: the operator saw a traceback
    for a write that had landed, and might re-run a script that is not
    idempotent (Task B review, 2026-10-06). The calls were removed; this
    keeps them out.

    Proven to fail by injection, 2026-10-06: re-adding the call to
    scripts/sprint5_cvqboost_quote_fix.py turned this red naming that file."""
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    # Exempt: this migration hashes EXPORT_DIR BEFORE it writes, so it fails
    # before the write, not after it.
    exempt = {"migrate_paper_fields_drop_citation.py"}
    offenders = sorted(p.name for p in scripts.glob("*.py") if p.name not in exempt
                       and re.search(r"^\s*regenerate\(conn, EXPORT_DIR\)", p.read_text(encoding="utf-8"), re.M))
    assert offenders == [], f"scripts still regenerate the retired export after writing: {offenders}"


def test_the_store_location_can_be_overridden(monkeypatch, tmp_path):
    """ADR-0004 A7 (a), Q4 = 1: EBDB_STORE_DIR is the one override."""
    monkeypatch.setenv("EBDB_STORE_DIR", str(tmp_path))
    assert store_dir() == tmp_path
    assert script_paths(__file__)[1] == tmp_path / "evidence.db"


def test_no_export_can_be_written_inside_the_repository(tmp_path):
    """ADR-0004 A7 (b): the committed export is retired. A historical
    script's regenerate(conn, EXPORT_DIR) fails loudly, and so does any
    dump aimed inside the repository."""
    import pytest as _pytest
    from store.export import regenerate
    conn = create_store(tmp_path / "s.db")
    try:
        with _pytest.raises(RuntimeError, match="no committed export"):
            regenerate(conn, NO_COMMITTED_EXPORT)
        with _pytest.raises(RuntimeError, match="inside the repository"):
            regenerate(conn, Path(__file__).resolve().parents[1] / "export")
    finally:
        conn.close()
