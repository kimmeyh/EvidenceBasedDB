# Sprint 10 Plan: Fix the Hooks and the Dirac Records, Then Read the Next 74

**Dates**: from 2026-10-18. **No deadline.**
**Branch**: `feature/20261018_Sprint_10` (cut at the Phase 6.6 carry-forward
from Sprint 9's branch, 2026-10-18, after PR #88 merged to develop and PR
#100 to main)
**Scope** (DEFINED, team lead 2026-10-18): F39, F57, F50, F81, F82, F83,
F84, F85, F86, F87. F39 and F57 are permanent, so each is released as a
copy with the next free number: F88 (F39 release for Sprint 10) and F89
(F57 release for Sprint 10, 74 records). F51 stays HOLD and is not in
scope.

## Objective

Clear the whole non-HOLD backlog in one sprint. First fix the code-edit
hook that blocks read-only commands (it blocked one during this sprint's
planning), and log Sprint 9's reader outcomes so this sprint's readers
work under the corrected rules. Then correct the nine Dirac-1 records,
enter Phase 2's Dirac-3S verification, close the Zenodo re-check, decide
the never-write hook's threat model, and source the optimization bounds
the answer document states without a source. Then read the next 74
records for claims, and tighten the discovery filters last.

## Tasks

Est is coordinator time for the judgment steps, calibrated from Sprint 9's
`## Actuals`: 780 estimated minutes ran in 291 (about 37 percent); small
code and document tasks took about 15 percent of their card estimate,
reading tasks about 40 percent, and reviews set the end of the reading
tasks. The card estimates are cut on those ratios, and each task that
changes `store/`, `scripts/` or a hook carries one fresh-eyes review and
fix cycle in its estimate. Runtime is separate, with its dominant term.
Models follow `.claude/model_assignment_heuristics.json`.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F81, the code-edit hook's false block.** `_shell_edits_code` in `.claude/hooks/block_unraw_escape.py` searches for an in-place flag over the whole rest of the command, past `;`, `&&`, `\|\|` and `\|`, so `sed -n 1,5p store/recheck.py; grep -i foo README.md` reads as `sed -i` and is blocked (reproduced at planning, 2026-10-18: the live hook blocked that read and named the hook file itself as a target). The flag search and the target search stop at the end of the tool's own command segment. Tests call `_shell_edits_code` directly: the two blocked read shapes pass; `sed -i` on a code file, alone and after a `;`, is still blocked; each proven by injection | 15m | none | Claude, top tier (security-relevant hook) |
| B | **F88, F39 release for Sprint 10: models and heuristics.** The models available here listed with id, version and release date from Anthropic's models and pricing pages on the day, never from memory; changes since F67 (2026-10-12) recorded. Sprint 9's outcomes logged as `learning_log` rows from `SPRINT_9_SUMMARY.md` and its review records: Sonnet 5.5 first-pass readers (F78 and F80) were accurate on quotes and numbers, and their main defect was adding conclusions the source does not state; fresh-eyes reviews found defects in every structural task. Reader task patterns tightened where that evidence supports it; `SPRINT_PLANNING.md`'s role table kept in step; a test guards what the release adds, proven by injection | 30m | about 1 min (two documentation pages) | Claude, top tier (mandatory: model assignment) |
| C | **F50, "compute, never store" qualified.** A dated amendment to `docs/research/cyc-knowledge-representation.md` point 7 ("Look facts up rather than storing them where a lookup is reliable"): Cyc stores a count at every index layer beside its data and updates both together (`removal_modules_lookup.java`, line 84, already cited by the Sprint 6 amendment); a stored count is allowed here only with a test that recomputes and compares it. The point's text stays as written | 15m | none | Claude, top tier |
| D | **F86, the Zenodo record's primary source.** One DataCite request for DOI:10.5281/zenodo.19985473 (`sepulveda-jimenez-2026-optimality-generalization-quantum-oracle-sketching`; `metadata_provider` Crossref/DataCite; today only an HTTP probe from 2026-10-03 is recorded). If DataCite answers, the probe is recorded through `store/recheck.py` and the clock resets under ADR-0005 A9; if not, the reason is recorded and the record's access or provider routing corrected | 10m | about 5 s (one request) | Claude |
| E | **F82, the never-write hook's threat model (Class 1, Q2 = 1).** The stated threat model stays accidental writes by this repository's own sessions; the open forms a session could type by accident (abbreviated long options such as `--outp`, short-option clusters containing `O`, `--ext-diff` and `--textconv`) are blocked, each with a test proven by injection; the deliberate-evasion forms (pager, editor and config variables; command names built from strings or variables) are named in the hook's docstring as outside its model, with the reason | 30m | none | Claude, top tier (security-relevant hook) |
| F | **F84, the nine Dirac-1 records (Class 1, Q1 = 1; Q3 = 1).** An ADR-0004 amendment (A10) adds `platform:dirac-1` beside `platform:dirac-3` and `platform:dirac-3s`, by the same rule A8 used for Dirac-3S (one context per QCi system); the `contexts` row added with a backup; the nine records (the seven application pages whose header says "Device: Dirac-1", the risk-based UAS trajectory page, and the QC-7 article `quantumcomputinginc-nd-entropy-quantum-computing-offers-an`) retagged with the reason; their first-pass assertions in `manifests/sprint9_f80_reads/group_j3.json` (10 assertions, already drafted under `platform:dirac-1`) and the QC-7 article's in `group_j2.json` re-checked against the source and entered, each quote checked by a test; each record read and yielding, or left at `seen` with the reason | 40m | none (all nine are local HTML copies) | Claude, top tier (ADR, certainty) |
| G | **F85, Phase 2's Dirac-3S verification.** `docs/phase2/F142_DIRAC3S_VERIFY.md` re-read at Phase 2's commit current when the task starts (it changed after c141a57: 7 lines in, 4 out, last at e126dbd on 2026-10-17; Phase 2's HEAD was 6dd104a at planning). 3 or 4 HW assertions entered by Sprint 9 Task A's inbound path, provenance naming the repository, commit, file and run; every quote checked by a test against the file at that commit; each related to `dirac3s-analog-resolution-about-200-to-1`, `dirac3s-error-correction-is-a-post-processing-step` and `dirac3s-time-per-sample-by-schedule` as the text supports. Phase 2's own caveats (two fits, descriptive not a test, the post-processing cause unverified) carried into the values | 30m | none | Claude, top tier (certainty) |
| H | **F83, per-instance bounds for optimization problems.** The answer document's section 5 point 5 states the per-instance certificate (a relaxation or dual bound, and the gap an exact solver reports) with no source in the store; the store holds one related record (`gabbassov-2024-lagrangian-duality-quantum-optimization-overcoming`, at `seen`). Primary sources entered through the door at `seen` and read: a convex optimization text its authors publish freely (for weak duality and the duality gap) and a solver's own documentation of its reported gap. Section 5 point 5 rewritten as verified with the store ids, in a dated amendment. Nothing fetched around a paywall | 45m | about 1 min (two or three documents, none from arXiv) | Claude, top tier (certainty); Sonnet 5.5 first-pass read, every quote checked by the coordinator |
| I | **F89, F57 release for Sprint 10: read for claims, 74 records.** Ranked by the card's order. No record under `hsbc-2026` or `platform:dirac-3s` is left at `seen` or `screened`, and the 11 under `platform:dirac-3` were all screened and refused by F80 (9 of them are Task F's, which do not count toward the 74: Q3 = 1), so the release is the 74 most-cited `qml` records at `seen` or `screened` with no screening read yet, by F80's rule (OpenAlex citation counts). Each screened, read directly if it bears on a context, and yielding; each refused one stays `seen` with its reason. The count is refreshed (snapshot as of 2026-10-18: 2,042 at `seen` or `screened`, 2,031 never screened) | 120m | about 22 min: up to 74 arXiv PDFs not held locally, serial at 18 s inside F52's cap; OpenAlex counts in a few requests | Claude, top tier (certainty); Sonnet 5.5 first-pass readers under Task B's rules, every quote checked by the coordinator |
| J | **F87, tighter discovery filters.** Per stream in `scripts/discover_candidates.py`, a filter change that drops the off-topic kinds F62's run admitted (ml: software libraries, nature-inspired metaheuristics; tensor: knowledge-graph tensor factorization, density estimation, equivariant potentials; qml: quantum chemistry and hardware papers, an unrelated medical survey). A re-run's top 25 per stream with the off-topic count before and after, and the records each change drops named; no record the team lead accepted at Sprint 9 Q4 lost. A test per filter change, proven by injection. The OpenAlex key (present in the environment at planning) goes only in the Authorization header and is never logged | 40m | about 10 min: 4 streams twice, OpenAlex inside the daily budget, Semantic Scholar at 1 request per second | Claude; the team lead reviews the before and after lists at Manual Validation |

**Sequence**: A, B, C, D, E, F, G, H, I, J. A first, because the hook
blocks read-only commands every later task uses. B second, so the readers
in H and I work under rules corrected by Sprint 9's evidence. C, D and E
are small and independent; E waits on Q2. F and G before I, because they
settle the Dirac contexts I's ranking reads. J last among the builds,
because its review happens at Manual Validation. Total about 375 minutes
of coordinator time, plus about 35 minutes of runtime. No findings
allowance: the scope is not dominated by verification (Sprint 13 rule,
`SPRINT_PLANNING.md`). **If a Criterion 3 stop becomes necessary, the cut
line is before J**: J moves to Sprint 11. Deferring approved work is a
Class 3 decision and is never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-10-18): PR #88 merged to develop (86f2383) and
  PR #100 to main (270961e, tagged `sprint-9`); no open sprint issue;
  tree clean; suite 950 passed. The branch was cut from Sprint 9's branch,
  so develop's merge commit is not its ancestor, but no non-merge commit
  on develop or main is missing from it. Dependency scan not applicable
  (no requirements file; standard library and pytest only).
  `CHECKLIST-Phase2-pre.md` had no Sprint 9 section: back-filled with
  commit evidence at this phase.
