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
| 3 | docs/sprints/SPRINT_3_SUMMARY.md | [OK] Complete | 2026-09-18 to 2026-09-19 |

## Last Completed Sprint

**Sprint 3: Correct the Foundations, Then Measure Adjudication** (PR #20,
draft, review in progress). Delivered Tasks A-H per
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
and review-protocol depth recorded as a first-class input to F11/F18.
Full detail: `docs/sprints/SPRINT_3_SUMMARY.md`; results:
`docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`; retrospective:
`docs/sprints/SPRINT_3_RETROSPECTIVE.md` (16 categories x 4 roles; team
lead all "Very Good", Development Team five "Good"). Zero metered spend.

**The measurement Sprint 3 did NOT produce**: team-lead adjudication
minutes per record (F11), by design -- this sprint produced the four
independent reviews F11 compares against. F11 is now sequenced after
F25 D1-D3 so it measures adjudication of corrected records.

## Current sprint

None. Sprint 4 has not yet been scoped -- this section is populated at
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
  the "volume without judgment" risk ADR-0005 section 2c warns is MORE
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
  judgment
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
  sequentially after F7 (so neither anchors the other's judgment)

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
  at a time), find pairs or groups where the SAME kind of judgment call
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
  treats as closest to team-lead-level judgment. As an independent
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
  independent measurement of its own tier's judgment. F11 (below) is
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
- **Design input from Sprint 3's own results (retrospective improvement
  4, 2026-09-19)**: on the identical 18 records, the two reviews whose
  PROTOCOL required cross-record comparison and primary-source
  verification (F9, F10) found 7 inconsistencies and 4 real citation
  defects; the two whose protocol was per-record internal consistency
  (F7, F8) confirmed 18/18. Review depth is a protocol property at least
  as much as a tier property. F11 must therefore (a) give the team lead
  the SAME primary-source access the F10 protocol used (the local PDFs,
  the arXiv/publisher pages), or the timing measures a shallower task
  than F10 performed; and (b) record which protocol the team lead
  actually followed per record, so the eventual minutes-per-record
  number is comparable to F10's 599 seconds / 150k tokens for the set,
  not to F7's 182 seconds
- **Sequencing against F25 (recorded there too)**: run after F25 steps
  D1-D3 land, so the team lead adjudicates API-verified citations and a
  tier that means what the ADR says -- otherwise F11 measures the cost
  of re-finding defects F10 already found
- Depends on: F7, F8, F9, F10 -- all complete as of 2026-09-18, run in
  parallel with zero cross-visibility (not "in that order"; the
  sequential design was removed on 2026-09-18 at the team lead's
  direction). Results: `docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`.
  Also depends on F25 D1-D3 per the sequencing note above

**F12. Design and implement a paper/reference intake workflow -- SUPERSEDED by F25 (2026-09-19)**
- Absorbed into F25 Part C (team lead, 2026-09-19: one place for "a new
  paper enters the store correctly"). Its open questions (paper sidecar
  or not; what a non-paper reference needs recorded; one intake path or
  three; interaction with F5 and continuous seed-directory additions) and
  its three example inputs (a LinkedIn-hosted reference,
  `arxiv.org/abs/2602.11092`, `github.com/merlinquantum/merlin`) are
  carried verbatim in F25 C4. Number retained, never reused.

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
  (~90 British-to-US pairs across the -our/-or, -ise/-ize, -ence/-ense
  and doubled-consonant families; the literal examples that used to sit
  here were rewritten into US/US pairs by this very script's first
  sweep -- caught by Copilot on PR #20 -- which is exactly why the
  script's PROTECTED-span mechanism exists),
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
  license quotation) rather than whole-file exclusion as the primary
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
- **First `learning_log` entry, available now (Sprint 3 retrospective
  improvement 4, 2026-09-19)**: same 18 records, four tiers, zero
  cross-visibility. Haiku (per-record, quoted-anchor protocol): 18/18
  confirm, 0 defects found, 82,586 tokens, 182 s. Sonnet (per-record +
  certainty check): 18/18 confirm, correctly declared the certainty
  step not applicable, 70,021 tokens, 155 s. Opus (set-level cross-
  record protocol): 7 inconsistencies, 75,802 tokens, 208 s. Fable-tier
  Opus (full adjudication + primary-source verification): 4 real
  citation defects + 2 structural findings, 150,290 tokens, 599 s. The
  heuristic this seeds is NOT "use the top tier" -- it is that the
  protocol (cross-record comparison, primary-source verification)
  produced the findings, and any review card must require that
  protocol explicitly regardless of the tier assigned. Encode protocol
  as a first-class field beside tier in the heuristics file
