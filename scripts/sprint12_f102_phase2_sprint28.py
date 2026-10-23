#!/usr/bin/env python3
"""Sprint 12 Task C (F102): Phase 2's Sprint 28 results, entered by the inbound path.

Seven result documents in hsbc-qfraud-phase2's `docs/phase2/`, read whole
on 2026-10-23 at Phase 2 commit 10086da (branch feature/20261019_Sprint_28,
PR #46 still draft), through `git show`, so a later edit in Phase 2 cannot
change what is checked. One reference record per document, as F93 entered
F108, and 12 SIM assertions. INTAKE_WORKFLOW.md section 43. The second
apply added F111, whose result the first missed, and corrected five values
(fresh-eyes review of 5bcafe0).

Certainty as F93's: the consumer project's own measurement, read directly,
starts HIGH; each value carries Phase 2's own limits, and its inferences
are attributed as inferences. No relation is linked (ADR-0004 A8 (b));
where a result bears on a stored claim, the value names it.

Every quote is checked by `require_verbatim`, with the value, against the
blob at COMMIT (markdown bold dropped first) before anything is written,
and written only through the verified write path (intake sections 26 and
31). DRY-RUN BY DEFAULT; `--apply` takes a verified backup first.
Idempotent.
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
from store.ingest import (AssertionRecord, insert_paper, insert_verified_assertion,  # noqa: E402
                          sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
TAG = "Sprint 12 Task C, F102"
PHASE2 = r"D:\Data\Harold\github\hsbc-qfraud-phase2"
COMMIT = "10086da7246219c0c096de27417e2bb1f5dfb41d"
REPO_URL = "https://github.com/kimmeyh/hsbc-qfraud-phase2"
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit 10086da, read directly on {TODAY}"
SYNC_REASON = (f"{TODAY} ({TAG}): corrected against the document at 10086da to carry what its source says "
               "(fresh-eyes review of 5bcafe0; INTAKE_WORKFLOW.md section 43, second apply)")
OWN = ("Started HIGH: the consumer project's own measurement, read directly at Phase 2 commit 10086da "
       "(PR #46 still draft)")

# key -> (file, last commit touching it, SHA-256 of the blob at COMMIT, heading, first line, run, disposition,
#         applicability)
DOCS = {
    "f151": ("docs/phase2/F151_HGB_COMPARATOR.md", "e9946f5",
             "caa8d3a641e1a43e878d1ecf571da45c38585d484a40c2d0ca20b431848afea3",
             "F151: Why the ULB HGB Comparator Was Unstable", "Sprint 28 Task A (#48)",
             "experiments/phase2/results/f151_hgb_cause.json, seeds 42-46",
             "Reference: the HSBC Phase 2 project's controlled test of why its HGB baseline on ULB was unstable, "
             "and its restatement of F130's CVQBoost proxy reading against the stable HGB",
             [["ml", "HGB's L2 setting at 0.17% prevalence -- Bottom line and The controlled changes"],
              ["hsbc-2026", "the CVQBoost proxy against the stable HGB -- Bottom line"]]),
    "f152": ("docs/phase2/F152_EXP2_RESULT.md", "0b5ea6c",
             "d70f2ed24d1a37ad13c6d18f6325d0bd54a09a6271403986edfcc6f4ab31f85c",
             "Experiment 2 (F152): temporal validity on IEEE-CIS, the result", "Sprint 28 Task B (#49), 2026-10-22",
             "experiments/phase2/results/f152_exp2.json, seeds 42-46, three rolling-origin folds",
             "Reference: the HSBC Phase 2 project's preregistered test of classical models trained on earlier "
             "months of IEEE-CIS and scored on later ones",
             [["ml", "four classical lanes scored month by month on IEEE-CIS -- BLUF and Results"]]),
    "f153": ("docs/phase2/F153_EXP3_DESIGN.md", "cfff1fe",
             "e4d924f8a2feff9d2cd6e1c904f2b749a456d5f07de0cbfc56f0ba16f90c7598",
             "Experiment 3 (F153): the proxy design, the result", "Sprint 28 Task C (#50), 2026-10-22",
             "experiments/phase2/results/f153_exp3_design.json, six instances",
             "Reference: the HSBC Phase 2 project's preregistered design check for a Dirac integer formulation "
             "that selects weak learners; it fails its own falsifier",
             [["hsbc-2026", "the device arm's learner-selection formulation -- BLUF and Results"]]),
    "f110": ("docs/phase2/F110_SCALING.md", "7f5b3c0",
             "bf97920206e391efe1a223e2cf137f8a39ee4426c8879de14e684d07c77fb672",
             "Experiment 6 (F110): training time against sample count, the result",
             "Sprint 28 Task E (#52), 2026-10-22",
             "experiments/phase2/results/f110_scaling.json, seeds 42-46, four row fractions",
             "Reference: the HSBC Phase 2 project's preregistered timing of a CVQBoost proxy fit against the "
             "number of training rows",
             [["hsbc-2026", "the CVQBoost pool build and proxy solve timed by rows -- BLUF and Results"]]),
    "f114": ("docs/phase2/F114_CALIBRATED_PLUGIN.md", "74ce420",
             "588df2026a0bf5c585e8cb21d9df953b0751a961f47aac2cd500d1b2e4a59f57",
             "F114 gate: an isotonic-calibrated plug-in on F108's simulator", "Sprint 28 Task G (#53), 2026-10-22",
             "experiments/phase2/results/f114_calibrated_plugin.json, seeds 42-46",
             "Reference: the HSBC Phase 2 project's test of a calibrated HGB plug-in ceiling estimate against "
             "F108's simulator, whose Bayes error is known",
             [["ml", "a calibrated plug-in Bayes-error estimate against a known ceiling -- BLUF and Results"]]),
    "f154": ("docs/phase2/F154_WHERE_MODELS_WIN.md", "79fbe19",
             "07f39e2bf43098fd7e843d708ec75cdad76014b9fcef773cb9325bb3346b3ed6",
             "F154: Where Each Model Wins, on the Stored ULB Predictions", "Sprint 28 Task F (#47)",
             "experiments/phase2/results/f154_confusion.json, ten seeds 42-51",
             "Reference: the HSBC Phase 2 project's pairwise test of whether any stored model, classical, "
             "CVQBoost proxy or Dirac-3 hardware, is better than another on a subset of ULB",
             [["hsbc-2026", "every stored model pair on ULB, by amount and by day -- Bottom line"]]),
    "f111": ("docs/phase2/F111_LOKE_PROTOCOL.md", "bf7b589",
             "63fc82eb62f10d1cb5f0ebc8f617fc6c161d3abd2439d42df3f778f99bb1a570",
             "Experiment 4 (F111): the CVQBoost-KNN lane, the result",
             "Sprint 28 Task D (#51), 2026-10-22 (pilot) and 2026-10-23 (run)",
             "experiments/phase2/results/f111_loke_protocol.json, seeds 42-51, two protocols",
             "Reference: the HSBC Phase 2 project's re-run of the CVQBoost-KNN lane under Loke et al.'s protocol "
             "and its own, against the published 0.8108 and the stable HGB",
             [["hsbc-2026", "the CVQBoost-KNN lane under two protocols -- BLUF, Results and Reading"]]),
}
# The date of each document's last commit, for its citation.
DATES = {"f111": "2026-10-23"}


def src_id(key: str) -> str:
    return f"hsbc-qfraud-phase2-{key}-sprint28-result"


def source_bytes(key: str) -> bytes:
    """The document exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{DOCS[key][0]}"], capture_output=True,
                          check=True).stdout


