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
| 5 | docs/sprints/SPRINT_5_SUMMARY.md | [OK] Complete | 2026-09-23 to 2026-09-25 |
| 6 | docs/sprints/SPRINT_6_SUMMARY.md | [OK] Complete | 2026-09-27 to 2026-10-05 |
| 7 | docs/sprints/SPRINT_7_SUMMARY.md | [OK] Complete | 2026-10-06 to 2026-10-10 |
| 8 | docs/sprints/SPRINT_8_SUMMARY.md | [OK] Complete | 2026-10-10 to 2026-10-14 |
| 9 | docs/sprints/SPRINT_9_SUMMARY.md | [OK] Complete | 2026-10-14 to 2026-10-18 |
| 10 | docs/sprints/SPRINT_10_SUMMARY.md | [OK] Complete | 2026-10-18 to 2026-10-21 |
| 11 | docs/sprints/SPRINT_11_SUMMARY.md | [OK] Complete | 2026-10-21 to 2026-10-23 |
| 12 | docs/sprints/SPRINT_12_SUMMARY.md | [OK] Complete | 2026-10-23 to 2026-10-24 |
| 13 | docs/sprints/SPRINT_13_SUMMARY.md | [OK] Complete | 2026-10-24 to 2026-10-28 |

## Last Completed Sprint

Sprint 13 is below; Sprint 12 follows it for continuity.

### Sprint 13: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records (2026-10-24 to 2026-10-28, PR #131)

