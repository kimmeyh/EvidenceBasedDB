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

# Hand-transcribed entries (no arXiv id / DOI), the shape Sprint 4 Task B's
# door requires of anything it cannot resolve from an API: a visible
# hand-transcribed marker, the page it was read from, a title, and a REAL
# local path for access (the fixture points these at files it creates).
SAMPLE_ENTRIES = [
    {
        "id": "griffin-2026-cvqboosting-fraud",
        "title": "Improving credit card transaction fraud detection using CVQBoosting",
        "citation": "Griffin, P., \"Improving credit card transaction fraud detection using CVQBoosting\", QCi Dirac-3 working paper, 2026-03 (hand-transcribed from cover)",
        "citation_origin": "hand",
        "transcribed_from": "cover",
        "access": "<tmp>/griffin.pdf",
        "context": "platform:dirac-3",
        "disposition": "Directly relevant: CVQBoost fraud-detection application on Dirac-3, the same platform this project measures",
        "promote": True,
    },
    {
        "id": "recruit-2026-case-story",
        "title": "Recruit Case Story",
        "citation": "Vendor case study, \"Recruit Case Story\", v5, publisher and date not stated in the document (hand-transcribed from cover)",
        "citation_origin": "hand",
        "transcribed_from": "cover",
        "access": "<tmp>/recruit.pdf",
        "context": "qc",
        "disposition": "Vendor marketing material, not a paper. Recorded with this disposition rather than forced into a paper citation shape",
        "promote": False,
    },
]


def _materialise(entries: list[dict], tmp: Path) -> list[dict]:
    """Point each entry's access at a real file under tmp (the validator
    requires an existing local path for hand-transcribed papers)."""
    out = []
    for e in entries:
        e = dict(e)
        if e.get("access", "").startswith("<tmp>/"):
            path = tmp / e["access"][len("<tmp>/"):]
            path.write_bytes(b"%PDF-1.4 fixture")
            e["access"] = str(path)
        out.append(e)
    return out


@pytest.fixture
def store_and_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        metadata_path = Path(tmp) / "seed_set_metadata.json"
        export_dir = Path(tmp) / "export"
        create_store(db_path).close()
        metadata_path.write_text(json.dumps(_materialise(SAMPLE_ENTRIES, Path(tmp))), encoding="utf-8")
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


def test_promote_run_after_a_seen_only_run_still_promotes(store_and_metadata):
    """Regression test for Claude PR #1 review finding 2: the original
    existing-record check skipped promotion whenever a row already
    existed, so running the script once at seen tier and then again with
    --promote (the exact two-pass workflow this script's own docstring
    describes) could never promote anything -- every row was already
    present by the second run."""
    db_path, metadata_path, export_dir = store_and_metadata

    first = _run_script(db_path, metadata_path, export_dir)
    assert first.returncode == 0, first.stderr

    second = _run_script(db_path, metadata_path, export_dir, ["--promote"])
    assert second.returncode == 0, second.stderr
    assert "1 of those promoted" in second.stdout, second.stdout

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


def test_promote_run_does_not_duplicate_records(store_and_metadata):
    db_path, metadata_path, export_dir = store_and_metadata
    _run_script(db_path, metadata_path, export_dir)
    _run_script(db_path, metadata_path, export_dir, ["--promote"])

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


def test_a_bad_entry_names_itself_and_the_run_writes_nothing(store_and_metadata):
    """F6 finding 3 (PR #1 review) as CORRECTED by the PR #20 review
    (2026-09-19). The Sprint 3 Task B version used a SAVEPOINT per entry and
    this test asserted the entry BEFORE the bad one "survived" -- which it
    did, because under Python's legacy sqlite3 transaction mode each
    entry's RELEASE was a real commit. So a mid-loop failure left earlier
    entries durable and export/ never regenerated: store and export
    silently diverged. The reviewer proved it with a second connection.

    Contract now: a bad entry (an undefined context, rejected by the FK on
    record_contexts.context_id) SECOND in a three-entry list must (1) be
    named with its position in the error, (2) roll back the ENTIRE run --
    the entry before it is absent too -- and (3) leave export/ unwritten.
    This assertion was flipped deliberately, for the reason above; it was
    not loosened."""
    db_path, metadata_path, export_dir = store_and_metadata
    entries = [
        SAMPLE_ENTRIES[0],
        {
            "id": "bad-entry-undefined-context",
            "title": "A Paper With a Bad Context",
            "citation": "Nobody, N., \"A Paper With a Bad Context\", 2026 (hand-transcribed from cover)",
            "citation_origin": "hand",
            "transcribed_from": "cover",
            "access": "<tmp>/bad.pdf",
            "context": "platform:not-a-real-platform",
            "disposition": "deliberately invalid for this test",
            "promote": False,
        },
        SAMPLE_ENTRIES[1],
    ]
    metadata_path.write_text(json.dumps(_materialise(entries, metadata_path.parent)), encoding="utf-8")

    proc = _run_script(db_path, metadata_path, export_dir)
    assert proc.returncode != 0
    assert "bad-entry-undefined-context" in proc.stderr
    assert "position 1" in proc.stderr
    assert "Nothing was written" in proc.stderr

    import store as store_module
    conn = store_module.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'paper'").fetchone()[0]
    conn.close()
    assert count == 0, "a failing run must roll back every entry, including the ones before the bad one"
    assert not export_dir.exists(), "export/ must not be regenerated on a failing run"


def test_an_entry_without_an_id_is_named_by_position(store_and_metadata):
    """PR #20 review (2026-09-19): entry["id"] was read outside the guarded
    block, so a malformed entry died with a bare KeyError naming nothing."""
    db_path, metadata_path, export_dir = store_and_metadata
    entries = [SAMPLE_ENTRIES[0], {"citation": "no id here", "access": "x", "context": "qc", "disposition": "d"}]
    metadata_path.write_text(json.dumps(_materialise(entries, metadata_path.parent)), encoding="utf-8")
    proc = _run_script(db_path, metadata_path, export_dir)
    assert proc.returncode != 0
    assert "position 1" in proc.stderr and "no 'id'" in proc.stderr
