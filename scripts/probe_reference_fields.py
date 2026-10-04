#!/usr/bin/env python3
"""Run the computed-field probes (ADR-0005 A4 (b), Sprint 6 Task F) and keep
each one's last result, date and provider (the probe rule).

`store/probes.py` computes; this script chooses which records, times the
run, and writes through `store.ingest.record_probe`. arXiv traffic is
serial and paced (Sprint 5 rule), so a full run is sized from a pilot.

    python scripts/probe_reference_fields.py --pilot             # 30 records across source types, dry run
    python scripts/probe_reference_fields.py --pilot --apply
    python scripts/probe_reference_fields.py --all --apply --heartbeat <file>
    python scripts/probe_reference_fields.py --ids a,b,c [--apply]

DRY-RUN BY DEFAULT: prints what each probe found and how long it took.
`--apply` takes a verified backup first and commits per record, so a stop
loses nothing. Never stores a guess: a probe that cannot answer a field
leaves it unset and says why.
"""
from __future__ import annotations

import sys
import time
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import record_probe  # noqa: E402
from store.probes import landing_url, probe_access, probe_arxiv, probe_doi  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PILOT = {"arxiv": 12, "doi": 10, "github": 3, "hand-url": 5}  # 30, every source type


def kind_of(access: str) -> str:
    parsed = citations.parse_access(access)
    if parsed:
        return parsed[0]
    return "hand-url" if landing_url(access) else "hand-local"


def select(conn, args: list[str]) -> list[tuple[str, str, str]]:
    rows = [(r["record_id"], r["access"]) for r in
            conn.execute("SELECT record_id, access FROM paper_fields ORDER BY record_id")]
    if "--ids" in args:
        wanted = set(args[args.index("--ids") + 1].split(","))
        return [(i, a, kind_of(a)) for i, a in rows if i in wanted]
    if "--all" in args:
        return [(i, a, kind_of(a)) for i, a in rows]
    # Pilot: spread across the alphabet within each type, deterministic.
    out = []
    for kind, n in PILOT.items():
        of_kind = [(i, a) for i, a in rows if kind_of(a) == kind]
        step = max(1, len(of_kind) // n)
        out += [(i, a, kind) for i, a in of_kind[::step][:n]]
    return out


TERMINAL = ("withdrawn", "retracted")


def keeps_terminal_status(conn, record_id: str, field_name: str, value: str) -> bool:
    """A probe never turns a recorded withdrawal or retraction back into
    `preprint` or `published`. The probe sees a withdrawal only when arXiv's
    comment says the word; Task I (2026-10-04) recorded four from arXiv's
    own signature (/pdf 404) whose comments give only the reason. Both
    states are terminal on their registries."""
    if field_name != "publication_status" or value in TERMINAL:
        return False
    row = conn.execute("SELECT value FROM paper_probes WHERE record_id = ? AND field = 'publication_status'",
                       (record_id,)).fetchone()
    return bool(row and row[0] in TERMINAL)


def probe(record_id: str, access: str, kind: str, fetcher):
    """[(field, value, provider)], notes."""
    found, notes = [], []
    if kind in ("arxiv", "doi"):
        ident = citations.parse_access(access)[1]
        r = probe_arxiv(record_id, ident, fetcher) if kind == "arxiv" else probe_doi(record_id, ident, fetcher)
        found += [(f, v, r.provider) for f, v in sorted(r.values.items())]
        notes += r.notes
    url = landing_url(access)
    if url:
        found.append(("access_status", probe_access(url), "HTTP probe"))
    elif kind == "hand-local":
        notes.append("no public URL: access_status not probed")
    return found, notes


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    apply = "--apply" in args
    heartbeat = Path(args[args.index("--heartbeat") + 1]) if "--heartbeat" in args else None
    conn = connect(DB_PATH)
    try:
        targets = select(conn, args)
        if apply:
            backup_before_write(DB_PATH, "probe reference fields")
        fetcher = citations.PacedFetcher()
        today = date.today().isoformat()
        timings: dict[str, list[float]] = {}
        errors = 0
        for n, (rid, access, kind) in enumerate(targets, 1):
            t0 = time.monotonic()
            try:
                found, notes = probe(rid, access, kind, fetcher)
            except Exception as ex:  # noqa: BLE001 -- one record's failure is reported, the run goes on
                found, notes = [], [f"ERROR {type(ex).__name__}: {ex}"]
                errors += 1
            dt = time.monotonic() - t0
            timings.setdefault(kind, []).append(dt)
            print(f"[{n}/{len(targets)}] {rid} ({kind}, {dt:.1f}s): "
                  + ("; ".join(f"{f}={v} [{p}]" for f, v, p in found) or "nothing answered")
                  + (f"  -- {' | '.join(notes)}" if notes else ""))
            if apply:
                for field_name, value, provider in found:
                    if keeps_terminal_status(conn, rid, field_name, value):
                        print(f"      kept {rid}'s recorded withdrawal or retraction over the probe's {value!r}")
                        continue
                    record_probe(conn, rid, field_name, value, provider, today)
                conn.commit()
            if heartbeat:
                heartbeat.write_text(f"{datetime.now().isoformat(timespec='seconds')} {n}/{len(targets)} {rid}\n",
                                     encoding="utf-8")
        print("\nseconds per record by type: " + ", ".join(
            f"{k}: n={len(v)} mean {sum(v) / len(v):.1f} max {max(v):.1f}" for k, v in timings.items()))
        print(f"errors: {errors}")
        if apply:
            regenerate(conn, EXPORT_DIR)
            print("APPLIED; export regenerated")
        else:
            print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
