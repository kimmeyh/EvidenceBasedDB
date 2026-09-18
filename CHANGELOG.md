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

### 2026-09-17 to 2026-09-18 (Sprint 2, PR #11)

Sprint 2 validated the store against both ground truths, guarded its
shared vocabulary, and made it viewable from the CLI: Tasks A-E, G per
`docs/sprints/SPRINT_2_PLAN.md` (Task F replaced mid-sprint, see below).
Full detail: `docs/sprints/SPRINT_2_SUMMARY.md`,
`docs/sprints/SPRINT_2_RETROSPECTIVE.md`, and the PR #11 commit history.
This entry summarizes rather than restates those numbers.

- **fix**: re-derived every seed-set paper's real applicability from its
  actual PDF content (Task A), correcting a Sprint 1 undercount where
  most papers carried only their single primary context despite
  ADR-0005 defining applicability as a separate plural field
- **feat**: extracted and validated the first real HSBC-submission
  assertions (Task B) -- the B1 variable-count case from the consumer
  repository's own preregistration amendments, with a `contradicts`
  relation between the corrected and the documented-wrong value
- **fix**: spot-checked store content against the 44 source PDFs
  directly (Task C); resolved seed-directory drift (a book relocated to
  the non-repo Books directory, the QBoost paper added, both confirmed
  intentional) and added the QBoost paper with a real citation
- **test**: guard for ADR-0004/ADR-0005 vocabulary agreement (Task D,
  F76), verified by injection
- **docs**: both ADRs' 20-paper checkpoints walked against the real
  store and recorded as dated amendments (Task E, F75; ADR-0004
  Amendment A4, ADR-0005 Amendment A1), later corrected for two
  internally-inconsistent counts found by code review and given
  explicit point-in-time qualifiers so a snapshot count is not read as
  a durable fact in a document that does not permit edits in place
- **feat**: `scripts/view.py` (Task G, F3) -- contexts / paper /
  assertion modes, plain text or `--json`, no server. Found and fixed a
  Windows console encoding defect (cp1252 crash on non-ASCII `--json`
  output) during build, verified by injection
- **process**: Task F (team-lead adjudication timing) REPLACED by F7-F11
  (Class 3 scope change) -- four model-tier adversarial review cards
  (Haiku, Sonnet, Opus, Fable) plus F11, the original measurement,
  sequenced to run after F7-F10 against the same record set
- **chore**: hook enforcing the AskUserQuestion ban
  (`.claude/hooks/block_ask_user_question.py`), added after the rule
  was violated twice in one session despite being fully documented
  beforehand; a mechanical `gh issue list` check added to Phase 5
  after two issues stayed open despite `Closes #N` commit messages on
  a feature branch; a data-precondition check added to
  `SPRINT_PLANNING.md`'s estimation guidance
- **process**: Sprint 2 retrospective run (16 categories x 4 roles, all
  "Very Good"); F7-F14 added to the backlog for future sprint selection
