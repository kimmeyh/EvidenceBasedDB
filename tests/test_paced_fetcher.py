"""PacedFetcher keeps arXiv's requested spacing (PR #30 review, 2026-09-22).

Why this file exists: `PacedFetcher` is the DEFAULT production fetcher --
`scripts/intake.py` and `scripts/refresh_citations.py` both fall back to it
when no fetcher is injected -- and until this file it had zero tests. The
review agent disabled the host check entirely (`if "export.arxiv.org" in
url` -> `if False`) and the full 395-test suite still passed.

What losing the pacing costs, from the module docstring's own measurement:
arXiv answers a burst with HTTP 406 and then refuses EVERY further request
from this client for several minutes, single ids included. The 1,200-paper
bulk pass is budgeted at about an hour on the assumption pacing holds, so a
refactor that drops the host check ships silently and fails only on a live
bulk run.

Injection-verified 2026-09-22: `if "export.arxiv.org" in url` -> `if False`
turns test_consecutive_arxiv_requests_are_spaced red; removing the
module clock stamp (`_last_arxiv_request = _monotonic()`, since Sprint 6) turns it red as well.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import citations  # noqa: E402

ARXIV = "https://export.arxiv.org/api/query?id_list=2303.05509"
CROSSREF = "https://api.crossref.org/works/10.1145/3007651"


@pytest.fixture
def clock(monkeypatch):
    """A fake monotonic clock that only advances when someone sleeps."""
    state = {"now": 1000.0, "slept": []}
    monkeypatch.setattr(citations, "_monotonic", lambda: state["now"])

    def fake_sleep(seconds):
        state["slept"].append(round(seconds, 3))
        state["now"] += seconds
    monkeypatch.setattr(citations, "_sleep", fake_sleep)
    return state


def test_consecutive_arxiv_requests_are_spaced(clock):
    calls = []
    fetcher = citations.PacedFetcher(inner=lambda u, a: calls.append(u) or b"ok", interval_s=3.0)
    fetcher(ARXIV, "application/atom+xml")
    fetcher(ARXIV, "application/atom+xml")
    fetcher(ARXIV, "application/atom+xml")
    assert len(calls) == 3
    assert clock["slept"] == [3.0, 3.0], (
        "each arXiv request after the first must wait the full interval; "
        f"slept {clock['slept']}")


def test_the_first_arxiv_request_does_not_wait(clock):
    fetcher = citations.PacedFetcher(inner=lambda u, a: b"ok", interval_s=3.0)
    fetcher(ARXIV, "application/atom+xml")
    assert clock["slept"] == [], "nothing to pace against on the first request"


def test_other_hosts_are_not_paced_and_do_not_reset_the_arxiv_clock(clock):
    """Crossref and DataCite have no such limit. A DOI fetch between two
    arXiv fetches must neither sleep itself nor let the next arXiv request
    skip its wait."""
    fetcher = citations.PacedFetcher(inner=lambda u, a: b"ok", interval_s=3.0)
    fetcher(ARXIV, "application/atom+xml")
    fetcher(CROSSREF, "application/json")
    fetcher(CROSSREF, "application/json")
    assert clock["slept"] == [], "a non-arXiv host must not be paced"
    fetcher(ARXIV, "application/atom+xml")
    assert clock["slept"] == [3.0], "the arXiv clock is only advanced by arXiv requests"


def test_time_already_spent_counts_toward_the_interval(clock):
    """Pacing waits only for the REMAINDER. A bulk run that spends two
    seconds parsing between requests should sleep one, not three."""
    fetcher = citations.PacedFetcher(inner=lambda u, a: b"ok", interval_s=3.0)
    fetcher(ARXIV, "application/atom+xml")
    clock["now"] += 2.0  # work happened between requests
    fetcher(ARXIV, "application/atom+xml")
    assert clock["slept"] == [1.0]


def test_the_default_interval_is_twice_arxivs_published_rate():
    """Pinned so nobody 'optimizes' the bulk run into a multi-minute block.
    6 s since 2026-10-04 (team lead): at arXiv's published 3 s, a sustained
    run of about 1,130 lookups ended in HTTP 429 for everything."""
    assert citations.ARXIV_MIN_INTERVAL_S == 6.0
    assert citations.PacedFetcher().interval_s == 6.0


def test_the_wrapped_fetcher_receives_url_and_accept_unchanged(clock):
    seen = []
    fetcher = citations.PacedFetcher(inner=lambda u, a: seen.append((u, a)) or b"body", interval_s=0.0)
    assert fetcher(ARXIV, "application/atom+xml") == b"body"
    assert seen == [(ARXIV, "application/atom+xml")]


def test_default_inner_is_the_real_fetcher():
    assert citations.PacedFetcher().inner is citations.default_fetcher


def test_a_second_pacer_shares_the_clock_regression(clock):
    """Sprint 6 retrospective I1: a NEW pacer must not start at zero. intake
    built one per entry, and none of them ever waited. Proven to fail by
    injection: with the clock moved back onto each instance, the second
    pacer's request went out with no wait."""
    citations.PacedFetcher(inner=lambda u, a: b"ok")(ARXIV, "x")
    citations.PacedFetcher(inner=lambda u, a: b"ok")(ARXIV, "x")
    assert clock["slept"] == [citations.ARXIV_MIN_INTERVAL_S]
