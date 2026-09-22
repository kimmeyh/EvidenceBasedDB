# Sprint 4 Summary: Fix the Path, Fix the Records, Measure the Cost

Created 2026-09-22 per the three-doc rule (workflow 3.2.1), as part of
Phase 7 at the team lead's standing request. Sourced from git history, PR
#30, the issues, `docs/sprints/SPRINT_4_F11_TIMING_LOG.json` and
`docs/sprints/SPRINT_4_RETROSPECTIVE.md` -- never the master plan, which
this document instead feeds.

**Dates**: 2026-09-19 to 2026-09-22 (no deadline; `SPRINT_4_PLAN.md`'s own
scope statement).
**Branch**: `feature/20260919_Sprint_4`, PR #30 (draft at the time of
writing).
**Scope**: Task A (re-home the delivery cycle, F27), then F25 in full
(D2 the door, D3 amend-and-correct, D4 re-filing, D5 intake, D6
extraction), F11 after D3, plus F15-F17, F18, F20 and F26. Eleven tasks,
eleven issues (#31-#41), all closed.
**Worked by two sessions on one branch**: a managed remote session (Tasks
D, I, J, K) and a local session on the machine holding the PDFs (Tasks B,
C, E, F, G, H). Task A preceded both.

## What shipped

- **Task A** (F27): the delivery cycle re-homed. Backlog Refinement is
  Sprint N Phase 1 on the N branch; `sprint_status.json` advances at the
  carry-forward cut; the Stop hook and the plan-doc guard now agree by
  construction rather than contradicting each other for one turn. Proven
  by a simulated close-out in both directions. `77806d4`, #31.
- **Task B** (F25 D2): the ingestion door. `store/citations.py` derives
  citations and titles from arXiv, Crossref and DataCite;
  `validate_paper()` grew the rules that refuse the F10 defect classes
  (a hand-typed citation for a resolvable id, audit text inside a
  citation, a tier named in a disposition, an unanchored applicability
  rationale, a blank title, a bare "local file" access);
  `paper_fields.citation` dropped and the read-tier CHECK added in one
  migration with a byte-identical export; `value` became the title.
  16 guards, each proven to fail by injection. `95e8807`, #32.
- **Task C** (F25 D3): ADR-0005 amendment A2, then every F10 citation and
  access defect corrected by re-derivation rather than retyping. 22
  api-origin citations refreshed; 24 hand-origin records given real local
  paths and the visible hand-transcribed marker; `rand-2023` renamed
  `rand-2022` (decision Q4) with the foreign-key closure walked; `udaru`
  moved to hand-origin because its printed DOI is not registered at
  doi.org; `rand` and `freericks` moved to api-origin because registered
  DOIs exist. The Sprint 1 seed generator was retired: it was the old
  door. `7f1109f`, #33.
- **Task D** (F26): `store/export.py` batches its per-record child
  queries, 275 SQL statements down to 22 at 54 records, export
  byte-identical. `cf82289`, #34.
- **Task E** (F11): `scripts/render_f11_packet.py` generates the
  adjudication packet from the store -- the 18 F10-reviewed records, each
  with its primary-source link, its fields, its dated change history and
  F10's finding beneath it -- plus a timing sheet. `c3efab9`, #35.
- **Task F** (F25 D4): the world/method/ml re-filing pass across all 48
  papers, against context tests written down FIRST (in
  `docs/INTAKE_WORKFLOW.md` section 8, committed with Task G before this
  pass ran). 26 context sets changed. `method` 8 to 16 rows, `ml` 0 to 15,
  `platform:braket` 0 to 1; `world` stayed at 4 but moved off `arute` (an
  engineering demonstration) and `rand` (a policy report) onto `zajac` (a
  proved theorem) and `kerger` (proved round complexity). Every rationale
  anchored to where it was read. `72cdbf8`, #36.
- **Task G** (F25 D5, F12 absorbed): `docs/INTAKE_WORKFLOW.md` and
  `scripts/intake.py` -- one door for papers, repositories, references
  and books; derived ids; a bulk manifest path with per-entry commit and
  resume-by-id; `--verify` as the mechanized F10 protocol. A `github`
  access kind was added to `store/citations.py`, built from identity
  fields only so the refresh diff stays quiet across pushes. `64d067f`,
  #37.
- **Task H** (F25 D6): five papers promoted to `read` after direct page
  reads, five assertions extracted with GRADE-style certainty reasons
  (one high, one moderate, three low), and the first `contradicts`
  relation wired: `fourier-wall` against both CVQBoost accuracy claims,
  with `zajac`'s theorem supporting `fourier-wall`. `847ddd6`, #38.
- **Task I** (F15, F16, F17): the hook family -- auto-advance-window Stop
  hook, deliverables-commit hook, mutation-lock pair -- each with real
  subprocess tests, each proven by injection, each registered on its own
  matcher. `904bda7`, #39.
- **Task J** (F20): `docs/BACKLOG_REFINEMENT.md` wrapped as an invokable
  skill against the numbering Task A produced. `6e7406e`, #40.
- **Task K** (F18): `.claude/model_assignment_heuristics.json`, with
  protocol as a first-class field beside tier. `aba1310`, #41.

## Also delivered

- **The first-try proof (F25 C5)**: `arXiv:2602.11092` (MerLin) and
  `github.com/merlinquantum/merlin` through the finished door on the live
  store, `--verify` reporting 7/7 PASS on each with no correction pass
  afterward. At Manual Validation the third F12 example arrived (the team
  lead's LinkedIn link) and turned out to be the same thread: a post by
  the Fourier Wall author reading the MerLin paper. It went through the
  reference path, body saved verbatim outside version control. `2db9cf6`.
- **ADR-0005 A3 and ADR-0004 A5** (`fec2bcc`), written at the team lead's
  decision after A2, recording what the sprint added afterwards: the
  repository access kind, non-paper kinds by disposition prefix, derived
  ids, A2's pending items closed, and the four context tests as a
  refinement of ADR-0004's context table.
- **The CHANGELOG** caught up and its two guards fixed (`19f2089`): both
  had been parsing one heading of five since Sprint 1.
- **The Pere placeholder removed** at the team lead's direction
  (`c2f93d4`); the related papers now sit under `QMLPapers/` for a future
  sprint.

## Actuals

Wall clock is commit-to-commit from `git log` (local time); delegated-agent
figures are the tokens and duration each agent reported on completion.
Plan estimate was 785 Claude-side minutes, every card `[no-history]`.

- Phase 3.7 approval (12:02) to Task A commit (12:08): 6 min.
- Task B (the door, 16 guards + the migration): 86 min, 12:08 to 13:34.
  Estimate 120 min. Under.
- Remote session, Tasks D, J, K, I: 20:51 to 21:00 by its own commit
  times, four tasks. Estimates 30 + 20 + 45 + 90 = 185 min. Far under, and
  the figure understates the work: the commits are the end of a session
  whose start is not in this branch's history.
- Task C (amend + correct, including the arXiv 406 diagnosis): about 150
  min of local-session work ending 19:29. Estimate 90 min. **Over, about
  1.7x** -- the arXiv batch-refusal diagnosis was roughly 90 minutes of it.
- Task E (F11 packet + tests): 7 min, 19:29 to 19:36.
- Task G (intake design, script, tests, first-try proof): 16 min, 19:36
  to 19:52, with the evidence agent running in parallel. Estimate 90 min.
- Task F (re-filing all 48): 3 min to commit, 19:52 to 19:55, after the
  evidence agent's 472 s run. Estimate 90 min. The agent carried the
  reading; the judgment was written while it read.
- Task H (five papers to read, extraction): 8 min, 19:55 to 20:03, after
  the second agent's 183 s run. Estimate 120 min.
- Delegated agents: evidence gathering for Task F, 199,780 tokens / 472 s;
  evidence gathering for Task H, 133,883 tokens / 183 s. Both read-only,
  both reports spot-checked against the PDFs before use.
- Manual Validation items (Pere removal, LinkedIn reference, both ADR
  amendments, CHANGELOG): 23:36 to 00:18, about 42 min.
- F11 timing run: 22:33 to 22:52 on 2026-09-21, 19.4 min.
- Retrospective improvements 1-8: about 55 min on 2026-09-22.
- Tests: 255 at sprint start, 362 at Manual Validation, 395 after the
  retrospective improvements. Test files 22 to 36.
- Diff: 66 files changed, 7,981 insertions, 1,301 deletions (Task A
  through Task H).

## The measurement this sprint produced

**F11, the number ADR-0004 says the design is constrained by**: 1.08
team-lead minutes per record, 19.4 minutes for 18 records, 18/18 accept
with zero revisions (log:
`docs/sprints/SPRINT_4_F11_TIMING_LOG.json`; heuristics
`learning_log[1]`).

Recorded with its caveat, because the caveat is the finding. This was
CONFIRM MODE: records already corrected by Tasks C, F and H, each shown
with F10's own finding beneath it. Against F10's 599 s of model time on
the same 18 (33 s per record), the team lead spent about twice the wall
clock and confirmed everything. Two readings are both true: the
corrections held under a second, human pass; and by this repository's own
escalation trigger, a review that confirms everything with zero rejections
is evidence about protocol depth as much as about the records. What cold
adjudication costs was not measured. F29 cards it.

## Findings surfaced, now backlogged

- **F29** (new): cold-mode adjudication timing, the number F11 did not
  measure. `scripts/adjudication_timing.py --mode cold` and a packet
  variant that omits the findings block already exist for it.
- **Two Class 1 decisions** recorded in `docs/INTAKE_WORKFLOW.md` section
  10, both due before the first bulk book load: a `paper_fields.kind`
  column replacing the disposition-prefix convention, and an ISBN
  resolver for books without a DOI.
- **The bulk set arrived mid-sprint**: `QMLPapers/` now holds 1,618 files
  with per-year `manifest.tsv`. Section 9 of the intake design records
  what that means for the bulk path, so the bulk sprint does not
  re-derive it.

## Verification

- Full suite: 395 passed, 0 skipped, 0 failed (2026-09-22).
- Every guard added this sprint was broken, watched go red, and restored:
  16 in Task B, 12 in Task C, 7 in Task G, 5 in the seed-metadata guard,
  5 in the retrospective improvements.
- Committed export matches a fresh regeneration from the store
  (`tests/test_export_currency.py`).
- Store as of 2026-09-22: 48 papers (24 api-origin, 24 hand-origin);
  6 `read`, 14 `screened`, 28 `seen`; 87 applicability rows, all anchored;
  13 assertions; 12 `paper_yields`; 3 `contradicts`, 2 `supports`.
  `value == provenance` on 0 of 48.
- All eleven issues (#31-#41) closed; PR #30 checklist 11/11.
