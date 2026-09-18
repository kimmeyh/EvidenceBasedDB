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

**Sprint 2: Validate, Guard, and View the Store** (PR #11 merged to
develop, then develop merged to main via PR #19). Delivered Tasks A-E, G
per `docs/sprints/SPRINT_2_PLAN.md`: re-derived real paper applicability
(Task A, corrected a Sprint 1 undercount), extracted and validated a real
HSBC-submission assertion (Task B), spot-checked store content against
the 44 source PDFs and added the QBoost paper (Task C), a vocabulary
guard between ADR-0004/0005 (Task D, F76), both ADRs' 20-paper
checkpoints walked and recorded as dated amendments (Task E, F75), and
`scripts/view.py` (Task G, F3). Task F (team-lead adjudication timing)
was REPLACED mid-sprint by F7-F11 (Class 3 scope change, backlog). Also
delivered: F12 and F13 added to the backlog, `CLAUDE.md`'s explicit
US-English statement, three retrospective improvements applied as
commits (mechanical GitHub-issue-state check in Phase 5, the
`block_ask_user_question.py` hook, a data-precondition check in
`SPRINT_PLANNING.md`), and PR #11 review fixes (Copilot + Claude): a
genuinely vacuous guard test corrected and verified by injection, two
internally-inconsistent counts in ADR-0004's Amendment A4 fixed before
merge, `scripts/view.py`'s connection-close/error-handling hardened, and
both ADR amendments given explicit point-in-time qualifiers after the
team lead flagged that a bare count in a document with edit
restrictions reads as a durable fact rather than a snapshot -- now a
standing `CLAUDE.md` rule for future measurement-style amendments. F14
added to the backlog from the review's remaining findings. Full detail:
`docs/sprints/SPRINT_2_SUMMARY.md`; retrospective:
`docs/sprints/SPRINT_2_RETROSPECTIVE.md` (16 categories x 4 roles, all
"Very Good"). Zero metered spend; this repository has none.

**The measurement Sprint 2 did NOT produce**: team-lead adjudication time
per record, ADR-0004's own named design constraint, deferred a second
time. Sprint 1 deferred it by team-lead decision; Sprint 2's own Task F
was scoped to produce it and was replaced instead by F7-F11 (backlog),
sequenced so F11 runs after F7-F10 complete in a future sprint.

## Current sprint

**Sprint 3: Correct the Foundations, Then Measure Adjudication** (branch
`feature/20260918_Sprint_3`, plan drafted 2026-09-18, awaiting Phase 3.7
approval). Scope (team lead, 2026-09-18): F2 (spamfilter-multi deep-dive,
Phase 1 only), F6 (six remaining PR #1 code-review findings), F13 (US
English spelling guard), F14 (data-correction script hardening) -- run
first, in that order -- then F7, F8, F9, F10 (adversarial
record-adjudication review, one card per model tier) run second,
independently and in parallel with each other. F11 explicitly out of
scope this sprint. Full detail: `docs/sprints/SPRINT_3_PLAN.md`.

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
- **CORRECTED (team lead, 2026-09-18): runs INDEPENDENTLY of F7/F8, not
  after them.** F7-F10 are four separate measurements of how each model
  tier reviews the SAME cold record set on its own -- "they should not
  be designed to depend on each other. They are independent reviews to
  see how each of them will do the review and what they will find." This
  card's own review task (finding cross-record inconsistencies in the
  ORIGINAL record set) does not require F7/F8's output to execute; it
  only needs the record set itself, same as F7 and F8 do
- Depends on: the same ~18-20 screened-tier record set as F7/F8, reviewed
  in parallel with them, not sequenced after their findings

