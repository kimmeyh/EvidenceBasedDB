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