def source_text(key: str) -> str:
    return plain(source_bytes(key).decode("utf-8").replace("**", ""))


def source_entry(key: str) -> dict:
    file, last, sha, heading, first, run, disposition, applicability = DOCS[key]
    return {
        "id": src_id(key), "kind": "reference", "context": applicability[0][0], "tier": "read",
        "title": heading,
        "citation": (f'hsbc-qfraud-phase2, "{heading}," {file}, commit {last}, '
                     f'{DATES.get(key, "2026-10-22")}; {first} '
                     "(hand-transcribed from the document's heading and first line and the repository's git log)"),
        "transcribed_from": f'the heading "{heading}" and the line "{first}"',
        "disposition": disposition,
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 {sha} at Phase 2 commit 10086da (the last commit to touch the file "
                     f"is {last}). Run: {run}. Phase 2's PR #46 was still a draft when this was read; a later "
                     "change is a later card. The private repository's URL is the citation's pointer; the record "
                     "depends on the commit. Read-only from this repository (F79)."),
        "found_via": "read from Phase 2 at Sprint 12 Phase 1.2, 2026-10-23 (carded as F102)",
        "cited_as": file,
        "checked_against_source": f"{TODAY}, Claude, read the whole document at commit 10086da via git show",
        "reads": [["Claude", TODAY, "full", "the whole document at commit 10086da"]],
        "applicability": applicability,
        "updated_reason": f"{TODAY}: added by scripts/sprint12_f102_phase2_sprint28.py ({TAG}); read in full",
    }


