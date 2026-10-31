# Sprint 14 Summary: Read PHI-OMEGA, Review the 302 Cloud Reads, Then Learn What the Store Says

**Dates**: 2026-10-29 to 2026-10-31. **Branch**: `feature/20261029_Sprint_14`.
**PR**: #140 into develop. **Issues**: #141 to #147 (Tasks A to G).
Sources: the plan (`SPRINT_14_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_14_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 54 to 59 (`docs/INTAKE_WORKFLOW.md`). Every count below is
a snapshot as of 2026-10-31.

## What shipped

- **F119 (Task A, #141).** Brighindi's PHI-OMEGA paper, posts, images and
  code entered: 4 sources, 12 assertions, with the contradicts links the
  fresh-eyes reviews settled.
- **F122 (Task B, #142).** The F95 release: 165 unnamed PDFs in `Papers\`
  linked to their records by the ledger; 1 was F119's paper.
- **F123 (Task C, #143).** Roadmap-to-QML at ea6f42a7c0: 4 papers entered,
  7 withdrawn or retracted marks checked.
- **F120 (Task D, #144).** Phase 2's Sprint 29 results (F156, F158, F160,
  F166) entered from 22d16c3; one F108 value corrected.
- **F117 and F114 (Tasks E and F, #145 and #146).** The 302 cloud results
  rebuilt from their branches, reviewed by the Sonnet tier with the
  coordinator's sign-off, and applied with F114's local reads: first 47
  groups (7,715 assertions; the first apply was restored and re-run as
  4d969d9), then, after Manual Validation, the last 19 groups (5,000 new
  assertions: 1,796 HIGH, 3,204 LOW) and 28 certainty settlements by the
  team lead. 18 papers stay out (the team lead's decision); 8 records
  stay unread (F125).
- **F118 (Task G, #147).** `docs/spikes/F118_WHAT_THE_STORE_SAYS.md`:
  what the store says over 16 themes, what it means for the fraud
  challenge, and what Phase 2 should run, before and after 14 Nov.
  Updated in place on 2026-10-31 with F176, production scale, a
  10,000-logical-qubit machine, and experiments that would raise stored
  LOW claims.
- **Retrospective improvements, all done in this sprint (Q1 to Q7).** The
  hand-edit rule (Q1); the apply lists fields no review item names (Q2);
  finalize refuses an applied group or reads a named store (Q3); the dry
  run names every refusal (Q4); the applier renamed
  `scripts/full_read_apply.py` (Q5); the two live apply tests share one
  apply (Q6); one period before "NOT upgraded" in 900 stored reasons and
  at its source (Q7, INTAKE 59). Q8 carded as F130; Q9 added to F128.

Store: 2,335 -> 2,345 papers (1,653 -> 1,789 at `read`); 10,735 -> 23,653
assertions (4,059 -> 8,167 HIGH). Papers at `seen` or `screened` with no
read row: 654 -> 524.

## Manual Validation decisions

- At planning: Q1 = 2 (F114 at 50 papers, with Boyd), Q2 = 1, Q3 = 1.
- At Manual Validation (2026-10-31): Q1 = 1 (the 28 settlements as
  recommended), Q2 = 1 (the 18 papers stay out). Team lead: "Manual
  Validation complete".
- Retrospective (2026-10-31): "Very Good" in every rated category; all
  nine improvement questions answered option 1.

## Actuals

Wall clock from `git log` (local time). Plan estimate for A to G: about
1,195 minutes at the cards' estimates.

- Plan approved 2026-10-30 09:19; Manual Validation hand-over 21:43: 744
  minutes for A to G, with reader and review tiers in the background
  (about 62 percent of the estimate; Sprint 13: 26 percent, which had no
  cloud review to run).
- After Manual Validation (2026-10-31 13:41 on): the last 19 groups, three
  review-and-fix rounds, the retrospective and its seven improvements.
- Subagents: the Sonnet review tier per group, F114's local readers, the
  F118 theme readers, and one fresh-eyes reviewer per code or store
  commit.

## Findings surfaced

- The reader's nearest-fit context replaced two stored contexts that no
  review decided (one a `platform:dirac-3`); the live suite found it.
  Guarded by the stored-context check and, since Q2, by the "undecided"
  list on every apply.
- A guard proven red once went vacuous after a data change (the context
  test, once the sign-off named its ids). The test now takes them out.
- Settlement text edited by pattern missed variants in 5 of 13 reasons;
  each was edited by hand, and Q1 makes that the rule.
- A format bug from before this sprint put a doubled period before "NOT
  upgraded"; most of its 900 stored instances were written in Sprint 14.
  Fixed at the source and in the store (Q7). Its fresh-eyes review found
  that the format note had moved 365 full-read records' `updated` date,
  which would have made the sync guard drop a corrected sign-off; the
  guard now reads the date of the last real change.
