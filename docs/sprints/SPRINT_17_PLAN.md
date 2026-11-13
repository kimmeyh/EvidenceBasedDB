# Sprint 17 Plan: Test Faster, Then Read on the API Credit

**Dates**: from 2026-11-07. **Outside date**: the $100 API credit expires
2026-11-18 (team lead), so F144's build and pilot come early.
**Branch**: `feature/20261107_Sprint_17` (cut at the Phase 6.6 carry-forward
from Sprint 16's branch, 2026-11-07, after PR #164 merged to develop and PR
#173 to main; tagged `sprint-16`). F144 works on its own branch from this
one, with its own draft PR (the team lead's brief).
**Scope** (DEFINED, team lead 2026-11-07): F140, F144, F114, F142, F141,
F143. The team lead's changes at selection:

- F140 first, "and complete it so that any other testing in the sprint
  uses this newly implemented testing methodology".
- F114 reads 10 papers this sprint, not 30, and none of them is a paper
  F144 reads. The two PDFs the team lead saved into `Papers\` on
  2026-11-07 are among the 10.
- F143 added to the recommended scope.
- F39 was not selected, so model assignments rest on Sprint 13's release
  (F111) and `.claude/model_assignment_heuristics.json`.

## Objective

Make the local test suite fast and risk-based, and use it for every other
test run in the sprint (F140). Build the Batch API reader and pilot it on
5 papers before the credit expires (F144). Then ship the retrospective's
four pipeline fixes (F142) and the full paper view (F141), read 10
papers under the improved pipeline (F114), and find why the agents' cost
per page rose (F143).

## Tasks

Est is coordinator time for the judgment steps. Sprint 16's `## Actuals`:
Tasks A to E took about 415 minutes for 240 estimated (1.7 times); the
reads ran at 0.75 reader minutes and 0.24 reviewer minutes per page. Each
task that changes `store/`, `scripts/` or a hook carries one fresh-eyes
review and fix cycle. Runtime is separate, with its dominant term.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F140, testing: risk-based, effective, fast.** All nine parts of the card: the generated inventory (a test fails if a test file is missing from it); why the local run is slow, with the top causes fixed; tests that cannot fail or pin planned data; a risk tier per test file; `--changed` made import-aware; store data checks once per apply; when a red proof is stale; which full runs are needed. `docs/F140_TESTING_ANALYSIS.md`, each recommendation asked as its own numbered question. The approved ones are implemented per Q2 before Task B starts, and the workflow's test points are updated to match | 150m [no-history] timebox (analysis) + per Q2 (implementation) | `pytest --durations=0` over the full suite: about 69 minutes at Sprint 16's last run, once at the start; a second full run after the fixes, to measure them | Claude, top tier |
| B | **F144, the Batch API reader and its 5-paper pilot.** On its own branch and draft PR. Every bullet of the card: the API reader prompt (passes `tests/test_reader_prompts.py`); `scripts/batch_read.py`, dry run by default, with ranking order, ledger groups, the text with page markers, page images where the pipeline uses them, `max_tokens` at the 300k beta, the key per Q1, a resumable state file outside git, no resend, raw results saved first, reader group files checked by `sprint13_g_check.py`, cost from the API's usage, the $95 cap and the 2026-11-18 stop; the four rule tests, each proven red. The `anthropic` SDK in its own environment outside git, pinned in `requirements-batch.txt` (as OCR's). Pilot: 5 papers from the top of the ranking, then STOP and report (pages, tokens, cost, check results, file locations, total, cost per page and per paper, papers $100 covers, what a no-tool read lost), with a batch size and a paste-in prompt | 240m [no-history] timebox | the pilot batch: most batches finish within 1 hour (Anthropic, 2026-11-07); 5 requests | Claude, top tier; the batch reads are Sonnet 5.5 on the API |
| C | **F142, four pipeline fixes.** Reader telemetry outside the repository (or out of the tree fingerprint), coordinated with Task A's part 6; a sign-off table to add or split an assertion; long proof appendices split across reviewers; both status fields set in one step. Each with a test proven red | 105m | none | Claude, top tier |
| D | **F141, the paper view in full.** `view.py paper <id> --full`; the default output unchanged; a test proven red | 15m | none | Claude, top tier |
| E | **F114, 10 papers.** Order: the 2 PDFs saved into `Papers\` on 2026-11-07 (Ayan Sar et al., IEEE Access 2026, 43 pages; PSI's web article "A proof of the Aaronson-Ambainis conjecture", 9 pages), each entered through the intake door; Christophe Pere's list (unchanged since 399b022651, checked 2026-11-07); then 8 from the ledger, from the first group not yet read in full, with Sprint 16's exclusions (saved web pages with no article, directory sources, books). The 10 are fixed by id at the task start and written to F144's exclusion list; F144 never selects them. Under the Sprint 16 prompts with C's fixes; up to 5 local readers; each reviewer reads the paper in full; one apply with its trial and verified backup | 15m (entry) + 25m (review and sign-off, at Sprint 15's 2.4m per record) | no estimate as a limit (no reading budget). At Sprint 16's rate, about 26 pages per paper and 0.99 agent minutes per page, about 260 agent minutes in the background | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| F | **F143, why per-page cost rose.** Each Sprint 16 group's cost split by paper kind (proof-heavy, figure-heavy, experiment, survey), by pages viewed as images and by re-reviews; Task E's telemetry added; the cause named with its evidence, and each fix asked as its own numbered question | 90m [no-history] timebox | none | Claude, top tier |

**Sequence** (changed at approval, team lead 2026-11-07: "don't run F140
until F144 is finished"): B first, through its pilot report. A next and
complete, with every approved change in place before C to F test anything
(Q2 = 2). C and D then; C's telemetry part before E's readers start. E's
readers run in the background while F is written; F uses E's telemetry
too. One apply at a time. Total about 625 minutes at the cards' estimates
plus Q2's implementation time; at Sprint 16's 1.7 times, about 1,060
minutes, plus the reads in the background and the pilot batch. No findings
allowance: the scope is not dominated by verification.

**If a Criterion 3 stop becomes necessary, the cut line is F, then E's
ledger papers**: F moves to the backlog, and E stops at the groups it has
reviewed. Deferring approved work is a Class 3 decision and is never made
unilaterally.

**Full suite**: twice (before the Manual Validation hand-over, and after
any retrospective improvements that change code), unless Task A's approved
recommendations change these test points. From Task A's end, every test
run in the sprint follows its new method.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-11-07): PR #164 merged to develop (3180aad) and
  PR #173 to main (85fbeae, tagged `sprint-16`); no open sprint issue;
  working tree clean except this plan. Dependency check: `uv pip list
  --outdated` lists only the global Python environment's packages; this
  repository pins only `requirements-ocr.txt`, which is current.
- **The store (snapshot as of 2026-11-07)**: 2,367 papers (1,813 at
  `read`, 554 at `seen`); 522 with no read row; 36,209 assertions (11,491
  `high`). F114: 880 of 1,430 ledger records not read in full, in 187
  groups.
- **F144's facts, checked on Anthropic's batch-processing page
  (2026-11-07)**: Batch prices for Claude Sonnet 5.5 are $1 per MTok
  input and $5 per MTok output (50% of standard). Most batches finish
  within 1 hour; a batch expires if processing does not complete within
  24 hours, and an expired request is not billed. Results are available
  for 29 days. A batch holds at most 100,000 requests or 256 MB. The
  `output-300k-2026-03-24` beta raises `max_tokens` to 300,000 for batch
  requests on Sonnet 5.5 (and Opus 5.5). **Not checkable from here**: the
  credit's amount, scope and expiry, which are account facts (the team
  lead's, as given).
- **F144's environment (2026-11-07)**: the `anthropic` package is not
  installed in the Python environment, and no `ANTHROPIC_API_KEY` is set
  in this session's shell. Both are needed before the pilot (Q1, and the
  team lead's step below).
- **The key and Claude Code (Anthropic's Claude Code authentication page,
  2026-11-07)**: Claude Code's own credential order puts the
  `ANTHROPIC_API_KEY` environment variable above the subscription login.
  In interactive mode Claude Code asks once whether to use it, and "In
  non-interactive mode (`-p`), the key is always used when present". A
  key set under that name where Claude Code runs could make Claude Code's
  own work spend the credit (and fail at $0). Q1 asks how the key is
  named.
- **F144's candidates (data precondition, 2026-11-07)**: of the 522
  records with no read row, 173 are GitHub repository records (not
  candidates, as in Sprint 13's F112), 107 name an arXiv id (6 of them
  withdrawn, kept as records only, so not candidates) and 242 a DOI; 2
  name neither. 167 of the 522 are F114 ledger records (groups g295 to
  g329) whose PDF is already in `Papers\` (Sprint 13 Task G's downloads,
  INTAKE section 55); `store.recheck.local_pdf` does not find these
  because their `access` names the arXiv id or DOI, so F144 takes their
  file from the ledger. The rest need a free copy fetched by the paced
  fetcher, or go on the hand-download list (Q2 = 1 of the brief).
- **F114's new papers**: 2 PDFs saved into `Papers\` on 2026-11-07, not
  named by any record: `2026-11_Ayan_QML_in_Medical_Image_Analysis_From_Diagnostics_to_Surgery_Planning.pdf`
  (DOI 10.1109/ACCESS.2026.3663498, 43 pages) and
  `2026-11 A proof of the Aaronson-Ambainis conjecture by PSI.pdf` (a web
  article from PSI, saved from a browser, 9 pages). Christophe Pere's list
  is still at 399b022651 (2026-11-05).
- **F114's ledger front**: the first records not read in full are left
  out by Sprint 16's rules (g047's and g069's saved web pages with no
  article, the OpenCyc and ds3lab directory sources); the 8 are chosen by
  the same script rule at the task start.
- **Plan-to-branch verification** (3.2.2.1): no Task A to F artifact
  exists yet (`docs/F140_TESTING_ANALYSIS.md`, `scripts/batch_read.py`,
  `requirements-batch.txt` and `view.py --full` are absent); F140 to F144
  and F114 are open cards.

## The team lead's question at selection

"Does this mark them as screened or that the paper is available in the
cache or ? how would this help us do some of the work of reading papers
and save future token spend?" Read as a question about F144's batch reads.
(If it meant F114, F114's reads are applied in this sprint, so each of its
10 papers ends at `read` with a full read row.)

- **What a batch read leaves**: no store change. The paper stays `seen`
  with no read row until a later sprint reviews and applies it. What
  exists afterward:
  - the PDF on disk (fetched once, if it was not local);
  - its extracted text in the shared text cache (keyed by the file's
    SHA-256, F136), so no later step extracts it again;
  - its reader group file in the repository, already checked by
    `sprint13_g_check.py` (every quote checked against that text);
  - its ledger group, and its entry in the state file as "read by batch,
    waiting for review". F114 and F57 releases skip any record in a batch
    group, so it is not read twice.
- **What it saves**: the first-pass read, which is about 59% of Sprint
  16's agent tokens per page (readers 4,633 of 7,857), is paid from the
  API credit, not from Claude Code usage. The later sprint still pays for
  the review (each reviewer reads the paper in full, Sprint 16 Q5 = 2),
  the coordinator's sign-off and one apply. At the pilot's measured cost,
  Task B reports how many papers the credit covers.

## Decisions for the team lead

**Approved 2026-11-07** ("Sprint plan approved as amended ... proceed with
execution"), with the team lead's answers and changes:

- **Q1 (the team lead's own answer)**: "I will put it in the .env file in
  the local repository D:\Data\Harold\github\EvidenceBasedDB and then we
  can use if from there", the key "will be called ANTHROPIC_API_KEY", and
  "Update uv for python-env (not sure of package name)". So: `.env` at the
  repository root, ignored by git; the package is `python-dotenv`, added
  with `uv` beside `anthropic`; the script reads the key with
  `dotenv_values`, which returns it without putting it in the environment,
  so Claude Code's credential order never sees an `ANTHROPIC_API_KEY`
  variable. A hook (`block_env_secret_reads.py`) blocks Claude from
  reading, printing, editing or staging `.env`, done first, before the
  team lead created the file. The team lead created it the same day (".env
  is ready to be tried").
- **Order changed** (team lead, 2026-11-07): "you can test the api key
  before F144 finishes, but don't run F140 until F144 is finished". So F144
  (Task B) runs first, F140 (Task A) after F144's pilot report, then C to
  F. This reverses the selection's "F140 first" and Q2's "F140 before
  F144"; Q2 = 2 still holds for F140 against the tasks after it (every
  approved F140 recommendation is implemented before C to F's testing).

Team lead, 2026-11-07, earlier: "2. 2" (Q2 = 2). Q1 asked again with a `.env`
option, after the team lead asked "do we have an .env file where we can
store the key?" (no: neither the repository nor
`D:\Data\Harold\EvidenceBasedDB\` holds one, and `.gitignore` does not
name `.env`; checked 2026-11-07).

- **Q2 = 2**: every approved F140 recommendation is implemented, whatever
  its size, before F144 starts. F144's pilot then runs later, with fewer
  days left for its follow-on batches before 2026-11-18. If F140's
  implementation would push the pilot past 2026-11-14, that is reported
  to the team lead as a changed commitment the day it is known.

- **Q1 (asked again). Where is the API key kept?**
  1. A `.env` file outside the repository,
     `D:\Data\Harold\EvidenceBasedDB\.env`, holding one line,
     `EBDB_ANTHROPIC_API_KEY=...`, that you paste in once. Only the script
     reads it, with a few lines of its own code (no new package). Claude
     Code keeps using your subscription; no shell sees the key; nothing
     needs a restart. Task B adds `.env` to `.gitignore` and a hook,
     proven red, that blocks any tool call by Claude from reading or
     printing that file.
  2. A Windows user variable, `EBDB_ANTHROPIC_API_KEY`. Claude Code keeps
     using your subscription, but you must restart Claude Code, and every
     command Claude runs can see the variable.
  3. `ANTHROPIC_API_KEY`, as the brief says. Claude Code asks once whether
     to use it; if approved, or in any non-interactive run, Claude Code's
     own work bills to the credit and stops when the credit reaches $0.
  - Recommend 1
- **Q2 (answered 2). How much of F140's implementation happens before F144 starts?**
  F140's analysis ends in recommendations you approve one by one.
  1. The approved recommendations up to a 120-minute timebox, then F144
     starts; larger ones are carded for Sprint 18. F144's pilot runs
     about 1 to 2 days after approval, well before 2026-11-18.
  2. Every approved recommendation, whatever its size, before F144
     starts. The methodology is complete for all later testing, but F144
     waits an unknown time and its follow-on batches have fewer days
     before the credit expires.
  - Recommend 1

**Your step (not a question)**: before Task B's pilot, put the key where
Q1 chooses (with Q1 = 1: create `D:\Data\Harold\EvidenceBasedDB\.env`
with the one line, after Task B's hook is in place). Claude never reads
or prints its value.

## Premise falsifier

**The premises**: (a) the local suite's slowness has a few fixable causes
(F140); (b) a no-tool batch read of a whole paper produces a reader group
file that passes `sprint13_g_check.py` (F144); (c) a batch read costs about
$0.15 to $0.30 per paper (the team lead's forecast); (d) F142's telemetry
fix stops reader-blocked gates; (e) the per-page cost rise has a nameable
cause (F143).

**What would disprove each**: (a) `--durations` shows the time spread
evenly over many tests: A reports it, and the 10-minute target is restated
with its reason; (b) a pilot result fails the check on its quotes or its
shape: B keeps it, flags it, and reports what the prompt must change
before any further batch; (c) the pilot's measured cost per paper is
outside the forecast: B reports the measured figure and how many papers
the credit covers at it; (d) a gate turns INVALID while E's readers work:
the fix is incomplete and returns to C; (e) no split of the data explains
the rise: F says so and names what data would.

**The checks cannot merely confirm**: the pilot's check reads the
extracted text, not the model's copy; the cost comes from the API's usage
fields, not from the forecast; A's timings are measured before and after.

## Risks

| Risk | Mitigation |
|---|---|
| The key leaks into output, a file or a commit | Read only from the environment; a test proven red that no output, state file or result holds it; never echoed by any command |
| Claude Code itself spends the credit | Q1 (the key kept outside Claude Code's credential order) |
| F140's full implementation (Q2 = 2) delays F144 past the credit | The pilot's date is tracked in the status note; a slip past 2026-11-14 is reported the day it is known |
| A record is sent twice, or a closed session loses a batch | The state file is saved before polling; no resend once a result is saved; a test proven red |
| Spending passes the credit | The $95 cap checked before each batch on the estimated cost; the running total from the API's usage; a test proven red |
| A batch read is cut short | `max_tokens` at the 300k beta; a result whose `stop_reason` is `max_tokens` is flagged, never treated as whole |
| A no-tool read misses figures or image-only pages | Page images sent where the pipeline uses them, or the page listed as not read with its reason; the pilot report names the loss |
| F114 and F144 read the same paper | E's 10 fixed by id first and written to F144's exclusion list; F144 skips any record in a batch or reading group |
| A faster suite drops a guard | A's inventory names each guard; the risk tiers keep the high-impact guards on every gate; the full suite stays the backstop |
| A reader relabels a stored context or grade | The applier's stored-context guard and the "undecided" list |
| A write reaches a sibling repository | Phase 2 read only; no fetch in a sibling repository |
| The email address, the OpenAlex key or the API key leaks | None is sent or printed; requests carry the UA "EvidenceBasedDB-fetcher/1.0" |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time; F144's state file for its batches |

## Definition of Done

- A: `docs/F140_TESTING_ANALYSIS.md` with the generated inventory and each
  recommendation asked; the approved ones in place per Q2, each with a
  test proven red where it adds a guard; the full suite's time before and
  after; the workflow's test points updated to match
- B: on its own branch and draft PR; the API prompt passes
  `tests/test_reader_prompts.py`; the four rule tests proven red; 5 pilot
  results saved and checked; the spend recorded and under the cap; the
  store's stamp unchanged; the pilot report, the batch size and the
  paste-in prompt given to the team lead
- C: the four parts, each with a test proven red; no gate INVALID while
  E's readers work
- D: `--full` with its test proven red
- E: 10 papers read in full, reviewed and applied once, none of them
  F144's; the 2 new PDFs entered; the counts before and after; a second
  apply writes nothing
- F: the cost split and the cause named, or the reason it cannot be
- Every test run after A by A's method; CI green on the sprint PR before
  Manual Validation

## Out of scope

F144's batches after the pilot (they run from the paste-in prompt, after
the team lead reads the report). Reviewing or applying any batch result
(a later sprint). F39 (not selected). F57 releases beyond F144. F138 and
F90 (HOLD). Downloading any paper around a paywall. Any write to
`hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
