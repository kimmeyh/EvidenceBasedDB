"""Export tests for the Evidence Based DB (Sprint 1 Task C).

ADR-0004 section 2: the export must be deterministic ("the diff is
reviewable") and it is the artifact, never hand-edited. These tests target
that property directly: a re-export of unchanged data must be
byte-identical, and a genuine data change must show up as a small diff, not
a reordered file.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import create_store  # noqa: E402
from store.export import export_class, regenerate  # noqa: E402


@pytest.fixture
def db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        conn = create_store(db_path)
        yield conn
        conn.close()


def _insert_term(conn, record_id, value="a term", reading_level=8):
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, reading_level, updated, updated_reason) "
        "VALUES (?, 'term', ?, 'a source', 'N/A', ?, '2026-09-15', 'created')",
        (record_id, value, reading_level),
    )
    conn.execute(
        "INSERT INTO term_fields (record_id, plain_definition) VALUES (?, 'a plain definition')",
        (record_id,),
    )
    conn.commit()


def test_export_class_returns_records_sorted_by_id(db):
    _insert_term(db, "zebra-term")
    _insert_term(db, "alpha-term")
    _insert_term(db, "mid-term")
    records = export_class(db, "term")
    assert [r["id"] for r in records] == ["alpha-term", "mid-term", "zebra-term"]


def test_export_empty_class_returns_empty_list(db):
    assert export_class(db, "assertion") == []


def test_regenerate_is_deterministic_byte_for_byte(db):
    """Two exports of the same unchanged data must be identical files, not
    merely equal in content -- ADR-0004's "diff is reviewable" claim
    depends on this holding at the byte level, since a spurious reorder
    would show as a diff with no data change behind it."""
    _insert_term(db, "term-a")
    _insert_term(db, "term-b")

    with tempfile.TemporaryDirectory() as out1, tempfile.TemporaryDirectory() as out2:
        regenerate(db, out1)
        regenerate(db, out2)
        for name in ("contexts.json", "assertions.json", "acronyms.json", "terms.json", "papers.json"):
            content1 = (Path(out1) / name).read_bytes()
            content2 = (Path(out2) / name).read_bytes()
            assert content1 == content2, f"{name} differs between two exports of unchanged data"


def test_export_files_end_with_exactly_one_trailing_newline(db):
    _insert_term(db, "term-a")
    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        for name in ("contexts.json", "terms.json"):
            text = (Path(out) / name).read_text(encoding="utf-8")
            assert text.endswith("\n") and not text.endswith("\n\n"), name


def test_export_is_valid_json_per_class(db):
    _insert_term(db, "term-a")
    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        for name in ("contexts.json", "assertions.json", "acronyms.json", "terms.json", "papers.json"):
            json.loads((Path(out) / name).read_text(encoding="utf-8"))


def test_a_data_change_produces_a_localized_diff_not_a_reorder(db):
    """The point of the export: changing one record's value must not
    reshuffle every other record's position in the file."""
    _insert_term(db, "term-a", value="original value")
    _insert_term(db, "term-b")
    _insert_term(db, "term-c")

    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        before = (Path(out) / "terms.json").read_text(encoding="utf-8").splitlines()

        db.execute("UPDATE records SET value = 'changed value' WHERE id = 'term-a'")
        db.commit()
        regenerate(db, out)
        after = (Path(out) / "terms.json").read_text(encoding="utf-8").splitlines()

    assert len(before) == len(after)
    changed_lines = sum(1 for b, a in zip(before, after) if b != a)
    assert changed_lines == 1, (
        f"expected exactly one changed line for a one-field update, got {changed_lines}"
    )


def test_contexts_export_matches_the_seeded_contexts(db):
    """create_store seeds the three pilot contexts plus Task D's
    domain-scale additions; see tests/test_contexts.py for the dedicated
    domain-scale context test suite."""
    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        contexts = json.loads((Path(out) / "contexts.json").read_text(encoding="utf-8"))
    assert {c["id"] for c in contexts} == {
        "hsbc-2026", "world", "method",
        "ml", "qc", "qml",
        "platform:dirac-3", "platform:braket", "platform:classiq",
    }


def test_paper_export_carries_yields_to_its_assertions(db):
    """ADR-0005 section 2b2: a paper is a source of assertions. The export
    must carry that link, not just the paper's own provenance fields."""
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('paper-1', 'paper', 'a paper', 'itself', 'N/A', '2026-09-15', 'created')"
    )
    db.execute(
        "INSERT INTO paper_fields (record_id, tier, citation, access, disposition, checked_against_source) "
        "VALUES ('paper-1', 'read', 'Cite, 2026', 'arXiv:0000.00000', 'why it matters', '2026-09-15, Claude, read in full')"
    )
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('assertion-1', 'assertion', 'a claim', 'paper-1', 'PROJ', '2026-09-15', 'created')"
    )
    db.execute("INSERT INTO paper_yields (paper_id, assertion_id) VALUES ('paper-1', 'assertion-1')")
    db.commit()

    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        papers = json.loads((Path(out) / "papers.json").read_text(encoding="utf-8"))

    assert papers[0]["yields"] == ["assertion-1"]
    assert papers[0]["checked_against_source"] == "2026-09-15, Claude, read in full"


def test_paper_checked_against_source_never_is_preserved_not_omitted(db):
    """ADR-0005 section 2: 'never' is a statement someone made and must
    appear in the export, distinct from a field that was never populated."""
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('paper-1', 'paper', 'a paper', 'itself', 'N/A', '2026-09-15', 'created')"
    )
    db.execute(
        "INSERT INTO paper_fields (record_id, tier, citation, access, disposition, checked_against_source) "
        "VALUES ('paper-1', 'seen', 'Cite, 2026', 'arXiv:0000.00000', 'not yet screened', 'never')"
    )
    db.commit()

    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        papers = json.loads((Path(out) / "papers.json").read_text(encoding="utf-8"))

    assert papers[0]["checked_against_source"] == "never"


def test_assertion_export_carries_citation_context_and_documents(db):
    """Regression test for Copilot PR #1 review finding 2: citation_context
    was accepted by the ingestion dataclass, populated by a real ingestion
    script, but had no schema column and no export path -- silently
    dropped between the store and the committed artifact."""
    db.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('a1', 'assertion', 'a claim', 'a source', 'N/A', '2026-09-15', 'created')"
    )
    db.execute(
        "INSERT INTO assertion_fields (record_id, units, rounding, citation_context) "
        "VALUES ('a1', 'AUPRC', '4 decimal places', '\"the exact sentence making the claim\"')"
    )
    db.execute("INSERT INTO assertion_documents (record_id, document) VALUES ('a1', 'docs/paper/appendix.md')")
    db.commit()

    with tempfile.TemporaryDirectory() as out:
        regenerate(db, out)
        assertions = json.loads((Path(out) / "assertions.json").read_text(encoding="utf-8"))

    assert assertions[0]["citation_context"] == '"the exact sentence making the claim"'
    assert assertions[0]["units"] == "AUPRC"
    assert assertions[0]["documents"] == ["docs/paper/appendix.md"]
