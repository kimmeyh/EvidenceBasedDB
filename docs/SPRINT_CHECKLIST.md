# Sprint Checklist (single page)

Consult at EVERY phase boundary (open this file in the same turn; walk lines with DONE/N-A/NOT-DONE + evidence). Full detail: SPRINT_EXECUTION_WORKFLOW.md.

## Phase 1: Backlog Refinement (Sprint N's first phase, on Sprint N's branch -- re-homed from prior-sprint Phase 8, 2026-09-19)
- [ ] sprint_status.json advanced to N at the carry-forward cut (`"Phase 1.1 Backlog Refinement"`, `plan_doc: null`); status line says Sprint N
- [ ] 1.1 CHANGELOG reconciled for Sprint N-1 (from git history, never memory)
- [ ] 1.2 Pass 1 sweep for N-1: issues closed, docs triad incl. SUMMARY (+ `## Actuals`), master plan rolled, shipped cards pruned BY HAND
- [ ] 1.3 Design-document currency: ADR-0004/0005 still match schema and export; `pytest -q` green
- [ ] 1.4 Read ALL_SPRINTS_MASTER_PLAN.md + repo CHECKLIST-Phase2-pre.md; read BACKLOG_REFINEMENT.md "Backlog Presentation Format" THIS TURN; present "Sprint N Candidates at a glance" (Summary Index first, F# IDs, numeric priorities, HOLD one-liners)
- [ ] 1.5 Record team-lead selection; update master plan; commit

## Phase 2: Pre-Kickoff
- [ ] Previous PR merged; previous sprint issues CLOSED (manual close; feature->develop does not auto-close)
- [ ] Working tree clean; develop pulled current; sprint branches never deleted
- [ ] `pytest -q` green; dependency scan noted

## Phase 3: Kickoff & Planning
- [ ] Previous sprint SUMMARY doc created and linked in master plan (three-doc rule: PLAN + RETROSPECTIVE + SUMMARY, no exceptions)
- [ ] SPRINT_N_PLAN.md drafted: objective, tasks, quantifiable acceptance criteria, minute estimates
- [ ] Plan verified against branch state (already-shipped work marked, stale paths corrected); re-estimated if findings
- [ ] Branch exists (usually via prior 6.6 carry-forward); DRAFT PR created/updated (STAYS DRAFT until 7.7)
- [ ] One GitHub issue per task (`sprint` label) BEFORE first task file is touched; all OPEN
- [ ] Explicit team-lead approval obtained; PR body updated to approved plan

## Phase 4: Execution (auto-advance window: no permission-asking)
- [ ] Tasks in plan order; tests after each change; commits reference issue #N
- [ ] `git status --short` before every staging; every entry accounted for; 0* files committed neutrally, never read
- [ ] Provenance discipline: every record's `provenance` field set before commit

## Phase 5: Review & Validation
- [ ] Full suite green; committed export matches a fresh regeneration from the store (`tests/test_export_currency.py`)
- [ ] Plan acceptance criteria walked line by line WITH EVIDENCE
- [ ] Handed to team lead for manual validation (questions correct from here)
- [ ] Manual Validation list contains ONLY end-user functionality and team-lead decisions; no test run, dry run, byte-identity check or data spot-check appears in it (those are done before hand-over; state in one line that they passed)
- [ ] Every amendment to an existing ADR presented as `ADR-<n> <adr-name>`, then What changed and Why, then the specific language quoted for review; ADR reviews first, functional steps after

## Phase 6: Push & Finalize PR
- [ ] Branch pushed; existing draft PR body updated (still DRAFT); interim status given, not "ready"
- [ ] ON MERGE NOTIFICATION: next sprint branch created FROM CURRENT FEATURE BRANCH immediately; post-merge work committed there; never stash; never branch from develop post-merge

## Phase 7: Retrospective (before ready)
- [ ] 7-step protocol run in order (SPRINT_RETROSPECTIVE.md); 16 categories x 4 roles, verbatim, no placeholders
- [ ] Improvements proposed + dispositioned; now-items committed; backlog-items -> master plan with F#s
- [ ] Completion updates: master plan Last Completed Sprint; CHECKLIST-Phase2-pre.md reconciled; sprint_status updated
- [ ] `gh pr ready` (ONLY here); final gate; team lead notified for approval

## Phase 8: Delivery hand-off (the finishing sprint's last phase)
- [ ] Team lead merges feature->develop, then develop->main (Claude never merges)
- [ ] 6.6 carry-forward cut of Sprint N+1's branch FROM the current feature branch; sprint_status advanced to N+1 in the same turn
- [ ] From here the session is Sprint N+1 Phase 1 -- go to the top of this checklist
