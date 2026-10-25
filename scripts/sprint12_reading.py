#!/usr/bin/env python3
"""Sprint 12 Tasks F and G (F104, F105): the first-pass reads entered, one ledger.

`manifests/sprint12_read_ledger.json` gives every record this sprint reads
to exactly one group and each group to one task (F: g01 to g03, the papers
Roadmap-to-QML added; G: g04 to g53, the 400-record slice). One Sonnet 5.5
reader per group wrote `manifests/sprint12_reads/group_<g>.json` (kept
verbatim) under `READER_PROMPT.md`. A reader file whose records are not
exactly its group's is refused, so no two reads touch one record. Task E's
pages are the coordinator's (section 44) and are not entered here.

HOW THE SOURCES WERE READ (ADR-0005 A4: a subagent's read alone never
qualifies `read`): as Sprint 11 (`sprint11_reading.py`). The coordinator
checked every quote against the source text by script
(`require_verbatim`, with the value's figures) and read every value against
its quoted passages in context. QUOTE_EDITS, EXTRA_QUOTES, VALUE_REPLACE,
CONTEXT_FIX, DROP and HIGH record that read.

CERTAINTY (INTAKE_WORKFLOW.md section 45, the grading rule): HIGH only
through `store.grading`, each HIGH id with its basis (setup, scope,
definition, proved result, stated limit) and where the paper settles it.
Everything else as the store's GRADE mapping: an empirical result from one
study, an author's claim and a cited claim start LOW; a vendor's
description of its own product starts MODERATE and a vendor's result LOW.
The reader's own suggestion is never used.

    python scripts/sprint12_reading.py --task G            # dry run: every quote checked; nothing written
    python scripts/sprint12_reading.py --task G --apply    # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import grade, high_grades  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_verified_assertion,  # noqa: E402
                          set_tier, sync_verified_assertion, validate_assertion)
from store.quotes import QUOTE, plain, require_edit_basis, require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
TAGS = {"F": "Sprint 12 Task F, F104", "G": "Sprint 12 Task G, F105"}
LEDGER = ROOT / "manifests" / "sprint12_read_ledger.json"
READS_DIR = ROOT / "manifests" / "sprint12_reads"
F104 = ROOT / "manifests" / "sprint12_f104_roadmap.json"
SUBAGENT_READER = f80.SUBAGENT_READER

COORDINATOR_DETAIL = ("every quoted passage with about 220 characters each side, every quote checked verbatim and "
                      "every figure in a value checked against its quotes by script; the rest of the paper not "
                      "read by the coordinator" + f80.f78.ABSENCE_NOTE)

# Exact source characters a reader's quote missed, looked up in the source text: (old, new or None to drop).
QUOTE_EDITS: dict[str, list[tuple[str, str | None]]] = {
    # g01: quotes for the parts of the value the coordinator cut (see VALUE_REPLACE)
    "qinn-simulated-nisq-scope": [("noisy intermediate-scale quantum computers (NISQ) cannot support", None)],
    "photonic-qrc-zero-bias-power-scope": [("The zero-bias state achieved an MSE", None)],
    # review of 5744e2d: the second quote is a cited result ([39]), not the paper's own limit.
    "qaoa-qa-limitation-smooth-angles": [("If this restriction is relaxed", None)],
}
EXTRA_QUOTES: dict[str, list[str]] = {
    # g15: the parts of the value the reader's quotes lost at a dash or a curly quote in the source.
    "bowles-open-classical-encoding": [
        "(for potentially larger label dimension) can be usefully encoded in classical models using a tractable "
        "amount of resources"],
    "bowles-toy-problem-outperform": ["based on learning the payoff behaviour of a zero-sum game"],
    "callison-exceptional-amplitudes-fail": ["In the process, we observe and explain particular ranges of",
                                             "values of the target amplitude"],
    "akpinar-setup-nine-maps-pca5": [
        "Considering the limitations of the NISQ computers in both datasets, the PCA value was set to 5."],
    # g19: the passages the value rests on that the reader's quotes stopped short of.
    "sequent-dqc-identity-vqc": ["resembles the identity function",
                                 "of degree 1 arbitrarily well, even if the VQC is not affecting the prediction at all"],
    "sequent-scope-limits": ["we only considered the simple architecture with fixed angle embeddings"],
    "bensberg-derivatives-unavailable": [
        "analytical expressions for energy derivatives of highly accurate electronic structure methods"],
    # g21: which assumption "this assumption" is.
    "qchannel-markovian-limit": ["Before we proceed, we comment on our underlying assumption of Markovianity"],
    # g23: the subjects of the reader's quotes.
    "pqc-approx-assumes-arbitrary-unitaries": ["Secondly, we assume that the trainable circuit blocks"],
    "stock-data-binary-three-day": ["For this experiment, we use historical stock data from Apple"],
    # g22: what "not addressed" refers to.
    "qml-survey-excludes-qrl": ["In addition to the paradigms mentioned, reinforcement learning (RL) represents the "
                                "third paradigm.",
                                "for a comprehensive overview of the literature on quantum reinforcement learning"],
    # g25: what "the latter", "This" and the simulator are.
    "qsann-near-term-scope": [
        "Another model consists of several quantum variational circuits which use a Gaussian projected "
        "self-attention method", "and then post-processing using classical calculations."],
    "post-selection-limit": ["By particle conservation and starting with a single particle",
                             "Such measurements are ignored in postprocessing.",
                             "This is a powerful error mitigation option"],
    "vqe-benchmark-molecules-setup": ["MindQuantum[21] was used as the quantum simulator"],
    # g33: the subject of the reader's quote.
    "ppn-demo-speed-limited": ["In our demonstration of photonic probabilistic machine learning, the speed and "
                               "energy efficiency were limited by the"],
    # g37: which network.
    "qwalk-limited-validation": [
        "Although the proposed quantum walk algorithm was only tested on Zachary",
        "karate club network as a test case; however, it needs to be validated through various examples and "
        "mathematical proof"],
    # review of 5744e2d: the passages each corrected value rests on.
    "yang-simulator-limit": [
        "Due to the large amount of test data with interference between the SM and NP, which would consume too "
        "much machine time,",
        "so we choose the better-fitting SCA instead of pairwise in this subsection"],
    "aqnn-coherence-entanglement-no-help": [
        "a non-coherence-generating operation M is able to realize a coherent channel in this way only if it can "
        "activate coherence",
        "Noting that GIOs violate this condition [13], the following no-go result holds"],
    "gilfuster-trainability-definition": [
        "with high probability with respect to a training set S of polynomial size being sampled i.i.d. according "
        "to D"],
    "hamlearn-computational-basis": [
        "but where state preparation and measurement are restricted to the computational basis",
        "For nearest-neighbor Hamiltonians with only Pauli"],
    "huggins-selective-teleportation-restricted": [
        "Our scheme is likely generalizable to all diagonal unitaries that are members of the Clifford hierarchy"],
    "fisher-bures-wy-factor-two": ["for an algorithm like natural gradient descent"],
    "analog-vec-accuracy": ["on linearly inseparable datasets such as concentric circles and MNIST digits"],
    "akpinar-glioma-low-performance": ["gives better results in terms of total processing time"],
    "dqf-beats-nystrom-rqf-not": ["classification tasks using a dataset with"],
    # g47: the rest of the proof sentence, after the apostrophe that stopped the reader's quote.
    "watts-unconditional-sampling-separation": [
        "be reproduced by constantdepth bounded fan-in classical circuits, even up to additive error"],
    # g49: the abstract's target ratio, on the far side of the quoted word "shots".
    "chernyavskiy-constant-shots": [
        "show that with these modifications the median number of quantum circuit runs",
        "required to achieve AR=0.95 counterintuitively decreases towards a nearly constant value"],
}
VALUE_REPLACE: dict[str, str] = {  # the coordinator's read; each replacement says only what its quotes say
    # g05: the setup without the accuracy, which is its own (empirical) assertion.
    "bosonic-classifier-setup": (
        "The authors report that 200 training data were used to train the optical quantum circuit and "
        "classification was performed on 1500 test data, that the number of classes is 2, and that the circuit has "
        "a total of about 220 optical components on a silicon optical waveguide."),
    # g04: the cost scalings and "fermion gases and lattice spin models" are not in the quotes.
    "giuliani-sample-limit": (
        "The authors state that their kernel ridge regression approach is ultimately limited by the number of "
        "samples."),
    "verdel-scope-assumption-free": (
        "The authors state that their approach is immediately extended to other classes of quantum simulators."),
    # g06: what the quotes hold, no more (the tuple's parts, the self-adaptive weights); and both of the
    # paper's own statements where they differ ("all ten" against "most cases").
    "ikeda-definition-qefg": "The paper defines a quantum extensive-form game by a tuple (Definition II.1).",
    "setty-setup-problems": (
        "The authors state that they adapt and generalize the framework to a quantum machine learning setting for a "
        "variety of problems, including the 2D Poisson's equation, a second-order linear differential equation, a "
        "system of differential equations, and the nonlinear Duffing and Riccati equations."),
    "oh-qsvdd-outperforms": (
        "The authors state that for all ten anomaly detection tasks QSVDD outperformed both the QAE-based method and "
        "the classical DSVDD under similar training conditions; elsewhere they state that QSVDD outperformed DSVDD "
        "in most cases, despite using fewer model parameters."),
    # g10: what the quotes hold (the cross-entropy test, the "other work", the lattice, the noise future work
    # are not in them).
    "iqp-sampling-hardness-checked-small": (
        "The authors state that they study anti-concentration this way for systems with up to 20 qubits, and for "
        "larger numbers of qubits use the fact that the probability distributions converge to the Porter-Thomas "
        "distribution."),
    "iqp-target-distribution-known": (
        "The authors state that a training issue does not arise in their case because they assume knowledge of the "
        "target probability distribution."),
    "nqs-ite-stability": (
        "The authors report evidence that their method offers higher stability and final energy accuracy than the "
        "optimization of neural quantum states with energy as a loss function."),
    "tc-avqite-small-molecules": (
        "The authors state that TC-AVQITE is used to calculate ground state energies across the potential energy "
        "surfaces of H4, LiH and H2O, and that the study focuses on small molecular systems."),
    # g07: what the quotes hold (the error-correcting code, the remedies tried, the device name are not in them).
    "aaronson-yamakawa-zhandry": (
        "The author states that there is a polynomial-time quantum algorithm for the problem he describes (Yamakawa "
        "and Zhandry's), and that if f is a truly random function, any classical algorithm would need exponentially "
        "many queries to f to solve it."),
    "asaoka-eight-class-drop": (
        "The authors report that in the eight-class task the test accuracy decreases significantly, and that the "
        "accuracy did not reach the level achieved in the four-class classification task."),
    "chan-lih-ibm-perth": (
        "The authors report that in their quantum chemistry run (Fig. 2(e)) the VQE converges within 1.1% of the "
        "ground-state energy after 99 function evaluations, with the fidelity F improving from 0.067 to 0.78."),
    # g10: the theorem's number is in the anchor, not the quotes.
    "determinant-sampling-theorem": (
        "The paper states that there is a quantum determinant sampling algorithm that requires O(nd2) "
        "pre-processing to orthogonalize A, and generates subsequent samples using a quantum circuit with "
        "O(nd log n) gates and with total depth O(d log n) (the source prints the exponent as nd2)."),
    # g11: the conditions the value added (feature and class counts, MNIST, a convolutional front end) are not in
    # the quotes.
    "roca-jerat-favorable-small-qudits": (
        "The authors report favorable comparisons against the best classical models, and state that the trend holds "
        "even for small quantum systems, with dimensions d < 5 and algorithms with a few layers (L = 1, 2)."),
    "roca-jerat-mnist-bottleneck": (
        "The authors observe that small quantum systems often act as bottlenecks, resulting in lower accuracy "
        "compared to their classical counterparts."),
    # g14: the stated limit without the result the same sentence carries (that result is its own assertion).
    "mironowicz-challenges-remain": (
        "The authors state that challenges such as scalability, hardware limitations and algorithmic complexity "
        "remain for QML algorithms."),
    "wang-hamemb-no-speedup": (
        "The authors state that their model does not provide speedups for either training or inference when "
        "compared to classical techniques."),
    # g13: each stated limit without the result its sentence or its second quote carries; the split without
    # the lost exponent read as a number.
    "random-forest-split-setup": (
        "The authors state that the samples were randomly split into training and testing data (printed 9 × 104 "
        "and 104 in the text layer, which loses the exponent), with 50 different train-test cycles, and that random "
        "forest was used throughout."),
    "noiseless-simulators-preliminary": (
        "The authors state that, for the variational approach, they used noiseless simulators."),
    "shqmm-overfit-and-classical-data": (
        "The authors state that the current results are likely to be overfitted given the complexity of the "
        "relationship between a complex model and simple data with lower number and dimensionality of hidden "
        "states."),
    "conventional-baseline-extrapolated": (
        "The authors state that the improved process reconstruction they achieved using entanglement does not "
        "demonstrate a provable quantum advantage."),
    "noisy-lossy-platform": (
        "The authors state that the photonic platform is noisy and lossy, with system losses of approximately 20%."),
    # g16: the limit without the result beside it; the open question the quote does not hold, cut.
    # review of 5744e2d: "restricted" refers to the generalization, not the family the scheme reduces.
    "huggins-selective-teleportation-restricted": (
        "The authors state that their scheme is likely generalizable to all diagonal unitaries that are members of "
        "the Clifford hierarchy, but that this is still a relatively restricted class of unitaries."),
    "jerbi-no-classical-lower-bound": (
        "The authors state that, to strengthen their results, one would ideally prove matching lower bounds for the "
        "classical complexity of this task."),
    # g17: the simulator's name is not in the quotes; the limit without the result beside it.
    "hqcnn-dataset-and-circuit-setup": (
        "The authors state that the dataset comprises 3 064 T1-weighted contrast-enhanced images extracted from 233 "
        "patients, and that a quantum device with four qubits is initialized using PennyLane."),
    "hl-qft-experimental-challenges": (
        "The authors state that their results indicate the experimental challenges with respect to the required "
        "system size, measurement resolution and sample size."),
    # g18: what the quotes hold (the encoder and decoder placement, the two methods named, are not in them); the
    # setup without its priority claim; the scope without the open question about the field.
    "tabi-setup-simulated-single-use": (
        "The authors state that they study the performance of simulated architectures for standard encoded radio "
        "signals over a noisy channel, and that they focus on the case of single channel use (n = 1)."),
    "tomesh-scope-constraint-aware-ansatz": (
        "The authors state that they focus solely on the case which uses the constraint-aware ansatz and therefore "
        "requires the use of multi-controlled gates."),
    "venkatesh-measurements-exponential": (
        "The authors state that the number of circuit measurements scales exponentially with the number of qubits."),
    "wang-setup-hehplus": (
        "The authors state that they utilized a fully programmable photonic chip to experimentally estimate the QNG, "
        "and that they compare vanilla-gradient-based VQE and QNG-based VQE in finding the ground state of the "
        "He-H+ cation."),
    # g19: the degree the reader could not quote, now quoted (EXTRA_QUOTES).
    "sequent-dqc-identity-vqc": (
        "The authors argue that if the variational quantum circuit resembles the identity function, the dressed "
        "quantum circuit can approximate any polynomial function of degree 1 arbitrarily well, even if the VQC is "
        "not affecting the prediction at all."),
    # g21: the scope without the recommendation beside it.
    "tsp-encoding-results-limited-to-6-nodes": (
        "The authors state that their results were obtained for instances up to 6 nodes, and that it remains an open "
        "question whether the performance of the permutation encoding is due to the small problem size."),
    # g20: the study's own limit, without the general runtime claim beside it.
    "nadim-limit-qsvc-scalability": (
        "The authors state that they encountered significant challenges in training QSVC with datasets containing "
        "more than 500 instances, primarily due to its sluggish runtime."),
    # g22: the caveat without the measured observation beside it.
    "maqrl-barren-plateau-caveat": (
        "The authors state that it cannot be ruled out that barren plateaus may occur in gradient-free methods under "
        "different conditions or in more complex scenarios."),
    # g24: each setup without the capability claimed for it.
    "an-dual-model-setup": (
        "The authors state that they have developed a machine learning framework that utilizes LSTM to predict "
        "quantum dynamics and infer Hamiltonian parameters."),
    "baek-proposal": (
        "The authors state that they propose a new version of QCNN, named scalable quantum convolutional neural "
        "network (sQCNN), and a novel training algorithm (RF-Train)."),
    # g26: the future work the quote does not hold, cut.
    "single-qubit-scope": (
        "The authors state that, for the sake of clarity and simplicity, they restricted themselves to the case of a "
        "single qubit."),
    # g25: the theorem's number is in the anchor; the limit without the claim beside it; the setup as quoted.
    "zxw-four-shift-nogo": (
        "The thesis proves that it is not possible to compute the gradient of gates with generator eigenvalues −λ, "
        "0, λ using less than four shifts."),
    "zxw-bp-tool-cannot-prove": (
        "The author states that the numerical tool cannot formally prove or disprove the existence of barren "
        "plateaus."),
    "vqe-benzene-experiment-setup": (
        "The authors state that the quantum machine is used exclusively for single-point energy evaluations, and "
        "that the quantum circuits act on 8 qubits."),
    # g27: each limit without the measured result beside it, or the part its quotes do not hold.
    "block-encoding-success-decay": (
        "The authors state that, with every application of the ancilla method, the overall probability of success "
        "will decrease exponentially, which is a typical feature of block-encoding methods."),
    "qae-simulator-and-limits": (
        "The authors state that training and evaluation were performed on a statevector simulator, and that future "
        "work includes deploying the architecture on real quantum hardware."),
    "eevqe-limits": (
        "The authors state that the verification of EEVQE on actual NISQ devices should be addressed in future "
        "studies."),
    # g28: what the quotes hold (the basis states, the scaling with samples, the hardware plans are not in them).
    "mvqn-radix-three-cost": "The paper states that, under its hardware cost model, the minimum cost happens when r = 3.",
    "afqmc-cost-prefactor": (
        "The authors state that their algorithm essentially gives a prefactor to the cost of a standard AFQMC with a "
        "single determinant trial wave function, and that their implementation has not really focused on speedups."),
    "mvqn-no-hardware-yet": "The author states that the next step is to realize multi-valued quantum neurons experimentally.",
    "dmet-vqe-future-noise": (
        "The authors state that future research will focus on integrating error mitigation and noise-resilient "
        "algorithms to further enhance scalability and reliability."),
    # g30: what the quotes hold (the map's name, the error-free case, the superselection reason are not in them);
    # each scope without the result or comparison beside it.
    "aqnn-scope-maximal-storage": (
        "The authors state that throughout the work they only consider aQNNs with maximal storage capacity, that "
        "is, those whose evolution is given by Eq.(1)."),
    # review of 5744e2d: the no-go rests on the paper's model, whose operations are GIOs (its faulty-aQNN section
    # says other errors may not keep it); the condition restored from the sentence before the proposition.
    "aqnn-coherence-entanglement-no-help": (
        "The paper states, noting that GIOs violate the condition that a non-coherence-generating operation can "
        "activate coherence, that coherence cannot be used to enhance the performance of aQNNs, and that initial "
        "entanglement cannot be used to reduce the depth of aQNNs."),
    "fermionic-hubbard-class-scope": (
        "The authors state that they provide an algorithm to learn a class of fermionic Hubbard Hamiltonians at the "
        "Heisenberg limit, allowing complex hopping amplitudes and nonzero chemical potentials in addition to the "
        "on-site interactions."),
    "fermionic-hubbard-ancilla-overhead": (
        "The authors state that their protocol utilizes O(N ) ancillary fermionic modes, where N is the system size, "
        "and that a natural next step would be an algorithm that eliminates the ancilla overhead altogether."),
    "noisy-ae-scope-and-condition": (
        "The authors state that they study the noisy amplitude estimation problem where the noise source is assumed "
        "to be depolarization, but its intensity is unknown."),
    # g32: the theorem's number is not in the quote; each limit as its quote gives it.
    "survey-qst-optimal-bound": (
        "The survey states that two works, by Haah et al. and by O'Donnell and Wright, obtained optimal bounds for "
        "the sample complexity of quantum state tomography."),
    "sqp-scope-limited-not-ruled-out": (
        "The authors state that their work does not conclusively rule out the possibility of use-cases for SQPs."),
    "mle-hl-local-hamiltonian-limit": "The authors state that the protocol's advantages are most apparent for local Hamiltonians.",
    "hqnn-qcnn-scalability-limit": (
        "The authors state that, given the limitations of current NISQ devices, the QCNN can only handle a small "
        "number of qubits, limiting its scalability."),
    # g31: the system's version number and the cited year are not in the quotes.
    "vrp-annealer-size-limit": (
        "The authors state that the largest annealer available to them has a limit of around 145 fully connected "
        "variables, and that the additional complexity of the embedding problem decreases the viability of applying "
        "the quantum algorithms for the last mile delivery problem at scale."),
    "qgl-nonconvex-cost-landscape": (
        "The authors state, citing other work, that the cost landscapes of training quantum algorithms are generally "
        "non-convex, making it difficult to establish general guarantees about the computational expense of the "
        "optimizations."),
    # g35: what the quotes hold (the Hessian's eigenvalues, the convergence condition, the future work are not in
    # them).
    "gustafson-hessian-dependence-limit": (
        "The authors state that the efficacy of the line search optimization is contingent upon accurate conjugate "
        "search directions being obtained from the Hessian in the low-level theory."),
    "larson-convergence-proved": (
        "The authors state that, building on previous results, they proved that with high probability their method "
        "exhibits a worst-case convergence rate (the rate and its condition are lost in the text layer)."),
    "larson-noise-estimate-limit": (
        "The authors state that it is not entirely technically correct, though reasonable, to continue using the "
        "standard error of cost function estimates as the estimate."),
    # g33: the theorem's number is in the anchor, not the quote.
    "che-theorem2-geometric-locality-scope": (
        "The paper states its lower bound for the circuit complexity of a geometrically local quantum circuit, with "
        "respect to the n-qubit chain."),
    # g36: the classical methods are not named in the quotes.
    "xqml-iris-setup": (
        "The authors state that they utilize the Iris dataset to compare classical ML algorithms with the "
        "Variational Quantum Classifier (VQC) and the Quantum Support Vector Classifier (QSVC)."),
    # g37: the network named; the limit as the quotes give it.
    "qwalk-limited-validation": (
        "The author states that the algorithm was only tested on Zachary's karate club network, and that it needs to "
        "be validated through various examples and mathematical proof."),
    "muse-simulation-only": (
        "The authors state that they plan to use IBM quantum devices to run MUSE on real hardware, and that due to "
        "lack of funding they could not perform such runs."),
    # g39: the quote stops before "gradient flow".
    "qnn-convergence-setup": "The authors state that they focus on QNNs equipped with the mean square loss.",
    # g38: each limit as its quotes give it (the measured non-convergence, the dataset, the 3-means are not in
    # them).
    "tn-search-limits": (
        "The authors state that expanding the bond dimension and applying the method to larger systems are "
        "essential steps to enhance its applicability."),
    "sqnn-simulator-17-qubit-limit": (
        "The authors state that the work is exploratory and carried out on a quantum system simulator using the "
        "TensorFlow Quantum library, and that a VQC made up of basic quantum blocks can only contain at most 17 "
        "qubits."),
    "coreset-limits": (
        "The authors state that errors in computation were not a concern for their simulations but become one on "
        "quantum hardware, and that the two-label representation forces a coreset of half the size they could have "
        "used."),
    # g40: the setup as its quote gives it (the next step is not quoted).
    "pqk-noiseless-simulator": (
        "The authors state that their current analysis employs a noiseless simulator, which is adequate for "
        "initial tests on shallow circuits and shot noise."),
    # g42: the setup as its quote gives it ("randomly initialised" is not in it). Review of 5744e2d: the
    # definition whole, its probability condition quoted (EXTRA_QUOTES), not cut; the proposition's assumption kept.
    "gilfuster-trainability-definition": (
        "The paper defines a learning model as trainable if, for each task, the empirical risk of the hypothesis "
        "produced by the learning algorithm is close to the optimal one within the class, with high probability "
        "with respect to a training set of polynomial size sampled i.i.d. according to D."),
    "gilfuster-bp-trainable": (
        "The paper proves that QML models exist that have barren plateaus under the uniform distribution of "
        "parameters and are trainable for learning tasks that are classically intractable under standard "
        "cryptographic assumptions."),
    "hoffmann-random-data-setup": (
        "The authors state that one test task is a binary classification task on 100 generated datapoints."),
    # g46: the scope and setups as their quotes give them (the other encodings, "real industrial" and PDBbind
    # are not in them).
    "rff-hamiltonian-encoding-scope": (
        "The authors state that the study focuses on Hamiltonian encoding, a key ingredient to express QML models "
        "as finite Fourier series."),
    "pathmatters-problem-setup": (
        "The authors state that the benchmark problem is the optimization of work allocation in a press shop "
        "producing vehicle parts."),
    "qdmd-test-set": (
        "The authors state that 363 pairs of protein-ligand complexes from the dataset after 2019 were randomly "
        "selected as a test set."),
    # g44: each as its quotes give it ("more general settings" and the estimating algorithms are not in them).
    "qgnn-no-empirical-eval": (
        "The authors list further analysis and empirical evaluations to assess the performance and scalability of "
        "their Quantum GNN architectures as future research directions."),
    "eqbm-info-matrices": (
        "The authors state that they establish analytical expressions for the Fisher–Bures, Wigner–Yanase, and "
        "Kubo–Mori information matrix elements of evolved quantum Boltzmann machines."),
    # g48: each limit without the result mixed into it; the conditions as the quote gives them.
    "qaoa-no-general-guarantee": (
        "The authors state that their numerics on random instances do not provide general performance "
        "guarantees."),
    "varemb-noise-not-studied": (
        "The authors state that, from the quantum computation perspective, the effect of hardware noise on the "
        "results should be investigated."),
    "qgrid-utility-needs-more-study": (
        "The authors state that further investigation is needed to explore any evidence of potential quantum "
        "utility in the energy sector."),
    "qaoa-qa-conditions": (
        "The authors analytically show that QAOA energy approximates that of quantum annealing under two "
        "conditions: the angles vary smoothly from one layer to the next and their sum is bounded by a constant."),
    # g47: each limit as its quote gives it (the offline training, the machine time and "one of the analyses"
    # are not in them).
    "wang-qiml-offline-fixed-generator": (
        "The authors state that the limited scalability and noise of NISQ superconducting devices make full "
        "end-to-end quantum training infeasible at present."),
    # review of 5744e2d: the cut lost the scope. The paper ran its examples on real hardware; only this
    # subsection's analysis was simulated, for machine time (the sentence quoted whole in EXTRA_QUOTES).
    "yang-simulator-limit": (
        "The authors state that, because the large amount of test data would consume too much machine time, they "
        "only performed the simulation of quantum computation on a simulator for the analysis in this "
        "subsection."),
    # g49: each as its quotes give it; the theorem number to the anchor; each limit without the result or the
    # unquoted part mixed into it.
    "chicano-theorem1-exponential": (
        "The paper proves that, for a number of QAOA layers p that is a constant independent of the problem size "
        "n, under its condition on the angles, one can build a family of linear Ising models for which the QAOA "
        "runtime grows exponentially with the problem size n."),
    "bucher-scaling-limit": (
        "The authors state that they limit evaluation to p = 12, and that deeper layers could likely lead to "
        "better TTS."),
    "chen2024-scope-larger-molecules": (
        "The authors state that the study compares VQD and SSVQE in determining the low-lying excited states of "
        "LiH, and that investigating their effectiveness on larger chemical molecules is crucial."),
    "chernyavskiy-limits": (
        "The authors state that the approach remains heuristic, that the analysis is restricted to numerical "
        "simulations with system sizes up to n = 30 qubits, and that the simulations of the sampling stage "
        "contain no noise."),
    "chicano-noiseless-oracle-scope": (
        "The authors state that they assume throughout the paper perfect quantum computers with no noise, and "
        "that the runtime they obtain is a lower bound of the real runtime of QAOA for any classical optimization "
        "algorithm."),
    # g50: the result numbers and the figure number to the anchor; each as its quotes give it.
    "st-connectivity-subsumes-learning-graph-wdt": (
        "The paper states that the st-connectivity framework subsumes the (adaptive/extended) learning graph "
        "frameworks and the bomb-testing/guessing-tree/weighted-decision-tree frameworks."),
    "randomized-algorithms-to-st-connectivity": (
        "The paper states that any bounded-error randomized query algorithm can be turned into an instance of the "
        "st-connectivity framework, with the same complexity up to a constant factor."),
    "wdt-speedup-at-most-quadratic": (
        "The authors state that these frameworks can never obtain a more-than-quadratic speed-up over "
        "deterministic algorithms."),
    "drl-agent-average-fidelities": (
        "The authors report average fidelities of 0.9922, 0.9919, and 0.9636 for the cases shown, with standard "
        "deviations of 0.0012, 0.0012, and 0.0361."),
    "nn-solver-one-network-per-eigenstate": (
        "The author states that obtaining each eigenstate requires training a separate neural network."),
    "quadratization-loses-noiseless-quality": (
        "The authors state that the price paid is a loss in the quality of the noiseless solution, and that the "
        "quadratized Hamiltonian is not guaranteed to preserve the ground state of the original problem."),
    "qpic-no-long-term-measure": (
        "The authors state that they did not measure whether QPic could aid long-term acquisition of the relevant "
        "knowledge or whether participants could continue solving similar problems after a long break from the "
        "course."),
    "qpic-comparative-groups-pending": (
        "The authors state that further investigation with comparative groups is underway to explore these "
        "factors in more depth and to refine the teaching approach."),
    # g52: each as its quotes give it (the further work, the extrapolation, "the first iteration" and the DQC
    # algorithm are not in them).
    "degree-scaling-limit": (
        "The authors state that as the degree of the polynomial increases the methods they propose do not scale "
        "favorably with the degree of the polynomial considered."),
    "extrapolates-low-reorg": (
        "The authors state that they constructed three initial training datasets containing 54, 99 and 119 "
        "molecules encoded using N = 7, 16 and 22 bits."),
    "octacene-first-iteration": (
        "The authors report that FM+QAOA was also applied to a larger dataset with N = 22, predicting a compound "
        "(octacene)."),
    "weather-stream-function": (
        "The authors state that they demonstrate how a quantum model can be trained to accurately reproduce "
        "real-world global stream function dynamics at a resolution of 4 degrees."),
    # g51: each setup, scope and limit as its quotes give it (re-uploading, "pretrained", the gradient methods,
    # "polynomial depth" and the analytical suggestion are not in them).
    "setup-ion-trap-no-simulator": (
        "The authors train a binary classifier on a hybrid architecture that combines an ion trap-based quantum "
        "system with a classical processor, using a set of 250 random points in a 2D plane, without the guidance "
        "of any classical simulation."),
    "setup-dataset-and-model": (
        "The authors use 1,223 image patches (723 with cracks and 500 without) and a ResNet18 network as the "
        "classical algorithm, with the features reduced from 512 to 4 in the first linear layer."),
    "backprop-unavailable-on-hardware": (
        "The authors state that backpropagation is not available on real devices, and that a larger number of "
        "evaluations, longer training times and more jobs to submit are the consequences."),
    "scope-small-stage-numerical": (
        "The authors state that they carried out detailed numerical comparisons for small values of p, starting "
        "with p = 1 and continuing with p = 2 and p = 5."),
    "pqc-can-fit-arbitrary-labels-theorem": (
        "The paper shows that parameterized quantum circuits can produce any labeling of arbitrary sets of quantum "
        "states, provided they fulfill its distinguishability condition."),
    # g08: the setup without its result; the comparison as the quotes give it.
    "smpp-noise-aware-14": (
        "The authors state that the instances were evaluated in a noise-free simulation with up to 21 to-be-captured "
        "locations and in a noise-aware simulation with up to 14."),
    "kta-feature-map-comparable-accuracy": (
        "The authors compare eight new approaches with the original across nine varied binary classification "
        "problems from the UCI machine learning repository, and report larger margins on training data (in excess "
        "of 20% larger)."),
    # g01: the scope alone; the NISQ sentence is the authors' claim about the field, not their scope.
    "qinn-simulated-nisq-scope": (
        "The authors state that their paper showcases the ability of a simulated network to estimate the density of "
        "distributions."),
    # g01: the stated limit alone; the MSE is an empirical result.
    "photonic-qrc-zero-bias-power-scope": (
        "The authors state that the zero-bias power figure characterizes the power required to maintain the "
        "reservoir configuration, but not the total system power."),
    # review of 5744e2d: each value says only what its quotes say (the Pauli letters the text layer lost, the
    # cited separation, "cycle graph", "penalty parameter", "standard", the dataset name, the lost superscript).
    "hamlearn-computational-basis": (
        "The authors show that, with state preparation and measurement restricted to the computational basis, for "
        "nearest-neighbor Hamiltonians with only Pauli interactions of the two kinds the source names (their "
        "letters are lost in the text layer), a class which captures contemporary Rydberg atom platforms, all of "
        "the parameters can be reconstructed over 1D and 2D rectangular lattices up to unavoidable gauges."),
    "qaoa-qa-limitation-smooth-angles": (
        "The authors state that an important limitation of their findings is their restriction to gradually "
        "varying QAOA angles."),
    "dtqw-qnn-universal": (
        "The paper proves that the DTQW-QNN is universal for all unitary operations on the overall Hilbert space."),
    "dual-vqe-finite-c-estimate": (
        "The authors state that Theorem 1 guarantees that dual-VQE provides a rigorous lower bound on the "
        "ground-state energy in a limit of c, and that for finite c the value provided by dual-VQE is technically "
        "an estimate rather than a strict bound."),
    "tqnn-mnist-setup": (
        "The authors state that the test uses the MNIST dataset of 60000 images of handwritten digits of shape "
        "28×28, divided into training and testing sets with an 80-20 ratio, and that the two perceptrons are "
        "trained for 10 epochs."),
    "akpinar-glioma-low-performance": (
        "The authors state that, although one rotational gate used as a feature map gives better results in terms "
        "of total processing time, its classification performance value is too low to be generalized."),
    "qsvm-complexity-cited": (
        "The authors state that the overall complexity of the quantum SVM is O (log(NM)), whereas classical "
        "complexity of the SVM is O M2 (M + N) (as the text layer prints it; the superscript layout is lost), where "
        "N is the dimension of the feature space and M is the number of training vectors."),
}
CONTEXT_FIX: dict[str, str] = {}  # an assertion's context where the reader's did not fit
DROP: dict[str, str] = {  # an assertion not entered, with the reason
    "theorem-20-separation": ("g52: the extracted text lost the square root from the bound (it prints 'O(n L)', and "
                              "the root lands in 'ma√y' a line above), so the value would store a wrong complexity"),
    "eqcnn-no-hardware-run": ("g05: the quote lists a hardware run as a possible further step; the value's 'so the "
                              "results are numerical' was the reader's inference, and eqcnn-setup-numerical already "
                              "states the numerical setup"),
    **{aid: ("g09: GPU4PySCF is classical GPU software for density functional theory; its speed-ups bear on no "
             "context of the store (not quantum computing, not QML)")
       for aid in ("gpu4pyscf-30x-speedup", "gpu4pyscf-scf-hessian-speedup", "gpu4pyscf-benchmark-scope")},
    "gbs-graph-nonnegative-no-interference": ("g08: the quote begins 'is nonnegative' and does not name what is; the "
                                              "value's 'adjacency matrix' is not in it"),
    "dqc1-kernel-purity-accuracy": ("g10: the quote stops before what the control qubit's purity is said to "
                                    "improve; the value's 'three datasets' and 'raises the accuracy' are not in it"),
}
VENDOR_DESCRIPTIONS: set[str] = {  # a vendor's description of its own product (MODERATE), not a result
    "dou-qpanda-scope",
}
# A statement about the field, its devices or its literature, not about the paper's own work: LOW, with that
# reason rather than "an empirical result". The first group the coordinator kept LOW; the rest were graded HIGH
# "stated limit" and moved here by the fresh-eyes review of 5744e2d.
FIELD_STATEMENTS: set[str] = {
    "gonon-no-learning-advantage-established", "advantage-immature", "quantum-game-learning-infancy",
    "cv-encoding-overhead-limit", "classical-can-outperform-large-scale", "qnlp-limited-small-datasets",
    "casas-no-experimental-realization",
    "qubo-precision-limits-quality", "radio-measurement-reencode-limit", "qtm-comparable-libraries-caveat",
    "backprop-unavailable-on-hardware", "qcnn-scaling-limit", "liao-open-coherence-question",
    "nisq-tda-few-high-betti-examples", "pulsar-qsvm-scaling-limit", "hybrid-interaction-open",
    "jaderberg-fair-comparison-open", "qaoa-hardware-demand-limit", "qsvm-device-limit", "infoqgan-minelimit",
    "mironowicz-challenges-remain",
}
# Every HIGH grade: (basis, where the paper settles it), after the coordinator's read. A measured result,
# even a negative one, is empirical and stays LOW (Sprint 11's fresh-eyes review): g05's
# transmon-reuploading-not-beating-linear and transmon-reuploading-slow-training. The fresh-eyes review of
# 5744e2d moved 18 out of HIGH: 14 statements about the field (FIELD_STATEMENTS), and 4 conclusions drawn from
# the paper's own measurements (qhpo-not-worth-short-searches, qals-tsp-solution-not-valid,
# smpp-cannot-compete-yet, vqsd-zero-povm-limit). "We do not claim X" is a stated limit; "we found X" is a result.
HIGH = high_grades({
    # g05
    "sc-circuit-review-scope": ("scope", "abstract, p.1: a short review, a starter document"),
    "vrp-qsvm-setup-simulated": ("setup", "abstract, p.1, and the acknowledgment: 3- and 4-city cases on simulators"),
    "bosonic-classifier-setup": ("setup", "conclusion, p.6: data sizes, classes and components"),
    "bosonic-classifier-no-entanglement": ("stated limit", "conclusion, p.6: the states are not entangled"),
    "transmon-reuploading-setup": ("setup", "abstract and conclusion: four transmons, one qubit measured"),
    "qise-define-quantum-engineering": ("definition", "section I"),
    "qise-recommendations-scope": ("scope", "section VII, p.22: the recommendations are the authors'"),
    "q3drism-qubit-count-limit": ("stated limit", "conclusion and perspectives: 14 qubits"),
    "q3drism-hardware-limits-local-hamiltonian": ("stated limit", "section 2, Beyond a Local Algorithm"),
    "eqcnn-setup-numerical": ("setup", "abstract, p.1, and the section IV figure captions"),
    # g01
    "qinn-simulated-nisq-scope": ("scope", "introduction, p.2: a simulated network"),
    "qinn-params-mostly-classical": ("setup", "section 4, p.12, and the conclusion: 2k parameters, mostly classical"),
    "phn-hyperparameter-dependence": ("stated limit", "section IV conclusion, p.6"),
    "phn-parameter-counts": ("setup", "appendix A: 769, 3 and 2 parameters"),
    "rflip-mst2-comparison-setup": ("setup", "section 4: the MST2 C++ code as the comparison"),
    "rflip-heuristic-limits": ("stated limit", "section 4, the limitations paragraph"),
    "qml-tutorial-scope": ("scope", "abstract"),
    "qml-tutorial-advantage-definition": ("definition", "section 1.1.2"),
    "qml-vs-classical-setup": ("setup", "sections 3.2 and 3.6: 150 records, 4 simulated qubits"),
    "photonic-qrc-zero-bias-power-scope": ("stated limit", "results, Computing with a zero-power reservoir core, "
                                                           "p.12"),
    "subspace-controllable-setup": ("setup", "section III: 5,000 MNIST-1D samples, 10-fold cross validation"),
    "subspace-controllable-single-task": ("stated limit", "section I: a single classical task"),
    "qcnn-simulated-not-advantage": ("stated limit", "discussion and conclusion: simulated, not evidence of "
                                                     "advantage"),
    # g02
    "symmetrized-coefficient-variance-sum": ("proved result", "Theorem 8, section III"),
    "variance-not-gradient-guarantee": ("stated limit", "section III, after Theorem 8"),
    "dqi-oracle-approximation-gap": ("proved result", "Theorem 1, section 3.2, in the oracle setting it names"),
    "dqi-code-rate-example": ("proved result", "Theorem 2, section 5"),
    "dqi-oracle-caveat": ("stated limit", "section 6 discussion: the result relies on an oracle"),
    "dqi-no-new-primitive": ("scope", "section 6 discussion"),
    "kernel-noiseless-simulation": ("setup", "section II: exact noiseless statevector simulation"),
    "vqe-review-scope": ("scope", "abstract"),
    "hamlearn-uniform-control": ("proved result", "section 2.1, for generic 2-local Hamiltonians"),
    "hamlearn-computational-basis": ("proved result", "section 2.2, 1D and 2D rectangular lattices"),
    "hamlearn-no-heisenberg": ("proved result", "Theorem 3, as the outlook states it"),
    "interference-numerical-limit": ("stated limit", "section VIII, Limitations"),
    "interference-retrospective": ("stated limit", "section VIII, Discussion"),
    "qnn-no-advantage-claim": ("scope", "section 6 discussion: an advantage study is out of scope"),
    # g03
    "mmd-corruption-bound-lemma": ("proved result", "Lemma III.1 with its proof, p.2"),
    "simulation-attack-model-scope": ("stated limit", "sections IV and V, pp.4-5"),
    "simulated-circuits-noise-future-work": ("setup", "section IV-A, p.4, and section VIII, p.10: simulated in "
                                                      "PennyLane"),
    "iqp-rkhs-fourier-representation": ("proved result", "Theorem 1 and Corollary 2, section III, p.3"),
    "iqp-synthetic-only-limit": ("stated limit", "section V, p.12"),
    "hamiltonian-embedding-generalization-bound": ("proved result", "Theorem 2 and Corollary 3, section III-A, "
                                                                    "conditional on a low-energy ground state"),
    "hamiltonian-embedding-open-advantage-question": ("stated limit", "section V, p.20"),
    # g04 (zhu-heterogeneity-needed stays LOW: an observed decline is a measurement)
    "gqw-noise-untested": ("stated limit", "section V, p.16: noise and other spectra untested"),
    "bentellis-no-generalization": ("scope", "section V, p.7: two processors and one algorithm only"),
    "giuliani-poly-resources": ("proved result", "Theorem 1 and Corollary 1, under the efficient-learning "
                                                 "assumption"),
    "giuliani-sample-limit": ("stated limit", "section 6, p.8"),
    "heredge-resnet-possible": ("proved result", "Theorem 1, pp.7-8"),
    "heredge-exponential-success-decay": ("stated limit", "section II, p.12"),
    # g06
    "ikeda-definition-qefg": ("definition", "Definition II.1, section II.B, p.5"),
    "ikeda-scope-1d": ("scope", "section IV, p.9: a one-dimensional lattice"),
    "liao-setup-models": ("setup", "abstract and section I: the unitary TTN and the MERA"),
    "oh-setup-simulation": ("setup", "section 4 and conclusion: 20 instances, eight input qubits"),
    "ren-review-scope": ("scope", "conclusions"),
    "sahin-setup-datasets": ("setup", "abstract: synthetic data and a breast cancer dataset"),
    "sahin-no-guarantee": ("stated limit", "conclusion, p.9"),
    "setty-setup-problems": ("setup", "abstract, p.1: the problems solved"),
    "setty-quantum-advantage-open": ("stated limit", "section 4, p.12"),
    "tancara-setup-simulation": ("setup", "abstract: simulated damping channels make the dataset"),
    "wang-symmetric-ansatz-proved": ("proved result", "section 6 and section 1 item 2: the paper's own 'We prove'"),
    "wang-setup-gsp": ("setup", "abstract and section 6: ground state preparation"),
    "wang-future-generalization": ("stated limit", "section 6, p.9: machine learning left to future work"),
    # g10 (subpool-little-impact stays LOW: an observed result)
    "dqc1-kernel-exponential-measurements": ("stated limit", "discussion and conclusion, p.8"),
    "iqp-sampling-hardness-checked-small": ("setup", "section III: up to 20 qubits (the conclusion says 16)"),
    "iqp-target-distribution-known": ("setup", "section IV: the target distribution is assumed known"),
    "multi-angle-qaoa-lie-dimension": ("proved result", "abstract and section XI: the six families"),
    "barren-plateaus-only-multi-angle": ("stated limit", "section XI discussion, pp.17-18"),
    "determinant-sampling-theorem": ("proved result", "Theorem 1.3, section 1, and Theorem 5.5"),
    "determinant-sampling-classical-open": ("stated limit", "section 1"),
    "nqs-ite-no-symmetries": ("setup", "section 5, p.15: no symmetries used"),
    "tc-avqite-small-molecules": ("scope", "abstract and section V: H4, LiH and H2O"),
    "gpt-qe-proof-of-concept": ("stated limit", "section 4: a proof of concept; larger molecules needed"),
    # g09
    "analog-vec-linear-parameters": ("setup", "abstract and section II: parameters linear in the qubits"),
    "analog-vec-simulation-only": ("scope", "abstract and section V: numerical simulations; hardware future work"),
    "mcm-cb-protocol": ("setup", "abstract: the joint Fourier transform"),
    "mcm-cb-complete": ("proved result", "Theorem 2, section V"),
    "mcm-cb-unlearnable": ("stated limit", "section VIII, pp.23-24"),
    "ent-advantage-constant-vs-linear": ("proved result", "Theorem 1, sections I and II"),
    "ent-advantage-scope": ("scope", "section III discussion, pp.6-7: a contrived task, two model families"),
    "qhopfield-gardner-method": ("setup", "abstract: the method proposed"),
    "ambulance-gate-simulator-scope": ("scope", "section VIII A, p.53: gates on a simulator, annealing live"),
    "qclassifier-robust-weak-local": ("proved result", "Theorems 1 and 2, methods"),
    "qclassifier-robust-threat-model": ("scope", "introduction, p.2: a classical adversary"),
    "qclassifier-robust-universal-evidence": ("stated limit", "abstract and section III, p.10: evidence only"),
    "bayes-pqc-limits": ("stated limit", "section VI, pp.8-9"),
    # g07
    "asaoka-noise-free-simulation": ("setup", "abstract: noise-free statevector simulation"),
    "barthe-universality-proved": ("proved result", "abstract and section VI: constructive proofs"),
    "barthe-necessary-conditions-tradeoff": ("proved result", "abstract, sections I and VI"),
    "barthe-advantage-left-open": ("stated limit", "section VI"),
    "chan-lih-single-gadget-limit": ("stated limit", "the quantum chemistry paragraph"),
    "chern-shimming-definition": ("definition", "part I.B"),
    "chern-scope-advantage-processor": ("scope", "part VII conclusions, p.21"),
    "nakayama-dataset-setup": ("setup", "abstract: six Hamiltonians, 4 to 20 qubits, 300 samples a class"),
    # g08
    "gbs-graph-better-classical-possible": ("stated limit", "section VI, p.9"),
    "photonic-psr-limit-landscape": ("stated limit", "section 4, p.5"),
    "kta-feature-map-open-work": ("stated limit", "section 4 conclusion, p.20"),
    "quenc-setup-simulation-and-qpu": ("setup", "abstract: simulations and a superconducting processor"),
    "quenc-measurements-linear": ("setup", "section 7 conclusion, p.20: the encoding's measurement count"),
    "smpp-noise-aware-14": ("setup", "section V, p.5: 21 and 14 locations"),
    "httn-sizes-tested": ("scope", "section V, p.12: the system sizes"),
    "httn-scaling-limit": ("stated limit", "section V, p.12"),
    "tang-no-exponential-speedup": ("proved result", "Theorem 1, and the abstract's consequence"),
    "tang-input-assumption": ("scope", "abstract: under strong input assumptions"),
    "tang-impractical-exponents": ("stated limit", "section 1.4, p.7"),
    # g11
    "olsacher-weak-dissipation-scope": ("scope", "section IV, pp.11-12: weak dissipation, direct device access"),
    "pechal-advantage-not-evaluated": ("stated limit", "section IV, pp.6-7"),
    "rabinovich-setup-14-qubits": ("setup", "abstract and section I: up to 14 qubits at the noiseless optimum"),
    "rabinovich-noiseless-optimum-focus": ("stated limit", "section V, p.8"),
    "roca-jerat-statevector-scope": ("scope", "sections I and III: full wave-function access; no superiority "
                                              "claimed"),
    "smith-vqe-small-scale-setup": ("setup", "abstract: VQE, shown numerically"),
    "smith-kernel-evaluation-limit": ("stated limit", "section VII, p.14"),
    "tapia-fraud-setup": ("setup", "section 1, p.2: credit card fraud data"),
    "tapia-not-proof-of-advantage": ("stated limit", "section 5, p.23"),
    "wang-chip-setup-15-shifters": ("setup", "p.5: the chip's 15 phase shifters"),
    "wang-larger-scale-open": ("stated limit", "conclusion, p.6"),
    "zaborniak-small-sample-limits": ("stated limit", "section IV.C, p.5: 30 structures, one run each"),
    # g12 (gga-vqe-h6-and-qpu-noise-limits stays LOW: "perform poorly" is a measured result)
    "gcim-experiment-setup": ("setup", "p.6: four molecules, seven geometries, STO-3G"),
    "gcim-nonorthogonal-cost": ("stated limit", "GCIM ansatz section, p.4"),
    "benchmark-guidelines-aim": ("scope", "abstract: guidelines toward a standard"),
    "benchmark-attributes-hard-together": ("stated limit", "conclusion, p.35"),
    "hintons-theoretical-scope": ("scope", "introduction, pp.1-2: a theoretical contribution"),
    "hintons-no-benchmark": ("stated limit", "conclusion, p.9: no benchmark against classical models"),
    "noise-sim-train-real-test": ("setup", "conclusions, p.12: trained on simulated, tested on real data"),
    "qrnn-rc-setup": ("setup", "abstract: random weights, only the linear layer trained"),
    "course-design": ("scope", "abstract: the lecture and exercise series"),
    "course-not-yet-evaluated": ("stated limit", "conclusion and future work, p.8: surveys left to a refinement"),
    # g14
    "lu-da-construction-requirements": ("setup", "abstract: single-qubit operations and global Rydberg driving"),
    "lu-da-noise-model-scope": ("scope", "section II, pp.4-5: coherent errors only"),
    "mironowicz-review-scope": ("scope", "abstract: an overview"),
    "moussa-refoqus-geometric-convergence": ("proved result", "appendix, Proposition 4, under its assumptions"),
    "moussa-refoqus-tested-only-two-tasks": ("stated limit", "section VIII: two tasks, no real device"),
    "qin-mbhva-no-errors-considered": ("stated limit", "section 4"),
    "qin-mbhva-theoretical-cz-scheme": ("scope", "section 4: a theoretical analysis, CZ scheme"),
    "sachdeva-no-advantage-over-cplex": ("stated limit", "section V conclusion"),
    "sachdeva-comparison-qualifications": ("stated limit", "section V conclusion"),
    "sadhu-study-scope-vqsd": ("scope", "abstract: RL-QAS for VQSD"),
    "sadhu-phase-transition-problem-specific": ("stated limit", "section VI, p.11"),
    "sahu-label-extension-proposal": ("setup", "abstract: label states for the marked nodes"),
    "sahu-early-stage-limit": ("stated limit", "section 5, p.14"),
    "sahu-simple-lattice-scope": ("scope", "section 5, p.14: a 2D lattice without boundary conditions"),
    "wang-hamemb-no-speedup": ("stated limit", "section 3.2, p.12"),
    "wang-hamemb-training-setup": ("setup", "section 3.2, p.12: 20 initialisations, 500 Adam iterations"),
    "wang-principles-incomplete": ("stated limit", "section 4 discussion"),
    # g15
    "zia-setup-oam-single-setting": ("setup", "abstract: OAM as an ancillary degree of freedom"),
    "acuto-setup-digital-simulation": ("scope", "abstract: digital simulation of the circuits"),
    "ai-three-stair-setup": ("setup", "abstract: evaluator and designer, crosstalk errors"),
    "ai-future-error-sources": ("stated limit", "discussion, p.5: further error sources left to future work"),
    "akpinar-setup-nine-maps-pca5": ("setup", "abstract and section V: 9 feature maps, PCA 5"),
    "bowles-open-classical-encoding": ("stated limit", "section 10 outlook, p.31: an open question"),
    "buessen-scope-ising-xy": ("scope", "abstract: Ising and XY spin chains"),
    "callison-scope-depth-limited": ("scope", "abstract: including limited circuit depth"),
    "fadol-quadratic-scaling-limit": ("stated limit", "section 4 discussion, p.13"),
    # g13 (shqmm-no-classical-simulation-advantage stays LOW: a measured result)
    "random-forest-split-setup": ("setup", "section III A: the split and 50 cycles"),
    "hqnn-qubit-setup": ("setup", "section III C, p.6: seven qubits"),
    "single-city-graph-scope": ("stated limit", "abstract and section V, p.10: one city graph"),
    "noiseless-simulators-preliminary": ("stated limit", "section VII, p.12: noiseless simulators"),
    "dwave-hardware-setup": ("setup", "section V B, p.7: the two annealers"),
    "scaling-experiment-setup": ("setup", "section IV A, pp.3-4: 12 qubits, one dataset, noise-free"),
    "noise-study-limited-error-types": ("stated limit", "section V, p.5"),
    "shqmm-overfit-and-classical-data": ("stated limit", "section 4, p.10"),
    "benchmark-setup": ("setup", "section 3.2, p.4: five-level QAOA, 21 to 30 qubits"),
    "l3-cache-limit": ("setup", "section 3.2, p.5: the 64 MB L3 cache"),
    "mgm-bqp-complete": ("proved result", "Theorem 21, p.24"),
    "riccati-polylog-time": ("proved result", "section I A, p.6: the summary of the paper's results"),
    "riccati-assumptions-not-general": ("stated limit", "section VI, p.26"),
    "output-not-pure-state": ("scope", "section VI, p.25: outputs as observables"),
    "conventional-baseline-extrapolated": ("stated limit", "Fig. 2(c) discussion, p.4"),
    "noisy-lossy-platform": ("setup", "outlook, p.5: about 20% losses"),
    # g16 (gonon-no-learning-advantage-established stays LOW: a statement about the literature, not the paper)
    "galvao-scope-quantum-data": ("scope", "abstract: quantum systems, not classical data"),
    "gonon-qnn-error-bound": ("proved result", "Theorem II.4"),
    "gonon-qnn-universal": ("proved result", "Corollary II.7"),
    "gyurik-pac-limit": ("stated limit", "section 4, p.23"),
    "he-qqa-memory-limit": ("stated limit", "section IV conclusion"),
    "he-qqa-simulation-platform": ("setup", "abstract: simulation platforms"),
    "huggins-precomp-model-definition": ("definition", "section 1, p.1: the precomputation cost model"),
    "huggins-selective-teleportation-restricted": ("stated limit", "section 6, p.16"),
    "huijgen-scope-10-qubits": ("scope", "abstract: up to 10 qubits, simulated"),
    "jansen-qudit-product-state-setup": ("setup", "abstract: one qudit per node, a product state"),
    "jansen-no-entanglement": ("scope", "section IV, p.8: without entanglement"),
    "jerbi-no-classical-lower-bound": ("stated limit", "section 5, p.11"),
    # g17 (hqcnn-meningioma-glioma-confusion and photonic-qgan-low-diversity stay LOW: measured results)
    "hqcnn-dataset-and-circuit-setup": ("setup", "sections III A and III C: the dataset, four qubits"),
    "qaoa-decoding-classical-simulation-limit": ("stated limit", "section VI conclusion"),
    "shot-noise-scope-not-cptp-noise": ("scope", "introduction and conclusion: shot noise only"),
    "qsl-review-scope": ("scope", "abstract and section 1: a classical perspective"),
    "qrl-scope-two-state-no-speedup": ("scope", "sections I and IV: dissipation, not speedup; a two-state system"),
    "hl-qft-experimental-challenges": ("stated limit", "section VI conclusion"),
    "qcl-hardware-setup-ibmq-ehningen": ("setup", "section III: ibmq_ehningen, 27 qubits"),
    "qcl-coupled-de-simulator-only": ("scope", "abstract and section VII: on a simulator"),
    "photonic-qgan-experiment-reduced-training": ("setup", "section III F: 1000 iterations, 3000 SPSA steps"),
    # g18
    "tabi-setup-simulated-single-use": ("scope", "abstract and section II: simulated, n = 1"),
    "tomesh-scope-constraint-aware-ansatz": ("scope", "section 1, p.2: the constraint-aware ansatz only"),
    "tudisco-setup-qubits-fixed-pca": ("setup", "section 6, p.19: fixed qubits, PCA"),
    "venkatesh-measurements-exponential": ("stated limit", "section VI, p.6"),
    "venkatesh-setup-synthetic-images": ("setup", "abstract: synthetic images"),
    "wang-setup-hehplus": ("setup", "abstract and introduction: a photonic chip, He-H+"),
    "wiersema-limit-conflicting-labels": ("stated limit", "section V, p.6"),
    "wossnig-theory-needs-benchmark": ("stated limit", "section 1.2, p.19"),
    "zhang-setup-18-qubits": ("setup", "results, p.3: 18 qubits, depth 20, 216 parameters"),
    "zhang-limit-supervised-only": ("stated limit", "discussion and outlook, p.7"),
    # g19
    "zimboras-bp-extrapolation-crude": ("stated limit", "section II.B, p.5: a crude extrapolation"),
    "sequent-scope-limits": ("stated limit", "section 7, p.7"),
    "beaudoin-scope-proof-of-concept": ("scope", "section 4.4, p.6: a proof of concept"),
    "bensberg-derivatives-unavailable": ("stated limit", "section 5, p.21"),
    "nora-not-efficiently-contractible": ("stated limit", "section 1, p.1"),
    "fellner-benchmark-setup": ("setup", "abstract: three systems, 27 tasks"),
    "fellner-idealized-simulation-limit": ("stated limit", "section VI, p.10: idealized conditions"),
    "autoqml-cloud-architecture": ("setup", "section II.A, p.2"),
    "autoqml-brute-force-limit": ("stated limit", "section V, p.7"),
    "gupta-hamiltonian-learning-scope": ("scope", "section 4, p.18: up to 6 qubits"),
    # g21
    "tsp-encoding-results-limited-to-6-nodes": ("scope", "discussion, p.6: up to 6 nodes"),
    "tsp-permutation-encoding-no-hamiltonian": ("stated limit", "conclusions, p.5"),
    "qregression-numerics-classically-emulated": ("setup", "numerical results, p.18: emulated, 13 qubits"),
    "qregression-state-preparation-costly": ("stated limit", "conclusion, p.22"),
    "qvc-radio-dataset-setup": ("setup", "dataset description, p.3: 5000 and 500 per class"),
    "egoqgnn-simulator-setup": ("setup", "experiments, p.8: the OriginQ simulator"),
    "vqa-noise-study-setup": ("scope", "abstract: random QUBO, Gaussian noise"),
    "vqa-noise-limited-data": ("stated limit", "section VI"),
    "qchannel-markovian-limit": ("stated limit", "section II C: the Markovian assumption"),
    "qchannel-ibmq-setup": ("setup", "section III and appendix: ibmq ehningen, 20 000 shots"),
    "qgen-grover-lower-bound": ("proved result", "section IV A"),
    "qgen-scalability-open": ("stated limit", "conclusion, p.14"),
    "vqnn-dataset-setup": ("setup", "experiments, p.4: 200 and 2,000 images"),
    "vqnn-limited-datasets": ("stated limit", "conclusion, p.4"),
    # g20
    "heimann-limit-transfer-to-general-qml": ("stated limit", "section V, pp.9-10: one-dimensional data, RX"),
    "herbst-threats-to-validity": ("stated limit", "section 6.1, p.11"),
    "hodapp-limit-molecule-convergence": ("stated limit", "section 6.3, p.23"),
    "lee-qmaml-setup-simulated-hamiltonians": ("setup", "Figure 3 and results: 12, 20, 10 and 14 qubits"),
    "mohseni-scope-superconducting-gate-based": ("scope", "section I, p.2: superconducting, gate-based"),
    "mohseni-limit-focus-on-cost-criterion": ("stated limit", "section VIII, p.60"),
    "nadim-limit-qsvc-scalability": ("stated limit", "section 5, p.17: more than 500 instances"),
    "periyasamy-limit-proof-of-concept-scale": ("stated limit", "sections I and VI"),
    # g23 (classical-can-outperform-large-scale stays LOW: a statement about the field; reqgan-quality-not-scale-
    # with-qubits stays LOW: a measured result)
    "pqc-approximates-c0-lp-sobolev": ("proved result", "Theorems 2 to 4, pp.2-6"),
    "pqc-approx-assumes-arbitrary-unitaries": ("setup", "section 2, p.4: the second assumption"),
    "l2-convergence-not-other-modes": ("stated limit", "section 2, p.4"),
    "stock-data-binary-three-day": ("setup", "section VI.A, p.14: Apple data, binary"),
    "reqgan-setup-small-mnist": ("setup", "section I, p.4: 25 epochs, 20 images, 2 to 4 qubits"),
    "qshap-scaling-limit": ("stated limit", "section VI, p.12"),
    "qas-decouples-representation-from-search": ("setup", "section 1, p.2: the framework's design"),
    "horizontal-gates-costly-to-decompose": ("stated limit", "section 6, p.12"),
    # g22
    "qng-study-scope-toy-model": ("scope", "section I, p.2: a toy model, not state of the art"),
    "qng-qfim-cost-limit": ("stated limit", "section VII, p.14"),
    "qml-survey-scope": ("scope", "abstract: applications on quantum hardware"),
    "qml-survey-excludes-qrl": ("scope", "section 1, p.1: reinforcement learning not addressed"),
    "cvqe-qpu-cpu-split": ("setup", "abstract: the QPU and CPU roles"),
    "vmpomc-study-scope": ("scope", "abstract: up to N = 100 spins"),
    "vmpomc-bottleneck": ("stated limit", "section 5, pp.9-10"),
    "maqrl-coin-game-setup": ("setup", "abstract: the Coin Game"),
    "maqrl-barren-plateau-caveat": ("stated limit", "section 7"),
    "maqrl-simulator-only": ("stated limit", "section 7: hardware left to future work"),
    "annealing-shared-layout-limit": ("stated limit", "conclusion and outlook"),
    # g24
    "wilkie-setup-8vertex": ("setup", "section III, p.4: 11,117 graphs, L-BFGS, 100 seeds"),
    "wilkie-random-limit": ("stated limit", "section III.A, p.4: up to 10 per graph"),
    "yun-setup-mnist-reduced": ("setup", "section VI, p.10: 4 x 4, four classes"),
    "yun-future-realistic": ("stated limit", "section VII, p.13: real-life scenarios left to future work"),
    "an-dual-model-setup": ("setup", "abstract and conclusion: an LSTM framework"),
    "adermann-setup-422": ("setup", "abstract and section V: [[4,2,2]], simulated, 2 qubits"),
    "baek-proposal": ("setup", "abstract and section 5: sQCNN and RF-Train"),
    "baek-dataset-scope": ("scope", "sections 1 and 4.2.3: MNIST and FMNIST"),
    "beaulieu-setup-mmacd": ("setup", "Fig. 2 caption, p.5: five datasets, five subsamples"),
    "beaulieu-error-caveat": ("stated limit", "sections III.A and IV"),
    "bondarenko-universal-def": ("definition", "introduction, p.2"),
    "bondarenko-scope-product": ("scope", "discussion, p.5: product inputs, classically simulated"),
    # g26
    "napa-nongradient-setup": ("setup", "the NAPA framework section: a non-gradient optimizer"),
    "napa-open-question": ("stated limit", "section VIII"),
    "dtqw-qnn-universal": ("proved result", "Theorem 1, section III, p.4"),
    "dtqw-depth-bound-worst-case": ("stated limit", "section VI, p.8"),
    "pwmcts-scaling-noise-limit": ("stated limit", "section 5, p.19: noiseless simulations"),
    "qedc-ml-early-stage": ("scope", "section VII, p.21: an early-stage version"),
    "single-qubit-scope": ("scope", "section 4, p.9: a single qubit"),
    "qram-fixed-ansatz-no-incremental": ("stated limit", "section 6, p.5"),
    "eqv-test-set-setup": ("setup", "section IV, p.3: 300 and 30 MNIST-2 images"),
    # g25 (ld-daqc-unit-overlap-epsilon stays LOW: an unnumbered derivation the paper itself calls idealized)
    "vqe-benzene-experiment-setup": ("setup", "sections 2.5 and 4: single-point evaluations, 8 qubits"),
    "qsann-near-term-scope": ("scope", "section V.B, p.4: the variational-circuit model"),
    "qsann-dataset-size": ("setup", "section V.C, p.5: 74 and 31 samples"),
    "post-selection-limit": ("stated limit", "section VII.E, p.9"),
    "ld-daqc-resource-assumptions": ("setup", "section VI.D, p.11: gate times, noise-free"),
    "ld-daqc-idealized-limit": ("stated limit", "section IV, after Eq. (16)"),
    "vqe-benchmark-molecules-setup": ("setup", "section 5, p.18: six molecules, MindQuantum"),
    "vqe-benchmark-ram-limit": ("stated limit", "section 5, p.18"),
    "hamming-net-simulated-data": ("setup", "supplementary information, p.9"),
    "hamming-net-tomography-limit": ("stated limit", "p.8"),
    "multigrid-vqe-simulation-only": ("scope", "sections V.A and VI: Aer, no hardware noise"),
    "multigrid-vqe-seed-ansatz-arbitrary": ("stated limit", "section IV, p.5"),
    "zxw-four-shift-nogo": ("proved result", "Theorem 4.16"),
    "zxw-2n-term-shift-rule": ("proved result", "abstract and Theorem 4.13"),
    "zxw-bp-tool-cannot-prove": ("stated limit", "section 6.2"),
    # g27
    "rbm-dbm-universal-ansatz": ("proved result", "abstract: the closure and universality proved, analytic "
                                                  "coefficients"),
    "rbm-dbm-circuit-scaling": ("proved result", "abstract: the construction's qubit and depth counts"),
    "block-encoding-success-decay": ("stated limit", "section III, p.5"),
    "dos-qtda-protocol": ("scope", "abstract: a DOS-based protocol"),
    "simulators-only-noise-untested": ("stated limit", "section 4, p.8: simulators only"),
    "qae-simulator-and-limits": ("stated limit", "sections V and VI: a statevector simulator"),
    "scaling-untested": ("stated limit", "section V, p.9"),
    "eevqe-limits": ("stated limit", "section V, pp.11-12"),
    # g28
    "afqmc-cost-prefactor": ("stated limit", "section V, p.12"),
    "mvqn-roots-of-unity": ("definition", "abstract: truth values as roots of unity"),
    "mvqn-no-hardware-yet": ("stated limit", "section IV, pp.10-11: not yet realized experimentally"),
    "teleport-routing-assumed-errors": ("stated limit", "section 3.1, p.9: assumed future error values"),
    "review-scope-ml-for-qc": ("scope", "abstract: the review's topics"),
    "review-not-in-depth": ("scope", "section 1, p.2: a broad overview"),
    "trojannet-threat-model": ("setup", "section IV: the threat model"),
    "qai-scope-not-completeness": ("scope", "section 6: no claim to completeness"),
    "dmet-vqe-future-noise": ("stated limit", "conclusions, p.16: error mitigation left to future work"),
    # g30 (the maring-* gate and photon figures stay LOW: a vendor's measured results)
    "tqnn-mnist-setup": ("setup", "sections VI A and VI B: MNIST, 80-20, 10 epochs"),
    "tqnn-needs-quantum-hardware-limit": ("stated limit", "sections VI B and VIII"),
    "aqnn-retrieves-min-relative-entropy-attractor": ("proved result", "Lemma 2, section 2.1, p.4"),
    "aqnn-scope-maximal-storage": ("scope", "section 1.1, p.2: maximal storage capacity only"),
    "aqnn-coherence-entanglement-no-help": ("proved result", "Propositions 6 and 7, section 2"),
    "fermionic-hubbard-heisenberg-scaling": ("proved result", "Theorem 1, section II A, p.4"),
    "fermionic-hubbard-class-scope": ("scope", "abstract and Theorem 1: the Hamiltonian class"),
    "fermionic-hubbard-ancilla-overhead": ("stated limit", "abstract and section III, p.19"),
    "qavb-numerical-setup": ("setup", "section VI: GMM clustering, two and ten datasets"),
    "fully-feasible-vqc-setup": ("setup", "section V, p.8: 100 instances, l = 1, 2, 3"),
    "fully-feasible-vqc-limit": ("stated limit", "section VI, p.9"),
    "noisy-ae-fisher-matrix-diagonal": ("proved result", "section III: the diagonal Fisher matrix"),
    "noisy-ae-scope-and-condition": ("scope", "section I, p.2: depolarization of unknown intensity"),
    "qbm-information-matrix-formulas": ("proved result", "Theorems 1 and 2"),
    "qbm-no-numerics-open-barren-plateau": ("stated limit", "section VII, p.11"),
    # g32
    "sqp-scope-limited-not-ruled-out": ("stated limit", "conclusion, p.9"),
    "qlg-negative-semidefinite-proof": ("proved result", "section II: the theorem and its proof"),
    "mle-hl-local-hamiltonian-limit": ("stated limit", "section V, p.8"),
    "qnlp-dataset-limit": ("stated limit", "abstract, p.2: a small dataset"),
    "hqnn-qcnn-scalability-limit": ("stated limit", "section 2"),
    "qaoa-vrp-scalability-limit": ("stated limit", "abstract and section 4.6"),
    "1p1q-simulation-scope-limit": ("stated limit", "encoding section, p.3: jets only, ten constituents"),
    # g31 (qaoa-labs-idealized-setting and qsnn-boundary-confusion stay LOW: a result's interpretation, a measured
    # result)
    "qaoa-labs-no-claim-best": ("stated limit", "introduction, p.3"),
    "fmnist-training-classical-scope": ("scope", "introduction and discussion: trained classically, no advantage "
                                                 "sought"),
    "qrbm-stated-limits": ("stated limit", "section VI, p.5"),
    "qgl-survey-scope": ("scope", "section 1, p.2"),
    "qhnn-small-size-limit": ("stated limit", "section 3: small sizes, N = 10"),
    # g29 (advantage-immature stays LOW: a statement about the field)
    "fashion-mnist-setup": ("setup", "section 3, p.9: 1000 images per class, PCA to 10, 500 RBMs"),
    "no-speedup-guarantee": ("stated limit", "discussion and conclusion, p.14"),
    "vqls-sim-setup": ("setup", "section V: 10 matrices, depth 1 to 20"),
    "entanglement-tradeoff": ("stated limit", "section VI"),
    "unique-minimum-generic-case": ("proved result", "Corollary 6, section III.4"),
    "deep-qaoa-sim-setup": ("setup", "section I: up to 1000 layers, downhill simplex"),
    "neglected-aspects": ("stated limit", "section VI"),
    "dense-mlp-proof-of-concept": ("scope", "section III A: a proof of concept"),
    "pca-gauge-limit": ("stated limit", "section V"),
    "nash-equals-kkt-bss": ("proved result", "Theorem 3.1"),
    "alternating-br-converges": ("proved result", "Theorem 4.1"),
    "classical-mwu-result-fails": ("proved result", "section 5, Theorem 5.1"),
    "open-convergence-questions": ("stated limit", "section 8"),
    "noise-deconvolution-scope": ("scope", "chapter 8: a known, invertible noise map"),
    "qfid-eval-setup": ("setup", "section V: 25 QASMbench circuits, Aer noise models"),
    "qfid-limits": ("stated limit", "sections V-C and VII"),
    # g34
    "reservoir-setup-lorenz63": ("setup", "introduction, p.1: four reservoirs, Lorenz63"),
    "gasp-method-scope": ("scope", "abstract: GASP for QSVM kernel circuits"),
    "dpqc-no-barren-plateau-condition": ("proved result", "Theorem 1, section I B 3, p.4"),
    "dpqc-at-least-as-expressive": ("proved result", "section I B 2, p.3 (Observation 1)"),
    "dpqc-trainability-open": ("stated limit", "section VII, p.22"),
    "dpqc-numerics-size-open": ("stated limit", "section VII, p.22"),
    "evaluation-setup-pdbbind": ("setup", "section III, p.8: the 2020 PDBBind core set"),
    "hs-modular-scope": ("scope", "introduction, p.1: modules, not a standalone course"),
    # g35 (kang-two-qubit-noise-poor stays LOW: a measured result; larson-convergence-proved stays LOW: the
    # statement is cut short in the text layer and no theorem was read)
    "gustafson-hessian-dependence-limit": ("stated limit", "section V, p.7"),
    "harvey-classically-simulable": ("scope", "section 2, p.3: classically simulable by design"),
    "huang-no-barren-plateau-no-advantage": ("stated limit", "section VIII, pp.12-13"),
    "kang-assumption-error-corrected-cz": ("setup", "abstract: error-corrected CZ assumed"),
    "larson-noise-estimate-limit": ("stated limit", "section 5, p.30"),
    # g33 (tree-unitarity-tradeoff-butterfly-velocity and qcc-bounds-bures-entanglement-distance stay LOW: a
    # fragment, and an interpretation of the theorems)
    "hamiltonian-locality-testing-operator-norm-hard": ("proved result", "section 1, p.2"),
    "hamiltonian-learning-exponentially-hard-average-case": ("proved result", "abstract: the learning lower bound"),
    "hamiltonian-testing-no-inverse-evolution": ("setup", "section 1.1, footnote 1, p.2"),
    "qals-implementation-setup": ("setup", "section 6, p.24: C++ and Python, D-Wave, Hybrid baseline"),
    "tree-unitarity-solvable-dynamics": ("proved result", "abstract and section VII"),
    "tree-circuits-scope-spacelike-tree": ("scope", "section I, p.2: spacelike trees only"),
    "muta-proposed-universal-qnn": ("proved result", "section IV.A, Property 2"),
    "muta-hardware-scope-photonic-gkp": ("scope", "section V, p.9: photonic GKP"),
    "che-theorem2-geometric-locality-scope": ("scope", "Theorem 2, section III: geometrically local circuits"),
    "rle-fed-vqe-test-setup": ("setup", "abstract: LiH and H2, the bases"),
    "rle-fed-vqe-limit-ansatz": ("stated limit", "numerical results discussion"),
    "ppn-setup-opo": ("setup", "abstract: a bistable OPO"),
    "ppn-demo-speed-limited": ("stated limit", "discussion, pp.6-7"),
    "aam-qaoa-converges-high-depth": ("proved result", "section V"),
    # g36 (qaoa-tl-aspen-no-recovery stays LOW: a measured result; swaptest-qnn-two-layer-equivalent stays LOW:
    # Proposition 6 holds only up to an error the value does not carry)
    "sunflower-graph-mild-expander": ("proved result", "Theorem 3.5"),
    "sunflower-quantum-pathfinding-poly-time": ("proved result", "Theorem 5.4"),
    "sunflower-classical-exponential-oracle-model": ("proved result", "Theorem 6.3"),
    "qrc-rv-reservoir-setup": ("setup", "results: 10 qubits, 3 layers"),
    "qrc-rv-no-advantage-claim": ("stated limit", "closing discussion"),
    "qaoa-tl-hardware-setup": ("setup", "section IV, p.8: three MIS instances, four devices"),
    "hqcnn-simulation-setup": ("setup", "methods: an Apple M4 CPU"),
    "hqcnn-simulation-only-limit": ("stated limit", "discussion: simulations only"),
    "semiauto-eigensolver-no-convergence-guarantee": ("stated limit", "section 4"),
    "swaptest-qnn-module-assumption": ("setup", "section 5, p.13: the swap-test module assumed"),
    "swaptest-qnn-no-empirical-evaluation": ("stated limit", "section 5, p.13: theory only"),
    "xqml-simulator-limit": ("stated limit", "section IX: a simulator only"),
    "xqml-iris-setup": ("setup", "abstract: Iris, VQC and QSVC"),
    # g37
    "rl-mot-limited-parameters": ("stated limit", "discussion and outlook"),
    "sdp-five-problems-scope": ("scope", "abstract: five problems as SDPs"),
    "sdp-intractable-at-scale": ("stated limit", "section 9, p.29"),
    "qml-monograph-scope": ("scope", "abstract: the monograph's audience and topics"),
    "qwalk-simplicial-algorithm": ("setup", "abstract: the walk and its Fourier coin"),
    "qwalk-limited-validation": ("stated limit", "sections 5 and 6: one network"),
    "qaoa-tutorial-scope": ("scope", "overview, p.1: a tutorial, ibmq_ehningen"),
    "muse-simulation-only": ("stated limit", "section VI: no hardware runs"),
    # g39 (gnn-expressibility-extrapolation-limit stays LOW: a measured result)
    "qnn-sublinear-convergence-pauli": ("proved result", "Theorem 3.2"),
    "qnn-convergence-setup": ("setup", "section 1, p.3: the mean square loss"),
    "qnn-convergence-limit-m-gt-1": ("stated limit", "section 5, p.14"),
    "qfl-scope-ordinary-qc": ("setup", "section I: QFLGD on ordinary quantum computers"),
    "qfl-demo-simulated-steps": ("scope", "section VI: some steps simulated in Qiskit"),
    "certrand-soundness": ("proved result", "abstract: soundness in two senses"),
    "certrand-verification-limit": ("stated limit", "abstract: about 60 qubits"),
    "paoa-no-interference": ("definition", "section II, p.3"),
    "ts-aim-setup": ("setup", "abstract: the teacher-student scheme"),
    "gnn-expressibility-dataset": ("setup", "abstract: 25,000 and 12,000 samples"),
    "lierank-exponential-cost": ("stated limit", "section V, p.9"),
    "lierank-approximation-heuristic": ("stated limit", "section V, p.9"),
    # g38
    "gsp-analysis-setup-adiabatic": ("setup", "abstract and section IV: the adiabatic recasting"),
    "portfolio-simulator-15-qubits": ("setup", "experimental setup: 100 problems, 15 qubits"),
    "tn-search-limits": ("stated limit", "section V"),
    "wazni-setup-simulator-small-dataset": ("stated limit", "abstract and section 7: simulation, a small dataset"),
    "dual-vqe-proposal": ("definition", "abstract: the dual-VQE"),
    "dual-vqe-finite-c-estimate": ("stated limit", "section V: an estimate for finite c"),
    "sqnn-simulator-17-qubit-limit": ("stated limit", "abstract and section V-B: a simulator, 17 qubits"),
    "coreset-limits": ("stated limit", "section V"),
    # g40 (the measured gradient, kernel, timing and loading results stay LOW)
    "bayes-gradient-shot-noise-only": ("setup", "Introduction, p.2"),
    "fermionic-consistency-np-complete": ("proved result", "Theorem 1, section 1.2"),
    "fermionic-proper-pac-hard": ("proved result", "Corollary 1, section 1.2"),
    "fermionic-improper-pac-open": ("stated limit", "section 1.3, p.9"),
    "vqe-scope-hydrogen-pauli-sim": ("setup", "sections III and V"),
    "adaptive-synthetic-data-scope": ("scope", "abstract"),
    "qhpo-proprietary-vueling-data": ("setup", "section II"),
    "pqk-single-dataset-limit": ("stated limit", "section 6"),
    "pqk-noiseless-simulator": ("setup", "section 6"),
    "loading-connectivity-limit": ("stated limit", "section 5"),
    # g41 (the measured and claimed results stay LOW; usatyuk-style labels are not limits)
    "qnn-as-ridge-function-sum": ("proved result", "section 2: the matrix derivation"),
    "rus-fusion-and-universality-proofs": ("proved result", "Theorems 6.4 and 6.10"),
    "fusion-network-factorization": ("proved result", "Theorem 4.15"),
    "xy-flow-only-x-and-y-fusions": ("stated limit", "section 7"),
    "qal-two-scenarios-setup": ("scope", "section V, p.11"),
    "workforce-sample-20-managers-17-companies": ("setup", "section II.A, p.2"),
    "workforce-sample-not-representative": ("stated limit", "section II.B, p.3"),
    "qml-intro-scope": ("scope", "abstract"),
    "rydberggpt-architecture": ("definition", "abstract: the encoder-decoder transformer"),
    "lles-tasks-setup": ("setup", "section IV"),
    "lles-scalability-open": ("stated limit", "section IV"),
    # g42 (hoffmann-small-batch-limit stays LOW: a measured result)
    "ganguly-simulator-only": ("setup", "section IV"),
    "ganguly-data-trim": ("setup", "section III.A"),
    "gilfuster-trainable-nondequantizable-exist": ("proved result", "Corollary 4 and section 6, p.10"),
    "gilfuster-bp-trainable": ("proved result", "Proposition 1"),
    "gilfuster-trainability-definition": ("definition", "Definition 1, section 2"),
    "gilfuster-contrived-supervised-only": ("stated limit", "section 5, p.8-9"),
    "grange-tutorial-scope": ("scope", "abstract"),
    "hellstern-scaling-open": ("stated limit", "Conclusion"),
    "henke-benchmarks": ("setup", "abstract"),
    "hoffmann-random-data-setup": ("setup", "section 4.1"),
    "iaconis-approximate-encoding": ("definition", "abstract: the approximate amplitude encoding"),
    "jaderberg-scale-limit": ("stated limit", "section IV"),
    # g43 (orbit-qaoa-shot-setup stays LOW: the shot count is given as an empirical observation)
    "krylov-search-range": ("scope", "Fig. 1 caption, p.1"),
    "joch-scope": ("scope", "abstract"),
    "kairon-bp-ec-equivalence": ("proved result", "Theorem 1, section III"),
    "kairon-no-advantage-claim": ("stated limit", "section IV"),
    "kundu-no-real-hardware": ("stated limit", "section 7.2"),
    "kundu-three-problems": ("stated limit", "section 7.2"),
    "kundu-sok-scope": ("scope", "abstract"),
    "lee-binary-only": ("scope", "section 6"),
    "infoqgan-setup": ("setup", "2-dimensional data generation section"),
    # g46 (pathmatters-resources-limit stays LOW: a measured result)
    "autoqml-statevector-simulation-only": ("setup", "section V, p.8"),
    "autoqml-supervised-only": ("scope", "section V, p.8"),
    "rff-sufficient-conditions-dequantization": ("proved result", "Propositions III.3 to III.5"),
    "rff-hamiltonian-encoding-scope": ("scope", "section V, p.9"),
    "rff-verification-cost-limit": ("stated limit", "section V, p.8"),
    "qtc-pipeline-setup": ("setup", "section IV, pp.3-4"),
    "qtc-framework-limit-categories-features": ("stated limit", "section V, p.5"),
    "qite-noise-error-bounds": ("proved result", "Theorems 1 and 2, section IV"),
    "qite-global-markovian-noise-scope": ("scope", "section V, p.6"),
    "qite-mitigation-future-work": ("stated limit", "section V, p.7"),
    "pathmatters-problem-setup": ("setup", "abstract"),
    "qdmd-classical-hardware": ("setup", "section II, p.3"),
    "qdmd-test-set": ("setup", "section IV, p.5"),
    "genomic-qml-setup": ("setup", "section IV, p.9"),
    # g44 (quantum-game-learning-infancy stays LOW: a statement about the field)
    "qgnn-no-empirical-eval": ("stated limit", "section 7.2, p.35"),
    "qgd-no-guarantee-vs-all-classical": ("stated limit", "section I, p.2"),
    "ftql-constant-regret": ("proved result", "abstract and section 7"),
    "ftql-only-pure-equilibria-stable": ("proved result", "abstract and section 7, p.14"),
    "qtm-scope-single-machine-simulation": ("scope", "abstract and sections III and IV"),
    "eqbm-info-matrices": ("proved result", "abstract and section VII, p.19"),
    "fisher-bures-wy-factor-two": ("proved result", "section VII.A and Corollary 8"),
    "eqbm-no-simulation-yet": ("stated limit", "section VII.B, p.20"),
    "gnn-ae-bv-small-circuits": ("scope", "abstract and section I"),
    "gnn-ae-preliminary-future": ("stated limit", "section IV, p.4"),
    "mpstime-small-dataset-scope": ("scope", "section V, p.21"),
    "mpstime-fixed-length": ("stated limit", "section V, p.21"),
    # g45 (qnlp-limited-small-datasets and cv-encoding-overhead-limit stay LOW: statements about the field)
    "phase-circuits-need-symmetric-patterns": ("stated limit", "section VIII, p.17"),
    "pi-qml-simulation-scope": ("setup", "section V"),
    "dcqaoa-docking-simulated-on-gpu": ("setup", "abstract"),
    "vqe-h2-qiskit-ibm-setup": ("setup", "abstract"),
    "cv-encoding-setup-churn": ("setup", "Methods, p.2"),
    # g48 (qcbr-classical-better-some-cases stays LOW: a measured result)
    "implicit-diff-bell-sensitivity": ("stated limit", "section 4.3, p.14"),
    "qaoa-no-general-guarantee": ("stated limit", "abstract"),
    "qaoa-scope-maxcut-512": ("scope", "abstract and section 6"),
    "varemb-noise-not-studied": ("stated limit", "Discussion"),
    "qubo-scope-16-variables": ("scope", "section 1"),
    "qgrid-utility-needs-more-study": ("stated limit", "section 6"),
    "qaoa-qa-equivalence-proof": ("proved result", "Theorem III.4"),
    "qaoa-qa-conditions": ("proved result", "abstract: the analytic result"),
    "qaoa-qa-limitation-smooth-angles": ("stated limit", "Discussion, p.17"),
    # g47 (the measured hardware, accuracy and cost results stay LOW)
    "tucker-hardware-setup": ("setup", "section 6, p.31"),
    "wang-qiml-offline-fixed-generator": ("stated limit", "section 3.4, p.26"),
    "wang-qiml-qubit-scale": ("setup", "section 2, p.4"),
    "watts-unconditional-sampling-separation": ("proved result", "abstract and Theorem 3"),
    "watts-bounded-random-input-scope": ("scope", "abstract"),
    "watts-open-unbounded-inputs": ("stated limit", "section 2, p.9"),
    "yang-simulator-limit": ("stated limit", "section 3.4, p.25"),
    "zalivako-images-chosen-separable": ("setup", "abstract"),
    "zalivako-setup-five-qubits": ("setup", "abstract"),
    "zhang-rf-lower-bound": ("proved result", "Theorem 1, section 3"),
    "zhang-rf-scope-hamiltonian-targets": ("scope", "section 5, p.6"),
    "zhou-quangcn-setup-4-qubits": ("setup", "section 3, p.5"),
    "zhou-quangcn-single-real-run": ("stated limit", "section 3, p.5"),
    "abbas-accuracy-weighted-dequantised": ("proved result", "abstract"),
    "abbas-ensemble-contains-deutsch-jozsa": ("proved result", "abstract"),
    "abbas-dj-reduction-not-useful-ml": ("stated limit", "Conclusion, p.5"),
    # g49 (casas-no-experimental-realization stays LOW: a statement about the field)
    "bucher-architecture-setup": ("setup", "abstract"),
    "bucher-simulation-scale": ("scope", "section VI"),
    "bucher-scaling-limit": ("stated limit", "section V"),
    "casas-circuits-presented": ("scope", "abstract"),
    "casas-ame-definition": ("definition", "section I, p.1"),
    "chen2022-qdrqn-setup": ("setup", "sections 6.1 and 6.3"),
    "chen2024-scope-larger-molecules": ("scope", "abstract and section IV"),
    "cheng-setup-quantum-inspired": ("setup", "abstract and sections V.A-B"),
    "chernyavskiy-limits": ("stated limit", "section V, p.6-7"),
    "chernyavskiy-setup": ("setup", "abstract"),
    "chicano-theorem1-exponential": ("proved result", "Theorem 1, section 3, p.6"),
    "chicano-proved-p1-p2-only": ("stated limit", "section 3, p.7"),
    "chicano-noiseless-oracle-scope": ("scope", "sections 2 and 4"),
    "choy-setup": ("setup", "Appendix A, p.10"),
    # g50 (labs-size-limit-about-30-variables stays LOW: a measured result)
    "st-connectivity-subsumes-learning-graph-wdt": ("proved result", "Result 1.1 (Theorems 5.13 and 5.17)"),
    "randomized-algorithms-to-st-connectivity": ("proved result", "Result 1.2 (Theorem 5.24)"),
    "wdt-speedup-at-most-quadratic": ("proved result", "Result 1.4 (Theorems 5.27 and 5.28)"),
    "st-vs-randomized-open-question": ("stated limit", "Open question 1.5"),
    "feature-selection-limits-simulator-scale": ("setup", "abstract"),
    "drl-stream-learning-qubit-control-setup": ("setup", "abstract"),
    "nn-solver-one-network-per-eigenstate": ("stated limit", "Conclusions, item 7"),
    "qrc-noise-setup-lih-three-channels": ("setup", "sections II and III"),
    "quadratization-loses-noiseless-quality": ("stated limit", "abstract and section V"),
    "review-scope-property-prediction-surrogates": ("scope", "abstract"),
    "qpic-study-design-high-school": ("setup", "abstract and Methods"),
    "qpic-no-long-term-measure": ("stated limit", "section 4, p.32"),
    "qpic-comparative-groups-pending": ("stated limit", "section 4, p.33-34"),
    # g51 (scope-ga-over-gradient-problem-setup stays LOW: a measured result with its scope)
    "setup-ion-trap-no-simulator": ("setup", "Introduction p.2 and Results p.3"),
    "book-omits-complexity-caveats": ("stated limit", "Myth 5, p.98"),
    "scope-simulated-no-full-docking": ("stated limit", "sections 8.2 and 12"),
    "embedding-bottleneck": ("stated limit", "section 13, p.16"),
    "setup-dataset-and-model": ("setup", "sections 4 and 5.1"),
    "scope-small-stage-numerical": ("scope", "section V, p.7"),
    "future-work-classical-comparison": ("stated limit", "section VII, p.12"),
    "pqc-can-fit-arbitrary-labels-theorem": ("proved result", "Theorem 2, section II.E"),
    "scope-tested-regime-no-good-generalization-ban": ("stated limit", "abstract and section II.E"),
    # g52 (chem-accuracy-limit stays LOW: a measured result)
    "degree-scaling-limit": ("stated limit", "section VI"),
    "extrapolates-low-reorg": ("setup", "abstract: the three training datasets"),
    "noiseless-emulation-only": ("setup", "section V"),
    "gsqas-method": ("definition", "abstract: the pre-training and the predictor"),
    "gsqas-scope": ("scope", "section 6"),
    "weather-no-advantage": ("stated limit", "section VI, p.9"),
    "path-edge-query-complexity": ("proved result", "abstract and section 4"),
    "witness-state-algorithm": ("proved result", "abstract: the main technical contribution"),
    # g53 (the measured accuracies and errors stay LOW)
    "jing-qtrc-numerical-scope": ("scope", "abstract"),
    "jing-qtrc-decoherence-limit": ("stated limit", "Discussion, the decoherence paragraph"),
})

EMPIRICAL = "Started LOW: an empirical result from one study. NOT upgraded"
AUTHOR_CLAIM = "Started LOW: the authors' own claim, not tested in the paper. NOT upgraded"
CITED = "Started LOW: a claim the source cites from other work, not tested in it. NOT upgraded"
FIELD = ("Started LOW: a statement about the field, its devices or its literature, not about the paper's own work. "
         "NOT upgraded")


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def task_f_ids() -> set[str]:
    return {e["record_id"] for e in json.loads(F104.read_text(encoding="utf-8"))["entered"]}


def no_copy(task: str) -> dict[str, str]:
    """The ledger's no_copy records of this task, with their reasons."""
    f_ids = task_f_ids()
    return {rid: why for rid, why in ledger()["no_copy"].items() if (rid in f_ids) == (task == "F")}


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
    otherwise = FIELD if aid in FIELD_STATEMENTS else {"cited": CITED, "shown": EMPIRICAL}.get(a["kind"],
                                                                                                AUTHOR_CLAIM)
    return grade(aid, HIGH, otherwise=("low", otherwise))


