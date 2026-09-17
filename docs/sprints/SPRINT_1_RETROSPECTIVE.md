## Sprint 1 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not flawless. All eight tasks (A-H) shipped plus the sibling-repo write guard, seven ported memory files, and F2-F4 carded at validation -- substantial scope for a first sprint. Real rework happened: the export corruption caused by `test_ingest_seed_set.py`'s first version (isolated DB/METADATA paths but not EXPORT_DIR, silently overwriting the real `export/` directory), and two ad-hoc shell-quoting false negatives in my own smoke tests (`block_unraw_escape.py`, `block_sibling_repo_writes.py`) that cost re-verification passes. Both were caught before they reached a commit, which is the process working, but "caught before commit" is not "did not happen."

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Strong. Every hook, every schema constraint, and the export's determinism property were verified by injection, not just by a passing run -- `test_schema.py`'s CHECK constraints were proven to reject their exact violation, `test_hook_registration.py`'s and `test_sibling_repo_write_guard.py`'s hooks were exercised against controlled payloads, and `test_export_currency.py` caught the real export-corruption bug described above the same day it happened. The one gap: the new `test_no_source_repository_process_leakage.py` guard is itself untested against a false negative in CI specifically (verified locally by injection, not on the runner).

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: No real baseline to compare against -- every Sprint 1 estimate was `[no-history]` by construction. Task H alone grew from "remove hsbc references" to an 11-file, 4-commit rework once the actual scan ran, which is the expected shape of a first no-history estimate: too small until the real surface area is measured. Actuals were not recorded in a form Sprint 2 can calibrate against (F2's proposed deep-dive into spamfilter-multi's estimation method is directly relevant here).

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The plan's own premise-falsifier design (Task E before Task F) was the right shape even though its actual execution was deliberately curtailed by the team lead mid-sprint -- the DESIGN correctly gated the expensive step behind a cheap check, and when the team lead chose to skip the check, that choice and its consequence were recorded as an amendment rather than silently absorbed. Task H's sub-steps (scan, classify, review, apply, test) held up exactly as planned across four commits.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: One background research agent (paper metadata extraction) did the right kind of work for a fork/subagent -- read 46 PDFs, extracted real citations, caught a filename arXiv-id error and an empty file. No escalation needed during the sprint; main-loop work stayed main-loop.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Mixed. The numbered-question format switch (mid-sprint, after the team lead flagged it) should have been the format from turn one -- it was already documented practice in a sibling repository, and this repository went a full session without it before the team lead had to ask directly. Once adopted, question framing improved. Narration of blockers (Task E's deferred measurement, the export-corruption bug) was immediate and specific, not glossed.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The domain-scale-contexts question (Task D) surfaced a genuine tension between the plan's literal text and ADR-0004's own "add a context only when forced" rule -- correctly surfaced as a question rather than silently picking one reading, and the team lead's answer (seed the full set now) is recorded as a deliberate exception to the ADR's default, not a quiet override.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, with one finding this retro carries forward: ADR-0004 and ADR-0005 have NOT been updated with a single amendment reflecting anything Sprint 1 actually built or found, despite Sprint 1 crossing the 20-paper checkpoint both ADRs name. The missing-yield gap Task E found in ADR-0005's own worked example is still undocumented in the ADR itself. This is now explicitly part of F75's scope, but it should have been flagged as a documentation debt the moment it was found, not only at Manual Validation.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Two real friction points, both process-shaped rather than one-off mistakes: (1) ad-hoc bash smoke tests via `echo | python hook.py` produced false negatives THREE separate times this sprint (unraw-escape, sibling-repo-writes, and the seed-set test's export corruption) before switching to a `subprocess.run()`-based harness with real JSON encoding. The fix should be a stated convention, not a lesson re-learned per hook. (2) `git checkout -b` and heredoc-adjacent Bash calls are silently subject to `block_unraw_escape`/`block_shell_metachar_expansion` firing on unrelated content in the same message -- correct behavior, but the pattern recurred often enough to be worth naming.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Adjudication-cost risk (the plan's own named top risk) materialized as "we decided not to measure it yet" rather than a bad number -- a legitimate outcome, but it means Sprint 1 closes without resolving its own most important named risk, which is now F75's job. The applicability-field gap (single context per paper) was not a named risk in the plan at all and was found only at Manual Validation review, not during Task F itself -- worth asking whether Task F's own acceptance criteria should have caught it.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Master plan is current (F2-F4 added and ordered by dependency at Manual Validation). Sprint 1's own summary/retrospective docs are what this turn is producing. No blockers named.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The schema's actual implementation carries choices ADR-0004/0005 do not mention explicitly (join tables for `see_also` and `assertion_documents` rather than inline lists, the specific CHECK-constraint enumerations) -- none contradict the ADRs, but none are recorded as amendments either. Per CLAUDE.md's own "early innovation: expect revision" framing, an implementation detail that diverges from or elaborates on the ADR text should be a recorded amendment, however small.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**:
  - [Claude] Fold an ADR amendment recording the actual schema's join-table choices into whichever Sprint 2 task first touches store/schema.sql again -- target: Sprint 2 plan, est: 15m
  - [Claude] Add a stated convention (CLAUDE.md or QUALITY_STANDARDS.md) that hook/script smoke tests use subprocess.run() with programmatic JSON, never a bash `echo | python` pipe -- target: Sprint 2 plan, est: 10m

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond F2-F4, already carded at Manual Validation.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The one background research agent (46-paper metadata extraction) produced first-pass-correct, directly usable output: real citations sourced from actual PDF content, not filenames, with two genuine defects caught (truncated arXiv id, empty seed file) and clearly flagged rather than silently corrected. No rework needed on its output beyond my own promotion-count decisions (which papers to mark `screened`), which were editorial judgment, not correctness fixes.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None from the Development Team side.

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | Mandate subprocess.run() with real JSON for all hook/script smoke tests; ban `echo \| python` pipes | Category 9 (Process Issues) | process/tooling | 10m | now |
| 2 | Record an ADR amendment for the schema's undocumented implementation choices (join tables) | Category 12 (Architecture Maintenance) / Category 8 (Documentation) | documentation debt | 15m | backlog (folded into F75) |
| 3 | Add an explicit "output matches every ADR-defined field" acceptance-criterion pattern to sprint-card templates | Category 10 (Risk Management) | process improvement | unknown | backlog (folded into F2) |

Team lead, 2026-09-16: "all as recommended."
