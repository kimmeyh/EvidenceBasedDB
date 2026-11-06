"""Sprint 16 Tasks F and G: Roadmap-to-QML from ea6f42a7c0 to 399b022651, and the team lead's two named papers
(INTAKE_WORKFLOW.md section 72). The list's copies and the PDFs live outside the repository, so the source tests are
live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F16 = _load("f16_roadmap", "sprint16_f114_roadmap.py")
G16 = _load("g16_named", "sprint16_f57_named.py")
ARXIV = ["2610.42029", "2611.00272", "2611.00303", "2611.05079"]
QUANTUM = ["10.22331/q-2026-10-20-2239", "10.22331/q-2026-10-29-2256"]


def test_only_a_quantum_link_new_since_the_previous_commit_is_entered(tmp_path, monkeypatch):
    """A Quantum link already listed at the previous commit is not new, even when the store does not hold it.
    Proven to fail by injection, 2026-11-06: with the `url not in before` condition removed from `new_quantum`, the
    old link was entered too."""
    old, new = tmp_path / "old", tmp_path / "new"
    for folder, text in ((old, "[A](https://quantum-journal.org/papers/q-2020-01-01-1/)\n"),
                         (new, "[A](https://quantum-journal.org/papers/q-2020-01-01-1/)\n"
                               "[B](https://quantum-journal.org/papers/q-2026-10-20-2239/)\n"
                               "[C](https://doi.org/10.1000/not-quantum)\n")):
        (folder / "x").mkdir(parents=True)
        (folder / "x" / "x.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(F16.f104, "FILES", ("x/x.md",))
    monkeypatch.setattr(F16.f104, "COPY_DIR", new)
    monkeypatch.setattr(F16, "PREVIOUS_DIR", old)
    monkeypatch.setattr(F16.f104, "held_text", lambda conn: "")
    got = F16.new_quantum(None)
    assert [g["doi"] for g in got] == ["10.22331/q-2026-10-20-2239"] and got[0]["label"] == "B"
    assert F16.quantum_name("q-2026-10-20-2239", type("M", (), {"authors": ["Caro, M."], "title": "A (b) c"})) == \
        "2026-10_Caro_A-b-c_q-2026-10-20-2239.pdf"


def test_the_release_points_at_its_own_commit():
    assert F16.f104.COMMIT == F16.COMMIT != F16.PREVIOUS
    assert F16.PREVIOUS.startswith("ea6f42a7c0") and F16.COMMIT.startswith("399b022651")
    assert F16.f104.COPY_DIR.name == "Roadmap-to-QML_399b022651" and "399b022651" in F16.f104.FOUND_VIA
    assert F16.f104.MANIFEST.name == "sprint16_f114_roadmap.json"


def test_the_named_papers_manifest_is_named_in_the_workflow():
    assert G16.intake.unrecorded_manifest(G16.MANIFEST) is None


@pytest.mark.live_store
def test_the_six_list_papers_and_two_named_papers_are_held(live_conn):
    """Proven to fail before the applies, 2026-11-06: none of the 8 records existed."""
    manifest = json.loads(F16.MANIFEST.read_text(encoding="utf-8"))
    assert sorted(e["arxiv"] for e in manifest["entered"]) == ARXIV
    assert sorted(e["doi"] for e in manifest["quantum_entered"]) == QUANTUM
    rids = [e["record_id"] for e in manifest["entered"] + manifest["quantum_entered"]]
    rids += [G16.WHITE_PAPER, "goes-2021-qboost-regression-problems-solving-partial"]
    for rid in rids:
        tier, access, evidence = live_conn.execute("SELECT tier, access, evidence FROM paper_fields WHERE "
                                                   "record_id = ?", (rid,)).fetchone()
        # Entered "seen"; Task F's reads then move a list paper to "read" (full suite, 2026-11-06: bhalgami)
        assert tier in ("seen", "read"), rid
        local = Path([p.strip() for p in access.split("|") if p.strip().lower().endswith(".pdf")][0])
        assert hashlib.sha256(local.read_bytes()).hexdigest() in evidence, rid
    for rid in rids[:6]:
        assert live_conn.execute("SELECT 1 FROM paper_found_via WHERE record_id = ? AND route LIKE ?",
                                 (rid, f"{F16.f104.FOUND_VIA}%")).fetchone(), rid
    assert live_conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = 'code-of'",
                             (G16.REPO, G16.WHITE_PAPER)).fetchone()
    assert "hand-transcribed from" in live_conn.execute("SELECT provenance FROM records WHERE id = ?",
                                                        (G16.WHITE_PAPER,)).fetchone()[0]
    assert live_conn.execute("SELECT disposition FROM paper_fields WHERE record_id = ?",
                             (G16.REPO,)).fetchone()[0] == G16.REPO_DISPOSITION  # no longer "linked to no paper"


@pytest.mark.live_store
def test_a_rerun_of_the_briefs_plans_the_briefs_already_written(live_conn):
    """Fresh-eyes review: with the re-entry groups found afresh, a re-run after the briefs were written skipped
    g133-r1 and g154-r1 and planned g156 in full and g157. Proven to fail by injection, 2026-11-06: with REENTER
    emptied, the plan differed from the briefs on disk."""
    local = _load("s16_local", "sprint16_f114_local.py")
    groups, _ = local.plan(local.ledger(), live_conn)
    for g, recs in groups.items():
        brief = json.loads((local.LOCAL / "briefs" / f"{g}.json").read_text(encoding="utf-8"))
        assert [r["record_id"] for r in brief["records"]] == [r["record_id"] for r in recs], g
    assert sorted(groups) == ["g133-r1", "g154-r1", "g155", "g156", "g333", "g334"]


@pytest.mark.live_store
def test_a_second_apply_enters_nothing(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        assert all(line.startswith("exists") for line in G16.apply_changes(conn, apply=True))
        log, manifest = F16.f104.apply_changes(conn, True, F16.CachedFetcher())
        assert not log and manifest["arxiv_ids_new"] == 0 and F16.new_quantum(conn) == []
    finally:
        conn.close()
