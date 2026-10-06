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

import http.client
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from store import citations
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
        notice = retraction_notice(doi, fetcher)
        if notice:
            r.values["publication_status"] = "retracted"
            r.notes.append(f"Crossref retraction notice {notice}")
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
        r.provider = "DataCite"
        r.notes.append("not in Crossref; DataCite carries no publication status or retraction notices")
        return r
    kind = msg.get("type", "")
    if kind == "posted-content":
        r.values["publication_status"] = "preprint"
    elif kind in _PUBLISHED_TYPES:
        r.values["publication_status"] = "published"
    else:
        r.notes.append(f"Crossref type {kind!r} is not mapped to a status")
    notice = retraction_notice(doi, fetcher)
    if notice:
        r.values["publication_status"] = "retracted"
        r.notes.append(f"Crossref retraction notice {notice}")
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


def landing_url(access: str) -> str | None:
    """The public page a reader would open for this source."""
    parsed = citations.parse_access(access)
    if parsed:
        kind, ident = parsed
        return {"arxiv": f"https://arxiv.org/abs/{ident}", "doi": f"https://doi.org/{ident}",
                "github": f"https://github.com/{ident}"}[kind]
    _, sep, url = access.partition(" | ")
    return url.strip() if sep and url.strip().startswith("http") else None


def probe_access(url: str, _open=None, timeout: int = 30) -> str | None:
    """What a reader gets at `url`, stated as observed. A paywall cannot be
    told from a page reliably, so it is never claimed; a page that returns
    200 with almost no visible words is a bot challenge or a script shell.

    None means NO ANSWER: a 429, a 5xx, or no connection describes this
    client or the network at that moment, not the source, and must not
    replace the last good measurement (Sprint 6 Phase 5 review)."""
    _open = _open or urllib.request.urlopen
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EvidenceBasedDB access probe)"})
    try:
        with _open(req, timeout=timeout) as resp:
            body = resp.read(400_000)
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as err:
        if err.code == 429 or err.code >= 500:
            return None
        return {401: "refused (HTTP 401)", 403: "refused (HTTP 403)", 404: "not found (HTTP 404)",
                410: "gone (HTTP 410)"}.get(err.code, f"error (HTTP {err.code})")
    except (OSError, http.client.HTTPException):
        return None
    if "html" in ctype and visible_words(body) < 50:
        return "bot challenge or script shell (HTTP 200, under 50 visible words)"
    return "open (HTTP 200)"
