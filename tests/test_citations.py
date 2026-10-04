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
    # A DOI-shaped folder in a LOCAL PATH is not a DOI (PR #30 review,
    # 2026-09-22). Reading one silently reclassified a hand-origin paper
    # as api and fetched a DIFFERENT paper's metadata under that spurious
    # DOI -- the one path found where a wrong citation attaches with no error.
    ("C:/Users/x/10.5555/12345678.pdf", None),
    (r"C:\Users\x\10.5555\12345678.pdf", None),
    # ... but a real DOI beside a path still resolves, because it says "doi".
    ("D:/Papers/paper.pdf | https://doi.org/10.1145/3007651", ("doi", "10.1145/3007651")),
    # The POSIX and UNC branch of the path check, untested until the
    # round-2 audit: deleting that alternative left the whole suite green
    # while a share path resolved as a DOI.
    ("/mnt/papers/10.5555/12345678.pdf", None),
    ("//server/share/10.5555/12345678.pdf", None),
    # A RELATIVE path, which the first version of the fix missed entirely.
    ("papers/10.5555/12345678.pdf", None),
    ("../papers/10.5555/12345678.pdf", None),
    # A path with NO document extension: only the rooted-path signal can
    # catch these, so both signals stay independently load-bearing.
    ("/mnt/archive/10.5555/12345678", None),
    ("//server/share/10.5555/12345678", None),
])
def test_parse_access_recognises_only_resolvable_ids(access, expected):
    assert citations.parse_access(access) == expected


GITHUB_JSON = json.dumps({
    "full_name": "merlinquantum/merlin",
    "description": "MerLin enables researchers to build, train, and benchmark photonic quantum machine learning models using familiar ML tools.",
    "html_url": "https://github.com/merlinquantum/merlin", "homepage": "https://merlinquantum.ai/",
    "license": {"spdx_id": "MIT"}, "created_at": "2025-06-06T12:21:57Z", "pushed_at": "2026-09-10T08:37:40Z",
    "default_branch": "main", "topics": ["qml", "photonic-quantum-computing"], "archived": False,
}).encode()


@pytest.mark.parametrize("access,expected", [
    ("https://github.com/merlinquantum/merlin", ("github", "merlinquantum/merlin")),
    ("github.com/merlinquantum/merlin/tree/main/docs", ("github", "merlinquantum/merlin")),
    ("https://github.com/merlinquantum/merlin.git | D:\\Data\\Harold\\github\\merlin", ("github", "merlinquantum/merlin")),
    ("https://github.com/kimmeyh", None),
])
def test_parse_access_recognises_a_github_repository(access, expected):
    assert citations.parse_access(access) == expected


def test_render_github_repository_is_stable_across_pushes():
    """Sprint 4 Task G: built from identity fields only (owner/name,
    description, license, created, URL), never HEAD, so the refresh diff
    stays quiet across ordinary commits."""
    md = citations.parse_github(GITHUB_JSON)
    assert md.kind == "github" and md.ident == "merlinquantum/merlin" and md.year == "2025"
    assert citations.render_citation(md) == (
        'merlinquantum, "MerLin enables researchers to build, train, and benchmark photonic quantum machine learning models '
        'using familiar ML tools.," GitHub repository merlinquantum/merlin, MIT license, created 2025-06-06, https://github.com/merlinquantum/merlin')
    changed = json.loads(GITHUB_JSON); changed["pushed_at"] = "2027-01-01T00:00:00Z"; changed["stargazers_count"] = 999
    assert citations.render_citation(citations.parse_github(json.dumps(changed).encode())) == citations.render_citation(md)


def test_resolve_routes_a_github_url_to_the_github_api():
    seen = []

    def fetcher(url, accept):
        seen.append(url)
        return GITHUB_JSON
    md, rendered = citations.resolve("https://github.com/merlinquantum/merlin", fetcher=fetcher)
    assert seen == ["https://api.github.com/repos/merlinquantum/merlin"] and md.kind == "github"
    assert rendered.startswith("merlinquantum, ")


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


