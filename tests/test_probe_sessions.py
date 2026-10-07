"""F52 (Sprint 7 Task C): probes from arXiv's abstract page, under a
per-session cap, with an early pause on refusals and a resumable run.

No network: the abstract pages are synthetic, carrying only the markers
read from two live pages on 2026-10-06 (2308.08167 withdrawn, 2405.12044
published); arXiv's own page text is not copied into the repository."""
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

from store import citations, create_store, probes  # noqa: E402
from store.ingest import PaperRecord, insert_paper, record_probe  # noqa: E402

FILLER = "<p>" + "word " * 80 + "</p>"  # an open page has visible words


def _page(ident: str, *, banner: bool = False, comment: str = "", jref: str = "", doi: str = "") -> bytes:
    parts = [f'<html><head><meta name="citation_arxiv_id" content="{ident}" />',
             f'<meta name="citation_doi" content="{doi}" />' if doi else "", "</head><body>", FILLER]
    if banner:
        parts.append('<span class="error" style="border: 2px solid grey">This paper has been withdrawn by A. Author</span>')
    if comment:
        parts.append(f'<td class="tablecell comments mathjax"><em>{comment}</em></td>')
    parts.append(f'<td class="tablecell arxivdoi"><a href="https://doi.org/10.48550/arXiv.{ident}">x</a></td>')
    if jref:
        parts.append(f'<td class="tablecell jref">{jref}</td>')
    if doi:
        parts.append(f'<td class="tablecell doi"><a href="https://doi.org/{doi}" data-doi="{doi}">x</a></td>')
    return "".join(parts + ["</body></html>"]).encode()


class _Resp:
    def __init__(self, body: bytes):
        self.body, self.headers = body, {"Content-Type": "text/html; charset=utf-8"}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self.body


def _http(code):
    return urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(b""))


def _site(pages: dict):
    """urlopen stand-in: the abs page per id, or an exception."""
    seen = []

    def _open(req, timeout):
        url = req.full_url
        seen.append(url)
        body = pages[url.rsplit("/", 1)[1]]
        if isinstance(body, Exception):
            raise body
        return _Resp(body)
    _open.seen = seen
    return _open


_NO_NOTICE = json.dumps({"message": {"items": []}}).encode()
_DATACITE = json.dumps({"data": {"attributes": {
    "titles": [{"title": "T"}], "creators": [], "publicationYear": 2024, "version": "1", "dates": [],
    "relatedIdentifiers": [{"relationType": "IsVersionOf", "relatedIdentifierType": "DOI",
                            "relatedIdentifier": "10.1000/published"}]}}}).encode()


def _inner(url, accept):
    if "export.arxiv.org" in url:
        raise _http(429)  # the API refuses, as at the Sprint 7 pre-flight
    if "api.crossref.org" in url:
        return _NO_NOTICE
    if "api.datacite.org" in url:
        return _DATACITE
    raise AssertionError(f"unexpected request {url}")


@pytest.fixture(autouse=True)
def _no_waiting(monkeypatch):
    monkeypatch.setattr(citations, "_sleep", lambda s: None)


# ------------------------------------------------------------ the page parser

def test_the_abstract_page_gives_status_version_and_access_in_one_request():
    site = _site({"2405.12044": _page("2405.12044", jref="Quantum 8, 1475 (2024)", doi="10.22331/q-2024-09-17-1475")})
    r = probes.probe_arxiv_site("p", "2405.12044", citations.PacedFetcher(inner=_inner), _open=site)
    assert r.values == {"publication_status": "published", "version_of": "10.22331/q-2024-09-17-1475"}
    assert r.access == probes.OPEN and r.provider == probes.SITE_PROVIDER
    assert len(site.seen) == 1 and citations.arxiv_requests_this_session() == 1


def test_a_withdrawal_is_read_from_the_banner_or_the_comment():
    for page in (_page("2308.08167", banner=True), _page("2308.08167", comment="This paper has been withdrawn by the authors.")):
        assert probes.parse_arxiv_abs(page.decode(), "2308.08167")[0] is True
    r = probes.probe_arxiv_site("p", "2308.08167", citations.PacedFetcher(inner=_inner),
                                _open=_site({"2308.08167": _page("2308.08167", banner=True)}))
    assert r.values["publication_status"] == "withdrawn"


def test_a_plain_page_is_a_preprint_and_arxivs_own_doi_is_never_the_version():
    assert probes.parse_arxiv_abs(_page("2401.00001").decode(), "2401.00001") == (False, "", "")
    assert probes.parse_arxiv_abs(_page("2401.00001", doi="10.48550/arXiv.2401.00001").decode(),
                                  "2401.00001")[2] == ""


def test_a_page_for_another_record_answers_nothing_regression():
    """A redirect or a challenge page must not become a 'preprint'. Proven
    to fail by injection, 2026-10-06: with the citation_arxiv_id check
    removed, this page parsed as a preprint."""
    assert probes.parse_arxiv_abs(_page("2401.99999").decode(), "2401.00001") is None
    assert probes.parse_arxiv_abs("<html>" + FILLER + "</html>", "2401.00001") is None


