# Sprint 16 Plan: Read Once, Check Once, Write Once, Then Test It on 20 Papers

**Dates**: from 2026-11-05. **No deadline** (Phase 2's PoC notification
date, 14 Nov 2026, is the nearest outside date).
**Branch**: `feature/20261105_Sprint_16` (cut at the Phase 6.6 carry-forward
from Sprint 15's branch, 2026-11-05, after PR #149 merged to develop and PR
#163 to main; tagged `sprint-15`)
**Scope** (DEFINED, team lead 2026-11-05): F136, F134, F135, F137, F114,
F57, and a new card the team lead asked the Coding Agent Team to write,
F139 (reading efficiency), "completed before running F114 this sprint so
that the reading updates can be tested". The team lead's changes at
selection:

- F95 and F98 are folded into F114. F114 reads 30 papers per sprint by
  default, all sources together, and 20 this sprint "to test out the new
  reading updates".
- F114 no longer reads books. Books move to a new card, F138, on HOLD.
- F51: the team lead asked "Does this still have to be on hold?" (Q4).
- F39 was not selected, so model assignments rest on Sprint 13's release
  (F111) and `.claude/model_assignment_heuristics.json` as updated in
  Sprint 15.

## Objective

Make each paper's read cost what it must and no more: each PDF's text
extracted once, each quote checked once, each row written once, with the
time and tokens per page and per paper measured (F136, F139). Close the
two reader-check defects Sprint 15 found (F134, F135) and settle the
Dunjko records (F137). Then test the new pipeline on F114's 20 papers,
new ones first, and read the two papers the team lead named under F57.

## Tasks

Est is coordinator time for the judgment steps. Sprint 15's `## Actuals`:
about 1,205 minutes estimated; the reads ran in the background over about
3 days, and about 48 minutes were lost to repeated work (a trial without
its text cache, and quote checks of unchanged groups). Each task that
changes `store/`, `scripts/` or a hook carries one fresh-eyes review and
fix cycle. Runtime is separate, with its dominant term.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F136, extract once and check once.** One text cache location that every store copy reads (today `<store dir>\text_cache\`, so a copy elsewhere misses it); the applier compares each assertion with its stored row and checks only what it will insert or change; a second apply checks nothing and writes nothing; a changed quote is still checked; INTAKE's rule reads "every write is checked; an unchanged row is not". Each with a test proven red | 50m | a trial on a store copy (seconds once the cache is shared) | Claude, top tier |
| B | **F139, read once, check once, write once.** Step 1: the telemetry file per group (pages, figures, reader and reviewer minutes and tokens, quote checks, cache misses, rows written, applies) and a Sprint 15 baseline from its progress files. Step 2: each "once" on the card put in place with a test proven red, or named with the reason it is not; the reviewer's read per Q5. Step 3: the measures on F114's first group set against the baseline before the other groups start | 120m [no-history] timebox | none for steps 1 and 2; step 3 is F114's first group | Claude, top tier |
| C | **F134, number-only table cells.** A page number is still dropped; a number-only table cell is kept or found another way; each with a test proven red; every stored quote still matches word for word (the live quote tests) | 30m | the live quote tests over 34,891 assertions, from the shared cache | Claude, top tier |
| D | **F135, a stated limit's type.** The reader prompt names the type of a stated limit on a measured result; the check and the prompt agree; a test proven red | 20m | none | Claude, top tier |
| E | **F137, the Dunjko records**, per Q6. They are one paper: the arXiv preprint (1709.02779) and its journal version (Reports on Progress in Physics 81(7), 2018). Each assertion ends under the record Q6 names, each move with its note; the local-file check passes | 20m | one store write, with its verified backup | Claude, top tier (certainty) |
| F | **F114, 20 papers under the new pipeline.** Order per Q1: the 6 papers new on Christophe Pere's list at 399b022651 (none in the store), any unnamed PDF in `Papers\` (none on 2026-11-05), then the ledger from the first group not yet read in full. Books excluded per Q7. The Sprint 15 reader prompt with B's, C's and D's changes; up to 5 local readers; review per Q5; the coordinator's sign-off and the team lead's certainty decisions; one apply. Also: `scripts/hand_download_list.py` and the `hand-download-list` skill name F114 instead of F95 | 30m (prompt) + 50m (review and sign-off, at Sprint 15's 2.4m per record) | no estimate as a limit (no reading budget). The dominant term is the whole-paper reads with their figures; B's telemetry on the first group sizes the rest | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| G | **F57, the two named papers** (size per Q2): the wangy8205165 white paper `Quantum_NeuralNetwork.pdf` (2,082,720 bytes on GitHub), entered as a paper record linked to its repository record, and the QBoost paper per Q3; each fetched once into `Papers\` and read in full under F's pipeline, after F's readers | 15m + 10m (review) | two downloads, one GitHub request and one arXiv request | as F |
| H | **F51, per Q4.** If released: the CVQBoost findings record and its six assertions entered from the 2026-08-04 document (SHA-256 `425358a7b4cec71f...`), each graded by what the document shows (single runs are measured results), with Phase 2's F162 result (no in-pocket win repeats over ten seeds) linked as contradicting where it bears | 45m (only if Q4 = 1) | one store write, with its verified backup | Claude, top tier (certainty) |

**Sequence**: A first (the team lead's Sprint 15 retrospective Q1). B next,
because it changes the pipeline F uses. C and D then, because they change
the reader's check and prompt. E and H while F's readers run. F's first
group is B's step 3; F's other groups start only after its measures are
reported in the status note. G after F's readers, in the same slots. One
apply at a time. Total about 345 minutes at the cards' estimates (390 if
Q4 = 1), plus the reader time in the background. No findings allowance:
the scope is not dominated by verification.

**If a Criterion 3 stop becomes necessary, the cut line is inside F**: F
stops at the groups it has reviewed, and the rest stay in F114. Deferring
approved work is a Class 3 decision and is never made unilaterally.

**Full suite** (workflow, Phase 4): twice, before the Manual Validation
hand-over and after any retrospective improvements. Every other commit
runs `python scripts/run_suite.py --changed` and CI's set on the PR.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-11-05): PR #149 merged to develop (7dca2c9) and
  PR #163 to main (dff5c49, tagged `sprint-15`); no open sprint issue;
  working tree clean except this plan's own edits. Dependency check: `uv
  pip list --outdated` on the OCR environment lists nothing outdated
  (`rapidocr` 3.10.0, `onnxruntime` 1.31.1, pinned in
  `requirements-ocr.txt`). Tests: the document guards pass locally (32
  tests); CI's set runs on the draft PR.
- **The store (snapshot as of 2026-11-05)**: 2,358 papers; 1,836 with a
  read row, 522 with none; 34,891 assertions (11,071 `high`). F114: 892
  of 1,430 ledger records not read in full, in 190 groups.
- **F114's new papers**: Christophe Pere's list moved from ea6f42a7c0 to
  399b022651 (2026-11-05); its 6 new papers are not in the store by id
  or link. `Papers\` holds 386 PDFs; none saved after 2026-11-01 is
  unnamed.
- **Books in F114 and F57** (rule on F114's card, Q7): Simeone 2022 (229
  pages, read in part) and Cichocki 2016 (176 pages, no read row) in the
  ledger; Freericks 2026 and Schuld 2018 (both Springer books) in F57.
  `Books\` holds 44 PDFs, none in the store. A page count over F114's 892
  records found 9 over 150 pages; by their titles the other 7 are
  reviews, theses or long articles (titles only, not yet checked).
- **F137's premise**: arXiv 1709.02779 (one version, 2017-09-08) and DOI
  10.1088/1361-6633/aab406 (Crossref: Reports on Progress in Physics
  81(7), 2018-06-19, same authors, title plus "a review of recent
  progress") are one paper. The card assumed two papers sharing a PDF.
- **G's papers**: the white paper is on GitHub (2,082,720 bytes). arXiv
  2108.13346 has only v1 (2021-08-30, "11 pages, 3 figures");
  `arxiv.org/abs/2108.13346v2` returns 404. The repository's
  `qboost.pdf` is 486,746 bytes; which paper it holds is not known
  without downloading it. The store has no record of 2108.13346.
- **F51's hold**: both copies of the findings document still hash to
  `425358a7b4cec71f...` (2026-08-04). Phase 2's develop (43bc362) cites
  the document as "planning reference only" in several places and holds
  no re-run of it; its F162 (2026-10-23) re-tested the in-pocket wins
  over ten seeds and none repeats reliably.
- **Plan-to-branch verification** (3.2.2.1): no Task A to H artifact
  exists yet; F136, F134, F135, F137, F114, F57, F51 are open cards; F138
  and F139 are new and free.

## Decisions for the team lead

Each is answered by a digit; each ends with a recommendation.

- **Q1. Which papers make up F114's 20?** (1) The 6 new on Christophe
  Pere's list first, then 14 from the ledger: the new papers are read in
  the sprint they appear, as F98 did. (2) 20 from the ledger, and the 6
  new ones wait for the next sprint's 30. (3) 20 from the ledger plus the
  6 new as extras (26 papers, about a third more reading). Recommend 1.
- **Q2. How many F57 records does Sprint 16 read?** (1) Only the two
  papers you named, read after F114's 20 under the same new pipeline (22
  papers in all). (2) The two named papers inside F114's 20, so the sprint
  reads 20 in all. (3) The two named papers plus 18 from F57's ranking (40
  papers in all, about twice the reading). Recommend 1.
- **Q3. Which copy of the QBoost paper is read?** arXiv has no version 2
  of 2108.13346; it lists only v1 (2021-08-30). (1) arXiv v1, the only
  arXiv version, as "get from arxiv" asked; one request. (2) The
  repository's `qboost.pdf`, whatever version it holds; its title page is
  checked against arXiv v1 first and the difference reported. (3) Both
  are fetched, and only the one whose title page matches what you meant
  is read; you decide at Manual Validation. Recommend 1.
- **Q4. Does F51 stay on HOLD?** It waits on a re-run that Phase 2 is
  not doing: Phase 2 uses the document as a planning reference only, and
  it has not changed since 2026-08-04. (1) Release it into Sprint 16
  (about 45 minutes): the record and its six assertions are entered from
  the 2026-08-04 document, and Phase 2's F162 result is linked where it
  contradicts. The store can then cite the findings by record. (2)
  Release it from HOLD to the backlog at Priority 50, for a later sprint.
  (3) Keep it on HOLD. (4) Close it: Phase 2's stored results cover the
  question. Recommend 1.
- **Q5. Does the reviewer read each paper in full a second time?** Today
  each group's reviewer reads the whole paper with its source, so each
  paper is read twice. Sprint 15 sent one reviewer back for deciding items
  from quotes alone. Per-paper token figures do not exist yet; F139
  measures them on the first group. (1) Decide after F114's first group:
  the first group runs both ways (a full second read, and a read of only
  the passages each assertion cites plus the checker's flags), F139
  reports the time, tokens and findings of each, and you choose before the
  other groups start. (2) Keep the full second read: no loss, and each
  paper costs about two reads. (3) The reviewer reads only the cited
  passages and the flags: about half the reading cost per paper, but no
  second reader looks for what the first reader missed. Recommend 1.
- **Q6. How does the store hold the two Dunjko records?** They are one
  paper: the arXiv preprint and its 2018 journal version. (1) One record:
  the journal record keeps the paper, with the arXiv id added to its
  access; the 2017 record's assertions move to it, each with a note; the
  2017 record is closed as a duplicate that names the journal record.
  Counts then show one paper. (2) Two records, linked as preprint and
  journal version; the assertions stay under the 2017 record. Counts show
  two papers for one work. Recommend 1.
- **Q7. Are monographs books?** Under the rule on F114's card, a whole
  book or a monograph (an ISBN, a whole-book DOI, or a series such as
  Foundations and Trends) is a book. (1) Yes: Simeone 2022 and Cichocki
  2016 leave F114 for F138 with the two Springer books from F57. (2) No,
  only whole books with an ISBN: the two monographs stay in F114 and are
  read as papers. Recommend 1.

## Premise falsifier

**The premises**: (a) most of a paper's cost beyond its first read is
repeated work; (b) checking a quote once, when it is written, keeps every
stored quote verbatim; (c) the pipeline still reads every section,
appendix, proof and figure; (d) the two Dunjko records are one paper.

**What would disprove each**: (a) B's telemetry on the first group shows
the repeated steps are a small share of time and tokens: B reports it,
and the "once" changes that do not pay are named and dropped; (b) a live
quote test finds a stored quote that no longer matches its source: the
check-once rule is wrong for that case and returns to the team lead; (c) a
review finds a section or figure not read and not named in `not_read`:
the read is sent back; (d) the journal PDF differs from the preprint in
its content: E reports it and Q6 is asked again.

**The checks cannot merely confirm**: the live quote tests read the
source text from the cache, not the reader's copy; Q5's first group runs
both reviews on the same papers, so the comparison can come out either
way.

## Risks

| Risk | Mitigation |
|---|---|
| Fewer checks let a wrong quote through | Every write is still checked once against the source text; the live quote tests read every stored quote |
| A lighter review misses what a reader skipped | Q5 decides from measured findings on the same papers, not from a forecast |
| The shared text cache is written by two runs at once | One apply at a time; the cache key is the file's SHA-256; A writes each cache entry whole (to a temporary name, then renamed), with a test |
| Telemetry adds work to each reader | Counted by the scripts and the agents' own reports, not by hand |
| A reader relabels a stored context or grade | The applier's stored-context guard and the "undecided" list |
| A usage limit stops a reader mid-paper | Progress and restart, unchanged |
| A write reaches a sibling repository | Phase 2 read only, through local refs and the GitHub API; no fetch in a sibling repository |
| The email address or the OpenAlex key leaks | Neither is sent: arXiv, Crossref and GitHub requests carry a generic client name |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: the shared cache, the check-only-what-changes applier and the INTAKE
  wording, each with a test proven red; a rerun checks no quote
- B: the telemetry file for every F114 group; each "once" in place with
  its test, or named with its reason; the first group's measures set
  against the baseline and reported before the other groups start
- C, D: each with a test proven red; every stored quote still verbatim
- E: per Q6; the local-file check passes for the Dunjko record or records
- F: F114's 20 papers read in full, figures and image pages included,
  reviewed per Q5 and applied once; the 6 new list papers per Q1; no book
  read; the counts before and after; a second apply writes nothing
- G: per Q2 and Q3; each named paper read in full and applied
- H: per Q4
- Full suite before Manual Validation, through `scripts/run_suite.py`;
  every other commit gated on `--changed` and CI's set; CI green on the
  sprint PR before Manual Validation

## Out of scope

F39 (not selected). F138 and F90 (HOLD). F114 past its 20 papers. F57
past Q2's answer. Downloading any paper around a paywall. Any write to
`hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
