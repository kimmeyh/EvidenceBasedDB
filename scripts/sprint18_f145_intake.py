#!/usr/bin/env python3
"""Sprint 18 Task E (F145): qubit-lab.ch's Evidence page and its machine-readable run file, entered as one source
record and its stated results. INTAKE_WORKFLOW.md section 80.

qubit-lab.ch is a Swiss firm selling a platform (the "RQP" products) whose runs this page reports, so every result
is a vendor's claim about its own product: `vendor-self-claim`, graded LOW with the store's one fixed vendor reason
(`store.grading.low_grade("vendor claim")`). Its conflict of interest is named in the record's disposition, and each
value carries its own scope (simulator or device, data, one run).

Read in full, 2026-11-21: the saved page (about 83,000 characters of text) and `/evidence-runs.json` (13 run
records). The page also links public study PDFs, briefs and the QMC run's result files; the plan's scope is the page
and the run file, so these are listed in section 80, not read. Gated material ("on request", the Resource Room) is
listed and never requested.

Every quote is checked by `require_verbatim`, with the value's figures, against the saved page before anything is
written; written only through the verified write path. No assertion relation is written: ADR-0004 A8 (b) links
`supports` only when the whole claim is confirmed, and section 80 names each candidate pair with its reason.

A record already in the store is compared with this script's version: for an assertion, every column it writes and
its context; for the source, its tier, access, disposition, evidence and applicability. The same is skipped
("exists"). A difference in a field that `DECIDED` names for that record is a reviewed correction, written through
`store.ingest.sync_decided_assertion` ("correct"); any other difference stops the run before anything is written
("DIFFERS").

    python scripts/sprint18_f145_intake.py            # dry run
    python scripts/sprint18_f145_intake.py --apply    # verified backup first; a second apply writes nothing
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import low_grade  # noqa: E402
from store.common_names import with_common_names  # noqa: E402
from store.ingest import (AssertionRecord, insert_paper, insert_verified_assertion,  # noqa: E402
                          sync_decided_assertion, validate_assertion)
from store.quotes import require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-11-21"
TAG = "Sprint 18 Task E, F145"
COPY_DIR = Path(r"D:\Data\Harold\EvidenceBasedDB\References\qubit-lab_evidence_2026-11-21")
PAGE_URL = "https://qubit-lab.ch/evidence"
RUNS_URL = "https://qubit-lab.ch/evidence-runs.json"
PAGE = COPY_DIR / "evidence.html"
RUNS = COPY_DIR / "evidence-runs.json"
SOURCE_ID = "qubit-lab-2026-evidence-method-studies-published-runs"
FOUND_VIA = ("the team lead, 2026-11-07, Sprint 17 planning: \"add to backlog for next sprint - what can we learn "
             "from this site: https://qubit-lab.ch/evidence#qmc-correlation-0 about Quantum Computing\"")
REASON = f"{TODAY} ({TAG}): extracted from the saved page, read in full on {TODAY}"
LOW_VENDOR = low_grade("vendor claim")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry() -> dict:
    return {
        "id": SOURCE_ID, "kind": "reference", "context": "qml", "tier": "read",
        "title": "Evidence, not promises: published runs and method studies",
        "citation": (f"qubit-lab.ch, \"Evidence, not promises: published runs and method studies,\" web page, "
                     f"{PAGE_URL}, read 2026-11-21, with its run file {RUNS_URL} (version 1.0, 13 records) "
                     "(hand-transcribed from the page's heading and subtitle; the page carries no single date: its "
                     "latest entry is dated 20 Nov 2026)"),
        "transcribed_from": "the page's \"Evidence, not promises\" heading and its subtitle; the run file's version",
        "access": f"{PAGE} | {RUNS} | {PAGE_URL} | {RUNS_URL}",
        "disposition": ("Reference: a vendor's own evidence page. qubit-lab.ch sells the RQP platform whose runs and "
                        "method studies it reports (conflict of interest: every result is about its own product, "
                        "on its own site, not peer reviewed). 7 method studies and 5 sample runs (6 run records), "
                        "each with a printed verdict from a controlled vocabulary and a machine-readable record. "
                        "Study PDFs, briefs and the QMC result files are public and not yet read; sample reports and "
                        "raw results are gated (Resource Room, on request) and not requested"),
        "evidence": (f"Local copy {PAGE.name}, SHA-256 {sha(PAGE)}, saved {TODAY}; local copy {RUNS.name}, "
                     f"SHA-256 {sha(RUNS)}, saved {TODAY}; fetched once each with the UA "
                     "EvidenceBasedDB-fetcher/1.0"),
        "applicability": [
            ["qml", "a vendor's quantum kernel and variational classifier studies and runs, on synthetic, demo and "
                    "public credit data, each with its printed verdict -- read in full"],
            ["qc", "a vendor's QAOA and amplitude-estimation runs and studies, one on IBM hardware -- read in full"],
            ["method", "how the vendor makes its studies: designs locked before the first run, numbers reproduced "
                       "by a committed script, corrections disclosed, a controlled verdict vocabulary -- read in "
                       "full"]],
        "found_via": FOUND_VIA, "cited_as": PAGE_URL,
        "checked_against_source": f"{TODAY}, Claude, read the whole saved page and run file",
        "reads": [["Claude", TODAY, "full", "the whole saved page and the run file"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint18_f145_intake.py ({TAG}); read in full",
    }


def A(**kw) -> AssertionRecord:
    if "certainty" in kw or "certainty_reasons" in kw:
        raise ValueError(f"{kw.get('id')}: every F145 grade is the store's fixed vendor LOW; its scope is in the value")
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "vendor-self-claim")
    kw["certainty"], kw["certainty_reasons"] = LOW_VENDOR
    kw["provenance"] = f"{SOURCE_ID}, {kw['provenance']}"
    kw["citation_context"] = "; ".join(f'"{q}" ({kw["provenance"].split(", ", 1)[1]})' for q in kw.pop("quotes"))
    return AssertionRecord(**kw)


ASSERTIONS: list[AssertionRecord] = [
    A(id="qubit-lab-qaoa-concentration-study-ql-st-001", context="qc",
      value=("qubit-lab.ch reports, over 12,397 certified QAOA runs on 24 instances (20 synthetic dense Markowitz "
             "at 12 qubits and 4 real demo books at 7-16 qubits), in exact statevector simulation only: the budget "
             "penalty ratio, not the ansatz, is the biggest lever on concentration (Spearman -0.91, 95% CI -0.95 to "
             "-0.80, CVaR training); a right classical seed puts the optimum on top on 100% of runs, while on the "
             "real books a wrong seed never escaped, at any depth or budget: 0 of 96 (below 3.1% at 95% "
             "confidence); and on the real books, n = 12 per distance, the adaptive ansatz escapes a wrong seed "
             "83/75/50% of the time at 1/2/3 assets off"),
      provenance="Study 1 of 7, run record QL-ST-001",
      quotes=["24 instances: 20 synthetic dense Markowitz at 12 qubits + 4 real demo books at 7–16 qubits · 12,397 "
              "certified runs",
              "Wrong seed on real books: never escaped, at any depth or budget",
              "Penalty ratio vs concentration: Spearman −0.91 (CVaR; 95% CI −0.95 to −0.80)",
              "The biggest lever is the problem's budget penalty, not the ansatz",
              "classical seed: right seed 100% of runs, wrong seed 0 of 96 (below 3.1% at 95% confidence)",
              "adaptive ansatz escapes a wrong seed 83/75/50% (1/2/3 assets off, real books, n = 12 per distance",
              "Exact statevector simulation only — no hardware"]),
    A(id="qubit-lab-qaoa-noise-ladder-ibm-kingston-ql-st-002", context="qc",
      value=("qubit-lab.ch reports trained QAOA circuits on a real 14-qubit portfolio book replayed on ibm_kingston "
             "(IBM Heron r2, 156 qubits, 20,000 shots per circuit, raw, no error mitigation): routing onto the "
             "heavy-hex lattice multiplied two-qubit gates by about 2.5 (182 to 440 at p = 1, 2,190 to 5,454 for "
             "the adaptive circuit); only p = 1 kept structure (seed peak 8.5% to 0.8%) and p of 3 or more read "
             "out statistically uniform; the adaptive circuit, 10.08% on the optimum in exact simulation, had 0 "
             "hits in 20,000 on the device; and a simulation built from the device's calibration was optimistic "
             "by 2.6 to 3.5 times. One book, one day, one backend"),
      provenance="Study 2 of 7, run record QL-ST-002",
      quotes=["ibm_kingston (IBM Heron r2, 156 qubits), 20,000 shots per circuit, raw (no error mitigation)",
              "Real 14-qubit demo book (16,384 states)",
              "routing onto the heavy-hex lattice multiplied two-qubit gates by ~2.5",
              "182 → 440 at p = 1, 2,190 → 5,454 for the adaptive circuit",
              "device: only p = 1 retains structure (seed peak 8.5% → 0.8%), p ≥ 3 statistically uniform, adaptive 0 "
              "hits in 20,000 (below 0.015% at 95% confidence)",
              "adaptive circuit (10.08% exact, modal)",
              "calibration-based prediction optimistic ×2.6–3.5 (shot-noise intervals stay above ×2.3)",
              "One book, one day, one backend, raw and unmitigated — the study says so."]),
    A(id="qubit-lab-qsvm-advantage-island-ql-st-003", context="qml",
      value=("qubit-lab.ch reports that on labels generated by the same fidelity kernel the classifier uses (a "
             "best case, stated as such), a quantum kernel classifier beat ten threshold-tuned classical variants "
             "in 94% or more of arms at every size up to 12 qubits, at 512 shots as at exact simulation, eroding at "
             "14-16 qubits; with classical low-order structure in the labels it won 0 times on pure low-order "
             "labels and began to win only at 75% quantum-native mixing; and its own screening checklist vetoed 83 "
             "of 84 winning datasets. Simulation only, one feature-map family"),
      provenance="Study 3 of 7, run record QL-ST-003",
      quotes=["Quantum-native by construction — generated by the same fidelity kernel the classifier uses",
              "Ten variants, each threshold-tuned",
              "Wins in ≥94% of arms at every size up to 12 qubits — at 512 shots as at exact simulation; erosion at "
              "14–16 qubits",
              "classical wall located: 0 wins on pure low-order labels, wins begin at 75% quantum-native mixing",
              "own screening checklist vetoed 83 of 84 winning datasets",
              "exact or binomially shot-sampled simulation, no hardware runs · one feature-map family (zz-like, 2 "
              "repeats)"]),
    A(id="qubit-lab-vqc-island-ql-st-004", context="qml",
      value=("qubit-lab.ch reports that on labels built to favour the variational classifier, its score relative "
             "to the quantum kernel classifier on identical rows rose monotonically from 0.98 to 1.18 across 4-16 "
             "qubits (the kernel method perfect at 4 qubits, the VQC ahead from 12); no trainability wall appeared "
             "through 16 qubits (initial gradient norms flat at 0.055-0.092); and 512-shot inference moved F1 by a "
             "median of -0.004. Exact-statevector training, one shallow local-cost ansatz family"),
      provenance="Study 4 of 7, run record QL-ST-004",
      quotes=["Native families are best-case envelopes per method",
              "paired VQC/QSVM 0.98 → 1.18 across 4–16 qubits on VQC-native labels (QSVM perfect at 4 qubits, VQC "
              "ahead from 12)",
              "no trainability wall observed through 16 qubits (init gradients flat 0.055–0.092; best native score AT "
              "16 qubits)",
              "512-shot inference noise negligible (median ΔF1 −0.004 with the exact-trained threshold held fixed)",
              "Exact-statevector training (training under shots: registered future work) · one shallow local-cost "
              "ansatz family"]),
    A(id="qubit-lab-kernel-configuration-atlas-ql-st-005", context="qml",
      value=("qubit-lab.ch reports, over its quantum kernel product's settings: 100% / 86% / 33% / 25% of "
             "configurations measurable at 512 shots at 4 / 8 / 12 / 16 qubits (36% at 32,768 shots at 16q); one "
             "offered setting, the angle map with rotation Z, encodes nothing (kernel identically 1 in all 1,440 "
             "cells); and of 150 refereed configurations 4 met the win rule at exact simulation, all angle maps, "
             "and 0 once their exact classical twin joined the referee. The design was deposited with Zenodo (DOI "
             "10.5281/zenodo.22498143) before the first run"),
      provenance="Study 5 of 7, run record QL-ST-005",
      quotes=["Measurable at 512 shots: 100% / 86% / 33% / 25% of configurations at 4 / 8 / 12 / 16 qubits (36% at "
              "32,768 shots at 16q)",
              "the angle map with rotation Z encodes nothing: kernel identically 1 in all 1,440 cells",
              "of 150 refereed configurations 4 met the win rule at exact simulation — all angle maps, 0 once their "
              "exact classical twin joins the referee",
              "deposited with Zenodo (DOI 10.5281/zenodo.22498143) before the first run"]),
    A(id="qubit-lab-vqc-configuration-atlas-ql-st-006", context="qml",
      value=("qubit-lab.ch reports, over its variational classifier's settings: with a local measurement and the "
             "product's default initialization, 86% of configurations screen as trainable at 16 qubits; the global "
             "parity measurement halves its gradient per qubit, and 0 of 22 refereed runs with it won; 9 of 80 "
             "refereed trainings won, while 0 of 18 configurations that screened as concentrated won or reached "
             "kernel parity, against 11 of 42 that screened as trainable; the graded gradient reading predicts "
             "refereed outcomes with AUC 0.88; eight of eleven registered hypotheses fell. Exact simulation, no "
             "hardware"),
      provenance="Study 6 of 7, run record QL-ST-006",
      quotes=["With a local measurement and the product's default initialization 86% of configurations screen as "
              "trainable at 16 qubits",
              "the global parity measurement halves its gradient per qubit under every initialization; 0 of 22 "
              "refereed runs with it won",
              "9 wins of 80; 0 of 18 concentrated configurations won or reached kernel parity, 11 of 42 trainable "
              "ones did",
              "the graded gradient reading predicts refereed outcomes with AUC 0.88",
              "Eight of eleven registered hypotheses fell",
              "Exact simulation, no shot noise in training, no hardware"]),
    A(id="qubit-lab-qml-sensitivity-map-credit-ql-st-009", context="qml",
      value=("qubit-lab.ch reports, from 360 trainings of its variational classifier on German Credit, Taiwan "
             "credit default, an internal dataset and a synthetic control, in exact simulation: input scaling moves "
             "the test score by 16.4 points on German Credit and 12.7 on Taiwan, above the noise level (12.1 and "
             "6.1, registered as the 80th percentile of the differences between two random starts); no circuit with "
             "more two-qubit gates beats the 14-gate default beyond the noise level; and the best of 27 "
             "hand-searched configurations against logistic regression is on par on Taiwan (66.1 against 64.8) "
             "and below on German Credit (61.6 against 66.8). No advantage is claimed on the real datasets"),
      provenance="Study 7 of 7, run record QL-ST-009",
      quotes=["360 trainings, each a run of the QML RQP Pro",
              "Input scaling moves the test score by 16.4 points on German Credit and 12.7 on Taiwan, above the noise "
              "level of 12.1 and 6.1.",
              "The noise level is the registered 80th percentile of the differences between two starts",
              "lands within one point of the best of 27 hand-searched configurations (German Credit 60.7 against "
              "61.6, Taiwan 65.3 against 66.1)",
              "no circuit with more two-qubit gates beats the 14-gate default beyond the noise level",
              "against logistic regression: on par on Taiwan (66.1 against 64.8), below on German Credit (61.6 "
              "against 66.8)",
              "Every score is an exact simulator value",
              "no advantage is claimed on the real datasets"]),
    A(id="qubit-lab-qmc-basket-call-ql-ev-006", context="qc",
      value=("qubit-lab.ch reports pricing a basket call at correlation 0.5 on a 16 x 16 = 256-state grid with "
             "low-depth amplitude estimation on a statevector simulator (9 qubits, 20 seeded repetitions per "
             "budget): the fitted slope of error against cost was 0.87 (ideal 1) against 0.43 for plain Monte "
             "Carlo (theory 0.5); the quantum estimate was more accurate from about 7,200 model evaluations on and "
             "2.6 times more accurate at the largest budget; the deepest circuit has 13,056 two-qubit gates. "
             "Printed verdict: Method study, advantage not claimed. The vendor revised the 7,200 and 2.6 figures on "
             "1 Nov 2026 (qubit-lab-qmc-basket-correction-400-repetitions)"),
      provenance="Run 1 of 5, run record QL-EV-006",
      quotes=["57.8%, correlation 0.5), strike 100 · 16 × 16 = 256 joint states on a log-spaced grid",
              "Statevector simulator with shot sampling, 9 qubits · 20 seeded repetitions per budget",
              "fitted slope 0.87 (ideal 1)",
              "fitted slope 0.43 (theory 0.5)",
              "more accurate than classical Monte Carlo from about 7,200 evaluations on, 2.6× at the largest budget",
              "Deepest circuit 13,056 two-qubit gates (784 per Grover step) — far beyond today's hardware",
              "a method study by construction; advantage not claimed",
              "Correction, 1 Nov 2026 · 200 repetitions."]),
    A(id="qubit-lab-qmc-basket-correction-400-repetitions", context="qc",
      value=("qubit-lab.ch corrected its basket-call run on 1 Nov 2026: at 200 repetitions the quantum estimate at "
             "correlation 0.5 is about 1.8 times more accurate (not 2.6); at 400 repetitions, against the exact "
             "classical error curve, the crossover is about 8,100 at correlation 0.5 and about 9,400 at correlation "
             "0, a move of +16% (90% bootstrap interval -6% to +38%), so zero is not excluded; the slopes, classical "
             "then amplitude estimation, are 0.49 and 0.86 at correlation 0.5 and 0.48 and 0.87 at correlation 0; "
             "and at the largest budget at correlation 0.5 the quantum estimate is about 1.9 times more accurate, "
             "classical Monte Carlo needing about 3.5 times the model evaluations"),
      provenance="Run 1 of 5, the corrections of 1 Nov 2026",
      quotes=["Correction, 1 Nov 2026 · 200 repetitions.",
              "We extended both cases to 400 repetitions",
              "at correlation 0.5 the quantum estimate is about 1.8 times more accurate (not 2.6)",
              "Against the exact curve the crossover is about 8,100 at correlation 0.5 and about 9,400 at "
              "correlation 0, a move of +16% (90% bootstrap interval −6% to +38%; theory +21%), so zero is still not "
              "excluded.",
              "Slopes: classical 0.49 / 0.48, amplitude estimation 0.86 / 0.87.",
              "At the largest budget at correlation 0.5 the quantum estimate is about 1.9 times more accurate, and "
              "classical Monte Carlo would need about 3.5 times the model evaluations for the same accuracy."]),
    A(id="qubit-lab-portfolio-qaoa-parity-ql-ev-001", context="qc",
      value=("qubit-lab.ch reports a warm-started QAOA run (depth p=4, seed 42) on a demo portfolio of 23 binary "
             "decisions (8,388,608 candidate portfolios), statevector simulator with exact readout: its best "
             "portfolio equals the SCIP-proven optimum (gap 0.0%), while the optimum's probability was 0.0016%, "
             "137 times uniform; a classical heuristic stopped 3.2% short. Printed verdict: Parity"),
      provenance="Run 2 of 5, run record QL-EV-001",
      quotes=["QAOA, depth p=4, warm-started, seed 42",
              "Statevector simulator, 23 qubits, exact readout (no sampling)",
              "8,388,608",
              "Gap 0.0% — best QAOA portfolio equals the SCIP-proven optimum, bit for bit · P(optimum) 0.0016% = "
              "137× uniform",
              "Heuristic search, 465 candidates — +3.2% gap, optimum not reached",
              "Printed verdict: Parity 16 Jul 2026"]),
    A(id="qubit-lab-collateral-cvar-qaoa-parity-ql-ev-003", context="qc",
      value=("qubit-lab.ch reports a warm-started CVaR QAOA run (depth p=3) on a 24-variable collateral "
             "allocation demo, every one of 16.8M states read exactly: the enumeration-proven optimum became the "
             "modal state at 2.6% (about 428,000 times uniform), from a stated classical warm start; the 36-variable "
             "flagship exceeded the simulator and its quantum stage was skipped. Printed verdict: Parity"),
      provenance="Run 3 of 5, run record QL-EV-003",
      quotes=["Warm-started CVaR QAOA, depth p=3, fixed seeds",
              "24-variable register",
              "Exact statevector readout of all 16.8M states",
              "Gap 0.00% — the optimum became the modal state at 2.6% (~428,000× uniform)",
              "Concentrated on the enumeration-proven optimum from a stated warm start; advantage not claimed",
              "36-variable flagship exceeds the simulator — quantum stage skipped by design",
              "Printed verdict: Parity 10 Aug 2026"]),
    A(id="qubit-lab-index-replication-qaoa-parity-ql-ev-002", context="qc",
      value=("qubit-lab.ch reports a QAOA run (depth p=2, 3 restarts, exact readout, 17 qubits, 544 two-qubit "
             "gates) on an S&P 500 demo mandate: its basket is a certified-optimal one after repair and a single "
             "disclosed polish swap, while only 3.6% of raw readout met the basket size and the mandate rules; a "
             "greedy heuristic was 3.39% short; on today's hardware the circuit would retain about 7% fidelity. "
             "Printed verdict: Parity"),
      provenance="Run 4 of 5, run record QL-EV-002",
      quotes=["S&P 500 demo mandate — illustrative, not investment advice",
              "QAOA, depth p=2, 3 restarts, exact readout",
              "17 qubits, 544 two-qubit gates",
              "Gap 0.00% — its basket is a certified-optimal one, after repair and a single disclosed polish swap",
              "Only 3.6% of raw quantum readout met the 20-name basket size and the mandate rules",
              "Greedy heuristic (industry-standard shortcut) +3.39%",
              "On today's hardware this circuit would retain ~7% fidelity",
              "Printed verdict: Parity 12 Jul 2026"]),
    A(id="qubit-lab-qml-power-price-no-advantage-ql-ev-004", context="qml",
      value=("qubit-lab.ch reports an 8-qubit quantum kernel classifier on German power-price spikes (17,157 rows, "
             "an exact 10,294 x 10,294 kernel) against six tuned classical baselines including an order-matched "
             "periodic twin: advantage factor 0.92 on raw features (95% CI 0.896-0.937, below 1.0) and 0.99 on "
             "Fourier-engineered features (95% CI 0.975-1.011, includes 1.0). Printed verdict: No advantage "
             "demonstrated, a verdict about one dataset"),
      provenance="Run 5 of 5, run record QL-EV-004",
      quotes=["17,157 rows · exact 10,294×10,294 quantum kernel · 8-qubit feature map",
              "Six tuned classical baselines incl. an order-matched periodic twin to interaction order 3",
              "Advantage factor 0.92× raw (95% CI 0.896–0.937, below 1.0) · 0.99× Fourier-engineered (95% CI "
              "0.975–1.011, includes 1.0)",
              "Printed verdict: No advantage demonstrated 23 Jul 2026",
              "A verdict about one dataset, not about quantum"]),
    A(id="qubit-lab-qml-quantum-native-advantage-ql-ev-005", context="qml",
      value=("qubit-lab.ch reports that on a quantum-native demo dataset (labels from a quantum teacher, "
             "engineered to sit in quantum territory) its quantum kernel and 6-qubit variational classifier reached "
             "an advantage factor of 1.45 (95% CI 1.31-1.62, entirely above 1.0), VQC test F1 0.89 against 0.71 "
             "for the best classical model. Printed verdict: Advantage demonstrated; its scope is the gate working "
             "in both directions, not a market dataset win"),
      provenance="Run 5 of 5, run record QL-EV-005",
      quotes=["Quantum kernel + 6-qubit variational quantum classifier",
              "Advantage factor 1.45× (95% CI 1.31–1.62, entirely above 1.0) · VQC test F1 0.89 vs 0.71 best classical",
              "Quantum-native demo data — engineered to sit in quantum territory; scope is the gate working in both "
              "directions, not a market dataset win",
              "Printed verdict: Advantage demonstrated 26 Jul 2026"]),
    A(id="qubit-lab-baf-fraud-no-complementary-signal", context="qml",
      value=("qubit-lab.ch reports that on the public BAF fraud benchmark (fraud-ops configuration, 15-qubit "
             "kernel) the fitted quantum blend weight was 0.00, the ensemble delta against a stack of every "
             "classical baseline was +0.0002 (95% CI -0.0004 to +0.0011, a statistical zero), and a fraud-tuned "
             "run's advantage factor was 0.92 (95% CI 0.83-1.00), classical ahead. Printed verdict: no "
             "complementary signal. One public benchmark, one configuration"),
      provenance="Run 5 of 5, the complementary-signal panel of 7 Aug 2026",
      quotes=["BAF fraud benchmark, fraud-ops configuration, 15-qubit kernel",
              "0.00 Quantum blend weight — fitted on validation",
              "+0.0002 Ensemble delta vs classical-stack control 95% CI −0.0004 to +0.0011 — statistical zero.",
              "0.92× Advantage factor, fraud-tuned run 95% CI 0.83–1.00 — classical ahead.",
              "Printed verdict: no complementary signal"]),
    A(id="qubit-lab-evidence-method-locked-designs-reproduced-numbers", context="method",
      value=("qubit-lab.ch states how its studies are made: each design is locked in writing before the first run "
             "(publicly tagged from the VQC study on, and once deposited with an independent registry, not checked "
             "here); certified classical referees score every run; each published number is reproduced from the "
             "committed raw results by a committed script before it is printed; a figure later found imprecise is "
             "corrected in the document's revision notes; and every record carries a fixed field order and a "
             "controlled verdict vocabulary, machine-readable at /evidence-runs.json"),
      provenance="How these studies are made, and each run record's footer",
      quotes=["Each design is locked in writing before the first run",
              "from the VQC study onward, publicly tagged before the first run",
              "The RQP platform's certified classical referees score every run",
              "each published number is reproduced from the committed raw results by a committed script before it "
              "is printed",
              "Where a published figure was later found imprecise, the correction is disclosed in the document's "
              "revision notes.",
              "Fixed field order · controlled verdict vocabulary (Advantage demonstrated / Parity / No advantage "
              "demonstrated / Inconclusive) · all records machine-readable at /evidence-runs.json"]),
]

_STORED = ("SELECT r.value, r.provenance, r.certainty, r.certainty_reasons, r.evidence_tag, r.fidelity, "
           "a.citation_context, a.claim_type, a.derivation "
           "FROM records r JOIN assertion_fields a ON a.record_id = r.id WHERE r.id = ?")
_FIELDS = ("value", "provenance", "certainty", "certainty_reasons", "evidence_tag", "fidelity", "citation_context",
           "claim_type", "derivation")
_SOURCE = "SELECT tier, access, disposition, evidence FROM paper_fields WHERE record_id = ?"

# Corrections decided after the first apply, each with the fields its review decided; written through
# store.ingest.sync_decided_assertion, which refuses any other changed field. A stored record that differs in a
# field not named here stops the run.
DECIDED = {
    # The second fresh-eyes review, 2026-11-21: the page scopes "0 of 96" to the real books ("Wrong seed on real
    # books: never escaped"); the first value let it read as covering all 24 instances.
    "qubit-lab-qaoa-concentration-study-ql-st-001": {"value", "citation_context"},
}
FIX_NOTE = (f"{TODAY} ({TAG}, the second fresh-eyes review): the wrong seed's 0 of 96 scoped to the real books, "
            "as the page states, with its quote")


def counts(conn) -> str:
    n = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'assertion'").fetchone()[0]
    p = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'paper'").fetchone()[0]
    return f"papers {p}; assertions {n}"


def verify_all() -> list:
    """Every quote verbatim in the saved page, with the value's figures, BEFORE anything is written."""
    text = source_text(str(PAGE))
    return [(a, require_verbatim(a.id, a.citation_context, text, value=a.value)) for a in ASSERTIONS]


