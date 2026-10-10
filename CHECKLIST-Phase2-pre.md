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

- [x] **C**: Task A -- repository on GitHub, private; seeded methodology
      pushed; CI running the five inherited guards
      Evidence (2026-10-03, Sprint 6 Task B): 8aea01d, f5f2177; `.github/workflows/ci.yml`; SPRINT_1_SUMMARY.md "Verification"
- [x] **C**: Task B -- SQLite schema for the four record classes, with the
      ADR-0004 spine and class-specific fields
      Evidence (2026-10-03, Sprint 6 Task B): 53f944e; `store/schema.sql`; `tests/test_schema.py`
- [x] **C**: Task C -- deterministic text export, regenerated and committed.
      The export is the artifact; the store is a build output
      Evidence (2026-10-03, Sprint 6 Task B): df6cd31; `store/export.py`; `tests/test_export_currency.py`
- [x] **C**: Task D -- contexts as first-class (`world`, `ml`, `qc`, `qml`,
      `platform:*`, `method`); factored assumptions, not tags
      Evidence (2026-10-03, Sprint 6 Task B): a9a8618; `store/seed_contexts.sql`; `tests/test_contexts.py`
- [ ] **H+C**: Task E -- ingest one paper end to end (the Lenat/Marcus record
      from ADR-0005) and TIME the adjudication. This is the premise falsifier:
      its result can send Task F back to the drawing board before 46 records
      are committed to the schema
      Evidence (2026-10-03, Sprint 6 Task B): the ingest was done (6b8debb, 10e1c8f). The TIMING was NOT done in Sprint 1: the team lead deferred it (SPRINT_1_PLAN.md "AMENDED 2026-09-16"; 10e1c8f "defer adjudication-time measurement to F75"); first measured in Sprint 4 as F11 (3105b0c, 1.08 min per record, confirm mode). Left unchecked: the row as written was not met in Sprint 1.
- [x] **H+C**: Task F -- load the 46-paper seed set at `seen` tier; promote a
      VARIETY of ~20 to `screened`
      Evidence (2026-10-03, Sprint 6 Task B): 549ff56, e0f4418; SPRINT_1_SUMMARY.md: 44 distinct records (2 exact duplicates), 17 promoted to `screened`
- [x] **C**: Task G -- determinate-fact resolvers, at minimum the consumer
      repository's amendment count, computed rather than stored
      Evidence (2026-10-03, Sprint 6 Task B): 00e66c4; `store/resolvers.py`; `tests/test_resolvers.py`
- [ ] **H+C**: Adjudication time recorded per record; sprint reports the
      median (Definition of Done, SPRINT_1_PLAN.md)
      Evidence (2026-10-03, Sprint 6 Task B): NOT done in Sprint 1 (SPRINT_1_SUMMARY.md "Measurement Sprint 1 did NOT produce"). Delivered in Sprint 4: 18 records, median 1.0 min, range 0.6-1.8 (3105b0c; `docs/sprints/SPRINT_4_F11_TIMING_LOG.json`). Left unchecked for Sprint 1.
- [x] **H+C**: Task H (F1, added 2026-09-15) -- hsbc-quantum-fraud-2026 process
      content scanned, classified KEEP/REWRITE/DELETE, and the classification
      reviewed by the team lead BEFORE any edit is applied
      Evidence (2026-10-03, Sprint 6 Task B): attested in SPRINT_1_SUMMARY.md "Verification" and SPRINT_1_RETROSPECTIVE.md; no standalone classification document exists
- [x] **C**: Task H -- approved classification applied across the affected
      files
      Evidence (2026-10-03, Sprint 6 Task B): 58eb7fa, 44068d9, bb78283, 70fb842
- [x] **C**: Task H -- regression test committed that fails if a disallowed
      pattern (Dirac-3, `experiments/src`, `results.json`, `prereg-freeze`,
      etc.) reappears outside an allow-listed historical/provenance context,
      verified by injection before trusting it
      Evidence (2026-10-03, Sprint 6 Task B): 70fb842; `tests/test_no_source_repository_process_leakage.py`

