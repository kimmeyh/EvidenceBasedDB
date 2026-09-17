# Sprint 1 Summary: Build the Store

Created during Sprint 2 planning per the three-doc rule (workflow 3.2.1).
Sourced from git history, PR #1, PR #10, and `docs/sprints/SPRINT_1_
RETROSPECTIVE.md` -- never the master plan, which this document instead
feeds.

**Dates**: 2026-09-15 to 2026-09-17 (no deadline; SPRINT_1_PLAN.md's own
scope statement).
**Branch**: `feature/20260915_Sprint_1`, merged to `develop` via PR #1
(2026-09-17T04:16:13Z), then `develop` merged to `main` via PR #10
(2026-09-17T04:16:43Z).
**Scope**: implement the Evidence Based DB and load the seed set (tracked
in the consumer repository as F77), extended mid-sprint with Task H (F1,
native to this repository): remove hsbc-quantum-fraud-2026 process content
inherited at seeding.

## What shipped

- **Task A**: CI running the five inherited guards. The five PowerShell
  hooks converted to Python during pre-kickoff so the hazard class
  `test_hook_registration.py` guards against (a doubled-backslash JSON
  escape) is closed by construction rather than continued vigilance.
- **Task B**: SQLite schema for the four record classes (`assertion`,
  `acronym`, `term`, `paper`) per ADR-0004 section 3 and ADR-0005 section 2.
  Every CHECK constraint and foreign key verified by injection to actually
  reject its violation.
- **Task C**: deterministic JSON export as the committed artifact (ADR-0004
  section 2). Byte-identical re-export of unchanged data proven; a
  currency test guards the committed `export/` against the real store.
- **Task D**: domain-scale contexts seeded (9 total: the 3 pilot contexts
  plus `ml`, `qc`, `qml`, `platform:dirac-3`, `platform:braket`,
  `platform:classiq`), ahead of ADR-0004's own "add only when forced" rule
  by team-lead decision, since the full set was confirmed needed within
  the sprint.
- **Task E**: the Lenat/Marcus paper ingested end to end, proving the
  ingestion path Task F would run 46 times. Found and fixed a real gap in
  ADR-0005's own worked example (a `supports` link naming an assertion the
  ADR never actually drafted). The adjudication-time measurement this
  task's premise-falsifier design called for was deliberately deferred by
  team-lead decision, moved to F75.
- **Task F**: 44 distinct paper records loaded at `seen` (46 seed files
  minus two exact duplicates), 17 promoted to `screened` for variety.
  Citations extracted from real PDF content via background research, not
  guessed from filenames -- caught a filename-truncated arXiv id, an empty
  seed file, and (post-hoc, team-lead review) a citation missing a
  co-author entirely.
- **Task G**: a determinate-fact resolver for the consumer repository's
  amendment count (32, computed live against its `PREREGISTRATION.md`),
  per CLAUDE.md's standing rule that determinate facts are computed, never
  stored.
- **Task H (F1)**: removed hsbc-quantum-fraud-2026 process content (a
  Dirac-3 hardware-approval rule, `experiments/src` paths, `results.json`/
  `prereg-freeze` artifacts, a consumer-specific submission calendar)
  presented as this repository's own live rules, across 11 governing docs
  and 3 ADRs. A regression test (`test_no_source_repository_process_
  leakage.py`) verified by injection to guard against recurrence.

## Also delivered, outside the original eight tasks

- A hook (`block_sibling_repo_writes.py`) blocking writes into
  `spamfilter-multi` or `hsbc-quantum-fraud-2026` from this repository's
  sessions, team-lead directive mid-sprint. Read access stays unrestricted.
- Seven memory files and a `CLAUDE.md` "Things Claude Should NOT Do"
  section ported from spamfilter-multi (plain-numbered questions,
  re-presenting instructions rather than referencing scrollback, and
  related communication preferences that never reached this repository at
  seeding because hsbc-quantum-fraud-2026 itself never carried them).
- PR #1 review (Copilot + Claude, both requested and completed): found and
  fixed a real FK-coupling bug (`assertion_documents` blocked on
  `assertion_fields` rather than `records`), a silently-dropped
  `citation_context` field, and a `--promote` ordering bug. All three
  fixed with regression tests before merge; six further findings backlogged
  as F6.

## Measurement Sprint 1 did NOT produce

**Team-lead adjudication time per record** -- ADR-0004 names this "the
number the whole design is constrained by." A partial review ran
(~7 minutes against one paper record and its assertions) and was then
deliberately stopped: "I would like to remove the review and leave
everything up to your best, informed... We will get back to validating
the DB contents at a future step in a future backlog item." This is now
F75's job, against ~20 real records rather than one.

## Findings surfaced at Manual Validation and PR review, now backlogged

- **F2**: deep-dive spamfilter-multi (read-only) for reusable process
  assets -- hooks, memories, CLAUDE.md, skills, sprint orchestration,
  sprint-card design, model-selection heuristics, task-estimation method,
  architecture docs/ADRs, PowerShell-to-Python candidates.
- **F3**: an easy, CLI-startable way to view DB content by context, by
  paper, and by assertion.
- **F4**: validate the store against the HSBC submission's own
  determinations, and against the 44 source papers read directly. Carries
  a real gap: every paper record has exactly one `context` even though
  ADR-0005 defines a separate plural `applicability` field that was never
  populated during Task F.
- **F5**: identify QCi-affiliated paper authors, find their other work
  (arXiv, then DOI, then Google Scholar), and scrape QCi's own Dirac-3/
  `eqc_models`/training documentation -- all staged under
  `D:\Data\Harold\EvidenceBasedDB\References\`, never committed here.
- **F6**: six further PR #1 code-review findings (redundant citation
  storage, unenforced tier validation, missing per-record transaction
  boundaries, export N+1 queries, duplicated path-resolution boilerplate,
  duplicated export-function shape) -- each a moderate-scope design
  question, not a quick fix.
- **F75, F76**: carried from the consumer repository's own backlog, both
  now actionable (F77/Task F complete, 44 papers loaded past the 20-paper
  threshold both ADRs name for their own checkpoint).

## Retrospective outcome

16 categories x 4 roles, all rated "Very Good" by the combined Product
Owner/Scrum Master/Lead Developer feedback. The Development Team draft
(Claude) agreed on outcome while surfacing real friction underneath: three
smoke-test false negatives from shell-quoting (fixed as a stated
`subprocess.run()` convention, applied immediately), a documentation debt
(ADR-0004/0005 carry zero Sprint 1 amendments despite crossing their own
20-paper checkpoint, folded into F75), and a risk that materialized
without being named in the plan (the single-context-per-paper undercount,
folded into F4). Full detail: `docs/sprints/SPRINT_1_RETROSPECTIVE.md`.

## Verification

Full test suite: 105 passed, 1 skipped (pre-existing, unrelated), CI green
on every push to the feature branch and on the merge to `develop`.
