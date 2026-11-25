# Sprint 19 Decisions

Every question (q) and improvement (i) of Sprint 19, stored in full (F151,
team lead 2026-11-22: "please store all quesitons, decisions and
Improvement in full. If you still need an answer to one and it has
scrolled off the screen, always re-ask with the full contents every
time").

The rules:

- Each entry is written here, in the AUTHORITATIVE shape of
  `docs/SPRINT_RETROSPECTIVE.md`, BEFORE it is shown.
- A message that needs an answer shows EVERY open entry, pasted from this
  file unchanged. `.claude/hooks/block_procedural_question_stop.py` blocks a
  reply that asks an item not stored here, leaves out an open entry, or
  changes an entry's text.
- The answer is recorded under its entry, verbatim, with its date read
  from the clock: `- **Answer** (team lead, YYYY-MM-DD): "..."`. An entry
  with no Answer line is open.
- A fact that changes after asking goes in a dated `- Changed since asked
  (YYYY-MM-DD): ...` line under the entry; the entry is never edited.

q1 to q7 were asked before this file existed (Task A builds it) and are
back-filled here from the messages that showed them. q5 was shown twice:
once with ledger-order options, then revised after the team lead asked,
"Did F57 have a relative rating system that could be applied to the new
combined list?"; the revised entry is the one answered.

## q1. Where the 306 papers read only in part belong
- Asked: 2026-11-24 (the Sprint 19 plan draft)
- What it is: 306 papers were read in part in Sprints 9 to 12, before the
  2026-10-25 rule that every read is full. They are outside F114's ledger
  and are at `read`, so F57 ("seen and screened") does not hold them
  either. No card reads them again.
- What it prevents and/or catches: it prevents 306 papers keeping partial
  claims forever because no card names them.
- Prevention or control: prevention.
- Long-term value: every paper in the store is read in full, as the
  2026-10-25 rule asks.
- Evidence: the 1,507 records with no full read reconcile exactly (858 +
  306 + 168 + 173 + 2); 279 of the 306 have a local copy.
- Extends: F57 and the 2026-10-25 full-read rule.
- Effort: about 10m to change the card; the reads about 8,000 pages and
  about 7,900 agent minutes over later sprints.
- Options:
  - **a. (Recommendation)** The 306 added to F57 as its second list, read
    after F57's never-read papers, in F57's order.
    - Pro: one card holds every paper outside the ledger.
    - Con: F57 grows from 151 to 457 papers.
  - **b.** A new card for the 306, with its own priority.
    - Pro: its priority is set apart from F57's.
    - Con: one more permanent card; the two share an order rule.
  - **c.** No change: the 306 keep their partial reads.
    - Pro: no reading time spent.
    - Con: they stay outside the full-read rule, unlisted.
- **Answer** (team lead, 2026-11-25): "a. but as a combined list with a note as to what needs to be done for each paper (fields - full read, local,...). Update priorities across the combined list using the F114 priority method." Then: "Add the 306 to F114 list before updating the combined list with re-calculated priorities using the F114 method."

## q2. How F57's 30 are filled, when at most 29 have a free copy
- Asked: 2026-11-24 (the Sprint 19 plan draft)
- What it is: of F57's 151 papers, 29 have a free copy (fetcher dry run),
  and some of those links may refuse a download.
- What it prevents and/or catches: it prevents a release that silently
  reads fewer than asked, or fills with papers not chosen.
- Prevention or control: prevention.
- Long-term value: each release says where its papers came from.
- Evidence: the dry run of 2026-11-24; 122 with no free copy.
- Extends: F57's known limit (a record with no free copy cannot reach
  `read`).
- Effort: about the same in every option, about 26 agent minutes per
  paper.
- Options:
  - **a. (Recommendation)** Every F57 paper whose copy downloads (up to
    29), then the rest of the 30 from the top of q1's 306.
    - Pro: 30 papers read, as asked.
    - Con: a few of the 30 are re-reads of papers read in part.
  - **b.** Only the F57 papers whose copies download, no fill.
    - Pro: only never-read papers.
    - Con: fewer than 30.
  - **c.** The fill from F114's ledger instead.
    - Pro: no change to F57's card.
    - Con: F114 reads more than the 40 set, under F57's name.
- **Answer** (team lead, 2026-11-25): "after combining the F57 and F114 lists per q1, the combined number should be 60 (not this is new now that they are combined) that have free copies."

## q3. Which ledger papers make up F114's 39
- Asked: 2026-11-24 (the Sprint 19 plan draft)
- What it is: F114's card says "the ledger, in its order". The first
  groups not read in full are g157 to g294 (688 papers read in part);
  Sprints 17 and 18 skipped them without saying why.
- What it prevents and/or catches: it prevents the skip continuing as an
  unstated rule.
- Prevention or control: control (it records the order).
- Long-term value: the card says the order every release follows.
- Evidence: `scripts/sprint13_g_status.py` reports g157 to g294 as `not
  started`.
- Extends: F114's order rule; q20's split (2026-11-09).
- Effort: about 5m; the same reading time either way.
- Options:
  - **a. (Recommendation)** Never-read papers first (g372 onward), then
    g157 to g294.
    - Pro: each read adds claims to a paper that has none.
    - Con: the 688 read-in-part papers wait about 4 more sprints.
  - **b.** The card's literal order: g157 onward.
    - Pro: the card's words, unchanged.
    - Con: papers with no claims wait longer.
