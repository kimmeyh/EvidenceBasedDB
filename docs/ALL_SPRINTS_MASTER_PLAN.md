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

## Last Completed Sprint

Sprint 6 is below; Sprint 5 follows it for continuity.

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

**Sprint 7** (branch `feature/20261006_Sprint_7`, cut 2026-10-06 at the
Sprint 6 carry-forward, after PR #54 merged to develop and PR #67 merged
develop to main). Phase 1 Backlog Refinement complete.

**Scope selected 2026-10-06 (team lead, DEFINED)**: F59, F58, F52, F53, F54,
F44, F45. Team lead's order: F59 first; F58; F52 and F53 together; F54;
F44 ("each download is approved - do this after 59, 58, 52 and 54, but
before 45"); F45. Plan: `docs/sprints/SPRINT_7_PLAN.md` (draft, awaiting
approval). Refinement Q2 (priority changes) is carried to the plan as Q9.

## Next Sprint Candidates

Refined 2026-09-27 after Sprint 5 (Sprint 6 Phase 1.2); Sprint 6's shipped
cards pruned BY HAND (Edit tool, card by card) at its Phase 7, 2026-10-05.
Shipped and pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint
2); F2 Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25,
F26, F27 (Sprint 4); F5, F28, F30, F31 (Sprint 5); F32-F38, F40-F43, F47
(Sprint 6; F35's 30 unlinked notes continue as F54, F41's CVQBoost part as
F51). F39 is permanent and stays. Closed without
implementation: F19, F29 (Sprint 5 scope selection, reasons under Sprint 5
in "Last Completed Sprint"). The superseded stubs F12 and F21-F24 were
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

**F59. F39 release for Sprint 7: re-verify the models and act on Haiku 4.5's retirement (~45m) Priority 10** (NEW 2026-10-06)
- Phase: Process
- Platform: as F39
- The second release of F39. Haiku 4.5's recorded retirement is "not
  sooner than 2026-10-15", inside Sprint 7, and the heuristics name Sonnet
  5.5 as its successor; this release re-reads the models page that day,
  records what changed, and moves the subagent tier if the retirement has
  happened or been rescheduled.
- The existing test fails on a tier past its retirement without a
  successor, so the release keeps it green with evidence, not by editing
  dates.
- Depends on: nothing; runs first in the sprint.

### Cyc and CVQBoost intake (proposed 2026-10-03)

