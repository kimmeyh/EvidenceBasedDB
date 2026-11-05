#!/usr/bin/env python3
"""Sprint 15 Task M (F130): Phase 2's Sprint 30 results, by the inbound path; F166 repointed with them.

Read at Phase 2 commit COMMIT, the head of PR #74 on 2026-11-04, through `git show` on the team lead's local clone,
which holds the commit; no fetch in a sibling repository (F79). INTAKE_WORKFLOW.md section 66.

Five new source records, each read whole:

- F174: `docs/phase2/algorithms/IEEE_COMPARISON.md` and the seven IEEE-CIS algorithm documents beside it (one run,
  `f174_ieee_algorithms.json`). Three assertions.
- F176 (`F176_BELOW_GREEDY.md`), F169 (`F169_PLUGIN_BINS.md`), F170 (`F170_MISSED_NEIGHBORS.md`) and F171
  (`F171_MISSED_IEEE.md`), one document and one record each. Six assertions.

And F166's record repointed: Phase 2's Sprint 30 added TP, FP, TN and FN to its eight ULB documents (72182b2), so the
local-file check read ULB_COMPARISON.md as changed. Every stored F166 value is verbatim at COMMIT and confirmed by
name; the first read (2026-10-30, commit 6242b8a) is kept in the evidence.

Context by section 43's rule: `ml` for a classical method on a simulator (F169), `hsbc-2026` for a result about the
project's own lanes or Experiment 3. No assertion is linked: the plan named `supports` or `contradicts` links to the
LOW claims each bears on, and no stored claim states the same fact whole (ADR-0004 A8 (b)'s rule for a link); each
reason names the stored claims it bears on instead.

Every quote is checked by `require_verbatim`, with the value, against the blobs at COMMIT before anything is written.
DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

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


f120 = _load("f120", "sprint14_f120_phase2.py")
intake = f120.intake

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, _ = script_paths(__file__)
TODAY = "2026-11-04"
TAG = "Sprint 15 Task M, F130"
PHASE2 = f120.PHASE2
REPO_URL = f120.REPO_URL
COMMIT = "366cf370fe5ac17981818e1d3c1422dd230414e6"
SHORT = COMMIT[:7]
OWN = f"Started HIGH: the consumer project's own measurement, read directly at Phase 2 commit {SHORT} (PR #74)"
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit {SHORT}, read directly on {TODAY}"
SYNC_REASON = f"{TODAY} ({TAG}): wording corrected against the documents at {SHORT} on the fresh-eyes review"
NOT_LINKED = "not linked (ADR-0004 A8 (b): no stored claim states the same fact whole)"

ALG = "docs/phase2/algorithms/"
# key -> (file, SHA-256 of the blob at COMMIT, the last commit to touch it)
BLOBS = {
    "ieee": (ALG + "IEEE_COMPARISON.md", "c3b02a03db4ab0b075b283454daa6c2001d19a4d7f1c34d68ad47ef39c8cd3e2"),
    "ieee_catboost": (ALG + "IEEE_CATBOOST.md", "baa2abd88f4920c9237403040789e384670431f508ec6f117bd678d079702a1e"),
    "ieee_lightgbm": (ALG + "IEEE_LIGHTGBM.md", "fa78eb15ebe4f4cda277a1adc71649ed362caeebc65ee629b13adb2462b32711"),
    "ieee_xgboost": (ALG + "IEEE_XGBOOST.md", "d0a58ee933898a029949f989cf22d1fbf61be2e1854d6b1dcb4b5145fb8098ae"),
    "ieee_hgb": (ALG + "IEEE_HGB.md", "807532fb1031513789d13d577d5be98410776d541abb9d10e8a0c11fc5277066"),
    "ieee_proxy": (ALG + "IEEE_CVQBOOST_PROXY.md", "7ced298145ea565871869937bfe54dd11d6ae2338af38fee8ed358a761d15342"),
    "ieee_svm": (ALG + "IEEE_SVM.md", "b11f55d66c04bc69214035fbebc0c785a1a235e90db60960c6f45308ba3c42fb"),
    "ieee_logistic": (ALG + "IEEE_LOGISTIC_REGRESSION.md",
                      "d05ea30810434c0f1b7f4f46fe77c31bf7d62597d0c6c9cf46205d9939df5df5"),
    "f176": ("docs/phase2/F176_BELOW_GREEDY.md", "4a8d5db8f8204aceb0cc404288263afcb8ba65749e51c726f46ae3caed3898ec"),
    "f169": ("docs/phase2/F169_PLUGIN_BINS.md", "d3752253bb9f91f62503dffd317e280b8713827405476378ed13d11112859157"),
    "f170": ("docs/phase2/F170_MISSED_NEIGHBORS.md",
             "8e8bd32c225bd4742c0b452a81a205f0e8ba916df56ca81a3ae91f6330a1f93f"),
    "f171": ("docs/phase2/F171_MISSED_IEEE.md", "e2cd6d5afe67a091d6b716430e5f25a80af7b9b063381abdead283b1413d4be6"),
    # F166's eight documents, as Sprint 30 left them (72182b2 added the confusion counts)
    "ulb": (ALG + "ULB_COMPARISON.md", "aea521a1fc2ac4da35aba436039369e2114d0965a44cd3d573b038b0681b4b3c"),
    "ulb_catboost": (ALG + "ULB_CATBOOST.md", "18b19af63bfcd1831b077b10b9da2237fd44b5adb9aa045cb72d4f8f643a93e8"),
    "ulb_lightgbm": (ALG + "ULB_LIGHTGBM.md", "0286d6027f1f16e29dbc3dd4c66f46b019bf3c524e93d1c9faa8088297afc740"),
    "ulb_xgboost": (ALG + "ULB_XGBOOST.md", "cf9c7ef663148e116e8a839104dbfe45bba4cd08e4b9ad7bc3c09897a9228aad"),
    "ulb_hgb": (ALG + "ULB_HGB.md", "4bd12a160656f2c26d8b9c54470a0ab6778ab9cb7e768ff07e4947f66ea09c63"),
    "ulb_proxy": (ALG + "ULB_CVQBOOST_PROXY.md", "a57a6365c1da3f4b14106ae46549b559fa963fb0614f1a6edb2dd5d8fb787dc6"),
    "ulb_svm": (ALG + "ULB_SVM.md", "89cf2f408c5b005fa3eb77d5aa5c4120991ae848ffb5dcc32ea3e3185f0faf0a"),
    "ulb_logistic": (ALG + "ULB_LOGISTIC_REGRESSION.md",
                     "0c56bbd58e899ef8effa10a7a779b543587a93a5ffae67655c7c41487ff8a04e"),
}
# The run files the documents report (named in the evidence; their hashes checked with the documents').
RESULTS = {
    "f174": ("experiments/phase2/results/f174_ieee_algorithms.json",
             "9955c120aeb99db2b325017b24cc62744ede0029af7927a2e4adb1b07afcf3c7"),
    "f176": ("experiments/phase2/results/f176_below_greedy.json",
             "ce648ee0e627fc48f0c75bdd4c6046f03353d383b5d7069d244db4cf2da0e7c8"),
    "f169": ("experiments/phase2/results/f169_plugin_bins.json",
             "4f17465b55acdfcb69c6277952f2a6b26c0478a50016631c926e7b067030ec0a"),
    "f170": ("experiments/phase2/results/f170_missed_neighbors.json",
             "e0d4a9e5e5a673a4b02a3ce7a4c67d5980c88361715b081ddb447b2e396d0c73"),
    "f171": ("experiments/phase2/results/f171_missed_ieee.json",
             "8c37916529dffca7d7520fc21099d134807bb238080918e937679ca65718ce89"),
    "f171_budgets": ("experiments/phase2/results/f171_budgets.json",
                     "54361b0d550ec79de513294f8397a7fa96dc64823f5be0460fe0c3299281e07c"),
    "f166": ("experiments/phase2/results/f166_ulb_algorithms.json",
             "f00511e9bd9c71684f3526e3ab17618c87c1a4a2daff6266448f7ae6b47c1f91"),
}
SETS = {
    "f174": ["ieee", "ieee_catboost", "ieee_lightgbm", "ieee_xgboost", "ieee_hgb", "ieee_proxy", "ieee_svm",
             "ieee_logistic"],
    "f176": ["f176"], "f169": ["f169"], "f170": ["f170"], "f171": ["f171"],
    "f166": ["ulb", "ulb_catboost", "ulb_lightgbm", "ulb_xgboost", "ulb_hgb", "ulb_proxy", "ulb_svm", "ulb_logistic"],
}
# key -> (record id, title as transcribed, Sprint 30 task, run keys, disposition, applicability)
RECORDS = {
    "f174": ("hsbc-qfraud-phase2-f174-sprint30-ieee-algorithms", "IEEE-CIS: seven algorithms compared (F174)",
             "Sprint 30 Task D (#78)", ["f174"],
             "Reference: the HSBC Phase 2 project's best achievable result per algorithm on IEEE-CIS, seven "
             "algorithms tuned on month 3 and scored on month 4 under one preregistered protocol over ten seeds, "
             "with the paired tests",
             [["hsbc-2026", "the CVQBoost proxy against six classical algorithms on IEEE-CIS -- BLUF and Adjacent "
                            "pairs"],
              ["ml", "six classical algorithms tuned on IEEE-CIS -- each algorithm document's Configurations tried"]]),
    "f176": ("hsbc-qfraud-phase2-f176-sprint30-result",
             "F176: can a classical solver get below greedy on F160's IEEE-CIS instances?", "Sprint 30 Task E (#79)",
             ["f176"],
             "Reference: the HSBC Phase 2 project's Experiment 3 check of whether a classical solver gets below "
             "greedy's learner-selection objective, with the method check on small exact instances",
             [["hsbc-2026", "Experiment 3's room on IEEE-CIS -- Result and The check"]]),
    "f169": ("hsbc-qfraud-phase2-f169-sprint30-result",
             "F169: the F108 plug-in with estimators set for extreme imbalance", "Sprint 30 Task F (#80)", ["f169"],
             "Reference: the HSBC Phase 2 project's test of two plug-in Bayes-error estimators on F108's fraud "
             "simulator, whose Bayes error is known",
             [["ml", "a ceiling estimator on a fraud simulator -- Result and What the rule does not show"]]),
    "f170": ("hsbc-qfraud-phase2-f170-sprint30-result",
             "F170: are the ULB frauds that every model misses among legitimate rows?", "Sprint 30 Task G (#81)",
             ["f170"],
             "Reference: the HSBC Phase 2 project's nearest-neighbor test of where the ULB frauds that every model "
             "family misses sit",
             [["hsbc-2026", "the project's model families on ULB, its CVQBoost lanes among them -- Result"]]),
    "f171": ("hsbc-qfraud-phase2-f171-sprint30-result", "F171: does the group every model misses shrink on IEEE-CIS?",
             "Sprint 30 Task H (#82)", ["f171", "f171_budgets"],
             "Reference: the HSBC Phase 2 project's count of the IEEE-CIS frauds every model family misses, against "
             "ULB's, at three alert budgets",
             [["hsbc-2026", "the project's model families on IEEE-CIS and ULB -- Result and Profile"]]),
}


def blob(path: str) -> bytes:
    """A file exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{path}"], capture_output=True, check=True).stdout


