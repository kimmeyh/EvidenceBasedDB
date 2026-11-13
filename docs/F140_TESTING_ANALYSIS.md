# F140: Testing analysis (Sprint 17 Task A)

Status: findings complete; the recommendations wait for the team lead's
answers. Each is presented as its own item (q4 to q14) in the shape of
`docs/SPRINT_RETROSPECTIVE.md`, "Presenting improvements, questions and
decisions", and the answers are recorded at the end of this document.
**Every count, time and percentage here is a snapshot as of
2026-11-07.** The suite and the store both grow, so a number here is
true of that day only.

## Summary

- The local full suite took 44m34s on 2026-11-07 (1,615 tests). Sprint
  12 ran 1,202 tests in 199 s. The test count grew 34%; the time per test
  grew about 10 times (0.17 s to 1.66 s).
- The slowdown came in two steps (Part 2): the store's data grew (F114's
  first apply of 7,715 assertions on 2026-10-30, about 5 to 15 to 25
  minutes), then Sprint 15's thin-page check started `pdfinfo` once per
  PDF in every test process (about 40 to 60 minutes from 2026-11-04).
- The second cause is fixed (5454ccb, and its review fixes): the page
  count is kept on disk. The slowest test went from 230 s to 37 s.
- After the fix a full run took 37m48s (1,618 tests), while the new cache
  filled for the first time and one gate ran beside it. The 10-minute
  target is not met. The live-store data checks are 69% of the time, and
  the work they do grows with every paper read.
- This machine has 32 processors and the suite uses one. Running the
  suite in parallel (q4) is the one lever large enough for the target.
- Sprint 16 spent about 547 minutes in 12 gates during its 15.6 hours of
  task execution. 130 of those minutes were two INVALID runs, and 99
  were two FAILED runs.
- Reviews in Sprints 13 to 16 found 11 classes of defect that no test
  caught first. Five classes (A, F, G, H, J) still have no test that
  covers the class; each has a named cheapest test (q10 to q14).

## Part 1: the inventory

`docs/test_inventory.json`, written by `python scripts/test_inventory.py
--junit FILE --write`. One row per test file: what it guards (the first
sentence of its docstring), its kind, its tests and seconds from a timed
full run, where it runs (`full`, `ci`, and the change that picks it under
`--changed`), whether its docstring records a red proof, and the last
time it caught a real defect where one is on record (`CAUGHT` in the
script). `tests/test_test_inventory.py` fails when a test file is
missing, when a row names a file that is gone, and when a computed field
differs from what the script computes now. `run_suite --changed` runs it
on any test-file change.

By kind (seconds of test time):

| Kind | Files | Run 1 (before) | Run 2 (after) |
|---|---|---|---|
| live-store data check | 63 | 1,888 (71%) | 1,562 (69%) |
| hook check | 12 | 513 (19%) | 312 (14%) |
| unit | 35 | 180 (7%) | 301 (13%) |
| document check | 14 | 59 (2%) | 75 (3%) |
| guard | 5 | 8 | 8 |

129 test files; 109 record a red proof; 113 run on CI. The hook and unit
times moved between runs with no change to those tests: run-to-run
variation on this machine is large, so a single run's seconds are a
guide, not a measurement to two figures.

## Part 2: why local is slow

Measured: run 1 (2026-11-07, before the fix, `pytest --durations=0
--junitxml`): 44m34s wall, 2,647 s of test time, 1,615 passed. Run 2
(after the fix): 37m48s, 1,618 passed. Run 2 filled the new disk cache
for the first time, and a 22.8-minute gate in the other checkout
overlapped its first 5 minutes. A warm run has not been timed alone.

### The history of the full suite (from the session logs' `SUITE` lines)

- 2026-10-23: 13 minutes (1,175 tests), then 3 minutes once F100's text
  cache landed (1,202 tests; Sprint 12's "199 s warm").
- 2026-10-25 to 2026-10-30: 4 to 5.5 minutes (1,303 to 1,476 tests).
- 2026-10-30 20:40 and 2026-10-31: 8, then 15 to 25 minutes (1,476 to
  1,485 tests). This followed b185729 (2026-10-30 20:18), F114's first
  apply: 7,715 assertions, each a quote the live-store checks verify
  against its PDF.
- 2026-11-04 to 2026-11-06: 39 to 69 minutes (1,520 to 1,578 tests).
  This followed Sprint 15's OCR work (d485069, in the working tree from
  2026-11-04): the thin-page check calls `page_count`, which started
  `pdfinfo` once per PDF in every process.
- 2026-11-07: 29.6 minutes (a gate), 44m34s (run 1, timed), 37m48s
  (run 2, timed, after the fix).

### Causes, in order

