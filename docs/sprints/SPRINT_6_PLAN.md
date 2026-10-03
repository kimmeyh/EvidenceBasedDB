# Sprint 6 Plan: Decide the Fields Once, Then Load at Scale

**Dates**: from 2026-10-03. **No deadline.**
**Branch**: `feature/20260927_Sprint_6` (cut at the Phase 6.6/8.2
carry-forward from Sprint 5's branch, 2026-09-27)
**Scope** (DEFINED, team lead 2026-10-03), in the team lead's order: F40,
F38, F43, F34, F36, F37, F47, F41, F42, F32, F33, F35. Priorities as
proposed at 1.4 (F34 16, F36 18, F37 20, F33 22, F35 24). Q3 = 1: F32
includes the bulk load. Q4: the CVQBoost findings are NOT entered this
sprint ("it will be updated after the next hsbc repo sprint (the
experiement will be re-run) and then it can be referenced").

## Objective

Sprint 5 filled the store to 347 papers and showed what the records cannot
yet say: whether a source was withdrawn or retracted, how it was found, how
much of it was read, whether an assertion is extracted or synthesized. This
sprint decides those fields ONCE, in one dated amendment to ADR-0004 and
ADR-0005, migrates the store to them, and only then loads at scale: the
Cyc and Fourier Wall package (11 sources, 35 assertions), the withdrawn and
retracted papers, about 1,410 QML papers, and the 135 code repositories
attached to their papers. Around that: the first release of the permanent
model-evaluation item, and two small process fixes.

## Tasks

Est is coordinator time for the judgment steps (Sprint 5 calibration:
coordinator estimates overstated agent- and background-carried work 4-7x).
Runtime is separate, with its dominant term. Model assignments follow
`.claude/model_assignment_heuristics.json` as of 2026-10-03; **Task A (F40)
runs first and may revise them**. Every task that changes `store/`, a hook,
the door or a recovery path gets a fresh-eyes reviewer launched at its
commit (Sprint 5 improvement 5), and one review-and-fix cycle in its
estimate.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F40 -- first release of F39.** List the models available, verified against Anthropic's models page that day (pre-flight: it moved to `platform.claude.com`); record per tier the model id, version, price, context, retirement date and the date checked; act on what changed (Sonnet 5.5 is current while the heuristics and the SPRINT_PLANNING.md role table name Sonnet 5 and "Fable 5"; **Haiku 4.5 retires not sooner than 2026-10-15**, so the Developers tier needs a decision); re-read `learning_log`; update tiers, patterns, triggers and the role table with evidence; a test fails when a tier lacks a verification date or names a model the page does not list | 45m | about 5 min (pages) | Claude, top tier |
| B | **F38 -- checklist back-fill.** Sprint 1 rows checked with the commit or document that proves each; Sprints 2-4 sections added the same way | 30m | none | Sonnet subagent (evidence), Claude review |
| C | **F43 -- assert the table, not the summary.** One dated paragraph in `INTAKE_WORKFLOW.md` with the two worked examples (the CVQBoost findings' "3-8x" against ratios 83, 7.6, 8.2, 1.7; the hardware plan's "superlinear" against a fitted exponent of 0.75). Lands before Task G writes assertions | 20m | none | Claude |
| D | **F34 + F36 + F37 + F47 -- the amendment, written.** Per decisions Q1-Q7 below: dated amendments at the bottom of ADR-0004 (assertion fields: `derivation`, and `claim_type` if Q5 = 1) and ADR-0005 (publication status, the ten reference fields, the read-tier vocabulary and cost per Q7, the admission-against-interest rule). Text reviewed at Manual Validation, presented as name, what changed and why, quoted language | 90m | none | Claude, top tier (ADR) |
| E | **The migration.** `store/schema.sql` and a dry-run-by-default migration script (verified backup first) for the stored fields; the door validates them (`set_tier` refuses `grep`, `subagent`, `summary` at `read`); `store/export.py` emits them; **`store/rebuild.py` `KNOWN_KEYS`, `_paper_from_export` and the assertion path learn every new key in the same commit**, or the CI rebuild test fails; `learnings.py` reads `derivation` instead of the provenance string; the F47 test (every `certainty_reasons` naming the upgrade names its cost); computed fields as resolvers, not columns | 150m | under 1 min (347 records) | Claude, top tier; fresh-eyes review at commit |
| F | **F36 back-fill.** Stored fields from what the store already holds: `found_via` from dispositions ("Bulk intake ... [TAG]", "F5's QCi author search (<person>, <rule>)", the Sprint 1 seed note), `metadata_provider` from `updated_reason`, `cited_as` for the 121 bibliography records from the preserved `BIBLIOGRAPHY.md`; judgment fields (`read_extent`, disclosed `coi`) QUEUED, never guessed. Computed fields: PILOT on 30 records across source types before any full run | 60m | `[unbounded]` until the pilot: registry lookups about 1 s each, publisher-page probes up to 30 s with 403s; full run sized from the pilot, heartbeat file if over 30 min | Claude; Sonnet subagent for the queue report |
| G | **F41 -- the Cyc and Fourier Wall package, without the CVQBoost findings.** Intake section 15 appended first (the handoff's `01`, dated); manifest of the 10 Cyc and repository sources (pre-flight: 10 planned, 0 refused) plus the hardware-plan record (decision 4.2: hand-origin `Reference:`, `access` the hsbc repository's `docs/HARDWARE_PLAN_PHASE_2.md`, pinned at `a6c3453`, which matched the working copy at planning; applicability `hsbc-2026` and `platform:dirac-3`); the sprint script with the 6 CVQBoost assertions removed (35 remain; pre-flight: none of them relates to a removed one), the three hardware-plan assertions yielding the new record, decision 3 (two certainty changes via `append_updated_reason`), decision 4.1's `method` row on the Fourier Wall record only; every new record and assertion carries the Task E fields | 75m | about 1 min (GitHub with token, hand records) | Claude, top tier (certainty) |
| H | **F42 -- the two Cyc research documents** into `docs/research/` with F42 in their names and links, the review's session-file links turned into record ids, "Generalisation" fixed; the dated amendment appended to `cyc-knowledge-representation.md` | 30m | none | Claude |
| I | **F33 -- withdrawn and retracted, discoverable both ways.** Pre-flight corrected the card twice: the six withdrawn ids are in `QMLPapers/<year>/failed-downloads.txt`, not in any `manifest.tsv` (so the bulk load would never have reached them; this task creates their records), and the journal retraction IS discoverable through Crossref: notice `10.1007/s00500-026-11351-6`, type `retraction`, dated 2026-03-10, found with the `updates:` filter. Records at `seen` with publication status per Q1, the reason from arXiv's comment, the two `superseded-by` links per Q1 | 60m | about 1 min (7 lookups) | Claude |
| J | **F32 -- manifest and bulk load.** Generator over the 12 arXiv-bearing TSVs (1,436 rows; `NonArxiv` routed to the DOI or hand path), writing to the folder per Q9, excluding Task I's ids; every entry carries the Task E fields (`found_via` "QMLPapers/<year>/manifest.tsv"); dry run per Q8; load with a heartbeat file | 60m | **82 min per pass at 3.5 s per id if arXiv keeps answering (0.5 s measured on 2026-10-03), about 5 h per pass under the Sprint 5 refusal (13 s per id)**; arXiv lookups dominate | Claude; background run |
| K | **F35 -- the 135 repositories.** `store/citations.py` reads a GitHub token from the environment (never logged; pre-flight: the `gh` token gives 5,000 requests per hour against 60), with a test; each note's repository through the GitHub path, attached to its paper by a `code-of` source link carrying the note's quoted evidence sentence; a wrong attachment removable without touching the paper | 75m | under 5 min with the token | Claude; fresh-eyes review at commit (citations.py) |

**Sequence**: A first (the assignments below may change with it); B and C
(C before G); D then E then F (the amendment decided, then migrated, then
back-filled); G and H; I; J; K (K needs J's papers). All arXiv traffic stays
serial across tasks and agents (Sprint 5 rule).

**Total about 700 minutes of coordinator time** plus Task J's runtime (82
min to 10 h, see above) and Task F's pilot-sized runtime. Calibrated against
Sprint 5's actuals; the review-and-fix cycles are inside E and K. **If a
Criterion 3 stop becomes necessary, the cut line is before J and K**: the
bulk load and the repositories move to Sprint 7 as a unit, nothing else
depends on them. Deferring approved work is a Class 3 decision and is never
made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **arXiv, the exact request Task J sends** (`citations.fetch_arxiv_batch`,
  one id): answered by arXiv's own API in 0.5 s on 2026-10-03, no DataCite
  fallback. One request is not a sustained run; Task J is sized both ways.
- **Withdrawn arXiv PDF**: `arxiv.org/pdf/2308.08167` returns HTTP 404, as
  F33 states.
- **F33's ids**: all six withdrawn ids are in `failed-downloads.txt`
  (2023: 2; 2024: 3; 2025: 1), none in a `manifest.tsv`.
- **Crossref, the retraction**: the article's own record says "RETRACTED
  ARTICLE" in its title but carries no `update-to`; the retraction notice
  `10.1007/s00500-026-11351-6` (type `retraction`, 2026-03-10) points at
  it and is returned by `works?filter=updates:<doi>`.
- **F41's manifest without the CVQBoost entry**: `intake.py --manifest`
  dry run, 10 planned, 0 already present, 0 refused (the new hollow-page
  check passed on the five `References` copies).
- **F41's script**: no surviving assertion `supports` or `contradicts` one
  of the six CVQBoost assertions (all relations target records already in
  the store); the promotions write applicability before `set_tier`, so
  Sprint 5's improvement 1 does not refuse them.
- **The hardware plan**: last commit `a6c3453` on
  `docs/HARDWARE_PLAN_PHASE_2.md`, working copy unmodified (read-only on the
  sibling repository).
- **GitHub**: `gh` is logged in; with its token `api.github.com/rate_limit`
  reports a core limit of 5,000 per hour.
- **Anthropic's models page**: reachable at
  `platform.claude.com/docs/en/about-claude/models/overview` (301 from
  docs.anthropic.com).
- **Plan-to-branch verification** (3.2.2.1): none of the Task D-K artifacts
  exists yet; `INTAKE_WORKFLOW.md` ends at section 14, so the handoff's
  section 15 is next; `rebuild.py`'s `KNOWN_KEYS` lists the current export
  keys only; the store holds 347 papers and 23 assertions; suite 506 passed
  on this branch.
- **Phase 2 gates**: PR #43 merged to develop and PR #53 to main; no open
  sprint issues or PRs; tree clean. Dependency scan not applicable (standard
  library and pytest only).

## Decisions for the team lead at approval (numbered; answer with digits)

The amendment (Task D) is Class 1 and ADR-first, and the auto-advance
window forbids asking later, so its substance is decided here; its text is
reviewed at Manual Validation.

- **Q1. How a withdrawn or retracted source is represented (F34).**
  (1) A `publication_status` field on the paper record (`published |
  preprint | withdrawn | retracted`), computed from the registry where one
  answers (arXiv comment and PDF status; Crossref `updates:` notices) and
  stored with an anchor for hand-origin records; "superseded by" as a
  `superseded-by` source link (F36 field 6); (2) a context; (3) a
  certainty input only, with no field. Recommend 1: status is a fact about
  the source, contexts partition claims (ADR-0004 section 3b), and a
  certainty input alone would hide the status from every query.
- **Q2. What a retraction does to certainty.** (1) An assertion whose only
  yielding sources are withdrawn or retracted is computed to `very-low`
  with the named reason, visibly, in the export; (2) a flag a human weighs,
  certainty unchanged. Recommend 1: GRADE treats a retracted study as
  unusable, and computing it keeps the reason visible.
- **Q3. The ten F36 fields as carded** (four computed: `publication_status`,
  `version_of`, `access_status`, affiliations; six stored: `found_via`,
  `read_extent`, `source_links`, disclosed `coi`, `cited_as`,
  `metadata_provider`), with `read_extent` gaining `grep` and `subagent`
  and `set_tier` refusing `grep`, `subagent` and `summary` at `read`.
  (1) Yes; (2) No, I will name changes. Recommend 1.
- **Q4. F37: `derivation: extracted | synthesized | project`, and a
  synthesized assertion's certainty capped at its weakest input** (Cyc's
  `strength_combine` rule). (1) Yes, with the cap; (2) Yes, without the
  cap (reasons only). Recommend 1.
