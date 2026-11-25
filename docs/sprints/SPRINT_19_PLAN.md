# Sprint 19 Plan: Questions Kept in Full, Free Ids, One Full Suite, and 60 Papers from One List

**Dates**: from 2026-11-24. **Branch**: `feature/20261124_Sprint_19` (cut at
the Phase 6.6 carry-forward from Sprint 18's branch, 2026-11-24, after PR
#183 merged to develop and PR #190 to main; tagged `sprint-18`).
**Scope** (DEFINED, team lead, 2026-11-24, Phase 1.4): F151, F114 at 40
papers ("do 40 papers this sprint"), F150, F155, F152, F153, and F57 (a
release of the highest-priority 30). F39 was not selected, so model
assignments rest on `.claude/model_assignment_heuristics.json` (last
release 2026-10-30).

**Amended by the team lead's answers, 2026-11-25 (q1 to q7 below).** F57's
papers and the 306 papers read only in part join F114's ledger; F57 is
folded into F114 (q7 = a); one combined list, computed by a script (q6 =
a), ranked by F57's ranking across the whole list (q5 = b); this sprint
reads the top 60 that can be read, each one that cannot be read replaced
by the next (q2, q3). The 40 + 30 of the selection become 60. The papers
with no abstract and no citation count are carded for a 4-sprint release
(q5 = b). **Approved 2026-11-25 (q4)**: "Sprint plan approved as amended
(with any comments I provided), proceed with execution."

**F150 is a one-time change to the standard process** (team lead: "This
changes the standard process so that F150 does not need to be included in
future sprints"). From this sprint on, the full suite runs once. This
replaces Sprint 18's q18 = b, which kept the second run for Sprint 18 only.

**Issues**: Tasks A to F are #192 to #197. **PR**: #191 (draft).

## Objective

Keep every question and decision in one file, in full, and re-ask from it
(F151). Make every new assertion id free when it is chosen (F155). Run the
full suite once per sprint (F150). Put every paper still to be read in one
ranked list, and read its top 60 in full (F114, with F57 folded in). Settle
the 20 HIGH assertions whose quotes do not hold them (F152), and measure
the real defect rate in "held in part" (F153).

## Tasks

Est is coordinator time for the judgment steps. Sprint 18's `## Actuals`:
Tasks A to F took at least about 480 minutes against about 677 estimated
(the start of execution is not in a commit, so the actual is a lower
bound). Sprint 16's reads ran at about 26 pages per paper and 0.99 agent
minutes per page; Sprint 15's review and sign-off at 2.4 coordinator
minutes per record. Each task that changes `store/`, `scripts/` or a hook
carries one fresh-eyes review and fix cycle. Runtime is separate, with its
dominant term.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F151, every question stored in full.** `docs/sprints/SPRINT_N_DECISIONS.md`: each q and i written in full (every field of the AUTHORITATIVE shape, exactly one "(Recommendation)") before it is shown; each answer recorded word for word with its date from the clock; a later fact goes in a dated note under the entry, never an edit. Every message that needs an answer re-shows every open entry, pasted from the file. A test in `tests/test_sprint_documents.py` fails on a missing field, a count of "(Recommendation)" other than one, or a reused id. `.claude/hooks/block_procedural_question_stop.py` blocks a reply that asks an item not in the file, leaves out an open item, or changes an item's text. Both proven red. The workflow, checklist, retrospective doc and `CLAUDE.md` name the file. This plan's q1 to q7 are back-filled into `SPRINT_19_DECISIONS.md` with their answers | 60m [no-history] timebox | none | Claude, top tier |
| B | **F150, the full suite once.** `docs/SPRINT_EXECUTION_WORKFLOW.md` (the "runs twice per sprint" paragraph), `docs/SPRINT_CHECKLIST.md` (Phases 5 and 7) and `scripts/run_suite.py` (its docstrings) say one full run per sprint, before the Manual Validation hand-over. Every later commit runs `python scripts/run_suite.py --changed`, which still adds every `live_store` test after a store write. `gh pr ready` waits for CI green on the PR. A test fails if any of the three says "twice", or if the workflow stops naming `--changed` as the gate after the hand-over; proven red | 30m | none | Claude, top tier |
| C | **F155, free ids by construction.** `unique_assertion_id(record_id, name)` beside `f117_build_groups.prefixed`, using its author-and-year rule. `scripts/sprint13_g_check.py` refuses a taken id and prints a free one. `scripts/f146_checks.py` names the given id that an answered id is one character away from. Sprint 18's `vqe-definition` collision reproduced and given a free id. All three proven red. Done before any Sprint 19 brief is written | 75m | none | Claude, top tier |
| D | **F114, one list, 60 papers (F57 folded in).** (1) F57's 151 papers and the 306 read only in part enter F114's ledger as one-paper groups, named by `sprint13_g_ledger.new_groups` (q1, and "Add the 306 to F114 list before updating the combined list"). (2) `scripts/reading_list.py`, read only: every ledger paper not read in full, one line each with its group, contexts, citation count, what it needs (never read, read in part, or batch-read and not applied) and its copy (local path, free copy to fetch, or hand download); ranked by F114's steps 1 to 3 (new PDFs in `Papers\`, new papers on Christophe Pere's list, papers you name), then by F57's ranking across the whole list (q5 = b): context (`hsbc-2026`, the Dirac platforms, `qml`, `qc`, `ml`, `world`, `method`), then OpenAlex citation count, then uncounted by id. The counts are fetched once (batches of 50, the key in the header only) and saved with the selection in `manifests/sprint19_reading_ranking.json`, never in the store. A test fails if a paper appears twice or a readable paper is missing; proven red. (3) The 60: the 1 new list paper (arXiv 2611.27815, entered through the intake door, the list's new commit recorded), then the top of the list; a paper whose copy cannot be had (no free copy, a refused download, a book) is noted and the next one is taken, until 60 are read (q2, q3). Free copies fetched by `sprint10_f89_downloads.py`'s rules; a paywalled paper is never fetched and goes on the hand-download list. (4) Sprint 18's prompts with the i1 sentence; up to 5 local readers; each reviewer reads the paper in full; one apply through `sync_decided_assertion`, verified backup first. (5) The master plan: F57 folded into F114 (q7 = a): F57's ranking becomes F114's priority method; at each release F114 adds the papers intake entered at `seen` since the last release; F57's card removed (its history in git). The new card for the papers with no abstract and no citation count (q5 = b), across 4 sprints | 30m (ledger and list) + 60m (`reading_list.py` and its test) + 20m (entry) + 144m (review and sign-off, 60 at 2.4m) + 15m (cards) | the counts: about 27 OpenAlex requests, minutes. The fetch: up to about 60 downloads, minutes. The reads, at Sprint 16's rate: about 1,560 pages and about 1,540 agent minutes in the background (no reading budget) | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| E | **F152, the 20 "not held" HIGH items.** Each re-read in its paper (9 of the 20 are lemmas from one paper). Where new quotes hold the value, they are added; where none can, the item is graded LOW with its reason. Written through `sync_decided_assertion` and `store/quotes.py`, verified backup first; a second apply writes nothing; the audit, run again on the 20, gives "held" for every HIGH that remains | 60m | 20 re-reads in about 10 papers; one audit subagent run of 20 items | Claude, top tier; one Sonnet 5.5 audit subagent |
| F | **F153, a sample triage of 100 "held in part".** 100 items drawn with a fixed seed, spread across the audit's runs. Each classed as a real overstatement, wording only, or a reader error, by two Sonnet 5.5 subagent runs of 50 with controls, every class checked by the coordinator. The rate with its 95% interval recorded in `docs/INTAKE_WORKFLOW.md`; it decides whether a follow-up card is needed. Nothing written to the store | 60m | two subagent runs of 50 items, about 10 minutes each | Claude, top tier; Sonnet 5.5 subagents |

