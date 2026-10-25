#!/usr/bin/env python3
"""Sprint 13 Task F (F112, the F57 release): the first-pass reads entered, one ledger.

`manifests/sprint13_read_ledger.json` gives every record this task reads to
exactly one group (g01 to g100, the 806-record slice less 11 with no copy).
One Sonnet 5.5 reader per group wrote `manifests/sprint13_reads/group_<g>.json`
(kept verbatim) under `READER_PROMPT.md`. A reader file whose records are not
exactly its group's is refused, so no two reads touch one record. The reads
are entered in two halves (g01 to g50, g51 to g100), each with its own
fresh-eyes review; the 11 no-copy records go with the first.

HOW THE SOURCES WERE READ (ADR-0005 A4: a subagent's read alone never
qualifies `read`): as Sprint 12 (`sprint12_reading.py`). The coordinator
checked every quote against the source text by script
(`require_verbatim`, with the value's figures) and read every value against
its quoted passages in context. QUOTE_EDITS, EXTRA_QUOTES, VALUE_REPLACE,
CONTEXT_FIX, DROP and HIGH record that read.

CERTAINTY (INTAKE_WORKFLOW.md sections 45 and 49): HIGH only through
`store.grading.high_grades`, each HIGH id with its basis and where the paper
settles it. Every LOW names its reason through `store.grading.low_grade`:
a measured result, an authors' claim, a cited claim, a statement about the
field, or a theoretical result (THEORY_LOW, with its cause). A vendor's
description of its own product starts MODERATE and a vendor's result LOW.
The reader's `certainty_suggestion` is never used. The reader's
`result_type` is a second opinion on the LOW reason: where it says
"theoretical" or "field", or the value's words name a proof or a bound, and
the coordinator's reason differs, the coordinator names the case
(MEASURED_DESPITE or NOT_FIELD) with why; a test fails otherwise.

    python scripts/sprint13_reading.py --half 1            # dry run: every quote checked; nothing written
    python scripts/sprint13_reading.py --half 1 --apply    # verified backup first
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
from store.grading import grade, high_grades, low_grade  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_verified_assertion,  # noqa: E402
                          set_tier, sync_verified_assertion, validate_assertion)
from store.quotes import QUOTE, plain, require_edit_basis, require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-25"
TAG = "Sprint 13 Task F, F112"
LEDGER = ROOT / "manifests" / "sprint13_read_ledger.json"
READS_DIR = ROOT / "manifests" / "sprint13_reads"
HALVES = {"1": (1, 50), "2": (51, 100)}
SUBAGENT_READER = f80.SUBAGENT_READER

COORDINATOR_DETAIL = ("every quoted passage with about 220 characters each side, every quote checked verbatim and "
                      "every figure in a value checked against its quotes by script; the rest of the paper not "
                      "read by the coordinator" + f80.f78.ABSENCE_NOTE)

# Exact source characters a reader's quote missed, looked up in the source text: (old, new or None to drop).
QUOTE_EDITS: dict[str, list[tuple[str, str | None]]] = {
    # g04: quotes cut before what their values say; the source's own continuation
    "nigatu-93x-speedup": [("up to 93x over classical optimizers like", "up to 93x over classical optimizers like "
                                                                        "Nelder-Mead")],
    "patel-qbm-convergence-proof": [
        ("rigorously prove that it converges to an", "rigorously prove that it converges to an ε-approximate "
                                                     "stationary point of the energy function optimized over "
                                                     "parameter space")],
    "patel-qbm-scope-thermal-states": [
        ("most pertinent for the situation in which low-temperature thermal states of",
         "most pertinent for the situation in which low-temperature thermal states of H are computationally "
         "difficult to generate but thermal states of G(θ) are not")],
    "patel-qbm-barren-plateau-open": [
        ("to determine whether the landscape of the objective function",
         "to determine whether the landscape of the objective function f (θ) suffers from the barren-plateau "
         "problem")],
    # g05
    "qdataset-simulated-not-hardware": [
        ("which would be common across", "which would be common across a variety of laboratories and experimental "
                                         "setups")],
    # g06
    "qsaf-not-quantum-mechanics": [("rather than a contribution", "rather than a contribution to quantum mechanics")],
    # g09: the quote does not say which method gave 83 percent, or on which dataset
    "kmeans-su2-accuracy": [("which produced an accuracy of 83 percent", None)],
    # g12: a measured figure the reader put in a scope or setup assertion; the assertion keeps its scope
    "bincoletto-scope-hydrogenic-only": [("the largest amount of energy outliers occur for the H12 system", None)],
    "bonan-experiment-setup": [("over 90% accuracy of classfication on the test dataset", None)],
    # g58: measured observations inside a scope
    "dibom-simulation-scale": [("the computation takes about 1 hour on an 8-core", None)],
    "cepaite-scale-and-noise": [("we see noise from the device begin to take over", None)],
    "chen2018-simulated-exact-probabilities": [("with an error within 3%", None)],  # g59
    "gsa-role-of-qpu": [("The error increases with increasing bond length", None)],  # g68
    # g13: a cited proof the reader put in a scope assertion
    "scope-single-round-algorithms": [("Hastings proves that a classical local tensor algorithm outperform", None)],
    # g14: quotes cut mid-word or mid-phrase; the source's own continuation
    "gbs-cvar-vqe-beats-vqe": [  # the drop first: the edited quote holds the dropped one's words
        ("achieving almost perfect success rates for", None),
        ("We observe that employing CVaR outperforms VQE signif",
         "We observe that employing CVaR outperforms VQE significantly, achieving almost perfect success rates for "
         "α = 0.01 or 0.1.")],
    "hwaware-qsvm-9123": [("discovers a 12-gate circuit using exclusively IBM",
                           "discovers a 12-gate circuit using exclusively IBM native gates")],
    # the column's name is in double quotes in the source, which a citation's quote cannot carry
    "moe-fraud-dataset-setup": [("Since we opted to use cross-validation in our benchmark, we decided to remove the",
                                 None)],
    "kmeans-quantum-quadratic-small-regime": [
        ("we showcase a quadratic improvement in the", "we showcase a quadratic improvement in the ε dependence "
                                                       "compared to our classical algorithm in the small ε regime"),
        ("the quantum algorithm will do better than the classical algorithm when", None)],
    "safe-qml-value-not-accuracy": [
        ("lies not in surpassing classical methods in peak accuracy",
         "lies not in surpassing classical methods in peak accuracy, but in providing a compact, structured hypothesis "
         "class that supports SAFE learning objectives")],
    # g15
    "demidik-datasets": [("we consider the task of classifying 32 subjects into two groups",
                          "we consider the task of classifying 32 subjects into two groups: relapsed non-transformed "
                          "FL (nFL) and transformed FL (tFL)")],
    # g17
    "ferber-or-query-model": [("induces at least one edge in G.", None)],  # the extra quote below holds it whole
    "fleury-qiskit-agreement": [("gives a quantum circuit that meets the quantum circuit generated by application of "
                                 "algorithm 1.", None)],  # its comparison is with algorithm 1, not Qiskit
    # g18: quotes cut before what their values say
    "gandhi-dqgp-srtm-nrmse": [("DQGP achieves 32.4%", "DQGP achieves 32.4% ± 22.7% lower NRMSEtest than FACT-GP")],
    "gandhi-dqgp-synthetic-nrmse": [("For the synthetic dataset, DQGP achieves on average 47.0%",
                                     "For the synthetic dataset, DQGP achieves on average 47.0% ± 14.0% lower "
                                     "NRMSEtest than FACT-GP")],
    "gerlach-mapf-first-algorithms": [("suggest that our approach dominates previous QUBO",
                                       "suggest that our approach dominates previous QUBO formulations and "
                                       "state-of-the-art MAPF solvers")],
    "gharibyan25c-classical-compare": [("slightly worse than a convolutional neural network",
                                        "yielding an accuracy of 0.94. Notably, we find that this is slightly worse "
                                        "than a convolutional neural network")],
    # g19
    "imps-circuits-t-count-reduction": [("we similarly find an advantage, with up to a 5.2",
                                         "we similarly find an advantage, with up to a 5.2× reduction in T -count")],
    "qwgan-bioprocess-setup": [("is equal to 20.", None)],  # the quote does not say what equals 20
    "distributed-qelm-linear-resource-reduction": [
        ("this corresponds to a linear improvement in the required reservoir dimension",
         "this corresponds to a linear improvement in the required reservoir dimension, since for large Nq-qubit "
         "inputs it scales as 2Nq /n, compared to the 2Nq for the single threelayer architecture")],
    # g42: a measured AUC inside a stated limit
    "daqc-qubit-limit": [("On the harder 10-class tasks, DAQC maintains high AUC", None)],
    # g26
    "open-problem-two-qubit": [("it is an interesting open problem to identify the minimal type of pre-processing beyond",
                                "it is an interesting open problem to identify the minimal type of pre-processing beyond "
                                "PBTq needed for non-classical teleportation of two-qubit states")],
    # g25: a measured finding inside a scope statement
    "lstm-scope-eight-qubits": [("Crucially, the LSTM improved classification of ambiguous boundary cases", None)],
    "distributed-qelm-polynomial-k-reservoirs": [
        ("any target exhibiting a nonlinearity of order k can be reconstructed using k reservoirs",
         "For polynomial targets, it has been shown that any target exhibiting a nonlinearity of order k can be "
         "reconstructed using k reservoirs, although specific targets can be recovered with fewer reservoirs")],
    # Fresh-eyes review of cec6020: a measured result inside a stated limit leaves the limit with its quote
    # (half 2's g51 to g69, re-audited by the same rule, are the last five)
    "photonic-classifier-limit-below-10-photons": [("we observed a noticeable drop in accuracy", None)],
    "atchade-limits": [("we have also detected some limitations", None)],
    "rydberg-sim-not-hardware": [("the performance of the QuEra processor was adequate", None)],
    "docking-12-qubit-local-optima-limit": [("our investigation into a 12-qubit system", None)],
    "qasa-limits-simulated-training-few-seeds": [("Most pairwise t-tests therefore do not reach", None)],
    "gqsp-optimization-limit": [("It is crucial to mention the poor performance", None)],
    "medmnist-not-beating-classical": [("do not outperform the best-performing classical ML model", None)],
    "mcquack-stated-limitations": [("it does not outperform simple classical baselines", None)],
    "qcbm-stated-limitations": [("the KL divergence remains high after training", None)],
    "ippdt-limits": [("the full-depth baseline can outperform the progressive strategies", None)],
    "annealer-limits": [("generation of the D-Wave annealers is far from perfect", None)],
    "nakano-high-temperature-limit": [("classical proposals are sufficiently efficient", None)],
}
EXTRA_QUOTES: dict[str, list[str]] = {
    # g01: a proved result's conditions, which the reader's quotes left out
    "dd-theorem-peak-at-interpolation": [
        "Consider a Lipschitz continuous quantum feature map ρ with p linearly independent dimensions, and consider "
        "a linear regression problem in the corresponding feature space.",
        "are d-dimensional i.i.d. Gaussian normal random samples"],
    "dd-corollary-rdm-peak-linear-in-qubits": [
        "Consider a quantum kernel model based on the RDM projection of an L-Lipschitz continuous quantum feature map "
        "ρ(x) on n qubits.",
        "d-dimensional i.i.d. Gaussian random samples"],
    "lstm-optimizer-time-per-pass-scaling": [
        "If A is a gradient-dependent algorithm the the total time for one full pass (forward and backward) takes"],
    # g02: what the reader's quote left unnamed
    "sbqe-fashion-mnist-accuracy": ["90.25% ± 0.18% on MNIST (exceeding amplitude encoding by 2.1 percentage points"],
    "larose-variational-fewest-resources": ["is a primary bottleneck for quantum Krylov and for QPE"],
    # g03
    "ionq-hardware-results": ["ultimately reaching large optimal solution probabilities of ≳ 0.5 with 24 or fewer qubits"],
    "random-search-baseline": ["was searched for one hour by random search, and the number of quantum circuits seen "
                               "during that time was used to estimate the running time of the entire search"],
    # g04
    "nigatu-93x-speedup": ["as problem dimensionality increases"],
    "okumura-discretization-limit": ["Moreover, this operation should be performed cautiously because it increases "
                                     "the number of quantum bits and computational complexity."],
    "patel-qbm-convergence-proof": ["polynomial in ε−1, the number of parameters, and the norm of the Hamiltonian "
                                    "being optimized"],
    # g05
    "gqsim-synthetic-separation": ["The figure shows that the average distance between samples in classes is well "
                                   "separated for their corresponding classes in X space."],
    # g11: the subject of the defended result, item 8 (the source's dashed aside left out)
    "physical-hamiltonians-embed-universal": ["8. Proving that physically relevant Hamiltonians"],
    # g12: Definition 6's clause; pdftotext drops the weight and the states' symbols
    "bonan-lsp-definition": ["then for any ∈ [0, 1], 1 + (1 − ) 2 is classified into the same class too."],
    # g14
    "gbs-local-minima-failures": ["For α = 0.25 and N = {12, 16}, the fraction of successful runs decreases."],
    "hwaware-qsvm-9123": ["Evaluated on the UCI Breast Cancer Wisconsin dataset"],
    "safe-qml-simulator-scope": ["We deliberately do not report computational time comparisons across models."],
    # g15: what "this effect", the data and the method were
    "das-jc-model-limits": ["in the dispersive limit of the JC model, the cavity",
                            "dissipation channel can, in principle, induce an effective qubit decay."],
    "daskin-qlstm-simulation": ["The noisy sine data is generated by"],
    "daskin-vqpm-scaling": ["deep-circuit QAOA configurations at small qubit numbers quickly diminish"],
    "daskin-vqpm-noise": ["For a 12-qubit QUBO problem(generated with random seed 42)"],
    # g16
    "hva-entanglement-resource": ["Conversely, in the problem-inspired Hamiltonian Variational Ansatz (HVA)"],
    # g17
    "ferber-or-query-model": ["When we submit a set S of vertices to the oracle, it tells us whether or not S induces "
                              "at least one edge in G.", "(we may query subsets in superposition)"],
    "flores-garrigos-spambase-hardware-subset": ["classification performance compared to using all features."],
    # g18
    "gandhi-dqgp-srtm-nrmse": ["Aggregating the improvements across the four SRTM environments"],
    "gharibyan25c-sim-accuracy": ["Our largest model involved 16 blocks each consisting of 14 qubits and 6 "
                                  "variational processing layers"],
    # g19
    "qnbm-linearized-model-efficient-sampling": ["In fact, this construction is precisely a Bayesian network",
                                                 "Clearly the same construction does not work for the non-linear QNBM"],
    "distributed-qelm-linear-resource-reduction": ["From the analytical expressions in Eqs. 5 and 8"],
    "q2sar-auc-vs-gradient-boosting": ["demonstrating that a quantum-enhanced model can outperform a strong classical "
                                       "baseline"],
    # g25
    "qrf-open-question": ["If we forecast a portion of the range between the maximum and the minimum"],
    # g46: section 5 places the abstract's 98.00% on the training set
    "wang25h-accuracy": ["Moreover, the RQNN has higher accuracy (98.00%) on the training set"],
    # g27
    "a-graph-future-scope": ["for specific graph families, extensions to multipartite settings"],
    "laneve-open-epsilon": ["This statement seems to suggest there exists an algorithm which directly solves the "
                            "problem with"],
    # Fresh-eyes review of cec6020: the passage a value rests on, which the reader's quotes left out
    "qaoa-xy-turnover-limitation": ["than the classical baselines"],
    "single-shot-definition": ["is identical to the majority label"],
    "exact-learning-definition-threshold": ["An algorithm is said to be an exact learner for", "it outputs a hypothesis",
                                            "with high probability"],
    "gross-memory-limit-large-n": ["Note that the resulting optimal measurement operator",
                                   "Explicitly constructing and storing"],
    "open-problem-limit": ["proving or disproving the statement", "no classical algorithm dequantizes",
                           "sparse Hermitian"],
    "stationary-noise-breaks-exchangeability": ["Without exchangeable scores, we cannot assert that the rank of the "
                                                "test score is uniformly distributed"],
}
VALUE_REPLACE: dict[str, str] = {  # the coordinator's read; each replacement says only what its quotes say
    # g01
    "mqt-molecules-and-qubit-counts": ("The authors state that they employ the Bravyi-Kitaev mapping for H2 (8 qubits), "
                                       "LiH (12 qubits) and BeH2 (14 qubits), and the Jordan-Wigner transformation for "
                                       "H4 (8 qubits)."),
    "graph-stabilizer-code-bijection": ("The thesis proves that every stabilizer code is essentially uniquely "
                                        "represented by an encoder-respecting graph, and conversely, that this "
                                        "representation is in bijection with tableaus, and gives an efficient "
                                        "compilation algorithm that transforms tableaus into graphs."),
    # g02: "DisCoCat" is not in the quotes
    "qrnn-text-categorization": ("The authors report that both QRNN models achieve an accuracy of 100% on the MC "
                                 "text task (130 sentences, 100 for training and 30 for test), much better than the "
                                 "syntactic analysis-based quantum model they cite; the table row reads 100% 100% "
                                 "100% 79.8%."),
    # g03: the reader's quote dropped what was reached; the 169 hours are an estimate from one hour of search
    "ionq-hardware-results": ("The authors report hardware runs on IonQ devices reaching optimal-solution "
                              "probabilities of ≳ 0.5 with 24 or fewer qubits and 0.19 with 28 qubits, with the "
                              "32-qubit instance terminated early but still sampling the optimal solution."),
    "random-search-baseline": ("The authors report that random search, run for one hour and extrapolated, took about "
                               "169 hours to generate a quantum circuit with four qubits and a quantum cost of 6, "
                               "which they use as a baseline for how hard synthesis is."),
    # g04
    "okumura-discretization-limit": ("The authors state that the coarseness of the discretization must be fine to "
                                     "compute true predictions from the inverse transform, and that this operation "
                                     "should be performed cautiously because it increases the number of quantum bits "
                                     "and computational complexity."),
    "patel-qbm-convergence-proof": ("The authors state that they rigorously prove their algorithm converges to an "
                                    "ε-approximate stationary point of the energy function, using a number of "
                                    "samples polynomial in the inverse accuracy, the number of parameters, and the "
                                    "norm of the Hamiltonian."),  # the text layer's ε−1 is ε to the power −1
    # g05: "separated the classes" said more than the reader's quotes
    "gqsim-synthetic-separation": ("The authors report that on a synthetic image data set with left and right pixels "
                                   "blocked, the average distance between samples is well separated for their "
                                   "classes, and state that they verified this numerically for all points in X."),
    # g06: the reader's value added a method its quote does not name
    "noise-study-scope": ("The authors state that they investigate the impact of quantum noise on various QML "
                          "algorithms applied to a genomic sequence dataset."),
    # g07: each value said more than its quotes
    "qelm-mnist-scope": ("The authors state that they performed numerical experiments using the MNIST dataset with "
                         "their MPS-based QELM for classification, and that, looking ahead, it will be important to "
                         "explore how this algorithm can be applied more widely."),
    "vqa-barren-plateau-mcclean": ("The author states, citing McClean and colleagues (2018), that the chance that the "
                                   "gradient is arbitrarily close to zero for a random point grows exponentially with "
                                   "the number of qubits and the number of parameters."),
    "sturm-dwave-quality-drops": ("The authors report that on the D-Wave annealer, again, the solution quality "
                                  "decreases with the problem size, which they call a clear limit to the usability "
                                  "of quantum annealers for industry relevant problems."),
    "sweke-scope-regression": ("The authors state that their short note shows that, for a wide range of instances, "
                               "this approach can be simplified."),
    "hubbard-three-qd-accuracy": ("The authors report an accuracy of 10% for both tunnelling parameters t within the "
                                  "same number of iterations as used for the two-QD system."),
    "thabet-small-gain": "The authors report a small gain in performance compared to state-of-the-art models.",
    # g08: each value named a dataset, a scope or a method its quotes do not
    "spinchain-changepoint": ("The authors report that the spin chain Hamiltonian framework outperforms the other "
                              "methods in detecting mean jump and variance jump changes."),
    "spinchain-clustering": ("The authors report that the spin chain Hamiltonian appears to offer better TS "
                             "clustering when compared with the DWT and QIPF frameworks."),
    "dpm-carleman-truncation-limit": ("The authors state that the truncation error of quantum Carleman linearization "
                                      "is difficult to control analytically, and that they do not yet have a "
                                      "rigorous bound for it."),
    "qel-simulation-setup": ("The authors state that in their simulation MNIST digits are used as the dataset, and "
                             "that 20 quantum base learners of 4-qubits are combined."),
    # g09: each value named a device, a baseline, a dataset or a regime its quotes do not
    "qracle-headline-gains": ("The authors report that Qracle achieves a reduction in initial loss of up to 10.86, "
                              "decreases optimization steps by up to 64.42%, and gives up to a 26.43% reduction in "
                              "SMAPE, with all results averaged over the validation set of each application."),
    "sequel-scaling-exponent": ("The authors report that their quantum training achieves a higher scaling exponent "
                                "than classical backpropagation (1.01 vs. 0.78), and an exponent of 0.64 for "
                                "equilibrium propagation training."),
    "kmeans-su2-accuracy": ("The authors report that the SU2 feature map yielded an accuracy of 88.6% on the Iris "
                            "dataset and 91.0% on the breast cancer dataset."),
    "pulsed-outperforms-gate": ("The authors report that the pulse-based model consistently outperforms its gate-based "
                                "counterpart in test accuracy and generalization under equivalent noise, and retains "
                                "useful accuracy at depolarizing probabilities where the gate-based model has degraded "
                                "to near-random performance."),
    "radar-qsvm-vs-svm": ("The authors report that the classical SVM achieves 98.52% accuracy using all 15 extracted "
                          "micro-Doppler features, and the QSVM 94.81% with only 4 features obtained through PCA."),
    "radar-hardware-fidelity": ("The authors state that IBM Fez consistently outperforms IBM Torino in fidelity, "
                                "entropy and noise resilience, and describe the higher fidelity as an increase from "
                                "approximately 89% to 94%."),
    "hqk-quantum-data": ("The authors report that, for synthetic quantum data, their method consistently outperforms "
                         "the classical Gaussian kernel."),
    "fin-ann-better-midrange": ("The authors report that the classical ANNs performed slightly better than the QNNs, "
                                "with higher AUC and accuracy, and conclude that classical models retain an advantage "
                                "on mid-range cross-asset features."),
    "fin-qlstm-regimes": ("The authors report that, in a live trading simulation across four market regimes of the "
                          "S&P 500, the QLSTM improves risk-adjusted returns in two of the four, and state that the "
                          "QLSTM underperforms economically."),
    # g10: "compressed" is not in the quote
    "qsrf-matches-baselines": ("The authors report that a 100-tree QsRF trained on these codes matches full-feature "
                               "baselines on ICM-150/500."),
    # g11: each value said more than its quotes (a proof, a consequence, a graph family, a simulation)
    "no-spam-robustness": "The authors state that it would be desirable to make their protocols robust to SPAM noise.",
    "fourier-expansion-is-etk": ("The authors state that the finite Fourier expansion of any quantum kernel can be "
                                 "written directly as an ETK contraction, with the ETK entries given precisely by the "
                                 "Fourier coefficients."),
    "qfi-entropy-depth-reduction": ("The authors report measuring high QFI and entropy in the range of 0.84-1.0, with "
                                    "depth and gate count reduction by 20-86%."),
    "qcmrf-beats-agnostic-on-random-graphs": ("The authors report that their QCMRF models reach better performance "
                                              "than the problem-agnostic QCIBMs while significantly reducing the "
                                              "number of trainable parameters, since they exploit the sparsity of the "
                                              "graph."),
    "exact-model-via-sn-qft": ("The authors describe a quantum algorithm that encodes a probabilistic model over "
                               "permutations into the amplitudes of a quantum state by making use of the QFT over the "
                               "symmetric group."),
    "hamiltonian-complexity-conjectured": ("The author states that anticipated computational resources to determine "
                                           "ground state energy and calculate energy relative to a state have been "
                                           "conjectured."),
    # g12: each value named a dataset, an institution, a tool or a conclusion its quotes do not
    "bincoletto-mixed-schnet-small-data": ("The authors report that, compared with the linear SchNet results, the "
                                           "accuracy improved by one order of magnitude, which they call remarkable "
                                           "given the size of the training set."),
    "bincoletto-scope-hydrogenic-only": ("The authors state that in this work they focus on hydrogenic systems because "
                                         "they are relatively simple to treat."),
    "blanchette-program-aim": ("The authors describe creating and launching an undergraduate degree in quantum "
                               "information science, aiming to address this gap by training quantum software "
                               "developers in three and a half years."),
    "bonan-lsp-verification-method": ("The author presents a quick and sound method for the robustness verification "
                                      "of quantum classifiers that are Linear Sound, and reports that it successfully "
                                      "verified a classifier's robustness when classifying the MNIST dataset."),
    "bonan-experiment-setup": ("The author states that, due to the limited capability of classical computers to "
                               "simulate quantum circuits, the dataset was filtered to binary classification only, "
                               "simulating 8 qubits."),
    "borle-no-hardware": ("The authors state that at the time of writing there was no publicly available hardware that "
                          "would support problems of the sizes in their work."),
    "boulebnane-mapleSAT-more-efficient": ("The authors report that, for all the problems considered, the scaling of "
                                           "MapleSAT appears to be more efficient than the scaling of QAOA, and that "
                                           "none of the problems demonstrated an improved running time scaling of QAOA "
                                           "compared with MapleSAT."),
    "boulebnane-scope-one-layer": ("The authors state that they focus on QAOA with only one layer (p = 1), and that "
                                   "whether the relative difficulty of the CSP families considered would be maintained "
                                   "for higher p cannot be answered conclusively with their techniques."),
    "campbell-initialisation-time-only": ("The authors state that these objects are best interpreted as "
                                          "initialisation-time characterisations of a circuit."),
    "canonici-qubo-svm-performance": ("The authors state that one of their proposed versions seems to achieve higher "
                                      "performance and lower errors, and that the data obtained via a real QPU extend "
                                      "up to 24 atoms."),
    # g13: each value named a cause, a baseline, a task or a subject its quotes do not
    "nn-extrapolate-larger-deeper-circuits": ("The authors report that neural networks accurately predict the output "
                                              "of larger and deeper circuits than those used for training, even "
                                              "reaching circuit sizes intractable for the most common simulation "
                                              "libraries."),
    "scope-single-round-algorithms": ("The authors state that Hastings' local tensor algorithms are typically "
                                      "iterative, but that this work focuses on single round algorithms."),
    "qrp-higher-accuracy-than-pnr": ("The authors report that the reservoir consistently provided higher accuracy of "
                                     "predictions, both in the QPU hardware implementation and in digital simulations "
                                     "performed using the Perceval Python package."),
    "limit-exponential-scaling-bottleneck": ("The authors state that the spaces involved scale exponentially with the "
                                             "number of modes or particles, and that this results in a mild scaling of "
                                             "reservoir size, as shown in Fig. 3, but can result in an overwhelming "
                                             "workload for the classical network at the output."),
    "qru-higher-accuracy-than-mono-encoded-vqc": ("The authors report that, compared at matched parameter count with a "
                                                  "standard mono-encoded variational quantum circuit baseline, QRUs "
                                                  "obtain higher accuracy."),
    "qru-gains-small-depths-cost-linear": ("The authors report that most gains occur at small depths, with diminishing "
                                           "returns as depth increases while training cost grows approximately "
                                           "linearly."),
    # g14: each value named a dataset, an ansatz, a regime or a qualifier its quotes do not
    "gbs-cvar-vqe-beats-vqe": ("The authors report that employing CVaR outperforms VQE significantly, achieving almost "
                               "perfect success rates for α = 0.01 or 0.1."),
    "gbs-local-minima-failures": ("The authors report that for α = 0.25 and N = {12, 16} the fraction of successful "
                                  "runs decreases, that the failing instances typically involve 3 or 4 flight "
                                  "activities, and that the algorithm appears trapped in local minima."),
    "moe-fraud-ap-0793-vs-xgb": ("The authors report that the routed hybrid architecture with 0.6 threshold achieves "
                                 "average precision scores of 0.793, compared to 0.770 for XGBoost, on 3 repeated "
                                 "5-fold cross-validation benchmarks."),
    "moe-fraud-latency-routing": ("The authors report that approximately 3% of the points were submitted to quantum "
                                  "hardware, resulting in an additional inference overhead of 21 minutes, and that, "
                                  "with a holdout set of approximately 14,000 points, a fully quantum architecture "
                                  "would require nearly 12 hours for inference alone."),
    "moe-fraud-dataset-setup": "The authors state that roughly 0.172% of the data is classified as fraud.",
    "mm-vqe-molecular-limit": ("The authors state that the qubit sizes they are able to demonstrate are at the "
                               "transition point of the term scaling."),
    "kmeans-quantum-quadratic-small-regime": ("The authors state that, assuming superposition quantum access to the "
                                              "data using QRAM, they showcase a quadratic improvement in the ε "
                                              "dependence compared to their classical algorithm in the small ε "
                                              "regime."),
    "safe-qml-f1-competitive": ("The authors report that the proposed QML model achieved a mean F1-macro score of "
                                "0.978 and the SVM the highest, 0.983, with all models evaluated using 5-fold "
                                "cross-validation."),
    # g15: each value named a task, a method, a dataset or a tool its quotes do not
    "das-jc-memory-tasks": ("The authors state that they demonstrated that the reservoir has a very limited memory of "
                            "the injected input sequences for linear tasks but a fairly good memory for nonlinear "
                            "tasks."),
    "das-jc-mackey-glass-rmse": ("The authors report that the JC and DJC models yielded comparable performance with "
                                 "optimum RMSE values in the range 10% < RMSE < 22%, and that for 1-step forecasting "
                                 "they achieved a minimum RMSE of approximately 1%."),
    "daskin-qlstm-bounds": ("The author states that the bound on the change of entropy can be understood through the "
                            "entangling and disentangling power of unitaries."),
    "daskin-vqpm-scaling": ("The authors report that, for QAOA, even the deepest tested configuration (p = 8) exhibits "
                            "a sharp drop from 0.70 at n = 4 to 0.18 at n = 16, and describe their method as "
                            "maintaining a stable average target state probability between 0.35 and 0.46 across most "
                            "sizes."),
    "daskin-vqpm-setup": ("The authors state that the scaling comparison was evaluated over 10 trials per step, under "
                          "a restricted maximum of 30 iterations and a static threshold (pdiff = 0.01)."),
    "daskin-vqpm-noise": ("The authors report that, for a 12-qubit QUBO problem with 100,000 shots per qubit "
                          "measurement, the algorithm locked only 9 out of 12 qubits within the maximum iterations and "
                          "converged to a suboptimal solution with energy -23.0683, compared to the optimal -26.7515 "
                          "found by the noiseless simulation."),
    "deborba-kernel-scope": ("The authors propose a hybrid learning method based on classic kernel methods and, as a "
                             "test case, apply it to classify whether new randomly generated points in a finite square "
                             "are inside or outside a circle located inside this square."),
    "lejarza-qfiae": ("The thesis reports that QFIAE achieved a relative error of about 1% with circuits within the "
                      "depth and width limits of current NISQ devices, and that the full algorithm ran on the quantum "
                      "computers of Qibo and IBM Quantum for tadpole integrals, reaching errors around 5%."),
    "demidik-longitudinal-iqp": ("The authors report that the longitudinal IQP feature map consistently demonstrates "
                                 "improved test performance relative to the IQP approach."),
    "demidik-datasets": ("The authors state that one task classifies 32 subjects into two groups, relapsed "
                         "non-transformed FL (nFL) and transformed FL (tFL), and that another dataset holds 150 "
                         "subjects with a longitudinal collection of 3 or 4 individual MRI scans."),
    # g16: each value named a model or a baseline its quotes do not
    "spatea-newton-mse": ("The authors report that, on G+ES(20) and L+ES(20), their method enhances the "
                          "state-of-the-art approach ClofNet, reducing the error from 0.009 to 0.0076 and from 0.023 "
                          "to 0.0189, respectively."),
    "finite-history-open": ("The authors state that understanding when such compressions are possible, and how the "
                            "required history dependence depends on the structure of the dynamics, remains an open "
                            "problem."),
    "qutrit-qaoa-cited": ("The authors report, citing another study, that the qutrit QAOA achieved the same or better "
                          "solution quality with shallower circuits and half the number of two-qubit gates per layer."),
    # g17: each value named a game, a dataset, a case or a guarantee its quotes do not
    "ferber-bounded-degree-graph-theorem": ("The authors state that, for a graph G on n vertices with m unknown edges "
                                            "and maximum degree d, there is a quantum algorithm that identifies all m "
                                            "edges in G within a number of queries the theorem bounds."),
    "ferber-or-query-model": ("The authors state that, when a set S of vertices is submitted to the oracle, it tells "
                              "whether or not S induces at least one edge in G, and that quantum queries may query "
                              "subsets in superposition."),
    "ferber-optimal-two-cliques-case": ("The authors state that, in a worst case they discuss, their algorithm performs "
                                        "optimally, up to logarithmic factors."),
    "ferreira-qrc-mario-error-rate": ("The authors report that the error rate remains low (below 5%) for temperatures "
                                      "as high as T = 2, where the originality for sequences of length 2 and 3 exceeds "
                                      "and matches, respectively, that of the Markov generator."),
    "ferreira-qrc-roblox-error-rate": ("The authors report that QRC significantly outperforms the Markov chain "
                                       "generator, achieving an error rate as low as 36% for the optimal number of 6 "
                                       "qubits."),
    "ferreira-qrc-noise-effect": ("The authors report that even a small depolarization rate of 1% significantly "
                                  "diminishes the QRC's ability to replicate sequences longer than 15 features, and "
                                  "that the theoretical advantage in adding noise does not translate to better level "
                                  "generation."),
    "finet-emulation-limit": ("The authors state that the quantum step is emulated using classical simulation tools, "
                              "and that their simulations ran under limited computational resources due to their "
                              "inability to emulate their quantum protocol at a larger scale."),
    "fleury-compact-circuit-method": ("The authors state that they demonstrate a straightforward and efficient method to "
                                      "construct compact circuits that are easy to implement."),
    "fleury-qiskit-agreement": ("The authors report that experimental results confirm the algorithm's correctness in "
                                "defining quantum circuits aligned with the Qiskit library's results."),
    "flores-garrigos-gallstone-vs-baselines": ("The authors report that the IonQ Forte solution, reducing "
                                               "dimensionality from 32 to 19 features, outperforms both PCA (with 95% "
                                               "explained variance) and the SelectKBest method based on mutual "
                                               "information."),
    "fonseca-vqe-complexity": ("The authors state, for the simplest version of the algorithm, a circuit depth and a "
                               "total scaling that grow polynomially with N (the exponents are lost in the text "
                               "layer)."),
    # g18: each value named a dataset, a device, a condition or a scale its quotes do not
    "gandhi-dqgp-srtm-nrmse": ("The authors report that, aggregating the improvements across the four SRTM "
                               "environments, DQGP achieves 32.4% ± 22.7% lower NRMSEtest than FACT-GP."),
    "gandhi-dqgp-synthetic-nrmse": ("The authors report that for the synthetic dataset DQGP achieves on average "
                                    "47.0% ± 14.0% lower NRMSEtest than FACT-GP."),
    "gandhi-dqgp-failure-case": ("The authors state that for some datasets FACT-GP yields lower NRMSEtest than DQGP, "
                                 "and attribute this rare performance gap to the high-dimensional mapping of sparse "
                                 "data using expressive quantum kernels."),
    "gerlach-mapf-first-algorithms": ("The authors state that they present the first optimal hybrid quantum-classical "
                                      "MAPF algorithms, and that experiments suggest their approach dominates previous "
                                      "QUBO formulations and state-of-the-art MAPF solvers."),
    "gerlach-mapf-hardware-limit": ("The authors state that considering problems with more than 100 agents would lead "
                                    "to unreasonable results due to the hardware limitations they describe."),
    "gharibyan23-2d-connectivity": "The authors report finding that 2D connectivity greatly outperforms qubits arranged on a line.",
    "gharibyan23-ibm-fire-opal": ("The authors report a marked improvement in approximation accuracy when using the Fire "
                                  "Opal optimization, particularly significant in circuits that included more than 22 "
                                  "two-qubit gates."),
    "gharibyan25c-sim-accuracy": ("The authors report that the best performance in the quantum models is achieved with "
                                  "the BAE loading method, and that their largest model, of 16 blocks each of 14 "
                                  "qubits and 6 variational processing layers, yields an accuracy of 0.94."),
    "gharibyan25c-classical-compare": ("The authors report that their model yielding an accuracy of 0.94 is slightly "
                                       "worse than a convolutional neural network with fewer parameters but better "
                                       "than a vanilla fully-connected neural network with more weights."),
    "gharibyan25c-fez-3000cx": ("The authors report that even with over 3000 two-qubit gates they correctly classify "
                                "68% of the images, and that the 99th percentile of outcomes for random guessing would "
                                "lead to an accuracy of 65%."),
    "gharibyan25l-fidelity-aqce": ("The authors report that, loading the same images with a pre-determined circuit "
                                   "structure and a fixed 2-qubit gate count of 65, they achieve a larger fidelity "
                                   "despite a more rigid circuit ansatz."),
    "gherib-cvdv-so2-hardware": ("The authors report that a single frozen-Gaussian variant of their algorithm was used "
                                 "to simulate the photoelectron spectrum of SO2 from physical quantum hardware, and "
                                 "that the resulting simulated spectrum matches well with the experimental one."),
    # g19: each value named a count, a data type, a cause or a comparison its quotes do not
    "qcc-net-only-qaoa-kernel-gains-weight-with-rbf": ("The authors report that only the most complex and parametric "
                                                       "quantum kernel (QAOA) attains a higher optimum weight in "
                                                       "pairwise combination with the most performant classical kernel "
                                                       "(RBF), and that the classical RBF kernel and its combinations "
                                                       "performed the best overall."),
    "qcc-net-synthetic-data-setup": ("The authors state that each dataset instance consisted of 100 samples, and that "
                                     "kernel metrics are medians over 120 instances, across datasets with d = 2 to 13 "
                                     "features."),
    "imps-circuits-t-count-reduction": ("The authors report that, after decomposing into the Clifford+T gate set, they "
                                        "find an advantage with up to a 5.2× reduction in T-count, for the TFIM "
                                        "Hamiltonian with t = 2.0."),
    "imps-circuits-two-qubit-depth": ("The authors report that, in simulations involving time-evolution, their circuits "
                                      "are found to be more efficient in 2-qubit gate depth than all Trotterizations "
                                      "tested."),
    "qwgan-bioprocess-dtw-score": ("The authors report a Dynamic Time Warping score of 0.6843, lower than the 1.954 "
                                   "reported in a cited work, which they read as their QGAN-generated synthetic data "
                                   "more accurately capturing the temporal dynamics."),
    "qwgan-bioprocess-setup": ("The authors state that the quantum circuit of their model comprises five qubits "
                               "arranged in three layers, and that they trained the model for 2000 epochs."),
    "xqml-two-novel-explanation-methods": ("The authors state that they propose two explanation methods designed "
                                           "specifically for quantum machine learning models, one of them quantum "
                                           "layerwise relevance propagation (QLRP)."),
    "xqml-numerics-no-superiority-claim": ("The authors state that their goal is to display the practical application "
                                           "of their protocols, not to claim that quantum models have an advantage "
                                           "over classical algorithms in explainability, nor that their techniques are "
                                           "superior to established ones, and that different methods perform "
                                           "differently for different tasks and under different metrics."),
    "qnbm-linearized-model-efficient-sampling": ("The authors state that one can sample efficiently and classically "
                                                 "from the whole network with O(E) calculations, where E is the number "
                                                 "of edges, that this construction is precisely a Bayesian network, and "
                                                 "that the same construction does not work for the non-linear QNBM."),
    "qnbm-training-volatile": ("The authors report training a (5, 0, 6) network on three types of target probability "
                               "distributions, and that training on the Discrete Gaussian distribution is markedly "
                               "volatile."),
    "distributed-qelm-linear-resource-reduction": ("The authors state that, from the analytical expressions in Eqs. 5 "
                                                   "and 8, their distributed architecture corresponds to a linear "
                                                   "improvement in the required reservoir dimension for large inputs, "
                                                   "compared to the single three-layer architecture, a linear "
                                                   "reduction in resource requirements per unit."),
    "distributed-qelm-polynomial-k-reservoirs": ("The authors report that, for polynomial targets, any target "
                                                 "exhibiting a nonlinearity of order k can be reconstructed using k "
                                                 "reservoirs, although specific targets can be recovered with fewer."),
    "distributed-qelm-simulation-only": ("The authors state that, beyond numerical simulations, the appeal of the "
                                         "approach is in its testing in experiments in NISQ quantum hardware platforms, "
                                         "and that understanding the noise robustness of these models is crucial."),
    # Fresh-eyes review of cec6020 (2026-10-25): a figure garbled in the text layer (an exponent printed flat,
    # so N^2 reads "N 2") passes the figure check, because the garble is the same in quote and value. Each value
    # below says the figure in words, or says the exponent is lost.
    "laskar-lemma3-gate-count": ("The paper states in Lemma 3 that, for an n-qubit circuit, the QATE algorithm requires "
                                 "O(n) 1-qubit gates and (n − 1 choose 2) + 2(n − 2) 2-qubit gates to design a "
                                 "bi-symmetric diagonal evolution operator."),
    "qaoa-hc-embedding-limit": ("The author states that the embedding requires (n − 1) squared qubits, so simulation "
                                "is limited to n no more than 6, and that n = 3 and 4 (a triangle and a square) were "
                                "simulated."),
    "simplex-rank-reduction": ("The paper shows that, for any specific constant rank r, an algorithm for simplex "
                               "finding in rank-r hypergraphs with n to the power r/2 queries would imply an O(n) "
                               "algorithm for triangle finding."),
    "simplex-4-algorithm": ("The paper proves an adaptive learning graph algorithm for 4-simplex finding with n to the "
                            "power 2.455 quantum queries, improving the trivial n to the power 2.5 algorithm."),
    "mm-vqe-ising-speedup": ("The authors report that, for a fully connected Ising Hamiltonian up to 20 qubits, where "
                             "all terms commute, the method offers a speedup polynomial in N in terms of the "
                             "percentage of time saved (the exponent is lost in the text layer)."),
    "lejarza-clustering": ("The thesis states that its quantum K-means design offers exponential speedups in vector "
                           "dimensionality d and number of clusters K on quantum hardware with qRAM, that its quantum "
                           "kT-jet clustering improves the runtime polynomially in N over the classical one (the "
                           "exponents are lost in the text layer), and that its quantum simulations showed clustering "
                           "efficiencies comparable to classical methods."),
    "galvis-gpq-classical-baseline": ("The authors state that a classical GPQ method with the Hilbert space "
                                      "approximation would cost a polynomial in M (the exponent is lost in the text "
                                      "layer), and so the advantage of the quantum algorithm is polynomial."),
    "tqnn-kjunta-query-complexity": ("The authors report that applying their amplitude-amplification training "
                                     "approach to the class of positive k-juntas gives an upper bound on the quantum "
                                     "examples sufficient (its exponents are lost in the text layer), with "
                                     "experimental results seemingly showing that a tighter upper bound is possible."),
    "gqsp-angle-precision": ("The authors report that the Prony-based angle-finding algorithm generates angle "
                             "sequences of precision 10 to the power −13 for polynomial degrees up to hundreds "
                             "within a second."),
    "gqsp-query-halving": ("The authors report, from a numerical benchmark for Hamiltonian simulation, that the GQSP "
                           "scheme essentially halves the queries to signal operators compared to ordinary QSP at "
                           "precision 10 to the power −13."),
    # The same review: a HIGH value that said more than its quotes, trimmed or given the passage it rests on.
    "single-shot-definition": ("The authors define a quantum classifier as single-shot exactly when the probability "
                               "that a random label is identical to the majority label assigned by the classifier is "
                               "very high."),
    "exact-learning-definition-threshold": ("The authors define an exact learner by an algorithm that outputs a "
                                            "hypothesis meeting its condition with high probability, and they set the "
                                            "probability threshold at 0.95 rather than the 2/3 some authors use."),
    "gross-memory-limit-large-n": ("The authors state that explicitly constructing and storing the resulting optimal "
                                   "measurement operator eventually limits the feasibility of the full optimization "
                                   "for large N."),
    "open-problem-limit": ("The authors state that proving or disproving the statement that no classical algorithm "
                           "dequantizes the problem for an unknown sparse Hermitian matrix will either limit or "
                           "clarify the implications of their Corollary 15."),
    "stationary-noise-breaks-exchangeability": ("The authors state that without exchangeable scores they cannot "
                                                "assert that the rank of the test score is uniformly distributed, so "
                                                "without the assumption of stationary noise they cannot obtain "
                                                "guarantees in the form given in Theorem 1."),
    # The same review: a measured clause inside a stated limit is dropped from the value with its quote.
    "gqsp-optimization-limit": "The authors state that how stable the root-finding approach is in general is an open problem.",
    "medmnist-not-beating-classical": ("The authors state that the classical models use the full spatial dimensions "
                                       "of the images while their QML model uses a significantly reduced feature set, "
                                       "dictated by quantum hardware constraints."),
    "mcquack-stated-limitations": ("The authors state that training on quantum hardware is currently infeasible for "
                                   "practically relevant system sizes, and that the simulations are performed on a "
                                   "noiseless simulator."),
    "qcbm-stated-limitations": ("The authors state that training on a classical simulator rather than real quantum "
                                "hardware precludes observation of hardware-specific noise effects, and that basis "
                                "encoding introduces quantization error."),
    "ippdt-limits": "The authors state that IP-PDT is not a universal remedy for barren plateaus.",
    "annealer-limits": ("The author states that the applicability of the algorithm to current devices is "
                        "limited by their small number of qubits and sparse connectivity."),
    "nakano-high-temperature-limit": "The authors state that the method is not intended for high-temperature settings.",
    # g52 to g64, re-audited after the review of cec6020: the measured clause left with its quote
    "photonic-classifier-limit-below-10-photons": ("The authors state that whether this degradation can be overcome "
                                                   "by further increasing the training dataset remains an open "
                                                   "question for future work."),
    "quantumgep-quantum-chemistry-limit": ("The authors state that in quantum chemistry more work remains to obtain "
                                           "more precise quantum circuits for the exact ground state."),
    "atchade-limits": ("The authors state that the qubits' scarcity and susceptibility to errors and decoherence "
                       "significantly cap the complexity and size of the models they can reliably implement."),
    "rydberg-sim-not-hardware": ("The authors state that their optimization was performed on a simulator instead of "
                                 "the Aquila hardware, so it is important to study the performance on actual "
                                 "hardware."),
    "docking-12-qubit-local-optima-limit": ("The authors state that one notable caveat of their approach is the "
                                            "algorithm's vulnerability to converging towards local optima within the "
                                            "vast parameter space."),
    # g59, g63, g67: an exponent printed flat in the text layer, said in words
    "chen2020-parameter-count": ("The authors state that for the considered testing environments variational quantum "
                                 "deep Q-learning involves parameters as small as O(n), against n cubed for tabular "
                                 "Q-learning and n squared for neural network based deep Q-learning, and describe "
                                 "this as quantum advantage in memory and parameter count."),
    "date-aqsvm-time-complexity": ("The paper states that if the precision for all parameters is fixed, the qubit "
                                   "footprint and time complexity of the quantum approach would be quadratic in N, "
                                   "which it calls an order of magnitude better than the classical algorithm, cubic "
                                   "in N, and that estimating ST99 and ST99(OPT) for a generic QUBO formulation of "
                                   "the SVM problem is beyond the scope of the present work."),
    "ghosh-reverse-engineering-mean-error": ("The authors report that multi-qubit classifiers can be reverse-engineered "
                                             "under specific conditions with a mean error of order 10 to the power −2 "
                                             "in a reasonable time."),
    # g69: each value trimmed to what its quotes say
    "halder-rbm-ansatz-accuracy": "The authors report that the accuracy is achieved using a substantially shallow depth ansatz.",
    "enqode-eval-setup": ("The authors state that all experiments used 8-qubit circuits with an 8-layer ansatz, and "
                          "that they randomly sampled 5 classes per dataset and 500 images per class."),
    # g68: the measured error trend is dropped from this scope
    "gsa-role-of-qpu": ("The authors state that the primary purpose of the QPU calculations is to identify the most "
                        "important Fock states through the obtained measurement samples."),
    # g67: the test bed is not in the quotes; the 20 W figure conflicts with the paper's kW figures (reader)
    "gheisarnejad-qdrl-scheme-and-testbed": ("The authors state that the quantum principle is incorporated into deep "
                                             "reinforcement learning to address the hardware limitations of "
                                             "conventional computers, and that the real-time outcomes of their "
                                             "controller are compared with a model predictive control scheme."),
    "gheisarnejad-proof-of-concept-only": ("The authors state that the scheme was evaluated by HiL experiments, and "
                                           "that the work presents a proof of concept."),
    # g65: "a fixed low number of bits" is cut from the quote
    "exploratory-no-scaling": ("The authors state that the data set could easily be classified by a classical "
                               "network, that their setup precludes any discussion of scaling, and that the work is "
                               "exploratory."),
    # g63: each value trimmed to what its quotes say
    "cranganore-limit-code-classification-labels": ("The authors state that their code classification-based "
                                                     "approach assumes a label for each classic task that maps it to "
                                                     "its quantum counterpart."),
    "cranganore-limit-photonic-circuit-model": ("The authors state that photonic machines proved to have the best "
                                                "performance with the measurement-based model, so circuit synthesis "
                                                "and mapping might not guarantee the best performance."),
    "dasilva-limit-dataset-resolution": ("The authors state that the limitations of the NASA POWER dataset include "
                                         "its daily resolution and non-geostationary satellite sources."),
    "dave-setup-simulation-300-points": ("The authors state that the algorithms are compared through simulation "
                                         "experiments on two low-energy carbon datasets, and that the metrics are "
                                         "calculated for 300 data points."),
    "oliveira-setup-simulator-two-devices": ("The authors state that the experiments ran on two non-error-corrected "
                                             "quantum processors, ibmq athens and ibmq santiago."),
    # g61: the quote breaks off before "significance"
    "qasa-limits-simulated-training-few-seeds": ("The authors state that model training is performed on a classical "
                                                 "state-vector simulator, and that quantum baseline comparisons use "
                                                 "n = 3 random seeds due to the high cost of quantum simulation."),
    # g60: each value trimmed to what its quotes say
    "hybrid-qnn-maze-noise-free-simulator-scope": ("The authors state that the experiments were tested and trained on "
                                                   "full-classical hardware in an ideal, noise-free environment, and "
                                                   "that training a hybrid model on a real quantum computer is "
                                                   "challenging."),
    "qlstm-rc-rl-model-setup": ("The authors state that they use an 8-qubit VQC-based QLSTM with input and hidden "
                                "dimensions of 4, explore 1, 2 and 4 VQC layers, and run 80 parallel local agents."),
    "ae-vqc-stated-limitations": ("The authors state as limitations that all experiments were performed with quantum "
                                  "simulators, and that the method was investigated only in image classification."),
    # g59: each value trimmed to what its quotes say
    "chaudhary-proof-of-concept-scope": ("The authors describe the Ising test as a proof-of-concept of using the QGAN "
                                         "to generalize from low energy Ising states, and leave further tests for "
                                         "future work."),
    "chaudhary-mode-collapse": ("The authors state that the QGAN tends to converge to a distribution that has zero "
                                "probabilities for certain states, and that the precise cause requires further "
                                "investigation."),
    "chen2018-simulated-exact-probabilities": ("The authors state that the experiment was done on a simulated quantum "
                                               "computer, on classical hardware where exact measurement probabilities "
                                               "are available."),
    "chen2023-setup-simulation-8-qubits": ("The authors state that results are from numerical simulations within the "
                                           "tasks considered, with an 8-qubit VQC of two variational layers, 96 "
                                           "quantum parameters in total, and 80 parallel agents."),
    # g58: the measured runtime and the noise observation are dropped from these scopes
    "dibom-simulation-scale": "The authors state that the classical computation time is exponential in n.",
    "cepaite-scale-and-noise": "The authors state that their study focused on problem sizes up to 55 qubits on IBM hardware.",
    # g57: each value trimmed to what its quotes say
    "bhattacharyya-heisenberg-limit": ("The authors state that, for the more general Hamiltonians they discuss, "
                                       "finding the optimal Clifford state may be NP-hard."),
    "bhowmik-survey-scope": ("The authors state that the paper introduces QML and its applications for anomaly "
                             "detection in consumer electronics, and includes five case studies of recent works."),
    # g56: average-case performance and advantage are not in the quote
    "qwoa-benchmarking-future": ("The authors state that detailed and large-scale benchmarking for various problems "
                                 "is an important future area of research."),
    # g55: each value trimmed to what its quotes say
    "cvqbm-simulator-only": ("The authors state that the experiments were conducted on a simulator, and leave the "
                             "experimental realization of their CVQBM on photonic quantum hardware to future work."),
    "cvqbm-hardware-limit": ("The authors state that the available hardware cannot accommodate their CVQBM, mainly "
                             "because of the lack of online squeezers, since the parameters of the available offline "
                             "squeezers are fixed."),
    # g54: Nelder-Mead is not in the quotes
    "arrasmith-scope": ("The authors state that their work casts doubt on the notion that the choice of optimizer "
                        "could avoid barren plateaus, and that Proposition 1 is relevant to gradient-free optimizers "
                        "that search the landscape from a random initial point."),
    # g53: "current state-of-the-art RL" is not in the quote
    "qcd-gym-insufficient-performance": ("The authors state that the approaches do not provide sufficient "
                                         "performance for robust and scalable applicability."),
    # g52: each value trimmed to what its quotes say
    "noise-study-scope-effective-model": ("The authors state that the present results do not by themselves establish "
                                          "that the observed improvement is unique to physical quantum noise, and that "
                                          "the study examines single-layer QGNNs on molecular property prediction."),
    "photonic-classifier-scope-one-task": ("The authors state that the classifier implemented a three-layer data "
                                           "re-uploading model, and that the classification task involved a circular "
                                           "decision boundary."),
    # g51: each value trimmed to what its quotes say
    "qtransformer-survey-challenges": "The authors state that the survey examines key technical challenges.",
    "noise-theory-simulation-scope": "The authors state that the present simulations assume independent gate-level noise.",
    "qcdge-calculation-levels": ("The authors state that the ground-state calculations were performed at the "
                                 "B3LYP/6-31G* level with the BJD3 dispersion correction."),
    # g50: each value trimmed to what its quotes say
    "yu-setup-noiseless-sim": ("The authors state that they evaluate seven representative model pairs across "
                               "classification and sequential decision-making tasks, that all quantum circuits are "
                               "evaluated on a noiseless state-vector simulator, and that all classification models are "
                               "evaluated on the same BAS dataset."),
    "jiang-two-qubit-reduced-data": ("The authors state that they use two qubits, forming a four-dimensional Hilbert "
                                     "space, which they found sufficient, after an explained variance analysis using "
                                     "Principal Component Analysis."),
    "zajac-setup-synthetic": ("The authors state that they generated a training set of Ntrain = 500 observations and a "
                              "test set of Ntest = 1001, and that final model performance was validated on physical "
                              "quantum hardware using five distinct benchmark points."),
    "zanotta-classical-simulation-setup": ("The authors state that they compare QO-SPINN, classical SPINN and PINN on "
                                           "the quality of the retrieved solution rather than on speedup, and that "
                                           "their approach excludes any quantum and statistical noise."),
    "zanotta-hardware-limit": ("The authors state that current quantum hardware limitations in noise and number of "
                               "qubits prevent immediate realization of the theoretical speedups in practical "
                               "applications."),
    # g48: the seven variables padded to eight are not in the quotes
    "wisniewska-scope-simulation-one-dataset-three-qubits": ("The authors state that all calculations and simulations "
                                                             "were done in Python, and that the eight input features "
                                                             "require three qubits."),
    # g47: the origin-of-advantage clause is not in the quote
    "qtde-no-formal-guarantees": ("The authors state that they do not provide formal guarantees regarding quantum "
                                  "advantage, expressive power, or generalisation performance."),
    # g46
    "wang25h-accuracy": ("The author reports that RQNN reached an accuracy of 98.00% on a non-linear discrete data "
                         "classification under amplitude damping noise, higher than the compared quantum neural "
                         "network; the results section places the 98.00% on the training set."),
    # g44: the review's listed topics beyond the quote are dropped; "8k" and "6k" are 8 and 6 to the power k with the
    # exponent printed inline, so the value no longer states them as products
    "qkm-review-scope": ("The review states that it analyses non-variational supervised quantum kernel methods, "
                         "covering their foundations in classical kernel theory, constructions of fidelity and "
                         "projected quantum kernels, and methods for their estimation in practice."),
    "cutting-cost-exponential": ("The authors state that wire cutting and gate cutting each produce a number of "
                                 "subcircuit combinations that grows exponentially with the number of cuts k, and that "
                                 "the scaling remains exponential in the number of cuts."),
    # g43: each value added a clause its quotes do not carry
    "quso-classical-simulation-random-instances": ("The authors state that the numerical experiments were conducted "
                                                   "using randomly generated power grid instances of varying sizes and "
                                                   "loads that adhere to the physical properties of real world power "
                                                   "grids, allowing for large-scale experiments."),
    "quso-qaoa-not-near-optimal": ("The authors state that the QAOA was not able to reach near-optimal solution quality "
                                   "in most cases, and that future work should conduct a broader hyperparameter search "
                                   "and larger problem instances."),
    "positive-p-simulation-framework": ("The authors state that the work presents an efficient computational framework "
                                        "based on the phase-space positive-P method for simulating bosonic "
                                        "neuromorphic systems."),
    "gqpinn-symmetry-limit": ("The authors state that their current approach enforces symmetry primarily at the level "
                              "of the target solution, for example rotational invariance."),
    # g42
    "daqc-qubit-limit": ("The authors state that they limit their DAQC design to 16 qubits in this study due to the "
                         "limitations of current quantum hardware."),
    "tshf-simulation-only": ("The authors state that the quantum simulations were performed using the lightning.qubit "
                             "backend, and that the study is inherently constrained by the limits of classical "
                             "simulation."),
    "sim-exact-only": ("The authors state that their results focus on calculating the exact expectation value without "
                       "considering noise and sampling effects."),
    # g41: each value named a detail its quotes do not carry
    "shofar-assumption-sampling-noise": ("The authors state that the training kernel matrix is assumed to be exact "
                                         "(a noiseless training phase), and that their results consider only the "
                                         "fundamental sampling noise."),
    "shmueli-power-open": ("The author states that the precise computational power of BQP^OI is an open question, and "
                           "that no trivial way was found to solve computational problems with major implications for "
                           "complexity theory."),
    "singh-pokhrel-preliminary": "The authors state that their analysis is preliminary and that investigations are ongoing.",
    # g40: each value named a detail its quotes do not carry
    "schetakis-setup-data-simulated": ("The authors state that they analyzed 40 days of traffic flow data collected "
                                       "during March and April 2023, with a time resolution of 1.5 minutes, and that "
                                       "the quantum networks were simulated on conventional hardware."),
    "shah-limit-aspect-ratio": ("The authors state that the performance of all of these algorithms depends on certain "
                                "aspect-ratio-like quantities, and that improving this dependence is an open problem."),
    # g39: each value gave a cause its quotes do not carry
    "xqml-run-scope-ibm-brisbane": ("The authors state that, with only IBM devices to select from, they used "
                                    "ibm_brisbane, and that they classified only 1815 samples (918 and 897 of class 0 "
                                    "and 1 respectively) using 1024 real device shots for each sample."),
    "qrf-fashion-mnist-accuracy": "The authors report that simulations on Fashion-MNIST reach up to 89.3% accuracy.",
    # g38: the regression clause is not in the quote
    "classification-only-scope": "The authors state that they only considered classification tasks in this work.",
    # g37: "quadratically" is not in the quotes
    "quyen-dl-ml-limits": ("The authors state that the Distance Loss method requires fidelity evaluations for all "
                           "pairs of training samples, that the Measurement Loss method achieves linear scaling, and "
                           "that a recurring optimization phenomenon they call the trajectory crossing problem "
                           "occurs."),
    # g36: the extracted "217-dimensional" is most likely 2 to the 17th with its exponent lost; the value no
    # longer restates the garbled figure as a dimension
    "hhl-advantage-claim": ("The authors state that their implemented quantum solution, which they call a record for a "
                            "linear system solution on quantum computers, demonstrates algorithmic quantum advantage "
                            "over classical solutions (the problem dimension is printed with its exponent lost in the "
                            "extracted text)."),
    # g35: each value gave a reason or a contrast its quotes do not
    "qcbm-preprocessing-setup": ("The authors state that, for high-dimensional datasets such as Telco Churn with 20 "
                                 "features, PCA is applied to reduce dimensionality to principal components that "
                                 "retain at least 95% of the total variance."),
    "qsvm-scope-single-dataset-svm-baselines": ("The authors state that all results derive from the insurance "
                                                "classification task on MIMIC-CXR, and that the quantum kernel "
                                                "advantage is therefore relative to SVM-based baselines."),
    "quanv-ae-fixed-random-quantum-filters": ("The authors state that, in this configuration, the quantum filtering "
                                              "layer is a non-trainable set of quantum-based filters built from "
                                              "randomized quantum circuits, implemented using PennyLane."),
    # g34: the future-step clause is not in the quote
    "hindi-qnlp-no-hardware-yet": ("The authors state that, to date, all experiments have been conducted on simulated "
                                   "or hybrid quantum platforms."),
    # g31: each value added a detail its quotes do not carry
    "deutsch-jozsa-not-practical": "The authors state that this problem and algorithm are not of practical use.",
    "vqa-framework-three-metrics": ("The authors state that their framework for evaluating VQAs combines three "
                                    "complementary metrics, and that they formalize reproducibility."),
    "vqa-framework-proof-of-concept": ("The authors state that, as a proof of concept, they apply the framework on a "
                                       "16-qubit QUBO instance."),
    "qaoa-xy-turnover-limitation": ("The authors state that the primary practical limitation observed is turnover: "
                                    "QAOA-XY exhibited substantially higher average monthly turnover (76.8%) than the "
                                    "classical baselines."),
    "state-decay-needs-ancillas": "The authors state that how many ancillas are necessary is unknown.",
    # g30: each value added a clause its quotes do not carry
    "ssp-warm-start-mean": ("The authors report that, with the quantum-derived solution as a warm start, the resulting "
                            "QWS plans achieve a mean SD improvement of +1.7% and a mean reduction of 0.2% in drive "
                            "distance per shipment across all weekly schedules and scenarios."),
    "qlustering-proof-of-concept-scope": ("The authors state that the work is intended as a theoretical proof of "
                                          "concept, and that they do not attempt an exhaustive benchmark against the "
                                          "full landscape of clustering algorithms."),
    "rectification-noise-limit": ("The authors state that Theorem 1 requires that bit flip errors occur randomly and "
                                  "independently for each qubit."),
    "trigger-label-circularity": ("The authors state that the models are in large part reconstructing a known analytic "
                                  "function from its own ingredients."),
    # g28: each value named a detail its quotes do not
    "qmd-quantum-inspired-basis": ("The authors state that QMD is based on a quantum-annealing-inspired algorithm, and "
                                   "that its hSB algorithm can be applied to any formulation of objective function "
                                   "under binary variables."),
    "vqa-constrained-comparison-scope": ("The authors state that a direct comparison with ansatz-based schemes is "
                                         "omitted due to their substantial implementation overhead."),
    # g27: the quotes do not say the result holds for any positive epsilon
    "laneve-open-epsilon": ("The authors state that their result seems to suggest there exists an algorithm that "
                            "directly solves the problem in the limiting case, and that finding such an algorithm is an "
                            "open question."),
    # g25
    "lstm-scope-eight-qubits": "The authors state that the evaluation used data from eight superconducting transmon qubits.",
    # g23: the noise and trace-distance finding is not in the quote
    "margin-noise-open-question": ("The authors state that a deeper theoretical understanding of the relationship "
                                   "between noise, margins, and generalization, along with strategies to mitigate "
                                   "these effects, will be critical."),
    # g22: the order-of-magnitude reading is not in the quote
    "annealer-speedup-estimate": ("The authors estimate that classification and printing out would take about 8000 "
                                  "microseconds on a classical computer, whereas samples can be obtained from the QPU "
                                  "in 168 microseconds."),
    "q2sar-auc-vs-gradient-boosting": ("The authors report that their QMKL-SVM approach achieved a superior AUC score "
                                       "(0.875 vs. 0.804) on the DYRK1A inhibitor dataset, and describe the comparison "
                                       "as against a strong classical baseline."),
}
CONTEXT_FIX: dict[str, str] = {  # an assertion's context where the reader's did not fit
    # g06: the reader wrote its result_type, "setup", in the context field; each takes its paper's context
    "results-simulation-only": "world", "pha-larger-systems-open": "qc", "noise-study-scope": "qml",
    "simulation-only-hardware-missing": "qml", "latent-features-qubits": "qml",
    "full-hardware-run-infeasible": "qml", "pqk-capacity-limit": "qml",
    "spe-evaluation-setup": "qml",  # g20: the reader wrote "method"
    "complexity-signature-auc": "qml",  # g38: the reader wrote "method"
    "qcml-bond-limits-no-uniform-claim": "qml",  # g39: the reader wrote "method"
    "autoqresearch-staged-confirmation": "qml",  # g41: the reader wrote "method"
    "lean-qbench-limits": "qc",  # g51: the reader wrote "method"
    "bucher-fair-benchmark-guidelines": "qc",  # g58: the reader wrote "method"; the paper benchmarks quantum optimization
    "bucher-maxcut-results": "qc",
    "bucher-guidelines-incomplete": "qc",
}
DROP: dict[str, str] = {  # an assertion not entered, with the reason
    "qwiener-advantage-open": "g56: the quotes do not hold the open question the value states",
}
VENDOR_DESCRIPTIONS: set[str] = set()  # a vendor's description of its own product (MODERATE), not a result
# A statement about the field, its devices or its literature, not about the paper's own work.
FIELD_STATEMENTS: set[str] = {
    "autoqml-nisq-constraints",  # g01
    "qc-not-outperforming-for-most-ml", "data-loading-exponential-slowdown", "quantum-advantage-questionable",  # g03
    "patel-hardware-small-molecules", "patel-hadamard-test-cost", "patel-qpe-not-nisq",  # g04
    "rohe-no-single-benchmark",  # g05: drawn from the review of the literature, not from a run
    "no-quantum-advantage-claim",  # g06
    "vqa-consensus-no-practical-use", "tomar-qml-challenges", "tomar-outperform-claim",  # g07
    "tomar-benchmarking-needed",
    "blanchette-workforce-bottleneck",  # g12
    "nisq-guaranteed-algorithms-need-millions",  # g13
    "lejarza-limit",  # g15: progress the field still needs, not a limit of the thesis's own work
    "qudit-limits",  # g16: a review's statement about qudit hardware
    "fischbach-scalability-challenge", "fonseca-vqe-near-term-claim", "fonseca-barren-plateau-difficulty",  # g17
    "xqml-field-evidence-missing", "ml-for-qc-specialists-nisq-caveats",  # g19
    "gong-hybrid-not-universal-advantage",  # g20
    "vqe-no-best", "vqe-bottleneck",  # g21: a review's statements about the methods it reviews
    "qdl-trainability-simulability", "qdl-open-question",  # g24
    "thesis-dequantization-open",  # g27
    "dequantization-building-blocks",  # g32: a survey's reading of the dequantization literature
    "provable-separations-not-settled", "trainable-implies-simulable", "benchmarks-not-at-scale",  # g33: a review
    "mostly-simulated", "bp-avoidance-implies-simulability",  # g33
    "qml-speedups-idealized", "qml-encoding-cost", "qml-lack-of-datasets",  # g36
    "photonic-dv-cv-scope", "photonic-photon-loss-challenge",  # g39: a review's statements about its field
    "review-open-theory", "suite-hw-limit",  # g42
    "advantage-hard-to-establish", "qkm-sampling-cost",  # g44
    "wendin-entangle-20-qubits",  # g47
    "whitaker-no-efficient-classical-subnetwork-search",  # g48
    "simplex-lower-bound-gap",  # g49
    "qtransformer-survey-qla-static", "qtransformer-survey-challenges",  # g51
    "cfd-review-nisq-out-of-reach", "cfd-review-hybrid-limits",  # g53
    "babbush-few-applications",  # g54
    "qwasserstein-no-true-definition", "qwasserstein-qwgan-toy-only",  # g56: a review's statements on the field
    "bertl-practical-limits", "bhowmik-qubit-limit",  # g57
    "qml-nisq-limited-resources-challenge",  # g60
    "corli-infancy-advantage-unknown", "corli-data-loading",  # g62
    "dave-limit-deployment-challenges",  # g63: about quantum deployment in general, not the paper's own work
    "no-other-known-features", "hybrid-contribution-studies-lacking", "systematic-circuit-design-lacking",  # g65
    "ganguly-advantage-not-shown",  # g67: about QNLP as a field
    "no-native-quantum-anomaly-detection",  # g68
    "hasanzadeh-uc-hardware-limits", "hasanzadeh-uc-qml-limits",  # g69: a survey's conclusions on the field
    "hegde-no-nisq-advantage-yet", "hegde-optimization-polynomial",  # g69
}
# A reader's "field" the coordinator did not follow, with why.
NOT_FIELD: dict[str, str] = {}
# Every HIGH grade: (basis, where the paper settles it), after the coordinator's read. A measured result,
# even a negative one, stays LOW.
HIGH = high_grades({
    # g01
    "mqt-scaling-bottleneck": ("stated limit", "Discussion: amplitude embedding's exponential preparation cost"),
    "mqt-molecules-and-qubit-counts": ("setup", "numerical experiments: the molecules, qubit counts and mappings"),
    "qinspired-head-attribution-uncertain": ("stated limit", "section 6, p.16"),
    "dd-theorem-peak-at-interpolation": ("proved result", "Theorem 1, section IV, formal proof in Appendix D"),
    "dd-corollary-rdm-peak-linear-in-qubits": ("proved result", "Corollary 3, section VII, with its proof"),
    "dd-limits-concentration-and-pqcs": ("stated limit", "section VIII"),
    "graph-stabilizer-code-bijection": ("proved result", "Theorems 4.1.1 and 4.2.5, chapter 4"),
    "graph-code-encoding-depth-twice-degree": ("proved result", "Theorem 4.1.2 item 3; formal version section 4.4"),
    "graph-codes-scope-limits-vs-qldpc": ("scope", "section 4.1.1: not aimed at asymptotically good qLDPC codes"),
    "autoqml-study-scope-four-use-cases": ("setup", "section 6: the four use-cases"),
    "autoqml-framework-not-yet-built": ("scope", "section 6: the framework is to be implemented after this study"),
    "lstm-optimizer-simulation-setup": ("setup", "section VI: infinite shots; one run at 100 shots"),
    "qtn-protein-dataset-setup": ("setup", "section 3.1: the dataset"),
    "qtn-protein-noise-free-limit": ("stated limit", "section 4, Limitations"),
    # g02
    "sbqe-experiment-setup": ("setup", "sections IV.A and IV.B"),
    "sbqe-stated-limitations": ("stated limit", "section V, pp.6-7"),
    "qenn-quantum-inspired-only": ("setup", "sections 3.2 and 4.2: the layers simulate interference classically"),
    "qenn-stated-limitations": ("stated limit", "section 6.1, p.10"),
    "larose-problem-size": ("setup", "section I.A.1, p.3"),
    "larose-stated-limitations": ("stated limit", "section IV.A, p.11, and section II, p.5"),
    "laskar-lemma3-gate-count": ("proved result", "Lemma 3 and its counting proof, section IV, p.8"),
    "laskar-stated-limits": ("stated limit", "sections IV.A and VI"),
    "qrnn-data-setup": ("setup", "sections 4.1 and 4.2"),
    "qrnn-open-trainability": ("stated limit", "section 5, p.21: trainability left open"),
    "qbtree-qram-assumption": ("scope", "section 4.1: the results assume a QRAM that does not yet exist"),
    "cvqelm-setup": ("setup", "section 4"),
    "cvqelm-hardware-not-validated": ("stated limit", "section 5, p.16: no on-bench validation yet"),
    "qdc-experiment-setup": ("setup", "section 5, p.8"),
    "qdc-classical-hardware": ("setup", "section 5, p.8: run on classical GPUs"),
    "qdc-stated-limitations": ("stated limit", "section 6, pp.10-11"),
    # g03
    "no-guarantee-optimal-classical": ("stated limit", "sections 7 and 8, p.9"),
    "cartpole-not-evidence-of-advantage": ("stated limit", "section 6.4, p.8"),
    "comparison-setup-equal-mse": ("setup", "section V.B"),
    "sample-not-exhaustive": ("scope", "section II"),
    "model-omits-cost-and-noise": ("stated limit", "section 4"),
    "analysis-limited-binary-few-datasets": ("stated limit", "section 5, p.14"),
    "two-effects-introduced": ("definition", "abstract and section 2"),
    "review-scope": ("scope", "abstract"),
    "hardware-ansatz-truncated": ("setup", "p.6"),
    "optimality-unknown": ("stated limit", "section IV.B, p.6"),
    # g04
    "nakano-spectral-gap-setup": ("setup", "section IV A"),
    "nakano-high-temperature-limit": ("stated limit", "the Fig. 8 discussion: not intended for high temperatures"),
    "nakano-larger-models-open": ("stated limit", "section V, p.9"),
    "nigatu-simulated-versus-hardware": ("setup", "the abstract and the implementation section, which differ"),
    "okumura-setup-data": ("setup", "the numerical experiments section"),
    "okumura-discretization-limit": ("stated limit", "conclusion"),
    "ozhigov-course-scope": ("scope", "annotation"),
    "park-setup-vqe-ising": ("scope", "abstract"),
    "park-hyperparameter-sensitivity": ("stated limit", "section 4"),
    "patel-qbm-scope-thermal-states": ("scope", "section VII"),
    "patel-qbm-barren-plateau-open": ("stated limit", "section VIII"),
    "patel-review-scope": ("scope", "abstract"),
    "patil-setup-simulated-noise": ("setup", "section III"),
    "patil-generalization-future": ("stated limit", "section IV"),
    # g05
    "qdataset-52-simulated-datasets": ("setup", "section 6, p.27"),
    "qdataset-size": ("setup", "section 1.4, p.4"),
    "qdataset-simulated-not-hardware": ("scope", "section 1.4, p.5: the datasets are simulations"),
    "tvha-test-systems": ("setup", "section 1, p.4"),
    "tvha-no-hardware-runs": ("stated limit", "section 5: hardware benchmarks named as future work"),
    "pranjic-scope-limit": ("stated limit", "section IV"),
    "pranjic-sparkov-dataset": ("setup", "appendix B"),
    "quertier-setup": ("setup", "sections 1.1 and 2.1"),
    "gqsim-proposal": ("definition", "abstract"),
    "gqsim-embedding-challenge": ("stated limit", "section V"),
    "ramoa-setup": ("setup", "abstract"),
    "roget-quadratic-only-if": ("stated limit", "the discussion: quadratic only under the same data access"),
    "rohe-review-method": ("setup", "section 1"),
    "rohe-limitations": ("stated limit", "section 7"),
    # g06
    "qsaf-definition": ("definition", "abstract"),
    "qsaf-not-quantum-mechanics": ("scope", "section 1.1, p.3"),
    "dicke-ansatz-feasible-states": ("definition", "abstract: a property of the ansatz as constructed"),
    "results-simulation-only": ("stated limit", "conclusion, p.9"),
    "pha-larger-systems-open": ("stated limit", "section VIII"),
    "noise-study-scope": ("setup", "introduction"),
    "simulation-only-hardware-missing": ("stated limit", "section V"),
    "latent-features-qubits": ("setup", "section IV.A"),
    "full-hardware-run-infeasible": ("stated limit", "section V"),
    "pqk-capacity-limit": ("stated limit", "section V"),
    # g07
    "qelm-mnist-scope": ("scope", "section II and the conclusion"),
    "vqe-definition": ("definition", "section 2.1.1, p.4"),
    "vqa-doc-scope": ("scope", "preface, p.3"),
    "sturm-setup": ("setup", "abstract"),
    "sweke-scope-regression": ("scope", "abstract"),
    "hubbard-scope": ("scope", "section VII: the inputs the results rest on"),
    "thabet-limit-real-world": ("stated limit", "section 6"),
    "qsvr-setup": ("setup", "abstract"),
    # g08
    "spinchain-simulated-python": ("setup", "section 7, p.6"),
    "spinchain-open-questions": ("stated limit", "section 8"),
    "dpm-carleman-truncation-limit": ("stated limit", "the Carleman linearization section, p.4"),
    "dpm-scope-excludes-state-prep": ("scope", "main results, after Theorems 1 and 2"),
    "dreinforce-benchmark-setup": ("setup", "abstract and Results"),
    "dreinforce-quantum-inspired-only": ("definition", "the method section: inspired by quantum annealing"),
    "quasciml-problem-specific": ("stated limit", "conclusions"),
    "ring-setup-ibm": ("setup", "section I"),
    "vqls-qsvm-simulator-only": ("stated limit", "sections IV and V"),
    "qel-simulation-setup": ("setup", "section V"),
    "quark-simulated-small-scope": ("scope", "sections 5 and 6"),
    # g09
    "qracle-sim-setup": ("setup", "section V, Datasets"),
    "sequel-network-setup": ("setup", "Methods and Fig. 1"),
    "sequel-coherent-not-run": ("stated limit", "Results, quantum coherent training, p.6"),
    "sequel-proof-of-principle": ("stated limit", "Conclusions, p.6"),
    "kmeans-datasets-setup": ("setup", "section 3.2, p.4"),
    "kmeans-misclassification": ("stated limit", "section 5, p.8"),
    "pulsed-sim-setup": ("setup", "sections I and IV-A"),
    "pulsed-stated-limits": ("stated limit", "section V, p.11"),
    "pulsed-noise-range": ("scope", "section IV-C: a stress test beyond typical gate error rates"),
    "cql-demo-setup": ("setup", "numerical demonstrations (a), p.5"),
    "cql-complexity-open": ("stated limit", "numerical demonstrations, p.5"),
    "radar-data-setup": ("setup", "sections 4.1 and 4.5"),
    "radar-cost-limit": ("stated limit", "section 6.1, p.12"),
    "hqk-sample-sizes": ("setup", "sections V-A2 and V-B"),
    "fin-simulation-only": ("setup", "section V-A, p.15"),
    # g10
    "vqsm-h4-scope": ("scope", "abstract"),
    "vqsm-deep-circuit-limit": ("stated limit", "the convergence section, near Fig. 9"),
    "qsrf-simulator-only": ("stated limit", "the cost analysis and Future Work"),
    "qms-qram-assumption": ("setup", "abstract"),
    "qms-kmeans-qram-constant-time": ("scope", "section III: the QRAM loading the K-means result assumes"),
    "pptnqfe-no-qa": ("scope", "section 1.3, p.2"),
    "pptnqfe-noise-overhead-limit": ("stated limit", "Conclusions, pp.12-13"),
    "qpatch-dataset-setup": ("setup", "section III"),
    "qpatch-limits": ("stated limit", "section IV"),
    "mutation-simulator-setup": ("setup", "section V"),
    "nn-state-prep-limits": ("stated limit", "section IV, Limitations"),
    "atom-pretrain-setup": ("setup", "sections 3 and 4"),
    # g11
    "learning-needs-n-qubit-memory": ("scope", "abstract, item 3"),
    "no-spam-robustness": ("stated limit", "section 1.4, open question 2"),
    "compressibility-limited-to-random-maps": ("stated limit", "the numerical section, p.5"),
    "scaling-limit-20-qubits": ("stated limit", "conclusion and future work"),
    "no-hardware-validation": ("stated limit", "conclusion and future work"),
    "parameter-counts-10-node": ("setup", "the numerical experiments: the circuits as built"),
    "not-every-qml-algorithm": ("scope", "introduction"),
    "no-empirical-comparison": ("stated limit", "section V, Discussion"),
    "no-success-probability-bound": ("stated limit", "the appendix on QSVT conditioning"),
    "noise-not-tested": ("stated limit", "conclusion"),
    # g12
    "bincoletto-evaluation-setup": ("setup", "section II.A, data generation"),
    "bincoletto-scope-hydrogenic-only": ("scope", "section II.A"),
    "blanchette-program-aim": ("setup", "abstract: the authors' own program"),
    "bonan-lsp-definition": ("definition", "section 3, Definition 6"),
    "bonan-experiment-setup": ("stated limit", "section 4.1"),
    "borle-no-hardware": ("stated limit", "section 7, Future work"),
    "bose-limits-simulation-only": ("stated limit", "section VI"),
    "boulebnane-scope-one-layer": ("stated limit", "sections I and VI"),
    "campbell-scope-commuting-encoders": ("stated limit", "section VII.A, item 1"),
    "campbell-initialisation-time-only": ("stated limit", "section VII.A, item 4"),
    "campbell-numerical-truncation": ("stated limit", "section VII.A, numerical limitations"),
    "canonici-experimental-setup": ("setup", "section 9"),
    "canonici-qpu-training-only": ("scope", "section 1"),
    # g13
    "scope-limit-future-simulation-may-reach": ("stated limit", "section 5, p.18: the limit of its intractability claim"),
    "scope-not-comprehensive-review": ("scope", "preface"),
    "qaoa-hybrid-definition": ("definition", "section 2.5, p.20"),
    "scope-single-round-algorithms": ("scope", "introduction, p.2"),
    "setup-5-city-noise-free-statevector": ("setup", "section V.A, p.6"),
    "setup-10-instances-depth-up-to-3": ("setup", "section V.A, p.6"),
    "no-quantum-advantage-established": ("stated limit", "section V, p.16"),
    "setup-ibm-up-to-156-qubits-statevector": ("setup", "introduction, p.3"),
    "setup-100-states-70-training": ("setup", "Results, p.4"),
    "limit-exponential-scaling-bottleneck": ("stated limit", "Discussion, pp.7-8"),
    "limits-engineered-features-thresholding-baselines": ("stated limit", "section 5, p.20"),
    # g14
    "gbs-proof-of-principle-small": ("stated limit", "section VII, Conclusion"),
    "qnn-bitflip-more-than-two-errors": ("stated limit", "section 4, Limitations of this Approach"),
    "hwaware-qsvm-limitations": ("stated limit", "section IV.E, Limitations"),
    "moe-fraud-dataset-setup": ("setup", "section 3.1"),
    "mm-vqe-molecular-limit": ("stated limit", "section IV, p.3"),
    "kmeans-scope-balanced-qram": ("scope", "section 1.2: balanced clusters; QRAM query complexity"),
    "safe-qml-simulator-scope": ("stated limit", "section 6 and section 3.1"),
    "qsl-threshold-and-open-question": ("stated limit", "section 1.3"),
    # g15
    "das-jc-model-limits": ("scope", "Discussion, p.12: the master equation and the decay left out"),
    "daskin-vqpm-setup": ("setup", "Fig. 10 caption and section 5"),
    "deborba-kernel-scope": ("scope", "English abstract"),
    "deleon-vqe-limits": ("stated limit", "sections III and VI"),
    "demidik-datasets": ("setup", "section IV"),
    "demidik-limits": ("stated limit", "section V"),
    "derieux-limits": ("stated limit", "sections 2 and 4"),
    # g16
    "du-setup-sim": ("setup", "section III, p.4"),
    "falabella-setup": ("setup", "section 5, pp.9-11"),
    "not-hidden-variable": ("scope", "section VI, p.12"),
    "finite-history-open": ("stated limit", "section VI d, p.13"),
    "qgat-setup": ("setup", "section 4, p.7"),
    # g17
    "ferber-or-query-model": ("setup", "abstract: the query model"),
    "ferreira-qrc-simulation-only-scope": ("stated limit", "introduction and section III.B"),
    "finet-emulation-limit": ("stated limit", "sections 2.4 and 5"),
    "fischbach-review-scope": ("scope", "abstract"),
    "fleury-didactic-scope": ("scope", "section 3, Conclusion"),
    "flores-garrigos-32-qubit-limit": ("stated limit", "section IV, datasets"),
    "gacon-dualqte-fidelity-drawback": ("stated limit", "section 7.4, p.136"),
    # g18
    "galvis-gpq-simulator-only": ("scope", "introduction and section 7"),
    "gandhi-dqgp-simulator-setup": ("stated limit", "section 4, experimental setup"),
    "gerlach-mapf-hardware-limit": ("stated limit", "section 5, Quantum Hardware Limitations"),
    "gharibyan23-barren-plateau-claim": ("scope", "abstract"),
    "gharibyan25c-no-advantage": ("stated limit", "sections 4.3 and 5"),
    "gharibyan25l-coarse-verification": ("stated limit", "section 5"),
    "gherib-cvdv-scope": ("scope", "introduction"),
    "gherib-cvdv-limitations": ("stated limit", "section III F"),
    "ghosh-harmonic-no-qc-compare": ("scope", "section 3"),
    # g19
    "qcc-net-synthetic-data-setup": ("setup", "section IV.B and the Fig. 4 caption"),
    "qcc-net-simulated-kernels-limit": ("stated limit", "abstract and section V"),
    "imps-circuits-scope-2site-1d": ("scope", "sections II and IV"),
    "qwgan-bioprocess-setup": ("setup", "section 4"),
    "qwgan-bioprocess-hardware-limit": ("stated limit", "section 6"),
    "xqml-two-novel-explanation-methods": ("definition", "abstract and section V: the methods the paper proposes"),
    "xqml-numerics-no-superiority-claim": ("scope", "sections IV and V"),
    "xqml-scalability-limit": ("stated limit", "section V"),
    "qnbm-further-evidence-required": ("stated limit", "section 4, Outlook"),
    "distributed-qelm-simulation-only": ("stated limit", "section VI"),
    "q2sar-dataset-and-pca-setup": ("setup", "section III.A"),
    "q2sar-single-best-kernel-reported": ("scope", "section III.B"),
    "q2sar-single-split-limit": ("stated limit", "section VI"),
    "ml-for-qc-specialists-scope": ("scope", "section 1.2"),
    # g20
    "spe-evaluation-setup": ("setup", "Conclusion"),
    "gonon-bounds-limits": ("stated limit", "sections 1 and 5"),
    "gross-memory-limit-large-n": ("stated limit", "section II"),
    "gutierrez-ideal-assumptions-limit": ("stated limit", "Conclusion"),
    "habibi-future-work-limits": ("stated limit", "section 7, future work"),
    # g21
    "ippdt-limits": ("stated limit", "section 6"),
    "medq-setup": ("setup", "section 5.1"),
    "medq-theory-gap": ("stated limit", "section 6.1"),
    "bnsl-qram": ("stated limit", "section 1"),
    "qsgd-setup": ("setup", "abstract and section 4.1"),
    "phase-space-no-escape": ("stated limit", "section 5.1"),
    "qpe-setup": ("setup", "section IV.B"),
    # g22
    "egas-hardware-not-yet": ("stated limit", "section V"),
    "qb-qdk-training-setup": ("setup", "the paper's list of its own conditions (i) and (iii)"),
    "qb-qdk-misclassification-noise": ("stated limit", "results discussion"),
    "ensemble-control-no-backaction": ("stated limit", "section 6"),
    "annealer-overheads-excluded": ("stated limit", "section 5"),
    "annealer-digit-test-small": ("scope", "section 4.2"),
    "qpinn-quantum-inspired-kernel": ("definition", "sections I and V: what the method is"),
    "qpinn-dataset-scale": ("setup", "abstract"),
    "qpinn-limits-transfer-generality": ("stated limit", "section IV.B"),
    "replica-open-limits": ("stated limit", "section V"),
    "power-of-data-open-limits": ("stated limit", "Discussion"),
    "qgoa-scope-early-stage": ("scope", "sections VI and VII"),
    # g23
    "qkbandit-stated-limits": ("stated limit", "Appendix L"),
    "analogqk-simulation-only": ("setup", "benchmark results section"),
    "margin-noise-open-question": ("stated limit", "Conclusion"),
    "vmf-practical-algorithm-deferred": ("stated limit", "section V"),
    "qsynth-scope-limits": ("stated limit", "Discussion"),
    "rmmc46-low-momentum-limit": ("stated limit", "section 5.1"),
    "santaqlaus-simulation-scope": ("stated limit", "the simulation sections and the outlook"),
    "qgp-scalability-condition": ("stated limit", "p.5, the limit of Theorem 1"),
    "qgp-no-gp-gaussian-pauli": ("proved result", "Theorem 2, with Theorems C.3 and C.4: Gaussian states with Pauli "
                                                   "observables in B4"),
    # g24
    "no-advantage-claim": ("scope", "section V, p.12"),
    "boston-setup": ("setup", "section 4"),
    "annealer-limits": ("stated limit", "the thesis Abstract and Summary"),
    "shadow-advantage-theorem": ("proved result", "Theorem 1 (informal statement; proof in the Appendix): under the "
                                                  "hardness of the discrete cube root"),
    "shadow-example-contrived": ("stated limit", "section IV, Discussion"),
    "qdl-taxonomy": ("definition", "abstract: the review's taxonomy"),
    "zero-discord-scope": ("scope", "abstract"),
    # g25
    "lstm-scope-eight-qubits": ("setup", "abstract"),
    "lstm-limit-multiqubit": ("stated limit", "section 6, p.9"),
    "shot-framework-setup": ("setup", "abstract, p.1, and section 4"),
    "shot-limit-no-hardware": ("stated limit", "section 5, p.15"),
    "hamqaoa-limit-landscape": ("stated limit", "section VI, p.17"),
    "kqw-limit-k3": ("stated limit", "section III, discussion of Tables II and III"),
    "underdet-method-setup": ("definition", "Introduction, p.2: the score the paper applies"),
    "qham-limit-hardware": ("stated limit", "section 4.1"),
    "mediation-scope": ("setup", "abstract, p.1"),
    "mediation-limits": ("stated limit", "Discussion, p.10"),
    "qrf-open-question": ("stated limit", "section V, p.10"),
    # g26
    "dataset-2829-annotation-kappa": ("setup", "section 3 and threats to validity"),
    "researcher-bias-threat": ("stated limit", "threats to validity"),
    "simulation-memory-limit": ("stated limit", "the authors' statement of their experiments' limit"),
    "default-config-scope": ("scope", "section IV"),
    "open-problem-limit": ("stated limit", "section 5"),
    "pbtmax-breaks-classical-threshold": ("proved result", "abstract, a main result proved in the paper: for bipartite "
                                                           "states and one-way classical teleportation"),
    "tight-bounds-scope": ("scope", "abstract"),
    "open-problem-two-qubit": ("stated limit", "Conclusion"),
    "proposed-vqa": ("definition", "abstract: the algorithm the paper proposes"),
    "demo-size": ("scope", "section 5"),
    "hyperparameter-sensitivity": ("stated limit", "section 5"),
    "stated-limitations": ("stated limit", "section 5, Limitations"),
    "simulator-only": ("stated limit", "the QAOA experiment section"),
    "future-work-larger": ("stated limit", "Conclusion"),
    # g27
    "damped-oscillator-bqp-hard": ("proved result", "Theorem 8, section 4: additive precision, damping bounded by an "
                                                    "inverse polynomial in the number of qubits"),
    "damping-gap-open": ("stated limit", "section 6, open problems"),
    "a-graph-no-data": ("scope", "section VIII, data availability"),
    "a-graph-future-scope": ("stated limit", "section VII, Conclusion"),
    "iqm-results-pending": ("stated limit", "Table 10 note, p.21"),
    "afqmc-ad-limits": ("stated limit", "section III and Conclusion"),
    "wsbd-proof-sgd-only": ("scope", "Appendix A, proof scope paragraph"),
    "lan-open-noise": ("stated limit", "section 5, future work"),
    "thesis-runtime-parameters": ("stated limit", "thesis conclusion, p.175"),
    "laneve-open-epsilon": ("stated limit", "section V, Conclusions"),
    # g28
    "egate-nnvqe-initializer-not-solver": ("stated limit", "section 6, p.13"),
    "egate-benchmarks-controlled-topologies": ("scope", "section 6, p.13"),
    "pqlm-tiny-model-scope": ("stated limit", "section 4.3"),
    "qmd-quantum-inspired-basis": ("definition", "abstract, p.1: the method the paper proposes"),
    "qmd-blind-docking-future-work": ("stated limit", "Conclusions"),
    "qpod-qdkl-nisq-limits": ("stated limit", "section 3, Discussion"),
    "qpod-qdkl-experiment-setup": ("setup", "section 4.1"),
    "qsph-simulator-only-limits": ("stated limit", "section 5, p.23"),
    "vqa-constrained-loss-global-minimum": ("proved result", "Theorem 1, section III.B: for the paper's loss, with "
                                                             "every infeasible solution given a higher loss"),
    "vqa-constrained-comparison-scope": ("scope", "section IV"),
    "vqa-constrained-efficient-oracle-assumption": ("setup", "Introduction: the framework's stated assumption"),
    # g29
    "pqmr-sharing-scope": ("setup", "End Matter D1 and the Fig. 4 caption"),
    "qcnn-task-setup": ("setup", "section 4"),
    "vqa-ideal-scope": ("scope", "Introduction"),
    "gc-hybrid-design": ("definition", "abstract: the method's design"),
    "gc-qubit-limit": ("stated limit", "Discussion"),
    "hpqs-limit": ("stated limit", "section 5, Limitations and Future Work"),
    "qrkd-simulation-limit": ("stated limit", "section 5"),
    # g30
    "vqmps-sim-budget": ("setup", "section V, p.8"),
    "vqmps-stated-limit": ("stated limit", "Conclusion, p.8"),
    "qrc-numerical-scope": ("scope", "abstract"),
    "bh-qrc-size-limit": ("stated limit", "Conclusions"),
    "qae-setup": ("setup", "section VII.B"),
    "ssp-mps-limit": ("stated limit", "section V, Conclusions and Outlook"),
    "qlustering-proof-of-concept-scope": ("scope", "Introduction"),
    "classical-verification-sparse": ("proved result", "Theorem 3, main text: a classical client with the random "
                                                       "example oracle, sparse Fourier coefficients"),
    "rectification-noise-limit": ("stated limit", "after Theorem 1, main text"),
    "trigger-label-circularity": ("stated limit", "section 6.5"),
    "trigger-split-and-inputs-limit": ("stated limit", "section 6.5"),
    # g31
    "hep-simulated-data-setup": ("setup", "abstract, p.1"),
    "resource-analysis-needed": ("stated limit", "section IV.C, p.7"),
    "tutorial-logical-model-scope": ("scope", "abstract, p.1"),
    "deutsch-jozsa-not-practical": ("stated limit", "section 4.4"),
    "vqa-ansatz-scope": ("setup", "abstract, p.1"),
    "photonic-conjectured-scaling-limit": ("stated limit", "section 5, p.21"),
    "photonic-fixed-photon-number-scope": ("scope", "section 5, p.21"),
    "qmu-evaluation-setup": ("setup", "abstract, p.1"),
    "qmu-class-level-only": ("stated limit", "section 4, p.7"),
    "vqa-framework-three-metrics": ("definition", "abstract, p.1: the framework the paper proposes"),
    "vqa-framework-proof-of-concept": ("setup", "abstract, p.1"),
    "vqa-framework-single-instance-limit": ("stated limit", "the limitations section"),
    "qaoa-xy-backtest-universe": ("scope", "abstract and the depth-scaling diagnostics"),
    "state-decay-needs-ancillas": ("stated limit", "section V"),
    "no-hardware-implements-nonunitary-gate": ("stated limit", "section F"),
    # g32
    "cv-qfl-gaussian-no-advantage": ("stated limit", "Discussion, p.16"),
    "cmps-expressibility-not-trainability": ("stated limit", "Conclusions, p.17"),
    "variational-symmetry-and-depth-limits": ("stated limit", "abstract, p.1, and Introduction, p.2"),
    "framework-no-practical-advantage-claim": ("scope", "Introduction, p.1, and Conclusions, p.14"),
    "zx-rl-initial-study-scope": ("stated limit", "section V"),
    "qvas-scaling-not-yet-realised": ("stated limit", "sections 8.4 and 9"),
    "qsm-small-scale-and-classical-simulable": ("stated limit", "sections III and V"),
    "qubo-anomaly-not-solvable-on-qpu": ("stated limit", "section 4, p.7"),
    "qubo-anomaly-fraud-dataset-setup": ("setup", "section 3.2.3"),
    # g33
    "cartpole-setup": ("setup", "section 3"),
    "lipschitz-limitation": ("stated limit", "section 6"),
    "no-bp-guarantee-beyond-threshold": ("stated limit", "section I"),
    "preliminary-evidence-limit": ("stated limit", "section I and the results discussion"),
    "not-random-generatable": ("proved result", "section 1, contribution 1, proved in the appendix: conditional on "
                                                "BQP not in the second level of the polynomial hierarchy"),
    "heuristic-assumption-scope": ("scope", "section 1"),
    "exclusively-theoretical": ("scope", "reproducibility statement"),
    "dequantization-open": ("stated limit", "thesis chapter 8"),
    "ideal-simulator-scope": ("setup", "the computational details"),
    "lrqaoa-scope": ("setup", "abstract"),
    "raw-performance-scope": ("scope", "the benchmark design discussion"),
    # g34
    "gibbs-no-mixing-time-shortcut": ("stated limit", "Introduction, pp.1-2"),
    "gibbs-scope-periodic-tori": ("scope", "Introduction, p.2"),
    "gdqlc-setup-simulation-no-qaoa-baseline": ("scope", "section 4, p.5"),
    "gdqlc-limits-size-hardware-theory": ("stated limit", "sections 4 and 5"),
    "qmlhcs-setup-quantum-inspired-classical": ("setup", "section V.A"),
    "qmlhcs-minimal-validation-limit": ("stated limit", "Introduction"),
    "hindi-qnlp-setup-simulated-250-sentences": ("setup", "sections 5 and 6"),
    "hindi-qnlp-no-hardware-yet": ("stated limit", "section 7"),
    "eqs-scope-simulation-and-onetime-cost": ("scope", "Introduction, p.2"),
    "bhmass-setup-sdss-simulation": ("setup", "sections 4.2 and 6"),
    "bhmass-simulation-idealized-limit": ("stated limit", "Discussion"),
    "som-may-detect-graph-geometry-not-chaos": ("stated limit", "Discussion"),
    "acls-scope-pure-state-closed-system": ("scope", "abstract and section 6"),
    # g35
    "qupid-setup-simulator-20-qubits": ("setup", "section V, Experimental Setup"),
    "exact-learning-definition-threshold": ("definition", "Definition 2.3 and the threshold choice, section 2"),
    "faithful-ml-baseline-and-tuning-scope": ("setup", "section 3"),
    "qcbm-preprocessing-setup": ("setup", "section IV.B"),
    "qcbm-stated-limitations": ("stated limit", "sections VI.B and VI.D"),
    "qsvm-simulation-only-limit": ("stated limit", "section VI.F, Simulated quantum hardware"),
    "qsvm-scope-single-dataset-svm-baselines": ("stated limit", "section VI.F"),
    "quanv-ae-fixed-random-quantum-filters": ("setup", "section 3"),
    "benchmark-dependence-stated-limits": ("stated limit", "sections III and IV"),
    # g36
    "training-experiment-underdimensioned": ("stated limit", "section III.B.2"),
    "lookback-scope-black-scholes": ("scope", "sections 1 and 2.1"),
    "lookback-variational-limits": ("stated limit", "section 5.3.1"),
    "multichip-limits-and-design": ("stated limit", "sections 3.1 and 6"),
    "ibm-mnist-study-bounds": ("stated limit", "Conclusion"),
    "hhl-hardware-scale": ("setup", "Conclusion"),
    "hhl-restricted-matrices": ("scope", "the paper's statement of the matrices it considers"),
    "qchop-simulation-setup": ("setup", "section IV"),
    "qchop-penalty-contingent": ("stated limit", "section V"),
    "qchop-inequality-constraints": ("stated limit", "section V"),
    "qdataset-52-datasets": ("definition", "thesis chapter 3 abstract: what the QDataSet contains"),
    # g37
    "pirnay-structured-data-limit": ("stated limit", "section V"),
    "quast-feasibility-definition": ("definition", "the paper's feasibility criterion"),
    "quast-prototype-validation-stage": ("stated limit", "the paper's statement of its validation status"),
    "protsenko-simulation-only-proof-of-concept": ("scope", "the paper's statement of its setup"),
    "ptacek-scope-future-work": ("scope", "abstract and Conclusion"),
    "qrun-classical-surrogate-scope": ("scope", "the paper's statement of its approach"),
    "quyen-classical-svm-limit": ("stated limit", "Conclusion"),
    "raj-small-simulated-scope": ("stated limit", "the paper's statement of its scope"),
    "raj-nash-equilibrium-training-difficulty": ("stated limit", "the paper's report of a training limitation"),
    "rambach-toy-data-scope": ("stated limit", "the outlook"),
    # g38
    "hamiltonian-paths-4n-minus-6": ("proved result", "Lemma 4.7 with its proof, p.7"),
    "single-shot-definition": ("definition", "Definition 2, p.4"),
    "classification-only-scope": ("scope", "Conclusion, p.11"),
    "study-scope": ("setup", "sections 2.1 and 3.3"),
    "stated-hardware-limit": ("stated limit", "Discussion, p.11"),
    "experiment-sizes": ("setup", "section 5.1 and the Figure 8 caption"),
    "conjecture-general-ansatz": ("stated limit", "section 3, p.9"),
    "study-scope-emulators": ("scope", "abstract and section 3.1"),
    "experiment-scope": ("setup", "section III.C, p.8"),
    "speedup-condition": ("scope", "the complexity analysis, p.5"),
    "classical-amplitude-assumption": ("setup", "the maximization algorithm, p.4"),
    "circuit-size": ("setup", "the complexity analysis, p.5"),
    "proof-of-principle-scope": ("stated limit", "section 8"),
    # g39
    "qcml-bond-data-setup": ("setup", "sections 4, 5.1 and 6.1"),
    "qcml-bond-limits-no-uniform-claim": ("stated limit", "sections 5.2, 6.2 and 8"),
    "vcbe-classical-preprocessing-limit": ("stated limit", "abstract and section 6"),
    "xqml-run-scope-ibm-brisbane": ("scope", "section 5"),
    "pauli-exp-scope-1d-future-work": ("scope", "section IV"),
    # g40
    "sarkar-setup-noiseless-9-params": ("setup", "sections I and IV"),
    "sarkar-scaling-open-question": ("stated limit", "sections I and IV"),
    "sauvage-limits-utility-beyond-classical": ("stated limit", "sections I and V"),
    "schetakis-setup-data-simulated": ("setup", "sections 3.1 and 5"),
    "schetakis-limits-equivalence-qubits": ("stated limit", "sections 5 and 6"),
    "schwabe-setup-params-simulated": ("setup", "sections II and III"),
    "shah-quantum-kmeanspp-guarantee": ("proved result", "Theorem 1, p.2: the QRAM model, O(log k) approximation with "
                                                         "probability at least 0.99"),
    "shah-dequantized-qi-kmeanspp": ("proved result", "Theorem 2, p.3: O(log k) approximation in expectation with "
                                                      "probability at least 0.99"),
    "shah-limit-aspect-ratio": ("stated limit", "section 5"),
    "shao-setup-clifford-pauli-rotations": ("setup", "sections I and II: the method's assumptions"),
    "sharma-setup-split": ("setup", "section IV.A"),
    # g41
    "autoqresearch-llm-not-isolated": ("stated limit", "section VII.D"),
    "autoqresearch-hardware-single-run": ("stated limit", "the hardware validation section"),
    "shofar-assumption-sampling-noise": ("scope", "sections I.B and VI"),
    "dvqls-no-hardware-no-noise": ("stated limit", "section III, closing discussion"),
    "shmueli-power-open": ("stated limit", "section 1.3"),
    "singh-pokhrel-setup": ("setup", "section 2"),
    "singh-pokhrel-preliminary": ("stated limit", "Conclusion"),
    "singh-hhl-simulator-setup": ("setup", "section 5.1"),
    "singh-hhl-limits": ("stated limit", "section 6.2"),
    "medmnist-not-beating-classical": ("stated limit", "section 3"),
    # g42
    "daqc-hw-scope": ("setup", "section 2.2"),
    "daqc-qubit-limit": ("stated limit", "section 2.1"),
    "singh-qml-review-scope": ("scope", "abstract"),  # renamed in group_g42.json: g03 already holds "review-scope"
    "suite-setup": ("definition", "abstract: what the paper delivers"),
    "boqgan-sim-scope": ("stated limit", "sections 3.8 and 4.3"),
    "tshf-simulation-only": ("stated limit", "sections 4.2 and 6"),
    "sim-exact-only": ("stated limit", "section IV"),
    # g43
    "stationary-noise-breaks-exchangeability": ("scope", "section 3: the condition for Theorem 1's guarantee"),
    "aqcp-evaluation-limits": ("stated limit", "section 5.4, p.17"),
    "qne-optimization-error-not-analyzed": ("stated limit", "section 6, p.28"),
    "quso-classical-simulation-random-instances": ("setup", "abstract"),
    "quso-qaoa-not-near-optimal": ("stated limit", "section VII, p.8"),
    "speedups-asymptotic-idealised-only": ("scope", "section 1.1"),
    "no-near-term-practical-speedup": ("stated limit", "section 5.2, p.24"),
    "linear-kernel-only-simulator": ("stated limit", "sections 1 and 7, pp.2 and 12"),
    "security-semi-honest-only": ("scope", "sections 6.3 and 8"),
    "positive-p-simulation-framework": ("definition", "abstract: what the work presents"),
    "positive-p-limits": ("stated limit", "sections IV.A and IV.B, pp.9-10"),
    "implementation-not-optimized": ("stated limit", "section IV, p.6"),
    "gqpinn-benchmark-scope": ("setup", "abstract"),
    "gqpinn-symmetry-limit": ("stated limit", "section VII"),
    # g44
    "qkm-review-scope": ("scope", "abstract"),
    "real-device-limit-100-samples": ("stated limit", "section 4.1"),
    "qdislib-scope": ("definition", "abstract: the library the paper introduces"),
    "cutting-cost-exponential": ("stated limit", "the overview and Conclusion"),
    "qgfa-test-scale": ("setup", "the test cases and their figure captions"),
    "mcts-limits": ("stated limit", "section VI"),
    "virtuous-cycle-scope": ("scope", "abstract"),
    "qnn-study-limits": ("stated limit", "section 6"),
    # g45
    "tfim-simulation-setup": ("setup", "section 2, p.4"),
    "mcquack-stated-limitations": ("stated limit", "section 6"),
    "meta-dataset-setup": ("setup", "section 4"),
    "future-work-limits": ("stated limit", "section 5, p.14"),
    "no-advantage-claimed": ("scope", "abstract, p.2"),
    "simulation-setup-n6": ("setup", "the numerical test"),
    "utility-limited-blackbox": ("stated limit", "Introduction"),
    "small-qubit-caveat": ("stated limit", "section 3.4, p.67"),
    "toy-dataset-limit": ("stated limit", "the Limitations section"),
    "vdd-scope-small-n-one-ansatz": ("scope", "section IV"),
    "vdd-struggles-tfim-disordered": ("stated limit", "section VII"),
    # g46
    "kcm-succinctness-incomparable": ("proved result", "Theorem 1, section 3; proofs in the appendix"),
    "kcm-fidelity-intractable": ("proved result", "Theorem 3 with Lemma 31 and Corollary 37: conditional on the "
                                                  "exponential time hypothesis"),
    "kcm-practice-untested": ("stated limit", "section 7"),
    "vlasic-performance-link-posited": ("stated limit", "section V.2"),
    "wang22-scope": ("setup", "section 4"),
    "wang23-limit-no-metric": ("stated limit", "section 5"),
    "wang24-scope-single-qubit": ("stated limit", "section V"),
    "wang25-scope": ("scope", "Introduction"),
    "wang25h-setup": ("setup", "section 5"),
    # g47
    "fock-product-state-scope": ("scope", "the paper's statement of its scope"),
    "robust-training-query-cost": ("proved result", "Theorem 1, Methods, proofs in the Appendix: under local stability "
                                                    "and sparsity assumptions"),
    "robust-training-assumed-access": ("scope", "the assumptions of Theorem 1"),
    "robust-training-open-directions": ("stated limit", "Discussion"),
    "qsm-open-scope": ("stated limit", "Discussion"),
    "xgswap-single-device-limit": ("stated limit", "Conclusion"),
    "qtde-small-simulated-scope": ("stated limit", "Discussion"),
    "qtde-no-formal-guarantees": ("stated limit", "Discussion"),
    # g48
    "whitaker-pure-quantum-selection-needs-advances": ("stated limit", "Section 4"),
    "white-scope-vqc-qsvc-pima-8-qubits": ("scope", "Sections II.A and II.C"),
    "wilkie-simulation-scope-no-advantage": ("scope", "Section VI.A"),
    "wilkie-vcg-support-size-limit": ("stated limit", "Sections IV.D and VII"),
    "willsch-qaoa-n40-not-converged": ("stated limit", "Sections 3.4 and 5"),
    "wisniewska-scope-simulation-one-dataset-three-qubits": ("scope", "the setup section"),
    "wu-weakly-noisy-scope-gate-independent-noise": ("scope", "Section 1 and Definition 2"),
    "wu-weakly-noisy-theory-only-gate-dependent-noise-open": ("stated limit", "Appendices B and C"),
    "wu-qcnn-radii-setup-noiseless-simulation": ("scope", "Sections II and IV"),
    "wu-qru-scope-simulation-only": ("scope", "the experimental setup"),
    "wu-qru-limits-no-hardware-no-theory-estimated-baselines": ("stated limit", "the future work section and a table note"),
    # g49
    "nnas-eval-scope": ("scope", "Section III.A"),
    "tqfm-simulation-scope": ("scope", "Section VI"),
    "tqfm-barren-plateau-open": ("stated limit", "Section VII, Conclusion and Prospect"),
    "qnn-spectral-limits": ("stated limit", "the Remarks and Limitations paragraph, Section 1"),
    "qcforest-initial-build-linear": ("stated limit", "Section I.A"),
    "gqsp-optimization-limit": ("stated limit", "the discussion of the numerical results"),
    "qaoa-hc-embedding-limit": ("stated limit", "the Conclusion"),
    "simplex-4-algorithm": ("proved result", "Theorem 3, Section 1.2"),
    # g50
    "yu-setup-noiseless-sim": ("setup", "Section 3.4"),
    "yue-scope-minimal-model": ("stated limit", "Section V"),
    "jiang-infinite-shot-limit": ("stated limit", "Section VI"),
    "jiang-two-qubit-reduced-data": ("setup", "the paper's statement of its setup"),
    "zajac-setup-synthetic": ("setup", "Section 3"),
    "zajac-proof-of-concept": ("stated limit", "Section 8"),
    "zakavati-setup-lindblad": ("setup", "the paper's statement of its setup"),
    "zanotta-classical-simulation-setup": ("setup", "Section V"),
    "zanotta-hardware-limit": ("stated limit", "Section VI"),
    "zhang-eqas-setup": ("setup", "Section III"),
    "zhang-scope-future": ("stated limit", "the Discussion"),
    # g51
    "qtransformer-survey-two-paradigms": ("scope", "the Abstract"),
    "lean-qbench-limits": ("stated limit", "Section 7.1"),
    "anyon-kernel-scope-two-particle": ("stated limit", "Section VI"),
    "ansatz-2d-scope-limit": ("stated limit", "Section V"),
    "noise-theory-simulation-scope": ("stated limit", "the Discussion, Section III"),
    "qnn-decoder-scope-stabilizer-codes": ("scope", "the Discussion"),
    "qcdge-size-and-scope": ("scope", "the Abstract"),
    "qcdge-calculation-levels": ("setup", "the Abstract"),
    "qcdge-selection-rule-limit": ("stated limit", "Technical Validation, the functional-group analysis"),
    # g52
    "noise-study-scope-effective-model": ("stated limit", "Sections III and IV"),
    "qae-scope-no-advantage-claim": ("scope", "Section 1"),
    "qae-limits-simulator-kernel-only": ("stated limit", "the Section 4 discussion"),
    "contrastive-qml-setup-four-qubits": ("setup", "Sections 2 and 3"),
    "contrastive-qml-hardware-single-draw-limit": ("stated limit", "the Fig. 4 caption and the Discussion"),
    "qbackprop-exponential-classical-overhead-caveat": ("stated limit", "Section 1"),
    "qrc-validation-is-theoretical": ("scope", "the Abstract and Section 1"),
    "photonic-classifier-scope-one-task": ("setup", "Sections III and IV"),
    "photonic-classifier-limit-below-10-photons": ("stated limit", "Section III"),
    "adiabatic-training-scope-simulated-only": ("scope", "Section 5"),
    "adiabatic-training-expressiveness-limit": ("stated limit", "the Conclusions"),
    "cvar-vqa-instance-classically-easy": ("scope", "Section II"),
    "cvar-vqa-no-scaling-inference": ("stated limit", "Section V"),
    # g53
    "rfqrc-circuit-depth-independent": ("setup", "Section III"),
    "dataloading-error-budget-partition": ("setup", "Section V"),
    "quantumgep-quantum-chemistry-limit": ("stated limit", "the Conclusion"),
    "qopf-hardware-limits": ("stated limit", "the Abstract and Section V"),
    "reupload-future-work-real-data": ("stated limit", "the Discussion"),
    # g54
    "scoop-simulation-scope": ("scope", "Section IX"),
    "anwar-classical-data-scope": ("stated limit", "the Introduction"),
    "arai-small-size-limit": ("stated limit", "the Discussion and Conclusion"),
    "arrasmith-scope": ("scope", "the Discussion"),
    "arthur-qubit-limit": ("stated limit", "Section IV"),
    "atchade-limits": ("stated limit", "Sections IV.E and IX"),
    # g55
    "multilevel-qaoa-p1-analytic-scope": ("scope", "Section III"),
    "multilevel-qaoa-open-directions": ("stated limit", "the Conclusion"),
    "dequantization-needs-classical-access": ("stated limit", "the Discussion"),
    "sparse-qsvt-resists-dequantization": ("stated limit", "Section 3"),
    "hamiltonian-learning-open-question": ("stated limit", "a footnote to the introduction"),
    "cvqbm-simulator-only": ("stated limit", "the Introduction and Section 5"),
    "cvqbm-hardware-limit": ("stated limit", "Section 5"),
    "malware-exploratory-scope": ("scope", "the paper's statement of its scope"),
    "aiso-scope-two-applications": ("scope", "the Abstract and the Conclusion"),
    "qite-classically-simulable": ("stated limit", "the Conclusion"),
    "rydberg-sim-not-hardware": ("stated limit", "the Conclusion"),
    # g56
    "altgraph-fake-backend": ("setup", "Section 5"),
    "altgraph-mse-limit": ("stated limit", "Section 5.2"),
    "qnn-graph-small-sim": ("stated limit", "Section V"),
    "trex-single-vqe-run": ("stated limit", "Section V"),
    "hubo-setup-small-cases": ("setup", "Section 4"),
    "qwoa-nonvariational-definition": ("definition", "Section V"),
    "qwoa-benchmarking-future": ("stated limit", "Section V"),
    # g57
    "bermejo-benchmark-scope": ("scope", "the Abstract and the Conclusions"),
    "bertl-review-scope": ("scope", "the start of Section 2"),
    "bhattacharyya-heisenberg-limit": ("stated limit", "Section VI"),
    "bhowmik-survey-scope": ("scope", "the Abstract"),
    "borle-39-variable-limit": ("stated limit", "Section IV"),
    "bowles-data-scope": ("stated limit", "Section III and a footnote"),
    "boy-dataset-scope": ("scope", "Section IV"),
    "bravo-no-advantage-claim": ("stated limit", "Section II and the Conclusion"),
    # g58
    "bucher-guidelines-incomplete": ("stated limit", "Section V"),
    "calzavara-l1-bound-limit": ("stated limit", "Section III"),
    "dibom-trainability-limit": ("stated limit", "Section VII"),
    "dibom-simulation-scale": ("scope", "the paper's statement of its simulations"),
    "dpqnn-scope-33-bus": ("setup", "Section 5"),
    "qnode-framework-adjoint": ("definition", "Sections III and IV"),
    "qnode-tightness-open": ("stated limit", "Sections IV and VI"),
    "carles-stationarity-limit": ("stated limit", "Section VI"),
    "caro-classical-verification-parity": ("proved result", "Theorem 2, proved in Section 6: unconditional for SQ "
                                                            "access, conditional on the hardness of LPN for random "
                                                            "example access"),
    "caro-open-oracle-separation": ("stated limit", "Section 1"),
    "cepaite-runtime-excludes-sampling": ("stated limit", "Sections VII and IX"),
    "cepaite-no-advantage-yet": ("stated limit", "Section IX"),
    "cepaite-scale-and-noise": ("scope", "Section IX"),
    # g59
    "chakraborty-bivariate-scope": ("stated limit", "Section I"),
    "chatterjee-qpu-queue-limit": ("stated limit", "Section III"),
    "chaudhary-proof-of-concept-scope": ("stated limit", "Section IV"),
    "chaudhary-scaling-limits": ("stated limit", "Section VI"),
    "chaudhary-mode-collapse": ("stated limit", "Section IV"),
    "chen2018-simulated-exact-probabilities": ("scope", "Section 5"),
    "chen2020-simple-environments": ("stated limit", "Section VII"),
    "chen2023-setup-simulation-8-qubits": ("setup", "Section VI"),
    # g60
    "hybrid-qnn-maze-noise-free-simulator-scope": ("scope", "Sections I and VI"),
    "hybrid-qnn-maze-stated-technical-constraints": ("stated limit", "Section VI"),
    "qlstm-rc-rl-model-setup": ("setup", "Section 6"),
    "qdqn-dper-experiment-setup": ("setup", "Section 6"),
    "qrl-definition-vqc-policy-value": ("definition", "Section III"),
    "noise-aware-qaoa-benchmark-setup": ("setup", "Section V"),
    "noise-aware-qaoa-error-threshold-setup": ("setup", "Section III"),
    "ae-vqc-qubit-count-amplitude-encoding": ("definition", "the amplitude encoding the paper defines"),
    "ae-vqc-stated-limitations": ("stated limit", "Section 4"),
    "qlstm-qaoa-transfer-training-setup": ("setup", "Section IV"),
    "learnable-observable-method-setup": ("setup", "Sections I and V"),
    "learnable-observable-simulation-scope": ("scope", "the Abstract and Section V"),
    # g61
    "adaboostq-hardware-setup": ("setup", "the paper's statement of its experiment"),
    "uav-simulated-data-no-hardware": ("stated limit", "the Abstract and the Conclusion"),
    "recovery-rate-simulator-proof-of-concept": ("stated limit", "Section 6"),
    "pqkd-simulator-backend": ("setup", "Section 4"),
    "qasa-limits-simulated-training-few-seeds": ("stated limit", "Section 4"),
    "sqsnn-benchmarks-by-classical-simulation": ("scope", "Section V"),
    "qil-simulated-with-tfq": ("setup", "Section V"),
    "sisr-limited-qpu-access": ("stated limit", "a footnote on the first page"),
    # g62
    "cimini-limits-quantumness-simulability": ("stated limit", "Section IV"),
    "coelho-simulator-scope": ("setup", "Section 6 and the Appendix"),
    "collis-scope-simulator": ("stated limit", "Sections IV and V"),
    "coroi-future-work-noise": ("stated limit", "the Conclusion"),
    "correll-cost-limit": ("stated limit", "the paper's discussion of its IonQ run"),
    "correr-scope-noise": ("scope", "the paper's statement of its scope"),
    "cowlessur-small-circuit": ("setup", "the paper's statement of its setup"),
    "cowlessur-privacy-open": ("stated limit", "the Conclusion"),
    # g63
    "coyle-density-qnn-gradient-overhead": ("proved result", "Corollary 1 and Proposition 1: if K = O(log(N)) and "
                                                             "each sub-unitary admits a backpropagation scaling"),
    "coyle-density-qnn-scope-fixed-structure": ("scope", "the Results"),
    "cranganore-hybrid-wms-architecture": ("scope", "Section 8"),
    "cranganore-limit-code-classification-labels": ("stated limit", "Section 6"),
    "cranganore-limit-photonic-circuit-model": ("stated limit", "Section 6"),
    "dasilva-setup-site-simulator-split": ("setup", "Sections II and III and the Acknowledgements"),
    "dasilva-limit-dataset-resolution": ("stated limit", "the Conclusion"),
    "dalyac-repetition-rate-few-hz": ("stated limit", "Box 4"),
    "dangwal-setup-simulation-sizes": ("setup", "Section 6"),
    "dangwal-limit-other-mitigation-not-evaluated": ("stated limit", "Section 7"),
    "dave-setup-simulation-300-points": ("setup", "Sections I and IV"),
    "oliveira-qocc-one-qubit-measurement": ("definition", "the Introduction and Section V"),
    "oliveira-setup-simulator-two-devices": ("setup", "Section I"),
    "oliveira-limit-multiclass-parameters": ("stated limit", "Section VII"),
    # g64
    "maxcut-tests-single-node-scope": ("scope", "Section V"),
    "simulated-with-yao-julia": ("setup", "Section 4"),
    "kernels-simulated-tensor-network-gpu": ("setup", "the Abstract"),
    "fidelity-kernels-classically-simulable-limit": ("stated limit", "Section I"),
    "docking-12-qubit-local-optima-limit": ("stated limit", "Sections III and IV"),
    "all-experiments-ideal-noise-free-simulator": ("scope", "Section 4"),
    "gbls-theorem2-sampling-probability": ("proved result", "Theorem 2, under the optimal setting; proof in Appendix A"),
    "gibbs-variety-independence-model": ("proved result", "Theorem 5.5, Section 5: for any graph G with N vertices"),
    "qcmi-variety-irreducibility-open": ("stated limit", "Question 3.12, Section 3"),
    # g65
    "scope-max-clique-simple-graphs": ("scope", "the Introduction"),
    "theorem1-restricted-environments": ("scope", "the text following Theorem 1"),
    "theorem1-oracle-and-not-quantitative": ("stated limit", "the text at Theorem 1"),
    "control-over-interactions-challenging": ("stated limit", "the Conclusion"),
    "equal-coupling-assumption": ("setup", "Section 2"),
    "noiseless-simulation-only": ("stated limit", "the Conclusion"),
    "simple-system-not-general-claim": ("stated limit", "the Conclusion"),
    "survey-scope-gate-computing": ("scope", "the Introduction"),
    "exploratory-no-scaling": ("stated limit", "the section on the digit data"),
    "exponentially-long-circuit-some-labels": ("stated limit", "the Abstract"),
    # g66
    "qglm-setup-simulated-4-components": ("setup", "the paper's statement of its setup"),
    "nisq-qpf-test-scope": ("scope", "the case-study section"),
    "qps-update-limitation": ("stated limit", "the discussion of the Gram-Schmidt update"),
    "quadro-limits": ("stated limit", "the paper's statement of its limits"),
    "qphase-setup-simulated-data": ("setup", "the paper's statement of its setup"),
    "opmech-abstraction-timing": ("setup", "the paper's description of its course"),
    "opmech-linear-algebra-caveat": ("stated limit", "the paper's description of its course"),
    "nnqmc-ph-limits": ("stated limit", "the paper's statement of its limits"),
    "deepvqe-scope": ("scope", "the Abstract and the numerical demonstrations"),
    # g67
    "galvao-simulation-setup": ("setup", "Section I"),
    "galvis-simulation-setup": ("setup", "Section IV"),
    "galvis-variance-distant": ("stated limit", "Section IV"),
    "galvis-time-parameter-sensitivity": ("stated limit", "Section V"),
    "ganguly-dataset-setup": ("setup", "Section III"),
    "georgiou-bounds-scope-assumption": ("stated limit", "the text after Theorem 3"),
    "gerlach-experiment-setup": ("setup", "Section 4"),
    "gerlach-correlation-form-depends-on-kernel": ("stated limit", "Section 4"),
    "gheisarnejad-qdrl-scheme-and-testbed": ("setup", "the Abstract and Section 5"),
    "gheisarnejad-proof-of-concept-only": ("stated limit", "Section 6"),
    "ghosh-threat-model": ("scope", "the Abstract"),
    "gili-simulator-only-hardware-open": ("stated limit", "Fig. 1 and Section IV"),
    # g68
    "supervised-only-no-experiment": ("stated limit", "Section V"),
    "white-paper-scope": ("scope", "the Abstract"),
    "kdm-quantum-inspired-exploratory": ("scope", "Sections 1 and 4"),
    "qrc-experiment-setup-limits": ("stated limit", "Section III"),
    "fairness-limits-random-models": ("stated limit", "Sections 6 and 7"),
    "quprofs-limitations": ("stated limit", "Limitations and Future Work"),
    "quprofs-eval-scope": ("setup", "the Abstract"),
    "gsa-role-of-qpu": ("scope", "Section III"),
    "gsa-open-scaling": ("stated limit", "Section III"),
    "quanbench-setup": ("setup", "the Abstract and Section I"),
    "quanbench-limits": ("stated limit", "Section VI"),
    # g69
    "haghparast-six-step-curriculum": ("scope", "Section I"),
    "haghparast-no-evaluation-yet": ("stated limit", "Section VIII, Future Works"),
    "halder-rbm-setup": ("setup", "Section III"),
    "halder-rbm-limits": ("stated limit", "Section II and the Conclusions"),
    "enqode-eval-setup": ("setup", "Section V"),
    "hasanzadeh-uc-survey-scope": ("scope", "the Abstract"),
    "dvqe-no-speedup-simulator": ("stated limit", "the Conclusion"),
    "hassanshahi-advantage-open": ("stated limit", "Section 5"),
    "he-simulation-scope": ("scope", "Section 4"),
    "hegde-position-three-strategies": ("scope", "the Abstract"),
})

# The LOW reasons, from store.grading.
EMPIRICAL = low_grade("measured result")[1]
AUTHOR_CLAIM = low_grade("authors' claim")[1]
CITED = low_grade("cited claim")[1]
FIELD = low_grade("field statement")[1]
# A theoretical result (a proof, derivation, bound or scaling, argued but not run) kept LOW, with the cause.
THEORY_LOW: dict[str, str] = {
    "qbtree-range-query-independent-of-output": "g02: the quotes carry the paper's summary, not Theorem 4.4 itself",
    # g03: an analysis of the algorithms' stated resource counts, not a run and not a proof
    "pareto-reduction-two-dense-two-sparse": "g03: a Pareto analysis of published resource counts, not a proof",
    "dense-reduces-to-zhang21a-unitary": "g03: a Pareto analysis of published resource counts, not a proof",
    "sweke-exact-kernel-eval": "g07: the quotes carry the paper's summary; the section 4 derivation was not read",
    "thabet-expressivity": ("g07: the propositions were read as statements only, and the paper says part of the "
                            "distinction is shown by experiment"),
    "dpm-solver-query-complexity": ("g08: informal Theorem 1; the quote stops before the complexity it states, and "
                                    "the proof in the supplement was not read"),
    "quark-query-complexity": "g08: the quote is the paper's summary of its proof; the proof was not read",
    "vqsm-tridiagonal": "g10: the abstract's summary; the conditions it names are not quoted",
    "qms-quadratic-speedup": "g10: the abstract's claim; the complexity analysis was not quoted, and it assumes a QRAM",
    # g11: a theorem's statement quoted from the abstract or introduction, without its conditions; proofs not read
    "hamiltonian-learning-memory-tradeoff": "g11: the abstract's summary; the subroutines' proofs were not read",
    "fourier-expansion-is-etk": "g11: the introduction's statement; the appendix proof was skimmed only",
    "off-span-prediction-collapse": "g11: the abstract's statement; the reference-free model Theorem 2 assumes is not quoted",
    "exponential-training-directions": "g11: the abstract's statement of Theorem 4; its conditions are not quoted",
    "exact-model-via-sn-qft": "g11: an algorithm design, not run; the appendices were skimmed only",
    "variational-model-universal": "g11: a dissertation's defended result; the chapter 5 proof was not read",
    "physical-hamiltonians-embed-universal": "g11: a dissertation's defended result; the proof was not read",
    "boulebnane-p1-success-probability": "g12: the abstract's statement; the derivations in sections III and IV were not read",
    "campbell-data-agnostic-framework": "g12: the abstract's statement; the derivations in sections II to V were skimmed",
    "degree2-classical-beats-qaoa": "g13: the introduction's summary of Theorem 1; the theorem itself is not quoted",
    "degree3-qaoa-beats-classical": ("g13: the introduction's summary of Theorem 2; its girth and expectation "
                                     "conditions are not quoted"),
    # g14: the abstract's or introduction's statement; the proofs were not read
    "mm-vqe-time-complexity": "g14: the abstract's summary; the complexity appendix was skimmed only",
    "kmeans-uniform-sampling-improvement": "g14: the abstract's summary; the appendix proofs were not read",
    "kmeans-quantum-quadratic-small-regime": "g14: the contributions' summary of Theorem 3.5; its proof was not read",
    "qsl-tomography-implies-lower-bounds": "g14: the abstract's summary of Theorem 1.1; the formal proofs were not read",
    "qsl-decision-problem-extension": "g14: the abstract's summary of Theorem 1.3; the formal proofs were not read",
    "daskin-qlstm-bounds": "g15: the bound is described, not stated; the section 3 derivation is not quoted",
    "lejarza-clustering": "g15: a thesis's summary of its speedups; chapters 4 to 6 were not read in full",
    "qubits-linear-constraints": "g16: a scaling argument from the paper's formulation, not a proof",
    "vqls-dimension": "g16: a dimension count from the authors' construction, argued and not run",
    "positivity-divisibility-tradeoff": "g16: no labeled theorem; the framework's derivations are not quoted",
    "ferber-bounded-degree-graph-theorem": ("g17: Theorem 1.3's quote stops before its bound, which pdftotext garbles; "
                                            "the proof was skimmed only"),
    "ferber-optimal-two-cliques-case": "g17: the optimality rests on a cited lower bound; the passage is garbled",
    "fonseca-vqe-complexity": "g17: an operation count for a didactic simple case, not a proved bound or a run",
    "gacon-stochastic-qgt-estimator": "g17: a thesis conclusion's summary; the chapter 5 and 6 derivations were not read",
    "galvis-gpq-poly-advantage": "g18: the abstract's summary; the section 5 complexity analysis was skimmed",
    "galvis-gpq-classical-baseline": "g18: a complexity comparison stated in the introduction, not derived in the quotes",
    "gerlach-mapf-optimality-criterion": "g18: the criterion and its proof are named, not quoted",
    "ghosh-harmonic-exact-2d": "g18: the construction is stated; the section 2.1 derivation was skimmed",
    "qnbm-rus-not-trivially-bayesian": "g19: an argument that one simulation route fails, called a strong suggestion; no hardness proof",
    "qnbm-linearized-model-efficient-sampling": ("g19: a prose derivation in section 3.1; the model it covers, the "
                                                 "linearized network, is named only by contrast"),
    "hamming-exponent-intrinsic-dimension": "g20: a connection the authors establish; no theorem with its conditions is quoted",
    "gonon-noisy-qnn-uat": "g20: the abstract's statement; the theorem's conditions (Theorem 3.17) are not quoted, proofs not checked",
    "gross-optimal-observable-method": "g20: a method formulation; the optimality holds under kernel ridge regression assumptions not quoted",
    "gutierrez-two-layer-squeezing-time": ("g20: a derived result; its assumptions (ideal time-reversal, negligible "
                                           "decoherence, weak field) are stated elsewhere"),
    "gutierrez-sequential-layers-constructive": "g20: a derived result under the same unquoted assumptions",
    "habibi-ea-mdp-optimal-policy": "g20: the abstract states a proof; the theorem and its conditions are not quoted",
    "bnsl-speedup": "g21: the running-time bounds are not quoted; only that a speedup holds under a growth condition on F",
    "qsgd-rate": "g21: the rate and the locality conditions are not quoted",
    "phase-space-stinespring": "g21: a derivation summary in section 6; proof not checked by the reader",
    "wasserstein-bound-diagnostic": "g22: the bounds themselves are not quoted",
    "ensemble-control-kld-framework": "g22: a framework proposal; the analytical controller is not quoted",
    "replica-generalization-error-eigentask": "g22: a replica-method calculation; its results are not quoted",
    "prediction-error-bounds-method": "g22: the abstract's statement; the bounds are derived in appendices the reader did not check",
    "classical-ml-with-data-not-guaranteed-advantage": "g22: the conclusion's summary; the bounds behind it are not quoted",
    "qkbandit-approx-kernel-lower-regret": "g23: the regime and the choice of kernel are not stated in the quote",
    "qkbandit-info-gain-exponential": "g23: the bound itself is not quoted",
    "margin-bound-qnn": "g23: the quote describes the bound's property; Theorem 2.1's statement is not quoted",
    "vmf-convergence-theorem": "g23: Theorem 1's statement is cut short in the quote",
    "vmf-scope-eigenvalue-range": "g23: a capability the authors' analysis claims; the eigenvalue range is not quoted",
    "not-all-shadowfiable": "g24: Theorem 5's statement is cut short in the quote",
    "zero-discord-commuting": "g24: Theorem 3.8's statement is cut short in the quote; its proof rests on a cited result",
    "shot-sufficient-theory": "g25: the sufficient shot numbers are not quoted",
    "hamqaoa-guarantees": "g25: the guarantees themselves are not quoted",
    "qrf-query-complexity": "g25: the complexity bound is not quoted, only what it does not depend on",
    "storage-not-sufficient": "g26: the lemma's access model is not named in the quote ('certain efficient quantum access')",
    "corollary-sparse-dequantization": "g26: Corollary 15 is not quoted in full; the quotes give its condition and a reading",
    "strict-hierarchy": "g26: the values and the hierarchy they separate are not quoted",
    "gate-complexity-factor": "g26: the gate-count factor itself is not given in the quote",
    "a-graph-ppt-condition": "g27: the PPT condition is not quoted; the quote is cut short",
    "dla-polynomial-condition": "g27: 'verified', not proved; no statement with its conditions is quoted",
    "thesis-proved-speedups": "g27: a thesis summary of several results; no running time is quoted",
    "laneve-quadratic-speedup": "g27: 'certain sampling distributions' are not named in the quote",
    "laneve-classical-lower-bound": "g27: Theorem 6 is cut off before its bound",
    "midcircuit-filter-and-heuristic-mixer": "g28: 'show mathematically' with no statement of how strong the bias is",
    "vqa-gradient-cost-ol": "g29: Theorem 1's conditions (the ansatz and the cost function) are not in the quote",
    "vqa-one-year-20-qubits": "g29: an extrapolated time estimate in an ideal setting, not a theorem",
    "agnostic-parity-noisy": "g30: Theorem 2's condition (uniform input marginal) is not in the quotes",
    "photonic-fixed-order-polynomial-trainable": "g31: rests on a conjectured scaling the paper states is not yet established",
    "photonic-polynomial-speedup": "g31: the classes of observables and the speed-up are not stated in the quotes",
    "constant-measurement-graph-connectivity": "g31: an algorithm's claimed certainty; no theorem with its conditions is quoted",
    "cv-qfl-gate-complexity": "g32: a derived gate count; no theorem with its conditions is quoted",
    "flipped-model-erm-no-advantage": "g32: the conclusion's summary; the reader did not read the derivation",
    "lce-constant-gradient": "g33: Theorem 2's statement is quoted only in fragments",
    "taylor-surrogate-complexity": "g33: the conclusion's summary of Theorems 3 and 4; proofs not read",
    "identification-advantage": "g33: the 'broad class' of tasks is not defined in the quote",
    "hw-preserving-no-bp": "g33: the connectivity assumptions are 'certain assumptions', not stated in the quote",
    "gibbs-periodic-poly-speedup-mean-estimation": "g34: the query counts are not quoted",
    "gibbs-morse-exponential-precision-suggested": "g34: a comparison the authors say 'suggests' a speedup; not a theorem",
    "acls-geometric-flexibility-needs-joint-dependence": "g34: shown in the pure-state setting; the reader did not read the proofs",
    "tqnn-kjunta-query-complexity": "g35: an upper bound the authors 'found'; its derivation was not read",
    "tqnn-compare-literature": "g35: the regime and the assumption the comparison needs are not in the quote",
    "benchmark-dependence-bound": "g35: the inequality is cut off in the quote",
    "hhl-depth-reduction": "g36: a circuit-depth estimate for a 50-qubit scheme; no derivation is quoted",
    "cartan-analytic-method": "g36: 'certain classes' of symmetric spaces are not named in the quote",
    "pirnay-learner-perfect-precision": "g37: Theorem III.1 is quoted only in fragments",
    "qrun-fourier-claim": "g37: a claim with a proof sketch only",
    "quyen-dl-ml-limits": "g37: cost counts by construction and an observed phenomenon; no theorem is stated",
    "single-shot-bounded-by-distinguishability": "g38: the bound and the 'certain depth' are not quoted; proofs not read",
    "generic-single-shot-not-trainable": "g38: an argument about expressivity, not a stated theorem",
    "gradient-variance-exponent": "g38: derived for one particular ansatz and target that the quote does not name",
    "pac-bayes-bounds-quantum-channels": "g38: the bounds themselves are not quoted; proofs not read",
    "equivariant-tighter-bounds": "g38: Theorem 6 is stated informally; the bound is not quoted",
    "quadratic-speedup-training": "g38: the speed-up holds only when 2k < n, a condition outside this quote",
    "sauvage-gqml-graph-toolbox": "g40: a characterization the reader skimmed; no statement is quoted",
    "shao-2mc-obppp-estimator": "g40: the estimator's cost scaling is stated, not proved in the quotes",
    "shofar-theorem2-shot-bound": "g41: Theorem 2's bound is not quoted",
    "shmueli-gi-gapcvp-in-bqpoi": "g41: the theorem statements did not extract; only the class definition is quoted",
    "shmueli-exponential-speedup-claim": "g41: rests on hardness assumptions the quote does not name",
    "aqcp-asymptotic-coverage": "g43: a guarantee inherited from cited work; the adapted theorem's proof was not read",
    "qne-error-bounds": "g43: the bounds are not quoted; theorem statements and proofs not read in full",
    "qne-assumptions-and-exponential-worst-case": "g43: the worst-case copy complexity is a derived result; no bound is quoted",
    "qvsp-dimension-dependent-correction": "g43: the dimension dependence is not quoted",
    "cutting-plane-improved-bounds-idealised": "g43: the improved bounds are not quoted",
    "quantum-feature-maps-proved": "g43: a correctness proof the quote names but does not state",
    "rediscovers-simon": "g45: a reading of the method's output, not a stated theorem",
    "gradient-variance-lower-bound": "g45: Theorem 5.4.1's condition is quoted; its bound is described, not quoted",
    "vlasic-riemannian-framework": "g46: the derived formulas are not quoted",
    "vlasic-geodesic-simplification": "g46: a summary sentence of a result; its statement and conditions are not quoted",
    "vyas-flux-fluctuation": "g46: the relation itself is not quoted",
    "wang25-loss-barrier": "g46: Theorem 1 is quoted only in fragments",
    "wang25-concentration": "g46: the 'broad and typical data assumptions' are not stated in the quote",
    "learning-capacity-poly-photon": "g47: the proof is in a supplementary note the file does not contain",
    "wilkie-disjoint-constraint-gadgets-compose": "g48: Proposition IV.1 itself is not quoted, only the sentences around it",
    "wu-weakly-noisy-complexity-learning-algorithm-efficient": ("g48: Theorems 2 and 3 are named; their statements "
                                                                "and conditions are not quoted"),
    "qnn-spectral-amplitude-priority": "g49: only the claim 'we prove' is quoted; the derivation is not",
    "qcforest-retrain-runtime": "g49: the runtime is stated as a claim; its theorem and conditions are not quoted",
    "yue-bound-state-restores": "g50: 'we find' introduces the finding; the analysis behind it is not quoted",
    "zhang-heisenberg-theorem": "g50: Theorem 1's statement and conditions are not quoted, only sentences about it",
    "anyon-kernel-effective-dimension": "g51: the effective-dimension analysis is described, not quoted",
    "noise-purity-generalization-gap": "g51: derived from a surrogate model; the derivation is not quoted",
    "noise-finite-optimum-disappears": "g51: derived from a surrogate model; the derivation is not quoted",
    "qnn-decoder-standard-qec-bound": "g51: Theorems 1 and 2 are summarized; their statements and conditions are not quoted",
    "qnn-decoder-quadratic-improvement": "g51: only the claim 'We then prove' is quoted, not Theorem 3",
    "qbackprop-impossible-single-copy": "g52: 'we argue' introduces an argument in an appendix that is not quoted",
    "qbackprop-multicopy-quantum-resource-scaling": "g52: the abstract's claim is quoted; Theorem 9 and its conditions are not",
    "rfqrc-conditionally-stable": "g53: 'We analytically show' introduces the result; the quote breaks off before it",
    "scoop-minds-theorem": "g54: sentences about Theorem 1 are quoted; its statement and conditions are not",
    "arrasmith-cost-differences": "g54: the abstract's claim is quoted; Proposition 1 and its conditions are not",
    "improved-classical-qsvt-match": "g55: the abstract's claim is quoted; the main theorem and its conditions are not",
    "improved-classical-qsvt-applications": "g55: the abstract's claim is quoted; the corollaries are not",
    "hamiltonian-learning-poly-time": "g55: a fragment of the claim is quoted; the main theorem is not",
    "aiso-exponential-saving": "g55: the abstract's claim is quoted; Theorems 3 and 4 are not",
    "qwiener-universality-proof": "g56: the abstract's claim of a proof is quoted; the theorem is not",
    "bhattacharyya-submodular-theorem": "g57: a sentence about Theorem IV.1 is quoted; its statement is not",
    "boy-chain-contraction": "g57: the corollary itself is not quoted, only its name and one condition",
    "bravo-universality": "g57: the constructive argument is described; the reader did not check its derivation",
    "bravo-classical-equivalence": "g57: only the claim 'We prove' is quoted",
    "calzavara-lipschitz-bounds": "g58: the abstract's claims are quoted; the proofs are in appendices not quoted",
    "calzavara-polynomial-barren-plateaux": "g58: the bounds are described; Lemma 8 is not quoted",
    "dibom-universality": "g58: the reduction argument is described, not quoted",
    "dpqnn-privacy-guarantee": "g58: Theorem 1's name is quoted; its statement and conditions are not",
    "caro-mixture-superposition-learning": "g58: sentences about Theorem 1 are quoted; its statement is not",
    "caro-no-distribution-independent-advantage": "g58: a fragment of Theorem 3 is quoted; its conditions are not",
    "chatterjee-cnot-count": "g59: an analytic count of the circuits' CNOT gates; its derivation is not quoted",
    "chen2020-parameter-count": "g59: an analytic parameter count; its derivation is not quoted",
    "noise-aware-qaoa-compilation-complexity": "g60: an analytic complexity; its derivation is not quoted",
    "qil-q-bc-error-bound": "g61: Theorem 1's bound is described, not quoted; its proof was not read",
    "coelho-linear-executions": "g62: the complexity is claimed in the text; its derivation is not quoted",
    "coroi-bm-protocol": "g62: the abstract's statement is quoted; Theorem 1 and its conditions are not",
    "coroi-ef-lower-bound": "g62: the abstract's claim is quoted; Theorem 2 and its conditions are not",
    "coyle-density-qnn-mixing-lemma": "g63: proved 'under certain assumptions' that are not quoted",
    "date-aqsvm-time-complexity": "g63: an analytic complexity under fixed precision; its derivation is not quoted",
    "gbls-quadratic-query-complexity-claim": "g64: the claim is quoted; the query-complexity bound is not derived in the quote",
    "quantum-birch-theorem": "g64: Theorem 5.10 is described, not quoted",
    "quadratic-learning-efficiency-rl": "g65: the abstract's claim is quoted; Theorem 1 and its construction are not",
    "planar-routing-where-classical-not-possible": "g65: the examples are named; their analysis is not quoted",
    "georgiou-adversarial-generalization-bounds": "g67: the bounds are described in fragments; Theorems 2 and 3 are not quoted",
    "georgiou-train-with-strong-adversary": "g67: a reading of Theorem 5's bound; the theorem is not quoted",
    "random-encoders-barren-plateaus": "g68: the abstract's claim is quoted; Theorems 1 and 2 and the local case's assumptions are not",
    "qec-encoders-concatenation": "g68: the result is summarized; Theorems 3 and 4 and their conditions are not quoted",
    "fairness-reduction-noise-improves": "g68: the claims are quoted; Theorems 1 and 2 are not",
    # Fresh-eyes review of cec6020 (2026-10-25): half 1 HIGHs that did not meet the rule above, now LOW like
    # their siblings. A theorem is HIGH only when its statement and conditions are quoted.
    "graph-random-codes-tradeoff-extends-qgv": "g01, review: the abstract's claim; the trade-off and Theorems 4.1.6 and 4.5.10 are not quoted",
    "lstm-optimizer-time-per-pass-scaling": "g01, review: both theorem quotes stop before the run-time formula; the conditions are not quoted",
    "sbqe-equivalent-to-mlp": "g02, review: a derivation from the paper's equations, no theorem stated",
    "patel-qbm-convergence-proof": "g04, review: the abstract's claim; Theorem 1's conditions are not quoted",
    "roget-quadratic-improvement": "g05, review: the abstract's claim; Theorem 4's margin condition is not quoted",
    "distributed-qelm-linear-resource-reduction": "g19, review: a derivation from the paper's equations, no theorem stated",
    "ippdt-saturation": "g21, review: the abstract's claim; Theorem 4.2's conditions are quoted only in a fragment",
    "bnsl-seth": "g21, review: the bound whose base it refers to is not quoted (garbled in the text layer)",
    "qgp-matchgate-gp-proved": "g23, review: the abstract's claim; Theorem 1 is informal and its conditions are not quoted",
    "kqw-distinguish-cfi": "g25, review: 'we provide theoretical proofs' with no statement quoted; the proofs not checked",
    "k1qw-localized": "g25, review: 'we also prove' with no statement or conditions quoted",
    "tn-global-barren": "g29, review: the abstract's claim; Theorem 5 is not quoted",
    "tn-local-no-barren": "g29, review: the abstract's claim; Theorems 6 and 7 are not quoted",
    "tn-entropy-volume-law": "g29, review: the abstract's result (a); the theorem and its conditions are not quoted",
    "qfs-error-rectification": "g30, review: Theorem 1 is garbled in the text layer and its condition is not quoted",
    "pirnay-qnc0-nc0-pac-separation": "g37, review: two abstract fragments; Theorem III.1 is not quoted",
    "pauli-exp-permutation-similar": "g39, review: the abstract's claim; the proof was not checked by the reader",
    "simplex-rank-reduction": "g49, review: the quote is the paper's paraphrase of Theorem 1, which is garbled",
}
# A measured result whose words name a proof or a bound, or that a reader typed "theoretical", with why it is
# measured.
MEASURED_DESPITE: dict[str, str] = {
    # g01
    "mqt-pretraining-few-shot-lih": "the 'theoretical values' are the reference energies the error is measured against",
    # g03
    "classical-saturates-quantum-does-not": "'sample complexity' is the number of samples the training runs needed",
    "runtime-scaling-better-than-classical": ("the classical times are measured and the quantum ones estimated; "
                                              "'complexity classes' is the authors' aside"),
    "kernel-concentration-observed": "'We show' introduces a numerical demonstration on 100 generated points",
    "pipeline-mnist-vs-others": "g06: 'image complexity' is the authors' reason for the CIFAR-10 result",
    "bincoletto-transferable-parameter-prediction": "g12: 'we show' introduces a numerical evaluation on H2 to H12",
    "canonici-qubo-svm-performance": "g12: 'We show' introduces results from QPU runs and simulations",
    "sl-cost-exponential-interlayer-variance": ("g13: the exponential cost is a numerical finding on one circuit "
                                                "family; the paper gives no proof of it"),
    "mm-vqe-ising-speedup": "g14: the O(N 2) speedup is measured time saved in simulations up to 20 qubits",
    "derieux-convergence": "g15: 'we have shown' introduces training runs in simulation",
    "derieux-parameters": "g15: 'we have shown' introduces a count of the models' parameters",
    "annealer-faster-small": "g16: 'We show' introduces timed runs of a D-Wave hybrid solver against Gurobi",
    "ferreira-qrc-noise-effect": ("g17: the 'theoretical advantage' is a cited claim the noise simulations did not "
                                  "bear out"),
    "gacon-dualqte-fewer-measurements": "g17: 'asymptotically' describes a trend the author observes in numerical benchmarks",
    "ghosh-harmonic-main": "g18: 'we show' introduces benchmarks against physics-informed networks",
    "gonon-ibm-fez-envelope": "g20: the hardware errors are measured on ibm_fez; 'analytical' names the envelope they are compared to",
    "qsgd-accuracy": "g21: a measured validation accuracy in simulation; 'theoretical upper limit' is its reference",
    "qkbandit-u-shaped-regret": "g23: 'complexity' is the approximation's size, varied in experiments",
    "analogqk-noise-helps": "g23: simulated kernel performance; 'model complexity' is the authors' explanation",
    "margin-predicts-generalization": "g23: 'proved to be' means turned out to be, in QCNN experiments",
    "hamqaoa-numerics": "g25: 'we show' introduces numerical simulations",
    "underdet-score-works": "g25: 'We show' introduces numerical experiments on synthetic and real data",
    "tn-numerics-scope": "g29: numerical results at d = 2 and D = 2; 'Theorem 6' is what they are compared to",
    "qrc-ss-accuracy": "g30: simulated accuracies; 'asymptotic limit' names the infinite-shot case simulated",
    "qmc-ring-1-62-percent": "g32: 'we show' introduces a numerical evaluation of the authors' formulae at five layers",
    "qsm-complexity-threshold": "g32: 'circuit complexity' is the circuit size varied in training runs",
    "regqpg-robustness": "g33: 'We show' introduces training runs on CartPole",
    "qmlhcs-bounded-loss-under-drift": "g34: 'bounded' describes a loss curve in one simulated run",
    "r-qupid-adversarial-robustness": "g35: 'bounds' are the attack bounds of FGSM and PGD in simulated tests",
    "quyen-lll-stability": "g37: measured optimization stability; 'linear computational complexity' describes the loss",
    "complexity-signature-auc": "g38: a fitted classifier's AUC; 'data complexity measures' are its inputs",
    "correlation-with-gap": "g38: correlations over 1400 training runs; 'complexity term' is the bound's term",
    "qrf-shot-count-scaling": "g39: a numerical finding; 'theoretical' names the accuracy it is compared to",
    "quso-qaoa-outperforms-high-load": "g43: 'We show' introduces simulated runs up to 14 qubits",
    "reservoir-size-non-monotonic": "g43: 'We show' introduces simulated reservoir benchmarks",
    "qnn-adversarial-robustness": "g44: 'proved to be' means turned out to be, in attack experiments",
    "qnn-quantum-noise-robustness": "g44: 'proves its strength' describes simulated noise experiments",
    "top3-accuracy-85-7": "g45: a measured Top-3 accuracy; 'complexity metrics' are the classifier's features",
    "wu-weakly-noisy-numerics-lower-bound-not-growing-with-depth": ("g48: a numerical estimate in simulation; "
                                                                    "'complexity lower bound' is the quantity estimated"),
    "yue-fidelity-saturation": "g50: a computed fidelity; 'bound' names the bound state, not a bound",
    "lean-qbench-top-scores": "g51: measured benchmark scores; 'theorem' names the Lean tasks the agents attempted",
    "qrc-learn-invariants": "g53: 'We show' introduces tests on the Lorenz-63 and Lorenz-96 systems",
    "bermejo-one-qubit-accuracy": "g57: 'we show' introduces simulated clustering results",
    "bucher-tsp-xy-qaoa": "g58: measured time-to-solution; 'circuit complexity' describes the circuit's size",
    "carles-proof-of-concept-qrc": "g58: 'we show' introduces an experiment on a transmon device",
    "chen2018-shallow-circuits-discriminate": "g59: numerical simulations; 'theoretically optimal' names the reference POVMs",
    "chen2018-error-inconclusive-tradeoff": "g59: training results; 'theoretical minimum' is the reference they miss",
    "pqkd-cifar-teacher-stronger": "g61: measured accuracies; 'task complexity' is the authors' explanation",
    "collis-learning-and-accuracy": "g62: 'proved' means turned out to be, in simulated training",
    "correr-pqc-faster-complexity": "g62: 'complexity' is the circuit complexity measured in numerical runs",
    "date-aqsvm-accuracy-on-par": "g63: 'We show' introduces training runs on five benchmark datasets",
    "date-aqsvm-speedup-8m-features": "g63: measured training times; O(N 3) is the classical algorithm's cost",
    "parser-toolchain-ports-problem-across-simulators": "g64: 'proved' means turned out to be, in a verification run",
    "random-quantum-networks-outperform-claim": ("g64: 'show numerically' introduces the outperformance; the "
                                                 "complexity analysis is named, not used in the value's claim"),
    "static-vqa-fail-4-node-shortest-path": "g64: measured failures; 'complexity' is the authors' explanation",
    "qnn-learns-digit-distinction-simulated": "g65: 'We show' introduces a classical simulation of training",
    "qps-beyond-classical": "g66: 'we show' introduces a worked example from transfer learning",
    "galvao-noise-hinders-accuracy": "g67: 'We have shown' refers to noisy simulations in Qiskit",
    "georgiou-synthetic-numerics-loose-bound": "g67: numerical experiments in a synthetic setting; 'bound' is the theory they test",
    "kdm-classification-on-par": "g68: measured accuracies; 'comparable complexity' describes the deep model compared",
    "halder-rbm-ansatz-accuracy": "g69: a computed energy accuracy; 'bound' names an error figure the reader did not quote",
    "hassanshahi-qsvm-parity": "g69: measured ROC AUC scores; 'derived' means computed from the runs",
}


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


ONLY: list[str] = []  # --groups, dry run only: the coordinator's check of the groups reviewed so far


def groups_of(half: str) -> list[str]:
    lo, hi = HALVES[half]
    return [g for n in range(lo, hi + 1) if (g := f"g{n:02d}") in ledger()["groups"] and (not ONLY or g in ONLY)]


def no_copy(half: str) -> dict[str, str]:
    """The ledger's no-copy records, entered with the first half."""
    return dict(ledger()["no_copy"]) if half == "1" else {}


