"""F147 (Sprint 18 Task B): a stored assertion is synced only through
`store.ingest.sync_decided_assertion`, which refuses a field no review
decided before anything of that assertion is written.

Before F147 the live applier wrote such a field and listed it afterwards as
"undecided"; the defect reached the store 4 times (4d969d9, ed5ab01,
aabdd49, d740d72). The one-time appliers of Sprints 9 to 17 are frozen by
`store.write_path.SYNC_FROZEN` (team lead q2 = a, 2026-11-19): a new script
that names `sync_verified_assertion` is refused by the scan and, before the
backup, by `backup_before_write`.

Proven to fail by injection, 2026-11-21, each restored (a grep for INJECTED
in store/ finds nothing):
- the refusal removed from `sync_decided_assertion` (`undecided = []  #
  INJECTED`): test_an_undecided_field_is_refused_and_nothing_is_written went
  red (the value was written);
- the savepoint's ROLLBACK TO removed (`pass  # INJECTED`): the same test
  went red (the refused value stayed in the row);
- the `BEGIN` before the savepoint removed (`pass  # INJECTED`):
  test_a_sync_from_no_open_transaction_still_leaves_the_commit_to_the_caller
  went red (RELEASE of the outermost savepoint committed on its own);
- the SYNC_FROZEN check removed from `script_problems` (`if False and
  ...  # INJECTED`): test_a_new_script_that_syncs_directly_is_refused went
  red.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import create_store  # noqa: E402
from store.ingest import (AssertionRecord, UndecidedField, insert_verified_assertion,  # noqa: E402
                          sync_decided_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402
from store.write_path import SYNC_FROZEN, script_problems  # noqa: E402

SOURCE = plain("We show that the problem is intractable for R above two. The budget is fixed.")
QUOTE = '"the problem is intractable for R" (p.3)'


def _assertion(value: str = "a claim", updated: str = "2026-11-21") -> AssertionRecord:
    return AssertionRecord(id="a1", value=value, provenance="p1, p.3", evidence_tag="N/A", context="qml",
                           citation_context=QUOTE, derivation="extracted", updated=updated, updated_reason="test")


@pytest.fixture
def conn(tmp_path):
    path = tmp_path / "evidence.db"
    c = create_store(path)
    a = _assertion(updated="2026-11-20")
    insert_verified_assertion(c, a, require_verbatim(a.id, a.citation_context, SOURCE, value=a.value))
    c.commit()
    yield c
    c.close()


def _sync(conn, value: str, decided: set[str]) -> list[str]:
    a = _assertion(value)
    return sync_decided_assertion(conn, a, require_verbatim(a.id, QUOTE, SOURCE, value=value), "note", "2026-11-21",
                                  decided)


def _value(conn) -> str:
    return conn.execute("SELECT value FROM records WHERE id = 'a1'").fetchone()[0]


def test_a_decided_field_is_written(conn):
    assert _sync(conn, "a narrower claim", {"value"}) == ["value"]
    assert _value(conn) == "a narrower claim"


def test_an_undecided_field_is_refused_and_nothing_is_written(conn):
    with pytest.raises(UndecidedField, match="no review decided value"):
        _sync(conn, "a narrower claim", {"citation_context"})
    assert _value(conn) == "a claim"
    reason = conn.execute("SELECT updated_reason FROM records WHERE id = 'a1'").fetchone()[0]
    assert "note" not in reason  # the sync's own note was rolled back with the value


def test_a_refusal_leaves_the_callers_earlier_work_to_the_caller(conn):
    """The savepoint must not commit or drop the caller's own writes: a refused sync leaves them in the open
    transaction, and the caller's rollback removes them."""
    conn.execute("UPDATE records SET updated_reason = updated_reason || ' | caller' WHERE id = 'a1'")
    with pytest.raises(UndecidedField):
        _sync(conn, "a narrower claim", set())
    assert conn.in_transaction
    assert conn.execute("SELECT updated_reason FROM records WHERE id = 'a1'").fetchone()[0].endswith("caller")
    conn.rollback()
    assert not conn.execute("SELECT updated_reason FROM records WHERE id = 'a1'").fetchone()[0].endswith("caller")


def test_a_sync_from_no_open_transaction_still_leaves_the_commit_to_the_caller(conn):
    assert not conn.in_transaction
    _sync(conn, "a narrower claim", {"value"})
    assert conn.in_transaction  # RELEASE did not commit on its own
    conn.rollback()
    assert _value(conn) == "a claim"


def test_a_new_script_that_syncs_directly_is_refused():
    text = "from store.ingest import sync_verified_assertion\nsync_verified_assertion(conn, a, v, n, t)\n"
    assert any("F147" in p for p in script_problems(text, "sprint18_new_applier.py"))
    assert not any("F147" in p for p in script_problems(text, "sprint17_q29_q31_grades.py"))


def test_the_live_applier_is_not_frozen_and_syncs_only_through_the_decided_path():
    assert "full_read_apply.py" not in SYNC_FROZEN
    text = (ROOT / "scripts" / "full_read_apply.py").read_text(encoding="utf-8")
    assert script_problems(text, "full_read_apply.py") == []
    assert "sync_decided_assertion" in text


def _code_names(path: Path) -> set[str]:
    """The names a script's code uses (not its comments or strings)."""
    import ast
    names = set()
    for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.alias):
            names.add(n.name.rsplit(".", 1)[-1])
    return names


def test_each_frozen_script_exists_and_still_calls_the_old_sync():
    """A frozen name whose script does not call sync_verified_assertion would let a later edit add one unseen."""
    assert {n for n in SYNC_FROZEN if not (ROOT / "scripts" / n).is_file()} == set()
    assert {n for n in SYNC_FROZEN if "sync_verified_assertion" not in _code_names(ROOT / "scripts" / n)} == set()


def test_every_script_that_calls_the_old_sync_is_frozen_or_legacy():
    """The closed list matches the code: the 16 frozen, the 6 LEGACY scripts of Sprints 9 and 10 (sync_assertion),
    and no other script, the live applier included."""
    from store.write_path import LEGACY
    callers = {p.name for p in (ROOT / "scripts").glob("*.py")
               if _code_names(p) & {"sync_assertion", "sync_verified_assertion"}}
    assert callers - SYNC_FROZEN - LEGACY == set()
    assert len(SYNC_FROZEN) == 16 and len(callers & LEGACY) == 6
