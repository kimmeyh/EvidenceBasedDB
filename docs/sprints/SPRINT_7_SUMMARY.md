# Sprint 7 Summary: Move the Data Out, Then Measure arXiv Safely

**Dates**: 2026-10-06 to 2026-10-10. **Branch**: `feature/20261006_Sprint_7`.
**PR**: #68. **Issues**: #69 to #75 (Tasks A to G), all closed. Sources: the
plan (`SPRINT_7_PLAN.md`), `git log`, the issues, the retrospective
(`SPRINT_7_RETROSPECTIVE.md`). Every count below is a snapshot as of
2026-10-10.

## What shipped

- **F59 (Task A, #69).** Model tiers re-verified against Anthropic's models
  page; the Developers tier moved to Sonnet 5.5.
- **F58 (Task B, #70).** The store and its backups moved to
  `D:\Data\Harold\EvidenceBasedDB\store` (override `EBDB_STORE_DIR`); the
  committed export retired (Q1 = 2); real-data tests marked `live_store`,
  run locally and deselected in CI. ADR-0004 A7, ADR-0003 A2 and ADR-0005
  A5, all approved at Manual Validation. A fresh-eyes review found the
  Windows path used off Windows and post-write export calls; both fixed.
- **F52 (Task C, #71).** arXiv requests 18 s apart, a 240-request session
  cap with 2-hour pauses, the abstract page as the fallback source. Bulk
  run: 1,524 records in 12 sessions, 36 hours, 0 errors, no refusal.
- **F53 (Task D, #72).** `--refresh` and `--stale` built. Running them each
  cycle was not adopted (Manual Validation Q12, below).
- **F54 (Task E, #73).** The 30 unlinked repository notes linked or
  re-reported; arXiv:2108.00131 (the mislabeled QMLPapers file) entered;
  F35's screened candidates linked.
- **F44 (Task F, #74).** The eight Cycorp papers in `Papers\` with local
  path and SHA-256; T07 read in full; two assertions.
- **F45 (Task G, #75).** Seven Dirac-3 sources read and promoted; 14
  assertions; all 25 quotes with a local copy verified verbatim by test.
- **ADR-0005 A6.** The probes are built and capped; a record is re-checked
  about every 12 months, not every cycle. Approved at Manual Validation.

Store: 1,875 -> 1,947 papers; 60 -> 76 assertions. Suite: 572 -> 610.

## Manual Validation decisions

- Q9: no priority changes outside the Sprint 7 scope.
- Q12 = 1, Q15 = 2, Q16 = 1, Q18 = 1: re-check each record about every 12
  months on a staggered schedule (24 half-month sections), built in Sprint
  8 as F64.
- Q13: no action on the Dirac-3 949 / 954 level ceiling; 949 stands until
  shown higher.
- Q19 = 1: ADR-0005 A6 approved as revised. Q20: the per-cycle refresh is
  replaced by A6 and F64; the stored probe results are kept.
- New cards: F63 (two Dirac-3 admissions in arXiv:2407.04512), F64, and
  F65 (the Dirac-3S, target Sprint 8; added in Phase 7).

## Actuals

Wall clock is commit-to-commit from `git log` (local time). Plan estimate:
about 705 Claude-side minutes plus Task C's runtime (planned 5.8 hours).

- Plan approved and recorded 2026-10-06 20:28 (b9ce2ca).
- A: 20:30 (2 min after approval). B: 20:35 to 21:08, with its review fixes
  (about 40 min; est 210). C's code and D: 21:08 to 21:36 (D 4 min; est 60).
  E: 21:36 to 22:55 across three commits, with the F61 and F62 cards in
  between (about 80 min; est 60).
- Task C runtime: 2026-10-06 21:36 to 2026-10-08 09:49, **36 hours**,
  against the plan's 5.8. The plan's figure assumed one request per paper
  at 15 s; the approved Q5 = 1 (API plus page, two requests) and Q7 (18 s)
  were not carried back into it (retrospective I1, I2).
- F: 09:54 to 10:09 on 2026-10-08 (15 min; est 90). G: 10:09 to 10:27 (18
  min; est 120). Both are lower bounds: work before a commit is invisible
  to `git log` (retrospective I7 records task start times from Sprint 8).
- Phase 5 and the hand-over: 10:27 to 10:32. Manual Validation: 2026-10-08
  18:36 to 2026-10-09 08:28. Retrospective: 2026-10-09 to 2026-10-10.
- Delegated agents: fresh-eyes reviews on Tasks B and C, read-only; every
  finding verified before it was fixed.

## Findings surfaced

- The arXiv API gave no answer from about 20:00 on 2026-10-07 to 00:33 on
  2026-10-08; the abstract page answered all 107 papers in that window.
- The arXiv API carries affiliations for about 1% of papers (13 of 1,301).
- F-301's "80 percent" for Dirac-3 is not in the critique paper; F-302's
  122% gap includes about 24% from the QUBO formulation.
- The Dirac-3 User Guide's 949 is a variable count; QCi's eqc-direct docs
  give at most 954 levels. No action (Q13).
- The re-probe of the 107 page-answered records, promised during Task C,
  was dropped after measuring the 1% yield and disclosed only at Manual
  Validation (retrospective I4).

## Verification

- Suite 610 passed at every commit from Phase 5 on, including the
  `live_store` tests; CI green.
- `gh issue list --label sprint --state open`: empty.