def test_render_caps_the_author_list_at_ten_then_et_al():
    md = citations.parse_crossref(CROSSREF_JSON)
    md.authors = [f"A{i}, X." for i in range(12)]
    rendered = citations.render_citation(md)
    assert rendered.startswith(", ".join(f"A{i}, X." for i in range(10)) + ", et al., \"")
    assert "A10" not in rendered
    md.authors = [f"A{i}, X." for i in range(10)]
    assert "et al." not in citations.render_citation(md)


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


DATACITE_ARXIV_JSON = json.dumps({"data": {"attributes": {
    "doi": "10.48550/arxiv.2303.05509",
    "titles": [{"title": "Quantum-Enhanced Greedy Combinatorial Optimization Solver"}],
    "creators": [{"familyName": "Dupont", "givenName": "Maxime"}, {"familyName": "Evert", "givenName": "Bram"}],
    "publicationYear": 2023, "publisher": "arXiv", "version": "2",
    "dates": [{"date": "2023-03-09T18:59:37Z", "dateType": "Submitted"}, {"date": "2023-11-17T01:28:51Z", "dateType": "Submitted"},
              {"date": "2023-11-22T01:09:02Z", "dateType": "Updated"}, {"date": "2023", "dateType": "Issued"}],
    "relatedIdentifiers": [{"relationType": "IsVersionOf", "relatedIdentifierType": "DOI", "relatedIdentifier": "10.1126/sciadv.adi0487"}],
    "url": "https://arxiv.org/abs/2303.05509",
}}}).encode()


def test_fetch_arxiv_batch_sends_one_id_per_request_paced(monkeypatch):
    """Task C measurement: a multi-id id_list request earns a 406 and a
    several-minute block for this client; single ids paced 3 s do not."""
    seen, waits = [], []
    monkeypatch.setattr(citations, "_sleep", waits.append)

    def spy(url, accept):
        seen.append(url)
        return ARXIV_ATOM.replace(b"2303.05509", url.split("id_list=")[1].encode())
    got = citations.fetch_arxiv_batch(["2303.05509", "2211.15631"], fetcher=spy)
    assert set(got) == {"2303.05509", "2211.15631"}
    assert [u.split("id_list=")[1] for u in seen] == ["2303.05509", "2211.15631"]
    assert "," not in "".join(seen)
    assert waits == [citations.ARXIV_MIN_INTERVAL_S]


def test_fetch_arxiv_batch_falls_back_to_datacite_when_arxiv_refuses(monkeypatch):
    monkeypatch.setattr(citations, "_sleep", lambda s: None)

    def fetcher(url, accept):
        if "export.arxiv.org" in url:
            raise _http_error(406)
        assert "api.datacite.org/dois/10.48550/arXiv.2303.05509" in url
        return DATACITE_ARXIV_JSON
    got = citations.fetch_arxiv_batch(["2303.05509"], fetcher=fetcher)
    md = got["2303.05509"]
    assert md.kind == "arxiv" and md.extra["provider"] == "DataCite" and md.version == "v2"
    assert citations.render_citation(md) == ('Dupont, M., Evert, B., "Quantum-Enhanced Greedy Combinatorial Optimization Solver," '
                                             'arXiv:2303.05509v2, DOI:10.1126/sciadv.adi0487, 2023-11-17')  # latest Submitted, = arXiv's `updated`


def test_fetch_arxiv_batch_propagates_a_non_retryable_arxiv_error(monkeypatch):
    def fetcher(url, accept):
        raise _http_error(404)
    with pytest.raises(Exception, match="404"):
        citations.fetch_arxiv_batch(["2303.05509"], fetcher=fetcher)


def test_xml_with_doctype_or_entity_is_refused():
    """XXE / billion-laughs shapes never occur in a real arXiv feed; refuse
    rather than parse (stdlib ElementTree, no defusedxml dependency)."""
    evil = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><feed xmlns="http://www.w3.org/2005/Atom"/>'
    with pytest.raises(ValueError, match="DOCTYPE"):
        citations.parse_arxiv_atom(evil)


