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

- **After each sprint (Phase 7.7 / 8.2)**: update "Last Completed Sprint"; add
  the sprint's row to "Past Sprint Summary" once its SUMMARY doc exists; prune
  shipped items from "Next Sprint Candidates"; add retro Category-14 items
  with new F#s.
- **During Sprint N+1 planning (Phase 3.2.1)**: create
  `docs/sprints/SPRINT_N_SUMMARY.md` for the just-finished sprint and link it
  here.
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

## Last Completed Sprint

**Sprint 2: Validate, Guard, and View the Store** (PR #11, open, awaiting
merge). Delivered Tasks A-E, G per `docs/sprints/SPRINT_2_PLAN.md`:
re-derived real paper applicability (Task A, corrected a Sprint 1
undercount), extracted and validated a real HSBC-submission assertion
(Task B), spot-checked store content against the 44 source PDFs and added
the QBoost paper (Task C), a vocabulary guard between ADR-0004/0005 (Task
D, F76), both ADRs' 20-paper checkpoints walked and recorded as dated
amendments (Task E, F75), and `scripts/view.py` (Task G, F3). Task F
(team-lead adjudication timing) was REPLACED mid-sprint by F7-F11 (Class 3
scope change, backlog). Also delivered: F12 and F13 added to the backlog,
`CLAUDE.md`'s explicit US-English statement, and three retrospective
improvements applied as commits (mechanical GitHub-issue-state check in
Phase 5, the `block_ask_user_question.py` hook, a data-precondition check
in `SPRINT_PLANNING.md`). Full detail: `docs/sprints/SPRINT_2_SUMMARY.md`;
retrospective: `docs/sprints/SPRINT_2_RETROSPECTIVE.md` (16 categories x 4
roles, all "Very Good"). Zero metered spend; this repository has none.

**The measurement Sprint 2 did NOT produce**: team-lead adjudication time
per record, ADR-0004's own named design constraint, deferred a second
time. Sprint 1 deferred it by team-lead decision; Sprint 2's own Task F
was scoped to produce it and was replaced instead by F7-F11 (backlog),
sequenced so F11 runs after F7-F10 complete in a future sprint.

## Current sprint

None. Sprint 3 has not yet been scoped -- this section is populated at
Phase 3 Kickoff once the team lead's selection from the candidates below
is recorded.

## Next Sprint Candidates

Populated 2026-09-15/16. F75/F76 carried verbatim from the consumer
repository's own backlog, both gated on this repository's own F77 work.
F1 (2026-09-15) shipped in Sprint 1 as Task H and is pruned per convention.
F2-F5 added 2026-09-16 at Sprint 1's Manual Validation.

**F2. Deep-dive spamfilter-multi for reusable process assets (~large, no-history) Priority 5**
- Phase: Process / tooling. Tentatively assigned Sprint 2 (team lead, 2026-09-16)
- Platform: N/A -- process, docs, and `.claude/` assets
- **This is a two-phase item, and the first phase is research/carding, not
  implementation.** Phase 1 (this card): survey `spamfilter-multi` (read-only,
  hook-enforced) across every named candidate area below, and for each
  candidate produce its OWN sprint card (or one shared card for a tightly
  related cluster) with a concrete rework plan and an estimate. Phase 2:
  execute the resulting cards in dependency order. This card's own
  acceptance criteria are Phase 1's only; Phase 2 is the cards it produces,
  not part of this card's own estimate.
- **Named candidate areas to survey** (team lead, 2026-09-16): `.claude/hooks`;
  memory files; `CLAUDE.md` structure and content; skills; sprint
  orchestration (the sprint execution doc set); sprint-card design;
  heuristics for model selection per sprint task; how that repository
  estimates sprint-task development time, with a view to implementing
  something similar here; `docs/architecture.md` and its ADRs; PowerShell
  scripts that could convert to Python and be used here (this repository
  already did one round of exactly this for its own inherited hooks, Sprint
  1 pre-kickoff -- the same method applies).
