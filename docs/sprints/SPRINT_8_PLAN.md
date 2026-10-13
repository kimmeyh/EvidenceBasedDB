# Sprint 8 Plan: Read QCi's Newest Guide, Then Build the Yearly Re-check

**Dates**: from 2026-10-10. **No deadline.**
**Branch**: `feature/20261010_Sprint_8` (cut at the Phase 6.6 carry-forward
from Sprint 7's branch, 2026-10-10, after PR #68 and PR #76 merged)
**Scope** (DEFINED, team lead 2026-10-10): F65, F63, F64, F60, F61, and an
F39 release, registered as F67 ("F39 as Haiku 5.5 was released and we will
want to include in the list of models"). F66, carded the same day with a
Sprint 8 target, was added at approval (Q1 = 1) and runs first.

## Objective

QCi published a user guide for the Dirac-3S, its upgraded Dirac-3, in
September 2026. This sprint reads it in full and classes every Dirac-3
assertion the store holds against it, so the hsbc work can see what changed
on the newer system; the two Dirac-3 admissions found in Sprint 7 enter in
the same task. It then builds the staggered yearly re-check the team lead
designed at Sprint 7 Manual Validation, so 1,500 papers loaded in one month
never come due in one sprint. Two smaller sourcing items follow: the
mislabeled QMLPapers file and the Massoli survey list, which sets up F62's
discovery for Sprint 9. It opens with the model check, since Haiku 5.5 is
now listed.

## Tasks

Est is coordinator time for the judgment steps. Calibration from Sprint 7's
`## Actuals`: code tasks ran well under estimate (B about 40 minutes against
210, D 4 against 60); reading tasks measured 15 to 18 minutes but are lower
bounds, since work before a commit is invisible to `git log`. The carded
estimates are kept: they are likely high for C, and B carries the findings
allowance below. Runtime is separate, with its dominant term. Model
assignments follow `.claude/model_assignment_heuristics.json` as Task B
leaves it. Task D changes `store/` and gets a fresh-eyes reviewer at its
commit, with one review-and-fix cycle in its estimate.

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F66, develop as the default branch.** The team lead's three phases as carded: Phase A inspect and report (re-checked at approval: the default is still `main`); Phase B only the changes the team lead approves (default to develop, `git remote set-head`, CI on PRs into develop AND main, the release step written down, a test that fails if `ci.yml` stops triggering on either branch); Phase C verify and report. Its own feature branch and PR into develop; no merge, no branch deleted | 60m | about 2 min (GitHub API) | Claude; the team lead approves Phase B and merges |
| B | **F67, F39 release for Sprint 8.** Re-read the models page and the pricing page the same day; record per tier what changed since F59 (2026-10-06); the haiku tier moves from Haiku 4.5 to Haiku 5.5 with its id, price, context, output and retirement date; the Developers role to Haiku 5.5 (Q6 = 1), patterns with a Sonnet rationale staying; the SPRINT_PLANNING.md role table and the test agree | 30m | about 2 min (two pages) | Claude, top tier |
| C | **F65 with F63, the Dirac-3S guide and the two admissions.** Enter the Dirac-3S User Guide (Rev A, 38 pp., SHA-256 `0ddbc533...5971`) as a source, as the Dirac-3 guide v0.0.4 was (local path plus SHA-256); read it in full; class each of the 19 assertions in `platform:dirac-3` (14 from F45) against it as confirmed, changed, superseded or not addressed, recorded per Q3 = 1 (a separate `platform:dirac-3s` context, "they should be separate"; the Dirac-3 assertions untouched; common claims the guide confirms listed and linked `supports`, "ok to list common assertions, facts... that you can confirm"); new Dirac-3S claims as `vendor-self-claim` with page anchors; the team lead's listed items, if received (not yet received); then F63's two quotes from arXiv:2407.04512 (p.15, p.6) with relations to the existing Dirac-3 assertions. Every quote verified verbatim against the local PDF text by test. **Findings allowance 30%** (SPRINT_PLANNING.md): classing 19 assertions against a new guide produces relations and assertions that cannot be counted yet | 240m + 72m allowance | none (local files; the guide's text layer extracts, 110 to 238 words per sampled page) | Claude, top tier (certainty) |
| D | **F64, the staggered 12-month re-check.** Section = SHA-256 of the record id, first 8 hex digits as an integer, mod 24 (computed, never stored); last check = the latest `probed_on` across the record's probe fields; next re-check = the first start of its section at least 10 months after the last check (computed, never stored); `probe_reference_fields.py --due <date>` selects the due records, replacing `--stale` as the Phase 1.3 check; the brief check adds arXiv version detection (the abstract page's latest `vN` against the local PDF's first-page stamp), new parsing tested on saved page fixtures, never a live request in a test; output three lists (re-pull, withdrawn, newly published), nothing downloaded; `view.py paper <id>` shows the section and the date; a never-checked record uses the same algorithm from its `updated` date (Q4: "end of the line after 10 months - same algorithm"); every paper is covered whatever its kind (Q5 = 1, "but all papers"): arXiv by its abstract page, DOI by Crossref, GitHub or any other URL by one request to its page, a local path by file presence and its SHA-256 where one is recorded; ADR-0005 A7 written first; Phase 1.3 of the workflow updated | 240m | **none this sprint**: the first records come due in mid-August 2027. After that, per section, about 65 arXiv papers at 18 s = about 20 min, plus about 16 DOI, GitHub, URL and local records in under 1 min, inside F52's cap | Claude, top tier (ADR); fresh-eyes review at commit |
| E | **F60, the mislabeled QMLPapers file.** First-page arXiv id of every PDF under `QMLPapers\` against its manifest row (13 manifests, 1,470 PDFs); every mismatch listed; the Asfaw paper's real arXiv id found; whether it belongs in the collection goes to Manual Validation (the team lead's call) | 30m | about 3 min (pilot: 20 files in 2.6 s; 19 of 20 carry a first-page stamp, so files without one are listed, not guessed) | Claude |
| F | **F61, the Massoli survey list.** `allPapers.md` (145 KB; the repository's last commit is 2022-02-10, so the list is static) parsed to 184 entries; duplicates found first (arXiv id, DOI, normalized title and first author); new entries through the door at `seen` with `found_via` naming the list and the topic tags; IEEE records by DOI with no account, PDFs never fetched; the survey (2107.03313) gets the list as its companion repository | 120m | about 10 min: about 150 Crossref DOI lookups at about 1 s, plus at most 22 new arXiv entries at 18 s (about 7 min), one capped session | Claude |

**Sequence (Q2 = 1, with F66 first)**: A, B, C, D, E, F. B comes before
the reading and code tasks because it sets the model assignments they use.
A's Phase B waits on the team lead's approval of its Phase A findings, and
the approval message says to ask as late as possible: so A's Phase A runs
first and its report is presented with the Manual Validation hand-over,
then A's Phases B and C follow the answer. Total about 792 minutes of
coordinator time (720 plus C's 72-minute allowance), plus about 17 minutes
of runtime. **If a Criterion 3 stop becomes necessary, the cut line is
before F**: F moves to Sprint 9 with F62, which it feeds. Deferring
approved work is a Class 3 decision and is never made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Phase 2 gates**: PR #68 merged to develop (99bb450) and PR #76 to main
  (d649505); `gh issue list --label sprint --state open` empty; no open PR;
  tree clean; suite 617 passed. Dependency scan not applicable (standard
  library and pytest only).
- **F67**: the models page answers (HTTP 302 to the docs host, then 200)
  and lists `claude-haiku-5-5`: "From $0.10 / input MTok, From $0.50 /
  output MTok", 1M context, 128K output, retirement not sooner than
  2027-10-07. "From" means tiered pricing; Task B reads the pricing page
  for the figure to record.
- **F65**: the guide is at
  `D:\Data\Harold\EvidenceBasedDB\References\QCi-site\systems\Dirac_3S_Users_Guide_Rev_A-1.pdf`,
  38 pages, SHA-256 prefix `0ddbc5339966a42a` (matches the card); 13.7 MB
  with 37 embedded images, but the text layer extracts: 7,322 words,
  sampled pages 5, 12, 20 and 30 at 110 to 238 words each. So the
  verbatim-quote test works as in F45. Page 12 already states "Dirac-3S is
  not an exact solver and does not guarantee discovery of the global
  optimum."
- **F65, the store's shape**: `assertion_relations` allows only `supports`
  and `contradicts` (schema CHECK); the only QCi platform context is
  `platform:dirac-3`, with 19 assertions. "Changed" and "superseded" have no
  relation type and the Dirac-3S has no context: Q3.
- **F65, the precedent**: the Dirac-3 User Guide v0.0.4 is the record
  `ctfassets-2026-dirac-3-user-guide-v0`, access "local path | vendor URL".
  The Dirac-3S guide has no public URL known yet; the task looks for one on
  QCi's site and records only the local path if none exists.
- **F63**: the local copy is
  `QMLPapers\2024\Nguyen-et-al._2024_Entropy-Computing-A-Paradigm-for-Optimization-in-Open-Photonic-Systems__2407.04512.pdf`.
- **F64, the store**: 1,947 papers; 1,848 have probe rows, all dated
  2026-10-03 to 2026-10-08; 1,552 have arXiv access (about 65 per section).
  99 have no probe row: 59 https (GitHub and sites), 35 local paths, 4 DOI,
  1 arXiv (Q4).
- **F64, the code**: `store/probes.py` parses no arXiv version number today
  (it reads status, version-of DOI and access); version detection is new
  parsing, tested on saved fixtures. `probe_reference_fields.py` has
  `cycle_start` and `stale_probes`, which `--due` replaces as the Phase 1.3
  check.
- **F60**: 13 manifests (1,440 rows) and 1,470 PDFs; the Asfaw row names
  `2108.0131`, one digit short.
- **F61**: `allPapers.md` answers through the GitHub API with the `gh`
  token (145,143 bytes); Crossref has no stated per-request delay in
  `store/citations.py` beyond retries, so the lookups run serially.
- **Plan-to-branch verification** (3.2.2.1): no Task A to F artifact exists (at drafting)
  yet; F60, F61, F63, F64, F65 and F67 are open cards.

## Decisions for the team lead at approval (numbered; answer with digits)

**DECIDED 2026-10-12** (team lead: "q1. 1 (double-check as this may have
already been done q2 as recommended other than F66 first q3 1 - they should
be separate - ok to list common assertions, facts... that you can confirm.
q4 - end of the line after 10 months - same algorithm q5. 1, but all papers
q6. 1", and "Sprint plan approved as amended"):

- **Q1 = 1**: F66 added as Task A. Double-checked at approval: the default
  branch is still `main` (`gh repo view`, 2026-10-12).
- **Q2 = 1, F66 first**: A (F66), B (F67), C (F65 with F63), D (F64), E
  (F60), F (F61).
- **Q3 = 1**: `platform:dirac-3s` as its own context; the claims the guide
  confirms for both systems listed and linked.
- **Q4**: no special case. A record with no probe row takes its `updated`
  date as its last check, and the same rule gives its section's first start
  at least 10 months later. Cost: none now.
- **Q5 = 1, all papers**: every kind is re-checked, local paths included
  (file present, SHA-256 unchanged where recorded). Per section about 65
  arXiv papers (about 20 minutes) plus about 16 others (under 1 minute).
- **Q6 = 1**: the Developers role moves to Haiku 5.5.

The questions as asked:

Q3 is Class 1 (it adds a context, part of ADR-0004's spine), and Q4 and Q5
shape ADR-0005 A7; the auto-advance window forbids asking later, so their
substance is decided here and the amendment text is reviewed at Manual
Validation.

- **Q1. F66 (develop as the default branch) in Sprint 8?** It was carded
  today with a Sprint 8 target but is not in the selection list.
  (1) Add it, run first: about 60 minutes; release PRs into main get
  tested; `gh pr create` targets develop; "Closes #N" then closes issues
  on feature-to-develop merges; you approve Phase A's findings before any
  change, and you merge its PR. (2) Leave it for Sprint 9. Recommend 1.
- **Q2. Task order.** (1) A (F67), B (F65 with F63), C (F64), D (F60),
  E (F61): the model check sets the assignments the others use. (2) Your
  listed order: F65, F63, F64, F60, F61, then F67. Recommend 1.
- **Q3. How the Dirac-3S findings are recorded (F65, Class 1).**
  (1) A new context `platform:dirac-3s` (ADR-0004 dated amendment, the
  context added as data, about 20 minutes): Dirac-3S claims are their own
  assertions under it; where the guide agrees with a Dirac-3 assertion,
  a `supports` link; where it differs, the Dirac-3S assertion states the
  difference and names the Dirac-3 assertion, and a `contradicts` link
  only if both cannot hold for the same system; the Dirac-3 assertions stay
  untouched and stay true for the Dirac-3. The hsbc work can ask either
  system's context. (2) New relation types `confirms` and `supersedes`: a
  schema migration and an ADR-0004 amendment, about 90 minutes more plus a
  review cycle. (3) Dirac-3S assertions under `platform:dirac-3` with a
  note: no extra time, but one context then holds two systems, and a query
  for the Dirac-3 returns Dirac-3S claims. Recommend 1.
- **Q4. When the 99 never-checked papers come due (F64).** (1) At once:
  the first Phase 1.3 after F64 ships (Sprint 9) checks the 64 with a
  network address (59 https, 4 DOI, 1 arXiv) in under 5 minutes, once; the
  35 local-path records are left to F48 (a moved or changed file is F48's
  check, not a re-check). (2) Spread with the rest: their first check about
  10 months from today, in their own section; no cost now, but 64 records
  stay unchecked until mid-2027. Recommend 1.
- **Q5. Which kinds the re-check covers (F64).** (1) arXiv, DOI and GitHub
  alike: per section about 65 arXiv papers (about 20 minutes) plus about 12
  DOI and GitHub records (under 1 minute), every two weeks from August
  2027; DOI records also report a retraction or a new version of record.
  (2) arXiv only: about 20 minutes per section; DOI and GitHub records are
  never re-checked. Recommend 1.
- **Q6. The Developers role (F67).** (1) Move it to Haiku 5.5: from $0.10
  input and $0.50 output per million tokens against Sonnet 5.5's $2 and
  $10, 20 times lower; task patterns whose learning_log favors Sonnet
  (reading and evidence gathering, Sprint 4 Tasks F and H) stay on Sonnet;
  no Haiku 5.5 outcome is measured yet, so the first one is recorded. (2)
  List Haiku 5.5 as the haiku tier but keep the Developers role on Sonnet
  5.5 until a measured outcome. Recommend 1.

**Not numbered**: F65's card names a list of further items from the team
lead (2026-10-10). It has not arrived in three messages (each held a paste
placeholder or a quoted request for it). Task C plans against the card's
scope; items received before Task C starts are added to it, and items
received later are carded.

## Premise falsifier

**The premises**: (a) the Dirac-3S guide states its claims in extractable
text, so quotes can be verified by test; (b) a record id hashes evenly
across 24 sections; (c) the arXiv abstract page shows a paper's latest
version number; (d) a QMLPapers file's first page carries the arXiv id of
the paper it holds; (e) most Massoli entries resolve to a DOI.

**What would disprove each**: (a) a quoted sentence is absent from the
page's text: the claim is dropped or read from the page image and marked
so, never reworded; (b) the 1,552 arXiv ids fall more than 50% above the
mean in any section; (c) a saved abstract page has no `vN` marker; (d) a
file's stamp names a different id than its row: that is F60's finding, and
a file with no stamp is listed, not inferred; (e) Crossref returns no DOI
for a BibTeX record without one: the entry is listed as unresolved.

**The checks cannot merely confirm**: the quote test matches text extracted
fresh from the PDF; the section test runs over the real ids and over
synthetic ids, and is proven to fail by injecting a constant hash; the
version parser test includes a page with no version marker; F60's check
compares two independent sources (the manifest and the file).

## Risks

| Risk | Mitigation |
|---|---|
| A Dirac-3S claim is read as replacing a Dirac-3 one | Q3: separate contexts; Dirac-3 assertions are never edited |
| F63's admissions are given an upgrade the provenance does not support (Class 2) | Both enter at the certainty their provenance supports; the admission-against-interest upgrade, with why each costs QCi something, is presented at Manual Validation, not applied in the window |
| The re-check bunches in one sprint after a future bulk load | Sections come from the id, never the load date; a test over synthetic ids |
| Version parsing breaks when arXiv changes its page | Tested on saved fixtures; an unparsed page is reported, never treated as "no new version" |
| F61's arXiv entries break the cap | All arXiv traffic serial, through F52's capped fetcher |
| Session continuity | `sprint_status.json` note at every task start, with the clock time (Sprint 7 I7) |

## Definition of Done

- A: Phase C's checks pass (default develop; `gh pr create` targets
  develop; CI on both branches); the release step written; the trigger test
  proven by injection
- B: each tier re-verified with the date; the haiku tier names Haiku 5.5;
  the Developers role on Haiku 5.5; the test green on evidence
- C: the guide entered with local path and SHA-256 and read in full (read
  row); every `platform:dirac-3` assertion classed (confirmed, changed,
  superseded, not addressed) and recorded under its own context; every quote verified
  verbatim by test; F63's two assertions entered with page anchors and their
  relations; the team lead's items answered or carded
- D: ADR-0005 A7 written; section and next date computed and shown by
  `view.py`; `--due` selects only due records; a revised version on a
  fixture is reported for re-pull; the section spread proven by test and by
  injection; Phase 1.3 updated; the fresh-eyes review's findings fixed
- E: every manifest row matched to its file or listed; the Asfaw paper's
  id found; its belonging decided at Manual Validation
- F: every entry classed as in the store (with its match), entered, or
  refused with the door's reason
- Full suite green before every commit, gated on pytest's own exit code

## Out of scope

F39 itself (released as F67), F46, F48, F50, F55, F56,
F57, F62 (Sprint 9, fed by E), F51 (HOLD). F49 closed at scope selection.
Downloading any PDF. Any write to `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.
