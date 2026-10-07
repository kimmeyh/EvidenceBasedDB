"""Shared test setup.

Sprint 6 retrospective I1 (2026-10-05): arXiv pacing keeps ONE clock per
process (`store.citations._last_arxiv_request`), so a test that sends an
arXiv request would otherwise make the next test wait or measure against
it. Each test starts with no arXiv request on record.

ADR-0004 A7 (Sprint 7 Task B, F58, 2026-10-06): there is no committed export.
Two kinds of test follow from that:

- MECHANISM tests (the door, the dump and its rebuild, backups, restore,
  retention) build a small synthetic store with `synthetic_store` and run
  everywhere, CI included.
- Checks of the REAL data use `live_conn`, `live_copy` or `live_export` and
  must carry `@pytest.mark.live_store`. Locally a missing store FAILS them,
  never skips them. CI cannot reach the store and deselects the marker by
  name in .github/workflows/ci.yml. A live fixture used by an unmarked test
  fails, so CI's deselection cannot silently miss one.
"""
from __future__ import annotations

import sqlite3
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import citations, connect, create_store, store_dir  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import (  # noqa: E402
    AssertionRecord, PaperRecord, add_found_via, add_read, add_source_link, insert_assertion, insert_paper,
    record_probe,
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live_store: reads the real store outside the repository (ADR-0004 A7); "
                   "fails locally when it is missing; deselected on CI")


@pytest.fixture(autouse=True)
def _fresh_arxiv_clock(monkeypatch):
    monkeypatch.setattr(citations, "_last_arxiv_request", float("-inf"))


# ------------------------------------------------------------------ live store

def _live_db(request) -> Path:
    if request.node.get_closest_marker("live_store") is None:
        pytest.fail(f"{request.node.nodeid} reads the live store; mark it @pytest.mark.live_store "
                    "so CI's deselection covers it")
    db = store_dir() / "evidence.db"
    if not db.exists():
        pytest.fail(f"live store {db} is missing (ADR-0004 A7: it lives outside the repository; "
                    "set EBDB_STORE_DIR if it is elsewhere). A live_store test fails, never skips.")
    return db


def _open_read_only(db: Path) -> sqlite3.Connection:
    """Every live fixture opens the live store this way, so no test can
    write to it (Task B review, 2026-10-06: live_copy and live_export
    opened it read-write)."""
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


@pytest.fixture
def live_conn(request):
    """The live store, opened READ-ONLY."""
    conn = _open_read_only(_live_db(request))
    yield conn
    conn.close()


@pytest.fixture
def live_copy(request, tmp_path) -> Path:
    """A copy of the live store taken with the SQLite backup API, for tests
    that must write. The live store itself is never written."""
    db = _live_db(request)
    target = tmp_path / "live_copy.db"
    src, dst = _open_read_only(db), sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return target


@pytest.fixture(scope="session")
def _live_dump_once(tmp_path_factory) -> dict:
    """The live store dumped ONCE per session (1,875 papers take seconds).
    Reached only through `live_export`, which checks the marker first."""
    return {"dir": None, "factory": tmp_path_factory}


@pytest.fixture
def live_export(request, _live_dump_once) -> Path:
    """An on-demand dump of the live store, for tests that read the JSON.
    Shared by the whole session, so its files are made read-only: a test
    that changes one fails at once instead of corrupting every later live
    test (Task B review, 2026-10-06). Copy it before changing anything."""
    db = _live_db(request)
    if _live_dump_once["dir"] is None:
        out = _live_dump_once["factory"].mktemp("live_export")
        conn = _open_read_only(db)
        try:
            regenerate(conn, out)
        finally:
            conn.close()
        for f in out.iterdir():
            f.chmod(stat.S_IREAD)
        _live_dump_once["dir"] = out
    return _live_dump_once["dir"]


# ------------------------------------------------------------------ synthetic store

def build_synthetic_store(db: Path) -> Path:
    """A small store that exercises every record shape the door writes:
    papers at each tier, applicability, yields, reads, routes, probes,
    source links, assertions with relations and a computed cap."""
    conn = create_store(db)
    common = dict(citation_origin="api", citation_source="replay", context="qml",
                  updated="2026-10-06", updated_reason="synthetic fixture")
    insert_paper(conn, PaperRecord(
        id="alpha-2024-first-paper", tier="read", access="arXiv:2401.00001", value="First paper",
        citation="Alpha, A., \"First paper,\" arXiv:2401.00001v1, 2024-01-02", disposition="A fixture paper",
        checked_against_source="2026-10-06, Claude, pp.1-2 directly",
        reads=[("Claude", "2026-10-06", "partial", "pp.1-2")],
        applicability=[("qml", "fixture rationale -- p.1 abstract")], **common))
    insert_paper(conn, PaperRecord(
        id="beta-2025-second-paper", tier="seen", access="arXiv:2501.00002", value="Second paper",
        citation="Beta, B., \"Second paper,\" arXiv:2501.00002v1, 2025-01-03", disposition="Another fixture paper",
        found_via=[("fixture collection", "Beta 2025")], **common))
    insert_paper(conn, PaperRecord(
        id="gamma-repo-github-repo", tier="seen", access="https://github.com/gamma/repo", value="Gamma repo",
        citation="gamma, \"Gamma repo,\" GitHub repository gamma/repo, created 2024-01-01, https://github.com/gamma/repo",
        disposition="Code repository: fixture", **common))
    add_found_via(conn, "alpha-2024-first-paper", "fixture collection", "Alpha 2024")
    record_probe(conn, "alpha-2024-first-paper", "publication_status", "published", "arXiv", "2026-10-06")
    record_probe(conn, "beta-2025-second-paper", "publication_status", "preprint", "arXiv", "2026-10-06")
    add_source_link(conn, "gamma-repo-github-repo", "alpha-2024-first-paper", "code-of", "Code is at the repo.")
    for aid, cert in (("claim-one", "low"), ("claim-two", "high")):
        insert_assertion(conn, AssertionRecord(
            id=aid, value=f"value of {aid}", provenance="alpha-2024-first-paper, p.1", evidence_tag="N/A",
            context="qml", certainty=cert, certainty_reasons="fixture", derivation="extracted",
            citation_context='"a quoted sentence" (p.1)', updated="2026-10-06", updated_reason="fixture"),
            yielded_by="alpha-2024-first-paper")
    insert_assertion(conn, AssertionRecord(
        id="learning-fixture", value="a synthesis", provenance="synthesis of the assertions that support it",
        evidence_tag="N/A", context="qml", certainty="moderate", certainty_reasons="fixture",
        derivation="synthesized", updated="2026-10-06", updated_reason="fixture"))
    for source in ("claim-one", "claim-two"):
        conn.execute("INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) "
                     "VALUES (?, 'learning-fixture', 'supports')", (source,))
    add_read(conn, "beta-2025-second-paper", "agent", "2026-10-06", "abstract")
    conn.commit()
    conn.close()
    return db


@pytest.fixture
def synthetic_store(tmp_path) -> Path:
    return build_synthetic_store(tmp_path / "evidence.db")


@pytest.fixture
def synthetic_dump(synthetic_store, tmp_path) -> Path:
    """An on-demand dump of the synthetic store."""
    conn = connect(synthetic_store)
    try:
        regenerate(conn, tmp_path / "synthetic_dump")
    finally:
        conn.close()
    return tmp_path / "synthetic_dump"