- **Standing constraint on every candidate, stated once here so each
  resulting card does not have to re-derive it**: `spamfilter-multi` builds a
  Windows and Android app in Flutter/Dart. Every candidate will need
  reworking for a Python/SQLite evidence database with no mobile
  deployment, no UI framework, and no app-store release cycle. A resulting
  card that ports content unmodified because it "looked generic enough" is
  a scope failure -- this is precisely the mistake Sprint 1 Task H spent a
  full task correcting for hsbc-quantum-fraud-2026's own inherited content,
  and the same discipline applies to anything pulled from spamfilter-multi.
- **Recommended execution method** (proposed, team lead to confirm or
  amend): (1) a single research pass (fork or fresh session) reads
  spamfilter-multi across all named areas and produces, PER AREA, a short
  finding: what exists there, what it is FOR in that repository's own
  terms, and a first-pass verdict on relevance (adopt / adopt-with-rework /
  not applicable) -- this is the "deep dive to analyze each candidate" the
  team lead asked for, done once, broadly, before any card is written; (2)
  from that pass, draft one sprint card per adopt-or-adopt-with-rework
  candidate (or one shared card for a tightly coupled cluster, e.g.
  "sprint-card design" and "model-selection heuristics" likely belong
  together since both shape how a card is written); (3) order the drafted
  cards by dependency -- CLAUDE.md/architecture-doc conventions likely gate
  anything that CITES them (a hook or skill that assumes a doc section
  which does not yet exist here); estimation heuristics likely gate
  "implement similar task estimation" as its own follow-on rather than the
  same card; (4) present the ordered card list at Sprint 2 refinement for
  selection, same as any other backlog slate -- Phase 2's execution is
  itself a normal sprint's worth of approved cards, not a single
  undifferentiated task.
- **Not this card's job**: deciding adopt/reject for any specific candidate.
  That is Phase 1's OUTPUT, reviewed by the team lead before Phase 2 starts.
- Depends on: nothing technical. Read access to spamfilter-multi already
  exists and is hook-enforced read-only (2026-09-15 standing rule).

**F3. Easy CLI-startable way to view DB content (~unknown, no-history) Priority 20**
- Phase: Tooling. Tentatively assigned Sprint 2 (team lead, 2026-09-16)
- Platform: this repository, `store/` and a new `scripts/` or `view/` entry point
- Team lead: view by context (title of every item in that context); view by
  paper (all data related to that paper); view by assertion (all applicable
  data). "Propose a viewing method, but needs to be easy and startable from
  CLI."
- **Proposed method** (for review at carding, not yet built): a single
  `python scripts/view.py <mode> [id]` entry point reading directly from
  `store/evidence.db` (read-only connection), three modes:
  - `view.py contexts` -- lists every context with a COUNT of records
    claiming it; `view.py contexts <context-id>` -- lists every record's id
    and one-line value/title filed under that context (via `record_contexts`
    plus, for papers, `paper_applicability`, per the F# item below about
    single-context papers undercounting true applicability)
  - `view.py paper <paper-id>` -- the full paper record plus every assertion
    it yields (via `paper_yields`), each with ITS full fields, not just ids
  - `view.py assertion <assertion-id>` -- the full assertion record plus its
    `supports`/`contradicts` relations resolved to the other assertion's
    value (not just the bare id), and which paper (if any) yields it
  - No server, no web UI: this is a `sqlite3`-backed read tool, output as
    plain text or `--json` for scripting, matching this repository's own
    "no speculative abstraction" standard (QUALITY_STANDARDS.md) -- a
    dashboard is not warranted at 45 records
- Depends on: the F# item below (single-context-per-paper undercounting) is
  a real gap this tool would otherwise silently inherit; resolve or at
  least document it before or alongside this card, not after, since a
  browsing tool that repeats the undercount is worse than no tool, per
  QUALITY_STANDARDS.md "verify the artifact you ship, not a proxy for it"

**F4. Validate the store against the HSBC submission and against the 44 source papers (~unknown, no-history) Priority 6**
- Phase: Validation. Tentatively assigned Sprint 2 (team lead, 2026-09-16)
- Platform: this repository's store/export, cross-referenced against
  `hsbc-quantum-fraud-2026` (read-only) and the seed-set PDFs
  (`D:\Data\Harold\EvidenceBasedDB\Papers`, read-only, never copied in)
