"""Tests for scripts/refresh_citations.py (Sprint 4 Task B, F25 C1).

Runs the real script as a subprocess against a temp store with an
injected fetcher (the wrapper defines it), same pattern as the other
script tests. No network.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import connect, create_store  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refresh_citations.py"
ATOM = (ROOT / "tests" / "test_citations.py").read_text(encoding="utf-8").split('ARXIV_ATOM = b"""')[1].split('"""')[0]

STALE = 'Dupont, M., et al., "Quantum Enhanced Greedy Solver for Optimization Problems," arXiv:2303.05509v1, 2023-03-09'
FRESH = ('Dupont, M., Evert, B., "Quantum-Enhanced Greedy Combinatorial Optimization Solver," '
         'arXiv:2303.05509v2, Science Advances 9, eadi0487 (2023), DOI:10.1126/sciadv.adi0487, 2023-11-17')


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        export_dir = Path(tmp) / "export"
        conn = create_store(db_path)
        conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) VALUES "
                     "('dupont', 'paper', ?, ?, 'N/A', '2026-09-16', 'seeded')", (STALE, STALE))
        conn.execute("INSERT INTO paper_fields (record_id, tier, access, disposition) VALUES ('dupont', 'screened', 'arXiv:2303.05509', 'd')")
        conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) VALUES "
                     "('vendor', 'paper', 'Vendor doc', 'Vendor, \"Doc\" (hand-transcribed from cover)', 'N/A', '2026-09-16', 'seeded')")
        conn.execute("INSERT INTO paper_fields (record_id, tier, access, disposition) VALUES ('vendor', 'seen', ?, 'd')", (str(Path(tmp) / "v.pdf"),))
        conn.commit(); conn.close()
        yield db_path, export_dir


def _run(db_path: Path, export_dir: Path, args: list[str]) -> subprocess.CompletedProcess:
    wrapper = (
        "import sys, importlib.util\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('refresh', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r}); mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        f"ATOM = {ATOM!r}.encode()\n"
        "mod.FETCHER = lambda url, accept: ATOM\n"
        f"raise SystemExit(mod.main({args!r}))\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True, encoding="utf-8")


def test_dry_run_reports_differs_and_no_id_and_writes_nothing(store):
    db_path, export_dir = store
    proc = _run(db_path, export_dir, [])
    assert proc.returncode == 0, proc.stderr
    assert "DIFFERS dupont" in proc.stdout and "NO-ID   vendor" in proc.stdout
    assert "PLANNED (dry run" in proc.stdout
    conn = connect(db_path)
    assert conn.execute("SELECT provenance FROM records WHERE id='dupont'").fetchone()["provenance"] == STALE
    conn.close()
    assert not export_dir.exists()


def test_apply_rewrites_citation_and_title_with_a_dated_reason_and_regenerates(store):
    db_path, export_dir = store
    proc = _run(db_path, export_dir, ["--apply"])
    assert proc.returncode == 0, proc.stderr
    conn = connect(db_path)
    row = conn.execute("SELECT value, provenance, updated_reason FROM records WHERE id='dupont'").fetchone()
    vendor = conn.execute("SELECT provenance FROM records WHERE id='vendor'").fetchone()["provenance"]
    conn.close()
    assert row["provenance"] == FRESH
    assert row["value"] == "Quantum-Enhanced Greedy Combinatorial Optimization Solver"
    assert "re-derived from arxiv:2303.05509 via arXiv" in row["updated_reason"] and "previous citation" in row["updated_reason"]
    assert vendor.startswith("Vendor,"), "a NO-ID paper is never touched"
    assert (export_dir / "papers.json").exists()
    papers = json.loads((export_dir / "papers.json").read_text(encoding="utf-8"))
    assert next(p for p in papers if p["id"] == "dupont")["citation"] == FRESH


def test_apply_keeps_a_same_day_reason_written_by_an_earlier_pass(store):
    """Task C runs two correction passes on one day; the second must not
    erase the first's explanation."""
    db_path, export_dir = store
    from datetime import date
    today = date.today().isoformat()
    conn = connect(db_path)
    conn.execute("UPDATE records SET updated_reason = ? WHERE id = 'dupont'", (f"{today}: access field corrected (earlier pass)",))
    conn.commit(); conn.close()
    proc = _run(db_path, export_dir, ["--apply"])
    assert proc.returncode == 0, proc.stderr
    conn = connect(db_path)
    reason = conn.execute("SELECT updated_reason FROM records WHERE id='dupont'").fetchone()[0]
    conn.close()
    assert reason.startswith(f"{today}: access field corrected (earlier pass) | {today}: citation and title re-derived")


def test_json_report_is_written(store, tmp_path):
    db_path, export_dir = store
    out = tmp_path / "report.json"
    proc = _run(db_path, export_dir, ["--json", str(out)])
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert {e["id"]: e["status"] for e in report} == {"dupont": "DIFFERS", "vendor": "NO-ID"}
