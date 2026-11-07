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
| 14 | docs/sprints/SPRINT_14_SUMMARY.md | [OK] Complete | 2026-10-29 to 2026-10-31 |
| 15 | docs/sprints/SPRINT_15_SUMMARY.md | [OK] Complete | 2026-11-01 to 2026-11-05 |

## Last Completed Sprint

Sprint 15 is below; Sprint 14 follows it for continuity.

### Sprint 15: Read Every Page, Figures and Images Included, Then Read 100 More Papers (2026-11-01 to 2026-11-05, PR #149, merged to develop and to main via PR #163 on 2026-11-05; tagged sprint-15)

Thirteen tasks, thirteen issues (#150-#162). **Tooling**: re-entry groups
for records left unread (F125); page anchors and latent defects (F126,
F127). **Reading**: OCR of image-only pages by RapidOCR (F115); figures
and embedded images read (F116); F114's 100 papers and the F57 release's
100 records read in full (F114, F133); F128's gaps read or put on the
hand-download list. **Corrections**: Phase 2's F151, F153, F154 re-read
(F124); 10 textbook LOW grades set HIGH by the team lead (F129).
**Inbound**: Phase 2's Sprint 30 results at 43bc362 (F130). The F95 and
F98 releases found nothing new (F131, F132). Store 2,345 -> 2,358 papers
(1,789 -> 1,805 `read`), 23,653 -> 34,891 assertions (8,167 -> 11,071
HIGH); suite 1,485 -> 1,543 tests. Manual Validation: 36 certainty
changes and Q2 to Q9 decided; a team-lead decision is now kept against a
later review or an older script's rerun. Retrospective: team lead all
"Very Good". Full detail: `docs/sprints/SPRINT_15_SUMMARY.md`.

### Sprint 14: Read PHI-OMEGA, Review the 302 Cloud Reads, Then Learn What the Store Says (2026-10-29 to 2026-10-31, PR #140, merged to develop and to main via PR #148 on 2026-10-31; tagged sprint-14)

Seven tasks, seven issues (#141-#147). **Papers**: Brighindi's PHI-OMEGA
paper, posts and code (F119); the F95 and F98 releases (F122, F123).
**Inbound**: Phase 2's Sprint 29 results (F120). **Full reads**: the 302
cloud results rebuilt and reviewed (F117) and F114's local reads, applied
as F114's first release (66 groups; 28 certainty settlements by the team
lead; 18 papers kept out). **Spike**: what the store says, for the fraud
challenge (F118, `docs/spikes/F118_WHAT_THE_STORE_SAYS.md`). Store 2,335
-> 2,345 papers (1,653 -> 1,789 `read`), 10,735 -> 23,653 assertions;
suite 1,424 -> 1,485 tests. Retrospective: team lead all "Very Good"; all
nine improvements option 1: Q1 to Q7 done in the sprint (among them the
applier renamed `scripts/full_read_apply.py` and 900 doubled periods
fixed), Q8 carded as F130, Q9 added to F128. Full detail:
`docs/sprints/SPRINT_14_SUMMARY.md`.

### Sprint 13: Fix Sprint 12's Two Defects, Check the Models, Then Read 800 Records (2026-10-24 to 2026-10-28, PR #131, merged to develop and to main via PR #139 on 2026-10-29; tagged sprint-13)

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

**Sprint 16** (branch `feature/20261105_Sprint_16`, cut 2026-11-05 at the
Sprint 15 carry-forward, after PR #149 merged to develop and PR #163 merged
develop to main).

- **Scope** (DEFINED, team lead 2026-11-05): F136, F134, F135, F137,
  F114 (20 papers this sprint, then 30 per sprint; F95 and F98 folded
  in; books excluded), F57, and the new F139 (reading efficiency,
  before F114's reads). F138 (books) carded on HOLD. F39 was not
  selected, so model assignments rest on Sprint 13's release (F111).
- **Fixed before selection by the team lead**: F136 is Sprint 16's first
  task (Sprint 15 retrospective Q1 = 1), and F57's next release reads two
  named papers first (the wangy8205165 white paper, then arXiv
  2108.13346), then follows the relevance ranking (Sprint 15 Manual
  Validation Q7 = 2). arXiv lists only v1 of 2108.13346 (checked
  2026-11-05), so "v2" is a plan question.
- **The team lead asked of F51**: "Does this still have to be on hold?"
  Answered as a plan question.
- **Plan**: `docs/sprints/SPRINT_16_PLAN.md` (drafted 2026-11-05, waiting
  for approval).

## Next Sprint Candidates

Refined 2026-11-05 after Sprint 15 (Sprint 16 Phase 1.2); Sprint 15's
shipped cards (F115, F116, F124, F125, F126, F127, F128, F129, F130 and
the released copies F131, F132 and F133) pruned BY HAND (Edit tool, card
by card) the same day. F114 stays: Sprint 15 read its second release and
892 of its records are still to read. Sprint 15's retrospective Category
13 became F136's widening (Q1 = 1, Sprint 16's first task); Category 14
was "none" (F136 and F137 were carded during the sprint).
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
and F105 (Sprint 12); F107, F108, F113 and the released copies F109 to
F112 (Sprint 13; F113's unread groups carried as F114); F117, F118, F119,
F120 and the released copies F122 and F123 (Sprint 14; F114's first
release shipped there, and the card stays for the rest); F115, F116,
F124 to F130 and the released copies F131 to F133 (Sprint 15). F121 (a spike
carded 2026-10-30) merged into F118 the same day, team lead: "Update
card F118 and sit this in sprint 14 after F117 completes". F39 and F57
are permanent and stay; F95 and F98 were permanent until 2026-11-05,
when the team lead folded both into F114. Closed without
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

**F39. Evaluate the available models and update the model-assignment heuristics -- PERMANENT (~30m per release) Priority 70** (NEW 2026-09-29; effort re-derived from Sprint 10's release at Sprint 11 Task B, F94)
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

### HOLD Items (waiting on an external event)

**F51. The CVQBoost findings record and its six assertions (~45m) Priority 50** (NEW 2026-10-03; released from HOLD 2026-11-05)
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
- Hold checked 2026-10-29 (Sprint 14 Phase 1.2): the `References\` and
  FourierWall2 copies still hash to `425358a7b4cec71f...`. Phase 2's
  Sprint 29 (read only, at 22d16c3) adds no re-run of the findings
  document. Stays HOLD.
- Hold checked 2026-11-01 (Sprint 15 Phase 1.2): the `References\` and
  FourierWall2 copies still hash to `425358a7b4cec71f...`. Stays HOLD.
- Hold checked 2026-11-05 (Sprint 16 Phase 1.2): both copies still hash
  to `425358a7b4cec71f...`. Stays HOLD.
- **Released from HOLD into Sprint 16** (team lead, 2026-11-05, Sprint 16
  plan Q4 = 1, after asking "Does this still have to be on hold?"). Phase
  2 cites the document as a planning reference only and holds no re-run
  of it, so the hold would not release. The record and its six
  assertions enter from the 2026-08-04 document, with Phase 2's F162
  result linked where it contradicts.
- Depends on: the hsbc repository's re-run of the experiment.

**F138. Read in full the books in the store and in the Books folder, with no reading budget (no estimate: as long as the reads take) Priority HOLD** (NEW 2026-11-05, team lead at Sprint 16 scope selection: "split out the reading of any books into a similar backlog items to F114 but for books and put it on HOLD")
- Phase: Sourcing / extraction (books)
- Value: this enables a book's claims to enter the store under a process
  sized for a book, without slowing F114's paper reads.
- Platform: the store; `D:\Data\Harold\EvidenceBasedDB\Books\` (44 PDFs
  on 2026-11-05, none named by a record's `access`); F114's reader
  prompt, review and applier.
- A book is a whole book or monograph (an ISBN, a whole-book DOI with no
  chapter suffix, or a monograph series such as Foundations and Trends) or
  a textbook. A thesis, a review article and a chapter in conference
  proceedings are papers and stay in F114 or F57.
- Candidates found on 2026-11-05 (snapshot as of that date):
  - From F114's ledger, not yet read in full (moved here by the team
    lead's Sprint 16 Q7 = 1, 2026-11-06: monographs are books):
    simeone-2022-introduction-quantum-machine-learning-engineers (229
    pages, read in part) and
    cichocki-2016-tensor-networks-dimensionality-reduction-large (176
    pages, no read row).
  - In F57 (no read row): freericks-2026-quantum-mechanics-done-right-book
    (Springer, its copy in `Books\`) and
    schuld-2018-supervised-learning-quantum-computers (Springer, no copy;
    also on F90).
  - Books already read in full: boyd-2004-convex-optimization and
    dawid-2025-modern-applications-machine-learning-quantum.
  - The `Books\` folder: 44 PDFs, most of them programming books outside
    the store's contexts; each is entered only if it bears on a context.
- On HOLD until the team lead releases it.
- Acceptance per release: each book read in full (every chapter and
  appendix) and applied, or given its reason; the counts before and after.
- Depends on: the team lead's release from HOLD

### Carded at Sprint 6 Manual Validation, 2026-10-05

**F57. Read for claims: the records still at `seen` and `screened`, each read in full (no estimate: as long as the reads take; permanent, no reading budget since 2026-10-25) Priority 90** (NEW 2026-10-05, team lead at Sprint 6 MV)
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
- **Sprint 16's release follows F57's relevance ranking** (team lead,
  2026-11-04, Sprint 15 Manual Validation Q7 = 2). Sprint 15's F133
  release read the next 100 ledger records with a local file instead,
  because no unread record outside the ledger had a local copy (Changed
  Commitment 9). So Sprint 16's release first fetches free copies of the
  ranking's top records (the paced fetcher; a paywalled one goes on the
  hand-download list), then reads them in ranking order.
- **Sprint 16's release reads one named paper first** (team lead,
  2026-11-05): the white paper `Quantum_NeuralNetwork.pdf` in
  `github.com/wangy8205165/Quantum-NeuralNetwork-WhitePaper`. Sprint 12
  (F103) entered that repository as a GitHub repository record only; the
  PDF in it has no paper record and no local copy (checked 2026-11-05).
  The release fetches it once into `Papers\`, enters it as a paper record
  whose access names the repository and file, links the repository
  record to it, and reads it in full before the ranking's records.
- **And a second named paper** (team lead, 2026-11-05: "unless already
  read ... get from arxiv for our purposes"): `qboost.pdf` in
  `github.com/wangy8205165/QuantumBoost`, which the team lead identified
  as arXiv 2108.13346 (given as "2108.133346"; 2108.13346 is "QBoost for
  regression problems: solving partial differential equations", Goes et
  al., 2021, checked on arXiv 2026-11-05). No local copy in `Papers\`, no
  manifest names it, and the store has no record of it (all checked
  2026-11-05), so it is not already read. The team lead: "only need to
  read v2 of the paper". arXiv lists only v1 (2021-08-30;
  `arxiv.org/abs/2108.13346v2` returns 404, checked 2026-11-05), so
  which copy is read is a Sprint 16 plan question. It is read in full
  after the white paper. This is not Neven et al.'s
  2012 QBoost paper, which has a local copy.
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
  - **Snapshot as of 2026-10-29** (Sprint 14 Phase 1.2): unchanged since
    Sprint 13's apply. 2,335 papers; 1,653 at `read`; 682 at `seen` or
    `screened` (681 and 1), of which 654 have no read row; 10,735
    assertions (4,059 HIGH). F114 holds the full reads still to do, and
    F117 the 302 cloud results waiting for review.
  - **Snapshot as of 2026-11-01** (Sprint 15 Phase 1.2; store unchanged
    since Sprint 14's last apply, counts from `SPRINT_14_SUMMARY.md`):
    2,345 papers; 1,789 at `read`; 524 at `seen` or `screened` with no
    read row; 23,653 assertions (8,167 HIGH). F114's 1,091 records not
    yet read in full overlap this count: a record read in part in Sprint
    13 has a read row and is F114's, not F57's.
  - **Snapshot as of 2026-11-05** (Sprint 16 Phase 1.2): 2,358 papers;
    1,836 with a read row; 522 with none; 34,891 assertions (11,071
    `high`, 97 `moderate`, 23,720 `low`). F114's 892 records not yet read
    in full overlap this count as before. arXiv 2108.13346 has no record
    in the store (id and title searched, 2026-11-05), so the release
    enters it new.
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
- Hold checked 2026-11-05 (Sprint 16 Phase 1.2): no file saved into
  `Papers\` since 2026-11-01 is unnamed, so none of the 8 has arrived.
  Stays HOLD.
- Depends on: the team lead's downloads

### Carded during Sprint 15 (2026-11-01)

**F134. Table cells that hold only a number are dropped from the text a quote is checked against (~30m) Priority 30** (NEW 2026-11-01, Sprint 15 Task H, reader g115)
- Phase: Reading (quote check)
- Value: a quote or a value number from a table cell is checked against
  the text the paper holds, not refused or passed by accident.
- Platform: `store/quotes.py` `plain()`, which drops each line that holds
  only a number so a quote may cross a page break (line 52 on
  2026-11-01).
- The non-layout text puts a table cell on its own line, so cells such
  as 881 and 160 are dropped with the page numbers. The layout text
  keeps them inside their row, so most table quotes still pass; a quote
  that runs across a number-only line in the non-layout text does not.
  The rule predates Sprint 15.
- Seen twice in Sprint 15's reads (2026-11-01): reader g115, and reader
  g120 on cumming-2022, whose Tables XIII, XV and XVI node counts and
  chain lengths could not be quoted; those values are held only in the
  figures list's `shows`.
- Acceptance: a page number is still dropped; a number-only table cell
  is kept, or the check finds it some other way; each with a test proven
  red, and the full live suite still green (every stored quote still
  verbatim).
- Depends on: none

**F135. A stated limit about a measured result meets the "measured is never HIGH" check (~20m) Priority 32** (NEW 2026-11-01, Sprint 15 Task H, reader g118)
- Phase: Reading (reader prompt and check)
- Value: a reader records a stated limit with its true result type
  instead of changing the type to clear a check.
- Platform: `scripts/sprint13_g_check.py`;
  `manifests/sprint15_f114_reads/READER_PROMPT.md`.
- Reader g118 set `result_type` to "theoretical", "claim" or "setup" on
  five stated-limit assertions (four in coopmans-2024, one in
  cortes-2026) because the check refuses a HIGH suggestion on a
  "measured" result. Each group's review judges these items, but the
  prompt does not say which type a stated limit on a measured result
  takes.
- Acceptance: the prompt names the type of a stated limit; the check
  and the prompt agree; a test proven red.
- Depends on: none

**F136. Each PDF's text is extracted once and each quote is checked once, ever (~50m) Priority 10** (NEW 2026-11-04, team lead at Sprint 15 Manual Validation, Q9: "We need to updat the rule as it violates the 'Long-term Effective, while as efficient as reasonalby possible' primary rule"; carded, not done now. Widened 2026-11-05; team lead retrospective Q1 = 1: Sprint 16's first task)
- Phase: Store tooling (apply)
- Value: a rerun or a second apply takes seconds, not minutes, and each
  write still carries a fresh quote check.
- Platform: `scripts/full_read_apply.py` (`verify`, `commit_apply`);
  the rule's wording in `docs/INTAKE_WORKFLOW.md`.
- The applier checks every quote of every assertion in every reviewed
  group (about 10,000 for Sprint 15's 47 groups) before it writes,
  although most are stored exactly as their review wants them and
  nothing is written for them. Sprint 15's apply of its last 24 groups
  (2026-11-04) re-checked the 23 groups applied that morning. The rule
  being kept: an assertion is written only after its quotes are checked
  against the source text (Sprint 10 retrospective I2,
  `store.ingest.insert_verified_assertion`). An unchanged row is not a
  write and needs no check.
- Not chosen (Q9 option 2): reusing a dry run's passing check for a
  new write through a stored receipt. That weakens the guarantee and is
  a Class 1 change to ADR-0004's evidence rule.
- Acceptance: the applier compares each assertion with its stored row
  first and checks only those it will insert or change; a second apply
  checks nothing and writes nothing; a changed quote is still checked
  (a test proven red); the rule's wording in INTAKE says "every write
  is checked; an unchanged row is not".
- **Widened 2026-11-05** (team lead): "This reading the PDF should ever
  be done once per PDF, ever, and once done should never need to read it
  again. The quotes only need to be verified once per PDF, ever, and
  should never need to be done again."
  - Text extraction (pdftotext, and OCR) runs once per file, ever. The
    text cache is keyed by the file's digest already; the gap is that a
    trial store copy without the cache extracts every PDF again (894 PDFs,
    about 25 minutes, Sprint 15). The cache gets one fixed location that
    every store copy reads, so no copy can miss it. This replaces
    retrospective improvement Q1 (copy the cache with each trial).
  - A quote is checked once, when it is first written. A rerun, a second
    apply or a later sprint never checks it again. A new or changed quote
    is checked once, against the cached text, in seconds.
  - Added acceptance: a trial on a store copy extracts no PDF the cache
    holds (a test proven red); a rerun of an apply checks no quote.
- Depends on: none

**F137. The two Dunjko records share one PDF: which paper is each (~30m) Priority 34** (NEW 2026-11-04, team lead at Sprint 15 Manual Validation, Q5 = 1)
- Phase: Reading (record repair)
- Value: each record points at its own paper, and each assertion sits
  under the paper that states it.
- Platform: the store; `D:\Data\Harold\EvidenceBasedDB\Papers\`.
- The Dunjko 2017 and 2018 records hold one byte-identical PDF. Reader
  g131 (Sprint 15) entered its new assertions under the 2017 record
  only (INTAKE_WORKFLOW.md section 64).
- **Found at Sprint 16 planning (2026-11-05)**: they are one paper.
  dunjko-2017 is arXiv 1709.02779 (one version, 2017-09-08);
  dunjko-2018 is DOI 10.1088/1361-6633/aab406, Reports on Progress in
  Physics 81(7), 2018-06-19, by the same authors with the same title
  plus "a review of recent progress" (Crossref). So no second paper is
  missing; the question is how the store holds a preprint and its
  journal version (Sprint 16 plan question). Team lead Q6 = 1
  (2026-11-06): one record. dunjko-2018 keeps the paper and adds the
  arXiv id; dunjko-2017's assertions move to it, each with a note; the
  2017 record is closed as a duplicate.
- Acceptance: each record's paper identified from its citation; the
  missing paper fetched by the paced fetcher if it is free (else on the
  hand-download list); assertions moved to the record that states them,
  each move with its note; the local-file check passes for both.
- Depends on: none

### Carded during Sprint 16 (2026-11-05)

**F139. Read once, check once, write once: each paper's read as efficient as it can be and still full (~120m [no-history] timebox) Priority 10** (NEW 2026-11-05, team lead at Sprint 16 scope selection: "need a way to optimize the reading - still very effective for the purpose of updating the database, but be as efficient as reasonably possible (total time per page, per paper), total token usage per paper, only test what must be tested, only test once, only read once, only write once, only update the database once, only red test once... Looking for the Coding Agent Team to fill in additional details and propose the backlog item. Assign to this sprint. Should be completed before running F114 this sprint so that the reading updates can be tested")
- Phase: Reading (pipeline)
- Value: this prevents time and tokens spent on repeated work (the same
  text extracted, the same quote checked, the same paper read, the same
  row written more than once), while each paper is still read in full.
- Platform: the reader and reviewer prompts
  (`manifests/sprint15_f114_reads/`), `scripts/sprint13_g_check.py`,
  `scripts/f117_review.py`, `scripts/full_read_apply.py`, `store/quotes.py`
  and its text cache, `scripts/run_suite.py`.
- **Measure first.** Per paper: pages, figures, reader and reviewer
  minutes, reader and reviewer tokens as each agent reports them, quote
  checks run, text-cache misses, store rows written and applies run. The
  pipeline writes these to one telemetry file per group; the summary's
  Actuals report them per page and per paper. A baseline comes from
  Sprint 15's progress files where they hold the figure, and is marked
  unknown where they do not.
- **Each "once", mapped to where it happens today** (Coding Agent Team,
  2026-11-05, from the Sprint 15 pipeline):
  - Extract once: the text cache, keyed by the file's SHA-256 (F136 makes
    one cache location for every store copy).
  - Check each quote once: today the reader's checker
    (`sprint13_g_check.py`), then the dry run, the trial apply and the
    live apply (`full_read_apply.py`) each check every quote, so a quote
    is checked about four times, and again on every rerun (the
    reviewer reads the passages but does not run the check). After: the checker checks a quote when the reader
    writes it, records the pass with the file's SHA-256 and the quote's
    hash, and later steps check only a quote that changed (F136 for the
    applier).
  - Read once: today the reader reads the whole paper and the reviewer
    reads it again with the source. Whether the reviewer keeps a second
    full read is the team lead's decision (Sprint 16 plan question): it
    is where most of a paper's second token cost sits, and Sprint 15
    sent a reviewer back for deciding from quotes alone.
  - Render once: each figure page is rendered to an image once per file
    and kept beside the text cache, not again by the reviewer.
  - Write once, update the database once: today a group can be written
    by the live apply, then the Manual Validation decisions script, then
    fix-up syncs. After: decisions are gathered before the apply where
    they can be, and one apply writes each row once; the trial on a store
    copy runs only when the applier itself changed since its last trial.
  - Test only what must be tested, once: `run_suite.py --changed` already
    picks the tests a change touches; the full suite runs only where the
    workflow names it (team lead, 2026-11-04). A store write that changes
    no code no longer triggers every `live_store` test, only those that
    read the rows written.
  - Red-test once: each new guard is proven red once, at the commit that
    adds it, and its docstring says how; it is not proven again later.
- **No loss of effectiveness**: every section, appendix, proof and figure
  is still read; every written quote still matches its source word for
  word; the review still finds what Sprint 15's found.
- Acceptance: the telemetry file for each of F114's Sprint 16 groups;
  each "once" above either in place with a test proven red, or named
  with the reason it is not; per-page and per-paper time and tokens for
  the 20 papers set beside Sprint 15's baseline in the summary; no read
  loses a section, figure or quote check.
- Depends on: F136 (extract once, check once in the applier)

**F140. Testing: risk-based, effective, and as fast as reasonably possible (~150m [no-history] timebox) Priority 10** (NEW 2026-11-06, team lead during Sprint 16 Phase 4: "Card for next sprint - improve the testing efficiency while being risk-based effective", with Phase 2's F180 as a reference, not to be copied; card approved as written the same day, Q1 = 1)
- Phase: Tooling and process
- Value: this prevents hours of local test time per sprint, and the
  gates that cannot run while a reader works, while every guard still
  catches what it was written to catch.
- Platform: every file under `tests/`, `scripts/run_suite.py` and its
  selection rules, the hooks, CI, and the sprint workflow's test points.
- Why, measured (every count a snapshot as of 2026-11-06):
  - The local full suite took 199 s warm in Sprint 12 (F100) and
    4,124 s (1:08:43, 1,578 tests) before Sprint 16's Manual
    Validation: about 20 times slower, cause not yet known.
  - CI's test job (`-m "not live_store"`, no store) takes 45 s.
  - `--changed` falls back to large sets: Sprint 16 Task A's change to
    `store/__init__.py` ran the full suite (1,550 tests); the Task F
    gate ran 82 files (1,097 tests, 45:49) because the store had changed.
  - Every reader check writes telemetry into the repository, so no gate
    could run while a reader worked (Sprint 16 Task F, INVALID verdicts).
  - The full suite before Manual Validation failed 1 of 1,578: an intake
    test pinned tier "seen", which the planned reads changed to "read".
- Scope:
  1. Inventory, generated by a script so it can be reproduced: per test
     file, what it guards; its kind (unit, guard, live-store data check,
     document check, hook check); its local time from
     `pytest --durations=0`; where it runs (`--changed`, full suite, CI);
     its proof record ("Proven red" docstring); and the last time it
     caught a real defect (git history, retrospectives).
  2. Why local is slow: per-test durations; store queries without an
     index; fixtures that open or hash the store per test instead of
     per session; pdftotext calls not served by F136's text cache;
     interpreter start; antivirus or the D: disk. Fix the top causes.
     Target: the full suite back under 10 minutes.
  3. Effectiveness: guards that cannot fail or duplicate another; tests
     that pin a value the planned work changes (they go red for a reason
     that is not a defect); defect classes found by reviews in Sprints 13
     to 16 that no test caught, and the cheapest test that would have.
  4. A risk tier per test file. Risk is likelihood times impact (ISTQB
     CTFL v4.0.1, section 5.2). High impact: a missed defect damages the
     store or a boundary (the appliers with their backup and second-apply
     checks, `store/merges.py`, the certainty grading and escalation in
     `f117_review.py`, provenance, and the sibling-write, commit-verdict
     and `--no-verify` hooks). High likelihood: code changed this sprint
     or changed often (Memon et al., ICSE-SEIP 2017). High-tier tests
     run on every gate; the others when their files change.
  5. Selection (test impact analysis): `--changed` made import-aware, not
     name-match only; last failures first (`--ff`) and new tests; the
     `store/__init__.py` fallback narrowed to its importers if the
     inventory shows that is safe. The full suite stays the backstop at
     its two fixed points.
  6. Store-data checks apart from code checks: a `live_store` test checks
     data, not code. Decide whether the store's checks run once after each
     apply, keyed by the store stamp `run_suite` already records, and not
     inside each code gate (extends F139's "a store write triggers only
     the tests that read the rows written"). Move telemetry writes out of
     the repository during a read, or out of the tree fingerprint, so a
     reader no longer blocks a gate.
  7. Red proofs: here a proof runs once, by hand, and its docstring
     records it (`test_guard_discipline.py`; F139's "red-test once").
     Decide when a proof is stale (its test, the guarded code or a shared
     fixture changed) and whether `--changed` names the stale proofs to
     repeat. Outside practice: mutation analysis on changed lines only
     (Petrovic and Ivankovic, ICSE-SEIP 2018).
  8. Which full runs, and where: the local full suite runs twice a sprint
     (Sprint 11 I2); CI runs the non-store set and cannot replace the
     local run, since it has no store. Measure whether a faster local run
     (part 2) plus store checks after each apply (part 6) makes the
     second full run unnecessary when the retrospective changes no code.
  9. Not applied: learned test selection (Machalica et al., ICSE-SEIP
     2019); this repository has too few test failures to train on.
     Recorded so it is not proposed again without that history.
- Deliverable: `docs/F140_TESTING_ANALYSIS.md` with the generated
  inventory, the findings, and recommendations that each state what they
  give up, each asked as its own numbered question. Taken recommendations
  land in the sprint if small, or as new cards.
- Acceptance: a test fails when a test file is missing from the
  inventory; every timing measured; the 20x cause named with its
  evidence; the full suite under 10 minutes, or the reason it is not;
  Sprint 16's gate timeline rebuilt from `sprint_status.json`, the
  verdict records and the commit times; target stated: an approved small
  change verified and committed in its development time plus about 15
  minutes.
- Depends on: nothing. Informs: F100's runner, Phases 4 to 7 of every
  sprint, F114's reads.

**F141. The paper view prints each assertion in full (~15m) Priority 40** (NEW 2026-11-06, team lead at Sprint 16 Manual Validation: "this seems to cut off the assertion(s), is there a way to get the full assertion?"; Q3 = 2, carded for Sprint 17)
- Phase: Tooling (the store viewer)
- Value: the team lead reads a paper's assertions in full from one
  command, without a PowerShell pipe over `--json`.
- Platform: `scripts/view.py`.
- Today `python scripts/view.py paper <id>` cuts each assertion to its
  first 100 characters (and each `contexts` line to 80). The full text is
  in `--json` and in `view.py assertion <id>`. Until this ships:
  `python scripts/view.py paper <id> --json | ConvertFrom-Json |
  Select-Object -ExpandProperty yields | Format-List id, certainty,
  value, provenance, citation_context`.
- Scope: a `--full` option on `paper` that prints each yielded
  assertion's id, certainty, full value, provenance and quotes; the
  default output unchanged.
- Acceptance: a test, proven red, that `--full` prints a value longer
  than 100 characters whole.
- Depends on: nothing.

### Carded during Sprint 13 (2026-10-26 to 2026-10-28)

**F114. Read in full the new papers (Papers folder, Christophe Pere's list) and the Task G ledger's papers, 30 per sprint, books excluded (no estimate: as long as the reads take) Priority 10** (NEW 2026-10-26, team lead at Sprint 13 Task G: "pause after the 5 current agents complete and backlog the remaining for the next sprint"; F95 and F98 folded in, 30 per sprint, books moved to F138, team lead 2026-11-05)
- **Changed 2026-11-05 (team lead, Sprint 16 scope selection)**: "combine
  F95 and F98 into F114 and default to 30 total papers per sprint (but
  only 20 for this sprint in order to test out the new reading updates)
  and update so that it no longer includes reading books". So:
  - **Size**: 30 papers per sprint by default, all sources together;
    Sprint 16 reads 20. A paper read here is not read again by F57.
  - **Order in each release**: (1) every PDF in `Papers\` (and its
    subfolders) that no record's `access` names, matched to a record by
    DOI or arXiv id first so a paper already stored is linked, not entered
    twice, then entered through the intake door (was F95); (2) every paper
    Christophe Pere's list (github.com/Christophe-pere/Roadmap-to-QML,
    GitHub REST, read only) added since the commit the last release
    recorded, matched the same way, with the new commit recorded (was F98);
    (3) the Task G ledger in ledger order. A paper that cannot be entered
    or read keeps its reason.
  - **Named papers and new list papers count inside the 30** (team lead,
    2026-11-05, Sprint 16 plan Q1 = 1 and Q2 = 2: "next sprint the will be
    included in F114"). A paper the team lead names for reading is read
    in F114's next release, after the list's new papers and before the
    ledger, not in F57's. Sprint 16's 20: the 6 new list papers, the 2
    named papers, then 12 from the ledger.
  - **The team lead's files** in `Papers\` are never renamed or moved.
  - **The hand-download list** (team lead, 2026-10-22: "Keep an on going
    list of these in relative priority order"): computed by
    `python scripts/hand_download_list.py`, never kept by hand, shown by
    the `hand-download-list` skill. A listed paper the team lead saves into
    `Papers\` is caught by step (1). 53 records on 2026-11-05.
  - **Books are excluded** and read under F138 instead. A book is a whole
    book or monograph (an ISBN, a whole-book DOI such as
    `10.1007/978-...` with no chapter suffix, or a monograph series such
    as Foundations and Trends) or a textbook. A thesis, a review article
    and a chapter in conference proceedings are papers.
  - **Last snapshots of F95 and F98 (2026-11-05)**: `Papers\` holds 386
    PDFs; 165 are named by no record's `access`, all Task G downloads that
    this card's ledger names; no unnamed file was saved after 2026-11-01.
    The list moved from ea6f42a7c0 to 399b022651 and adds 6 papers, none
    in the store: arXiv 2610.42029, 2611.00303, 2611.00272 and 2611.05079,
    and the Quantum journal papers q-2026-10-20-2239 and
    q-2026-10-29-2256. The F95 and F98 cards were removed on 2026-11-05;
    their histories are in git (last at 3a08106).
- Acceptance per release: every new PDF in `Papers\` and every new paper
  on the list linked, entered or given a reason, and the list's commit
  recorded; the release's papers read in full, reviewed and applied; a
  paper without a copy on the hand-download list with its reason; no book
  read; the counts before and after; a second apply writes nothing.
- Phase: Sourcing / extraction
- Value: finishes F113. **Snapshot as of 2026-10-26**: 287 groups, 1,430
  records, in `manifests/sprint13_g_ledger.json`, none read by a
  Sprint 13 reader.
- Platform: Sprint 13 Task G's (F113, pruned 2026-10-29 after its groups
  g001 to g042 shipped; its card is in git at 83b2e99):
  `manifests/sprint13_g_reads/READER_PROMPT.md` (with its "Progress and
  restart" section), up to 5 first-pass readers, the coordinator review
  of each group, and `scripts/full_read_apply.py` for the apply with
  its verified backup (it stops if a read row would be rewritten, unless
  `--update-reads` is named)
- What a full read is (carried from F113): every section, appendix and
  proof. Each theorem is entered with its statement and conditions
  quoted. No cap on assertions. Each record's stored assertions are given
  to its reader: each is confirmed, corrected, widened or narrowed from
  the whole paper, and new ones are added.
- The ledger's own acceptance (from 2026-10-26): for groups g043 to g329, every record with a copy read in
  full, its `paper_reads` row `full`, its assertions updated or added
  under the grading rules; every record without a copy listed with its
  reason and on the hand-download list; the counts before and after;
  each group's reader file and review committed under
  `manifests/sprint13_g_reads/` and `manifests/sprint13_g_reviews/`; a
  second apply writes nothing.
- Depends on: none now (F113's groups g001 to g042 were applied in Sprint
  13); the 302 results already fetched are F117's
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
- **Snapshot as of 2026-11-01** (Sprint 15 Phase 1.2, after F114's first
  release shipped in Sprint 14 with F117): of the 1,430 records in groups
  g043 to g329, 339 have a `full` read row dated 2026-10-26 or later;
  1,091 do not, in 227 groups. The 1,091 include the 18 papers the team
  lead kept out at Sprint 14 Manual Validation (Q2 = 1), the 8 records
  left unread in reviewed groups (F125), udaru-2025-qml-credit-risk (F115)
  and the records never sent. The cloud credit that ran Sprint 13's 302
  reads is spent; a release now runs on local readers (up to 5) unless
  the team lead funds the cloud path again. Sprint 14's local rate: 50
  papers inside a 744-minute sprint with review and apply.
- **Snapshot as of 2026-11-05** (Sprint 16 Phase 1.2, after Sprint 15's
  100 and F133's 100 from the ledger): of the 1,430 records, 538 have a
  `full` read row dated 2026-10-26 or later; 892 do not, in 190 groups.
  Sprint 15's local rate: 200 records (47 groups) read whole with
  figures and OCR pages, reviewed and applied in a sprint of about 5
  days.

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
