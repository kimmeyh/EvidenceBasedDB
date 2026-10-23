#!/usr/bin/env python3
"""Sprint 11 Manual Validation Q3 = 1 (intake section 40): F62's discovery
papers with no free copy join the computed hand-download list.

Each store record named in `discovery\\f62_hand_download_*.md` (outside
git) that is not yet on the list gets one updated-reason segment putting it
there, naming the discovery file. From then on the store alone decides
membership (`scripts/hand_download_list.py`).

    python scripts/sprint11_q3_f62_hand_download.py            # dry run
    python scripts/sprint11_q3_f62_hand_download.py --apply    # verified backup first
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

_spec = importlib.util.spec_from_file_location("hdl", Path(__file__).with_name("hand_download_list.py"))
hdl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hdl)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
DISCOVERY = Path(r"D:\Data\Harold\EvidenceBasedDB\discovery")
_DOI = re.compile(r"DOI: (\S+?);")


def discovery_dois() -> dict[str, str]:
    """DOI (lower case) to the discovery file that lists it, oldest file first."""
    out: dict[str, str] = {}
    for path in sorted(DISCOVERY.glob("f62_hand_download_*.md")):
        for doi in _DOI.findall(path.read_text(encoding="utf-8")):
            out.setdefault(doi.lower(), path.name)
    return out


def apply_changes(conn, apply: bool) -> list[str]:
    log = []
    for doi, name in discovery_dois().items():
        row = conn.execute("SELECT r.id, r.updated_reason FROM records r JOIN paper_fields p ON p.record_id = r.id "
                           "WHERE lower(p.access) LIKE ?", (f"%{doi}%",)).fetchone()
        if row is None:
            log.append(f"absent {doi}: not in the store; stays in {name} only")
            continue
        rid, reason = row
        if hdl.on_list(reason):
            log.append(f"exists {rid}")
            continue
        if apply:
            append_updated_reason(conn, rid, f"{TODAY} (Sprint 11 Manual Validation, Q3 = 1): F62 discovery found "
                                  f"no free copy (discovery\\{name}); on the hand-download list", TODAY)
        log.append(f"listed {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "Sprint 11 Q3 F62 papers on the hand-download list")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, apply)
        if apply:
            conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print(f"{sum(x.startswith('listed') for x in log)} listed, {sum(x.startswith('exists') for x in log)} already on "
          f"it, {sum(x.startswith('absent') for x in log)} not in the store")
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
