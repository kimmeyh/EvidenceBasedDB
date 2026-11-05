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

## Sprint 8: Read QCi's Newest Guide, Then Build the Yearly Re-check (reconciled 2026-10-13 at Phase 7)

Evidence for each row is the commit named.

- [x] **H+C**: Task A (F66) -- develop as the default branch, `sprint-N` tags, ADR-0001 A2 (abadd7a, PR #84)
- [x] **C**: Task B (F67) -- Haiku 5.5 as the haiku tier (4923cf9)
- [x] **H+C**: Task C (F65 with F63) -- Dirac-3S guide, ADR-0004 A8 (0a9655f); review fixes (1e02aba); Q7 upgrades (56c6950)
- [x] **H+C**: Task D (F64) -- staggered re-check, ADR-0005 A7 (d0d9c93); review fixes (e8530e3); `--due` lists only, ADR-0005 A8 (3dde5ef)
- [x] **C**: Task E (F60) -- manifest check (d43822d); report corrected at Manual Validation (88f2c7a)
- [x] **C**: Task F (F61) -- Massoli list (15b7e90)
- [x] **C**: Task G (F71, added at Phase 7) -- Dirac-3S release, benchmarking review, product page, site diff (899afaa)
- [x] **H+C**: Manual Validation Q1-Q8 decided and applied (88f2c7a, abadd7a, 56c6950)
- [x] **H+C**: Retrospective, 16 x 4 (0182581), improvements I1-I6 applied (ec4da7b, 3bd964f, 204d228, 3dde5ef, 6a260ce, 08b0751), review fixes (91f508b, 301ea4c)
- [x] **H**: The stored QPU-seconds balance removed (7e04efa)

## Sprint 9: Read the Ceiling Papers, Then Open the Phase 2 Exchange (back-filled 2026-10-18 at Sprint 10 Phase 2)

Not reconciled at Sprint 9's Phase 7, and Sprint 10's Phase 1.2 sweep
missed the gap; found when this file was walked at Sprint 10 Phase 2.
Evidence for each row is the commit named, each on develop
(`git log origin/develop --grep "#N"`).

- [x] **C**: Task A (F79) -- Phase 2 exchange, guard, inbound path, outbound prompt (8c30fe6); review fixes (2b90897, a996f83, 38c256f)
- [x] **C**: Task B (F68, F69) -- old-style arXiv ids, parenthesized DOIs, Massoli and Wiebe (070137e)
- [x] **C**: Task C (F74) -- ADR-0005 A9 (9f7e5fa)
- [x] **C**: Task D (F48) -- SHA-256 and the local source check (7006739)
- [x] **C**: Task E (F78) -- downloads and clones (44a8383); group read (801f234); answer document (b413fc4); review fixes (d14520a); closed papers after Manual Validation (8b6c8ca)
- [x] **C**: Task F (F46) -- 20 pending facts dispositioned (cec5732)
- [x] **C**: Task G (F80) -- slice selected (a4ec09c); read (9f71f19); review fixes (9d5b4c9)
- [x] **C**: Task H (F55) -- cites links, ADR-0005 A10 (4c997a1, daf1fa8)
- [x] **C**: Task I (F56) -- corroborated flag, ADR-0004 A9 (79ae0d4); review fixes (9fa268a, 53a0be0)
- [x] **C**: Task J (F62) -- discovery and hand-download list (ea79e0e); review fixes (360bec4)
- [x] **C**: Task K (F51) -- hold checked, stays HOLD (d283dfe)
- [x] **C**: CI red from 2026-10-15 fixed (deb726d); Copilot finding fixed (52a439a)
- [x] **H+C**: Manual Validation Q1-Q6 decided and applied (4530b35, 8b6c8ca)
- [x] **H+C**: Retrospective, 16 x 4 (fdd8018), improvements I1, I3, I4, I5 applied (202478f, 3a455ce, 8c94ef4), I7 applied (d54d2c0, 47cbdc1); I2 and I6 skipped (team lead)
- [x] **C**: Post-hand-over review fixes (7a0d32d)

## Sprint 10: Fix the Hooks and the Dirac Records, Then Read the Next 74 (back-filled 2026-10-21 at Sprint 11 Phase 1.2)

Not reconciled at Sprint 10's Phase 7 (retrospective step 7 names it; it
was missed); found by Sprint 11's Phase 1.2 sweep. Evidence for each row is
the commit named, each on develop (`git log origin/develop --grep "#N"`).

