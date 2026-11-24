# Sprint 18 Plan: The Agreement Map and the HIGH Audit, 30 Papers, and Safer Applies

**Dates**: from 2026-11-19. **Branch**: `feature/20261113_Sprint_18` (cut at
the Phase 6.6 carry-forward from Sprint 17's branch, 2026-11-13, after PR
#174 merged to develop and PR #182 to main; tagged `sprint-17`).
**Scope** (DEFINED, team lead, received 2026-11-18 at about 11:50pm): F146,
F114, F149, F147, F145, F148. This is option a of the Phase 1.4 slate. F39
was not selected, so model assignments rest on
`.claude/model_assignment_heuristics.json` (last release 2026-10-30).

**The outside date has passed.** F146's card says "on the API credit
before it expires" and "nothing sent on or after 2026-11-18". The team
lead gave the credit's expiry as 2026-11-18 (2026-11-07), and
`scripts/batch_read.py` refuses every send from that day
(`STOP = date(2026, 11, 18)`, line 71). The scope arrived at 11:50pm on
2026-11-18, and this plan is written on 2026-11-19. So F146 cannot run on
the credit as carded. q1 asks how F146 runs. Whether any credit remains
is an account fact that cannot be checked from here.

**Answered 2026-11-19: q1 = c, q2 = a.** F146 runs on Claude Code
subagents on the team lead's subscription, with no API spend; no API key
is read by F146. F147 moves the live applier and every new applier to the
shared function and freezes the 23 one-time scripts by a test.

## Objective

Build the agreement map and the HIGH audit (F146), and run them the way
q1 decides. Read 30 more papers in full (F114). Make every apply write
only the fields a review decided (F147), and make document counts come from
the store (F148). Fix the ledger's group naming (F149), and learn what
qubit-lab.ch's Evidence pages hold (F145).

## Tasks

Est is coordinator time for the judgment steps. Sprint 17's `## Actuals`:
Tasks A to F took about 780 minutes for 625 estimated (1.25 times). Sprint
16's reads ran at 0.75 reader minutes and 0.24 reviewer minutes per page.
Each task that changes `store/`, `scripts/` or a hook carries one
fresh-eyes review and fix cycle. Runtime is separate, with its dominant
term.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F149, the ledger's next group name.** `scripts/sprint13_g_ledger.py` line 75 sets `start = len(groups)`; it becomes the highest group number plus one, as `batch_read.next_group` does. A test on a ledger with a gap, proven red | 15m | none | Claude, top tier |
| B | **F147, one apply function.** A shared function in `store/ingest.py` takes the review's decided fields and refuses any other field, naming it. `scripts/full_read_apply.py` moves to it, so Task D's apply runs through it. The other appliers per q2. A test, proven red, that an undecided field is refused; Task D's trial apply shows the same writes as before the change | 120m [no-history] timebox | none | Claude, top tier |
| C | **F146, the agreement map and the HIGH audit.** Built in full, dry run by default, on F144's rules (a forecast and a worst case before each send, a cap, a saved result never sent again, a failing result kept and flagged, the key never printed or written). Part 1: Haiku 5.5 screens pairs of assertions from different papers that share a context and a topic; Sonnet 5.5 judges each kept pair (supports, contradicts or unrelated, with the deciding quotes). Part 2: Sonnet 5.5 checks each HIGH value against its own quotes (held, held in part, not held, with why). Results are proposals, saved outside the store. How the sends run: q1 = c, Claude Code subagents on the subscription, no API spend: a script screen replaces the Haiku screen for part 1, the scripts write each subagent's input file and check its result file, and a saved result is never run again. Each rule tested and proven red | 240m [no-history] timebox | q1 = c: the dry run counts the candidate pairs first (the map's size is not known until then: `[unbounded]` until the dry run). The HIGH audit: 11,754 assertions, about 830 characters each; about 40 Sonnet 5.5 subagent runs of about 300 assertions, about 3 hours at 5 in parallel `[no-history]` | Claude, top tier; Sonnet 5.5 subagents judge |
| D | **F114, 30 papers.** Order: (1) the 1 new PDF in `Papers\`, Huang 2023, linked to its stored record `huang-2023-noise-resilient-single-pixel-compressive` (at `seen`); (2) the 3 papers Christophe Pere's list added at 7113ded1df (arXiv 2611.08461, 2611.10105, 2611.08821), each fetched once from arXiv and entered through the intake door, with the list's new commit recorded; (3) 26 from the ledger, from the first group not yet read in full, with Sprint 16's exclusions (saved web pages with no article, directory sources, books), new groups named by Task A's fix. Readers under Sprint 17's prompts with q28's quotes-first rule; up to 5 local readers; each reviewer reads the paper in full; one apply through Task B's function, with its trial and verified backup | 20m (entry) + 72m (review and sign-off, at Sprint 15's 2.4m per record) | no estimate as a limit (no reading budget). At Sprint 16's rate, about 26 pages per paper and 0.99 agent minutes per page: about 780 agent minutes in the background | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| E | **F145, qubit-lab.ch's Evidence pages.** Read the public page and `/evidence-runs.json` in full; enter qubit-lab.ch as a source record (a vendor, its conflict of interest named) and each study's and run's stated result as an assertion with its own limits, quotes checked and certainty graded (a vendor's own result, single source); link each to what the store holds on the same question, with its reason; list gated or "on request" material without requesting it; a short note on what this repository and Phase 2 could adopt, each adoption asked as its own question | 120m [no-history] timebox | two fetches (pre-flight below) | Claude, top tier |
| F | **F148, counts from the store.** `scripts/doc_counts.py` prints, or writes into a dated block, the counts a document names (assertions, papers, HIGH and LOW by basis, group states). Its block in `docs/INTAKE_WORKFLOW.md` and in Sprint 18's summary. Earlier dated sections and ADR amendments keep their snapshots. A `live_store` test, proven red, that the block matches the store | 90m [no-history] timebox | one store read, seconds | Claude, top tier |

**Sequence**: A, then B, both before D's apply. D's readers start after A,
in the background. C is built while they read; its subagent runs (q1 = c)
start after D's reads, so the two do not share the usage limits at once. E and
F next. D's review and apply come last, through B's function. One apply at
a time. Total about 677 minutes at the cards' estimates; at Sprint 17's
1.25 times, about 850 minutes, plus D's reads in the background and C's
subagent runs (about 3 hours for the audit, the map unknown until the dry
run). No findings allowance: the scope is not dominated by
verification.

**If a Criterion 3 stop becomes necessary, the cut line is F, then E**:
each moves to the backlog. Deferring approved work is a Class 3 decision
and is never made unilaterally.

**Full suite**: twice (before the Manual Validation hand-over, and after
any retrospective improvements that change code). Every other gate is
`python scripts/run_suite.py --changed`.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-11-19): PR #174 merged to develop (4728112) and
  PR #182 to main (125cb9d, tagged `sprint-17`); no open sprint issue;
  working tree clean except this plan and the status file. Dependency
  check: `uv pip list --outdated` lists the global Python environment's
  packages only (among them `anthropic` 2.6.0, latest 2.10.0); no
  security-relevant bump is named. The full suite: see the status note.
- **The store (snapshot as of 2026-11-19)**: 2,369 papers (1,822 at
  `read`, 547 at `seen`); 37,408 assertions (11,754 `high`, 25,554 `low`,
  97 `moderate`, 1 `very-low`, 2 with no certainty).
- **F114's ledger (snapshot as of 2026-11-19)**: 1,676 records in 515
  groups; 792 with a `full` read row, 884 without, in 326 groups. The
  2026-11-13 master plan figures (725 and 951) counted only read rows dated
  2026-10-26 or later; corrected in this commit.
- **F114's new papers**: no PDF saved into `Papers\` since 2026-11-10.
  The list is still at 7113ded1df (2026-11-10). Each of the 3 arXiv ids
  answers HTTP 200 with `application/pdf` (UA
  "EvidenceBasedDB-fetcher/1.0", 2026-11-19); none is in the store.
- **F145's source (spike, 2026-11-19)**: `https://qubit-lab.ch/evidence`
  answers HTTP 200, `text/html`, 493,993 bytes, about 82,500 characters of
  text without scripts and styles: the content is in the HTML, so no
  browser is needed. `https://qubit-lab.ch/evidence-runs.json` answers
  HTTP 200, `application/json`, 30,271 bytes, with a `verdictVocabulary`
  ("Advantage demonstrated", "Parity", "No advantage demonstrated",
  "Inconclusive", "Method study") and records `QL-EV-001` onward.
- **F146's facts**: `scripts/batch_read.py` holds the state file, the cap,
  the stop date and the no-resend rule F146 reuses. The `anthropic` SDK
  2.6.0 is installed. Batch prices as of 2026-11-07 (Anthropic's batch
  page, re-checked before any send): Sonnet 5.5 $1 and $5 per MTok in and
  out, Haiku 5.5 $0.05 and $0.25. The HIGH audit's size, from the store:
  11,754 HIGH assertions, about 830 characters each (533 value, reasons
  and provenance; 297 quotes).
- **F147's inventory (code, not only documents)**: 24 scripts call
  `sync_assertion` or `sync_verified_assertion` (`store/ingest.py` lines
  723 and 730). One is the live applier, `scripts/full_read_apply.py` (its
  `decided_fields` at line 370). The other 23 are one-time sprint appliers,
  `sprint9_f46_pending_facts.py` to `sprint17_q29_q31_grades.py`.
  **Corrected 2026-11-21 (Task B):** a text search counts comments too.
  Counted from the parsed code, 22 one-time appliers call a sync function,
  not 23: 6 of Sprints 9 and 10 call `sync_assertion` (already exempt as
  `store.write_path.LEGACY`), and 16 of Sprints 11 to 17 call
  `sync_verified_assertion` (`store.write_path.SYNC_FROZEN`).
  `sprint9_f46_pending_facts.py` and `sprint15_mv_decisions.py` name it
  only in a comment. q2 = a freezes all 22; the decision does not change.
  (An earlier correction the same day said 24; it counted the comments.)
- **F148's inventory**: `docs/INTAKE_WORKFLOW.md` has about 115 lines that
  state a count of assertions, papers, records, HIGH or LOW, across
  sections 1 to 77. Each section is dated; the counts are snapshots.
- **F149's inventory**: `scripts/sprint13_g_ledger.py` line 75,
  `start = len(groups)`. Today g001 to g509 are contiguous, so the defect
  has not fired.
- **Plan-to-branch verification** (3.2.2.1): no Task A to F artifact
  exists (`scripts/doc_counts.py` is absent; no F146 script exists;
  `sprint13_g_ledger.py` still uses the count; no qubit-lab.ch record is
  in the store). F145 to F149 and F114 are open cards.

## Decisions for the team lead

**q1. How F146's sends run, now that the credit's stop date has passed**
- What it is: F146 was carded to run on the $97 API credit before
  2026-11-18. The scope arrived late on 2026-11-18, and the plan is
  written on 2026-11-19. Nothing can be sent on the credit.
- What it prevents and/or catches: it prevents money being spent without
  your decision, and it prevents F146 being built against a deadline that
  has passed.
- Prevention or control: prevention (the decision comes before any send).
- Long-term value: the agreement map and the HIGH audit are the store's
  first cross-paper check and its first check of every HIGH grade.
- Evidence: `batch_read.py` line 71; your words of 2026-11-07 ("$97,
  expiring 2026-11-18"); the HIGH audit's size above. Whether any credit
  remains is not checkable from here.
- Extends: Sprint 17's q26 = a (the credit's use) and F144.
- Effort: the build is 240m in every option except d. Run cost per option
  below. Each run is once, not recurring.
- Options:
  - **a. (Recommendation)** You get both parts built and dry-run, with a
    cost forecast from the real counts, and nothing spent until you decide.
    No send this sprint until then: at the forecast I ask one more question
    (pay for standard API use, run on Claude Code subagents, or stop), with
    the measured numbers. The stop date becomes a setting you approve.
    - Pro: no money is spent without a decision made on real numbers; the
      map's size, unknown until the dry run counts the pairs, is known
      before anything is spent.
    - Con: one more decision mid-sprint; the results may land in Sprint 19
      if the answer is "stop".
  - **b.** You get both parts run on the Batch API at standard billing,
    after you add funds to the account. Forecast for the HIGH audit, from
    the store's sizes at the 2026-11-07 prices: about $15 to $26 (lower if
    20 assertions share one request). The agreement map's cost is unknown
    until the dry run counts the pairs; a cap you set stops it.
    - Pro: both results this sprint; the cheapest model time per check.
    - Con: new spending on your account; the map's cost is not known at
      the moment you approve it.
  - **c.** You get both parts run by Claude Code subagents on your
    subscription, with no API spend. The HIGH audit is about 40 Sonnet 5.5
    runs of about 300 assertions each, about 3 hours of wall clock at 5 in
    parallel `[no-history]`; the agreement map is limited to the pairs a
    script screen keeps.
    - Pro: no new money.
    - Con: it competes with Task D's readers for the same usage limits, and
      a weekly limit pauses both; a subagent screen is weaker than the
      Haiku screen.
  - **d.** F146 moves to the backlog (a Class 3 de-scope), and the sprint
    is 240m shorter.
    - Pro: about 300 minutes off the sprint at Sprint 17's pace.
    - Con: neither the map nor the audit; you selected F146 for this sprint.
- **Answer (team lead, 2026-11-19): c.**

**q2. Which existing appliers F147 moves to the shared function**
- What it is: the card says "the existing appliers move to it". There are
  24: the live applier `full_read_apply.py` and 23 one-time sprint scripts.
- What it prevents and/or catches: it prevents an undecided field write,
  the defect that reached the store 4 times (4d969d9, ed5ab01, aabdd49,
  d740d72).
- Prevention or control: prevention.
- Long-term value: every future apply is safe by construction.
- Evidence: the inventory above; the 4 defects were in sprint-specific
  appliers; the one-time scripts are re-run rarely (Sprint 17 re-ran
  `sprint17_q23_corrections.py` once, after q29 and q31, and
  `decided_day` kept the later decisions).
- Extends: Sprint 17's q11 = a (F147's card) and `store/write_path.py`'s
  refusal of scripts that hold their own "Started LOW" text.