**Sequence**: A first, so every question from here on is stored. B next.
C before any reader brief. D's ledger, list and selection next; its
readers then run in the background, up to 5 at once. E and F are worked
while they read. One apply at a time: E's when it is ready, then D's.

**Total**: about 554 minutes at the estimates, plus about 1,540 agent
minutes of reading in the background (about 5 hours of wall clock at 5
readers in parallel at best; a usage-limit pause is waited out, never cut
around). No findings allowance: verification does not dominate the scope.

**If a Criterion 3 stop becomes necessary, the cut line is F, then E**:
each moves to the backlog. Deferring approved work is a Class 3 decision
and is never made unilaterally.

**Full suite**: once (before the Manual Validation hand-over; F150). Every
other gate is `python scripts/run_suite.py --changed`.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-11-24): PR #183 merged to develop (a3f5437,
  same tree as Sprint 18's last commit c0dd8ac) and PR #190 to main
  (e85915d, tagged `sprint-18`); no open sprint issue; the working tree
  clean except `.vscode/`. Dependency check: `uv pip list --outdated`
  lists the global Python environment's packages only (among them
  `anthropic` 2.6.0, latest 2.14.0, and `cryptography` 45.0.5, latest
  50.0.2); no Sprint 19 task uses either, and no security advisory is
  named here. The gate on the refinement commit: `run_suite.py --changed`,
  596 passed.
- **The store (snapshot as of 2026-11-24)**: 2,373 papers (1,853 at
  `read`, 520 at `seen`, none at `screened`). The store holds no
  abstracts and no citation counts (`paper_probes` holds access status,
  affiliations, publication status and version links only).
