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

import os
import shlex
import sqlite3
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import store  # noqa: E402
from store import citations, connect, create_store, quotes, store_dir  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import (  # noqa: E402
    AssertionRecord, PaperRecord, add_found_via, add_read, add_source_link, insert_assertion, insert_paper,
    record_probe,
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live_store: reads the real store outside the repository (ADR-0004 A7); "
                   "fails locally when it is missing; deselected on CI")
    if not getattr(sys, "_ebdb_local_only_hook", False):
        sys.addaudithook(_refuse_local_only)
        sys._ebdb_local_only_hook = True


# ------------------------------------------------------------------ local-only resources

# Sprint 9 retrospective I7 (team lead, 2026-10-18, Q1 = 2): CI was red for
# three days because three tests read local PDFs (pdftotext) or the local
# Phase 2 repository without the live_store marker, and every local run was
# green. An unmarked test now finds these resources missing on this machine
# too, exactly as CI does: pdftotext and every path under the data folder or
# a sibling repository raise FileNotFoundError. So the mislabel fails at the
# desk, not on CI. Reaches this process only (opens, directory listings,
# sqlite connects, subprocess and os launches); a child process is not
# watched.
#
# LIMITS (PR #88 review, 2026-10-18), each still caught by CI, as before:
# - exists(), is_file() and stat() raise no audit event, so an unmarked
#   existence check on a local path passes here.
# - The guard is on only while an unmarked test runs: module-level code,
#   parametrize lists, skipif conditions and module- or session-scoped
#   fixtures run before it.
# - A store moved with EBDB_STORE_DIR is not watched; the default data
#   folder is (tests point that variable at temporary folders).
_ROOT = Path(__file__).resolve().parents[1]
_LOCAL_ONLY_ROOTS = (str(store.DEFAULT_STORE_DIR.parent), _ROOT.parent)  # data folder; sibling repos
_local_only = {"refuse": False}


def _norm(p) -> str:
    return os.path.normcase(os.path.abspath(p))


def is_local_only(path) -> bool:
    """True for a path CI cannot have: under the data folder, or under a
    sibling repository (the folder holding this repository, minus this
    repository)."""
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, (str, os.PathLike)):
        return False
    text = str(path)
    if text.startswith("file:"):  # a sqlite URI
        text = text[5:].split("?", 1)[0]
    if not text or text == ":memory:":
        return False
    target, repo = _norm(text), _norm(_ROOT)
    if target == repo or target.startswith(repo + os.sep):
        return False
    return any(target == _norm(r) or target.startswith(_norm(r) + os.sep) for r in _LOCAL_ONLY_ROOTS)


def _refuse_local_only(event: str, args: tuple) -> None:
    if not _local_only["refuse"]:
        return
    paths: list = []
    if event in ("open", "os.listdir", "os.scandir", "sqlite3.connect"):
        paths = [args[0]] if args else []
    elif event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.spawn", "os.startfile"):
        if event == "subprocess.Popen":
            executable, argv, cwd = args[0], args[1], args[2]
        elif event == "os.system":
            executable, argv, cwd = None, args[0], None
        elif event == "os.spawn":
            executable, argv, cwd = args[1], args[2], None  # (mode, path, args, env)
        else:
            executable, argv, cwd = args[0], (args[1] if len(args) > 1 else None), None
        if isinstance(argv, (str, bytes, os.PathLike)):
            # On Windows the event carries the list already joined into one
            # command line (first injection, 2026-10-18: pdftotext and a
            # Phase 2 `git -C` both passed until this split was added).
            line = os.fsdecode(argv)
            try:
                argv = [a.strip('"') for a in shlex.split(line, posix=False)]
            except ValueError:  # an unbalanced quote; the hook must never fail on its own parsing
                argv = [a.strip('"') for a in line.split()]
        else:
            argv = list(argv or [])
        argv = [os.fsdecode(a) if isinstance(a, (bytes, os.PathLike)) else a for a in argv]
        program = executable or (argv[0] if argv else "")
        if Path(os.fsdecode(program)).stem.lower() == "pdftotext":
            raise FileNotFoundError("pdftotext is not available to a test without @pytest.mark.live_store "
                                    "(CI has none; Sprint 9 retrospective I7)")
        # an option's value counts too: --in=D:\... (review, 2026-10-18)
        paths = [cwd, executable, *argv, *(a.split("=", 1)[1] for a in argv if isinstance(a, str) and "=" in a)]
    else:
        return
    for p in paths:
        if p is not None and is_local_only(p):
            raise FileNotFoundError(f"{p} is outside the repository and not on CI; mark the test "
                                    "@pytest.mark.live_store (Sprint 9 retrospective I7)")


@pytest.fixture(autouse=True)
def _local_only_resources(request):
    """Unmarked tests see the machine CI sees. A source read through
    `store.quotes` is refused before its cache is consulted, so a PDF read
    by an earlier live_store test cannot hide the read. (Until F100 the
    caches were emptied here instead, so every live test extracted its PDFs
    again: about 10 of the suite's 13 minutes.)"""
    if request.node.get_closest_marker("live_store") is not None:
        yield
        return

    def refuse(path):
        raise FileNotFoundError(f"{path}: a source read needs @pytest.mark.live_store (Sprint 9 retrospective I7)")

    quotes.READ_GUARD = refuse
    _local_only["refuse"] = True
    try:
        yield
    finally:
        _local_only["refuse"] = False
        quotes.READ_GUARD = None


@pytest.fixture(autouse=True)
def _fresh_arxiv_clock(monkeypatch):
    monkeypatch.setattr(citations, "_last_arxiv_request", float("-inf"))
    monkeypatch.setattr(citations, "_arxiv_requests_this_session", 0)  # the session cap's count (Sprint 7 Task C)


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
