# F118: what the store says, what it means for the fraud challenge, and what to run next

Sprint 14 Task G (F118, #147), written 2026-10-30 and updated
2026-10-31. **Every count in this memo is a snapshot as of 2026-10-31**,
taken after F114's last 19 groups of the first release entered
(0eddd23) and their corrections were applied (the last with backup
`evidence-20261031T173833940424`). The theme readers read the store of
2026-10-30, after F114's corrected re-apply (4d969d9); the Limits
section says how the later entries were checked. The store grows by
design; rerun `scripts/f118_themes.py` for current counts.

## Bottom line

- **In the 16 themes read, the store holds no result in which a quantum
  model beats a tuned classical model on tabular, imbalanced data.** Every positive fraud
  result is a simulation on a small or rebalanced subset, against an
  untuned or published comparator. Phase 1 and Phase 2's own results are
  nulls against tuned boosting.
- **What is proved is mostly limits.** Barren plateaus, kernel
  concentration, dequantization of classical-data algorithms, and the
  generalization bound all bind as qubits grow. The proved advantages
  are on constructed or cryptographic problems, not on tabular data.
- **For Exp 3 (feature selection on Dirac-3S), the themes read hold no
  HIGH or independent case in which a quantum or quantum-inspired solver
  beats a tuned classical comparator.** Four single studies, all LOW,
  report quantum feature selection as competitive or better
  (orquin-qfs-competitive, varqfs-vs-classical, qaoa-fs-comparable,
  hellstern-dataset-dependent); their comparators were not tuned for the
  comparison. The benchmark solvers ran at fixed settings, not tuned per
  instance, and penalty weights were not tuned. Phase 2's own falsifier
  result says the formulation, not the solver, is the limit.
- **Phase 2 has since answered the solver question on IEEE-CIS** (its
  F176, Sprint 30, read at d14fdb7): a classical solver got below greedy
  on 3 of 6 instances, each by under 2e-05, against room of about 0.08
  to 0.097, and SCIP did not beat greedy in 1,200 s on any. The
  formulation, not the solver, is the limit there, and gains that small
  may sit below what Dirac-3S resolves.
- **The cheapest, most decisive next steps are classical**: the same
  solver test on the f153 instances, an equal-feature ablation, a
  classical surrogate for any quantum kernel, and a rounding test of
  whether Dirac-3S could resolve F176's gains. These run in minutes and
  decide whether any device time is worth spending before 14 Nov 2026.
- **At production scale the gap widens toward classical.** ULB (284,807
  rows, 30 features) is toy-sized; production fraud data runs to 20 to
  100 million rows a day. Classical training grows about linearly in
  rows; every quantum learner that reads all rows pays at least linear
  loading at a far slower clock, times shots, and per-transaction quantum
  scoring cannot meet a millisecond budget. The quantum steps that fit
  that scale act on a small summary (a feature-selection or weak-learner
  QUBO built from streamed statistics) or on a sample (section "At
  production scale").

## How this memo was made

1. **Questions.** Phase 2's decisions were read from
   `hsbc-qfraud-phase2` at commit 5dfdfc5 (2026-10-30 09:27 -0400),
   `docs/phase2/PHASE2_POC_PLAN_DRAFT.md` (its six experiments) and
   `docs/phase2/PHASE2_POC_PLAN.md`, read only through `git show`. The
   team lead's own questions are on F118's card in
   `docs/ALL_SPRINTS_MASTER_PLAN.md`, kept verbatim there.
2. **Inventory, computed.** `scripts/f118_themes.py` (read only) counts
   the store and selects 16 themes by keyword on each assertion's value.
3. **Read per theme.** Five Sonnet 5.5 readers, one per group of themes,
   each read its packets and the store's quotes and wrote what is settled
   (HIGH), what is only measured or claimed and under what conditions,
   where assertions conflict, and what is missing. Their reports are in
   the non-repository folder `work\f118\readers\`.
4. **Synthesis.** Opus 5.5 wrote this memo from the five reports. Each id
   cited below was checked to exist in the store, and 10 were read
   against their stored value (section "Citations checked").

## The questions

**From Phase 2** (`hsbc-qfraud-phase2` at 5dfdfc5,
`docs/phase2/PHASE2_POC_PLAN_DRAFT.md`), its six experiments:

1. Exp 1: what confounds a quantum-against-classical comparison.
2. Exp 2: whether results hold over time (temporal validity).
3. Exp 3: cardinality-constrained feature or learner selection on
   Dirac-3S, the critical path; greedy ends 0.096 to 0.098 above the
   floor.
4. Exp 4: replication under Loke's protocol (done).
5. Exp 5: transfer across segments (on hold).
6. Exp 6: training time against sample count.

**From the team lead** (F118's card, 2026-10-30, verbatim):

7. "how gates work, what sets of gates can be used for what purpose
   (guessing that there are micro algorithms (small set of gates) that
   can be used to do X that are useful"
8. "what are the micro algorithms that appear to be useful (math, how
   to store data, how to read data in, how to get data out)"
9. "is there anything useful that is not hybrid between QC and
   Classical?"
10. "what are the best practices for hybrid algorithms"
11. "how can the unique properties of QC (entanglement, superposition,
    interference and ???) be taken advantage of and for what use cases"
12. "where does quantum advantage show itself": "what use cases are
    proven/nearly proven (just need more qubits or gates or ???)"; "what
    use cases are most likely for quantum advantage (all)"; "about how
    many qubits would it take for each use case to reach advantage";
    "are the use cases limited to search and optimization (grouping,
    routing, selection, scheduling,...)"
13. "how does ML using QC/Classical hybrid fit in": Gradient Boost
    (XGBoost, CatBoost, LightGBM); Bagging ensembles (Random Forest,
    Balanced RF, Extra Trees); linear and probabilistic (Logistic
    Regression, Linear SVM, Naive Bayes); Anomaly detection (One-Class
    SVM, Local Outlier Factor, Isolation Forest); Neural Networks (MLP,
    ResNet, Deep Learning); "Any others that might be useful to try?"
14. "how might QC be applied to GenAI training or Inference and how many
    qubits would be needed?"

**Grades.** HIGH means a definition, a proved result, a setup, a scope
or a limit the paper itself establishes. LOW means measured, simulated,
claimed, resting on a cited result, or a vendor's own claim. A measured
result is LOW by rule however well it was run. Phase 2's own
measurements are graded HIGH as measurements of record (ADR-0004's
consumer rule), which is not the same as a proof; this memo says so
where it matters.

## Inventory (snapshot 2026-10-31)

- 23,653 assertions on 2,345 paper records.
- By context: `qml` 11,497; `qc` 8,026; `ml` 1,766; `method` 1,604;
  `world` 566; `hsbc-2026` 88; Dirac platforms 106 (`dirac-3s` 50,
  `dirac-3` 44, `dirac-1` 12). An assertion may carry more than one
  context.
- By certainty: LOW 15,386 (65%); HIGH 8,167 (35%); MODERATE 97;
  very-low 1; none 2.
- By claim type: positive 18,745; absence 4,255; vendor's own claim 653.
- Tagged SIM 31, HW 16, PROJ 2; the rest carry no tag.
- Paper reads: 596 `full`, 2,199 `partial`, 1,629 `subagent`, 1 `grep`.
  Papers by tier: 1,789 `read`, 556 `seen`.
- Theme sizes (assertions / of which HIGH): advantage 1,452 / 280;
  kernels 791 / 262; trainability 848 / 265; encoding and readout
  966 / 372; noise and mitigation 829 / 233; generalization 506 / 150;
  tensor networks 313 / 93; QUBO and feature selection 1,652 / 461;
  fraud and imbalance 302 / 107; benchmarking 1,501 / 483; gates and
  primitives 2,254 / 712; hybrid practice 2,025 / 675; quantum resources
  828 / 253; resource estimates 1,077 / 347; classical families 436 /
  117; GenAI 327 / 108. A keyword cut, not a classification: the readers
  dropped what did not bear. The readers' packets were cut on
  2026-10-30, about a fifth smaller per theme than these counts; the
  later entries were checked as the Limits section says, and every id
  cited here was checked against the store on 2026-10-31.

**Limits of this memo.**
- 65% of the assertions are LOW, and the `partial` reads outnumber the
  `full` ones four to one. A LOW finding is one study's report.
- The theme readers read the store before F114's last 19 groups entered
  (5,000 assertions, 2026-10-31). Those were searched for HIGH
  assertions on advantage, fraud, imbalance, tabular data, kernels,
  feature selection, QUBO and dequantization (119 hits); none reports a
  quantum model beating a tuned classical one, so the bottom line
  stands. 18 papers stay out of the store (the team lead's decision)
  and 8 records are unread (F125).
- The readers note that several proved theorems are graded LOW where
  the stored value does not quote the bound (for example
  kernel-exponential-concentration). Such a result is cited here with
  its grade and the note.

## What the store has taught us, per theme

The 16 themes are written as 13 sections. Three are merged where the
readers found them inseparable: quantum resources and resource
estimates go under Advantage, and benchmarking goes under Fraud,
imbalance and benchmarking.

### Advantage, and where it shows

- **Settled.** Grover search is a quadratic, optimal speedup
  (qml-grover-quadratic-speedup-optimal). Exponential separations are
  proved only on constructed problems: RSA-based optimization instances
  (pirnay-superpoly-advantage), discrete-log learning
  (discrete-log-projected-kernel-advantage), shadow models
  (shadow-advantage-theorem) and continuous-variable state learning
  (coroi-ef-lower-bound). For classical data no exponential advantage is
  known (cerezo-no-known-exponential-advantage-classical-data, HIGH).
- **Not limited to search and optimization.** The stated use cases also
  include sampling, learning quantum states, Monte Carlo
  (fqmci-full-quadratic-advantage), linear algebra
  (hhl-runtime-kappa2-logn-over-eps), reinforcement learning
  (jerbi-quadratic-speedup-conditional) and chemistry. Few touch
  card-transaction data.
- **Dequantization.** The exponential speedup of quantum recommendation
  is removed when the data has classical sampling access
  (tang-no-exponential-speedup, HIGH); dequantization needs classical
  access (dequantization-needs-classical-access, HIGH). Fidelity kernels
  can be simulated classically (fidelity-kernels-classically-simulable-limit),
  and real-amplitude encodings give a classical kernel
  (real-amplitude-encoding-pqc-is-classical-kernel). Some trainable
  circuits are proved not dequantizable
  (gilfuster-trainable-nondequantizable-exist, HIGH).
- **Resources that matter.** Entanglement and superposition are not
  enough: Clifford circuits have both and simulate classically
  (chowdhury-gottesman-knill-restated-stabilizer-simulable, HIGH);
  non-stabilizer resources are needed
  (howard-stabilizer-subtheory-efficiently-simulable, HIGH).
  Contextuality is necessary for magic-state-distillation speedup
  (howard-contextuality-necessary-for-msd-speedup). Entanglement is
  also one of four named sources of exponential concentration
  (qelm-exponential-concentration, HIGH).
- **Qubit counts the store states** (all LOW unless noted): a QNN wider
  than 60 qubits for an experimental advantage (jaderberg-scale-limit,
  HIGH); 50 to 100 qubits for strong kernel separation on fraud,
  stated by the authors of a 20-qubit study (hardware-scope-limits);
  tens to hundreds of millions of physical qubits for chemistry
  (mohseni-resource-estimate-chemistry) and for a QAOA race
  (omanakuttan-crossover-table). Two RSA-2048 estimates conflict
  (rsa-2048-qubit-estimate against nisq-factoring-resources-beyond-nisq,
  whose exponent is printed flat). No other use case has a stated count.

### Kernels

- **Settled.** Fidelity-kernel entries concentrate exponentially in the
  qubit count, so the shots needed grow exponentially
  (qfk-vanishing-similarity-definition, dqc1-kernel-exponential-measurements,
  both HIGH). A fidelity kernel's information gain is O(4^n log T)
  (qkbandit-info-gain-exponential, HIGH). Estimating every kernel entry
  to precision epsilon takes shots scaling as "msvM/eps^2" as stored
  (shofar-precise-kernel-scaling, HIGH; the stored quote is garbled, so
  the exact form needs the paper's Theorem 5).
- **Measured.** A simulated 15% average-precision gain on fraud at 20
  qubits, on 500 subsampled transactions with 25 frauds
  (quantum-kernel-ap-separation, dataset-and-simulation-setup); a
  replication found it "discernible but minimally significant"
  (ocsvm-precision-not-clear-advantage). On nine UCI tabular sets,
  classical kernels beat the best quantum kernel on 8, none significant
  in five folds, but 6 of 7 significant over 16 paired seeds
  (qksvm-classical-kernels-better-on-uci-tabular). Bandwidth is the most
  important hyperparameter (bandwidth-most-important-hyperparameter),
  and tuning it can make the kernel classically simulable
  (cited-slattery-no-advantage).
- **Missing.** A feature-count threshold for concentration, and any
  kernel result against a tuned boosted tree.

### Trainability

- **Settled.** Random 2-design circuits and global costs have
  exponentially small gradients (mcclean-rpqc-gradient-variance-exp-small),
  and the authors cast doubt that the choice of optimizer, gradient-free
  included, avoids them (arrasmith-scope). Local
  costs at logarithmic depth (cerezo-local-cost-polynomial-gradient-log-depth),
  S_n-equivariant circuits (sn-equivariant-qnn-guarantees) and symmetric
  ansatze (wang-symmetric-ansatz-proved) avoid them, all HIGH. Absence of
  a barren plateau does not guarantee trainability
  (dpqc-trainability-open, HIGH).
- **Pattern, not theorem.** Barren-plateau mitigations with polynomial
  bounds "consistently appear" classically simulable
  (meyer-barren-plateau-definition, HIGH as a statement of the
  pattern); the stronger claims are LOW and cited.

### Noise and mitigation

- **Settled.** Noise can induce barren plateaus, and most QML work does
  not model noise (cerezo-noise-undermines-qml-claims, HIGH). A fully
  depolarized kernel predicts nothing (noisy-kernel-worst-hypothesis,
  HIGH). Post-selection discards shots (post-selection-limit, HIGH), and
  mitigated kernel estimates are biased (shofar-biased-noise-separate,
  HIGH).
- **Measured.** A simulated noisy fraud QSVM fell from accuracy 0.78 to
  0.55 (fraud-qsvm-noisy-simulator-accuracy-drop-no-hardware); a
  hardware QSVR kernel scored AUC 0.50 (qsvr-hardware-auc-050).
  Probabilistic error cancellation has a variance overhead of order
  10^128 at 127 qubits (gacon-pec-sampling-overhead, order of magnitude
  only); zero-noise extrapolation is cheap but biased
  (gacon-zne-biased-estimator).

### Generalization and sample complexity

- **Settled.** Generalization error scales as about sqrt(T log T / N)
  for T trainable gates and N samples
  (caro-generalization-error-sqrt-t-over-n, stored HIGH; the review
  proposes LOW, one of the 28 changes waiting for the team lead). Quantum PAC sample
  complexity equals classical up to constants
  (ciliberto-quantum-pac-sample-complexity-equivalent, HIGH).
- **Missing.** Any measured law of quantum training time against N. The
  one wall-clock figure is a simulator one: more than 100 hours for QSVC
  on 682 instances at 8 qubits and 15 features (scaling-limits).

### Encoding and readout

- **Settled.** Angle encoding takes one qubit per feature at constant
  depth; amplitude encoding takes log2 N qubits
  (ae-vqc-qubit-count-amplitude-encoding, HIGH) but state-preparation
  depth linear in the nonzero amplitudes or worse
  (appendix-b2-amplitude-state-prep-depth-limit, HIGH). QRAM needs
  O(Nd) physical resources (ciliberto-qram-caveats, HIGH) and has not
  been built. Papers at tens or hundreds of features compress first with
  PCA or a classical layer (pca-compression-and-angle-encoding, HIGH).
- **Loading cost grows with the data.** For quantum oracle sketching,
  runtime is dominated by O~(N) data loading, unavoidable only when each
  gate has a constant number of degrees of freedom
  (zhao-runtime-dominated-by-data-loading, HIGH; one method, under that
  condition). A kernel Gram matrix on M points takes Theta(M^2) state
  preparations (faryad-quantum-kernel-gram-theta-m2-preparations, LOW,
  no proof given).

### Gates and small reusable circuits

- **Settled.** A universal set can be single-qubit gates plus one
  entangling gate: textbook background, cited and used in a proof, not
  proved there (muta-property2-universality, HIGH for the paper's own
  universality property). Gates outside a
  device's native set are decomposed at transpile time, at a cost in
  depth and noise (midcircuit-multiqubit-gate-overhead, HIGH).
  Fault-tolerant cost models count T gates
  (omanakuttan-t-count-decomposition, HIGH).
- **Near-term useful circuits.** The swap test and the Hadamard test
  compute overlaps with one readout qubit (swap-test-purpose-and-outcome,
  pi-qml-overlap-measurement, HIGH). Phase estimation, HHL and QSVT need
  fault tolerance (hhl-not-nisq, cao18-qpe-too-deep-for-nisq, LOW); HHL
  needs sparse, well-conditioned matrices and efficient loading
  (biamonte-hhl-speedup-caveats, HIGH).
- **Missing.** A standard text on gates (Nielsen and Chuang) and current
  vendor native-gate documentation.

### Hybrid practice

- **Settled.** Use shallow circuits and local costs, re-upload data, and
  keep trainable gates few relative to training points
  (quyen-naive-tqfm-cancels, caro-generalization-error-sqrt-t-over-n).
  Parameter shift is exact (qcl-gradient-by-pi-over-2-shift, HIGH) but
  costs circuits linear in the parameters. Identity-style initialization
  helps only for local costs (ippdt-limits, HIGH).
- **Measured.** Optimizer rankings conflict: COBYLA, Adam and SPSA-type
  methods each win under different conditions. No shot-budget rule.

### QUBO, annealing and Dirac solvers

- **One direct comparison.** Phase 2's own: greedy equalled the best
  objective any method found on the learner-selection instances, and
  the formulation, not the solver, was the limit
  (f153-learner-selection-formulation-fails-its-falsifier, HIGH as a
  measurement of record).
- **Elsewhere, classical solvers win or tie.** Branch-and-cut matched
  every reference energy on 176 instances (hellstern-conclusions-main);
  LR-QAOA never improved on the better of SA and a tensor-network anneal
  (hellstern-result-lrqaoa-no-improvement); independent tabu and SA beat
  Dirac-3 on its published Max-k-Cut benchmarks
  (classical-solvers-match-dirac3-published-benchmarks). All LOW.
- **The comparators were not tuned.** Hellstern's SA ran at fixed
  restarts and sweeps (hellstern-setup-solver-configs, HIGH); Gerlach
  left penalty tuning to future work (penalty-tuning-left-to-future,
  HIGH).
- **Dirac facts.** Dirac-3's variable ceiling falls with interaction
  order (dirac3-variable-ceiling-falls-with-interaction-order); its
  analog resolution is about 200:1 (dirac3-analog-resolution-about-200-to-1,
  HIGH); it returns sub-optimal answers at a measured rate
  (dirac3-returns-suboptimal-answers-at-a-measurable-rate, HIGH, an
  admission against interest) and its optics could be classically
  simulated (dirac3-optics-could-be-classically-simulated, HIGH). QCi's
  Dirac-3S headline "optimal on every planted instance" is contradicted
  by its own table (dirac3s-all-optimal-headline-contradicted-by-own-table,
  HIGH). The favorable Dirac-3 papers are QCi-authored
  (favorable-dirac3-papers-are-qci-authored, HIGH). No independent
  measurement of Dirac-3S exists in the store.
- **Missing.** Any penalty weight for a cardinality constraint, and any
  tuned classical feature-selection head-to-head at realistic size.

### Tensor networks and quantum-inspired methods

- **Settled.** Any variational QML model can be written as an MPS model
  (vqml-is-mps-theorem, HIGH); finite-Fourier quantum kernels map to a
  spectral tensor network (fourier-expansion-is-etk, HIGH). A
  dequantized k-means++ exists (shah-dequantized-qi-kmeanspp, HIGH).
- **Missing.** Any tabular or fraud tensor-network result against a
  tuned boosting bar.

### Fraud, imbalance and benchmarking

- **The best-documented confound is an unstable or untuned baseline.**
  Phase 2's default HGB scored AUPRC 0.375 (SD 0.170); setting L2 = 1.0
  gave 0.804 (f151-hgb-default-l2-zero-unstable-at-extreme-imbalance).
- **Quantum fraud results ran on tiny or rebalanced sets**: 500 samples
  with 25 frauds (dataset-and-simulation-setup), 4 features and 8
  training points (acae-fraud-proof-of-concept-scale), a test set
  undersampled to about 43% fraud
  (fraudtransformer-evaluation-set-undersampled). Preprocessing before
  the split inflates results (kabane-presplit-inflation).
- **Phase 2's tuned comparison**: tuned boosting leads on ULB and the
  CVQBoost proxy is fifth of seven
  (f166-ulb-tuned-boosting-leads-proxy-fifth), with the proxy given its
  own top 17 features while the classical lanes used all 30 columns.
  The order among the four boosting libraries and the proxy is not
  established at Bonferroni 0.05/6; two adjacent pairs are: the proxy
  above the linear SVM, and the SVM above logistic regression. At a 0.5%
  alert budget, recall spreads less than AUPRC (0.8305 to 0.8589 against
  0.7270 to 0.8329); the recall order is untested
  (f166-ulb-recall-at-alert-budget-spread-narrower-than-auprc).
- **Drift.** The one temporal measurement is Phase 2's rolling-origin
  IEEE-CIS run: LightGBM led every month, and logistic regression fell
  from 0.337 to 0.122 on month 5
  (f152-ieee-cis-trees-beat-logistic-lightgbm-leads). Most published
  fraud scores use random splits (han-ieee-cis-best-test-scores-random-split).

### Classical model families, and where a hybrid fits

- **Gradient boosting** is the strongest family on ULB and IEEE-CIS. The
  hybrid in the store is QBoost-style weak-learner selection, with
  negative measured results (kimmeyh-h1b-primary-null-9-of-10-seeds).
- **Bagging**: a quantum random forest is defined with a query-complexity
  theorem (qrf-model-definition, qrf-theorem-1, HIGH); measured results
  are small and LOW. Nothing on balanced random forest or extra trees.
- **Linear and probabilistic**: QSVM and QUBO-SVM results, all LOW. Naive
  Bayes is the exact label rule of the CardSim simulator
  (allen-cardsim-label-is-naive-bayes-rank-cutoff, HIGH), so it tests
  only that simulator.
- **Anomaly detection** is, by inference, the best fit for the kernel
  route (one-class kernel setups exist, for example
  bhowmik-kyriienko-setup), but the store holds no tuned classical
  isolation forest, LOF or one-class SVM number on fraud. Noise is the
  main bottleneck of variational anomaly detection
  (vqad-noise-bottleneck, HIGH).
- **Neural networks**: small circuits replace MLP layers with fewer
  parameters in LOW studies; no tabular fraud result.
- **Others worth trying**, from the store: tabular foundation models
  (qu-tabicl-benchmark, LOW, one study, against TabPFNv2 and CatBoost
  on TALENT),
  cost-sensitive learning with a derived threshold
  (hoppner-instance-threshold, HIGH), stacking, graph models, and QUBO
  feature selection (orquin-qfs-competitive, LOW).

### Generative AI

- **Settled.** Learning shallow generative QNNs is quantumly easy and
  classically hard under a stated conjecture, for exact sampling
  (classically-hard-quantumly-easy-generative-models, HIGH). Useful
  generative advantage and its crossover are open
  (gqa-open-hardness-crossover, HIGH).
- **Qubit counts stated**: 68 physical qubits (an effective 816) in one
  hardware run (idqnn-hardware-quantum-beats-classical-models, LOW, with
  a classical-simulation caveat); 20 qubits for Born machines
  (pqa-setup-20-variables). No count for training or running an LLM at
  useful scale.

## What it means for the competition, per question

Each answer states what the store supports and how certain it is.

**Phase 2's experiments**

1. **Exp 1, the confound.** The store names the confounds: untuned or
   unstable baselines, tiny or rebalanced data, unequal feature access,
   preprocessing before the split, and simulation in place of
   hardware. Implication: no quantum lane should be compared
   except against tuned, stable classical lanes on the same rows, the
   same features and the same split, over many seeds with paired tests.
   Certainty: HIGH for Phase 2's own entries, LOW for the literature.
2. **Exp 2, temporal validity.** The store holds only Phase 2's own
   rolling-origin run. Implication: keep thresholds and alert budgets
   fixed from earlier folds (Inference, from one LOW finance result that
   a tuned threshold did not transfer). Certainty: thin; a gap (below).
3. **Exp 3, feature selection on Dirac-3S.** No HIGH or independent
   result shows a quantum or quantum-inspired solver beating a tuned
   classical comparator. Four LOW single studies report quantum feature
   selection competitive or better against untuned comparators. The
   benchmark solvers ran at fixed settings, not tuned per instance, with
   penalty weights untuned. Phase 2's falsifier puts the limit on the
   formulation, and its F176 (IEEE-CIS, not yet in the store) found
   classical gains below greedy of under 2e-05 against room near 0.08 to
   0.097. Implication: no device run on this formulation until a
   classical rounding test shows Dirac-3S could resolve gains of that
   size; run the same solver test on the f153 instances; and at
   production scale this is the quantum role that fits, because the
   QUBO is built from statistics accumulated over the rows, so its size
   does not grow with them. Certainty: HIGH for the setups, LOW for the
   comparisons.
4. **Exp 4, replication under Loke's protocol.** Done in Phase 2; the
   store records the protocol's effect on HGB
   (f111-protocol-moves-hgb-not-measurably-the-knn-lane). No new
   implication.
5. **Exp 5, segment transfer.** On hold in Phase 2. The store adds
   nothing.
6. **Exp 6, training time against sample count.** The store bounds
   error, not time. One method's loading is linear in rows under a
   stated condition (HIGH), and one paper claims without proof that a
   kernel Gram matrix is quadratic in rows (LOW). Implication: Phase 2's
   classical slope of about 1.4
   (f110-cvqboost-pool-build-grows-faster-than-rows) is not a quantum
   number; a kernel lane's feasible row count is set by device seconds
   for M squared circuits times shots. At 100 million rows a full Gram
   matrix is about 10^16 entries, so a kernel lane needs landmarks (the
   Nystrom form cuts circuit runs from order N squared to order N times
   M squared, coelho-linear-executions, LOW). Certainty: HIGH for the
   scoped loading bound, LOW for the Gram count, nothing for a measured
   quantum law.

**The team lead's questions**

7. **How gates work, and which sets serve which purpose.** Universal
   sets (single-qubit plus one entangling gate) run anything; Clifford
   gates alone simulate classically; fault-tolerant work counts T gates;
   devices transpile to their native set at a cost. Implication: write
   circuits in rotations plus CNOT or CZ and judge cost in native
   two-qubit gates after transpiling. Certainty: HIGH; the store lacks a
   standard text (gap).
8. **Useful small circuits (math, storing, reading in, getting out).**
   Near term: the swap and Hadamard tests for overlaps, angle loading
   after PCA, and expectation-value readout. Phase estimation, HHL and
   QSVT wait for fault tolerance. Certainty: HIGH for definitions, LOW
   for costs.
9. **Anything useful that is not hybrid.** Nothing demonstrated on
   hardware for fraud-like data. Fault-tolerant algorithms are future;
   quantum-data tasks do not apply; quantum-inspired classical methods
   are useful and proven. Certainty: rests on HIGH "no end-to-end
   advantage" statements and LOW reviews.
10. **Best practices for hybrid algorithms.** Shallow, local-cost,
    symmetry-aware circuits; few trainable gates per training point;
    parameter shift or SPSA-type gradients by budget; identity-style
    initialization for local costs; a tuned classical baseline as the
    test. Certainty: HIGH for the trainability points, LOW for optimizer
    and shot choices.
11. **Using entanglement, superposition and interference.** They are
    necessary but not sufficient; non-stabilizer resources are needed
    for advantage, and entanglement is also a named source of
    exponential concentration. Use cases that exploit them are search, sampling,
    Monte Carlo and quantum-data learning, not tabular classification.
    Certainty: HIGH for the limits.
12. **Where advantage shows, how close, how many qubits, and whether
    only search and optimization.** Proved advantages are on constructed
    or cryptographic problems; the nearest "needs only better hardware"
    cases are Monte Carlo (proved quadratic, no qubit count stored) and
    chemistry (tens to hundreds of millions of physical qubits, LOW);
    no exponential advantage is known for classical data. Use cases go
    beyond search and optimization. The only fraud-relevant qubit count
    is 50 to 100 for kernel separation, a LOW author statement.
    Certainty: HIGH for the proofs, LOW for every count.
13. **How hybrid ML fits each classical family.** Boosting is the bar,
    and the QBoost-style hybrid is negative so far; bagging, linear and
    neural hybrids have only small LOW results; anomaly detection is the
    best fit for a quantum kernel, but its classical side is unmeasured
    in the store. QUBO feature selection keeps the final model classical
    and fits the qubit budget best (Inference). Certainty: LOW.
14. **GenAI training or inference, and qubits.** One proved hardness
    result for generative sampling; no qubit count for LLM-scale work.
    Implication: GenAI is not a lane for this challenge. Certainty: HIGH
    for the result, nothing for a count.

## At production scale

ULB's 284,807 rows train in seconds classically; production fraud data
accumulates 20 to 100 million rows a day. The comparison at that scale
is about how each side grows, and it moves toward classical. Points
marked (outside the store) are the coordinator's knowledge, not stored
evidence; F128 carries them as reading targets.

- **Classical** gradient boosting with histogram splits grows about
  linearly in rows times features per tree, runs distributed, and scores
  a transaction in about a millisecond (outside the store).
- **Quantum, reading every row**: loading is at least linear in rows
  (HIGH for one method, under its condition), each row costs several
  logical operations per feature at a clock of kHz to MHz, and training
  repeats that for every shot and every pass (Inference: 100 million
  rows of 30 features is about 3 billion loading operations, about an
  hour per pass and shot at an optimistic 1 MHz).
- **QRAM does not remove the cost**: it needs physical resources of
  order rows times features and may not give a genuine advantage once
  all are counted (ciliberto-qram-caveats, HIGH); most QML speed-ups
  assume a preloaded one (dunjko-qml-speedups-need-qram-assumptions,
  LOW); one design did not support incremental data
  (qram-fixed-ansatz-no-incremental, HIGH, for that study).
- **Scoring** a transaction with a circuit and its shots cannot meet a
  millisecond budget at that volume.

**Methods that process rows a few at a time** (memory independent of
rows; throughput still per row):

1. Variational classifiers trained by mini-batch gradient descent:
   about twice the parameter count in circuit runs per row per step,
   times shots; F118's trainability limits apply.
2. A fixed quantum feature map feeding a classical streaming learner
   (quantum extreme learning machines, reservoirs, projected-kernel
   features): only the classical readout trains. The nonlinearity comes
   only from the encoding (innocenti-qelm-nonlinearity-from-encoding,
   HIGH); highly random reservoirs make the models unscalable
   (qelm-random-reservoir-unscalable, HIGH); local dynamics matched
   Haar-random ones and may be classically simulable (LOW); finite shots
   bias the prediction (shot-noise-error-scaling, LOW).
3. Quantum kernels on M fixed landmark rows (Nystrom): M circuits per
   new row; memory M rows and an M by M matrix
   (coelho-nystrom-definition, HIGH; coelho-linear-executions, LOW).
4. QUBOs on accumulated statistics (feature-selection QUBO, QBoost): a
   classical pass over the rows updates a d by d (or K by K) matrix, and
   only that matrix reaches the solver. **This is the quantum role that
   fits production scale**, and it is Phase 2's Exp 3 lane.

Methods that need every row loaded into quantum memory (HHL-based
classifiers, quantum PCA, the QRAM-based quantum SVM, full Gram-matrix
kernels) do not fit, and their low-rank cases are dequantized.

## On a fault-tolerant machine (10,000 logical qubits)

A thought experiment the team lead asked on 2026-10-31. The store holds
no fault-tolerant resource estimates (F128), so the figures here are
outside the store and marked so.

- **What stays**: tuned classical models remain the bar for tabular
  fraud; loading stays at least linear in rows; dequantization, kernel
  concentration (worse with more qubits), barren plateaus from
  expressive or global-cost circuits, and the generalization bound all
  hold on perfect hardware. Only noise-induced limits go.
- **What changes**: cost is counted in T gates and T-depth; phase and
  amplitude estimation, Grover and QSVT become usable; non-hybrid use
  becomes real (factoring, chemistry and materials, Monte Carlo for risk
  and pricing). Published derivative-pricing estimates put advantage
  near 7,500 logical qubits with very large T-depth (outside the store),
  so the logical clock, not the qubit count, would decide it.
  Quadratic speed-ups likely lose to classical hardware on early
  fault-tolerant machines (Babbush et al., 2021; outside the store).
- **For the fraud model**: the answer stays classical. The quantum case
  moves to adjacent tasks: Monte Carlo risk (cost independent of rows)
  and the cryptography that protects the bank.

## Experiments, ranked

Ranked by how much each decides for Phase 2 before the 14 Nov 2026
notification date, against its cost. Costs come from stored figures
where one exists; others are rough and marked so.

1. **Tuned classical solvers and a penalty sweep on the f153
   instances.** Hypothesis: greedy plus local swap, SA with a tuned
   schedule, and a sweep of the cardinality penalty reach the same floor
   as greedy, so the formulation is the limit. Ids:
   f153-learner-selection-formulation-fails-its-falsifier,
   hellstern-setup-solver-configs, penalty-tuning-left-to-future. Cost:
   CPU minutes, no device time. Changes the approach: a gap of at least
   0.01 below greedy means the formulation is not the limit and a device
   run is worth its cost; no gap means stop sending this formulation to
   a device. Extends Exp 3. **Half answered**: Phase 2's F176 ran the
   solver part on the IEEE-CIS instances (gains under 2e-05; no
   penalty sweep). The f153 instances and the penalty sweep remain.
1a. **Rounding test for F176's gains.** Hypothesis: rounding the QUBO's
   coefficients to Dirac-3S's about 200:1 resolution changes the
   objective by more than 2e-05, so the device cannot resolve the gains
   a classical solver found. Ids: dirac3-analog-resolution-about-200-to-1
   and F176's result file. Cost: CPU minutes. Changes the approach: if
   the rounding error exceeds the gains, no device run on this
   formulation can show anything.
2. **Equal-feature ablation.** Hypothesis: giving the classical lanes the
   proxy's 17 features closes the proxy's edge over linear models, so
   feature choice, not the quantum step, explains it. Ids:
   f166-ulb-tuned-boosting-leads-proxy-fifth,
   kimmeyh-h1b-primary-null-9-of-10-seeds. Cost: CPU minutes. Changes the
   approach: a match leaves QUBO feature selection as the only quantum
   role to test. Extends Exp 1.
3. **Classical surrogate for any quantum kernel lane.** Hypothesis: a
   random-Fourier-feature, MPS or spectral tensor-network surrogate
   reproduces the kernel's AUPRC on fraud features. Ids:
   fidelity-kernels-classically-simulable-limit, vqml-is-mps-theorem,
   fourier-expansion-is-etk, cited-slattery-no-advantage. Cost: CPU
   minutes. Changes the approach: a match means the lane has no gap to
   exploit; a persistent gap with a small bond dimension points to a map
   worth a hardware run. Fills the gate-based arm (F6).
4. **Kernel concentration against qubit count and bandwidth on fraud
   features.** Hypothesis: off-diagonal variance falls exponentially for
   the fidelity kernel and stays flat for the projected kernel, and
   bandwidth moves one toward the other. Ids:
   qfk-vanishing-similarity-definition,
   bandwidth-most-important-hyperparameter, hardware-scope-limits. Cost:
   simulator minutes at 2 to 14 qubits (rough). Changes the approach:
   collapse before 20 qubits caps the qubit count or forces a projected
   kernel.
5. **Dirac-3S resolution test at 200:1.** Hypothesis: rescaling the
   Hamiltonian so distinct coefficients differ by at least max/200 does
   not change solution quality, so resolution is not the limit. Ids:
   dirac3-analog-resolution-about-200-to-1,
   f153-two-resolution-checks-disagree-in-kind,
   dirac3s-time-per-sample-schedule-2-by-size. Cost: classical rounding
   first; then about 75 s of device time per 100-sample job at 91
   variables and about 260 s at 560 (Inference from the stored
   per-sample times). Changes the approach: a quality change locates
   the device shortfall in precision.
6. **Tiered kernel test against Phase 2's tuned baselines on ULB.**
   Hypothesis: no quantum kernel on PCA features beats tuned HGB across
   the ten seeds with a paired test. Ids: quantum-kernel-ap-separation,
   qksvm-classical-kernels-better-on-uci-tabular,
   f166-ulb-tuning-chose-unweighted-linear-and-l2-hgb. Cost: simulator
   minutes to hours on a 20,000-row stratified subsample (rough).
   Changes the approach: no win drops kernels to a documented negative.
7. **Sample-count sweep with a tuned classical control.** Hypothesis: a
   small quantum model's generalization gap shrinks with N as the bound
   says but never beats the tuned control. Ids:
   caro-generalization-error-sqrt-t-over-n, scaling-limits. Cost:
   simulator hours (the one stored timing is over 100 hours for 682
   instances at 8 qubits). Extends Exp 6.
8. **Per-sample success rate on Dirac-3S.** Hypothesis: one sample is
   optimal far less often than best-of-N tables show. Ids:
   dirac3s-best-of-batch-hides-low-per-sample-success,
   dirac3-returns-suboptimal-answers-at-a-measurable-rate. Cost: device
   seconds at the same per-job figures as experiment 5.

### Experiments that would raise the certainty of stored LOW claims

An experiment never raises a published paper's assertion from LOW: the
paper's result stays what the paper showed. What a run adds is a new
measured assertion from Phase 2's own data, entered HIGH as a
measurement of record and linked `supports` or `contradicts` to the LOW
claim (ADR-0004 A8, as F65 did for Dirac-3). These are the LOW claims a
Phase 2 run of CPU or simulator minutes would confirm or contradict.
None can run in this repository, which holds no fraud data and has no
route of its own for an experiment's provenance; each goes to Phase 2
in the prompt below.

- The four LOW quantum feature-selection positives
  (orquin-qfs-competitive, varqfs-vs-classical, qaoa-fs-comparable,
  hellstern-dataset-dependent): rerun their comparison on ULB and
  IEEE-CIS against a tuned comparator with the same feature budget
  (experiments 1 and 2).
- Kernel concentration and bandwidth (quantum-kernel-ap-separation,
  hardware-scope-limits, bandwidth-most-important-hyperparameter):
  experiment 4, a 2 to 14 qubit sweep on fraud features.
- Classical simulability of quantum extreme learning machines
  (qelm-local-dynamics-match-haar-classically-simulable): a fixed
  local reservoir against a Haar-random one on PCA-reduced ULB, with a
  classical random-feature surrogate (experiment 3).
- The Nystrom circuit count (coelho-linear-executions): count circuit
  runs for a landmark kernel at three row counts; a direct measurement.
- Shot-noise bias in the readout (shot-noise-error-scaling): vary shots
  per sample on one simulated reservoir.

## Gaps, carded

The store cannot answer these; F128 (`docs/ALL_SPRINTS_MASTER_PLAN.md`)
holds them as reading targets, and the Phase 2 prompt below sends the
experiments:

- Qubit counts per use case: the primary resource-estimate papers.
- Penalty weights for a cardinality constraint and a tuned feature
  selection comparison: Ferrari Dacrema et al., cited in
  dacrema-comparison-cited but not read.
- Quantum data-loading cost against rows: the Faryad paper in full.
- Drift and delayed labels in card fraud: no source in the store.
- Gate theory and native gate sets: a standard text and vendor
  documentation.
- Tensor-network classifiers on tabular data: Stoudenmire and Schwab.
- Tuned classical anomaly-detection numbers on fraud.
- Three stored assertions that hold two claims of different grade
  (split candidates from F117's review).
- Production-scale timing, classical against quantum, with loading,
  shots and per-transaction scoring at 20 to 100 million rows a day.
- QRAM feasibility and cost at that scale.
- Fault-tolerant resource estimates for amplitude-estimation risk
  models and for the quadratic-speed-up break-even (Babbush et al.,
  2021; Chakrabarti et al. on derivative pricing).

## Citations checked

On 2026-10-31, every id this memo cites (124) was found in the live
store. These ten were read against their stored value and grade; three
memo statements were corrected by the read, as noted.

| Id | Stored grade | What the memo says, and the check |
|---|---|---|
| cerezo-no-known-exponential-advantage-classical-data | high | No exponential advantage known for classical data. Matches |
| jaderberg-scale-limit | high | QNN wider than 60 qubits. Matches |
| hardware-scope-limits | low | 50 to 100 qubits for strong separation, an author statement. Matches |
| quantum-kernel-ap-separation | low | 15% AP separation at 20 qubits, simulated. Matches |
| qksvm-classical-kernels-better-on-uci-tabular | low | Classical better on 8 of 9. Corrected: significance added |
| f151-hgb-default-l2-zero-unstable-at-extreme-imbalance | high | AUPRC 0.375 (SD 0.170) against 0.804. Matches |
| f153-learner-selection-formulation-fails-its-falsifier | high | Greedy equalled the best; formulation fails its falsifier. Matches |
| dirac3-analog-resolution-about-200-to-1 | high | Resolution about 200:1. Matches |
| caro-generalization-error-sqrt-t-over-n | low | sqrt(T log T / N). Set LOW at the team lead's decision, 2026-10-31: the proof covers 2-qubit gates only |
| f166-ulb-tuned-boosting-leads-proxy-fifth | high | Proxy fifth of seven, 17 against 30 features. Corrected: order not established |

## The Phase 2 prompt (draft, for the team lead to paste)

Writes never cross between the repositories (F79), so this goes to a
Phase 2 session as a pasted prompt. It carries each claim inline,
because a citation into this private store may not resolve there
(ADR-0005).

```
From EvidenceBasedDB's F118 memo (store snapshot of 2026-10-31; Phase 2
read at d14fdb7, your Sprint 30 validation draft). For each item below:
if one of your cards already covers it, add the source line to that
card; if none does, card it in docs/ALL_SPRINTS_MASTER_PLAN.md with the
source line kept. Propose each one's place: before or after the 14 Nov
2026 notification date. Do not run anything on a device without the
team lead's approval.

What the store found:
- In the themes read, no stored result shows a quantum model beating a
  tuned classical model on tabular, imbalanced data. Positive fraud
  results are simulations on small or rebalanced subsets against
  untuned comparators (LOW, published studies).
- No HIGH or independent result shows a quantum or quantum-inspired
  solver beating a tuned classical comparator on cardinality-constrained
  selection. Four single studies report quantum feature selection
  competitive or better, against untuned comparators (LOW). Your F153
  falsifier and your F176 (gains below greedy under 2e-05 against room
  near 0.08 to 0.097; SCIP never beat greedy) put the limit on the
  formulation.
- At production scale (20 to 100 million rows a day) the comparison is
  about growth: classical training grows about linearly in rows; a
  quantum learner that reads every row pays at least linear loading at
  a far slower clock, times shots; QRAM needs resources of order rows
  times features (HIGH, a review); per-transaction quantum scoring
  cannot meet a millisecond budget. The quantum role that fits is a
  QUBO built from statistics accumulated over the rows (feature or
  weak-learner selection), whose size does not grow with them.
- On a fault-tolerant machine, tuned classical models stay the bar for
  tabular fraud: loading, dequantization, kernel concentration and the
  generalization bound do not depend on noise. The quantum case moves to
  Monte Carlo risk and cryptography.

Before 14 Nov 2026 (CPU or simulator minutes; zero metered seconds):
1. Rounding test for F176's gains: round each instance's coefficients
   to Dirac-3S's about 200:1 resolution and measure the objective
   change. If it exceeds 2e-05, no device run on this formulation can
   show anything; hold F161 and any Exp 3 device run until this is done.
2. F176's solver test and a cardinality-penalty sweep on the F153
   instances (F176 ran IEEE-CIS only, with no penalty sweep).
3. Equal-feature ablation: give the classical lanes the CVQBoost
   proxy's 17 features on ULB (and on IEEE-CIS once F174 completes). A
   match leaves QUBO feature selection as the only quantum role.
4. A classical surrogate (random Fourier features, MPS or a spectral
   tensor network) for any quantum kernel lane; a match means the lane
   has no gap to exploit.
5. Kernel concentration against qubit count (2 to 14) and bandwidth on
   fraud features, fidelity against projected kernel.
Each result enters EvidenceBasedDB as a measurement of record linked to
the published LOW claims it confirms or contradicts.

After 14 Nov 2026 (plan, then run as the outcome allows):
6. Production-scale framing: measure classical training and scoring
   time at 1, 10 and 100 million rows (synthetic growth of IEEE-CIS is
   acceptable, labeled), and state a quantum lane's loading, shot and
   scoring cost at the same sizes from its circuit. This replaces a
   comparison at ULB's size.
7. Streaming QUBO selection: build the feature- or learner-selection
   QUBO from statistics accumulated in one pass over the rows, and test
   that it matches the in-memory build. This is the Exp 3 design that
   survives production scale.
8. Fault-tolerant resource estimates (logical qubits, T-count,
   wall-clock) for each candidate quantum step at production sizes, and
   for an amplitude-estimation risk model.
9. Tiered kernel test against your tuned ULB baselines, ten seeds,
   paired tests; sample-count sweep with a tuned classical control (Exp
   6); per-sample success rate on Dirac-3S against best-of-N (device
   seconds, on approval).
```
