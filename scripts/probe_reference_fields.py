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
    python scripts/probe_reference_fields.py --refresh --apply --sessions \
        --progress <file> --heartbeat <file>                     # a full refresh (F53); not run each cycle
    python scripts/probe_reference_fields.py --stale [--before YYYY-MM-DD]
    python scripts/probe_reference_fields.py --due [YYYY-MM-DD]  # list what is due; no request
    python scripts/probe_reference_fields.py --due [YYYY-MM-DD] --probe --apply --sessions \
        --progress <file> [--report <file>]                      # Phase 1.3 (F64, ADR-0005 A7)

DUE (F64, ADR-0005 A7): every paper has a computed section (1 to 24) and a
next re-check date, the first start of its section at least 10 months
after its last check (`store/recheck.py`). `--due` alone lists the papers
due on or before the date given (default today), from stored dates, and
sends no request (Sprint 8 retrospective I4: a dry run of a probe still
probes, and one started by mistake may have sent arXiv requests).
`--due --probe` runs the brief check on them:
arXiv by its abstract page alone (one request), with the latest version
read from the page; other kinds as below; a local path by the file's
presence and SHA-256. It ends with three lists (re-pull, withdrawn, newly
published) plus local files missing or changed and pages whose version
could not be read. Nothing is downloaded.

STALE (F53): a probe measured before the current cycle's start (the date in
the sprint branch's name) is stale once Phase 1.3 has run. `--stale` lists
them and exits 1 when there is any; `--refresh` selects every record with a
stale probe or none. Hand-recorded values are readings, never stale.

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
`--site` skips the API check and uses the abstract page (one request per
paper); a dry run with it checks the page parser against stored API values.

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

