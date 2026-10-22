# Intake Workflow: how a source enters the store

Design document, Sprint 4 Task G (backlog item F25 part C4/C5, absorbing
F12). Status: **in force** for papers, repositories and references;
**designed, not yet exercised** for books (Sprint 4 decision Q5). Governs
`scripts/intake.py`. Amend by dated section at the bottom, not by silent
edit, once a design choice here has shipped records.

## 1. The one rule

**Every source type converges on the same store-update step:**
`store.ingest.insert_paper()`, whose `validate_paper()` is the door Sprint 4
Task B built. Whatever the source (a PDF found on LinkedIn, an arXiv id, a
GitHub repository, a book), the record is derived where it can be derived
and checked the same way before it is written. There is no second path.
The Sprint 1 seed generator was the second path and was retired in Task C
for exactly that reason.

The door's rules, restated for intake (the tests are in
`tests/test_ingest.py`, `tests/test_intake.py`):

- `citation_origin` is `api` when `access` carries an arXiv id, a DOI or a
  GitHub repository URL. The citation and the title are derived from the
  source of record (`store/citations.py`: arXiv, Crossref, DataCite,
  GitHub) and rendered in one house style. A hand-typed citation for an id
  that would resolve is refused.
- `citation_origin` is `hand` only when nothing resolves. Then the citation
  ends with the visible marker `(hand-transcribed from <page>)`, `access`
  is the real local path outside version control (optionally followed by
  ` | <url>` for an id-less web page), and `transcribed_from` names the page.
- `value` is the title. `disposition` is one line and names no tier. Every
  `applicability` rationale ends with a source anchor (` -- arXiv abstract`,
  ` -- p.1 keywords`, ` -- GitHub repository description`). No audit-trail
  text inside a citation; corrections go to `updated_reason`.
- Tier obligations (ADR-0005 A2): `seen` needs a disposition; `screened`
  needs applicability derived from the source; `read` needs
  `checked_against_source` (schema CHECK) and extracted `yields`.

## 2. The command

`scripts/intake.py`, dry-run by default, `--apply` to write. One record
from the command line, or many from a JSON manifest. `--verify <id>` runs
the first-try check (section 6) on a record already in the store.

| Source | `access` | Origin | Id | Notes |
|---|---|---|---|---|
| arXiv paper | `arXiv:2602.11092` or the abs URL | api (arXiv API; DataCite `10.48550/arXiv.<id>` as per-id fallback) | derived: `<family>-<year>-<five title words>` | one request per id, 3 s apart; a 1,200-paper pass is about an hour |
| DOI paper, report, book with a DOI | `DOI:10.7249/RRA1367-6` | api (Crossref, then DataCite) | derived | a DOI that is not registered at doi.org is refused with that message; record it hand-origin with the printed DOI in `evidence` (`udaru-2025`) |
| GitHub repository | `https://github.com/owner/name` | api (GitHub REST) | derived: `<owner>-<name>-github-repo` | citation built from identity fields only (owner/name, description, license, created, URL), never HEAD, so the refresh diff is quiet across pushes |
| Reference (article, post, vendor doc, training material) | `<local copy> \| <url>` | hand | `--id` required | the local copy preserves content the source may not keep live (section 4) |
| Book without a DOI | `<local file>` | hand today; ISBN path designed (section 5) | `--id` required | |

`--kind paper|book|reference|repo` (repo is inferred from a GitHub URL).
Until `paper_fields.kind` exists (section 7, a schema decision), a
non-paper kind is named at the start of the disposition, `Book:`,
`Reference:`, `Code repository:`, and `intake.py` enforces the prefix.

## 3. What the Papers directory needs per paper: nothing beyond the file

F12's first question. **No sidecar.** The store already holds every
determinate fact about the paper (citation from the API, title, access,
disposition, applicability, tier), and CLAUDE.md's rule is that determinate
facts are computed, never stored twice. A sidecar `.md` beside the PDF would
be a second copy that drifts. The PDF (or the original file) is the only
thing the directory holds; the record's `access` points at it (hand-origin)
or at the id (api-origin, where the local file is a convenience copy the
record does not depend on).

Filename convention for new files, so a directory listing sorts and reads:
`<YYYY-MM>_<source-or-first-author>_<short-title>[_v<N>].<ext>`, which is
what the 2026 files already in `Books/` follow. Existing files keep their
names; `access` carries whatever the name is.

## 4. What a reference needs when it is not a paper

F12's second question, with the `eqc_models` PyPI package, a LinkedIn-hosted
article and a vendor training document as the named cases.

- **Preserve the content locally, because the source may not stay live.**
  A web article is saved as PDF (print to PDF) or as the page's text under
  `D:\Data\Harold\EvidenceBasedDB\References\`; a package page is saved
  the same way. This is the local copy `access` points at.
- **Record the links in `access`**: `<local copy> | <url>`. The URL is the
  citation's resolvable pointer; the local copy is what the record depends
  on. A DOI or arXiv id, when the reference has one, makes it api-origin
  and the local copy optional.
- **Cite it by hand, visibly**: author or organization, title, site or
  publisher, date as printed, then `(hand-transcribed from <page>)`.
- **Say what it is in the disposition's first words**: `Reference: ...`.

The LinkedIn example from F12 went through this path on 2026-09-19 once the
team lead supplied the URL at Manual Validation (`https://lnkd.in/p/es-nvegJ`,
a post by Javier Mancilla Montero reading the MerLin paper): the post body
was saved verbatim under `References/`, the record is
`mancilla-2026-linkedin-merlin-reproduces-18-qml-papers` (hand-origin,
"Reference:" disposition, one anchored applicability row), and `--verify`
passed 7/7. The three F12 examples turned out to be one thread: the post,
the paper it reads (arXiv:2602.11092) and the code it links.

## 5. Books (decision Q5: designed, nothing ingested)

Books resolve by DOI when the publisher issues one (Springer does:
`freericks-2026` was switched to api-origin in Task C on DOI
`10.1007/978-3-031-87845-9`, which Crossref returns with title, subtitle,
author and publisher). For books without a DOI the next resolver is the
ISBN: Open Library's `https://openlibrary.org/isbn/<isbn>.json` returns
title, publish date, publishers and author keys (a second call per author).
That resolver is **not implemented**; the 6 incoming books are recorded
hand-origin from the title page until it is, and the design records it here
so it is built before a bulk book load, not after. The `Books/` directory
holds 44 files as of 2026-09-19 (was 38 at planning); most are programming
texts outside this library's scope and are not intake candidates until a
context claims them.

## 6. Bulk intake (about 1,200 papers and 6 books incoming)