def test_when_the_page_does_not_answer_datacite_gives_the_version_and_no_status():
    r = probes.probe_arxiv_site("p", "2401.00001", citations.PacedFetcher(inner=_inner),
                                _open=_site({"2401.00001": _http(429)}))
    assert r.provider == "DataCite" and r.access is None
    assert r.values == {"version_of": "10.1000/published"}


def test_the_cap_is_never_swallowed_by_the_site_probe(monkeypatch):
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 0)
    with pytest.raises(citations.ArxivSessionCapReached):
        probes.probe_arxiv_site("p", "2401.00001", citations.PacedFetcher(inner=_inner),
                                _open=_site({"2401.00001": _page("2401.00001")}))


# ------------------------------------------------------------ the session runner

def _script(monkeypatch, site):
    spec = importlib.util.spec_from_file_location("probe_script_sessions", ROOT / "scripts" / "probe_reference_fields.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "SITE_OPEN", site)
    pauses = []
    monkeypatch.setattr(mod, "_pause", pauses.append)
    return mod, pauses


def _store(tmp_path, ids):
    conn = create_store(tmp_path / "s.db")
    for ident in ids:
        insert_paper(conn, PaperRecord(id=f"p{ident}", tier="seen", access=f"arXiv:{ident}", disposition="d",
                                       context="qml", value="t", citation="C", citation_origin="api",
                                       citation_source="replay", updated="2026-10-06", updated_reason="test"))
    conn.commit()
    return conn


IDS = ["2401.00001", "2401.00002", "2401.00003", "2401.00004", "2401.00005"]


def test_a_capped_run_stops_and_the_next_run_resumes_regression(monkeypatch, tmp_path):
    """Cap 3: the API check takes one request, two pages answer, the third
    page's request would exceed the cap. That record is neither written nor
    marked done; a second run with the same progress file finishes the rest
    and re-probes nothing. Proven to fail by injection, 2026-10-06: with the
    cap handler after the catch-all, the run went on past the cap (rc 0)."""
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 3)
    mod, _ = _script(monkeypatch, _site({i: _page(i) for i in IDS}))
    conn, progress = _store(tmp_path, IDS), tmp_path / "progress.txt"
    targets = mod.select(conn, ["--unprobed"])
    rc = mod.run(conn, targets, citations.PacedFetcher(inner=_inner), apply=True, sessions=False,
                 progress=progress, heartbeat=None)
    assert rc == 2
    assert progress.read_text().split() == ["p2401.00001", "p2401.00002"]
    assert conn.execute("SELECT COUNT(DISTINCT record_id) FROM paper_probes").fetchone()[0] == 2
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 10)
    rc = mod.run(conn, targets, citations.PacedFetcher(inner=_inner), apply=True, sessions=False,
                 progress=progress, heartbeat=None)
    assert rc == 0
    assert sorted(progress.read_text().split()) == sorted(f"p{i}" for i in IDS)
    assert conn.execute("SELECT COUNT(DISTINCT record_id) FROM paper_probes").fetchone()[0] == 5
    conn.close()


def test_sessions_pause_between_caps_and_finish(monkeypatch, tmp_path):
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 3)
    mod, pauses = _script(monkeypatch, _site({i: _page(i) for i in IDS}))
    conn, beat = _store(tmp_path, IDS), tmp_path / "heartbeat.txt"
    rc = mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=True,
                 sessions=True, progress=None, heartbeat=beat)
    assert rc == 0
    assert pauses == [mod.PAUSE_HOURS * 3600] * 2  # 2 + 2 + 1 records over three sessions
    assert "FINISHED" in beat.read_text()
    conn.close()


def test_refusals_end_a_session_early_and_two_quiet_sessions_stop_the_run_regression(monkeypatch, tmp_path):
    """Three no-answers in a row end the session without spending the rest
    of the budget; two such sessions with nothing answered stop the run.
    Proven to fail by injection, 2026-10-06: with MAX_NO_ANSWERS raised to
    99, the first session spent its whole cap on refusals."""
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 50)
    ids = [f"2401.{n:05d}" for n in range(1, 11)]
    site = _site({i: _http(429) for i in ids})
    mod, pauses = _script(monkeypatch, site)
    conn = _store(tmp_path, ids)
    rc = mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=True,
                 sessions=True, progress=None, heartbeat=None)
    assert rc == 3
    assert len(site.seen) == 6 and len(pauses) == 1  # 3 per session, two sessions, one pause between
    conn.close()


def test_a_differing_value_is_reported(monkeypatch, tmp_path, capsys):
    mod, _ = _script(monkeypatch, _site({"2401.00001": _page("2401.00001", jref="J. 1 (2024)")}))
    conn = _store(tmp_path, ["2401.00001"])
    record_probe(conn, "p2401.00001", "publication_status", "preprint", "arXiv", "2026-10-04")
    mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=False,
            sessions=False, progress=None, heartbeat=None)
    assert "DIFFERS p2401.00001 publication_status: stored 'preprint', probe 'published'" in capsys.readouterr().out
    conn.close()
