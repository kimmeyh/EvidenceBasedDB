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


def test_apply_writes_an_api_origin_record_with_a_derived_id(store):
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
    assert not export_dir.exists(), "no export is written since ADR-0004 A7"
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
    assert not export_dir.exists(), "no export is written since ADR-0004 A7"
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


def test_verify_checks_the_read_tier_obligations(store):
    """The read tier is what ADR-0005 treats as load-bearing: the source was
    opened (`checked_against_source`) AND claims were extracted (`yields`).
    `--verify` is the mechanized F10 protocol, so this is the branch that
    matters most, and it was untested until the PR #30 review."""
    db_path, export_dir, _ = store
    assert _run(db_path, export_dir, ARXIV_ARGS + ["--apply"]).returncode == 0
    conn = connect(db_path)
    # Promote WITHOUT the obligations: checked_against_source set, no yields.
    conn.execute("UPDATE paper_fields SET tier = 'read', checked_against_source = '2026-09-22, read pp.1-8' "
                 "WHERE record_id = ?", (DUPONT_ID,))
    conn.commit(); conn.close()
    proc = _run(db_path, export_dir, ["--verify", DUPONT_ID])
    assert proc.returncode == 1
    assert "FAIL  read tier" in proc.stdout and "yields=0" in proc.stdout

    # Now give it a yielded assertion: the same record passes.
    conn = connect(db_path)
    conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
                 "VALUES ('a1', 'assertion', 'a claim', 'src', 'N/A', '2026-09-22', 'test')")
    conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES ('a1', 'qc')")
    conn.execute("INSERT INTO paper_yields (paper_id, assertion_id) VALUES (?, 'a1')", (DUPONT_ID,))
    conn.commit(); conn.close()
    ok = _run(db_path, export_dir, ["--verify", DUPONT_ID])
    assert ok.returncode == 0, ok.stdout
    assert "PASS  read tier" in ok.stdout


def test_verify_checks_the_hand_origin_marker_and_that_the_file_still_exists(store, tmp_path):
    """A hand-origin record's whole claim to provenance is the visible
    marker plus a real local file. Both branches were untested."""
    db_path, export_dir, tmp = store
    pdf = tmp / "post.pdf"
    pdf.write_bytes(b"%PDF")
    args = [f"{pdf} | https://example.org/post", "--kind", "reference", "--context", "qml",
            "--id", "author-2026-a-post", "--title", "A Post",
            "--hand-citation", 'Author, A., "A Post," Example, 2026-09-01 (hand-transcribed from p.1)',
            "--transcribed-from", "p.1", "--disposition", "Reference: a post", "--apply"]
    assert _run(db_path, export_dir, args).returncode == 0
    ok = _run(db_path, export_dir, ["--verify", "author-2026-a-post"])
    assert ok.returncode == 0, ok.stdout
    assert "PASS  hand-transcribed marker present" in ok.stdout
    assert "PASS  access is an existing local path" in ok.stdout

    # The file moves away: the record can no longer show its source.
    pdf.unlink()
    gone = _run(db_path, export_dir, ["--verify", "author-2026-a-post"])
    assert gone.returncode == 1
    assert "FAIL  access is an existing local path" in gone.stdout

    # The marker is edited out: the citation no longer admits it was typed.
    pdf.write_bytes(b"%PDF")
    conn = connect(db_path)
    conn.execute("UPDATE records SET provenance = 'Author, A., \"A Post,\" Example, 2026-09-01' "
                 "WHERE id = 'author-2026-a-post'")
    conn.commit(); conn.close()
    unmarked = _run(db_path, export_dir, ["--verify", "author-2026-a-post"])
    assert unmarked.returncode == 1
    assert "FAIL  hand-transcribed marker present" in unmarked.stdout


def test_verify_reports_a_source_it_cannot_reach_rather_than_passing(store):
    """An api-origin record whose provider is unreachable must FAIL the
    citation check, not skip it: 'could not check' is not 'checked'."""
    db_path, export_dir, _ = store
    assert _run(db_path, export_dir, ARXIV_ARGS + ["--apply"]).returncode == 0
    wrapper = (
        "import sys, importlib.util\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('intake', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r}); mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        "mod.FETCHER = lambda url, accept: (_ for _ in ()).throw(RuntimeError('network down'))\n"
        f"raise SystemExit(mod.main(['--verify', {DUPONT_ID!r}]))\n"
    )
    proc = subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 1
    assert "FAIL  citation matches the source of record" in proc.stdout
    assert "could not resolve" in proc.stdout


def _atom_for(ident: str) -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
<entry><id>http://arxiv.org/abs/{ident}v1</id><title>A title for {ident}</title>
<published>2024-01-02T00:00:00Z</published><updated>2024-01-02T00:00:00Z</updated>
<author><name>Ada Lovelace</name></author></entry></feed>""".encode()


def test_one_run_shares_one_pacer_so_arxiv_requests_are_spaced_regression(monkeypatch):
    """Sprint 6 Task J (2026-10-04): build_record made a NEW PacedFetcher per
    entry, a new pacer never waits, and 684 entries went to arXiv in 10
    minutes against the team lead's 6 s spacing. Since retrospective I1
    (2026-10-05) the clock is process-wide, so new pacers are safe. Proven to
    fail by injection: with each new PacedFetcher resetting the clock (the
    old per-instance behavior), no wait was recorded between the entries."""
    import importlib.util
    from store import citations
    spec = importlib.util.spec_from_file_location("intake_pacing", ROOT / "scripts" / "intake.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    waits, clock = [], [100.0]
    monkeypatch.setattr(citations, "_sleep", lambda s: waits.append(round(s, 3)))
    monkeypatch.setattr(citations, "_monotonic", lambda: clock[0])
    monkeypatch.setattr(citations, "default_fetcher",
                        lambda url, accept: _atom_for(url.split("id_list=")[1]))
    for ident in ("2401.00001", "2401.00002"):
        mod.build_record({"access": f"arXiv:{ident}", "context": "qml", "disposition": "test"}, today="2026-10-04")
    assert waits == [citations.ARXIV_MIN_INTERVAL_S], f"arXiv requests in one run must be paced; waits were {waits}"


def _intake_module(name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "intake.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_manifest_no_intake_section_names_is_refused_regression(tmp_path):
    """Sprint 6 retrospective I2: the section comes BEFORE the manifest runs.
    Proven to fail by injection: with the name check replaced by True, the
    unnamed manifest was accepted."""
    mod = _intake_module("intake_i2")
    doc = tmp_path / "INTAKE_WORKFLOW.md"
    doc.write_text("## 18. Applied: manifests/named_one.json", encoding="utf-8")
    assert "not named" in mod.unrecorded_manifest(ROOT / "manifests" / "never_written_section.json", doc)
    assert mod.unrecorded_manifest(ROOT / "manifests" / "named_one.json", doc) is None
    assert mod.unrecorded_manifest(tmp_path / "scratch_retry.json", doc) is None  # outside manifests/


def test_every_committed_manifest_is_named_in_the_workflow():
    mod = _intake_module("intake_i2b")
    for m in sorted((ROOT / "manifests").glob("*.json")):
        if m.name == "qmlpapers_routes_for_present.json":
            continue  # not an intake manifest (INTAKE_WORKFLOW section 17)
        assert mod.unrecorded_manifest(m) is None, m.name
