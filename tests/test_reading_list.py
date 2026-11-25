"""Sprint 19 Task D (F114 with F57 folded in; team lead q5 = b, q6 = a): one reading list, computed.

The test fails if a paper appears twice (in two live ledger groups, or twice in the list) or if a paper to read in
full is missing from the list. Proven red by injection, 2026-11-25, with three injections at once: `problems`
returning [], `rows` with its `readable` filter cut (a paper read in full, a repository and a book listed), and
`to_add` with its held check cut (a held paper added again). All 5 tests failed. Restored, 5 passed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reading_list as rl  # noqa: E402
import sprint19_f114_ledger as s19  # noqa: E402


def _p(reads=(), access="arXiv:2101.00001", tier="seen", contexts=("qml",), disposition="", title="A paper"):
    return {"access": access, "tier": tier, "title": title, "disposition": disposition, "reads": set(reads),
            "groups_read": set(), "contexts": list(contexts)}


def _ledger(groups: dict[str, list[str]]) -> dict:
    return {"groups": {g: {"records": [{"record_id": r, "file": ""} for r in rids]} for g, rids in groups.items()}}


def test_problems_names_each_kind():
    P = {"a": _p(), "b": _p(), "c": _p()}
    L = _ledger({"g001": ["a"], "g002": ["a", "b"]})
    listed = [{"record_id": "a"}, {"record_id": "a"}, {"record_id": "b"}]
    got = rl.problems(L, P, listed)
    assert any("a: in two ledger groups (g001, g002)" == x for x in got), got
    assert "a: twice in the list" in got
    assert "c: a paper to read in full, missing from the list" in got
    assert rl.problems(_ledger({"g001": ["a"], "g002": ["b"], "g003": ["c"]}), P,
                       [{"record_id": r} for r in "abc"]) == []


def test_rows_order_and_filter():
    """q5 = b: `first` in its order, then context (hsbc-2026, Dirac, qml, ...), then most cited, no count last."""
    P = {"done": _p(reads=["full"]), "repo": _p(access="https://github.com/x/y"),
         "hsbc": _p(contexts=["hsbc-2026"]), "dirac": _p(contexts=["platform:dirac-3"]),
         "qml-many": _p(), "qml-few": _p(), "qml-none": _p(), "ml": _p(contexts=["ml"]), "named": _p(contexts=["ml"]),
         "book": _p()}
    rl.NOT_TO_READ.setdefault("book", "a book (test)")
    try:
        L = _ledger({"g1": list(P)})
        ranking = {"first": ["named"], "counts": {"qml-many": {"cited_by_count": 900}, "qml-few": {"cited_by_count": 3},
                                                   "qml-none": {"cited_by_count": None}, "ml": {"cited_by_count": 10**6}}}
        order = [x["record_id"] for x in rl.rows(L, P, ranking)]
    finally:
        rl.NOT_TO_READ.pop("book")
    assert order == ["named", "hsbc", "dirac", "qml-many", "qml-few", "qml-none", "ml"], order


def test_to_add_takes_only_readable_papers_no_group_holds():
    P = {"held": _p(), "new": _p(), "part": _p(reads=["partial"], tier="read"), "full": _p(reads=["full"]),
         "repo": _p(access="https://github.com/a/b"), "gone": _p(disposition="Withdrawn by the authors"),
         "noaccess": _p(access="")}
    got = rl.to_add(P, {"held"})
    assert got == {"never read": ["new"], "read in part": ["part"]}, got


def test_the_ledger_script_adds_one_paper_per_group_and_a_second_run_adds_nothing():
    P = {"a": _p(), "b": _p(reads=["partial"], tier="read")}
    L = _ledger({"g010": ["x"]})
    added = s19.add(L, P)
    assert [(g, r) for g, r, _ in added] == [("g011", "a"), ("g012", "b")]
    assert all(len(L["groups"][g]["records"]) == 1 for g, _, _ in added)
    assert s19.add(L, P) == []


@pytest.mark.live_store
def test_the_live_list_holds_every_paper_to_read_once():
    L = json.loads(rl.LEDGER.read_text(encoding="utf-8"))
    with rl.read_only() as conn:
        P = rl.papers(conn)
    listed = rl.rows(L, P, rl.load_ranking())
    assert rl.problems(L, P, listed) == []
    assert all(not rl.readable(x["record_id"], P[x["record_id"]]) for x in listed)
    ranking = rl.load_ranking()
    assert set(ranking["counts"]) >= {x["record_id"] for x in listed} - set(ranking.get("first", [])), \
        "a listed paper has no entry in the ranking manifest: run `reading_list.py rank --write`"
