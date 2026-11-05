"""Sprint 15 Task H step 1: the reader check's `--sprint15` rules (scripts/sprint13_g_check.py) and the applier's
figure rule (scripts/full_read_apply.py), each from a Sprint 14 finding or from F115, F116 and F126. Neither opens
the real store or a real PDF here."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from store import quotes

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TEXT = quotes.plain("the accuracy rises with the qubit count as Figure 3 shows. a sentence on page five of the paper.")


def _paper(**changes) -> dict:
    p = {"record_id": "r", "read_extent": "full", "sections_read": ["1 Introduction"], "figure_count": 1,
         "figures": [{"figure": "Figure 3", "page": 4, "kind": "line plot", "shows": "accuracy against qubits",
                      "confirmed_by": "the accuracy rises with the qubit count"}],
         "existing": [{"id": "s1", "verdict": "confirmed", "context": "qml"}],
         "assertions": [{"id_suggestion": "n1", "value": "Read from Figure 3: about 0.9 at about 12 qubits",
                         "anchor": "Figure 3, p.4", "quotes": ["the accuracy rises with the qubit count"],
                         "from_figure": True, "certainty_suggestion": "low"}]}
    p.update(changes)
    return p


def test_the_sprint15_rules_each_name_their_breach(monkeypatch):
    """Proven to fail by injection, 2026-11-01: with sprint15_problems returning [] the test went red on the first
    breach; with the page check's page list taken from the wrong page (first + 1), the right-page quote was named."""
    check = _load("sprint13_g_check")
    pages = {4: "the accuracy rises with the qubit count as Figure 3 shows.", 5: "a sentence on page five of the paper."}
    monkeypatch.setattr(check, "page_text", lambda path, first, last: quotes.plain(
        " ".join(pages.get(n, "") for n in range(first, last + 1))))
    stored = {"s1": "qml"}
    assert check.sprint15_problems(_paper(), stored, TEXT, "x.pdf") == []
    breaches = {
        "sections_read": _paper(sections_read=[]),
        "figure_count": _paper(figure_count=2),
        "figures lists": _paper(figures=None),
        "no kind": _paper(figures=[{**_paper()["figures"][0], "kind": ""}]),
        "no_text_confirms": _paper(figures=[{**_paper()["figures"][0], "confirmed_by": ""}]),
        "confirmed_by is not verbatim": _paper(figures=[{**_paper()["figures"][0], "confirmed_by": "not in it at all"}]),
        "never changes a stored context": _paper(existing=[{"id": "s1", "verdict": "confirmed", "context": "ml"}]),
        "never high": _paper(assertions=[{**_paper()["assertions"][0], "certainty_suggestion": "high"}]),
        "anchors are PDF pages": _paper(assertions=[{**_paper()["assertions"][0], "anchor": "Figure 3, p.2"}]),
    }
    for words, p in breaches.items():
        found = check.sprint15_problems(p, stored, TEXT, "x.pdf")
        assert any(words in x for x in found), (words, found)
    # a quote that runs onto the next page is on its page; one two pages on is not
    late = {**_paper()["assertions"][0], "anchor": "p.4", "quotes": ["a sentence on page five of the paper"]}
    assert check.page_problems("t", late, "x.pdf", TEXT) == []
    assert check.page_problems("t", {**late, "anchor": "p.3"}, "x.pdf", TEXT)
    # a source that is not a PDF has no pages to check
    assert check.page_problems("t", late, "x.html", TEXT) == []
    # page lists and shortened ranges (review of Task F: only the first page was read, and "123-24" failed)
    assert check.spans("Section 3, p.4 and 9") == [(4, 4), (9, 9)]
    assert check.spans("pp. 4, 9") == [(4, 4), (9, 9)]
    assert check.spans("pp. 123-24") == [(123, 124)]
    assert check.spans("p.4 to 6") == [(4, 6)]
    assert check.spans("Section 2") == []
    # fresh-eyes review, 2026-11-02; proven to fail by injection, 2026-11-02, with the old pattern and bound restored
    assert check.spans("Section 2, page 9") == [(9, 9)]
    assert check.spans("Table 1, P. 9") == [(9, 9)]
    assert check.spans("Figure 3, pages 4-5") == [(4, 5)]
    assert check.spans("Section 2, p.0") == []


