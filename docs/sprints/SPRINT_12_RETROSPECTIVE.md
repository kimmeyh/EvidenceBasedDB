# Sprint 12 Retrospective: Fix the Entities, Speed the Suite, Then Read 400 Records

**Date**: 2026-10-24. **PR**: #122. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete".

## Sprint 12 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All 7 tasks met their acceptance criteria. Rework before hand-over came from the fresh-eyes reviews, one per code or store task: Task A took five applies (its review found 7 Sprint 5 contexts with no quote marks and a wrong page; its new test found a ".;" join), E three, F two, G two after its first (the 5744e2d review: 1 Critical, 7 Important). No rework after Manual Validation.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard was proven to fail by injection (1,175 tests at Sprint 11's close, 1,253 at hand-over). Two gaps: the first full run failed 2 tests that assumed the store before the reads, and one docstring named an injection (a straight apostrophe) that did not go red; a real early-closing quote did, and the docstring now says so. The replaced-value sign check (`unsupported_by_basis`) ran only with the store, so CI never ran it; a test now runs it from the quotes alone. F100 cut the warm suite from 781 s to 199 s.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimated 990 minutes. Plan approval (13:09) to the Manual Validation hand-over (19:31) was 382 minutes of wall clock, 146 of them idle at the usage limit (15:55 to 18:20): about 236 active minutes, about 24 percent (Sprint 11: 28 percent; Sprint 10: 53). First commits: A 13:20, D 13:28, C 13:38, B 14:03, E 14:35, F 15:07, G 19:00. The tasks overlapped (B's baseline ran 13:20 to 13:33, E started 13:29), so per-task minutes cannot be separated from `git log`.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan held; two statements changed during execution and were disclosed: E's series is stated in each record, not linked (no link type fits), and the read ledger was built with G, after E ran. The cut line inside G was not needed.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sonnet 5.5 readers, one ledger group each, up to 5 at once, read 413 records in 53 groups. The coordinator's read, on the top tier, replaced 118 values and dropped 7 assertions. The fresh-eyes reviewer found what the coordinator missed: meaning, not counts.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Changed commitments were disclosed in the next message and the status note (E's series, the ledger order, INTAKE section 46's shell append). One slip: the first Manual Validation hand-over went out while CI on the status commit was still running; the Stop hook caught it and the message was re-sent after CI passed.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: "400 total" needed a question (Q1); answered 1 at planning. The Classiq request arrived in two parts during Phase 1.4 and was absorbed into F95's release before planning.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: ADR-0005 A11; intake sections 42 to 47, each bullet written before its apply; the workflow's Phase 4 rule names the targeted runner mode. Section 46 was first appended with a shell heredoc, against CLAUDE.md; later edits used the Edit tool.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The usage limit stopped the session mid G for 146 minutes; the ledger and the status note made the restart exact (g29 and g31 resumed). The code-edit hook blocked `$(...)` in a loop and readers' heredoc writes of `.py` files; both moved to allowed forms. `--changed` cannot see a store write, so after each apply the store-wide guards ran by hand or by a full suite (proposal I1).

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: arXiv traffic stayed serial at 18 s, about 53 requests. The 3 withdrawn arXiv papers were found by their 404 and confirmed on their abstract pages, not worked around. No write crossed into a sibling repository. Phase 2 was read at a named commit.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ready. F57 count 1,449 unread with no read row; 43 papers on the hand-download list; F51 still HOLD on its re-run.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: ADR-0005 A11 records the decision-backed source link; its restatements were checked. Grading now lives in `store/grading.py`, which the write-path rule requires of new reading scripts. One record id begins with a hyphen (`-2024-dual-capability-machine-learning-models`); it predates this sprint and ids are keys, so it is not renamed, but nothing stops a new one (proposal I3).

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] Correct the 13 ".;" joins left in F48 and F97 values -- target: Sprint 13 plan, est: 20m. [Dev Team] Give the 3 LOW proved results their own stored reason instead of "an empirical result" -- target: Sprint 13 plan, est: 15m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond the improvement proposals.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: High on quotes, as in Sprint 11. The readers' main defect was again saying more than the quote (118 values replaced) and suggesting HIGH for measured results. Two readers stopped on 429s and resumed cleanly from their group files.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Improvement Decisions

Proposed 2026-10-24, prevention first, each extending an existing
prevention. Dispositions pending the team lead.

| # | Improvement | Root cause | Type | Recommendation | Disposition |
|---|---|---|---|---|---|
| I1 | `run_suite.py --changed` also runs the `live_store` guards when the store changed since the last PASSED verdict | The targeted mode picks tests from changed repository files; a store write changes none | Prevention (extends F100's runner) | Now, 30m | pending |
| I2 | `store/grading.py` names a basis for every LOW too (measured result, field statement, proved result not checked), so a LOW cannot store the wrong reason | A LOW took its reason from a default branch | Prevention (extends Sprint 11 I3's helper) | Backlog, into F57's next release, 30m | pending |
| I3 | `make_id` keeps the family name whole (no stop-word removal) and refuses an id that does not begin with a letter or digit; a `live_store` test names any stored one beyond the known exception | `intake.make_id` builds `<family>-<year>-...`; its slug drops stop words, so the first author "An" (An, Z., arXiv:2405.13582) slugged to nothing and the id starts with "-" | Prevention | Now, 20m | pending |