import json
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, recheck, script_paths  # noqa: E402
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
MAX_ATTEMPTS = 3       # sessions a record is retried without an arXiv answer
SITE_OPEN = None       # urlopen for the abstract page and access probes; tests inject
_pause = time.sleep    # module attributes so tests do not wait two hours
_now = time.time       # and can move the wall clock the saved state uses


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
    if "--due" in args:
        return [(i, a, kind_of(a)) for i, a, _ in recheck.due(conn, due_date(args))]
    if "--unprobed" in args:
        # No probe at all, or an arXiv record whose status arXiv never
        # answered (a DataCite version_of alone is not a finished probe).
        probed = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_probes")}
        with_status = {r[0] for r in conn.execute(
            "SELECT record_id FROM paper_probes WHERE field = 'publication_status'")}
        return [(i, a, k) for i, a in rows for k in [kind_of(a)]
                if i not in probed or (k == "arxiv" and i not in with_status)]
    if "--refresh" in args:
        # Phase 1.3 (F53): every record with a stale probe or none at all.
        fresh = {r[0] for r in conn.execute("SELECT DISTINCT record_id FROM paper_probes")} - {
            s[0] for s in stale_probes(conn, cycle_start())}
        return [(i, a, kind_of(a)) for i, a in rows if i not in fresh]
    # Pilot: spread across the alphabet within each type, deterministic.
    out = []
    for kind, n in PILOT.items():
        of_kind = [(i, a) for i, a in rows if kind_of(a) == kind]
        step = max(1, len(of_kind) // n)
        out += [(i, a, kind) for i, a in of_kind[::step][:n]]
    return out


def due_date(args: list[str]) -> date:
    """`--due [YYYY-MM-DD]`: the date given, else today. A date in another
    form is refused, never read as today (PR #77 review: `--due 10/13/2026`
    listed, and with --probe checked, the wrong set)."""
    i = args.index("--due")
    nxt = args[i + 1] if i + 1 < len(args) else ""
    if not nxt or nxt.startswith("--"):
        return date.today()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", nxt):
        raise ValueError(f"--due takes a date as YYYY-MM-DD, got {nxt!r}")
    return date.fromisoformat(nxt)


SPRINT_STATUS = ROOT / ".claude" / "sprint_status.json"


def cycle_start(status_path: Path | None = None) -> str:
    """The current delivery cycle's first day, computed from the sprint
    branch's name (`feature/YYYYMMDD_Sprint_N`, cut at Phase 6.6). Phase 1.3
    re-runs the probes, so after it no probe should be older than this."""
    branch = json.loads((status_path or SPRINT_STATUS).read_text(encoding="utf-8"))["current_sprint"]["branch"]
    m = re.search(r"(\d{4})(\d{2})(\d{2})_Sprint", branch)
    if not m:
        raise ValueError(f"cannot read a cycle start date from branch {branch!r}")
    return "-".join(m.groups())


def stale_probes(conn, before: str) -> list[tuple[str, str, str, str]]:
    """(record_id, field, provider, probed_on) for every probe measured
    before `before` (F53). A hand-recorded value (provider 'hand') is a
    reading with an anchor, not a registry measurement, so no probe run can
    refresh it and it is never stale."""
    return [tuple(r) for r in conn.execute(
        "SELECT record_id, field, provider, probed_on FROM paper_probes "
        "WHERE probed_on < ? AND provider <> 'hand' ORDER BY record_id, field", (before,))]


def report_stale(conn, before: str) -> int:
    """`--stale`: list every stale probe; exit 1 when there is any."""
    rows = stale_probes(conn, before)
    for rid, field_name, provider, probed_on in rows:
        print(f"STALE {rid} {field_name} [{provider}] probed {probed_on}")
    records = len({r[0] for r in rows})
    print(f"{len(rows)} probe(s) on {records} record(s) older than the cycle start {before}"
          + ("; refresh with --refresh --apply --sessions --progress <file>" if rows else ""))
    return 1 if rows else 0


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


def probe(record_id: str, access: str, kind: str, fetcher, mode: str = "api", extra: dict | None = None):
    """[(field, value, provider)], notes, arxiv_answered (None when the
    record sent nothing to arXiv). With `extra` (the re-check, F64), the
    page's latest arXiv version and any local-copy check are put there, and
    a local-only record's file check is returned as its access_status."""
    found, notes, answered = [], [], None
    if extra is not None and recheck.local_paths(access):
        status, note = recheck.check_local(access, extra.get("evidence"))
        extra["local"] = (status, note)
        if kind == "hand-local":
            found.append(("access_status", status, recheck.LOCAL_FILE_PROVIDER))
            return found, [note] if note else [], None
    if kind == "arxiv" and mode == "site":
        r = probe_arxiv_site(record_id, citations.parse_access(access)[1], fetcher, _open=SITE_OPEN)
        found += [(f, v, r.provider) for f, v in sorted(r.values.items())]
        if r.access is not None:
            found.append(("access_status", r.access, "HTTP probe"))
        if extra is not None:
            extra["latest_version"] = r.latest_version
        return found, notes + r.notes, r.provider == SITE_PROVIDER
    if kind == "arxiv":
        # API mode: the API for status, version and affiliations, and the
        # abstract page (the second request, which the access probe needs
        # anyway) parsed too. The page shows withdrawals the API comment
        # does not: 4 of the 6 recorded ones (live check, 2026-10-06). If
        # the API did not answer, the page answers in its place.
        ident = citations.parse_access(access)[1]
        api = probe_arxiv(record_id, ident, fetcher)
        page = probe_arxiv_site(record_id, ident, fetcher, _open=SITE_OPEN)
        best = api if api.provider == "arXiv" or page.provider != SITE_PROVIDER else page
        provided = {f: (v, best.provider) for f, v in best.values.items()}
        if page.values.get("publication_status") == "withdrawn" and best is api and \
                api.values.get("publication_status") != "withdrawn":
            provided["publication_status"] = ("withdrawn", SITE_PROVIDER)
            notes.append("withdrawal read from the abstract page; the API comment did not say so")
        found += [(f, v, p) for f, (v, p) in sorted(provided.items())]
        notes += best.notes
        if page.access is not None:
            found.append(("access_status", page.access, "HTTP probe"))
        return found, notes, best.provider in ("arXiv", SITE_PROVIDER)
    if kind == "doi":
        r = probe_doi(record_id, citations.parse_access(access)[1], fetcher)
        found += [(f, v, r.provider) for f, v in sorted(r.values.items())]
        notes += r.notes
        if extra is not None and r.answered and not r.values:
            extra["answered_without_value"] = r.provider
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


FINDING_LISTS = ("re-pull", "withdrawn", "newly published", "local copy missing or changed", "version unread",
                 # F74 (ADR-0005 A9): faults that are not the paper's, and
                 # papers that stay due because their own source was silent
                 # (reported at Manual Validation, team lead Q4 = 1).
                 "primary source did not answer (stays due)", "tool failure", "probe failure")


def recheck_findings(findings: dict[str, list[str]], rid: str, access: str, kind: str, found, before: str | None,
                     extra: dict, local_version_of=None, local_copy_of=None) -> None:
    """Sort one re-checked record into the lists ADR-0005 A7 (d) names.
    `before` is the publication_status stored before this check."""
    # The record's own local path first, then QMLPapers by id (PR #77
    # review: a copy kept in Papers\ under another name was never found, so
    # the record landed in no list).
    local_copy_of = local_copy_of or (lambda ident: recheck.local_pdf(access, ident))
    local_version_of = local_version_of or (lambda ident: recheck.local_version(ident, path=local_copy_of(ident)))
    if not any(recheck.is_primary_answer(kind, p, v) for _, v, p in found):
        sources = " or ".join(recheck.PRIMARY_PROVIDERS.get(kind, ("its source",)))
        # Task D review (2026-10-18): a registry that answered with nothing
        # the store records (an unmapped type, no relation, no affiliation)
        # is not silent; it is said so. The paper still stays due: no
        # publication_status value exists for "the registry states none".
        said = (f"{extra['answered_without_value']} answered but stated nothing the store records"
                if extra.get("answered_without_value") else f"no answer from {sources}")
        findings["primary source did not answer (stays due)"].append(
            f"{rid}: {kind}, {said}" + (f"; others answered: "
            f"{', '.join(sorted({p for _, _, p in found}))}" if found else ""))
    status = next((v for f, v, _ in found if f == "publication_status"), None)
    if status in TERMINAL and before not in TERMINAL:
        findings["withdrawn"].append(f"{rid}: {status}")
    # Only a real change: from `preprint`, or from no status at all (said
    # so). A recorded withdrawal or retraction is kept (keeps_terminal_status),
    # so a probe's `published` over it is not news.
    if status == "published" and before in ("preprint", None):
        doi = next((v for f, v, _ in found if f == "version_of"), "")
        findings["newly published"].append(f"{rid}: {doi or 'no DOI given'}"
                                           + (" (no status was recorded before)" if before is None else ""))
    if kind == "arxiv":
        latest = extra.get("latest_version")
        ident = citations.parse_access(access)[1]
        try:
            local = local_version_of(ident) if latest is not None else None
            tool_error = None
        except recheck.PdfToolError as err:
            local, tool_error = None, err
        if tool_error:
            # The tool's fault, not the paper's (F74): no stamp verdict.
            findings["tool failure"].append(f"{rid}: {tool_error}; the local copy's version was not read")
        elif latest is None:
            findings["version unread"].append(f"{rid}: the abstract page showed no version")
        elif local is not None and latest > local:
            findings["re-pull"].append(f"{rid}: local copy v{local}, arXiv shows v{latest}")
        elif local is None and local_copy_of(ident) is not None:
            findings["version unread"].append(f"{rid}: the local copy's first page has no readable stamp")
    local_check = extra.get("local")
    if local_check and local_check[0] in ("local copy missing", "local copy changed (SHA-256 differs)",
                                          "local copy unreadable"):
        findings["local copy missing or changed"].append(f"{rid}: {local_check[0]} ({local_check[1]})")


def load_findings(path: Path | None) -> dict[str, list[str]]:
    """The lists a stopped run already wrote to `--report`, so a resumed run
    (`--progress` skips finished records) adds to them instead of losing them."""
    findings: dict[str, list[str]] = {name: [] for name in FINDING_LISTS}
    if path and path.exists():
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            head = line.rsplit(":", 1)[0]
            if not line.startswith("  ") and head in findings:
                current = head
            elif line.startswith("  ") and current:
                findings[current].append(line[2:])
    return findings


def report_findings(findings: dict[str, list[str]], path: Path | None, quiet: bool = False) -> None:
    lines = []
    for name in FINDING_LISTS:
        lines.append(f"{name}: {len(findings[name])}")
        lines += [f"  {item}" for item in findings[name]]
    text = "\n".join(lines)
    if not quiet:
        print("\n== re-check lists (nothing downloaded)\n" + text)
    if path:
        path.write_text(text + "\n", encoding="utf-8")


def _beat(heartbeat: Path | None, text: str) -> None:
    if heartbeat:
        heartbeat.write_text(f"{datetime.now().isoformat(timespec='seconds')} {text}\n", encoding="utf-8")


def _state_path(progress: Path | None) -> Path | None:
    return progress.with_name(progress.name + ".state.json") if progress else None


def _save_state(path: Path | None, *, paused_until: float | None = None) -> None:
    """The session's arXiv count, the last request's wall time, and any
    pause, beside the progress file: a restart must honor the cap and the
    pause (Task C review, 2026-10-06: they lived only in process memory)."""
    if path:
        path.write_text(json.dumps({"requests": citations.arxiv_requests_this_session(),
                                    "last_request": _now(), "paused_until": paused_until}), encoding="utf-8")


def _resume_session(path: Path | None) -> bool:
    """Apply a saved state. True when the saved session continues (its count
    restored); False when a new session starts."""
    if not path or not path.exists():
        return False
    state = json.loads(path.read_text(encoding="utf-8"))
    now = _now()
    if state.get("paused_until") and state["paused_until"] > now:
        print(f"resuming inside a pause: waiting {(state['paused_until'] - now) / 60:.0f} more minute(s)")
        _pause(state["paused_until"] - now)
        return False
    if now - state.get("last_request", 0) < PAUSE_HOURS * 3600:
        citations.continue_arxiv_session(int(state.get("requests", 0)))
        _pause(max(0.0, state["last_request"] + citations.ARXIV_MIN_INTERVAL_S - now))
        print(f"resuming the saved session: {citations.arxiv_requests_this_session()} arXiv request(s) already used")
        return True
    return False


def run(conn, targets, fetcher, *, apply: bool, sessions: bool, progress: Path | None,
        heartbeat: Path | None, force_site: bool = False, recheck_mode: bool = False,
        report: Path | None = None) -> int:
    # A report is reloaded only when this run resumes one (its progress file
    # lists finished records); a fresh run over an old report path starts
    # empty (PR #77 review: a dry run then --apply with the same --report
    # listed every finding twice).
    resuming = bool(progress and progress.exists() and progress.read_text(encoding="utf-8").split())
    findings = load_findings(report) if resuming else {name: [] for name in FINDING_LISTS}
    rc = _run(conn, targets, fetcher, apply=apply, sessions=sessions, progress=progress, heartbeat=heartbeat,
              force_site=force_site or recheck_mode, findings=findings if recheck_mode else None,
              report_path=report if recheck_mode else None)
    if recheck_mode:
        report_findings(findings, report)
    return rc


def _run(conn, targets, fetcher, *, apply: bool, sessions: bool, progress: Path | None,
         heartbeat: Path | None, force_site: bool, findings: dict[str, list[str]] | None,
         report_path: Path | None = None) -> int:
    done = set(progress.read_text(encoding="utf-8").split()) if progress and progress.exists() else set()
    todo = [t for t in targets if t[0] not in done]
    if done:
        print(f"resuming: {len(targets) - len(todo)} record(s) already finished per {progress}")
    state = _state_path(progress)
    citations.assume_recent_arxiv_request()  # another process may have just asked arXiv
    continuing = _resume_session(state)
    timings: dict[str, list[float]] = {}
    refusals: dict[str, int] = {}  # arXiv no-answers per record, across sessions
    errors = 0
    session, quiet_sessions = 0, 0
    while todo:
        session += 1
        if not continuing:
            citations.reset_arxiv_session()
        continuing = False
        first_arxiv = next((citations.parse_access(a)[1] for _, a, k in todo if k == "arxiv"), None)
        mode = "site" if force_site or not (first_arxiv and api_answers(first_arxiv, fetcher)) else "api"
        print(f"\n== session {session}: arXiv source = {'API (+ abstract page for access)' if mode == 'api' else 'abstract page'}; "
              f"{len(todo)} record(s) to go")
        no_answers, answered_this_session, stop_reason = 0, 0, None
        remaining, retry = [], []
        for n, (rid, access, kind) in enumerate(todo, 1):
            if stop_reason:
                remaining.append((rid, access, kind))
                continue
            t0 = time.monotonic()
            extra, before = None, None
            if findings is not None:
                extra = {"evidence": conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?",
                                                  (rid,)).fetchone()[0]}
                row = conn.execute("SELECT value FROM paper_probes WHERE record_id = ? AND "
                                   "field = 'publication_status'", (rid,)).fetchone()
                before = row[0] if row else None
            try:
                found, notes, answered = probe(rid, access, kind, fetcher, mode, extra)
            except citations.ArxivSessionCapReached:
                # BEFORE the catch-all: the record is not written and not
                # marked done, so the next session redoes it.
                stop_reason = "cap"
                remaining.append((rid, access, kind))
                continue
            except Exception as ex:  # noqa: BLE001 -- one record's failure is reported, the run goes on
                found, notes, answered = [], [f"ERROR {type(ex).__name__}: {ex}"], None
                errors += 1
                probe_error = f"{rid}: the probe raised {type(ex).__name__}: {ex}"
            else:
                probe_error = None
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
            if findings is not None and extra is not None:
                # One set of findings per record: a retry in a later session
                # replaces this record's lines instead of adding to them.
                for name in FINDING_LISTS:
                    findings[name] = [x for x in findings[name] if not x.startswith(f"{rid}: ")]
                if probe_error:
                    # A probe that raised says nothing about the paper (F74):
                    # reported as a probe failure, never as "showed no version".
                    findings["probe failure"].append(probe_error)
                else:
                    try:
                        recheck_findings(findings, rid, access, kind, found, before, extra)
                    except Exception as ex:  # noqa: BLE001 -- a sorting failure is a finding, not the end of the run
                        findings["probe failure"].append(f"{rid}: could not be sorted ({type(ex).__name__}: {ex})")
                if report_path:
                    report_findings(findings, report_path, quiet=True)  # written as it grows: a stop loses nothing
            if apply:
                for field_name, value, provider in found:
                    if keeps_terminal_status(conn, rid, field_name, value):
                        print(f"      kept {rid}'s recorded withdrawal or retraction over the probe's {value!r}")
                        continue
                    record_probe(conn, rid, field_name, value, provider, date.today().isoformat())  # the run crosses midnight
                conn.commit()
            finished = True
            if answered is True:
                no_answers, answered_this_session = 0, answered_this_session + 1
            elif answered is False:
                no_answers += 1
                refusals[rid] = refusals.get(rid, 0) + 1
                # arXiv did not answer this record: whatever DataCite gave is
                # kept, but the record is NOT finished, so a later session
                # asks arXiv again for its status (Task C review, 2026-10-06),
                # up to MAX_ATTEMPTS sessions so the run always ends.
                if refusals[rid] < MAX_ATTEMPTS:
                    finished = False
                    retry.append((rid, access, kind))
                else:
                    print(f"      gave up on {rid} after {MAX_ATTEMPTS} sessions without an arXiv answer")
                if no_answers >= MAX_NO_ANSWERS:
                    stop_reason = "refused"
                    print(f"      {MAX_NO_ANSWERS} arXiv no-answers in a row: ending session {session} early")
            if finished and progress:
                with progress.open("a", encoding="utf-8") as fh:
                    fh.write(rid + "\n")
            _save_state(state)
            _beat(heartbeat, f"session {session} ({mode}) arXiv requests {citations.arxiv_requests_this_session()}/"
                             f"{citations.ARXIV_SESSION_CAP} record {n}/{len(todo)} {rid}")
        todo = remaining + retry
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
        _save_state(state, paused_until=_now() + PAUSE_HOURS * 3600)
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
    # Another process (Task E's linking, an intake) may write during a
    # 20-hour run; wait up to 2 minutes for its lock instead of 5 seconds.
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        if "--stale" in args:
            before = args[args.index("--before") + 1] if "--before" in args else cycle_start()
            return report_stale(conn, before)
        try:
            targets = select(conn, args)
        except ValueError as ex:
            print(f"error: {ex}", file=sys.stderr)
            return 2
        if "--due" in args and "--probe" in args and "--progress" in args and "--report" not in args:
            # A resumed run skips finished records, so their findings live
            # only in the report (PR #77 review).
            print("error: --due --probe --progress needs --report, or a resumed run loses the first run's findings",
                  file=sys.stderr)
            return 2
        if "--due" in args and "--probe" in args and not recheck.QMLPAPERS.exists():
            print(f"WARNING: {recheck.QMLPAPERS} is missing; only records whose access names a local path can be "
                  "version-checked", file=sys.stderr)
        if "--due" in args and "--probe" not in args:
            # Sprint 8 retrospective I4: without --probe, --due only lists,
            # from stored dates; no request is sent and nothing is written.
            if apply:
                print("error: --due --apply checks the web; add --probe to say so", file=sys.stderr)
                return 1
            print(f"{len(targets)} record(s) due on or before {due_date(args)} (ADR-0005 A7); listed from "
                  "stored dates, no request sent. Add --probe to check them.")
            for rid, access, _ in targets:
                section, last, nxt = recheck.schedule(conn, rid)
                print(f"  {rid}  section {section}  last {last or '-'}  next {nxt or 'now'}  {access}")
            return 0
        if apply:
            backup_before_write(DB_PATH, "probe reference fields")
        if "--due" in args:
            print(f"{len(targets)} record(s) due on or before {due_date(args)} (ADR-0005 A7)")
        rc = run(conn, targets, citations.PacedFetcher(), apply=apply, sessions="--sessions" in args,
                 progress=path_arg("--progress"), heartbeat=path_arg("--heartbeat"), force_site="--site" in args,
                 recheck_mode="--due" in args, report=path_arg("--report"))
        print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
        return rc
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
