#!/usr/bin/env python3
"""F148 (Sprint 18 Task F): the counts a document names, printed from the store, never typed.

A count typed into a document by hand was wrong at least 5 times (5e10948, bb82d0a, 80fcbb9, 6e4bfb7, 6d5bcec,
f1257c1). This script computes them from the store, read-only, and either prints them or rewrites the one block
between the markers below in a document, dated. Earlier dated sections and ADR amendments keep their snapshots: the
block is the document's current count, and `tests/test_doc_counts.py` (live_store) fails when it no longer matches
the store, so a store write is followed by `--write`.

    python scripts/doc_counts.py                          # print the block
    python scripts/doc_counts.py --write docs/INTAKE_WORKFLOW.md [more docs]   # rewrite each document's block
"""
from __future__ import annotations

import datetime as dt
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
BEGIN = "<!-- doc_counts: begin (written by scripts/doc_counts.py; do not edit by hand) -->"
END = "<!-- doc_counts: end -->"
LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
READS = ROOT / "manifests" / "sprint13_g_reads"
REVIEWS = ROOT / "manifests" / "sprint13_g_reviews"
LEVELS = ("high", "moderate", "low", "very-low")
BASIS = re.compile(r"Started (?:HIGH|LOW|MODERATE): ([^.;(,:]+)")  # low_grade writes "basis: why"
SHOWN = 100  # a basis held by fewer assertions is counted under "other"


def read_only(path: Path = None) -> sqlite3.Connection:
    return sqlite3.connect(f"{Path(path or DB_PATH).resolve().as_uri()}?mode=ro", uri=True)


def bases(conn, level: str) -> list[tuple[str, int]]:
    """The basis each assertion at `level` started from, as its certainty_reasons name it; small ones as "other"."""
    c = Counter()
    for (r,) in conn.execute("SELECT certainty_reasons FROM records WHERE class = 'assertion' AND certainty = ?",
                             (level,)):
        m = BASIS.match(r or "")
        c[m.group(1).strip() if m else "other"] += 1
    big = [(b, n) for b, n in c.most_common() if n >= SHOWN and b != "other"]
    rest = sum(c.values()) - sum(n for _, n in big)
    return big + ([("other", rest)] if rest else [])


def counts(conn) -> dict:
    by_level = dict(conn.execute("SELECT COALESCE(certainty, 'ungraded'), COUNT(*) FROM records "
                                 "WHERE class = 'assertion' GROUP BY 1").fetchall())
    tiers = dict(conn.execute("SELECT tier, COUNT(*) FROM paper_fields GROUP BY tier").fetchall())
    import json
    groups = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]
    read = {p.stem[len("group_"):] for p in READS.glob("group_*.json")}
    reviewed = {p.stem for p in REVIEWS.glob("g*.json")}
    return {"assertions": sum(by_level.values()), "by_level": by_level,
            "high_bases": bases(conn, "high"), "low_bases": bases(conn, "low"),
            "papers": sum(tiers.values()), "tiers": tiers,
            "groups": len(groups), "groups_read": len(set(groups) & read),
            "groups_reviewed": len(set(groups) & reviewed)}


def block(c: dict, today: str) -> str:
    lv = ", ".join(f"{k.upper()} {c['by_level'][k]:,}" for k in (*LEVELS, "ungraded") if c["by_level"].get(k))
    hb = "; ".join(f"{b} {n:,}" for b, n in c["high_bases"])
    lb = "; ".join(f"{b} {n:,}" for b, n in c["low_bases"])
    tiers = ", ".join(f"{k} {v:,}" for k, v in sorted(c["tiers"].items()))
    return "\n".join([
        BEGIN,
        f"Counts from the store as of {today}, printed by `scripts/doc_counts.py` (never typed):",
        "",
        f"- Assertions: {c['assertions']:,} ({lv}).",
        f"- HIGH by the basis it started from: {hb}.",
        f"- LOW by the basis it started from: {lb}.",
        f"- Papers and other sources: {c['papers']:,} ({tiers}).",
        f"- Ledger groups: {c['groups']:,}; with a read file {c['groups_read']:,}; with a review file "
        f"{c['groups_reviewed']:,}.",
        END])


def rewrite(doc: Path, text: str) -> bool:
    """Replace the document's one block with `text`; refuse a document with none or with more than one."""
    body = doc.read_text(encoding="utf-8")
    n = body.count(BEGIN)
    if n != 1 or body.count(END) != 1 or body.index(END) < body.index(BEGIN):
        raise SystemExit(f"REFUSED: {doc} holds {n} doc_counts blocks; it needs exactly one, begin before end")
    start, end = body.index(BEGIN), body.index(END) + len(END)
    new = body[:start] + text + body[end:]
    if new != body:
        doc.write_text(new, encoding="utf-8")
    return new != body


def block_in(doc: Path) -> str:
    body = doc.read_text(encoding="utf-8")
    return body[body.index(BEGIN):body.index(END) + len(END)]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    today = dt.date.today().isoformat()
    with read_only() as conn:
        text = block(counts(conn), today)
    if "--write" not in args:
        print(text)
        return 0
    for name in args[args.index("--write") + 1:]:
        doc = Path(name) if Path(name).is_absolute() else ROOT / name
        print(f"{'rewrote' if rewrite(doc, text) else 'current'} {doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
