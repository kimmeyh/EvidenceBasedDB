#!/usr/bin/env python3
"""Sprint 5 Task G (F5 sub-parts 3 and 4): QCi's own documentation and the eqc-models package.

Scope (team lead, Q3 = 1, 2026-09-24): the LATEST version of each software
package's documentation, de-duplicated across the three paths the site
mounts it under (learn/support, learn/developer-resources, learn/module),
plus lessons, applications, research and publications, products/systems
and technology pages. Not press releases or SEC filings (outside the
card's "key docs, training, QML methods"), not older package versions
(the same pages again).

robots.txt (checked 2026-09-23): `User-Agent: * / Allow: /`. One request
per second.

Storage (Q6 as assumed at approval): pages under
D:/Data/Harold/EvidenceBasedDB/References/QCi-site/<section>/, the package
under References/eqc_models/. Pages already saved by the bibliography run
(Task B) are not fetched again. A page with fewer than
sprint5_bibliography.MIN_VISIBLE_WORDS visible words is a shell and is
listed as a failure, not kept.

Dry run by default (prints the selection); --apply fetches.

Usage: python scripts/sprint5_qci_site.py [--apply]
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_bibliography as bib  # noqa: E402

SITE = "https://quantumcomputinginc.com"
OUT = bib.REFERENCES / "QCi-site"
PKG_OUT = bib.REFERENCES / "eqc_models"
MOUNTS = ("learn/support", "learn/developer-resources", "learn/module")
FLAT_SECTIONS = ("learn/lessons", "learn/applications", "learn/research-and-publications", "products/systems",
                 "technology")
_VERSION = re.compile(r"/v(\d+(?:\.\d+)+)(/|$)")


def _vt(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def select(urls: list[str]) -> tuple[list[tuple[str, str]], dict]:
    """Return [(url, relative target)], plus counts for the report."""
    latest: dict[str, str] = {}
    for u in urls:
        m = _VERSION.search(u)
        if m:
            pkg = u[: m.start()].rstrip("/").split("/")[-1]
            latest[pkg] = max(latest.get(pkg, "0"), m.group(1), key=_vt)
    chosen: dict[str, tuple[str, str]] = {}
    counts = {"sitemap": len(urls), "older_versions_skipped": 0, "duplicate_mounts_skipped": 0}
    for u in sorted(urls):
        path = u.removeprefix(SITE).strip("/")
        if any(path.startswith(m) for m in MOUNTS):
            m = _VERSION.search(u)
            if m:
                pkg = u[: m.start()].rstrip("/").split("/")[-1]
                if m.group(1) != latest[pkg]:
                    counts["older_versions_skipped"] += 1
                    continue
                key = f"{pkg}/{u[m.end():].strip('/') or 'index'}"
            else:
                key = "/".join(path.split("/")[2:]) or path   # an unversioned package or module landing page
            if key in chosen:
                counts["duplicate_mounts_skipped"] += 1
                continue
            chosen[key] = (u, f"package-docs/{key.replace('/', '__')}.html")
        elif any(path == s or path.startswith(s + "/") for s in FLAT_SECTIONS):
            section = path.split("/")[1] if path.startswith(("learn/", "products/")) else "technology"
            chosen[path] = (u, f"{section}/{path.split('/')[-1] or 'index'}.html")
    counts["selected"] = len(chosen)
    return list(chosen.values()), counts


def already_saved() -> dict[str, Path]:
    """Pages the bibliography run saved (QC-6, QC-7), by URL, so none is fetched twice."""
    out = {}
    manual = bib.REFERENCES / "2026-09_HSBC-Phase2-research_BIBLIOGRAPHY.md"
    if manual.exists():
        for e in bib.parse(manual.read_text(encoding="utf-8")):
            for i, u in enumerate(e.urls):
                if u.startswith(SITE):
                    p = bib.REFERENCES / bib.web_filename(e, u, i)
                    if p.exists():
                        out[u.rstrip("/")] = p
    return out


def fetch_package(apply: bool) -> list[str]:
    meta = json.loads(bib._get("https://pypi.org/pypi/eqc-models/json", "application/json"))
    version = meta["info"]["version"]
    files = [f for f in meta["urls"] if f["packagetype"] in ("sdist", "bdist_wheel")]
    lines = [f"eqc-models {version}: {', '.join(f['filename'] for f in files)}"]
    if apply:
        PKG_OUT.mkdir(parents=True, exist_ok=True)
        (PKG_OUT / f"eqc-models-{version}_pypi-metadata.json").write_text(json.dumps(meta["info"], indent=1),
                                                                           encoding="utf-8")
        for f in files:
            target = PKG_OUT / f["filename"]
            if not target.exists():
                data = bib._get(f["url"])
                import hashlib
                if hashlib.sha256(data).hexdigest() != f["digests"]["sha256"]:
                    raise ValueError(f"{f['filename']}: sha256 does not match PyPI's")
                target.write_bytes(data)
            lines.append(f"SAVED {target} (sha256 verified against PyPI)")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    sitemap = bib._get(f"{SITE}/sitemap.xml").decode("utf-8", "replace")
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    pages, counts = select(urls)
    saved = already_saved()
    print(json.dumps(counts))
    failures: list[str] = []
    fetched = reused = 0
    for url, rel in pages:
        target = OUT / rel
        if url.rstrip("/") in saved:
            reused += 1
            print(f"REUSED  {url} -> {saved[url.rstrip('/')].name}")
            continue
        if not apply:
            continue
        if target.exists():
            continue
        try:
            data = bib._get(url)
            time.sleep(1.0)
            if bib.visible_words(data) < bib.MIN_VISIBLE_WORDS:
                raise ValueError(f"no content ({bib.visible_words(data)} visible words)")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            fetched += 1
        except (urllib.error.URLError, OSError, ValueError) as ex:
            failures.append(f"{url}\t{ex}")
    for line in fetch_package(apply):
        print(line)
    if apply:
        (OUT / "failures.txt").write_text("\n".join(failures) + "\n", encoding="utf-8")
        print(f"fetched {fetched}, reused {reused}, failed {len(failures)} -> {OUT}")
    else:
        by = {}
        for _, rel in pages:
            by[rel.split("/")[0]] = by.get(rel.split("/")[0], 0) + 1
        print(f"PLANNED {len(pages)} pages {by}; {reused} already saved. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
