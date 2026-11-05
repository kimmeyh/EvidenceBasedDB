#!/usr/bin/env python3
"""Sprint 14 Task E (F117): each F114 group's review, from the items a reviewer must decide to the applier's review
file (`manifests/sprint13_g_reviews/<g>.json`, as Task G's were).

`items <g>` writes WORK/review/items/<g>.json: every decision the group needs, one item each, with what the reviewer
reads to make it (record, anchor, value, quotes, the reader's suggestion and reason):
  - "new-high": a new assertion the reader suggested HIGH: "high" with a basis and why, or "low" with why;
  - "new-theory": a new theoretical result the reader did not suggest HIGH: "low" with its cause, or "high";
  - "changed": a stored assertion the reader corrected, narrowed, widened or contradicted: "accept" or "keep" with
    why, and the grade of the accepted value ("high" with basis and why, or "low" with why);
  - "stored-high": a stored HIGH the reader confirmed: "high" with basis and why, or "low" with why.
The Sonnet 5.5 reviewer writes WORK/review/decisions/<g>.json: {"<item id>": {"decision": ..., "basis": ...,
"why": ..., "grade": ...}}.

`finalize <g> <reviewed_on>` turns the decisions into the review file, refusing a missing or malformed decision. A
stored assertion whose grade the decisions would change (HIGH to LOW, or LOW to HIGH) is a certainty change, which
the team lead decides (F117's card): it is listed in WORK/review/escalations/<g>.pending.json and the group is not
finalized until the decision is recorded in WORK/review/escalations/<g>.json as {"<id>": "low" | ["low", why] |
["high", basis, why]}; a LOW against the reviewer's HIGH names its own cause. Any stored certainty counts, MODERATE
included; a vendor's own claim is never HIGH. Finalize refuses a sign-off edit the applier would ignore or could not
enter.

Finalize reads stored grades from the live store, so it refuses a group already applied there: the stored grades
would be the applied ones. `--store <path>` names the store to read instead, a copy of the backup taken before the
apply (Sprint 14 retrospective Q3: g079 and g094 were re-finalized that way by hand, with EBDB_STORE_DIR).
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402
from store.grading import BASES  # noqa: E402
from store.ingest import FULL_READ_MARK  # noqa: E402

_spec = importlib.util.spec_from_file_location("f117_build_groups", ROOT / "scripts" / "f117_build_groups.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)

_, DB_PATH, _ = script_paths(__file__)
REVIEW = build.cloud.WORK / "review"
READS_DIR = build.READS_DIR
REVIEWS_DIR = ROOT / "manifests" / "sprint13_g_reviews"
TAG = "Sprint 14 Task E, F117 (F114 cloud read)"
READER = "Claude Sonnet 5.5 (F114 cloud session)"
LOCAL_TAG = "Sprint 14 Task F, F114 (local read)"
LOCAL_READER = "Claude Sonnet 5.5 (F114 local reader, manifests/sprint14_f114_reads/READER_PROMPT.md)"
S15_TAG = "Sprint 15 Task H, F114 (local read)"
S15_READER = "Claude Sonnet 5.5 (F114 local reader, manifests/sprint15_f114_reads/READER_PROMPT.md)"
UNRECORDED = "Claude (F114 cloud session; the model is not in the result's commits, the launcher's default was Sonnet)"
CHANGED = {"corrected", "narrowed", "widened", "contradicted"}


def stored_certainty(ids: list[str]) -> dict[str, str]:
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        return {i: (row[0] if row else "") for i in ids
                for row in [conn.execute("SELECT certainty FROM records WHERE id = ?", (i,)).fetchone()]}
    finally:
        conn.close()


def stored_text(ids: list[str]) -> dict[str, tuple[str, str]]:
    """(value, citation_context) as stored: a confirmed entry may carry no value of its own (g043's pilot found two
    such stored-high items blank), so the reviewer reads the stored assertion itself."""
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        return {r[0]: (r[1], r[2] or "") for r in conn.execute(
            "SELECT r.id, r.value, f.citation_context FROM records r LEFT JOIN assertion_fields f ON f.record_id = r.id "
            f"WHERE r.id IN ({','.join('?' * len(ids))})", ids)}
    finally:
        conn.close()


def papers(g: str) -> list[dict]:
    return json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))["papers"]


def applied(g: str) -> list[str]:
    """The ids that show the group already applied on the store at DB_PATH: a new assertion that exists there, or a
    stored one whose history holds the applier's full-read note from its paper. A paper read whole twice can show here
    with no apply of this group; `--store` then names the store to read."""
    ps = papers(g)
    # Under the id the applier enters it (the sign-off's id_fix), and never a dropped one (review of 7b2179f).
    so = REVIEW / "signoff" / f"{g}.json"
    edits = json.loads(so.read_text(encoding="utf-8")) if so.exists() else {}
    id_fix, drop = edits.get("id_fix", {}), edits.get("drop", {})
    new = [id_fix.get(a["id_suggestion"], a["id_suggestion"]) for p in ps for a in p.get("assertions", [])
           if a["id_suggestion"] not in drop]
    old = {x["id"]: p["record_id"] for p in ps for x in p.get("existing", [])}
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        hits = [i for i in new if conn.execute("SELECT 1 FROM records WHERE id = ?", (i,)).fetchone()]
        for i, rid in old.items():
            row = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (i,)).fetchone()
            if row and f"{FULL_READ_MARK}: " in (row[0] or "") and f" from {rid}; " in row[0]:
                hits.append(i)
    finally:
        conn.close()
    return hits


def _show(rid: str, a: dict, aid: str) -> dict:
    return {"id": aid, "record": rid, "anchor": a.get("anchor"), "value": a.get("value"), "quotes": a.get("quotes"),
            "result_type": a.get("result_type"), "claim_type": a.get("claim_type"),
            "suggested": a.get("certainty_suggestion"),
            "suggested_basis": a.get("high_basis"), "reader_reason": a.get("certainty_reason")}


def items(g: str, stored: dict[str, str] | None = None,
          text: dict[str, tuple[str, str]] | None = None) -> list[dict]:
    ps = papers(g)
    ids = [x["id"] for p in ps for x in p.get("existing", [])]
    if stored is None:
        stored = stored_certainty(ids)
    if text is None:
        text = stored_text(ids) if ids else {}
    out = []
    for p in ps:
        rid = p["record_id"]
        for a in p.get("assertions", []):
            if a.get("certainty_suggestion") == "high":
                out.append({"kind": "new-high", **_show(rid, a, a["id_suggestion"])})
            elif a.get("result_type") == "theoretical":
                out.append({"kind": "new-theory", **_show(rid, a, a["id_suggestion"])})
        for x in p.get("existing", []):
            was_value, was_quotes = text.get(x["id"], ("", ""))
            shown = {"stored_value": was_value, "stored_quotes": was_quotes}
            if x["verdict"] in CHANGED:
                out.append({"kind": "changed", "verdict": x["verdict"], "reader_note": x.get("note"),
                            "stored": stored.get(x["id"]), **_show(rid, x, x["id"]), **shown})
            elif x["verdict"] == "confirmed" and stored.get(x["id"]) == "high":
                out.append({"kind": "stored-high", "stored": "high", **_show(rid, x, x["id"]), **shown})
    return out


def _grade(item: dict, d: dict) -> tuple[str, str, str]:
    """(grade, basis, why) from a decision, refused unless well formed."""
    grade = d.get("grade") if item["kind"] == "changed" else d.get("decision")
    if grade not in ("high", "low"):
        raise ValueError(f"{item['id']}: grade must be high or low, not {grade!r}")
    why = (d.get("why") or "").strip()
    if not why:
        raise ValueError(f"{item['id']}: every decision names why")
    basis = d.get("basis") or ""
    if grade == "high" and basis not in BASES:
        raise ValueError(f"{item['id']}: a HIGH names a basis in {sorted(BASES)}, not {basis!r}")
    if grade == "high" and item.get("claim_type") == "vendor-self-claim":  # the applier writes it LOW (review of de1efff)
        raise ValueError(f"{item['id']}: a vendor's own claim is LOW (store.grading); decide it low with why")
    return grade, basis, why


def _settled(aid: str, v) -> tuple[str, str, str]:
    """The team lead's decision on an escalation: "low", ["low", why], or ["high", basis, why] (review of 46d088d: a
    bare "high" could not name its basis, and a mistyped value was taken without a word; review of aabdd49: a LOW
    settled against a HIGH proposal names its own cause)."""
    if v == "low":
        return "low", "", ""
    if isinstance(v, list) and len(v) == 2 and v[0] == "low" and str(v[1]).strip():
        return "low", "", v[1]
    if isinstance(v, list) and len(v) == 3 and v[0] == "high" and v[1] in BASES and str(v[2]).strip():
        return "high", v[1], v[2]
    raise ValueError(f"{aid}: a settled decision is \"low\", [\"low\", why] or [\"high\", basis, why], not {v!r}")


def finalize(g: str, reviewed_on: str, stored: dict[str, str] | None = None) -> dict:
    its = items(g, stored)
    decisions = json.loads((REVIEW / "decisions" / f"{g}.json").read_text(encoding="utf-8"))
    missing = [i["id"] for i in its if i["id"] not in decisions]
    if missing:
        raise ValueError(f"{g}: no decision for {missing}")
    stray = sorted(set(decisions) - {i["id"] for i in its})
    if stray:
        raise ValueError(f"{g}: decisions for no item: {stray}")
    esc_path = REVIEW / "escalations" / f"{g}.json"
    settled = json.loads(esc_path.read_text(encoding="utf-8")) if esc_path.exists() else {}
    stray = sorted(set(settled) - {i["id"] for i in its})
    if stray:
        raise ValueError(f"{g}: settled decisions for no item: {stray}")
    review = {"group": g, "reviewed_on": reviewed_on, "tag": TAG, "reader": READER, "coordinator_note": "",
              "graded_high": {}, "theory_low": {}, "keep_stored": {}, "requote": {}}
    escalate = {}
    for item in its:
        d = decisions[item["id"]]
        if item["kind"] == "changed":
            if d.get("decision") == "keep":
                if not (d.get("why") or "").strip():
                    raise ValueError(f"{item['id']}: a stored assertion kept against the reader names why")
                review["keep_stored"][item["id"]] = d["why"]
                continue
            if d.get("decision") != "accept":
                raise ValueError(f"{item['id']}: a changed verdict is accept or keep")
        grade, basis, why = _grade(item, d)
        # Any stored certainty the applier would overwrite, MODERATE included (review of 46d088d: only HIGH and LOW
        # were checked); a stored NULL has no grade to override and is not escalated.
        was = (item.get("stored") or "").lower()
        if was and grade != was:
            if item["id"] not in settled:
                escalate[item["id"]] = {"record": item["record"], "stored": was, "proposed": grade, "why": why,
                                        "value": item["value"], "anchor": item["anchor"]}
                continue
            proposed = grade
            grade, s_basis, s_why = _settled(item["id"], settled[item["id"]])
            if grade == "high":
                if item.get("claim_type") == "vendor-self-claim":  # the applier refuses it (review of aabdd49)
                    raise ValueError(f"{item['id']}: settled HIGH, but a vendor's own claim is LOW (store.grading)")
                basis, why = s_basis, f"kept HIGH at the team lead's decision: {s_why}"
            elif s_why:
                why = s_why
            elif proposed == "high":  # the reviewer's why argues for HIGH and is no cause of a LOW (review of aabdd49)
                raise ValueError(f"{item['id']}: a LOW settled against a HIGH proposal names its cause: "
                                 "[\"low\", why]")
        if grade == "high":
            review["graded_high"][item["id"]] = [basis, why]
        elif item["result_type"] == "theoretical":
            review["theory_low"][item["id"]] = why
        if item["kind"] == "stored-high" and grade == "low":
            review["requote"][item["id"]] = f"regraded LOW at the team lead's decision: {why}"
    if escalate:
        esc_path.parent.mkdir(parents=True, exist_ok=True)
        (REVIEW / "escalations" / f"{g}.pending.json").write_text(json.dumps(escalate, indent=1, ensure_ascii=False),
                                                                    encoding="utf-8")
        raise ValueError(f"{g}: {len(escalate)} certainty changes wait for the team lead "
                         f"(escalations/{g}.pending.json)")
    held = {p["record_id"] for p in papers(g)}
    # F125 (Sprint 15 Task C): a re-entry group has no ledger entry; what it leaves unread is its brief's own "unread",
    # not its records' parent mark (NEXT_RELEASE) (review of 34034bd: a record that stayed unread could not be named).
    if build.REENTRY.match(g):
        unread = build.reentry_briefs()[g][1]
    else:
        ledger = {r["record_id"] for r in
                  json.loads(build.cloud.LEDGER.read_text(encoding="utf-8"))["groups"][g]["records"]}
        unread = {r: why for r, why in build.UNREAD.items() if r in ledger and r not in held}
    if unread:
        review["unread"] = unread
    local = {r for r in held if build.local_file(r)}
    # Sprint 15 Task H: a read under Sprint 15's prompt carries figure_count (its check requires it); it names that
    # sprint's prompt, not Sprint 14's (g062-r1 was first finalized as a Sprint 14 read)
    s15 = {p["record_id"] for p in papers(g) if "figure_count" in p}
    tag_of = {r: (S15_TAG, S15_READER) if r in s15 else (LOCAL_TAG, LOCAL_READER) for r in local}
    whole = local and local == held and len(set(tag_of.values())) == 1  # read wholly by one sprint's local readers
    if whole:
        review["tag"], review["reader"] = next(iter(tag_of.values()))
    readers = {r: UNRECORDED for r in held if r in UNRECORDED_MODEL and r not in local}
    if local and not whole:  # a mixed group: each local read names its own reader and tag (review of 1cb63bb)
        readers.update({r: tag_of[r][1] for r in local})
        review["tags"] = {r: tag_of[r][0] for r in sorted(local)}
    if readers:
        review["readers"] = readers
    own_requotes = set(review["requote"])
    ps = papers(g)
    _merge_signoff(g, review, ps=ps)
    _check_written(g, review, ps, own_requotes, stored)
    return review


# The coordinator's sign-off edits, in the applier's own tables, kept per group in WORK/review/signoff/<g>.json so a
# re-finalize writes them again instead of losing them. theory_low is here for a requoted theoretical stored LOW,
# which is no item (review of aabdd49).
SIGNOFF_TABLES = {"value_replace", "extra_quotes", "quote_edits", "anchor_fix", "context_fix", "requote", "drop",
                  "result_type_fix", "theory_low", "reenter"}  # reenter: record id -> why (review of b185729)
EDIT_TABLES = ("value_replace", "extra_quotes", "quote_edits", "anchor_fix", "context_fix", "result_type_fix")


def _check_written(g: str, review: dict, ps: list[dict], own_requotes: set[str],
                   stored: dict[str, str] | None) -> None:
    """Refuse what the applier would ignore without a word or could not enter (review of aabdd49): an edit on an id
    it does not write, a drop of a stored id, a requote of an entry it does not rebuild, a sign-off requote that
    changes a stored certainty nobody decided, and a rewritten entry with no value."""
    new = {a["id_suggestion"]: a for p in ps for a in p.get("assertions", [])}
    old = {x["id"]: x for p in ps for x in p.get("existing", [])}
    keep = set(review.get("keep_stored", {}))
    problems = [f"drop {i}: not a new assertion" for i in review.get("drop", {}) if i not in new]
    for i in review["requote"]:
        x = old.get(i)
        if x is None or x["verdict"] != "confirmed" or i in keep:
            problems.append(f"requote {i}: not a confirmed stored entry the applier rebuilds")
    written = ({i for i in new if i not in review.get("drop", {})}
               | {i for i, x in old.items() if i not in keep and (x["verdict"] in CHANGED or i in review["requote"])})
    for table in EDIT_TABLES:
        problems += [f"{table} {i}: an id the applier does not write" for i in review.get(table, {}) if i not in written]
    signed = [i for i in review["requote"] if i not in own_requotes and i in old]
    if signed and stored is None:
        stored = stored_certainty(signed)
    for i in signed:
        will = "high" if i in review["graded_high"] else "low"
        was = (stored.get(i) or "").lower()
        if was and was != will:
            problems.append(f"requote {i}: rewrites stored {was} as {will}; decide its grade as an item, not a "
                            "sign-off")
    for i in written:
        a = new.get(i) or old[i]
        if not " ".join((review.get("value_replace", {}).get(i) or a.get("value") or "").split()):
            problems.append(f"{i}: written with no value; give it a value_replace")
    if problems:
        raise ValueError(f"{g}: " + "; ".join(sorted(problems)))


def _merge_signoff(g: str, review: dict, ps: list[dict]) -> None:
    path = REVIEW / "signoff" / f"{g}.json"
    if not path.exists():
        return
    edits = json.loads(path.read_text(encoding="utf-8"))
    unknown = sorted(set(edits) - SIGNOFF_TABLES)
    if unknown:
        raise ValueError(f"{g}: sign-off tables the applier does not read: {unknown}")
    ids = {a["id_suggestion"] for p in ps for a in p.get("assertions", [])} | {
        x["id"] for p in ps for x in p.get("existing", [])}
    records = {p["record_id"] for p in ps}
    for table, entries in edits.items():
        stray = sorted(set(entries) - (records if table == "reenter" else ids))
        if stray:
            raise ValueError(f"{g}: sign-off {table} names ids not in the group: {stray}")
        clash = sorted(set(entries) & set(review.get(table, {})))
        if clash:
            raise ValueError(f"{g}: sign-off {table} names ids the review already holds: {clash}")
        review.setdefault(table, {}).update(entries)


# The 15 results whose commits carry no Co-Authored-By trailer (checked 2026-10-30); filled by `models`.
UNRECORDED_MODEL: set[str] = set()


def main(argv: list[str]) -> int:
    global UNRECORDED_MODEL, DB_PATH
    argv = list(argv)
    store = None
    if "--store" in argv:
        k = argv.index("--store")
        if k + 1 >= len(argv) or not Path(argv[k + 1]).is_file():
            raise SystemExit("--store names an existing store file")
        store = Path(argv[k + 1]).resolve()
        del argv[k:k + 2]
    models = REVIEW / "models.json"
    if models.exists():
        UNRECORDED_MODEL = {r for r, m in json.loads(models.read_text(encoding="utf-8")).items() if not m}
    cmd, g = argv[0], argv[1]
    if cmd == "items":
        out = REVIEW / "items" / f"{g}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        its = items(g)
        out.write_text(json.dumps(its, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{g}: {len(its)} items -> {out}")
    elif cmd == "finalize":
        if not models.exists():  # without it the 15 results with no recorded model take the cloud reader's name
            raise SystemExit(f"{models} is missing; finalize names each result's reader from it")
        if store is not None:
            DB_PATH = store
        else:
            hits = applied(g)
            if hits:
                raise SystemExit(f"{g} is already applied on {DB_PATH} ({', '.join(hits[:3])}"
                                 f"{', ...' if len(hits) > 3 else ''}), so its stored grades are the applied ones. "
                                 "Finalize against a copy of the backup taken before the apply: --store <path>")
        review = finalize(g, argv[2])
        path = REVIEWS_DIR / f"{g}.json"
        if path.exists():
            raise SystemExit(f"{path} exists; a signed review is never overwritten")
        path.write_text(json.dumps(review, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{g}: {len(review['graded_high'])} HIGH, {len(review['theory_low'])} theoretical LOW, "
              f"{len(review['keep_stored'])} kept stored -> {path}")
    else:
        raise SystemExit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
