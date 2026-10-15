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

## Last Completed Sprint

Sprint 8 is below; Sprint 7 follows it for continuity.

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

**Sprint 9** (branch `feature/20261014_Sprint_9`, cut 2026-10-14 at the
Sprint 8 carry-forward, after PR #77 merged to develop and PR #87 merged
develop to main). **Scope (DEFINED, team lead 2026-10-14)**: F78, F79,
F74, F68, F69, F62, F57, F55, F56, F48, F46, F51. F51 is a HOLD item
selected while its hold stands; planning checks whether the Phase 2
repository now holds the re-run it waits on. Priorities renumbered at
selection in steps of 10, 2 for items that sprint together (the slate's
numbers, which the team lead's selection used): F78 10, F79 20, F74 30,
F68 40, F69 42, F39 50, F62 60, F57 70, F55 80, F56 82, F48 90, F50 100,
F46 110. F57 released as F80. Plan: `docs/sprints/SPRINT_9_PLAN.md`.

## Next Sprint Candidates

Refined 2026-10-14 after Sprint 8 (Sprint 9 Phase 1.2); Sprint 8's shipped
cards pruned BY HAND (Edit tool, card by card) the same day.
Shipped and pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint
2); F2 Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25,
F26, F27 (Sprint 4); F5, F28, F30, F31 (Sprint 5); F32-F38, F40-F43, F47
(Sprint 6; F35's 30 unlinked notes continued as F54, F41's CVQBoost part as
F51); F44, F45, F52, F53, F54, F58, F59 (Sprint 7; F53's per-cycle refresh
replaced by F64's 12-month re-check; F54's 10 "unsure" and 140 third-party
repository candidates stay held back in `sprint7_f35_screen.json` and
`QMLPapers\Repos\REVIEW.md`); F60, F61, F63, F64, F65, F66, F67, F71
(Sprint 8). F39 is permanent and stays. Closed without
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

### Cyc and CVQBoost intake (proposed 2026-10-03)

