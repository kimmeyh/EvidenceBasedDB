# Sprint 3 Plan: Correct the Foundations, Then Measure Adjudication

**Dates**: from 2026-09-18. **No deadline.**
**Branch**: `feature/20260918_Sprint_3` (cut at Phase 6.6 carry-forward from
Sprint 2's own branch)
**Scope** (DEFINED, team lead 2026-09-18): **F2** (spamfilter-multi deep-dive,
Phase 1 only), **F6** (six remaining PR #1 code-review findings), **F13**
(US English spelling guard), **F14** (harden one-off data-correction
scripts) -- run first, in that stated order -- then **F7**, **F8**, **F9**,
**F10** (adversarial record-adjudication review, one card per model tier:
Haiku, Sonnet, Opus, Fable) -- run second, independently and in parallel
with each other.

## Objective

Sprint 2 left four corrections/hardening items on the backlog and designed
four independent model-tier reviews to replace its own deferred
adjudication-timing measurement. Team lead, 2026-09-18: fix the foundations
first ("I believe these need to be done first so that the items are
corrected before starting F7-F10"), then run the four reviews -- which are
explicitly NOT a pipeline: "they should not be designed to depend on each
other. They are independent reviews to see how each of them will do the
review and what they will find." F11 (the team-lead-timed comparison
against all four reviews) is NOT in this sprint's scope; it depends on
F7-F10 completing and is sequenced for a future sprint's own selection.

## Why this order

F2, F6, F13, and F14 do not touch F7-F10's own inputs (the ~18-20
screened-tier records under review) in a way that would change what those
reviewers see -- F6's six findings are code/schema/refactor questions in
`store/ingest.py` and `store/export.py`, not record-content rewrites, and
F2/F13/F14 do not touch the store at all. The team lead's stated reason for
sequencing them first is that these are corrections that should land BEFORE
F7-F10 run, not a technical blocking dependency; this plan follows that
instruction as given rather than second-guessing it, and records the
distinction here so a future reader understands why the sequence is
team-lead judgement, not a schema-level gate.

## Tasks

| # | Task | Est | Owner |
|---|---|---|---|
| A | F2 Phase 1: survey `spamfilter-multi` (read-only) across every named candidate area and produce one drafted sprint card (or shared card for a tightly coupled cluster) per adopt/adopt-with-rework candidate, ordered by dependency | large, no-history | Claude (top tier -- backlog refinement is a mandatory top-tier activity) |
| B | F6: address the five actionable PR #1 findings (redundant citation storage, unenforced tier/checked_against_source validation, no per-record transaction boundaries, duplicated path-resolution boilerplate, duplicated export-function shape). Finding 4 (export N+1 queries) stays explicitly deferred as premature at this scale | unknown, no-history | Claude |
| C | F13: port `hsbc-quantum-fraud-2026`'s `us_english_fix.py`/`test_us_english.py` pair (read-only source), adapted for span-level protection of verbatim paper/book quotations rather than whole-file exclusion; resolve the citation-fields-in-exports scope question the card itself raises before building | small, no-history | Claude |
| D | F14: harden `apply_paper_applicability.py` against the two silent-failure findings from Sprint 2's own PR review (typo'd id silently skipped; partial-state re-run silently incomplete) | small, no-history | Claude |
| E | F7: Haiku adversarial review of the ~18-20 screened-tier records, forced-quotation protocol (confirm/reject citation, primary context, applicability rationale; each confirmation cites the exact source sentence) | unknown, no-history | Claude (Haiku subagent) |
| F | F8: Sonnet adversarial review of the SAME record set, independently -- same fields as F7 plus certainty/certainty_reasons/fidelity, checking whether stated reasons actually justify the level chosen | unknown, no-history | Claude (Sonnet subagent) |
| G | F9: Opus adversarial review of the SAME record set, independently -- cross-record consistency (same kind of judgement call made differently across records), not per-record correctness | unknown, no-history | Claude (Opus, top tier) |
| H | F10: Fable adversarial review of the SAME record set, independently -- a full accept/reject/revise pass across every field, same shape as F7/F8/F9 rather than a disagreement-adjudicator over their output | unknown, no-history | Claude (Fable, top tier) |

