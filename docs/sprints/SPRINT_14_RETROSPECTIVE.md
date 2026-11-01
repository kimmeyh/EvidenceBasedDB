# Sprint 14 Retrospective: Read PHI-OMEGA, Review the 302 Cloud Reads, Then Learn What the Store Says

**Date**: 2026-10-31. **PR**: #140. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete". Counts are a snapshot as of 2026-10-31.

## Sprint 14 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All seven tasks (A to G) delivered, and all 72 F114 groups are in the store. Rework was heavy: the F114 apply ran six times (b185729 entered 10 refused papers and was restored; 4d969d9 re-applied; a notes-only re-apply for 6 wrong refusal notes; the 2026-10-31 apply, its context-fix re-apply, and two re-applies for the reviews of 0eddd23 and bb82d0a). Each rework was caught by a review or the suite, not by the team lead, but each cost a backup, a trial and a suite run. The common cause: the applier trusted reader fields (context, why_not) that no review had decided, and I edited settlement text by pattern instead of by hand.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The live-store suite caught the context defect that every earlier check missed (F65's "every Dirac-3 assertion is classed" test). Every new guard was proven red by injection. Two gaps: the trial apply on a copy checked only that a second apply writes nothing, not which fields changed on stored records that no review item named; and a guard proven red once turned vacuous after a data change (the context test passed with no check once the sign-off named its own ids in `context_fix`, found by the review of 0eddd23).

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Tasks A to D ran near or under their estimates. E and F ran far over in coordinator time, because of the six applies and the five-round page-fixer review chain; F carried no estimate as a limit (no reading budget). The measured actuals go in SPRINT_14_SUMMARY.md. Full-suite runs grew from about 8 to about 23 minutes as the store grew.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan sized the review well (Sonnet per group, Opus sign-off, the team lead for certainty changes). It did not foresee two decisions hidden in reader fields: whether a refused paper re-enters (found at the review of b185729) and whether a stored context may change (found by the suite). Both are now guards.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 reviewers per group were sound; the Opus cross-group pass found 86 inconsistencies and its rule held. Fresh-eyes reviewers after each store commit found real defects every time (10 refused papers entered, 6 wrong notes, 3 memo overstatements, a vacuous test, false settlement reasons). The page-fixer review chain ran five rounds for diminishing returns (F126).

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The Manual Validation hand-over carried every question, option and disclosure in full. Weak point: a status request ended a turn with a "how should I continue?" question; the team lead has since said a status request never pauses work (memory saved).

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The scope was clear. The hidden requirement was that a refused or off-topic paper is the team lead's decision, not a reader's; it was surfaced at review and asked as Manual Validation Q2.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: INTAKE 58 holds six dated corrections. One INTAKE-first slip (2026-10-30, the notes re-apply ran before its section was written); on 2026-10-31 every correction was written before its apply. The F118 memo needed three corrections after review before hand-over, and INTAKE 58 stated two counts wrongly (corrected by dated addition).

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Finalize reads stored grades from the live store, so it cannot be re-run after an apply without pointing it at the pre-apply backup; two untracked review files were deleted before this was found and were regenerated. The applier's dry run refuses items one at a time, so 5 sign-off fixes took 5 dry runs. A British spelling inside an assertion id failed the suite in INTAKE.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every store write had a verified backup and a trial on a copy, and the restore of b185729 worked as designed. The risk not managed was a field changed without a decision; the guard now covers context, but the class (any field the review does not grade) is wider.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Carried: F125 (8 unread F114 records), F126 (page-fixer leftovers, the muta anchor), F127 (the QCI Dirac guard is over-strict), F128 (gap reading and split candidates), F129 (LOW grades resting on a textbook fact). The F118 memo's Phase 2 prompt waits for the team lead to paste it into a Phase 2 session.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No ADR amendment this sprint. The applier grew three guards (reenter, refusal_reason, stored context); `scripts/sprint13_g_reading.py` is now the main intake path for full reads and still carries a Sprint 13 name. (Note, 2026-10-31, after Q5 = 1: renamed `scripts/full_read_apply.py` in 7b2179f.)

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [DEV] The trial apply lists every field it changed on a stored record that no review item names -- target: Sprint 15 plan, est: 45m. [DEV] Finalize takes an explicit store path, or refuses once its group is applied -- target: Sprint 15 plan, est: 30m. [DEV] The dry run reports every refusal at once -- target: Sprint 15 plan, est: 30m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [DEV] Name the full-read applier for what it is, not for Sprint 13 -- estimated: 60m, priority: 60, depends on: none. [DEV] Live-store tests that each re-run the whole apply share one applied copy, to cut the suite time -- estimated: 120m, priority: 50, depends on: none.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Reviewers returned grounded findings with record ids and page evidence. One reviewer (g113) ran about 9 hours of wall time; its findings were used, but its late notice arrived after the hand-over. One reviewer's run was flagged by the harness for a permission-mode bypass; a check found no write to the repository or the store.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | Edit settlement or review text by hand, never by pattern (Q1) | Dev Team, category 1 | Process | 10m | Now (Q1 = 1) |
| 2 | Trial apply lists fields changed on stored records that no review item names (Q2) | Dev Team, categories 2 and 10 | Guard | 45m | Now (Q2 = 1) |
| 3 | Finalize takes an explicit store path, or refuses once its group is applied (Q3) | Dev Team, category 9 | Tooling | 30m | Now (Q3 = 1) |
| 4 | The dry run reports every refusal at once (Q4) | Dev Team, category 9 | Tooling | 30m | Now (Q4 = 1) |
| 5 | Rename the full-read applier (Q5) | Dev Team, category 12 | Refactor | 60m | Now (Q5 = 1) |
| 6 | Share one applied store copy among the live-store apply tests (Q6) | Dev Team, category 14 | Test speed | 120m | Now (Q6 = 1) |
| 7 | One period, not two, before "NOT upgraded" in 900 stored reasons (Q7; INTAKE section 59) | Fresh-eyes review of 25d3985 | Store fix | 60m | Now (Q7 = 1) |
| 8 | Phase 2's Sprint 30 results into the store after Sprint 30 merges (Q8) | F118 memo | Intake | 60m | Carded for Sprint 15 as F130 (Q8 = 1) |
| 9 | Three new reading gaps: production-scale timing, QRAM cost, fault-tolerant estimates (Q9) | F118 memo | Backlog | 10m | Added to F128 now (Q9 = 1) |

Team lead, 2026-10-31: "q1. 1 q2. 1 q3. 1 q4. 1 q5. 1 q6. 1 q7. 1 q8. 1
q9. 1". Each question was asked on its own, with detail, the alternative
considered and a recommendation. Option 1 was "Now" for Q1 to Q7, "Card it
for Sprint 15" for Q8 and "Add them to F128 now" for Q9. Claude's
recommendations differed on Q2 to Q8; the team lead chose option 1 for
every question, so Q2 to Q7 are done in this sprint.
