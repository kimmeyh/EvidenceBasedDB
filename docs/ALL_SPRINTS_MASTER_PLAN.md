# All Sprints Master Plan

Created 2026-09-15, structure adapted from hsbc-quantum-fraud-2026's
ALL_SPRINTS_MASTER_PLAN.md (itself adapted from spamfilter-multi). This
document is IN THE REPOSITORY and persists across conversations. Read it
before every sprint (Phase 1/2), update it after every sprint (Phase 7.7/8.2).

**Nothing below is carried from either source repository's history.** This
repository's own sprint count starts at 1. F77 is the one item that crosses
the boundary: it is the consumer repository's own backlog number for "build
the Evidence Based DB," recorded there and tracked here as the reason this
repository exists. No other F# from either source repository applies here.

## Maintenance Guide

- **At each sprint's Phase 7.7, then in Sprint N+1's Phase 1.2 sweep**
  (re-homed 2026-09-19 from "Phase 8.2"): update "Last Completed Sprint";
  add the sprint's row to "Past Sprint Summary" once its SUMMARY doc
  exists; prune shipped items from "Next Sprint Candidates"; add retro
  Category-14 items with new F#s.
- **`docs/sprints/SPRINT_N_SUMMARY.md`** is created at Sprint N's Phase 7 or
  at the latest in Sprint N+1's Phase 1.2, and linked here.
- **IDs**: F# for all features/process/tech-debt items native to this
  repository, starting at F1; next available number; never reuse. A number
  quoted from the consumer repository (F77 and any future cross-reference)
  keeps that repository's number and is never renumbered into this
  repository's sequence.
- **Estimates**: minutes/hours from recorded actuals; `[no-history]` where
  uncalibrated. This repository has no recorded actuals yet; every Sprint 1
  estimate is `[no-history]` by construction.
- `CHECKLIST-Phase2-pre.md` is the LIVE deliverable ledger; this document is
  the sprint-scoping view over it. Keep them consistent; the checklist wins on
  deliverable truth, this file wins on sprint sequencing.

## Past Sprint Summary

| Sprint | Summary doc | Status | Duration |
|---|---|---|---|
| 1 | docs/sprints/SPRINT_1_SUMMARY.md | [OK] Complete | 2026-09-15 to 2026-09-17 |
| 2 | docs/sprints/SPRINT_2_SUMMARY.md | [OK] Complete | 2026-09-17 to 2026-09-18 |
| 3 | docs/sprints/SPRINT_3_SUMMARY.md | [OK] Complete | 2026-09-18 to 2026-09-19 |
| 4 | docs/sprints/SPRINT_4_SUMMARY.md | [OK] Complete | 2026-09-19 to 2026-09-23 |

## Last Completed Sprint

Sprint 4 is below; Sprint 3 follows it for continuity.

### Sprint 4: Fix the Path, Fix the Records, Measure the Cost (2026-09-19 to 2026-09-23, PR #30, merged to main via PR #42)

Eleven tasks, eleven issues, all closed, run across a local session and a
managed remote session on one branch. **The path**: an ingestion door
(`store/citations.py`, `validate_paper`'s rules) that derives citations from
arXiv, Crossref, DataCite and GitHub and refuses a hand-typed one for a
resolvable id; one intake for papers, repositories, references and books
(`docs/INTAKE_WORKFLOW.md`, `scripts/intake.py`) with `--verify` as a
mechanized F10 protocol; `paper_fields.citation` dropped and a read-tier
CHECK added in one migration. **The records**: every F10 citation and access
defect corrected by re-derivation rather than retyping, 48 papers re-filed
against context tests written down FIRST, five papers promoted to `read`
with GRADE-style assertions and the store's first `contradicts` relation.
**The cost**: F11 measured at last -- 1.08 team-lead minutes per corrected
record, 18/18 accept, recorded with the caveat that it measures confirm-mode
review, not the cold adjudication F10's 599 s compares against (F29 cards
that).

