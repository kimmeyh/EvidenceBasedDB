#!/usr/bin/env python3
"""Sprint 13 Task G (F113): the full re-read entered, one ledger, no budget.

Team lead, 2026-10-25, at Manual Validation: "fully read all the papers that
are not marked 'read' and update all conclusions ... It is far more
important to read them all, get all the conclusions, profs, assertions...
than some budget". `manifests/sprint13_g_ledger.json` gives every record
not read in full to exactly one group. One Sonnet 5.5 reader per group read
each paper whole under `manifests/sprint13_g_reads/READER_PROMPT.md` and
wrote a verdict on every stored assertion and every claim the stored ones
miss; the coordinator copies the reader file, unchanged, to
`manifests/sprint13_g_reads/group_<g>.json` at its review. A reader file
whose records are not exactly its group's is refused.

HOW THE SOURCES WERE READ (ADR-0005 A4: a subagent's read alone never
qualifies `read`): the reader read the whole paper. The coordinator checked
every quote against the source text by script (`require_verbatim`, with the
value's figures) and read every value against its quoted passages in
context. The tables below record that read.

WHAT IS WRITTEN:
- a new claim: inserted, graded as in Task F;
- a stored assertion the reader corrected, narrowed, widened or
  contradicted: synced to the reader's value and quotes, regraded, unless
  the coordinator keeps the stored one (KEEP_STORED, with why);
- a stored assertion the reader confirmed: unchanged, unless the
  coordinator takes the reader's fuller quotes (REQUOTE), for example a
  theorem's statement and conditions that can carry a HIGH;
- a stored assertion the reader found "not in the paper": the
  coordinator's decision in NOT_IN_PAPER, with why.
Each synced assertion's updated_reason carries FULL_READ_MARK, so a later
apply of the script that first wrote it does not undo the full read (the
store's sync refuses to, by that mark).

THE COORDINATOR'S REVIEW of each group is `manifests/sprint13_g_reviews/
<g>.json`, loaded into the tables below: the date, the HIGH grades with
their basis, the cause of every theoretical result kept LOW, and every edit.
A group is entered only once its review exists.

CERTAINTY: HIGH only through `store.grading.high_grades`, each id with its
basis and where the paper settles it; every LOW names its reason through
`store.grading.low_grade`. The reader's `certainty_suggestion` is never
used. The LOW reason follows the result type as the coordinator settled it
(the reader's, or RESULT_TYPE_FIX where the coordinator read it otherwise):
a theoretical result kept LOW needs its cause in THEORY_LOW, and the run
refuses one without; a setup statement not graded HIGH is the authors'
claim.

    python scripts/sprint13_g_reading.py                     # dry run of every reviewed group
    python scripts/sprint13_g_reading.py --groups g001,g002  # dry run of named groups
    python scripts/sprint13_g_reading.py --apply             # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import grade, high_grades, low_grade  # noqa: E402
from store.ingest import (FULL_READ_MARK, AssertionRecord, add_read, append_updated_reason,  # noqa: E402
                          insert_verified_assertion, set_tier, sync_verified_assertion, validate_assertion)
from store.quotes import QUOTE, plain, require_edit_basis, require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TAG = "Sprint 13 Task G, F113"
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
READS_DIR = ROOT / "manifests" / "sprint13_g_reads"
SUBAGENT_READER = f80.SUBAGENT_READER
COORDINATOR_DETAIL = ("every quoted passage read in context and every quote and figure checked against the source by "
                      "script; the paper read whole by the first-pass reader, whose verdicts on the stored assertions "
                      "the coordinator read against their passages")
CHANGED = {"corrected", "narrowed", "widened", "contradicted"}

# The date each group was reviewed and entered: a group's reads carry it, so a second apply on any day writes nothing.
REVIEWED_ON: dict[str, str] = {}

# The coordinator's read, as in Task F; each entry rests on named passages.
QUOTE_EDITS: dict[str, list[tuple[str, str | None]]] = {}
EXTRA_QUOTES: dict[str, list[str]] = {}
VALUE_REPLACE: dict[str, str] = {}  # each replacement says only what its quotes say
CONTEXT_FIX: dict[str, str] = {}
ANCHOR_FIX: dict[str, str] = {}
DROP: dict[str, str] = {}  # a new assertion not entered, with the reason
KEEP_STORED: dict[str, str] = {}  # a stored assertion kept against the reader's verdict, with why
REQUOTE: dict[str, str] = {}  # a confirmed stored assertion rebuilt from the reader's fuller quotes, with why
NOT_IN_PAPER: dict[str, str] = {}  # the coordinator's decision on a stored claim the paper does not hold
VENDOR_DESCRIPTIONS: set[str] = set()
FIELD_STATEMENTS: set[str] = set()

THEORY_LOW: dict[str, str] = {}  # a theoretical result kept LOW, with its cause
MEASURED_DESPITE: dict[str, str] = {}  # a measured result whose words name a proof or a bound, with why
RESULT_TYPE_FIX: dict[str, str] = {}  # the coordinator's result type where it differs from the reader's
EXTENT_FIX: dict[str, list[str]] = {}  # record id -> [extent, detail]: the coordinator's reading of a read's extent
ID_FIX: dict[str, str] = {}  # a new assertion's id where the reader's suggestion is already another source's

REVIEWS_DIR = ROOT / "manifests" / "sprint13_g_reviews"
_TABLES = {"quote_edits": QUOTE_EDITS, "extra_quotes": EXTRA_QUOTES, "value_replace": VALUE_REPLACE,
           "context_fix": CONTEXT_FIX, "anchor_fix": ANCHOR_FIX, "drop": DROP, "keep_stored": KEEP_STORED,
           "requote": REQUOTE, "not_in_paper": NOT_IN_PAPER, "theory_low": THEORY_LOW,
           "measured_despite": MEASURED_DESPITE, "result_type_fix": RESULT_TYPE_FIX, "extent_fix": EXTENT_FIX,
           "id_fix": ID_FIX}
RESULT_TYPES = {"measured": "measured result", "claim": "authors' claim", "cited": "cited claim",
                "field": "field statement", "setup": "authors' claim"}


def _load_reviews() -> dict[str, tuple[str, str]]:
    """Fill the tables from every review file; an id named by two groups is refused."""
    high: dict[str, tuple[str, str]] = {}
    for path in sorted(REVIEWS_DIR.glob("g*.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        g = review["group"]
        if path.stem != g:
            raise ValueError(f"{path.name} holds group {g}")
        REVIEWED_ON[g] = review["reviewed_on"]
        for key, table in _TABLES.items():
            for aid, v in review.get(key, {}).items():
                if aid in table:
                    raise ValueError(f"{aid}: named in {key} by two groups")
                table[aid] = [tuple(edit) for edit in v] if key == "quote_edits" else v
        for aid, (basis, why) in review["graded_high"].items():
            if aid in high:
                raise ValueError(f"{aid}: graded HIGH by two groups")
            high[aid] = (basis, why)
    moved = edits_under_moved_ids()
    if moved:
        raise ValueError(f"{moved}: an edit under an id that ID_FIX moves; name the edit under the stored id")
    return high


def edits_under_moved_ids() -> list[str]:
    """record() and verify() look an edit up under the stored id, so an edit under a reader's id that ID_FIX moves
    would be neither written nor checked (reviews of 6d8dec7 and 9c79048); anchor and context fixes too (review of
    57107f1)."""
    edits = set(VALUE_REPLACE) | set(QUOTE_EDITS) | set(EXTRA_QUOTES) | set(ANCHOR_FIX) | set(CONTEXT_FIX)
    return sorted(set(ID_FIX) & edits)


HIGH = high_grades(_load_reviews())

ONLY: list[str] = []


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def groups() -> list[str]:
    """The reviewed groups: those with a date in REVIEWED_ON, or ONLY's for a dry run."""
    names = ONLY or sorted(REVIEWED_ON)
    missing = [g for g in names if g not in ledger()["groups"]]
    if missing:
        raise ValueError(f"not in the ledger: {missing}")
    return names


