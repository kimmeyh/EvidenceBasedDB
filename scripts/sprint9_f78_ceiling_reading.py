#!/usr/bin/env python3
"""Sprint 9 Task E (F78): the ceiling-estimation (CE) group read and entered.

Team lead, 2026-10-14: "is there a way to find the maximum, near maximum
predictions or can't be better than... on any ML dataset and/or any
optimization problem". The 31 CE records plus Ishida et al. 2023 and Theisen
et al. 2021 (entered by `manifests/sprint9_f78_ishida_theisen.json`).

HOW THEY WERE READ (ADR-0005 A4: a subagent's report alone never qualifies a
paper for `read`):
- First pass: six Sonnet 5.5 readers, one per group, each reading its sources
  in full (groups B, C and D skimmed proofs or appendix tables; group F read
  the named repository files). Their output is kept verbatim in
  `manifests/sprint9_f78_reads/group_*.json`; this script never edits it.
- Coordinator (Claude, 2026-10-15): read each source's opening and every
  passage an assertion quotes, in its surrounding text. That is the
  `partial` read row. Boyd, Dhama, Butt and Tschirschwitz were also read in
  full by Claude on 2026-10-13, and Zhao (JMLR 2013) and Ushio in part.
- Every quote is verbatim in the local copy (`tests/test_f78_ceiling_reading.py`).

WHAT THE COORDINATOR CHANGED, each with its reason: DROPPED (two
assertions), VALUE_EDITS (whole values replaced) and REMOVE (sentences cut:
the readers' own inferences, mostly about fraud, which belong in the answer
document as inference, not in a sourced value).

CERTAINTY follows the store's GRADE convention: a theorem proved in the
paper starts HIGH; one empirical study starts LOW; a statement of what the
paper or code itself says starts HIGH as a document fact; the authors' own
untested or cited claims start LOW. Named moves are in CERTAINTY_OVERRIDES.

DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent: an
existing assertion, read row or applicability row is skipped. No network.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_assertion,  # noqa: E402
                          set_tier, sync_assertion)
from store.quotes import require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-15"
TAG = "Sprint 9 Task E, F78"
READS_DIR = ROOT / "manifests" / "sprint9_f78_reads"
GROUPS = "abcdefgh"
# Group G is Chen et al. 2025, read on 2026-10-16 once the team lead's hand
# download arrived (Manual Validation item 7); every other group, TODAY.
READ_ON = {"g": "2026-10-16", "h": "2026-10-16"}  # H: the JMLR 2016 paper (team lead Q6 = 1)


def read_on(group: str) -> str:
    return READ_ON.get(group, TODAY)

RECORD_ID = {"ishida-2023": "ishida-2023-performance-my-deep-network-too",
             "theisen-2021": "theisen-2021-evaluating-state-art-classification-models"}

CLONES = r"D:\Data\Harold\EvidenceBasedDB\GitHubRepos"
REPOS = {  # record id -> (clone folder, commit)
    "fraud-detection-handbook-fraud-detection-handbook-github-repo": ("fraud-detection-handbook", "81cf7d1"),
    "ibm-amlsim-github-repo": ("AMLSim", "7338a4b"),
    "namebrandon-sparkov-data-generation-github-repo": ("Sparkov_Data_Generation", "b5eb45c"),
    "ryotaushio-bayes-error-estimation-github-repo": ("bayes-error-estimation", "bb7ed54"),
    "lesleywheat-bayeserrorrate-estimatortester-github-repo": ("bayesErrorRate-estimatorTester", "db00042"),
    "ds3lab-feebee-github-repo": ("feebee", "6c6851d"),
}

# Read in full (or in part) by Claude on 2026-10-13, per the F78 card.
EARLIER_READS = {
    "boyd-2012-unachievable-region-precision-recall-space": ("full", "the whole paper"),
    "dhama-2026-fundamental-limits-fraud-detection-card": ("full", "the whole paper"),
    "butt-2026-bernoulli-cusum-bayes-optimal-detection": ("full", "the whole paper"),
    "tschirschwitz-2025-label-convergence-defining-upper-performance": ("full", "the whole paper"),
    "jmlr-2013-beyond-fano-s-inequality-bounds": ("partial", "in part, on 2026-10-13 (F78 card); pages not recorded"),
    "ushio-2026-practical-estimation-optimal-classification-error": (
        "partial", "in part, on 2026-10-13 (F78 card); pages not recorded"),
}

SUBAGENT_DETAIL = {
    "a": "first pass, the whole paper (Sonnet 5.5 reader, group A)",
    "b": "first pass, the whole paper; proof sections skimmed (Sonnet 5.5 reader, group B)",
    "c": "first pass, the whole paper; application proofs and appendix proofs skimmed (Sonnet 5.5 reader, group C)",
    "d": "first pass, the whole paper; appendix tables and experiment figures skimmed (Sonnet 5.5 reader, group D)",
    "e": "first pass, the whole paper, every page and appendix (Sonnet 5.5 reader, group E)",
    "g": "first pass, the whole paper, every page; the reference list not read (Sonnet 5.5 reader, group G)",
    "h": ("first pass, in part: sections 1 to 4 and 8 in full; appendix A.3 to A.5 by keyword (A.4's two-point part "
          "read); sections 5 to 7 and appendices B and C not read (Sonnet 5.5 reader, group H)"),
}
# Quotes the reader copied with a space lost from the extracted text (the
# PDF sets an en space before a theorem's parenthesis and a space before
# punctuation after a formula).
QUOTE_EDITS = {
    "chen-benchmark-accuracy": [("datasets,BG-BER", "datasets, BG-BER")],
    "chen-unbiased-oracle": [("Theorem 1(", "Theorem 1 (")],
    "chen-consistency-theorems": [("Theorem 2(", "Theorem 2 ("), ("Theorem 3(", "Theorem 3 (")],
    "chen-complexity-claim": [("O(n(log2 n)2),", "O(n(log2 n)2) ,"), ("O(n2).", "O(n2) ."),
                              ("is O(n), so", "is O(n) , so"), ("is O(n(log2 n)2).", "is O(n(log2 n)2) .")],
}
SUBAGENT_READER = "Claude Sonnet 5.5 (first-pass subagent)"
ABSENCE_NOTE = ("; any absence a value states (a test not run, a case not covered) rests on the first-pass full "
                "read, not on these passages")
COORDINATOR_DETAIL = ("the opening and every passage an assertion quotes, each with about 450 characters of "
                      "surrounding text; proofs, appendices and tables beyond those passages not read by the "
                      "coordinator" + ABSENCE_NOTE)
COORDINATOR_DETAIL_REREAD = ("re-read: the opening and every passage an assertion quotes, in context (the whole "
                             "paper was read by the same reader on 2026-10-13)")
COORDINATOR_DETAIL_REPO = "every quoted README or code passage with its surrounding text" + ABSENCE_NOTE
COORDINATOR_DETAIL_PAGE = "the whole saved page (the handbook's Foreword)"


def coordinator_detail(rid: str) -> str:
    """Review of 2026-10-15: one text for every source misdescribed the four
    papers read in full on 2026-10-13 and the one-page HTML Foreword."""
    if rid in REPOS:
        return COORDINATOR_DETAIL_REPO
    if EARLIER_READS.get(rid, ("",))[0] == "full":
        return COORDINATOR_DETAIL_REREAD
    if rid == "github-nd-reproducible-machine-learning-for-credit":
        return COORDINATOR_DETAIL_PAGE
    return COORDINATOR_DETAIL

DROPPED = {
    "theisen-table1-estimates-exceed-sota-some-corpora":
        "the reader's own row-by-row computation from Table 1, not a statement in the paper",
    "sparkov-ceiling-needs-profile-overlap":
        "the reader's inference about a ceiling; the code states no such thing",
}

VALUE_EDITS = {
    "butt-table4-n1-achieved-exceeds-ceiling": (
        "In Table IV the n=1 bin shows achieved F1 0.494 against a ceiling of 0.487, an efficiency of 101.6%. A "
        "measured result above the paper's Bayes-optimal ceiling means that ceiling, computed from estimated "
        "parameters, did not hold as a strict bound in that bin.",
        "the reader's list of possible causes is not in the paper"),
    "butt-abstract-explains-0.4-claimed": (
        "The paper claims the ceiling explains why unsupervised methods cluster near F1 of about 0.4 on "
        "Bitcoin-OTC (the body says 0.3 to 0.4).",
        "'cites no F1 values for those methods' could not be confirmed from the passages read; the comparison with "
        "dataset-wide F1 values (review, 2026-10-15) set unlike quantities against the per-node ceiling"),
    "tschirschwitz-bound-fails-with-dominant-convention": (
        "The authors say it is reasonable to assume that a model following a dominant labeling convention could "
        "exceed the convergence threshold, and that models may overfit to such a convention. The estimate also "
        "extrapolates from the repeated-label subset to the whole dataset and may suffer a domain gap.",
        "the reader's 'A model can exceed it' dropped the authors' hedge (review, 2026-10-15)"),
    "fdh-sim-scenario3-label-not-function-of-features": (
        "In the handbook simulator's scenario 3, which transactions of a compromised customer become fraud is a "
        "random sample of one third of them, and the chosen ones have their amounts multiplied by 5. The label is "
        "therefore not a fixed rule on the observable columns, and the code does not show that the Bayes error on "
        "those columns is zero.",
        "the reader wrote that the same features can carry different labels, but the chosen transactions' amounts "
        "change, so that wording is wrong"),
}

# Sentences or clauses cut from a reader's value: (exact text, replacement).
REMOVE = {
    # Review of 2026-10-15: a false sentence (the abstract does give the
    # attack scope, "for strategic attacks"), and three unlabeled
    # conclusions of the readers.
    "butt-0451-is-strategic-n2-only": [(
        " The abstract states it as 'this ceiling' for Bitcoin-OTC without the attack-type scope.", "")],
    "fano-bounds-weak-nonasymptotic-and-adaptive-limits": [(
        " So a Fano-derived limit is a weak-converse style bound, not a guaranteed tight ceiling at finite sample "
        "size.", "")],
    "toner-loss-floor-worked-example-40pct-symmetric": [(
        " A training loss below the floor therefore signals overfitting to noisy labels.", "")],
    "wheat-equal-class-sizes-no-imbalance-tested": [(
        ", so a rare-event BER near 0.2 percent was not covered", "")],
    "boyd-theorem2-min-aucpr-formula": [(
        "At pi = 0.1 it is about 0.05; it rises toward 0.31 at pi = 0.5.",
        "At pi = 0.1 it is about 0.05, and it increases as pi approaches 0.5.")],
    "wheat-samples-per-class-for-5pct-range": [(
        ", so the 5 percent target is wide relative to a BER near 0.2 percent (that last remark is an inference, "
        "not in the paper)", "")],
    "fano-binary-case-uses-exact-form-not-simplified": [
        (" A binary fraud label needs this exact form.", ""),
        ("; a skewed fraud prior is not covered by this remark", "")],
    "max-fscore-bounds-from-conditional-entropy": [(
        "roughly 2*beta/(1+beta) <= FSC <= (2-2*beta)/(2-beta) (formula read from garbled extraction, check "
        "against the PDF)", "2*beta/(1+beta) <= FSC <= (2-2*beta)/(2-beta)")],
    "no-mi-estimator-accurate-without-strong-assumptions": [
        ("(credited to McAllester and Stratos, ref [21])", "(the paper's reference [21])"),
        (" Implication for a ceiling check: an estimated MI between features and label is itself uncertain and is "
         "not a guaranteed bound.", "")],
    "cl-assumes-class-conditional-noise": [
        (" (for example, harder-to-label fraud cases being labeled wrong more often)", "")],
    "cl-threshold-design-targets-class-imbalance": [(
        " It does not test a rare-positive binary case such as 0.2 percent fraud, and it reports no precision or "
        "recall of error finding there.", "")],
    "cl-real-data-issues-are-not-all-label-errors": [(
        " So a CL flag count overstates pure label error and is not a direct estimate of an accuracy ceiling.", "")],
    "blanchard-solution-is-maximal-denoising": [(
        " If mutual irreducibility fails, the estimate can exceed the true noise; this last point is a reader "
        "consequence.", "")],
    "blanchard-ignoring-noise-biases-metrics-and-unequal-priors": [(
        " A 0.2 percent positive fraud set has very unequal priors, so this applies; the paper does not test it.",
        "")],
    "toner-label-noise-implies-risk-lower-bound": [("; an accuracy ceiling is a separate step the paper does not take",
                                                    "")],
    "toner-bound-needs-separable-clean-labels": [(
        " A fraud task with irreducible class overlap breaks this assumption, so the floor would then understate "
        "the true loss floor.", "")],
    "toner-bound-needs-noise-rate-and-balanced-classes-for-asymmetric": [(
        " The paper does not derive a bound for a heavily imbalanced case such as 0.2 percent positives.", "")],
    "jimenez-epistemic-estimates-are-lower-bounds-incomplete": [(
        " For the fraud question this means an ensemble or Bayesian estimate that says the model has little left "
        "to learn understates how far the model could still improve.", "")],
    "jimenez-completeness-check-needs-simulation-and-bias-check": [(
        " So a held-out check of the model, not the uncertainty method alone, is needed to learn whether the model "
        "is biased and can still improve.", "")],
    "thanh-theorem1-lower-bound-model-true-error": [("; the paper never uses the term Bayes error", "")],
    # Chen 2025 (group G, read 2026-10-16 after the team lead's download):
    # the reader's own critique of the proof, its reading of Table 4's
    # spread, a judgment on the validity criterion, and a relevance clause.
    "chen-unbiased-oracle": [(
        " The proof is a short chain of equalities that exchanges the infimum over classifiers with the expectation "
        "(Eq. 2) without a stated condition.", "")],
    "chen-synthetic-accuracy": [(
        ", which contradicts the authors' sentence that EF-BER has the smallest MSE across datasets.",
        ", while the text says EF-BER has the smallest MSE across the different datasets.")],
    "chen-unbiasedness-experiment": [(
        " The printed means for the three methods are close to each other (for example about 2.4E-03 to 2.6E-03 in "
        "one parameter setting and about 5.5E-03 to 6.4E-03 in the other), so the gaps are small relative to the "
        "printed standard deviations; the authors still call this better unbiasedness.", "")],
    "chen-benchmark-accuracy": [(
        " This criterion cannot detect an underestimate: an estimate far below the true BER also passes.", "")],
    "chen-imbalance-untested": [(
        ", so it gives no evidence for rare-positive (for example 0.2 percent) tabular problems", "")],
    # Chen, Guntuboyina and Zhang 2016 (group H, read 2026-10-16, Q6 = 1):
    # two clauses narrowed to what the quoted passages say.
    "cgz-nonuniform-zero-one-corollary7": [(
        "in the discrete uniform setting", "in the discrete setting with parameter and action sets {1, ..., N}")],
    "cgz-limitations-spikes": [(
        " The paper gives a partitioning fix (Remark 11) for densities bounded above.",
        " It names an ad hoc fix, described in Remark 11, for specific examples.")],
    "thanh-lower-bound-only-no-upper": [(
        " A lower bound says error is at least this high; it does not say whether error can still be reduced.", "")],
    "thanh-osyn-failure-conditions-generator-and-n": [(
        " Rare-event data such as fraud is where mode collapse and a small labeled set are risks (reader's "
        "inference, not stated by the authors).", "")],
    "allen-cardsim-label-is-naive-bayes-rank-cutoff": [(
        " In principle that makes a true ceiling computable by applying the generator's own scoring function, but "
        "the paper does not compute one (reader's inference).", "")],
    "allen-cardsim-no-ceiling-reported-best-model-numbers": [(
        " The paper does not say how close these are to the best possible score under its own label process.", "")],
    "allen-cardsim-independent-draws-no-sequence-signal": [(
        " A ceiling computed on CardSim therefore cannot reflect sequence or recency signal that real card fraud may "
        "carry.", "")],
    "allen-cardsim-some-fraud-parameters-assumed": [(
        " A ceiling computed on CardSim is a ceiling for an assumed process, not for real fraud.", "")],
    "altman-amlworld-labels-complete-by-construction": [(" The paper does not compute a best-achievable score from it.",
                                                         "")],
    "altman-baseline-f1-far-below-perfect-no-ceiling": [(
        " They do not say whether the remaining gap is learnable from the features given. The table numbers come "
        "from the page text, not from the quotes.", "")],
    "altman-account-ids-excluded-leakage-guard": [(
        " If IDs were included, scores on this benchmark could be inflated and any ceiling estimate would be "
        "contaminated (reader's inference).", "")],
    "altman-shared-graph-and-model-raise-f1": [(
        " This is evidence that information in the dataset (cross-bank visibility), not only model choice, sets "
        "achievable detection.", "")],
    "altman-synthetic-results-may-not-transfer": [(" A ceiling on these datasets is a ceiling for the simulated world.",
                                                   "")],
    "ostman-amlgentex-node-label-from-pattern-membership": [(" The paper does not compute a best-achievable score.",
                                                             "")],
    "ostman-amlgentex-difficulty-is-a-tuned-design-parameter": [(
        " Low scores on these datasets therefore reflect chosen generator settings, not a natural ceiling.", "")],
    "ostman-amlgentex-label-noise-injection": [(
        " This lets a user measure how label error limits performance against a known truth.", "")],
    "ostman-amlgentex-not-faithful-to-production-data": [(" Scores or ceilings on it do not carry over to real data.",
                                                          "")],
    "han-fusion-gain-over-best-single-model-modest": [(
        " This is an empirical measure of model-side headroom, not a ceiling.", "")],
    "han-ieee-cis-best-test-scores-random-split": [(" A temporal split would likely score differently (reader's "
                                                    "inference).", "")],
    "ding-power-law-fit-quality-by-family": [(
        " A high R2 on seven points does not by itself validate extrapolation to the floor (reader's inference).",
        "")],
    # The paper prints these sizes as powers of ten; the values say so.
    "ksg-mine-infonce-fail-dimension-thresholds-gaussian": [("N from 100 to 10,000", "N from 10^2 to 10^4")],
    "existing-mi-estimators-fail-above-100-dims-n2000": [("N = 2,000 samples", "N = 2 x 10^3 samples"),
                                                         ("d = 10 to 5,000;", "d = 10 to 5 x 10^3;"),
                                                         ("up to d = 5,000", "up to d = 5 x 10^3")],
    "amlsim-false-alerts-exist": [(
        " A ceiling on detection from structure alone depends on how separable those are from SAR sets, which the "
        "code does not compute.", "")],
}

THEOREM = "Started HIGH: a result proved in the paper, read in context"
EMPIRICAL = "Started LOW: an empirical result from one study. NOT upgraded"
DOC_FACT = "Started HIGH: a statement of what the source itself says (its method, scope or limits), read in context"
CODE_FACT = "Started HIGH: a statement of what the code does, read directly in the shallow clone at the named commit"
AUTHOR_CLAIM = "Started LOW: the authors' own claim or a claim they cite, not tested in the paper. NOT upgraded"

CERTAINTY_OVERRIDES = {
    "dhama-theorem9-regret-floor-form": (
        "moderate", THEOREM + ". DOWNGRADED one level: the proof is a sketch in a single-author preprint and the "
                              "constant c is unspecified"),
    "dhama-heterogeneity-jensen-worse": (
        "moderate", THEOREM + ". DOWNGRADED one level: one-paragraph proof sketches"),
    "fdh-sim-scenario3-label-not-function-of-features": (
        "moderate", CODE_FACT + ". DOWNGRADED one level: the Bayes-error part is the coordinator's inference "
                                "from the code, not stated by the source"),
    "amlsim-false-alerts-exist": ("high", CODE_FACT),
    # The reader downgraded this only because the formula came from garbled
    # extraction; the coordinator confirmed it in context on 2026-10-15.
    "max-fscore-bounds-from-conditional-entropy": (
        "high", THEOREM + ". The F-score interval was checked by the coordinator against the passage in context"),
    "tschirschwitz-bound-fails-with-dominant-convention": (
        "low", AUTHOR_CLAIM + ". Hedged by the authors ('it is reasonable to assume')"),
    # These two reader downgrades rest on a reason that no longer applies
    # once the reader's fraud remark was cut from the value.
    "blanchard-ignoring-noise-biases-metrics-and-unequal-priors": (
        "high", THEOREM + " (a short algebraic argument in Sec. 2)"),
}

# F46's nine ceiling facts (handoff 07-assertion-candidates-pending.md),
# each entered (by the assertions named), merged, or refused with the reason.
FACT_DISPOSITIONS = {
    "F-701": ("entered, corrected", ["wheat-samples-per-class-for-5pct-range", "wheat-requirement-depends-on-scenario",
                                     "wheat-equal-class-sizes-no-imbalance-tested"],
              "sample sizes right; 'collapses beyond 4 features' and 'equal priors' overstated"),
    "F-703": ("merged", ["auprc-not-generally-superior-under-imbalance"],
              "McDermott was already read and yields the same statement; nothing re-entered"),
    "F-704": ("not entered", [],
              "an absence claim resting on one second-hand search; the 33 sources read contain no closed-form AUPRC "
              "ceiling under label noise, but that is not a search of the literature"),
    "F-705": ("entered, corrected", ["infomax-can-yield-low-fscore-and-high-cost-risk",
                                     "max-fscore-bounds-from-conditional-entropy"],
              "proved; the paper calls its bounds sharp, not loose"),
    "F-706": ("entered, corrected", ["ksg-mine-infonce-fail-dimension-thresholds-gaussian"],
              "thresholds are Gowri et al. (NeurIPS 2024), one Gaussian simulation up to N = 10^4; the KSG bias formula "
              "is in neither MI paper and is not entered"),
    "F-707": ("entered in part", ["fdh-sim-scenario1-amount-over-220", "fdh-sim-scenario2-two-terminals-28-days",
                                  "fdh-sim-scenario3-random-third-times-five",
                                  "fdh-sim-scenario3-label-not-function-of-features"],
              "the scenario rules match the code; the zero-Bayes-error corollary is not stated by the source and does "
              "not hold on the observable columns"),
    "F-708": ("entered, corrected", ["dhama-theorem9-regret-floor-form", "dhama-abstract-four-in-denominator-vs-theorem"],
              "three impairments in the denominator, delay in the numerator, all under a square root"),
    "F-709": ("entered, corrected", ["ding-floor-c-is-model-and-config-specific", "ding-power-law-fit-quality-by-family",
                                     "ding-replicator-cv-b-0144-protocol-spread"],
              "c is a model-and-setup floor; the 127 were a cohort of partial replicators; 'preprocessing alone' "
              "overstated"),
    "F-710": ("refuted in detail", ["qksvm-classical-kernels-better-on-uci-tabular"],
              "the direct read of Kakavand found classical kernels significantly better on 6 of 7 datasets and a "
              "quantum kernel better on one; the second-hand 'none of 29 comparisons reached 0.05' does not stand"),
}

CLOSED = {  # the team lead's hand downloads (plan Q3 = 1); Chen 2025 arrived 2026-10-16 and is group G
    "te-sun-1994-generalizing-fano-inequality": "DOI:10.1109/18.335943",
}
# Team lead, 2026-10-16: no free copy of Han and Verdu; Q6 = 1, cover its
# content from free sources (Scarlett's (108) below, and the JMLR 2016
# paper as group H).
NOT_OBTAINABLE = {
    "te-sun-1994-generalizing-fano-inequality": (
        "2026-10-16 (Sprint 9 Task E, F78): NOT READ, not obtainable: the team lead has no free copy (Manual "
        "Validation item 7). Team lead Q6 = 1: its content is covered by Scarlett and Cevher 2019, equation (108) "
        "(scarlett-fano-data-processing-form-holds-for-any-prior), and by chen-2016-bayes-risk-lower-bounds "
        "(Corollary 5, a generalized Fano inequality for any prior)"),
}

SCARLETT = "scarlett-2019-introductory-guide-fano-s-inequality"
SCARLETT_ANCHOR = "Section 7.2, equation (108), and the 'Non-uniform priors' paragraph, pp. 35-36"
SCARLETT_READ = ("Claude", "2026-10-16", "partial",
                 "section 7.2 and the 'Non-uniform priors' paragraph (pp. 35-36), re-read for team lead Q6 = 1")
# Entered by the coordinator from that re-read (no first-pass reader): the
# free statement of the inequality Han and Verdu build on.
COORDINATOR_ASSERTIONS = [
    AssertionRecord(
        id="scarlett-fano-data-processing-form-holds-for-any-prior",
        value=("Scarlett and Cevher state that most generalizations of Fano's inequality rest on the data "
               "processing inequality for KL divergence: for any event E, the mutual information I(V; V-hat) is at "
               "least the binary KL divergence between the probability of E under the joint distribution of V and "
               "V-hat and its probability under the product of their marginals (equation (108)). That step makes "
               "no use of a uniform prior and holds in the non-uniform case, where the classical form's term can be "
               "too large to be useful. They credit Han and Verdu (their reference [57]) with weakening it into "
               "simpler lower bounds for non-uniform settings with discrete alphabets."),
        provenance=f"{SCARLETT}, {SCARLETT_ANCHOR}",
        citation_context="; ".join(f'"{q}" ({SCARLETT_ANCHOR})' for q in (
            "Most of these are not derived based on the most well-known proof of Theorem 1, but are instead based "
            "on an alternative proof via the data processing inequality for KL divergence",
            "is the binary KL divergence function",
            "may be too large for the bound to be useful",
            "the step (108) makes no use of uniformity, and continues to hold even in the non-uniform case",
            "In [57], this bound was further weakened to provide simpler lower bounds for non-uniform settings with "
            "discrete alphabets.")),
        evidence_tag="N/A", context="ml", certainty="high", certainty_reasons=DOC_FACT,
        fidelity="scoped", derivation="extracted", claim_type="positive", updated="2026-10-16",
        updated_reason=("2026-10-16 (Sprint 9 Task E, F78; team lead Q6 = 1): extracted by the coordinator from a "
                        "re-read of section 7.2 (pp. 35-36)")),
]


def load_groups() -> list[tuple[str, dict]]:
    out = []
    for g in GROUPS:
        data = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))
        out += [(g, p) for p in data["papers"]]
    return out


def edited_value(aid: str, value: str) -> str:
    if aid in VALUE_EDITS:
        return VALUE_EDITS[aid][0]
    for old, new in REMOVE.get(aid, []):
        if old not in value:
            raise ValueError(f"{aid}: the text to remove is not in the reader's value: {old[:60]!r}")
        value = value.replace(old, new)
    return re.sub(r"\s+", " ", value).strip()


def certainty(aid: str, kind: str, suggestion: str, is_repo: bool, reader_reason: str = "") -> tuple[str, str]:
    if aid in CERTAINTY_OVERRIDES:
        return CERTAINTY_OVERRIDES[aid]
    if kind == "proved":
        start = CODE_FACT if is_repo else THEOREM
        if suggestion in ("moderate", "low"):
            # Review of 2026-10-15: the first version returned HIGH for every
            # "proved" assertion, discarding the reader's stated downgrade.
            return (suggestion, f"{start}. DOWNGRADED to {suggestion} for the first-pass reader's stated reason, "
                                f"kept by the coordinator: {reader_reason.rstrip('.')}")
        return ("high", start)
    if kind == "estimated":
        return ("low", EMPIRICAL)
    if suggestion == "high":
        return ("high", DOC_FACT)
    return ("low", AUTHOR_CLAIM)


def local_file(group: str, paper: dict, rid: str) -> str:
    if rid in REPOS:
        return CLONES + "\\" + REPOS[rid][0]
    return paper["file"].replace("/", "\\")


def assertions() -> list[tuple[str, AssertionRecord, str]]:
    """(group, assertion, yielding record id) for every kept assertion."""
    out = []
    for g, p in load_groups():
        rid = RECORD_ID.get(p["record_id"], p["record_id"])
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            if aid in DROPPED:
                continue
            value = edited_value(aid, a["value"])
            cert, reasons = certainty(aid, a["kind"], a.get("certainty_suggestion", ""), rid in REPOS,
                                      a.get("certainty_reason", ""))
            anchor = a["anchor"]
            quotes = list(a["quotes"])
            for old, new in QUOTE_EDITS.get(aid, []):
                if not any(old in q for q in quotes):
                    raise ValueError(f"{aid}: the quote text to fix is not in the reader's quotes: {old!r}")
                quotes = [q.replace(old, new) for q in quotes]
            day = read_on(g)
            out.append((g, AssertionRecord(
                id=aid, value=value, provenance=f"{rid}, {anchor}",
                citation_context="; ".join(f'"{q}" ({anchor})' for q in quotes),
                evidence_tag="N/A", context=a.get("context") or "ml", certainty=cert, certainty_reasons=reasons,
                fidelity=a.get("fidelity") or "scoped", derivation="extracted", claim_type="positive",
                updated=day, updated_reason=f"{day} ({TAG}): extracted from {rid}; first-pass read by a subagent, "
                                            "every quoted passage read in context by the coordinator"), rid))
    return out


def sha_note(path: str, day: str = TODAY) -> str:
    data = Path(path).read_bytes()
    return f"Local copy SHA-256 {hashlib.sha256(data).hexdigest()}, {len(data):,} bytes, recorded {day} (F78)"


def apply_changes(conn) -> list[str]:
    check_quotes(conn)
    log = []
    groups = load_groups()
    for g, p in groups:
        day = read_on(g)
        rid = RECORD_ID.get(p["record_id"], p["record_id"])
        row = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
        if row is None:
            raise ValueError(f"{rid}: not in the store")
        access, evidence, tier = row
        local = local_file(g, p, rid)
        # (1) the local copy in `access`, with its hash (Task D's rule)
        if not recheck.local_paths(access or ""):
            conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (f"{access} | {local}", rid))
            note = (f"Shallow clone at commit {REPOS[rid][1]} in GitHubRepos, made {TODAY} (plan Q2 = 2)"
                    if rid in REPOS else sha_note(local, day))
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?",
                         (f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{day} ({TAG}): local copy added to access", day)
            log.append(f"access {rid} += {local}")
        # (2) applicability, `screened`'s obligation (ADR-0005 A2)
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            ctx = next((a.get("context") for a in p["assertions"] if a.get("context")), "ml")
            anchor = "README and core code" if rid in REPOS else "abstract"
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, f"{p['what_it_is'].rstrip('.')} -- {anchor}"))
            log.append(f"applic {rid} [{ctx}]")
        # (3) the reads
        have = {(r[0], r[1], r[2]) for r in conn.execute(
            "SELECT reader, read_on, extent FROM paper_reads WHERE record_id = ?", (rid,))}
        reads = []
        if rid in EARLIER_READS:
            extent, detail = EARLIER_READS[rid]
            reads.append(("Claude", "2026-10-13", extent, detail))
        sub_detail = (f"first pass: {p.get('partial_detail') or 'the whole source'} (Sonnet 5.5 reader, group F)"
                      if g == "f" else SUBAGENT_DETAIL[g])
        reads.append((SUBAGENT_READER, day, "subagent", sub_detail))
        reads.append(("Claude", day, "partial", coordinator_detail(rid)))
        for reader, on, extent, detail in reads:
            if (reader, on, extent) not in have:
                add_read(conn, rid, reader, on, extent, detail)
                log.append(f"read   {rid} [{reader}, {on}, {extent}]")
            elif (old := conn.execute("SELECT detail FROM paper_reads WHERE record_id = ? AND reader = ? AND read_on = ? "
                                      "AND extent = ?", (rid, reader, on, extent)).fetchone()[0]) != detail:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? AND read_on = ? "
                             "AND extent = ? AND detail = ?", (detail, rid, reader, on, extent, old))
                log.append(f"update {rid} read detail [{reader}, {on}, {extent}]")
        # (4) promotion
        if tier != "read":
            checked = (f"2026-10-13, Claude, read in full; {day} every quoted passage re-read in context"
                       if EARLIER_READS.get(rid, ("",))[0] == "full" else
                       f"{day}, Claude, read the opening and every quoted passage in context; first pass by a "
                       "subagent")
            set_tier(conn, rid, "read", checked_against_source=checked)
            log.append(f"tier   {rid} -> read")
    for g, a, rid in assertions():
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            # The script is the record's source: a correction reaches the
            # store, with the reason in updated_reason. Every field is
            # compared (Sprint 9 retrospective I4: the hand-named list here
            # left the quotes out, so a corrected quote never landed).
            day = read_on(g)
            why = "fresh-eyes review" if day == TODAY else "coordinator"
            changed = sync_assertion(conn, a, f"{day} ({TAG} {why}): corrected to the script's current text", day)
            log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
            continue
        insert_assertion(conn, a, yielded_by=rid)
        log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
    for rid, ident in CLOSED.items():
        reason = (f"{TODAY} ({TAG}): not read; no free copy ({ident}). On the team lead's hand-download list "
                  "(Sprint 9 plan Q3 = 1); read when the file arrives in Papers\\")
        current = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
        if "hand-download list" not in current:
            append_updated_reason(conn, rid, reason, TODAY)
            log.append(f"note   {rid} (awaiting hand download)")
    for rid, reason in NOT_OBTAINABLE.items():
        current = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0] or ""
        if "not obtainable" not in current:
            append_updated_reason(conn, rid, reason, "2026-10-16")
            log.append(f"note   {rid} (not obtainable; covered by free sources)")
    reader, on, extent, detail = SCARLETT_READ
    if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND reader = ? AND read_on = ? AND extent = ?",
                        (SCARLETT, reader, on, extent)).fetchone():
        add_read(conn, SCARLETT, reader, on, extent, detail)
        log.append(f"read   {SCARLETT} [{reader}, {on}, {extent}]")
    for a in COORDINATOR_ASSERTIONS:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_assertion(conn, a, yielded_by=SCARLETT)
            log.append(f"assert {a.id} <- {SCARLETT} [{a.certainty}] (coordinator)")
            continue
        changed = sync_assertion(conn, a, "2026-10-16 (Sprint 9 Task E, F78): corrected to the script's "
                                 "current text", "2026-10-16")
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def quote_source(paper: dict, a: dict) -> str:
    """The local file a reader's assertion quotes (its own quote_file, else the paper's)."""
    return (a.get("quote_file") or paper["file"]).split(" (")[0]


def check_quotes(conn) -> None:
    """Every quote verbatim in its local source, BEFORE anything is written
    (Sprint 9 retrospective I3); raises on the first assertion that fails."""
    sources = {a["id_suggestion"]: quote_source(p, a) for _, p in load_groups() for a in p["assertions"]}
    for _, a, _ in assertions():
        require_verbatim(a.id, a.citation_context, source_text(sources[a.id]))
    access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (SCARLETT,)).fetchone()[0]
    local = next(s.strip() for s in access.split("|") if s.strip().lower().endswith(".pdf"))
    for a in COORDINATOR_ASSERTIONS:
        require_verbatim(a.id, a.citation_context, source_text(local))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kept = assertions()  # validates every edit before anything is written
    ids = [a.id for _, a, _ in kept]
    if len(ids) != len(set(ids)):
        print("duplicate assertion ids")
        return 1
    if "--apply" not in args:
        for g, a, rid in kept:
            print(f"assert {a.id} <- {rid} [{a.certainty}]")
        print(f"{len(kept)} assertions; {len(DROPPED)} dropped. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F78 ceiling group read and entered")
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
