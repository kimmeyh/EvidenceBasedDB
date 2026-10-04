"""The computed-field probes (store/probes.py, Sprint 6 Task F). No network:
every registry answer is a fixture shaped like the real response."""
from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import probes  # noqa: E402


def _atom(comment: str = "", jref: str = "", doi: str = "", aff: str = "") -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
<entry><id>http://arxiv.org/abs/2308.08167v2</id><title>A title</title>
<author><name>A. Author</name>{f'<arxiv:affiliation>{aff}</arxiv:affiliation>' if aff else ''}</author>
{f'<arxiv:comment>{comment}</arxiv:comment>' if comment else ''}
{f'<arxiv:journal_ref>{jref}</arxiv:journal_ref>' if jref else ''}
{f'<arxiv:doi>{doi}</arxiv:doi>' if doi else ''}
</entry></feed>""".encode()


def _fetcher(routes: dict):
    def fetch(url, accept):
        for key, body in routes.items():
            if key in url:
                if isinstance(body, Exception):
                    raise body
                return body
        raise AssertionError(f"unexpected request {url}")
    return fetch


_NO_NOTICE = json.dumps({"message": {"items": []}}).encode()


def _http(code):
    return urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(b""))


def test_arxiv_withdrawal_is_read_from_the_comment():
    r = probes.probe_arxiv("p", "2308.08167", _fetcher({"export.arxiv.org": _atom(comment="This paper has been withdrawn by the author")}))
    assert r.values["publication_status"] == "withdrawn" and r.provider == "arXiv"


def test_arxiv_journal_doi_means_published_and_names_the_version():
    r = probes.probe_arxiv("p", "2308.08167", _fetcher({"export.arxiv.org": _atom(doi="10.1/x", aff="Uni A"),
                                                        "filter=updates": _NO_NOTICE}))
    assert r.values == {"publication_status": "published", "version_of": "10.1/x", "affiliations": "Uni A"}


def test_arxiv_plain_record_is_a_preprint():
    r = probes.probe_arxiv("p", "2308.08167", _fetcher({"export.arxiv.org": _atom()}))
    assert r.values == {"publication_status": "preprint"}


def test_when_arxiv_refuses_the_status_is_left_unanswered_regression():
    """A withdrawal shows only in arXiv's comment, so DataCite's answer must
    not become 'preprint'. Proven to fail by injection: with the DataCite
    branch recording 'preprint', this test went red."""
    datacite = json.dumps({"data": {"attributes": {"titles": [{"title": "T"}], "creators": [],
                                                   "publicationYear": 2023, "dates": []}}}).encode()
    r = probes.probe_arxiv("p", "2308.08167", _fetcher({"export.arxiv.org": _http(503), "api.datacite.org": datacite}))
    assert "publication_status" not in r.values and r.provider == "DataCite"
    assert any("unanswered" in n for n in r.notes)


def test_crossref_retraction_notice_overrides_published():
    msg = json.dumps({"message": {"type": "journal-article", "author": []}}).encode()
    notice = json.dumps({"message": {"items": [{"DOI": "10.1007/notice", "update-to": [
        {"type": "retraction", "DOI": "10.1007/ARTICLE"}]}]}}).encode()
    r = probes.probe_doi("p", "10.1007/article", _fetcher({"filter=updates": notice, "api.crossref.org/works/": msg}))
    assert r.values["publication_status"] == "retracted" and "10.1007/notice" in r.notes[0]


def test_crossref_posted_content_is_a_preprint_and_an_unknown_type_is_not_guessed():
    pre = json.dumps({"message": {"type": "posted-content"}}).encode()
    odd = json.dumps({"message": {"type": "peer-review"}}).encode()
    assert probes.probe_doi("p", "10.1/a", _fetcher({"filter=updates": _NO_NOTICE, "works/": pre})).values == \
        {"publication_status": "preprint"}
    r = probes.probe_doi("p", "10.1/a", _fetcher({"filter=updates": _NO_NOTICE, "works/": odd}))
    assert "publication_status" not in r.values and "peer-review" in r.notes[0]


class _Resp:
    def __init__(self, body: bytes, ctype: str = "text/html"):
        self.body, self.headers = body, {"Content-Type": ctype}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self.body


def test_access_probe_states_what_it_observed():
    words = ("word " * 80).encode()
    assert probes.probe_access("https://example.org", _open=lambda req, timeout: _Resp(b"<html>" + words + b"</html>")) == "open (HTTP 200)"
    assert probes.probe_access("https://example.org", _open=lambda req, timeout: _Resp(b"<html><script>x</script></html>")).startswith("bot challenge")

    def refused(req, timeout):
        raise _http(403)
    assert probes.probe_access("https://example.org", _open=refused) == "refused (HTTP 403)"


def test_landing_url_per_access_kind():
    assert probes.landing_url("arXiv:2308.08167") == "https://arxiv.org/abs/2308.08167"
    assert probes.landing_url("doi:10.1234/x") == "https://doi.org/10.1234/x"
    assert probes.landing_url("D:/x/page.html | https://example.org/p") == "https://example.org/p"
    assert probes.landing_url("D:/x/report.pdf") is None
