"""Sprint 11 Task F (F97): new papers and the team lead's list entered before
reading, by `scripts/sprint11_f97_intake.py`. Every local copy is in its
record's `access`, each repository named as a paper's code is linked
`code-of` to it with evidence, NVIDIA/auto-ontology-eval is entered and linked
to nothing (no source names it as a paper's code), and a second apply
writes nothing."""
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


def test_only_the_eval_repository_is_unlinked():
    """A change from the plan, disclosed 2026-10-22: a link needs a source
    that names the repository as the paper's code."""
    f97 = _script()
    unlinked = [o for o, paper, evidence in f97.REPOS if paper is None]
    assert unlinked == ["NVIDIA/auto-ontology-eval"]
    assert all(evidence and evidence.strip() for _, paper, evidence in f97.REPOS if paper)


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
    changed = [x for x in log if not x.startswith(("exists", "no link", "before:", "after:"))]
    assert not changed, changed
    assert sum(1 for x in log if x.startswith("exists link")) == 6
    assert sum(1 for x in log if x.startswith("no link")) == 1
