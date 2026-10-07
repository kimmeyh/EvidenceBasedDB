# ADR-0014: Evidence Based DB -- storage, schema and repository boundary

## Status

**ACCEPTED 2026-09-13** by the team lead.

What acceptance covers: the storage decision (SQLite first, committed text
export, named triggers for NoSQL and graph), the three record classes and their
schema spine, contexts rather than tags, the escalating reading level with its
postgraduate threshold, and the repository boundary (`EvidenceBasedDB`, private).

What it does NOT cover: **no implementation is authorised by this document.**
F39 was scoped as investigation and design, and building is a separate decision
with its own card. ADR-0015, which depends on this one's storage decision,
remains Proposed.

Supersedes nothing. Amended by later ADRs if the named triggers fire.

**Accepted does NOT mean settled here.** This design has not yet met a single
imported paper. See "Maturity" below: revision after the first ~20 papers is
the expected outcome, and recorded as a dated amendment rather than an edit.

## Date

2026-09-12

## Maturity: EARLY INNOVATION, revision expected

**Team lead, 2026-09-14: these ADRs and the database itself cannot be written in
stone. After importing roughly 20 papers we expect to find that some of this
works, some does not, and some fields need adding. That is expected, not
failure.**

This matters because "Accepted" on an ADR normally signals a settled decision --
the PDF toolchain, the results-store schema, the branch model. Those were
accepted after the practice had been exercised. **This design has not yet met a
single imported paper.** Reading it with the same finality would be a category
error, and would make the first necessary change feel like a defeat.

### The first checkpoint: 20 papers

At approximately 20 imported papers, review both ADRs against what actually
happened and record the answers:

| Question | What a bad answer looks like |
|---|---|
| Which fields were never filled? | A field nobody populated is dead weight; remove it |
| Which fields were filled with the same value every time? | Not carrying information; probably belongs in the context |
| What did we want to record and have nowhere to put? | The additions this checkpoint exists to find |
| How long did team-lead adjudication take per paper? | The number the whole design is constrained by (ADR-0015 section 2c) |
| Did the tiers land where predicted? | If everything is `read`, tiering is theatre |
| Did any `supports` or `contradicts` link get used? | scite's 0.8% says these are rare; zero at 20 papers is uninformative, zero at 200 is a finding |

**Revising after that review is the expected outcome, not an admission.** A
design that survives its first twenty papers unchanged has probably not been
tested against them.

### What revision does NOT mean

Two things stay stable through the early phase, because changing them costs more
than it saves:

1. **Provenance on every record.** The reason this system exists. A field can
   come or go; a record that cannot say where its value came from is the defect
   the whole thing is built against.
2. **Contexts as the partitioning mechanism.** Adding contexts is expected;
   replacing contexts with tags would undo the one structural idea taken from
   forty years of Cyc.

Everything else is provisional until the practice says otherwise.

### How revisions get recorded

Not by editing these ADRs in place. **A dated amendment section at the bottom**,
naming what changed and what observation forced it -- the same discipline the
preregistration uses, and for the same reason: a document that silently becomes
correct teaches nobody why it was wrong.

## Context

### The problem, in the project's own evidence

The same fact is restated across many documents with nothing linking the copies.
Every instance below is a real defect this project shipped or nearly shipped:

| Defect | What happened |
|---|---|
| **A15** | `0.7688` quoted in four places as the frozen pool's AUPRC at k=6. It appears in **no artifact** -- the mean of an exploratory five-seed run carried into a ten-seed write-up. It was carrying a claim the true value inverts |
| **Sprint 8** | The QCi letter asserted "twelve amendments" while the enclosed preregistration had seventeen |
| **A19** | The amendment count changed and had to be corrected in every document that named it |
| **F52** | B1's variable count read **78** in three places and **91** in two, in the same submission |
| **Sprint 13** | `summarize_b2.py` wrote "78 vars" into the shipped evidence artifact, which A24 had already corrected in prose |
| **Sprint 13** | Appendix A.5 quoted `0.5739`, a real number from a different file, in a sentence about fold 0 whose real value is `0.5424` |

Each was caught by a human reading, or by a script written for that one check.

### Why the existing controls do not close it

`test_document_figures_resolve.py` (F44) already does the cheap half: every
number in the three documents must resolve to a stored value or be registered
with a reason. It carries **66 registered exemptions** and it works.

Its own docstring states the gap, and Sprint 13 then demonstrated it exactly:

> It does NOT catch a figure that exists in the store but is quoted in the wrong
> place.

That is the `0.5739` defect. Both numbers are real, so a global value-set lookup
accepts either anywhere. **Closing it needs per-claim provenance -- this sentence
cites THAT row -- which is what an evidence base is.**

### The second and third record classes

The team lead has added vocabulary to the scope, and it is not decoration.
Guidelines §8 says a non-specialist reviewer must be able to follow the
technical approach, and §6 puts technical reviewers and enterprise
representatives on the same panel. A maintained glossary at a defined reading
level is the mechanism for that, and it becomes more valuable in Phase 2 when
the audience widens again.

### Scale, measured 2026-09-12 rather than estimated

An inventory of the three submitted documents, verified against them:

| Record class | Submitted package | Proposal only | All five documents |
|---|---|---|---|
| Acronyms | 57 | 43 | 94 |
| Technical terms | 126 | 108 | ~143 |
| **Glossary total** | **183** | **151** | **~237** |

Plus the assertion class: 168 result rows over 30 distinct keys, 66 registered
figure exemptions, and 32 amendments.

