"""F45 (Sprint 7 Task G): every Dirac-3 assertion quotes a source that was
read directly and promoted, and the quote is in that source's local copy."""
from __future__ import annotations

import html
import importlib.util
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.live_store

# Read from the nature.com article page, of which no copy is kept (the
# script's docstring); checked by hand on 2026-10-08, so not re-checked here.
NO_LOCAL_COPY = {
    "Dirac-3 produces best-observed solutions (over 100 samples per instance) within 0.16–2.47% of the optimal "
    "energies.",
    "B. E., W. D., D. H., J. R. and L. N. hold shares or options in Quantum Computing Inc.",
}
_QUOTE = re.compile(r'(?:^|; )"(.+?)" \(')


def _script():
    spec = importlib.util.spec_from_file_location("f45", ROOT / "scripts" / "sprint7_f45_dirac3_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _plain(text: str) -> str:
    """The typographic forms the anchors name made plain, page-number lines
    dropped (a quote may cross a page break), whitespace collapsed."""
    for typographic, plain in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                               ("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬀ", "ff"), ("ﬃ", "ffi"), ("ﬄ", "ffl"),
                               ("​", "")):
        text = text.replace(typographic, plain)
    text = re.sub(r"(?m)^\s*\d+\s*$", " ", text)
    return re.sub(r"\s+", " ", text)


@lru_cache(maxsize=None)
def _text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        modes = (["pdftotext", "-enc", "UTF-8", path, "-"], ["pdftotext", "-enc", "UTF-8", "-layout", path, "-"])
        return " || ".join(_plain(subprocess.run(m, capture_output=True, check=True).stdout.decode("utf-8", "replace"))
                           for m in modes)
    page = Path(path).read_text(encoding="utf-8", errors="replace")
    page = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    return _plain(html.unescape(re.sub(r"<[^>]+>", " ", page)))


def test_every_quote_is_in_a_yielding_source(live_conn):
    """Proven to fail by injection, 2026-10-08: with the curly quotation
    marks no longer made plain, the User Guide's "qudit," quote (in
    dirac3-variable-coupling-computed-in-fpga) was not found and this test
    named it."""
    f45 = _script()
    checked = 0
    for assertion, yielded_by in f45.ASSERTIONS:
        stored = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                   (assertion.id,)).fetchone()[0]
        quotes = _QUOTE.findall(stored)
        assert quotes, f"{assertion.id}: no quote found"
        texts = [_text(f45.LOCAL[r]) for r in yielded_by if r in f45.LOCAL]
        for q in quotes:
            if q in NO_LOCAL_COPY:
                continue
            assert any(q in t for t in texts), f"{assertion.id}: not verbatim in its sources: {q[:70]}"
            checked += 1
    assert checked >= 20


def test_every_source_is_read_and_yields(live_conn):
    """Proven to fail by injection, 2026-10-08: with the read date in the
    query moved a day, the User Guide was reported as lacking its read row
    and this test went red."""
    f45 = _script()
    for rid, *_ in f45.PROMOTIONS:
        tier = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
        assert tier == "read", rid
        assert live_conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND reader = 'Claude' AND "
                                 "read_on = ?", (rid, f45.TODAY)).fetchone(), f"{rid}: no read row"
        assert live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ?", (rid,)).fetchone(), rid
    for assertion, yielded_by in f45.ASSERTIONS:
        got = {r[0] for r in live_conn.execute("SELECT paper_id FROM paper_yields WHERE assertion_id = ?",
                                               (assertion.id,))}
        assert got == set(yielded_by), assertion.id


def test_absence_scope_coi_and_the_zeno_conflict(live_conn):
    f45 = _script()
    claim_type, scope = live_conn.execute(
        "SELECT claim_type, search_scope FROM assertion_fields WHERE record_id = "
        "'dirac3-no-fault-tolerance-claim-in-qci-sources'").fetchone()
    assert claim_type == "absence" and "545" in scope and f45.TODAY in scope
    for rid in f45.COI:
        coi = live_conn.execute("SELECT coi FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
        assert coi and re.search(r"\s--\s\S", coi), f"{rid}: coi missing or without its anchor"
    assert live_conn.execute("SELECT 1 FROM assertion_relations WHERE from_assertion_id = "
                             "'eqc-zeno-mechanism-claimed-huang-2025' AND to_assertion_id = ? AND "
                             "relation = 'contradicts'", (f45.F205,)).fetchone()
