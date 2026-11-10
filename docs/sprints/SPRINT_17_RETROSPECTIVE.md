# Sprint 17 Retrospective: Test Faster, Then Read on the API Credit

**Date**: 2026-11-10. **PR**: #174. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). Counts are a snapshot
as of the date each names.

## Sprint 17 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All six tasks (A to F) delivered, and every Manual Validation decision built: q20, q23, q24, q28, q29 = b and q31. Rework, in order of cost: the second working folder (`EvidenceBasedDB-sprint17`), created without asking, cost two merges, a CHANGELOG conflict and a re-run of every Manual Validation step in one folder (q24); the q23 correction script appended its quotes on every apply, so its second apply wrote duplicates into 4 records and a third apply repaired them; the Defender walkthrough was written before checking which scanner was active (Norton 360 was).

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: F140 changed the suite most: about 69 minutes at Sprint 16's last run, now 7 to 11 minutes for the full suite on 16 workers and 6 to 10 for a targeted gate. Every new guard was proven red by injection. The gates caught a missing inventory row twice and the applier re-checking rows the team lead had corrected (q23). One defect reached the store first: the q23 double append. A test that ran the plan twice before the first apply would have caught it, and the q20 and q29 scripts then had one from the start.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Tasks A to F ran from 13:04 on 2026-11-07 to 02:00 on 2026-11-08, about 780 minutes, against about 625 at the cards' estimates (1.25 times; Sprint 16 was 1.7). Manual Validation follow-up, unplanned by nature, ran across 2026-11-08 to 2026-11-10 and was dominated by the folder merge (q24), q23, q20 and their reviews.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The order the team lead set (F144 first, then F140) worked: the pilot's cost and flag rates were known before F140 and E started. The plan did not say where F144's branch would be worked; I chose a second folder without asking, and nothing in the plan or the rules stopped it.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 readers and reviewers for Task E's 10 papers; Sonnet 5.5 on the Batch API for 13 papers ($3.00 of the $95 cap, 2026-11-07). Fresh-eyes general-purpose reviewers found real defects each time: Albash's unquoted passages (q23, H1), the silent skip in the applier, and the moved q20 papers that no reader would offer.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every dropped or changed commitment was disclosed in the next message (the Task E prompt paths, the 158 count, the Defender steps). Three questions carried my errors: q20's count (158, not 161); q30's option b, which promised a LOW reason the grading code does not allow; and decision dates recorded as 2026-11-08 that the session log shows were 2026-11-09. One footer was typed by hand; the Stop hook caught it.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The team lead sharpened two definitions that now bind every question: prevention against control (q11), and effort as build cost plus run cost and how often (q13). q14 ("read the whole paper") and q19 (replaced by q28, a better prompt rather than a repair round) changed my proposals, not the requirements.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: INTAKE sections 75 to 77, `docs/F140_TESTING_ANALYSIS.md` and `docs/F143_READING_COST.md` were written with the work, and every commit changed the CHANGELOG. Snapshot dates were stated on every count. Seven decision dates had to be corrected after the fact (7270922).

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The second folder was the largest: git cannot check out one branch in two folders, so the main folder could not switch until the worktree was removed, and the footer read the wrong folder's status. The hooks worked as controls: a Python rewrite of a `.py` file, a `$()` in a python command, pending CI at hand-over, and a stale footer were each blocked.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The credit's expiry (2026-11-18) was the named risk: F144 was built and measured first, and F146 is carded at Priority 10 for Sprint 18. Every store write took a verified backup first, and every correction script ran dry by default. A re-run of an older script cannot undo a later decision (`decided_day`), which held in practice when the q23 script was re-run after q29 and q31.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ready: F146 (agreement map, HIGH audit) at Priority 10 with 8 days of credit left at the cut; the 161 one-paper groups with briefs; the quotes-first reader rule; F145, F147, F148 carded. Tight: F146 must send before 2026-11-18.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No ADR amendment this sprint. The grading vocabulary held: q31 kept the fixed LOW reasons instead of a one-off text. The read ledger gained a `superseded` note without breaking "one record, one group". The store holds 37,408 assertions and 11,754 HIGH (2026-11-10).

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] `scripts/sprint13_g_ledger.py` names a new group from `len(groups)`; one gap or deletion in the ledger would reuse a name. Use the highest number plus one, as `batch_read.next_group` does -- target: Sprint 18 plan, est: 15m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond the cards already added this sprint (F146, F147, F148).

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Task E's readers needed 8 corrections after review (q23), none of them a lost paper or page. The batch readers' replies were all flagged, at 16.6 check problems per 100 assertions after the self-check (71 in 428, 2026-11-07), most a number not in its quotes; q28's rule is the response. The reviewers' reports were accurate when checked, with one miscount (5 papers listed as 6) that a store query settled.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None.

## Improvement Decisions

Team lead, 2026-11-10: "i1. a i2. b i3. b i4. a".

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| i1 | No new working folder or worktree without asking | Dev Team, categories 1, 4 and 9 | Hook + rule | 30m | Now (a): `.claude/hooks/block_worktree_add.py` on the shell and EnterWorktree tools, `tests/test_block_worktree_add.py` (proven red), a CLAUDE.md line |
| i2 | A script that adds to stored text is tested for a second run before its first apply | Dev Team, categories 1 and 2 | Process | 5m | Now (b): a Phase 4 line in `docs/SPRINT_EXECUTION_WORKFLOW.md`, not enforced |
| i3 | Every option in a question checked against the code and data before it is asked | Dev Team, category 6 | Process | 10m | Skip, tracked (b): two cases this sprint (q20's count, q30's option b); a third brings it back |
| i4 | A decision's date read from the clock when the answer arrives | Dev Team, categories 6 and 8 | Process | 10m | Now (a): a Phase 5 line in `docs/SPRINT_EXECUTION_WORKFLOW.md` |

Category 13's item (the ledger script names a new group from `len(groups)`; 15m) is carded as F149 for the Sprint 18
plan.