def load_groups() -> list[tuple[str, dict]]:
    """Every paper of the reviewed groups; refuses a reader file whose records are not its group's."""
    out, L = [], ledger()
    for g in groups():
        papers = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))["papers"]
        want = {r["record_id"] for r in L["groups"][g]["records"]}
        got = [p["record_id"] for p in papers]
        if set(got) != want or len(got) != len(want):
            raise ValueError(f"group {g}: reader file records {sorted(set(got) ^ want)} differ from the ledger")
        out += [(g, p) for p in papers]
    return out


def quotes_of(aid: str, a: dict) -> list[str]:
    qs = list(a.get("quotes") or [])
    for old, new in QUOTE_EDITS.get(aid, []):
        hits = [i for i, q in enumerate(qs) if old in q]
        if not hits:
            raise ValueError(f"{aid}: the quote text to replace is not there: {old[:60]!r}")
        if new is None:
            del qs[hits[0]]
        else:
            qs[hits[0]] = qs[hits[0]].replace(old, new)
    return qs + EXTRA_QUOTES.get(aid, [])


def certainty(aid: str, a: dict) -> tuple[str, str]:
    if a["claim_type"] == "vendor-self-claim":
        if aid in VENDOR_DESCRIPTIONS:
            return "moderate", f"{f80.VENDOR_START}. Not upgraded: a description of the product, not a result"
        return low_grade("vendor claim")
    kind = result_type(aid, a)
    if aid in HIGH:
        return grade(aid, HIGH, otherwise=low_grade("authors' claim"))  # never used: aid is in HIGH
    if kind == "theoretical":
        if aid not in THEORY_LOW:
            raise ValueError(f"{aid}: a theoretical result kept LOW names its cause in THEORY_LOW")
        return low_grade("theoretical result", THEORY_LOW[aid])
    if aid in THEORY_LOW:
        raise ValueError(f"{aid}: in THEORY_LOW but its result type is {kind!r}")
    if kind == "vendor":
        return low_grade("vendor claim")
    return low_grade("field statement" if aid in FIELD_STATEMENTS else RESULT_TYPES[kind])


