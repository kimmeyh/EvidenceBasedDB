#!/usr/bin/env python3
"""Sprint 2 Task A (F4 part 1): apply re-derived applicability to all 44
seed-set papers.

Sprint 1 Task F set each paper's single primary `context` but never
populated the separate, plural `paper_applicability` table ADR-0005
section 2d defines (44 of 45 papers had an empty applicability array).
This script applies the results of a background research pass that read
every paper's actual PDF content to determine its real applicability
(and confirmed or flagged its primary context).

Data is defined inline rather than in a JSON file since it is a one-time
correction applied once to existing records, not a repeatable ingestion
path -- Task F's own ingest_seed_set.py remains the ingestion path for
future new papers.

Usage: python scripts/apply_paper_applicability.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

# (paper_id, [(context_id, rationale), ...])
# Sourced from a background research pass that read each paper's actual
# PDF content (2026-09-17). Every context claimed here has a real
# rationale grounded in that reading, not padding for coverage.
APPLICABILITY: dict[str, list[tuple[str, str]]] = {
    "neven-2012-qboost-adiabatic-quantum-optimization": [
        ("qml", "Introduces QBoost, the adiabatic-quantum-optimization boosting algorithm that CVQBoost directly descends from"),
        ("qc", "Uses adiabatic quantum optimization (D-Wave hardware) as the discrete-optimization substrate for classifier training"),
    ],
    "kawchak-2023-coding-tips-cirq-qiskit-pennylane": [
        ("qml", "Coding-tips deck for QML frameworks (Cirq, Qiskit, PennyLane)"),
        ("method", "Tooling/coding-practice reference for QML development, not a research claim"),
    ],
    "qci-2024-unconventional-computing-medium": [
        ("qc", "Explains QCi's own hardware paradigm in general terms"),
        ("platform:dirac-3", "Part of QCi's own 'unconventional hardware' learning module underpinning Dirac-3"),
    ],
    "lubinski-2023-application-oriented-benchmarks-qedc": [
        ("qc", "Cross-platform quantum computing benchmarking suite (gate-based hardware: IonQ, Quantinuum, and others)"),
        ("method", "Establishes a general benchmarking methodology relevant to evaluating quantum claims"),
    ],
    "pelofske-2022-quantum-volume-nisq-ieee": [
        ("qc", "NISQ hardware benchmarking (quantum volume) across multiple vendors"),
    ],
    "bcg-2022-value-of-quantum-benchmarks": [
        ("qc", "Industry/investment commentary on quantum computing benchmarking value"),
    ],
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu": [
        ("qc", "Benchmarks simulators and physical QPUs across multiple vendors on runtime/accuracy/cost"),
        ("qml", "Benchmark workload is quantum neural networks (QNNs), a QML technique"),
    ],
    "bleximo-2020s-applications-and-impact": [
        ("qc", "Vendor slide deck on Bleximo's quantum hardware applications"),
    ],
    "freericks-2026-quantum-mechanics-done-right-book": [
        ("world", "General physics/QM textbook content, independent of any specific project"),
    ],
    # pere-qml-github-repo-empty: file is 0 bytes, no content exists to
    # determine any real applicability. Deliberately left with NO
    # applicability rows rather than guessed from the filename.
    "coleman-2022-guide-to-qc-benchmarking-certification": [
        ("qc", "Trade-press explainer on quantum computing benchmarking and certification tooling"),
    ],
    "britt-humble-2017-hpc-with-qpus-acm": [
        ("qc", "ACM paper on integrating QPUs into HPC system architectures"),
    ],
    "rand-2023-pqc-critical-infrastructure-assessment": [
        ("qc", "Assesses quantum computing's cryptographic threat to critical infrastructure (post-quantum crypto)"),
        ("world", "Policy/national-security framing independent of any specific platform or project"),
    ],
    "rand-2023-pqc-critical-infrastructure-assessment-appendix-b": [
        ("qc", "Companion appendix to the RAND PQC assessment, same subject matter"),
    ],
    "mandra-2021-hybridq-simulator-nasa": [
        ("qc", "Hybrid quantum circuit simulator spanning multiple backend types"),
        ("method", "A simulation-methodology tool relevant to testing quantum circuits without hardware"),
    ],
    "ibm-2023-qiskit-explorer-attendee-guide": [
        ("method", "Pedagogical guidebook for learning Qiskit-based quantum programming"),
        ("qc", "Introductory quantum computing hardware/software content via IBM's own platform"),
    ],
    "loke-2026-cvqboosting-fraud-detection-smu": [
        ("platform:dirac-3", "Confirmed from page 1 keywords: 'Photonic Quantum Processor, Dirac-3'; CVQBoost executed on QCi's Dirac-3"),
        ("qml", "Confirmed from page 1 keywords: 'Quantum Machine Learning (QML), CVQBoost, Quantum Boosting' -- a hybrid QML algorithm"),
    ],
    "mancilla-2026-spectra-datasets-substack": [
        ("qml", "Blog post on constructing datasets for demonstrating QML advantage, same author/topic as the Fourier Wall paper"),
    ],
    "kerger-2023-mind-the-o-distributed-quantum-algorithms": [
        ("qc", "Theoretical paper on quantum distributed computing algorithms"),
    ],
    "wang-2025-quantum-optimization-nn-compression": [
        ("qml", "Applies adiabatic quantum computing (QUBO) to neural network compression, a QML/optimization intersection"),
        ("qc", "Uses quantum annealing hardware directly as the optimization substrate"),
    ],
    "li-2024-photon-counting-raman-spectroscopy": [
        ("world", "General photonics/spectroscopy physics, independent of quantum computing or QML"),
    ],
    "interviewbit-python-cheat-sheet": [
        ("method", "Generic Python reference material, could support any code written in this project"),
    ],
    "emami-2025-financial-fraud-entropy-computing-qci": [
        ("platform:dirac-3", "CVQBoost executed on QCi's own Dirac-3 (Entropy Quantum Computing) hardware; all six authors are QCi employees, confirmed from the arXiv affiliation block"),
        ("qml", "CVQBoost is a hybrid quantum-classical machine-learning boosting algorithm"),
    ],
    "qci-2026-entropy-computing-trade-magazine": [
        ("platform:dirac-3", "Trade-magazine feature specifically on QCi's Entropy Computing/photonic Dirac-3 technology"),
    ],
    "qci-2024-profiling-cvqboost": [
        ("platform:dirac-3", "QCi's own internal profiling document for CVQBoost, which runs on Dirac-3"),
        ("qml", "Covers CVQBoost algorithm performance, a QML method"),
    ],
    "udaru-2025-qml-credit-risk": [
        ("qml", "Reviews QML methods (QSVM, quantum neural networks) applied to credit-risk assessment"),
    ],
    "alonso-2025-qml-fourier-distribution-option-pricing": [
        ("qml", "Uses parametrized quantum circuits and quantum-accelerated Monte Carlo for option-pricing distribution estimation"),
    ],
    "chen-2025-qml-classical-defi": [
        ("qml", "Compares quantum ML models against classical ML in DeFi trading"),
    ],
    "kawchak-2023-qiskit-pennylane-qml-demos": [
        ("qml", "Catalogue of QML demo notebooks (quantum NNs, kernels, GANs, autoencoders)"),
        ("method", "Tooling/coding-practice survey, not a research claim"),
    ],
    "idq-quantis-qrng-pcie-brochure": [
        ("qc", "Quantum random number generator hardware; closest available fit, no context precisely matches QRNG"),
    ],
    "zapata-2025-qc-for-finance-guide": [
        ("qc", "Introductory guide on quantum computing's use in finance generally, not QML-specific"),
    ],
    "dupont-2023-quantum-enhanced-greedy-solver": [
        ("qc", "Quantum-classical hybrid optimization algorithm run on gate-based hardware"),
    ],
    "tung-2026-qmes-quantum-meta-learning-kernel-encoding": [
        ("qml", "Meta-learning package for selecting encoding circuits in quantum kernel methods"),
    ],
    "kawchak-2023-quantum-parameter-study-qml": [
        ("qml", "Parameter study of a quantum-augmented ResNet50 (quantum transfer learning) across three datasets"),
    ],
    "arute-2019-quantum-supremacy-google-nature": [
        ("qc", "Landmark quantum supremacy demonstration on a superconducting processor"),
        ("world", "A foundational, platform-independent scientific milestone referenced broadly beyond any one project"),
    ],
    "huynh-2023-quantum-inspired-ml-survey": [
        ("qml", "Survey specifically distinguishing Quantum-Inspired ML (QiML) from QML methods"),
    ],
    "kawchak-2023-resnet50-quantum-transfer-learning": [
        ("qml", "Cost/efficiency comparison of quantum vs classical transfer learning"),
    ],
    "mancilla-2026-fourier-wall-spectra": [
        ("qml", "Establishes structural conditions under which QML models can or cannot beat classical baselines on tabular data"),
    ],
    "sakhnenko-2026-data-efficient-qml": [
        ("qml", "Studies data-efficiency and generalization of quantum kernel methods vs classical kernels"),
    ],
    "dwave-2023-operational-excellence-ebook": [
        ("qc", "General D-Wave marketing content on quantum annealing for business optimization; no QML-specific content"),
    ],
    "zajac-2026-inverse-born-rule-equivalence": [
        ("qml", "Proves real-valued amplitude encodings in QML collapse to classical quadratic forms -- a QML data-encoding theory result"),
    ],
    "rehman-2026-qstar-adaptive-routing": [
        ("qml", "Quantum transfer learning framework routing between classical and quantum classifier heads"),
    ],
    "dwave-2021-recruit-case-story": [
        ("qc", "D-Wave quantum annealing case study for TV-ad allocation optimization"),
    ],
    "dwave-pattison-food-group-case-story": [
        ("qc", "D-Wave quantum annealing case study for driver-scheduling optimization"),
    ],
    "dwave-2024-unlocking-power-of-quantum": [
        ("qc", "D-Wave marketing ebook profiling the same case studies as the standalone files (compiled/superset edition)"),
    ],
}

# Both judgment calls resolved by the research pass (2026-09-17), recorded
# here rather than silently applied: no schema/data change follows from
# either beyond what APPLICABILITY above already reflects.
#
# 1. dwave-2023-operational-excellence-ebook: NOT reclassified as a book/
#    class-mismatch. Confirmed vendor marketing collateral, same class as
#    the three standalone D-Wave case-story files already in the seed
#    set, not book-class content like Freericks. Its existing seen-tier
#    paper record and qc context stay as-is.
# 2. loke-2026-cvqboosting-fraud-detection-smu: confirmed spans BOTH qml
#    and platform:dirac-3 (already reflected above). Primary context
#    platform:dirac-3 confirmed correct. All six authors confirmed
#    SMU/NTU academic, none QCi-affiliated -- relevant input for F5.


def main() -> int:
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1

    conn = connect(DB_PATH)

    # TWO PASSES: decide everything, THEN write (PR #20 review, 2026-09-19).
    # The F14 version returned exit 1 on a missing or mismatched paper, but
    # only AFTER committing the papers it could apply and regenerating the
    # export -- so "exit 1" did not mean "nothing was written", and a
    # human fixing the typo and re-running then hit the mismatch path for
    # every paper that had landed on pass one. Now pass 1 checks every key
    # against the store with no writes; any problem exits 1 with the store
    # and export/ untouched, so a non-zero exit means exactly "no change".
    missing_papers: list[str] = []
    mismatched_papers: list[str] = []
    to_apply: list[tuple[str, list[tuple[str, str]]]] = []
    already_set = 0

    for paper_id, applicability in APPLICABILITY.items():
        exists = conn.execute(
            "SELECT record_id FROM paper_fields WHERE record_id = ?", (paper_id,)
        ).fetchone()
        if not exists:
            print(f"error: {paper_id} not found in paper_fields", file=sys.stderr)
            missing_papers.append(paper_id)
            continue

        # F14 finding 2 (PR #11 review): a paper already holding ANY row
        # was previously skipped unconditionally, which masks a partial
        # prior run. Compare the existing (context, rationale) PAIRS
        # against the intended ones -- not just the context ids (PR #20
        # review: a changed rationale was silently accepted as "already
        # matching", and ADR-0005 section 2d makes the rationale part of
        # the record). A mismatch is reported, never auto-overwritten.
        existing_pairs = {
            (row["context_id"], row["rationale"])
            for row in conn.execute(
                "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?",
                (paper_id,),
            )
        }
        if existing_pairs:
            intended_pairs = set(applicability)
            if existing_pairs != intended_pairs:
                only_existing = sorted(c for c, _ in existing_pairs - intended_pairs)
                only_intended = sorted(c for c, _ in intended_pairs - existing_pairs)
                print(
                    f"error: {paper_id} applicability differs from APPLICABILITY "
                    f"(contexts or rationales; store-only: {only_existing}, "
                    f"intent-only: {only_intended}) -- mismatch, not touching. A partial "
                    "prior run or a changed intent needs a human decision, not an "
                    "automatic overwrite.",
                    file=sys.stderr,
                )
                mismatched_papers.append(paper_id)
            else:
                already_set += 1
            continue

        to_apply.append((paper_id, applicability))

    if missing_papers or mismatched_papers:
        conn.close()
        print(
            f"error: {len(missing_papers)} paper(s) not found, "
            f"{len(mismatched_papers)} paper(s) had a mismatched applicability set. "
            f"NOTHING was written ({len(to_apply)} paper(s) that could have been applied "
            "were not); store/evidence.db and export/ are unchanged. Fix APPLICABILITY "
            "and re-run.",
            file=sys.stderr,
        )
        return 1

    # Pass 2: write. A constraint failure here names the paper and context
    # (PR #20 review: the F6 finding 3 class, previously unported here) and
    # rolls back the whole run, so store and export/ stay consistent.
    try:
        for paper_id, applicability in to_apply:
            for context_id, rationale in applicability:
                try:
                    conn.execute(
                        "INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                        (paper_id, context_id, rationale),
                    )
                except sqlite3.Error as e:
                    raise RuntimeError(
                        f"failed applying context {context_id!r} to {paper_id!r}: {e}"
                    ) from e
    except RuntimeError:
        conn.rollback()
        conn.close()
        raise

    conn.commit()
    regenerate(conn, EXPORT_DIR)
    conn.close()

    print(
        f"Applied applicability to {len(to_apply)} papers "
        f"({already_set} already had matching applicability set)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
