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
| 5 | docs/sprints/SPRINT_5_SUMMARY.md | [OK] Complete, PR #43 awaiting merge | 2026-09-23 to 2026-09-25 |

## Last Completed Sprint

Sprint 5 is below; Sprint 4 follows it for continuity.

### Sprint 5: Make the Store Durable, Then Fill It (2026-09-23 to 2026-09-25, PR #43)

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
Sprint 4 carry-forward). Phase 1 Backlog Refinement complete.

**Scope selected 2026-09-23 (team lead, DEFINED)**: **F31** (new: download
and process the HSBC Phase 2 bibliography, then propose the fields it
shows the store is missing), **F30** (store durability), **F28** (learn
from the papers), **F5** (QCi deep-dive, with every find added to the
store through the existing intake path). Plan:
`docs/sprints/SPRINT_5_PLAN.md`.

**Closed 2026-09-23 without implementation (team lead):**
- **F19** (SPRINT_RESUME_GUIDE.md and a startup-check skill): "This is not
  necessary if the sprint execution docs are kept up-to-date. In other
  repositories using the same Sprint framework Coding Agents pick up where
  everything is left off very quickly by looking at github and reading a
  couple of documents. This can be closed."
- **F29** (cold-mode adjudication timing): "This is not needed and can be
  closed." F11's confirm-mode number (1.08 team-lead minutes per record)
  stands as the store's only adjudication measurement; the cold-mode
  number stays unmeasured by decision, not by omission.

