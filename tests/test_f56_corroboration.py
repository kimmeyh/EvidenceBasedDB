"""F56 (Sprint 9 Task I): the computed "corroborated" flag (ADR-0004 A9).

A supporter counts only when it is rated at the same or a higher certainty
and is independent: different papers, authors and organizations. A same-
vendor pair never counts, nor does a vendor's own claim whose supporter
cannot show its organization. The flag never changes stored certainty.
Synthetic store; no network."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper, record_probe  # noqa: E402
from store.resolvers import corroboration  # noqa: E402
from tests.conftest import build_synthetic_store  # noqa: E402

COMMON = dict(citation_origin="api", citation_source="replay", context="qml", updated="2026-10-15",
              updated_reason="fixture")


def _paper(conn, pid: str, authors: str, affiliations: str | None = None) -> None:
    insert_paper(conn, PaperRecord(
        id=pid, tier="seen", access=f"arXiv:2601.{abs(hash(pid)) % 90000 + 10000}", value=pid,
        citation=f'{authors}, "{pid}," arXiv, 2026-01-01', disposition="fixture", **COMMON))
    if affiliations:
        record_probe(conn, pid, "affiliations", affiliations, "Crossref", "2026-10-15")


def _claim(conn, aid: str, paper: str, certainty: str, claim_type: str = "positive") -> None:
    insert_assertion(conn, AssertionRecord(
        id=aid, value=f"value of {aid}", provenance=f"{paper}, p.1", evidence_tag="N/A", context="qml",
        certainty=certainty, certainty_reasons="fixture", derivation="extracted", claim_type=claim_type,
        citation_context='"q" (p.1)', updated="2026-10-15", updated_reason="fixture"), yielded_by=paper)


def _supports(conn, src: str, dst: str) -> None:
    conn.execute("INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) "
                 "VALUES (?, ?, 'supports')", (src, dst))


@pytest.fixture
def store(tmp_path):
    db = build_synthetic_store(tmp_path / "evidence.db")
    conn = connect(db)
    _paper(conn, "p-indep-a", "Adams, A., Brown, B.")
    _paper(conn, "p-indep-b", "Clark, C.")
    _claim(conn, "x-indep", "p-indep-a", "high")
    _claim(conn, "y-indep", "p-indep-b", "high")
    _supports(conn, "y-indep", "x-indep")
    # Same vendor: different authors, both affiliated with QCi.
    _paper(conn, "p-qci-1", "Nguyen, L., Sua, Y.M.", "Quantum Computing Inc., Leesburg, VA")
    _paper(conn, "p-qci-2", "Robinson, J.", "Quantum Computing Inc")
    _claim(conn, "x-vendor", "p-qci-1", "moderate", "vendor-self-claim")
    _claim(conn, "y-vendor", "p-qci-2", "high")
    _supports(conn, "y-vendor", "x-vendor")
    # A vendor's own claim, and the supporter names no organization.
    _paper(conn, "p-vendor-3", "Wang, P.")
    _paper(conn, "p-unknown", "Lee, K.")
    _claim(conn, "x-vendor-2", "p-vendor-3", "low", "vendor-self-claim")
    _claim(conn, "y-unknown", "p-unknown", "high")
    _supports(conn, "y-unknown", "x-vendor-2")
    # Shared author; lower-rated supporter; same paper.
    _paper(conn, "p-shared-1", "Doe, J., Eve, E.")
    _paper(conn, "p-shared-2", "Doe, J.")
    _claim(conn, "x-shared", "p-shared-1", "moderate")
    _claim(conn, "y-shared", "p-shared-2", "high")
    _supports(conn, "y-shared", "x-shared")
    _claim(conn, "y-lower", "p-indep-b", "low")
    _supports(conn, "y-lower", "x-indep")
    _claim(conn, "y-same-paper", "p-indep-a", "high")
    _supports(conn, "y-same-paper", "x-indep")
    # The live store's two misses (2026-10-15): one vendor under two names,
    # and two project documents cited by repository name, not by person.
    _paper(conn, "p-alias-1", "Smith, A.", "QCi")
    _paper(conn, "p-alias-2", "Jones, B.", "Quantum Computing Inc., Leesburg, VA")
    _claim(conn, "x-alias", "p-alias-1", "moderate")
    _claim(conn, "y-alias", "p-alias-2", "moderate")
    _supports(conn, "y-alias", "x-alias")
    _paper(conn, "p-repo-1", "hsbc-quantum-fraud-2026")
    _paper(conn, "p-repo-2", "hsbc-qfraud-phase2")
    _claim(conn, "x-repo", "p-repo-1", "moderate")
    _claim(conn, "y-repo", "p-repo-2", "high")
    _supports(conn, "y-repo", "x-repo")
    conn.commit()
    yield conn
    conn.close()


def _why(result, x, y) -> str:
    return dict(result[x]["by"] + result[x]["not_counted"])[y]


def test_an_independent_supporter_at_equal_certainty_corroborates(store):
    """Proven to fail by injection, 2026-10-15: with every pair read as not
    both from papers, the list came back empty."""
    result = corroboration(store)
    assert [y for y, _ in result["x-indep"]["by"]] == ["y-indep"]


def test_a_same_vendor_pair_never_counts(store):
    """Proven to fail by injection, 2026-10-15: with the shared-organization
    check removed from corroboration(), y-vendor was counted as
    corroborating x-vendor."""
    result = corroboration(store)
    assert result["x-vendor"]["by"] == []
    assert _why(result, "x-vendor", "y-vendor") == "shared organization(s): qci, quantum computing"


def test_a_vendor_claim_needs_both_organizations_named(store):
    """Proven to fail by injection, 2026-10-15: with the vendor rule removed,
    y-unknown was counted as corroborating x-vendor-2."""
    result = corroboration(store)
    assert result["x-vendor-2"]["by"] == []
    assert "independence is not shown" in _why(result, "x-vendor-2", "y-unknown")


def test_shared_authors_lower_ratings_and_the_same_paper_never_count(store):
    """Proven to fail by injection, 2026-10-15: with the shared-author check
    removed, x-shared's supporter read as independent."""
    result = corroboration(store)
    assert _why(result, "x-shared", "y-shared") == "shared author(s): doe"
    assert _why(result, "x-indep", "y-lower") == "rated lower (low against high)"
    assert _why(result, "x-indep", "y-same-paper") == "same paper (p-indep-a)"


