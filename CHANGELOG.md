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
