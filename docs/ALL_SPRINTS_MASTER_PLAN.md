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

## Last Completed Sprint

Sprint 7 is below; Sprint 6 follows it for continuity.

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

**Sprint 8** (branch `feature/20261010_Sprint_8`, cut 2026-10-10 at the
Sprint 7 carry-forward, after PR #68 merged to develop and PR #76 merged
develop to main). **Scope (DEFINED, team lead 2026-10-10)**: F65, F63,
F64, F60, F61, and an F39 release (registered as F67: "Haiku 5.5 was
released and we will want to include in the list of models"). F66, carded
the same day with a Sprint 8 target, is not in the selection list; it is
asked as a question at plan approval, never planned in by inference. Plan:
`docs/sprints/SPRINT_8_PLAN.md`.

## Next Sprint Candidates

Refined 2026-10-10 after Sprint 7 (Sprint 8 Phase 1.2); Sprint 7's shipped
cards pruned BY HAND (Edit tool, card by card) the same day.
Shipped and pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint
2); F2 Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25,
F26, F27 (Sprint 4); F5, F28, F30, F31 (Sprint 5); F32-F38, F40-F43, F47
(Sprint 6; F35's 30 unlinked notes continued as F54, F41's CVQBoost part as
F51); F44, F45, F52, F53, F54, F58, F59 (Sprint 7; F53's per-cycle refresh
replaced by F64's 12-month re-check; F54's 10 "unsure" and 140 third-party
repository candidates stay held back in `sprint7_f35_screen.json` and
`QMLPapers\Repos\REVIEW.md`). F39 is permanent and stays. Closed without
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

**F39. Evaluate the available models and update the model-assignment heuristics -- PERMANENT (~1h per release) Priority 10** (NEW 2026-09-29)
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

### Carded during Sprint 7 (2026-10-06 to 2026-10-10)

**F60. A mislabeled QMLPapers file: the "Asfaw 2108.0131" PDF is another paper (~30m) Priority 50** (NEW 2026-10-06, found in Sprint 7 Task E)
- Phase: Sourcing / collection hygiene
- Platform: `D:\Data\Harold\EvidenceBasedDB\QMLPapers\2021\manifest.tsv`
  (outside the repository; read only from here), `scripts/intake.py`
- Found reading the PDF for F54: the file
  `Asfaw-et-al._2021_Building-a-Quantum-Engineering-Undergraduate-Program__2108.0131.pdf`
  begins "arXiv:2108.00131v2 [cs.LG] 22 Feb 2022" and is Radhakrishnan,
  Stefanakis, Belkin and Uhler on infinite-width neural networks for matrix
  completion, the paper whose code its repository note names
  (`uhlerlab/ntk_matrix_`). The manifest row's title (Asfaw et al.) and its
  id (`2108.0131`, one digit short) do not match the file. The Asfaw paper
  itself was never downloaded; its real arXiv id is not yet verified.
- Sprint 7 Task E enters `2108.00131` (the paper on disk) and links its
  repository; this card is the rest: find the Asfaw paper's real id, decide
  whether it belongs in the collection, and look for other rows whose file
  is not the paper the row names (a first-page id check against the
  manifest id, all folders).
- Acceptance: every manifest row's id matches its file's first-page id, or
  the mismatch is listed; the Asfaw paper entered or recorded as out of
  scope with the reason.

