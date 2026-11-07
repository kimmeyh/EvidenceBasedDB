"""Text from page images (F115, Sprint 15 Task F).

A page whose text layer is empty or nearly empty gave a reader nothing: udaru-2025-qml-credit-risk is ten page
images, and the team lead marked it unread (2026-10-27). Such a page is now rendered by `pdftoppm` and read by
RapidOCR, a cross-platform engine the team lead chose over Windows' own OCR (2026-11-01: "would prefer a cross
platform OCR ability"). The engine runs in its own virtual environment (`requirements-ocr.txt`), through
`scripts/ocr_worker.py`, because its dependencies would raise the main interpreter's numpy from 1.26 to 2.5.

What it gives:
- `thin_pages(path)`: the pages of a PDF whose text layer holds fewer than TEXT_FLOOR visible characters;
- `ocr_pages(path)`: those pages' OCR text, page by page, with the engine that read them;
- `image_text(path)`: the OCR text of an image file that is a source of its own (not a page of a PDF).

The text is cached in `store.text_cache_dir()` (outside git, one folder for every store copy, F136) as
`pdftotext`'s is: the key is the file's
SHA-256, the render resolution, `pdftoppm`'s version and the engine's pinned versions, so a changed file or engine
reads again. A source that needs OCR when the engine is missing raises OcrUnavailable: an image-only page is never
read as empty without a word.

Grading (team lead, 2026-11-01, plan Q3): OCR text from a page of a stored PDF grades as the text layer does; OCR
text from an image file outside a PDF is HIGH only when another source corroborates the claim, otherwise MEDIUM at
most (`scripts/full_read_apply.py` enforces it). A quote found only in OCR text is marked "OCR" in its anchor.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from store import DEFAULT_DATA_DIR, text_cache_dir

TEXT_FLOOR = 40  # visible characters: a page with fewer has no text layer worth the name
DPI = 200
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp")
OCR_PYTHON_ENV = "EBDB_OCR_PYTHON"
WORKER = Path(__file__).resolve().parents[1] / "scripts" / "ocr_worker.py"
REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements-ocr.txt"


class OcrUnavailable(RuntimeError):
    """A source needs OCR and the engine cannot run."""


@dataclass(frozen=True)
class OcrText:
    pages: dict[int, str]  # page number (1-based; 1 for an image file) -> its OCR text
    engine: dict  # RapidOCR's and ONNX Runtime's versions and each model file's SHA-256, as the worker reported


def engine_python() -> Path:
    """The OCR environment's interpreter: EBDB_OCR_PYTHON, or `ocr-venv` in the data folder. A fixed folder, not
    beside `store_dir()` (F136): its path is part of the OCR cache key, so a store copy elsewhere found neither the
    engine nor its cached text."""
    override = (os.environ.get(OCR_PYTHON_ENV) or "").strip()
    if override:
        return Path(override)
    venv = Path(DEFAULT_DATA_DIR) / "ocr-venv"
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def visible(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def _disk_cached(path: str, kind: str, make):
    """`make()`'s JSON-able result for `path`, kept in the text cache under the file's SHA-256 and `kind` (F140,
    Sprint 17 Task A). The page count and the per-page fallback were kept for the process only, so every test process
    started `pdfinfo` once per PDF: 390 starts and 180 of 230 seconds in one quote test, at 0.3 to 0.6 seconds a
    process start on this machine. A folder that cannot be written is simply not used, as for `_pdftotext`."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    try:
        cached = text_cache_dir() / f"{digest}-{kind}.json"
    except RuntimeError:  # no store folder off Windows
        cached = None
    if cached is not None:
        try:
            return json.loads(cached.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    from store.quotes import CACHE_MISSES
    CACHE_MISSES[kind.split("-")[0]] += 1  # F139's miss count, so a run reports what it extracted
    value = make()
    if cached is not None:
        try:
            cached.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=cached.parent, suffix=".partial",
                                             delete=False) as partial:
                json.dump(value, partial, ensure_ascii=False)
            Path(partial.name).replace(cached)
        except OSError:
            pass
    return value


@lru_cache(maxsize=None)
def page_count(path: str) -> int:
    def run() -> int:
        out = subprocess.run(["pdfinfo", path], capture_output=True, check=True).stdout.decode("utf-8", "replace")
        return int(re.search(r"^Pages:\s+(\d+)", out, re.M)[1])
    return int(_disk_cached(path, "pdfinfo-pages", run))


def page_texts(path: str) -> list[str]:
    """Each page's text layer. pdftotext ends every page with a form feed, but a page's own text may hold one too
    (Qian et al. 2021: 103 parts for 23 pages), so a split that disagrees with pdfinfo's count is replaced by one
    extraction per page. Kept for the process, as `_pdf_text` is (fresh-eyes review of Task F: one pdfinfo per PDF,
    and per quote in the reader check)."""
    return list(_page_texts(path))


def page_layouts(path: str) -> list[str]:
    """Each page's text in pdftotext's -layout mode, split from the cached whole-file extraction the same way
    (F139, Sprint 16 Task B): the reader's check ran one uncached `pdftotext -layout -f -l` per anchor, 58 of its 62
    seconds on a 494-assertion group."""
    return list(_page_texts(path, True))


