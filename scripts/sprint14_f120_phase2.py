#!/usr/bin/env python3
"""Sprint 14 Task D (F120): Phase 2's Sprint 29 results, by the inbound path.

Read at Phase 2 commit 6242b8a, the head of PR #63 (merged 2026-10-30) and the commit current when the task started.
Read only (F79), through `git show` on the team lead's local clone, which holds the commit; the plan named the GitHub
API because local refs then stopped at 22d16c3, and both give the same bytes. INTAKE_WORKFLOW.md section 56.

Two new source records, each a set of documents whose quotes are checked against their joined text:

- F166: `docs/phase2/algorithms/ULB_COMPARISON.md` and the seven algorithm documents beside it (one run,
  `f166_ulb_algorithms.json`). Four assertions.
- Sprint 29's results with no page of their own under `docs/phase2/`: `docs/sprints/SPRINT_29_VALIDATION.md` (V2, V4,
  V5, V7 and Decision D1) with the preregistered entries they ran under (`PREREGISTRATION_DRAFT.md`: F108's F156
  amendment, Experiment 3's F160 amendment, the F158 entry). Five assertions: F156, F158 (two), F160, F159.

And one stored value corrected: Phase 2 recomputed three of F108's plug-in ratios (F164), so
`f108-hgb-plugin-overstates-bayes-error-5-to-12-percent` changes; the F108 and F162 paper records are repointed at
6242b8a, with their earlier reads kept in the evidence. Every other stored value from those two documents is
verbatim at 6242b8a and confirmed by name in section 56. F167's PoC plan draft states no result: read, not entered.

Context by section 43's rule: `ml` for a classical method on a public data set or a simulator, `hsbc-2026` for a
result about the project's own CVQBoost lanes. No relation is linked (ADR-0004 A8 (b)); each reason names the stored
claims it bears on.

Every quote is checked by `require_verbatim`, with the value, against the blobs at COMMIT before anything is written.
DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_paper,  # noqa: E402
                          insert_verified_assertion, sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


f93 = _load("f93", "sprint11_f93_f108_ceiling.py")
f108 = _load("f108", "sprint13_f108_phase2.py")
intake = f93.intake

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-30"
TAG = "Sprint 14 Task D, F120"
PHASE2 = f93.PHASE2
REPO_URL = f93.REPO_URL
COMMIT = "6242b8a97e9658d783fc97ad06fe3a20e67e46a5"
OWN = ("Started HIGH: the consumer project's own measurement, read directly at Phase 2 commit 6242b8a (PR #63, "
       "merged 2026-10-30)")
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit 6242b8a, read directly on {TODAY}"
SYNC_REASON = (f"{TODAY} ({TAG}): corrected against the document at 6242b8a, where Phase 2 recomputed three of the "
               "ratios the stored value carried (F164; INTAKE_WORKFLOW.md section 56)")
NOT_LINKED = "not linked (ADR-0004 A8 (b))"

ALG = "docs/phase2/algorithms/"
# key -> (file, SHA-256 of the blob at COMMIT)
BLOBS = {
    "comparison": (ALG + "ULB_COMPARISON.md", "075c7f4dcc04026820cdcaf58d8a8dff7bbf4455fb4168bb6088e3f9a70e5a99"),
    "catboost": (ALG + "ULB_CATBOOST.md", "f65feb78bb93e97f23977d758253dcc3a1b382cb13923c5084f955c164c780c3"),
    "lightgbm": (ALG + "ULB_LIGHTGBM.md", "367d89ce41b871fea0d71527f1c104295caa2ab8a1c6e82b8b997e28b93662c0"),
    "xgboost": (ALG + "ULB_XGBOOST.md", "813557945c1ce590d5d0fab07f258788a8fb8f294b66f491e05a82762a615bab"),
    "hgb": (ALG + "ULB_HGB.md", "42b0c841a6cf8c353d25b24c27f2b2e6398e350f14833061908b1abbe6628681"),
    "proxy": (ALG + "ULB_CVQBOOST_PROXY.md", "f70ec353bc62f2d248dc8fd4e7f8b7432ed9d82cc935384193471857fdac0c43"),
    "svm": (ALG + "ULB_SVM.md", "3f24aab1f16e53d8bb2c14d3ca23c07ae9533f3f594b074a7550627b8a261e00"),
    "logistic": (ALG + "ULB_LOGISTIC_REGRESSION.md",
                 "6b8dcd6493ec7a190ec8ab84cff5820871296a3315e270809de582606c0891b0"),
    "validation": ("docs/sprints/SPRINT_29_VALIDATION.md",
                   "5ec287aec779ac609db9521aaff03900bb392676215c186c88c9f6a3f2d1fdd4"),
    "prereg": ("experiments/phase2/PREREGISTRATION_DRAFT.md",
               "d9279360c57fc90698453e3c8f8ebfbb844701c736ea4f5d7532f2906b835890"),
    "f108": ("docs/phase2/F108_CEILING_VALIDATION.md",
             "f3a7d4833dd87bb07a397a133da1e94154055a57e2d3a0d5df59216e040ed636"),
    "f162": ("docs/phase2/F162_IN_POCKET.md", "780d7f4b5033ce83756bd9e7534d629439271369d5b1bcb910f467daf2c6b06c"),
}
# The run files the documents report, read to check the headline figures (tests/test_sprint14_f120.py).
RESULTS = {
    "f156": ("experiments/phase2/results/f156_hp_bound.json",
             "ee6aa43c2549a873215a12270573b6edcedd3ef221e7a42f9cf58007c0134d23"),
    "f158": ("experiments/phase2/results/f158_fraud_types.json",
             "1e60f3fd4f90b85fa85c11cb766e6d9dd70a457f4eabe8a403d3dbea6d132238"),
    "f159": ("experiments/phase2/results/f159_parallel_pool.json",
             "964e3f1c8d474822030732e9f3c881924dd4bb2b7a90222c386576aefd654b56"),
    "f160": ("experiments/phase2/results/f160_room_ieee.json",
             "15ee3e5d9ce2fcb0a17dd2bb0382f877badd07b5803e69c57679ec03dcac373a"),
    "f166": ("experiments/phase2/results/f166_ulb_algorithms.json",
             "f00511e9bd9c71684f3526e3ab17618c87c1a4a2daff6266448f7ae6b47c1f91"),
}
SETS = {
    "set": ["comparison", "catboost", "lightgbm", "xgboost", "hgb", "proxy", "svm", "logistic"],
    "results": ["validation", "prereg"],
}
SET_ID = "hsbc-qfraud-phase2-f166-sprint29-ulb-algorithms"
RES_ID = "hsbc-qfraud-phase2-sprint29-results"


def blob(path: str) -> bytes:
    """A file exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{path}"], capture_output=True, check=True).stdout