def A(key: str, **kw) -> tuple[str, AssertionRecord]:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "SIM")
    kw.setdefault("context", "ml")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    kw["provenance"] = f"{src_id(key)}, {kw['provenance']}"
    return key, AssertionRecord(**kw)


ASSERTIONS: list[tuple[str, AssertionRecord]] = [
    A("f151", id="f151-hgb-default-l2-zero-unstable-at-extreme-imbalance",
      value=("On deduplicated ULB (0.17% fraud; Phase 2's preparation, 13 features, seeds 42-46), scikit-learn's "
             "HistGradientBoostingClassifier with its default l2_regularization=0 was unstable: AUPRC mean "
             "0.375, SD 0.170, range 0.480. Setting l2_regularization=1.0 and nothing else gave mean 0.804, SD "
             "0.022, range 0.055, within 0.03 of Phase 1's XGBoost reference (0.816). The default ran 10 or 11 "
             "iterations on every seed (measured). Phase 2's mechanism, inferred: with no L2 term a leaf holding "
             "mostly frauds gets a very large value, so early stopping halts almost at once. A larger "
             "min_samples_leaf is not ruled out"),
      provenance="Bottom line, The controlled changes and Mechanism",
      citation_context=('"The cause is HGB\'s default `l2_regularization=0`." (Bottom line, markdown bold dropped); '
                        '"Setting it to 1.0, and changing nothing else, closes the spread" (Bottom line); '
                        '"seeds 42-46" (Bottom line); "13 mutual-information features" (The controlled changes); '
                        '"At 0.17% prevalence a leaf holding mostly frauds" (Mechanism); '
                        '"mean 0.804, SD 0.022, range 0.055, within 0.03 of Phase 1\'s XGBoost matched13 (0.816)" '
                        '(Bottom line); "The default fails it: mean 0.375, SD 0.170, range 0.480." (Bottom line); '
                        '"with no L2 term, a leaf\'s value is about -G / H" (Mechanism, "Inferred"); "The default\'s '
                        'early stopping then halts almost at once" (Mechanism, "Inferred"); "it ran 10 or 11 '
                        'iterations on every seed (`summary.default.n_iter`)" (Mechanism, measured: the run\'s '
                        'field); "Leading alternative not ruled out: a larger '
                        '`min_samples_leaf`" (Mechanism, markdown bold dropped)'),
      certainty_reasons=(OWN + ". HIGH for the measured spread under the controlled change; the mechanism is Phase "
                         "2's inference, attributed as such. Scope: one data set, five seeds")),
    A("f151", id="f151-cvqboost-proxy-below-stable-hgb-on-ulb", context="hsbc-2026",
      value=("Against the stable HGB (l2_regularization=1.0) on deduplicated ULB, both of Phase 2's F130 CVQBoost "
             "proxy variants score lower test AUPRC: the KNN variant by 0.027 (95% interval -0.046 to -0.008) and "
             "the dct baseline by 0.036 (-0.047 to -0.026). Phase 2 reverses F130's voided reading that the proxy "
             "beat HGB, which came from the unstable default comparator"),
      provenance="Bottom line",
      citation_context=('"Setting it to 1.0, and changing nothing else, closes the spread" (Bottom line); '
                        '"F130\'s voided ULB reading reverses." (Bottom line, markdown bold dropped); "KNN by 0.027 '
                        '(95% interval -0.046 to -0.008), the dct baseline by 0.036 (-0.047 to -0.026)" (Bottom '
                        'line); "F130\'s "beats HGB" came from a broken comparator." (Bottom line)'),
      certainty_reasons=OWN + ". Scope: one data set, five seeds; the proxy, not Dirac hardware"),
    A("f152", id="f152-ieee-cis-trees-beat-logistic-lightgbm-leads",
      value=("Trained on earlier months of IEEE-CIS and scored on later ones (five seeds, three rolling-origin "
             "folds), XGBoost beat logistic regression on floor-normalized AUPRC on both full months (month 4 "
             "+0.106, month 5 +0.359, 97.5% intervals excluding zero), as preregistered. LightGBM led every "
             "month (0.526, 0.536, 0.616), then the stable HGB, then XGBoost (secondary, uncorrected); logistic "
             "regression fell from 0.337 to 0.122 on month 5. Phase 2's stated limit: trained on drifting "
             "features; one data set"),
      provenance="BLUF, Results and What this does not settle",
      citation_context=('"trained on drifting features." (opening, markdown bold dropped); "Month 4: +0.106, '
                        '97.5% interval [+0.089, +0.123]. Month 5: +0.359 [+0.341, +0.378]." (BLUF); "LightGBM '
                        'leads on every month" (BLUF); "Month 4: LightGBM 0.526, HGB 0.499, XGBoost 0.443, '
                        'logistic 0.337." (Results, markdown bold dropped); "Month 5: LightGBM 0.536, HGB 0.496, '
                        'XGBoost 0.481, logistic 0.122." (Results, markdown bold dropped); "Month 6 (secondary, '
                        '8,111 rows): LightGBM 0.616" (Results, markdown bold dropped); "secondary, uncorrected, '
                        'each interval excluding zero" (BLUF); "One dataset, three folds from one six-month file." '
                        '(What this does not settle)'),
      certainty_reasons=(OWN + ". HIGH for the preregistered P1 and the measured AUPRC; the order among tree "
                         "lanes is secondary and uncorrected, and stated so")),
    A("f153", id="f153-learner-selection-formulation-fails-its-falsifier", context="hsbc-2026",
      value=("Phase 2's preregistered integer formulation for choosing weak learners (Experiment 3) failed its "
             "own falsifier on all six instances: at ridge weight 0.002 (the rule's fallback; no weight met the "
             "rule), the gap between the best selection found and the floor was 0.0016 to 0.0026, below the "
             "required 0.01, and greedy selection equalled the best objective any method found (SCIP stopped at "
             "its 300 s cap without improving on it). The device quote computed for it, 77 to 251 s on Dirac-3S "
             "(an inferred bracket), was not carried forward as ready. Phase 2's reading: the limit is the "
             "formulation, not the solver"),
      provenance="BLUF, Results and Reading",
      citation_context=('"Experiment 3 (F153): the proxy design, the result" (heading); '
                        '"the gap between the best selection found and the floor is 0.0016 to 0.0026, below the '
                        '0.01 the entry requires" (BLUF); "greedy equals the best objective found on all six '
                        'instances" (Results); "SCIP stopped at its 300 s cap on all six without improving on '
                        'greedy." (Results); "so no device quote is carried forward as ready" (BLUF, markdown bold '
                        'dropped); "Controls at 0.002: greedy equals the best objective found" (Results, markdown '
                        'bold dropped); "0.002, rule not met" (Results, markdown bold dropped); "Device quote: 77 '
                        'to 251 s on Dirac-3S (inferred bracket from F139\'s two Dirac-3 integer probes). Not '
                        'carried forward as ready (falsifier)." (Results, markdown bold dropped); "The limit is '
                        'the formulation, not the solver." (Reading)'),
      certainty_reasons=(OWN + ". HIGH for the measured falsifier. The device quote is Phase 2's inferred bracket, "
                         "and \"Consistent with F94 ... the limit is the formulation\" is Phase 2's reading, both "
                         "attributed as such. Scope: six instances of one formulation; no device run")),
    A("f153", id="f153-two-resolution-checks-disagree-in-kind", context="hsbc-2026",
      value=("On Phase 2's Experiment 3 Hamiltonians the max/min ratio of nonzero coefficients was about 2.01, far "
             "inside Dirac's 200:1 limit as QCi's answer of 2026-10-20 places it, so that half of the guide's "
             "check passes; but only 2.9% to 6.2% of coefficient pairs differed by at least max/200, so the "
             "guide's pairwise half fails. F104's gate, a separate check, also fails on all six. Which of the two "
             "the device honors is unverified"),
      provenance="Results and Reading",
      citation_context=('"Experiment 3 (F153): the proxy design, the result" (heading); '
                        '"the max/min ratio of the nonzero coefficients is about 2.01, far inside 200" (Results); '
                        '"only 2.9% (`mid`) to 6.2% (`free`) of coefficient pairs differ by at least max / 200" '
                        '(Results); "so that half passes" (Results, markdown bold dropped); "so the pairwise half '
                        'fails" (Results, markdown bold dropped); "The guide\'s check" (Results, markdown bold '
                        'dropped); "QCi\'s answer of 2026-10-20 placed the 200:1 limit" (Reading); "F104\'s gate: '
                        'fails on all six" (Results, markdown bold dropped); "Which of the two the device actually '
                        'honors is still unverified" (Reading, markdown bold dropped)'),
      certainty="moderate",
      certainty_reasons=(OWN + ". MODERATE: both measurements are exact, but which one bears on the device is "
                         "unverified, and the value is about that question. Bears on "
                         "dirac3s-analog-resolution-about-200-to-1; not linked (ADR-0004 A8 (b))")),
    A("f110", id="f110-cvqboost-pool-build-grows-faster-than-rows", context="hsbc-2026",
      value=("Timing Phase 2's CVQBoost proxy fit against training rows (five seeds, four row fractions up to "
             "170,235 rows), the serial weak-learner pool build was the largest part at every row count and grew "
             "with a log-log slope of 1.40 (91 variables) and 1.44 (833 variables), both 97.5% intervals above "
             "the preregistered band [0.7, 1.3]: the linear-growth prediction is false. At full rows the "
             "833-variable build took 773 s on average"),
      provenance="BLUF and Results",
      citation_context=('"both 97.5% intervals are above the predicted band [0.7, 1.3]" (BLUF); '
                        '"91 variables: 1.40 [1.35, 1.45]. P1 band [0.7, 1.3]: outside." (Results); "833 variables: '
                        '1.44 [1.38, 1.49]. Outside." (Results); "The build is the largest part at every fraction in '
                        'both cells." (Results); "P1 is false at both cell sizes." (BLUF, markdown bold dropped); '
                        '"(17,023 / 42,559 / 85,118 / 170,235 rows)" (Results); "build 28.4 / 115 / 301 / 773" '
                        '(Results, 833 variables)'),
      certainty_reasons=OWN + ". Scope: one machine, a serial build (the parallel builder needs fork)"),
    A("f110", id="f110-proxy-solve-flat-paper-2s-not-like-for-like", context="hsbc-2026",
      value=("In the same timing, the proxy solve at 833 variables was flat in rows at about 0.35 s (slope -0.03, "
             "interval inside the predicted band); at 91 variables the solve took 0 to 4 ms and could not be "
             "read (9 of 20 below the timer's resolution). Phase 2 infers, from the slope, about 650 s of training "
             "at 150,000 rows and 833 variables (about 50 s at 91) against the 2 s QCi's paper reports; even with "
             "the build divided by the processor count (32), an ideal a real parallel build does not reach, about "
             "20 s and about 2 s. Phase 2 states the comparison is not like for like: the paper's pool size, weak "
             "learners and hardware are not stated in what Phase 2 holds, and its 2 s may exclude the pool build"),
      provenance="BLUF, Results and Beside the predictions",
      citation_context=('"At 833 variables the solve is flat in rows, at about 0.35 s." (BLUF); "833 variables: '
                        '-0.03 [-0.13, 0.07]. Inside." (Results); "At 91 variables it takes 0 to 4 ms, and 9 of 20 '
                        'solves are below the timer\'s resolution." (BLUF); "the full training is about 650 s at 833 '
                        'variables and about 50 s at 91 variables" (Beside the predictions); "If the build were '
                        'divided by the processor count (32), an ideal that a real parallel build does not reach, '
                        'the 833-variable training would still be about 20 s; the 91-variable training would be '
                        'about 2 s." (Beside the predictions); "the paper\'s pool size, weak learners and hardware '
                        'are not stated in what we hold" (Beside the predictions); "The paper\'s 2 s at 150,000 '
                        'rows." (Beside the '
                        'predictions, markdown bold dropped); "That scaling is an inference from the fitted slope, '
                        'not a measurement." (Beside the predictions); "The comparison is not like for like" (Beside '
                        'the predictions); "its 2 s may exclude the pool build" (Beside the predictions)'),
      certainty_reasons=(OWN + ". HIGH for the measured solve; the 650 s is Phase 2's extrapolation and the 2 s "
                         "comparison its inference, both attributed as such")),
    A("f114", id="f114-calibrated-plugin-misses-known-ceiling",
      value=("On F108's simulator, whose Bayes error is known, an isotonic-calibrated plug-in built on the stable "
             "HGB (l2_regularization=1.0, fit on 75% of training rows) recovered the ceiling on 2 of 5 seeds on "
             "the main arm, where 4 are needed, the same count as F108's default plug-in; every seed overestimated "
             "the Bayes error by about 3% to 13%, and calibration moved the estimate by less than 0.0002. On the "
             "other two arms it did worse than F108's default plug-in, which recovered 5 of 5 on each: 3 of 5 on "
             "the noise arm and 0 of 5 on the zero-ceiling arm. Two changes happened at once (the regularization "
             "and the smaller fitting set), and this run cannot separate them. So F114 stays blocked. Compare f108-hgb-plugin-overstates-bayes-error-5-to-12-percent (a different model "
             "and fitting set; not linked, ADR-0004 A8 (b))"),
      provenance="BLUF, What ran and Results",
      citation_context=('"The calibrated plug-in does not recover the ceiling, so F114 stays blocked." (BLUF, '
                        'markdown bold dropped); "it is within the margin on 2 of 5 seeds; the rule needs 4" (BLUF); '
                        '"differ by less than 0.0002 on every seed" (BLUF); "Every seed\'s estimate is above the Bayes '
                        'error, by about 3% to 13%" (Results, markdown bold dropped); "fit on 75% of the training '
                        'rows" (What ran); "(`l2_regularization=1.0`)" (What ran); "Noise arm: calibrated 3 of 5, '
                        'uncalibrated 4 of 5. F108\'s default plug-in recovered 5 of 5 here." (Results, markdown '
                        'bold dropped); "Zero-ceiling reference arm: calibrated 0 of 5, uncalibrated 1 of 5." '
                        '(Results, markdown bold dropped); "Two changes happened at once: the regularization and '
                        'the smaller fitting set (75% of train). This run cannot separate them" (Reading)'),
      certainty_reasons=OWN + ". Scope: one simulator, five seeds"),
    A("f154", id="f154-no-stored-model-better-on-a-ulb-subset", context="hsbc-2026",
      value=("Across 66 pairs of Phase 2's stored ULB models (classical lanes, three CVQBoost proxy setups, Dirac-3 "
             "hardware; ten seeds), none was reliably better than another on either subset tested (amount above "
             "the median, or day 1): no interaction interval excluded zero at the Bonferroni level over 132 "
             "tests, and the verdict did not change with tied scores given a tie-neutral share. In every pair both "
             "models flagged at least 776 of the 950 test frauds, and over all ten seeds at most 34 were caught by "
             "one and missed by the other (the catch counts of the heavily tied families are inflated by the tied "
             "rows). Phase 2's stated limit: one fraud moves a subset's recall by about 2-3 points, so a small "
             "subset effect is below what the design can see. Phase 2 infers an ensemble routing on these subsets "
             "would not help; a subset defined otherwise is not ruled out"),
      provenance="Bottom line, What was compared and Why the test is the interaction",
      citation_context=('"No stored model is reliably better than another on either subset." (Bottom line, '
                        'markdown bold dropped); "None of the 132 primary tests (66 pairs, 2 subsets) has an '
                        'interaction interval that excludes zero." (Bottom line); "both models flag at least 776 of '
                        'the 950 test frauds" (Bottom line); "number at most 34 over all ten seeds" (Bottom line); '
                        '"Bonferroni over the family, m = 132" (Why the test is the interaction, markdown bold '
                        'dropped); "day (`Time` below 86,400 s, or not)" (What was compared); "on day 1" (Why the '
                        'test is the interaction); "these files give an ensemble no subset to route on" (Bottom '
                        'line); "a subset '
                        'defined by something other than amount or day" (Bottom line); "With tied scores given a '
                        'tie-neutral share instead of all being flagged, still none fires." (Bottom line); "Their '
                        'catch counts are inflated by those extra rows." (Limits); "the verdict does not change" '
                        '(Limits); "One fraud moves a subset\'s recall by about 2-3 points, so a small subset effect '
                        'is below what this design can see." (Limits)'),
      certainty_reasons=(OWN + ". HIGH for the null as tested; the ensemble reading is Phase 2's inference, "
                         "attributed as such. Scope: stored predictions, two subsets, 95 frauds per seed")),
    A("f111", id="f111-cvqboost-knn-lane-below-published-value-under-loke-protocol", context="hsbc-2026",
      value=("Re-running the CVQBoost-KNN lane under Loke et al.'s protocol (no deduplication, a 70/30 stratified "
             "split, SMOTETomek at 0.02; seeds 42-51; solved classically on the Hamiltonian eqc-models sends, no "
             "device), Phase 2 measured mean AUC-PR 0.760 (range 0.683-0.829), 0.051 below the published 0.8108 "
             "and outside its preregistered tolerance of 0.03. The paper's seeds cannot be recovered and settings "
             "it leaves open may differ, so Phase 2 does not claim the published value is wrong"),
      provenance="BLUF, Results, Reading and What was not done",
      citation_context=('"The lane is not consistent with the published 0.8108." (BLUF, markdown bold dropped); '
                        '"Its mean under A is 0.760, 0.051 below; the entry\'s tolerance is 0.03." (BLUF); '
                        '"Protocol A (Loke et al.\'s: no deduplication, 70/30 stratified, SMOTETomek at 0.02)" '
                        '(The pilot, markdown bold dropped); "Seeds 42-51, both protocols, both lanes" (Results); '
                        '"KNN lane AUC-PR: A mean 0.760 (range 0.683-0.829)" (Results, markdown bold dropped); '
                        '"The paper\'s seeds cannot be recovered, and settings it leaves open (feature count, '
                        'resampling ratio) may differ." (Reading); "so it does not claim the published value is '
                        'wrong" (Reading); "No device: the lane was solved classically on the Hamiltonian '
                        'eqc-models sends." (What was not done)'),
      certainty_reasons=(OWN + ". HIGH for the measured lane; the protocol is Phase 2's reading of Loke et al.'s "
                         "paper and code. Scope: ten seeds, one data set, no device. Bears on "
                         "cvqboost-knn-aucpr-0-8108-kaggle-fraud; not linked (ADR-0004 A8 (b)): Phase 2 cannot say "
                         "why the published value is not reached")),
    A("f111", id="f111-stable-hgb-beats-cvqboost-knn-lane-under-both-protocols", context="hsbc-2026",
      value=("Under both protocols on ULB (seeds 42-51), Phase 2's stable HGB (F151's setting) scored higher AUC-PR "
             "than the CVQBoost-KNN lane: by 0.082 (interval 0.061 to 0.104) under Loke et al.'s protocol and by "
             "0.033 (0.014 to 0.053) under Phase 2's deduplicated one, with no resampling. Phase 2: for a QML claim "
             "on ULB the comparison that matters is against a stable classical model on the same rows"),
      provenance="BLUF, Results and Reading",
      citation_context=('"The stable HGB beats the KNN lane under both protocols: by 0.082 [0.061, 0.104] under A '
                        'and by 0.033 [0.014, 0.053] under B." (BLUF, markdown bold dropped); "HGB AUC-PR (F151\'s '
                        'stable setting)" (Results, markdown bold dropped); "Seeds 42-51, both protocols, both '
                        'lanes" (Results); "Protocol B (ours: deduplicated, 60/20/20, no resampling)" (The pilot, '
                        'markdown bold dropped); "For a QML claim on ULB, the comparison that matters is against a '
                        'stable classical model on the same rows" (Reading, markdown bold dropped)'),
      certainty_reasons=OWN + ". Scope: ten seeds, one data set, the lane solved classically, no device"),
    A("f111", id="f111-protocol-moves-hgb-not-measurably-the-knn-lane", context="hsbc-2026",
      value=("Phase 2's primary result for the CVQBoost-KNN lane: Loke et al.'s protocol against Phase 2's did not "
             "measurably change it (AUC-PR difference -0.014, 95% interval -0.046 to +0.019, 10 paired seeds), but "
             "it did move the stable HGB (+0.035, +0.008 to +0.062). Under Loke et al.'s protocol 267 to 329 "
             "evaluation rows per seed have an exact copy in the training rows; the protocols differ in more than "
             "duplicates, so the run cannot say which part moves HGB"),
      provenance="BLUF and What was not done",
      citation_context=('"Primary result: the protocol does not measurably change the KNN lane." (BLUF, markdown '
                        'bold dropped); "-0.014, 95% interval [-0.046, +0.019], 10 paired seeds" (BLUF); "The '
                        'protocol does move HGB: A minus B is +0.035 [+0.008, +0.062]." (BLUF, markdown bold '
                        'dropped); "under A, 267 to 329 evaluation rows per seed (mean 303.5) have an exact copy in '
                        'the training rows" (BLUF); "A differs from B in more than duplicates" (BLUF); "so this run '
                        'cannot say which part moves it" (BLUF)'),
      certainty_reasons=OWN + ". Scope: ten paired seeds, one data set, the lane solved classically, no device"),
]