- **Q5. `claim_type` (positive, absence, vendor self-claim) in this same
  amendment.** (1) Yes, so the assertion fields change once; (2) No, card
  it separately. Recommend 1.
- **Q6. F47's rule as carded**: the admission-against-interest upgrade
  applies only when the claim costs its author something, and a test
  checks every `certainty_reasons` naming the upgrade also names that
  cost. (1) Yes; (2) No, I will reword. Recommend 1.
- **Q7. The ADR-0005 A2 divergence found at Phase 1.3**: A2's tier table
  puts `read`'s cost on the team lead, but `read` has been reached twice on
  Claude's direct reading (Sprint 4 Task H, Sprint 5 pilot), both accepted.
  (1) Amend A2: `read` may be reached on Claude's direct reading, recorded
  in `checked_against_source` with `read_extent` `full` or `partial`; the
  team lead adjudicates learnings and any record they choose; (2) Keep A2:
  future promotions to `read` need the team lead. Recommend 1: it states
  the practice you have accepted twice, instead of leaving the ADR wrong.
- **Q8. Task J's dry run.** (1) A stratified sample (10 per year folder,
  about 120) read in full, then one full `--apply` in the background with a
  heartbeat file; (2) a full dry run and a full apply. Recommend 1: the
  door refetches on `--apply`, so a full dry run doubles the runtime; the
  sample still exercises every folder, and the apply reports every refusal.
  What it gives up: a refusal outside the sample is found during the apply,
  not before it (the apply commits per entry, so nothing is half-written).
