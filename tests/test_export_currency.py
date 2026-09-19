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
def test_live_store_has_been_migrated_off_the_citation_column():
    """PR #20 review guarded paper_fields.citation against diverging from
    records.provenance until F25 B4 dropped it. Sprint 4 Task B dropped it
    (scripts/migrate_paper_fields_drop_citation.py) and added the read-tier
    CHECK in the same rebuild. This guards that the LIVE store -- not just
    schema.sql, which create_store() reads for fresh stores -- actually
    carries the new shape, so a session working against an unmigrated
    evidence.db fails loudly here rather than at the first insert."""
    conn = connect(DB_PATH)
    try:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(paper_fields)")]
        assert "citation" not in cols, (
            f"live store still has paper_fields.citation ({cols}); run "
            "scripts/migrate_paper_fields_drop_citation.py --apply")
        ddl = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'paper_fields'").fetchone()["sql"]
        assert "checked_against_source IS NOT NULL" in ddl, "live store lacks the read-tier CHECK"
    finally:
        conn.close()