## Standing constraints (apply to every sprint, not only Sprint 1)

- [ ] **C**: `--no-verify` never used; the five inherited hooks stay active
      and registered (verified by `tests/test_hook_registration.py`)
      Evidence (2026-10-03, Sprint 6 Task B): hooks registered and tested (`tests/test_hook_registration.py`, now 12 hook files). "Never used" cannot be proven from git history; left unchecked as unprovable, not as violated.
- [x] **C**: Every assertion in the store carries provenance; a record that
      cannot say where its value came from is treated as a defect, not an
      omission
      Evidence (2026-10-03, Sprint 6 Task B): `records.provenance TEXT NOT NULL` (`store/schema.sql` line 52): a record without provenance cannot be written
- [x] **C**: Determinate facts resolve rather than being stored (CLAUDE.md
      standing rule)
      Evidence (2026-10-03, Sprint 6 Task B): 00e66c4 (`store/resolvers.py`); `scripts/learnings.py` (Sprint 5) computes and stores nothing
- [ ] **H+C**: Reading-level escalation tracked one grade at a time from 8
      toward the PhD ceiling; a cluster at 17+ is logged as a finding about
      the source document
      Evidence (2026-10-03, Sprint 6 Task B): NOT VERIFIABLE: `reading_level` is populated (values 11 and 13), but no document tracks the escalation or logs a 17+ cluster. Left unchecked.

## Design-document checkpoint (both ADRs, six questions each)

- [x] **H+C**: After roughly 20 papers are loaded (Task F above), review
      ADR-0004 and ADR-0005 against what actually happened. Record findings as
      dated amendments at the bottom of each ADR, never as silent edits
      Evidence (2026-10-03, Sprint 6 Task B): done in Sprint 2 Task E, not Sprint 1: d6cb846 (ADR-0004 A4, ADR-0005 A1); b7724e3 (point-in-time qualifiers)

---

## Sprints 2 to 4 (back-filled 2026-10-03, Sprint 6 Task B, F38)

Rows written after the fact from each sprint's plan and summary; every
commit cited was confirmed to exist with `git cat-file`.

- [x] **C**: Sprint 2 Task A (F4 part 1) -- 0eaa705
- [x] **C**: Sprint 2 Task B (F4 part 2) -- 14b57b5
- [x] **C**: Sprint 2 Task C (F4 part 3, QBoost added) -- 3fd7f4c
- [x] **C**: Sprint 2 Task D (F76 vocabulary guard) -- 4b81c2c
- [x] **C**: Sprint 2 Task E (F75 ADR checkpoint) -- d6cb846
- [ ] **H+C**: Sprint 2 Task F (F75 adjudication measurement) -- NOT run; replaced by F7-F11 (a312da9), delivered in Sprint 3 (F7-F10) and Sprint 4 (F11, 3105b0c)
- [x] **C**: Sprint 2 Task G (F3 `view.py`) -- ed13474
- [x] **C**: Sprint 3 Task A (F2 survey) -- d6b8834
- [x] **C**: Sprint 3 Task B (F6 findings) -- c81d628
- [x] **C**: Sprint 3 Task C (F13 US English guard) -- 71063fc
- [x] **C**: Sprint 3 Task D (F14 hardening) -- c0baa44
- [x] **C**: Sprint 3 Tasks E-H (F7-F10 independent reviews) -- 38b5360
- [x] **C**: Sprint 4 Task A (F27) -- 77806d4
- [x] **C**: Sprint 4 Task B (the door) -- 95e8807
- [x] **C**: Sprint 4 Task C (corrections) -- 7f1109f
- [x] **C**: Sprint 4 Task D (F26 batched export) -- cf82289
- [x] **H+C**: Sprint 4 Task E (F11 timing) -- 3105b0c
- [x] **C**: Sprint 4 Task F (re-filing) -- 72cdbf8
- [x] **C**: Sprint 4 Task G (intake workflow) -- 64d067f
- [x] **C**: Sprint 4 Task H (five papers to read) -- 847ddd6
- [x] **C**: Sprint 4 Task I (hook family) -- 904bda7
- [x] **C**: Sprint 4 Task J (skill) -- 6e7406e
- [x] **C**: Sprint 4 Task K (heuristics file) -- aba1310

