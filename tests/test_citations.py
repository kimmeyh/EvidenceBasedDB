"""Tests for store/citations.py (Sprint 4 Task B, F25 C1).

No network: every provider response is an inline fixture shaped like the
real one observed at Sprint 4 planning (arXiv Atom for 2303.05509,
Crossref JSON for 10.1145/3007651). The fetcher is injected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import citations  # noqa: E402

ARXIV_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2303.05509v2</id>
    <updated>2023-11-17T18:00:00Z</updated>
    <published>2023-03-09T18:00:00Z</published>
    <title>Quantum-Enhanced Greedy Combinatorial
  Optimization Solver</title>
    <author><name>Maxime Dupont</name></author>
    <author><name>Bram Evert</name></author>
    <arxiv:doi>10.1126/sciadv.adi0487</arxiv:doi>
    <arxiv:journal_ref>Science Advances 9, eadi0487 (2023)</arxiv:journal_ref>
  </entry>
</feed>
"""

CROSSREF_JSON = json.dumps({"message": {
    "DOI": "10.1145/3007651",
    "title": ["High-Performance Computing with Quantum Processing Units"],
    "author": [{"family": "Britt", "given": "Keith A."}, {"family": "Humble", "given": "Travis S."}],
    "container-title": ["ACM Journal on Emerging Technologies in Computing Systems"],
    "volume": "13", "issue": "3", "article-number": "39",
    "published-print": {"date-parts": [[2017, 3, 31]]},
    "URL": "https://doi.org/10.1145/3007651",
}}).encode()

DATACITE_JSON = json.dumps({"data": {"attributes": {
    "doi": "10.5281/zenodo.3233986",
    "titles": [{"title": "The Turing Way: A Handbook for Reproducible Data Science"}],
    "creators": [{"familyName": "Arnold", "givenName": "Becky"}, {"name": "The Turing Way Community"}],
    "publicationYear": 2019, "publisher": "Zenodo",
    "dates": [{"date": "2019-03-25", "dateType": "Issued"}],
    "url": "https://zenodo.org/record/3233986",
}}}).encode()


def fake_fetcher(url: str, accept: str) -> bytes:
    if "export.arxiv.org" in url:
        return ARXIV_ATOM
    if "api.crossref.org" in url:
        if "10.1145/3007651" in url:
            return CROSSREF_JSON
        raise RuntimeError("HTTP 404")
    if "api.datacite.org" in url:
        return DATACITE_JSON
    raise RuntimeError(f"unexpected url {url}")


@pytest.mark.parametrize("access,expected", [
    ("arXiv:2303.05509", ("arxiv", "2303.05509")),
    ("arXiv:2211.15631v1", ("arxiv", "2211.15631")),
    ("https://arxiv.org/abs/2602.11092", ("arxiv", "2602.11092")),
    ("DOI:10.1145/3007651", ("doi", "10.1145/3007651")),
    ("https://doi.org/10.1109/TQE.2022.3184764", ("doi", "10.1109/TQE.2022.3184764")),
    ("https://proceedings.mlr.press/v25/neven12/ (PMLR); also stored at D:\\Papers, no arXiv id found", None),
    ("local file, no DOI/arXiv id", None),
    ("", None),
])
def test_parse_access_recognises_only_resolvable_ids(access, expected):
    assert citations.parse_access(access) == expected


def test_parse_arxiv_atom_normalises_title_authors_version_and_journal_ref():
    (md,) = citations.parse_arxiv_atom(ARXIV_ATOM)
    assert md.ident == "2303.05509" and md.version == "v2"
    assert md.title == "Quantum-Enhanced Greedy Combinatorial Optimization Solver"  # newline collapsed
    assert md.authors == ["Dupont, M.", "Evert, B."]
    assert md.doi == "10.1126/sciadv.adi0487"
    assert md.journal_ref == "Science Advances 9, eadi0487 (2023)"
    assert md.date == "2023-11-17" and md.year == "2023"


def test_render_arxiv_citation_is_house_style_and_deterministic():
    (md,) = citations.parse_arxiv_atom(ARXIV_ATOM)
    rendered = citations.render_citation(md)
    assert rendered == ('Dupont, M., Evert, B., "Quantum-Enhanced Greedy Combinatorial Optimization Solver," '
                        'arXiv:2303.05509v2, Science Advances 9, eadi0487 (2023), DOI:10.1126/sciadv.adi0487, 2023-11-17')
    assert citations.render_citation(md) == rendered


def test_parse_and_render_crossref():
    md = citations.parse_crossref(CROSSREF_JSON)
    assert md.authors == ["Britt, K.A.", "Humble, T.S."]
    assert citations.render_citation(md) == (
        'Britt, K.A., Humble, T.S., "High-Performance Computing with Quantum Processing Units," '
        'ACM Journal on Emerging Technologies in Computing Systems, 13(3), 39, DOI:10.1145/3007651, 2017-03-31')


def test_fetch_doi_falls_back_to_datacite_when_crossref_does_not_know_the_doi():
    md = citations.fetch_doi("10.5281/zenodo.3233986", fetcher=fake_fetcher)
    assert md.title.startswith("The Turing Way")
    assert md.authors == ["Arnold, B.", "The Turing Way Community"]
    assert md.date == "2019-03-25"


def test_resolve_routes_by_access_kind():
    md, rendered = citations.resolve("arXiv:2303.05509", fetcher=fake_fetcher)
    assert md.kind == "arxiv" and rendered.startswith("Dupont, M.")
    md, rendered = citations.resolve("DOI:10.1145/3007651", fetcher=fake_fetcher)
    assert md.kind == "doi" and rendered.startswith("Britt, K.A.")


def test_resolve_refuses_an_access_with_no_id():
    with pytest.raises(LookupError, match="no resolvable"):
        citations.resolve("local file, no DOI/arXiv id", fetcher=fake_fetcher)


def test_fetch_arxiv_batch_uses_one_id_list_request():
    seen = []

    def spy(url, accept):
        seen.append(url)
        return ARXIV_ATOM
    citations.fetch_arxiv_batch(["2303.05509", "2211.15631"], fetcher=spy)
    assert len(seen) == 1 and "id_list=2303.05509,2211.15631" in seen[0]


def test_xml_with_doctype_or_entity_is_refused():
    """XXE / billion-laughs shapes never occur in a real arXiv feed; refuse
    rather than parse (stdlib ElementTree, no defusedxml dependency)."""
    evil = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><feed xmlns="http://www.w3.org/2005/Atom"/>'
    with pytest.raises(ValueError, match="DOCTYPE"):
        citations.parse_arxiv_atom(evil)


def test_user_agent_is_the_plain_one_arxiv_accepts():
    """Pre-flight 2026-09-19: export.arxiv.org returned HTTP 406 to
    browser-style and mailto-bearing User-Agents and 200 to a plain one.
    Pinned so nobody 'improves' the header back into a 406."""
    assert citations.USER_AGENT == "curl/8.0"
