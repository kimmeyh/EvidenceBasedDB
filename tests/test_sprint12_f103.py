"""F103 (Sprint 12 Task E): PoJen Wang's two Classiq challenge posts, the
organiser's wrap-up and the named repository, entered from saved copies
(INTAKE_WORKFLOW.md section 44). The copies live outside the repository,
so every test here is live_store."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f103", ROOT / "scripts" / "sprint12_f103_intake.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F103 = _script()


def test_every_quote_and_figure_is_in_its_saved_page():
    """Proven to fail by injection, 2026-10-23: with "272" changed to
    "273" in the depth-95 value, verify_all named
    wang-2026-classiq-logo-oracle-depth-95-272-cnots. Restored."""
    assert len(F103.verify_all()) == 5


def test_the_store_holds_what_the_script_writes(live_conn):
    """Each source at `read` with every copy's SHA-256 in its evidence;
    each assertion as written; the two parts name each other in their
    dispositions and are not linked (no link type fits a series,
    ADR-0005 A10); the repository is linked to nothing. Proven to fail by
    injection, 2026-10-23: run against the backup taken before the apply,
    it named the first source; against the backup taken before the
    applicability was added, it named the first source's empty
    applicability."""
    for _, entry in F103.entries():
        row = live_conn.execute("SELECT tier, evidence, access FROM paper_fields WHERE record_id = ?",
                                (entry["id"],)).fetchone()
        assert row is not None and row[0] == "read", entry["id"]
        assert tuple(row[1:]) == (entry["evidence"], entry["access"]), entry["id"]
        applicability = [list(r) for r in live_conn.execute(
            "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (entry["id"],))]
        assert applicability == entry["applicability"], entry["id"]
    part1, part2 = F103.SOURCES["part1"]["id"], F103.SOURCES["part2"]["id"]
    assert part2 in F103.SOURCES["part1"]["disposition"] and part1 in F103.SOURCES["part2"]["disposition"]
    repo = "wangy8205165-quantum-neuralnetwork-whitepaper-github-repo"
    for rid in (part1, part2, repo):
        assert not live_conn.execute("SELECT 1 FROM source_links WHERE from_id = ? OR to_id = ?",
                                     (rid, rid)).fetchone(), rid
    for key, a in F103.ASSERTIONS:
        row = live_conn.execute("SELECT r.value, r.certainty, r.certainty_reasons, f.citation_context FROM records r "
                                "JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        assert row is not None and tuple(row) == (a.value, a.certainty, a.certainty_reasons,
                                                  a.citation_context), a.id
        assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                 (F103.SOURCES[key]["id"], a.id)).fetchone(), a.id


def test_a_second_apply_writes_nothing_and_every_copy_is_named(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        log = F103.apply_changes(conn, apply=True)
        assert F103.PART2_PDF.name not in F103.unnamed_pdfs(conn)
    finally:
        conn.close()
    changed = [x for x in log if not x.startswith(("exists", "before:", "after:", "unnamed PDF"))]
    assert not changed, changed
