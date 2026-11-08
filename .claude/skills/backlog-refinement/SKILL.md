---
name: backlog-refinement
description: Run a Backlog Refinement pass for this repository (Sprint N Phase 1.2 Completeness Sweep or Phase 1.4 Scope Selection) and present "Sprint N Candidates at a glance" in the authoritative format from docs/BACKLOG_REFINEMENT.md. Use when the team lead asks for refinement, a candidate slate, backlog grooming, or when Phase 1 of a sprint begins.
---

# Backlog Refinement (invokable wrapper for docs/BACKLOG_REFINEMENT.md)

Sprint 4 Task J (F20), 2026-09-19. This skill adds no content of its
own. `docs/BACKLOG_REFINEMENT.md` is the authoritative process and
presentation format; this wrapper makes reading it fresh the invocation
contract instead of a habit. The failure it prevents is this
repository's own named pattern: checking that a rule exists is not the
same as applying it (CLAUDE.md "Things Claude Should NOT Do").

## Hard rules

1. **Step 1 is not optional and does not carry over.** Read
   `docs/BACKLOG_REFINEMENT.md` IN THIS TURN, before producing any
   candidate presentation. A read from an earlier turn, a memory file, or
   a recalled summary does not count (workflow invariant 5: "read the
   format doc before producing its output... never reproduce from
   memory"). Skipping this step is a process violation, not a shortcut.
2. **Numbering follows the 2026-09-19 re-homing (Sprint 4 Task A).**
   Backlog Refinement is Sprint N's Phase 1, on Sprint N's branch, the
   moment the 6.6 carry-forward cut exists. It is never the prior
   sprint's Phase 8 (re-homed 2026-09-19). The slate is titled for the
   sprint being planned, which is the branch's sprint number.
3. **F#-only rule.** Every item carries a real registered F# from
   `docs/ALL_SPRINTS_MASTER_PLAN.md`. GitHub issue numbers, task letters
   and card references never appear in a candidate presentation.
4. **No grid tables in the presentation; no invented tiers; numeric
   priorities in increments of 10 (2 for items that sprint together);
   the recommendation first, at most 20 items, details in the index's
   order with no group headers, HOLD items after the 20.**
5. **Pass 1 never selects scope. Pass 2 is the only pass that does.**
   The team lead makes the final call; the slate is a proposal.
6. **Decision questions take the shape of `docs/SPRINT_RETROSPECTIVE.md`,
   "Presenting improvements, questions and decisions"**: `q1` to `qN`,
   lettered options with pros and cons, one marked "(Recommendation)",
   answered as "q1. a" (team lead, 2026-11-07). Never the AskUserQuestion
   tool (hook-blocked in this repository).

## Procedure

### Step 1: read the format doc, this turn

Open `docs/BACKLOG_REFINEMENT.md` and read the whole file, then re-read
its "Backlog Presentation Format (AUTHORITATIVE)" section immediately
before writing the slate. Mirror it exactly.

### Step 2: name the pass and the sprint

State in one line which pass this is and for which sprint:

- **Phase 1.2, Pass 1 (Completeness Sweep) for Sprint N-1**: confirm
  Sprint N-1's issues are closed, its docs triad exists (PLAN,
  RETROSPECTIVE, SUMMARY with `## Actuals`), the master plan is rolled
  (Last Completed Sprint, Past Sprint Summary row), shipped cards are
  pruned BY HAND (never by a script), and `.claude/sprint_status.json`
  already says Sprint N in `"Phase 1.1 Backlog Refinement"` with `plan_doc: null`.
  Corrections only.
- **Phase 1.4, Pass 2 (Scope Selection) for Sprint N**: the slate.

Phase 1.1 (CHANGELOG reconciliation for Sprint N-1) and Phase 1.3
(design-document currency: ADR-0004 and ADR-0005 still match the schema
and the export) run between the two passes, per
`docs/SPRINT_EXECUTION_WORKFLOW.md` "Phase 1 detail". Confirm both are
done before Pass 2, or do them first.

### Step 3: gather the inputs

Read `docs/ALL_SPRINTS_MASTER_PLAN.md` (Next Sprint Candidates and the
item details) and the repo-root `CHECKLIST-Phase2-pre.md`. Gather
velocity actuals from the previous sprint's `SPRINT_{N-1}_SUMMARY.md`
`## Actuals` section, never from memory. Identify stale or obsolete
items (anything three or more sprints old gets re-read, not re-listed).

### Step 4: present "Sprint N Candidates at a glance"

Produce the presentation in the format read in Step 1 (revised
2026-10-14): Summary Index first, in three parts:
"Recommended for Sprint N" (Claude's proposed scope, with its total), then at most 20
non-HOLD items by priority, Priority 10 first (the rest counted in one
line), then the HOLD items one line each in the same full shape. The
item details follow as one flat list in exactly that order, with no
group headers: each item's `Phase:` line names its group. Each item in
the verbatim item format (Phase, Value, Platform, description bullets,
Acceptance, Depends on; F94, 2026-10-22). Estimates in minutes, never
hours, calibrated from the actuals gathered in Step
3, `[no-history]` plus a timebox where none exist.

### Step 5: record the selection

Sprint scope is DEFINED, never additive (`docs/SPRINT_PLANNING.md`): the
team lead's selection list IS the complete scope. Record it in the
master plan's Current sprint section, commit with
`docs: Backlog refinement - <date> - <summary>`, and proceed to Phase 2
(Pre-Kickoff), then Phase 3 (Kickoff and Planning).

## What this skill does not do

It does not plan the sprint (Phase 3), does not create issues or the
draft PR (Phase 3.3.1 and 3.4), and does not decide scope. It presents;
the team lead selects.
