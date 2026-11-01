#!/usr/bin/env python3
"""Sprint 14 Task G (F118): what the store says, step 2 and 3 of the card. Read only.

`python scripts/f118_themes.py` computes the inventory (assertions by context, certainty, claim type and SIM or HW
tag; paper reads by extent) and selects each theme's assertions by keyword on the value, writing
WORK/inventory.json and WORK/themes/<theme>.json for the theme readers. Every count is a snapshot of the day it runs;
the memo states the date. A keyword selection is a rough cut, not a classification: a theme reader drops what does
not bear on its theme.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f118")

# One pattern per theme, matched case-insensitively on the assertion's value.
THEMES = {
    "advantage": r"quantum advantage|speed-?up|supremacy|beyond[- ]classical|dequantiz|classical(ly)? simulat|"
                 r"exponential separation|outperform",
    "kernels": r"\bkernel|bandwidth|exponential concentration|fidelity kernel|projected kernel",
    "trainability": r"barren plateau|vanishing gradient|trainab|gradient variance|local minima|"
                    r"overparametri|expressib",
    "encoding-and-readout": r"(data|amplitude|angle|basis|feature) encod|encoding (scheme|circuit|cost)|data load|"
                            r"state preparation|amplitude embedding|angle embedding|feature map|qram|readout|"
                            r"number of (shots|measurements)|measurement (cost|overhead)|tomograph|classical shadow",
    "noise-and-mitigation": r"error mitigation|error correction|fault[- ]toleran|\bnisq\b|logical qubit|"
                            r"zero[- ]noise|decoherence|noise (model|level|rate|robust)|under noise|noisy hardware",
    "generalization": r"sample complexity|generali[sz]ation|pac learn|vc dimension|rademacher|overfit",
    "tensor-networks": r"tensor network|matrix product|\bmps\b|\bpeps\b|\bttn\b|tensor train|quantum[- ]inspired",
    "qubo-and-feature-selection": r"\bqubo\b|ising|anneal|dirac|feature selection|cardinality|combinatorial "
                                 r"optimi|\bqaoa\b|max-?cut",
    "fraud-and-imbalance": r"fraud|imbalanc|anomal|outlier|credit card|financ|bank",
    "benchmarking": r"baseline|benchmark|hyperparameter|tuned|fair comparison|ablation|cross-validation|"
                    r"\bauc\b|\bf1\b|precision|recall",
    "gates-and-primitives": r"\bgate|universal|clifford|\bcnot\b|fourier transform|\bqft\b|phase estimation|"
                            r"amplitude (estimation|amplification)|grover|swap test|\bhhl\b|block[- ]encod|"
                            r"qsvt|hadamard test|circuit depth",
    "hybrid-practice": r"hybrid|variational|\bvqe\b|\bvqc\b|parameter[- ]shift|optimi[sz]er|ansatz",
    "quantum-resources": r"entangle|superposition|interference|contextual|magic|non-?stabili[sz]er",
    "resource-estimates": r"\d[\d,]* (logical |physical )?qubits|qubit count|resource estimat|t[- ]count|"
                          r"number of qubits",
    "classical-families": r"xgboost|catboost|lightgbm|gradient boost|random forest|extra trees|bagging|"
                          r"logistic regression|\bsvm\b|support vector|naive bayes|isolation forest|"
                          r"local outlier|one-class|multilayer perceptron|\bmlp\b|resnet|deep learning",
    "genai": r"generative|\bgan\b|\bllm\b|large language|transformer|attention mechanism|diffusion model|"
             r"born machine|inference",
}


def _rows(conn: sqlite3.Connection) -> list[dict]:
    q = ("SELECT r.id, r.value, r.certainty, r.certainty_reasons, r.evidence_tag, r.provenance, f.claim_type, "
         "group_concat(c.context_id) FROM records r JOIN assertion_fields f ON f.record_id = r.id "
         "LEFT JOIN record_contexts c ON c.record_id = r.id WHERE r.class = 'assertion' GROUP BY r.id ORDER BY r.id")
    keys = ("id", "value", "certainty", "reasons", "tag", "provenance", "claim_type", "contexts")
    return [dict(zip(keys, row)) for row in conn.execute(q)]


def inventory(conn: sqlite3.Connection, rows: list[dict]) -> dict:
    contexts = Counter(c for r in rows for c in (r["contexts"] or "").split(",") if c)
    return {
        "assertions": len(rows),
        "papers": conn.execute("SELECT count(*) FROM records WHERE class = 'paper'").fetchone()[0],
        "by_context": dict(contexts.most_common()),
        "by_certainty": dict(Counter(r["certainty"] or "none" for r in rows).most_common()),
        "by_claim_type": dict(Counter(r["claim_type"] for r in rows).most_common()),
        "by_tag": dict(Counter(r["tag"] for r in rows).most_common()),
        "reads_by_extent": dict(conn.execute("SELECT extent, count(*) FROM paper_reads GROUP BY extent").fetchall()),
        "papers_by_tier": dict(conn.execute("SELECT tier, count(*) FROM paper_fields GROUP BY tier").fetchall()),
    }


def select(rows: list[dict]) -> dict[str, list[dict]]:
    pats = {t: re.compile(p, re.I) for t, p in THEMES.items()}
    return {t: [r for r in rows if p.search(r["value"] or "")] for t, p in pats.items()}


def main() -> int:
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        rows = _rows(conn)
        inv = inventory(conn, rows)
    finally:
        conn.close()
    themes = select(rows)
    inv["by_theme"] = {t: {"assertions": len(v), "high": sum(r["certainty"] == "high" for r in v)}
                       for t, v in themes.items()}
    (WORK / "themes").mkdir(parents=True, exist_ok=True)
    (WORK / "inventory.json").write_text(json.dumps(inv, indent=1), encoding="utf-8")
    for t, v in themes.items():
        (WORK / "themes" / f"{t}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(inv, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