def differs(conn, a: AssertionRecord) -> set[str] | None:
    """None when `a` is not stored; else the names of the fields where the stored record differs from this script's
    version (empty when it matches). The value is compared as the store keeps it (`with_common_names`)."""
    row = conn.execute(_STORED, (a.id,)).fetchone()
    if row is None:
        return None
    want = dict(zip(_FIELDS, (getattr(a, f) for f in _FIELDS)))
    want["value"] = with_common_names(a.value)
    out = {f for f, got in zip(_FIELDS, row) if got != want[f]}
    contexts = {c for (c,) in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,))}
    if a.context not in contexts:
        out.add("context")
    return out


def source_differs(conn) -> set[str] | None:
    """None when the source record is not stored; else the names of its fields that differ from `entry()`."""
    row = conn.execute(_SOURCE, (SOURCE_ID,)).fetchone()
    if row is None:
        return None
    e = entry()
    out = {f for f, got in zip(("tier", "access", "disposition", "evidence"), row) if got != e[f]}
    stored = {tuple(r) for r in conn.execute("SELECT context_id, rationale FROM paper_applicability "
                                             "WHERE record_id = ?", (SOURCE_ID,))}  # a Row is not a tuple
    if stored != {tuple(x) for x in e["applicability"]}:
        out.add("applicability")
    return out


