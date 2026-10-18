"""Resolvers for the COMPUTED reference fields (ADR-0005 A4 (b), Sprint 6 Task F).

`publication_status`, `version_of`, `access_status` and affiliations are
determinate facts, so they are computed from the registry, never typed.
The store keeps only each probe's last result with its date and provider
(the probe rule; `store.ingest.record_probe`). This module computes; it
writes nothing.

A probe that cannot answer says so (it returns no value for that field),
and the field stays unset: a guess recorded as a measurement is worse than
a gap. In particular, a withdrawal is visible only in arXiv's own record
(the comment), so when arXiv refuses and DataCite answers, the status is
left unanswered rather than called a preprint.
"""
from __future__ import annotations

import html
import http.client
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from store import citations, recheck
from store.citations import _ATOM, _safe_xml_root
from store.ingest import visible_words

_WITHDRAWN_WORDS = ("withdrawn", "withdraw this paper", "has been withdrawn")
_PUBLISHED_TYPES = ("journal-article", "proceedings-article", "book-chapter", "book", "monograph", "report",
                    "dissertation", "edited-book", "reference-entry", "standard")


@dataclass
class ProbeResult:
    record_id: str
    provider: str = ""
    values: dict[str, str] = field(default_factory=dict)  # field name -> value
    notes: list[str] = field(default_factory=list)       # what could not be answered, and why
    # access_status observed by the SAME request (the arXiv site probe), so
    # the caller does not spend a second request on it; None = not observed.
    access: str | None = None
    # The latest version the abstract page shows (ADR-0005 A7 (d)); None =
    # not read. Set only by the site probe.
    latest_version: int | None = None
    # The DOI registry answered, even if it stated nothing the store records
    # (Task D review, 2026-10-18), so the re-check report can say so instead
    # of "no answer". Set only by probe_doi.
    answered: bool = False


def _arxiv_entry(ident: str, fetcher) -> tuple[str, str, str, list[str]] | None:
    """(comment, journal_ref, doi, affiliations) from arXiv's own record, or
    None when arXiv returned no entry."""
    root = _safe_xml_root(fetcher(f"{citations.ARXIV_API}?id_list={ident}", "application/atom+xml"))
    for e in root.findall("a:entry", _ATOM):
        if not (e.findtext("a:title", default="", namespaces=_ATOM) or "").strip():
            continue
        comment = " ".join((e.findtext("arxiv:comment", default="", namespaces=_ATOM) or "").split())
        jref = " ".join((e.findtext("arxiv:journal_ref", default="", namespaces=_ATOM) or "").split())
        doi = (e.findtext("arxiv:doi", default="", namespaces=_ATOM) or "").strip()
        affs = sorted({" ".join((a.text or "").split()) for a in e.iter(f"{{{_ATOM['arxiv']}}}affiliation")
                       if (a.text or "").strip()})
        return comment, jref, doi, affs
    return None


def retraction_notice(doi: str, fetcher) -> str | None:
    """The DOI of a Crossref retraction notice that points at `doi`, if any.
    Crossref answers a retraction through the NOTICE (`updates:` filter),
    not through the article's own record (pre-flight, 2026-10-03)."""
    url = f"https://api.crossref.org/works?filter=updates:{urllib.parse.quote(doi, safe='/')}&rows=5"
    items = json.loads(fetcher(url, "application/json"))["message"]["items"]
    for item in items:
        for upd in item.get("update-to", []):
            if upd.get("type") == "retraction" and upd.get("DOI", "").lower() == doi.lower():
                return item.get("DOI")
    return None


_CROSSREF_FAILURES = (OSError, ValueError, KeyError, TypeError, http.client.HTTPException)


def _check_retraction(r: ProbeResult, doi: str, fetcher) -> None:
    """Apply a Crossref retraction notice to `r`. A Crossref failure is a
    note, never an exception: it must not throw away the status the
    registry already answered (Task C review, 2026-10-06), and the status
    stays as answered, with the unchecked notice said."""
    try:
        notice = retraction_notice(doi, fetcher)
    except _CROSSREF_FAILURES as ex:
        r.notes.append(f"Crossref retraction check did not answer ({type(ex).__name__}); not checked this run")
        return
    if notice:
        r.values["publication_status"] = "retracted"
        r.notes.append(f"Crossref retraction notice {notice}")


