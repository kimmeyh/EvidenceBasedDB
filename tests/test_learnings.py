"""The computed synthesis (Sprint 5 Task I, F28; docs/LEARNING_SYNTHESIS.md).

Runs scripts/learnings.py against a store rebuilt from the committed
export, so it needs no local store and runs on CI.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.rebuild import rebuild  # noqa: E402

QML = "learning-qml-no-reliable-tabular-accuracy-gain"


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    db = tmp_path_factory.mktemp("learn") / "evidence.db"
    rebuild(ROOT / "export", db, check_local_paths=False).close()
    c = connect(db)
    yield c
    c.close()


def _mod():
    spec = importlib.util.spec_from_file_location("learnings", ROOT / "scripts" / "learnings.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_learnings_are_found_by_provenance_not_by_absence_of_a_paper(conn):
    """hsbc-b1-variable-count-wrong-78 is yielded by no paper and is the
    target of a `contradicts` edge, yet is NOT a synthesis; the first
    definition caught it."""
    ids = _mod().learning_ids(conn)
    assert QML in ids
    assert "hsbc-b1-variable-count-wrong-78" not in ids
    assert all(i.startswith("learning-") for i in ids)


def test_balance_counts_assertions_not_sources_regression(conn):
    """cvqboost-vs-xgboost-auc-under-balancing is yielded by two papers; it
    is ONE piece of evidence. Proven to fail by injection: the first
    version joined paper_yields per row and reported moderate: 2."""
    item = _mod().learning(conn, QML)
    ids = [e["id"] for e in item["evidence"]]
    assert len(ids) == len(set(ids)), "an evidence assertion appears once, whatever its number of sources"
    cvq = next(e for e in item["evidence"] if e["id"] == "cvqboost-vs-xgboost-auc-under-balancing")
    assert "emami-2025" in cvq["sources"] and "qci-2024-profiling" in cvq["sources"]
    assert item["balance"]["supports"].get("moderate") == 1


def test_every_learning_names_why_and_has_evidence(conn):
    m = _mod()
    for lid in m.learning_ids(conn):
        item = m.learning(conn, lid)
        assert item["certainty"] and item["certainty_reasons"], lid
        assert item["evidence"], f"{lid} has no supporting or contradicting assertion"


def test_learnings_does_not_create_a_missing_store(tmp_path, monkeypatch):
    """sqlite3.connect creates the file; an empty evidence.db then blocks
    rebuild_store_from_export.py --apply (fresh-eyes review, 2026-09-24)."""
    m = _mod()
    missing = tmp_path / "evidence.db"
    monkeypatch.setattr(m, "DB_PATH", missing)
    assert m.main([]) == 1
    assert not missing.exists()
