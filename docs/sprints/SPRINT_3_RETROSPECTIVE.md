## Sprint 3 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Eight tasks shipped in dependency order; the four reviews ran genuinely in parallel as fresh subagents; the premise-falsifier check (an export diff before F7-F10 started) was performed explicitly rather than assumed. Wall clock from Phase 3.7 approval to the last task commit was 46 minutes (see SPRINT_3_SUMMARY.md, Actuals).

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not Very Good. Guard discipline caught three defects in the Development Team's own first attempts: a savepoint-naming bug (caught by the full suite), a vacuous exclusion test that checked a broken constant against itself (caught by injection), and the US English fixer rewriting frozen ADR amendments and sprint docs (caught by diff review before anything was staged). Every catch happened before commit, which is the process working; the number of first attempts that needed catching is the honest finding.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Every estimate was `[no-history]` for a third sprint. F10 alone consumed 150,290 subagent tokens and 599 seconds; F6 was the longest of Tasks A-D at 14 minutes. None of this was recorded in a form Sprint 4 could calibrate against until retrospective improvement 2 added the `## Actuals` section this sprint.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The two-part sequence, the explicit premise falsifier, and the corrected F9/F10 cards held through execution with no scope change.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good, with the sprint's most useful finding: on the same 18 records, F7 and F8 (per-record internal consistency protocols) confirmed 18/18; F9 and F10 (cross-record comparison and primary-source verification protocols) found 7 inconsistencies and 4 real citation defects. Review depth tracked the protocol at least as much as the tier. Recorded as F18's first `learning_log` entry and as a design input to F11 (improvement 4).

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The `block_ask_user_question.py` hook fired once and blocked the call -- the mechanism held where the documented rule alone had twice failed in Sprint 2. One end-of-turn status line was guessed rather than measured, one turn after the team lead set the rule, and the team lead caught it; the memory rule now requires a shell `date` call in the same turn.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The F9/F10 sequential-dependency design (drafted by the Development Team in Sprint 2) contradicted the team lead's independence requirement and was caught and corrected at planning, before it shaped execution.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Review results preserved in a dedicated document; F25 consolidated with reviewer order and dependency order kept as separate sections; every count dated per the point-in-time rule and re-verified against the store rather than copied from the reviews.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Two real issues: a write-shaped one-off script was run against the live tree with no dry-run mode (recovered because nothing was staged), and a fork's accurate completion report was briefly distrusted after a context compaction hid the turn in which its work had been committed. Both are now workflow rules (improvements 1 and 3).

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Both named falsifier conditions were checked, not merely stated: zero export changes across Tasks A-D, and each of F7-F10 confirmed to have made zero repo changes.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F15-F20 and F25 are carded with dependencies and the team-lead decisions listed up front; F11's sequencing against F25 is recorded as a recommendation rather than left open.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not Very Good. F10 showed that the Development Team's own Sprint 2 ADR-0005 Amendment A1 ("expected at their tier") excused the `screened`-tier contradiction rather than resolving it, and that Task B's triplication fix stopped one layer short of the store. Both are now F25 decisions, but the earlier amendment should have surfaced them.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond the four improvements below, all applied as commits in this sprint.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond F15-F20 and F25, already carded.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F10's primary-source verification was the highest-quality review output this repository has received; F7 behaved exactly as its card predicted; the Task A fork's survey was accurate on every claim later verified against the repository.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None from the Development Team side.

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | Write-shaped one-off scripts are dry-run by default; `--apply` required to write (`scripts/us_english_fix.py` refactored as the reference implementation, with tests) | Category 9 (Process Issues) | process/tooling | 20m | now |
| 2 | Every sprint summary carries an `## Actuals` section (wall clock per task from `git log`, subagent tokens/duration), starting with Sprint 3 | Category 3 (Effort Accuracy), third sprint running | process | 15m | now |
| 3 | A delegated task's report is verified against repository state before being trusted or dismissed (SPRINT_EXECUTION_WORKFLOW.md Phase 4) | Category 9 (Process Issues) | process | 10m | now |
| 4 | Review depth is a protocol property, not only a tier property; recorded as a design input on F11 and as F18's first `learning_log` entry | Category 5 (Model Assignments) | backlog design input | 10m | now (team lead upgraded from backlog) |

Team lead, 2026-09-19: "all 4 now."
