"""Sprint 16 Task F: a group's review texts are written by `f117_review.py items`, in the form REVIEW_PROMPT.md
describes (Sprint 15 wrote them by hand; checked byte for byte against three of those on 2026-11-06)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from store import ocr

ROOT = Path(__file__).resolve().parents[1]


def _review():
    spec = importlib.util.spec_from_file_location("f117_review", ROOT / "scripts" / "f117_review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_thin_page_is_replaced_by_its_ocr_text_and_an_existing_text_is_kept(tmp_path, monkeypatch):
    """Proven to fail by injection, 2026-11-06: with the OCR branch removed from `paper_text`, page 2 kept its empty
    text layer."""
    r = _review()
    monkeypatch.setattr(ocr, "page_texts", lambda path: ["page one\n", "", "page three\n"])
    monkeypatch.setattr(ocr, "ocr_pages", lambda path: ocr.OcrText({2: "read by OCR"}, {}))
    assert r.paper_text("x.pdf") == "page one\n\f[OCR text of page 2]\nread by OCR\fpage three\n"
    monkeypatch.setattr(r, "TEXTS", tmp_path)
    monkeypatch.setattr(r, "papers", lambda g: [{"record_id": "a", "file": "x.pdf"}, {"record_id": "b", "file": "y"}])
    (tmp_path / "b.txt").write_text("already read", encoding="utf-8")
    assert r.write_texts("g1") == ["a.txt"]
    assert (tmp_path / "b.txt").read_text(encoding="utf-8") == "already read"
    assert json.dumps((tmp_path / "a.txt").read_text(encoding="utf-8")).count("OCR text of page 2") == 1
