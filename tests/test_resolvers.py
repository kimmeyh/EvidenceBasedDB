"""Tests for store/resolvers.py (Sprint 1 Task G).

CLAUDE.md standing rule: determinate facts are computed, never stored.
These tests prove the resolver actually reads live content rather than
returning a cached/hardcoded number -- per this repository's guard-
discipline standard, a resolver that always returns the same value
regardless of its source is indistinguishable from a stored constant and
worse, because it looks like it isn't one.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store.resolvers import consumer_amendment_count  # noqa: E402


@pytest.mark.live_store  # reads a sibling repository; found by the I7 guard (2026-10-18)
def test_resolves_against_the_real_consumer_repository_if_present():
    """Sanity check against the actual live document. Skips rather than
    fails if the consumer repository is not present on this machine --
    this resolver is inherently environment-dependent, and that is the
    point: it has no fallback value to fall back to."""
    from store.resolvers import CONSUMER_REPO_PREREGISTRATION

    if not CONSUMER_REPO_PREREGISTRATION.exists():
        pytest.skip("consumer repository not present on this machine")
    count = consumer_amendment_count()
    assert count > 0


def test_raises_when_the_consumer_repository_is_absent():
    """No fallback value -- a resolver that silently returns 0 or a
    remembered number on a missing source is the same defect class this
    resolver exists to avoid (A19: the amendment count changed and had to
    be corrected in every document that named it)."""
    missing_path = Path(tempfile.gettempdir()) / "definitely-does-not-exist-preregistration.md"
    assert not missing_path.exists()
    with pytest.raises(FileNotFoundError):
        consumer_amendment_count(path=missing_path)


def test_counts_the_actual_amendment_lines_in_a_synthetic_document(tmp_path):
    """Proves the resolver COUNTS rather than returns a constant: three
    synthetic amendment lines resolve to 3, not to whatever the real
    consumer repository currently holds."""
    doc = tmp_path / "PREREGISTRATION.md"
    doc.write_text(
        "# Preregistration\n\n"
        "## Amendment log\n\n"
        "- 2026-01-01 (A1): First amendment.\n"
        "- 2026-01-02 (A2): Second amendment.\n"
        "- 2026-01-03 (A3): Third amendment.\n",
        encoding="utf-8",
    )
    assert consumer_amendment_count(path=doc) == 3


def test_adding_a_fourth_amendment_line_changes_the_count(tmp_path):
    """The resolver TRACKS the source, verified by injection: a document
    edited to add one more amendment line must resolve to one more, not
    the same cached number."""
    doc = tmp_path / "PREREGISTRATION.md"
    doc.write_text(
        "## Amendment log\n\n"
        "- 2026-01-01 (A1): First.\n"
        "- 2026-01-02 (A2): Second.\n",
        encoding="utf-8",
    )
    before = consumer_amendment_count(path=doc)

    doc.write_text(
        doc.read_text(encoding="utf-8") + "- 2026-01-03 (A3): Third.\n",
        encoding="utf-8",
    )
    after = consumer_amendment_count(path=doc)

    assert after == before + 1


def test_does_not_count_non_amendment_lines(tmp_path):
    """A line that merely MENTIONS an amendment (prose, a reference
    elsewhere in the doc) must not be counted -- only the log's own
    dated-entry format counts."""
    doc = tmp_path / "PREREGISTRATION.md"
    doc.write_text(
        "This document was amended after A1 and A2 were recorded.\n"
        "See also: amendment A3 discussed in the retrospective.\n"
        "## Amendment log\n\n"
        "- 2026-01-01 (A1): The only real entry.\n",
        encoding="utf-8",
    )
    assert consumer_amendment_count(path=doc) == 1
