#!/usr/bin/env python3
"""Sort the store's quantum-advantage claims into families (Sprint 9 Task E, F78).

Team lead, 2026-10-14: "noting that all QML potential advantages are based
on the fact that Quantum can do Optimization problems potentially faster and
with better results - I think". This computes, from the store, which
families the QML papers that CLAIM an advantage fall into. It reads titles
only: a title that claims an advantage is a claim, not evidence that the
advantage holds. Computed every time, never stored (CLAUDE.md: determinate
facts are computed). Read-only.

    python scripts/qml_advantage_families.py            counts per family
    python scripts/qml_advantage_families.py --titles   with every title
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

CLAIMS = re.compile(r"advantage|speed-?ups?|supremacy|outperform|exponential|beyond classical|quantum[- ]enhanced",
                    re.IGNORECASE)

# First match wins, so the order matters: a "quantum kernel ... speedup"
# title is a kernel claim before it is a generic one.
FAMILIES = [
    ("optimization", r"qaoa|anneal|optimi[sz]|max[- ]?cut|qubo|ising|combinatorial|np-hard|pathfinding|coalition"),
    ("kernels and feature maps", r"kernel|svm|support vector|feature (space|map)"),
    ("linear algebra", r"\bhhl\b|linear (system|solver|algebra)|matrix inversion|massive classical data"),
    ("sampling and generative models",
     # "sampling"/"sampler", not "samples": "Quantum enhanced probing of
     # multilayered-samples" is a sensing paper (review, 2026-10-15).
     r"\bsampl(ing|ers?)\b|generative|born machine|\bgans?\b|boltzmann|distribution learning|monte carlo|"
     r"randomness"),
    ("quantum data and sensing", r"quantum data|from experiments|observables?|sensing|sensor|probing|many-body|"
                                 r"information decoder|state learning"),
    ("quantum dynamics (reservoirs, simulation)", r"reservoir|hamiltonian|chaos"),
    ("learning theory", r"\bpac\b|learnab|generali[sz]ation|computational advantage|provabl"),
]
OTHER = "other or unspecified"


def family(title: str) -> str:
    for name, pattern in FAMILIES:
        if re.search(pattern, title, re.IGNORECASE):
            return name
    return OTHER


def claims(conn) -> list[tuple[str, str]]:
    """(record id, title) for every qml paper whose title claims an advantage."""
    rows = conn.execute("SELECT r.id, r.value FROM records r JOIN record_contexts x ON x.record_id = r.id "
                        "WHERE r.class = 'paper' AND x.context_id = 'qml' ORDER BY r.id")
    return [(rid, title) for rid, title in rows if CLAIMS.search(title or "")]


def sort_claims(conn) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {name: [] for name, _ in FAMILIES}
    out[OTHER] = []
    for rid, title in claims(conn):
        out[family(title)].append((rid, title))
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    conn = connect(DB_PATH)
    try:
        total = conn.execute("SELECT COUNT(*) FROM record_contexts x JOIN records r ON r.id = x.record_id "
                             "WHERE r.class = 'paper' AND x.context_id = 'qml'").fetchone()[0]
        sorted_claims = sort_claims(conn)
    finally:
        conn.close()
    n = sum(len(v) for v in sorted_claims.values())
    print(f"{n} of {total} qml papers have a title that claims an advantage, a speedup or an enhancement")
    for name, items in sorted(sorted_claims.items(), key=lambda kv: -len(kv[1])):
        print(f"- {name}: {len(items)}")
        if "--titles" in args:
            for rid, title in items:
                print(f"    {title}  [{rid}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
