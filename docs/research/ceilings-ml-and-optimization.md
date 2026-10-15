# Can this dataset or problem be done better? Ceilings for ML and bounds for optimization

Sprint 9 Task E (F78), 2026-10-15. Every count below is a snapshot as of
2026-10-15. The team lead's question, 2026-10-14: "is there a way to find
the maximum, near maximum predictions or can't be better than... on any ML
dataset and/or any optimization problem. This will be helpful at least on
wether further improvement can be done on a dataset or if a better dataset
is needed."

Sections 1 to 4 are **verified**: each point names the store assertion that
holds it, with its quote and anchor in the store. Section 5 is **inferred**:
the coordinator's reasoning from those sources, not stated by any of them.
Keep the two apart when citing this document.

## Short answer

- **For an ML dataset, yes in principle, never exactly in practice.** The
  ceiling is the Bayes error: the lowest error any classifier can reach on
  that data distribution. No method computes it for real data. Several
  estimate it, bound it, or compute it for a model of the data, and each
  fails under named conditions (section 1).
- **No estimator read here has been tested at a fraud-like positive rate.**
  Wheat et al. drew equal numbers of points per class
  (`wheat-equal-class-sizes-no-imbalance-tested`); Ishida et al. report no
  class-imbalanced experiment and need the class prior for their
  positive-confidence estimator (`ishida-pconf-needs-class-prior`);
  confident learning was shown on imbalanced data only at 9, 12 and 79
  percent (`cl-threshold-design-targets-class-imbalance`). Card fraud is
  about 0.2 percent positive. This is the largest gap for HSBC's use.
  (Corrected 2026-10-15 after review: the first version said "the lowest
  Bayes error any of these studies simulated was 1 percent", which was
  false, since Theisen et al. report flow-model Bayes errors as low as
  1.07e-4, and which confused the Bayes error with the positive rate.)
- **For an optimization problem, yes, in two narrow ways from the store:**
  instances whose optimum is known by construction (planted) or published
  (best-known), and minimax lower bounds that hold for a whole class of
  problems, not for one instance (section 2). Per-instance certificates
  (relaxations and duality gaps) are standard practice but are not yet in
  the store (section 5).
- **Optimization is one family of claimed QML advantage, not the basis of
  all of them.** Of 85 QML titles in the store that claim an advantage, 16
  are optimization claims; the rest are kernels, sampling, learning theory,
  quantum data, dynamics, linear algebra, or name no mechanism (section 3).

## 1. Ways to find a ceiling for an ML dataset (verified)

