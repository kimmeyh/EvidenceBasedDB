"""F60 (Sprint 8 Task E): the manifest check classes each row by the arXiv
stamp on its file's first page. Runs on a synthetic folder; no real PDF is
read."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("f60", ROOT / "scripts" / "sprint8_f60_manifest_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_asfaw_case_is_a_mismatch():
    """The Sprint 7 finding: row 2108.0131, file stamped 2108.00131.
    Proven to fail by injection, 2026-10-12: with classify comparing only
    the first four digits, this test went red."""
    cls, stamped = _mod().classify("2108.0131", "arXiv:2108.00131v2 [cs.LG] 22 Feb 2022\nWide neural networks")
    assert (cls, stamped) == ("mismatch", "2108.00131")


def test_classes_for_every_row_and_unlisted_file(tmp_path):
    folder = tmp_path / "2021"
    folder.mkdir()
    (folder / "manifest.tsv").write_text(
        "file\tarxiv_id\turl\ttitle\n"
        "A__2101.00001.pdf\t2101.00001\tu\tA\n"
        "B__2101.00002.pdf\t2101.00002\tu\tB\n"
        "C__2101.00003.pdf\t2101.00003\tu\tC\n"
        "D__2101.00004.pdf\t2101.00004\tu\tD\n", encoding="utf-8")
    pages = {"A__2101.00001.pdf": "arXiv:2101.00001v3 [quant-ph]", "B__2101.00002.pdf": "arXiv:2101.09999v1",
             "C__2101.00003.pdf": "Journal of Things, vol. 1", "E.pdf": ""}
    for name in pages:
        (folder / name).write_bytes(b"%PDF")
    rows = _mod().check(tmp_path, read=lambda p: pages[p.name])
    got = {r["file"]: r["cls"] for r in rows}
    assert got == {"A__2101.00001.pdf": "match", "B__2101.00002.pdf": "mismatch", "C__2101.00003.pdf": "no stamp",
                   "D__2101.00004.pdf": "missing", "E.pdf": "no manifest row"}


def test_a_mismatch_lists_the_real_papers_copy_elsewhere_in_the_collection(tmp_path):
    """Sprint 8 retrospective I2: the Asfaw row named 2108.0131 (one digit
    short), its file was another paper, and the F60 report said the real
    paper was never downloaded; 2108.01311 was in `Workforce`. A mismatch
    now lists every copy of the row's id, the short id's completions and
    the stamped id, anywhere under the root. Proven to fail by injection,
    2026-10-13: with local_copies matching exact names only, `copies` was
    missing the Workforce file and this test went red."""
    year, other = tmp_path / "2021", tmp_path / "Workforce"
    year.mkdir()
    other.mkdir()
    (year / "manifest.tsv").write_text("file\tarxiv_id\turl\ttitle\nAsfaw__2108.0131.pdf\t2108.0131\tu\tAsfaw\n",
                                       encoding="utf-8")
    (year / "Asfaw__2108.0131.pdf").write_bytes(b"%PDF")
    (other / "Asfaw-et-al__2108.01311.pdf").write_bytes(b"%PDF")
    rows = _mod().check(tmp_path, read=lambda p: "arXiv:2108.00131v2 [cs.LG]")
    (row,) = rows
    assert row["cls"] == "mismatch"
    assert "Workforce/Asfaw-et-al__2108.01311.pdf" in row["copies"]


def test_local_copies_completes_only_a_short_new_style_id(tmp_path):
    from store.recheck import local_copies
    (tmp_path / "a__2108.01311.pdf").write_bytes(b"%PDF")
    (tmp_path / "b__0801.12341.pdf").write_bytes(b"%PDF")
    assert [p.name for p in local_copies("2108.0131", tmp_path)] == ["a__2108.01311.pdf"]
    assert local_copies("0801.1234", tmp_path) == []  # 2008: four digits was the full length
    assert local_copies("2108.01311", tmp_path)[0].name == "a__2108.01311.pdf"
