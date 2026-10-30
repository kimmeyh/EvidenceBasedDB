# Sprint 14 Plan: Read PHI-OMEGA, Review the 302 Cloud Reads, Then Learn What the Store Says

**Dates**: from 2026-10-30. **No deadline** (Phase 2's PoC notification
date, 14 Nov 2026, is the date F118's experiments aim at where possible).
**Branch**: `feature/20261029_Sprint_14` (cut at the Phase 6.6 carry-forward
from Sprint 13's branch, 2026-10-29, after PR #131 merged to develop and PR
#139 to main)
**Scope** (DEFINED, team lead 2026-10-30): F119, F95, F98, F120, F117, F118
(after F117) and F114 at 50 papers ("Q1 50 papers"). F95 and F98 are
permanent, so each is released as a copy with the next free number: F122
(F95 release for Sprint 14) and F123 (F98 release). F121 was retired into
F118 on 2026-10-30, so its number is not used. F39 was recommended and not
selected. F118 answers the team lead's "Not asked yet" questions (Q3 = 1:
in F118, after F117).

## Objective

Read the PHI-OMEGA paper first, with its posts, images and code, and enter
what it claims beside what supports it. Bring in the new Roadmap-to-QML
papers and Phase 2's Sprint 29 results. Review and apply the 302 full reads
the cloud sessions returned, each step on the cheapest model its protocol
allows, and read 50 more papers in full. Then answer, from reviewed
evidence, what the store has taught us about QC, ML and QML, what it means
for the competition approach, and which experiments to run.

## Tasks

Est is coordinator time for the judgment steps, at the cards' estimates.
Sprint 13's `## Actuals`: tasks A to F ran in about 385 active minutes
against about 1,490 estimated (about 26 percent; Sprint 12: 24 percent).
Each task that changes `store/`, `scripts/` or a hook carries one
fresh-eyes review and fix cycle. Runtime is separate, with its dominant
term. Models follow `.claude/model_assignment_heuristics.json` as Sprint
13's F111 left it (last checked 2026-10-25).

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F119, the PHI-OMEGA paper, first.** The 3-page paper read in full; a paper record with its `access`; every claim entered with its quote and certainty; the missing reproducibility material (the raw files and `simulation.py` the author's own repository says are not published) entered as an absence claim with its search scope; the LinkedIn posts, comment thread and three images entered as the author's own claims, distinct from the paper. Of the 608-file Zenodo archive and the three cloned repositories, only the parts that bear on the paper's claims are read (Q11 = 1, Sprint 13) | 60m | none (local files; the archive is a local zip) | Claude, top tier (certainty) |
| B | **F122, the F95 release.** Every PDF in `Papers\` no record names (166 on 2026-10-29: 165 are Task G's downloads of store records, which keep their records and are read by F114; 1 is A's paper); any file the team lead saves before the task is included; counts before and after | 5m | none (local files) | Claude, top tier |
| C | **F123, the F98 release.** Roadmap-to-QML's commit recorded (ea6f42a7c0 on 2026-10-29, or newer on the day); the 4 arXiv ids not in the store entered through the intake door and read in full; the 7 withdrawn or retracted marks each compared with the store, a record corrected only from the arXiv or publisher page | 60m | 4 arXiv PDFs serial at 18 s (about 2 min) inside F52's cap; the 4 reads by first-pass readers in the background | Claude, top tier (certainty); first-pass readers at Sonnet 5.5 |
| D | **F120, Phase 2's Sprint 29 results.** Read through the GitHub API at Sprint 29's merged head (PR #63, 6242b8a, merged 2026-10-30; no `git fetch` in Phase 2, so not by local refs, which stop at 22d16c3): F166 (best result per algorithm on ULB), F158 (the per-type cascade), F160 (Experiment 3's room check on IEEE-CIS) and F156 (the Henze-Penrose bound), Phase 2's numbers; F159 and F167 entered only if they state a result; the F108 and F162 document changes compared with the stored values. Each result with its limits and `SIM` or hardware tag, related by ADR-0004 A8 (b) to the claims it bears on | 90m | a few GitHub API reads | Claude, top tier (certainty) |
| E | **F117, the 302 cloud results.** First, the recovery found at planning: the local copies (`WORK/results/`) and `launches.json` are no longer in the Temp folder (cause unknown; the run log and the briefs remain), so `fetch` is rebuilt from the 302 `cloud/f114/<record>` branches, each branch's base taken as its merge-base with the Sprint 13 branch, the stray-file check unchanged, and the work folder moved out of Temp (Q3). Then the review by protocol: a script for the quote check, schema, ids and a verdict on every stored assertion; Haiku 5.5 flags a result whose own words contradict its label ("full" beside "sampled"), a HIGH suggestion with no settling passage, and figures or tables named but not entered; Sonnet 5.5 checks each changed verdict and HIGH suggestion against the passage it quotes and drafts each group's decisions; Opus 5.5 checks consistency across groups and signs off each decision file; the team lead decides any certainty change a review makes. A tier that confirms every record with no rejection is re-run with source access. Flagged results handled per Q2. Applied through `scripts/sprint13_g_reading.py` with its verified backup; each tier's outcome logged in the heuristics' `learning_log` | 20m (rebuild) + 480m | [unbounded] until piloted: the dominant term is Sonnet's per-record pass over 302 papers with their text, 5 at once; the first 5 records are the pilot, and their time sizes the rest before the next batch starts (heartbeat to a file); Haiku's pass reads the result files only; the apply a few minutes | Claude, top tier (sign-off, certainty); Haiku 5.5 and Sonnet 5.5 subagents as listed |
| F | **F114 at 50 papers.** Groups g103 to g112 of `manifests/sprint13_g_ledger.json` in ledger order (50 records, all with a local copy, among them boyd-2004-convex-optimization, whose session's partial read resumes from its branch under the prompt's "Progress and restart"; Q1). Read in full by local first-pass readers (the cloud credit is $0), each group reviewed by the coordinator as Task G's were, then applied after E's apply (one writer at a time) | 120m (coordinator review) | no estimate as a limit (no reading budget). [unbounded] until piloted: the dominant term is the whole-paper reads, 10 groups of 5, sharing the 5 reader slots with E; the first group's time sizes the rest (heartbeat to a file) | Claude, top tier (certainty); up to 5 first-pass readers at Sonnet 5.5 |
| G | **F118, what the store says, after E's apply.** The six steps on the card: the questions from Phase 2's PoC plan draft and open cards, plus the team lead's own questions (QC in general, where advantage shows and at how many qubits, how each classical model family fits a hybrid, GenAI); the inventory computed; about sixteen themes by query; up to 5 Sonnet 5.5 readers per theme group; Opus 5.5's synthesis with 10 citations checked against the store; implications per question; at least 5 experiments ranked; the Phase 2 prompt drafted; the gaps carded. One memo under `docs/spikes/`, every count dated, every finding citing assertion ids. F's applied records are included if F is applied by then | 360m | the theme readers about 1 to 2 hours in the background | Claude, top tier (synthesis); Sonnet 5.5 theme readers; Haiku 5.5 only where keywords leave a theme unclear |

**F118's estimate is 360 minutes, not the 240 in the selection list.**
The card was raised on 2026-10-30, before the selection, when the team
lead's "Not asked yet" questions were added (about six more themes and one
section per classical model family). The selection quoted the earlier
slate's figure.

**Sequence**: A first (team lead), with B after it (B links A's paper).
E's rebuild next, before anything else touches the results, so the only
copy is on disk again. Then C and D, while E's Haiku and Sonnet passes run
in the background; F's readers share the five reader slots with E's
passes. E's apply first, F's apply second, then G. Total about 1,195
minutes at the cards' estimates; at Sprints 12 and 13's ratios, about 290
to 330 active minutes, plus the reader time in the background. No findings
allowance: the scope is not dominated by verification, though E's review
will find some results to send back (Q2). **If a Criterion 3 stop becomes
necessary, the cut line is inside F**: F stops at the groups it has
reviewed and the rest return to F114. Deferring approved work is a Class 3
decision and is never made unilaterally.

**Full suite** (team lead, 2026-10-23): twice, before the Manual
Validation hand-over and after any retrospective improvements. Every other
commit runs `python scripts/run_suite.py --changed`.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-10-30): PR #131 merged to develop (bb4cb80) and
  PR #139 to main (952c9e3, tagged `sprint-13`, retitled "Sprint 13:
  Develop to Main"); no open sprint issue; working tree clean. Dependency
  scan not applicable (no requirements file; standard library and pytest
  only).
- **The store (snapshot as of 2026-10-29)**: 2,335 papers (1,653 `read`, 1
  `screened`, 681 `seen`); 10,735 assertions (4,059 HIGH); 654 unread with
  no read row.
- **F119**: the paper, both references, the three images the PHI-OMEGA
  reference names, the Zenodo zip and the three cloned repositories are
  all in place under `D:\Data\Harold\EvidenceBasedDB\`.
- **F122**: 374 PDFs in `Papers\`; 166 named by no record (165 Task G
  downloads dated 2026-10-25, 1 new file, A's paper).
- **F123**: Roadmap-to-QML at ea6f42a7c0 (2026-10-27), 9 commits after
  a239747648; 34 arXiv ids added, 30 already in the store, 4 not.
- **F120**: Phase 2's Sprint 29 merged on 2026-10-30 (PR #63, head
  6242b8a; develop to main by PR #73). Local refs stop at 22d16c3, and no
  `git fetch` is run in a sibling repository, so D reads through the
  GitHub API.
- **F117**: 302 `cloud/f114/<record>` branches on GitHub and as local
  remote-tracking refs; a sample branch's merge-base with the Sprint 13
  branch is 6eafb0d, its launch commit. The local `WORK/results/` folder
  and `launches.json` are gone (found 2026-10-30); `WORK/logs/run.txt` and
  the 329 group briefs remain. `fetch` needs `launches.json` for each
  branch's base, hence E's rebuild.
- **F114**: groups g103 to g112 hold 50 records, each with a local copy;
  udaru-2025 (g076, image-only, needs F115, not selected) and the two
  abbas-2020 records (g079) are outside these groups.
- **Plan-to-branch verification** (3.2.2.1): no Task A to G artifact exists
  yet; every selected F# is an open card in the master plan; F122 and
  F123 are free numbers.

## Decisions (team lead, 2026-10-30)

- Scope as above; F114 at 50 papers; Q3 = 1 (F118 answers the team
  lead's questions after F117); PR #139 retitled (Q2 = 1).

Open at approval:

- **Q1**: which 50 papers F114 reads.
- **Q2**: what happens to a cloud result E flags as not read in full.
- **Q3**: where the cloud results and briefs live from now on.

## Premise falsifier

**The premises**: (a) the PHI-OMEGA paper's central claim has no support
in the paper itself; (b) the 4 new Roadmap papers bear on a context;
(c) Phase 2's Sprint 29 documents add results the store does not hold;
(d) the 302 cloud results are sound enough that most are applied, and the
cheaper tiers find what the card says they can; (e) the store can answer
most of F118's questions.

**What would disprove each**: (a) a proof, theorem or reproducible data
found in the paper or the parts of the archive it names: entered and
graded on it, and the card's first look recorded as wrong; (b) a paper
refused as bearing on no context: reported with its reason; (c) every
Sprint 29 value already stored: D reports "confirmed by name"; (d) more
than a quarter of the 302 sent back, or Haiku's flags missing what
Sonnet's pass finds: reported per tier in the `learning_log`, and the
split revised; (e) a question with no assertion behind it: the memo says
so and cards the gap, never fills it from memory.

**The checks cannot merely confirm**: the quote checks run in the write
path against text extracted fresh from each source; E's rebuild refuses a
branch that touches anything outside its folder, as `fetch` did; each
Phase 2 value is compared with its document's text at a named commit; G's
10 citations are checked against the store by id.

## Risks

| Risk | Mitigation |
|---|---|
| The only copy of the 302 results is on GitHub branches | E's rebuild runs first and saves them outside Temp (Q3); the branches are never deleted |
| A rebuilt base lets a stray file through | The base is the merge-base with the Sprint 13 branch, which holds every launch commit; the stray check reads every commit from it |
| A cheap tier passes a defect | The protocol, not the tier, finds defects (heuristics `learning_log[0]`); a tier that rejects nothing is re-run with source access |
| A cloud reader labeled a read "full" that it sampled (Boyd) | Haiku flags it from the result's own words; Q2 decides what happens to it |
| Two applies write the same store at once | E's apply, then F's, then G reads; one writer at a time |
| The usage limit stops the session mid-read | Each group's file is its own checkpoint; the status note makes a restart exact |
| F118's memo states more than the evidence holds | Every finding cites assertion ids; 10 citations checked; a qubit count only where an assertion states one |
| A self-published paper's claims are graded as settled | A's claims stay at the author's own claim unless the paper or its code settles them |
| Phase 2's documents change after D reads them | Provenance names the commit; a later change is a later card |
| A write reaches a sibling repository | Phase 2 read only, through the GitHub API; no fetch in a sibling repository |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A: the paper read in full and recorded; every claim with its quote and
  certainty; the absence claim with its search scope; the posts, comments
  and images entered as the author's own claims; a second apply writes
  nothing
- B: every unnamed PDF handled; counts before and after
- C: the list's commit recorded; the 4 new papers entered and read in
  full, or given a reason; the 7 marks compared with the store
- D: each Sprint 29 result entered with its limits and tag, and related;
  each changed value corrected or confirmed by name; a second apply
  writes nothing
- E: the 302 results on disk outside Temp, every branch checked for stray
  files; each of the 302 with a decision; flagged results handled per Q2;
  the apply's counts before and after; a second apply writes nothing;
  each tier's outcome in the `learning_log`
- F: the 50 records read in full, or kept with their reason; each group
  reviewed and applied; the counts before and after
- G: the memo with its questions and their Phase 2 source; a section per
  theme citing assertion ids; 10 citations checked; an implication per
  question; at least 5 experiments ranked; the Phase 2 prompt drafted;
  the gaps carded
- Full suite before Manual Validation, through `scripts/run_suite.py`;
  every other commit gated on `--changed` and CI's set; CI green on the
  sprint PR before Manual Validation

## Out of scope

F39 (recommended, not selected). F115 and F116. F57's release (F114 and
F117 carry the reads this sprint). F114 past its 50 papers, and its
image-only and abbas-2020 records. F90 and F51 (HOLD). Downloading any
paper around a paywall. Any write to `hsbc-qfraud-phase2`,
`hsbc-quantum-fraud-2026` or `spamfilter-multi`.
