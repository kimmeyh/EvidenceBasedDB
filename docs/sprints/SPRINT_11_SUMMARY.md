# Sprint 11 Summary: Enter QCi's Answers, Then Read 200 Records and Every New Paper

**Dates**: 2026-10-21 to 2026-10-23. **Branch**: `feature/20261021_Sprint_11`.
**PR**: #113 into develop. **Issues**: #114 to #120 (Tasks A to G).
Sources: the plan (`SPRINT_11_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_11_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 32 to 41 (`docs/INTAKE_WORKFLOW.md`). Every count below is
a snapshot as of 2026-10-23.

## What shipped

- **F99, the F39 release (Task A, #114).** Models unchanged on Anthropic's
  pages 2026-10-21; Sprint 10's reader outcomes logged; the parallel-reader
  pattern recorded.
- **F94 (Task B, #115).** Backlog cards adopt spamfilter-multi's practices:
  minutes, a Value line and Acceptance on every card, with a test; each
  practice adopted, adapted or declined in `BACKLOG_REFINEMENT.md`.
- **F92 (Task C, #116).** QCi's three emails of 2026-10-20 and 2026-10-21
  entered from Phase 2's `docs/qci_package/`: 18 assertions. Correction
  during review: one `supports` link failed ADR-0004 A8(b) and was
  withdrawn by name.
- **F93 (Task D, #117).** Phase 2's F108 result: no ceiling method recovered
  a known ceiling on a simulator; 4 assertions and a dated amendment to the
  ceilings answer document.
- **F91 (Task E, #118).** Google Quantum AI's magic state cultivation paper,
  by DOI with the free preprint read: 6 assertions.
- **F97, the F95 release (Task F, #119).** 38 new files in `Papers\` and the
  team lead's list to 36 records (7 new) and 6 repositories; 125 assertions
  from 37 records.
- **F96, the F57 release (Task G, #120).** 200 records by relevance, one
  ledger, up to 5 readers: 649 assertions from 189 records; 8 with no copy
  (7 for hand download, Mezquita 2021 retracted).
- **Manual Validation decisions.** `NVIDIA/auto-ontology-eval` linked
  `code-of` its blog on the team lead's decision (Q1 = 2); the
  hand-download list computed from the store in priority order, each entry
  with its target file name and why it matters, shown by the
  `hand-download-list` skill (Q2, Q3 = 1: F62's discovery papers joined it).
  F100 carded (faster suite); F98 and F95's next repository named.
- **Retrospective I1a, I1b, I2, I4 applied** (team lead, 2026-10-23); I3
  carded on F57 from Sprint 12's release; I5 skipped. See Findings.

Store: 2,284 -> 2,302 papers (224 -> 455 at `read`); 793 -> 1,595
assertions. F57 count: 1,847 at `seen` or `screened`. Suite: 1,084 ->
1,175.

## Manual Validation decisions

- Items 1 to 5: approved or acknowledged.
- Q1 = 2: link auto-ontology-eval, its evidence naming the decision (the
  first source link resting on a decision, not a source sentence).
- Q2: an ongoing hand-download list in priority order; order confirmed at
  the retrospective (Q2 = 1).
- Q3 = 1: F62's 22 discovery papers join the list (done now, not in Sprint
  12 as the option said; disclosed).

## Actuals

Wall clock is commit-to-commit from `git log` (local time); lower bounds,
and readers ran in parallel. Plan estimate: 655 minutes.

- Plan approved 2026-10-21 23:41; Manual Validation handed over 2026-10-22
  02:42: about 181 minutes for all seven tasks with their reviews, about 28
  percent of the estimate (Sprint 10: 53 percent; Sprint 9: 37 percent).
- Per task, lower bounds with G overlapping the rest: A 19m, B 10m, C, D
  and E together 44m, F and G together 93m, hand-over 15m. Task G's 325m
  assumed serial reads; the ledger and 5 readers cut it most.
- After the hand-over: Manual Validation decisions and suite runs
  2026-10-22 11:59 to 12:54 (about 2 hours of work in no estimate);
  retrospective improvements 2026-10-23 09:36 to 10:11, with three full
  suites of about 13 minutes each.

## Findings surfaced

- The first F and G applies ran without `require_edit_basis` and with the
  figure check only printed; the full suite and a fresh-eyes review caught
  it (7 values past their quotes, measured results at HIGH). I1a and I1b
  move those checks into `require_verbatim` and the backup gate.
- I1a's new check found 2 of 1,595 stored quotes never fully checked:
  F92's (a missing space after ";"; corrected and re-applied) and Sprint
  7's `cyc-2007-eight-tactic-types` (on the Sprint 12 plan list).
- An interim message called the full suite passed before its output was
  read; I2's runner prints one verdict from the exit code and the commit
  hook refuses a commit of a tree with a red or invalid verdict.
- The code-edit hook blocked read-only searches whose pattern named sed;
  I4 makes the Edit tool the one way to edit any repository file and
  treats search patterns as data.
- Rule decided for F100: the full suite runs twice per sprint, before
  Manual Validation and after retrospective improvements (Q2 = 1: the
  targeted runner mode is built in F100 from timings).

## PR reviews

- Each task's fresh-eyes review ran during Phase 4; findings fixed before
  the hand-over (the A8(b) link, the edit-basis and figure checks, the HIGH
  grades).
- An automated security review of bc658b1 found the commit hook importing
  the suite runner from the command's repository; fixed in 9046f08, proven
  by injection.
- Copilot: no review was requested on PR #113; the team lead waived it,
  2026-10-23 ("no need to re-request the copilot review").

## Verification

- Suite 1,175 passed at 7db1e84 through `scripts/run_suite.py`
  (SUITE PASSED, rc=0), including the `live_store` tests.
- CI green on every push since the hand-over.
- Issues #114 to #120 close by PR #113's `Closes` lines on the merge into
  develop.
