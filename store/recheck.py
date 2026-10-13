"""The staggered 12-month re-check (ADR-0005 A7, Sprint 8 Task D, F64).

Computes; writes nothing. Every paper belongs to one of 24 half-month
sections of the calendar year, taken from a hash of its id, so a bulk load
spreads over the year instead of coming due in one sprint. Its next
re-check is the first start of its section at least 10 months after its
last check. The section, the last check and the next re-check are all
computed from stored dates, never stored themselves.

Also here: reading the latest arXiv version from an abstract page, and the
version stamp on the first page of a local PDF, for the re-pull list.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import date
from pathlib import Path

SECTIONS = 24
MIN_MONTHS = 10
LOCAL_FILE_PROVIDER = "local file check"
QMLPAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\QMLPapers")


def section_of(record_id: str) -> int:
    """1 to 24: the first 8 hex digits of the id's SHA-256, mod 24, plus 1."""
    return int(hashlib.sha256(record_id.encode("utf-8")).hexdigest()[:8], 16) % SECTIONS + 1


def section_start(year: int, section: int) -> date:
    """Section 1 starts January 1, 2 starts January 16, ... 24 starts December 16."""
    if not 1 <= section <= SECTIONS:
        raise ValueError(f"section must be 1 to {SECTIONS}, got {section}")
    return date(year, (section - 1) // 2 + 1, 1 if section % 2 else 16)


def _add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):  # the 31st of a 30-day month lands on its last day
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise AssertionError("unreachable")


def next_recheck(last_check: date, section: int) -> date:
    """The first start of `section` on or after last_check + 10 months."""
    earliest = _add_months(last_check, MIN_MONTHS)
    start = section_start(earliest.year, section)
    return start if start >= earliest else section_start(earliest.year + 1, section)


def last_check(conn, record_id: str) -> date | None:
    """The latest probe date, leaving out hand-recorded readings (never
    refreshed, ADR-0005 A6 (c)); a record with no probe takes its `updated`
    date (plan Q4: the same rule, from the date it was last written). None
    when neither holds a date."""
    row = conn.execute("SELECT MAX(probed_on) FROM paper_probes WHERE record_id = ? AND provider <> 'hand'",
                       (record_id,)).fetchone()
    if row and row[0]:
        return date.fromisoformat(row[0])
    updated = (conn.execute("SELECT updated FROM records WHERE id = ?", (record_id,)).fetchone() or [""])[0] or ""
    try:
        return date.fromisoformat(updated[:10])
    except ValueError:
        return None


def schedule(conn, record_id: str) -> tuple[int, date | None, date | None]:
    """(section, last check, next re-check) for one paper. With no date to
    start from, both dates are None and the paper counts as due now."""
    section = section_of(record_id)
    last = last_check(conn, record_id)
    return section, last, (next_recheck(last, section) if last else None)


def due(conn, on: date) -> list[tuple[str, str, date | None]]:
    """(record_id, access, next re-check) for every paper due on or before
    `on`, including any with no date to start from."""
    out = []
    for rid, access in conn.execute("SELECT record_id, access FROM paper_fields ORDER BY record_id"):
        nxt = schedule(conn, rid)[2]
        if nxt is None or nxt <= on:
            out.append((rid, access, nxt))
    return out


# --------------------------------------------------------------- versions
_HISTORY = re.compile(r'<div class="submission-history">(.*?)</div>', re.DOTALL)
_VERSION = re.compile(r"\[v(\d+)\]")
_STAMP = re.compile(r"arXiv:(\d{4}\.\d{4,5})v(\d+)")


def latest_version(page: str) -> int | None:
    """The highest [vN] in an abstract page's submission history, or None
    when the page has no history block (a page that cannot be read says so;
    it is never taken as "no newer version")."""
    block = _HISTORY.search(page)
    versions = [int(v) for v in _VERSION.findall(block.group(1))] if block else []
    return max(versions) if versions else None


def stamp_version(first_page_text: str, ident: str) -> int | None:
    """The version in arXiv's first-page stamp ("arXiv:2407.04512v4 ...")
    when it names `ident`, else None."""
    for found_id, v in _STAMP.findall(first_page_text):
        if found_id == ident:
            return int(v)
    return None


def local_copy(ident: str, root: Path = QMLPAPERS) -> Path | None:
    """The local PDF whose file name ends `__<ident>.pdf` (the QMLPapers
    naming convention), or None."""
    if not root.exists():
        return None
    hits = sorted(root.rglob(f"*__{ident}.pdf"))
    return hits[0] if hits else None


_SHORT_NEW_STYLE = re.compile(r"(\d{4})\.(\d{4})")


def local_copies(ident: str, root: Path = QMLPAPERS) -> list[Path]:
    """Every local PDF anywhere under `root` for `ident`: the exact
    `__<ident>.pdf` names, and, for a new-style id one digit short (four
    digits after a YYMM of 1501 or later, when arXiv ids have five), the
    names it is a prefix of. A finding that a paper has no local copy is
    computed with this, never asserted by hand (Sprint 8 retrospective I2:
    the F60 report said the Asfaw paper was never downloaded; its row named
    2108.0131, and 2108.01311 was already in `Workforce`)."""
    if not root.exists():
        return []
    hits = set(root.rglob(f"*__{ident}.pdf"))
    short = _SHORT_NEW_STYLE.fullmatch(ident)
    if short and int(short.group(1)) >= 1501:
        hits.update(root.rglob(f"*__{ident}[0-9].pdf"))
    return sorted(hits)


def local_version(ident: str, root: Path = QMLPAPERS) -> int | None:
    path = local_copy(ident, root)
    if path is None:
        return None
    text = subprocess.run(["pdftotext", "-l", "1", str(path), "-"], capture_output=True,
                          check=False).stdout.decode("utf-8", "replace")
    return stamp_version(text, ident)


# -------------------------------------------------------------- local files
_SHA = re.compile(r"SHA-256 ([0-9a-f]{64})")


def local_paths(access: str) -> list[str]:
    """Every rooted local path segment in an access field: a drive letter or
    a leading slash, as `citations.parse_access` treats a path."""
    return [seg.strip() for seg in access.split("|") if re.match(r"^\s*(?:[A-Za-z]:[\\/]|/)", seg)]


def check_local(access: str, evidence: str | None) -> tuple[str, str]:
    """(access_status value, note) for a local copy: present with its
    SHA-256 unchanged, present with no recorded hash, changed, or missing."""
    paths = local_paths(access)
    if not paths:
        return "", "no local path"
    path = Path(paths[0])
    if not path.exists():
        return "local copy missing", f"{path} not found"
    if path.is_dir():
        # A folder (an unpacked release, a repository) has no single hash.
        return "local copy present (a folder; not hashed)", ""
    m = _SHA.search(evidence or "")
    if not m:
        return "local copy present (no SHA-256 recorded)", ""
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as err:
        return "local copy unreadable", f"{path}: {type(err).__name__}"
    if digest != m.group(1):
        return "local copy changed (SHA-256 differs)", f"{path} differs from the recorded SHA-256"
    return "local copy present (SHA-256 unchanged)", ""
