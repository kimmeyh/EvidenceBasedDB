# Sprint 1 Plan: Build the Store

**Dates**: from 2026-09-14. **No deadline.**
**Branch**: `feature/YYYYMMDD_Sprint_1` (cut at kickoff)
**Scope** (DEFINED, team lead 2026-09-14; extended 2026-09-15 with Task H):
implement the Evidence Based DB and load the seed set (tracked in the consumer
repository as **F77**), and remove misleading hsbc-quantum-fraud-2026 process
content this repository inherited at seeding (**F1**, native to this
repository).

## Objective

Turn two accepted ADRs into something that holds records, and **measure the one
number the whole design is constrained by**: minutes of team-lead adjudication
per accepted record.

## Why this sprint exists at all

ADR-0004 and ADR-0005 are both ACCEPTED and both state explicitly that they do
NOT authorise implementation. The consumer repository's close-out sweep found
that nothing created the thing: the checkpoint card depended on ~20 papers being
loaded, and no card loaded them. This sprint is that gap.

## The measurement that outranks the code

**Record adjudication time per record, from the first one, not retrospectively.**

ADR-0004 names it the number the design is constrained by, and it is unknown. At
five minutes per record, a domain knowledge base over QML, ML and QC is a year of
evenings and the ambition needs rethinking. At thirty seconds it is safe. **We
do not know which, and every other decision in this sprint is cheaper to change
than that one.**

Agent drafting is not the constraint. The team lead's serial attention is.

## Tasks

| # | Task | Est | Owner |
|---|---|---|---|
| A | Repository on GitHub, private; push the seeded methodology; CI running the five inherited guards | 60m | Claude + **team lead** |
| B | SQLite schema for the four record classes, with the ADR-0004 spine and the class-specific fields | 120m | Claude |
| C | Deterministic text export, regenerated and committed. **The export is the artifact; the store is a build output** | 90m | Claude |
| D | Contexts as first-class: `world`, `ml`, `qc`, `qml`, `platform:*`, `method`. Factored assumptions, not tags | 90m | Claude |
| E | Ingest one paper end to end -- the Lenat/Marcus record already worked in ADR-0005 -- and time the adjudication | 60m | Claude + **team lead** |
| F | Load the 46-paper seed set at `seen` tier; promote a VARIETY of ~20 to `screened` | 240m | Claude + **team lead** |
| G | Determinate-fact resolvers: at minimum the consumer's amendment count, computed not stored | 60m | Claude |
| H | **F1**: remove hsbc-quantum-fraud-2026 process content this repository does not need (see below) | [no-history] | Claude + **team lead** |

**Sequence**: A first. B and C together, since the export is what makes the
store replaceable. D before F, because contexts must exist before records claim
them. E before F, as a single-record dry run that surfaces schema problems
while they cost one record rather than forty-six. H runs independently of
B-G's data-model work and can happen any time after A; sequenced last here
only so it does not compete for attention with the premise falsifier in E.

**Total ~12 hours** plus Task H (estimate pending its own scoping pass) plus
the standing 30% findings allowance.

### Task H detail: remove hsbc-quantum-fraud-2026 process content (F1)