- **A manifest, not a directory scan.** `intake.py --manifest file.json`
  reads a JSON list of entries with the same fields as the command line.
  The manifest is authored (by the team lead, or by F5's discovery run) and
  reviewed before `--apply`; a dry run prints every derived record.
- **Per-entry commit, resume by id.** Unlike the seed loader (all-or-
  nothing, right for a 45-record replay), a bulk run that fails at entry
  700 keeps 699 and reports the failure; the re-run skips ids already
  present. The export regenerates once at the end of a run that wrote
  anything.
- **Pacing.** arXiv is one id per request, 3 seconds apart (measured
  2026-09-19: an `id_list` batch earns a 406 and a several-minute refusal
  for this client; single ids do not). Crossref and GitHub have no such
  limit at this scale. About one hour per 1,200 arXiv ids.
- **`seen` is the bulk tier.** A bulk entry needs `access`, a primary
  `context`, and a one-line disposition that says why it was pulled
  ("Bulk intake 2026-10 from F5's QCi author search; not yet screened" is
  honest). Applicability is derived at `screened` by an agent reading the
  abstract with anchors, one cluster at a time, not at load.
- **Ids are derived**, so two people loading the same paper get the same
  id and the second is skipped as present.

## 7. The first-try proof (F25 C5) and the mechanized check

The acceptance test for "correct on the first try": one real paper through
the finished path, then the F10 protocol against the result with **no
correction pass afterward**. Run 2026-09-19 on `arXiv:2602.11092` (the F12
example): `intake.py --apply` wrote
`notton-2026-merlin-discovery-engine-photonic-hybrid` at `screened` with two
anchored applicability rows; `intake.py --verify` then reported every check
PASS (citation SAME as the source of record, title SAME, disposition one
line with no tier word, every rationale anchored, screened obligations met,
value is the title). Its code repository went through the same door as
`merlinquantum-merlin-github-repo`. The exact output is in the Sprint 4
summary.

`--verify` is the F10 protocol as a program, and it is also what Phase 1.3
(design-document currency) runs across the store each delivery cycle beside
`refresh_citations.py`: an api-origin record whose citation drifts from the
API, a hand-origin record whose file has moved, a rationale that lost its
anchor, all surface then rather than at a reviewer's desk a year later.

## 8. Context tests: which contexts a source bears on (F25 D4)

Written down BEFORE the Sprint 4 Task F re-filing pass ran, as the pass
required, and applied to all 48 paper records by
`scripts/sprint4_task_f_refiling.py`. `applicability` names the contexts a
source bears on; each rationale ends with the anchor naming where it was
read (` -- arXiv abstract`, ` -- PDF p.2 keywords`). The Sprint 3 reviews
(F9, F10) found the same judgment made differently across records with no
stated rule; these are the rules.

- **`world`** -- true independent of any project: mathematics, physics,
  standard expansions. Test: *a theorem, a proof, a physical law, or a
  measurement of nature that would be true if this project did not
  exist.* Passes `zajac` (a proved Equivalence Theorem), `kerger` (proved
  round complexity), `li` (an instrument sensitivity result in
  experimental physics), `freericks` (a physics textbook). Fails `arute`
  (an engineering demonstration of a device, a contested empirical
  claim), `rand` (a policy report), `britt-humble` (an architecture
  paper). "Platform-independent" is not the test; "about the world rather
  than about a system" is.
- **`method`** -- how this library and its consumers build, reason about
  and evaluate claims. Test: *the source is about how to benchmark,
  evaluate, certify, simulate for evaluation, or define the vocabulary of
  a field; or it is practitioner tooling and coding practice for building
  the experiments this library reads.* Passes benchmark suites
  (`lubinski`, `pelofske`, `kordzanganeh`), certificates (`mancilla`),
  simulators built as evaluation tools (`mandra`), controlled-study
  tooling (`sakhnenko`, `tung`), vocabulary-defining surveys (`huynh`),
  architecture metrics (`britt-humble`), and the tooling decks and guides
  (`kawchak`, `ibm`, `interviewbit`). Fails marketing commentary on why
  benchmarking matters (`bcg`).
- **`ml`** -- machine learning generally. Test: *classical ML content
  that does not depend on a quantum substrate is the object of study or a
  named comparator: a named classical algorithm as baseline (XGBoost,
  random forest, kernel methods), a classical model as the thing being
  compressed or trained, or ML as the paper's subject.* Passes `emami`,
  `loke`, `qci-2024-profiling` (XGBoost baselines), `neven` (boosting),
  `mancilla` (gradient-boosted trees), `chen`, `rehman`, `sakhnenko`,
  `tung`, `wang` (CNN compression), the two `kawchak` ResNet50 decks,
  `dwave-2021-recruit` (L1LR, RFFS), `huynh` (QiML runs in classical
  frameworks), `lenat-marcus` (LLMs). Fails a brochure that lists AI as an
  application area (`idq`), an analogy (`qci-2024-unconventional`).
- **`qml` via workload** -- the intersection of ml and qc, not the union.
  Test: *the workload or model is itself a quantum ML model (QNN, quantum
  kernel, variational classifier, quantum boosting), or the ML model is
  the thing a quantum optimizer trains or compresses, or QML is the
  subject.* Passes `wang` (a CNN is the optimized target) and `neven`
  (a classifier is trained on the annealer); fails `dupont` (a spin-glass
  instance is not an ML model). `kordzanganeh` loses `qml`: its abstract
  names no QNN workload; restore at `read` tier if the body shows one.
- **`qc` subsumption** -- a source carries `qc` when its quantum-computing
  content is not already captured by a `platform:*` context it carries.
  `emami`, `loke`, `qci-2024-profiling` are Dirac-3 through and through
  (no `qc`); `qci-2024-unconventional` explains unconventional computing
  in general and also names the Dirac-3 module (both); `neven` runs on
  D-Wave, for which no `platform:*` context exists, so `qc` is where the
  substrate is recorded.
- **`hsbc-2026`** is never claimed by a paper: relevance to the project is
  not membership in its context (F8's observation, kept as policy).

## 9. Observed 2026-09-19 (evening): the bulk set has arrived

Recorded the day this design was written, after section 6 was drafted
from the planning estimate of "about 1,200 papers and 6 books".
`D:\Data\Harold\EvidenceBasedDB\QMLPapers\` now holds 1,618 files: year
folders `2007-2017` through `2026` (about 1,410 PDFs named
`<Authors>_<Year>_<Title>__<arXiv id>.pdf`), each year folder carrying a
`manifest.tsv` with columns `file, arxiv_id, url, title` (about 1,450
rows in all), a `failed-downloads.txt` and a `needs-manual-download.txt`
(24 lines in all); plus `Repos/` (137 `_repo.md` notes, each named for
the paper and arXiv id it belongs to), `Reviews/` (33), `Workforce/`
(28), `NonArxiv/` (7 PDFs without an arXiv id) and `Books/` (2).

What this means for section 6, stated now so the bulk sprint does not
re-derive it:

- The intake manifest is GENERATED from the year `manifest.tsv` files, not
  authored by hand: `arxiv_id` gives api-origin access for about 1,410
  records; `title` is discarded (the door derives it from the API); the
  year folder gives nothing the API does not. Counts are a snapshot as of
  this date.
- The judgment fields still need a human or an agent per record. For the
  bulk `seen` load the honest defaults are `context: qml` (the collection
  is named for it, and the disposition says that is why) and a
  disposition of the form "Bulk intake 2026-MM from QMLPapers/<year>/
  manifest.tsv (a QML literature collection); not yet screened".
  Screening happens later, one cluster at a time, with anchored
  applicability from the abstract.
- `NonArxiv/`, `Reviews/`, `Workforce/` and `Books/` take the paper path
  when a DOI resolves and the hand path (section 4) otherwise; `Repos/`
  notes point at repositories that take the GitHub path (section 2), the
  note itself being local evidence, not the record.
- `failed-downloads.txt` and `needs-manual-download.txt` are the first
  entries of the bulk run's exception list, not intake candidates.
- At one arXiv request per 3 seconds the api-origin part of this set is
  about 70 minutes of wall clock; DataCite carries any id arXiv refuses.

## 10. Decisions this design leaves to the team lead (Class 1)

1. **`paper_fields.kind` column** (`paper | book | reference | repo`) as
   the next ADR-0005 amendment, replacing the disposition-prefix
   convention in section 2. Recommended: yes, at the sprint that first
   loads books in bulk; a prefix is a convention, a column is a fact.
2. **ISBN resolver** (section 5) before the first bulk book load.
   Recommended: yes, in the same sprint.
3. **Provenance as artifact pointer** (ADR-0004 section 3 read strictly):
   whether `provenance` for a source should become the retrieval record
   (API response and date) rather than the citation string. Recorded in
   ADR-0005 A2 as the next candidate amendment; not needed for intake.

## 11. Applied 2026-09-24: the HSBC Phase 2 bibliography (Sprint 5 Task C, F31)

Written BEFORE the manifest was generated, as the plan requires, applying
section 8's tests to each of the bibliography's 15 sections. Every record
gets ONE primary context at `seen`; applicability is not derived at load
(section 6). Where a section mixes kinds, the exception is named.

- **1. Fourier Wall / SPECTRA** -> `qml` (quantum-versus-classical ML on
  tabular data is the subject). `[FW-3]` (the SPECTRA datasets) ->
  `method`: benchmark datasets are how claims are evaluated.
- **2. Dequantization** -> `qml`.
- **3. The exponential-advantage claim** -> `qml`, including the blog,
  the critique, the news item and the code repository about it.
- **4. Entanglement in QML** -> `qml`. `[EN-6]` (many-body localization
  for variational quantum SIMULATION) -> `qc`: no ML workload.
- **5. Interference, magic, resource theory** -> `world`: each is a
  theorem about quantum information that would hold if this project did
  not exist (the `zajac` precedent).
- **6. Dissipation and noise** -> `qml` where the object is a learning
  model (`[DS-1]` reservoir computing, `[DS-2]` barren plateaus in
  variational training, `[DS-3]`, `[DS-4]`); `[DS-5]` (a framework for
  quantum algorithms generally) -> `qc`.
- **7 and 8. QCi primary sources and independent critiques** ->
  `platform:dirac-3` (section 8's subsumption rule: Dirac-3 through and
  through, no `qc`). `[QC-3]` (a proposal for FUTURE all-optical hardware,
  "Not Dirac-3" in the bibliography's own words) -> `qc`.
- **9. QML on fraud** -> `qml`.
- **10. Tensor networks** -> `ml`: quantum-INSPIRED models run classically
  are not a quantum workload (the qml test). `[TN-4]` (tensor networks FOR
  quantum computing) -> `qc`.
- **11. Classical SOTA for fraud** -> `ml`.
- **12. Ceiling estimation / Bayes error** -> `ml`, except the two pure
  information-theory results, `[CE-22]` (a guide to Fano's inequality) and
  `[CE-23]` (Han and Verdu, generalizing Fano) -> `world`.
- **13. Gate-based platforms** -> `platform:braket` for the AWS pages
  (`[GP-1]`-`[GP-3]`), `platform:classiq` for `[GP-5]`-`[GP-7]`, `qc` for
  `[GP-4]` (the Aquila device paper) and `[GP-8]` (cross-vendor pricing).
- **14. Challenge documents** and **15. Related entries in the same
  track** -> `hsbc-2026`. Section 8's "never claimed by a paper" is about
  PAPERS whose relevance to the project is not membership; these are the
  challenge's own documents and its entries, which ARE specific to the
  submission by the context's own definition.

**Disposition**, one line, no tier word: `Bulk intake 2026-09 from the HSBC
Phase 2 bibliography [<TAG>] (<section name>); not yet screened`, prefixed
`Reference: ` or `Code repository: ` for those kinds (section 2).

**Not re-entered**: `[FW-1]` and `[QC-5]` (already records), `[QC-9]`
(the Neven QBoost paper, already `neven-2012-qboost-adiabatic-quantum-optimization`).
Counts in this section are a snapshot as of 2026-09-24.

## 12. Applied 2026-09-24: papers found by F5's QCi author search (Sprint 5 Task H)

Written BEFORE the search ran. An author's other papers span every topic,
so the reason a paper was found (a QCi-affiliated author) says nothing
about what it is about, and no single default context is honest. The
primary context is therefore taken from the arXiv subject categories the
registry itself records (DataCite `subjects`, scheme `arXiv`), mapped by
section 8's tests:

- a quantum category (`quant-ph`) AND a machine-learning category
  (`cs.LG`, `stat.ML`, `cs.AI`, `cs.NE`) -> `qml` (the intersection, not
  the union);
- a quantum category alone -> `qc`;
- a machine-learning category alone -> `ml`;
- anything else (optics, condensed matter, mathematics, other computer
  science) -> `world`, the context for results about nature and
  mathematics independent of this project. A later screening pass may
  refine it; `seen` promises nothing more.

A journal-only hit (a Crossref DOI with no arXiv record) carries no arXiv
categories and takes `qc`, the field every one of the 18 people was found
through, with the disposition saying the context was not derived.

**Disposition**: `Bulk intake 2026-09 from F5's QCi author search
(<person>, <rule>); not yet screened`, where `<rule>` is `seed` or
`network` from the disambiguation rule in
`docs/research/2026-09-24_F5_qci_affiliated_people.md`.

## 13. Applied 2026-09-24: QCi's own site and packages (Sprint 5 Task H, F5 sub-parts 3 and 4)

Written BEFORE the manifest was generated. Scope of what becomes a record
is the team lead's Q4 = 1: one `Reference:` record per lesson, application
note and research page, one per software package; the package
documentation pages, training modules, product and technology pages stay
staged under `References/QCi-site/` (the local copy each package record
points at is its documentation landing page, or for `eqc-models` the
released sdist). Contexts by section 8's tests:

- **application notes** (`learn/applications/...`, "... on Dirac-3") ->
  `platform:dirac-3`; the three that run on EmuCore, QCi's reservoir
  computing device (`classification-on-emucore`,
  `image-classification-using-emucore`, `narma10-on-emucore`), -> `qc`.
  (Corrected 2026-09-24, same day, after the load: this line first
  listed `reservoir-computing` as a fourth, but that page is a section
  landing page and was not entered; 11 Dirac-3 and 3 EmuCore notes were.)
- **lessons** (vendor teaching material on optimization, light, photonic
  and quantum computing) -> `qc`: they explain the field, not the device;
- **research and publications** pages (topic overviews citing QCi papers)
  -> `qc`; the papers they cite enter through F5's author search, not
  through the page;
- **packages**: `eqc-models`, `eqc-direct`, `qci-client` (the Dirac-3
  software stack) -> `platform:dirac-3`; `emucore-direct` (reservoir
  computing device) and `uqrng-direct` (random number generator) -> `qc`.

Already records, not re-entered: the Dirac-3 User Guide (`[QC-2]`) and
the fraud-detection application note (`[QC-6]`), both from Task C, and
`profiling-of-cvqboost-algorithm-fraud-detection`, the web version of the
white paper held since Sprint 1 as `qci-2024-profiling-cvqboost`. Section
landing pages (`applications`, `entropy-quantum-optimization`, `lessons`,
`research-and-publications`) are navigation, not sources.
Citation: `Quantum Computing Inc., "<page title>," quantumcomputinginc.com,
<date if the page prints one, else n.d.> (hand-transcribed from the saved
page's title bar)`.

## 14. Amendment 2026-09-25: "not yet screened" is removed at promotion

Sections 6 and 11 prescribe a bulk disposition ending "; not yet
screened". That clause states tier in prose, and the Sprint 5 F28 pilot
left it stale on six papers it promoted to `read` (found in the team
lead's Manual Validation run). **Team lead's decision (Q7 = 2)**: keep the
wording for `seen` records, and remove the clause at each promotion.
Implemented in `store.ingest.set_tier()`, the one sanctioned tier-change
path, which also appends the removal to `updated_reason`; guarded by
`tests/test_ingest.py::test_promotion_removes_not_yet_screened_regression`.

## 15. Added 2026-10-03: assert the table, not the summary (Sprint 6 Task C, F43)

A source's prose summary of its own table is a second claim, and it can be
wrong while the table is right. When the two disagree, the assertion states
what the TABLE shows, and its `certainty_reasons` name the mismatch, so the
summary's wording never enters the store as if it were the measurement.
Both worked examples were checked against their sources on 2026-10-03:

- **FourierWall2, `docs/CVQBoost_Findings.md`, section 11.** The takeaway
  says CVQBoost's "in-segment train-test gap is 3-8x XGBoost's on every
  `target` cell". The table above it gives gaps of 0.083 against 0.001
  (energy, 83x), 0.389 against 0.051 (maintenance, 7.6x), 0.212 against
  0.026 (oil and gas, 8.2x) and 0.135 against 0.080 (telecom, 1.7x). The
  range is 1.7x to 83x, and one cell is below 3x.
- **hsbc-quantum-fraud-2026, `docs/HARDWARE_PLAN_PHASE_2.md`, at commit
  `a6c3453`.** The text says "Cost is also superlinear in variables"; the
  same paragraph's two-factor fit is roughly `vars^0.75 x levels^0.52`. An
  exponent of 0.75 is sublinear.

The fix to a source's own wording belongs to that source (for the hsbc
repository, a session working there; this repository never writes to it).

## 16. Applied 2026-10-03: the Cyc sources and the hardware plan (Sprint 6 Task G, F41)

**Order, stated because it slipped.** Sections 11 to 13 require this section
BEFORE the manifest runs. On 2026-10-03 the manifest
(`manifests/sprint6_f41_cyc_sources.json`) was applied first and this
section was appended minutes later, from the handoff draft written on
2026-09-29 before any manifest existed. The context decisions below are that
draft's, made in advance; only the write order slipped. Recorded for the
Sprint 6 retrospective.

The text follows the handoff's draft section (`01-intake-section-15-draft.md`,
2026-10 handoff, outside version control), renumbered 16 because section 15
is F43's. **Counts in this section are a snapshot as of 2026-10-03.**

- **Cyc engine source, releases, manual pages and archives** -> `method`. The
  precedent is `lenat-marcus-2023-trustworthy-ai`: material about how Cyc
  represents and reasons is methodology for this library, the tool it is
  building. None of it passes the `world` test (an engineering system, not a
  theorem or a measurement of nature), and none carries an ML or quantum
  workload.
  - `white-flame/clyc` is a third-party port with no Cycorp affiliation. It
    takes `method` like the rest, and its disposition says what it is.
- **The hsbc repository's Phase 2 hardware plan** -> `hsbc-2026` (decision
  4.2 of 2026-10-03). It is the submission's own document, which section 11
  says takes the context by its own definition. Its applicability adds
  `platform:dirac-3` for the Experiment 3 cost table, so the two Dirac-3 cost
  assertions it yields sit inside it. A living document, so the record pins
  commit `a6c3453`.
- **Not entered: the CVQBoost findings document** and the six assertions it
  yields. The team lead deferred its authorship until the hsbc repository
  re-runs the experiment (Sprint 6 Q4); card F51 holds it.

**Tier at load.** Sources read directly enter at `read` with
`checked_against_source` naming what was read, anchored applicability, and
(since ADR-0005 A4) a `read_extent` row of `full` or `partial` by that
reader. Sources known only through the research agent enter at `seen`.

**Local copies.** The four 2002 Cycorp manual pages were copied to
`References\` on 2026-09-29 (SHA-256 verified against their sources). The
engine source, the two OpenCyc releases and the documentation archive stay
under `GitHubRepos\`; each record's `access` points there.

**Disposition**, one line, no tier word, prefixed `Reference:` or
`Code repository:` for those kinds (section 2).

**Not entered here, and why:** seven Cycorp papers found by the research
agent have no local copy and no verified identifier, and wait on a download
decision (the handoff's `04-pending-sources.md`); Siegel, Goolsbey,
Kahlert, Matthews, "The Cyc System: Notes on Architecture" (Cycorp, 2004)
was never obtained and goes on the exception list.

## 17. Applied 2026-10-04: the QMLPapers bulk load (Sprint 6 Task J, F32)

**Written after the load, on 2026-10-05, and stated as such** (Sprint 6
retrospective I2, the same slip as section 16). The decisions it records
were made in advance, in section 9 and in the Sprint 6 plan (Q8, Q9); only
this section's write order slipped. Since I2, `scripts/intake.py` refuses
`--apply` on a manifest under `manifests/` that no section here names, so
this cannot recur. **Counts are a snapshot as of 2026-10-04.**

- `manifests/qmlpapers_bulk.json` (1,403 entries) and
  `manifests/qmlpapers_sample.json` (115, the Q8 dry run): generated by
  `scripts/qmlpapers_manifest.py` from the 13 `manifest.tsv` files, never
  by hand. Context `qml` and section 9's disposition wording; `found_via`
  is the TSV, `cited_as` its title line. 1,402 loaded; 1 refused
  (`2108.0131`, malformed in the 2021 TSV).
- `manifests/qmlpapers_nonarxiv.json` (3 entries): the `NonArxiv` rows whose
  URLs carry no resolvable id. Beer et al. took the DOI printed on its
  page 1; Aaronson and Zhang-Ni took the hand path, with no year, since
  page 1 prints none.
- `manifests/qmlpapers_routes_for_present.json` (34 rows): papers already in
  the store gain the collection as a second `found_via` route; not an
  intake manifest.
- arXiv pacing: 6 s between requests, one attempt, then DataCite (team
  lead, 2026-10-04). A new pacer per entry never waited until the clock
  became process-wide (retrospective I1).

## 18. Applied 2026-10-08: the eight pending Cycorp papers (Sprint 7 Task F, F44)

**Written before the load.** The eight papers the 2026-09-28 research agent
found (the 2026-10 handoff's `04-pending-sources.md`), downloaded with the
team lead's approval of 2026-10-06 ("each download is approved") and
entered by `scripts/sprint7_f44_cycorp_papers.py`, not by a manifest.
Section 16's context rule applies: every one is about how Cyc represents
and reasons, so each takes `method`.

- **Files.** Each PDF is in `D:\Data\Harold\EvidenceBasedDB\Papers\` under
  section 3's convention. The month in the name is the printed month where
  the paper prints one (PH20, April 2020), the registry's issue month where
  a DOI resolves (S19, L10), the arXiv month (S16), and otherwise the PDF's
  own creation date (T07, R05, M06, OV19), which the script records.
- **Origin.** Three resolve, so they are api-origin, with `access` =
  `<local path> | <identifier>`: S16 (`arXiv:1603.04402`), and two DOIs
  found on Crossref on 2026-10-08 that the plan did not expect, S19
  (`10.1609/aaai.v33i01.33011360`, AAAI 2019) and L10
  (`10.1609/aimag.v31i3.2299`, AI Magazine 31(3), 2010). Section 1 refuses
  a hand citation for an id that resolves. L10's local copy is the
  Northwestern mirror (27 pages), not the publisher's PDF; its record says
  so. The other five are hand-origin with `access` = `<local path> | <url>`;
  OV19 and PH20 are vendor documents with no venue, so they are
  `Reference:` records.
- **Venues not printed on the page.** T07, R05 and M06 print only the AAAI
  copyright. Each citation names its venue and says where the venue came
  from: the AAAI URL path, and the reference lists of the other Cycorp
  papers (T07 cites R05's workshop; S19 cites M06's symposium).
- **SHA-256.** Recorded in each record's `evidence`, with the source URL,
  the size and the download date, as section 16 did for the 2002 manual
  pages.
- **Tier.** Seven enter at `seen`. T07 is read in full (six pages) and
  enters at `read`, yielding two `vendor-self-claim` assertions: about a
  thousand inference modules (2007), and eight tactic types. The second is
  not reconciled with the six base tactic types the 2009 LarKC source
  lists; its `certainty_reasons` say why.

## 19. Applied 2026-10-15: Phase 2 results (Sprint 9 Task A, F79)

Team lead, 2026-10-14: "they are both consumers of each other and reads
are permitted without direct prompts from the other - so each could read
from each other, but cannot write to each other". This repository and
`hsbc-qfraud-phase2` read each other freely; neither writes to the other.

**Inbound: a Phase 2 result entering the store.**

- **Read it from Phase 2's git history, at a named commit.** Use
  `git -C <phase2> show <commit>:<file>`, which is a read. Never read the
  working tree as the evidence: Phase 2 is an active repository, and its
  files move. Pin the last commit that touched the file, and check that the
  working copy still matches it.
- **Never copy it into Phase 2 and never edit it there.** The local copy
  the record depends on is the committed blob itself. Its SHA-256 goes in
  the record's `evidence`.
- **Provenance names four things:** the repository, the commit, the file
  and the run (date and sprint, as the document states them). `access` is
  `<local path in Phase 2> | <GitHub URL at the commit>`. The repository
  is private, so the URL is the pointer, and the commit is what the record
  depends on.
- **Assert only what the document still stands behind.** A Phase 2
  document corrects itself in place. A column or figure it declares wrong
  is not asserted, and a result it calls unverified is not imported.
- **Certainty** follows the Phase 1 precedent: the consumer project's own
  hardware measurement, read directly, starts HIGH (`HW`). It is the same
  project as earlier consumer results, so a `supports` link between them
  is fine, but it is not independent corroboration.
- **The quote test reads the blob at the commit.** It never reads the
  working tree, so it neither breaks nor passes on text that was never read.

The first trial: `scripts/sprint9_f79_phase2_b4_b5_inbound.py`, record
`hsbc-qfraud-phase2-b4-b5-hardware-result` (Phase 2's
`docs/B4_B5_HARDWARE_RESULT.md` at commit 139fa13). It yields four
assertions: Dirac-3 matches its classical proxy inside the pocket; no
in-segment edge on the 8 scoreable cells; the device sits below Phase 2's
classical bar; and B5's QSVM is weak. The quotes are checked by
`tests/test_f79_phase2_inbound.py`.

**Outbound: a change wanted in Phase 2.** Write a prompt the team lead
pastes into a Phase 2 session. Never write the change from here (hook:
`.claude/hooks/block_sibling_repo_writes.py`). The prompt:

- states what to change, and where (file and line or section);
- says why, with each claim's provenance inline (record id, source and
  anchor), because Phase 2's session may not resolve this repository's
  ids;
- asks for that repository's own test or check, proven to fail where it
  guards something.

## 20. Applied 2026-10-15: F68's door fixes and the F69 paper (Sprint 9 Task B)

- **The door reads two more identifier forms** (`store/citations.py`,
  `parse_access`): old-style arXiv ids from before April 2007
  (`quant-ph/0405098`, `math.PR/0601001`), and DOIs that contain
  parentheses (`10.1016/0304-4149(89)90040-9`). A closing parenthesis with
  no opening one inside the DOI belongs to the prose and is dropped.
- **The five Massoli entries refused on 2026-10-12** were re-run by
  `scripts/sprint9_f68_massoli_rerun.py`, which reuses F61's parsing,
  classification and entry shape for only those five. All five entered at
  `seen`. Their `updated_reason` names F61's script (its entry builder)
  with the Sprint 9 tag.
- **F69: the file named "Cerezo" is by Nathan Wiebe.** Its first page reads
  "To cite this article: Nathan Wiebe 2020 New J. Phys. 22 091001", and its
  second page gives `https://doi.org/10.1088/1367-2630/abac39`. It is open
  access (IOP "PERSPECTIVE, OPEN ACCESS"). It enters at `seen` through the
  door by `manifests/sprint9_f69_wiebe_key_questions.json`: access
  `<local path> | DOI:10.1088/1367-2630/abac39`, the local copy's SHA-256 in
  `evidence`, and `found_via` naming the QMLPapers `NonArxiv` folder. The
  file's misleading name is recorded, not changed: the folder is the team
  lead's.

## 21. Applied 2026-10-15: the ceiling group's local copies and two new papers (Sprint 9 Task E, F78)

- **Downloads** (team lead, 2026-10-14: every paper in the group with no
  local PDF goes into `Papers\`): `scripts/sprint9_f78_downloads.py` saved
  Ishida et al. (arXiv:2202.00395), Theisen et al. (arXiv:2106.03357), Thanh
  et al. (arXiv:2511.00964, the preprint of the Machine Learning paper) and
  Allen (the Federal Reserve's own FEDS 2025-017 PDF), each checked against
  its first page. arXiv went through the door's paced fetcher. Chen et al.
  2025 and Han and Verdu 1994 have no free copy; they are the team lead's
  hand downloads (plan Q3 = 1) and were not fetched.
- **Repositories** (plan Q2 = 2): six shallow clones in
  `D:\Data\Harold\EvidenceBasedDB\GitHubRepos\`, each read at the commit
  named in its read row. The seventh record (CE-14) is the handbook's
  rendered site, the same source as the handbook repository.
- **Two papers the group cites but the store lacked** enter at `seen` by
  `manifests/sprint9_f78_ishida_theisen.json`, each with `access`
  `arXiv:<id> | <local path>`; the reading script promotes them.
- **Han and Verdu 1994** is stored as `te-sun-1994-generalizing-fano-inequality`:
  Crossref gave the first author's name as one string, so the derived id
  took "te-sun". The citation reads "Te Sun Han". Ids are not renamed; the
  record's evidence says so.

## 22. Applied 2026-10-15: the first read-for-claims slice (Sprint 9 Task G, F80)

- **The slice** is recorded in `manifests/sprint9_f80_slice.json` by
  `scripts/sprint9_f80_slice.py` (team lead, plan Q7 = 2): the 26 records at
  `seen` or `screened` under `hsbc-2026`, `platform:dirac-3` and
  `platform:dirac-3s`, none in the ceiling group, and the 50 most-cited
  `qml` records at `seen` or `screened`. It is a record of what this sprint
  chose, not an intake list: it adds no record, and its citation counts are
  never written to the store (they change).
- **Counts.** OpenAlex, queried by each record's arXiv DOI, then by the
  journal DOI the store's probes recorded (`version_of`): 1,146 of 1,521
  candidates counted. Semantic Scholar's unauthenticated batch endpoint
  answered 429 to every attempt on 2026-10-15 and is not used. The 375
  uncounted records are the selection's stated limit.
- **Copies.** `scripts/sprint9_f80_downloads.py` saved the free arXiv
  version of the 21 slice papers stored by journal DOI only, each checked
  for its arXiv stamp on the first page. One repository was shallow-cloned
  into `GitHubRepos\` (plan Q2 = 2's rule).
- From Sprint 10, F57 releases 74 records per sprint until none remain at
  `seen` or `screened` (team lead, 2026-10-15).

## 23. Applied 2026-10-15: the slice read and entered (Sprint 9 Task G, F80)

- **Reads.** Ten Sonnet 5.5 first-pass readers, kept verbatim in
  `manifests/sprint9_f80_reads/group_*.json` (J1 to J3 the submission's
  sources, Q1 to Q7 the QML papers). Some entries name a `quote_file` or
  `quote_file_default` in the session's scratch folder: those were the
  readers' text extracts and no longer exist. `scripts/sprint9_f80_reading.py`
  ignores them and resolves every quote to the real source file, and the
  quote test checks it there.
- **Entered** (as a snapshot on 2026-10-15): 65 of the 76 records promoted to
  `read`, 233 assertions (234 first; the review dropped one that restated a
  determinate fact), each read with a subagent row and the coordinator's
  `partial` row (ADR-0005 A4). Local copies were added to `access` where
  missing, each with its SHA-256. The two clones carry the commit they were
  read at instead. eqc-models carries SHA-256s for the wheel and the PyPI
  metadata it was read from, beside the stored sdist.
- **Refused** (11, kept at `seen`, each with its reason in the record's
  history): eight QCi application pages and one QCi article name Dirac-1
  while the store tags them `platform:dirac-3` (F84). The space-logistics
  page has no body text. The trade magazine PDF has no text layer.

## 24. Applied 2026-10-15: the F62 discovery candidates at `seen` (Sprint 9 Task J, Manual Validation Q4 = 1)

- **What entered.** The team lead chose all 100 candidates in the four
  top-25 lists of `f62_review_2026-10-15.md` except 13 named off-topic.
  `scripts/sprint9_f62_enter_seen.py` pins each exclusion to its title,
  so a re-ranked file stops the run instead of excluding the wrong paper.
  All 87 entered at `seen` (as a snapshot on 2026-10-15): 50 `ml`, 16 `qc`,
  11 `world`, 10 `qml`.
- **Through the door, never from OpenAlex.** Id, title and citation come
  from the identifier: the arXiv id where OpenAlex or Semantic Scholar gave
  one (57, paced 18 s apart), the DOI otherwise. OpenAlex's DOI can be a
  mirror's ("Attention Is All You Need" carries a preprint server's DOI).
- **A title check refused 5 at first.** Each arXiv preprint has a title
  other than the published paper's (nnU-Net's preprint is "Automated Design
  of Deep Learning Methods for Biomedical Image Segmentation"). They are
  the same works; they entered by the journal DOI, whose title matched. A
  wrong identifier attaches a different paper with no error, so the check
  stays.
- **Context** is the stream's (the fraud stream enters as `ml`: the HSBC
  context holds the submission's own facts), except where it was plainly
  wrong: quantum simulation and chemistry papers in the qml stream are
  `qc`, condensed-matter and tensor-method physics in the tensor stream are
  `world`, and three tensor decomposition papers are `ml`. Screening
  refines it.
- **Reading** comes later, from F57's 74-per-sprint release.

## 25. Applied 2026-10-16: Task E's two closed papers (Sprint 9 Task E, F78; Manual Validation item 7 and Q6 = 1)

- **Chen et al. 2025 arrived** as the team lead's hand download,
  `Papers\2025-MM_Chen_An-efficient-Bayes-error-rate-estimation-method.pdf`
  (the "MM" placeholder was left in the name; the paper was published
  online 11 April 2025; the record points at the file as named). It was
  read in the Task E shape: a first-pass subagent read the whole paper
  (`manifests/sprint9_f78_reads/group_g.json`, kept verbatim), then the
  coordinator read the opening and every quoted passage in context. 12
  assertions entered, as a snapshot on 2026-10-16. The coordinator cut five
  reader judgments (a critique of the proof, a reading of Table 4's spread,
  a judgment on the validity criterion, a contradiction phrased as the
  reader's, a relevance clause) and restored one space a quote had lost.
- **Han and Verdu 1994 has no free copy** (team lead, 2026-10-16). It
  stays at `seen` with that reason. Team lead Q6 = 1: its content is
  covered by free sources instead.
  - Scarlett and Cevher 2019 (already `read`), section 7.2, equation
    (108): the data-processing form of Fano holds for a non-uniform prior;
    entered as a coordinator assertion from a re-read of pp. 35-36.
  - Chen, Guntuboyina and Zhang 2016, "On Bayes Risk Lower Bounds", JMLR
    17 (open access; arXiv:1410.0503), whose Corollary 5 is a generalized
    Fano inequality for any prior and any zero-one loss. Downloaded from
    jmlr.org to `Papers\2016-12_Chen_On-Bayes-Risk-Lower-Bounds.pdf` and
    entered through the door by
    `manifests/sprint9_q6_chen_guntuboyina_zhang.json`, then read in the
    Task E shape (group H): sections 1 to 4 and 8 in full, so the subagent
    row says "in part". 9 assertions entered, two clauses narrowed to what
    the quoted passages say.
- **Quote check fixes.** The shared normalizer in the quote tests now
  expands the "ff", "ffi" and "ffl" ligatures, as it already did "fi" and
  "fl" (the JMLR text sets "affirmative" with one). Five Chen quotes had
  lost a space the PDF carries ("Theorem 1 (", "O(n2) ."); restored by
  `QUOTE_EDITS`. The Task E sync now compares quotes too, so a corrected
  quote reaches the store.

## 26. Rule from 2026-10-17: a reading script checks quotes before it writes, and syncs every field (Sprint 9 retrospective I3 and I4)

- **Check before the write.** A script that enters assertions with quotes
  calls `store.quotes.require_verbatim(record_id, citation_context, text)`
  for every assertion, with `text` from `store.quotes.source_text(path)`,
  before it writes anything. A quote not in its local source stops the run,
  so it never reaches the store. The live-store quote tests stay as the
  backstop. `scripts/sprint9_f78_ceiling_reading.py` (`check_quotes`) is
  the first script to do this.
- **One normalizer.** `store.quotes.plain` applies Unicode NFKC, then makes
  the typographic quotes plain. Ligatures, the micro sign and other
  compatibility forms fold in one step, not one hand-added character per
  new source. Compare `plain(quote)` with the plain source text, never the
  raw quote.
- **Sync every field.** A script that corrects an assertion it already
  entered calls `store.ingest.sync_assertion(conn, wanted, note, today)`,
  never its own UPDATE over a hand-named list of columns. The field list is
  checked against `AssertionRecord` on every call, so a field cannot be left
  out (Task E's list left out the quotes). Documents and relations are only
  added to, never removed: other steps add them later. A corrected context
  replaces the stored ones (review of 3a455ce). `sprint9_f78` and
  `sprint9_f80` both use it.

## 27. Applied 2026-10-18: Sprint 10's sourced entries (Tasks F, G and H: F84, F85, F83)

Every count is a snapshot as of 2026-10-18.

- **F84** (`scripts/sprint10_f84_dirac1.py`): no new source. The nine QCi
  records F80 refused are retagged to `platform:dirac-1` (ADR-0004 A10)
  and read; their 12 assertions come from F80's read groups
  (`manifests/sprint9_f80_reads/group_j3.json`, `group_j2.json`).
- **F85** (`scripts/sprint10_f85_dirac3s_verify.py`): the second Phase 2
  result by section 19's inbound path, read through `git show` at Phase 2
  commit e126dbd; a reference record and four HW assertions.
- **F83** (`scripts/sprint10_f83_optimization_bounds.py`): two hand-entered
  sources. Boyd and Vandenberghe's Convex Optimization, downloaded from the
  authors' free copy into `Papers\` with its SHA-256; Gurobi 13.0's
  parameter reference, saved into `References\Gurobi\`.
- **Section 26 was missed, then applied.** None of the three scripts called
  `require_verbatim` before writing on its first apply; only the
  live-store tests checked the quotes, after the write. Each now runs
  `check_quotes()` first, and a test plants a quote that is not in the
  source and expects the refusal. No stored quote was wrong (the tests had
  passed on every apply).

## 28. Applied 2026-10-18: the second read-for-claims slice (Sprint 10 Task I, F89)

- **The slice** is recorded in `manifests/sprint10_f89_slice.json` by
  `scripts/sprint10_f89_slice.py`: the 74 most-cited `qml` records at
  `seen` or `screened` with no read row. Nothing unread remains under
  `hsbc-2026` or the Dirac platforms (the script refuses to run if any
  does). The nine Dirac-1 records do not count (plan Q3 = 1). Like
  section 22's file, it records what the sprint chose and adds no record;
  counts are never written to the store.
- **Counts.** Taken as F80's were (OpenAlex by arXiv DOI, then by a probed
  journal DOI): 1,098 of 1,481 candidates counted (605 and 493); 383
  uncounted, the selection's stated limit. The top 74 run from 732 to 65
  citations.
- **F57's count, refreshed:** 2,033 records at `seen` or `screened`, of
  which 2,031 have no read row.

## 29. Applied 2026-10-18: the second slice read and entered (Sprint 10 Task I, F89)

Every count is a snapshot as of 2026-10-18.

- **Copies.** `scripts/sprint10_f89_downloads.py` fetched free copies of the
  slice papers with none (arXiv through the paced fetcher; open-access PDFs
  OpenAlex lists), into `Papers\`; two more by their direct open-access
  links, one by an arXiv title search, and Dunjko 2020's Quantum Views page
  into `References\QuantumViews\`. Nine papers have no free copy (NO_COPY in
  the reading script): each stays `seen` with that reason and goes on the
  hand-download list.
- **Reads.** Nine Sonnet 5.5 first-pass readers, kept verbatim in
  `manifests/sprint10_f89_reads/group_r1.json` to `group_r9.json`, under
  the protocol F88 tightened (a reader's own conclusions in
  `reader_inference`, never in a value). `scripts/sprint10_f89_reading.py`
  enters them after the coordinator's read: every quote checked before the
  write (section 26), nine quotes corrected to the source's exact
  characters, two values rewritten, three contexts corrected, one record
  refused (a workforce review that bears on no context).
- **Result.** 64 of the 74 records read and yielding 216 assertions (42
  HIGH, 2 MODERATE, 172 LOW, by the grading Sprint 9's reads used); 1 refused; 9 with no
  copy. The store holds 224 records at `read` and 793 assertions.
- **F57's count after this release:** 1,969 records at `seen` or
  `screened`, of which 1,966 have no read row (the other 3 are read and
  refused: two by F80, one here).

## 30. Applied 2026-10-19: the live discovery re-run's candidates at `seen` (Sprint 10 Task J, F87; Manual Validation Q4 = 2 and Q6)

Every count is a snapshot as of 2026-10-19.

- **What entered.** The live re-run (`f62_review_2026-10-19.md`) listed 99
  candidates in its four top lists, after the F87 filters dropped 14
  off-topic records before ranking. The team lead excluded 6 more as
  off-topic; 2 were Sprint 9 exclusions back at the top. The team lead
  moved 2 qml-stream papers that apply classical ML to molecules (FCHL
  revisited; the alchemical representation paper) to `ml`: "do these
  better fit in ml and can be switched there". `scripts/sprint10_f87_enter_seen.py`
  pins every exclusion and both switches to their titles. All 91 entered
  at `seen`: 55 `ml`, 19 `qc`, 11 `world`, 6 `qml`.
- **The door and the title check are section 24's.** The check refused 5
  at first, each an arXiv preprint titled other than the published paper
  (qml 5's preprint is "Robust determination of molecular spectra on a
  quantum processor"). They entered by the journal DOI, whose title
  matched.
- **F57's count after this release:** 2,060 records at `seen` or
  `screened`, of which 2,057 have no read row. The store holds 2,284
  papers.

## 31. Rule from 2026-10-21: the quote check is in the write path, and the coordinator's edits name their passages (Sprint 10 retrospective I1 and I2)

Extends section 26. The 18 scripts that wrote assertions before this
rule (Sprint 10 and earlier) have run and stay as they are, listed by name
in `tests/test_verified_writes.py`; every other script in `scripts/`,
whatever its name, is held to both rules. The scan matches names, not
calls, so an aliased import is caught too.

- **Write only through the check (I2).** `require_verbatim` returns a
  `Verified`. A script writes assertions with
  `store.ingest.insert_verified_assertion(conn, a, verified)` and
  `sync_verified_assertion(conn, a, verified, note, today)`, never
  `insert_assertion` or `sync_assertion`. Each refuses a write whose
  `Verified` is missing or names another record or other quotes. Sprint
  10's Tasks F, G and H wrote before checking; with this path they could
  not have.
- **Name the passage behind every edit (I1).** When the coordinator
  replaces a reader's value, drops a quote or moves a context, the script
  calls `store.quotes.require_edit_basis(record_id, value, basis, text)`
  first. `basis` is the passage or passages the edit rests on, each
  verbatim in the source. For a replaced value, every number and math sign
  in it must be in those passages; a figure read from the page image
  because the text layer lost it (the root sign in F89's "R >= sqrt 2")
  goes in `read_from_page`, and the value says so. The check does not test
  meaning: a wrong word with the right numbers passes, so the fresh-eyes
  review stays.
- **Measured on Sprint 10's F89 edits** (snapshot as of 2026-10-21): the
  rule flags the root-2 value and four more whose numbers are in the
  source but not in their quotes. No stored value is wrong.

## 32. Applied 2026-10-21: the third read-for-claims slice, 200 records (Sprint 11 Task G, F96)

Every count is a snapshot as of 2026-10-21. **Written after the slice ran,
not before** (a slip, disclosed in the sprint note: section 11's order puts
the section first; `tests/test_intake.py` caught it at the next full run).

- **The slice** is recorded in `manifests/sprint11_f96_slice.json` by
  `scripts/sprint11_f96_slice.py`: the 200 most-cited `qml` records at
  `seen` or `screened` with no read row, in F57's relevance order (team
  lead, 2026-10-21: "switch back to the relavance ranking"). Nothing unread
  remains under `hsbc-2026` or the Dirac platforms. Left out: the 15
  records Task F reads (arXiv ids in the names of unlinked PDFs in
  `Papers\`, and the team lead's list), so no record is read twice; and the
  9 records of section 29's slice still unread for want of a free copy.
- **Counts.** Taken as F89's were: 1,015 of 1,405 candidates counted (565
  by arXiv DOI, 450 by a probed journal DOI); 390 uncounted, the
  selection's stated limit. The top 200 run from 65 to 14 citations.
- **Copies.** `scripts/sprint11_f96_downloads.py` (section 29's rules, with
  a heartbeat file) saved 9 free copies into `Papers\`; one failed on an
  SSL certificate error (Macaluso 2020); 7 have no free copy known to
  OpenAlex. The rest of the 200 had local copies already.
- **F57's count before this release:** 2,060 records at `seen` or
  `screened`, of which 2,057 have no read row.
- **The read ledger** (`manifests/sprint11_read_ledger.json`, built by
  `scripts/sprint11_read_ledger.py`) gives every record Tasks E, F and G
  read to exactly one group of at most 8, read by one first-pass reader;
  at most 5 readers run at once (team lead, 2026-10-21). Task G's 200: 192
  in groups g01 to g24, 8 in `no_copy` with the reason. Readers work from
  local files only, under `manifests/sprint11_reads/READER_PROMPT.md`, and
  return `manifests/sprint11_reads/group_<g>.json`.
  `tests/test_sprint11_read_ledger.py` fails if a record is in two groups
  or a reader file holds a record outside its group.
