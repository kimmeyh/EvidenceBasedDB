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
    # The refused records were not finished: --unprobed still selects them.
    assert {f"p{i}" for i in ids} <= {t[0] for t in mod.select(conn, ["--unprobed"])}
    conn.close()


def test_a_refused_record_is_retried_then_given_up_so_the_run_ends_regression(monkeypatch, tmp_path):
    """Task C review, 2026-10-06: a refused record was marked done and kept
    only DataCite's version_of, losing its status for good. Now it is
    retried in later sessions, up to MAX_ATTEMPTS, and then given up, so two
    refused records (fewer than MAX_NO_ANSWERS) cannot loop forever.
    Proven to fail by injection, 2026-10-06: with every record marked
    finished again, the progress file held the refused ids after session 1
    and no pause happened."""
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 50)
    ids = ["2401.00001", "2401.00002", "2401.00003"]
    site = _site({"2401.00001": _page("2401.00001"), "2401.00002": _http(429), "2401.00003": _http(429)})
    mod, pauses = _script(monkeypatch, site)
    conn, progress = _store(tmp_path, ids), tmp_path / "progress.txt"
    rc = mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=True,
                 sessions=True, progress=progress, heartbeat=None)
    assert rc == 0
    assert len(pauses) == mod.MAX_ATTEMPTS - 1
    assert site.seen.count("https://arxiv.org/abs/2401.00002") == mod.MAX_ATTEMPTS
    assert sorted(progress.read_text().split()) == [f"p{i}" for i in ids]  # given up, so finished
    status = {r[0] for r in conn.execute("SELECT record_id FROM paper_probes WHERE field = 'publication_status'")}
    assert status == {"p2401.00001"}
    assert [t[0] for t in mod.select(conn, ["--unprobed"])] == ["p2401.00002", "p2401.00003"]
    conn.close()


def test_a_restart_honors_the_saved_pause_and_count_regression(monkeypatch, tmp_path):
    """Task C review, 2026-10-06: the count and the pause lived only in
    memory, so a restart started a fresh session at once. Proven to fail by
    injection, 2026-10-06: with _resume_session returning False at once,
    no wait happened and the count restarted at 0."""
    mod, pauses = _script(monkeypatch, _site({"2401.00001": _page("2401.00001")}))
    monkeypatch.setattr(mod, "_now", lambda: 10_000.0)
    conn, progress = _store(tmp_path, ["2401.00001"]), tmp_path / "progress.txt"
    state = mod._state_path(progress)
    state.write_text(json.dumps({"requests": 7, "last_request": 9_000.0, "paused_until": 12_000.0}))
    mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=False,
            sessions=False, progress=progress, heartbeat=None)
    assert pauses[0] == 2_000.0  # the rest of the saved pause
    state.write_text(json.dumps({"requests": 7, "last_request": 9_999.0, "paused_until": None}))
    citations.reset_arxiv_session()
    assert mod._resume_session(state) is True
    assert citations.arxiv_requests_this_session() == 7
    assert pauses[-1] == pytest.approx(citations.ARXIV_MIN_INTERVAL_S - 1.0)
    conn.close()


def test_a_new_run_waits_before_its_first_arxiv_request_regression(monkeypatch, tmp_path):
    """The pacing clock is per process; a run started right after another
    sent its first request 0.3 s in (2026-10-06). Proven to fail by
    injection, 2026-10-06: without the assume_recent_arxiv_request call in
    run(), the first request did not wait."""
    waits = []
    monkeypatch.setattr(citations, "_sleep", waits.append)
    monkeypatch.setattr(citations, "_monotonic", lambda: 500.0)
    mod, _ = _script(monkeypatch, _site({"2401.00001": _page("2401.00001")}))
    conn = _store(tmp_path, ["2401.00001"])
    mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=False,
            sessions=False, progress=None, heartbeat=None, force_site=True)
    assert waits and waits[0] == citations.ARXIV_MIN_INTERVAL_S
    conn.close()


def test_api_mode_takes_a_withdrawal_from_the_page_regression(monkeypatch):
    """Live check, 2026-10-06: the abstract page showed all 6 recorded
    withdrawals; the API comment showed 2. In API mode the page is fetched
    anyway (for access), so its withdrawal wins. Proven to fail by
    injection, 2026-10-06: without the override, the status was the API's
    'preprint'."""
    atom = (b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" '
            b'xmlns:arxiv="http://arxiv.org/schemas/atom"><entry><id>http://arxiv.org/abs/2401.00001v2</id>'
            b'<title>T</title><arxiv:comment>Not needed anymore</arxiv:comment></entry></feed>')

    def inner(url, accept):
        return atom if "export.arxiv.org" in url else _inner(url, accept)
    mod, _ = _script(monkeypatch, _site({"2401.00001": _page("2401.00001", banner=True)}))
    found, notes, answered = mod.probe("p", "arXiv:2401.00001", "arxiv", citations.PacedFetcher(inner=inner), "api")
    assert ("publication_status", "withdrawn", probes.SITE_PROVIDER) in found
    assert ("access_status", probes.OPEN, "HTTP probe") in found and answered is True
    assert citations.arxiv_requests_this_session() == 2


def test_a_crossref_failure_keeps_the_page_result(monkeypatch):
    def inner(url, accept):
        if "api.crossref.org" in url:
            raise _http(503)
        return _inner(url, accept)
    r = probes.probe_arxiv_site("p", "2405.12044", citations.PacedFetcher(inner=inner),
                                _open=_site({"2405.12044": _page("2405.12044", doi="10.22331/q-1")}))
    assert r.values == {"publication_status": "published", "version_of": "10.22331/q-1"}
    assert any("retraction check did not answer" in n for n in r.notes)