def probe_arxiv(record_id: str, ident: str, fetcher) -> ProbeResult:
    r = ProbeResult(record_id)
    try:
        got = _arxiv_entry(ident, fetcher)
    except citations.ARXIV_FAILURES:
        # Any arXiv failure goes to DataCite (team lead, 2026-10-04): the full
        # run of 2026-10-03 lost 8 of 142 ids to read timeouts.
        got = None
    if got is None:
        r.provider = "DataCite"
        md = citations.parse_datacite_arxiv(fetcher(
            citations.DATACITE_API + urllib.parse.quote(citations.ARXIV_DOI_PREFIX + ident, safe="/."),
            "application/vnd.api+json"), ident)
        if md.doi and not md.doi.lower().startswith("10.48550/"):
            r.values["version_of"] = md.doi
        r.notes.append("arXiv did not answer; publication_status left unanswered (a withdrawal shows only in arXiv's comment)")
        return r
    r.provider = "arXiv"
    comment, jref, doi, affs = got
    if any(w in comment.lower() for w in _WITHDRAWN_WORDS):
        r.values["publication_status"] = "withdrawn"
    elif jref or doi:
        r.values["publication_status"] = "published"
    else:
        r.values["publication_status"] = "preprint"
    if doi:
        r.values["version_of"] = doi
        _check_retraction(r, doi, fetcher)
    if affs:
        r.values["affiliations"] = "; ".join(affs)
    return r


def probe_doi(record_id: str, doi: str, fetcher) -> ProbeResult:
    r = ProbeResult(record_id, provider="Crossref")
    quoted = urllib.parse.quote(doi, safe="/")
    try:
        msg = json.loads(fetcher(citations.CROSSREF_API + quoted, "application/json"))["message"]
    except urllib.error.HTTPError as err:
        if err.code != 404:
            raise
        return _probe_datacite(r, quoted, fetcher)
    r.answered = True
    kind = msg.get("type", "")
    if kind == "posted-content":
        r.values["publication_status"] = "preprint"
    elif kind in _PUBLISHED_TYPES:
        r.values["publication_status"] = "published"
    else:
        r.notes.append(f"Crossref type {kind!r} is not mapped to a status")
    _check_retraction(r, doi, fetcher)
    rel = msg.get("relation") or {}
    for key in ("is-preprint-of", "has-preprint"):
        for item in rel.get(key, []):
            if item.get("id"):
                r.values["version_of"] = item["id"]
                break
    affs = sorted({" ".join(a.get("name", "").split()) for au in msg.get("author", [])
                   for a in au.get("affiliation", []) if a.get("name")})
    if affs:
        r.values["affiliations"] = "; ".join(affs)
    return r


# DataCite's resourceTypeGeneral values that say where a work stands. Any
# other value (Text, Dataset, Software, ...) is not guessed.
_DATACITE_STATUS = {"Preprint": "preprint", "JournalArticle": "published", "ConferencePaper": "published",
                    "Book": "published", "BookChapter": "published", "Dissertation": "published",
                    "Report": "published"}
# Only a preprint relation names another version of the paper. Zenodo's
# IsVersionOf names its all-versions ("concept") DOI, which is the same
# work, so it is not a version_of.
_DATACITE_VERSION = ("IsPreprintOf", "HasPreprint")


