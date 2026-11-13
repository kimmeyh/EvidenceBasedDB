# Sprint 17 Summary: Test Faster, Then Read on the API Credit

**Dates**: 2026-11-07 to 2026-11-10. **Branch**: `feature/20261107_Sprint_17`.
**PR**: #174 into develop; PR #181 (F144) merged into the sprint branch by the team lead on 2026-11-09.
**Issues**: #175 to #180 (Tasks A to F).
Sources: the plan (`SPRINT_17_PLAN.md`), `git log`, the issues, the retrospective (`SPRINT_17_RETROSPECTIVE.md`),
`.claude/sprint_status.json`, intake sections 75 to 77 (`docs/INTAKE_WORKFLOW.md`), `docs/F140_TESTING_ANALYSIS.md`
and `docs/F143_READING_COST.md`. Every count below is a snapshot as of the date it names.

## What shipped

- **F140 (Task A, #175).** The test inventory (a test fails when a test file is missing from it), the full suite on
  16 workers, no repeat full run on an unchanged tree, the high-impact files on every gate, last failures first, the
  reading tests' duplicate text work removed. The full suite went from about 69 minutes (Sprint 16's last run) to 7
  to 11 minutes. Analysis and every decision in `docs/F140_TESTING_ANALYSIS.md`.
- **F144 (Task B, #176, PR #181).** `scripts/batch_read.py`, the Batch API reader: dry run by default, the $95 cap,
  no send on or after 2026-11-18, no resend, results kept and flagged, the key never printed or written. A 5-paper
  pilot and an 8-paper measurement batch: 13 papers, $3.00 (2026-11-07). After the self-check, 16.6 check problems
  per 100 assertions (71 in 428). Nothing written to the store.
- **F142 (Task C, #177).** Reader telemetry out of the gate's tree id, a sign-off table that adds or splits an
  assertion, long proof appendices split across reviewers, and both status fields set in one step.
- **F141 (Task D, #178).** `view.py paper <id> --full` prints each assertion whole; the default output is unchanged.
- **F114 (Task E, #179).** 10 papers read in full by local readers, reviewed and applied (1,201 assertions entered or
  changed), and a second apply wrote nothing. Ledger groups g230, g295, g296 and g348.
- **F143 (Task F, #180).** The cost per page rose because each page now yields more assertions, most in
  theory-heavy papers; tokens per assertion did not rise. `docs/F143_READING_COST.md`.

## Manual Validation decisions

- q24 = a (2026-11-08): F144's branch combined into the sprint branch; the second working folder removed.
- q5 (2026-11-08): Norton 360 is the active scanner; the team lead applied its exclusions. Full suite 10m16s before,
  6m57s after (one run each).
- 2026-11-09: q11 = a (F147 carded; a card-template line now), q12 skip and track, q13 = a (F148 carded), q14 "NO,
  read the whole paper", q20 = a (161 papers of g297 to g329 split into one-paper groups g349 to g509), q21 and q22
  not needed, q23 = a (8 Task E assertions corrected), q26 = a (F146 carded: the agreement map and the HIGH audit),
  q27 = a, q28 = a (the quotes-first reader rule, replacing q19).
- 2026-11-10: q30 = a (the earlier "q20 b" meant q29 = b: Albash's Grover assertion HIGH again, as a stated limit),
  q31 = a (Pere's LOW reason gains its why).
- Retrospective (2026-11-10): "Very Good" in every rated category; "none" for minor updates, backlog updates and
  open questions. i1 = a (the worktree hook), i2 = b (a checklist line), i3 = b (skip, tracked), i4 = a (a workflow
  line). Category 13 carded as F149.

Store: 36,209 assertions and 11,491 HIGH at planning (2026-11-07); 37,408 assertions, 11,754 HIGH, 25,554 LOW, 97
MODERATE and 1 VERY LOW on 2026-11-10; 2,369 papers.

## Actuals

Wall clock from `git log` and the status notes (local time). Plan estimate for A to F: about 625 minutes at the
cards' estimates, plus the reader time in the background (no reading budget).

- Phase 1 and planning: 2026-11-07 13:04 (Phase 1 commit) to 14:58 (plan approved, key-file hook).
- Tasks A to F: 14:58 on 2026-11-07 to 02:00 on 2026-11-08, about 660 minutes from approval (about 780 from the
  Phase 1 commit), against about 625 estimated. B, its pilot and its measurement batch ran first (to 21:50, with
  A's work interleaved from 17:44); A's decisions were built by 22:50; C and D by 23:21; E applied and F written by
  01:36; the review of E's apply recorded by 02:00.
- Manual Validation follow-up, 2026-11-08 16:14 to 2026-11-10 08:53: the folder merge (q24, two merges), q23 and its
  reviews, q20 and its review, q28, the answers and cards, and q29 to q31. Not estimated: its size followed the
  decisions.
- Batch API: 13 papers, $3.00 of the $95 cap (2026-11-07).
- Subagents: Sonnet 5.5 readers and reviewers for Task E's 10 papers; Sonnet 5.5 on the Batch API for 13 papers;
  general-purpose fresh-eyes reviewers on each script, store and hook change (Task E's apply, q23's apply, the
  applier change, the q20 split). Their per-agent tokens are in Task E's telemetry files; the reviewers' were not
  recorded.

## Findings surfaced

- The batch readers' replies all failed the check, most for a number its quotes do not hold; q28's quotes-first rule
  is the response, to be measured on the next batch.
- A second working folder, made without asking, split the work and cost a merge cycle and a second hand-over
  (retrospective i1, now hook-enforced).
- A correction script that appends must be tested for a second run before its first apply (i2).
- Two assertions have no certainty at all: `cyc-truth-values-four` and `cyc-context-count` (Lenat and Marcus 2023),
  unchanged since 2026-10-03 and entered in Sprint 1's dry run. Found while writing this summary; not changed.
