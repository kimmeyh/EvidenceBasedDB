#!/usr/bin/env python3
"""Sprint 13 Task G (F113): the full re-read entered, one ledger, no budget.
Named `sprint13_g_reading.py` until Sprint 14 (retrospective Q5): it enters
F114's groups too, so the name now says what it does. History before the
rename (CHANGELOG, INTAKE_WORKFLOW.md) keeps the old name.

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

    python scripts/full_read_apply.py                     # dry run of every reviewed group
    python scripts/full_read_apply.py --groups g001,g002  # dry run of named groups
    python scripts/full_read_apply.py --apply             # verified backup first
    python scripts/full_read_apply.py --apply --update-reads  # also rewrite read rows, when intended

An apply that would rewrite a read row this script wrote earlier is rolled
back unless --update-reads names the rewrite as intended (Sprint 13
retrospective I1).

The dry run reports every refusal at once, not the first (Sprint 14
retrospective Q4). Every apply, the trial on a copy first, lists each field
it changed on a stored assertion that no review item names, as "undecided"
lines and a count (Sprint 14 retrospective Q2: the reader's context label
replaced two stored contexts, and only the live suite found it).
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import DEFAULT_STORE_DIR, connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import grade, high_grades, low_grade  # noqa: E402
from store.ingest import (FULL_READ_MARK, AssertionRecord, add_read, append_updated_reason,  # noqa: E402
                          checked_when_stored, insert_verified_assertion, set_tier, sync_verified_assertion, validate_assertion)
from store.merges import holder, promotes  # noqa: E402
from store.ocr import IMAGE_SUFFIXES  # noqa: E402
from store.quotes import (QUOTE, ocr_only_quotes, plain, read_from_figure, require_edit_basis, require_verbatim,  # noqa: E402
                          source_text)

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)
_spec = importlib.util.spec_from_file_location("review_additions", Path(__file__).with_name("review_additions.py"))
additions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(additions)

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
# F126: when and by which task a later sign-off corrected a confirmed stored assertion's anchor, "<date> (<task>)";
# without it the group's review day and tag are used.
ANCHOR_FIX_ON: dict[str, str] = {}
DROP: dict[str, str] = {}  # a new assertion not entered, with the reason
KEEP_STORED: dict[str, str] = {}  # a stored assertion kept against the reader's verdict, with why
REQUOTE: dict[str, str] = {}  # a confirmed stored assertion rebuilt from the reader's fuller quotes, with why
# The words a grade the team lead decided at Manual Validation carries in its reasons ("UPGRADED ... the team lead's
# decision at Sprint 8 Manual Validation (Q7)"; scripts/sprint15_mv_decisions.py); apply_changes keeps such a grade
TEAM_LEAD_GRADE = "the team lead's decision at"
NOT_IN_PAPER: dict[str, str] = {}  # the coordinator's decision on a stored claim the paper does not hold
VENDOR_DESCRIPTIONS: set[str] = set()
FIELD_STATEMENTS: set[str] = set()

THEORY_LOW: dict[str, str] = {}  # a theoretical result kept LOW, with its cause
MEASURED_DESPITE: dict[str, str] = {}  # a measured result whose words name a proof or a bound, with why
RESULT_TYPE_FIX: dict[str, str] = {}  # the coordinator's result type where it differs from the reader's
EXTENT_FIX: dict[str, list[str]] = {}  # record id -> [extent, detail]: the coordinator's reading of a read's extent
REENTER: dict[str, str] = {}  # record id -> why: a paper refused at an earlier read whose assertions now enter
REFUSED = re.compile(r"read (whole )?at first pass and NOT entered")
ID_FIX: dict[str, str] = {}  # a new assertion's id where the reader's suggestion is already another source's
# F142 part 2 (Sprint 17 Task C): group -> the review's "add" table, the assertions the coordinator's sign-off added
# to the read or split from one (`review_additions`); merged by load_groups, so the read file is never edited by hand.
ADD: dict[str, dict] = {}

# F114's groups (g043 on, Sprint 14 Task E, F117) were read in cloud sessions and entered in Sprint 14, so their
# review names its own tag and reader; a group without them is one of Task G's. "readers" overrides the reader for
# one record (a result whose commits do not record the model), and "tags" its tag (a paper Task F read locally in a
# group otherwise read in the cloud; review of 1cb63bb). "unread" leaves a record out of its group with why.
GROUP_TAG: dict[str, str] = {}
GROUP_READER: dict[str, str] = {}
RECORD_READER: dict[str, str] = {}
RECORD_TAG: dict[str, str] = {}
UNREAD: dict[str, dict[str, str]] = {}
# F137 (Sprint 16 Task E, team lead Q6 = 1, 2026-11-06): `store.merges` names each record closed as a duplicate and
# the record that holds its assertions now. A reader file that names the duplicate still reads as written (g131), and
# its assertions are entered, checked and owned under the holder; the duplicate itself is never promoted again.

REVIEWS_DIR = ROOT / "manifests" / "sprint13_g_reviews"
_TABLES = {"quote_edits": QUOTE_EDITS, "extra_quotes": EXTRA_QUOTES, "value_replace": VALUE_REPLACE,
           "context_fix": CONTEXT_FIX, "anchor_fix": ANCHOR_FIX, "drop": DROP, "keep_stored": KEEP_STORED,
           "requote": REQUOTE, "not_in_paper": NOT_IN_PAPER, "theory_low": THEORY_LOW,
           "measured_despite": MEASURED_DESPITE, "result_type_fix": RESULT_TYPE_FIX, "extent_fix": EXTENT_FIX,
           "id_fix": ID_FIX, "reenter": REENTER, "anchor_fix_on": ANCHOR_FIX_ON}
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
        if "tag" in review:
            GROUP_TAG[g] = review["tag"]
        if "reader" in review:
            GROUP_READER[g] = review["reader"]
        RECORD_READER.update(review.get("readers", {}))
        RECORD_TAG.update(review.get("tags", {}))
        if review.get("unread"):
            UNREAD[g] = review["unread"]
        if review.get("add"):
            ADD[g] = review["add"]
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


def tag(g: str, rid: str = "") -> str:
    return RECORD_TAG.get(rid) or GROUP_TAG.get(g, TAG)


def first_pass(g: str, rid: str) -> str:
    """Who read the paper whole: a cloud session (Task E's F114 results), else a subagent (Task G's, and Task F's
    local readers)."""
    return "cloud session" if "cloud read" in tag(g, rid) else "subagent"


def reader(g: str, rid: str) -> str:
    return RECORD_READER.get(rid) or GROUP_READER.get(g, SUBAGENT_READER)


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


# F125 (Sprint 15 Task C): a record a reviewed group left unread is read later in a re-entry group "<g>-r<n>", with its
# own group file and review file; a reviewed group's files are never rewritten. Its records are exactly the ones its
# predecessor's review left unread (g113-r1 takes what g113 left, g113-r2 what g113-r1 left), so no record is entered
# by two groups.
REENTRY = re.compile(r"^(g\d+)-r([1-9]\d*)$")


def group_records(g: str) -> set[str]:
    m = REENTRY.match(g)
    if not m:
        return {r["record_id"] for r in ledger()["groups"][g]["records"]}
    before = m[1] if m[2] == "1" else f"{m[1]}-r{int(m[2]) - 1}"
    if before not in REVIEWED_ON:
        raise ValueError(f"{g}: re-enters what {before} left unread, and {before} has no review")
    return set(UNREAD.get(before, {}))


def groups() -> list[str]:
    """The reviewed groups: those with a date in REVIEWED_ON, or ONLY's for a dry run."""
    names = ONLY or sorted(REVIEWED_ON)
    missing = [g for g in names if (REENTRY.match(g) or [None, g])[1] not in ledger()["groups"]]
    if missing:
        raise ValueError(f"not in the ledger: {missing}")
    return names


