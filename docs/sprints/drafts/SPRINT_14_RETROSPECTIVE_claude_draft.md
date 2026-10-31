# Sprint 14 Retrospective: Claude's draft (Development Team)

Drafted 2026-10-31 while the team lead writes the PO, SM and LD feedback.
Counts are a snapshot as of 2026-10-31.

### 1. Effective while as Efficient as Reasonably Possible

All seven tasks (A to G) delivered, and all 72 F114 groups are in the
store. Rework was heavy: the F114 apply ran four times (b185729 entered
10 refused papers and was restored; 4d969d9 re-applied; a notes-only
re-apply for 6 wrong refusal notes; the 2026-10-31 apply and its
context-fix re-apply). Each rework was caught by a review or the suite,
not by the team lead, but each cost a backup, a trial and a suite run.
The common cause: the applier trusted reader fields (context, why_not)
that no review had decided.

### 2. Testing Approach

The live-store suite caught the context defect that every earlier check
missed (F65's "every Dirac-3 assertion is classed" test). Every new
guard was proven red by injection. Gap: the trial apply on a copy only
checked "a second apply writes nothing"; it did not compare the copy
against the pre-apply backup for fields no review decided. A field diff
after the trial would have caught the context change before the live
apply.

### 3. Effort Accuracy

Not yet measured; the Actuals go in SPRINT_14_SUMMARY.md from the
commit and task logs. Expected pattern, as in Sprints 12 and 13: the
coordinator time ran far over the plan for E and F because of the four
applies and the five-round page-fixer chain; A to D ran near or under.
Full-suite runs grew from about 8 to 25 minutes as the store grew.

### 4. Planning Quality

The plan sized the review well (Sonnet per group, Opus sign-off, team
lead for certainty changes). It did not foresee two classes of
decision the reader fields carry: whether a refused paper re-enters
(found at the review of b185729) and whether a stored context may
change (found by the suite). Both are now guards.

### 5. Model Assignments

Sonnet 5.5 reviewers per group were sound; the Opus cross-group pass
caught 86 inconsistencies and its rule held. Fresh-eyes reviewers after
each store commit found real defects every time (10 refused papers, 6
notes, 3 memo overstatements). The page-fixer review chain ran five
rounds for diminishing returns (F126).

### 6. Communication

The Manual Validation hand-over carried every question, option and
disclosure in full. Weak point: a status request ended a turn with a
"how should I continue?" question; the team lead has since said a
status request never pauses work (memory saved).

### 7. Requirements Clarity

The scope was clear. The hidden requirement was that a refused or
off-topic paper is the team lead's decision, not a reader's; it was
surfaced at review and asked as MV Q2.

### 8. Documentation

INTAKE 58 holds four dated corrections. One INTAKE-first slip
(2026-10-30, the notes re-apply ran before its section was written);
on 2026-10-31 every correction was written before its apply. The F118
memo needed three corrections after review before hand-over.

### 9. Process Issues

- Finalize reads stored grades from the live store, so it cannot be
  re-run after an apply without pointing it at the pre-apply backup;
  two untracked review files were deleted before this was found and
  were regenerated.
- The applier's dry run refuses items one at a time, so 5 sign-off
  fixes took 5 dry runs.
- A British spelling inside an assertion id failed the suite in INTAKE.

### 10. Risk Management

Every store write had a verified backup and a trial on a copy, and the
restore of b185729 worked as designed. The risk not managed was a
field changed without a decision; the guard now covers context, but
the class (any field the review does not grade) is wider.

### 11. Next Sprint Readiness

Carried: F125 (8 unread F114 records), F126 (page-fixer leftovers, the
muta anchor), F127 (QCI Dirac guard over-strict), F128 (gap reading and
split candidates), F129 (LOW grades resting on a textbook fact). The
F118 memo's Phase 2 prompt waits for the team lead to paste it.

### 12. Architecture Maintenance

No ADR amendment this sprint. The applier grew three guards (reenter,
refusal_reason, stored context); `scripts/sprint13_g_reading.py` is now
the main intake path for full reads and carries a Sprint 13 name.

### 13. Minor Function Updates for the Next Sprint Plan

- Trial apply compares the copy with the pre-apply backup and lists
  every field changed on a stored record that no review item names.
- Finalize takes an explicit store path (or refuses after an apply) so
  a re-finalize never reads post-apply grades.
- The dry run reports every refusal at once, not the first.

### 14. Function Updates for the Future Backlog

- Rename or wrap the full-read applier under a name that is not
  Sprint 13's.
- Suite time: live-store tests that each re-run the whole apply
  (3 to 10 minutes each) could share one applied copy.

### 15. Assigned Coding Agents Quality

Reviewers returned grounded findings with record ids and page
evidence. One reviewer (g113) ran about 9 hours of wall time; its
findings were used, but its late notice arrived after hand-over.

### 16. Questions to be discussed before ending the sprint

None from the Development Team.
