# How Cyc organizes its facts, and how it answers quickly

> **Entered in `docs/research/` by Sprint 6 Task H (F42), 2026-10-03.** Written
> 2026-09-28 in a Claude Code session outside the repository; text unchanged
> except US spelling, file links, and this box. Sources, as store records:
> `asanchez75-opencyc-github-repo` (the reviewed repository and its OWL
> exports), `cycorp-2009-larkc-cyc-inference-engine-source`,
> `cycorp-2012-opencyc-4-0-release`, `cycorp-2002-opencyc-0-7-0-release`,
> `cycorp-2002-introduction-cyc-inferencing`,
> `cycorp-2002-sbhl-subsumption-based-heuristic-modules`,
> `cycorp-2002-kb-term-indexing-cyc`, `cycorp-2002-cyc-canonicalizer`,
> `yuxi-liu-wired-cyc-archive-github-repo`, `white-flame-clyc-github-repo`,
> and `lenat-marcus-2023-trustworthy-ai`. "You" and "your" in the text mean
> the team lead. Local paths name where the sources sat on 2026-09-28.

Review of `D:\Data\Harold\github\opencycasanchez75`, three primary sources
downloaded 2026-09-28, and a primary-source web research pass. Revised
2026-09-28. Extends
`EvidenceBasedDB/docs/research/cyc-knowledge-representation.md` rather than
repeating it.

## Bottom line

**Your repo alone shows how Cyc organizes facts. It cannot show how Cyc reasons,
because the inference engine was never downloaded into it.** Three further
sources now close that gap, all obtained with your approval and all read without
running anything:

| Source | Date | What it shows |
|---|---|---|
| Cycorp's own inference-engine source, donated to the LarKC project | 2009 | The mechanism, verbatim |
| Cycorp's reference manual pages, recovered from the Internet Archive | 2002 | The design, in Cycorp's words |
| The OpenCyc 4.0 release, unpacked | 2012 | What the shipped engine stored on disk |

**How Cyc answers quickly, in one paragraph.** Every query is broken into small
subproblems. Each subproblem is offered to specialized modules, and each module
declares in advance what it costs and whether it is complete. A planner picks the
next piece of work by adding up weighted heuristic scores, a design that runs
unchanged from the 2002 manual to the 2009 source. The commonest questions,
"is X a kind of Y," never touch the rule engine at all: they are answered by
walking dedicated graphs. And every index stores counts at every layer, so the
planner knows roughly how many answers a lookup will return before it runs it.

