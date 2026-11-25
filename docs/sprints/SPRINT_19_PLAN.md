# Sprint 19 Plan: Questions Kept in Full, Free Ids, One Full Suite, and 70 Papers Read

**Dates**: from 2026-11-24. **Branch**: `feature/20261124_Sprint_19` (cut at
the Phase 6.6 carry-forward from Sprint 18's branch, 2026-11-24, after PR
#183 merged to develop and PR #190 to main; tagged `sprint-18`).
**Scope** (DEFINED, team lead, 2026-11-24, Phase 1.4): F151, F114 at 40
papers ("do 40 papers this sprint"), F150, F155, F152, F153, and F57 (a
release of the highest-priority 30). F39 was not selected, so model
assignments rest on `.claude/model_assignment_heuristics.json` (last
release 2026-10-30).

**F150 is a one-time change to the standard process** (team lead: "This
changes the standard process so that F150 does not need to be included in
future sprints"). From this sprint on, the full suite runs once. This
replaces Sprint 18's q18 = b, which kept the second run for Sprint 18 only.

## Objective

Keep every question and decision in one file, in full, and re-ask from it
(F151). Make every new assertion id free when it is chosen (F155). Run the
full suite once per sprint (F150). Read 70 papers in full: 40 for F114 and
30 for F57. Settle the 20 HIGH assertions whose quotes do not hold them
(F152), and measure the real defect rate in "held in part" (F153).

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
| A | **F151, every question stored in full.** `docs/sprints/SPRINT_N_DECISIONS.md`: each q and i written in full (every field of the AUTHORITATIVE shape, exactly one "(Recommendation)") before it is shown; each answer recorded word for word with its date from the clock; a later fact goes in a dated note under the entry, never an edit. Every message that needs an answer re-shows every open entry, pasted from the file. A test in `tests/test_sprint_documents.py` fails on a missing field, a count of "(Recommendation)" other than one, or a reused id. `.claude/hooks/block_procedural_question_stop.py` blocks a reply that asks an item not in the file, leaves out an open item, or changes an item's text. Both proven red. The workflow, checklist, retrospective doc and `CLAUDE.md` name the file. This plan's q1 to q4 are back-filled into `SPRINT_19_DECISIONS.md` with their answers | 60m [no-history] timebox | none | Claude, top tier |
| B | **F150, the full suite once.** `docs/SPRINT_EXECUTION_WORKFLOW.md` (the "runs twice per sprint" paragraph), `docs/SPRINT_CHECKLIST.md` (Phases 5 and 7) and `scripts/run_suite.py` (its docstrings) say one full run per sprint, before the Manual Validation hand-over. Every later commit runs `python scripts/run_suite.py --changed`, which still adds every `live_store` test after a store write. `gh pr ready` waits for CI green on the PR. A test fails if any of the three says "twice", or if the workflow stops naming `--changed` as the gate after the hand-over; proven red | 30m | none | Claude, top tier |
| C | **F155, free ids by construction.** `unique_assertion_id(record_id, name)` beside `f117_build_groups.prefixed`, using its author-and-year rule. `scripts/sprint13_g_check.py` refuses a taken id and prints a free one. `scripts/f146_checks.py` names the given id that an answered id is one character away from. Sprint 18's `vqe-definition` collision reproduced and given a free id. All three proven red. Done before any Sprint 19 brief is written | 75m | none | Claude, top tier |
| D | **F114, 40 papers.** Order (the card's): (1) new PDFs in `Papers\`: none (snapshot 2026-11-24); (2) the 1 paper Christophe Pere's list added at 24853a7acb, arXiv 2611.27815 (Srimahajariyapong et al. 2026), fetched once from arXiv, entered through the intake door, the list's new commit recorded; (3) none named by you; (4) 39 from the ledger, per q3. Under q3 = a: g372 to g381, g383 to g405, g409 to g414 (one paper each; g382, Cichocki 2016, is a book, F138). New groups named by `sprint13_g_ledger.new_groups`. Readers under Sprint 18's prompts with the i1 sentence; up to 5 local readers shared with E; each reviewer reads the paper in full; one apply through `sync_decided_assertion`, verified backup first | 20m (entry) + 96m (review and sign-off, 40 at 2.4m) | no estimate as a limit (no reading budget). At Sprint 16's rate, about 1,040 pages and about 1,030 agent minutes in the background | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| E | **F57, the highest-priority 30.** The list refreshed 2026-11-24 (below): 151 papers, none in F114's ledger, so none overlaps D. F57's order (Sprint 17's F144 slice): `qml`, `qc`, `ml`, `world`, then most cited. Each paper's free copy fetched by `scripts/sprint10_f89_downloads.py`'s rules (arXiv through the paced fetcher; else the open-access PDF OpenAlex lists; a paywalled paper never fetched), saved into `Papers\`, never overwriting. Each paper with no copy gets its hand-download reason in the apply. The 30 per q2. One-paper ledger groups so each paper has exactly one reader; same prompts, review and apply as D | 30m (slice and fetch) + 72m (review and sign-off, 30 at 2.4m) | the fetch: 29 OpenAlex lookups and 29 downloads, minutes. The reads, at Sprint 16's rate: about 780 pages and about 770 agent minutes in the background | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| F | **F152, the 20 "not held" HIGH items.** Each re-read in its paper (9 of the 20 are lemmas from one paper). Where new quotes hold the value, they are added; where none can, the item is graded LOW with its reason. Written through `sync_decided_assertion` and `store/quotes.py`, verified backup first; a second apply writes nothing; the audit, run again on the 20, gives "held" for every HIGH that remains | 60m | 20 re-reads in about 10 papers; one audit subagent run of 20 items | Claude, top tier; one Sonnet 5.5 audit subagent |
| G | **F153, a sample triage of 100 "held in part".** 100 items drawn with a fixed seed, spread across the audit's runs. Each classed as a real overstatement, wording only, or a reader error, by two Sonnet 5.5 subagent runs of 50 with controls, every class checked by the coordinator. The rate with its 95% interval recorded in `docs/INTAKE_WORKFLOW.md`; it decides whether a follow-up card is needed. Nothing written to the store | 60m | two subagent runs of 50 items, about 10 minutes each | Claude, top tier; Sonnet 5.5 subagents |

**Sequence**: A first, so every question from here on is stored. B next.
C before any reader brief for D or E. D's and E's readers then start in the
background, up to 5 at once across both. F and G are worked while they
read. One apply at a time: F's when it is ready, then D's, then E's.

**Total**: about 503 minutes at the cards' estimates, plus about 1,800
agent minutes of reading in the background (about 6 hours of wall clock
at 5 readers in parallel at best; a usage-limit pause is waited out, never
cut around). No findings allowance: verification does not dominate the
scope. If G's rate shows a real defect class, the follow-up is a card,
not this sprint's work.

**If a Criterion 3 stop becomes necessary, the cut line is G, then F**:
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
  `read`, 520 at `seen`, none at `screened`).
- **How many papers still need a full read (snapshot as of 2026-11-24)**:
  1,507 paper records have no `full` read row.
  - Papers to read: **1,315**.
    - 858 in F114's ledger (148 at `seen`, 710 read in part), in 302
      groups. 13 of them (g335 to g347) hold F144's Batch API reads, not
      applied. 1 of them, Cichocki 2016, is a book (F138).
    - 151 for F57: no read row, outside the ledger (detail in E's
      pre-flight).
    - 306 read in part (Sprints 9 to 12, before the 2026-10-25 full-read
      rule), outside the ledger, on no card; 279 have a local copy (q1).
  - Not papers to read: 173 GitHub repository records; 6 withdrawn and 2
    retracted (records only); 2 books in F57's list (F138, HOLD); F90's
    7 (HOLD, no free copy); 2 read and refused. These 192 and the 1,315
    make the 1,507.
  - After this sprint's 70: about 1,245 papers.
- **D's new paper**: arXiv 2611.27815 answers HTTP 200 with
  `application/pdf` (UA "EvidenceBasedDB-fetcher/1.0", 2026-11-24); it is
  not in the store. No PDF in `Papers\` is new.
- **D's 39 ledger papers (2026-11-24)**: each has its PDF at its ledger
  path. g382 (Cichocki 2016) is left out as a book. g406 to g408 are
  applied.
- **The ledger's order (finding, 2026-11-24)**: groups g157 to g294 hold
  688 papers read in part (2026-10-23 to 25), never re-read in full, at
  `not started`. Sprints 17 and 18 skipped them: Sprint 17 called g295 "the
  first group not yet read in full", and Sprint 18 took g349 onward (q20's
  split of the never-read Task G downloads). No document records why. q3
  asks which comes next.
- **E's list (2026-11-24, the refresh you asked for)**: 520 papers at
  `seen`. 177 are F114 ledger records; 173 are GitHub repositories; 2 have
  a read row; 168 have no read row and an arXiv id or a DOI. Of the 168:
  6 withdrawn, 2 retracted, 2 books (F138) and F90's 7 (HOLD), so 151 are
  F57's. None has a local copy (`store.recheck.local_pdf`). No paper has
  been read since F57's last release that is still on the list.
- **E's free copies (dry run, 2026-11-24)**: the fetcher's dry run on the
  151 (OpenAlex lookups only, nothing downloaded): **29 have a free copy
  OpenAlex knows of; 122 have none** (96 closed, 26 with no PDF link). The
  29 by F57's order: 1 `qml` (Mahroo 2023, arXiv), 8 `qc` (among them Kim
  2023, "Evidence for the utility of quantum computing before fault
  tolerance", and Aaronson 2011, linear optics), 19 `ml` (most of them
  fraud detection: Bolton 2002, Hilal 2022, Pourhabibi 2020 and others),
  1 `world`. Some links (ACM, ScienceDirect, IEEE) may refuse an automated
  download; each refusal is listed, never worked around. So at most 29 of
  the 30 can come from F57's own list (q2).
- **F152's input**: the 20 "not held" results of F146's audit (intake
  section 79).
- **F153's input**: the 4,672 "held in part" results of F146's audit.
- **Plan-to-branch verification** (3.2.2.1): no Task A to G artifact
  exists (no `SPRINT_19_DECISIONS.md`; `run_suite.py` still says twice; no
  `unique_assertion_id`; no Sprint 19 reader manifests). F150 to F155,
  F114 and F57 are open cards.

## Decisions for the team lead

**q1. Where the 306 papers read only in part belong**
- What it is: 306 papers were read in part in Sprints 9 to 12, before your
  2026-10-25 rule that every read is full. They are outside F114's ledger
  and are at `read`, so F57 ("seen and screened") does not hold them
  either. No card reads them again.
- What it prevents and/or catches: it prevents 306 papers keeping partial
  claims forever because no card names them.
- Prevention or control: prevention.
- Long-term value: every paper in the store is read in full, as your
  2026-10-25 rule asks.
- Evidence: the count above (1,507 records with no full read reconcile
  exactly: 858 + 306 + 168 + 173 + 2); 279 of the 306 have a local copy,
  so no fetch is needed for most.
- Extends: F57 and your 2026-10-25 full-read rule.
- Effort: about 10m now to change the card. The reads: about 306 x 26
  pages, about 8,000 pages and about 7,900 agent minutes over later
  sprints, at the release size you choose.
- Options:
  - **a. (Recommendation)** You get the 306 added to F57 as its second
    list: read after F57's never-read papers, in F57's order (`hsbc-2026`
    and the Dirac platforms first: up to 19 of them; then `qml`, 257). Papers
    with no claims at all come first.
    - Pro: one card holds every paper outside the ledger; no new card to
      track.
    - Con: F57 grows from 151 to 457 papers.
  - **b.** You get a new card for the 306, with its own priority.
    - Pro: you set its priority apart from F57's.
    - Con: one more permanent card; the two cards share an order rule.
  - **c.** You get no change: the 306 keep their partial reads.
    - Pro: no reading time spent.
    - Con: they stay outside your full-read rule, unlisted.

**q2. How F57's 30 are filled, when at most 29 have a free copy**
- What it is: of F57's 151 papers, 29 have a free copy (dry run above),
  and some of those links may refuse a download. So F57's own list gives
  at most 29.
- What it prevents and/or catches: it prevents a release that silently
  reads fewer than you asked, or fills with papers you did not choose.
- Prevention or control: prevention.
- Long-term value: each release says where its papers came from.
- Evidence: the dry run above; 122 with no free copy.
- Extends: F57's known limit (a record with no free copy cannot reach
  `read`).
- Effort: about the same in every option; the reading time is per paper,
  about 26 agent minutes each.
- Options:
  - **a. (Recommendation)** You get every F57 paper whose copy downloads
    (up to 29), in F57's order, and the rest of the 30 from the top of
    q1's 306 in F57's order (these have local copies). The 122 with no
    copy, and any refused download, go on the hand-download list. Needs
    q1 = a; with q1 = b or c this becomes option b.
    - Pro: 30 papers read, as you asked; the fill is the next papers in
      F57's own order.
    - Con: a few of the 30 are re-reads of papers already read in part.
  - **b.** You get only the F57 papers whose copies download (29 at
    most), no fill.
    - Pro: only never-read papers.
    - Con: fewer than 30.
  - **c.** You get the fill from F114's ledger instead (the papers after
    D's 39).
    - Pro: no change to F57's card.
    - Con: F114 then reads more than the 40 you set, under F57's name.

**q3. Which ledger papers F114's 39 are**
- What it is: F114's card says "the ledger, in its order". The first
  groups not read in full are g157 to g294 (688 papers read in part in
  October). Sprints 17 and 18 skipped them and read the never-read papers
  from g295 and g349 onward, without saying why.
- What it prevents and/or catches: it prevents the skip continuing as an
  unstated rule.
- Prevention or control: control (it records the order).
- Long-term value: the card says the order every release follows.
- Evidence: the ledger finding above; `scripts/sprint13_g_status.py`
  reports g157 to g294 as `not started`.
- Extends: F114's order rule; q20's split (2026-11-09).
- Effort: about 5m to write the rule into the card; the same reading time
  either way.
- Options:
  - **a. (Recommendation)** You get never-read papers first: g372 onward
    (g372 to g414, 39 papers, 36 of them never read), then g157 to g294.
    The card says so.
    - Pro: each read adds claims to a paper that has none; it matches what
      Sprints 17 and 18 did.
    - Con: the 688 read-in-part papers wait about 4 more sprints.
  - **b.** You get the card's literal order: g157 onward (39 papers read
    in part in October).
    - Pro: the card's words, unchanged.
    - Con: papers with no claims at all wait longer.

**q4. The plan**
- What it is: this plan, Tasks A to G, in the sequence above.
- What it prevents and/or catches: approval opens the auto-advance window;
  without it no task starts.
- Prevention or control: control.
- Long-term value: a defined sprint.
- Evidence: the pre-flights above.
- Extends: Phase 3.7.
- Effort: about 503 coordinator minutes plus about 1,800 agent minutes of
  reading in the background.
- Options:
  - **a. (Recommendation)** You approve the plan as written, with q1 to
    q3 as you answer them.
    - Pro: work starts now, in the stated order.
    - Con: none known.
  - **b.** You approve it with changes you name.
    - Pro: your changes are absorbed in the commit that records them.
    - Con: one more round before work starts.

## Premise falsifier

**The premises**: (a) a stored question file can be checked mechanically
(F151); (b) `--changed` covers every commit after the hand-over, store
writes included (F150); (c) an id can be made free at the moment it is
chosen (F155); (d) the 70 papers have readable copies (D, E); (e) the 20
"not held" items can be settled from their papers (F152); (f) a sample of
100 measures the "held in part" defect rate (F153).

**What would disprove each**: (a) the hook cannot read the reply's text,
so it cannot compare it with the file: A states that and keeps the test
only; (b) a store write after the hand-over runs no `live_store` test:
B's test fails; (c) the reader still writes a taken id: C's check refuses
it, and the injection proves it; (d) a download is refused or a copy is
not the paper: E lists it and takes the next paper in order; (e) a paper
does not state the value at all: F grades it LOW with that reason; (f)
the two subagent runs disagree on more than a third of the items: G
reports the disagreement and the interval, not one rate.

**The checks cannot merely confirm**: A's, B's and C's checks are proven
red by injection; E's copies are checked page one against the record; G's
controls carry known answers.

## Risks

| Risk | Mitigation |
|---|---|
| F151's hook blocks a reply that is correct | The hook names the item it found missing or changed; proven red and green on real replies before it is registered |
| F150 leaves a store write after the hand-over unchecked | `--changed` adds every `live_store` test file after a store write; B's test pins that sentence |
| A fetched copy is the wrong paper | Page one checked against the record before any read; an arXiv copy must name its id |
| A download goes around a paywall | Only arXiv and the open-access PDF OpenAlex lists; a refusal is listed, never retried another way |
| 70 papers outrun the usage limits | Up to 5 readers; a pause is waited out, never cut around; progress files restart a reader where it stopped |
| An apply writes an undecided field | `sync_decided_assertion` only; a verified backup first; a second apply writes nothing |
| F152 changes a grade without a basis | Each change names its quote or its LOW reason; the audit re-run on the 20 |
| An agent writes a result by script or by edit | The i1 sentence in every prompt; `tests/test_reader_prompts.py` fails on a prompt that lacks it |
| A write reaches a sibling repository | Phase 2 read only; no fetch in a sibling repository |
| The email address or the OpenAlex key leaks | Neither is sent or printed; requests carry the UA "EvidenceBasedDB-fetcher/1.0" or the fetcher's own |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time; readers' progress files |

## Definition of Done

- A: `SPRINT_19_DECISIONS.md` with q1 to q4 and their answers; the test and the hook proven red; the process docs and `CLAUDE.md` name the file
- B: the three places say once; the test proven red; this plan says once
- C: `unique_assertion_id`, the read checker's refusal and the near-miss naming, each proven red; the `vqe-definition` case reproduced
- D: 40 papers read in full, reviewed and applied once; arXiv 2611.27815 entered and the list's commit recorded; the counts before and after; a second apply writes nothing
- E: 30 papers read in full, reviewed and applied once, per q2; each paper with no copy given its hand-download reason; F57's card updated per q1; the counts before and after; a second apply writes nothing
- F: all 20 decided and written, backup first; a second apply writes nothing; the audit re-run gives "held" for every remaining HIGH
- G: the rate and its 95% interval in `docs/INTAKE_WORKFLOW.md`; nothing written to the store
- CI green on the sprint PR before Manual Validation

## Out of scope

F154 (the semantic pair screen) and F39 (not selected). F138 and F90
(HOLD). Applying F144's 13 Batch API reads (g335 to g347). Any fix to the
4,672 "held in part" items beyond G's sample (a card, if G's rate calls
for one). Downloading any paper around a paywall. Any write to
`hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
