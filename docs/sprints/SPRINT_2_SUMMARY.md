# Sprint 2 Summary: Validate, Guard, and View the Store

Created 2026-09-18 per the three-doc rule (workflow 3.2.1), at the team
lead's request as part of Phase 7 rather than deferred to Sprint 3 kickoff.
Sourced from git history, PR #11, and `docs/sprints/SPRINT_2_RETROSPECTIVE.md`
-- never the master plan, which this document instead feeds.

**Dates**: 2026-09-17 to 2026-09-18 (no deadline; `SPRINT_2_PLAN.md`'s own
scope statement).
**Branch**: `feature/20260917_Sprint_2`, PR #11 (open, awaiting merge).
**Scope**: F4 (validate the store against the HSBC submission and the 44
source papers), F75 (action the 20-paper ADR checkpoint), F76 (guard the
shared ADR-0004/0005 vocabulary), F3 (CLI DB viewer). Task F, originally
"time team-lead adjudication directly," was REPLACED mid-sprint (Class 3
scope change, team lead 2026-09-17) by F7-F11, added to the backlog rather
than executed inside this sprint.

## What shipped

- **Task A** (F4 part 1): re-derived every seed-set paper's real
  applicability from its actual PDF content, correcting the undercount
  Sprint 1 left behind (44 of 45 papers had an empty `applicability` array
  despite ADR-0005 defining it as a plural field). Populated
  `paper_applicability` for all 44 seed-set papers; corrected 45 of 46
  after Task C's addition.
- **Task B** (F4 part 2): found the store held zero HSBC-derived
  assertions, so the plan's own "spot-check against HSBC's determinations"
  had nothing to check. Team lead decision: extract real assertions
  first, then validate them. Extracted the B1 variable-count case from
  ADR-0004's own motivating example (`hsbc-b1-variable-count`, corrected
  value 91; `hsbc-b1-variable-count-wrong-78`, the documented defect,
  `contradicts` relation between them) sourced from the consumer
  repository's `PREREGISTRATION.md` amendments A25/A30.
- **Task C** (F4 part 3): spot-checked store content against the 44 source
  PDFs directly. Found the seed directory had drifted since Sprint 1's
  snapshot (the Freericks book moved to `Books/`, correctly; the QBoost
  paper -- Neven et al. 2012 -- newly present, confirmed intentional and
  needed per F5's own backlog scope). Added the QBoost paper to the store
  with citation extracted from the real PDF, applicability `qml` + `qc`.
  Team lead directive: seed-directory additions happen continuously and
  are expected, not a drift alarm each time.
- **Task D** (F76): wrote `tests/test_adr_context_vocabulary.py`, guarding
  agreement between the ADRs' stated context lists and the database's
  actual contexts, verified by injection (a record naming an undefined
  context fails the guard).
- **Task E** (F75): walked both ADRs' six-question 20-paper checkpoint
  against real store statistics. ADR-0004 Amendment A4: units/rounding
  never filled (0 of 6), `evidence_tag` N/A for 53 of 54, no missing-field
  gap found, tiers landed as predicted (27/18/1), `supports`/`contradicts`
  each used once. ADR-0005 Amendment A1: `checked_against_source` 1 of 46,
  applicability 45 of 46 (corrected from an initial miscounted 44 of 46),
  yields 1 of 46. The sixth question on both ADRs (adjudication time)
  explicitly deferred to F11.
- **Task F, REPLACED**: the team-lead-timed adjudication measurement was
  not run this sprint. Replaced by F7-F10 (adversarial record-adjudication
  review, one card per model tier -- Haiku, Sonnet, Opus, Fable -- each
  designed for that model's own characteristics) plus F11 (the original
  measurement itself, sequenced to run AFTER F7-F10 so the comparison is
  apples-to-apples against the same record set).
- **Task G** (F3): built `scripts/view.py` -- three modes (`contexts`,
  `paper`, `assertion`), no server, `sqlite3`-backed, plain text or
  `--json`. Found and fixed a real defect during build/test: Windows
  consoles default to `cp1252`, which crashed on `--json` output
  containing non-ASCII citation text; fixed by reconfiguring stdout to
  UTF-8 at startup, verified by injection.

## Also delivered, outside the original six tasks

- **F12** added to the backlog: design a paper/reference intake workflow,
  raised by the team lead mid-sprint on finding three new items (a
  non-arXiv reference, an arXiv paper, a GitHub repo) with no standing
  process to bring them in.
- **F13** added to the backlog: guard US English spelling in this
  repository's own process/design docs, modeled on
  `hsbc-quantum-fraud-2026`'s `us_english_fix.py`/`test_us_english.py`
  pair (read-only source, ported and adapted here since this repository
  has no frozen-filing exemption the way the consumer repository does).
  `CLAUDE.md` now states explicitly that this repository is US English
  (previously undeclared).
- Three retrospective improvements applied as commits before this summary
  was written (see Retrospective outcome below), rather than only
  backlogged: a mechanical GitHub-issue-state check added to Phase 5, a
  hook (`block_ask_user_question.py`) enforcing the AskUserQuestion ban
  that had twice been violated this sprint, and a data-precondition check
  added to `SPRINT_PLANNING.md`'s Estimation section.

## Measurement Sprint 2 did NOT produce

**Team-lead adjudication time per record** -- ADR-0004's own named
constraint, deferred once already in Sprint 1. This sprint's Task F was
scoped to produce it directly and was replaced instead by F7-F11
(backlog), a disclosed Class 3 scope change rather than a silent miss.
F11 is sequenced to run after F7-F10 complete in a future sprint.

## Findings surfaced during execution, now backlogged

- **F7-F10**: adversarial record-adjudication review, one card per model
  tier (Haiku, Sonnet, Opus, Fable), each with review instructions and
  failure-mode framing specific to that model.
- **F11**: the team-lead adjudication-timing measurement itself, run after
  F7-F10 against the same record set they processed.
- **F12**: paper/reference intake workflow design (two-phase: design,
  then build).
- **F13**: US English spelling guard for this repository's own process
  docs, ported from the consumer repository's equivalent pair.

## Retrospective outcome

16 categories x 4 roles, all rated "Very Good" by the combined Product
Owner/Scrum Master/Lead Developer feedback. The Development Team draft
(Claude) agreed on outcome while naming two real process gaps underneath:
Communication (Category 6) and Process Issues (Category 9) both rated
"Good, not Very Good" on the Development Team's own account, since the
AskUserQuestion ban was violated twice in one session despite being fully
documented beforehand, and the `Closes #N` auto-close gap (issues #13,
#15) recurred despite already being a named defect class in
`SPRINT_EXECUTION_WORKFLOW.md`. Both gaps produced retrospective
improvements approved and applied immediately ("all 3 now," 2026-09-18):
a mechanical issue-state check in Phase 5, a hook enforcing the
AskUserQuestion ban rather than relying on memory alone, and a
data-precondition check in `SPRINT_PLANNING.md` for the third gap
(Task B's scope assumption). Full detail:
`docs/sprints/SPRINT_2_RETROSPECTIVE.md`.

## Verification

Full test suite: 136 passed, 1 skipped (pre-existing, unrelated to this
sprint). Verified by injection throughout: the vocabulary guard (Task D),
the view-tool relation resolution and UTF-8 fix (Task G), and the new
AskUserQuestion hook (retrospective improvement 2).
