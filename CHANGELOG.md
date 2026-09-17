# Changelog

Policy: updated in the SAME commit as the change it describes, under
`## [Unreleased]`, grouped by date, newest first. Format:
`- **type**: Description (Issue #N / PR #N)` with type in
feat | fix | docs | test | chore | process.

**Workflow step 8.1.1 reconciles this file BEFORE backlog refinement, every
delivery cycle.** The same-commit policy held for six days in the consumer
repository and then silently stopped for eight, across seven sprints. A policy
that depends on remembering at the moment of committing is the class of rule
this project keeps having to replace with a step.

## [Unreleased]

### 2026-09-14

- **chore**: Repository seeded from `hsbc-quantum-fraud-2026`. Carried: the
  sprint methodology (execution workflow, process, planning, checklist,
  retrospective, stopping criteria, backlog refinement), quality and testing
  standards, five hooks, three practice ADRs renumbered 0001-0003, and five
  process guards. NOT carried: anything about the fraud submission, the ML/QML
  runs, or Dirac-3 hardware
- **docs**: ADR-0014 and ADR-0015 MOVED here as 0004 and 0005. They are this
  repository's design rather than the consumer's; the originals remain there as
  the record of when the decisions were made
- **chore**: Three hooks deliberately NOT carried --
  `block-unapproved-submission-edit`, `block-reactive-amendment` and
  `block-frozen-history-rewrite`. Each guards a frozen artifact of the fraud
  submission that does not exist here, and a hook guarding a missing file is a
  hook that cannot fire
- **test**: `.claude/settings.json` written STRUCTURALLY via json.dump rather
  than by hand, and every registered path verified to resolve at write time. Two
  hooks in the consumer repository were dead for their entire life because a
  single backslash before `block-` is a JSON escape
- **chore**: corrected a seeding mistake -- the first attempt put the git
  repository inside `D:\Data\Harold\EvidenceBasedDB\` (the non-repo staging
  directory), conflating the two. Reseeded to the correct
  `D:\Data\Harold\github\EvidenceBasedDB\` and removed the misplaced copy,
  verified to hold no uncommitted changes or unpushed commits first.
  `README.md` and `CLAUDE.md` now record the two-directory layout as a table

### 2026-09-15 to 2026-09-17 (Sprint 1, PR #1)

Sprint 1 built the store end to end: Tasks A-H per
`docs/sprints/SPRINT_1_PLAN.md`, plus the sibling-repo write guard and F2-F6
backlog items surfaced at Manual Validation and PR review. Full detail:
`docs/sprints/SPRINT_1_SUMMARY.md` (created during Sprint 2 planning, per
the three-doc rule), `docs/sprints/SPRINT_1_RETROSPECTIVE.md`, and the PR
#1 commit history. This entry summarizes rather than restates those
numbers, per this project's own "a number must be traceable to a committed
generator" standard -- run the suite, don't copy a count.

- **chore**: the five inherited PowerShell hooks converted to Python
  (Task A pre-kickoff), removing the doubled-backslash JSON-escape hazard
  by construction rather than by continued vigilance
- **feat**: SQLite schema for the four record classes (Task B), a
  deterministic JSON export as the committed artifact (Task C), and
  domain-scale contexts seeded per ADR-0004 section 3b (Task D)
- **feat**: one paper (Lenat/Marcus) ingested end to end (Task E); the
  44-paper seed set loaded at `seen`, 17 promoted to `screened` for variety
  (Task F); a determinate-fact resolver for the consumer repository's
  amendment count, computed live rather than stored (Task G)
- **docs**: removed hsbc-quantum-fraud-2026 process content (Dirac-3
  hardware rules, `experiments/src`, `results.json`, a submission calendar)
  presented as this repository's own live rules across 11 files (Task H,
  F1), with a regression test verified by injection
- **chore**: added a hook blocking writes into `spamfilter-multi` or
  `hsbc-quantum-fraud-2026` from this repository's sessions (read access
  stays unrestricted)
- **fix**: PR #1 review (Copilot + Claude) found `assertion_documents` FK
  coupling that blocked citing a document on an assertion with no
  units/rounding, a silently-dropped `citation_context` field, and a
  `--promote` ordering bug that no-opped promotion on an already-seeded
  store. All three fixed with regression tests before merge
- **process**: Sprint 1 retrospective run (16 categories x 4 roles, all
  "Very Good"); F2 (spamfilter-multi deep-dive), F3 (CLI DB viewer), F4
  (accuracy validation against the HSBC submission and the source papers),
  F5 (QCi author/documentation deep-dive), and F6 (remaining PR review
  findings) added to the backlog for Sprint 2 selection