def _probe_datacite(r: ProbeResult, quoted: str, fetcher) -> ProbeResult:
    """A DOI Crossref does not know, asked of DataCite (F86, Sprint 10 Task
    D). Until then this branch labeled the result DataCite without sending
    the request, so a DataCite DOI never recorded a primary answer and
    stayed due forever under ADR-0005 A9. DataCite carries no retraction
    notices; that is said, not assumed away."""
    r.provider = "DataCite"
    try:
        attrs = json.loads(fetcher(citations.DATACITE_API + quoted, "application/vnd.api+json"))["data"]["attributes"]
    except urllib.error.HTTPError as err:
        if err.code != 404:
            raise
        r.notes.append("not in Crossref and not in DataCite")
        return r
    r.answered = True
    general = (attrs.get("types") or {}).get("resourceTypeGeneral", "")
    if general in _DATACITE_STATUS:
        r.values["publication_status"] = _DATACITE_STATUS[general]
    else:
        r.notes.append(f"DataCite resourceTypeGeneral {general!r} is not mapped to a status")
    for rel in attrs.get("relatedIdentifiers") or []:
        if rel.get("relationType") in _DATACITE_VERSION and rel.get("relatedIdentifier"):
            r.values["version_of"] = rel["relatedIdentifier"]
            break
    affs = sorted({" ".join((a if isinstance(a, str) else a.get("name") or "").split())
                   for c in attrs.get("creators") or [] for a in c.get("affiliation") or []} - {""})
    if affs:
        r.values["affiliations"] = "; ".join(affs)
    r.notes.append("not in Crossref; DataCite answered (it carries no retraction notices)")
    return r


def landing_url(access: str) -> str | None:
    """The public page a reader would open for this source."""
    parsed = citations.parse_access(access)
    if parsed:
        kind, ident = parsed
        return {"arxiv": f"https://arxiv.org/abs/{ident}", "doi": f"https://doi.org/{ident}",
                "github": f"https://github.com/{ident}"}[kind]
    _, sep, url = access.partition(" | ")
    return url.strip() if sep and url.strip().startswith("http") else None


OPEN = "open (HTTP 200)"


def _observe(url: str, _open=None, timeout: int = 30) -> tuple[str | None, bytes | None]:
    """(access status, body). The body is returned only for an open page."""
    _open = _open or urllib.request.urlopen
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EvidenceBasedDB access probe)"})
    try:
        with _open(req, timeout=timeout) as resp:
            body = resp.read(400_000)
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as err:
        if err.code == 429 or err.code >= 500:
            return None, None
        if err.code == 403 and citations.is_arxiv_host(url):
            # arXiv blocks a client with 403: a fact about this client, not
            # the paper, so no answer (Task C review, 2026-10-06).
            return None, None
        return {401: "refused (HTTP 401)", 403: "refused (HTTP 403)", 404: "not found (HTTP 404)",
                410: "gone (HTTP 410)"}.get(err.code, f"error (HTTP {err.code})"), None
    except (OSError, http.client.HTTPException):
        return None, None
    if "html" in ctype and visible_words(body) < 50:
        return "bot challenge or script shell (HTTP 200, under 50 visible words)", None
    return OPEN, body


def probe_access(url: str, _open=None, timeout: int = 30) -> str | None:
    """What a reader gets at `url`, stated as observed. A paywall cannot be
    told from a page reliably, so it is never claimed; a page that returns
    200 with almost no visible words is a bot challenge or a script shell.

    None means NO ANSWER: a 429, a 5xx, or no connection describes this
    client or the network at that moment, not the source, and must not
    replace the last good measurement (Sprint 6 Phase 5 review)."""
    return _observe(url, _open, timeout)[0]


# ------------------------------------------------------------- arXiv's site
# Sprint 7 Task C (F52, Q5 = 1): while the API answers 429, arXiv's abstract
# page is the source. Markers read from two live pages on 2026-10-06
# (2308.08167, withdrawn; 2405.12044, published in Quantum).
SITE_PROVIDER = "arXiv abstract page"
_PAGE_ID = re.compile(r'<meta name="citation_arxiv_id" content="([^"]+)"')
_WITHDRAWN_BANNER = re.compile(r'<span class="error"[^>]*>[^<]*has been withdrawn', re.IGNORECASE)
_COMMENTS_CELL = re.compile(r'<td class="tablecell comments[^"]*">(.*?)</td>', re.DOTALL)
_JREF_CELL = re.compile(r'<td class="tablecell jref">(.*?)</td>', re.DOTALL)
# The published version's DOI. Never `tablecell arxivdoi`: that is arXiv's
# own 10.48550 DOI for the preprint itself.
_RELATED_DOI = re.compile(r'<td class="tablecell doi">.*?data-doi="([^"]+)"', re.DOTALL)
_CITATION_DOI = re.compile(r'<meta name="citation_doi" content="([^"]+)"')
_TAG = re.compile(r"<[^>]+>")


