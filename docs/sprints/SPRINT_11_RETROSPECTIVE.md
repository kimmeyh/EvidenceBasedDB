# Sprint 11 Retrospective: Enter QCi's Answers, Then Read 200 Records and Every New Paper

**Date**: 2026-10-22. **PR**: #113. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete". It carried this note, new in this sprint's prompt:

> Note: The overall goals of the Retrospective is for the entire team (Coding Agents and Non-Coding agents) to be long-term (many sprints) more effective while as efficient as reasonably possible in the context of long-term support of the repository and keeping in mind the Architecture, Software Engineering, Security, DevOps, Six Sigma (heavily weighting improvement that can prevent any current and future issues instead of responding to them), Agile standards and best practices.  To accomplish this we must base what we do on facts supported by references, honesty, objectivity while treating each other in a "tactfully honest way" (as opposed to "brutally honest").

### Claude's feedback on the new wording (asked for: "Please be open with you feedback on the changes")

Given 2026-10-22 12:25 in chat; recorded here because it was asked for as
part of the retrospective.

- **What it adds that helps.** It states the goal as long-term, and it names
  security, which no earlier prompt did (no security finding arose this
  sprint). "Facts supported by references" matches how the Development
  Team section already works: each claim points at a commit, a test or an
  intake section. "Tactfully honest" sets a clear tone.
- **Repetition.** "Prevent rather than respond" now appears twice: in the
  Six Sigma parenthetical and in "Ensure that all improvement suggestions
  first attempt to prevent the problem from happening first". One copy is
  enough.
- **Name the Six Sigma practice.** If root-cause analysis is wanted (5
  Whys, or DMAIC's Control step), naming it lets each proposal carry a
  "Root cause" line. The proposals below carry one, as a trial.
- **Grammar.** "The overall goals ... is" reads better as "The overall goal
  ... is".
- **On "Very Good" in every category.** This sprint's Development Team
  section records real slips: a "suite passed" claim made before its
  output was read, a write-path check skipped at first apply, and a wrong
  context claim in a Manual Validation question. If "Very Good" means "the
  process caught them before the team lead did", one line saying so would
  make the record clearer for later sprints.

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
- **Claude Code Development Team**: [Dev Team] Fix Pande 2020's citation, which carries "&amp;" from Crossref -- target: Sprint 12 plan, est: 10m. [Dev Team] Correct `cyc-2007-eight-tactic-types`, whose quote stops at its inner `"split" (` so the rest was never checked (found by I1a, intake section 41) -- target: Sprint 12 plan, est: 15m.

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
where one is connected. Detailed for the team lead the same day ("need
more informaion on all the Improvements suggestions"); the closer look
changed two recommendations (I4 and I5, from now to skip). Team lead,
2026-10-23: "apply now: i1a, i1b, i2"; I2 moved from the recommended
backlog to now. I3, I4 and I5 were re-presented the same day and await
the team lead's disposition.

| # | Improvement | Root cause | Type | Recommendation | Disposition |
|---|---|---|---|---|---|
| I1a | `require_verbatim` also refuses a quote mark that does not parse, and, given the value, a figure the assertion's own quotes do not hold | The checks lived in one script's `verify()`, so any other script could skip them | Prevention (extends Sprint 10 I2: `store.quotes`) | Now, 40m | Now (2026-10-23): done; intake section 41. Found 2 stored quotes never fully checked: F92's (corrected) and a Sprint 7 Cyc quote (Sprint 12, section 13) |
| I1b | `backup_before_write`, which every `--apply` already calls, first runs the static write-path scan (`test_verified_writes.py`'s `script_problems`) on the calling script and refuses on a problem | The scan ran only with the full suite, after the apply | Prevention (extends the mandatory backup call) | Now, 30m | Now (2026-10-23): done; `store/write_path.py` |
| I2 | A suite runner: one verdict line from the exit code, recorded with the commit, invalid if the tree changed during the run; the commit hook reads it | The verdict was read by eye from scrolling output | Prevention (extends `block_commit_with_piped_tests.py`) | Backlog, folded into F100 | Now (2026-10-23, team lead): done; `scripts/run_suite.py`. The hook refuses a red or invalid verdict for the tree but does not require one; that rule stays F100's (card updated) |
| I3 | A shared grading helper: HIGH only with a named basis per id (setup, scope, definition, proved result, stated limit), required of new reading scripts by the same static scan | Each reading script keeps its own HIGH_REVIEWED set with no reason per id | Prevention (extends HIGH_REVIEWED and the static scan) | Backlog, into Sprint 12's F57 release | pending |
| I4 | The code-edit check in `block_unraw_escape.py` ignores text inside a search pattern | The check matches paths and verbs across a whole command | Prevention of false blocks | Skip | pending |
| I5 | A section written before its apply takes its counts from the dry run's printed line | A count typed from memory | A written rule | Skip | pending |
