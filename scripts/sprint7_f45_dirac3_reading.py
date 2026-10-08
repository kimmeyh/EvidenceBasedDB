#!/usr/bin/env python3
"""Sprint 7 Task G (F45): the Dirac-3 reading pass. Seven sources read
directly on 2026-10-08 are promoted to `read` and yield fourteen
assertions: F-201 to F-209, F-301 to F-303 from the 2026-10 handoff's
`07-assertion-candidates-pending.md`, plus the planning note's QCi noise
claims (master plan F45, 2026-10-05).

Every quote was located on its page in the local copy (pdftotext, page by
page) and is checked by `tests/test_f45_dirac3_reading.py`. Where the
second-hand candidate and the source disagree, the assertion states what
the source says and its `certainty_reasons` name the difference
(INTAKE_WORKFLOW.md section 15, assert the table, not the summary):
F-301's "roughly 80 percent" is not in the critique, and F-302's 122% gap
bundles the formulation's share with the device's.

The protein design paper (`emami-2026-...`, DOI only) was read from its
public nature.com article page (one request, 2026-10-08); no copy is
kept. DRY-RUN BY DEFAULT; `--apply` takes a verified backup first.
Idempotent: an existing assertion, link, read or note is skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, add_read, append_updated_reason, insert_assertion, set_tier  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-08"
TAG = "Sprint 7 Task G, F45"
REASON = f"{TODAY} ({TAG}): extracted from a source read directly on {TODAY}"
CTX = "platform:dirac-3"

UG = "ctfassets-2026-dirac-3-user-guide-v0"
N24 = "nguyen-2025-entropy-computing-paradigm-optimization-open"
H25 = "huang-2025-noise-reversal-entropy-quantum-computing"
M26 = "moosavian-2026-critical-comment-entropy-computing-paradigm"
B26 = "ballin-2026-optimal-stratification-sampling-frame-comparative"
PROTEIN = "emami-2026-entropy-quantum-computing-fixed-backbone"
LESSONS = "qci-lessons-entropy-quantum-computing-overview"
FRAUD = "emami-2025-financial-fraud-entropy-computing-qci"    # already `read` (Sprint 4)
SHELL = "qci-research-an-open-quantum-system-for-discrete-optimization"

LOCAL = {
    UG: r"D:\Data\Harold\EvidenceBasedDB\References\2026_QC-2_ctfassets_Dirac-3-User-Guide-v0-0-4.pdf",
    N24: r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2024\Nguyen-et-al._2024_Entropy-Computing-A-Paradigm-for-Optimization-in-Open-Photonic-Systems__2407.04512.pdf",
    H25: r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2025\Huang-Hu_2025_Noise-Reversal-by-Entropy-Quantum-Computing__2502.08591.pdf",
    M26: r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2026\Moosavian-Ravan_2026_A-Critical-Comment-on-Entropy-Computing-A-Paradigm-for-Optimization__2605.03612.pdf",
    B26: r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2026\Ballin-Barcaroli_2026_Optimal-Stratification-of-a-Sampling-Frame-A-Comparative-Study-of__2608.10787.pdf",
    LESSONS: r"D:\Data\Harold\EvidenceBasedDB\References\QCi-site\lessons\entropy-quantum-computing-overview.html",
    FRAUD: r"D:\Data\Harold\EvidenceBasedDB\Papers\QCI - Financial Fraud Detection with Entropy Computing 2503.11273v1.pdf",
}

# (record, applicability rationale -- anchor, checked_against_source, read extent, read detail)
PROMOTIONS = [
    (UG, "QCi's own specification of Dirac-3: variable limits by interaction order, dynamic range, integer "
         "levels, architecture and failure rate -- sections 3 to 5, pp. 11-19",
     f"{TODAY}, Claude, read all 37 pages of the local PDF directly", "full", "all 37 pages"),
    (N24, "The peer-reviewed description of the Dirac-3 hardware: weak coherent states, measurement and feedback, "
          "engineered dissipation -- pp. 3-6 and Supplementary Notes 1 and 4",
     f"{TODAY}, Claude, read pp. 1-6 and 15-16 and Supplementary Notes 1 and 4 (pp. 24-26, 31) directly",
     "partial", "pp. 1-6, 15-16, 24-26, 31"),
    (H25, "QCi's statement of how EQC is meant to work: the quantum Zeno effect and error correction -- p.4",
     f"{TODAY}, Claude, read pp. 1 and 4 directly", "partial", "pp. 1, 4"),
    (M26, "An independent classical reproduction of the Dirac-3 benchmarks in arXiv:2407.04512 -- sections 3 and 7",
     f"{TODAY}, Claude, read all 14 pages and the supplement directly", "full", "all pages and the supplement"),
    (B26, "An independent case study running Dirac-3 on a stratification QUBO against classical solvers -- "
          "abstract, sections 4.7, 6 and 7.3, Appendix B.3",
     f"{TODAY}, Claude, read the abstract (p.1), pp. 15-18, section 7.3 and Appendix B.3 (p.25) directly",
     "partial", "p.1, pp. 15-18, section 7.3, Appendix B.3"),
    (PROTEIN, "A QCi-authored Dirac-3 result on protein design, with its authors' disclosed interests -- "
              "Abstract and Competing interests",
     f"{TODAY}, Claude, read the abstract, author information and competing interests of the nature.com article "
     "page directly (one request; no copy kept)", "partial", "abstract, author information, competing interests"),
    (LESSONS, "QCi's own lesson on what EQC does with loss and noise -- page body",
     f"{TODAY}, Claude, read the saved page's full text (560 words) directly", "full", "whole page"),
]

# record -> the disclosed conflict of interest, ending with its anchor
COI = {
    N24: "All authors hold shares or options in QCi; Y. Huang is named on a related patent -- pp. 15-16, "
         "Competing Interests",
    PROTEIN: "B. E., W. D., D. H., J. R. and L. N. hold shares or options in Quantum Computing Inc. -- "
             "Competing interests section of the nature.com article",
}

NOTES = [
    (FRAUD, f"{TODAY} ({TAG}): p.1 lists all six authors at Quantum Computing Inc (QCi); the paper has no "
            "competing-interests statement, so no coi is recorded. Yields favorable-dirac3-papers-are-qci-authored"),
    (SHELL, f"{TODAY} ({TAG}): the saved page is a 103-word shell (navigation and a Download link, no body text), "
            "so it yields nothing; the paper behind the link was not fetched"),
]


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", CTX)
    return AssertionRecord(**kw)


F205 = "dirac3-mechanism-is-engineered-dissipation-not-zeno"
SEARCH_SCOPE = (f"{TODAY}, Claude: every saved QCi site file under References/QCi-site (545 HTML files), the Dirac-3 "
                "User Guide v0.0.4, arXiv:2407.04512v4, arXiv:2502.08591v1 and arXiv:2503.11273v1, searched for "
                "fault[- ]toleran* and error[- ]correct*. No fault-tolerance claim for Dirac-3 or EQC; the one "
                "'fault-tolerant' (arXiv:2502.08591 p.1) describes gate-based machines. Not searched: QCi press "
                "releases, SEC filings and pages not saved locally")

# (assertion, [yielding records]); the first yields through insert_assertion
ASSERTIONS: list[tuple[AssertionRecord, list[str]]] = [
    (A(id="dirac3-variable-ceiling-falls-with-interaction-order",
       value=("Dirac-3's maximum number of variables, assuming all-to-all connectivity, falls with interaction order: "
              "949 for first and second order, 135 for third, 39 for fourth and 19 for fifth; the 949 headline "
              "figure applies to first and second order only"),
       provenance=f"{UG}, p.12, Table 1 (the quasi-continuous column)",
       citation_context=('"First 949 Second 949 Third 135 Fourth 39 Fifth 19" (p.12, Table 1 rows, read as a '
                         'table); "Maximum Number of Variables 949 (See Table (1) for details)" (p.11)'),
       certainty="moderate",
       certainty_reasons="Started MODERATE: vendor primary documentation of its own device's limits. Not upgraded",
       fidelity="exact", claim_type="vendor-self-claim"), [UG]),
    (A(id="dirac3-analog-resolution-about-200-to-1",
       value=("Dirac-3 struggles to distinguish very small coupling terms: its effective analog resolution is about "
              "200:1 (23 dB), so the largest coefficient may be at most about 200 times the smallest, and two "
              "coefficients must differ by at least the largest divided by 200 to be resolved"),
       provenance=f"{UG}, p.14, section 4.4 Dynamic Range and Solution Quality, equations 5 to 7",
       citation_context=('"it struggles to distinguish very small coupling terms due to its effective analog '
                         'resolution limit, which is approximately 200:1, or 23 dB." (p.14)'),
       certainty="high",
       certainty_reasons=("Started MODERATE: vendor primary documentation. UPGRADED one level for admission against "
                          "interest: a limit of QCi's own product, costly to disclose because it bounds which "
                          "problems the device can represent"),
       fidelity="exact", claim_type="vendor-self-claim"), [UG]),
    (A(id="dirac3-variable-coupling-computed-in-fpga",
       value=("In Dirac-3 the interaction among variables is computed electronically: an FPGA processes the photon "
              "measurements and matrix multiplication emulates the global interaction of each qudit, with the "
              "results fed back into the optical system iteration by iteration"),
       provenance=f"{UG}, p.19, section 5.1 Computing Time",
       citation_context=('"Dirac-3 leverages digital electronics through the utilization of a field-programmable '
                         'gate array (FPGA) to process quantum wavefunction measurements information." (p.19); '
                         '"Matrix multiplication is used to emulate the global interaction of each "qudit," with '
                         'results feeding back into the quantum system and undergoing multiple iterations '
                         'sequentially." (p.19; the typographic quotation marks normalized)'),
       certainty="moderate",
       certainty_reasons=("Started MODERATE: vendor primary documentation of its own architecture. Not upgraded: a "
                          "plain description, not a disclosure against interest. arXiv:2407.04512 p.4 says the same "
                          "(the FPGA computes each time bin's losses, emulating the interaction terms)"),
       fidelity="exact", claim_type="vendor-self-claim"), [UG]),
    (A(id="dirac3-uses-weak-coherent-states-not-fock-states",
       value=("Dirac-3 does not use the photon-number (Fock) states its paradigm is defined on: QCi states that "
              "deterministic photon-number generation is practically difficult and that it uses coherent states with "
              "ultra-low mean photon number instead, keeping about 1% or fewer of pulses above one photon"),
       provenance=f"{N24}, p.4, section 2.1; the User Guide ({UG}) says the same on p.15, section 4.5",
       citation_context=('"While our entropy computing approach implementation is designed for photon number states '
                         'or Fock states, it is practically difficult with the current state-of-the-art in '
                         'deterministic photon number generation [27, 28]. In current hybrid implementation of '
                         'Dirac-3, we use a common approximation of Fock states which is coherent states with '
                         'ultra-low mean photon number µ[29]. Dirac-3 is maintained such that about 1% or less of '
                         'pulses has more than 1 photon." (p.4)'),
       certainty="high",
       certainty_reasons=("Started MODERATE: peer-reviewed (Communications Physics 8:411; the probe's version_of "
                          "10.1038/s42005-025-02324-6). UPGRADED one level for admission against interest: QCi's "
                          "own authors concede the shipped device does not use the states the paradigm is defined "
                          "on, costly to disclose. The independent critique (arXiv:2605.03612 p.1) makes the same "
                          "point"),
       fidelity="exact", claim_type="vendor-self-claim"), [N24, UG]),
    (A(id=F205,
       value=("The peer-reviewed Dirac-3 paper describes its mechanism as engineered dissipation: the target "
              "Hamiltonian is mapped onto an effective dissipative operator; quantum Zeno blockade appears only as "
              "one possible loss medium for an all-optical extension that was not built"),
       provenance=f"{N24}, p.3 (Introduction) and p.25 (Supplementary Note 1, the all-optical extension)",
       citation_context=('"a target Hamiltonian is mapped onto an effective dissipative operator to solve an '
                         'optimization problem in the photon number Hilbert space." (p.3); "This loss medium can be '
                         'implemented via Quantum Zeno blockade where the loss must be stronger than the cavity '
                         'coupling[65–67], or sum frequency generation, promoting dissipation in which the system '
                         'would gradually relax to the effective ground state." (p.25)'),
       certainty="moderate",
       certainty_reasons=("Started MODERATE: peer-reviewed description of the built machine. NOT downgraded for "
                          "the inconsistency with arXiv:2502.08591, which claims the Zeno effect for EQC in general "
                          "(eqc-zeno-mechanism-claimed-huang-2025): that paper describes the paradigm, this one the "
                          "device that exists. The conflict is recorded as a contradicts link"),
       fidelity="exact", claim_type="vendor-self-claim"), [N24]),
    (A(id="dirac3-per-loop-measurement-rules-out-quantum-advantage",
       value=("Dirac-3 detects its photons in every feedback loop and computes the next optical waveform "
              "electronically; QCi's own authors write that this frequent measurement in the computational basis "
              "rules out a quantum advantage for the measurement-and-feedback version"),
       provenance=f"{N24}, p.5 (section 2.1) and p.31 (Supplementary Note 4, Entropy Computing)",
       citation_context=('"The upconverted photons are detected using a high-efficiency, low-dark-count silicon '
                         'single-photon detector (Si-SPD)." (p.5); "While the measurement-and-feedback based '
                         'version could include non-Gaussian statisitics, the frequent measurement in the '
                         'computational basis clearly rules out a quantum advantage." (p.31; the source\'s spelling '
                         '"statisitics" kept)'),
       certainty="high",
       certainty_reasons=("Started MODERATE: peer-reviewed. UPGRADED one level for admission against interest: "
                          "the vendor's own paper concedes its shipped design cannot give a quantum advantage, "
                          "costly to publish"),
       fidelity="exact", claim_type="vendor-self-claim"), [N24]),
    (A(id="dirac3-no-fault-tolerance-claim-in-qci-sources",
       value=("No fault-tolerance claim for Dirac-3 or EQC appears in QCi's primary sources searched; QCi's "
              "specification classifies the device as a \"Hybrid Analog Machine with Quantum Optics and Digital "
              "Electronics\""),
       provenance=f"{UG}, p.11 (the classification), and the search named in search_scope",
       citation_context='"Hybrid Analog Machine with Quantum Optics and Digital Electronics" (p.11, section 3 table)',
       certainty="low",
       certainty_reasons=("Started MODERATE: QCi's own documents. DOWNGRADED one level: an absence claim, only as "
                          "good as its search. The classification itself is a direct quote. Context: fault "
                          "tolerance is a gate-model concept, and QCi's lesson page contrasts EQC with error "
                          "correction rather than claiming it (eqc-presented-as-harnessing-noise-not-correcting-it)"),
       fidelity="exact", claim_type="absence", search_scope=SEARCH_SCOPE), [UG]),
    (A(id="dirac3-returns-suboptimal-answers-at-a-measurable-rate",
       value=("QCi documents that Dirac-3 has some probability of returning a sub-optimal answer even for a simple "
              "problem; its worked example returned the optimum in 23 of 100 trials"),
       provenance=f"{UG}, pp. 17-18, section 4.7 Analog Nature and Figure 2",
       citation_context=('"it is not unusual that even for a simple problem that can be solved in digital computer, '
                         'Dirac-3 will have some probability of returning a sub-optimal answer." (p.17); "Dirac-3 '
                         'returns optimal solution 23% and sub-optimal 77% after 100 trials." (p.18, Figure 2 '
                         'caption)'),
       certainty="high",
       certainty_reasons=("Started MODERATE: vendor primary documentation. UPGRADED one level for admission against "
                          "interest: a failure rate of QCi's own product, costly to disclose"),
       fidelity="exact", claim_type="vendor-self-claim"), [UG]),
    (A(id="dirac3-integer-variables-bounded-0-to-16",
       value=("In Dirac-3's integer solver each variable takes an integer value from 0 to 16; for more than 16 "
              "states QCi recommends the continuous solver, and QUBO is the case of 2 levels per variable"),
       provenance=f"{UG}, p.14, section 4.2 Integer Solver",
       citation_context=('"For problems requiring more than 16 states, the continuous solver is recommended." (p.14); '
                         '"This flexible encoding allows Dirac-3 to support Quadratic Unconstrained Binary '
                         'Optimization (QUBO) by setting the number of levels for each variable to 2." (p.14)'),
       certainty="moderate",
       certainty_reasons=("Started MODERATE: vendor primary documentation. Not upgraded. Cross-check of the total "
                          "level budget (2026-10-08): the User Guide gives no number for it (error 19, p.33, says "
                          "only that the total levels \"exceed limit\"); its 949 is a variable count for first and "
                          "second order (Table 1, p.12). QCi's eqc-direct basic-usage page (References/QCi-site "
                          "package-docs, read directly) states sum of levels <= 954, or 477 binary variables; "
                          "arXiv:2608.10787 Appendix B.3 (p.25) reports a Developer Beginner Guide stating 949. The "
                          "hsbc repository's hardware plan checks levels against 949"),
       fidelity="exact", claim_type="vendor-self-claim"), [UG]),
    (A(id="eqc-zeno-mechanism-claimed-huang-2025",
       value=("A QCi paper with NASA Langley claims that EQC evolves into the least-loss state through rapid "
              "measurements via the quantum Zeno effect"),
       provenance=f"{H25}, p.4",
       citation_context=('"EQC uses "weak coupling" to the environment in a series of rapid measurements, causing '
                         'the system to evolve into the least loss state via the quantum Zeno effect [30, 31]." '
                         '(p.4; the typographic quotation marks normalized)'),
       certainty="low",
       certainty_reasons=("Started LOW: a preprint, and a claim about the paradigm, not a measurement. Not upgraded. "
                          "The peer-reviewed Dirac-3 paper describes engineered dissipation instead and offers "
                          "Zeno blockade only for an unbuilt all-optical extension"),
       fidelity="exact", claim_type="vendor-self-claim", contradicts=[F205]), [H25]),
    (A(id="eqc-presented-as-harnessing-noise-not-correcting-it",
       value=("QCi presents EQC as harnessing loss and noise instead of correcting them, and claims its solution "
              "state mitigates or avoids the need for quantum error correction"),
       provenance=f"{LESSONS}, page body; {H25}, p.4",
       citation_context=('"Instead of trying to avoid loss and noise, we harness them to build quantum machines whose '
                         'capacity and speed could outmatch existing computing modalities." (lesson page body); '
                         '"Once obtained, the solution state will remain in a decoherence-free subspace, thereby '
                         'mitigating or avoiding the requirement for quantum error correction [32]." (arXiv:2502.08591 '
                         'p.4)'),
       certainty="low",
       certainty_reasons=("Started LOW: vendor marketing and a preprint, with no measurement behind the error "
                          "correction claim. Not upgraded. Error correction and fault tolerance are gate-model "
                          "concepts; QCi frames EQC against them rather than meeting them"),
       fidelity="exact", claim_type="vendor-self-claim"), [LESSONS, H25]),
    (A(id="classical-solvers-match-dirac3-published-benchmarks",
       value=("An independent group reproduced the benchmarks of arXiv:2407.04512 on a consumer CPU: Ipopt solved "
              "QPLIB_0018 to optimality in a fraction of a second on one core, and on 30-node Max-k-Cut simulated "
              "annealing and tabu search found the exact maximum in most trials in 0.1 to 0.6 ms, while Dirac-3's "
              "results centered on sub-optimal cuts; they conclude the device behaves like sampling from an effective "
              "Gibbs distribution"),
       provenance=f"{M26}, p.4 (section 3.2), pp. 5-6 (section 3.3, Table 1) and p.11 (section 7)",
       citation_context=('"The solver converged to the known optimal solution in a fraction of a second on a single '
                         'CPU core." (p.4); "Crucially, the heuristic methods (Simulated Annealing and Tabu Search) '
                         'found the exact global maximum in the vast majority of trials, with mean runtimes between '
                         '0.1ms and 0.6ms." (p.6); "we have shown that the observed behavior of the Dirac-3 system is '
                         'consistent with sampling from an effective Gibbs distribution at a problem-dependent '
                         'temperature." (p.11)'),
       certainty="low",
       certainty_reasons=("Started LOW: a preprint, independent of QCi. Not upgraded. Assert the table, not the "
                          "summary (INTAKE_WORKFLOW.md section 15): the second-hand candidate's \"roughly 80 percent "
                          "success for Dirac-3\" on QPLIB_0018 is not in the paper, which says only that Dirac-3 "
                          "needed parameter tuning for a high success probability (p.4); its Dirac-3 Max-k-Cut "
                          "figures are reconstructed from QCi's own Figure 4 on a different graph (p.5, Figure 3), "
                          "with success rates computed assuming the device found the optimum (p.5, Table 1 note); "
                          "the authors asked QCi twice for the graph and got no reply (p.7)"),
       fidelity="exact", claim_type="positive"), [M26]),
    (A(id="dirac3-stratification-falls-short-ballin-2026",
       value=("On a 20-stratum sampling-frame stratification QUBO run on the free tier, Dirac-3's partition needed a "
              "sample size of 286, against 160 for the best-known QUBO solution (a GPU Ising machine) and 129 for a "
              "classical genetic algorithm; on the common objective its energy was 936.61 against the best-known "
              "501.0. The authors find a genuine optimisation that settles well short"),
       provenance=f"{B26}, p.16 (Table 3), pp. 17-18 (section 6.1)",
       citation_context=('"The two runs on real quantum hardware fall much further short: IBM\'s QAOA returns 262 and '
                         'the QCi Dirac-3 returns 286." (p.16; the typographic apostrophe normalized); "The Dirac-3 '
                         'run, by contrast, shows evidence of a non-trivial optimisation process" (p.17); '
                         '"Reevaluating the decoded Dirac-3 partition directly under the identical common one-hot '
                         'objective (same weights, same penalty) used for D-Wave and Amplify AE gives an energy of '
                         '936.61, against the best-known 501.0" (p.18)'),
       certainty="low",
       certainty_reasons=("Started LOW: a preprint, independent (the authors declare no conflicts, p.1), one case "
                          "study that the authors say is not a controlled experiment, under a free-tier 100-variable "
                          "cap. Not upgraded. Assert the table, not the summary (INTAKE_WORKFLOW.md section 15): "
                          "the second-hand \"122 percent gap\" against 129 bundles the formulation's share (the "
                          "best-known QUBO solution already needs 160, about 24%) with the device's (286 against "
                          "160)"),
       fidelity="exact", claim_type="positive"), [B26]),
    (A(id="favorable-dirac3-papers-are-qci-authored",
       value=("Three papers reporting favorable Dirac-3 results are QCi-authored: the fraud detection paper lists all "
              "six authors at QCi; all authors of the Communications Physics paper hold shares or options in QCi; and "
              "the protein design paper has six of seven authors at QCi, five with disclosed shares or options. Its "
              "best-observed solutions are 0.16 to 2.47% from optimal, a near-miss, and the exact classical solver "
              "remains faster in absolute terms"),
       provenance=(f"{FRAUD}, p.1 byline; {N24}, pp. 15-16 Competing Interests; {PROTEIN}, Abstract, Author "
                   "information and Competing interests"),
       citation_context=('fraud paper p.1 byline: each of the six authors at Quantum Computing Inc (QCi); "All '
                         'authors hold shares or options in QCi." (arXiv:2407.04512 pp. 15-16; the page number '
                         'between the pages dropped); "Dirac-3 produces best-observed solutions (over 100 samples per '
                         'instance) within 0.16–2.47% of the optimal energies." (protein paper Abstract); "B. E., '
                         'W. D., D. H., J. R. and L. N. hold shares or options in Quantum Computing Inc." (protein '
                         'paper Competing interests)'),
       certainty="high",
       certainty_reasons=("Started HIGH: each paper's own byline and competing-interests statement, read directly. "
                          "Not downgraded. The coi of each disclosing record is stored on that record"),
       fidelity="exact", claim_type="positive"), [FRAUD, N24, PROTEIN]),
]


def apply_changes(conn) -> list[str]:
    log = []
    for rid, rationale, checked, extent, detail in PROMOTIONS:
        conn.execute("INSERT OR IGNORE INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                     (rid, CTX, rationale))
        if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND reader = 'Claude' AND read_on = ?",
                            (rid, TODAY)).fetchone():
            add_read(conn, rid, "Claude", TODAY, extent, detail)
        if conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] != "read":
            set_tier(conn, rid, "read", checked_against_source=checked)
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read directly and promoted", TODAY)
            log.append(f"read   {rid}")
    for rid, coi in COI.items():
        if conn.execute("SELECT coi FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] is None:
            conn.execute("UPDATE paper_fields SET coi = ? WHERE record_id = ?", (coi, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): disclosed coi recorded", TODAY)
            log.append(f"coi    {rid}")
    for assertion, yielded_by in ASSERTIONS:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (assertion.id,)).fetchone():
            log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, assertion, yielded_by=yielded_by[0])
        for extra in yielded_by[1:]:
            conn.execute("INSERT OR IGNORE INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)",
                         (extra, assertion.id))
        log.append(f"assert {assertion.id} <- {', '.join(yielded_by)} [{assertion.certainty}, {assertion.claim_type}]")
    for rid, note in NOTES:
        prior = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
        if note not in prior:
            append_updated_reason(conn, rid, note, TODAY)
            log.append(f"note   {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    missing = [p for p in LOCAL.values() if not Path(p).exists()]
    if missing:
        print("missing local copies:\n" + "\n".join(missing))
        return 1
    if "--apply" not in args:
        for a, by in ASSERTIONS:
            print(f"assert {a.id} <- {', '.join(by)} [{a.certainty}, {a.claim_type}]")
        print(f"promote {len(PROMOTIONS)}; coi {len(COI)}; notes {len(NOTES)}")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F45 Dirac-3 reading pass")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
