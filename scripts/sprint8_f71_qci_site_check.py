#!/usr/bin/env python3
"""Sprint 8 Task G (F71): what is new on quantumcomputinginc.com since the
2026-09-24 scrape, and the three pages from F65's recovered list.

The baseline is the scrape at `D:\\Data\\Harold\\EvidenceBasedDB\\References\\
QCi-site\\` (546 files, 2026-09-24). The current site is its sitemap, saved
on 2026-10-13 under `References\\QCi-site_2026-10-13\\_crawl\\sitemap.xml`.
Both folders are outside the repository; nothing here writes the store.

The sitemap's `lastmod` is not a change signal (most pages show the day it
was read, scraped ones included), so a page counts as changed only when its
visible text differs from the scraped copy's. Computed lists:

  new      in a section the scrape covered, in the sitemap and not in the
           scrape
  recent   in a section the scrape did not cover (news, modules,
           benchmarking, developer resources, ...), with a sitemap
           `lastmod` on or after the scrape date. `lastmod` cannot show a
           change, but a date before the scrape does show the page was not
           changed after it, so this bounds the uncovered sections
  changed  in both, visible text different beyond the site-wide changes
           (a difference found on at least half of the compared pages, or
           of the pages in the same section, is the site's or the
           section's own menu, not the page)
  gone     scraped, no longer in the sitemap
  versions software-package versions in the sitemap that the scrape did
           not hold (package docs are counted by version, not by page)
  ambiguous a scraped page with two sitemap URLs that could be it (listed,
           never guessed)
  fetch_failed a page whose last logged fetch was not a 200 (a redirect
           included), told apart from one never fetched (not_fetched)

FETCHING: `--fetch` gets every page the lists need (the scraped pages, to
compare, and the new pages outside the package docs), serially, 3 s apart,
into the 2026-10-13 folder; a page already saved is not fetched again, so a
stopped run resumes. Without `--fetch` nothing is requested and the lists
are computed from what is saved. `--out <file>` writes them as JSON.
"""
from __future__ import annotations

import difflib
import html
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REFS = Path(r"D:\Data\Harold\EvidenceBasedDB\References")
OLD = REFS / "QCi-site"
NEW = REFS / "QCi-site_2026-10-13"
SITEMAP = NEW / "_crawl" / "sitemap.xml"
SITE = "https://quantumcomputinginc.com"
USER_AGENT = "Mozilla/5.0 (compatible; EvidenceBasedDB-research)"
SPACING_S = 3.0
SCRAPED_ON = "2026-09-24"

# The scrape's folders and the site sections they came from.
SECTIONS = {
    "applications": "/learn/applications/",
    "lessons": "/learn/lessons/",
    "research-and-publications": "/learn/research-and-publications/",
    "systems": "/products/systems/",
    "technology": "/technology/",
}
PACKAGE_PATH = re.compile(r"/(?P<pkg>[a-z-]+-software-package)/(?P<ver>v\d+\.\d+\.\d+)(?:/|$)")


def sitemap_entries(path: Path = SITEMAP) -> dict[str, str]:
    """URL -> lastmod date (YYYY-MM-DD, or '' where the sitemap gives none)."""
    out = {}
    text = path.read_text(encoding="utf-8")
    if "<sitemapindex" in text:
        # An index lists other sitemaps, not pages; reading it as pages would
        # report every scraped page as gone (PR #77 review).
        raise ValueError(f"{path} is a sitemap index; save the sitemaps it lists and read those")
    for block in re.findall(r"<url>(.*?)</url>", text, flags=re.S):
        loc = re.search(r"<loc>(.*?)</loc>", block)
        mod = re.search(r"<lastmod>(.*?)</lastmod>", block)
        if loc:
            out[loc.group(1).strip()] = mod.group(1).strip()[:10] if mod else ""
    return out


def sitemap_urls(path: Path = SITEMAP) -> list[str]:
    return list(sitemap_entries(path))


def covered(url: str) -> bool:
    return any(url == SITE + s.rstrip("/") or url.startswith(SITE + s) for s in SECTIONS.values())


def is_package_doc(url: str) -> bool:
    return "-software-package" in url


def visible_text(page: str) -> str:
    """The text a reader sees: scripts, styles and tags removed, entities
    decoded, whitespace collapsed (as tests/test_f45_dirac3_reading.py
    reads a saved page)."""
    page = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", page, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page))).strip()


