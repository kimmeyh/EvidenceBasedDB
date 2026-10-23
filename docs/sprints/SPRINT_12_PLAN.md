# Sprint 12 Plan: Fix the Entities, Speed the Suite, Then Read 400 Records

**Dates**: from 2026-10-23. **No deadline.**
**Branch**: `feature/20261023_Sprint_12` (cut at the Phase 6.6 carry-forward
from Sprint 11's branch, 2026-10-23, after PR #113 merged to develop and PR
#121 to main)
**Scope** (DEFINED, team lead 2026-10-23): F101, F95, F98, F100, F102, F57
("Can you do 400 total this sprint") and F51. F57, F95 and F98 are
permanent, so each is released as a copy with the next free number: F103
(F95 release for Sprint 12), F104 (F98 release for Sprint 12, its first)
and F105 (F57 release for Sprint 12, 400 records). F51 is a HOLD card whose
hold condition is not met (pre-flight below); Q2 asks how it runs. F39 and
F90 are not selected.

## Objective

Correct the stored defects Sprint 11 found, then make the test suite fast
enough that its gates stop costing a quarter hour each. Enter Phase 2's
Sprint 28 results, and the CVQBoost findings record. Then read more than
any sprint so far: the Classiq circuit challenge pages, the new papers in
Christophe Pere's list, and the 400 most relevant unread records, by up to
five agents from one ledger.

## Tasks

Est is coordinator time for the judgment steps, at the cards' estimates.
Sprint 11's `## Actuals`: 655 estimated minutes ran in about 181 (about 28
percent); Sprint 10 ran at about 53 percent. Reviews set the end of the
reading tasks, so each reading task carries its quote checks in its
estimate, and each task that changes `store/`, `scripts/` or a hook
carries one fresh-eyes review and fix cycle. Runtime is separate, with its
dominant term. Models follow `.claude/model_assignment_heuristics.json`.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F101, the stored defects Sprint 11 found.** (1) Every stored "&amp;" corrected to "&": the card named Pande 2020; the store holds 4 records with it (pre-flight below), each corrected through the verified write path, the source of the correction (Crossref's escaped text) named in the evidence; record ids are keys and are not renamed (`dunjko-2018-machine-learning-amp-...` keeps its id). (2) `cyc-2007-eight-tactic-types`: the quote re-read in its source past the inner `"split" (`, the value re-checked against the whole quote. (3) A `live_store` test fails on any stored HTML entity, proven by injection. A second apply writes nothing; I1a's stray-quote check finds 0 | 30m | none (local store and one local source) | Claude, top tier (certainty) |
| B | **F100, a faster suite and the targeted runner mode.** (1) One full run through `scripts/run_suite.py` with per-test timings (`--durations=0`), the slowest 30 tests and the total by file recorded with their date; (2) the top items fixed without removing a guard (one store copy per session where a test only reads after writing, extracted PDF text cached across tests, slow tests marked); (3) the targeted mode in `run_suite.py` (team lead's Q2 = 1, 2026-10-23): the changed test files, the tests of each changed script or module, and CI's set, chosen from step (1)'s timings; the workflow's Phase 4 rule names it; (4) the full suite's wall clock before and after. Every guard touched still fails by injection | 90m | about 30 min: two full runs of about 13 min each, plus targeted runs | Claude, top tier (hooks and test design); fresh-eyes review at its commit |
| C | **F102, Phase 2's Sprint 28 results.** Phase 2's `docs/sprints/SPRINT_28_VALIDATION.md` and the result documents it names (F151, F152, F153, F110, F114, F154) read at the commit current when the task starts (10086da at planning, its PR #46 still draft). Each result entered as inbound evidence under `ml` (with `hsbc-2026` where Phase 2's own data is meant), Phase 2's stated limits carried into the values; F151's restatement of F130 and F114's miss related to the store's earlier claims by ADR-0004 A8 (b), `contradicts` only where both cannot hold. F111 (Experiment 4, running on 2026-10-23) entered only if its result is committed by then | 70m | none (local files) | Claude, top tier (certainty) |
| D | **F51, the CVQBoost findings record and its six assertions** (Q2). Q2 = 1: the findings document entered at its current hash (`425358a7b4cec71f...`, "Last updated 2026-08-04"), the record and its six assertions written through the verified write path with provenance naming the version; when the re-run lands, a newer record is linked `superseded-by`. Q2 = 2: no work; F51 stays HOLD | 45m | none | Claude, top tier (certainty) |
| E | **F103, F95 release for Sprint 12.** (1) Every PDF in `Papers\` no record names (0 at planning; whatever the team lead saves before the task); (2) the repository the team lead named, `wangy8205165/Quantum-NeuralNetwork-WhitePaper`, as a GitHub repository record, linked only where a source names it as a paper's code; (3) the Classiq circuit challenge as three web source records under `qc`, as the F95 card states: PoJen Wang's Part 1 (compiler field guide) and Part 2 (depth-95 phase oracle), linked as a series, and Classiq's wrap-up page; Part 2's 19-page PDF the local copy; only each author's own measurements entered, Part 1's survey claims about other work not entered as its own; the "top five" and "first" placings both kept; (4) every entered paper read, or kept at `seen` with its reason; counts before and after | 45m | about 2 min: 3 web pages, one PDF, one GitHub REST call | Claude, top tier (certainty) |
| F | **F104, F98's first release.** Roadmap-to-QML read at its current commit (a239747648 at planning; recorded), the arXiv ids in its year files and `Workforce.md` matched to the store: about 21 of 1,402 are new. Those entered through the door at `seen` and read under F57's rules from the shared ledger; each kept at `seen` with its reason where it cannot be read. The 1,142 already at `seen` stay F57's | 60m | about 15 min: about 21 arXiv metadata and PDF requests, serial at 18 s | Claude, top tier (certainty); Sonnet 5.5 first-pass readers |
| G | **F105, F57 release for Sprint 12: 400 records** (Q1). F57's relevance order: nothing is unread under `hsbc-2026` or a Dirac context, so the release is the 400 most-cited `qml` records at `seen` or `screened` with no read row (OpenAlex counts, F89's rule), leaving out E's and F's records. Sprint 11's I3 first (card text on F57): a shared helper in `store/` grades HIGH only with a basis named per id (setup, scope, definition, proved result, stated limit), and `store/write_path.py`'s rule requires new reading scripts to use it, proven by injection. Read by up to 5 agents in parallel from the ledger; each record read and yielding, or kept at `seen` with its reason; the count refreshed | 680m (650 for 400 at the card's rate, 30 for I3) | about 2 hours: up to about 350 arXiv PDFs not held locally (1,199 of the 1,398 unread `qml` records carry an arXiv id), serial at 18 s inside F52's cap, heartbeat to a file; OpenAlex counts in a few requests | Claude, top tier (certainty); up to 5 Sonnet 5.5 first-pass readers, every quote checked in the write path |

**The read ledger (E, F and G).** Before E starts, one ledger
(`manifests/sprint12_read_ledger.json`) lists every record E, F and G will
read and gives each to exactly one task and one agent group. A test fails
if any record appears twice, and the reading scripts write only the records
their group holds. PDFs are fetched by one serial fetcher, never by the
agents, so five readers never make five arXiv streams.

**Sequence**: A, B, then C and D, then E, F and G together. A first,
because its guard joins the suite B times. B second, so every later commit
gates on the targeted mode. C and D are small and independent. E, F and G
run in parallel from the ledger; G's fetcher starts in the background as
soon as the slice is selected. Total about 1,020 minutes at the cards'
estimates; at Sprints 10 and 11's ratios, about 290 to 540 minutes, plus
about 2.5 hours of runtime, mostly in the background. No findings
allowance: the scope is not dominated by verification. **If a Criterion 3
stop becomes necessary, the cut line is inside G**: G stops at the count
it has reached and the rest returns to F57. Deferring approved work is a
Class 3 decision and is never made unilaterally.

**Full suite** (team lead, 2026-10-23): twice, before the Manual
Validation hand-over and after any retrospective improvements. B's two
timing runs are measurements, not gates. Every other commit runs its
targeted tests plus CI's set.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-10-23): PR #113 merged to develop (21e9550) and
  PR #121 to main (d83a623, tagged `sprint-11`); no open sprint issue; no
  open PR; working tree clean after the refinement commits; CI's set 1,034
  passed at 9564a9d. Dependency scan not applicable (no requirements file;
  standard library and pytest only).
- **The store (snapshot as of 2026-10-23)**: 2,302 papers (455 `read`, 2
  `screened`, 1,845 `seen`); 1,595 assertions; 1,840 unread with no read
  row. Unread by context: `qml` 1,398, `qc` 262, `ml` 121, `world` 41,
  `method` 12, `platform:classiq` 3, `platform:braket` 3; `hsbc-2026` and
  every Dirac context 0. Of the 1,398 `qml`, 1,199 carry an arXiv id and
  31 a DOI.
- **F101**: "&amp;" is stored in 4 records, not 1: the values of
  `jeffery-2024-multidimensional-quantum-walks-recursion-quantum` and
  `dunjko-2018-machine-learning-amp-artificial-intelligence`, and the
  provenance of those two, `pande-2020-bibliometric-survey-quantum-machine-learning`
  and `yang-2023-survey-important-issues-quantum-computing`. The task
  corrects all 4 (the card's defect class, computed, not the one named).
- **F102**: Phase 2 at 10086da on `feature/20261019_Sprint_28`, read only;
  the validation document names each result file. Experiment 4 started
  2026-10-23, about 825 minutes projected.
- **F51**: the hold condition is not met. Two copies hash to
  `425358a7b4cec71f...` and say "Last updated 2026-08-04", unchanged since
  the 2026-10-15 check. The third copy the card names
  (`hsbc-quantum-fraud-2026\fourierwall2\CVQBoost_Findings.md`) is no
  longer present, and that repository's git history holds no file at that
  path. No re-run has rewritten the document.
- **F103**: 151 PDFs in `Papers\`, 0 named by no record. The three
  Classiq-challenge pages answered on 2026-10-23 (WebFetch, read only); no
  GitHub repository is linked from them.
- **F104**: Roadmap-to-QML at a239747648 (last push 2026-10-20): year files
  `2007-2017/` to `2026/` and `Workforce.md`, 1,402 distinct arXiv ids;
  1,381 in the store (1,142 `seen`, 239 `read`).
- **Plan-to-branch verification** (3.2.2.1): no Task A to G artifact exists
  yet; every selected F# is an open card in the master plan; F103, F104 and
  F105 are free numbers.

## Decisions (for approval)

- **Q1. What "400 total" counts.** 1: G reads 400 from F57's ranking, and
  E's and F's papers come on top (about 425 reads in all; G as estimated,
  680m, about 2 hours of fetching). 2: 400 reads in all, E's and F's
  included (G reads about 375; about 40 fewer minutes and 8 fewer of
  fetching). Recommend 1.
- **Q2. How F51 runs, its hold condition unmet.** 1: entered now from the
  2026-08-04 document at its current hash, superseded by a newer record
  when the re-run lands (45m). 2: kept on HOLD and out of this sprint
  (scope drops 45m). Recommend 1.
- **Q3. The ADR-0005 mismatch found at Phase 1.3** (not in the selection):
  1: added to this sprint as a dated amendment saying a source link may
  rest on a recorded team-lead decision, named in its evidence, with the
  next free number (15m). 2: carded for a later sprint. 3: kept as a
  finding only. Recommend 1.

## Premise falsifier

**The premises**: (a) "&amp;" is the only HTML entity stored; (b) a few
tests dominate the suite's time; (c) Phase 2's Sprint 28 documents still
state the results the card records; (d) the findings document is the
version the six assertions were drafted from; (e) the Classiq pages state
the figures the card quotes; (f) about 21 of Roadmap-to-QML's papers are
new to the store; (g) the 400 most-cited unread `qml` records bear on a
context often enough to yield.

**What would disprove each**: (a) A's entity test finds others: each is
corrected the same way, and the count is reported; (b) the timings are
flat: the suite is then sped up by sharing setup, or the plan says no
large gain exists, and the targeted mode carries the saving; (c) a file
changed: the assertions follow the file at its commit; (d) the six
assertions' quotes fail the write-path check against it: they are
corrected or dropped by name; (e) a figure is absent from its page: it is
not entered; (f) the match by id misses records held by DOI: the count is
re-run by DOI and corrected; (g) more than half refused as not bearing on
any context: the ranking is reported as wrong, not hidden.

**The checks cannot merely confirm**: the entity test reads every stored
text field; the timings come from pytest's own durations; the quote checks
run in the write path against text extracted fresh from each source; the
ledger test fails on any record in two groups.

## Risks

| Risk | Mitigation |
|---|---|
| A faster suite drops a guard | No guard removed; every guard B touches is injected and seen red; the full suite runs twice regardless |
| The targeted mode misses a test a change affects | It always adds CI's set; the two full runs per sprint backstop it; B's review checks the mapping |
| Two readers write the same record | One ledger, one group per record; a test fails on a duplicate |
| Five readers multiply arXiv traffic | One serial fetcher at 18 s inside F52's cap; agents read local copies only |
| A first-pass reader grades HIGH without a basis | G's I3 helper refuses HIGH without a named basis, proven by injection |
| F51's record outlives the re-run silently | Its provenance names the version and hash; the re-run's record links `superseded-by` |
| A blog's survey claim enters as its own | Only each author's own measurements are entered (E) |
| Phase 2's draft results change after the read | Provenance names the commit; a later change is a later card |
| A team-lead file in `Papers\` is renamed or moved | Never: matching reads names only |
| A closed paper is fetched around its paywall | Never: free copies only; a closed one joins the hand-download list |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: every stored "&amp;" corrected (4 at planning); the Cyc quote whole
  and checked; the entity test proven by injection; a second apply writes
  nothing
- B: per-test timings and the wall clock before and after recorded; the
  targeted mode in `run_suite.py` and the workflow; every touched guard
  still fails by injection
- C: each named result entered at Phase 2's commit with its limits, and
  related where it bears on a stored claim
- D: per Q2: the record and its six assertions entered at the named hash,
  or F51 left HOLD
- E: the unnamed PDFs and the named repository handled; the three
  challenge pages entered with their own measurements; counts before and
  after
- F: the list's commit recorded; every new paper matched, entered or given
  a reason; each read or kept with its reason
- G: 400 records per Q1 read from the ledger, each yielding or kept with
  its reason; HIGH grades carry their basis; the count refreshed; no
  record in two groups
- Full suite before Manual Validation, through `scripts/run_suite.py`;
  every other commit gated on its targeted tests and CI's set; CI green on
  the sprint PR before Manual Validation

## Out of scope

F39 and F90 (not selected). F57's, F95's and F98's later releases.
Downloading any paper around a paywall. Any write to `hsbc-qfraud-phase2`,
`hsbc-quantum-fraud-2026` or `spamfilter-multi`.
