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


EMPTY_TITLE_CROSSREF = json.dumps({"message": {
    "DOI": "10.5555/notitle", "title": [], "author": [{"family": "Z", "given": "Q"}],
    "issued": {"date-parts": [[2020]]}}}).encode()


def _run_with(db_path, export_dir, args, fetcher_src):
    """Same as _run, but the caller supplies the fetcher line."""
    wrapper = (
        "import sys, importlib.util\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('refresh', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n"
        f"mod.DB_PATH = Path({str(db_path)!r}); mod.EXPORT_DIR = Path({str(export_dir)!r})\n"
        f"MARKED = {MARKED_TITLE_CROSSREF!r}\n"
        f"DATACITE = {DATACITE_ARXIV_NO_JOURNAL_REF.encode()!r}\n"
        f"{fetcher_src}\n"
        f"raise SystemExit(mod.main({args!r}))\n"
    )
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True, encoding="utf-8")


def test_a_provider_record_with_no_title_is_an_error_not_a_silent_skip(store):
    """PR #30 review: apply() skipped DIFFERS rows whose fetched title was
    empty and main() still printed success, so a paper kept its stale
    citation and nothing named it. An empty provider title is an ERROR --
    the run could not answer the question it was asked."""
    db_path, export_dir = store
    conn = connect(db_path)
    conn.execute("UPDATE paper_fields SET access = 'DOI:10.5555/notitle' WHERE record_id = 'dupont'")
    conn.commit(); conn.close()
    src = f"mod.FETCHER = lambda url, accept: {EMPTY_TITLE_CROSSREF!r}"
    proc = _run_with(db_path, export_dir, ["--apply"], src)
    assert "ERROR   dupont" in proc.stdout
    assert "no title" in proc.stdout
    assert proc.returncode == 1, "a run that could not resolve a paper must not report success"
    conn = connect(db_path)
    kept = conn.execute("SELECT provenance FROM records WHERE id='dupont'").fetchone()["provenance"]
    conn.close()
    assert kept == STALE, "the stale citation must be left alone, not blanked"


def test_ids_limits_the_run_to_the_papers_named(store):
    """The subset filter is the safety rail for a targeted re-run; a defect
    here rewrites every paper instead of the ones asked for."""
    db_path, export_dir = store
    proc = _run(db_path, export_dir, ["--ids", "vendor"])
    assert proc.returncode == 0, proc.stderr
    assert "vendor" in proc.stdout
    assert "dupont" not in proc.stdout, "--ids must exclude every paper not named"
    assert "1 paper(s)" in proc.stdout


def test_an_unresolvable_paper_is_reported_and_the_run_says_so(store):
    """The ERROR path: the provider raises, the paper is named, and the exit
    code reflects that the run did not do what was asked."""
    db_path, export_dir = store
    src = "mod.FETCHER = lambda url, accept: (_ for _ in ()).throw(RuntimeError('HTTP Error 503'))"
    proc = _run_with(db_path, export_dir, ["--apply"], src)
    assert "ERROR   dupont" in proc.stdout and "503" in proc.stdout
    assert proc.returncode == 1


MARKED_TITLE_CROSSREF = '{"message": {"DOI": "10.5555/marked", "title": ["Benchmarks NOTE: superseded by the 2024 revision"], "author": [{"family": "Z", "given": "Q"}], "issued": {"date-parts": [[2020]]}}}'.encode()


def test_every_row_is_validated_before_any_row_is_written(store):
    """DECIDE, THEN WRITE. apply() ran no validation at all until the PR #30
    review: it issued a direct UPDATE on `records` and skipped every
    validate_paper rule. A provider title carrying an audit marker
    ("NOTE:", "recorded once" -- ordinary English) would then write a
    citation the door refuses on the next pass, leaving a row no script
    could fix."""
    db_path, export_dir = store
    conn = connect(db_path)
    conn.execute("UPDATE paper_fields SET access = 'DOI:10.5555/marked' WHERE record_id = 'dupont'")
    conn.commit(); conn.close()
    proc = _run_with(db_path, export_dir, ["--apply"],
                     "mod.FETCHER = lambda url, accept: MARKED")
    assert proc.returncode != 0, "a citation the door would refuse must not be written"
    assert "audit-trail" in (proc.stdout + proc.stderr)
    conn = connect(db_path)
    kept = conn.execute("SELECT provenance FROM records WHERE id='dupont'").fetchone()["provenance"]
    conn.close()
    assert kept == STALE, "nothing is written when validation refuses"


