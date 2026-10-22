#!/usr/bin/env python3
"""Sprint 11 Task G (F96): free copies of the slice's papers that have no local copy.

Exactly Sprint 10's rules (`scripts/sprint10_f89_downloads.py`), pointed at
`manifests/sprint11_f96_slice.json`: arXiv through the door's paced fetcher
(18 s apart, inside F52's cap; the one fetcher this sprint's readers share,
so five readers never make five arXiv streams), else the open-access PDF
OpenAlex lists; a paywalled paper is listed, never fetched; an existing file
is never overwritten. A heartbeat line goes to `--heartbeat <file>` after
every paper, since the run is longer than 30 minutes (SPRINT_PLANNING.md).
DRY-RUN BY DEFAULT; `--apply` downloads.
"""
from __future__ import annotations

import builtins
import importlib.util
import sys
from datetime import datetime
from pathlib import Path

_spec = importlib.util.spec_from_file_location("f89dl", Path(__file__).with_name("sprint10_f89_downloads.py"))
f89dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f89dl)

f89dl.SLICE = f89dl.ROOT / "manifests" / "sprint11_f96_slice.json"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--heartbeat" in args:
        beat = Path(args[args.index("--heartbeat") + 1])
        real_print = builtins.print

        def print_and_beat(*a, **k):
            real_print(*a, **k)
            with beat.open("a", encoding="utf-8") as fh:
                fh.write(f"{datetime.now():%H:%M:%S} " + " ".join(str(x) for x in a) + "\n")
        f89dl.print = print_and_beat
    return f89dl.main([a for a in args if a == "--apply"])


if __name__ == "__main__":
    sys.exit(main())
