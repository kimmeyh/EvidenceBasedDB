#!/usr/bin/env python3
"""Sprint 6 Task G (F41): the Cyc and Fourier Wall package, WITHOUT the
CVQBoost findings (Q4: they wait for the hsbc re-run; card F51).

Adapted 2026-10-03 from the handoff draft (prepared 2026-09-29 outside the
repository, tested 2026-09-30) for the team lead's decisions of 2026-10-03:
the six CVQBoost assertions are filtered out; the hardware plan has its own
record (decision 4.2) and yields its three assertions; decision 3's two
certainty changes and decision 4.1's `method` row on the Fourier Wall record
are applied; every assertion carries ADR-0004 A6's fields and every
promotion records its read extent (ADR-0005 A4). The draft's text follows.

Modeled on scripts/sprint4_task_h_extraction.py. Dry run by default; --apply
writes. Run AFTER 03-manifest-sources.json has been applied, because most
assertions below are yielded by records that manifest creates.

What it does, in order:
  1. Adds applicability to three existing `seen` records, then promotes them to
     `read` (set_tier requires applicability for `screened` and `read`).
  2. Extends the checked_against_source note on the Fourier Wall record, which
     is already `read` but was checked on pp.12-13 only.
  3. Inserts 41 assertions: 23 from FACTS-WITH-CERTAINTY.md whose sources were
     read directly, and 18 new Cyc assertions. Tested 2026-09-30 against a
     COPY of store/evidence.db with stand-in rows for the 8 new sources: 41
     inserted, foreign_key_check 0 problems, repository untouched.
  4. Appends notes to existing Cyc assertions that the new ones refine.

Every quote in citation_context was re-checked against the local source on
2026-09-30 by substring match after whitespace normalization. Where the source
carries markup (markdown bold, HTML links, Lisp comment markers), the quote
drops the markup and says so. reading_level is deliberately None throughout: the grade-escalation
pass has not been done and a guessed level is worse than none.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, add_read, append_updated_reason, insert_assertion, set_tier  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-03"
TAG = "Sprint 6 Task G"
REASON = f"{TODAY} ({TAG}): extracted from sources read directly 2026-09-22 to 2026-09-28; see docs/research/2026-09-28_F42_cyc-kb-organization-and-inference.md"

# Source record ids. The first three are derived by the door from the GitHub
# API (confirmed by an intake.py dry run on 2026-09-29).
# opencyc-latest.owl.gz is a blob in that repository's git history (MD5 96110c055c66b8774529b3b529ac2b55,
# matching the repository README); the session's working copy was in a temp folder.
OPENCYC_REPO = "asanchez75-opencyc-github-repo"
LARKC = "cycorp-2009-larkc-cyc-inference-engine-source"
OC40 = "cycorp-2012-opencyc-4-0-release"
OC07 = "cycorp-2002-opencyc-0-7-0-release"
INFER = "cycorp-2002-introduction-cyc-inferencing"
SBHL = "cycorp-2002-sbhl-subsumption-based-heuristic-modules"
INDEX = "cycorp-2002-kb-term-indexing-cyc"
CVQ = "kimmey-2026-maximizing-predictions-cvqboost-cumulative-findings"
FW = "mancilla-2026-fourier-wall-spectra"
WANG = "wang-2024-transition-role-entangled-data-quantum"
TNC = "resonance-alliance-2026-2026-global-quantum-ai-challenge"   # the Terms and Conditions PDF
CRIT = "resonance-alliance-2026-assessment-criteria"
# Decision 4.2 (2026-10-03): the hardware plan has its own source record,
# pinned at commit a6c3453, and yields the three assertions that cite it.
HWPLAN = "hsbc-quantum-fraud-2026-hardware-plan-phase-2"

# --- 1 and 2. Applicability, then promotion -----------------------------------
# (record, [(context, rationale -- anchor)], checked_against_source)
PROMOTIONS = [
    (WANG, [("qml", "Schmidt-rank threshold on entangled training data: entanglement helps below a threshold set by the "
                    "number of measurements and hurts above it -- PDF p.5 Discussion")],
     "2026-09-23, Claude, extracted the arXiv PDF text and read p.5 (simulation results and Discussion) directly"),
    (TNC, [("hsbc-2026", "The challenge's governing terms: participant IP, the license to Resonance, confidentiality -- "
                         "PDF p.2 section 4 and p.4 section 7")],
     "2026-09-22, Claude, read the full five-page PDF directly (References copy)"),
    (CRIT, [("hsbc-2026", "The challenge's Phase 1 and Phase 2 scoring weights and what reviewers assess -- PDF p.3 Phase 2 table")],
     "2026-09-22, Claude, read the full four-page PDF directly (References copy)"),
]
FW_CHECKED = ("2026-09-19, Claude, read pp.12-13 directly (Honesty and scope; Conclusion) plus the abstract via DataCite; "
              "2026-09-22, Claude, read the full 16-page arXiv v1 PDF directly")

# --- 3. Assertions: (AssertionRecord, yielded_by or None) ----------------------
# ADR-0004 A6 (Sprint 6 Task E): every assertion here is read from a source
# that yields it, so `extracted`. claim_type is classified one by one: the
# Cycorp manual pages describing Cyc are the vendor on its own product; facts
# measured by reading the code or the release files are ours, so `positive`;
# one absence claim carries its search scope.
VENDOR_SELF_CLAIMS = {
    "cyc-2002-node-heuristics-combined-by-linear-sum", "cyc-2002-hl-modules-declare-cost-per-literal",
    "cyc-cnf-storage-gives-modus-tollens-free", "cyc-index-layers-carry-counts",
    "cyc-sbhl-graph-modules-for-transitive-hierarchies",
}
ABSENCE_SCOPES = {
    "cyc-owl-export-drops-microtheory-assignment":
        "streaming parse of the whole of opencyc-latest.owl.gz (asanchez75/opencyc) for any per-fact microtheory "
        "assignment, 2026-09-27 (docs/research/2026-09-28_F42_cyc-kb-organization-and-inference.md)",
}


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("reading_level", None)
    kw.setdefault("derivation", "extracted")
    if kw["id"] in VENDOR_SELF_CLAIMS:
        kw.setdefault("claim_type", "vendor-self-claim")
    elif kw["id"] in ABSENCE_SCOPES:
        kw.setdefault("claim_type", "absence")
        kw.setdefault("search_scope", ABSENCE_SCOPES[kw["id"]])
    return AssertionRecord(**kw)

ASSERTIONS: list[tuple[AssertionRecord, str | None]] = [
    # ---- CVQBoost on Dirac-3 (team lead's own measurements) ----
    (A(id="cvqboost-ridge-must-scale-with-record-count",
       value=("CVQBoost's ridge coefficient lambda_coef is added to a QUBO diagonal of order n_records, so small values (0.1, 1, 10) "
              "are no-ops; on oilgas/target (N about 25,700) sweeping 0, 2,500, 25,000, 50,000 and 100,000 raised overall AUROC "
              "0.8817, 0.8837, 0.8878, 0.8885, 0.8887, monotonic but flattening, peaking at about 2 to 4 times n_records; the "
              "source then sets lambda_coef to about 2 x n_records per dataset"),
       provenance=f"{CVQ}, section 3 parameter table and section 9 runs 4, 5, 6, 8 and 9",
       evidence_tag="HW", context="platform:dirac-3",
       citation_context=('"The QUBO was over-concentrating weights; ridging toward a more uniform convex combination '
                         'generalizes better." (section 3)'),
       certainty="high",
       certainty_reasons=("Started HIGH: the team's own measurement on Dirac-3 with a pinned seed and a recorded run log. NOT "
                          "downgraded: the sweep is monotonic over five points and the mechanism (a diagonal of order N) explains "
                          "it. NOT generalized: one dataset and one label; the per-dataset scaling rule is inferred, then applied in "
                          "the section 10 rollout"),
       fidelity="scoped"), CVQ),
    (A(id="cvqboost-relaxation-schedule-4-no-gain-3-8x-cost",
       value=("On Dirac-3, raising CVQBoost's relaxation_schedule from 2 to 4 gave no measurable accuracy change (overall AUROC "
              "0.8802 against 0.8805) at about 3.8 times the QPU cost per sample (63 s against 234 s for the same run)"),
       provenance=f"{CVQ}, section 3, section 4 cost table and section 9 runs 2 and 3",
       evidence_tag="HW", context="platform:dirac-3",
       citation_context='"cost ~3.8x more QPU per sample. Pure waste here." (section 3)',
       certainty="high",
       certainty_reasons="Started HIGH: own measurement, one knob varied against a pinned seed. NOT downgraded",
       fidelity="scoped"), CVQ),
    (A(id="cvqboost-16-samples-no-better-than-8",
       value=("CVQBoost with num_samples 16 showed no discernible improvement over 8 on Dirac-3 at twice the QPU cost, because "
              "solve() keeps only the lowest-energy sample and lower QUBO energy does not improve generalization"),
       provenance=f"{CVQ}, section 3 and section 9 runs 3 and 4",
       evidence_tag="HW", context="platform:dirac-3",
       citation_context='"(8 was marginally better, within noise) at ~half the QPU." (section 3)',
       certainty="moderate",
       certainty_reasons=("Started HIGH: own measurement. DOWNGRADED one level for imprecision: an absence of effect from one "
                          "comparison, described by the source as within noise, not a measured equivalence"),
       fidelity="scoped"), CVQ),
    (A(id="cvqboost-shallow-weak-learners-hurt",
       value=("Making CVQBoost's weak learners shallower (max_depth 2, 50 trees) cut overall AUROC from 0.8878 to 0.8391 on "
              "oilgas/target and turned its in-segment result back into a loss against XGBoost"),
       provenance=f"{CVQ}, section 3 and section 9 run 7",
       evidence_tag="HW", context="platform:dirac-3",
       citation_context=('"The full-depth per-subset learners carry the signal; the simplex + ridge already regularize the '
                         'ensemble." (section 3)'),
       certainty="high",
       certainty_reasons="Started HIGH: own measurement, one knob varied against a pinned seed, large effect. NOT downgraded",
       fidelity="scoped"), CVQ),
    (A(id="cvqboost-in-segment-overfit-exceeds-xgboost",
       value=("On the tuned SPECTRA rollout, CVQBoost's in-segment ROC-AUC train-to-test gap exceeded XGBoost's on all four "
              "target cells: energy_steel 0.083 against 0.001, maintenance 0.389 against 0.051 (CVQBoost 0.981 train, 0.592 "
              "test), oilgas 0.212 against 0.026, telecom 0.135 against 0.080"),
       provenance=f"{CVQ}, section 11 table",
       evidence_tag="HW", context="platform:dirac-3",
       citation_context='"i.e. CVQBoost is mostly memorizing there." (section 11, of maintenance/target)',
       certainty="high",
       certainty_reasons=("Started HIGH: own measurement, one seed, all four cells in the same direction. NOT downgraded. The value "
                          "states the table, not the section's summary: the summary says the gap is '3-8x XGBoost's on every "
                          "target cell', but the table's ratios are 83, 7.6, 8.2 and 1.7. The source calls its in-segment wins "
                          "fragile on this basis"),
       fidelity="scoped"), CVQ),
    (A(id="spectra-label-leak-signature-identical-perfect-models",
       value=("Using SPECTRA's target_real or in_pocket column as a feature when predicting target leaks the answer, with a "
              "recognizable signature: precision exactly 1.000 and both models near-perfect and identical, because both copied "
              "the leaked column"),
       provenance=f"{CVQ}, section 2",
       evidence_tag="N/A", context="method",
       citation_context=('"Symptom: precision = 1.000, both models near-perfect and identical (they just copied the leaked '
                         'column)." (section 2, markdown bold removed)'),
       certainty="high",
       certainty_reasons="Started HIGH: own observation with a mechanistic explanation that any reader can reproduce. NOT downgraded",
       fidelity="exact"), CVQ),

    # ---- hsbc-2026 project facts ----
    (A(id="hsbc-dirac3-allocation-1681-after-sizing-probes",
       value=("Of the 3,000 Dirac-3 seconds granted on 2026-09-09, 1,039 were drawn by the Phase 1 campaign and 280 by the integer "
              "sizing probes of 2026-09-23, leaving 1,681"),
       provenance=f"{HWPLAN}, Allocation position table",
       evidence_tag="N/A", context="hsbc-2026",
       certainty="high",
       certainty_reasons=("Started HIGH: the project's own ledger, read directly, arithmetic checked (3,000 - 1,039 - 280 = 1,681). "
                          "Note CHECKLIST-Phase2.md line 61 still read 1,961 on 2026-09-30, the figure before the probes"),
       fidelity="exact"), HWPLAN),
    (A(id="challenge-terms-participant-ip-retained",
       value="Under the challenge terms, all intellectual property in a submission remains the participant's",
       provenance=f"{TNC}, p.2 section 4.1",
       evidence_tag="N/A", context="hsbc-2026",
       citation_context='"All intellectual property contained in your submission remains your property." (p.2, section 4.1)',
       certainty="high", certainty_reasons="Started HIGH: the governing contract, read directly and quoted verbatim",
       fidelity="exact"), TNC),
    (A(id="challenge-terms-arxiv-publication-carve-out",
       value=("The challenge terms limit how Resonance may share a submission but carve out material already publicly available, "
              "naming an arXiv paper as the example"),
       provenance=f"{TNC}, p.2 section 4.2",
       evidence_tag="N/A", context="hsbc-2026",
       citation_context='"unless it is already publicly available (for example as part of an ArXiv paper)" (p.2, section 4.2)',
       certainty="high", certainty_reasons="Started HIGH: the governing contract, read directly and quoted verbatim",
       fidelity="exact"), TNC),
    (A(id="challenge-terms-confidentiality-binds-on-sponsor-material",
       value=("The challenge's confidentiality clause binds a participant only on receiving sponsor problem statements, briefings, "
              "compute resources or other non-public material as a finalist; it obliges Resonance to treat the technical "
              "content of submissions as confidential within evaluation, subject to the section 4.2 license"),
       provenance=f"{TNC}, p.4 section 7",
       evidence_tag="N/A", context="hsbc-2026",
       citation_context=('"If you are selected as a finalist and are given access to sponsor problem statements, technical '
                         'briefings, compute resources, or other non-public materials, you agree to treat such information as '
                         'confidential" (p.4, section 7)'),
       certainty="high",
       certainty_reasons=("Started HIGH: the governing contract, read directly. Scope: the value states what section 7 says; "
                          "what it leaves unrestricted is a reading, and is deliberately not asserted"),
       fidelity="exact"), TNC),
    (A(id="challenge-phase2-scoring-accepts-parity",
       value=("The Phase 2 criteria weight PoC quality and results at 30 percent, asking for evidence of quantum advantage, parity "
              "or a credible path to advantage; enterprise relevance 25; technical rigor 20; scalability 15, asking whether "
              "constraints are honestly assessed; presentation 10. The table is marked subject to change before Phase 2"),
       provenance=f"{CRIT}, p.3 Phase 2 table and p.2 section 4",
       evidence_tag="N/A", context="hsbc-2026",
       citation_context='"Is there evidence of quantum advantage, parity, or a credible path to advantage?" (p.3)',
       certainty="moderate",
       certainty_reasons=("Started HIGH: governing document read directly. DOWNGRADED one level for indirectness: the document says "
                          "the Phase 2 table 'is subject to change prior to the launch of Phase 2' (p.2), so it may not be the "
                          "criteria applied"),
       fidelity="exact"), CRIT),
    (A(id="dirac3-integer-cost-tracks-variables-not-levels",
       value=("Dirac-3 integer-solver cost tracked variable count rather than level budget across five sizing calls: 8 variables "
              "and 32 levels 4 s; 24 and 96, 8 s; 60 and 240, 28 s; 150 and 600, 165 s; 60 and 840, 71 s. The last two are a "
              "controlled pair: 1.4 times the levels cost 2.3 times less"),
       provenance=f"{HWPLAN}, Experiment 3 cost table (measured 2026-09-23)",
       evidence_tag="HW", context="platform:dirac-3",
       certainty="high",
       certainty_reasons=("Started HIGH: the project's own hardware measurements, all status ok, read directly. NOT downgraded. "
                          "Scope: the controlled comparison is a single pair, so the mechanism is demonstrated rather than characterized"),
       fidelity="scoped"), HWPLAN),
    (A(id="dirac3-integer-cost-per-level-line-falsified",
       value=("A two-point fit of Dirac-3 integer-solver cost at 0.0625 s per level was off by 1.6 and 4.1 times on the next two "
              "calls; a five-point fit gives roughly vars^0.75 x levels^0.52, with points missing by up to 45 percent, so cost "
              "grows faster than linearly when the level budget grows with the variable count"),
       provenance=f"{HWPLAN}, Experiment 3 cost discussion",
       evidence_tag="HW", context="platform:dirac-3",
       certainty="moderate",
       certainty_reasons=("Started HIGH: own measurement. DOWNGRADED one level for imprecision: five points, and the source offers the "
                          "exponents 'as indicative rather than as a formula'. The source says cost is 'superlinear in "
                          "variables'; its own fit has a variable exponent of 0.75, so the value states the joint growth "
                          "(0.75 + 0.52 = 1.27 when levels scale with variables) instead"),
       fidelity="scoped"), HWPLAN),

    # ---- Fourier Wall (all yielded by the already-read FW record). Only the four facts that bear on public
    # tabular data support fourier-wall-public-tabular-refuses-qml; the rest concern the authors' own substrates. ----
    (A(id="fourier-wall-five-conditions-for-qnn-advantage",
       value=("An angle-encoded QNN can beat a tuned classical model only where five conditions hold together: an off-grid "
              "spectrum (rho_off above 0.3), a non-separable term of order at least 3, near-independent features, a "
              "tree-breaking frequency, and a dense, non-enumerable spectrum"),
       provenance=f"{FW}, p.4 Algorithm 1 and p.5 conditions C1 to C5",
       evidence_tag="N/A", context="qml",
       citation_context='"otherwise an integer-grid surrogate dequantizes the model" (p.5, C1)',
       certainty="low",
       certainty_reasons=("Started LOW: preprint v1 from one group, 2026, no independent replication. NOT upgraded: the argument is "
                          "transparent and the counterfactual is shown, but transparency is not replication"),
       fidelity="scoped", supports=["fourier-wall-public-tabular-refuses-qml"]), FW),
    (A(id="fourier-wall-loud-residual-gate-favors-classical",
       value=("In the SPECTRA tier-1 screen a strong JOINT minus GA2M residual means the spectrum is sparse and enumerable, so an "
              "order-matched classical twin wins; the candidate signature is strong interaction with a silent residual "
              "(HGB minus GAM +0.15, residual +0.00, joint ratio 9.9) against the sparse pocket's residual of +0.37"),
       provenance=f"{FW}, p.8 section 6.3",
       evidence_tag="N/A", context="qml",
       citation_context='"(strong interaction, silent enumeration)" (p.8)',
       certainty="low",
       certainty_reasons="Started LOW: single-group preprint; both substrates are semi-synthetic by construction, as the paper states",
       fidelity="scoped"), FW),
    (A(id="fourier-wall-incomplete-bar-manufactures-advantage",
       value=("On the Fourier Wall's sparse pocket a classical bar of GAM, GA2M and HGB alone credits the quantum model with "
              "advantage at 0.758 against 0.721, while adding the order-matched JOINT twin reads the same structure classically "
              "at 0.968"),
       provenance=f"{FW}, p.4 section 5",
       evidence_tag="N/A", context="method",
       citation_context='"a bar of GAM, GA2M and HGB alone would credit the quantum model with an advantage at 0.758 vs. 0.721" (p.4)',
       certainty="low",
       certainty_reasons=("Started LOW: single-group preprint. NOT upgraded for admission against interest: the counterfactual argues "
                          "for the authors' own bar-completeness requirement, so it costs them nothing"),
       fidelity="exact", supports=["fourier-wall-public-tabular-refuses-qml"]), FW),
    (A(id="fourier-wall-certified-gap-0-699-vs-0-994",
       value=("On the Fourier Wall's certified dense substrate the complete classical bar tops out at 0.699 ROC-AUC while the "
              "dynamics-matched quantum model reaches 0.994, and an exact classical simulator ties it at 0.993"),
       provenance=f"{FW}, p.11 Figure 7",
       evidence_tag="N/A", context="qml",
       certainty="low",
       certainty_reasons=("Started LOW: single-group preprint. NOT upgraded: the labels come from a simulated Heisenberg chain, so this "
                          "is a positive control on a semi-synthetic substrate, not a natural dataset"),
       fidelity="scoped"), FW),
    (A(id="fourier-wall-advantage-is-resource-scaling-crossover-13-19",
       value=("The Fourier Wall's certified advantage is a resource-scaling claim, not an accuracy claim at small width: the only "
              "classical model matching it pays a simulation cost that grows exponentially with process width, with a measured "
              "wall-clock crossover at about 13 to 19 sites"),
       provenance=f"{FW}, p.7 section 6.3 and Figure 6",
       evidence_tag="N/A", context="qml",
       certainty="low",
       certainty_reasons="Started LOW: single-group preprint; the crossover depends on the authors' own cost model for both lanes",
       fidelity="scoped"), FW),
    (A(id="fourier-wall-is-a-feature-engineering-target",
       value=("The Fourier Wall paper treats the wall as a feature-engineering target: re-expressing cyclic covariates as phases "
              "and whitening the encoded block can move a problem toward the QNN's regime"),
       provenance=f"{FW}, p.4 section 4",
       evidence_tag="N/A", context="qml",
       certainty="low",
       certainty_reasons="Started LOW: single-group preprint, measured on the authors' own substrates",
       fidelity="scoped"), FW),
    (A(id="fourier-wall-c5-needs-an-interacting-process",
       value=("The Fourier Wall's demanding condition is a target tied to an interacting process rather than a level or trend, "
              "which the authors say holds by physics for quantum hardware telemetry, sensor arrays, spin-system readouts and "
              "spectroscopy; the certificate refused every raw public target the authors tested"),
       provenance=f"{FW}, p.8 section 6.4 and p.4 section 5",
       evidence_tag="N/A", context="qml",
       certainty="low",
       certainty_reasons="Started LOW: single-group preprint; the refusal claim covers only the targets the authors tested",
       fidelity="scoped", supports=["fourier-wall-public-tabular-refuses-qml"]), FW),
    (A(id="fourier-wall-route-and-blend-two-requirements",
       value=("The Fourier Wall's route-and-blend deployment re-ranks within a band of the classical score, and has two "
              "load-bearing requirements: the router's gate must be independent of the specialist's features, and the "
              "specialist must match its certified configuration, since an undertrained single-restart variant turned the "
              "blend negative (-0.043)"),
       provenance=f"{FW}, p.11 section 7, Algorithm 2",
       evidence_tag="N/A", context="qml",
       citation_context='"an under-trained single-restart variant turned the same blend negative (-0.043)" (p.11)',
       certainty="low", certainty_reasons="Started LOW: single-group preprint, measured once on one substrate",
       fidelity="scoped"), FW),
    (A(id="fourier-wall-correlation-partially-dequantizes",
       value=("Correlated encoded features let a QNN's joint term leak into low-order projections that classical twins capture, "
              "so correlation is a partial dequantizer, which is why the SPECTRA pipeline whitens the encoded block"),
       provenance=f"{FW}, p.5 condition C3",
       evidence_tag="N/A", context="qml",
       citation_context='"Correlation is a partial dequantizer." (p.5, C3)',
       certainty="low", certainty_reasons="Started LOW: single-group preprint",
       fidelity="exact", supports=["fourier-wall-public-tabular-refuses-qml"]), FW),

    # ---- Entangled data ----
    (A(id="entangled-data-schmidt-rank-threshold",
       value=("For learning quantum dynamics from entangled data, raising the Schmidt rank lowers prediction error only below a "
              "threshold set by the number of measurements and raises it above: in simulation the critical rank was 3 at 10 "
              "measurements and 4 at 100, with monotonic improvement only above about 1,000"),
       provenance=f"{WANG}, p.5 simulation results and Discussion",
       evidence_tag="N/A", context="qml",
       citation_context='"critical point which is r = 3 for m = 10 and r = 4 for m = 100" (p.5)',
       certainty="moderate",
       certainty_reasons=("Started MODERATE: peer-reviewed (Nature Communications) theory with matching simulation. NOT upgraded: the "
                          "setting is learning quantum dynamics with a fixed observable, not classical tabular classification, so "
                          "its use for fraud circuits is indirect"),
       fidelity="scoped"), WANG),

    # ---- Cyc: the knowledge base as exported ----
    (A(id="cyc-genls-is-a-rule-macro",
       value=("Cyc defines genls as a rule-macro predicate: (genls Poodle Dog) is shorthand for the rule (implies (isa ?OBJ "
              "Poodle) (isa ?OBJ Dog)), stored as one ground fact that the engine treats as fully equivalent to the rule"),
       provenance=f"{OPENCYC_REPO}, opencyc-latest.owl.gz, Cycorp's rdfs:comment on RuleMacroPredicate",
       evidence_tag="N/A", context="method",
       citation_context=('"genls is a rule-macro-predicate whose expansion assertion is (expansion genls (implies (isa ?OBJ :ARG1) '
                         '(isa ?OBJ :ARG2))" (RuleMacroPredicate comment, HTML link markup removed)'),
       certainty="high",
       certainty_reasons="Started MODERATE: vendor documentation. UPGRADED one level: verbatim from the knowledge base's own definition",
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), OPENCYC_REPO),
    (A(id="cyc-22-predicates-have-special-hl-support",
       value=("OpenCyc's knowledge base names 22 predicates with special HL support, most of them graph or identity relations: isa, "
              "genls, genlPreds, genlInverse, genlMt, disjointWith, subsetOf, negationPreds, negationInverse, equals, different, "
              "termOfUnit, quotedIsa and others"),
       provenance=f"{OPENCYC_REPO}, opencyc-latest.owl.gz, instances of HLPredicate",
       evidence_tag="N/A", context="method",
       citation_context='"HLPredicate is the collection of all Cyc predicates which have special HL support" (HLPredicate comment, HTML link markup removed)',
       certainty="high", certainty_reasons="Started HIGH: measured membership of a collection in the export, with Cycorp's definition verbatim",
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), OPENCYC_REPO),
    (A(id="cyc-owl-export-drops-microtheory-assignment",
       value=("OpenCyc's 2012 OWL export keeps the microtheory hierarchy (9,167 genlMt statements) but not the microtheory of each "
              "fact: only 19 definingMt statements appear among 2,189,031 statements, although Cyc requires every assertion to "
              "be true in at least one microtheory"),
       provenance=f"{OPENCYC_REPO}, opencyc-latest.owl.gz, measured 2026-09-27 (census.py, pass3.py)",
       evidence_tag="N/A", context="method",
       certainty="high", certainty_reasons="Started HIGH: a count over the whole export by streaming parse. NOT downgraded",
       fidelity="scoped"), OPENCYC_REPO),
    (A(id="cyc-genls-closure-31-times-direct-edges",
       value=("The transitive closure of genls over OpenCyc's exported taxonomy is 5,974,958 ancestor pairs against 193,309 direct "
              "edges, 31 times more, with a median of 47 ancestors per collection; 45 percent of collections have more than one "
              "parent"),
       provenance=f"{OPENCYC_REPO}, opencyc-latest.owl.gz, measured 2026-09-28 (closure.py, analyze.py)",
       evidence_tag="N/A", context="method",
       certainty="high",
       certainty_reasons=("Started HIGH: computed over the full exported graph. Scope: the export's edges may not equal the engine's "
                          "stored genls assertions exactly"),
       fidelity="scoped"), OPENCYC_REPO),

    # ---- Cyc: the 2002 design, in Cycorp's manual ----
    (A(id="cyc-2002-node-heuristics-combined-by-linear-sum",
       value=("Cyc-10 chose the next search node by summing weighted heuristics: favor fewer literals and fewer free variables, "
              "strongly favor nodes with no free variables, very weakly favor higher nodes, weakly disfavor negative literals, "
              "disfavor unification cycles and literals whose constant has no index for the predicate; the lowest sum is "
              "expanded next"),
       provenance=f"{INFER}, sections 4.1 and 4.2",
       evidence_tag="N/A", context="method",
       citation_context='"These heuristic rules act in concert, according to a linear summation rule." (section 4.2)',
       certainty="moderate",
       certainty_reasons=("Started MODERATE: vendor documentation of its own design. NOT upgraded: a manual can describe intent "
                          "rather than the running code, and this is Cyc-10 as of 2002"),
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), INFER),
    (A(id="cyc-2002-hl-modules-declare-cost-per-literal",
       value=("In Cyc-10 each HL module applicable to a literal had to supply a heuristic estimate of its cost, and the literal "
              "with the lowest summed cost was expanded first"),
       provenance=f"{INFER}, section 4.3",
       evidence_tag="N/A", context="method",
       citation_context=('"each HL module which applies to a literal must be able to provide a heuristic estimate for how expensive '
                         'it would be to apply that module to the literal." (section 4.3)'),
       certainty="moderate", certainty_reasons="Started MODERATE: vendor documentation of its own 2002 design",
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), INFER),
    (A(id="cyc-cnf-storage-gives-modus-tollens-free",
       value=("Cyc-10 stored and reasoned over formulas in conjunctive normal form, so one stored clause can prove any of its "
              "literals and modus tollens comes without extra rules; a canonical literal order reduces formula lookup to a "
              "structural-equality test"),
       provenance=f"{INFER}, section 2",
       evidence_tag="N/A", context="method",
       citation_context='"using CNF as a canonical form means that you get modus tollens inferencing \\"for free\\"." (section 2)',
       certainty="moderate", certainty_reasons="Started MODERATE: vendor documentation of its own 2002 design",
       fidelity="exact"), INFER),
    (A(id="cyc-index-layers-carry-counts",
       value=("Cyc indexes each term's assertions by argument position, then predicate, then microtheory, and every layer stores "
              "a count, so the number of assertions a lookup would touch is known before the lookup runs"),
       provenance=f"{INDEX}, section Argument Positions 1-5",
       evidence_tag="N/A", context="method",
       citation_context='"layer 1 : ( <count> . <pred-tree> ) or NIL" (Argument Positions 1-5)',
       certainty="moderate",
       certainty_reasons=("Started MODERATE: vendor documentation of its own 2002 design. NOT upgraded here; the 2009 code that "
                          "reads the counts is a separate assertion, cyc-lookup-cost-is-index-count, which supports this one"),
       fidelity="exact"), INDEX),
    (A(id="cyc-sbhl-graph-modules-for-transitive-hierarchies",
       value=("Cyc's SBHL modules support fast subsumption tests over hierarchies each defined by ground atomic assertions of one "
              "transitive predicate (genls, genlMt, genlPreds, genlAttributes), using special data structures and over fifty "
              "API functions, with disjoint domains per hierarchy"),
       provenance=f"{SBHL}, opening paragraphs",
       evidence_tag="N/A", context="method",
       citation_context=('"The SBHL modules are a growing collection of modules that support very fast inference involving '
                         'subsumption tests with respect to particular subsumption hierarchies." (opening)'),
       certainty="moderate", certainty_reasons="Started MODERATE: vendor documentation of its own 2002 design",
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), SBHL),

    # ---- Cyc: the 2009 engine source ----
    (A(id="cyc-lookup-cost-is-index-count",
       value=("In the 2009 Cyc engine the lookup removal module's cost is a fixed cheap constant when the literal is fully bound, "
              "and otherwise the GAF count read from the index, so index counts feed the planner's cost estimates directly"),
       provenance=f"{LARKC}, inference/modules/removal/removal_modules_lookup.java line 84 (removal_lookup_pos_cost)",
       evidence_tag="N/A", context="method",
       citation_context=('"return control_vars.$cheap_hl_module_check_cost$.getGlobalValue(); ... return '
                         'inference_trampolines.inference_num_gaf_lookup_index(asent, $kw0$POS);" (lines 89 and 91)'),
       certainty="high", certainty_reasons="Started HIGH: the code itself, read directly",
       fidelity="exact", supports=["cyc-index-layers-carry-counts"]), LARKC),
    (A(id="cyc-2009-thirteen-weighted-strategic-heuristics",
       value=("The 2009 Cyc tactician declares thirteen strategic heuristics with scaling factors: Shallow And Cheap 1, "
              "Completeness 1, Occam's Razor 250, Magic Wand 1,000, Backtracking Considered Harmful 10,000, backchainRequired "
              "10,000, highlyRelevantAssertion 10,000, highlyRelevantTerm 10,000, number of literals 10,000, number of rule "
              "literals 10,000, Historical Utility 20,000, Rule Connectedness 20,000, number of Skolems 300,000"),
       provenance=f"{LARKC}, inference/harness/inference_strategic_heuristics.java lines 1241 to 1272 and their $list constants",
       evidence_tag="N/A", context="method",
       citation_context='"The simplest explanation is best. Our measure of simplicity is the shallowest transformation depth." (Occam\'s Razor comment, line 1316, whitespace normalized)',
       certainty="high", certainty_reasons="Started HIGH: the code itself, extracted by script and read directly",
       fidelity="exact", supports=["heuristics-over-general-reasoning"]), LARKC),
    (A(id="cyc-rule-success-prior-about-3-percent",
       value=("The 2009 Cyc engine's historical-utility heuristic falls back to an average rule success probability of about "
              "0.029 when a rule has no history"),
       provenance=f"{LARKC}, inference/harness/inference_analysis.java line 1418 (constant) and line 1285 (use)",
       evidence_tag="N/A", context="method",
       citation_context='"makeDouble(0.02939361143247565)" (line 1418)',
       certainty="high", certainty_reasons="Started HIGH: the code itself, read directly. It is a search-control prior, not a truth weight",
       fidelity="exact", supports=["cyc-no-numeric-confidence"]), LARKC),
    (A(id="cyc-tms-removal-cascades-through-dependents",
       value=("In the 2009 Cyc engine, removing an argument for an assertion runs truth maintenance, and removing an assertion "
              "removes every deduction that depends on it"),
       provenance=f"{LARKC}, tms.java lines 194 (tms_remove_argument) and 538 (tms_remove_dependents)",
       evidence_tag="N/A", context="method",
       citation_context='"Remove all the deductions depending on this ASSERTION." (tms.java line 538)',
       certainty="high",
       certainty_reasons=("Started HIGH: the code's own docstrings, read directly. Scope: the recursive recomputation path was traced "
                          "by the research agent, not re-read line by line"),
       fidelity="exact"), LARKC),
    (A(id="cyc-deduction-strength-is-weakest-support",
       value=("The 2009 Cyc engine combines the strengths of a deduction's supports discretely: unknown if any support is "
              "unknown, otherwise default if any is default, otherwise monotonic, so a deduction is as strong as its weakest "
              "support; unknown is an HL strength value alongside default and monotonic"),
       provenance=f"{LARKC}, inference/harness/argumentation.java line 95 (the combining loop) and line 117 (strength_combine)",
       evidence_tag="N/A", context="method",
       citation_context='"if (((strength1 == $kw5$UNKNOWN) || (strength2 == $kw5$UNKNOWN))) { return $kw5$UNKNOWN;" (lines 120 to 122, whitespace normalized)',
       certainty="high", certainty_reasons="Started HIGH: the code itself, read directly",
       fidelity="exact", supports=["cyc-no-numeric-confidence", "cyc-truth-values-four"]), LARKC),
    (A(id="cyc-2009-type-checks-at-entry-not-during-search",
       value=("In the 2009 Cyc engine, well-formedness checking defaults to strict, while using argument types to filter "
              "backward inferences is off by default; forward inference does type-filter"),
       provenance=(f"{LARKC}, wff_vars.java line 344 (*WFF-MODE* :STRICT), at_vars.java line 550 "
                   "(*SEMANTIC-DNF-HL-FILTERING-ENABLED* NIL), removal_modules_conjunctive_pruning.java line 589 "
                   "(*RESIDUAL-TRANSFORMATION-VALIDATION-ENABLED?* NIL), inference/harness/forward.java line 1561 "
                   "(*TYPE-FILTER-FORWARD-DNF* T)"),
       evidence_tag="N/A", context="method",
       citation_context='"defparameter(\\"*SEMANTIC-DNF-HL-FILTERING-ENABLED*\\", NIL)" (at_vars.java)',
       certainty="high", certainty_reasons="Started HIGH: the code's defaults, read directly. Scope: inference parameters can rebind them",
       fidelity="exact"), LARKC),

    # ---- Cyc: the shipped releases ----
    (A(id="opencyc-sbhl-type-check-default-reversed-2002-2012",
       value=("OpenCyc shipped *SUSPEND-SBHL-TYPE-CHECKING?* as T in release 0.7.0 (2002), skipping SBHL type checks, and as NIL in "
              "release 4.0 (2012), whose comment calls checking slower but correcter"),
       provenance=(f"{OC40}, server/cyc/run/init/parameters.lisp line 23; {OC07}, run/init/parameters.lisp line 20"),
       evidence_tag="N/A", context="method",
       citation_context='"Type checking occurs in SBHL modules iff this is NIL, which is slower but correcter." (4.0 parameters.lisp lines 21 to 22, comment markers removed)',
       certainty="high", certainty_reasons="Started HIGH: the shipped configuration files, read directly",
       fidelity="exact"), OC40),
    (A(id="opencyc-kb-5022-counts",
       value=("OpenCyc 4.0's knowledge base KB 5022 holds 1,889,842 assertions, 188,111 constants, 48,238 function-built terms "
              "(NARTs), 337,085 stored deductions and 17,942 HL supports, per its shipped count files; constant 0 is genls"),
       provenance=f"{OC40}, server/cyc/run/units/5022/*-count.text and constant-shell.text",
       evidence_tag="N/A", context="method",
       certainty="high", certainty_reasons="Started HIGH: the release's own count files, read directly. A snapshot of that release",
       fidelity="exact"), OC40),
    (A(id="opencyc-4-0-ships-precomputed-structures",
       value=("OpenCyc 4.0 ships precomputed structures beside its assertions: SBHL module graphs (27.4 MiB with index), SBHL "
              "caches (5.6 MiB), term indexes (29.9 MiB with index), cardinality estimates (2.6 MiB), deductions (18.4 MiB with "
              "index); its rule-utility-experience file, the history behind the Historical Utility heuristic, is 1 byte"),
       provenance=f"{OC40}, server/cyc/run/units/5022 file listing",
       evidence_tag="N/A", context="method",
       certainty="high",
       certainty_reasons="Started HIGH: file names and sizes measured directly. Scope: file contents are serialized and were not decoded",
       fidelity="scoped", supports=["cyc-lookup-cost-is-index-count"]), OC40),
]
# Sprint 6 Q4 (team lead, 2026-10-03): the CVQBoost findings wait for the hsbc
# re-run, so the six assertions that record yields are NOT entered (card F51).
# Kept in the list above, unchanged from the tested draft, and filtered here.
ASSERTIONS = [(a, y) for a, y in ASSERTIONS if y != CVQ]

# Read extents for the promotions (ADR-0005 A4 (c)), transcribed from each
# record's checked_against_source.
PROMOTION_READS = {
    WANG: [("Claude", "2026-09-23", "partial", "PDF p.5 (simulation results and Discussion)")],
    TNC: [("Claude", "2026-09-22", "full", "")],
    CRIT: [("Claude", "2026-09-22", "full", "")],
}
FW_READ = ("Claude", "2026-09-22", "full", "the 16-page arXiv v1 PDF")

# Decision 4.1 (a): the Fourier Wall assertion filed under `method` sits inside
# its source's applicability.
FW_METHOD_ROW = ("method", "How an incomplete classical bar manufactures a quantum advantage: the order-matched JOINT "
                           "twin -- p.4 section 5")

# Decision 3 (c): two certainty changes, each with its reason appended.
CERTAINTY_CHANGES = [
    ("heuristics-over-general-reasoning", "moderate",
     f"{TODAY} ({TAG}, decision 3): UPGRADED one level, LOW to MODERATE: the 2002 Cycorp manual (inferencing.html, "
     "node-selection heuristics and their linear-sum weighting) and the 2009 engine source "
     "(inference_strategic_heuristics.java, lines 1241 to 1272), read 2026-09-28, are direct evidence of the mechanism. "
     "Stopped at one level: both are Cycorp's own, so neither is independent of the vendor"),
    ("cyc-no-numeric-confidence", "low",
     f"{TODAY} ({TAG}, decision 3): set, not chosen. Started LOW: position paper, the author's testimony about his own "
     "system. NOT upgraded: the 2009 source supports it (argumentation.java strength_combine, line 117, combines discrete "
     "strengths; inference_analysis.java line 1418's 0.029 rule prior is search control, not belief), but the claim is "
     "an absence, checked against a 2009 subset whose function bodies are withheld (missing-larkc), and the code is "
     "Cycorp's own"),
]

# --- 4. Notes on existing records ----------------------------------------------
NOTES = [
    ("cyc-truth-values-four",
     f"{TAG}: refined, not reversed. Assertions carry four composite truth values; the 2009 engine's argumentation also uses "
     "an 'unknown' strength at the HL level (see cyc-deduction-strength-is-weakest-support). Whether 'unknown' should count "
     "as a fifth value is a question for the sprint, not settled here"),
    ("cyc-no-numeric-confidence",
     f"{TAG}: supported by the 2009 source: argumentation combines discrete strengths, and the numbers found in the engine "
     "(productivity, heuristic weights, a 0.029 rule-success prior) are search control, not degrees of belief"),
    ("cyc-hl-module-count",
     f"{TAG}: the 2026-09-28 research agent reports that Taylor, Matuszek, Smith and Witbrock (FLAIRS 2007) give a figure "
     "of about a thousand. Not verified here; that paper is pending a local copy (handoff 04-pending-sources.md)"),
    ("cyc-context-count",
     f"{TAG}: OpenCyc's 2012 OWL export has 765 direct Microtheory instances. Not a contradiction: OpenCyc is a fragment "
     "of Cyc"),
]


def apply_changes(conn) -> list[str]:
    log = []
    for pid, applicability, checked in PROMOTIONS:
        for ctx, rationale in applicability:
            if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id=? AND context_id=?", (pid, ctx)).fetchone():
                conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                             (pid, ctx, rationale))
        for read in PROMOTION_READS[pid]:
            add_read(conn, pid, *read)
        set_tier(conn, pid, "read", checked_against_source=checked)
        append_updated_reason(conn, pid, REASON, TODAY)
        log.append(f"read   {pid}")
    add_read(conn, FW, *FW_READ)
    set_tier(conn, FW, "read", checked_against_source=FW_CHECKED)
    # Decision 4.1 assumed the record had no `method` row; it has one (from
    # its arXiv abstract, Sprint 4 re-filing), so the assertion already sits
    # inside its source's applicability. Add the row only if it is missing.
    has_method = conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ? AND context_id = 'method'",
                              (FW,)).fetchone()
    if not has_method:
        conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                     (FW, *FW_METHOD_ROW))
    append_updated_reason(conn, FW, f"{TODAY} ({TAG}): checked_against_source extended to the full 16-page read of "
                          "2026-09-22" + ("" if has_method else "; method applicability added (decision 4.1)"), TODAY)
    log.append(f"note   {FW} (checked extended; method row {'already present' if has_method else 'added'})")
    for rid, level, reason in CERTAINTY_CHANGES:
        old = conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?", (rid,)).fetchone()
        conn.execute("UPDATE records SET certainty = ?, certainty_reasons = ? WHERE id = ?",
                     (level, f"{old[1]} | {reason}" if old[1] else reason, rid))
        append_updated_reason(conn, rid, f"{TODAY} ({TAG}, decision 3): certainty {old[0]} -> {level}", TODAY)
        log.append(f"cert   {rid}: {old[0]} -> {level}")
    for assertion, yielded_by in ASSERTIONS:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (assertion.id,)).fetchone():
            log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, assertion, yielded_by=yielded_by)
        rel = (f" supports {assertion.supports}" if assertion.supports else "")
        log.append(f"assert {assertion.id} <- {yielded_by} [{assertion.certainty}]{rel}")
    # The SBHL-default assertion is yielded by both releases.
    if not conn.execute("SELECT 1 FROM paper_yields WHERE paper_id=? AND assertion_id=?",
                        (OC07, "opencyc-sbhl-type-check-default-reversed-2002-2012")).fetchone():
        conn.execute("INSERT INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)",
                     (OC07, "opencyc-sbhl-type-check-default-reversed-2002-2012"))
    for rid, note in NOTES:
        existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
        # The note itself, not the TAG: decision 3's certainty change writes the
        # TAG first on cyc-no-numeric-confidence, which made the draft's TAG
        # check skip that record's note (found on the 2026-10-03 dry run).
        if note not in existing:
            append_updated_reason(conn, rid, note, TODAY)
            log.append(f"note   {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    if "MM" in TODAY or TAG.startswith("Sprint N "):
        print("REFUSED: set TODAY and TAG first; they are written into every record's updated and updated_reason")
        return 1
    if do_apply:
        backup_before_write(DB_PATH, "sprint6 task G cyc and facts")  # F30: verified backup, or no write
    conn = connect(DB_PATH)
    conn.isolation_level = None  # the explicit BEGIN/COMMIT/ROLLBACK below own the transaction
    try:
        conn.execute("BEGIN")
        for line in apply_changes(conn):
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
        print("applied")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