**Two findings from the inventory change the scope.**

**First, seven acronyms I had assumed were in scope are not in the submitted
package at all** -- QUBO, QPU, QFE, EQC, SHAP, ADR and T&C appear only in the
preregistration or the requirements matrix. Verified by grep, zero hits across
all three documents. Scoping the glossary to what a judge actually reads is a
real reduction, not a rounding.

**Second, 85% of the glossary burden sits in the proposal**: 43 of 57 acronyms
and 108 of 126 terms. The appendix adds almost no new vocabulary, only new
instances of the same vocabulary. Its 32 unique entries are the statistical
machinery -- BCa, Spearman, permutation p, seed SD, free-sign logistic stack --
which are simultaneously the hardest to simplify and the least likely to be
read first.

**Therefore: the 8th-grade target applies to the PROPOSAL set (151 records), and
the appendix-only statistical tail is allowed a higher register.** That is a
scope decision the inventory earned, and it makes the reading-level commitment
honest rather than aspirational.

### SCOPE CORRECTION, 2026-09-13 (team lead)

**The 151 glossary records are the FIRST USE CASE, not the scope.** I had been
treating the HSBC submission's vocabulary as the boundary. It is not. The target
is a domain knowledge base covering:

- **quantum machine learning**
- **machine learning** generally
- **quantum computing**
- **each of the major quantum computing platforms** and their differences

That is a different order of magnitude, and it changes four things I had
settled. Recording them here rather than quietly revising, because the earlier
sizing is what several decisions rested on.

**1. The sizing argument weakens, and the "we are not Cyc" defence with it.**
"151 records is why this is tractable" no longer holds. A domain base over
QML/ML/QC is thousands of terms with real structure between them. Still far
short of Cyc's tens of millions, and still bounded by being a DOMAIN rather than
common sense -- but the honest comparison is now "a technical encyclopedia",
not "a project glossary".

**2. Authorship economics become the central design question**, where before
they were a footnote. Cyc's answer was 2,000 person-years, and their finding
that LARGER TEAMS REDUCED productivity [LM23 p13] is a warning about
coordination, not about effort. Our answer has to be agent-drafted and
human-adjudicated, with the adjudication cost per record held low enough that it
does not become the bottleneck. **That is the number to design against**, and it
is measurable: minutes of team-lead review per accepted record.

**3. Contexts multiply, and this is where Cyc's mechanism starts to earn its
keep.** Three contexts served one project. A domain base needs at least:

| Context | Holds |
|---|---|
| `world` | Mathematics, physics, facts true independent of platform |
| `ml` | Machine learning generally |
| `qc` | Quantum computing generally |
| `qml` | The intersection, which is NOT the union of the two |
| `platform:dirac-3` | QCi's continuous-variable optimizer |
| `platform:braket` | AWS gate-based access |
| `platform:classiq` | Circuit synthesis |
| `platform:ibm-q`, `platform:ionq`, ... | As needed |
| `method` | How we build and reason, including about this library |
| `hsbc-2026` | The first use case's project-specific assertions |

**The platform contexts are the strongest argument for microtheories over
tags.** "Dynamic range" means something different on a photonic analog optimizer
than on a superconducting gate machine. "Qubit count" is not even defined on
Dirac-3. A tag cannot express that; a context with factored-out assumptions can
hold both without contradiction, which is exactly what Cyc built contexts for --
"Cyc can reason within the StarWars context and name several Jedi, and not have
a contradiction with the same question being asked in the RealWorld context"
[LM23 p15].

**4. The build order changes.** The glossary-first plan still holds, because the
HSBC vocabulary is a real slice that exercises the schema. But it is now
explicitly a PILOT whose purpose is to learn the authorship cost before
committing to the domain, not a deliverable that completes the work.

**What does NOT change**: determinate facts stay computed rather than stored;
heuristics still name what they stand in for; provenance is still required; and
Lenat's footnote 9 is still the argument against building a general reasoner.

## Decision

### 0. It is called the Evidence Based DB, and it is PRIVATE for now

**Team lead, 2026-09-13.** Name: **Evidence Based DB**. Repository:
**`EvidenceBasedDB`**. Visibility: **private**.

The name was chosen over "fact database", which this project had used since
Sprint 8, and the reason is this repository's own record. `0.7688` appeared in
four documents and was not a fact. The unconverged solver produced figures that
were not facts. A store called a *fact* database asserts the very property it
exists to check; "evidence base" is the term whose established usage -- graded
findings, quality levels attached, revision expected -- matches what this
actually holds. It also reuses vocabulary already in the project, since
`[HW]`/`[SIM]`/`[PROJ]` are *evidence* tags.

**Superseded 2026-09-13:** the CARD is renamed too. F39 is the Evidence Based
Database card everywhere it is live. CHANGELOG entries keep their original
wording, because rewriting a dated record is the retroactive edit this project
now forbids.

**PRIVATE HAS A CONSEQUENCE, stated here so it is a decision and not a
surprise.** This repository is public and judged. While `EvidenceBasedDB` is
private, **no citation from this repository may depend on it resolving** -- a
reader following a pointer into a private repository gets a 404, which is the
dangling-reference defect this project keeps finding, in a new place.

So for as long as it is private, the rule in section 5 is not a preference but a
constraint: citations carry their claim and provenance inline, and the library id
is an identifier for someone who already has access. Revisit if and when it
goes public.

### 1. It starts OUTSIDE this repository

