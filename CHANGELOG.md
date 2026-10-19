# Changelog

Policy: updated in the SAME commit as the change it describes, under
`## [Unreleased]`, grouped by date, newest first. Format:
`- **type**: Description (Issue #N / PR #N)` with type in
feat | fix | docs | test | chore | process.

**Workflow step 8.1.1 reconciles this file BEFORE backlog refinement, every
delivery cycle.** The same-commit policy held for six days in the consumer
repository and then silently stopped for eight, across seven sprints. A policy
that depends on remembering at the moment of committing is the class of rule
this project keeps having to replace with a step.

## [Unreleased]

### 2026-10-18 onward (Sprint 10, in progress)

- **process**: Sprint 10 Manual Validation decisions recorded (2026-10-19):
  ADR-0004 A10 approved as written (Q1 = 1); a registry answer with nothing
  recordable stays due (Q2 = 1); ML libraries stay in review (Q3 = 1); live
  discovery re-run now (Q4 = 2); F57 closing rule at the retrospective
  (Q5 = 1). The team lead rejected a validation step that asked them to run
  a shell command to check the code-edit hook: a hook fires only on
  Claude's own tool calls, so the step proved nothing. The workflow's
  Manual Validation rule now says so; Claude ran the check itself (not
  blocked)

- **chore**: Sprint 10 Phase 5.3 Manual Validation handed over
  (2026-10-18). Tasks A to J done with every fresh-eyes review answered;
  suite 1,053 passed locally; CI green. Three changed commitments restated
  (Task E's `--ext-diff`/`--textconv`; Task I's 9 unread records; Task J
  measured on Sprint 9's pool, 13 to 3). Aimeur 2007 kept on the
  hand-download list (ICML's archived link no longer resolves); Q1 to Q5
  asked

- **fix**: Task A (F81, #102) -- the code-edit hook no longer blocks a read
  of a code file followed by another command's `-i` (`sed -n 1,5p x.py;
  grep -i y z`): the flag and target search stops at the editor's own
  `;`, `&` or `|`, outside quotes. A second `sed -i` on the same line is
  now found on its own (it was hidden inside the first match). Nine tests,
  proven by three injections
- **fix**: Task A review (2026-10-18; fresh-eyes and automated security
  review) -- the cut in 021d2a8 let seven in-place edits through (a
  backslash escape, a `2>&1` redirect, `$(...)` or backticks before the
  file). The cut now models those, and the search fails closed: when the
  editor's own text has the flag but names no code file, the whole line
  is searched. A read inside `bash -c "..."` followed by `grep -i` passes.
  Eleven cases, each proven against 021d2a8 or by injection. A second
  security review found `bash -c "sed "'-i ...'` still passed (a quote
  closed mid-word continues the word); fixed, proven by two injections.
  A third found quotes inside a file name or the awk keyword
  (`store/x'.py'`, `in"place"`) passed, a gap older than Task A; every
  check now reads the text with quotes removed. That exposed an older
  offset bug: a path inside an editor's, copy's or tee's own text was
  placed against the `cd`s by its offset in that text, so an edit of a
  scratch file after a `cd` out of the repository was blocked. Fixed;
  six cases, each proven against 6690c39
- **process**: Task B (F88, the F39 release for Sprint 10, #103) -- models
  and pricing pages read 2026-10-18: no change since F67 (same four ids,
  prices, context, output and retirement dates); every tier re-verified.
  Sprint 9's reader outcomes logged (accurate quotes and numbers; added
  conclusions the main defect); the reading protocol now requires a
  separate `reader_inference` field. Two tests, each proven by injection
- **docs**: Task C (F50, #104) -- dated amendment to the Cyc research
  document's point 7: Cyc stores a count at every index layer
  (`removal_modules_lookup.java`, line 84, re-read in the engine source);
  a stored count is allowed here only beside its data, updated with it,
  and checked by a test that recomputes it
- **fix**: Task D (F86, #105) -- the DOI probe never asked DataCite:
  after a Crossref 404 it labeled its result DataCite and returned empty,
  so a DataCite DOI could never record a primary answer under ADR-0005
  A9. It now sends the DataCite request and records status (from
  resourceTypeGeneral), a preprint relation as `version_of` (not Zenodo's
  all-versions IsVersionOf) and affiliations. The Zenodo record
  (DOI:10.5281/zenodo.19985473) answered: preprint, QDR Labs; its clock
  reset (next re-check 2028-04-16). Snapshot as of 2026-10-18: 157 of 256
  DOI records hold no primary answer, none due before mid-2027. Two
  tests, proven by two injections
- **fix**: Task D review (2026-10-18) -- a DOI registry that answered with
  nothing the store records (an unmapped type such as "Text", no relation,
  no affiliation) was reported as "no answer"; the re-check report now
  says it answered. It still stays due: no `publication_status` value
  means "the registry states none" (raised for Manual Validation). A null
  DataCite affiliation name no longer raises. Two tests, two injections
- **fix**: Task I review (2026-10-18) -- two values I passed in my own
  read were WRONG: Carleman's complexity is T^2 q poly(log T, log n,
  log 1/epsilon)/epsilon, not "polylogarithmic in T, n and 1/error"; the
  lower bound's threshold is R of at least the square root of 2 (the text
  layer drops the root sign; my quote edit then cut the quotes at "R ≥ 2",
  so both checks passed a wrong value). Also: the readout-versus-gate
  measurement cut from a HIGH limit statement; a survey's physics claim and
  Martin's two values (proved only for one- and two-qubit terms) to LOW;
  Zuchongzhi's F2 errors with their Hartree average; Khairy's median;
  three quotes for stated figures; HIGH is now an explicit reviewed list
  (39), tested. Valdez is retracted: not for the hand-download list.
  Re-applied; 13 assertions corrected. Two injections
- **fix**: Task J review (2026-10-18) -- the ml topic rule also dropped
  scikit-learn and PyTorch, and the generic tensor topic "Machine Learning
  and Algorithms" could drop a tensor-network learning paper: a learning
  term in the title now keeps an ml record, and that tensor topic is
  removed (13 excluded records now fall to 3, not 2; none accepted lost).
  Dropped records are kept in the saved JSON; the check script states that
  its "moved up" list is an approximation; a test runs main with an
  off-topic work. One injection
- **feat**: Task J (F87, #111) -- the discovery streams drop, before
  ranking, the off-topic kinds the team lead excluded at Sprint 9 Manual
  Validation: OpenAlex topics per stream (software libraries and
  metaheuristics in ml; spin-qubit hardware and a medical survey in qml;
  materials, superconductivity, density estimation and pseudo-ensembles in
  tensor) and a codebase release note. Measured on Sprint 9's own pool
  (`scripts/sprint10_f87_filter_check.py`, no request): 13 excluded records
  in the top 25 lists before, 2 after (the single-photon platform paper and
  the black-hole paper share a topic with accepted ones); no accepted record
  lost; 11 move up for review. Dropped records are listed in the review,
  never hidden. Fourteen tests, two injections
- **feat**: Task I (F89, #110; the F57 release for Sprint 10) -- the 74
  most-cited unread `qml` records: 65 with a free copy read by nine Sonnet
  5.5 readers under the `reader_inference` rule, then the coordinator's
  read of every value against its quoted passages. 64 entered at `read`
  with 216 assertions (42 HIGH, 2 MODERATE, 172 LOW); 1 refused (a
  workforce review); 9 with no free copy stay `seen` for the hand-download
  list. Nine quotes corrected to the source's exact characters, two values
  rewritten (Innan's two AUCs are different curves; Aimeur's bound as
  printed), three contexts corrected. Snapshot as of 2026-10-18: 224
  records at `read`, 793 assertions, 1,969 at `seen` or `screened`. Eight
  tests, three injections; intake section 29
- **process**: Sprint 10 Tasks F, G and H missed INTAKE_WORKFLOW.md
  section 26 (Sprint 9 retrospective I3): their scripts wrote before
  checking quotes, which only the live-store tests then did. Each now runs
  `check_quotes()` before any write, and a test plants a quote not in the
  source and expects the refusal. No stored quote was wrong. Intake
  section 27 records the three tasks' entries
- **fix**: Task H review (2026-10-18) -- no wrong figure, but four
  overstatements corrected: the inferred link to Dirac named "the
  instances sent to Dirac devices", while Phase 2's Dirac-3 work uses its
  continuous and integer solvers, where the 1-or-minus-1 bound does not
  apply as written (a same-day correction in the answer document); the
  two-way partitioning value gains "W symmetric" and "in general";
  Gurobi's value drops "exact" and adds the second stopping rule
  (MIPGapAbs, default 1e-10); the verified sentence's "relaxation or dual
  bound" is a dual bound. The figure test reads only Gurobi's two entries
  and treats 1e-4 as one token; the store test compares every field. One
  injection
- **feat**: Task H (F83, #109) -- per-instance optimization bounds
  sourced: Boyd and Vandenberghe's Convex Optimization (the authors' free
  copy, downloaded to Papers with SHA-256; sections 5.1.5, 5.2.2 and
  5.5.1 read) and Gurobi 13.0's MIPGap entry (saved to References). Four
  assertions: weak duality without convexity, the two-way partitioning
  dual and SDP bound, the duality gap as a certificate, and Gurobi's
  relative gap. The ceilings answer document gains a dated amendment
  making section 5 point 5 verified; applying the SDP bound to Dirac's
  Ising and QUBO instances is marked inferred. Four tests, two
  injections; the figure check reads only the pages read (a whole-book
  check passed an injected figure)
- **fix**: Task G review (2026-10-18) -- the entry below put a WRONG
  statement in the store for about 15 minutes: the B4 value said
  Dirac-3's 0.895 and 0.901 fell outside the band [0.8832, 0.9095]; both
  lie inside it, and it is the Dirac-3S cosines that fall outside (so
  Phase 2's falsifier fires). Corrected and re-applied, with the band
  quote added; a test now computes which cosines lie in the band. The
  fineness value also gains Phase 2's caveat that the cloud response had
  no raw-values field to check the post-processing inference against.
  One injection
- **feat**: Task G (F85, #108) -- Phase 2's Dirac-3S verification
  (`docs/phase2/F142_DIRAC3S_VERIFY.md`) entered by the inbound path at
  Phase 2 commit e126dbd (revised after the card's c141a57; the same blob
  at HEAD 98f9671): a reference record and four HW assertions (B4 twin
  optimum on two seeds, returned weights finer than the 0.005 step with
  the cause unverified, AUPRC unchanged, per-sample cost at schedule 2).
  Phase 2's own limits carried in each value. No relation linked: by
  A8 (b) none confirms or contradicts a whole existing claim (output
  versus input resolution; different problem sizes); each value names the
  related assertion. Seven tests, three injections
- **fix**: Task F review (2026-10-18) -- the entry below was WRONG on one
  point: "scales better than cubic" was QCi's own conclusion (the page
  says "better than O ( n 3 )"; the coordinator's check searched for the
  word "cubic" and missed the notation). The value now states it with its
  quote. Also corrected: the portfolio value gave the page's example
  period as the run (the backtest ran 2022-01-13 to 2022-12-30), and the
  reader's "(modes)" gloss is cut. ADR-0004 A10 correction: filing the
  QC-7 article's two claims under `platform:dirac-1` is an inference from
  its one Dirac 1 sentence. The descriptions test now holds its own list
  (its first version compared against the script's set, so it could not
  fail as claimed). Two injections
- **feat**: Task F (F84, #107; Class 1, Q1 = 1, Q3 = 1) -- ADR-0004 A10
  adds `platform:dirac-1` (A8's rule: one context per QCi system; A8's
  "revisit" answered: no claim spans the systems). The nine QCi sources
  Sprint 9 refused (seven "Device: Dirac-1" pages, the UAS case study,
  the QC-7 article) are retagged from `platform:dirac-3`, read and
  entered: 12 assertions, 6 vendor descriptions MODERATE and 6 vendor
  results LOW. The coordinator's read cut two reader conclusions the
  pages do not state ("scales better than cubic"; "64 binary variables").
  Every quote and stated figure checked by test; seven tests, four
  injections; F80's refused-stays-seen test narrowed to the other two
- **process**: Task E (F82, #106; Class 1, team lead Q2 = 1) -- the
  never-write hook's threat model stays accidental writes. Now blocked
  with a guarded path: an abbreviated long option of a writing one
  (`--outp`, `--ext`), a short cluster with O (`-nO`), `--ext-diff` and
  `--textconv`. Pager, editor and config variables and command names
  built from variables are named in the docstring as outside the model.
  Eight blocked and four allowed cases; each blocked case passed against
  the previous hook; two injections
- **fix**: Task E review (2026-10-18) -- the O rule blocked reads whose
  search value held an O (`log -SOAuth`, `-GOne`, `grep -e -Option`), and
  the older `--output.*` rule blocked `--output-indicator-new`; all now
  pass. `--ext-diff` and `--textconv` are no longer blocked (a CHANGED
  COMMITMENT from the approved Task E line): git runs the guarded
  repository's own configured programs on a plain `git diff` by default,
  so that block guarded nothing, and such a program is that repository's
  configuration, not this session writing. Two injections. A security
  review of that fix found one shared list of value-taking options let
  `grep -n -O x`, `grep -LO`, `grep -GO`, `grep -3O` and `diff -M
  --output=...` through; the lists are now per subcommand, digits continue
  the scan, and a bare closing quote after `"git"` is not read as the
  subcommand. Five cases; one injection. A third review: a long writing
  option after a value-taking flag was skipped as its value
  (`shortlog -n --output=...`); such a word is now never skipped (fail
  closed). Two cases; one injection

- **docs**: Sprint 10 Phases 1.5 to 3 (2026-10-18) -- scope selected (all
  ten non-HOLD items; F88 and F89 released from F39 and F57); Phase 2
  gates passed; `CHECKLIST-Phase2-pre.md` back-filled for Sprint 9, which
  Phase 1.2 missed; `SPRINT_10_PLAN.md` drafted with Q1 to Q3 and the
  draft PR opened

- **docs**: Sprint 10 Phase 1 (2026-10-18) -- the team lead merged PR #88
  into develop and PR #100 to main; `sprint-9` tagged on PR #100's merge
  commit (270961e); carry-forward cut `feature/20261018_Sprint_10` from
  the Sprint 9 branch; sprint status advanced; CHANGELOG reconciled (three
  Sprint 9 entries added below: the slate, the plan draft and the Manual
  Validation hand-over)

### 2026-10-14 to 2026-10-18 (Sprint 9, PR #88, merged to develop 2026-10-18 and to main via PR #100 the same day; tagged sprint-9)

- **fix**: Review of the I7 commit (2026-10-18) -- the CI stop check could
  trap a session on a failure it cannot fix; a stop citing a criterion, a
  "STOP:" line or BLOCKED now reports it. The local-only guard also watches
  os-level launches and an option's value (`--in=PATH`); its limits
  (existence checks, collection time, a moved store) are documented. Tests
  added for the data folder, cwd and arguments, and gh's real fail-open
  path; injection-proven (Issue #99 / PR #88)
- **process**: Sprint 9 retrospective I7 (team lead, 2026-10-18, Q1 = 2).
  Prevention: `tests/conftest.py` gives every test without `live_store`
  the machine CI sees -- pdftotext and any path under the data folder or a
  sibling repository raise FileNotFoundError -- so a missing marker fails
  locally, not on CI. It found a fourth such test at once
  (`test_resolvers.py`, a sibling-repository read that skipped on CI),
  now marked. Control: the Stop hook blocks a stop in Phases 5 to 7 while
  any check on the sprint's PR is failing or running. Both proven by
  injection (`tests/test_local_only_guard.py`,
  `tests/test_block_procedural_question_stop.py`) (Issue #99 / PR #88)
- **fix**: CI red on PR #88 since 2026-10-15 00:31 (070137e), on every push
  including the Manual Validation hand-over, unnoticed until 2026-10-18:
  three "every number is in the source" tests (F46, F78, F79) read local
  PDFs with pdftotext or the local Phase 2 repository without the
  `live_store` marker CI deselects. Marked; CI green at deb726d (Issue #94)
- **fix**: PR #88 Copilot review (2026-10-18) -- `view.py paper` computes
  the whole-store corroboration map once, not once per yielded assertion;
  test proven by injection
- **fix**: Review of the post-hand-over commits (2026-10-18) -- a corrected
  context now replaces the stored ones (added beside them, the wrong one
  stayed); the F80 script uses `sync_assertion` too (its own list compared
  six fields); the sync tests cover every compared column and pin the
  not-compared group (moving a field there turned nothing red); a missing
  `assertion_fields` row is a named error. Injection-proven
- **process**: Sprint 9 retrospective I3 and I4 (2026-10-17) -- I3:
  `store/quotes.py` is the one quote normalizer and check (moved out of a
  test module); `plain` applies Unicode NFKC, so ligatures and the micro
  sign fold in one step; the Task E script checks every quote before it
  writes. Three quote tests compared raw quotes and now normalize both
  sides. I4: `store.ingest.sync_assertion` compares every `AssertionRecord`
  field (the list checked against the dataclass on every call) and only
  adds contexts, documents and relations; the Task E script uses it for
  both of its syncs (its coordinator sync also skipped the quotes).
  INTAKE section 26. Tests proven by injection
- **process**: Sprint 9 retrospective I1 (2026-10-17) -- the Stop hook
  `block_procedural_question_stop.py` also blocks a status-footer last line
  whose time is more than 5 minutes from the clock, on every branch and in
  every phase; it reads `last_assistant_message`, which the Stop input
  carries. Tests proven by injection
- **process**: Sprint 9 retrospective I5 (2026-10-17) -- the
  shell-metacharacter hook's block message leads with the exit-code form
  (`> log 2>&1; rc=$?`) when the blocked expansion is `${PIPESTATUS[...]}`,
  blocked in Sprints 8 and 9 alike; behavior tests added, proven by injection
- **docs**: Sprint 9 retrospective recorded (2026-10-16); team lead: apply
  I1 and I3 to I5 now, I2 and I6 not needed. PR #88 body carries Closes #89
  to #99
- **feat**: Task E's closed papers (Sprint 9 Task E, Issue #93,
  2026-10-16) -- Chen et al. 2025 read from the team lead's download (12
  assertions); Han and Verdu 1994 recorded not obtainable; team lead Q6 = 1:
  its content entered from free sources, Scarlett's equation (108) as a
  coordinator assertion and Chen, Guntuboyina and Zhang 2016 (JMLR, open
  access) entered through the door and read in part (9 assertions); the
  answer document gains a dated addendum. The Task E sync now compares
  quotes; the quote normalizer expands three more ligatures. INTAKE
  section 25
- **feat**: Manual Validation decisions applied (Sprint 9, 2026-10-15) --
  ADRs approved as proposed; Q1 = 1 recorded on ADR-0004 A9 (an
  unrecorded-organization pair still counts, labeled; no code change); Q3
  = 1: the three QCi admission-against-interest assertions upgraded low ->
  moderate with their cost and the decision (Task G, Issue #95); Q4 = 1:
  87 F62 candidates entered at `seen` through the door by
  `scripts/sprint9_f62_enter_seen.py`, 5 retitled preprints by journal DOI
  after the title check refused them (Task J, Issue #98; INTAKE section
  24); Q2 = 2 and Q5 = 2 carded as F86 (the Zenodo record) and F85 (Phase
  2's Dirac-3S verification). Tests injection-proven
- **docs**: Sprint 9 Manual Validation handed over (2026-10-15, c04450c,
  reconciled 2026-10-18) -- ADR-0005 A9 and A10 and ADR-0004 A9 for
  review, and questions Q1 to Q5 with a recommendation each
- **fix**: F62 review (Sprint 9 Task J, Issue #98) -- a Semantic Scholar
  answer counts only for the same title (a wrong-paper answer had won); a
  second pass for refusals; refused candidates listed apart so a refusal
  cannot hide a paper; no bonus for a stream's own context, `dirac` and
  `braket` anchored; books routed to `Books\` under that folder's naming;
  particles and hyphens kept in file names; the key dropped on a redirect
  to another host; tests for each, injection-proven, and a vacuous key
  assertion replaced by an output-file check. Re-run recorded on the F62
  card
- **feat**: `view.py paper` shows cites and cited-by (Sprint 9, F55, Issue
  #96, daf1fa8)
- **feat**: F62 discovery with the approved rubric (Sprint 9 Task J, Issue
  #98) -- `scripts/discover_candidates.py` now ranks by citations per year
  cross-checked against Semantic Scholar (paced, backoff on 429, arXiv
  fallback), x1.5 for a store-context match, duplicate titles collapsed,
  unchecked counts after checked ones; writes 25 per stream for review and
  a hand-download list with every free-copy search; the pilot stays behind
  `--pilot`. Run of 2026-10-15 recorded on the F62 card. Tests
  injection-proven
- **fix**: F55 and F56 review (Sprint 9, Issues #96 and #97) -- the
  corroboration parser read "Name, I. (Affiliation)" and accented names
  wrongly, both toward independence: fixed and tested, with organization
  names matched by leading words; a non-vendor pair with no recorded
  organizations now says "not compared" (dated corrections to ADR-0004 A9
  and ADR-0005 A10); a CI round trip exports `corroborated_by`; a rollback
  test for the migration; injection proofs recorded for nine more tests;
  one test that could not fail removed
- **docs**: F51 hold checked (Sprint 9 Task K, Issue #99) -- all three
  copies of the CVQBoost findings document unchanged (SHA-256
  `425358a7b4cec71f...`, "Last updated 2026-08-04"); stays HOLD; recorded on
  the F51 card
- **feat**: F56, the computed "corroborated" flag (Sprint 9 Task I, Issue
  #97) -- ADR-0004 A9; `store/resolvers.py` `corroboration`: a supporter at
  equal or higher certainty that is independent (different papers, named
  authors, organizations by name and initials; a vendor's own claim needs
  both organizations named); shown in `scripts/view.py` and exported as the
  derived `corroborated_by`, never stored and never moving certainty. Two
  same-source pairs the first build counted on the live store (QCi under
  two names; two project documents cited by repository name) are now
  tested cases. 1 of 17 supported assertions flagged (snapshot,
  2026-10-15). `tests/test_f56_corroboration.py`, injection-proven
- **feat**: F55, `cites` links (Sprint 9 Task H, Issue #96) -- ADR-0005
  A10; `cites` added to `source_links` by a table rebuild
  (`scripts/migrate_sprint9_cites_link_type.py`, backup first) with a
  `to_id` index; `store/links.py` reads a link from both ends;
  `scripts/sprint9_f55_cites.py` asked Crossref for 807 DOIs (750 answers
  carried a reference list; cached outside git) and wrote 5,620 links, 793 of 2,102 papers at an end
  (snapshot, 2026-10-15); tests for the migration, matching, the cache and
  a live recompute of every stored link, injection-proven
- **fix**: F80 review (Sprint 9 Task G, Issue #95) -- fresh-eyes review
  of 9f71f19: five values corrected (one contradicted its source, one
  carried a figure from another experiment); vendor descriptions graded
  MODERATE (only one of seven was); three grades set by what the claim is;
  Henriet's routing result typed as the vendor's own; Cao and Henriet
  applicability moved to `qc`, Miri's rationale corrected; Miri and Wang
  conflicts of interest recorded; the Kaggle dataset-size assertion dropped
  (a determinate fact already held); a re-apply now syncs quotes, contexts,
  claim types and provenance, with a live test that the store matches the
  script; admission-against-interest candidates listed for Manual
  Validation; F84 card, F65 comment and INTAKE section 23 corrected.
  233 assertions (snapshot, 2026-10-15)
- **feat**: F80 slice read and entered (Sprint 9 Task G, Issue #95) --
  `scripts/sprint9_f80_reading.py`: ten first-pass readers
  (`manifests/sprint9_f80_reads/`), then the coordinator read every quoted
  passage in context; 65 of 76 records promoted to `read`, 234 assertions
  (snapshot, 2026-10-15). The coordinator's read corrected seven values and
  stripped an unsupported clause from eqc-models. 11 records refused with
  reasons; the nine that name Dirac-1 are carded as F84. Vendor claims about
  their own product are graded LOW (see the review fix above for descriptions). The
  17 new Dirac-3 assertions are classed against the Dirac-3S guide
  (F65 `CLASSED`). `tests/test_f80_slice_reading.py`, each test proven red
  by injection
- **feat**: F80 slice selected and its copies fetched (Sprint 9 Task G,
  Issue #95) -- `scripts/sprint9_f80_slice.py` records the 76-record slice
  in `manifests/sprint9_f80_slice.json` (the 26 consumer-context records
  and the 50 most-cited `qml` records, 263 to 4,662 citations); counts from
  OpenAlex by arXiv DOI, then by the store's probed journal DOI (1,146 of
  1,521 counted; Semantic Scholar's unauthenticated batch refused every
  attempt and is not used; the 375 uncounted are recorded as a limit);
  `scripts/sprint9_f80_downloads.py` fetched 21 free arXiv copies into
  `Papers\`, each stamp-checked; one repository shallow-cloned
- **feat**: F46, the 20 remaining pending facts (Sprint 9 Task F, Issue
  #94) -- each checked against its primary source and entered, merged or
  refused with the reason (`FACT_DISPOSITIONS` in
  `scripts/sprint9_f46_pending_facts.py`): 15 entered (most corrected: the
  handoff wording overstated its source in 10: nine corrected, one entered in part), 2 merged into assertions
  already read (F-402, F-604), 3 not entered (F-001: the cited restatement
  of Holevo does not exist; F-008: the handoff's own arithmetic, Han and
  Verdu pending; F-603: the repository was never identified). 12 sources
  promoted to `read` with a subagent row and the coordinator's partial row
  (Zhao et al. read in part even at first pass; its absence claim carries
  the search as its scope); 53 assertions; two arXiv PDFs downloaded by
  `scripts/sprint9_f46_downloads.py` (committed with d14520a); tests check
  quotes, figures, dispositions, read rows and idempotence, each proven by
  injection. The answer document's family counts refreshed after the
  "samples" fix
- **fix**: F78 fresh-eyes review (Sprint 9 Task E, Issue #93) -- the
  answer document's false "lowest Bayes error simulated was 1 percent" is
  replaced by the positive-rate gap it meant (Theisen reports flow-model
  Bayes errors down to 1.07e-4, checked in Table 1); its verified section no
  longer restates ideas cut from the values ("its ceiling is knowable",
  noise "caps accuracy"), which moved to section 5 as inference; one false
  stored sentence removed (Butt's abstract does give the attack scope);
  proved results now keep the first-pass reader's stated downgrade (11
  assertions; Butt's Theorem 1 is moderate), Tschirschwitz's hedge restored
  (low), Butt's unlike comparison dropped, three unlabeled reader
  conclusions cut; read-row details now say which papers were re-read after
  a full read and that absences rest on the first-pass read; the script
  corrects stored values and read details; the family sort no longer reads
  "samples" as sampling
- **docs**: the F78 answer document,
  `docs/research/ceilings-ml-and-optimization.md` (Sprint 9 Task E, Issue
  #93) -- the ways to find a ceiling for an ML dataset, each with what it
  needs and when it fails, citing store assertions; two verified routes
  for optimization bounds; a computed sort of the store's QML-advantage
  claims into families (`scripts/qml_advantage_families.py`: optimization
  is 16 of 85, snapshot 2026-10-15); F46's nine ceiling facts; inferred
  steps for HSBC kept apart; a test that every cited id is in the store;
  F83 carded (per-instance optimization bounds have no source yet)
- **feat**: F78, the ceiling-estimation group read and entered (Sprint 9
  Task E, Issue #93) -- 28 CE records plus Ishida and Theisen promoted to
  `read` (29 of the 31 CE records are now at `read`, with McDermott), each with two read rows: a Sonnet 5.5 first-pass read of the
  whole source (`subagent`) and the coordinator's `partial` read of the
  opening and every quoted passage in context; Boyd, Dhama, Butt and
  Tschirschwitz also carry Claude's full reads of 2026-10-13. 140
  assertions from 257 verbatim quotes, certainty by the GRADE convention
  (73 high, 3 moderate, 64 low); 2 reader assertions dropped and the
  readers' own inferences cut from 36 values, each with its reason in
  `scripts/sprint9_f78_ceiling_reading.py`; 26 local paths added with
  SHA-256; F46's nine ceiling facts each entered, merged or refused with
  the reason; Chen 2025 and Han and Verdu 1994 stay `seen`, awaiting the
  team lead's hand download. Tests check every quote, every figure in a
  value, the cuts, the read rows and idempotence, each proven by injection
- **feat**: F48, honest local paths (Sprint 9 Task D, Issue #92) --
  `scripts/check_local_sources.py` lists every local source that is
  missing, changed or unhashed (the re-check's own `check_local`, so the
  two agree) and records a SHA-256 where none was; 112 hashes recorded, so
  124 of 127 local-access records carry one and 3 are folders (snapshot
  2026-10-15); a moved-file test and a never-overwrite test, each proven
  by injection, and a live test that no local file lacks a hash. Found on
  the way: Task A's Phase 2 record held only the committed blob's hash (LF)
  while the working copy is CRLF, so it read as changed; its evidence now
  leads with the working copy's hash
- **feat**: F74, re-check correctness (Sprint 9 Task C, Issue #91) --
  ADR-0005 A9: a re-check counts only when the paper's own primary source
  answered (arXiv for arXiv, Crossref or DataCite for a DOI, the page for a
  URL, a present file for a local copy); `pdftotext` failures are "tool
  failure" and a probe that raised is "probe failure", never findings about
  the paper; each run lists "primary source did not answer (stays due)" for
  Manual Validation; five tests, each proven by injection. Snapshot
  2026-10-15: 1 of 2,100 papers has probes but no primary answer
- **process**: the never-write hook states its threat model (accidental
  writes, not evasion); F82 carded for the remaining evasive forms the third
  automated security review listed
- **fix**: second automated security review of the never-write hook
  (2026-10-15, Issue #89) -- a git read subcommand that writes through an
  option (`--output`, `-O`, `--open-files-in-pager`, `-c`, `--config-env`)
  now blocks when a guarded path appears, and `git` is found after a quote,
  backtick or brace, not only after whitespace; each proven by injection
- **fix**: the never-write hook's git check is fail-closed (automated
  security review of 2b90897, 2026-10-15) -- when a guarded path appears,
  every git invocation must name a read subcommand (show, log, diff,
  status, grep, rev-parse and a few more); any other subcommand blocks,
  whatever global options come first; proven by injection (Issue #89)
- **feat**: F68 and F69 (Sprint 9 Task B, Issue #90, 070137e) -- the door
  reads old-style arXiv ids (`quant-ph/0405098`) and DOIs with parentheses,
  tests proven by injection; the five Massoli entries refused on 2026-10-12
  entered at `seen` by `scripts/sprint9_f68_massoli_rerun.py` (their
  `updated_reason` names F61's script, whose entry builder it reuses, with
  the Sprint 9 tag); the "Cerezo" PDF in QMLPapers\NonArxiv is Nathan
  Wiebe's New J. Phys. perspective, entered by DOI with its SHA-256
  (INTAKE_WORKFLOW.md section 20)
- **fix**: F79 fresh-eyes review (Sprint 9 Task A, Issue #89) -- the
  never-write hook now blocks `git -C <repo> <write>` and the git verbs
  that change a tree (checkout, restore, stash, apply, tag), plus
  Remove-Item, Copy-Item, Move-Item, Rename-Item, tee and `sed -i`, each
  proven by injection; two inbound assertions corrected ("exact" dropped;
  the computed means and the unchecked bar basis stated); the inbound
  script now corrects an existing record whose text changed; a test checks
  every number in a value against the source; the Phase 2 prompt names
  the gap as Edit/Write only
- **feat**: F79, the Phase 2 exchange (Sprint 9 Task A, Issue #89) --
  `hsbc-qfraud-phase2` named as the active consumer; the never-write hook,
  its memory file and CLAUDE.md cover Phase 2's repository and Claude Code
  project directories, test proven by injection; INTAKE_WORKFLOW.md
  section 19 sets the inbound path (read at a named commit via `git show`)
  and the outbound prompt shape; first inbound record
  `hsbc-qfraud-phase2-b4-b5-hardware-result` with four HW assertions, quotes
  verified against the pinned blob; a prompt drafted for Phase 2 to close
  its guard's gap on this repository's memory directory; F81 carded (the
  code-edit hook blocks read-only `sed -n`)
- **docs**: Sprint 9 plan approved (2026-10-15, team lead) with Q1 to Q9
  answered; F78's repositories shallow-cloned (Q2 = 2); re-check failures
  reported at Manual Validation (Q4); the first read-for-claims slice
  widened to 76 records (Q7 = 2); F57 now releases 74 records per sprint
  until none remain at `seen` or `screened` (PR #88)
- **docs**: Sprint 9 scope selected and plan drafted (2026-10-14, 27c9d94
  and 81b87e2, reconciled 2026-10-18) -- 12 items selected at refinement,
  F79 corrected to free reads both ways and no writes; Tasks A to K drafted
  with decisions Q1 to Q9; F80 released from F57
- **docs**: Sprint 9 Phase 1 (2026-10-14) -- the team lead merged PR #84
  and PR #77 into develop and PR #86 and PR #87 to main; `sprint-8` tagged
  on PR #87's merge commit; carry-forward cut `feature/20261014_Sprint_9`
  from the Sprint 8 branch; sprint status advanced; CHANGELOG reconciled
- **process**: every PR title starts `Sprint N: ` (team lead,
  2026-10-14): `Sprint N: <sprint name>`, `Sprint N: F<n> <title>`,
  `Sprint N: Develop to Main`; workflow 3.3.1 and the release step
- **docs**: F78 and F79 carded (2026-10-14, team lead) -- F78 reads the
  whole ceiling-estimation (CE) group in full, enters it, downloads every
  paper with no local PDF into `Papers\` outside the repository, and
  answers whether a dataset or optimization problem can be done better;
  F79 records that hsbc-qfraud-phase2 and this repository consume each
  other by pasted prompt only, and extends the never-write rule and hook
  to Phase 2

### 2026-10-10 to 2026-10-14 (Sprint 8, PR #77, merged to develop 2026-10-14 and to main via PR #87 the same day; tagged sprint-8)

- **docs**: Sprint 8 Phase 1 (2026-10-10) -- carry-forward cut
  `feature/20261010_Sprint_8` from the Sprint 7 branch after PR #68
  (develop) and PR #76 (main); sprint status advanced in the "Phase n.n
  Name" format; CHANGELOG reconciled for Sprint 7's last three days;
  Sprint 7 completeness sweep; design-document currency checked; candidate
  slate presented
- **docs**: F66 carded (2026-10-10, team lead at Phase 1.4, target Sprint
  8) -- make develop the default branch, with main as the release branch
  changed only by a tagged develop-to-main PR; CI to run on PRs into both
- **docs**: Backlog refinement (2026-10-10, Phase 1.5) -- Sprint 8 scope
  selected: F65, F63, F64, F60, F61 and an F39 release (F67, Haiku 5.5);
  priorities renumbered in steps of 10 (Q2 = 1); F49 closed without
  implementation as moot under ADR-0004 A7 (Q3 = 1)
- **docs**: Sprint 8 plan drafted (2026-10-10, Phase 3) -- Tasks A to E
  (F67, F65 with F63, F64, F60, F61) with planning pre-flights and six
  decisions for approval; F67 carded (the F39 release, Haiku 5.5); F66 and
  F67 under a new "Carded during Sprint 8" heading
- **docs**: Sprint 8 plan approved as amended (2026-10-12) -- F66 added as
  Task A; decisions Q1 to Q6 absorbed into the task lines; issues #78 to #83
- **chore**: F67, the F39 release for Sprint 8 (Task B, #79, 2026-10-12) --
  the haiku tier now names Haiku 5.5 (`claude-haiku-5-5`, tiered by prompt
  length); the Developers role moves to it (Q6 = 1); the other tiers
  re-verified unchanged; a release note records Claude Mythos 5.1 as listed
  and unassigned
- **docs**: F66 Phase A inspection (Task A, #78) -- findings held for the
  Manual Validation hand-over; no change made
- **feat**: F65 with F63 (Task C, #80, 2026-10-12) -- the Dirac-3S User
  Guide Rev A entered and read in full (SHA-256 recorded); ADR-0004 A8 adds
  the context `platform:dirac-3s`; 17 Dirac-3S assertions and F63's two
  Dirac-3 admissions, every quote verified against the local PDFs by
  `tests/test_f65_dirac3s_reading.py`; the 19 prior Dirac-3 assertions
  classed against the guide; admission-against-interest upgrades held for
  Manual Validation
- **feat**: F64, the staggered 12-month re-check (Task D, #81, 2026-10-12)
  -- `store/recheck.py` computes each paper's section (1 to 24, from its
  id's hash), last check and next re-check; `probe_reference_fields.py
  --due` checks only the papers due, every kind (local files by presence
  and SHA-256), and prints three lists (re-pull, withdrawn, newly
  published); arXiv version read from the abstract page against the local
  copy's first-page stamp; `view.py paper` shows the schedule; ADR-0005
  A7; workflow Phase 1.3 updated
- **fix**: Task C fresh-eyes review (2026-10-12) -- eight assertions'
  wording, quotes or reasons corrected to say only what the quoted text
  supports (sample cap, integer range, ceiling, FPGA, coherent states,
  CE/FCC, entanglement); two classes changed to "confirmed in part"; the
  `supports` links from copied Dirac-3 text marked as vendor restatements;
  the context description no longer says "successor"; the supports test
  checks both directions
- **fix**: Task D fresh-eyes review (2026-10-12) -- a folder or an
  unreadable local file no longer stops the re-check; "newly published"
  counts only a change from preprint or from no status; an unreadable local
  stamp is listed as "version unread"; the report is written as it grows and
  reloaded by a resumed run; ADR-0005 A7 states the 10-to-22-month first
  round; tests added for the exact-10-month boundary, terminal statuses and
  the run's plumbing
- **feat**: F60 (Task E, #82, 2026-10-12) -- every QMLPapers manifest row
  checked against its file's first-page arXiv stamp
  (`scripts/sprint8_f60_manifest_check.py`, read-only): 1,397 match, one
  mismatch (the Asfaw row; the paper is arXiv:2108.01311, already in the
  store), 38 with no stamp, 28 PDFs with no row; report in
  `docs/sprints/SPRINT_8_F60_MANIFEST_CHECK.md`
- **feat**: F61 (Task F, #83, 2026-10-12) -- the Massoli et al. survey
  list mined: 184 entries, 137 entered at `seen` through the door, 28
  already in the store, 1 duplicate, 18 refused with reasons; the list's
  repository linked to the survey as `dataset-of`; report in
  `docs/sprints/SPRINT_8_F61_MASSOLI_LIST.md`; F68 carded (old-style arXiv
  ids and DOIs with parentheses); SPRINT_CHECKLIST 1.3 names the due
  re-check
- **docs**: Manual Validation answers (2026-10-13) -- ADR-0004 A8 and
  ADR-0005 A7 approved; F69 carded (the Cerezo NonArxiv paper, Q8 = 1);
  the F60 report corrected: the Asfaw PDF was already present in
  `QMLPapers/Workforce` under 2108.01311, so no download was made
- **feat**: Q7 applied (2026-10-13, #80) -- the five admission-against-interest
  candidates raised from moderate to high on the team lead's decision; each
  reason says what the claim cost QCi to disclose; the two F63 reasons name
  Dirac-3; a re-apply keeps the upgrades (test proven to fail by
  injection). Not recorded in the CHANGELOG at the time; added here
- **docs**: Sprint 8 retrospective recorded (2026-10-13) -- team lead
  verbatim, Claude feedback in 16 categories, improvements I1-I6 proposed.
  Not recorded in the CHANGELOG at the time; added here
- **fix**: QPU balance removed from the store (2026-10-13, team lead) --
  `hsbc-dirac3-allocation-1681-after-sizing-probes` held a Dirac-3
  QPU-seconds balance that was stale after QCi's grant of 2026-10-09; a
  balance is answered by the account, not stored.
  `scripts/sprint8_remove_qpu_balance.py` removed it (backup taken first);
  Sprint 6's script no longer carries it; `tests/test_qpu_balance_not_stored.py`
  (both tests proven to fail)
- **process**: Sprint 8 retrospective I1 (2026-10-13, team lead: all six
  now) -- a question with numbered options is never titled as yes/no, and
  every decision question ends with "Recommend N"; added to CLAUDE.md's
  question rules, the workflow's Phase 5 hand-over and the memory file
- **process**: Sprint 8 retrospective I2 (2026-10-13) -- a "no local copy"
  finding is computed: `store.recheck.local_copies` searches all of
  QMLPapers and completes a new-style id one digit short; the F60 check
  lists every copy for a mismatch or missing row (the real run now names
  the Asfaw copy in `Workforce`); workflow Phase 4 note; tests proven to
  fail by injection
- **process**: Sprint 8 retrospective I3 (2026-10-13) -- one shared builder,
  `store.ingest.admission_upgrade_reason`, writes every
  admission-against-interest upgrade reason with "costly to disclose,
  because ..." and refuses an empty cost; the F65 script uses it (its
  stored reasons unchanged); the F47 test stays as the backstop; test
  proven to fail by injection
- **process**: Sprint 8 retrospective I4 (2026-10-13) -- `--due` alone
  lists the papers due from stored dates and sends no request; the
  re-check is `--due --probe`; `--due --apply` without `--probe` is
  refused; ADR-0005 A8; workflow Phase 1.3 and checklist 1.3 updated; test
  proven to fail by injection
- **process**: Sprint 8 retrospective I5 (2026-10-13) -- the existing
  `block_unraw_escape.py` hook now also blocks a shell edit of a
  repository code file (`sed -i`, `perl -i`, a redirect or `tee`,
  PowerShell `Set-Content`/`Add-Content`/`Out-File` onto a `.py` or
  `.sql`); heredoc bodies and scratch files outside the repository pass;
  bypass token `allow_shell_code_edit`; workflow Phase 4 names the rule;
  tests proven to fail by injection
- **process**: Sprint 8 retrospective I6 (2026-10-13) -- work approved
  during an open sprint goes on the sprint branch unless the team lead
  asks for a separate PR; added to workflow 6.6 and to the
  branch-from-develop hook's block message, before its bypass token
- **fix**: I1-I6 fresh-eyes review (2026-10-13) -- the I5 hook now also
  blocks sed after `xargs`, `env` or `bash -c`, `perl -0pi`, `1>` and `&>`,
  and no longer loses later lines after a `<<<` here-string; it no longer
  blocks a PowerShell write whose target is not code, a `git commit -m`
  message, or a relative path after a `cd` out of the repository (12 cases
  added, each red against the first version); the upgrade-reason builder
  avoids a double period; the QPU-balance test reads either quote style in
  any scripts subfolder; the removal script refuses on every
  non-cascading link
- **fix**: I5 hook edge-case pass (2026-10-13, team lead asked whether the
  edge cases had been searched; they had not) -- now also blocks `>|`,
  any fd redirect, `tee` with options or several files, `dd of=`, `cp`,
  `mv`, Copy-Item and Move-Item onto code, `awk -i inplace`, `ruby -pi`,
  `sed -i''`, `find -exec sed -i` and `ls-files | xargs sed -i`,
  `[IO.File]::WriteAll*`, `New-Item -Value`, every repository code type
  (.py .sql .yml .ini, plus .yaml .toml .ps1 .sh) in any case, and a `cd`
  back into the repository; no longer reads PowerShell here-strings,
  `gh api -f body=` values or full-line comments; the bypass token counts
  only outside data; known limits listed in the hook; 26 new cases red
  against the previous version
- **docs**: F71 carded and planned as Sprint 8 Task G (2026-10-13, team
  lead Q1 = 2, #85) -- F65's four recovered items; plan amendment with
  pre-flights (robots.txt allows all; 2,854 sitemap URLs; `lastmod` is no
  change signal), risks and Definition of Done; F70 skipped because the
  workflow quotes the consumer repository's F70
- **feat**: F71, Sprint 8 Task G (2026-10-13, #85) -- the Dirac-3S release,
  the Technical Reference module (its Continuous Solver Benchmarking review
  read in full) and the Dirac-3 product page (now the Dirac-3S page) entered
  as five references at `read`; two QCi arXiv papers at `seen`; 11
  assertions under `platform:dirac-3s` (the review's all-optimal headline
  against its own Table 6, its two ub = 10 counts, which device ran); four
  admission-against-interest candidates held for the team lead; the site
  diff computed (`scripts/sprint8_f71_qci_site_check.py`: 4 changed, 5 new,
  1 gone, 43 recent in uncovered sections, qci-client v5.0.3); report
  `docs/sprints/SPRINT_8_F71_QCI_SITE_CHECK.md`; QCi's PDFs kept with the
  other references outside the repository (team lead); tests proven by
  injection
- **fix**: PR #77 review findings (2026-10-13; Claude pr-review-toolkit
  code, test-coverage and silent-failure reviews; Copilot found none on
  #77) -- site check: a section of one or two pages keeps its own change
  (the menu rule needs 3 pages), ambiguous matches listed, redirects and
  failed fetches reported, undated pages counted recent, a sitemap index
  and unknown flags refused; re-check: the record's own local path first
  (`recheck.local_pdf`), an invalid `--due` date refused, a fresh run no
  longer repeats an old report's findings and a retry replaces a record's
  lines, `--progress` needs `--report`; `view.py` shows "now" for an
  undated paper; F71 script: exact id match and SHA-256 on every local
  copy; hook: a heredoc a shell runs is scanned, `truncate`, the `py`
  launcher and python writes onto .sql caught, an internal error fails
  open with a warning; workflow I2 sentence corrected to what the search
  covers; F74 carded (a partial answer resets the re-check clock; a tool
  failure blames the paper)
- **docs**: Sprint 8 close-out (2026-10-13) -- `SPRINT_8_SUMMARY.md` with
  Actuals; master plan Last Completed Sprint and summary row; checklist
  reconciled; retrospective notes Task G
- **chore**: sprint status note (2026-10-13) -- times corrected to the
  commit times; the merge-readiness message's omitted F71 question
  disclosed and recorded; the team lead's EDB query (a proved performance
  ceiling) answered from six papers read locally, nothing written to the
  store; Zhao et al.'s JMLR PDF saved beside its CE-7 reference, outside
  the repository
- **docs**: F71 Class 2 decided (2026-10-14, team lead = 6) -- none of the
  four admission-against-interest candidates upgraded; all stay at
  moderate; the F71 report says so

### 2026-10-13 (F66, Sprint 8 Task A, PR #84)

- **process**: F66 (Sprint 8 Task A, #78, PR #84 into develop,
  2026-10-13) -- develop set as the GitHub default branch; `Closes #N`
  now closes issues on a merge into develop; the release step (PR
  develop -> main, merged by the team lead, then tag the merge `sprint-N`)
  written into workflow 8.1 and SPRINT_PROCESS.md; ADR-0001 A2; CI stays
  on PRs into develop only (team lead decision); tags `sprint-1` to
  `sprint-7` pushed on the seven past main merges
- **docs**: PR #84 review fixes (2026-10-13) -- "team lead", not "owner",
  merges develop -> main, as everywhere else in the process docs (Copilot);
  ADR-0001 A2's lead-in now matches its two changes and one decision not
  to change (Claude code review)

### 2026-10-06 to 2026-10-10 (Sprint 7, PR #68, merged to develop 2026-10-10 and to main via PR #76 the same day)

- **docs**: Sprint 7 Phase 1 (2026-10-06) -- carry-forward cut
  `feature/20261006_Sprint_7` from the Sprint 6 branch after PR #54
  (develop) and PR #67 (main), carrying F58's card, which was committed
  after the merge; CHANGELOG reconciled; Sprint 6 completeness sweep;
  design-document currency checked; candidate slate presented
- **docs**: Sprint 7 scope selected (team lead, 2026-10-06): F59, F58, F52,
  F53, F54, F44, F45; `SPRINT_7_PLAN.md` drafted with pre-flights (the arXiv
  API still answers 429; arxiv.org's robots.txt sets a 15 s crawl delay) and
  decisions Q1-Q9
- **docs**: Sprint 7 plan approved (2026-10-06): no export (Q1 = 2), one
  backup location (Q2 = 1), every arXiv request 18 s apart (Q7), F after C
  and G after F (Q8); issues #69-#75 = Tasks A-G
- **process**: F59, F39 release for Sprint 7 (Task A, Issue #69) -- the
  models page re-read 2026-10-06: every tier's id, price, context, maximum
  output and retirement date unchanged; Haiku 4.5 still "not sooner than
  October 15, 2026", no successor Haiku listed. The Developers role and the
  one Haiku task pattern move to Sonnet 5.5 now, ahead of the date
- **feat**: F58, the store out of the repository (Task B, Issue #70) --
  ADR-0004 A7, ADR-0003 A2 and ADR-0005 A5 first; the store and its 35
  backups moved to `D:\Data\Harold\EvidenceBasedDB\store` (verified backup
  first, copied with the SQLite backup API, integrity and counts checked);
  `store.script_paths` reads one setting (override `EBDB_STORE_DIR`);
  `export/` removed from the repository and no export is written (Q1 = 2;
  history kept, Q3 = 1); `regenerate_export.py --out` and
  `rebuild_store_from_export.py --from` as on-demand tools; backup
  retention's rule 3 is now "one of the 10 newest" (its own injection test
  found that `parsed[-0:]` is the whole list); real-data tests carry the
  `live_store` marker (locally a missing store fails them; CI deselects them
  by name); `test_export_currency.py` retired; CLAUDE.md, the workflow and
  `.gitignore` updated
- **fix**: Task B fresh-eyes review findings (Issue #70) -- CI was red: off
  Windows the default `D:\` store path is one relative segment and resolved
  inside the checkout, so `store_dir()` now refuses it there and names
  `EBDB_STORE_DIR` (new test, proven by injection); 17 historical scripts
  committed their write and only then hit the retired export, so those
  `regenerate` calls are gone and a test keeps them out (proven by
  injection); both public export writers refuse a folder inside the
  repository, not only `regenerate`; every live fixture opens the store
  read-only and the shared session dump is read-only; the append-only
  `updated_reason` check also anchors at 3bf2eda, the last export, so Sprint
  6's records are covered; stale docstrings corrected
- **feat**: F52 machinery (Task C, Issue #71) -- every arXiv request, API
  and site, 18 s apart (Q7); a per-session cap of 240 arXiv requests on the
  shared clock that raises before the request over it (Q6); the abstract
  page as the probe source while the API refuses, answering status, version
  of record and access in one request (Q5), the API retried once per
  session; a session ends early after 3 arXiv no-answers in a row and two
  such sessions stop the run; `--sessions` pauses 2 hours between caps;
  `--progress` makes a stopped run resumable; values that differ from the
  stored probe print as DIFFERS. Five guards proven by injection
- **fix**: Task C fresh-eyes review findings (Issue #71) -- a record arXiv
  refused was marked done and lost its status for good: it now stays
  unfinished and is retried in later sessions, up to 3, and `--unprobed`
  selects an arXiv record without a status; the session count and the
  pause are saved beside the progress file so a restart honors them; a
  Crossref failure no longer discards the registry's answer; an arXiv 403,
  or an open page that is not the paper's, records no access; a 2-minute
  SQLite busy timeout; a new run waits the full interval before its first
  arXiv request (found live: 0.3 s after the previous run); `--site`
  forces the abstract page. Live check: the page matched the API on the
  pilot's 12 papers (8 published with their DOIs, 4 preprints) and saw all
  6 recorded withdrawals, 4 of which the API comment never showed; so in
  API mode the abstract page (fetched anyway for access) is parsed too and
  its withdrawal wins, at no extra request
- **feat**: F54, the 30 unlinked repository notes (Task E, Issue #73) --
  `scripts/sprint7_f54_recover_repo_notes.py` linked 23 of them (24 links,
  24 new records): 9 by the owner's repository list (punctuation lost at a
  line wrap), 9 by the paper's own PDF text (cut-short names), 1 by GitHub
  search with its query (the cited owner is gone; the repository belongs to
  a co-author), 4 Zenodo records by DOI. Each link's evidence says how it
  was found. 7 reported again with what was tried: 4 repositories gone, 1
  candidate rejected (Julia, where the paper says Python), 1 on Gitee (no
  route), and `2108.0131`, whose PDF is a different paper (arXiv:2108.00131)
- **feat**: F54's last item (Task E, Issue #73) -- arXiv:2108.00131
  (Radhakrishnan et al., PNAS), the paper actually in the mislabeled
  QMLPapers file, entered through the door in a pause of Task C's run (one
  arXiv request), with its code `uhlerlab/ntk_matrix_completion` linked
- **feat**: F62 card and read-only discovery pilot (team lead, Q11 = 1 and
  3) -- `scripts/discover_candidates.py` ranks candidate papers from
  OpenAlex metadata in four streams (ml, qml, tensor, fraud), drops what the
  store holds, and writes its report outside the repository; the OpenAlex
  key is read from `OPENALEX_API_KEY` and sent only in a header (guard
  proven by injection). Pilot of 100 found stream-precision and
  citation-quality issues, recorded on F62
- **feat**: F35's held-back repository candidates, the optional slice of
  F54 (Task E, Issue #73) -- the 78 with score >= 0 screened (subagent, read
  only) into `scripts/sprint7_f35_screen.json`: 42 own, 26 third-party, 10
  unsure; every "own" row checked independently (repository resolves 40 of
  40; sentence in the paper's PDF 40 of 40); `sprint7_f35_screen_links.py`
  applied 39 links and 38 new records, each carrying the paper's sentence
  and how it was found. Unsure and third-party rows held back
- **feat**: F53, probes each cycle and a stale report (Task D, Issue #72)
  -- `probe_reference_fields.py --stale` lists every probe measured before
  the cycle start (computed from the sprint branch's date) and exits 1 when
  any is stale; hand-recorded readings are never stale; `--refresh`
  selects stale and unprobed records; Phase 1.3 of the workflow runs the
  refresh within F52's cap, then `--stale`. Guard proven by injection
- **feat**: F52, the bulk probe run (Task C, Issue #71) -- 1,524 records
  probed in 12 capped sessions over 36 hours (2026-10-06 21:36 to
  2026-10-08 09:49), 0 errors, no arXiv refusal; 107 statuses from the
  abstract page where the API did not answer; affiliations on 13 of 1,301
  API answers. ADR-0005 A6 records F52 and F53 as built and the
  measurements; Phase 1.3's runtime estimate corrected from 20 to 36+ hours
- **feat**: F44, the eight Cycorp papers (Task F, Issue #74) -- downloaded
  to `Papers\` under the naming convention (approved 2026-10-06), each
  record's `access` a local path plus its identifier or URL and its
  `evidence` the SHA-256; INTAKE_WORKFLOW.md section 18 written before the
  load. S16 by arXiv id, and S19 and L10 by DOIs found on Crossref (the plan
  expected S19 hand-origin); five hand-origin, OV19 and PH20 as
  `Reference:`. T07 read in full and promoted; it yields two
  `vendor-self-claim` assertions (about a thousand inference modules in
  2007; eight tactic types, unreconciled with the 2009 code's six) and
  settles Sprint 6's open note on `cyc-hl-module-count`. Guards proven by
  injection. `restore_store.py`'s closing message no longer names the
  retired export
- **feat**: F45, the Dirac-3 reading pass (Task G, Issue #75) -- seven
  sources read directly and promoted (the User Guide and the critique in
  full; arXiv:2407.04512, arXiv:2502.08591, arXiv:2608.10787, the protein
  paper's article page and QCi's EQC lesson in part), yielding 14
  assertions: F-201 to F-209, F-301 to F-303 and the planning note's QCi
  noise claims, every quote checked against its local copy. F-207 enters
  as `absence` with its search scope (545 QCi site files and four PDFs);
  the Zeno claim contradicts the peer-reviewed dissipation mechanism;
  disclosed coi stored on two records. Two second-hand errors corrected by
  the reading (section 15): F-301's "80 percent" is not in the critique,
  and F-302's 122% bundles a 24% formulation gap. Guards proven by
  injection
- **docs**: Phase 5 I4 re-read (2026-10-08) -- ADR-0004 A7 matched to the
  code in two sentences (CI deselects by marker; off Windows with no
  override, `store_dir()` refuses and names `EBDB_STORE_DIR`) (de4e487);
  Manual Validation package handed over
- **docs**: Manual Validation decisions (2026-10-08 and 2026-10-09) -- Q9
  keep priorities; Q13 no action on the 949 / 954 Dirac-3 level ceiling;
  F63 carded (two Dirac-3 admissions in arXiv:2407.04512); Q12 = 1 a
  12-month re-check, Q15 = 2 built in Sprint 8, Q16 = 1 F64 carded (the
  staggered 24-section schedule); ADR-0005 A6 revised and approved (Q19);
  ADR-0004 A7, ADR-0003 A2, ADR-0005 A5 approved; Phase 1.3 no longer
  refreshes the probes each cycle (b8f3bca, 89accb9)
- **docs**: Sprint 7 retrospective (2026-10-09 and 2026-10-10) -- team
  lead's feedback verbatim (all Very Good) with Claude's (f403121); F65
  carded (Dirac-3S, target Sprint 8); `SPRINT_7_SUMMARY.md`; master plan
  and checklist rolled (cf6f5e4)
- **process**: Sprint 7 retrospective I1-I7 (2026-10-10, Q21 = 1) --
  decision options state their cost; the plan absorbs its decisions at
  3.7; options lead with the outcome; dropped commitments disclosed in the
  next message; the amendment re-read covers restatements; one sprint
  status format ("Phase n.n Name") read by the footer, the Phase 4 Stop
  hook and the tests, with the stored `updated` field removed; task start
  times in the note. Guards proven by injection (0747a9b, 9cf69a6)
- **fix**: Copilot review on PR #68 (2026-10-10) -- the abstract-page probe
  note said "access not recorded" for a 404 or 410 that IS recorded; PEP 8
  spacing (a63cad9)

### 2026-09-27 to 2026-10-06 (Sprint 6, PR #54, merged to develop 2026-10-06 and to main via PR #67 the same day)

- **docs**: F58 carded and targeted for Sprint 7 (2026-10-06): the store,
  its backups and the export move out of the repository, ADR-0004 amendment
  first (840d255)
- **chore**: Sprint 6 merge-ready (2026-10-05): Copilot review complete
  with no findings; PR #54 marked ready (66f1b20)
- **docs**: Sprint 6 completion updates (2026-10-05): SPRINT_6_SUMMARY.md;
  master plan rolled and shipped cards pruned by hand; checklist Sprint 6
  section (be72649)
- **process**: Sprint 6 retrospective improvements I1-I6, all applied now
  (2026-10-05): one process-wide arXiv clock (I1, I6, 498f53c); intake
  refuses a manifest no INTAKE_WORKFLOW section names (I2, f58f5d2); task
  issue numbers resolved from the task letter, hook-checked (I3, 4ea7e6b);
  Phase 5 re-reads amendments against the code and bulk loads state their
  derived fields at planning (I4, I5, eeb2e46)
- **docs**: Sprint 6 retrospective recorded (2026-10-05, 9ae41db)
- **docs**: Sprint 6 Phase 1 (2026-09-27) -- carry-forward cut after PR #43
  (develop) and PR #53 (main); CHANGELOG reconciled; master plan swept by
  hand; Phase 1.3 design-document currency recorded (refresh over 347
  papers: SAME 247, NO-ID 98, POORER 1, DIFFERS 1)
- **docs**: F39 carded as the first permanent item (model evaluation), F40
  its Sprint 6 release (2026-09-29)
- **docs**: F41-F50 registered from the Cyc and CVQBoost handoff, with
  planning notes on F36 and F37 (2026-10-03)
- **docs**: Sprint 6 scope selected (12 items) and `SPRINT_6_PLAN.md`
  drafted with pre-flights and decisions Q1-Q11 (2026-10-03)
- **process**: F40, the first release of permanent item F39 (Task A, Issue
  #55) -- each model tier in `model_assignment_heuristics.json` now names its
  verified model, id, price, context, retirement date and the date checked,
  from Anthropic's models page (2026-10-03): Fable 5.1, Opus 5.5, Sonnet 5.5,
  Haiku 4.5. Haiku 4.5 retires not sooner than 2026-10-15; the Developers
  role then moves to Sonnet 5.5, and a new trigger flags any tier within 30
  days of retirement. The SPRINT_PLANNING.md role table no longer says
  "Fable 5"; three guards, each proven by injection
- **docs**: F43 (Task C, Issue #57) -- `INTAKE_WORKFLOW.md` section 15:
  assert the table, not the summary; both worked examples verified at
  source (CVQBoost's "3-8x" against table ratios of 1.7x to 83x; the
  hardware plan's "superlinear" beside its own `vars^0.75` fit)
- **docs**: F38 (Task B, Issue #56) -- `CHECKLIST-Phase2-pre.md` back-filled
  for Sprints 1 to 4: 45 rows checked with a verified commit or document, 5
  left unchecked with the reason (Sprint 1's adjudication timing and median,
  first measured in Sprint 4; Sprint 2's replaced measurement; "--no-verify
  never used", unprovable from history; reading-level escalation, not
  tracked anywhere)
- **docs**: F34, F36, F37, F47 (Task D, Issue #58) -- ADR-0004 A6
  (`derivation`, `claim_type` with `search_scope`, the synthesis cap and
  the retraction floor, both computed and exported as derived keys) and
  ADR-0005 A4 (`publication_status`, the ten reference fields with the
  probe rule, the `read_extent` gate at `read`, `read`'s cost restated per
  Q7, the admission-against-interest rule)
- **feat**: the migration (Task E, Issue #59) -- `store/schema.sql` gains
  `assertion_fields.derivation`, `claim_type`, `search_scope` (every
  assertion now has a row), `paper_fields.metadata_provider` and `coi`, and
  the tables `paper_found_via`, `paper_reads`, `paper_probes`,
  `source_links`; `scripts/migrate_sprint6_reference_fields.py` (dry run by
  default, verified backup, per-piece idempotent) applied to the live store:
  23 assertions back-filled (18 extracted, 3 synthesized, 2 project; 8
  vendor-self-claim). The door validates the new fields and `set_tier`
  refuses `read` without a `full` or `partial` read; the export emits them
  plus the computed `certainty_cap` and `certainty_cap_reason`
  (`learning-qml-no-reliable-tabular-accuracy-gain`: moderate, capped low);
  the rebuild restores every new key and never writes the derived ones
  back; `learnings.py` selects on `derivation`; the F47 test
- **fix**: Task E fresh-eyes review (Issue #59) -- the `read` gate also
  holds at insert (`intake --tier read` went around it) and binds the read
  to the reader named in `checked_against_source`; a synthesis inherits its
  inputs' retraction floor; a caller-set `metadata_provider` is refused
  unless the citation is the door's or a replay; the migration rolls back
  itself, with its own tests (schema parity, idempotency, dry run, rollback
  proven by injection); `checked_against_source = 'never'` no longer
  satisfies `read`
- **feat**: F36 back-fill, stored fields (Task F, Issue #60) --
  `scripts/backfill_reference_fields.py` routed all 347 papers
  (`found_via`), 121 with `cited_as` from the preserved bibliography, 249
  with `metadata_provider` (135 DataCite and 7 others named in the history,
  107 inferred from the access id and marked so), and `read_extent` for the
  12 papers at `read` from `checked_against_source`; `coi` (347) and
  `read_extent` below `read` (14) queued, not guessed
- **feat**: F41, the Cyc and Fourier Wall package without the CVQBoost
  findings (Task G, Issue #61) -- `manifests/sprint6_f41_cyc_sources.json`
  (10 Cyc and repository sources plus the hardware plan, pinned at hsbc
  `a6c3453`; 11 written, 0 refused) and
  `scripts/sprint6_task_g_cyc_and_facts.py` (35 assertions, the six CVQBoost
  ones filtered; three promotions to `read` with their read extents;
  decision 3's certainty changes; decision 4.1's `method` row found already
  present); `INTAKE_WORKFLOW.md` section 16, appended after the manifest ran
  (the order slip is stated in the section)
- **docs**: F42, the two Cyc research documents (Task H, Issue #62; commit 39b179e's subject says #63 in error) --
  `docs/research/2026-09-28_F42_*`; the dated amendment appended to
  `cyc-knowledge-representation.md`; its "Generalization" heading fixed and
  the `-isation` pair added to `scripts/us_english_fix.py`, which now
  catches it (proven: the guard went red on the old heading)
- **feat**: F36 computed fields (Task F part 2, Issue #60) -- `store/probes.py`
  (publication status from arXiv's comment, journal_ref and DOI or Crossref's
  type and `updates:` notices; version of record; affiliations; access as
  observed) and `scripts/probe_reference_fields.py` (pilot of 30 across
  source types, then all 361 papers, heartbeat file, per-record commits).
  Snapshot 2026-10-03: 139 published, 96 preprint, 0 withdrawn or retracted
  among existing records; access 286 open, 31 bot challenge or script shell, 12 refused, 6 not found; 3 arXiv ids left unanswered (DataCite cannot show
  a withdrawal); 8 read timeouts re-probed after a DataCite fallback was
  added for timeouts
- **feat**: F35 code (Task K, Issue #65) -- `store/citations.py` sends a
  GitHub token from `GITHUB_TOKEN` or `GH_TOKEN` on api.github.com requests
  only, never logged (ADR-0002), with tests proven by injection;
  `scripts/link_code_repositories.py` parses the 135 notes (129 GitHub, 6
  reported: 4 Zenodo or Gitee, 2 malformed) and runs after Task J
- **feat**: F32 NonArxiv rows (Task J, Issue #64) -- `scripts/qmlpapers_manifest.py`
  reconciles all 1,440 TSV rows (1,403 new, 15 already in the store, 19
  duplicates across folders, 3 hand path, 0 malformed); the three hand-path
  rows entered from their page 1 (`manifests/qmlpapers_nonarxiv.json`: Beer
  et al. by its printed DOI, Aaronson and Zhang-Ni hand-transcribed)
- **fix**: Q11 (Task L, Issue #66) -- `du-2024` citation refreshed to its Scientific
  Reports publication (`refresh_citations.py --apply`, verified backup)
- **feat**: F32 bulk load, first part (Task J, Issue #64) -- 717 of 1,403
  QMLPapers entries in at `seen`, each with its `found_via` and `cited_as`.
  Stopped at entry 765: arXiv's API answered read timeouts, then HTTP 429 to
  every request, after about 1,130 lookups in 3.5 hours at 3 s spacing
  (arxiv.org itself and status.arxiv.org were up). Refused so far: 2 for the
  entry itself (`2108.0131` malformed in the TSV; `2403.07059` HTTP 404), the
  rest timeouts, retried in the second part
- **fix**: arXiv pacing (team lead, 2026-10-04: "increase the request rate at
  every 6 seconds ... If a request failes on arxiv, then try via DataCite";
  Q2 = 2) -- `ARXIV_MIN_INTERVAL_S` 6.0; arXiv gets one attempt and any
  arXiv failure (any HTTP code, timeout, bad feed) goes to DataCite, in the
  door and in the probes; tests proven by injection. `intake.py` writes its
  output as UTF-8 (an author name outside cp1252 stopped the sample dry run)
- **feat**: F32 bulk load complete (Task J, Issue #64) -- 1,402 of 1,403
  entries in at `seen` (1,810 papers in the store as of 2026-10-04);
  `2403.07059`'s earlier 404 was transient; 1 refused for the entry itself
  (`2108.0131`, malformed in `QMLPapers/2021/manifest.tsv`); 34 second
  `found_via` rows on papers already present
- **fix**: arXiv requests were NEVER paced between intake entries (Task J,
  2026-10-04) -- `intake.py` built a new `PacedFetcher` per entry, and a new
  pacer never waits. Present since Sprint 4 (64d067f). The resumed load sent
  684 requests in 10 minutes against the team lead's 6 s instruction, and
  the 429s of 2026-10-03 most likely had the same cause. One pacer per run
  now (`_fetcher()`), in intake and in Task I's script; test proven by
  injection. arXiv refused again after the burst, so Task I waits 2 hours
- **feat**: F35 complete (Task K, Issue #65) -- 105 of the 135 repository
  notes linked (`code-of`, with the paper's sentence); 30 reported: 23
  repositories return HTTP 404 (most are URLs truncated by the note
  extractor), 6 notes are not GitHub links or are malformed, 1 paper is the
  malformed `2108.0131`. Two door fixes found on the way: GitHub answers a
  repository's canonical name, so two notes can share a record; and
  `parse_access` read `github.com/<owner>/arXiv-2502.18361-...` as an arXiv
  id (test proven by injection)
- **feat**: F33, withdrawn and retracted (Task I, Issue #63) -- after the
  2-hour arXiv pause, 6 s spacing: six withdrawn arXiv preprints at `seen`
  with `publication_status` withdrawn from arXiv's own signature (`/pdf`
  HTTP 404, measured 2026-10-04; four of the six comments give only the
  reason, never the word "withdrawn"), each comment quoted as the reason;
  Valdez and Melin retracted, from Crossref notice
  `10.1007/s00500-026-11351-6`; `superseded-by` links to `2405.13351` and
  `2210.14450`. The Lin duplicate and its replacement derive the same id, so
  the withdrawn copy carries its arXiv number. A probe can no longer
  downgrade a recorded withdrawal or retraction (test proven by injection)
- **fix**: Phase 5 fresh-eyes review of the Sprint 6 store changes, all
  findings taken -- every request that lands on arXiv (the API, the site,
  an arXiv DOI at doi.org) now shares the 6 s pacer, including the access
  probe's GET and Task I's `/pdf` HEAD, which had gone out unpaced; every
  arXiv failure (an HTML or truncated body, a connection reset) reaches
  DataCite (`ARXIV_FAILURES`); a 429, a 5xx or no connection is "no answer",
  never an access status (none had been stored); Task I's links are
  idempotent on re-run; `parse_access` counts an arXiv id beside a
  repository in either order. Guards proven by injection
- **feat**: Manual Validation follow-up (team lead, 2026-10-05: "look at the
  hsbc repo ... Find and add as evidence") -- the hsbc Phase 1 results memo
  as a source (pinned at 203881e, read directly) and two `platform:dirac-3`
  assertions: Dirac-3 matched the exact classical optimum on the Phase 1
  CVQBoost formulation (-0.0010 AUPRC, CI containing zero), and that
  formulation is near-trivial (strictly convex, nearly degenerate), so it
  does not test hard problems. Neither source sentence mentions error
  correction
- **docs**: Manual Validation decisions Q1, Q2, Q3, Q4, Q5 = 1 (both
  amendments accepted; inputs only in `assertion_relations`; the 14
  `claim_type` classifications kept; the cap stays computed); cards F52 to F57 (bulk probes with an
  arXiv cap, probes each cycle, the 30 unlinked notes, `cites` links, the
  corroboration question, the permanent read-for-claims program) and a Q9
  note on F45
- **fix**: the F47 test ignored case and flagged "NOT upgraded for admission
  against interest" on the record F47 names as not qualifying; now
  case-sensitive and never after NOT, with that sentence in its test

### 2026-09-23 to 2026-09-25 (Sprint 5, PR #43, merged to develop 2026-09-27 and to main via PR #53 the same day)

Reconciled 2026-09-27 at Sprint 6 Phase 1.1 against `git log`: commits on
2026-09-23, -24 and -25, none on 2026-09-26, the two merges on 2026-09-27.
Every commit below was entered in the same commit as its change; the
entries were checked against the log, not rewritten. Full detail:
`docs/sprints/SPRINT_5_SUMMARY.md`.

- **fix**: PR #43 Copilot review (2026-09-25) -- one finding verified false
  (the `visible_words` pattern is lazy; a two-script test now pins it, proven
  by injecting the greedy form), one fixed (`sprint_status.json` date)

- **docs**: Sprint 5 scope (F31, F30, F28, F5), F19 and F29 closed without
  implementation, F32-F35 carded for Sprint 6, plan approved with decisions
  Q1-Q6 (PR #43)
- **feat**: store durability (Task A, F30, Issue #44) --
  `scripts/rebuild_store_from_export.py` rebuilds the store from the
  committed export through the real door and proves the regenerated export
  byte-identical (it is, first run); `store/backup.py` takes a SQLite-API
  backup before every live `--apply`, verified at creation, with three-rule
  retention (32 days; newest of the last 5 sprints; never before its content
  is committed); `scripts/restore_store.py` restores and verifies;
  `validate_paper(check_local_paths=False)` is the one explicit exception the
  rebuild needs to run on CI; 14 tests, each guard carrying its own injection
- **feat**: HSBC Phase 2 bibliography downloaded (Task B, F31 part 1, Issue
  #45) -- `scripts/sprint5_bibliography.py`: 120 entries, 64 arXiv PDFs plus
  web, vendor and challenge copies saved under the existing material folders
  (Q1 = 2), 9 found already on disk and 3 already in the store, none fetched
  twice; `BIBLIOGRAPHY.md` preserved under `References/`; 14 items on a
  manual-download list with reasons. A saved page with fewer than 50 visible
  words is treated as a failure, after four publisher bot-challenge pages, a
  JavaScript-only page and a redirect stub were first saved as "copies"
- **docs**: QCi-affiliated people identified from the papers themselves
  (Task E, F5 sub-part 1, Issue #48) --
  `docs/research/2026-09-24_F5_qci_affiliated_people.md`: 18 people, each
  verified on a named page; none of the SMU/Loke authors is QCi-affiliated;
  Task F's disambiguation rule written before any search hit was read
- **feat**: HSBC Phase 2 bibliography processed into the store (Task C, F31
  part 2, Issue #46) -- `scripts/sprint5_bibliography_manifest.py` generated
  121 entries under context rules written first (`INTAKE_WORKFLOW.md`
  section 11); `intake.py` wrote 121, refused 0 (73 arXiv, 16 DOI, 10
  repositories, 22 hand-origin); `--verify` 7/7 on a sample of every source
  type. DOIs used only when written, derived-and-confirmed, or found by
  exact title plus year, first author and venue (an exact-title match first
  picked a 2015 conference abstract for a 2014 Nature paper). `intake.py`
  now records when DataCite, not arXiv, supplied the metadata (68 records).
  `test_every_paper_has_real_applicability` aligned to ADR-0005 A2: the
  obligation is `screened`'s, not `seen`'s, with an injection test
- **docs**: F36 carded (Task D, F31 part 3, Issue #47) -- the nine per-entry
  elements of the bibliography a paper record cannot hold, each classed as
  computed (a resolver) or stored, a dry-run back-fill for existing papers,
  and "decide together with F34"; reading notes deliberately NOT a field
- **feat**: QCi's own documentation and package pulled (Task G, F5 sub-parts
  3-4, Issue #50) -- `scripts/sprint5_qci_site.py`: of the sitemap's 2,755
  URLs, 1,660 older package versions and 170 duplicate mounts skipped per
  Q3 = 1; 544 pages saved under `References/QCi-site/`, 1 reused from Task
  B, 25 dead sitemap links (HTTP 404) listed; `eqc-models` 0.21.0 sdist and
  wheel saved, sha256-verified against PyPI. The plan estimated about 300
  pages; the latest package docs alone are 462
- **feat**: learning from the papers, designed and piloted (Task I, F28,
  Issue #52) -- `docs/LEARNING_SYNTHESIS.md`: a key learning is an
  assertion with "synthesis of" provenance, its evidence wired by
  `supports`/`contradicts`, its certainty derived by named reasons;
  `scripts/learnings.py` computes the evidence table, storing nothing.
  Pilot: six papers to `read`, seven assertions, three learnings (QML on
  tabular data MODERATE; resampling for strong trees LOW; metric and power
  checks MODERATE). Existing primitives sufficed; three gaps proposed, not
  applied. Two defects found and fixed on the way: the query double-counted
  an assertion with two sources, and the promotion skipped `screened`'s
  applicability (caught by the aligned guard)
- **feat**: every paper the 18 QCi people co-authored, where a written rule
  can tell (Task F, F5 sub-part 2, Issue #49) -- `scripts/sprint5_qci_authors.py`:
  seed (another of the 18 co-authors) then a two-shared-co-author network,
  written before the search; strict name matching for common families
  (`tests/test_qci_author_matching.py`, proven by injection); 191
  acceptances, 121 new papers, 39 arXiv PDFs to `QCiAuthorsPapers/`. The
  rule leaves most of Miri's, Chancellor's and Sam Wu's earlier papers
  unresolved: reported per person, not downloaded, for a team-lead decision
- **fix**: four defects in the Task A durability code, found by the Phase 5
  fresh-eyes review -- `restore_store.py` could not restore a corrupt live
  store (it now moves the unverifiable file aside and restores into a fresh
  one) and could prune the very backup it was restoring (now protected);
  retention rule 3 kept any backup of an intermediate state forever (now
  also met when an export commit landed after the backup); `learnings.py`
  created an empty store when none existed. The write-script coverage guard
  now asks whether a script writes, not whether its text mentions --apply.
  Each fix has a test built on the failing case
- **feat**: the QCi authors' papers into the store (Task H part 2, F5,
  Issue #51) -- 121 accepted papers through the door under
  `INTAKE_WORKFLOW.md` section 12's category rule: 108 written, 13 skipped
  as other versions (preprint, journal, conference) of works written
  earlier in the same run, 0 refused; `--verify` 7/7 on samples. `[QC-8]`
  (Emami et al., Scientific Reports 2026), unobtainable from the
  bibliography alone, arrived through the author search. Store: 329 papers
- **fix**: Manual Validation feedback -- `learnings.py` quotes each sentence
  once and cuts only at a word; `view.py contexts` no longer lists a
  primary-context paper again "via applicability" (pre-existing since Sprint
  2); the six pilot papers' stale "not yet screened" removed, and
  `set_tier()` now removes it at every promotion (Q7); the Table 3 rows
  under `cvqboost-vs-xgboost-auc-under-balancing` added (Q6); F37 carded (Q4)
- **feat**: Q1 revised by the team lead -- the author-search hits the
  co-authorship rule left unresolved were screened on their abstracts for
  QML, ML or the Zeno effect (`scripts/sprint5_qci_topic_screen.py`, rule
  written first): 392 unresolved, 25 matched, 4 rejected on reading, 21
  entered at `seen` with "authorship not confirmed" in the disposition;
  15 PDFs downloaded. Store: 350 papers. Q8: the three weakest on
  authorship removed at the team lead's decision; 347 papers
- **process**: Sprint 5 retrospective improvements 1-8, all applied now
  (team lead: "do all now"), each extending an existing control --
  `set_tier()` refuses `screened`/`read` without applicability (1); the
  unraw-escape hook also blocks Python rewriting a `.py` file from a shell
  command (2); the guard-discipline test fails on `or True` / `assert True`
  (3); the door refuses a hand-origin record whose saved `.html` copy has
  fewer than 50 visible words (4); fresh-eyes review at the structural
  task's commit (5); computed numbers and reported caps (6); estimation
  calibration and the Sprint 5 model-assignment log rows (7); F36 gains the
  metadata provider as its tenth field (8). Every mechanical one proven by
  injection

### 2026-09-19 to 2026-09-23 (Sprint 4, PR #30, merged to develop and main 2026-09-23)

Sprint 4 fixed the path, fixed the records, and prepared the cost
measurement: Tasks A-K per `docs/sprints/SPRINT_4_PLAN.md`, run across a
local session (B, C, E, F, G, H) and a managed remote session (D, I, J, K)
on the same branch. Full detail in the PR #30 commit history and, once
written, `docs/sprints/SPRINT_4_SUMMARY.md`. This entry summarizes.

- **process**: the delivery cycle re-homed -- Backlog Refinement is Sprint N
  Phase 1 on the N branch, `sprint_status.json` advances at the carry-forward
  cut, the Stop hook and the plan-doc guard agree by construction (Task A,
  F27)
- **feat**: the ingestion door (Task B, F25 D2) -- `store/citations.py`
  derives citations and titles from arXiv, Crossref, DataCite and (Task G)
  GitHub; `validate_paper()` refuses hand-typed citations for resolvable
  ids, audit text in citations, tier words in dispositions, unanchored
  rationales; `paper_fields.citation` dropped and the read-tier CHECK added
  in one migration; `value` is the title
- **fix**: every F10 citation and access defect corrected by re-derivation,
  not retyping (Task C, F25 D3): 22 api-origin citations refreshed, 24
  hand-origin records given real paths and the visible marker, `rand-2023`
  renamed `rand-2022`, `udaru` to hand-origin (printed DOI unregistered),
  `rand` and `freericks` to api-origin (registered DOIs found); the seed
  generator retired; arXiv measured to refuse this client's `id_list`
  batches, so one id per request with DataCite as fallback
- **docs**: ADR-0005 A2 (`screened` as practiced, the citation rule
  enforced, three field changes, the rand rename), A3 (repository access
  kind, non-paper kinds by disposition prefix, derived ids, A2's pending
  items closed) and ADR-0004 A5 (the four context tests); every count a
  dated snapshot
- **feat**: `store/export.py` batches child queries, byte-identical export
  (Task D, F26; 275 statements to 22 at 54 records)
- **feat**: the F11 adjudication packet, generated from the store with each
  record's source link and F10 finding (Task E); the timing run is the team
  lead's; #35 stays open until the number is recorded
- **feat**: the intake workflow (Task G, F25 D5; F12 absorbed) --
  `docs/INTAKE_WORKFLOW.md` and `scripts/intake.py`, one door for papers,
  repositories, references and books, manifest mode for the bulk set that
  arrived during the sprint (1,618 files under `QMLPapers/`), `--verify` as
  the first-try check; all three F12 examples in the store (one thread:
  the LinkedIn post, the MerLin paper, the MerLin repository), 7/7 each
- **fix**: all 48 papers re-filed against pre-registered context tests
  (Task F, F25 D4): `method` 8 to 16 rows, `ml` 0 to 15, `world` moved off
  `arute` and `rand` onto `zajac` and `kerger`; every rationale anchored;
  nine dispositions rewritten; pinned tests moved with reasons
- **feat**: five papers to `read` after direct reads, five assertions with
  GRADE-style reasons, `fourier-wall` contradicts the two CVQBoost accuracy
  claims, `zajac` supports `fourier-wall`; Neven 2012 lineage confirmed
  (Task H, F25 D6)
- **process**: the hook family F15-F17 (Task I), `BACKLOG_REFINEMENT.md` as
  a skill (Task J, F20), `.claude/model_assignment_heuristics.json` with
  protocol as a first-class field (Task K, F18)
- **chore**: `pere-qml-github-repo-empty` removed at the team lead's
  direction (its 0-byte seed file is gone and the related papers sit under
  `QMLPapers/`); Manual Validation scope recorded in the workflow: only
  end-user functionality and team-lead decisions reach it, and an ADR
  amendment is reviewed as name, what changed and why, quoted language
- **test**: the CHANGELOG currency guard now reads the range-dated section
  headers this file uses; it had read 2026-09-14 as the newest entry for
  three sprints and passed on its own defect until the calendar moved
- **process**: F11 measured 2026-09-21 -- the team lead adjudicated the 18
  corrected records in 19.4 minutes, 1.08 per record, 18/18 accept. Recorded
  with its caveat: this is CONFIRM mode over model-corrected records with
  F10's findings in view, not the cold adjudication F10's 599 s compares
  against. F29 cards the cold measurement
- **fix**: PR #30 review round 1 (Copilot plus three Claude reviewers)
  found five defects, one merge-blocking and already shipped: an inverted
  ternary had destroyed `updated_reason` on 44 of 48 paper records, 43 of
  them losing the Sprint 1 seed-load note. Recovered from git by
  `scripts/recover_updated_reason_history.py`. Also: an api-origin record
  could carry any fabricated citation with no network call; an empty
  provider title was skipped while the run reported success; `apply()`
  wrote to `records` without passing the door; a DOI-shaped folder in a
  local path was read as a DOI; and Copilot alone caught GitHub-backed
  records being routed to `fetch_doi` and reported as broken DOIs
- **fix**: PR #30 review round 2, run against round 1's own fixes, found
  that three of those guards did not guard. The append-only test scanned
  SOURCE TEXT, so three rewrites destroyed history with the full suite
  green; the citation marker was a string a caller could type, refusing an
  omission but not a fabrication; and the new commit hook drifted its
  offsets, blocking at 19 preceding lines and ALLOWING at 20. Fixed
  structurally: one `append_updated_reason` implementation that all four
  sites call and the tests EXECUTE, a sentinel object compared by identity,
  and exact offsets. Copilot also found CI red on every fresh checkout (a
  test failed rather than skipped when the gitignored store was absent) and
  one hook registered without a timeout
- **chore**: F30 carded for Sprint 5 after the team lead asked about
  database backups -- the premise check found there were none, and the
  deeper gap is that no script rebuilds the store from the committed
  export, the recovery path ADR-0004's design implies

### 2026-09-18 to 2026-09-19 (Sprint 3, PR #20)

Sprint 3 corrected the foundations, then measured adjudication: Tasks A-H
per `docs/sprints/SPRINT_3_PLAN.md`. Full detail:
`docs/sprints/SPRINT_3_SUMMARY.md` (with the first recorded Actuals),
`docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md`,
`docs/sprints/SPRINT_3_RETROSPECTIVE.md`, and the PR #20 commit history.
This entry summarizes rather than restates those numbers.

- **process**: spamfilter-multi surveyed read-only across ten named areas
  (Task A, F2 Phase 1); six genuinely new process assets carded as
  F15-F20; everything else was already here in adapted form
- **fix**: five PR #1 code-review findings closed (Task B, F6) --
  `validate_paper()`, `store.script_paths()`, `_copy_nonnull()`/
  `_child_list()`, citation read from provenance at export; Finding 4
  (N+1 queries) stays deferred as premature
- **test**: US English guard over living process docs (Task C, F13), with
  every ADR and everything under `docs/sprints/` excluded as frozen
  records after the fixer's first run rewrote them and was caught before
  commit; nineteen real corrections applied
- **fix**: `apply_paper_applicability.py` fails loudly on a typo'd paper
  id or a mismatched applicability set (Task D, F14)
- **process**: four INDEPENDENT model-tier adjudication reviews of the same
  18 screened papers, zero cross-visibility (Tasks E-H, F7-F10): Haiku and
  Sonnet 18/18 confirm; Opus 7 cross-record inconsistencies; Fable-tier
  Opus 4 source-verified citation defects plus an unearned `screened` tier
  and the value/provenance/citation triplication at the store-write layer.
  Findings consolidated with F12 into F25 at the team lead's direction
- **process**: Sprint 3 retrospective (team lead all "Very Good";
  Development Team five "Good", one theme: its own first attempts needed
  the guards). Four improvements applied: write-shaped scripts dry-run by
  default, `## Actuals` in every summary, delegated reports verified
  against repo state, review-protocol depth recorded on F11/F18
- **fix**: PR #20 review (Copilot 5, Claude code-reviewer 4, silent-
  failure-hunter 11) -- the Task B savepoint design had committed per
  entry under Python's legacy sqlite3 mode and the Task D script wrote
  before deciding; both now all-or-nothing ("decide, then write" added to
  QUALITY_STANDARDS.md); `set_tier()` closes the validator bypass; blank
  `checked_against_source` rejected; the US English test imports the
  script's own exclusion lists instead of restating them
- **chore**: end-of-turn status line and the memory rule that its time
  comes from a shell call, never an estimate (team lead, 2026-09-19)

### 2026-09-17 to 2026-09-18 (Sprint 2, PR #11)

Sprint 2 validated the store against both ground truths, guarded its
shared vocabulary, and made it viewable from the CLI: Tasks A-E, G per
`docs/sprints/SPRINT_2_PLAN.md` (Task F replaced mid-sprint, see below).
Full detail: `docs/sprints/SPRINT_2_SUMMARY.md`,
`docs/sprints/SPRINT_2_RETROSPECTIVE.md`, and the PR #11 commit history.
This entry summarizes rather than restates those numbers.

- **fix**: re-derived every seed-set paper's real applicability from its
  actual PDF content (Task A), correcting a Sprint 1 undercount where
  most papers carried only their single primary context despite
  ADR-0005 defining applicability as a separate plural field
- **feat**: extracted and validated the first real HSBC-submission
  assertions (Task B) -- the B1 variable-count case from the consumer
  repository's own preregistration amendments, with a `contradicts`
  relation between the corrected and the documented-wrong value
- **fix**: spot-checked store content against the 44 source PDFs
  directly (Task C); resolved seed-directory drift (a book relocated to
  the non-repo Books directory, the QBoost paper added, both confirmed
  intentional) and added the QBoost paper with a real citation
- **test**: guard for ADR-0004/ADR-0005 vocabulary agreement (Task D,
  F76), verified by injection
- **docs**: both ADRs' 20-paper checkpoints walked against the real
  store and recorded as dated amendments (Task E, F75; ADR-0004
  Amendment A4, ADR-0005 Amendment A1), later corrected for two
  internally-inconsistent counts found by code review and given
  explicit point-in-time qualifiers so a snapshot count is not read as
  a durable fact in a document that does not permit edits in place
- **feat**: `scripts/view.py` (Task G, F3) -- contexts / paper /
  assertion modes, plain text or `--json`, no server. Found and fixed a
  Windows console encoding defect (cp1252 crash on non-ASCII `--json`
  output) during build, verified by injection
- **process**: Task F (team-lead adjudication timing) REPLACED by F7-F11
  (Class 3 scope change) -- four model-tier adversarial review cards
  (Haiku, Sonnet, Opus, Fable) plus F11, the original measurement,
  sequenced to run after F7-F10 against the same record set
- **chore**: hook enforcing the AskUserQuestion ban
  (`.claude/hooks/block_ask_user_question.py`), added after the rule
  was violated twice in one session despite being fully documented
  beforehand; a mechanical `gh issue list` check added to Phase 5
  after two issues stayed open despite `Closes #N` commit messages on
  a feature branch; a data-precondition check added to
  `SPRINT_PLANNING.md`'s estimation guidance
- **process**: Sprint 2 retrospective run (16 categories x 4 roles, all
  "Very Good"); F7-F14 added to the backlog for future sprint selection

### 2026-09-15 to 2026-09-17 (Sprint 1, PR #1)

Sprint 1 built the store end to end: Tasks A-H per
`docs/sprints/SPRINT_1_PLAN.md`, plus the sibling-repo write guard and F2-F6
backlog items surfaced at Manual Validation and PR review. Full detail:
`docs/sprints/SPRINT_1_SUMMARY.md` (created during Sprint 2 planning, per
the three-doc rule), `docs/sprints/SPRINT_1_RETROSPECTIVE.md`, and the PR
#1 commit history. This entry summarizes rather than restates those
numbers, per this project's own "a number must be traceable to a committed
generator" standard -- run the suite, don't copy a count.

- **chore**: the five inherited PowerShell hooks converted to Python
  (Task A pre-kickoff), removing the doubled-backslash JSON-escape hazard
  by construction rather than by continued vigilance
- **feat**: SQLite schema for the four record classes (Task B), a
  deterministic JSON export as the committed artifact (Task C), and
  domain-scale contexts seeded per ADR-0004 section 3b (Task D)
- **feat**: one paper (Lenat/Marcus) ingested end to end (Task E); the
  44-paper seed set loaded at `seen`, 17 promoted to `screened` for variety
  (Task F); a determinate-fact resolver for the consumer repository's
  amendment count, computed live rather than stored (Task G)
- **docs**: removed hsbc-quantum-fraud-2026 process content (Dirac-3
  hardware rules, `experiments/src`, `results.json`, a submission calendar)
  presented as this repository's own live rules across 11 files (Task H,
  F1), with a regression test verified by injection
- **chore**: added a hook blocking writes into `spamfilter-multi` or
  `hsbc-quantum-fraud-2026` from this repository's sessions (read access
  stays unrestricted)
- **fix**: PR #1 review (Copilot + Claude) found `assertion_documents` FK
  coupling that blocked citing a document on an assertion with no
  units/rounding, a silently-dropped `citation_context` field, and a
  `--promote` ordering bug that no-opped promotion on an already-seeded
  store. All three fixed with regression tests before merge
- **process**: Sprint 1 retrospective run (16 categories x 4 roles, all
  "Very Good"); F2 (spamfilter-multi deep-dive), F3 (CLI DB viewer), F4
  (accuracy validation against the HSBC submission and the source papers),
  F5 (QCi author/documentation deep-dive), and F6 (remaining PR review
  findings) added to the backlog for Sprint 2 selection

### 2026-09-14

- **chore**: Repository seeded from `hsbc-quantum-fraud-2026`. Carried: the
  sprint methodology (execution workflow, process, planning, checklist,
  retrospective, stopping criteria, backlog refinement), quality and testing
  standards, five hooks, three practice ADRs renumbered 0001-0003, and five
  process guards. NOT carried: anything about the fraud submission, the ML/QML
  runs, or Dirac-3 hardware
- **docs**: ADR-0014 and ADR-0015 MOVED here as 0004 and 0005. They are this
  repository's design rather than the consumer's; the originals remain there as
  the record of when the decisions were made
- **chore**: Three hooks deliberately NOT carried --
  `block-unapproved-submission-edit`, `block-reactive-amendment` and
  `block-frozen-history-rewrite`. Each guards a frozen artifact of the fraud
  submission that does not exist here, and a hook guarding a missing file is a
  hook that cannot fire
- **test**: `.claude/settings.json` written STRUCTURALLY via json.dump rather
  than by hand, and every registered path verified to resolve at write time. Two
  hooks in the consumer repository were dead for their entire life because a
  single backslash before `block-` is a JSON escape
- **chore**: corrected a seeding mistake -- the first attempt put the git
  repository inside `D:\Data\Harold\EvidenceBasedDB\` (the non-repo staging
  directory), conflating the two. Reseeded to the correct
  `D:\Data\Harold\github\EvidenceBasedDB\` and removed the misplaced copy,
  verified to hold no uncommitted changes or unpushed commits first.
  `README.md` and `CLAUDE.md` now record the two-directory layout as a table