| Method | What it gives | What it needs | Fails or misleads when | Store assertions |
|---|---|---|---|---|
| Soft-label estimator (mean of min(p, 1-p)) | An unbiased estimate of the Bayes error, with no model and no features | A class probability per example, for example from several human reviewers | Soft labels are noisy (biased unless sign labels exist); calibrated labels can still be badly wrong | `ishida-soft-label-mean-min-unbiased`, `ishida-naive-noisy-soft-labels-biased`, `ushio-calibration-guarantee-not-enough`, `ushio-isotonic-calibration-consistent-if-ordered`, `bestperf-bayes-error-mean-min-p` |
| Model reached the estimate | A check that a model has reached the ceiling | The estimate above | A model can score below the estimated ceiling when labeling procedures differ | `ishida-vit-below-estimated-bayes-error-cifar10`, `ishida-fashion-mnist-gap-small` |
| Nearest-neighbor and graph (kNN, GHP) estimators | Lower and upper bounds on the Bayes error from features | Many samples per class, few dimensions, a good embedding | Over 4 to 10 features, or under about 1,000 to 2,500 samples per class; no estimator wins both bounds | `wheat-samples-per-class-for-5pct-range`, `wheat-requirement-depends-on-scenario`, `wheat-knn-best-no-estimator-meets-all-goals`, `renggli-knn-ghp-best-lower-bound-estimators`, `renggli-feature-transformation-required`, `renggli-no-estimator-wins-both-bounds` |
| Testing an estimator without the true value (FeeBee) | A score for how well an estimator tracks known label-noise increases | A strong state-of-the-art error | The state of the art is weak (YELP), so failures go unseen | `renggli-feebee-label-noise-lemma`, `renggli-framework-needs-strong-sota`, `feebee-bound-corridor-under-noise` |
| Normalizing flows | The exact Bayes error of a fitted generative model | A flow model that fits the data well | The flow fits poorly; there is no measure of how far its Bayes error is from the data's | `theisen-bayes-error-invariant-invertible-map`, `theisen-no-guarantee-flow-matches-true-bayes`, `theisen-sota-near-optimal-only-when-easy` |
| Information bounds (Fano, Hellman and Raviv; F-score and cost bounds) | A lower and an upper bound on the Bayes error, and an interval for the best F-score, from the conditional entropy H(y given x) | H(y given x) or the mutual information between features and label | The interval for F-score is wide; maximizing mutual information can give a low F-score | `fano-hellman-bayes-error-bounds-two-class`, `max-fscore-bounds-from-conditional-entropy`, `infomax-can-yield-low-fscore-and-high-cost-risk`, `fano-binary-case-uses-exact-form-not-simplified` |
| Estimating mutual information | The input the information bounds need | Low-dimensional structure in the data | KSG fails from 13 dimensions, MINE from 25, InfoNCE from 37 (one Gaussian study); no estimator is accurate without assumptions | `ksg-mine-infonce-fail-dimension-thresholds-gaussian`, `no-mi-estimator-accurate-without-strong-assumptions`, `neural-mi-accuracy-needs-low-dim-latent-structure` |
| Annotator agreement (label convergence) | An upper bound on the metric set by contradictory labels | Examples labeled twice | One labeling convention dominates; the subset is not representative | `tschirschwitz-lvis-label-convergence-interval`, `tschirschwitz-derivation-interannotator-map`, `tschirschwitz-bound-fails-with-dominant-convention` |
| Label-noise estimation | An estimate of how much of the data is mislabeled, and a lower bound on proper-loss risk under label noise (not on accuracy) | Out-of-sample probabilities; noise that depends only on the class | Noise depends on the features; classes overlap; a flagged count mixes errors with ambiguous cases | `cl-estimates-joint-noisy-true-labels-by-counting`, `cl-assumes-class-conditional-noise`, `blanchard-identifiability-two-conditions`, `blanchard-class-overlap-separate-from-label-noise`, `toner-label-noise-implies-risk-lower-bound` |
| Learning curves (error(N) = aN^-b + c) | A floor c for one model class and setup | Training on several data sizes | c is per model and setup, not a dataset floor; extrapolation beyond 10 times the data is unreliable | `ding-floor-c-is-model-and-config-specific`, `ding-extrapolation-beyond-10x-unreliable`, `ding-replicator-cv-b-0144-protocol-spread` |
| Uncertainty methods (ensembles, Bayesian) | A split into reducible and irreducible uncertainty | A second-order model | Model bias inflates the "irreducible" part; epistemic estimates are lower bounds | `jimenez-bias-inflates-aleatoric-and-hides-epistemic`, `jimenez-epistemic-estimates-are-lower-bounds-incomplete` |
| Synthetic data with a known label process | A dataset whose labeling rule is written down (none of these papers computes a ceiling from it; see section 5) | A simulator | The simulator's rule is an assumption, not real fraud; in some simulators the label is not a fixed rule on the observable columns | `allen-cardsim-label-is-naive-bayes-rank-cutoff`, `altman-amlworld-labels-complete-by-construction`, `ostman-amlgentex-node-label-from-pattern-membership`, `amlsim-label-set-by-alert-flag`, `fdh-sim-scenario3-label-not-function-of-features` |
| A metric's floor | The worst score any ranking can get | The positive rate | It is a floor, not a ceiling | `boyd-theorem1-min-precision-given-recall`, `boyd-theorem2-min-aucpr-formula` |

Two fraud-specific results bear directly on "better model or better data":

- **The information environment sets a floor.** In card networks, label
  censorship, decline rate and label corruption multiply in the
  denominator of a regret lower bound, while model complexity enters only
  as log N (`dhama-theorem9-regret-floor-form`,
  `dhama-investment-priority-corollary`). The paper gives no numbers and
  calls the result a floor, not a forecast
  (`dhama-not-a-forecast-no-numbers`).
- **A detector's ceiling depends on how much evidence each case carries.**
  For trust fraud on Bitcoin-OTC, the F1 ceiling for count-based detectors
  rises from 0.487 at one rating to 0.883 above ten
  (`butt-table4-ceiling-rises-with-n`); at one rating, the achieved F1
  exceeded the stated ceiling (`butt-table4-n1-achieved-exceeds-ceiling`),
  so the ceiling is not strict as computed.

## 2. Bounds for optimization problems (verified)

- **Minimax lower bounds for a class of problems.** Fano's inequality and
  the data processing inequality lower-bound the optimality gap any
  algorithm can guarantee after n noisy queries, over a finite set of hard
  functions (`fano-extends-to-noisy-optimization-minimax-risk`). This is a
  worst case over the class, not a bound for one instance, and Fano-based
  bounds can be weak at finite sample size
  (`fano-bounds-weak-nonasymptotic-and-adaptive-limits`).
