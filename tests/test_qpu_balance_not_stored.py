"""Team lead, 2026-10-13: a QPU-seconds balance is not stored. It changes
with every run and every grant, and the account answers it (CLAUDE.md:
determinate facts are computed, never stored). The one record that held a
balance was removed by scripts/sprint8_remove_qpu_balance.py."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REMOVED = "hsbc-dirac3-allocation-1681-after-sizing-probes"


@pytest.mark.live_store
def test_the_removed_balance_is_not_in_the_store(live_conn):
    """Proven to fail, 2026-10-13: run before the removal's --apply, this
    test named the record."""
    assert live_conn.execute("SELECT 1 FROM records WHERE id = ?", (REMOVED,)).fetchone() is None, \
        f"{REMOVED} is back in the store"


def test_no_script_would_re_add_it():
    """Proven to fail by injection, 2026-10-13: with the assertion restored
    to scripts/sprint6_task_g_cyc_and_facts.py, this test named that file."""
    pattern = re.compile(rf'id="{re.escape(REMOVED)}"')
    offenders = [p.name for p in (ROOT / "scripts").glob("*.py") if pattern.search(p.read_text(encoding="utf-8"))]
    assert offenders == [], f"a script would re-add {REMOVED}: {offenders}"
