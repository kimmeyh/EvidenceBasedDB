"""F87 (Sprint 10 Task J): the discovery streams drop the off-topic kinds the
team lead excluded at Sprint 9 Manual Validation, before ranking, and lose
no record the team lead accepted. Measured on Sprint 9's saved pool, so
before and after are the same candidates."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("stream, topic, title", [
    ("ml", "Computational Physics and Python Applications", "SciPy 1.0"),
    ("ml", "Data Analysis with R", "Welcome to the Tidyverse"),
    ("ml", "Metaheuristic Optimization Algorithms Research", "Grey Wolf Optimizer"),
    ("qml", "Quantum and electron transport phenomena", "Quantum logic with spin qubits"),
    ("qml", "Brain Tumor Detection and Classification", "Brain tumor detection"),
    ("tensor", "Machine Learning in Materials Science", "The design space of E(3)-equivariant"),
    ("tensor", "Quantum many-body systems", "Codebase release 0.3 for ITensor"),
])
def test_an_off_topic_kind_is_dropped(stream, topic, title):
    """Proven to fail by injection, 2026-10-18: with off_topic() returning
    None, every case went red."""
    dc = _load("dc", "discover_candidates.py")
    assert dc.off_topic({"stream": stream, "topic": topic, "title": title})


@pytest.mark.parametrize("stream, topic, title", [
    ("ml", "Advanced Neural Network Applications", "Attention Is All You Need"),
    ("qml", "Quantum Computing Algorithms and Architectures", "Barren plateaus in variational quantum computing"),
    ("tensor", "Quantum many-body systems", "The ITensor Software Library for Tensor Network Calculations"),
    ("tensor", "Black Holes and Theoretical Physics", "Entanglement of purification through holographic duality"),
    ("fraud", "Imbalanced Data Classification Techniques", "Credit Card Fraud Detection"),
    # A topic dropped in one stream is kept in another
    ("qml", "Machine Learning and Algorithms", "A quantum learning paper"),
    # Task J review: ML libraries the team lead never excluded, and a generic
    # topic a tensor-network learning paper could carry
    ("ml", "Computational Physics and Python Applications", "Scikit-learn: Machine Learning in Python"),
    ("ml", "Computational Physics and Python Applications", "Automatic differentiation in PyTorch"),
    ("tensor", "Machine Learning and Algorithms", "Learning with Pseudo-Ensembles"),
])
def test_an_accepted_kind_is_kept(stream, topic, title):
    dc = _load("dc", "discover_candidates.py")
    assert dc.off_topic({"stream": stream, "topic": topic, "title": title}) is None


@pytest.mark.live_store  # reads Sprint 9's pool, outside the repository
def test_on_sprint_9s_pool_no_accepted_record_is_lost_and_three_excluded_remain():
    """Before: 13 excluded records in the four top-25 lists. After: 3 (the
    single-photon platform paper and the black-hole paper share a topic with
    accepted ones; the pseudo-ensembles paper carries a generic topic the
    review kept off the list). Proven to fail by injection, 2026-10-18: with
    "Black Holes and Theoretical Physics" added to the tensor topics, the
    accepted holography paper was lost and the first assertion went red."""
    check = _load("f87check", "sprint10_f87_filter_check.py")
    m = check.measure(json.loads(check.POOL.read_text(encoding="utf-8")))
    assert not [t for r in m.values() for t in r["accepted_lost"]]
    assert sum(r["excluded_before"] for r in m.values()) == 13
    assert sorted(t for r in m.values() for t in r["excluded_still_in_top"]) == [
        "A versatile single-photon-based quantum computing platform", "Complexity, action, and black holes",
        "Learning with Pseudo-Ensembles"]


def test_main_drops_an_off_topic_work_before_ranking_and_lists_it(tmp_path, monkeypatch):
    """Task J review: no test ran main with an off-topic work. One kept and
    one off-topic work per stream: the off-topic one is never asked of
    Semantic Scholar, is counted as dropped, is listed in the review's
    dropped section and is kept in the JSON. Proven to fail by injection,
    2026-10-18: with the drop removed from main's candidate list, 6
    Semantic Scholar requests went out instead of 4 and this test went
    red."""
    import importlib.util as iu
    spec = iu.spec_from_file_location("dct", ROOT / "tests" / "test_discover_candidates.py")
    tdc = iu.module_from_spec(spec)
    spec.loader.exec_module(tdc)
    dc = _load("dc", "discover_candidates.py")
    off = dict(tdc.WORK, id="https://openalex.org/W2", doi="https://doi.org/10.1/scipy",
               title="SciPy 1.0: fundamental algorithms", primary_topic={
                   "display_name": "Computational Physics and Python Applications"})
    monkeypatch.setattr(dc, "fetch_stream", lambda stream, per, key: [tdc.WORK] + ([off] if stream == "ml" else []))
    monkeypatch.setattr(dc, "store_keys", lambda conn: (set(), set(), set()))
    monkeypatch.setattr(dc, "openalex_key", lambda: None)
    monkeypatch.setattr(dc.sqlite3, "connect", lambda *a, **k: type("C", (), {"close": lambda self: None})())
    urls = []

    def s2(url):
        urls.append(url)
        return json.dumps({"citationCount": 9, "year": 2024, "title": "Explaining Anomalies"}).encode()
    assert dc.main(["--out", str(tmp_path)], s2_fetch=s2, sleep=lambda s: None) == 0
    assert len(urls) == len(dc.STREAMS)  # the off-topic work was never checked
    review = next(tmp_path.glob("f62_review_*.md")).read_text(encoding="utf-8")
    assert "### ml: dropped as off-topic before ranking (F87)" in review and "SciPy 1.0" in review
    saved = json.loads(next(tmp_path.glob("f62_review_*.json")).read_text(encoding="utf-8"))
    assert [c["dropped"] for c in saved if c["title"].startswith("SciPy")] == [
        "topic: Computational Physics and Python Applications"]
