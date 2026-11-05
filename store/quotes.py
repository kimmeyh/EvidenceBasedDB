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

import hashlib
import html
import json
import re
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from store import store_dir

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


# Set by the test harness for a test without @pytest.mark.live_store: called
# with the path before any read, cached or not, so a read an earlier live
# test cached cannot hide that CI has no such file (Sprint 9 retrospective
# I7). Until F100 (Sprint 12) the harness emptied the caches instead, which
# made every live test extract its PDFs again.
READ_GUARD = None


def pdf_text(path: str) -> str:
    """Both pdftotext layouts, joined: a quote may survive one and not the other."""
    if READ_GUARD is not None:
        READ_GUARD(path)
    return _pdf_text(path)


OCR_MARK = " || OCR: "


@lru_cache(maxsize=None)
def _pdf_text(path: str) -> str:
    """Both text layers; then, after OCR_MARK, the OCR text of the pages whose text layer is empty or nearly empty
    (F115, Sprint 15 Task F), so a quote a reader took from such a page is checked against what the engine read."""
    from store.ocr import ocr_pages
    text = " || ".join(plain(_pdftotext(path, layout)) for layout in (False, True))
    ocr = ocr_pages(path)
    return text + (OCR_MARK + plain(" ".join(ocr.pages[n] for n in sorted(ocr.pages))) if ocr.pages else "")


def ocr_only_quotes(citation_context: str | None, text: str) -> list[str]:
    """The quotes found only in the OCR part of a source's text, not in its text layer: each must say "OCR" in its
    anchor (F115). An image file's text is all OCR."""
    layer, _, ocr = text.partition(OCR_MARK)
    if text.startswith("OCR: "):
        layer, ocr = "", text
    out = []
    for quote in QUOTE.findall(citation_context or ""):
        q = plain(quote)
        if q not in layer and q in ocr:
            out.append(quote)
    return out


@lru_cache(maxsize=1)
def _pdftotext_version() -> str:
    out = subprocess.run(["pdftotext", "-v"], capture_output=True)
    return " ".join((out.stdout + out.stderr).decode("utf-8", "replace").split()[:3])


def _pdftotext(path: str, layout: bool) -> str:
    """pdftotext's raw output, through a disk cache (F100, Sprint 12): the
    suite extracted the same PDFs on every run, about 0.6 s a layout, 13 of
    its 13 minutes in quote checks. The key is the file's SHA-256, the
    layout and pdftotext's version, so a changed file or a new pdftotext
    extracts again; `plain` is applied after the cache, so a change to it
    is never hidden. The cache lives in the store folder (`text_cache\\`),
    outside git; a folder that cannot be written is simply not used. The
    text is stored as bytes, so it comes back exactly as extracted, and a
    file that does not decode is extracted again."""
    cmd = ["pdftotext", "-enc", "UTF-8", *(["-layout"] if layout else []), path, "-"]
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    # The options as well as the version: an option added later extracts again (review of fdedff9).
    tool = hashlib.sha256(" ".join([_pdftotext_version(), *cmd[:-2]]).encode()).hexdigest()[:12]
    name = f"{digest}-{'layout' if layout else 'plain'}-{tool}.txt"
    try:
        return (store_dir() / "text_cache" / name).read_bytes().decode("utf-8")
    except (OSError, RuntimeError, UnicodeDecodeError):  # RuntimeError: no store folder off Windows
        pass
    text = subprocess.run(cmd, capture_output=True, check=True).stdout.decode("utf-8", "replace")
    try:
        cached = store_dir() / "text_cache" / name
        cached.parent.mkdir(exist_ok=True)
        # A name of its own per writer, so two processes never share a half-written file.
        with tempfile.NamedTemporaryFile(dir=cached.parent, suffix=".partial", delete=False) as partial:
            partial.write(text.encode("utf-8"))
        Path(partial.name).replace(cached)
    except (OSError, RuntimeError):
        pass
    return text


def html_text(path: str) -> str:
    if READ_GUARD is not None:
        READ_GUARD(path)
    return _html_text(path)


@lru_cache(maxsize=None)
def _html_text(path: str) -> str:
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
    from store.ocr import IMAGE_SUFFIXES, image_text
    if suffix in IMAGE_SUFFIXES:  # F115: a picture file is all OCR text
        if READ_GUARD is not None:
            READ_GUARD(path)
        return "OCR: " + plain(image_text(path).pages[1])
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
    """What `require_verbatim` returns: this record's quotes and value,
    exactly as checked against its source. Made only by `require_verbatim`;
    the verified write helpers compare it with the record they write, so a
    check run without the value cannot license a write."""
    record_id: str
    citation_context: str
    value: str | None


