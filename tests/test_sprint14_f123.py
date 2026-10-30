"""F123 (Sprint 14 Task C, F98's release): Roadmap-to-QML from a239747648
to ea6f42a7c0 (INTAKE_WORKFLOW.md section 57). The list's copies and the
PDFs live outside the repository, so the source tests are live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f123", ROOT / "scripts" / "sprint14_f123_roadmap.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F123 = _script()
NEW = ["2609.19983", "2610.32762", "2610.34430", "2610.35126"]


def test_the_release_points_at_its_own_commit_and_keeps_f104s():
    """The loaded F104 module is this script's own copy: F104's constants
    are untouched where F104's tests load it."""
    assert F123.f104.COMMIT == F123.COMMIT != F123.PREVIOUS
    assert F123.PREVIOUS.startswith("a239747648") and F123.COMMIT.startswith("ea6f42a7c0")
    assert F123.f104.COPY_DIR.name == "Roadmap-to-QML_ea6f42a7c0" and F123.PREVIOUS_DIR.name.endswith("a239747648")
    assert "ea6f42a7c0" in F123.f104.FOUND_VIA
    assert F123.f104.MANIFEST.name == "sprint14_f123_roadmap.json"
    assert "sprint14_f123_roadmap.py" in F123.f104.entry("2609.19983", ("2026/2026.md", "x"))["updated_reason"]


def test_a_mark_is_read_from_the_list_line():
    """Proven to fail by injection, 2026-10-30: with the pattern's
    RETRACTED alternative removed, the second line went unmatched."""
    lines = ("- [Banday et al, 2024, Early Detection](https://arxiv.org/pdf/2409.10932) **[WITHDRAWN by the authors]**",
             "- [Valdez & Melin, 2022, A review](https://link.springer.com/article/10.1007/s00500-022-07037-4) "
             "**[RETRACTED 10 March 2026]**",
             "- [Lin et al., 2023, Implementing](https://arxiv.org/abs/2304.05672) **[WITHDRAWN by the authors; "
             "duplicate upload, published as [2210.14450](https://arxiv.org/abs/2210.14450)]**")
    assert [F123._MARK.search(x).group(1).split()[0] for x in lines] == ["WITHDRAWN", "RETRACTED", "WITHDRAWN"]
    assert F123._MARK.search("- [A paper](https://arxiv.org/abs/2401.00001)") is None


@pytest.mark.live_store
def test_the_manifest_names_the_copy_and_what_changed():
    m = json.loads(F123.MANIFEST.read_text(encoding="utf-8"))
    assert m["commit"] == F123.COMMIT and m["previous_commit"] == F123.PREVIOUS
    for name, digest in m["files"].items():
        assert hashlib.sha256(F123.f104.copy_of(name).read_bytes()).hexdigest() == digest, name
    assert [e["arxiv"] for e in m["entered"]] == NEW
    assert len(m["newly_linked_since_previous"]) == 32 and set(NEW) <= set(m["newly_linked_since_previous"])
    assert m["routes_added_to_held_papers"] == 28
    assert len(m["marks"]) == 7 and all(x["store_agrees"] for x in m["marks"])


@pytest.mark.live_store
def test_the_store_holds_the_four_and_routes_only_the_newly_linked(live_conn):
    """Proven to fail by injection, 2026-10-30: run against the backup taken
    before the apply, it named sein-2026 (no record) first."""
    m = json.loads(F123.MANIFEST.read_text(encoding="utf-8"))
    for e in m["entered"]:
        row = live_conn.execute("SELECT tier, access FROM paper_fields WHERE record_id = ?", (e["record_id"],)).fetchone()
        assert row is not None and row[0] in ("seen", "read"), e["record_id"]
        assert re.match(rf"arXiv:{re.escape(e['arxiv'])} \| ", row[1]), e["record_id"]
        assert [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                                (e["record_id"],))] == ["qml"], e["record_id"]
    routed = {r[0] for r in live_conn.execute("SELECT record_id FROM paper_found_via WHERE route LIKE ?",
                                              (f"{F123.f104.FOUND_VIA}%",))}
    hold = F123.f104.holders(live_conn)
    want = {rid for i in m["newly_linked_since_previous"] for rid in hold.get(i, [])}
    assert routed == want and len(routed) == 32


@pytest.mark.live_store
def test_a_second_apply_enters_nothing_and_adds_no_route(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        before = conn.execute("SELECT COUNT(*) FROM paper_found_via").fetchone()[0]
        log, manifest = F123.f104.apply_changes(conn, apply=True, fetcher=F123.f104.CachedFetcher())
        after = conn.execute("SELECT COUNT(*) FROM paper_found_via").fetchone()[0]
    finally:
        conn.close()
    assert not log and manifest["entered"] == [] and before == after
    assert manifest["arxiv_ids_listed"] == 1450  # not vacuous: the list was read