Two ADR amendments (ADR-0005 A2 and A3) plus ADR-0004 A5, all dated, none an
edit in place. Eight retrospective improvements applied the day they were
approved.

**What the reviews found, which is the honest part.** Round 1 (Copilot plus
three Claude reviewers) found five defects including one merge-blocking and
already shipped: an inverted ternary had destroyed `updated_reason` on 44 of
48 paper records, 43 losing the Sprint 1 seed-load note, while the script's
own dry-run gate reported zero refusals. Round 2, run against round 1's own
fixes, found that three of those fixes' guards did not guard -- the
append-only test scanned source text rather than executing the code, so
three rewrites destroyed history with the full suite green; the new citation
marker was a string a caller could type; and the new commit hook drifted its
offsets, blocking at 19 preceding lines and allowing at 20. All fixed
structurally. Copilot separately caught GitHub records routed to `fetch_doi`,
CI red on every fresh checkout, and a hook registered without a timeout.

Suite 255 -> 458 tests. Full detail: `docs/sprints/SPRINT_4_SUMMARY.md`;
retrospective: `docs/sprints/SPRINT_4_RETROSPECTIVE.md` (16 categories x 4
roles; team lead all "Very Good", Development Team nine "Very Good" and four
"Good", each tied to a named lapse). Zero metered spend.

**The lesson worth carrying**: a guard that pins a PHRASING pins nothing.
Two vacuous guards were found in the CHANGELOG checks, and a third was
written during the sprint's own review round. The standard that holds is the
one this repository already had: a test must EXECUTE the thing it guards.

### Sprint 3: Correct the Foundations, Then Measure Adjudication** (PR #20
merged to develop, then develop merged to main via PR #29, both
2026-09-19). Delivered Tasks A-H per
`docs/sprints/SPRINT_3_PLAN.md`: the spamfilter-multi survey with six new
process cards F15-F20 (Task A, F2 Phase 1); five PR #1 code-review
findings fixed at the store/export layer with `validate_paper()`,
per-entry savepoints and shared helpers (Task B, F6); the US English
guard over living process docs, with frozen ADRs and sprint docs excluded
(Task C, F13); `apply_paper_applicability.py` hardened against silent
partial failure (Task D, F14); and four INDEPENDENT model-tier
adjudication reviews of the same 18 screened papers with zero
cross-visibility (Tasks E-H, F7-F10), whose findings -- 4 real citation
defects, 7 cross-record inconsistencies, an unearned `screened` tier and
the value/provenance/citation triplication at the store-write layer --
were consolidated with F12 into F25 at the team lead's direction during
Manual Validation. Four retrospective improvements applied as commits:
dry-run-by-default for write-shaped scripts, an `## Actuals` section in
every sprint summary, delegated-report verification against repo state,
and review-protocol depth recorded as a first-class input to F11/F18. PR
#20 review (Copilot 5, Claude code-reviewer 4, silent-failure-hunter 11)
found two real bugs in the sprint's own work -- the Task B savepoints
committed per entry under Python's legacy sqlite3 mode, and the Task D
script wrote before deciding -- both fixed as all-or-nothing, with
"decide, then write" added to QUALITY_STANDARDS.md, `set_tier()` closing
the validator bypass, and the US English test importing the script's own
exclusion lists. Full detail: `docs/sprints/SPRINT_3_SUMMARY.md`; results:
`docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`; retrospective:
`docs/sprints/SPRINT_3_RETROSPECTIVE.md` (16 categories x 4 roles; team
lead all "Very Good", Development Team five "Good"). Zero metered spend.

**The measurement Sprint 3 did NOT produce**: team-lead adjudication
minutes per record (F11), by design -- this sprint produced the four
independent reviews F11 compares against. F11 is now sequenced after
F25 D1-D3 so it measures adjudication of corrected records.

## Current sprint

**Sprint 5** (branch `feature/20260923_Sprint_5`, cut 2026-09-23 at the
Sprint 4 carry-forward). Phase 1 Backlog Refinement complete; scope not yet
selected. The slate is below.