**Why this is a task and not a quick edit.** This repository was seeded from
`hsbc-quantum-fraud-2026` and correctly carries some of that history (the
CHANGELOG's "seeded from" entry, ADR provenance notes). It ALSO carries
inherited process content that is not history but live, misleading
instruction: `SPRINT_EXECUTION_WORKFLOW.md` line 3 calls itself "authoritative
... for hsbc-quantum-fraud-2026"; the same document and
`SPRINT_STOPPING_CRITERIA.md` and `QUALITY_STANDARDS.md` reference
`pytest experiments/src -q`, `results.json`, `prereg-freeze`, and a hard
Dirac-3 metered-hardware-approval rule -- none of which exist or apply here. A
scan on 2026-09-15 for
`hsbc|Quantum Insider|Dirac-3|QCi|IEEE-CIS|SPECTRA|prereg-freeze|experiments/src`
matched 22 files. Removing all of it blindly would delete real provenance
(e.g. "this ADR was moved here from the consumer repository"); keeping all of
it leaves a workflow doc that tells a future session to wait for hardware
approval that will never come. This needs a judgment pass, not a find-replace.

**Sub-steps**:
1. Re-run the scan (the pattern list above; expect drift from Sprint 1's own
   work) and enumerate every hit with its file and line.
2. Classify each hit: **KEEP** (accurate history about this repository's own
   origin), **REWRITE** (a process rule that has a real equivalent here and
   should be restated in this repository's own terms, e.g. "hardware
   override" has no equivalent and should simply be removed, not restated),
   or **DELETE** (applies only to the source repository's own submission
   process and has no equivalent here at all).
3. Present the classification for team-lead review before editing -- this is
   a judgment call across 22 files and a wrong DELETE destroys provenance.
4. Apply the approved classification.
5. Write a test (`tests/test_no_source_repository_process_leakage.py` or
   similar) that fails if one of these patterns reappears outside an
   explicitly allow-listed historical/provenance context, so this does not
   need re-discovering by a future grep.

**Acceptance criteria for Task H**:
- A re-scan of the same pattern set returns only hits classified KEEP
- `SPRINT_EXECUTION_WORKFLOW.md`, `SPRINT_STOPPING_CRITERIA.md`, and
  `QUALITY_STANDARDS.md` contain no Dirac-3, `experiments/src`, or
  `results.json` references presented as this repository's own live rules
- The new test passes on the cleaned tree and fails when a disallowed pattern
  is reintroduced outside the allow-list (verified by injection, per this
  repository's own guard-discipline standard)
- Full test suite still green after the edits

## Premise falsifier

**The premise**: a structured store with provenance beats prose for the claims
this project makes.

**What would disprove it**: if adjudication runs long enough that the seed set
alone consumes the sprint, the design is too heavy for its purpose and the
schema should shrink before it grows. **Measured in task E, before task F
commits to forty-six.**

**The check cannot merely confirm**: E is a single record with a real clock on
it, and its result can send F back to the drawing board.

## Risks

| Risk | Mitigation |
|---|---|
| **Adjudication cost sinks the ambition** | Task E measures it on one record before task F scales to 46 |
| Schema wrong in a way 46 records entrench | E first; the 20-paper checkpoint exists for the rest |
| `Books` and `GitHubRepos` do not fit the paper class | Out of scope this sprint by team-lead decision. Papers only |
| Cross-repository vocabulary drift | Known and carded as F76 in the consumer repo. Not this sprint |
| Building a reasoner by accident | Lenat's footnote 9. Inference, graph store and embeddings are all out of scope and none of their triggers has fired |
| Task H deletes real provenance along with dead process content | Classification reviewed by the team lead before any edit (Task H sub-step 3), not decided unilaterally |
| Task H's own estimate is unknown ahead of the scan | Sized after sub-step 1 enumerates the actual hit count; timeboxed if it runs long, per the anti-pattern rule against uncalibrated estimates |

## Definition of Done

- The repository exists, private, with CI green on the inherited guards
- The four record classes are implemented, and the export regenerates
  deterministically from the store
- One paper is ingested end to end with its assertions separated
- The 46-paper seed set is at `seen`; ~20 chosen for VARIETY are at `screened`
- **Adjudication time is recorded per record**, and the sprint reports the median
- Determinate facts resolve rather than being stored
- Task H's acceptance criteria (above) are all met, with the classification
  reviewed before editing and a regression test committed

## Out of scope

Inference. The graph store. Embeddings. `Books` and `GitHubRepos`. Any change to
the consumer repository. The 8th-grade explanatory document, which is F73 there
and follows this sprint.
