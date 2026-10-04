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
Crossref does not know the DOI; and arXiv's own `10.48550/arXiv.<id>`
DOIs, the fallback when the arXiv API refuses). Pre-flight at Sprint 4
planning (2026-09-19): all three reachable; arXiv returned HTTP 406 to
browser-style User-Agents and to ones carrying a `(mailto:...)` block, and
200 to a plain one -- hence USER_AGENT below.

**Measured in Sprint 4 Task C (2026-09-19), against export.arxiv.org from
this client (Python urllib):** a single-id request gets 200; the very next
multi-id `id_list=a,b,...` request gets 406, after which EVERY urllib
request, single ids included, gets 406 for several minutes; curl sends the
same multi-id URL at the same moment and gets 200. Retries do not help
inside the block. So `fetch_arxiv_batch` sends ONE id per request, paced
ARXIV_MIN_INTERVAL_S apart (arXiv's own published rate), and falls back to
DataCite per id when arXiv still refuses. A full 1,200-paper pass is about
an hour, which the sprint plan already budgeted.

Network is injected (`fetcher`) so every caller and test can run without
it; `default_fetcher` is the only function here that touches a socket.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable

USER_AGENT = "curl/8.0"  # see module docstring: arXiv 406s on anything fancier
ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works/"
DATACITE_API = "https://api.datacite.org/dois/"
DOI_HANDLE_API = "https://doi.org/api/handles/"  # the registry itself; responseCode 100 = no such handle
ARXIV_MIN_INTERVAL_S = 3.0
MAX_AUTHORS = 10  # rendered before "et al."; see render_citation

_ARXIV_ID = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(v\d+)?")
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>,;)]+)")
_GITHUB = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?=[/\s|#?]|$)")
GITHUB_API = "https://api.github.com/repos/"
_ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

Fetcher = Callable[[str, str], bytes]  # (url, accept) -> body

_ACCESS_SEP = " | "  # `<local path> | <identifier or url>`
_ROOTED_PATH = re.compile(r"^[A-Za-z]:[\\/]|^[\\/]{1,2}[^\\/]")
_DOCUMENT_FILE = re.compile(r"[\\/][^\\/]*\.(?:pdf|epub|djvu|txt|md|html?|docx?)$", re.IGNORECASE)
_DOI_ANNOUNCED = re.compile(r"(?i)doi[:.]|doi\.org/")


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

    Returns ("arxiv", "2303.05509"), ("doi", "10.1145/3007651") or
    ("github", "owner/name"), or None when the field names only a local
    file or nothing.

    A LOCAL PATH IS NOT AN IDENTIFIER CARRIER. `papers/10.5555/x.pdf` has a
    DOI-shaped folder in it, and reading that as a DOI silently reclassifies
    a hand-origin paper as api and fetches a DIFFERENT paper's metadata --
    the one route found where a wrong citation attaches with no error
    (PR #30 review, 2026-09-22; extended to relative paths 2026-09-23).

    The access convention is `<local path> | <identifier>`, so path
    detection is PER SEGMENT: a path segment is skipped, and the rest of
    the string is searched normally. Judging the whole string by its first
    segment dropped a legitimate bare DOI after the separator, which the
    round-2 review predicted and a probe confirmed.
    """
    if not access:
        return None

    segments = [seg.strip() for seg in access.split(_ACCESS_SEP)]
    # A segment is path-shaped when it is rooted (drive letter or leading
    # slash) OR ends in a document filename -- the second signal is what
    # catches a relative path like `papers/10.5555/x.pdf`.
    searchable = " ".join(
        seg for seg in segments
        if not (_ROOTED_PATH.match(seg) or _DOCUMENT_FILE.search(seg))
        or _DOI_ANNOUNCED.search(seg)  # "...doi:10.x/y" inside a path still counts
    )

    m = _DOI.search(searchable)
    if m:
        return ("doi", m.group(1).rstrip("."))
    m = _ARXIV_ID.search(searchable)
    if m and ("arxiv" in searchable.lower() or "/abs/" in searchable):
        return ("arxiv", m.group(1))
    m = _GITHUB.search(searchable)
    if m:
        return ("github", f"{m.group(1)}/{m.group(2)}")  # Sprint 4 Task G: a repository is a source of record too
    return None


RETRY_CODES = (406, 429, 500, 502, 503, 504)
RETRY_SLEEPS_S = (3.0, 6.0)  # two retries: 3 attempts in all
_sleep = time.sleep          # module attributes so tests can stub the wait
_monotonic = time.monotonic  # and the clock PacedFetcher measures against


def github_token() -> str | None:
    """A GitHub token from the environment (GITHUB_TOKEN, then GH_TOKEN), or
    None. Read per request, so a run started without one stays
    unauthenticated rather than failing. The caller sets it, for example
    from `gh auth token`; this module never reads a credential file."""
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return None


def default_fetcher(url: str, accept: str, _open=None) -> bytes:
    """GET with the plain User-Agent, retrying on transient refusals.

    Sprint 4 Task C (2026-09-19), measured against export.arxiv.org: six
    requests fired back-to-back all returned HTTP 406; the same six paced
    3 s apart all returned 200, with identical headers. So 406 from arXiv
    is intermittent and load-shaped, not (only) a header problem, and one
    attempt is the wrong number. Three attempts with 3 s / 6 s backoff;
    any other failure propagates at once.
    """
    _open = _open or urllib.request.urlopen
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    token = github_token() if url.startswith(GITHUB_API) else None
    if token:
        # Sprint 6 Task K (F35): 5,000 requests per hour against 60. The token
        # goes into this one header and nowhere else: never into a URL, a log
        # line, an exception or the store.
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    for attempt, wait in enumerate((*RETRY_SLEEPS_S, None)):
        try:
            with _open(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            if err.code not in RETRY_CODES or wait is None:
                raise
            _sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


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


ARXIV_DOI_PREFIX = "10.48550/arXiv."


def parse_datacite_arxiv(body: bytes, ident: str) -> Metadata:
    """DataCite's record for arXiv's own DOI, shaped like an arXiv record so
    the render is the same house style. Differences from the Atom API,
    stated so a later refresh's DIFFERS is understood: no journal_ref (the
    published version's DOI comes through as IsVersionOf), and the date is
    the latest version's SUBMISSION date, which is what arXiv's Atom
    `updated` carries; DataCite's own "Updated" dates include metadata
    touches and would drift the render."""
    attrs = json.loads(body)["data"]["attributes"]
    md = parse_datacite(body)
    version = str(attrs.get("version") or "").strip()
    by_type: dict[str, list[str]] = {}
    for d in attrs.get("dates", []):
        if len(str(d.get("date", ""))) >= 10:
            by_type.setdefault(d.get("dateType", ""), []).append(str(d["date"])[:10])
    dates = by_type.get("Submitted") or by_type.get("Updated") or []
    date = max(dates) if dates else (md.date or md.year)
    doi = next((r["relatedIdentifier"] for r in attrs.get("relatedIdentifiers", [])
                if r.get("relationType") == "IsVersionOf" and r.get("relatedIdentifierType") == "DOI"), "")
    return Metadata(kind="arxiv", ident=ident, title=md.title, authors=md.authors, year=date[:4], date=date,
                    version=f"v{version}" if version and not version.startswith("v") else version,
                    doi=doi, source_url=f"https://arxiv.org/abs/{ident}", extra={"provider": "DataCite"})


def fetch_arxiv_batch(ids: list[str], fetcher: Fetcher | None = None) -> dict[str, Metadata]:
    """Metadata for many arXiv ids, keyed by id without version.

    ONE request per id, paced ARXIV_MIN_INTERVAL_S apart (see the module
    docstring for why not `id_list`). When arXiv still refuses an id after
    default_fetcher's retries, DataCite's record for arXiv's own DOI is
    used and the Metadata says so in extra["provider"]; ids neither source
    can give are simply absent from the result, and the caller reports
    them.
    """
    fetcher = fetcher or default_fetcher
    out: dict[str, Metadata] = {}
    for i, ident in enumerate(ids):
        if i:
            _sleep(ARXIV_MIN_INTERVAL_S)
        try:
            for md in parse_arxiv_atom(fetcher(f"{ARXIV_API}?id_list={ident}", "application/atom+xml")):
                out[md.ident] = md
            if ident in out:
                continue
        except urllib.error.HTTPError as err:
            if err.code not in RETRY_CODES:
                raise
        out[ident] = parse_datacite_arxiv(
            fetcher(DATACITE_API + urllib.parse.quote(ARXIV_DOI_PREFIX + ident, safe="/."), "application/vnd.api+json"),
            ident,
        )
    return out


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
    subtitle = " ".join(((msg.get("subtitle") or [""])[0] or "").split())
    if subtitle and subtitle.lower() not in title.lower():
        title = f"{title}: {subtitle}"  # Crossref keeps a book's subtitle apart (freericks-2026, Task C)
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
                    doi=attrs.get("doi", ""), source_url=attrs.get("url", "") or "",
                    extra={"provider": "DataCite"})


def provider_of(md: Metadata) -> str:
    """Which registry answered (ADR-0005 A4 field 10, `metadata_provider`).
    `extra["provider"]` is set only on the DataCite paths (an arXiv id
    answered by DataCite, or a DOI Crossref did not know); otherwise the
    kind names the registry."""
    return md.extra.get("provider") or {"arxiv": "arXiv", "doi": "Crossref", "github": "GitHub"}.get(md.kind, md.kind)


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
            if not doi_is_registered(doi, fetcher):
                # Sprint 4 Task C: udaru-2025's printed DOI (10.63278/...) is
                # unknown to Crossref AND DataCite because it is not in the
                # DOI system at all. Say that, rather than "two 404s".
                raise LookupError(
                    f"DOI {doi} is not registered at doi.org (handle lookup: no such handle). "
                    "A printed DOI that does not resolve is not an access path: record the paper "
                    "as hand-transcribed with a real local path and note the printed DOI in evidence."
                ) from datacite_err
            raise LookupError(f"DOI {doi}: Crossref ({crossref_err}); DataCite ({datacite_err})") from datacite_err


def doi_is_registered(doi: str, fetcher: Fetcher | None = None) -> bool:
    """Ask the DOI registry itself. responseCode 1 = found, 100 = no such
    handle. Any transport failure counts as 'unknown' and returns True so
    the caller reports the provider errors instead of a false negative."""
    fetcher = fetcher or default_fetcher
    try:
        body = json.loads(fetcher(DOI_HANDLE_API + urllib.parse.quote(doi, safe="/"), "application/json"))
    except urllib.error.HTTPError as err:
        # doi.org sends responseCode 100 WITH an HTTP 404 (observed
        # 2026-09-19 for 10.63278/ijcrcr.v8i.3419), so a 404 here is the
        # registry's own "no such handle", not a transport failure.
        return err.code != 404
    except Exception:  # noqa: BLE001
        return True
    return body.get("responseCode") != 100


def parse_github(body: bytes) -> Metadata:
    """GitHub's repository record, shaped for the house style (Sprint 4 Task
    G, F25 C4: `github.com/merlinquantum/merlin` was one of the three F12
    example inputs). The citation is built from fields that change only
    when the repository's identity changes -- owner/name, description,
    license, creation date, URL -- never from the moving HEAD, so the
    refresh diff stays quiet across ordinary pushes. The HEAD commit and
    retrieval date belong in `checked_against_source` when a record is
    read against a specific revision."""
    g = json.loads(body)
    full = g.get("full_name") or ""
    desc = " ".join((g.get("description") or "").split())
    lic = (g.get("license") or {}).get("spdx_id") or ""
    created = (g.get("created_at") or "")[:10]
    return Metadata(kind="github", ident=full, title=desc or full, authors=[full.split("/")[0]] if full else [],
                    year=created[:4], date=created, venue="GitHub repository",
                    source_url=g.get("html_url") or f"https://github.com/{full}",
                    extra={"license": lic, "default_branch": g.get("default_branch") or "", "homepage": g.get("homepage") or "",
                           "topics": g.get("topics") or [], "archived": bool(g.get("archived"))})


def fetch_github(owner_repo: str, fetcher: Fetcher | None = None) -> Metadata:
    fetcher = fetcher or default_fetcher
    return parse_github(fetcher(GITHUB_API + owner_repo, "application/vnd.github+json"))


def fetch(kind: str, ident: str, fetcher: Fetcher | None = None) -> Metadata:
    if kind == "arxiv":
        got = fetch_arxiv_batch([ident], fetcher)
        if ident not in got:
            raise LookupError(f"arXiv {ident}: no entry returned")
        return got[ident]
    if kind == "doi":
        return fetch_doi(ident, fetcher)
    if kind == "github":
        return fetch_github(ident, fetcher)
    raise ValueError(f"unknown identifier kind {kind!r}")


def render_citation(md: Metadata) -> str:
    """Deterministic, one line, the store's house style:
    `Last, F., Last, F., "Title," Venue, DOI:..., YYYY-MM-DD` for a DOI
    record; `..., "Title," arXiv:ID[vN][, journal ref], YYYY-MM-DD` for an
    arXiv record. No commentary, no audit trail -- those belong in
    `updated_reason`/`evidence` (validate_paper enforces it)."""
    # Corporate author when the registry record names no people: Crossref's
    # record for RAND's RRA1367-6 (Sprint 4 Task C) carries a publisher and
    # no contributors, and "RAND Corporation, ..." is standard citation
    # practice for that case; "Unattributed" is only for a record that names
    # neither.
    # At most MAX_AUTHORS names, then "et al.": arute-2019 has 77 authors
    # and the full list is one API call away (determinate facts are
    # computed, never stored). Deterministic, so the refresh diff is stable.
    names = md.authors[:MAX_AUTHORS] + (["et al."] if len(md.authors) > MAX_AUTHORS else [])
    authors = ", ".join(names) if names else (md.extra.get("publisher") or md.venue or "Unattributed")
    # House style puts the comma inside the title's closing quote, so the
    # title is joined to what follows with a space, not the ", " separator.
    head = f'{authors}, "{md.title},"'
    parts: list[str] = []
    if md.kind == "github":
        # `merlinquantum, "MerLin enables ...," GitHub repository merlinquantum/merlin, MIT license, created 2025-06-06, https://github.com/merlinquantum/merlin`
        parts.append(f"{md.venue} {md.ident}")
        if md.extra.get("license"):
            parts.append(f"{md.extra['license']} license")
        if md.date:
            parts.append(f"created {md.date}")
        parts.append(md.source_url)
        return f"{head} {', '.join(parts)}"
    if md.kind == "arxiv":
        parts.append(f"arXiv:{md.ident}{md.version}")
        if md.journal_ref:
            parts.append(md.journal_ref)
        if md.doi:
            parts.append(f"DOI:{md.doi}")
    else:
        publisher_used_as_author = not md.authors and bool(md.extra.get("publisher"))
        if md.venue:
            parts.append(md.venue)
        elif md.extra.get("publisher") and not publisher_used_as_author:
            parts.append(md.extra["publisher"])  # a book/report has a publisher where an article has a journal
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
            wait = self.interval_s - (_monotonic() - self._last_arxiv)
            if wait > 0:
                # Module attribute, not time.sleep directly, so tests can stub
                # the wait like the rest of this file does (PR #30 review).
                _sleep(wait)
            self._last_arxiv = _monotonic()
        return self.inner(url, accept)
