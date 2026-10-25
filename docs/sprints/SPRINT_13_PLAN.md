# Sprint 13 Plan: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records

**Dates**: from 2026-10-25. **No deadline.**
**Branch**: `feature/20261024_Sprint_13` (cut at the Phase 6.6 carry-forward
from Sprint 12's branch, 2026-10-24, after PR #122 merged to develop and PR
#130 to main)
**Scope** (DEFINED, team lead 2026-10-25): F107, F98, F95, F108, F39 and
F57 at 800 records. F39, F57, F95 and F98 are permanent, so each is
released as a copy with the next free number: F109 (F95 release for Sprint
13), F110 (F98 release), F111 (F39 release) and F112 (F57 release, 800
records). F90 is put on HOLD ("Can put this one on HOLD for now"); F51
stays HOLD.

## Objective

Correct the two stored defects Sprint 12 found, and bring Phase 2's later
Sprint 28 work into the store. Check the models before the largest read so
far is assigned to them. Then read 800 records, nearly every unread `qml`
record, by up to five agents from one ledger, with every LOW grade naming
its own reason.

## Tasks

Est is coordinator time for the judgment steps, at the cards' estimates.
Sprint 12's `## Actuals`: 990 estimated minutes ran in about 236 active
minutes (about 24 percent); Sprint 11 ran at about 28 percent. Reviews set
the end of the reading task, so it carries its quote checks in its
estimate, and each task that changes `store/`, `scripts/` or a hook
carries one fresh-eyes review and fix cycle. Runtime is separate, with its
dominant term. Models follow `.claude/model_assignment_heuristics.json`, as
Task B leaves it.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F107, two stored defects from Sprint 12.** (1) The ".;" joins: 16 paper records' `evidence`, 1 `paper_reads` detail and 1 `paper_probes` value hold ".;" (pre-flight below); each read first, a join corrected (punctuation only), a ".;" the source prints kept and named. (2) The 3 LOW proved results that store "an empirical result" (INTAKE_WORKFLOW.md section 47; `larson-convergence-proved` is one): each given its own reason, the grade kept LOW. A `live_store` test fails on a ".;" join in those fields, proven by injection; a second apply writes nothing | 35m | none (local store) | Claude, top tier (certainty) |
| B | **F111, the F39 release.** Each tier's model id, version, price, context window and retirement date verified on Anthropic's pages that day; what changed since Sprint 11's release recorded; Sprint 12's outcomes logged (53 Sonnet 5.5 reader groups, 118 values replaced by the coordinator, the reviewer's 1 Critical and 7 Important findings, all on meaning); tiers and task patterns changed only with named evidence; the heuristics test proven to fail by injection. Done before F's readers launch, so their assignment rests on it | 30m | a few minutes: Anthropic's models and pricing pages | Claude, top tier (mandatory: model assignment) |
| C | **F109, the F95 release.** Every PDF in `Papers\` no record names (0 on 2026-10-25; whatever the team lead saves before the task); each matched, entered or given a reason; each entered paper read or kept at `seen` with its reason; counts before and after | 15m | none (local files) | Claude, top tier (certainty) |
| D | **F110, the F98 release.** Roadmap-to-QML's current commit recorded; the diff from a239747648 (no commit since, on 2026-10-25); any new paper matched, entered and read under F57's rules from F's ledger | 10m | one GitHub REST call | Claude, top tier |
| E | **F108, Phase 2's later Sprint 28 work.** Phase 2's documents read at the commit current when the task starts (9993ab6 locally; PR #46 head fefd24b on GitHub, 2026-10-25). F162 entered under `ml` with its limits, related by ADR-0004 A8 (b) to the stored SPECTRA pocket claims (the three B4 assertions and `fourier-wall-incomplete-bar-manufactures-advantage`); each stored value from Phase 2's F111, F114, F151, F153, F154 and F110 compared with its changed document and corrected or confirmed by name | 60m | none (local files) | Claude, top tier (certainty) |
| F | **F112, the F57 release: 800 records** (Q1). First F57's I2 (30m): `store/grading.py` takes a named reason for every LOW (measured result, statement about the field, proved result not checked by the reader), required of new reading scripts by the write-path rule, proven by injection. Then the slice: the 800 most-cited `qml` records at `seen` or `screened` with no read row (OpenAlex counts, F89's rule), leaving out the 24 records earlier slices found no copy for. Read by up to 5 agents from one ledger; each record read and yielding, or kept at `seen` with its reason; the count refreshed | 1330m (1300 for 800 at the card's rate, 30 for I2) | about 4 to 6 hours of reader time in the background: about 100 groups of 8, 5 at once; 32 arXiv PDFs not held locally, serial at 18 s (about 10 min) inside F52's cap; OpenAlex counts in a few requests | Claude, top tier (certainty); up to 5 first-pass readers at the tier B confirms (Sonnet 5.5 today), every quote checked in the write path |

**The read ledger (C, D and F).** One ledger
(`manifests/sprint13_read_ledger.json`) lists every record C, D and F will
read and gives each to exactly one task and one agent group. A test fails
if any record appears twice, and the reading scripts write only the records
their group holds. PDFs are fetched by one serial fetcher, never by the
agents.

**Sequence**: A, then B (the models are checked before any reader is
assigned), then F's I2 and slice, with the fetcher in the background. F's
readers start as soon as the ledger exists; C, D and E run while they read.
F's values are reviewed by two fresh-eyes reviewers, one per half of the
groups, since Sprint 12's single review of 413 records found 1 Critical
and 7 Important problems. Total about 1,480 minutes at the cards'
estimates; at Sprints 11 and 12's ratios, about 355 to 415 active minutes,
plus the reader time in the background. No findings allowance: the scope
is not dominated by verification. **If a Criterion 3 stop becomes
necessary, the cut line is inside F**: F stops at the groups it has
reviewed and the rest return to F57. Deferring approved work is a Class 3
decision and is never made unilaterally.

**Full suite** (team lead, 2026-10-23): twice, before the Manual
Validation hand-over and after any retrospective improvements. Every other
commit runs `python scripts/run_suite.py --changed`, which since Sprint
12's I1 adds the store's tests after any store write.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-10-24): PR #122 merged to develop (0c554bb) and
  PR #130 to main (a3ad99a, tagged `sprint-12`); no open sprint issue;
  working tree clean after the refinement commit 590c79b. Dependency scan
  not applicable (no requirements file; standard library and pytest only).
- **The store (snapshot as of 2026-10-25)**: 2,334 papers (869 `read`, 2
  `screened`, 1,463 `seen`); 2,970 assertions; 1,449 unread with no read
  row; 0 unread under `hsbc-2026` or a Dirac context.
- **F112**: 830 `qml` candidates; 24 left out (no copy in an earlier
  slice), leaving 806. Of the 806, 767 have a local copy, 32 only an arXiv
  id (one paced fetch each), 7 neither. 800 is 99 percent of what is left
  under `qml` (Q1).
- **F107**: ".;" in 16 `paper_fields.evidence`, 1 `paper_reads.detail`, 1
  `paper_probes.value`; 0 in assertion values, provenance, reasons or
  citation contexts.
- **F108**: Phase 2 read locally at 9993ab6 (2026-10-24); GitHub reports
  PR #46 head fefd24b, still draft. Changed since 10086da: F162's document
  (new) and the F111, F114, F151, F153, F154 and F110 documents (Phase
  2's numbers). The 4 stored pocket claims E relates F162 to exist.
- **F110**: Roadmap-to-QML's last commit is a239747648 (2026-10-20), the
  one Sprint 12 recorded.
- **F109**: 180 PDFs in `Papers\`, 0 named by no record.
- **F111**: the heuristics file names Haiku 5.5, Sonnet 5.5, Opus 5.5 and
  Fable 5.1; its learning log ends 2026-10-21.
- **Plan-to-branch verification** (3.2.2.1): no Task A to F artifact
  exists yet; every selected F# is an open card in the master plan; F109
  to F112 are free numbers.

## Questions for approval

**Q1. How many records should F112 read?**
1. All 806 readable `qml` records: the 800 asked for plus the 6 least
   cited. It clears `qml` in one release for about 1 percent more reading
   (one more reader group).
2. 800, exactly as selected. The 6 least-cited `qml` records wait for the
   next release.

Recommend 1

## Premise falsifier

**The premises**: (a) the ".;" joins are join errors, not source text;
(b) the 3 LOW proved results are the only LOW grades with the wrong reason
type; (c) Phase 2's changed documents change at least one stored value;
(d) the 800 most-cited unread `qml` records bear on a context often enough
to yield; (e) the models in the heuristics file are still current.

**What would disprove each**: (a) a ".;" is in its source: it stays and is
named; (b) I2's rule, run over the release, finds others in stored
records: each is reported by name and corrected, or the count is
reported; (c) every compared value still matches: E reports "confirmed by
name", and the card's premise is recorded as wrong; (d) more than half
refused as not bearing on any context: the ranking is reported as wrong,
not hidden; (e) a tier changed or retired: B updates it before F's readers
launch.

**The checks cannot merely confirm**: the join test reads every stored
text field it names; the quote checks run in the write path against text
extracted fresh from each source; each Phase 2 value is compared with the
document's text at a named commit; the ledger test fails on any record in
two groups.

## Risks

| Risk | Mitigation |
|---|---|
| The usage limit stops the session mid-read (Sprint 12: once, at 413 records) | The ledger and the status note make a restart exact; each group's file is its own checkpoint |
| One review misses meaning errors across 800 records | Two fresh-eyes reviewers, one per half; each finding checked against its source before it is fixed |
| Two readers write the same record | One ledger, one group per record; a test fails on a duplicate |
| Five readers multiply arXiv traffic | One serial fetcher at 18 s inside F52's cap; agents read local copies only |
| A reader grades without a basis | HIGH needs a named basis (Sprint 12) and LOW a named reason (I2), both proven by injection |
| A corrected Phase 2 value loses its history | The correction names both commits in the record's reason |
| Phase 2's draft results change after the read | Provenance names the commit; a later change is a later card |
| A team-lead file in `Papers\` is renamed or moved | Never: matching reads names only |
| A closed paper is fetched around its paywall | Never: free copies only; a closed one joins the hand-download list |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| A write reaches a sibling repository | Read only, by local refs and the GitHub API; no fetch inside a sibling repository (the 2026-10-25 slip) |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: 0 ".;" joins left in the named fields (any printed by the source
  named); the 3 reasons corrected; the join test proven by injection; a
  second apply writes nothing
- B: every tier verified on Anthropic's pages that day; Sprint 12's
  outcomes logged; each rule change with its evidence; the heuristics test
  proven by injection
- C: every unnamed PDF handled; counts before and after
- D: the list's commit recorded; every new paper matched, entered or given
  a reason
- E: F162 entered and related; each changed value corrected or confirmed
  by name; a second apply writes nothing
- F: I2's rule proven by injection; the records per Q1 read from the
  ledger, each yielding or kept with its reason; HIGH and LOW grades carry
  their basis; both halves reviewed; the count refreshed; no record in two
  groups
- Full suite before Manual Validation, through `scripts/run_suite.py`;
  every other commit gated on `--changed` and CI's set; CI green on the
  sprint PR before Manual Validation

## Out of scope

F90 (HOLD, team lead 2026-10-25). F51 (HOLD: waiting on the re-run). F57's,
F95's, F98's and F39's later releases, and F57's order after `qml` (asked
when the next release is planned). Downloading any paper around a paywall.
Any write to `hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.