Registered 2026-10-03 at the team lead's request from
`D:\Data\Harold\EvidenceBasedDB\Handoff-2026-10\ebdb-handoff\12-backlog-cards-proposed.md`,
prepared outside the repository; card text as drafted there. File names
`01` to `12` (`03-manifest-sources.json`, `07-assertion-candidates-pending.md`,
`11-decisions-2026-10-03.md`, and so on) refer to that folder;
`FACTS-WITH-CERTAINTY.md` is in its parent, `Handoff-2026-10\`. All
estimates are `[no-history]`.

**F46. Remaining reading pass: the other pending facts, split at selection (~large, no-history) Priority 110**
- Phase: Sourcing / extraction
- Platform: N/A
- The rest of `07`: World (8), entanglement (1), the April 2026 claim (4),
  classical fraud detection (7), ceiling estimation (9). Too large for one
  card; split by source group when a sprint selects it.
- Depends on: F45 (shipped in Sprint 7; its actual, 14 assertions from
  seven sources, calibrates this estimate).

### Store and process lessons from Cyc (proposed 2026-10-03)

**F48. Keep local source paths honest (~2h) Priority 90**
- Phase: Tooling
- Platform: `store/ingest.py`, a new check script
- A local `access` path breaks silently when a file moves. Seen during the
  Cyc work: three archives moved to the Recycle Bin; the hsbc repository
  exists at two paths, and only one has `docs\`.
- Acceptance: SHA-256 recorded for every local-access source; a check that
  reports a missing file or a changed hash; a test with one moved file that
  the check catches.
- Depends on: none. F41 adds nine local-access sources, so earlier is
  better.

**F50. Qualify "compute, never store" with Cyc's stored counts (~30m) Priority 100**
- Phase: Process
- Platform: `docs/research/cyc-knowledge-representation.md` (dated amendment)
- Point 7 says counts should be computed, never stored. Cyc stores a count at
  every index layer and the planner reads it as the lookup cost
  (`removal_modules_lookup.java`, line 84). The difference: Cyc keeps the
  count beside the data and updates both together.
- Acceptance: a dated amendment to point 7. A stored count is allowed only
  with a test that recomputes and compares it.
- Depends on: none.

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

**F55. Record which papers cite which, as a computed link (~2h) Priority 80** (NEW 2026-10-05, Sprint 6 MV Q10 = 1)
- Phase: Sourcing / computed fields
- Platform: Crossref reference lists (`works/<doi>`, field `reference`),
  arXiv-to-DOI via `version_of`; `source_links`
- A `cites` link between two SOURCE records in the store, computed from the
  publisher's reference list (probe rule: last result, date, provider),
  never typed by hand. Recorded once, readable from both ends.
- Not a certainty input (Q10 = 1): a citation is not corroboration, since a
  citing paper may criticize. Its use is to FIND candidate corroboration
  for F56: the papers that cite A are where to look for evidence on A's
  claims.
- Needs an ADR-0005 amendment (a new link type, computed). Coverage is
  partial: many arXiv preprints have no Crossref reference list.
- Acceptance: links for every pair both in the store where a reference list
  answers; coverage reported; no link typed by hand.

**F56. Should corroboration raise an assertion's certainty, and how? (~1h decision, then build) Priority 82** (NEW 2026-10-05, team lead at Sprint 6 MV)
- Phase: Design / ADR (Class 1)
- Team lead, 2026-10-05: "if we have a paper who's assertions scores very
  high and with verifiable evidence and it is linke to another paper that
  verifies the claims of the first paper or otherwise increases the
  confidance of the assertions of the other paper, shoudn't that affect the
  assertions/claims in some way" ... "Think it is important and could be
  used, but not sure how".
- Today only downward caps are computed (ADR-0004 A6); `supports` between
  assertions is recorded but never moves certainty. GRADE does raise
  certainty for consistent results across independent studies.
- Options to decide: (1) a computed "corroborated" flag beside the stored
  certainty when an assertion is supported by an INDEPENDENT assertion
  (different authors, not the same vendor) at equal or higher certainty;
  the assessor then decides an upgrade, with the reason; (2) a computed
  upward cap, symmetric to A6's; (3) leave it to judgment, as now.
- Independence is the hard part: same lab, same dataset, or the same vendor
  is not corroboration (the admission-against-interest rule's logic).
- Depends on: F55 helps find candidates; not required.

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

### Carded during Sprint 7 (2026-10-06 to 2026-10-10)

**F62. Discover, rank and triage candidate papers from open metadata, with a hand-download list (~4h plus review) Priority 60** (NEW 2026-10-06, team lead during Sprint 7, Q11 = 1 and 3)
- Phase: Sourcing / discovery
- Platform: `scripts/discover_candidates.py` (pilot built in Sprint 7),
  OpenAlex (abstracts, topics, citations, open-access copies), Semantic
  Scholar (cross-check: arXiv id, citations, free PDF), `scripts/intake.py`
- Team lead, 2026-10-06: "is there a way to get enough of the papers
  related to QML and ML (targeting and prioritizing around what we think
  are valuable) to evaluate the papers we would be interested, then check
  all the other sources and develop a prioritized sub-list of papers we may
  want to download by hand"; "... and tensors"; "we are interested in the
  best of Machine Learning (ML) even if it is unrelated to Quantum
  Computing and Credit Card Fraud and Fraud".
- Pipeline: discover by stream; drop what the store holds (DOI, arXiv id,
  normalized title); rank (computed each run, never stored); the team lead
  reviews the top of each stream on title and abstract; chosen papers enter
  through the door by DOI at `seen`; for papers chosen for READING, the
  free copy (arXiv first, inside F52's cap; then other open copies); the
  rest form the hand-download list (rank, title, DOI, publisher link, why,
  target file name). F61's survey list is one more discovery input. IEEE
  PDFs by hand only (F61's note: Xplore's license bars automated downloads).
- **Pilot facts (snapshot as of 2026-10-06; 25 per stream, keyless)**:
  - Streams: ml (the most-cited works in OpenAlex's Artificial
    Intelligence and Computer Vision subfields since 2012), qml, tensor,
    fraud.
  - Already in the store: qml 14 of 25; ml, tensor and fraud 0 of 25.
  - Abstract present: ml 21, qml 17, tensor 21, fraud 20 (of 25 each).
  - No free copy, so hand-download candidates: ml 6, qml 1, tensor 4,
    fraud 12. Fraud is where an account matters most.
  - Precision findings: OpenAlex's `search` parameter matched far too
    broadly (a sentiment-analysis survey for QML, YOLO for tensor
    networks); the `title_and_abstract.search` filter fixed qml and
    tensor, and fraud needed "fraud" in the TITLE plus an ML term in the
    abstract.
  - Data-quality finding in the ml stream: OpenAlex merged-record errors
    distort citation ranks (a tutoring-systems paper credited with 78,458
    citations; "Attention Is All You Need" as a 2025 record under an
    unknown DOI prefix). Before ranking, cross-check citations against
    Semantic Scholar and collapse duplicate titles to the canonical record.
- Budget: OpenAlex meters a daily budget (keyless about 100 searches;
  single-DOI lookups free); the team lead has an OpenAlex key, read from
  `OPENALEX_API_KEY` (user environment) and sent only in the Authorization
  header. Semantic Scholar: 1 request per second with a free key.
- Acceptance: a ranking rubric approved by the team lead; per stream, a
  reviewed top list; the chosen papers entered; a hand-download list with
  every entry's free-copy search recorded.
- Depends on: F52's cap for arXiv; F61 (shared discovery input).

### Carded during Sprint 8 (2026-10-10 onward)

**F68. The door misses two identifier forms: old-style arXiv ids and DOIs with parentheses (~1h) Priority 40** (NEW 2026-10-12, found in Sprint 8 Task F)
- Phase: Sourcing / intake
- Platform: `store/citations.py` (`parse_access`), `scripts/intake.py`
- Found running F61 against the Massoli list (2026-10-12): `arXiv:quant-ph/0405098`,
  `quant-ph/0107012` and `quant-ph/0001106` were refused as hand-origin ("needs
  --id"), because `parse_access` reads only new-style ids; and
  `10.1016/s0020-0255(00)00055-4` and `10.1016/0304-4149(89)90040-9` were cut at
  the parenthesis and refused as unregistered. Both are real, registered
  identifiers.
- Acceptance: both forms resolve through the door; a test for each, proven by
  injection; the five Massoli entries re-run through F61's script.
- Depends on: none

**F69. Enter the Cerezo NonArxiv paper, "Key questions for the quantum machine learner to ask themselves" (~20m) Priority 42** (NEW 2026-10-13, team lead at Sprint 8 Manual Validation, Q8 = 1; found in Sprint 8 Task E)
- Phase: Sourcing / intake
- Platform: `scripts/intake.py`; the local file
  `D:\Data\Harold\EvidenceBasedDB\QMLPapers\NonArxiv\Cerezo_2020_Key-questions-for-the-quantum-machine-learner-to-ask-themselves.pdf`
- F60's check (2026-10-12) found this PDF in `QMLPapers\NonArxiv` with no
  manifest row and no store record (by id, access or title). It has no
  arXiv id in its file name.
- Acceptance: its identifier (DOI or arXiv id) found from the PDF or a
  search, or the record entered by local path plus SHA-256; entered at
  `seen` through the door with `found_via` naming the QMLPapers folder; or
  recorded as out of scope, with the reason.
- Depends on: none

**F78. Ceiling estimation: read the whole CE group in full and enter it, so the store answers "can this dataset or problem be done better?" (~7h) Priority 10** (NEW 2026-10-14, team lead EDB query, Q1 = 1, Q3 = 2 everything in full, Q4 = 1 first task of Sprint 9; TARGET: Sprint 9)
- Phase: Content / reading
- Platform: the 31 records whose disposition names `[CE-n]` (the HSBC
  Phase 2 bibliography's "Ceiling estimation / Bayes error" group); local
  copies in `D:\Data\Harold\EvidenceBasedDB\Papers\` and `References\`;
  a new `scripts/sprint9_f78_ceiling_reading.py` (dry run by default,
  verified backup on `--apply`, idempotent)
- Team lead, 2026-10-13: "did we find the paper that proposes/finds a
  theoretical optimum for any ML ... cannot be any more than X ... confusion
  matrix, AUPUC or other", then "it might not have been ML, but an
  optimization problem"; 2026-10-14: "add all of them to the store, read
  them all and update the database", and "is there a way to find the
  maximum, near maximum predictions or can't be better than... on any ML
  dataset and/or any optimization problem. This will be helpful at least on
  wether further improvement can be done on a dataset or if a better
  dataset is needed."
- **Facts at carding (snapshot as of 2026-10-14, read only)**: 31 CE
  records; 1 read (McDermott, CE-5); 6 read on 2026-10-13 and not yet
  recorded (Boyd, Dhama, Butt and Tschirschwitz in full; Zhao, CE-7, and
  Ushio in part); 14 unread ceiling or Bayes-error papers (11 with local
  copies; Chen 2025, Te Sun 1994 and Thanh 2026 publisher-only); 3
  synthetic-data papers (Allen, Altman, Ostman); 7 repositories or a
  handbook. Not in the store: Ishida et al., ICLR 2023 (arXiv:2202.00395)
  and Theisen et al., NeurIPS 2021 (arXiv:2106.03357).
- Scope: every item read in full (Q3 = 2), repositories by README and
  code; each read recorded in `paper_reads`; Zhao and Ushio finished; the
  ceiling, bound and method claims entered as assertions with section
  anchors (Butt's 0.451 F1 ceiling with the gap between its abstract and
  its Theorem 1 and its Table IV exceedance; Tschirschwitz's LVIS bound;
  Zhao's F-score and BER bounds; Boyd's AUPRC minimum); `access` pointed
  at the local copy plus the identifier; Ishida and Theisen entered
  through the door (two serial arXiv requests inside the cap); each
  publisher-only paper tried once and recorded if unobtainable.
- **Local copies (team lead, 2026-10-14: "also include adding any papers
  that are not downloaded as PDF's to the local repository in an
  appropriate folder")**: every paper in the group with no local PDF is
  downloaded into `D:\Data\Harold\EvidenceBasedDB\Papers\` (outside git;
  the folder that already holds the group's 11 local copies) under its
  `YYYY-MM_Author_Title.pdf` convention, with its SHA-256 recorded and
  `access` naming both the identifier and the path. Expected: Ishida,
  Theisen, Chen 2025, Te Sun 1994, Thanh 2026, Allen 2025; a paywalled one
  is recorded as such, not downloaded around the paywall. The 7
  repositories are read on GitHub; a clone into `GitHubRepos\` is asked at
  planning.
- Acceptance: every CE record at `read` or carrying a recorded reason it
  is not; every quote verified verbatim against its local copy by test;
  a short answer document for the team lead's question (ML ceilings and
  optimization bounds, each method with its source), with verified and
  inferred kept apart.
- Depends on: none

**F79. hsbc-qfraud-phase2 and this repository read each other freely and never write to each other; anything to be written goes as a pasted prompt (~30m) Priority 20** (NEW 2026-10-14, team lead "yes" to carding it, scope stated the same day and corrected the same day; TARGET: Sprint 9)
- Phase: Process / repository
- Platform: `CLAUDE.md`, `.claude/hooks/block_sibling_repo_writes.py`, its
  test, the read-but-never-write memory file, `docs/INTAKE_WORKFLOW.md`
- **Facts at carding (snapshot as of 2026-10-14)**: `kimmeyh/hsbc-quantum-fraud-2026`
  (Phase 1) is archived; the active consumer is `kimmeyh/hsbc-qfraud-phase2`
  (Sprint 26, PR 21 open; private, like this repository). CLAUDE.md still
  names the archived repository as the first consumer, and the
  sibling-write rule and hook list only `spamfilter-multi` and
  `hsbc-quantum-fraud-2026`.
- Team lead, 2026-10-14: "hsbc-qfraud-phase2 will be on ongoing consumer
  of the EvidenceBasedDB - it will read it and reference the library/store
  of papers, but never write to this repository - any transfer will be via
  prompt (it will write a prompt and I will copy/paste it into this
  session)). The EvidenceBasedDB is also a consumer of hsbc-qfraud-phase2,
  in that it will run QML tests/experiments against
  QC/photonic/entropy/reservior simulators and devices and those could be
  valuable additions to the EvidenceBasedDB. But this session cannot write
  to hsbc-qfraud-phase2 - any transfers to hsbc-qfraud-phase2 would be via
  prompts developed here and then pasted into the hsbc-qfraud-phase2
  claude session." Corrected the same day: "they are both consumers of
  each other and reads are permitted without direct prompts from the
  other - so each could read from each other, but cannot write to each
  other".
- Scope: (1) CLAUDE.md names Phase 2 as the consumer, keeps Phase 1 as
  history, and states the rule: each repository reads the other
  directly, with no prompt needed; neither writes to the other; a change
  wanted in the other repository goes as a prompt the team lead pastes; (2) the hook and
  the rule cover `hsbc-qfraud-phase2` (read freely, never write); (3)
  inbound: an intake path for Phase 2 experiment results, read directly
  from the Phase 2 repository (a pasted prompt may point at them, but the
  files at the named commit are the evidence), each entered with
  provenance naming the repository, commit and run, and certainty from
  that evidence;
  (4) outbound: a prompt shape for answers sent to Phase 2, with each
  claim's provenance inline (ADR-0005: no citation may depend on this
  private store resolving); (5) Phase 2's own read-only guard is that
  repository's change, so a prompt asking for it is drafted here for the
  team lead to paste.
- Acceptance: a hook test that a write into the Phase 2 path is blocked,
  proven to fail by injection; the intake path tried on one real Phase 2
  result.
- Depends on: none

**F80. F57 release for Sprint 9: read for claims, first slice of 76 (~3.5h) Priority 70** (NEW 2026-10-14, released from the permanent F57 at Sprint 9 scope selection; slice widened 2026-10-15 at approval, Q7 = 2)
- Phase: Sourcing / extraction (released copy of the permanent F57)
- Platform: the store; the 26 records at `seen` or `screened` under
  `hsbc-2026`, `platform:dirac-3` and `platform:dirac-3s` (snapshot as of
  2026-10-14), none in the CE group, plus the 50 most-cited `qml` records
  at `seen` or `screened`
- Scope per F57's release steps, the slice per Sprint 9 plan Q7 = 2.
- Acceptance: the slice screened; every promoted record read and
  yielding; every refused one with its reason.
- Depends on: none

**F74. Re-check correctness: a partial answer must not reset the 12-month clock, and a tool failure must not read as the paper's fault (~1.5h) Priority 30** (NEW 2026-10-13, PR #77 silent-failure review; TARGET: Sprint 9)
- Phase: Store / re-check (ADR-0005 A7)
- Platform: `store/recheck.py` (`last_check`), `scripts/probe_reference_fields.py`
  (the probe writes and `recheck_findings`)
- Found by the PR #77 review, 2026-10-13, read only:
  - **A partial answer resets the clock.** `last_check` is the latest
    `probed_on` over every provider except hand readings. If arXiv's
    abstract page fails and DataCite answers, the DataCite field is written
    with today's date, so the paper leaves `--due` for about 10 months with
    its version unread and its withdrawal unchecked. A `local file check`
    that records "local copy missing" does the same.
  - **A tool failure blames the paper.** When `pdftotext` is missing or
    fails, the first page reads as empty and the paper is listed as "no
    readable stamp"; a record whose probe raised is listed as "the abstract
    page showed no version".
- Scope: decide (ADR-0005 amendment) which probe answers count as a
  completed check, and count only those in `last_check`; report a tool
  failure as a tool failure. Both are design decisions about what the
  stored dates mean, so they are carded rather than patched in the review.
- Acceptance: a test where DataCite answers and arXiv does not leaves the
  paper due; a test with `pdftotext` unavailable reports the tool, not the
  paper; both proven to fail by injection.
- Depends on: F64 (done)

### Carded during Sprint 9 (2026-10-14 onward)

**F81. The code-edit hook blocks read-only `sed -n` commands (~30m) Priority 120** (NEW 2026-10-15, Sprint 9 Task A)
- Phase: Process / hooks
- Platform: `.claude/hooks/block_unraw_escape.py` (`_shell_edits_code`)
- Found 2026-10-15: two read-only commands were blocked as code edits. Each
  was `sed -n <range>p <code file>; ... | grep -i ...`. The hook's own
  message says "Reading with sed -n, cat or grep is fine." The likely cause
  (inferred, not yet tested): the in-place flag search runs over the rest of
  the command past `;`, so a later `grep -i` reads as `sed -i`.
- Cost: friction only. The Read and Grep tools work around it. But a guard
  that blocks correct work trains bypass.
- Acceptance: the two blocked shapes pass; `sed -i` on a code file is still
  blocked; both proven by injection.
- Depends on: none

**F82. Decide how far the never-write hook should go against evasive command forms (~1h) Priority 130** (NEW 2026-10-15, Sprint 9 Task A, third automated security review)
- Phase: Process / hooks
- Platform: `.claude/hooks/block_sibling_repo_writes.py`
- Three automated security reviews of the Phase 2 extension (2026-10-15)
  each found more forms a regex misses. Fixed the same day: `git -C`
  writes, PowerShell write cmdlets, `tee`, `sed -i`, a fail-closed git read
  list, write-capable options on reads, and `git` after a quote or
  backtick. Still open: abbreviated long options (`--outp`) and short-option
  clusters containing `O`; pager, editor and config environment variables
  (`GIT_PAGER`, `GIT_CONFIG_*`, `$env:` assignments); `--ext-diff` and
  `--textconv`; command names built from strings or variables (`iex`,
  `& (...)`, `$cmd`).
- The decision (Class 1): the hook's stated threat model is accidental
  writes by this repository's own sessions, not evasion. Option 1 keeps
  that model and closes only forms a session might type by accident.
  Option 2 makes every shell command that names a guarded path
  fail-closed unless it matches a short read allowlist, which blocks more
  legitimate reads.
- Depends on: none

**F83. Source per-instance bounds for optimization problems (~1h) Priority 140** (NEW 2026-10-15, Sprint 9 Task E answer document, section 5)
- Phase: Sourcing / reading
- Platform: the store; `docs/research/ceilings-ml-and-optimization.md`
- The answer document's optimization section has two verified routes
  (minimax lower bounds over a class; instances with a known or best-known
  optimum). The standard per-instance certificate (a relaxation or dual
  bound, and the gap an exact solver reports) is stated there as general
  practice with no source in the store.
- Acceptance: primary sources for relaxation and duality bounds (for
  example a linear or semidefinite relaxation text and a solver's gap
  definition) entered and read; section 5 point 5 rewritten as verified,
  with the store ids, as a dated amendment.
- Depends on: none

**F84. Nine QCi records name Dirac-1 but are tagged Dirac-3 (~1h) Priority 150** (NEW 2026-10-15, Sprint 9 Task G)
- Phase: Store correction
- Platform: the store (`record_contexts`, `contexts`)
- Eight QCi application pages name Dirac-1: seven state "Device: Dirac-1"
  in their header (dimensionality reduction, feature selection, graph
  partitioning, max-cut, portfolio optimization, set partitioning,
  traveling salesman), and the risk-based UAS trajectory page names Dirac-1
  throughout its body (Dirac-3 only as future work). The QC-7 article names
  Dirac 1 and never Dirac-3. All nine are
  tagged `platform:dirac-3`. The store has no Dirac-1 context, so Task G
  refused their figures and left them at `seen`.
- Acceptance: a decision on a Dirac-1 context (add `platform:dirac-1`, or
  retag to a general QCi context), the nine records retagged with the
  reason, and their first-pass assertions
  (`manifests/sprint9_f80_reads/group_j2.json` and `group_j3.json`)
  re-checked and entered against the right context.
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