class _Resp:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body


def _http_error(code: int):
    import urllib.error
    return urllib.error.HTTPError("https://export.arxiv.org/x", code, "refused", {}, None)


def test_default_fetcher_retries_transient_refusals_with_backoff(monkeypatch):
    """Sprint 4 Task C measurement: arXiv returned 406 to a burst and 200
    to the same requests paced 3 s apart. One attempt is the wrong number."""
    calls, waits = [], []
    def fake_open(req, timeout):
        calls.append(req.full_url)
        if len(calls) < 3:
            raise _http_error(406)
        return _Resp(b"<feed/>")
    monkeypatch.setattr(citations, "_sleep", waits.append)
    assert citations.default_fetcher("https://api.crossref.org/works/x", "application/json", _open=fake_open) == b"<feed/>"
    assert len(calls) == 3 and waits == list(citations.RETRY_SLEEPS_S)


def test_default_fetcher_gives_up_after_the_last_retry(monkeypatch):
    monkeypatch.setattr(citations, "_sleep", lambda s: None)
    def always_406(req, timeout):
        raise _http_error(406)
    with pytest.raises(Exception, match="406|refused"):
        citations.default_fetcher("https://api.crossref.org/works/x", "application/json", _open=always_406)


def test_default_fetcher_does_not_retry_a_404(monkeypatch):
    waits = []
    monkeypatch.setattr(citations, "_sleep", waits.append)
    calls = []
    def not_found(req, timeout):
        calls.append(1)
        raise _http_error(404)
    with pytest.raises(Exception):
        citations.default_fetcher("https://api.crossref.org/works/x", "application/json", _open=not_found)
    assert calls == [1] and waits == []


def test_render_uses_the_publisher_as_corporate_author_when_the_record_names_no_people():
    """Crossref's record for RAND RRA1367-6 (Sprint 4 Task C): type
    edited-book, publisher RAND Corporation, zero contributors."""
    body = json.dumps({"message": {"DOI": "10.7249/rra1367-6", "title": ["Preparing for Post-Quantum Critical Infrastructure"],
                                   "publisher": "RAND Corporation", "type": "edited-book",
                                   "issued": {"date-parts": [[2022]]}}}).encode()
    md = citations.parse_crossref(body)
    assert md.authors == []
    assert citations.render_citation(md) == 'RAND Corporation, "Preparing for Post-Quantum Critical Infrastructure," DOI:10.7249/rra1367-6, 2022'


def test_render_book_keeps_crossref_subtitle_and_publisher():
    """freericks-2026 (Task C): Crossref's book record splits the subtitle
    into `subtitle` and has a publisher but no container-title."""
    body = json.dumps({"message": {"DOI": "10.1007/978-3-031-87845-9", "title": ["Quantum Mechanics Done Right"],
                                   "subtitle": ["The Shortest Path from Novice to Researcher"],
                                   "author": [{"family": "Freericks", "given": "James K."}],
                                   "publisher": "Springer Nature Switzerland", "type": "book",
                                   "issued": {"date-parts": [[2026]]}}}).encode()
    md = citations.parse_crossref(body)
    assert md.title == "Quantum Mechanics Done Right: The Shortest Path from Novice to Researcher"
    assert citations.render_citation(md) == ('Freericks, J.K., "Quantum Mechanics Done Right: The Shortest Path from Novice to Researcher," '
                                             'Springer Nature Switzerland, DOI:10.1007/978-3-031-87845-9, 2026')


def test_fetch_doi_names_an_unregistered_doi_instead_of_two_404s():
    """udaru-2025's printed DOI 10.63278/ijcrcr.v8i.3419: doi.org handle
    lookup returns responseCode 100 (no such handle), checked 2026-09-19."""
    def fetcher(url, accept):
        if "doi.org/api/handles" in url:
            return json.dumps({"responseCode": 100, "handle": "10.63278/ijcrcr.v8i.3419"}).encode()
        raise RuntimeError("HTTP Error 404: Not Found")
    with pytest.raises(LookupError, match="not registered at doi.org"):
        citations.fetch_doi("10.63278/ijcrcr.v8i.3419", fetcher=fetcher)