## Sprint 5: Make the Store Durable, Then Fill It (reconciled 2026-09-25 at Phase 7)

**Drift found at this reconciliation**: the Sprint 1 rows above were never
checked off, and Sprints 2 to 4 had no section here, although all four
sprints closed with their docs triads. Back-filled with per-row evidence on
2026-10-03 (Sprint 6 Task B, F38). Evidence for each Sprint 5 row is the commit named.

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

## Sprint 6: Decide the Fields Once, Then Load at Scale (reconciled 2026-10-05 at Phase 7)

Evidence for each row is the commit named; every hash was checked with
`git cat-file` at this reconciliation.

- [x] **C**: Task A (F40) -- model tiers verified, test proven by injection (b7cde4d)
- [x] **C**: Task B (F38) -- checklist back-filled for Sprints 1 to 4 (d35d945)
- [x] **C**: Task C (F43) -- INTAKE_WORKFLOW section 15 (efadb67)
- [x] **H+C**: Task D -- ADR-0004 A6 and ADR-0005 A4 written (745af25, 1ffb5df, 26f26d9), accepted at Manual Validation
- [x] **C**: Task E -- migration, byte-identical round trip (7b63965); review fixes (3708e63)
- [x] **C**: Task F (F36) -- stored back-fill (3708e63); computed probes (32a6deb)
- [x] **C**: Task G (F41) -- 11 sources, 35 assertions, CVQBoost part held as F51 (32a6deb)
- [x] **C**: Task H (F42) -- the two Cyc research documents and the amendment (39b179e)
- [x] **C**: Task I (F33) -- six withdrawn, one retracted, two superseded-by links (5478880)
- [x] **C**: Task J (F32) -- 1,402 of 1,403 loaded (aca2be1, cfeb485)
- [x] **C**: Task K (F35) -- 105 of 135 notes linked, 30 reported (90784bf, 95f35c3, cfeb485)
- [x] **C**: Task L -- du-2024 refreshed (dff3595)
- [x] **C**: Phase 5 fresh-eyes review findings fixed (34893bb)
- [x] **H+C**: Manual Validation Q1-Q10 decided and applied (fdc8532, 3cbadae, e841545)
- [x] **H+C**: Retrospective, 16 x 4, improvements I1-I6 applied (498f53c, f58f5d2, 4ea7e6b, eeb2e46)

## Sprint 7: Move the Data Out, Then Measure arXiv Safely (reconciled 2026-10-10 at Phase 7)

Evidence for each row is the commit named.

- [x] **C**: Task A (F59) -- model tiers re-verified, Developers to Sonnet 5.5 (b5fdf01)
- [x] **H+C**: Task B (F58) -- ADR-0004 A7, ADR-0003 A2, ADR-0005 A5 (3bf2eda); store out of the repository, export retired (65a048e); review fixes (d0b837d); accepted at Manual Validation
- [x] **C**: Task C (F52) -- cap, pacing, page fallback (60f831a, f360e04, 3200be3); bulk run measured in ADR-0005 A6 (5a2dac1)
- [x] **C**: Task D (F53) -- `--stale` and `--refresh` (0e7e2e7); per-cycle run replaced by a 12-month re-check (89accb9)
- [x] **C**: Task E (F54) -- notes linked (de3caa5, 8fe2fd5, c0d321b)
- [x] **C**: Task F (F44) -- eight Cycorp papers, T07's two assertions (2a27964)
- [x] **C**: Task G (F45) -- Dirac-3 reading pass, 14 assertions (a4eeeea)
- [x] **C**: Phase 5 I4 re-read, ADR-0004 A7 matched to the code (de4e487)
- [x] **H+C**: Manual Validation Q9, Q12-Q20 decided and applied (b8f3bca, 89accb9)
- [x] **H+C**: Retrospective, 16 x 4 (f403121), improvements I1-I7 applied (0747a9b; I6's status format in the commit after cf6f5e4)