- **How many papers still need a full read (snapshot as of 2026-11-24)**:
  1,507 paper records have no `full` read row.
  - Papers to read: **1,315**, all in F114's ledger once D's step (1)
    runs.
    - 858 in F114's ledger now (148 at `seen`, 710 read in part), in 302
      groups. 13 of them (g335 to g347) hold F144's Batch API reads, not
      applied. 1 of them, Cichocki 2016, is a book (F138).
    - 151 that were F57's: no read row, outside the ledger.
    - 306 read in part (Sprints 9 to 12, before the 2026-10-25 full-read
      rule), outside the ledger; 279 have a local copy.
  - Not papers to read: 173 GitHub repository records; 6 withdrawn and 2
    retracted (records only); 2 books in F57's list (F138, HOLD); F90's
    7 (HOLD, no free copy); 2 read and refused. These 192 and the 1,315
    make the 1,507.
  - After this sprint's 60: about 1,255 papers.
- **The new list paper**: arXiv 2611.27815 answers HTTP 200 with
  `application/pdf` (UA "EvidenceBasedDB-fetcher/1.0", 2026-11-24); it is
  not in the store. No PDF in `Papers\` is new.
- **The ledger's order (finding, 2026-11-24)**: `scripts/sprint13_g_ledger.py`
  orders by why a read is needed (a theoretical result kept LOW, then not
  yet read, then the rest), then by record id, so by first author. It is
  not a relevance ranking. Groups g157 to g294 (688 papers read in part)
  are the "rest" bucket from "he..." onward; Sprints 17 and 18 skipped
  them. q5 = b replaces the order with F57's ranking.
- **F57's papers (2026-11-24, the refresh asked for)**: 520 papers at
  `seen`. 177 are F114 ledger records; 173 are GitHub repositories; 2 have
  a read row; 168 have no read row and an arXiv id or a DOI. Of the 168:
  6 withdrawn, 2 retracted, 2 books (F138) and F90's 7 (HOLD), so 151.
  None has a local copy. A dry run of the free-copy fetcher (OpenAlex
  lookups only): 29 have a free copy OpenAlex knows of; 122 have none.
- **F152's input**: the 20 "not held" results of F146's audit (intake
  section 79).
- **F153's input**: the 4,672 "held in part" results of F146's audit.
- **Plan-to-branch verification** (3.2.2.1): no Task A to F artifact
  exists (no `SPRINT_19_DECISIONS.md`; `run_suite.py` still says twice; no
  `unique_assertion_id`; no `reading_list.py`; no Sprint 19 reader
  manifests). F150 to F155, F114 and F57 are open cards.

## Decisions for the team lead

Each answer is recorded verbatim, dated from the clock when it arrived.

**q1. Where the 306 papers read only in part belong**
- What it is: 306 papers read in part in Sprints 9 to 12, before the
  2026-10-25 full-read rule, outside F114's ledger and at `read`, on no
  card.
- Options offered: a. (Recommendation) added to F57 as a second list; b. a
  new card; c. no change.
- **Answer (team lead, 2026-11-25)**: "a. but as a combined list with a
  note as to what needs to be done for each paper (fields - full read,
  local,...). Update priorities across the combined list using the F114
  priority method." Then: "Add the 306 to F114 list before updating the
  combined list with re-calculated priorities using the F114 method."

**q2. How F57's 30 are filled, when at most 29 have a free copy**
- Options offered: a. (Recommendation) fill from the 306; b. no fill; c.
  fill from F114's ledger.
- **Answer (team lead, 2026-11-25)**: "after combining the F57 and F114
  lists per q1, the combined number should be 60 (not this is new now
  that they are combined) that have free copies."

**q3. Which ledger papers make up F114's 39**
- Options offered: a. (Recommendation) never-read papers first (g372
  onward); b. the card's literal order (g157 onward).
- **Answer (team lead, 2026-11-25)**: "If there are 1,507 records with no
  full read ... For every one that is not read, add the next one so that
  60 total can be read. Make sense?" The order itself was decided by q5.

**q4. The plan**
- **Answer (team lead, 2026-11-25)**: "Sprint plan approved as amended
  (with any comments I provided), proceed with execution. All Sprint
  tasks and sub-tasks are approved."

**q5. How the combined list is ordered**
- Options offered (after the team lead asked, 2026-11-25, "Did F57 have a
  relative rating system that could be applied to the new combined
  list?"): a. (Recommendation) never-read first, then read in part, each
  by F57's ranking; b. the whole list by F57's ranking; c. the ledger's
  existing order.
- **Answer (team lead, 2026-11-25)**: "b - for all the papers with no
  abstracts and citations in order to relative prioritize - add a backlog
  item across 4 sprints to read the abstract and citations (see the old
  F57 ranking process) and update the F114 list item with the updated
  priority. F114 continues with the highest priority N items where the
  paper can be read in each sprint."

**q6. Where the combined list lives**
- Options offered: a. (Recommendation) `scripts/reading_list.py`,
  computed; b. a one-time list in the master plan.
- **Answer (team lead, 2026-11-25)**: "a".

**q7. What happens to F57's card**
- Options offered: a. (Recommendation) folded into F114; b. kept to feed
  new `seen` papers to F114's ledger.
- **Answer (team lead, 2026-11-25)**: "a - and any new "seen" papers get
  added to the f114 list (when it runs next sprint)".

## Premise falsifier

**The premises**: (a) a stored question file can be checked mechanically
(F151); (b) `--changed` covers every commit after the hand-over, store
writes included (F150); (c) an id can be made free at the moment it is
chosen (F155); (d) at least 60 of the list's top papers have a readable
copy (D); (e) the 20 "not held" items can be settled from their papers
(F152); (f) a sample of 100 measures the "held in part" defect rate
(F153).

**What would disprove each**: (a) the hook cannot read the reply's text,
so it cannot compare it with the file: A states that and keeps the test
only; (b) a store write after the hand-over runs no `live_store` test:
B's test fails; (c) the reader still writes a taken id: C's check refuses
it, and the injection proves it; (d) the list runs out of readable papers
before 60: D reports the count reached; (e) a paper does not state the
value at all: E grades it LOW with that reason; (f) the two subagent runs
disagree on more than a third of the items: F reports the disagreement
and the interval, not one rate.

**The checks cannot merely confirm**: A's, B's, C's and D's list checks
are proven red by injection; D's copies are checked page one against the
record; F's controls carry known answers.

## Risks

| Risk | Mitigation |
|---|---|
| F151's hook blocks a reply that is correct | The hook names the item it found missing or changed; proven red and green on real replies before it is registered |
| F150 leaves a store write after the hand-over unchecked | `--changed` adds every `live_store` test file after a store write; B's test pins that sentence |
| The ranking stores a count that changes | The counts live in the dated selection manifest, never in the store |
| A fetched copy is the wrong paper | Page one checked against the record before any read; an arXiv copy must name its id |
| A download goes around a paywall | Only arXiv and the open-access PDF OpenAlex lists; a refusal is listed, never retried another way |
| 60 papers outrun the usage limits | Up to 5 readers; a pause is waited out, never cut around; progress files restart a reader where it stopped |
| An apply writes an undecided field | `sync_decided_assertion` only; a verified backup first; a second apply writes nothing |
| F152 changes a grade without a basis | Each change names its quote or its LOW reason; the audit re-run on the 20 |
| An agent writes a result by script or by edit | The i1 sentence in every prompt; `tests/test_reader_prompts.py` fails on a prompt that lacks it |
| A write reaches a sibling repository | Phase 2 read only; no fetch in a sibling repository |
| The email address or the OpenAlex key leaks | Neither is sent or printed; requests carry the UA "EvidenceBasedDB-fetcher/1.0" or the fetcher's own |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time; readers' progress files |

## Definition of Done

- A: `SPRINT_19_DECISIONS.md` with q1 to q7 and their answers; the test and the hook proven red; the process docs and `CLAUDE.md` name the file
- B: the three places say once; the test proven red; this plan says once
- C: `unique_assertion_id`, the read checker's refusal and the near-miss naming, each proven red; the `vqe-definition` case reproduced
- D: the 151 and the 306 in the ledger; `reading_list.py` and its test proven red; the ranking manifest; 60 papers read in full, reviewed and applied once, each skipped paper noted with its reason; arXiv 2611.27815 entered and the list's commit recorded; F57 folded into F114 and the 4-sprint card written; the counts before and after; a second apply writes nothing
- E: all 20 decided and written, backup first; a second apply writes nothing; the audit re-run gives "held" for every remaining HIGH
- F: the rate and its 95% interval in `docs/INTAKE_WORKFLOW.md`; nothing written to the store
- CI green on the sprint PR before Manual Validation

## Out of scope

F154 (the semantic pair screen) and F39 (not selected). F138 and F90
(HOLD). Applying F144's 13 Batch API reads (g335 to g347) as they stand
(their papers are on the list and are read again if they rank in the
top 60). Reading abstracts for the new 4-sprint card (from Sprint 20).
Any fix to the 4,672 "held in part" items beyond F's sample. Downloading
any paper around a paywall. Any write to `hsbc-qfraud-phase2`,
`hsbc-quantum-fraud-2026` or `spamfilter-multi`.
