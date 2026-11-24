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
| 16 | docs/sprints/SPRINT_16_SUMMARY.md | [OK] Complete | 2026-11-05 to 2026-11-07 |
| 17 | docs/sprints/SPRINT_17_SUMMARY.md | [OK] Complete | 2026-11-07 to 2026-11-10 |
| 18 | docs/sprints/SPRINT_18_SUMMARY.md | [OK] Complete | 2026-11-13 to 2026-11-23 |

## Last Completed Sprint

Sprint 18 is below; Sprint 17 follows it for continuity.

### Sprint 18: The Agreement Map and the HIGH Audit, 30 Papers, and Safer Applies (2026-11-13 to 2026-11-23, PR #183, merge to develop pending the team lead)

Six tasks, six issues (#184-#189). **Apply**: one apply function that
writes only the fields a review decided (F147); the ledger names a new
group from the highest number (F149). **Audit and map** on Claude Code
subagents, no API spend (F146): every HIGH assertion with quotes checked
(12,524: 7,834 held, 4,672 held in part, 20 not held), and 490 pairs
screened (54 independent supports, 4 contradicts); nothing written to the
store. **Reading**: F114's 30 papers read in full and applied (2,688
assertions entered); qubit-lab.ch's Evidence page entered (F145); the
documents' counts printed from the store (F148). Store (snapshot
2026-11-22): 37,408 -> 40,112 assertions (11,754 -> 12,528 HIGH); 2,373
papers. Manual Validation: g361's two temperatures LOW (q7); q12's
upgrade rule applied with no qualifying pair; F150 to F154 carded; the
do-as-recommended rule. Retrospective: team lead all "Very Good"; i1
(agents write results with the Write tool only), i2 (the inventory keeps
its timings), F155 carded (i3). Full detail:
`docs/sprints/SPRINT_18_SUMMARY.md`.

### Sprint 17: Test Faster, Then Read on the API Credit (2026-11-07 to 2026-11-10, PR #174, merge to develop pending the team lead)

