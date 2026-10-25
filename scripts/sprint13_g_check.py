#!/usr/bin/env python3
"""Sprint 13 Task G (F113): a reader's own check of its group file, before it finishes.

The same checks the write path makes (`store.quotes.require_verbatim`: every
quote verbatim in the source's text layer, every figure in a value held by
its own quotes, no stray quote mark), plus the shape this task's prompt asks
for: a verdict on every stored assertion given to the reader, a full read or
a reason for each part not read, and the grading fields. Read-only: it
writes nothing and never opens the store.

Usage:
  python scripts/sprint13_g_check.py <group file> <group brief>
Prints one line per problem and ends "N problems"; 0 is the reader's finish line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import plain, require_verbatim, source_text  # noqa: E402

VERDICTS = {"confirmed", "corrected", "narrowed", "widened", "contradicted", "not in the paper"}
RESULT_TYPES = {"measured", "theoretical", "field", "claim", "cited", "vendor", "setup"}
BASES = {"setup", "scope", "definition", "proved result", "stated limit"}
KINDS = {"shown", "claimed", "cited"}
CLAIM_TYPES = {"positive", "absence", "vendor-self-claim"}
CONTEXTS = {"qml", "qc", "ml", "world", "method"}


def assertion_problems(tag: str, a: dict, text: str) -> list[str]:
    out = []
    quotes = a.get("quotes") or []
    if not quotes:
        return [f"{tag}: no quotes"]
    cc = "; ".join(f'"{q}" ({a.get("anchor") or "anchor"})' for q in quotes)
    try:
        require_verbatim(tag, cc, text, value=a.get("value") or "")
    except ValueError as e:
        out.append(str(e))
    for q in quotes:
        if not 10 <= len(q) <= 300:
            out.append(f"{tag}: a quote of {len(q)} characters (10 to 300)")
    if a.get("result_type") not in RESULT_TYPES:
        out.append(f"{tag}: result_type {a.get('result_type')!r} is not one of {sorted(RESULT_TYPES)}")
    if a.get("kind") not in KINDS:
        out.append(f"{tag}: kind {a.get('kind')!r}")
    if a.get("claim_type") not in CLAIM_TYPES:
        out.append(f"{tag}: claim_type {a.get('claim_type')!r}")
    if a.get("context") not in CONTEXTS:
        out.append(f"{tag}: context {a.get('context')!r}")
    if a.get("certainty_suggestion") == "high" and a.get("high_basis") not in BASES:
        out.append(f"{tag}: a high suggestion needs high_basis, one of {sorted(BASES)}")
    if not (a.get("anchor") or "").strip():
        out.append(f"{tag}: no anchor (section and page)")
    return out


def paper_problems(p: dict, given: set[str]) -> list[str]:
    rid = p.get("record_id", "?")
    out = []
    path = p.get("file") or ""
    if not Path(path).is_file():
        return [f"{rid}: file not found: {path}"]
    text = plain(source_text(path))
    if p.get("read_extent") not in ("full", "partial"):
        out.append(f"{rid}: read_extent must be full or partial")
    if p.get("read_extent") == "partial" and not (p.get("not_read") or "").strip():
        out.append(f"{rid}: a partial read names each part not read and why, in not_read")
    answered = {e.get("id") for e in p.get("existing", [])}
    for missing in sorted(given - answered):
        out.append(f"{rid}: no verdict on stored assertion {missing}")
    for e in p.get("existing", []):
        tag = f"{rid}/{e.get('id')}"
        if e.get("verdict") not in VERDICTS:
            out.append(f"{tag}: verdict {e.get('verdict')!r} is not one of {sorted(VERDICTS)}")
            continue
        if e["verdict"] == "not in the paper":
            if not (e.get("note") or "").strip():
                out.append(f"{tag}: say in note what the paper says instead")
            continue
        if e["verdict"] != "confirmed" or e.get("quotes"):
            out += assertion_problems(tag, e, text)
        if e["verdict"] != "confirmed" and not (e.get("note") or "").strip():
            out.append(f"{tag}: say in note what changed and why")
    if p.get("bears_on_context") and not p.get("assertions") and not p.get("existing"):
        out.append(f"{rid}: bears on a context but has no assertions")
    for a in p.get("assertions", []):
        out += assertion_problems(f"{rid}/{a.get('id_suggestion')}", a, text)
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    brief = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    given = {r["record_id"]: {e["id"] for e in r.get("stored_assertions", [])} for r in brief["records"]}
    problems = [f"{rid}: no entry for this record" for rid in sorted(set(given) - {p.get("record_id")
                                                                                   for p in data.get("papers", [])})]
    problems += [x for p in data.get("papers", []) for x in paper_problems(p, given.get(p.get("record_id"), set()))]
    for x in problems:
        print(x)
    print(f"{len(problems)} problems")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
