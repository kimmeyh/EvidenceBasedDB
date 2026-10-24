# Sprint 12 Summary: Fix the Entities, Speed the Suite, Then Read 400 Records

**Dates**: 2026-10-23 to 2026-10-24. **Branch**: `feature/20261023_Sprint_12`.
**PR**: #122 into develop. **Issues**: #123 to #129 (Tasks A to G).
Sources: the plan (`SPRINT_12_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_12_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 42 to 47 (`docs/INTAKE_WORKFLOW.md`). Every count below is
a snapshot as of 2026-10-24.

## What shipped

- **F101 (Task A, #123).** Every stored "&amp;" corrected (4 records, 6
  fields); `store.citations` unescapes provider text; a `live_store` test
  fails on any stored HTML entity. The stray-quote check found 3 more
  assertions whose quotes never parsed, and the review of 5466953 found 7
  Sprint 5 contexts with no quote marks; all re-quoted, values corrected
  where the source said less.
- **F100 (Task B, #124).** The full suite in 199 s warm (781 s before;
  602 s cold): PDF text cached by SHA-256, one store copy per session where
  a test only reads. `run_suite.py --changed` runs the changed tests and
  every test that names a changed module or file; the workflow's Phase 4
  rule names it.
- **F102 (Task C, #125).** Phase 2's Sprint 28 results entered by the
  inbound path at Phase 2's commit: 7 reference records and 12 assertions,
  F111 included.
- **F106 (Task D, #126).** ADR-0005 A11: a source link may rest on a
  recorded team-lead decision, its evidence naming who, when and where; a
  test enforces the form.
- **F103 (Task E, #127).** The Classiq circuit challenge: 3 web source
  records, the named repository (unlinked: no source names it as a paper's
  code), 5 assertions. The two-part series is stated in each record, not
  linked.
- **F104 (Task F, #128).** Roadmap-to-QML at a239747648: 21 new papers
  entered, 20 read (74 assertions), 1 withdrawn on arXiv.
- **F105 (Task G, #129).** Sprint 11's I3 first: `store/grading.py` grades
  HIGH only with a named basis, required by the write-path rule. Then 400
  records by citation count from one ledger, 53 groups, up to 5 readers:
  393 read (1,283 assertions), 7 with no copy, each with its reason.

Store: 2,302 -> 2,334 papers (455 -> 869 at `read`); 1,595 -> 2,970
assertions. F57 count: 1,449 at `seen` or `screened` with no read row.
Suite: 1,175 -> 1,253.

## Manual Validation decisions

- ADR-0005 A11 reviewed; the new reads, the hand-download list (43) and
  the PR checked. No decision questions. Team lead, 2026-10-24: "Manual
  Validation complete".

## Actuals

Wall clock from `git log` and the session's own timestamps (local time).
Plan estimate: 990 minutes.

- Plan approved 2026-10-23 13:09; Manual Validation handed over 19:31:
  382 minutes, of which 146 idle at the usage limit (15:55 to 18:20).
  About 236 active minutes, about 24 percent of the estimate (Sprint 11:
  28 percent; Sprint 10: 53 percent).
- First commits: A 13:20, D 13:28, C 13:38, B 14:03, E 14:35, F 15:07, G
  19:00. The tasks overlapped (B's baseline ran 13:20 to 13:33; E started
  13:29), so per-task minutes cannot be separated.
- Subagents: 53 Sonnet 5.5 readers (one group each, up to 5 at once) and
  one fresh-eyes reviewer per code or store commit.

## Findings surfaced

- The 5744e2d review found meaning errors, not count errors: a value said
  a paper ran only on a simulator (it ran on hardware), three values had
  lost a stated condition, and 18 HIGH grades were field statements or
  measured results. All fixed in eeabd3b; a CI test now checks the signs in
  every replaced value against its quotes.
- 3 papers in the slice are withdrawn on arXiv (Mahroo 2023, Jaiswal 2025,
  Banday 2024).
- `--changed` cannot see a store write (retrospective I1).
- One record id begins with a hyphen: `make_id` drops stop words, and the
  first author is "An" (retrospective I3).

## PR reviews

- Each code or store task's fresh-eyes review ran at its commit, in Phase
  4; every finding was fixed or disclosed before the hand-over.
- Copilot: requested on PR #122 on 2026-10-24 by the GraphQL bot path,
  confirmed attached in `reviewRequests`; its findings are handled before
  `gh pr ready`.

## Verification

- Full suite 1,253 passed through `scripts/run_suite.py` (SUITE PASSED,
  rc=0), including the `live_store` tests, on a tree unchanged during the
  run.
- CI green on 18e9f43.
- Issues #123 to #129 close by PR #122's `Closes` lines on the merge into
  develop.
