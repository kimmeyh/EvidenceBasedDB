#!/usr/bin/env python3
"""Sprint 8 Task C (F65 with F63): QCi's Dirac-3S User Guide (September
2026, Revision A) read in full on 2026-10-12, its claims entered under the
new context `platform:dirac-3s` (ADR-0004 A8, plan Q3 = 1), and each of the
19 Dirac-3 assertions classed against it; then F63's two admissions from
arXiv:2407.04512, read on pp. 6 and 15.

The two systems stay separate (team lead, Q3: "they should be separate - ok
to list common assertions, facts... that you can confirm"). A Dirac-3S
assertion is linked `supports` to a Dirac-3 assertion only when the WHOLE
Dirac-3 claim is confirmed; a partial match is stated in the text and not
linked (ADR-0004 A8 (b)). No Dirac-3 assertion is edited.

Certainty: vendor documentation starts MODERATE, as in F45. An upgrade for
admission against interest is a Class 2 decision: the candidates are listed
in CANDIDATE_UPGRADES for Manual Validation, and only the ids the team lead
approves, in UPGRADES_APPROVED, are raised (see wanted()).

Every quote was located in the local copy (pdftotext, page by page) and is
checked by `tests/test_f65_dirac3s_reading.py`. DRY-RUN BY DEFAULT;
`--apply` takes a verified backup first. Idempotent: an existing context,
record, link or read is skipped.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, admission_upgrade_reason, append_updated_reason,  # noqa: E402
                          insert_assertion, insert_paper)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-12"
TAG = "Sprint 8 Task C, F65 and F63"
REASON = f"{TODAY} ({TAG}): extracted from a source read directly on {TODAY}"
CTX = "platform:dirac-3s"
CTX_DESCRIPTION = "QCi's Dirac-3S modular optimization system (ADR-0004 A8, 2026-10-12)"

D3S = "qci-2026-dirac-3s-user-guide-rev-a"
UG = "ctfassets-2026-dirac-3-user-guide-v0"
N24 = "nguyen-2025-entropy-computing-paradigm-optimization-open"

D3S_FILE = r"D:\Data\Harold\EvidenceBasedDB\References\QCi-site\systems\Dirac_3S_Users_Guide_Rev_A-1.pdf"
D3S_SHA256 = "0ddbc5339966a42ab67c44988d7a12a599724c462839ecc2848189f048af5971"
D3S_BYTES = 13714215
LOCAL = {
    D3S: D3S_FILE,
    UG: r"D:\Data\Harold\EvidenceBasedDB\References\2026_QC-2_ctfassets_Dirac-3-User-Guide-v0-0-4.pdf",
    N24: r"D:\Data\Harold\EvidenceBasedDB\QMLPapers\2024\Nguyen-et-al._2024_Entropy-Computing-A-Paradigm-for-Optimization-in-Open-Photonic-Systems__2407.04512.pdf",
}

GUIDE_ENTRY = {
    "id": D3S, "kind": "reference", "context": CTX, "tier": "read",
    "title": "Dirac-3S User Guide, September 2026, Revision A",
    "citation": ('Quantum Computing Inc., "Dirac-3S User Guide," September 2026, Revision A, document '
                 'QCi-QMS-900-000001 (hand-transcribed from p.1 and the page header)'),
    "transcribed_from": "p.1 title page and the header line \"QCi-QMS-900-000001 | Rev A\" on every page",
    "disposition": ("Reference: QCi's user guide for the Dirac-3S, a 5U base module with optional expansion modules; "
                    "variable ceilings, solver types, parameters, timing and installation"),
    "access": D3S_FILE,
    "evidence": (f"Local copy provided by the team lead (file dated 2026-10-10); SHA-256 {D3S_SHA256}; "
                 f"{D3S_BYTES:,} bytes; 38 pages; PDF created 2026-09-24. No public URL found on {TODAY}: QCi's "
                 "user-guides page and Dirac-3S product page link no PDF"),
    "found_via": "team lead, 2026-10-10 (F65)",
    "cited_as": "Dirac_3S_Users_Guide_Rev_A-1.pdf",
    "checked_against_source": f"{TODAY}, Claude, read all 38 pages of the local PDF directly",
    "reads": [["Claude", TODAY, "full", "all 38 pages"]],
    "applicability": [[CTX, "QCi's own specification of the Dirac-3S: configurations, variable ceilings, solver "
                            "types, parameters and timing -- sections 1 to 5, pp. 6-24"]],
    "updated_reason": f"{TODAY}: added by scripts/sprint8_f65_dirac3s_reading.py ({TAG}); read in full",
}


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", CTX)
    kw.setdefault("fidelity", "exact")
    return AssertionRecord(**kw)


VENDOR = "Started MODERATE: vendor primary documentation of its own device. Not upgraded"
DOC_FACT = ("Started HIGH: a statement about what the guide itself says, checked directly against the local copy "
            "page by page")
REUSE = "dirac3s-guide-reuses-dirac-3-text-and-figures"
COPIED = (" The passage repeats the Dirac-3 guide's wording and names Dirac-3 (see " + REUSE + "), so the "
          "`supports` link records a vendor restatement, not independent corroboration")
SEARCH_SCOPE = (f"{TODAY}, Claude: the full text of the Dirac-3S User Guide Rev A (all 38 pages, pdftotext), "
                "searched for fault[- ]toleran*, error[- ]correct*, entangle*, Zeno and advantage. The only "
                "'error correction' is the post-processing step in section 4 and Figure 8; no fault-tolerance, "
                "entanglement, Zeno or quantum-advantage claim. Not searched: the two companion documents the "
                "guide names in section 8 (Software Interface Reference, Continuous Solver Benchmarking), which "
                "were not available")

# (assertion, [yielding records]); the first yields through insert_assertion
ASSERTIONS: list[tuple[AssertionRecord, list[str]]] = [
    (A(id="dirac3s-variable-ceiling-by-configuration",
       value=("The Dirac-3S base module (one 5U unit) takes at most 949 variables at second order, 135 at third, 39 "
              "at fourth and 19 at fifth, all-to-all; with one expansion module the ceilings rise to 9,980, 580, "
              "145 and 55. The guide lists no first-order row"),
       provenance=f"{D3S}, p.11, Table 2 (Dirac-3S Hardware Characteristics and Configuration Options)",
       citation_context=('"Max number of variables 2nd 949 9980" (p.11, Table 2 rows, read as a table); "Max number '
                         'of variables 3rd 135 580" (p.11); "Max number of variables 4th 39 145" (p.11); "Max number '
                         'of variables 5th 19 55" (p.11)'),
       certainty="moderate", certainty_reasons=VENDOR + ". The base figures for second to fifth order equal those of "
       "dirac3-variable-ceiling-falls-with-interaction-order; its first-order row has no Dirac-3S counterpart, so "
       "that assertion is confirmed only in part and is not linked (ADR-0004 A8 (b))",
       claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-power-and-size-by-configuration",
       value=("The Dirac-3S base configuration is one 5U rackmount unit drawing 100 W; adding one expansion module adds "
              "a second 5U unit, and the pair draws under 1,500 W"),
       provenance=f"{D3S}, p.11, Table 2 (Power Consumption and Physical Dimensions rows)",
       citation_context='"Power Consumption 100 W" (p.11); "< 1500 W" (p.11, the expansion column)',
       certainty="moderate", certainty_reasons=VENDOR, claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-analog-resolution-about-200-to-1",
       value=("The Dirac-3S guide repeats the Dirac-3 resolution limit: an effective analog resolution of about 200:1 "
              "(23 dB), so the largest coefficient may be at most about 200 times the smallest"),
       provenance=f"{D3S}, p.18, section 5.3 Dynamic Range and Solution Quality",
       citation_context=('"it struggles to distinguish very small coupling terms due to its effective analog '
                         'resolution limit, which is approximately 200:1, or 23 dB." (p.18)'),
       certainty="moderate", certainty_reasons=VENDOR + " here (an admission-against-interest upgrade, as F45 gave "
       "the Dirac-3 assertion, is a Manual Validation decision)." + COPIED, claim_type="vendor-self-claim",
       supports=["dirac3-analog-resolution-about-200-to-1"]), [D3S]),
    (A(id="dirac3s-guide-gives-two-integer-ranges",
       value=("The Dirac-3S guide gives two different ranges for its integer solver: 0 to 15 in Table 1 (p.10) and 0 "
              "to 16 in section 5.1 (p.17), where it also says more than 16 states need the continuous solver; the "
              "guide does not say which holds for the Dirac-3S"),
       provenance=f"{D3S}, p.10 (Table 1) and p.17 (section 5.1)",
       citation_context=('"Integer Solver vi ∈ {0, . . . , 15}" (p.10, Table 1); "vi ∈ N, 0 ≤ vi ≤ 16" (p.17); "For '
                         'problems requiring more than 16 states, the continuous solver is recommended." (p.17)'),
       certainty="high", certainty_reasons=DOC_FACT + ". Section 5.1 restates the whole Dirac-3 assertion (0 to 16), "
       "so it is confirmed in part; Table 1 conflicts, and \"more than 16 states\" fits 0 to 15 (16 states) better "
       "than 0 to 16 (17 states). Not linked until QCi resolves the two figures", claim_type="positive"), [D3S]),
    (A(id="dirac3s-sum-constraint-1-to-10000",
       value=("The Dirac-3S continuous solver keeps the variables non-negative with a fixed sum R between 1 and 10,000; "
              "a larger R spreads the same number of resolution levels more thinly, so precision falls"),
       provenance=f"{D3S}, p.10 (Table 1), p.15 (sum_constraint) and p.17 (section 5.1)",
       citation_context=('"Value must be between 1 and 10000." (p.15); "This behavior reflects a fundamental '
                         'tradeoff: increasing the solution space without increasing resolution granularity reduces '
                         'effective precision." (p.17)'),
       certainty="moderate", certainty_reasons=VENDOR, claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-not-an-exact-solver",
       value=("QCi states that the Dirac-3S is not an exact solver and does not guarantee finding the global optimum: "
              "each run returns samples, and the best sample is the answer"),
       provenance=f"{D3S}, p.12, section 3 How Dirac-3S Computes",
       citation_context=('"Dirac-3S is not an exact solver and does not guarantee discovery of the global optimum." '
                         '(p.12)'),
       certainty="moderate", certainty_reasons=VENDOR + " here (an admission-against-interest candidate for Manual "
       "Validation). Consistent with dirac3-returns-suboptimal-answers-at-a-measurable-rate, but that claim's "
       "23-in-100 rate is a Dirac-3 measurement, so it is not linked", claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-worked-example-is-not-like-for-like",
       value=("The Dirac-3S guide's worked example returns the optimum in 97 of 100 trials, against 23 of 100 in the "
              "Dirac-3 guide v0.0.4, but the two examples are different problems: the x2-squared coefficient is 3.7 "
              "against 4 and the sum constraint 4 against 6; and the Dirac-3S figure names Dirac-3. The pair does not "
              "show that the Dirac-3S returns optimal answers more often"),
       provenance=f"{D3S}, p.21 (section 5.7, equation 7 and Figure 5); {UG}, pp. 17-18 (equation 8 and Figure 2)",
       citation_context=('"subject to a sum constraint x1 + x2 + x3 = 4." (Dirac-3S guide p.21); "Dirac-3 returns '
                         'optimal solution 97% and sub-optimal 3% after 100 trials." (Dirac-3S guide p.21, Figure 5 '
                         'caption); "when running on Dirac-3 with a sum constraint of 6" (Dirac-3 guide p.17); '
                         '"optimal solution 23% and sub-optimal 77% after 100 trials." (Dirac-3 guide p.18, Figure 2 '
                         'caption)'),
       certainty="high", certainty_reasons=DOC_FACT + ", both guides read in full. The Dirac-3 assertion "
       "dirac3-returns-suboptimal-answers-at-a-measurable-rate stands for the Dirac-3", claim_type="positive"),
     [D3S, UG]),
    (A(id="dirac3s-uses-weak-coherent-states",
       value=("The Dirac-3S guide repeats that the hybrid implementation approximates photon-number (Fock) states with "
              "ultra-low-mean-photon-number coherent states, about 1% or less of pulses carrying more than one photon, "
              "and lets the user set the mean photon number between 6.67e-5 and 6.67e-3; its overview (p.6) says "
              "quantum information is represented using photon-number states, which section 5.4 qualifies"),
       provenance=f"{D3S}, p.19, section 5.4 Mean Photon Number and Shot Noise; p.6, section 1.2",
       citation_context=('"In current hybrid implementation of Dirac-3, we use a common approximation of Fock states '
                         'which is coherent states with ultra-low mean photon number" (p.19); "Dirac-3 is maintained '
                         'such that about 1% or less of pulses has more than 1 photon." (p.19); "Users have option to '
                         'modify MPN to search for best parameter for their problems between the range from 6.67" '
                         '(p.19; the range continues "x 10^-5 to 6.67 x 10^-3" in superscript notation); "Quantum '
                         'information is represented using photon-number states across optical modes" (p.6)'),
       certainty="moderate", certainty_reasons=VENDOR + "." + COPIED, claim_type="vendor-self-claim",
       supports=["dirac3-uses-weak-coherent-states-not-fock-states"]), [D3S]),
    (A(id="dirac3s-coupling-computed-in-fpga",
       value=("In the Dirac-3S, as in the Dirac-3, the interaction among variables is computed electronically: an FPGA "
              "processes the photon measurements and matrix multiplication emulates the global interaction, fed back "
              "into the optical system over many sequential iterations"),
       provenance=f"{D3S}, p.23, section 5.8 Understanding Dirac-3S Timing",
       citation_context=('"Dirac-3 leverages digital electronics through the utilization of a field-programmable gate '
                         'array (FPGA) to process quantum wavefunction measurements information." (p.23); "Matrix '
                         'multiplication is used to emulate the global interaction of each "qudit," with results '
                         'feeding back into the quantum system and undergoing multiple iterations sequentially." '
                         '(p.23; the typographic quotation marks normalized)'),
       certainty="moderate", certainty_reasons=VENDOR + "." + COPIED, claim_type="vendor-self-claim",
       supports=["dirac3-variable-coupling-computed-in-fpga"]), [D3S]),
    (A(id="dirac3s-photon-count-is-the-feedback-signal",
       value=("The Dirac-3S guide states that the machine uses the single-photon count of each time bin as its "
              "feedback signal, so every loop measures and feeds back; it does not repeat the quantum-advantage "
              "admission of arXiv:2407.04512"),
       provenance=f"{D3S}, p.19, section 5.4; p.13, Figure 3",
       citation_context=('"uses single photon count of each time-bin as a feedback signal." (p.19); "Quantum '
                         'fluctuations + measurement + digital feedback" (p.13, Figure 3)'),
       certainty="moderate", certainty_reasons=VENDOR + ". Confirms the measurement half of "
       "dirac3-per-loop-measurement-rules-out-quantum-advantage, not its admission, so not linked",
       claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-error-correction-is-a-post-processing-step",
       value=("The Dirac-3S guide's \"error correction\" is a post-processing step on the returned samples: results "
              "come with energy and solution after error correction and raw values before it, and the worked example "
              "turns the raw [2.0005233, 0.0, 1.9994767] into [2.0, 0.0, 2.0]; the guide does not define the step"),
       provenance=f"{D3S}, p.16 (response fields and example) and p.24 (Figure 8)",
       citation_context=('"energy - list of energies for best solution found (float32 precision) for each sample from '
                         'Dirac hardware after error correction" (p.16); "\'raw_solution\': [[2.0005233, 0.0, '
                         '1.9994767]]," (p.16); "\'solution\': [[2.0, 0.0, 2.0]]," (p.16)'),
       certainty="high", certainty_reasons=DOC_FACT, claim_type="positive"), [D3S]),
    (A(id="dirac3s-no-fault-tolerance-claim-in-guide",
       value=("The Dirac-3S guide makes no fault-tolerance, entanglement, quantum Zeno or quantum-advantage claim; it "
              "describes the machine as a hybrid analog system combining quantum optics and digital electronics"),
       provenance=f"{D3S}, p.6, section 1.2, and the search named in search_scope",
       citation_context='"Dirac-3S implements EQC as a hybrid analog system combining quantum optics and digital electronics." (p.6)',
       certainty="low", certainty_reasons=("Started MODERATE: QCi's own document. DOWNGRADED one level: an absence "
                                            "claim, only as good as the search behind it"),
       claim_type="absence", search_scope=SEARCH_SCOPE,
       supports=["dirac3-no-fault-tolerance-claim-in-qci-sources"]), [D3S]),
    (A(id="dirac3s-time-per-sample-by-schedule",
       value=("On a basic 50-variable sum-constraint problem, without pre- and post-processing, QCi gives the average "
              "time per sample as 0.236 s for relaxation schedule 1, 0.420 s for 2, 1.093 s for 3 and 1.278 s for 4"),
       provenance=f"{D3S}, p.23, Table 4",
       citation_context='"Schedule Average time per sample (s) 1 0.236 2 0.420 3 1.093 4 1.278" (p.23, Table 4, read as a table)',
       certainty="moderate", certainty_reasons=VENDOR + ". The section's text names Dirac-3 (see " + REUSE + ")",
       claim_type="vendor-self-claim", units="seconds per sample"), [D3S]),
    (A(id="dirac3s-not-yet-ce-or-fcc-compliant",
       value=("QCi states that the Dirac-3S is still going through CE or FCC emissions certification, and that users "
              "should take precautions and use the device at their own risk"),
       provenance=f"{D3S}, p.5, Warning",
       citation_context=('"This device is undergoing the process to become compliant with CE or FCC emissions '
                         'certification testings." (p.5)'),
       certainty="moderate", certainty_reasons=VENDOR + " here (an admission-against-interest candidate for Manual "
       "Validation)", claim_type="vendor-self-claim"), [D3S]),
    (A(id="dirac3s-on-premises-has-no-100-sample-cap",
       value=("QCi states that an on-premises Dirac-3S is not subject to the 100-sample maximum of its cloud devices; "
              "the guide's own parameter table (Table 3) still gives Number of Samples a range of 1 to 100, so the "
              "guide is inconsistent on the on-premises limit"),
       provenance=f"{D3S}, p.21, section 5.6 Number of Samples; p.18, Table 3",
       citation_context=('"User devices are not subject to the sample maximum of 100 that exists for cloud devices." '
                         '(p.21); "Number of independent solution samples generated per solver exe-" (p.18, Table 3, '
                         'the Number of Samples row; its range column reads 1-100)'),
       certainty="moderate", certainty_reasons=VENDOR, claim_type="vendor-self-claim"), [D3S]),
    (A(id=REUSE,
       value=("Much of the Dirac-3S guide is Dirac-3 text: section 2 is headed \"Dirac-3 at a Glance\", section 4 "
              "\"Writing an Initial Program for Dirac-3\", and the performance passages and figure captions in "
              "section 5 (Figures 4, 5 and 7) name Dirac-3. The guide does not say whether those results were "
              "measured on a Dirac-3S"),
       provenance=f"{D3S}, p.10 (section 2), p.14 (section 4), pp. 20-23 (Figures 4, 5, 7)",
       citation_context=('"2 Dirac-3 at a Glance" (p.10); "4 Quick Start/Writing an Initial Program for Dirac-3" '
                         '(p.14); "runs of Dirac-3 (blue) and gradient descent algorithm (red)." (p.20, Figure 4 '
                         'caption); "Dirac-3 samples more optimal states as we increase the relaxation schedule." '
                         '(p.23, Figure 7 caption)'),
       certainty="high", certainty_reasons=DOC_FACT, claim_type="positive"), [D3S]),
    (A(id="dirac3s-expansion-modules-scale-problem-size",
       value=("QCi presents the Dirac-3S as modular: expansion modules connect to the base module to raise problem "
              "size and, it says, speed, and the machine is meant as an accelerator inside existing CPU and GPU "
              "workflows rather than a replacement; the speed claim is not quantified in the guide"),
       provenance=f"{D3S}, p.9 (section 1.5) and p.7 (section 1.4)",
       citation_context=('"Multiple Expansion Modules can be incorporated within a single Dirac-3S installation to '
                         'support larger optimization problem sizes and faster speed." (p.9); "Dirac-3S is not '
                         'intended to replace the user\'s existing computing infrastructure." (p.7; the typographic '
                         'apostrophe normalized)'),
       certainty="low", certainty_reasons=("Started LOW: a vendor capability statement with no measurement behind the "
                                            "speed claim. Not upgraded"), claim_type="vendor-self-claim"), [D3S]),
    # F63: two admissions by QCi's own authors in arXiv:2407.04512 (context platform:dirac-3)
    (A(id="dirac3-does-not-use-entanglement",
       context="platform:dirac-3",
       value=("QCi's own authors state that the current Dirac-3 hybrid implementation does not use quantum "
              "entanglement; they attribute its speed to relaxation and fast optical propagation, and its escape from "
              "local minima to the intrinsic randomness of quantum fluctuations"),
       provenance=f"{N24}, p.15 (Discussion)",
       citation_context=('"The speed of our approach comes from relaxation mechanism as well as the fast propagation '
                         'and processing of information within light." (p.15); "Our current Dirac-3 hybrid '
                         'implementation does not utilize quantum entanglement." (p.15)'),
       certainty="moderate",
       certainty_reasons=("Started MODERATE: peer-reviewed (Communications Physics 8:411), QCi-authored. Not upgraded "
                          "here: an admission-against-interest upgrade (a vendor limiting what its product can claim "
                          "to be) is a Manual Validation decision"),
       claim_type="vendor-self-claim", supports=["dirac3-per-loop-measurement-rules-out-quantum-advantage"]), [N24]),
    (A(id="dirac3-optics-could-be-classically-simulated",
       context="platform:dirac-3",
       value=("QCi's own authors write that Dirac-3's optical parts involve no large-scale non-Gaussian quantum "
              "superpositions and so could in principle be classically simulated, as argued for coherent Ising "
              "machines"),
       provenance=f"{N24}, p.6 (section 2.1)",
       citation_context=('"It is worth noting that since the optical parts of the system do not involve large scale '
                         'non-Gaussian quantum superpositions, they could in principle be instead classically '
                         'simulated, as has been argued in the coherent Ising machine setting" (p.6)'),
       certainty="moderate",
       certainty_reasons=("Started MODERATE: peer-reviewed, QCi-authored. Not upgraded here: an admission-against-"
                          "interest upgrade is a Manual Validation decision"),
       claim_type="vendor-self-claim", supports=["dirac3-per-loop-measurement-rules-out-quantum-advantage"]), [N24]),
]

# Every platform:dirac-3 assertion present before this task, classed against the Dirac-3S guide.
CLASSED = {
    "dirac3-analog-resolution-about-200-to-1": ("confirmed", "dirac3s-analog-resolution-about-200-to-1"),
    "dirac3-uses-weak-coherent-states-not-fock-states": ("confirmed", "dirac3s-uses-weak-coherent-states"),
    "dirac3-variable-coupling-computed-in-fpga": ("confirmed", "dirac3s-coupling-computed-in-fpga"),
    "dirac3-no-fault-tolerance-claim-in-qci-sources": ("confirmed", "dirac3s-no-fault-tolerance-claim-in-guide"),
    "dirac3-variable-ceiling-falls-with-interaction-order": ("confirmed in part", "dirac3s-variable-ceiling-by-configuration"),
    "dirac3-integer-variables-bounded-0-to-16": ("confirmed in part", "dirac3s-guide-gives-two-integer-ranges"),
    "dirac3-returns-suboptimal-answers-at-a-measurable-rate": ("confirmed in part", "dirac3s-worked-example-is-not-like-for-like"),
    "dirac3-per-loop-measurement-rules-out-quantum-advantage": ("confirmed in part", "dirac3s-photon-count-is-the-feedback-signal"),
    "eqc-presented-as-harnessing-noise-not-correcting-it": ("confirmed in part", None),
    "dirac3-mechanism-is-engineered-dissipation-not-zeno": ("not addressed", None),
    "eqc-zeno-mechanism-claimed-huang-2025": ("not addressed", None),
    "classical-solvers-match-dirac3-published-benchmarks": ("not addressed", None),
    "cvqboost-vs-xgboost-training-time-dirac3": ("not addressed", None),
    "dirac3-fidelity-test-is-near-trivial-on-convex-formulation": ("not addressed", None),
    "dirac3-integer-cost-per-level-line-falsified": ("not addressed", None),
    "dirac3-integer-cost-tracks-variables-not-levels": ("not addressed", None),
    "dirac3-matches-exact-optimum-on-convex-cvqboost": ("not addressed", None),
    "dirac3-stratification-falls-short-ballin-2026": ("not addressed", None),
    "favorable-dirac3-papers-are-qci-authored": ("not addressed", None),
    # Added 2026-10-15 (Sprint 9 Task A, F79): Phase 2's B4 and B5 hardware
    # runs, which the Dirac-3S guide does not address.
    "dirac3-matches-classical-proxy-in-pocket-spectra-b4": ("not addressed", None),
    "cvqboost-in-segment-edge-negative-on-device-spectra-b4": ("not addressed", None),
    "qsvm-on-dirac3-weak-on-ulb-b5": ("not addressed", None),
    # Added 2026-10-15 (Sprint 9 Task G, F80): the slice's QCi pages, packages
    # and the postquantum article, classed against the guide's text. The guide
    # gives the device 2nd to 5th order (not the package), a sum constraint R
    # of 1 to 10,000, eqc-direct on Python 3.8 to 3.10 (p.33), and per-sample
    # times of 1.093 s for schedule 3 against 1.278 s for 4 on its own problem.
    "eqc-models-dirac3-sum-constraint": ("confirmed in part", "dirac3s-sum-constraint-1-to-10000"),
    "eqc-models-polynomial-fifth-order": ("confirmed in part", "dirac3s-variable-ceiling-by-configuration"),
    "dirac3-portfolio-relaxation-schedule-3-vs-4": ("confirmed in part", "dirac3s-time-per-sample-by-schedule"),
    "eqc-models-direct-solver-python-limit": ("confirmed in part", None),
    "eqc-models-dirac3-cloud-solvers": ("not addressed", None),
    "eqc-direct-package-v2-0-2": ("not addressed", None),
    "qci-client-package-v5-0-0": ("not addressed", None),
    "dirac3-portfolio-255-monthly-problems-21y": ("not addressed", None),
    "dirac3-portfolio-outperforms-ndx-vendor-claim": ("not addressed", None),
    "dirac3-portfolio-vs-localsolver-energies-similar": ("not addressed", None),
    "dirac3-qap-5x5-found-optimum": ("not addressed", None),
    "dirac3-qap-spread-optimal-to-166pct": ("not addressed", None),
    "qci-fraud-qboost-vs-xgboost-table": ("not addressed", None),
    "qci-fraud-qboost-speed-power-claim": ("not addressed", None),
    "postquantum-qubit-counts-are-variables": ("not addressed", None),
    "postquantum-no-independent-advantage-2025": ("not addressed", None),
    "postquantum-eqc-heuristic-view": ("not addressed", None),
}

# Admission-against-interest candidates, for the team lead at Manual
# Validation (Class 2): id -> why the statement costs QCi something.
CANDIDATE_UPGRADES = {
    "dirac3-does-not-use-entanglement": ("QCi gives up an entanglement claim for Dirac-3 (the source says "
                                         "\"Our current Dirac-3 hybrid implementation\", p.15; it says nothing of "
                                         "Dirac-3S or QCi's other products)"),
    "dirac3-optics-could-be-classically-simulated": ("QCi concedes that Dirac-3's optical parts could in principle be "
                                                     "classically simulated (arXiv:2407.04512, p.6, on Dirac-3 only)"),
    "dirac3s-analog-resolution-about-200-to-1": ("a limit of QCi's own product that bounds which problems the device "
                                                 "can represent (F45 upgraded the Dirac-3 statement the same way)"),
    "dirac3s-not-an-exact-solver": "QCi disclaims any guarantee that the device finds the optimum",
    "dirac3s-not-yet-ce-or-fcc-compliant": "QCi admits a regulatory gap that limits where the device can be deployed",
}
# The candidates the team lead approved (Q7, 2026-10-13: "all 5", once the
# entanglement statement named its product). apply_changes raises each one
# moderate -> high, and the sync keeps it there (it compares certainty too).
UPGRADES_APPROVED: set[str] = set(CANDIDATE_UPGRADES)
UPGRADE_DECISION = "the team lead's decision at Sprint 8 Manual Validation (Q7), 2026-10-13"
UPGRADE_NOTE = f"2026-10-13 ({TAG}): certainty UPGRADED moderate -> high for admission against interest, {UPGRADE_DECISION}"


def wanted(assertion: AssertionRecord) -> tuple[str, str]:
    """(certainty, certainty_reasons) the store should hold: as entered,
    or one level up where the team lead approved the upgrade."""
    if assertion.id not in UPGRADES_APPROVED:
        return assertion.certainty, assertion.certainty_reasons
    if assertion.certainty != "moderate":
        raise ValueError(f"{assertion.id}: an upgrade starts from moderate, not {assertion.certainty}")
    return "high", admission_upgrade_reason(assertion.certainty_reasons, CANDIDATE_UPGRADES[assertion.id],
                                            UPGRADE_DECISION)

N24_READ = ("Claude", TODAY, "partial", "pp. 6 and 15 re-read for F63")
REVIEW_NOTE = (f"{TODAY} ({TAG}, fresh-eyes review): value, quotes or certainty reasons corrected to say only what "
               "the quoted text supports")


def sha256_of(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def apply_changes(conn) -> list[str]:
    log = []
    if conn.execute("SELECT 1 FROM contexts WHERE id = ?", (CTX,)).fetchone() is None:
        conn.execute("INSERT INTO contexts (id, description) VALUES (?, ?)", (CTX, CTX_DESCRIPTION))
        log.append(f"context {CTX}")
    if conn.execute("SELECT 1 FROM records WHERE id = ?", (D3S,)).fetchone() is None:
        insert_paper(conn, intake.build_record(GUIDE_ENTRY, today=TODAY))
        log.append(f"paper  {D3S} [read]")
    if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND read_on = ? AND detail = ?",
                        (N24, TODAY, N24_READ[3])).fetchone():
        add_read(conn, N24, *N24_READ)
        append_updated_reason(conn, N24, f"{TODAY} ({TAG}): pp. 6 and 15 re-read; yields "
                              "dirac3-does-not-use-entanglement and dirac3-optics-could-be-classically-simulated",
                              TODAY)
        log.append(f"read   {N24}")
    if conn.execute("SELECT description FROM contexts WHERE id = ?", (CTX,)).fetchone()[0] != CTX_DESCRIPTION:
        conn.execute("UPDATE contexts SET description = ? WHERE id = ?", (CTX_DESCRIPTION, CTX))
        log.append(f"context {CTX} description corrected")
    for assertion, yielded_by in ASSERTIONS:
        certainty, reasons = wanted(assertion)
        stored = conn.execute(
            "SELECT r.value, f.citation_context, r.certainty_reasons, r.certainty FROM records r "
            "JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (assertion.id,)).fetchone()
        if stored:
            want = (assertion.value, assertion.citation_context, reasons, certainty)
            if tuple(stored) != want:
                # The fresh-eyes review of Task C (2026-10-12) corrected
                # wording entered earlier the same day, and Manual
                # Validation (2026-10-13) decided the upgrades; the
                # appended reason says which.
                upgraded = stored[3] == "moderate" and certainty == "high"
                conn.execute("UPDATE records SET value = ?, certainty = ?, certainty_reasons = ? WHERE id = ?",
                             (assertion.value, certainty, reasons, assertion.id))
                conn.execute("UPDATE assertion_fields SET citation_context = ? WHERE record_id = ?",
                             (assertion.citation_context, assertion.id))
                append_updated_reason(conn, assertion.id, UPGRADE_NOTE if upgraded else REVIEW_NOTE,
                                      "2026-10-13" if upgraded else TODAY)
                log.append(f"{'upgrade' if upgraded else 'fixed  '} {assertion.id} [{certainty}]")
            else:
                log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, replace(assertion, certainty=certainty, certainty_reasons=reasons),
                         yielded_by=yielded_by[0])
        for extra in yielded_by[1:]:
            conn.execute("INSERT OR IGNORE INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)",
                         (extra, assertion.id))
        log.append(f"assert {assertion.id} <- {', '.join(yielded_by)} [{certainty}, {assertion.claim_type}]")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    missing = [p for p in LOCAL.values() if not Path(p).exists()]
    if missing:
        print("missing local copies:\n" + "\n".join(missing))
        return 1
    if sha256_of(D3S_FILE) != D3S_SHA256:
        print(f"{D3S_FILE} differs from the copy read on {TODAY} (SHA-256)")
        return 1
    if "--apply" not in args:
        intake.build_record(GUIDE_ENTRY, today=TODAY)  # validates the entry; nothing written
        for a, by in ASSERTIONS:
            print(f"assert {a.id} <- {', '.join(by)} [{a.certainty}, {a.claim_type}]")
        for rid, (cls, by) in CLASSED.items():
            print(f"class  {rid}: {cls}" + (f" ({by})" if by else ""))
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F65 Dirac-3S guide and F63 admissions")
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