def load_groups() -> list[tuple[str, dict]]:
    """Every paper of the reviewed groups; refuses a reader file whose records are not its group's."""
    out = []
    for g in groups():
        papers = additions.merge(g, json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))["papers"],
                                 ADD.get(g, {}))
        want = group_records(g) - set(UNREAD.get(g, {}))
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
        if aid in HIGH:  # a signed HIGH would be written LOW without a word (review of de1efff)
            raise ValueError(f"{aid}: graded HIGH, but a vendor's own claim is LOW; correct the review")
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
    value = " ".join((VALUE_REPLACE.get(sid) or a.get("value") or "").split())
    if not value:  # a confirmed entry may carry no value; a requote would blank the stored one (review of de1efff)
        raise ValueError(f"{sid}: no value to write; give it a value_replace or leave it out of REQUOTE")
    return AssertionRecord(
        id=sid, value=value,
        provenance=f"{rid}, {anchor}",
        citation_context="; ".join(f'"{q}" ({anchor})' for q in quotes_of(sid, a)),
        evidence_tag="N/A", context=CONTEXT_FIX.get(sid) or a["context"], certainty=cert,
        certainty_reasons=reasons, fidelity=a.get("fidelity") or "scoped", derivation="extracted",
        claim_type=a["claim_type"],
        search_scope=("the paper's own text, as read" if a["claim_type"] == "absence" else None),
        updated=REVIEWED_ON.get(g, ""), updated_reason=(
            f"{REVIEWED_ON.get(g, '')} ({tag(g, rid)}): {FULL_READ_MARK}: {why} from {rid}; the paper read whole by a "
            f"first-pass {first_pass(g, rid)}, every quoted passage read in context "
            "by the coordinator"))


