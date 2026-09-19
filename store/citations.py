"""Bibliographic metadata from the source of record, never from a keyboard
(Sprint 4 Task B, F25 C1).

ADR-0005 section 2: `citation` is "pulled from an API, never hand-typed".
Nothing enforced that through Sprint 3, and the F10 review found the
predictable consequences in the seed set -- a wrong title (dupont), a
dropped author (kordzanganeh), a citation with no year and an id carrying
the wrong one (rand), a duplicate-file claim that hashing disproved
(mancilla), six preprints superseded by published versions the records
never mention. This module is the one place bibliographic data enters the
store: an `access` id (arXiv or DOI) goes in, a canonical citation string
and a title come out.

Providers: arXiv (Atom API), Crossref (DOI), DataCite (DOI, tried when
Crossref does not know the DOI). Pre-flight at Sprint 4 planning
(2026-09-19): all three reachable; **arXiv returns HTTP 406 to
browser-style User-Agents and to ones carrying a `(mailto:...)` block,
regardless of Accept**, and 200 to a plain one -- hence USER_AGENT below.
arXiv asks for 3 seconds between requests; `fetch_arxiv_batch` uses the
API's own `id_list` to fetch many ids per request instead.

Network is injected (`fetcher`) so every caller and test can run without
it; `default_fetcher` is the only function here that touches a socket.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable

USER_AGENT = "curl/8.0"  # see module docstring: arXiv 406s on anything fancier
ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works/"
DATACITE_API = "https://api.datacite.org/dois/"
ARXIV_MIN_INTERVAL_S = 3.0

_ARXIV_ID = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(v\d+)?")
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>,;)]+)")
_ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

Fetcher = Callable[[str, str], bytes]  # (url, accept) -> body


@dataclass
class Metadata:
    """The subset of bibliographic metadata this store renders."""
    kind: str                     # "arxiv" | "doi"
    ident: str                    # arXiv id (no version) or DOI
    title: str
    authors: list[str]            # rendered "Last, F.M." in source order
    year: str                     # "YYYY" or ""
    date: str                     # "YYYY-MM-DD" when the source gives one, else year
    venue: str = ""               # journal / proceedings / "" for a preprint
    version: str = ""             # arXiv "v3" when known
    doi: str = ""                 # DOI when known (arXiv records may carry one)
    journal_ref: str = ""         # arXiv-supplied journal reference, if any
    source_url: str = ""
    extra: dict = field(default_factory=dict)


def parse_access(access: str) -> tuple[str, str] | None:
    """Recognise a resolvable identifier inside an `access` field.

    Returns ("arxiv", "2303.05509") or ("doi", "10.1145/3007651"), or None
    when the field names only a local file, a bare URL, or nothing.
    """
    if not access:
        return None
    m = _DOI.search(access)
    if m:
        return ("doi", m.group(1).rstrip("."))
    m = _ARXIV_ID.search(access)
    if m and ("arxiv" in access.lower() or "/abs/" in access):
        return ("arxiv", m.group(1))
    return None


def default_fetcher(url: str, accept: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _initials(given: str) -> str:
    parts = [p for p in re.split(r"[\s\-]+", given.strip()) if p]
    return "".join(p[0].upper() + "." for p in parts)


def _render_author(family: str, given: str) -> str:
    family = family.strip()
    given = given.strip()
    if not given:
        return family
    return f"{family}, {_initials(given)}"


def _split_arxiv_name(name: str) -> tuple[str, str]:
    # arXiv gives "Given Family" (sometimes with suffixes); take the last token as family.
    tokens = name.strip().split()
    if len(tokens) == 1:
        return tokens[0], ""
    return tokens[-1], " ".join(tokens[:-1])


def _safe_xml_root(body: bytes) -> ET.Element:
    """Parse untrusted XML without entity expansion. arXiv's Atom feed
    never legitimately carries a DOCTYPE or ENTITY declaration, so their
    presence is refused outright (XXE / billion-laughs shapes); defusedxml
    is used when installed, stdlib ElementTree -- which does not resolve
    external entities -- otherwise. This repository carries no third-party
    dependencies, so the refusal is the guard that always runs."""
    head = body[:4096].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("refusing XML with a DOCTYPE/ENTITY declaration (not a valid arXiv response)")
    try:
        from defusedxml import ElementTree as safe_et  # type: ignore
        return safe_et.fromstring(body)
    except ImportError:
        return ET.fromstring(body)


def parse_arxiv_atom(body: bytes) -> list[Metadata]:
    root = _safe_xml_root(body)
    out: list[Metadata] = []
    for e in root.findall("a:entry", _ATOM):
        raw_id = (e.findtext("a:id", default="", namespaces=_ATOM) or "").strip()
        m = _ARXIV_ID.search(raw_id)
        if not m:
            continue  # arXiv's "no results" entry has no id of that shape
        ident, version = m.group(1), (m.group(2) or "")
        title = " ".join((e.findtext("a:title", default="", namespaces=_ATOM) or "").split())
        authors = [
            _render_author(*_split_arxiv_name(a.findtext("a:name", default="", namespaces=_ATOM) or ""))
            for a in e.findall("a:author", _ATOM)
        ]
        published = (e.findtext("a:published", default="", namespaces=_ATOM) or "")[:10]
        updated = (e.findtext("a:updated", default="", namespaces=_ATOM) or "")[:10]
        doi = (e.findtext("arxiv:doi", default="", namespaces=_ATOM) or "").strip()
        journal_ref = " ".join((e.findtext("arxiv:journal_ref", default="", namespaces=_ATOM) or "").split())
        out.append(Metadata(
            kind="arxiv", ident=ident, title=title, authors=authors,
            year=(updated or published)[:4], date=updated or published,
            version=version, doi=doi, journal_ref=journal_ref,
            source_url=f"https://arxiv.org/abs/{ident}{version}",
            extra={"published": published, "updated": updated},
        ))
    return out


def fetch_arxiv_batch(ids: list[str], fetcher: Fetcher | None = None) -> dict[str, Metadata]:
    """One request for many ids (arXiv's id_list), keyed by id without version."""
    if not ids:
        return {}
    fetcher = fetcher or default_fetcher
    url = f"{ARXIV_API}?id_list={','.join(ids)}&max_results={len(ids)}"
    return {md.ident: md for md in parse_arxiv_atom(fetcher(url, "application/atom+xml"))}


def _date_parts(msg: dict) -> str:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            p = parts[0]
            if len(p) >= 3:
                return f"{p[0]:04d}-{p[1]:02d}-{p[2]:02d}"
            if len(p) == 2:
                return f"{p[0]:04d}-{p[1]:02d}"
            return f"{p[0]:04d}"
    return ""


def parse_crossref(body: bytes) -> Metadata:
    msg = json.loads(body)["message"]
    title = " ".join((msg.get("title") or [""])[0].split())
    authors = [_render_author(a.get("family", ""), a.get("given", "")) for a in msg.get("author", []) if a.get("family") or a.get("name")]
    date = _date_parts(msg)
    venue = (msg.get("container-title") or [""])[0]
    extra = {k: msg.get(k) for k in ("volume", "issue", "page", "article-number", "type", "publisher") if msg.get(k)}
    return Metadata(kind="doi", ident=msg.get("DOI", ""), title=title, authors=authors,
                    year=date[:4], date=date, venue=venue, doi=msg.get("DOI", ""),
                    source_url=msg.get("URL", ""), extra=extra)


def parse_datacite(body: bytes) -> Metadata:
    attrs = json.loads(body)["data"]["attributes"]
    title = " ".join(((attrs.get("titles") or [{}])[0].get("title") or "").split())
    authors = []
    for c in attrs.get("creators", []):
        if c.get("familyName"):
            authors.append(_render_author(c["familyName"], c.get("givenName", "")))
        elif c.get("name"):
            authors.append(c["name"])
    year = str(attrs.get("publicationYear") or "")
    date = ""
    for d in attrs.get("dates", []):
        if d.get("dateType") in ("Issued", "Available") and d.get("date"):
            date = str(d["date"])[:10]
            break
    return Metadata(kind="doi", ident=attrs.get("doi", ""), title=title, authors=authors,
                    year=year, date=date or year, venue=attrs.get("publisher", "") or "",
                    doi=attrs.get("doi", ""), source_url=attrs.get("url", "") or "")


def fetch_doi(doi: str, fetcher: Fetcher | None = None) -> Metadata:
    """Crossref first (it knows the published version); DataCite if Crossref 404s."""
    fetcher = fetcher or default_fetcher
    quoted = urllib.parse.quote(doi, safe="/")
    try:
        return parse_crossref(fetcher(CROSSREF_API + quoted, "application/json"))
    except Exception as crossref_err:  # noqa: BLE001 -- provider-specific failures fall through to DataCite
        try:
            return parse_datacite(fetcher(DATACITE_API + quoted, "application/vnd.api+json"))
        except Exception as datacite_err:  # noqa: BLE001
            raise LookupError(f"DOI {doi}: Crossref ({crossref_err}); DataCite ({datacite_err})") from datacite_err


def fetch(kind: str, ident: str, fetcher: Fetcher | None = None) -> Metadata:
    if kind == "arxiv":
        got = fetch_arxiv_batch([ident], fetcher)
        if ident not in got:
            raise LookupError(f"arXiv {ident}: no entry returned")
        return got[ident]
    if kind == "doi":
        return fetch_doi(ident, fetcher)
    raise ValueError(f"unknown identifier kind {kind!r}")


def render_citation(md: Metadata) -> str:
    """Deterministic, one line, the store's house style:
    `Last, F., Last, F., "Title," Venue, DOI:..., YYYY-MM-DD` for a DOI
    record; `..., "Title," arXiv:ID[vN][, journal ref], YYYY-MM-DD` for an
    arXiv record. No commentary, no audit trail -- those belong in
    `updated_reason`/`evidence` (validate_paper enforces it)."""
    authors = ", ".join(md.authors) if md.authors else "Unattributed"
    # House style puts the comma inside the title's closing quote, so the
    # title is joined to what follows with a space, not the ", " separator.
    head = f'{authors}, "{md.title},"'
    parts: list[str] = []
    if md.kind == "arxiv":
        parts.append(f"arXiv:{md.ident}{md.version}")
        if md.journal_ref:
            parts.append(md.journal_ref)
        if md.doi:
            parts.append(f"DOI:{md.doi}")
    else:
        if md.venue:
            parts.append(md.venue)
        vol = md.extra.get("volume")
        issue = md.extra.get("issue")
        page = md.extra.get("page") or md.extra.get("article-number")
        if vol:
            parts.append(f"{vol}({issue})" if issue else str(vol))
        if page:
            parts.append(str(page))
        if md.doi:
            parts.append(f"DOI:{md.doi}")
    if md.date:
        parts.append(md.date)
    tail = ", ".join(p for p in parts if p)
    return f"{head} {tail}" if tail else head


def resolve(access: str, fetcher: Fetcher | None = None) -> tuple[Metadata, str]:
    """access -> (metadata, rendered citation). Raises LookupError when the
    access field carries no resolvable id -- callers then take the
    hand-transcribed path with its explicit marker."""
    parsed = parse_access(access)
    if parsed is None:
        raise LookupError(f"no resolvable arXiv id or DOI in access {access!r}")
    md = fetch(*parsed, fetcher=fetcher)
    return md, render_citation(md)


class PacedFetcher:
    """A fetcher that keeps arXiv's requested spacing between requests to
    export.arxiv.org and leaves other hosts alone. For bulk runs."""

    def __init__(self, inner: Fetcher | None = None, interval_s: float = ARXIV_MIN_INTERVAL_S):
        self.inner = inner or default_fetcher
        self.interval_s = interval_s
        self._last_arxiv = 0.0

    def __call__(self, url: str, accept: str) -> bytes:
        if "export.arxiv.org" in url:
            wait = self.interval_s - (time.monotonic() - self._last_arxiv)
            if wait > 0:
                time.sleep(wait)
            self._last_arxiv = time.monotonic()
        return self.inner(url, accept)
