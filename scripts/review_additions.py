#!/usr/bin/env python3
"""F142 part 2 (Sprint 17 Task C): the sign-off `add` table, which adds an assertion to a group's read, or splits one.

Sprint 16 (Manual Validation Q1 = 3) split `he-simulation-scope` in two by editing the reader's read file by hand
(`manifests/sprint13_g_reads/group_g154-r1.json`, commit db2abe3). A read file is the reader's own output; an edit there
records no decision and no reason. The coordinator now writes the new assertion in the group's sign-off,
`WORK/review/signoff/<g>.json`:

    "add": {"<new id>": {"record_id": "<a paper of the group>", "why": "<the decision and who made it>",
                         "assertion": {"value": ..., "anchor": ..., "quotes": [...], "result_type": ...,
                                       "claim_type": ..., "context": ..., "kind": ...}}}

and the read file is never touched. `f117_review.papers` merges it, so the new assertion is an item to decide, always
(kind "new-added"), and finalize runs the reader's own checks on it (`text_problems`); finalize then copies the table into the review file, and `full_read_apply.load_groups` merges it from there, so
the applier enters it, checks its quotes against the paper, and refuses its id where another source holds it. A split
is a `value_replace` on the old assertion plus an `add` for the part it gives up.

One function, used by both scripts, so the review and the apply cannot see two different groups.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("sprint13_g_check", Path(__file__).with_name("sprint13_g_check.py"))
reader = importlib.util.module_from_spec(_spec)  # the reader's own check (fresh-eyes review of 2580ce2)
_spec.loader.exec_module(reader)

FIELDS = ("value", "anchor", "quotes", "result_type", "claim_type", "context", "kind")
# The reader's allowed values; a value outside them crashed the applier's grading with a KeyError, not a refusal
ALLOWED = {"result_type": reader.RESULT_TYPES, "claim_type": reader.CLAIM_TYPES, "context": reader.CONTEXTS,
           "kind": reader.KINDS}
MARK = "added_at_signoff"  # the sign-off's why, written into the stored assertion's history by the applier


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


def text_problems(papers: list[dict], add: dict, text_of) -> list[str]:
    """The reader's checks that read the paper (`sprint13_g_check`): every quote verbatim and 10 to 300 characters,
    a figure in the value held by its quotes, a high suggestion with its basis and reason, a measured result never
    high, a figure reading never high, and each quote on a page its anchor names. `text_of(path)` gives the plain
    text. Run by `f117_review.finalize` on every added assertion, as the reader's check runs on every reader's one."""
    out = []
    file_of = {p["record_id"]: p.get("file") or "" for p in papers}
    for aid, entry in add.items():
        a, path = {**entry["assertion"], "id_suggestion": aid}, file_of[entry["record_id"]]
        tag = f"{entry['record_id']}/{aid}"
        text = text_of(path)
        out += reader.assertion_problems(tag, a, text)
        if a.get("from_figure") and a.get("certainty_suggestion") == "high":
            out.append(f"{tag}: a value read from a figure is never high on the figure alone")
        out += reader.page_problems(tag, a, path, text)
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
    bad += [f"{f} {a[f]!r} is not one of {sorted(allowed)}" for f, allowed in ALLOWED.items()
            if f not in missing and a.get(f) not in allowed]
    own ={a.get("id_suggestion"), a.get("id")} - {None, aid}
    if own:
        bad.append(f"the assertion names another id, {sorted(own)}")
    return bad
