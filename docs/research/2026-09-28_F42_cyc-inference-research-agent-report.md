# Cyc heuristic inference: research agent report

> **Entered in `docs/research/` beside the Cyc review by Sprint 6 Task H (F42),
> 2026-10-03.** Its claims tagged `[agent]` are second-hand: none enters the store as
> an assertion until the source is read directly. See the 2026-10 handoff's
> `07-assertion-candidates-pending.md` and `04-pending-sources.md`
> (`D:\Data\Harold\EvidenceBasedDB\Handoff-2026-10\ebdb-handoff\`, outside version
> control).

**Provenance.** Produced 2026-09-27 by a background research agent working for
this session, and saved here unedited in substance so that every `[agent]` tag in
`2026-09-28_F42_cyc-kb-organization-and-inference.md` resolves to a file. **I did not re-read the
agent's sources**, except where the review marks a claim `[verbatim]` after
checking it against the downloaded Cycorp source.

**One known error in this report.** Under "Checks against the existing note" it
says no source was found for reasoners bidding on *time*. That is wrong: Lenat and
Marcus 2023, p14, says Cyc "interrupts reasoners who exceeded their bid on how
long they would take." The agent grepped that paper for terms and missed the
sentence. The review corrects this in section 6.

---

## Summary

- **Q1, Q5, Q6 are now established at mechanism level.** The main new source is
  Cycorp's own circa-2009 inference-engine code, released under Apache 2.0 to the
  LarKC project.
- **Q2 (SBHL caching) has an unresolved version conflict** between Cycorp sources
  dated 2005, 2009, 2019 and 2023.
- **Q7: no per-assertion numeric confidence was found anywhere.** Numeric values
  exist only for search control (productivity, per-rule historical success
  counts). They are not truth weights.

## Source key and read-depth labels

- **[G:x]** Cycorp glossary entry at `https://cyc.com/archives/glossary/x/`. Read
  directly (excerpt). WebFetch passes pages through a summarizing model; each
  quoted entry was re-fetched in "copy exactly" mode. Direct curl was blocked by
  Cloudflare, so quotes are not character-verified.
- **[CODE]** Cycorp SubL-to-Java source, "Copyright (c) 1995-2009 Cycorp Inc.",
  Apache 2.0, released to LarKC:
  https://sourceforge.net/p/larkc/code/HEAD/tree/trunk/platform/src/main/java/com/cyc/cycjava/cycl/
  - Read through the third-party Common Lisp port Clyc
    (https://github.com/white-flame/clyc, folder `larkc-cycl/`), whose authors
    have no Cycorp affiliation. Only original Cycorp docstrings and string
    constants were quoted, not the porter's comments or Clyc's AI-generated docs.
  - Many function bodies in the release are stubbed `missing-larkc`.
  - **[CODE-X]**: strings also checked against the SourceForge Java (tms,
    inference_strategic_heuristics, removal_modules_conjunctive_pruning, forward,
    sbhl_cache, inference_modules, and the kb_indexing `num-gaf-arg-index`
    docstring).
  - **[CODE-P]**: read in the port only.
  - Version: 2009, ResearchCyc lineage.
- **[T07]** Taylor (UT Austin); Matuszek, Smith, Witbrock (Cycorp). FLAIRS 2007.
  https://cdn.aaai.org/FLAIRS/2007/FLAIRS07-027.pdf. Read in full.
- **[R05]** Ramachandran (UIUC); Reagan, Goolsbey (Cycorp). AAAI Workshop 2005.
  https://cyc.com/wp-content/uploads/2019/07/First-Orderized-1.pdf. Read in full.
- **[S16]** Sharma, Goolsbey (Cycorp); Witbrock (Lucid AI). arXiv 1603.04402.
  https://arxiv.org/pdf/1603.04402. Read in full.
- **[S19]** Sharma, Goolsbey (Cycorp), 2019.
  https://www.cyc.com/wp-content/uploads/2019/07/AAAI-SharmaA.1646.pdf. Grepped.
- **[M06]** Matuszek, Cabral, Witbrock, DeOliveira (Cycorp), 2006.
  https://cdn.aaai.org/Symposia/Spring/2006/SS-06-05/SS06-05-007.pdf. Read in full.
- **[OV19]** Cycorp "Technology Overview", PDF created Dec 2019.
  https://cyc.com/wp-content/uploads/2021/04/Cyc-Technology-Overview.pdf. Read in
  full. Current Cyc.
- **[PH20]** Parisi and Hart, Cycorp, Apr 2020.
  https://cyc.com/wp-content/uploads/2021/04/bayesnetspaper.pdf. Read in full.
- **[LM23]** Lenat and Marcus, arXiv 2308.04445. **Grepped only**, which is how
  the time-bid sentence was missed.
- **[L10]** Lenat et al. (Cycorp), AI Magazine 2010, read at
  https://cogsci.northwestern.edu/documents/LenatEtAl_2010.pdf. Grepped.

---

## 1. Module inventory and dispatch

**Harness roles (glossary).**
- Harness: "takes in canonicalized queries and attempts to provide proofs for
  them by performing Removal and Transformation. The three main parts... are the
  Worker, the Tactician, and the Strategist." [G:inference-harness]
- Strategist: "reasons about the resource constraints and determines which
  Tactician or Tacticians would be best to use... cuts them off if they exceed
  their resource constraints." [G:strategist]
- Tactician: "maintains a store of work that can be performed, and chooses among
  those tasks, instructing a Worker to work on them." [G:tactician]
- Worker: "does all the low-level work such as creating problems and links,
  bubbling up proofs." [G:worker]
- Problem: stores a query plus "problem links expressing its logical or
  inferential connections to other problems; tactics indicating units of
  inferential work." [G:problem]

**Removal vs transformation.**
- Removal: "always strictly simplifies the problem, by providing bindings for an
  open problem or by proving or failing to prove a closed problem." [G:removal]
- Removal modules remove "one or more literals" from the query.
  [G:removal-modules]
- Transformation: a literal "is replaced by another literal or conjunction of
  literals," based on "a rule in the Cyc KB." [G:transformation]

**Module inventory (2009 code).**
- HL module types: `:removal`, `:removal-conjunctive`, `:meta-removal`,
  `:transformation`, `:meta-transformation`, `:rewrite`, `:structural`,
  `:meta-structural`; plus separate preference, forward, after-adding and
  simplification module files. [CODE-X]
- Meta-removal: "modules which execute other removal tactics on the same
  problem." [CODE-X]
- Removal modules are generic, universal, external or predicate-specific; the
  specific table is "A mapping between predicates and a list of modules which
  exclusively service that predicate." [CODE-X]
- Tactic types: `:removal :meta-removal :transformation :rewrite :structural
  :removal-conjunctive`. [CODE-P]
- Problem-link types: removal, transformation, residual-transformation, rewrite,
  join-ordered, join, split, restriction, union, disjunctive-assumption, answer,
  indirection. [CODE-P]
- Unreconciled: T07 says "eight tactic types"; the 2009 code lists 6 tactic types
  and 12 link types.

**Cost and completeness declarations.**
- Module properties include `:required-pattern`, `:applicability`, `:cost`,
  `:cost-pattern`, `:completeness`, `:complete-pattern`, `:exclusive`,
  `:supplants`, `:preferred-over`. [CODE-X]
- Cost is "the estimated # of child nodes generated by HL-MODULE when applied to
  OBJECT." [CODE-X]
- Completeness levels `(:impossible :grossly-incomplete :incomplete :complete)`,
  "sorted from least complete to most complete." [CODE-P]

**How the Tactician chooses.**
- T07: the Balanced Tactician "heuristically selects tactics in a best-first
  manner" using "tactic type, productivity, completeness, and preference."
- T07: productivity is "related to the expected number of answers... lower
  productivity tactics are typically preferred," valid 0 to 10^8.
- Code: "A balanced Tactician type which uses a depth-first stack for removal
  problems and a linear combination of heuristics to choose which
  transformation-motivated tactics to execute." [CODE-P]
- Heuristic scaling factors: shallow-and-cheap 1, completeness 1, Occam's razor
  250, magic wand 1000, backtracking-considered-harmful 10000, backchainRequired
  10000, highlyRelevantAssertion 10000, highlyRelevantTerm 10000, historical
  utility 20000, rule connectedness 20000, literal counts 10000, skolem count
  300000. [CODE-X]
- A default productivity cutoff exists, "above which tactics will be ignored
  instead of executed." [CODE-P]

**Decomposition.**
- T07: the harness "breaks a problem down into sub-problems and selects among the
  modules that may apply to each problem... pruning entire branches of search
  based on expected productivity."
- T07 tactic examples: "splitting a conjunction into multiple clauses, looking up
  the truth value of a fully-bound clause, or finding appropriate bindings for a
  partial sentence via indexing."
- S16 describes transformation and restriction links in the search graph.

**Synthesis (agent's inference).** R05's "pandemonium" model, where modules
"check whether they are applicable to the given subproblem and make a bid,"
corresponds to matching `:required-pattern`/`:applicability` to produce
candidate tactics, then scoring them. S16 and S19 formalize the scoring as
Σ wᵢfᵢ(s).

**Meta-reasoning and counts.** OV19: "90% of the time" on HL modules, "9%" on
meta-level rules, "1%" on meta-meta-level rules. Module counts: "approximately a
thousand" (T07); "hundreds to thousands" (R05); "over 1,100" (OV19, LM23).

## 2. SBHL

- SBHL modules "are removal modules that support efficient searches for Cyc's
  most frequently used transitive predicates (#$genls, #$genlMt, and
  #$genlPreds)", plus isa, disjointWith, genlInverse, negationPreds,
  negationInverse. [G:sbhl-module]
- 2009 code declares SBHL modules for genls, disjointWith, isa, quotedIsa,
  genlMt, negationMt, genlPreds, genlInverse, negationPreds, negationInverse.
  [CODE-P]
- Four dated data points, unresolved:
  1. **2005 [R05]:** for disjointWith, "it walks up the genls graph for Cube,
     marking each node as a goal," then walks the other term's genls checking for
     a goal hit; each link traversal does "another graph walk of the genlMt
     graph"; "for the common cases, the computation is cached."
  2. **2009 [CODE]:** the SBHL graph is a hash table of per-node link structures
     backed by a file vector; `:sticky`/`:swapout` "caching policies" govern
     swapping links into memory, not closure caches [CODE-P]. Search by marking:
     "Marks the forward true closure of NODE in MODULE with relevance determined
     by MT and TV" [CODE-P]. Closure caches cover only short fixed lists
     [CODE-X]: for genls, "The collections that have their specs cached", 11
     CycL-meta collections. General transitivity modules use "general
     transitivity graph walking of KB assertions" [CODE-P]. A TVA cache exists
     for transitiveViaArg [CODE-P].
  3. **2019 [OV19]:** some agents cache "transitive relations like during and
     subOrganizations"; for genls, "even more efficient if the transitive closure
     of the whole graph of that binary relation genls is--redundantly--
     precomputed and stored."
  4. **2023 [LM23]:** "the transitive-reasoning Heuristic-Level module
     redundantly stores the full closure of each transitive relation, ahead of
     time," example physicallyLocatedIn.
- Conclusion: in 2005 and 2009, genls/isa/disjointWith were answered by
  marking-based graph walks with selective caching. Whether current Cyc
  precomputes the full genls closure is not established by public primary
  sources.

## 3. Indexing

- GAF-argument index keyed term, then argument position, then predicate, then
  microtheory: "Return the number of gafs indexed off of TERM ARGNUM PRED MT."
  [CODE-X]
- Predicate-extent index keyed predicate, then microtheory. [CODE-P]
- Rule index types "(:pred, :ist-pred, :func, :isa, :genls, :genl-mt, :exception,
  or :pragma)", split by literal sense. [CODE-P]
- Best index is the smallest count: "First look for mt-insensitive counts,
  then... try to do better by finding a smaller mt-sensitive count." [CODE-P]
- Lookup module cost is the index count, feeding the Tactician's productivity
  estimate. [CODE-P; since verified verbatim in the review]
- Terms with few assertions use a flat index, converting to "the more complex
  form" past a threshold. [CODE-P]
- R05: the transitivity module "performs a graph walk over the indexing
  structures of the KB." [G:hl-support]: the KB-HL-support object "is used to
  improve indexing and caching, thereby making the TMS process faster."

## 4. Argument-type pruning

- The WFF Checker "is invoked when CycL sentences are asserted or edited, and when
  they are issued as queries," checking constraints "such as those imposed by
  #$argIsa, #$argQuotedIsa, #$argGenls." [G:wff-checker]
- 2009 default `*wff-mode*` is `:strict`. [CODE-P; since verified verbatim]
- Example constraint `(arg1Isa biologicalMother Animal)`. [M06]
- Inference-time filtering exists but is off by default for backward inference:
  `*semantic-dnf-hl-filtering-enabled*` NIL; `*residual-transformation-validation-
  enabled?*` NIL ("Temporary control variable, should eventually stay T");
  `:residual-transformation-non-wff` module; problem-store validation default
  `:none`; `*type-filter-forward-dnf*` T. [CODE-P/X; defaults since verified]
- Cycorp on why arg-types prune weakly: "The generality of some domain
  constraints ensures that it is difficult to identify implausible sub-queries."
  [S16, footnote 4]. S16 learns per-rule type restrictions that re-order rather
  than prune.

## 5. Forward vs backward

- "Direction is a value attached to every assertion": `:forward`, `:backward`,
  `:code` ("HL module performs reasoning, assertion not used in regular
  inference"). "Most tools... use the following defaults: GAFs have direction
  :forward and rules have direction :backward." [G:direction] No evidence that Cyc
  chooses direction automatically.
- A `:forward` assertion "may participate in both forward and backward
  inference"; a `:backward` one "in backward inference only." [G]
- A forward trigger literal "will cause the rule to fire when an assertion
  matching it is added to the KB"; non-trigger literals suppress firing. [G]
- Forward inference runs with `:transformation-allowed? NIL`, so antecedents are
  proved by removal only. [CODE-X] Conclusions cascade through a queue. [CODE-P]
- R05: "2.3 of the 2.5 seconds are spent in forward inference."

## 6. Truth maintenance

- "The Cyc TMS relies on the fact that each assertion has all of its arguments
  recorded in the data structure." "When a Deduction is added to the KB, TMS
  records the list of Supports that can be used to re-justify the deduction."
  Some supports are re-evaluated only on "Redo TMS". [G:truth-maintenance-system]
- A deduction "is an argument supporting a deduced assertion... lists all the
  premises (assertions, including one rule)." [G:deduction]
- `tms-remove-argument`: "Remove ARGUMENT for ASSERTION from the KB and perform
  necessary truth maintenance"; recomputes truth value from remaining arguments;
  if none remain, `tms-remove-dependents`: "Remove all the deductions depending on
  this ASSERTION," recursively. [CODE-X; since verified verbatim]
- "truth maintenance is always on." [R05]
- Argumentation is discrete: monotonic beats default; asserted default wins among
  defaults; contradiction bodies are `missing-larkc`; a deduction's strength is
  the weakest of its supports (`strength-combine`). [CODE-P]

## 7. Numeric confidence

- **Per-assertion confidence: none found.** Strength has 2 values; with truth,
  4 composite values; "Together with 'unknown', these form the representations of
  truth at the HL level." [G:strength] Cycorp contrasts Cyc with Bayesian
  conditional probabilities, describing "pro/con argumentation." [PH20]
- **Numbers that exist are for search control:** productivity 0 to 10^8 [T07];
  per-rule considered/success counts and
  `*average-rule-historical-success-probability*` 0.0294, described as "prior
  probability" [CODE; value since verified verbatim]; S16 answer-count
  regression; S19 Monte Carlo step selection.
- KB content: `(increases-Generic ... likelihood)` is qualitative [M06]; a
  clinical KB holds heuristics "about degrees of risk and likelihood of outcomes",
  representation unspecified [L10].
- Do not cite LM23's "probability decay curve" as Cyc implementation; it sits in
  the desiderata section, not "How Cyc handles."

## Checks against the existing note (as reported by the agent)

- "1,100+" modules: confirmed [OV19, LM23].
- Budget interrupts: confirmed [G:strategist; T07].
- "Bid on time": the agent reported no source. **This was wrong; see the
  provenance note at the top.**
- Four truth values: confirmed, plus "unknown" at the HL.
- "More specific trumps more general": not visible in 2009 code; bodies withheld.

## Could not establish (agent)

1. Current module inventory, defaults, genls closure strategy; Cycorp's
   inference-algorithm page requires login; web.archive.org was blocked.
2. Contradiction resolution and specificity preference in code (`missing-larkc`).
3. Whether backward-query answers are stored as deductions.
4. Lenat and Guha 1990.
5. Siegel, Goolsbey, Kahlert, Matthews, "The Cyc System: Notes on Architecture"
   (2004, Cycorp); ResearchGate 403; Academia.edu untried:
   https://www.academia.edu/50247031
6. Sharma and Forbus 2013 (Northwestern).
7. Per-assertion probability: searched all 141 glossary titles, the cyc.com
   publications list, the 2009 file tree, PH20, OV19, LM23, M06, L10, and two web
   searches.

## Sources

- Glossary index: https://cyc.com/glossary/ ; entries under
  https://cyc.com/archives/glossary/{hl-module, removal-modules, removal,
  transformation, sbhl-module, tactician, strategist, worker, tactic, problem,
  inference-harness, cyc-inference-engine, direction, forward-inference,
  backward-inference, forward-assertion, forward-trigger-literal,
  forward-non-trigger-literal, truth-maintenance-system, deduction,
  deduced-assertion, dependent, support, hl-support, justification, argument,
  strength, argument-constraint, wff-checker, well-formed-formula,
  inference-parameter, rule-macro-predicate, heuristic-level, tva}/
- LarKC Java: https://sourceforge.net/p/larkc/code/HEAD/tree/trunk/platform/src/main/java/com/cyc/cycjava/cycl/
- Clyc port: https://github.com/white-flame/clyc
- Papers as linked in the source key. Cycorp publications:
  https://cyc.com/publications/
