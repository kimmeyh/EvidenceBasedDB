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
the team lead decides (F117's card): it is listed in WORK/review/escalations/<g>.json and the group is not finalized
until the decision is recorded there as {"<id>": "high" | "low"}.
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


def _show(rid: str, a: dict, aid: str) -> dict:
    return {"id": aid, "record": rid, "anchor": a.get("anchor"), "value": a.get("value"), "quotes": a.get("quotes"),
            "result_type": a.get("result_type"), "suggested": a.get("certainty_suggestion"),
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
    return grade, basis, why


def finalize(g: str, reviewed_on: str, stored: dict[str, str] | None = None) -> dict:
    its = items(g, stored)
    decisions = json.loads((REVIEW / "decisions" / f"{g}.json").read_text(encoding="utf-8"))
    missing = [i["id"] for i in its if i["id"] not in decisions]
    if missing:
        raise ValueError(f"{g}: no decision for {missing}")
    esc_path = REVIEW / "escalations" / f"{g}.json"
    settled = json.loads(esc_path.read_text(encoding="utf-8")) if esc_path.exists() else {}
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
        was = item.get("stored")
        if was in ("high", "low") and grade != was:
            if item["id"] not in settled:
                escalate[item["id"]] = {"record": item["record"], "stored": was, "proposed": grade, "why": why,
                                        "value": item["value"], "anchor": item["anchor"]}
                continue
            grade = settled[item["id"]]
            if grade == "high" and basis not in BASES:
                raise ValueError(f"{item['id']}: the team lead kept it HIGH; its basis must be named")
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
    ledger = {r["record_id"] for r in json.loads(build.cloud.LEDGER.read_text(encoding="utf-8"))["groups"][g]["records"]}
    unread = {r: why for r, why in build.UNREAD.items() if r in ledger}
    if unread:
        review["unread"] = unread
    held = {p["record_id"] for p in papers(g)}
    local = {r for r in held if build.local_file(r)}
    if local and local == held:  # read wholly by Task F's local readers
        review["tag"], review["reader"] = LOCAL_TAG, LOCAL_READER
    readers = {r: UNRECORDED for r in held if r in UNRECORDED_MODEL and r not in local}
    if local and local != held:  # a mixed group: each local read names its own reader and tag (review of 1cb63bb)
        readers.update({r: LOCAL_READER for r in local})
        review["tags"] = {r: LOCAL_TAG for r in sorted(local)}
    if readers:
        review["readers"] = readers
    return review


# The 15 results whose commits carry no Co-Authored-By trailer (checked 2026-10-30); filled by `models`.
UNRECORDED_MODEL: set[str] = set()


def main(argv: list[str]) -> int:
    global UNRECORDED_MODEL
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
