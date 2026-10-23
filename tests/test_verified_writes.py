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
from store.write_path import LEGACY, script_problems  # noqa: E402

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
    insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, SOURCE, value=a.value))
    assert conn.execute("SELECT 1 FROM records WHERE id = 'a1'").fetchone()


@pytest.mark.parametrize("verified", [
    None,
    Verified("a2", '"the problem is intractable for R" (p.3)', "a claim"),  # another record's check
    Verified("a1", '"the problem is intractable" (p.3)', "a claim"),  # the quotes changed after the check
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
    insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, SOURCE, value=a.value))
    with pytest.raises(ValueError, match="not checked against its source"):
        sync_verified_assertion(conn, _assertion('"the problem is intractable" (p.3)'), None, "note", "2026-10-21")


# ------------------------------------------------------------------ Sprint 11 I1a

@pytest.mark.parametrize("value", [None, "another claim"])
def test_a_check_without_the_records_value_licenses_no_write(conn, value):
    """Sprint 11 retrospective I1a: a check run without `value=`, or on
    another value, skipped the figure check, so it cannot license the
    write. Proven to fail by injection, 2026-10-23: with the value
    comparison removed from _require_verified, both cases wrote the record
    and went red."""
    a = _assertion()
    with pytest.raises(ValueError, match="value was not checked"):
        insert_verified_assertion(conn, a, require_verbatim(a.id, a.citation_context, SOURCE, value=value))
    assert not conn.execute("SELECT 1 FROM records WHERE id = 'a1'").fetchone()


@pytest.mark.parametrize("context", [
    '"the problem is intractable for R" (p.3);"B = 192 circuit evaluations" (p.4)',  # F92's missing space
    '"the problem is intractable for R" (p.3), "B = 192 circuit evaluations" (p.4)',  # a comma
    '"We show that the "problem" (that is, R) is intractable" (p.3)',  # Sprint 7's Cyc quote, cut short
])
def test_a_quote_the_pattern_skips_is_refused(context):
    """Proven to fail by injection, 2026-10-23: with the stray_quote_marks
    call removed from require_verbatim, all three passed with their second
    quote, or the rest of the first, never checked."""
    with pytest.raises(ValueError, match="does not parse"):
        require_verbatim("a1", context, SOURCE)


def test_a_quote_mark_inside_a_quote_or_its_anchor_is_not_stray():
    require_verbatim("a1", '"the problem is intractable for R" (p.3; the source\'s "R" kept)', SOURCE)


@pytest.mark.parametrize("value, figures", [
    ("The budget is 190 evaluations.", "190"),
    ("Intractable for R in 3 of 5 cases.", "3, 5"),
])
def test_a_figure_its_own_quotes_do_not_hold_is_refused(value, figures):
    """Proven to fail by injection, 2026-10-23: with the figure check
    removed from require_verbatim, both values passed."""
    with pytest.raises(ValueError, match=f"states {figures},"):
        require_verbatim("a1", '"B = 192 circuit evaluations" (p.4)', SOURCE, value=value)


def test_names_and_listed_page_figures_are_not_figures():
    context = '"B = 192 circuit evaluations" (p.4)'
    require_verbatim("a1", context, SOURCE, value="On Phase 2's Dirac-3, the budget is 192 evaluations.")
    require_verbatim("a1", context, SOURCE, value="192 evaluations, 40 per seed", read_from_page=("40",))


# The rule itself moved to store.write_path (Sprint 11 retrospective I1b),
# so backup_before_write runs it before a write; this scan is the backstop.
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

# ------------------------------------------------------------------ Sprint 11 I1b

_CALLS_BACKUP = ("from store.backup import backup_before_write\n"
                 "def apply(db, backups):\n"
                 "    return backup_before_write(db, 'probe', backups)\n")


def _run_from_script(scripts_dir: Path, name: str, body: str, db: Path, backups: Path, monkeypatch):
    import store.write_path as wp
    monkeypatch.setattr(wp, "SCRIPTS", scripts_dir.resolve())
    script = scripts_dir / name
    script.write_text(body + _CALLS_BACKUP, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.apply(db, backups)


@pytest.mark.parametrize("name, body, refused", [
    ("sprint12_probe.py", "insert_assertion = None\n", True),
    ("sprint12_probe.py", "VALUE_REPLACE = {}\ninsert_verified_assertion = None\n", True),
    ("sprint12_probe.py", "insert_verified_assertion = None\n", False),
    ("sprint10_f89_reading.py", "insert_assertion = None\n", False),  # LEGACY: has run, stays as it is
])
def test_the_backup_refuses_a_script_that_breaks_the_rule_before_anything_is_written(
        tmp_path, monkeypatch, conn, name, body, refused):
    """Sprint 11 retrospective I1b: the scan above ran only with the full
    suite, after Tasks F and G had written. backup_before_write now runs it
    on the calling script first. Proven to fail by injection, 2026-10-23:
    with the require_clean_callers() call removed from backup_before_write,
    both refused cases took a backup and went red."""
    db, backups = tmp_path / "evidence.db", tmp_path / "backups"
    (tmp_path / "scripts").mkdir()
    if refused:
        with pytest.raises(RuntimeError, match="refused before the backup"):
            _run_from_script(tmp_path / "scripts", name, body, db, backups, monkeypatch)
        assert not backups.exists() or not any(backups.iterdir())
    else:
        assert _run_from_script(tmp_path / "scripts", name, body, db, backups, monkeypatch).exists()


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