def test_fetch_doi_reads_doi_org_404_as_unregistered():
    """The live shape: doi.org answers a missing handle with HTTP 404 (the
    JSON body carries responseCode 100 but a real fetcher raises first)."""
    def fetcher(url, accept):
        if "doi.org/api/handles" in url:
            raise _http_error(404)
        raise RuntimeError("HTTP Error 404: Not Found")
    with pytest.raises(LookupError, match="not registered at doi.org"):
        citations.fetch_doi("10.63278/ijcrcr.v8i.3419", fetcher=fetcher)


def test_fetch_doi_keeps_provider_errors_when_the_doi_is_registered_but_both_providers_fail():
    def fetcher(url, accept):
        if "doi.org/api/handles" in url:
            return json.dumps({"responseCode": 1}).encode()
        raise RuntimeError("HTTP Error 503")
    with pytest.raises(LookupError, match=r"Crossref \(HTTP Error 503\); DataCite"):
        citations.fetch_doi("10.1000/registered", fetcher=fetcher)


def test_user_agent_is_the_plain_one_arxiv_accepts():
    """Pre-flight 2026-09-19: export.arxiv.org returned HTTP 406 to
    browser-style and mailto-bearing User-Agents and 200 to a plain one.
    Pinned so nobody 'improves' the header back into a 406."""
    assert citations.USER_AGENT == "curl/8.0"


def test_doi_is_registered_says_unknown_when_the_registry_cannot_be_reached():
    """A DNS blip against doi.org must NOT become the confident, wrong
    message "DOI X is not registered", which tells the operator to re-record
    a perfectly good paper as hand-transcribed. Transport failure means
    unknown, and unknown must surface the PROVIDER errors instead.

    PR #30 review, 2026-09-22: inverting the `except Exception: return True`
    default left all 45 citation/refresh/intake tests green.
    """
    import socket

    def fetcher(url, accept):
        if "doi.org/api/handles" in url:
            raise socket.timeout("timed out")
        raise RuntimeError("HTTP Error 404: Not Found")

    with pytest.raises(LookupError) as excinfo:
        citations.fetch_doi("10.1000/real-but-unreachable", fetcher=fetcher)
    message = str(excinfo.value)
    assert "Crossref" in message and "DataCite" in message
    assert "not registered" not in message, (
        "an unreachable registry must not be reported as a negative answer")


def test_doi_is_registered_returns_true_on_transport_failure():
    """The same rule at the unit level: unknown biases toward True."""
    import socket

    def unreachable(url, accept):
        raise socket.timeout("timed out")

    assert citations.doi_is_registered("10.1000/x", fetcher=unreachable) is True


# ---------------------------------------------------------------- GitHub token (Sprint 6 Task K, F35)

def test_github_requests_carry_the_token_and_nothing_else_does_regression(monkeypatch):
    """The token goes into the Authorization header of api.github.com
    requests only. Proven to fail by injection: with the header line in
    default_fetcher removed, the first assertion went red; with the URL
    check removed, the arXiv request carried the token and the second did."""
    monkeypatch.setenv("GITHUB_TOKEN", "tok-FIXTURE-123")
    monkeypatch.delenv("GH_TOKEN", raising=False)
    seen = {}

    def fake_open(req, timeout):
        seen[req.full_url] = req.get_header("Authorization")
        return _Resp(b"{}")

    citations.default_fetcher(citations.GITHUB_API + "owner/name", "application/json", _open=fake_open)
    citations.default_fetcher("https://export.arxiv.org/x", "application/atom+xml", _open=fake_open)
    assert seen[citations.GITHUB_API + "owner/name"] == "Bearer tok-FIXTURE-123"
    assert seen["https://export.arxiv.org/x"] is None