- Depends on: F7, F8, F9, F10 complete (they are, 2026-09-18) and
  ideally F11, for the team-lead baseline the `learning_log` should be
  scored against. Build after F11 if F11 is near; otherwise seed from
  the entry above and add F11's row when it lands.

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

**F21. Fix the value/provenance/citation triplication at the store-write layer -- SUPERSEDED by F25 (2026-09-19)**
- Consolidated into F25 Part B4 / C3. Number retained, never reused.

**F22. Settle the `screened`-tier definition as a dated ADR amendment -- SUPERSEDED by F25 (2026-09-19)**
- Consolidated into F25 Part B3. Number retained, never reused.

**F23. Deliberate world/method/ml re-filing pass across all 46 papers -- SUPERSEDED by F25 (2026-09-19)**
- Consolidated into F25 Part B2. Number retained, never reused.

**F24. Mechanize citation refresh against arXiv/Crossref/DataCite APIs -- SUPERSEDED by F25 (2026-09-19)**
- Consolidated into F25 Part B1 / C1 / C5. Number retained, never reused.

**F25. Adjudication-review remediation: correct the paper records, and make the next paper right on the first try (~large, no-history) Priority 16**
- Phase: Data quality + ingestion process. Consolidates F12 and F21-F24
  (team lead, 2026-09-19): the findings of the four independent Sprint 3
  adjudication reviews (F7-F10, full record in
  `docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`) plus the paper/
  reference intake design F12 carried, in ONE card, because the team
  lead's framing is the right one -- "not just the DB entries need to be
  fixed, but a plan to ensure that the next paper that is read and
  incorporated into the DB is incorporated correctly on first try."
  Fixing 46 records without fixing the path that produced them buys one
  clean snapshot; the 47th paper reintroduces the defect class.
- Platform: `store/ingest.py`, `store/schema.sql` (one possible
  migration, flagged below as a decision), `docs/adr/0005-reference-
  library.md` (one dated amendment), a new `scripts/refresh_citations.py`,
  a one-off re-filing script, `store/evidence.db` + `export/*.json`,
  `tests/`.
- **Every count in this card is a snapshot as of 2026-09-19, re-verified
  against the live store when this card was written**, not copied from
  the reviews (46 papers; `citation` == `provenance` on 46/46 and ==
  `value` on 45/46; tiers 1 read / 18 screened / 27 seen; all 18
  screened papers have zero `paper_yields` rows; applicability rows by
  context: qc 23, qml 20, method 7, platform:dirac-3 5, world 4, `ml` 0,
  `hsbc-2026` 0).

**Part A -- Findings, by reviewer** (most rigorous first; each reviewer
ran cold with zero visibility into the others)

