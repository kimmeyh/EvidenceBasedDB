# Sprint 8 Summary: Read QCi's Newest Guide, Then Build the Yearly Re-check

**Dates**: 2026-10-10 to 2026-10-13. **Branch**: `feature/20261010_Sprint_8`.
**PRs**: #77 (the sprint) and #84 (F66, its own branch), both into develop.
**Issues**: #78 to #83 (Tasks A to F) and #85 (Task G, added 2026-10-13).
Sources: the plan (`SPRINT_8_PLAN.md`, with its 2026-10-13 amendment),
`git log`, the issues, the retrospective (`SPRINT_8_RETROSPECTIVE.md`).
Every count below is a snapshot as of 2026-10-13.

## What shipped

- **F66 (Task A, #78, PR #84).** develop is the GitHub default branch; a
  merge into develop closes its issues; release merges to main are tagged
  `sprint-N` (tags `sprint-1` to `sprint-7` pushed); CI stays on PRs into
  develop (team lead). ADR-0001 A2.
- **F67 (Task B, #79).** The haiku tier names Haiku 5.5; the Developers role
  moved to it.
- **F65 with F63 (Task C, #80).** The Dirac-3S User Guide Rev A read in full
  under the new context `platform:dirac-3s` (ADR-0004 A8); 17 Dirac-3S
  assertions; F63's two Dirac-3 admissions; the 19 prior Dirac-3 assertions
  classed against the guide. At Manual Validation (Q7) five admission
  upgrades were applied.
- **F64 (Task D, #81).** The staggered 12-month re-check: 24 computed
  sections, `--due`, arXiv version detection, three report lists (ADR-0005
  A7). After the retrospective, `--due` alone only lists (ADR-0005 A8, I4).
- **F60 (Task E, #82).** 1,397 of 1,440 QMLPapers manifest rows match their
  files; the Asfaw row's real id is 2108.01311, already held.
- **F61 (Task F, #83).** The Massoli survey list: 137 entered at `seen`, 28
  already in the store, 18 refused with reasons.
- **F71 (Task G, #85; added at Phase 7, team lead Q1 = 2).** F65's item
  list, recovered from the team lead's input history: the Dirac-3S
  release, QCi's Continuous Solver Benchmarking review (read in full), the
  Dirac-3 product page (now the Dirac-3S page), and the site diff since
  the 2026-09-24 scrape. 11 assertions; four admission candidates held for
  the team lead. Report: `SPRINT_8_F71_QCI_SITE_CHECK.md`.
- **Retrospective I1 to I6**, all applied (team lead: "apply all 6 now"),
  with a fresh-eyes review and an edge-case pass on the I5 hook.
- **The stored QPU-seconds balance removed** (team lead).

Store: 1,947 -> 2,093 papers; 76 -> 105 assertions (one removed, the QPU
balance). Suite: 617 -> 745.

## Manual Validation decisions

- Q1 = 1, Q2 = 1: ADR-0004 A8 and ADR-0005 A7 approved.
- Q3: F66's changes approved except CI on main (no) and a CI guard test (no).
- Q4 = 1, Q5: `sprint-N` tags, including the seven past releases.
- Q6: no download needed; the Asfaw PDF was already in `Workforce`.
- Q7: all five admission upgrades, once the entanglement statement named
  Dirac-3.
- Q8 = 1: F69 carded (the Cerezo NonArxiv paper).
- Phase 7: F65's four items added as F71 and run (Q1 = 2); QCi's PDFs kept
  with the other references; no second retrospective.

## Actuals

Wall clock is commit-to-commit from `git log` (local time); lower bounds,
since work before a commit does not show. Plan estimate: 792 minutes for A
to F, plus 180 for G.

- Plan approved 2026-10-12 23:01. B 23:04 (3 min; est 30). C 23:16 plus
  review fixes to 23:31 (about 27 min; est 312). D 23:27 plus fixes to
  23:35 (about 19 min; est 240). E 23:40 (5 min; est 30). F 2026-10-13
  00:00 (20 min; est 120). A's Phase B after Manual Validation, 01:17 (est
  60, with Phase A at 23:01).
- Manual Validation: 2026-10-13 00:06 to 08:54. Retrospective and I1-I6:
  08:55 to 11:27; the hook edge-case pass to 12:12.
- G: planned 12:20, done 12:43 (23 min; est 180), including about 9 min of
  fetching (129 pages, 3 s apart).
- The estimates ran high by roughly 4 to 10 times on reading and code
  tasks, as in Sprint 7; reviews, not first builds, set the end of C and D.
- Delegated agents: fresh-eyes reviews of C, D and I1-I6 (read only); every
  finding verified before it was fixed.

## Findings surfaced

- QCi's benchmarking review contradicts its own headline: "zero optimality
  gap across all" planted instances, against Table 6's 7.56 and 9.59
  percent gaps; the press release repeats the headline.
- QCi's documents do not settle which device ran the benchmark (cloud API
  in the review; a direct private-address client and "Dirac-3" in the
  notebook and the text).
- The Dirac-3 product page now serves the Dirac-3S; the Dirac-3
  specification is gone from it.
- F65's list had sat in the team lead's input history since 2026-10-10; it
  was recovered there, not re-sent.

## PR reviews (2026-10-13)

- **Copilot**: #77 no findings; #84 one low finding ("owner" for the
  develop-to-main merge, where the docs say "team lead"), fixed in f8a2be6
  and its thread resolved.
- **Claude (pr-review-toolkit)**: code review (#77 three findings, #84 one
  wording slip), test coverage and silent failures (#77). Fixed in 385f769
  and f8a2be6: the site check's small-section bug and its other gaps, the
  re-check's local-copy lookup, report duplication and date parsing,
  `view.py`'s "None", the F71 script's id match and hashes, and four hook
  gaps. Carded as F74 (Sprint 9): a partial answer resets the re-check
  clock, and a tool failure is reported as the paper's fault. Not changed:
  tests for the one-shot QPU-removal script (already applied; a re-run does
  nothing). The dispositions are posted as one comment on each PR.

## Verification

- Suite 759 passed at the last commit, including the `live_store` tests.
- `gh issue list --label sprint --state open`: #78 (closes with PR #84) and
  #85 (closes with PR #77), both by `Closes` lines that fire on the merge
  into develop.
