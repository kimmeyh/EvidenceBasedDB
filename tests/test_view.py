"""Tests for scripts/view.py (Sprint 2 Task G, F3).

F3: an easy, CLI-startable way to view DB content -- three modes
(contexts, paper, assertion), plain text or --json, no server. Exercised
against a small synthetic store built with the same helpers production
uses (store.create_store, store.ingest), not the real 46-paper store, so
this suite passes independent of what the real store currently holds.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCRIPT = ROOT / "scripts" / "view.py"

from store import create_store  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper  # noqa: E402


def _run_view_cli(db_path: Path, args: list[str], console_encoding: str = "utf-8") -> subprocess.CompletedProcess:
    """Runs the REAL scripts/view.py as a subprocess against db_path, via a
    wrapper that monkeypatches DB_PATH before calling main() -- same
    pattern as tests/test_ingest_seed_set.py's `_run_script`, so the
    script under test is exactly what production runs.

    `console_encoding` lets a test simulate the actual Windows console
    default (cp1252) via PYTHONIOENCODING: without `sys.stdout.
    reconfigure(encoding="utf-8")`, Python's own stdout write would use
    that codepage and raise UnicodeEncodeError on non-cp1252 characters
    (which includes Greek letters -- cp1252 cannot represent them at
    all). Captured as raw BYTES rather than text: decoding the test's own
    capture as cp1252 would be just as lossy as the bug this test guards
    against, since the fix's whole point is that the script writes UTF-8
    regardless of PYTHONIOENCODING.
    """
    wrapper = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "import importlib.util\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('view', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r})\n"
        f"sys.argv = ['view.py'] + {args!r}\n"
        "raise SystemExit(mod.main())\n"
    )
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = console_encoding
    proc = subprocess.run(
        [sys.executable, "-c", wrapper],
        capture_output=True,
        env=env,
    )
    return subprocess.CompletedProcess(
        args=proc.args,
        returncode=proc.returncode,
        stdout=proc.stdout.decode("utf-8"),
        stderr=proc.stderr.decode("utf-8", errors="replace"),
    )


def _load_view_module():
    spec = importlib.util.spec_from_file_location("view", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _seed_store(db_path: Path):
    conn = create_store(db_path)

    insert_paper(
        conn,
        PaperRecord(
            id="test-paper-one",
            value="A Test Paper About QML",
            tier="read",
            citation="Tester, T., \"A Test Paper About QML\", 2026",
            citation_origin="api", citation_source="replay",  # fixture replays a rendered citation
            access="arXiv:0000.00002",
            disposition="fixture",
            context="qml",
            applicability=[("qml", "primary topic -- fixture"), ("qc", "uses a QC backend -- fixture")],
            checked_against_source="2026-09-17, fixture", reads=[("fixture", "2026-09-17", "full", "")],
        ),
    )
    insert_assertion(
        conn,
        AssertionRecord(
            id="test-assertion-two",
            value="A second assertion that contradicts the first",
            provenance="test-paper-one, p2",
            evidence_tag="N/A", derivation="extracted",
            context="qml",
            certainty="low",
            certainty_reasons="fixture",
            fidelity="exact",
            reading_level=10,
            documents=["test-paper-one"],
        ),
    )
    insert_assertion(
        conn,
        AssertionRecord(
            id="test-assertion-one",
            value="Test assertion value with unicode: café, αβγ",
            provenance="test-paper-one, p1",
            evidence_tag="N/A", derivation="extracted",
            context="qml",
            certainty="high",
            certainty_reasons="fixture",
            fidelity="exact",
            reading_level=10,
            documents=["test-paper-one"],
            contradicts=["test-assertion-two"],
        ),
        yielded_by="test-paper-one",
    )
    conn.commit()
    return conn


@pytest.fixture
def store_conn():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        conn = _seed_store(db_path)
        yield conn
        conn.close()


@pytest.fixture
def store_db_path():
    """Same seed data as store_conn, but yields a closed store's PATH
    instead of an open connection, for subprocess-based tests that open
    their own connection against the file (a second connection to an
    already-open sqlite3.Connection from the SAME process is fine, but a
    separate PROCESS needs the writer connection closed first to avoid
    Windows file-locking flakiness)."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        conn = _seed_store(db_path)
        conn.close()
        yield db_path


