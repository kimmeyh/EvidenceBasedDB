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
    monkeypatch.setattr(b, "local_pdf", lambda path, rid: rid)
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
    the first page, "p.4.2" became "p.12.2"."""
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
    ]
    got = []
    for anchor, on, _ in cases:
        a = {"id": "x", "anchor": anchor,
             "quotes": [_q(n) if n != "unfound" else "a sentence the text layer garbled beyond use" for n in on]}
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
    (tmp_path / "reads" / "group_g080.json").write_text("kept", encoding="utf-8")
    b.main(["--write"])
    assert (tmp_path / "reads" / "group_g080.json").read_text(encoding="utf-8") == "kept"


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


def test_two_different_ids_on_one_assertion_are_refused(tmp_path, monkeypatch):
    b = _build(tmp_path, monkeypatch, {"c": [{"id": "one", "id_suggestion": "two"}], "d": []})
    with pytest.raises(ValueError, match="two ids"):
        b.entry("c")