- **The store (snapshot as of 2026-10-18)**: 2,190 papers (148 `read`, 14
  `screened`, 2,028 `seen`); 557 assertions. Unread records by context:
  `qml` 1,655, `qc` 252, `ml` 75, `world` 31, `method` 12,
  `platform:dirac-3` 11, `platform:classiq` 3, `platform:braket` 3;
  `hsbc-2026` and `platform:dirac-3s` 0. 11 records at `seen` carry a
  screening read row (F80's refusals).
- **F81**: reproduced live, above.
- **F84**: the contexts table holds `platform:dirac-3` and
  `platform:dirac-3s`, no Dirac-1 context. Nine records confirmed in F80's
  read groups: eight application pages in `group_j3.json` with their
  assertions drafted under `platform:dirac-1`, and the QC-7 article in
  `group_j2.json`. `qci-package-eqc-models` also mentions Dirac-1 but
  describes the current package; it stays under `platform:dirac-3`.
- **F85**: Phase 2's file changed after c141a57 (e126dbd, 2026-10-17).
- **F86**: as above; one HTTP probe recorded, no DataCite answer.
- **F83**: the store's only duality record is at `seen`; the free
  textbook and solver documentation are found and checked for an open
  copy at the task.
- **F87**: `OPENALEX_API_KEY` is present (read as a boolean, never
  printed).
- **F50**: point 7 read in full; the card's paraphrase matches its intent.
- **Plan-to-branch verification** (3.2.2.1): no Task A to J artifact
  exists yet; every selected F# is an open card in the master plan; F88
  and F89 are free numbers.

## Decisions (team lead, 2026-10-18, at approval)

The team lead answered "q1 1 q2 1 q3 1", then "plan approved". The plan
is approved with these answers. Tasks E, F and I are
rewritten to them in this commit (Sprint 7 retrospective I2); no runtime
changes, since each answer was the option the estimates assumed.

- **Q1 = 1 (Class 1, F84).** A `platform:dirac-1` context, by ADR-0004
  amendment A10 under A8's rule (one context per QCi system).
- **Q2 = 1 (Class 1, F82).** The never-write hook guards against
  accidental writes only; the accidental forms are blocked, the
  deliberate-evasion forms are named as outside its model.
- **Q3 = 1 (F84 and F89).** The nine Dirac-1 records do not count toward
  the 74: Sprint 10 reads 74 new records plus the nine.

Issues, one per task: A #102, B #103, C #104, D #105, E #106, F #107,
G #108, H #109, I #110, J #111.

## Premise falsifier

**The premises**: (a) F81's cause is the flag search running past the
command separator; (b) Sprint 9's reader defects were mostly added
conclusions, so a rule against unstated conclusions targets the real
failure; (c) the nine records' text supports Dirac-1 claims; (d)
Phase 2's revised file still states the F142 result the card records;
(e) the next 74 most-cited `qml` records bear on a context often enough
to yield; (f) the discovery filters can drop the off-topic kinds without
losing accepted records.

**What would disprove each**: (a) a read-only shape still blocked after
the segment fix, or a `sed -i` that passes: the cause is elsewhere, and
the test says so; (b) Sprint 9's review records show another defect
class as large: B logs it and the rule changes follow the record, not
this plan; (c) a page names Dirac-3 as the device it ran on: that record
stays under `platform:dirac-3`, with the reason; (d) the revised file
changes the result: the assertions follow the file at its commit, and the
card's figures are corrected; (e) more than half the 74 refused as not
bearing on any context: the ranking is reported as wrong, not hidden; (f)
an accepted Sprint 9 record falls out of a re-run: that filter change is
reverted or narrowed.

**The checks cannot merely confirm**: the F81 test runs the exact shape
that was blocked, and a `sed -i` beside it; the quote tests match text
extracted fresh from each source at its named commit or local copy; J's
before and after counts come from two runs of the same script, and its
loss check compares against the Sprint 9 accepted list by id.

## Risks

| Risk | Mitigation |
|---|---|
| F81's fix lets a real code edit through | The `sed -i` tests run beside the read shapes; both proven by injection; fresh-eyes review at the commit |
| F82 under Option 2 blocks legitimate reads of Phase 2 | Q2 states that cost; under Option 1 nothing new is blocked except accidental write forms |
| A Dirac-1 claim is read as a Dirac-3 claim | The new context keeps the systems apart; a query for Dirac-3 does not return them (A8's rule) |
| A Phase 2 caveat is dropped on entry | The values carry Phase 2's own qualifiers, quoted; certainty from the run count (two fits) |
| A first-pass reader adds an unstated conclusion | Task B's rule first; every quote and every value checked by the coordinator against the source |
| A closed paper is fetched around its paywall | Never: H and I use free copies only; a closed one goes on a hand-download list |
| arXiv refusal under the cap | All arXiv traffic serial, 18 s apart, through F52's capped fetcher; a refusal stops the run, never a retry burst |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| CI turns red unnoticed | The Stop hook (Sprint 9 I7) holds Phases 5 to 7 while CI is not green; local tests without `live_store` see CI's machine |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: both read shapes pass; `sed -i` on a code file still blocked; tests
  proven by injection
- B: the models list verified that day; Sprint 9's outcome rows logged;
  any rule change names its evidence; the guard test proven by injection
- C: the dated amendment written; point 7 unchanged
- D: the DataCite answer recorded, or the reason and the corrected
  routing
- E: per Q2; every new block tested and proven by injection; the
  docstring states the threat model
- F: per Q1 and Q3; the nine retagged with the reason; their assertions
  entered with quotes checked by test, or each refused with the reason
- G: 3 or 4 HW assertions entered at Phase 2's named commit; quotes
  checked by test; relations recorded
- H: the primary sources entered and read; the answer document amended
  with the store ids
- I: 74 records screened; every promoted record read and yielding; every
  refused one with its reason; the count refreshed
- J: per stream, the filter change, the records it drops, the off-topic
  count before and after; no accepted record lost; tests proven by
  injection
- Full suite green before every commit, gated on pytest's own exit code;
  CI green on the sprint PR before Manual Validation

## Out of scope

F51 (HOLD; its hold is not re-checked this sprint, last checked
2026-10-15). F57's later releases. Downloading any paper around a
paywall. Any write to `hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.

## Noted for the retrospective

The F57 card says a refused record "stays `seen` with the reason" and
that the item "closes when the count is 0" of records at `seen` or
`screened`. Both cannot hold: the 11 refused by F80 keep the count above
0 forever. Task I counts both figures (all records at `seen` or
`screened`, and those never screened) so the closing rule can be fixed
with the evidence in hand.
