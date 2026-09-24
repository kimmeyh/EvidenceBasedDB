#!/usr/bin/env python3
"""Sprint 5 Task I correction: applicability for the six pilot papers.

The pilot (scripts/sprint5_task_i_pilot.py) promoted six papers from `seen`
straight to `read`. `read` carries `screened`'s obligations too (ADR-0005
Amendment A2: applicability derived from the source), and the pilot did
not write them. `test_every_screened_or_read_paper_has_real_applicability`
caught it on the next suite run. This writes them, from the pages already
read for the pilot, each rationale ending in its source anchor
(docs/INTAKE_WORKFLOW.md section 8 tests).

DRY RUN BY DEFAULT; `--apply` takes a verified backup (F30), commits,
regenerates export/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import _ANCHOR, append_updated_reason  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-24"

APPLICABILITY = {
    "2604.18837": [
        ("qml", "Quantum-kernel SVMs, including quantum kernel training, are the models under test -- arXiv abstract"),
        ("ml", "Classical kernel SVMs (RBF and others) are the named comparators on UCI tabular data -- arXiv abstract"),
        ("method", "A benchmarking protocol: nested cross-validation, Wilcoxon and Friedman tests, seed sensitivity -- p.14 section 6.2"),
    ],
    "2309.11647": [
        ("qml", "Regression with parameterized quantum circuits is the object of study -- p.3 main results"),
        ("world", "Proved theorems on when random Fourier features reproduce PQC models, true independent of this project -- pp.13-14 Theorem 1"),
    ],
    "2509.06873": [
        ("qml", "Quantum extreme learning machines classifying reduced image data are the model -- arXiv abstract"),
    ],
    "2201.08528": [
        ("ml", "Oversampling (SMOTE and variants) with XGBoost, CatBoost, LightGBM and weaker learners is the subject -- p.4 section 4.1"),
        ("method", "Proves AUC is a proper metric under i.i.d. sampling, an evaluation result -- p.2 Theorem 1"),
    ],
    "2606.29720": [
        ("ml", "Calibration of random forest and gradient boosting under resampling is the subject -- arXiv abstract"),
        ("method", "Evaluates calibration (ECE) with paired Wilcoxon tests and Holm-Bonferroni correction -- p.3 section IV-C"),
    ],
    "2401.06091": [
        ("method", "How to evaluate classifiers under class imbalance: AUROC versus AUPRC -- p.2 Theorem 1"),
        ("ml", "Validated on XGBoost models over four public fairness datasets -- p.7 section 3.2"),
    ],
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    for rows in APPLICABILITY.values():
        for ctx, why in rows:
            assert _ANCHOR.search(why), f"rationale without a source anchor: {why}"
    if apply:
        backup_before_write(DB_PATH, "task i applicability --apply")
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        for arxiv, rows in APPLICABILITY.items():
            pid = conn.execute("SELECT record_id FROM paper_fields WHERE access = ?", (f"arXiv:{arxiv}",)).fetchone()[0]
            for ctx, why in rows:
                conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                             (pid, ctx, why))
            append_updated_reason(conn, pid, f"{TODAY} (Sprint 5 Task I): applicability derived from the pages read "
                                             "for the pilot (the read-tier promotion had skipped it)", TODAY)
            print(f"APPLICABILITY {pid}: {', '.join(c for c, _ in rows)}")
        if not apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; rolled back). Re-run with --apply.")
            return 0
        conn.execute("COMMIT")
        regenerate(conn, EXPORT_DIR)
        print("COMMITTED; export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