def result_type(aid: str, a: dict) -> str:
    return RESULT_TYPE_FIX.get(aid, a["result_type"])


def anchor_safe(anchor: str) -> str:
    return anchor.replace('"', "'")  # a quote mark inside a label would break the quote pattern


def record(g: str, rid: str, aid: str, a: dict, why: str, sid: str | None = None) -> AssertionRecord:
    """Graded under the reader's id `aid`; stored, and edited, under `sid` (ID_FIX's id, else `aid`), the id
    verify() checks an edit under (review of 9c79048)."""
    sid = sid or aid
    cert, reasons = certainty(aid, a)
    anchor = anchor_safe(ANCHOR_FIX.get(sid) or a["anchor"])
    return AssertionRecord(
        id=sid, value=" ".join((VALUE_REPLACE.get(sid) or a["value"]).split()),
        provenance=f"{rid}, {anchor}",
        citation_context="; ".join(f'"{q}" ({anchor})' for q in quotes_of(sid, a)),
        evidence_tag="N/A", context=CONTEXT_FIX.get(sid) or a["context"], certainty=cert,
        certainty_reasons=reasons, fidelity=a.get("fidelity") or "scoped", derivation="extracted",
        claim_type=a["claim_type"],
        search_scope=("the paper's own text, as read" if a["claim_type"] == "absence" else None),
        updated=REVIEWED_ON.get(g, ""), updated_reason=(
            f"{REVIEWED_ON.get(g, '')} ({TAG}): {FULL_READ_MARK}: {why} from {rid}; the paper read whole by a "
            "first-pass subagent, every quoted passage read in context by the coordinator"))


