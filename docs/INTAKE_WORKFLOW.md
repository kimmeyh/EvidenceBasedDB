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