def check_hashes() -> list[str]:
    return [f"{k}: blob at {COMMIT[:7]} has changed" for k, d in DOCS.items()
            if hashlib.sha256(source_bytes(k)).hexdigest() != d[2]]


def verify_all() -> list:
    """Every quote verbatim in its document at COMMIT BEFORE anything is
    written (INTAKE_WORKFLOW.md sections 26, 31 and 41)."""
    texts = {k: source_text(k) for k in DOCS}
    return [(k, a, require_verbatim(a.id, a.citation_context, texts[k], value=a.value)) for k, a in ASSERTIONS]


def apply_changes(conn) -> list[str]:
    checked = verify_all()
    log = []
    for key in DOCS:
        if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (src_id(key),)).fetchone() is None:
            insert_paper(conn, intake.build_record(source_entry(key), today=TODAY))
            log.append(f"paper  {src_id(key)}")
    for key, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            insert_verified_assertion(conn, a, verified, yielded_by=src_id(key))
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
        for key in DOCS:
            intake.build_record(source_entry(key), today=TODAY)  # validates the entry; nothing written
            print(f"paper  {src_id(key)} [read]")
        for key, a, _ in verify_all():
            validate_assertion(a)  # the checks insert_assertion runs; nothing written
            print(f"assert {a.id} <- {key} [{a.certainty}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F102 Phase 2 Sprint 28 results")
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
