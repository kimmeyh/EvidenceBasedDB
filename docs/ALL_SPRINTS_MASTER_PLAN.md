# All Sprints Master Plan

Created 2026-09-15, structure adapted from hsbc-quantum-fraud-2026's
ALL_SPRINTS_MASTER_PLAN.md (itself adapted from spamfilter-multi). This
document is IN THE REPOSITORY and persists across conversations. Read it
before every sprint (Phase 1/2), update it after every sprint (Phase 7.7/8.2).

**Nothing below is carried from either source repository's history.** This
repository's own sprint count starts at 1. F77 is the one item that crosses
the boundary: it is the consumer repository's own backlog number for "build
the Evidence Based DB," recorded there and tracked here as the reason this
repository exists. No other F# from either source repository applies here.

## Maintenance Guide

- **After each sprint (Phase 7.7 / 8.2)**: update "Last Completed Sprint"; add
  the sprint's row to "Past Sprint Summary" once its SUMMARY doc exists; prune
  shipped items from "Next Sprint Candidates"; add retro Category-14 items
  with new F#s.
- **During Sprint N+1 planning (Phase 3.2.1)**: create
  `docs/sprints/SPRINT_N_SUMMARY.md` for the just-finished sprint and link it
  here.
- **IDs**: F# for all features/process/tech-debt items native to this
  repository, starting at F1; next available number; never reuse. A number
  quoted from the consumer repository (F77 and any future cross-reference)
  keeps that repository's number and is never renumbered into this
  repository's sequence.
- **Estimates**: minutes/hours from recorded actuals; `[no-history]` where
  uncalibrated. This repository has no recorded actuals yet; every Sprint 1
  estimate is `[no-history]` by construction.
- `CHECKLIST-Phase2-pre.md` is the LIVE deliverable ledger; this document is
  the sprint-scoping view over it. Keep them consistent; the checklist wins on
  deliverable truth, this file wins on sprint sequencing.

## Past Sprint Summary

| Sprint | Summary doc | Status | Duration |
|---|---|---|---|

None yet. Sprint 1 is in flight; its row is added here once
`docs/sprints/SPRINT_1_SUMMARY.md` exists (created during Sprint 2 planning,
per the three-doc rule).

## Last Completed Sprint

None. This repository has completed zero sprints.

## Current sprint

**Sprint 1: Build the Store** (from 2026-09-14, no deadline). Scope defined by
the team lead 2026-09-14, tracked in the consumer repository as **F77**: turn
ADR-0004 and ADR-0005 into a working store, load the 46-paper seed set, and
measure record-adjudication time per record before scaling past one record.
Full detail: `docs/sprints/SPRINT_1_PLAN.md`.

## Next Sprint Candidates

Populated 2026-09-15 from the consumer repository's own backlog (F75, F76 --
both carried here verbatim, both gated on this repository's own F77 work) plus
one item native to this repository (F1, added this date).

**F1. Remove HSBC / Quantum Insider references from this repository (~unknown, no-history) Priority 5**
- Phase: Sprint 1 (added mid-refinement 2026-09-15) or Sprint 2, team lead's call at kickoff
- Platform: N/A -- documentation and process files only
- This repository was seeded from `hsbc-quantum-fraud-2026` and correctly
  carries some of that provenance as history (e.g. CHANGELOG's "seeded from"
  entry, this document's own header). It ALSO carries inherited process
  content that is not history but active, misleading instruction: a hard
  Dirac-3 metered-hardware-approval rule, `pytest experiments/src -q` as a
  gate command, `results.json` and `prereg-freeze` as governing artifacts, and
  `SPRINT_EXECUTION_WORKFLOW.md` line 3 naming itself "authoritative... for
  hsbc-quantum-fraud-2026" rather than for this repository
- 22 files currently match a scan for `hsbc|Quantum Insider|Dirac-3|QCi|
  IEEE-CIS|SPECTRA|prereg-freeze|experiments/src` (2026-09-15 count; re-scan
  before carding, this list will have moved). Every hit needs a decision, not
  a blanket removal: some are accurate, load-bearing provenance ("this ADR was
  moved here from the consumer repository") and must stay
- **Scope of the card, not this refinement pass**: enumerate every match,
  classify each as KEEP (accurate history), REWRITE (process rule that must be
  restated in this repository's own terms), or DELETE (applies only to the
  source repository's hardware/submission process and has no equivalent
  here); get the classification reviewed before editing, since this is a
  judgment call across 22 files and a wrong DELETE loses real provenance
- Acceptance criteria (drafted here, to be sharpened into a real sprint card):
  a re-scan of the same pattern set returns only KEEP-classified hits; every
  KEEP hit is provenance about this repository's own history, not live
  instruction; `SPRINT_EXECUTION_WORKFLOW.md`, `SPRINT_STOPPING_CRITERIA.md`
  and `QUALITY_STANDARDS.md` contain no Dirac-3, `experiments/src`, or
  `results.json` references presented as this repository's own rules; a test
  exists that fails if one of these patterns is reintroduced outside an
  explicitly allow-listed historical/provenance context
- Depends on: nothing technical; needs a decision on whether it runs inside
  Sprint 1 (before Task A's "CI running the five inherited guards" line is
  read as settled) or as Sprint 2's first item

**F75. Action the 20-paper ADR checkpoint (~2h) Priority 6**
- Phase: Evidence Based DB / process (carried from the consumer repository's
  Sprint 14 retrospective improvement 5, 2026-09-14)
- Platform: `docs/adr/0004-evidence-based-db.md`, `0005-reference-library.md`
- Both ADRs promise a review at approximately 20 imported papers, with six
  named questions and the bad answer stated for each. A promise in a document
  is exactly what this project keeps having to replace with a mechanism, and
  an unactioned checkpoint is a note nobody reads
- The question that matters most is the measured one: how long team-lead
  adjudication takes per paper. At five minutes, 2,000 papers is 160 hours and
  the design needs rethinking; at thirty seconds the ambition is safe.
  Everything else in the checkpoint is schema tuning
- Revisions are recorded as dated amendments at the bottom of each ADR, never
  as edits in place
- Depends on: this repository's own F77 work (Sprint 1) and ~20 papers loaded
  (Sprint 1 Task F)

**F76. Guard the shared vocabulary between ADR-0004 and ADR-0005 (~1h) Priority 7**
- Phase: Evidence Based DB / tooling (carried from the consumer repository's
  Sprint 14 retrospective improvement 6, 2026-09-14)
- Platform: this repository
- ADR-0005's `applicability` field points at ADR-0004's context list rather
  than carrying its own enumeration. That was the right call -- two lists
  naming the same things is how the consumer repository's B1 variable count
  came to read differently across documents -- but nothing enforces that they
  agree
- Needs a test that fails when a record names a context the schema does not
  define, and when the ADRs' stated context lists diverge from the database's
- Depends on: this repository's own F77 work (Sprint 1)

### Out of scope, not yet candidates

- Inference, the graph store, and embeddings (explicitly out of scope per
  Lenat's footnote 9 -- none of their triggers has fired)
- `Books` and `GitHubRepos` record classes (paper records only this sprint)
- The 8th-grade explanatory document (F73 in the consumer repository;
  sequenced after this repository's own F77 work so its contents can be
  validated against the store)

## Design documents governing this repository

- `docs/adr/0004-evidence-based-db.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- `docs/adr/0005-reference-library.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- Both carry a six-question review due after roughly 20 papers are loaded.
  Revisions land as dated amendments at the bottom of each ADR, never as
  silent edits.