def local_name(url: str) -> Path:
    """Where a page fetched on 2026-10-13 is saved: its URL path, folders
    and all, under the 2026-10-13 folder."""
    rel = url.replace(SITE, "").strip("/") or "index"
    return NEW / (rel + ".html")


def scraped_pages(old: Path = OLD) -> dict[str, Path]:
    """URL -> scraped file, for the scraped sections (not package docs),
    matched by the last path segment within the section."""
    out = {}
    for folder, section in SECTIONS.items():
        for f in sorted((old / folder).glob("*.html")):
            # A file named for its folder is the section's own index page.
            out[SITE + section.rstrip("/") if f.stem == folder else f"{SITE}{section}{f.stem}"] = f
    return out


def resolve(scraped: dict[str, Path], urls: list[str]) -> tuple[dict[str, Path], list[str], list[str]]:
    """Each scraped file's current URL (the sitemap URL in the same section
    with the same last segment), the scraped files with none (gone), and
    those with more than one candidate (ambiguous: listed, never guessed)."""
    by_slug: dict[tuple[str, str], list[str]] = {}
    for u in urls:
        for section in SECTIONS.values():
            if u.startswith(SITE + section):
                by_slug.setdefault((section, u.rstrip("/").rsplit("/", 1)[-1]), []).append(u)
    present = set(urls)
    matched, gone, ambiguous = {}, [], []
    for guess, f in scraped.items():
        if guess in present:  # a section index, or an exact path
            matched[guess] = f
            continue
        section = next(s for s in SECTIONS.values() if guess.startswith(SITE + s))
        candidates = by_slug.get((section, f.stem), [])
        if len(candidates) == 1:
            matched[candidates[0]] = f
        elif candidates:
            ambiguous.append(f"{f.parent.name}/{f.name}: {', '.join(sorted(candidates))}")
        else:
            gone.append(f"{f.parent.name}/{f.name}")
    return matched, gone, ambiguous


def scraped_versions(old: Path = OLD) -> set[tuple[str, str]]:
    found = set()
    for f in (old / "package-docs").glob("*.html"):
        for m in PACKAGE_PATH.finditer(f.read_text(encoding="utf-8", errors="replace")):
            found.add((m["pkg"], m["ver"]))
    return found


def fetch(url: str, target: Path) -> str:
    """The page's status, saving its body only for a 200 at the same
    address. A redirect is reported, not saved: a removed page that
    redirects to the home page would otherwise read as "changed" (PR #77
    review)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            status = str(resp.status)
            final = resp.geturl()
    except urllib.error.HTTPError as ex:
        return f"HTTP {ex.code}"
    except (urllib.error.URLError, TimeoutError, http.client.HTTPException, ConnectionError) as ex:
        return f"no answer ({ex})"
    if final.rstrip("/") != url.rstrip("/"):
        return f"redirected to {final}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    return status


def word_changes(before: str, after: str) -> frozenset[tuple[str, str]]:
    """The word-level differences between two texts, each as (old words,
    new words)."""
    a, b = before.split(" "), after.split(" ")
    return frozenset((" ".join(a[i1:i2]), " ".join(b[j1:j2]))
                     for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
                     if op != "equal")


MIN_CHROME_PAGES = 3


def site_wide(diffs: dict[str, frozenset]) -> frozenset:
    """Differences found on at least half of the compared pages, and on at
    least MIN_CHROME_PAGES of them: the site's own navigation and footer,
    not the page (on 2026-10-13, a new "Benchmarking" menu entry on every
    page). The floor keeps a section of one or two pages from reading its
    own change as menu (PR #77 review: a lone page's whole difference was
    its own "half")."""
    counts: dict[tuple[str, str], int] = {}
    for d in diffs.values():
        for change in d:
            counts[change] = counts.get(change, 0) + 1
    return frozenset(c for c, n in counts.items() if n >= MIN_CHROME_PAGES and n * 2 >= len(diffs))


def section_of(url: str) -> str:
    return next((s for s in SECTIONS.values() if url == SITE + s.rstrip("/") or url.startswith(SITE + s)), "")


def split_changed(diffs: dict[str, frozenset]) -> tuple[list[str], list[str]]:
    """(changed, unchanged): a page is changed when it differs beyond the
    site's chrome and its own section's (a section sidebar that gained an
    entry differs on every page of that section). Known limit: the same
    real change on at least three pages and half of a section reads as that
    section's menu."""
    site = site_wide(diffs)
    by_section: dict[str, frozenset] = {}
    for s in {section_of(u) for u in diffs}:
        by_section[s] = site_wide({v: d for v, d in diffs.items() if section_of(v) == s})
    changed = sorted(u for u, d in diffs.items() if d - site - by_section[section_of(u)])
    return changed, sorted(u for u in diffs if u not in changed)


