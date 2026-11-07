# Sprint 16 Summary: Read Once, Check Once, Write Once, Then Test It on 20 Papers

**Dates**: 2026-11-05 to 2026-11-07. **Branch**: `feature/20261105_Sprint_16`.
**PR**: #164 into develop. **Issues**: #165 to #172 (Tasks A to H).
Sources: the plan (`SPRINT_16_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_16_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 70 to 74 (`docs/INTAKE_WORKFLOW.md`), and the telemetry
files in `manifests/sprint16_f114_reads/telemetry/`. Every count below is
a snapshot as of 2026-11-07.

## What shipped

- **F136 (Task A, #165, f286746).** Each PDF's text extracted once, into
  one text cache every store copy reads; the applier checks only the
  quotes it will insert or change, and a second apply checks nothing and
  writes nothing.
- **F139 (Task B, #166, 215354e).** One telemetry file per group (pages,
  reader and reviewer minutes and tokens, quote checks, cache misses,
  rows written, applies), a Sprint 15 baseline, and each "once" on the
  card put in place with a test proven red, or named with its reason.
- **F134 and F135 (Tasks C and D, #167 and #168, 0b83abf).** A table
  cell that holds only a number is kept and found; a stated limit on a
  measured result keeps its type in the prompt and the check.
- **F137 (Task E, #169, cd3b56b).** The two Dunjko records (arXiv
  1709.02779 and its 2018 journal version) held as one, through a shared
  `store/merges.py`.
- **F114 (Task F, #170, ea4f63b, db45ffc, db2abe3).** 20 papers read in
  full (531 pages) in six groups: g333 and g334 (the 6 new papers on
  Christophe Pere's list and the team lead's 2), g133-r1, g154-r1, g155
  and g156's first record. Each group applied with a trial, a verified
  backup, a live apply and a second apply that wrote nothing.
- **F57 (Task G, #171, ea4f63b).** The two named papers (the wangy8205165
  white paper and the QBoost paper, arXiv 2108.13346 v1) fetched once
  and read as two of F's 20.
- **F51 (Task H, #172, ea4f63b, db2abe3).** The CVQBoost findings record
  and its seven assertions; the seventh
  (`cvqboost-tuned-in-segment-wins-single-run`, LOW) added at Manual
  Validation. Phase 2's F162 and B4 are named in its reasons and not
  linked as contradicting it.

Store: 34,897 -> 36,209 assertions (HIGH 11,071 -> 11,491; LOW 23,726 ->
24,618); papers at `read` 1,805 -> 1,813, at `seen` 562 -> 554.

## Manual Validation decisions

- At planning (2026-11-05 and 2026-11-06): Q1 = 1, Q2 = 2, Q3 = 1, Q4 = 1
  (F51 released from HOLD), Q5 = 2 (each reviewer reads the paper in
  full), Q6 = 1 (one Dunjko record), Q7 = 1 (monographs are books, to
  F138).
- During the sprint: F140 carded (testing, risk-based and fast; team
  lead's request with Phase 2's card as a reference).
- At Manual Validation (2026-11-06 and 2026-11-07): Q1 = 3 (split
  `he-simulation-scope`; `qgan-training-testing-100-per-class` added,
  both HIGH), Q2 = yes (the seventh CVQBoost assertion), Q3 = 2 (F141,
  the paper view in full, carded), Q4 = 1 (a prompt for Phase 2 with
  experiments that would confirm or refute the seventh assertion).
- Retrospective (2026-11-07): "Very Good" in every rated category;
  "none" for minor updates, backlog updates and open questions. The five
  improvements: 1 to 4 into the Sprint 17 plan (F142), 5 to the backlog
  (F143).

## Actuals

Wall clock from `git log` and the status notes (local time). Plan
estimate for A to H: about 380 minutes at the cards' estimates, plus the
reader time in the background (no reading budget).

- Phase 1 and planning: 2026-11-05 18:52 to 2026-11-06 00:26 (plan
  approved).
- Tasks A to E: 2026-11-06 00:26 to 07:21, about 415 minutes for 240
  estimated (A 50m, B 120m timebox, C 30m, D 20m, E 20m in the plan). B took the most: the telemetry module and its baseline.
- Tasks F, G and H set up by 11:37; the reads and five applies done by
  15:55; Manual Validation hand-over at 16:05.
- After Manual Validation: g154-r1's split, apply and the seventh
  assertion committed 2026-11-07 00:22.
- Reading telemetry over the 20 papers (531 pages, 6 groups):
  - readers 397 minutes and 2,460,218 tokens (0.75 minutes and 4,633
    tokens per page; Sprint 15: 0.44 and 3,645);
  - reviewers 129 minutes and 1,711,769 tokens (0.24 minutes and 3,224
    tokens per page; Sprint 15: 0.14 and 1,676);
  - 5,709 quote checks, 0 text-cache misses, 219 pages rendered, 1,331
    live writes, 6 live applies.
- Unplanned time: the full suite before Manual Validation (1:08:43, one
  stale tier pin, fixed), the `--changed` gates after store writes (one
  ran 45:49), two reviewers re-run on long proof appendices, and gates
  that came back INVALID while readers wrote telemetry.
- Subagents: Sonnet 5.5 readers and reviewers per group, Opus 5.5
  sign-off, and one fresh-eyes reviewer per code or store commit.

## Findings surfaced

- The "once" work removed the repeated script work (0 cache misses; each
  second apply checked no quote), but the agents' cost per page rose
  (readers +27% tokens and +70% minutes, reviewers +92% and +74%).
  Task B's premise, that "once" would lower the agents' cost, was false.
  Carded as F143.
- The local full suite takes about 69 minutes (199 seconds in Sprint 12).
  Carded as F140.
- A paper that gives two reasons in one stored value needs a split, and
  the pipeline has no table for it (F142 part 2).
- A long proof appendix needs more than one reviewer from the start
  (F142 part 3).
- Reader telemetry inside the repository blocks every gate while a
  reader works (F142 part 1).
