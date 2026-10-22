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

## Last Completed Sprint

Sprint 10 is below; Sprint 9 follows it for continuity.

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

**Sprint 11** (branch `feature/20261021_Sprint_11`, cut 2026-10-21 at the
Sprint 10 carry-forward, after PR #101 merged to develop and PR #112 merged
develop to main).

- **Scope**: not yet selected (Phase 1.4).

## Next Sprint Candidates

Refined 2026-10-21 after Sprint 10 (Sprint 11 Phase 1.2); Sprint 10's shipped
cards pruned BY HAND (Edit tool, card by card) the same day.
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
copy carried as F90). F39 and F57 are
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

**F39. Evaluate the available models and update the model-assignment heuristics -- PERMANENT (~1h per release) Priority 50** (NEW 2026-09-29)
- Phase: Process (recurring)
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
- Depends on: nothing

### HOLD Items (waiting on an external event)

**F51. The CVQBoost findings record and its six assertions (~45m) Priority HOLD** (NEW 2026-10-03)
- Phase: Sourcing / intake
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
- Depends on: the hsbc repository's re-run of the experiment.

### Carded at Sprint 6 Manual Validation, 2026-10-05

**F57. Read for claims: the records still at `seen` and `screened` (permanent, released in slices) Priority 70** (NEW 2026-10-05, team lead at Sprint 6 MV)
- Phase: Sourcing / extraction (permanent item, like F39)
- Team lead, 2026-10-05: "what else has not been read for claims - if not
  in backlog, add backlog item to do any missing 'read for claims' entries".
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

### Carded at Sprint 10 Manual Validation (2026-10-19)

**F90. Read the eight F89 papers with no free copy, once the team lead has downloaded them (~45m) Priority 60** (NEW 2026-10-19, Sprint 10 Manual Validation step 5)
- Phase: Reading
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

### Carded 2026-10-19, after Sprint 10 Manual Validation

