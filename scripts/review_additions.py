#!/usr/bin/env python3
"""F142 part 2 (Sprint 17 Task C): the sign-off `add` table, which adds an assertion to a group's read, or splits one.

Sprint 16 (Manual Validation Q1 = 3) split `he-simulation-scope` in two by editing the reader's read file by hand
(`manifests/sprint13_g_reads/group_g154-r1.json`, commit db2abe3). A read file is the reader's own output; an edit there
records no decision and no reason. The coordinator now writes the new assertion in the group's sign-off,
`WORK/review/signoff/<g>.json`:

    "add": {"<new id>": {"record_id": "<a paper of the group>", "why": "<the decision and who made it>",
                         "assertion": {"value": ..., "anchor": ..., "quotes": [...], "result_type": ...,
                                       "claim_type": ..., "context": ...}}}

and the read file is never touched. `f117_review.papers` merges it, so the new assertion is an item to decide like a
reader's; finalize copies the table into the review file, and `full_read_apply.load_groups` merges it from there, so
the applier enters it, checks its quotes against the paper, and refuses its id where another source holds it. A split
is a `value_replace` on the old assertion plus an `add` for the part it gives up.

One function, used by both scripts, so the review and the apply cannot see two different groups.
"""
from __future__ import annotations

import copy

FIELDS = ("value", "anchor", "quotes", "result_type", "claim_type", "context")
MARK = "added_at_signoff"  # the assertion's own record of the decision: the sign-off's why


def merge(g: str, papers: list[dict], add: dict) -> list[dict]:
    """The group's papers with each `add` entry appended to its paper's assertions, as a copy; the read is unchanged.
    Refused, every problem named at once: an id the group already holds, a paper not in the group, no why, a
    missing field, an empty quote, or an assertion that names an id of its own."""
    if not add:
        return papers
    out = copy.deepcopy(papers)
    by_record = {p["record_id"]: p for p in out}
    held = ({a.get("id_suggestion") for p in out for a in p.get("assertions", [])}
            | {x["id"] for p in out for x in p.get("existing", [])})
    problems = []
    for aid, entry in add.items():
        bad = _problems(aid, entry, held, by_record)
        if bad:
            problems += [f"{aid}: {b}" for b in bad]
            continue
        by_record[entry["record_id"]].setdefault("assertions", []).append(
            {**entry["assertion"], "id_suggestion": aid, MARK: entry["why"].strip()})
        held.add(aid)
    if problems:
        raise ValueError(f"{g}: sign-off add: " + "; ".join(problems))
    return out


def _problems(aid: str, entry, held: set, by_record: dict) -> list[str]:
    if not isinstance(entry, dict):
        return ["an entry is {record_id, why, assertion}"]
    bad = []
    if not str(aid).strip():
        bad.append("no id")
    if aid in held:
        bad.append("an id the group already holds")
    if entry.get("record_id") not in by_record:
        bad.append(f"{entry.get('record_id')!r} is not a paper of the group")
    if not isinstance(entry.get("why"), str) or not entry["why"].strip():
        bad.append("names no why")
    a = entry.get("assertion")
    if not isinstance(a, dict):
        return bad + ["no assertion"]
    missing = [f for f in FIELDS if f != "quotes" and not (isinstance(a.get(f), str) and a[f].strip())]
    quotes = a.get("quotes")
    if not isinstance(quotes, list) or not quotes or not all(isinstance(q, str) and q.strip() for q in quotes):
        missing.append("quotes")
    if missing:
        bad.append(f"missing {missing}")
    own = {a.get("id_suggestion"), a.get("id")} - {None, aid}
    if own:
        bad.append(f"the assertion names another id, {sorted(own)}")
    return bad
