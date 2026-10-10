# Sprint Planning

Adapted 2026-08-30 from spamfilter-multi's SPRINT_PLANNING.md via hsbc-quantum-fraud-2026. Governs how sprints are scoped, staffed, estimated, and carded. Execution mechanics live in SPRINT_EXECUTION_WORKFLOW.md.

**REWORKED 2026-09-16 (Sprint 1 Task H, F1).** References to the consumer
repository's frozen preregistration, its Dirac-3/Braket/Kaggle tool
dependencies, its `results.json` schema, and its submission deadline have
been replaced with this repository's own equivalents where one exists, and
removed where none does.

## Team roles

| Role | Assigned to |
|---|---|
| Customer Representative / Product Owner / Agile Coach / Scrum Master / Chief Architect / Chief Developer / Chief Test Engineer | Harold Kimmey (the team lead) |
| Assistant Scrum Master, Architecture Development Team, Senior Test Engineers, Development Team | Claude Code (whichever model executes the task; parallel subagents allowed) |
| Lead Developer | Claude Code top tier (Fable 5.1 preferred, Opus 5.5 otherwise) |
| Senior Developers | Claude Code Sonnet 5.5 (subagents) |
| Developers | Claude Code Sonnet 5.5 (subagents) from 2026-10-06 (F59); Haiku 4.5 no longer assigned, ahead of its retirement (not sooner than 2026-10-15) |

**Model versions are verified, not remembered (F39, permanent; first release
Sprint 6 Task A, F40, 2026-10-03).** Each tier's model id, price, context
window, retirement date and the date it was last checked live in
`.claude/model_assignment_heuristics.json`, sourced from Anthropic's models
page. This table must name the same versions; a test fails if it does not,
and if a tier passes its retirement date with no successor.

**Data-driven complement (Sprint 4 Task K, F18, 2026-09-19)**: the table
above is static. `.claude/model_assignment_heuristics.json` records task
patterns with a recommended tier AND a required review protocol,
escalation triggers, a scoring rubric, and a `learning_log` of real
outcomes (first row: Sprint 3's F7-F10, where the protocol rather than
the tier produced the findings; second row: F11's team-lead timing, filled
in when it lands, never estimated). Consult it when assigning a card;
update it at every retrospective (Category 5). Guarded by
`tests/test_model_assignment_heuristics.py`.

## Activities requiring the top tier (Fable/Opus) -- MANDATORY

Sprint planning; retrospectives; backlog refinement; architecture/schema deep dives; ADR authoring; best-practices research; security-sensitive review; any decision touching an ACCEPTED ADR's spine (record classes, contexts, certainty model). Implementation tasks (loaders, scripted runs, doc edits) may be delegated to Sonnet/Haiku subagents. Before starting a top-tier activity, confirm the active model is top tier; escalate if not.

## ADR-first approach

Architectural or schema-shaping changes get an ADR designed and team-lead-approved BEFORE implementation. ADR-0004 and ADR-0005 are this repository's own architecture: the store's schema, contexts, and certainty model. Amendments to an ACCEPTED ADR's spine are ADR-class decisions, recorded as a dated amendment at the bottom of the ADR, never a silent edit.

## Audience-first rule for deliverables (Sprint 4 retro improvement 3)

Before drafting ANY external-facing document (results memo, paper section, sponsor package, submission artifact), state at the top of the task: who reads this, and what must they believe or decide after reading it. That statement shapes structure and emphasis, and it belongs at the START of the task -- a framing correction after the draft exists costs a rewrite. (Sprint 4: the production-bound framing arrived after the results memo was drafted and materially changed it.)

## Config-provenance check (mandatory when porting configs; Sprint 3 retro improvement 2)

A frozen or tuned configuration carried from one dataset to another is a HYPOTHESIS, not a setting. Planning any item that ports a config records where the config came from (dataset, class balance, scale) and sanity-checks it against the target's characteristics -- imbalance first. A config whose provenance data differs materially gets a cheap proxy/smoke evaluation before full runs.

## Capability pre-flight (mandatory for tool-dependent items)

