# Sprint 5 Plan: Make the Store Durable, Then Fill It

**Dates**: from 2026-09-23. **No deadline.**
**Branch**: `feature/20260923_Sprint_5` (cut at the Phase 6.6 carry-forward
from Sprint 4's branch, 2026-09-23)
**Scope** (DEFINED, team lead 2026-09-23), in the team lead's own order:
**F31** (new: download the HSBC Phase 2 bibliography's references, process
them into the store, then propose the fields the bibliography shows the
store is missing), **F30** (store durability), **F28** (learn from the
papers), **F5** (QCi deep-dive; "After finding, add them to the db using
the existing process"). **Closed without implementation** at the same
selection: F19 and F29, with the team lead's reasons recorded verbatim in
`docs/ALL_SPRINTS_MASTER_PLAN.md` ("Current sprint").

## Objective

Sprints 1 to 4 built a store of 48 papers and a door that every new source
must pass. Sprint 5 is the first sprint that grows the store in bulk:
about 120 bibliography references and QCi's authors, site and package.
Before the first bulk write, the store becomes durable (F30): today a lost
`store/evidence.db` has no scripted recovery. Then the two sources go
through the one door at the `seen` tier. Around that: the first design
for turning many assertions into "what we now believe, at what certainty,
and why" (F28), and a proposal, from the bibliography's own shape, for
the fields every reference should carry (F31 part 3).

## Tasks

Est is Claude-side implementation time. Runtime is the wall clock of the
run itself, with the dominant term named (SPRINT_PLANNING.md, Sprint 8/9
improvements).

| # | Task | Est | Runtime (dominant term) | Owner |
|---|---|---|---|---|
| A | **F30 -- store durability, in the card's dependency order.** (1) `scripts/rebuild_store_from_export.py`: read the committed `export/*.json` into a fresh store through the real ingestion path, regenerate, assert byte-identical to what it read. (2) Backup on write: a shared helper every write-shaped script calls inside `--apply` before its transaction, using `sqlite3.Connection.backup()`; each backup verified at creation (open, `PRAGMA integrity_check`, record counts) and the run FAILS if it does not check out; retention per the team lead's 2026-09-23 decision (32 days; newest backup of each of the last 5 sprints kept; never delete a backup whose content is not yet in a committed `export/`); `backups/` gitignored. (3) `scripts/restore_store.py` with a test that restores into a temp store and proves the regenerated export matches. Every guard proven to fail by injection | 120m `[no-history]`, timebox 180m | under 1 s per backup (measured 15 ms on the 252 KB store, 2026-09-23) | Claude, top tier (durability design); Sonnet subagent for the retention tests |
| B | **F31 part 1 -- download.** First, preserve `BIBLIOGRAPHY.md` beside the downloads (its scratch workspace is not durable). Generate a download list from the file, de-duplicated against the store AND the disk (11 of 75 arXiv ids are already on disk; none is fetched twice). Fetch arXiv PDFs strictly one at a time, never concurrent with any other arXiv traffic (see pre-flight); save open-access DOI/journal copies; save each web reference as a local copy (`INTAKE_WORKFLOW.md` section 4); copy `[CH-1]`-`[CH-3]` from the consumer repository's `docs/` (read-only there); GitHub repositories are api-origin and are not cloned. Every item that cannot be fetched (paywall, HTTP 403, rotated CDN link) goes on a `needs-manual-download.txt`, never silently dropped. Placement per Q1 | 60m `[no-history]`, timebox 90m | about 5 min: 64 arXiv PDFs x (3 s spacing + about 0.7 s transfer, measured) = about 4 min dominant; about 35 web pages at 1 s = about 1 min. Plus any arXiv back-off: unbounded while a 429 is active, so the script resumes from its own list | Claude, top tier; Haiku subagent for web-page saving |
| C | **F31 part 2 -- process into the store.** Generate an intake manifest for `scripts/intake.py`: `access` from the arXiv id, DOI, GitHub URL, or `<local copy> \| <url>`; primary `context` per section from the `INTAKE_WORKFLOW.md` section 8 tests, written down per section BEFORE the manifest is generated; one-line disposition "Bulk intake 2026-09 from the HSBC Phase 2 bibliography, [TAG]; not yet screened". Dry run read in full, then `--apply` (after Task A, so a backup precedes it), `--verify` on a sample of each source type, export regenerated. The 9 on-disk-but-not-in-store papers per Q2 | 90m `[no-history]`, timebox 120m | about 4 min at 3 s per id, about 16 min at the 13 s per id measured under refusal: 73 arXiv metadata requests dominant; about 12 Crossref/DataCite and about 10 GitHub requests under 1 min | Claude, top tier (context judgment) |
| D | **F31 part 3 -- propose the missing fields.** After C, compare what `BIBLIOGRAPHY.md` records per entry against what a paper record holds, and card the gap as a NEW backlog item (F36; F32-F35 were taken by the team lead's Sprint 6 bulk-intake cards on 2026-09-23) with its fields, decided together with F34 (publication status, the same family of fact), the ADR it amends, and a re-processing path that fills the new fields on all existing papers through the door (dry run by default). No schema change this sprint (a new field is Class 1, ADR-first) | 45m `[no-history]`, timebox 60m | none | Claude, top tier (schema proposal) |
| E | **F5 sub-part 1 -- identify QCi-affiliated people.** From the PDFs, not from memory: `emami-2025`, `loke-2026`, `qci-2024-profiling`, and the QCi papers Task C adds (`[QC-1]`, `[QC-3]`, `[QC-4]`, `[QC-8]`). Full names verified against the paper's own author and affiliation lines; for the SMU/Loke paper, who (if anyone) is QCi-affiliated is established, not assumed. Output: a list of people with the page each was verified on | 45m `[no-history]`, timebox 60m | none (local PDFs) | Sonnet subagent evidence gathering, top-tier judgment |
| F | **F5 sub-part 2 -- every paper each person co-authored, any topic.** Pilot first: one arXiv author query per person, paced, recording hit counts. Then disambiguate every hit against the person's affiliation and co-author network before downloading (a name alone is not a key); search order arXiv, then Crossref/DOI, then Google Scholar (team lead, 2026-09-16). A person whose hits cannot be split by affiliation or co-author is reported as unresolved with the counts, not downloaded. Downloads to the F5 folder layout per Q6, one at a time | 120m `[no-history]`, timebox 180m | `[unbounded]` until the pilot: pilot about 10 people x 3 s = under 1 min; download then N papers x 3.7 s. Heartbeat file if N exceeds about 480 (30 min) | Claude, top tier (disambiguation) |
| G | **F5 sub-parts 3 and 4 -- QCi's site and `eqc_models`.** Scrape `quantumcomputinginc.com` per Q3 (robots.txt allows all; sitemap has 2,755 URLs, most of them the same package docs repeated per version and mounted under three paths). Pull `eqc-models` 0.21.0 (latest of 29 releases) from PyPI: sdist and wheel, source and bundled docs. Save the Dirac-3 User Guide v0.0.4 (`[QC-2]`, also in F31) once, not twice | 60m `[no-history]`, timebox 90m | about 5 min: about 300 pages x 1 s politeness interval dominant (Q3 option 1); about 45 min under option 2 | Haiku subagent for the scrape, Claude review |
| H | **F5 ingest.** Author papers from F as `seen` api-origin records; site material and the package as `Reference:` records per Q4; same manifest path, dry run, `--apply`, `--verify` sample, export regenerated | 60m `[no-history]`, timebox 90m | N arXiv ids x 3 s (N from F's pilot) dominant; site records are hand-origin with no API call | Claude, top tier |
| I | **F28 -- learn from the papers: design, then pilot per Q5.** A design document answering the card's open questions (what a "key learning" is as a record; how it carries its evidence; synthesis as a computed query, never a stored copy; which tier extracts and which adjudicates; how new papers are triaged for extraction). If Q5 = 2: one pilot cluster taken to `read` with GRADE-style assertions and relations, and the synthesis shown as a query over them, using ONLY existing primitives. If the pilot cannot express a learning without a new field or class, that is the finding, and it becomes a proposed ADR amendment for Manual Validation, not an implementation | 180m `[no-history]` (design 90m, pilot 90m), timebox 240m | none beyond Task C's records | Claude, top tier (design; ADR-class) |

**Sequence**: A first: F30's own card names the bulk load as its trigger,
so no bulk `--apply` runs before backup-on-write exists. Then B -> C -> D
(F31 in order). E is read-only on local PDFs and may run beside B. Then
F -> G -> H (F5 in order). I last, so its pilot can draw on the new
records. **All arXiv traffic is serial across the whole sprint**: B, C, F
and H never overlap each other, a subagent, or a probe.

**Total ~780 minutes of Claude-side work** (about 13 hours) plus about 20
minutes of measured runtime, plus Task F's runtime, which is unbounded
until its pilot. Calibration from Sprint 4's Actuals: coordinator time ran
far under estimate wherever a subagent carried the reading (Tasks F and H
at 3 and 8 minutes against 90 and 120), and 1.7x OVER where an external
API refused requests (Task C, the arXiv 406). This sprint is API-bound in
four tasks, so the 1.7x case is the one to plan for. **No 30% findings
allowance**: the sprint is intake, not verification; the exceptions an
intake produces (refusals, paywalls, title mismatches) are inside B's and
C's estimates. **If a Criterion 3 stop becomes necessary, the cut line is
before Task I** (F28 is the lowest-priority item and design-only in its
first half). Deferring approved work is a Class 3 decision and is never
made unilaterally.

## Pre-flights performed at planning (SPRINT_PLANNING.md, capability pre-flight)

- **Data precondition, bibliography vs store vs disk** (2026-09-23):
  120 tagged entries in 15 sections; 75 distinct arXiv ids. In the store:
  2 (`[FW-1]` Fourier Wall, `[QC-5]` QCi fraud paper). On disk but not in
  the store: 9, all under `QMLPapers/<year>/`. To download: 64 arXiv
  PDFs, plus the non-arXiv entries (about 6 with a DOI in the text, about
  10 journal or proceedings pages, about 10 GitHub repositories, about 25
  web, vendor, news and challenge pages). The on-disk copy of
  `2509.06873` is filed under an older title ("Behind the scenes of the
  Quantum Extreme Learning Machines") than the one arXiv now returns and
  `[EN-1]` cites: a file name is not the source of record either.
- **arXiv metadata, the exact request shape Task C sends**
  (`store.citations.fetch_arxiv_batch`, one id per request, 3 s apart):
  **75 of 75 resolved**, in 984.8 s: about 13.1 s per id against 3 s
  planned. That is the full refusal path (3 s pace, then 3 s and 6 s
  retries, then the DataCite fallback) on nearly every id, consistent
  with the HTTP 429 below having begun early in the run. The script did
  not record which provider answered each id, so "mostly DataCite" is an
  inference from the timing, not a measurement. Consequence for Tasks C
  and H: plan the metadata runtime at 13 s per id while refusals last
  (73 ids: about 16 min, not 4), and record the provider per record.
  **Titles, compared by eye against the bibliography**: two entries cite
  a title that does not belong to their id. `[IN-2]` gives "The Physical
  and Contextual Limits of Quantum Speedup" for `2605.12675`, which arXiv
  titles "Answer Partitions and Oracle Access Determine Quantum Query
  Complexity"; `[CL-21]` gives RelBench for `2312.04615`, which is
  "Relational Deep Learning: Graph Representation Learning on Relational
  Databases". Either the id or the title is wrong in each. The door
  derives titles from the id, so neither becomes a wrong record, but the
  bibliography's reading notes for those two may describe a different
  paper; Task C records both in the exceptions list for the team lead
  rather than guessing which half is right. The remaining differences are
  subtitle truncations and small wording changes.
- **arXiv PDF download** (`arxiv.org/pdf/<id>`, plain User-Agent): 200,
  4.18 MB in 0.72 s. **Finding**: this probe ran while the metadata batch
  above was active against `export.arxiv.org`, and a probe to the API
  afterwards returned **HTTP 429**. The two hosts appear to share one
  per-client limit, and arXiv's terms ask for a single connection at a
  time. Hence the sequence rule above: all arXiv traffic in this sprint is
  serial, across tasks, subagents and probes. The follow-up probes were
  stopped rather than retried, so the retries did not extend the refusal
  being measured (Sprint 4 improvement 3).
- **QCi site**: 200; `robots.txt` is `Allow: /` with a sitemap. The
  sitemap lists 2,755 URLs: `learn/support` 966, `learn/developer-resources`
  963, `learn/module` 388, press releases 211, blogs 62, SEC filings 36,
  products/systems 21, lessons 21, applications 19, research and
  publications 15, technology 7. Most of the documentation is the same
  package docs (five packages) repeated per version and mounted under
  three paths; latest-version-only, it is 742 pages before de-duplication
  across the mounts. This is what Q3 decides.
- **PyPI**: `pypi.org/pypi/eqc-models/json` 200; latest 0.21.0, 29
  releases. **Dirac-3 User Guide** (`[QC-2]`, CDN link): 200, 4.69 MB.
- **F5 author search**: NOT probed at planning. The arXiv 429 above was
  active, and a probe during it would have measured the refusal rather
  than the search. Task F is `[unbounded]` with its pilot as its first
  step, per SPRINT_PLANNING.md.
- **Plan-to-branch verification** (3.2.2.1): none of the planned
  artifacts exists (`rebuild_store_from_export.py`, `restore_store.py`, a
  backup helper, `backups/`, a Sprint 5 manifest, a synthesis design
  document). `scripts/intake.py`, `store/citations.py` and
  `docs/INTAKE_WORKFLOW.md` exist and are the path Tasks C and H use
  unchanged. Store at 48 papers (28 `seen`, 14 `screened`, 6 `read`) and
  13 assertions. Suite 458 passed on this branch.
- **Phase 2 gates**: PR #30 merged to develop and PR #42 to main; no open
  `sprint` issues; no open PRs; working tree clean; tests green. The
  dependency scan (2.6) is not applicable: the repository imports only
  the standard library and pytest, and declares no dependencies.

## Decisions for the team lead at approval (numbered; answer with digits)

**DECIDED 2026-09-24 (team lead: "Sprint plan approved as amended (with
any comments I provided), proceed with execution")**: Q1 = 2 (merge into
the existing folders), Q2 = 1, Q3 = 1, Q4 = 1, Q5 = 2, Q6 = author papers
under `D:\Data\Harold\EvidenceBasedDB\QCiAuthorsPapers\<person>\`
(the team lead's own path). Q6 named one folder; the site scrape and the
package keep the proposed `References\QCi-site\` and
`References\eqc_models\` (Claude's assumption, stated at approval).
**Q1 = 2 in practice**: QML and quantum sections (FW, DQ, EX, EN, IN, DS,
QC, IC, QF, TN, and `[GP-4]`) go to `QMLPapers\<year>\` under that
folder's filename convention; classical ML sections (CL, CE) go to
`Papers\`; web, vendor, news and challenge pages go to `References\`.
The existing `manifest.tsv` files are NOT edited: they are the record of
the collection's own download run, and F32 reads them; files added here
are already in the store by the time F32 runs, and its derived ids skip
them. `BIBLIOGRAPHY.md` is preserved under `References\`.
Team lead's two questions at approval, answered: Task A uses SQLite's own
backup API (`sqlite3.Connection.backup()`), not a file copy; Task B's 64
downloads are what remains AFTER removing the 11 already on disk.

These shape Tasks B, C, F, G, H and I, so they are answered with the plan
rather than mid-sprint (the auto-advance window forbids asking later).

- **Q1. Where the bibliography downloads land.** (1) A new collection
  folder `D:\Data\Harold\EvidenceBasedDB\Phase2Bibliography\` holding
  the papers with a `manifest.tsv` in the `QMLPapers` column layout plus
  a `bib_tag` column, `BIBLIOGRAPHY.md` itself, and web references under
  `References\Phase2Bibliography\`; (2) merge into the existing folders:
  QML arXiv papers into `QMLPapers\<year>\`, other papers into `Papers\`,
  web pages into `References\`. Recommend 1: the bibliography stays one
  traceable collection, and its classical-ML half (sections 11 and 12)
  does not land in a folder whose name `INTAKE_WORKFLOW.md` section 9 uses
  as the reason for a `qml` default.
- **Q2. The 9 bibliography papers already on disk under `QMLPapers\` but
  not in the store.** (1) Ingest them in Task C, pointed at where they
  are, not downloaded again; (2) leave them for a future bulk load of
  `QMLPapers\`. Recommend 1: they are bibliography entries, and because
  ids are derived, a later bulk load skips them as already present.
- **Q3. How much of QCi's site to scrape.** (1) Latest version only of
  each package's documentation, de-duplicated across the three mount
  points, plus lessons (21), applications (19), research and
  publications (15), products/systems (21) and technology (7): about 300
  pages; (2) every sitemap page, every version, press releases and SEC
  filings included: 2,755 pages. Recommend 1: older versions and the
  duplicate mounts repeat the same content, and press releases and SEC
  filings are outside the card's "key docs, training, QML methods".
- **Q4. Which QCi site material becomes store records.** (1) One
  `Reference:` record per lesson, application note, research publication,
  the Dirac-3 User Guide, and one per software package, with the package
  documentation staged beside it, not recorded page by page: about 60
  records; (2) one record per scraped page: about 300. Recommend 1: an API
  reference page is not a claim-bearing source, and 240 of them at `seen`
  would bury the 60 that are.
- **Q5. How far F28 goes this sprint.** (1) Design document and a
  proposed ADR text only; no record changes; (2) design plus a pilot:
  one cluster of about 6 papers taken to `read`, with extracted
  assertions, relations, and the synthesis shown as a computed query,
  using only the store's existing primitives. Recommend 2: whether the
  existing primitives suffice is the design's central question, and only
  a pilot answers it with evidence rather than argument.
- **Q6. F5 folder names** (the card's proposal, "team lead's call at
  carding"): `References\QCi-authors\<person>\`, `References\QCi-site\`,
  `References\eqc_models\`. (1) Yes, use these; (2) No, I will name them.

## Premise falsifier

**The premises**: (a) the committed export is a complete artifact from
which the store can be rebuilt (ADR-0004 section 2); (b) the one door
takes a bibliography written for another purpose without a code change;
(c) a person's name plus affiliation and co-author network is enough to
find their papers without collisions; (d) the store's existing primitives
can express a "key learning" with its evidence.

**What would disprove each**: (a) Task A's rebuild regenerates an export
that is NOT byte-identical to the committed one: then the store holds
something the export does not carry, which is both a durability hole and
an ADR-0004 finding; (b) Task C's dry run refuses more than 10% of
entries for a reason that is not a real defect in the entry, or any entry
needs a change to `intake.py` or `validate_paper()`: then the door was
shaped to the seed set and `QMLPapers`, and C grows; (c) Task F's pilot
finds a person whose hits cannot be split: that person is reported with
counts and not downloaded; (d) Task I's pilot cannot state a learning
without a new field or class: that becomes a proposed ADR amendment.

**The checks cannot merely confirm**: the rebuild compares bytes against
the committed export from a fresh temporary store, and its guard is
proven by injecting a store column the export does not carry and watching
it go red; the dry run is read in full before `--apply`, with every
refusal classified; the disambiguation rule is written down before the
first hit is read.

## Risks

| Risk | Mitigation |
|---|---|
| arXiv refuses the client mid-run (seen at planning: HTTP 429) | All arXiv traffic serial across the sprint; each script resumes from its own list; `fetch_arxiv_batch` already falls back to DataCite per id; the Sprint 4 406 lesson is in the pre-flight rule |
| Volume without judgment (ADR-0005 section 2c): about 180+ new `seen` records | Every record says in its disposition where it came from and that it is not screened; screening is a later, per-cluster step; Q4 keeps API reference pages out of the store |
| Copyrighted material reaches git | Downloads land only under `D:\Data\Harold\EvidenceBasedDB\`; `.gitignore` already blocks `*.pdf`; `git status --short` read before every staging |
| Author-name collisions pull in the wrong person's papers | Disambiguation rule written first; unresolved people reported, not downloaded |
| A bulk `--apply` corrupts or loses the store | Task A lands first; every `--apply` is preceded by a verified backup; the rebuild script is the last line |
| The consumer repository is written by mistake while copying `[CH-1]`-`[CH-3]` | Read-only copy out of it; `block_sibling_repo_writes.py` enforces |
| Team-lead adjudication cost per record (ADR-0004's constraint) | Nothing in this sprint asks the team lead to adjudicate a record; new records stop at `seen`; Task I's pilot promotes about 6 |
| Session continuity across a long, API-bound sprint | `sprint_status.json` `note` written at every task boundary (Sprint 4 improvement 4) |

## Definition of Done

- Task A: `rebuild_store_from_export.py` rebuilds a fresh store whose
  regenerated export is byte-identical to the committed one; every
  write-shaped script's `--apply` takes a verified backup first and fails
  if verification fails; retention implements all three rules and deletes
  nothing any rule protects; `restore_store.py` has a test that restores
  and proves the export matches; each guard proven to fail by injection
- Task B: `BIBLIOGRAPHY.md` preserved; every entry is on disk, pointed at
  an existing copy, api-origin with no file needed, or listed in
  `needs-manual-download.txt` with its reason; no file downloaded twice
- Task C: every Task B entry is in the store at `seen` or listed with the
  door's refusal reason; context rules per section written down before
  the manifest; `--verify` passes on a sample of each source type; export
  currency green
- Task D: F36 carded in the master plan with its fields, the ADR section
  it amends, and a dry-run-by-default re-processing path for existing
  papers
- Task E: a list of QCi-affiliated people, each with full name and the
  PDF page it was verified on
- Task F: per-person hit counts from the pilot; every downloaded paper
  disambiguated by a stated rule; unresolved people reported with counts
- Task G: the site scrape per Q3 and `eqc-models` 0.21.0 on disk under
  the Q6 layout
- Task H: F-G material in the store per Q4 through the same door;
  `--verify` sample passes; export currency green
- Task I: the design document answers each open question in the F28
  card; per Q5, the pilot's learnings are a computed query over existing
  primitives, or the gap is a proposed ADR amendment presented at Manual
  Validation
- Full suite green before every commit (gated on pytest's exit code, never
  a pipe); every new guard proven to fail by injection

## Out of scope

Bulk intake of `QMLPapers\` (1,618 files): not selected, and carded for
Sprint 6 as F32 to F35 (team lead, 2026-09-23); Task C touches
only the 9 files the bibliography names (per Q2). Screening (`screened`
tier) of any new record. Any schema change, including the fields Task D
proposes (carded as F36 for a later sprint) and any ADR change Task I
proposes (presented, not applied). The other scratch-workspace documents
beside `BIBLIOGRAPHY.md` (`PROPOSED-PHASE2-PLAN.md` and six research
notes). F19 and F29 (closed). Any write to `hsbc-quantum-fraud-2026` or
`spamfilter-multi`.
