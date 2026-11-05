# Sprint 15 Summary: Read Every Page, Figures and Images Included, Then Read 100 More Papers

**Dates**: 2026-11-01 to 2026-11-05. **Branch**: `feature/20261031_Sprint_15`.
**PR**: #149 into develop. **Issues**: #150 to #162 (Tasks A to M).
Sources: the plan (`SPRINT_15_PLAN.md`), `git log`, the issues, the
retrospective (`SPRINT_15_RETROSPECTIVE.md`), `.claude/sprint_status.json`,
intake sections 60 to 67 (`docs/INTAKE_WORKFLOW.md`). Every count below is
a snapshot as of 2026-11-05.

## What shipped

- **F131 and F132 (Tasks A and B, #150 and #151).** The F95 and F98
  releases found nothing new (`Papers\` unchanged beyond F123's 4;
  Roadmap-to-QML still at ea6f42a7c0).
- **F125 (Task C, #152).** Re-entry groups for records a reviewed group
  left unread; 4 re-entry groups read, reviewed and applied.
- **F126 and F127 (Tasks D and E, #153 and #154).** The page-fixer cases
  and the latent defects, each with a test proven red; the
  muta-hardware-scope-photonic-gkp anchor corrected to p.8.
- **F115 (Task F, #155).** Image-only pages read by RapidOCR 3.10.0 over
  ONNX Runtime 1.31.1, in its own virtual environment outside git; the
  text cached outside git, marked as OCR, with the engine and models in
  provenance; udaru-2025-qml-credit-risk read in full from it.
- **F116 (Task G, #156).** Readers render and view each figure and
  embedded image; a value read only from a figure is marked so and never
  HIGH on the figure alone. The pilot was ledger group g114.
- **F114 (Task H, #157).** The Sprint 15 reader prompt and review
  protocol, each new rule with a test proven red; 100 papers read in
  full, figures and image pages included (g113-r1 to g133, with the
  re-entry groups).
- **F133 (Task I, #158).** The F57 release: the next 100 file-backed
  ledger records (g134 to g154), read and reviewed as H's were.
- **F128 (Task J, #159).** The gaps F118 found: 9 free targets read in
  full; the rest on the hand-download list with their reasons.
- **F124 (Task K, #160).** F151, F153 and F154's documents re-read at
  Phase 2's develop head; each value corrected or confirmed by name.
- **F129 (Task L, #161).** 10 LOW grades resting on a textbook fact
  proposed HIGH; all 10 set HIGH at Manual Validation (Q2 = 1).
- **F130 (Task M, #162).** Phase 2's Sprint 30 results from merged commit
  43bc362: 5 records, 9 HIGH assertions, F166 repointed.

Store: 2,345 -> 2,358 papers (1,789 -> 1,805 at `read`); 23,653 -> 34,891
assertions (8,167 -> 11,071 HIGH). Papers at `seen` or `screened` with no
read row: 524 -> 522.

## Manual Validation decisions

- At planning (2026-11-01): Q1 = 1, Q2 = 2, Q3 = 3 with the team lead's
  OCR qualification, Q4 = 1; F115's engine changed to RapidOCR.
- At Manual Validation (2026-11-04): Q1 = 1 (36 certainty changes as
  recommended), Q2 = 1 (F129's 10 HIGH), Q3 = 2 (five stay LOW), Q4 =
  both MODERATE ("as the reviewer graded them, because neither paper
  states the absence itself"), Q5 = 1, Q6 = 2 (context to `qc`), Q7 = 2
  (Sprint 16's F57 release follows F57's ranking), Q8 = 2 (dalzell stays
  one LOW), Q9 carded as F136.
- Retrospective (2026-11-05): "Very Good" in every rated category;
  "none" for minor updates, backlog updates and open questions.

## Actuals

Wall clock from `git log` and the status notes (local time). Plan
estimate for A to M: about 1,205 minutes at the cards' estimates.

- Plan approved 2026-11-01 13:59; Manual Validation hand-over 2026-11-04
  18:09. The reads of H, I and J ran in the background from 2026-11-01
  evening to 2026-11-04 06:20, up to 5 readers at a time, with usage-limit
  pauses waited out.
- After Manual Validation (2026-11-04 evening to 2026-11-05): 36
  escalations recorded, 24 groups finalized and applied (one trial, one
  live apply), the decisions script, two review-and-fix rounds and the
  `--changed` fixes.
- Avoidable time: about 25 minutes when the first trial store lacked its
  text cache; about 23 minutes per applier run on quote checks of
  unchanged groups (F136).
- Subagents: Sonnet 5.5 readers and reviewers per group, the Opus 5.5
  sign-off and cross-group pass, and one fresh-eyes reviewer per code or
  store commit.

## Findings surfaced

- A team-lead decision could be undone by a rerun of an older script or a
  later review. Guarded twice: the applier keeps a grade whose reasons
  carry "the team lead's decision at", and `sync_assertion` refuses any
  sync dated before a row's Manual Validation note.
- A trial store copy without its text cache re-reads every PDF.
- Two readers skimmed reference pages and one reviewer decided items from
  quotes alone; each was sent back, and reviewer prompts now forbid
  subagents.
- Older tests pinned to data (a count, a quote) went red when the team
  lead's decisions changed that data; each now derives what it checks.
