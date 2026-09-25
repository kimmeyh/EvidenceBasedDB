# Changelog

Policy: updated in the SAME commit as the change it describes, under
`## [Unreleased]`, grouped by date, newest first. Format:
`- **type**: Description (Issue #N / PR #N)` with type in
feat | fix | docs | test | chore | process.

**Workflow step 8.1.1 reconciles this file BEFORE backlog refinement, every
delivery cycle.** The same-commit policy held for six days in the consumer
repository and then silently stopped for eight, across seven sprints. A policy
that depends on remembering at the moment of committing is the class of rule
this project keeps having to replace with a step.

## [Unreleased]

### 2026-09-23 onward (Sprint 5, PR #43)

- **docs**: Sprint 5 scope (F31, F30, F28, F5), F19 and F29 closed without
  implementation, F32-F35 carded for Sprint 6, plan approved with decisions
  Q1-Q6 (PR #43)
- **feat**: store durability (Task A, F30, Issue #44) --
  `scripts/rebuild_store_from_export.py` rebuilds the store from the
  committed export through the real door and proves the regenerated export
  byte-identical (it is, first run); `store/backup.py` takes a SQLite-API
  backup before every live `--apply`, verified at creation, with three-rule
  retention (32 days; newest of the last 5 sprints; never before its content
  is committed); `scripts/restore_store.py` restores and verifies;
  `validate_paper(check_local_paths=False)` is the one explicit exception the
  rebuild needs to run on CI; 14 tests, each guard carrying its own injection
- **feat**: HSBC Phase 2 bibliography downloaded (Task B, F31 part 1, Issue
  #45) -- `scripts/sprint5_bibliography.py`: 120 entries, 64 arXiv PDFs plus
  web, vendor and challenge copies saved under the existing material folders
  (Q1 = 2), 9 found already on disk and 3 already in the store, none fetched
  twice; `BIBLIOGRAPHY.md` preserved under `References/`; 14 items on a
  manual-download list with reasons. A saved page with fewer than 50 visible
  words is treated as a failure, after four publisher bot-challenge pages, a
  JavaScript-only page and a redirect stub were first saved as "copies"
- **docs**: QCi-affiliated people identified from the papers themselves
  (Task E, F5 sub-part 1, Issue #48) --
  `docs/research/2026-09-24_F5_qci_affiliated_people.md`: 18 people, each
  verified on a named page; none of the SMU/Loke authors is QCi-affiliated;
  Task F's disambiguation rule written before any search hit was read
- **feat**: HSBC Phase 2 bibliography processed into the store (Task C, F31
  part 2, Issue #46) -- `scripts/sprint5_bibliography_manifest.py` generated
  121 entries under context rules written first (`INTAKE_WORKFLOW.md`
  section 11); `intake.py` wrote 121, refused 0 (73 arXiv, 16 DOI, 10
  repositories, 22 hand-origin); `--verify` 7/7 on a sample of every source
  type. DOIs used only when written, derived-and-confirmed, or found by
  exact title plus year, first author and venue (an exact-title match first
  picked a 2015 conference abstract for a 2014 Nature paper). `intake.py`
  now records when DataCite, not arXiv, supplied the metadata (68 records).
  `test_every_paper_has_real_applicability` aligned to ADR-0005 A2: the
  obligation is `screened`'s, not `seen`'s, with an injection test
- **docs**: F36 carded (Task D, F31 part 3, Issue #47) -- the nine per-entry
  elements of the bibliography a paper record cannot hold, each classed as
  computed (a resolver) or stored, a dry-run back-fill for existing papers,
  and "decide together with F34"; reading notes deliberately NOT a field
- **feat**: QCi's own documentation and package pulled (Task G, F5 sub-parts
  3-4, Issue #50) -- `scripts/sprint5_qci_site.py`: of the sitemap's 2,755
  URLs, 1,660 older package versions and 170 duplicate mounts skipped per
  Q3 = 1; 544 pages saved under `References/QCi-site/`, 1 reused from Task
  B, 25 dead sitemap links (HTTP 404) listed; `eqc-models` 0.21.0 sdist and
  wheel saved, sha256-verified against PyPI. The plan estimated about 300
  pages; the latest package docs alone are 462
- **feat**: learning from the papers, designed and piloted (Task I, F28,
  Issue #52) -- `docs/LEARNING_SYNTHESIS.md`: a key learning is an
  assertion with "synthesis of" provenance, its evidence wired by
  `supports`/`contradicts`, its certainty derived by named reasons;
  `scripts/learnings.py` computes the evidence table, storing nothing.
  Pilot: six papers to `read`, seven assertions, three learnings (QML on
  tabular data MODERATE; resampling for strong trees LOW; metric and power
  checks MODERATE). Existing primitives sufficed; three gaps proposed, not
  applied. Two defects found and fixed on the way: the query double-counted
  an assertion with two sources, and the promotion skipped `screened`'s
  applicability (caught by the aligned guard)
- **feat**: every paper the 18 QCi people co-authored, where a written rule
  can tell (Task F, F5 sub-part 2, Issue #49) -- `scripts/sprint5_qci_authors.py`:
  seed (another of the 18 co-authors) then a two-shared-co-author network,
  written before the search; strict name matching for common families
  (`tests/test_qci_author_matching.py`, proven by injection); 191
  acceptances, 121 new papers, 39 arXiv PDFs to `QCiAuthorsPapers/`. The
  rule leaves most of Miri's, Chancellor's and Sam Wu's earlier papers
  unresolved: reported per person, not downloaded, for a team-lead decision
- **fix**: four defects in the Task A durability code, found by the Phase 5
  fresh-eyes review -- `restore_store.py` could not restore a corrupt live
  store (it now moves the unverifiable file aside and restores into a fresh
  one) and could prune the very backup it was restoring (now protected);
  retention rule 3 kept any backup of an intermediate state forever (now
  also met when an export commit landed after the backup); `learnings.py`
  created an empty store when none existed. The write-script coverage guard
  now asks whether a script writes, not whether its text mentions --apply.
  Each fix has a test built on the failing case
- **feat**: the QCi authors' papers into the store (Task H part 2, F5,
  Issue #51) -- 121 accepted papers through the door under
  `INTAKE_WORKFLOW.md` section 12's category rule: 108 written, 13 skipped
  as other versions (preprint, journal, conference) of works written
  earlier in the same run, 0 refused; `--verify` 7/7 on samples. `[QC-8]`
  (Emami et al., Scientific Reports 2026), unobtainable from the
  bibliography alone, arrived through the author search. Store: 329 papers
- **fix**: Manual Validation feedback -- `learnings.py` quotes each sentence
  once and cuts only at a word; `view.py contexts` no longer lists a
  primary-context paper again "via applicability" (pre-existing since Sprint
  2); the six pilot papers' stale "not yet screened" removed, and
  `set_tier()` now removes it at every promotion (Q7); the Table 3 rows
  under `cvqboost-vs-xgboost-auc-under-balancing` added (Q6); F37 carded (Q4)
- **feat**: Q1 revised by the team lead -- the author-search hits the
  co-authorship rule left unresolved were screened on their abstracts for
  QML, ML or the Zeno effect (`scripts/sprint5_qci_topic_screen.py`, rule
  written first): 392 unresolved, 25 matched, 4 rejected on reading, 21
  entered at `seen` with "authorship not confirmed" in the disposition;
  15 PDFs downloaded. Store: 350 papers. Q8: the three weakest on
  authorship removed at the team lead's decision; 347 papers
- **process**: Sprint 5 retrospective improvements 1-8, all applied now
  (team lead: "do all now"), each extending an existing control --
  `set_tier()` refuses `screened`/`read` without applicability (1); the
  unraw-escape hook also blocks Python rewriting a `.py` file from a shell
  command (2); the guard-discipline test fails on `or True` / `assert True`
  (3); the door refuses a hand-origin record whose saved `.html` copy has
  fewer than 50 visible words (4); fresh-eyes review at the structural
  task's commit (5); computed numbers and reported caps (6); estimation
  calibration and the Sprint 5 model-assignment log rows (7); F36 gains the
  metadata provider as its tenth field (8). Every mechanical one proven by
  injection

### 2026-09-19 to 2026-09-23 (Sprint 4, PR #30, merged to develop and main 2026-09-23)

Sprint 4 fixed the path, fixed the records, and prepared the cost
measurement: Tasks A-K per `docs/sprints/SPRINT_4_PLAN.md`, run across a
local session (B, C, E, F, G, H) and a managed remote session (D, I, J, K)
on the same branch. Full detail in the PR #30 commit history and, once
written, `docs/sprints/SPRINT_4_SUMMARY.md`. This entry summarizes.

- **process**: the delivery cycle re-homed -- Backlog Refinement is Sprint N
  Phase 1 on the N branch, `sprint_status.json` advances at the carry-forward
  cut, the Stop hook and the plan-doc guard agree by construction (Task A,
  F27)
- **feat**: the ingestion door (Task B, F25 D2) -- `store/citations.py`
  derives citations and titles from arXiv, Crossref, DataCite and (Task G)
  GitHub; `validate_paper()` refuses hand-typed citations for resolvable
  ids, audit text in citations, tier words in dispositions, unanchored
  rationales; `paper_fields.citation` dropped and the read-tier CHECK added
  in one migration; `value` is the title
- **fix**: every F10 citation and access defect corrected by re-derivation,
  not retyping (Task C, F25 D3): 22 api-origin citations refreshed, 24
  hand-origin records given real paths and the visible marker, `rand-2023`
  renamed `rand-2022`, `udaru` to hand-origin (printed DOI unregistered),
  `rand` and `freericks` to api-origin (registered DOIs found); the seed
  generator retired; arXiv measured to refuse this client's `id_list`
  batches, so one id per request with DataCite as fallback
- **docs**: ADR-0005 A2 (`screened` as practiced, the citation rule
  enforced, three field changes, the rand rename), A3 (repository access
  kind, non-paper kinds by disposition prefix, derived ids, A2's pending
  items closed) and ADR-0004 A5 (the four context tests); every count a
  dated snapshot
- **feat**: `store/export.py` batches child queries, byte-identical export
  (Task D, F26; 275 statements to 22 at 54 records)
- **feat**: the F11 adjudication packet, generated from the store with each
  record's source link and F10 finding (Task E); the timing run is the team
  lead's; #35 stays open until the number is recorded
- **feat**: the intake workflow (Task G, F25 D5; F12 absorbed) --
  `docs/INTAKE_WORKFLOW.md` and `scripts/intake.py`, one door for papers,
  repositories, references and books, manifest mode for the bulk set that
  arrived during the sprint (1,618 files under `QMLPapers/`), `--verify` as
  the first-try check; all three F12 examples in the store (one thread:
  the LinkedIn post, the MerLin paper, the MerLin repository), 7/7 each
- **fix**: all 48 papers re-filed against pre-registered context tests
  (Task F, F25 D4): `method` 8 to 16 rows, `ml` 0 to 15, `world` moved off
  `arute` and `rand` onto `zajac` and `kerger`; every rationale anchored;
  nine dispositions rewritten; pinned tests moved with reasons
- **feat**: five papers to `read` after direct reads, five assertions with
  GRADE-style reasons, `fourier-wall` contradicts the two CVQBoost accuracy
  claims, `zajac` supports `fourier-wall`; Neven 2012 lineage confirmed
  (Task H, F25 D6)
- **process**: the hook family F15-F17 (Task I), `BACKLOG_REFINEMENT.md` as
  a skill (Task J, F20), `.claude/model_assignment_heuristics.json` with
  protocol as a first-class field (Task K, F18)
- **chore**: `pere-qml-github-repo-empty` removed at the team lead's
  direction (its 0-byte seed file is gone and the related papers sit under
  `QMLPapers/`); Manual Validation scope recorded in the workflow: only
  end-user functionality and team-lead decisions reach it, and an ADR
  amendment is reviewed as name, what changed and why, quoted language
- **test**: the CHANGELOG currency guard now reads the range-dated section
  headers this file uses; it had read 2026-09-14 as the newest entry for
  three sprints and passed on its own defect until the calendar moved
- **process**: F11 measured 2026-09-21 -- the team lead adjudicated the 18
  corrected records in 19.4 minutes, 1.08 per record, 18/18 accept. Recorded
  with its caveat: this is CONFIRM mode over model-corrected records with
  F10's findings in view, not the cold adjudication F10's 599 s compares
  against. F29 cards the cold measurement
- **fix**: PR #30 review round 1 (Copilot plus three Claude reviewers)
  found five defects, one merge-blocking and already shipped: an inverted
  ternary had destroyed `updated_reason` on 44 of 48 paper records, 43 of
  them losing the Sprint 1 seed-load note. Recovered from git by
  `scripts/recover_updated_reason_history.py`. Also: an api-origin record
  could carry any fabricated citation with no network call; an empty
  provider title was skipped while the run reported success; `apply()`
  wrote to `records` without passing the door; a DOI-shaped folder in a
  local path was read as a DOI; and Copilot alone caught GitHub-backed
  records being routed to `fetch_doi` and reported as broken DOIs
- **fix**: PR #30 review round 2, run against round 1's own fixes, found
  that three of those guards did not guard. The append-only test scanned
  SOURCE TEXT, so three rewrites destroyed history with the full suite
  green; the citation marker was a string a caller could type, refusing an
  omission but not a fabrication; and the new commit hook drifted its
  offsets, blocking at 19 preceding lines and ALLOWING at 20. Fixed
  structurally: one `append_updated_reason` implementation that all four
  sites call and the tests EXECUTE, a sentinel object compared by identity,
  and exact offsets. Copilot also found CI red on every fresh checkout (a
  test failed rather than skipped when the gitignored store was absent) and
  one hook registered without a timeout
- **chore**: F30 carded for Sprint 5 after the team lead asked about
  database backups -- the premise check found there were none, and the
  deeper gap is that no script rebuilds the store from the committed
  export, the recovery path ADR-0004's design implies

### 2026-09-18 to 2026-09-19 (Sprint 3, PR #20)

Sprint 3 corrected the foundations, then measured adjudication: Tasks A-H
per `docs/sprints/SPRINT_3_PLAN.md`. Full detail:
`docs/sprints/SPRINT_3_SUMMARY.md` (with the first recorded Actuals),
`docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`,
`docs/sprints/SPRINT_3_RETROSPECTIVE.md`, and the PR #20 commit history.
This entry summarizes rather than restates those numbers.

- **process**: spamfilter-multi surveyed read-only across ten named areas
  (Task A, F2 Phase 1); six genuinely new process assets carded as
  F15-F20; everything else was already here in adapted form
- **fix**: five PR #1 code-review findings closed (Task B, F6) --
  `validate_paper()`, `store.script_paths()`, `_copy_nonnull()`/
  `_child_list()`, citation read from provenance at export; Finding 4
  (N+1 queries) stays deferred as premature
- **test**: US English guard over living process docs (Task C, F13), with
  every ADR and everything under `docs/sprints/` excluded as frozen
  records after the fixer's first run rewrote them and was caught before
  commit; nineteen real corrections applied
- **fix**: `apply_paper_applicability.py` fails loudly on a typo'd paper
  id or a mismatched applicability set (Task D, F14)
- **process**: four INDEPENDENT model-tier adjudication reviews of the same
  18 screened papers, zero cross-visibility (Tasks E-H, F7-F10): Haiku and
  Sonnet 18/18 confirm; Opus 7 cross-record inconsistencies; Fable-tier
  Opus 4 source-verified citation defects plus an unearned `screened` tier
  and the value/provenance/citation triplication at the store-write layer.
  Findings consolidated with F12 into F25 at the team lead's direction
- **process**: Sprint 3 retrospective (team lead all "Very Good";
  Development Team five "Good", one theme: its own first attempts needed
  the guards). Four improvements applied: write-shaped scripts dry-run by
  default, `## Actuals` in every summary, delegated reports verified
  against repo state, review-protocol depth recorded on F11/F18
- **fix**: PR #20 review (Copilot 5, Claude code-reviewer 4, silent-
  failure-hunter 11) -- the Task B savepoint design had committed per
  entry under Python's legacy sqlite3 mode and the Task D script wrote
  before deciding; both now all-or-nothing ("decide, then write" added to
  QUALITY_STANDARDS.md); `set_tier()` closes the validator bypass; blank
  `checked_against_source` rejected; the US English test imports the
  script's own exclusion lists instead of restating them
- **chore**: end-of-turn status line and the memory rule that its time
  comes from a shell call, never an estimate (team lead, 2026-09-19)

### 2026-09-17 to 2026-09-18 (Sprint 2, PR #11)

Sprint 2 validated the store against both ground truths, guarded its
shared vocabulary, and made it viewable from the CLI: Tasks A-E, G per
`docs/sprints/SPRINT_2_PLAN.md` (Task F replaced mid-sprint, see below).
Full detail: `docs/sprints/SPRINT_2_SUMMARY.md`,
`docs/sprints/SPRINT_2_RETROSPECTIVE.md`, and the PR #11 commit history.
This entry summarizes rather than restates those numbers.

- **fix**: re-derived every seed-set paper's real applicability from its
  actual PDF content (Task A), correcting a Sprint 1 undercount where
  most papers carried only their single primary context despite
  ADR-0005 defining applicability as a separate plural field
- **feat**: extracted and validated the first real HSBC-submission
  assertions (Task B) -- the B1 variable-count case from the consumer
  repository's own preregistration amendments, with a `contradicts`
  relation between the corrected and the documented-wrong value
- **fix**: spot-checked store content against the 44 source PDFs
  directly (Task C); resolved seed-directory drift (a book relocated to
  the non-repo Books directory, the QBoost paper added, both confirmed
  intentional) and added the QBoost paper with a real citation
- **test**: guard for ADR-0004/ADR-0005 vocabulary agreement (Task D,
  F76), verified by injection
- **docs**: both ADRs' 20-paper checkpoints walked against the real
  store and recorded as dated amendments (Task E, F75; ADR-0004
  Amendment A4, ADR-0005 Amendment A1), later corrected for two
  internally-inconsistent counts found by code review and given
  explicit point-in-time qualifiers so a snapshot count is not read as
  a durable fact in a document that does not permit edits in place
- **feat**: `scripts/view.py` (Task G, F3) -- contexts / paper /
  assertion modes, plain text or `--json`, no server. Found and fixed a
  Windows console encoding defect (cp1252 crash on non-ASCII `--json`
  output) during build, verified by injection
- **process**: Task F (team-lead adjudication timing) REPLACED by F7-F11
  (Class 3 scope change) -- four model-tier adversarial review cards
  (Haiku, Sonnet, Opus, Fable) plus F11, the original measurement,
  sequenced to run after F7-F10 against the same record set
- **chore**: hook enforcing the AskUserQuestion ban
  (`.claude/hooks/block_ask_user_question.py`), added after the rule
  was violated twice in one session despite being fully documented
  beforehand; a mechanical `gh issue list` check added to Phase 5
  after two issues stayed open despite `Closes #N` commit messages on
  a feature branch; a data-precondition check added to
  `SPRINT_PLANNING.md`'s estimation guidance
- **process**: Sprint 2 retrospective run (16 categories x 4 roles, all
  "Very Good"); F7-F14 added to the backlog for future sprint selection

### 2026-09-15 to 2026-09-17 (Sprint 1, PR #1)

Sprint 1 built the store end to end: Tasks A-H per
`docs/sprints/SPRINT_1_PLAN.md`, plus the sibling-repo write guard and F2-F6
backlog items surfaced at Manual Validation and PR review. Full detail:
`docs/sprints/SPRINT_1_SUMMARY.md` (created during Sprint 2 planning, per
the three-doc rule), `docs/sprints/SPRINT_1_RETROSPECTIVE.md`, and the PR
#1 commit history. This entry summarizes rather than restates those
numbers, per this project's own "a number must be traceable to a committed
generator" standard -- run the suite, don't copy a count.

- **chore**: the five inherited PowerShell hooks converted to Python
  (Task A pre-kickoff), removing the doubled-backslash JSON-escape hazard
  by construction rather than by continued vigilance
- **feat**: SQLite schema for the four record classes (Task B), a
  deterministic JSON export as the committed artifact (Task C), and
  domain-scale contexts seeded per ADR-0004 section 3b (Task D)
- **feat**: one paper (Lenat/Marcus) ingested end to end (Task E); the
  44-paper seed set loaded at `seen`, 17 promoted to `screened` for variety
  (Task F); a determinate-fact resolver for the consumer repository's
  amendment count, computed live rather than stored (Task G)
- **docs**: removed hsbc-quantum-fraud-2026 process content (Dirac-3
  hardware rules, `experiments/src`, `results.json`, a submission calendar)
  presented as this repository's own live rules across 11 files (Task H,
  F1), with a regression test verified by injection
- **chore**: added a hook blocking writes into `spamfilter-multi` or
  `hsbc-quantum-fraud-2026` from this repository's sessions (read access
  stays unrestricted)
- **fix**: PR #1 review (Copilot + Claude) found `assertion_documents` FK
  coupling that blocked citing a document on an assertion with no
  units/rounding, a silently-dropped `citation_context` field, and a
  `--promote` ordering bug that no-opped promotion on an already-seeded
  store. All three fixed with regression tests before merge
- **process**: Sprint 1 retrospective run (16 categories x 4 roles, all
  "Very Good"); F2 (spamfilter-multi deep-dive), F3 (CLI DB viewer), F4
  (accuracy validation against the HSBC submission and the source papers),
  F5 (QCi author/documentation deep-dive), and F6 (remaining PR review
  findings) added to the backlog for Sprint 2 selection

### 2026-09-14

- **chore**: Repository seeded from `hsbc-quantum-fraud-2026`. Carried: the
  sprint methodology (execution workflow, process, planning, checklist,
  retrospective, stopping criteria, backlog refinement), quality and testing
  standards, five hooks, three practice ADRs renumbered 0001-0003, and five
  process guards. NOT carried: anything about the fraud submission, the ML/QML
  runs, or Dirac-3 hardware
- **docs**: ADR-0014 and ADR-0015 MOVED here as 0004 and 0005. They are this
  repository's design rather than the consumer's; the originals remain there as
  the record of when the decisions were made
- **chore**: Three hooks deliberately NOT carried --
  `block-unapproved-submission-edit`, `block-reactive-amendment` and
  `block-frozen-history-rewrite`. Each guards a frozen artifact of the fraud
  submission that does not exist here, and a hook guarding a missing file is a
  hook that cannot fire
- **test**: `.claude/settings.json` written STRUCTURALLY via json.dump rather
  than by hand, and every registered path verified to resolve at write time. Two
  hooks in the consumer repository were dead for their entire life because a
  single backslash before `block-` is a JSON escape
- **chore**: corrected a seeding mistake -- the first attempt put the git
  repository inside `D:\Data\Harold\EvidenceBasedDB\` (the non-repo staging
  directory), conflating the two. Reseeded to the correct
  `D:\Data\Harold\github\EvidenceBasedDB\` and removed the misplaced copy,
  verified to hold no uncommitted changes or unpushed commits first.
  `README.md` and `CLAUDE.md` now record the two-directory layout as a table