def test_the_sprint15_rules_run_only_with_the_option(tmp_path, monkeypatch, capsys):
    """An earlier sprint's read is checked as it ran; with --sprint15 the new rules apply. Proven to fail by
    injection, 2026-11-01: with main passing the stored contexts always, the run without the option named the
    missing figures list."""
    import json
    check = _load("sprint13_g_check")
    monkeypatch.setattr(check, "source_text", lambda path: TEXT)
    src = tmp_path / "x.html"
    src.write_text("x")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({"records": [{"record_id": "r", "file": str(src), "stored_assertions": []}]}))
    read = tmp_path / "read.json"
    read.write_text(json.dumps({"papers": [{"record_id": "r", "file": str(src), "read_extent": "full",
                                            "bears_on_context": "", "why_not": "not on any context"}]}))
    check.main([str(read), str(brief)])
    assert capsys.readouterr().out.strip() == "0 problems"
    check.main([str(read), str(brief), "--sprint15"])
    out = capsys.readouterr().out
    assert "figures lists every figure" in out and "sections_read" in out


def test_a_new_assertion_named_by_id_is_refused_under_sprint15(tmp_path, monkeypatch, capsys):
    """Reader g117 (2026-11-01): 36 of one paper's 37 new assertions said `id`, not `id_suggestion`, and the check
    printed 0 problems. Proven to fail by injection, 2026-11-01: with the key check removed, the `id` assertion
    passed."""
    import json
    check = _load("sprint13_g_check")
    monkeypatch.setattr(check, "source_text", lambda path: TEXT)
    src = tmp_path / "x.html"
    src.write_text("x")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({"records": [{"record_id": "r", "file": str(src), "stored_assertions": []}]}))
    a = {k: v for k, v in _paper()["assertions"][0].items() if k != "id_suggestion"}
    read = tmp_path / "read.json"
    for assertion, named in (({**a, "id": "n1"}, True), ({**a, "id_suggestion": "n1"}, False)):
        read.write_text(json.dumps({"papers": [{**_paper(existing=[]), "file": str(src), "assertions": [assertion]}]}))
        check.main([str(read), str(brief), "--sprint15"])
        assert ("r/n1: name a new assertion's id `id_suggestion`" in capsys.readouterr().out) is named


def test_a_figure_read_value_and_an_ocr_quote_are_checked_on_every_read(monkeypatch):
    """A number read by eye stands without a quote only as "about N", in a value that says it was read from a
    figure; a quote found only in OCR text says "OCR" in its anchor. Proven to fail by injection, 2026-11-01: with
    read_from_figure returning (), the "about 0.9" value was refused; with the OCR line removed, the unmarked OCR
    quote passed."""
    check = _load("sprint13_g_check")
    a = _paper()["assertions"][0] | {"kind": "shown", "claim_type": "positive", "context": "qml",
                                     "result_type": "measured"}
    assert check.assertion_problems("t", a, TEXT) == []
    assert any("0.9" in x for x in check.assertion_problems("t", {**a, "from_figure": False}, TEXT))
    assert any("says so" in x for x in check.assertion_problems("t", {**a, "value": "about 0.9 at 12 qubits"}, TEXT))
    assert any("12" in x for x in check.assertion_problems("t", {**a, "value": "Read from Figure 3: 0.9 at 12"}, TEXT))
    # the label is a name, not a pass for its number elsewhere (fresh-eyes review, 2026-11-02). Proven to fail by
    # injection, 2026-11-02: with the label's number excused again, "at depth 3" passed unquoted.
    assert check.assertion_problems("t", {**a, "value": "Read from Figures 3 and 4: about 0.9"}, TEXT) == []
    assert check.assertion_problems("t", {**a, "value": "Read from Figure 3(b): about 0.9, below Figure 2(a)"},
                                    TEXT) == []
    # a panel letter may be upper case (g134's "Figure 7C and 7D", recheck 2026-11-02). Proven to fail by
    # injection, 2026-11-02: with the label's panel letter lower case only, the value was refused for its 7.
    assert check.assertion_problems("t", {**a, "value": "Read from Figure 7C and 7D: about 0.9"}, TEXT) == []
    # a number joined to a label but followed by a word is a count, not a label (fresh-eyes review, 2026-11-04).
    # Proven to fail by injection, 2026-11-04: without the label's no-word-follows guard, both 4 and 30 passed.
    assert any("4" in x for x in check.assertion_problems(
        "t", {**a, "value": "Read from Figure 3, 4 qubits: about 0.9"}, TEXT))
    assert any("30" in x for x in check.assertion_problems(
        "t", {**a, "value": "Read from Figure 2A, 30 K: about 0.9"}, TEXT))
    assert any("3" in x for x in check.assertion_problems(
        "t", {**a, "value": "Read from Figure 3: about 0.9 at depth 3"}, TEXT))
    ocr_text = TEXT + quotes.OCR_MARK + "a sentence read from a page image"
    o = {**a, "from_figure": False, "value": "The authors state it.", "quotes": ["a sentence read from a page image"],
         "anchor": "Section 2, p.3"}
    assert any("OCR" in x for x in check.assertion_problems("t", o, ocr_text))
    assert check.assertion_problems("t", {**o, "anchor": "Section 2, p.3, OCR"}, ocr_text) == []


