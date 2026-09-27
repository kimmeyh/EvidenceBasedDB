# Learning from the papers: key learnings as a computed synthesis

Design document, Sprint 5 Task I (backlog item F28, Issue #52). Status:
**proposed**. The pilot in section 6 uses only primitives the store already
has; section 7 lists what the pilot showed is missing, as proposals for
the team lead, not as changes. Amend by dated section once a choice ships
records.

## 1. The question (team lead, 2026-09-19)

"Start to devise a way to learn from the papers -- key learnings about
QML, how QML might be able to improve predictions (tools, techniques,
algorithms...), key learnings about ML, how we might be able to improve ML
predictions (tools, techniques, algorithms...)."

Who reads the output: the team lead and the agents that design the next
experiment. What they must be able to do after reading it: see what the
store's evidence says about a technique, at what certainty, from which
sources, and where the sources disagree -- without anyone having written
that summary by hand.

## 2. What already exists, and what does not

The store already holds the primitives (ADR-0004 section 3, ADR-0005
sections 2b2, 2e, 2f):

- **assertions** with provenance, GRADE-style `certainty` and named
  `certainty_reasons`, `citation_context` (the verbatim sentence) and a
  context;
- **`supports` and `contradicts`** between assertions;
- **`paper_yields`**: which paper each assertion came from;
- **contexts** as partitions (`qml`, `ml`, `method`, ...).

Before Sprint 5 it held 13 assertions, one worked disagreement
(`fourier-wall-public-tabular-refuses-qml` contradicts the two CVQBoost
results, and `real-amplitude-encoding-pqc-is-classical-kernel` supports
it), and no way to ask "what do we believe about X". What does not exist:
(a) extraction at scale, and (b) a synthesis layer.

## 3. What a "key learning" is: an assertion, not a new class

**Decision proposed**: a key learning is an ordinary assertion whose value
is a GENERALIZATION ("On public tabular benchmarks, quantum kernel and
variational classifiers have not shown a statistically significant
accuracy gain over tuned classical baselines"), and whose evidence is the
set of source assertions linked to it by `supports` or `contradicts`.

- It is recognized by its `provenance`, which begins **"synthesis of"**
  and names no paper. (The first attempt recognized it by computation
  alone -- "an assertion no paper yields that something supports or
  contradicts" -- and the pilot's first run disproved it: section 7,
  finding 1.)
- Its `certainty` follows ADR-0005 section 2e from its evidence: it starts
  at the certainty of its strongest supporting assertion, moves DOWN for a
  named reason (inconsistency: any `contradicts` edge from an assertion at
  equal or higher certainty; indirectness: evidence from a narrower setting
  than the learning claims; imprecision), and never moves UP past its
  strongest evidence. The reasons are written, as for any assertion.
- ADR-0004 section 3's trigger for a new class ("a record whose fields
  diverge") does not fire: a learning has exactly an assertion's fields.
  That is the evidence the pilot was run to get (section 6).

**Why not a new class**: a class is a schema decision (Class 1) and it
would duplicate the assertion's fields. **Why not a stored summary**:
CLAUDE.md -- determinate facts are computed, never stored. The learning's
VALUE is a claim (someone must write it and be accountable for it); the
EVIDENCE TABLE under it (which sources, which certainties, which
disagree) is determinate and is computed every time.

## 4. Synthesis is a query

`scripts/learnings.py` (view-style, read-only) computes, for every
learning or for one:

- the learning, its certainty and reasons;
- every supporting and contradicting assertion, each with its certainty,
  its source paper, the paper's tier and `checked_against_source`, and the
  verbatim `citation_context`;
- the contexts the evidence spans (a learning about `qml` supported only by
  `ml` evidence is visibly indirect);
- a one-line balance: n supporting (by certainty level), n contradicting.

Nothing it prints is stored. Run it after any extraction and the answer
reflects the store as it is.

## 5. Who extracts, who adjudicates, which papers

- **Extraction** (`screened` -> `read` with yields): a read-only agent
  gathers verbatim quotes with page numbers; the lead model checks every
  quote used against the page and writes the assertion and its certainty
  reasons (the Sprint 4 Task H protocol). Sprint 3's finding stands:
  protocol depth, not model tier, produced the findings (F18,
  `.claude/model_assignment_heuristics.json`).
- **Adjudication** of a LEARNING (its value and certainty) is the team
  lead's: that is a judgment the store's design says only the team lead
  can make (ADR-0005 section 2c, "your review time is still scarce").
  Source assertions keep the Sprint 4 precedent (lead model, recorded in
  `checked_against_source`).
- **Triage** of what to extract next: by question, not by paper. A
  learning under construction names the evidence it lacks; the papers
  whose disposition or abstract bears on that gap are read next. At
  roughly 1,300 papers and 1.08 team-lead minutes per confirm-mode record
  (F11), reading everything to `read` is not the plan; reading what a
  question needs is.

## 6. Pilot (Sprint 5, Q5 = 2, 2026-09-24)

`scripts/sprint5_task_i_pilot.py` (dry run by default; applied after a
verified backup). Counts are a snapshot as of 2026-09-24.

- **Six papers to `read`**, all loaded at `seen` hours earlier by Task C:
  Kakavand et al. (quantum-kernel SVMs vs classical on nine UCI tables),
  Sweke et al. (random Fourier features and dequantization, theory), De
  Lorenzis et al. (quantum extreme learning machines, simulation), Elor
  and Averbuch-Elor (SMOTE and strong learners), Liu (resampling and
  calibration), McDermott et al. (AUROC vs AUPRC, theory plus
  experiments). Two read-only agents extracted verbatim quotes with pages
  (105,183 tokens / 287 s; 133,613 tokens / 505 s); every quote used was
  then checked by exact substring on the page named. One page number was
  wrong (the Spearman result is p.8, not p.9) and was corrected.
- **Seven assertions**, each with GRADE-style certainty and named reasons
  (three HIGH: two theorems and one arithmetic property of the exact
  Wilcoxon test; four LOW: single empirical studies).
- **Three learnings**, wired by `supports` and `contradicts`:
  - `learning-qml-no-reliable-tabular-accuracy-gain` (qml, MODERATE):
    five supporting assertions (one HIGH, one MODERATE, three LOW) from
    six source papers, one LOW contradicting assertion (the Loke CVQBoost
    AUC-PR result), including two assertions the store held before the
    sprint;
  - `learning-ml-resampling-not-the-lever-for-strong-trees` (ml, LOW):
    two independent LOW supports;
  - `learning-method-check-metric-and-power-before-reading-a-difference`
    (method, MODERATE): two HIGH supports.
- `python scripts/learnings.py` prints each learning with its evidence,
  sources and verbatim sentences; nothing it prints is stored.
- **A defect in the pilot itself, caught by a guard**: the promotion went
  `seen` -> `read` and skipped `screened`'s obligation (applicability,
  ADR-0005 Amendment A2). `test_every_screened_or_read_paper_has_real_applicability`,
  aligned to that amendment earlier the same day, failed on the next
  suite run; `scripts/sprint5_task_i_applicability.py` wrote the anchored
  applicability from the pages already read. Lesson for the extraction
  path at scale: promote through `screened`, not past it.

**The answer to the design's central question**: the existing primitives
DO express a key learning with its evidence, its disagreements and a
derived certainty. No new class was needed. Three gaps appeared, below.

**What extraction changed, which is the argument for extraction.** The
bibliography's note on Kakavand et al. reads "0 of 29 comparisons reached
alpha=0.05". The paper says that result is a power floor at five folds,
and that with 16 paired seeds classical kernels are significantly BETTER
on 6 of 7 datasets. A learning written from the note would have said
"no difference"; the one written from the paper says "classical better".
That is F36 item 9 demonstrated: reading notes point at where to look;
they do not become assertions.

## 7. What the pilot showed is missing (proposals for the team lead, not changes)

1. **A learning cannot be recognized by computation alone.** The first
   definition ("an assertion no paper yields that something supports or
   contradicts") caught `hsbc-b1-variable-count-wrong-78`, a project
   assertion sourced from the consumer repository's amendment log. The
   pilot uses a provenance convention ("synthesis of ..."), which is a
   string, and a convention is the weakest kind of guard. **Proposed**: an
   explicit derivation marker on assertions (`derivation: extracted |
   synthesized | project`), as a dated amendment to ADR-0004 section 3,
   decided with F34/F36 so the assertion and paper fields change once.
2. **Some evidence neither supports nor contradicts.** Sweke et al. prove
   that random Fourier features are not a generic dequantizer AND that
   they match some circuits efficiently. Wiring it as `supports` or
   `contradicts` would overstate it, so it is extracted and left unwired.
   **Proposed**: wait. Add a `qualifies` relation only when a second case
   needs it; one case is not a pattern (QUALITY_STANDARDS.md, no
   speculative abstraction).
3. **An assertion can have several sources, and a synthesis must count
   evidence, not sources.** The first query counted
   `cvqboost-vs-xgboost-auc-under-balancing` twice because two papers
   yield it. Fixed in `scripts/learnings.py` and guarded by
   `tests/test_learnings.py` (proven by injection). No schema change is
   needed; recorded because the same double count would recur in any
   hand-built summary, which is why the summary is a query.
4. **Who adjudicates a learning.** Section 5 proposes the team lead. The
   three learnings carry "awaiting team-lead adjudication" in their
   provenance; the pilot does not decide it.
