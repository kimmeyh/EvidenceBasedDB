"""Tests for scripts/ingest_seed_set.py (Sprint 1 Task F).

Exercises the loader's logic directly against a synthetic metadata file
and a temp store, rather than the real 46-paper seed set -- this test
suite must pass whether or not scripts/seed_set_metadata.json (the real,
extracted data) has been generated yet.
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

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ingest_seed_set.py"

SAMPLE_ENTRIES = [
    {
        "id": "griffin-2026-cvqboosting-fraud",
        "citation": "Griffin, P., \"Improving credit card transaction fraud detection using CVQBoosting\", QCi Dirac-3 working paper, 2026-03",
        "access": "local file, no DOI/arXiv id",
        "context": "platform:dirac-3",
        "disposition": "Directly relevant: CVQBoost fraud-detection application on Dirac-3, the same platform this project measures",
        "promote": True,
    },
    {
        "id": "recruit-2026-case-story",
        "citation": "Vendor case study, \"Recruit Case Story\", v5, publisher and date not stated in the document",
        "access": "local file, no DOI/arXiv id",
        "context": "qc",
        "disposition": "Vendor marketing material, not a paper. Recorded as seen with this disposition rather than forced into a paper citation shape",
        "promote": False,
    },
]


@pytest.fixture
def store_and_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        metadata_path = Path(tmp) / "seed_set_metadata.json"
        export_dir = Path(tmp) / "export"
        create_store(db_path).close()
        metadata_path.write_text(json.dumps(SAMPLE_ENTRIES), encoding="utf-8")
        yield db_path, metadata_path, export_dir


def _run_script(db_path: Path, metadata_path: Path, export_dir: Path, extra_args: list[str] | None = None):
    # Run via a small wrapper that monkeypatches DB_PATH/METADATA_PATH/
    # EXPORT_DIR rather than editing the real script's constants, so the
    # script under test is exactly what production runs. ALL THREE must be
    # overridden -- an earlier version of this test overrode only DB_PATH
    # and METADATA_PATH, and the script's unconditional regenerate(conn,
    # EXPORT_DIR) call wrote a synthetic export over the REAL committed
    # export/ directory, corrupting it. Every path must be a real Path
    # object, not a string -- the script calls .exists() on them.
    wrapper = (
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "import importlib.util\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('ingest_seed_set', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r})\n"
        f"mod.METADATA_PATH = Path({str(metadata_path)!r})\n"
        f"mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        f"sys.argv = ['ingest_seed_set.py'] + {extra_args or []!r}\n"
        "raise SystemExit(mod.main())\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True)


def test_loads_all_entries_at_seen_tier_by_default(store_and_metadata):
    db_path, metadata_path, export_dir = store_and_metadata
    proc = _run_script(db_path, metadata_path, export_dir)
    assert proc.returncode == 0, proc.stderr

    conn_module = sys.modules.get("store") or __import__("store")
    conn = conn_module.connect(db_path)
    tiers = {
        row["record_id"]: row["tier"]
        for row in conn.execute("SELECT record_id, tier FROM paper_fields")
    }
    conn.close()
    assert tiers == {
        "griffin-2026-cvqboosting-fraud": "seen",
        "recruit-2026-case-story": "seen",
    }


def test_promote_flag_promotes_only_flagged_entries(store_and_metadata):
    db_path, metadata_path, export_dir = store_and_metadata
    proc = _run_script(db_path, metadata_path, export_dir, ["--promote"])
    assert proc.returncode == 0, proc.stderr

    import store as store_module
    conn = store_module.connect(db_path)
    tiers = {
        row["record_id"]: row["tier"]
        for row in conn.execute("SELECT record_id, tier FROM paper_fields")
    }
    conn.close()
    assert tiers == {
        "griffin-2026-cvqboosting-fraud": "screened",
        "recruit-2026-case-story": "seen",
    }


def test_running_twice_does_not_duplicate(store_and_metadata):
    db_path, metadata_path, export_dir = store_and_metadata
    _run_script(db_path, metadata_path, export_dir)
    proc = _run_script(db_path, metadata_path, export_dir)
    assert proc.returncode == 0, proc.stderr
    assert "2 already present" in proc.stdout, proc.stdout

    import store as store_module
    conn = store_module.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'paper'").fetchone()[0]
    conn.close()
    assert count == 2


def test_a_non_paper_entry_still_gets_a_record_with_an_honest_disposition(store_and_metadata):
    """ADR-0005 section 2: a rejected/mismatched paper is still a record."""
    db_path, metadata_path, export_dir = store_and_metadata
    _run_script(db_path, metadata_path, export_dir)

    import store as store_module
    conn = store_module.connect(db_path)
    row = conn.execute(
        "SELECT disposition FROM paper_fields WHERE record_id = 'recruit-2026-case-story'"
    ).fetchone()
    conn.close()
    assert "not a paper" in row["disposition"].lower() or "vendor" in row["disposition"].lower()
