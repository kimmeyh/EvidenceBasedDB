# Sprint 18 Summary: The Agreement Map and the HIGH Audit, 30 Papers, and Safer Applies

**Dates**: 2026-11-13 to 2026-11-23. **Branch**: `feature/20261113_Sprint_18`.
**PR**: #183 into develop. **Issues**: #184 to #189 (Tasks A to F).
Sources: the plan (`SPRINT_18_PLAN.md`), `git log`, the issues, the retrospective (`SPRINT_18_RETROSPECTIVE.md`),
`.claude/sprint_status.json`, and intake sections 78 to 81 (`docs/INTAKE_WORKFLOW.md`). Every count below is a
snapshot as of the date it names.

## What shipped

- **F149 (Task A, #184).** The ledger names a new group from the highest gNNN plus one, not from the number of
  groups, so a gap or a deletion cannot reuse a name.
- **F147 (Task B, #185).** `store.ingest.sync_decided_assertion`, the one apply function from Sprint 18 on: it writes
  only the fields a review decided, and a note dated "(Sprint N Manual Validation" protects a team-lead decision from
  a re-apply. The live applier moved to it; the 23 one-time scripts are frozen by a test (q2 = a).
- **F146 (Task C, #186).** On Claude Code subagents, no API spend (q1 = c): 69 runs, about 9.19 million tokens, about
  300 minutes; nothing written to the store.
  - The HIGH audit (2026-11-21): every HIGH assertion with quotes (12,524) has a result: 7,834 held, 4,672 held in
    part, 20 not held. 189 of 189 controls right.
  - The agreement map: 490 screened pairs, 333 supports (279 not independent, 54 independent), 4 contradicts, 153
    unrelated. 18 of 18 controls right. The word-overlap screen found 0 of the store's 24 known relations (F154).
- **F114 (Task D, #187).** 30 papers in 28 groups read in full, reviewed and applied (2,688 assertions entered:
  775 HIGH; 288 theoretical results kept LOW with their cause); a second apply wrote nothing. Intake section 78.
- **F145 (Task E, #188).** qubit-lab.ch's Evidence page entered through the intake door. Intake section 80.
- **F148 (Task F, #189).** `scripts/doc_counts.py`: the counts a document names are printed from the store between
  markers, and a test fails when they differ.

## Manual Validation decisions

- Handed over 2026-11-21 08:17, after CI passed (the first send, while CI was pending, was blocked by the Stop hook).
- 2026-11-21: F150 carded (the full suite once per sprint, as the other repositories do).
- 2026-11-22: F151 carded (every question stored in full in one file, re-asked from it). q4 to q10 as recommended,
  with the team lead's "just do as recommended" (now a standing rule): q7 = a, both of g361's temperatures LOW, each
  naming the other (`scripts/sprint18_q7_grades.py`, backup first); q10 = a, F152 carded. q12, the team lead's rule
  (an independent agreement with an experiment or proof on both sides goes up one level): no pair qualifies that is
  not already HIGH, so nothing changed. q13 = a (F154 carded). q14 to q17 not carded (Phase 2 suggestions, which this
  repository does not make). q18 = b (the second full suite before `gh pr ready` stays).
- 2026-11-23: q11 = a (F153 carded) and q14 = a confirmed.
- Retrospective (2026-11-23): "Very Good" in every rated category; "none" for minor updates, backlog updates and open
  questions. i1 to i5 applied as recommended under the do-as-recommended rule: i1 (agents write results with the
  Write tool only, a test on every prompt from Sprint 19 on), i2 (`test_inventory.py --write` keeps the timings), i3
  (F155 carded), i4 and i5 skipped and tracked. 2026-11-24: the team lead confirmed "i1. a", "i5. b" and, after
  questions, "i2. a i3. a i4. b"; F155 revised to make an id unique when chosen. q19 = a: `CHECKLIST-Phase2-pre.md`
  frozen after Sprint 18 (Phase 2 reads this repository directly).

Store: 37,408 assertions and 11,754 HIGH at the end of Sprint 17 (2026-11-10); 40,112 assertions, 12,528 HIGH,
27,484 LOW, 97 MODERATE, 1 VERY LOW and 2 ungraded on 2026-11-22; 2,373 papers (read 1,853).

## Actuals

Wall clock from `git log` and the status notes (local time). Plan estimate for A to F: about 677 minutes at the
cards' estimates (about 850 at Sprint 17's 1.25 times), plus the readers' time in the background.

- Phase 1: 2026-11-13 11:31 (Phase 1.1 to 1.3 commit). Planning: the plan drafted 2026-11-19 00:21; q1 and q2
  answered and recorded 2026-11-19 20:13; the plan approved 2026-11-20 (q3 = a).
- Tasks A to F: the first task commit 2026-11-21 00:10, the last 08:06. Execution began on 2026-11-20, but no commit
  records the hour, so the actual is not exact: at least about 480 minutes, against about 677 estimated.
- Manual Validation: handed over 2026-11-21 08:17; the decisions applied 2026-11-22 15:57; q11 and q14 confirmed
  2026-11-23. Not estimated: its size followed the decisions.
- Subagents: Sonnet general-purpose readers and reviewers for Task D's 30 papers; 69 Sonnet subagent runs for F146
  (about 9.19 million tokens). No Batch API spend.

## Findings surfaced

- The HIGH grade holds for most assertions checked against their quotes, but 20 did not hold and 4,672 held only in
  part; F152 and F153 follow up. Readers' strictness on "held in part" varied from about 50 to about 90 in 200.
- Subagents' answers were right on all 207 controls, but four broke the write rules (g350, g361, g511 by script;
  a008 by edit) and two mistyped an id (a018, a030): retrospective i1 and F155.
- Five reader ids were already other sources' and were renamed after review (F155).
- `--changed` after a store write takes 9 to 11 minutes, longer than the full suite (about 6): F150.