def set_text(name: str) -> str:
    """The set's documents joined, markdown bold dropped; a quote names its document in its anchor."""
    return plain(" ".join(blob(BLOBS[k][0]).decode("utf-8").replace("**", "") for k in SETS[name]))


def _shas(keys: list[str]) -> str:
    """The first key's is the first "SHA-256 <hex>" in the evidence, the one the local-file check
    (store/recheck.py) compares with the access path's document."""
    return "; ".join(f"{BLOBS[k][0]} SHA-256 {BLOBS[k][1]}" for k in keys)


def entry(key: str) -> dict:
    rid, title, task, runs, disposition, applicability = RECORDS[key]
    file = BLOBS[SETS[key][0]][0]
    many = len(SETS[key]) > 1
    return {
        "id": rid, "kind": "reference", "context": applicability[0][0], "tier": "read", "title": title,
        "citation": (f'hsbc-qfraud-phase2, "{title}," {file}'
                     + (" and the seven algorithm documents beside it" if many else "")
                     + f", commit {SHORT}, {TODAY}; {task} (hand-transcribed from the document's heading and the "
                       "repository's git log)"),
        "transcribed_from": f'the heading "{title}"',
        "disposition": disposition,
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 per document at Phase 2 commit {SHORT}: {_shas(SETS[key])}. Run: "
                     + "; ".join(f"{RESULTS[r][0]} (blob SHA-256 {RESULTS[r][1]})" for r in runs)
                     + ", evidence tag SIM, zero metered seconds. The private repository's URL is the citation's "
                       "pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "found_via": f"read from Phase 2 at {TAG}, {TODAY} (PR #74)",
        "cited_as": file,
        "checked_against_source": (f"{TODAY}, Claude, read "
                                   + ("all eight documents" if many else "the whole document")
                                   + f" in full at commit {SHORT} via git show"),
        "reads": [["Claude", TODAY, "full", (f"{Path(file).name} and the seven algorithm documents, each in full"
                                             if many else f"{Path(file).name} in full") + f", at commit {SHORT}"]],
        "applicability": applicability,
        "updated_reason": f"{TODAY}: added by scripts/sprint15_f130_phase2.py ({TAG}); read in full",
    }


def A(key: str, **kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "SIM")
    kw.setdefault("context", "hsbc-2026")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    kw["provenance"] = f"{RECORDS[key][0]}, {kw['provenance']}"
    return AssertionRecord(**kw)


ASSERTIONS = {
    "f174": [
        A("f174", id="f174-ieee-lightgbm-leads-four-pairs-reliable",
          value=("On IEEE-CIS, tuned on month 3 and scored on month 4 over ten seeds (42-51), seven algorithms rank "
                 "by mean test AUPRC: LightGBM 0.5785, HGB 0.5211, CatBoost 0.5114, XGBoost 0.4960, Phase 2's "
                 "CVQBoost proxy 0.4862, a linear SVM 0.3612 and logistic regression 0.3564. Of the six adjacent "
                 "pairs, four reject under the entry's exact Wilcoxon test at Bonferroni 0.05 / 6 (LightGBM above "
                 "HGB, CatBoost above XGBoost, the proxy above the SVM, the SVM above logistic regression), but three "
                 "of the four rest on a lane whose test AUPRC is the same on every seed (XGBoost, the SVM and "
                 "logistic regression each chose one configuration on every seed, and the months are fixed), so the "
                 "seeds are not independent evidence there; the SVM against logistic regression is one test month. "
                 "The order of HGB and CatBoost, and of XGBoost and the proxy, is not established. Phase 2's limits: "
                 "one test month, one grid per algorithm (F166's), device lanes, QSVM and QNN outside it"),
          provenance="IEEE_COMPARISON.md BLUF and Adjacent pairs, each algorithm document's BLUF and Limits",
          citation_context=('"Over 10 seeds (42-51), the order by mean test AUPRC is LightGBM, HGB, CatBoost, '
                            'XGBoost, the proxy, SVM and logistic regression." (IEEE_COMPARISON.md, BLUF); "Tuned on '
                            'month 3 and scored on month 4 over 10 seeds (42-51)" (each algorithm document, BLUF); '
                            '"LightGBM reaches a mean test AUPRC of 0.5785" (IEEE_LIGHTGBM.md, BLUF); "HGB reaches a '
                            'mean test AUPRC of 0.5211" (IEEE_HGB.md, BLUF); "CatBoost reaches a mean test AUPRC of '
                            '0.5114" (IEEE_CATBOOST.md, BLUF); "XGBoost reaches a mean test AUPRC of 0.4960" '
                            '(IEEE_XGBOOST.md, BLUF); "CVQBoost proxy reaches a mean test AUPRC of 0.4862" '
                            '(IEEE_CVQBOOST_PROXY.md, BLUF); "SVM reaches a mean test AUPRC of 0.3612" (IEEE_SVM.md, '
                            'BLUF); "Logistic regression reaches a mean test AUPRC of 0.3564" '
                            '(IEEE_LOGISTIC_REGRESSION.md, BLUF); "the exact two-sided Wilcoxon signed-rank test on '
                            'per-seed AUPRC differences is primary, at Bonferroni 0.05 / 6." (IEEE_COMPARISON.md, '
                            'Adjacent pairs); "Of the six adjacent pairs, 4 differ reliably under the entry\'s test: '
                            'LightGBM above HGB; CatBoost above XGBoost; CVQBoost proxy above SVM; SVM above logistic '
                            'regression." (IEEE_COMPARISON.md, BLUF); "rest on a lane whose test AUPRC is the same on '
                            'every seed, so the seeds are not independent evidence there" (IEEE_COMPARISON.md, BLUF); '
                            '"It chose the same configuration on every seed, and the months are fixed, so the seed '
                            'does not change the result." (IEEE_XGBOOST.md, IEEE_SVM.md and '
                            'IEEE_LOGISTIC_REGRESSION.md, Test-month results); "The p value comes from the repeats; '
                            'the evidence is one test month." (IEEE_COMPARISON.md, Adjacent pairs); "so the order '
                            'among HGB and CatBoost; XGBoost and the proxy is not established." (IEEE_COMPARISON.md, '
                            'BLUF); "One test month. Month-to-month drift is outside this result; F152 scores months '
                            '4-6." (each algorithm document, Limits); "One protocol and one grid per algorithm, '
                            'F166\'s." (each algorithm document, Limits); "Device lanes (CVQBoost on hardware, QSVM) '
                            'and QNN are outside this part of F157." (each algorithm document, Limits)'),
          certainty_reasons=(OWN + ". HIGH for the measured ranking and the paired tests under the entry's rule, "
                             "with Phase 2's own caution on the three pairs that rest on a fixed lane. Scope: one "
                             "test month, ten seeds, one grid per algorithm, the proxy and not Dirac hardware. Bears "
                             "on f152-ieee-cis-trees-beat-logistic-lightgbm-leads (XGBoost above logistic regression "
                             "on months 4 and 5, and LightGBM leading every month, at five seeds) and on "
                             "han-ieee-cis-best-test-scores-random-split (AUPRC 0.6699 on a random split, LOW): a "
                             "temporal split and a different protocol, so neither is confirmed whole; " + NOT_LINKED)),
        A("f174", id="f174-ieee-recall-at-budget-bounded-by-capacity",
          value=("On IEEE-CIS's test month (fraud rate 3.47%), the seven tuned algorithms of Phase 2's comparison "
                 "caught on average 0.1215 to 0.1389 of the frauds at the month's own 0.5% alert budget of 427 rows, "
                 "which can catch at most 427 of the month's 2,962 frauds. Scores tied at the budget's last place are "
                 "all flagged and counted, so HGB on 1 of 10 seeds and the proxy on 8 of 10 flagged a few more rows "
                 "(the proxy up to 442). F152's adversarial drift control stopped "
                 "at its cap of 20 rounds with a final adversarial AUC of 0.9906 on the tuning fold and 0.9450 on the "
                 "scored fold: a classifier could still tell the training months from the scored month"),
          provenance="IEEE_COMPARISON.md Notes",
          citation_context=('"At the test month\'s own 0.5% alert budget (427 rows), mean recall lies between 0.1215 '
                            'and 0.1389." (IEEE_COMPARISON.md, Notes); "The month\'s fraud rate is 3.47%, so the '
                            'budget can catch at most 427 of its 2,962 frauds (F171)." (IEEE_COMPARISON.md, Notes); '
                            '"scores tied at the budget\'s last place are all flagged, so a lane can flag more rows '
                            'than the budget: HGB on 1 of 10 seeds, up to 428 rows against a budget of 427; the proxy '
                            'on 8 of 10 seeds, up to 442 rows against a budget of 427. The counts include those rows." '
                            '(IEEE_COMPARISON.md, Notes); "on the tuning fold it stopped at its cap of 20 rounds, with a final adversarial AUC of '
                            '0.9906; on the scored fold it stopped at its cap of 20 rounds, with a final adversarial '
                            'AUC of 0.9450." (IEEE_COMPARISON.md, Notes); "An AUC near 1 means a classifier still '
                            'tells the training months from the scored month." (IEEE_COMPARISON.md, Notes)'),
          certainty_reasons=(OWN + ". HIGH for the measured recall range and the stated capacity, which is "
                             "arithmetic on the month's own counts. Scope: one test month. Phase 2 does not say how "
                             "much of the gap between months the drift explains, so the value does not either")),
        A("f174", id="f174-ieee-cvqboost-proxy-scores-heavily-tied",
          value=("On IEEE-CIS, Phase 2's CVQBoost proxy chose its full configuration on every seed (a serially built "
                 "pool of 833 learners on 17 features) and reached mean test AUPRC 0.4862 (95% t interval 0.4751 to "
                 "0.4973), fifth of seven. Its test scores are heavily tied (tie fraction 0.9365 to 0.9631; the most "
                 "common score covers 0.8434 to 0.9111 of test rows), so a threshold moves many rows at once. Its "
                 "mean train-test AUPRC gap, 0.3771, is the largest of the seven algorithm documents' (LightGBM "
                 "0.2947, XGBoost 0.3169, HGB 0.1861, CatBoost 0.1846, logistic regression 0.0465, the SVM 0.0363)"),
          provenance="IEEE_CVQBOOST_PROXY.md BLUF, Configurations tried, Test-month results and Limits; each algorithm "
                     "document's Test-month results",
          citation_context=('"CVQBoost proxy reaches a mean test AUPRC of 0.4862 (95% t interval 0.4751 to 0.4973). '
                            'It is number 5 of 7 by mean test AUPRC" (IEEE_CVQBOOST_PROXY.md, BLUF); "| config full '
                            '| 10 of 10 |" (IEEE_CVQBOOST_PROXY.md, Configurations tried); "Every pool was built '
                            'serially. The chosen configuration\'s pool used 17 features and held 833 learners." '
                            '(IEEE_CVQBOOST_PROXY.md, Configurations tried); "The proxy\'s test scores are heavily '
                            'tied: the tie fraction is 0.9365 to 0.9631, and the most common score covers a share of '
                            '0.8434 to 0.9111 of test rows." (IEEE_CVQBOOST_PROXY.md, Limits); "A threshold moves '
                            'every row with a tied score at once" (IEEE_CVQBOOST_PROXY.md, Limits); "| Train-test '
                            'AUPRC gap | 0.3771 |" (IEEE_CVQBOOST_PROXY.md, Test-month results); "| Train-test AUPRC '
                            'gap | 0.2947 |" (IEEE_LIGHTGBM.md); "| Train-test AUPRC gap | 0.3169 |" '
                            '(IEEE_XGBOOST.md); "| Train-test AUPRC gap | 0.1861 |" (IEEE_HGB.md); "| Train-test '
                            'AUPRC gap | 0.1846 |" (IEEE_CATBOOST.md); "| Train-test AUPRC gap | 0.0465 |" '
                            '(IEEE_LOGISTIC_REGRESSION.md); "| Train-test AUPRC gap | 0.0363 |" (IEEE_SVM.md)'),
          certainty_reasons=(OWN + ". HIGH for the measured choice, ties and gaps. 'Largest of the seven' is this "
                             "repository's comparison of the seven documents' figures, each quoted; Phase 2's "
                             "comparison page does not state it for IEEE-CIS. Scope: one test month, the proxy and "
                             "not Dirac hardware. Bears on f166-ulb-cvqboost-proxy-largest-train-test-gap (the same "
                             "lane's largest gap on ULB, 0.2075): the same pattern on a second data set, a different "
                             "fact, so " + NOT_LINKED)),
    ],
    "f176": [
        A("f176", id="f176-below-greedy-on-3-of-6-by-tiny-gains",
          value=("On F160's six IEEE-CIS learner-selection instances (Experiment 3), a classical solver got more "
                 "than 1e-6 below greedy's objective on 3 (42/free, 42/mid and 43/free), and nothing beat greedy on "
                 "the other 3. The largest gain on any instance is under 2e-05, less than a five-thousandth of the "
                 "gap between greedy and the floor (about 0.097 on 42/free). Simulated annealing from greedy found "
                 "the gains on both free instances, and the swap search tied it on 42/mid. SCIP did not beat greedy "
                 "anywhere: it stopped at its 1,200 s cap on all six with a selection above greedy's. Its dual bound "
                 "tightens the room bound to about 0.081-0.084 on the mid instances only. The rebuilt instances' "
                 "greedy objectives equal F160's within 1e-9"),
          provenance="F176_BELOW_GREEDY.md Result",
          citation_context=('"Yes, on 3 of 6 instances, by very little." (F176_BELOW_GREEDY.md, Result, markdown bold '
                            'dropped); "The best selection found is more than 1e-6 below greedy\'s objective on '
                            '42/free, 42/mid and 43/free." (Result); "On 43/mid, 44/free and 44/mid nothing beat '
                            'greedy." (Result); "The largest gain on any instance is under 2e-05, less than a '
                            'five-thousandth of the gap between greedy and the floor." (Result); "the gap to the floor '
                            'stays about 0.097" (Result); "Simulated annealing from greedy on both `free` instances" '
                            '(Result); "the swap search and simulated annealing from greedy (SA seed 42) reached the '
                            'same objective, -0.8215201929." (Result); "SCIP did not beat greedy anywhere." (Result); '
                            '"It stopped at its 1,200 s cap on all six, with a selection above greedy\'s" (Result); '
                            '"SCIP\'s dual bound tightens the room only on the `mid` instances." (Result); "so the '
                            'room bound is about 0.081-0.084, not 0.098." (Result); "Each instance\'s greedy objective '
                            'equals F160\'s recorded one within 1e-9, so these are F160\'s instances." (Result)'),
          certainty_reasons=(OWN + ". HIGH for the measured objectives and the solver runs. Scope: six instances, "
                             "classical solvers only, the objective and no test score. Bears on "
                             "f160-exp3-room-check-passes-on-ieee-cis (the room check passes on these instances): "
                             "here the room is shown reachable only by about 1e-05, and Phase 2 says the rest is not "
                             "shown to exist; a different fact, so " + NOT_LINKED)),
        A("f176", id="f176-swap-search-misses-exact-optimum-on-3-of-7",
          value=("On 26 small learner-selection instances solved exactly by enumeration (20 learners choosing 4), "
                 "greedy was above the exact optimum on 7, and Phase 2's one-for-one swap search reached the optimum "
                 "on 4 of the 7 and stayed at greedy's value on the other 3. So on F176's three IEEE-CIS instances "
                 "where nothing beat greedy, that does not show greedy is optimal. Phase 2 infers, untested, that "
                 "gains of about 1e-05 may sit below what the Dirac-3S device resolves (F104's resolution gate)"),
          provenance="F176_BELOW_GREEDY.md The check, What the result does not show and What it changes",
          citation_context=('"On 26 small instances (20 learners choosing 4, solved exactly by enumeration" '
                            '(F176_BELOW_GREEDY.md, The check); "greedy is above the exact optimum on 7." (The check); '
                            '"the swap search reaches the exact optimum on 4 of the 7" (The check); "On the other 3 '
                            '(random_4, random_7 and random_12) the swap search stays at greedy\'s value." (The check, '
                            'markdown bold dropped); "A one-for-one swap search is a local method: it stops where no '
                            'single swap improves." (The check); "does not show that greedy is optimal." (The check); '
                            '"so the device question becomes whether Dirac-3S reaches it faster or further." (What it '
                            'changes); "Reasonable inference, not tested: gains of about 1e-05 may sit below what the '
                            'device resolves (F104\'s resolution gate)" (What it changes)'),
          certainty_reasons=(OWN + ". HIGH for the measured check on 26 exact instances. The device sentence is "
                             "Phase 2's inference, attributed as untested. Scope: 20-learner instances, one local "
                             "method")),
    ],
    "f169": [
        A("f169", id="f169-lightgbm-bins-plugin-passes-f108-rule",
          context="ml",
          value=("On F108's fraud simulator, whose Bayes error is known, a plug-in Bayes-error estimate from LightGBM "
                 "with 4,095 bins and no early stopping recovered the known Bayes error on 5 of 5 seeds on every arm "
                 "(main, label-flip noise, reference), and one from HGB with early stopping off on 4 of 5 on the "
                 "main arm, the rule's minimum: the first ceiling methods to pass F108's harness. Phase 2's limits: "
                 "LightGBM's reference-arm passes are degenerate (on seeds 42-45 its test AUPRC there equals the "
                 "arm's fraud rate, 0.0006), so the reference arm does not show that the finer bins fix HGB's "
                 "failure; a pass does not show the plug-in is accurate on ULB or IEEE-CIS, where the Bayes error is "
                 "unknown; and on the main arm LightGBM's test AUPRC (0.282 to 0.300) stays below the Bayes "
                 "classifier's (0.296 to 0.318)"),
          provenance="F169_PLUGIN_BINS.md Result, What the rule does not show and What it changes",
          citation_context=('"Both estimators pass F108\'s rule on the main arm." (F169_PLUGIN_BINS.md, Result, '
                            'markdown bold dropped); "This is the first ceiling method to pass F108\'s harness, after '
                            'the calibrated plug-in (Sprint 28) and F156\'s Henze-Penrose bound (Sprint 29) failed." '
                            '(Result); "(LightGBM, 4,095 bins, HGB\'s shape, no early stopping): recovered on 5 of 5 '
                            'seeds on every arm (main, label-flip noise, reference)." (Result); "(HGB, F108\'s '
                            'settings, early stopping off): recovered on 4 of 5 seeds on the main arm" (Result); "HGB '
                            'without early stopping passes at the minimum, 4 of 5." (What the rule does not show); '
                            '"On seeds 42-45, LightGBM\'s test AUPRC there is 0.0006, the arm\'s fraud rate, so it '
                            'ranks frauds no better than chance." (What the rule does not show); "So the reference arm '
                            'does not show that the finer bins fix HGB\'s failure." (What the rule does not show); '
                            '"It does not show that the plug-in is accurate on ULB or IEEE-CIS, where the Bayes error '
                            'is unknown." (What the rule does not show); "(LightGBM\'s test AUPRC 0.282 to 0.300 '
                            'against a Bayes AUPRC of 0.296 to 0.318)" (What it changes); "Recovering the Bayes error '
                            'is not the same as ranking as well as the Bayes classifier." (What it changes)'),
          certainty_reasons=(OWN + ". HIGH for the measured recovery under F108's preregistered rule. Scope: one "
                             "simulator, five seeds. Bears on f108-no-ceiling-method-recovered-known-ceiling (MODERATE: "
                             "none of F108's methods recovered the ceiling) and f114-calibrated-plugin-misses-known-"
                             "ceiling: those methods still failed, and this is a new estimator, so neither is "
                             "contradicted; " + NOT_LINKED)),
    ],
    "f170": [
        A("f170", id="f170-ulb-missed-by-all-frauds-sit-among-legitimate-rows",
          value=("On ULB (12 model families, seeds 42-51), the 36 frauds that every family missed in every seed in "
                 "which they were test rows sit among legitimate rows: the median share of legitimate rows among each "
                 "fraud's 10 nearest training rows (Euclidean, on the 30 standardized features) is 1.0 for them "
                 "against 0.1 for the 370 frauds some family caught in every such seed; 12 frauds missed in some "
                 "seeds and caught in others are left out. Every missed fraud has mostly legitimate neighbors, "
                 "against 16.2% of caught frauds; a two-sided Mann-Whitney U test rejects (p below 1e-20). A "
                 "simulator check, where the information limit is known, fired first. Phase 2's limits: consistent "
                 "with, not proof of, an information limit, since the neighbors are measured in the same 30 features "
                 "the models use; it shows where the missed frauds sit, not that no model could catch them"),
          provenance="F170_MISSED_NEIGHBORS.md Result and What the result does not show",
          citation_context=('"the share of legitimate rows among its 10 nearest training rows (Euclidean, on the 30 '
                            'features standardized on the training rows)." (F170_MISSED_NEIGHBORS.md, Result); "The 12 '
                            'on-split families of F158 step 3, seeds 42-51, are compared." (Result); "36 frauds are '
                            'missed by every family in every seed in which they are test rows, and 370 are caught by '
                            'some family in every such seed." (Result); "Median legitimate share: 1.0 missed, 0.1 '
                            'caught." (Result); "Every missed fraud has mostly legitimate neighbors; 16.2% of caught '
                            'frauds do." (Result); "12 distinct frauds are missed in some seeds and caught in others" '
                            '(Result); "U rejects at alpha 0.05 (p below 1e-20)" (Result); "two-sided '
                            'Mann-Whitney U rejects" (Result); "The comparison can detect a known information limit, '
                            'so the ULB reading is made." (Result); "Consistent with, not proof of, an information '
                            'limit." (What the result does not show, markdown bold dropped); "The neighbors are '
                            'measured in the same 30 features the models use." (What the result does not show); "The '
                            'test shows where the missed frauds sit, not that no model could catch them." (What the '
                            'result does not show)'),
          certainty_reasons=(OWN + ". HIGH for the measured neighbor shares and the test. Scope: one data set, one "
                             "feature space, ten seeds. Bears on f154-no-stored-model-better-on-a-ulb-subset (no "
                             "stored model better on a ULB subset): consistent with it, a different measure, so "
                             + NOT_LINKED)),
    ],
    "f171": [
        A("f171", id="f171-ieee-missed-by-all-share-not-shown-smaller",
          value=("Phase 2 counted the share of (fold, seed, test fraud) pairs no model family flags. At every alert "
                 "budget a larger share of IEEE-CIS frauds is missed by all than of ULB frauds (preregistered 0.5% "
                 "budget: 81.5% against 11.2%; at three times each fold's fraud rate, the like-for-like budget: "
                 "18.2% against 11.2%), but the counts compare 4 IEEE-CIS families with 12 ULB families, so the gap "
                 "is not shown to come from the data, and the entry's reading that richer fields catch more frauds "
                 "is not met. At 0.5% the budget itself misses 42% of IEEE-CIS month 4's frauds before any model is "
                 "scored: 427 alerts per family for 2,962 frauds, so four families with no overlap flag at most "
                 "1,708. The other budgets are post hoc and exploratory; a "
                 "4-family ULB count was not computed"),
          provenance="F171_MISSED_IEEE.md Result and What the result does not show",
          citation_context=('"Share of (fold, seed, test fraud) pairs that no family flags." (F171_MISSED_IEEE.md, '
                            'Result); "At every budget, a larger share of IEEE-CIS frauds is missed by all families '
                            'than of ULB frauds, but the counts compare 4 IEEE-CIS families with 12 ULB families." '
                            '(Result, markdown bold dropped); "| 0.5% (preregistered) | 81.5% | 11.2% | 42.3% |" '
                            '(Result); "The like-for-like row is the matched budget, 18.2% against 11.2%." (Result); '
                            '"More families flag more distinct frauds, so the gap is not shown to come from the data." '
                            '(Result); "is not met." (Result); "On IEEE-CIS month 4, each family has 427 alerts for '
                            '2,962 frauds." (Result); "Four families with no overlap could flag at most 1,708" '
                            '(Result); "so 1,254 frauds (42%) are missed before any model is scored." '
                            '(Result); "The post hoc budgets are exploratory." (What the result does not show); "A '
                            '4-family ULB count was not computed." (What the result does not show)'),
          certainty_reasons=(OWN + ". HIGH for the measured shares and the stated capacity; the cross-data-set "
                             "comparison is Phase 2's own 'not shown'. Scope: four IEEE-CIS families, months 4-6, "
                             "seeds 42-46; twelve ULB families, seeds 42-51. Bears on "
                             "f170-ulb-missed-by-all-frauds-sit-among-legitimate-rows (the same question on ULB)")),
        A("f171", id="f171-ieee-missed-profile-productcd-w-devicetype-missing",
          value=("At the 0.5% budget, IEEE-CIS frauds missed by all of Phase 2's four families differ on raw fields "
                 "from frauds some family caught: ProductCD W is 53.0% of missed rows against 7.5% of caught, "
                 "ProductCD C 32.5% against 73.2%, DeviceType missing 55.4% against 8.5%, and the median C1 is 2 "
                 "against 14. 5,264 distinct rows are missed in some seed; the two groups are not disjoint (a row "
                 "missed in one seed and caught in another is in both), and the caught group's size and the overlap "
                 "are not recorded. Phase 2 says the profile shows what the top 0.5% of each ranking looks like more "
                 "than what models cannot see"),
          provenance="F171_MISSED_IEEE.md Profile and What the result does not show",
          citation_context=('"ProductCD W: 53.0% of missed rows, 7.5% of caught rows. ProductCD C: 32.5% against '
                            '73.2%." (F171_MISSED_IEEE.md, Profile); "DeviceType missing: 55.4% of missed, 8.5% of '
                            'caught." (Profile); "C1 median 2 missed, 14 caught" (Profile); "the two are not disjoint, '
                            'and the result records neither group\'s size nor the overlap" (Profile); "so the profile '
                            'shows what the top 0.5% looks like, more than what models cannot see." (Profile); '
                            '"5,264 distinct rows are missed in some seed." (Profile)'),
          certainty_reasons=(OWN + ". HIGH for the measured shares as recorded, with Phase 2's stated limits on "
                             "what they mean. Scope: four families, one budget; the groups overlap")),
    ],
}

# F166's record, repointed at COMMIT with its first read kept (Sprint 30 added the confusion counts).
F166_ID = f120.SET_ID
F166_READ = (f"ULB_COMPARISON.md and the seven algorithm documents, each in full, at commit {SHORT}, to compare the "
             "stored values with Phase 2's Sprint 30 edits (F130)")
F166_NOTE = (f"{TODAY} ({TAG}): access, evidence and checked_against_source repointed at Phase 2 commit {SHORT} "
             "(PR #74), where the eight documents were re-read whole (INTAKE_WORKFLOW.md section 66)")


def f166_repointed() -> dict[str, str]:
    file = BLOBS["ulb"][0]
    return {
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 per document at Phase 2 commit {SHORT} (the last commit to touch them is "
                     f"72182b2): {_shas(SETS['f166'])}. Run: {RESULTS['f166'][0]} (blob SHA-256 "
                     f"{RESULTS['f166'][1]}, unchanged), seeds 42-51, evidence tag SIM, zero metered seconds. Read "
                     "first on 2026-10-30 at commit 6242b8a (ULB_COMPARISON.md blob SHA-256 "
                     f"{f120.BLOBS['comparison'][1]}); re-read whole on {TODAY} at {SHORT}: Phase 2's Sprint 30 added "
                     "TP, FP, TN and FN at each test fold's own 0.5% budget, and a note on tied scores at the "
                     "budget's last place (the proxy flagged up to 297 rows against a budget of 284 on 7 of 10 seeds, "
                     "counted in its recall); the four stored values confirmed by name, the recall range unchanged "
                     "by it. The private repository's URL "
                     "is the citation's pointer; the record depends on the commit. Read-only from this repository "
                     "(F79)."),
        "checked_against_source": f"{TODAY}, Claude, read all eight documents in full at commit {SHORT} via git show",
    }


def check_hashes() -> list[str]:
    files = {**BLOBS, **RESULTS}
    return [f"{k}: blob at {SHORT} has changed" for k, (path, sha) in files.items()
            if hashlib.sha256(blob(path)).hexdigest() != sha]


def stored_f166(conn) -> list[tuple[str, str, str]]:
    return conn.execute("SELECT r.id, r.value, f.citation_context FROM paper_yields y JOIN records r ON "
                        "r.id = y.assertion_id JOIN assertion_fields f ON f.record_id = r.id WHERE y.paper_id = ? "
                        "ORDER BY r.id", (F166_ID,)).fetchall()


def verify_all(conn) -> tuple[list, list[str]]:
    """Every new quote, and every stored F166 quote, verbatim in its documents at COMMIT, with its value, BEFORE
    anything is written. Raises on the first that is not."""
    checked = []
    for key, items in ASSERTIONS.items():
        text = set_text(key)
        checked += [(RECORDS[key][0], a, require_verbatim(a.id, a.citation_context, text, value=a.value))
                    for a in items]
    ulb = set_text("f166")
    rows = stored_f166(conn)
    if not rows:
        raise ValueError(f"{F166_ID}: no stored assertion")
    confirmed = []
    for aid, value, cc in rows:
        require_verbatim(aid, cc, ulb, value=value)
        confirmed.append(f"confirm {aid} (verbatim at {SHORT})")
    return checked, confirmed


def apply_changes(conn) -> list[str]:
    checked, _ = verify_all(conn)
    log = []
    for key in RECORDS:
        e = entry(key)
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (e["id"],)).fetchone() is None:
            insert_paper(conn, intake.build_record(e, today=TODAY))
            log.append(f"paper  {e['id']}")
    for src, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            insert_verified_assertion(conn, a, verified, yielded_by=src)
            log.append(f"assert {a.id}")
        else:  # a correction after the first apply reaches the store, not "nothing to write" (fresh-eyes review)
            changed = sync_verified_assertion(conn, a, verified, SYNC_REASON, TODAY)
            if changed:
                log.append(f"synced {a.id}: {', '.join(changed)}")
    if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND read_on = ? AND detail = ?",
                        (F166_ID, TODAY, F166_READ)).fetchone():
        add_read(conn, F166_ID, "Claude", TODAY, "full", F166_READ)
        log.append(f"read   {F166_ID}")
    want = f166_repointed()
    row = conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                       (F166_ID,)).fetchone()
    # Repointed only from F120's 6242b8a form or this script's own earlier wording: a later repoint is kept
    # (fresh-eyes review: a rerun would otherwise move F166 back to COMMIT)
    if tuple(row) != (want["access"], want["evidence"], want["checked_against_source"]) and (
            f120.COMMIT in row[0] or COMMIT in row[0]):
        conn.execute("UPDATE paper_fields SET access = ?, evidence = ?, checked_against_source = ? WHERE record_id = ?",
                     (want["access"], want["evidence"], want["checked_against_source"], F166_ID))
        append_updated_reason(conn, F166_ID, F166_NOTE, TODAY)
        log.append(f"repoint {F166_ID}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_hashes()
    if bad:
        print("\n".join(bad))
        return 1
    conn = connect(DB_PATH)
    try:
        checked, confirmed = verify_all(conn)
    finally:
        conn.close()
    if "--apply" not in args:
        for key in RECORDS:
            e = entry(key)
            intake.build_record(e, today=TODAY)  # validates the entry; nothing written
            print(f"paper  {e['id']} [read]")
        for _, a, _ in checked:
            validate_assertion(a)
            print(f"assert {a.id} [{a.certainty}, {a.context}]")
        print("\n".join(confirmed))
        print(f"repoint {F166_ID} at {SHORT}")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F130 Phase 2 Sprint 30 results and F166 repoint")
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
