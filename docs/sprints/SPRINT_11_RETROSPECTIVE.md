# Sprint 11 Retrospective: Enter QCi's Answers, Then Read 200 Records and Every New Paper

**Date**: 2026-10-22. **PR**: #113. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete". It carried this note, new in this sprint's prompt:

> Note: The overall goals of the Retrospective is for the entire team (Coding Agents and Non-Coding agents) to be long-term (many sprints) more effective while as efficient as reasonably possible in the context of long-term support of the repository and keeping in mind the Architecture, Software Engineering, Security, DevOps, Six Sigma (heavily weighting improvement that can prevent any current and future issues instead of responding to them), Agile standards and best practices.  To accomplish this we must base what we do on facts supported by references, honesty, objectivity while treating each other in a "tactfully honest way" (as opposed to "brutally honest").

## Sprint 11 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All 7 tasks met their acceptance criteria. Rework before hand-over: Tasks F and G were applied twice, because the first apply ran without `require_edit_basis` (intake section 31) and with the figure check only printed. The full suite and the fresh-eyes review caught it: 7 values still past their quotes and 3 measured results at HIGH (5 moved to LOW in all). Task C's first apply linked a `supports` that failed ADR-0004 A8(b); withdrawn by name. Rework after Manual Validation was small: the Q1 link, the computed list (Q2, Q3) and its skill.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard was proven to fail by injection (1,131 tests at hand-over, 1,134 after Manual Validation). Three gaps were found by tests or review, not prevented by design: the quote pattern skipped a quote with no space after ";", so `require_verbatim` passed it unchecked (caught by the F93 number test); the F11 packet went stale when a G record moved to `read`; and the reading script edited values without the section 31 check, which `test_verified_writes.py` caught only at the full suite, after the first apply. The suite's 11.5 minutes (CI: 45 s without the store tests) is now F100.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimated 655 minutes. Plan approval (23:41) to the Manual Validation hand-over (02:42) took about 181 minutes of wall clock, about 28 percent, with up to 5 readers in parallel (Sprint 10: 53 percent; Sprint 9: 37 percent). Commit to commit (lower bounds, G overlapping the rest): A 19m, B 10m, C, D and E together 44m, F and G together 93m, hand-over 15m. Task G's 325m assumed serial reads; the ledger and 5 readers cut it most. Manual Validation added about 2 hours of decisions work and suite runs in no estimate.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan held. Two plan statements were wrong and disclosed: Task F's snapshot said 37 unlinked files (38; one counted with G), and the NVIDIA eval repository could not be linked by source (asked at Q1). The hand-download list had no owner until Q2.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 readers, one ledger group each, up to 5 at once, worked: after the prompt fix, groups g16 onward had 0 quote misses. The coordinator's own read, on the top tier, replaced 13 values; it was also the source of the HIGH grades the review corrected.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Changed commitments were disclosed in the next message and in the status note (37 vs 38 files, the unlinked repository, the second apply, Q3 done now rather than in Sprint 12). Two real failures: an interim message called the full suite passed before its output was read (it had 2 failures), and the Manual Validation question Q3 called many F62 papers `hsbc-2026` when the store files them under `ml`. Both corrected in the next message and the note.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: F57's order changed twice on 2026-10-21 (newest first, then back to relevance), both before planning. Q2's "ongoing list in relative priority order" needed an ordering rule the team lead did not state; I chose one, stated it in intake sections 39 and 40, and the follow-up request (file names, reasons, a skill) refined it.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Intake sections 32 to 40; a dated amendment to the ceilings answer document (F93); BACKLOG_REFINEMENT.md's adopted, adapted and declined list (F94). Section 39's first draft hand-counted 17 records; the resolver returned 16. The computed-not-stored rule caught its own author.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The code-edit hook blocked a JSON-only edit because the same command ran pytest on a test file, and a JSON heredoc whose prose named script files; split into separate calls. Parallel readers shared one scratchpad and one overwrote another's temp files; the reader prompt now names a per-group folder. Reader stray files landed in the repository root and were moved out. A full suite ran while an injection was live; it was stopped and re-run clean, which cost 11 minutes.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: arXiv traffic stayed serial at 18 s. No paywall or TLS failure was worked around (Macaluso's host is on the list). No write crossed into a sibling repository. One precedent accepted knowingly: the first source link whose evidence is a decision, not a source sentence (Q1 = 2), with the evidence saying so.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ready. F98 (Christophe Pere's list) and F100 (faster suite) are carded; F95 names the next repository (wangy8205165/Quantum-NeuralNetwork-WhitePaper); F57 count 1,840 unread; 38 papers on the hand-download list.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No ADR amended. The write-path checks this sprint needed (edit basis, figures, quote parse) live partly in `store.quotes` and partly in one script's `verify()`; that split is how the first apply missed them (proposal I1).

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] Fix Pande 2020's citation, which carries "&amp;" from Crossref -- target: Sprint 12 plan, est: 10m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond F100, already carded at the team lead's request.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: High. Readers' first-pass quotes were mostly exact; misses were typed dashes and minus signs (11 corrected). Their main defect was saying more than the quote (13 values replaced).

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none (Q3 was answered: 1).

## Improvement Decisions

Proposed 2026-10-22, prevention first, extending an existing prevention
where one is connected. Awaiting the team lead's disposition.

| # | Improvement | Type | Disposition | Commit |
|---|---|---|---|---|
| I1 | The write path itself refuses what Sprint 11's `verify()` refuses: a quote that does not parse, a value changed from the reader's without `require_edit_basis`, and a figure not in the assertion's own quotes | Prevention (extends Sprint 10 I1 and I2: `store.quotes`, `insert_verified_assertion`) | pending | |
| I2 | A suite runner that reports one verdict line from the exit code, records it with the commit, and marks the run invalid if the working tree changed during it | Prevention (extends the commit-gate hook; folds into F100) | pending | |
| I3 | HIGH needs a stated basis per id (setup, scope, definition, proved result); a test refuses HIGH for a measured result | Prevention (extends HIGH_REVIEWED and its test) | pending | |
| I4 | The code-edit check in `block_unraw_escape.py` (Sprint 8 I5) judges each command segment on its own and ignores text inside a search pattern, so a JSON edit beside a pytest call, or a read-only `grep` whose pattern contains "sed -i" (blocked 2026-10-22 while drafting this retrospective), is not blocked | Prevention of false blocks (extends the Sprint 8 I5 check) | pending | |
| I5 | A section written before its apply takes every count from the dry run's printed line, never by hand | Prevention (extends intake rule 26's order: section, then apply) | pending | |
