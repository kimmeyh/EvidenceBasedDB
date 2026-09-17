# Sprint 2 Plan: Validate, Guard, and View the Store

**Dates**: from 2026-09-17. **No deadline.**
**Branch**: `feature/YYYYMMDD_Sprint_2` (cut at kickoff)
**Scope** (DEFINED, team lead 2026-09-17): **F4** (validate the store against
the HSBC submission and the 44 source papers), **F75** (action the 20-paper
ADR checkpoint), **F76** (guard the shared ADR-0004/0005 vocabulary), **F3**
(an easy CLI-startable way to view DB content).

## Objective

Sprint 1 built a store nobody has yet checked against its own ground truth.
This sprint closes that gap on two fronts at once -- **is the store accurate**
(F4), and **is the design still sound at the scale it now holds** (F75) -- then
locks the fix in with a guard (F76) and makes the corrected content usable
(F3).

## Why this sprint exists at all

Sprint 1's Manual Validation and PR #1 review surfaced three findings nobody
had acted on yet: every paper record carries exactly one `context` even
though ADR-0005 defines a separate plural `applicability` field that Task F
never populated (44 of 45 papers currently have an empty `applicability`
array, confirmed 2026-09-17); the store has never been checked against
either of its two ground truths (what the HSBC submission itself determined,
and what the 44 source PDFs actually say); and the adjudication-time
measurement ADR-0004 calls "the number the whole design is constrained by"
was deliberately deferred in Sprint 1 and has still not been produced.
F75 and F76 were also carried from the consumer repository's own backlog
and are gated on exactly the work Sprint 1 just finished (44 papers loaded,
past the ~20 threshold both ADRs name).

## The measurement that outranks the code

**Team-lead adjudication time per record, against ~20 real records.**

This is Sprint 1's own deferred measurement, now due. ADR-0004 names it as
the number the whole design is constrained by: at five minutes per record a
domain knowledge base over QML/ML/QC needs rethinking; at thirty seconds it
is safe. Sprint 1 shipped without it by deliberate team-lead decision, not
by failure -- Task E's single-record dry run was cut short and the team lead
explicitly deferred the measurement to "a future step in a future backlog
item." This sprint is that step, and it runs at a larger, more informative
sample (~20 records) than the one record Sprint 1's premise falsifier
would have used.

## Tasks