Team-lead direction, 2026-09-12. A separate repository, with this project as its
**first consumer rather than its owner**. Some or all may be brought in later as
a separate decision on the evidence.

Three reasons this is right rather than merely instructed:

- This repository is a **submitted, judged artifact**. Its history is frozen and
  its hooks refuse rewrites. A tool under active design does not belong inside
  something that must not churn.
- The glossary is **reusable across projects**; the fraud submission is one use.
- If it fails, it fails **somewhere that does not touch the evidence record**.

**Boundary status: PROVISIONAL.** Revisit once there is a working store and real
usage, not before.

### 2. Storage: SQLite, with a text export committed alongside

**SQLite** as the store of record. **A deterministic text export** (JSON or
Markdown per record class) regenerated from it and committed, so:

- the store is queryable, transactional and enforces a schema;
- the **diff is reviewable** -- a fact changing value shows up in review, which is
  the entire point given that the defects above were all silent;
- a consumer needs no database to read a fact, only the export.

The export is generated, never hand-edited. This is the same shape as
`b2_hardware.json` regenerating from `results.json`, which this project already
relies on.

### 2b. SQLite first; NoSQL and a graph DB when a NAMED trigger fires

**Team lead, 2026-09-13: we may end up needing all three -- relational, document
and graph -- but start with SQLite and let the need announce itself.**

That is the same discipline this project has applied to every other tooling
question, and it has been right every time: measure before adopting. ADR-0015
does it for retrieval (search before embeddings). Sprint 13 did it for the pool
fixture (three options measured, smallest chosen). Cyc did it the other way and
Lenat records the cost -- they assumed ONE representation would serve, then
spent years "vainly searching for some fast general-purpose reasoning algorithm
over HOL, which probably doesn't exist" [LM23 p14].

**The risk in "start simple" is that the trigger never gets recognised**, and
the project limps along with the wrong store because switching feels expensive.
So the triggers are named now, while nothing is at stake:

| Store | Adopt when | NOT when |
|---|---|---|
| **SQLite** (now) | Default. Schema enforcement, transactions, one file, no server | -- |
| **Document / NoSQL** | Record shapes diverge so far that the relational schema becomes mostly-NULL columns, or per-platform records need genuinely different fields rather than different values | A record merely has optional fields. That is what NULL is for |
| **Graph** | A query needs TRANSITIVE traversal we cannot express -- "every term reachable from `qml` through prerequisites", "which contexts inherit from `qc`", "what depends on this assertion if it changes" | We merely have foreign keys. Joins are not a graph problem |