def parse_arxiv_abs(page: str, ident: str) -> tuple[bool, str, str] | None:
    """(withdrawn, journal_ref, doi) from an abstract page, or None when the
    page is not arXiv's page for `ident` (a challenge page, a redirect
    elsewhere): an unrecognized page answers nothing."""
    m = _PAGE_ID.search(page)
    if not m or m.group(1).split("v")[0] != ident:
        return None
    comment_cell = _COMMENTS_CELL.search(page)
    comment = html.unescape(_TAG.sub(" ", comment_cell.group(1))) if comment_cell else ""
    withdrawn = bool(_WITHDRAWN_BANNER.search(page)) or any(w in comment.lower() for w in _WITHDRAWN_WORDS)
    jref_cell = _JREF_CELL.search(page)
    jref = " ".join(html.unescape(_TAG.sub(" ", jref_cell.group(1))).split()) if jref_cell else ""
    doi_m = _RELATED_DOI.search(page) or _CITATION_DOI.search(page)
    doi = html.unescape(doi_m.group(1)).strip() if doi_m else ""
    if doi.lower().startswith("10.48550/"):
        doi = ""
    return withdrawn, jref, doi


def probe_arxiv_site(record_id: str, ident: str, fetcher, _open=None) -> ProbeResult:
    """publication_status, version_of and access_status from ONE request to
    arXiv's abstract page, paced and counted by `fetcher.wait_for` (the
    session cap raises from there and is never caught here). Affiliations
    are not on the page and are left unanswered. When the page does not
    answer, DataCite gives version_of, as with the API (team lead,
    2026-10-04: "If a request fails on arxiv, then try via DataCite")."""
    r = ProbeResult(record_id)
    url = f"https://arxiv.org/abs/{ident}"
    if hasattr(fetcher, "wait_for"):
        fetcher.wait_for(url)
    r.access, body = _observe(url, _open)
    parsed = parse_arxiv_abs(body.decode("utf-8", "replace"), ident) if body else None
    if parsed is None:
        seen = r.access
        # An "open" page that is not arXiv's page for this id (a challenge,
        # a redirect) says nothing about the paper's access either. A 404 or
        # 410 from arXiv is about the paper, and stays.
        if seen == OPEN or (seen or "").startswith("bot challenge"):
            r.access = None
        r.notes.append("arXiv's abstract page did not answer" if seen is None else
                       f"arXiv's abstract page gave no record ({seen}); access "
                       + ("not recorded" if r.access is None else "recorded"))
        try:
            md = citations.parse_datacite_arxiv(fetcher(
                citations.DATACITE_API + urllib.parse.quote(citations.ARXIV_DOI_PREFIX + ident, safe="/."),
                "application/vnd.api+json"), ident)
        except (OSError, ValueError, KeyError, http.client.HTTPException) as ex:
            r.notes.append(f"DataCite did not answer either ({type(ex).__name__})")
            return r
        r.provider = "DataCite"
        if md.doi and not md.doi.lower().startswith("10.48550/"):
            r.values["version_of"] = md.doi
        r.notes.append("publication_status left unanswered (a withdrawal shows only on arXiv)")
        return r
    r.provider = SITE_PROVIDER
    r.latest_version = recheck.latest_version(body.decode("utf-8", "replace"))
    withdrawn, jref, doi = parsed
    if withdrawn:
        r.values["publication_status"] = "withdrawn"
    elif jref or doi:
        r.values["publication_status"] = "published"
    else:
        r.values["publication_status"] = "preprint"
    if doi:
        r.values["version_of"] = doi
        _check_retraction(r, doi, fetcher)
    r.notes.append("affiliations are not on the abstract page; left unanswered")
    return r