- **Instances with a known optimum.** Planted instances have their optimum
  by construction, which is how QCi's own review shows that its "optimal on
  every instance" headline does not hold at the harder contrast
  (`dirac3s-all-optimal-headline-contradicted-by-own-table`). Library
  instances with published best-known values (QPLIB) show how close a
  solver gets, and on QCi's three QPLIB instances all three solvers matched
  them (`dirac3s-qplib-results-do-not-separate-solvers`).

## 3. Where claimed QML advantages come from (computed, not verified)

`python scripts/qml_advantage_families.py` sorts every `qml` paper whose
title claims an advantage, a speedup or an enhancement. Snapshot as of
2026-10-15: 85 of 1,706.

- other or unspecified (the title names no mechanism): 34
- optimization: 16
- sampling and generative models: 9
- kernels and feature maps: 8
- learning theory: 8
- quantum data and sensing: 5
- quantum dynamics (reservoirs, simulation): 4
- linear algebra: 1

This is a sort of **claims by title**, not evidence that any advantage
holds. The counts are rough: the "optimization" 16 include a code record
that duplicates its paper ("Evidence of Scaling Advantage..."), a
counter-claim ("The Quantum Approximate Optimization Algorithm Can Require
Exponential Time to Optimize Linear Functions") and a comparison between two
quantum methods ("Advantages of multistage quantum walks over QAOA"). Re-run
the script for current counts.

## 4. F46's nine ceiling facts (verified dispositions)

| Fact | Disposition | Why |
|---|---|---|
| F-701 | entered, corrected | Sample sizes right; "collapses beyond 4 features" and "equal priors" overstated |
| F-703 | merged | McDermott, already read, yields the same statement |
| F-704 | not entered | An absence claim from one second-hand search; the 33 sources read are not a literature search |
| F-705 | entered, corrected | Proved; the paper calls its bounds sharp, not loose |
| F-706 | entered, corrected | The thresholds are from one Gaussian simulation (Gowri et al.); the KSG bias formula has no source here |
| F-707 | entered in part | The scenario rules match the code; the zero-Bayes-error corollary does not hold on the observable columns |
| F-708 | entered, corrected | Three impairments in the denominator, delay in the numerator, all under a square root |
| F-709 | entered, corrected | c is a model-and-setup floor; "preprocessing alone" overstated |
| F-710 | refuted in detail | The direct read of Kakavand found classical kernels significantly better on 6 of 7 datasets and a quantum kernel better on one |

The machine-readable version is `FACT_DISPOSITIONS` in
`scripts/sprint9_f78_ceiling_reading.py`.

## 5. Inferred: how to apply this to HSBC fraud (coordinator, not in any source)

None of the following is stated by the sources read. It is a plan built
from them, to be tested.

0. **A simulator with a written-down labeling rule makes its own ceiling
   computable in principle**: score each record with the generator's rule
   (CardSim's naive Bayes posterior, for example) and measure how well that
   ideal scorer does. None of the simulator papers does this, and where the
   label depends on random draws the observable columns do not determine it.

1. **Measure label quality first.** Have several reviewers label a
   stratified sample of transactions, frauds over-sampled, and record each
   reviewer's call. The share of disagreement bounds what any model can
   score against those labels (the Tschirschwitz and Ishida ideas). If
   reviewers disagree often, better labels come before a better model.
2. **Estimate the Bayes error from those soft labels** (Ishida; Ushio with
   isotonic calibration). This needs no features, so the dimension limits of
   section 1 do not apply. It has not been tested at 0.2 percent, so check
   it first on a simulator with a known rule (CardSim or the handbook
   simulator), where the true answer can be computed.
3. **Fit learning curves per model family** (Ding). If the floor c of the
   best family is close to its current error, more data of the same kind
   will not help; new information (features, labels, faster feedback) is
   what can.
4. **Treat a small model-to-model gain as a signal about the data.** On
   IEEE-CIS, fusing strong boosted trees gained about two AUPRC points over
   the best single model (`han-fusion-gain-over-best-single-model-modest`).
   Together with Dhama's result, a pattern of small gains from model changes
   points at the information environment, not the model.
5. **For an optimization problem instance**, the standard certificate is a
   bound from a relaxation or a dual (linear or semidefinite relaxation,
   Lagrangian dual, the branch-and-bound gap reported by an exact solver):
   any solution within that gap of the bound is provably near-optimal. This
   is general operations-research practice, **not sourced in the store
   yet**; F83 cards entering primary sources for it.

## Open gaps

- No source read tests a positive rate near 0.2 percent.
- Chen et al. 2025 (Machine Learning, a Bayes-error estimator) and Han and
  Verdu 1994 (IEEE Transactions on Information Theory, generalizing Fano)
  are not read yet: no free copy; they are on the team lead's hand-download
  list.
- Per-instance optimization bounds have no source in the store (F83).
