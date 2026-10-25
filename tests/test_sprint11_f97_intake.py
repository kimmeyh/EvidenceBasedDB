"""Sprint 11 Task F (F97): new papers and the team lead's list entered before
reading, by `scripts/sprint11_f97_intake.py`. Every local copy is in its
record's `access`, each repository named as a paper's code is linked
`code-of` to it with evidence, NVIDIA/auto-ontology-eval is linked to the
blog record on the team lead's decision (Manual Validation Q1 = 2; no source
names it as the article's code, and its evidence says so), and a second
apply writes nothing."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f97", ROOT / "scripts" / "sprint11_f97_intake.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_eval_link_names_the_team_leads_decision():
    """Every repository is linked with evidence. The one link no source
    supports (auto-ontology-eval, team lead 2026-10-22, Q1 = 2) says in its
    evidence that it rests on the team lead's decision, and no other link
    borrows that evidence. Proven to fail by injection, 2026-10-22: with
    cace-bench's link given EVAL_DECISION as its evidence, this test named
    both repositories."""
    f97 = _script()
    assert all(paper and evidence and evidence.strip() for _, paper, evidence in f97.REPOS)
    decided = [o for o, _, evidence in f97.REPOS if evidence == f97.EVAL_DECISION]
    assert decided == ["NVIDIA/auto-ontology-eval"]
    assert "rests on the team lead's decision" in f97.EVAL_DECISION
    assert "No source names it" in f97.EVAL_DECISION


def test_a_held_record_is_matched_by_whole_access_token():
    """`existing` skips the network for records already held (F100), so a
    wrong match would skip a new record. Proven to fail by injection,
    2026-10-23: with the whole-token check made a substring check,
    auto-ontology found the -eval record. Restored."""
    import sqlite3
    f97 = _script()
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE paper_fields (record_id TEXT, access TEXT)")
    conn.execute("INSERT INTO paper_fields VALUES ('eval', 'https://github.com/NVIDIA/auto-ontology-eval')")
    conn.execute("INSERT INTO paper_fields VALUES ('p', 'arXiv:2401.00001 | D:\\Papers\\a.pdf')")
    assert f97.existing(conn, "https://github.com/NVIDIA/auto-ontology") is None
    assert f97.existing(conn, "https://github.com/nvidia/AUTO-ontology-eval/") == "eval"
    assert f97.existing(conn, "arXiv:2401.00001") == "p"
    assert f97.existing(conn, "arXiv:2401.0000") is None


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    """Proven to fail by injection, 2026-10-22: with Hoppner 2020's file
    pointed at the Elor 2022 record in LOCAL_COPIES, this test named the
    copy line."""
    from store import connect
    f97 = _script()
    conn = connect(live_copy)
    try:
        log = f97.apply_changes(conn, apply=True)
    finally:
        conn.close()
    changed = [x for x in log if not x.startswith(("exists", "before:", "after:"))]
    assert not changed, changed
    assert sum(1 for x in log if x.startswith("exists link")) == 7
