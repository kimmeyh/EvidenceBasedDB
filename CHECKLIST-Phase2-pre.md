# Checklist: Deliverable Ledger (LIVE)

Owners: **H** = Harold (only he can do it), **C** = Claude (I do it), **H+C** =
decision or review done together.

**STATUS: LIVE. Update this file as work progresses.**

Created 2026-09-15, adapted from hsbc-quantum-fraud-2026's
`CHECKLIST-Phase2-pre.md`. That file tracked a "Phase 1 submitted, waiting on
Phase 2 selection" gap specific to a competition timeline; this repository has
no equivalent phase structure. What is kept is the FUNCTION: a live,
reconciled ledger of what the current sprint promised, checked at every sprint
close per workflow 3.2.1 and 8.2, so a promise made in a sprint plan does not
quietly go unverified. What is dropped is everything specific to the QCi
submission calendar.

**Nothing here may be marked done without evidence.** Per SPRINT_EXECUTION_
WORKFLOW.md invariant 4: open the artifact and check it, do not recall having
done it.

---

## Sprint 1: Build the Store (F77, consumer-repository number)

Source: `docs/sprints/SPRINT_1_PLAN.md`. Reconciled at Sprint 1 close-out
(Phase 7/8) and at the start of every sprint thereafter until every row below
is checked or explicitly deferred with a reason.

- [ ] **C**: Task A -- repository on GitHub, private; seeded methodology
      pushed; CI running the five inherited guards
- [ ] **C**: Task B -- SQLite schema for the four record classes, with the
      ADR-0004 spine and class-specific fields
- [ ] **C**: Task C -- deterministic text export, regenerated and committed.
      The export is the artifact; the store is a build output
- [ ] **C**: Task D -- contexts as first-class (`world`, `ml`, `qc`, `qml`,
      `platform:*`, `method`); factored assumptions, not tags
- [ ] **H+C**: Task E -- ingest one paper end to end (the Lenat/Marcus record
      from ADR-0005) and TIME the adjudication. This is the premise falsifier:
      its result can send Task F back to the drawing board before 46 records
      are committed to the schema
- [ ] **H+C**: Task F -- load the 46-paper seed set at `seen` tier; promote a
      VARIETY of ~20 to `screened`
- [ ] **C**: Task G -- determinate-fact resolvers, at minimum the consumer
      repository's amendment count, computed rather than stored
- [ ] **H+C**: Adjudication time recorded per record; sprint reports the
      median (Definition of Done, SPRINT_1_PLAN.md)
- [ ] **H+C**: Task H (F1, added 2026-09-15) -- hsbc-quantum-fraud-2026 process
      content scanned, classified KEEP/REWRITE/DELETE, and the classification
      reviewed by the team lead BEFORE any edit is applied
- [ ] **C**: Task H -- approved classification applied across the affected
      files
- [ ] **C**: Task H -- regression test committed that fails if a disallowed
      pattern (Dirac-3, `experiments/src`, `results.json`, `prereg-freeze`,
      etc.) reappears outside an allow-listed historical/provenance context,
      verified by injection before trusting it

## Standing constraints (apply to every sprint, not only Sprint 1)

- [ ] **C**: `--no-verify` never used; the five inherited hooks stay active
      and registered (verified by `tests/test_hook_registration.py`)
- [ ] **C**: Every assertion in the store carries provenance; a record that
      cannot say where its value came from is treated as a defect, not an
      omission
- [ ] **C**: Determinate facts resolve rather than being stored (CLAUDE.md
      standing rule)
- [ ] **H+C**: Reading-level escalation tracked one grade at a time from 8
      toward the PhD ceiling; a cluster at 17+ is logged as a finding about
      the source document

## Design-document checkpoint (both ADRs, six questions each)

- [ ] **H+C**: After roughly 20 papers are loaded (Task F above), review
      ADR-0004 and ADR-0005 against what actually happened. Record findings as
      dated amendments at the bottom of each ADR, never as silent edits

---

## Sprint 5: Make the Store Durable, Then Fill It (reconciled 2026-09-25 at Phase 7)

**Drift found at this reconciliation**: the Sprint 1 rows above were never
checked off, and Sprints 2 to 4 have no section here, although all four
sprints closed with their docs triads. Marking those rows now needs per-row
evidence, which is Sprint 6 Phase 1.2 work (carded there), not a
recollection. Evidence for each Sprint 5 row is the commit named.

- [x] **C**: Task A (F30) -- rebuild byte-identical, verified backup before
      every write, restore by script (b0a66ec; review fixes d2da51d)
- [x] **C**: Task B (F31) -- 96 files, none twice, 14 on the manual list (b0b0c84)
- [x] **C**: Task C (F31) -- 121 records at seen, 0 refused (775d6de)
- [x] **C**: Task D (F31) -- F36 carded (a33ca2f)
- [x] **C**: Task E (F5) -- 18 people, page-cited (b54c11a)
- [x] **C**: Task F (F5) -- 191 acceptances, 39 PDFs (f76372f)
- [x] **C**: Task G (F5) -- 544 pages, eqc-models 0.21.0 (508a14d)
- [x] **C**: Task H (F5) -- 52 site + 108 author records (b880e76, b6f7636)
- [x] **C**: Task I (F28) -- design and pilot, 3 learnings (0de4a48)
- [x] **H+C**: Manual Validation Q1-Q9 decided and applied (b130786, 3d929e5, 4ca65c2)
- [x] **H+C**: Retrospective, 16 x 4, improvements 1-8 applied (d735f6f, 5be2402)
