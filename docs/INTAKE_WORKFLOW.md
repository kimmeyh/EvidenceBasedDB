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

## 33. Applied 2026-10-22: QCi's answers of 2026-10-20 and 2026-10-21, as vendor statements (Sprint 11 Task C, F92)

Every count is a snapshot as of 2026-10-22. Written before the script was
applied.

- **Sources.** Three replies filed by the team lead in Phase 2's
  `docs/qci_package/` (read only, F79). Phase 2 git-ignores that folder,
  so no commit names them; each source record names the file, its SHA-256
  at read, the sender and the send date, and
  `scripts/sprint11_f92_qci_answers.py` refuses to run when a hash
  differs. Send dates come from the headers: the 2026-10-20 reply's date
  and the first 2026-10-21 reply's time are read from the header each is
  quoted under in the later reply.
- **Text.** An Outlook `.msg` holds its body as UTF-16LE; the script
  decodes the whole file at both byte alignments and matches each quote in
  that text through `require_verbatim` before any write, then writes only
  through `insert_verified_assertion` (section 31). Phase 2's
  `docs/phase2/DIRAC_UNDERSTANDINGS.md` section 4 at b074780 was read for
  the question numbering (the email's 3 to 14 are its A1 to A12).
- **Grading.** A vendor's statement by email: `vendor-self-claim`,
  evidence tag N/A, MODERATE; LOW where the answer is hedged ("I assume")
  or states a plan (raw values on the cloud, Dirac-3S replacing Dirac-3,
  9980 levels) or names no comparison ("much better results"). Values name
  roles; citations name the sender.
- **Relations.** Stored assertions are not rewritten, and no link is
  made. Every bearing is named in the value with the reason no link is
  made (ADR-0004 A8 (b)): the guide still says what the stored records say
  it says, and the cloud answers add to it. The first apply linked the
  answer to question 8 `supports`
  `dirac3s-analog-resolution-about-200-to-1`; the fresh-eyes review the
  same day found that it fails A8 (b) (that record states the guide's
  text, the "yes" answered a two-part question, and the next answer
  narrows the ratio to linear contributions). The script withdraws it by
  name, since the sync adds relations and never removes them. The same
  review corrected seven values, two citations' subject line, and one
  inferred role; one finding (a "sum of levels 954" already documented)
  was not adopted, as neither the store nor Phase 2's section 4 holds it. The 954 levels are entered twice (Dirac-3
  and Dirac-3S) with the unit "not stated", as the email gives none.
- **Count.** 3 source records at `read` and 18 assertions.
  `tests/test_f92_qci_answers.py` checks the hashes, each quote in its own
  email, each number in its own quotes, that no link remains, the hedges and
  the stored values.
- **Classed against the Dirac-3S guide.** Three of the 18 are under
  `platform:dirac-3`, so the F65 guard
  (`test_every_prior_dirac3_assertion_is_classed`) failed in the full suite
  until they were classed. All three are "not addressed" in
  `scripts/sprint8_f65_dirac3s_reading.py` CLASSED: the guide predates the
  emails and mentions none of the three points. The guard did its job; the
  F92 apply had not checked it.

## 34. Applied 2026-10-22: Phase 2's F108 ceiling validation, by the inbound path (Sprint 11 Task D, F93)

Every count is a snapshot as of 2026-10-22. Written after the first apply and
before the commit (section 33 was written first; this one ran in the same
pass and is recorded here at once).

