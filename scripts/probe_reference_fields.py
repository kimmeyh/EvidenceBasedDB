#!/usr/bin/env python3
"""Run the computed-field probes (ADR-0005 A4 (b), Sprint 6 Task F) and keep
each one's last result, date and provider (the probe rule).

`store/probes.py` computes; this script chooses which records, times the
run, and writes through `store.ingest.record_probe`. arXiv traffic is
serial, 18 s apart, and capped per session (Sprint 7 Task C, F52):

    python scripts/probe_reference_fields.py --pilot             # 30 records across source types, dry run
    python scripts/probe_reference_fields.py --pilot --apply
    python scripts/probe_reference_fields.py --unprobed --apply --sessions \
        --progress <file> --heartbeat <file>                     # the bulk run, overnight
    python scripts/probe_reference_fields.py --ids a,b,c [--apply]
    python scripts/probe_reference_fields.py --all [--apply]

SESSIONS (team lead, 2026-10-04 and Sprint 7 Q5-Q7): at most
citations.ARXIV_SESSION_CAP arXiv requests per session, then a pause of at
least PAUSE_HOURS. The cap is counted on the shared arXiv clock and raises
before the request over it goes out; the record it interrupts is not
written and not marked done, so the next session redoes it. Without
`--sessions` the run stops at the cap (exit 2). A session also ends early
after MAX_NO_ANSWERS arXiv no-answers in a row: refusals are a signal about
this client, and spending the rest of the budget on them is the failure
Sprint 6 measured. Two sessions in a row that end that way with nothing
answered stop the run (exit 3).

SOURCE (Q5 = 1): each session starts with ONE API request. If the API
answers, that session uses the API for status, version and affiliations
and the abstract page for access (two arXiv requests per paper); if not,
the abstract page alone answers status, version and access in one request.

RESUME: `--progress <file>` lists every record whose probe finished, one id
per line; a later run with the same file skips them. The store records
measurements only, never an attempt.

DRY-RUN BY DEFAULT: prints what each probe found and how long it took.
`--apply` takes a verified backup first and commits per record, so a stop
loses nothing. Never stores a guess: a probe that cannot answer a field
leaves it unset and says why. A value that differs from the stored one is
printed as DIFFERS.
"""
from __future__ import annotations

