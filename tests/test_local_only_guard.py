"""Sprint 9 retrospective I7 (team lead, 2026-10-18, Q1 = 2): a test without
the live_store marker finds the local-only resources missing on this machine,
as CI does (the guard is in tests/conftest.py).

Proven to fail by injection, 2026-10-18: with `sys.addaudithook` removed from
pytest_configure, the three refusal tests below went red (the sibling read
and the sqlite connect raised nothing, and pdftotext ran). Restored and green
again. A second injection: with @pytest.mark.live_store removed from
tests/test_f79_phase2_inbound.py::test_every_number_in_a_value_is_in_the_source
(one of the three tests that turned CI red from 2026-10-15), that test failed
locally with the I7 message (only after the Windows command-line split was
added: the first run of this injection passed, which is how that gap was
found). A third: with the marker removed from
tests/test_f78_ceiling_reading.py::test_every_number_in_a_paper_value_is_in_the_paper,
it failed with "pdftotext is not available". Restored. A fourth, after the
PR #88 review: with the option-value split removed from the guard,
test_an_unmarked_test_cannot_run_a_command_in_or_naming_a_sibling failed
(--in=PATH ran). Restored."""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import store  # noqa: E402
SIBLING = ROOT.parent / "a-sibling-repository" / "README.md"


def test_an_unmarked_test_cannot_read_a_sibling_repository():
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        SIBLING.read_text(encoding="utf-8")


def test_an_unmarked_test_cannot_open_a_store_outside_the_repository():
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        sqlite3.connect(ROOT.parent / "a-sibling-repository" / "evidence.db")


def test_an_unmarked_test_cannot_run_pdftotext():
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        subprocess.run(["pdftotext", "-v"], capture_output=True)


@pytest.mark.skipif(os.name != "nt", reason="the data folder is a Windows path; on CI it does not exist")
def test_an_unmarked_test_cannot_read_the_data_folder():
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        (Path(str(store.DEFAULT_STORE_DIR.parent)) / "Papers" / "x.pdf").read_bytes()


def test_an_unmarked_test_cannot_run_a_command_in_or_naming_a_sibling(tmp_path):
    """PR #88 review, 2026-10-18: the cwd and argument branches, including
    an option's value (--in=PATH), had no test of their own."""
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        subprocess.run([sys.executable, "-c", "0"], cwd=SIBLING.parent, capture_output=True)
    with pytest.raises(FileNotFoundError, match="retrospective I7"):
        subprocess.run([sys.executable, "-c", "0", f"--in={SIBLING}"], capture_output=True)


def test_an_unmarked_test_still_reads_the_repository_and_temp(tmp_path):
    assert "CLAUDE.md" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    (tmp_path / "x.txt").write_text("ok", encoding="utf-8")
    assert (tmp_path / "x.txt").read_text(encoding="utf-8") == "ok"


@pytest.mark.live_store
def test_a_live_store_test_is_not_refused():
    """The marker lifts the guard: the refusal is gone, so a missing file is
    the operating system's own FileNotFoundError, without the I7 text."""
    with pytest.raises(FileNotFoundError) as err:
        SIBLING.read_text(encoding="utf-8")
    assert "retrospective I7" not in str(err.value)