- **Two related but distinct deep-dives, team lead 2026-09-16**: (1) does
  what this store holds match what the HSBC submission itself determined
  -- the assertions, figures, and claims the consumer repository's own
  documents already settled; (2) does the store's content of the 44 loaded
  papers accurately represent what those papers actually say, checked
  against the source PDFs directly, not against a prior extraction pass's
  own notes
- **Known gap this card should examine and correct, surfaced at Sprint 1
  Manual Validation**: every paper record in the current export has exactly
  ONE `context`, even though ADR-0005 section 2 defines `context` (seen-tier,
  singular) and `applicability` (screened-tier, PLURAL, "context ids it
  bears on") as deliberately separate fields, and `paper_applicability`
  exists in the schema as a many-to-many table that Task F never populated
  for any of the 44 seed-set papers. A paper genuinely spanning two contexts
  (e.g. the SMU CVQBoosting paper, `qml` and `platform:dirac-3` both) is
  findable under only whichever single context was chosen, undercounting
  every cross-context query. Fix as part of this card's accuracy pass, not
  as a separate item, since correcting it requires re-reading each paper
  against its actual content anyway
- **Second known judgment call to revisit**: `dwave-2023-operational-
  excellence-ebook` was recorded as a normal (low-priority) paper record;
  `freericks-2026-...-book` was excluded as a class mismatch. Both are
  book-shaped vendor/academic content; confirm during this deep-dive
  whether the D-Wave ebook should be reclassified to match
- Depends on: F77 (Sprint 1, complete)

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
  the "volume without judgement" risk ADR-0005 section 2c warns is MORE
  dangerous than fewer, reviewed records.
- Depends on: nothing technical. Read-only web access and the existing
  seed-set metadata are both already available.

**F6. Address the six remaining PR #1 code-review findings (~unknown, no-history) Priority 9**
- Phase: Tooling / robustness. Surfaced by the Claude code-review agent on
  PR #1, 2026-09-16; the two most contained findings and both Copilot
  findings were fixed directly on the PR (commit 7d7f6c1). These six are
  each a moderate-scope design or refactor question, not a quick fix
- **1. Redundant citation storage**: `insert_paper()` writes the same
  citation string into both `records.provenance` and `paper_fields.
  citation`. CLAUDE.md's own standing rule warns against exactly this
  ("determinate facts are COMPUTED, never stored... one value restated in
  five documents drifted in three of them"). Needs a decision on which
  field is canonical and whether the other should be a resolver
- **2. Tier/checked_against_source not enforced**: `store/schema.sql`'s own
  comment documents that `checked_against_source` is REQUIRED at
  tier='read', enforced "at the application layer" -- but no application-
  layer check exists. `insert_paper()` accepts any tier/checked_against_
  source combination unchecked. Needs a `validate_paper()` or equivalent
- **3. No per-record transaction boundaries during bulk ingestion**: both
  ingestion scripts commit once after their whole loop. A mid-loop FK
  violation aborts the run with an unhandled traceback naming no offending
  record. Needs per-record savepoints or at least per-record error context
- **4. Export N+1 queries**: `store/export.py` issues 2-5 additional
  SELECTs per record instead of batching one query per related table
  across the whole class. Real, but explicitly a performance concern at a
  scale (hundreds of records) this repository has not reached yet (45
  records currently) -- lowest priority of the six, premature to fix now
- **5. Duplicated path-resolution boilerplate**: `ROOT`/`DB_PATH`/
  `EXPORT_DIR` resolution, the `DB_PATH.exists()` precondition, and the
  record-existence check are copy-pasted near-identically across
  `ingest_seed_set.py`, `ingest_lenat_marcus.py`, and `regenerate_
  export.py`. A fourth ingestion script (F5's QCi deep-dive is already on
  the backlog) will paste this a fourth time without a shared helper
- **6. Duplicated export-function shape**: `_export_assertion`,
  `_export_acronym`, `_export_term`, `_export_paper` in `store/export.py`
  each repeat the same "query one row, copy non-null columns one by one,
  query 0-3 child tables, attach if non-empty" shape. A small `_copy_
  nonnull()`/`_child_list()` helper would collapse the duplication
- **Also flagged but likely skip, not a card**: `.claude/hooks/block_
  branch_from_develop.py` and its three siblings each define an identical
  `_read_command()` helper verbatim. Real duplication, but these are
  security-relevant hook files; a shared-helper refactor there should wait
  for F2's spamfilter-multi hook research rather than be rushed alone
- Depends on: nothing technical. Findings 1 and 5 likely belong together
  (both touch every ingestion call site); triage order at Sprint 2
  refinement

**F7. Adversarial record-adjudication review by Haiku (~unknown, no-history) Priority 11**
- Phase: Research / adjudication substitution. Surfaced Sprint 2 mid-Task F
  (team lead, 2026-09-17): replace team-lead adjudication timing with
  model-based adversarial review confirmations, one card per model tier,
  each designed for that specific model rather than a generic template
  with a name swapped
- **What this reviewer is FOR**: Haiku is this project's own documented
  "Developer" tier (SPRINT_PLANNING.md) -- fast, cheap, used today for
  bulk/mechanical subagent work. As an adjudication reviewer, its
  distinguishing risk is NOT missing subtle context, it is being too
  agreeable/fast and confirming a record without actually re-deriving
  the claim from the source. Its review protocol must therefore force
  verification rather than reward speed: require it to quote the exact
  source sentence supporting each field it confirms (not paraphrase),
  and reject a "looks right" confirmation with no quoted anchor
- **Review task**: given one paper/assertion record and its cited source
  (PDF path or provenance pointer), confirm or reject: citation accuracy
  (author/title/venue), the primary context, and (if present) each
  applicability entry's rationale -- EACH confirmation must be
  accompanied by a directly quoted source fragment, not a summary
  judgement
- **What would make this reviewer's output untrustworthy, name it now**:
  a review that confirms every field with no quoted evidence, or that
  quotes the SAME generic sentence for multiple different fields
  (a sign of pattern-matching rather than reading)
- Depends on: the ~18-20 screened-tier records Task F was going to review
  manually; this card's output is compared against F8-F10's for
  inter-model agreement, not accepted alone

**F8. Adversarial record-adjudication review by Sonnet (~unknown, no-history) Priority 12**
- Phase: Research / adjudication substitution. Same origin as F7
- **What this reviewer is FOR**: Sonnet is this project's own documented
  "Senior Developer" tier -- the workhorse model actually doing most of
  this sprint's own implementation work. As a reviewer, its risk is
  neither Haiku's over-agreeableness nor Fable/Opus's expected rigor: it
  is MOST likely to correctly flag genuine errors but under-flag subtle
  scope/certainty misjudgments (e.g. a `certainty: high` that a stricter
  reviewer would downgrade for a reason the schema's own `certainty_
  reasons` field should have named but didn't)
- **Review task**: same fields as F7 (citation, context, applicability),
  PLUS certainty/certainty_reasons/fidelity where present -- explicitly
  check whether the STATED reasons actually justify the level chosen
  (ADR-0004 section 3's GRADE-style model), not just whether a reasons
  field is non-empty
- **What would make this reviewer's output untrustworthy, name it now**:
  agreeing with every existing certainty level without ever proposing a
  different one -- a reviewer that never disagrees is not reviewing
- Depends on: same record set as F7; designed to run independently, not
  sequentially after F7 (so neither anchors the other's judgement)

**F9. Adversarial record-adjudication review by Opus (~unknown, no-history) Priority 13**
- Phase: Research / adjudication substitution. Same origin as F7
- **What this reviewer is FOR**: Opus is this project's own documented
  top tier (alongside Fable), mandatory today for ADR-spine decisions,
  retrospectives, and security-sensitive review. As an adjudication
  reviewer its expected strength is catching cross-record inconsistency
  (a context or certainty level that is locally defensible but
  contradicts how a similar record elsewhere was adjudicated) rather
  than single-record correctness, which F7/F8 already cover
- **Review task**: given the FULL set of records under review (not one
  at a time), find pairs or groups where the SAME kind of judgement call
  was made differently -- two papers with structurally similar
  applicability that got different certainty treatment, two assertions
  from comparable sources with different fidelity levels -- and state
  the inconsistency explicitly, citing both record ids
- **What would make this reviewer's output untrustworthy, name it now**:
  finding zero inconsistencies across ~20 records adjudicated by
  different processes (Task F/A/B/C ran at different times, by
  different means) -- zero found here reads as not having actually
  cross-compared, not as the records being perfectly consistent
- Depends on: F7 and F8's findings should be available as input (Opus
  reviews the SET, informed by what per-record review already surfaced),
  making this the last of the three peer reviews to run, before F10

**F10. Adversarial record-adjudication review by Fable (~unknown, no-history) Priority 14**
- Phase: Research / adjudication substitution. Same origin as F7
- **What this reviewer is FOR**: Fable is this project's own documented
  preferred top tier / Lead Developer role. As the final reviewer in the
  sequence, its distinguishing job is not first-pass review (F7/F8
  already did that) or cross-record consistency (F9 already did that) --
  it is adjudicating DISAGREEMENTS the other three produced, the actual
  decision a team lead would have to make when reviewers disagree
- **Review task**: given F7, F8, and F9's findings together, for every
  point where two or more reviewers disagreed (a confirmed field one
  flagged and another didn't; an inconsistency F9 found that F7/F8's
  per-record review missed or contradicted), make the actual call --
  which reviewer was right, and why, citing the source directly rather
  than deferring to reviewer consensus alone
- **What would make this reviewer's output untrustworthy, name it now**:
  resolving every disagreement in favour of whichever reviewer flagged
  MORE issues (favouring strictness as a proxy for correctness) rather
  than checking each disagreement against the actual source
- Depends on: F7, F8, F9 all complete. This is the last of the four
  cards to run and is this backlog item's own measure of whether model-
  based review can substitute for team-lead adjudication AT ALL --
  compare Fable's final call rate and time cost against what Task F's
  original team-lead-timed measurement would have cost, once both
  numbers exist

**F11. Team-lead adjudication timing, run AFTER F7-F10 (~unknown, no-history) Priority 15**
- Phase: Measurement. Team lead, 2026-09-17: "yes backlog, yes replacing
  task f. We are going to move it after completion of backlog items
  F7-10 as F11?" -- confirmed
- **This is Sprint 2 Task F's original measurement, not a new idea.**
  ADR-0004 names it "the number the whole design is constrained by":
  minutes of team-lead adjudication per accepted record. Sprint 1
  deferred it once already; this sprint's own Task F was going to
  produce it directly against ~20 screened-tier records, and is now
  REPLACED by F7-F10's model-based review instead of running standalone
- **Why AFTER F7-F10, not instead of them**: F10's own card already
  names the comparison this measurement exists to make -- "compare
  Fable's final call rate and time cost against what Task F's original
  team-lead-timed measurement would have cost." Running F11 after F7-F10
  complete means the team lead times adjudication on the SAME record
  set the four model reviewers already processed, so the comparison is
  apples-to-apples (same records, same starting review state) rather
  than a cold, unassisted timing run
- **What this measures that F7-F10 cannot**: F7-F10 measure whether
  MODEL review agrees with itself and catches real issues. Only F11
  measures the actual number ADR-0004 names -- team-lead minutes per
  record -- and only F11 can answer whether reviewing model OUTPUT
  (confirm/reject F10's resolved calls) costs less team-lead time than
  adjudicating a record cold, which is the real question this whole
  substitution is testing
- Depends on: F7, F8, F9, F10 all complete, in that order. This is the
  last item in the F7-F11 sequence and closes out what Sprint 2's
  original Task F was scoped to produce

**F12. Design and implement a paper/reference intake workflow (~unknown, no-history) Priority 16**
- Phase: Process / tooling. Added 2026-09-17 (team lead), mid-Sprint-2, on
  finding three new items to add (an example non-arXiv reference, an arXiv
  paper, and a GitHub repository): "Will need a way to easily add papers
  and references as I find them." Example set given: a LinkedIn-hosted
  reference link, `arxiv.org/abs/2602.11092`, and
  `github.com/merlinquantum/merlin`.
- **This is a two-phase item, and the first phase is design, not
  implementation** (same shape as F2). Phase 1 (this card): determine the
  best process for turning a found item (a link, a citation, a repo) into
  the correct repository update(s). Phase 2: build whatever Phase 1
  concludes is needed (a script, a template, a checklist) and use it going
  forward.
- **Open questions this card exists to answer, not to pre-decide**:
  - What does the PAPER repository (`D:\Data\Harold\EvidenceBasedDB\Papers`,
    non-git per `CLAUDE.md`'s two-directories table) need per new paper
    beyond the PDF itself -- is a companion `.md` sidecar warranted, or does
    `store/evidence.db` + `export/papers.json` already carry everything a
    sidecar would duplicate (this repository's own "determinate facts are
    computed, never stored" rule argues against a sidecar that just
    restates fields the store already has)?
  - What does the REFERENCES repository need per new reference, given
    references are NOT always papers -- non-technical articles, vendor
    training documents, software packages (the `eqc_models` PyPI package
    named at Sprint 1 close-out is exactly this case)? At minimum: what
    filename convention, what content must be preserved locally (the
    source may not stay live -- a LinkedIn link is not archival), and what
    links (source URL, DOI/arXiv id, PyPI/GitHub url) must be recorded and
    where.
  - Is one intake process enough for all three source types in the given
    example (a non-technical link, an arXiv paper, a GitHub repository), or
    does each need its own path converging on the same store update step?
  - How does this interact with F5's QCi deep-dive (bulk paper discovery)
    and F4/Task C's finding that the seed directories are NOT a fixed
    snapshot -- additions are continuous and expected. This card's output
    should be the standing process Task C's finding already implies is
    needed, not a one-off script for the three example items alone.
- **Not this card's job**: ingesting the three example items themselves.
  Those are illustrative inputs for designing the process, not a to-do
  list to clear by hand; Phase 2 (or a follow-on card) applies the
  resulting process to them along with everything else found since.
- Depends on: nothing technical. Can run independent of F7-F11 and F5.

**F13. Guard US English spelling in this repository's own process/design docs (~small, no-history) Priority 17**
- Phase: Process / tooling. Added 2026-09-17 (team lead), found while reviewing
  Sprint 2's docs: "this is a US English based repository (looked like we
  were unsure previously)." `CLAUDE.md` now states the policy explicitly
  (2026-09-17); this card builds the enforcement.
- Platform: this repository's own `.md` files -- ADRs, sprint plans,
  `CLAUDE.md`, `docs/*.md`. NOT `store/`, `export/`, or anything under
  `D:\Data\Harold\EvidenceBasedDB\` (papers, books -- out of this
  repository entirely).
- **Model, don't design from scratch**: `hsbc-quantum-fraud-2026` (read-only
  from this repository) built exactly this pair 2026-09-16/17:
  `scripts/us_english_fix.py` (a British-to-US converter over tracked
  markdown) and `experiments/src/test_us_english.py` (the guarding test,
  parametrized per file). Both are well-shaped for porting: a word-pair list
  (behaviour/behavior, organise/organize, licence/license, ~90 pairs),
  case-preserving substitution, a `PROTECTED` list of exact spans that must
  never be rewritten (proper nouns, direct quotations), and a test that
  fails the whole suite loudly (not silently skips) if the tracked-file
  count collapses to near-zero -- guards against the exact vacuous-guard
  failure this repository's own `test_guard_discipline.py` already
  documents as a recurring class here.
- **The one adaptation that is NOT a copy-paste**: the sibling repo excludes
  whole files/directories (`docs/paper/`, `docs/submission/`,
  `PREREGISTRATION.md`) because those are a FROZEN, already-submitted
  filing -- editing them after the fact would falsify a document of record.
  This repository has no equivalent frozen filing. Team lead, 2026-09-17:
  the exemption here is narrower and different in kind -- text quoted or
  cited VERBATIM from a paper or book keeps that source's own spelling (a
  `citation` field, a direct quotation in an ADR amendment, a paper title
  in `docs/ALL_SPRINTS_MASTER_PLAN.md`), but nothing else in this
  repository's own prose is exempt just because it lives in the same file.
  This means the port needs SPAN-level protection (quotation-aware, e.g.
  skip text inside `"..."` that is attributed to a source, or an explicit
  per-file list of protected spans as the sibling repo already does for its
  licence quotation) rather than whole-file exclusion as the primary
  mechanism.
- **Also needs a decision this card should make explicit, not assume**:
  whether `citation`-shaped fields inside committed JSON/markdown exports
  (`export/papers.json` citation strings, `store/*.sql` seed data) are in
  scope at all, given ADR-0004's own "the export is generated, never
  hand-edited" rule -- a guard that fires on generated output the source
  data itself controls would be testing the wrong layer.
- Depends on: nothing technical. Independent of F7-F12.

**F75. Action the 20-paper ADR checkpoint (~2h) Priority 7**
- Phase: Evidence Based DB / process (carried from the consumer repository's
  Sprint 14 retrospective improvement 5, 2026-09-14)
- Platform: `docs/adr/0004-evidence-based-db.md`, `0005-reference-library.md`
- Both ADRs promise a review at approximately 20 imported papers, with six
  named questions and the bad answer stated for each. A promise in a document
  is exactly what this project keeps having to replace with a mechanism, and
  an unactioned checkpoint is a note nobody reads
- The question that matters most is the measured one: how long team-lead
  adjudication takes per paper. At five minutes, 2,000 papers is 160 hours and
  the design needs rethinking; at thirty seconds the ambition is safe.
  Everything else in the checkpoint is schema tuning
- **CARRIES Sprint 1 Task E's deferred measurement (team lead, 2026-09-16).**
  Task E's premise-falsifier design called for timing a team-lead review of
  one ingested record BEFORE Task F scaled to 46 papers. A partial review ran
  (~7 minutes against the paper record and its assertions) and was then
  deliberately stopped: "I would like to remove the review and leave
  everything up to your best, informed (search and use AI as needed). We
  will get back to validating the DB contents at a future step in a future
  backlog item." Task E therefore shipped WITHOUT a completed
  adjudication-time measurement -- the schema and ingestion path are proven
  to work end to end, but the actual number ADR-0004 calls "the number the
  whole design is constrained by" is not yet known. F75 is that future step:
  it must produce the measurement Task E's falsifier logic was designed to
  produce, now against ~20 real records rather than one, since that
  opportunity was deliberately deferred rather than lost
- Revisions are recorded as dated amendments at the bottom of each ADR, never
  as edits in place
- Depends on: this repository's own F77 work (Sprint 1) and ~20 papers loaded
  (Sprint 1 Task F)

**F76. Guard the shared vocabulary between ADR-0004 and ADR-0005 (~1h) Priority 8**
- Phase: Evidence Based DB / tooling (carried from the consumer repository's
  Sprint 14 retrospective improvement 6, 2026-09-14)
- Platform: this repository
- ADR-0005's `applicability` field points at ADR-0004's context list rather
  than carrying its own enumeration. That was the right call -- two lists
  naming the same things is how the consumer repository's B1 variable count
  came to read differently across documents -- but nothing enforces that they
  agree
- Needs a test that fails when a record names a context the schema does not
  define, and when the ADRs' stated context lists diverge from the database's
- Depends on: this repository's own F77 work (Sprint 1)

### Out of scope, not yet candidates

- Inference, the graph store, and embeddings (explicitly out of scope per
  Lenat's footnote 9 -- none of their triggers has fired)
- `Books` and `GitHubRepos` record classes (paper records only this sprint)
- The 8th-grade explanatory document (F73 in the consumer repository;
  sequenced after this repository's own F77 work so its contents can be
  validated against the store)

## Design documents governing this repository

- `docs/adr/0004-evidence-based-db.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- `docs/adr/0005-reference-library.md` -- ACCEPTED, early-innovation, does NOT
  authorise implementation on its own
- Both carry a six-question review due after roughly 20 papers are loaded.
  Revisions land as dated amendments at the bottom of each ADR, never as
  silent edits. **The threshold is crossed**: 44 papers loaded (Sprint 1
  Task F), so this checkpoint (F75) is now actionable rather than pending.
