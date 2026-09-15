# Sprint 1 Plan: Build the Store

**Dates**: from 2026-09-14. **No deadline.**
**Branch**: `feature/YYYYMMDD_Sprint_1` (cut at kickoff)
**Scope** (DEFINED, team lead 2026-09-14): implement the Evidence Based DB and
load the seed set. Tracked in the consumer repository as **F77**.

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

**Sequence**: A first. B and C together, since the export is what makes the
store replaceable. D before F, because contexts must exist before records claim
them. E before F, as a single-record dry run that surfaces schema problems
while they cost one record rather than forty-six.

**Total ~12 hours** plus the standing 30% findings allowance.

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

## Definition of Done

- The repository exists, private, with CI green on the inherited guards
- The four record classes are implemented, and the export regenerates
  deterministically from the store
- One paper is ingested end to end with its assertions separated
- The 46-paper seed set is at `seen`; ~20 chosen for VARIETY are at `screened`
- **Adjudication time is recorded per record**, and the sprint reports the median
- Determinate facts resolve rather than being stored

## Out of scope

Inference. The graph store. Embeddings. `Books` and `GitHubRepos`. Any change to
the consumer repository. The 8th-grade explanatory document, which is F73 there
and follows this sprint.