def assertions(problems: list[str] | None = None) -> list[tuple[str, AssertionRecord, str, dict]]:
    """(group, record, paper id, paper) for every new claim entered and every stored one changed. With `problems`,
    a record that is refused is named there and left out, so every refusal is found in one run (Sprint 14
    retrospective Q4); without it, the first refusal raises."""
    out = []

    def add(g, rid, p, *args):
        try:
            rec = record(g, rid, *args)
            if holder(rid) != rid:  # F137: owned, checked and yielded under the record it was merged into
                rec = replace(rec, provenance=f"{holder(rid)}{rec.provenance[len(rid):]}")
            out.append((g, rec, holder(rid), p))
        except ValueError as e:
            if problems is None:
                raise
            problems.append(str(e))

    for g, p in load_groups():
        rid = p["record_id"]
        for e in p.get("existing", []):
            aid = e["id"]
            if aid in KEEP_STORED or aid in NOT_IN_PAPER:
                continue
            if e["verdict"] in CHANGED or (e["verdict"] == "confirmed" and aid in REQUOTE):
                add(g, rid, p, aid, e, f"{e['verdict']} at a full read")
        for a in p.get("assertions", []):
            aid = a["id_suggestion"]
            if aid not in DROP:  # an assertion the sign-off added says so in its history (F142 part 2)
                how = "added at the coordinator's sign-off" if additions.MARK in a else "extracted at a full read"
                add(g, rid, p, aid, a, how, ID_FIX.get(aid, aid))
    return out


def decided_fields(aid: str, verdict: str | None) -> set[str]:
    """The fields of a stored assertion that a review item names (Sprint 14 retrospective Q2). An accepted changed
    verdict names the reader's whole entry and its grade, but not its context: the reader's context is its nearest
    fit, and only CONTEXT_FIX decides one."""
    named = set()
    if verdict in CHANGED:  # every synced column but the context (fresh-eyes review of 7b2179f: some were missing)
        named |= {"value", "provenance", "evidence_tag", "certainty", "certainty_reasons", "fidelity",
                  "reading_level", "units", "rounding", "citation_context", "derivation", "claim_type",
                  "search_scope", "documents", "supports", "contradicts"}
    if aid in REQUOTE:
        named |= {"provenance", "citation_context"}
        if REQUOTE[aid].startswith("regraded"):
            named |= {"certainty", "certainty_reasons"}
    if aid in VALUE_REPLACE:
        named.add("value")
    if aid in QUOTE_EDITS or aid in EXTRA_QUOTES:
        named.add("citation_context")
    if aid in ANCHOR_FIX:
        named |= {"provenance", "citation_context"}
    if aid in HIGH or aid in THEORY_LOW or aid in RESULT_TYPE_FIX:
        named |= {"certainty", "certainty_reasons"}
    if aid in CONTEXT_FIX:
        named.add("context")
    return named


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


def ocr_check(a, file: str, text: str | None) -> None:
    """F115 (Sprint 15 Task F). A quote found only in a source's OCR text says "OCR" in its anchor, so a reader of
    the record knows the words came from a page image. The team lead's grading rule (2026-11-01, plan Q3): OCR of a
    stored PDF's page grades as its text layer; a claim from an image file outside a PDF is HIGH only when another
    source corroborates it, named in its HIGH's why ("corroborated by <record>"), otherwise MEDIUM at most."""
    # The anchor runs to the ")" that ends the quote's entry, so an anchor holding "(Methods)" is read whole (review
    # of Task F: "[^)]*" stopped at the first ")").
    # text None (F136): the quotes are stored as written and were marked when checked; the grade rule still runs
    unmarked = [q for q in (ocr_only_quotes(a.citation_context, text) if text is not None else [])
                if not re.search(rf'"{re.escape(q)}" \((?:(?!\)(?:; "|$)).)*\bOCR\b', a.citation_context)]
    if unmarked:
        raise ValueError(f"{a.id}: quotes found only in OCR text need \"OCR\" in their anchor: {unmarked}")
    if (Path(file).suffix.lower() in IMAGE_SUFFIXES and a.certainty == "high"
            and not re.search(r"\bcorroborated by\b", a.certainty_reasons or "")):
        raise ValueError(f"{a.id}: a claim read from an image file is HIGH only when another source corroborates "
                         "it (\"corroborated by <record>\" in its why); otherwise MEDIUM at most")


