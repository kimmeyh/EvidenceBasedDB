# Sprint 15 Plan: Read Every Page, Figures and Images Included, Then Read 100 More Papers

**Dates**: from 2026-11-01. **No deadline** (Phase 2's PoC notification
date, 14 Nov 2026, is the date F128's reads aim at where possible).
**Branch**: `feature/20261031_Sprint_15` (cut at the Phase 6.6 carry-forward
from Sprint 14's branch, 2026-10-31, after PR #140 merged to develop and PR
#148 to main; tagged `sprint-14`)
**Scope** (DEFINED, team lead 2026-11-01): F114 (next release, 100
papers), F125, F126, F127, F128, F115, F95, F98, F124, F129, F116, F57 and
F130. F95, F98 and F57 are permanent, so each is released as a copy with
the next free number: F131 (F95 release for Sprint 15), F132 (F98 release)
and F133 (F57 release). The team lead marked F128, F95 and F98 "always in
addition to F114": their reads do not count toward F114's 100. F39 was not
selected.

## The team lead's question on F114, answered

Team lead, 2026-11-01: "Hoping this process was updated to ensure the
entire paper was read and processed (no time limit per paper), nothing left
to be done later. Updated for all the best practices found while reading
the last couple of hundred papers (models...)".

- **Already true, since 2026-10-25**: no time limit and no assertion cap per
  paper. Every section, appendix and proof is read, and each theorem is
  entered with its statement and conditions. `tests/test_reader_prompts.py`
  fails on any reader prompt that names a part-read or a cap.
- **Not yet true: two parts of a paper are still left for later.**
  - **Figures.** The current prompt counts a plot as read when its caption
    and the text around it are read. A result shown only in a graph is never
    entered. F116 closes this.
  - **Page images.** A page with no text layer gives the reader nothing.
    udaru-2025-qml-credit-risk is all images. F115 closes this.
  - So this plan runs F115 and F116 BEFORE F114's reads (Q1), and the 100
    papers are read with figures and image pages included.
- **Not yet in the prompt: Sprint 14's lessons.** Task H's first step writes
  them into a Sprint 15 reader prompt and review protocol (listed under
  Task H), each guarded by a test proven red.

## Objective

Close the three tooling defects F114's last release left (F125, F126,
F127). Give every reader the text of image-only pages (F115) and the
ability to read figures and images (F116). Then read 100 more of F114's
papers in full, with nothing left for later, under a reader prompt that
carries Sprint 14's lessons. Around that: the reading targets F118's memo
found (F128), the F95, F98 and F57 releases, the three stale Phase 2 source
records (F124), the LOW grades resting on a textbook fact (F129), and
Phase 2's Sprint 30 results if they merge in time (F130).

## Tasks

Est is coordinator time for the judgment steps, at the cards' estimates.
Sprint 14's `## Actuals`: tasks A to G ran in 744 minutes against about
1,195 estimated (about 62 percent; Sprint 13: 26 percent). Each task that
changes `store/`, `scripts/` or a hook carries one fresh-eyes review and
fix cycle. Runtime is separate, with its dominant term. Models follow
`.claude/model_assignment_heuristics.json` (updated 2026-10-30, with
Sprint 14's `learning_log` row).

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F131, the F95 release.** Every PDF in `Papers\` no record names (none new on 2026-11-01 beyond F123's 4, already entered); any file the team lead saves before the task is included; counts before and after | 5m | none (local files) | Claude, top tier |
| B | **F132, the F98 release.** Roadmap-to-QML's commit recorded (ea6f42a7c0 on 2026-11-01, or newer on the day); a newer commit's diff entered and read in full | 5m | one GitHub REST read | Claude, top tier |
| C | **F125, a way back in.** A record left unread in a reviewed group (8 today, among them g113's three chen-2026 records) can be read, reviewed and entered under its own group file and review file; `scripts/sprint13_g_status.py` reads `work\f114\local\` | 30m | none | Claude, top tier |
| D | **F126, page anchors.** The three page-fixer cases ("p.12-15.3", a stray "of 10", "p.12a") each with a test proven red, then green; the muta-hardware-scope-photonic-gkp anchor corrected from p.9 to p.8 through a tested path | 20m | one store write, with its verified backup | Claude, top tier |
| E | **F127, latent defects.** The merged-branch refusal, the clash check's substring match, the builder's three edge cases, and the refusal guard that ignores a later reversal (9 QCI Dirac papers): each with a test proven red, then green | 20m | none | Claude, top tier |
| F | **F115, text from page images.** Every local source whose text layer is empty or nearly empty, page by page, listed with its date; those pages converted by RapidOCR (cross-platform, pip-installed into its own virtual environment outside git, pinned in `requirements-ocr.txt`; amended at approval from Windows' built-in OCR, see "Decisions for the team lead"), from page images rendered by `pdftoppm`; the text kept outside git in the text cache, marked as OCR, with the engine, its version, the ONNX Runtime version and the model files named in provenance; the quote check reads it; the OCR grading rule per Q3; a test proven red when an image-only page is read as empty without a flag. udaru-2025-qml-credit-risk is then read in full as the first of F114's 100 | 120m | [unbounded] until the scan runs: the dominant term is `pdftotext` over every local source (cached by SHA-256, so mostly cache hits), then OCR at about 1 to 3 s per page on the pages found | Claude, top tier |
| G | **F116, figures and images.** Readers render each page that holds a figure or an embedded image (`pdftoppm`, `pdfimages`) and view it. For each figure: its kind, what it shows (axes, trend, marked values), and the passage that confirms it, quoted, or a statement that no text confirms it. A value read only from a figure is marked so and never graded HIGH on the figure alone. A pilot on 5 papers whose key results are in plots sizes the cost per figure before Task H's readers start | 180m | the pilot's 5 papers by one reader; the per-figure time it measures sizes Task H | Claude, top tier; one Sonnet 5.5 pilot reader |
| H | **F114, 100 papers, with nothing left for later.** Step 1: the Sprint 15 reader prompt and review protocol (below), each new rule with a test proven red. Step 2: the 100 papers: udaru (after F), the 8 records left unread in reviewed groups (after C), then ledger order from g114. The 18 papers the team lead kept out stay out. Read in full by up to 5 local first-pass readers, figures and image pages included; each group reviewed by a Sonnet 5.5 reviewer with the paper's text; the coordinator's sign-off and a cross-group pass on Opus 5.5; the team lead decides each certainty change. Applied by `scripts/full_read_apply.py` after a trial on a store copy, with its verified backup | 60m (prompt) + 240m (review and sign-off) | no estimate as a limit (no reading budget). [unbounded] until piloted: the dominant term is the whole-paper reads with their figures, 20 groups of 5; the first group's time sizes the rest (heartbeat to a file) | Claude, top tier (sign-off, certainty); Sonnet 5.5 readers and reviewers |
| I | **F133, the F57 release** (size per Q2). The 11 records that name only a local file first, then F57's relevance ranking, from the 524 with no read row; read under H's prompt, after H's readers, sharing the 5 reader slots; reviewed and applied as H's are | 240m (Q2 = 2: 100 records) | no estimate as a limit; sized from H's measured time per paper | as H |
| J | **F128, the gaps F118 found.** Each target placed: a free copy (arXiv or the publisher) fetched and read in full under H's prompt, in addition to the 100; a book or paywalled source put on the hand-download list with its reason. Targets on 2026-11-01: Gidney and Ekera (1905.09749), Babbush et al. 2021 (2011.04149), Chakrabarti et al. (2012.03819), Woerner and Egger (1806.06893), Stoudenmire and Schwab (1605.05775), XGBoost (1603.02754), LightGBM (NeurIPS 2017), a QRAM architecture paper (0708.1879) and its critique (2305.10310), Ferrari Dacrema et al. (not in the store), Faryad in full (stored, read in part), Dal Pozzolo 2014 (stored, unread), Nielsen and Chuang (book), vendor native-gate documents, a concept-drift source for card fraud, tuned anomaly-detection baselines on fraud, and the 3 split candidates | 30m + 120m (review) | about 12 papers at F52's 18 s per arXiv request; reads in the background | as H |
| K | **F124, three Phase 2 records.** F151, F153 and F154's documents re-read whole at Phase 2's develop head (af03165 on 2026-11-01, through the GitHub API; no fetch in a sibling repository); each stored value corrected or confirmed by name; the earlier read and blob SHA-256 kept; the local-file check passes | 45m | a few GitHub API reads | Claude, top tier (certainty) |
| L | **F129, LOW grades on a textbook fact.** The 11 keyword candidates each read against its passage and the cross-group rule; a sample of the keyword cut's misses checked; each proposed change put to the team lead as a certainty change at Manual Validation | 30m | none | Claude, top tier |
| M | **F130, Phase 2's Sprint 30 results**, once PR #74 merges (open on 2026-11-01): F176, F169, F170, F171 and F174 (once its run completes), each from the merged commit, linked `supports` or `contradicts` to the LOW claims it bears on. If PR #74 has not merged by the Manual Validation hand-over, per Q4 | 60m | a few GitHub API reads | Claude, top tier (certainty) |

**Task H, step 1: what the Sprint 15 reader prompt and review protocol add.**
The prompt is Sprint 14's (`manifests/sprint14_f114_reads/READER_PROMPT.md`)
with these changes, each from a Sprint 14 finding:

- **Figures and images are read, not skipped** (F116). The caption-only
  exemption is removed. A reader that cannot view a figure says so in
  `not_read`, and the read is then `partial`.
- **Image-only pages are read from their OCR text** (F115), and each quote
  from them is marked as OCR.
- **`read_extent` "full" needs its evidence**: the reader lists each
  section and appendix read and the number of figures read. A Sprint 13
  cloud reader labeled Boyd "full" after sampling it.
- **A reader never changes a stored assertion's context.** It proposes a
  context only for a new assertion. In Sprint 14 a reader's nearest-fit
  context replaced two stored contexts that no review had decided.
- **Anchors are PDF page numbers, and each quote is on the page it cites**
  (F126).
- **One claim per assertion.** F117 found three assertions that each held
  two claims of different grades.
- **Grade suggestions follow the cross-group rule**: a textbook-standard
  result is background and is not by itself a reason for LOW (F129).
- **A paper that bears on no context is still read in full.** Its
  `why_not` is a suggestion; whether it enters is the team lead's decision
  (Sprint 14 Manual Validation Q2).
- **The review protocol is Sprint 14's**, with its guards: a Sonnet 5.5
  reviewer per group with source access; a cross-group pass and the sign-off
  on Opus 5.5; a trial apply on a store copy that lists every field no
  review item decides (Q2 of Sprint 14's retrospective) and every refusal
  at once (Q4); one writer at a time; settlement text edited by hand (Q1).
- **Guard**: `tests/test_reader_prompts.py` gains a check that a prompt from
  Sprint 15 on requires figures to be read and names the OCR text, proven
  red by injection.

**Sequence**: A and B first (5 minutes each). C, D and E next: they change
the tools H uses. F, then G's pilot, then H's step 1. H's readers then
start: udaru first, then the 8, then g114 on. J's reads and I's reads share
the 5 reader slots after H's first groups, in that order. K and L run while
the readers work. M when PR #74 merges. One apply at a time: H, then I and
J. Total about 1,205 minutes at the cards' estimates (1,085 at planning,
plus 120 for Q2 = 2); at Sprint 14's ratio, about 750 active minutes, plus
the reader time in the background. No
findings allowance: the scope is not dominated by verification. **If a
Criterion 3 stop becomes necessary, the cut line is inside I**: I stops at
the records it has reviewed, and the rest return to F57. Deferring approved
work is a Class 3 decision and is never made unilaterally.

**Full suite** (team lead, 2026-10-23): twice, before the Manual
Validation hand-over and after any retrospective improvements. Every other
commit runs `python scripts/run_suite.py --changed`.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates** (2026-11-01): PR #140 merged to develop (9059061) and
  PR #148 to main (934a416, tagged `sprint-14`); no open sprint issue
  (#145 to #147 closed by hand at Phase 1.2); working tree clean before
  this plan. Dependency scan not applicable (no requirements file;
  standard library and pytest only).
- **The store (snapshot as of 2026-11-01)**: 2,345 papers (1,789 `read`);
  23,653 assertions (8,167 HIGH); 524 with no read row. F114: 1,091 of
  1,430 records without a full read dated 2026-10-26 or later, in 227
  groups.
- **F115**: no Tesseract on this machine. `pdftoppm` (MiKTeX) rendered
  udaru's page 1 at 200 dpi, and Windows' built-in OCR
  (`Windows.Media.Ocr` through Windows PowerShell 5.1; PowerShell 7 cannot
  load it) returned the page's text ("Quantum Machine Learning For Credit
  Risk: A Next-Generation Approach To Risk Assessment ... DOI:
  10.63278/jicrcr.vi.3419"). Its maximum image dimension is 10,000 pixels.
  No install is needed.
  **Superseded at approval (2026-11-01)**: the team lead asked for a
  cross-platform engine. RapidOCR 3.10.0 (Apache-2.0) over ONNX Runtime
  1.31.1 (MIT), installed by pip into a scratch virtual environment, read
  the same page to 103 lines in 5.9 s, with the title, DOI and abstract
  correct. Its three models (PP-OCRv6 detection and recognition, and a
  direction classifier) ship inside the wheel with their SHA-256 in the
  wheel's RECORD, so no model is downloaded at run time. An install into
  the main interpreter would raise numpy from 1.26.2 to 2.5.4, so the
  engine gets its own virtual environment. Pip-installable on Linux and
  macOS by its packaging; verified on Windows only.
- **F116**: `pdftoppm` and `pdfimages` are present; the Read tool views a
  rendered PNG, so a reader can see a figure.
- **F128**: of the targets, 9 named by arXiv id are not in the store; Faryad
  is stored and read in part; Dal Pozzolo 2014 is stored with no read row;
  Ferrari Dacrema's feature-selection paper is not in the store.
- **F124**: the three records still point at Phase 2 commit 10086da;
  Phase 2's develop head is af03165 (2026-10-30, GitHub API).
- **F130**: Phase 2's Sprint 30 PR #74 is open.
- **F131 and F132**: `Papers\` holds 378 PDFs, none new beyond F123's 4;
  Roadmap-to-QML is at ea6f42a7c0.
- **Plan-to-branch verification** (3.2.2.1): no Task A to M artifact
  exists yet; every selected F# is an open card in the master plan; F131,
  F132 and F133 are free numbers.

## Decisions for the team lead

Team lead, 2026-11-01, approving the plan: "q1 1 q2 2 q3 3 however
anything in an ocr of a pdf is likely confirmed in the pdf for ocr of
images not in pdf's I would hold high's for things that can be otherwise
corroborated, otherwise medium is the highest. q4 1". And on F115: "would
prefer a cross platform OCR ability even if for Windows this is the best
one (what is the next best alternative python package)?"

- **Q1 = 1**: F115 and F116 run before F114's reads, so the 100 papers are
  read with figures and image pages included.
- **Q2 = 2**: the F57 release (Task I) is 100 records, about 240 minutes of
  review.
- **Q3 = 3, with the team lead's qualification.** The rule as recorded:
  - Text OCR'd from a page of a stored PDF is graded the same as text-layer
    text: HIGH is allowed.
  - Text OCR'd from an image file that is not inside a PDF (a picture file
    entered as a source) is HIGH only when another source corroborates the
    claim; otherwise MEDIUM is the highest grade.
  - This is consistent with Task G's rule: Q3 is about OCR text (words read
    by the engine), while G's rule is about a value estimated by eye from a
    plot, which is never HIGH on the figure alone.
- **Q4 = 1**: if Phase 2's PR #74 has not merged by the Manual Validation
  hand-over, F130 returns to the backlog for Sprint 16.
- **F115's engine**: changed from Windows' built-in OCR to RapidOCR, the
  cross-platform choice (pre-flight above). Disclosed in the approval
  acknowledgment: the planning message said nothing needed installing; the
  engine now needs a pip install into its own virtual environment.

## Premise falsifier

**The premises**: (a) figures hold results the text alone does not give;
(b) RapidOCR gives text good enough for the quote check; (c) the
Sprint 15 prompt leaves nothing in a paper unread; (d) the F128 targets
answer the gaps F118 named; (e) Phase 2's F151, F153 and F154 documents
changed values the store holds.

**What would disprove each**: (a) G's pilot finds no figure value that the
text lacks: G reports it, and figure reading stays a check rather than a
source; (b) OCR text fails the quote check on quotes a reader took from
the page image: F reports the failure rate, and Q3's rule applies; (c) a
review finds a part of a paper not read and not named in `not_read`: the
read is sent back; (d) a target read in full does not state what the gap
needs: J says so and the gap stays open; (e) every value unchanged: K
reports "confirmed by name".

**The checks cannot merely confirm**: the quote check runs against text
extracted fresh from each source, and for OCR text against the OCR output,
not the reader's copy; G's pilot compares figure values with the text
before any rule is set; H's reviewers read the paper, not the reader's
summary.

## Risks

| Risk | Mitigation |
|---|---|
| Reading figures raises each paper's read time a lot | G's pilot measures it before H starts; no budget, so the time is reported, not cut |
| OCR misreads a symbol, so a quote passes or fails wrongly | OCR text is marked; Q3's grading rule; quotes from OCR pages checked against the page image |
| A reader relabels a stored context or grade | The applier's stored-context guard and the "undecided" list on every trial apply |
| A usage limit stops a reader mid-paper | Progress and restart, unchanged; each group file is its own checkpoint |
| Two applies write the store at once | One writer at a time: H, then I and J |
| F130 waits on a merge outside this repository | Q4 decides now what happens if it has not merged |
| A write reaches a sibling repository | Phase 2 read only, through the GitHub API; no fetch in a sibling repository |
| The email address or the OpenAlex key leaks | The key goes only in the Authorization header and is never logged; no request carries the email |
| CI turns red unnoticed | The Stop hook holds Phases 5 to 7 while CI is not green |
| Session continuity | `sprint_status.json` note at every task start, with the clock time |

## Definition of Done

- A, B: each release's counts before and after; the list's commit recorded
- C, D, E: each defect with a test proven red, then green; the muta anchor
  corrected; the status script reads the local work folder
- F: the list of image-only sources with its date; udaru's text given to
  the quote check; the test proven red; OCR provenance on each such source
- G: the pilot's 5 papers with each figure entered or named; the cost per
  figure measured
- H: the Sprint 15 prompt with its test proven red; the 100 papers read in
  full, figures and image pages included, or kept with their reason; each
  group reviewed and applied; the counts before and after; a second apply
  writes nothing
- I: the release's records read in full or given a reason; applied
- J: each target in the store and read, or on the hand-download list with
  its reason
- K: each of the three documents re-read; values corrected or confirmed;
  the local-file check passes
- L: each candidate read; each proposed change put to the team lead
- M: per Q4
- Full suite before Manual Validation, through `scripts/run_suite.py`;
  every other commit gated on `--changed` and CI's set; CI green on the
  sprint PR before Manual Validation

## Out of scope

F39 (not selected). F114 past its 100 papers. The 18 papers the team lead
kept out in Sprint 14. F90 and F51 (HOLD). Downloading any paper around a
paywall. Any write to `hsbc-qfraud-phase2`, `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.
