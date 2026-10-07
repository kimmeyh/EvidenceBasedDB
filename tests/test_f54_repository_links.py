"""F54 (Sprint 7 Task E): every repository link recovered from a failed
note says how its repository was found, after the paper's own sentence
(team lead, 2026-10-05: a match found by search is recorded as found by
search, with the query)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f54", ROOT / "scripts" / "sprint7_f54_recover_repo_notes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_recovered_link_says_how_it_was_found(live_conn):
    """Proven to fail by injection, 2026-10-06: with the check pointed at a
    phrase the evidence does not carry ("How located"), the count went red
    (0 against 24)."""
    rows = live_conn.execute("SELECT from_id, to_id, evidence FROM source_links "
                             "WHERE evidence LIKE '%How found (Sprint 7 F54)%'").fetchall()
    assert len(rows) == sum(len(t) for t in _script().RESOLVED.values()) == 24
    for from_id, to_id, evidence in rows:
        quote, _, how = evidence.partition(" [How found (Sprint 7 F54): ")
        assert quote.strip(), f"{from_id} -> {to_id}: the paper's own sentence is missing"
        assert how.endswith(".]") and len(how) > 20, f"{from_id} -> {to_id}: how it was found is missing"


def test_every_screened_f35_link_carries_its_sentence(live_conn):
    """The F35 slice: one link per distinct 'own' row with a link type, each
    with the paper's own sentence first. Proven to fail by injection,
    2026-10-06: with rows_to_link no longer dropping the duplicate rows, the
    expected count rose to 41 against 39 links."""
    spec = importlib.util.spec_from_file_location("f35", ROOT / "scripts" / "sprint7_f35_screen_links.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    expected = mod.rows_to_link(json.loads(mod.SCREEN.read_text(encoding="utf-8")))
    rows = live_conn.execute("SELECT evidence FROM source_links "
                             "WHERE evidence LIKE '%How found (Sprint 7 F35 screen)%'").fetchall()
    assert len(rows) == len(expected) == 39
    assert all(r[0].split(" [How found")[0].strip() for r in rows)


def test_the_search_match_names_its_query(live_conn):
    row = live_conn.execute("SELECT evidence FROM source_links WHERE from_id = "
                            "'arturmiroszewski-large-scale-qsvm-github-repo'").fetchone()
    assert row and 'query "Large_scale_QSVM in:name"' in row[0]
