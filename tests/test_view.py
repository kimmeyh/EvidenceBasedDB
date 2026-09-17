"""Tests for scripts/view.py (Sprint 2 Task G, F3).

F3: an easy, CLI-startable way to view DB content -- three modes
(contexts, paper, assertion), plain text or --json, no server. Exercised
against a small synthetic store built with the same helpers production
uses (store.create_store, store.ingest), not the real 46-paper store, so
this suite passes independent of what the real store currently holds.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCRIPT = ROOT / "scripts" / "view.py"

from store import create_store  # noqa: E402
from store.ingest import AssertionRecord, PaperRecord, insert_assertion, insert_paper  # noqa: E402


def _load_view_module():
    spec = importlib.util.spec_from_file_location("view", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def store_conn():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "evidence.db"
        conn = create_store(db_path)

        insert_paper(
            conn,
            PaperRecord(
                id="test-paper-one",
                value="A Test Paper About QML",
                tier="read",
                citation="Tester, T., \"A Test Paper About QML\", 2026",
                access="local file",
                disposition="fixture",
                context="qml",
                applicability=[("qml", "primary topic"), ("qc", "uses a QC backend")],
                checked_against_source="2026-09-17, fixture",
            ),
        )
        insert_assertion(
            conn,
            AssertionRecord(
                id="test-assertion-two",
                value="A second assertion that contradicts the first",
                provenance="test-paper-one, p2",
                evidence_tag="N/A",
                context="qml",
                certainty="low",
                certainty_reasons="fixture",
                fidelity="exact",
                reading_level=10,
                documents=["test-paper-one"],
            ),
        )
        insert_assertion(
            conn,
            AssertionRecord(
                id="test-assertion-one",
                value="Test assertion value with unicode: café, αβγ",
                provenance="test-paper-one, p1",
                evidence_tag="N/A",
                context="qml",
                certainty="high",
                certainty_reasons="fixture",
                fidelity="exact",
                reading_level=10,
                documents=["test-paper-one"],
                contradicts=["test-assertion-two"],
            ),
            yielded_by="test-paper-one",
        )
        conn.commit()
        yield conn
        conn.close()


def test_contexts_list_reports_direct_and_applicability_counts(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_list(store_conn)
    qml = next(c for c in data["contexts"] if c["id"] == "qml")
    assert qml["direct_count"] >= 2
    qc = next(c for c in data["contexts"] if c["id"] == "qc")
    assert qc["applicability_count"] >= 1


def test_contexts_detail_lists_records_and_applicability_papers(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_detail(store_conn, "qml")
    ids = {r["id"] for r in data["records"]}
    assert "test-paper-one" in ids
    assert "test-assertion-one" in ids

    qc_data = mod.cmd_contexts_detail(store_conn, "qc")
    applicability_ids = {r["id"] for r in qc_data["papers_via_applicability"]}
    assert "test-paper-one" in applicability_ids


def test_contexts_detail_errors_on_unknown_context(store_conn):
    mod = _load_view_module()
    data = mod.cmd_contexts_detail(store_conn, "no-such-context")
    assert "error" in data


def test_paper_mode_includes_full_yielded_assertion_fields(store_conn):
    mod = _load_view_module()
    data = mod.cmd_paper(store_conn, "test-paper-one")
    assert data["id"] == "test-paper-one"
    assert len(data["applicability"]) == 2
    assert len(data["yields"]) == 1
    yielded = data["yields"][0]
    assert yielded["id"] == "test-assertion-one"
    assert yielded["certainty"] == "high"


def test_paper_mode_errors_on_unknown_paper(store_conn):
    mod = _load_view_module()
    data = mod.cmd_paper(store_conn, "no-such-paper")
    assert "error" in data


def test_assertion_mode_resolves_relations_to_values_not_bare_ids(store_conn):
    mod = _load_view_module()
    data = mod.cmd_assertion(store_conn, "test-assertion-one")
    assert data["id"] == "test-assertion-one"
    assert data["yielded_by_paper"] == "test-paper-one"
    assert len(data["contradicts"]) == 1
    contradicted = data["contradicts"][0]
    assert contradicted["id"] == "test-assertion-two"
    assert contradicted["value"] == "A second assertion that contradicts the first"


def test_assertion_mode_errors_on_unknown_assertion(store_conn):
    mod = _load_view_module()
    data = mod.cmd_assertion(store_conn, "no-such-assertion")
    assert "error" in data


def test_json_output_survives_non_ascii_characters(store_conn, capsys):
    """Regression: Windows consoles default to cp1252, which cannot encode
    accented or Greek characters. An earlier version of this script crashed
    with UnicodeEncodeError on --json output containing such text; fixed by
    reconfiguring stdout to UTF-8 at startup."""
    mod = _load_view_module()
    data = mod.cmd_assertion(store_conn, "test-assertion-one")
    text = json.dumps(data, indent=2, ensure_ascii=False)
    assert "café" in text
    assert "αβγ" in text
    parsed = json.loads(text)
    assert parsed["value"] == data["value"]
