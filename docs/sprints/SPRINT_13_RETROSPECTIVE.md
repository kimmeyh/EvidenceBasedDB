# Sprint 13 Retrospective: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records

**Date**: 2026-10-28. **PR**: #131. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete". Counts are a snapshot as of 2026-10-28.

## Sprint 13 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Tasks A to F met their acceptance criteria by the first hand-over (2026-10-25 07:12). Task G (F113), added at Manual Validation, read 210 records whole in groups g001 to g042 and applied them; groups g043 on went to the F114 cloud readers, which stopped at $0 credit with 302 results fetched and not yet reviewed (F117, Sprint 14). Rework after the apply: two store defects (the sync's one-column writes, eb3941a; Task G's apply rewriting 114 Task F read rows, 5e10948), then the extent change of Manual Validation Q7 (2bab87b). Most of the F114 launcher's 11 fix commits came from launching it, not from planning it.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard was proven red by injection. The full suite found the Task F overwrite after the apply (6 failures); `--changed` had not, because it ran before the store write that caused it. The trial apply's log showed 114 "update read" lines, and nobody, me included, asked why a first apply updated rows. A trial log needs a check, not only a read: an apply of new reads that logs an update is a stop.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Tasks A to F were estimated at about 1,490 minutes; plan approval (2026-10-25 00:47) to the first hand-over (07:12) was 385 minutes of wall clock, with reader time in the background (about 26 percent; Sprint 12: 24 percent). Task G carried no estimate as a limit (no reading budget); its forecast of 20 to 40 hours of reader time for 1,991 records was not tested, since 210 were read locally and 302 in the cloud before the pause and the credit stop.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan for A to F held. Task G entered at Manual Validation without a plan of its own for how its read rows share a day with Task F's; the key collision (reader, day, extent) was a planning gap that a pre-flight query would have shown: 57 of its records had Task F rows dated 2026-10-25.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 readers did the first pass, with every quote checked in the write path and the coordinator at the top tier; the fresh-eyes reviewers found real defects in most code commits (Task G: 4 review cycles, each with a finding). F117 now splits the review by protocol across Haiku 5.5, Sonnet 5.5 and Opus 5.5; its evidence is still to come.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The Task F overwrite was disclosed at Manual Validation with its cause, its repair and the unquestioned trial log. Manual Validation ran to 13 questions over four days, because Task G and the PHI-OMEGA intake arrived inside it; each message re-presented every open question in full. The CHANGELOG lapse (below) was disclosed in the message that fixed it.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Two requirements surfaced mid-sprint: no reading budget (2026-10-25) and the read extent wording (Q7: `full` when the paper was read whole). Both are now in tests. "Process" in Q11 (later Q13) meant the coordinator's review of the cloud results; I echoed it with a time and a recommendation before acting.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: INTAKE section 53 records the apply, both defects and their repairs; its first counts were wrong twice (208 whole and 2 with exceptions, not 210; 306 read rows, not 153; 200 plus 8 for the slice), each caught by a fresh-eyes review. CHANGELOG lagged 19 commits from 2026-10-26 to 2026-10-28 and was caught up at close (71705d8); the same-commit policy slipped during the F114 launch, and `test_changelog_currency` did not see it because it checks only that the newest entry is within 5 days of the newest commit.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Seven older scripts still UPDATE read rows by key alone (sprint9_f78:527, sprint9_f80:387, sprint10_f83:208, sprint10_f84:214, sprint10_f89:358, sprint11:558, sprint12:1515); none runs again as written, but a re-run on a day another script wrote would repeat the Task F overwrite. Machine memory pressure gave 2 MemoryError failures that pass alone.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The pre-apply backup made the repair exact (a diff showed 0 rows missing). The risk that materialized was one script owning another's rows; the mitigation (ownership by wording, tested both ways) covers Task F and Task G only.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: F119 (PHI-OMEGA, Priority 10) is carded with its files in the library, all three images saved, and two references (Q12 = 1); F117 (the 302 cloud results) at 20, F118 at 22.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No ADR amendment this sprint. The `paper_reads` key (record, reader, day, extent, detail) allowed two scripts' rows to look alike; ownership is now by wording in the scripts, not in the schema. Worth a look at the F75 checkpoint.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] An apply's trial log that shows an "update" where only new rows are expected stops the apply, by a check in the apply script -- target: Sprint 14 plan, est: 30m. [Dev Team] The seven older scripts' key-only read-row UPDATEs scoped by their own detail, with a guard on every script -- target: Sprint 14 plan, est: 45m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] Read-row ownership in the schema (a writer column on `paper_reads`), so no script matches another's rows by wording -- estimated: 120m, priority: 40, depends on: F75 checkpoint.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The Sonnet 5.5 readers' quotes passed the write-path check; the coordinator replaced values where the meaning drifted. The fresh-eyes reviewers were the most productive agents of the sprint: each review of a store or script commit found at least one real problem. The F114 cloud readers produced 302 results; their quality is unknown until F117.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Improvement Decisions

Proposed 2026-10-28, prevention first. Team lead, 2026-10-28: "q1 1, q2 1,
q3 3 q4 1" (I1, I2 and I4 now; I3 skipped, against the recommendation to
backlog it).

| # | Improvement | Root cause | Type | Recommendation | Disposition |
|---|---|---|---|---|---|
| I1 | A trial apply that logs an update to a read row where the plan expects only new rows refuses the real apply until the update is named as intended | 114 "update read" lines in Task G's trial log were read and not questioned | Prevention | Now, 30m (F117 applies through this script in Sprint 14) | Now (2026-10-28): done; `commit_apply` rolls the apply back and names each rewrite unless `--update-reads` is given; test proven red |
| I2 | Every `UPDATE paper_reads` in `scripts/` scoped by the row's own detail; a test names any that matches by key alone (the 7 older scripts fixed) | The 7 older scripts carry the same key-only match that rewrote Task F's rows | Prevention | Now, 45m | Now (2026-10-28): done, narrowed rather than closed (review of c978e50); the seven UPDATEs name the stored detail, `tests/test_read_row_updates.py` reads parsed code in `scripts/` and `store/`; proven red. A row another script wrote under the same reader, day and extent can still be the one compared when this script's own row is missing; no such collision exists on those scripts' days (store query, 2026-10-28) |
| I3 | A writer column on `paper_reads`, so ownership is in the schema, not in wording | The table's key cannot tell two scripts' rows apart | Prevention (schema) | Backlog, priority 40, 120m, after the F75 checkpoint | Skip (2026-10-28) |
| I4 | `test_changelog_currency` names any sprint-branch commit whose short hash or subject no CHANGELOG entry covers | The test checks only that the newest entry is within 5 days of the newest commit, so 19 commits inside that window went unseen | Detection | Backlog, priority 40, 60m | Now (2026-10-28): done; `test_every_commit_has_its_changelog_entry` from 71705d8 on, proven red (it named db8aeb7 and af2c2ca before their entry); skips on CI's shallow clone, so it runs at the desk and in the full suite |
