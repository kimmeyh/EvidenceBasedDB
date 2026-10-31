"""Sprint 14 Task G (F118): the inventory and theme selection behind the memo, against a store built in memory."""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _themes():
    spec = importlib.util.spec_from_file_location("f118_themes", ROOT / "scripts" / "f118_themes.py")
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    return t


def _store() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        "CREATE TABLE records (id TEXT, class TEXT, value TEXT, provenance TEXT, evidence_tag TEXT, certainty TEXT, "
        "certainty_reasons TEXT);"
        "CREATE TABLE assertion_fields (record_id TEXT, claim_type TEXT);"
        "CREATE TABLE record_contexts (record_id TEXT, context_id TEXT);"
        "CREATE TABLE paper_reads (record_id TEXT, extent TEXT);"
        "CREATE TABLE paper_fields (record_id TEXT, tier TEXT);")
    rows = [("bp", "The paper proves a barren plateau for global costs.", "high", "N/A", ["qml", "qc"]),
            ("ff", "The authors report an isolation forest baseline on credit card fraud.", "low", "SIM", ["ml"]),
            ("other", "The authors state the company's address.", "low", "N/A", ["world"])]
    for i, v, c, tag, ctxs in rows:
        conn.execute("INSERT INTO records VALUES (?, 'assertion', ?, 'p', ?, ?, '')", (i, v, tag, c))
        conn.execute("INSERT INTO assertion_fields VALUES (?, 'positive')", (i,))
        conn.executemany("INSERT INTO record_contexts VALUES (?, ?)", [(i, x) for x in ctxs])
    conn.execute("INSERT INTO records VALUES ('p', 'paper', '', '', '', NULL, '')")
    conn.execute("INSERT INTO paper_reads VALUES ('p', 'full')")
    conn.execute("INSERT INTO paper_fields VALUES ('p', 'read')")
    return conn


def test_the_inventory_counts_each_assertion_once_and_every_context():
    """A record with two contexts counts once among the assertions and once under each context. Proven to fail by
    injection, 2026-10-30: with the GROUP BY removed from _rows, "bp" counted twice."""
    t = _themes()
    conn = _store()
    rows = t._rows(conn)
    inv = t.inventory(conn, rows)
    assert inv["assertions"] == 3 and inv["papers"] == 1
    assert inv["by_context"] == {"qml": 1, "qc": 1, "ml": 1, "world": 1}
    assert inv["by_certainty"] == {"low": 2, "high": 1} and inv["by_tag"] == {"N/A": 2, "SIM": 1}


def test_a_theme_takes_what_its_pattern_names_and_nothing_else():
    """Proven to fail by injection, 2026-10-30: with the trainability pattern matching "the", "other" was taken."""
    t = _themes()
    themes = t.select(t._rows(_store()))
    assert [r["id"] for r in themes["trainability"]] == ["bp"]
    assert [r["id"] for r in themes["fraud-and-imbalance"]] == ["ff"]
    assert [r["id"] for r in themes["classical-families"]] == ["ff"]
    assert all(r["id"] != "other" for v in themes.values() for r in v)
