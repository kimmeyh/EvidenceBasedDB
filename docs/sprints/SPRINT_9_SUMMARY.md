# Sprint 9 Summary: Read the Ceiling Papers, Then Open the Phase 2 Exchange

**Dates**: 2026-10-14 to 2026-10-17. **Branch**: `feature/20261014_Sprint_9`.
**PR**: #88 into develop. **Issues**: #89 to #99 (Tasks A to K).
Sources: the plan (`SPRINT_9_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_9_RETROSPECTIVE.md`), `.claude/sprint_status.json`.
Every count below is a snapshot as of 2026-10-17.

## What shipped

- **F79 (Task A, #89).** The Phase 2 exchange: each repository reads the
  other freely and never writes to it; a wanted change goes as a prompt the
  team lead pastes. The never-write hook covers Phase 2 (three security
  reviews; the third's evasion forms carded as F82). Inbound path in
  INTAKE section 19; the first Phase 2 record from commit 139fa13. The
  outbound prompt is `SPRINT_9_F79_PHASE2_PROMPT.md`. F81 carded.
- **F68 with F69 (Task B, #90).** The door reads old-style arXiv ids and
  parenthesized DOIs; five Massoli entries and the Wiebe paper entered.
- **F74 (Task C, #91).** Only the primary source resets the re-check clock;
  tool and probe failures are reported as such (ADR-0005 A9).
- **F48 (Task D, #92).** SHA-256 recorded for 112 local files; a moved file
  or changed hash is reported by the re-check.
- **F78 (Task E, #93).** The ceiling-estimation group read and entered, with
  the answer document `docs/research/ceilings-ml-and-optimization.md`. After
  Manual Validation: Chen 2025 read from the team lead's download; Han and
  Verdu 1994 not obtainable, covered by Scarlett's (108) and Chen,
  Guntuboyina and Zhang 2016 (JMLR), entered and read in part (Q6 = 1).
- **F46 (Task F, #94).** 20 pending facts: 15 entered, 2 merged, 3 not
  entered, each with its reason.
- **F80 (Task G, #95).** The first 76-record read-for-claims slice: 65 read,
  233 assertions; 11 refused with reasons (F84 carded). From Sprint 10, F57
  releases 74 records per sprint.
- **F55 (Task H, #96).** 5,620 computed `cites` links from 807 Crossref
  reference lists (ADR-0005 A10, migration with backup); `view.py paper`
  shows cites and cited-by.
- **F56 (Task I, #97).** A computed corroborated flag beside stored
  certainty; same-vendor pairs never count (ADR-0004 A9).
- **F62 (Task J, #98).** Discovery ranked per stream; 87 candidates entered
  at `seen` (Q4 = 1); a hand-download list.
- **F51 (Task K, #99).** Hold checked; stays HOLD.
- **Retrospective I1, I3, I4 and I5** applied (team lead); I2 and I6 skipped.

Store: 2,093 -> 2,190 papers (148 at `read`); 105 -> 557 assertions;
5,620 `cites` links. Suite: 759 -> 925.

## Manual Validation decisions

- ADR-0005 A9 and A10 and ADR-0004 A9 approved as proposed.
- Q1 = 1: an unrecorded-organization corroboration pair counts, labeled.
- Q2 = 2: the Zenodo record carded as F86.
- Q3 = 1: three admission-against-interest upgrades, low to moderate.
- Q4 = 1: every top-listed F62 candidate except 13 off-topic.
- Q5 = 2: Phase 2's F142 (Dirac-3S on B4) carded as F85.
- Q6 = 1: Han and Verdu covered from free sources.

## Actuals

Wall clock is commit-to-commit from `git log` (local time); lower bounds,
and subagents ran in parallel. Plan estimate: 780 minutes.

- Plan approved 2026-10-15 00:05; Manual Validation handed over 04:56: 291
  minutes for all 11 tasks with their reviews, about 37 percent of the
  estimate.
- A 14 min plus 19 of review fixes (est 30). B 2 (est 25). C 4 (est 30).
  D 5 (est 30). E 35 plus 15 (est 195). F 7 (est 117). G 58 plus 29 (est
  210). H, I and K finished at 03:11 to 03:12, alongside G's review (est 45,
  60, 10). J 34 plus 46 (est 90).
- After Manual Validation: decisions applied 2026-10-15 15:22; Task E's
  closed papers 2026-10-16 14:46 (after the team lead's download).
  Retrospective 2026-10-16; I1, I3, I4 and I5 applied 2026-10-17.
- The estimates, already cut by about 3, still ran about 2.7 times high.
  Reviews set the end of E, G and J; Task J's review took longer than its
  build.

## Findings surfaced

- A Fano-type bound cannot set a fraud ceiling: at a positive rate of 0.17
  percent the generalized Fano bound falls to zero once the features carry
  about 2.9 millionths of a nat (coordinator arithmetic on CGZ Corollary 5,
  marked as inference in the answer document).
- Chen 2025's practical estimator is cheaper, not more accurate, than the
  earlier method, and it is never tested on imbalanced classes.
- Phase 2's F142: Dirac-3S returned the B4 reference optimum where Dirac-3
  did not (carded F85).

## PR reviews

- **Copilot** (at e0b580d): one medium finding. `view.py paper` recomputed
  the whole-store corroboration map once per yielded assertion. Fixed: the
  map is computed once per view; test proven by injection. Thread answered
  and resolved.
- **Claude (pr-review-toolkit, fresh eyes)** on the commits after the
  hand-over: three findings, all verified and fixed in 7a0d32d. A corrected
  context was added beside the wrong one; the F80 script kept its own
  six-field sync; the sync tests covered 5 of 13 fields and did not pin the
  not-compared group. Two low notes left as they are: a re-run could move
  `updated` backward (the skipped I2), and NFKC folds superscripts.
- Every task's own fresh-eyes review ran during Phase 4; findings fixed
  before the Manual Validation hand-over.

## Verification

- Suite 925 passed at the last commit, including the `live_store` tests.
- CI green at deb726d. It was red from 070137e (2026-10-15 00:31) to
  52a439a, unnoticed until 2026-10-18: three tests that read local files
  lacked the `live_store` marker (retrospective addendum).
- Issues #89 to #99 are open and close by PR #88's `Closes` lines on the
  merge into develop.