def figure_ids(p: dict) -> set[str]:
    """The stored ids of a paper's assertions read from a figure (F116, Sprint 15 Task G)."""
    return ({ID_FIX.get(a["id_suggestion"], a["id_suggestion"]) for a in p.get("assertions", []) if a.get("from_figure")}
            | {e["id"] for e in p.get("existing", []) if e.get("from_figure")})


def figure_check(a) -> None:
    """F116 (Sprint 15 Task G): a value read by eye from a figure says so, and is never HIGH on the figure alone."""
    if not re.search(r"\bread from (figure|fig\.|table|the image)", a.value, re.I):
        raise ValueError(f'{a.id}: a value read from a figure says so ("Read from Figure N: ...")')
    if a.certainty == "high":
        raise ValueError(f"{a.id}: a value read from a figure is never HIGH on the figure alone")


LAST_VERIFY: Counter = Counter()  # F136: what the last verify() checked, and what it found stored as written


CHECKED_BY_GROUP: Counter = Counter()  # F139: per group, the assertions the last verify() checked (new or changed)


def record_telemetry(step: str) -> list[str]:
    """F139: the last verify's quote checks per group, as one step in each group's telemetry file
    (`scripts/read_telemetry.py`); a group without a file is not measured. At an apply the checked assertions are
    the ones it entered or whose quote or value it changed, so they are its assertions written too (its other rows,
    such as read rows and access notes, are not counted)."""
    spec = importlib.util.spec_from_file_location("read_telemetry", Path(__file__).with_name("read_telemetry.py"))
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    writes = step in ("trial", "apply")
    return [g for g, n in sorted(CHECKED_BY_GROUP.items())
            if t.step(g, step, quote_checks=n, **({"assertions_written": n} if writes else {})) is not None]


def verify_counts() -> str:
    return (f"quote checks: {LAST_VERIFY['checked']} checked, {LAST_VERIFY['stored as written']} stored as written "
            f"(checked when written, not again); {LAST_VERIFY['sources read']} sources read")


def _text(texts: dict[str, str], file: str) -> str:
    if file not in texts:  # once per file: setdefault built the argument, plain() over the whole text, every time
        texts[file] = plain(source_text(file))
    return texts[file]


def verify(conn=None) -> list[tuple[AssertionRecord, str, dict, object]]:
    """Every quote verbatim in its source, every coordinator edit resting on named passages, and every figure in
    a value in its own quotes, BEFORE anything is written. Every refusal is collected and raised together (Sprint 14
    retrospective Q4: a dry run named one, and each fix found the next).

    F136 (Sprint 16 Task A): with `conn`, an assertion whose quotes and value a full read of the same source
    already stored exactly as it would write them is not checked again (`checked_when_stored`): that write checked
    them, and a sync writes no quote or value for it. Only a new or changed quote is checked, so a second apply checks nothing and reads no
    source. The checks that read no source (the figure, image-HIGH and record rules) still run on every row."""
    texts: dict[str, str] = {}
    out = []
    problems: list[str] = []
    LAST_VERIFY.clear()
    CHECKED_BY_GROUP.clear()
    for g, a, rid, p in assertions(problems):
        try:
            from_figure = a.id in figure_ids(p)
            verified = checked_when_stored(conn, a, rid) if conn is not None else None
            CHECKED_BY_GROUP[g] += 0  # every group present, a group with nothing new as 0
            if verified is not None:
                LAST_VERIFY["stored as written"] += 1
                ocr_check(a, p["file"], None)
            else:
                LAST_VERIFY["checked"] += 1
                CHECKED_BY_GROUP[g] += 1
                quotes = QUOTE.findall(a.citation_context)
                text = _text(texts, p["file"])
                from_page = read_from_figure(a.value) if from_figure else ()
                verified = require_verbatim(a.id, a.citation_context, text, value=a.value, read_from_page=from_page)
                if a.id in VALUE_REPLACE:  # a figure reading's edited value keeps its figure exemption (Sprint 15 MV
                    require_edit_basis(a.id, a.value, quotes, text, read_from_page=from_page)  # apply: 5 refused)
                if a.id in QUOTE_EDITS:
                    require_edit_basis(a.id, None, [n for _, n in QUOTE_EDITS[a.id] if n] or quotes, text)
                ocr_check(a, p["file"], text)
            if from_figure:
                figure_check(a)
            validate_assertion(a)
        except ValueError as e:
            problems.append(str(e))
            continue
        out.append((a, rid, p, verified))
    LAST_VERIFY["sources read"] = len(texts)
    LAST_VERIFY["checked"] += 0  # present when 0, for the counts line and its tests
    if problems:
        raise ValueError(f"{len(problems)} refused:\n" + "\n".join(problems))
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
    if g in GROUP_TAG:
        detail += f" ({reader(g, p['record_id'])}, {tag(g, p['record_id'])}, group {g})"
    else:
        detail += f" (Sonnet 5.5 reader, {TAG}, group {g})"
    if p.get("version_note"):
        detail += f"; version: {p['version_note']}"
    return detail