- **Q9. Where Task J's manifest goes.** (1) `manifests/`, committed, so
  the load is reproducible; (2) `export/`; (3) the scratchpad, not
  committed. Recommend 1: `export/` holds the store's outputs.
- **Q10. The CVQBoost remainder.** The findings record, its six assertions
  and decision 4.1's `method` row would vanish when F41 is pruned. (1) Card
  them as F51, HOLD until the hsbc re-run; (2) No card. Recommend 1.
- **Q11. The one citation the Phase 1.3 refresh found out of date**
  (`du-2024`, now published in Scientific Reports, DOI
  `10.1038/s41598-025-14754-x`). It is not in the selected scope. (1) Add
  it: `refresh_citations.py --ids du-2024-... --apply`, about 5 minutes;
  (2) Leave it for Sprint 7's Phase 1.3. Recommend 1.

## Premise falsifier

**The premises**: (a) the amendment's fields can be added to a store of
347 papers, and the store still rebuilds byte-identically from its export;
(b) about 1,410 bulk records enter through the one door with almost no
refusals; (c) the handoff package applies as tested on 2026-09-30, minus
the CVQBoost part; (d) the model heuristics can be stated as verified
facts, not roles.

**What would disprove each**: (a) after Task E, `rebuild_store_from_export.py`
reports a difference, or the CI rebuild test fails on an unknown key: the
export is no longer a complete artifact, which stops Task J; (b) Task J
refuses more than 1% for a reason that is not a defect in the entry: the
door was shaped to smaller sets; (c) Task G's `PRAGMA foreign_key_check`
returns a row, or an assertion's context is outside its source's
applicability without a stated convention; (d) Task A finds a tier whose
model no current page lists: the assignment table was pointing at nothing.

