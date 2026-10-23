"""F101 (Sprint 12 Task A): no HTML entity anywhere in the store, the
metadata parsers undo the escapes the providers send, and every stored
quote parses (INTAKE_WORKFLOW.md section 42).

The parser tests run on CI; the store tests are live_store."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.citations import parse_crossref, parse_datacite  # noqa: E402
from store.quotes import QUOTE, require_verbatim, stray_quote_marks  # noqa: E402

ENTITY = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")


def test_crossref_titles_and_venues_are_unescaped():
    """Proven to fail by injection, 2026-10-23: with `_text` returning its
    input without `html.unescape`, this test and the DataCite one below
    showed "Machine learning &amp; AI" and "Divide &amp; Conquer".
    Restored."""
    body = json.dumps({"message": {"DOI": "10.1/x", "title": ["Machine learning &amp; AI"],
                                   "container-title": ["Science &amp; Technology Libraries"],
                                   "author": [{"family": "O&#39;Brien", "given": "M."}],
                                   "publisher": "Taylor &amp; Francis",
                                   "issued": {"date-parts": [[2020, 10, 1]]}}}).encode()
    md = parse_crossref(body)
    assert md.title == "Machine learning & AI"
    assert md.venue == "Science & Technology Libraries"
    assert md.authors == ["O'Brien, M."]
    assert md.extra["publisher"] == "Taylor & Francis"


def test_datacite_titles_venues_and_names_are_unescaped():
    """The venue and names were missed by 5466953 (fresh-eyes review).
    Proven to fail by injection, 2026-10-23: with the publisher passed
    through unchanged, `venue` read "Taylor &amp; Francis". Restored."""
    body = json.dumps({"data": {"attributes": {"doi": "10.1/y", "titles": [{"title": "Divide &amp; Conquer"}],
                                               "publisher": "Taylor &amp; Francis",
                                               "creators": [{"familyName": "O&#39;Brien", "givenName": "M."},
                                                            {"name": "R&amp;D Group"}],
                                               "publicationYear": 2024, "dates": []}}}).encode()
    md = parse_datacite(body)
    assert md.title == "Divide & Conquer"
    assert md.venue == "Taylor & Francis"
    assert md.authors == ["O'Brien, M.", "R&D Group"]


@pytest.mark.live_store
def test_no_html_entity_is_stored_anywhere(live_conn):
    """Every text field of every table. Proven to fail by injection,
    2026-10-23: run against the backup taken before the first apply, it
    named the 4 records section 42 corrected (6 fields)."""
    found = []
    tables = [r[0] for r in live_conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    for table in tables:
        cols = [c[1] for c in live_conn.execute(f"PRAGMA table_info({table})")]
        for row in live_conn.execute(f"SELECT * FROM {table}"):
            found += [f"{table}.{col}: {row[0]}" for col, v in zip(cols, row) if isinstance(v, str) and ENTITY.search(v)]
    assert not found, found


@pytest.mark.live_store
def test_every_stored_quote_parses(live_conn):
    """I1a's stray-quote check over the whole store, plus a context with no
    quote at all, which the stray check cannot see (fresh-eyes review of
    5466953: 7 Sprint 5 contexts held a passage with no quote marks): 0
    after section 42. Proven to fail by injection, 2026-10-23: run against
    the backup taken before the first apply, it named the 4 assertions
    section 42 corrected (the Cyc quote and 3 with no anchor); against the
    one taken before the third apply, it named the 7 with no quote marks.
    Restored to the live store."""
    bad = [rid for rid, ctx in live_conn.execute("SELECT record_id, citation_context FROM assertion_fields")
           if ctx and ctx.strip() and (stray_quote_marks(ctx) or not QUOTE.findall(ctx))]
    assert not bad, bad


def _script():
    spec = importlib.util.spec_from_file_location("f101", ROOT / "scripts" / "sprint12_f101_corrections.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F101 = _script()


@pytest.mark.live_store
@pytest.mark.parametrize("rid", sorted(F101.QUOTE_FIXES))
def test_each_corrected_quote_is_whole_and_holds_its_value(live_conn, rid):
    """Each re-quoted assertion as stored: one quote per passage, all
    verbatim in its source, the value's figures held, and a corrected
    value (VALUE_FIXES) is the one stored."""
    ctx, value = live_conn.execute(
        "SELECT f.citation_context, r.value FROM assertion_fields f JOIN records r ON r.id = f.record_id "
        "WHERE f.record_id = ?", (rid,)).fetchone()
    source, passages = F101.QUOTE_FIXES[rid]
    assert ctx == F101.context_of(passages)
    assert len(QUOTE.findall(ctx)) == len(passages)
    assert value == F101.VALUE_FIXES.get(rid, value)
    require_verbatim(rid, ctx, F101.text_of(source), value=value)


@pytest.mark.live_store
def test_paper_evidence_is_corrected_and_the_history_says_what_changed(live_conn):
    """The fourth apply (fresh-eyes review of 6d2bed4): each evidence fix
    made, no ".;" join left on a local-copy note, and each history note
    present. Proven to fail by injection, 2026-10-23: run against the
    backup taken before the fourth apply, it named the Kakavand evidence."""
    for paper, fixes in F101.EVIDENCE_FIXES.items():
        evidence = live_conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?", (paper,)).fetchone()[0]
        for old, new in fixes:
            assert new in evidence and old not in evidence, paper
    assert set(F101.EVIDENCE_FIXES) <= set(F101.LOCAL_COPIES)
    for paper in F101.LOCAL_COPIES:
        evidence = live_conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?", (paper,)).fetchone()[0]
        assert F101.JOIN[0] not in evidence, paper
    for rid, note in {**F101.ADDENDA, **F101.SYNC_REASONS}.items():
        history = live_conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0]
        assert note in history, rid