**The graph trigger is the one most likely to fire, and the likeliest cause is
context inheritance.** If `platform:dirac-3` specialises `qc` which specialises
`world`, and prerequisites form chains (the escalation ladder's rungs), then
"what does a reader need before this term" is a reachability query. SQLite can
do recursive CTEs, so the trigger is not "we have a hierarchy" -- it is "the
recursive queries have become the hard part of the code."

**Record the trigger when it fires.** A dated note saying which query forced the
change, with the query in it. Otherwise the next reader inherits a three-store
architecture with no account of why, which is the same defect as a figure with
no provenance.

**Migration is cheap by construction, and that is deliberate.** The store of
record is SQLite but the ARTEFACT is the committed text export. A different
engine consumes the same export. This is the same reason the export exists at
all -- it makes the store replaceable and the diff reviewable, and those turn
out to be the same property.

### 3. Three record classes, one schema spine

Every record, regardless of class, carries:

| Field | Meaning |
|---|---|
| `id` | Stable, human-readable. Documents cite this, not the value |
| `class` | `assertion` \| `acronym` \| `term` |
| `value` | The number, the expansion, or the definition |
| `provenance` | Pointer to what establishes it: a `results.json` row + config hash, an artifact path, an amendment, an external citation |
| `evidence_tag` | `HW` \| `SIM` \| `PROJ` \| `N/A` -- reuses the existing vocabulary rather than inventing one |
| `certainty` | `high` \| `moderate` \| `low` \| `very-low`. DERIVED, never chosen. See ADR-0015 section 2e |
| `certainty_reasons` | REQUIRED whenever certainty is not the starting level. The named reasons that moved it |
| `fidelity` | `exact` \| `scoped` \| `consequence` -- how FAITHFUL the definition is. See section 5 |
| `reading_level` | US grade level the definition actually achieves, 8 to 20. How HARD it is. See section 5 |
| `prerequisites` | Ids of records a reader needs first. The escalation ladder's rungs |
| `updated` | Date, and the amendment or issue that moved it |

Class-specific fields:

- **`assertion`**: `units`, `rounding`, and the `documents` that cite it.
- **`acronym`**: `expansion`, `plain_definition` (8th-grade), `visual` (link to
  an image or short animation where one genuinely helps).
- **`term`**: `plain_definition` (1–3 sentences, 8th-grade), `visual`,
  `see_also`.

**Scoring fields are carried on every class from the start**, even where unused
today, so the schema does not need widening later. The one that earns its place
immediately is `certainty`: this project already separates measured from
projected via evidence tags, but **not strong-measured from weak-measured**. The
score-degeneracy caveat, the single-seed spot checks, and the adversarial
control that never converged are asserted with genuinely different certainty,
and today that lives only in prose.

**This was a 0.0 to 99.9 percent `confidence` field until 2026-09-14**, and the
change is worth recording rather than quietly making. Two things were wrong with
the percentage. It is unfalsifiable -- `62%` cannot be argued with, which makes
it a weaker instrument than it looks in a project whose whole posture is that
claims should be checkable. And it was labelled "Cyc-derived" when the research
in `../research/cyc-knowledge-representation.md` establishes that **Cyc carries
no numeric confidence on assertions at all**; the library's own first record
holds that fact as `cyc-no-numeric-confidence`.

ADR-0015 section 2e replaced it with the GRADE model -- four levels, a starting
level set by the evidence tag, and NAMED reasons for every move. The reasons are
the audit trail, and they are the part worth having.

### 3b. Contexts, not tags: three at pilot, ten-plus at domain scale

**Cyc's microtheories are the right mechanism**, and they are better than a
project/world flag for a reason that is not obvious until you read why they
exist: a context factors out the assumptions its assertions SHARE, so records
inside it get terser and reasoning within it gets faster. "Every assertion in
the 2023 context doesn't need to start out 'In the year 2023...'"
[LM23 p15].

**Pilot contexts**, settled 2026-09-13 when the first non-project record
arrived. The domain-scale set is larger and is listed in the scope correction
above; these three are what the pilot needs:

| Context | Holds | Example |
|---|---|---|
| `hsbc-2026` | Assertions specific to this project | amendment count; campaign totals; B2's +0.0256 |
| `world` | True independent of any project | 2+2=4; E=mc^2; standard acronym expansions |
| `method` | How we build and reason, including about this library | arXiv:2308.04445 |

The third one was not in the original sketch and was forced by the first record
the library will hold. arXiv:2308.04445 is neither project evidence nor a world
fact: it is methodology for the tool being built. Discovering that on record one
is a good sign for the mechanism and a bad sign for designing contexts in
advance.

**Rule for adding a context**: only when assertions genuinely share an
assumption the existing contexts do not. Cyc has about 10,000, kept down by
COMPUTING contexts (`IntersectContexts`) rather than reifying every combination
[LM23 p15]. Three is the right number to start with; the failure mode to avoid
is a context per project, which is a tag wearing a costume.

**Why this matters for reuse**: a future project inherits `world` and `method`
for free and adds only its own context. That is the whole argument for the
library living outside this repository.

### 4. Citation and validation

Documents cite by id -- concrete syntax deferred to implementation, since it must
survive pandoc to PDF and that constraint is empirical. A build step resolves
every citation and **fails on an unresolved or stale one**. This is the
mechanism that would have caught A15, the amendment-count drift, and the 78/91
split.

### 5. Reading level ESCALATES one grade at a time, and the target is a path not a term

**Team lead, 2026-09-12.** Start every definition at 8th grade. Where an honest
definition is not achievable at that level, go up ONE grade and try again.
Repeat until it is achievable. Record the level that worked.

**The ceiling is PhD (grade 20), and reaching it is not a failure.** The purpose
is that a reader can follow along and grow what they understand: if everything
AROUND a hard term is explained lower, almost all of it is understandable well
before the hard term, and the hard term becomes reachable rather than a wall.

Grades 13 to 16 are college freshman through senior and are **acceptable, not
deficient** -- a motivated reader reaches them. The level that warrants attention
is **postgraduate, 17 and above**, and specifically a CLUSTER of it: that is
where a reader cannot climb without prior specialist training, which is the one
case the ladder cannot fix.

That reframing matters more than it first appears. Reading level is a property
of a **path**, not of a term in isolation. A grade-11 term sitting in grade-9
surroundings is climbable. The same term surrounded by other grade-11 terms is
not. **This is why `prerequisites` is part of the schema and not a nicety**: it
records the rungs, so the ladder can be checked for gaps rather than assumed.

#### The escalation, worked on the terms that failed at 8

Tested rather than asserted. The earlier draft of this ADR declared seven terms
unachievable; escalation rescues most of them.

| Term | 8 | 9 | 10 | 11 | Achieved |
|---|---|---|---|---|---|
| convex | NO | **yes** | | | **9** |
| BCa interval | NO | **yes** | | | **9** |
| simplex | NO | **yes** | | | **9** |
| split dispersion, not sampling error | NO | **yes** | | | **9** |
| step-wise average precision | NO | | **yes** | | **10** |
| effective analog resolution (200:1) | **yes** | | | | **8** |
| 23 dB dynamic range | NO | NO | NO | **yes** | **11** |
| rank-one to numerical precision | NO | NO | NO | **yes** | **11** |

**"Convex" is the case that proves the rule.** At 8th grade the natural gloss is
"bowl-shaped, so there is one lowest point" -- which CONTRADICTS our own appendix,
where the minimiser set is a face of the simplex, a flat region rather than a
point. At 9th grade it works: *"The problem has no false bottoms. Any lowest
point you find is genuinely the lowest, so there is no risk of getting stuck
somewhere that only looks best."* That drops the false uniqueness and keeps the
property that actually matters -- it is why a classical solve is a valid check on
the device.

A flat `fidelity: consequence` would have written that term off. One grade of
escalation recovered an honest definition. **The measured failure is worth more
than the binary one**, and the earlier draft was simply wrong to give up.

#### The distribution is itself a finding

Grade levels across the glossary say something about the submission that no
individual entry does: a cluster of grade-13-and-above terms in one section is
evidence that the SECTION is over-jargoned, not merely that its vocabulary is
hard. That is a document-quality signal, available for free once the field
exists, and it is worth watching in Phase 2 where the audience widens.

#### `fidelity` and `reading_level` are different axes, and both are kept

- `reading_level` answers **how hard**.
- `fidelity` answers **how faithful**.

They are independent. "Hamiltonian" reaches 8th grade comfortably and is still
`scoped`: the definition is true for this paper's usage -- a table of costs the
machine minimises -- and would be wrong as a general physics definition. A
physics-literate judge must not read it as an error, so the record says so.

Keeping only one of the two fields would lose real information either way.

#### Why this survives contact with the project's standards

The submission's credibility rests on not overclaiming. A glossary that quietly
overclaimed about its own definitions -- shipping a comfortable falsehood because
the honest version was harder -- would undercut the thing it exists to support.
Escalation is what makes the honest version reachable instead of abandoned.

## Alternatives considered

### Extend the F44 registry in place
- **Description**: grow the `REGISTERED` dict in `test_document_figures_resolve.py` into the fact store.
- **Pros**: zero new infrastructure; already works; already in CI.
- **Cons**: it is a Python literal in a test file. No provenance, no confidence, no vocabulary classes, and it cannot express "this sentence cites that row" -- the exact gap. It would also put a growing data structure inside a frozen repository.
- **Why rejected**: it solves the half already solved and cannot reach the half that matters.

### Plain JSON or YAML files, no database
- **Description**: one file per class, hand-edited, validated by a script.
- **Pros**: no dependency; trivially diffable; no export step.
- **Cons**: no referential integrity, no query, and hand-editing at domain scale invites exactly the drift the store exists to prevent.
- **Why rejected**: the failure mode returns in a new place. Kept as the **export format**, which is where its diffability is worth having.

### Document store or graph database from the start
- **Description**: adopt NoSQL or a graph engine immediately, on the grounds that a domain knowledge base with context inheritance is graph-shaped.
- **Pros**: the shape argument is real. Context inheritance and prerequisite chains ARE graphs, and a graph engine would express them natively.
- **Cons**: it prices in a need we have not met yet. SQLite handles recursive queries via CTEs, and at pilot scale the hierarchy is three contexts deep. Adopting an engine for a problem we have not yet had is how projects acquire architecture they cannot justify.
- **Why rejected FOR NOW, with named triggers**: see section 2b. Both remain live options and the conditions for adopting them are written down rather than left to judgement.

### A real Cyc or an ontology engine
- **Description**: adopt Cyc, or an RDF/OWL triple store.
- **Pros**: genuine inference; the confidence model is native.
- **Cons**: enormously heavier than the problem. The team lead's own framing was "functionally representative, NOT a LISP reimplementation".
- **Why rejected**: we need provenance and a confidence field, not a reasoner.

### Do nothing; keep verifying by hand
- **Description**: continue as Sprints 8 through 13 did.
- **Pros**: no build cost.
- **Cons**: it has failed six times on record, and the last one reached a judge-facing document.
- **Why rejected**: the failure rate is the argument.

## Consequences

### Positive
- The `0.5739` defect class becomes detectable rather than luck-dependent.
- Confidence becomes explicit and reviewable instead of living in prose.
- The glossary serves the non-specialist reviewer the Guidelines describe.
- Built outside, it cannot destabilise a submitted artifact.

### Negative
- A cross-repository dependency, which is a real cost and the reason the
  boundary is provisional.
- Citation-by-id makes documents less readable in raw Markdown.
- ~1,000 records is genuine authorship, and the glossary half especially.
- **A fact database can be confidently wrong.** It centralises the value and
  therefore centralises the error. The provenance field is what keeps it
  checkable; a record without one is worse than no record.

### Neutral
- The export is another generated artifact, on the pattern already in use.

## Preregistration touchpoints

Section 11 (analysis-code and results-store rules) governs how results rows are
written; this ADR consumes those rows and changes nothing about them. The
preregistration governs methodology; this is an engineering decision around it.
**No amendment is required to adopt this ADR.**

## Open questions for the team lead

1. ~~Repository name and visibility.~~ **DECIDED 2026-09-13**: named
   **Evidence Based DB**, repository `EvidenceBasedDB`, **private for now**. See
   section 0, including the citation constraint that privacy imposes.
2. ~~Does the glossary ship?~~ **DECIDED 2026-09-13: INTERNAL for now.** A
   repository asset, not a submission appendix. Consequence: the review bar is
   ours rather than a judge's, so entries may be drafted and improved in place
   instead of needing to be right before they appear. Revisit for Phase 2, where
   a glossary is a plausible appendix and the audience widens.
3. ~~Who authors the 151 proposal-set definitions?~~ **DECIDED 2026-09-13:
   source them from existing dictionaries and references wherever possible, and
   Claude drafts the rest for the team lead to review.**

   This changes the cost materially. Most of the 43 acronyms have standard
   expansions that need no invention -- AUPRC, GBDT, PCA, KNN, LDA are defined
   in any ML reference. The work concentrates in two places: terms this project
   uses in a SCOPED sense (see `fidelity`), where a general dictionary
   definition would be wrong for our usage, and the grade-11-and-above tail
   where no source writes at that level.

   **A sourced definition carries its source in `provenance`, exactly like an
   asserted number.** A definition with no source and no author is the same
   defect class as a figure with no artifact.
4. ~~Is a grade-13-or-higher cluster a trigger to revise the document?~~
   **DECIDED 2026-09-13: no. The threshold is POSTGRADUATE, grade 17 and above.**

   The team lead's reasoning, and it corrects mine: grades 13 to 16 are college
   freshman through senior. A term that lands there is not a problem, because a
   motivated reader reaches it -- which is the whole point of the escalation
   ladder. **A cluster at POSTGRADUATE level is the signal worth addressing**,
   because that is where the reader cannot climb without prior specialist
   training.

   | Grade | Level | Verdict |
   |---|---|---|
   | 8-12 | Middle and high school | Target range |
   | 13-16 | College freshman to senior | Acceptable; reachable |
   | 17+ | Postgraduate | **Cluster here is a finding** |

   Still a review signal and never an automatic edit. The Phase 1 documents are
   frozen; this applies to Phase 2 writing.

## References

- F39 (this card, the Evidence Based Database), F44 (`test_document_figures_resolve.py`), F72 (reference
  library, gated on this storage decision)
- Amendments A15, A19, A24; findings F52, and the Sprint 13 evidence walk
- `docs/sprints/SPRINT_13_SUMMARY.md`, `docs/sprints/SPRINT_8_RETROSPECTIVE.md`
- [`../research/cyc-knowledge-representation.md`](../research/cyc-knowledge-representation.md) -- primary-source research on Cyc, read 2026-09-13. It CORRECTS two things this ADR originally assumed: Cyc has four composite truth values rather than five, and carries NO numeric confidence on assertions, so the confidence field here is our own design and must stand on its own merits
- Lenat, D. and Marcus, G., arXiv:2308.04445 (2023), cited above as [LM23]

## Amendments

Recorded rather than edited in place, because this ADR is Accepted. Each entry
names what changed and what observation forced it.

**2026-09-14 (A1): ADR-0015 is ACCEPTED; the Status section above is stale.**
The Status section says "ADR-0015, which depends on this one's storage decision,
remains Proposed". It was accepted on 2026-09-14, after this document. Found by
an adversarial review of PR #94.

Worth recording as an amendment rather than a typo fix, because it is this
project's signature defect appearing between the two ADRs written to prevent it:
one value, maintained in three places -- 0014's Status, 0015's Status, and
`README.md` -- where one moved and the other did not. ADR-0015 section 22-28
argues at length that leaving a decision Proposed when the practice has settled
produces "a practice that is settled and a record that says otherwise". That is
precisely the state the stale sentence described.

**2026-09-14 (A2): `confidence` replaced by `certainty` plus
`certainty_reasons` on every record class.** The schema spine mandated a 0.0 to
99.9 percent `confidence` field while ADR-0015 section 2e abolished it as
unfalsifiable, so the assertion class required both a field and its own
replacement. The percentage was also labelled "Cyc-derived" against research
establishing that Cyc carries no numeric confidence at all. Found by the same
review.

**2026-09-14 (A3): `class` gains a fourth value, `paper`.** Section 3 defined
`class` as `assertion | acronym | term` and claimed the schema would not need
widening. ADR-0015 section 1 adds papers as a fourth class. The claim was wrong
within a day, which is the argument for the 20-paper checkpoint rather than
against the schema.

**2026-09-17 (A4): The 20-paper checkpoint (46 papers loaded), five of six
questions answered.** Sprint 2 Task E, walked against the real store rather
than recollection.

**Every count below is a snapshot as of 2026-09-17, against the store as
it existed that day.** They are expected to change as more papers and
assertions are added (CLAUDE.md: additions to the seed directories happen
over time and are expected) -- none of these numbers should be read as a
current fact at any later date without re-querying the store. Raised by
the team lead (2026-09-18) after a code review found two of these counts
had already drifted from the store's actual state by the time this
amendment was drafted.

- **Which fields were never filled?** `units` and `rounding`
  (`assertion_fields`) -- 0 of 8 assertions. `assertion_documents` -- 0 rows,
  despite the field existing since Task B. Neither has an assertion yet
  whose claim genuinely needs a unit, a rounding note, or a citing document
  beyond its own provenance; both stay in the schema rather than being
  removed, since the sample (8 assertions, from two papers -- Lenat/Marcus
  and the HSBC preregistration) is too small to conclude the fields are
  dead weight rather than simply not yet needed.
- **Which fields were filled with the same value every time?** `evidence_tag`
  -- 53 of 54 records carry `N/A`; only the two HSBC-derived assertions
  (Sprint 2 Task B) carry `PROJ`. This is the field the ADR's own bad-
  answer criterion names directly: "not carrying information; probably
  belongs in the context." At 54 records, mostly from ONE methodology
  paper (Lenat/Marcus) plus 46 paper-tier records that do not themselves
  carry evidence tags, this reads as premature rather than settled --
  revisit once assertions are extracted from a wider mix of papers,
  including ones with genuine [HW]/[SIM] figures to tag.
- **What did we want to record and have nowhere to put?** Nothing found.
  `paper_applicability` (added Sprint 2 Task A, 59 rows across 45 of 46
  papers) and `assertion_documents`/`citation_context` (added Sprint 2, PR
  #1 review) both closed real gaps found in practice rather than exposing
  a new one.
- **Did the tiers land where predicted?** Yes: 27 `seen`, 18 `screened`, 1
  `read`, out of 46 papers. Not "everything is read" -- the ADR's own
  named failure mode did not happen.
- **Did any `supports` or `contradicts` link get used?** Yes, once each (2
  relations total, both from the Lenat/Marcus paper's own worked example).
  Consistent with scite's cited 0.8% contrasting-citation baseline; per the
  ADR's own framing, uninformative at this sample size, not yet a finding.
- **How long did team-lead adjudication take per paper?** NOT YET ANSWERED.
  This is Sprint 2 Task F's own job, running separately from this
  amendment, against a ~20-record sample from the `screened` tier. Task E
  (this amendment) intentionally does not answer it, since answering it
  well needs its own dedicated, timed pass rather than a number estimated
  alongside five other questions.

**Consequence**: no schema field is removed or added by this amendment.
The evidence at 46 papers does not yet meet the bar either bad-answer
criterion sets (a field that is definitively dead weight, or a context
that is definitively missing information) -- it meets the bar for
"watch, do not conclude yet." Revisit `units`/`rounding`/`evidence_tag`
at a wider, more diverse sample (F5's QCi-author papers and F2's broader
ingestion would both help) rather than at a fixed paper count.

**2026-09-19 (A5): the context tests.** Sprint 4 Task F (F25 part D4)
re-filed every paper against four written tests after Sprint 3's reviews
(F9, F10) found the section 4 definitions applied inconsistently across the
18 `screened` records. The tests refine the table above, they do not replace
it: `world` is passed by a theorem, a proof, a physical law or a measurement
of nature that would be true if this project did not exist, and failed by an
engineering demonstration, a policy report or an architecture paper, however
platform-independent; `method` is passed by a source about how claims are
benchmarked, evaluated, certified, simulated for evaluation or named, and by
practitioner tooling for building the experiments this library reads; `ml`
is passed when classical ML content is the object of study or a named
comparator; `qml` is claimed via workload: the model itself is quantum ML,
or an ML model is what a quantum optimizer trains or compresses; `qc` is not
claimed beside a `platform:*` context that already carries the quantum
content; `hsbc-2026` is never claimed by a paper. The full statement, with
the records each test passed and failed, is `docs/INTAKE_WORKFLOW.md`
section 8.

**Every count below is a snapshot as of the end of 2026-09-19**, after the
pass: `method` 16 applicability rows (was 8), `ml` 15 (was 0), `world` 4
(unchanged in number; moved off `arute` and `rand`, onto `zajac` and
`kerger`), `platform:braket` 1 (was 0). 26 of 48 records changed context
set; every rationale now ends with the anchor naming where it was read.

**2026-10-03 (A6): two new assertion fields, `derivation` and
`claim_type`, and two computed certainty caps.** Sprint 6 Task D (backlog
items F37 and F34, with the `claim_type` question F37's planning note
raised), taking decisions Q2, Q4 and Q5 approved at Sprint 6 planning
(team lead: "q1. 1 q2. 1 ... q11. 1"). Decided in one amendment with
ADR-0005 A4 so the assertion fields change once.

**Every count below is a snapshot as of 2026-10-03, against the store as
it existed before Sprint 6 Task E's migration.** The store grows by
design; re-query it rather than reading these numbers as current later.

*Why.* A learning was recognized only by a provenance string beginning
"synthesis of" (`scripts/learnings.py`, Sprint 5). The pilot's first
definition, "no paper yields it", wrongly caught a project assertion
(`docs/LEARNING_SYNTHESIS.md` section 7). A record that is told apart from
its neighbors by the wording of a free-text field is one edit away from
being misfiled. Separately, an absence claim ("QCi does not claim fault
tolerance") and a vendor's claim about its own product were stored exactly
like a measured result, with nothing a query could select on.

*(a) `derivation: extracted | synthesized | project`, on every
assertion.* `extracted`: read from a source, which yields it
(`paper_yields`). `synthesized`: a generalization over other assertions
(a learning). `project`: a fact about this project or its consumer, whose
provenance is the project's own document. Back-filled from what the store
holds: provenance beginning "synthesis of" is `synthesized`; a `yields`
row is `extracted`; neither is `project`. As of this date: 18 extracted, 3
synthesized, 2 project (`hsbc-b1-variable-count` and
`hsbc-b1-variable-count-wrong-78`). `scripts/learnings.py` selects on
the column, not on the string.

*(b) A synthesized assertion's inputs.* Its inputs are the assertions
with a `supports` relation to it in `assertion_relations`, and there must
be at least two. **This departs from the F37 planning note's wording**
("provenance names at least two existing assertion ids"): the ids already
live in `assertion_relations`, and restating them in provenance would be
the one-value-in-two-places drift this project exists against. Provenance
stays "synthesis of the assertions that support or contradict it (see
assertion_relations)". A `contradicts` row is evidence the synthesis must
answer, not an input.

*(c) The synthesis cap (decision Q4).* A synthesized assertion's
certainty is capped at the weakest of its inputs. This is Cyc's rule for
deductions (`argumentation.java`, `strength_combine`, line 117): a
conclusion is no stronger than its weakest premise. As of this date the
cap moves one of the three learnings:
`learning-qml-no-reliable-tabular-accuracy-gain` is `moderate` with
inputs at `low`, `low`, `high`, `low` and `moderate`, so it is capped to
`low`; `learning-ml-resampling-not-the-lever-for-strong-trees` is `low`
with inputs at `low` and `low`, unchanged;
`learning-method-check-metric-and-power-before-reading-a-difference` is
`moderate` with inputs at `high` and `high`, unchanged.

*(d) The retraction floor (decision Q2).* An assertion whose only
yielding sources are `withdrawn` or `retracted` (ADR-0005 A4) is computed
to `very-low`, with the reason naming each source and its status. GRADE
treats a retracted study as unusable; computing the floor keeps the
reason visible instead of leaving it to a reader to notice.

*(e) Where the caps live.* Both caps are determinate from other stored
facts, so they are COMPUTED, never stored. Stored `certainty` and
`certainty_reasons` remain the assessor's GRADE judgment. The export
emits each assertion's computed cap, when one applies, as separate derived
keys (`certainty_cap`, `certainty_cap_reason`) beside the stored ones, and
the rebuild path does not write derived keys back into the store. Folding
the cap into `certainty` would make the rebuild write a computed value
into a stored field, and the export would stop being a byte-identical
round trip.

*(f) `claim_type: positive | absence | vendor-self-claim` (decision
Q5).* `positive` is the default: the source states something that is.
`absence`: the claim is that something was not found ("no closed form
exists", "QCi does not claim fault tolerance"). An absence claim is only
as good as the search behind it, so it requires a new
`assertion_fields.search_scope` (what was searched, and the date),
refused at the door when empty; `citation_context` stays reserved for
quoted text. `vendor-self-claim`: a vendor's statement about its own
product, flagged so a query can select it and a certainty reason can cite
it. The 23 existing assertions are classified one by one at the
migration (Sprint 6 Task E), each with its reason in `updated_reason`;
none becomes `absence` without its scope.

*Consequence for section 3.* The assertion record gains two fields and a
conditional third (`search_scope`). `certainty` keeps its meaning:
derived by the assessor, with reasons. The new computed caps are a second,
mechanical reading beside it, never a replacement.

*Revisit when* a learning is built on another learning (a cap over a
cap). The `vendor-self-claim` flag and the admission-against-interest
rule (ADR-0005 A4 (e)) already meet: both assertions that carry the
upgrade are a vendor's statement about its own system, which is where an
admission against interest belongs.

**2026-10-06 (A7): the store leaves the repository, and the committed export
is retired.** Sprint 7 Task B (backlog item F58), taking the team lead's
request of 2026-10-06 and decisions Q1 = 2, Q2 = 1, Q3 = 1 and Q4 = 1
approved at Sprint 7 planning. This amendment reverses section 2's
"text export committed alongside"; ADR-0003 A2 and ADR-0005 A5 carry the
same change into those documents.

**Every count below is a snapshot as of 2026-10-06.** The store grows by
design; re-query it rather than reading these numbers as current later.

*Why.* The team lead, 2026-10-06: "sqlite db needs to be stored off
repository in D:\Data\Harold\EvidenceBasedDB\store and not in github any
longer as it will quickly exceed space allowed by github." The database and
its backups were already gitignored; what GitHub held was the export
(2.7 MB, `papers.json` 2.6 MB for 1,875 papers, about 1.4 KB per paper).
GitHub warns at 50 MiB per file and blocks at 100 MiB (docs.github.com,
"About large files on GitHub", read 2026-10-06), and every regeneration
adds a version to the history. A collection meant to reach tens of
thousands of papers cannot keep its full text in the repository.

*(a) Where the data lives.* The store is
`D:\Data\Harold\EvidenceBasedDB\store\evidence.db` and its backups are in
`D:\Data\Harold\EvidenceBasedDB\store\backups\`, outside every repository.
`store.script_paths` is the one place that resolves them: the default is
that folder, and the environment variable `EBDB_STORE_DIR` overrides it
(tests and CI point it at a temporary folder). No script writes data inside
the repository; a test checks that every default path resolves outside it.
`.gitignore` keeps `*.db` and `backups/` so a stray copy never lands.

*(b) The store is the record; the committed export is retired (Q1 = 2).*
Section 2 made the SQLite store a build output and the committed export the
artifact. That is reversed: the store is the record, and git holds code and
documents only. `export/` is removed from the repository; write scripts no
longer regenerate an export. `store/export.py` and `store/rebuild.py` stay
as library code: `scripts/regenerate_export.py --out <dir>` writes an
on-demand dump (outside the repository) and
`scripts/rebuild_store_from_export.py --from <dir>` rebuilds a store from
one. Neither has a default inside the repository. The export's past
versions stay in git history (Q3 = 1); nothing is rewritten.

*(c) What is lost, and what stands in for it.* Lost: a reviewable diff of
every data change, git history of what the store said and when, and a CI
round trip over the real data. In their place: every record's
`updated_reason` is append-only and says what changed and why; a verified
backup precedes every write (Sprint 5, unchanged); the team lead's daily
backups of the drive, kept 40 days, are the redundancy (Q2 = 1); and the
local suite keeps one round trip over the real data (dump the live store,
rebuild from the dump, dump again, compare bytes), so the on-demand dump
stays a proven recovery path.

*(d) Backup retention (replaces Sprint 5's rule 3).* Rule 3 kept a backup
until its content was in a committed export, and that export no longer
exists. A backup is now deleted only when ALL THREE hold: it is older than
32 days; it is not the newest backup of one of the last 5 sprints; and it
is not one of the 10 newest backups. At least ten backups therefore survive
whatever their age.

*(e) Tests.* Mechanism tests (backup, restore, retention, the dump and
rebuild round trip, determinism) run on small synthetic stores and run
everywhere. Checks of the REAL data (the admission-against-interest rule,
synthesis inputs, the caps, the learnings, the F11 packet) carry the
`live_store` pytest marker and read the live store read-only, or a copy
taken with the SQLite backup API when they must write. Locally a missing
store FAILS them, never skips them. CI cannot reach `D:\` and deselects
them by name in `.github/workflows/ci.yml`, with the reason beside it.

*Consequence for section 2.* "SQLite, with a text export committed
alongside" now reads: SQLite, outside the repository, with verified
backups; an export is an on-demand dump, never committed.

*Revisit when* the store needs a second reader on another machine (then a
shared location or a published dump is the question), or when a data
change needs review before it lands (then a reviewable dump comes back,
outside git).