def read_extent(p: dict) -> str:
    """Team lead, Sprint 13 Manual Validation Q7 = 2 (2026-10-28): a whole-paper read is stored as `full`, as F113's
    acceptance says, not `subagent` as in Sprints 11 and 12; the reader's name still says it was a subagent. A read
    with a named exception is `partial`."""
    extent, _ = EXTENT_FIX.get(p["record_id"], (p.get("read_extent"), ""))
    return "full" if extent == "full" else "partial"


def is_mine(name: str, detail: str) -> bool:
    """A paper_reads row this script wrote. Task F (F112) read 57 of these papers on 2026-10-25, a review day of
    Task G's, under the same reader names, and the first apply took Task F's rows for its own and rewrote their
    detail (full suite, 2026-10-27); a row is matched by its wording, never by reader, day and extent alone."""
    if name == "Claude":
        return detail.startswith(COORDINATOR_DETAIL[:40])
    return any(t in detail for t in {TAG, *GROUP_TAG.values(), *RECORD_TAG.values()})


def write_reads(conn, rid: str, day: str, detail: str, extent: str, first: str = SUBAGENT_READER) -> list[str]:
    """The first-pass read and the coordinator's, added or brought to this script's extent and wording; a row
    another script wrote under the same reader and day is left as it is."""
    log = []
    have = {(r[0], r[1]): (r[2], r[3]) for r in conn.execute(
        "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,)) if is_mine(r[0], r[3])}
    for name, ext, det in ((first, extent, detail), ("Claude", "partial", COORDINATOR_DETAIL)):
        old = have.get((name, day))
        if old is None:
            add_read(conn, rid, name, day, ext, det)
            log.append(f"read   {rid} [{name}, {ext}]")
        elif old != (ext, det):
            conn.execute("UPDATE paper_reads SET extent = ?, detail = ? WHERE record_id = ? AND reader = ? "
                         "AND read_on = ? AND extent = ? AND detail = ?", (ext, det, rid, name, day, *old))
            log.append(f"update read {rid} [{name}, {old[0]} to {ext}]")
    return log


def refused_without_reversal(conn, p: dict) -> bool:
    """A paper an earlier read refused would get a new assertion, and its review names no reversal in REENTER
    (review of b185729: 10 refused papers entered because a later reader chose a context)."""
    rid = p["record_id"]
    if rid in REENTER:
        return False
    row = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()
    if not (row and standing_refusal(row[0] or "")):
        return False
    new = [ID_FIX.get(a["id_suggestion"], a["id_suggestion"]) for a in p.get("assertions", [])
           if a["id_suggestion"] not in DROP]
    return any(not conn.execute("SELECT 1 FROM records WHERE id = ?", (i,)).fetchone() for i in new)


REVERSED = re.compile(r"\brefusal\b.*\bno longer applies\b")


def standing_refusal(reason: str) -> bool:
    """A refusal in the record's history that no later note reverses (F127, from the review of 4d969d9: 9 QCI Dirac
    papers carry Sprint 9's refusal, which Sprint 10 reversed with "... refusal ... no longer applies")."""
    notes = reason.split(" | ")
    # a reversal that quotes the refusal's words is not itself a refusal (review of the uncommitted D and E)
    refusals = [i for i, n in enumerate(notes) if REFUSED.search(n) and not REVERSED.search(n)]
    return bool(refusals) and not any(REVERSED.search(n) for n in notes[refusals[-1] + 1:])


def same_source(rid: str, provenance: str) -> bool:
    """The provenance names this record as a whole token: not the start of a longer record id, and not one that goes
    on with a dot ("v-2" in "v-2.5"), though a sentence may end after it (F127; as f117_build_groups.same_source).
    Case is ignored, as the SQL LIKE it replaces ignored it."""
    return re.search(rf"(?<![\w-]){re.escape(rid)}(?![\w-]|\.\w)", provenance, re.I) is not None


def held_by_another(conn, aid: str, owner: str) -> bool:
    """A stored assertion `aid` whose provenance does not name `owner` (F127, from the review of cecf20d: the check
    was NOT LIKE %owner%, a substring test)."""
    row = conn.execute("SELECT r.provenance FROM records r JOIN assertion_fields f ON f.record_id = r.id "
                       "WHERE r.id = ?", (aid,)).fetchone()
    return row is not None and not same_source(owner, row[0] or "")


def refusal_reason(p: dict) -> str:
    """Why a paper with nothing entered was not entered. A sign-off drop wins over the reader's `why_not`, which may
    say where its assertions were to be entered (review of 4d969d9: 6 notes said "entered under qc")."""
    dropped = [DROP[a["id_suggestion"]] for a in p.get("assertions", []) if a["id_suggestion"] in DROP]
    return "; ".join(dict.fromkeys(dropped)) if dropped else p.get("why_not") or ""


def anchor_moves(conn) -> list[tuple[AssertionRecord, object]]:
    """F126 (Sprint 15 Task D): an ANCHOR_FIX on a confirmed stored assertion that nothing rebuilds (not in REQUOTE)
    was never written; g104's review found muta-hardware-scope-photonic-gkp's passage on PDF p.8, stored as p.9, and
    the reader's entry held no quotes to rebuild from. Such an assertion is rebuilt from its stored row with only its
    anchor changed, each stored quote checked against the source again; a grade the review gives it is written, as
    for any assertion the review grades, and otherwise the stored grade is kept."""
    out = []
    for g, p in load_groups():
        rid = p["record_id"]
        for e in p.get("existing", []):
            aid = e["id"]
            if (aid not in ANCHOR_FIX or e["verdict"] in CHANGED or aid in REQUOTE or aid in KEEP_STORED
                    or aid in NOT_IN_PAPER):
                continue
            row = conn.execute(
                "SELECT r.value, r.evidence_tag, r.certainty, r.certainty_reasons, r.fidelity, r.reading_level, "
                "f.units, f.rounding, f.citation_context, f.derivation, f.claim_type, f.search_scope FROM records r "
                "JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (aid,)).fetchone()
            if row is None:
                raise ValueError(f"{aid}: anchor_fix on a stored assertion the store does not hold")
            value, tag_, cert, reasons, fidelity, level, units, rounding, cc, derivation, claim_type, scope = row
            quotes = QUOTE.findall(cc or "")
            if not quotes:
                raise ValueError(f"{aid}: no stored quote to carry the corrected anchor")
            # one anchor for every quote: quotes from different places are not collapsed onto one (review of the
            # uncommitted D and E); such an assertion is rebuilt through REQUOTE instead
            # each anchor read whole, as ocr_check reads it: "[^)]*" stopped at an inner ")" and missed the anchor
            # "Section 2 (Methods), p.3" (fresh-eyes review, 2026-11-02)
            anchors = set(re.findall(r'" \(((?:(?!\)(?:; "|$)).)*)\)(?=; "|$)', cc))
            if len(anchors) > 1:
                raise ValueError(f"{aid}: its stored quotes carry {len(anchors)} anchors; correct it through REQUOTE")
            if aid in HIGH or aid in THEORY_LOW:
                cert, reasons = (grade(aid, HIGH, otherwise=low_grade("authors' claim")) if aid in HIGH
                                 else low_grade("theoretical result", THEORY_LOW[aid]))
            contexts = [r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                                   (aid,))]
            if not contexts:
                raise ValueError(f"{aid}: no stored context to keep")
            anchor = anchor_safe(ANCHOR_FIX[aid])
            when = ANCHOR_FIX_ON.get(aid) or f"{REVIEWED_ON.get(g, '')} ({tag(g, rid)})"
            day = when[:10]
            a = AssertionRecord(
                id=aid, value=value, provenance=f"{holder(rid)}, {anchor}",  # F137: the holding record
                citation_context="; ".join(f'"{q}" ({anchor})' for q in quotes), evidence_tag=tag_,
                context=contexts[0], units=units, rounding=rounding, certainty=cert,
                certainty_reasons=reasons, fidelity=fidelity, reading_level=level, derivation=derivation,
                claim_type=claim_type, search_scope=scope, updated=day,
                updated_reason=f"{when}: {FULL_READ_MARK}: anchor corrected at the sign-off to "
                               f"{anchor}; the stored quotes checked against the source again")
            # F136: an anchor already stored as corrected is not checked again (a sync then changes nothing)
            out.append((a, checked_when_stored(conn, a, holder(rid))
                        or require_verbatim(aid, a.citation_context, plain(source_text(p["file"])), value=value)))
    return out


def write_anchor_moves(conn) -> list[str]:
    log = []
    for a, verified in anchor_moves(conn):
        changed = sync_verified_assertion(conn, a, verified, a.updated_reason, a.updated)
        # sync's date guard writes nothing when the row changed after the fix's day; the dry run listed the move, so
        # a skip is said, not dropped (fresh-eyes review, 2026-11-02)
        stored = conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?", (a.id,)).fetchone()
        if not changed and stored[0] != a.citation_context:
            raise ValueError(f"{a.id}: anchor not written: the stored row changed after {a.updated}; date the fix in "
                             "ANCHOR_FIX_ON or rebuild it through REQUOTE")
        if changed:
            log.append(f"anchor {a.id} [{', '.join(changed)}]")
            undecided = [c for c in changed if c not in decided_fields(a.id, "confirmed")]
            if undecided:
                log.append(f"undecided {a.id} [{', '.join(undecided)}]")
    return log


def apply_changes(conn) -> list[str]:
    checked = verify(conn)
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    for g, p in load_groups():
        rid, detail, day = p["record_id"], read_detail(g, p), REVIEWED_ON[g]
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        if refused_without_reversal(conn, p):
            raise ValueError(f"{rid}: refused at an earlier read; drop its assertions or name the reversal in reenter")
        path = p["file"].replace("/", "\\")
        if path.lower() not in {s.lower() for s in recheck.local_paths(access or "")}:
            note = f"Local copy {f80._sha(Path(path))}, recorded {day} ({tag(g, rid)})"
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ? WHERE record_id = ?",
                         (f"{access} | {path}" if access else path,
                          f"{evidence.rstrip().rstrip('.')}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{day} ({tag(g, rid)}): local copy added to access", day)
            log.append(f"access {rid}")
        for aid, why in NOT_IN_PAPER.items():
            if any(e["id"] == aid for e in p.get("existing", [])):
                note = f"{day} ({tag(g, rid)}): {FULL_READ_MARK}: NOT in the paper at a full read: {why}"
                stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (aid,)).fetchone()[0] or ""
                if note not in stored:
                    append_updated_reason(conn, aid, note, day)
                    log.append(f"not in paper {aid}")
        kept = [a for a in p.get("assertions", []) if a["id_suggestion"] not in DROP]
        entered = kept or [e for e in p.get("existing", []) if e["id"] not in NOT_IN_PAPER]
        log += write_reads(conn, rid, day, detail, read_extent(p), reader(g, rid))
        if not entered:
            why = refusal_reason(p)
            note = f"{day} ({tag(g, rid)}): read whole at first pass and NOT entered: {why}"
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
        if promotes(rid, tier):
            set_tier(conn, rid, "read", checked_against_source=(
                f"{day}, Claude, read every quoted passage in context and checked every quote and figure against "
                f"the source; the paper read whole at first pass by a {first_pass(g, rid)}"))
            log.append(f"tier   {rid} -> read")
    for a, rid, p, verified in checked:
        if a.context not in contexts:
            raise ValueError(f"{a.id}: context {a.context!r} is not a context")
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        stored = [r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))]
        if a.id not in CONTEXT_FIX and stored and a.context not in stored:
            # The reader's context is its nearest fit; a stored one was set by an earlier intake and is changed only
            # by the sign-off (Sprint 14 suite after the 2026-10-31 apply: platform:dirac-3 was replaced by qc).
            a = replace(a, context=stored[0])
        verdict = next((e["verdict"] for e in p.get("existing", []) if e["id"] == a.id), None)
        if verdict == "confirmed":
            # A confirmed entry rebuilt for its quotes or its grade (REQUOTE) changes only what its review names; the
            # reader's fidelity and claim type are suggestions no item decides (Sprint 15 Manual Validation trial:
            # six regraded rows went from "scoped" to "exact", three from "absence" to "positive")
            fid, ctype, scope = conn.execute(
                "SELECT r.fidelity, f.claim_type, f.search_scope FROM records r JOIN assertion_fields f "
                "ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
            a = replace(a, fidelity=fid, claim_type=ctype, search_scope=scope)
            if ctype == "vendor-self-claim" and a.certainty == "high":  # graded on the reader's claim type (review)
                raise ValueError(f"{a.id}: a vendor's own claim is LOW (store.grading); its review graded it HIGH")
        held, held_why = conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?",
                                      (a.id,)).fetchone()
        if TEAM_LEAD_GRADE in (held_why or "") and TEAM_LEAD_GRADE not in (a.certainty_reasons or ""):
            # A grade the team lead decided after the review stands until a review records a decision of its own; a
            # rerun's date alone must not decide it (fresh-eyes review of the Sprint 15 Manual Validation apply)
            a = replace(a, certainty=held, certainty_reasons=held_why)
        changed = sync_verified_assertion(conn, a, verified, a.updated_reason, a.updated)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
        undecided = [c for c in changed if c not in decided_fields(a.id, verdict)]
        if undecided:
            log.append(f"undecided {a.id} [{', '.join(undecided)}]")
    return log + write_anchor_moves(conn)


