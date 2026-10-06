"""Shared test setup.

Sprint 6 retrospective I1 (2026-10-05): arXiv pacing keeps ONE clock per
process (`store.citations._last_arxiv_request`), so a test that sends an
arXiv request would otherwise make the next test wait or measure against
it. Each test starts with no arXiv request on record.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import citations  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_arxiv_clock(monkeypatch):
    monkeypatch.setattr(citations, "_last_arxiv_request", float("-inf"))
