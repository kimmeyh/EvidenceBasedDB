"""scripts/intake.py -- the one door (Sprint 4 Task G). Real script, real
subprocess, temp store, injected fetcher; no network.

Injection record 2026-09-19: with the anchor rule commented out of
validate_paper, test_dry_run_refuses_an_unanchored_rationale went red;
with the kind-prefix check removed from build_record,
test_repository_kind_requires_its_disposition_prefix went red.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from store import connect, create_store  # noqa: E402

SCRIPT = ROOT / "scripts" / "intake.py"
DUPONT_ID = "dupont-2023-quantum-enhanced-greedy-combinatorial-optimization"
MERLIN_ID = "merlinquantum-merlin-github-repo"


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        create_store(db_path).close()
        yield db_path, Path(tmp) / "export", Path(tmp)


def _run(db_path: Path, export_dir: Path, args: list[str]) -> subprocess.CompletedProcess:
    wrapper = (
        "import sys, importlib.util\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from tests.test_citations import fake_fetcher, GITHUB_JSON\n"
        "def fetcher(url, accept):\n"
        "    if 'api.github.com' in url: return GITHUB_JSON\n"
        "    return fake_fetcher(url, accept)\n"
        f"spec = importlib.util.spec_from_file_location('intake', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r}); mod.EXPORT_DIR = Path({str(export_dir)!r}); mod.FETCHER = fetcher\n"
        f"raise SystemExit(mod.main({args!r}))\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True, encoding="utf-8")


ARXIV_ARGS = ["arXiv:2303.05509", "--context", "qc", "--tier", "screened",
              "--disposition", "Hybrid quantum-classical greedy optimization on Rigetti hardware",
              "--applicability", "qc=Run on gate-based hardware -- arXiv abstract"]


def test_dry_run_derives_the_record_and_writes_nothing(store):
    db_path, export_dir, _ = store
    proc = _run(db_path, export_dir, ARXIV_ARGS)
    assert proc.returncode == 0, proc.stderr
    assert f"PLANNED {DUPONT_ID}" in proc.stdout and "Dupont, M., Evert, B." in proc.stdout
    conn = connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 0
    conn.close()
    assert not export_dir.exists()


def test_apply_writes_an_api_origin_record_with_a_derived_id_and_regenerates(store):
    db_path, export_dir, _ = store
    proc = _run(db_path, export_dir, ARXIV_ARGS + ["--apply"])
    assert proc.returncode == 0, proc.stderr
    conn = connect(db_path)
    row = conn.execute("SELECT r.value, r.provenance, p.tier FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?", (DUPONT_ID,)).fetchone()
    app = conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (DUPONT_ID,)).fetchall()
    conn.close()
    assert row["value"] == "Quantum-Enhanced Greedy Combinatorial Optimization Solver"
    assert row["provenance"].startswith('Dupont, M., Evert, B., "Quantum-Enhanced') and row["tier"] == "screened"
    assert [(a["context_id"], a["rationale"]) for a in app] == [("qc", "Run on gate-based hardware -- arXiv abstract")]
    assert (export_dir / "papers.json").exists()
    again = _run(db_path, export_dir, ARXIV_ARGS + ["--apply"])
    assert again.returncode == 0 and f"PRESENT {DUPONT_ID}" in again.stdout


def test_dry_run_refuses_an_unanchored_rationale(store):
    db_path, export_dir, _ = store
    args = ARXIV_ARGS[:-1] + ["qc=Run on gate-based hardware"]
    proc = _run(db_path, export_dir, args)
    assert proc.returncode == 1 and "no source anchor" in proc.stdout


def test_repository_kind_requires_its_disposition_prefix(store):
    db_path, export_dir, _ = store
    base = ["https://github.com/merlinquantum/merlin", "--context", "qml",
            "--applicability", "qml=photonic quantum machine learning models -- GitHub repository description"]
    bad = _run(db_path, export_dir, base + ["--disposition", "MerLin framework code"])
    assert bad.returncode == 1 and "must start with 'Code repository:'" in bad.stdout
    good = _run(db_path, export_dir, base + ["--disposition", "Code repository: MerLin framework code", "--apply"])
    assert good.returncode == 0, good.stderr
    conn = connect(db_path)
    row = conn.execute("SELECT provenance FROM records WHERE id = ?", (MERLIN_ID,)).fetchone()
    conn.close()
    assert row is not None and "GitHub repository merlinquantum/merlin, MIT license" in row["provenance"]


def test_hand_origin_needs_an_id_and_the_door_shape(store):
    db_path, export_dir, tmp = store
    pdf = tmp / "post.pdf"
    pdf.write_bytes(b"%PDF")
    base = [f"{pdf} | https://example.org/post", "--kind", "reference", "--context", "qml", "--title", "A Post",
            "--hand-citation", 'Author, A., "A Post," Example, 2026-09-01 (hand-transcribed from p.1)', "--transcribed-from", "p.1",
            "--disposition", "Reference: a blog post worth keeping"]
    no_id = _run(db_path, export_dir, base)
    assert no_id.returncode == 1 and "needs --id" in no_id.stdout
    ok = _run(db_path, export_dir, base + ["--id", "author-2026-a-post", "--apply"])
    assert ok.returncode == 0, ok.stderr
    conn = connect(db_path)
    assert conn.execute("SELECT value FROM records WHERE id = 'author-2026-a-post'").fetchone()["value"] == "A Post"
    conn.close()


def test_manifest_commits_per_entry_and_resumes(store, tmp_path):
    db_path, export_dir, _ = store
    manifest = tmp_path / "m.json"
    entries = [
        {"access": "arXiv:2303.05509", "context": "qc", "tier": "screened", "disposition": "d",
         "applicability": [["qc", "why -- arXiv abstract"]]},
        {"access": "arXiv:2303.05509", "id": "second-copy", "context": "qc", "disposition": "d",
         "applicability": [["qc", "no anchor here"]]},
        {"access": "https://github.com/merlinquantum/merlin", "context": "qml", "disposition": "Code repository: MerLin"},
    ]
    manifest.write_text(json.dumps(entries), encoding="utf-8")
    proc = _run(db_path, export_dir, ["--manifest", str(manifest), "--apply"])
    assert proc.returncode == 1, "one refused entry makes the run report failure"
    assert "REFUSED second-copy" in proc.stdout and "2 written, 0 already present, 1 refused" in proc.stdout
    conn = connect(db_path)
    ids = {r[0] for r in conn.execute("SELECT id FROM records")}
    conn.close()
    assert ids == {DUPONT_ID, MERLIN_ID}, "the entries before and after the bad one landed (per-entry commit)"
    assert (export_dir / "papers.json").exists()
    rerun = _run(db_path, export_dir, ["--manifest", str(manifest), "--apply"])
    assert "0 written, 2 already present, 1 refused" in rerun.stdout


def test_verify_runs_the_first_try_checks_and_catches_a_drifted_citation(store):
    db_path, export_dir, _ = store
    assert _run(db_path, export_dir, ARXIV_ARGS + ["--apply"]).returncode == 0
    ok = _run(db_path, export_dir, ["--verify", DUPONT_ID])
    assert ok.returncode == 0, ok.stdout
    assert "FAIL" not in ok.stdout and "citation matches the source of record  (SAME)" in ok.stdout
    conn = connect(db_path)
    conn.execute("UPDATE records SET provenance = 'hand-edited' WHERE id = ?", (DUPONT_ID,))
    conn.commit(); conn.close()
    drifted = _run(db_path, export_dir, ["--verify", DUPONT_ID])
    assert drifted.returncode == 1 and "FAIL  citation matches the source of record  (DIFFERS" in drifted.stdout
    missing = _run(db_path, export_dir, ["--verify", "nobody"])
    assert missing.returncode == 1 and "FAIL  record exists" in missing.stdout