**Manual Validation decisions, 2026-09-25 (team lead: "1. 2 2.1 3 1 4. 1
5. 2 6. add the row it rests on 7 2"):**
- Q1 = 2, then REVISED the same morning (team lead: "can you pull any of
  the papers from the authors IF they are related to QML, ML or the Zeno
  effect (can you screen the abstracts to determine)"): no looser name
  rule, but the unresolved hits were screened on their abstracts; 21 of
  392 entered, marked "authorship not confirmed" (research doc, "Q1
  revised"). Q8 = 2: the three weakest on authorship then removed; 18
  remain.
- Q9 = 1: Manual Validation complete; proceed to Phase 7.
- Q2 = 1: retention rule 3's "superseded" clause (a backup is covered once
  an export commit landed after it) accepted.
- Q3 = 1: the six pilot papers' `read` promotions on Claude's reading
  accepted as they stand (the Sprint 4 Task H practice); the three
  learnings stay "awaiting team-lead adjudication".
- Q4 = 1: an explicit assertion derivation marker carded as F37.
- Q5 = 2: the papers `[IN-2]` and `[CL-21]` meant are not added; the store
  holds what their ids point to.
- Q6: the table rows `cvqboost-vs-xgboost-auc-under-balancing` rests on
  added after the vendor's sentence, which is kept
  (`scripts/sprint5_cvqboost_quote_fix.py`).
- Q7 = 2: bulk `seen` dispositions keep "; not yet screened"; `set_tier()`
  removes it at every promotion (`tests/test_ingest.py`).

## Next Sprint Candidates

Refined 2026-09-23 after Sprint 4 (Sprint 5 Phase 1.2). Shipped and
pruned per convention: F1 (Sprint 1); F3, F4, F75, F76 (Sprint 2); F2
Phase 1, F6, F7-F10, F13, F14 (Sprint 3); F11, F15-F18, F20, F25, F26,
F27 (Sprint 4). The superseded stubs F12 and F21-F24 are removed now
that F25 has shipped -- their history lives in the Sprint 3 and 4 docs
and in git. Remaining items below, newly added ones marked. F19 and F29
were closed at Sprint 5 scope selection (see "Current sprint" above).
F5, F28, F30 and F31 shipped in Sprint 5 and are pruned (history in the
Sprint 5 docs and git).

### Bulk intake: targeted for Sprint 6 (team lead, 2026-09-23)

Added 2026-09-23 during Sprint 5 Phase 3 at the team lead's request, "Add
to backlog and target for next sprint". Card text is the team lead's;
lines marked **Planning note** are Claude's checks against the disk the
same day, and every count in them is a snapshot as of 2026-09-23.

**F32. Generate the bulk intake manifest from the QMLPapers manifest.tsv files (~90m) Priority 14**
- Phase: Sourcing / bulk intake
- Platform: N/A for tracked content -- reads `D:\Data\Harold\EvidenceBasedDB\QMLPapers\`
  (NOT this repository; ADR-0005 section 3), writes a manifest JSON under `export/`
- INTAKE_WORKFLOW section 9 already specifies this: the manifest is GENERATED
  from the twelve year `manifest.tsv` files, never authored by hand. Their
  columns are `file, arxiv_id, url, title` (about 1,450 rows). `arxiv_id`
  gives api-origin `access`; `title` is discarded because the door derives it
  from the API.
- Emits `context: qml` and the section 9 disposition wording verbatim:
  "Bulk intake 2026-MM from QMLPapers/<year>/manifest.tsv (a QML literature
  collection); not yet screened".
- Excludes the ids listed in F33 (withdrawn/retracted), so they are not
  loaded as ordinary sources.
- Acceptance: a dry run prints every derived record and exits non-zero on any
  row whose `arxiv_id` is absent or malformed; the generated manifest loads
  under `intake.py --manifest` without hand editing; row count reconciles
  against the twelve TSVs.
- This enables the ~1,410-record bulk load with no hand authoring.
- **Planning note (counts)**: 13 `manifest.tsv` files exist. Twelve carry
  `file, arxiv_id, url, title`: the 10 year folders (1,381 rows) plus
  `Reviews` (30) and `Workforce` (25), 1,436 rows in all. The thirteenth,
  `NonArxiv/manifest.tsv`, has `file, source_url, pdf_url, title` and 4
  rows; it has no `arxiv_id`, so a generator that reads every TSV must
  route it to the DOI or hand path (section 9) rather than fail on it.
  The 9 files Sprint 5 Task C ingests (F31, Q2) are already present by
  then and are skipped by derived id.
- **Planning note (output location)**: `export/` is the store's committed
  artifact (ADR-0004 section 2). `tests/test_export_currency.py` checks
  only its five named files, so a manifest there breaks no test, but it
  would place an intake INPUT among the store's OUTPUTS. A separate path
  (for example `manifests/`) keeps the two apart. Team lead's call at
  carding.

**F33. Ingest withdrawn and retracted status as first-class facts (~2h) Priority 16**
- Phase: Sourcing / bulk intake
- Platform: arXiv API `<arxiv:comment>` field; Springer article page for the retraction
- Seven papers in the bulk set changed status after publication and the store
  has nowhere to say so. A store whose purpose is provenance and derived
  certainty must not ingest a retracted source as an ordinary one.
- Six author-withdrawn, verified 2026-09-18 by `/abs` returning 200 while
  `/pdf` returns 404, reason read from `<arxiv:comment>`: `2308.08167`
  (superseded by `2405.13351`), `2304.05672` (duplicate upload, published as
  `2210.14450`), `2409.10932`, `2403.17444`, `2410.03853`, `2503.23408`.
- One retracted: Valdez & Melin 2022, `10.1007/s00500-022-07037-4`, retraction
  notice dated 10 March 2026 on the publisher page. No arXiv record exists,
  so the arXiv path cannot discover it.
- Two of the withdrawn name a superseding paper; the store should be able to
  carry that relation rather than lose it.
- Depends on: F34 (the ADR must say how status is represented before
  records are written)
- Acceptance: each of the seven carries its status, its source of truth, and
  its stated reason; a query can list them; the two superseding ids are linked.
- This prevents a retracted paper being cited as evidence without warning.
- **Planning note (order)**: this card is Priority 16 and depends on F34 at
  Priority 18, so priority order and dependency order disagree. Either F34
  moves ahead of it, or the sprint plan sequences F34 first regardless of
  priority.

**F34. ADR amendment: how the store represents a withdrawn or retracted source (~1h) Priority 18**
- Phase: Design / ADR
- Platform: N/A
- ADR-0004 and ADR-0005 define provenance and derived certainty but say
  nothing about a source whose status changed after publication. F33 cannot
  be written correctly until this is decided.
- Questions for the team lead (Class 1): is status a field on the record, a
  context, or a derived-certainty input? Does a retraction force certainty to
  a floor, or is it a named reason a human weighs? How is "superseded by
  <id>" represented -- an assertion relation, or a field?
- Note the asymmetry: arXiv withdrawal is discoverable from the API, journal
  retraction is not. The design should not assume the API can find it.
- Acceptance: the chosen representation is written into the ADR with its
  reasoning, and F33's acceptance criteria are restated against it.
- This enables the withdrawn/retracted ingest and prevents the same question
  being re-litigated per record.
- **Planning note**: Sprint 5 Task D proposes new per-reference fields from
  the HSBC bibliography (peer-review status, access status and similar) as
  card F36. Publication status is the same family of fact, so F34 and F36
  should be decided together in one amendment, not two.

**F35. Map the 135 verified repository notes to the GitHub intake path (~2h) Priority 20**
- Phase: Sourcing / bulk intake
- Platform: GitHub API (`store/citations.py` already carries `GITHUB_API` and
  a `_GITHUB` matcher)
- `QMLPapers\Repos\` holds 135 `_repo.md` notes, one per paper whose authors
  released code. Each names the repository, the owning paper's arXiv id, and
  quotes the sentence in the paper that announces the release.
- INTAKE_WORKFLOW section 9 is explicit that the note is local evidence, not
  the record: the repository takes the section 2 GitHub path and the note
  supplies the provenance for why it is attached to that paper.
- `REVIEW.md` holds 218 further candidates the extractor would not accept
  automatically. 78 score >= 0 and are a real work queue; 140 score < 0 and
  are mostly third-party dependencies (Qiskit, PennyLane) correctly held back.
  This item covers the 135 only; the 78 are a later screening pass.
- The extraction is heuristic and produced three rounds of corrected defects.
  Each note quotes its evidence sentence precisely so a wrong attachment is
  visible; spot-check before trusting the set.
- Depends on: F32 (the papers must exist as records before repositories
  attach)
- Acceptance: each of the 135 resolves to a live repository or is reported;
  every attachment carries the quoted evidence sentence; a wrong attachment
  is removable without touching the paper record.
- This enables "which papers ship runnable code" to be answered from the store.
- **Planning note (counts)**: 135 `_repo.md` notes confirmed on disk;
  `INTAKE_WORKFLOW.md` section 9 recorded 137 on 2026-09-19, so two were
  removed in between. `REVIEW.md` exists both at `QMLPapers\REVIEW.md` and
  `QMLPapers\Repos\REVIEW.md`; the card should name which one is the queue.
  GitHub's unauthenticated API allows 60 requests per hour, so 135
  lookups take over two hours unless the run authenticates.

### Proposed by Sprint 5 Task D (F31 part 3), 2026-09-24

**F36. Reference fields the HSBC Phase 2 bibliography shows the store is missing, and a back-fill for existing papers (~large, no-history) Priority 22**
- Phase: Design / ADR, then back-fill. Proposed 2026-09-24 by Sprint 5 Task D
  at the team lead's request ("note any additional fields or content you
  think we should keep for all references based on the content of
  BIBLIOGRAPHY.md ... Also include a way re-process existing papers to fill
  in the new fields and content"). **Decide together with F34**: publication
  status (withdrawn, retracted, superseded) is the same family of fact as
  field 3 below, and one ADR amendment should settle both.
- Platform: `store/schema.sql`, ADR-0005 section 2 (paper record fields) as
  a dated amendment, `store/ingest.py` (the door validates the new fields),
  `store/export.py`, a new back-fill script.
- **Method**: every per-entry element of `BIBLIOGRAPHY.md` (120 entries,
  preserved at `References/2026-09_HSBC-Phase2-research_BIBLIOGRAPHY.md`)
  was compared with what a paper record can hold today (`records` spine
  plus `paper_fields`, `paper_applicability`, `paper_yields`). Nine
  elements have no home (a tenth, the metadata provider, was added at the
  Sprint 5 retrospective). Each is classed by CLAUDE.md's rule --
  determinate facts are COMPUTED (a resolver), never stored -- because
  four of the nine are determinate and must not become stored copies.
- **The nine, with a recommendation each:**
  1. **How it was found** (`found_via`): the collection and locator, e.g.
     "HSBC Phase 2 bibliography [DQ-5]", "F5 author search (Nicholas
     Chancellor, network)", "QMLPapers/2024/manifest.tsv". Today it lives
     only in disposition prose, so "everything from collection X" is a text
     search. STORED (a fact about our process, not about the paper), as a
     child table so one paper can be found by two routes.
  2. **How much of it the reader read** (`read_extent`): the bibliography
     marks "Read in full (16pp)", "Abstract only", "read via arXiv HTML",
     "Appendices not extracted -- theorem statements read from HTML render".
     `checked_against_source` says WHO checked, at `read` only; nothing says
     how much. A claim read from an abstract and one read from Table 3 are
     not the same evidence. STORED, per reader and date: `full | partial:
     <what> | abstract | html-render | summary`.
  3. **Publication and review status** (`publication_status`): preprint,
     peer-reviewed at a venue, not peer reviewed (`[EX-4]` Zenodo), vendor
     document, blog, news, conference abstract (the `[IN-3]` ISMVL item).
     Plus F34's withdrawn, retracted, superseded. MOSTLY COMPUTED: arXiv
     `journal_ref`, DataCite `IsVersionOf`, Crossref `type` answer it for
     api-origin records; stored only for hand-origin ones, with an anchor.
  4. **Version of record** (`version_of`): the bibliography pairs arXiv ids
     with journal DOIs (`[EN-2]` Nature Communications, `[DS-2]` npj QI,
     `[DS-3]` APL Computational Physics, `[CL-5]` Mathematics, `[QC-1]`
     Communications Physics). COMPUTED from the registries (DataCite
     `IsVersionOf`, arXiv `doi`); never typed.
  5. **Access status** (`access_status`): paywalled (`[QF-10]`), HTTP 403
     to automation (`[EN-3]`, `[EN-4]`, `[QF-9]`), bot-challenge pages
     (Springer, Nature, Kaggle), a CDN link that "may rotate" (`[QC-2]`).
     COMPUTED by a probe, stored only as the probe's last result and date,
     so it can be re-run rather than trusted.
  6. **Links to code and data** (`source_links`): "Code:", "Software:",
     datasets (`[FW-3]`'s UCI ids, `[CL-20]`'s BAF suite). Sprint 5 Task C
     entered 10 repositories as their own records with nothing tying them to
     their papers; F35 needs exactly this link for 135 more. STORED as a
     typed relation between SOURCE records (`code-of`, `dataset-of`,
     `version-of`, `superseded-by`, `responds-to`), carrying the evidence
     sentence. Evidential support and contradiction stay between
     ASSERTIONS (ADR-0005 section 2b2); a critique (`[IC-1]` on `[QC-1]`)
     is recorded as `responds-to`, and what it refutes is extracted as
     assertions with `contradicts`.
  7. **Affiliation and conflict of interest** (`coi`): "All six authors at
     QCi", "Disclosed QCi shares/options" (`[QC-8]`), "HSBC-affiliated
     author" (`[QF-4]`), "Genuinely independent" (`[IC-2]`), vendor in-kind
     support (loke-2026). GRADE's risk-of-bias domain needs it, and today a
     certainty reason can only restate it in prose. Affiliations are
     COMPUTED where the registry carries them; a disclosed interest is
     STORED with its anchor (page, section).
  8. **How the source was cited** (`cited_as`): the bibliography cites 6
     entries differently from their registry -- `[IN-2]` and `[CL-21]` give
     titles of OTHER papers for their ids, `[EX-4]` a paraphrase, `[CE-20]`
     and `[QF-6]` a different year, `[IC-1]` a wrong initial. That is this
     store's founding defect class caught in a collection's own citations.
     STORED on the `found_via` row (how THAT route cited it), so a later
     comparison against the registry is a query, not a re-read.
  9. **Reading notes** (the `>` lines: "0 of 29 comparisons reached
     alpha=0.05", "Overclaim", "Does not transfer"): NOT a field. They are
     claims, and a claim enters as an assertion with provenance through
     extraction. Recommended: the extraction pass (F28's pilot shows the
     path) reads the preserved bibliography as a pointer to where to look,
     and each note becomes an assertion only once checked against the paper.
  10. **Which registry answered** (`metadata_provider`; added 2026-09-25,
     Sprint 5 retrospective improvement 8): arXiv refused 73 of 75 paced
     requests in Sprint 5 and DataCite answered, and the rendered citation
     differs slightly by provider (no journal_ref from DataCite). Today the
     provider is a phrase appended to `updated_reason` on 68 records
     ("metadata from DataCite"). STORED as a field, set by the door from
     `Metadata.extra["provider"]`, so a refresh can explain a DIFFERS; the
     back-fill reads the existing phrase.
- **Not recommended**: a topic field from the bibliography's 15 section
  names. Contexts already partition; a free topic list is "a tag wearing a
  costume" (ADR-0004 section 3b).
- **Re-processing existing papers** (`scripts/backfill_reference_fields.py`,
  dry run by default, one verified backup before `--apply` per F30):
  - COMPUTED fields (3, 4, 5, and affiliations in 7) are resolvers, so
    "back-fill" means running them once over every record and storing
    nothing but the probe dates -- the first run over the 48 seed papers
    doubles as their test;
  - `found_via` (1) is derived for every existing record from text the
    store already holds: the Sprint 1 seed-load note, the "Bulk intake ...
    [TAG]" dispositions, F5's "(<person>, <rule>)" dispositions;
  - `cited_as` (8) is filled for bibliography records from the preserved
    file, and for the seed set from `scripts/seed_set_metadata.json`'s
    history in git;
  - `read_extent` (2) and disclosed `coi` (7) are human-or-agent judgments;
    the script QUEUES them for the next screening pass and never guesses;
  - every write appends to `updated_reason`, never replaces it.
- Depends on: F34 (decide together), then this card's ADR-0005 amendment
  before any schema change (Class 1, ADR-first).

**F37. An explicit derivation marker on assertions (~small, no-history) Priority 24** (NEW 2026-09-25)
- Phase: Design / ADR. Carded at Sprint 5 Manual Validation (Q4 = 1) from
  the F28 pilot's finding 1 (`docs/LEARNING_SYNTHESIS.md` section 7).
- Platform: ADR-0004 section 3 (dated amendment), `store/schema.sql`,
  `store/ingest.py`, `scripts/learnings.py`.
- A learning is recognized today only by a provenance string beginning
  "synthesis of"; the pilot's first definition ("no paper yields it")
  wrongly caught a project assertion. Proposed: `derivation: extracted |
  synthesized | project` on every assertion, back-filled from existing
  provenance, with `learnings.py` reading the column instead of a string.
- Depends on: decide in the same ADR amendment as F34 and F36, so the
  assertion and paper fields change once.

**F38. Back-fill CHECKLIST-Phase2-pre.md for Sprints 1 to 4, with evidence per row (~small, no-history) Priority 12** (NEW 2026-09-25)
- Phase: Process. Found at Sprint 5's Phase 7 reconciliation: the Sprint 1
  rows were never checked off and Sprints 2 to 4 have no section, although
  each sprint closed with its docs triad. The file's own rule is "nothing
  here may be marked done without evidence", so the back-fill cites the
  commit or document for every row rather than recollection.
- Platform: `CHECKLIST-Phase2-pre.md`; the Sprint 1-4 PLAN and SUMMARY docs.
- Target: Sprint 6 Phase 1.2 (completeness sweep), where the reconciliation
  belongs.

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
