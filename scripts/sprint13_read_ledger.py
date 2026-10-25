#!/usr/bin/env python3
"""Sprint 13: the one read ledger for Task F (F112, the F57 release).

Sprint 11's ledger rules (`scripts/sprint11_read_ledger.py`), pointed at
this sprint's files: one record, one group, one first-pass reader; at most
5 readers at once, in waves; a record with no local copy goes to `no_copy`
with its reason, never to a reader. `tests/test_sprint13_read_ledger.py`
fails if any record is held twice.

New this sprint: a record the serial fetcher could not get names why
(arXiv's 404, or no free copy OpenAlex knows), read from the download log,
instead of one reason for all; a record whose arXiv paper Sprint 12 found
withdrawn says so.

Usage:
  python scripts/sprint13_read_ledger.py --download-log <file>
Writes `manifests/sprint13_read_ledger.json`. Refuses to add a record that
any existing group already holds.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("ledger11", Path(__file__).with_name("sprint11_read_ledger.py"))
ledger11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger11)

ROOT = ledger11.ROOT
ledger11.LEDGER = LEDGER = ROOT / "manifests" / "sprint13_read_ledger.json"
ledger11.SLICE = ROOT / "manifests" / "sprint13_f112_slice.json"
WITHDRAWN = {"mahroo-2023-trainable-variational-quantum-multiblock-admm":
             "no local copy: withdrawn on arXiv (2303.16318, abstract page read 2026-10-23; INTAKE_WORKFLOW.md "
             "section 46); arXiv returned 404 for the PDF on 2026-10-25"}
_FAILED = re.compile(r"^FAILED\s+(\S+):\s+(.+)$")
_NO_FREE = re.compile(r"^no free copy known to OpenAlex: (\S+) \((.+)\)$")


def fetch_reasons(log: Path) -> dict[str, str]:
    """Why the fetcher got no copy, per record, from its log."""
    out = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        if m := _FAILED.match(line):
            out[m.group(1)] = f"no local copy: the paced fetch failed on 2026-10-25 ({m.group(2)})"
        elif m := _NO_FREE.match(line):
            out[m.group(1)] = f"no local copy: no free copy known to OpenAlex ({m.group(2)})"
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    log = Path(args[args.index("--download-log") + 1])
    ledger = ledger11.load()
    rows, missing = ledger11.task_g_rows(log)
    reasons = fetch_reasons(log)
    missing = {rid: WITHDRAWN.get(rid) or reasons.get(rid) or why for rid, why in missing.items()}
    ledger["no_copy"].update(missing)
    n = ledger11.add_groups(ledger, "F", rows)
    assert not ledger11.duplicates(ledger)
    LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"task F: {len(rows)} records in groups up to g{n:02d}; no copy: {len(ledger['no_copy'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
