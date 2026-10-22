#!/usr/bin/env python3
"""Sprint 11 Tasks F and G (F97, F96): the first-pass reads entered, one ledger.

`manifests/sprint11_read_ledger.json` gives every record this sprint reads
to exactly one group and each group to one task (G: groups g01 to g24, the
200-record slice; F: g25 onward, the new papers). One Sonnet 5.5 reader per
group wrote `manifests/sprint11_reads/group_<g>.json` (kept verbatim) under
`READER_PROMPT.md`. A reader file whose records are not exactly its group's
is refused, so no two reads touch one record.

HOW THE SOURCES WERE READ (ADR-0005 A4: a subagent's read alone never
qualifies `read`): the coordinator checked every quote against the source
text by script (`store.quotes.require_verbatim`, the write path's own check,
INTAKE_WORKFLOW.md section 31) and every figure in a value against that
assertion's quotes, then read every value against its quoted passages with
about 220 characters each side. That read is what QUOTE_EDITS, VALUE_REPLACE,
CONTEXT_FIX, DROP and HIGH_REVIEWED record.

CERTAINTY follows the store's GRADE mapping as Sprint 10 Task I used it
(`sprint10_f89_reading.py`): a result proved in the paper, or the paper's own
statement of its setup, scope or limits, starts HIGH, and only the ids named
in HIGH_REVIEWED get it, after the coordinator's read; an empirical result
from one study, an author's claim and a cited claim start LOW; a vendor's
description of its own product starts MODERATE and a vendor's result LOW. No
admission-against-interest upgrade is made. The reader's own suggestion is
not used.

A record whose reader found nothing that bears on any context (no
assertions, a `why_not`) gets its read rows and the reason, and keeps its
tier: it was read, and yields nothing. A Task G record with no copy (the
ledger's `no_copy`) keeps its tier with the reason in NO_COPY.

    python scripts/sprint11_reading.py --task G            # dry run: every quote checked; nothing written
    python scripts/sprint11_reading.py --task G --apply    # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_verified_assertion,  # noqa: E402
                          set_tier, sync_verified_assertion, validate_assertion)
from store.quotes import QUOTE, plain, require_edit_basis, require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
TAGS = {"G": "Sprint 11 Task G, F96", "F": "Sprint 11 Task F, F97"}
LEDGER = ROOT / "manifests" / "sprint11_read_ledger.json"
READS_DIR = ROOT / "manifests" / "sprint11_reads"
SUBAGENT_READER = f80.SUBAGENT_READER

COORDINATOR_DETAIL = ("every quoted passage with about 220 characters each side, every quote checked verbatim and "
                      "every figure in a value checked against its quotes by script; the rest of the paper not "
                      "read by the coordinator" + f80.f78.ABSENCE_NOTE)

# Task G records the ledger holds with no copy, each with its own reason
# (`sprint11_f96_downloads.py` log, 2026-10-21; OpenAlex's oa_status).
NO_COPY = {
    "da-silva-2012-classical-superposed-learning-quantum-weightless": "Elsevier, closed (OpenAlex oa_status closed)",
    "panella-2009-neurofuzzy-networks-nonlinear-quantum-learning": "IEEE, closed (OpenAlex oa_status closed)",
    "pande-2020-bibliometric-survey-quantum-machine-learning": "Taylor & Francis, closed (OpenAlex oa_status closed)",
    "kamruzzaman-2020-quantum-deep-learning-neural-networks": "Springer chapter, closed (OpenAlex oa_status closed)",
    "chakraborty-2020-analytical-review-quantum-neural-network": "IEEE conference, closed (OpenAlex oa_status closed)",
    "sergioli-2020-quantum-quantum-like-machine-learning": "Springer, closed (OpenAlex oa_status closed)",
    "macaluso-2020-variational-algorithm-quantum-neural-networks": (
        "OpenAlex lists a free copy, but its host failed TLS certificate verification on 2026-10-21; not fetched "
        "around the check"),
    "mezquita-2021-retracted-chapter-review-k-nn": (
        "a RETRACTED chapter (title); OpenAlex lists no PDF for it although it marks it green"),
}
RETRACTED = {"mezquita-2021-retracted-chapter-review-k-nn"}

# Exact source characters a reader's quote missed (an em dash or a minus
# sign typed as ASCII, a dropped symbol), looked up in the source text.
QUOTE_EDITS: dict[str, list[tuple[str, str | None]]] = {
    "qsvm-dual-complexity": [("O(M 4.67/2)", "O(M 4.67/ε2)")],
    "qsvm-primal-pegasos-complexity": [("O(min{M 2/6, 1/10})", "O(min{M 2/ε6, 1/ε10})")],
    "pqc-concept-only": [("a concept--lower", "a concept—lower")],
    "zx-method-not-complete": [("not complete--especially", "not complete—especially")],
    "best-cv-score-quantum-093-vs-classical-091": [("(score=0.91", "(score = 0.91")],
    "fqmci-numerical-slope": [("QMCI is -1.02", "QMCI is −1.02"), ("value of -1 (", "value of −1 (")],
    "qcnn-classical-surrogate-matches": [("surrogate--based", "surrogate—based"), ("shadows--that", "shadows—that")],
    "ion-trap-circle-4-layers": [("counterpart A =", "counterpart A∗ =")],
    "dqfim-numerical-setup": [("V = U (g) with random parameter g,", "V = U (θg) with random parameter θg,")],
    "sim-exponential-crossover": [("ments -- yet", "ments — yet")],
    "feasibility-threshold-ising-ratio": [("97 - 98%", "97 − 98%")],
}
EXTRA_QUOTES: dict[str, list[str]] = {
    # g25
    "kabane-presplit-inflation": [
        "As shown in Table 1[2]",
        # fresh-eyes review, 2026-10-22: "SMOTE" is in the table's caption, not the reader's quotes
        "Table 1: XGBoost Performance Metrics with SMOTE Sampling Before Train-Test Split"],
    # g27
    "qkm-fewer-examples-classical-data": [
        "we propose to generate artificial labels for classical datasets (relabeling) that are more advantageous for "
        "quantum learners"],
    "hybridq-qutip-speed": [
        "QuTiP (version 4.7)",
        # fresh-eyes review, 2026-10-22: "local" was outside the reader's quotes
        "the time taken to apply a local depolarizing channel on each qubit"],
    "rand-ncf-critical-enablers": [
        "NCF 3, Provide Internet Based Content, Information, and Communication Services",
        "NCF 35, Provide Identity Management and Associated Trust Support Services",
        "NCF 52, Provide Information Technology Products and Services"],
    # g02
    "khan-qlstm-accuracy-table5": ["Table 5: Predictive Accuracy Analysis"],
    # g07: the reader left out the error term; the text layer prints it plainly.
    "qfm-toxicity-comparable": ["60.4±5.1%, on par with the best classical kernels"],
    # g11: the uncertainty the reader's value left as "stated with an uncertainty".
    "ion-trap-circle-4-layers": ["Asim = 93 ± 2%"],
    # g15: the value's hardware future work sits after the reader's quote.
    "simulated-only-future-hardware": ["evaluating performance on actual (rather than simulated) quantum devices"],
    # g19: the value's IID statement sits beside the reader's quotes.
    "slimqfl-mini-mnist-iid-setup": [
        "We conduct all experiments on miniMNIST with independent and identically distributed (IID) data."],
    # g20: the product name sits just before the reader's quote.
    "ronkko-iqm-spark-description": ["we introduce the IQM SparkTM"],
    # g21: the qubit counts and the multivariate case sit around the reader's quotes.
    "qcbm-scaling-limit": [
        "Increasing the number of qubits to five or six, for the one-dimensional case",
        "The same problem appeared when increasing the number of features in the multivariate case"],
    "qsvr-hardware-auc-050": [
        "the kernel estimation of our QSVR was carried out on real hardware for the CoverT and MNIST data sets"],
    # g22: the vendor and the chosen model sit just before the reader's quotes.
    "peixoto-ibm-hardware-run": [
        "the quantum computers provided by IBM", "only the best performant model HP-set was used, i.e. the TPE-trained VQC"],
    # g23: the system studied sits beside the reader's quote.
    "embedding-framework-mgo-vacancy": ["studying the optical properties of the neutral oxygen vacancy in MgO"],
    # g24: the device and the two applications sit beside the reader's quotes.
    "lee-qcnn-noise-robustness": ["We used the noise parameters observed from IBMQ Jakarta"],
    "neumann-dqml-proposal": ["We will consider a distributed adder and a distributed distance-based classifier."],
    # Fresh-eyes review, 2026-10-22: replaced values that said more than their quotes.
    "qsvm-dual-complexity": ["ε the solution accuracy compared to the ideal result from exact expectation values"],
    "qsvm-primal-pegasos-complexity": [
        "We prove under an empirically motivated assumption that the kernelized primal problem can alternatively be "
        "solved"],
    "roadmap-1000-qubits-2023": [
        "leading research groups and computing companies confidently plan the development of",
        "each new generation of quantum processors surpasses the previous generation by a significant factor"],
    "rydberg-fidelity-81-to-90": ["the average residual interaction strength is reduced to"],
}
VALUE_REPLACE: dict[str, str] = {  # the coordinator's read; each replacement says only what its quotes say
    # g25: the table is introduced as "Table 1[2]", the paper's reference 2.
    "kabane-presplit-inflation": (
        "The paper presents, as Table 1 marked with its reference [2], XGBoost with SMOTE sampling before the "
        "train-test split reaching accuracy 99.969%, precision 99.938%, recall 100%, F1-score 99.969% and AUC "
        "99.969%, and states the near-perfect performance is likely influenced by data leakage."),
    # g26: the quote says "comparatively low", not "lower than GBDTs".
    "tfm-synthetic-noise": (
        "The authors report that on 20 synthetic datasets with high noise and weak class separation the foundation "
        "models reach the highest AUC, but their SSC remains comparatively low."),
    # g27: the datasets are relabeled to favor quantum kernels (same paper, section III).
    "qkm-fewer-examples-classical-data": (
        "On semi-artificial classical datasets, whose labels the authors generate to be more advantageous for "
        "quantum learners while the features stay unchanged, the authors report that quantum kernel methods can "
        "require fewer training examples than classical kernels to reach comparable error, and call it the first "
        "empirical evidence that this is possible."),
    "hybridq-qutip-speed": (
        "The authors report that, on one quad-core machine, HybridQ substantially outperforms QuTiP "
        "(version 4.7) after around 7 qubits when applying a local depolarizing channel to each qubit."),
    "rand-ncf-critical-enablers": (
        "The authors identify three national critical functions as critical enablers of the PQC migration: NCF 3 "
        "(Internet-based content, information and communication services), NCF 35 (identity management and "
        "associated trust support services) and NCF 52 (information technology products and services)."),
    # g29: results of a stylized economic model, scoped to it.
    "correlated-errors-segment-the-market": (
        "In their model of credit-market competition, the authors show that with correlated screening errors "
        "(potentially from similar AI systems and overlapping financial-sector data) ex-ante identical lenders "
        "specialize across distinct market segments, generating a hockey-stick interest-rate schedule, while with "
        "independent errors a single market segment emerges."),
    "policy-effects-ai-and-data-sharing": (
        "In their model, the authors find that adoption of AI technology benefits borrowers who face high rates and "
        "improves financial inclusion, while a mandatory data-sharing policy has ambiguous spillover effects on the "
        "financially excluded."),
    # g08: "does not test real quantum hardware" is the reader's inference, not the quote.
    "benchmark-scope-simulation": (
        "The authors state that the benchmark is performed via classical simulations on different artificial and "
        "small-scale reference classification datasets."),
    # g11: the uncertainty written out.
    "ion-trap-circle-4-layers": (
        "The authors report that for the two-dimensional circle problem with 4 layers the classification accuracy "
        "on the QPU is Asim = 93 ± 2%, slightly lower than its classically simulated counterpart A∗ = 97%."),
    # g12: the text layer runs the year into footnote marker 46; the value keeps what is printed.
    "roadmap-1000-qubits-2023": (
        "The authors state that leading research groups and computing companies plan quantum computers of "
        "1000-qubit size by the year the text layer prints as 202346 (a year run into a footnote marker), and "
        "that it is not possible to tell at present whether each new generation of quantum processors will surpass "
        "the previous one by a significant factor."),
    # g18: "seven-class stripe problem" and "IBM" are not in the quotes.
    "qudit-squeezing-needed": (
        "The authors report that without the squeezing operation the median accuracy saturates at around 0.7, while "
        "with squeezing the median accuracy reaches 0.95 and higher."),
    "qudit-hardware-limit": (
        "The authors report that when re-trained and evaluated on actual hardware, performance is comparable to "
        "simulation only for the first two layers, then saturates and decreases strongly. They state that only "
        "single-qudit circuits were "
        "investigated and multi-qudit circuits are a necessary next step."),
    # g20: the authors' employer is not in the quotes.
    "ronkko-iqm-spark-description": (
        "The authors introduce the IQM Spark prototype, a 5-qubit superconducting quantum computer designed and "
        "developed to enable low-barrier access to both its hardware and software components."),
    # g21: "linear connectivity only" and "IBM" are not in the quotes.
    "qcbm-linear-connectivity-no-swap": (
        "The authors state that the multivariate Born machine with the (linear, 1) choice can be mapped to an IBM "
        "Quantum chip without using any SWAP gates."),
    "qsvr-hardware-auc-050": (
        "The authors report that when the QSVR kernel was estimated on real hardware for the CoverT and MNIST data "
        "sets, the AUC was 0.50 for both, meaning no advantage over random guessing."),
    # g23: "2D" sits outside the quotes.
    "rydberg-fidelity-81-to-90": (
        "The authors report an estimated ground state fidelity of 81% for the experimental graph, and that for an "
        "alternative graph whose average residual interaction strength is reduced, the ground state fidelity after "
        "the same quasi-adiabatic evolution is improved to 90%."),
    # g19: the quote is the figure legend, without its figure number.
    "qvit-comparable-to-classical": (
        "The authors report that the hybrid QViT obtains almost the same ROC curve and AUC score as the classical "
        "baseline, though it lags by approximately two percentage points; the figure legend gives AUC 0.793 for the "
        "classical model and 0.775 for the quantum model."),
    # g07: the error term the reader left out.
    "qfm-toxicity-comparable": (
        "The authors report a toxicity screening experiment, a binary classification on a dataset of 286 molecules, "
        "that achieved an F1-score of 60.4±5.1%, on par with the best classical kernels."),
    # g01: the exponents the text layer flattens, written out.
    "qsvm-dual-complexity": (
        "The authors show that the dual QSVM training problem can be solved in O(M^4.67/ε^2) quantum circuit "
        "evaluations (the source prints O(M 4.67/ε2)), where M denotes the size of the data set and ε the solution "
        "accuracy."),
    "qsvm-primal-pegasos-complexity": (
        "The authors prove, under an empirically motivated assumption, that the kernelized primal problem can be "
        "solved in O(min{M^2/ε^6, 1/ε^10}) evaluations (the source prints O(min{M 2/ε6, 1/ε10})) by a "
        "generalization of the classical Pegasos algorithm."),
}
CONTEXT_FIX: dict[str, str] = {}  # an assertion's context where the reader's did not fit
DROP: dict[str, str] = {}  # an assertion not entered, with the reason
VENDOR_DESCRIPTIONS: set[str] = {  # a vendor's description of its own product (MODERATE), not a result
    "limix-design-and-license", "limix-2-design-synthetic-pretraining", "toolkit-composition", "no-data-movement-claim",
    "ronkko-iqm-spark-description",
}
HIGH_REVIEWED: set[str] = {  # every HIGH grade, named after the coordinator's read
    # g25
    "hoppner-instance-threshold", "hoppner-calibration-assumption", "hoppner-datasets-design", "alves-fifar-dataset",
    "alves-baseline-limitation", "alves-synthetic-experts-limit", "fey-rdl-blueprint", "fey-relbench-scope",
    "cheng-review-scope", "kabane-dataset", "lyu-rectified-logits", "lyu-margin-rebalancing", "lyu-scope-limits",
    "qu-tabicl-limitations", "lachi-lightrdl-scope",
    # g26
    "fraudtransformer-evaluation-set-undersampled", "fraudtransformer-deterministic-runs",
    "ggbm-downside-dimension-expansion", "conformal-gt-finite-sample-guarantee", "conformal-gt-conservative",
    "mild-imbalance-is-over-experts", "tfm-scope-limit", "qedc-suite-introduced", "qedc-limitations", "not-exhaustive",
    # g27
    "qkm-semi-artificial-setup", "qkm-limits-not-conclusive", "qpu-hpc-two-integration-paths", "rand-unknowns-remain",
    "hybridq-integrates-techniques", "hybridq-state-vector-multinode-planned", "kerger-fewer-rounds",
    "kerger-impractical-constants", "aqc-nn-small-models-only", "defi-limitations-crypto-only",
    # g28
    "alonso-fourier-pqc-method", "alonso-training-randomness-limit", "qstar-setup-simulated", "qstar-single-seed-limit",
    "dupont-rigor-future-work", "qmes-noiseless-simulation-scope", "qmes-classical-inference",
    "arute-circuit-size-fidelity", "arute-fidelity-not-directly-computable", "huynh-qiml-definition",
    "ryu-margin-bound-encodings", "ryu-simulation-noise-limit", "akhtyamov-synthetic-no-llm",
    "akhtyamov-no-supervisor-review",
    # g29
    "nfs-same-fourier-space-as-qnn", "tested-regime-scope", "correlated-errors-segment-the-market",
    "policy-effects-ai-and-data-sharing", "stylized-model-scope",
    # g01
    "cd-ansatz-optimization-offline", "qsvm-dual-complexity", "qsvm-primal-pegasos-complexity",
    "qsvm-scope-training-only", "qmlids-setup-backends", "pqc-redundancy-lower-bounds", "pqc-linear-encoding-bound",
    "pqc-bounds-logarithmic-tight", "pqc-concept-only", "qubo-bench-hss-opaque", "dawid-scope-educational",
    "qmlhealth-screening-counts", "rm-kernel-scaling", "rm-experiment-setup",
    # g02
    "west-noiseless-simulation-scope", "west-adv-training-caveat", "gentile-qmla-bath-infeasible",
    "peters-benign-overfitting-fourier-analogy", "peters-concrete-example", "peters-scope-restricted",
    "deng-gbs-setup-jiuzhang", "deng-open-question-better-classical", "khan-qlstm-no-noise", "verdon-qgnn-introduced",
    "verdon-qgnn-four-applications", "verdon-first-explorations-numerical", "innocenti-qelm-effective-measurement",
    "innocenti-qelm-training-analogy", "innocenti-qelm-nonlinearity-from-encoding", "innocenti-qelm-sampling-noise",
    # g03
    "kopczyk-scope", "kopczyk-decoherence-limit", "perlin-mlft-method", "perlin-hardware-errors-neglected",
    "zhang-quddpm-proposal", "zhang-generalization-open", "adcock-scope", "dunjko-review-scope", "xia-linear-only",
    "cimini-setup", "li-scope", "li-simulated-benchmarks", "li-encoding-empirical",
    # g04
    "dalzell-survey-scope-provable", "tacchino-open-problems-scope", "garg-survey-scope", "pelofske-scope-limits",
    "belis-limits-nq4-no-preclusion", "belis-hardware-run-scope", "cheng-hardware-proof-of-concept-scope",
    # g05
    "family1-one-qubit-per-bit-depth-1", "family1-state-not-optimal-for-speedup", "circuits-verified-by-simulation-only",
    "setup-train-on-integrable-limits-vqe-states", "supervised-qcnn-cannot-detect-absent-phases",
    "barren-plateau-mitigation-proof", "hardware-circuit-size-limited-by-gate-infidelity",
    "born-machines-two-vi-methods", "ksd-method-needs-explicit-priors", "no-training-features-of-its-own",
    "noisy-sim-closest-to-hardware", "zx-method-not-complete", "benchmark-hard-timeout-1h",
    "dataset-size-limited-by-quantum-resources",
    # g06
    "qlt-scope-boolean-open-practical", "qkm-benchmark-setup", "qkm-generalizability-limit",
    "qml-slr-selection-94-papers", "qml-slr-validity-single-reviewer", "tnqml-qtn-definition",
    "qek-small-graph-simulation-scope", "fqmci-full-quadratic-advantage", "fqmci-smoothness-requirement",
    "pqa-setup-20-variables", "pqa-tracks-not-comprehensive",
    # g07
    "qrc-dissipation-universality-proof", "qiro-scope-proof-of-concept", "qiro-backtracking-not-scalable",
    "qaoa-study-setup-scope", "qaoa-future-work-tradeoff", "hqpinn-three-qubit-simulated", "hqpinn-3d-still-hard",
    "qfm-proof-of-concept-limits",
    # g08
    "benchmark-scope-simulation", "xqaoa-exact-family", "qdh-trainability-proof", "qdh-classical-simulatability",
    "qtl-no-advantage-claim", "qtl-small-dataset", "qrl-hyperparameter-sensitivity", "abs-platform-scope",
    "abs-adaptivity-emulated", "qpinn-limitations",
    # g09
    "pqc-bilstm-setup", "qelm-fourier-expressivity", "qelm-exponential-concentration",
    "qelm-random-reservoir-unscalable", "qcnn-simulated-only", "vqa-gibbs-proof-of-concept", "qgen-simulation-limits",
    "obppp-complexity", "obppp-limits", "crnn-memory-separation", "crnn-quadratic-only", "svqx-experiments",
    "svqx-complexity-limit",
    # g10
    "liu-scope-single-layer", "neukart-scale-embedded", "neukart-limits-not-optimal", "yang-method-setup",
    "yang-noisy-complexity-exponential", "cimini-method-setup", "cimini-experiment-scope", "gacon-qgt-free-method",
    "gacon-noise-open-questions", "patel-hard-instances", "patel-classical-simulation-no-advantage",
    "rapp-advantage-uncertain",
    # g11
    "qcnn-no-full-dequantization", "qrc-setup-ising-reservoir", "qneuron-setup-and-limit", "qaoa-fs-setup",
    "qaoa-fs-limits", "approx-encoding-hardware-limit", "qbm-poly-gibbs-states", "qbm-pretraining-lowers-bound",
    "qbm-scope-no-hidden-units", "qbm-bounds-loose", "ion-trap-setup", "ion-trap-limited-optimization",
    "nisqrc-hardware-extent", "nisqrc-memory-tradeoff",
    # g12
    "two-qubit-simulator-800-200", "discussion-comparable-more-work", "untuned-defaults-two-datasets",
    "classical-fourier-algorithm-complexity", "scope-clifford-pauli-circuits", "not-a-simulation-no-benchmark",
    "large-classical-still-best", "scope-classical-data-open-questions", "framework-contribution-scope",
    "noise-not-benchmarked", "simulation-only-setup", "no-surpass-unsure-future-work", "quantum-nfl-lower-bound",
    "quantum-bound-stronger-than-classical", "setup-ideal-realisable-pairs", "no-computational-advantage-claimed",
    # g13
    "qbm-hidden-two-methods", "qbm-efficiency-conditional-on-gibbs", "qbm-no-lower-bounds", "wiebe-perspective-scope",
    "varqfs-proof-of-principle", "dqfim-rank-dla-bound", "dqfim-numerical-setup", "shallow-circuit-learning-poly-time",
    "shallow-circuit-depth-limit", "dissipation-tested-examples",
    # g14
    "setup-simulator-only-small-vqc", "lipschitz-bound-trainable-encoding", "generalization-bound-involves-encoding",
    "fixed-encoding-lipschitz-not-tunable", "success-probability-limited", "scalability-open-question",
    "evaluation-setup", "simulation-only-limitation", "noise-suppresses-qfim-eigenvalues",
    "noise-turns-on-null-eigenvalues", "some-noise-cannot-raise-rank", "no-extra-circuits-condition",
    "hardware-run-not-converged", "dataset-and-simulation-setup", "labels-used-for-tuning", "simulation-setup",
    # g15
    "tsp-sizes-and-hardware-limit", "clifford-mapping-gradient-variance", "method-scope-clifford-ansatz",
    "correlated-parameters-open", "simulated-only-future-hardware", "lack-of-data-not-typical-problem",
    # g16
    "qelm-limited-to-12-qubits-simulation", "qelm-hardware-not-tested", "qpk-converges-to-qntk-only-lazy",
    "qpk-simulated-only", "qnn-bagging-fewer-features-limit", "qnn-ensemble-ibm-lagos-run", "mbdf-uniqueness-limit",
    "qtl-six-qubits-simulation", "gqml-scope-tutorial", "gqml-label-invariance-setting", "qgrand-channel-errors-only",
    "qgrand-fault-tolerance-open", "qnn-gp-convergence-proof", "qnn-gp-haar-scope", "qnn-gp-not-all-qnns",
    # g17
    "study-basis-interviews", "not-representative-biased", "limits-qaoa-lih", "scope-ibm-backends",
    "vqml-is-mps-theorem", "dequantization-scope-expressivity", "scope-three-vqe-larger-scale",
    "fidelity-bounds-hamiltonian-norms", "bound-not-tight", "review-27-records",
    # g18
    "rydberg-setup-numerical", "rydberg-topology-limit", "acae-fraud-proof-of-concept-scale",
    "acae-scalability-limit", "qdropout-setup-small", "qdropout-future-hardware", "hybrid-actor-critic-linear-dynamics",
    "qnn-simulator-qubit-limit",
    # g19
    "qp-methodology-ongoing-experiment", "qp-trial-design-sample", "qp-needs-more-evidence",
    "pi-encoding-setup-noiseless", "pi-encoding-no-advantage-guarantee", "smpp-benchmark-setup",
    "qelm-small-systems-scope", "slimqfl-mini-mnist-iid-setup", "slimqfl-open-convergence-noniid",
    "qvit-setup-simulated-params", "qvit-limits-expressiveness-no-hardware", "qlstm-setup-param-counts",
    "qlstm-noiseless-no-nisq-training", "nqe-setup-four-qubit-qcnn", "nqe-open-network-architecture",
    # g20
    "li-dataset-and-noise-free-baseline", "olivera-limits-and-open-questions", "sgarbas-scope-narrow",
    "shin-qmine-proposal", "shin-qmine-simulation-only", "umeano-open-challenges", "consiglio-vsv-proposal",
    "consiglio-vsv-simulation-scope", "consiglio-vsv-exponential-parameters",
    # g21
    "pegasos-qka-simultaneous", "qcbm-linear-connectivity-no-swap",
    "imdb-setup-150-samples-5-qubit", "random-layer-universal-observable",
    "random-layer-extra-cost", "random-layer-scope-small-systems", "photonic-option-pricing-three-values",
    "copy-complexity-defined", "erm-generally-inapplicable-quantum-data", "no-quantum-advantage-discussion",
    "findings-specific-feature-space-size",
    # Fresh-eyes review, 2026-10-22: a measured negative result from one study is empirical, not a stated limit,
    # so qudit-hardware-limit, fischer-residual-bias-large-systems, qcbm-scaling-limit, qsvr-hardware-auc-050
    # and ewaniuk-weak-nonlinearity-trainability are LOW.
    # g22
    "ewaniuk-coupler-model-setup", "guo-qlof-speedup", "guo-qram-assumption",
    "guo-choice-of-k-out-of-scope", "incudini-test-protocol", "incudini-limited-configuration", "lamata-review-scope",
    "peixoto-qubit-limit-setup", "perron-quest-workshop-scope", "poggel-implementation-scope",
    "poggel-metric-drawbacks",
    # g23
    "cnn-limit-weak-correlation-only", "review-scope-search-window", "vqe-limit-simple-error-mitigation",
    "vqe-limit-subspace-search-efficiency", "embedding-framework-mgo-vacancy", "embedding-limit-error-compensation",
    "qctf-four-steps", "qctf-limit-untested", "rydberg-3sat-experiment", "rydberg-limit-technical-limits-unknown",
    # g24
    "lee-qcnn-scope-binary-simulation", "liu-qpf-practical-limits", "mathur-qfl-inclusion-criteria",
    "michel-dave-scope-ideal-processor", "michel-dave-limits-runtime-errors", "mykhailova-course-scope",
    "mykhailova-limits-testing-and-evaluation", "neumann-dqml-proposal", "neumann-dqml-limits",
    "nokkala-benchmark-tasks-only", "rodriguez-nqk-single-kernel-matrix", "rodriguez-nqk-scope-simulation",
}

PROVED_OR_OWN = ("Started HIGH: a result proved in the paper, or the paper's own statement of its setup, scope or "
                 "limits, read in context")
EMPIRICAL = "Started LOW: an empirical result from one study. NOT upgraded"
AUTHOR_CLAIM = "Started LOW: the authors' own claim, not tested in the paper. NOT upgraded"
CITED = "Started LOW: a claim the source cites from other work, not tested in it. NOT upgraded"


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def groups_of(task: str) -> list[str]:
    return sorted(g for g, v in ledger()["groups"].items() if v["task"] == task)


def load_groups(task: str) -> list[tuple[str, dict]]:
    """Every paper of the task's groups; refuses a reader file whose records are not its group's."""
    out, L = [], ledger()
    for g in groups_of(task):
        papers = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))["papers"]
        want = {r["record_id"] for r in L["groups"][g]["records"]}
        got = [p["record_id"] for p in papers]
        if set(got) != want or len(got) != len(want):
            raise ValueError(f"group {g}: reader file records {sorted(set(got) ^ want)} differ from the ledger")
        out += [(g, p) for p in papers]
    return out


def quotes_of(a: dict) -> list[str]:
    qs = list(a["quotes"])
    for old, new in QUOTE_EDITS.get(a["id_suggestion"], []):
        hits = [i for i, q in enumerate(qs) if old in q]
        if not hits:
            raise ValueError(f"{a['id_suggestion']}: the quote text to replace is not there: {old[:60]!r}")
        if new is None:
            del qs[hits[0]]
        else:
            qs[hits[0]] = qs[hits[0]].replace(old, new)
    return qs + EXTRA_QUOTES.get(a["id_suggestion"], [])


def certainty(aid: str, a: dict) -> tuple[str, str]:
    if a["claim_type"] == "vendor-self-claim":
        if aid in VENDOR_DESCRIPTIONS:
            return "moderate", f"{f80.VENDOR_START}. Not upgraded: a description of the product, not a result"
        return "low", (f"{f80.VENDOR_START}. DOWNGRADED one level: a result or claim the vendor reports about its "
                       "own product, not independently checked")
    if aid in HIGH_REVIEWED:
        return "high", PROVED_OR_OWN
    if a["kind"] == "cited":
        return "low", CITED
    if a["kind"] == "shown":
        return "low", EMPIRICAL
    return "low", AUTHOR_CLAIM


def anchor_safe(anchor: str) -> str:
    # A quote mark inside a label would break the quote pattern (Task D finding).
    return anchor.replace('"', "'")


def assertions(task: str) -> list[tuple[str, AssertionRecord, str, dict]]:
    tag, out = TAGS[task], []
    for g, p in load_groups(task):
        rid = p["record_id"]
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            if aid in DROP:
                continue
            cert, reasons = certainty(aid, a)
            anchor = anchor_safe(a["anchor"])
            out.append((g, AssertionRecord(
                id=aid, value=" ".join((VALUE_REPLACE.get(aid) or a["value"]).split()),
                provenance=f"{rid}, {anchor}",
                citation_context="; ".join(f'"{q}" ({anchor})' for q in quotes_of(a)),
                evidence_tag="N/A", context=CONTEXT_FIX.get(aid) or a["context"], certainty=cert,
                certainty_reasons=reasons, fidelity=a.get("fidelity") or "scoped", derivation="extracted",
                claim_type=a["claim_type"],
                search_scope=("the paper's own text, as read" if a["claim_type"] == "absence" else None),
                updated=TODAY, updated_reason=(f"{TODAY} ({tag}): extracted from {rid}; first-pass read by a "
                                               "subagent, every quoted passage read in context by the coordinator")),
                rid, p))
    return out


def verify(task: str) -> list[tuple[AssertionRecord, str, dict, object]]:
    """Every quote verbatim in its source, every coordinator edit resting on
    named passages, and every figure in a value in its own quotes, BEFORE
    anything is written (section 31)."""
    texts: dict[str, str] = {}
    out = []
    for _, a, rid, p in assertions(task):
        quotes = QUOTE.findall(a.citation_context)
        if a.citation_context.count('"') != 2 * len(quotes):
            raise ValueError(f"{a.id}: a quote mark the quote pattern does not parse")
        text = texts.setdefault(p["file"], plain(source_text(p["file"])))
        verified = require_verbatim(a.id, a.citation_context, text)
        if a.id in VALUE_REPLACE:  # the replaced value's passages are the quotes printed with it
            require_edit_basis(a.id, a.value, quotes, text)
        if a.id in QUOTE_EDITS:
            require_edit_basis(a.id, None, [n for _, n in QUOTE_EDITS[a.id] if n] or quotes, text)
        if numbers := unquoted_numbers(a):
            raise ValueError(f"{a.id}: figures {numbers} are not in its own quotes")
        out.append((a, rid, p, verified))
    return out


def unquoted_numbers(a: AssertionRecord) -> list[str]:
    # A digit closing a hyphenated name (LimiX-2) is a name, not a figure, as in F89's test.
    quoted = " ".join(plain(q) for q in QUOTE.findall(a.citation_context))
    return [n for n in re.findall(r"(?<![\w.,])(?<![A-Za-z]-)\d+(?:[.,]\d+)?", plain(a.value))
            if not re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", quoted)]


def read_detail(g: str, p: dict) -> str:
    detail = (f"first pass, in part: {p['partial_detail']}" if p.get("read_extent") == "partial"
              else "first pass, the whole source") + f" (Sonnet 5.5 reader, group {g.upper()})"
    if p.get("version_note"):
        detail += f"; version: {p['version_note']}"
    return detail


def apply_changes(conn, task: str) -> list[str]:
    tag, checked = TAGS[task], verify(task)
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    if task == "G":
        if set(NO_COPY) != set(ledger()["no_copy"]):
            raise ValueError("NO_COPY differs from the ledger's no_copy")
        for rid, why in sorted(NO_COPY.items()):
            reason = f"{TODAY} ({tag}): selected for reading and NOT read: {why}; on the hand-download list"
            if rid in RETRACTED:
                reason = f"{TODAY} ({tag}): NOT read and NOT for the hand-download list: {why}"
            stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
            if reason not in stored:
                append_updated_reason(conn, rid, reason, TODAY)
                log.append(f"no copy {rid}")
    for g, p in load_groups(task):
        rid, detail = p["record_id"], read_detail(g, p)
        have = {(r[0], r[1], r[2]): r[3] for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,))}
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        path = p["file"].replace("/", "\\")
        if path.lower() not in {s.lower() for s in recheck.local_paths(access or "")}:
            note = f"Local copy {f80._sha(Path(path))}, recorded {TODAY} ({tag})"
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ? WHERE record_id = ?",
                         (f"{access} | {path}" if access else path,
                          f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({tag}): local copy added to access", TODAY)
            log.append(f"access {rid}")
        kept = [a for a in p["assertions"] if a["id_suggestion"] not in DROP]
        if not kept:  # read, and nothing in it bears on a context: the reason, not a tier change
            if (SUBAGENT_READER, TODAY, "subagent") not in have:
                add_read(conn, rid, SUBAGENT_READER, TODAY, "subagent", detail)
                why = p.get("why_not") or "; ".join(DROP[a["id_suggestion"]] for a in p["assertions"])
                append_updated_reason(conn, rid, f"{TODAY} ({tag}): read at first pass and NOT entered: {why}", TODAY)
                log.append(f"refuse {rid}")
            continue
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            ctx = p["bears_on_context"]
            if ctx not in contexts:
                raise ValueError(f"{rid}: applicability context {ctx!r} is not a context")
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, f"{p['what_it_is'].rstrip('.')} -- first-pass read"))
            log.append(f"applic {rid} [{ctx}]")
        for reader, extent, det in ((SUBAGENT_READER, "subagent", detail), ("Claude", "partial", COORDINATOR_DETAIL)):
            if (reader, TODAY, extent) not in have:
                add_read(conn, rid, reader, TODAY, extent, det)
                log.append(f"read   {rid} [{reader}, {extent}]")
            elif have[(reader, TODAY, extent)] != det:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? AND read_on = ? "
                             "AND extent = ?", (det, rid, reader, TODAY, extent))
                log.append(f"update read {rid} [{reader}]")
        if tier != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{TODAY}, Claude, read every quoted passage in context and checked every quote and figure against "
                "the source; first pass by a subagent"))
            log.append(f"tier   {rid} -> read")
    for a, rid, _, verified in checked:
        if a.context not in contexts:
            raise ValueError(f"{a.id}: context {a.context!r} is not a context")
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, f"{TODAY} ({tag}): corrected to the script's current "
                                          "text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    task = args[args.index("--task") + 1]
    kept = assertions(task)
    ids = [a.id for _, a, _, _ in kept]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    with connect(DB_PATH) as conn:
        clash = [i for i in ids if conn.execute(
            "SELECT 1 FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ? AND "
            "r.provenance NOT LIKE ?", (i, f"%{dict((a.id, rid) for _, a, rid, _ in kept)[i]}%")).fetchone()]
    if dupes or clash:
        print(f"duplicate assertion ids: {dupes}; ids already held by another source: {clash}")
        return 1
    if "--apply" not in args:
        checked = verify(task)
        for a, _, _, _ in checked:
            validate_assertion(a)
        papers = load_groups(task)
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"{len(kept)} assertions from {len(papers)} records "
              f"({sum(1 for _, p in papers if not [a for a in p['assertions'] if a['id_suggestion'] not in DROP])} "
              f"with none); {len(NO_COPY) if task == 'G' else 0} with no copy. Every quote verbatim, every edit "
              "on named passages, every figure in its quotes. DRY RUN: "
              "nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, f"{TAGS[task]} reads entered")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, task)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