def source_bytes(key: str) -> bytes:
    return blob(BLOBS[key][0])


def set_text(name: str) -> str:
    """The set's documents joined, markdown bold dropped; a quote names its document in its anchor."""
    return plain(" ".join(source_bytes(k).decode("utf-8").replace("**", "") for k in SETS[name]))


def _shas(keys: list[str]) -> str:
    return "; ".join(f"{BLOBS[k][0]} {BLOBS[k][1]}" for k in keys)


def set_entry() -> dict:
    file = BLOBS["comparison"][0]
    return {
        "id": SET_ID, "kind": "reference", "context": "hsbc-2026", "tier": "read",
        "title": "ULB: seven algorithms compared (F166)",
        "citation": (f'hsbc-qfraud-phase2, "ULB: seven algorithms compared (F166)," {file} and the seven algorithm '
                     "documents beside it, commit 3846b20, 2026-10-30; Sprint 29 Task F (#69) (hand-transcribed from "
                     "the documents' headings and Card lines and the repository's git log)"),
        "transcribed_from": 'the heading "ULB: seven algorithms compared (F166)" and the line "F166 (Sprint 29 Task F, '
                            '#69), the ULB part of F157"',
        "disposition": ("Reference: the HSBC Phase 2 project's best achievable result per algorithm on ULB, seven "
                        "algorithms tuned under one preregistered protocol over ten seeds, with the paired tests"),
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 per document at Phase 2 commit 6242b8a (the last commit to touch them is "
                     f"3846b20): {_shas(SETS['set'])}. Run: {RESULTS['f166'][0]} (blob SHA-256 {RESULTS['f166'][1]}), "
                     "seeds 42-51, evidence tag SIM, zero metered seconds. The private repository's URL is the "
                     "citation's pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "found_via": "read from Phase 2 at Sprint 14 Phase 1.2, 2026-10-29 (carded as F120)",
        "cited_as": file,
        "checked_against_source": f"{TODAY}, Claude, read all eight documents in full at commit 6242b8a via git show",
        "reads": [["Claude", TODAY, "full", "ULB_COMPARISON.md and the seven algorithm documents, each in full, at "
                                            "commit 6242b8a"]],
        "applicability": [
            ["hsbc-2026", "the CVQBoost proxy against six classical algorithms on ULB -- BLUF and Adjacent pairs"],
            ["ml", "six classical algorithms tuned on ULB -- each algorithm document's Configurations tried"],
        ],
        "updated_reason": f"{TODAY}: added by scripts/sprint14_f120_phase2.py ({TAG}); read in full",
    }


def results_entry() -> dict:
    file = BLOBS["validation"][0]
    pre = BLOBS["prereg"][0]
    return {
        "id": RES_ID, "kind": "reference", "context": "hsbc-2026", "tier": "read",
        "title": "Sprint 29 Manual Validation, with the preregistered entries it reports",
        "citation": (f'hsbc-qfraud-phase2, "Sprint 29 Manual Validation," {file}, commit 50cbb1f, 2026-10-28, and '
                     f"{pre} section 6, commit 15775da, 2026-10-27 (hand-transcribed from the documents' headings "
                     "and the repository's git log)"),
        "transcribed_from": 'the heading "Sprint 29 Manual Validation" and the entry headings "F158: fraud types, '
                            'per-type detectors against one model" and "Amendment, 2026-10-26 (Sprint 29 Task D, F156)"',
        "disposition": ("Reference: the HSBC Phase 2 project's Sprint 29 results with no page of their own (F156's "
                        "Henze-Penrose bound, F158's fraud types, F159's parallel pool build, F160's room check on "
                        "IEEE-CIS), with the preregistered entries they ran under"),
        "access": (f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file} | "
                   f"{REPO_URL}/blob/{COMMIT}/{pre}"),
        "evidence": (f"Committed blob SHA-256 per document at Phase 2 commit 6242b8a: {_shas(SETS['results'])}. Runs: "
                     + "; ".join(f"{RESULTS[k][0]} (blob SHA-256 {RESULTS[k][1]})"
                                 for k in ("f156", "f158", "f159", "f160"))
                     + ". Evidence tag SIM, zero metered seconds. The private repository's URL is the citation's "
                     "pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "found_via": "read from Phase 2 at Sprint 14 Phase 1.2, 2026-10-29 (carded as F120)",
        "cited_as": file,
        "checked_against_source": (f"{TODAY}, Claude, read the validation record in full and the three entries in "
                                   "full at commit 6242b8a via git show; the headline figures checked against the run "
                                   "files"),
        "reads": [["Claude", TODAY, "full", "SPRINT_29_VALIDATION.md in full, and PREREGISTRATION_DRAFT.md's F156 "
                                            "amendment, Experiment 3's F160 amendment and the F158 entry in full, at "
                                            "commit 6242b8a"]],
        "applicability": [
            ["hsbc-2026", "the project's own CVQBoost and Experiment 3 results -- V2, V5 and V7 step 3"],
            ["ml", "a ceiling estimator and per-type detectors on a fraud simulator -- V4 and V7 step 1"],
        ],
        "updated_reason": f"{TODAY}: added by scripts/sprint14_f120_phase2.py ({TAG}); read in full",
    }


def A(src: str, **kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "SIM")
    kw.setdefault("context", "hsbc-2026")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    kw["provenance"] = f"{src}, {kw['provenance']}"
    return AssertionRecord(**kw)


F166 = [
    A(SET_ID, id="f166-ulb-tuned-boosting-leads-proxy-fifth",
      value=("On deduplicated ULB (a 60/20/20 split, ten seeds 42-51), seven algorithms each tuned on validation "
             "over configurations named before any score rank by mean test AUPRC: CatBoost 0.8329, LightGBM 0.8270, "
             "XGBoost 0.8229, HGB 0.8124, Phase 2's CVQBoost proxy 0.7925, a linear SVM 0.7419 and logistic "
             "regression 0.7270. Of the six adjacent pairs, two differ reliably under the entry's exact Wilcoxon test "
             "at Bonferroni 0.05 / 6: the proxy above the SVM and the SVM above logistic regression. The order among "
             "the four boosting libraries and the proxy is not established; HGB against the proxy (mean difference "
             "0.0198, p 0.0098) is above the Bonferroni level. Phase 2's limits: one protocol and one grid per "
             "algorithm, so each figure is the best of the configurations named, not the best possible; device "
             "lanes, QSVM and QNN are outside it"),
      provenance="ULB_COMPARISON.md BLUF and Adjacent pairs, each algorithm document's BLUF and Limits",
      citation_context=('"Over 10 seeds (42-51), the four gradient-boosting libraries lead by mean test AUPRC, the '
                        'CVQBoost proxy is next, then the linear SVM and logistic regression." (ULB_COMPARISON.md, '
                        'BLUF); "`data.stratified_split` (60/20/20)" (each document, Data); "CatBoost reaches a mean '
                        'test AUPRC of 0.8329" (ULB_CATBOOST.md, BLUF); "LightGBM reaches a mean test AUPRC of 0.8270" '
                        '(ULB_LIGHTGBM.md, BLUF); "XGBoost reaches a mean test AUPRC of 0.8229" (ULB_XGBOOST.md, '
                        'BLUF); "HGB reaches a mean test AUPRC of 0.8124" (ULB_HGB.md, BLUF); "CVQBoost proxy reaches '
                        'a mean test AUPRC of 0.7925" (ULB_CVQBOOST_PROXY.md, BLUF); "SVM reaches a mean test AUPRC '
                        'of 0.7419" (ULB_SVM.md, BLUF); "Logistic regression reaches a mean test AUPRC of 0.7270" '
                        '(ULB_LOGISTIC_REGRESSION.md, BLUF); "the exact two-sided Wilcoxon signed-rank test on '
                        'per-seed AUPRC differences is primary, at Bonferroni 0.05 / 6." (ULB_COMPARISON.md, Adjacent '
                        'pairs); "Of the six adjacent pairs, 2 differ reliably under the entry\'s test: CVQBoost proxy '
                        'above SVM; SVM above logistic regression." (ULB_COMPARISON.md, BLUF); "so the order among '
                        'CatBoost, LightGBM, XGBoost, HGB and the proxy is not established." (ULB_COMPARISON.md, '
                        'BLUF); "HGB against CVQBoost proxy: mean difference 0.0198, Wilcoxon p 0.0098; reading: no '
                        'reliable difference" (ULB_COMPARISON.md, Adjacent pairs); "One protocol and one grid per '
                        'algorithm. A larger grid may do better; this is the best of the configurations named in the '
                        'entry, not the best possible." (each document, Limits); "Device lanes (CVQBoost on hardware, '
                        'QSVM) and QNN are outside this part of F157." (each document, Limits)'),
      certainty_reasons=(OWN + ". HIGH for the measured ranking and the paired tests under the entry's rule. Scope: "
                         "one data set, ten seeds, one grid per algorithm, the proxy and not Dirac hardware. Bears on "
                         "f151-cvqboost-proxy-below-stable-hgb-on-ulb (the F130 proxy variants reliably below the "
                         "stable HGB, on 13 features and five seeds): here a different, tuned proxy is below HGB by "
                         "0.0198 but not reliably at the family level, so the two can both hold; " + NOT_LINKED)),
    A(SET_ID, id="f166-ulb-cvqboost-proxy-largest-train-test-gap",
      value=("In Phase 2's tuned ULB comparison (ten seeds, 42-51), its CVQBoost proxy chose the full configuration "
             "(k 17, order 3) of its three on every seed and reached mean test AUPRC 0.7925 (95% t interval 0.7705 to "
             "0.8146), fifth of seven. Its mean train-test AUPRC gap was the largest of the seven, 0.2075, against "
             "0.0190 for the linear SVM and 0.0291 for logistic regression, the smallest. The full configuration's "
             "pool came from F159's 32-worker parallel build, which F159 showed gives the same pool as the serial "
             "build"),
      provenance="ULB_CVQBOOST_PROXY.md BLUF and Configurations tried, ULB_COMPARISON.md Notes",
      citation_context=('"Over 10 seeds (42-51)" (ULB_COMPARISON.md, BLUF); "The full configuration (k 17, order 3) '
                        'was chosen on every seed." (ULB_CVQBOOST_PROXY.md, Configurations tried); "3 configurations, '
                        'named in the entry before any score." (ULB_CVQBOOST_PROXY.md, Configurations tried); '
                        '"CVQBoost proxy reaches a mean test AUPRC of 0.7925 (95% t interval 0.7705 to 0.8146). It is '
                        'number 5 of 7 by mean test AUPRC" (ULB_CVQBOOST_PROXY.md, BLUF); "The proxy\'s train-test '
                        'AUPRC gap has the largest mean (0.2075); the SVM\'s and logistic regression\'s are the '
                        'smallest (0.0190 and 0.0291)." (ULB_COMPARISON.md, Notes); "Its pool was built with F159\'s '
                        'parallel build (32 workers), which F159 showed gives the same pool as the serial build" '
                        '(ULB_CVQBOOST_PROXY.md, Configurations tried)'),
      certainty_reasons=(OWN + ". HIGH for the measured gap and choice. Scope: one data set, ten seeds, the proxy "
                         "and not Dirac hardware. Phase 2 does not say why the gap is largest, so the value does not "
                         "either")),
    A(SET_ID, id="f166-ulb-recall-at-alert-budget-spread-narrower-than-auprc",
      value=("At a 0.5% alert budget, the seven tuned algorithms of Phase 2's ULB comparison caught on average 0.8305 "
             "to 0.8589 of the test frauds, a narrower spread than their mean test AUPRC (0.7270 to 0.8329). The "
             "entry's paired test is on AUPRC only, so no recall difference is tested"),
      provenance="ULB_COMPARISON.md Notes and Adjacent pairs",
      citation_context=('"At the 0.5% alert budget, mean recall on the test fold lies between 0.8305 and 0.8589 for '
                        'all seven, a narrower spread than AUPRC\'s." (ULB_COMPARISON.md, Notes); "CatBoost reaches a '
                        'mean test AUPRC of 0.8329" (ULB_CATBOOST.md, BLUF); "Logistic regression reaches a mean test '
                        'AUPRC of 0.7270" (ULB_LOGISTIC_REGRESSION.md, BLUF); "the exact two-sided Wilcoxon '
                        'signed-rank test on per-seed AUPRC differences is primary" (ULB_COMPARISON.md, Adjacent '
                        'pairs)'),
      certainty_reasons=(OWN + ". HIGH for the measured spread, which Phase 2 reports as a note, untested. Scope: "
                         "one data set, ten seeds. Bears on f154-no-stored-model-better-on-a-ulb-subset (stored ULB "
                         "models that catch nearly the same frauds); " + NOT_LINKED + ": a different measure")),
    A(SET_ID, id="f166-ulb-tuning-chose-unweighted-linear-and-l2-hgb",
      context="ml",
      value=("On deduplicated ULB, tuned on validation by Phase 2 over ten seeds (42-51): logistic regression and a "
             "linear SVM chose class_weight balanced on no seed; HGB chose l2_regularization 1.0 on every seed (7, 1 "
             "and 2 seeds across three learning-rate and leaf settings); and an RBF SVM, fit on a stratified "
             "20,000-row subsample because the kernel is quadratic in rows, beat the linear SVM on validation on 2 of "
             "10 seeds, so the lane kept the linear form. Each validation fold holds about 95 frauds, so validation "
             "AUPRC is noisy"),
      provenance="ULB_LOGISTIC_REGRESSION.md, ULB_SVM.md and ULB_HGB.md, Configurations tried and Limits",
      citation_context=('"Over 10 seeds (42-51)" (ULB_COMPARISON.md, BLUF); "No seed chose `class_weight` balanced." '
                        '(ULB_LOGISTIC_REGRESSION.md and ULB_SVM.md, Configurations tried); "l2_regularization 1.0, '
                        'learning_rate 0.05, max_leaf_nodes 31 | 7 of 10" (ULB_HGB.md, Configurations tried); '
                        '"l2_regularization 1.0, learning_rate 0.1, max_leaf_nodes 15 | 1 of 10" (ULB_HGB.md, '
                        'Configurations tried); "l2_regularization 1.0, learning_rate 0.1, max_leaf_nodes 31 | 2 of '
                        '10" (ULB_HGB.md, Configurations tried); "on a stratified 20,000-row subsample of the training '
                        'fold, because an RBF kernel on the full fold is quadratic in rows" (ULB_SVM.md, Alternative '
                        'tried); "It did so on 2 of 10 seeds, so the lane keeps the linear form." (ULB_SVM.md, '
                        'Alternative tried, markdown bold dropped); "Each validation fold holds about 95 frauds, so '
                        'validation AUPRC is noisy" (each document, Limits)'),
      certainty_reasons=(OWN + ". HIGH for the recorded choices. Scope: one data set, ten seeds, one grid. "
                         "Consistent with f151-hgb-default-l2-zero-unstable-at-extreme-imbalance (l2 0 chosen on no "
                         "seed here), which used 13 features and five seeds; " + NOT_LINKED + ": a tuning choice does "
                         "not confirm the instability whole")),
]

RES = [
    A(RES_ID, id="f156-henze-penrose-bound-fails-on-f108-simulator",
      context="ml",
      value=("Phase 2 tested the Henze-Penrose bound (Berisha, Wisler, Hero and Spanias, 2016) as a ceiling "
             "estimator on F108's fraud simulator, on an exact minimum spanning tree over a stratified 60,000-row "
             "subsample. On the main arm the interval contained the true Bayes error on 2 of 5 seeds and was narrow "
             "on 0 of 5, where the rule needs 4 of 5; where it missed, its lower end sat just above the true value. "
             "Phase 2's entry had shown before the run that the two terms cannot both hold for this bound there: "
             "the width is at least about 0.0030 against a cap of about 0.0012-0.0013. So F114 has no validated "
             "ceiling estimator and stays blocked; the team lead chose on 2026-10-28 to card F108's second named "
             "candidate, an HGB set for extreme imbalance"),
      provenance="SPRINT_29_VALIDATION.md V4 and Decision D1; PREREGISTRATION_DRAFT.md, F108's F156 amendment",
      citation_context=('"the Henze-Penrose bound of Berisha, Wisler, Hero and Spanias (IEEE TSP 2016" '
                        '(PREREGISTRATION_DRAFT.md, F156 amendment); "On a Euclidean minimum spanning tree of the '
                        'pooled rows" (PREREGISTRATION_DRAFT.md, F156 amendment); "the tree is built on a stratified '
                        'random subsample of the training rows that keeps the class share" (PREREGISTRATION_DRAFT.md, '
                        'F156 amendment); "Size: 60,000 rows, drawn with the seed." (PREREGISTRATION_DRAFT.md, F156 '
                        'amendment); "The tree is exact" (PREREGISTRATION_DRAFT.md, F156 amendment); "On the main arm '
                        'the interval contained the true Bayes error on 2 of 5 seeds and was narrow on 0 of 5; the '
                        'rule needs 4 of 5." (SPRINT_29_VALIDATION.md, V4); "Where it missed, the lower end sat just '
                        'above the true value." (SPRINT_29_VALIDATION.md, V4); "The entry had shown before the run '
                        'that both terms cannot hold together here." (SPRINT_29_VALIDATION.md, V4); "so the width is '
                        'at least about 0.0030; the width cap is about 0.0012-0.0013." (PREREGISTRATION_DRAFT.md, F156 '
                        'amendment); "F114 stays blocked." (SPRINT_29_VALIDATION.md, V4, markdown bold dropped); '
                        '"Add a card for F108\'s second named candidate, an HGB set for extreme imbalance" '
                        '(SPRINT_29_VALIDATION.md, Decision D1, option 2); "Answer (team lead, 2026-10-28): 2." '
                        '(SPRINT_29_VALIDATION.md, Decision D1, markdown bold dropped)'),
      certainty_reasons=(OWN + ". HIGH for the measured counts, which the run file's summary holds (contains 2, "
                         "narrow 0 of 5). Scope: one simulator, five seeds, the main arm deciding. Bears on "
                         "f108-no-ceiling-method-recovered-known-ceiling and f114-calibrated-plugin-misses-known-ceiling "
                         "(a fifth and sixth method that miss the same known ceiling); " + NOT_LINKED + ": a different "
                         "estimator, which confirms neither whole")),
    A(RES_ID, id="f158-per-type-cascade-below-one-model-on-simulator",
      context="ml",
      value=("On F108's fraud simulator (seeds 42-49), where every fraud is of type S2 (a compromised terminal), S3 "
             "(a compromised customer, amount x5) or both, a cascade of one detector per type, scoring a row by the "
             "larger of the two probabilities, caught fewer test frauds within a 0.5% alert budget than one model "
             "trained on all fraud: recall difference mean -0.069, 95% interval -0.126 to -0.013, so the cascade is "
             "below one model. A reference with the type labels shuffled among the training frauds was also below, "
             "by less. Phase 2's step on real data (clustering ULB and IEEE-CIS) did not run, its condition being a "
             "cascade above. Phase 2 had named the risk before the run: gradient boosting already concentrates on "
             "hard rows"),
      provenance="SPRINT_29_VALIDATION.md V7; PREREGISTRATION_DRAFT.md, the F158 entry",
      citation_context=('"S2 (a compromised terminal) and S3 (a compromised customer, amount x5)" '
                        '(PREREGISTRATION_DRAFT.md, F158, Data); "Every fraud is S2, S3 or both" '
                        '(PREREGISTRATION_DRAFT.md, F158, Data); "one detector with target S2, one with target S3; a '
                        'row\'s score is the larger of the two probabilities" (PREREGISTRATION_DRAFT.md, F158, '
                        'Models); "Step 1 (simulator, seeds 42-49): recall at the 0.5% budget, cascade minus single '
                        'model, mean -0.069, 95% interval -0.126 to -0.013: the cascade is below one model." '
                        '(SPRINT_29_VALIDATION.md, V7, markdown bold dropped); "the cascade with the type labels '
                        'shuffled among the training frauds" (PREREGISTRATION_DRAFT.md, F158, Models); "The '
                        'shuffled-type reference was also below, by less." (SPRINT_29_VALIDATION.md, V7); "Step 2 (ULB '
                        'and IEEE-CIS clustering)" (PREREGISTRATION_DRAFT.md, F158, markdown bold dropped); "Step 2 '
                        'did not run (its condition is a cascade above)." (SPRINT_29_VALIDATION.md, V7); "Gradient '
                        'boosting already concentrates on hard rows, so the gain may be small (the card\'s named '
                        'risk)." (PREREGISTRATION_DRAFT.md, F158, Hypothesis and prediction)'),
      certainty_reasons=(OWN + ". HIGH for the measured difference under the entry's test (the run file reads "
                         "\"below\", Wilcoxon p 0.0156, interval excluding zero). Scope: one simulator with two fraud "
                         "types, eight seeds; why the cascade is below is not tested")),
    A(RES_ID, id="f158-ulb-frauds-missed-by-every-stored-model-near-zero",
      value=("On ULB, 106 of 950 (seed, test fraud) pairs, 95 test frauds on each of seeds 42-51, were missed at the "
             "0.5% budget by all twelve on-split model families of Phase 2's stored set (a thirteenth is off-split and "
             "left out); on V1-V8 these frauds sit near zero, where the caught frauds do not. A fraud on more than "
             "one seed's test fold counts once per seed, and the number of distinct frauds is not recorded. "
             "Descriptive: no test"),
      provenance="SPRINT_29_VALIDATION.md V7; PREREGISTRATION_DRAFT.md, the F158 entry, Step 3",
      citation_context=('"106 of 950 (seed, test fraud) pairs, 95 test frauds on each of seeds 42-51, were missed by '
                        'all twelve on-split stored model families (a thirteenth is off-split and left out); on V1-V8 '
                        'they sit near zero, where the caught frauds do not." (SPRINT_29_VALIDATION.md, V7); "A fraud '
                        'on more than one seed\'s test fold counts once per seed; the number of distinct frauds is not '
                        'recorded." (SPRINT_29_VALIDATION.md, V7); "the ULB test frauds that every model in F154\'s '
                        'stored set misses at the 0.5% budget" (PREREGISTRATION_DRAFT.md, F158, Step 3); "No test." '
                        '(PREREGISTRATION_DRAFT.md, F158, Step 3)'),
      certainty_reasons=(OWN + ". HIGH for the measured count, which the run file holds (106 missed, 844 caught). "
                         "Scope: one data set, Phase 2's stored predictions. Bears on "
                         "f154-no-stored-model-better-on-a-ulb-subset (the same stored models catch nearly the same "
                         "frauds); " + NOT_LINKED + ": a description, not that test")),
    A(RES_ID, id="f160-exp3-room-check-passes-on-ieee-cis",
      value=("Phase 2's Experiment 3 room check (F160) passes on IEEE-CIS. Its reason, stated before the run and "
             "inferred: on ULB (fraud rate about 0.17%) the room is about 0.007, below the 0.01 the falsifier "
             "requires; on IEEE-CIS (about 3.5%) it is about 0.14. A positive control passed first. On IEEE-CIS "
             "(seeds 42-44, 60 and 136 variables), greedy selection ended 0.096-0.098 above the floor on every "
             "instance (the largest gap 0.0985), against the 0.01 rule, and F104's resolution gate passes; the "
             "guide-based resolution check fails on every instance, as on the control, and the falsifier needs both "
             "checks to fail, so it does not fire. SCIP stopped at its 300 s cap on every instance without beating "
             "greedy; its dual bound puts the true optimum between greedy and about 0.08-0.18 below it, so no solver "
             "has yet been shown to beat greedy. The design reopens on IEEE-CIS; F25 stays on HOLD for its own "
             "reason (F102 not filed)"),
      provenance="SPRINT_29_VALIDATION.md V5; PREREGISTRATION_DRAFT.md, Experiment 3's F160 amendment",
      citation_context=('"Why another dataset, stated before any run (inferred)." (PREREGISTRATION_DRAFT.md, F160 '
                        'amendment, markdown bold dropped); "On ULB (fraud rate about 0.17%) that is about 0.007, '
                        'below the 0.01 the falsifier requires" (PREREGISTRATION_DRAFT.md, F160 amendment); "On '
                        'IEEE-CIS (about 3.5%) it is about 0.14, so the rule can pass there in principle." '
                        '(PREREGISTRATION_DRAFT.md, F160 amendment); "The positive control passed first." '
                        '(SPRINT_29_VALIDATION.md, V5); "On IEEE-CIS (seeds 42-44, 60 and 136 variables), greedy ends '
                        '0.096-0.098 above the floor on every instance (corrected 2026-10-28 from 0.096-0.099: the '
                        'largest gap is 0.0985), against the 0.01 rule; F104\'s resolution gate passes." '
                        '(SPRINT_29_VALIDATION.md, V5); "The guide-based resolution check fails on every instance, as '
                        'it does on the control; the falsifier needs both checks to fail, so it does not fire." '
                        '(SPRINT_29_VALIDATION.md, V5); "SCIP stopped at its 300 s cap on every instance without '
                        'beating greedy." (SPRINT_29_VALIDATION.md, V5, Caveat); "Its dual bound puts the true optimum '
                        'between greedy and about 0.08-0.18 below it." (SPRINT_29_VALIDATION.md, V5); "No solver has '
                        'yet been shown to beat greedy." (SPRINT_29_VALIDATION.md, V5); "F25\'s card records the '
                        'reopened design." (SPRINT_29_VALIDATION.md, V5); "F25\'s HOLD reason (F102 not filed) '
                        'stands." (SPRINT_29_VALIDATION.md, V5)'),
      certainty_reasons=(OWN + ". HIGH for the measured gaps and checks; why the room differs between the data sets "
                         "is Phase 2's inference, attributed as such. Scope: three seeds, two instance sizes, one "
                         "fold, the proxy formulation. Bears on f153-learner-selection-formulation-fails-its-falsifier "
                         "(the same design failing on ULB, where SCIP also stopped at its cap without improving on "
                         "greedy): both hold, on different data sets; " + NOT_LINKED)),
    A(RES_ID, id="f159-parallel-pool-build-equals-serial-and-is-faster",
      value=("Phase 2's parallel build of its CVQBoost proxy's weak-learner pool on ULB (F159) gave the same pool as "
             "the serial build on the validation rows at all four row fractions and all five worker counts. At full "
             "ULB rows the serial build took 730.3 s and 32 workers 45.8 s; 16 workers were 11.24 times faster than "
             "serial, and the longest single learner took 2.0 s. Per-learner time rose with the worker count (summed "
             "learner time 738.6 s at 1 worker, 1101.6 s at 32); what takes the rest of the wall time is not "
             "measured. The first run stopped with a MemoryError at 32 workers on the 0.5 fraction and its resume "
             "hung for 9 hours; the cause is unverified, and each parallel build is now stopped after 2 times its "
             "fraction's serial time"),
      provenance="SPRINT_29_VALIDATION.md V2",
      citation_context=('"Every parallel pool equals the serial pool on the validation rows, at all four row '
                        'fractions and all five worker counts." (SPRINT_29_VALIDATION.md, V2); "Full ULB rows: serial '
                        '730.3 s; 32 workers 45.8 s; 16 workers 11.24 times faster than serial." '
                        '(SPRINT_29_VALIDATION.md, V2); "The longest single learner took 2.0 s" '
                        '(SPRINT_29_VALIDATION.md, V2); "Per-learner time rose with the worker count (summed learner '
                        'time 738.6 s at 1 worker, 1101.6 s at 32); what takes the rest of the wall time is not '
                        'measured." (SPRINT_29_VALIDATION.md, V2); "the first run stopped with a `MemoryError` at 32 '
                        'workers on the 0.5 fraction; its resume then hung for 9 hours" (SPRINT_29_VALIDATION.md, V2); '
                        '"The cause of the `MemoryError` is unverified" (SPRINT_29_VALIDATION.md, V2, markdown bold '
                        'dropped); "each parallel build is stopped after 2 times its fraction\'s serial time" '
                        '(SPRINT_29_VALIDATION.md, V2)'),
      certainty_reasons=(OWN + ". HIGH for the measured equality and times, which the run file holds (serial 730.3 s, "
                         "16 workers 11.24 times, all pools equal). Scope: one machine, one configuration; the cause "
                         "of the MemoryError is unverified, as Phase 2 says. Bears on "
                         "f110-cvqboost-pool-build-grows-faster-than-rows (the serial build at full rows, 773 s on "
                         "average); " + NOT_LINKED + ": a different measure")),
]

_f108 = next(a for a in f93.ASSERTIONS if a.id == "f108-hgb-plugin-overstates-bayes-error-5-to-12-percent")
_OLD_QUOTE = ('"plug-in 0.0064-0.0070 against 0.0060-0.0063, ratios 1.053, 1.097, 1.105, 1.114 and 1.118" (Results, '
              'main arm)')
# The stored value whose source Phase 2 changed (F164), against the document at COMMIT.
CORRECTED: list[AssertionRecord] = [
    dataclasses.replace(
        _f108,
        value=_f108.value.replace(
            "ratios 1.053 to 1.118:",
            "ratios 1.053 to 1.119 (three of the five corrected by Phase 2 on 2026-10-26, recomputed from the rows):"),
        citation_context=_f108.citation_context.replace(_OLD_QUOTE, (
            '"plug-in 0.0064-0.0070 against 0.0060-0.0063, ratios 1.053, 1.097, 1.106, 1.116 and 1.119" (Results, '
            'main arm); "(Corrected 2026-10-26, F164: the last three read 1.105, 1.114 and 1.118; recomputed from the '
            'rows as the plug-in estimate over the Bayes error. The count is unchanged.)" (Results, main arm)')),
        certainty_reasons=_f108.certainty_reasons.replace("commit eef3349", "commit 6242b8a (first read at eef3349)"),
        updated=TODAY, updated_reason=SYNC_REASON),
]

# The two paper records whose documents changed, each repointed at COMMIT with its earlier read kept.
REREAD = {
    "f108": (f93.SRC, "5348add", f93.RUN, "2026-10-22", "eef3349", f93.SHA256,
             "Phase 2 recomputed three plug-in ratios and the noise arm's range (F164); one stored value corrected, "
             "the other three confirmed by name (F120)"),
    "f162": (f108.F162_ID, "5348add", "experiments/phase2/results/f162_in_pocket.json, seeds 42-51, three cells",
             "2026-10-25", "9cbe5ba", f108.BLOBS["f162"][1],
             "Phase 2 marked the recorded wall time unverified (F164), a figure the store never held; both stored "
             "values confirmed by name (F120)"),
}
READ_DETAIL = "the whole document at commit 6242b8a, to compare the stored values with Phase 2's Sprint 29 edits (F120)"
REPOINT_NOTE = (f"{TODAY} ({TAG}): access, evidence and checked_against_source repointed at Phase 2 commit 6242b8a, "
                "where the document was re-read whole (INTAKE_WORKFLOW.md section 56)")


def repointed(key: str) -> dict[str, str]:
    rid, last, run, first_on, first_at, old_sha, why = REREAD[key]
    file = BLOBS[key][0]
    return {
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 {BLOBS[key][1]} at Phase 2 commit 6242b8a (the last commit to touch the "
                     f"file is {last}). Run: {run}. Read first on {first_on} at commit {first_at} (blob SHA-256 "
                     f"{old_sha}); re-read whole on {TODAY} at 6242b8a: {why}. The private repository's URL is the "
                     "citation's pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "checked_against_source": f"{TODAY}, Claude, read the whole document at commit 6242b8a via git show",
    }


def check_hashes() -> list[str]:
    files = {**BLOBS, **RESULTS}
    return [f"{k}: blob at {COMMIT[:7]} has changed" for k, (path, sha) in files.items()
            if hashlib.sha256(blob(path)).hexdigest() != sha]


def verify_all() -> list:
    """Every quote verbatim in its documents at COMMIT BEFORE anything is
    written (INTAKE_WORKFLOW.md sections 26, 31 and 41)."""
    texts = {"set": set_text("set"), "results": set_text("results"),
             "f108": plain(source_bytes("f108").decode("utf-8").replace("**", ""))}
    return ([(SET_ID, a, require_verbatim(a.id, a.citation_context, texts["set"], value=a.value)) for a in F166]
            + [(RES_ID, a, require_verbatim(a.id, a.citation_context, texts["results"], value=a.value)) for a in RES]
            + [(f93.SRC, a, require_verbatim(a.id, a.citation_context, texts["f108"], value=a.value))
               for a in CORRECTED])


def apply_changes(conn) -> list[str]:
    checked = verify_all()
    log = []
    for entry in (set_entry(), results_entry()):
        if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (entry["id"],)).fetchone() is None:
            insert_paper(conn, intake.build_record(entry, today=TODAY))
            log.append(f"paper  {entry['id']}")
    for key in REREAD:
        rid = REREAD[key][0]
        if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND read_on = ? AND detail = ?",
                            (rid, TODAY, READ_DETAIL)).fetchone():
            add_read(conn, rid, "Claude", TODAY, "full", READ_DETAIL)
            log.append(f"read   {rid}")
        want = repointed(key)
        row = conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                           (rid,)).fetchone()
        if tuple(row) != (want["access"], want["evidence"], want["checked_against_source"]):
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ?, checked_against_source = ? "
                         "WHERE record_id = ?", (want["access"], want["evidence"], want["checked_against_source"], rid))
            append_updated_reason(conn, rid, REPOINT_NOTE, TODAY)
            log.append(f"repoint {rid}")
    for src, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            insert_verified_assertion(conn, a, verified, yielded_by=src)
            log.append(f"assert {a.id}")
        else:
            changed = sync_verified_assertion(conn, a, verified, SYNC_REASON, TODAY)
            if changed:
                log.append(f"synced {a.id}: {', '.join(changed)}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_hashes()
    if bad:
        print("\n".join(bad))
        return 1
    if "--apply" not in args:
        for entry in (set_entry(), results_entry()):
            intake.build_record(entry, today=TODAY)  # validates the entry; nothing written
            print(f"paper  {entry['id']} [read]")
        for src, a, _ in verify_all():
            validate_assertion(a)
            print(f"{'correct' if src == f93.SRC else 'assert'} {a.id} [{a.certainty}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F120 Phase 2 Sprint 29 results")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log) or "nothing to write")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