def test_a_stored_assertion_keeps_its_own_context_outside_the_five(tmp_path, monkeypatch, capsys):
    """Reader g133 (2026-11-02): two emami-2025 assertions are stored under platform:dirac-3, so a narrowed verdict
    could neither keep the stored context (a reader never changes one) nor pass the five-context check. Its own
    stored context passes; any other outside the five is still refused. Proven to fail by injection, 2026-11-02:
    with the stored context no longer passed to assertion_problems, the kept platform:dirac-3 was refused."""
    import json
    check = _load("sprint13_g_check")
    monkeypatch.setattr(check, "source_text", lambda path: TEXT)
    src = tmp_path / "x.html"
    src.write_text("x")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({"records": [{"record_id": "r", "file": str(src), "stored_assertions": [
        {"id": "s1", "context": "platform:dirac-3"}]}]}))
    e = {"id": "s1", "verdict": "narrowed", "value": "The authors state it.", "anchor": "Section 1, p.5",
         "quotes": ["a sentence on page five of the paper"], "kind": "shown", "claim_type": "positive",
         "result_type": "measured", "note": "narrowed to page five"}
    read = tmp_path / "read.json"
    for context, refused in (("platform:dirac-3", False), ("platform:dirac-1", True)):
        read.write_text(json.dumps({"papers": [{**_paper(existing=[{**e, "context": context}], assertions=[]),
                                                "file": str(src)}]}))
        check.main([str(read), str(brief), "--sprint15"])
        lines = capsys.readouterr().out.splitlines()
        assert (f"r/s1: context {context!r}" in lines) is refused  # the five-context line, not the stored-context one


def test_the_applier_refuses_a_figure_read_value_graded_high_or_unlabeled():
    """F116: the coordinator's grade, not only the reader's suggestion, is checked. Proven to fail by injection,
    2026-11-01: with figure_check's HIGH test removed, the HIGH figure value passed."""
    apply = _load("full_read_apply")
    p = {"assertions": [{"id_suggestion": "n1", "from_figure": True}, {"id_suggestion": "n2"}],
         "existing": [{"id": "s1", "from_figure": True}]}
    assert apply.figure_ids(p) == {"n1", "s1"}

    class A:
        id, value, certainty = "n1", "Read from Figure 3: about 0.9", "low"

    apply.figure_check(A)
    A.certainty = "high"
    with pytest.raises(ValueError, match="never HIGH"):
        apply.figure_check(A)
    A.certainty, A.value = "low", "about 0.9"
    with pytest.raises(ValueError, match="says so"):
        apply.figure_check(A)


def test_the_applier_reads_an_ocr_anchor_that_holds_parentheses():
    """Review of Task F: the OCR-anchor pattern stopped at the first ")", so "Section 2 (Methods), p.3, OCR" passed
    the reader check and was refused at apply. Proven to fail by injection, 2026-11-01: with "[^)]*" restored, the
    marked quote was refused."""
    apply = _load("full_read_apply")

    class A:
        id, certainty, certainty_reasons = "n1", "low", ""
        citation_context = '"a sentence read from a page image" (Section 2 (Methods), p.3, OCR)'

    text = "the layer" + quotes.OCR_MARK + "a sentence read from a page image"
    apply.ocr_check(A, "x.pdf", text)
    A.citation_context = '"a sentence read from a page image" (Section 2 (Methods), p.3); "the layer" (p.1, OCR)'
    with pytest.raises(ValueError, match="OCR"):
        apply.ocr_check(A, "x.pdf", text)