**F61. Mine the Massoli et al. survey's curated paper list for candidates (~2h plus runtime) Priority 60** (NEW 2026-10-06, team lead during Sprint 7)
- Phase: Sourcing / collections
- Platform: `github.com/fvmassoli/survey-quantum-computation`
  (`allPapers.md`, `LeapIntoQuantumComputationsPaperList.xlsx`), the
  companion list of arXiv:2107.03313 ("A Leap among Quantum Computing and
  Quantum Neural Networks: A Survey"); `scripts/intake.py`
- Team lead, 2026-10-06, on the F35 screen holding this repository back as
  "neither code nor data": "this repository may contain papers that we are
  interested in (although there likely could be duplicates of what we
  already have)".
- **Facts at carding (snapshot as of 2026-10-06)**: 184 entries, each a
  link plus a BibTeX record, tagged by topic (Quantum Perceptrons, QNNs,
  gate model and adiabatic). 25 titles already match a store record exactly
  (an undercount: punctuation and subtitle variants miss); 31 entries carry
  an arXiv id, 9 of them already in the store. Most link to publishers (APS
  29, Nature 26, Springer 14, IOP 12, IEEE 11), so the door's DOI path, not
  arXiv, carries most of them; several BibTeX records have no DOI.
- Scope: duplicates are found before anything is entered (arXiv id, DOI,
  then normalized title and first author); new entries go through the door
  at `seen` with `found_via` naming this list and the entry's topic tags as
  the collection locator; the survey itself (2107.03313, already in the
  store) gets the list as its companion repository.
- Acceptance: every entry classed as already in the store (with the record
  it matched), entered, or refused with the door's reason.
- Depends on: arXiv entries share F52's cap; run outside its sessions.
- Timing (team lead, 2026-10-06, Q10 = 1): Sprint 8 backlog refinement, not
  added to Sprint 7.
- IEEE entries (team lead asked 2026-10-06; checked that day): IEEE papers
  carry Crossref DOIs (prefix 10.1109), so their RECORDS enter through the
  door's DOI path with no IEEE account; Crossref title search resolved the
  list's first IEEE-linked entry to its DOI. Many also have an arXiv
  preprint (IEEE's policy allows posting the accepted version). Only the PDF
  needs the team lead's IEEE account, and only by hand: IEEE Xplore's
  license allows individual downloads for personal research but prohibits
  systematic downloading "using a robot, spider, crawler, screen scraping or
  similar", and the Xplore API's personal key covers metadata and open
  access content only. So a PDF is fetched only when a paper is to be READ:
  its arXiv version first, else a list (DOI, Xplore link, target file name)
  the team lead downloads by hand into `D:\Data\Harold\EvidenceBasedDB\Papers`.

**F62. Discover, rank and triage candidate papers from open metadata, with a hand-download list (~4h plus review) Priority 62** (NEW 2026-10-06, team lead during Sprint 7, Q11 = 1 and 3)
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

**F63. Two Dirac-3 admissions in arXiv:2407.04512 as assertions (~1h) Priority 32** (NEW 2026-10-08, found in Sprint 7 Task G; team lead approved as a Sprint 8 candidate at Manual Validation)
- Phase: Content / assertions
- Platform: the store; record `nguyen-2025-entropy-computing-paradigm-optimization-open`
  (read partially in Sprint 7 Task G); a script in the pattern of
  `scripts/sprint7_f45_dirac3_reading.py`
- Two statements by QCi's own authors, found while reading for F45 and not
  entered (outside Task G's planned assertions). Both checked verbatim
  against the local copy with pdftotext on 2026-10-08:
  - p.15: "Our current Dirac-3 hybrid implementation does not utilize
    quantum entanglement."
  - p.6: the optical parts "do not involve large scale non-Gaussian quantum
    superpositions, they could in principle be instead classically
    simulated, as has been argued in the coherent Ising machine setting".
- Both are candidates for the admission-against-interest upgrade: a vendor
  stating a limit of its own product. Each upgrade must say why the
  statement is costly to the vendor.
- Acceptance: each entered with its page anchor and a verbatim-quote test;
  relations to the existing Dirac-3 assertions (for example
  `dirac3-per-loop-measurement-rules-out-quantum-advantage`) recorded.
- Depends on: none.

**F64. Staggered 12-month re-check, with revised-version detection and a re-pull list (~4h) Priority 40** (NEW 2026-10-09, team lead at Sprint 7 Manual Validation, Q12 = 1, Q15 = 2, Q16 = 1)
- Phase: Sourcing / currency
- Platform: `scripts/probe_reference_fields.py`, `store/probes.py`,
  `scripts/view.py`, Phase 1.3 of `docs/SPRINT_EXECUTION_WORKFLOW.md`,
  ADR-0005 (a new amendment)
- Team lead, 2026-10-09: a re-check "every 6-12 months (most do not change
  after first upload) and only a brief check to ensure the paper has not
  been replaced, withdrawn or updated. If updated, then we can re-pull the
  paper"; "we can't have it do 1,000+ papers in one sprint as we loaded all
  the current papers in the last month"; split them into 24 sections, the
  first about 10 months out, then 1/24th every 2 weeks, picked up by the
  next sprint that passes the date.
- Proposed process (presented 2026-10-09; the team lead approves it at
  Sprint 8 refinement):
  - Section: every record belongs to one of 24 half-month sections of the
    calendar year (1 = January 1-15, 2 = January 16-31, ... 24 = December
    16-31), computed from its id (a stable hash, mod 24). Computed, never
    stored; an id never changes, so the section never does. About 1/24 of
    the records fall in each.
  - Next re-check date: the first start of the record's section that is
    at least 10 months after its last check. Computed from the stored
    check date, never stored itself. For the papers checked in October
    2026 that gives mid-August 2027 to early August 2028, 1/24th every
    two weeks;
    after that, each record comes due once a year in its own section. A
    paper entered later falls into its section too, so a bulk load never
    bunches into one sprint.
  - Phase 1.3: re-check every record whose next re-check date is on or
    before the sprint's start. About 65 arXiv papers per section, one
    request each (the abstract page): about 20 minutes, well inside F52's
    cap. A sprint that spans two sections takes both.
  - The brief check: withdrawn; published with a DOI (replaced by the
    journal version); a newer arXiv version than the local copy (the page
    shows the latest version; the local PDF's first page carries a stamp
    such as "arXiv:2407.04512v4"); the link still opens.
  - Output: three lists for the team lead: newer version, to re-pull;
    withdrawn; newly published. Nothing is downloaded automatically.
  - `view.py paper <id>` shows the section and the next re-check date.
- Replaces `--stale` against the cycle start as the Phase 1.3 check:
  "stale" becomes "past its next re-check date".
- Acceptance: the section and the date computed and shown; Phase 1.3 picks
  up only due records; a bulk load spreads over the 24 sections (a test
  over synthetic ids); a revised version on a test record is reported for
  re-pull; ADR-0005 amended.
- Depends on: F52's cap (built).

**F65. Deep research into the Dirac-3S, QCi's upgraded Dirac-3 (~3h) Priority 30** (NEW 2026-10-10, team lead during Sprint 7 Phase 7; TARGET: Sprint 8)
- Phase: Content / platform research
- Platform: `D:\Data\Harold\EvidenceBasedDB\References\QCi-site\systems\Dirac_3S_Users_Guide_Rev_A-1.pdf`
  (outside the repository; "Dirac-3S User Guide, September 2026, Revision
  A", QCi-QMS-900-000001, 38 pp., created 2026-09-24, SHA-256
  0ddbc5339966a42ab67c44988d7a12a599724c462839ecc2848189f048af5971);
  the store's Dirac-3 assertions from F45; a script in the pattern of
  `scripts/sprint7_f45_dirac3_reading.py`
- Team lead, 2026-10-10: "Add to backlog and target NEXT sprint: deep
  research into the new Dirac-3S (upgraded Dirac-3 system)", with a list
  of further items. **The list did not arrive** (the message held a paste
  placeholder, not its text); it is added here when the team lead re-sends
  it, before Sprint 8 planning.
  - **Recovered 2026-10-13** from the team lead's own Claude Code input
    history (the paste was first made on 2026-10-10 in another project's
    session, with the same request, and only its placeholder was carried
    here). Its 11 lines are three links and one instruction, with blank
    lines between: the PR Newswire release "Quantum Computing Inc.
    Announces Dirac-3S Scaling to Nearly 10,000 Variables"
    (`https://www.prnewswire.com/news-releases/quantum-computing-inc-announces-dirac-3s-scaling-to-nearly-10-000-variables-302895913.html`);
    QCi's "Dirac-3S technical reference" learning module
    (`https://quantumcomputinginc.com/learn/module/dirac-3s-technical-reference`);
    QCi's Dirac-3 product page
    (`https://quantumcomputinginc.com/products/systems/dirac-3`); and "Do
    a deep dive on quantumcomputinginc.com for anything new since last
    scrape." The original request also said the research comes "before any
    further usage of Dirac-3 qpu seconds". Sprint 8 Task C read the guide
    only; none of the four items was answered in Sprint 8.
- Scope: read the guide in full and enter it as a source; for each
  Dirac-3 assertion from F45 (the variable ceiling, the 200-to-1 analog
  resolution, the 0-to-16 integer bound and the 949 / 954 level count,
  the summation constraint, the measurement loop), record whether the
  Dirac-3S guide confirms, changes or supersedes it, as a relation to the
  existing assertion, never an edit of it; new Dirac-3S claims as
  `vendor-self-claim` with page anchors; the team lead's listed items.
- Acceptance: the guide read in full (read row and SHA-256); every F45
  Dirac-3 assertion classed against the guide (confirmed, changed,
  superseded, or not addressed); every quote verified verbatim against the
  local copy by test; the team lead's items each answered or carded.
- Depends on: F63 (same QCi source family; can run in the same task).

### Carded during Sprint 8 (2026-10-10 onward)

**F67. F39 release for Sprint 8: add Haiku 5.5 and re-verify the tiers (~30m) Priority 10** (NEW 2026-10-10, team lead at Sprint 8 scope selection)
- Phase: Process (released copy of the permanent F39)
- Platform: `.claude/model_assignment_heuristics.json`,
  `docs/SPRINT_PLANNING.md` (team roles table),
  `tests/test_model_assignment_heuristics.py`; Anthropic's models page
- Team lead, 2026-10-10: "F39 as Haiku 5.5 was released and we will want
  to include in the list of models".
- **Facts at carding (snapshot as of 2026-10-10, models page)**: Claude
  Haiku 5.5, `claude-haiku-5-5`, "for high-volume, latency-sensitive tasks
  such as classification, extraction, and routing"; pricing "From $0.10 /
  input MTok, From $0.50 / output MTok" (Sonnet 5.5: $2 / $10); 1M context,
  128K output; retirement not sooner than 2027-10-07. The heuristics file's
  haiku tier still names Haiku 4.5 (retiring not before 2026-10-15), and the
  Developers role has been on Sonnet 5.5 since F59.
- Acceptance: F39's five release steps; the haiku tier names Haiku 5.5 with
  the date checked; the Developers role per the plan's decision; the test
  green on evidence.
- Depends on: nothing

**F68. The door misses two identifier forms: old-style arXiv ids and DOIs with parentheses (~1h) Priority 64** (NEW 2026-10-12, found in Sprint 8 Task F)
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

**F69. Enter the Cerezo NonArxiv paper, "Key questions for the quantum machine learner to ask themselves" (~20m) Priority 66** (NEW 2026-10-13, team lead at Sprint 8 Manual Validation, Q8 = 1; found in Sprint 8 Task E)
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

**F66. Make develop the default branch: a git-flow model with main as the release branch (~1h) Priority 20** (NEW 2026-10-10, team lead at Sprint 8 Phase 1.4; TARGET: Sprint 8)
- Phase: Process / repository
- Platform: GitHub repository settings (`gh repo edit`),
  `.github/workflows/ci.yml`, the sprint docs and scripts that name a
  branch
- Team lead, 2026-10-10: "add to backlog and target for next sprint -
  switch the default branch from main to develop". The model: develop is
  the GitHub default, where feature work is integrated, and feature and
  sprint branches open PRs into it; main is the release branch, changed
  only by a PR from develop to main that the team lead merges, and each
  release merge is tagged.
- **Facts at carding (snapshot as of 2026-10-10, read only)**: the default
  branch is `main`; `develop` and `main` both exist on origin; the one CI
  workflow runs on `pull_request` into `develop` only, so a release PR into
  `main` is not tested today; no `dependabot.yml`.
- The team lead's instructions, kept in their three phases:
  - Phase A, inspect and report, change nothing: the default branch;
    whether `develop` exists locally and on origin; commits on each side
    the other lacks (`git rev-list --count` both ways), and whether main's
    extra commits change any file (`git diff --stat <merge-base>
    origin/main`); open PRs and their bases; CI workflows and their
    triggers, noting any that start or stop running when the default
    changes; `dependabot.yml`'s `target-branch`, branch protection or
    rulesets (a 403 on a private free repository means none), CODEOWNERS;
    every branch name in scripts, hooks, docs and tests ("main", "master",
    "develop", "default branch", "--base", "origin/HEAD"), each classed as
    must change, fine as is, or history (records of past events are never
    edited). Findings as bullets, then a numbered list of proposed
    changes; stop for approval.
  - Phase B, approved changes only: create `develop` from main only if it
    is missing; if main has commits with real file changes that develop
    lacks, stop and ask (never merge main into develop without approval);
    `gh repo edit --default-branch develop`, then `git remote set-head
    origin -a`, verified with `gh repo view`; CI on `pull_request` into
    develop AND main, so release PRs are tested; Dependabot (if present)
    `target-branch: develop`; open PRs into main that are feature work are
    listed and retargeted only with approval (`gh pr edit N --base
    develop`); fix the "must change" hits and write down the release step:
    "PR develop -> main, merged by the owner, then tag the merge." Edits on
    a feature branch with a PR into develop; the suite runs before each
    commit; commit messages state no test results.
  - Phase C, verify and report: the default is develop (`gh repo view
    --json defaultBranchRef`); `gh pr create` with no `--base` targets
    develop; CI triggers include develop and main; a note that "Closes
    #N" now closes issues when a PR merges into develop, since GitHub
    reads the keyword only on PRs into the default branch. Report as
    bullets: what changed, what was left alone and why, any decision
    still open.
- Standing limits: no PR merged and no branch deleted by Claude; every
  decision a plain numbered list answered by one digit.
- Acceptance: Phase C's checks all pass; the release step written in the
  workflow docs; a test that fails if `ci.yml` stops triggering on either
  branch, proven by injection.
- Depends on: none. Best done first in the sprint: the sprint PR's base
  and its "Closes #N" behavior both follow the default.

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