def test_without_a_token_github_requests_stay_unauthenticated(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    seen = []
    citations.default_fetcher(citations.GITHUB_API + "o/n", "application/json",
                              _open=lambda req, timeout: seen.append(req.get_header("Authorization")) or _Resp(b"{}"))
    assert seen == [None] and citations.github_token() is None


def test_the_token_never_appears_in_a_failure(monkeypatch):
    """A refused request's exception must not carry the credential (ADR-0002:
    values are never logged)."""
    import urllib.error
    monkeypatch.setenv("GH_TOKEN", "tok-FIXTURE-456")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def refused(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 401, "Bad credentials", {}, None)

    with pytest.raises(urllib.error.HTTPError) as err:
        citations.default_fetcher(citations.GITHUB_API + "o/n", "application/json", _open=refused)
    assert "tok-FIXTURE-456" not in str(err.value) and "tok-FIXTURE-456" not in repr(err.value)


def test_fetch_arxiv_batch_falls_back_to_datacite_on_a_timeout_regression(monkeypatch):
    """Sprint 6 Task J: 20 bulk ids were refused on arXiv read timeouts
    because only an HTTP refusal fell through to DataCite. Proven to fail by
    injection: without the timeout clause, the TimeoutError propagated."""
    monkeypatch.setattr(citations, "_sleep", lambda s: None)

    def fetcher(url, accept):
        if "export.arxiv.org" in url:
            raise TimeoutError("The read operation timed out")
        return DATACITE_ARXIV_JSON
    md = citations.fetch_arxiv_batch(["2303.05509"], fetcher=fetcher)["2303.05509"]
    assert md.extra["provider"] == "DataCite"


def test_arxiv_gets_one_attempt_and_the_batch_goes_to_datacite_regression(monkeypatch):
    """Team lead, 2026-10-04 (Q2 = 2): no arXiv retries; any arXiv failure
    goes straight to DataCite, so a refused id costs ONE arXiv request.
    Proven to fail by injection: with arXiv given the retry sleeps again,
    three arXiv requests were counted."""
    monkeypatch.setattr(citations, "_sleep", lambda s: None)
    arxiv_calls = []

    def fake_open(req, timeout):
        if "arxiv.org" in req.full_url:
            arxiv_calls.append(req.full_url)
            raise _http_error(429)
        return _Resp(DATACITE_ARXIV_JSON)

    def fetcher(url, accept):
        return citations.default_fetcher(url, accept, _open=fake_open)

    md = citations.fetch_arxiv_batch(["2303.05509"], fetcher=fetcher)["2303.05509"]
    assert len(arxiv_calls) == 1 and md.extra["provider"] == "DataCite"


def test_an_arxiv_404_also_goes_to_datacite(monkeypatch):
    monkeypatch.setattr(citations, "_sleep", lambda s: None)

    def fetcher(url, accept):
        if "export.arxiv.org" in url:
            raise _http_error(404)
        return DATACITE_ARXIV_JSON
    assert citations.fetch_arxiv_batch(["2303.05509"], fetcher=fetcher)["2303.05509"].extra["provider"] == "DataCite"


def test_an_arxiv_id_inside_a_repository_name_is_the_repository_regression():
    """Sprint 6 Task K: the door read this repository URL as arXiv:2502.18361
    and resolved it to the paper it belongs to. Proven to fail by injection:
    with the inside-repo check removed, parse_access returned ("arxiv", ...)."""
    url = "https://github.com/salvatore-lorenzo/arXiv-2502.18361-QELMWITNESS"
    assert citations.parse_access(url) == ("github", "salvatore-lorenzo/arXiv-2502.18361-QELMWITNESS")
    assert citations.parse_access("arXiv:2502.18361") == ("arxiv", "2502.18361")
    assert citations.parse_access("https://arxiv.org/abs/2502.18361") == ("arxiv", "2502.18361")
