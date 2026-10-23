"""F100 (Sprint 12 Task B): the quote checks' PDF text, cached on disk and
across tests, without weakening the CI guard.

Before F100 the harness emptied the in-process text caches before every
test without @pytest.mark.live_store, so no such test could pass on a read
an earlier live test had cached; the price was that every live test
extracted its PDFs again. Now `store.quotes.READ_GUARD` refuses the read
before any cache is consulted, and pdftotext's raw output is kept on disk,
keyed by the file's SHA-256, the layout and pdftotext's version."""
from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import quotes  # noqa: E402
from store.quotes import pdf_text as directly_imported  # noqa: E402


def test_a_cached_read_is_still_refused_without_live_store(monkeypatch):
    """The guard runs before the cache. Proven to fail by injection,
    2026-10-23: with the READ_GUARD check removed from `pdf_text`, the
    stand-in cache answered and the first `pytest.raises` failed. Restored."""
    monkeypatch.setattr(quotes, "_pdf_text", lambda path: "cached text")
    monkeypatch.setattr(quotes, "_html_text", lambda path: "cached text")
    with pytest.raises(FileNotFoundError, match="live_store"):
        quotes.pdf_text(r"D:\somewhere\a.pdf")
    with pytest.raises(FileNotFoundError, match="live_store"):
        directly_imported(r"D:\somewhere\a.pdf")  # as test_f91 and the F91 script import it
    with pytest.raises(FileNotFoundError, match="live_store"):
        quotes.source_text(r"D:\somewhere\a.html")


def _fake_pdftotext(monkeypatch, calls: list):
    def run(cmd, capture_output=True, check=False):
        if cmd[1] == "-v":
            return subprocess.CompletedProcess(cmd, 0, b"", b"pdftotext version 4.00 test")
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, f"text {len(calls)}".encode(), b"")

    monkeypatch.setattr(quotes, "subprocess", types.SimpleNamespace(run=run))
    quotes._pdftotext_version.cache_clear()


def test_the_disk_cache_is_keyed_by_content_and_layout(monkeypatch, tmp_path):
    """Proven to fail by injection, 2026-10-23: with the SHA-256 left out
    of the cache key, the changed file returned the old text. Restored."""
    calls: list = []
    _fake_pdftotext(monkeypatch, calls)
    (tmp_path / "store").mkdir()  # the cache makes text_cache\, never the store folder itself
    monkeypatch.setenv("EBDB_STORE_DIR", str(tmp_path / "store"))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    assert quotes._pdftotext(str(pdf), False) == "text 1"
    assert quotes._pdftotext(str(pdf), False) == "text 1"  # from disk: no second run
    assert quotes._pdftotext(str(pdf), True) == "text 2"  # the other layout is its own entry
    assert len(calls) == 2
    pdf.write_bytes(b"%PDF two")
    assert quotes._pdftotext(str(pdf), False) == "text 3"  # a changed file extracts again
    assert len(list((tmp_path / "store" / "text_cache").glob("*.txt"))) == 3


def test_a_folder_that_cannot_be_written_only_skips_the_cache(monkeypatch, tmp_path):
    calls: list = []
    _fake_pdftotext(monkeypatch, calls)
    blocker = tmp_path / "store"
    blocker.write_text("a file where the store folder would be")
    monkeypatch.setenv("EBDB_STORE_DIR", str(blocker))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    assert quotes._pdftotext(str(pdf), False) == "text 1"
    assert quotes._pdftotext(str(pdf), False) == "text 2"  # no cache, so each call extracts
