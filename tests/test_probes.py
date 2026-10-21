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


def _datacite(general: str, relations=(), affiliation=None) -> bytes:
    """Shaped like DataCite's answer for DOI:10.5281/zenodo.19985473 on
    2026-10-18 (affiliation a list of names, as there)."""
    return json.dumps({"data": {"attributes": {
        "types": {"resourceTypeGeneral": general},
        "relatedIdentifiers": [{"relationType": t, "relatedIdentifier": i} for t, i in relations],
        "creators": [{"name": "Sepulveda-Jimenez, Alfredo", "affiliation": affiliation or []}]}}}).encode()


def test_a_doi_crossref_does_not_know_is_asked_of_datacite_regression():
    """F86 (Sprint 10 Task D): after a Crossref 404 the probe labeled its
    result DataCite without sending a DataCite request, so a DataCite DOI
    never recorded a primary answer and stayed due forever (ADR-0005 A9).
    Zenodo's IsVersionOf (its all-versions DOI) is the same work and is not
    a version_of. Proven to fail by injection, 2026-10-18: with the branch
    restored to return without a request, this test went red; a second,
    with IsVersionOf added to the version relations, also went red."""
    r = probes.probe_doi("p", "10.5281/zenodo.19985473", _fetcher({
        "api.crossref.org": _http(404),
        "api.datacite.org/dois/10.5281/zenodo.19985473": _datacite(
            "Preprint", [("IsVersionOf", "10.5281/zenodo.19985472")], ["QDR Labs"])}))
    assert r.provider == "DataCite"
    assert r.values == {"publication_status": "preprint", "affiliations": "QDR Labs"}
    assert any("no retraction notices" in n for n in r.notes)


def test_datacite_states_only_what_it_says():
    """A preprint relation names the other version; an unmapped resource
    type is not guessed; a DOI neither registry knows says so."""
    r = probes.probe_doi("p", "10.1/a", _fetcher({"api.crossref.org": _http(404), "api.datacite.org": _datacite(
        "Preprint", [("IsPreprintOf", "10.1/published")])}))
    assert r.values == {"publication_status": "preprint", "version_of": "10.1/published"}
    r = probes.probe_doi("p", "10.1/a", _fetcher({"api.crossref.org": _http(404), "api.datacite.org": _datacite("Dataset")}))
    assert "publication_status" not in r.values and any("'Dataset'" in n for n in r.notes)
    r = probes.probe_doi("p", "10.1/a", _fetcher({"api.crossref.org": _http(404), "api.datacite.org": _http(404)}))
    assert r.values == {} and "not in DataCite" in r.notes[0] and not r.answered


def test_datacite_affiliation_objects_are_read_and_a_null_name_is_skipped():
    """Task D review (2026-10-18): the object form ({"name": ...}) had no
    test, and a null name raised. Proven to fail by injection, 2026-10-18:
    with `or ""` back to the default argument, this test raised."""
    r = probes.probe_doi("p", "10.1/a", _fetcher({"api.crossref.org": _http(404), "api.datacite.org": _datacite(
        "Preprint", affiliation=[{"name": "QDR Labs"}, {"name": None}])}))
    assert r.values["affiliations"] == "QDR Labs" and r.answered


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


def test_a_probe_never_downgrades_a_recorded_withdrawal_regression(tmp_path):
    """Task I recorded four withdrawals from arXiv's /pdf 404 signature whose
    comments never say 'withdrawn'; a later probe would have called them
    preprints. Proven to fail by injection: with keeps_terminal_status
    returning False, the preprint value was reported as writable."""
    import importlib.util
    from store import create_store
    from store.ingest import PaperRecord, insert_paper, record_probe
    spec = importlib.util.spec_from_file_location("probe_script", ROOT / "scripts" / "probe_reference_fields.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    conn = create_store(tmp_path / "s.db")
    insert_paper(conn, PaperRecord(id="p", tier="seen", access="arXiv:2304.05672", disposition="d", context="qml",
                                   value="t", citation="C", citation_origin="api", citation_source="replay",
                                   updated="2026-10-04", updated_reason="test"))
    record_probe(conn, "p", "publication_status", "withdrawn", "arXiv", "2026-10-04")
    assert mod.keeps_terminal_status(conn, "p", "publication_status", "preprint") is True
    assert mod.keeps_terminal_status(conn, "p", "publication_status", "retracted") is False
    assert mod.keeps_terminal_status(conn, "p", "access_status", "open (HTTP 200)") is False
    conn.close()


def test_a_rate_limit_or_no_connection_is_no_answer_not_an_access_status():
    """Sprint 6 Phase 5 review: '429' and 'unreachable' describe this client
    at that moment, and were overwriting the last good measurement."""
    def limited(req, timeout):
        raise _http(429)

    def down(req, timeout):
        raise TimeoutError("timed out")
    assert probes.probe_access("https://example.org", _open=limited) is None
    assert probes.probe_access("https://example.org", _open=down) is None