- **A1. Fable-tier (F10)** -- verified 18 records against PRIMARY sources
  (arXiv abstract pages, publisher pages, four local PDFs). 93 field
  calls: 38 accept / 43 revise / 12 reject. Found:
  - Four independently-confirmable citation defects: `dupont-2023`
    title wrong (recorded "Quantum Enhanced Greedy Solver for
    Optimization Problems"; actual "Quantum-Enhanced Greedy Combinatorial
    Optimization Solver"); `kordzanganeh-2022` missing its third author
    (Basil Kyriacou); `rand-2023-...` carries NO year in its citation and
    the only year on the record -- in its id -- is wrong (source says
    2022); `mancilla-2026` asserts two seed files are "identically-
    content" and hashing shows they are not.
  - Six records pin a preprint superseded by a peer-reviewed version the
    record never mentions: `dupont` (Science Advances 9(45)),
    `kordzanganeh` (Advanced Quantum Technologies 6, 2300043), `emami`
    (Springer proceedings chapter), `lubinski` (IEEE TQE, and the v3
    date is 2023-01-10 not -11), `mandra` (IEEE/ACM QCS 2021), `wang`
    (v2, "submitted to Elsevier"). `pelofske` is complete on DOI but
    omits volume/pages/article number and the LANL affiliation.
    `rehman`'s NYU Abu Dhabi affiliation is asserted but not verifiable
    from the arXiv page. `zajac` title punctuation differs from arXiv.
    `qci-2024-profiling` is formatted like a peer-reviewed citation while
    having no authors, venue, DOI or version, and does not say so.
  - `access` fields that say only "local file" (`loke`, `qci-2024`,
    `rand`) where ADR-0005 section 3 requires a DOI, an arXiv id, or an
    actual local path; `rand`'s stable URL is printed inside the report
    the record speculates about; `neven`'s access field is the model to
    copy (URL + local path + explicit negative finding).
  - Audit trail embedded inside `citation` strings (`loke`'s 700-char
    correction narrative, `kordzanganeh`'s arXiv-id note, `lubinski`'s
    and `mancilla`'s duplicate-file notes) -- correct instincts, wrong
    field; belongs in `updated_reason`/`evidence`, and is the reason
    `citation` cannot be machine-validated today.
  - Dispositions violating ADR-0005's "one line: why it was worth
    recording": adjectives carrying no information ("LANDMARK",
    "Extremely high-value", five variants of "strong candidate"), and
    `kordzanganeh`'s disposition says "seen tier" while its `tier` column
    says `screened` -- a determinate fact stored twice, disagreeing.
  - Applicability rationales that are true but materially incomplete in
    the wrong direction: `wang`'s "uses quantum annealing hardware
    directly" when the D-Wave Advantage ran only the two smallest models
    and the larger ones ran on a CLASSICAL Fujitsu Digital Annealer;
    `lubinski`'s "gate-based hardware: IonQ, Quantinuum" when the author
    list includes D-Wave; `kordzanganeh`'s "workload is QNNs" with no
    stated evidence; `rehman`'s symmetric-routing description of an
    asymmetric confidence-thresholded fallback; `qci-2024`'s "covers
    performance" for a document with specific, checkable, hedged
    results.
  - Two structural REJECTs against the whole set: (i) `screened` is
    unearned on all 18 -- ADR-0005 2c defines it as "an agent extracted
    the claim and proposed a verdict," nothing was extracted, and
    Amendment A1 excuses rather than reconciles this; (ii) `value` ==
    `provenance` == `citation` byte-identical -- this project's founding
    defect reproduced inside every paper row, one layer below where
    Sprint 3 Task B (F6 finding 1) fixed it at the export layer.
  - The highest-value latent content: a direct `contradicts` relation
    between `mancilla`/`zajac` (tabular QML advantage is structurally
    near-impossible; real amplitude encodings collapse to classical
    quadratic forms) and `emami`/`loke`/`qci-2024` (CVQBoost beats
    XGBoost on tabular fraud data). Both sides are in the store;
    `assertion_relations` is built; only extraction is missing.
- **A2. Opus (F9)** -- reviewed the 18 as a SET (~55 pairwise
  comparisons across 6 clusters). 7 inconsistencies, none of which
  requires a source PDF to see:
  - `world` applied on two incompatible tests within one pass:
    "platform-independent" passed `arute` (a contested empirical claim)
    and `rand` (a CISA-sponsored policy report) but not `britt-humble`
    (vendor-neutral HPC architecture); "mathematics/physics ground
    truth" (ADR-0004's actual definition) would pass `zajac`, the one
    theorem in the set, which got nothing. F10 reached the identical
    conclusion independently.
  - `method` inconsistently earned: `lubinski` and `mandra` got it for
    benchmarking/simulation methodology; `pelofske` (peer-reviewed IEEE,
    structurally the same sentence) did not; `mancilla` (whose
    disposition literally says "methodology") and `zajac` did not.
  - `qml` via workload: `kordzanganeh` earned `qml` because its benchmark
    payload was QNNs; `dupont` (same shape, optimization payload) did
    not; `wang` got both. The rule that separates them is coherent
    ("the optimized target must itself be an ML model") but is stated
    nowhere.
  - An unstated qc-subsumption rule: D-Wave-substrate `neven` keeps a
    generic `qc` row beside its specific one; Dirac-3-substrate
    `emami`/`loke`/`qci-2024` drop `qc`; and `qci-2024-unconventional-
    computing` (outside the 18) carries BOTH, so the rule is not even
    followed where it would explain the pattern.
  - Rationale-provenance asymmetry inside the CVQBoost cluster: `loke`
    and `emami` name where they looked ("page 1 keywords", "the arXiv
    affiliation block"); `qci-2024-profiling` -- the vendor-authored,
    non-peer-reviewed one that most needed an anchor -- names nothing.
  - `huynh` says its subject is "distinct from QML proper" twice and
    files under `qml` alone; `ml` exists and has zero users across all
    46 papers.
  - Ruled out, correctly, as non-findings: alphabetical applicability
    ordering (an export artifact) and the uniform absence of `hsbc-2026`
    on every paper (a global policy, consistently applied).
- **A3. Sonnet (F8)** -- 18/18 confirm on citation/context/applicability
  by internal-consistency reading. Its distinguishing contribution: it
  verified two ways that the certainty-reasoning half of its own task
  was NOT APPLICABLE (zero `paper_yields` for all 18; the store's 6
  yields rows all belong to one out-of-scope `read` paper) and said so
  explicitly instead of fabricating an assessment against empty data.
  It also noted, approvingly, that `emami` and `loke` are flagged as
  HSBC-relevant without claiming `hsbc-2026` -- relevance-to-a-project
  correctly not conflated with belonging-to-its-context.
- **A4. Haiku (F7)** -- 18/18 confirm, 0 reject, 0 unverified, under a
  protocol that required a quoted anchor per confirmation. The anchors
  resolve to "the title/disposition text matches the rationale," which
  is genuine evidence of internal consistency but not of correctness;
  every defect A1 found sits inside records A4 confirmed. This is the
  over-agreeable outcome F7's own card predicted, and it is the first
  real data point for F11.
- **Convergence worth weighing**: A1 and A2, with zero shared context,
  independently reached the same conclusions on `world`, on `method`,
  on `ml`'s zero users, on the `qci-2024` rationale being the weakest of
  its cluster, and on the latent `mancilla`-vs-CVQBoost contradiction.
  Independent convergence is stronger evidence than either report
  alone; those items are treated as settled findings below, not
  opinions.

**Part B -- Correct the existing records** (every change is a dated
`updated_reason`, never a silent overwrite; the export regenerates)

- **B1. Citation and access corrections** (from A1), applied through the
  refresh path in C1 so each is re-derived from the API/source rather
  than hand-retyped a second time: the four defects (`dupont` title,
  `kordzanganeh` author, `rand` year, `mancilla` false duplicate claim);
  the six superseded preprints; `pelofske`'s missing volume/pages/
  affiliation; `rehman`'s unverified affiliation (confirm from PDF
  byline or drop); `zajac` punctuation; `qci-2024` stating explicitly
  that no authors/venue/DOI exist; `access` fields given a real local
  path plus resolvable URL (`loke`, `qci-2024`, `rand`), on `neven`'s
  model. Move every piece of audit trail out of `citation` into
  `updated_reason`/`evidence` (`loke`, `kordzanganeh`, `lubinski`,
  `mancilla`). **Decision for the team lead**: `rand`'s id bakes in the
  wrong year -- rename the id (cascading through `record_contexts` and
  `paper_applicability`; nothing yields from it yet, so the blast radius
  is small today and only grows) or keep the id and record the
  correction in `updated_reason`. Recommend rename now, while cheap.
- **B2. world/method/ml re-filing pass across all 46 papers** (from A1
  + A2, convergent). First write down the tests, THEN apply them: `world`
  = mathematics/physics/standard-expansion facts true independent of any
  project (drop from `arute` and `rand`; add to `zajac`); `method` = how
  this library and its consumers build, reason and evaluate claims (add
  to `pelofske`, `mancilla`, `tung`; consider `britt-humble`; justify or
  drop `mandra`); `ml` = classical ML content not dependent on a quantum
  substrate (split `huynh` into `ml` + `qml`; add to `emami` for the
  XGBoost head-to-head, `neven` for the boosting formulation, `mancilla`
  for the public-tabular-benchmark result; decide `wang`'s primary
  context); state the qml-via-workload rule and apply it uniformly to
  `dupont`/`kordzanganeh`/`wang`; state the qc-subsumption rule and apply
  it uniformly to `neven`/`emami`/`loke`/`qci-2024`/`qci-2024-
  unconventional`. Fix the incomplete-in-the-wrong-direction rationales
  (`wang` D-Wave-only-for-small-models, `lubinski` platform list,
  `kordzanganeh` QNN evidence or drop, `rehman` asymmetric routing,
  `qci-2024` specific hedged results, `britt-humble` tight/loose
  taxonomy). Bring every disposition to one line and remove the `tier`
  mention from `kordzanganeh`'s. Every rationale that survives must name
  where it was read from (page, section, byline), on the `loke`/`emami`
  model -- a rationale that cannot say where its value came from is the
  defect this whole system exists against. **Existing tests pin some of
  what this pass changes**: `tests/test_paper_applicability.py` and
  `tests/test_qboost_paper_added.py` assert specific applicability sets
  (e.g. `neven` == {qml, qc}, which B2 may extend with `ml`). Each such
  test is updated in the SAME commit as the re-filing that changes it,
  with the reason in the commit message, and never loosened to a
  superset or a count to make it pass -- a pinned expectation that
  moved for a stated reason is a record; one that was relaxed is a
  guard that stopped guarding.
- **B3. Settle the `screened` tier** (from A1; a dated ADR-0005
  amendment, never a silent edit). **Decision for the team lead**: (a)
  demote every screened-with-zero-yields paper to `seen` (18 today), the
  honest claim; or (b) amend section 2c to define the tier the practice
  actually uses -- "dispositioned and applicability-derived, not yet
  mined" -- with `yields` moving to `read`. Either resolves the
  contradiction Amendment A1 papered over; (b) preserves the information
  the 18 records genuinely carry (a real disposition and re-derived
  applicability distinguish them from the 27 `seen`), so recommend (b),
  with the amendment also restating that `checked_against_source` and
  `yields` are the `read`-tier obligations.
- **B4. Fix the triplication at the store-write layer** (from A1;
  extends Sprint 3 Task B, which fixed only the export). `insert_paper()`
  must stop accepting `citation` and `provenance` as two independent
  inputs that happen to be equal. **Decision for the team lead**: drop
  `paper_fields.citation` as a stored column (schema migration -- a
  table rebuild in SQLite, plus `test_schema.py`/`test_ingest.py`
  updates) or keep the column and have `insert_paper()` derive it from
  `records.provenance` with no independent parameter. Recommend the
  drop: a derived column that still exists is a column someone will
  eventually write to directly. Note ADR-0004 section 3 defines
  `provenance` as "pointer to what establishes it" -- for a paper that
  is arguably the artifact (local path / API response / retrieval
  date), not the citation; decide whether to take that further step
  now or record it as the next amendment. **`value` is the third copy
  and must be fixed in the same pass**: `ingest_seed_set.py` sets
  `value=entry["citation"]`, which is why `value` == `citation` on
  45/46 papers, while `PaperRecord`'s own comment defines `value` as
  "a one-line description of the paper." Make `value` the paper's
  title (or a one-line description), so the three fields carry three
  different things: what it is (`value`), how to cite it (`citation`,
  API-derived), and what establishes the record (`provenance`).
- **B5. Extract the contradiction** (from A1/A2, convergent; the natural
  end state, last in sequence). Promote `loke`, `emami`, `qci-2024-
  profiling`, `mancilla`, `zajac` to `read` (each then owes
  `checked_against_source` and `yields`, which C2 enforces), extract the
  opposing assertions with GRADE-style `certainty_reasons` (vendor
  self-benchmarking is the textbook downgrade case for `emami`/
  `qci-2024`; `wang`'s own section 8 limitations are `certainty_reasons`
  written by the authors), and wire `assertion_relations` `contradicts`
  between them. Also confirm which Neven paper CVQBoost's lineage
  actually rests on (QCi cites "Neven et al. 2009", the store holds
  2012) before any assertion cites `neven-2012`. Three smaller F10
  findings land here as `evidence`-tier notes and candidate `supports`
  relations, so they are not lost between now and extraction: (i)
  `emami`'s "all six authors are QCi employees" is correct on the
  byline but Nicholas Chancellor holds a concurrent Durham University
  affiliation -- the vendor-independence inference is thinner than it
  looks, and belongs in `evidence` when the record reaches `read`; (ii)
  `rehman`'s confidence-thresholded quantum fallback and `mancilla`'s
  "deploy the certified model as a specialist alongside the production
  system" are the same deployment pattern reached independently -- a
  `supports` relation once both yield assertions; (iii) `tung`'s
  meta-learned encoding selection "without requiring quantum evaluation
  during inference" and `mancilla`'s simulator-free SPECTRA screen are
  both cheap pre-screens for whether quantum is worth attempting --
  the same relation, and a theme the library should be able to query.

**Part C -- Make the next paper right on the first try** (guards, not a
checklist; each proven to fail by injection per this repository's
guard-discipline standard)

- **C1. Citations come from an API, never from a keyboard.** ADR-0005
  section 2 already says so; nothing enforced it, and every B1 defect is
  the direct consequence. Build `scripts/refresh_citations.py`
  (F24's proposal): given a paper's `access` (arXiv id / DOI), fetch the
  bibliographic record from arXiv, Crossref or DataCite, render the
  canonical citation string, and DIFF it against the store -- flagging
  mismatches and superseded versions for human review, never auto-
  applying (an overwrite would clobber `loke`'s correction history).
  Then make it the ingestion path: `insert_paper()` accepts an `access`
  id and derives the citation; a hand-typed citation is refused UNLESS
  the record explicitly declares it has no resolvable id (the
  `qci-2024`/`rand` case), in which case `citation` must carry a
  visible "hand-transcribed from <page>, no DOI/arXiv id" marker and
  `access` must carry the actual local path. Run the refresh on a
  schedule (each delivery cycle, Phase 8.3 design-doc currency check is
  the natural slot) so a preprint that gets published is caught, not
  discovered by a reviewer a year later. **Retire the hand-typed source
  explicitly**: today every citation originates in
  `scripts/seed_set_metadata.json`, generated from hand-authored dicts
  in `scripts/generate_seed_set_metadata.py`, and `ingest_seed_set.py`
  reads it verbatim. Either that file becomes an OUTPUT of the refresh
  script (ids in, API-derived citations out) or it stops carrying
  `citation` at all and carries only `access` ids plus the human-
  authored fields (`disposition`, `context`, `promote`). Leaving it as
  is means the next bulk load reintroduces hand-typed citations through
  the old door while the new one stands guarded beside it. The first
  deliverable of C1 is the refresh script run in diff mode against all
  46 papers -- which also independently verifies F10's primary-source
  claims (the corrected `dupont` title, the six published versions)
  rather than taking a reviewer's finding on trust; a finding is itself
  a claim that needs provenance.
- **C2. `validate_paper()` grows teeth.** Sprint 3 Task B added it with
  one rule (tier `read` requires `checked_against_source`). Extend it,
  each rule with a failing test: tier semantics per the B3 decision
  (`read` requires `yields` >= 1 and `checked_against_source`;
  `screened` per the amended definition); `access` must be a DOI, an
  arXiv id, or an existing local path -- a bare "local file" is
  rejected; `disposition` is one line (a length/newline guard);
  `citation` may not contain audit-trail markers ("CORRECTED", "NOTE:",
  "verified against", "recorded once") -- those go to `updated_reason`/
  `evidence`; a paper whose disposition text names a tier is rejected
  (the column is the resolver); every `paper_applicability` rationale
  must be non-empty and, **decision for the team lead**, either (i) end
  with a source anchor by convention ("-- p.1 keywords", "-- arXiv
  affiliation block"), guarded by a regex, or (ii) gain an explicit
  `evidence_anchor` column, which is a schema change and therefore a
  Class 1 ADR decision. Recommend (i) now, (ii) recorded as the next
  amendment if (i) proves too loose.
- **C3. One write, one source of truth.** B4's fix, stated as the
  guard: a test that inserts a paper and asserts `citation` is derived,
  not independently settable (or that the column no longer exists).
- **C4. The intake workflow (F12, absorbed verbatim).** Team lead,
  2026-09-17: "Will need a way to easily add papers and references as I
  find them," with three example inputs -- a LinkedIn-hosted reference
  link, `arxiv.org/abs/2602.11092`, and `github.com/merlinquantum/
  merlin`. Design first, build second. The questions F12 existed to
  answer, unchanged: what the PAPER directory (`D:\Data\Harold\
  EvidenceBasedDB\Papers`, non-git) needs per paper beyond the PDF -- a
  sidecar `.md`, or nothing, since the store already holds it and
  "determinate facts are computed, never stored"; what a REFERENCE needs
  when it is not a paper (non-technical article, vendor training doc,
  the `eqc_models` PyPI package) -- filename convention, what content
  to preserve locally because the source may not stay live, which links
  (URL, DOI/arXiv, PyPI/GitHub) recorded where; whether one intake path
  serves all three source types or three paths converge on one store-
  update step; how this interacts with F5's bulk QCi discovery and with
  the fact that the seed directories grow continuously. **New
  constraint from Parts A-C**: whatever the design, every source type
  converges on the SAME store-update step, and that step is C1 + C2 +
  C3 -- the intake workflow is the only door, and the guards stand in
  it. Not this part's job: ingesting the three examples by hand; they
  are the first inputs through the finished door.
- **C5. Prove the door holds.** For each guard in C1-C3: break it, watch
  the test go red, restore. Then run one real paper end to end through
  the finished path (the arXiv example from C4 is the obvious candidate)
  and confirm the resulting record passes the F10 protocol -- citation
  matches the API, access resolves, disposition is one line, every
  rationale names its anchor, tier matches its obligations -- with no
  human correction pass afterward. That single record is the acceptance
  test for "correct on the first try."

**Part D -- Execution sequence, by dependency** (not by reviewer)

1. Team-lead decisions first, since three of them shape the code: B3
   tier option (a/b), B4 column drop vs derive, C2 anchor convention vs
   column, B1 `rand` id rename. All four are numbered questions at the
   sprint that selects this card.
2. Build the door before pushing anything through it: C1 refresh script
   in diff/review mode, C2 validator rules, C3/B4 write-layer fix, each
   with its failing test (C5 injection proofs as they land).
3. B3 ADR-0005 amendment (dated), then B1 citation/access corrections
   applied via the C1 path so they are re-derived rather than retyped.
4. B2 re-filing pass across all 46, with the context tests written down
   before the first record is touched, run through the C2 validator.
5. C4 intake design, then the three example items through the finished
   path, then C5's single-record acceptance test.
6. B5 promotion, extraction, and the `contradicts` relation.

- **Too large for one sprint?** Probably: Parts B and C are each a
  sprint's worth. If split, the cut is between D2-D3 (the door, plus
  the ADR amendment and citation corrections) and D4-D6 (re-filing,
  intake, extraction) -- never between "fix the records" and "fix the
  path," which is the split the team lead's framing rules out.
- **Not this card's job**: F11 (the team-lead timing comparison against
  F7-F10) -- it consumes the review record, not this remediation; F5's
  bulk QCi discovery (it will be the first heavy user of C4's door once
  it exists); F18 (model-assignment heuristics), even though Part A's
  reviewer comparison is its natural seed data.
- Depends on: nothing technical. Supersedes F12, F21, F22, F23, F24.
- **Sequencing against F11 (recommendation, recorded here so the next
  refinement does not re-derive it)**: run F25 steps D1-D3 (the
  decisions, the guarded ingestion path, the ADR amendment, the citation
  and access corrections) BEFORE F11, so the team lead times
  adjudication of records whose citations are API-verified and whose
  tier means what the ADR says -- otherwise F11 measures the cost of
  re-finding defects F10 already found, not the cost of adjudicating.
  D4-D6 (re-filing, intake design, extraction) can follow F11; the
  re-filing in particular benefits from the team lead's own
  adjudication pass having just happened on the same records.

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
