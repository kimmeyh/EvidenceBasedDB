#!/usr/bin/env python3
"""Sprint 9 Task E (F78): download the ceiling group's free PDFs that have no
local copy into D:\\Data\\Harold\\EvidenceBasedDB\\Papers\\ (outside git).

Team lead, 2026-10-14: "also include adding any papers that are not
downloaded as PDF's to the local repository in an appropriate folder".
Only free copies: arXiv and the Federal Reserve's own PDF. The two closed
papers (Chen 2025, Han and Verdu 1994) are the team lead's hand downloads
and are never fetched here. arXiv requests go through the door's paced
fetcher (18 s apart, inside F52's cap). An existing file is never
overwritten. Prints each file's SHA-256 and size. DRY-RUN BY DEFAULT;
`--apply` downloads.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations  # noqa: E402

PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")

DOWNLOADS = [
    ("https://arxiv.org/pdf/2202.00395",
     "2022-02_Ishida_Is-the-Performance-of-My-Deep-Network-Too-Good-to-Be-True.pdf"),
    ("https://arxiv.org/pdf/2106.03357",
     "2021-06_Theisen_Evaluating-State-of-the-Art-Classification-Models-Against-Bayes-Optimality.pdf"),
    ("https://arxiv.org/pdf/2511.00964",
     "2026-03_Thanh_Using-Synthetic-Data-to-Estimate-the-True-Error.pdf"),
    ("https://www.federalreserve.gov/econres/feds/files/2025017pap.pdf",
     "2025-02_Allen_CardSim-A-Bayesian-Simulator-for-Payment-Card-Fraud-Detection.pdf"),
]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    fetcher = citations.PacedFetcher()
    failed = 0
    for url, name in DOWNLOADS:
        target = PAPERS / name
        if target.exists():
            data = target.read_bytes()
            print(f"exists  {name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes")
            continue
        if "--apply" not in args:
            print(f"planned {url} -> {name}")
            continue
        try:
            data = fetcher(url, "application/pdf")
        except Exception as ex:  # noqa: BLE001 -- reported; the others still run
            print(f"FAILED  {url}: {type(ex).__name__}: {ex}")
            failed += 1
            continue
        if not data.startswith(b"%PDF"):
            print(f"FAILED  {url}: the answer is not a PDF ({data[:40]!r})")
            failed += 1
            continue
        target.write_bytes(data)
        print(f"saved   {name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes")
    print("APPLIED" if "--apply" in args else "DRY RUN: nothing downloaded. Re-run with --apply.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