@lru_cache(maxsize=None)
def _page_texts(path: str, layout: bool = False) -> tuple[str, ...]:
    from store.quotes import _pdftotext
    pages = _pdftotext(path, layout).split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    n = page_count(path)
    if len(pages) != n:
        def per_page() -> list[str]:
            return [subprocess.run(["pdftotext", "-enc", "UTF-8", *(["-layout"] if layout else []), "-f", str(i),
                                    "-l", str(i), path, "-"],
                                   capture_output=True, check=True).stdout.decode("utf-8", "replace")
                    for i in range(1, n + 1)]
        from store.quotes import _pdftotext_version  # the extraction's tool is part of the key, as for `_pdftotext`
        tool = hashlib.sha256(_pdftotext_version().encode()).hexdigest()[:12]
        pages = _disk_cached(path, f"pages-{'layout' if layout else 'plain'}-{tool}", per_page)
    return tuple(pages)


def one_line(text: str) -> str:
    """OCR text with its boxes joined by spaces: RapidOCR gives each box its own line, and `quotes.plain` drops a
    line that holds only a number (a page number), which would drop a table cell or an axis tick (fresh-eyes review
    of Task F)."""
    return " ".join(text.splitlines())


def thin_pages(path: str) -> list[int]:
    """The 1-based pages of a PDF whose text layer holds fewer than TEXT_FLOOR visible characters."""
    return [i + 1 for i, t in enumerate(page_texts(path)) if visible(t) < TEXT_FLOOR]


@lru_cache(maxsize=1)
def _tool() -> str:
    """The render and the engine, as a short key: a change to either reads every page again."""
    out = subprocess.run(["pdftoppm", "-v"], capture_output=True)
    version = " ".join((out.stdout + out.stderr).decode("utf-8", "replace").split()[:3])
    pins = [line.strip() for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]
    worker = hashlib.sha256(WORKER.read_bytes()).hexdigest()  # a change to the worker reads again (review of Task F)
    return hashlib.sha256(" ".join([version, f"{DPI}dpi", *pins, worker, str(engine_python())]).encode()).hexdigest()[:12]


def _cache(path: str, kind: str, pages: list[int]) -> Path | None:
    """The key holds the pages read: a change to TEXT_FLOOR or to pdftotext that makes another page thin reads again,
    never serves a cache that lacks the page (fresh-eyes review of Task F)."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    which = hashlib.sha256(",".join(map(str, pages)).encode()).hexdigest()[:8]
    try:
        return text_cache_dir() / f"{digest}-{kind}-{_tool()}-{which}.json"
    except RuntimeError:  # no store folder off Windows
        return None


def _run_worker(images: list[str]) -> dict:
    python = engine_python()
    if not python.exists():
        raise OcrUnavailable(f"the OCR engine is not installed at {python}; install it from requirements-ocr.txt "
                             f"or set {OCR_PYTHON_ENV}")
    done = subprocess.run([str(python), "-I", str(WORKER), *images], capture_output=True)
    if done.returncode != 0:
        raise OcrUnavailable(f"the OCR worker exited {done.returncode}: "
                             f"{done.stderr.decode('utf-8', 'replace')[-600:]}")
    return json.loads(done.stdout.decode("utf-8"))


def _read(path: str, kind: str, pages: list[int]) -> OcrText:
    cached = _cache(path, kind, pages)
    if cached is not None:
        try:
            body = json.loads(cached.read_text(encoding="utf-8"))
            text = OcrText({int(k): one_line(v) for k, v in body["pages"].items()}, body["engine"])
            if sorted(text.pages) == sorted(pages):
                return text
        except (OSError, ValueError, KeyError):
            pass
    from store.quotes import CACHE_MISSES
    CACHE_MISSES["ocr"] += 1  # F139
    with tempfile.TemporaryDirectory() as tmp:
        if kind == "image":
            images = [path]
        else:
            images = []
            for n in pages:
                out = Path(tmp) / f"p{n}"
                subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(n), "-l", str(n), "-png", "-singlefile",
                                path, str(out)], capture_output=True, check=True)
                images.append(f"{out}.png")
        body = _run_worker(images)
    result = OcrText({n: page["text"] for n, page in zip(pages, body["pages"])}, body["engine"])
    if cached is not None:
        try:
            cached.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=cached.parent, suffix=".partial",
                                             delete=False) as partial:
                json.dump({"pages": result.pages, "engine": result.engine, "dpi": DPI}, partial, ensure_ascii=False)
            Path(partial.name).replace(cached)
        except OSError:
            pass
    return OcrText({n: one_line(t) for n, t in result.pages.items()}, result.engine)


def ocr_pages(path: str) -> OcrText:
    """The OCR text of a PDF's thin pages; empty when it has none, and then the engine is never started."""
    pages = thin_pages(path)
    return _read(path, "ocr", pages) if pages else OcrText({}, {})


def image_text(path: str) -> OcrText:
    """The OCR text of an image file that is a source of its own."""
    return _read(path, "image", [1])


def provenance(text: OcrText, pages: list[int] | None = None) -> str:
    """The engine that read the pages, in words a record's evidence can carry."""
    e = text.engine
    models = ", ".join(f"{name} SHA-256 {sha[:12]}" for name, sha in sorted(e.get("models", {}).items()))
    which = pages if pages is not None else sorted(text.pages)
    return (f"OCR of page images (pages {which}) by RapidOCR {e.get('rapidocr')} on ONNX Runtime "
            f"{e.get('onnxruntime')} ({models}), rendered by pdftoppm at {DPI} dpi")
