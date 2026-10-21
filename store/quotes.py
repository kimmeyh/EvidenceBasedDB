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

Sprint 10 retrospective (2026-10-21). I2: `require_verbatim` returns a
`Verified` record, and the verified write helpers in `store.ingest` refuse a
write without the one that matches it, so the check cannot be forgotten
(Tasks F, G and H forgot it at first apply). I1: `require_edit_basis`
checks the coordinator's own edits to a reader's work, which were wrong four
times in Sprint 10 and caught only by review.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import unicodedata
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Verified:
    """What `require_verbatim` returns: this record's quotes, exactly as
    checked against its source. Made only by `require_verbatim`; the
    verified write helpers compare it with the record they write."""
    record_id: str
    citation_context: str


def require_verbatim(record_id: str, citation_context: str | None, text: str) -> Verified:
    """Refuse an assertion whose quotes are not all in its source, or that
    carries none. Called before the write, so a bad quote never reaches the
    store."""
    if not QUOTE.findall(citation_context or ""):
        raise ValueError(f"{record_id}: no quote in citation_context")
    missing = missing_quotes(citation_context, text)
    if missing:
        raise ValueError(f"{record_id}: not verbatim in its source: {missing[0][:80]!r}"
                         + (f" (and {len(missing) - 1} more)" if len(missing) > 1 else ""))
    return Verified(record_id, citation_context)


# A number with its sign: a minus sign (U+2212) is always a sign; a hyphen
# is one only where it does not follow a letter, digit or point, so
# "0.974-0.976" is a range, while "10^-2" and " -0.5" are negative.
_NUMBER = re.compile(r"(?:(?<![\w.])-)?\d+(?:\.\d+)?")
_THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")
_SUPERSCRIPT = str.maketrans({"⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4", "⁵": "^5", "⁶": "^6",
                              "⁷": "^7", "⁸": "^8", "⁹": "^9", "⁻": "^-"})
_MATH_SIGNS = "√≥≤±×∞≈≠∑∏∫∂<>"


def _fold(text: str) -> str:
    """`plain` without its page-number rule, which would delete a value or
    passage that is only a number (fresh-eyes review, 2026-10-21);
    superscripts become ^n before NFKC can merge "10²" into "102"."""
    text = unicodedata.normalize("NFKC", text.translate(_SUPERSCRIPT))
    for typographic, ascii_form in _TYPOGRAPHIC:
        text = text.replace(typographic, ascii_form)
    return re.sub(r"\s+", " ", text.replace("−", " -"))


def _numbers(text: str) -> set[str]:
    return set(_NUMBER.findall(_THOUSANDS.sub("", text)))


def unsupported_by_basis(value: str, basis: list[str]) -> list[str]:
    """The numbers (with their sign) and math signs in `value` that no
    passage in `basis` holds. A digit inside a word counts ("F2" holds a 2):
    that makes the check weaker, never wrong."""
    joined = _fold(" ".join(basis))
    value = _fold(value)
    return sorted((_numbers(value) - _numbers(joined)) | {s for s in _MATH_SIGNS if s in value and s not in joined})


def require_edit_basis(record_id: str, value: str | None, basis: list[str], text: str,
                       read_from_page: tuple[str, ...] = ()) -> None:
    """Refuse a coordinator edit (a replaced value, a dropped quote, a moved
    context) that names no source passage, names one not verbatim in the
    source, or, for a replaced `value`, states a number or math sign none of
    its passages holds (Sprint 10 retrospective I1).

    `read_from_page` lists what was read from the page image because the
    text layer lost it (the root sign of "R >= sqrt 2" in Sprint 10's F89):
    each item is exempt, and the value itself should say so. It cannot check
    meaning: a wrong word with the right numbers still passes, so reviews
    stay."""
    if not basis:
        raise ValueError(f"{record_id}: a coordinator edit names no source passage")
    missing = [q for q in basis if plain(q) not in text]
    if missing:
        raise ValueError(f"{record_id}: an edit's passage is not verbatim in its source: {missing[0][:80]!r}")
    if value is not None:
        unsupported = [t for t in unsupported_by_basis(value, basis) if t not in read_from_page]
        if unsupported:
            raise ValueError(f"{record_id}: the edited value states {', '.join(unsupported)}, which no named "
                             "passage holds; correct the value, or read it from the page and list it in "
                             "read_from_page")
