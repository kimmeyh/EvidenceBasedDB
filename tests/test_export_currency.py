"""Guards that the COMMITTED export matches the store it claims to export
(Sprint 1 Task C acceptance criterion).

Per this repository's QUALITY_STANDARDS.md "verify the artifact you ship,
not a proxy for it": a test that regenerates its own fixture and then
checks it proves nothing about whether the committed file is current. This
test regenerates into a TEMP directory from the real store/evidence.db and
diffs against the real committed export/ directory.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "store" / "evidence.db"
EXPORT_DIR = ROOT / "export"


@pytest.mark.skipif(not DB_PATH.exists(), reason="store/evidence.db not present (gitignored; build it locally)")
def test_committed_export_matches_a_fresh_regeneration():
    conn = connect(DB_PATH)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            regenerate(conn, tmp)
            stale = []
            for name in ("contexts.json", "assertions.json", "acronyms.json", "terms.json", "papers.json"):
                fresh = (Path(tmp) / name).read_bytes()
                committed_path = EXPORT_DIR / name
                if not committed_path.exists():
                    stale.append(f"{name}: missing from export/")
                    continue
                committed = committed_path.read_bytes()
                if fresh != committed:
                    stale.append(f"{name}: differs from a fresh regeneration")
            assert not stale, (
                "export/ is stale relative to store/evidence.db: "
                f"{stale}. Run scripts/regenerate_export.py and commit the result."
            )
    finally:
        conn.close()


@pytest.mark.skipif(not DB_PATH.exists(), reason="store/evidence.db not present (gitignored; build it locally)")
def test_paper_citation_column_has_not_diverged_from_provenance():
    """PR #20 review (2026-09-19). Since Sprint 3 Task B the export reads a
    paper's citation from records.provenance, which leaves
    paper_fields.citation a write-only NOT NULL column that insert_paper()
    still populates. Until F25 B4 drops the column, this guard catches the
    only way it can do harm: a future writer setting the two differently,
    producing a silently ignored value in a column whose name promises it
    is the citation."""
    conn = connect(DB_PATH)
    try:
        diverged = [
            r["id"]
            for r in conn.execute(
                "SELECT r.id FROM records r JOIN paper_fields p ON p.record_id = r.id "
                "WHERE p.citation <> r.provenance"
            )
        ]
        assert not diverged, (
            f"paper_fields.citation differs from records.provenance on {diverged}; "
            "the export ignores paper_fields.citation, so this value is lost. "
            "F25 B4 removes the column; until then the two must agree."
        )
    finally:
        conn.close()