def assertions() -> list[tuple[str, AssertionRecord, str, dict]]:
    """(group, record, paper id, paper) for every new claim entered and every stored one changed."""
    out = []
    for g, p in load_groups():
        rid = p["record_id"]
        for e in p.get("existing", []):
            aid = e["id"]
            if aid in KEEP_STORED or aid in NOT_IN_PAPER:
                continue
            if e["verdict"] in CHANGED or (e["verdict"] == "confirmed" and aid in REQUOTE):
                out.append((g, record(g, rid, aid, e, f"{e['verdict']} at a full read"), rid, p))
        for a in p.get("assertions", []):
            aid = a["id_suggestion"]
            if aid not in DROP:
                out.append((g, record(g, rid, aid, a, "extracted at a full read", ID_FIX.get(aid, aid)), rid, p))
    return out


def grades_not_written(conn) -> list[str]:
    """A confirmed stored assertion the review grades but the apply does not write (it is not in REQUOTE) keeps
    its stored certainty; each one whose stored certainty is not the review's grade (review of 6d8dec7)."""
    problems = []
    for _, p in load_groups():
        for e in p.get("existing", []):
            aid = e["id"]
            if e["verdict"] in CHANGED or aid in REQUOTE or aid in KEEP_STORED or aid in NOT_IN_PAPER:
                continue
            if aid in HIGH:
                want = grade(aid, HIGH, otherwise=low_grade("authors' claim"))[0]
            elif aid in THEORY_LOW:
                want = low_grade("theoretical result", THEORY_LOW[aid])[0]
            else:
                continue
            row = conn.execute("SELECT certainty FROM records WHERE id = ?", (aid,)).fetchone()
            if row is None or row[0] != want:
                problems.append(f"{aid}: graded {want}, stored {row[0] if row else 'nothing'}, and not rewritten; "
                                "add it to REQUOTE or change the grade")
    return problems


def verify() -> list[tuple[AssertionRecord, str, dict, object]]:
    """Every quote verbatim in its source, every coordinator edit resting on named passages, and every figure in
    a value in its own quotes, BEFORE anything is written."""
    texts: dict[str, str] = {}
    out = []
    for _, a, rid, p in assertions():
        quotes = QUOTE.findall(a.citation_context)
        text = texts.setdefault(p["file"], plain(source_text(p["file"])))
        verified = require_verbatim(a.id, a.citation_context, text, value=a.value)
        if a.id in VALUE_REPLACE:
            require_edit_basis(a.id, a.value, quotes, text)
        if a.id in QUOTE_EDITS:
            require_edit_basis(a.id, None, [n for _, n in QUOTE_EDITS[a.id] if n] or quotes, text)
        out.append((a, rid, p, verified))
    return out


def read_detail(g: str, p: dict) -> str:
    """The reader's account of its read, in the store's words, never the reader's own ("skimmed" and the like);
    the coordinator's EXTENT_FIX where it read the extent otherwise."""
    extent, why = EXTENT_FIX.get(p["record_id"], (p.get("read_extent"), p.get("not_read", "")))
    if extent == "full":
        detail = "first pass, the whole paper, every page and appendix"
        if p["record_id"] in EXTENT_FIX:
            detail += f" ({why.rstrip('.')})"
    else:
        detail = f"first pass, the whole paper except: {why}"
    detail += f" (Sonnet 5.5 reader, {TAG}, group {g})"
    if p.get("version_note"):
        detail += f"; version: {p['version_note']}"
    return detail


def is_mine(extent: str, detail: str) -> bool:
    """A paper_reads row this script wrote. Task F (F112) read 57 of these papers on 2026-10-25, a review day of
    Task G's, under the same reader names, and the first apply took Task F's rows for its own and rewrote their
    detail (full suite, 2026-10-27); a row is matched by its wording, never by reader, day and extent alone."""
    return TAG in detail if extent == "subagent" else detail.startswith(COORDINATOR_DETAIL[:40])


