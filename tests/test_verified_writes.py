"""Sprint 10 retrospective I1 and I2 (2026-10-21): the quote check moves
into the write path, and the coordinator's own edits name the source
passage they rest on.

I2: Tasks F, G and H (F84, F85, F83) wrote to the store before checking
their quotes, against intake rule 26, because each script had to remember
to call `require_verbatim`. Now `require_verbatim` returns a `Verified`,
and `insert_verified_assertion` / `sync_verified_assertion` refuse a write
without the one that matches the record. Scripts from Sprint 11 on use
only those.

I1: four of the coordinator's own reads were wrong in Sprint 10 (F84, F85,
F89 twice) and only reviews caught them. `require_edit_basis` refuses an
edit with no named passage, a passage not verbatim in the source, or a
replaced value stating a number or math sign no passage holds."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import create_store  # noqa: E402
from store.ingest import AssertionRecord, insert_verified_assertion, sync_verified_assertion  # noqa: E402
from store.quotes import Verified, plain, require_edit_basis, require_verbatim  # noqa: E402

SOURCE = plain("We show that the problem is intractable for R ≥ √2. The budget is B = 192 circuit evaluations. "
                "Errors are around 10−2 to 10−1.")


def _assertion(context: str = '"the problem is intractable for R" (p.3)') -> AssertionRecord:
    return AssertionRecord(id="a1", value="a claim", provenance="p1, p.3", evidence_tag="N/A", context="qml",
                           citation_context=context, derivation="extracted", updated="2026-10-21",
                           updated_reason="test")


@pytest.fixture
def conn(tmp_path):
    c = create_store(tmp_path / "evidence.db")
    yield c
    c.close()


# ------------------------------------------------------------------ I2

def test_a_checked_assertion_is_written(conn):
    a = _assertion()
    insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, SOURCE))
    assert conn.execute("SELECT 1 FROM records WHERE id = 'a1'").fetchone()


@pytest.mark.parametrize("verified", [
    None,
    Verified("a2", '"the problem is intractable for R" (p.3)'),  # another record's check
    Verified("a1", '"the problem is intractable" (p.3)'),  # the quotes changed after the check
])
def test_an_unchecked_assertion_is_refused_before_anything_is_written(conn, verified):
    """Proven to fail by injection, 2026-10-21: with _require_verified's
    test inverted to always pass, all three cases wrote the record and went
    red."""
    with pytest.raises(ValueError, match="not checked against its source"):
        insert_verified_assertion(conn, _assertion(), verified)
    assert not conn.execute("SELECT 1 FROM records WHERE id = 'a1'").fetchone()


def test_a_sync_is_refused_without_the_check(conn):
    a = _assertion()
    insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, SOURCE))
    with pytest.raises(ValueError, match="not checked against its source"):
        sync_verified_assertion(conn, _assertion('"the problem is intractable" (p.3)'), None, "note", "2026-10-21")


# Each problem a new script can have, by the rule it breaks. Names, not
# calls, so an aliased import (`import insert_assertion as ins`) or an
# attribute reference is caught too (fresh-eyes review, 2026-10-21);
# `insert_verified_assertion` does not match. Comments are not code.
_DIRECT_WRITE = re.compile(r"\b(insert|sync)_assertion\b")
_TOKEN_NAME = re.compile(r"\bVerified\b")
_WRITES = re.compile(r"\b(insert|sync)_(verified_)?assertion\b")
_EDIT_TABLE = re.compile(r"(?m)^(VALUE|QUOTE|CONTEXT)_[A-Z_]+\s*[:=]")

# The scripts written before this rule (Sprint 10 and earlier). They have
# run, and stay as they are; every other script in scripts/ is held to it,
# whatever its name.
LEGACY = {
    "ingest_hsbc_b1_variable_count.py", "ingest_lenat_marcus.py", "sprint4_task_h_extraction.py",
    "sprint5_task_i_pilot.py", "sprint6_mv_dirac3_fidelity.py", "sprint6_task_g_cyc_and_facts.py",
    "sprint7_f44_cycorp_papers.py", "sprint7_f45_dirac3_reading.py", "sprint8_f65_dirac3s_reading.py",
    "sprint8_f71_qci_dirac3s_reading.py", "sprint9_f46_pending_facts.py", "sprint9_f78_ceiling_reading.py",
    "sprint9_f79_phase2_b4_b5_inbound.py", "sprint9_f80_reading.py", "sprint10_f83_optimization_bounds.py",
    "sprint10_f84_dirac1.py", "sprint10_f85_dirac3s_verify.py", "sprint10_f89_reading.py",
}


def script_problems(text: str) -> list[str]:
    code = re.sub(r"#.*", "", text)
    out = []
    if _DIRECT_WRITE.search(code):
        out.append("writes an assertion without the quote check (use insert_verified_assertion)")
    if _TOKEN_NAME.search(code):
        out.append("names Verified (only require_verbatim makes one; pass on what it returns)")
    if _WRITES.search(code) and _EDIT_TABLE.search(code) and "require_edit_basis(" not in code:
        out.append("edits readers' values, quotes or contexts without require_edit_basis")
    return out


def test_new_scripts_write_only_through_the_checked_path():
    problems = {p.name: script_problems(p.read_text(encoding="utf-8"))
                for p in sorted((ROOT / "scripts").glob("*.py")) if p.name not in LEGACY}
    assert not {k: v for k, v in problems.items() if v}


@pytest.mark.parametrize("planted, expected", [
    ("insert_assertion(conn, a, yielded_by=rid)", "without the quote check"),
    ("changed = sync_assertion(conn, a, note, TODAY)", "without the quote check"),
    ("from store.ingest import insert_assertion as ins\nins(conn, a)", "without the quote check"),
    ("write = ingest.sync_assertion", "without the quote check"),
    ("v = Verified(a.id, a.citation_context)", "names Verified"),
    ("from store.quotes import Verified as V", "names Verified"),
    ("insert_verified_assertion(conn, a, v)\nVALUE_REPLACE = {'x': 'a new value'}\n"
     "# require_edit_basis( is only mentioned here", "without require_edit_basis"),
])
def test_the_script_rule_names_each_planted_problem(planted, expected):
    """Proven to fail by injection, 2026-10-21: with script_problems()
    returning [] every case went red; and a planted
    scripts/sprint11_injected_probe.py that called insert_assertion, and
    later a planted scripts/ingest_injected_probe.py that imported it under
    an alias, each turned the scan of scripts/ red until removed."""
    assert any(expected in p for p in script_problems(planted))
    clean = ("insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, text))\n"
             "VALUE_REPLACE = {}\nrequire_edit_basis(aid, value, basis, text)\n"
             "CONTEXT_BY_RANK = {}  # an entry script's table, with no assertion written\n")
    assert script_problems(clean) == []
    assert script_problems("CONTEXT_BY_RANK = {}\ninsert_paper(conn, paper)\n") == []


# ------------------------------------------------------------------ I1

def test_an_edit_resting_on_its_passage_passes():
    require_edit_basis("e1", "The budget is 192 circuit evaluations.", ["B = 192 circuit evaluations"], SOURCE)


@pytest.mark.parametrize("value, basis, match", [
    ("anything", [], "names no source passage"),
    ("anything", ["a passage the source never had"], "not verbatim in its source"),
    # Sprint 10's F89: the text layer drops the root sign, so the passage
    # stops before the threshold and a value stating it is refused
    ("Intractable for R of at least the square root of 2.", ["the problem is intractable for R"], "states 2"),
    ("Intractable for R ≥ √2.", ["the problem is intractable for R"], "√"),
    ("The budget is 190 circuit evaluations.", ["B = 192 circuit evaluations"], "states 190"),
    # Fresh-eyes review, 2026-10-21: a value that is only a number, a
    # flipped exponent, a flipped inequality
    ("190", ["B = 192 circuit evaluations"], "states 190"),
    ("errors around 10^2", ["around 10−2 to 10−1"], "states 2"),
    ("intractable for R > 1", ["the problem is intractable for R"], "states .*>"),
])
def test_an_edit_without_its_basis_is_refused(value, basis, match):
    """Proven to fail by injection, 2026-10-21: with the number and sign
    comparison removed from require_edit_basis, every case from the root
    sign on went red."""
    with pytest.raises(ValueError, match=match):
        require_edit_basis("e1", value, basis, SOURCE)


def test_a_figure_read_from_the_page_passes_only_when_listed():
    value = "Intractable for R of at least the square root of 2; the root sign is read from the page."
    with pytest.raises(ValueError, match="states 2"):
        require_edit_basis("e1", value, ["the problem is intractable for R"], SOURCE)
    require_edit_basis("e1", value, ["the problem is intractable for R"], SOURCE, read_from_page=("2",))


def test_a_dropped_quote_or_moved_context_needs_a_passage_but_no_value():
    require_edit_basis("e1", None, ["B = 192 circuit evaluations"], SOURCE)
    with pytest.raises(ValueError, match="names no source passage"):
        require_edit_basis("e1", None, [], SOURCE)


@pytest.mark.live_store  # reads F89's PDFs
def test_on_f89s_own_edits_the_rule_finds_the_root_sign_and_four_unquoted_figures():
    """Measured 2026-10-21 on Sprint 10's F89 VALUE_REPLACE, each value's
    own quotes as its basis: the root-2 value is flagged (its "2"), and four
    more state figures their quotes do not hold (Durr 2004; F2's 12 qubits;
    the 192-evaluation budget; Grossi's Tables 8 and 9). Every one of those
    figures is in its source, so no stored value is wrong; under I1 each
    would have named one more passage."""
    from store.quotes import QUOTE, unsupported_by_basis
    spec = importlib.util.spec_from_file_location("f89", ROOT / "scripts" / "sprint10_f89_reading.py")
    f89 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f89)
    stored = {a.id: a for _, a, _, _ in f89.assertions()}
    flagged = {aid for aid, value in f89.VALUE_REPLACE.items()
               if unsupported_by_basis(value, QUOTE.findall(stored[aid].citation_context))}
    assert flagged == {"quadratic-ode-lower-bound-strong-nonlinearity", "aimeur-mst-quantum-optimal-n32",
                       "zuchongzhi-vqe-f2-above-chemical-accuracy", "qaoa-rl-kde-gap-reduction-vs-nelder-mead",
                       "fraud-mixed-quantum-classical-ensemble-accuracy"}