Registered 2026-10-03 at the team lead's request from
`D:\Data\Harold\EvidenceBasedDB\Handoff-2026-10\ebdb-handoff\12-backlog-cards-proposed.md`,
prepared outside the repository; card text as drafted there. File names
`01` to `12` (`03-manifest-sources.json`, `07-assertion-candidates-pending.md`,
`11-decisions-2026-10-03.md`, and so on) refer to that folder;
`FACTS-WITH-CERTAINTY.md` is in its parent, `Handoff-2026-10\`. All
estimates are `[no-history]`. Priorities 26, 28 and 30 sprint together; so
do 40 and 42, and 60 and 62.

**F44. Download and intake the eight pending Cycorp papers (~90m) Priority 40**
- Phase: Sourcing / intake
- Platform: arXiv API for S16; hand-origin records for the rest
- The eight in `04-pending-sources.md`: T07 (FLAIRS 2007), R05 (2005), S16
  (arXiv:1603.04402), S19 (2019), M06 (2006), OV19 (Technology Overview,
  2019), PH20 (2020), L10 (AI Magazine 2010; look for a DOI first).
- Downloads need the team lead's approval (filename, source, size). Files go
  to `Papers\` under the naming convention, never into the repository.
- Enter at `seen`. The 2026-09-28 agent's reading is not a
  `checked_against_source` by this library's standard.
- Acceptance: eight records, each with a local `access` path and a SHA-256;
  T07 is read directly to settle "eight tactic types" (2007) against the six
  the 2009 code lists, and the "about a thousand HL modules" figure for
  `cyc-hl-module-count`.
- Depends on: F41 (section 15 sets the context rule for Cyc sources).

**F45. Dirac-3 reading pass: promote four sources and enter up to 11 facts (~2h) Priority 42**
- Phase: Sourcing / extraction
- Platform: N/A
- From `07-assertion-candidates-pending.md`: F-201 to F-206, F-208, F-209
  (the Dirac-3 User Guide v0.0.4 and arXiv:2407.04512), F-301 and F-302 (the
  two independent assessments), F-303 (a per-paper affiliation check).
- Each source is read directly, promoted with applicability, then yields its
  assertion: the Sprint 4 task H pattern. F-209: cross-check the 949-level
  figure in the hsbc hardware plan.
- Not in scope: F-207, an absence claim, which waits for the `claim_type`
  decision (F37 planning note).
- Acceptance: each promoted record names what was read and when; each
  assertion quotes its source verbatim; facts that duplicate an existing
  assertion become `supports` links instead.
- Depends on: F41.
- **Planning note, 2026-10-05 (Sprint 6 MV Q9 = 1)**: add the three QCi
  sources on Dirac-3's error behavior, all at `seen`:
  `huang-2025-noise-reversal-entropy-quantum-computing`,
  `qci-research-an-open-quantum-system-for-discrete-optimization`,
  `qci-lessons-entropy-quantum-computing-overview`. Record what they claim
  about noise and error correction as `vendor-self-claim`, beside the
  gate-model contrast (fault tolerance is a gate-model concept). F-207 is
  no longer blocked: `claim_type` exists, so it enters as `absence` with its
  search scope. The hsbc measurement is already in the store
  (`dirac3-matches-exact-optimum-on-convex-cvqboost`, with its limit
  `dirac3-fidelity-test-is-near-trivial-on-convex-formulation`).

**F46. Remaining reading pass: the other pending facts, split at selection (~large, no-history) Priority 80**
- Phase: Sourcing / extraction
- Platform: N/A
- The rest of `07`: World (8), entanglement (1), the April 2026 claim (4),
  classical fraud detection (7), ceiling estimation (9). Too large for one
  card; split by source group when a sprint selects it.
- Depends on: F45 (to calibrate the estimate from its actual).

### Store and process lessons from Cyc (proposed 2026-10-03)

**F48. Keep local source paths honest (~2h) Priority 60**
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

**F49. Prove the export keeps every context (~1h) Priority 62**
- Phase: Tooling
- Platform: `tests/`
- OpenCyc's 2012 OWL export dropped the microtheory of every fact: 19
  `definingMt` statements in 2,189,031. Cyc requires every assertion to sit
  in a microtheory, and nothing noticed the loss.
- Acceptance: a test that, for every record, the contexts in
  `store/evidence.db` equal the contexts in `export/`, in both directions;
  proven to fail by removing one context from a copy of the export.
- Depends on: none.
- **Planning note, 2026-10-06 (Sprint 7 Task B)**: largely moot under
  ADR-0004 A7 (Q1 = 2): there is no committed export to drop a context. What
  survives is the on-demand dump's round trip, which
  `test_the_live_store_round_trips_through_a_dump` already proves byte for
  byte. Recommend closing at the next refinement.

**F50. Qualify "compute, never store" with Cyc's stored counts (~30m) Priority 70**
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

**F52. Probe the computed fields for the bulk papers, under a per-session arXiv cap (~2h plus runtime) Priority 26** (NEW 2026-10-05, Sprint 6 MV Q6 = 1)
- Phase: Sourcing / computed fields
- Platform: `scripts/probe_reference_fields.py`, `store/citations.py`
- The 1,402 QMLPapers papers loaded by Sprint 6 Task J have no
  `publication_status`, `version_of`, `access_status` or affiliations probe.
  At 6 s per arXiv request that is about 1,400 requests and at least 2.5
  hours.
- Add a per-session arXiv request cap (a count, enforced by the shared
  pacer), so a run stops itself before arXiv throttles it; a stopped run
  resumes on the records still unprobed.
- Evidence for the cap: about 1,130 lookups in 3.5 hours ended in HTTP 429
  on 2026-10-03, with the intake pacing defect live; after the fix the
  number arXiv tolerates is unknown, so the first run measures it.
- Acceptance: every bulk paper probed or reported; the cap tested; no
  stored value from a run that got no answer.

**F53. Run the probes each delivery cycle and report stale ones (~1h) Priority 28** (NEW 2026-10-05, Sprint 6 MV Q7 = 1)
- Phase: Process / tooling
- Platform: `docs/SPRINT_EXECUTION_WORKFLOW.md` Phase 1.3,
  `scripts/probe_reference_fields.py`
- ADR-0005 A4's probe rule names this as not built: Phase 1.3 runs
  `refresh_citations.py` but not the probes, and nothing reports a probe
  older than one cycle.
- Acceptance: Phase 1.3 runs the probes (within F52's cap); a report lists
  every probe older than the last cycle; a test fails on a stale probe.

**F54. Recover the 30 repository notes that did not link (~1h) Priority 32** (NEW 2026-10-05, Sprint 6 MV Q8 = 1)
- Phase: Sourcing / repositories
- Platform: `scripts/link_code_repositories.py`, the GitHub API (token)
- Sprint 6 Task K reported 30 of 135 notes: 23 repositories return HTTP 404
  (most URLs were cut short by the note extractor: `zhihan-z/MCM_`,
  `dfki-ric-quantum/learning_`, `yikaimao/Q`), 6 are Zenodo, Gitee or
  malformed links, 1 belongs to the malformed `2108.0131`.
- Step 1: read the full URL from the paper's own text (the note quotes the
  sentence). Step 2, team lead 2026-10-05: "if still unfound, can you try to
  find the repo on github.com using the partial URL" (GitHub search by owner
  and name prefix). A match found by search is recorded as found by search,
  with the query, so the link's evidence says how it was found.
- Acceptance: each of the 30 linked with its evidence, or reported again
  with what was tried.
- Include `2108.0131`, malformed in `QMLPapers/2021/manifest.tsv` and the
  one refusal of the Sprint 6 bulk load: read the full id from the paper's
  own PDF in that folder, then enter it through the door (Sprint 6
  retrospective category 13).
- Carried from F35 (pruned at Sprint 6 Phase 7): `QMLPapers\Repos\REVIEW.md`
  holds 218 further candidates the extractor would not accept automatically;
  78 score >= 0 and are a real screening queue, 140 score < 0 and are mostly
  third-party dependencies (Qiskit, PennyLane), correctly held back. A later
  pass, or a slice of this card if a sprint selects it.

**F55. Record which papers cite which, as a computed link (~2h) Priority 34** (NEW 2026-10-05, Sprint 6 MV Q10 = 1)
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

**F56. Should corroboration raise an assertion's certainty, and how? (~1h decision, then build) Priority 36** (NEW 2026-10-05, team lead at Sprint 6 MV)
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

**F57. Read for claims: the records still at `seen` and `screened` (permanent, released in slices) Priority 38** (NEW 2026-10-05, team lead at Sprint 6 MV)
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

### Targeted for Sprint 7 (team lead, 2026-10-06)

**F58. Move the store, its backups and the export out of the repository (~3h, ADR first) Priority 8** (NEW 2026-10-06)
- Phase: Design / ADR, then migration
- Team lead, 2026-10-06, verbatim: "Add to backlog for next sprint - sqlite
  db needs to be stored off repository in D:\Data\Harold\EvidenceBasedDB\store
  and not in github any longer as it will quickly exceed space allowed by
  github. Database backups should similarly be moved to
  D:\Data\Harold\EvidenceBasedDB\store\backups and once they have bee moved
  then the .json files are no longer needed and can be removed from the
  repository. Noting that wether the chema.sql and ingest.py and
  restore_store.py should stay in the repo (likely) or move with the DB
  should be recommended by the coding agent team. Will need to include an
  amendment to ADR-0004 for these updates"
- **Facts at carding (snapshot as of 2026-10-06)**:
  - `store/evidence.db` (3.1 MB) and `store/backups/` (34 files, 46 MB) are
    already NOT in GitHub: `.gitignore` excludes `*.db` and `backups/`. They
    live in the working tree, so the move is from the repository FOLDER,
    not from GitHub.
  - What GitHub holds is the JSON export (`export/`, 2.7 MB: `papers.json`
    2.6 MB for 1,875 papers, about 1.4 KB per paper). The whole repository
    is about 7.7 MB of git objects; `papers.json` has changed in 30 commits.
  - GitHub's limits (docs.github.com, "About large files on GitHub", read
    2026-10-06): a warning above 50 MiB per file, a block above 100 MiB per
    file, and repositories "ideally less than 1 GB, and less than 5 GB is
    strongly recommended". At about 1.4 KB per paper, `papers.json` reaches
    50 MiB near 36,000 papers; every regeneration also adds a new version to
    the history.
  - `D:\Data\Harold\EvidenceBasedDB\store` does not exist yet.
- **Coding agent team recommendation (requested by the team lead)**:
  `schema.sql`, `ingest.py`, `restore_store.py`, `rebuild.py`, `backup.py`
  and every other script STAY in the repository: they are code, versioned
  and tested, and the door's rules live in them. Only DATA moves. The store
  path becomes one setting read in one place (`store.script_paths`), with
  the off-repository default and an environment override for tests and CI.
- **What removing the export changes, to decide at planning (Class 1)**:
  1. The export is today the reviewable record of the data (ADR-0004
     section 2: "the store is a build output; the export is the artifact").
     Without it, git holds no history of what the store said and when, and
     a data change has no diff to review.
  2. 12 test files read the committed export, including the byte-identity
     rebuild check that CI runs. They move to the off-repository export or
     to small committed fixtures; CI cannot reach `D:\`.
  3. Recovery then rests on the backups alone. Options: (a) keep a full
     export beside the store, off-repository, regenerated on every write;
     (b) also keep backups somewhere off this machine; (c) keep a small
     committed sample export for CI and review.
- Platform: `store/__init__.py` (`script_paths`), `store/backup.py`,
  `scripts/*.py` that write or read the store or the export, `.gitignore`,
  `tests/` (export-reading tests), `.github/workflows/ci.yml`; ADR-0004 (a
  dated amendment, required by the team lead); ADR-0005 section 3 and
  `CLAUDE.md` ("The two directories") also name these locations.
- Acceptance: the ADR-0004 amendment accepted before any move; the store
  and backups at the new paths with a verified backup taken before the move;
  every script and test passes with the new paths; the export's fate as
  decided; no data file left in the repository; `git rm` of `export/` only
  after the decided replacement exists and a rebuild from it is proven.
- Depends on: none. Run before F52, F57 or any other bulk load.

**F60. A mislabeled QMLPapers file: the "Asfaw 2108.0131" PDF is another paper (~30m) Priority 44** (NEW 2026-10-06, found in Sprint 7 Task E)
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

**F61. Mine the Massoli et al. survey's curated paper list for candidates (~2h plus runtime) Priority 46** (NEW 2026-10-06, team lead during Sprint 7)
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
