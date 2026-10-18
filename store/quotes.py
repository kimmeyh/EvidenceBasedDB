"""The verbatim-quote check: one normalizer, one source reader, one check
(Sprint 9 retrospective I3, 2026-10-17).

Until Sprint 9 these lived in a test module (tests/test_f45_dirac3_reading.py)
that six other tests imported, so a quote was first compared with its source
AFTER it was in the store, and the normalizer grew one character at a time
as sources arrived: the curly quotes and fi/fl in Sprint 7, the ff/ffi/ffl
ligatures in Sprint 9, with an en space (U+2002) fixed by hand in the quote
itself. `plain` now applies Unicode NFKC first, which folds every
compatibility form (ligatures, en and em spaces, the no-break space, full-width
letters) in one step, then makes the typographic quotes plain. NFKC leaves
the curly quotes alone, so that mapping stays.

A reading script calls `require_verbatim` on every assertion BEFORE it writes;
the tests stay as the backstop on what is already in the store.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import unicodedata
from functools import lru_cache
from pathlib import Path

# A quote inside citation_context: "<quote>" (<anchor>), joined by "; ".
QUOTE = re.compile(r'(?:^|; )"(.+?)" \(')

_TYPOGRAPHIC = (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("​", ""))


def plain(text: str) -> str:
    """Compatibility forms folded (NFKC), typographic quotes made plain,
    page-number lines dropped (a quote may cross a page break), whitespace
    collapsed. Applied to both sides of every comparison."""
    text = unicodedata.normalize("NFKC", text)
    for typographic, ascii_form in _TYPOGRAPHIC:
        text = text.replace(typographic, ascii_form)
    text = re.sub(r"(?m)^\s*\d+\s*$", " ", text)
    return re.sub(r"\s+", " ", text)


@lru_cache(maxsize=None)
def pdf_text(path: str) -> str:
    """Both pdftotext layouts, joined: a quote may survive one and not the other."""
    modes = (["pdftotext", "-enc", "UTF-8", path, "-"], ["pdftotext", "-enc", "UTF-8", "-layout", path, "-"])
    return " || ".join(plain(subprocess.run(m, capture_output=True, check=True).stdout.decode("utf-8", "replace"))
                       for m in modes)


@lru_cache(maxsize=None)
def html_text(path: str) -> str:
    page = Path(path).read_text(encoding="utf-8", errors="replace")
    page = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    return plain(html.unescape(re.sub(r"<[^>]+>", " ", page)))


def source_text(path: str) -> str:
    """The plain text of a local source: a PDF, a saved page, a notebook's
    cells, or any other text file as it is."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return pdf_text(path)
    if suffix in (".html", ".htm"):
        return html_text(path)
    raw = p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".ipynb":
        raw = "\n".join("".join(c.get("source", [])) for c in json.loads(raw)["cells"])
    return plain(raw)


def missing_quotes(citation_context: str | None, text: str) -> list[str]:
    """The quotes in `citation_context` that are not verbatim in `text`
    (already plain)."""
    return [q for q in QUOTE.findall(citation_context or "") if plain(q) not in text]


def require_verbatim(record_id: str, citation_context: str | None, text: str) -> None:
    """Refuse an assertion whose quotes are not all in its source, or that
    carries none. Called before the write, so a bad quote never reaches the
    store."""
    if not QUOTE.findall(citation_context or ""):
        raise ValueError(f"{record_id}: no quote in citation_context")
    missing = missing_quotes(citation_context, text)
    if missing:
        raise ValueError(f"{record_id}: not verbatim in its source: {missing[0][:80]!r}"
                         + (f" (and {len(missing) - 1} more)" if len(missing) > 1 else ""))