- **Answer** (team lead, 2026-11-25): "If there are 1,507 records with no full read """The 1,507 records with no full read add up exactly: 858 + 306 + 168 + 173 + 2""" For every one that is not read, add the next one so that 60 total can be read. Make sense?" The order itself was decided by q5.

## q4. The plan
- Asked: 2026-11-24 (the Sprint 19 plan draft); re-shown 2026-11-25
- What it is: the Sprint 19 plan, Tasks A to G, rewritten from the
  answers as Tasks A to F (one 60-paper reading task).
- What it prevents and/or catches: approval opens the auto-advance window;
  without it no task starts.
- Prevention or control: control.
- Long-term value: a defined sprint.
- Evidence: the plan's pre-flights.
- Extends: Phase 3.7.
- Effort: about 503 coordinator minutes plus about 1,800 agent minutes of
  reading, as first drafted.
- Options:
  - **a. (Recommendation)** The plan approved as written (later: as
    rewritten from the answers).
    - Pro: work starts now.
    - Con: none known.
  - **b.** Approved with changes named (later: the rewritten plan reviewed
    first).
    - Pro: changes absorbed before work starts.
    - Con: one more round.
- **Answer** (team lead, 2026-11-25): "Sprint plan approved as amended (with any comments I provided), proceed with execution. All Sprint tasks and sub-tasks are approved."

## q5. How the combined list is ordered
- Asked: 2026-11-25 (revised the same day)
- What it is: after the 306 and F57's 151 join F114's ledger, the list
  needs one priority rule. F114's method is (1) new PDFs in `Papers\`, (2)
  new papers on Christophe Pere's list, (3) papers named, (4) the ledger
  in its order, which is alphabetical inside its buckets, not a relevance
  ranking.
- What it prevents and/or catches: it prevents an alphabetical order
  deciding which papers are read first.
- Prevention or control: control.
- Long-term value: every sprint reads the most relevant remaining papers,
  by one rule.
- Evidence: the ledger script's docstring; F57's ranking, used in Sprints
  9 to 13 and 17; about 299 never-read and 1,016 read-in-part readable
  papers (2026-11-24).
- Extends: F114's order rule and F57's relevance ranking.
- Effort: about 20m in the list script, plus a few minutes of OpenAlex
  requests at each selection.
- Options:
  - **a. (Recommendation)** Steps 1 to 3, then every never-read paper,
    then every paper read in part, each part by F57's ranking (context,
    then citations).
    - Pro: papers with no claims first, the most relevant of each part
      first.
    - Con: the read-in-part papers wait until the never-read ones with a
      copy are done.
  - **b.** Steps 1 to 3, then the whole list by F57's ranking, mixed.
    - Pro: the most relevant paper is always next.
    - Con: some sprints re-read papers with partial claims while never-read
      papers wait.
  - **c.** Steps 1 to 3, then the ledger in its existing order, new groups
    appended.
    - Pro: no counts needed.
    - Con: the order stays alphabetical.
- **Answer** (team lead, 2026-11-25): "b - for all the papers with no abstracts and citations in order to relative prioritize - add a backlog item across 4 sprints to read the abstract and citations (see the old F57 ranking process) and update the F114 list item with the updated priority. F114 continues with the highest priority N items where the paper can be read in each sprint."

## q6. Where the combined list lives
- Asked: 2026-11-25
- What it is: the combined list, with a note for each paper.
- What it prevents and/or catches: it prevents a hand-kept list that
  drifts from the store (determinate facts are computed, never stored).
- Prevention or control: prevention.
- Long-term value: the list is current every time it runs.
- Evidence: the hand-download list already works this way
  (`scripts/hand_download_list.py`).
- Extends: the hand-download list and F114's ledger.
- Effort: about 60m for option a, inside the reading task.
- Options:
  - **a. (Recommendation)** A read-only `scripts/reading_list.py`, one line
    per paper (group, context, citations, what it needs, its copy), with a
    test that fails on a paper listed twice or a readable paper missing.
    - Pro: computed, never stale, one place to look.
    - Con: about 60m to build.
  - **b.** A one-time list in the master plan.
    - Pro: about 30m less now.
    - Con: stale after the first read.
- **Answer** (team lead, 2026-11-25): "a"

## q7. What happens to F57's card
- Asked: 2026-11-25
- What it is: once its papers join F114's ledger, F57 holds no papers of
  its own.
- What it prevents and/or catches: it prevents two cards claiming the same
  papers.
- Prevention or control: prevention.
- Long-term value: one card reads every paper.
- Evidence: on 2026-11-05 F95 and F98 were folded into F114 the same way.
- Extends: that 2026-11-05 decision.
- Effort: about 10m.
- Options:
  - **a. (Recommendation)** F57 folded into F114: its ranking becomes
    F114's priority method; at each release F114 adds the papers intake
    entered at `seen` since the last release; the card removed, its
    history in git.
    - Pro: one card, one list, one ranking.
    - Con: F57's history only in git.
  - **b.** F57 kept as a permanent card that only feeds new `seen` papers
    to F114's ledger.
    - Pro: its card stays in the master plan.
    - Con: a card that reads nothing.
- **Answer** (team lead, 2026-11-25): "a - and any new "seen" papers get added to the f114 list (when it runs next sprint)"