- [x] **C**: Task A (F81) -- code-edit hook cuts at the editor's own command (021d2a8); review and three security-review fixes (10f7741, 6690c39, f1cb0bc)
- [x] **C**: Task B (F88, F39 release) -- models verified, Sprint 9 reader rows, reader_inference rule (1c57ecd)
- [x] **C**: Task C (F50) -- Cyc's stored counts qualify point 7 (69be67c)
- [x] **C**: Task D (F86) -- DOI probe asks DataCite; Zenodo answered (250ede3); review fix (c634d00)
- [x] **C**: Task E (F82) -- never-write hook, git options per subcommand (6cd9002); review and security fixes (6c37e83, 08f5510, d4d664c); `--ext-diff`/`--textconv` unblocked (changed commitment, disclosed)
- [x] **C**: Task F (F84) -- ADR-0004 A10 platform:dirac-1, nine records, 12 assertions (9781f9f); review fix and A10 correction (826a189)
- [x] **C**: Task G (F85) -- Phase 2's Dirac-3S verification, four assertions (7ddc2e1); review fix (596a1dc)
- [x] **C**: Task H (F83) -- per-instance optimization bounds (15846d1); review fix and intake rule 26 applied to F, G, H (0a366e2)
- [x] **C**: Task I (F89) -- slice (11744c1); copies (bae11ed); 64 read, 216 assertions (cc4d5c0); review fixes (3af3fd9); 8 with no free copy carded as F90 (9648c6d)
- [x] **C**: Task J (F87) -- discovery filters (fb5c0ba); review fixes (3af3fd9); live re-run (672e982); 91 entered at seen (e45c1c3)
- [x] **H+C**: Manual Validation Q1-Q6 decided and applied (c0e8c22, 672e982, e45c1c3); step 5 moved to Sprint 11 as F90
- [x] **H+C**: Retrospective, 16 x 4 (9648c6d); I1 and I2 applied (74049f0) with review fixes (b45b2b5); I3 skipped (team lead)
- [x] **C**: Summary and master plan roll (d0a1791); Copilot finding fixed (2c2e1b9); PR #101 ready (75f9ada)

## Sprint 11: Enter QCi's Answers, Then Read 200 Records and Every New Paper (reconciled 2026-10-23 at Phase 7.7)