def apply_changes(conn, apply: bool) -> list[str]:
    checked = verify_all()
    stop = [f"{SOURCE_ID} ({', '.join(sorted(d))})" for d in [source_differs(conn)] if d]
    for a, _ in checked:
        d = differs(conn, a)
        if d and not d <= DECIDED.get(a.id, set()):
            stop.append(f"{a.id} ({', '.join(sorted(d))})")
    if stop:
        raise SystemExit("DIFFERS, nothing written: stored, and not as this script states them, in a field no "
                         "review decided: " + "; ".join(stop))
    log = [f"before: {counts(conn)}"]
    record = intake.build_record(entry(), today=TODAY)
    if source_differs(conn) is not None:
        log.append(f"exists {record.id}")
    else:
        if apply:
            insert_paper(conn, record)
        log.append(f"source {record.id} [{record.tier}]")
    for a, verified in checked:
        d = differs(conn, a)
        if d:
            if apply:
                sync_decided_assertion(conn, a, verified, FIX_NOTE, TODAY, DECIDED[a.id])
            log.append(f"correct {a.id} ({', '.join(sorted(d))})")
            continue
        if d is not None:
            log.append(f"exists {a.id}")
            continue
        if apply:
            insert_verified_assertion(conn, a, verified, yielded_by=SOURCE_ID)
        else:
            validate_assertion(a)
        log.append(f"assert {a.id} [{a.certainty}]")
    if apply:
        log.append(f"after:  {counts(conn)}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    missing = [str(p) for p in (PAGE, RUNS) if not p.exists()]
    if missing:
        print("missing local copies:\n" + "\n".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F145 qubit-lab.ch Evidence page")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, apply)
        if apply:
            conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