def apply_changes(conn) -> list[str]:
    checked = verify()
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    for g, p in load_groups():
        rid, detail, day = p["record_id"], read_detail(g, p), REVIEWED_ON[g]
        have = {(r[0], r[1], r[2]): r[3] for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,)) if is_mine(r[2], r[3])}
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        path = p["file"].replace("/", "\\")
        if path.lower() not in {s.lower() for s in recheck.local_paths(access or "")}:
            note = f"Local copy {f80._sha(Path(path))}, recorded {day} ({TAG})"
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ? WHERE record_id = ?",
                         (f"{access} | {path}" if access else path,
                          f"{evidence.rstrip().rstrip('.')}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{day} ({TAG}): local copy added to access", day)
            log.append(f"access {rid}")
        for aid, why in NOT_IN_PAPER.items():
            if any(e["id"] == aid for e in p.get("existing", [])):
                note = f"{day} ({TAG}): {FULL_READ_MARK}: NOT in the paper at a full read: {why}"
                stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (aid,)).fetchone()[0] or ""
                if note not in stored:
                    append_updated_reason(conn, aid, note, day)
                    log.append(f"not in paper {aid}")
        kept = [a for a in p.get("assertions", []) if a["id_suggestion"] not in DROP]
        entered = kept or [e for e in p.get("existing", []) if e["id"] not in NOT_IN_PAPER]
        for reader, extent, det in ((SUBAGENT_READER, "subagent", detail), ("Claude", "partial", COORDINATOR_DETAIL)):
            if (reader, day, extent) not in have:
                add_read(conn, rid, reader, day, extent, det)
                log.append(f"read   {rid} [{reader}, {extent}]")
            elif have[(reader, day, extent)] != det:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? AND read_on = ? "
                             "AND extent = ? AND detail = ?", (det, rid, reader, day, extent, have[(reader, day, extent)]))
                log.append(f"update read {rid} [{reader}]")
        if not entered:
            why = p.get("why_not") or "; ".join(DROP.get(a["id_suggestion"], "") for a in p.get("assertions", []))
            note = f"{day} ({TAG}): read whole at first pass and NOT entered: {why}"
            stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
            if note not in stored:
                append_updated_reason(conn, rid, note, day)
                log.append(f"refuse {rid}")
            continue
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            ctx = p["bears_on_context"]
            if ctx not in contexts:
                raise ValueError(f"{rid}: applicability context {ctx!r} is not a context")
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, f"{p['what_it_is'].rstrip('.')} -- first-pass full read"))
            log.append(f"applic {rid} [{ctx}]")
        if tier != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{day}, Claude, read every quoted passage in context and checked every quote and figure against "
                "the source; the paper read whole at first pass by a subagent"))
            log.append(f"tier   {rid} -> read")
    for a, rid, _, verified in checked:
        if a.context not in contexts:
            raise ValueError(f"{a.id}: context {a.context!r} is not a context")
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, a.updated_reason, a.updated)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--groups" in args:
        if "--apply" in args:
            print("--groups is for a dry run; an apply enters every reviewed group")
            return 1
        ONLY[:] = args[args.index("--groups") + 1].split(",")
    kept = assertions()
    ids = [a.id for _, a, _, _ in kept]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    owner = {a.id: rid for _, a, rid, _ in kept}
    with connect(DB_PATH) as conn:
        clash = [i for i in ids if conn.execute(
            "SELECT 1 FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ? AND "
            "r.provenance NOT LIKE ?", (i, f"%{owner[i]}%")).fetchone()]
        unwritten = grades_not_written(conn)
    if dupes or clash or unwritten:
        print(f"duplicate assertion ids: {dupes}; ids already held by another source: {clash}")
        print("\n".join(unwritten))
        return 1
    if "--apply" not in args:
        checked = verify()
        for a, _, _, _ in checked:
            validate_assertion(a)
        papers = load_groups()
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"{len(kept)} assertions entered or changed from {len(papers)} records. Every quote verbatim, every "
              "edit on named passages, every figure in its quotes. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, f"{TAG} full reads entered")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
