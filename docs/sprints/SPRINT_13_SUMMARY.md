# Sprint 13 Summary: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records

**Dates**: 2026-10-24 to 2026-10-28. **Branch**: `feature/20261024_Sprint_13`.
**PR**: #131 into develop. **Issues**: #132 to #138 (Tasks A to G).
Sources: the plan (`SPRINT_13_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_13_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 48 to 53 (`docs/INTAKE_WORKFLOW.md`). Every count below is
a snapshot as of 2026-10-28.

## What shipped

- **F107 (Task A, #132).** The ".;" join corrected in 16 paper records'
  evidence (two source-printed ".;" kept); 5 theoretical results kept LOW
  now name their own cause instead of "an empirical result". A `live_store`
  guard reads every text column of the paper and assertion tables.
- **F111 (Task B, #133).** The F39 release: every tier's id, price,
  context, maximum output and retirement date unchanged on 2026-10-25;
  Sprint 11's and 12's outcomes logged; one rule added: a reader's
  certainty suggestion is never applied.
- **F109 (Task C, #134).** `Papers\` held 180 PDFs, each named by a record.
- **F110 (Task D, #135).** Roadmap-to-QML still at a239747648; no new paper.
- **F108 (Task E, #136).** Phase 2 read at 9cbe5ba: F162 entered (one
  reference record, 2 SIM assertions under `hsbc-2026`); three F102
  values corrected.
- **F112 (Task F, #137).** First F57's I2: every LOW names its reason
  through `store.grading.low_grade`. Then all 806 readable `qml` records:
  795 read in 100 groups (2,710 assertions), 11 with no copy, each with
  its reason.
- **F113 (Task G, #138), added at Manual Validation.** Manual Validation
  Q2 to Q4 first (the write-path rule reads parsed code; `--changed` runs
  the document guards; common names after a source's spelling). The
  reading budget removed everywhere. Then the full re-read: groups g001
  to g042 read whole and applied (210 records: 208 `full`, 2 `partial`;
  5,489 assertions written or synced). Groups g043 on went to F114's cloud
  readers, one paper per session; they stopped at $0 credit with 302
  results fetched and not yet reviewed (F117), 3 papers kept unread, 1,126
  records backlogged.
- **Library (outside git).** Brighindi's PHI-OMEGA paper, three posts and
  their images, the comment thread and five code sources, in two
  references (F119, first in Sprint 14).

Store: 2,334 -> 2,335 papers (869 -> 1,653 at `read`); 2,970 -> 10,735
assertions (4,059 HIGH). Papers at `seen` or `screened` with no read row:
1,449 -> 654. Suite: 1,253 -> 1,424 at the post-retrospective full run.

## Manual Validation decisions

- At planning, Q1 = 1 (all 806). At Manual Validation: Q2 = fix now ("before reading any more papers"); Q3
  and Q4 fixed. Task G added (no reading budget). Q5 = 1 (the
  hand-download list). Q7 = 2 (Task G's reads stored `full` or
  `partial`). Q8 = 1 (the no-copy papers and repositories stay in F114).
  Q9 = 1 and Q10 = 1 (F119 first in Sprint 14, files added now). Q11 = 1,
  Q12 = 1, Q13 = 2 (F117 in Sprint 14). Team lead, 2026-10-28: "Manual
  Validation complete".

## Actuals

Wall clock from `git log` (local time). Plan estimate for A to F: about
1,490 minutes.

- Plan approved 2026-10-25 00:47; first Manual Validation hand-over 07:12:
  385 minutes for A to F, with reader time in the background (about 26
  percent of the estimate; Sprint 12: 24 percent).
- Task G (no estimate as a limit): 2026-10-25 14:47 to the apply on
  2026-10-27, with F114's cloud runs on 2026-10-26 and 2026-10-27.
- Subagents: 100 Sonnet 5.5 reader groups for F, 42 for G's local groups,
  302 cloud sessions, and one fresh-eyes reviewer per code or store commit.

## Findings surfaced

- Task G's apply rewrote 114 Task F read rows from the same day; the full
  suite found it, the store was repaired exactly from the pre-apply
  backup, and both scripts now match their own rows by wording. The
  retrospective's I1, I2 and I4 add the guards (see the retrospective).
- The sync wrote one column at a time and broke the absence CHECK on the
  trial apply (fixed before the real apply).
- The CHANGELOG fell 19 commits behind; caught up, and a test now names
  any commit without an entry.
