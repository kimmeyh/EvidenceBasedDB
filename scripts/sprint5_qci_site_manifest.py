#!/usr/bin/env python3
"""Sprint 5 Task H (F5 sub-parts 3 and 4): intake manifest for QCi's own site and packages.

Reads the pages Task G saved under D:/Data/Harold/EvidenceBasedDB/References/QCi-site/
and writes a JSON manifest for `scripts/intake.py --manifest`. Nothing is
written to the store here. What becomes a record, and its context, is
docs/INTAKE_WORKFLOW.md section 13 (written before this code): the team
lead's Q4 = 1 -- one record per lesson, application note and research page,
one per software package -- with the documentation, training modules,
product and technology pages staged, not recorded.

Usage: python scripts/sprint5_qci_site_manifest.py --out <manifest.json>
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_bibliography as bib  # noqa: E402

SITE_DIR = bib.REFERENCES / "QCi-site"
PKG_DIR = bib.REFERENCES / "eqc_models"
BASE = "https://quantumcomputinginc.com"
SECTION_URL = {"lessons": "learn/lessons", "applications": "learn/applications",
               "research-and-publications": "learn/research-and-publications"}
LANDING = {"applications", "entropy-quantum-optimization", "lessons", "research-and-publications", "reservoir-computing"}
EMUCORE = {"classification-on-emucore", "image-classification-using-emucore", "narma10-on-emucore"}
ALREADY_RECORDS = {"profiling-of-cvqboost-algorithm-fraud-detection": "qci-2024-profiling-cvqboost"}
# Packages (section 13): (name, context, local copy under References, public URL)
PACKAGES = [
    ("eqc-models", "platform:dirac-3", None, "https://pypi.org/project/eqc-models/0.21.0/"),
    ("eqc-direct", "platform:dirac-3", "eqc-direct-software-package", None),
    ("qci-client", "platform:dirac-3", "qci-client-software-package", None),
    ("emucore-direct", "qc", "emucore-direct-software-package", None),
    ("uqrng-direct", "qc", "uqrng-direct-software-package", None),
]


def page_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    t = " ".join(html.unescape(m.group(1)).split()) if m else path.stem
    return re.sub(r"\s*[|\-]\s*(QCi|Quantum Computing Inc\.?)\s*$", "", t).strip()


def page_date(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', text) or \
        re.search(r'article:published_time"\s+content="(\d{4}-\d{2}-\d{2})', text)
    return m.group(1) if m else "n.d."


def _entry(rid: str, local: Path, url: str, title: str, context: str, where: str, date: str) -> dict:
    return {"access": f"{local} | {url}", "kind": "reference", "id": rid, "context": context, "title": title,
            "citation": f'Quantum Computing Inc., "{title}," quantumcomputinginc.com, {date} '
                        f"(hand-transcribed from {where})",
            "transcribed_from": where,
            "disposition": f"Reference: QCi site scrape 2026-09 (F5 sub-part 3), {where.split(' of ')[-1]}; not yet screened"}


def build() -> tuple[list[dict], list[str]]:
    out, notes = [], []
    for section, context in (("lessons", "qc"), ("applications", "platform:dirac-3"),
                             ("research-and-publications", "qc")):
        for f in sorted((SITE_DIR / section).glob("*.html")):
            slug = f.stem
            if slug in LANDING:
                notes.append(f"{section}/{slug}: landing page, not a source")
                continue
            if slug in ALREADY_RECORDS:
                notes.append(f"{section}/{slug}: already a record ({ALREADY_RECORDS[slug]})")
                continue
            ctx = "qc" if slug in EMUCORE else context
            url = next((u for u in _urls(section) if u.rstrip("/").endswith("/" + slug)), f"{BASE}/{SECTION_URL[section]}/{slug}")
            out.append(_entry(f"qci-{section.split('-')[0]}-{slug}"[:80], f, url, page_title(f), ctx,
                              f"the saved page's title bar of {SECTION_URL[section]}", page_date(f)))
    for name, context, docs, url in PACKAGES:
        if name == "eqc-models":
            local = PKG_DIR / "eqc_models-0.21.0.tar.gz"
            title = "eqc-models 0.21.0 (Python package)"
            where = "the PyPI release metadata of eqc-models"  # upload date 2026-08-13, pypi.org JSON API
        else:
            cands = sorted((SITE_DIR / "package-docs").glob(f"{docs}__*index*.html")) or \
                sorted((SITE_DIR / "package-docs").glob(f"{docs}__*.html"))
            if not cands:
                notes.append(f"package {name}: no saved documentation page; not entered")
                continue
            local = cands[0]
            url = f"{BASE}/learn/support/software-packages/{docs}"
            title = f"{name} software package documentation"
            where = f"the saved documentation pages of {docs}"
        out.append({"access": f"{local} | {url}", "kind": "reference", "id": f"qci-package-{name}",
                    "context": context, "title": title,
                    "citation": f'Quantum Computing Inc., "{title}," {"pypi.org" if name == "eqc-models" else "quantumcomputinginc.com"}, '
                                f'{"2026-08-13" if name == "eqc-models" else "n.d."} (hand-transcribed from {where})',
                    "transcribed_from": where,
                    "disposition": f"Reference: QCi software package {name} (F5 sub-part {'4' if name == 'eqc-models' else '3'}); "
                                   "documentation staged beside it; not yet screened"})
    return out, notes


_SITEMAP: list[str] = []


def _urls(section: str) -> list[str]:
    if not _SITEMAP:
        _SITEMAP.extend(re.findall(r"<loc>([^<]+)</loc>", bib._get(f"{BASE}/sitemap.xml").decode("utf-8", "replace")))
    return [u for u in _SITEMAP if f"/{SECTION_URL[section]}/" in u]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    out_path = Path(args[args.index("--out") + 1])
    manifest, notes = build()
    out_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(notes))
    by: dict[str, int] = {}
    for m in manifest:
        by[m["context"]] = by.get(m["context"], 0) + 1
    print(f"\nMANIFEST {len(manifest)} entries {by} -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