Any item that depends on an external capability (a GitHub API behavior, a library's SQLite feature, a PDF/text-extraction tool) gets a ~5-minute spike proving the single primitive it depends on BEFORE the item is estimated or built. If the spike fails, the item is re-scoped first. Also applies to environment preconditions in validation steps: confirm the environment actually works now, do not assume.

**The pre-flight tests the request shape the CODE will send, not a simpler one (Sprint 4 improvement 3).** Probe the exact call, with the same batching, headers and pacing the implementation will use. Sprint 4's arXiv pre-flight fetched one id, found the User-Agent that works, and passed; the implementation then used the API's own `id_list` to batch many ids per request, which arXiv answers with HTTP 406 and follows with a multi-minute refusal of every further request from that client, single ids included. That cost about 90 minutes mid-sprint to diagnose, and the diagnosis was slowed by probing in bursts, which extended the block being measured. A pre-flight that differs from production in batching, concurrency or headers has tested a different request. When a probe does hit a rate limit or a refusal, pace the follow-up probes at the documented interval rather than retrying immediately: the retry is then part of the measurement, not a second cause.

**The pre-flight inventories CODE, not only documents (Sprint 10 improvement 6).** Grep the source tree for whatever the item is about to change, not just the docs that mention it. F40's card listed four documents referencing the path being moved and was verified against exactly those four. It missed `data.py`, which hardcoded the ULB dataset location -- so the repository that Appendix C promises "regenerates every figure" would have worked on no machine but the author's. The card was right about every document and silent about the one line that mattered.

**A task that adds records at scale states which derived fields run on them (Sprint 6 retrospective I5, 2026-10-05).** For a bulk load, the plan names each computed or derived field the new records will carry (probes, back-fills, links), with its runtime sized from a pilot, or names the card that defers it. Sprint 6 sized its computed-field probes for the 347 papers already in the store and loaded 1,402 more without saying whether they would be probed; they were not, and F52 was carded at Manual Validation. The question costs one line at planning and a sprint of drift when it is skipped.

**Every option in a decision states its cost (Sprint 7 retrospective I1, 2026-10-09).** Extends the line above from derived fields to every decision the team lead makes at planning. Each numbered option carries its runtime for one run, computed from that option's own inputs (requests per item, spacing, cap, pauses), and, when the option adds a step that recurs (each sprint, each Phase 1.3), its cost per recurrence and how often it recurs. Sprint 7 planned Task C at 5.8 hours from one request per paper at 15 s; the approved options (Q5 = 1, two requests per paper; Q7, 18 s) made it 36 hours, and Task D built a refresh "each cycle" that would have cost about two nights every sprint. Neither cost was in front of the team lead at the choice, and Task D was replaced at Manual Validation by a yearly re-check. A cost stated in the option is a decision made once; a cost discovered after approval is rework.

## Defined-scope rule (team lead, 2026-08-30 -- binding)

Sprint scope is DEFINED, never additive: the team lead's selection list IS the complete scope. Items previously proposed, drafted, or carded are NOT in scope unless they appear in the selection. If an unselected item looks critical-path, raise it as a question during refinement; never plan it in by inference. Cards created for unselected items are closed as premature and recreated at the sprint that selects them.

## Planning inputs and outputs (Phase 3)

Inputs: sprint goal (1-2 sentences), refined candidates (BACKLOG_REFINEMENT.md format), velocity actuals. Outputs: SPRINT_N_PLAN.md (objective, tasks, quantifiable acceptance criteria, estimates in minutes, risk, model assignments), previous sprint's SUMMARY doc, one GitHub sprint card per task (template in .github/ISSUE_TEMPLATE/sprint_card.yml), draft PR updated.

## Card standards

- **Definition of Ready** (one line): scope clear, acceptance criteria quantifiable, estimate assigned, no unresolved blockers, priority set, owner named.
- **Task-level Definition of Done** (referenced, not copy-pasted): acceptance criteria met with evidence; tests green; every touched record's provenance and evidence_tag set; docs updated in the same commit; committed with the issue number.
- Every card carries: Sprint number, Category, Priority, What/Why, Acceptance Criteria, Model Assignment + Complexity, Owner (team lead or Claude).
- Team-lead-owned cards (portal actions, external sends, approvals) are tracked like any other card; Claude verifies and records completion evidence but never executes them.

## Estimation

Minutes, from recorded actuals of comparable step-types; `[no-history]` + timebox where uncalibrated. Re-estimate after plan-to-branch-state verification findings (workflow 3.2.2.1/3.2.2.2). Record actuals at task completion; recompute at retro Category 3.

### Data-precondition check for "validate/check X against Y" items (Sprint 2 retrospective improvement 3)

Before estimating a card phrased as "validate," "check," "spot-check," or "compare" X against Y, confirm X actually exists to be checked -- do not assume it because the card's own name implies it. Sprint 2's Task B ("spot-check the store's assertions against the HSBC submission's own determinations") was estimated assuming matching assertions already existed in the store; none did, which turned a spot-check into an extraction-then-check task and expanded scope mid-sprint (a real, correct expansion, but one the estimate should have anticipated). This is the same failure mode the Capability pre-flight above guards for tool/environment preconditions, applied to data preconditions instead: a 5-minute check (does at least one record of the class being validated exist?) before the item is estimated, not after work starts.

### Calibration from recorded actuals (Sprint 5 retrospective improvement 7, 2026-09-25)

Two sprints now carry `## Actuals`, and they point the same way. Sprint 4
estimated 785 Claude-side minutes; Sprint 5 estimated 780 and executed in
about 108 minutes of coordinator wall clock (plan approval 08:19 to the last
task commit 10:07, 2026-09-24), with about 126 more for Manual Validation
fixes. Coordinator-minute estimates overstated the work 4 to 7 times
wherever agents or background runs carried it, and ran OVER only where an
external API refused requests (Sprint 4 Task C, 1.7x).

So: estimate the coordinator's time as the judgment steps only (rules
written, dry runs read, quotes checked, reviews answered), and put the rest
in the **Runtime** column with its dominant term. The Sprint 5 runtime
numbers, sized that way, were the accurate ones (arXiv at 13 s per id under
refusal matched the planning pre-flight). Plan one review-and-fix cycle per
structural task (see the Phase 4 fresh-eyes rule), because that is where
Sprint 5's unplanned time went.