def test_contexts_list_reports_direct_and_applicability_counts(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_list(store_conn)
    qml = next(c for c in data["contexts"] if c["id"] == "qml")
    assert qml["direct_count"] >= 2
    qc = next(c for c in data["contexts"] if c["id"] == "qc")
    assert qc["applicability_count"] >= 1


def test_contexts_detail_lists_records_and_applicability_papers(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_detail(store_conn, "qml")
    ids = {r["id"] for r in data["records"]}
    assert "test-paper-one" in ids
    assert "test-assertion-one" in ids

    qc_data = mod.cmd_contexts_detail(store_conn, "qc")
    applicability_ids = {r["id"] for r in qc_data["papers_via_applicability"]}
    assert "test-paper-one" in applicability_ids


def test_contexts_detail_errors_on_unknown_context(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_detail(store_conn, "no-such-context")
    assert "error" in data


def test_paper_mode_includes_full_yielded_assertion_fields(store_conn):
    mod = _load_view_module()
    data = mod.cmd_paper(store_conn, "test-paper-one")
    assert data["id"] == "test-paper-one"
    assert len(data["applicability"]) == 2
    assert len(data["yields"]) == 1
    yielded = data["yields"][0]
    assert yielded["id"] == "test-assertion-one"
    assert yielded["certainty"] == "high"


def test_paper_mode_errors_on_unknown_paper(store_conn):
    mod = _load_view_module()
    data = mod.cmd_paper(store_conn, "no-such-paper")
    assert "error" in data


def test_assertion_mode_resolves_relations_to_values_not_bare_ids(store_conn):
    mod = _load_view_module()
    data = mod.cmd_assertion(store_conn, "test-assertion-one")
    assert data["id"] == "test-assertion-one"
    assert data["yielded_by_paper"] == "test-paper-one"
    assert len(data["contradicts"]) == 1
    contradicted = data["contradicts"][0]
    assert contradicted["id"] == "test-assertion-two"
    assert contradicted["value"] == "A second assertion that contradicts the first"


def test_assertion_mode_errors_on_unknown_assertion(store_conn):
    mod = _load_view_module()
    data = mod.cmd_assertion(store_conn, "no-such-assertion")
    assert "error" in data


def test_json_output_survives_non_ascii_characters(store_db_path):
    """Regression: Windows consoles default to cp1252, which cannot encode
    accented or Greek characters. An earlier version of this script crashed
    with UnicodeEncodeError on --json output containing such text; fixed by
    reconfiguring stdout to UTF-8 at startup (scripts/view.py, `sys.stdout.
    reconfigure(encoding="utf-8")`).

    CORRECTED (code review finding, 2026-09-18): the original version of
    this test called json.dumps() directly in the test process and never
    touched sys.stdout at all, so it could not have failed even if the
    reconfigure() fix were removed entirely -- confirmed by the reviewer
    commenting out those lines and watching this test still pass. This
    version runs the REAL script as a subprocess with PYTHONIOENCODING
    forced to cp1252 (the actual failure environment), which fails with
    UnicodeEncodeError without the fix and passes with it -- verified by
    injection below."""
    proc = _run_view_cli(store_db_path, ["assertion", "test-assertion-one", "--json"], console_encoding="cp1252")
    assert proc.returncode == 0, f"stderr: {proc.stderr}"
    data = json.loads(proc.stdout)
    assert "café" in data["value"]
    assert "αβγ" in data["value"]


def test_main_reports_missing_db_file():
    missing = Path(tempfile.gettempdir()) / "definitely-does-not-exist-evidence.db"
    proc = _run_view_cli(missing, ["contexts"])
    assert proc.returncode == 1
    assert "does not exist" in proc.stderr


def test_main_requires_id_for_paper_and_assertion_modes(store_db_path):
    for mode in ("paper", "assertion"):
        proc = _run_view_cli(store_db_path, [mode])
        assert proc.returncode == 1
        assert "requires an id" in proc.stderr


def test_main_exit_code_reflects_error_for_unknown_paper(store_db_path):
    proc = _run_view_cli(store_db_path, ["paper", "no-such-paper", "--json"])
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert "error" in data


def test_main_succeeds_for_real_contexts_listing(store_db_path):
    proc = _run_view_cli(store_db_path, ["contexts"])
    assert proc.returncode == 0, f"stderr: {proc.stderr}"
    assert "qml" in proc.stdout


def test_primary_context_paper_is_not_listed_again_via_applicability_regression(store_conn):
    """`view.py contexts <id>` prints the applicability section as "(not
    primary context)". test-paper-one's primary context is qml and it also
    claims qml applicability; it must appear once, in the direct list.
    Proven to fail by injection: without the NOT IN clause it appeared in
    both (team lead's Manual Validation run, 2026-09-25, 26 such papers)."""
    mod = _load_view_module()
    data = mod.cmd_contexts_detail(store_conn, "qml")
    direct = {r["id"] for r in data["records"]}
    via = {r["id"] for r in data["papers_via_applicability"]}
    assert "test-paper-one" in direct
    assert not (direct & via), f"listed twice: {sorted(direct & via)}"
    assert "test-paper-one" in {r["id"] for r in mod.cmd_contexts_detail(store_conn, "qc")["papers_via_applicability"]}


def test_a_paper_view_computes_corroboration_once(synthetic_store, monkeypatch):
    """PR #88 Copilot review: `cmd_paper` called `cmd_assertion` per yielded
    assertion and each recomputed the whole-store corroboration map. The
    synthetic paper alpha-2024-first-paper yields two assertions. Proven to
    fail by injection, 2026-10-18: with `cmd_paper` passing no map, the
    count was 3 (its own, then one per assertion) and this test went red;
    restored, green."""
    from store import connect
    mod = _load_view_module()
    calls = []
    real = mod.resolvers.corroboration
    monkeypatch.setattr(mod.resolvers, "corroboration", lambda conn: calls.append(1) or real(conn))
    conn = connect(synthetic_store)
    try:
        data = mod.cmd_paper(conn, "alpha-2024-first-paper")
    finally:
        conn.close()
    assert len(data["yields"]) == 2
    assert len(calls) == 1
