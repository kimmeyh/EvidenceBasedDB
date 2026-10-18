# Sprint 9 Plan: Read the Ceiling Papers, Then Open the Phase 2 Exchange

**Dates**: from 2026-10-14. **No deadline.**
**Branch**: `feature/20261014_Sprint_9` (cut at the Phase 6.6 carry-forward
from Sprint 8's branch, 2026-10-14, after PR #77 and PR #87 merged)
**Scope** (DEFINED, team lead 2026-10-14): F78, F79, F74, F68, F69, F62,
F57, F55, F56, F48, F46, F51. F57 is permanent, so it is released as F80
(this sprint's slice). F51 is a HOLD item; Task K checks its hold.

## Objective

The team lead asked whether a dataset or an optimization problem has a
ceiling that no model can beat, so the team knows whether to improve the
model or get better data. This sprint reads the store's whole
ceiling-estimation group in full, enters what it proves, and writes the
answer down. It first fixes the rules between this repository and
hsbc-qfraud-phase2 (each reads the other freely; neither writes to the
other), then clears the small fixes the reading depends on: the door's
two identifier forms, the re-check's two correctness faults, and SHA-256
on every local copy. After the reading it runs the remaining pending
facts, the first released slice of "read for claims", citation links,
the corroboration decision and paper discovery.

## Tasks

Est is coordinator time for the judgment steps, calibrated from Sprint 8's
`## Actuals`: reading and code tasks ran 4 to 10 times under their card
estimates (Task C: a 38-page guide read and 19 assertions classed in about
27 minutes, plus review), so the card estimates are cut by about 3 and
reading tasks carry a findings allowance. Runtime is separate, with its
dominant term. Models follow `.claude/model_assignment_heuristics.json`.
Every task that changes `store/` or `scripts/` gets a fresh-eyes review at
its commit, with one review-and-fix cycle in its estimate.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F79, the Phase 2 exchange.** CLAUDE.md names `hsbc-qfraud-phase2` as the consumer, keeps Phase 1 as history, and states the rule: each repository reads the other directly, with no prompt needed; neither writes to the other; a change wanted in the other repository goes as a prompt the team lead pastes. The never-write hook and its memory file add Phase 2's repository and Claude Code project directory; a hook test proven to fail by injection. `docs/INTAKE_WORKFLOW.md` gets the inbound path (a Phase 2 result read from Phase 2's files at a named commit, provenance naming repository, commit and run) and the outbound prompt shape (each claim with its provenance inline). A prompt is drafted for the team lead to paste into Phase 2, asking it to add its own never-write guard for this repository. The inbound path is tried on one real Phase 2 result (Q9) | 30m | none | Claude, top tier |
| B | **F68 with F69, two door fixes and one paper.** `parse_access` reads old-style arXiv ids (`quant-ph/0405098`) and DOIs with parentheses; a test for each, proven by injection; the five Massoli entries re-run through F61's script. Then the Cerezo PDF: its identifier from its first page or a search, entered at `seen` through the door, or recorded out of scope with the reason | 25m | about 1 min (5 door lookups, 1 search) | Claude |
| C | **F74, re-check correctness.** ADR-0005 A9: a re-check counts as complete only when the paper's own primary source answered (Q4 = 1). Every paper whose primary source failed is listed at Manual Validation with a recommendation for each: investigate now, card it for Sprint 10, or accept it as due and retry at the next Phase 1.3. `last_check` counts only those answers; a missing or failing `pdftotext` is reported as a tool failure, not as the paper's fault; a probe that raised is reported as a probe failure. Two tests (DataCite answers and arXiv does not, so the paper stays due; `pdftotext` unavailable), each proven by injection | 30m | none (nothing due before August 2027) | Claude, top tier (ADR) |
| D | **F48, honest local paths.** SHA-256 recorded for every local-access source (125 records; 11 carry one today); a check that reports a missing file or a changed hash, folded into the re-check's local-file check so it runs on the same schedule; a test with one moved file, proven by injection | 30m | about 1 min (114 files hashed locally) | Claude |
| E | **F78, the ceiling-estimation group, read in full (team lead, 2026-10-14: "read everything in full").** All 31 CE records, plus Ishida et al. 2023 (arXiv:2202.00395) and Theisen et al. 2021 (arXiv:2106.03357) entered through the door. Every paper and repository read in full and its read recorded; Zhao and Ushio finished; the ceiling, bound and method claims entered as assertions with section anchors, every quote verified verbatim by test (Butt's 0.451 F1 ceiling with its abstract-to-theorem gap and its Table IV exceedance; Tschirschwitz's LVIS bound; Zhao's F-score and BER bounds; Boyd's AUPRC minimum; the Bayes-error estimators and where each fails). F46's nine ceiling facts (F-701 to F-710) are answered here, since they come from the same papers. Local copies: Ishida, Theisen and Thanh (arXiv), Allen (Federal Reserve) downloaded into `Papers\` with SHA-256; Chen 2025 and Te Sun 1994 are closed, so they go on a hand-download list (Q3). Repositories per Q2 = 2: each shallow-cloned into `D:\Data\Harold\EvidenceBasedDB\GitHubRepos\` (outside git), its commit recorded in the read row. The answer document `docs/research/ceilings-ml-and-optimization.md`: how to find a ceiling for an ML dataset and a bound for an optimization problem, each method with its source, verified and inferred kept apart, plus a sort of the store's QML-advantage claims into families (optimization, kernels, linear algebra, sampling, quantum data). **Findings allowance 30%** | 150m + 45m allowance | about 2 min: 3 arXiv PDFs at 18 s spacing inside F52's cap, 1 Federal Reserve PDF, 7 shallow clones | Claude, top tier (certainty); Sonnet 5.5 subagents for first-pass reads, every quote checked by the coordinator |
| F | **F46, the remaining pending facts (non-ceiling).** From the handoff's `07-assertion-candidates-pending.md`: World (8), Entanglement in QML (1), the April 2026 claim (4), Classical fraud detection (7); 20 facts. Each source read directly first, then the assertion; the four already-read records compared before adding (a `supports` link, a refinement or a duplicate); new records for the sources with none (the NVIDIA blog and Kaggle write-up, the Kaggle leaderboard with its access date, the ULB temporal-split repository, the April 2026 blog post). The Holevo bound (F-001) needs a primary source: the 1973 paper or a textbook, else it stays out with the reason. **Findings allowance 30%** | 90m + 27m allowance | about 4 min: about 12 arXiv PDFs at 18 s, inside the cap | Claude, top tier (certainty) |
| G | **F80, F57 release for Sprint 9: read for claims, first slice of 76 (Q7 = 2).** Ranked by the card's order: the 26 records at `seen` or `screened` under `hsbc-2026` (6), `platform:dirac-3` (18) and `platform:dirac-3s` (2), none in the CE group; then the 50 most-cited `qml` records at `seen` or `screened`. Each screened, read directly if it bears on a context, and yielding; each refused one stays `seen` with its reason. From Sprint 10, F57 releases 74 records per sprint until none remain (team lead, 2026-10-15) | 210m | about 20 min: up to 66 arXiv PDFs not held locally, at 18 s | Claude, top tier |
| H | **F55, citation links.** A computed `cites` link (Q5: a new link type, ADR-0005 amendment and schema migration with backup) from Crossref reference lists, for every pair of papers both in the store; recorded once, readable from both ends; never typed by hand; coverage reported. Not a certainty input | 45m | about 8 min: 214 DOI records plus arXiv records whose probe found a journal DOI, one Crossref request each, serial (pre-flight: Chen 2025 returns 44 references) | Claude, top tier (ADR) |
| I | **F56, corroboration (Class 1 decision at approval, Q6).** As decided: ADR-0004 amendment, then the build. Under the recommendation, a computed "corroborated" flag shown beside the stored certainty when an INDEPENDENT assertion (different authors, not the same vendor) at equal or higher certainty supports it; the assessor decides any upgrade, with the reason; `view.py` shows the flag; a test with a same-vendor pair that must not count, proven by injection | 20m + 40m | none | Claude, top tier (ADR) |
| J | **F62, discovery and the hand-download list.** The pilot script run with the team lead's OpenAlex key (Authorization header only) under the ranking rubric approved at Q8; citations cross-checked against Semantic Scholar and duplicate titles collapsed before ranking; per stream (ml, qml, tensor, fraud) a top list for the team lead's review at Manual Validation; chosen papers enter through the door at `seen`; a hand-download list (rank, title, DOI, publisher link, why, target file name) with every entry's free-copy search recorded | 90m | about 10 min: 4 streams, OpenAlex searches inside the daily budget, Semantic Scholar at 1 request per second | Claude; the team lead reviews the lists |
| K | **F51, the CVQBoost findings record (HOLD check).** Pre-flight: the findings document is unchanged since 2026-08-04 (SHA-256 prefix `425358a7b4cec71f` at both copies), so the re-run it waits on has not landed there. Per Q9 | 10m | none | Claude |

**Sequence**: A, B, C, D, E, F, G, H, I, J, K. A first, because the
sprint reads Phase 2 and its guard should cover it before then. B and D
before E, because E's intake uses the door and E's downloads need
SHA-256 recording. C is independent and small. E before F, because F's
ceiling facts were moved into E. H before I, because citation links find
corroboration candidates. J last among the builds, because its review
happens at Manual Validation. Total about 780 minutes of coordinator
time (708 plus 72 minutes of allowance), plus about 46 minutes of
runtime (Q7 = 2 added 150 minutes and 14 minutes of arXiv traffic). **If a Criterion 3 stop becomes necessary, the cut line is
before J**: J and K move to Sprint 10. Deferring approved work is a
Class 3 decision and is never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates**: PR #77 merged to develop (4d5115b) and PR #87 to main
  (8feffca, tagged `sprint-8`); no open sprint issue; no open PR; tree
  clean; suite 705 passed with 54 live-store tests deselected, and the 54
  passed separately. Dependency scan not applicable (standard library and
  pytest only).
- **The store (snapshot as of 2026-10-14)**: 2,093 papers (38 `read`, 14
  `screened`, 2,041 `seen`); 105 assertions. Access kinds: 1,576 arXiv,
  267 URL, 214 DOI, 125 local; 11 of the 125 local records carry a SHA-256.
  `source_links` allows only `code-of`, `dataset-of`, `version-of`,
  `superseded-by` and `responds-to` (schema CHECK), and holds no
  `version-of` link: F55 needs a new type (Q5).
- **F78**: 31 CE records (1 read, 6 read on 2026-10-13 and not recorded,
  14 unread papers, 3 synthetic-data papers, 7 repositories or a
  handbook). OpenAlex, with the team lead's key in the Authorization
  header: Thanh 2026 is open (arXiv:2511.00964); Allen 2025 is open
  (federalreserve.gov PDF); Chen 2025 (Machine Learning, Springer) and
  Te Sun 1994 (IEEE Transactions on Information Theory) are closed.
  Ishida (arXiv:2202.00395, ICLR 2023 oral) and Theisen
  (arXiv:2106.03357, NeurIPS 2021) verified by search on 2026-10-14.
- **F46**: the handoff file lists 48 facts; F45 entered the Dirac-3 and
  independent-assessment groups. Of the 29 left, 9 are ceiling facts
  (moved into E) and 20 are World, Entanglement, April 2026 and Classical
  fraud. Three already-read records yield an assertion close to a fact
  (F-402, F-604, plus F-703 and F-710 in E): compared, not re-entered.
- **F51**: `References\2026-08_Kimmey_CVQBoost-Findings.md` and the
  FourierWall2 copy share SHA-256 prefix `425358a7b4cec71f` and say "Last
  updated 2026-08-04". Phase 2 has newer CVQBoost results
  (`docs/B4_B5_HARDWARE_RESULT.md`, B4 and B5 run on Dirac-3 on
  2026-10-06; F29's ridge finding, 2026-10-13), read only.
- **F55**: Crossref `works/10.1007/s10994-025-06761-w` returns
  `reference-count` 44 with the list present, with a plain User-Agent and
  no email.
- **F57 slice**: 26 records at `seen` or `screened` under `hsbc-2026`,
  `platform:dirac-3` or `platform:dirac-3s`; none in the CE group.
- **F79**: `block_sibling_repo_writes.py` lists four paths (the two
  sibling repositories and their Claude Code project directories), none
  for Phase 2. Phase 2 is at `D:\Data\Harold\github\hsbc-qfraud-phase2`,
  private, Sprint 26 with PR 21 open.
- **F62**: `scripts/discover_candidates.py` reads the OpenAlex key from
  the environment and sends it only in the Authorization header; the key
  is present.
- **Plan-to-branch verification** (3.2.2.1): no Task A to K artifact
  exists yet; every selected F# is an open card in the master plan.

## Decisions (team lead, 2026-10-15, at approval)

The team lead answered "q1. 1 highest priority first q2 2 q3 walk me
through downloading right after this with detailed steps, while other
tasks run q4 1, but reported at Manual Validation with recommendation to
investigate further or backlog for next sprint or ?? | q5 1 q6 1 q7 2 we
need to read all that have not been read, so backlog a repeated item to
read in chunck of 74 until they have all been read. q8 1 q9 1". The plan
is approved with these answers.

- **Q1 = 1.** The slate's top 20 run most important first, Priority 10 at
  the top, under the recommendation. The format doc already says this; no
  change.
- **Q2 = 2.** F78's 7 repositories are shallow-cloned into
  `D:\Data\Harold\EvidenceBasedDB\GitHubRepos\`, outside git, each
  clone's commit recorded in its read row.
- **Q3 = 1.** The team lead downloads Chen 2025
  (DOI:10.1007/s10994-025-06761-w) and Han and Verdu 1994
  (DOI:10.1109/18.335943) by hand into `Papers\`. The step-by-step
  walkthrough was given at approval; Task E reads each when it arrives,
  and each read stays pending until then.
- **Q4 = 1, with a report.** A re-check counts only when the paper's own
  primary source answered. Every paper left due because its primary source
  failed is reported at Manual Validation with a recommendation:
  investigate now, card it for Sprint 10, or accept it as due.
- **Q5 = 1.** `cites` becomes a new `source_links` type: schema migration
  with a backup, and an ADR-0005 amendment.
- **Q6 = 1 (Class 1).** A computed "corroborated" flag beside the stored
  certainty; the assessor decides any upgrade, with the reason. ADR-0004
  amendment.
- **Q7 = 2, and a standing rule.** The first slice is 76 records: the 26
  under the consumer's contexts plus the 50 most-cited `qml` records. F57
  now releases 74 records per sprint, every sprint, until no record is
  left at `seen` or `screened` (recorded on the F57 card). Task G grows
  from 60 to 210 minutes.
- **Q8 = 1.** F62 ranks by citations per year, cross-checked against
  Semantic Scholar, with a context bonus; 25 per stream for review.
- **Q9 = 1.** F51 stays held; Task K records the check; Task A's inbound
  trial uses Phase 2's B4 and B5 hardware result.

## Premise falsifier

**The premises**: (a) the CE papers state their bounds in extractable
text, so quotes can be verified by test; (b) Crossref reference lists
cover enough of the store to make `cites` useful; (c) a paper's primary
source answers often enough that Q4's rule does not leave most papers
due forever; (d) the local paths still resolve to the files recorded;
(e) the 26-record slice holds papers that bear on the consumer's
contexts.

**What would disprove each**: (a) a quoted bound is absent from the
extracted text: the claim is read from the page image and marked so, or
dropped, never reworded; (b) fewer than 10% of the 214 DOI records return
a reference list: F55 ships with the coverage figure and no further work;
(c) a primary source fails on more than 10% of a section's papers in a
test run against saved fixtures: Q4's rule is revisited at Manual
Validation; (d) a local file is missing or its hash differs: that is
F48's finding, listed; (e) more than half the slice is refused as not
bearing on any context: the ranking is reported as wrong, not hidden.

**The checks cannot merely confirm**: the quote tests match text
extracted fresh from each local copy; the hook test injects a write into
Phase 2's path; the F74 tests run with a provider removed; F48's test
moves a real temporary file; F55's coverage is a count against the total,
not a sample.

## Risks

| Risk | Mitigation |
|---|---|
| A ceiling claim is entered as stronger than its proof (Butt's abstract over its theorem) | The assertion states the theorem's actual scope and the exceedance, quoted; certainty from the proof, not the abstract |
| An estimate is read as a proof | Bayes-error estimates enter as estimates, with their stated failure conditions; the answer document keeps "estimated" and "proved" apart |
| A write lands in Phase 2 | Task A extends the hook first; the hook test proves the block |
| A closed paper is fetched around its paywall | Never: Q3 sends it to the team lead's hand-download list |
| F56 lets non-independent evidence raise certainty | Q6's recommendation keeps the human decision; a same-vendor test proves the flag ignores it |
| arXiv refusal under the cap | All arXiv traffic serial, 18 s apart, through F52's capped fetcher; a refusal stops the run, never a retry burst |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: CLAUDE.md, the hook, its memory file and INTAKE_WORKFLOW.md name
  Phase 2 and the rule; the hook test proven by injection; the Phase 2
  guard prompt drafted; one Phase 2 result entered by the inbound path
- B: both identifier forms resolve; tests proven by injection; the five
  Massoli entries re-run; the Cerezo paper entered or refused with reason
- C: ADR-0005 A9 written; both tests proven by injection
- D: every local-access source carries a SHA-256; the check reports a
  moved file; the test proven by injection
- E: every CE record at `read` or carrying the recorded reason it is not;
  Ishida and Theisen entered; 4 PDFs downloaded with SHA-256; the
  hand-download list delivered; every quote verified by test; the answer
  document written
- F: each of the 20 facts entered, merged with an existing assertion, or
  refused with the reason
- G: the slice screened; every promoted record read and yielding; every
  refused one with its reason
- H: the ADR amendment; `cites` links for every pair a reference list
  answers; coverage reported
- I: the ADR-0004 amendment per Q6; the flag shown; the same-vendor test
  proven by injection
- J: a reviewed top list per stream; chosen papers entered; the
  hand-download list with every free-copy search recorded
- K: the hold checked and recorded per Q9
- Full suite green before every commit, gated on pytest's own exit code

## Out of scope

F39 (no model change since F67; not selected), F50 (not selected).
Downloading any paper around a paywall. Any write to
`hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