1. **pdfinfo started once per PDF per process (fixed).** `page_count`
   was cached for the process only. In
   `test_sprint13_reading::test_every_quote_is_in_its_source[1]` that was
   390 starts and 180 of 230 s (cProfile). The fix keeps the page count
   and the per-page fallback in the text cache, keyed on the file's
   SHA-256 and poppler's version and options. With the cache filled the
   test takes 37 s.
2. **The store's data grew.** The quote checks read every quote of every
   read paper against its PDF. The slowest warm test,
   `test_sprint12_reading::test_every_quote_is_in_its_source[G]`, takes
   37 s: 18.6 s builds the plain text of 384 PDFs (89 million
   characters), and its own second `plain()` of each text adds 5.5 s.
   This is real work, and it grows with every paper read.
3. **Process start costs 0.3 to 0.6 s on this machine.** Measured:
   `pdfinfo -v` 0.598 s, `python -c pass` 0.413 s, `cmd /c exit` 0.312 s.
   A typical Windows machine starts Python in well under 0.1 s, so the
   likely cause is real-time antivirus scanning of each new process. This
   is an inference; it was not proven (q5).
4. **Hook checks start one Python process per test.** 397 tests in 12
   files, 312 to 513 s. `test_block_commit_with_piped_tests.py` is the
   slowest at about 3.9 s a test. These tests run the real hook in a real
   subprocess on purpose: an in-process call would not catch a hook that
   fails to start.
5. **A store copy per test.** `live_copy` copies the 78 MB store with
   SQLite's backup API for each test that uses it; the slowest setup was
   24.75 s (`test_full_read_apply`). Minor in total.

Checked and not a cause: store queries without an index (none of the 40
slowest tests is a store query); a fixture that hashes the store per
test (the store stamp is size and modification time); pdftotext calls
the text cache misses (Sprint 16 recorded 0; the run 2 profile shows
none); the number-line pattern in `quotes.plain` (3.1 s over 768 texts,
the same as a pattern that cannot cross a line break).

### The 10-minute target

Not met. The reason is cause 2: the data checks do real work that grows
with the store, on one processor of 32. The levers, largest first: run
the suite in parallel (q4); run the data checks only when the store
changed (already in place, Part 6); trim the duplicate `plain()` in the
quote tests (q6).

## Part 3: effectiveness

### Guards that cannot fail

20 test files record no red proof in their docstring (the
`red_proof_recorded` column). Each is a candidate for a guard that cannot
fail; none was proven vacuous in this analysis. Seven guards in Sprints
13 to 16 were found vacuous by review (class A below).

### Tests that pin a value the planned work changes

One on record: before Sprint 16's Manual Validation an intake test pinned
the tier "seen", which the planned reads changed to "read" (db45ffc). It
went red for a reason that was not a defect. Duplicate guards were not
measured: no method in this analysis finds them reliably, and none is
claimed.

### Defects reviews found that no test caught first (Sprints 13 to 16)

Found by a research subagent from the retrospectives, INTAKE_WORKFLOW and
git history. Every cited commit exists and its subject fits its class;
one commit for each class without a test (A f599950, F d740d72, G
25d3985, H 6e4bfb7, J Sprint 15 retrospective section 15) was read in
full and agrees.

- A. A guard that could not fail (7): 44e2512, f599950, 8f2b408, fed2d56,
  bb82d0a, 0b83abf, and the figure-exemption half in Sprint 15's
  retrospective. Cheapest test: replay each guard's recorded injection
  and require red (q10).
- B. A bypass spelling of a static rule (6): ed53933, 6173bad, b6cdcd0,
  745c6e6, 7758890, ac91f2f. Tested now by each fix's cases.
- C. A pattern edge case (5): 44502b8, 8c869cc, 9c79048, 59233c1,
  c60cfe9. Tested now.
- D. An edit or decision dropped or keyed wrong (4): 57107f1, c827018,
  7914e80, 4e75c07. Tested now.
- E. A protection keyed on a date (2): 80fcbb9, 8c10247. Tested now.
- F. An applier wrote a field no review decided (4): 4d969d9, ed5ab01,
  aabdd49, d740d72. The guards are narrow; the class is wider. Cheapest
  test: a trial apply whose diff fails on any stored field no review
  item names (q11).
- G. Stored text edited by a pattern (1): 25d3985. Cheapest test: no
  stored reason holds a stale "pending escalation" phrase (q12).
- H. A documented count not derived from the store (5 or more): 5e10948,
  bb82d0a, 80fcbb9, 6e4bfb7, 6d5bcec, f1257c1. Cheapest test: a
  live-store test that recomputes each snapshot count INTAKE_WORKFLOW
  cites, from a manifest of (section, query, value) (q13).
