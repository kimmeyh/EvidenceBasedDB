"""F115 (Sprint 15 Task F): text from page images. The engine runs in its own virtual environment (store.ocr), which
CI does not have, so these tests fake the worker; the one test that runs RapidOCR on udaru's real pages is
live_store."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from store import ocr, quotes

UDARU = (r"D:\Data\Harold\EvidenceBasedDB\Papers\QML Quantum Machine Learning For Credit Risk -A Next-Generation "
         r"Approach To Risk Assessment 202511.pdf")


def test_a_thin_page_is_found_and_read_and_a_missing_engine_is_never_silence(tmp_path, monkeypatch):
    """A page with fewer than TEXT_FLOOR visible characters is the one sent to OCR; a source that needs OCR when
    the engine is missing raises, so an image-only page is never read as empty without a flag. Proven to fail by
    injection, 2026-11-01: with _run_worker returning an empty result when the engine was missing, the page came
    back empty and nothing was raised; with TEXT_FLOOR at 0, no page was thin."""
    monkeypatch.setattr(quotes, "_pdftotext", lambda path, layout: "a full page of text, " * 4 + "\fx\f\f")
    monkeypatch.setattr(ocr, "page_count", lambda path: 3)
    assert ocr.thin_pages("any.pdf") == [2, 3]
    monkeypatch.setenv(ocr.OCR_PYTHON_ENV, str(tmp_path / "no-python.exe"))
    monkeypatch.setattr(ocr, "_cache", lambda path, kind, pages: None)
    monkeypatch.setattr(ocr.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    with pytest.raises(ocr.OcrUnavailable, match="not installed"):
        ocr.ocr_pages("any.pdf")


def test_ocr_text_is_cached_by_file_and_engine_and_named_in_provenance(tmp_path, monkeypatch):
    """The worker's text is kept page by page with the engine that read it, and a second read comes from the cache.
    Proven to fail by injection, 2026-11-01: with the cache write removed, the worker ran twice."""
    source = tmp_path / "s.pdf"
    source.write_bytes(b"%PDF fake")
    monkeypatch.setattr(ocr, "thin_pages", lambda path: [2])
    monkeypatch.setattr(ocr, "_tool", lambda: "t")
    monkeypatch.setattr(ocr, "text_cache_dir", lambda: tmp_path / "text_cache")
    monkeypatch.setattr(ocr.subprocess, "run", lambda *a, **k: None)  # pdftoppm
    calls = []
    engine = {"rapidocr": "3.10.0", "onnxruntime": "1.31.1", "models": {"PP-OCRv6_rec_small.onnx": "ab" * 32}}

    def worker(images):
        calls.append(images)
        return {"engine": engine, "pages": [{"image": images[0], "text": "Quantum Maçhine Learning"}]}

    monkeypatch.setattr(ocr, "_run_worker", worker)
    first = ocr.ocr_pages(str(source))
    assert first.pages == {2: "Quantum Maçhine Learning"} and len(calls) == 1
    assert ocr.ocr_pages(str(source)) == first and len(calls) == 1
    assert ocr.provenance(first) == ("OCR of page images (pages [2]) by RapidOCR 3.10.0 on ONNX Runtime 1.31.1 "
                                     "(PP-OCRv6_rec_small.onnx SHA-256 abababababab), rendered by pdftoppm at 200 dpi")


def test_a_changed_page_set_reads_again_and_a_number_box_survives(tmp_path, monkeypatch):
    """Fresh-eyes review of Task F: the cache was keyed without the pages read, so a page made thin later (a new
    TEXT_FLOOR, a new pdftotext) was served from a cache that lacked it, as empty; and the OCR boxes were joined by
    line, so `plain` dropped a box holding only a number (a table cell). Proven to fail by injection, 2026-11-01:
    with the page list out of the cache key and the page check out of _read, the second read did not run the worker;
    with one_line returning its text unchanged, "92" was lost."""
    source = tmp_path / "s.pdf"
    source.write_bytes(b"%PDF fake")
    monkeypatch.setattr(ocr, "_tool", lambda: "t")
    monkeypatch.setattr(ocr, "text_cache_dir", lambda: tmp_path / "text_cache")
    monkeypatch.setattr(ocr.subprocess, "run", lambda *a, **k: None)
    calls = []

    def worker(images):
        calls.append(images)
        return {"engine": {}, "pages": [{"image": i, "text": "Accuracy\n92\nModel A"} for i in images]}

    monkeypatch.setattr(ocr, "_run_worker", worker)
    monkeypatch.setattr(ocr, "thin_pages", lambda path: [2])
    ocr.ocr_pages(str(source))
    monkeypatch.setattr(ocr, "thin_pages", lambda path: [2, 5])
    again = ocr.ocr_pages(str(source))
    assert len(calls) == 2 and sorted(again.pages) == [2, 5]
    assert "Accuracy 92" in quotes.plain(again.pages[5])


def test_a_quote_found_only_in_ocr_text_is_named(monkeypatch):
    """The quote check reads OCR text after the text layer, and names a quote found only there, which must carry
    "OCR" in its anchor. Proven to fail by injection, 2026-11-01: with the OCR text left out of _pdf_text, the OCR
    quote was not in the text; with the layer not compared, the text-layer quote was named too."""
    monkeypatch.setattr(quotes, "_pdftotext", lambda path, layout: "a sentence in the text layer")
    monkeypatch.setattr(ocr, "ocr_pages", lambda path: ocr.OcrText({3: "a sentence read from an image"}, {}))
    quotes._pdf_text.cache_clear()
    try:
        text = quotes._pdf_text("x.pdf")
    finally:
        quotes._pdf_text.cache_clear()
    assert "a sentence read from an image" in text
    cc = '"a sentence in the text layer" (p.1); "a sentence read from an image" (p.3, OCR)'
    assert quotes.ocr_only_quotes(cc, text) == ["a sentence read from an image"]
    assert quotes.ocr_only_quotes('"anything" (Figure 1)', "OCR: anything here") == ["anything"]


@pytest.mark.live_store
def test_a_form_feed_inside_a_page_does_not_make_a_page():
    """Qian et al. 2021's text holds form feeds inside its pages: a split gave 103 parts for 23 pages, and OCR asked
    pdftoppm for page 24 (2026-11-01, the first run over every thin page). Proven to fail by injection the same
    day: with the page count not checked, page 24 and later were listed."""
    path = r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2021\Qian-et-al._2021_The-dilemma-of-quantum-neural-networks__2106.04975.pdf"
    assert ocr.page_count(path) == 23
    assert all(n <= 23 for n in ocr.thin_pages(path))


@pytest.mark.live_store
def test_udarus_page_images_are_read():
    """udaru-2025-qml-credit-risk is ten page images; its title, DOI and abstract come back from RapidOCR, and the
    quote check finds a sentence of its abstract."""
    assert ocr.thin_pages(UDARU) == list(range(1, 11))
    text = ocr.ocr_pages(UDARU)
    assert "Quantum Machine Learning For Credit Risk" in text.pages[1]
    assert "10.63278/jicrcr" in text.pages[1].replace(" ", "")
    assert text.engine["rapidocr"] == "3.10.0"
    assert "Financial sectors are based on credit risk modeling" in quotes.source_text(UDARU)