**Sequence**: Tasks A-D run first, in the stated order (A, B, C, D), per
team-lead instruction. Tasks E-H run second, ALL FOUR IN PARALLEL against
the identical record set -- no reviewer sees another's output, so the
model-tier comparison this backlog item exists to produce is not biased by
review order. F11 (comparing all four outputs against team-lead timing) is
explicitly out of scope for this sprint.

**Total effort**: F2 (large), F6/F7/F8/F9/F10 (unknown, no-history), F13/F14
(small) -- no calibrated total exists yet for this combination; each
no-history item gets a timebox at kickoff per `docs/SPRINT_PLANNING.md`'s
own Estimation section rather than a guessed total.

## Premise falsifier

**The premise**: fixing the four foundational items first, then running
four fully independent model-tier reviews, produces a fair, comparable
measurement of how each tier reviews the same record set -- one this
project can actually use to decide whether model-based review can
substitute for team-lead adjudication (F11's eventual job).

**What would disprove it**: (1) F6's changes to `store/ingest.py` or
`store/export.py` turn out to alter record VALUES (not just code
structure) in a way that changes what F7-F10 would see -- if this happens,
F6 must complete and the export must be regenerated and diffed BEFORE E-H
start, not run concurrently with them; (2) any of F7-F10's reviews is
run with visibility into another's output (a shared conversation, a
shared scratch file, a prompt that references "what Haiku already
found") -- this would silently reintroduce the sequential-dependency
design the team lead explicitly rejected, and the resulting comparison
would be worthless without anyone noticing until F11 tries to use it.

**The check cannot merely confirm**: before starting Tasks E-H, diff
`export/*.json` against Task B's own pre-change state and confirm zero
record-VALUE changes (schema/code changes are fine; content changes are
not). Each of F7-F10 must be launched from a state with no memory of the
others' output -- a fresh session or subagent per review, not the same
conversation running all four in sequence with context carried forward.

## Risks

| Risk | Mitigation |
|---|---|
| F6's "moderate-scope design or refactor question" findings turn out larger than estimated once actually scoped | Named `unknown, no-history`; re-estimate after the plan-to-branch-state verification findings, per `SPRINT_PLANNING.md` workflow 3.2.2.1/3.2.2.2 |
| F2 Phase 1 produces MORE cards than a single future sprint can hold | Explicitly Phase 1's own risk to surface, not resolve -- the team lead selects from the drafted cards at a future refinement, same as any other backlog slate |
| F7-F10 accidentally run with cross-visibility (the exact failure the premise falsifier names) | Each review runs as its own fresh session or subagent invocation with no shared context; verified before declaring the four reviews complete |
| F13's citation-fields-in-exports scope question (raised by the card itself) is decided wrong, either testing generated output or missing real prose drift | Task C resolves this explicitly as part of scoping, before building the guard, per the card's own "needs a decision this card should make explicit, not assume" |
| F14's fix changes `apply_paper_applicability.py`'s exit-code contract in a way nothing else expects | Script is one-off and already fully run against the live store; re-running it after the fix is a no-op verification step (0 applied, 0 skipped, exit 0), not a live risk |

## Definition of Done

- F2 Phase 1 complete: a survey finding per named candidate area, and one
  drafted sprint card per adopt/adopt-with-rework candidate, ordered by
  dependency, presented for team-lead review. Phase 2 (execution) is
  explicitly NOT part of this sprint's Definition of Done
- F6's five actionable findings fixed with regression tests; Finding 4
  stays recorded as deferred, not silently dropped
- F13's guard exists, passing, verified by injection (a British spelling
  introduced into a tracked doc fails the guard; a verbatim source
  quotation containing one does not)
- F14's two findings fixed; `apply_paper_applicability.py` re-run against
  the live store confirms a clean no-op (0 applied, 0 skipped that
  should not be, exit 0)
- F7, F8, F9, F10 each produce a complete, independent review of the same
  record set, with zero cross-visibility between them, ready for a future
  sprint's F11 to compare against team-lead timing
- Full test suite green before every commit; every fix verified by
  injection per this repository's own guard-discipline standard

## Out of scope

**F11** (team-lead adjudication timing, compared against F7-F10) --
explicitly sequenced for a future sprint, after this sprint's F7-F10
outputs exist to compare against. **F5** (QCi deep-dive) -- not selected
this sprint. **F12** (paper/reference intake workflow) -- not selected
this sprint. Any change to the consumer repository (`hsbc-quantum-fraud-
2026`) or `spamfilter-multi` beyond read-only research for F2.