def load_groups(half: str) -> list[tuple[str, dict]]:
    """Every paper of the half's groups; refuses a reader file whose records are not its group's."""
    out, L = [], ledger()
    for g in groups_of(half):
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
        return low_grade("vendor claim")
    if aid in THEORY_LOW:
        return grade(aid, HIGH, otherwise=low_grade("theoretical result", THEORY_LOW[aid]))
    basis = "field statement" if aid in FIELD_STATEMENTS else {"cited": "cited claim", "shown": "measured result"}.get(
        a["kind"], "authors' claim")
    return grade(aid, HIGH, otherwise=low_grade(basis))


def anchor_safe(anchor: str) -> str:
    # A quote mark inside a label would break the quote pattern (Sprint 11 Task D finding).
    return anchor.replace('"', "'")


def assertions(half: str) -> list[tuple[str, AssertionRecord, str, dict]]:
    out = []
    for g, p in load_groups(half):
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
                updated=TODAY, updated_reason=(f"{TODAY} ({TAG}): extracted from {rid}; first-pass read by a "
                                               "subagent, every quoted passage read in context by the coordinator")),
                rid, p))
    return out


def verify(half: str) -> list[tuple[AssertionRecord, str, dict, object]]:
    """Every quote verbatim in its source, every coordinator edit resting on
    named passages, and every figure in a value in its own quotes, BEFORE
    anything is written (section 31)."""
    texts: dict[str, str] = {}
    out = []
    for _, a, rid, p in assertions(half):
        quotes = QUOTE.findall(a.citation_context)
        text = texts.setdefault(p["file"], plain(source_text(p["file"])))
        verified = require_verbatim(a.id, a.citation_context, text, value=a.value)
        if a.id in VALUE_REPLACE:  # the replaced value's passages are the quotes printed with it
            require_edit_basis(a.id, a.value, quotes, text)
        if a.id in QUOTE_EDITS:
            require_edit_basis(a.id, None, [n for _, n in QUOTE_EDITS[a.id] if n] or quotes, text)
        out.append((a, rid, p, verified))
    return out