def stray_quote_marks(citation_context: str) -> list[int]:
    """The positions of quote marks outside every parsed quote and its
    anchor (Sprint 11 retrospective I1a). A quote QUOTE does not parse is
    never checked: Sprint 11's F92 wrote `;"On which problem class?"` with
    no space after the semicolon, and a Sprint 7 Cyc quote stops at its
    inner `"split" (`. A quote mark inside a quote, or inside its anchor
    (`(p.31; the source's spelling "statisitics" kept)`), is not stray."""
    covered: set[int] = set()
    for m in QUOTE.finditer(citation_context):
        covered.update(range(m.start(), m.end()))
        depth, i = 1, m.end()
        while i < len(citation_context) and depth:
            depth += {"(": 1, ")": -1}.get(citation_context[i], 0)
            covered.add(i)
            i += 1
    return [i for i, ch in enumerate(citation_context) if ch == '"' and i not in covered]


# A number joined to a label ("Figures 3 and 4", "Figure 7C and 7D") is part of it only when no word follows it: in
# "Figure 3, 4 qubits" the 4 is a count, not a label (fresh-eyes review, 2026-11-04)
FIGURE_LABEL = (r"(?:Figures?|Figs?\.|Tables?) ?\d+[A-Za-z]?"
                r"(?:\s*(?:,|and|to|[-–])\s*\d+[A-Za-z]?(?![A-Za-z\d]|\s*[A-Za-z]))*")


def unquoted_figures(value: str, citation_context: str, read_from_page: tuple[str, ...] = ()) -> list[str]:
    """The figures in `value` that none of its own quotes holds. Moved from
    Sprint 11's reading script, whose 649 values passed it. Lighter than
    `unsupported_by_basis`, which checks a coordinator's replaced value
    with its signs: a digit inside a word, or closing a hyphenated name
    (LimiX-2, Dirac-3), is a name here, not a figure, and so is a phase
    ("Phase 2's simulator", in F92's and F93's values)."""
    quoted = " ".join(plain(q) for q in QUOTE.findall(citation_context))
    value = re.sub(r"\bPhase \d+\b", "Phase", plain(value))
    # a figure or table label ("Read from Figure 3: ...", "than in Figure 4(a)") is a name, while the same number
    # elsewhere in the value still needs its quote (fresh-eyes review, 2026-11-02: excusing "3" everywhere let
    # "at depth 3" stand unquoted)
    value = re.sub(rf"\b{FIGURE_LABEL}", "Figure", value)
    return [n for n in re.findall(r"(?<![\w.,])(?<![A-Za-z]-)\d+(?:[.,]\d+)?", value)
            if not re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", quoted) and n not in read_from_page]


def read_from_figure(value: str) -> tuple[str, ...]:
    """The numbers a value read by eye from a plot (F116, Sprint 15 Task G): each one written "about N", the only
    form in which a figure-read number may stand without a quote that holds it. A figure's label is a name, which
    unquoted_figures leaves out."""
    return tuple(re.findall(r"\babout [-−]?(\d+(?:[.,]\d+)?)", plain(value)))


def require_verbatim(record_id: str, citation_context: str | None, text: str, value: str | None = None,
                     read_from_page: tuple[str, ...] = ()) -> Verified:
    """Refuse an assertion whose quotes are not all in its source, that
    carries none, that has a quote mark the quote pattern does not parse,
    or whose `value` states a figure its own quotes do not hold. Called
    before the write, so a bad quote never reaches the store.

    Sprint 11 retrospective I1a (2026-10-23): the last two checks lived only
    in one reading script's `verify()`, so the other scripts skipped them.
    The write helpers refuse a `Verified` whose value is not the record's,
    so the figure check cannot be left out by omitting `value`.
    `read_from_page` lists figures read from the page image, as in
    `require_edit_basis`."""
    if not QUOTE.findall(citation_context or ""):
        raise ValueError(f"{record_id}: no quote in citation_context")
    if stray_quote_marks(citation_context):
        raise ValueError(f"{record_id}: a quote mark the quote pattern does not parse, so its quote is never "
                         "checked (separate quotes with '; ' and end each with ' (anchor)')")
    missing = missing_quotes(citation_context, text)
    if missing:
        raise ValueError(f"{record_id}: not verbatim in its source: {missing[0][:80]!r}"
                         + (f" (and {len(missing) - 1} more)" if len(missing) > 1 else ""))
    if value is not None and (figures := unquoted_figures(value, citation_context, read_from_page)):
        raise ValueError(f"{record_id}: the value states {', '.join(figures)}, which its own quotes do not hold")
    return Verified(record_id, citation_context, value)


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
