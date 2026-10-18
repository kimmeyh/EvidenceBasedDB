#!/usr/bin/env python3
"""Sprint 9 Task F (F46): download the free arXiv copies of the two pending-fact
sources with no local PDF into D:\\Data\\Harold\\EvidenceBasedDB\\Papers\\
(outside git), as Task E did for the ceiling group.

Howard et al. 2014 (Nature, arXiv:1401.4174) and Ortiz Marrero et al. 2021
(PRX Quantum, arXiv:2010.15968). Two arXiv requests through the door's paced
fetcher, 18 s apart, inside F52's cap. An existing file is never
overwritten. DRY-RUN BY DEFAULT; `--apply` downloads.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("f78dl", Path(__file__).with_name("sprint9_f78_downloads.py"))
f78dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f78dl)

f78dl.DOWNLOADS = [
    ("https://arxiv.org/pdf/1401.4174",
     "2014-01_Howard_Contextuality-Supplies-the-Magic-for-Quantum-Computation.pdf"),
    ("https://arxiv.org/pdf/2010.15968",
     "2020-10_Ortiz-Marrero_Entanglement-Induced-Barren-Plateaus.pdf"),
]

if __name__ == "__main__":
    sys.exit(f78dl.main())
