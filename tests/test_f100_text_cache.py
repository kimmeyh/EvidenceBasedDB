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

REAL_VERSION = quotes._pdftotext_version


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


def _fake_pdftotext(monkeypatch, calls: list, version: str = "fake pdftotext 9.99"):
    def run(cmd, capture_output=True, check=False):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, f"text {len(calls)}\r\n".encode(), b"")

    monkeypatch.setattr(quotes, "subprocess", types.SimpleNamespace(run=run))
    # Patched, never cache-cleared and refilled: a fake version left in the
    # lru_cache keyed every later live quote check (review of fdedff9).
    monkeypatch.setattr(quotes, "_pdftotext_version", lambda: version)


def test_the_disk_cache_is_keyed_by_content_and_layout(monkeypatch, tmp_path):
    """Proven to fail by injection, 2026-10-23: with the SHA-256 left out
    of the cache key, the changed file returned the old text. Restored."""
    calls: list = []
    _fake_pdftotext(monkeypatch, calls)
    monkeypatch.setenv("EBDB_TEXT_CACHE_DIR", str(tmp_path / "text_cache"))  # made by the first write (F136)
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"  # from disk, byte for byte: no second run
    assert quotes._pdftotext(str(pdf), True) == "text 2\r\n"  # the other layout is its own entry
    assert len(calls) == 2
    pdf.write_bytes(b"%PDF two")
    assert quotes._pdftotext(str(pdf), False) == "text 3\r\n"  # a changed file extracts again
    assert len(list((tmp_path / "text_cache").glob("*.txt"))) == 3
    assert not list((tmp_path / "text_cache").glob("*.partial"))


def test_a_store_copy_elsewhere_reads_the_same_cache(monkeypatch, tmp_path):
    """F136 (Sprint 16 Task A; team lead, 2026-11-05: "reading the PDF should ever be done once per PDF, ever").
    Sprint 15's trial on a store copy (EBDB_STORE_DIR pointed at the copy) found an empty cache and extracted 894
    PDFs again. The cache folder no longer follows EBDB_STORE_DIR. Proven to fail by injection, 2026-11-06: with
    text_cache_dir() returning store_dir() / "text_cache", the copy extracted again (2 calls) and the default
    folder named the copy's. Restored."""
    import store
    calls: list = []
    _fake_pdftotext(monkeypatch, calls)
    monkeypatch.setenv("EBDB_TEXT_CACHE_DIR", str(tmp_path / "text_cache"))
    monkeypatch.setenv("EBDB_STORE_DIR", str(tmp_path / "live"))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"
    monkeypatch.setenv("EBDB_STORE_DIR", str(tmp_path / "trial copy"))
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"  # the copy reads the cache: nothing extracted
    assert len(calls) == 1
    # Without its own variable the cache is the live store's folder, wherever EBDB_STORE_DIR points
    monkeypatch.delenv("EBDB_TEXT_CACHE_DIR")
    monkeypatch.setattr(store, "_on_windows", lambda: True)
    assert store.text_cache_dir() == Path(store.DEFAULT_STORE_DIR) / "text_cache"


def test_a_new_pdftotext_extracts_again(monkeypatch, tmp_path):
    """Proven to fail by injection, 2026-10-23: with the version left out
    of the cache key, the second version returned the first one's text.
    Restored."""
    monkeypatch.setenv("EBDB_TEXT_CACHE_DIR", str(tmp_path / "text_cache"))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    calls: list = []
    _fake_pdftotext(monkeypatch, calls, "fake pdftotext 4.00")
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"
    _fake_pdftotext(monkeypatch, calls, "fake pdftotext 4.05")
    assert quotes._pdftotext(str(pdf), False) == "text 2\r\n"
    assert len(calls) == 2


def test_the_real_version_is_never_left_faked():
    """The suite-wide half of the version leak: after the fakes above,
    the module's version reader is the real one again (pdftotext itself
    cannot run in an unmarked test). The fakes patch the reader and never
    run the real one, so its cache holds only what the real binary said.
    Proven to fail by injection, 2026-10-23: with the fake put back to
    clearing and refilling the real reader's cache, this test named the
    fake version. Restored."""
    assert quotes._pdftotext_version is REAL_VERSION
    if REAL_VERSION.cache_info().currsize:  # a cached value is read, never made here
        # Every fake version above starts "fake": the reader keeps only the first three words.
        assert "fake" not in REAL_VERSION()


def test_a_folder_that_cannot_be_written_only_skips_the_cache(monkeypatch, tmp_path):
    calls: list = []
    _fake_pdftotext(monkeypatch, calls)
    blocker = tmp_path / "text_cache"
    blocker.write_text("a file where the cache folder would be")
    monkeypatch.setenv("EBDB_TEXT_CACHE_DIR", str(blocker))
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF one")
    assert quotes._pdftotext(str(pdf), False) == "text 1\r\n"
    assert quotes._pdftotext(str(pdf), False) == "text 2\r\n"  # no cache, so each call extracts
