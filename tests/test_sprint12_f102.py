"""F102 (Sprint 12 Task C): Phase 2's Sprint 28 results, entered by the
inbound path (INTAKE_WORKFLOW.md section 43). The documents are read from
the sibling repository at a named commit, which CI does not have, so every
test here is live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import QUOTE  # noqa: E402

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f102", ROOT / "scripts" / "sprint12_f102_phase2_sprint28.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_document_is_the_blob_read():
    f102 = _script()
    for key, doc in f102.DOCS.items():
        assert hashlib.sha256(f102.source_bytes(key)).hexdigest() == doc[2], key


def test_every_quote_and_figure_is_in_its_document():
    """`verify_all` runs require_verbatim with each value. Proven to fail by
    injection, 2026-10-23: with "0.027" changed to "0.028" in the F130
    restatement's value, it named f151-cvqboost-proxy-below-stable-hgb-on-ulb.
    Restored."""
    checked = _script().verify_all()
    assert len(checked) == 12
    # The number written (second apply, 2026-10-23): a dropped quote is a change to explain, not drift.
    assert sum(len(QUOTE.findall(a.citation_context)) for _, a, _ in checked) == 99


def test_the_store_holds_what_the_script_writes(live_conn):
    """Proven to fail by injection, 2026-10-23: run against the backup
    taken before the apply, it named f151; run against the backup taken
    before the second apply, it named f111 (not yet entered)."""
    f102 = _script()
    for key in f102.DOCS:
        tier = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (f102.src_id(key),)).fetchone()
        assert tier is not None and tuple(tier) == ("read",), key
    for key, a in f102.ASSERTIONS:
        row = live_conn.execute("SELECT r.value, r.evidence_tag, f.citation_context, r.certainty, "
                                "r.certainty_reasons FROM records r JOIN assertion_fields f ON f.record_id = r.id "
                                "WHERE r.id = ?", (a.id,)).fetchone()
        assert row is not None and tuple(row) == (a.value, "SIM", a.citation_context, a.certainty,
                                                  a.certainty_reasons), a.id
        contexts = {c for (c,) in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                                     (a.id,))}
        assert contexts == {a.context}, a.id
        assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                 (f102.src_id(key), a.id)).fetchone(), a.id
