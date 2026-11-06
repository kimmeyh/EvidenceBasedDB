"""F134 (Sprint 16 Task C): a table cell that holds only a number is kept for the quote check, and a page number is
still dropped. Neither opens the store or a real PDF here."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from store import ocr, quotes

ROOT = Path(__file__).resolve().parents[1]

# pdftotext without layout: page 1 ends "...the end of a sentence" with its page number 12 on the page's last line;
# page 2 opens with its running page number 13, then a table whose cells each sit on a line of their own.
RAW = ("the end of a sentence\n12\n\f13\nthat runs onto the next page.\nTable XIII Nodes\n881\n160\nChain length\n"
       "Table XIV\n")
LAYOUT = "the end of a sentence\n 12\nthat runs onto the next page.\n\fTable XIII Nodes   881   160   Chain length\n"


def _text(monkeypatch, raw=RAW, layout="") -> str:
    monkeypatch.setattr(quotes, "_pdftotext", lambda path, lay: layout if lay else raw)
    monkeypatch.setattr(ocr, "ocr_pages", lambda path: ocr.OcrText({}, {}))
    quotes._pdf_text.cache_clear()
    try:
        return quotes._pdf_text("x.pdf")
    finally:
        quotes._pdf_text.cache_clear()


def test_a_number_only_cell_is_found_and_a_page_number_is_still_dropped(monkeypatch):
    """Proven to fail by injection, 2026-11-06: with the third form left out of `_pdf_text`, the quote through the
    table's cells was not found; with number-only lines kept in every form (`plain`'s rule and `cells_text`'s edge
    rule both removed), the quote across the page break was not found; with the third form keeping a page's first and last number lines (fresh-eyes review of Tasks C and
    D), the quote that carries the page numbers was found."""
    text = _text(monkeypatch)
    across_the_break = quotes.plain("the end of a sentence that runs onto the next page.")
    through_the_cells = quotes.plain("Table XIII Nodes 881 160 Chain length")
    assert across_the_break in text
    assert through_the_cells in text
    assert "sentence 12" not in text and "13 that runs" not in text  # a page number is in no form
    assert "sentence 12 that" not in quotes.plain(RAW)  # plain() itself still drops the page number
    quotes.require_verbatim("t", f'"{through_the_cells}" (Table XIII, p.2)', text, value="881 nodes")


def test_the_page_check_finds_a_cell_on_its_page(monkeypatch):
    """The reader check's page check holds the same form. Proven to fail by injection, 2026-11-06: with the
    number-only form left out of `page_text`, the cell quote was named as off its page."""
    spec = importlib.util.spec_from_file_location("sprint13_g_check", ROOT / "scripts" / "sprint13_g_check.py")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    monkeypatch.setattr(check, "page_texts", lambda path: RAW.split("\f"))
    monkeypatch.setattr(check, "page_layouts", lambda path: ["", ""])
    monkeypatch.setattr(check, "_ocr", lambda path: {})
    a = {"anchor": "Table XIII, p.2", "quotes": ["Table XIII Nodes 881 160 Chain length"]}
    text = quotes.plain(RAW, keep_numbers=True)
    assert check.page_problems("t", a, "x.pdf", text) == []
    assert check.page_problems("t", {**a, "anchor": "p.4"}, "x.pdf", text)  # not on page 4 or 5
