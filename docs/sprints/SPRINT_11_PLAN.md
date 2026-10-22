# Sprint 11 Plan: Enter QCi's Answers, Then Read 200 Records and Every New Paper

**Dates**: from 2026-10-21. **No deadline.**
**Branch**: `feature/20261021_Sprint_11` (cut at the Phase 6.6 carry-forward
from Sprint 10's branch, 2026-10-21, after PR #101 merged to develop and PR
#112 to main)
**Scope** (DEFINED, team lead 2026-10-21): F94, F92, F39, F91, F57, F93,
F95. F39, F57 and F95 are permanent, so each is released as a copy with the
next free number: F99 (F39 release for Sprint 11), F96 (F57 release for
Sprint 11, 200 records) and F97 (F95 release for Sprint 11). F90 is not
selected: its 8 papers wait for the team lead's downloads. F98 is carded
for Sprint 12. F51 stays HOLD and is not in scope.

## Objective

Read more than any sprint so far, without two readers touching the same
record. First release the model rules the readers work under, and redesign
the backlog cards from spamfilter-multi's practices. Then enter QCi's
answers to Phase 2 (including the Hamiltonian confirmation and the 954
integer levels) and Phase 2's ceiling result. Then read: the Science
paper, every PDF in `Papers\` no record names, the team lead's seven new
papers with their six repositories, and the 200 most relevant unread
records, by up to five agents from one ledger.

## Tasks

Est is coordinator time for the judgment steps, calibrated from Sprint 10's
`## Actuals`: 375 estimated minutes ran in about 200 (about 53 percent);
the card estimates below are already cut on that ratio. Reviews set the
end of the reading tasks, so each reading task carries its quote checks in
its estimate, and each task that changes `store/`, `scripts/` or a hook
carries one fresh-eyes review and fix cycle. Runtime is separate, with its
dominant term. Models follow `.claude/model_assignment_heuristics.json`.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F99, F39 release for Sprint 11: models and heuristics.** The models available here listed with id, version and release date from Anthropic's models and pricing pages on the day, never from memory; changes since F88 (2026-10-18) recorded. Sprint 10's outcomes logged as `learning_log` rows from `SPRINT_10_SUMMARY.md`: the Sonnet 5.5 readers were accurate, and four of the coordinator's own reads were wrong, each caught by a fresh-eyes review (the cause I1 and I2 answered). A task pattern for parallel readers (up to 5, one ledger, no shared record) added with its review protocol; `SPRINT_PLANNING.md`'s role table kept in step; a test guards what the release adds, proven by injection | 30m | about 1 min (two documentation pages) | Claude, top tier (mandatory: model assignment) |
| B | **F94, backlog cards from spamfilter-multi's practices.** spamfilter-multi's `docs/BACKLOG_REFINEMENT.md`, master plan cards and `docs/SPRINT_PLANNING.md` read at its current commit (20d2a7ab at planning), read only. Each practice adopted, adapted or declined with a one-line reason in `docs/BACKLOG_REFINEMENT.md`'s item format: at least the value statement, the Definition of Ready, minutes always, the screenshot evidence path, and light detail for far items. The backlog-refinement skill kept in step. An adopted format rule gets a test over the master plan's cards, proven by injection; the open cards converted by hand, estimates re-derived | 45m | none | Claude, top tier (mandatory: backlog refinement) |
| C | **F92, QCi's answers of 2026-10-20 and 2026-10-21.** The three emails read in Phase 2's `docs/qci_package/` (git-ignored there, so provenance names file, SHA-256, sender and date) and `DIRAC_UNDERSTANDINGS.md` section 4 at b074780. Each answer that bears on a stored claim entered as a vendor-statement assertion under `platform:dirac-3s` or `platform:dirac-3`, hedges kept ("I assume", "I'm assuming"), related by ADR-0004 A8 (b) to the claims the card names (`contradicts` only where both cannot hold); the 954 levels entered with its unit stated as not given; the 9980 as a stated plan. Stored assertions not rewritten. Every quote checked through the verified write path | 55m | none (local files) | Claude, top tier (certainty) |
| D | **F93, Phase 2's F108 ceiling validation.** `docs/phase2/F108_CEILING_VALIDATION.md` re-read at Phase 2's commit current when the task starts (eef3349 at carding). The result entered as inbound evidence (provenance: repository, commit, file, run), each method's outcome and Phase 2's own caveat (pass rule set after the run) carried into the values; `docs/research/ceilings-ml-and-optimization.md` given a dated amendment that names the store ids, its text as written left in place | 40m | none | Claude, top tier (certainty) |
| E | **F91, the magic state cultivation paper.** Entered by `DOI:10.1126/science.aee7961` with arXiv:2512.13908 linked as `version_of`, its free PDF saved to `Papers\` under intake section 3; read, with the headline claims (error reduction factor, fidelity bound, acceptance rate) entered, each quote checked against the preprint, and the abstracts' difference ("at least" 0.9999(1)) recorded | 40m | about 20 s (one arXiv PDF, through the paced fetcher) | Claude, top tier (certainty); Sonnet 5.5 first-pass read |
| F | **F97, F95 release for Sprint 11: new papers in `Papers\` and the team lead's list.** (1) The 37 PDFs no record's `access` names (snapshot as of 2026-10-21; 17 carry an arXiv id an existing record holds) matched by DOI or arXiv id first and linked, the rest entered through the door; (2) the team lead's list on the F97 card: the NVIDIA blog article (local copy kept), arXiv:2610.24426, NBER w35905 (copied into `Papers\`; the original left as is), arXiv:2509.16410 (already `pere-2025-data-complexity-threshold-between-classical`: read, not re-entered), arXiv:2610.10629, arXiv:2610.00841, arXiv:2509.03505 (and arXiv:2609.17488, which LimiX's repository cites, checked); six GitHub repository records, each linked to its paper; (3) every entered or matched paper read, or kept at `seen` with the reason; counts before and after recorded | 120m | about 5 min: up to 8 arXiv requests serial at 18 s; 6 GitHub REST calls; one blog page | Claude, top tier (certainty); Sonnet 5.5 first-pass readers |
| G | **F96, F57 release for Sprint 11: 200 records, by relevance, up to 5 agents.** Ranked by F57's order: no record under `hsbc-2026` or a Dirac context is unread, so the release is the 200 most-cited `qml` records at `seen` or `screened` with no read row (OpenAlex counts, F80's rule), excluding any record E or F reads. Read by up to 5 agents in parallel from one ledger (below); each record read and yielding, or kept at `seen` with its reason; the count refreshed | 325m | about 65 min: up to 200 arXiv PDFs not held locally, serial at 18 s inside F52's cap, with heartbeat to a file; OpenAlex counts in a few requests | Claude, top tier (certainty); up to 5 Sonnet 5.5 first-pass readers under Task A's rules, every quote checked in the write path |

**The read ledger (E, F and G).** Before E starts, one ledger
(`manifests/sprint11_read_ledger.json`) lists every record E, F and G will
read and gives each to exactly one task and one agent group. A test fails
if any record appears twice, and the reading scripts write only the records
their group holds (team lead, 2026-10-21: "no 2 'read's should impact the
same record"). PDFs are fetched by one serial fetcher, never by the agents,
so five readers never make five arXiv streams.

**Sequence**: A, B, C, D, then E, F and G together. A first, so the
readers work under rules corrected by Sprint 10's evidence. B second,
so the cards this sprint writes use the new format. C and D are small and
independent. E, F and G run in parallel from the ledger; the coordinator's
quote checks set their pace. Total about 655 minutes of coordinator time,
plus about 70 minutes of runtime. No findings allowance: the scope is not
dominated by verification (Sprint 13 rule, `SPRINT_PLANNING.md`). **If a
Criterion 3 stop becomes necessary, the cut line is inside G**: G stops at
the count it has reached and the rest returns to F57. Deferring approved
work is a Class 3 decision and is never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-10-21): PR #101 merged to develop (45883ef) and
  PR #112 to main (5a98c36, tagged `sprint-10`); no open sprint issue; no
  open PR; suite 1,084 passed. The branch was cut from Sprint 10's branch,
  so develop's merge commit is not its ancestor, but no non-merge commit
  on develop is missing from it. Dependency scan not applicable (no
  requirements file; standard library and pytest only).
  `CHECKLIST-Phase2-pre.md`'s Sprint 10 section back-filled at Phase 1.2.
- **The store (snapshot as of 2026-10-21)**: 2,284 papers (224 `read`, 14
  `screened`, 2,046 `seen`); 793 assertions. Unread records by context:
  `qml` 1,596, `qc` 271, `ml` 130, `world` 42, `method` 12,
  `platform:classiq` 3, `platform:braket` 3; `hsbc-2026` and every Dirac
  context 0.
- **F97**: 134 PDFs in `Papers\`, 37 named by no record's `access`, 17 of
  them carrying an arXiv id an existing record holds. The six repositories
  answer on GitHub REST (licenses: Apache-2.0 for both NVIDIA repositories
  and data_complexity_framework, MIT for cace-bench, none stated for
  margin-gen-qml-classical-encoding, NOASSERTION for LimiX). LimiX's
  description cites arXiv:2609.17488, not the team lead's 2509.03505.
  `w35905.pdf` is present (1.35 MB): NBER Working Paper 35905, Farboodi,
  Kondor and Kurlat, "Credit Markets with New Screening Technologies",
  October 2026. arXiv:2509.16410 is in the store at `seen`; the other
  five arXiv ids are not.
- **F92**: the two 2026-10-21 emails read in full (Wes Dyk; Charlotte
  Brown); Phase 2 git-ignores `docs/qci_package/`. The store holds the
  claims the card names, including `dirac3-integer-variables-bounded-0-to-16`
  and `dirac3-matches-exact-optimum-on-convex-cvqboost`.
- **F98** (not in scope): Christophe Pere's `Roadmap-to-QML` answers on
  GitHub REST, last push 2026-10-20.
- **Plan-to-branch verification** (3.2.2.1): no Task A to G artifact exists
  yet; every selected F# is an open card in the master plan; F96, F97 and
  F99 are free numbers.

## Decisions (team lead, at approval)

**Q1. How many records does Sprint 11 read in all?**
1. **About 250:** G reads 200 records, and E's and F's papers come on top
   (about 45, of which 17 may already be in the store). Adds about 70
   minutes, all in E and F. Sprint 10's Q3 = 1 set the same rule.
2. **200:** E's and F's papers count toward the 200, so G reads about 155.

Recommend 1

## Premise falsifier

**The premises**: (a) Sprint 10's reader evidence supports a parallel
reader pattern with no shared record; (b) spamfilter-multi's card
practices transfer to a records repository; (c) QCi's emails bear on the
stored claims the card names; (d) Phase 2's F108 file still states the
result the card records; (e) the PDFs in `Papers\` no record names are
papers not yet in the store; (f) the 200 most-cited unread `qml` records
bear on a context often enough to yield.

**What would disprove each**: (a) two groups write the same record, or a
reader's quote fails the write-path check more often than Sprint 10's
rate: the ledger test or the check stops it, and A's rule changes follow;
(b) a practice needs a field this repository's cards cannot carry: it is
declined with the reason, not forced; (c) an answer does not bear on the
claim the card names: it is entered unrelated, with the reason; (d) the
file changed: the assertions follow the file at its commit, and the card's
figures are corrected; (e) most of the 37 match existing records: the
count says so, and they are linked, not entered; (f) more than half the
200 refused as not bearing on any context: the ranking is reported as
wrong, not hidden.

**The checks cannot merely confirm**: the ledger test reads the ledger and
the written rows, and fails on any record in two groups; the quote checks
run in the write path against text extracted fresh from each source; the
`Papers\` match is by identifier, and its counts come from the same query
before and after.

## Risks

| Risk | Mitigation |
|---|---|
| Two readers write the same record | One ledger, one group per record; a test fails on a duplicate; each script writes only its group's records |
| Five readers multiply arXiv traffic | One serial fetcher at 18 s inside F52's cap; agents read local copies only |
| A first-pass reader adds an unstated conclusion | Task A's rules first; every quote checked in the write path, every edit naming its passage (intake section 31) |
| QCi's hedged answers read as firm | Hedges quoted in the value; graded as a vendor's email statement; the 954 unit stated as not given |
| A team-lead file in `Papers\` is renamed or moved | Never: matching reads names only; NBER w35905 is copied in, its original untouched |
| A closed paper is fetched around its paywall | Never: free copies only; a closed one goes on a hand-download list |
| A repository without a license is redistributed | Repository records hold identity fields only (intake section 2); nothing is copied into git |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: the models list verified that day; Sprint 10's outcome rows logged;
  the parallel-reader pattern added; the guard test proven by injection
- B: each practice adopted, adapted or declined with its reason; an adopted
  rule tested and proven by injection; the open cards converted by hand
- C: each answer that bears on a stored claim entered with its hedge and
  related; quotes checked in the write path; no stored assertion rewritten
- D: the result entered at Phase 2's named commit with its caveat; the
  answer document amended with the store ids
- E: the paper at `read` with its assertions, the abstract difference
  recorded, or at `seen` with the reason
- F: every unnamed PDF linked, entered or given a reason; the team lead's
  seven papers and six repositories entered or matched and linked; each
  paper read or kept with its reason; counts before and after
- G: per Q1, the release read from the ledger; each record yielding or
  kept with its reason; the count refreshed; no record in two groups
- Full suite green before every commit, gated on pytest's own exit code;
  CI green on the sprint PR before Manual Validation

## Out of scope

F51 (HOLD). F90 (not selected). F98 (Sprint 12). F57's and F95's later
releases. Downloading any paper around a paywall. Any write to
`hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or `spamfilter-multi`.
