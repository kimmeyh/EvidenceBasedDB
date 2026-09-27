#!/usr/bin/env python3
"""Sprint 5, Manual Validation Q1 revised (team lead, 2026-09-25):

    "can you pull any of the papers from the authors IF they are related to
     QML, ML or the Zeno effect (can you screen the abstracts to determine)"

Applies to the author-search hits Task F's co-authorship rule left
UNRESOLVED. The rule was written first, in
docs/research/2026-09-24_F5_qci_affiliated_people.md ("Q1 revised"):

  1. keyword test on the registry abstract (title if no abstract);
  2. Claude reads every positive and rejects incidental matches -- the
     decisions live in REJECTED below, one line each, so the screen is a
     record and re-runs the same way;
  3. identity is NOT established: dispositions say so, and common-family
     admissions are listed separately.

Steps (dry by default, writes nothing to the store):
  screen   : print keyword positives with the matched terms and abstract
  --manifest-out FILE : intake manifest of the kept papers
  --apply  : also download kept arXiv PDFs to QCiAuthorsPapers/<person>/topic-screened/

Usage: python scripts/sprint5_qci_topic_screen.py --report <report.json> [--manifest-out F] [--apply]
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_bibliography as bib  # noqa: E402
import sprint5_qci_authors as qa  # noqa: E402
from store import citations  # noqa: E402

ML_TERMS = ["machine learning", "neural network", "deep learning", "reinforcement learning", "supervised",
            "unsupervised", "classifier", "classification", "reservoir computing", "extreme learning",
            "kernel method", "support vector", "boosting", "feature selection", "clustering",
            "generative model", "transformer", "large language model", "training data"]
ZENO_TERMS = ["zeno"]
_TERMS = re.compile("|".join(re.escape(t) for t in ML_TERMS + ZENO_TERMS), re.I)

# Claude's reading of each keyword positive, filled in after the first
# screen and before any manifest: id -> one-line reason the match is
# incidental. Everything positive and not listed here is kept.
REJECTED: dict[str, str] = {
    # Read 2026-09-25 by Claude (lead). Each is incidental or a duplicate version.
    "arXiv:1804.07653": "quantum error-correction codes; 'machine learning' only as an analogy for factor graphs",
    "arXiv:2112.03301": "radio-transient survey; 'clustering' is astronomical, not data clustering",
    "arXiv:2603.13205": "cosmic-ray radio detector; 'classification' of radio events in an instrument paper",
    "DOI:10.1364/ol.537295": "journal version of arXiv:2411.00953 (same title and abstract); the arXiv version is kept",
    # Team lead, Manual Validation Q8 (2026-09-25): topic passes, authorship least likely the QCi person.
    "arXiv:2405.02958": "removed by the team lead (Q8): MRI reconstruction, authorship doubtful under a common name",
    "DOI:10.1101/2021.05.04.21256502": "removed by the team lead (Q8): dental deep learning, authorship doubtful",
    "arXiv:2603.15546": "removed by the team lead (Q8): human-motion generation, authorship doubtful ('Sam Wu')",
}


def positives(report: dict) -> list[dict]:
    in_store = bib.store_arxiv_ids()
    accepted = {h["id"].lower() for r in report.values() for h in r["accepted"]}
    out, seen = [], set()
    for person, r in report.items():
        for h in r.get("unresolved", []):
            key = h["id"].lower()
            if key in seen or key in accepted or (key.startswith("arxiv:") and h["id"][6:] in in_store):
                continue
            text = h.get("abstract") or h["title"]
            found = sorted({m.group(0).lower() for m in _TERMS.finditer(text)})
            if not found:
                continue
            seen.add(key)
            fam = re.sub(r"[^a-z]", "", qa._ascii(person.split()[-1]))
            out.append({**h, "person": person, "terms": found, "common_family": fam in qa.COMMON_FAMILIES,
                        "tested_on": "abstract" if h.get("abstract") else "title"})
    return out


def manifest(kept: list[dict]) -> list[dict]:
    out = []
    for h in kept:
        topic = "Zeno" if any(t in ZENO_TERMS for t in h["terms"]) else "QML/ML"
        out.append({"access": h["id"], "context": qa.context_for(h),
                    "disposition": (f"Bulk intake 2026-09 from F5's QCi author search ({h['person']}, topic-screened "
                                    f"{topic}; authorship not confirmed by co-authorship); not yet screened")})
    return out


def download(kept: list[dict]) -> list[str]:
    on_disk, failures, last = bib.disk_index(), [], 0.0
    for h in kept:
        if not h["id"].startswith("arXiv:") or h["id"][6:] in on_disk:
            continue
        ident = h["id"][6:]
        md = citations.Metadata(kind="arxiv", ident=ident, title=h["title"],
                                authors=[f"{f}, {g}" for g, f in h["authors"]], year=str(h["year"] or ""), date="")
        folder = qa.OUT_DIR / re.sub(r"[^A-Za-z0-9-]+", "-", h["person"]).strip("-") / "topic-screened"
        wait = citations.ARXIV_MIN_INTERVAL_S - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        try:
            data = bib._get(f"https://arxiv.org/pdf/{ident}")
            last = time.monotonic()
            if not data.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / bib.qml_filename(md)).write_bytes(data)
            print(f"SAVED  {h['person']}: {ident}")
        except Exception as ex:  # noqa: BLE001 -- every failure is listed, none is fatal
            failures.append(f"{h['person']}\t{h['id']}\t{ex}")
    return failures


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    report = json.loads(Path(args[args.index("--report") + 1]).read_text(encoding="utf-8"))
    pos = positives(report)
    kept = [h for h in pos if h["id"] not in REJECTED]
    for h in pos:
        mark = "REJECT" if h["id"] in REJECTED else "KEEP  "
        print(f"{mark} {h['id']:34s} [{h['person']}{', COMMON NAME' if h['common_family'] else ''}] "
              f"{h['title'][:90]}\n        terms {h['terms']} on {h['tested_on']}"
              + (f"\n        rejected: {REJECTED[h['id']]}" if h["id"] in REJECTED else "")
              + f"\n        {(h.get('abstract') or '')[:400]}")
    unresolved = sum(len(r.get("unresolved", [])) for r in report.values())
    print(f"\n{unresolved} unresolved hits; {len(pos)} keyword positives; {len(REJECTED)} rejected on reading; "
          f"{len(kept)} kept ({sum(h['common_family'] for h in kept)} under a common family name)")
    if "--manifest-out" in args:
        Path(args[args.index("--manifest-out") + 1]).write_text(
            json.dumps(manifest(kept), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"MANIFEST {len(kept)} entries")
    if "--apply" in args:
        failures = download(kept)
        print(f"downloads done; {len(failures)} failure(s)")
        for f in failures:
            print("FAILED", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