**F10. Adversarial record-adjudication review by Fable (~unknown, no-history) Priority 14**
- Phase: Research / adjudication substitution. Same origin as F7
- **What this reviewer is FOR**: Fable is this project's own documented
  preferred top tier / Lead Developer role -- the tier this project
  treats as closest to team-lead-level judgement. As an independent
  fourth reviewer, its distinguishing job is the full adjudication a
  team lead would actually perform: not just confirming fields (F7) or
  checking certainty reasoning (F8) or cross-record consistency (F9)
  alone, but making the complete accept/reject/revise call on each
  record AS IF it were the final decision-maker, with no visibility
  into what the other three tiers found
- **REDESIGNED (team lead, 2026-09-18): runs INDEPENDENTLY, not as a
  disagreement-adjudicator over F7/F8/F9's output.** The original design
  had F10 reading the other three reviews and resolving their
  disagreements, which is incompatible with "these are independent
  reviews to see how each of them will do the review and what they will
  find" -- an adjudicator that reads prior verdicts cannot also be an
  independent measurement of its own tier's judgement. F11 (below) is
  where the four independent outputs actually get compared; F10 itself
  produces only its own independent review, same shape as F7/F8/F9
- **Review task**: given the same cold record set as F7/F8/F9, for each
  record make the full accept/reject/revise call across every field
  (citation, context, applicability, certainty/certainty_reasons/
  fidelity), citing the source directly for each call -- effectively a
  complete adjudication pass, not a narrower per-field check
- **What would make this reviewer's output untrustworthy, name it now**:
  a review that reaches the same verdict on every record with no
  variation in reasoning depth or citation specificity, which would
  read as a templated pass rather than genuine per-record adjudication
- Depends on: the same ~18-20 screened-tier record set as F7/F8/F9,
  reviewed independently and in parallel with them. F11 (not this card)
  is where all four tiers' findings are actually compared against each
  other and against team-lead timing

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

**F14. Harden the one-off data-correction scripts against silent partial failure (~small, no-history) Priority 18**
- Phase: Code quality / tooling. Added 2026-09-18, backlogged from PR #11's
  Claude code-review pass rather than fixed inline (both scripts had
  already been run against the live store; a behavior change alone would
  not affect data already applied, so this is about the NEXT time a
  similar one-off script is written, not a live defect in this store's
  current content).
- Platform: `scripts/apply_paper_applicability.py` (and the pattern it
  sets for any future one-off data-correction script of this shape).
- **Finding 1**: `apply_paper_applicability.py` prints a `warning:` to
  stderr and continues (exit 0 regardless) when a `paper_id` key in its
  hand-authored `APPLICABILITY` dict does not match any real record --
  the count is collected (`skipped_no_paper`) but never affects control
  flow. Since the script's own stated purpose is "apply to all 44
  seed-set papers," a single typo'd key means that paper is silently left
  with the exact empty-applicability defect the script exists to fix, and
  nothing forces anyone to notice a stderr line buried in normal output.
- **Finding 2**: the same script skips a paper entirely if it already has
  ANY row in `paper_applicability`, without checking whether the existing
  rows match the dict's intended context set -- a paper left
  half-populated by an interrupted prior run would be silently skipped
  and never completed on a re-run.
- **Proposed fix, for review at carding**: make `skipped_no_paper > 0`
  produce a non-zero exit code (or assert the applied+skipped count
  equals `len(APPLICABILITY)` before declaring success), and make the
  "already set" check compare the existing context-id set against the
  dict's intended set rather than trusting any non-zero count.
- Depends on: nothing technical. Low priority since it hardens a
  one-off script pattern rather than fixing a live defect.

## F2 Phase 1 output: drafted cards from the spamfilter-multi survey

Produced 2026-09-18 (Sprint 3 Task A). Six cards, each from a genuinely
NEW artifact found in `spamfilter-multi` (read-only) -- most of that
repository's process content is already present here in adapted form,
since this repository's own methodology was seeded via
`hsbc-quantum-fraud-2026`, which itself derived from spamfilter-multi.
Ordered by dependency below. Per F2's own card, this is Phase 1's
output only; adopt/reject and execution are the team lead's Phase 2
decision, not decided here.