Evidence for each row is the commit named, on the sprint branch
(`feature/20261021_Sprint_11`, PR #113).

- [x] **C**: Task A (F99, F39 release) -- models unchanged; Sprint 10 outcomes; parallel-reader pattern (a95b1a0)
- [x] **C**: Task B (F94) -- backlog cards adopt spamfilter-multi's practices (462cc15)
- [x] **C**: Tasks C, D, E (F92, F93, F91) -- QCi answers, F108 ceiling, magic state cultivation (a56b702)
- [x] **C**: Tasks F and G (F97, F96) -- slice and copies (ffd68c7); read ledger (729e8c8); new papers entered and read, 200-record slice read (874527c)
- [x] **H+C**: Manual Validation Q1-Q3 decided and applied (ae29cc1, bed6746); F100 carded (1844986)
- [x] **H+C**: Retrospective, 16 x 4 (bed6746, a87112a); I1a, I1b, I2 applied (bc658b1) with a security fix (9046f08); I3 carded, I4 applied, I5 skipped (7db1e84)
- [x] **C**: Summary, master plan roll and this section (this commit); Copilot review waived by the team lead; PR #113 ready

## Sprint 12: Fix the Entities, Speed the Suite, Then Read 400 Records (back-filled 2026-10-31 at Sprint 14 Phase 7.7)

Not reconciled at Sprint 12's or Sprint 13's Phase 7, and neither Phase 1.2
sweep caught it; found when this file was walked at Sprint 14 Phase 7.7.
Evidence for each row is the commit named, on `feature/20261023_Sprint_12`
(PR #122).

- [x] **C**: Task A (F101) -- HTML entities out of the store; every stored quote parses (5466953); review fixes (6d2bed4, 4c109e7)
- [x] **C**: Task B (F100) -- the suite in 199 s warm, from 781 s (fdedff9); review fixes (536e0f1)
- [x] **C**: Task C (F102) -- Phase 2's Sprint 28 results by the inbound path (5bcafe0); F111 entered, five values corrected (7ff07f5)
- [x] **C**: Task D (F106) -- ADR-0005 A11, a source link resting on a recorded team-lead decision (ffc3c2b)
- [x] **C**: Task E (F103) -- the Classiq challenge posts, wrap-up and named repository (c80c195); review fixes (77beaa0, 9698ead)
- [x] **C**: Task F (F104) -- Roadmap-to-QML's first release (f99139e); review fixes (9698ead)
- [x] **C**: Task G (F105) -- HIGH only with a named basis (e09a244); the slice, fetch and ledger (ce5c222); 413 reads entered (5744e2d); review fixes (eeabd3b)
- [x] **H+C**: Manual Validation (18e9f43)
- [x] **H+C**: Retrospective, 16 x 4, summary (48196d5); I1 and I3 applied, I2 carded on F57 (7b65d12); review fix (90af614)

## Sprint 13: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records (back-filled 2026-10-31 at Sprint 14 Phase 7.7)

Not reconciled at Sprint 13's Phase 7; found with Sprint 12's gap. Evidence
for each row is the commit named, on `feature/20261024_Sprint_13` (PR #131).

- [x] **C**: Task A (F107) -- the ".;" joins out of paper evidence; theoretical LOW grades name their cause (6c6f0ac); review fix (44502b8)
- [x] **C**: Task B (F111, F39 release) -- models unchanged; Sprint 11 and 12 outcomes logged (2599140)
- [x] **C**: Tasks C, D, E (F109, F110, F108) -- Papers and Roadmap checked; Phase 2's F162 entered (88bd065); review fix (c468a90)
- [x] **C**: Task F (F112) -- every LOW names its reason (dd620c7, ac91f2f); the slice and ledger (e621771); half 1 (cec6020, f782e53) and half 2 (ce2412e, 6cfc137) read and applied; anchors (7ea56e7, 84df57e)
- [x] **H+C**: Manual Validation Q2 to Q4 (ed53933, b0b41a3, 6173bad, b6cdcd0, 745c6e6, ce95e82, 8c869cc, 44e2512); Q7 (2bab87b); Q11 to Q13 (71705d8)
- [x] **C**: Task G (F113), added at Manual Validation -- no reading budget (a3b8074); the apply script and g001 to g042 (6d8dec7 to c827018, eb3941a, 5e10948); F114's cloud readers stopped at $0 credit (296863a to d5fe761)
- [x] **H+C**: Retrospective, 16 x 4 (db8aeb7, af2c2ca); I1, I2 and I4 applied, I3 skipped (c978e50, 8a06bf5)
- [x] **C**: Copilot finding fixed (9e7d9fb); summary, master plan roll (83b2e99); PR #131 ready

## Sprint 14: Read PHI-OMEGA, Review the 302 Cloud Reads, Then Learn What the Store Says (reconciled 2026-10-31 at Phase 7.7)

Evidence for each row is the commit named, on the sprint branch
(`feature/20261029_Sprint_14`, PR #140).

- [x] **C**: Task A (F119) -- PHI-OMEGA paper, posts, images and code (1b987dd); review fixes (6d5bcec, f1257c1)
- [x] **C**: Task B (F122, F95 release) -- 165 unnamed PDFs linked (ebff67c)
- [x] **C**: Task C (F123, F98 release) -- Roadmap-to-QML at ea6f42a7c0, 4 papers entered (577380e)
- [x] **C**: Task D (F120) -- Phase 2's Sprint 29 results (1f904ba); review fix (454c7a4)
- [x] **C**: Tasks E and F (F117, F114) -- cloud results rebuilt and reviewed (92d7634 to fed2d56); local reads (1cb63bb to 59233c1); first release applied (b185729, 4d969d9)
- [x] **C**: Task G (F118) -- inventory and theme packets (6400b23); the memo (ed5ab01, 6e4bfb7)
- [x] **H+C**: Manual Validation Q1 = 1 and Q2 = 1; the last 19 groups applied (0eddd23); review fixes (bb82d0a, 25d3985)
- [x] **H+C**: Retrospective, 16 x 4 (b665ee3, 25d3985); all nine improvements option 1: Q1 to Q7 applied, Q8 carded as F130, Q9 added to F128 (this commit)
- [x] **C**: Summary, master plan roll and this section (this commit); PR #140 ready after CI

## Sprint 15: Read Every Page, Figures and Images Included, Then Read 100 More Papers (reconciled 2026-11-05 at Phase 7.7)

Evidence for each row is the commit named, on the sprint branch
(`feature/20261031_Sprint_15`, PR #149).

- [x] **C**: Tasks A and B (F131, F132) -- the F95 and F98 releases find nothing new (53ad17d)
- [x] **C**: Task C (F125) -- re-entry groups (34034bd); review fix (4e75c07)
- [x] **C**: Tasks D to L (F126, F127, F115, F116, F114, F133, F128, F124, F129) -- OCR, the Sprint 15 prompts, the reads and the first apply (d485069); title corrected (ca13887)
- [x] **C**: Task M (F130) -- Phase 2's Sprint 30 results, F166 repointed (84e6aaa)
- [x] **H+C**: Manual Validation Q1 to Q9; the last 24 groups and the decisions applied; team-lead decisions guarded (8c10247)
- [x] **H+C**: Retrospective, 16 x 4 (this commit); improvement Q1 per the team lead's answer
- [x] **C**: Summary, master plan roll and this section (this commit); PR #149 ready after CI