def test_a_github_backed_record_is_refreshed_not_reported_as_a_broken_doi(store):
    """Copilot review of PR #30, 2026-09-22. review() routed every
    non-arXiv kind to fetch_doi(), so the repository record Task G added
    reported ERROR -- "DOI merlinquantum/merlin is not registered at
    doi.org ... record the paper as hand-transcribed" -- which is both
    wrong and actively misleading advice. Route by kind.
    """
    db_path, export_dir = store
    conn = connect(db_path)
    conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
                 "VALUES ('repo', 'paper', 'A repository', 'stale citation', 'N/A', '2026-09-20', 'seeded')")
    conn.execute("INSERT INTO paper_fields (record_id, tier, access, disposition) "
                 "VALUES ('repo', 'seen', 'https://github.com/merlinquantum/merlin', 'Code repository: MerLin')")
    conn.commit(); conn.close()

    src = ("from tests.test_citations import GITHUB_JSON\n"
           "mod.FETCHER = lambda url, accept: GITHUB_JSON")
    proc = _run_with(db_path, export_dir, ["--ids", "repo"], src)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ERROR" not in proc.stdout, proc.stdout
    assert "DIFFERS repo" in proc.stdout, "the stale citation should be reported as differing"
    assert "merlinquantum, " in proc.stdout, "the fetched citation comes from the GitHub API"
    assert "not registered at doi.org" not in proc.stdout, (
        "a repository must never be reported as an unregistered DOI")


DATACITE_ARXIV_NO_JOURNAL_REF = json.dumps({"data": {"attributes": {
    "doi": "10.48550/arxiv.2303.05509",
    "titles": [{"title": "Quantum-Enhanced Greedy Combinatorial Optimization Solver"}],
    "creators": [{"familyName": "Dupont", "givenName": "Maxime"},
                 {"familyName": "Evert", "givenName": "Bram"}],
    "publicationYear": 2023, "publisher": "arXiv", "version": "2",
    "dates": [{"date": "2023-11-17T01:28:51Z", "dateType": "Submitted"}],
    "relatedIdentifiers": [{"relationType": "IsVersionOf", "relatedIdentifierType": "DOI",
                            "relatedIdentifier": "10.1126/sciadv.adi0487"}],
    "url": "https://arxiv.org/abs/2303.05509",
}}})


def test_a_fallback_that_returns_less_is_reported_as_poorer_not_differs(store):
    """When arXiv refuses, DataCite answers -- but its record for an arXiv
    DOI carries no journal reference, so the re-render DROPS the published
    venue that an earlier arXiv-sourced run had captured.

    Proposing that as a change would quietly trade a richer citation for a
    poorer one every time arXiv rate-limits, and `--apply` would then write
    it. The run reports POORER and leaves the row alone (PR #30 review
    round, 2026-09-22; found by re-running the live refresh after the
    other fixes, not by a reviewer).
    """
    db_path, export_dir = store
    richer = ('Dupont, M., Evert, B., "Quantum-Enhanced Greedy Combinatorial Optimization Solver," '
              'arXiv:2303.05509v2, Science Advances 9, 45 (2023), DOI:10.1126/sciadv.adi0487, 2023-11-17')
    conn = connect(db_path)
    conn.execute("UPDATE records SET provenance = ?, value = ? WHERE id = 'dupont'",
                 (richer, "Quantum-Enhanced Greedy Combinatorial Optimization Solver"))
    conn.commit(); conn.close()

    src = ("import urllib.error\n"
           "def fetcher(url, accept):\n"
           "    if 'export.arxiv.org' in url:\n"
           "        raise urllib.error.HTTPError(url, 406, 'refused', {}, None)\n"
           "    return DATACITE\n"
           "mod.FETCHER = fetcher\n"
           "mod.citations._sleep = lambda s: None")
    proc = _run_with(db_path, export_dir, ["--apply"], src)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "POORER  dupont" in proc.stdout, proc.stdout
    assert "returned less than the stored citation carries" in proc.stdout

    conn = connect(db_path)
    kept = conn.execute("SELECT provenance FROM records WHERE id='dupont'").fetchone()["provenance"]
    conn.close()
    assert kept == richer, "the richer citation must survive an --apply run"
    assert "Science Advances" in kept