### Runtime is estimated SEPARATELY from implementation (Sprint 8 improvement 1)

Any task that produces results by running over a dataset carries TWO numbers in
the plan's task table: **Est** (time to write the code) and **Runtime** (expected
wall-clock of the run itself, computed from the ACTUAL row count, not assumed
from a smaller run).

Sprint 8 Task C was estimated at 120 minutes, which covered writing the runner.
The run then consumed 84 minutes without finishing a single fold and was killed
by its own timeout. The cause was a KNN H-matrix build that is
O(n_train x n_query) at 495,902 rows. The task had been audited for protocol
compliance and never once sized for runtime: those are different questions and
only one was asked.

Rules:

- State the dominant cost and its complexity in the task row, e.g. "KNN H-build
  O(n_train x n_query), 495,902 x 56,746".
- **NAME the dominant term and show its measurement (Sprint 9 improvement 2).**
  This rule was FOLLOWED in Sprint 9 and the estimate still missed by 47x: 10
  minutes planned against 7.9 hours actual, per run, three times. The twins and
  the GBDTs were both sized from real fits, and the GAM twin was piloted
  specifically because it looked like the risk. What was never sized was the
  CVQBoost pool build -- 300 seconds of the 335 per cell, the single dominant
  term, simply not on the list of things being thought about.

  So "I estimated the runtime" is not the bar. The bar is naming which
  component dominates and showing the number: "pool build 300s of 335s per
  cell, measured on the real split". If you cannot say which component
  dominates, the sizing is not finished -- enumerate every step the task
  executes, not the ones that come to mind.
- If the runtime cannot be estimated, say `[unbounded]` and add a PILOT on a
  subsample as a preceding task. Never let an unsized run start.
- Any run expected to exceed 30 minutes must emit heartbeat progress to a file
  before it is launched, not after it worries someone.

### A card justified by a measurement must name what would disprove it (Sprint 8 improvement 2)

If a card's rationale rests on a measurement, the card states a **Premise
falsifier**: the specific observation that would show the premise is wrong. If
no such observation can be named, the premise is unverified and the card does
not start.

F36 is the worked counter-example, and it cost a full card. Its premise was that
the appendix wasted page space to table break-waste. Its dry run removed all
five tables and observed the document shrink to 3 pages, which was read as
confirmation. It could not have been anything else: removing tables removes
their content AND their space, so the document was always going to shrink. The
check could only confirm. Direct measurement later showed every page already
filled its text block, with zero free space anywhere.

A check that cannot fail is not evidence. Write the falsifier first, and if the
dry run cannot produce the failing observation, redesign the dry run.

### A verification sprint GENERATES work; budget for it (Sprint 13 improvement 2)

A sprint whose tasks are "check that X is true" produces a second body of work
the moment a check fails, and that work is invisible at planning time because it
is contingent on findings that do not exist yet.

Sprint 13 measured it. Tasks A to D were estimated at about 200 minutes and ran
close to that. The six approved document corrections, the A32 amendment, one
backout and two re-renders added roughly 60 minutes that no card carried. None
of it was scope creep: every item came from a check doing exactly its job.

Rule: any sprint whose scope is dominated by verification carries a stated
**30% findings allowance** on top of its task estimates, named in the plan rather
than absorbed silently. If the checks all pass, the allowance is returned and the
sprint finishes early, which is the good outcome and should be recorded as such.

## Risk assessment per sprint plan

Each plan lists its top risks with mitigation: for this project always consider schema/provenance correctness, team-lead adjudication cost per record (the number ADR-0004 names as the design's own constraint), and context/session continuity.
