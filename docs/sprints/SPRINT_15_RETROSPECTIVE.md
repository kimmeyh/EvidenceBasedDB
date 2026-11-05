# Sprint 15 Retrospective: Read Every Page, Figures and Images Included, Then Read 100 More Papers

**Date**: 2026-11-05. **PR**: #149. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). Counts are a snapshot
as of 2026-11-05.

## Sprint 15 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All 13 tasks (A to M) delivered. All 47 Sprint 15 groups are in the store, read whole with figures and OCR pages, and every Manual Validation decision is applied. Three costs were avoidable. The first trial apply copied the store without its text cache, so it re-extracted 894 PDFs (about 25 minutes). The applier checks the quotes of every group on each run, about 23 minutes for 47 groups, when it writes only a few; the team lead named this a breach of the primary rule, and it is carded as F136. And I ran the full suite more often than the work needed, until the team lead stopped it.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard was proven red by injection, including the three applier fixes at Manual Validation. The trial apply on a store copy found all 9 refusals and the 8 undecided fields before the live store was touched. One gap: the second half of the figure-exemption test called the applier on a path that never reached the edit check, so it could not fail. The fresh-eyes review found it; that half now calls the check directly. The full suite's three older failures (F46, F80 and a British-spelled id) were real conflicts with Sprint 15's full reads, not flakes.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: A to C ran at or under their estimates. H and I carried no estimate as a limit (no reading budget); the reads took most of 2026-11-01 to 2026-11-04 in the background. The coordinator time went mostly to review rework: two readers sent back for skimming (g146, g149), Dawid's book review sent back to read every passage, and the Manual Validation applies. The measured actuals are in SPRINT_15_SUMMARY.md.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Running F115 and F116 before the reads (Q1) worked: the 100 papers were read with their figures and image pages. The plan did not foresee that Task I could only take ledger records (no unread record outside the ledger had a local copy), nor that H and I could not be applied apart. Both were disclosed as changed commitments (9 and 10). Thirteen changed commitments in one sprint is a high count; most came from facts found during the reads, not from planning errors.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 readers and reviewers, with the Opus 5.5 sign-off and cross-group pass, held. One reader was first launched on Opus 5.5 by an omission and relaunched on Sonnet within minutes (changed commitment 6). The fresh-eyes reviewer on Opus found the one real gap at Manual Validation: the team lead's grades were protected by a date alone.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Each changed commitment was disclosed in the next message and in the status note. One slip: commit d485069's title said the 100 papers were applied when only 23 of the 47 groups were; it was corrected in ca13887 and in the CHANGELOG. My first answer on the slow trial apply explained the mechanism before the cause; the team lead had to ask why anything was read at all.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The Q3 OCR grading rule, with the team lead's qualification, was clear and was applied as recorded. Two requirements surfaced late and were settled by the team lead: a decision already checked is not checked again (F136), and the full suite is not re-run without a reason.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Intake sections 60 to 67 record each apply with its counts and dates. Each INTAKE section was written before its store apply. F136 and F137 were carded with the team lead's words.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Three tooling slips. The trial store copy needed the text cache copied by hand, and the first trial missed it. The Manual Validation script was first dated 2026-11-04, the review day, so a rerun of the applier would have reverted g144's decisions; the store was restored from its verified backup and the script re-run dated 2026-11-05. A Phase 2 test session ran on the same machine during the last `--changed` run, which took 79 minutes; its 5 failures were 1 real defect (above) and 4 tests pinned to data the decisions changed.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan's risks held: no write reached a sibling repository, one writer at a time, and a verified backup before each store write. One risk not in the plan materialized: a team-lead decision could be undone by a later review or by a rerun of an older script (the `--changed` run found the second: sprint12_reading.py would have moved one context back). Both are now guarded: the applier's TEAM_LEAD_GRADE rule and `sync_assertion`'s `decided_day` refusal, each proven red. The F130 wait on Phase 2's PR #74 was handled by Q4 and the team lead's Q1 = 3.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ready. F136 (Priority 12) makes the next apply take seconds, not minutes; F137 holds the Dunjko records; Sprint 16's F57 release follows F57's ranking (Q7 = 2).

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No schema or ADR change. OCR text is held outside git in the text cache with its engine, version and model files in provenance, as ADR-0005 section 3 requires. The team lead's grade is a stored fact the applier now reads, not a date it infers.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [DEV] A trial store copy always takes the text cache with it, or refuses -- target: Sprint 16 plan, est: 20m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none (F136 and F137 were carded during the sprint).

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Most readers read whole on the first pass. Two did not: g146 used a subagent and skimmed reference pages, and g149 skimmed references and used an override token in its scratch. Both were sent back and fixed, and reviewer prompts now forbid subagents. Dawid's book reviewer decided about 199 items from quotes alone and was sent back to read every passage (13 HIGH to LOW).

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | A trial store copy always takes the text cache with it, or refuses (Q1) | Dev Team, categories 1 and 9 | Tooling | 20m | Replaced 2026-11-05 by the team lead's rule (each PDF's text extracted once, ever; each quote checked once, ever), carded in F136 (one fixed text cache every store copy reads); team lead Q1 = 1: backlog, Sprint 16's first task (about 50m) |