**The single most instructive fact** is still the one from the first pass. `genls`,
Cyc's "is a kind of" relation, is defined as a rule macro: `(genls Poodle Dog)`
is, in Cycorp's words, "shorthand for the rule `(implies (isa ?OBJ Poodle) (isa
?OBJ Dog))`." The meaning is a rule. The storage is one edge in a graph. The
engine walks the graph. In the shipped 2012 knowledge base, `genls` is constant
number zero.

**Scope.** The engine source is 2009. The shipped system is 2012. Cycorp's
current prose (2019 to 2023) is summarized from a research pass and is marked as
such. Where these disagree, this report says which date each claim belongs to.

### Read depth, used throughout

| Tag | Meaning |
|---|---|
| **[measured]** | I computed it directly from a file |
| **[verbatim]** | I read the exact text in a primary source I hold locally |
| **[agent]** | A research agent read it directly in a primary source; I did not re-read it. Its full report, with sources and its own read-depth labels, is [cyc-inference-research-agent-report.md](2026-09-28_F42_cyc-inference-research-agent-report.md) |
| **[synthesis]** | My inference across sources |

---

## 1. Sources

### 1a. Your repo

| Item | Status |
|---|---|
| History | 6 commits, 2018-03-16 to 2020-06-26. Mirror of `github.com/asanchez75/opencyc` |
| OpenCyc 4.0 engine archives | **Absent.** 134-byte Git LFS pointer stubs; local LFS store empty |
| OWL exports, 2008 to 2012 | Present in history as real blobs |
| `opencyc-latest.owl.gz` | **Authentic.** MD5 matches the README. Content is 2012 despite the name |
| `opencyc-2012-05-10-readable.owl.gz` | **Corrupt.** MD5 mismatch, truncated gzip, 8.7 MB against ~20 MB siblings |
| Git index | **21 staged deletions.** Not touched |

Read with `git cat-file -p` only, which writes nothing to the index or working
tree.

### 1b. Sources obtained 2026-09-28

All three are under `D:\Data\Harold\EvidenceBasedDB\GitHubRepos\`, which is not a
git repository. Nothing was executed.

**LarKC Cyc engine source** - `larkc-cyc-engine-source\cycl\`

| Field | Value |
|---|---|
| Origin | `svn.code.sf.net/p/larkc/code/trunk/platform/src/main/java/com/cyc/cycjava/cycl/` |
| Maintainer | The EU-funded LarKC consortium's own SourceForge project |
| Files | 411, 21,097,078 bytes, **every size verified against the server** |
| Revision | Mostly SVN r1216; five files r1336 to r1590 (2010-2011) |
| License | Each file: "Copyright (c) 1995-2009 Cycorp Inc." under Apache 2.0 |
| Manifest | `MANIFEST.json` with SHA-256 per file |
| Caveat | A **subset**. Many function bodies were withheld and read `missing-larkc` |

**Cycorp documentation, recovered** - `cyc-archive-docs\`

| Field | Value |
|---|---|
| Origin | `github.com/yuxi-liu-wired/cyc-archive`, commit `62026a2`, 2026-09-20. Apache 2.0 |
| Content | 1,342 files, 69.2 MB. Mirrors of cyc.com, opencyc.org, research.cyc.com, LarKC site and wiki, Cycorp blog, Cyc 101 slides |
| Excluded | TPTP and IEEE archives, a 71.5 MB audio file, third-party blogs, and two executables |
| Gap | Six files not written: duplicate copies of one 2009 blog post whose encoded paths exceed Windows' 260-character limit |
| Key pages | `websites/www.cyc.com/cycdoc/ref/`: `inferencing.html`, `sbhl.html`, `kb-indexing.html`, `canon.html`, all dated March 2002 |

**OpenCyc 4.0 release** - archive `opencyc-4.0-linux.tgz`, unpacked in
`opencyc-4.0Linux\` (reorganized by you during the session)

| Field | Value |
|---|---|
| Origin | `sourceforge.net/projects/opencyc-backups`, a third-party mirror. Cycorp's own copy was removed 2017-03-13 |
| File | `opencyc-4.0-linux.tgz`, 191,506,807 bytes |
| SHA-256 | `6d0d28cc...5ecb664`, **identical to your repo's LFS pointer**. Byte-for-byte the file your repo was meant to hold |
| Content | Valid gzip dated 2012-06-13; 575 entries; no absolute paths, no `..`, no symlinks. Unpacked to 635 MB |
| License | `LEGAL.txt`: the knowledge base "is licensed under the Apache License, Version 2.0"; the server binary under a Cycorp free-of-charge license |

**All three archives your repo was missing are now present and verified.** You
added `opencyc-4.0-windows.zip` and `opencyc-0.7.0b.zip` to the same folder
during the session. Both match your repo's LFS pointer hashes byte-for-byte
(`ab5cbdedb966...` and `ecb81c2413c6...`), as does the Linux archive.

**What the folders you pulled contain** [measured]:

| Folder | Contents | Useful for this question? |
|---|---|---|
| `opencyc-4.0Linux\` | The 4.0 release, unpacked | Yes: KB unit files, counts, `parameters.lisp` |
| `opencyc-4.0W11\` | The 4.0 Windows release. Its KB unit files are byte-identical to the Linux release | **No new content** for reasoning |
| `opencyc-0.7.0\` | The 2002 release | Partly. Its `src\` is the client Java API (`org.opencyc`), not the engine. It adds `run\tests\inference-benchmarks.lisp` and a 2002 `parameters.lisp`, both used in section 5 |

**Cleanup, 2026-09-28, with your approval.** The Windows folder originally also
held a nested copy of the Linux release, a second copy of the Linux archive, and
11 Linux shell scripts, all verified identical to copies kept elsewhere. They were
moved to the Recycle Bin, 855 MB in total. Every kept folder now matches its
archive file for file: Linux 514 of 514, Windows 811 of 811, 0.7.0 1,219 of
1,219. The 0.7.0 folder holds a Windows executable, `run\bin\latest.exe`, which I
did not run.

**Upstream issue #2 is explained.** It reports the 4.0 archive as "not in gzip
format." The real file is valid gzip. The reporter almost certainly downloaded the
134-byte LFS pointer text instead of the archive.

---

## 2. The shape of the knowledge base, measured

### Census of the 2012 OWL export [measured]

| Measure | Measured | README claim |
|---|---|---|
| Terms | **239,264** | ~239,000 |
| Statements | **2,189,031** | ~2,093,000 triples |
| Collections | 116,822 | |
| Binary predicates (`owl:ObjectProperty`) | 18,014 | ~22,000 predicates in total |
| Higher-arity predicates, exported as individuals | e.g. 1,790 `TernaryPredicate` | |
| Terms with an English comment | 105,690 (44%) | |

### The engine's own counts for the same release [measured]

OpenCyc 4.0 ships plain-text count files beside its knowledge base, labeled
`KB 5022`:

| Count | Value |
|---|---|
| Assertions | 1,889,842 |
| Named constants | 188,111 |
| Function-built terms (NARTs) | 48,238 |
| **Stored deductions** | **337,085** |
| HL supports | 17,942 |
| Non-WFF records | 0 |

Constants plus NARTs total 236,349, within 1.2% of the export's 239,264 terms.
The export's statement count is higher than the engine's assertion count because
the export adds labels, English strings and external links.

**A figure not to reuse.** A third-party GitHub fork describes KB 5022 as holding
about 9 million assertions. The shipped count file says 1,889,842.

### The README's external-link count is internally inconsistent [measured]

The README states "~69,000 owl:sameAs links," then itemizes links summing to
about 80,976. The export holds 120,753. Every itemized figure matches closely; the
headline does not, and 34,060 unlisted links to OBO ontologies make up most of the
gap.

---

## 3. How the facts are organized [measured, verbatim]

### 3a. Collections have orders

> "FirstOrderCollection is the collection of all specializations of Individual."

> "Instances of SecondOrderCollection are collections of FirstOrderCollections."

### 3b. Collections are typed by what inference needs to know

| Meta-collection | Members |
|---|---|
| `ExistingObjectType` | 11,743 |
| `SpatiallyDisjointObjectType` | 10,547 |
| `OrganismClassificationType` | 7,591 |
| `FirstOrderCollection` | 7,091 |

> "the collection Dog is an instance of SpatiallyDisjointObjectType, since dogs
> do not spatially overlap."

Stating a property once on the type answers the question for every pair of
instances.

### 3c. The taxonomy is a heavily shared graph

| Measure | Value |
|---|---|
| `genls` edges | 193,309 |
| Roots | 1 (`Thing`) |
| Collections with more than one parent | **52,486 of 116,822 (45%)** |
| Longest path to `Thing`, typical | 13 to 26, peaking 16 to 21 |

The maximum of 59 is an artifact of one generated chain,
`(StringOfMaximumLengthFn N)`.

### 3d. About one term in six is built by a function

40,530 terms in the export (16.9%) are non-atomic, such as
`(AccessoryFn-Activity (PlayingFn Tennis-TheGame))`. The engine counts 48,238.
The 2009 source's documentation, via the Clyc port, explains the mechanism: a
closed function expression is **reified once** and recorded with `termOfUnit`,
after which it behaves like a named constant. [agent, secondary]

### 3e. Predicates carry their own constraints

| Constraint | Count |
|---|---|
| `arity` | 26,351 |
| `resultIsa` | 5,029 |
| `arg1Genl` to `arg3Genl` | 7,438 total |
| `arg3Isa` to `arg5Isa` | 6,800 total |
| `strictlyFunctionalInArgs` | 4,234 |

Predicates are also classed by logical property: 502 transitive, 334 symmetric,
232 reflexive, 200 antisymmetric.

### 3f. Negative knowledge is stored explicitly

| Construct | Count |
|---|---|
| `disjointWith` | 27,112 |
| `negationPreds` | 772 |
| `negationInverse` | 1,091 |
| `siblingDisjointExceptions` | 711 |

The last is defeasibility visible in data: named exceptions to a disjointness
rule.

### 3g. Microtheories, and what the export loses

> "each assertion in the Cyc knowledge base must be explicitly stated to be true
> in at least one microtheory."

> (genlMt SPEC-MT GENL-MT) "entails that everything that is true in GENL-MT is
> also true in SPEC-MT."

The hierarchy survives the export: 9,167 `genlMt` edges and 765 direct
`Microtheory` instances. **The assignment of each fact to its microtheory does
not.** OWL triples have no context slot, and only 19 `definingMt` statements
appear. Every one of 2.19 million statements arrives stripped of the context Cyc
requires.

### 3h. Rules are absent from the export, except in compressed form

No `implies` rules are exported. 835 rule macros are, covered in section 4.

---

## 4. What the knowledge base declares about its own reasoning [verbatim]

Cycorp's definitions, read from the export's own comments.

**Rule macros (835).** A sentence built from one "is treated by the Cyc system as
fully semantically equivalent to the (usually more complex) corresponding
sentence fitting the template. For example, genls is a rule-macro-predicate whose
expansion assertion is (expansion genls (implies (isa ?OBJ :ARG1) (isa ?OBJ
:ARG2)))."

**Predicates with special reasoning support (22).** `HLPredicate` is "the
collection of all Cyc predicates which have special HL support." Its members:
`isa`, `genls`, `genlPreds`, `genlInverse`, `genlMt`, `disjointWith`, `subsetOf`,
`negationPreds`, `negationInverse`, `equals`, `different`, `equalSymbols`,
`differentSymbols`, `elementOf`, `evaluate`, `termOfUnit`, `quotedIsa`,
`conceptuallyRelated`, `forwardNonTriggerLiteral`, `justification-Partial`, and two
`genls` variants. Almost all are graph or identity relations.

**Temporal graph support (27).** `SBHLTimePredicate` is "the collection of all
Cyc predicates which have special SBHL-time module support," including
`startsAfterEndingOf`, `temporallySubsumes`, `birthDate` and `dateOfDeath`.

**Engine code coupled to KB by name.** `CycLReformulatorConstant`: "The
reformulator mentions many of these constants in code, and depends on their
existence and correct usage in the KB to operate properly."

---

## 5. How Cyc finds answers quickly: a dated lineage

**What stays constant across all four snapshots** [synthesis]: queries are split
into subproblems; modules declare their own costs; a planner ranks work by a
weighted linear sum of heuristics; transitive hierarchies are handled by graph
modules, not rules. What changes is the machinery around those ideas.

### 5.1 The 2002 design (Cycorp manual, Cyc-10) [verbatim]

Source: `cycdoc/ref/inferencing.html`, "Last Update: 3/29/02."

**Why a new approach was needed.** "The Cyc knowledge base contains over 1
million assertions. Many approaches commonly taken by other inference engines
(such as frames, RETE match, Prolog, etc.) just don't scale well to KBs of this
size."

**Everything is converted to one internal form.** Formulas are "stored
internally, and reasoned with, in conjunctive normal form (CNF)." The payoff:
"using CNF as a canonical form means that you get modus tollens inferencing 'for
free'." One stored clause can prove any of its literals, "as if all three forms of
the rule were virtually present in the KB." Existentials become reified Skolem
functions.

**Canonical order makes lookup cheap.** "The advantage of a canonical literal
order is that it simplifies KB lookup; only a test for structural equality is
required to determine that 2 formulas are the same."

**Microtheories cut the search space.** Cyc "uses contexts called microtheories
to optimize inferencing by restricting search domains."

**The node-selection heuristics, as Cycorp lists them:**

| Heuristic | Strength |
|---|---|
| Favor nodes with fewer literals to satisfy | Normal |
| Favor nodes that have fewer free variables | Normal |
| Very weakly favor nodes higher up in the search tree | Very weak |
| Strongly favor nodes with no free variables left | Strong |
| Weakly disfavor nodes which include negative literals | Weak |
| Disfavor nodes which might be part of a unification cycle | Normal |
| Disfavor nodes less likely to be satisfied by KB lookup | Normal |

The reasons are given for each. No free variables means "there's a good chance
we'll be able to determine the truth value of the formula just by doing a KB
lookup." Negative literals are disfavored "because the KB consists primarily of
positive assertions." The lookup heuristic adds disfavor for each literal that
mentions "a predicate and a constant, but the constant has no index for the
predicate in the KB."

**How they combine.** "These heuristic rules act in concert, according to a
linear summation rule ... a chorus of agents, each of which corresponds to one
heuristic ... the agents shriek more or less loudly, according to how strongly
they disfavor the node. ... the open node with the lowest sum is expanded next."

**Which literal to work on.** "each HL module which applies to a literal must be
able to provide a heuristic estimate for how expensive it would be to apply that
module to the literal ... the literal which has the lowest heuristic cost is
favored most strongly."

**Search can pause and resume.** "The state of the search is maintained, so that
a search which suspends due to resource constraints can resume where it left
off." Forward inference uses depth-first search, "since forward inference
requires traversal of the whole search tree anyway."

**Equality is cheap by assumption.** "It's as if the KB had a unique names
assumption: objects with different names are assumed to be not equal, unless you
specifically override the assumption."

**What Cycorp chose to benchmark (2000)** [verbatim]. OpenCyc 0.7.0 ships
`run/tests/inference-benchmarks.lisp`, by Keith Goolsbey of Cycorp, dated
2000/02/01, "inference tests which are to be used as inference efficiency
benchmarks." Its speed test builds a 25-deep `genls` chain under `Thing`, a
two-level microtheory hierarchy, 1,023 people linked by a `parent` predicate
declared a `genlPreds` of a transitive `ancestor`, and one backward rule for
`sibling`. Every question is asked from the child microtheory, so each answer
must cross `genlMt`. **Cycorp's own efficiency test targets exactly the graph
paths the SBHL modules exist for** [synthesis]: deep taxonomy, context
visibility, predicate hierarchy and transitivity.

### 5.2 Indexing makes the cost estimates free (2002) [verbatim]

Source: `cycdoc/ref/kb-indexing.html`, March 2002.

Every term points to an index with slots for argument positions 0 to 5, for
positive and negative uses in rules, for rules stated in a microtheory, and for
everything else. Each slot is layered: **argument position, then predicate, then
microtheory, then the assertions.** Critically, **every layer carries a count**:
"( <count> . <pred-tree> )", "( <count> . <mt-tree> )", "( <count> .
<assertions> )".

**This is what makes the heuristics cheap** [synthesis]. The planner can read how
many assertions a lookup will touch from a counter already stored in the index,
without doing the lookup. The 2009 source implements exactly this [verbatim].
`removal_lookup_pos_cost` in `removal_modules_lookup.java` returns a fixed
`*cheap-hl-module-check-cost*` when the literal is fully bound, and otherwise
`inference_num_gaf_lookup_index`, the count read straight from the index.

Rules are indexed separately by direction: "( <forward> <backward> )".

### 5.3 SBHL: graph modules for hierarchies (2002) [verbatim]

Source: `cycdoc/ref/sbhl.html`, March 2002.

> "The SBHL modules are a growing collection of modules that support very fast
> inference involving subsumption tests with respect to particular subsumption
> hierarchies. Each module is associated with a particular hierarchy, and each
> hierarchy is defined by ground, atomic assertions in the KB having a particular
> transitive predicate."

They are "implemented with special datastructures and over fifty special-purpose
API functions." The hierarchies are kept apart deliberately: "the domains of
each of the SBHL predicates are disjoint," so collections, predicates,
microtheories and attributes each get their own graph.

**The graph path doubles as the explanation.** The manual's example of "why is a
dog an animal": "a dog is a kind of canine," "a canine is a kind of non-human
animal," "a non-human animal is a kind of animal."

### 5.4 The Balanced Tactician (2007) [agent]

Source: Taylor, Matuszek, Smith, Witbrock (Cycorp), FLAIRS 2007, read in full by
the research agent.

- The Balanced Tactician "heuristically selects tactics in a best-first manner"
  using "tactic type, productivity, completeness, and preference."
- Productivity is "related to the expected number of answers ... lower
  productivity tactics are typically preferred," valid from 0 to 10^8.
- It breaks problems into subproblems, "pruning entire branches of search based
  on expected productivity."

### 5.5 The 2009 engine, read in Cycorp's source [verbatim unless marked]

**Three roles** [agent, glossary]. The Strategist "reasons about the resource
constraints and determines which Tactician or Tacticians would be best to use";
the Tactician "maintains a store of work that can be performed, and chooses among
those tasks"; the Worker "does all the low-level work."

**Two kinds of step** [agent, glossary]. Removal "always strictly simplifies the
problem, by providing bindings for an open problem or by proving or failing to
prove a closed problem." Transformation replaces a literal using "a rule in the
Cyc KB." Removal is the fast lookup path; transformation is backward chaining.

**Module types** [verbatim]: `:removal`, `:removal-conjunctive`, `:meta-removal`,
`:transformation`, `:meta-transformation`, `:rewrite`, `:structural`,
`:meta-structural`. The shipped source includes 25 removal-module files: lookup,
`isa`, `genls`, `genlPreds`, transitivity, symmetry, reflexivity, evaluation,
abduction, conjunctive pruning and others.

**Completeness is declared, in four levels** [verbatim]:
`:impossible`, `:grossly-incomplete`, `:incomplete`, `:complete`.

**The Tactician's heuristics, with their weights** [verbatim, all thirteen]. From
`inference_strategic_heuristics.java`. Cycorp's own comment for each:

| Weight | Heuristic | Cycorp's comment |
|---|---|---|
| 1 | Shallow And Cheap | "Prefer tactics which are shallower ... and which are cheap, i.e. have a lower productivity." |
| 1 | Completeness | "Prefer tactics which are complete." |
| 250 | Occam's Razor | "The simplest explanation is best. Our measure of simplicity is the shallowest transformation depth." |
| 1,000 | Magic Wand | Disprefer incomplete removal tactics "expected to yield no answers ... it's a waste of time to execute them." |
| 10,000 | Backtracking Considered Harmful | After non-trivial conjunction tactics on a problem, "disprefer executing any more" |
| 10,000 | backchainRequired | "Prefer transformation tactics on backchainRequired predicates." |
| 10,000 | highlyRelevantAssertion | "Prefer proof paths using higher proportions of highlyRelevantAssertions." |
| 10,000 | highlyRelevantTerm | "Prefer working on problems that contain more highlyRelevantTerms." |
| 10,000 | # of Literals | "Prefer working on problems with a smaller number of literals." |
| 10,000 | # of Rule Literals | "Prefer using rules with a smaller number of literals." |
| 20,000 | Historical Utility | "Prefer proof paths using rules that have worked well in the past ... i.e. prior probability." |
| 20,000 | Rule Connectedness | "Prefer proof paths using sets of rules that have ... pairwise worked together in the past." |
| 300,000 | # of Skolems | "Prefer working on problems with a smaller number of skolem functions." |

**Compare this with 2002** [synthesis]. The 2002 "fewer literals" and "fewer
free variables" heuristics survive as "# of Literals" and "Shallow And Cheap."
What is new by 2009 is **learning from experience**: two heuristics, weighted
among the heaviest, reward rules that have succeeded before. The prior used when
there is no history is `0.02939361143247565` [verbatim], so a rule is assumed to
help about 3% of the time until it proves otherwise.

**Type checking: strict at the door, mostly off during search** [verbatim]:

| Setting | 2009 default | Meaning |
|---|---|---|
| `*WFF-MODE*` | `:STRICT` | Reject sentences that do not provably meet argument constraints |
| `*SEMANTIC-DNF-HL-FILTERING-ENABLED*` | `NIL` | Do not use argument types to filter inferences |
| `*RESIDUAL-TRANSFORMATION-VALIDATION-ENABLED?*` | `NIL` | Pruning of ill-typed conjunctions is off |
| `*TYPE-FILTER-FORWARD-DNF*` | `T` | Forward inference does type-filter |

Constraints are enforced when facts enter and when queries are asked. During
backward search they are mostly not used to prune. A Cycorp paper gives the
reason: "The generality of some domain constraints ensures that it is difficult to
identify implausible sub-queries." [agent, S16]

**Truth maintenance** [verbatim]. From `tms.java`: `tms-remove-argument` will
"Remove ARGUMENT for ASSERTION from the KB and perform necessary truth
maintenance," and `tms-remove-dependents` will "Remove all the deductions
depending on this ASSERTION." So a derived fact with another surviving
justification stays, with its truth value recomputed; one with none is removed,
and removal cascades. [agent, for the recomputation path]

**Argumentation combines discrete strengths** [verbatim]. `strength-combine` in
`argumentation.java`: a deduction's strength is the weakest of its supports. The
bodies that resolve true-versus-false conflicts were withheld as `missing-larkc`.
[agent, for the withheld detail]

### 5.6 What the shipped 2012 engine stored on disk [measured]

The OpenCyc 4.0 knowledge base is 65 unit files. Their names and sizes show what
Cyc keeps precomputed beside the facts:

| Unit file | Size | What it is |
|---|---|---|
| `assertion.cfasl` | 108.7 MB | The assertions |
| `indices.cfasl` + index | 29.9 MB | The argument-position indexes of section 5.2 |
| `sbhl-module-graphs.cfasl` + index | 27.3 MB | The SBHL hierarchy graphs of section 5.3 |
| `deduction.cfasl` + index | 18.4 MB | 337,085 stored justifications for truth maintenance |
| `sbhl-cache.cfasl` | 5.6 MB | SBHL caches |
| `sbhl-modules.cfasl` | 3.8 MB | SBHL module definitions |
| `cardinality-estimates.cfasl` | 2.6 MB | Precomputed counts for planning |
| `defns-cache`, `arg-type-cache`, `arity-cache`, `somewhere-cache` | 1.8 MB | Small lookup caches |
| `rule-utility-experience.cfasl` | **empty** | The history behind "Historical Utility" |

Three observations:

- **The planner's learning heuristics had nothing to learn from.** The per-rule
  success history ships empty, so in OpenCyc 4.0 the two 20,000-weight heuristics
  fall back to the 3% prior.
- **SBHL caches look selective, not a full closure.** I computed the full `genls`
  closure over the exported taxonomy [measured]: **5,974,958 ancestor pairs**
  against 193,309 direct edges, 31 times more, with a median of 47 ancestors per
  collection. The shipped `sbhl-cache` is 5.6 MB, a fifth the size of the 27.3 MB
  graph that holds only the direct edges [measured]. A store 31 times larger than
  the graph cannot fit in a file a fifth its size [synthesis]. This is
  **consistent with** the 2009 source's short fixed cache lists and **against**
  full `genls` precomputation in this release. It is not proof: the file encoding
  is unknown, and the export's edges may not match the engine's exactly.
- **Cycorp reversed its speed-versus-correctness default over the decade.** The
  2012 `parameters.lisp` [verbatim]: "Type checking occurs in SBHL modules iff
  this is NIL, which is slower but correcter," shipped as `NIL`, so checking is
  on. The 2002 OpenCyc 0.7.0 `parameters.lisp` [verbatim] shipped the same
  setting as `T`, so checking was off. **Early OpenCyc chose speed; later OpenCyc
  chose correctness**, and said so in writing.

### 5.7 Cycorp's current description (2019 to 2023) [agent]

- Reasoning time is split "90%" in HL modules, "9%" in meta-level rules and "1%"
  in meta-meta-level rules. [Cycorp Technology Overview, 2019]
- Module count "over 1,100." [2019, and Lenat and Marcus 2023]
- **An unresolved conflict about closures.** The 2023 paper says "the
  transitive-reasoning Heuristic-Level module redundantly stores the full closure
  of each transitive relation, ahead of time," with `physicallyLocatedIn` as its
  example. The 2019 overview is conditional about `genls`. The 2005 paper and the
  2009 source describe graph walks with selective caching. **Whether current Cyc
  precomputes the full `genls` closure is not established by any public primary
  source.** The 2012 disk evidence in 5.6 leans against it for that release only.

---

## 6. Additions and corrections to the existing research note

- **New: the node-selection heuristics, in Cycorp's words** (5.1). The existing
  note describes modules bidding; it now has the actual list and weighting rule.
- **New: the thirteen weighted heuristics of 2009, verbatim** (5.5), and the
  shift from purely syntactic heuristics toward learning from rule history.
- **New: counts at every index layer** (5.2) are what make "no index for this
  predicate" a zero-cost heuristic.
- **New: truth maintenance mechanics** (5.5). This was the note's first "could
  not establish" item. It is now established for 2009.
- **New: HL support is declared inside the knowledge base** (section 4).
- **Refined, not reversed: truth values.** The note says four composite values,
  not five, and that stands for assertions. Cycorp's glossary adds that together
  with "unknown" these "form the representations of truth at the HL level." An
  assertion carries one of four; an HL answer can also be unknown. [agent]
- **A version nuance on "bid on time," not a weakening.** The note's quote is
  primary and verbatim: Cyc "interrupts reasoners who exceeded their bid on how
  long they would take" [Lenat and Marcus 2023, p14]. The 2009 source measures
  module cost differently: `:cost` is the "estimated # of child nodes generated
  by HL-MODULE" [verbatim], with productivity alongside. Whether time-based bids replaced
  node-count estimates after 2009, or the 2023 prose describes the same mechanism
  loosely, is not established. *Correction recorded: an earlier draft of this
  report called the note's claim unsupported. That was wrong; the research pass
  missed the quote, and I repeated the miss.*
- **Confirmed and sharpened: no per-assertion numeric confidence.** Numbers do
  exist in Cyc, but every one found is for **search control**: productivity,
  heuristic weights, the 3% rule-success prior. None is a degree of belief in a
  fact. Cycorp contrasts its "pro/con argumentation" with Bayesian conditional
  probability rather than claiming to use it. [agent, verbatim for the prior]
- **Unchanged:** the 2023 figures (about 10,000 contexts, over 1,100 modules)
  describe current Cyc. OpenCyc 2012 is a smaller fragment.

---

## 7. What this means for EvidenceBasedDB

Two points, briefly.

**Your committed text export should be tested for context preservation.** Cyc's
own OWL export kept the taxonomy and dropped every fact's microtheory. The
mechanism your ADR-0014 names as the one structure that must stay stable is
exactly what Cyc's serialization lost.

**"Computed, never stored" needs one nuance.** Cyc stores cheap derived values on
purpose: index counts at every layer, cardinality estimates, SBHL graphs and
selected caches. It maintains them incrementally so that **planning** never has to
compute them. The principle in your README holds for facts a command can answer.
It should not stop you storing the counts and indexes that make choosing what to
look up cheap.

---

## 8. What I could not establish

- **Current Cyc's module inventory and defaults.** Cycorp's inference-algorithm
  page requires a login. Everything in 5.5 is 2009.
- **How contradictions are resolved, and whether "more specific trumps more
  general" is in code.** Those function bodies were withheld from LarKC.
- **Whether backward-query answers are stored as deductions.** No statement found
  either way.
- **The cfasl compression**, which limits the SBHL size argument in 5.6 to
  "consistent with."
- **How many tactic types there are.** The 2007 paper says "eight tactic types";
  the 2009 source enumerates six tactic types and twelve problem-link types. Not
  reconciled. [agent]
- **Whether time-based bids (2023 prose) replaced node-count cost estimates
  (2009 code)**, or describe the same mechanism loosely. See section 6.
- **Lenat and Guha 1990**, not consulted.

---

## Method notes

- OWL analysis: streaming parse of the 252 MB export; scripts `census.py`,
  `pass2.py` to `pass5.py`, `analyze.py` in a scratch folder.
- Source verification: every claim tagged [verbatim] from 2009 was grepped in the
  downloaded Java. Heuristic weights were extracted by script from
  `inference_strategic_heuristics.java`.
- The research agent's report is saved as
  [cyc-inference-research-agent-report.md](2026-09-28_F42_cyc-inference-research-agent-report.md),
  with one known error flagged at its top. Claims tagged [agent] were not re-read
  by me.
- The `genls` closure count in 5.6 was computed from the export's parent graph
  (`closure.py`).
