"""F148 (Sprint 18 Task F): the counts a document names are printed from the store by `scripts/doc_counts.py`,
never typed, and the block a document holds must match the store.

Proven to fail by injection, 2026-11-21, each restored (a grep for INJECTED in scripts/doc_counts.py finds nothing):
- `rewrite` refusing only a document with no block (`if n == 0:  # INJECTED`):
  test_a_document_with_no_block_or_two_is_refused went red (two blocks, and an end before its begin, passed);
- `rewrite` adding a newline after the block: test_the_block_is_rewritten_in_place_and_nothing_else_changes went red;
- the papers line printing the assertion count: test_the_block_states_each_count_it_was_given went red;
- the basis pattern without ":" in its stop class (the fresh-eyes review: 9 LOW reasons fell into "other"):
  test_a_basis_is_named_up_to_the_why_low_grade_appends went red;
- the assertion count in INTAKE_WORKFLOW.md's block typed as 40,111 against a store holding 40,112:
  test_each_documents_block_matches_the_store went red; `doc_counts.py --write` restored it.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "doc_counts.py"
DOCS = [ROOT / "docs" / "INTAKE_WORKFLOW.md"]


def _mod():
    spec = importlib.util.spec_from_file_location("doc_counts", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FAKE = {"assertions": 10, "by_level": {"high": 4, "low": 6}, "high_bases": [("the paper's own setup", 4)],
        "low_bases": [("a theoretical result", 6)], "papers": 3, "tiers": {"read": 2, "seen": 1},
        "groups": 5, "groups_read": 4, "groups_reviewed": 3}


def test_the_block_is_rewritten_in_place_and_nothing_else_changes(tmp_path):
    mod = _mod()
    doc = tmp_path / "doc.md"
    old = mod.block({**FAKE, "assertions": 9}, "2026-11-20")
    doc.write_text(f"# Title\n\nbefore\n\n{old}\n\nafter\n", encoding="utf-8")
    new = mod.block(FAKE, "2026-11-21")
    assert mod.rewrite(doc, new)
    assert doc.read_text(encoding="utf-8") == f"# Title\n\nbefore\n\n{new}\n\nafter\n"
    assert not mod.rewrite(doc, new)  # a second write changes nothing


def test_a_document_with_no_block_or_two_is_refused(tmp_path):
    mod = _mod()
    text = mod.block(FAKE, "2026-11-21")
    for body in ("no block here\n", f"{text}\n{text}\n", f"{mod.END}\n{mod.BEGIN}\n"):
        doc = tmp_path / "doc.md"
        doc.write_text(body, encoding="utf-8")
        with pytest.raises(SystemExit, match="REFUSED"):
            mod.rewrite(doc, text)
        assert doc.read_text(encoding="utf-8") == body


def test_the_block_states_each_count_it_was_given():
    mod = _mod()
    text = mod.block(FAKE, "2026-11-21")
    for piece in ("as of 2026-11-21", "Assertions: 10 (HIGH 4, LOW 6)", "the paper's own setup 4",
                  "a theoretical result 6", "Papers and other sources: 3 (read 2, seen 1)", "Ledger groups: 5",
                  "with a read file 4", "with a review file 3"):
        assert piece in text, piece


def test_a_basis_is_named_up_to_the_why_low_grade_appends():
    """low_grade writes "Started LOW: <basis>: <why>"; the basis must not take the why with it."""
    import sqlite3
    mod = _mod()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (class, certainty, certainty_reasons)")
    rows = [("Started LOW: an empirical result from one study. NOT upgraded",) * 1] * 150
    rows += [("Started LOW: an empirical result from one study: one run on one device. NOT upgraded",)] * 5
    conn.executemany("INSERT INTO records VALUES ('assertion', 'low', ?)", rows)
    assert mod.bases(conn, "low") == [("an empirical result from one study", 155)]


@pytest.mark.live_store
@pytest.mark.parametrize("doc", DOCS, ids=lambda d: d.name)
def test_each_documents_block_matches_the_store(doc):
    """The block is the document's current count: after a store write, run `scripts/doc_counts.py --write`."""
    mod = _mod()
    held = mod.block_in(doc)
    day = re.search(r"as of (\d{4}-\d{2}-\d{2})", held).group(1)
    with mod.read_only() as conn:
        want = mod.block(mod.counts(conn), day)
    assert held == want, "the counts block no longer matches the store: run scripts/doc_counts.py --write " + str(doc)
