# Sprint 6 Retrospective: Decide the Fields Once, Then Load at Scale

**Date**: 2026-10-05. **PR**: #54. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete".

## Sprint 6 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All twelve tasks shipped, and the store grew from 361 to 1,875 papers with every new field in place. Rework was real: the Task E review cycle, two back-fill re-runs (a provider regex misread "Crossref/DataCite"), three repository-linking re-runs after crashes, and a bulk load stopped and restarted twice. Most of that rework traces to one defect (the unpaced intake fetcher) that was found late.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Strong where it was applied: every new guard was proven to fail by injection, and two of my own tests were caught as vacuous during that step (the rollback test that passed with the rollback removed; the first F47 regex that flagged the very record F47 names). Weak where it was missing: no test exercised arXiv pacing ACROSS intake entries, so a Sprint 4 defect survived to Sprint 6 and broke the team lead's 6 s instruction once. Tests pinned the interval constant, not the behavior.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimate about 700 coordinator minutes plus Task J's runtime. Commits run from plan approval (0044a44, 2026-10-03 20:11) to the last Phase 5 fix (26f26d9, 2026-10-04 04:45): about 8.5 hours, of which about 4 hours were the two 2-hour arXiv pauses; Tasks A to C had been worked before their commit times, so true effort is somewhat higher than the span shows. Task J's runtime fell inside the planned 82 min to 10 h. The pattern from Sprints 4 and 5 held: coordinator estimates overstate work, and the external API sets the real duration.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The pre-flights paid off (F33's ids, the retraction notice, the F41 dry run). Two gaps: the plan sized Task F's computed fields for 347 records and did not say whether the 1,402 bulk records would be probed in the same sprint (now F52); and decision 4.1 assumed a missing `method` row that already existed.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Top tier for the ADR and the migration was right. The two fresh-eyes reviewers (code-reviewer subagent) found real defects both times: 4 in Task E, 7 in Phase 5, including two pacing gaps. No subagent was used for the Task F queue report; the queue turned out to be a one-line query.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: I reported the pacing defect plainly, including that my earlier explanation of the 429s was wrong. Misses: I closed the wrong issue once (#63 for #62, reopened at once), and Task H's commit subject carries the wrong number. Long background runs were reported by progress notes; the 10-minute burst that broke the 6 s rule was found from its runtime, not from a guard.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The team lead's arXiv instruction (6 s, pause 2 h, DataCite on failure) had one ambiguity, retries, which I asked as a numbered question before acting. The ADR text promised a Phase 1.3 probe run that was never planned; corrected before review, carded as F53.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: CHANGELOG kept current per task. Two slips: INTAKE_WORKFLOW section 16 was appended after its manifest ran (stated in the section), and ADR-0005 A4's probe rule claimed a mechanism that did not exist until corrected at Phase 5.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Hooks caught four real mistakes before they landed: a piped test gate, a Python rewrite of a .py file, an unescaped Windows path, and a sibling-repo path in a generator command (a false positive, worked around without the override token). The pacing defect is the process lesson: a rule enforced by a constant is not enforced unless the object that holds the clock is shared.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: "arXiv refuses a sustained run" was a named risk; the mitigation (serial traffic, DataCite fallback, per-entry commits) held, so nothing was lost. But the risk materialized partly because of our own defect, which the risk table did not consider.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Store at 1,875 papers, 60 assertions, export byte-identical. Cards F52-F57 are written; F52 (bulk probes) should run before anything else hits arXiv, under its cap.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Two ADR amendments accepted; the computed-versus-stored rule held in code (derived keys never written back, probe rows as dated measurements). `parse_access` needed two fixes (GitHub names containing arXiv ids; order).

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:
  - [DT] Record in the Sprint 6 summary that commits 39b179e and 32a6deb cite the wrong issue numbers (H is #62, G is #61) -- target: Sprint 7 plan, est: 5m
  - [DT] Add `2108.0131` (malformed in QMLPapers/2021/manifest.tsv) to F54's list with the full id read from the paper -- target: Sprint 7 plan, est: 15m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:
  - [DT] A behavior test for every external-API pacer: count real waits across a multi-record run, not the constant -- estimated: 1h, priority: 30, depends on: none

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Both review agents were accurate: every finding I checked was real, file and line exact, and the severity calls held. One Phase 5 finding (the HEAD bypassing the pacer) was in code I had written hours earlier, after the first review.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Improvement Decisions

Team lead, 2026-10-05: "all now". Every improvement prevents its problem at the source first, and extends an existing mechanism where one exists.

- **I1. One arXiv clock per process** (now): the pacing clock moves from each `PacedFetcher` instance to module level in `store/citations.py`, so a new pacer can never start at zero (the defect class behind the 2026-10-03 429s). Control: a test that a second, separate pacer waits.
- **I2. Intake refuses a manifest that no intake section names** (now): `intake.py --manifest <file in manifests/> --apply` refuses unless `docs/INTAKE_WORKFLOW.md` names the file, so the section is written first.
- **I3. Issue numbers resolved from the task letter** (now): the task-to-issue map is stored as named pairs in `.claude/sprint_status.json`; `scripts/close_task_issue.py <letter>` closes the right issue; a hook blocks a commit subject "Task X (#N)" whose N does not match X.
- **I4. Phase 5 re-reads each new amendment against the code** (now): extends the Phase 5 acceptance walk in `docs/SPRINT_EXECUTION_WORKFLOW.md`.
- **I5. Bulk loads state their derived fields at planning** (now): extends the capability pre-flight in `docs/SPRINT_PLANNING.md`.
- **I6. Retire the per-script pacer workarounds** (now, with I1): one way to pace.
