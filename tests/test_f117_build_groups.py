"""Sprint 14 Task E (F117): F114's per-paper cloud results assembled into group reader files."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _build(tmp_path: Path, monkeypatch, results: dict[str, list[dict]]):
    spec = importlib.util.spec_from_file_location("f117_build_groups", ROOT / "scripts" / "f117_build_groups.py")
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    work = tmp_path / "work"
    (work / "results").mkdir(parents=True)
    for rid, assertions in results.items():
        (work / "results" / f"{rid}.json").write_text(json.dumps({"papers": [{"record_id": rid, "assertions": assertions}]}),
                                                      encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {
        "g001": {"records": [{"record_id": "old"}]},
        "g076": {"records": [{"record_id": r} for r in ("a", "u")]},
        "g079": {"records": [{"record_id": r} for r in ("b", "abbas")]},
        "g080": {"records": [{"record_id": r} for r in ("c", "d")]}}}), encoding="utf-8")
    monkeypatch.setattr(b.cloud, "WORK", work)
    monkeypatch.setattr(b.cloud, "LEDGER", ledger)
    monkeypatch.setattr(b.cloud, "FIRST_GROUP", "g043")
    monkeypatch.setattr(b, "UNREAD", {"u": "page images only"})
    monkeypatch.setattr(b, "READS_DIR", tmp_path / "reads")
    monkeypatch.setattr(b, "held_elsewhere", lambda ids: {})
    monkeypatch.setattr(b, "LOCAL", work / "local")
    monkeypatch.setattr(b, "local_pdf", lambda path, rid: f"{rid}.pdf")
    monkeypatch.setattr(b, "pdf_pages", lambda path: ())
    monkeypatch.setattr(b, "PAGE_NOTES", [])
    (work / "local" / "briefs").mkdir(parents=True)
    (work / "local" / "reads").mkdir()
    (tmp_path / "reads").mkdir()
    return b


def test_a_local_read_is_taken_over_the_cloud_result_and_its_group_waits_for_the_reader(tmp_path, monkeypatch):
    """Sprint 14 Task F: a local reader's group file is the paper's read; a cloud result named in NOT_A_READ (Boyd's,
    which sampled the book) is not; a group with a local brief waits for its reader's group file; a record the brief
    trims that has no cloud result is left for the next release, and a record the brief holds is not. Proven to fail
    by injection, 2026-10-30: with entry() reading the cloud result first, g079's b held the cloud assertion; with
    NOT_A_READ empty, g079 was built from b's cloud result before b's local read existed; with waiting() always empty,
    g079 was built while its reader was at work (review of 1cb63bb: the test patched WAIT, so this never ran); with
    local_unread() not checking the brief, c, briefed and not yet read, was marked for the next release."""
    b = _build(tmp_path, monkeypatch, {"b": [{"id": "cloud"}], "a": [], "c": [], "d": []})
    monkeypatch.setattr(b, "NOT_A_READ", {"b"})
    local = tmp_path / "work" / "local"
    (local / "briefs" / "g079.json").write_text(json.dumps({"records": [{"record_id": r} for r in ("b", "abbas")]}),
                                                encoding="utf-8")
    group = local / "reads" / "group_g079.json"
    assert "g079" not in b.buildable()  # b has only the cloud result, which is not a read
    assert b.waiting() == {"g079"}
    group.write_text(json.dumps({"papers": [{"record_id": r, "assertions": [{"id_suggestion": f"{r}-local"}]}
                                            for r in ("abbas", "b")]}), encoding="utf-8")
    assert b.waiting() == set()
    assert b.buildable()["g079"] == ["b", "abbas"]
    assert b.entry("b") == {"record_id": "b", "assertions": [{"id_suggestion": "b-local"}]}
    assert b.local_file("abbas") == group
    (local / "briefs" / "g080.json").write_text(json.dumps({"records": [{"record_id": "c"}]}), encoding="utf-8")
    for r in ("c", "d"):
        (tmp_path / "work" / "results" / f"{r}.json").unlink()
    assert b.local_unread() == {"d": b.NEXT_RELEASE}
    assert "g080" not in b.buildable()  # c's reader is at work


def test_a_group_is_built_only_when_named_and_a_changed_reader_file_is_refused(tmp_path, monkeypatch):
    """Sprint 15: g131's run built g130 while g130's reader was still editing, and since the builder never rebuilds,
    the reader's last edits (101 items became 108) would have been lost without a word. `--group` builds only the
    groups named; each built file records its reader file's SHA-256, and a run stops when that file has changed.
    Proven to fail by injection, 2026-11-02: with --group ignored, g080 was built too; with stale() returning [],
    the changed g079 passed."""
    b = _build(tmp_path, monkeypatch, {"a": [], "c": [], "d": []})
    local = tmp_path / "work" / "local"
    (local / "briefs" / "g079.json").write_text(json.dumps({"records": [{"record_id": r} for r in ("b", "abbas")]}),
                                                encoding="utf-8")
    read = local / "reads" / "group_g079.json"
    read.write_text(json.dumps({"papers": [{"record_id": r, "assertions": []} for r in ("abbas", "b")]}),
                    encoding="utf-8")
    assert b.main(["--write", "--group", "g079"]) == 0
    assert sorted(p.name for p in (tmp_path / "reads").iterdir()) == ["group_g079.json"]
    built = json.loads((tmp_path / "reads" / "group_g079.json").read_text(encoding="utf-8"))
    assert built["read_sha256"] == b.read_sha256("g079")
    read.write_text(json.dumps({"papers": [{"record_id": r, "assertions": [{"id_suggestion": "late"}]}
                                           for r in ("abbas", "b")]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="g079"):
        b.main(["--write"])


QUOTE_A = "the bound holds for every n at least two and is tight"
QUOTE_B = "the same experiment was repeated on hardware with ten seeds"
QUOTE_C = "we thank the referees for their careful reading of the draft"


def test_a_local_reads_page_anchor_is_set_to_the_pdf_page_its_quotes_are_on(tmp_path, monkeypatch):
    """Review of g104 (Sprint 14 Task F): the local readers' text layers had lost their page breaks, so their page
    anchors ran up to 15 pages off. A page is set where it can be computed, dropped where it is wrong and cannot
    be, and an anchor left with no section is listed. Proven to fail by injection, 2026-10-30: with entry() not
    calling fix_pages, the anchor kept p.9; with the one-page check removed, the anchor naming two pages was rewritten
    to one; with the empty-anchor check removed, "p.9" became ""; with `not found` removed from the first check, an
    anchor none of whose quotes was found lost its page."""
    b = _build(tmp_path, monkeypatch, {})
    pages = ("front matter", f"intro {QUOTE_A}", f"results {QUOTE_B} {QUOTE_C}", f"appendix {QUOTE_C}")
    monkeypatch.setattr(b, "pdf_pages", lambda path: tuple(b._norm(p) for p in pages))
    local = tmp_path / "work" / "local"
    (local / "briefs" / "g079.json").write_text(json.dumps({"records": [{"record_id": "abbas"}]}), encoding="utf-8")
    (local / "reads" / "group_g079.json").write_text(json.dumps({"papers": [{"record_id": "abbas", "assertions": [
        {"id_suggestion": "off", "anchor": "Theorem 1, Section 2, p.9", "quotes": [QUOTE_A]},
        {"id_suggestion": "right", "anchor": "Section 2, pp.1-2", "quotes": [QUOTE_A]},
        {"id_suggestion": "section-only", "anchor": "Section 4", "quotes": [QUOTE_B]},
        {"id_suggestion": "two-pages-named", "anchor": "Section 2, p.5; Section 4, p.7", "quotes": [QUOTE_A]},
        {"id_suggestion": "repeated-quote", "anchor": "Section 4, p.1", "quotes": [QUOTE_C]},
        {"id_suggestion": "page-only", "anchor": "p.9", "quotes": [QUOTE_C]},
        {"id_suggestion": "not-found", "anchor": "Section 5, p.6", "quotes": ["a sentence the text layer garbled"]}],
        "existing": [{"id": "stored", "anchor": "Section 2 and 4, p.1", "quotes": [QUOTE_A, QUOTE_B]}]}]}),
        encoding="utf-8")
    anchors = {a.get("id_suggestion") or a["id"]: a["anchor"] for p in [b.entry("abbas")]
               for a in p["assertions"] + p["existing"]}
    assert anchors == {"off": "Theorem 1, Section 2, p.2", "right": "Section 2, pp.1-2", "section-only": "Section 4",
                       "two-pages-named": "Section 2; Section 4", "repeated-quote": "Section 4",
                       "stored": "Section 2 and 4, pp.2-3", "page-only": "p.9", "not-found": "Section 5, p.6"}
    assert [n.split(": ")[1] for n in b.PAGE_NOTES if "left for the coordinator" in n] == ["page-only"]


def test_a_web_page_is_not_page_fixed_and_pages_are_split_as_the_reader_check_splits_them(tmp_path, monkeypatch):
    """Sprint 15 Task H: g120's cycorp-2002 is a saved web page, and the builder ran pdftotext on it and stopped;
    and a page that holds its own form feed (Qian et al. 2021: 103 parts for 23 pages) put every later quote pages
    late. Proven to fail by injection, 2026-11-01: with the ".pdf" test removed, the web page's entry called
    pdf_pages; with pdf_pages splitting on form feeds, the quote after the inner form feed was on page 3."""
    b = _build(tmp_path, monkeypatch, {})
    monkeypatch.setattr(b, "local_pdf", lambda path, rid: f"{rid}.html")
    monkeypatch.setattr(b, "pdf_pages", lambda path: pytest.fail("a web page has no PDF pages"))
    local = tmp_path / "work" / "local"
    (local / "briefs" / "g079.json").write_text(json.dumps({"records": [{"record_id": "cyc"}]}), encoding="utf-8")
    (local / "reads" / "group_g079.json").write_text(json.dumps({"papers": [{"record_id": "cyc", "assertions": [
        {"id_suggestion": "web", "anchor": "Section 2, p.9", "quotes": [QUOTE_A]}]}]}), encoding="utf-8")
    assert b.entry("cyc")["assertions"][0]["anchor"] == "Section 2, p.9"
    from store import ocr
    monkeypatch.setattr(ocr, "page_texts", lambda path: [f"one {QUOTE_A}\f still page one", f"two {QUOTE_B}"])
    spec = importlib.util.spec_from_file_location("f117_build_groups", ROOT / "scripts" / "f117_build_groups.py")
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    pages = fresh.pdf_pages("x.pdf")
    assert [i for i, t in enumerate(pages, 1) if fresh._norm(QUOTE_B) in t] == [2]


def _q(n: int) -> str:
    return f"quoted passage number {n} long enough to be matched on its page"


PAGES = tuple(f"page {n} text {_q(n)}" for n in range(1, 17))


def test_page_lists_sections_and_punctuation(tmp_path, monkeypatch):
    """Review of 11d443a: a page list ("p.6, 14", "pp.6 and 8") kept its stale tail; one range stretched over
    several sections; a drop left stray punctuation and the rest of a page list; an unfound quote forced a drop.
    Proven to fail by injection, 2026-10-30: with PAGE matching one page or range only (11d443a's), "p.6, 14" became
    "pp.7-16, 14"; with pages joined as one range, "Abstract; Section V.B, pp.6-8" became "pp.1-7"; with
    _without_pages's cleanup removed, "Section 3.1, p.4 (Figure 4)" became "Section 3.1, (Figure 4)"; with unfound
    quotes kept in `on`, "Section 2.1, p.13" lost its page; with `keep` empty, the pages an unfound quote may be on
    were lost ("pp.6-7 and 9" became "p.10"). Review of 8f2b408, proven to fail by injection 2026-10-30: with the
    "printed" prefix case-sensitive, "Printed p.145" became "Printed p.3"; with no lookahead after a list item,
    "p.12, 4.3" became "p.7.3"; without "to" ranges, "pp. 12 to 15" became "p.14 to 15"; without compressed ranges,
    "pp.12-5" became "p.13"; without the new cleanup, a drop left "(, Figure 2)". Review of aa8c75f, proven to fail
    the same day: with a period refused after a list item, "pp.6, 8." became "p.8, 8."; with a "to" range not ending
    its clause, "p.4 to 6 qubits" became "p.12 qubits"; with every "on" before a comma removed, "(noise turned on)"
    lost its last word. Review of ee397c6, proven to fail the same day: with "of" ending a list item, "p.12, 4 of 10
    qubits" lost its 4; with a preposition removed only after a space, "(see p.4)" left "(see)"; with no guard on
    the first page, "p.4.2" became "p.12.2". Review of ccaedc2: that guard backtracked, so with ccaedc2's guard
    "p.12.3" became "p.72.3" (proven red the same day)."""
    b = _build(tmp_path, monkeypatch, {})
    norm = tuple(b._norm(p) for p in PAGES)
    cases = [
        ("Sections 6 and 9, p.6, 14", [7, 16], "Sections 6 and 9, pp.7, 16"),
        ("Section IV.B.2, pp.6 and 8", [5, 9], "Section IV.B.2, pp.5, 9"),
        ("Abstract; Section V.B, pp.6-8", [1, 7], "Abstract; Section V.B, pp.1, 7"),
        ("Section 3, pp.4-5", [8, 9, 10], "Section 3, pp.8-10"),
        ("Section 3.1, p.4 (Figure 4); Section 5, p.9", [2], "Section 3.1 (Figure 4); Section 5"),
        ("Exercise 1.2 (p.3) and Appendix A.2 (p.9)", [5], "Exercise 1.2 and Appendix A.2"),
        ("Section IV.B, p.8 and 9; Appendix A.1, p.11-12", [2], "Section IV.B; Appendix A.1"),
        ("Section 2.1, p.13", [14, "unfound"], "Section 2.1, pp.13-14"),
        ("Section II.C.2 and Section IV.B.2, pp.6-7 and 9", ["unfound", 10], "Section II.C.2 and Section IV.B.2, "
                                                                            "pp.6-7, 9-10"),
        ("Section 2, p.5—6", [12], "Section 2, p.12"),
        ("Results, pages 4-5", [12], "Results, p.12"),
        ("Section 4, PDF p.9 (printed p.145)", [3], "Section 4, PDF p.3 (printed p.145)"),
        ("Section 2, pp.6, 8", [6, 8], "Section 2, pp.6, 8"),
        ("Fig. 3, Eq. (5), Section 2", [3], "Fig. 3, Eq. (5), Section 2"),
        # Review of 8f2b408: a capitalized or colon "printed" clause, a number after a page list, "to" ranges,
        # leftovers of a drop, and a compressed range.
        ("Section 4, Printed p.145", [3], "Section 4, Printed p.145"),
        ("Section 4, printed: p.145", [3], "Section 4, printed: p.145"),
        ("Section 4, p.12, 4.3", [7], "Section 4, p.7, 4.3"),
        ("Section 4, p.12, 4 qubits", [7], "Section 4, p.7, 4 qubits"),
        ("Fig. 2 p.3, 2024 edition", [9], "Fig. 2 p.9, 2024 edition"),
        ("Section 4, p.12, 4", [4], "Section 4, p.12, 4"),
        ("Section 3, pp. 12 to 15", [14], "Section 3, pp. 12 to 15"),
        ("Section 3, pp. 2 to 5", [8], "Section 3, p.8"),
        ("Section 3 (p.4, Figure 2), Section 5, p.9", [2], "Section 3 (Figure 2), Section 5"),
        ("Theorem 2 on p.4; Section 5, p.9", [2], "Theorem 2; Section 5"),
        ("Section 3 [p.4] and Section 5 [p.9]", [2], "Section 3 and Section 5"),
        ("Lemma 1, pp.12-5", [13], "Lemma 1, pp.12-5"),
        # Review of aa8c75f: a list ending its sentence, a "to" before a count, a word that led into no page.
        ("Section 1, pp.6, 8.", [8], "Section 1, pp.6, 8."),
        ("Section 1, pp.6 and 8.", [9], "Section 1, p.9."),
        ("Section 3, p.4 to 6 qubits", [12], "Section 3, p.12 to 6 qubits"),
        ("Section 3, p.3 to 5 of the appendix", [8], "Section 3, p.8 of the appendix"),
        ("Section 5 (noise turned on), p.4; Section 6, p.9", [2], "Section 5 (noise turned on); Section 6"),
        ("Section 3 in p.4 and Section 5, p.9", [2], "Section 3 and Section 5"),
        # Review of ee397c6: "of" after a count, a preposition after "(" or first, a section after "p.".
        ("Section 4, p.12, 4 of 10 qubits", [7], "Section 4, p.7, 4 of 10 qubits"),
        ("Section 3 (see p.4); Section 5, p.9", [2], "Section 3; Section 5"),
        ("See p.4; Section 3, p.9", [2], "Section 3"),
        ("Section 3, p.4.2", [12], "Section 3, p.4.2"),
        # Review of ccaedc2: the guard backtracked, so "p.12.3" matched "p.1".
        ("Section 4, p.12.3", [7], "Section 4, p.12.3"),
        ("Section 3, p.12.3 and p.9", [2], "Section 3, p.12.3 and p.2"),
    ]
    got = []
    for anchor, on, _ in cases:
        a = {"id": "x", "anchor": anchor,
             "quotes": [_q(n) if n != "unfound" else "a sentence the text layer garbled beyond use" for n in on]}
        b.fix_pages("r", a, norm)
        got.append(a["anchor"])
    assert got == [want for _, _, want in cases]


def test_the_page_fixers_three_leftover_cases(tmp_path, monkeypatch):
    """F126 (Sprint 15 Task D): the three cases Sprint 14 left after five review rounds. A dash range's end had no
    ".digit" guard, so "p.12-15.3" became "p.7.3"; a dropped "to" range left its "of 10"; "p.12a" became "p.7a". A
    clause the fixer cannot read as pages is left as written, as "p.12.3" is. Proven to fail, 2026-11-01, run before
    the change: the three anchors came back as "Section 4, p.7.3", "Section 3, of 10; Section 5" and "Section 4,
    p.7a"."""
    b = _build(tmp_path, monkeypatch, {})
    norm = tuple(b._norm(p) for p in PAGES)
    cases = [
        ("Section 4, p.12-15.3", [7], "Section 4, p.12-15.3"),
        ("Section 3, p.4 to 6 of 10; Section 5, p.9", [2], "Section 3; Section 5"),
        ("Section 4, p.12a", [7], "Section 4, p.12a"),
        # the guards leave the ordinary range and the "to" range they share their pattern with as they were
        ("Section 4, pp.12-15", [7], "Section 4, p.7"),
        ("Section 3, p.4 to 6 of 10", [9], "Section 3, p.9 of 10"),
        # review of the uncommitted D and E: "of" is dropped only after a "to" range; a "to" range whose end is a
        # section or carries a letter is left as written, as the dash form is; a glued "ff" is not a page. Proven
        # to fail by injection, 2026-11-01: with "of N" dropped after any clause, "of 2019" was lost; with the "to"
        # form out of _BAD_RANGE, "p.12 to 15.3" became "p.7 to 15.3"
        ("Fig 3 on p.4 of 2019 survey; Section 5, p.9", [2], "Fig 3 of 2019 survey; Section 5"),
        ("Section 4, p.12 to 15.3", [7], "Section 4, p.12 to 15.3"),
        ("Section 4, p.12 to 15a", [7], "Section 4, p.12 to 15a"),
        ("Section 4, p.4ff", [7], "Section 4, p.4ff"),
    ]
    got = []
    for anchor, on, _ in cases:
        a = {"id": "x", "anchor": anchor, "quotes": [_q(n) for n in on]}
        b.fix_pages("r", a, norm)
        got.append(a["anchor"])
    assert got == [want for _, _, want in cases]


def test_only_whole_groups_are_built_and_ids_are_renamed(tmp_path, monkeypatch):
    """A group is built when every record has a result or the team lead's unread mark; a record only set aside from
    the cloud (abbas, read by Task F) holds its group back; an unread record that has a result (u, whose file gave
    nothing to read) is left out of its group file. Proven to fail by injection, 2026-10-30: with the build counting
    f114_cloud.UNREAD (which holds abbas) as unread, g079 was built; with the rename removed, the entry kept `id`;
    with unread records kept in the file, g076 held u."""
    b = _build(tmp_path, monkeypatch, {"a": [{"id": "x1"}], "b": [], "c": [{"id_suggestion": "y"}],
                                       "d": [{"id": "z", "id_suggestion": "z"}], "old": [], "u": []})
    monkeypatch.setattr(b.cloud, "UNREAD", {"u": "page images only", "abbas": "set aside from the cloud"})
    assert b.buildable() == {"g076": ["a"], "g080": ["c", "d"]}
    assert b.main(["--write"]) == 0
    g076 = json.loads((tmp_path / "reads" / "group_g076.json").read_text(encoding="utf-8"))
    assert g076 == {"papers": [{"record_id": "a", "assertions": [{"id_suggestion": "x1"}]}]}
    g080 = json.loads((tmp_path / "reads" / "group_g080.json").read_text(encoding="utf-8"))
    assert [a for p in g080["papers"] for a in p["assertions"]] == [{"id_suggestion": "y"}, {"id_suggestion": "z"}]
    (tmp_path / "reads" / "group_g080.json").write_text('{"papers": []}', encoding="utf-8")
    b.main(["--write"])
    assert (tmp_path / "reads" / "group_g080.json").read_text(encoding="utf-8") == '{"papers": []}'


def test_a_repeated_or_taken_id_takes_its_papers_author_and_year(tmp_path, monkeypatch):
    """Each cloud session saw one paper, so generic ids repeat across papers, and the applier's ID_FIX cannot tell
    them apart. Proven to fail by injection, 2026-10-30: with assemble renaming nothing, both papers kept
    `conclusion-summary`; with the store check removed, `dla-definition` kept the id another source holds."""
    b = _build(tmp_path, monkeypatch, {})
    entries = {"xu-2025-accelerating-rl": [{"id_suggestion": "conclusion-summary"}, {"id_suggestion": "own-id"}],
               "ahmad-2026-quantum-vs-classical": [{"id_suggestion": "conclusion-summary"}],
               "barlow-2026-subspace-control": [{"id_suggestion": "dla-definition"}],
               "lan-2026-beyond-expressivity": [{"id_suggestion": "lan-own"}]}
    monkeypatch.setattr(b, "entry", lambda rid: {"record_id": rid, "assertions": [dict(a) for a in entries[rid]]})
    monkeypatch.setattr(b, "held_elsewhere", lambda ids: {i: "lan-2026-other-paper, Section 3" for i in ids
                                                          if i == "dla-definition"})
    built, renames = b.assemble({"g043": ["xu-2025-accelerating-rl", "barlow-2026-subspace-control"],
                                 "g082": ["ahmad-2026-quantum-vs-classical", "lan-2026-beyond-expressivity"]})
    ids = {p["record_id"]: [a["id_suggestion"] for a in p["assertions"]] for ps in built.values() for p in ps}
    assert ids == {"xu-2025-accelerating-rl": ["xu-2025-conclusion-summary", "own-id"],
                   "barlow-2026-subspace-control": ["barlow-2026-dla-definition"],
                   "ahmad-2026-quantum-vs-classical": ["ahmad-2026-conclusion-summary"],
                   "lan-2026-beyond-expressivity": ["lan-own"]}
    assert len(renames) == 3


def test_a_group_built_late_never_takes_an_id_a_written_file_holds(tmp_path, monkeypatch):
    """Review of cecf20d: a lower group built after a higher one took the prefix the higher group's file already held
    (two files with one id); a prefixed id was never looked up in the store; "...-assessment" counted as the same
    source as "...-assessment-appendix-b"; two papers with the same author and year were not tested. Proven to fail
    by injection, 2026-10-30: with `written` not counted as taken, g079 took chen-2024-x a second time; with the store
    check removed from prefixed, chen-2024-y kept the id the store holds; with same_source a substring test, the
    appendix's id was kept; with `new not in taken` removed, both chen-2024 papers took chen-2024-z."""
    b = _build(tmp_path, monkeypatch, {})
    entries = {"chen-2024-a": [{"id_suggestion": "x"}], "chen-2024-b": [{"id_suggestion": "x"}],
               "other-2025-p": [{"id_suggestion": "x"}], "chen-2024-c": [{"id_suggestion": "y"}],
               "chen-2024-d": [{"id_suggestion": "z"}], "chen-2024-e": [{"id_suggestion": "z"}],
               "rand-2022-assessment": [{"id_suggestion": "w"}], "zed-2023-k": [{"id_suggestion": "x"}]}
    monkeypatch.setattr(b, "entry", lambda rid: {"record_id": rid, "assertions": [dict(a) for a in entries[rid]]})
    held = {"y": "elsewhere-2020-q, p.1", "chen-2024-y": "elsewhere-2020-q, p.2",
            "w": "rand-2022-assessment-appendix-b, p.3"}
    monkeypatch.setattr(b, "held_elsewhere", lambda ids: {i: held[i] for i in ids if i in held})
    first, _ = b.assemble({"g080": ["chen-2024-b"], "g090": ["other-2025-p"]})
    (tmp_path / "reads" / "group_g080.json").write_text(json.dumps({"papers": first["g080"]}), encoding="utf-8")
    (tmp_path / "reads" / "group_g090.json").write_text(json.dumps({"papers": first["g090"]}), encoding="utf-8")
    assert first["g080"][0]["assertions"][0]["id_suggestion"] == "chen-2024-x"
    late, _ = b.assemble({"g079": ["chen-2024-a", "chen-2024-c", "chen-2024-d", "chen-2024-e", "rand-2022-assessment",
                                   "zed-2023-k"]}, b.written_ids())
    ids = {p["record_id"]: p["assertions"][0]["id_suggestion"] for p in late["g079"]}
    assert ids == {"chen-2024-a": "chen-2024-a-x", "chen-2024-c": "chen-2024-c-y", "chen-2024-d": "chen-2024-z",
                   "chen-2024-e": "chen-2024-e-z", "rand-2022-assessment": "rand-2022-w", "zed-2023-k": "zed-2023-x"}


def test_a_written_files_bare_id_is_never_taken_and_a_rebuild_keeps_its_decided_ids(tmp_path, monkeypatch):
    """Review of 7914e80: no test held an id that a written file holds bare and the new batch holds once, or drove
    main, so neither `aid in written` nor main passing written_ids() was proven; a group rebuilt after its file was
    deleted was prefixed against another batch, so its ids could change under its review decisions. Proven to fail by
    injection, 2026-10-30: with `or aid in written` removed, chen-2024-a kept x; with main calling assemble(new), the
    same; with the decided-id check removed, the rebuild wrote chen-2024-x under decisions naming chen-2024-a-x."""
    b = _build(tmp_path, monkeypatch, {})
    entries = {"chen-2024-a": [{"id_suggestion": "x"}]}
    monkeypatch.setattr(b, "entry", lambda rid: {"record_id": rid, "assertions": [dict(a) for a in entries[rid]]})
    monkeypatch.setattr(b, "buildable", lambda: {"g076": ["chen-2024-a"]})
    (tmp_path / "reads" / "group_g080.json").write_text(json.dumps({"papers": [
        {"record_id": "other", "assertions": [{"id_suggestion": "x"}]}]}), encoding="utf-8")
    b.main(["--write"])
    g076 = tmp_path / "reads" / "group_g076.json"
    assert json.loads(g076.read_text(encoding="utf-8"))["papers"][0]["assertions"][0]["id_suggestion"] == "chen-2024-x"
    g076.unlink()
    (tmp_path / "reads" / "group_g080.json").unlink()
    decisions = tmp_path / "work" / "review" / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "g076.json").write_text(json.dumps({"chen-2024-a-x": {}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="chen-2024-a-x"):
        b.main(["--write"])
    assert not g076.exists()
    # Fresh-eyes review of f79714b: a group reviewed in parts (F142 part 3) was invisible to this guard. Proven red
    # 2026-11-07: with `decided_ids` reading only `<g>.json` again (INJECTED), the rebuild below was written.
    (decisions / "g076.json").unlink()
    (decisions / "g076.p1.json").write_text(json.dumps({"other-id": {}}), encoding="utf-8")
    (decisions / "g076.p2.json").write_text(json.dumps({"chen-2024-a-x": {}}), encoding="utf-8")
    (decisions / "g076.p1.old.json").write_text("{}", encoding="utf-8")  # a stray name is not a part
    with pytest.raises(SystemExit, match="chen-2024-a-x"):
        b.main(["--write"])
    assert not g076.exists()


def test_two_different_ids_on_one_assertion_are_refused(tmp_path, monkeypatch):
    b = _build(tmp_path, monkeypatch, {"c": [{"id": "one", "id_suggestion": "two"}], "d": []})
    with pytest.raises(ValueError, match="two ids"):
        b.entry("c")


def test_the_builders_three_edge_cases(tmp_path, monkeypatch):
    """F127 (Sprint 15 Task E), from the review of 7914e80: written_ids did not count an id_fix target in the review
    files, so a new paper could be prefixed onto one; held_elsewhere returned nothing when the store file was missing,
    so every store check passed without a word; same_source took "." as a token end, so v-2 matched inside v-2.5.
    Proven to fail, 2026-11-01, run before the change: src-x was missing from written_ids, held_elsewhere returned {},
    and same_source("v-2", "v-2.5, p.1") was True."""
    b = _build(tmp_path, monkeypatch, {})
    (tmp_path / "reads" / "group_g050.json").write_text(
        json.dumps({"papers": [{"record_id": "p", "assertions": [{"id_suggestion": "x"}]}]}), encoding="utf-8")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "g050.json").write_text(json.dumps({"id_fix": {"x": "src-x"}}), encoding="utf-8")
    monkeypatch.setattr(b, "REVIEWS_DIR", reviews)
    assert b.written_ids() == {"x", "src-x"}
    spec = importlib.util.spec_from_file_location("f117_fresh", ROOT / "scripts" / "f117_build_groups.py")
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    monkeypatch.setattr(fresh, "DB_PATH", tmp_path / "no-store.db")
    with pytest.raises(FileNotFoundError, match="no-store.db"):
        fresh.held_elsewhere({"x"})
    assert not b.same_source("v-2", "v-2.5, p.1")
    assert b.same_source("v-2", "drawn from v-2.")
    assert b.same_source("v-2", "v-2, p.1")


def test_a_re_entry_group_is_built_from_its_local_reads(tmp_path, monkeypatch):
    """F125 (Sprint 15 Task C): a local brief named "g080-r1" holds records a reviewed group left unread; once its
    reader's group file exists, the group is built under that name, though its parent's brief marks the records for
    the next release. Proven to fail, 2026-11-01, run before the change: the re-entry group was never buildable.
    After the review of 34034bd, proven to fail by injection: with the predecessor check removed, the brief missing
    e was built; with the brief's "unread" ignored, the group with e still unread was never built."""
    b = _build(tmp_path, monkeypatch, {"c": []})
    local = tmp_path / "work" / "local"
    (local / "briefs" / "g080.json").write_text(json.dumps({"records": [{"record_id": "c"}]}), encoding="utf-8")
    (local / "reads" / "group_g080.json").write_text(json.dumps({"papers": [{"record_id": "c"}]}), encoding="utf-8")
    monkeypatch.setattr(b, "UNREAD", {**b.UNREAD, **b.local_unread()})
    assert b.UNREAD["d"] == b.NEXT_RELEASE
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    monkeypatch.setattr(b, "REVIEWS_DIR", reviews)
    brief = local / "briefs" / "g080-r1.json"
    brief.write_text(json.dumps({"records": [{"record_id": "d"}]}), encoding="utf-8")
    # review of 34034bd: a brief is checked against its predecessor's review before anything is built
    with pytest.raises(ValueError, match="g080 has no review"):
        b.buildable()
    (reviews / "g080.json").write_text(json.dumps({"unread": {"d": "next release", "e": "no text"}}), encoding="utf-8")
    with pytest.raises(ValueError, match=r"\['e'\] differ from what g080's review left unread"):
        b.buildable()
    brief.write_text(json.dumps({"records": [{"record_id": "d"}, {"record_id": "e"}],
                                 "unread": {"e": "no text, still"}}), encoding="utf-8")
    assert "g080-r1" not in b.buildable()  # its reader is at work
    (local / "reads" / "group_g080-r1.json").write_text(
        json.dumps({"papers": [{"record_id": "d", "assertions": [{"id_suggestion": "d-one"}]}]}), encoding="utf-8")
    assert b.buildable()["g080-r1"] == ["d"]  # e stays unread, as its brief says
    assert b.entry("d") == {"record_id": "d", "assertions": [{"id_suggestion": "d-one"}]}