**F91. Enter and read Google Quantum AI's magic state cultivation experiment, Science 2026 (~1h) Priority 62** (NEW 2026-10-19, team lead request; carded at Priority 65, moved to 62 at Sprint 11 Phase 1.4 to keep the step-of-10 rule, as a reading item that sprints with F90)
- Phase: Sourcing / intake, then reading
- Platform: `scripts/intake.py`; `D:\Data\Harold\EvidenceBasedDB\Papers\`
- Team lead, 2026-10-19: "Can you add this paper to the backlog for the
  next sprint", with a screenshot of `DOI: 10.1126/science.aee7961`.
- **Facts at carding (snapshot as of 2026-10-19, from Crossref and arXiv,
  read only)**: Rosenfeld, Gidney, Roberts et al. (Google Research, with
  NASA Ames co-authors), "Magic state cultivation on a superconducting
  quantum processor", Science, published online 2026-10-15, article
  eaee7961, 65 references. Crossref lists the license as starting
  2027-10-15, so the publisher's copy is likely paywalled until then (not
  checked). The free preprint is arXiv:2512.13908 (v1). The abstracts
  differ: the Science abstract says the state fidelity is "at least"
  0.9999(1); the arXiv v1 abstract omits "at least". Data:
  DOI:10.5281/zenodo.17872003. The theory it tests,
  Gidney, Shutty and Jones, arXiv:2409.17595, is a reference.
- Not found in the repository's manifests or scripts by either
  identifier (code search, 2026-10-19). The store itself is local and
  was not checked; the door skips an id already present.
- Context by intake section 8: `qc` (a device demonstration of quantum
  error correction; no ML workload, and not a `world` result).
- Scope: (1) enter by `DOI:10.1126/science.aee7961`, with the arXiv
  preprint linked as `version_of` and its free PDF saved to `Papers\`
  under section 3's convention (inside the arXiv cap); (2) read it and
  enter the headline claims as assertions (error reduction factor,
  fidelity bound, acceptance rate), each quote checked before the write
  (intake section 26) against the preprint, with every place the
  published wording differs recorded; (3) optionally enter
  arXiv:2409.17595 at `seen` as the protocol it tests.
- Acceptance: the record at `read` with its assertions, or at `seen`
  with the reason it was not read; the abstract difference above
  recorded in the record's evidence.
- Depends on: none

### Carded at Sprint 11 Phase 1.4 (2026-10-21)

**F92. Enter QCi's 2026-10-20 and 2026-10-21 answers to Phase 2's Dirac-3S questions, and correct the records they change (~1h15m) Priority 40** (NEW 2026-10-21, read from Phase 2 at Sprint 11 Phase 1.4; widened the same day by two later emails)
- Phase: Inbound evidence (F79)
- Platform: the store; `hsbc-qfraud-phase2` read only
  (`docs/phase2/DIRAC_UNDERSTANDINGS.md` section 4 at commit b074780, and
  the three replies under `docs/qci_package/`)
- A QCi field service engineer answered Phase 2's questions A1 to A12 and
  P2 on 2026-10-20 (P1 still open at b074780). Two later emails, filed
  2026-10-21 (team lead), add:
  - **P1 answered.** Wes Dyk (QCi), 2026-10-21: "I can confirm that the
    Hamiltonian constructed in eqc_models.ml.classifierqboost follows the
    formula described" (J = HH^T + lambda*I, C = -2Hy, sum 1, w >= 0),
    opening "I'm assuming you are referring to your eqc_submit module".
    Bears on `dirac3-matches-exact-optimum-on-convex-cvqboost`, whose
    "identical Hamiltonian" rests on that reading.
  - **Integer levels raised.** Charlotte Brown (QCi), 2026-10-21: "We have
    increased to 954 levels on the integer solver on both the 3 and 3S
    systems. In the coming weeks, we will be also increasing the possible
    levels on 3S to 9980 levels as well." It does not say whether 954 is
    per variable or the total budget; record that gap, do not resolve it.
    Bears on `dirac3-integer-variables-bounded-0-to-16`,
    `dirac3s-guide-gives-two-integer-ranges` and A4's "16 levels". The
    9980 is a plan, entered as a stated plan, not a capability.
- Several answers bear on records in the store (read at b074780, snapshot
  as of 2026-10-21):
  - A6b: raw values are not yet offered on the cloud; outputs are after
    built-in error correction (A6a). Bears on
    `dirac3s-error-correction-is-a-post-processing-step` and
    `dirac3s-returned-weights-finer-than-0005-step`, which says "QCi
    states raw values come back too".
  - A9: every result in the Dirac-3S guide was measured on-premises on a
    Dirac-3S, computation only. Bears on
    `dirac3s-guide-reuses-dirac-3-text-and-figures` ("the guide does not
    say whether those results were measured on a Dirac-3S").
  - A4 (16 levels, values 0 to 15, hedged "I assume"); A11 (the cloud cap
    is 100 samples per job); A12 (not seedable); A6 (resolution the same
    as Dirac-3's about 200:1). Bear on
    `dirac3s-guide-gives-two-integer-ranges`,
    `dirac3s-on-premises-has-no-100-sample-cap` and
    `dirac3s-analog-resolution-about-200-to-1`.
- Grading: a vendor's own statement, by email, not a published document;
  each answer's hedge kept (A4's "I assume").
- Acceptance: each email's primary copy read in Phase 2's
  `docs/qci_package/`. Phase 2 git-ignores that folder, so no commit
  names it: provenance names the file, its SHA-256 at read (the 2026-10-21
  pair: Wes e79296e68a0d82bc..., Charlotte 6f9254b78b208df2...), the
  sender and the send date. Each answer that bears on a stored claim entered as a
  vendor-statement assertion under `platform:dirac-3s` (or
  `platform:dirac-3` for A2), related by ADR-0004 A8 (b) (`contradicts`
  only where both cannot hold); every quote checked through the verified
  write path (intake sections 26 and 31). Stored assertions are not
  rewritten: a newer statement is related to them.
- Depends on: none

**F93. Enter Phase 2's F108 result: no ceiling method recovered a known ceiling on a simulator (~1h) Priority 80** (NEW 2026-10-21, read from Phase 2 at Sprint 11 Phase 1.4)
- Phase: Inbound evidence (F79)
- Platform: the store; `docs/research/ceilings-ml-and-optimization.md`;
  `hsbc-qfraud-phase2` read only (`docs/phase2/F108_CEILING_VALIDATION.md`
  at commit eef3349, 2026-10-18)
- Phase 2 built a fraud simulator whose Bayes error is known exactly and
  tested ceiling estimators against it (five seeds). Its BLUF: on the main,
  no-noise arm no method recovered the known ceiling, so none is validated
  for real data. The plug-in overstated the Bayes error by 5-12 percent;
  the learning-curve floor did similarly; the AUPRC floor understated the
  attainable AUPRC by about 0.04; the Cover-Hart interval held the truth
  on 3 of 5. Phase 2 states its own caveat: the pass rule was read after
  the run.
- This answers, in part, what the ceilings answer document leaves open:
  its learning-curve route (Ding) is one of the methods F108 tested.
- Acceptance: the document read at the commit current when the work
  starts; 3 or 4 assertions (context `ml`, with `hsbc-2026` where Phase
  2's own data is meant) through the verified write path, Phase 2's
  caveats carried into the values; a dated amendment to the answer
  document naming them.
- Depends on: none

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