def test_one_vendor_under_two_names_is_one_organization(store):
    """Proven to fail by injection, 2026-10-15: with the initials key
    removed from _org_keys, y-alias was counted as corroborating x-alias."""
    result = corroboration(store)
    assert result["x-alias"]["by"] == []
    assert _why(result, "x-alias", "y-alias") == "shared organization(s): qci"


def test_documents_cited_by_repository_name_never_count(store):
    """Proven to fail by injection, 2026-10-15: with the named-author
    requirement relaxed to "a person or an organization", y-repo was counted
    as corroborating x-repo."""
    result = corroboration(store)
    assert _why(result, "x-repo", "y-repo") == "no named author on one side"


def test_the_derived_key_exports_and_the_dump_rebuilds_byte_identically(store, tmp_path):
    """Review of 79ae0d4: the CI round trip never exported corroborated_by
    (the synthetic store flags nothing), so only the live test covered it.
    Proven to fail by injection, 2026-10-15: with corroborated_by removed
    from rebuild.DERIVED_KEYS, the rebuild refused the dump."""
    from store.export import regenerate
    from store.rebuild import rebuild_and_compare
    regenerate(store, tmp_path / "dump")
    exported = json.loads((tmp_path / "dump" / "assertions.json").read_text(encoding="utf-8"))
    assert [r["corroborated_by"] for r in exported if r["id"] == "x-indep"] == [
        [{"id": "y-indep", "why": "different papers and authors; organizations not recorded on one side, so not "
                                  "compared"}]]
    assert rebuild_and_compare(tmp_path / "dump", check_local_paths=False) == []


def test_parenthesized_affiliations_and_accents_are_read(store):
    """Review of 79ae0d4: "Neven, H. (Google Inc.)" lost the author and
    misread the organization, and accented spellings of one author did not
    match. Proven to fail by injection, 2026-10-15: with _fold returning its
    input unchanged, brandao and brandão were two authors and y-accent
    counted; with the parenthesis split removed, y-paren counted."""
    _paper(store, "p-paren-1", "Matuszek, C. (Cycorp), Lee, D. (MIT)")
    _paper(store, "p-paren-2", "Witbrock, M.", "Cycorp Inc.")
    _claim(store, "x-paren", "p-paren-1", "moderate")
    _claim(store, "y-paren", "p-paren-2", "high")
    _supports(store, "y-paren", "x-paren")
    _paper(store, "p-accent-1", "Brandão, F.G.S.L., Smith, J.")
    _paper(store, "p-accent-2", "Brandao, F.G.S.L.")
    _claim(store, "x-accent", "p-accent-1", "moderate")
    _claim(store, "y-accent", "p-accent-2", "high")
    _supports(store, "y-accent", "x-accent")
    _paper(store, "p-dwave-1", "Neven, H. (Google Inc.), Macready, W.G. (D-Wave Systems Inc.)")
    _paper(store, "p-dwave-2", "King, A.D.", "D-Wave")
    _claim(store, "x-dwave", "p-dwave-1", "moderate")
    _claim(store, "y-dwave", "p-dwave-2", "high")
    _supports(store, "y-dwave", "x-dwave")
    store.commit()
    result = corroboration(store)
    assert _why(result, "x-paren", "y-paren") == "shared organization(s): cycorp"
    assert _why(result, "x-accent", "y-accent") == "shared author(s): brandao"
    assert _why(result, "x-dwave", "y-dwave") == "shared organization(s): d wave"


def test_view_shows_the_flag_beside_certainty(store, tmp_path):
    db = tmp_path / "evidence.db"
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "view.py"), "assertion", "x-vendor", "--json"],
                         capture_output=True, text=True, env={**os.environ, "EBDB_STORE_DIR": str(db.parent)}, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["certainty"] == "moderate"
    assert data["corroborated_by"] == []
    assert data["supporters_not_counted"][0]["id"] == "y-vendor"
