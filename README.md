# Evidence Based DB

A store of **assertions, acronyms, technical terms and papers**, each carrying
provenance and a derived certainty. Private.

Its first consumer is the HSBC quantum fraud submission
(`github.com/kimmeyh/hsbc-quantum-fraud-2026`, public). The target scope is a
domain knowledge base over quantum machine learning, machine learning, quantum
computing, and the major quantum computing platforms.

## Why it exists

Not in principle. From defects the consumer repository actually shipped:

| Defect | What happened |
|---|---|
| `0.7688` | Quoted in four documents as a measured AUPRC. It appears in **no artifact** -- the mean of an exploratory five-seed run, carried into a ten-seed write-up |
| "twelve amendments" | A letter asserted twelve while the enclosure had seventeen |
| 78 vs 91 | The same variable count read 78 in three places and 91 in two, in one submission |
| `0.5739` | A real number from the wrong file, quoted in a sentence about a different fold |
| `949` | One device limit, restated **nine times** in one document |

Each was caught by a human reading, or by a script written for that one check.
Every one is the same shape: **a value maintained in several places, where one
moved and the others did not.**

## The design in five lines

- **The assertion is the unit.** A paper is a SOURCE of assertions, not a record
  in itself. Four papers cited in the consumer's submission yielded at least
  eight separately checkable claims.
- **Provenance is mandatory.** A record that cannot say where its value came
  from is the defect this exists against.
- **Determinate facts are computed, never stored.** If a command can answer it,
  the database holds a resolver.
- **Certainty is derived, with named reasons** (GRADE). `62%` cannot be argued
  with; "started low, position paper; upgraded one level for admission against
  interest" can.
- **Contexts, not tags.** `world`, `ml`, `qc`, `qml`, `platform:dirac-3`,
  `method`. Shared assumptions factor out, which is why "dynamic range" can mean
  different things on different hardware without contradiction.

Full design: [`docs/adr/0004-evidence-based-db.md`](docs/adr/0004-evidence-based-db.md)
and [`docs/adr/0005-reference-library.md`](docs/adr/0005-reference-library.md).

## Status

**Early innovation.** Both ADRs are Accepted AND expected to change. Nothing is
built yet; this repository currently holds the methodology, the design, and the
research behind it.

The first real test is the **20-paper checkpoint** that both ADRs carry: which
fields were never filled, which were filled identically every time, what we
wanted to record and had nowhere to put, and above all **how long team-lead
adjudication took per record**. That last number is what the whole design is
constrained by, and it is unknown.

## Papers are not here

**Records, never PDFs.** Most published papers are not redistributable and
several in the seed set are vendor or conference material. The `access` field
points at a DOI, an arXiv id, or a local path.

**Two directories, deliberately distinct:**

| Path | What it is |
|---|---|
| `D:\Data\Harold\github\EvidenceBasedDB\` | This repository. Version-controlled |
| `D:\Data\Harold\EvidenceBasedDB\` | Not a repository. Material connected to the solution that never gets committed |

The second holds `Papers` (46), `Books` (38), `GitHubRepos` (8) and
`References`. Read from it; never copy into here.

## Layout

```
docs/
  adr/        design decisions; 0004 and 0005 are the live design
  research/   primary-source research, recording what could NOT be established
  sprints/    plan / retrospective / summary per sprint
.claude/
  hooks/      mechanical guards, seeded from the consumer repository
src/          the store and the export (not yet built)
tests/        process guards, each encoding a failure paid for once
```

## Prior art, read rather than assumed

[`docs/research/cyc-knowledge-representation.md`](docs/research/cyc-knowledge-representation.md)
records what Cyc actually does, from primary sources, and **corrects two things
this project had previously recorded as fact**. The finding that most shaped the
design is Lenat's own footnote: Cyc's general theorem prover timed out on over a
million consecutive queries and was switched off a decade ago. Everything Cyc
does is done by 1,100 specialised shortcuts.

That is the standing argument against building a general reasoner here.