_WHOLE = re.compile(r"^(read the )?(whole|full) (paper|text)|^main text read in full|^abstract through (the )?conclusion",
                    re.I)


def read_detail(g: str, p: dict) -> str:
    # Readers marked "full" for reads they then listed as a few sections (abstract, introduction, results,
    # conclusion), so the list, where there is one, is what the record says was read. A note that says the
    # whole paper was read is not a list (fresh-eyes review of cec6020: 7 of the 113).
    if p.get("read_extent") == "partial":
        detail = f"first pass, in part: {p['partial_detail']}"
    elif p.get("partial_detail") and _WHOLE.search(p["partial_detail"].strip()):
        detail = f"first pass, the whole source ({p['partial_detail'].strip().rstrip('.')})"
    elif p.get("partial_detail"):
        detail = f"first pass, the parts the reader lists: {p['partial_detail']}"
    else:
        detail = "first pass, the whole source"
    detail += f" (Sonnet 5.5 reader, group {g.upper()})"
    if p.get("version_note"):
        detail += f"; version: {p['version_note']}"
    return detail


def apply_changes(conn, half: str) -> list[str]:
    checked = verify(half)
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    for rid, why in sorted(no_copy(half).items()):
        reason = (f"{TODAY} ({TAG}): NOT read and NOT for the hand-download list: {why}" if "withdrawn" in why
                  else f"{TODAY} ({TAG}): selected for reading and NOT read: {why}; on the hand-download list")
        stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
        if reason not in stored:
            append_updated_reason(conn, rid, reason, TODAY)
            log.append(f"no copy {rid}")
    for g, p in load_groups(half):
        rid, detail = p["record_id"], read_detail(g, p)
        have = {(r[0], r[1], r[2]): r[3] for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,))}
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        path = p["file"].replace("/", "\\")
        if path.lower() not in {s.lower() for s in recheck.local_paths(access or "")}:
            note = f"Local copy {f80._sha(Path(path))}, recorded {TODAY} ({TAG})"
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ? WHERE record_id = ?",
                         (f"{access} | {path}" if access else path,
                          f"{evidence.rstrip().rstrip('.')}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): local copy added to access", TODAY)
            log.append(f"access {rid}")
        kept = [a for a in p["assertions"] if a["id_suggestion"] not in DROP]
        if not kept:  # read, and nothing in it bears on a context: the reason, not a tier change
            if (SUBAGENT_READER, TODAY, "subagent") not in have:
                add_read(conn, rid, SUBAGENT_READER, TODAY, "subagent", detail)
                why = p.get("why_not") or "; ".join(DROP[a["id_suggestion"]] for a in p["assertions"])
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read at first pass and NOT entered: {why}", TODAY)
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
        changed = sync_verified_assertion(conn, a, verified, f"{TODAY} ({TAG}): corrected to the script's "
                                          "current text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    half = args[args.index("--half") + 1]
    if "--groups" in args:
        if "--apply" in args:
            print("--groups is for a dry run; an apply enters a whole half")
            return 1
        ONLY[:] = args[args.index("--groups") + 1].split(",")
    kept = assertions(half)
    ids = [a.id for _, a, _, _ in kept]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    owner = {a.id: rid for _, a, rid, _ in kept}
    with connect(DB_PATH) as conn:
        clash = [i for i in ids if conn.execute(
            "SELECT 1 FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ? AND "
            "r.provenance NOT LIKE ?", (i, f"%{owner[i]}%")).fetchone()]
    if dupes or clash:
        print(f"duplicate assertion ids: {dupes}; ids already held by another source: {clash}")
        return 1
    if "--apply" not in args:
        checked = verify(half)
        for a, _, _, _ in checked:
            validate_assertion(a)
        papers = load_groups(half)
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"{len(kept)} assertions from {len(papers)} records "
              f"({sum(1 for _, p in papers if not [a for a in p['assertions'] if a['id_suggestion'] not in DROP])} "
              f"with none); {len(no_copy(half))} with no copy. Every quote verbatim, every edit on named passages, "
              "every figure in its quotes. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, f"{TAG} reads entered, half {half}")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, half)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
