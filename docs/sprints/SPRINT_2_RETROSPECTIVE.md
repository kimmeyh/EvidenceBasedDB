## Sprint 2 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Task A's applicability re-derivation gated everything correctly (B, C, G all depended on or benefited from it running first); running B and C together against different ground truths in one team-lead review pass avoided a second review cycle.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good, with one real finding along the way: `test_view.py`'s Windows tempdir cleanup and a `--json` `UnicodeEncodeError` on non-ASCII citation text were both caught by actually running the tool against real data before declaring Task G done, not by unit tests in isolation. The guard-discipline injection proof (revert the relation-resolution fix, watch it fail, restore) held throughout, including for the retrospective-improvement hook added after Manual Validation.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The plan's task-order sequencing (A first, then B/C in parallel, D/E flexible, G last) matched actual execution order with no rework caused by sequencing being wrong. Task B's scope gap (no HSBC assertions existed yet to spot-check) is the one real estimation miss, now the source of the data-precondition-check improvement added to `SPRINT_PLANNING.md`.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The Class 3 scope change (Task F to F7-F11) was recorded as a dated amendment in `SPRINT_2_PLAN.md` with an explicit "why this is Class 3" rationale, rather than a quiet task swap -- exactly the discipline this project's own Decision-Class Checkpoint Protocol asks for.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. This sprint's F7-F10 design work is itself a step toward making model-tier assignment measurable (comparing Haiku/Sonnet/Opus/Fable review quality against team-lead adjudication time) rather than judged qualitatively going forward.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not Very Good. The AskUserQuestion ban was violated twice in one session during Task C's directory-drift finding, the second time immediately after already being corrected for the identical thing, with the rule present in `CLAUDE.md` and memory the whole time. Both violations were fixed and the rule strengthened in-session; the retrospective now hook-enforces it (`.claude/hooks/block_ask_user_question.py`) so it does not depend on remembering a documented rule under time pressure.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, with one gap worth naming: Task B's original scope ("spot-check assertions against HSBC's determinations") assumed matching assertions already existed in the store, and none did. The team lead's decision to extract real assertions first, then check them, was the right correction, but the plan itself should have verified the precondition before estimating the task -- now Sprint Planning improvement 3.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Dated amendments (never silent edits) were used consistently: ADR-0004 Amendment A4 and ADR-0005 Amendment A1 (both walking the six-question checkpoint against real store statistics), `SPRINT_2_PLAN.md`'s Class 3 scope-change amendment, and `CLAUDE.md`'s new explicit US-English statement.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not Very Good. The `Closes #N` gap (issues #13 and #15 stayed open despite commit messages referencing them, since auto-close only fires on merge to develop, not on feature-branch commits) recurred even though `SPRINT_EXECUTION_WORKFLOW.md` already documented it as a known defect class (workflow 2.3). Documenting a gap is not the same as checking for it -- now a mechanical step in Phase 5 (retrospective improvement 1).

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The premise falsifier was taken seriously -- Task B/C findings were evaluated explicitly against "systematic inaccuracy" criteria before being treated as isolated fixes, and the sprint's own top-named risk (adjudication cost) was not silently dropped when Task F was replaced; it was carried forward as F11, sequenced to run after F7-F10 so the eventual measurement is still produced.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F7-F13 are fully carded with dependencies, priorities, and explicit "not this card's job" boundaries, ready for refinement without further design work. `sprint_status.json` reflects execution-complete state accurately.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Both ADRs' early-innovation checkpoints were walked against real data (not just re-affirmed on faith), and one real correction was made mid-sprint (the applicability count, initially miscounted as 44 of 46, corrected to 45 of 46 before the amendment was committed) rather than deferred or silently absorbed.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond the three retrospective improvements already applied as commits (Phase 5 issue-state check, the AskUserQuestion hook, the data-precondition estimation check).

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None beyond F7-F13, already carded in `docs/ALL_SPRINTS_MASTER_PLAN.md` at Manual Validation and mid-sprint.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. No subagents were needed this sprint; all work stayed direct, main-loop.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: None from the Development Team side.

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
| 1 | Before declaring Manual Validation ready, run `gh issue list --label sprint --state open` and account for every result | Category 9 (Process Issues) | process/tooling | 5m | now |
| 2 | Hook-enforce the AskUserQuestion ban (`.claude/hooks/block_ask_user_question.py`), rather than relying on `CLAUDE.md`/memory alone | Category 6 (Communication) | process/tooling | 30m | now |
| 3 | Add a data-precondition check to `SPRINT_PLANNING.md`'s Estimation section for "validate/check X against Y" cards | Category 3 (Effort Accuracy) / Category 7 (Requirements Clarity) | process improvement | 10m | now |

Team lead, 2026-09-18: "all 3 now."
