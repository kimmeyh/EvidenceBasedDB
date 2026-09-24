#!/usr/bin/env python3
"""Key learnings, computed (Sprint 5 Task I, F28; design in docs/LEARNING_SYNTHESIS.md).

A LEARNING is an assertion whose provenance begins "synthesis of" (a
generalization over other assertions, which reach it through `supports`
and `contradicts`). The first definition -- "an assertion no paper yields
that something supports or contradicts" -- was tried first and caught
hsbc-b1-variable-count-wrong-78, a project assertion sourced from the
consumer repository's amendment log: not being yielded by a paper does
not make an assertion a synthesis. See docs/LEARNING_SYNTHESIS.md section 7. This script finds them and prints each
with its evidence: every supporting and contradicting assertion, its
certainty, its source paper and that paper's tier, and the verbatim
sentence it rests on. Nothing printed is stored -- the evidence table is
determinate and is recomputed on every run (CLAUDE.md: determinate facts
are computed, never stored).

Read-only. Usage:
    python scripts/learnings.py              # every learning
    python scripts/learnings.py <id>         # one learning
    python scripts/learnings.py --json       # machine-readable
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_, DB_PATH, _ = script_paths(__file__)
ORDER = {"high": 0, "moderate": 1, "low": 2, "very-low": 3, None: 4}


def learning_ids(conn) -> list[str]:
    rows = conn.execute(
        "SELECT r.id FROM records r "
        "WHERE r.class = 'assertion' AND r.provenance LIKE 'synthesis of%' "
        "ORDER BY r.id"
    )
    return [r["id"] for r in rows]


def evidence(conn, learning_id: str) -> list[dict]:
    """One row per EVIDENCE ASSERTION, never per source. An assertion two
    papers yield (cvqboost-vs-xgboost-auc-under-balancing: emami and the
    QCi profiling report) is one piece of evidence with two sources; the
    first version of this query joined paper_yields directly and counted
    it twice in the balance (found on the pilot's first run, 2026-09-24)."""
    rows = conn.execute(
        "SELECT a.relation, e.id, e.value, e.certainty, e.certainty_reasons, "
        "       (SELECT group_concat(context_id) FROM record_contexts c WHERE c.record_id = e.id) AS contexts, "
        "       (SELECT group_concat(y.paper_id || ' (' || pf.tier || ')', '; ') FROM paper_yields y "
        "          JOIN paper_fields pf ON pf.record_id = y.paper_id WHERE y.assertion_id = e.id) AS sources, "
        "       f.citation_context "
        "FROM assertion_relations a "
        "JOIN records e ON e.id = a.from_assertion_id "
        "LEFT JOIN assertion_fields f ON f.record_id = e.id "
        "WHERE a.to_assertion_id = ? ORDER BY a.relation DESC, e.id",
        (learning_id,),
    )
    return [dict(r) for r in rows]


def learning(conn, learning_id: str) -> dict:
    r = conn.execute("SELECT id, value, certainty, certainty_reasons, "
                     "(SELECT group_concat(context_id) FROM record_contexts c WHERE c.record_id = records.id) AS contexts "
                     "FROM records WHERE id = ?", (learning_id,)).fetchone()
    if r is None:
        raise SystemExit(f"no record {learning_id!r}")
    ev = evidence(conn, learning_id)
    balance = {"supports": {}, "contradicts": {}}
    for e in ev:
        level = e["certainty"] or "unrated"
        balance[e["relation"]][level] = balance[e["relation"]].get(level, 0) + 1
    evidence_contexts = sorted({c for e in ev for c in (e["contexts"] or "").split(",") if c})
    return {**dict(r), "evidence": ev, "balance": balance, "evidence_contexts": evidence_contexts}


def render(item: dict) -> str:
    lines = [f"LEARNING {item['id']}  [{item['contexts']}]  certainty: {item['certainty']}",
             f"  {item['value']}",
             f"  why this certainty: {item['certainty_reasons']}",
             f"  balance: supports {item['balance']['supports'] or '-'}; "
             f"contradicts {item['balance']['contradicts'] or '-'}; evidence contexts {item['evidence_contexts']}"]
    for e in sorted(item["evidence"], key=lambda e: (e["relation"] != "supports", ORDER.get(e["certainty"], 4))):
        src = e["sources"] or "no source paper"
        lines.append(f"  {e['relation'].upper():11s} {e['certainty'] or 'unrated':9s} {e['id']}  <- {src}")
        if e["citation_context"]:
            lines.append(f"      \"{e['citation_context'][:220]}\"")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    ids = [a for a in args if not a.startswith("--")]
    conn = connect(DB_PATH)
    try:
        items = [learning(conn, i) for i in (ids or learning_ids(conn))]
    finally:
        conn.close()
    if as_json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(render(i) for i in items) if items else "no learnings in the store yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