- I. A subprocess failure read as empty (1): c60cfe9. Tested now.
- J. An agent read less than the whole paper (4): g146, g149, Dawid's
  book, Monaco and Heimann. Partly guarded (7758890). Cheapest test:
  refuse a review whose cited pages cover less than the PDF's page count
  (q14).
- K. A currency test narrower than its lapse (1): the CHANGELOG 19 commits
  behind in Sprint 13. Tested now (71705d8, 8a06bf5).

Tests that went red on a real defect, recorded in the inventory's
`last_caught`: test_f65_dirac3s_reading (2026-10-22, Issue #116);
test_sprint12_reading, test_sprint13_reading and test_sprint13_g_apply
(2026-10-28, 5e10948); test_changelog_currency (2026-10-28, db8aeb7 and
af2c2ca); test_intake (2026-11-04). The subagent also named a catch by
test_f65 on 2026-10-30 or 31 and a `--changed` catch on 2026-11-05
(8c10247); neither was found in the cited records, so neither is
recorded.

## Part 4: risk tiers

Risk is likelihood times impact (ISTQB CTFL v4.0.1, section 5.2).

- High impact: a missed defect damages the store or a boundary. The
  appliers with their backup and second-apply checks, `store/merges.py`,
  the certainty grading and escalation in `f117_review.py`, provenance,
  and the sibling-write, commit-verdict and `--no-verify` hooks.
- High likelihood: code changed this sprint or changed often (Memon et
  al., ICSE-SEIP 2017).
- Proposed rule: the high-impact test files run on every gate; the
  others when `--changed` picks them (q8).

## Part 5: selection

`--changed` today matches names: a test file is picked when it names the
changed module, or names a script that imports a changed `store/` module.
A change to `store/__init__.py`, `tests/conftest.py`, a pytest file or a
requirements file runs the full suite. An import-aware pick would narrow
the `store/__init__.py` case, but every store test imports `store`, so
the gain there is small. `--ff` (last failures first) is cheap and loses
nothing (q9).

## Part 6: store-data checks apart from code checks

Already in place (F139, Sprint 16): `run_suite` records the store's stamp
when a run that covered every store test passed, and `--changed` adds the
63 live-store files only when the stamp has changed since. So a store
write costs one live-store run at the next gate, not one per gate.
Sprint 16's 45-minute gates were those runs, after each apply.

Telemetry writes inside the tree made two Sprint 16 gates INVALID (130
minutes). Task C (F142 part 1) moves telemetry out of the tree this
sprint; this analysis does not duplicate it.

## Part 7: red proofs

A proof runs once, by hand, and the docstring records it. A proof is
stale when its test, the guarded code, or a shared fixture has changed
since. Outside practice runs mutation analysis on changed lines only
(Petrovic and Ivankovic, ICSE-SEIP 2018). Class A (q10) is the same
problem seen from the defect side.

## Part 8: which full runs, and where

The local full suite runs twice a sprint (Sprint 11 I2): before Manual
Validation and after the retrospective. CI runs the non-store set and has
no store, so it cannot replace the local run (q7).

### Sprint 16's gate timeline

Rebuilt from `.claude/sprint_status.json`'s history (`git log -p`), the
commit times, and the `SUITE` verdict lines in the session log. The
verdict file `.claude/suite_verdict.json` keeps only the last run and is
not committed, so the session log is the record. Times are local (UTC-5;
two anchors agree: the 02:24 gate and commit f286746, the 15:54 gate and
commit db45ffc at 15:55). Each time is when the run ended; it started
its duration earlier.

| Ended | Verdict | Tests | Minutes | Scope | During |
|---|---|---|---|---|---|
| 11-06 02:24 | PASSED | 1,550 | 60.2 | full | Task A commit |
| 11-06 04:29 | PASSED | 968 | 46.0 | targeted | Task B commit |
| 11-06 05:11 | PASSED | 974 | 29.1 | targeted | Tasks C and D |
| 11-06 05:49 | PASSED | 974 | 32.6 | targeted | Tasks C and D commit |
| 11-06 06:39 | FAILED | 1,077 | 30.2 | targeted | Task E |
| 11-06 07:21 | PASSED | 1,124 | 26.7 | targeted | Task E commit |
| 11-06 08:32 | INVALID | 1,108 | 39.9 | targeted | Tasks F to H, readers writing |
| 11-06 10:14 | INVALID | 1,108 | 89.8 | targeted | Tasks F to H, readers writing |
| 11-06 11:37 | PASSED | 1,108 | 75.7 | targeted | Tasks F to H commit |
| 11-06 15:06 | FAILED | 1,578 | 68.7 | full | before Manual Validation |
| 11-06 15:54 | PASSED | 1,097 | 45.8 | targeted | reads commit |
| 11-06 15:58 | PASSED | 231 | 2.1 | targeted | F140 card |

Total 547 minutes of gate time inside 15.6 hours of task execution
(00:26 to 16:05). Gates overlapped reads in the background, so this is
not 547 minutes of idle time; it is the time a commit waited.

## Part 9: not applied

Learned test selection (Machalica et al., ICSE-SEIP 2019) is not
applied. This repository has too few test failures to train on. Recorded
so it is not proposed again without that history.

## Recommendations

Asked as q4 to q14 in the Sprint 17 message of 2026-11-07 (q1 to q3 were
F144's). Each answer is recorded here when it comes.

- q4. Run the suite in parallel (pytest-xdist). Team lead, 2026-11-07:
  a, "however, when doing parallels verify that the parallel execution
  can be completed (not stalled due to locked files, 2 processes changing
  the same file...)".
- q5. Test whether antivirus causes the slow process start. Team lead:
  c, with a request for a step-by-step walkthrough of a real-time
  exclusion for `D:\Data\Harold\github` and `D:\Data\Harold\EvidenceBasedDB`
  that keeps the weekly scan. Given 2026-11-07 (contextual exclusions,
  `ScanTrigger:OnAccess`, and a weekly custom scan task); the before and
  after timing waits on the team lead applying it. Then found
  (2026-11-08): Defender is in passive mode, and Norton 360 is the
  active scanner, so the Defender steps do not apply. The team lead
  applied Norton 360 exclusions for both folders ("both are listed").
  The full suite on the same tree took 10m16s before and 6m57s after;
  this is one run each, so run-to-run variation is not ruled out.
- q6. Drop the duplicate `plain()` in the quote tests. Team lead: a.
- q7. Skip the second full run when the retrospective changes nothing.
  Team lead: a.
- q8. High-impact test files run on every gate. Team lead: a.
- q9. Last failures first on every gate. Team lead: a.
- q10. Replay each guard's recorded injection (class A). Team lead: "skip
  until proven valuable and then only for items missed/caught". Recorded
  as skip and track: a guard that misses a defect, or catches one, gets
  its replay then.
- q11. A trial apply fails on a field no review named (class F). Team
  lead: "the recommended is not prevention as prevention is keeping it
  from ever happening (improved requirements/card, improved development
  methodology...)". Re-presented with prevention options. Team lead,
  2026-11-09: a. One apply function that refuses any field no review
  decided, carded as F147 for Sprint 18; and now, a card-template line
  in `docs/BACKLOG_REFINEMENT.md`: a card for an applier lists every
  field it writes.
- q12. No stored reason holds a stale phrase (class G). Re-presented.
  Team lead, 2026-11-09: "make note for future sprints in case we see
  more of these in the future". Recorded as skip and track: seen once
  (25d3985); a second case brings back the computed status (stored
  reasons hold no status words; the status is computed when a record
  is read).
- q13. Snapshot counts in INTAKE recomputed from the store (class H).
  Team lead: effort must give the cost to build and the cost to run, and
  how often. Re-presented. The rule is now in
  `docs/SPRINT_RETROSPECTIVE.md`. Team lead, 2026-11-09: a. A count
  generator, `scripts/doc_counts.py`, carded as F148 for Sprint 18.
- q14. A review that cites fewer pages than the PDF is refused (class J).
  Team lead: "none of these prevents it - what can we do so that it NEVER
  comes back without reading all the pages - 100% reading of all the
  pages." Re-presented with page-chunked assignment. Team lead,
  2026-11-09: "NO, read the whole paper". No chunking: a paper is read
  whole, as the full-read rule says.

## Acceptance (from the card)

- A test fails when a test file is missing from the inventory: yes,
  `tests/test_test_inventory.py`, proven red three ways.
- Every timing measured: yes, two timed full runs, a profile of the
  slowest tests, and the gate history.
- The 20x cause named with its evidence: yes, Part 2: the data growth and
  the pdfinfo starts, each tied to its commit.
- The full suite under 10 minutes, or the reason it is not: not met at
  first (the reason and the levers are in Part 2). Met after q4, q6 and
  q9 (snapshot 2026-11-07): the full suite through `run_suite.py` on 16
  workers passed 1,642 tests in 4m58s. The trial before it, 1,641 in
  6m51s, finished under a one-hour limit with the tree unchanged and no
  file left half-written. This is a dated amendment; the summary above
  is kept as written.
- Sprint 16's gate timeline rebuilt: yes, Part 8.
- Target stated: an approved small change verified and committed in its
  development time plus about 15 minutes. Today a `--changed` gate that
  adds no store tests takes 1.5 to 10 minutes (Sprint 17 gates); a gate
  that adds the store's tests takes about 25 to 45 minutes, which q4
  addresses.
