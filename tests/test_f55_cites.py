"""F55 (Sprint 9 Task H): `cites` links computed from Crossref reference
lists (ADR-0005 A10). Matching, versions, the cache and the fetch rules on
fixtures with a fake fetcher (no network), and on the live store: every
stored `cites` link is recomputed from the cached lists, so none was typed."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f55", ROOT / "scripts" / "sprint9_f55_cites.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CITING = {"10.1/citing": {"citing-journal", "citing-arxiv-version"}}
BY_DOI = {"10.1/citing": {"citing-journal", "citing-arxiv-version"}, "10.2/cited": {"cited-paper"},
          "10.48550/arxiv.2101.00001": {"arxiv-paper"}}
BY_ARXIV = {"2101.00001": {"arxiv-paper"}, "quant-ph/0405098": {"old-arxiv-paper"}}
REFS = [
    {"key": "r1", "DOI": "10.2/CITED"},                                   # DOI, case differs
    {"key": "r2", "DOI": "10.9/not-in-store"},                            # not in the store
    {"key": "r3", "unstructured": "Smith, J. Something. arXiv:quant-ph/0405098 (2004)."},
    {"key": "r4", "unstructured": "A paper with 2101.00001 but no preprint server named"},
    {"key": "r5", "DOI": "10.1/citing"},                                  # its own DOI: a version, never a link
    {"key": "r6", "DOI": "10.48550/arXiv.2101.00001"},                    # arXiv's DOI
]


def _cache(f55, root: Path, refs=REFS, status=200) -> None:
    root.mkdir(parents=True, exist_ok=True)
    f55.cache_file("10.1/citing", root).write_text(json.dumps(
        {"doi": "10.1/citing", "fetched_on": "2026-10-15", "status": status, "reference_count": len(refs),
         "reference": refs}), encoding="utf-8")


def test_links_match_by_doi_and_arxiv_and_skip_versions(tmp_path):
    """Proven to fail by injection, 2026-10-15: with `targets - sources`
    removed from compute_links, the version pair citing-journal ->
    citing-arxiv-version appeared and this test failed."""
    f55 = _script()
    _cache(f55, tmp_path)
    links, cov = f55.compute_links(CITING, BY_DOI, BY_ARXIV, tmp_path)
    pairs = set(links)
    expected = {(s, d) for s in ("citing-journal", "citing-arxiv-version")
                for d in ("cited-paper", "old-arxiv-paper", "arxiv-paper")}
    assert pairs == expected
    assert "10.2/cited" in links[("citing-journal", "cited-paper")]
    assert "arXiv:quant-ph/0405098" in links[("citing-journal", "old-arxiv-paper")]
    assert cov["references"] == 6 and cov["references_with_doi"] == 4 and cov["references_matched"] == 3


def test_an_id_without_arxiv_named_is_not_matched(tmp_path):
    f55 = _script()
    _cache(f55, tmp_path, refs=[REFS[3]])
    links, _ = f55.compute_links(CITING, BY_DOI, BY_ARXIV, tmp_path)
    assert not links


def test_a_404_counts_as_not_found_and_yields_nothing(tmp_path):
    f55 = _script()
    _cache(f55, tmp_path, status=404)
    links, cov = f55.compute_links(CITING, BY_DOI, BY_ARXIV, tmp_path)
    assert not links and cov["not_found"] == 1 and cov["answered"] == 0


def test_fetch_caches_200_and_404_but_not_a_failure_and_never_asks_twice(tmp_path):
    """Proven to fail by injection, 2026-10-15: with the `path.exists()`
    check removed from fetch(), the second run asked both DOIs again
    (asked 2, not 0)."""
    f55 = _script()
    asked = []

    def fetcher(url, accept):
        asked.append(url)
        if url.endswith("missing"):
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO())
        if url.endswith("broken"):
            raise urllib.error.HTTPError(url, 503, "Unavailable", {}, io.BytesIO())
        return json.dumps({"message": {"reference-count": 1, "reference": [{"DOI": "10.2/cited"}]}}).encode()

    dois = ["10.1/ok", "10.1/missing", "10.1/broken"]
    first = f55.fetch(dois, fetcher, tmp_path, "2026-10-15", sleep=lambda s: None)
    assert first == {"asked": 3, "cached": 0, "failed": 1}
    assert json.loads(f55.cache_file("10.1/missing", tmp_path).read_text(encoding="utf-8"))["status"] == 404
    assert not f55.cache_file("10.1/broken", tmp_path).exists()
    asked.clear()
    second = f55.fetch(dois[:2], fetcher, tmp_path, "2026-10-15", sleep=lambda s: None)
    assert second == {"asked": 0, "cached": 2, "failed": 0} and not asked


def test_requests_are_paced(tmp_path):
    f55 = _script()
    waits = []
    f55.fetch(["10.1/a", "10.1/b", "10.1/c"],
              lambda url, accept: json.dumps({"message": {"reference": []}}).encode(), tmp_path, "2026-10-15",
              sleep=waits.append)
    assert waits == [f55.INTERVAL_S, f55.INTERVAL_S]


@pytest.mark.live_store
def test_every_stored_cites_link_is_recomputed_from_the_cache(live_conn):
    """No `cites` link is typed: each stored one, with its evidence, comes
    out of the cached reference lists again.
    Proven to fail by injection, 2026-10-15: with the Kadowaki DOI removed
    from Herman et al.'s cached list (then restored from a copy), the link
    herman-2023 -> kadowaki-1998 was named."""
    f55 = _script()
    citing, by_doi, by_arxiv = f55.store_identifiers(live_conn)
    links, _ = f55.compute_links(citing, by_doi, by_arxiv)
    stored = {(f, t): e for f, t, e in live_conn.execute(
        "SELECT from_id, to_id, evidence FROM source_links WHERE link_type = 'cites'")}
    assert stored, "no cites links stored"
    assert {k: v for k, v in stored.items() if links.get(k) != v} == {}
