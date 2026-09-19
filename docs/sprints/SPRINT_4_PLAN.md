# Sprint 4 Plan: Fix the Path, Fix the Records, Measure the Cost

**Dates**: from 2026-09-19. **No deadline.**
**Branch**: `feature/20260919_Sprint_4` (cut at Phase 6.6 carry-forward from
Sprint 3's branch, 2026-09-19)
**Scope** (DEFINED, team lead 2026-09-19), in the team lead's own order of
priority: a NEW first item -- re-home the Phase 8.* activities so that a
sprint is called by its branch's number from Backlog Refinement onward --
then **F15, F16, F17, F27** (the hook family), **all of F25** (task order
mine), **F11** when appropriate (after F25 D3), **F20**, **F18**, **F26**.
Also added to the backlog for Sprint 5 at the team lead's request: **F28**
(learn from the papers).

## Objective

Sprint 3 measured the paper records and found real defects in them and
in the path that produced them. Sprint 4 fixes the path first, then the
records through the fixed path, then finally produces the number three
sprints have deferred -- team-lead adjudication minutes per record --
against records worth adjudicating. Around that spine: the process
guards Sprint 3's survey found missing, and the export batching that
becomes necessary before roughly 1,200 papers and 6 books arrive.

## The correction this sprint starts with

Team lead, 2026-09-19: "need to adjust so that the Sprint # is called by
the same as the Branch Sprint # starting when you start Backlog
Refinement. Not sure how we ended up with Backlog Refinement as prior
sprint phase 8 while in other repositories it is an early next sprint
branch."

Verified against the docs, not recalled: `SPRINT_EXECUTION_WORKFLOW.md`
already carries BOTH shapes at once -- "Phase 1: Backlog Refinement
(mandatory, every sprint)" at the top of the phase list AND "Phase 8:
Delivery Cycle" at the bottom holding Refinement Pass 1 (8.2), the
design-doc currency check (8.3) and Refinement Pass 2 (8.4);
`BACKLOG_REFINEMENT.md` says refinement "runs TWICE per cycle as part of
Phase 8"; `SPRINT_CHECKLIST.md` lists the same under Phase 8. The
close-out Stop hook and `test_sprint_status_points_at_a_real_sprint`
then contradict each other for exactly the turns spent in that
mis-homed phase (F27), which is how Sprint 3's close-out got blocked.
Task A resolves the whole cluster at once, before anything else, so the
rest of this sprint runs -- and reports its status line -- as Sprint 4
from the moment the branch exists.

## Tasks

| # | Task | Est | Owner |
|---|---|---|---|
| A | **Re-home the delivery cycle and close F27.** Phase 8 shrinks to what genuinely belongs to the finishing sprint (team-lead merges; the 6.6 carry-forward cut). CHANGELOG reconciliation, Refinement Pass 1, design-doc currency and Refinement Pass 2 become Sprint N+1's Phase 1 (Backlog Refinement) and Phase 2 (Pre-Kickoff), on the N+1 branch. `sprint_status.json` advances to N+1 at the carry-forward with `status: phase_1_refinement`, `plan_doc: null`; the guard test requires a plan doc only from Phase 3 on; the Stop hook and the test then agree by construction. `BACKLOG_REFINEMENT.md`'s template becomes "Sprint N Candidates at a glance". Edits: `SPRINT_EXECUTION_WORKFLOW.md`, `SPRINT_CHECKLIST.md`, `SPRINT_PROCESS.md`, `BACKLOG_REFINEMENT.md`, master plan Maintenance Guide, `.claude/hooks/verify_closeout_complete.py` (plus its first behavioral test), `tests/test_sprint_documents.py`, the status-line memory rule. Proven by a simulated close-out in both directions | 60m `[no-history]`, timebox 90m | Claude, top tier (process design) |
| B | **F25 D2 -- build the door.** C1: `scripts/refresh_citations.py` fetching from Crossref (DOI), arXiv (id; plain User-Agent, see pre-flight) and DataCite, rendering a canonical citation and DIFFING against the store in review mode; `insert_paper()` derives `citation` from an `access` id, refusing a hand-typed one unless the record declares no resolvable id (then a visible "hand-transcribed from <page>" marker and a real local path). `scripts/seed_set_metadata.json` stops carrying `citation`. C2: `validate_paper()` rules per the Q1-Q3 decisions (tier obligations; `access` must be DOI/arXiv/existing local path; one-line disposition; no audit-trail markers in `citation`; no tier named in a disposition; every applicability rationale ends with a source anchor). C3/B4: `insert_paper()` takes one bibliographic input; `paper_fields.citation` dropped or derived per Q2; `value` becomes the title. Every rule with a failing test | 120m `[no-history]`, timebox 180m | Claude, top tier for design; Sonnet subagents for rule tests |
| C | **F25 D3 -- amend, then correct through the door.** B3: ADR-0005 dated amendment per Q1 (and the read-tier CHECK added to the schema alongside Q2's migration). B1: the four defects (`dupont` title, `kordzanganeh` author, `rand` year and id per Q4, `mancilla` false duplicate claim), the six superseded preprints, `pelofske`/`rehman`/`zajac`/`qci-2024` citation gaps, and the three `access` fields, all re-derived via C1 rather than retyped; audit trail moved from `citation` to `updated_reason`/`evidence` (`loke`, `kordzanganeh`, `lubinski`, `mancilla`). Export regenerated; every change a dated `updated_reason` | 90m `[no-history]`, timebox 120m | Claude, top tier |
| D | **F26 -- batch the export's child queries.** One query per related table per class, grouped in Python, byte-identical export as the acceptance test (the determinism property is the thing at risk). Measured baseline 276 statements / 8.8 ms at 54 records | 30m `[no-history]`, timebox 45m | Sonnet subagent, Fable review |
| E | **F11 -- team-lead adjudication timing** on the 18 screened records as corrected by Task C, using the F10 protocol with the same primary-source access (local PDFs, arXiv/publisher pages). Claude prepares the packet (record sheet, source links, per-record timing and protocol log) and records the result as the first real number against ADR-0004's constraint; the row goes into F18's `learning_log` | packet 30m; timing team-lead paced | **Team lead** (timing); Claude (packet, recording) |
| F | **F25 D4 -- the world/method/ml re-filing pass** across all 46 papers: write the three context tests down first, then apply them; state the qml-via-workload and qc-subsumption rules; fix the incomplete-in-the-wrong-direction rationales; one-line dispositions; every surviving rationale names its source anchor. Tests that pin applicability sets updated in the same commit with the reason, never loosened | 90m `[no-history]`, timebox 120m | Claude, top tier (judgment) |
| G | **F25 D5 -- the intake workflow (F12 absorbed) and the first-try proof.** Design for the three source types AND for bulk: ~1,200 papers and 6 books incoming (arXiv asks 3 s between requests, so a full arXiv pass is about an hour; Crossref polite pool). Books per Q5. Every source type converges on the C1-C3 door. Then the three F12 examples through the finished path, and C5's single-record acceptance test with no human correction pass afterward | 90m `[no-history]`, timebox 120m | Claude, top tier |
| H | **F25 D6 -- extract the contradiction.** Promote `loke`, `emami`, `qci-2024-profiling`, `mancilla`, `zajac` to `read` via `set_tier()` (each then owing `checked_against_source` and `yields`), extract the opposing assertions with GRADE-style `certainty_reasons`, wire `contradicts`; the three smaller F10 notes as `evidence`/`supports`; confirm which Neven paper CVQBoost's lineage rests on | 120m `[no-history]`, timebox 150m | Claude, top tier |
| I | **F15, F16, F17 -- the hook family.** Auto-advance-window Stop hook with an EvidenceBasedDB fixture set; Phase 3.3.1 deliverables commit hook (`pr`/`github_issues` fields); mutation-lock pair with staleness handling. Each a real subprocess test, each proven by injection, each registered under its own matcher (the `test_hook_registration.py` discipline) | 90m `[no-history]` total, timebox 120m | Sonnet subagents in parallel, Fable review |
| J | **F20 -- wrap `BACKLOG_REFINEMENT.md` as a skill**, against the phase numbering Task A produces | 20m `[no-history]`, timebox 30m | Haiku or Sonnet subagent |
| K | **F18 -- the model-assignment heuristics file**, seeded with the F7-F10 `learning_log` entry already in its card plus Task E's team-lead row; protocol as a first-class field beside tier | 45m `[no-history]`, timebox 60m | Claude, top tier |

**Sequence**: A first (everything after it reports as Sprint 4 correctly
and closes out cleanly). Then B -> C -> D in that order: the door before
any correction passes through it; the export batching after the schema
settles so it batches the final shape. E (F11) runs after C, per the team
lead's "after D3?" -- yes, exactly there, so the team lead times corrected
records; it is team-lead paced and does not block F-K. F -> G -> H
complete F25. I, J and K are independent of the F25 chain: I can run any
time after A (subagents in parallel); J after A; K after E.

**Total ~785 minutes of Claude-side work** (about 13 hours) plus the
team-lead-paced F11 timing, plus the standing 30% findings allowance --
larger than Sprint 2's 720 and the largest plan yet. Calibration: Sprint
3's Actuals show 46 minutes of coordinator wall clock for eight tasks
because forks and subagents carried the reading; these estimates are
coordinator-plus-subagent effort, still `[no-history]`, and Task E is the
first item ever timed by the team lead. **If a Criterion 3 stop becomes
necessary, the cut line is after Task G** (H and K are the natural
deferrals; F25 D1-D5 and F11 are the sprint's spine). Deferring approved
work is a Class 3 decision and is never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Crossref**: `api.crossref.org/works/<doi>` returns full metadata
  (title, container, authors) in 0.17 s. PASS.
- **DataCite**: `api.datacite.org/dois/<doi>` returns metadata in 0.77 s
  (first sample DOI 404'd because it does not exist, not because of the
  API). PASS.
- **arXiv**: `export.arxiv.org/api/query` returns **HTTP 406** to `urllib`
  with User-Agents of the form `Mozilla/...` or carrying a
  `(mailto:...)` block, regardless of `Accept`; returns 200 with a plain
  UA such as `curl/8.0`, and via `curl -L`. PASS with a documented
  gotcha that C1 must encode. The probe also independently confirmed
  F10's `dupont` finding: the real title is "Quantum-Enhanced Greedy
  Combinatorial Optimization Solver", 16 authors.
- **Data precondition** (SPRINT_PLANNING.md, Sprint 2 improvement 3):
  `D:\Data\Harold\EvidenceBasedDB\` holds Papers 46 (the seed set --
  the ~1,200 are NOT there yet), Books 44 (was 38: the 6 new books have
  arrived), GitHubRepos 8, References 0. Task G designs for the bulk
  arrival; nothing in this sprint depends on the 1,200 being present.
- **Plan-to-branch verification** (3.2.2.1): none of the planned
  artifacts exists yet (`refresh_citations.py`, the three hook files,
  the skill, the heuristics file); the four process docs reference
  "Phase 8" in the places Task A targets.

## Decisions for the team lead at approval (numbered; answer with digits)

These are F25's four D1 decisions plus one raised by the incoming books.
They shape Tasks B, C and G, so they are answered with the plan rather
than mid-sprint.

- **Q1. The `screened` tier**: (1) demote every screened-with-zero-yields
  paper to `seen`; (2) amend ADR-0005 section 2c to define `screened` as
  "dispositioned and applicability-derived, not yet mined", with
  `checked_against_source` and `yields` as the `read`-tier obligations.
  Recommend 2.
- **Q2. `paper_fields.citation`**: (1) drop the column (table rebuild,
  test updates), adding the read-tier CHECK in the same migration; (2)
  keep it and derive it from `provenance` in `insert_paper()`. Recommend
  1.
- **Q3. Applicability rationale evidence**: (1) a source anchor by
  convention at the end of every rationale ("-- p.1 keywords"), guarded
  by a regex; (2) an explicit `evidence_anchor` column (schema change,
  Class 1). Recommend 1 now, 2 as the next amendment if 1 proves loose.
- **Q4. `rand-2023-...`'s id carries the wrong year**: (1) rename to
  `rand-2022-...` now, cascading through `record_contexts` and
  `paper_applicability` (nothing yields from it yet); (2) keep the id,
  record the correction in `updated_reason`. Recommend 1.
- **Q5. The 6 books** (Books/ grew 38 -> 44; the `Books` record class is
  out of scope per the master plan): (1) Task G designs the book path as
  part of the intake workflow (design only, no class added, no book
  ingested this sprint); (2) books stay staged and out of scope entirely
  until a later sprint. Recommend 1.

## The measurement that outranks the code

**Team-lead adjudication minutes per record (Task E, F11)**, against the
18 corrected records, using F10's protocol. ADR-0004 names it the number
the whole design is constrained by; Sprints 1, 2 and 3 each deferred it
for a stated reason. This sprint produces it, and F18 records it beside
the four model tiers' costs (Haiku 182 s, Sonnet 155 s, Opus 208 s,
Fable-tier 599 s for the same set).

## Premise falsifier

**The premise**: guarding the ingestion path first, then correcting the
records through it, yields a store whose 46 records pass the F10
protocol without a human correction pass, and a door through which the
47th (and the 1,247th) paper enters the same way.

**What would disprove it**: (1) C1's diff mode, run against all 46
papers, shows that API-derived citations disagree with the store on far
more than the defects F10 named -- if that is formatting (author
initials, venue abbreviations) the canonical renderer needs a decision;
if it is substance, F10 under-counted and Task C grows; (2) Task G's
single-record acceptance test needs a human correction after the record
passes every guard -- meaning a guard is missing and Task B is not done;
(3) Task A's simulated close-out fails either the hook or the test in
the new numbering -- meaning the re-homing moved the contradiction rather
than removing it.

**The check cannot merely confirm**: the C1 diff is run and read before
Task C starts, not after; the C5 record is a real paper (the arXiv
example from F12); the close-out simulation runs a real Stop-hook payload
and the real test against a scratch status file, in both the passing and
the failing direction.

## Risks

| Risk | Mitigation |
|---|---|
| Task A changes the process docs, the hook, the test and the status file at once; a slip strands the next close-out | Simulated close-out in both directions before A's commit; the hook gets its first behavioral test; Sprint 4's own close-out is the live test |
| F25 D2-D6 is two sprints of work in one card, and this plan adds five more items around it | Named cut line after Task G; Criterion 3 stop with original-vs-new estimates if any task hits 2x; nothing deferred unilaterally |
| Q2's table rebuild (dropping `paper_fields.citation`) touches every paper row and several tests | Migration script is dry-run by default (QUALITY_STANDARDS.md), export byte-identical before/after except for the intended `value` change, and the divergence guard from PR #20 stays until the column is gone |
| arXiv rate limits (3 s between requests) make the bulk path slow | Task G designs the bulk path around it (batch id_list queries, which arXiv supports; resume from a checkpoint); the 1,200 are not ingested this sprint |
| The re-filing pass (Task F) is judgment-heavy and changes applicability on many of the 46 records | Context tests written down before the first record is touched; each pinned test updated with its reason in the same commit; the F9/F10 record is the checklist |
| Team-lead timing (Task E) does not happen inside the sprint | F11 has been deferred three times for good reasons; the packet is prepared early (after C) and the sprint does not block on it -- F-K continue; if it slips, F18 seeds from the four model rows and adds the team-lead row when it lands |

## Definition of Done

- Task A: the four process docs, the master plan's Maintenance Guide, the
  hook, the guard test and the status-line rule all describe ONE
  numbering in which Backlog Refinement is Sprint N+1 Phase 1 on the
  N+1 branch; `sprint_status.json` advances at the carry-forward; a
  simulated close-out passes both guards, and a simulated stale file
  fails both; F27 closed
- F25 D2: `refresh_citations.py` diffs all 46 papers against Crossref/
  arXiv/DataCite in review mode; `insert_paper()` derives `citation`
  from an id and refuses hand-typed input without the declared exception;
  every C2 rule has a test proven to fail; `value` is the title;
  `paper_fields.citation` is resolved per Q2; `seed_set_metadata.json`
  no longer carries citations
- F25 D3: ADR-0005 amendment landed per Q1 (dated, appended); every B1
  correction applied through C1 with a dated `updated_reason`; no audit
  trail remains inside any `citation`; `access` fields resolve
- F26: statement count per `regenerate()` no longer grows with record
  count; export byte-identical before and after
- F11: the team-lead minutes-per-record number recorded with its
  protocol, or, if timing did not happen, the packet delivered and the
  deferral recorded as a Class 3 decision -- never silently
- F25 D4: the three context tests written in the plan of the pass before
  it ran; all 46 papers re-filed against them; tests updated with reasons
- F25 D5: the intake design covers papers, references, repos, and (per
  Q5) books, converging on the door; the three F12 examples are in the
  store; one real paper passed the F10 protocol with no correction pass
- F25 D6: five papers at `read` with yields; the `contradicts` relation
  between the mancilla/zajac and CVQBoost assertions exists and exports
- F15, F16, F17: three hooks registered on their own matchers, each with
  a subprocess test proven by injection
- F20: the skill exists and its first step is reading the format doc in
  the same turn
- F18: the heuristics file exists with at least the F7-F10 row and the
  protocol field; the team-lead row added if Task E produced it
- Full test suite green before every commit; every guard proven to fail
  by injection; export currency green at every commit

## Out of scope

Ingesting the ~1,200 incoming papers or the 6 books (Task G designs the
door; F5 and Sprint 5 walk them through it). **F28** (learn from the
papers) -- carded for Sprint 5 at the team lead's request. **F19** (resume
guide and startup-check skill) -- not selected. **F5** -- not selected.
Any change to the consumer repository or to `spamfilter-multi` beyond
read-only reference.
