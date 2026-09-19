"""Tests for scripts/apply_paper_applicability.py (Sprint 3 Task D, F14).

F14 hardens this one-off data-correction script against two silent-
failure findings from PR #11's review: a typo'd paper_id in APPLICABILITY
previously produced a stderr warning and exit 0 regardless, and a paper
already holding ANY applicability row was skipped unconditionally without
checking whether the existing rows matched the intended set.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import create_store  # noqa: E402
from store.ingest import PaperRecord, insert_paper  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply_paper_applicability.py"


@pytest.fixture
def store_and_export():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        export_dir = Path(tmp) / "export"
        conn = create_store(db_path)
        insert_paper(
            conn,
            PaperRecord(
                id="paper-one",
                value="A Test Paper",
                tier="seen",
                citation="Tester, T., 2026",
                citation_origin="api",
                access="arXiv:0000.00011",
                disposition="fixture",
                context="qml",
            ),
        )
        insert_paper(
            conn,
            PaperRecord(
                id="paper-two",
                value="Another Test Paper",
                tier="seen",
                citation="Tester, T. 2, 2026",
                citation_origin="api",
                access="arXiv:0000.00012",
                disposition="fixture",
                context="qc",
            ),
        )
        conn.commit()
        conn.close()
        yield db_path, export_dir


def _run_script(db_path: Path, export_dir: Path, applicability: dict) -> subprocess.CompletedProcess:
    # Same wrapper pattern as tests/test_ingest_seed_set.py: monkeypatch
    # DB_PATH/EXPORT_DIR/APPLICABILITY on the loaded module rather than
    # editing the real script, so the script under test is exactly what
    # production runs.
    wrapper = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "import importlib.util\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('apply_paper_applicability', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r})\n"
        f"mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        f"mod.APPLICABILITY = {applicability!r}\n"
        "raise SystemExit(mod.main())\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True)


def test_applies_applicability_to_a_real_paper(store_and_export):
    db_path, export_dir = store_and_export
    applicability = {"paper-one": [("qml", "primary topic"), ("qc", "backend")]}
    proc = _run_script(db_path, export_dir, applicability)
    assert proc.returncode == 0, proc.stderr

    import store as store_module
    conn = store_module.connect(db_path)
    rows = {
        r["context_id"]
        for r in conn.execute("SELECT context_id FROM paper_applicability WHERE record_id = 'paper-one'")
    }
    conn.close()
    assert rows == {"qml", "qc"}


def test_a_typod_paper_id_fails_the_run_not_just_warns(store_and_export):
    """F14 finding 1: a paper_id with no matching record must fail the
    run (non-zero exit), not just print a warning and exit 0."""
    db_path, export_dir = store_and_export
    applicability = {"paper-one-TYPO-DOES-NOT-EXIST": [("qml", "primary topic")]}
    proc = _run_script(db_path, export_dir, applicability)
    assert proc.returncode != 0
    assert "not found" in proc.stderr


def _applicability_rows(db_path: Path, paper_id: str) -> set:
    import store as store_module
    conn = store_module.connect(db_path)
    rows = {
        (r["context_id"], r["rationale"])
        for r in conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (paper_id,))
    }
    conn.close()
    return rows


def test_a_failing_run_writes_nothing_not_even_the_valid_papers(store_and_export):
    """PR #20 review (2026-09-19): the F14 version committed the papers it
    COULD apply and regenerated export/ before returning exit 1, so a
    non-zero exit did not mean "nothing written". Now validation runs to
    completion first; any problem exits 1 with store and export untouched."""
    db_path, export_dir = store_and_export
    applicability = {
        "paper-one": [("qml", "primary topic")],
        "does-not-exist": [("qc", "typo'd key")],
    }
    proc = _run_script(db_path, export_dir, applicability)
    assert proc.returncode != 0
    assert "NOTHING was written" in proc.stderr
    assert _applicability_rows(db_path, "paper-one") == set(), "the valid paper must not be applied on a failing run"
    assert not export_dir.exists(), "export/ must not be regenerated on a failing run"


def test_a_changed_rationale_is_a_mismatch_not_a_clean_noop(store_and_export):
    """PR #20 review (2026-09-19): comparing context ids alone accepted a
    changed rationale as "already matching". ADR-0005 section 2d makes the
    rationale part of the record, so it is compared too."""
    db_path, export_dir = store_and_export
    first = _run_script(db_path, export_dir, {"paper-one": [("qml", "ORIGINAL rationale")]})
    assert first.returncode == 0
    second = _run_script(db_path, export_dir, {"paper-one": [("qml", "CHANGED rationale")]})
    assert second.returncode != 0
    assert "mismatch" in second.stderr
    assert _applicability_rows(db_path, "paper-one") == {("qml", "ORIGINAL rationale")}


def test_a_constraint_failure_names_the_paper_and_context_and_writes_nothing(store_and_export):
    """PR #20 review (2026-09-19): the F6 finding 3 class, previously not
    ported here -- an FK violation inside the insert loop was a bare
    sqlite3 traceback naming no paper."""
    db_path, export_dir = store_and_export
    applicability = {
        "paper-one": [("qml", "fine")],
        "paper-two": [("platform:not-a-real-platform", "undefined context")],
    }
    proc = _run_script(db_path, export_dir, applicability)
    assert proc.returncode != 0
    assert "paper-two" in proc.stderr and "platform:not-a-real-platform" in proc.stderr
    assert _applicability_rows(db_path, "paper-one") == set(), "the whole run rolls back on a constraint failure"
    assert not export_dir.exists()


def test_a_matching_already_set_paper_is_a_clean_noop(store_and_export):
    db_path, export_dir = store_and_export
    applicability = {"paper-one": [("qml", "primary topic")]}
    first = _run_script(db_path, export_dir, applicability)
    assert first.returncode == 0

    second = _run_script(db_path, export_dir, applicability)
    assert second.returncode == 0
    assert "already had matching applicability" in second.stdout


def test_a_mismatched_already_set_paper_fails_the_run(store_and_export):
    """F14 finding 2: a paper whose EXISTING applicability set does not
    match the intended set (e.g. left half-populated by an interrupted
    prior run) must fail the run and name the mismatch, not be silently
    skipped as if it were already correctly done."""
    db_path, export_dir = store_and_export
    first_pass = {"paper-one": [("qml", "primary topic")]}
    first = _run_script(db_path, export_dir, first_pass)
    assert first.returncode == 0

    changed_intent = {"paper-one": [("qml", "primary topic"), ("qc", "a second context now intended")]}
    second = _run_script(db_path, export_dir, changed_intent)
    assert second.returncode != 0
    assert "mismatch" in second.stderr

    import store as store_module
    conn = store_module.connect(db_path)
    rows = {
        r["context_id"]
        for r in conn.execute("SELECT context_id FROM paper_applicability WHERE record_id = 'paper-one'")
    }
    conn.close()
    assert rows == {"qml"}, "a mismatch must not be auto-overwritten -- the original row must survive untouched"