- Effort: per option below; run cost none.
- Options:
  - **a. (Recommendation)** You get the live applier and every new applier
    through the function, and the 23 one-time scripts frozen: a test, proven
    red, lists them and fails if a script not on the list calls the old
    functions directly. About 120m, the card's estimate.
    - Pro: the card's estimate holds; every apply from now on is checked.
    - Con: a re-run of an old one-time script is not checked by the new
      function (it still meets `decided_day` and the write path's checks).
  - **b.** You get all 24 moved, each old script dry-run before and after
    to show the same writes. About 120m plus about 8m each for 23 scripts,
    about 305m.
    - Pro: no apply path is left outside the function.
    - Con: about 185 more minutes, mostly on scripts that already ran and
      may never run again.
- **Answer (team lead, 2026-11-19): a.**

## Premise falsifier

**The premises**: (a) the store's HIGH values can be checked from their
own quotes without the PDF (F146 part 2); (b) pairs sharing a context and
a topic are few enough to judge (F146 part 1); (c) a shared function can
refuse an undecided field without changing what the live applier writes
(F147); (d) qubit-lab.ch's public pages state results with limits that
can be quoted (F145); (e) the counts a document names can be computed from
the store (F148).

**What would disprove each**: (a) the dry run finds HIGH assertions with
no quote stored: C counts them and lists them apart, as not checkable from
quotes; (b) the dry run counts more pairs than the cap allows: C reports
the count and a narrower screen, before any send; (c) Task D's trial apply
writes a field differently through the function: B is wrong, and is
fixed before D's live apply; (d) the pages state a verdict with no
quotable limit: E enters it LOW with that reason; (e) a count names a
quantity the store does not hold (for example a time): F leaves it typed
and lists it.

**The checks cannot merely confirm**: C's counts come from the store, not
the forecast; B's check compares the trial apply's writes before and
after; F's test compares the block with a fresh store read.

## Risks

| Risk | Mitigation |
|---|---|
| Money spent without a decision | q1 = c: no API send in F146; a test, proven red, that F146's scripts import no API client |
| The key leaks into output, a file or a commit | F146 reads no key (q1 = c); the hook on `.env` stays in force |
| F147 changes what an apply writes | D's trial apply compared before and after B; a verified backup before each live apply; a second apply writes nothing |
| An F146 proposal changes a grade without a decision | Results saved outside the store as proposals; nothing written without your decision; a test proven red |
| A vendor's claim graded too high (F145) | A vendor's own result, single source: its conflict of interest named in the record; certainty by `store.grading` |
| F114 and F146 compete for usage limits (q1 = c) | D's readers first; F146's subagents after D's reads, or paused at a limit and resumed, never cut short |
| A reader relabels a stored context or grade | The applier's stored-context guard and the "undecided" list, now also F147's function |
| A write reaches a sibling repository | Phase 2 read only; no fetch in a sibling repository |
| The email address, the OpenAlex key or the API key leaks | None is sent or printed; requests carry the UA "EvidenceBasedDB-fetcher/1.0" |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time; F146's state file for its sends |

## Definition of Done

- A: the next group named from the highest number plus one; its test proven red
- B: the shared function with its test proven red; the live applier moved and the one-time scripts (22, corrected from 23 on 2026-11-21) frozen by a test proven red (q2 = a); D's trial apply writes the same as before B
- C: both parts built, dry-run and forecast from the real counts; each rule tested and proven red; runs on Sonnet 5.5 subagents (q1 = c), each run's input and result saved, and the proposals counted and sampled for you; nothing written to the store without a decision
- D: 30 papers read in full, reviewed and applied once through B's function; Huang 2023 linked; the 3 list papers entered and the list's commit recorded; the counts before and after; a second apply writes nothing
- E: the source and its assertions entered with quotes checked and certainty graded; each link with its reason; the gated items listed; the note's proposals asked
- F: `scripts/doc_counts.py`, its blocks in `docs/INTAKE_WORKFLOW.md` and the summary, its test proven red
- CI green on the sprint PR before Manual Validation

## Out of scope

Applying any F146 proposal to the store (a decision after its results).
An ADR-0004 amendment for "corroborated by an independent study" as a basis
for HIGH (asked after F146's results, not built here). F39 (not selected).
F57 releases. F138 and F90 (HOLD). F144's batch reads of F114 papers.
Downloading any paper around a paywall. Requesting qubit-lab.ch's gated
material. Any write to `hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.
