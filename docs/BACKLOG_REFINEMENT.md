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

**Revised 2026-10-14 (team lead, Sprint 9 Phase 1.4):** the details are no longer grouped under phase headers, they follow the Summary Index's order, the Summary Index holds at most 20 items, and Claude's recommendation for the sprint comes first. Until then the details sat under `### <Phase Name>` groups in a different order from the index, so an item had to be found twice.

**Summary Index first**, in three parts. The heading names the sprint being planned, which is the branch's sprint number:

1. **Recommended for Sprint <N>**: Claude's proposed scope, each item's header line, with the total estimate. It is a proposal; the team lead selects.
2. **The top 20**: the 20 highest-priority non-HOLD items (fewer if fewer exist), header lines only, ordered by priority, Priority 10 first. Recommended items appear here too, in their priority place. Items past the 20th are counted in one line ("N more, Priority X to Y, in the master plan"), not listed.
3. **HOLD items**: one line each in the same full shape, after the 20 (never a bare ID list).

```markdown
## Sprint <N> Candidates at a glance

**Recommended for Sprint <N>** (~<total>):
- **F75. Action the 20-paper ADR checkpoint (~2h) Priority 6**

**Top 20 by priority:**
- **F75. Action the 20-paper ADR checkpoint (~2h) Priority 6**
- **F76. Guard the shared vocabulary between ADR-0004 and ADR-0005 (~1h) Priority 7**
- ...
- 3 more, Priority 120 to 140, in the master plan

**HOLD:**
- F13. Phase 2 planning (~unknown) Priority HOLD
```

**Item details** follow, one flat list in exactly the Summary Index's order (the top 20, then the HOLD items), with no group headers. Each recommended item is detailed once, in its priority place. An item's group is named in its own `Phase:` line, never as a header. **Item format** (verbatim):
```markdown
**<ID>. <Title> (~<effort>) Priority <N>**
- Phase: <phase/stage name; this is where the group is named>
- Platform: <N/A, or the specific tool/service the item touches>
- <description bullet>
- <description bullet>
- Depends on: <dependencies if any>
```

**Rules**:
- Priorities are NUMERIC, increments of 10; items that should sprint together use increments of 2. Never ad-hoc groupings.
- No `### <Phase Name>` group headers in the details; the `Phase:` line carries the group (team lead, 2026-10-14).
- HOLD items use `Priority HOLD` and come after the top 20, with full detail bullets.
- Bugs and tech debt interleave by priority; no separate sections.
- Completed items are REMOVED (history lives in sprint docs and git).
- No grid tables for the presentation.

## Definition of Ready

Clear scope, quantifiable acceptance criteria, minute-based estimate, no unresolved blockers, clear priority. Not-ready states: Needs Clarification / Needs Research / Blocked / Too Large (split it).

## Anti-patterns

Analysis paralysis (timebox); premature detail on far-future items (title + priority only); stale backlog (review anything 3+ sprints old); missing value statements (every item answers "this enables / this prevents"); uncalibrated estimates; scope creep during refinement (defer new ideas to the add step, sized, not designed).