Six tasks, six issues (#175-#180). **Tooling**: the full suite from about
69 minutes to 7 to 11, with a test inventory and last failures first
(F140); reader telemetry out of the gate's tree id and the sign-off fixes
(F142); `view.py paper <id> --full` (F141). **Batch API**: the reader on
the Anthropic credit, dry run by default, the $95 cap and the 2026-11-18
stop (F144, PR #181); 13 papers for $3.00 (2026-11-07), nothing written
to the store. **Reading**: F114's 10 papers read in full and applied
(1,201 assertions entered or changed); the cost per page explained
(F143). Store (snapshot 2026-11-10): 36,209 -> 37,408 assertions (11,491
-> 11,754 HIGH); 2,369 papers. Manual Validation: one working folder
(q24), 8 assertions corrected (q23), 161 papers split into one-paper
groups (q20), the quotes-first reader rule (q28), the Albash and Pere
grades (q29, q31); F146 to F148 carded. Retrospective: team lead all
"Very Good"; the worktree hook (i1), two workflow lines (i2, i4); F149
carded. Full detail: `docs/sprints/SPRINT_17_SUMMARY.md`.

### Sprint 16: Read Once, Check Once, Write Once, Then Test It on 20 Papers (2026-11-05 to 2026-11-07, PR #164, merged to develop and to main via PR #173 on 2026-11-07; tagged sprint-16)

Eight tasks, eight issues (#165-#172). **Tooling**: each PDF's text
extracted once and each quote checked once (F136); each read measured,
with a telemetry file per group, and each "once" put in place (F139);
number-only table cells kept and a stated limit's type named (F134,
F135). **Store**: the two Dunjko records held as one (F137); the
CVQBoost findings record and its seven assertions (F51). **Reading**:
F114's 20 papers read in full (531 pages), including the 6 new papers
on Christophe Pere's list and F57's two named papers. Store (snapshot
2026-11-07): 34,897 -> 36,209 assertions (11,071 -> 11,491 HIGH); papers
at `read` 1,805 -> 1,813. Finding: the scripts' repeated work is gone,
but the agents' cost per page rose (F143). Manual Validation: the
`he-simulation-scope` split, the seventh CVQBoost assertion, F140 and
F141 carded. Retrospective: team lead all "Very Good"; F142 and F143
carded. Full detail: `docs/sprints/SPRINT_16_SUMMARY.md`.

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

**Sprint 18** (branch `feature/20261113_Sprint_18`, cut 2026-11-13 at the
Sprint 17 carry-forward, after PR #174 merged to develop and PR #182 merged
develop to main).

- **Scope** (team lead, 2026-11-18): F146, F114 (30 papers), F149, F147,
  F145, F148.
- **Plan**: `docs/sprints/SPRINT_18_PLAN.md`, approved 2026-11-20 (q1 = c,
  q2 = a, q3 = a). All six tasks done; Manual Validation complete
  (2026-11-23); retrospective done (`docs/sprints/SPRINT_18_RETROSPECTIVE.md`).

## Next Sprint Candidates

Refined 2026-11-13 after Sprint 17 (Sprint 18 Phase 1.2); Sprint 17's
shipped cards F140, F141, F142 and F143 pruned BY HAND (Edit tool, card by
card) the same day. F144 shipped too but stays as the record of the
Batch API reader's rules, which F146 depends on; it is pruned when F146
ships. F114 stays: Sprint 17 read 10 of its papers and split 161 more
into one-paper groups (q20). Sprint 17's retrospective Category 13 became
F149 (team lead, "i1. a i2. b i3. b i4. a").
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
F124 to F130 and the released copies F131 to F133 (Sprint 15); F51,
F134 to F137 and F139 (Sprint 16); F140 to F143 (Sprint 17). F121 (a spike
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
  - **Snapshot as of 2026-11-07** (Sprint 17 Phase 1.2): 2,367 papers
    (1,813 at `read`, 554 at `seen`); 1,845 with a read row; 522 with
    none (Sprint 16's 8 new papers entered with their reads); 36,209
    assertions (11,491 `high`, 97 `moderate`, 24,618 `low`). Sprint 16
    read F57's two named papers inside F114.
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
- **Snapshot as of 2026-11-07** (Sprint 17 Phase 1.2, after Sprint 16's
  20): of the 1,430 records, 550 have a `full` read row dated 2026-10-26
  or later; 880 do not, in 187 groups. Sprint 16's rate (telemetry):
  20 papers, 531 pages, 397 reader minutes and 129 reviewer minutes,
  read, reviewed and applied in about 2 days.
- **Snapshot as of 2026-11-13** (Sprint 18 Phase 1.2, after Sprint 17's
  10 and the q20 split): the ledger holds 1,676 records in 515 groups
  (298 not started, 171 applied, 33 superseded, 13 read but not
  applied); 792 have a `full` read row, 884 do not, in 326 groups
  (corrected 2026-11-18 at Sprint 18 planning: the first figures, 725
  and 951, counted only read rows dated 2026-10-26 or later, which drops
  the full reads of groups g001 to g042 made before that date). Step (1): `Papers\` holds 172 PDFs that no record's `access`
  names; 171 are ledger downloads, and 1 is new
  (`2023_Huang_Noise-Resilient-Single-Pixel-Compressive-Sensing-with-Single-Photon.pdf`,
  saved 2026-11-07; it is the stored record
  `huang-2023-noise-resilient-single-pixel-compressive`, at `seen`, so it
  is linked, not entered). Step (2): the list moved from 399b022651 to
  7113ded1df (2026-11-10) and adds 3 papers: arXiv 2611.08461,
  2611.10105 and 2611.08821. Sprint 17's rate: 10 papers read, reviewed
  and applied by local readers inside Tasks A to F.

### Carded during Sprint 17 (2026-11-07)

**F144. A Batch API reader on the $100 API credit: build it and pilot 5 papers (~240m [no-history] timebox) Priority 10** (NEW 2026-11-07, team lead at Sprint 17 Phase 1, before the slate: "add this as a backlog item - a special way to read several papers using the api token budget", with the full brief pasted; Q1 = 1 and Q2 = 1 decided in it)
- Phase: Reading (pipeline, metered)
- Value: this enables papers with no read row to be read in full on the
  team lead's $100 promotional API credit before it expires on
  2026-11-18, without local reader time, and with results the existing
  pipeline reviews and applies.
- Platform: the Anthropic Message Batches API (`claude-sonnet-5-5`), the
  `ANTHROPIC_API_KEY` environment variable; `manifests/sprint13_g_ledger.json`
  and its group builder, the brief builder, the reader prompts
  (`manifests/sprint16_f114_reads/READER_PROMPT.md` and Sprint 15's),
  `scripts/f114_cloud.py` (`paper_text`, briefs),
  `scripts/sprint13_g_check.py`, `scripts/full_read_apply.py`,
  `store/quotes.py`, `store/ocr.py`, `tests/test_reader_prompts.py`,
  `store/write_path.py`.
- **Facts given by the team lead (verified by them 2026-11-07; re-check
  on platform.claude.com, pricing and batch-processing pages, before
  building)**: the credit is $100 of promotional credit for the Agent SDK,
  API, Batch API, Playground and Managed Agents, not Claude Code; it
  expires 2026-11-18; no payment method is on file, so spending stops at
  $0. Batch prices are 50% of standard: Sonnet 5.5 at $1 per MTok input
  and $5 per MTok output. Most batches finish within 1 hour; results stay
  29 days. The `output-300k-2026-03-24` beta raises `max_tokens` to
  300,000 for batch requests on Sonnet 5.5 and Opus 5.5. No Batch API
  script exists in the repository (searched 2026-11-07). The team lead's
  forecast: $0.15 to $0.30 per paper (a forecast, not a limit).
- **Decided (team lead, 2026-11-07)**: Q1 = 1: Batch API, Sonnet 5.5,
  one request per paper, no tools. Q2 = 1: the records with no read row
  (522 on 2026-11-07), in F57's relevance-ranking order; a record with no
  local or free copy goes on the hand-download list, not into a batch.
- **Where results go**: in the repository, in the shape the pipeline
  already consumes (ledger groups, briefs, reader group files that
  `sprint13_g_check.py` checks), for a later sprint's coordinator review
  and `full_read_apply.py`. This work writes NOTHING to the store.
- **What to build**:
  1. Read the current pipeline first (the files under Platform).
  2. An API version of the reader prompt: change only what a no-tool
     request cannot do (no scripts, saved files, pushes or progress
     files); keep every page, no cap, every verdict and rule word for
     word; it passes `tests/test_reader_prompts.py`.
  3. A script (for example `scripts/batch_read.py`), dry run by default,
     that:
     - takes the next N records in ranking order and gives them ledger
       groups as earlier sprints did;
     - sends one request per paper with the reader prompt, the brief and
       the extracted text with its page markers; a page with no text
       layer or with figures gets its page image if that fits the
       pipeline, else is listed as not read with its reason;
     - sets `max_tokens` high (the 300k beta) so no read is cut short,
       never as a budget;
     - reads the key only from `ANTHROPIC_API_KEY`, never prints it, and
       never writes it to a file, log or commit;
     - saves each batch's id and state to a resumable state file outside
       git before it polls; never sends a record again once its result is
       saved;
     - when a batch ends, saves each raw result at once, writes each as a
       reader group file where the pipeline reads it, runs
       `sprint13_g_check.py` on it, and records pass or fail (a failing
       result is kept and flagged, never dropped);
     - records each request's input and output tokens from the API's
       usage, computes the cost from the pricing page, and prints the
       running total against $100;
     - refuses a batch whose estimated cost would take the total past a
       cap (default $95), and stops before 2026-11-18.
  4. Tests for the rules (no resend, the spend cap, no key in output,
     the result location), each proven red by injection; a CHANGELOG
     entry; an INTAKE_WORKFLOW.md section if a manifest is added.
- **Pilot**: on a new branch from the sprint branch, with a draft PR
  (never merged by Claude). 5 papers from the top of the ranking, then
  STOP and report as bullets: each paper's pages, tokens in and out, and
  cost; each check result and where its files are; the total spent; the
  measured cost per page and per paper, and how many more papers $100
  covers at that rate; anything the no-tool read lost (figures, OCR
  pages) against a local read.
- **After the pilot**: (a) a recommended batch size, small enough that
  each batch's results are saved and checked before the next goes, so a
  lost session loses at most one batch; (b) one short prompt the team
  lead pastes into a new session to run the next X papers in batches of
  that size, resume from the state file, and stop at the spend cap.
- Process: every decision question in the shape of
  `docs/SPRINT_RETROSPECTIVE.md`, "Presenting improvements, questions and
  decisions" (team lead, 2026-11-07; the card first said a numbered list
  with a "Recommend N" line); the requirement echoed back before more
  than one file is touched (CLAUDE.md).
- Acceptance: the API reader prompt passes `tests/test_reader_prompts.py`;
  the four rule tests exist, each proven red; 5 pilot papers sent, each
  result saved in the repository as a reader group file with its check
  result recorded; the spend recorded from the API's usage and under the
  cap; the store unchanged (its stamp before and after); the pilot report,
  the batch size and the paste-in prompt given to the team lead.
- Depends on: nothing. Time-bound: the credit expires 2026-11-18, so the
  build and the follow-on batches must run before then.

**F145. What qubit-lab.ch's Evidence pages teach about quantum computing, and about how to show evidence (~120m [no-history] timebox) Priority 20** (NEW 2026-11-07, team lead during Sprint 17 planning: "add to backlog for next sprint - what can we learn from this site: https://qubit-lab.ch/evidence#qmc-correlation-0 about Quantum Computing", with a screenshot of the page's menu)
- Phase: Sourcing / extraction (web source) and method review
- Value: this enables the store to hold a practitioner's published,
  pre-registered quantum results with their own verdicts and limits, and
  shows this repository and Phase 2 a way of presenting evidence that a
  reader can check.
- Platform: https://qubit-lab.ch/evidence (read only, the UA
  "EvidenceBasedDB-fetcher/1.0"); its public files only (for example
  `/evidence-runs.json` and the Zenodo design, DOI
  10.5281/zenodo.22498143); the intake door; the store.
- What the page holds (read 2026-11-07, a summary, not yet checked
  against the page): qubit-lab.ch, a Swiss firm offering PQC readiness
  and quantum prototyping for financial services, publishes "Evidence,
  not promises":
  - Six method studies (August to September 2026): "Which method" (QAOA
    concentration over 12,397 certified runs), "Noise & hardware" (a
    noise ladder ending on IBM ibm_kingston, Heron r2, 156 qubits,
    20,000 shots, unmitigated), "QSVM island", "VQC island", "Kernel
    atlas" and "VQC atlas".
  - Five sample runs: Quantum Monte Carlo, Portfolio, Collateral, Index
    replication and QML classification.
  - Its verdicts are mostly "Parity" or "No advantage demonstrated". The
    Monte Carlo run (simulator, model evaluations) shows amplitude
    estimation converging faster, with advantage not claimed. The
    correlation-0 follow-up (the link the team lead gave) reports the
    slopes unchanged and a crossover shift that does not exclude zero at
    200 and 400 repetitions.
  - It cites arXiv 2607.15815, "The Fourier Wall", already in the store
    as `mancilla-2026-fourier-wall-spectra` (read), for its
    classification method.
  - Several studies' raw results and scripts are "on request" or gated in
    a "Resource Room"; designs were tagged in a public repository before
    the runs.
- Scope:
  1. Read the public Evidence pages and public files in full; enter
     qubit-lab.ch as a source record (a vendor, with its conflict of
     interest named) and each study's and run's stated result as an
     assertion with its own limits, quotes checked. Gated or "on request"
     material is listed, not requested.
  2. Link each result to what the store already holds on the same
     question (QAOA, quantum kernels and VQC, amplitude estimation, The
     Fourier Wall, Phase 2's CVQBoost and SPECTRA results), as
     corroborating or contradicting where it bears.
  3. A short note on what this repository and Phase 2 could adopt from
     the presentation: the verdict vocabulary, pre-registration tags,
     certified run records in machine-readable form, and published
     corrections. Each adoption is asked as its own numbered question.
- Acceptance: the source and its assertions entered with quotes checked
  and certainty graded (a vendor's own result, single source); each link
  to existing assertions with its reason; the gated items listed; the
  note's proposals asked.
- Depends on: nothing. Target: Sprint 18 (team lead, "for next sprint").

**F146. The agreement map, then the HIGH audit, on the API credit before it expires (~240m [no-history] timebox) Priority 10** (NEW 2026-11-09, team lead at Sprint 17 Manual Validation, q26 = a: "What the API credit does in Sprint 18 - option a")
- Phase: Certainty (metered, Message Batches API)
- Value: this enables the store to say, for each assertion, which
  assertions from other papers support or contradict it, and to show
  that each HIGH value is held by its own quotes. Both are judged by a
  model, recorded with provenance, and decided by the team lead, never
  written to a grade by the script.
- Platform: the Anthropic Message Batches API, `ANTHROPIC_API_KEY` (read
  only from the environment, never printed or written);
  `scripts/batch_read.py`'s state, cap and stop rules; `store.grading`;
  the `assertion_relations` table (42 links as of 2026-11-09: 35
  supports, 7 contradicts).
- Facts (a snapshot as of 2026-11-09): 37,408 assertions; 11,753 HIGH.
  The team lead gives the credit as $97, expiring 2026-11-18; F144 had
  spent $3.00 of its $95 cap by 2026-11-07. Batch prices, from the
  claude-api skill's cache of 2026-11-03 (re-check on the pricing page
  before sending): Haiku 5.5 $0.05 / $0.25 per MTok in and out, Sonnet
  5.5 $1 / $5.
- Scope:
  1. The agreement map. Haiku 5.5 screens pairs of assertions from
     different papers that share a context and a topic. Sonnet 5.5 judges
     each pair the screen keeps: supports, contradicts or unrelated, with
     the quotes that decide it. Results are saved as proposals, outside
     the store.
  2. The HIGH audit. Sonnet 5.5 checks each HIGH value against its own
     quotes: held, held in part, or not held, with why.
  3. Both reuse F144's rules: dry run by default, a cost forecast and a
     worst case before each send, the cap (the credit left, less a
     margin), nothing sent on or after 2026-11-18, a saved result never
     sent again, a failing result kept and flagged.
- Asked of the team lead in Sprint 18, before anything is written to the
  store: whether "corroborated by an independent study" becomes an ADR
  basis for HIGH (ADR-0004 amendment), and which proposals are applied.
- Acceptance: both batches collected, the spend recorded per request,
  the proposals counted and sampled for the team lead, nothing written
  to the store without a decision, each rule tested and proven red.
- Depends on: F144 (its state file and rules). Before 2026-11-18.

**F147. One apply function that writes only the fields a review decided (~120m [no-history] timebox) Priority 20** (NEW 2026-11-09, team lead at Sprint 17 Manual Validation, q11 = a)
- Phase: Store integrity (prevention)
- Value: this enables every future applier to be safe by construction:
  a field no review decided cannot be written, so the defect never
  reaches the store.
- Platform: `store/ingest.py` (`sync_assertion`,
  `sync_verified_assertion`), `scripts/full_read_apply.py`
  (`decided_fields`), the sprint applier scripts.
- Evidence: an applier wrote an undecided field 4 times (4d969d9,
  ed5ab01, aabdd49, d740d72), each needing a fix and a re-apply.
- Scope: appliers write through one shared function that takes the
  review's decided fields and refuses any other field, naming it. The
  existing appliers move to it.
- Acceptance: an applier that tries an undecided field is refused, by a
  test proven red; the existing appliers pass through it unchanged.
- Already done (Sprint 17): the card-template line "lists every field
  this applier writes" in `docs/BACKLOG_REFINEMENT.md`.
- Depends on: nothing.

**F148. Counts in documents written from the store, never typed (~90m [no-history] timebox) Priority 20** (NEW 2026-11-09, team lead at Sprint 17 Manual Validation, q13 = a)
- Phase: Documentation integrity (prevention)
- Value: this enables a count in INTAKE_WORKFLOW.md or a sprint summary
  to be right when written, since a script prints it from the store with
  its date.
- Platform: a new `scripts/doc_counts.py`; `docs/INTAKE_WORKFLOW.md`;
  the sprint summaries.
- Evidence: 5 or more wrong counts (5e10948, bb82d0a, 80fcbb9, 6e4bfb7,
  6d5bcec, f1257c1).
- Scope: `scripts/doc_counts.py` prints, or writes into a dated block,
  the counts a document names (assertions, papers, HIGH and LOW by
  basis, group states). ADR amendments keep their dated snapshots, as
  CLAUDE.md requires.
- Acceptance: the generator's block in INTAKE_WORKFLOW.md and the next
  summary, a test that a block it wrote matches the store (live_store),
  proven red.
- Depends on: nothing.

**F149. The ledger script names a new group from the highest number, not the count (~15m) Priority 20** (NEW 2026-11-10, Sprint 17 retrospective Category 13, the Development Team, from the fresh-eyes review of the q20 split)
- Phase: Reading (pipeline)
- Value: this prevents a new ledger group from reusing an existing group's name when the ledger has a gap.
- Platform: `scripts/sprint13_g_ledger.py`; `manifests/sprint13_g_ledger.json`.
- `sprint13_g_ledger.py` names a new group `g{len(groups) + 1}`. Today the names g001 to g509 are contiguous, so the next is g510, which is right; one deleted or skipped name would make it reuse a name. `scripts/batch_read.py`'s `next_group` already uses the highest number plus one.
- Acceptance: the script names a new group from the highest number plus one, with a test on a ledger with a gap, proven red.
- Depends on: nothing. Target: the Sprint 18 plan.

### Carded during Sprint 18 (2026-11-21)

**F150. The full suite runs once per sprint, before the Manual Validation hand-over; after that, only the changed tests and CI (~30m) Priority 20** (NEW 2026-11-21, team lead at Sprint 18 Manual Validation: "all the other repositories have converted to only running the full suite once per sprint - once after development is complete and before the PR runs, prior to manual validation. At the end all that runs is a CI suite run. Have we adjusted to that and if not, can you write a sprint card for it")
- Phase: Process (testing)
- Value: this removes the second local full suite (about 6 minutes, and a
  wait before `gh pr ready`) and gives this repository the same test rule
  as spamfilter-multi and Phase 2.
- Platform: `docs/SPRINT_EXECUTION_WORKFLOW.md` (the "full suite runs
  twice per sprint" paragraph, line 78 on 2026-11-21);
  `docs/SPRINT_CHECKLIST.md` (Phase 5 and Phase 7); `scripts/run_suite.py`
  (module docstring, "the full suite runs twice a sprint", and
  `full_run_already_passed`'s docstring); the sprint plan's "Full suite"
  line (Sprint 12 to Sprint 18 plans copy it).
- **Not adjusted yet (checked 2026-11-21).** The rule here is Sprint 11
  retrospective I2 (team lead, 2026-10-23): twice, before the Manual
  Validation hand-over and after the retrospective's improvements. F140 q7
  (2026-11-07) only skips the second run when the tree and the store are
  unchanged. No test pins "twice".
- **How the other repositories adapted (read 2026-11-21):**
  - spamfilter-multi: the full suite runs ONCE, at Phase 5.2, through
    `scripts/run-full-suite.py` on an idle machine (Sprint 85 q6, F350
    R-6); per change, only the changed files' tests plus the high risk
    tier; "CI keeps the full suite". The origin is Sprint 64 IMP-6, team
    lead 2026-09-03: "this only needs to be done once per sprint, more of
    an integration test prior to manual validation as this kind of test is
    time and token expensive". One leftover there: its 7.7.1 step still
    says "analyzer + full suite green and push" after review fixes.
  - hsbc-qfraud-phase2: at the push of the retrospective's improvement
    commits, CI's full job starts (`gh workflow run ci.yml`), and after
    `gh pr ready` the completion claim waits for that job
    (`scripts/check_ci_status.py --wait --require-job full`;
    `docs/SPRINT_CHECKLIST.md` Phase 7, F177 / Sprint 31 D17). No second
    local full run.
- **The difference here:** CI runs `-m "not live_store"` only, because the
  store is not on CI. So "CI only at the end" would leave a store write
  made after the hand-over (a Manual Validation regrade or a retrospective
  apply) unchecked by CI. `run_suite.py --changed` already covers that: it
  adds every `live_store` test file when the store's stamp changed since
  the last passed run (Sprint 12 retrospective I1). So after the hand-over,
  each commit is gated by `--changed`, and the end of the sprint is CI on
  the PR.
- The change: the workflow paragraph, the checklist and the runner's
  docstrings say ONE full run per sprint, before the Manual Validation
  hand-over; every later commit (Manual Validation fixes, the
  retrospective's improvements) runs `python scripts/run_suite.py
  --changed`; `gh pr ready` waits for CI green on the PR. A change to a
  file every test depends on still makes `--changed` run the full suite,
  as now. `full_run_already_passed` (F140 q7) stays: it still stops a
  repeated full run on an unchanged tree.
- Acceptance: the three places state the same rule; a test fails if
  `docs/SPRINT_EXECUTION_WORKFLOW.md`, `docs/SPRINT_CHECKLIST.md` or
  `scripts/run_suite.py` says the full suite runs twice, or if the
  workflow stops naming `--changed` as the gate after the hand-over;
  proven red by injection; the next sprint plan's "Full suite" line says
  once.
- Depends on: nothing. Target: the Sprint 19 plan (team lead, q18 = b,
  2026-11-22); Sprint 18 keeps its second full run after the retrospective.

**F151. Every question, decision and improvement stored in full in one file per sprint, and re-asked from it in full (~60m [no-history] timebox) Priority 10** (NEW 2026-11-22, team lead at Sprint 18 Manual Validation: "Add to backlog for next sprint: please store all quesitons, decisions and Improvement in full. If you still need an answer to one and it has scrolled off the screen, always re-ask with the full contents every time (it is to hard to scroll back to find them).")
- Phase: Process (presentation)
- Value: this makes every open question findable in one file, and makes
  each re-ask an exact copy, so the team lead never scrolls back to find
  a question or its options.
- Platform: `docs/sprints/SPRINT_N_DECISIONS.md` (new, one per sprint);
  `docs/SPRINT_RETROSPECTIVE.md` ("Presenting improvements, questions and
  decisions (AUTHORITATIVE)"); `docs/SPRINT_EXECUTION_WORKFLOW.md`;
  `docs/SPRINT_CHECKLIST.md` (Phase 1.4, 3, 5.3, 7);
  `tests/test_sprint_documents.py`;
  `.claude/hooks/block_procedural_question_stop.py`; `CLAUDE.md` ("Don't
  point Harold back").
- **What exists today (2026-11-22).** CLAUDE.md and the memory file
  `feedback_represent_dont_reference.md` already say to re-present every
  open item in full. Nothing stores the items: a q is written only in a
  terminal message, so a re-ask is retyped from memory or from the
  transcript, and can drift (in Sprint 18 the hand-over was re-sent after
  the Stop hook blocked it, by copying from the transcript). Retrospective
  i items are written to `SPRINT_N_RETROSPECTIVE.md`; q items are written
  nowhere.
- **How Phase 2 does it (read 2026-11-22):** its workflow rule 11 (team
  lead, 2026-10-30, Sprint 29): "Every decision is written before it is
  asked", in full, to `docs/sprints/SPRINT_n_DECISIONS.md`, with a stable
  ID; "Re-ask by pasting the entry unchanged"; changed facts go in a dated
  "Changed since asked" note under the entry, and the original is never
  edited; the answer is recorded under each entry. Files exist for
  Sprints 29 to 34. Its retrospective maps a decision's options to an
  item's letters when one item is both.
- The change:
  - Every q and i is written in full, in the AUTHORITATIVE shape (title,
    What it is, What it prevents and/or catches, Prevention or control,
    Long-term value, Evidence, Extends, Effort, options a to z with pros
    and cons, one "(Recommendation)"), to
    `docs/sprints/SPRINT_N_DECISIONS.md` BEFORE it is shown. Retrospective
    i items go there too (the retrospective file links to them), so one
    file holds them all.
  - Each entry records when it was asked, then the answer verbatim with
    its date; facts that change after asking go in a dated "Changed since
    asked" note, never an edit of the original.
  - Every message that needs an answer re-shows EVERY open entry in full,
    pasted from the file, never a reference and never a summary.
  - The file's open entries are its single list: the Manual Validation
    hand-over and the retrospective read it to know what is still open.
- Acceptance:
  - A test fails when a DECISIONS entry lacks a field, has not exactly
    one "(Recommendation)", or reuses an ID; proven red by injection.
  - The Stop hook (`block_procedural_question_stop.py`) blocks a reply
    that asks a q or i which is not in the sprint's DECISIONS file, or
    that leaves out an open entry, or whose text differs from the stored
    entry; proven red by injection.
  - The four process docs and CLAUDE.md name the file and the
    paste-unchanged rule.
- Depends on: nothing. Target: the Sprint 19 plan (team lead: "for next
  sprint"). Sprint 18's q4 to q18 are re-asked in full in each message
  until answered, under the current rule.

**F152. Re-quote the 20 HIGH assertions whose quotes do not hold them, or grade each LOW (~60m) Priority 20** (NEW 2026-11-22, team lead at Sprint 18 Manual Validation, q10 = a)
- Phase: Reading (corrections)
- Value: this makes each of the 20 a HIGH its own quotes support, or a LOW
  that says why, instead of a HIGH known to be unsupported.
- Platform: F146's audit results (`D:\Data\Harold\EvidenceBasedDB\work\f146\audit\out\`,
  verdict "not held"); `docs/INTAKE_WORKFLOW.md` section 79 lists them (9
  are lemmas from one paper, run a034); `store.ingest.sync_decided_assertion`
  (F147); `store/quotes.py`.
- In each of the 20, the quotes hold only a lead-in, a title or a fragment.
  Each item is re-read in its paper: new quotes that hold the value are
  added (decided field: the quotes), or, where none can, the item is graded
  LOW with the reason (decided fields: certainty and its reason).
- Acceptance: all 20 decided, written through `sync_decided_assertion` with
  a verified backup; a second apply writes nothing; the F146 checker's
  audit, run again on the 20, gives "held" for every HIGH that remains.
- Depends on: nothing.

**F153. A sample triage of 100 "held in part" from the HIGH audit, to measure the real defect rate (~60m) Priority 30** (NEW 2026-11-22, Sprint 18 Manual Validation q11 = a, taken as recommended under the team lead's "just do as recommended"; confirmed by the team lead 2026-11-23, "q11. a")
- Phase: Reading (quality)
- Value: this tells whether the 4,672 "held in part" items are worth fixing
  one by one, before anyone spends days on them.
- Platform: F146's audit results; `scripts/f146_checks.py`.
- In each "held in part" item the value says something its quotes do not
  (a method name, a condition, a formula). The readers' strictness ran from
  about 50 to about 90 of each 200, so 4,672 is a list to review, not a
  defect rate.
- A random sample of 100 (seeded, so it can be drawn again), stratified by
  run so no one reader's strictness dominates, is classified by the
  coordinator: a real overstatement, wording only, or the reader was
  wrong. The rate, with its 95% interval, decides a next card or none.
- Acceptance: the sample, each item's class with its why, and the rate,
  recorded in `docs/INTAKE_WORKFLOW.md`; nothing written to the store.
- Depends on: nothing.

**F154. A semantic pair screen for the agreement map, measured against the 24 known relations before any run (~180m [no-history] timebox) Priority 30** (NEW 2026-11-22, team lead at Sprint 18 Manual Validation, q13 = a)
- Phase: Reading (cross-paper analysis)
- Value: this lets the map find agreement and conflict between papers that
  word the same finding differently, which the word-overlap screen cannot
  (recall 0 of 24 at every setting tried in Sprint 18).
- Platform: `scripts/f146_checks.py` (`screen`, `known_pairs`, `map`); a
  local embedding model (no API spend unless the team lead decides one);
  `D:\Data\Harold\EvidenceBasedDB\work\f146\`.
- The screen is chosen and tuned on recall against the store's 24 judged
  relations between papers BEFORE any map run, and its precision is
  sampled; the map runs only if recall is useful. Pairs the map judges
  "supports" with both sides independent and both resting on an experiment
  or a proof take the q12 rule (team lead, 2026-11-22): LOW to MODERATE,
  MODERATE to HIGH; every other pair changes nothing. That rule changes a
  grade for the first time only here (Sprint 18's 54 pairs gave none,
  `docs/INTAKE_WORKFLOW.md` section 81), so the card adds its grading path
  and a dated ADR-0004 amendment before any write.
- Acceptance: recall on the 24 recorded, with the setting chosen; if a map
  runs, its pairs checked by `f146_checks.py`, and any upgrade written
  through `sync_decided_assertion` with a verified backup.
- Depends on: nothing.

**F155. The read checker names an id another source already holds, and a near-miss id (~60m) Priority 20** (NEW 2026-11-23, Sprint 18 retrospective i3, applied under the team lead's do-as-recommended rule)
- Phase: Reading (F114 reads; F152 and F153 checks)
- Value: a reader's id that collides with another source's, or that is one
  character off a given id, is named by the reader's own check before
  review, instead of being found at review or by chance.
- Platform: `scripts/sprint13_g_check.py` (the local read checker, run by
  each reader); `scripts/f146_checks.py` (`problems`), read-only on the
  store.
- Sprint 18 evidence (`docs/INTAKE_WORKFLOW.md` section 78): five reader
  ids in g510 and g352 (`data-availability-on-request`, `review-scope`,
  `vqe-definition`, `qaoa-definition`, `schwinger-model-definition`) were
  already other sources' and were renamed after review. Audit runs a018
  and a030 each mistyped one given id; it was found only when the item was
  handed out again.
- The read checker reports a new assertion id already held by another
  source (in the store, or new in another group of the same release). The
  audit and map checkers name, for an answered id that was not given, the
  given id at an edit distance of 1.
- Acceptance: both checks proven red by injection; a Sprint 18 collision
  (g352's `vqe-definition`) reproduced against a copy of its group file.
- Depends on: nothing.

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