**The checks cannot merely confirm**: the rebuild compares bytes from a
fresh temporary store; the rebuild test's injection (an unknown key) is
extended to the new fields; the bulk apply reports every refusal with its
reason; the F40 test is proven by injecting a tier with no verification
date.

## Risks

| Risk | Mitigation |
|---|---|
| The migration touches every paper row and the export format | Dry-run-by-default migration, verified backup first, byte-identity rebuild as the gate, fresh-eyes review at the commit |
| arXiv refuses a sustained run again | Serial traffic; the door's DataCite fallback; Task J sized both ways; heartbeat file; per-entry commits so a stop loses nothing |
| Volume without judgment: about 1,600 new `seen` records | `found_via` and the disposition say where each came from and that it is unscreened; screening stays per cluster |
| The bulk load enters records before their fields exist | Sequence: D, E before J; J's generator emits the new fields |
| The handoff package was tested on 2026-09-30, before Sprint 5's improvements | Every script runs dry first and is read; Task G's acceptance is the FK check and the suite |
| Writing to a sibling repository | Read-only on hsbc; the hook enforces; the hardware plan is pinned by commit, not copied |
| Haiku 4.5 may retire from 2026-10-15 | Task A runs first and decides the Developers tier |
| Team-lead adjudication cost (ADR-0004's constraint) | No record is promoted to `read` this sprint except Task G's three, which the handoff read and Q7 governs |
| Session continuity across a long, runtime-heavy sprint | `sprint_status.json` note written at every task boundary |

## Definition of Done

- A: each tier names a verified model with id, price, context, retirement
  and date checked; the role table matches; the test fails on a missing
  date (proven by injection)
- B: every checklist row for Sprints 1-4 cites evidence
- C: the dated paragraph with both worked examples
- D: dated amendments at the bottom of ADR-0004 and ADR-0005 per Q1-Q7,
  none an edit in place
- E: schema, door, export and rebuild agree; the rebuild is byte-identical
  after the migration; every new guard proven to fail by injection; the
  fresh-eyes review's findings fixed with tests
- F: stored fields back-filled from existing text; judgment fields queued;
  computed fields piloted and sized
- G: 11 sources and 35 assertions in, FK check clean, the suite passes, the
  CVQBoost part left out and accounted for (Q10)
- H: both documents present, no `Fxx`, the amendment appended
- I: 7 records with status, reason and source of truth; the two
  superseded-by links; a query lists them
- J: the bulk records in at `seen` with their fields; refusals listed with
  reasons
- K: each of the 135 resolved to a live repository and attached, or
  reported; the token never appears in output or logs
- Full suite green before every commit, gated on pytest's own exit code

## Out of scope

The CVQBoost findings record and its six assertions (Q4; Q10 cards them).
F44, F45, F46, F48, F49, F50 (not selected). Screening any new record.
Any write to `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