| # | Task | Est | Owner |
|---|---|---|---|
| A | F4 part 1: re-derive every paper's real applicability (not just its single primary context) from the actual PDF content; populate `paper_applicability` for all 44 seed-set papers | 180m | Claude |
| B | F4 part 2: spot-check the store's assertions and paper records against the HSBC submission's own determinations (what the consumer repository's documents already settled) | 120m | Claude + **team lead** |
| C | F4 part 3: spot-check the store's content against the 44 source PDFs directly, not against Task F's own extraction notes; resolve the two flagged judgment calls (dwave-2023-operational-excellence-ebook vs. the Freericks book classification) | 150m | Claude + **team lead** |
| D | F76: write the test guarding ADR-0004/ADR-0005 vocabulary agreement (a record naming an undefined context; the ADRs' stated context lists diverging from the database's) | 60m | Claude |
| E | F75: walk both ADRs' six named questions against what Sprint 1 actually built and found; record findings as dated amendments, never edits in place | 90m | Claude + **team lead** |
| F | F75: **the measurement itself** -- time team-lead adjudication across ~20 real records, sourced from the `screened`-tier subset Task F already promoted for variety | [unbounded; team-lead-paced] | **team lead** + Claude |
| G | F3: build `scripts/view.py` (contexts / paper / assertion modes, plain-text and `--json`, no server) against the store AFTER Task A's applicability fix lands | 120m | Claude |

**Sequence**: A first -- it is the one correction every other task either
depends on (G) or would otherwise re-derive by hand (B, C). B and C run in
either order once A is done, since both are independent spot-checks against
different ground truths; running them together lets one team-lead review
session cover both. D can run any time after A, since it only needs the
corrected schema/data shape to test against, not the review itself. E
should run before F, since walking the six named questions is what
surfaces which ~20 records are worth timing (not merely the first 20 by
id). G runs last, after A, so it is never built against the exact
undercount it exists to display correctly.

**Total ~720 minutes of Claude-side work** (12 hours) plus Task F's
team-lead-paced measurement, which is intentionally not estimated in
Claude-minutes since it is the team lead's own serial attention being
measured, plus the standing 30% findings allowance given this sprint is
dominated by verification (SPRINT_PLANNING.md: "a verification sprint
GENERATES work").

## Premise falsifier

**The premise**: this store's records are an accurate, sufficiently
efficient-to-produce representation of their sources, at a scale a single
team lead can actually adjudicate.

**What would disprove it**: (1) Task B or C finds systematic inaccuracies
-- not isolated typos, but a pattern of misattribution or misrepresentation
across multiple records -- which would mean Task F's extraction method
itself is unreliable and needs redesigning before more papers are loaded,
not merely patched record by record; (2) Task F's adjudication-time
measurement lands at or above five minutes per record, which per ADR-0004's
own stated math makes the domain-scale ambition (thousands of records)
untenable at any team size this project actually has.

**The check cannot merely confirm**: both are real measurements against
real records, not a rerun of Sprint 1's own extraction pass on itself. A
result on either axis can send this sprint's own remaining tasks (and
Sprint 3's backlog) back to the drawing board.

## Risks

| Risk | Mitigation |
|---|---|
| **Adjudication cost still sinks the ambition** (Sprint 1's own deferred risk, now due) | Task F measures it directly against ~20 records; ADR-0004's own math names the failure threshold |
| Task A's re-derivation finds MORE than an applicability gap -- e.g. wrong primary contexts too | Task A re-reads every paper's actual content, not just adds applicability rows; a wrong primary context is corrected in the same pass |
| Tasks B/C surface findings large enough to need their own sprint cards | Named explicitly in the premise falsifier; a systematic-inaccuracy finding is a STOP-and-report per SPRINT_STOPPING_CRITERIA.md Criterion 7 (fundamental design failure), not silently absorbed |
| F75's six-question walk finds the schema itself needs to change | Recorded as a dated ADR amendment (ADR-0004/0005's own "early innovation: expect revision" framing), never a silent edit; a spine-level change is Class 1 and needs explicit approval regardless of sprint-plan approval |
| F3 built before Task A's fix lands, baking in the undercount | Sequenced explicitly last in the task order; G's own row states the dependency |
| Task F (the adjudication timing) has no calibrated estimate | Deliberately left `[unbounded; team-lead-paced]` rather than guessed -- this is exactly the number this sprint exists to produce, not one it can assume in advance |

## Definition of Done

- Every one of the 44 seed-set papers has its real applicability re-derived
  from the actual PDF content and recorded in `paper_applicability`, not
  left at the single-context default
- The store's content has been spot-checked against both the HSBC
  submission's own determinations and the 44 source PDFs directly, with
  findings (if any) recorded as issues or ADR amendments rather than
  silently fixed and unrecorded
- A test exists and passes that fails when a record names an undefined
  context, or when the ADRs' stated context lists diverge from the
  database's (F76), verified by injection per this repository's own
  guard-discipline standard
- Both ADRs' six-question checkpoints are walked and answered, with
  findings recorded as dated amendments at the bottom of each ADR
- **Team-lead adjudication time per record is measured against ~20 real
  records and reported**, with its provenance stated (measured, not
  extrapolated or assumed)
- `scripts/view.py` exists with working `contexts`, `paper`, and
  `assertion` modes, built against the corrected applicability data, with
  tests

## Out of scope

F2 (spamfilter-multi deep-dive) and F5 (QCi author/documentation
deep-dive) -- both explicitly deferred by team-lead decision at Sprint 1's
close-out refinement, since running them alongside this sprint's
adjudication-cost measurement would dilute the one question Sprint 2 most
needs to answer. F6 (the six remaining PR #1 code-review findings) --
real but no dependency forces it into this sprint. Any change to the
consumer repository. Ingesting new papers beyond the existing 44 (that is
Sprint 3-or-later scope, gated on this sprint's own accuracy findings).