def wanted_lists(entries: dict[str, str]) -> tuple[dict[str, Path], list[str], list[str], list[str], list[str]]:
    """(scraped pages matched to their URL, gone, ambiguous, new, recent).
    A page with no `lastmod` counts as recent: no date is not an old date."""
    urls = list(entries)
    matched, gone, ambiguous = resolve(scraped_pages(), urls)
    rest = [u for u in urls if u not in matched and not is_package_doc(u)]
    new = sorted(u for u in rest if covered(u))
    recent = sorted(u for u in rest if not covered(u) and (not entries[u] or entries[u] >= SCRAPED_ON))
    return matched, gone, ambiguous, new, recent


def fetch_failures(log: Path) -> dict[str, str]:
    """URL -> the last status logged for it, for the URLs whose last fetch
    was not a 200 (so a failed fetch is told apart from one never tried)."""
    last: dict[str, str] = {}
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                last[parts[2]] = parts[1]
    return {u: s for u, s in last.items() if s != "200"}


def compute(entries: dict[str, str], log: Path | None = None) -> dict:
    urls = list(entries)
    matched, gone, ambiguous, new, recent = wanted_lists(entries)
    failed = fetch_failures(log or NEW / "_crawl" / "fetch-log.tsv")
    diffs, unread = {}, []
    for u, old_file in sorted(matched.items()):
        saved = local_name(u)
        if not saved.exists():
            unread.append(u)
            continue
        diffs[u] = word_changes(visible_text(old_file.read_text(encoding="utf-8", errors="replace")),
                                visible_text(saved.read_text(encoding="utf-8", errors="replace")))
    changed, unchanged = split_changed(diffs)
    versions_now = {(m["pkg"], m["ver"]) for u in urls for m in [PACKAGE_PATH.search(u)] if m}
    return {"snapshot": "2026-10-13", "baseline": SCRAPED_ON, "sitemap_urls": len(urls),
            "scraped_pages_compared": len(matched), "new": new,
            "recent": [f"{entries[u] or 'no date'} {u}" for u in recent], "changed": changed,
            "unchanged": len(unchanged), "ambiguous": ambiguous,
            "fetch_failed": [f"{failed[u]} {u}" for u in unread if u in failed],
            "not_fetched": [u for u in unread if u not in failed], "gone": sorted(gone),
            "new_package_versions": sorted(f"{p} {v}" for p, v in versions_now - scraped_versions()),
            "package_versions_now": sorted(f"{p} {v}" for p, v in versions_now)}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    known = {"--fetch", "--out"}
    unknown = [a for i, a in enumerate(args) if a.startswith("-") and a not in known]
    if unknown or ("--out" in args and args.index("--out") + 1 >= len(args)):
        print(f"usage: sprint8_f71_qci_site_check.py [--fetch] [--out FILE] (not understood: {unknown or '--out'})",
              file=sys.stderr)
        return 2
    entries = sitemap_entries()
    if "--fetch" in args:
        matched, _, _, new, recent = wanted_lists(entries)
        wanted = sorted(set(matched) | set(new) | set(recent))
        todo = [u for u in wanted if not local_name(u).exists()]
        print(f"{len(wanted)} pages wanted, {len(todo)} to fetch, {SPACING_S:.0f} s apart")
        log = NEW / "_crawl" / "fetch-log.tsv"
        log.parent.mkdir(parents=True, exist_ok=True)
        for i, u in enumerate(todo):
            if i:
                time.sleep(SPACING_S)
            status = fetch(u, local_name(u))
            with log.open("a", encoding="utf-8") as fh:
                fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{status}\t{u}\n")
            print(f"{status:>4} {u}")
    result = compute(entries)
    for key in ("new", "recent", "changed", "gone", "ambiguous", "fetch_failed", "not_fetched", "new_package_versions"):
        print(f"{key}: {len(result[key])}")
    if "--out" in args:
        Path(args[args.index("--out") + 1]).write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