import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import record_probe  # noqa: E402
from store.probes import (  # noqa: E402
    SITE_PROVIDER, _arxiv_entry, landing_url, probe_access, probe_arxiv, probe_arxiv_site, probe_doi,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PILOT = {"arxiv": 12, "doi": 10, "github": 3, "hand-url": 5}  # 30, every source type
PAUSE_HOURS = 2.0      # team lead, 2026-10-04: "pause for 2 hours"
MAX_NO_ANSWERS = 3     # arXiv no-answers in a row that end a session early
SITE_OPEN = None       # urlopen for the abstract page and access probes; tests inject
_pause = time.sleep    # module attribute so tests do not wait two hours


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
    if "--unprobed" in args:
        probed = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_probes")}
        return [(i, a, kind_of(a)) for i, a in rows if i not in probed]
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


def api_answers(ident: str, fetcher) -> bool:
    """The once-per-session check (Q5 = 1): does the arXiv API answer now?
    One request, counted against the cap like any other."""
    try:
        return _arxiv_entry(ident, fetcher) is not None
    except citations.ARXIV_FAILURES:
        return False


def probe(record_id: str, access: str, kind: str, fetcher, mode: str = "api"):
    """[(field, value, provider)], notes, arxiv_answered (None when the
    record sent nothing to arXiv)."""
    found, notes, answered = [], [], None
    if kind == "arxiv" and mode == "site":
        r = probe_arxiv_site(record_id, citations.parse_access(access)[1], fetcher, _open=SITE_OPEN)
        found += [(f, v, r.provider) for f, v in sorted(r.values.items())]
        if r.access is not None:
            found.append(("access_status", r.access, "HTTP probe"))
        return found, notes + r.notes, r.provider == SITE_PROVIDER
    if kind in ("arxiv", "doi"):
        ident = citations.parse_access(access)[1]
        r = probe_arxiv(record_id, ident, fetcher) if kind == "arxiv" else probe_doi(record_id, ident, fetcher)
        found += [(f, v, r.provider) for f, v in sorted(r.values.items())]
        notes += r.notes
        if kind == "arxiv":
            answered = r.provider == "arXiv"
    url = landing_url(access)
    if url:
        # Paced and counted like every request that lands on arXiv: the
        # landing page of an arXiv record IS arxiv.org (Sprint 6 Phase 5 review).
        if hasattr(fetcher, "wait_for"):
            fetcher.wait_for(url)
        status = probe_access(url, _open=SITE_OPEN)
        if status is None:
            notes.append("access probe got no answer (429, 5xx or no connection); last measurement kept")
        else:
            found.append(("access_status", status, "HTTP probe"))
    elif kind == "hand-local":
        notes.append("no public URL: access_status not probed")
    return found, notes, answered


def _beat(heartbeat: Path | None, text: str) -> None:
    if heartbeat:
        heartbeat.write_text(f"{datetime.now().isoformat(timespec='seconds')} {text}\n", encoding="utf-8")


def run(conn, targets, fetcher, *, apply: bool, sessions: bool, progress: Path | None,
        heartbeat: Path | None) -> int:
    done = set(progress.read_text(encoding="utf-8").split()) if progress and progress.exists() else set()
    todo = [t for t in targets if t[0] not in done]
    if done:
        print(f"resuming: {len(targets) - len(todo)} record(s) already finished per {progress}")
    timings: dict[str, list[float]] = {}
    errors = 0
    session, quiet_sessions = 0, 0
    while todo:
        session += 1
        citations.reset_arxiv_session()
        first_arxiv = next((citations.parse_access(a)[1] for _, a, k in todo if k == "arxiv"), None)
        mode = "api" if first_arxiv and api_answers(first_arxiv, fetcher) else "site"
        print(f"\n== session {session}: arXiv source = {'API (+ abstract page for access)' if mode == 'api' else 'abstract page'}; "
              f"{len(todo)} record(s) to go")
        no_answers, answered_this_session, stop_reason = 0, 0, None
        remaining = []
        for n, (rid, access, kind) in enumerate(todo, 1):
            if stop_reason:
                remaining.append((rid, access, kind))
                continue
            t0 = time.monotonic()
            try:
                found, notes, answered = probe(rid, access, kind, fetcher, mode)
            except citations.ArxivSessionCapReached:
                # BEFORE the catch-all: the record is not written and not
                # marked done, so the next session redoes it.
                stop_reason = "cap"
                remaining.append((rid, access, kind))
                continue
            except Exception as ex:  # noqa: BLE001 -- one record's failure is reported, the run goes on
                found, notes, answered = [], [f"ERROR {type(ex).__name__}: {ex}"], None
                errors += 1
            dt = time.monotonic() - t0
            timings.setdefault(kind, []).append(dt)
            print(f"[{n}/{len(todo)}] {rid} ({kind}, {dt:.1f}s): "
                  + ("; ".join(f"{f}={v} [{p}]" for f, v, p in found) or "nothing answered")
                  + (f"  -- {' | '.join(notes)}" if notes else ""))
            for field_name, value, provider in found:
                row = conn.execute("SELECT value FROM paper_probes WHERE record_id = ? AND field = ?",
                                   (rid, field_name)).fetchone()
                if row and row[0] != value:
                    print(f"      DIFFERS {rid} {field_name}: stored {row[0]!r}, probe {value!r} [{provider}]")
            if apply:
                for field_name, value, provider in found:
                    if keeps_terminal_status(conn, rid, field_name, value):
                        print(f"      kept {rid}'s recorded withdrawal or retraction over the probe's {value!r}")
                        continue
                    record_probe(conn, rid, field_name, value, provider, date.today().isoformat())  # the run crosses midnight
                conn.commit()
            if progress:
                with progress.open("a", encoding="utf-8") as fh:
                    fh.write(rid + "\n")
            if answered is True:
                no_answers, answered_this_session = 0, answered_this_session + 1
            elif answered is False:
                no_answers += 1
                if no_answers >= MAX_NO_ANSWERS:
                    stop_reason = "refused"
                    print(f"      {MAX_NO_ANSWERS} arXiv no-answers in a row: ending session {session} early")
            _beat(heartbeat, f"session {session} ({mode}) arXiv requests {citations.arxiv_requests_this_session()}/"
                             f"{citations.ARXIV_SESSION_CAP} record {n}/{len(todo)} {rid}")
        todo = remaining
        used = citations.arxiv_requests_this_session()
        print(f"== session {session} ended ({stop_reason or 'all records done'}): {used} arXiv request(s), "
              f"{answered_this_session} arXiv record(s) answered, {len(todo)} record(s) to go")
        if not todo:
            break
        quiet_sessions = quiet_sessions + 1 if stop_reason == "refused" and answered_this_session == 0 else 0
        if quiet_sessions >= 2:
            print("STOPPED: two sessions in a row ended on refusals with nothing answered. arXiv is refusing "
                  "this client; resume later with the same --progress file.")
            _beat(heartbeat, f"STOPPED after session {session}: arXiv refusing; {len(todo)} to go")
            return 3
        if not sessions:
            print(f"SESSION CAP: stopped after {used} arXiv request(s). Pause at least {PAUSE_HOURS:g} hours, "
                  "then resume with the same --progress file.")
            return 2
        until = datetime.now() + timedelta(hours=PAUSE_HOURS)
        print(f"   pausing {PAUSE_HOURS:g} h, until {until:%H:%M}")
        _beat(heartbeat, f"session {session} done, {len(todo)} to go; paused until {until:%Y-%m-%d %H:%M}")
        _pause(PAUSE_HOURS * 3600)
    if timings:
        print("\nseconds per record by type: " + ", ".join(
            f"{k}: n={len(v)} mean {sum(v) / len(v):.1f} max {max(v):.1f}" for k, v in timings.items()))
    print(f"errors: {errors}")
    _beat(heartbeat, f"FINISHED after {session} session(s); errors {errors}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    apply = "--apply" in args

    def path_arg(name: str) -> Path | None:
        return Path(args[args.index(name) + 1]) if name in args else None

    conn = connect(DB_PATH)
    try:
        targets = select(conn, args)
        if apply:
            backup_before_write(DB_PATH, "probe reference fields")
        rc = run(conn, targets, citations.PacedFetcher(), apply=apply, sessions="--sessions" in args,
                 progress=path_arg("--progress"), heartbeat=path_arg("--heartbeat"))
        print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
        return rc
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
