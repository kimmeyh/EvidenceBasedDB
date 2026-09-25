# Sprint 5 Retrospective: Make the Store Durable, Then Fill It

**Date**: 2026-09-25. **PR**: #43. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete".

## Sprint 5 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All nine tasks delivered and the store grew from 48 to 347 papers through the one door with 0 refusals, plus a working synthesis pilot. Efficiency was helped by running the slow, API-bound jobs (arXiv at about 13 s per id under refusal, the site scrape, the author search) in the background while other tasks proceeded. Rework counted honestly: the author search ran three times (truncation fix; abstracts for the revised Q1), the manifest generator went through four DOI-lookup fixes, and my own shell-heredoc patches broke Python strings three times before I switched to the Edit tool for multi-line code.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard carries its own injection and was seen to fail. The suite caught three real defects in my own work before the team lead did: the applicability guard (after I aligned it to ADR-0005 A2) caught the pilot skipping `screened`'s obligation; the write-script coverage guard caught a script it should have listed; the durability tests caught the working-tree/HEAD confusion. But I wrote one vacuous assertion (`== 48 or True`) and had to catch it on reread, and Manual Validation still found two display defects and a stale disposition that no test covered. 458 -> 496 tests.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimate 780 Claude-side minutes; actual execution about 108 minutes of coordinator wall clock (approval 08:19 to the last task commit 10:07 on 2026-09-24), plus about 126 minutes of Manual Validation fixes on 2026-09-25. The Sprint 4 pattern held, more strongly: estimates in coordinator minutes overstate work that agents and background runs carry. Runtime estimates were the better numbers: arXiv metadata at 13 s per id matched the refusal-path measurement taken at planning. The miss was size, not time: the QCi site was 544 pages against about 300 planned.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The pre-flights paid off. The arXiv 429 found at planning became the serial-traffic rule that held all sprint, and the title-mismatch check predicted what Task C found. The premise falsifiers worked as designed: (a) held (byte-identical rebuild), (b) held (0 refusals), (c) was falsified for prolific authors and reported, not hidden. Weak spot: the plan did not say what "read" promotion owes (applicability), so the pilot skipped it.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Four delegated agents: two Sonnet evidence extractors (105k and 134k tokens), one fresh-eyes reviewer (85k), and none for coding. The reviewer earned its place: four real defects in the durability code, including a restore that could not restore a corrupt store. Evidence agents were accurate on 22 of 23 quotes (one wrong page number). Keeping judgment (context rules, certainty, disambiguation) in the lead model was right.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Status updates were regular, and every decision was a numbered question. Two lapses: I twice reported counts before checking them (a commit message summing to 55 instead of 52, amended before push; "5 entries" that listed 6) and one comparison in a docstring was false (Lac Nguyen "4 against 13") until I corrected it.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Clear overall. Q6 of the plan named one folder where three were implied; I stated the assumption at approval rather than asking. The team lead's mid-validation Q1 revision (topic screen) was a new requirement handled inside the sprint with its rule written first.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Rules were written before each run they governed (INTAKE_WORKFLOW sections 11-13, the disambiguation rule, the topic screen), and corrections to shipped sections carry dated notes. CHANGELOG kept current per commit. The Sprint 5 SUMMARY with Actuals is still to write (Phase 7).

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: arXiv's API refused this client for the whole sprint (429 and 406) while arxiv.org served every PDF; DataCite carried the metadata. My bash heredocs holding Python with "\n" inside strings repeatedly produced broken files; the metachar hook blocked one command correctly. Publisher bot-challenge pages were first saved as if they were content.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The named risks were the right ones. arXiv refusal materialized and was contained by design. Volume without judgment was contained by `seen` plus honest dispositions. The durability risk was mitigated before the first bulk write, and a verified backup preceded every one of the nine `--apply` runs. Unnamed risk that materialized: identity collisions in author search were worse for common names than planned, and the family-name query silently truncated.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: F32-F35 are carded for Sprint 6 with planning notes; F36 and F37 should be decided with F34 in one ADR amendment. The store rebuilds from its export and backs up before writes, so the 1,410-record bulk load starts from a safe base.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No ADR text changed. One guard was aligned to ADR-0005 A2 (applicability is `screened`'s obligation), documented. The door gained one explicit exception (`check_local_paths`) for the rebuild, defaulting to strict. Export determinism held: rebuild byte-identical at 48 and at 347 papers.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:
  - [DEV] Refresh the manual-download list: [QC-8] now arrived via the author search -- target: Sprint 6 plan, est: 5m
  - [DEV] Prune F5, F28, F30, F31 from Next Sprint Candidates and add Sprint 5 to Past Sprint Summary -- target: Sprint 6 plan, est: 15m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:
  - [DEV] A promotion path through `screened` for extraction at scale (the pilot skipped it) -- estimated: 1h, priority: 26, depends on: F37
  - [DEV] Record the metadata provider as a field rather than updated_reason text -- estimated: 30m, priority: 28, depends on: F36

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Evidence agents: high first-pass correctness (22 of 23 quotes exact, one page off), stayed read-only, disclosed an accidental temp file and deleted it. Reviewer: precise, reproduced one finding on scratch copies rather than the live store, and scoped its confidence. No coding was delegated this sprint.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none from the Development Team.

## Improvement Decisions

Team lead, 2026-09-25, verbatim: "do all now". All eight applied in commit
5be2402, each extending an existing control; every mechanical one proven by
injection.

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | A promotion owes the lower tiers' obligations: set_tier() refuses screened/read without applicability | Dev 2, 4 | Code guard (extends set_tier's read-tier check) | 20m | now |
| 2 | Code files change through Edit/Write, never a python-in-shell rewrite of a .py file | Dev 1, 9 | Hook (extends block_unraw_escape.py) | 45m | now |
| 3 | A tautological assertion fails the suite | Dev 2 | Test (extends test_guard_discipline.py) | 20m | now |
| 4 | A saved local copy must carry content (visible-word check at the door) | Dev 9 | Code guard (extends validate_paper) | 30m | now |
| 5 | Fresh-eyes review at the structural task's commit, not Phase 5 | Dev 5, 10 | Workflow doc (extends the fresh-eyes rule) | 10m | now |
| 6 | Numbers in prose computed in the same turn; caps reported | Dev 6, 10 | Standard (extends "computed, never stored") | 10m | now |
| 7 | Estimation calibration from Sprint 4-5 actuals; Sprint 5 learning_log rows | Dev 3, 5 | Planning doc + heuristics file | 15m | now |
| 8 | Metadata provider as a field | Dev 14 | Backlog (extends F36 as item 10) | 5m | now |
