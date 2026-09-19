# Sprint 3 Summary: Correct the Foundations, Then Measure Adjudication

Created 2026-09-19 per the three-doc rule (workflow 3.2.1), as part of
Phase 7 at the team lead's standing request. Sourced from git history, PR
#20, `docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md` and
`docs/sprints/SPRINT_3_RETROSPECTIVE.md` -- never the master plan, which
this document instead feeds.

**Dates**: 2026-09-18 to 2026-09-19 (no deadline; `SPRINT_3_PLAN.md`'s own
scope statement).
**Branch**: `feature/20260918_Sprint_3`, PR #20 (draft, review in
progress at the time of writing).
**Scope**: F2 (Phase 1 only), F6, F13, F14 -- run first, in that order --
then F7, F8, F9, F10 run second, independently and in parallel, per the
team lead: "they should not be designed to depend on each other." F11
explicitly out of scope.

## What shipped

- **Task A** (F2 Phase 1): read-only survey of `spamfilter-multi` across
  all ten named areas, delegated to a fork. Six genuinely new artifacts
  found and carded as F15-F20 (auto-advance-window hook, Phase 3.3.1
  deliverables hook, mutation-lock pair, model-assignment heuristics
  file, SPRINT_RESUME_GUIDE + startup-check skill, backlog-refinement
  skill wrapper). Most other content was already present here in adapted
  form, since this repository's methodology descends from the same
  source via hsbc-quantum-fraud-2026.
- **Task B** (F6): five actionable PR #1 code-review findings fixed with
  regression tests, each verified by injection. Citation now read from
  `provenance` at the export layer; `validate_paper()` added, enforcing
  `checked_against_source` at tier `read`; per-entry SAVEPOINTs in
  `ingest_seed_set.py` naming the failing entry; `store.script_paths()`
  replacing four copies of path boilerplate; `_copy_nonnull()`/
  `_child_list()` collapsing the repeated export shape, confirmed
  byte-identical by hashing the export before and after. Finding 4 (N+1
  queries) stays deferred as premature.
- **Task C** (F13): the US English fixer/guard pair ported from
  hsbc-quantum-fraud-2026 and adapted. Nineteen real corrections applied
  in living prose. Two defects in the Development Team's own first
  attempt caught before commit: the fixer had no exclusion for frozen ADR
  amendments and sprint docs and rewrote them during its smoke test
  (reverted uncommitted, exclusion list added); the exclusion test was
  vacuous (checked the exclusion constant against itself), fixed to a
  hardcoded expectation and proven by injection.
- **Task D** (F14): `apply_paper_applicability.py` now fails the run on a
  typo'd paper id and on an existing-vs-intended applicability mismatch
  rather than warning and exiting 0; re-run against the live store
  confirmed a clean no-op (44 already matching). First test file for the
  script added.
- **Tasks E-H** (F7-F10): four independent adjudication reviews of the
  same 18 screened-tier papers, each a fresh subagent with zero
  cross-visibility. Haiku 18/18 confirm; Sonnet 18/18 confirm and
  correctly declared the certainty check not applicable (zero yields);
  Opus 7 cross-record inconsistencies; Fable-tier Opus 93 field calls
  verified against primary sources, finding 4 real citation defects and
  two structural problems (`screened` unearned on all 18; value/
  provenance/citation triplication at the store-write layer). Full record
  in `docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`.

## Also delivered

- F21-F24 drafted from the review findings, then consolidated with F12
  into **F25** at the team lead's direction during Manual Validation:
  findings by reviewer (Fable, Opus, Sonnet, Haiku), corrections to the
  existing records, first-try ingestion guards, and an execution sequence
  by dependency; every count re-verified against the store on 2026-09-19.
  Five gaps found in the after-completion review were folded in (the
  `value` field as the third copy; retiring `seed_set_metadata.json` as a
  citation source; three smaller F10 findings; deliberate test updates;
  F11 sequencing).
- F9/F10's backlog cards corrected at planning to remove a sequential-
  dependency design that contradicted the independence requirement.
- Four retrospective improvements applied as commits (see Retrospective
  outcome).
- Process guards proved themselves: `block_ask_user_question.py` blocked
  one call; the end-of-turn status line rule was set and then tightened
  after one guessed timestamp.

## Actuals

Wall clock is commit-to-commit from `git log` (local time, 2026-09-18),
which includes the coordinating session's own overhead; delegated-agent
figures are the tokens and duration each subagent reported on completion.
These are the first recorded actuals in this repository; every plan
estimate to date has been `[no-history]`.

- Phase 3.7 approval to Task A commit: 4 min wall clock at the
  coordinator; the Task A fork itself ran 266 s and consumed 433,817
  tokens (plus a 35 s resend of its report after a context compaction).
- Task B (F6, five findings): 14 min.
- Task C (F13, including the revert and redesign): 9 min.
- Task D (F14): 4 min.
- Tasks E-H (F7-F10, launched together): 13 min wall clock to the
  results commit. Per agent -- Haiku 82,586 tokens / 182 s; Sonnet
  70,021 / 155 s; Opus 75,802 / 208 s; Fable-tier Opus 150,290 / 599 s.
- Approval to last task commit: 46 min (13:57 to 14:43).
- F25 consolidation during Manual Validation (2026-09-19): 17 min between
  the consolidation commit and the fold-in commit; the consolidation's
  own drafting time is not separately recoverable from git.

## Measurement Sprint 3 did NOT produce

Team-lead adjudication minutes per record (F11), by design: this sprint
produced the four independent reviews F11 compares against. F11 is now
sequenced after F25 D1-D3 so the team lead adjudicates API-verified
citations and a tier that means what the ADR says.

## Findings surfaced, now backlogged

- **F15-F20**: six process/tooling cards from the spamfilter-multi
  survey.
- **F25**: adjudication-review remediation -- the paper-record
  corrections and the first-try ingestion guards, superseding F12 and
  F21-F24. Four team-lead decisions are listed at its head for the
  sprint that selects it.

## Retrospective outcome

16 categories x 4 roles. The team lead rated all sixteen "Very Good."
The Development Team rated five categories "Good" (Testing Approach,
Effort Accuracy, Communication, Process Issues, Architecture
Maintenance), all on one theme: its own first attempts needed the
guards more often than they should have, and the Sprint 2 ADR-0005
amendment F10 challenged shows the same pattern at the design level. Four
improvements approved "all 4 now" (2026-09-19): dry-run-by-default for
write-shaped scripts (applied to `us_english_fix.py` with tests), an
`## Actuals` section in every summary (this one is the first), delegated-
report verification against repository state, and review-protocol depth
recorded as a first-class input to F11 and F18. Full detail:
`docs/sprints/SPRINT_3_RETROSPECTIVE.md`.

## Verification

Full test suite at the retrospective commit: see the commit message for
the count (176 passed, 1 pre-existing skip, before the two new dry-run
tests). Every fix verified by injection. Premise falsifier held: zero
export changes across Tasks A-D; each of F7-F10 made zero repository
changes.
