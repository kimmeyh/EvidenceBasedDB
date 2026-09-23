# Backlog Refinement Process

Adapted 2026-08-30 from spamfilter-multi's BACKLOG_REFINEMENT.md. The presentation format below is AUTHORITATIVE: read this section in the same turn immediately before producing any candidate presentation; mirror it exactly; ad-hoc tiers, grid tables, or unregistered IDs are process violations.

## When refinement runs

Refinement is MANDATORY and runs TWICE per cycle, as **Sprint N's Phase 1 on Sprint N's branch** (re-homed 2026-09-19, Sprint 4 Task A; it was "prior sprint Phase 8", which made a session report Sprint N-1 while working on Sprint N's branch):

- **Pass 1 -- Completeness Sweep (Phase 1.2)**: immediately after the 6.6 carry-forward cut, in parallel with the team lead's main merge. Purpose: confirm every close-out step of Sprint N-1 actually happened (issues closed, docs triad present, master plan rolled, shipped items pruned, sprint_status advanced to N). Corrections only; NEVER selects scope.
- **Pass 2 -- Scope Selection (Phase 1.4)**: after the delivery-cycle artifacts are current. Presents the slate titled for the sprint being planned -- "Sprint N Candidates at a glance"; the team lead selects; feeds Phase 2 and 3. The ONLY pass that selects scope.

A pass can be SHORT when little needs correcting or selecting; short is not skipped.

## Session structure (timeboxed, 30-60 minutes total)

Prepare (read master plan + repo CHECKLIST, gather velocity actuals) -> Review (stale/obsolete items) -> Prioritize (value x effort x risk; team lead makes the final call) -> Estimate (minutes, calibrated from recorded actuals, never remembered totals; unknowns tagged `[no-history]` and timeboxed) -> Add new items -> Cleanup -> Commit (`docs: Backlog refinement - <date> - <summary>`).

## Item identification

Every item carries a real registered ID: **F#** for features/process/tech-debt items (next available number from ALL_SPRINTS_MASTER_PLAN.md), or **Issue #N** for GitHub issues without an F#. Never invent unregistered slugs.

**F#-only rule (team lead, Sprint 2 retro, 2026-08-30)**: in every refinement presentation and candidate slate, items are referenced by their backlog identifier (F#) and NOTHING else. GitHub issue numbers, task letters, and card references never appear in a candidate presentation; they belong on sprint cards and PR bodies only.

## Backlog Presentation Format (AUTHORITATIVE)

**Summary Index first** -- every item's header line only, in presentation order, HOLD items one line each in the same full shape (never a bare ID list). The heading names the sprint being planned, which is the branch's sprint number:

```markdown
## Sprint <N> Candidates at a glance

- **F75. Action the 20-paper ADR checkpoint (~2h) Priority 6**
- **F76. Guard the shared vocabulary between ADR-0004 and ADR-0005 (~1h) Priority 7**
- ...
- F13. Phase 2 planning (~unknown) Priority HOLD
```

**Item format** (verbatim):
```markdown
**<ID>. <Title> (~<effort>) Priority <N>**
- Phase: <phase/stage name>
- Platform: <N/A, or the specific tool/service the item touches>
- <description bullet>
- <description bullet>
- Depends on: <dependencies if any>
```

**Rules**:
- Priorities are NUMERIC, increments of 10; items that should sprint together use increments of 2. Never ad-hoc groupings.
- Group items under `### <Phase Name>` section headers matching this repository's own sprint sequence (e.g. Foundation, Process, Tooling) -- never a fixed set copied from another project's timeline.
- HOLD items use `Priority HOLD` in a `### HOLD Items (<reason>)` section at the bottom, with full detail bullets there.
- Bugs and tech debt interleave by priority within their phase group; no separate sections.
- Completed items are REMOVED (history lives in sprint docs and git).
- No grid tables for the presentation.

## Definition of Ready

Clear scope, quantifiable acceptance criteria, minute-based estimate, no unresolved blockers, clear priority. Not-ready states: Needs Clarification / Needs Research / Blocked / Too Large (split it).

## Anti-patterns

Analysis paralysis (timebox); premature detail on far-future items (title + priority only); stale backlog (review anything 3+ sprints old); missing value statements (every item answers "this enables / this prevents"); uncalibrated estimates; scope creep during refinement (defer new ideas to the add step, sized, not designed).
