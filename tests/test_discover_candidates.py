"""scripts/discover_candidates.py (F62 pilot): no network; OpenAlex answers
are fixtures shaped like the real response."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _mod():
    spec = importlib.util.spec_from_file_location("discover", ROOT / "scripts" / "discover_candidates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WORK = {
    "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1109/QAI.2025.33", "title": "Explaining  Anomalies",
    "publication_year": 2024, "cited_by_count": 10,
    "open_access": {"oa_status": "green", "oa_url": "https://arxiv.org/pdf/2505.03911"},
    "abstract_inverted_index": {"tensor": [1], "We": [0], "networks": [2]},
    "primary_location": {"source": {"display_name": "QAI", "host_organization_name": "IEEE"}},
    "locations": [{"landing_page_url": "https://arxiv.org/abs/2505.03911"}],
    "primary_topic": {"display_name": "Anomaly Detection"},
}


def test_the_key_goes_only_in_the_header_regression():
    """A key in the URL reaches logs and exception messages. Proven to fail
    by injection, 2026-10-06: with api_key added to the query parameters,
    the URL assertion went red."""
    req = _mod().request_for({"search": "x"}, "SECRET-KEY")
    assert "SECRET-KEY" not in req.full_url
    assert req.get_header("Authorization") == "Bearer SECRET-KEY"
    assert _mod().request_for({"search": "x"}, None).get_header("Authorization") is None


def test_a_candidate_carries_abstract_rank_and_free_copy():
    c = _mod().candidate(WORK, "tensor", date(2026, 10, 6))
    assert c["abstract"] == "We tensor networks"
    assert c["doi"] == "10.1109/QAI.2025.33" and c["arxiv"] == "2505.03911"
    assert c["cites_per_year"] == round(10 / 3, 1) and c["title"] == "Explaining Anomalies"


def test_store_duplicates_are_found_by_doi_arxiv_or_title_regression():
    """Proven to fail by injection, 2026-10-06: with the title check
    removed from held_by_store, the title-only duplicate came back None."""
    mod = _mod()
    c = mod.candidate(WORK, "tensor", date(2026, 10, 6))
    assert mod.held_by_store(c, ({"10.1109/qai.2025.33"}, set(), set())) == "doi"
    assert mod.held_by_store(c, (set(), {"2505.03911"}, set())) == "arxiv"
    assert mod.held_by_store(c, (set(), set(), {mod.norm_title("Explaining anomalies!")})) == "title"
    assert mod.held_by_store(c, (set(), set(), set())) is None


def test_it_refuses_to_write_inside_the_repository(capsys):
    assert _mod().main(["--out", str(ROOT / "discovery")]) == 2
    assert "inside the repository" in capsys.readouterr().err


def test_a_stream_request_uses_the_stream_spec():
    seen = []

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"results": [WORK]}).encode()

    def opener(req, timeout):
        seen.append(req.full_url)
        return Resp()
    assert _mod().fetch_stream("fraud", 5, None, opener=opener) == [WORK]
    assert "title.search%3Afraud" in seen[0] and "title_and_abstract.search" in seen[0] and "per_page=5" in seen[0]


# ---------------------------------------------------------------- Sprint 9 Task J (Q8 rubric)

def _cand(mod, **kw):
    c = mod.candidate(WORK, "qml", date(2026, 10, 15))
    c.update(kw)
    return c


def test_semantic_scholar_count_ranks_and_a_disagreement_is_flagged():
    """OpenAlex merged-record errors inflate counts (Sprint 7 pilot).
    Proven to fail by injection, 2026-10-15: with score() keeping the
    OpenAlex count when Semantic Scholar answered, this test went red."""
    mod = _mod()
    c = _cand(mod, cited_by=78458, year=2024, title="A tutoring paper", abstract="",
              s2_status="answered", s2_cites=3000, s2_year=2024)
    s = mod.score(c, date(2026, 10, 15))
    assert s["rank_cites"] == 3000 and s["score"] == 1000.0
    assert s["citation_check"].startswith("DISAGREE")


def test_a_context_match_earns_the_bonus_and_unchecked_stays_openalex():
    mod = _mod()
    plain = mod.score(_cand(mod, cited_by=30, year=2024, title="Deep nets", abstract=""), date(2026, 10, 15))
    fraud = mod.score(_cand(mod, cited_by=30, year=2024, title="Credit card fraud detection", abstract=""),
                      date(2026, 10, 15))
    assert plain["score"] == 10.0 and plain["citation_check"] == "unchecked" and plain["contexts"] == []
    assert fraud["score"] == 15.0 and fraud["contexts"] == ["hsbc-2026"]


def test_an_unchecked_count_never_outranks_a_checked_one():
    """Proven to fail by injection, 2026-10-15: with rank_key sorting by
    score alone, the unchecked 45,780-citation record came first."""
    mod = _mod()
    today = date(2026, 10, 15)
    bogus = _cand(mod, title="AutoResearch Lite", cited_by=45780, year=2026, abstract="", s2_status="not found")
    real = _cand(mod, title="Attention", cited_by=24487, year=2017, abstract="", s2_status="answered",
                 s2_cites=196851, s2_year=2017)
    for c in (bogus, real):
        c.update(mod.score(c, today))
    assert [c["title"] for c in sorted([bogus, real], key=mod.rank_key)] == ["Attention", "AutoResearch Lite"]


def test_duplicate_titles_collapse_to_the_most_cited():
    mod = _mod()
    a = _cand(mod, title="Attention Is All You Need", cited_by=5)
    b = _cand(mod, title="Attention is all you need!", cited_by=90000)
    kept, n = mod.collapse_duplicates([a, b])
    assert n == 1 and kept == [b]


def test_a_refusal_leaves_a_candidate_unchecked_never_guessed():
    import io
    import urllib.error
    mod = _mod()

    def refuse(code):
        def f(url):
            raise urllib.error.HTTPError(url, code, "x", {}, io.BytesIO())
        return f
    c = _cand(mod, arxiv=None)
    waits = []
    assert mod.s2_check(c, refuse(429), waits.append) == {"s2_status": "unchecked (HTTP 429)"}
    assert waits == list(mod.S2_BACKOFF_S)
    assert mod.s2_check(c, refuse(404), waits.append) == {"s2_status": "not found"}


def test_a_429_is_retried_and_a_doi_miss_falls_back_to_arxiv():
    """Sprint 9 Task J's first run: 52 of 192 requests refused, and the ml
    list's top three (OpenAlex record errors) went unchecked.
    Proven to fail by injection, 2026-10-15: with the arXiv fallback
    removed, the second case came back 'not found'."""
    import io
    import urllib.error
    mod = _mod()
    calls = []

    def flaky(url):
        calls.append(url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(url, 429, "x", {}, io.BytesIO())
        return json.dumps({"citationCount": 7, "year": 2017, "title": "Explaining Anomalies"}).encode()
    assert mod.s2_check(_cand(mod), flaky, lambda s: None)["s2_cites"] == 7 and len(calls) == 2

    def doi_missing(url):
        if "DOI:" in url:
            raise urllib.error.HTTPError(url, 404, "x", {}, io.BytesIO())
        return json.dumps({"citationCount": 150000, "year": 2017, "title": "Explaining anomalies"}).encode()
    got = mod.s2_check(_cand(mod, doi="10.65215/2q58a426", arxiv="1706.03762"), doi_missing, lambda s: None)
    assert got["s2_status"] == "answered" and got["s2_year"] == 2017


def test_the_hand_list_names_the_file_and_records_every_search():
    mod = _mod()
    c = _cand(mod, arxiv=None, oa_url=None, s2_status="answered", s2_arxiv=None, s2_pdf=None,
              title="Fraud: A Study", first_author="Müller", date="2024-03-05", doi="10.1/x")
    c.update(mod.score(c, date(2026, 10, 15)))
    text = mod.render_hand_list({"fraud": [c]}, date(2026, 10, 15))
    assert "2024-03_Muller_Fraud-A-Study.pdf" in text and "https://doi.org/10.1/x" in text
    assert "Semantic Scholar open PDF: none (answered)" in text and "OpenAlex open-access URL: none" in text


def test_semantic_scholar_requests_are_paced_and_no_output_holds_the_key(tmp_path, monkeypatch):
    """Proven to fail by injection, 2026-10-15: with the sleep before each
    Semantic Scholar request after the first removed, waits was empty; with
    the key written into the review header, the file check went red. (The
    first version also asserted no Semantic Scholar URL held the key, which
    could not fail: s2_check never receives it. Task J review.)"""
    mod = _mod()
    monkeypatch.setattr(mod, "fetch_stream", lambda stream, per, key: [WORK])
    monkeypatch.setattr(mod, "store_keys", lambda conn: (set(), set(), set()))
    monkeypatch.setattr(mod, "openalex_key", lambda: "SECRET-KEY")
    monkeypatch.setattr(mod.sqlite3, "connect", lambda *a, **k: type("C", (), {"close": lambda self: None})())
    urls, waits = [], []

    def s2(url):
        urls.append(url)
        return json.dumps({"citationCount": 9, "year": 2024, "title": "Explaining Anomalies"}).encode()
    assert mod.main(["--out", str(tmp_path)], s2_fetch=s2, sleep=waits.append) == 0
    assert len(urls) == len(mod.STREAMS) and waits == [mod.S2_INTERVAL_S] * (len(mod.STREAMS) - 1)
    written = list(tmp_path.iterdir())
    assert len(written) == 3 and not any("SECRET-KEY" in f.read_text(encoding="utf-8") for f in written)


def test_a_different_paper_is_a_mismatch_never_a_count():
    """Task J review: a 2026 record came back as a 2021 work with 9
    citations and its count won. Proven to fail by injection, 2026-10-15:
    with same_title always true, the mismatch came back 'answered'."""
    mod = _mod()
    other = lambda url: json.dumps({"citationCount": 9, "year": 2021, "title": "Something else"}).encode()
    got = mod.s2_check(_cand(mod, arxiv=None), other, lambda s: None)
    assert got["s2_status"].startswith("mismatch") and "s2_cites" not in got
    assert mod.score(_cand(mod, **got), date(2026, 10, 15))["citation_check"] == "unchecked"


def test_the_earlier_year_is_used():
    """Task J review: changing min to max passed every test. Proven to fail
    by injection, 2026-10-15: with max, rank_year was 2024, not 2017."""
    mod = _mod()
    c = _cand(mod, cited_by=100, year=2024, title="X", abstract="", s2_status="answered", s2_cites=100,
              s2_year=2017)
    assert mod.score(c, date(2026, 10, 15))["rank_year"] == 2017


def test_no_bonus_inside_a_streams_own_context_and_dirac_is_anchored():
    """Task J review: every fraud record and 57 of 59 qml records took the
    bonus, and "dirac" matched the Dirac equation. Proven to fail by
    injection, 2026-10-15: with STREAM_CONTEXT emptied, the fraud score was
    15.0, not 10.0."""
    mod = _mod()
    today = date(2026, 10, 15)
    fraud = _cand(mod, stream="fraud", cited_by=30, year=2024, title="Credit card fraud", abstract="")
    assert mod.score(fraud, today)["score"] == 10.0
    assert mod.score(dict(fraud, stream="ml"), today)["score"] == 15.0
    assert mod.context_matches(_cand(mod, title="The Dirac equation", abstract="")) == []
    assert mod.context_matches(_cand(mod, title="Benchmarks on Dirac-3", abstract="")) == ["platform"]


def test_books_go_to_books_and_names_keep_particles_and_hyphens():
    mod = _mod()
    book = _cand(mod, type="book", title="Supervised Learning with Quantum Computers", publisher="Springer",
                 year=2018)
    assert mod.target_folder(book) == "Books"
    assert mod.target_name(book) == "Book - Supervised Learning with Quantum Computers - Springer 2018.pdf"
    work = dict(WORK, authorships=[{"author": {"display_name": "Andrea Dal Pozzolo"}}])
    paper = mod.candidate(work, "fraud", date(2026, 10, 15))
    paper.update(title="Human-level control", date="2015-02-25")
    assert mod.target_folder(paper) == "Papers"
    assert mod.target_name(paper) == "2015-02_Dal-Pozzolo_Human-level-control.pdf"


def test_a_redirect_to_another_host_drops_the_key():
    """Proven to fail by injection, 2026-10-15: with the remove_header line
    removed, the redirected request still carried Authorization."""
    import io
    mod = _mod()
    req = mod.request_for({"search": "x"}, "SECRET-KEY")
    handler = mod.DropAuthOnHostChange()
    away = handler.redirect_request(req, io.BytesIO(), 302, "Found", {}, "https://elsewhere.example/works")
    home = handler.redirect_request(req, io.BytesIO(), 302, "Found", {}, "https://api.openalex.org/works?page=2")
    assert away.get_header("Authorization") is None
    assert home.get_header("Authorization") == "Bearer SECRET-KEY"
