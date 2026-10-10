# Sprint 6 Summary: Decide the Fields Once, Then Load at Scale

**Dates**: 2026-09-27 to 2026-10-05. **Branch**: `feature/20260927_Sprint_6`.
**PR**: #54. **Issues**: #55 to #66 (Tasks A to L), all closed. Sources: the
plan (`SPRINT_6_PLAN.md`), `git log`, the issues, the retrospective
(`SPRINT_6_RETROSPECTIVE.md`). Every count below is a snapshot as of
2026-10-05.

## What shipped

- **F40, the first release of F39 (Task A, #55).** Every model tier in
  `.claude/model_assignment_heuristics.json` names a model verified against
  Anthropic's models page that day (id, price, context, retirement date,
  date checked); the role table matches; a test fails on a tier with no
  verification date.
- **F38 (Task B, #56).** `CHECKLIST-Phase2-pre.md` back-filled for Sprints 1
  to 4: 45 rows checked with a verified commit, 5 left unchecked with the
  reason.
- **F43 (Task C, #57).** INTAKE_WORKFLOW section 15, "assert the table, not
  the summary", with two worked examples.
- **The amendment (Task D, #58): F34, F36, F37, F47.** ADR-0004 A6
  (`derivation`, `claim_type`, the synthesis cap and the retraction floor,
  both computed) and ADR-0005 A4 (`publication_status`, the ten reference
  fields and the probe rule, the `read` gate, the admission-against-interest
  rule). Both accepted at Manual Validation.
- **The migration (Task E, #59).** Schema, door, export and rebuild agree;
  the export rebuilds byte-identically; derived keys are never written back.
  A fresh-eyes review found four defects; all fixed with tests.
- **F36 back-fill (Task F, #60).** `found_via` on every paper, `cited_as` on
  121, `metadata_provider` on 249 (named or marked inferred), `read_extent`
  for every `read` paper; `coi` and reading depth below `read` queued, not
  guessed. Computed fields piloted on 30 records, then probed for the 361
  original papers.
- **F41 without the CVQBoost findings (Task G, #61).** 11 sources (10 Cyc
  and repository sources plus the hsbc hardware plan, pinned at `a6c3453`)
  and 35 assertions; decision 3's two certainty changes. The CVQBoost part
  waits as F51.
- **F42 (Task H, #62).** The two Cyc research documents in `docs/research/`
  and the dated amendment to `cyc-knowledge-representation.md`.
- **F33 (Task I, #63).** Six withdrawn arXiv preprints (status from arXiv's
  `/pdf` 404 signature, the comment as the reason) and one retracted article
  (Crossref notice `10.1007/s00500-026-11351-6`); two `superseded-by` links.
- **F32 (Task J, #64).** 1,402 of 1,403 QMLPapers papers loaded at `seen`
  (one malformed id refused), each with its route and the collection's own
  citation line.
- **F35 (Task K, #65).** GitHub token support (never logged); 105 of 135
  repository notes linked to their papers by `code-of`, 30 reported.
- **Q11 (Task L, #66).** `du-2024` refreshed to its Scientific Reports
  publication.
- **Manual Validation follow-up.** The hsbc Phase 1 results memo entered as
  a source, with two `platform:dirac-3` assertions on solver fidelity and
  its limit. Cards F52 to F57.

Store: 361 -> 1,875 papers; 23 -> 60 assertions. Suite: 506 -> 572.

## Actuals

Wall clock is commit-to-commit from `git log` (local time). Plan estimate:
about 700 Claude-side minutes plus Task J's runtime (82 min to 10 h).

- Plan approved and recorded 2026-10-03 20:11 (0044a44). Tasks A to C had
  been worked before their commits at 20:14 to 20:17.
- Tasks D to H, K's code and the probes: 20:26 to 21:22 on 2026-10-03.
- Task J: from about 21:30 on 2026-10-03 to 02:31 on 2026-10-04, including a
  stop and restart and the team lead's two-hour arXiv pause (00:05 to 02:15).
- Task I: after a second two-hour pause, 04:30 to 04:37 on 2026-10-04.
- Phase 5 fixes: 04:44 on 2026-10-04. **Execution span: about 8.5 hours**,
  about 4 of them pauses.
- Manual Validation, follow-up and retrospective: 2026-10-05.
- Delegated agents: two fresh-eyes code reviews, 96,070 tokens / 160 s
  (Task E) and 82,674 tokens / 135 s (Phase 5). Read-only; every finding
  verified before it was fixed.

## Findings surfaced

- **arXiv pacing was never applied between intake entries** (since Sprint 4,
  64d067f): `intake.py` built a new pacer per entry and a new pacer never
  waited. It most likely caused the 2026-10-03 429s, and it broke the team
  lead's 6 s instruction once (684 requests in 10 minutes). Fixed, then
  prevented at the source (retrospective I1: one process-wide clock).
- A timeout, an HTML body or a connection reset from arXiv skipped the
  DataCite fallback; now every arXiv failure reaches DataCite.
- Four of the six withdrawn preprints' comments never say "withdrawn"; the
  `/pdf` 404 signature is the source of truth.
- `parse_access` read `github.com/<owner>/arXiv-2502.18361-...` as an arXiv
  id; fixed.
- The hsbc Dirac-3 runs show the device matched the exact classical optimum
  on the Phase 1 formulation, which the same memo calls near-trivial.

## Commit references corrected

Two commit subjects name the wrong issue (recorded here, since history is
not rewritten; retrospective category 13): 39b179e says #63 for Task H,
which is #62; 32a6deb says #62 for Task G, which is #61. Since
retrospective I3, a hook checks task issue numbers against
`sprint_status.json`.

## Verification

- Suite 572 passed at the retrospective-improvements commit (eeb2e46).
- The committed export rebuilds byte-identically
  (`tests/test_store_durability.py`), with every new field populated in a
  separate round-trip test.
- `gh issue list --label sprint --state open`: empty.