Seven tasks, seven issues (#132-#138). **Corrections**: the ".;" joins and
the LOW theoretical results' reasons (F107); Phase 2's F162 and three
F102 values (F108). **Process**: the F39 release (F111); every LOW names
its reason; the write-path rule reads parsed code; no reading budget.
**Papers**: Papers and Roadmap checked (F109, F110); all 806 readable
`qml` records, 795 read (F112); the full re-read (F113), 210 records
applied, 302 cloud results waiting for F117. Store 2,334 -> 2,335 papers
(869 -> 1,653 `read`), 2,970 -> 10,735 assertions; suite 1,253 -> 1,424.
Retrospective: team lead all "Very Good"; I1, I2 and I4 applied (a
read-row rewrite stops the apply; read-row updates name their detail;
every commit has its CHANGELOG entry), I3 skipped. Full detail:
`docs/sprints/SPRINT_13_SUMMARY.md`.

### Sprint 12: Fix the Entities, Speed the Suite, Then Read 400 Records (2026-10-23 to 2026-10-24, PR #122, merged to develop and to main via PR #130 on 2026-10-24; tagged sprint-12)

Seven tasks, seven issues (#123-#129). **Corrections**: every stored
"&amp;" and the Cyc quote (F101). **Process**: the full suite in 199 s warm
from 781 s, and the targeted runner mode (F100); ADR-0005 A11, a source
link resting on a recorded team-lead decision (F106). **Inbound**: Phase
2's Sprint 28 results at 10086da (F102). **Papers**: the Classiq challenge
pages and the named repository (F103); Roadmap-to-QML's first release, 21
entered and 20 read (F104); the F57 release of 400 records by up to 5
readers, HIGH only with a named basis (F105). Store 2,302 -> 2,334 papers
(455 -> 869 `read`), 1,595 -> 2,970 assertions; suite 1,175 -> 1,256.
Retrospective: team lead all "Very Good"; I1 (the runner sees store
writes) and I3 (no id starting with "-") applied, I2 carded on F57. Full
detail: `docs/sprints/SPRINT_12_SUMMARY.md`.

### Sprint 11: Enter QCi's Answers, Then Read 200 Records and Every New Paper (2026-10-21 to 2026-10-23, PR #113, merged to develop and to main via PR #121 on 2026-10-23; tagged sprint-11)

Seven tasks, seven issues (#114-#120). **Inbound**: QCi's three emails
(F92, 18 assertions) and Phase 2's F108 ceiling result (F93). **Papers**:
magic state cultivation (F91); 38 new files and the team lead's list
entered and read (F97); the 200-record F57 release read by up to 5 agents
from one ledger (F96, 649 assertions). **Process**: backlog cards adopt
spamfilter-multi's practices (F94); the F39 release (F99). Manual
Validation: a decision-backed `code-of` link, and a computed hand-download
list with a skill. Store 2,284 -> 2,302 papers (224 -> 455 `read`), 793 ->
1,595 assertions; suite 1,084 -> 1,175. Retrospective: team lead all "Very
Good"; I1a, I1b, I2 and I4 applied (quote-mark and figure checks in the
write path; the backup gate; the verdict runner; the Edit tool for every
in-place edit), I3 carded on F57, I5 skipped. Full detail:
`docs/sprints/SPRINT_11_SUMMARY.md`.

### Sprint 10: Fix the Hooks and the Dirac Records, Then Read the Next 74 (2026-10-18 to 2026-10-21, PR #101, merged to develop and to main via PR #112 on 2026-10-21; tagged sprint-10)

Ten tasks, ten issues (#102-#111), all closed. **Hooks**: the code-edit hook stops
blocking read-only commands (F81); the never-write hook covers abbreviated
and program-running git options (F82). **Dirac records**:
`platform:dirac-1` (F84, ADR-0004 A10, approved); Phase 2's Dirac-3S
verification entered (F85). **Sources**: per-instance optimization bounds
(F83); Cyc's stored counts (F50); the DOI probe asks DataCite (F86).
**Reading**: the 74-record F57 release, 64 read with 216 assertions (F89);
the 8 papers with no free copy carded as F90. **Discovery**: off-topic
kinds dropped before ranking (F87); a live re-run entered 91 candidates at
`seen`. Store 2,190 -> 2,284 papers, 557 -> 793 assertions; suite 950 ->
1,084. Retrospective: team lead all "Very Good"; I1 and I2 applied (the
quote check in the write path; the coordinator's edits name their
passages), I3 skipped. Full detail: `docs/sprints/SPRINT_10_SUMMARY.md`.

### Sprint 9: Read the Ceiling Papers, Then Open the Phase 2 Exchange (2026-10-14 to 2026-10-18, PR #88, merged to develop and to main via PR #100 on 2026-10-18; tagged sprint-9)

Eleven tasks, eleven issues (#89-#99), all closed. **Ceilings**: the
ceiling-estimation group read and entered with an answer document (F78);
the 20 remaining handoff facts dispositioned (F46). **The Phase 2
exchange**: free reads both ways, no writes, hook-enforced, with the first
inbound record (F79). **Reading at scale**: the first 76-record F57 slice,
65 read (F80); discovery ranked and triaged, 87 candidates at `seen`
(F62). **Store**: `cites` links (F55, ADR-0005 A10), a computed
corroborated flag (F56, ADR-0004 A9), primary-source re-checks (F74,
ADR-0005 A9), local-file hashes (F48), two identifier forms at the door
(F68, F69). F51 stays HOLD. Store 2,093 -> 2,190 papers, 105 -> 557
assertions; suite 759 -> 950. CI was red unnoticed from 2026-10-15 to
2026-10-18 (three tests lacked `live_store`); fixed, and retrospective I7
now prevents it. Retrospective: team lead all "Very Good"; I1, I3 to I5
and I7 applied, I2 and I6 skipped. Full detail:
`docs/sprints/SPRINT_9_SUMMARY.md`.

### Sprint 8: Read QCi's Newest Guide, Then Build the Yearly Re-check (2026-10-10 to 2026-10-14, PR #77 and PR #84, merged to develop and to main via PR #86 and PR #87 on 2026-10-14; tagged sprint-8)

Seven tasks, seven issues (#78-#83, #85; Task G added at Phase 7). **QCi's
newest material**: the Dirac-3S guide under its own context (ADR-0004 A8,
F65 with F63), and F65's recovered item list as F71: the release, QCi's
benchmarking review (its all-optimal headline contradicted by its own
Table 6) and the site diff since 2026-09-24. **The yearly re-check**: 24
computed sections, `--due` (ADR-0005 A7, A8). Also: develop as the default
branch with `sprint-N` release tags (F66, ADR-0001 A2), Haiku 5.5 (F67),
the QMLPapers manifest check (F60) and the Massoli list (F61). Store 1,947
-> 2,093 papers, 76 -> 105 assertions; suite 617 -> 745. Retrospective:
team lead all "Very Good"; six improvements applied. Full detail:
`docs/sprints/SPRINT_8_SUMMARY.md`.

### Sprint 7: Move the Data Out, Then Measure arXiv Safely (2026-10-06 to 2026-10-10, PR #68, merged to develop and to main via PR #76 on 2026-10-10)

Seven tasks, seven issues (#69-#75), all closed. **Data out**: the store
and backups moved to `D:\Data\Harold\EvidenceBasedDB\store`, the committed
export retired (ADR-0004 A7, ADR-0003 A2, ADR-0005 A5). **arXiv measured
safely**: 18 s spacing, a 240-request session cap, the abstract page as
fallback; 1,524 records probed in 36 hours with 0 errors (ADR-0005 A6). At
Manual Validation the per-cycle refresh became a staggered 12-month
re-check (F64). Content: eight Cycorp papers (F44) and the Dirac-3 reading
pass (F45, 14 assertions). Store 1,875 -> 1,947 papers, 60 -> 76
assertions; suite 572 -> 610. Retrospective: team lead all "Very Good";
seven improvements approved. Full detail: `docs/sprints/SPRINT_7_SUMMARY.md`.


### Sprint 6: Decide the Fields Once, Then Load at Scale (2026-09-27 to 2026-10-05, PR #54, merged to develop and to main via PR #67 on 2026-10-06)

Twelve tasks, twelve issues (#55-#66), all closed. **Fields decided once**:
ADR-0004 A6 (`derivation`, `claim_type`, two computed certainty caps) and
ADR-0005 A4 (publication status, ten reference fields under the probe rule,
the `read` gate, the admission-against-interest rule), both accepted at
Manual Validation, then migrated with a byte-identical round trip.
**Loaded at scale**: 1,402 QMLPapers papers (F32), the Cyc package without
the CVQBoost findings (F41; F51 holds the rest), six withdrawn and one
retracted source (F33), 105 repository links (F35). Store 361 -> 1,875
papers, 23 -> 60 assertions; suite 506 -> 572. Found mid-sprint: intake had
never paced arXiv between entries (since Sprint 4); fixed, then prevented at
the source. Retrospective: team lead all "Very Good"; six improvements
applied now. Full detail: `docs/sprints/SPRINT_6_SUMMARY.md`.

### Sprint 5: Make the Store Durable, Then Fill It (2026-09-23 to 2026-09-25, PR #43, merged to develop and to main via PR #53 on 2026-09-27)

Nine tasks, nine issues (#44-#52), all closed. **Durable first** (F30): the
store rebuilds byte-identically from the committed export, takes a verified
SQLite-API backup before every write, and restores by script. **Then
filled**: the HSBC Phase 2 bibliography (F31, 121 records, 0 refused, F36
carded), QCi's authors, site and package (F5: 108 co-authorship papers, 52
site references, 18 topic-screened papers), and the first computed
synthesis (F28: three learnings over existing primitives, F37 carded). Store
48 -> 347 papers; suite 458 -> 505; zero metered spend. F19 and F29 closed
without implementation. Retrospective: team lead all "Very Good"; eight
improvements applied now, each extending an existing control. Full detail:
`docs/sprints/SPRINT_5_SUMMARY.md`, `docs/sprints/SPRINT_5_RETROSPECTIVE.md`.

**The lesson worth carrying**: the author's own injection-proven tests did
not find the four defects a fresh-eyes reviewer found in the same code; a
review launched at the task's commit is now the rule.

**Sprint 5 scope and decisions, kept here from its "Current sprint" section
(moved 2026-09-27 at Sprint 6 Phase 1.2):**

- **Scope selected 2026-09-23 (team lead, DEFINED)**: F31 (new: download
  and process the HSBC Phase 2 bibliography, then propose the fields it
  shows the store is missing), F30 (store durability), F28 (learn from the
  papers), F5 (QCi deep-dive, with every find added to the store through
  the existing intake path).
- **Closed 2026-09-23 without implementation (team lead):** F19
  (SPRINT_RESUME_GUIDE.md and a startup-check skill): "This is not
  necessary if the sprint execution docs are kept up-to-date. In other
  repositories using the same Sprint framework Coding Agents pick up where
  everything is left off very quickly by looking at github and reading a
  couple of documents. This can be closed." F29 (cold-mode adjudication
  timing): "This is not needed and can be closed." F11's confirm-mode
  number (1.08 team-lead minutes per record) stands as the store's only
  adjudication measurement; the cold-mode number stays unmeasured by
  decision, not by omission.
- **Manual Validation decisions, 2026-09-25** (team lead: "1. 2 2.1 3 1 4. 1
  5. 2 6. add the row it rests on 7 2"): Q1 = 2, then REVISED the same
  morning ("can you pull any of the papers from the authors IF they are
  related to QML, ML or the Zeno effect (can you screen the abstracts to
  determine)"): 21 of 392 unresolved hits entered, marked "authorship not
  confirmed"; Q8 = 2 then removed the three weakest, 18 remain. Q2 = 1:
  retention rule 3's "superseded" clause accepted. Q3 = 1: the six pilot
  `read` promotions accepted; the three learnings stay "awaiting team-lead
  adjudication". Q4 = 1: F37 carded. Q5 = 2: the papers `[IN-2]` and
  `[CL-21]` meant are not added. Q6: the Table 3 rows added under
  `cvqboost-vs-xgboost-auc-under-balancing`, the vendor sentence kept.
  Q7 = 2: `set_tier()` removes "; not yet screened" at every promotion.
  Q9 = 1: Manual Validation complete.


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

**Sprint 13** (branch `feature/20261024_Sprint_13`, cut 2026-10-24 at the
Sprint 12 carry-forward, after PR #122 merged to develop and PR #130 merged
develop to main).

- **Scope** (DEFINED, team lead 2026-10-25): F107, F98, F95, F108, F39
  and F57 at 800 records. The permanent items are released as copies:
  F109 (F95), F110 (F98), F111 (F39) and F112 (F57, 800 records). F90
  put on HOLD ("Can put this one on HOLD for now"). F51 stays HOLD.
- **Plan**: `docs/sprints/SPRINT_13_PLAN.md` (approved 2026-10-25 as
  amended: Q1 = 1, F112 reads all 806 readable `qml` records).

## Next Sprint Candidates

Refined 2026-10-25 after Sprint 12 (Sprint 13 Phase 1.2); Sprint 12's shipped
cards (F100, F101, F102, F106 and the released copies F103, F104 and F105)
pruned BY HAND (Edit tool, card by card) the same day. F107 carded from
Sprint 12's retrospective Category 13; F108 from Phase 2's Sprint 28 work
after 10086da.
Shipped and pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint
2); F2 Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25,
F26, F27 (Sprint 4); F5, F28, F30, F31 (Sprint 5); F32-F38, F40-F43, F47
(Sprint 6; F35's 30 unlinked notes continued as F54, F41's CVQBoost part as
F51); F44, F45, F52, F53, F54, F58, F59 (Sprint 7; F53's per-cycle refresh
replaced by F64's 12-month re-check; F54's 10 "unsure" and 140 third-party
repository candidates stay held back in `sprint7_f35_screen.json` and
`QMLPapers\Repos\REVIEW.md`); F60, F61, F63, F64, F65, F66, F67, F71
(Sprint 8); F46, F48, F55, F56, F62, F68, F69, F74, F78, F79, F80
(Sprint 9; F62's open precision note carried as F87); F50, F81-F87 and
the released copies F88 and F89 (Sprint 10; F89's 8 papers with no free
copy carried as F90); F91-F94 and the released copies F96, F97 and F99
(Sprint 11); F100, F101, F102, F106 and the released copies F103, F104
and F105 (Sprint 12). F39, F57, F95 and F98 are
permanent and stay. Closed without
implementation: F19, F29 (Sprint 5 scope selection, reasons under Sprint 5
in "Last Completed Sprint"); F49 (Sprint 8 scope selection, Q3 = 1: moot
under ADR-0004 A7, since no committed export exists to drop a context, and
`test_the_live_store_round_trips_through_a_dump` already proves the
on-demand dump's round trip byte for byte). Priorities renumbered at Sprint
8 scope selection (Q2 = 1) in steps of 10, with steps of 2 for items that
sprint together. The superseded stubs F12 and F21-F24 were
removed after F25 shipped; their history lives in the Sprint 3 and 4 docs
and in git. Remaining items below.

### Permanent items

**F39. Evaluate the available models and update the model-assignment heuristics -- PERMANENT (~30m per release) Priority 50** (NEW 2026-09-29; effort re-derived from Sprint 10's release at Sprint 11 Task B, F94)
- Phase: Process (recurring)
- Value: this prevents agent work being assigned to a retired model or a
  tier whose measured outcomes no longer support it.
- Platform: `.claude/model_assignment_heuristics.json`,
  `docs/SPRINT_PLANNING.md` (team roles table),
  `tests/test_model_assignment_heuristics.py`; Anthropic's model
  documentation as the primary source
- Team lead, 2026-09-29: "add to backlog as permenant item and release a
  copy for this sprint: evaluate the models available and update the
  hueristics for how models are assigned to agents."
- **How a permanent item works (first of its kind here)**: F39 is never
  pruned. A sprint that selects it gets a released COPY with the next free
  F# ("F39 release for Sprint N"); the copy ships and is pruned like any
  card, and F39 stays.
- **Each release**: (1) list the models available to this environment
  with id, version and release date, verified against Anthropic's current
  documentation that day, never from memory; (2) record what changed since
  the last release (new models, retirements, price or context changes);
  (3) re-read the heuristics' `learning_log` outcomes since the last
  release; (4) update tiers, task patterns and escalation triggers, and
  the SPRINT_PLANNING.md role table, with each change naming its evidence;
  (5) a failing test guards whatever the release adds.
- Acceptance per release: every tier's facts verified on Anthropic's
  pages that day; the outcomes since the last release logged; each rule
  change names its evidence; its test proven to fail by injection.
- Depends on: nothing

**F95. Ingest and read the new papers in the Papers folder -- PERMANENT (~90m per release) Priority 20** (NEW 2026-10-21, team lead at Sprint 11 Phase 1.4)
- Phase: Sourcing / intake, then reading (permanent item, like F39)
- Value: this enables every paper the team lead saves to reach the store
  and be read within a sprint ("in general new papers are valuable").
- Platform: `D:\Data\Harold\EvidenceBasedDB\Papers\` (the team lead's
  folder: its files are never renamed or moved); `scripts/intake.py`; the
  verified write path (intake sections 26 and 31)
- Team lead, 2026-10-21: "Add a backlog item and assign to this sprint and
  all future sprints - paper folders for new items that have not been
  ingested or read - ingest them and then read them - in general new
  papers are valuable."
- **Released every sprint** as a copy with the next free F#, the same way
  as F39. Copied from the backlog into each sprint once: a sprint that
  skips it gets no second copy later, and the next sprint's copy simply
  covers whatever is new by then.
- Each release: (1) list every PDF in `Papers\` (and its subfolders) that
  no record's `access` names; (2) match each to a record by DOI or arXiv
  id first, so a paper already in the store is linked, not entered twice;
  (3) enter the rest through the intake door; (4) read each one not yet
  at `read` and enter its claims, every quote checked before the write;
  (5) a paper that cannot be entered or read keeps the reason.
- **Snapshot as of 2026-10-21**: 134 PDFs in `Papers\`; 37 are named by
  no record's `access` (some may already be in the store under their
  arXiv id). Read at a release, these count toward F57's total as well;
  they are not read twice.
- **Snapshot as of 2026-10-23** (Sprint 12 Phase 1.2): 151 PDFs in
  `Papers\`; 0 named by no record's `access` (file-name match). The next
  release holds the named repository below and any file saved after this
  date. The hand-download list holds 38 records.
- **Snapshot as of 2026-10-25** (Sprint 13 Phase 1.2): 180 PDFs in
  `Papers\` and its subfolders; 0 named by no record's `access`
  (file-name match). The hand-download list holds 43 records. The
  repository and the Classiq pages named for Sprint 12's release shipped
  as F103; nothing is named for the next release.
- **The hand-download list** (team lead, 2026-10-22, Sprint 11 Manual
  Validation Q2: "Keep an on going list of these in relative priority
  order and will likely download in the future"): computed by
  `python scripts/hand_download_list.py` (intake sections 39 and 40),
  never kept by hand, shown on request by the `hand-download-list` skill,
  each entry with its target file name and why it matters. A listed paper the team lead has saved into `Papers\` is
  caught by step (1) and leaves the list once linked.
- Acceptance per release: every unnamed PDF linked, entered or given a
  reason; every entered paper at `read` with its assertions, or at `seen`
  with its reason; the counts before and after recorded.
- Depends on: none

### HOLD Items (waiting on an external event)

**F51. The CVQBoost findings record and its six assertions (~45m) Priority HOLD** (NEW 2026-10-03)
- Phase: Sourcing / intake
- Value: this enables the store to cite the CVQBoost findings by record
  once the re-run settles them, instead of by a document that may change.
- Acceptance: the re-run's findings document read at its new hash; the
  record and its six assertions entered with the re-run's provenance.
- Platform: the Cyc and CVQBoost handoff
  (`D:\Data\Harold\EvidenceBasedDB\Handoff-2026-10\ebdb-handoff\`): the
  manifest entry `kimmey-2026-maximizing-predictions-cvqboost-cumulative-findings`,
  the six CVQBoost assertions in the sprint script, and decision 4.1's
  `method` applicability row on that record.
- Carded at Sprint 6 plan approval (Q10 = 1) so the remainder is not lost
  when F41 ships without it. Team lead, Q4: "it will be updated after the
  next hsbc repo sprint (the experiement will be re-run) and then it can be
  referenced".
- The record's authorship (decision 1 in the handoff) is settled by the
  re-run's own provenance, not by attribution.
- Hold checked 2026-10-15 (Sprint 9 Task K): all three copies
  (`References\2026-08_Kimmey_CVQBoost-Findings.md`, FourierWall2's
  `docs\CVQBoost_Findings.md`, the consumer repository's
  `fourierwall2\CVQBoost_Findings.md`) hash to SHA-256 `425358a7b4cec71f...`
  and say "Last updated 2026-08-04". Phase 2 has newer Dirac runs (B4 and
  B5 on 2026-10-06; F142 on Dirac-3S on 2026-10-15), read only, but none
  rewrites the findings document. Stays HOLD.
- Hold checked 2026-10-23 (Sprint 12 planning): two copies unchanged at
  `425358a7b4cec71f...`; the consumer repository's copy is no longer at
  its path. Selected for Sprint 12, then kept HOLD at plan Q2 = 2 (team
  lead: "I thought it had been run, so wait").
- Hold checked 2026-10-25 (Sprint 13 Phase 1.2): the `References\` and
  FourierWall2 copies still hash to `425358a7b4cec71f...`. Phase 2's F162
  (2026-10-23, at 9993ab6, read only) re-tested FourierWall2's single-run
  in-pocket wins over ten seeds: none repeats reliably. That is a Phase 2
  result (F108), not the findings document's re-run. Stays HOLD.
- Depends on: the hsbc repository's re-run of the experiment.

### Carded at Sprint 6 Manual Validation, 2026-10-05

**F57. Read for claims: the records still at `seen` and `screened`, each read in full (no estimate: as long as the reads take; permanent, no reading budget since 2026-10-25) Priority 70** (NEW 2026-10-05, team lead at Sprint 6 MV)
- Phase: Sourcing / extraction (permanent item, like F39)
- Platform: the store; first-pass readers under the parallel-reading
  pattern (`.claude/model_assignment_heuristics.json`), every quote checked
  in the write path
- Value: this enables the store's claims to cover the papers it already
  holds, not only the 224 read by 2026-10-21.
- Team lead, 2026-10-05: "what else has not been read for claims - if not
  in backlog, add backlog item to do any missing 'read for claims' entries".
- **No reading budget, and every read is full (team lead, 2026-10-25, at
  Sprint 13 Manual Validation).** "fully read all the papers that are not
  marked 'read' and update all conclusions ... remove the budget ... It is
  far more important to read them all, get all the conclusions, profs,
  assertions... than some budget ... ensure that all future paper reads
  have no budget."
  - Until then the reader prompt said "read at least the abstract,
    introduction, results and conclusion" and "2 to 4 assertions per
    paper", and releases were planned at a per-record rate (Sprint 13's
    F112: 1,310 minutes for 806 records, about 1.6 minutes each). Of
    Sprint 13's 795 reads, 551 said "in part" and 109 more listed only
    some sections (snapshot as of 2026-10-25).
  - From now on a reader reads every section, appendix and proof of the
    paper; `read_extent` is `full` only then, and anything not read is
    named with why (a page the text layer lost, not a choice of time).
    There is no cap on assertions: every result, theorem with its
    statement and conditions, definition, setup, stated limit and
    conclusion is entered.
  - An estimate in a plan is a forecast for the team lead, never a limit
    on a read. A release is no longer a slice sized to a budget: the
    remaining records are read in full (Sprint 13 Task G, F113), and a
    usage-limit pause is waited out, not cut around.
  - `tests/test_reader_prompts.py` fails on a reader prompt from Sprint 13
    Task G onward that names a part-read or an assertion cap.
- **Snapshot as of 2026-10-05**: 1,875 papers; 24 at `read`, all with
  yielded assertions; 14 `screened`; 1,837 `seen`. F45 and F46 cover only
  the handoff's pending facts, not these.
- Too large for one sprint. Each release: (1) screen a slice (applicability
  from the source, the Sprint 4 Task F tests); (2) rank by relevance to the
  consumer's open questions (`hsbc-2026`, `platform:dirac-3`, then `qml`);
  (3) read the top of the ranking directly and extract, under ADR-0005 A4's
  read gate. Records that do not bear on any context stay `seen` with the
  reason.
- Acceptance per release: the slice screened, the ranking recorded, every
  promoted record read and yielding, every refused one with its reason.
- **Release size: 74 records per sprint, every sprint, until no record is
  left at `seen` or `screened`** (team lead, 2026-10-15, Sprint 9 approval
  Q7: "we need to read all that have not been read, so backlog a repeated
  item to read in chunck of 74 until they have all been read"). Sprint 9's
  release (F80) is 76 records, as approved at Q7 = 2; from Sprint 10 each
  release is 74. Snapshot as of 2026-10-14: 2,055 records at `seen` or
  `screened`, so about 27 more releases at 74 each. The item closes when
  the count is 0, not before. Refresh the count at each release, because
  intake adds records.
- **Snapshot as of 2026-10-21** (Sprint 11 Phase 1.2): 2,284 papers; 224
  at `read`; 2,060 at `seen` or `screened`, of which 2,057 have no read row
  (3 are read and refused). Sprint 10's discovery re-run added 91 at
  `seen`. About 28 more releases at 74 each.
- **Release size raised to 200** (team lead, 2026-10-21, Sprint 11 Phase
  1.4): "Re-add the F57 that reads an additional 75 records each sprint
  ... should be copied from the backlog to each sprint (don't duplicate if
  skipped in one sprint) and increase the number to 200 each sprint.
  Continue until all records that are marked as 'seen' and 'screened' are
  marked 'read'."
  - Each sprint gets ONE released copy with the next free F# (Sprint 10's
    was F89; Sprint 11's is F96). A skipped sprint does not leave a second
    copy waiting.
  - **Order stays the relevance ranking in step (2).** The same message
    asked for newest paper first; the team lead withdrew that the same
    day: "sorry for F57 switch back to the relavance ranking".
  - **Up to 5 reading agents in parallel** (team lead, 2026-10-21: "these
    can run by up to 5 agents as everything else will likely not touch in
    a way that would negatively affect this item"). The sprint's other
    reading items (F95's release, a single-paper read card) run under the
    same release, from one ledger that gives each record to exactly one
    agent: "no 2 'read's should impact the same record." A test fails if
    any record appears in two groups.
  - At 200 per sprint: about 11 releases from the 2026-10-21 count of
    2,060.
  - **Snapshot as of 2026-10-23** (Sprint 12 Phase 1.2): 2,302 papers;
    455 at `read`; 1,847 at `seen` or `screened` (1,845 and 2). About 10
    more releases at 200.
  - **Snapshot as of 2026-10-25** (Sprint 13 Phase 1.2): 2,334 papers;
    869 at `read`; 1,465 at `seen` or `screened` (1,463 and 2), of which
    1,449 have no read row. About 8 more releases at 200, or 4 at
    Sprint 12's 400. Sprint 12's release of 400 ran inside a sprint
    that took about 24 percent of its estimate.
  - **Snapshot as of 2026-10-25, after Sprint 13's release (F112)**:
    2,335 papers; 1,653 at `read`; 682 at `seen` or `screened` (681 and
    1), of which 654 have no read row. F112 read 795 records (12 refused
    with no assertions, each with its reason) and listed 11 with no copy.
    About 4 more releases at 200.
  - Known limit (Sprint 10 finding): a record with no free copy, or one
    refused at reading, cannot reach `read`. Each release reports those
    separately, so the count that closes the item is visible.
  - **Not in any slice so far (the fresh-eyes review of e621771; snapshot
    as of 2026-10-25)**: every release's candidates came from
    `sprint9_f80_slice.qml_candidates`, which keeps only records whose
    access names an arXiv id or a DOI. Of 1,007 `qml` records at `seen`
    or `screened` with no read row, Sprint 13's 806 are those; 24 are
    earlier no-copy records; 166 are GitHub repositories; 11 name only a
    local file that exists (among them neven-2012's QBoost paper,
    aaronson's "read the fine print", four kawchak-2023 records). A later
    release reads the 11 (they need no fetch) and decides how a GitHub
    repository is read for claims, or that it is refused with a reason.
- **From Sprint 12's release: HIGH needs a named basis (Sprint 11
  retrospective I3; team lead, 2026-10-23: "i3 as recommended"; ~30m in
  the release).** In Sprint 11 each reading script kept its own
  `HIGH_REVIEWED` set with no reason per id, and the fresh-eyes review moved
  5 measured results from HIGH to LOW after the first apply. A shared helper
  in `store/` grades HIGH only with a basis named per id: setup, scope,
  definition, proved result, or stated limit. `store/write_path.py`'s rule
  requires every new reading script to use it. Acceptance: the release's
  HIGH grades each carry their basis; the rule proven by injection.
- **From Sprint 13's release: LOW names its reason too (Sprint 12
  retrospective I2; team lead, 2026-10-24: "q2 1"; ~30m in the release).**
  In Sprint 12 a LOW took its stored reason from a default branch, so 3
  proved results stored "an empirical result". `store/grading.py` takes a
  named reason for every LOW as well: measured result, statement about the
  field, or proved result not checked by the reader. Acceptance: no LOW in
  the release stores the default reason; the rule proven by injection.
- **Earlier sprints' theoretical results kept LOW as "an empirical result"
  (carded 2026-10-25, Sprint 13 Task F; INTAKE_WORKFLOW.md section 49).**
  Sprint 13's I2 corrected Sprint 12's 29. A classifier over the 499 such
  LOW assertions from Sprints 9 to 11 proposed 13 theoretical and 14 mixed
  (snapshot 2026-10-25); none is checked by the coordinator, and their
  reading scripts are legacy. Acceptance: each candidate's quotes read by
  the coordinator; each confirmed one stores a theoretical result's reason
  with its cause, through a correction that keeps the earlier live tests
  holding. ~60m.
- Depends on: none

### Carded at Sprint 10 Manual Validation (2026-10-19)

**F90. Read the eight F89 papers with no free copy, once the team lead has downloaded them (~30m) Priority HOLD** (NEW 2026-10-19, Sprint 10 Manual Validation step 5; HOLD from 2026-10-25)
- Phase: Reading
- **On HOLD** (team lead, 2026-10-25, Sprint 13 scope selection: "Can
  put this one on HOLD for now"). Was Priority 60. All 8 still at `seen`
  with no copy on that date.
- Value: this enables the eight most-cited unread papers (F89's top of
  the ranking) to be read once a copy exists.
- Platform: `D:\Data\Harold\EvidenceBasedDB\Papers\`, a Sprint 11 reading script
- Team lead, 2026-10-19: "can you push the download list of #5 to the
  next sprint." Sprint 10 Task I (F89) selected 74 records; 9 had no free
  copy. Valdez 2023 is retracted and stays out. The other 8 stay `seen`
  with that reason (snapshot as of 2026-10-19):
  - Schuld 2018, Supervised Learning with Quantum Computers.
    https://doi.org/10.1007/978-3-319-96424-9
  - Li 2020, A quantum deep convolutional neural network for image
    recognition. https://doi.org/10.1088/2058-9565/ab9f93
  - Narayanan 2000, Quantum artificial neural network architectures and
    components. https://doi.org/10.1016/s0020-0255(00)00055-4
  - Aimeur 2006, Machine Learning in a Quantum World.
    https://doi.org/10.1007/11766247_37
  - Ruan 2017, Quantum Algorithm for K-Nearest Neighbors Classification
    Based on the Metric of Hamming Distance.
    https://doi.org/10.1007/s10773-017-3514-4
  - Aimeur 2007, Quantum clustering algorithms (ICML). ICML lists it as
    free, but its archived link no longer resolves; Sprint 10 read the
    2013 journal version. https://doi.org/10.1145/1273496.1273497
  - Duan 2020, A survey on HHL algorithm.
    https://doi.org/10.1016/j.physleta.2020.126595
  - Panella 2011, Neural networks with quantum architecture and quantum
    learning. https://doi.org/10.1002/cta.619
- Acceptance: the team lead's step first (the eight PDFs in `Papers\`,
  any file name; the team lead's files are never renamed). Then each
  paper's access points at its file; each is read and entered under F89's
  rules (quotes checked before any write, intake section 26); a paper
  still missing stays `seen` with that reason. These count toward F57.
- Depends on: the team lead's downloads

### Carded at Sprint 11 Phase 1.4 (2026-10-21)

**F98. Review Christophe Pere's QML paper repository for new papers, then ingest and read them -- PERMANENT (~60m per release) Priority 22** (NEW 2026-10-21, team lead at Sprint 11 Phase 1.4, for Sprint 12 onward)
- Phase: Sourcing / intake, then reading (permanent item, like F39)
- Value: this enables the store to keep pace with a curated QML paper
  list maintained by an author whose papers it already holds.
- Acceptance per release: the list's commit recorded; every paper new
  since the last release matched, entered or given a reason; each read
  under F57's rules or kept at `seen` with its reason.
- Platform: https://github.com/Christophe-pere/Roadmap-to-QML ("This
  repository will contain the major papers, books and blog posts on QML";
  last push 2026-10-20 at carding), GitHub REST, read only; the intake
  door; the verified write path
- Team lead, 2026-10-21: "add to backlog for next sprint: every sprint
  review the Christophe Pere paper repository for new papers, ingest them and
  read them". Read as Roadmap-to-QML, his paper list; the seed set once
  held an empty "Christophere Pere QML Github Repo.txt" for it (removed in
  Sprint 4). Correct the repository here if another was meant.
- Released every sprint as one copy, like F95. Each release: (1) read the
  list at its current commit, recording the commit; (2) diff it against
  the commit the last release recorded (the first release takes the
  whole list); (3) match each paper to the store by DOI or arXiv id;
  (4) enter the new ones and read them under F57's rules and ledger.
- The first release may be large; it is sized from the list's count at
  that sprint's planning, and its overflow carries to the next release.
- **Sized at Sprint 12 Phase 1.2 (snapshot as of 2026-10-23, read only,
  commit a239747648)**: the list is year files (`2007-2017/` to `2026/`)
  plus `Workforce.md`, with 1,402 distinct arXiv ids. 1,381 are already in
  the store (1,142 at `seen`, 239 at `read`; matched by id in `access` or
  provenance), so the first release enters about 21. The 1,142 at `seen`
  are read under F57's releases, not twice.
- **Snapshot as of 2026-10-25** (Sprint 13 Phase 1.2): the first release
  (F104) recorded a239747648; the list has no commit since (GitHub REST,
  read only). A release now confirms the commit and enters nothing unless
  the list changes first.
- Depends on: none

### Carded at Sprint 13 Phase 1.2 (2026-10-25)

**F107. Correct two stored defects found in Sprint 12: the ".;" joins and the LOW proved results' reason (~35m) Priority 10** (NEW 2026-10-25, Sprint 12 retrospective Category 13, targeted for the Sprint 13 plan)
- Phase: Data correction
- Value: this prevents stored text from carrying a join error, and a LOW
  grade from naming a reason that is not its own.
- Platform: the store; the verified write path; `store/grading.py`
- Two findings, one card, each named in the retrospective (Category 13,
  Claude Code Development Team):
  - The ".;" joins (est 20m): where a hash note was appended to text that
    already ended in a full stop. Snapshot as of 2026-10-25: 16 paper
    records' `evidence`, 1 `paper_reads` detail and 1 `paper_probes`
    value hold ".;". Each is read first: a join is corrected, punctuation
    only; a ".;" the source itself prints stays.
  - The LOW proved results (est 15m): 3 assertions from Sprint 12's reads
    are proved results kept LOW because their quoted text was cut short,
    yet store "an empirical result" as the reason (INTAKE_WORKFLOW.md
    section 47; `larson-convergence-proved` is one). Each gets its own
    reason; the grade stays LOW.
- Acceptance: 0 ".;" joins left (any source-printed one named); the 3
  reasons corrected through the verified write path; a guard proven to
  fail by injection; a second apply writes nothing.
- Depends on: none (F57's I2 builds the general rule from Sprint 13's
  release; this card corrects the 3 already stored)

**F108. Enter Phase 2's later Sprint 28 work: F162 in the SPECTRA pocket, and the corrections to four results already entered (~60m) Priority 30** (NEW 2026-10-25, read from Phase 2 at Sprint 13 Phase 1.2)
- Phase: Inbound evidence (F79)
- Value: this prevents the store from holding values Phase 2 has since
  corrected, and enables the in-pocket result to sit beside the pocket
  claims it bears on.
- Platform: the store; `hsbc-qfraud-phase2` read only, branch
  `feature/20261019_Sprint_28` at 9993ab6 (2026-10-24): `docs/phase2/`
- Changed since F102 read 10086da (snapshot as of 2026-10-25, read only).
  The F numbers in this list are Phase 2's own backlog numbers, not this
  repository's (this repository's F110 and F111 are Sprint 13 releases):
  - F162 (new, `SIM`): inside the SPECTRA pocket, over ten seeds, the
    CVQBoost proxy is not reliably above HGB or XGBoost on any of three
    cells; XGBoost is reliably above it on two. FourierWall2's single-run
    in-pocket wins do not repeat. Phase 2: "nothing here justifies" a
    device run.
  - F111: the run time restated as 82.5 minutes of recorded lane time
    (about 95 wall clock, not recorded in the file); the "not dominated
    by an exact match" reason marked unverified.
  - F114: calibration moves some estimates on two of the three arms;
    every estimate above the Bayes error (calibrated 3 to 13 percent,
    uncalibrated 4 to 14).
  - F151, F153, F154, F110: smaller wording changes; each compared with
    the stored value.
- Acceptance: each document read at the commit current when the work
  starts (named in provenance); F162 entered under `ml` through the
  verified write path, with its limits, and related by ADR-0004 A8 (b)
  to the stored SPECTRA pocket claims (the three B4 assertions such as
  `dirac3-matches-classical-proxy-in-pocket-spectra-b4`, and
  `fourier-wall-incomplete-bar-manufactures-advantage`); each stored F102
  value whose source changed corrected or confirmed by name; a second
  apply writes nothing.
- Depends on: none (reads at a named commit)

### Released for Sprint 13 (2026-10-25)

**F109. F95 release for Sprint 13: new papers in `Papers\` (~15m) Priority 20** (NEW 2026-10-25, released copy of F95)
- Phase: Sourcing / intake, then reading
- Value: F95's, for the files in hand when the task starts.
- Platform: `D:\Data\Harold\EvidenceBasedDB\Papers\`; `scripts/intake.py`
- F95's steps (1) to (5). 0 unlinked PDFs on 2026-10-25; any file saved
  before the task starts is included.
- Acceptance: F95's per release.
- Depends on: none

**F110. F98 release for Sprint 13: Roadmap-to-QML since a239747648 (~10m) Priority 22** (NEW 2026-10-25, released copy of F98)
- Phase: Sourcing / intake, then reading
- Value: F98's, for the list at its commit on the task's day.
- Platform: github.com/Christophe-pere/Roadmap-to-QML, read only; the intake door
- The diff from a239747648 (no commit since, on 2026-10-25).
- Acceptance: F98's per release.
- Depends on: none

**F111. F39 release for Sprint 13: the models and the heuristics (~30m) Priority 50** (NEW 2026-10-25, released copy of F39)
- Phase: Process (recurring)
- Value: F39's, with Sprint 12's reading and review outcomes logged.
- Platform: `.claude/model_assignment_heuristics.json`; `docs/SPRINT_PLANNING.md`
- F39's steps (1) to (5); the last release was Sprint 11's (learning log
  last dated 2026-10-21).
- Acceptance: F39's per release.
- Depends on: none

**F112. F57 release for Sprint 13: read all 806 readable `qml` records, up to 5 agents, with the LOW-reason rule first (~1340m) Priority 70** (NEW 2026-10-25, released copy of F57)
- Phase: Sourcing / extraction
- Value: F57's, for this sprint's release (team lead, 2026-10-25: "800
  records"; plan Q1 = 1 widened it to all 806 readable `qml` records).
- Platform: the store; up to 5 Sonnet 5.5 first-pass readers, every quote
  checked in the write path
- F57's I2 first (a named reason for every LOW, 30m), then every
  readable `qml` record at `seen` or `screened` with no read row.
- Acceptance: each of the 806 at `read` with its assertions, or kept at
  `seen` with its reason; HIGH and LOW grades carry their basis; the count
  before and after recorded.
- Depends on: none

**F113. Read every unfinished paper in full, with no reading budget, and update every conclusion (no estimate: as long as the reads take) Priority 70** (NEW 2026-10-25, team lead at Sprint 13 Manual Validation; Sprint 13 Task G)
- Phase: Sourcing / extraction
- Value: the store's claims rest on whole papers, not on an abstract and
  a conclusion. Team lead, 2026-10-25: "fully read all the papers that
  are not marked 'read' and update all conclusions. That includes this
  sprints 551 adn 109 and any from prior runs ... It is far more
  important to read them all, get all the conclusions, profs,
  assertions... than some budget"; "it is OK to re-read all the
  partially read papers"; "need these resolved before Manual Validation
  is complete".
- Platform: the store; up to 5 first-pass readers at the tier Sprint 13
  Task B confirmed (Sonnet 5.5), the coordinator at the top tier; every
  quote checked in the write path; arXiv serial at 18 s inside F52's cap
- **Snapshot as of 2026-10-25** (2,335 papers; a read counts as full only
  when a reader or the coordinator recorded the whole paper and named no
  part left out; `manifests/sprint13_g_slice.json`): 1,997 not read in
  full.
  - 1,317 at `read`: 1,315 with a local copy, 1 with only a DOI
    (`emami-2026`), 1 GitHub repository.
  - 680 at `seen` or `screened`: 325 with a local copy (Task G's
    download run saved 165), 182 with only an arXiv id or a DOI, 173
    GitHub repositories. These 182 and `emami-2026` are the 183 with no
    local copy: 45 failed downloads and 138 with no free copy, listed in
    `manifests/sprint13_g_no_copy.json` for the hand-download list.
  - Updated 2026-10-25 after the download run finished: the line above
    first gave 226 with a local copy and 281 still to fetch or list.
  - Corrected 2026-10-25 (the fresh-eyes review of a3b8074): this card
    first gave 1,141 and 682 from an earlier count that did not treat a
    reader's "full" with listed parts as partial; the slice's own count
    was then 1,991, and is 1,997 since a note with an exception ("Whole
    paper read except ...") no longer counts as whole.
- What a full read is: every section, appendix and proof. Each theorem is
  entered with its statement and conditions quoted, so a theoretical
  result kept LOW for want of them (288 in Sprint 13's script) can be
  graded on the statement. No cap on assertions. Each record's stored
  assertions are given to its reader: each is confirmed, corrected,
  widened or narrowed from the whole paper, and new ones are added.
- Acceptance: every record with a copy read in full, its `paper_reads`
  row `full`, its assertions updated or added under the grading rules;
  every record without a copy listed with its reason and on the
  hand-download list; the counts before and after; a second apply writes
  nothing.
- Depends on: Manual Validation Q2 (the write-path bypasses closed before
  any more reads) and the reader prompt with no budget
- **Paused 2026-10-26 (team lead):** "pause after the 5 current agents
  complete and backlog the remaining for the next sprint". Sprint 13
  finishes groups g001 to g042 of `manifests/sprint13_g_ledger.json`
  and applies them; groups g043 to g329 move to F114.

**F114. Read in full the papers in Task G groups g043 to g329, with no reading budget (no estimate: as long as the reads take) Priority 10** (NEW 2026-10-26, team lead at Sprint 13 Task G: "pause after the 5 current agents complete and backlog the remaining for the next sprint")
- Phase: Sourcing / extraction
- Value: finishes F113. **Snapshot as of 2026-10-26**: 287 groups, 1,430
  records, in `manifests/sprint13_g_ledger.json`, none read by a
  Sprint 13 reader.
- Platform: the same as F113: `manifests/sprint13_g_reads/READER_PROMPT.md`
  (with its "Progress and restart" section), up to 5 first-pass readers,
  the coordinator review of each group, and `scripts/sprint13_g_reading.py`
  for the apply with its verified backup
- Acceptance: F113's acceptance, for groups g043 to g329; each group's
  reader file and review committed under `manifests/sprint13_g_reads/`
  and `manifests/sprint13_g_reviews/`; a second apply writes nothing.
- Depends on: F113's groups g001 to g042 applied in Sprint 13
- **Cloud reads, 2026-10-26 to 2026-10-27** (team lead: "q2 1"): papers
  read one per Claude Code cloud session by `scripts/f114_cloud.py`,
  results held outside the repository until the coordinator review.
  Stopped 2026-10-27 at 11:30am when the $246 of cloud credit reached $0
  (team lead: "Can stop sending more papers and backlog the remainder for
  next sprint"). **Snapshot as of 2026-10-27**, of the 1,430 records:
  - 302 results fetched, each on its branch `cloud/f114/<record>` and
    saved outside the repository, every one passing
    `scripts/sprint13_g_check.py` against its PDF; groups g043 to g102
    hold 58 groups read whole. None is reviewed or applied yet.
  - 3 kept unread: udaru-2025-qml-credit-risk (below);
    abbas-2020-power-quantum-neural-networks (three sessions pushed
    nothing); boyd-2004-convex-optimization (team lead: "keep it as unread
    until next sprint"; its session labeled the read full but read 714 of
    715 page segments, took nothing from Appendices A and C, and only
    sampled the examples, exercises and figures). To finish it (team
    lead, 2026-10-27: "is it possible to send the current results and
    ask it to complete the read?"): yes. Its 184 assertions and 3
    verdicts move from `done/` to `partial/` on its branch, with a
    `progress.json` note naming each part not yet read; a new session
    resumes from them, under the prompt's "Progress and restart", and
    adds to them instead of starting over.
  - 1,126 never sent: they stay in this card for the next sprint.
  - **Finding for the coordinator review:** a cloud reader can label a
    read "full" while saying elsewhere that it sampled, and the check
    passes it, because the check sees only an empty `not_read`. Each
    result's own summary is read against its `read_extent` before it is
    applied.
- **Unread, 2026-10-27 (team lead: "mark udaru-2025-qml-credit-risk as
  unread")**: its PDF (`Papers\QML Quantum Machine Learning For Credit
  Risk -A Next-Generation Approach To Risk Assessment 202511.pdf`, group
  g076) holds page images only; pdftotext gives 10 empty pages. Three
  cloud sessions got no text, and none pushed a result. It has no
  `paper_reads` row and keeps none until F115 gives it a text layer.

**F119. Read Brighindi's PHI-OMEGA paper with its post, comment thread, image and code, first in Sprint 14 (~60m [no-history] timebox) Priority 10** (NEW 2026-10-28, team lead: "add the following text and paper to the paper repository and terget read for next sprint - highest priority"; "the paper is ML-related as it is rlated to predictions/solvers"; Sprint 13 Manual Validation Q9 = 1, first, before F117; Q10 = 1, files and card added during Manual Validation)
- Phase: Sourcing / extraction
- Value: the paper claims that energy drift is "mathematically impossible"
  under its "algebraic metric closure"; a claim in the solver and
  prediction space (context `ml`, the team lead's call) enters the store
  only with what supports it, and what does not.
- Platform: everything outside version control (ADR-0005 section 3),
  described in two references (Sprint 13 Manual Validation Q12 = 1, team
  lead 2026-10-28): PHI-OMEGA / M-OMNIA in
  `References\2026-09_Brighindi_PHI-OMEGA_LinkedIn-post-and-comments.md`,
  and the MB-X.01 structural-coherence code (lon-mirror, OMNIA, the
  Zenodo archive) in
  `References\2026-04_Brighindi_MB-X.01-Structural-Coherence_LON-mirror-OMNIA.md`:
  - the paper, `Papers\2026-09_Brighindi_From-Open-Heuristics-to-Native-Runtime-Invariance.pdf`
    (3 pages, 2026-09-25, self-published);
  - the LinkedIn post and its comment thread, as the team lead pasted them;
  - the image, `ImagesAndVideo\Phi-Omega Invariant Substrate vs. Legacy Solvers.jpeg`
    (read by eye until F116 exists);
  - the code: DOI:10.5281/zenodo.19857066 saved in `GitHubRepos\` (the
    Tuttotorna GitHub account returned 404 on 2026-10-28), and, cloned
    to `GitHubRepos\` from the `phiomegaruntime-rgb` account,
    `m-domain-independent-core` (69a65eb), `m-omnia-validation`
    (d3e45f3) and `phi-infinity-runtime` (4ee4ea3);
  - two more images and an earlier post (2026-09-23), added the same day.
- What a first look found, 2026-10-28, before any read: no proof, no
  theorem and no results data in the paper, which says its "logs,
  cycle-by-cycle metrics, and comparative visual plots ensure full
  reproducibility"; the author's own `phi-infinity-runtime` holds the
  paper's stress test (seed 20260925) and says, in Italian, that the
  raw files and `simulation.py` are not published, that the counts are
  not reproducible from the repository, and that no "absolute immunity"
  follows from one seed; `m-omnia-validation` says "no empirically
  verified result is claimed"; the comment by Valerie Calveyrac asks for
  the theorem the paper does not give.
- Acceptance: the paper read in full (no budget); a paper record with its
  `access`; every claim entered with its quote and certainty; the absence
  of the reproducibility material entered as an absence claim with its
  search scope; the post, comments and image entered as the author's own
  claims, distinct from the paper; of the 608-file Zenodo archive, only
  the parts that bear on the paper's claims are read (Sprint 13 Manual
  Validation Q11 = 1, team lead 2026-10-28).
- Depends on: none

**F117. Review the 302 cloud results of F114, with each step on the cheapest model its protocol allows, then apply them (~480m [no-history] timebox) Priority 20** (NEW 2026-10-27, team lead: "do the follow-up review of the 302 results (determine which model is needed for this - or can it be split into multiple sections where one or more can be completed by haiku 5.5... sonnet 5.5... opus 5.5")
- Phase: Sourcing / extraction
- Value: 302 full reads (snapshot as of 2026-10-27) wait outside the
  store; until reviewed and applied, none of their verdicts or assertions
  counts.
- Platform: the results saved by `scripts/f114_cloud.py fetch` and their
  branches `cloud/f114/<record>`; the review tooling of Task G (one
  decision file per group); `scripts/sprint13_g_reading.py` for the apply
  with its verified backup; `.claude/model_assignment_heuristics.json`
- Split by protocol, not by tier alone. The heuristics' own evidence
  (Sprint 3, `learning_log[0]`): a per-record review with no source access
  confirmed 18 of 18 records at every tier, while the review with
  primary-source access found the defects. So a cheap tier gets only the
  steps whose answer is in the file itself:
  - **No model (script):** the quote check against the PDF (all 302 pass,
    2026-10-27), the schema, ids, a verdict on every stored assertion,
    and assertions per page against Task G's local reads.
  - **Haiku 5.5 (classification and extraction, the models page's stated
    use):** flag a result whose own words contradict its label: "full"
    beside "sampled", "selective" or an unread appendix, as Boyd's did;
    flag a HIGH suggestion whose `certainty_reason` names no settling
    passage; list each result's figures and tables named but not entered.
  - **Sonnet 5.5 (per record, with the paper's text):** each corrected,
    narrowed, widened or contradicted verdict, and each HIGH suggestion,
    checked against the passage it quotes; THEORY_LOW and NOT_HIGH
    decisions drafted per group, as Task G's reviews did.
  - **Opus 5.5 (set level, cross-record):** the same judgment made
    differently across groups, and every verdict that contradicts a
    stored assertion; it signs off each group's decision file.
  - **Team lead:** any certainty level a review changes, as the
    escalation triggers require.
- A review at any tier that confirms every record with no rejection is
  re-run with source access before it is trusted (escalation trigger).
- Acceptance: each of the 302 has a decision; the flagged results are
  sent back for a complete read, or kept unread with the reason; the
  apply's counts before and after; a second apply writes nothing; each
  tier's outcome logged in the heuristics' `learning_log`.
- Depends on: F113's groups g001 to g042 applied (Sprint 13)

**F118. Learn what the store says about QC, ML, QML, tensor networks and related physics, for the QML and ML credit card fraud challenge (~240m [no-history] timebox) Priority 22** (NEW 2026-10-27, team lead: "suggest an approach to look at the EvidenceBasedDB and determine what we have been able to learn about QC, ML, QML, Tensors and other quantum physics-related items that apply to QC and that could be related to QML/ML Credit Card Fraud challenge")
- Phase: Use of the evidence
- Value: the store exists to serve the fraud submission
  (`hsbc-qfraud-phase2`); this turns its assertions into answers to the
  questions that submission must settle, with each answer's certainty.
- Platform: the store (read only); Phase 2's repository, read for its
  open questions (reads are free, writes never cross: F79); a generated
  report, so no value is copied by hand
- Approach:
  1. **Questions first.** List the decisions the fraud work faces, read
     from Phase 2's plans and open items, for example: does any quantum
     kernel or variational classifier beat a tuned classical model on
     tabular, imbalanced data; what data encoding scales to the feature
     count; what noise, barren plateaus, dequantization and sample
     complexity rule out; what tensor-network and quantum-inspired
     methods offer classically; what QUBO and Dirac-3 style solvers do
     for feature selection; which anomaly-detection results transfer.
  2. **Inventory, computed.** Counts by context (`qc`, `ml`, `qml`,
     `method`, `world`), certainty and result type, each stated as a
     snapshot of its date.
  3. **Map assertions to questions.** Keywords first, then a Haiku 5.5
     classification pass, each mapping checked on a sample.
  4. **Synthesis per question** (Opus 5.5): what is settled (HIGH, with
     the proof or stated limit), what is only claimed or measured and
     under what conditions (simulated or hardware, qubits, dataset size),
     where assertions conflict, and what is missing. Every line cites
     assertion ids; the report is rendered from the store, never typed.
  5. **Gaps to backlog.** A question the store cannot answer becomes a
     reading target or a Phase 2 experiment, sent as a pasted prompt.
- Acceptance: the question list with its source in Phase 2; one section
  per question generated from the store; the gaps carded.
- Depends on: F117 (the review first, so the synthesis reads reviewed
  assertions)

**F115. Convert the text in page images to text, mainly in PDFs (~120m [no-history] timebox) Priority 20** (NEW 2026-10-27, team lead: "add a method to convert images in documents (primarly PDF's) that are text to text")
- Phase: Sourcing / extraction
- Value: a source whose pages are images gives the quote check no text, so
  no assertion from it can be verified, and a reader gets nothing to read.
  The first known case is udaru-2025-qml-credit-risk (F114 above).
- Platform: `store/quotes.py` (`source_text`, `_pdftotext` and its text
  cache); an OCR engine to be chosen and verified against its own
  documentation (for example Tesseract, or pdftotext's own output first
  checked for empty pages)
- Find every local source whose text layer is empty or nearly empty, page
  by page, and list them with a count as of the date run.
- Convert those pages to text, kept outside git like the text cache, and
  say in each record's provenance that its text came from OCR, with the
  engine and its version.
- Decide, as a team-lead question, whether a quote verified only against
  OCR text may be graded high.
- Acceptance: udaru-2025-qml-credit-risk gives its text to the quote
  check; the list of image-only sources, with its date; a test that fails
  when an image-only page is read as empty without being flagged.
- Depends on: none

**F116. Read the figures in a source: what a graph shows, and where the text confirms it (~180m [no-history] timebox) Priority 40** (NEW 2026-10-27, team lead: "read images that are graphs... and interpret the images (if a graph, what does the graph say and how is it confirmed in text)")
- Phase: Sourcing / extraction
- Value: readers now skip figures (Task G's prompt counts a plot as read
  when its caption and the text around it are read), so a result shown
  only in a graph is never entered, and a figure that disagrees with its
  text is never caught.
- Platform: the reader prompts (`manifests/sprint13_g_reads/READER_PROMPT.md`
  and `manifests/f114_cloud/READER_PROMPT.md`); page images rendered from
  the PDF for a reader that can see images
- For each figure: what kind it is (a plot, a diagram, a table as an
  image), what it shows (axes, trend, the values it marks), and the
  passage in the text that states or confirms it, quoted.
- A value read only from a figure is marked as read from the figure, as
  `read_from_page` already does for coordinator edits, and is never
  graded high on the figure alone.
- Acceptance: a pilot on a few papers with key results in plots; each
  figure entry names its figure number and page and quotes the confirming
  text, or says that no text confirms it.
- Depends on: F115 for figures inside image-only sources; none otherwise

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