def test_an_arxiv_block_or_a_foreign_page_records_no_access():
    """A 403 from arXiv is its block on this client; an open page that is
    not this paper's page says nothing about the paper."""
    fetcher = citations.PacedFetcher(inner=_inner)
    r = probes.probe_arxiv_site("p", "2401.00001", fetcher, _open=_site({"2401.00001": _http(403)}))
    assert r.access is None
    r = probes.probe_arxiv_site("p", "2401.00001", fetcher, _open=_site({"2401.00001": _page("2401.99999")}))
    assert r.access is None and "publication_status" not in r.values
    assert any("access not recorded" in n for n in r.notes)
    r = probes.probe_arxiv_site("p", "2401.00001", fetcher, _open=_site({"2401.00001": _http(404)}))
    assert r.access == "not found (HTTP 404)"
    # The note says what was done with the access value (Copilot, PR #68):
    # a 404 is about the paper and is recorded, so the note must not say
    # "not recorded". Proven to fail by injection, 2026-10-10: with the
    # note text restored to the unconditional "access not recorded", this
    # assertion went red.
    assert any("(not found (HTTP 404)); access recorded" in n for n in r.notes), r.notes


def test_api_mode_costs_two_requests_per_paper_and_stops_at_the_cap(monkeypatch, tmp_path):
    """When the API answers its session check, each paper costs the API
    request plus the abstract page for access. Cap 4: the check, then one
    paper (2), then the next paper's API request (4th); its access request
    would be the 5th and raises, so that paper is not written."""
    monkeypatch.setattr(citations, "ARXIV_SESSION_CAP", 4)
    atom = (b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" '
            b'xmlns:arxiv="http://arxiv.org/schemas/atom"><entry><id>http://arxiv.org/abs/2401.00001v1</id>'
            b'<title>T</title></entry></feed>')

    def inner(url, accept):
        return atom if "export.arxiv.org" in url else _inner(url, accept)
    mod, _ = _script(monkeypatch, _site({i: _page(i) for i in IDS}))
    conn = _store(tmp_path, IDS)
    rc = mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=inner), apply=True,
                 sessions=False, progress=None, heartbeat=None)
    assert rc == 2 and citations.arxiv_requests_this_session() == 4
    written = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_probes")}
    assert written == {"p2401.00001"}
    conn.close()


def test_a_differing_value_is_reported(monkeypatch, tmp_path, capsys):
    mod, _ = _script(monkeypatch, _site({"2401.00001": _page("2401.00001", jref="J. 1 (2024)")}))
    conn = _store(tmp_path, ["2401.00001"])
    record_probe(conn, "p2401.00001", "publication_status", "preprint", "arXiv", "2026-10-04")
    mod.run(conn, mod.select(conn, ["--all"]), citations.PacedFetcher(inner=_inner), apply=False,
            sessions=False, progress=None, heartbeat=None)
    assert "DIFFERS p2401.00001 publication_status: stored 'preprint', probe 'published'" in capsys.readouterr().out
    conn.close()


# ------------------------------------------------------------ F53: stale probes

def test_a_stale_probe_is_reported_and_fails_the_check_regression(monkeypatch, tmp_path, capsys):
    """F53: a probe measured before the cycle start is listed and the check
    exits 1; a fresh one, or a hand-recorded reading, is not. Proven to fail
    by injection, 2026-10-06: with the date comparison made always false,
    nothing was reported and the check exited 0."""
    mod, _ = _script(monkeypatch, None)
    conn = _store(tmp_path, ["2401.00001", "2401.00002", "2401.00003"])
    record_probe(conn, "p2401.00001", "publication_status", "preprint", "arXiv", "2026-10-03")    # stale
    record_probe(conn, "p2401.00002", "publication_status", "preprint", "arXiv", "2026-10-06")    # fresh
    record_probe(conn, "p2401.00003", "publication_status", "withdrawn", "hand", "2026-10-01",
                 anchor="the abstract page, read 2026-10-01")                                        # a reading
    assert mod.report_stale(conn, "2026-10-06") == 1
    out = capsys.readouterr().out
    assert "STALE p2401.00001 publication_status [arXiv] probed 2026-10-03" in out
    assert "p2401.00002" not in out and "p2401.00003" not in out
    record_probe(conn, "p2401.00001", "publication_status", "preprint", "arXiv", "2026-10-07")
    assert mod.report_stale(conn, "2026-10-06") == 0
    conn.close()


def test_refresh_selects_stale_and_unprobed_records(monkeypatch, tmp_path):
    mod, _ = _script(monkeypatch, None)
    monkeypatch.setattr(mod, "cycle_start", lambda: "2026-10-06")
    conn = _store(tmp_path, ["2401.00001", "2401.00002", "2401.00003"])
    record_probe(conn, "p2401.00001", "access_status", "open (HTTP 200)", "HTTP probe", "2026-10-03")
    record_probe(conn, "p2401.00002", "access_status", "open (HTTP 200)", "HTTP probe", "2026-10-06")
    assert [t[0] for t in mod.select(conn, ["--refresh"])] == ["p2401.00001", "p2401.00003"]
    conn.close()


def test_the_cycle_start_is_computed_from_the_sprint_branch(monkeypatch, tmp_path):
    mod, _ = _script(monkeypatch, None)
    status = tmp_path / "sprint_status.json"
    status.write_text(json.dumps({"current_sprint": {"branch": "feature/20261006_Sprint_7"}}))
    assert mod.cycle_start(status) == "2026-10-06"
    status.write_text(json.dumps({"current_sprint": {"branch": "main"}}))
    with pytest.raises(ValueError):
        mod.cycle_start(status)
    assert len(mod.cycle_start()) == 10  # the real file parses
