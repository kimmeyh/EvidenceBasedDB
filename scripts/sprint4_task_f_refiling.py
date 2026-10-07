#!/usr/bin/env python3
"""Sprint 4 Task F (F25 D4): the world/method/ml re-filing pass across every
paper record, against the context tests written down first in
docs/INTAKE_WORKFLOW.md section 8.

One-off, kept because it IS the record of what changed and why. Every
paper's applicability rows are REPLACED wholesale by the rows below (the
pass is deliberate: a paper missing from APPLICABILITY fails the coverage
check), every rationale ends with the anchor naming where it was read,
and the old-vs-new context set is written into `updated_reason`.

Evidence: verbatim abstracts (DataCite records for arXiv DOIs, Crossref)
and page-1/2 reads of the local PDFs, gathered 2026-09-19 and quoted in
the rationales; F10's body-read findings are cited where the abstract
alone does not carry the fact (`wang`).

DRY-RUN BY DEFAULT: applies inside one transaction, pushes every paper row
through validate_paper() WITH its applicability (the full door, including
the anchor rule), prints the per-record context diff, rolls back. `--apply`
commits only with zero refusals, then regenerates export/.

Tests that pin applicability sets move in the same commit with the reason:
tests/test_paper_applicability.py (loke gains ml: named classical weak
classifiers and baseline), tests/test_qboost_paper_added.py (neven gains
ml: a boosting framework for classifiers).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.ingest import PaperRecord, append_updated_reason, validate_paper  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-19"
TAG = f"{TODAY} (Sprint 4 Task F, F25 D4 re-filing)"

A = "arXiv abstract"
APPLICABILITY: dict[str, list[tuple[str, str]]] = {
    "alonso-2025-qml-fourier-distribution-option-pricing": [
        ("qml", f"Two hybrid classical-quantum option-pricing methods built on QML models based on Parametrized Quantum Circuits (PQCs), assessed against Quantum Accelerated Monte Carlo -- {A}"),
    ],
    "arute-2019-quantum-supremacy-google-nature": [
        ("qc", "Programmable superconducting Sycamore processor, 53 qubits; one instance of a random quantum circuit sampled a million times in about 200 seconds against an estimated 10,000 years for a classical supercomputer -- PDF p.1 abstract"),
    ],
    "bcg-2022-value-of-quantum-benchmarks": [
        ("qc", "Consulting-firm commentary on quantum-computing investment ($2.15 billion in 2020-2021) and on benchmarks as a source of competitive advantage for investors and end users -- PDF p.1-2 body text"),
    ],
    "bleximo-2020s-applications-and-impact": [
        ("qc", "Vendor overview of Bleximo's quantum hardware applications, opening with a pharmaceutical and materials use case -- PDF p.1 title page and p.2 section slide"),
    ],
    "britt-humble-2017-hpc-with-qpus-acm": [
        ("qc", "Integration of quantum processing units into current and future HPC system architectures; two integration pathways differentiated by infrastructure constraints on the QPU and the use cases expected of the HPC system -- Crossref abstract"),
        ("method", "Proposes new metrics capturing the interplay between system architecture and the quantum parallelism underlying computational performance -- Crossref abstract"),
    ],
    "chen-2025-qml-classical-defi": [
        ("qml", f"Pure quantum models (VQE classifier, QNN, QSVM) and hybrid quantum-classical models (QASA, QuantumRWKV) backtested on decentralized-finance market making -- {A}"),
        ("ml", f"Classical ML baselines Random Forest, Gradient Boosting and Logistic Regression, plus transformer models, in the same backtest -- {A}"),
    ],
    "coleman-2022-guide-to-qc-benchmarking-certification": [
        ("qc", "Trade-press explainer on comparing QPU performance across the stack as the field evolves -- PDF p.2 body text"),
        ("method", "Surveys benchmarking and certification techniques for QPUs and the vendor tooling around them (Classiq, Terra Quantum, River Lane, Unitary Fund, Q-CTRL) -- PDF p.1 diagram and p.2 body text"),
    ],
    "dupont-2023-quantum-enhanced-greedy-solver": [
        ("qc", f"Iterative quantum heuristic optimization on a programmable superconducting quantum system with up to 72 qubits, on Sherrington-Kirkpatrick spin-glass instances, systematically outperforming its classical greedy counterpart -- {A}"),
    ],
    "dwave-2021-recruit-case-story": [
        ("qc", "Recruit's feature-selection method programmed into D-Wave's 2000Q quantum annealer for digital-marketing optimization -- PDF p.1-2 body text"),
        ("qml", "Weak-classifier selection on a quantum annealer, needing 10% of the weak classifiers the classical method needed; a QBoost-shaped hybrid training step -- PDF p.2 body text"),
        ("ml", "Named classical feature-selection baselines: L1 Regularized Logistic Regression (L1LR) and Feature Selection by Random Forest (RFFS) -- PDF p.2 body text"),
    ],
    "dwave-2023-operational-excellence-ebook": [
        ("qc", "D-Wave marketing ebook on quantum annealing for business optimization; generic framing (global competition, supply-chain disruption), no QML content -- PDF p.1-2 slides"),
    ],
    "dwave-2024-unlocking-power-of-quantum": [
        ("qc", "D-Wave marketing ebook opening with a SavantX / Port of Los Angeles logistics case (the HONE framework on D-Wave quantum annealing), followed by the Pattison Food Group and Recruit summaries -- PDF p.1-2 body text"),
    ],
    "dwave-pattison-food-group-case-story": [
        ("qc", "Driver-scheduling auto-scheduler built on D-Wave's quantum computing solutions and deployed to production in late 2022; an 80-hour weekly task cut to 15 hours -- PDF p.1-2 body text"),
    ],
    "emami-2025-financial-fraud-entropy-computing-qci": [
        ("platform:dirac-3", f"CVQBoost leverages early hardware implementing Quantum Computing Inc's (QCi) Entropy Quantum Computing paradigm, Dirac-3; all six authors carry the QCi affiliation on the arXiv listing -- {A} and affiliation block"),
        ("qml", f"CVQBoost, a hybrid quantum-classical boosting classifier, applied to a fraud-detection test case -- {A}"),
        ("ml", f"Benchmarked against XGBoost evaluated on up to 48 CPUs and four NVIDIA L4 GPUs with the RAPIDS AI framework -- {A}"),
    ],
    "freericks-2026-quantum-mechanics-done-right-book": [
        ("world", "Open-access quantum mechanics textbook from novice to researcher; general physics content independent of any project -- PDF p.1 cover and p.2 half-title page"),
    ],
    "huynh-2023-quantum-inspired-ml-survey": [
        ("qml", f"Survey of Quantum-inspired Machine Learning (QiML), positioned against the broader QML field whose review literature it says treats QiML superficially -- {A}"),
        ("ml", f"QiML leverages principles of quantum mechanics within classical computational frameworks (tensor network simulations, dequantized algorithms): classical ML content by its own definition -- {A}"),
        ("method", f"Establishes a concrete definition of QiML by analyzing prior interpretations of the term and their ambiguities, the vocabulary boundary this library uses -- {A}"),
    ],
    "ibm-2023-qiskit-explorer-attendee-guide": [
        ("method", "Self-paced learning program guide for Qiskit (badges, Jupyter notebooks in the cloud, community conduct); a tooling and practice reference -- PDF p.1 title page and p.2 table of contents"),
        ("qc", "Introductory quantum computing through IBM's own platform and community program -- PDF p.2 table of contents"),
    ],
    "idq-quantis-qrng-pcie-brochure": [
        ("qc", "Quantum random number generator PCIe cards exploiting elementary quantum-optic processes; the closest available context, since none fits QRNG hardware -- PDF p.1-2 body text"),
    ],
    "interviewbit-python-cheat-sheet": [
        ("method", "Generic Python reference (operators, data types, functions, dictionaries, sets) that could support any code written here; minimal relevance -- PDF p.1 title page and p.2 table of contents"),
    ],
    "kawchak-2023-coding-tips-cirq-qiskit-pennylane": [
        ("method", "Coding tips for Cirq, Qiskit and PennyLane; a tooling and coding-practice reference, not a research claim -- PDF p.2 body text"),
        ("qml", "PennyLane described as differentiable programming with quantum machine learning; TensorFlow Quantum or Keras for the ML workflows -- PDF p.2 body text"),
    ],
    "kawchak-2023-qiskit-pennylane-qml-demos": [
        ("method", "Catalogue of 38 Qiskit and PennyLane demo notebooks with a developer guide on simulator speed (adjoint differentiation, lightning.qubit over default.qubit) -- PDF p.1 demo catalogue and p.2 developer guide"),
        ("qml", "The demos span quantum neural networks, quantum kernel ML, quantum GANs, quantum CNNs, quantum autoencoders and variational classifiers -- PDF p.1 demo catalogue"),
    ],
    "kawchak-2023-quantum-parameter-study-qml": [
        ("qml", "A 4-qubit quantum circuit with trainable parameters assisting a frozen ResNet50 classifier; accuracy, loss and runtime across three datasets -- PDF p.1 synopsis and p.2 discussion"),
        ("ml", "A ResNet50 neural network without trainable parameters as the classical component -- PDF p.1 synopsis"),
    ],
    "kawchak-2023-resnet50-quantum-transfer-learning": [
        ("qml", "Quantum transfer learning (QTL) head on the default.qubit simulator compared with classical transfer learning on two datasets -- PDF p.1 metrics table"),
        ("ml", "ResNet50 transfer learning on CPU, TPU, V100 and A100 as the classical comparison -- PDF p.1 metrics table"),
    ],
    "kerger-2023-mind-the-o-distributed-quantum-algorithms": [
        ("qc", f"Two algorithms in the Quantum CONGEST-CLIQUE model of distributed computation (approximate Steiner tree, exact directed minimum spanning tree) in O~(n^1/4) rounds -- {A}"),
        ("world", f"Characterizes the constants and logarithmic factors hidden by O~ notation, showing the asymptotic speedups help only for very large n; a proved complexity result independent of any project -- {A}"),
    ],
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu": [
        ("qc", f"Benchmarks runtime and accuracy across simulated and physical QPUs: the QMware and AWS SV1 simulators, Rigetti's Aspen-M2 and IonQ's Harmony -- {A}"),
        ("method", f"A cross-platform benchmarking methodology for simulated versus physical quantum processing units -- {A}"),
        ("platform:braket", f"The AWS SV1 simulator is one of the benchmarked back ends -- {A}"),
    ],
    "lenat-marcus-2023-trustworthy-ai": [
        ("method", f"Methodology for how this library builds and reasons: 16 desiderata for trustworthy AI and Cyc's curated-knowledge, higher-order-logic alternative -- {A}; mined pp. 1-16"),
        ("ml", f"Large language models trained to produce plausible but not necessarily correct outputs, the generative-AI approach the paper critiques -- {A}"),
    ],
    "li-2024-photon-counting-raman-spectroscopy": [
        ("world", "Single-photon counting Raman spectroscopy benchmarked against conventional and surface-enhanced Raman spectroscopy; sensitivity raised by up to eight orders of magnitude, an experimental-physics result -- Crossref abstract"),
    ],
    "loke-2026-cvqboosting-fraud-detection-smu": [
        ("platform:dirac-3", "Keywords name 'Photonic Quantum Processor, Dirac-3'; CVQBoost executed on QCi's photonic Dirac-3 processor -- PDF p.3 keywords and abstract"),
        ("qml", "Keywords name 'Quantum Machine Learning (QML), CVQBoost, Quantum Boosting'; a hybrid quantum-classical boosting ensemble -- PDF p.3 keywords and abstract"),
        ("ml", "Weak classifiers K-nearest neighbours, linear discriminant analysis, logistic regression and XGBoost; mean AUC-PR over 0.8, about 9% over the best published classical baseline -- PDF p.3 abstract"),
    ],
    "lubinski-2023-application-oriented-benchmarks-qedc": [
        ("qc", f"Open-source suite of application-oriented benchmarks measuring quantum hardware effectiveness as circuit width and depth vary, in the volumetric-benchmarking framework -- {A}"),
        ("method", f"A benchmarking methodology this library can apply to cross-platform claims -- {A}"),
    ],
    "mancilla-2026-fourier-wall-spectra": [
        ("qml", f"Conditions under which an angle-encoded quantum neural network (a partial Fourier series) can beat classical baselines on tabular data -- {A}"),
        ("method", f"SPECTRA, a two-tier certificate: a simulator-free structural screen, then a matched quantum model against five tuned classical twins with paired-bootstrap confidence bounds -- {A}"),
        ("ml", f"Gradient-boosted trees reach a held-out ROC-AUC of 0.999 on the real smart-meter target SPECTRA refuses -- {A}"),
    ],
    "mancilla-2026-spectra-datasets-substack": [
        ("qml", "Four industrial datasets re-expressed as periodic phases so a variational quantum model can show an edge; companion post to The Fourier Wall (arXiv:2607.15815) -- PDF p.1-2 body text"),
    ],
    "mandra-2021-hybridq-simulator-nasa": [
        ("qc", f"HybridQ, an extensible hybrid simulator for quantum circuits on CPUs and GPUs with HPC workload balancing across nodes -- {A}"),
        ("method", f"A common framework integrating multiple state-of-the-art simulation techniques; a tool for evaluating circuits without hardware -- {A}"),
    ],
    "merlinquantum-merlin-github-repo": [
        ("qml", "Build, train and benchmark photonic quantum machine learning models using familiar ML tools -- GitHub repository description"),
    ],
    "neven-2012-qboost-adiabatic-quantum-optimization": [
        ("qml", "QBoost: weak-classifier selection for boosting cast as the discrete optimization adiabatic quantum hardware solves; the algorithm CVQBoost descends from -- PDF p.1 abstract and keywords"),
        ("qc", "Training cast into the format required by existing adiabatic quantum hardware (D-Wave), for which no platform context exists -- PDF p.1 abstract"),
        ("ml", "A boosting framework for large-scale binary classifiers; keywords 'machine learning, supervised learning, boosting' -- PDF p.1 keywords"),
    ],
    "notton-2026-merlin-discovery-engine-photonic-hybrid": [
        ("qml", f"Introduces MerLin, an open-source discovery engine for photonic and hybrid quantum machine learning, reproducing eighteen photonic and hybrid QML works (kernel methods, reservoir computing, convolutional and recurrent architectures, generative models) -- {A}"),
        ("method", f"Designed around systematic benchmarking and reproducibility, releasing the reproductions as reusable modular experiments to establish a shared experimental baseline -- {A}"),
    ],
    "pelofske-2022-quantum-volume-nisq-ieee": [
        ("qc", "Quantum volume measured on 24 NISQ devices from IBM Q, IonQ, Rigetti, Oxford Quantum Circuits and Quantinuum; achieved values lag officially reported ones and depend on compilation effort -- PDF p.1 abstract"),
        ("method", "Quantum volume as the de-facto NISQ benchmark, reproduced independently rather than taken from provider reports -- PDF p.1 abstract"),
    ],
    "pere-qml-github-repo-empty": [],
    "qci-2024-profiling-cvqboost": [
        ("platform:dirac-3", "CVQBoost on QCi's Dirac-3, benchmarked against XGBoost on the imbalanced Kaggle credit-card fraud dataset across dataset sizes, feature counts and class-imbalance ratios -- PDF p.2 abstract"),
        ("qml", "CVQBoost, an extension of the QBoost algorithm leveraging quadratic optimization solvers -- PDF p.2 abstract"),
        ("ml", "XGBoost as the classical comparator: higher accuracy when balancing is minimal, CVQBoost catching up under ADASYN/SMOTE balancing, and superior runtime as data and feature counts grow -- PDF p.2 abstract"),
    ],
    "qci-2024-unconventional-computing-medium": [
        ("qc", "QCi's own explainer on unconventional computing in general (what does and does not count as unconventional) -- PDF p.1-2 body text"),
        ("platform:dirac-3", "A lesson from QCi's 'unconventional hardware' learning module, the framing that underpins Dirac-3 -- PDF p.1 body text"),
    ],
    "qci-2026-entropy-computing-trade-magazine": [
        ("platform:dirac-3", "Trade-magazine feature on QCi's Dirac-3 hybrid photonic system and entropy computing for NP-hard optimization, by four QCi authors -- PDF p.2-3 body text"),
    ],
    "rand-2022-pqc-critical-infrastructure-assessment": [
        ("qc", "Assesses quantum computing's cryptographic threat to the 55 national critical functions for CISA, the post-quantum transition -- PDF p.1 title page and p.iii About This Report"),
    ],
    "rand-2022-pqc-critical-infrastructure-assessment-appendix-b": [
        ("qc", "Companion appendix to the RAND post-quantum critical-infrastructure assessment, same subject -- PDF p.1 title page"),
    ],
    "rehman-2026-qstar-adaptive-routing": [
        ("qml", f"Quantum transfer-learning heads (manual and KetGPT-designed) on a frozen ResNet18; selective routing sends uncertain inputs to the quantum branch as a targeted fallback, not a uniform replacement -- {A}"),
        ("ml", f"Parameter-matched classical heads as baselines; the strongest fixed classical head stays highest at 81.6% accuracy -- {A}"),
    ],
    "sakhnenko-2026-data-efficient-qml": [
        ("qml", f"Quantum kernel methods needing fewer training examples than classical kernels to reach comparable error on classical data -- {A}"),
        ("ml", f"Classical kernel methods as the comparison, and a spectral-bias generalization metric brought over from them -- {A}"),
        ("method", f"A data-generation tool for semi-artificial datasets tailored to quantum kernel methods, enabling controlled studies -- {A}"),
    ],
    "tung-2026-qmes-quantum-meta-learning-kernel-encoding": [
        ("qml", f"Encoding-circuit selection for quantum kernel methods -- {A}"),
        ("method", f"Qmes, an open-source package recommending circuits by meta-learning without quantum evaluation at inference, validated on 105 classification and 86 regression datasets -- {A}"),
        ("ml", f"Datasets characterized with classical complexity measures and a pre-trained recommender model; meta-learning is classical ML -- {A}"),
    ],
    "udaru-2025-qml-credit-risk": [
        ("qml", "Quantum support vector machines, quantum neural networks and hybrid quantum-classical models for credit-risk classification, discussed conceptually -- PDF p.2 abstract"),
    ],
    "wang-2025-quantum-optimization-nn-compression": [
        ("qml", f"Pruning-quantization of convolutional neural networks formulated as a QUBO and solved by adiabatic quantum computing; the optimized target is an ML model -- {A}"),
        ("qc", f"Assesses the solution space of commercial quantum annealing devices -- {A}; F10's body read: the D-Wave Advantage ran only the two smallest models and the larger ones ran on a classical Fujitsu Digital Annealer -- docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md"),
        ("ml", f"CNN model compression compared against genetic algorithms and reinforcement learning -- {A}"),
    ],
    "zajac-2026-inverse-born-rule-equivalence": [
        ("qml", f"Real-valued amplitude encodings of classical data; the Inverse Born Rule Fallacy of reading such models as evidence of quantum computational power -- {A}"),
        ("world", f"Proves an Equivalence Theorem: any real-valued amplitude encoding composed with a data-independent unitary and computational-basis measurement yields exactly the class of classical quadratic forms; information-geometric excess identically 0 -- {A}"),
    ],
    "zapata-2025-qc-for-finance-guide": [
        ("qc", "Introductory guide to how quantum computing is transforming finance, written for finance students and professionals -- PDF p.1 preface"),
    ],
}

# One-line dispositions where F10 found adjectives carrying no information,
# stale checkpoint references, or where the evidence read contradicted the text.
DISPOSITIONS: dict[str, str] = {
    "arute-2019-quantum-supremacy-google-nature": "Peer-reviewed Nature paper reporting Google's quantum supremacy claim on the 53-qubit Sycamore processor; a high-value qc reference",
    "dupont-2023-quantum-enhanced-greedy-solver": "Quantum-classical hybrid optimization on up to 72 superconducting qubits benchmarked against classical greedy; relevant to the optimization/qc intersection",
    "emami-2025-financial-fraud-entropy-computing-qci": "QCi's own CVQBoost/Dirac-3 fraud-detection paper, benchmarked against XGBoost; among the most load-bearing papers for the HSBC consumer project and already cited in ADR-0004's motivating case",
    "loke-2026-cvqboosting-fraud-detection-smu": "Same CVQBoost/Dirac-3 fraud-detection subject as the HSBC consumer project, and the same Loke et al. group ADR-0005 cites for the 0.8108 AUPRC figure; all six authors SMU or NTU affiliated per the byline, none QCi, so F5's affiliation check must read the paper rather than assume from the topic",
    "mancilla-2026-fourier-wall-spectra": "Introduces the SPECTRA certificate for whether and when QML has genuine advantage on tabular data, a central question for this project",
    "pelofske-2022-quantum-volume-nisq-ieee": "Peer-reviewed IEEE benchmarking paper measuring quantum volume on 24 NISQ devices across five vendors",
    "dwave-2021-recruit-case-story": "D-Wave vendor case study (quantum annealing for TV-ad allocation via feature selection); marketing material, not a paper, but it names its classical baselines (L1LR, RFFS); may overlap with the operational-excellence ebook's case studies",
    "dwave-2024-unlocking-power-of-quantum": "D-Wave vendor ebook profiling customer case studies; a compiled superset of the standalone case stories (the SavantX / Port of Los Angeles case appears only here) rather than a duplicate edition; marketing material, not a paper",
    "udaru-2025-qml-credit-risk": "Conceptual review of QML for credit risk (QSVM, QNN, hybrid models) with no experiment or dataset described in its own abstract; VENUE-QUALITY CAVEAT: the journal is an unusual venue for this subject and the printed DOI is unregistered (see evidence), so weigh accordingly",
}

# Why a context moved, beyond the diff itself (appended to updated_reason).
WHY: dict[str, str] = {
    "arute-2019-quantum-supremacy-google-nature": "world dropped: an engineering demonstration of a device is a contested empirical claim, not mathematics/physics ground truth (context test, INTAKE_WORKFLOW.md section 8; F9 and F10 both flagged it)",
    "rand-2022-pqc-critical-infrastructure-assessment": "world dropped: a policy report is not mathematics/physics ground truth (F9, F10)",
    "zajac-2026-inverse-born-rule-equivalence": "world added: a proved Equivalence Theorem, the one theorem in the set (F9, F10)",
    "kerger-2023-mind-the-o-distributed-quantum-algorithms": "world added: proved round complexity is mathematics",
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu": "qml dropped: the abstract names no QNN workload and F10 asked for evidence or drop; restore at read tier if the body shows one. method and platform:braket added from the abstract (benchmarking methodology; AWS SV1 back end)",
    "dupont-2023-quantum-enhanced-greedy-solver": "qml not added: a spin-glass instance is not an ML model (qml-via-workload rule)",
    "wang-2025-quantum-optimization-nn-compression": "qc rationale now carries F10's body-read fact that the larger models ran on a classical Fujitsu Digital Annealer; ml added",
    "lubinski-2023-application-oriented-benchmarks-qedc": "qc rationale no longer lists vendors the abstract does not name (F10: the old list omitted D-Wave on the author list)",
    "rehman-2026-qstar-adaptive-routing": "qml rationale now describes the asymmetric confidence-thresholded fallback the abstract describes (F10)",
    "qci-2024-profiling-cvqboost": "ml added and the rationale carries the abstract's specific, hedged results (F9, F10: the weakest rationale in the CVQBoost cluster)",
    "britt-humble-2017-hpc-with-qpus-acm": "method added for the architecture metrics; the qc rationale now states the two integration pathways (F9's tight/loose taxonomy point)",
    "huynh-2023-quantum-inspired-ml-survey": "ml added: QiML runs in classical frameworks by the paper's own definition; method added for the vocabulary it defines (F9, F10: ml had zero users across the store)",
    "neven-2012-qboost-adiabatic-quantum-optimization": "ml added for the boosting formulation; qc kept because no platform context exists for D-Wave (qc-subsumption rule)",
    "loke-2026-cvqboosting-fraud-detection-smu": "ml added: named classical weak classifiers and baseline",
    "emami-2025-financial-fraud-entropy-computing-qci": "ml added: XGBoost head-to-head",
    "mancilla-2026-fourier-wall-spectra": "method added (SPECTRA is a certificate methodology) and ml added (gradient-boosted trees on the public tabular target) (F9)",
    "dwave-2021-recruit-case-story": "qml and ml added: the case story names weak-classifier selection on the annealer and its classical baselines (evidence read 2026-09-19 contradicted the 'no method' framing)",
    "dwave-2024-unlocking-power-of-quantum": "disposition corrected: the ebook is a superset with a SavantX case absent from the standalone stories (evidence read 2026-09-19)",
    "udaru-2025-qml-credit-risk": "disposition now states the evidentiary type (conceptual review, no experiment in its abstract), not only the venue caveat (evidence read 2026-09-19)",
    "li-2024-photon-counting-raman-spectroscopy": "world kept: an experimental-physics measurement independent of any project",
}


def _current(conn, pid: str) -> list[tuple[str, str]]:
    return [(r[0], r[1]) for r in conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ? ORDER BY context_id", (pid,))]


def apply_changes(conn) -> list[str]:
    ids = [r[0] for r in conn.execute("SELECT id FROM records WHERE class = 'paper' ORDER BY id")]
    missing = sorted(set(ids) - set(APPLICABILITY))
    extra = sorted(set(APPLICABILITY) - set(ids))
    if missing or extra:
        raise SystemExit(f"coverage: papers without a decision {missing}; decisions without a paper {extra}")
    known = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    log = []
    for pid in ids:
        before = _current(conn, pid)
        after = sorted(APPLICABILITY[pid])
        bad = [c for c, _ in after if c not in known]
        if bad:
            raise SystemExit(f"{pid}: unknown context(s) {bad}")
        conn.execute("DELETE FROM paper_applicability WHERE record_id = ?", (pid,))
        for ctx, rationale in after:
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)", (pid, ctx, rationale))
        old_set, new_set = {c for c, _ in before}, {c for c, _ in after}
        diff = ""
        if old_set != new_set:
            diff = f"contexts {sorted(old_set)} -> {sorted(new_set)}"
        if pid in DISPOSITIONS:
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (DISPOSITIONS[pid], pid))
        note = "; ".join(x for x in [diff or "contexts unchanged, every rationale re-anchored to where it was read", WHY.get(pid, ""),
                                     "disposition rewritten" if pid in DISPOSITIONS else ""] if x)
        existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()[0] or ""
        if TAG not in existing:
            # ONE append-only implementation, in store.ingest, executed by a
            # behavioral test. This site used to spell the join itself
            # (PR #30 round-2 audit, 2026-09-23).
            append_updated_reason(conn, pid, f"{TAG}: {note}", TODAY)
        log.append(f"{pid}: {diff or 'same set'}" + (" (disposition)" if pid in DISPOSITIONS else ""))
    return log


# Known exception, printed rather than hidden: the 0-byte seed file this
# record pointed at was removed from Papers/ between Task C (its gate saw
# the file at 1:34pm on 2026-09-19) and Task F (gone by 7:50pm). The record
# has no applicability to re-file; whether to delete it, keep it with a
# note, or replace it with the real repository via intake.py is a
# team-lead question raised at Sprint 4 Manual Validation.
GATE_EXCEPTIONS = {"pere-qml-github-repo-empty": "seed file removed from Papers/ on 2026-09-19; decision at Manual Validation"}


def gate(conn) -> list[str]:
    refusals = []
    rows = conn.execute(
        "SELECT r.id, r.value, r.provenance, r.updated, r.updated_reason, p.tier, p.access, p.disposition, p.evidence, p.mined_by, "
        "p.checked_against_source, (SELECT context_id FROM record_contexts c WHERE c.record_id = r.id LIMIT 1) AS context "
        "FROM records r JOIN paper_fields p ON p.record_id = r.id ORDER BY r.id").fetchall()
    for r in rows:
        origin = "api" if citations.parse_access(r["access"]) else "hand"
        import re
        m = re.search(r"hand-transcribed from ([^)]+)\)", r["provenance"] or "")
        paper = PaperRecord(id=r["id"], tier=r["tier"], access=r["access"], disposition=r["disposition"], context=r["context"] or "",
                            value=r["value"], citation=r["provenance"], citation_origin=origin,
                            hand_transcribed_from=m.group(1) if m else None, evidence=r["evidence"], mined_by=r["mined_by"],
                            checked_against_source=r["checked_against_source"], updated=r["updated"], updated_reason=r["updated_reason"],
                            applicability=_current(conn, r["id"]))
        try:
            validate_paper(paper)
        except ValueError as ex:
            if r["id"] in GATE_EXCEPTIONS:
                print(f"  EXCEPTION {r['id']}: {GATE_EXCEPTIONS[r['id']]} (door said: {str(ex)[:90]})")
                continue
            refusals.append(str(ex))
    return refusals


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        log = apply_changes(conn)
        refusals = gate(conn)
        for line in log:
            print(line)
        counts = dict(conn.execute("SELECT context_id, COUNT(*) FROM paper_applicability GROUP BY context_id ORDER BY context_id").fetchall())
        print(f"\n{len(log)} paper(s) re-filed; applicability rows by context: {counts}; "
              f"door gate (shape rules + applicability anchors; an api row's citation is NOT compared "
              f"against the API here -- that is refresh_citations.py): {len(refusals)} refusal(s)")
        for r in refusals:
            print("  REFUSED", r[:220])
        if refusals or not do_apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; nothing written). Re-run with --apply to commit." if not do_apply else "NOT APPLIED: the gate refused; nothing written.")
            return 0 if not do_apply else 1
        conn.execute("COMMIT")
        print("applied")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
