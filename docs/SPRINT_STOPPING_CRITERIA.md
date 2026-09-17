# Sprint Stopping Criteria

Adapted 2026-08-30 from spamfilter-multi's SPRINT_STOPPING_CRITERIA.md via hsbc-quantum-fraud-2026. Purpose: models work autonomously during sprint execution until one of these criteria is met. Stopping at the right time is not failure; stopping at the wrong time wastes the team lead's time.

**REWORKED 2026-09-16 (Sprint 1 Task H, F1).** The version inherited at
seeding carried a Criterion H specific to hsbc-quantum-fraud-2026's own
metered Dirac-3 hardware runs, and Criterion 9 referenced that project's
own submission deadline. Neither applies here: this repository has no
metered hardware and no submission calendar. Removed rather than
generalized -- there is no equivalent constraint in this repository to
generalize them into.

## Criteria 1-10

1. **NORMAL COMPLETION** -- all sprint tasks complete, tests green, acceptance criteria walked with evidence. Action: proceed to Phase 5 validation handoff, then Phase 6/7 per the workflow. Then present next-step options (review / next sprint / ad-hoc).
2. **BLOCKED** -- external dependency (a decision only the team lead can make, an external service or account this repository does not control) or an error persisting after 2-3 genuine resolution attempts. Action: document the blocker (root cause, attempted solutions, what unblocks) in the sprint issue, notify immediately, continue any unblocked tasks.
3. **SCOPE CHANGE** -- the team lead adds/changes requirements mid-sprint, or a task's true size is 2x+ the estimate. Action: stop, present original vs new estimate and options (reduce elsewhere / extend / defer), wait for decision. Deferring approved work is ALWAYS a Class-3 decision, never Claude's call.
4. **DISCOVERY** -- a defect in existing work. Critical (blocks the sprint): fix now, add a regression test, document. High: fix if time allows, else backlog with an issue. Medium/Low: issue + backlog, do NOT context-switch. **Precedence: a defect that invalidates a committed record's provenance or certainty, or any confidentiality/access-control violation (e.g. a paper's PDF committed into version control against ADR-0005 section 3), is NEVER Criterion 4 -- it is ALWAYS Criterion 7 (stop, document, wait), even inside the auto-advance window. Never silently fix and re-export evidence-bearing records.**
   - **4a. Team-lead-found gap in sprint theme**: extend scope WITHOUT formal change when ALL hold: same category as sprint work, cumulative fix < 2h, no new design decisions, team-lead-reported. Otherwise treat as 3 or 4.
5. **REVIEW REQUEST** -- the team lead asks for early review. Stabilize, commit, go to Phase 7.
6. **SPRINT REVIEW COMPLETE** -- Phase 7 done, PR ready, team lead notified. Wait for approval; on merge, execute 6.6 carry-forward immediately.
7. **FUNDAMENTAL DESIGN FAILURE** -- evidence the approach cannot work (for this project also: a discovered defect that invalidates a set of records already exported). Takes precedence over Criterion 4 whenever both could apply. Action: document, propose 2-3 alternatives, wait. If the fix would amend an ACCEPTED ADR's spine, that is Class 1 and requires explicit approval as a dated amendment (CLAUDE.md "Early innovation: expect revision").
8. **CONTEXT LIMIT** -- near the window's end: commit everything, reconcile CHECKLIST-Phase2-pre.md, update sprint status, write a clean handoff so the next session resumes from the repo alone.
9. **TIME LIMIT** -- wall-clock hours are NOT a stop signal by themselves. This repository has no fixed deadline (SPRINT_1_PLAN.md: "No deadline"). Do not wrap up early "concerned about hours"; do not defer approved scope on time intuition (Class 3).
10. **NOT A STOPPING CRITERION: implementation decisions.** Method A vs B, refactor vs extend, signature changes needed to meet acceptance criteria, single test failures, style warnings, approach uncertainty: make the best engineering judgment, document it, continue. Decision rule: "Does this decision enable the acceptance criteria?" YES -> decide and continue. NO -> it is scope change (Criterion 3).

## What should NOT cause stopping

Single test failure (fix it); analysis warning (fix or note); waiting on a push (background it); uncertainty (implement, test, iterate); feature seems minimal (acceptance criteria define done); minor style (fix or note); any implementation choice within scope.

## Stopping checklist (any stop)

- [ ] Work committed; no uncommitted changes stranded
- [ ] Sprint issue updated with status
- [ ] Blocker documented if applicable
- [ ] Team lead notified: reason, status (done/remaining), next steps, decision needed (if any)

## Communication template

```
STOP: [reason / criterion]
Status: [completed vs remaining]
Reason: [why stopping is necessary]
Action taken: [commits, docs, issues]
Next steps: [what resumes work]
Team-lead decision needed: [what, or "none"]
```