class ReadRowsRewritten(Exception):
    pass


def commit_apply(conn, update_reads: bool) -> list[str]:
    """Sprint 13 retrospective I1 (team lead, 2026-10-28): the g001 to g042 trial log showed 114 'update read' lines
    where only new reads were expected, nobody asked why, and the real apply rewrote Task F's rows. A rewritten read
    row is now a stop: the apply is rolled back unless the run names the rewrite as intended."""
    log = apply_changes(conn)
    rewrites = [x for x in log if x.split()[:2] == ["update", "read"]]  # not "update readout-..." (an assertion)
    if rewrites and not update_reads:
        conn.rollback()
        raise ReadRowsRewritten(f"{len(rewrites)} read rows would be rewritten; nothing written. Each must be intended; "
                         "if so, re-run with --update-reads:\n" + "\n".join(rewrites))
    conn.commit()
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--groups" in args:
        if "--apply" in args:
            print("--groups is for a dry run; an apply enters every reviewed group")
            return 1
        ONLY[:] = args[args.index("--groups") + 1].split(",")
    refused: list[str] = []
    kept = assertions(refused)
    ids = [a.id for _, a, _, _ in kept]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    owner = {a.id: rid for _, a, rid, _ in kept}
    with connect(DB_PATH) as conn:
        clash = [i for i in ids if held_by_another(conn, i, owner[i])]
        unwritten = grades_not_written(conn)
        try:  # F126: the anchor moves' quotes are checked at the dry run too
            moves = [a.id for a, _ in anchor_moves(conn)]
        except ValueError as e:
            moves, unwritten = [], unwritten + [str(e)]
    if "--apply" not in args:
        try:  # the quote checks too, so a dry run names every refusal at once (Q4); verify names assertions' own
            with connect(DB_PATH) as conn:  # F136: the rows stored as written are not checked again
                verify(conn)
            refused = []
        except ValueError as e:
            refused = [str(e)]
    if dupes or clash or unwritten or refused:
        print(f"duplicate assertion ids: {dupes}; ids already held by another source: {clash}")
        print("\n".join(unwritten + refused))
        return 1
    if "--apply" not in args:
        papers = load_groups()
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"anchor fixes on confirmed stored assertions: {moves}")
        print(verify_counts())
        if "--telemetry" in args:
            print(f"telemetry: dry run recorded for {record_telemetry('dry run')}")
        print(f"{len(kept)} assertions entered or changed from {len(papers)} records. Every quote verbatim, every "
              "edit on named passages, every figure in its quotes. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, f"{' and '.join(sorted({TAG, *GROUP_TAG.values(), *RECORD_TAG.values()}))} "
                                 "full reads entered")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = commit_apply(conn, "--update-reads" in args)
    except ReadRowsRewritten as e:
        print(e)
        return 1
    finally:
        conn.close()
    print("\n".join(log))
    undecided = [x for x in log if x.startswith("undecided ")]
    print(f"{len(undecided)} stored assertions with a field changed that no review item names"
          f"{'; read each before the live apply' if undecided else ''}")
    print(verify_counts())
    if "--telemetry" in args:  # a store other than the live one is a trial on a copy
        step = "apply" if Path(DB_PATH).resolve() == (Path(DEFAULT_STORE_DIR) / "evidence.db").resolve() else "trial"
        print(f"telemetry: {step} recorded for {record_telemetry(step)}")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
