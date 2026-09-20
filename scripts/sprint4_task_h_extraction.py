#!/usr/bin/env python3
"""Sprint 4 Task H (F25 D6): promote five papers to `read`, extract the
opposing assertions with GRADE-style certainty reasons, wire the
`contradicts` relation, and file the three smaller F10 notes where they
will be found again.

One-off, kept as the record. DRY-RUN BY DEFAULT: applies inside one
transaction, prints what it would write, rolls back. `--apply` commits and
regenerates export/.

Reading record (the `checked_against_source` values below are true
statements): pages were read directly from the local PDFs on 2026-09-19 --
loke pp.3-8 (Tables 3-4 on p.6); emami pp.11-14 (conclusions p.11,
acknowledgments and reference list pp.12-13, Tables 1-3 p.14) with the
abstract from the DataCite record; qci-2024-profiling pp.1-2 and p.11
(Table 3); mancilla pp.12-13 (Honesty and scope, Conclusion) with the
abstract; zajac p.5 (Theorem 1, Corollary 1, proof) and p.15
(Limitations). A read-only subagent supplied verbatim quotes with page
numbers for the remaining pages; every quote used as `citation_context`
below is one I checked on the page named.

Certainty follows ADR-0005 section 2e: start where the evidence type puts
it, move one level for a named reason, never further than the reasons
carry. The certainty_reasons say what moved it and what did not.

Lineage note (the plan asked): emami's reference list (p.13) cites
"H. Neven, V. S. Denchev, G. Rose, and W. G. Macready. Qboost: Large scale
classifier training with adiabatic quantum optimization. In ... Proceedings
of the Asian Conference on Machine Learning, volume 25 of PMLR, pages
333-348 ... 2012. URL https://proceedings.mlr.press/v25/neven12.html" --
exactly the paper the store holds as neven-2012. The QCi profiling report
says "Neven et al. (2009)" in its text (p.2) and prints no reference list
in its 11 pages; the 2009 citation is presumably the arXiv precursor of the
same line and is NOT verified here.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import AssertionRecord, insert_assertion, set_tier  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-19"
TAG = f"{TODAY} (Sprint 4 Task H, F25 D6)"
REASON = f"{TAG}: promoted to read after a direct read; assertions extracted; see paper_yields"

LOKE = "loke-2026-cvqboosting-fraud-detection-smu"
EMAMI = "emami-2025-financial-fraud-entropy-computing-qci"
QCI = "qci-2024-profiling-cvqboost"
MANCILLA = "mancilla-2026-fourier-wall-spectra"
ZAJAC = "zajac-2026-inverse-born-rule-equivalence"
NEVEN = "neven-2012-qboost-adiabatic-quantum-optimization"

# (paper id, checked_against_source, mined_by, evidence)
PROMOTIONS = [
    (LOKE,
     "2026-09-19, Claude, read pp.3-8 directly (Tables 3 and 4 on p.6)",
     "2026-09-19, Claude, pp.3-8",
     "Empirical study on the MLG-ULB Kaggle credit-card fraud dataset (70/30 split, SMOTE on the training fold only, "
     "test fold untouched), N = 10 runs with different seeds; CVQBoost on Dirac-3 with a heterogeneous weak-classifier "
     "pool (KNN, LDA, logistic regression, shallow XGBoost); the classical comparator (CAD, Gao et al. 2025) is a "
     "published figure, not a model re-run in the same lineup. Funded by OCBC with in-kind support from QCi (p.8). The "
     "authors' own limitations (p.7): benchmark datasets may not capture real banking transactions; KNN weak classifiers "
     "cost about 378 s each; remote solver overhead and third-party hardware access are bottlenecks."),
    (EMAMI,
     "2026-09-19, Claude, read pp.11-14 directly (conclusions, acknowledgments, reference list, Tables 1-3) plus the abstract via DataCite",
     "2026-09-19, Claude, pp.11-14 and abstract",
     "Vendor benchmark of CVQBoost on Dirac-3 against XGBoost on the Kaggle credit-card fraud dataset (38 features) and "
     "synthetic sets to 70M rows; averages over 10 runs with two-standard-deviation bars; four balancing strategies applied "
     "to training data only; XGBoost run on up to 48 CPUs and four NVIDIA L4 GPUs. Independence: 'All authors were "
     "completely supported by Quantum Computing Inc. in writing this paper' (p.12); the byline lists QCi for all six, and "
     "Chancellor's concurrent Durham University affiliation is not on it (F10 note, Sprint 3), so the six-QCi-authors "
     "reading is correct on the byline and thinner than it looks. Code: github.com/qci-github/eqc-studies/tree/main/CVQBoost. "
     "Its Table 1 (p.14) is the same AUC table as qci-2024-profiling's Table 3 (p.11), so the two records are one dataset, "
     "not two independent measurements."),
    (QCI,
     "2026-09-19, Claude, read pp.1-2 and p.11 directly (cover, abstract, Table 3)",
     "2026-09-19, Claude, pp.1-2 and p.11",
     "Vendor profiling report (no named authors, no venue, no DOI) whose Table 3 (p.11) carries the same 24 AUC rows as "
     "emami-2025's Table 1; the arXiv paper is the write-up of this report. Same dataset and same controls as emami-2025; "
     "not an independent measurement. Cites 'Neven et al. (2009)' in text (p.2) with no reference list."),
    (MANCILLA,
     "2026-09-19, Claude, read pp.12-13 directly (Honesty and scope; Conclusion) plus the abstract via DataCite",
     "2026-09-19, Claude, pp.12-13 and abstract",
     "Methods paper (preprint v1) introducing the SPECTRA certificate; one industrial smart-meter dataset with a real "
     "peak-load target (refused) and a semi-synthetic positive control (real covariates, label generated by a quantum "
     "process; the authors label it as such, p.12); the classical bar includes an order-matched twin and the exact "
     "simulator of the process family, which ties the accuracy (p.12); simulations at 14 qubits or fewer, no hardware "
     "run (p.12, 'Bounded, not provable'). Two authors, one company (Falcondale LLC). F10 notes filed here so they are "
     "not lost: (i) rehman-2026's confidence-thresholded quantum fallback and this paper's 'deploy as a routed "
     "specialist, never as a replacement' (p.12) are the same deployment pattern, a candidate `supports` once rehman "
     "yields; (ii) tung-2026's circuit recommendation 'without quantum evaluation at inference time' and SPECTRA's "
     "simulator-free tier-1 screen are both cheap pre-screens for whether quantum is worth attempting, a theme the "
     "library should be able to query."),
    (ZAJAC,
     "2026-09-19, Claude, read p.5 (Theorem 1, Corollary 1, proof) and p.15 (Limitations) directly, plus the abstract via DataCite",
     "2026-09-19, Claude, p.5 and p.15 and abstract",
     "Theoretical paper (preprint v2) with a proof and small simulator experiments (NumPy state vector, 2-3 qubits, 5 "
     "seeds; agent-read p.11). The core step of Theorem 1 -- a real state vector makes the expectation a real quadratic "
     "form, so only Re(M) contributes -- was checked independently by the reader: for Hermitian M and real c, "
     "c^T Im(M) c = 0 because Im(M) is antisymmetric. Scope per the authors (p.15): data-independent ansatz only; "
     "complex-valued encodings escape the bound (Remark 4, p.6); trainability and NISQ noise not addressed."),
]

ASSERTIONS: list[tuple[AssertionRecord, str]] = [  # (assertion, yielded_by)
    (AssertionRecord(
        id="cvqboost-knn-aucpr-0-8108-kaggle-fraud",
        value=("On the MLG-ULB Kaggle credit-card fraud dataset, CVQBoost run on Dirac-3 with KNN weak classifiers reached a mean "
               "AUC-PR of 0.8108 and AUC-ROC of 0.9821 over 10 runs, against 0.7423 and 0.9734 for the best published classical "
               "model (CAD, Gao et al. 2025): an absolute AUC-PR gain of 0.0685, about 9.2% relative"),
        provenance=f"{LOKE}, p.6 Table 3 and p.7 section 4.1",
        evidence_tag="N/A", context="qml",
        citation_context=('"In comparison, our Dirac-3 CVQBoost with KNN weak classifiers reached 0.8108 AUC-PR, an absolute improvement '
                          'of 0.0685 over CAD, corresponding to a relative improvement of approximately 9.2%." (p.7)'),
        certainty="low",
        certainty_reasons=("Started LOW: a single empirical study on one benchmark dataset, with in-kind vendor support (QCi, p.8). "
                           "NOT upgraded for the 10-run averaging: the comparator's figure is taken from another paper under a different "
                           "protocol ('under our evaluation protocol', p.5), no re-run of CAD in the same lineup, no confidence interval on "
                           "the 0.0685 gap; mancilla-2026 (p.12) would read a bar without an order-matched twin as untested. NOT "
                           "downgraded further: the test fold was kept free of synthetic samples and the split was resampled (p.5)"),
        fidelity="exact", reading_level=13, updated=TODAY, updated_reason=REASON), LOKE),
    (AssertionRecord(
        id="cvqboost-vs-xgboost-training-time-dirac3",
        value=("Training CVQBoost on Dirac-3 took 2.2 +/- 0.5 s at 150,000 training samples with 38 features, against 117.4 +/- 4.0 s "
               "for XGBoost on up to 48 CPUs and four NVIDIA L4 GPUs; XGBoost is faster below about 20,000 samples and slower above"),
        provenance=f"{EMAMI}, p.14 Table 2 and p.6 section 3.2.1",
        evidence_tag="N/A", context="platform:dirac-3", units="seconds (mean +/- 2 standard deviations over 10 runs)",
        citation_context=('"We also find that CVQBoost can be trained much faster, even when compared to state-of-the-art implementations '
                          'on GPU\'s and multicore systems." (p.11)'),
        certainty="low",
        certainty_reasons=("Started LOW: vendor self-benchmark, all authors 'completely supported by Quantum Computing Inc.' (p.12), "
                           "the textbook GRADE downgrade case for conflict of interest. NOT upgraded for the 10-run bars: the XGBoost "
                           "configuration is not shown to be tuned for speed parity, and 'train time' bundles classical pre-processing "
                           "with device time (Table 2 lists dirac3 time separately). Code is public (p.12), which makes replication "
                           "possible but has not happened"),
        fidelity="exact", reading_level=13, updated=TODAY, updated_reason=REASON), EMAMI),
    (AssertionRecord(
        id="cvqboost-vs-xgboost-auc-under-balancing",
        value=("With class balancing applied to the training data, CVQBoost's AUC on the Kaggle fraud dataset is below XGBoost's in 23 of "
               "the 24 reported strategy-and-ratio rows and above it in one (ADASYN at ratio 1.0: 0.8855 vs 0.8826); at minimal "
               "balancing (ratio 0.01) XGBoost leads by about 0.19 AUC (0.9003 vs 0.7105)"),
        provenance=f"{EMAMI}, p.14 Table 1; identical table in {QCI}, p.11 Table 3",
        evidence_tag="N/A", context="qml",
        citation_context=('"The results show that comparable accuracy with traditional boosting methods (XGBoost) when balancing '
                          'techniques have been applied. In particular, we found that CVQBoost can even exceed the performance of XGBoost '
                          'when the ADASYN balancing strategy is used." (p.11)'),
        certainty="moderate",
        certainty_reasons=("Started LOW: vendor self-benchmark (see the runtime assertion). UPGRADED one level for admission against "
                           "interest: the authors' own table shows the comparator ahead in 23 of 24 rows, which is costly to publish and "
                           "therefore credible; the assertion is read off that table, not off the prose that summarizes it favorably. "
                           "NOT upgraded further: one dataset, and qci-2024-profiling is the same table, not a second measurement"),
        fidelity="exact", reading_level=13, updated=TODAY, updated_reason=REASON), EMAMI),
    (AssertionRecord(
        id="fourier-wall-public-tabular-refuses-qml",
        value=("On public tabular benchmarks a tuned classical model reaches every target whose spectrum is low-order, on-grid, slow, "
               "correlated or enumerable, which is where public exports land, so QML losses there are a property of the datasets; "
               "on a real smart-meter peak-load target a gradient-boosted tree reached held-out ROC-AUC 0.999 against 0.910 for the "
               "QNN and the SPECTRA certificate refused the target"),
        provenance=f"{MANCILLA}, p.13 Conclusion and p.6 section 6.1",
        evidence_tag="N/A", context="qml",
        citation_context=('"Some tuned classical model reaches every target whose spectrum is low-order, on-grid, slow, correlated, or '
                          'sparse enough to enumerate, and public tabular exports essentially always land inside that reach. The negative '
                          'benchmark literature is therefore evidence about datasets, not about quantum models." (p.13)'),
        certainty="low",
        certainty_reasons=("Started LOW: preprint v1 from one two-person company, one industrial dataset, the authors' own certificate, "
                           "no independent replication. NOT downgraded: the classical bar is complete by construction (order-matched "
                           "twin and exact simulator included, p.12) and the refusal on the real target is a measurement, not an "
                           "argument. NOT upgraded: the general 'structural property' claim rests on the Fourier-series view of "
                           "angle-encoded QNNs and does not by itself cover other quantum models"),
        fidelity="scoped", reading_level=14, updated=TODAY, updated_reason=REASON,
        contradicts=["cvqboost-knn-aucpr-0-8108-kaggle-fraud", "cvqboost-vs-xgboost-auc-under-balancing"]), MANCILLA),
    (AssertionRecord(
        id="real-amplitude-encoding-pqc-is-classical-kernel",
        value=("Any parameterized quantum circuit built on a real-valued amplitude encoding of the data (including probability "
               "loading), with a data-independent ansatz and any observable, computes a function of the form c(x)^T A c(x) with A a real "
               "symmetric matrix: the reproducing kernel Hilbert space of the kernel (c(x)^T c(x'))^2, which a classical kernel machine "
               "computes in O(N^2) time; such models offer no quantum advantage of that kind"),
        provenance=f"{ZAJAC}, p.5 Theorem 1 and Corollary 1",
        evidence_tag="N/A", context="qml",
        citation_context=('"The hypothesis class of any real-valued amplitude encoding PQC therefore provides no Type B quantum '
                          'advantage: a classical kernel machine with the same data access computes the same functions." (p.5)'),
        certainty="high",
        certainty_reasons=("Started HIGH: a mathematical theorem with a short proof whose central step (a real state vector makes the "
                           "expectation a real quadratic form, so only Re(M) contributes; c^T Im(M) c = 0 for antisymmetric Im(M)) the "
                           "reader verified independently on p.5. NOT downgraded for preprint status: the result depends on the proof, "
                           "not on review. Scope is the authors' (p.15): data-independent ansatz only; complex-valued encodings escape "
                           "the bound; nothing is said about trainability or noise"),
        fidelity="exact", reading_level=16, updated=TODAY, updated_reason=REASON,
        supports=["fourier-wall-public-tabular-refuses-qml"]), ZAJAC),
]

NEVEN_NOTE = (f"{TAG}: lineage confirmed -- emami-2025's reference list (p.13) cites this exact paper (ACML 2012, PMLR volume 25, "
              "proceedings.mlr.press/v25/neven12.html) as QBoost's source; qci-2024-profiling cites 'Neven et al. (2009)' in text (p.2) "
              "with no reference list in its 11 pages, presumably the arXiv precursor of the same line, not verified")


def apply_changes(conn) -> list[str]:
    log = []
    for pid, checked, mined, evidence in PROMOTIONS:
        set_tier(conn, pid, "read", checked_against_source=checked)
        conn.execute("UPDATE paper_fields SET mined_by = ?, evidence = ? WHERE record_id = ?", (mined, evidence, pid))
        existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()[0] or ""
        if TAG not in existing:
            joined = f"{existing} | {REASON}" if existing.startswith(TODAY) else REASON
            conn.execute("UPDATE records SET updated = ?, updated_reason = ? WHERE id = ?", (TODAY, joined, pid))
        log.append(f"read   {pid}")
    for assertion, yielded_by in ASSERTIONS:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (assertion.id,)).fetchone():
            log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, assertion, yielded_by=yielded_by)
        if assertion.id == "cvqboost-vs-xgboost-auc-under-balancing":
            # The same 24-row table appears in both vendor documents; the
            # assertion is yielded by both, so the profiling report meets the
            # read-tier obligation (yields >= 1) with the claim it actually carries.
            conn.execute("INSERT INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)", (QCI, assertion.id))
        rel =(f" contradicts {assertion.contradicts}" if assertion.contradicts else "") + (f" supports {assertion.supports}" if assertion.supports else "")
        log.append(f"assert {assertion.id} <- {yielded_by} [{assertion.certainty}]{rel}")
    existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (NEVEN,)).fetchone()[0] or ""
    if TAG not in existing:
        conn.execute("UPDATE records SET updated = ?, updated_reason = ? WHERE id = ?",
                     (TODAY, f"{existing} | {NEVEN_NOTE}" if existing.startswith(TODAY) else NEVEN_NOTE, NEVEN))
        log.append(f"note   {NEVEN}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        log = apply_changes(conn)
        for line in log:
            print(line)
        tiers = dict(conn.execute("SELECT tier, COUNT(*) FROM paper_fields GROUP BY tier").fetchall())
        yields = conn.execute("SELECT COUNT(*) FROM paper_yields").fetchone()[0]
        rels = dict(conn.execute("SELECT relation, COUNT(*) FROM assertion_relations GROUP BY relation").fetchall())
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        print(f"\ntiers {tiers}; paper_yields {yields}; assertion_relations {rels}; foreign_key_check {len(fk)} problem(s)")
        if fk or not do_apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; nothing written). Re-run with --apply to commit." if not do_apply else "NOT APPLIED")
            return 0 if not do_apply else 1
        conn.execute("COMMIT")
        regenerate(conn, EXPORT_DIR)
        print("applied; export regenerated")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