## Next Sprint Candidates

Refined 2026-09-23 after Sprint 4 (Sprint 5 Phase 1.2). Shipped and
pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint 2); F2
Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25, F26,
F27 (Sprint 4). The superseded stubs F12 and F21-F24 are removed now
that F25 has shipped -- their history lives in the Sprint 3 and 4 docs
and in git. Remaining items below, newly added ones marked.

**F5. Deep-dive QCi: identify authors, find their other papers, scrape QCi's own documentation (~large, no-history) Priority 10**
- Phase: Sourcing / research. Tentatively assigned Sprint 2 (team lead, 2026-09-16)
- Platform: N/A for this repository's own tracked content -- output lands
  entirely under `D:\Data\Harold\EvidenceBasedDB\` (NOT this git repository;
  ADR-0005 section 3 is explicit that raw material stays outside version
  control, the `access` field points at it)
- **Three sub-parts, team lead 2026-09-16**:
  1. **Identify every QCi-affiliated person who authored or co-authored a
     paper already in this repository's store or seed set.** Search the DB
     export and the 44 seed-set papers' own citation/affiliation lines
     (already extracted once during Task F -- re-derive from the actual
     PDF content, not from memory of that extraction). Get FULL names, not
     initials, verified against the paper itself. `emami-2025-financial-
     fraud-entropy-computing-qci` already names six QCi-affiliated authors
     on its own arXiv title page (Emami, Dyk, Haycraft, Spear, Nguyen,
     Chancellor) as a confirmed starting point; the SMU/Loke CVQBoosting
     paper's "et al." need expanding from the actual PDF before assuming
     who among its author list, if anyone, is QCi-affiliated rather than
     SMU-affiliated.
  2. **For each identified person, determine a reliable way to search for
     papers they co-authored on ANY topic** (not just QCi/Dirac-3 work),
     and download all of them. **Search priority, team lead 2026-09-16:
     arXiv first, then DOI resolution (Crossref/publisher), then Google
     Scholar.** A name alone is not a unique search key (common-name
     collisions are a real risk); the card's own acceptance criteria should
     require disambiguating each hit against the person's known
     affiliation/co-author network before downloading, not accepting every
     name match.
  3. **Separately, scrape `quantumcomputinginc.com` itself** for: key docs
     on Dirac-3 and `eqc_models`; training/onboarding documentation; and
     anything covering QML methods the company publishes on (QBoost,
     CVQBoost, QSVM, and related). This is independent of sub-part 2 --
     official vendor documentation, not third-party authored papers.
  4. **Also pull the `eqc_models` package itself from PyPI** (team lead,
     2026-09-16) -- the released distribution, not only web documentation
     about it. Source and any bundled docs/examples both count as reference
     material under this card's scope.
- **Storage, team lead 2026-09-16 (clarified)**: everything lands in
  `D:\Data\Harold\EvidenceBasedDB\References\`, which the team lead
  confirmed is meant to hold exactly this kind of material -- non-technical
  articles, QCi's own training/website documentation, and downloaded
  packages like `eqc_models` from PyPI -- alongside the technical papers
  `Papers` already holds. Proposed sub-structure for review at carding:
  `References/QCi-authors/<person>/` for sub-part 2's per-author downloads,
  `References/QCi-site/` for sub-part 3's scrape, and
  `References/eqc_models/` for sub-part 4's PyPI pull -- team lead's call
  on exact naming at carding, this is a proposal.
- **Standing constraint, same as every paper record in this store**: the
  PDFs/scraped pages themselves are never committed into this git
  repository (ADR-0005 section 3, `.gitignore` already blocks `*.pdf`). If
  any of this material becomes a real DB record (not just staged material),
  it follows the same `seen`-tier paper-record path Task F already built,
  with its own `access` field pointing at the local path.
- **Not yet scoped, flag at carding**: whether a scraped/downloaded item
  becomes a full paper record immediately, or stays purely staged material
  ("might be used later," per the team lead's own framing) until a future
  sprint decides to ingest it. Recommend the latter, since ingesting
  unreviewed scraped content at `seen` tier without adjudication is exactly
  the "volume without judgment" risk ADR-0005 section 2c warns is MORE
  dangerous than fewer, reviewed records.
- Depends on: nothing technical. Read-only web access and the existing
  seed-set metadata are both already available.

**F28. Learn from the papers: what QML and ML each teach about improving predictions (~large, no-history) Priority 44**
- Phase: Knowledge synthesis. Added 2026-09-19 (team lead, at Sprint 4
  scoping, for the sprint AFTER Sprint 4): "Start to devise a way to
  learn from the papers -- key learnings about QML, how QML might be able
  to improve predictions (tools, techniques, algorithms...), key learnings
  about ML, how we might be able to improve ML predictions (tools,
  techniques, algorithms...)."
- Platform: the store (assertion class, contexts `qml`/`ml`/`method`,
  `assertion_relations`), `scripts/`, a new synthesis output whose form
  this card must decide
- **This is design first** (same shape as F2 and the old F12): the store
  already has the primitives -- assertions with provenance and GRADE-style
  certainty, `supports`/`contradicts` relations, contexts as partitions.
  What does not exist is (a) extraction at scale (F25 B5 extracts from
  five papers by hand; ~1,300 papers need a repeatable, guarded path
  through F25's door), and (b) a synthesis layer that turns many
  assertions into "what we now believe about X, at what certainty, and
  why" without restating any of them (CLAUDE.md: determinate facts are
  computed, never stored -- a synthesis is a QUERY over assertions, not
  a second copy)
- **Open questions this card exists to answer, not to pre-decide**: what a
  "key learning" is as a record (an assertion at context `qml`/`ml` with
  a `method`-context relation? a new class? ADR-0004 section 3 names the
  add-a-class trigger); how a learning about "how to improve predictions"
  carries its evidence (the `emami`/`loke`/`qci` vs `mancilla`/`zajac`
  `contradicts` pair F25 B5 wires is the first worked example); whether
  synthesis is `view.py`-style (computed on demand from the store) or a
  regenerated export per context; which model tier extracts and which
  adjudicates, given Sprint 3's finding that protocol depth, not tier,
  produced the findings (F18); and how the 1,200 incoming papers are
  triaged for extraction (all at `seen`, promote by relevance -- ADR-0005
  tiers as adjudication depth)
- **Not this card's job**: ingesting the 1,200 papers (that is F25's door
  plus F5's discovery), or extracting from all of them (tiering decides
  which reach `read`)
- Depends on: F25 (the door and the corrected records), F11 (the
  adjudication cost per record, which bounds how many papers can reach
  `read` at all). Sequenced for Sprint 5.

**F29. Cold-mode adjudication timing: the number F11 did not measure (~small, no-history) Priority 22**
- Phase: Measurement. Added 2026-09-22 (Sprint 4 retrospective improvement
  6), from the F11 run's own result.
- **What F11 measured, and what it did not.** On 2026-09-21 the team lead
  adjudicated the 18 F10-reviewed records in 19.4 minutes, 1.08 per record,
  accepting all 18 (log: `docs/sprints/SPRINT_4_F11_TIMING_LOG.json`). That
  is CONFIRM MODE: the records had already been corrected by Tasks C, F and
  H, and each was shown with F10's own finding printed beneath it. It is a
  real and useful number -- it is the cost of a human pass over
  model-corrected records -- but it is not the number F10's 599 seconds
  compares against, and this repository's own escalation trigger says a
  review that confirms everything with zero rejections is evidence about
  the protocol as much as about the records.
- **What this card measures**: the same protocol COLD. The source is opened
  before the corrected record is shown; F10's findings are not displayed;
  the record is adjudicated field by field against the source. Run on a
  sample (5 to 8 records is enough to bound it), not all 18, because the
  point is the ratio to confirm mode, not a second full pass.
- Platform: `scripts/adjudication_timing.py --mode cold` (built in Sprint 4
  improvement 6; it already records the mode in its log), a packet variant
  that omits the findings block, `.claude/model_assignment_heuristics.json`
  `learning_log`.
- **Why it matters for scale**: ADR-0004 says adjudication cost is the
  constraint on the whole design. With about 1,300 papers arriving, the
  planning question is how many can ever reach `read`. Confirm mode says
  about a minute each given a correct pipeline; cold mode says what it
  costs when the pipeline is not trusted, and the gap between them is the
  value of the pipeline, stated in minutes.
- Depends on: nothing technical. The tool and the packet generator both
  exist. Do NOT re-run on the same 18 records in confirm mode: that
  measurement is done.

**F30. Store durability: systematic backups, a real restore, and the missing rebuild-from-export (~medium, no-history) Priority 12**
- Phase: Operational safety. Added 2026-09-23 (team lead, at Sprint 4
  close-out): "There is a database backup and the database is not kept in
  the repository, right? Backups need to be done systematically and only
  preserved for a max of N days (propose 32) and min of M sprints
  (propose 5)."
- **The premise check, done 2026-09-23, because half of it was wrong.**
  The database is correctly NOT in the repository: no `.db` file is
  tracked, `.gitignore` excludes the store with a stated reason, and
  `store/evidence.db` (252 KB on that date) exists only on the team
  lead's machine. But **there was no backup.** No `.bak`, no dated copy,
  nothing anywhere in the tree. The only thing between the store and
  total loss was the committed `export/*.json`.
- **The real gap is the restore, not the backup.** ADR-0004 section 2
  calls the store a build output and the committed export the artifact,
  so the DATA is recoverable in principle -- the Sprint 4 remote session
  rebuilt the store from `export/` byte-identically. But it did so BY
  HAND, in a session that no longer exists, and `scripts/` has
  `regenerate_export.py` (store -> export) with nothing going the other
  way. A recovery path that exists in principle and has no script is the
  same defect class as a guard that has never been run.
- **SQLite gives us the mechanism; use it, not a file copy** (team lead,
  2026-09-23: "if it is [sqlite], then backups and restores are part of
  the sqlite package" -- correct, and it overturned this card's first
  draft). Measured on the live store that day: `sqlite3.Connection.backup()`
  (Python stdlib, present on 3.12.10 / SQLite 3.49.1) took **15 ms**,
  produced `PRAGMA integrity_check = ok` with all 48 papers, and is safe
  against a concurrent writer. A `shutil.copy2` of a live database takes
  0 ms and can capture a torn write that looks fine until it does not.
  Note the backup is **not byte-identical** to the source -- the API
  writes a freshly-packed database -- so a restore is verified by content
  (integrity check plus a regenerated export matching the committed one),
  never by comparing file bytes.
- Platform: `store/` (a shared backup helper), `scripts/` (a restore
  script and a `rebuild_store_from_export.py`), `.gitignore`,
  `docs/QUALITY_STANDARDS.md`, `tests/`.
- **Three pieces, in dependency order:**
  1. **`scripts/rebuild_store_from_export.py`** -- the missing recovery
     path. Reads the committed `export/*.json` into a fresh store through
     the real ingestion path, then regenerates and asserts the export is
     byte-identical to what it read. This is the piece that makes every
     other durability question secondary, and it is first for that reason.
  2. **Backup on write, not on a clock.** At 15 ms the backup is not a
     scheduled chore; it belongs inside `--apply`, before the
     transaction, in the helper every write-shaped script already shares.
     No cron, no drift, and each backup is aligned with a real change.
     **Every backup is verified at creation** (open it, `integrity_check`,
     count the records) and the run FAILS if it does not check out -- an
     unverified backup is the guard-never-run class again.
  3. **`scripts/restore_store.py`** -- restore is a script with a test,
     not a documented gesture. The test restores into a temp store and
     proves the regenerated export matches.
- **Retention (team lead's decision 2026-09-23, option 2a), three
  independent rules, ALL of which must allow a deletion:**
  - keep every backup for **32 days** (the team lead's number; at 252 KB
    a year of them is under 100 MB, so space is not the constraint --
    avoiding a stale second source of truth is);
  - never delete the **newest backup of each of the last 5 sprints**,
    regardless of age (the team lead's "min 5 sprints", expressed as what
    it protects: the state at each recent sprint boundary). Note sprints
    here run 1 to 3 days, so 5 sprints is about a week and sits INSIDE
    the 32 days rather than under it -- the two bounds are independent,
    not a range;
  - never delete a backup whose contents are **not yet in a committed
    `export/`**. This is the clause that actually matters: until the
    export is committed, the backup is the only copy.
- `backups/` is gitignored, for the same reason the store is.
- **Not this card's job**: off-machine or cloud backup (the store is
  rebuildable from a git-committed export, so the repository IS the
  off-machine copy); backing up `D:\Data\Harold\EvidenceBasedDB\`
  (Papers, Books, QMLPapers -- that is a separate question about material
  this repository deliberately does not own).
- Depends on: nothing technical. Sequenced for Sprint 5; the trigger is
  the 1,618-file bulk load, after which a lost store costs an hour of
  arXiv-paced re-fetching rather than a rebuild.

**F19. Build a SPRINT_RESUME_GUIDE.md and a startup-check skill (~medium, no-history) Priority 25**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `docs/SPRINT_RESUME_GUIDE.md` (163 lines) and its `startup-check`
  skill (read-only source, 2026-09-18 survey)
- Platform: a new `docs/SPRINT_RESUME_GUIDE.md`, a new
  `.claude/skills/startup-check/SKILL.md`
- **The gap this closes**: this repository has no single durable,
  low-token reference doc for "what phase are we in, what does that
  mean, what happens next" -- that content is currently scattered
  across `SPRINT_EXECUTION_WORKFLOW.md`, `SPRINT_STOPPING_CRITERIA.md`,
  and memory files, each read in full rather than referenced. The
  source's `startup-check` skill reads `sprint_status.json`, cross-
  checks it against actual git/branch state via four explicit staleness
  checks (does the branch match? does the sprint number match? did
  commits land after the file's last-updated timestamp? does CHANGELOG
  already show this sprint as complete?), and refuses to present stale
  `next_actions` as current -- directly the same discipline this
  repository's own CLAUDE.md already states as a standing rule ("don't
  act on a recalled memory without checking it against current repo
  state first") but currently unenforced by any single mechanized step
- **Adaptation needed**: the source's own resume-string generator
  (`memory-save` skill) assumes a `/compact`-style slash command this
  repository may not use the same way; port the STAGE-detection logic
  (BETWEEN-SPRINTS / REFINEMENT / PLANNING / EXECUTION / RETRO) and the
  staleness-check discipline, not the compaction-specific output format
- Depends on: nothing technical. Independent of every other F# card.

## Design documents governing this repository

- `docs/adr/0004-evidence-based-db.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- `docs/adr/0005-reference-library.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- `docs/INTAKE_WORKFLOW.md` -- how a source enters the store (Sprint 4 Task
  G, F25 C4/C5): one door for papers, repositories, references and books,
  `scripts/intake.py`, the bulk-manifest path, and the first-try check.
  Amended by dated section, never silently, once a choice has shipped records
- Both carry a six-question review due after roughly 20 papers are loaded.
  Revisions land as dated amendments at the bottom of each ADR, never as
  silent edits. **The checkpoint is DONE**: walked against the real store
  at 46 papers (Sprint 2 Task E, F75, shipped) -- ADR-0004 Amendment A4,
  ADR-0005 Amendment A1. Both amendments carry an explicit point-in-time
  qualifier (2026-09-18) since their counts are a snapshot, not a durable
  fact, in a document that does not permit edits in place.