- **Source.** `docs/phase2/F108_CEILING_VALIDATION.md` at Phase 2 commit
  eef3349, the last to touch it (HEAD dbfa4da holds the same blob), read
  through `git show`, SHA-256 pinned (section 19's inbound rule).
- **Entered.** 1 source record at `read` and 4 SIM assertions under `ml`
  by `scripts/sprint11_f93_f108_ceiling.py`, through the verified write
  path (section 31): the verdict at MODERATE (the pass rule was read after
  the run), three measurements at HIGH with Phase 2's inferences and
  unverified causes carried in the values. No relation: the learning-curve
  result confirms only half of `ding-floor-c-is-model-and-config-specific`.
- **Answer document.** `docs/research/ceilings-ml-and-optimization.md`
  carries a dated amendment naming the four assertions.
  `tests/test_f93_f108_ceiling.py` checks the hash, each quote at the
  pinned commit, each number in its own quotes, the carried caveats and
  the stored values.
- **Fresh-eyes review, the same day.** It found the amendment named the
  wrong method (section 5 point 2 is the soft-label estimator, which F108
  did not test) and stated the coordinator's reading unlabeled; both
  corrected. Two caveats added to the values (the reference arm passes
  only through the absolute margin; the AUPRC floor understates by about
  0.04 and is unstable), and a curation note moved from a value to its
  certainty reasons. **Finding:** one quote had no space after its `;`,
  so the quote pattern did not parse it and `require_verbatim` passed
  without checking it; the number test caught it. Recorded for the
  retrospective.

## 35. Applied 2026-10-22: magic state cultivation, by DOI with the free preprint read (Sprint 11 Task E, F91)

Every count is a snapshot as of 2026-10-22. Written before the first
apply; corrected after the fresh-eyes review and the second apply.

- **Source.** Rosenfeld et al., "Magic state cultivation on a
  superconducting quantum processor", Science, DOI:10.1126/science.aee7961.
  Crossref lists the publisher's license as starting 2027-10-15, so the
  Science copy was not used. The free preprint arXiv:2512.13908v1 was
  fetched through the paced fetcher into `Papers\` (SHA-256 642ec2da...,
  pinned in the test) and every quote is checked against it. The version
  link is recorded as a hand probe (`version_of` arXiv:2512.13908).
- **The abstracts differ.** The Science abstract says the fidelity is "at
  least 0.9999(1)"; the preprint v1 abstract does not say "at least". The
  record's evidence names the difference, and the fidelity assertion
  states the number as a lower bound, as the paper's conclusion does.
- **Entered.** 1 paper record at `read` (read in part: abstract,
  introduction, results, outlook, and three supplement sections) and 6
  assertions under `qc`, all LOW: 5 HW (one study's hardware
  measurement, by the device's maker, not replicated) and 1 SIM (the
  authors' projection for halved noise), by
  `scripts/sprint11_f91_magic_state.py` through the verified write path
  (section 31). No relation: no stored assertion makes the same claim.
- **Fresh-eyes review, the same day.** It found three values that
  misstated scope: the 8% retention named the circuit's contents as the
  filter (the filter is any detection event in the whole circuit); the
  76(3)% came from a different, shorter circuit and read as a like-for-like
  baseline; and "distance-5 surface code" is a distance-5 encoding
  compatible with the surface code, not itself matchable. The 40x figure
  is the full circuit's error, an upper bound on the state's. All four
  corrected, with the device (Willow) and the starting code (distance-3
  color code) named, and the paper's own caveats added: drift of about
  1×10−4 an hour, no leakage removal units, a proof-of-principle
  grafting. The projection to about 2 × 10−5 was added as its own SIM
  assertion. The disposition was synced to the same scope.
- **Test.** `tests/test_f91_magic_state.py` checks the preprint's hash,
  each quote in the preprint, that every pair of quote marks is a parsed
  quote (the section 34 finding; on its first run it caught a label of
  this script's own that held quote marks), each digit string in a value
  in its own quotes, the abstracts' difference, and every stored field.

## 36. Applied 2026-10-22: new papers in `Papers\` and the team lead's list, entered before reading (Sprint 11 Task F, F97)

Every count is a snapshot as of 2026-10-22. Written before the apply;
counts confirmed after it (`tests/test_sprint11_f97_intake.py`).

- **Before.** 2,289 paper-table records (229 `read`, 14 `screened`,
  2,046 `seen`, repositories included); 821 assertions.
- **Local copies linked.** 38 files in `Papers\` named by no record's
  `access`, Task G's 9 copies held out (the planning snapshot said 37;
  the difference is one file counted with G). Each matched its record by
  the arXiv id in its name or first-page stamp, or by a DOI on its first
  pages, and each record's title was checked against the PDF's first two
  pages. Three differ in form only (Kerger's title is LaTeX; Dupont's
  arXiv v1 title differs from the published one; RAND's DOI is printed as
  a rand.org short link), and one first-page arXiv id was a citation, not
  the paper's own (the QCi fraud paper cites arXiv:2407.04512), so it was
  not matched. 38 files to 36 records (two pairs of duplicate files);
  the path is appended to `access`, with the SHA-256 in `evidence`.
- **The team lead's list.** Six preprints through the paced fetcher
  (arXiv:2610.24426, 2610.10629, 2610.00841, 2509.03505, 2609.17488 and
  Pere's 2509.16410, already in the store with no copy), NBER Working
  Paper w35905 copied into `Papers\` (the original left in Downloads;
  identical SHA-256), and the NVIDIA blog article saved to `References\`.
  7 new records at `seen` (the blog's citation hand-transcribed from the
  page's own tags). 6 repository records; 6 `code-of` links, each
  carrying the sentence or title-page line that names the repository.
  LimiX's repository is linked to both LimiX papers: both title pages
  print it.
- **Changed from the plan: one repository is not linked.**
  `NVIDIA/auto-ontology-eval` is entered but linked to no paper: the blog
  article never names it, and GitHub describes it as a Text-to-SQL
  evaluation toolkit, so no source says it is the code of a paper here.
- **Script.** `scripts/sprint11_f97_intake.py` (`--fetch`, dry run,
  `--apply`). Reading follows by the ledger (section 32): the 30 matched
  records not yet `read`, the 7 new records and Pere's, in Task F
  groups.

## 37. Applied 2026-10-22: Task F's 38 records read and entered (Sprint 11 Task F, F97)

Every count is a snapshot as of 2026-10-22. Written before the apply;
counts confirmed after it. Section 38 records the second apply that
corrected two of these values' quotes.

- **Reads.** Ledger groups g25 to g29 (section 32's ledger; no record in
  two groups), one Sonnet 5.5 first-pass reader each, five at once, under
  `manifests/sprint11_reads/READER_PROMPT.md`. Every reader's quotes passed
  the repository's own extraction before it finished; the blog article was
  read through `store.quotes.source_text`, which the checker now uses too.
- **The coordinator's read.** Every value read against its quoted passages
  with about 220 characters each side. It changed seven values (a table the
  paper cites from its reference 2 presented as the paper's own; "lower
  than GBDTs" where the quote says "comparatively low"; relabeled datasets
  called "fully classical"; a machine and version outside the quotes; three
  critical functions left unnamed; two results of a stylized economic
  model not scoped to it) and added the quotes those changes rest on.
- **Grades.** HIGH only for the 54 ids named in HIGH_REVIEWED (a paper's
  own setup, scope, limits, definition or proved result); 4 vendor product
  descriptions MODERATE; every other assertion LOW. The reader's own
  suggestion is not used.
- **Entered.** 125 assertions from 37 records, each record to `read` with
  a subagent read row and the coordinator's partial read row. One record
  (Li 2024, photon-counting Raman spectroscopy) bears on no context: read
  rows and the reason, tier unchanged.
- **Script.** `scripts/sprint11_reading.py --task F`, through the verified
  write path (section 31); it refuses a reader file whose records are not
  its ledger group's.

## 38. Applied 2026-10-22: Task G's 192 records read and entered (Sprint 11 Task G, F96)

Every count is a snapshot as of 2026-10-22. Written before the first apply;
corrected after the fresh-eyes review and the second apply (below).

- **Reads.** Ledger groups g01 to g24 (section 32's ledger), one Sonnet 5.5
  first-pass reader each, at most five at once, under
  `manifests/sprint11_reads/READER_PROMPT.md`, from local copies only.
- **No copy: 8 records, not read, tier unchanged, the reason recorded on
  each.** Six are closed (Elsevier, IEEE twice, Taylor & Francis, Springer
  twice). Macaluso 2020's free host failed TLS certificate verification on
  2026-10-21 and was not fetched around the check. Those 7 go on the
  hand-download list. Mezquita 2021 is a RETRACTED chapter: not read and
  NOT for the hand-download list.
- **The coordinator's read.** Every value read against its quoted passages
  with about 220 characters each side, group by group. It replaced 13
  values: where the reader's text carried more than its quotes (a figure
  number, a device or vendor name, a task name, "2D", an author's
  employer, a connectivity property, a simulation scope the quotes do not
  state, a footnote marker run into a year), or less (an error term left
  out), or where the text layer flattened an exponent the value restores
  (two complexity bounds); added quotes for 16 assertions whose
  value rests on a sentence beside the reader's quote, and corrected 11
  quotes to the source's exact characters.
- **Mechanical checks, in `verify()`, before any write.** Every quote
  verbatim in the source text (`require_verbatim`); every quote parses as
  a quote; every replaced value and every quote edit rests on named
  passages (`require_edit_basis`, section 31); every figure in a value
  appears in that assertion's own quotes (stricter than section 29: the
  paper as a whole is not enough). Each one refuses the apply.
- **Slip, found by the full suite and the fresh-eyes review.** The first
  apply of Tasks F and G ran without `require_edit_basis`, and the figure
  check only printed in the dry run. `tests/test_verified_writes.py`
  failed on the script. The review also found 7 replaced values (Tasks F
  and G) still saying more than their quotes, and 3 measured results
  graded HIGH. The second apply, with both checks in `verify()`: quotes
  added for the 7 (or the extra words cut), and 5 measured negative
  results moved to LOW (qudit-hardware-limit,
  fischer-residual-bias-large-systems, qcbm-scaling-limit,
  qsvr-hardware-auc-050, ewaniuk-weak-nonlinearity-trainability): a
  measured result from one study is empirical, not a stated limit.
- **Grades.** HIGH only for the 281 ids named in HIGH_REVIEWED (a paper's
  own setup, scope, limits, definition or proved result); one vendor product
  description MODERATE (IQM's description of its Spark prototype); every
  other assertion LOW (367). A value that mixes the paper's own setup with
  an empirical claim stays LOW.
- **Entered.** 649 assertions from 189 records (qml 454, qc 156, world
  20, method 10, ml 9), each record to `read` with a subagent read row and
  the coordinator's partial read row. Three records bear on no context
  (Ke 2023, tree tensor network states; Lawrie 2023, metamaterial design;
  Avdonin 2023, quantum trees): read rows and the reason, tier unchanged.
- **F57's count after this release** (with Tasks E and F applied, the
  same query as section 32): 1,847 records at `seen` or `screened`, of
  which 1,840 have no read row (2,060 and 2,057 before). The store: 455
  `read`, 2 `screened`, 1,845 `seen`; 1,595 assertions.
- **Script.** `scripts/sprint11_reading.py --task G`, through the verified
  write path (section 31). `tests/test_sprint11_reading.py` covers Tasks F
  and G; `tests/test_sprint11_f97_intake.py` covers section 36's intake.

## 39. Applied 2026-10-22: Sprint 11 Manual Validation decisions (F97 link, the hand-download list)

Every count is a snapshot as of 2026-10-22. Written before the apply.

- **`NVIDIA/auto-ontology-eval` linked `code-of` the NVIDIA blog record
  (team lead, Q1 = 2).** Section 36 entered it unlinked, because no source
  names it as the article's code. The team lead chose the link anyway. Its
  evidence says so plainly: the link rests on the team lead's decision,
  not on a sentence in a source. The repository record's disposition and
  updated reason say the same. `scripts/sprint11_f97_intake.py --apply`;
  7 `code-of` links after (6 before).
- **The hand-download list is computed, never kept by hand (team lead,
  Q2: "Keep an on going list of these in relative priority order").** A
  record is on it when its updated reason puts it on the hand-download
  list (and not "NOT for the hand-download list"), it is not `read`, and
  its `access` names no local copy. A file dropped into `Papers\` and
  linked, or a read, takes it off with no edit to any list.
  `python scripts/hand_download_list.py` prints it.
- **Priority order.** First the records named for a question the team
  lead set (selected outside a ranked F57 release, so they carry no
  count; today only Te Sun 1994, from the F78 ceiling group). Then the
  rest by the OpenAlex citation count recorded when F57's relevance
  ranking selected them (`manifests/*_slice.json`), highest first. The
  order is a proposal: a record the team lead wants sooner can be moved up
  by a named override in the script.
- **On the list today: 16 records** (1 named, 15 ranked: 8 from Sprint
  10's release, 7 from Sprint 11's). Off it: Chen
  2025 (now `read`), and the two RETRACTED items (Valdez 2023, Mezquita
  2021), which are never for the list.
- **Not on it yet: F62's discovery candidates.** Sprint 9 and 10's F62
  runs wrote their own hand-download files outside git
  (`D:\Data\Harold\EvidenceBasedDB\discovery\f62_hand_download_*.md`). 22
  of their entries are store records at `seen` with no copy and no list
  segment, so the resolver does not see them (Schuld 2018 is on both; 2
  are not in the store). Folding them in is the team lead's call, asked
  at Manual Validation.
- **A first for the store.** The `code-of` link above is the first
  source link whose evidence is a decision rather than a sentence from a
  source. ADR-0004 A8(b) governs `supports` links between assertions, so
  it does not apply; the evidence names the decision so a reader can
  tell the two kinds apart.

## 40. Applied 2026-10-22: F62's discovery papers join the list; each entry names its file and why (Sprint 11 Manual Validation, Q3 = 1)

Every count is a snapshot as of 2026-10-22. Written before the apply.

- **One list (team lead, Q3 = 1).** The 22 store records named in
  `D:\Data\Harold\EvidenceBasedDB\discovery\f62_hand_download_*.md` that
  are not yet on the list get one updated-reason segment that puts them
  on it, naming the discovery file. After that, the store alone decides
  who is on the list (section 39's rule), and the discovery files are no
  longer read. `scripts/sprint11_q3_f62_hand_download.py` (dry run,
  `--apply` with a verified backup first; a second apply writes nothing).
  Schuld 2018 is on both lists and gets no second segment; 2 entries are
  not in the store and stay in the discovery files only.
- **Correction to the Manual Validation message.** It said many of the 22
  are `hsbc-2026` papers. In the store they are filed under `ml` (21) and
  `qc` (1); 18 came from the fraud discovery stream.
- **Each entry now shows (team lead, 2026-10-22: "include the best
  practice naming suggestion for each of the papers and why we think the
  paper is important. The list details need to be reproducible easily at
  any time"):**
  - the target path: `Papers\<YYYY-MM>_<First-author>_<Title-words>.pdf`
    (section 3's convention, as F62 built it: the first 8 title words), or
    `Books\Book - <Title> - <Publisher> <Year>.pdf` for a book;
  - why it matters, computed from the store: the task that selected it,
    its relevance group, its contexts, and its citation count.
- **Priority order, revised.** (1) Named for a question the team lead set
  (Te Sun 1994, the F78 ceiling question). (2) Fraud: the `hsbc-2026`
  context or F62's fraud stream, since fraud detection is the active
  consumer's domain. (3) `qml` or `qc`. (4) Everything else (`ml`,
  tensor, `world`). Within a group, by citation count, highest first:
  the count F57's ranking recorded, or the count in F62's disposition.
  Both are OpenAlex counts at the date of selection.
- **Shown on request** by the `hand-download-list` skill
  (`.claude/skills/hand-download-list/`), which runs
  `python scripts/hand_download_list.py` and shows its output as is.

## 41. Rule from 2026-10-23: the quote-mark and figure checks are in `require_verbatim`, and the backup refuses a script that breaks section 31 (Sprint 11 retrospective I1a and I1b)

Extends sections 26 and 31. Every count is a snapshot as of 2026-10-23.
Written before the apply below.

- **One quote check for every script (I1a).** In Sprint 11 two checks
  lived only in `scripts/sprint11_reading.py`'s `verify()`, so F91, F92
  and F93 never ran them. `store.quotes.require_verbatim` now also
  refuses:
  - a quote mark outside every parsed quote and its anchor
    (`stray_quote_marks`). The quote pattern needs `; ` between quotes
    and ` (anchor)` after each, and a quote it cannot parse is never
    checked. A quote mark inside a quote, or inside its anchor, is
    fine;
  - given `value=`, a figure in the value that its own quotes do not
    hold (`unquoted_figures`, moved from the reading script). A digit
    in a word, closing a hyphenated name (Dirac-3, LimiX-2), or in
    "Phase N" is a name; `read_from_page` lists figures read from the
    page image, as in section 31.
  `Verified` now carries the value, and the verified write helpers refuse
  one whose value is not the record's. So a check run without `value=`
  cannot license a write.
- **The scan runs before the write (I1b).** Section 31's static rule
  moved from `tests/test_verified_writes.py` to `store/write_path.py`.
  `store.backup.backup_before_write`, which every `--apply` calls first,
  runs it on each script in `scripts/` on the call stack and refuses
  before the backup and the write. The 18 legacy scripts stay exempt. The
  test still scans every script at the desk.
- **What the new check found in the store: 2 of 1,595 assertions.**
  - `qci-email-dirac3s-much-better-results-no-comparison-named` (F92,
    Sprint 11): `;"On which problem class?"` had no space after the
    semicolon, so that quote was never checked. It is verbatim in the
    email (question 12). `scripts/sprint11_f92_qci_answers.py` now has
    the space; `--apply` syncs the stored quote (dry run first, verified
    backup). A second apply writes nothing.
  - `cyc-2007-eight-tactic-types` (Sprint 7): the quote stops at its
    inner `"split" (`, so the rest of it was never checked. Its script
    is a legacy script and is not re-run here. Proposed for the Sprint 12
    plan, as a correction with its own section.
  - 10 more contexts hold quote marks inside a quote or an anchor, which
    is not stray.
- **Every Sprint 11 script passes the new checks.** The reading script
  (F 125, G 649), F91 (6), F92 (18, after the fix above) and F93 (4).
  F92's and F93's values name "Phase 2", which the reading script's
  check never met; that is why the "Phase N" rule exists.

## 42. Applied 2026-10-23: HTML entities out of stored citations, and the Cyc quote made whole (Sprint 12 Task A, F101)

Every count is a snapshot as of 2026-10-23. Written before the apply.

- **The entities came from the metadata providers.** Crossref and DataCite
  return titles and venues with HTML escapes in them ("Science &amp;
  Technology Libraries"), and `store.citations` copied them as they came.
  A scan of every text field of every table finds one entity, "&amp;", in
  4 records: the title (`value`) and citation (`provenance`) of
  `jeffery-2024-multidimensional-quantum-walks-recursion-quantum` (DataCite)
  and `dunjko-2018-machine-learning-amp-artificial-intelligence`
  (Crossref), and the citation of
  `pande-2020-bibliometric-survey-quantum-machine-learning` and
  `yang-2023-survey-important-issues-quantum-computing` (Crossref venues).
- **The generator is fixed first** (workflow invariant 7's corollary):
  `parse_crossref` and `parse_datacite` unescape the title, subtitle and
  venue, so a later intake or re-check renders "&". (The first commit,
  5466953, missed DataCite's venue, every author name and Crossref's
  publisher; the fresh-eyes review found it, and they are unescaped too
  now.) Then the 4 records
  are corrected: each field unescaped, and nothing else changed. Record
  ids are keys and are not renamed: the Dunjko id keeps its "amp". Each
  record's updated reason names this section.
- **A guard.** A `live_store` test fails on any HTML entity in any text
  field of the store.
- **The Cyc quote** (`cyc-2007-eight-tactic-types`, Sprint 7, section 41).
  Its first quote held the source's own quoted word, `"split" (`, which
  ends a quote in the quote pattern, so the words after it were never
  checked. It is now quoted in two parts around that word: `"There are
  eight tactic types which describes the kind of operation to be
  performed, such as" (p.147; ...)`, whose anchor says why it is in two
  parts, and `"(i.e. split a conjunction into two sub-problems)."
  (p.147)`. The p.148 quote ("... only handles five.") is kept as it was.
  A further quote, `"2007, American Association for Artificial
  Intelligence" (p.146, the copyright line; ...)`, holds the value's
  year, which the figure check of section 41 now requires. (The first
  apply anchored it p.147; the copyright line is on printed page 146, the
  PDF's first page. The third apply below corrects it.) The value is not
  changed. The quotes are checked by `require_verbatim` with the value
  and named as the edit's basis (`require_edit_basis`). Applied first, with
  the entities.
- **Three more quotes the pattern never parsed (found after that apply,
  written before the second).** Run over the whole store, section 41's
  stray-quote check names 3 more assertions, not the 2 section 41 counted:
  their quotes carry no anchor, so the pattern found no quote in them at
  all, and section 41's count looked only at contexts with at least one
  parsed quote. `cyc-general-prover-disabled` and
  `heuristics-over-general-reasoning` (Sprint 1, Lenat and Marcus 2023)
  and `hsbc-b1-variable-count` (Sprint 2, the consumer repository's
  preregistration, amendment A30, read only; read by `git show` at that
  file's last commit, 7261e4e, from the third apply on, as section 43
  reads Phase 2). Each is re-quoted from its
  source with an anchor, and the figures each value states (2023; 20,
  1989 and 1,100) are given quotes that hold them. The values are not
  changed. The second Lenat quote's dashes are in the layout text layer
  (`pdftotext -layout`), which the check reads alongside the plain one.
- **Lenat and Marcus 2023 had no local copy.** Its free arXiv PDF
  (arXiv:2308.04445) is saved to `Papers\` under section 3's convention,
  by one paced request (`--fetch`), and added to the record's `access`.
- **A third apply, after the fresh-eyes review of 5466953 (written before
  it).** The review found what the stray-quote check cannot see: 7
  contexts with no quote marks at all, so no check had ever read them
  (Sprint 5 Task I: `auprc-not-generally-superior-under-imbalance`,
  `oversampling-helps-weak-not-strong-boosters`,
  `qelm-local-dynamics-match-haar-classically-simulable`,
  `qksvm-classical-kernels-better-on-uci-tabular`,
  `resampling-degrades-calibration-recalibration-repairs`,
  `rff-not-generic-dequantizer-but-matches-some-pqcs`,
  `wilcoxon-n5-floor-is-not-parity`). The "every stored quote parses"
  claim above was a count this check could not produce. Now:
  - **The guard** also fails on a non-empty context with no parsed quote.
  - **Each of the 7 is re-quoted** from its PDF with anchors (PDF page
    indexes, the printed page where there is one), every figure in its
    value quoted, and the old sentence kept as a passage. Three papers had
    no local copy (De Lorenzis 2026, Kakavand 2026, Sweke 2025); their
    free arXiv PDFs are saved by the same paced `--fetch` and added to
    `access`.
  - **Four values are corrected** where re-quoting showed them to say
    more or less than the source, each with its passages as the edit's
    basis: Elor 2022 (the SVM exception is that its threshold could not
    be tuned); De Lorenzis 2026 (6 to 10 qubits for MNIST and
    Fashion-MNIST, 6 to 11 for CIFAR-10; the authors "suggest", with
    larger studies needed); Kakavand 2026 (datasets from UCI and OpenML;
    "8 of 9" is balanced accuracy, with none of the 29 five-fold
    comparisons significant); Liu 2026 (oversampling's effect is
    "small-to-moderate", not slight). Certainty is not changed.
  - **Every local copy carries its SHA-256** in `evidence` (F48's test
    found Lenat's missing after the first apply), including the three new
    copies.
  - **The anchor and pin corrections** noted above: the Cyc copyright
    line is p.146, and the preregistration is read at 7261e4e.
  - `store.citations` now also unescapes DataCite's venue, every author
    name and Crossref's publisher.
- **A fourth apply, after the fresh-eyes review of 6d2bed4 (written
  before it).**
  - **The Elor correction was itself wrong for MLP.** MLP's threshold
    was tuned: Table 3 (p.5) gives it F1 0.303 with the tuned threshold,
    against 0.411 with SMOTE. Only SVM's could not be tuned. The value
    now says balancing did better for both, quoting the "MLP & SVM"
    paragraph (p.4).
  - **Two values unchanged in the third apply carry a dropped qualifier
    or a weaker word than the paper's own summary**: McDermott 2024 (the
    two metrics differ "with respect to model-dependent parameters" only
    in how they weight false positives; prevalence also enters AUPRC)
    and Liu 2026 (back to "slightly", which the abstract's "real but
    small" supports, now with the ECE figures). The third apply's
    "small-to-moderate" was the paper's effect-size label, not its
    reading.
  - **One anchor named the wrong section**: De Lorenzis's qubit counts
    are in section 3, not 4.
  - **The record history now says what each sync changed.** The third
    apply logged every change as "quote made whole"; each corrected
    record gets a note naming the correction (the p.146 anchor, the
    7261e4e pin, each value and why).
  - **Two paper records' evidence text** still carried what the
    assertions' corrections fixed (Kakavand: "9 UCI"; De Lorenzis: one
    qubit range), and three ended ".;" where the hash note joined.
    Corrected. The new test then found a fourth, Sweke 2025, also from
    this script's first apply; corrected in a fifth apply. 13 more paper
    records carry the same ".;" join, written by F48 and F97 (as of
    2026-10-23); punctuation only, outside F101, and raised at the
    retrospective rather than changed here.
  - **A gap the guard still has**, not closed here: a context with one
    parsed quote and unquoted text beside it (for example
    `cvqboost-vs-xgboost-auc-under-balancing`) passes. 2 contexts as of
    2026-10-23, both describing a table's rows or a byline in the
    coordinator's words, with their figures outside any quote:
    `cvqboost-vs-xgboost-auc-under-balancing` and
    `favorable-dirac3-papers-are-qci-authored`. Raised at the
    retrospective: whether such a description may stand beside quotes,
    or must become quotes of the table cells.
- `scripts/sprint12_f101_corrections.py`: dry run by default; `--apply`
  takes a verified backup first; a second apply writes nothing.

## 43. Applied 2026-10-23: Phase 2's Sprint 28 results, by the inbound path (Sprint 12 Task C, F102)

Every count is a snapshot as of 2026-10-23. Written before the apply.

- **What is read.** Six result documents in `hsbc-qfraud-phase2`'s
  `docs/phase2/`, each read whole at Phase 2 commit 10086da (branch
  `feature/20261019_Sprint_28`; its PR #46 is still a draft), with the
  last commit that touched each: F151 (e9946f5), F152 (0b5ea6c), F153
  (cfff1fe), F110 (7f5b3c0), F114 (74ce420), F154 (79fbe19). Read only
  (F79), through `git show`, so a later edit in Phase 2 cannot change
  what is checked. F111 (Experiment 4) has no result at 10086da and is
  not entered.
- **One reference record per document**, as F93 entered F108: `tier`
  `read`, the citation hand-transcribed from the heading and first line
  and named so, `access` the working-copy path and the commit URL,
  `evidence` the SHA-256 of the committed blob.
- **Assertions: 9, every one `SIM`** (Phase 2's own tag on each
  document): F151's cause and the restated F130 reading (2), F152's
  ordering (1), F153's failed falsifier and the two resolution checks
  (2), F110's build slope and solve (2), F114's miss (1), F154's null
  (1). Certainty as F93's: the consumer project's own measurement, read
  directly, starts HIGH, and each value carries Phase 2's own limits;
  Phase 2's inferences are attributed as inferences.
- **Contexts.** `ml` for a result about a classical method on a public
  data set or a simulator (F151's cause, F152, F114); `hsbc-2026` for a
  result about the project's own CVQBoost and device lanes (F151's F130
  restatement, F153, F110, F154).
- **No relation is linked (ADR-0004 A8 (b)).** F114's calibrated plug-in
  overstates the Bayes error as F108's default plug-in did, but by 3% to
  13% with a different model and fitting set, so it confirms only part
  of `f108-hgb-plugin-overstates-bayes-error-5-to-12-percent`; its value
  names that record instead. F151's restatement of F130 has no stored
  claim to contradict: F130's "beats HGB" was never entered.
- `scripts/sprint12_f102_phase2_sprint28.py`: every quote checked by
  `require_verbatim`, with the value, against the blob at 10086da (markdown
  bold dropped first) before anything is written; dry run by default;
  `--apply` takes a verified backup; a second apply writes nothing.
- **A second apply, after the fresh-eyes review of 5bcafe0 (written
  before it).**
  - **F111 has a result at 10086da; the line above saying it has none is
    wrong.** `docs/phase2/F111_LOKE_PROTOCOL.md` ("Experiment 4 (F111):
    the CVQBoost-KNN lane, the result") was committed at bf7b589, an
    ancestor of 10086da. The error came from Phase 2's own
    `docs/sprints/SPRINT_28_VALIDATION.md`, which at 10086da still says
    "No result yet" for F111; the result document is the later word. It
    is entered now as a seventh reference record with 3 SIM assertions
    under `hsbc-2026`: the lane under Loke et al.'s protocol is 0.051
    below the published 0.8108 (Phase 2 does not claim the published
    value is wrong); the stable HGB beats the lane under both protocols;
    the protocol moves HGB but not measurably the lane. The first bears
    on `cvqboost-knn-aucpr-0-8108-kaggle-fraud`; not linked (ADR-0004
    A8 (b)), since Phase 2 says it cannot tell why.
  - **Five values carried less than their source said**, each corrected
    with its passages as the edit's basis: F110's 2 s comparison (the
    ideal-parallel bounds, about 20 s and about 2 s, and "not stated in
    what we hold"); F153's resolution figures (the 2.9% to 6.2% is the
    guide's pairwise check; F104's gate fails separately); F153's
    falsifier (at ridge weight 0.002; the device quote of 77 to 251 s
    was computed but not carried forward as ready; "the limit is the
    formulation" is Phase 2's reading); F154's null (its power limit and
    the tie-inflated catch counts); F114's miss (worse than F108's
    plug-in on the other two arms, and the run cannot separate the two
    changes). F151's "10 or 11 iterations" moves out of the inferred
    part: it was measured.
  - The store test now checks certainty and context, and the quote count
    must stay at the number written.

## 44. Applied 2026-10-23: the Classiq Quantum Circuit Challenge pages and the named repository (Sprint 12 Task E, F103)

Every count is a snapshot as of 2026-10-23. Written before the apply.

- **Papers with no record**: 0 at planning; on 2026-10-23 the only PDF
  no record names is Part 2's write-up, saved by this task. Section 42's
  three arXiv copies are named by their records.
- **Three web source records under `qc`, entered as Sprint 11 entered
  the NVIDIA blog**: a hand citation from each page's own title, author
  and date, `tier` `read`, the saved copy in `References\` (Part 2's
  19-page PDF in `Papers\` as its second copy; its QASM file and
  notebook bundle named in `evidence`, not copied). PoJen Wang's Part 1
  ("A field guide to quantum circuit compilers") and Part 2 ("A depth-95
  phase oracle for the Classiq logo"), both 2026-10-08, and Alex
  Gramolin's "Wrapping up the Classiq Quantum Circuit Challenge"
  (Classiq, 2026-10-06).
- **The series is stated, not linked (a change from the plan).** The
  plan said Part 1 and Part 2 are "linked as a series". No link type
  fits: `cites` is computed from Crossref reference lists only (ADR-0005
  A10, and a test recomputes every `cites` link from that cache), and
  `version-of`, `superseded-by` and `responds-to` say something else.
  Each record's citation says "Part 1 of 2" or "Part 2 of 2" and its
  disposition names the other record.
- **Assertions: 5, each quoting only its own author's measurements**:
  Part 1's run of three compilers on the baseline (MODERATE); Part 2's
  depth 95 with 272 CNOTs (HIGH: the organiser scored the same circuit
  and gives the same numbers) and where the reduction came from
  (MODERATE); Classiq's rules and participation counts (MODERATE, the
  organiser's own account) and its placings (HIGH, the organiser's to
  decide). Part 1's survey of other work is not entered as its claims.
  Both placings are kept: the blog says "top five" (written before the
  ranking), Classiq says first. Evidence tag `N/A`: a circuit's counted
  depth, not a hardware or simulator run.
- **The repository the team lead named**,
  `wangy8205165/Quantum-NeuralNetwork-WhitePaper`, as a GitHub
  repository record (one REST call), linked to no paper: no source names
  it as a paper's code.
- `scripts/sprint12_f103_intake.py`: `--fetch` saves the pages (never
  overwriting); every quote is checked by `require_verbatim` against the
  saved page before anything is written; dry run by default; `--apply`
  takes a verified backup; a second apply writes nothing.
- **A second apply, the same day: applicability.** The first apply
  entered the three pages at `read` with no applicability, which every
  screened or read paper must carry (`test_paper_applicability`). The
  full suite run before the commit found it; the targeted run did not,
  since a store write changes no file a test names. Each record now
  carries one `qc` entry with its rationale.
- **A third apply, the same day: the fresh-eyes review of c80c195.**
  Written before the apply. The review found the values above wrong in
  four places, and they are corrected here, not edited above:
  - **Grades follow the store's precedent.** An author's own
    measurement in a blog post, one study, starts LOW (Part 1's run and
    the redesign, both MODERATE above). Part 2's depth 95 with 272 CNOTs
    is MODERATE, not HIGH: LOW for the author's own claim, upgraded one
    level because the organiser scored it independently. The placings
    stay HIGH (the organiser's to decide). The organiser's CX counts for
    the top two are split into their own assertion, MODERATE.
  - **PyZX did not shorten the circuit.** Part 1's value listed it with
    the tools that did; the page says it lengthened the circuit, to
    depth 8950 with 8576 CNOTs, more than twice the baseline's CNOTs.
    "56 times shorter" is now measured against the baseline, as the page
    measures it. Part 1's run is "six versions of the circuit", not
    three.
  - **"Top five" was not written before the ranking.** The section
    above said so; the Part 2 page is dated 2026-10-08, after the
    organiser's 2026-10-06 wrap-up, and its PDF is dated 2026-10-01. The
    depth-95 value now gives the placing as the organiser's and names
    the placings record.
  - **The repository holds no code.** Its files (GitHub contents API,
    2026-10-23) are the LaTeX source and PDF of a white paper, "Quantum
    Neural Networks: Theory, Architectures, and Applications". Its
    disposition says so and keeps it at `seen` as a paper candidate.
  - The script now syncs a held record's disposition, not only inserts
    it; the test compares each disposition and citation with the store
    and checks the repository record and its access.
- **A fourth apply, the same day: the fresh-eyes review of 77beaa0.**
  Written before the apply. Two statements in the third-apply bullet
  above are wrong, and are corrected here, not edited there:
  - **The order of the pages cannot be decided from them.** The bullet
    says Part 2 (2026-10-08) came "after the organiser's 2026-10-06
    wrap-up". The saved Classiq page carries two dates, "Date 06 Oct
    2026" and "Date 9 October 2026", and its metadata gives
    `datePublished` 2026-10-09. The 2026-10-01 date of Part 2's PDF is
    its file metadata (CreationDate), not its text, and the PDF never
    says "top five". So whether Part 2 was written before the wrap-up is
    open. No store change: the depth-95 value already gives the placing
    as the organiser's.
  - **The PyZX error was in Part 2's assertion, not Part 1's.** The old
    `wang-2026-depth-95-came-from-redesign-not-compilers` put PyZX's
    depth 8950 and 8576 CNOTs inside "shortened ... by about 6 percent";
    Part 1's old value already said full_reduce "raised the CNOTs to
    8576". And Part 1's old disposition already said six compiler
    versions; the third apply reworded it to three tools and six
    versions of the circuit, which is no change in count.
  - **Values.** Part 1's value now says the one-qubit merging explains
    the T-count drop "of the first rows of his chart", as the page says,
    and names the two runs that lowered depth as the page does (Qiskit
    at level 3, and tket followed by Qiskit).
  - **The top-two counts stay MODERATE, with the reason stated.** Part
    2's depth 95 was upgraded because the organiser, the judge, scored it
    independently of the entrant. The organiser's counts are not
    upgraded on the entrant's agreement: the entrant is an interested
    party, and the published circuit was not re-run here.
  - **Not changed, with why.** The rules assertion keeps the organiser's
    setup and its participation counts together at MODERATE (the
    cautious grade of the two). The id prefix `classiq-2026-` stays:
    renaming an id the export already carries costs more than the
    inconsistency. The repository record's third-apply reason says
    "against the saved page" where its source was a GitHub file listing;
    that reason is history and stays, and this bullet records the
    correction. `sync_disposition` syncs only the disposition; the test
    compares citation and evidence, but not `transcribed_from`
    (carried to the retrospective).

## 45. Rule from 2026-10-23: a reading script grades HIGH only with a named basis (Sprint 11 retrospective I3, Sprint 12 Task G)

Extends sections 26, 31 and 41.

- **The gap.** Until Sprint 12 each reading script kept its own set of
  assertion ids the coordinator had judged HIGH, with no reason per id.
  A later reader could not tell why one empirical-looking value was HIGH
  and its neighbor LOW.
- **The helper.** `store/grading.py`: `high_grades` takes each HIGH with
  its basis and why, and refuses a basis that is not one of the five a
  paper itself settles: its own setup, its own scope, a definition, a
  result it proves, or a limit it states. `grade` returns HIGH with that
  basis in the certainty reasons, or the script's other grade, and
  refuses "high" as the other grade, so HIGH has one door.
- **The rule.** `store/write_path.py`: a script whose name contains
  "reading" and that writes assertions must call `high_grades` and must
  hold no literal "high" of its own. `backup_before_write` refuses it
  before the backup, as section 41's rule does. Sprint 10's and earlier
  reading scripts are already legacy; `sprint11_reading.py` is exempt
  from this rule only (it has run). An intake script that is not a
  reading script (F102, F103) keeps its literal grades, each with its
  own reasons.

## 46. Applied 2026-10-23: Roadmap-to-QML's first release (Sprint 12 Task F, F104, F98's first release)

Every count is a snapshot as of 2026-10-23. Written before the apply.

- **The list, at one commit.** Christophe Pere's Roadmap-to-QML
  (`github.com/Christophe-pere/Roadmap-to-QML`), read at commit
  `a239747648` (the head at planning, pushed 2026-10-20). Its 13
  markdown files (the year files, `Workforce.md`, `Reviews/Reviews.md`,
  the README) are saved under
  `References\Roadmap-to-QML_a239747648\`, outside git; the manifest
  records each file's SHA-256.
- **1,418 arXiv ids listed; 21 new.** Every arXiv id the files link is
  matched to the store by the ids its records' `access`, `evidence` and
  provenance hold. The 21 new ones enter through the door
  (`scripts/intake.py`) at `seen` under `qml`, each naming the file that
  lists it in `found_via` and `disposition`. Reading them is Task G's
  machinery, through the shared ledger (section 47).
- **One malformed link.** The 2021 file links Asfaw et al. 2021 as
  `2108.0131`; an id from 2015 on has five digits after the dot. The
  store already holds `2108.01311`, so nothing is entered for it; the
  manifest lists it under `malformed_links`.
- **Free copies: 20 of 21**, fetched by the one paced fetcher (18 s
  apart), each named with its SHA-256 in `evidence`. arXiv 2303.16318
  (Mahroo et al.) returned HTTP 404 for its PDF; the record enters at
  `seen` with no local copy and goes to the ledger's `no_copy`. Three
  copies carry no arXiv stamp on page 1 (2407.21062, 2609.23476,
  2609.24381); each first page was checked by hand and its title
  matches the arXiv metadata.
- **27 other links carried to the next F98 release, 9 with a DOI.**
  Links that are not arXiv are matched by the DOI in the URL where it has
  one; those the store does not hold, and those with no DOI, are listed
  in the manifest's `carried_to_next_release`. This release was sized to
  the arXiv ids at planning.
- `scripts/sprint12_f104_roadmap.py`: `--fetch` saves the list's files
  and the PDFs (arXiv and DataCite answers cached beside the list's
  copy, so the dry run and the apply send no arXiv request); dry run by
  default, which writes `manifests/sprint12_f104_roadmap.json`;
  `--apply` takes a verified backup; a second apply enters nothing and
  leaves the manifest as the first apply wrote it.
- **A second apply, the same day: the fresh-eyes review of f99139e.**
  Written before the apply.
  - **The match is recorded on the held papers.** The first apply named
    the list only on the 21 papers it entered. The 1,397 held papers the
    list links now get a `found_via` route naming the list and the file,
    as the earlier list release did (`scripts/qmlpapers_manifest.py`,
    `add_routes`), each with an appended updated reason.
  - **Matching.** An arXiv id in the DOI form `10.48550/arXiv.NNNN.NNNNN`
    now counts as held (none in the store on 2026-10-23, so nothing
    changes). A DOI counts as held only as a whole DOI, not as a
    substring of the joined text. A legacy Nature article id
    (`npjqi201523`) is no longer turned into a wrong DOI; an RSC article's
    DOI is read from its URL. **25 links are carried, not 27**: the RSC
    review by Sajjan et al. was listed twice and is held.
  - **No copy, and why.** arXiv 2303.16318 is withdrawn on arXiv (its
    abstract page, 2026-10-23), so it has no PDF. It enters the ledger's
    `no_copy` when Task G builds the ledger (section 47).
  - **1,418 against 1,402.** The F104 card counted the year files and
    `Workforce.md` (1,402 ids, recounted from the saved copy on
    2026-10-23); this release also reads `Reviews/Reviews.md` and the
    README, which add 16.
  - The manifest is rewritten by each run, keeping what an earlier apply
    entered and routed; the tests check every listed id is held and its
    records carry the route, and that the second apply still read the
    list.

## 47. Applied 2026-10-23: the F57 release for Sprint 12, read under the grading rule (Sprint 12 Task G, F105)

Every count is a snapshot as of its own date. Written before the slice
runs; each later step adds its bullet before it runs.

- **The slice: 400 records.** F57's order (team lead, 2026-10-21):
  `hsbc-2026`, then the Dirac platforms, then `qml`. Nothing is unread
  under the earlier contexts (0 on 2026-10-23), so the release is the 400
  most-cited `qml` records at `seen` or `screened` with no read row,
  counted by OpenAlex exactly as F89 and F96 counted them.
  `scripts/sprint12_f105_slice.py` writes
  `manifests/sprint12_f105_slice.json`. Left out: Task F's 21 records
  (they come on top of the 400, plan Q1 = 1), and the 17 records of the
  earlier slices (F89, F96) still unread, which had no free copy. 1,205
  candidates on 2026-10-23.
- **Free copies.** `scripts/sprint12_f105_downloads.py` runs Sprint 10's
  rules (`scripts/sprint10_f89_downloads.py`) on this slice: arXiv
  through the one paced fetcher (18 s apart), else the open-access PDF
  OpenAlex lists; a paywalled paper is listed, never fetched; an
  existing file is never overwritten. F52's cap (240 arXiv requests a
  session) counts per process, so `--session-count` starts the count at
  the requests Task F already sent; at the cap the run stops, and a run
  after the pause fetches what is still missing.
- **The read ledger.** `manifests/sprint12_read_ledger.json`
  (`scripts/sprint12_read_ledger.py`): Sprint 11's rule, one record, one
  group, one first-pass reader, at most 5 readers at once. New:
  `read_by_coordinator` holds Task E's three pages (section 44), read in
  full before the ledger existed, so no group can take them again. Task
  F's 20 records with a copy and the slice's records with a copy go into
  groups; a record with no copy goes to `no_copy` with its reason.
- **Readers.** `manifests/sprint12_reads/READER_PROMPT.md`, Sprint 11's
  prompt with one rule added: a "high" suggestion names its basis
  (section 45). The coordinator decides every grade.
- **What the slice and the fetch found (2026-10-23).** OpenAlex counted
  815 of the 1,205 candidates; the 400 run from 14 citations down to 1
  (the most-cited `qml` records were read by earlier releases). 389 of
  the 400 already had a local copy (most in the QMLPapers folder); 6 were
  planned from arXiv and 4 saved, each with its page-1 stamp; 2 are
  withdrawn on arXiv (2308.08167, 2409.10932, their abstract pages read
  the same day, as was 2303.16318's); 5 have no free copy known to
  OpenAlex. The ledger: 53 groups, 413 records (Task F's 20 in g01 to
  g03, the slice's 393 in g04 to g53), 8 in `no_copy` with their
  reasons, Task E's 3 read by the coordinator.
- **The reads, and the coordinator's read (2026-10-23).** Written before
  the apply. All 53 groups read, one Sonnet 5.5 first-pass reader each,
  at most five at once, from local copies only; each group's checker
  printed "0 missing". The coordinator read every value against its
  quoted passages group by group and recorded the read in
  `scripts/sprint12_reading.py`: 110 values replaced (each says only
  what its quotes say: a result, a theorem or figure number, a device,
  a dataset name or a reader's inference cut, or the passage added);
  18 assertions given the source sentence beside the reader's quote
  (most stopped at a curly quote, an apostrophe or a dash the text
  layer prints oddly); 2 quotes corrected; 7 assertions dropped, each
  with its reason (among them a bound whose square root the text layer
  lost, so the value would store a wrong complexity).
- **Grades, under section 45.** HIGH for 577 ids, each with its basis
  and where the paper settles it (Task F 34, Task G 543). Kept LOW
  against a reader's "high": a measured result, even a negative one;
  a statement about the field or the literature rather than the paper
  itself; a label that is not a limit. A future-work sentence that
  names something the paper did not do is a stated limit. One vendor
  product description MODERATE. Every other assertion LOW.
- **What the apply enters (dry run, 2026-10-23).** Task F: 74
  assertions from 20 records (34 HIGH, 40 LOW); 1 record with no copy
  (2303.16318, withdrawn). Task G: 1,283 assertions from 393 records
  (543 HIGH, 1 MODERATE, 739 LOW; qml 744, qc 464, ml 55, world 16,
  method 4); 9 records read that bear on no context (read rows and the
  reason, tier unchanged); 7 with no copy (2 withdrawn, not for the
  hand-download list; 5 with no free copy, on it). Before the apply the
  store held 465 `read`, 2 `screened`, 1,867 `seen`; 1,613 assertions.
- **The apply.** `python scripts/sprint12_reading.py --task F --apply`,
  then `--task G --apply`, each after a verified backup, through the
  verified write path (sections 31 and 41); a second apply of each
  writes nothing new. `tests/test_sprint12_reading.py` checks the store
  against the script.
- **Applied (2026-10-23).** 74 and 1,283 assertions entered, as the dry
  run said; 404 records to `read` (20 and 384). The second apply of each
  took its backup and wrote nothing. The store after: 869 `read`, 2
  `screened`, 1,463 `seen`; 2,970 assertions.
- **F57's count after this release (2026-10-23).** 1,465 records at
  `seen` or `screened`, of which 1,449 have no read row. 9 of the 393
  records read bore on no context, well under premise (g)'s half: the
  ranking held. Two tests assumed the pre-read store and were corrected:
  F104's entered papers may now be `read` when a ledger group read them,
  and the field round-trip test no longer adds a route its first `read`
  paper already holds.
- **A third apply, the same day: the fresh-eyes review of 5744e2d.**
  Written before the apply. Every count matched; the findings were
  about meaning, which no check can see. Each was read against its
  source before it was acted on.
  - **Cuts that lost a condition (1 Critical, 3 Important).** A
    replacement that cuts what a quote does not hold can cut too much:
    `yang-simulator-limit` said the paper ran only on a simulator, but
    the paper ran its examples on real hardware and simulated one
    subsection's analysis for machine time; `aqnn-coherence-entanglement-no-help`
    lost that its no-go rests on GIOs; Definition 1 of
    `gilfuster-trainability-definition` lost "with high probability";
    `gilfuster-bp-trainable` lost its cryptographic assumption. Each is
    restored with the source sentence that holds it. The rule, sharper:
    when the value says more than its quote, quote the rest of the
    sentence before cutting the value.
  - **18 HIGH grades moved to LOW.** 14 "stated limits" that are
    statements about the field, its devices or its literature, not the
    paper's own work; 4 that are conclusions from the paper's own
    measurements. "We do not claim X" is a stated limit; "we found X" is
    a result. A field statement now stores its own reason (a new FIELD
    reason, 21 ids with the 7 the coordinator had kept LOW), not "an
    empirical result".
  - **Values trimmed or re-quoted (11).** A cited result taken out of a
    HIGH limit's quotes; a Hamiltonian class narrowed to what the source
    names, its lost Pauli letters said so; a lost superscript said so;
    "restricted" applied to the class the source applies it to; words
    the quotes do not hold ("cycle graph", "penalty parameter",
    "standard", a dataset name, "good") cut or quoted.
  - **Kept as it was, and why.** `gnn-ae-preliminary-future` stays HIGH:
    after section 47's first cut its value is the future-work sentence
    alone. The proved results that are LOW because their text was cut
    short still store "an empirical result" as the reason (3 ids); the
    reason is wrong in name only, and is carried to the retrospective.
  - **The tables after the review.** 118 values replaced, 27 assertions
    given source sentences, 3 quotes dropped (the first bullet's "2
    quotes corrected" were 2 dropped; and of its 18 extra quotes, 6 were
    text-layer stops and 12 added a missing subject or referent), 7
    dropped assertions, 559 HIGH (Task F 34, Task G 525; Task G LOW 757).
  - **A new guard for CI.** `unsupported_by_basis` checked replaced
    values only inside `verify()`, which needs the source text, so CI
    never ran it. A test now runs it on every replaced value from the
    quotes alone.

## 48. Applied 2026-10-25: the ".;" joins, and the LOW reasons of theoretical results (Sprint 13 Task A, F107)

Every count is a snapshot as of its own date. Written before the apply.

- **The joins.** A script that appended "; Local copy ..." to evidence
  text already ending in a full stop left ".;". Sprint 12 Task A
  corrected the papers its own apply touched; on 2026-10-25 the store
  holds 16 more in `paper_fields.evidence`, every one before "Local
  copy". `scripts/sprint13_f107_joins.py` drops the full stop and keeps
  the separator, as Sprint 12 did; its dry run printed each of the 16 in
  context and all are sentence ends. Two ".;" elsewhere are the source's
  own text and stay: a `paper_reads` detail quoting an arXiv title that
  ends "...", and a `paper_probes` affiliation list after "Quantum
  Computing Inc.".
- **The LOW reasons: 5, not 3.** Sprint 12's section 47 counted 3
  theoretical results kept LOW that stored "an empirical result"; it
  named no ids. The reading script's own notes name 5 LOW grades whose
  cause is not a measurement, and all 5 store that reason:
  `larson-convergence-proved` (the statement cut short in the text layer,
  no theorem read), `swaptest-qnn-two-layer-equivalent` (Proposition 6
  holds only up to an error the value does not carry),
  `ld-daqc-unit-overlap-epsilon` (an unnumbered derivation the paper calls
  idealized), `tree-unitarity-tradeoff-butterfly-velocity` (a fragment of
  the paper's statement) and `qcc-bounds-bures-entanglement-distance`
  (the authors' interpretation of their Theorems 1 and 2). Each now
  stores "a theoretical result (proof, derivation or proposition) not
  checked in full by the reader" with its cause; every grade stays LOW.
  The correction is a table in `scripts/sprint12_reading.py`
  (`THEORY_LOW`), applied through its own path, so its live test, which
  compares the store with the script, keeps holding. Other LOW grades
  with a wrong reason type, if any, are not found by this: the coordinator
  named only these. F57's I2 (Sprint 13 Task F) makes every new LOW name
  its reason.
- **The guard.** A `live_store` test fails on a ".;" join in
  `paper_fields.evidence`.

## 49. Applied 2026-10-25: every LOW names its reason; Sprint 12's theoretical results corrected (Sprint 13 Task F, F112, I2)

Every count is a snapshot as of its own date. Written before the apply.

- **Section 48's premise was wrong.** It said the 5 were all the coordinator
  named and others "are not found by this". The fresh-eyes review of
  6c6f0ac found 8 more by reading, so the class is wider: a reader's kind
  "shown" took "an empirical result" by default, whether the paper
  measured the result or proved it.
- **The rule (Sprint 12 retrospective I2).** `store/grading.py` names
  every LOW reason (`low_grade`: measured result, theoretical result,
  field statement, authors' claim, cited claim). The texts are the ones
  the store already holds, so a script moved onto it writes nothing new. A
  theoretical result must say why it was not upgraded. `store/write_path.py`
  refuses a reading script that writes assertions without `low_grade` or
  with a "Started LOW" text of its own. `theory_words` is a guard, not a
  grader: a reading script's test requires every "measured result" whose
  value or quotes name a theorem, a proof, a derivation or an analytic
  count to be named by the coordinator, either as a theoretical result or
  in `MEASURED_DESPITE` with why.
- **Sprint 12, corrected.** On 2026-10-25 the store holds 604 Sprint 12
  LOW assertions stored as "an empirical result". A Sonnet 5.5 classifier
  read each one's value and quotes and proposed 33 as theoretical or
  mixed; the review named 8 (7 of them among the 33). The coordinator read
  every candidate's quotes and took 29: their reasons become "a
  theoretical result (proof, derivation or proposition)" with a cause that
  says only what the quotes show (for example "a bound from Theorem 11,
  not checked by the coordinator"). Five stay as measured: four whose
  value joins analysis with numerics (`tomesh-decomposition-on-scaling`,
  `iaconis-log-scaling`, `msqw-outperforms-qaoa-evidence`,
  `qnn-gp-wide-deep`) and `krylov-limiting-distribution`, whose quote does
  not show how the relationship was established. Every grade stays LOW.
  The classifier called 63 more "other" (the quotes do not show the
  method); some may be theoretical in the paper, and are not checked here.
- **Task A's 5, reworded.** Their reasons said "not checked in full by the
  reader", which did not fit 3 of them (the review): the prefix now names
  only the kind, and each cause carries the specific. The history note a
  sync writes is now `THEORY_NOTE`, naming this correction, so no later
  sync is dated as Task A's. `tree-unitarity-tradeoff-butterfly-velocity`
  keeps fidelity "exact": fidelity is the quote's, which is verbatim; its
  reason says the value is a fragment of the statement.
- **Before Sprint 12: counted, not corrected.** The same classifier read
  the 499 LOW assertions from Sprints 9 to 11 stored as "an empirical
  result" and proposed 13 as theoretical and 14 as mixed. They are not
  corrected here: their reading scripts have run and stay as they are
  (`store/write_path.py` LEGACY and GRADING_LEGACY), and the coordinator
  has not checked them. Carded on F57 for a later release.
- **A second apply, after the fresh-eyes review of dd620c7 (written
  before it).** The review read the PDFs; the coordinator checked each
  claim in the text layer before acting.
  - **4 more theoretical results**, each confirmed in its PDF:
    `apr-marking-equals-absorbing` ("we make the proof for general
    graphs"), `qkm-scalable-features` (Theorems 1 to 3),
    `hintons-layers-as-unitaries` (Theorem 6.2) and
    `krylov-limiting-distribution` (Section III). Keeping the last as
    measured, above, was wrong on the paper: its quote alone hid the
    method.
  - **2 moved back**: `mohseni-resource-estimate-chemistry` rests on
    simulation and benchmarking (a measured result again), and
    `pqc-gradient-cost-linear` is a textbook's statement about the field.
    Each sync writes its own dated note, not Sprint 12's.
  - **The guard was weak.** `theory_words` found 15 of the 34; it now
    reads "we show", "prove", "analytic", "theoretical", "bound" (as a
    whole word, not "boundary"), "scales as", "closed-form", a bare
    "complexity" and Omega, and finds 27 of the 36. The other 9 state a
    count or a speed-up with no such word: the guard catches the words,
    and the coordinator's read catches the rest. It flags 30 more stored
    measured results, each read and named in `MEASURED_DESPITE` with why.
  - **The write-path rule was easy to bypass**: `"Started " + "LOW"` and
    a bare `("low", reason)` passed. A literal `"low"` is now refused as a
    literal `"high"` is; the vendor LOW goes through `low_grade("vendor
    claim")`; an aliased import of `low_grade` counts.
  - **Corrected 2026-10-25 (the fresh-eyes review of cec6020).** The
    bullet above says more than the rule does. The concatenation case
    was caught by the literal `"low"` beside it, not by the concatenation:
    `"LO" + "W"` or `"LOW".lower()` with no quoted `"low"` still passes.
    And the rule had got weaker: matching the bare name `low_grade` let
    the import line alone pass. It now requires a call, of `low_grade` or
    of the name it is imported as (proven by injection). A reading script
    that compares a literal `"low"`, as a count would, is refused: a known
    false positive, recorded in `store/write_path.py`.
  - **A count corrected**: of the 499 rows from Sprints 9 to 11, one
    (`kimmeyh-headline-null-cvqboost-trails`) does not hold the exact
    text, so 498 store it exactly. The classifier's 13 and 14 stand.

## 50. Applied 2026-10-25: Phase 2's later Sprint 28 work, F162 and three corrected values (Sprint 13 Task E, F108)

Every count is a snapshot as of 2026-10-25. Written before the apply.

- **What is read, and at which commit.** The plan named 9993ab6. By the
  task's start Phase 2 had merged PR #46, whose head is 9cbe5ba, now the
  local HEAD; no file under `docs/phase2/` changed between the two, so
  the read is at 9cbe5ba. Read only (F79): `git show` and the GitHub API,
  no fetch. Changed since F102's read at 10086da: F110, F111, F114, F151,
  F153, F154, `PHASE2_POC_PLAN.md`, and F162 (new).
- **F162 entered**: one reference record and 2 SIM assertions, HIGH, the
  project's own measurement: the proxy is not reliably above HGB or
  XGBoost inside the SPECTRA pocket on any of three cells, and is
  reliably below XGBoost on two; FourierWall2's single-run in-pocket wins
  do not repeat over ten seeds. **Context `hsbc-2026`, not the plan's
  `ml`**: section 43's rule files a result about the project's own
  CVQBoost lanes under `hsbc-2026`; of the B4 device claims on the same
  cells, `cvqboost-device-below-classical-bar-spectra-b4` is under
  `hsbc-2026` and the other two under `platform:dirac-3` (this line first
  said all three were under both; corrected after the fresh-eyes review
  of 88bd065).
- **No relation linked (ADR-0004 A8 (b)).** F162 measures the proxy, not
  the device, so it confirms none of the three B4 claims whole, and its
  FourierWall2 finding is about a different model and bar from
  `fourier-wall-incomplete-bar-manufactures-advantage`. Each reason names
  the claims it bears on.
- **Three F102 values corrected**, each against its document at 9cbe5ba:
  - `f110-proxy-solve-flat-paper-2s-not-like-for-like`: the 91-variable
    solve could not be read because a separately timed J build was
    subtracted and 9 of 20 solves clamp, not because of the timer's
    resolution (Phase 2's own correction, 2026-10-23).
  - `f114-calibrated-plugin-misses-known-ceiling`: calibration moved no
    estimate on the main arm only; on the other two arms it moves some;
    the overestimate is 3% to 13% calibrated and 4% to 14% uncalibrated.
  - `f111-cvqboost-knn-lane-below-published-value-under-loke-protocol`:
    the range's top is 0.828, not 0.829.
  Each paper gets a second read row for the re-read.
- **Confirmed by name, unchanged**: the other 9 F102 values. F111's run
  time (now 82.5 minutes of recorded lane time) and its "not dominated by
  an exact match" reason (now unverified) were never stored; F151's dose
  wording and range-threshold note, F153's ridge-rule reading and F154's
  closest-cell configuration change no stored value.
- `scripts/sprint13_f108_phase2.py` holds F162 and the corrections; the
  Sprint 12 script stays the record of the read at 10086da, and its store
  test takes the three corrected ids from the Sprint 13 script.
- **A second apply, after the fresh-eyes review of 88bd065 (written
  before it).**
  - **The three paper records pointed at the old blob.** Their `access`,
    `evidence` and `checked_against_source` named 10086da, whose text says
    0.829, while the corrected values quote 9cbe5ba. Each is repointed at
    9cbe5ba, with the earlier read and its blob SHA-256 kept in the
    evidence. Every stored quote from these three documents is verbatim
    at 9cbe5ba (the review ran the check on all of them).
  - **F162's first value left out four qualifiers**, now carried: the
    energy_steel HGB case (an interval excluding zero, but p = 0.0098
    above the family level, so the rule reads no reliable difference),
    the 46 to 58 frauds per seed, Phase 2's inference that a telecom-only
    entry would decide telecom_churn, and the label limit. "Overall" now
    says it means the whole test set.

## 51. The F57 release for Sprint 13: every readable `qml` record (Sprint 13 Task F, F112)

Every count is a snapshot as of 2026-10-25. Written before the apply;
the read's own bullets follow before its apply.

- **The slice** (`scripts/sprint13_f112_slice.py`, written to
  `manifests/sprint13_f112_slice.json`): plan Q1 = 1, all 806 `qml`
  records at `seen` or `screened` with no read row whose access names an
  arXiv id or a DOI, nothing being unread under `hsbc-2026` or the Dirac
  platforms. The 24 records of the three earlier slices with no free copy
  are left out. Not candidates, and NOT read this sprint (the fresh-eyes
  review of e621771): 166 GitHub repositories and 11 records whose access
  names only a local file that exists; both are carded on F57. OpenAlex
  counted 417 (364 by the record's own identifier: 362 arXiv DOIs and 2
  journal DOIs; 53 by the journal version of an arXiv record), every one
  at 0 or 1 citations:
  Sprint 12 took the slice down to 1. The other 389 are not counted and
  come last, by id; the release reads them too, so a stop cuts the
  uncounted first and then the least cited.
- **The fetch** (`scripts/sprint13_f112_downloads.py`, Sprint 10's rules):
  33 arXiv PDFs (the plan said 32), serial at 18 s through the paced
  fetcher; 6 papers have no free copy OpenAlex knows (two closed, four
  Zenodo records), and go to the ledger's `no_copy` with that reason.
  The fetch saved 28; arXiv returned 404 for 5 (one of them
  mahroo-2023, the paper section 46 found withdrawn). One saved file had
  no arXiv stamp (farrelly-2019); its first page, read by the
  coordinator 2026-10-25, carries the record's title and authors.
- **The ledger** (`scripts/sprint13_read_ledger.py`, written to
  `manifests/sprint13_read_ledger.json`, Sprint 11's rules): 795 records
  in 100 groups of at most 8 (g01 to g100), and 11 in `no_copy`, each with
  its own reason read from the fetch log (the 5 fetch failures, the 6 with
  no free copy) instead of Sprint 11's one reason for all.
  `tests/test_sprint13_read_ledger.py` fails if a record is held twice
  or a no-copy reason is that one reason.
- **The reader prompt** (`manifests/sprint13_reads/READER_PROMPT.md`):
  Sprint 12's, with one new field, `result_type` (measured, theoretical,
  field, claim, cited, vendor, setup), the reader's suggestion of the LOW
  reason section 49 requires. The coordinator decides it.
- **Half 1, the read (g01 to g50, 400 records; written before its
  apply).** Sonnet 5.5 readers, at most 5 at once, each one group, each
  writing its file outside the tree; the coordinator copied each file into
  `manifests/sprint13_reads/` when it reviewed it. The dry run of
  2026-10-25: 1360 assertions from 400 records (10 with none), 542 HIGH
  and 818 LOW, contexts 934 `qml`, 346 `qc`, 57 `ml` and 23 `world`;
  every quote verbatim in its source, every figure in its own quotes.
  - **The coordinator's tables**, each entry read against its quotes:
    155 values trimmed to what their quotes say (`VALUE_REPLACE`), 29
    quote edits and 32 added quotes on named passages, 11 contexts fixed
    (a reader wrote "method" or "setup", which are not contexts), 46
    statements about the field, 128 theoretical results kept LOW with
    their cause (a theorem is HIGH only when its statement and its
    conditions are quoted) and 40 measured results whose words name a
    proof or a bound, each with why it is measured.
  - **What a read covered.** 236 records are marked `partial` with the
    sections read; 164 `full`. 113 of the 164 also list a few sections
    (abstract, introduction, results, conclusion), so the script enters
    those as "the parts the reader lists" instead of "the whole source":
    the reader's list, not its mark, is what the record says was read.
    24 files are another version or title of the record's paper, named
    in the read's `version_note`.
  - **One id renamed.** g03 and g42 both returned `review-scope`. The
    script refuses a duplicate id at run time, but a duplicate key in a
    coordinator table is silently the last one, so g42's file copy names
    it `singh-qml-review-scope`. `tests/test_sprint13_reading.py` now
    fails on a table key held twice and on a listed read entered as the
    whole source (both proven by injection, 2026-10-25).
  - **Kept out of values.** Figures the text layer garbled (an exponent
    lost, as in "217" for 2 to the 17th) and paper inconsistencies a
    reader flagged stay in the reader's inference, not in a value.
- **Corrections after the fresh-eyes review of cec6020** (snapshot
  2026-10-25; written before the apply that makes them). The review
  checked the counts above and found them right, and found the store
  matching the script. It found the grading applied unevenly, and two
  claims above false:
  - **26 of half 1's 542 HIGH are now LOW** (516 HIGH, 844 LOW):
    - 18 theorems whose quotes are the abstract's "we prove" or a
      paraphrase, not the statement with its conditions, now in
      `THEORY_LOW` with the cause, like siblings in the same papers
      already were (g30 Ma, g37 Pirnay, g29, g01, g05 and others).
    - 8 "stated limits" that are the paper's own measured results ("Q-NAS
      can achieve a higher accuracy", "did not improve robustness"); a
      measured result, even a negative one, stays LOW.
  - **7 stated limits keep HIGH without their measured clause**: the
    clause's quote is dropped and the value trimmed (for example
    `mcquack-stated-limitations` no longer carries "does not outperform
    simple classical baselines").
  - **Retracted: "Kept out of values."** 12 values carried an exponent the
    text layer printed flat ("O(n2.455)" for n to the 2.455, "10−13" for
    10 to the −13), and two (`patel-qbm-convergence-proof`,
    `fonseca-vqe-complexity`) were the coordinator's own replacements. The figure check cannot see this: the
    garble is the same in the quote and the value. Each now says the
    figure in words or says the exponent is lost, and
    `test_no_value_carries_a_figure_the_text_layer_garbled` fails on the
    pattern. g38 Roga's "2k" and "2(n + 2k) + 6" are not garbled: the
    paper's program register has 2k qubits for k training points.
  - **5 HIGH values said more than their quotes** (`single-shot-definition`,
    `exact-learning-definition-threshold`, `gross-memory-limit-large-n`,
    `open-problem-limit`, `stationary-noise-breaks-exchangeability`); each
    now has the passage it rests on, or is trimmed.
  - **Retracted: "113 of the 164 also list a few sections."** At least 7
    of the 113 say the whole paper was read ("Whole paper", "Read the full
    paper (7 pages)", "Abstract through conclusion"). `read_detail` now
    enters those as the whole source.
  - **Retracted: "`tests/test_sprint13_reading.py` now fails on...".** The
    tests were written and proven, but the file was not committed with
    cec6020: it partitions the whole slice, so it waits for half 2. It
    lands with half 2.
  - The same rules, applied to half 2's g51 to g69 before its apply, take
    2 more stated limits out of HIGH (`qcd-gym-insufficient-performance`,
    `arceci-limits`) and trim 5.
- **The hand-download list's order changed with half 1** (cec6020): the
  389 uncounted records (no OpenAlex count at selection) sort after every
  counted one in their group, not among the zeros, and a slice's
  uncounted row no longer hides another slice's count.
- **Corrections after the fresh-eyes review of f782e53** (snapshot
  2026-10-25; written before the apply that makes them). The review found
  the first correction pass still uneven, and the coordinator checked
  each case in the text layer before acting:
  - **14 more of half 1's HIGH are LOW** (now 502 HIGH, 858 LOW):
    - 8 theorems whose quotes are only the abstract's or introduction's
      "we prove", "we show" or "we find": `pbtmax-breaks-classical-threshold`,
      `damped-oscillator-bqp-hard`, `vqa-constrained-loss-global-minimum`,
      `classical-verification-sparse`, `not-random-generatable`,
      `kcm-succinctness-incomparable`, `kcm-fidelity-intractable`,
      `robust-training-query-cost`. The rule is now applied the same way
      everywhere: a theorem's own statement, formal or informal, quoted
      with its conditions is HIGH; an abstract's sentence about it is not.
      By that rule `coyle-density-qnn-gradient-overhead` (Corollary 1),
      `shah-quantum-kmeanspp-guarantee` (Theorem 1, checked in the text),
      `qgp-no-gp-gaussian-pauli`, `graph-stabilizer-code-bijection` and
      `shadow-advantage-theorem` keep HIGH.
    - 5 "stated limits" that are measured results: `qenn-stated-limitations`,
      `radar-cost-limit`, `hyperparameter-sensitivity`,
      `quso-qaoa-not-near-optimal`, `vdd-struggles-tfim-disordered`.
    - `qaoa-hybrid-definition`, a definition that lecture notes cite: HIGH
      is never given to a cited claim. The review did not find it; the
      test that bars it did, the first time the held test file ran.
  - **4 half 1 limits keep HIGH without their measured clause**
    (`qpinn-limits-transfer-generality`, `variational-symmetry-and-depth-limits`,
    `preliminary-evidence-limit`, `singh-pokhrel-preliminary`): the
    clause's quote is dropped or cut to the limit, and the value trimmed.
  - **Values.** `open-problem-limit` no longer says "unknown ... matrix";
    `hamiltonian-paths-4n-minus-6` no longer names a proof by induction;
    four flat-printed exponents are said in words (`mm-vqe-ising-speedup`
    N squared, `lejarza-clustering` N cubed to N squared log N,
    `galvis-gpq-classical-baseline` M cubed, `fonseca-vqe-complexity` k
    times N cubed and N to the 7th), with "printed flat in the text
    layer"; "the exponent is lost" is kept only where the flat print has
    more than one reading (`tqnn-kjunta-query-complexity`'s "n22k").
  - **The garbled-figure guard's pattern** flagged "(H2)" and "(B0)", a
    molecule and a field; a lower-case letter and digit now count only
    inside O(...). "R2" and "D2-sampling" are left on purpose: each is
    the field's usual flat spelling of a name (R squared, D squared
    sampling), not a figure. Proven red again by injection, 2026-10-25.
  - **Corrected: "At least 7 of the 113"** above: 8 say the whole paper
    was read.
  - **`store/write_path.py` has two more known bypasses**, recorded in its
    comment and not closed: `low_grade(` inside a string or a docstring
    counts as a call, and so does a call to a `low_grade` the script
    defines for itself.
  - **Half 2's g51 to g69, by the same rules**: 7 more out of HIGH
    (`caro-classical-verification-parity` to `THEORY_LOW`; the measured
    `galvis-variance-distant`, `galvis-time-parameter-sensitivity`,
    `cimini-limits-quantumness-simulability`, `qopf-hardware-limits`,
    `chaudhary-mode-collapse`; and `photonic-classifier-limit-below-10-photons`,
    whose limit is its measured drop, so it keeps both quotes as a
    measured result); 3 trimmed (`quantumgep-quantum-chemistry-limit`,
    `qite-classically-simulable`, `altgraph-mse-limit`); 3 values fixed
    (`oliveira-setup-simulator-two-devices` gains its simulator,
    `qcdge-calculation-levels` loses an orphan quote,
    `halder-rbm-ansatz-accuracy` names what "the accuracy" is).
  - **The LOW test was wrong for vendors.** A vendor's result starts
    MODERATE and is downgraded one level through `low_grade("vendor
    claim")`, so its reason does not start "Started LOW". The test now
    holds each vendor LOW to that text and every other LOW to "Started
    LOW" (proven red by injection, 2026-10-25).
- **Half 2, the read (g51 to g100, 395 records; written before its
  apply).** The same readers and the same rules as half 1, with the
  corrections above applied throughout. The dry run of 2026-10-25: 1350
  assertions from 395 records (2 with none: `beggs-2023` and
  `yusupov-2023` study quantum graphs in mathematics, with no computing
  or learning workload), 462 HIGH and 888 LOW, contexts 958 `qml`, 340
  `qc`, 37 `ml` and 15 `world`; every quote verbatim in its source, every
  figure in its own quotes, no value carrying a flat-printed figure.
  - **The coordinator's tables, half 2's share**: 127 values trimmed, 26
    quote edits, 11 added quotes, 9 contexts fixed (a reader wrote
    "method" or "setup"), 57 statements about the field, 132 theoretical
    results kept LOW with their cause, 51 measured results whose words
    name a proof or a bound, each with why.
  - **What a read covered.** 315 records are `partial` with the sections
    read; 80 `full`. 46 files are another version or title of the
    record's paper, named in the read's `version_note`.
  - **One id renamed.** g65 and g82 both returned
    `noiseless-simulation-only`; g82's file copy names it
    `nagano-noiseless-simulation-only`, as g42's was renamed in half 1.
  - **One assertion not entered.** `qwiener-advantage-open` (g56): its
    quotes do not hold the open question its value states (`DROP`).
  - **Reader-flagged figures and conflicts** (g88 Renaud's lost figures,
    g90 Sanavio's and Schetakis's, g91 Shaydulin's and Shang's, g94
    Tibaldi's inconsistency, g95 and g96 Wang's conflicts, g98 Yang's,
    g100 Ziiatdinov's) stay in the reader's inference; where one reached
    a value, the value is trimmed or the figure said in words.
- **Corrections after the fresh-eyes review of ce2412e** (snapshot as of
  2026-10-25; written before half 2's re-apply). Half 1 is unchanged.
  - **Two claims in the bullet above were false.** "No value carrying a
    flat-printed figure": `qaoa-qmf-best-empirical-scaling` (g91) said
    "grows as 1.46N", which is 1.46 to the power N; and g91 Shaydulin's
    figure had reached that value without being said in words. It now
    is, and the garble guard gains a branch for a decimal before N or n
    (proven red by injection).
  - **Out of HIGH:** `nghiem-exponential-copies-in-r` (a limit drawn
    from Theorem 2, whose statement is not quoted) and
    `dqnn-results-general-scope` (the generality of results whose own
    entries are LOW) go to the theoretical LOWs;
    `qnpg-outer-loop` (its "limitation" is the literature's) is a LOW
    authors' claim. **Into HIGH:** `scala-lazy-regime-limit`, filed as a
    field statement, is the paper's own stated limit on its own formal
    results. Half 2 is now 460 HIGH and 890 LOW.
  - **Cited or derived clauses left out of a HIGH:** a cited clause in
    `bounds-scope-query-count-only` ("[80]") and
    `schuld-speedup-caveat` ("[1, 9]"); the "almost all" clause of
    `connectivity-1d-chain-no-overhead`, which rests on a cited lower
    bound; the abstract's "we show" in `jeffery-subspace-graph`, a
    definition.
  - **A value that said the opposite of its quote:**
    `qucnn-no-network-trained` quoted "providing immediate computational
    advantage" without the negation the source prints just before it.
    The quote now carries it.
  - **Values that said more than their quotes:**
    `khoo-simulation-scope`, `facial-quantum-walk-model-scope`,
    `nagano-noiseless-simulation-only`, `nghiem-exponential-copies-in-r`
    and `qnpg-outer-loop` trimmed or given the passage; `wolf-field-state`
    had dropped the paper's "or" alternative, now restored.
  - **Locations:** 12 HIGH locations named no place in the paper, or the
    wrong one (`grb-dataset-setup` and `grb-simulation-limit` named
    Section V.C; the quotes are in VI). Each now names its section, read
    in the source.
  - **Half 2's share of the tables, corrected:** 134 values trimmed, 31
    quote edits, 15 added quotes, 9 contexts fixed, 56 statements about
    the field, 134 theoretical results kept LOW, 51 measured results.
  - **Guards.** Two checks in the HIGH test could not fail (the reason
    text is built from the basis; a vendor claim is graded before HIGH is
    consulted) and are removed. New: no id in HIGH and in THEORY_LOW or
    MEASURED_DESPITE (`certainty()` would let HIGH win silently); the
    store holds no Sprint 13 assertion the script no longer makes. Each
    proven red by an in-memory injection named in its docstring.
  - **write_path:** a third bypass recorded, not closed: comments are
    stripped with `#.*` before the LOW checks, so a `#` inside a string
    hides the rest of its line.
- **Corrections after the fresh-eyes review of 6cfc137** (snapshot as of
  2026-10-25; written before half 2's re-apply). Grades unchanged at 460
  HIGH and 890 LOW.
  - **The bullet above was wrong twice.** `qnpg-outer-loop` was not a
    LOW authors' claim: its kind made it "an empirical result". It
    explains a limitation the literature suggests, so it is now a
    statement about the field, with that passage quoted. And "6 values
    trimmed" in the CHANGELOG was 5 trimmed and 1 restored (`wolf`).
  - **`nghiem-exponential-copies-in-r`** said the state's symbol was
    lost in the text layer; it is not ("copies of ρ required"), and the
    quote now carries it.
  - **Reader anchors corrected in the stored provenance (new table
    `ANCHOR_FIX`):** a HIGH location corrected alone left the record
    naming the reader's wrong section beside it. `qneuron-simulation-only`
    (III.B), `slack-free-setup` (IV), `qumode-benchmark-setup` (IV.A and
    the Abstract), `stvqc-device-setup` (the Introduction: only its
    sentence has the quoted comma) and `ma-not-tested-on-hardware` (III).
    HIGH locations: `kqse-bound-not-tight` is p.3, after Theorem 2;
    `zhang-quantum-troenpy-not-developed` spans pp.13-14.
  - **Values:** `scala-lazy-regime-limit` says "most of the formal
    results", the paper's own, not "most formal results";
    `schuld-speedup-caveat` no longer uses "speedup" as its own word (the
    source puts it in quotation marks).
  - **Half 2's share of the tables, corrected again:** 135 values, 31
    quote edits, 15 added quotes, 9 contexts, 57 statements about the
    field, 134 theoretical LOWs, 51 measured results; 5 anchors.
- **Corrections after the fresh-eyes review of 7ea56e7** (2026-10-25;
  written before half 2's re-apply). Grades unchanged.
  - **One anchor "corrected" wrongly.** The reader's "Section III and
    Section IV" for `ma-not-tested-on-hardware` was right; 6cfc137 gave
    it the HIGH location "Section III, Results (Cases I and II)" and
    7ea56e7 wrote the same into `ANCHOR_FIX` (its bullet above says
    "(III)"). In
    reading order its first quote follows IV. CONCLUSION and its second
    is in III.A (Case I). Anchor and HIGH location now say so.
  - **`qnpg-outer-loop`** keeps the source's "likely".
  - **The CHANGELOG's "3 HIGH locations made exact"** was 4: kqse and
    zhang above, and qumode and stvqc, listed above with the anchors.

## 52. Applied 2026-10-25: the common name after a source's spelling (Sprint 13 Manual Validation Q4)

Team lead, 2026-10-25: "keep how the paper does them and then put in
parenthasses the more common name for them so that we can query the
database and still find all occurances of R2, R squared". Written before
the apply that makes it (snapshot as of 2026-10-25).

- **The rule.** `store.common_names.with_common_names` adds the common
  name in parentheses after a source's own spelling: "R2 (R squared)",
  "D2-sampling (D squared sampling)". `store.ingest` applies it to every
  value it inserts or syncs, so every reading script, past and future,
  gets it with nothing of its own, and a second apply writes nothing.
  Quotes are never touched; they stay verbatim.
- **The 18 values.** 17 carry "R2" (15 LOW; `tn-state-r2-threshold` and
  `shah-dequantized-qi-kmeanspp` HIGH) and 1 "D2-sampling" (the same
  shah value). They belong to four scripts: `sprint9_f78_ceiling_reading.py`
  (1), `sprint11_reading.py` (3), `sprint12_reading.py` (2) and
  `sprint13_reading.py` (12). Each script is re-applied, first against a
  copy of the store to show that these values are the only change.
- **Left as is.** `otgonbaatar-cp-decomposition-hsi` spells "R-squared",
  already the common name in words.

## 53. Sprint 13 Task G (F113): every paper read in full, with no budget

Team lead, 2026-10-25, at Manual Validation: "fully read all the papers
that are not marked 'read' and update all conclusions. That includes this
sprints 551 adn 109 and any from prior runs ... remove the budget ... It
is far more important to read them all, get all the conclusions, profs,
assertions... than some budget". Written before any read is applied
(snapshot as of 2026-10-25).

- **The slice** (`scripts/sprint13_g_slice.py`,
  `manifests/sprint13_g_slice.json`): every paper record not read in
  full. A read is full only when a `paper_reads` row says `full`, or a
  first-pass reader marked the paper `full` and listed no parts (or said
  the whole paper was read). A reader's `full` that listed sections is
  not full: 161 such in Sprints 11 and 12 and 121 in Sprint 13, many
  stored as "the whole source". Of 2,335 papers, 1,991 are not read in
  full:
  - 1,309 at `read` with a local copy; 1 at `read` with only a DOI
    (`emami-2026`); 1 at `read` that is a GitHub repository;
  - 160 at `seen` or `screened` with a local copy, 347 with only an
    arXiv id or a DOI, 173 GitHub repositories.
- **The downloads** (`scripts/sprint13_g_downloads.py`, Sprint 10's
  rules): the dry run planned 210 free copies (164 from arXiv, serial at
  18 s inside F52's cap, and 46 open-access PDFs OpenAlex lists) and
  found no free copy for 138. A paywalled paper is listed, never
  fetched; those go to the hand-download list with their reason.
- **The ledger** (`scripts/sprint13_g_ledger.py`,
  `manifests/sprint13_g_ledger.json`): one record, one group, one reader,
  at most 5 readers at once; groups of 5 papers. First the records whose
  stored assertions hold a theoretical result kept LOW for want of its
  statement, then the records not yet at `read`, then the rest. Each
  group's brief carries the record's stored assertions for its reader to
  judge; the briefs are store content and stay outside git.
- **The reader prompt** (`manifests/sprint13_g_reads/READER_PROMPT.md`):
  every page, every appendix and proof; no cap on assertions; a verdict
  on every stored assertion (confirmed, corrected, narrowed, widened,
  contradicted, not in the paper); each theorem with its statement and
  conditions quoted. `scripts/sprint13_g_check.py` is the reader's own
  check (the write path's quote and figure checks, and the shape).
- **GitHub repositories (174)** are not papers with a text layer; how
  they are read is the team lead's decision, asked at the end of the
  task.
- **Corrections after the fresh-eyes review of a3b8074** (2026-10-25;
  written before any Task G read is applied):
  - **The slice is 1,997, not 1,991.** A whole-paper note with an
    exception ("Whole paper read except related-work equations") and
    three e-mail reads marked `full` whose older thread was "not read"
    no longer count as full. F113's card had counts from an earlier run
    (1,141 and 682); it now matches the slice.
  - **The reader's check** now refuses a `full` read that names a part
    not read, a changed verdict with no value, a paper bearing on no
    context with no reason, a HIGH suggestion with no location or on a
    measured result, and a file that is not the brief's.
  - **The ledger only appends.** A re-run keeps every group a reader
    already holds and writes briefs only for new groups; the downloads'
    saved copies are found through their log (they carry author and
    title, not the record id). 66 fetched records and the 6 above joined
    as groups g295 to g309.
- **After the downloads finished** (2026-10-25; written before any Task
  G read is applied; counts are a snapshot as of that date):
  - **The run saved 165 copies and failed 45** (HTTP 403 or 404, two TLS
    failures, and publisher pages that were not a PDF). No failure was
    retried or fetched around. With the 138 that have no free copy, 183
    fetch-bucket records have no local copy. They are listed with their
    reason in `manifests/sprint13_g_no_copy.json`, and Task G's apply
    marks each for the hand-download list.
  - **The slice was re-run with the download log**: of 1,997 not read
    in full, 1,315 are at `read` with a local copy, 325 are at `seen` or
    `screened` with a local copy, 183 have no local copy (1 of them at
    `read`), and 174 are GitHub repositories.
  - **The ledger appended 99 records as groups g310 to g329**, which
    makes 329 groups and 1,640 records, every one with a local copy.
  - **The reader prompt was clarified** after groups g001 to g005 ran:
    a plot or drawing whose caption and surrounding text were read is not
    `not_read`, and a text layer that holds the paper twice is read from
    its first copy. The coordinator grades the earlier groups'
    figure-only gaps as `full` where every page of text was read.
- **Applied 2026-10-27: groups g001 to g042** (written before the apply;
  counts are a snapshot as of 2026-10-27). Team lead, 2026-10-26: "pause
  after the 5 current agents complete and backlog the remaining"; groups
  g043 to g329 are F114.
  - **What enters.** 210 records, read by a first-pass subagent (208
    whole, 2 with named exceptions: chatterjee-2024, table numbers lost
    in the text layer; perrier-2024, three scanned pages) and reviewed
    group by group by the coordinator
    (`manifests/sprint13_g_reviews/g001.json` to `g042.json`): 5,489
    assertions entered or changed, 1,987 HIGH and 3,502 LOW. Every quote
    is verbatim in its source, every edit rests on named passages, and
    every figure is in its quotes.
  - **Tried first on a copy of the store.** Records 8,017 to 13,070,
    assertions 5,682 to 10,735, HIGH assertions 2,125 to 4,059; 306 new
    `paper_reads` rows (a subagent row and a coordinator row for each of
    153 records) and 114 `update read` lines. A second apply wrote
    nothing. The 114 updates were not questioned before the real apply,
    and they were a defect (below).
  - **A store defect the trial found, fixed before the apply.**
    `store.ingest.sync_assertion` wrote a changed assertion one column
    at a time. The table's CHECK requires a search scope on every
    absence claim, so a stored claim moving to `absence` failed on the
    `claim_type` step before its `search_scope` was written. The sync now
    writes every changed column in one statement; a test in
    `tests/test_quotes_and_sync.py` was proven red by putting the old
    loop back.
  - **A second defect, found by the full suite after the apply and
    repaired 2026-10-28.** Task F (F112) read 57 of these papers on
    2026-10-25, which is also a Task G review day, under the same reader
    names. Task G's apply matched read rows by reader, day and extent
    only, took Task F's 114 rows (57 subagent, 57 coordinator) for its own
    and rewrote their detail. Both scripts now match a read row by their
    own wording (`is_mine` in `scripts/sprint13_g_reading.py`; the group
    marker in `scripts/sprint13_reading.py`), and a test in
    `tests/test_sprint13_g_apply.py` was proven red by making every row
    count as Task G's. The repair re-ran Task F's apply, which put its 114
    rows back with their original detail, then Task G's, which wrote no
    read row. Diffed against the pre-apply backup
    (`evidence-20261027T233851286095-...`), no `paper_reads` row is
    missing.
  - **How a read is recorded.** At the apply, as in Sprints 11 and 12, a
    subagent's read was a `paper_reads` row with extent `subagent`, its
    detail "first pass, the whole paper, every page and appendix (Sonnet
    5.5 reader, Sprint 13 Task G, F113, group gNNN)", or "first pass, the
    whole paper except: ..." for the 2 exceptions, beside the
    coordinator's `partial` row. F113's acceptance says `full`.
  - **Extent changed to `full`, 2026-10-28 (written before the apply).**
    Team lead, Manual Validation Q7 = 2: Task G's whole-paper reads are
    stored as `full`, the 2 reads with a named exception as `partial`;
    the reader's name ("Claude Sonnet 5.5 (first-pass subagent)") still
    says who read. Sprints 11 and 12 keep `subagent`. The apply moves the
    210 rows in place (`read_extent` and `write_reads` in
    `scripts/sprint13_g_reading.py`; a test proven red with the old
    extent), so no `subagent` row of Task G's is left beside its
    replacement. `scripts/sprint13_g_slice.py` counts a `full` row as a
    read in full only when its detail names no exception. 200 of the 208
    pass on the store alone. The other 8 (aaronson-2023, abbas-2023,
    ahmed-2025, akande-2025, albino-2023, boulebnane-2024, boy-2025,
    chan-2024) carry the reader's version note, which says the
    bibliography was "skimmed" or "skipped", so they leave a later slice
    only through their reader files (fresh-eyes review of 2bab87b).

## 54. Applied 2026-10-30: Brighindi's PHI-OMEGA paper, posts, images and code (Sprint 14 Task A, F119)

Every count is a snapshot as of 2026-10-30. Written before the apply.

- **Four source records, all under `ml`** (team lead, 2026-10-28: "the
  paper is ML-related as it is rlated to predictions/solvers"):
  - the paper, read in full: its text through the quote check's
    extractor, and its 3 pages viewed as images for the symbols the text
    layer keeps and Figure 1;
  - the LinkedIn posts and comment thread, read in full from the team
    lead's paste in `References\`, with the three images read by eye;
  - the author's repositories `phi-infinity-runtime` (4ee4ea3) and
    `m-omnia-validation` (d3e45f3), at `read` with a `partial` read row:
    only the files that bear on the paper's claims (Sprint 13 Manual
    Validation Q11 = 1).
- **The images are described, never quoted.** The quote check reads
  text, and an image has none (F116 does not exist yet). Each image is
  named with its SHA-256 in the posts record's evidence, with what it
  shows; the post's assertion says its image restates the post.
- **The Zenodo archive bears on none of the paper's claims.** Of its 610
  file entries (the reference said 608), none holds PHI-OMEGA, M-OMNIA,
  "dS = 0", arc-length, the seed 20260925, symplectic or Hamiltonian. It
  is named in the absence claim's search scope and not entered.
- **11 assertions, graded through `store.grading`.**
  - HIGH, each on its basis: the paper's definitions of its own axioms
    and gate (not that they hold); its stress test's setup; that it gives
    no proof for its closure claim (an absence claim, scoped to the whole
    paper, both repositories, the archive and a GitHub search); and the
    author's own repositories' stated limits.
  - LOW: the paper's central claim (failure "mathematically impossible"),
    its claim of full reproducibility, and both posts, each as the
    author's claim with no theorem, proof or data behind it; the
    Figure 1 result and the repository's counts as measured results from
    one seed, whose files are not published.
- **One `contradicts` link** (ADR-0004 A8 (b)): the repository's
  statement that the test is not reproducible from it and that no
  absolute immunity follows from one seed cannot hold beside the paper's
  claim that its logs ensure full reproducibility and prove immunity.
  Nothing else is linked: a claim made without proof does not contradict
  the absence of the proof.
- **The comment thread** is one reader's challenge (which systems does
  the closure preserve exactly, and is there a theorem); it is quoted in
  the post's assertion and named in the absence claim, not entered as a
  claim of its own.
- `scripts/sprint14_f119_reading.py`; a second apply writes nothing.

**Corrected 2026-10-30, after the fresh-eyes review of 1b987dd** (written
before the second apply). Four statements above were wrong or short:

- **The runtime read missed a file that bears on the claims.**
  `docs/M_OMNIA_STATO_RICERCA_2026-09-27.md`, which the README links,
  calls the closure "Ipotesi di formalizzazione" (a formalization
  hypothesis) and the 25 September result "Risultato nel simulatore
  definito; non dimostrazione fisica generale" (a result in the defined
  simulator, not a general physical proof). It is now read in full and
  yields a 12th assertion, HIGH as the repository's stated limit. The
  runtime's read row said "the rest bears on none of the paper's
  claims"; it now names the note and says the rest was not read. The
  absence claim's search scope names the note, and says the
  repositories' own Zenodo deposits were not searched.
- **"Nothing else is linked" was wrong.** The repository's "no absolute
  immunity is inferred from one seed" and the paper's abstract,
  "demonstrating absolute structural immunity", cannot both hold for the
  same test, so the stress-test limit is also linked `contradicts` to
  the central claim, and so is the new status-note assertion. The first
  link (to the reproducibility claim) stands on its immunity half: "not
  reproducible from this checkout" and "the logs ensure full
  reproducibility" can both hold, since the logs exist with the author.
  The absence claim is still not linked: a claim made without proof does
  not contradict the absence of the proof.
- **Two values held text no quote checked.** The Figure 1 assertion's
  "different metrics" (the repository's "sono metriche diverse") and the
  absence claim's thread quote are now quoted and checked against their
  own files. The stress-test limit adds "I rifiuti non equivalgono a una
  soluzione del compito" (the rejections are not a solution of the task).
- **Two descriptions above are corrected here.** Only the 25 September
  post's assertion says its image restates the post; the 23 September
  assertion does not name its image. The comment thread is a reader's
  challenge and the author's reply, which claims again, with no proof,
  that energy drift is "mathematically impossible".
- **Known and not changed:** the stored reason on a HIGH from a
  repository reads "the paper's own stated limit", because the template
  in `store/grading.py` says "paper" for every source; its "why" names
  the repository. The stress-test summary speaks of "l'autore" in the
  third person, so "the author's own repository" means the repository,
  not that Brighindi wrote every line.

**Corrected again 2026-10-30, after the fresh-eyes review of 6d5bcec**
(written before the third apply):

- **The status-note assertion's `contradicts` link is withdrawn.** It
  failed ADR-0004 A8 (b): "Risultato nel simulatore definito; non
  dimostrazione fisica generale" (a result in the defined simulator,
  not a general physical proof) can hold beside a claim of absolute
  immunity inside that simulator, and a closure the paper states as an
  axiom is already a hypothesis. The assertion keeps the limit in its
  value. One `contradicts` link to the central claim remains, from the
  stress-test limit, on "no absolute immunity is inferred from one
  seed" against "demonstrating absolute structural immunity". The
  value now says the note's row covers the 25 September manuscript on
  runtime invariance, the paper itself, not only its comparison.
- **The m-omnia read row now records its search.** It said "the rest
  bears on none of the paper's claims" with no search behind it. All 30
  tracked files at d3e45f3 were searched for PHI-OMEGA, the sum of dS,
  dS = 0, M_gate, the seed 20260925 and immunity, with no hits; the row
  says so. Each corrected read row's first text is kept in its record's
  updated_reason.
- **The read correction now has a test** that puts the first row back
  on a copy of the store and checks the apply corrects it.

## 55. The F95 release for Sprint 14: new papers in `Papers\` (Sprint 14 Task B, F122)

Every count is a snapshot as of 2026-10-30. Nothing is written to the
store: every unnamed file is already a store record.

- **Before** (2026-10-29, Sprint 14 Phase 1.2): 374 PDFs in `Papers\`
  and its subfolders; 166 named by no record's `access` (file-name match).
- **After** (2026-10-30, after Task A): 374 PDFs; 165 named by no
  record's `access`. Task A named the one new file, the PHI-OMEGA paper.
  No file was saved between the two counts.
- **The 165 are linked by the ledger, not by `access` now.** Each is
  Sprint 13 Task G's download of 2026-10-25 for a record already in the
  store: all 165 are in `manifests/sprint13_g_ledger.json`, in groups
  g295 to g329 (34 groups), each record at tier `seen`. Its `access`
  names the arXiv id or DOI. The g-reading apply adds the file to
  `access`, with its SHA-256, when its group is read (F114), the same
  as for every earlier group. This is the narrower reading of F95's
  step (2): the file is matched to its record and is not entered twice,
  but `access` is not written ahead of the read, so the hash and the
  read land together.
- **The hand-download list holds 53 records; none has a local copy.**
  No target path exists under `D:\Data\Harold\EvidenceBasedDB\`. A text
  match on `aimeur-2013` was a false hit: the line was aimeur-2007's
  reason, which names its 2013 journal version.
- Nothing to enter, nothing to read in this release beyond F119.

## 56. Applied 2026-10-30: Phase 2's Sprint 29 results, and one corrected F108 value (Sprint 14 Task D, F120)

Every count is a snapshot as of 2026-10-30. Written before the apply.

- **What is read, and at which commit.** Phase 2 commit 6242b8a, the
  head of PR #63 (merged 2026-10-30), current when the task started.
  The plan named the GitHub API, because local refs then stopped at
  22d16c3 and no `git fetch` is run in a sibling repository. By the
  task's start the team lead's own clone held 6242b8a, so the script
  reads with `git show`, as every earlier inbound script does; the API
  returns the same bytes (checked by SHA-256 on all 17 files). Read only
  (F79). Changed since F108's read at 9cbe5ba: `F108_CEILING_VALIDATION.md`
  and `F162_IN_POCKET.md` (F164's figure corrections), eight new F166
  documents under `docs/phase2/algorithms/`, `PHASE2_POC_PLAN_DRAFT.md`
  (new), `PREREGISTRATION_DRAFT.md`, and six new result files.
- **Two source records, each a set of documents.** A quote is checked
  against the set's joined text and names its document in its anchor
  (the F119 pattern for a source that spans files).
  - `hsbc-qfraud-phase2-f166-sprint29-ulb-algorithms`: the ULB
    comparison and the seven algorithm documents, all read in full.
  - `hsbc-qfraud-phase2-sprint29-results`: Phase 2's Sprint 29 Manual
    Validation record (V2, V4, V5, V7 and Decision D1) with the three
    preregistered entries those results ran under (F156, F158 and the
    F160 amendment). F156, F158, F159 and F160 have no page of their own
    under `docs/phase2/`. The validation record was corrected twice on
    Phase 2's review, so a live test checks its headline figures against
    the run files themselves.
- **Nine SIM assertions, HIGH**, the consumer project's own measurement,
  each carrying Phase 2's limits and attributing its inferences:
  - F166 (4): the seven tuned algorithms' ranking with the two reliable
    adjacent pairs; the proxy's train-test gap, the largest; the narrow
    spread of recall at the 0.5% alert budget; the classical tuning
    choices (no balanced class weights, HGB at l2 1.0 on every seed, the
    RBF SVM kept out).
  - F156: the Henze-Penrose bound fails on F108's simulator; F114 stays
    blocked.
  - F158 (2): the per-type cascade is below one model on the simulator;
    106 of 950 (seed, fraud) pairs on ULB are missed by every stored
    model family.
  - F160: Experiment 3's room check passes on IEEE-CIS.
  - F159: the parallel pool build equals the serial one and is faster.
  **Contexts by section 43's rule**: `ml` for the classical tuning
  choices, F156 and F158's simulator result; `hsbc-2026` for the rest,
  which are about the project's own CVQBoost lanes and Experiment 3.
- **F167, the PoC plan draft, states no result.** Read in full; nothing
  entered. Its figures point to result files entered here or earlier.
- **No relation linked (ADR-0004 A8 (b)).** Each reason names what it
  bears on: F166 against `f151-cvqboost-proxy-below-stable-hgb-on-ulb`
  (a different, tuned proxy below HGB by 0.0198, not reliably; both can
  hold); F156 against the F108 and F114 misses (another estimator, not
  the same claim); F160 against `f153-learner-selection-formulation-fails-
  its-falsifier` (ULB against IEEE-CIS; both hold); F159 against
  `f110-cvqboost-pool-build-grows-faster-than-rows`; F158 and F166's
  recall note against `f154-no-stored-model-better-on-a-ulb-subset`.
- **One stored value corrected**:
  `f108-hgb-plugin-overstates-bayes-error-5-to-12-percent` said "ratios
  1.053 to 1.118"; Phase 2 recomputed three of the five ratios from the
  rows (F164, 2026-10-26), and the top is now 1.119. The value, its
  quote and its reason change; its id, context and certainty do not. The
  Sprint 11 script stays the record of the read at eef3349, and its store
  test takes this value from the Sprint 14 script.
- **Confirmed by name, unchanged**: the other three F108 values and both
  F162 values; every quote of theirs is verbatim at 6242b8a. The noise
  arm's corrected range (1.076-1.097) and F162's wall time (now
  unverified) were never stored.
- **The F108 and F162 paper records are repointed at 6242b8a**, with the
  earlier read and its blob SHA-256 kept in the evidence, and each gets a
  second read row (the Sprint 13 pattern).
- `scripts/sprint14_f120_phase2.py`; `tests/test_sprint14_f120.py`.
- **A second apply, the same day: the fresh-eyes review of 1f904ba.**
  Written before the apply.
  - **The two new records failed the local-file check.** Their evidence
    named each document's hash with no "SHA-256" before it, so the check
    (`store/recheck.py`) compared the access path's document with a run
    file's hash and reported "local copy changed". The evidence now
    writes "SHA-256" before each hash, the access path's document first;
    the apply rewrites the two records' evidence. A live test runs the
    check on all four paper records this script writes.
  - **The corrected F108 value contradicted itself.** F164 corrected the
    Results ratios but left the BLUF's "0.5-1.8 points past the 10%
    margin". The value now attributes that range to Phase 2's summary.
    The reasons give the range from the corrected ratios, computed here
    from `f108_ceiling.json` and marked as not stated by Phase 2: 0.57,
    1.91 and 1.56 points (about 0.6-1.9).
  - **Wording against the sources.** F166's ranking now says the proxy
    uses its own top-k features (k 17) and the classical lanes all 30
    columns. F158's cascade value carries "so the gain may be small" and
    that its models (HGB, l2 1.0) see more than F108's three features.
    F159's value says the dead-worker wait is inferred, not shown, and
    its reasons give the one seed and cell the run file holds. F160's
    value states the room as Phase 2 does (a data term of 4 x fraud
    rate), drops a "so" the source does not have, and says F25's card
    records the reopened design. F166's gap value attributes F159's
    equality to Phase 2. F156's reasons name the fifth and sixth methods
    correctly.
  - **Not changed here.** The f151, f153 and f154 source records still
    point at Phase 2 commit 10086da, although Phase 2 changed their
    documents by 9cbe5ba; they failed the local-file check before this
    sprint. Carded as F124, not repointed here, because each
    needs its document re-read whole. Phase 2's own BLUF is Phase 2's to
    correct, by a prompt the team lead pastes there.

## 57. Applied 2026-10-30: Roadmap-to-QML's release for Sprint 14 (Sprint 14 Task C, F123, F98)

Every count is a snapshot as of 2026-10-30. Written before the apply.

- **The list, at one commit.** Roadmap-to-QML read at commit
  `ea6f42a7c0` (pushed 2026-10-27; the head on 2026-10-30), 9 commits
  after F104's `a239747648` (section 46). Its 13 files are saved under
  `References\Roadmap-to-QML_ea6f42a7c0\`, outside git; the manifest
  records each file's SHA-256.
- **1,450 arXiv ids listed; 32 linked for the first time since
  a239747648; 4 new to the store.** 28 of the 32 are papers the store
  already holds: the list replaced a publisher link with the arXiv link
  (Montanaro 2016, Huang et al. 2021 and 26 more) or named a withdrawn
  paper's replacement (2405.13351, 2210.14450). The 4 new ones
  (2609.19983, 2610.32762, 2610.34430, 2610.35126) enter through the door
  at `seen` under `qml`, each naming the file that lists it.
- **Routes only for the newly linked.** Each of the 28 held papers gets a
  `found_via` route naming the list at `ea6f42a7c0` and its file. The
  papers the list linked at `a239747648` already carry F104's route; a
  route at each new commit would restate the same match about 1,400
  times, so none is added.
- **Free copies: 4 of 4**, fetched by the paced fetcher (18 s apart),
  each named with its SHA-256 in `evidence`. 2610.32762 (Ortiz Cordero et
  al.) carries no arXiv stamp on page 1; its first page was checked by
  hand and its title and authors match the arXiv metadata.
- **Seven marks, compared with the store; no record changed.** The list
  now marks six papers WITHDRAWN by their authors (2308.08167,
  2304.05672, 2409.10932, 2403.17444, 2410.03853, 2503.23408) and one
  RETRACTED (Valdez and Melin 2022, DOI 10.1007/s00500-022-07037-4,
  marked "RETRACTED 10 March 2026"). Each is already held at `seen` with
  a disposition that says withdrawn or retracted (F33), so the store and
  the list agree. A record would be corrected only from the arXiv or
  publisher page, never from the list's mark. The manifest's `marks`
  lists each with its record.
- **20 other links carried, 7 with a DOI** (25 at F104). The 5 that left
  the carried list are the publisher links the list replaced with arXiv
  links the store holds. The malformed `2108.0131` (section 46) is still
  listed and still held as `2108.01311`.
- **Reading.** The 4 are read in full by local first-pass readers under
  `manifests/sprint14_f114_reads/READER_PROMPT.md` (Task G's prompt with
  its paths moved to F114's work folder; no budget), as ledger group g330
  beside Task F's, and applied with F's groups.
- `scripts/sprint14_f123_roadmap.py` loads F104's script and points it at
  this commit; dry run by default, which writes
  `manifests/sprint14_f123_roadmap.json`; `--apply` takes a verified
  backup; a second apply enters nothing and adds no route.
  `tests/test_sprint14_f123.py`.

## 58. F114's first release: groups g043 to g113 and g330, reviewed by F117 (Sprint 14 Tasks E and F)

Every count is a snapshot as of 2026-10-30. Written before the apply; the
counts that enter are added when it runs.

- **What is read.** 72 ledger groups, 351 records, every paper read in
  full under Task G's rules (section 53; no budget):
  - Task E: groups g043 to g102 and the cloud records of g103 to g113,
    read in cloud sessions in Sprint 13 and Sprint 14
    (`scripts/f114_cloud.py`; its results restored to
    `work\f114\results\`).
  - Task F: 54 records read by local first-pass readers under
    `manifests/sprint14_f114_reads/READER_PROMPT.md`: 50 papers of g079
    and g103 to g113 (Q1 = 2), and g330, Task C's 4 papers (section 57).
    Boyd and Vandenberghe's textbook (g103) was read by two readers in
    turn: the first stopped with its context full at PDF page 520, the
    second read the rest and checked every seed after it.
  - The readers proposed 13,660 new assertions and judged 633 stored ones
    (394 confirmed, 185 narrowed, 48 widened, 6 corrected).
- **Page anchors are computed for local reads.** A local reader's page
  is replaced by the PDF page its quotes are on, counted with pdftotext's
  form feeds (`fix_pages` in `scripts/f117_build_groups.py`); a "printed"
  page is left alone, and every change is listed when the group file is
  built. The readers' text layers had lost their page breaks, so anchors
  had run up to 15 pages off. Five fresh-eyes reviews of the fixer found
  defects, each fixed and proven red; F126 holds what is left (none of it
  in these groups).
- **How each group is reviewed (F117).** One Sonnet 5.5 reviewer per
  group decides every item from its passage read in context
  (`manifests/f117_reviews/REVIEW_PROMPT.md`); the coordinator (Opus 5.5)
  reads the decisions and signs the group off; `scripts/f117_review.py
  finalize` writes `manifests/sprint13_g_reviews/gNNN.json`. Boyd's 1,033
  items were reviewed in ten parts and merged by id (none lost or twice).
- **Every certainty change on a stored assertion is the team lead's.**
  Finalize stops on one and writes it to
  `work\f114\review\escalations\gNNN.pending.json`. 16 groups wait on
  them; they enter after the team lead's decisions at Manual Validation.
  56 groups are finalized: 2,910 graded HIGH and 630 theoretical results
  kept LOW. Any other result is LOW by default.
- **The sign-off's edits.** Value replacements, extra quotes and
  re-quotes are added to a group's review file (the applier's existing
  tables). Each replacement is checked as the applier checks it: its
  passages verbatim in the source and every number in its quotes. The
  text-layer slips (2^16 printed as 216, 10^4 as 104 and 10^5 as 105, a
  lost negation in Boyd) were read from the page image.
- **One grading rule across groups.** A proof that rests on a cited or
  unproved result is LOW, and its why names that result; standard
  background mathematics does not make a result LOW; a value shown only
  in part is LOW. Two consistency passes (Boyd's nine parts; the other
  groups' cited results and news or vendor pages) propose the corrections
  the coordinator applies, and stored assertions among them go to the
  team lead.
- **Left out.** 8 records are marked unread in their group's review, with
  why: among them g113's 3 chen-2026 papers, beyond Task F's 50 (F125).
  muta-hardware-scope-photonic-gkp keeps its stored page (F126).
- **How a read is recorded.** As in section 53: a `full` row naming the
  reader, with the group's tag; a local read in a group otherwise read in
  the cloud names its own tag and reader (`tags` and `readers` in the
  review file).
- **The apply.** `scripts/sprint13_g_reading.py` enters each finalized
  group. It is tried first on a copy of the store, then run with a
  verified backup; a second apply writes nothing.
- **Correction and the first apply, 2026-10-30 (counts a snapshot as of
  that date).** The counts above were written before the review fixes
  and the consistency passes, and are left as written:
  - The coordinator set 10 reviewer HIGHs on vendors' own claims to LOW
    (store.grading writes a vendor's own claim LOW), applied Boyd's
    consistency ruling (56 decisions; the exercise marker wins, the scalar
    second-derivative test is background), and applied 82 of the
    cross-group pass's 86 proposals. The line drawn: a textbook-standard
    result is background; a specific paper's lemma or derivation taken by
    citation makes an item LOW. 4 proposals were rejected on it.
  - 19 groups now wait on 28 certainty changes for the team lead (7 of
    them from the cross-group pass). g043's qnpg-sample-complexity no
    longer escalates: its proof rests on two cited lemmas, so the review
    keeps it LOW, as stored.
  - 6 groups are held: g052, g053, g054, g055, g060 and g061. Each holds
    a paper its reader marked as bearing on no context but entered
    assertions for anyway (184 in all); which context they take, if any,
    is the team lead's decision.
  - 47 groups were applied, with backup
    `evidence-20261030T194240209474-...db`: 7,715 new assertions (2,273
    HIGH, 5,442 LOW), 117 stored assertions updated, 106 applicability
    rows, 119 records raised to tier `read`, 9 records refused with
    their reason. A second apply wrote nothing.
- **Second correction, 2026-10-30, the same evening (counts a snapshot as
  of that date).** The fresh-eyes review of that apply found 10 papers an
  earlier read had refused as bearing on no context (F89, F96, F105,
  F112) entered with 467 assertions, because F114's reader chose a
  context; no review said so, and the 6 held groups had been held for
  the same question. The store was restored from the pre-apply backup
  (`evidence-20261030T194240209474-...db`; the state it replaced is kept
  in `evidence-20261030T203545673004-...db`) and the apply run again:
  - 18 papers are now recorded as read and NOT entered, their 763
    assertions waiting for the team lead's decision at Manual
    Validation: the 16 an earlier read refused, and darji-2024 and
    du-2024, whose readers gave no context.
  - The 6 held groups are applied, less those papers. 53 groups in all:
    7,897 new assertions (2,315 HIGH, 5,582 LOW), 117 stored assertions
    updated, 111 applicability rows, 129 records raised to `read`, 29
    records refused with their reason. A second apply wrote nothing.
  - The applier now refuses a new assertion on a paper an earlier read
    refused unless the review names the reversal (`reenter`).
- **Third correction, 2026-10-30, later the same evening.** The
  fresh-eyes review of 4d969d9 found that 6 of the 18 refusal notes
  (darji-2024, du-2024, faro-2024, grazioli-2025, lawrie-2023,
  li-gomez-2023) carried the reader's own reason, which for 3 of them
  said the assertions were entered under a context, and never named the
  team lead's pending decision. The applier now prefers the sign-off
  drop reason; a re-apply (backup
  `evidence-20261030T210228761119-...db`) appended the corrected note to
  those 6 records and wrote nothing else. The earlier notes stay, as
  history; the latest note on each record is the one that holds.
- **The team lead's decisions, 2026-10-31 (Sprint 14 Manual Validation;
  counts a snapshot as of that date).** Written before the apply; the
  counts that enter are added when it runs.
  - Q1 option 1: the 28 certainty changes in the 19 waiting groups are
    settled as recommended (`work\f114\review\escalations\gNNN.json`):
    4 stored LOWs raised to HIGH (qnpg-bias, qml-advantage-general-functions
    and qnn-decoder-standard-qec-bound as proved results, babbush-five-stages
    as the paper's own definition), 1 MODERATE and 22 HIGHs set LOW with
    the reviewer's cause, and cgz-nonuniform-zero-one-corollary7 kept HIGH
    with the square root its value had dropped restored (p.13, Eq 26; the
    stored value had the same slip). The 7 stored HIGHs set LOW whose
    reader gave no value keep their stored value (`value_replace`). The 19
    groups are finalized with `reviewed_on` 2026-10-31.
  - Q2 option 1: the 18 papers stay out. Their 763 drop reasons in the
    14 review files now end with the decision, so the apply appends one
    more note to each of the 18 records; the earlier notes stay, as
    history.
  - The dry run refused 5 of the settled items until their sign-off was
    fixed: 3 stored HIGHs set LOW whose reader gave no quotes take their
    stored quotes (`extra_quotes`); two-way-partitioning-dual-sdp-lower-bound's
    stored value stated "1 or -1", which none of its quotes hold, so its
    value now says only what its quotes say, with one added quote; and
    cgz-nonuniform-zero-one-corollary7's value states the square root in
    words, in the quote's own symbols.
  - Applied with backup `evidence-20261031T110555183383-...db`, first on a
    copy of the store: 5,000 new assertions (1,796 HIGH, 3,204 LOW), 136
    stored assertions updated (22 HIGH to LOW, 4 LOW to HIGH, 1 MODERATE
    to LOW, the rest keeping their grade), 1 record raised to `read`, and
    18 refusal notes appended. A second apply wrote nothing. The store now
    holds 23,653 assertions (8,167 HIGH, 15,386 LOW).
- **Fourth correction, 2026-10-31.** The full suite after that apply
  failed 3 live-store tests:
  - A real defect: the apply replaced the stored context of 2 assertions
    with the reader's nearest-fit label, which no review decided (context
    is not an item the F117 reviewer grades):
    dirac3-stratification-falls-short-ballin-2026 lost
    `platform:dirac-3` (to `qc`), and
    Abbas's effective-dimension bound (g079) moved from `qml` to
    `ml`. The applier now keeps a stored assertion's context unless the
    sign-off names it in `context_fix`. Both go back through a
    `context_fix` in the g079 and g094 sign-offs, because the stored
    contexts are now the wrong ones. The 2026-10-30 apply moved no stored
    context (its backups compared).
  - Finalize reads the stored grades from the store, so after an apply it
    no longer sees the certainty changes it settled. g079 and g094 were
    re-finalized against a copy of the pre-apply backup
    (`EBDB_STORE_DIR`), with the same counts as before.
  - Re-applied with backup `evidence-20261031T123122796779-...db`, first
    on a copy: the 2 contexts restored and nothing else; a second apply
    wrote nothing.
  - Two tests assumed the Sprint 9 and Sprint 10 scripts still own their
    assertions (F80: 12 ids; F83: two-way-partitioning-dual-sdp-lower-bound).
    F114's full reads rewrote them under reviewed verdicts, and the team
    lead decided their certainty changes. The tests now leave out an id
    whose stored history records a later full read, and still hold every
    other id to its script.
- **Fifth correction, 2026-10-31, the review of 0eddd23.** Written before
  the re-apply.
  - Two counts above are wrong as written: 138 stored assertions were
    updated, not 136 (136 changed value or grade; 2 changed other fields),
    and the 23,653 assertions also include 100 graded neither HIGH nor
    LOW (97 MODERATE, 1 very-low, 2 with no grade).
  - The 13 theoretical results set LOW at the team lead's decision kept
    the reviewer's cause as their certainty reason, and 4 of those said
    "g045 (or g109) has no pending escalation", which was false. Each is
    now settled as `["low", why]`, the cause less that sentence, ending
    with the team lead's decision; g045, g079, g095, g097, g102, g103,
    g106 and g109 were re-finalized against the pre-apply copy. The 10
    other LOW settlements carry the store's fixed reason for their result
    type, which has no place for the decision; their decision is recorded
    in this section and in `work\f114\review\escalations\`.
  - two-way-partitioning-dual-sdp-lower-bound's value said "the best"
    bound is an SDP's optimal value, which no quote held. It now quotes
    "The dual problem is an SDP" and the sentence on its optimal value.
  - The new context test passed with no check at all once the sign-off
    named both of its ids in `context_fix`; it now takes them out of
    `context_fix`. The F80 and F83 tests leave out an id only when its
    last change is a full read's rewrite, not a "NOT in the paper" note.
  - Re-applied with backup `evidence-20261031T144159928184-...db`, first
    on a copy: 13 records updated (the 13 certainty reasons, and the
    two-way value and quotes) and nothing else; a second apply wrote
    nothing.
- **Sixth correction, 2026-10-31, the review of bb82d0a.** Written before
  the re-apply. The fifth correction's edit of the 13 reasons was made by
  pattern and missed variants: qgen-grover-lower-bound kept a dangling
  "for it.", generalization-bound-involves-encoding kept the false
  "Stored HIGH; not in the g097 pending escalations.", and
  fidelity-bounds-hamiltonian-norms, qaoa-qa-conditions and
  qaoa-qa-equivalence-proof kept a sentence asking for the team lead's
  review that the decision now answers. Each is edited by hand. The
  two-way value's "can be solved efficiently" now has its quote ("This
  problem can be solved efficiently, ..."). g097, g102, g103 and g109
  were re-finalized against the pre-apply copy. Re-applied with backup
  `evidence-20261031T161240715569-...db`, first on a copy: 6 records
  updated and nothing else; a second apply wrote nothing.
- **Seventh correction, 2026-10-31, the review of 25d3985.** Written
  before the re-apply. barthe-necessary-conditions-tradeoff's reason
  compared the reader's value with a stored value the apply had already
  replaced; that comparison is removed. barthe-universality-proved's
  value began "The paper proves" while its reason says the proofs do not
  settle it; both barthe values now state the paper's claim as a claim
  ("The authors state that they prove", "The paper states, as its second
  central result"), which their quotes hold. caro-generalization-error-
  sqrt-t-over-n's reason loses a reviewer's "Gray:" label. g095 and g106
  re-finalized against the pre-apply copy. The review chain on these
  settlements stops here; what is left is cosmetic: a doubled period
  before "NOT upgraded" in about 900 reasons store-wide (it predates this
  sprint), and update notes that name the full read but not a quote
  extension. Re-applied with backup
  `evidence-20261031T173833940424-...db`, first on a copy: 3 records
  updated (the two barthe values and reasons, the caro reason) and
  nothing else; a second apply wrote nothing.
- **Rule, 2026-10-31 (Sprint 14 retrospective Q1 = 1): settlement and
  review text is edited by hand, never by pattern.** A settlement reason,
  a sign-off value or a review note is read and rewritten one record at a
  time with the Edit tool. A regular expression or a search-and-replace
  over several of them is not used, even when they look alike. The fifth
  correction edited 13 reasons by pattern and missed variants in 5 of
  them; the sixth correction found them only on review. A store-wide fix
  of a fixed template's format (not its words) is a script, as section
  59 is, and it names the exact string it replaces.

## 59. A doubled period before "NOT upgraded" (Sprint 14 retrospective Q7)

Written 2026-10-31, before the apply. Every count here is a snapshot as of
2026-10-31.

- **What is wrong.** `store.grading.low_grade` joins a LOW's reason as
  `Started LOW: <basis>: <why>. NOT upgraded`. A why that already ends in
  a period gives `.. NOT upgraded`. 900 stored `certainty_reasons` hold
  it, every one of them starting "Started LOW:". It predates Sprint 14;
  the full reads of Sprint 13 and 14 added most of them. No repository
  file holds the doubled text: each is computed by `low_grade`.
- **The fix at the source.** `low_grade` drops one trailing period from
  the why, so the template's own period is the only one.
- **The fix in the store.** `scripts/sprint14_q7_doubled_period.py`
  replaces the exact string `.. NOT upgraded` with `. NOT upgraded` in
  `certainty_reasons`, and nothing else. Dry run by default; `--apply`
  takes a verified backup first. Each changed record gets the note
  "2026-10-31 (Sprint 14 retrospective Q7): format only: ...", naming
  this section.
- **Why the note says "format only".** A full read owns a record whose
  last change names it (`FULL_READ_MARK`). The format note must not take
  that ownership away: the sync's same-day guard and the reading tests
  ask for the last change, and both now skip a note that carries
  `FORMAT_ONLY_MARK` (`store.ingest.last_change`). Without that, an older
  reading script dated 2026-10-31 could re-sync over a full read, and the
  F80 and F83 tests would hold 13 full-read records to their old scripts.
- **Checks.** A live-store test finds no `.. NOT upgraded` left. Trial on
  a copy first, then live; a second apply changes nothing, and an apply
  of the full-read applier (renamed `scripts/full_read_apply.py`, Q5) on
  the fixed copy changes nothing either: it now computes the single period
  the store holds.
- **Applied 2026-10-31** with backup
  `evidence-20261031T182657101772-...db`, first on a copy: 900 records
  fixed; a second apply fixed none; the full-read applier on the fixed
  copy changed nothing and listed no undecided field.
- **Correction, 2026-10-31, the review of 7b2179f.** The note moved
  `updated` to 2026-10-31 on all 900 records; on 365 of them the last real
  change is earlier (364 on 2026-10-30, 1 on 2026-10-26). The sync guard
  read `updated`, so a corrected sign-off dated on such a group's review
  day would have been refused without a word, and the "changed nothing"
  check above held for those 365 only because the guard skipped them. The
  guard now reads the date of the last real change when the last note is
  format-only; a record with no format note is read as before. The
  script's pattern now matches exactly two periods, so a why that ends in
  an ellipsis is left alone (none is stored). No store write: the 900
  records stay as fixed. With the corrected guard, the full-read applier
  on a fresh copy of the live store changed nothing and listed no
  undecided field, so the 365 records hold what their reviews say. For a
  basis that needs a why, a why of only "." is now refused by
  `low_grade` as no why at all; for any other basis it is dropped. A why
  that ends in two periods still gives two (none is stored).

## 60. A corrected anchor on a confirmed stored assertion (Sprint 15 Task D, F126)

Written 2026-11-01, before the apply. Every count here is a snapshot as of
2026-11-01.

- **What was wrong.** g104's review (Sprint 14 Task F) found the passage
  of `muta-hardware-scope-photonic-gkp` ("Here, we focus on photonic GKP
  computation") on PDF p.8 of Calderon et al. (arXiv 2405.08319); the
  store says Section V, p.9. The reader confirmed the assertion with no
  quotes or anchor, so REQUOTE had nothing to rebuild from, and the
  applier never wrote an ANCHOR_FIX on a confirmed stored assertion. It
  dropped it without a word.
- **The path.** `scripts/full_read_apply.py` now rebuilds such an
  assertion from its stored row with only its anchor changed (provenance
  and each quote's anchor), checks every stored quote against the source
  again, and writes it through the verified sync. A grade the review
  gives it is written as for any graded assertion; otherwise the stored
  grade stays. A review's `anchor_fix_on` dates the correction and names
  its task, so it does not take the group's older review day. The dry run
  lists each such move.
- **The entry.** g104's review gains `anchor_fix` (Section V, p.8) and
  `anchor_fix_on` (2026-11-01, Sprint 15 Task D, F126) for this one
  assertion. pdftotext puts the quote on PDF page 8 and on no other page.
- **What changes in the store.** One assertion: its provenance and
  citation_context (p.9 to p.8), and its certainty_reasons, which g104's
  review already graded HIGH with the basis "scope" and the corrected
  page. The certainty stays HIGH. Nothing else.
- **Checks.** Trial on a copy of the store first, then live with its
  verified backup; a second apply writes nothing; the apply lists no field
  that no review item names.
- **Applied 2026-11-01** with backup
  `evidence-20261101T155312102348-...db` (verified), first twice on a
  copy: the one assertion changed (provenance, certainty_reasons,
  citation_context), dated 2026-11-01; the second apply changed nothing;
  no undecided field.

## 61. Text from page images (Sprint 15 Task F, F115)

Written 2026-11-01. Every count here is a snapshot as of 2026-11-01. This
section writes nothing to the store: it records how image-only pages are
read from now on.

- **What was wrong.** A page with no text layer gave a reader nothing.
  udaru-2025-qml-credit-risk is ten page images, and the team lead marked
  it unread (2026-10-27).
- **The engine.** RapidOCR 3.10.0 (Apache-2.0) on ONNX Runtime 1.31.1
  (MIT), the cross-platform engine the team lead chose at plan approval
  over Windows' built-in OCR. It runs in its own virtual environment,
  `D:\Data\Harold\EvidenceBasedDB\ocr-venv` (outside git), installed from
  `requirements-ocr.txt`, because its dependencies would raise the main
  interpreter's numpy from 1.26.2 to 2.5.4. `store/ocr.py` calls it through
  `scripts/ocr_worker.py`. Its three models ship inside the wheel; the
  worker never downloads one, and reports each model file's SHA-256.
- **Which pages.** A page of a local PDF whose text layer holds fewer than
  40 visible characters. `pdftoppm` renders it at 200 dpi and RapidOCR
  reads it. The page count comes from `pdfinfo`: a text layer may hold a
  form feed inside a page (Qian et al. 2021: 103 parts for 23 pages), so a
  split that disagrees with the count is replaced by one extraction per
  page.
- **The scan, 2026-11-01.** Of 1,703 local PDFs, 64 have thin pages, 221
  pages in all (656 s for the whole OCR run, uncached). Most thin pages
  are figures or blank pages, and OCR finds little or no text on them;
  those are read as figures under Task G (F116). The sources whose text
  OCR supplies:
  - all pages image-only: udaru-2025-qml-credit-risk (10 pages, 38,016
    characters), mancilla-2026-spectra-datasets-substack (8 pages, 9,250),
    qci-2026-entropy-computing-trade-magazine (6 pages, 10,562);
  - some pages image-only:
    sturm-2023-theory-implementation-quantum-approximate-optimization (4
    pages, 2,257 characters), perrier-2024-quantum-geometric-machine-learning
    (9 pages, 948), mahmood-2026-classical-hybrid-quantum-machine-learning
    (1 page, 650).
- **The cache.** The OCR text is kept in the store folder's `text_cache\`,
  keyed by the file's SHA-256, the render resolution, `pdftoppm`'s version
  and the engine's pinned versions, so a changed file or engine reads
  again. A source that needs OCR when the engine is missing raises
  `OcrUnavailable`: an image-only page is never read as empty without a
  word.
- **The quote check reads it.** `store.quotes.source_text` gives the text
  layer, then ` || OCR: ` and the OCR text of the thin pages; an image
  file given as a source is all OCR text, after `OCR: `. A quote found
  only in OCR text needs "OCR" in its anchor; `scripts/full_read_apply.py`
  and the reader check refuse one without it.
- **Provenance.** `store.ocr.provenance` names the pages, the engine and
  its version, the ONNX Runtime version, each model's SHA-256 (first 12
  characters) and the render resolution.
- **Grading** (team lead, 2026-11-01, plan Q3). OCR text from a page of a
  stored PDF is graded as text-layer text: HIGH is allowed. OCR text from
  an image file that is not inside a PDF is HIGH only when another source
  corroborates the claim, named in its certainty reasons ("corroborated
  by <record>"); otherwise MEDIUM is the highest. The applier refuses a
  HIGH from an image file without it.
- **Readers.** Sprint 15's reader prompt
  (`manifests/sprint15_f114_reads/READER_PROMPT.md`) tells a reader where
  the OCR text is, to copy an OCR quote exactly as given (misreadings
  included, such as "Maçhine"), and to mark it "OCR". udaru is the first
  of F114's 100 papers (Task H).

## 62. Phase 2's F151, F153 and F154 repointed at develop af03165 (Sprint 15 Task K, F124)

Written 2026-11-01, before the apply. Every count here is a snapshot as of
2026-11-01.

- **What was wrong.** The three source records point at Phase 2 commit
  10086da. Phase 2's PR 46 review changed each document after it (last
  by 28bdbcd), so the local-file check read all three as changed.
- **The read.** Each document read whole at af03165, Phase 2's develop
  head (2026-10-30), through `git show` on the team lead's clone, which
  holds the commit; no fetch (F79). The blob at af03165 equals Phase 2's
  working copy of each file, so the local-file check reads it unchanged.
- **What changed, and what it does to the stored values.**
  - F151: the `l2_regularization=0.1` row now fails on level as well as
    SD; a note that the range threshold cannot decide at five seeds; the
    tasks that use the setting. Neither stored value states these: both
    confirmed by name (`f151-cvqboost-proxy-below-stable-hgb-on-ulb`,
    `f151-hgb-default-l2-zero-unstable-at-extreme-imbalance`).
  - F153: the objective's size is "between 0.8 and 1" (was "close to
    1"), and the data term "is at most 0.33%" of it. Neither stored value
    states the size: both confirmed by name
    (`f153-learner-selection-formulation-fails-its-falsifier`,
    `f153-two-resolution-checks-disagree-in-kind`).
  - F154: the closest cell names the proxy's `deep` configuration; 16
    exempt runs remain. The stored value states neither: confirmed by
    name (`f154-no-stored-model-better-on-a-ulb-subset`).
- **What changes in the store.** For each record: one `paper_reads` row
  (full, 2026-11-01), and `access`, `evidence` and
  `checked_against_source` repointed at af03165. The evidence keeps the
  first read (2026-10-22, commit 10086da) and its blob SHA-256. No
  assertion changes. Every stored quote is checked verbatim, with its
  value, at af03165 before the write (`scripts/sprint15_f124_phase2.py`).
- **Checks.** Trial on a copy of the store first, then live with its
  verified backup; a second apply writes nothing; the local-file check
  reads all three as unchanged.
- **Applied 2026-11-01** with backup
  `evidence-20261101T174117632352-...db` (verified), first twice on a
  copy: three read rows and three repoints; the second apply wrote
  nothing; the local-file check reads all three as unchanged.
- **Not in this section: F166.** Its document
  (`docs/phase2/algorithms/ULB_COMPARISON.md`) is unchanged on Phase 2's
  develop (af03165 holds the recorded blob). Phase 2's unmerged Sprint 30
  branch, which the clone has checked out, added confusion-count columns
  to it, so the local-file check, which hashes the working copy, reads it
  as changed. That is a question for the team lead.

## 63. Reading targets for the gaps F118 found (Sprint 15 Task J, F128)

Written 2026-11-01, before the apply. Every count here is a snapshot as of
2026-11-01.

- **What.** F118's memo (`docs/spikes/F118_WHAT_THE_STORE_SAYS.md`)
  found questions the store could not answer. F128 names a source for
  each. `scripts/sprint15_f128_targets.py` fetches each target with a
  free arXiv copy by F104's paced fetcher (18 s apart) into `Papers\`,
  checks the arXiv stamp on its first page, and enters it through the
  door at `seen`, naming the gap it fills in its disposition and
  `found_via` "F118 memo, F128". The manifest
  (`manifests/sprint15_f128_targets.json`) lists each entry and the
  hand-download list.
- **Entered (8).** Gidney and Ekera (1905.09749, RSA-2048), Lee et al.
  (2011.03494, chemistry), Woerner and Egger (1806.06893, risk),
  Chakrabarti et al. (2012.03819, derivative pricing), Babbush et al.
  (2011.04149), Stoudenmire and Schwab (1605.05775), XGBoost
  (1603.02754) and Jaques and Rattew (2305.10310, QRAM critique).
- **Held already (1).** Giovannetti, Lloyd and Maccone (0708.1879,
  QRAM) is `giovannetti-2008-quantum-random-access-memory`, under its PRL
  DOI, which the arXiv-id match did not see; the script now treats an
  existing record id as held. It already had a local copy
  (`2007-08_Giovannetti_Quantum-Random-Access-Memory.pdf`), so the copy
  fetched on 2026-11-01 was a re-download against the standing rule; it
  was deleted the same hour. The paper is read in its ledger group,
  g307, not with Task J's.
- **The hand-download list (7).** LightGBM (NeurIPS 2017; not on
  arXiv), Ferrari Dacrema et al. (not in the store), Nielsen and Chuang
  (a book), vendor native-gate documentation, Dal Pozzolo et al. 2014
  (stored, unread; a DOI and no local copy), a concept-drift source for
  card fraud, and tuned anomaly-detection baselines on fraud (no source
  chosen yet).
- **Reading.** The 8, with Faryad (stored, read in part), are read in
  full under Sprint 15's reader prompt, in addition to Task H's 100, as
  ledger groups g331 (5) and g332 (4).
- **A door fix.** The door refused Babbush et al.'s citation as audit
  text, because "error-corrected" in its title holds "CORRECTED". A
  marker now counts only as a word of its own (`store/ingest.py`, with a
  test proven red).
- **Checks.** Trial on a copy of the store first, then live with its
  verified backup; a second apply enters nothing.
- **Applied 2026-11-01** with backup
  `evidence-20261101T182904857546-...db` (verified), first twice on a
  copy: 8 papers entered at `seen`; Giovannetti et al. found held; the
  second apply entered nothing.

## 64. F114 at 100 papers, under Sprint 15's prompts (Sprint 15 Task H)

Written 2026-11-01, before the apply; the counts that enter are added
when it runs. Every count here is a snapshot as of 2026-11-01.

- **What is read.** 100 papers, each in full, figures included
  (`scripts/sprint15_f114_local.py` writes the briefs):
  - the records reviewed groups left unread that now have text, each in
    a re-entry group (F125, Sprint 15 Task C): g062-r1, g064-r1 and
    g076-r1 (pages that are images, read from OCR text, section 61) and
    g113-r1 (three chen-2026 papers);
  - then ledger order from g114 to g133. Four records whose source is a
    directory (cycorp x3, ds3lab-feebee) are left for a later release:
    the quote check reads one file per source.
  - Task J's 9 (section 63) are read the same way in g331 and g332.
- **The readers.** Local first-pass readers (Sonnet 5.5) under
  `manifests/sprint15_f114_reads/READER_PROMPT.md`: every figure and
  table is viewed and entered in a `figures` list; a value read from a
  figure says so, writes each number read by eye as "about N", and is
  never HIGH; an OCR quote is copied as the OCR gives it and its anchor
  says "OCR"; anchors are PDF pages, checked against the page's text;
  a reader never changes a stored context. The reader check's
  `--sprint15` option enforces each rule.
- **The review.** One Sonnet 5.5 reviewer per group under
  `manifests/sprint15_f114_reads/REVIEW_PROMPT.md` (section 58's, with
  the textbook rule, the figure rule and the OCR rule added); the
  coordinator (Opus 5.5) signs each group off, its edits in
  `work\f114\review\signoff\`; `f117_review.py finalize` writes the
  review file, naming Sprint 15's tag and prompt. Every certainty change
  on a stored assertion waits for the team lead.
- **The apply.** `scripts/full_read_apply.py`, which refuses a figure
  value that is HIGH or does not say it was read from a figure. A dry
  run, then a trial on a copy of the store, then live with its verified
  backup; a second apply enters nothing.
- **Sign-off so far.** g062-r1 (15 HIGH), g064-r1 (3 HIGH; one value
  cut back to its quote, since a logo hides the rest of the sentence)
  and g076-r1 (2 HIGH; a caveat cited to reference [16] set LOW as a
  cited result). Their dry run: 115 assertions from 3 records. g113-r1
  (52 HIGH, 6 theoretical LOW): two textbook identities the paper
  states without proof were set LOW and join F129's list for the team
  lead; the review prompt gained a dated amendment saying so. g114
  (63 HIGH, 5 theoretical LOW): two values that said "because" where the
  paper says "in part because" were cut back to their passages. g115
  waits for the team lead: its Theorem 2 is proved from a theorem of
  Zhang et al. [64] taken by citation, so it is LOW, and the stored HIGH
  that rests on it (qdh-trainability-proof) is the team lead's to lower.
  g116 waits for the team lead on one change:
  aam-qaoa-converges-high-depth, stored HIGH, rests on Theorem 12 of
  reference [14], cited, so the review proposes LOW. Its sign-off kept
  sisr-far-from-lasso-and-dl LOW as stored (its value also holds a
  measured speed-up) and set four result types the reader had changed
  to pass the reader check back to their true types (F135). g117 (97
  HIGH, 18 theoretical LOW) is finalized. g118 waits for the team lead
  on three stored HIGHs the review proposes LOW, each resting on a cited
  result (qbm-poly-gibbs-states, qbm-pretraining-lowers-bound,
  wdt-speedup-at-most-quadratic); its sign-off set three result types
  back and requoted mild-imbalance-is-over-experts at its stored HIGH
  with the paper's word, "complicates", for "do not apply". g119 (97
  HIGH, 44 theoretical LOW) is finalized; its sign-off requoted
  cranganore-limit-photonic-circuit-model at its stored HIGH with the
  authors' caveat alone, without the premise cited to [94]. g120 waits
  for the team lead: cyc-index-layers-carry-counts is stored MODERATE
  (vendor documentation of its own product, `store/grading.py`); its
  narrowed value is right, and the review proposes LOW. Its sign-off set
  qgrand-fidelity-lower-bound-by-bler LOW (the paper's text and its
  equation (32) state the bound in opposite directions) and one result
  type back to measured. g122 (54 HIGH) and g124 (83 HIGH) are
  finalized; four stored HIGHs whose page or section anchors were wrong
  were requoted with the reader's anchors, values unchanged
  (trojannet-threat-model, deleon-vqe-limits,
  qelm-limited-to-12-qubits-simulation, qelm-hardware-not-tested). A
  stated future-work gap in the paper's own work is HIGH on "stated
  limit", as in section 58's groups; a conjecture or wish is LOW. g121
  waits for the team lead: dalyac-repetition-rate-few-hz, stored HIGH, is
  a review's statement about hardware in the field (stage durations
  summed, without measurement or citation), so the review proposes LOW.
  In a review or survey, only a limit on the review's own work is a
  stated limit; dalzell-2025 says it gives results without proofs, so
  none of its 20 proof items is a proved result. Eight dalzell values
  that join a scope or definition to an opinion are LOW and marked
  "split recommended" in their review. g126 waits for the team lead:
  derieux-parameters, stored LOW, is proposed HIGH on "setup" (the
  central parameter counts, 1 against 25, are the paper's architecture
  counts in its Table 1, not a measurement). g125 (72 HIGH, 25
  theoretical LOW) is finalized; its sign-off kept
  fidelity-kernels-classically-simulable-limit HIGH by removing the
  clause cited to [9] from the value. For the cross-group pass: dees-2023
  grades LOW every lemma whose proof uses the parameter-shift rule, which
  the paper cites to [21] although its own Lemma 2.4.3 implies it;
  whether the rule is a textbook tool decides those items. g128 waits
  for the team lead on one change: qclassifier-robust-weak-local, stored
  HIGH, joins a generalization bound cited from reference [66] to a
  bound that holds under a 2-design assumption, so the review proposes
  LOW. Its sign-off kept quadratization-loses-noiseless-quality HIGH on
  "stated limit" by removing the reader's added clause (a reading of
  Fig. 4) and its quote; the narrowing to the clique expansion method
  stands. Three more textbook items carry the F129 prefix
  (frqi-encoding-qubit-count, amplitude-damping-not-unital,
  table-iii-pauli-action). g123's review is split in two, because
  dawid-2025 (a 287-page book) holds 273 of its 365 items: one reviewer
  takes the book and one the other four papers. The two decision files
  are joined before sign-off. The book's first review decided about 199
  items from their quotes alone and did not render its four figure
  pages; it was sent back, read every passage and rendered the pages,
  and 13 items went from HIGH to LOW (130 HIGH, 143 LOW). g123 waits for
  the team lead on two stored HIGHs of de-felice-2024:
  fusion-network-factorization (Theorem 4.15 takes determinism from
  reference [10], Theorem 4) and rus-fusion-and-universality-proofs
  (Theorem 6.10 rests on Propositions 6.8 and 6.9, which use reference
  [69] and Theorem 4.15). For each, a value limited to the step the
  paper proves itself (the factorization; Theorem 6.4) could stay HIGH.
  Its sign-off corrected dawid-fig-ucb-panels, LOW, to the rendered
  figure. g127 (116 HIGH, 10 theoretical LOW) and g131 (28 HIGH, 6
  theoretical LOW) are finalized; their dry run enters 504 assertions
  from 10 records. g127's sign-off replaced a pronoun the reader gave
  the thesis author with "the author". The two dunjko records (2017 and
  2018) hold one byte-identical PDF; reader g131 entered the new
  assertions under the 2017 record only, and whether the two records
  are one paper is the team lead's question. A group's built file is
  made from its reader's file as it stands: g130's was first built
  while its reader was still editing, and was rebuilt (101 items
  became 108) before its review. g130 (93 HIGH, 8 theoretical LOW) is
  finalized; the dry run of g127, g130 and g131 enters 740 assertions
  from 15 records. For the cross-group pass: six stored HIGHs of g130
  carry the stored result type "measured" on a scope or stated-limit
  statement (bayes-pqc-limits, qp-methodology-ongoing-experiment,
  qp-needs-more-evidence, qpic-comparative-groups-pending,
  qpic-no-long-term-measure, scope-max-clique-simple-graphs); no
  certainty changes. dundar-coecke-2025 states private-school
  performance "significantly higher" in its Discussion against a
  non-significant ANOVA in its Results (reader g130). g133 waits for
  the team lead on one change: cvqboost-vs-xgboost-auc-under-balancing,
  stored MODERATE, is a vendor's measured result on its own product
  (emami-2025: six QCi authors on QCi's Dirac-3), so the review proposes
  LOW. Its reader corrected cvqboost-vs-xgboost-training-time-dirac3,
  already LOW: the paper's 117.4 s is single-core XGBoost, not 48 CPUs
  and four GPUs, and at 150,000 samples 8-core XGBoost takes 4.2 s and
  GPU XGBoost 3.6 s against CVQBoost's 2.2 s. The reader check now lets
  a stored assertion keep a stored context outside the five
  (platform:dirac-3), which no read could otherwise pass. g129 (107
  HIGH, 62 theoretical LOW) is finalized; the dry run of g127, g129,
  g130 and g131 enters 1,236 assertions from 19 records. Its review
  confirmed the errors reader g129 found in du-2025's 260-page tutorial
  (Eqs. 2.19, 2.42, 3.25, 3.67, 3.68, Theorem 3.13, Lemma 4.12 and
  Eq. 5.6) and found four more (the depolarizing channel's p against
  p/4, Theorem 4.16's dropped Tr[O] = 0 condition, Eq. 3.32 against
  Eq. 3.31, and the ridge derivation's a^T K y); an item that rests on a
  printed step in error is LOW. About 20 items carry the F129 prefix,
  and the review grades LOW the field-level open questions in a review
  or tutorial (not limits on its own work), the class section 64 already
  names. g132 waits for the team lead on one change:
  findings-specific-feature-space-size (egginger-2024), stored HIGH,
  joins a scope clause to a measured result (relabeled datasets show
  different dependencies), so the review proposes LOW; a value holding
  the scope clause alone could stay HIGH. Seven ehrlich-2026 items
  carry the F129 prefix.
- **Task I (F133, the F57 release), 100 records.** The plan named first
  the 11 records whose access names only a local file, then F57's
  relevance ranking over the 524 records with no read row. Snapshot as
  of 2026-11-02: no unread record outside the read ledger names a local
  file, and every unread record with a local file is in the ledger past
  H's groups; the 355 outside it (175 with a DOI, 7 with an arXiv id,
  173 GitHub repositories) have no local copy. So Task I reads the next
  100 in ledger order, g134 to g154
  (`scripts/sprint15_f114_local.py --task-i`), under H's prompts, and
  one repository (fraud-detection-handbook) is left for a later release.
  Whether ledger order stands in for F57's context ranking is the team
  lead's question at Manual Validation. g134 waits for the team lead on
  two stored HIGHs of farboodi-2026: correlated-errors-segment-the-market
  (the proved Proposition 1 joined to an AI-systems attribution and a
  "smoothly increasing" shape the proposition does not require) and
  policy-effects-ai-and-data-sharing (stylized examples, not a proof).
  g138 waits on one: gacon-qgt-free-method joins its proposal (scope) to
  the claim that the QGT method is "infeasible for relevant system
  sizes", which rests on the authors' own modeled runtimes. Its sign-off
  corrected gacon-fig1-runtime-read, LOW, to the figure (about 25 hours,
  and the 1 year line near about 590 parameters).
  g136 waits on one: ferris-2022's post-selection-limit joins its stated
  limit (measurements thrown out) to the unmeasured claim that
  post-selection is "a powerful error mitigation option". g137 waits on
  two of fontana-2024, each narrowed to carry the paper's own conditions:
  lasa-gradient-variance-inverse-dla-dim (the inverse scaling is the
  authors' reading of Theorems 2.8 and 2.9, and they say the DLA
  dimension may not dominate) and rapid-mixing-polynomial-dla (Theorem
  H.1 follows Ref. [33] with "one can verify" steps). Its sign-off
  corrected three rydberggpt values whose text layer prints 10^5 and
  10^4 flat as 105 and 104, checked on the rendered pages; franco-2024's
  text and Figure 1 disagree on the screening counts, and only the
  totals both agree on (4,658 and 27) stand HIGH. g139 is finalized; its
  sign-off corrected galvis-simulation-shots the same way (10^6), and
  galvis-florez-2025's Introduction (eps^-3) and Section IV (eps^-5,
  log(1/delta)) disagree on the cost, so its speedup stays LOW.
  g141 waits on two of gentinetta-2024: qsvm-primal-pegasos-complexity
  (its derivation takes T = O(1/delta) from the Pegasos paper as a step,
  and Assumption 2 is unproved) and qsvm-dual-complexity (its proof uses
  cited theorems, and it holds only under Assumption 1 and with a fixed
  probability above one half, which the stored value omitted). The
  coordinator regraded practical-advantage-open LOW: it is an open
  question about the field, not a limit on the paper's own work.
  g140 waits on three: garcia-2023's qml-slr-selection-94-papers (its
  Section 2.5 reaches 70 studies, its PRISMA diagram 94 as 70 plus 24,
  Figure 1's bars sum to 9038 against the text's 5497, and its date
  range is 2017 to 2023 in some places and 2017 to 2022 in others), and
  two of garcia-martin-2024 (effects of noise):
  noise-suppresses-qfim-eigenvalues (Theorem 4 takes Theorem 6.1 of
  Mueller-Hermes, Franca and Wolf as a step) and
  noise-turns-on-null-eigenvalues (one single-qubit example and
  simulations; the paper says it does not attempt a proof).
  g142 waits on one: gheisarnejad-2023's qdrl-scheme-and-testbed joins a
  HIGH setup (compared with model predictive control on a hardware-in-
  the-loop testbed) to an untested purpose (quantum principles "to
  address the hardware limitations of conventional computers"); nothing
  in the file says anything ran on quantum hardware or a simulator. The
  gharibyan authors are BlueQubit, which sells the platform; their
  measured results are LOW.
  g143 waits on one: gibford-2025's qwgan-bioprocess-setup says "five
  qubits arranged in three layers", which conflicts with the paper's
  two repeated layers and 45 parameters; its 2000-epoch half could stand
  HIGH if split.
  g144 waits on two: gil-fuster-2025's gilfuster-bp-trainable
  (Proposition 1's proof takes results of Cerezo et al. 2021 and Liu et
  al. 2021 as steps, and its training is not gradient based) and
  gil-vidal-2020's pqc-bounds-logarithmic-tight (an introductory claim
  of tightness that no theorem or example proves; the bounds cover
  exact representation only). Its reviewer graded three absence items
  (no experiments, no hardware run) LOW because the paper never states
  the absence; the cross-group pass checks that against other groups.
  g145 waits on two: giuliani-2023's giuliani-poly-resources (it rests
  on Corollary 1, whose "it is possible to show" step is asserted, not
  shown) and gomez-2026's spe-evaluation-setup (the text says 20
  datasets in five places; Table 2 lists 16, counted on the rendered
  page). gomes-2024's proofs nearly all take results of Gilyen et al.
  or the GQSP paper as steps, so they are LOW, and the lemmas built on
  them are LOW in turn. Two stored HIGHs that stay HIGH are typed
  "measured" though neither is a measurement (autoqml-cloud-architecture
  is a setup, giuliani-sample-limit a stated limit); they join g130's
  six in the cross-group pass.
  g146 waits on two: gong-2026's hamlearn-computational-basis (the
  reconstruction is proved, but the value adds that it "captures
  contemporary Rydberg atom platforms", the authors' relevance claim)
  and gonski-2026's white-paper-scope (half of it is a field statement,
  "quantum computing remains in early stages"). gong-2026's Theorems 5
  to 9 rest on determinants computed modulo 1000003 at stated witness
  points, recorded but not checkable by hand; they stand HIGH, flagged.
  g147 is finalized; its sign-off wrote two grana-2025 shot counts
  (10^5 and 10^7, printed flat as 105 and 107) in words.
  g148 is finalized. Six more stored HIGHs that stay HIGH are typed
  "measured" though each is a scope, setup or stated limit
  (grange-tutorial-scope, not-representative-biased,
  study-basis-interviews, qrc-experiment-setup-limits,
  qml-survey-excludes-qrl, qml-survey-scope); they join the
  cross-group pass. Its reviewer graded groppe-2025's four Section IV
  challenges LOW as field-level statements, not limits on the paper's
  own experiment. g150 is finalized: gustafson-2024's Outlook says "2 to
  4" times better than Powell where its body gives about 1.4 for H2O,
  so the comparison is LOW. For the cross-group pass:
  qmlhealth-screening-counts is a stored HIGH typed "measured" (a
  setup), and gustafson-hessian-dependence-limit's quote is on p.6,
  not the stored p.7.
  g149 waits on two: gunlycke-2025's gsa-role-of-qpu (an interpretation
  of the QPU's role the paper does not test) and guo-2023's
  guo-qlof-speedup (an asymptotic count that assumes QRAM and a constant
  qubit count per point, with no experiment; its error-bound text says
  4ε1/P where Eq. 32 gives 8ε1/P). Its sign-off added to guo-2024's
  zuchongzhi-vqe-error-mitigation-two-orders that the paper's own Table
  I lists a LiH result with symmetry verification, which its text says
  was not shown. gunlycke-2025's 99.88% fidelity is IonQ's figure for
  its own system, with three IonQ authors, so it is LOW.
  The stored HIGHs typed "measured" though each is a scope, setup or
  stated limit (six in g130, two in g145, six in g148, one in g150)
  need no store change: the result type is not a stored column. It is
  used only while grading, and a confirmed stored row that is not
  rewritten keeps its stored certainty. Each group's dry run passed
  with them, so this cross-group item is closed.
  g154 is finalized: he-2024 runs no experiment of its own, so its
  limits on other authors' work are LOW. g151 is finalized; its
  sign-off typed rbm-ducc-not-chemical-accuracy, a stated limit on a
  measured result, as measured (F135). han-2025 (EnQode)'s abstract
  claims over 90% fidelity where its body reports 89% in ideal
  simulation, and han-2025 (MEDQ)'s "consistently exceeds" is
  contradicted by its own Table 5; both are LOW. g152 waits on one:
  harvey-2023's harvey-classically-simulable states that the models are
  classically simulable but never derives it, so it is graded
  "textbook, stated not proved (F129)". g153 waits on one: haug-2022's
  rm-experiment-setup (the main text and captions say N = 8 qubits,
  Appendix D says N = 9). Its sign-off widened
  haug24-ssvqe-numerics' anchor to pp.23-25, where its quotes sit.
  Every one of Task I's 100 records is read and reviewed.
- **The fresh-eyes review (2026-11-02)** of the uncommitted scripts
  found that g064-r1 re-entered a record refused on 2026-10-15 (its PDF
  then had no text layer) without naming the reversal, which would have
  stopped the live apply; its review now names it. The other findings
  are fixed in the scripts (CHANGELOG). Under the narrowed figure rule
  every Sprint 15 read passes except one g123 value read off an axis,
  corrected at the sign-off.
- **For the hand-download list.** deng-2023-solving-graph-problems-gaussian-boson:
  the local file is the 7-page Letter only; its Supplemental Material
  (its reference [26]) is a separate document not held, so it was not
  read (reader g126's `version_note`).
  gotting-2023-exploring-quantum-mechanical-advantage-reservoir: the
  letter's Supplementary Material (its covariance dimension
  calculation) is not in the local PDF (reader g147).
  gustafson-2024's supplemental hardware calibration data (reader
  g150), and the Supplementary Material of halder-2023 and the
  Supporting Information of halder-2025 (reader g151), are not in the
  local files.
- **Context questions for the team lead.** dell-anna-2025's
  qng-study-scope-toy-model is stored under context "method"; reader
  g125 reads it as "qc" and left it unchanged, as the prompt requires.
- **The trial apply (2026-11-04)** on a copy of the store entered every
  finalized group of Tasks H and I in one apply (the apply takes every
  reviewed group; `--groups` is for a dry run only): 4,947 new
  assertions, 190 read rows, 86 stored assertions updated, 11 records
  set to `read`, 8 applicability rows. A second apply entered nothing.
  Every count is a snapshot as of 2026-11-04. It listed 3 stored
  assertions with a field no review item names, each read by the
  coordinator before the live apply and accepted:
  trojannet-threat-model (claim type "absence" to "positive": the
  quote is the paper's threat model, a positive statement, so the
  stored type was wrong); cranganore-limit-photonic-circuit-model and
  qelm-hardware-not-tested (fidelity "scoped" to "exact": each value
  restates its quoted passage, and its reviewer confirmed it).
  The live apply (2026-11-04, after its verified backup) wrote the same
  lines as the trial; a second apply entered nothing.
- **The cross-group pass (2026-11-04).** Absence items: of the stored
  absence items on "no experiment" or "no hardware run", 9 of 10 are
  HIGH on the paper's own scope after a full read (an absence claim
  stands on its search, ADR-0004 decision Q5). Only g144's reviewer
  graded such items LOW for want of a sentence stating the absence. Its
  sign-off sets gilfuster-no-experiments and
  giordano-no-hardware-run-scope HIGH on scope, and keeps
  pqc-no-experiments LOW (the paper cites "a recent set of limited
  experiments [18]", so the absence is not clean). dees-2023: its
  Lemma 2.4.3 (p.8, proved) gives g(x) = A + B cos x + C sin x, from
  which rule (2.4) follows in one line the paper does not write. If the
  parameter-shift rule is a textbook tool, five stored LOWs could be
  HIGH: theorem-2-4-4-dth-derivative-parameter-shift,
  lemma-3-3-1-complexity-prototypical-loss-p-laplace,
  lemma-3-3-2-complexity-variational-loss,
  lemma-3-3-5-complexity-poisson and
  optimised-parameter-shift-two-versus-three-evaluations (the paper
  derives (2.5) and (2.6) from (2.4) on p.9). Lemmas 3.4.1 and 3.5.1
  (an estimator from [14]) and the two Section 3.6 items (counts
  stated, not derived; "clearly better scaling" not shown) stay LOW
  either way. These are stored certainties, so the team lead decides
  at Manual Validation.

## 65. Textbook-only LOW grades, proposed for the team lead (Sprint 15 Task L, F129)

`manifests/sprint15_f129_proposals.json` lists the stored LOW assertions
whose only stated cause is a textbook fact. F117's cross-group rule
(2026-10-30) says a textbook-standard result is background and does not
by itself make an item LOW; a specific paper's lemma taken by citation
does. Every count below is a snapshot as of 2026-11-01.

- **The cut.** 29 of 15,386 LOW assertions name a standard, textbook,
  background, well-known or classical fact in their certainty reasons
  (vendor and GRADE reasons excluded). The manifest proposes 10 for
  HIGH, keeps 6 LOW, and finds 13 that do not rest on a textbook fact.
  Each of the 10 was read against its passage in the source.
- **The misses.** 30 of the 2,693 theoretical-result LOW assertions
  outside the cut, drawn at random (seed 15): none rests only on a
  textbook fact.
- **Nothing is written to the store** before the team lead decides at
  Manual Validation. A decided change enters through F117's sign-off
  and escalation path, with its own verified backup.
- **Items added since.** Sprint 15's Task H and Task I readers set
  textbook statements given without proof LOW with the prefix
  "textbook, stated not proved (F129)" (section 64). They join this
  list at Manual Validation; the manifest itself is not changed.

## 66. Phase 2's Sprint 30 results, and F166 repointed (Sprint 15 Task M, F130)

Written 2026-11-04, before the apply. Every count here is a snapshot as of
2026-11-04. The team lead chose on 2026-11-04 (Question 1 = 3) to wait for
Phase 2's PR #74 to merge rather than change the local-file check.

- **The read.** Every document read whole at Phase 2 commit 366cf37, PR
  #74's head, through `git show` on the team lead's clone; no fetch
  (F79). The script (`scripts/sprint15_f130_phase2.py`) checks each blob's
  SHA-256 before it reads, so a document that changes before the merge
  stops it. If the merge changes a blob, the script is re-read at the
  merge commit before the apply.
- **Five new records, nine assertions.** F174's IEEE-CIS comparison and
  its seven algorithm documents (one record, three assertions: the
  ranking and its paired tests, recall at the alert budget against its
  capacity, and the proxy's tied scores and train-test gap); F176 (two:
  below greedy on 3 of 6 instances by under 2e-05, and the swap search's
  misses on exact instances); F169 (one: the LightGBM-bins plug-in
  passes F108's rule, with its stated limits); F170 (one: ULB frauds
  every model misses sit among legitimate rows); F171 (two: the
  missed-by-all share on IEEE-CIS against ULB, not shown smaller, and
  its raw-field profile). Every one is HIGH, the project's own
  measurement, evidence tag SIM. Context by section 43's rule: `ml` for
  F169, `hsbc-2026` for the rest.
- **No links.** The plan named `supports` or `contradicts` links to the
  LOW claims each result bears on. No stored claim states the same fact
  whole (ADR-0004 A8 (b)'s rule for a link), so each reason names the
  stored claims it bears on instead: F152's IEEE-CIS lanes and Han et
  al.'s random-split scores (LOW), F166's ULB gap, F160's room check,
  F108's and F114's ceiling failures, and F154's ULB subsets.
- **F166 repointed.** Sprint 30 added TP, FP, TN and FN to F166's eight
  ULB documents (72182b2), so the local-file check read
  ULB_COMPARISON.md as changed: the block behind Question 1. The four
  stored F166 values are verbatim at 366cf37 and confirmed by name; its
  access, evidence and checked_against_source move to 366cf37, with the
  first read (2026-10-30, 6242b8a) kept in the evidence, and a read row
  is added. Sprint 14's F120 apply would have put the old evidence back,
  so it now leaves a record re-read at a later commit alone (proven red).
- **Checks.** Trial on a copy of the store first (5 records, 9
  assertions, one read and one repoint; a second apply wrote nothing;
  F120's apply wrote nothing; all six records pass the local-file
  check), then live with its verified backup.
- **The fresh-eyes review (2026-11-04)** found no blocking defect and
  every figure right. Fixed before the apply: five values that dropped a
  limit their document states (F170's "in every seed in which they are
  test rows" and its 12 mixed frauds; F174's tied scores flagged past
  the 427-row budget; F171's 1,708-alert step to 42%; F171's profile,
  which borrowed a sentence about the cross-data-set comparison and
  missed its 5,264 rows); one reason that overstated F152 (XGBoost
  against logistic regression is months 4 and 5 only); a rerun now
  syncs a corrected value instead of skipping it, and never moves F166
  back from a later repoint (proven red); the run-file test checks all
  seven gaps, since the quote check reads the eight documents joined.
  F166's stored recall value is kept as it stands: Sprint 30's matching
  tie note (the proxy up to 297 rows against 284) is named in the
  repointed evidence, and the recall range it states is unchanged.
- **The merge and the apply (2026-11-04).** PR #74 merged as 43bc362,
  a merge commit whose parents are develop (af03165) and the PR's last
  head (a428b92); 366cf37 is its ancestor, and none of the 27 files the
  script reads changed after 366cf37, so the script names 366cf37
  unchanged. Trial on a fresh store copy (5 records, 9 assertions, one
  read, one repoint; a second apply wrote nothing), then live with its
  verified backup; a second live apply wrote nothing. The first live run
  of the store test failed on its own comparison (a sqlite3.Row against
  a tuple, never equal); fixed and proven red by injection.
- **Older checks the Sprint 15 full reads broke**, found by the full
  suite while the merge was pending (2026-11-04): Sprint 9's F46 apply
  now leaves a record a later full read owns alone (it would have undone
  F114's correction of faryad-state-prep-omega-2n-dimension-count); F80's
  refusal test accepts a refused record a later full read took (qci-2026,
  read whole by OCR); the spelling fixer protects the stored id that
  section 64 names with a British spelling.

## 67. Sprint 15 Manual Validation: the team lead's decisions applied

Written 2026-11-04, before the apply. Every count here is a snapshot as of
2026-11-04. The team lead answered the hand-over the same day:

- **Q1 = 1: the 36 certainty changes as proposed** (33 HIGH to LOW, 2
  MODERATE to LOW, 1 LOW to HIGH: derieux-parameters on "setup"). Each is
  recorded in its group's escalation file
  (`work\f114\review\escalations\<g>.json`) with the team lead's words,
  which lets the 24 groups that held them (g115 to g153, about 114
  records) be finalized and applied by `scripts/full_read_apply.py`.
  - **Rebuilding a regraded stored row needs its value and quotes.** A
    stored HIGH lowered to LOW is rebuilt by the applier, and eight
    readers' confirmed entries carry neither: finalize refused them ("no
    value"), and the apply refused four ("no quote"). Each got its stored
    value as a `value_replace` and its stored quotes as `extra_quotes` in
    its group's sign-off, unchanged from the store, so only the grade
    moves.
  - **A sign-off edit on a figure reading keeps its figure exemption.**
    The applier checked a `value_replace` on a value read from a figure
    without the "about N" exemption its own quote check gives, so five
    such edits were refused. Fixed in `verify()` (a test proven red). Two
    rydberggpt edits named the models M1 to M3, which no quote holds;
    their values now say "a model" and "each of the three trained
    models".
- **Q2 = 1: F129's 10 proposed HIGHs set HIGH**, each on the basis its
  proposal names (section 65), by `scripts/sprint15_mv_decisions.py`.
- **Q3 = 2: dees-2023's five parameter-shift LOWs stay LOW.** Nothing is
  written.
- **Q4: g144's two absence items are MODERATE** (the team lead: "Make
  both MEDIUM, as the reviewer graded them, because neither paper states
  the absence itself"; the store spells MEDIUM `moderate`).
  gilfuster-no-experiments and giordano-no-hardware-run-scope go back to
  the reviewer's LOW in g144's decisions (the cross-group pass's HIGH is
  kept in `g144.before_mv.json.bak`), are entered LOW, and the script
  raises them to MODERATE.
- **Q5 = 1: carded as F137** (the two Dunjko records share one PDF).
- **Q6 = 2: qng-study-scope-toy-model moves from `method` to `qc`**, by
  the same script.
- **Q7 = 2: Sprint 16's F57 release follows F57's ranking** (F57's card).
- **Q8 = 2: dalzell-2025's eight "split recommended" values stay single
  LOW assertions.** Nothing is written.
- **Q9 (the applier's quote check): carded as F136.** The applier checks
  every reviewed row's quotes before each apply, though most are stored
  as their review wants them: about 23 minutes for Sprint 15's 47 groups,
  most of it on rows it does not write. The team lead: "We need to updat
  the rule as it violates the 'Long-term Effective, while as efficient as
  reasonalby possible' primary rule".
- **A slip, and its fix.** The first trial copied the store but not its
  text cache, which sits in the store's folder, so it extracted every
  source again (894 files in 25 minutes) before it was stopped; the
  trial copies `text_cache\` with the database from now on.
- **A rebuilt confirmed row keeps the fields no review names.** The
  trial (2026-11-04: 6,282 new assertions, 228 read rows, 157 updates)
  listed 8 rows with an undecided field: six regraded rows had taken the
  reader's fidelity ("exact" for the stored "scoped") and three the
  reader's claim type ("positive" for the stored "absence", losing the
  search scope). The applier wrote a confirmed entry's fidelity, claim
  type and search scope from the reader's file, although only its quotes
  or grade were rebuilt. It now keeps the stored ones for a confirmed
  entry (a test on a store copy, proven red); a corrected or narrowed
  entry still takes the reader's whole entry.
- **Checks.** Trial on a store copy first, then live with its verified
  backup. The fix above changes only the rows the trial listed, so the
  live apply ran without a second 23-minute trial; its log is compared
  with the trial's, line for line, and lists no undecided field (it
  matched: 6,282 new assertions, 228 read rows, 157 updates, 0
  undecided). The decisions script's second run writes nothing.
- **A slip in the decisions' date, and its fix.** The script first ran
  dated 2026-11-04, the review day of g144, just after midnight. A
  rerun of the applier would then have put g144's two items back to LOW,
  because `sync_assertion` refuses a sync only when it is dated before a
  row's last change. The store was restored from the backup the script
  took (`scripts/restore_store.py`), and the script was run again dated
  2026-11-05, the day it was applied. A test proves that a rerun of the
  applier leaves all 12 regraded rows alone (proven red with the date put
  back).
- **The fresh-eyes review (2026-11-05)** found no blocking defect, and
  that the date alone protected the 12 rows: a review of their groups
  dated later would have written its LOW back. The applier now keeps a
  stored grade whose reasons carry "the team lead's decision at" unless
  the review's own reasons carry it too (exactly these 12 rows today; a
  test proven red). A confirmed row that keeps a stored
  "vendor-self-claim" type is refused if its review graded it HIGH (no
  such row today). The figure test's second half now calls the edit
  check itself, since verify's quote check refused that case first.
- **The `--changed` run after the apply (2026-11-05)** failed 5 of
  1,086. One was a real defect: a rerun of `sprint12_reading.py`, dated
  2026-10-23, would move qng-study-scope-toy-model's context back from
  `qc` (Q6 = 2), because the sync's date guard held only full-read rows
  and that row's decision note carries no grade phrase.
  `store.ingest.sync_assertion` now refuses any sync dated before the
  row's latest note of the form "YYYY-MM-DD (Sprint N Manual Validation"
  (`decided_day`), or a note whose body says "the team lead's decision
  at Sprint N Manual Validation" (Sprint 8 and 9's shape, added at its
  fresh-eyes review): 24 assertion rows, a snapshot as of 2026-11-05.
  The tests of every script that syncs those rows pass (100 tests). Three were older tests pinned to data the decisions and
  the full reads changed (the learnings balance after g133's decision,
  F101's re-quoted oversampling record, the Sprint 12 store test), and
  one was the applier's field test, which passed a namespace where the
  confirmed-row rebuild needs a dataclass. Each fix that guards a rule
  was proven red by injection.

## 68. Each PDF's text extracted once, each quote checked once (Sprint 16 Task A, F136)

Team lead, 2026-11-05: "This reading the PDF should ever be done once per
PDF, ever, and once done should never need to read it again. The quotes
only need to be verified once per PDF, ever, and should never need to be
done again." Counts are a snapshot as of 2026-11-06.

- **The rule, as it now reads: every write is checked; an unchanged row
  is not.** An assertion's quotes and value are checked against the
  source text (`require_verbatim`) once, before the write that stores
  them. A rerun, a second apply or a later sprint that would store them
  exactly as they are checks nothing and reads no source. "Exactly as
  they are" means the same quotes, the same value as the sync would
  write it (after common names), and a row that a full read of the same
  paper wrote. A new assertion, a changed quote or value, and a row an
  earlier partial read stored (from an abstract or another copy) are
  checked once, against the full read's source, as before. No test
  re-checks every stored quote; the guarantee is the check at each
  write (fresh-eyes review: an earlier draft of this section claimed
  such a test).
- **One text cache for every store copy.** `store.text_cache_dir()` is
  the live store's `text_cache\`, or `EBDB_TEXT_CACHE_DIR`; it no longer
  follows `EBDB_STORE_DIR`, so a trial on a store copy reads the same
  cache (Sprint 15's first trial extracted 894 PDFs again, about 25
  minutes). The OCR engine's folder is fixed the same way (its path is
  part of the OCR cache key). This replaces "the trial copies
  `text_cache\` with the database" (section 67).
- **The applier.** `scripts/full_read_apply.py`'s `verify(conn)` skips
  the quote check for a row stored with the same quotes and value
  (`store.ingest.checked_when_stored`) and reads a source only for the
  rows it checks. The checks that read no source (figure readings, the
  image-file HIGH rule, the record rules) still run on every row. Each
  run prints how many quotes it checked and how many it found stored as
  written.
- **Measured on a store copy (2026-11-06)**: a re-apply of every applied
  group checked 0 quotes and read 0 sources, in about 15 seconds. With
  the change removed, the same re-apply checked 30,113 quotes and read
  740 sources, in 554 seconds.
- **Checks.** Three tests, each proven red by injection: a store copy
  elsewhere reads the same cache; only a new or changed quote is checked
  (and a changed quote not in its source is still refused); a re-apply
  on a store copy checks no quote and reads no source.
- **Not changed.** `store.ocr.page_texts`' page-by-page fallback (for a
  PDF whose form feeds disagree with its page count) and `pdfinfo`'s page
  count still run once per process, not once ever. F139 measures them
  before anything is changed.

## 69. Read once, check once, write once: the read measured (Sprint 16 Task B, F139)

Team lead, 2026-11-05: "be as efficient as reasonably possible (total
time per page, per paper), total token usage per paper, only test what
must be tested, only test once, only read once, only write once, only
update the database once, only red test once". Every count below is a
snapshot as of 2026-11-06.

- **Telemetry, one file per group.** `scripts/read_telemetry.py` keeps
  `manifests/sprint16_f114_reads/telemetry/<group>.json`: the group's
  papers and their pages (`start`, from the brief), each reader and
  reviewer by task id with the tokens and minutes its completion notice
  reports (`agent`, entered by the coordinator), and each step that
  touched the group (the reader check, a render, the dry run, the trial,
  the apply) with the quote checks it ran, the text-cache misses it
  caused, the pages it rendered and the assertions it wrote (entered, or
  with a changed quote or value; an apply's read rows and access notes
  are not counted). The checker and
  the applier record a step only with `--telemetry`, so a test run never
  writes into a group's file. `report` computes the totals and the
  per-page figures each time; nothing is stored as a total. A field no
  step measured is "unknown", never 0. Tokens and minutes belong to an
  agent, which reads a whole group, so they are per group and per page,
  and per paper only where a group holds one paper.
- **The Sprint 15 baseline** (`read_telemetry.py baseline`, in
  `telemetry/baseline_sprint15.json`): 47 groups (g062-r1, g064-r1,
  g076-r1, g113-r1, g114 to g154, g331, g332; 13 folders in the same work
  folder were Sprint 14's and are left out), 209 papers, 6,108 PDF pages
  (2 papers are web pages, with no page count), 2,190 page images
  rendered. Readers: 22,265,688 tokens and 2,705 minutes; reviewers:
  10,239,461 tokens and 856 minutes. Per page: 3,645 reader tokens and
  1,676 reviewer tokens; 0.44 reader minutes and 0.14 reviewer minutes.
  Per paper: about 106,500 reader tokens and 49,000 reviewer tokens. One
  g122 reader failed, and a failed agent's notice carries no usage, so
  the reader sums are a lower bound by that agent's use
  (`reader_agents_without_usage`).
  Sources: the session's completion notices for tokens and minutes; the
  briefs and pdfinfo for pages; each group's work folder for images and
  for a second minutes figure (the span of its file times). A resumed
  agent's notice repeats its total tokens, so the last is kept; its
  duration can cover only the last leg or include the wait, so the
  minutes are approximate. One reviewer read two groups and is split
  evenly between them. Each notice is parsed on its own: the first
  version read a whole transcript line, and a background command's notice
  before an agent's on the same line counted g134's reviewer twice
  (fresh-eyes review; corrected before commit). Quote checks, cache
  misses and assertions written were not counted in Sprint 15:
  "unknown".
- **Each "once", where it stands:**
  - *Extract once*: in place (section 68), and now in the reader's check
    too. Its page check ran one uncached `pdftotext -layout` per anchor:
    58 of 62 seconds on g129 (494 assertions). Each page's two layouts
    now come from the cached whole-file extractions
    (`store.ocr.page_layouts`), and the OCR pages are looked up once per
    file. g129 now checks in 6 seconds (75 to 95 before), g120 in 4 (16
    before). Every Sprint 15 group still reports 0 problems except g123,
    whose 1 problem is the same line as before the change; g330 (a Sprint
    14 group) also prints the same 9 lines as before.
  - *Check each quote once*: in the applier, in place (section 68). In
    the reader's check, named and not built: a whole group now checks in
    3 to 22 seconds (all 60 groups in Sprint 15's work folder: 479
    seconds together), so a record
    of passed quotes would save seconds a run, and it would add a new
    maker of `Verified` fed by a reader's own files. The remaining fixed
    cost is pdfinfo's page count, about 0.6 seconds per PDF per run.
  - *Read once*: named and not done. The reviewer keeps the full second
    read (Sprint 16 plan, Q5 = 2).
  - *Render once*: in place. `scripts/render_page.py` renders a page once
    per file, page and resolution into the text cache's `pages` folder,
    and the reader and the reviewer prompts both use it at 100 dpi (the
    reviewer used 110, so no image could be shared). The saving is
    pdftoppm's time; an image costs the reviewer's tokens either way. A
    crop of one panel is not cached.
  - *Write once*: one apply per sprint. The trial on a store copy still
    runs before every apply, not only when the applier changed: the
    "undecided" lines (a stored field changed that no review item names)
    are computed only from an apply's log, so the trial is where they are
    read before the live apply. Since section 68 a trial re-checks no
    stored row (a re-apply of every applied group took about 15 seconds
    on a copy); only the new rows' quotes are checked.
  - *Test once*: `scripts/run_suite.py --changed` runs the tests a change
    touches and adds the 61 store test files only when the store changed.
    Narrowing those to "the tests that read the rows written" is named
    and not done: a store test checks a rule over every row, so no test
    can be left out by the rows a write touched. They run once after the
    one apply.
  - *Red-test once*: in place. Each new guard is proven red once at the
    commit that adds it and says how in its docstring
    (`tests/test_guard_discipline.py`).
- **Checks.** Five tests, each proven red by injection: an unmeasured
  field is "unknown", never 0; a repeated notice replaces the first and
  steps add up; the reader check and the applier record their steps; the
  Sprint 15 baseline counts each agent once; a page is rendered once. One
  more on the reader check: its page check runs no extraction per
  anchor. Not tested: the applier's trial-or-apply label, which compares
  the store path with the default; a live store moved with
  `EBDB_STORE_DIR` would be labeled a trial.
- **Still to come (Task B step 3).** The measures on F114's first Sprint
  16 group, set beside this baseline in the status note before the other
  groups start.

## 70. Table cells that hold only a number, and a stated limit's type (Sprint 16 Tasks C and D, F134 and F135)

- **F134, the cells.** `store.quotes.plain` drops each line that holds
  only a number, so a quote may cross a page break (the page number sits
  on a line of its own). The text layer without layout puts each table
  cell on a line of its own too, so a cell such as 881 was dropped, and
  a quote through a table's row could not be found (readers g115 and
  g120, Sprint 15). A PDF's text now holds a third form
  (`store.quotes.cells_text`): the text without layout with its
  number-only lines kept, except a page's first and last non-blank line
  when it holds only a number, since that is where a page number sits.
  It comes before the OCR part, and the reader check's page check holds
  the same form for each page. The page number is still dropped from all
  three forms, so a quote across a page break is found as before and a
  quote cannot carry a page number (the first version kept every number
  line; the fresh-eyes review found that a quote, and so its value,
  could then hold a page number). A table cell that is a page's first or
  last line is still dropped. The change only adds text a quote may
  match, so no stored quote can stop matching; the live quote tests
  confirm it at the full suite.
- **F135, a stated limit's type.** Reader g118 typed five stated limits
  on measured results "theoretical", "claim" or "setup", because the
  reader check refused a high suggestion on a "measured" result. The
  review prompt has said since Sprint 15 that such a limit is HIGH on
  "stated limit" whatever its type. Now the check agrees: a "measured"
  result may be suggested high only on `high_basis` "stated limit", and
  the Sprint 16 reader prompt says to keep the type "measured" and never
  change it to pass the check. What a measurement found, even a negative
  finding or a failure, is a result, not a stated limit, and stays low;
  the Sprint 16 review prompt's definition of "stated limit" now says the
  same (Sprint 15's listed "failure" among stated limits). The check is
  weaker by design: it passes any measured "high" on "stated limit",
  limit or not, and the review judges it. The applier grades from the
  coordinator's decisions, never the reader's suggestion, so no grade
  changes by this.
- **Checks.** Four tests, each proven red by injection: a cell is found
  and a page number still dropped; the page check finds a cell on its
  page; a stated limit keeps its type while another measured HIGH is
  still refused; the prompt and the check agree.

## 71. The two Dunjko records held as one (Sprint 16 Task E, F137)

- **The finding.** `dunjko-2017-machine-learning-artificial-intelligence-quantum`
  (arXiv 1709.02779) and
  `dunjko-2018-machine-learning-amp-artificial-intelligence` (DOI
  10.1088/1361-6633/aab406, Reports on Progress in Physics 81(7), 2018)
  are one paper: the preprint and its journal version. Their local copies
  are one byte-identical PDF (SHA-256 7aa572f736a826a0...). The team lead
  chose to hold them as one record (Q6 = 1, 2026-11-06).
- **The merge** (`scripts/sprint16_f137_dunjko.py`, dry run by default,
  `--apply` after a verified backup). It refuses unless the two local
  copies hash the same. dunjko-2018 keeps the paper and adds
  `arXiv:1709.02779` to its access, after the DOI (the DOI still
  resolves its citation). Each of dunjko-2017's assertions moves to
  dunjko-2018: its yield row and the record id in its provenance, with a
  note in its updated_reason. The anchor and the quotes stay as they
  were, since the PDF is the same. dunjko-2017 is closed as a duplicate,
  as the Lin duplicate was (F33): tier `seen`, a disposition that names
  dunjko-2018, and a `superseded-by` source link. Its reads,
  applicability and found-via rows stay as its history. A second run
  changes nothing.
- **Routes.** dunjko-2017's two found-via routes (QMLPapers and
  Roadmap-to-QML at a239747648) are copied to dunjko-2018, each with a
  note: each list linked arXiv 1709.02779, which dunjko-2018's access now
  holds. F104's test requires every record that holds a listed id to
  carry the list's route, and it went red on the first gate until the
  copy was made.
- **Later reads.** Two older reads name dunjko-2017: g131 (Sprint 13
  Task G) and Sprint 11's task G (group g03). `store.merges` names the
  merge (`MERGED_INTO`, `holder()`, `promotes()`), and both appliers
  (`scripts/full_read_apply.py` and `scripts/sprint11_reading.py`) ask
  it: such rows are entered, checked and owned under the record it was
  merged into, and a merged record's tier is never set back to read.
  The first gate found the Sprint 11 applier: its rerun set dunjko-2017
  back to read and its provenance back to dunjko-2017. Its test now
  checks the tier of the record that holds the rows.
- **Trial on a store copy** (2026-11-06): 69 assertions moved; a second
  run changed nothing; the applier's dry run and apply after it wrote
  nothing new, and no provenance named dunjko-2017. Counts are a
  snapshot as of 2026-11-06.
- **Applied live** 2026-11-06 06:08, after a verified backup
  (`evidence-20261106T060806262630-sprint16-f137-dunjko-records-merged.db`):
  69 assertions moved; the two routes were copied by a second apply at
  06:49, after its own verified backup
  (`evidence-20261106T064905128225-sprint16-f137-dunjko-records-merged.db`).
  The script also refuses to finish if any
  assertion still names dunjko-2017 in its provenance after the move,
  so an assertion with no yield row cannot stay behind unseen (fresh-eyes
  review).
- **Checks.** Three tests. Two unit tests were proven red by injection:
  a merged record's row is held by the record it was merged into (with
  `holder` returning the record itself, the row's owner named
  dunjko-2017); and a merged record is never set back to read by either
  applier (with the merge condition removed from `promotes`, dunjko-2017
  at seen was promoted; added at the fresh-eyes review). Both were
  proven red again after the functions moved into `store.merges`. The live test
  (`live_store`) was red before the live merge (dunjko-2017 at tier
  read) and is green after it; it checks the end state, including the
  local-file check passing for both records.

## 72. F114's new papers for Sprint 16: the list's 6 and the team lead's 2 (Sprint 16 Tasks F and G)

Every count is a snapshot as of 2026-11-06. Written before the applies.

- **The list, at one commit.** Roadmap-to-QML read at commit
  `399b022651` (pushed 2026-11-05; the head on 2026-11-06). Between
  `ea6f42a7c0` (section 57) and it, only `2026/2026.md` changed, by 6
  added lines. So that one file was fetched, and the other 12 were copied
  from the `ea6f42a7c0` copy; each copy's git blob hash was checked equal
  to its blob at `399b022651` first. The copies are under
  `References\Roadmap-to-QML_399b022651\`, outside git; the manifest
  `manifests/sprint16_f114_roadmap.json` records each file's SHA-256.
- **6 papers new to the store, all linked in `2026/2026.md`.** 4 arXiv
  ids (2610.42029, 2611.00272, 2611.00303, 2611.05079) and 2 Quantum
  journal papers by DOI (10.22331/q-2026-10-20-2239 and
  10.22331/q-2026-10-29-2256). Each enters through the door at `seen`
  under `qml`, with a route naming the list at `399b022651`. A Quantum
  link was carried before (F104 entered arXiv ids only); Quantum is open
  access, so `scripts/sprint16_f114_roadmap.py` now enters a new Quantum
  link by its DOI with the journal's PDF. Neither Quantum paper is held
  under another id: a title search of the store found none (F137's
  lesson); the script now refuses a Quantum entry whose title the store
  already holds (fresh-eyes review). The 20 other links are carried, as
  at section 57.
- **Free copies: 6 of 6.** The arXiv PDFs came through F104's paced
  fetcher (each carries its arXiv stamp on page 1); the Quantum PDFs came
  from `quantum-journal.org/papers/<id>/pdf/`. Each is named with its
  SHA-256 in `evidence`.
- **The team lead's 2 named papers (Task G, F57; Q2 = 2, Q3 = 1)**, from
  `manifests/sprint16_f57_named.json` through `build_record`, by
  `scripts/sprint16_f57_named.py`:
  - QBoost for regression (Goes et al., arXiv 2108.13346, v1, the only
    version), api-origin, from its local copy.
  - The wangy8205165 white paper, "Quantum Neural Networks: Theory,
    Architectures, and Applications" (29 pages), hand-origin: it has no
    DOI or arXiv id, and the PDF names no author, so the citation names
    the GitHub account and the commit. Its local copy's git blob
    (8f800932c0) is `Quantum_NeuralNetwork.pdf` at the repository's head
    commit 920c11c (2026-10-26). A `code-of` source link from the
    repository record (which holds the paper's LaTeX source and PDF) to
    the paper record. The repository record's disposition, which said it
    was linked to no paper, is corrected, with a note (fresh-eyes
    review). `scripts/sprint12_f103_intake.py` entered that record, so
    it holds the corrected text and Task G's script reads it from there;
    F103's test now allows that one link. A re-run finds each entry by its id or its access before
    any metadata request.
- **Reading.** The 8 are read in full by local readers under
  `manifests/sprint16_f114_reads/READER_PROMPT.md`, as two new ledger
  groups after g332: g333 (the 4 arXiv papers and the first Quantum
  paper) and g334 (the second Quantum paper and the 2 named papers).

## 73. F114 at 20 papers, under Sprint 16's prompts (Sprint 16 Task F)

Written 2026-11-06, before the apply; the counts that enter are added
when it runs. Every count here is a snapshot as of 2026-11-06.

- **What is read.** 20 papers, each in full, figures included
  (`scripts/sprint16_f114_local.py` writes the briefs and adds g333 and
  g334 to the ledger), in the plan's order:
  - g333 and g334: section 72's 8 papers;
  - then 12 from the ledger, from the first group not yet read in full.
    Each reviewed group's unread record that has a file re-enters (F125):
    g133-r1 (emmanoulopoulos-2022 and evans-2024) and g154-r1 (the four
    he and heese records Sprint 15 left at its 100). Then g155 (5) and
    g156's first record (henriet-2020); g156's other four wait for the
    next release.
  - Left out, as in Sprint 15: g069's and g072's unread saved web pages
    (no article), and the records whose source is a directory (three
    OpenCyc releases, ds3lab-feebee, the fraud-detection handbook). No
    book falls in the 12 (Q7: Simeone 2022 and Cichocki 2016 went to
    F138).
- **The readers.** Local first-pass readers (Sonnet 5.5) under
  `manifests/sprint16_f114_reads/READER_PROMPT.md`, one per group, each
  given its prompt with the group filled in. g333 runs first and alone:
  its telemetry is Task B's step 3, the measure against Sprint 15's
  baseline, recorded before the other five start.
- **The review.** One Sonnet 5.5 reviewer per group under
  `manifests/sprint16_f114_reads/REVIEW_PROMPT.md`; the reviewer reads
  each paper in full (Q5 = 2). `f117_review.py items` now also writes
  each paper's review text (`work\f114\texts\<record>.txt`), which
  Sprint 15 wrote by hand: its pages separated by form feeds, a thin page
  replaced by its OCR text. On 2026-11-06 it reproduced three of Sprint
  15's texts byte for byte (checked by hand with a scratch comparison,
  not by a test: the test uses made-up pages). `finalize` names Sprint 16's tag and prompt for
  these six groups (their reads carry `figure_count`, as Sprint 15's do,
  so they are told apart by group).
- **The apply.** `scripts/full_read_apply.py --telemetry`: a dry run,
  a trial on a copy of the store, then live with its verified backup; a
  second apply enters nothing. Every certainty change on a stored
  assertion waits for the team lead.
- **What ran (2026-11-06).** All 20 papers (531 pages) were read in full,
  and each group's check printed 0 problems. Five of the six groups are
  applied, each with its trial, its live apply after a verified backup,
  and a second apply that wrote nothing: g333 (515 assertions), g334
  (198), g133-r1 (125 changes), g155 (257 changes) and g156 (61 changes).
  g154-r1 (4 papers, 76 items decided) waits for one certainty change
  (`he-simulation-scope`, stored HIGH, proposed LOW) that the team lead
  decides; it applies after that answer. Counts, before the first apply
  (backup at 11:56) and after g155's: assertions 34,897 to 36,041
  (HIGH 11,071 to 11,431; LOW 23,726 to 24,510); papers at `read` 1,805
  to 1,813 and at `seen` 562 to 554 (the 8 new papers; the 12 ledger
  papers were already at `read`).
- **g154-r1, after the team lead's answer** (Manual Validation Q1 = 3,
  2026-11-06: split). `he-simulation-scope` gave two reasons as one: the
  three-class reduction is "Due to the high computational cost of
  simulating large-scale quantum systems", and the 100 samples per class
  are "To simulate real-world data scarcity". It now holds the first
  only (HIGH, stated limit; anchor corrected to p.11), and
  `qgan-training-testing-100-per-class` holds the second (HIGH, setup).
  The coordinator added that item to the read and recorded both
  decisions and the sign-off edits; trial, live apply after a verified
  backup, and a second apply that wrote nothing: 167 assertions entered
  and 8 changed. Assertions after it and Task H's seventh: 36,209
  (HIGH 11,491; LOW 24,618).
- **What the review found.**
  - g333's first reviewer graded Monaco's 70-page supplement from its
    statements and a citation search, not line by line. Two fresh
    reviewers then read every proof (49 and 45 items); 13 of the 94
    decisions changed (14%). A long proof appendix is split across
    reviewers by page from the start.
  - The dependence rule, as applied: a result whose proof reaches a
    specific other paper's theorem, even through the paper's own lemmas,
    is LOW, and its `why` names the cited result.
  - The coordinator's sign-off changed two grades: Monaco's
    `supp-e2a-tight-frames-coefficients` (the value drops the condition
    kappa < 1) and Henke's `henke-dwave-parameters` (the value says 100
    microsecond anneals for the D-Wave runs, but the Figure 3 run used
    20). Both are LOW.
- **The telemetry** (`python scripts/read_telemetry.py report <group>`).
  Per page over the 20 papers: readers 4,633 tokens and 0.75 minutes,
  reviewers 3,224 tokens and 0.24 minutes. Sprint 15's baseline is
  3,645 and 0.44 for readers, and 1,676 and 0.14 for reviewers. Every
  group had 0 text-cache misses, and every second apply checked no quote,
  so the repeated script work is gone. The agents' own reading is the
  cost, and it did not fall. The report first counted a trial's writes
  and the empty re-applies too; `totals` now counts only live writes
  (`tests/test_f139_telemetry.py`).
- **A table the text layer flattens.** Heimann's Tables IV and V are in
  the text layer as rows of numbers with no row labels. Their numbers are
  in the read's figure entries, not in assertions: a cell can be matched
  to its ansatz only on the rendered page.

## 74. The CVQBoost findings record and its seven assertions (Sprint 16 Task H, F51)

Written 2026-11-06, before the apply. Every count is a snapshot as of
2026-11-06.

- **Released from HOLD** (team lead, Q4 = 1). The hold waited for a
  re-run that Phase 2 does not hold; Phase 2 cites the document as a
  planning reference only.
- **The source.** FourierWall2's working document "Maximizing
  Predictions from CVQBoost: Cumulative Findings", last updated
  2026-08-04. Its two copies (`References\` and FourierWall2's
  `docs\`) both hash to SHA-256 `425358a7b4cec71f...` on 2026-11-06; the
  script refuses to run if either differs. Read in full on 2026-11-06,
  sections 1 to 12 and every table.
- **Authorship** (the handoff's decision 1, still open). The document
  names no author. F51's card says the authorship is settled by
  provenance, not by attribution. So the record
  (`fourierwall2-2026-maximizing-predictions-cvqboost-cumulative-findings`)
  cites the FourierWall2 campaign and names no person; its route cites
  the title. The `References\` copy's file name carries a name; the
  evidence says it is the collector's label, not an attribution.
- **The six assertions** are the handoff's
  (`05-sprint-script-draft.py`). Each value is rewritten so that every
  figure in it is in its own quotes, which the quote check requires. The
  rewrite drops two figures the drafts' quotes did not hold: the
  relaxation runs' AUROC pair and QPU seconds (section 9's table). Each
  is graded LOW, "measured result": each is one study's single run on
  one seed, and the document itself says "single stochastic runs". The
  handoff's 2026-09 HIGH grades predate `store.grading` (Sprint 12),
  under which a measured result is LOW; each reason says why. The
  in-segment overfitting assertion keeps the draft's note that the
  section's "3-8x" summary disagrees with its own table (ratios about
  83, 7.6, 8.2 and 1.7).
- **Applicability**: `platform:dirac-3` (sections 3 and 4) and `method`
  (section 2, the handoff's decision 4.1). The five Dirac-3 assertions
  are classed "not addressed" against the Dirac-3S guide in
  `scripts/sprint8_f65_dirac3s_reading.py` (F65's rule: each new Dirac-3
  assertion is classed when it is entered); the guide does not cover
  CVQBoost's tuning.
- **Phase 2's two records on the in-segment wins** (sections 6, 10 and
  11): B4's Dirac-3 replication
  (`cvqboost-in-segment-edge-negative-on-device-spectra-b4`: no
  in-segment advantage on any scoreable cell) and F162 (a proxy, not the
  device, over ten seeds on three cells, label target only: no in-pocket
  win repeats reliably). None of the six states a win, so no
  `contradicts` relation is written; the record's evidence names both.
  The shallow-learner assertion's loss is against a win at the default
  configuration, and its reason says so.
- **The seventh assertion** (team lead, Manual Validation Q2 = 1,
  2026-11-06). `cvqboost-tuned-in-segment-wins-single-run` states
  section 10's headline: on the tuned rollout (one run, seed 20260804),
  CVQBoost led inside the segment on ROC-AUC in 5 of 7 valid cells and
  on PR-AUC in 6 of 7 (the document's count, which takes a tie at 1.000
  on energy_steel target_real as a lead), and on the whole test set won
  ROC-AUC 2 of 8 and PR-AUC 3 of 8, with section 11's caveat that the
  edge is fragile and needs repeats. LOW, measured result. The fresh-eyes
  review moved the caveat from section 6, which states it for the
  untuned baseline, to section 11, which states it for this rollout. Its reason names B4 and F162, which did not find
  such wins. Neither is linked as `contradicts`: B4 compares the segment
  against a matched random segment, not against XGBoost, and F162 runs
  the proxy over three cells with XGBoost at library defaults, so
  neither repeats this configuration on the device. Classed "not
  addressed" against the Dirac-3S guide (F65). Trial, live apply after a
  verified backup, and a second apply that wrote nothing.
- **Fresh-eyes review** (after the first apply, 2026-11-06): the F162
  wording was narrowed to its limits and B4 named; the route's
  name-bearing citation was replaced by the title; the num_samples
  finding typed `positive` (an `absence` is a search of the source, and
  this is a run); the overfitting note restored; the leak assertion's
  fidelity set to `scoped` (its value leaves out "or vice versa"). The
  re-apply synced each, after its own verified backup; a further apply
  writes nothing.
- `scripts/sprint16_f51_cvqboost.py`: a dry run checks every quote;
  `--apply` takes a verified backup; a second apply writes nothing.
  `tests/test_sprint16_f51_cvqboost.py`.
