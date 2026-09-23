"""scripts/render_f11_packet.py renders every screened record with a
source link and a timing row (Sprint 4 Task E). Runs against a temp store,
never the live one; the committed packet's currency against the live store
is checked separately below.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from store import connect, create_store  # noqa: E402

SCRIPT = ROOT / "scripts" / "render_f11_packet.py"
PACKET = ROOT / "docs" / "sprints" / "SPRINT_4_F11_ADJUDICATION_PACKET.md"


def _load():
    spec = importlib.util.spec_from_file_location("render_f11_packet", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        conn = create_store(db_path)
        for pid, tier, access in [("a-screened", "screened", "arXiv:2303.05509"), ("b-seen", "seen", "DOI:10.1145/3007651"),
                                  ("c-screened", "screened", r"D:\x\y.pdf | https://example.org/page")]:
            conn.execute("INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) VALUES (?, 'paper', 'T', 'C', 'N/A', '2026-09-19', 'r')", (pid,))
            conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, 'qc')", (pid,))
            conn.execute("INSERT INTO paper_fields (record_id, tier, access, disposition) VALUES (?, ?, ?, 'd')", (pid, tier, access))
        conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES ('a-screened', 'qc', 'why -- p.1')")
        conn.commit()
        yield conn
        conn.close()


def test_packet_lists_only_screened_records_with_source_links_and_timing_rows(store):
    mod = _load()
    mod.F10_FINDINGS = {"a-screened": "finding a", "c-screened": "finding c"}  # the timed set is the F10 set
    text = mod.render(store)
    assert "### 1. `a-screened`" in text and "### 2. `c-screened`" in text
    assert "b-seen" not in text, "a record outside the F10 set is not in the F11 set"
    # A record F10 reviewed stays in the timed set after a tier change (Task H promoted five to read).
    store.execute("UPDATE paper_fields SET tier = 'read', checked_against_source = 'never' WHERE record_id = 'a-screened'")
    assert "### 1. `a-screened`" in mod.render(store) and "**Tier**: read" in mod.render(store)
    assert "https://arxiv.org/abs/2303.05509" in text
    assert r"D:\x\y.pdf | https://example.org/page" in text
    assert "| 1 | `a-screened` |" in text and "| 2 | `c-screened` |" in text
    assert "`qc`: why -- p.1" in text


def test_screened_records_added_after_f10_are_listed_apart_not_timed(store):
    """The comparison is apples to apples: the 18 F10 reviewed. A screened
    record added later (Task G's MerLin paper) is named but not numbered."""
    mod = _load()
    mod.F10_FINDINGS = {"a-screened": "finding a"}
    text = mod.render(store)
    assert "### 1. `a-screened`" in text and "### 2." not in text
    assert "not part of the timed comparison" in text and "`c-screened`" in text
    assert "| 1 | `a-screened` |" in text and "`c-screened` |" not in text.split("## Timing sheet")[1]


LIVE_DB = ROOT / "store" / "evidence.db"


@pytest.mark.skipif(not LIVE_DB.exists(),
                    reason="store/evidence.db not present (gitignored; build it locally)")
def test_committed_packet_is_current_against_the_live_store():
    """The packet is generated; a stale committed copy would time the wrong
    records.

    SKIPS rather than fails when the store is absent, matching
    tests/test_export_currency.py. It used to `pytest.fail`, which made CI
    red on every fresh checkout: `store/evidence.db` is gitignored and the
    workflow runs a bare `pytest -q` without building it (Copilot review of
    PR #30, 2026-09-23). A guard that cannot run is not a guard that failed.
    """
    conn = connect(LIVE_DB)
    try:
        expected = _load().render(conn)
    finally:
        conn.close()
    assert PACKET.exists(), "run python scripts/render_f11_packet.py"
    assert PACKET.read_text(encoding="utf-8") == expected, "packet is stale: re-run scripts/render_f11_packet.py and commit"
