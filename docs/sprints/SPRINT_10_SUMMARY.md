# Sprint 10 Summary: Fix the Hooks and the Dirac Records, Then Read the Next 74

**Dates**: 2026-10-18 to 2026-10-21. **Branch**: `feature/20261018_Sprint_10`.
**PR**: #101 into develop. **Issues**: #102 to #111 (Tasks A to J).
Sources: the plan (`SPRINT_10_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_10_RETROSPECTIVE.md`), `.claude/sprint_status.json`.
Every count below is a snapshot as of 2026-10-21.

## What shipped

- **F81 (Task A, #102).** The code-edit hook cuts a command at its own
  `;`, `&` or `|` outside quotes, so a read of a code file followed by
  another command's `-i` passes. Three automated security reviews each
  found a bypass (escapes, redirects, substitutions, mid-word quotes); all
  fixed.
- **F88, the F39 release (Task B, #103).** Models unchanged since F67; the
  Sprint 9 reader outcomes logged; readers put their own conclusions in
  `reader_inference`, never in a value.
- **F50 (Task C, #104).** The Cyc answer document's point 7 qualified by
  Cyc's stored counts, as a dated amendment.
- **F86 (Task D, #105).** The DOI probe asks DataCite after a Crossref 404;
  the Zenodo record answered. 157 of 256 DOI records hold no primary
  answer, none due before mid-2027.
- **F82 (Task E, #106).** The never-write hook blocks abbreviated and
  program-running git options per subcommand. Changed commitment:
  `--ext-diff` and `--textconv` were unblocked after review, because git
  runs those programs on a plain diff anyway, so the block guarded nothing.
- **F84 (Task F, #107).** ADR-0004 A10 and its correction: `platform:dirac-1`
  beside `dirac-3` and `dirac-3s`; nine QCi records retagged, 12
  assertions. Approved at Manual Validation (Q1 = 1).
- **F85 (Task G, #108).** Phase 2's Dirac-3S verification entered at Phase
  2 commit e126dbd: four hardware assertions.
- **F83 (Task H, #109).** Per-instance optimization bounds sourced (Boyd
  and Vandenberghe chapter 5; Gurobi's MIPGap) and the ceilings answer
  document amended.
- **F89, the F57 release (Task I, #110).** 74 `qml` records selected: 64
  read with 216 assertions, 1 refused, 9 with no free copy (Valdez 2023
  retracted; the other 8 carded as F90 at the team lead's request).
- **F87 (Task J, #111).** Discovery streams drop off-topic kinds before
  ranking: on Sprint 9's pool, 13 excluded records fell to 3 with none
  accepted lost. Changed commitment: measured on the saved pool, then
  re-run live at Manual Validation (Q4 = 2): 14 dropped before ranking; 91
  candidates entered at `seen` (Q6), two moved from the qml stream to `ml`
  at the team lead's request.
- **Retrospective I1 and I2** applied (team lead; I3 skipped): the quote
  check is in the write path (`insert_verified_assertion`), and the
  coordinator's own edits name their source passages
  (`require_edit_basis`); intake section 31.

Store: 2,190 -> 2,284 papers (148 -> 224 at `read`); 557 -> 793
assertions. F57 count 2,060 at `seen` or `screened`, 2,057 never read.
Suite: 950 -> 1,084.

## Manual Validation decisions

- Q1 = 1: ADR-0004 A10 and its correction approved as written.
- Q2 = 1: a registry answer with nothing recordable stays due; re-reported
  at each Phase 1.3.
- Q3 = 1: ML libraries stay in discovery review.
- Q4 = 2: the live discovery re-run, done during Manual Validation.
- Q5 = 1: F57's closing rule to the retrospective, where the team lead
  then skipped it (I3); the card keeps its rule.
- Q6: 6 more candidates excluded; FCHL and the alchemical paper moved to
  `ml`.
- Step 5 (8 hand-downloads) moved to Sprint 11 as F90. A validation step
  asking the team lead to run a shell command to check a hook was rejected:
  hooks fire only on Claude's tool calls (workflow rule added).

## Actuals

Wall clock is commit-to-commit from `git log` (local time); lower bounds,
and subagents ran in parallel. Plan estimate: 375 minutes.

- Plan approved 2026-10-18 15:56; Manual Validation handed over 19:14:
  about 200 minutes for all ten tasks with their reviews, about 53 percent
  of the estimate (Sprint 9: 37 percent).
- Reviews and fix cycles set the end of A (three security rounds), E
  (three), F, G, I and J.
- After Manual Validation: decisions 2026-10-19 00:27; live re-run 01:14
  (about 50 minutes of requests); 91 entries 09:29 to 09:47; retrospective
  2026-10-19; I1 and I2 applied 2026-10-21.

## Findings surfaced

- Four of the coordinator's own reads were wrong (F84's O(n^3) cut, F85's
  band attribution, F89's Carleman complexity and root-2 threshold); every
  one was caught by a fresh-eyes review before Manual Validation. I1 and I2
  are the response.
- On F89's edits, I1's number check flags the root-2 value and four values
  whose figures are in the source but not in their quotes; none is wrong.
- The F57 card's closing rule cannot be met while refused records stay
  `seen` (kept, team lead).
- No admission-against-interest candidates this sprint.

## PR reviews

- Every task's own fresh-eyes review ran during Phase 4; findings fixed
  before the Manual Validation hand-over.
- **Claude (fresh eyes) on I1 and I2** (74049f0): four findings, all
  fixed in b45b2b5: a value that was only a number skipped the check;
  sign flips and flipped inequalities passed; the scan missed aliased
  imports and scripts not named `sprint*`.
- **Copilot**: requested 2026-10-21; result recorded at Phase 7.7.

## Verification

- Suite 1,084 passed at b45b2b5, including the `live_store` tests.
- CI green on every push since the hand-over.
- Issues #102 to #111 are open and close by PR #101's `Closes` lines on the
  merge into develop.
