# Sprint 7 Plan: Move the Data Out, Then Measure arXiv Safely

**Dates**: from 2026-10-06. **No deadline.**
**Branch**: `feature/20261006_Sprint_7` (cut at the Phase 6.6 carry-forward
from Sprint 6's branch, 2026-10-06, after PR #54 and PR #67 merged)
**Scope** (DEFINED, team lead 2026-10-06): F59, F58, F52, F53, F54, F44,
F45. Team lead's order: "F59 first ... F58 ... F52 and F53 together ...
F54 ... F44 ... each download is approved - do this after 59, 58, 52 and
54, but before 45 ... F45".

## Objective

Sprint 6 loaded the store to 1,875 papers and found that arXiv pacing had
never held between intake entries. This sprint first moves the data (the
store, its backups and the export) out of the repository folder, decided
in an ADR amendment before anything moves, so the repository stays small
as the store grows. It then measures the bulk papers' computed fields under
a per-session arXiv cap, recovers the unlinked repository notes, enters the
eight Cycorp papers, and reads the Dirac-3 sources that answer the team
lead's error-correction question. It opens with the permanent model check,
timed by Haiku 4.5's retirement date.

## Tasks

Est is coordinator time for the judgment steps (calibration from Sprint 6's
`## Actuals`: about 4.5 hours of work inside an 8.5-hour span against about
700 estimated minutes; code and document tasks ran under estimate, and
external APIs set the length). Runtime is separate, with its dominant term.
Model assignments follow `.claude/model_assignment_heuristics.json` as of
2026-10-03; Task A re-verifies it first and may revise them. Every task
that changes `store/`, a hook or a recovery path gets a fresh-eyes reviewer
at its commit, and one review-and-fix cycle in its estimate.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F59, F39 release for Sprint 7.** Re-read the models page (pre-flight: reachable, HTTP 200); record what changed per tier with the date; act on Haiku 4.5's retirement (not before 2026-10-15; recorded successor Sonnet 5.5): move the Developers tier if the date has passed or the page shows a change; the existing test stays green on evidence | 45m | about 5 min (one page) | Claude, top tier |
| B | **F58, the data out of the repository, ADR first.** Dated amendments: ADR-0004 A7 (the store, backups and export locations; what replaces the committed export per Q1-Q3), ADR-0003 (its export lines), ADR-0005 (section 3 and the "full-text search over the committed export" line); then `store.script_paths` reads one setting (default `D:\Data\Harold\EvidenceBasedDB\store`, environment override `EBDB_STORE_DIR` for tests and CI); a verified backup, then the move; the 16 test files that read the export switch per Q1; `.gitignore`, CI, `CLAUDE.md` ("The two directories"), `SPRINT_EXECUTION_WORKFLOW.md` (two lines) updated; `git rm` of `export/` only after its replacement exists and a rebuild from it is proven | 210m | under 5 min (one copy of 3 MB plus 46 MB of backups) | Claude, top tier (ADR); fresh-eyes review at commit |
| C | **F52, bulk probes under a per-session arXiv cap.** The cap lives on the shared clock (Sprint 6 I1): a count of arXiv requests per session, then a stop; a stopped run resumes on the papers not yet probed. Source and pacing per Q5-Q7. Pilot on 30, then capped sessions with a heartbeat file | 120m | **1,403 arXiv papers.** Q5 option 1: one site request each at the 15 s crawl delay = 5.8 h, in sessions of Q6's cap (240 requests = 1 h) with pauses between; other kinds: 102 GitHub and 1 DOI in under 5 min | Claude; background runs |
| D | **F53, probes each cycle and a stale report.** Phase 1.3 of `SPRINT_EXECUTION_WORKFLOW.md` runs the probes within F52's cap; `scripts/probe_reference_fields.py --stale` lists every probe older than the last cycle; a test fails on a stale probe | 60m | none | Claude |
| E | **F54, the 30 unlinked repository notes.** First the full URL from the paper's own text, then (team lead) a GitHub search with the partial URL, recorded as found by search with its query; `2108.0131` read from its PDF and entered; F35's 78-candidate queue stays for a later pass unless time allows | 60m | under 5 min (GitHub, token; search 30/min) | Claude |
| F | **F44, the eight Cycorp papers.** Downloads approved by the team lead 2026-10-06 ("each download is approved"). Files to `D:\Data\Harold\EvidenceBasedDB\Papers\` under the naming convention, SHA-256 recorded; S16 through the door as arXiv; the rest hand-origin; L10's DOI looked for first; T07 read directly for "eight tactic types" and "about a thousand HL modules" (two assertions, `vendor-self-claim`) | 90m | about 3 min (7 PDFs from cdn.aaai.org, cyc.com, northwestern.edu; S16 one arXiv site request inside the cap) | Claude |
| G | **F45, the Dirac-3 reading pass.** Read directly: the User Guide v0.0.4 (local), arXiv:2407.04512, arXiv:2502.08591, arXiv:2605.03612, arXiv:2608.10787 (all local PDFs in QMLPapers), the two QCi site pages (local); F-201 to F-206, F-208, F-209, F-301, F-302, F-303 as assertions where the source says so; F-207 as `absence` with its search scope; vendor statements flagged; F-209 cross-checked against the hsbc hardware plan's 949 levels | 120m | none (local files) | Claude, top tier (certainty) |

**Sequence (team lead)**: A, B, C with D, E, F, G. Total about 705 minutes of
coordinator time plus C's runtime. Per Q8, E, F and G may proceed while C's
capped sessions pause; all arXiv traffic stays serial and inside the cap
(F's one S16 request counts). **If a Criterion 3 stop becomes necessary,
the cut line is before F**: F and G move to Sprint 8 as a unit; nothing
else depends on them. Deferring approved work is a Class 3 decision and is
never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **arXiv API, the exact request the code sends** (`PacedFetcher`, one id,
  2026-10-06): **HTTP 429**, more than two days after the last request
  (Task I, 2026-10-04 04:37). F52 cannot assume the API answers.
- **arXiv's site**: `arxiv.org/abs/2405.12044` HTTP 200 in 0.6 s; the abs page
  of `2308.08167` shows its withdrawal text, so the site carries status.
  **`arxiv.org/robots.txt`**: "Crawl-delay: 15"; `/abs`, `/pdf`, `/html`
  allowed; "Indiscriminate automated downloads from this site are not
  permitted". Sprint 6's access probes and Task I's `/pdf` checks went to the
  site at 6 s, below this delay: a finding, and Q7.
- **OpenAlex** as an alternative: 0 results for an arXiv DOI (it does not
  index arXiv papers that way); its headers show 1,000 requests per day.
  Not a route for F52.
- **F52 sizing**: 1,533 papers have no probe row: 1,403 arXiv, 102 GitHub,
  27 hand-origin, 1 DOI.
- **F58 inventory (code, not only documents)**: 32 scripts and modules get
  their paths from `store.script_paths`; `store/backup.py` puts backups
  beside the database; **16** test files read the committed export (F58's
  card said 12); CI runs `pytest -q` on ubuntu with no access to `D:\`.
  Documents naming the committed export: ADR-0003, ADR-0004 section 2,
  ADR-0005 (line 551), `SPRINT_EXECUTION_WORKFLOW.md` (two lines),
  `CLAUDE.md`. `D:\Data\Harold\EvidenceBasedDB\store` does not exist yet.
- **F54**: GitHub search with the `gh` token found `zhihan-z/MCM_Learnability`
  for the truncated note `zhihan-z/MCM_`; search allows 30 requests per
  minute, core 5,000 per hour.
- **F44**: the seven non-arXiv URLs each answer HTTP 200 with
  `application/pdf` (HEAD, 2026-10-06).
- **F45**: every source is in the store at `seen`, and every one has a local
  copy: the User Guide in `References\`, the four arXiv papers in
  `QMLPapers\2024`, `2025`, `2026`, the two QCi pages in
  `References\QCi-site\`. No network needed.
- **F59**: the models page answers HTTP 200.
- **Plan-to-branch verification** (3.2.2.1): no Task A-G artifact exists yet;
  F58, F59, F52-F54, F44, F45 are open cards; suite 572 passed on this
  branch.
- **Phase 2 gates**: PR #54 merged to develop and PR #67 to main; no open
  sprint issues; tree clean. Dependency scan not applicable (standard
  library and pytest only).

## Decisions for the team lead at approval (numbered; answer with digits)

**DECIDED 2026-10-06** (team lead: "q1. 2 q2. 1 as backups of any changes
are made every day and exist for 40 days q3. 1 q4. 1 q5. 1 q6. 1 q7. 1 -
switch all arxiv api calls and / requests to 18 seconds q8. E can run, F
should wait, G should wait for F | note this can run all night without any
impact on the team", and "Sprint plan approved as amended"):

- **Q1 = 2: no export.** The committed export is removed and none is kept
  off the repository; the store's verified backups are the recovery path.
  Consequences for Task B: automatic export regeneration leaves the write
  scripts; `store/export.py` and `store/rebuild.py` stay as library code
  (an on-demand dump and its rebuild, tested on synthetic stores);
  `tests/test_export_currency.py` retires; tests that checked the REAL data
  through the export read the live store instead, under a `live_store`
  pytest marker that fails (never skips) locally when the store is missing,
  and that CI deselects by name in `ci.yml`, since CI cannot reach `D:\`.
  Backup retention's rule 3 ("content is committed") loses its basis and is
  replaced in ADR-0004 A7.
- **Q2 = 1**: one backup location; the team lead's daily backups of the
  drive, kept 40 days, are the redundancy.
- **Q3 = 1**: the export's git history stays; no rewrite.
- **Q4 = 1**: default `D:\Data\Harold\EvidenceBasedDB\store`, override
  `EBDB_STORE_DIR`.
- **Q5 = 1**: arXiv's abstract page, the API retried once per session.
- **Q6 = 1**: 240 arXiv requests per session, then at least 2 hours' pause.
- **Q7, amended: every arXiv request, API and site alike, 18 s apart.**
  Task C's runtime becomes 1,403 x 18 s = about 7 hours of requests, in
  sessions of 240 (72 min) with 2-hour pauses: about 20 hours in all, run
  overnight ("can run all night without any impact on the team").
- **Q8, amended**: E may run during C's pauses; F waits for C to finish; G
  waits for F.
- **Q9**: not answered; the current priorities stand, and the question is
  asked again at Manual Validation.

F58 is Class 1 and ADR-first, and the auto-advance window forbids asking
later, so its substance is decided here; the amendment's text is reviewed
at Manual Validation.

- **Q1. Where the export goes (F58).** (1) A full export beside the store,
  `D:\Data\Harold\EvidenceBasedDB\store\export\`, regenerated on every
  write, plus a small committed fixture export (`tests/fixtures/export/`, a
  fixed sample of papers and every assertion) that CI and the export-reading
  tests use; (2) no export at all, backups only; (3) keep the export in the
  repository. Recommend 1: the full export stays the rebuild source and the
  readable copy of the data, off the repository; the fixture keeps CI able
  to prove the round trip. What 1 gives up: the store's history is no
  longer in git, so a data change has no reviewable diff; the backups are
  the history.
- **Q2. Backup redundancy (F58).** (1) One location, `...\store\backups\`, on
  the same disk as the store; (2) also copy each verified backup to a
  second location you name (another drive or a synced folder). Recommend 2:
  today a disk failure loses the store, its backups and, once Q1 lands, the
  export together. If 2, name the path.
- **Q3. The export's past history in git (F58).** (1) Keep it: about 2.7 MB
  per version, already compressed in the history; no rewrite; (2) rewrite
  history to remove it (destructive: a force-push to develop and main).
  Recommend 1.
- **Q4. The store path setting (F58).** (1) Default
  `D:\Data\Harold\EvidenceBasedDB\store`, override with the environment
  variable `EBDB_STORE_DIR`; (2) a path in a committed config file.
  Recommend 1: no machine-specific path in a tracked file beyond the
  default.
- **Q5. F52's source while the arXiv API refuses.** (1) arXiv's abstract
  page, one request per paper at the site's 15 s crawl delay, giving
  publication status (withdrawn text, journal reference), version of record
  (the DOI it prints) and access in one request; at each session start one
  API request checks whether the API answers again, and if it does the run
  uses the API at 6 s; (2) wait for the API, checking once per session; (3)
  DataCite only (no withdrawal can be seen). Recommend 1.
- **Q6. The per-session arXiv cap (F52).** (1) 240 arXiv requests per session
  (one hour at 15 s), then at least a 2-hour pause, as the team lead set on
  2026-10-04; (2) another number. Recommend 1; the first sessions measure
  whether arXiv tolerates it.
- **Q7. Site pacing.** (1) Every request to arxiv.org's site (`/abs`, `/pdf`,
  access probes) waits 15 s, per its robots.txt; the API stays at 6 s; (2)
  keep 6 s everywhere. Recommend 1: it is the site's own published rule,
  stricter than your 6 s, and Sprint 6 broke it unknowingly.
- **Q8. Overlap.** (1) E, F and G may run while C's capped sessions pause
  (F's single S16 request counts against the cap; G needs no network); (2)
  strictly after C finishes. Recommend 1: C's runtime is about 5.8 hours
  across sessions, and nothing else in E-G touches arXiv beyond S16.
- **Q9. The priority changes proposed at refinement** (F52 to 20, F53 to 22,
  F54 to 30, F45 to 40, F44 to 42, F57 to 50, F55 to 60, F56 to 62, F48 to
  70, F49 to 72, F50 to 80, F46 to 90). (1) Apply; (2) keep the current
  priorities.

## Premise falsifier

**The premises**: (a) the data can leave the repository folder and the
store still rebuilds byte-identically from the export at its new place;
(b) arXiv's site tolerates one request per 15 s in capped sessions; (c)
the eight Cycorp PDFs are the papers the handoff names; (d) the Dirac-3
sources state what the pending facts say they state.

**What would disprove each**: (a) the rebuild from the off-repository
export, or from the committed fixture, differs; a script still writes
inside the repository folder; (b) the site answers 429 or 403 inside a
capped session: the run stops itself, and the remaining papers wait; (c) a
downloaded PDF's title page names a different paper; (d) a fact's quoted
sentence is not on the page it cites: the fact is dropped, not reworded.

**The checks cannot merely confirm**: the rebuild compares bytes from a
fresh temporary store; a test proves no write path resolves inside the
repository; the cap test injects a 13th request against a cap of 12; every
F45 quote is matched against the local PDF text.

## Risks

| Risk | Mitigation |
|---|---|
| The move loses the store or its backups | A verified backup first; copy, verify counts and integrity, then remove the originals; the old paths refused afterward |
| Removing the export weakens review and CI | Q1: the full export moves beside the store; a committed fixture keeps CI's round trip; the decision is recorded in ADR-0004 A7 |
| arXiv refuses the site too | Q6's cap stops each session; the run resumes later; DataCite still answers version-of where it can |
| A test or script still resolves a path inside the repository | A test that every store, backup and export path resolves outside the repository unless `EBDB_STORE_DIR` points elsewhere |
| Haiku 4.5 retires mid-sprint | Task A runs first and moves the Developers tier on evidence |
| Downloads land inside the repository | Files go to `D:\Data\Harold\EvidenceBasedDB\Papers\`; the sibling-repo and records-not-PDFs rules hold |
| Session continuity across capped, paused sessions | `sprint_status.json` note at every boundary; the heartbeat file names the next unprobed paper |

## Definition of Done

- A: each tier re-verified with the date; the Developers tier acted on per
  the page; the test green on evidence
- B: amendments accepted at Manual Validation (text reviewed there); the
  store, backups and full export live under `D:\Data\Harold\EvidenceBasedDB\store`;
  the rebuild proven from the new export and from the committed fixture;
  no data file in the repository; every guard proven to fail by injection;
  the fresh-eyes review's findings fixed
- C: every bulk paper probed or reported; the cap tested by injection; no
  value stored from a request that got no answer; every arXiv request at
  its stated spacing
- D: Phase 1.3 runs the probes; the stale report exists; a test fails on a
  stale probe
- E: each of the 30 notes linked with its evidence or reported again with
  what was tried; `2108.0131` entered or reported
- F: eight records, each with a local path and SHA-256; T07's two figures
  read directly and entered
- G: each promoted source names what was read and when; each assertion
  quotes its source verbatim; F-207 with its search scope
- Full suite green before every commit, gated on pytest's own exit code

## Out of scope

F39 itself (released as F59), F46, F48, F49, F50, F55, F56, F57, F51 (HOLD
until hsbc Sprint 21 merges). Screening any bulk record. Any write to
`hsbc-quantum-fraud-2026` or `spamfilter-multi`.
