#!/usr/bin/env python3
"""Sprint 13 Task G (F113): free copies of the slice's papers that have no local copy.

Exactly Sprint 10's to 13's rules (`scripts/sprint10_f89_downloads.py`),
pointed at the `fetch` bucket of `manifests/sprint13_g_slice.json`: arXiv
through the door's paced fetcher (18 s apart, inside F52's cap), else the
open-access PDF OpenAlex lists; a paywalled paper is listed, never fetched;
an existing file is never overwritten. A heartbeat line goes to
`--heartbeat <file>` after every paper.

`--session-count N` starts this run's arXiv count at the requests already
sent this session by other runs (F52's cap counts per process).
DRY-RUN BY DEFAULT; `--apply` downloads.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location("f112dl", Path(__file__).with_name("sprint13_f112_downloads.py"))
f112dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f112dl)

SLICE = f112dl.f89dl.ROOT / "manifests" / "sprint13_g_slice.json"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    rows = [r for r in json.loads(SLICE.read_text(encoding="utf-8"))["slice"] if r["bucket"] == "fetch"]
    with tempfile.TemporaryDirectory() as tmp:
        fetch = Path(tmp) / "fetch_slice.json"
        fetch.write_text(json.dumps({"slice": rows}), encoding="utf-8")
        f112dl.f89dl.SLICE = fetch
        return f112dl.main(args)


if __name__ == "__main__":
    sys.exit(main())
