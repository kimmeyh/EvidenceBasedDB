"""F83 (Sprint 10 Task H): primary sources for per-instance optimization
bounds. Every quote is verbatim in its local copy, every figure a value
states is in its source, and the store holds what the script sets. The
sources sit outside the repository, so these are live_store tests."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _plain, _text  # noqa: E402

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f83", ROOT / "scripts" / "sprint10_f83_optimization_bounds.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _texts(f83) -> dict[str, str]:
    return {f83.BOYD: _plain(_text(str(f83.BOYD_PDF))), f83.GUROBI: _plain(_text(str(f83.GUROBI_HTML)))}


def test_every_quote_is_in_its_source():
    """Proven to fail by injection, 2026-10-18: with "always nonnegative"
    made "always positive" in the weak-duality quote, this test named
    weak-duality-lower-bound-holds-without-convexity."""
    f83 = _script()
    texts, bad, checked = _texts(f83), [], 0
    for a, src in f83.ASSERTIONS:
        for q in _QUOTE.findall(a.citation_context):
            if _plain(q) not in texts[src]:
                bad.append(f"{a.id}: {q[:70]}")
            checked += 1
    assert not bad, bad
    assert checked == 11


def _pages_read(f83) -> str:
    """Book pages 219 to 241 (PDF pages 233 to 255), the sections read. The
    whole book is too large a haystack: a first version of the test below
    searched all 714 pages and passed an injected "60" found elsewhere."""
    import subprocess
    out = subprocess.run(["pdftotext", "-f", "233", "-l", "255", str(f83.BOYD_PDF), "-"], capture_output=True,
                         check=True).stdout.decode("utf-8", "replace")
    return _plain(out)


def _entries_read(f83) -> str:
    """Gurobi's MIPGap and MIPGapAbs entries only (Task H review: across the
    whole parameter page, an injected default such as 1e-5 would pass).
    Each entry runs from "Name #" to the next "Name #"."""
    page = _texts(f83)[f83.GUROBI]
    out = []
    for name in ("MIPGap", "MIPGapAbs"):
        start = page.index(f" {name} # ")
        nxt = re.search(r" [A-Z][A-Za-z]+ # ", page[start + len(name) + 4:])
        out.append(page[start:start + len(name) + 4 + (nxt.start() if nxt else 0)])
    return " ".join(out)


def test_every_figure_in_a_value_is_in_its_source():
    """Proven to fail by injection, 2026-10-18: with "about 50 variables"
    made "about 60 variables", this test named
    two-way-partitioning-dual-sdp-lower-bound (60), once the Boyd text was
    limited to the pages read. A figure in e-notation is one token (1e-4).
    Second injection, after the Task H review: with the default "1e-4"
    made "1e-5" in the Gurobi value, this test named
    gurobi-mipgap-relative-gap-definition."""
    f83 = _script()
    texts, missing = _texts(f83), []
    texts[f83.BOYD] = _pages_read(f83)
    page = _texts(f83)[f83.GUROBI]
    assert "13.0" in page  # the manual's version label, outside the entries
    texts[f83.GUROBI] = _entries_read(f83) + " 13.0"
    for a, src in f83.ASSERTIONS:
        for num in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?:e-?\d+)?", a.value):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\d)", texts[src]):
                missing.append(f"{a.id}: {num}")
    assert not missing, missing


def test_the_store_holds_exactly_what_the_script_sets(live_conn):
    f83 = _script()
    bad = []
    for a, src in f83.ASSERTIONS:
        row = live_conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, r.fidelity, r.evidence_tag, "
            "f.citation_context, f.claim_type, f.derivation "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        ctx = [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        yielded = live_conn.execute("SELECT 1 FROM paper_yields WHERE paper_id = ? AND assertion_id = ?",
                                    (src, a.id)).fetchone()
        if not row or tuple(row) != (a.value, a.certainty, a.certainty_reasons, a.provenance, a.fidelity,
                                     a.evidence_tag, a.citation_context, a.claim_type, a.derivation) \
                or ctx != [a.context] or not yielded:
            bad.append(a.id)
    assert not bad, bad
    for src in (f83.BOYD, f83.GUROBI):
        tier, = live_conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (src,)).fetchone()
        assert tier == "read", src


def test_the_script_refuses_a_quote_not_in_its_source_before_writing():
    """INTAKE_WORKFLOW.md section 26: the check runs before the write. A
    planted quote must stop check_quotes()."""
    import dataclasses
    f83 = _script()
    a, src = f83.ASSERTIONS[0]
    f83.ASSERTIONS[0] = (dataclasses.replace(a, citation_context='"duality is always strong" (p. 1)'), src)
    with pytest.raises(ValueError, match="not verbatim"):
        f83.check_quotes()


def test_a_second_apply_writes_nothing(live_copy):
    from store import connect
    f83 = _script()
    conn = connect(live_copy)
    try:
        log = f83.apply_changes(conn)
    finally:
        conn.close()
    assert all(line.startswith("exists") for line in log), log