**F15. Hook-enforce the sprint auto-advance window (~medium, no-history) Priority 19**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `.claude/hooks/sprint-auto-advance.ps1` (read-only source, 2026-09-18
  survey), rewritten in Python for this repository per its own
  Python-hooks convention
- Platform: `.claude/hooks/`, a new `block_procedural_question_stop.py`
  (or similar), registered on the `Stop` event
- **The gap this closes**: this repository's own auto-advance window
  ("between Phase 3.7 approval and Manual Validation, do not ask
  permission at task/phase boundaries") is currently stated only in
  prose (`SPRINT_EXECUTION_WORKFLOW.md`'s "Auto-advance window" line).
  This repository has already lived the exact failure class this hook
  exists to prevent: the AskUserQuestion ban was ALSO prose-only and was
  violated twice in one Sprint 2 session before being hook-enforced
  (`.claude/hooks/block_ask_user_question.py`). The spamfilter-multi
  source names the identical origin story: "Opus 4.7 was observed
  violating the Phase Auto-Advance Rule even though the rule lives in
  CLAUDE.md... documentation-only controls proved insufficient."
- **What it should do, adapted from the source**: on the `Stop` event,
  if the branch is a sprint feature branch AND a `SPRINT_N_PLAN.md`
  exists AND `plan_approved: true` AND the sprint has not yet reached
  Manual Validation, block a stop whose last message ends in a
  procedural question with no named `SPRINT_STOPPING_CRITERIA.md`
  criterion cited. Allow outside that window (pre-approval, or at/after
  Manual Validation) -- asking is CORRECT there
- **Adaptation needed, not a copy-paste**: the source hook's question-
  detection logic (gerunds, "want me to", bare "next:", hortative "let
  me") is tuned against ~24 real violation/allow fixture pairs
  accumulated over many sprints in that repository. This repository has
  no equivalent fixture history yet; the initial version will need a
  smaller, EvidenceBasedDB-specific fixture set built from this
  project's own actual near-violations (the AskUserQuestion incidents
  are two ready examples of the shape to detect, even though they were
  a tool call, not a stop-message question)
- Depends on: nothing technical. Independent of every other F# card.

**F16. Hook-enforce Phase 3.3.1's two deliverables before task commits (~small, no-history) Priority 21**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `require-sprint-cards.ps1` (read-only source, 2026-09-18 survey)
- Platform: `.claude/hooks/`, a new `block_missing_sprint_cards.py`,
  registered on `PreToolUse` for `Bash|PowerShell`
- **What it should do**: block a `git commit` when
  `sprint_status.json`'s `plan_approved` is true but `github_issues` is
  empty or `pr` is null -- Phase 3.3.1 produces both together, and nothing
  currently stops a task commit from landing before either exists. This
  repository has not yet had the specific failure the source hook
  guards (six task commits landing with no cards, discovered at Phase 7)
  but the mechanism is cheap and the failure mode is structurally
  possible here the same way
- **Adaptation needed**: the source hook reads its own repository's
  `sprint_status.json` shape (`current_sprint.pr_number`); this
  repository's own file uses `pr` (see `.claude/sprint_status.json`,
  e.g. Sprint 3's `"pr": 20`) -- field name differs, logic is identical
- Depends on: nothing technical. Pairs naturally with F15 (both are
  Phase-boundary enforcement hooks) but neither blocks the other.

**F17. Port the mutation-lock pair for guard-discipline injection tests (~small, no-history) Priority 23**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `mutation-lock.ps1` + `block-commit-during-mutation.ps1` (read-only
  source, 2026-09-18 survey)
- Platform: `.claude/hooks/`, a new lock-file mechanism plus a
  `PreToolUse` hook blocking `git commit` while a lock is held
- **The gap this closes**: this repository's own guard-discipline
  standard (CLAUDE.md: "prove it FAILS... break the thing it guards,
  watch it go red, then restore") is followed by convention every
  sprint (Sprint 2's `block_ask_user_question.py` test, the ADR
  vocabulary guard fix, the `view.py` relation-resolution fix were all
  verified this way) but nothing stops a commit from landing mid-
  mutation, between the deliberate break and the restore. The source
  repository hit this twice in one sprint: once sweeping up a live
  mutation probe, once committing a mutated (false) Play Store
  declaration -- "vigilance was not the missing ingredient; a structural
  gate was"
- **Adaptation needed**: the source's own trigger (a Google Play
  declaration table) does not exist here; the mechanism (advisory lock
  file in a gitignored directory, checked by a commit-time hook, with
  staleness handling so a crashed session can't deadlock future
  commits) is fully generic and needs no EvidenceBasedDB-specific
  rework beyond the file paths
- Depends on: nothing technical. Independent of F15/F16.

**F18. Build a data-driven model-assignment heuristics file (~medium, no-history) Priority 60**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `.claude/model_assignment_heuristics.json` (read-only source,
  2026-09-18 survey)
- Platform: a new `.claude/model_assignment_heuristics.json` (or
  equivalent), referenced from `docs/SPRINT_PLANNING.md`'s existing
  static role table
- **What the source has that this repository doesn't**: task patterns
  with keywords mapped to a recommended model tier, each carrying a
  `success_rate` and `sample_size` from actual outcomes; explicit
  escalation triggers (e.g. "test failure after 2 Haiku attempts ->
  escalate to Sonnet"); a numeric scoring rubric (file impact +
  cognitive load + risk factors -> model threshold); and a `learning_log`
  of real assignment outcomes updated per retrospective. This
  repository's own `SPRINT_PLANNING.md` role table is static and
  qualitative -- Haiku/Sonnet/Opus/Fable roles are named, but nothing
  tracks whether an assignment actually worked
- **Directly seeded by this sprint's own F7-F10 (and future F11)**: once
  the four independent model-tier reviews run, their outcomes (which
  tier caught what, at what apparent cost) are exactly the kind of data
  point the source's `learning_log` accumulates. This card should not
  be built before F7-F11 produce at least one real data point, or it
  launches empty the same way the source's own file states it was
  "seeded from Phase 3.1-3.3 work, will refine over 3-5 sprints"
- Depends on: F7, F8, F9, F10 (and ideally F11) producing at least one
  round of real outcome data to seed the `learning_log` with -- building
  this card before then would ship an empty heuristics file with
  nothing to recommend from.

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

**F20. Wrap `docs/BACKLOG_REFINEMENT.md` as an invokable skill (~small, no-history) Priority 27**
- Phase: Process / tooling. Modeled on `spamfilter-multi`'s
  `backlog-refinement` SKILL.md (read-only source, 2026-09-18 survey)
- Platform: a new `.claude/skills/backlog-refinement/SKILL.md`
- **What this closes**: `docs/BACKLOG_REFINEMENT.md`'s presentation
  format is already current and matches the source's own template
  almost exactly (both clearly share the same lineage) -- there is no
  content gap. The gap is procedural: the source wraps its doc as an
  invokable skill with an explicit first step ("read the format doc IN
  THIS TURN, a read from an earlier turn does not count") and a named
  hard rule that skipping that step is a process violation. This
  repository has committed exactly this violation's cousin before
  (checking a memory/CLAUDE.md rule exists is not the same as applying
  it) -- wrapping the doc as a skill makes "read it fresh, every time"
  the invocation contract rather than a habit
- Depends on: nothing technical. Lowest-effort of the six; could be
  done alongside F19 since both touch the skills directory.

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
  silent edits. **The checkpoint is DONE**: walked against the real store
  at 46 papers (Sprint 2 Task E, F75, shipped) -- ADR-0004 Amendment A4,
  ADR-0005 Amendment A1. Both amendments carry an explicit point-in-time
  qualifier (2026-09-18) since their counts are a snapshot, not a durable
  fact, in a document that does not permit edits in place.
