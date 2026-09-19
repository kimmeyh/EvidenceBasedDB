# Sprint 3 Tasks E-H: F7-F10 Independent Adjudication Review Results

Four independent reviews of the same 18 screened-tier paper records
(`arute-2019-quantum-supremacy-google-nature` through
`zajac-2026-inverse-born-rule-equivalence`), one per model tier, run with
**zero cross-visibility between them** -- each as a fresh subagent with no
shared context, no access to another review's output, and no instruction
referencing another reviewer's existence. This is the record F11 (backlog,
future sprint) compares against team-lead-timed adjudication of the same
set.

**Snapshot date: 2026-09-18.** All counts and record states below are as
of that date, against the store as it existed then -- per the standing
rule in `CLAUDE.md` on point-in-time qualifiers for measurement-type
records.

**Premise-falsifier check passed before these reviews ran** (per
`SPRINT_3_PLAN.md`): `git diff` across every Task A-D commit showed zero
changes to `export/`, confirming F6's code/schema fixes did not alter any
record value before F7-F10 reviewed it.

## F7 (Haiku) -- Task E

**Protocol**: confirm/reject citation accuracy, primary context, and each
applicability entry, with every confirmation required to quote an exact
source substring (a "looks right" confirmation with no quoted anchor is
not acceptable per the card's own design).

**Result**: 18/18 fully confirmed, 0 rejections, 0 unverified.

**Reading the result**: this outcome is consistent with the exact risk
F7's own card named in advance -- "not missing subtle context, [but]
being too agreeable/fast and confirming a record without actually
re-deriving the claim from the source." Most quoted anchors resolve to
"the title/disposition text matches the applicability rationale," which
is real evidence of internal consistency but is not the same standard
F10 applied (verification against primary sources: arXiv abstracts,
publisher pages, local PDFs). F10 independently found 4 real citation
defects and multiple content-level applicability problems in this same
set that F7 did not surface. This gap between F7 and F10's findings, on
the identical record set, is itself the first real data point for F11's
eventual model-tier comparison.

## F8 (Sonnet) -- Task F

**Protocol**: same base fields as F7, plus an explicit certainty-reasoning
check (does `certainty_reasons` actually justify the assigned
`certainty` level) for any of the 18 that had yielded an assertion.

**Result**: 18/18 confirmed on citation/context/applicability, 0
rejections, 0 unverified. Certainty-reasoning check: **not applicable**,
verified and stated explicitly rather than silently skipped -- `SELECT
COUNT(*) FROM paper_yields` for all 18 ids returns 0; the store's only 6
`paper_yields` rows all belong to `lenat-marcus-2023-trustworthy-ai`
(tier `read`, out of this review's scope). None of the 18 screened-tier
papers under review have been mined, so none have assertion records to
adjudicate -- correctly identified as expected pipeline state per
ADR-0005 (yields/checked_against_source apply only at tier `read`), not
a defect.

**Reading the result**: F8 reached the same citation/context/
applicability verdict as F7 (18/18 confirm), but WITHOUT F10's
primary-source verification step, so it also missed the citation defects
F10 found. It correctly recognized and stated the certainty-check's
inapplicability rather than fabricating an assessment against empty
data, which is itself a meaningful positive signal about this tier's
reliability on the "know what you don't know" axis.

## F9 (Opus) -- Task G

**Protocol**: review the 18 records as a SET, not one at a time, to find
cross-record inconsistencies -- the same kind of judgment call made
differently across records with no stated reason for the difference.

**Result**: 7 genuine inconsistencies found, ranked by confidence
(~55 substantive pairwise comparisons made across 6 thematic clusters,
plus 2 whole-set mechanical sweeps).

- **High confidence (3)**: (1) `pelofske` (peer-reviewed IEEE) denied a
  `method` applicability row that structurally similar `lubinski`
  (arXiv) and `mandra` received on weaker venues; (2) `britt-humble`
  denied a `world` row on a "platform-independent" test that `arute` and
  `rand` passed on the identical test; (3) `dupont` denied `qml` under a
  rule (`kordzanganeh`'s "benchmark workload is QNNs, therefore qml")
  that would otherwise apply to it too.
- **Medium-high (1)**: rationale-quality asymmetry within the identical
  CVQBoost/Dirac-3 cluster -- `loke` and `emami` name their evidence
  ("confirmed from page 1 keywords," "confirmed from the arXiv
  affiliation block"); `qci-2024-profiling-cvqboost` does not, and it is
  the one vendor-authored, non-peer-reviewed record in the trio that most
  needed the anchor.
- **Medium (2)**: `neven` (D-Wave substrate) keeps a generic `qc` row
  alongside its platform-specific rationale; `emami`/`loke`/`qci-2024`
  (Dirac-3 substrate) drop `qc` entirely -- an unstated, inconsistently
  applied subsumption rule. `mancilla`/`zajac` (adjudication-methodology
  papers) denied `method` that `lubinski` received on the same
  "evaluates quantum claims" reasoning.
- **Lower (1)**: `huynh`'s own record text says its subject is "distinct
  from QML proper" and files it under `qml` alone, with the unused `ml`
  context available.
- **Also noted, not counted as an inconsistency**: `ml` context has zero
  users across all 46 papers in the store, despite several records
  (`wang`, `huynh`, `neven`) carrying substantial classical-ML content --
  flagged as a vocabulary-policy question for the 20-paper ADR checkpoint
  review, not a pairwise defect.

## F10 (Fable-tier Opus) -- Task H

**Protocol**: full ACCEPT/REJECT/REVISE adjudication of every field on
every record (citation, context, each applicability entry, and any
yielded assertion's certainty), verified against PRIMARY SOURCES (arXiv
abstract pages, publisher pages, four local PDFs read directly), not
just internal record consistency.

**Result**: 93 field-level calls -- 38 ACCEPT, 43 REVISE, 12 REJECT.
Full per-record detail in the review transcript (referenced from
`.claude/sprint_status.json`); highlights below.

**Real, source-verified defects found (not present in F7/F8/F9's
reviews, since neither fetched primary sources)**:
- `dupont-2023`: recorded title is wrong ("Quantum Enhanced Greedy Solver
  for Optimization Problems" vs. the actual "Quantum-Enhanced Greedy
  Combinatorial Optimization Solver"); also pins v1 though the paper
  reached v2 and was published in Science Advances.
- `kordzanganeh-2022`: a named author (Basil Kyriacou, third author) is
  missing from the citation; also pins v1 though the paper reached v2
  and was published in Advanced Quantum Technologies.
- `rand-2023-...`: the citation carries NO year at all, and the record's
  own id asserts 2023 -- the source's copyright page states 2022. The
  only year anywhere on the record is wrong.
- `mancilla-2026`: claims two seed files are "identically-content"; F10
  hashed both and they are NOT byte-identical (differ by ~7.7KB) --
  same paper, different files, a verification that was never actually
  performed despite being asserted.
- Five records (`emami`, `lubinski`, `mandra`, `wang`, `kordzanganeh`,
  `zajac` -- six, not five, per the per-record detail) cite a preprint
  version superseded by a peer-reviewed publication the record does not
  reference.

**Two cross-cutting structural findings, treated as REJECT against the
whole set**:
1. **`screened` tier is unearned on all 18.** ADR-0005 section 2c defines
   `screened` as "an agent extracted the claim and proposed a verdict";
   all 18 have zero `paper_yields` rows. ADR-0005's own Amendment A1
   (2026-09-17) calls this "expected at their tier," which F10 argues
   contradicts rather than reconciles with the tier's own definition.
   F10's recommendation: demote to `seen`, or amend section 2c to define
   a tier meaning "dispositioned but not yet mined."
2. **`value` == `provenance` == `citation`, byte-identical, on 46/46
   (`citation`==`provenance`) and 45/46 (`citation`==`value`) papers
   store-wide** -- the "one value restated" defect CLAUDE.md's standing
   rule warns against, reproduced inside a single row. F10 notes this
   independently corroborates (and predates, in terms of when the defect
   was introduced) the same `citation`/`provenance` duplication Sprint 3
   Task B (F6 finding 1) already fixed at the EXPORT layer -- F10's
   finding is that the STORE still writes both columns from the same
   source string at insert time, which Task B's fix did not change
   (Task B changed what the export reads, not what `insert_paper` writes
   to `paper_fields.citation`).
3. Additionally noted: citations are hand-typed against ADR-0005's
   explicit "pulled from an API, never hand-typed" rule, which F10
   argues is the direct cause of the wrong-title/dropped-author/wrong-year
   defects found above; the `ml` context unused across 46 papers (same
   finding F9 made independently); and a `world`-context test being
   applied inconsistently (`arute`'s contested supremacy claim and
   `rand`'s CISA policy report both claimed `world`, while `zajac`'s
   actual mathematical theorem -- the one record that fits `world`'s own
   "true independent of any project: mathematics, physics" definition --
   did not).

**F10's recommended sequence** (not actioned this sprint; recorded for
F11/future sprint scoping): (1) mechanize citation refresh against
arXiv/Crossref/DataCite APIs; (2) resolve the `value`/`provenance`/
`citation` triplication at the store-write layer, not just the export
layer; (3) settle the `screened`-tier question as a dated ADR amendment;
(4) a deliberate `world`/`method`/`ml` re-filing pass across all 46
papers; (5) promote `loke`/`emami`/`qci-2024`/`mancilla` to `read` and
extract assertions, specifically to wire the `contradicts` relation F10
identifies between `mancilla`/`zajac` (tabular QML advantage is
structurally near-impossible) and `emami`/`loke`/`qci-2024` (CVQBoost
beats XGBoost on tabular fraud data) -- both papers are already in the
store; only the extraction and the `assertion_relations` row are
missing.

## Cross-review observations (for F11 to weigh)

- **Confirmation rate alone does not separate the tiers**: F7 and F8 both
  reached 18/18 confirm with zero rejections; the actual defects (F10)
  and inconsistencies (F9) exist regardless. A future record-adjudication
  process that only measures "did the reviewer confirm or reject" would
  not have caught most of what F9 and F10 found.
- **Depth correlates with method, not obviously with model tier alone**:
  F9 and F10's designs (compare across the set; verify against primary
  sources) surfaced substantially more than F7/F8's designs (per-record
  internal consistency). Whether that's a tier effect or a protocol
  effect is exactly the question F11's design should isolate if a future
  sprint revisits this comparison.
- **No factual disagreement was found between F9 and F10's independent
  findings** where their scopes overlapped (e.g. both independently flagged
  the `qci-2024-profiling-cvqboost` rationale as the weakest of the
  CVQBoost cluster, and both independently flagged `mancilla`/`emami`-
  cluster's latent `contradicts` relationship) -- despite having zero
  visibility into each other's work. This convergence from independent
  starting points is itself a data point worth weighing at F11.

## Disposition of these findings

Per `SPRINT_3_PLAN.md`'s own Definition of Done, F7-F10's job was to
"produce a complete, independent review... ready for a future sprint's
F11 to compare against team-lead timing" -- not to action every finding
immediately. This document preserves that record. The findings above are
NOT actioned in Sprint 3; they are backlog input for a future sprint's
own selection (see `docs/ALL_SPRINTS_MASTER_PLAN.md` for the resulting
candidate items).

**2026-09-19 update**: the four candidate items first drafted from these
findings (F21-F24) were consolidated, together with F12 (paper/reference
intake workflow), into a single card, **F25**, at the team lead's
direction -- findings ordered Fable, Opus, Sonnet, Haiku; work ordered by
dependency; covering both correction of the existing records and the
ingestion guards that make the next paper right on the first try. F21-F24
and F12 remain in the master plan as one-line "superseded" stubs so
references here still resolve.
