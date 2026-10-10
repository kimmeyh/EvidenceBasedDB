#!/usr/bin/env python3
"""Sprint 5 Task I (F28, Q5 = 2): the learning-synthesis pilot.

Six papers to `read`, their assertions extracted with GRADE-style
certainty, and three LEARNINGS wired to their evidence with `supports` and
`contradicts` -- using only primitives the store already has. The design
is docs/LEARNING_SYNTHESIS.md; `scripts/learnings.py` is the query.

Reading record (the checked_against_source values are true statements):
two read-only agents extracted verbatim quotes with page numbers from the
local PDFs on 2026-09-24 (105,183 tokens / 287 s; 133,613 tokens / 505 s).
Every quote used below as `citation_context` was then checked by the lead
model against the page named, by exact-substring search of that page's
text; one page number was corrected (McDermott's Spearman result is on
p.8, not p.9 as reported). Where PDF text extraction garbles a symbol
(an arrow, a Greek letter) the quote stops before it rather than
reconstructing it.

Certainty follows ADR-0005 section 2e as Sprint 4 Task H applied it: a
single empirical study starts LOW; a theorem with its proof starts HIGH;
move one level only for a named reason. A LEARNING starts at its
strongest supporting assertion and moves DOWN for indirectness and for
contradiction at equal or higher certainty (docs/LEARNING_SYNTHESIS.md
section 3); its provenance begins "synthesis of".

Since Sprint 5 retrospective improvement 1 (2026-09-25) set_tier() refuses
these promotions: the papers had no applicability. Re-running this script
would need scripts/sprint5_task_i_applicability.py applied FIRST.

One-off, kept as the record. DRY RUN BY DEFAULT: applies inside one
transaction, prints, rolls back. `--apply` takes a verified backup (F30),
commits, and regenerates export/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, append_updated_reason, insert_assertion, set_tier  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-24"
TAG = f"{TODAY} (Sprint 5 Task I, F28 pilot)"
AGENT_NOTE = ("read-only agent extracted verbatim quotes with pages from the whole paper; Claude (lead) checked "
              "every quote used on its page")

# arXiv id -> (checked_against_source, mined_by, evidence)
PAPERS = {
    "2604.18837": (f"{TODAY}, Claude, pp.14-15 and 19 checked directly (Table 6, seed sensitivity); {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.1, 14-15, 19, 21, 42",
                   "Empirical study: 9 UCI binary tabular datasets, nested CV, quantum-kernel vs classical SVMs, "
                   "Wilcoxon/Friedman, 16-seed extension, IBM hardware validation. Funded by Schaeffler (not a quantum "
                   "vendor); competing interests declared none (p.42)."),
    "2309.11647": (f"{TODAY}, Claude, p.3 (main results) and pp.13-14 (Theorem 1) checked directly; {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.3, 13-14, 32-33",
                   "Theory paper (v4): theorems and proofs on when random Fourier features dequantize PQC regression. "
                   "No experiments. Two of seven authors list IBM Quantum as affiliation (p.1); public funding only."),
    "2509.06873": (f"{TODAY}, Claude, p.1 (abstract) and p.11 (conclusions) checked directly; {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.1, 5, 11",
                   "Simulation study (v3): quantum extreme learning machines on PCA/autoencoder-reduced MNIST, "
                   "Fashion-MNIST, CIFAR-10 at 6-11 qubits; image data, not tabular. Two of six authors list "
                   "Qilimanjaro Quantum Tech (a quantum vendor) as affiliation (p.1)."),
    "2201.08528": (f"{TODAY}, Claude, pp.4-5 (section 4.1, Table 3) checked directly; {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.2, 4-6",
                   "Empirical study (v3): 73 real tabular datasets, 7 classifiers, 6 oversamplers, 7 seeds; means with "
                   "one-SD bars, no formal test for the headline comparison; imbalance ratios not reported."),
    "2606.29720": (f"{TODAY}, Claude, p.3 (sections V-B, V-C) and p.7 (limitations) checked directly; {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.1-4, 7",
                   "Empirical study (preprint v1, single author): 5 OpenML datasets, imbalance ratio 1.9-70, random "
                   "forest and histogram gradient boosting, 10 seeds x 5-fold CV, Wilcoxon with Holm-Bonferroni."),
    "2401.06091": (f"{TODAY}, Claude, p.2 (Theorem 1 summary), p.4 (Theorem 2), p.8 and p.10 checked directly; {AGENT_NOTE}",
                   f"{TODAY}, Claude, pp.2, 4-5, 7-10",
                   "NeurIPS 2024 (v4): theorems relating AUROC and AUPRC plus synthetic and four real fairness-dataset "
                   "experiments; funding named (Berkowitz fellowship, NIH), appendix checklist not read."),
}

A = "assertion"
ASSERTIONS = [
    # (paper arXiv id, record, relations are wired after all exist)
    ("2604.18837", AssertionRecord(
        id="qksvm-classical-kernels-better-on-uci-tabular", context="qml", evidence_tag="N/A", fidelity="scoped",
        value=("On nine UCI binary tabular datasets with nested cross-validation, classical kernel SVMs outperformed "
               "the best quantum-kernel SVM on 8 of 9; with 16 paired seeds, classical kernels were significantly better "
               "on 6 of 7 datasets (p < 0.001) and a quantum kernel was significantly better only on haberman "
               "(+1.9 percentage points balanced accuracy, p = 0.004)"),
        provenance="kakavand-2026 (arXiv:2604.18837v1), p.19 seed-sensitivity analysis; p.14 section 6.2",
        citation_context=("On 6/7 datasets, classical kernels are significantly better (p < 0.001). On haberman, quantum "
                          "kernels are significantly better (p = 0.004), winning on 14/16 seeds."),
        certainty="low",
        certainty_reasons=("Started LOW: one empirical study. NOT downgraded: nested CV, 16 paired seeds, Wilcoxon and "
                           "Friedman tests, the authors' own power caveat stated (p.14), no quantum-vendor funding (p.42). "
                           "NOT upgraded: nine small UCI datasets, none at fraud scale or fraud-level imbalance"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2604.18837", AssertionRecord(
        id="wilcoxon-n5-floor-is-not-parity", context="method", evidence_tag="N/A", fidelity="exact",
        value=("With five paired observations the exact two-sided Wilcoxon signed-rank test cannot give p below 0.0625, "
               "so 'no comparison significant at 0.05' over five folds is a floor on power, not evidence that two "
               "models perform alike"),
        provenance="kakavand-2026 (arXiv:2604.18837v1), p.14 section 6.2",
        citation_context=("The lack of Wilcoxon significance is thus a sample-size limitation (n = 5), not an absence of "
                          "performance differences."),
        certainty="high",
        certainty_reasons=("Started HIGH: an arithmetic property of the exact test (the smallest two-sided p at n = 5 is "
                           "2/32), stated by the authors and confirmed by their own 16-seed rerun reaching significance"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2309.11647", AssertionRecord(
        id="rff-not-generic-dequantizer-but-matches-some-pqcs", context="qml", evidence_tag="N/A", fidelity="scoped",
        value=("Random-Fourier-feature linear regression is not a generic classical dequantization of parameterized "
               "quantum circuit regression, but for some practically relevant circuits and regression problems it provably "
               "matches the best circuit output efficiently"),
        provenance="sweke (arXiv:2309.11647v4), p.3 main results; Theorem 1 pp.13-14",
        citation_context="RFF-based linear regression cannot be a generic dequantization technique.",
        certainty="high",
        certainty_reasons=("Started HIGH: theorems with proofs (Appendix B). Scope is the paper's: regression, and the "
                           "positive result needs efficiently samplable re-weighting that the authors say often fails (p.14)"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2509.06873", AssertionRecord(
        id="qelm-local-dynamics-match-haar-classically-simulable", context="qml", evidence_tag="SIM", fidelity="scoped",
        value=("For quantum extreme learning machines on PCA- or autoencoder-reduced MNIST, Fashion-MNIST and CIFAR-10 at "
               "6 to 11 qubits, a local integrable XX evolution reached accuracy comparable to Haar-random unitaries, with "
               "limited entanglement that the authors judge compatible with efficient classical simulation"),
        provenance="de-lorenzis-2026 (arXiv:2509.06873v3), p.1 abstract; p.11 conclusions",
        citation_context=("Remarkably, the saturated performance is comparable to that obtained using Haar-random "
                          "unitaries that generate maximally complex dynamics, even though the XX model is integrable and "
                          "local."),
        certainty="low",
        certainty_reasons=("Started LOW: one simulation study. NOT upgraded: 6-11 qubits, comparison descriptive with no "
                           "test, authors ask for larger studies (p.11); image data, so INDIRECT for tabular prediction; "
                           "two authors at a quantum vendor (Qilimanjaro), which here argues against their interest"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2201.08528", AssertionRecord(
        id="oversampling-helps-weak-not-strong-boosters", context="ml", evidence_tag="N/A", fidelity="scoped",
        value=("Across 73 tabular datasets with validation-tuned hyperparameters, oversampling (random, SMOTE and three "
               "variants) improved AUC for weak classifiers (MLP, SVM, decision tree, AdaBoost, LightGBM) but not for "
               "XGBoost or CatBoost; for F1, tuning the decision threshold matched balancing except for MLP and SVM"),
        provenance="elor (arXiv:2201.08528v3), p.4 section 4.1 Figure 1(b); p.5 Table 3",
        citation_context=("balancing significantly improved prediction for the weak classifiers: MLP, SVM, decision tree, "
                          "Adaboost and LGBM. However, for the stronger classifiers, XGBoost and Catboost, it did not."),
        certainty="low",
        certainty_reasons=("Started LOW: one empirical study. NOT upgraded: dispersion reported as one SD with no formal "
                           "test for this comparison; imbalance ratios of the 73 datasets not reported, so fraud-level "
                           "imbalance is not shown to be covered"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2606.29720", AssertionRecord(
        id="resampling-degrades-calibration-recalibration-repairs", context="ml", evidence_tag="N/A", fidelity="scoped",
        value=("On five OpenML datasets (imbalance ratio 1.9 to 70) with random forest and histogram gradient boosting, "
               "SMOTE and random oversampling raised expected calibration error slightly and random undersampling strongly; "
               "one Platt or isotonic recalibration step brought the SMOTE model's ECE from 0.061 to 0.021 or 0.025, below "
               "the unsampled baseline"),
        provenance="liu (arXiv:2606.29720v1), p.3 sections V-B and V-C",
        citation_context=("indicating the harm comes specifically from altering the training data, not merely from "
                          "rebalancing the objective"),
        certainty="low",
        certainty_reasons=("Started LOW: one empirical study, single-author preprint. NOT downgraded: paired Wilcoxon with "
                           "Holm-Bonferroni, Cliff's delta, a designed sample-size control. NOT upgraded: five datasets; "
                           "the author bounds the result at imbalance ratio 70 (p.7), far below fraud's"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
    ("2401.06091", AssertionRecord(
        id="auprc-not-generally-superior-under-imbalance", context="method", evidence_tag="N/A", fidelity="scoped",
        value=("AUROC and AUPRC differ only in how they weight false positives: AUROC weighs all equally, AUPRC weighs "
               "them by the inverse of the model's rate of scoring above the threshold, so AUPRC prioritizes correcting "
               "high-score errors and, for a model calibrated on a low-prevalence subgroup, favors the higher-prevalence "
               "subgroup; AUPRC is therefore not generally the better metric under class imbalance"),
        provenance="mcdermott (arXiv:2401.06091v4, NeurIPS 2024), p.2 Theorem 1; p.4 Theorem 2; p.5 Theorem 3; p.8",
        citation_context=("AUROC weighs all false positives equally, whereas AUPRC weighs false positives at a threshold"),
        certainty="high",
        certainty_reasons=("Started HIGH: theorems with proofs. The subgroup result (Theorem 3) assumes perfect "
                           "calibration, which the authors name as its largest limitation (p.10); the real-data effect is "
                           "mild at prevalence ratios up to 2.7 (p.8)"),
        updated=TODAY, updated_reason=f"{TAG}: extracted at promotion to read")),
]

SYN = "synthesis of the assertions that support or contradict it (see assertion_relations); written by Claude, "
LEARNINGS = [
    AssertionRecord(
        id="learning-qml-no-reliable-tabular-accuracy-gain", context="qml", evidence_tag="N/A", fidelity="scoped",
        value=("On classical tabular prediction tasks, the evidence in this store shows no reliable accuracy gain from "
               "current quantum kernel, variational or quantum-boosting models over tuned classical baselines; where a "
               "quantum model helps, the gain is small and dataset-specific, and several model families provably reduce "
               "to classical kernels"),
        provenance=SYN + f"{TODAY}; awaiting team-lead adjudication",
        certainty="moderate",
        certainty_reasons=("Starts HIGH from its strongest support (real-amplitude-encoding-pqc-is-classical-kernel, a "
                           "theorem). DOWN one for INDIRECTNESS: the high-certainty support covers one model family, and the "
                           "empirical support is UCI tables, reduced images and one fraud dataset. NOT down for "
                           "inconsistency: the one contradicting result (cvqboost-knn-aucpr-0-8108-kaggle-fraud) is LOW, "
                           "below this level, and compares against a published figure rather than a re-run baseline"),
        updated=TODAY, updated_reason=f"{TAG}: learning written from the pilot's evidence"),
    AssertionRecord(
        id="learning-ml-resampling-not-the-lever-for-strong-trees", context="ml", evidence_tag="N/A", fidelity="scoped",
        value=("For strong gradient-boosted tree classifiers on imbalanced tabular data, resampling the training data is "
               "not a reliable way to improve predictions: it did not improve AUC for XGBoost or CatBoost, it degrades "
               "probability calibration unless followed by recalibration, and tuning the decision threshold gives "
               "comparable F1 at lower cost"),
        provenance=SYN + f"{TODAY}; awaiting team-lead adjudication",
        certainty="low",
        certainty_reasons=("Starts LOW from its strongest supports (two single empirical studies, each LOW). NOT down "
                           "further: the two agree and were run independently. Stated limit: neither tested imbalance near "
                           "fraud's (one does not report ratios, the other stops at 70)"),
        updated=TODAY, updated_reason=f"{TAG}: learning written from the pilot's evidence"),
    AssertionRecord(
        id="learning-method-check-metric-and-power-before-reading-a-difference", context="method", evidence_tag="N/A",
        fidelity="scoped",
        value=("Before a comparison of imbalanced-data classifiers is read as a difference between models, check it for "
               "metric and power artifacts: AUPRC's behavior under imbalance is metric-specific rather than generally "
               "better, and non-significance over very few folds cannot establish that two models are equal"),
        provenance=SYN + f"{TODAY}; awaiting team-lead adjudication",
        certainty="moderate",
        certainty_reasons=("Starts HIGH from its supports (a theorem and an arithmetic property of the exact test). DOWN "
                           "one for INDIRECTNESS: the learning generalizes a procedure from two specific results"),
        updated=TODAY, updated_reason=f"{TAG}: learning written from the pilot's evidence"),
]

# (from, to, relation): evidence -> learning
RELATIONS = [
    ("qksvm-classical-kernels-better-on-uci-tabular", "learning-qml-no-reliable-tabular-accuracy-gain", "supports"),
    ("qelm-local-dynamics-match-haar-classically-simulable", "learning-qml-no-reliable-tabular-accuracy-gain", "supports"),
    ("real-amplitude-encoding-pqc-is-classical-kernel", "learning-qml-no-reliable-tabular-accuracy-gain", "supports"),
    ("fourier-wall-public-tabular-refuses-qml", "learning-qml-no-reliable-tabular-accuracy-gain", "supports"),
    ("cvqboost-vs-xgboost-auc-under-balancing", "learning-qml-no-reliable-tabular-accuracy-gain", "supports"),
    ("cvqboost-knn-aucpr-0-8108-kaggle-fraud", "learning-qml-no-reliable-tabular-accuracy-gain", "contradicts"),
    ("oversampling-helps-weak-not-strong-boosters", "learning-ml-resampling-not-the-lever-for-strong-trees", "supports"),
    ("resampling-degrades-calibration-recalibration-repairs", "learning-ml-resampling-not-the-lever-for-strong-trees",
     "supports"),
    ("auprc-not-generally-superior-under-imbalance",
     "learning-method-check-metric-and-power-before-reading-a-difference", "supports"),
    ("wilcoxon-n5-floor-is-not-parity", "learning-method-check-metric-and-power-before-reading-a-difference",
     "supports"),
]
# rff-not-generic-dequantizer-but-matches-some-pqcs is extracted but NOT wired: it bounds the question in both
# directions (no generic dequantization; some circuits do dequantize), and claiming it for either side overstates it.


def paper_id(conn, arxiv: str) -> str:
    row = conn.execute("SELECT record_id FROM paper_fields WHERE access = ?", (f"arXiv:{arxiv}",)).fetchone()
    if row is None:
        raise SystemExit(f"no paper with access arXiv:{arxiv}; run Task C's intake first")
    return row["record_id"]


def run(conn) -> None:
    for arxiv, (checked, mined, evidence) in PAPERS.items():
        pid = paper_id(conn, arxiv)
        set_tier(conn, pid, "read", checked_against_source=checked)
        conn.execute("UPDATE paper_fields SET mined_by = ?, evidence = ? WHERE record_id = ?", (mined, evidence, pid))
        append_updated_reason(conn, pid, f"{TAG}: promoted to read after a direct read; assertions extracted; see paper_yields",
                              TODAY)
        print(f"READ    {pid}")
    for arxiv, rec in ASSERTIONS:
        pid = paper_id(conn, arxiv)
        rec.provenance = rec.provenance.replace(rec.provenance.split(" ")[0], pid, 1)
        insert_assertion(conn, rec, yielded_by=pid)
        print(f"ASSERT  {rec.id}  ({rec.certainty})  <- {pid}")
    for rec in LEARNINGS:
        insert_assertion(conn, rec)
        print(f"LEARN   {rec.id}  ({rec.certainty})")
    for frm, to, rel in RELATIONS:
        conn.execute("INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) VALUES (?, ?, ?)",
                     (frm, to, rel))
        print(f"LINK    {frm} {rel} {to}")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "task i pilot --apply")
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        try:
            run(conn)
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        if not apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; rolled back). Re-run with --apply.")
            return 0
        conn.execute("COMMIT")
        print("COMMITTED")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