def anchor_safe(anchor: str) -> str:
    # A quote mark inside a label would break the quote pattern (Sprint 11 Task D finding).
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
        text = texts.setdefault(p["file"], plain(source_text(p["file"])))
        verified = require_verbatim(a.id, a.citation_context, text, value=a.value)
        if a.id in VALUE_REPLACE:  # the replaced value's passages are the quotes printed with it
            require_edit_basis(a.id, a.value, quotes, text)
        if a.id in QUOTE_EDITS:
            require_edit_basis(a.id, None, [n for _, n in QUOTE_EDITS[a.id] if n] or quotes, text)
        out.append((a, rid, p, verified))
    return out


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
    for rid, why in sorted(no_copy(task).items()):
        reason = (f"{TODAY} ({tag}): NOT read and NOT for the hand-download list: {why}" if "withdrawn" in why
                  else f"{TODAY} ({tag}): selected for reading and NOT read: {why}; on the hand-download list")
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
                          f"{evidence.rstrip().rstrip('.')}; {note}" if evidence and evidence.strip() else note, rid))
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
    unknown = sorted(set(HIGH) - {a.id for _, a, _, _ in assertions("F") + assertions("G")}) if "--all" in args else []
    kept = assertions(task)
    ids = [a.id for _, a, _, _ in kept]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    owner = {a.id: rid for _, a, rid, _ in kept}
    with connect(DB_PATH) as conn:
        clash = [i for i in ids if conn.execute(
            "SELECT 1 FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ? AND "
            "r.provenance NOT LIKE ?", (i, f"%{owner[i]}%")).fetchone()]
    if dupes or clash or unknown:
        print(f"duplicate assertion ids: {dupes}; ids already held by another source: {clash}; "
              f"HIGH ids naming no assertion: {unknown}")
        return 1
    if "--apply" not in args:
        checked = verify(task)
        for a, _, _, _ in checked:
            validate_assertion(a)
        papers = load_groups(task)
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"{len(kept)} assertions from {len(papers)} records "
              f"({sum(1 for _, p in papers if not [a for a in p['assertions'] if a['id_suggestion'] not in DROP])} "
              f"with none); {len(no_copy(task))} with no copy. Every quote verbatim, every edit on named passages, "
              "every figure in its quotes. DRY RUN: nothing written. Re-run with --apply.")
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
