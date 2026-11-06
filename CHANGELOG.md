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

### 2026-11-05 onward (Sprint 16, in progress)

- **chore**: Sprint 16 opened (2026-11-05). The team lead merged PR #149
  into develop (7dca2c9) and PR #163 to main (dff5c49); `sprint-15`
  tagged on dff5c49; branch `feature/20261105_Sprint_16` cut from the
  Sprint 15 branch (6.6 carry-forward). Phase 1.1 reconciliation: every
  commit since 2026-10-31 changed this file; 2026-11-02 and 2026-11-03
  have no commits (the reads ran in the store and in uncommitted work
  files, committed on 2026-11-04)
- **docs**: Sprint 16 Phase 1.2 and 1.3 (2026-11-05). Sprint 15's
  issues #150 to #162 all closed; its triad present with Actuals; master
  plan rolled (Sprint 15 merged and tagged). Shipped cards F115, F116,
  F124 to F130 and the released copies F131 to F133 pruned by hand.
  Snapshots: F114 (892 of 1,430 records not read in full, 190 groups),
  F57 (522 papers with no read row; arXiv 2108.13346 not in the store),
  F95 (386 PDFs, no unnamed file saved since 2026-11-01), F98 (the list
  moved to 399b022651 with 6 new papers), F51 and F90 hold checks.
  Phase 1.3: 0 re-checks due; no ADR or schema change in Sprint 15
- **docs**: Backlog refinement 2026-11-05: Sprint 16 scope selected (team
  lead): F136, F134, F135, F137, F114, F57 and the new F139. F95 and F98
  folded into F114 (30 papers per sprint by default, 20 this sprint);
  their cards removed. Books leave F114 for the new F138, on HOLD.
  F139 carded by the Coding Agent Team (read once, check once, write
  once, with telemetry per paper). F137's premise corrected: the two
  Dunjko records are one paper (preprint and journal version). Sprint 16
  plan drafted (`docs/sprints/SPRINT_16_PLAN.md`), with 7 questions;
  draft PR #164 opened
- **docs**: Sprint 16 plan questions answered (team lead, 2026-11-05):
  Q1 = 1 (the 6 new list papers first), Q2 = 2 (the two named papers
  inside F114's 20; from Sprint 17, named and new list papers are part
  of F114's 30), Q3 = 1 (arXiv v1), Q4 = 1 (F51 released from HOLD into
  Sprint 16), Q5 = 2 (the reviewer keeps the full second read). The plan
  absorbs them; Q6 and Q7 are still open
- **docs**: Sprint 16 plan approved (team lead, 2026-11-06): Q6 = 1 (one
  Dunjko record: dunjko-2018 keeps the paper and adds the arXiv id; the
  2017 record's assertions move to it), Q7 = 1 (monographs are books:
  Simeone 2022 and Cichocki 2016 move from F114 to F138). Issues #165
  (Task A) to #172 (Task H) created; PR #164 body updated, still draft
- **feat**: Sprint 16 Task A (F136, #165): each PDF's text extracted
  once, each quote checked once. `store.text_cache_dir()` gives one
  cache every store copy reads (it no longer follows `EBDB_STORE_DIR`);
  the OCR engine folder is fixed too. `full_read_apply.py` checks only
  new or changed quotes (`store.ingest.checked_when_stored`) and prints
  its counts. On a store copy a re-apply now checks 0 quotes in about 15
  seconds (30,113 quotes, 740 sources, 554 seconds without it). INTAKE
  section 68 states the rule: every write is checked; an unchanged row
  is not. Three tests, each proven red. Also (Task F): the hand-download
  list and its skill name F114 instead of F95

### 2026-10-31 to 2026-11-05 (Sprint 15, PR #149, merged to develop 2026-11-05 and to main via PR #163 the same day; tagged sprint-15)

- **chore**: Sprint 15 opened (2026-10-31). The team lead merged PR #140
  into develop (9059061) and PR #148 to main (934a416); `sprint-14`
  tagged on 934a416; branch `feature/20261031_Sprint_15` cut from the
  Sprint 14 branch (6.6 carry-forward). Phase 1.1 reconciliation: every
  commit since 2026-10-29 changed this file; no day lacks its entry
- **docs**: Backlog refinement 2026-11-01 (Sprint 15 Phase 1.2 to 1.4):
  Sprint 14's issues #145 to #147 closed by hand (PR #140 named them
  without `Closes`); shipped cards pruned by hand (F117, F118, F119,
  F120, and the released copies F122 and F123); F114 stays with a
  snapshot (1,091 of its 1,430 records not yet read in full, in 227
  groups); snapshots refreshed on F57, F95 (no new file from the team
  lead), F98 (list unchanged at ea6f42a7c0), F51 (hold unchanged) and
  F130 (Phase 2's Sprint 30 PR #74 not merged). Phase 1.3: 0 re-checks
  due; no ADR or schema change in Sprint 14. Slate presented
- **docs**: Sprint 15 scope selected (team lead, 2026-11-01): F114 at 100
  papers, F125, F126, F127, F128, F115, F95, F98, F124, F129, F116, F57
  and F130; released copies F131 (F95), F132 (F98) and F133 (F57);
  priorities renumbered as the slate proposed; F39 not selected. Plan
  drafted (`docs/sprints/SPRINT_15_PLAN.md`): F115 and F116 run before
  F114's reads, so the 100 papers are read with figures and image pages;
  pre-flight: Windows' built-in OCR read udaru's page 1 (no Tesseract
  installed)
- **docs**: Sprint 15 plan approved (team lead, 2026-11-01): Q1 = 1, Q2 =
  2 (F133 reads 100 records), Q3 = 3 with the team lead's qualification
  (OCR of a stored PDF's page grades as text-layer text; OCR of an image
  file outside a PDF is HIGH only when corroborated, otherwise MEDIUM at
  most), Q4 = 1. F115's engine changed to RapidOCR (cross-platform, in its
  own virtual environment), at the team lead's request. Issues #150 to
  #162 (Tasks A to M)
- **docs**: Sprint 15 Tasks A and B (F131, F132): `Papers\` holds 378
  PDFs, none new since 2026-10-30; Roadmap-to-QML is still at
  ea6f42a7c0. No store write
- **feat**: Sprint 15 Task C (F125): a record a reviewed group left unread
  is read later in a re-entry group `<g>-r<n>` with its own group file and
  review file. The applier takes exactly the records the predecessor's
  review left unread; the builder builds the group from its local brief;
  the review finalizes it without a ledger entry. The status script reads
  `work\f114\local\`, counts a read only for the group it names, and
  calls a group with only its unread records left "applied". Each with a
  test proven red
- **fix**: the fresh-eyes review of 34034bd (Task C). A re-entry brief may
  leave a record unread again (its own `unread`, with why), so a group
  whose predecessor left a no-text record is buildable, and its review
  names it; the builder checks each re-entry brief against its
  predecessor's review before anything is built; a test ties the status
  script's group pattern to the applier's read detail. Each proven red
- **fix**: Sprint 15 Task D (F126): the page fixer leaves "p.12-15.3" and
  "p.12a" as written and drops a "to" range's "of 10" with it; the applier
  writes an ANCHOR_FIX on a confirmed stored assertion (it was dropped
  without a word), rebuilt from the stored row with every quote checked
  again, dated by the review's `anchor_fix_on`. Store: one assertion,
  muta-hardware-scope-photonic-gkp, now cites Section V, p.8 (INTAKE
  section 60; backup `evidence-20261101T155312102348-...db`). Each with a
  test proven red
- **fix**: Sprint 15 Task E (F127): `f114_cloud.fetch` refuses a merged
  result branch for every record and a record with no launch base (it
  saved one and raised KeyError on the other); the applier's clash check
  reads a record id as a whole token, not a substring; its refusal guard
  ignores a refusal a later note reversed ("... refusal ... no longer
  applies", 9 QCI Dirac papers); the builder counts id_fix targets as
  taken, raises when the store file is missing, and no longer matches
  "v-2" inside "v-2.5". Each with a test proven red. No store write
- **fix**: the fresh-eyes review of Tasks D and E (before their commit):
  "of N" is dropped only after a "to" range ("of 2019 survey" was lost);
  "p.12 to 15.3" is left as written, as "p.12-15.3" is; "p.4ff" is kept
  (a test records it); a reversal note that quotes the refusal's words no
  longer counts as a refusal; the clash check ignores case, as LIKE did;
  an anchor move refuses quotes with more than one anchor or no stored
  context. Each proven red
- **feat**: Sprint 15 Task F (F115): text from page images. A PDF page
  whose text layer holds fewer than 40 visible characters is rendered by
  `pdftoppm` and read by RapidOCR 3.10.0 on ONNX Runtime 1.31.1, in its
  own virtual environment outside git (`requirements-ocr.txt`,
  `scripts/ocr_worker.py`, `store/ocr.py`); an image file given as a
  source is read the same way. The text is cached by file and engine,
  follows the text layer in `source_text` after ` || OCR: `, and a quote
  found only there needs "OCR" in its anchor. A missing engine raises,
  never reads as empty. The grading rule of plan Q3 (an image file outside
  a PDF is HIGH only when corroborated) is enforced by the applier. Scan
  (2026-11-01): 64 of 1,703 local PDFs have thin pages, 221 in all; OCR
  supplies the text of udaru, mancilla and qci-2026 whole (INTAKE section
  61). Each test proven red. No store write
- **feat**: Sprint 15 Task H step 1: the Sprint 15 reader prompt
  (`manifests/sprint15_f114_reads/READER_PROMPT.md`): figures and images
  are read (the caption-only exemption is gone), each in a `figures` list;
  a value read from a figure says so, writes each number read by eye as
  "about N", and is never HIGH; OCR text is quoted as given and marked;
  a full read lists its sections; a reader never changes a stored context;
  anchors are PDF pages; one claim per assertion; a textbook result is no
  reason for LOW; a paper on no context is still read in full. The reader
  check's `--sprint15` option checks each rule (a quote must be on a page
  its anchor names), and the applier refuses a figure value that is HIGH
  or unlabeled. Each test proven red
- **fix**: the fresh-eyes review of Tasks F and H step 1 (before their
  commit): OCR boxes are joined by spaces, so a box holding only a number
  (a table cell) is no longer dropped as a page number; the OCR cache key
  holds the pages read, the worker's hash and the engine's interpreter, so
  a newly thin page reads again instead of being served empty; the
  applier reads an OCR anchor that holds parentheses; the prompt finds a
  page by `page_texts`, never by counting form feeds; the page check reads
  page lists ("p.4 and 9") and shortened ranges ("pp. 123-24") and skips
  an anchor with no page; `page_count`, the page split and the check's
  page text are kept per process; "about -0.5" is a figure reading; a
  reader may not add a context where the stored one is empty. Each proven
  red
- **feat**: Sprint 15 Task H: `scripts/sprint15_f114_local.py` writes the
  100 papers' briefs (24 groups, 2026-11-01): re-entry groups g062-r1,
  g064-r1, g076-r1 (the three image-only papers, now read from OCR text)
  and g113-r1, then ledger order from g114 to g133. Four records whose
  source is a directory (a code repository) are left for a later release:
  the quote check reads one file per source. g069's and g072's unread
  records stay unread (the saved web page holds no article)
- **feat**: Sprint 15 Task K (F124): Phase 2's F151, F153 and F154 source
  records re-read whole at Phase 2 develop af03165 and repointed there
  (`scripts/sprint15_f124_phase2.py`, INTAKE section 62). Their 5 stored
  values confirmed by name; every stored quote verbatim at af03165; the
  first read and its blob SHA-256 kept. Store: 3 read rows, 3 repoints
  (backup `evidence-20261101T174117632352-...db`); the local-file check
  reads all three as unchanged. Test proven red on the pre-apply backup
- **docs**: Sprint 15 Task L (F129): the LOW grades resting on a textbook
  fact (`manifests/sprint15_f129_proposals.json`): of 29 keyword
  candidates (snapshot 2026-11-01), 10 proposed HIGH for the team lead's
  decision at Manual Validation, 6 kept LOW for another cause, 13 not a
  textbook fact; 30 sampled misses hold none. No store write
- **feat**: Sprint 15 Task J (F128): the gap-reading targets
  (`scripts/sprint15_f128_targets.py`, INTAKE section 63). 8 arXiv papers
  fetched by the paced fetcher and entered at `seen` (Gidney and Ekera,
  Lee et al., Woerner and Egger, Chakrabarti et al., Babbush et al.,
  Stoudenmire and Schwab, XGBoost, Jaques and Rattew; backup
  `evidence-20261101T182904857546-...db`); with Faryad they are ledger
  groups g331 and g332, read under Sprint 15's prompt. Giovannetti et
  al. was held under its DOI with a local copy: the copy fetched again
  was deleted the same hour, and the script now never fetches it. 7 on
  the hand-download list with their reasons (LightGBM, Ferrari Dacrema,
  Nielsen and Chuang, vendor gate documentation, Dal Pozzolo 2014, and two
  with no source chosen)
- **docs**: Sprint 15 Task G (F116): the figure pilot, ledger group g114
  under Sprint 15's prompt (2026-11-01): 5 papers, 86 pages, 47 figures,
  174 new assertions, 0 check problems, about 85 minutes. Rendering and
  viewing a figure took about 15 s and entering it about as long again,
  so figures add roughly 10 to 15 percent to a read. The prompt gained a
  dated amendment from it: a crop command for small panels, and text-layer
  tables are entered as figures
- **fix**: the door no longer reads a title word as an audit marker
  ("error-corrected" held "CORRECTED"; `store/ingest.py`). Test proven red
- **feat**: Sprint 15 Task H: the review prompt
  (`manifests/sprint15_f114_reads/REVIEW_PROMPT.md`), Sprint 14's with
  three rules added: a textbook-standard result is never by itself the
  reason for LOW (F129), a value read from a figure is never HIGH (F116),
  and OCR text of a stored PDF grades as its text layer while an image
  file outside a PDF is HIGH only when corroborated (plan Q3)
- **fix**: the reader check's `--sprint15` option refuses a new assertion
  that names its id `id` instead of `id_suggestion` (reader g117: 36 of
  one paper's 37 assertions passed the check that way; the builder already
  took either key). Test proven red
- **fix**: the reader check's `--sprint15` option lets a stored assertion
  keep its own context when it is not one of the five (reader g133: two
  emami-2025 assertions stored under `platform:dirac-3` could neither
  keep the stored context nor pass the five-context check). Test proven
  red
- **fix**: the fresh-eyes review of Sprint 15's uncommitted scripts
  (2026-11-02), each fix with a test proven red:
  - g064-r1's review names the reversal of qci-2026's 2026-10-15 refusal
    (its PDF had no text layer; OCR now reads it), which had stopped the
    apply;
  - `full_read_apply.py` counts an anchor holding its own parentheses,
    so quotes from two places are never collapsed onto one, and raises
    when sync's date guard would skip an anchor move the dry run listed;
  - `f117_build_groups.py` builds only the groups `--group` names, and
    records each local reader file's SHA-256 so a run stops when a
    reader file changed after its group was built (g130 was built while
    its reader was editing);
  - `store/quotes.py` treats a figure or table label as a name without
    excusing its number elsewhere in the value ("Read from Figure 3:
    ... at depth 3" passed); one g123 value read off an axis became
    "about 10" at the sign-off;
  - the reader check's page anchors include "page", "pages" and any
    case, and "p.0" names no page;
  - `f114_cloud.py fetch` keeps a branch pushed before its first commit
    pending, not refused as merged;
  - `sprint15_f114_local.py`: a Task J record needs a local file (not a
    URL ending ".pdf") and a store row; `sprint15_f128_targets.py`
    writes its manifest only on an apply, adding to what was entered
- **feat**: Task I's 100 records (F133): `sprint15_f114_local.py
  --task-i` writes the briefs of ledger groups g134 to g154, never
  reaching Task J's groups. Test proven red
- **test**: Task J's groups are added to the ledger once, after g330, and
  never over a record another group holds
  (`scripts/sprint15_f114_local.py` `add_j_groups`). Proven red
- **fix**: `f117_review.py finalize` names Sprint 15's tag and reader
  prompt for a read that carries `figure_count`; it named Sprint 14's.
  g062-r1's review was written that way, deleted before any apply and
  written again. Test proven red
- **fix**: the group builder skips the page fixer for a source that is not
  a PDF (g120's saved web page stopped the build) and splits a PDF's
  pages with `store.ocr.page_texts`, as the reader check does, not on
  form feeds alone. No group built so far was affected: each of their
  PDFs splits on form feeds into its page count. Each proven red
- **docs**: carded F134 (a table cell that holds only a number is dropped
  by `plain()`, so it is missing from the non-layout text a quote is
  checked against) and F135 (a stated limit on a measured result meets the
  check that a measured result is never HIGH; reader g118 changed five
  result types to pass it)
- **fix**: a figure label's panel letter may be upper case
  (`store/quotes.py` `FIGURE_LABEL`): the recheck of every Sprint 15 read
  under the wider page rule refused g134's "Figure 7C and 7D" for its 7.
  The recheck found one other problem, g123's "n = 10", already fixed at
  sign-off. Proven red
- **fix**: a number joined to a figure label is part of the label only
  when no word follows it (`store/quotes.py` `FIGURE_LABEL`): in "Figure
  3, 4 qubits" the 4 is a count and must be in a quote. Found by the
  fresh-eyes review of the panel-letter fix. Proven red
- **test**: F128's manifest is written only by an apply, which keeps what
  an earlier apply entered (`scripts/sprint15_f128_targets.py`
  `record_entered`, moved out of `main`). Proven red both ways
- **feat**: Sprint 15 Tasks H and I applied (2026-11-04, INTAKE section
  64, snapshot as of that date): every finalized group applied in one live
  apply after a trial on a store copy, with a verified backup: 4,947
  assertions, 190 read rows, 86 updated, 11 records set to `read`, 8
  applicability rows; the 3 undecided fields accepted; a second apply
  entered nothing. The cross-group
  pass on absence items set g144's two "no experiment" items HIGH (9 of 10
  stored precedents are HIGH) and kept pqc-no-experiments LOW; five
  dees-2023 items and 64 escalations go to Manual Validation
- **docs**: INTAKE_WORKFLOW.md section 65 names Task L's
  `manifests/sprint15_f129_proposals.json` (10 proposed HIGH, 6 kept
  LOW, 13 not a textbook fact; snapshot 2026-11-01). The full suite of
  2026-11-04 found it unnamed (`test_every_committed_manifest_is_named_in_the_workflow`);
  nothing in it is applied before Manual Validation
- **feat**: Sprint 15 Task M (F130): Phase 2's Sprint 30 results by the
  inbound path (`scripts/sprint15_f130_phase2.py`, INTAKE_WORKFLOW.md
  section 66): five records (F174's IEEE-CIS comparison set, F176, F169,
  F170, F171) and nine HIGH assertions, every quote checked verbatim
  with its value at Phase 2 commit 366cf37; none linked, each reason
  names the stored claims it bears on. F166 repointed at the same
  commit, its four values confirmed, which clears the local-file block
  (Question 1 = 3). `tests/test_sprint15_f130.py`, each injection proven red
- **fix**: Sprint 14's F120 apply leaves a record re-read whole at a later
  commit alone; it would have put F166's 6242b8a evidence back over the
  F130 repoint. Proven red on a store copy
- **fix**: the fresh-eyes review of F130 (no blocking defect): five values
  carry the limits their documents state, one reason no longer
  overstates F152, a rerun syncs corrected values and keeps a later F166
  repoint (proven red), and the run-file test checks all seven gaps
- **fix**: three older checks that Sprint 15's full reads broke, found by
  the full suite on 2026-11-04 (each red there before its fix). Sprint 9's
  F46 apply leaves a record a later full read owns alone; it would have
  undone F114's correction of faryad-state-prep-omega-2n-dimension-count.
  F80's refusal test accepts a refused record a later full read took
  (qci-2026, read whole by OCR). The spelling fixer protects the stored
  id optimised-parameter-shift-two-versus-three-evaluations, which section
  64 names
- **feat**: Sprint 15 Task M applied (2026-11-04) after PR #74 merged as
  43bc362 (366cf37 its ancestor, no F130 input changed): trial, live
  apply with verified backup, second apply wrote nothing. The store
  test compares a tuple, not a sqlite3.Row (proven red by injection)
- **fix**: the fresh-eyes review of the three fixes: F46's guard also
  keeps a full read's correction after a later note that is not a full
  read (the rule `sync_assertion` applies; a test proven red on a store
  copy), and F80's refusal test fails if no refused record is left to
  check. The full suite of 2026-11-04 after the F130 apply: 1,531 passed
  (marked INVALID: these fixes were edited during the run; their own test
  files pass, 66 tests). No further full run, at the team lead's word
- **docs**: correction to d485069's title ("100 papers read whole and
  applied"): every record of Tasks H and I is read and reviewed, but
  only the 23 finalized groups of Sprint 15's 47 are applied. The other
  24 (about 114 records) each hold a certainty change only the team lead
  decides (36 in all), so their reviews are not finalized and the apply
  does not take them; they are applied after Manual Validation.
  Snapshot as of 2026-11-04. Sprint 15 moves to Manual Validation
- **feat**: Sprint 15 Manual Validation applied (team lead, 2026-11-04;
  INTAKE section 67): Q1's 36 certainty changes recorded in the
  escalation files, the 24 waiting groups finalized and applied (trial:
  6,282 new assertions, 228 read rows, 157 updates);
  `scripts/sprint15_mv_decisions.py` sets F129's 10 proposals HIGH (Q2),
  g144's two absence items MODERATE (Q4) and one context from `method`
  to `qc` (Q6); Q3 and Q8 write nothing. `tests/test_sprint15_mv_decisions.py`
- **fix**: the applier checks a sign-off's edited figure reading with the
  figure exemption its own quote check gives (five were refused), and a
  confirmed row rebuilt for its grade keeps its stored fidelity, claim
  type and search scope (the trial listed eight rows changed). Each with
  a test proven red
- **fix**: the fresh-eyes review of the Manual Validation apply: the
  applier keeps a grade the team lead decided ("the team lead's decision
  at") unless its review records a decision too, so no rerun's date can
  undo it; a confirmed row that keeps a vendor claim type is never
  written HIGH. The decisions script is dated the day it ran
  (2026-11-05): its first run, dated 2026-11-04, was restored from its
  backup and re-run. Test proven red
- **fix**: the `--changed` run after the Manual Validation apply (5
  failed of 1,086). `store.ingest.sync_assertion` refuses a sync dated
  before a row's latest Manual Validation decision note (new
  `decided_day`): a rerun of `sprint12_reading.py` moved
  qng-study-scope-toy-model's context back from `qc`, the team lead's
  Q6 = 2 (synthetic test and the live second-apply test, both proven
  red). Three older tests held data that the team lead's decisions and
  Sprint 15's full reads changed: the learnings balance is compared with
  a distinct count per grade (proven red), F101's re-quoted record a
  later full read owns is checked for verbatim quotes only, and the
  Sprint 12 store test skips a row decided later. The applier's field
  test builds a dataclass, which the confirmed-row rebuild needs. Its
  fresh-eyes review found no blocking defect; `decided_day` also reads a
  decision named in a note's body (Sprint 8 and 9's shape; proven red),
  the sync test checks the same-day boundary, and the Sprint 12 skip
  compares with the latest day that script syncs on
- **fix**: Copilot's review of PR #149. `page_text` stops on a pdftotext
  failure instead of reading it as an empty page (`check=True`; pdftotext
  exits 0 on a page range past the end, checked). The audit-marker check
  in `validate_paper` guards the right side of a marker that ends in a
  letter, so a title word such as "Correctedness" or "Corrected-error"
  passes; its fresh-eyes review kept "NOTE:x" and "CORRECTED-2026-09-16"
  refused. Both tests proven red
- **process**: Sprint 15 Phase 7 (2026-11-05): the retrospective
  (`docs/sprints/SPRINT_15_RETROSPECTIVE.md`; team lead "Very Good" in
  every rated category, "none" for 13, 14 and 16), the summary with its
  Actuals (`SPRINT_15_SUMMARY.md`), the master plan's Past Sprint Summary
  row and Last Completed Sprint entry, and the checklist's Sprint 15
  section. One improvement put to the team lead (Q1, the trial store copy
  takes its text cache)
- **docs**: carded F136 (the applier checks the quotes of what it writes,
  not of every reviewed row; team lead, Q9) and F137 (the two Dunjko
  records share one PDF; Q5); F57's card says Sprint 16's release follows
  its ranking (Q7)
- **docs**: F57's card names one paper for Sprint 16's release to read
  first (team lead, 2026-11-05): `Quantum_NeuralNetwork.pdf` in
  `wangy8205165/Quantum-NeuralNetwork-WhitePaper`. Sprint 12 entered the
  repository only; the PDF has no paper record and no local copy
- **docs**: F57's card adds arXiv 2108.13346 (QBoost for regression,
  Goes et al., 2021; the team lead's `QuantumBoost/qboost.pdf`), fetched
  from arXiv as v2 only and read after the white paper unless already
  read. F136 is
  widened (team lead, 2026-11-05): each PDF's text is extracted once,
  ever, from one fixed cache every store copy reads, and each quote is
  checked once, ever. This replaces retrospective Q1
- **process**: retrospective Q1 answered (team lead, 2026-11-05, Q1 =
  1): F136 is Sprint 16's first task (Priority 10, about 50m); recorded
  in the retrospective's Improvement Decisions. Phase 7.7 complete; PR
  #149 marked ready

### 2026-10-29 to 2026-10-31 (Sprint 14, PR #140, merged to develop 2026-10-31 and to main via PR #148 the same day; tagged sprint-14)

- **chore**: Sprint 14 opened (2026-10-29). The team lead merged PR #131
  into develop (bb4cb80) and PR #139 to main (952c9e3); `sprint-13`
  tagged on 952c9e3; branch `feature/20261029_Sprint_14` cut from the
  Sprint 13 branch (6.6 carry-forward). PR #139 is titled "Sprint 12:
  Develop to Main"; it was Sprint 13's release. Phase 1.1
  reconciliation: every commit since 2026-10-28 has its entry
- **docs**: Backlog refinement 2026-10-29 (Sprint 14 Phase 1.2 to 1.4):
  Sprint 13's shipped cards pruned by hand (F107, F108, F109 to F112,
  and F113, whose definitions of a full read and acceptance move into
  F114); F120 carded from Phase 2's Sprint 29 work at 22d16c3 (F156,
  F158, F160 and F166 results); snapshots refreshed on F95 (166 unnamed
  PDFs: 165 are Task G's downloads of store records, 1 is F119's paper),
  F98 (Roadmap-to-QML at ea6f42a7c0: 4 new arXiv ids, 7 withdrawn or
  retracted marks), F57 (unchanged: 654 with no read row) and F51 (hold
  unchanged). Phase 1.3: 0 re-checks due; no ADR or schema change in
  Sprint 13. Slate presented
- **docs**: PR #139 retitled "Sprint 13: Develop to Main" (team lead,
  2026-10-30, Q2 = 1). F121 carded (team lead, 2026-10-30): a spike over
  the store as it stands, for what has been learned, what it means for
  the competition approach, and which experiments to run, before Sprint
  14's scope is selected; F118 stays as the full synthesis after F117.
  Then merged the same day (team lead: "Update card F118 and sit this in
  sprint 14 after F117 completes"): F121 retired, its three outputs
  (what was learned, what it means for the approach, which experiments)
  and its approach moved into F118, which is placed in Sprint 14 after
  F117. The team lead's own questions (pasted 2026-10-30 under "Not
  asked yet": gates and micro algorithms, data in and out, non-hybrid
  uses, hybrid practice, where advantage shows and at how many qubits,
  how each classical model family fits a hybrid, GenAI) added to F118
  verbatim, with a keyword coverage snapshot; estimate 240m to 360m
- **docs**: Sprint 14 scope selected (team lead, 2026-10-30): F119, F95,
  F98, F120, F117, F118 (after F117) and F114 at 50 papers; released
  copies F122 (F95) and F123 (F98); F39 not selected. Plan drafted
  (`docs/sprints/SPRINT_14_PLAN.md`). Pre-flight finding: the 302 cloud
  results' local copies and `launches.json` are gone from the Temp
  folder (cause unknown); the 302 `cloud/f114/<record>` branches remain,
  and Task E rebuilds from them first. Phase 2's Sprint 29 merged (PR
  #63 at 6242b8a), so F120 reads it through the GitHub API. Draft PR
  #140
- **docs**: Sprint 14 plan approved as amended (team lead, 2026-10-30):
  Q1 = 2 with the Boyd book completed (F114's 50: abbas-2020-power, Boyd,
  then the next 48 in ledger order; the other abbas-2020 paper is one of
  the cloud results, so the plan corrects the option's "two"); Q2 = 1
  (a result not read in full is re-read this sprint); Q3 = 1 (the cloud
  work folder moves to `work\f114\` outside Temp). Issues #141 to #147
- **feat**: F119 (Sprint 14 Task A, #141, 2026-10-30): Brighindi's
  PHI-OMEGA paper read in full and entered with its posts, comment
  thread, three images (read by eye, described, not quoted) and the two
  author repositories that bear on its claims
  (`scripts/sprint14_f119_reading.py`, INTAKE section 54). 4 source
  records and 11 assertions under `ml`: the paper's definitions, its
  test's setup, the absence of any proof, and the repositories' own
  stated limits graded HIGH on those bases; its central claim, its
  reproducibility claim and both posts LOW as the author's claims; the
  Figure 1 result and the repository's counts LOW as one-seed measured
  results. One `contradicts` link: the author's repository says the test
  is not reproducible from it and proves no immunity. The Zenodo archive
  holds 610 file entries (not 608) and bears on none of the claims. A
  second apply writes nothing; tests proven red by injection
- **docs**: F122 (Sprint 14 Task B, #142, 2026-10-30): the F95 release.
  374 PDFs in `Papers\`; 166 unnamed before, 165 after (Task A named the
  PHI-OMEGA paper). The 165 are Task G downloads of store records in
  ledger groups g295 to g329, linked by the ledger; `access` names each
  file when F114 reads its group (the narrower reading of step (2),
  disclosed in INTAKE section 55). The hand-download list holds 53
  records, none with a local copy. No store write (ebff67c)
- **fix**: F119 corrected after its fresh-eyes review (Sprint 14 Task A,
  #141, 2026-10-30; INTAKE section 54, dated correction). The runtime
  read had missed `docs/M_OMNIA_STATO_RICERCA_2026-09-27.md`, which calls
  the closure a formalization hypothesis and the stress test a simulator
  result, not a general proof: read in full, a 12th assertion (HIGH,
  stated limit) entered, the read row and the absence claim's search
  scope corrected. Two `contradicts` links added to the paper's central
  claim (its "demonstrating absolute structural immunity" cannot hold
  beside the repository's limits); two values' repository and thread
  text now quoted and checked; the stress limit adds that rejections are
  not a solution of the task. A second apply writes nothing; tests
  proven red by injection (6d5bcec)
- **fix**: F119 corrected again after the review of 6d5bcec (Sprint 14
  Task A, #141, 2026-10-30; INTAKE section 54, second dated
  correction). The status-note assertion's `contradicts` link withdrawn:
  a simulator-only result can hold beside a claim of immunity inside
  that simulator (ADR-0004 A8 (b)); one link to the central claim
  remains, from the stress-test limit. The m-omnia read row now records
  its search (30 tracked files, no hits); each corrected row keeps its
  first text in updated_reason. A new test puts the first rows and the
  link back on a store copy and checks the apply corrects them; proven
  red by injection
- **feat**: F117's first step (Sprint 14 Task E, #145, 2026-10-30): the
  F114 cloud results rebuilt from their 302 branches, since Temp lost
  the only local copy and `launches.json`. `scripts/f114_cloud.py`
  gains `rebuild`: each branch's base is its merge-base with the Sprint
  13 branch (5 launch commits), the stray-file check runs from it, and
  the session and attempt come from the run log where it names them
  (297 of 302). Its work folder moves out of Temp to
  `D:\Data\Harold\EvidenceBasedDB\work\f114\` (Q3 = 1), with the 329
  briefs and the run log, each copied and checked by SHA-256 before the
  Temp copy was removed. Result: 302 results saved, 0 refused, 0 stale;
  the two papers never to be launched again (udaru-2025, abbas-2020) are
  marked. Test proven red by injection three ways (92d7634)
- **feat**: F117's applier (Sprint 14 Task E, #145, 2026-10-30):
  `scripts/sprint13_g_reading.py` takes, from a group's review file, its
  own tag and reader (F114's groups were read in cloud sessions and are
  entered in Sprint 14, so Task G's "Sprint 13 Task G ... subagent"
  wording would misstate their provenance), a reader per record (15
  results whose commits do not record the model), and `unread` records
  left out of their group with why (udaru-2025 in g076). Task G's 42
  groups dry-run unchanged (5,489 assertions from 210 records). The
  rebuilt 302 results all pass `sprint13_g_check.py` against their PDFs
  again (0 problems). Tests proven red by injection (de1efff)
- **fix**: F117 review fixes and the group build (Sprint 14 Task E,
  #145, 2026-10-30). Review of 92d7634: `rebuild` refuses a result
  branch already merged into the launch branch (its merge-base would be
  its own tip, so the stray-file check would see nothing; none is
  merged today); `scripts/sprint13_g_ledger.py` writes briefs to
  `work\f114\briefs`, where they now live. Correction to the 92d7634
  entry: the run log gave a session for 295 of the 302 branches, not
  297 (297 counts the 2 unread entries). New
  `scripts/f117_build_groups.py` assembles the per-paper results into
  group reader files in ledger order, renaming `id` to `id_suggestion`
  in 22 results; only whole groups are built (59 groups, 294 records:
  g079 and g103 wait for Task F). Tests proven red by injection (d2fcc8d)
- **feat**: F117's 59 group reader files written (Sprint 14 Task E,
  #145, 2026-10-30): `manifests/sprint13_g_reads/group_g043.json` to
  `group_g102.json` less g079, 290 records. Two build changes first.
  (1) 36 new-assertion ids that another paper also suggested (each
  session saw one paper, so `conclusion-summary` and the like repeat)
  or that the store holds for another source take their paper's author
  and year as a prefix, listed by the build. (2) Four results whose file
  gave nothing to read (mancilla-2026 and qci-2026 PDFs with no text
  layer; two qci-research web pages saved without their article) are
  left out unread, on the team lead's udaru precedent. The applier's dry
  run over the 59 groups finds no duplicate or clashing id. The Haiku
  tier flagged 69 of 302 results; every flag is a limit of the file
  (equations, tables, figures or supplements lost by the text layer, or
  no text), none a reader omission. Tests proven red by injection
  (cecf20d)
- **feat**: F117's Sonnet tier set up (Sprint 14 Task E, #145,
  2026-10-30): `manifests/f117_reviews/REVIEW_PROMPT.md` (the five HIGH
  bases, one decision per item, read in the paper's text, no budget)
  and `scripts/f117_review.py`, which lists each group's items (a new
  HIGH suggestion, a new theoretical result, a changed stored
  assertion, a confirmed stored HIGH) and turns the reviewer's
  decisions into the applier's review file. It refuses a missing
  decision, a HIGH outside the five bases or a decision with no why,
  and holds back any certainty change on a stored assertion for the
  team lead. Pilot on g043 (204 items) running. Tests proven red by
  injection (46d088d)
- **fix**: F117 items carry the stored text (Sprint 14 Task E, #145,
  2026-10-30). The g043 pilot found two stored-HIGH items blank: a
  reader who confirms a stored assertion may leave its value and quotes
  empty. Each changed or stored-HIGH item now carries `stored_value` and
  `stored_quotes` from the store, and the prompt says to decide on them.
  The pilot read the blank one from the store itself, so its decisions
  stand. Pilot: 204 decisions in about 8 minutes; g043 holds two
  LOW-to-HIGH changes for the team lead. Test proven red by injection
  (7f18e9f)
- **feat**: F120, Phase 2's Sprint 29 results entered (Sprint 14 Task D,
  #144, 2026-10-30), read at Phase 2 commit 6242b8a with `git show`
  (the team lead's clone now holds it; the plan said the GitHub API,
  which gives the same bytes). Two source records: the F166 document set
  (the ULB comparison and seven algorithm documents) and Sprint 29's
  validation record with its three preregistered entries. Nine SIM
  assertions: F166's tuned ranking, the proxy's train-test gap, recall
  at the alert budget and the classical tuning choices; F156's failed
  Henze-Penrose bound; F158's cascade below one model and the ULB frauds
  every stored model misses; F160's room check passing on IEEE-CIS;
  F159's parallel build. One stored value corrected: the F108 plug-in
  ratios now top out at 1.119 (Phase 2's F164 recomputation). The F108
  and F162 records repointed at 6242b8a. No relation linked (ADR-0004
  A8 (b)); each reason names what it bears on. A live test checks the
  headline figures against the run files. INTAKE section 56. A second
  apply writes nothing. Tests proven red by injection. Closes #144
  (1f904ba)
- **process**: F117's review prompt names the reading rule outright
  (Sprint 14 Task E, #145, 2026-10-30). Five of the first reviewers
  (g044 to g047, g049) decided some items, mostly setup items, from the
  quote or a grep snippet. Each was sent back and re-read them in
  context; g044 changed one decision and g045 thirteen (LOW to HIGH,
  once the full statements were read). The prompt now says setup items
  are read in context too and that a reviewer names any item it did not
  read; each launch repeats it and gives the reviewer its own scratch
  folder, after two reviewers overwrote each other's scratch files
- **feat**: F123, Roadmap-to-QML's release for Sprint 14 (Sprint 14 Task
  C, #143, 2026-10-30), read at ea6f42a7c0, 9 commits after F104's
  a239747648. 1,450 arXiv ids listed; 32 linked for the first time, 28 of
  them already held (the list replaced publisher links with arXiv links).
  The 4 new papers entered at `seen` with their free copies; the 28 held
  ones get a route naming the list at this commit, and no other route is
  restated. The list's 7 withdrawn or retracted marks all agree with the
  store (F33); no record changed. 20 non-arXiv links carried (25 at
  F104). `scripts/sprint14_f123_roadmap.py` reuses F104's script.
  INTAKE section 57. A second apply enters nothing and adds no route.
  Tests proven red by injection. The 4 reads run beside Task F's
  (577380e)
- **fix**: F120's fresh-eyes review of 1f904ba (Sprint 14 Task D, #144,
  2026-10-30). High: the two new Phase 2 source records failed the
  local-file check, because their evidence named the documents' hashes
  without "SHA-256" and the check read a run file's hash first; the
  evidence is rewritten, and a live test runs the check on all four
  paper records (red on the pre-fix backup). Medium: the corrected F108
  value carried Phase 2's BLUF range (0.5-1.8 points), which F164 left
  as it was; the value now attributes it, and the reasons give the range
  from the corrected ratios (0.57, 1.91, 1.56), computed here. Medium:
  F166's ranking now says the proxy uses its own top 17 features and the
  classical lanes all 30 columns. Low: five values reworded against the
  sources (F158's named risk and its models' features, F159's inferred
  wait and one seed, F160's data term, its "so" and F25's card, F166's
  attributed equality, F156's fifth and sixth methods). Tests now check
  the corrected value exactly, F166's figures against its run file, the
  named records exist, and the unchanged F108 and F162 quotes at
  6242b8a. F124 carded for the stale f151, f153 and f154 pointers.
  INTAKE section 56 addendum. A second apply writes nothing (454c7a4)
- **feat**: F114's local reads set up (Sprint 14 Task F, #146,
  2026-10-30). A new reader prompt,
  `manifests/sprint14_f114_reads/READER_PROMPT.md`: Task G's text with
  every path under `work\f114\local\` (the `s13g` folders are empty since
  Q3 moved the work). `scripts/sprint14_f114_local.py` writes the briefs
  for F's 50 papers in 12 groups (g079's abbas-2020, g103's Boyd and
  bucher, g104 to g112, g113's first 2), adds ledger group g330 for Task
  C's 4 papers, and seeds Boyd's resume in `partial\`, never `done\`,
  from page 1, since its cloud read sampled the book. The group builder
  takes a local read over a cloud result, does not count Boyd's cloud
  result as a read, waits for each local reader's group file, and leaves
  g113's other 3 records for F114's next release. `finalize` names the
  local reader and Task F's tag. Tests proven red by injection (1cb63bb)
- **fix**: the fresh-eyes review of 1cb63bb (Sprint 14 Task F, #146,
  2026-10-30). Two of the new guards had tests that could not fail:
  the test patched WAIT, and its brief held no unread record. WAIT is now
  `waiting()`, read from the briefs and the readers' group files, and
  the test exercises both. The builder takes a local read from the
  reader's checked group file, not its `done\` file. In a group that
  mixes cloud and local reads, `finalize` writes a per-record `tags`.
  The applier reads that field, so abbas, bucher and Boyd will not carry
  "F114 cloud read". The applier also says "first-pass subagent" for a
  local read, where it said "cloud session" for every Sprint 14 group.
  `f114_cloud.records()` stops at g329: g330 has no cloud brief, so
  `launch` and `run` crashed on it. F125 is carded for g113's 3 unread
  records, which have no way back in, and for the stale status script.
  Each fix was proven red by injection. g079's group file was built
  before the fix, and it matches the reader's checked file (f599950)
- **fix**: F114's local reads anchor the PDF page (Sprint 14 Task F,
  #146, 2026-10-30). g104's reviewer found page anchors 1 to 3 pages
  off. A check against the PDFs' pages found the same in every local
  group: g105, g106 and g107 ran up to 15 pages off, and Carlesso's
  lecture notes cited the printed page numbers. The readers' text layers
  had lost their page breaks. The cloud groups g095, g100 and g101 were
  mostly right (0 to 6 misses a paper, nearly all one page). The group
  builder now computes a local read's page from the PDF. An anchor
  naming one page or range takes the pages its quotes are on. An anchor
  with a quote off its pages, whose page cannot be computed, loses its
  pages and keeps its sections. An anchor with no quote found is left as
  it is. Each change is listed. The rebuild changed 288 anchors in g079
  and g104 to g107: 211 set and 77 dropped (snapshot as of 2026-10-30).
  The reader prompt now says a page is the PDF's page, counted with
  pdftotext's form feeds, and the readers still at work were told.
  g079's and g104's group files and g104's provisional review were
  deleted and rebuilt. None was committed, decisions are keyed by id, and
  the item counts did not change. Proven red by injection (11d443a)
- **fix**: the fresh-eyes review of f599950 and 11d443a (Sprint 14 Task
  F, #146, 2026-10-30). 11d443a's page fix wrote wrong anchors in 4
  ways:
  - A page list ("p.6, 14", "pp.6 and 8") kept its stale tail.
  - One range stretched across several sections ("pp.1-7").
  - A drop left stray punctuation and the rest of a page list.
  - An unfound quote forced a drop.
  A page clause is now the whole list, and it is read with an em dash,
  "page 9" and "PDF p.N". A "printed p.N" clause is left alone. Pages
  that are not one run are listed. A quote that is not found counts
  only in that the pages it may be on are kept. Cleanup is checked
  case by case.
  The rebuild of g079 and g104 to g107 changed 287 anchors: 42 lost
  their pages and none was left for the coordinator (snapshot as of
  2026-10-30). No changed anchor shows stray punctuation or a leftover
  page tail.
  Those group files and the reviews of g104 to g107 were deleted and
  rebuilt again (uncommitted). The item ids did not change, and each
  re-finalize gave its earlier counts.
  The applier test also could not fail with RECORD_TAG left out of
  `is_mine`: its GROUP_TAG held the local tag too. Each fix was proven
  red by injection
- **fix**: the fresh-eyes review of 8f2b408 (Sprint 14 Task F, #146,
  2026-10-30). The page fix still wrote wrong anchors in 5 ways:
  - "Printed p.145" and "printed: p.145" were taken as PDF pages.
  - A list took in the number after it: "p.12, 4.3" became "p.7.3",
    and "p.3, 2024 edition" lost its year.
  - A range with "to" ("pp. 12 to 15") left " to 15" behind.
  - A drop left "(, Figure 2)", "[]" or a dangling "on".
  - A compressed range ("pp.112-15") named no page.
  A list now goes on only to a bare number that ends its clause. The
  rebuild of the 13 local groups (g079, g103 to g113, g330) changed 9
  anchors, all damaged before by "to" ranges, such as "pp.6, 9 to 6 and
  9" and "Section 5, to, Fig. 6" (snapshot as of 2026-10-30). No id
  changed, so the reviews stand. Each fix was proven red by injection
- **fix**: the fresh-eyes review of aa8c75f (Sprint 14 Task F, #146,
  2026-10-30). Two regressions and one new defect:
  - A page list ending its sentence lost its tail: "pp.6, 8." became
    "p.8, 8.".
  - A "to" took a count after it: "p.4 to 6 qubits" became "p.12
    qubits".
  - The preposition cleanup removed any "on", "at", "in" or "see"
    before a comma: "(noise turned on)" lost its last word.
  A list item may now end with a period; a "to" range must end its
  clause or be followed by "of"; a preposition goes only with the page
  clause it led into. The rebuild of the 13 local groups changed no
  anchor (snapshot as of 2026-10-30). Each fix was proven red by
  injection
- **fix**: the fresh-eyes review of ee397c6 (Sprint 14 Task F, #146,
  2026-10-30). Allowing "of" after a list item let a count join the
  list ("p.12, 4 of 10 qubits" lost its 4): "of" now ends only a "to"
  range. A preposition after "(" or first in the anchor, in any case,
  now goes with its page clause ("(see p.4)" left "(see)"). "p.4.2" is a
  section, not page 4. The rebuild of the 13 local groups changed no
  anchor (snapshot as of 2026-10-30). Each fix was proven red by
  injection
- **fix**: the fresh-eyes review of ccaedc2 (Sprint 14 Task F, #146,
  2026-10-30). Its guard for "p.4.2" held only for a one-digit page:
  the regex backtracked, so "p.12.3" matched "p.1" and became "p.72.3".
  The first number now may not be followed by a digit either. A
  two-digit case was added and proven red. The rebuild of the 13 local
  groups changed no anchor (snapshot as of 2026-10-30). Left as it is,
  cosmetic and older: a dropped "p.4 to 6 of 10" leaves "of 10"
- **docs**: F126 carded (Sprint 14 Task F, 2026-10-30): the page-anchor
  leftovers. The fresh-eyes review of 59233c1 found no new defect and
  one older low-severity gap (a dash range's end has no ".digit"
  guard). Sprint 14 stopped the review chain there, after five rounds,
  rather than start a sixth for a one-token change. The card also holds
  "of 10" after a dropped "to" range, "p.12a", and
  muta-hardware-scope-photonic-gkp's stored page, which the apply cannot
  correct (its reader entry has no quotes to rebuild it from)
- **docs**: INTAKE 58 written before the apply (Sprint 14 Tasks E and F,
  #145 and #146, 2026-10-30): F114's first release, 72 groups and 351
  records, reviewed by F117; 56 groups finalized and 16 waiting on the
  team lead's escalations (snapshot as of 2026-10-30). The sprint status
  note records the changed commitments (the review chain stopped at
  five rounds; one stored page left for F126)
- **fix**: the fresh-eyes reviews of de1efff, 46d088d and 7f18e9f
  (Sprint 14 Task E, #145, 2026-10-30). The review script and the
  applier disagreed on what is written, so certainty could change
  without the team lead:
  - A stored MODERATE (98 in the store) could go to LOW with no
    escalation (g097's pennylane-gradient-method-fallback-order): every
    stored certainty now counts. A stored NULL is not escalated; it has
    no grade to override.
  - A signed HIGH on a vendor's own claim was written LOW without a word
    (10 new assertions in g049, g052, g054, g056, g067 and g068).
    Finalize and the applier now both refuse it; the store's rule (a
    vendor's own claim is LOW) stands.
  - A settled escalation was taken as written; it is now "low" or
    ["high", basis, why], so the team lead can keep a stored HIGH.
  - A requote of an entry with no value would have blanked the stored
    value; the applier refuses an empty value.
  - Decisions or settlements for no item are refused; finalize needs
    `models.json`.
  - Finalize merges the coordinator's sign-off edits from
    `review\signoff\<g>.json`, so a re-finalize keeps them.
  Each guard was proven red by injection
- **fix**: the fresh-eyes review of d2fcc8d and cecf20d (Sprint 14 Task
  E, #145, 2026-10-30). A group built late could take an id a group
  file already on disk held, since prefixes were given in group order
  over a rebuild in memory (74 author-year prefixes span groups in the
  ledger). Now only groups with no file are assembled, every id in a
  written file counts as taken, a prefixed id is looked up in the store
  too, the same-source test matches the record id as a whole token, and
  only the renames written are printed. Each guard was proven red by
  injection. g113 was rebuilt from its repaired reader file (24
  assertions' quotes re-taken from the canonical text, as the reader's
  own check had failed on them; one value restated in words): no id
  changed. F127 carded for two latent defects the review also found
- **docs**: F127 carded: `f114_cloud.fetch`'s merged-branch path and the
  applier's substring match on a stored provenance
- **fix**: the fresh-eyes review of aabdd49 (Sprint 14 Task E, #145,
  2026-10-30). Finalize now refuses:
  - a LOW the team lead settles against the reviewer's HIGH without its
    own cause (the reviewer's case for HIGH had become the LOW's cause);
    the settlement form `["low", why]` carries it;
  - a settled HIGH on a vendor's own claim (the applier refused it only
    after the signed review was written);
  - a sign-off requote that rewrites a stored certainty nobody decided
    (a stored MODERATE would have gone LOW unasked);
  - a sign-off drop of a stored id, a requote of an entry the applier
    does not rebuild, and an edit on an id it does not write, which the
    applier ignored without a word;
  - a rewritten entry with no value (91 confirmed stored-HIGH entries in
    the F114 reads have none).
  `theory_low` joins the sign-off tables, for a requoted theoretical
  stored LOW. Each guard was proven red by injection. A dry finalize of
  all 72 groups: 56 pass, 16 wait for the team lead, none refused
  (snapshot as of 2026-10-30). Keeping a stored MODERATE on a vendor's
  claim stays a "keep" decision, since store.grading writes a vendor's
  own claim LOW
- **fix**: the fresh-eyes review of 7914e80 (Sprint 14 Task E, #145,
  2026-10-30). No test held an id a written file holds bare and the new
  batch holds once, or drove `main`, so two of 7914e80's guards were
  unproven; both now have a test proven red. A group rebuilt after its
  file is deleted is prefixed against a different batch, so its ids
  could change under its review decisions: the builder now writes
  nothing when a rebuilt group lacks an id its decisions name (proven
  red). An existing file is reported as not rebuilt. Three low findings
  added to F127
- **data**: F114's first apply (Sprint 14 Tasks E and F, #145 and #146,
  2026-10-30; counts a snapshot as of that date). 47 groups entered with
  a verified backup: 7,715 new assertions (2,273 HIGH, 5,442 LOW) and
  117 stored assertions updated; a second apply wrote nothing. Before it,
  the coordinator applied Boyd's consistency ruling and 82 of the
  cross-group pass's 86 proposals, and set 10 reviewer HIGHs on vendors'
  own claims to LOW. 19 groups wait on 28 certainty changes for the team
  lead; 6 groups are held for a context decision on 6 off-topic papers.
  The group files (g079, g103 to g113, g330) and the 47 signed reviews
  are committed; INTAKE 58 has its dated correction; the
  `learning_log` has the tiers' outcomes. The live-store suite then
  failed 9 tests, each acted on:
  - one stored quote held "&nbsp;" from a pricing page
    (braket-simulator-instance-price-tables-not-in-text): cut before it
    by a sign-off `quote_edits` and re-applied with a backup;
  - Sprint 11's and F89's store checks now skip an assertion re-read in
    full (as Sprint 12's did), and F89's refused records may be `read`
    once a full read is recorded (kaur-2022 was read by F114);
  - no paper is left at `screened`, so the applicability injection takes
    a `read` paper, and QBoost is pinned at `read`;
  - the F11 packet is re-rendered (QBoost's tier), and the learning_log
    names an allowed protocol
- **fix**: the fresh-eyes review of b185729 (Sprint 14 Tasks E and F,
  2026-10-30; counts a snapshot as of that date). 10 papers an earlier
  read refused as bearing on no context were entered (467 assertions)
  because F114's reader chose a context. The store was restored from
  the pre-apply backup and the apply run again with the 18 such papers'
  763 assertions dropped by sign-off until the team lead decides, and
  the 6 held groups applied less those papers: 53 groups, 7,897 new
  assertions, a second apply writing nothing. The applier refuses a new
  assertion on a refused paper unless the review names the reversal
  (`reenter`, a new sign-off table); a refusal note names each reason
  once. F89's refused-record test is strict again. Each guard proven red
  by injection
- **feat**: `scripts/f118_themes.py` (Sprint 14 Task G, F118, #147,
  2026-10-30). Read only: computes the store's inventory and selects 16
  themes' assertions by keyword into packets for the theme readers, in
  the non-repository work folder. Its two tests were proven red by
  injection
- **fix**: the fresh-eyes review of 4d969d9 (Sprint 14 Tasks E and F,
  2026-10-30). 6 of the 18 refusal notes carried the reader's
  `why_not`, 3 saying the assertions were entered, and none naming the
  team lead's decision. `refusal_reason` now prefers the sign-off drop;
  a re-apply with a backup appended the corrected note to the 6 records
  and wrote nothing else (INTAKE 58, third correction). Its test was
  proven red by injection. The review's low finding (the refusal guard
  ignores a later reversal, failing closed on 9 QCI Dirac papers) is
  added to F127
- **docs**: the F118 memo, `docs/spikes/F118_WHAT_THE_STORE_SAYS.md`
  (Sprint 14 Task G, F118, #147, 2026-10-30; counts a snapshot as of
  that date): what the store holds per theme, an implication per Phase 2
  and team-lead question, 8 ranked experiments, the Phase 2 prompt
  drafted, every cited id found in the store and 10 read against their
  value. The gaps are carded as F128
- **fix**: the fresh-eyes review of ed5ab01 (Sprint 14 Tasks E, F and
  G, 2026-10-30). The memo overstated three findings, each also in the
  Phase 2 prompt: four LOW single studies do report quantum feature
  selection competitive or better (now named, with untuned comparators);
  benchmark solvers ran at fixed settings, not defaults; the
  data-loading bound is one method's, under a stated condition, and the
  Gram-matrix count is an unproved LOW claim. Smaller corrections: the
  TabICL comparators, the f166 recall wording and both established
  pairs, Monte Carlo has no stored qubit count, four paraphrases
  narrowed, the theme merges named, the snapshot's commit relabeled. A
  live-store test now runs the applier on a store copy and proves the
  refusal note comes through `refusal_reason` (proven red by
  injection); F127's QCI count is dated
- **docs**: F129 carded (Sprint 14 Task E, 2026-10-30): re-check the
  LOW grades that rest only on an unproved textbook fact, 11
  candidates by keyword on that date, against the cross-group rule
- **feat**: F114's last 19 groups applied (Sprint 14 Tasks E and F,
  2026-10-31), after the team lead's Manual Validation answers: Q1, the
  28 certainty changes settled as recommended (4 LOW to HIGH, 23 to LOW,
  cgz-nonuniform-zero-one-corollary7 kept HIGH with its square root
  restored); Q2, the 18 refused papers stay out, their drop reasons
  ending with the decision. 5,000 new assertions (1,796 HIGH, 3,204
  LOW), 136 stored ones updated; INTAKE 58 holds the counts and the 5
  sign-off fixes the dry run forced
- **fix**: the full suite after that apply (2026-10-31) failed 3 tests.
  The apply had replaced 2 stored contexts with the reader's label
  (ballin-2026's Dirac-3 assertion lost `platform:dirac-3`); the applier
  now keeps a stored context unless the sign-off names a `context_fix`
  (test proven red), and both were restored by re-apply. The F80 and F83
  store tests now leave out an id a later full read rewrote and hold
  every other id to its script (proven red by injection)
- **fix**: the review of 0eddd23 (2026-10-31): the 13 theoretical LOW
  settlements now name the team lead's decision (4 had said "no pending
  escalation"); two-way-partitioning quotes its SDP clause; the context
  test takes its ids out of `context_fix`, which had made it pass with
  no check; the F80 and F83 tests skip an id only when its last change
  is a full read's rewrite. INTAKE 58 corrects two counts (138 updated,
  not 136; 100 assertions neither HIGH nor LOW). Re-applied: 13 records
- **fix**: the review of bb82d0a (2026-10-31): 5 of the 13 settlement
  reasons kept a stale or false sentence the pattern edit missed (one
  still said "not in the g097 pending escalations"); each edited by hand.
  The two-way value's "can be solved efficiently" now quoted. INTAKE 58,
  sixth correction. Re-applied: 6 records
- **process**: Sprint 14 retrospective recorded (2026-10-31):
  `docs/sprints/SPRINT_14_RETROSPECTIVE.md`, the team lead's feedback
  verbatim ("Very Good" in every rated category; none for 13, 14 and
  16), with 6 improvement proposals pending the team lead's decision
- **process**: Sprint 14 Phase 7 (2026-10-31): retrospective prompt
  sent; Claude's Development Team draft in
  `docs/sprints/drafts/SPRINT_14_RETROSPECTIVE_claude_draft.md`
- **fix**: the review of 25d3985 (2026-10-31): the barthe reason no
  longer compares against a stored value the apply had replaced; both
  barthe values state the paper's claim as a claim; the caro reason
  loses a reviewer's "Gray:" label. g095 and g106 re-finalized against
  the pre-apply copy. INTAKE 58, seventh correction. Re-applied: 3
  records, backup 173833940424; a second apply wrote nothing
- **docs**: F118 memo updated in place (2026-10-31, team lead: "just
  update in place"): counts as of 2026-10-31 (23,653 assertions);
  F176's answer; production scale and a 10,000-logical-qubit machine;
  experiments that would raise the certainty of stored LOW claims; the
  Phase 2 prompt split at 14 Nov
- **process**: Sprint 14 retrospective decisions (2026-10-31, team lead
  "q1. 1 ... q9. 1"): all nine recorded; Q1 to Q7 done now, Q8 carded
  as F130 for Sprint 15, Q9's three gaps added to F128. Q1: INTAKE 58
  rule, settlement and review text edited by hand, never by pattern
- **feat**: Q2: every apply lists each field it changed on a stored
  assertion that no review item names ("undecided" lines and a count;
  `decided_fields`). Q4: the dry run names every refusal at once
  (`assertions` and `verify` collect them). Q5:
  `scripts/sprint13_g_reading.py` renamed `scripts/full_read_apply.py`,
  its test file `tests/test_full_read_apply.py`; history keeps the old
  name. Q6: the two live-store apply tests share one store copy and one
  apply. Each new test proven red by injection
- **feat**: Q3: `scripts/f117_review.py finalize` refuses a group
  already applied on the live store, and `--store <path>` names a
  pre-apply copy to read instead (proven red by injection; it refuses
  g095 on the live store)
- **fix**: Q7: `store.grading.low_grade` drops a why's own trailing
  period, so a reason never reads ".. NOT upgraded";
  `scripts/sprint14_q7_doubled_period.py` fixes the 900 stored reasons
  with a format-only note (`FORMAT_ONLY_MARK`), which
  `store.ingest.last_change` skips so a full read keeps its ownership
  of a record. INTAKE section 59
- **docs**: Sprint 14 Phase 7.7 (2026-10-31):
  `docs/sprints/SPRINT_14_SUMMARY.md` with Actuals; master plan rolled
  (Past Sprint Summary row, Last Completed Sprint); `CHECKLIST-Phase2-pre.md`
  reconciled for Sprint 14, and Sprints 12 and 13 back-filled: neither
  had been reconciled at its Phase 7, and no Phase 1.2 sweep caught it
- **fix**: the review of 7b2179f (2026-10-31): the Q7 note had moved
  `updated` on 365 full-read records, so the sync guard would have
  refused a corrected sign-off on its review day; the guard now reads the
  day of the last real change when the last note is format-only. The Q7
  pattern matches exactly two periods (an ellipsis is left alone);
  `decided_fields` names every synced column for a changed verdict;
  `f117_review.applied` looks for new assertions under their `id_fix` id
  and skips dropped ones. INTAKE 59 correction; no store write
- **test**: the review of 80fcbb9 (2026-10-31, no defect found): the
  guard test also reads the date branch while the format note is last;
  INTAKE 59 says which bases refuse a why of only "."
- **docs**: Copilot review of PR #140 (2026-10-31): the retrospective's
  Development Team answer that named the applier's Sprint 13 file now
  carries a dated note of the Q5 rename
- **chore**: Sprint 14 Phase 7.7 complete (2026-10-31): PR #140 ready,
  CI green, the Copilot thread resolved; the merge is the team lead's

### 2026-10-24 to 2026-10-28 (Sprint 13, PR #131, merged to develop 2026-10-29 and to main via PR #139 the same day; tagged sprint-13)

- **chore**: Sprint 13 opened (2026-10-24). The team lead merged PR #122
  into develop (0c554bb) and PR #130 to main (a3ad99a); `sprint-12`
  tagged on a3ad99a; branch `feature/20261024_Sprint_13` cut from the
  Sprint 12 branch (6.6 carry-forward). Phase 1.1 reconciliation: every
  day with commits since 2026-10-23 has entries; one commit lacked its
  own, added below under Sprint 12 (18e9f43)
- **docs**: Backlog refinement 2026-10-25 (Sprint 13 Phase 1.2 to 1.4):
  Sprint 12's shipped cards pruned by hand (F100 to F106); F107 carded
  from the retrospective's Category 13 (the ".;" joins, the LOW proved
  results' reason); F108 carded from Phase 2's Sprint 28 work at 9993ab6
  (F162 and corrections to results F102 entered); snapshots refreshed on
  F95, F98, F57 and F51. Phase 1.3: 0 re-checks due; schema unchanged;
  ADR-0005 A11 the only ADR change
- **docs**: Sprint 13 scope selected (team lead, 2026-10-25): F107, F98,
  F95, F108, F39 and F57 at 800 records; released copies F109 (F95), F110
  (F98), F111 (F39) and F112 (F57); F90 put on HOLD. Plan drafted
  (`docs/sprints/SPRINT_13_PLAN.md`); pre-flight: 806 readable `qml`
  records remain, so Q1 asks 800 or all 806. Approved as amended
  (2026-10-25): Q1 = 1 (all 806). Issues #132 to #137; draft PR #131
- **fix**: F107 (Sprint 13 Task A, 2026-10-25): the ".;" join before
  "Local copy" corrected in 16 paper records' evidence
  (`scripts/sprint13_f107_joins.py`); two source-printed ".;" kept. Five
  theoretical results kept LOW (the card said 3; the reading script's
  notes name 5) now store their own reason instead of "an empirical
  result", through `sprint12_reading.py`'s `THEORY_LOW` table so its live
  test still holds; grades unchanged. INTAKE_WORKFLOW.md section 48;
  `tests/test_sprint13_f107.py` (injections run) (Issue #132)
- **fix**: the fresh-eyes review of 6c6f0ac (2026-10-25): the join pattern
  missed a join after a capital, "%" or a quote mark, and its comment
  credited the wrong part for keeping "Inc."; widened (no new join in the
  store), and the live guard now reads every text column of the paper and
  assertion tables, not only `paper_fields.evidence` (both injections run).
  Its Important finding (more theoretical results kept LOW with "an
  empirical result") goes to Task F's I2, as the plan's premise (b) says
- **process**: F111 (Sprint 13 Task B, 2026-10-25): the F39 release.
  Anthropic's models and pricing pages read 2026-10-25: every tier's id,
  price, context, maximum output and retirement date unchanged; no new
  model holds a role. Sprint 11's and Sprint 12's outcomes logged (Sprint
  12 held no F39 release, so Sprint 11's row was missing). One rule added
  with its evidence: a reader's certainty suggestion is never applied.
  `test_a_reader_grade_suggestion_is_never_applied_regression` (two
  injections run) (Issue #133)
- **feat**: F112's I2 (Sprint 13 Task F, 2026-10-25): every LOW names its
  reason through `store.grading.low_grade` (measured result, theoretical
  result, field statement, authors' claim, cited claim; the texts the
  store already holds), and `store/write_path.py` refuses a reading script
  that writes without it. `theory_words` guards every "measured result"
  that names a theorem, proof, derivation or analytic count. Section 48's
  premise was wrong (the 6c6f0ac review found 8 more): 29 more Sprint 12
  theoretical results now store their reason with a cause, from a
  classifier's 33 candidates each checked by the coordinator; Task A's 5
  reworded (the old prefix fit 2 of them); grades unchanged. Sprints 9 to
  11: 27 candidates counted and carded on F57, not corrected.
  INTAKE_WORKFLOW.md section 49; four injections run (Issue #137)
- **fix**: the fresh-eyes review of dd620c7 (2026-10-25): 4 more Sprint 12
  theoretical results (each confirmed in its PDF), 2 moved back
  (mohseni's estimate is measured; pqc-gradient-cost-linear is a field
  statement), each with its own dated note; `theory_words` widened (27 of
  the 36 found, was 15 of 34; "bound" no longer matches "boundary") and
  30 more measured results named in `MEASURED_DESPITE`; the write-path
  rule refuses a literal "low" and takes the vendor LOW through
  `low_grade`; section 49's 499 is 498 exact. Injections run (Issue #137)
- **process**: F109 (Sprint 13 Task C, 2026-10-25): `Papers\` holds 180
  PDFs, and every one is named by a record; nothing to enter (Issue #134)
- **process**: F110 (Sprint 13 Task D, 2026-10-25): Roadmap-to-QML's
  latest commit is still a239747648 (2026-10-20), read by one GitHub REST
  call; no new paper (Issue #135)
- **feat**: F108 (Sprint 13 Task E, 2026-10-25): Phase 2 read at 9cbe5ba
  (PR #46 merged since planning; no `docs/phase2/` change from the plan's
  9993ab6). F162 entered under `hsbc-2026` (the plan said `ml`; section
  43's rule) with 2 SIM assertions, no relation linked (ADR-0004 A8 (b));
  three F102 values corrected (F110's unreadable solve, F114's
  calibration and range, F111's range) and the other 9 confirmed by name
  (`scripts/sprint13_f108_phase2.py`, INTAKE_WORKFLOW.md section 50,
  `tests/test_sprint13_f108.py`, two injections run) (Issue #136)
- **fix**: the fresh-eyes review of 88bd065 (2026-10-25): the three
  corrected values' paper records still pointed at 10086da's blob;
  repointed at 9cbe5ba with the earlier read kept in the evidence. F162's
  value now carries the energy_steel HGB case, the 46 to 58 frauds per
  seed, the inferred telecom-only entry and the label limit, and says what
  "overall" covers. Section 50's context line corrected. Injections run
  (Issue #136)
- **feat**: F112 (Sprint 13 Task F, 2026-10-25): the slice (806 `qml`
  records), the paced fetch (28 saved, 5 arXiv 404s, 6 with no free
  copy), and one read ledger: 795 records in 100 groups, 11 in `no_copy`
  each with its own reason. The reader prompt gains `result_type`. New
  `tests/test_sprint13_read_ledger.py`, 2 injections (Issue #137)
- **fix**: the fresh-eyes review of e621771 (2026-10-25): the slice is
  every `qml` record with an arXiv id or a DOI, not "every readable" one;
  the 166 GitHub repositories and 11 local-file records left out are
  carded on F57. Section 51's citation buckets corrected (362 arXiv DOIs
  and 2 journal DOIs by their own identifier, 53 by a journal version). A
  fetch failure no longer says "paced" (the log's FAILED covers both
  fetch paths). farrelly-2019's unstamped file checked by hand (Issue #137)
- **feat**: F112 half 1 (Sprint 13 Task F, cec6020, 2026-10-25): g01 to
  g50 read and applied, 1360 assertions from 400 records; the
  hand-download list puts uncounted records after every counted one in
  their group. This entry was missing from cec6020 and is added with the
  review below (Issue #137)
- **fix**: the fresh-eyes review of cec6020 (2026-10-25): 26 of half 1's
  HIGH are LOW (18 theorems quoted without statement and conditions, 8
  "stated limits" that are measured results); 7 limits lose a measured
  clause; 12 values with an exponent the text layer printed flat say it
  in words (new guard); 5 HIGH values given their passage; a "full" read
  whose note says the whole paper is entered as the whole source; the
  write-path LOW rule requires a call of `low_grade` again (the import
  alone had passed), and section 49 no longer claims the concatenation
  case is closed. Section 51's three false claims retracted. Injections
  run (Issue #137)
- **feat**: F112 half 2 (Sprint 13 Task F, 2026-10-25): g51 to g100 read
  and applied, 1350 assertions from 395 records (462 HIGH, 888 LOW); g82's
  duplicate id renamed; one assertion dropped with its reason.
  `tests/test_sprint13_reading.py` lands, with the garbled-figure guard
  and the vendor LOW case, each proven red by injection (Issue #137)
- **fix**: the fresh-eyes review of f782e53 (2026-10-25): 14 more of half
  1's HIGH are LOW (8 theorems quoted only from an abstract, 5 measured
  "limits", 1 cited definition) and 7 of g51 to g69's; 7 limits lose a
  measured clause; four flat exponents said in words; the garble guard no
  longer flags "(H2)" or "(B0)"; two write-path bypasses recorded, not
  closed; "7 of the 113" corrected to 8 (Issue #137)
- **fix**: the fresh-eyes review of ce2412e (2026-10-25): half 2 re-applied
  at 460 HIGH and 890 LOW (3 out of HIGH, 1 field statement found to be the
  paper's own stated limit and moved in); cited clauses and a show-result
  left out of 4 HIGH values; a quote that had lost the negation before it
  restored; 6 values trimmed to their quotes; "1.46N" said in words and
  section 51's "no flat-printed figure" retracted; 12 HIGH locations named
  by section; two test checks that could not fail removed, and three
  guards added (a decimal before N, no id both HIGH and named LOW, no
  stale store row), each proven red; a third write-path bypass recorded
  (Issue #137)
- **fix**: the fresh-eyes review of 6cfc137 (2026-10-25): "6 values
  trimmed" above was 5 trimmed and 1 restored; `qnpg-outer-loop` is a
  statement about the field, not an authors' claim; a symbol said lost
  is not; 5 reader anchors corrected in the stored provenance (new
  `ANCHOR_FIX`), 3 HIGH locations made exact, 2 values worded to their
  quotes. Half 2 re-applied; grades unchanged (Issue #137)
- **fix**: the fresh-eyes review of 7ea56e7 (2026-10-25): one of those 5
  anchors was a wrong correction of a right one (`ma-not-tested-on-hardware`
  is III.A and IV, Conclusion); "3 HIGH locations" above was 4; qnpg keeps
  "likely". Half 2 re-applied; grades unchanged (Issue #137)
- **fix**: Manual Validation Q2 (team lead, 2026-10-25: "q2 fix now
  before reading any more papers"): `store/write_path.py` reads each
  script's parsed code instead of its text. The three known bypasses are
  closed: "low_grade(" in a string or a docstring is not a call, a
  `low_grade` or `high_grades` the script defines or assigns for itself
  is refused, and a "#" in a string hides nothing. A script that does not
  parse is refused. Every script in `scripts/` gets the same verdict as
  before. Six new cases, proven red against the old rule (Issue #137)
- **fix**: the fresh-eyes review of ed53933 (2026-10-25): a name spelled
  as a whole string (`getattr(d, 'insert_assertion')`, `'Verified'`)
  escaped the parse, though the text rule had refused it; it counts as
  the name again. `sq.require_edit_basis(...)` through a module was
  wrongly refused; it counts as the call. Corrected: "Six new cases,
  proven red" above is five; the sixth, a call through
  `import store.grading as g`, passes both rules by design. Four more
  cases, each proven red against ed53933 (Issue #137)
- **fix**: the fresh-eyes review of b0b41a3 and 6173bad (2026-10-25): a
  dotted name or a call inside a string
  (`eval('store.ingest.insert_assertion')`, `exec('insert_assertion(...)')`)
  still passed; every identifier inside a string now counts. A changed
  manifest did not run `test_intake`, which reads every manifest; it does
  now. Each proven red. Every script keeps its verdict (Issue #137)
- **fix**: the fresh-eyes review of b6cdcd0 (2026-10-25): bytes literals
  and a grade quoted inside a string (`exec("g = 'high'")`, `b'high'`)
  still passed the write-path rule though the 1980406 text rule refused
  them; both count now. `--changed` now also runs the tests that read
  every file of a kind: the read-ledger tests and the reader-prompt guard
  on a manifest change, the four script scanners on a script change, and
  the guard-discipline test on a test change. Each proven red; every
  script keeps its verdict (Issue #137)
- **fix**: the fresh-eyes review of 745c6e6 and a3b8074 (2026-10-25):
  Task G's slice is 1,997, not 1,991 (a whole-paper note with an
  exception, and three e-mail reads with a part "not read", no longer
  count as full); F113's card had an earlier run's counts and now
  matches. The reader's check refuses a `full` read naming a part not
  read, a changed verdict with no value, a HIGH suggestion with no
  location or on a measured result, and a file not the brief's. The
  ledger only appends (66 fetched records and 6 more joined as g295 to
  g309). The budget guard catches "at most 5 assertions", "up to 4
  claims", "read the abstract" and minutes per paper; the write-path
  rule reads an edit table defined inside a string. Each proven red
  (Issue #138)
- **process**: No reading budget (team lead, 2026-10-25, at Manual
  Validation: "remove the budget ... ensure that all future paper reads
  have no budget"). F57's card drops its per-record rate; the new reader
  prompt (`manifests/sprint13_g_reads/READER_PROMPT.md`) asks for every
  page, appendix and proof, sets no cap on assertions, and gives each
  reader the record's stored assertions to confirm or correct. CLAUDE.md
  carries the rule; `tests/test_reader_prompts.py` fails on a prompt from
  Task G on that names a part-read or a cap, proven red with Task F's
  prompt in its place (Issue #138)
- **feat**: Sprint 13 Task G (F113, issue #138, added at Manual
  Validation): the slice of every paper not read in full (1,991 of 2,335,
  snapshot as of 2026-10-25; a reader's "full" that listed parts does not
  count), its downloads (Sprint 10's rules: 210 free copies planned, 138
  with none), the ledger builder and the reader's own check. INTAKE
  sections 52 (Q4's common names) and 53 (Task G) written before their
  applies (Issue #138)
- **fix**: Manual Validation Q3 (team lead, 2026-10-25: "q3 do now"):
  `scripts/run_suite.py --changed` runs `test_us_english` on any
  document change, as it already ran the em dash guard. 6cfc137's
  British spelling passed `--changed` and turned CI red. A test on this
  repository's own selection fails if either guard leaves the list,
  proven by injection (Issue #137)
- **fix**: Manual Validation Q4 (team lead, 2026-10-25: "keep how the
  paper does them and then put in parenthasses the more common name").
  `store/common_names.py` adds "(R squared)" after a paper's "R2" and
  "(D squared sampling)" after "D2-sampling"; `store.ingest` applies it
  on every insert and sync. The four owning reading scripts re-applied
  (with verified backups) changed exactly 18 values, 17 with R2 and 1
  with D2-sampling (snapshot as of 2026-10-25); a second apply wrote
  nothing. `tests/test_common_names.py` named all 18 against the
  pre-apply backup and passes on the live store. The three reading
  scripts' store-match tests compare the value as ingest stores it
  (Issue #138)
- **fix**: the hand-download list failed with `KeyError:
  'cited_by_count'` once Task G's slice (a3b8074) joined the
  `*_slice.json` manifests, since that slice records no OpenAlex count. A
  slice row with no count is now read past, as an uncounted one was; a
  test with no store, proven red on the old script, holds it (Issue #138)
- **chore**: Task G (F113) after its download run (snapshot as of
  2026-10-25): 165 copies saved and 45 failed, none retried. The slice,
  re-run with the download log, holds 1,997 records: 1,640 with a local
  copy, 183 without one, 174 GitHub repositories. The 183 are listed
  with their reason in `manifests/sprint13_g_no_copy.json` for the
  hand-download list. The ledger appended 99 records as groups g310 to
  g329. The reader prompt now says that a plot whose caption was read is
  not `not_read`, and that a text layer holding the paper twice is read
  from its first copy. `tests/test_backlog_cards.py` failed on F57's and
  F113's headers, which carry no estimate since the budget was removed; a
  reading card may now say "(no estimate: as long as the reads take ...)"
  in exactly those words, and every other card still states its minutes
  (Issue #138)
- **fix**: the fresh-eyes review of the Q4 fix (ce95e82) found that a
  bare "R2" is also a label in the active consumer's documents ("R2:
  exact weight below t", "research R2"), and the rule glossed every one
  as R squared. A bare R2 now gains the name only beside a number, a
  comparison or a statistic word, and never next to a label marker.
  "R-squared", "R^2", "R²" and "R2-score" now gain it too; one stored
  value ("R-squared value of 0.9959") was updated through its owner
  apply, and a second apply wrote nothing. The 18 values glossed before
  are unchanged under the new rule (Issue #138)
- **fix**: the fresh-eyes review of that fix (8c869cc) found that its
  40-character window still glossed labels with a number or a statistic
  word anywhere near ("Cloudflare R2 storage costs below $0.01", "In R2,
  accuracy was 0.9", "R2 = R1 + 0.5"), matched "train" inside
  "constraint", missed "R2: 0.93", "r-squared", "R2_score", "R2-scores",
  "coefficient of determination" and "D² sampling", and put the name
  inside a token ("R^2 (R squared)_adj"). A bare R2, R^2 or R² now gains
  the name only when a number follows through connecting words, a
  statistic noun follows, or a statistic word comes before it; the name
  goes after the whole token. Three of the four label tests had stayed
  green with both label guards removed; each guarded case now removes its
  own guard in the test and must turn glossed. No stored value changes
  (Issue #138)
- **fix**: the fresh-eyes review of 44e2512 (2026-10-26) found labels and
  the real plane still glossed ("rules R2", "Tables S1 and R2", "R1/R2",
  "in R² 3 points", "R2 from 2020"), common phrasings missed ("R2
  (0.93)", "R2 = .93", "the R2 of the model was 0.9", "R2 and RMSE of 0.9
  and 0.1", "R2 improved"), a second gloss after "coefficient of
  determination (R squared)", and a LaTeX token or a code call split. Each
  has a test; each guarded case removes its own guard and must turn
  glossed. Sprint 12 Task G's apply that morning glossed one more stored
  value ("coefficients of determination", plural) (Issue #138)
- **chore**: Task G (F113, 01338ff, 2026-10-25): the reader prompt forbids
  hook override tokens, after the g007 reader used one in its scratch
  folder; `tests/test_reader_prompts.py` fails on a prompt without the
  rule (Issue #138)
- **fix**: Task G (F113, 0765e9a and its review, 2026-10-26): an older
  reading script's sync no longer puts a partial read's value back over a
  row re-read in full. The first guard refused every later correction
  too; it now refuses only a sync dated on or before the full read's
  (`store.ingest.sync_assertion`), proven red by removing the date test
  (Issue #138)
- **feat**: Task G (F113, 2026-10-26): `scripts/sprint13_g_reading.py`
  enters the reviewed groups from `manifests/sprint13_g_reviews/` (one
  coordinator review per group, g001 to g042) and their reader
  files; `ID_FIX` stores a new assertion under another id where the
  reader's suggestion is already another source's. Dry run only; nothing
  applied yet (Issue #138)
- **feat**: Task G (F113, 2026-10-26, after readers g016 to g019 stopped
  at a usage limit): a reader saves its progress as it goes and starts
  from it. The reader prompt's "Progress and restart" section saves a
  partial file about every 10 pages and a done file per finished paper;
  `scripts/sprint13_g_check.py --partial` checks a part-finished group;
  `scripts/sprint13_g_status.py` computes each group's state from its
  files. `tests/test_reader_prompts.py` fails on a prompt without the
  section, and `tests/test_sprint13_g_restart.py` on the check and the
  status, each proven red by injection (Issue #138)
- **fix**: the fresh-eyes review of 6d8dec7 (2026-10-26): Task G's own
  sync skipped the date guard, so its next apply would have put a review's
  value back over a later correction; a full-read sync dated before the
  row's last change is now refused. An ordinal suffix ("2nd") matched the
  start of the next word, so "R2 of 0.93 than ..." went unglossed. The
  apply script refuses an edit under an id that `ID_FIX` moves, and refuses
  a graded confirmed row it does not rewrite unless the store already holds
  that grade. Each has a test proven red by injection (Issue #138)
- **fix**: the fresh-eyes review of 9c79048 (2026-10-26): `record()` read
  an edit under the reader's id while `verify()` and the guard used the
  stored id, so an edit named as the guard advised was dropped; edits are
  now read under the stored id. The same-day sync refusal looked for the
  full read anywhere in a row's history, so a second correction on one day
  was refused; it now asks whether the last change was the full read. Each
  has a test proven red by injection (Issue #138)
- **docs**: Task G paused (2026-10-26, team lead: "pause after the 5
  current agents complete and backlog the remaining for the next
  sprint"). Sprint 13 finishes groups g001 to g042 and applies them;
  groups g043 to g329 (snapshot as of 2026-10-26: 1,430 records) are
  registered as F114 in `docs/ALL_SPRINTS_MASTER_PLAN.md`, and F113's
  card records the pause (Issue #138)
- **fix**: the fresh-eyes review of 57107f1 (2026-10-26): `record()` still
  read ANCHOR_FIX and CONTEXT_FIX under the reader's id while value and
  quote edits used the stored id, and the moved-id guard did not cover
  them, so an anchor or context fix named under the stored id was dropped
  silently. Both are now read under the stored id and guarded; the tests
  were proven red by injection (Issue #138)
- **feat**: F114 cloud readers (2026-10-26, team lead: "cloud runs only one
  paper at a time, sends the 'brief' (it needs to be essentially the whole
  paper) ... do one pilot first, then adjust as needed and continue sending
  until completed or we run out of weekly tokens"). `scripts/f114_cloud.py`
  writes one paper's extracted text and brief into the tracked placeholders
  in `manifests/f114_cloud/inbox/`, starts a cloud session from a bundle of
  the working tree (`CCR_FORCE_BUNDLE=1`), and restores the placeholders,
  so the text never enters a commit (ADR-0005 section 3); the session pushes
  its result to `cloud/f114/<record>` and `fetch` saves it outside the
  repository without merging. `manifests/f114_cloud/READER_PROMPT.md` is
  Task G's prompt for one paper; `scripts/sprint13_g_check.py --text` checks
  quotes against the given text. Tests proven red by injection
  (`tests/test_f114_cloud.py`; the restart-phrase check in
  `tests/test_reader_prompts.py` now compares "\" and "/" alike) (Issue #138)
- **fix**: F114 after the pilot and its review (2026-10-26). The pilot read
  wierichs-2022-general-parameter-shift-rules-quantum in full, and its result
  passed the check against the PDF. Fixes: the session adds the GitHub
  remote before pushing (a bundled session has none); `fetch` reads git as
  UTF-8 (the Windows code page garbled 12 quotes); the paper goes as raw
  text with its page breaks, not one folded line holding it twice; the
  inbox is restored from HEAD, index included, and the session commits only
  its folder by pathspec and checks it was given RECORD; `fetch` checks
  every pushed commit, not only the final tree; a session silent for 3
  hours is launched again (3 attempts at most), and a refused or failed
  paper is set aside instead of stopping the run (Issue #138)
- **fix**: F114 sessions start from GitHub, not from an uploaded bundle
  (2026-10-26, team lead: "q2 1"). A bundled session is not linked to the
  repository, so every push was refused until the team lead linked it by
  hand. The launcher now reads the new session's id from its console
  (`scripts/f114_launch.ps1`) and sends the instructions, brief and paper
  text as one follow-up message; the session saves them outside the
  repository with `scripts/f114_unpack.py`. Tests proven red by injection
  (Issue #138)
- **fix**: F114 launcher fixes found while launching (2026-10-26):
  `claude --cloud` needs an interactive terminal, so it runs in its own
  console window, with its stderr logged (08d2f07, b9bfa1f, efd77d7); the
  launch script reads the console buffer with `GetValue` (cca6628);
  `fetch` reads results with `git cat-file`, since `git show` refused a
  long record id on Windows (fa09c8e); each cloud session is named after
  its paper (6eafb0d) (Issue #138)
- **docs**: F115 (text from page images) and F116 (read figures) carded;
  udaru-2025-qml-credit-risk kept unread (2026-10-27, team lead: "mark
  udaru-2025-qml-credit-risk as unread") (00da300)
- **fix**: the F114 loop never counts a paper marked unread as in flight
  (2026-10-27, 0d7597c)
- **docs**: F114 cloud reads stopped at $0 credit (2026-10-27, team lead:
  "Can stop sending more papers and backlog the remainder for next
  sprint"): 302 results fetched, 3 papers kept unread, 1,126 records
  backlogged (snapshot as of 2026-10-27) (d5fe761). F117 (review the 302
  results, split by model tier) and F118 (what the store says for the
  fraud challenge) carded (7aa184c)
- **chore**: Task G reviews finished through g042 (2026-10-27, cf62cff)
- **fix**: the sync writes every changed assertion field in one statement
  (2026-10-27): the trial apply broke the CHECK that an absence names its
  search scope, because the claim type was written before the scope; test
  proven red. INTAKE_WORKFLOW.md section 53 records the g001 to g042 apply
  (eb3941a) (Issue #138)
- **fix**: Task G's apply rewrote the detail of 114 Task F read rows from
  the same day (2026-10-28, found by the full suite). Both scripts now
  match their own read rows by wording; the live store was repaired by
  re-running Task F's apply, and a diff against the pre-apply backup shows
  no row missing (5e10948). The read writer is tested on a store that
  holds Task F's rows (915f9e4). Tests proven red by injection
- **chore**: Sprint 13 Phase 5.3 Manual Validation resumed after Task G
  (2026-10-28, ee6f8ad)
- **docs**: F119 carded at Priority 10 (2026-10-28, team lead: "add the
  following text and paper to the paper repository and terget read for
  next sprint - highest priority"): Brighindi's PHI-OMEGA paper, posts,
  comment thread, images and code, first in Sprint 14 (Manual Validation
  Q9 = 1, Q10 = 1). F117 and F118 move to Priorities 20 and 22 (91b757b).
  The card names the author's two PHI-OMEGA repositories (d5a3f94)
- **fix**: Task G's whole-paper reads stored as `full` (208) and the two
  with named exceptions as `partial` (2026-10-28, Manual Validation
  Q7 = 2); the rows first written as `subagent` are moved, not
  duplicated; test proven red (2bab87b). INTAKE names the 8 full reads
  the slice counts only through their reader files (d5a3f94)
- **docs**: Manual Validation Q11 = 1, Q12 = 1, Q13 = 2 (2026-10-28):
  F119 reads only the parts of the 608-file archive that bear on the
  paper's claims; the references split in two (PHI-OMEGA / M-OMNIA, and
  the MB-X.01 structural-coherence code); the 302 cloud results are
  reviewed in Sprint 14 after F119 (F117), and Sprint 13 closes now
- **docs**: Sprint 13 retrospective (2026-10-28): Claude's Development
  Team draft (db8aeb7); the team lead's feedback recorded verbatim and
  four improvements proposed (af2c2ca). Team lead: "q1 1, q2 1, q3 3
  q4 1" (I1, I2, I4 now; I3 skipped)
- **process**: Sprint 13 retrospective I1, I2 and I4 (2026-10-28). I1:
  Task G's apply is rolled back when it would rewrite a read row, unless
  `--update-reads` names the rewrite as intended (F117 applies through
  this script). I2: every `UPDATE paper_reads` names the row's stored
  detail; the seven older scripts that matched by reader, day and extent
  alone are narrowed to one row, and `tests/test_read_row_updates.py`
  names any that does not (including "+" joins, f-strings and DELETE).
  I4: `test_changelog_currency` names each commit from 71705d8 on that
  neither changes CHANGELOG.md nor is named in it by its short hash. Each
  test proven red by injection (c978e50). The fresh-eyes review of
  c978e50 found nothing Critical; acted on: "update readout-..." is not a
  read row, the commit marker cannot occur in a subject, the hash length
  is fixed at 7, the scan reads joined statements. Its Important finding
  is recorded, not fixed: the older scripts still compare whichever row
  shares the key, so they must not re-run on a day another script wrote
  (none does today) (8a06bf5)
- **fix**: Copilot's review of PR #131 (2026-10-28): `low_grade("vendor
  claim", why)` was refused as "not one of" the LOW reasons; it now says
  a vendor claim takes no why (latent: no caller passes one). Test proven
  red by injection (9e7d9fb)
- **docs**: Sprint 13 Phase 7.7 (2026-10-28): `SPRINT_13_SUMMARY.md` with
  its Actuals; master plan rolled (Past Sprint Summary row 13, Last
  Completed Sprint); `CHECKLIST-Phase2-pre.md` names no sprint, so nothing
  to reconcile. Copilot's one finding fixed and its thread resolved

### 2026-10-23 to 2026-10-24 (Sprint 12, PR #122, merged to develop 2026-10-24 and to main via PR #130 the same day; tagged sprint-12)

- **process**: Sprint 12 retrospective, 2026-10-24 (team lead: "q1 1 q2
  1 q3 1"). I1: `run_suite.py` records the store's stamp at each PASSED
  run that covered the store's tests, and `--changed` adds every
  `live_store` test file when the store changed since. I3: `intake.make_id`
  slugs a family that drops to nothing with its stop words kept (the
  first author "An" gave an id starting with "-"); every earlier id is
  unchanged, a non-alphanumeric start is refused, and the bulk manifest
  pins the known id. I2 carded on F57 from Sprint 13's release. Both
  guards proven by injection (PR #122)
- **fix**: the review of 7b65d12: a `--changed` run with a pytest filter
  (`-k`, `-m`) no longer records the store as checked, since the filter
  may deselect the store's tests; proven by injection (PR #122)
- **docs**: Sprint 12 Phase 5.3 (18e9f43, 2026-10-23): status to Manual
  Validation once CI was green on #122 (PR #122)
- **docs**: Sprint 12 retrospective, summary and Development Team draft,
  2026-10-24; Copilot review requested on #122 (PR #122)
- **fix**: F105 and F104 (Sprint 12 Tasks G and F) third apply,
  2026-10-23: the fresh-eyes review of 5744e2d. Four cuts that lost a
  condition restored from their source sentences (one value had said a
  paper ran only on a simulator; it ran on hardware). 18 HIGH grades
  moved to LOW: 14 statements about the field, 4 conclusions from the
  paper's own measurements; a field statement now stores its own
  reason. 11 values trimmed or re-quoted. 42 records updated; a fourth
  apply writes nothing. HIGH 559. A CI test now checks every replaced
  value's signs against its quotes. The 5744e2d entry's "2 quotes
  corrected" were 2 quotes dropped (INTAKE_WORKFLOW.md section 47)
  (Issue #129 / PR #122)
- **feat**: F105 and F104 (Sprint 12 Tasks G and F, the reads,
  2026-10-23): all 53 ledger groups read by first-pass readers and
  read again by the coordinator (`scripts/sprint12_reading.py`): 110
  values replaced, 18 given their source sentence, 2 quotes corrected,
  7 assertions dropped with their reasons. HIGH through `high_grades`
  only, each of 577 ids with its basis. Entered: 74 assertions from
  Task F's 20 records and 1,283 from Task G's 393 (9 bear on no
  context); 404 records to `read`; 8 with no copy keep their tier with
  the reason. A second apply writes nothing.
  `tests/test_sprint12_reading.py`, each guard proven to fail by
  injection (INTAKE_WORKFLOW.md section 47) (Issue #129 / PR #122)
- **feat**: F105 (Sprint 12 Task G, second part, 2026-10-23): the slice
  (`scripts/sprint12_f105_slice.py`, 400 `qml` records by OpenAlex
  citations), the downloads wrapper with `--session-count` and a
  heartbeat (4 saved, 2 withdrawn on arXiv), and the one read ledger
  (`scripts/sprint12_read_ledger.py`: 53 groups, 413 records; Task E's
  pages as read by the coordinator; `tests/test_sprint12_read_ledger.py`).
  The Sprint 12 reader prompt asks a "high" suggestion for its basis
  (INTAKE_WORKFLOW.md section 47) (Issue #129 / PR #122)
- **fix**: F104 (Sprint 12 Task F) second apply, 2026-10-23: the
  fresh-eyes review of f99139e. The 1,397 held papers the list links
  get a `found_via` route naming it; the DOI form of an arXiv id counts
  as held; DOIs match whole, not as substrings; a legacy Nature id is no
  longer turned into a wrong DOI; 25 links carried, not 27. The tests
  check every listed id is held and routed, and no longer pass on an
  empty list (INTAKE_WORKFLOW.md section 46) (Issue #128 / PR #122)
- **fix**: F103 (Sprint 12 Task E) fourth apply, 2026-10-23: the
  fresh-eyes review of 77beaa0. Section 44's third-apply bullet
  corrected (the pages' order is open; the PyZX error was Part 2's);
  Part 1's value scoped to "the first rows" and the two depth-lowering
  runs named as the page names them; the top-two counts' reason states
  why it is not upgraded (Issue #127 / PR #122)
- **feat**: F104 (Sprint 12 Task F, F98's first release, 2026-10-23):
  Roadmap-to-QML read at commit a239747648; 1,418 arXiv ids listed, 21
  new entered at `seen` under `qml` through the door, 20 with a free
  copy (2303.16318's PDF returned 404); one malformed link (2108.0131,
  held as 2108.01311); 27 other links, 9 with a DOI, carried to the next
  release in `manifests/sprint12_f104_roadmap.json`
  (INTAKE_WORKFLOW.md section 46) (Issue #128 / PR #122)
- **fix**: F103 (Sprint 12 Task E) third apply, 2026-10-23: the
  fresh-eyes review of c80c195. Grades follow the store's precedent (the
  author's own blog measurements LOW; depth 95 MODERATE, upgraded for the
  organiser's scoring; placings HIGH); PyZX recorded as lengthening the
  circuit; "top five" no longer called earlier than the ranking; the
  organiser's top-two CX counts split into their own assertion; the
  repository recorded as a white paper with no code. The script syncs a
  held record's disposition; the test checks each disposition, citation
  and the repository record (INTAKE_WORKFLOW.md section 44)
  (Issue #127 / PR #122)
- **feat**: Sprint 11 retrospective I3 (Sprint 12 Task G, first part,
  2026-10-23): `store/grading.py` grades HIGH only with a named basis
  (setup, scope, definition, proved result, stated limit) and its reason,
  and `store/write_path.py` refuses, before the backup, a new reading
  script that writes assertions without it or with a literal "high" of
  its own. Intake section 45. `tests/test_verified_writes.py` (injections
  run) (Issue #129)
- **feat**: F103 (Sprint 12 Task E, 2026-10-23): PoJen Wang's two posts
  on the Classiq Quantum Circuit Challenge (Part 1, a field guide to
  compilers; Part 2, his depth-95, 272-CNOT phase oracle) and Classiq's
  wrap-up, entered as reference records at `read` from saved copies, with
  5 assertions; the repository the team lead named
  (wangy8205165/Quantum-NeuralNetwork-WhitePaper) entered and linked to
  no paper. The two parts are stated as a series in their citations and
  dispositions, not linked: no link type fits (a change from the plan).
  Store as of 2026-10-23: 2,313 papers, 1,612 assertions. A second apply
  added the applicability the first left out, found by the full suite
  before the commit. Intake section 44;
  `scripts/sprint12_f103_intake.py`; `tests/test_sprint12_f103.py`
  (injections run) (Issue #127)
- **feat**: F102 second apply (Sprint 12 Task C, 2026-10-23), from the
  fresh-eyes review of 5bcafe0. F111's result, which the first apply
  missed (Phase 2's own validation file still said "No result yet"), is
  entered as a seventh reference record with 3 SIM assertions: the
  CVQBoost-KNN lane under Loke et al.'s protocol is 0.051 below the
  published 0.8108, the stable HGB beats it under both protocols, and the
  protocol moves HGB but not measurably the lane. Five values corrected
  to carry what their source says (F110, F153 twice, F154, F114), and
  F151's measured iteration count moved out of the inferred part. The
  test checks certainty, reasons and context, and the quote count is
  exact (99). Intake section 43 (Issue #125)
- **fix**: F100 follow-up (Sprint 12 Task B, 2026-10-23), from the
  fresh-eyes review of fdedff9. A test's fake pdftotext version stayed in
  the version reader's cache and keyed every later quote check in the
  run; the fakes now patch the reader, and a test proves a new version
  extracts again. The cache key holds pdftotext's options too, each
  writer gets its own temporary file, and the text is stored as bytes.
  `run_suite.py --changed` counted a deleted or renamed file as nothing,
  dropped quoted paths and test helpers, and said "SUITE SKIPPED" with
  exit 0 when nothing was picked; it now reads `git status -z
  --no-renames`, searches every changed name, follows a `store/` module
  into the scripts that import it, and runs the full suite for a shared
  file or an empty pick. A unit test for F97's `existing()`. Injections
  run (Issue #124)
- **fix**: F101 fourth and fifth applies (Sprint 12 Task A, 2026-10-23),
  from the fresh-eyes review of 6d2bed4. The Elor value now says
  balancing beat threshold tuning for both MLP and SVM (p.4, Table 3 on
  p.5); McDermott's value keeps "with respect to model-dependent
  parameters"; Liu's says "slightly", which the abstract's "real but
  small" supports, with the ECE figures; De Lorenzis's anchor is
  section 3. Kakavand's and De Lorenzis's evidence text corrected, and
  four ".;" joins this script wrote removed. Each sync now names what it
  changed, and four earlier syncs get a history note. Intake section 42
  (Issue #123)
- **feat**: F100 (Sprint 12 Task B, 2026-10-23): the full suite runs in
  199 s with a warm text cache (602 s cold), from 781 s; 1,202 tests
  passed in each timed run (snapshot 2026-10-23). The cause was
  `tests/conftest.py` clearing the PDF text cache before every unmarked
  test, so each quote check ran pdftotext again. `store/quotes.py` now
  keeps a disk cache under the store folder, keyed by the file's SHA-256,
  the layout mode and the pdftotext version, and a `READ_GUARD` hook
  takes the place of the cache clearing, so an unmarked test still cannot
  read a local file. The F97 second apply no longer calls the network for
  records already held (79 s to 0.04 s). `scripts/run_suite.py --changed`
  runs the tests for what changed. `tests/test_f100_text_cache.py`,
  `tests/test_run_suite_targeted.py` (injections run) (Issue #124)
- **feat**: F102 (Sprint 12 Task C, 2026-10-23): Phase 2's Sprint 28
  results entered by the inbound path. Six documents read at Phase 2
  commit 10086da through `git show` (F151, F152, F153, F110, F114, F154),
  one reference record each at `read` with its blob's SHA-256, and 9 SIM
  assertions, every quote checked with its value in the write path; no
  relation linked (ADR-0004 A8 (b)). Intake section 43;
  `scripts/sprint12_f102_phase2_sprint28.py`; `tests/test_sprint12_f102.py`
  (injections run) (Issue #125)
- **fix**: F101 follow-up (Sprint 12 Task A, 2026-10-23), from the
  fresh-eyes review of 5466953. 7 Sprint 5 contexts held a passage with
  no quote marks, which no check could read; each is re-quoted from its
  PDF, and 4 values the source did not fully support are corrected
  (Elor 2022, De Lorenzis 2026, Kakavand 2026, Liu 2026). The quote guard
  now also fails on a context with no parsed quote. Three free arXiv
  copies saved; every local copy's SHA-256 in `evidence` (F48's test found
  Lenat's missing). The Cyc copyright anchor is p.146; the preregistration
  is read at commit 7261e4e. `store.citations` also unescapes DataCite's
  venue, author names and Crossref's publisher. Intake section 42, third
  apply (injections run) (Issue #123)
- **docs**: F106 (Sprint 12 Task D, 2026-10-23): ADR-0005 amendment A11.
  A source link may rest on the team lead's recorded decision when no
  source states it; its evidence names who, the date, where it is
  recorded, and says the link rests on that decision. 1 such link of 170
  `code-of` links as of 2026-10-23 (the NVIDIA auto-ontology-eval
  repository, Sprint 11 Q1 = 2). No restatement of field 6 in
  `CLAUDE.md` or `docs/` needed a change. `tests/test_source_link_evidence.py`
  checks that every stored link has evidence and that a decision-backed
  one names all A11 asks; a source's own sentence cannot be told apart
  mechanically, so that stays an intake check (injections run) (Issue #126)
- **fix**: F101 (Sprint 12 Task A, 2026-10-23): HTML entities out of the
  store. `store.citations` now unescapes Crossref and DataCite titles,
  subtitles and venues; the 4 records that stored "&amp;" (Jeffery 2024,
  Dunjko 2018, Pande 2020, Yang 2023; 6 fields) corrected, ids kept.
  Every stored quote now parses: the Cyc quote cut at its inner
  `"split" (` and 3 Sprint 1 and 2 quotes with no anchor (found by
  running the stray-quote check over the whole store; section 41 had
  counted 2) re-quoted from their sources with anchors, values unchanged.
  Lenat and Marcus 2023's free arXiv copy saved and linked. Intake
  section 42; `scripts/sprint12_f101_corrections.py`;
  `tests/test_sprint12_f101.py` (injections run) (Issue #123)

- **chore**: Sprint 12 opened (2026-10-23). The team lead merged PR #113
  into develop (21e9550) and PR #121 to main (d83a623); `sprint-11`
  tagged on d83a623; branch `feature/20261023_Sprint_12` cut from the
  Sprint 11 branch (6.6 carry-forward). Phase 1.1 reconciliation: every
  day with commits since 2026-10-21 has entries; two commits lacked their
  own, added below under Sprint 11 (a87112a, 53cfe45)
- **docs**: Backlog refinement 2026-10-23 (Sprint 12 Phase 1.2 to 1.4):
  Sprint 11's shipped cards pruned by hand (F91 to F94, F96, F97); F101
  carded from the retrospective's Category 13 (Pande 2020's "&amp;", the
  Cyc quote); F102 carded from Phase 2's Sprint 28 results, read at
  10086da; snapshots refreshed on F57 (1,847 unread), F95 (0 unnamed
  PDFs) and F98 (1,402 ids, about 21 new). Phase 1.3: 0 re-checks due;
  schema and ADRs unchanged by Sprint 11
- **docs**: F95's next release names the Classiq Quantum Circuit Challenge
  result (team lead, 2026-10-23): PoJen Wang's two-part blog (the
  compiler field guide and the depth-95 write-up) and Classiq's wrap-up
  page as three web source records with local copies; no
  repository record (none is linked); the LinkedIn posts not entered
- **docs**: Sprint 12 scope selected (team lead, 2026-10-23): F101, F95,
  F98, F100, F102, F57 at 400 records and F51; released copies F103 (F95),
  F104 (F98) and F105 (F57). Plan drafted
  (`docs/sprints/SPRINT_12_PLAN.md`); F101 widened at planning from 1
  record to the 4 that store "&amp;". Approved as amended (2026-10-23):
  Q1 = 1 (400 from F57's ranking, others on top), Q2 = 2 (F51 stays
  HOLD), Q3 = 1 (F106, the ADR-0005 amendment, carded and added)

### 2026-10-21 to 2026-10-23 (Sprint 11, PR #113, merged to develop 2026-10-23 and to main via PR #121 the same day; tagged sprint-11)

- **docs**: `docs/sprints/SPRINT_11_SUMMARY.md` written (with `##
  Actuals`); master plan's Past Sprint Summary and Last Completed Sprint
  rolled for Sprint 11; `CHECKLIST-Phase2-pre.md` Sprint 11 section
  (2026-10-23, 53cfe45). Entry added at Sprint 12 Phase 1.1; the commit
  carried none

- **docs**: Sprint 11 retrospective recorded (2026-10-22, a87112a): team
  lead feedback, the feedback on the prompt's new wording, improvements
  I1a to I5 with root causes, the hand-download list order confirmed
  (Q2 = 1). Entry added at Sprint 12 Phase 1.1; the commit carried none

- **process**: Sprint 11 retrospective I3 to I5 disposed (2026-10-23). I4:
  every in-place edit of a repository file uses the Edit tool;
  `block_unraw_escape.py` blocks `sed -i`, `perl -i` and their kin on any
  repository file (not only code), treats a search pattern naming sed as
  data, and catches a quoted `"sed"` name. CLAUDE.md rule. I3 carded on
  F57 from Sprint 12's release; I5 skipped. Also: the commit hook loads the
  suite runner only from its own repository (security review).

- **process**: Sprint 11 retrospective I1a, I1b and I2 (2026-10-23, team
  lead: "apply now"). I1a: `store.quotes.require_verbatim` also refuses a
  quote mark the quote pattern does not parse and, given `value=`, a figure
  its own quotes do not hold; `Verified` carries the value, so a check
  without it licenses no write. It found F92's
  `qci-email-dirac3s-much-better-results-no-comparison-named`, whose second
  quote was never checked (corrected and re-applied; second apply writes
  nothing), and a Sprint 7 Cyc quote cut short (proposed for Sprint 12).
  I1b: the write-path scan moved to `store/write_path.py`, and
  `backup_before_write` runs it on the calling script before the backup.
  I2: `scripts/run_suite.py` prints one verdict from pytest's exit code
  and records it with the tree it ran on; the commit hook refuses a commit
  of a tree whose verdict is FAILED or INVALID. Intake section 41; every
  new guard proven by injection.

- **docs**: F100 carded for Sprint 12 (2026-10-22, team lead at Manual
  Validation): per-test timings, then a faster full suite and a decided
  commit-gate rule

- **feat**: Sprint 11 Manual Validation decisions (2026-10-22): the
  hand-download list is computed from the store in priority order
  (`scripts/hand_download_list.py`; 16 records as of 2026-10-22; Q2), and
  `NVIDIA/auto-ontology-eval` is linked `code-of` the NVIDIA blog record on
  the team lead's decision, which its evidence names (Q1 = 2; 7 links).
  F95 names the next release's repository
  (wangy8205165/Quantum-NeuralNetwork-WhitePaper). Intake section 39;
  `tests/test_hand_download_list.py`, `tests/test_sprint11_f97_intake.py`.
  Same day (Q3 = 1 and the team lead's follow-up): F62's 22 discovery
  papers with no copy marked onto the list in the store
  (`scripts/sprint11_q3_f62_hand_download.py`; 38 records); each entry
  names its target file (intake section 3) and why it matters, in four
  priority groups; the `hand-download-list` skill shows it on request.
  Intake section 40

- **feat**: F96 (Sprint 11 Task G, 2026-10-22, the F57 release): the
  200-record slice read: 192 records read by 24 first-pass readers (ledger
  groups g01 to g24) and by the coordinator against every quoted passage;
  649 assertions from 189 records (281 HIGH named one by one, 1 vendor
  description MODERATE, 367 LOW); 3 records bear on no context; 8 with no
  copy keep their tier with the reason (7 for hand download, Mezquita 2021
  retracted). The coordinator replaced 13 values and added quotes for 16.
  **fix**, same day: the first apply ran without `require_edit_basis` and
  with the figure check only printed; both now refuse in `verify()`, and
  the second apply corrected 7 values' quotes (F and G) and moved 5
  measured results from HIGH to LOW. Intake section 38;
  `tests/test_sprint11_reading.py` (Issue #120)
- **feat**: F97 (Sprint 11 Task F, 2026-10-22): new papers in `Papers\`
  and the team lead's list entered and read: 38 local files linked to 36
  records, 7 new records (six preprints, NBER w35905, the NVIDIA blog), 6
  repository records with 6 `code-of` links (`NVIDIA/auto-ontology-eval`
  entered unlinked: no source names it as a paper's code); 38 records read
  in ledger groups g25 to g29, 125 assertions from 37 records (54 HIGH, 4
  vendor descriptions MODERATE). Intake sections 36 and 37;
  `scripts/sprint11_f97_intake.py`, `scripts/sprint11_reading.py`;
  `tests/test_sprint11_f97_intake.py` (Issue #119)
- **feat**: F91 (Sprint 11 Task E, 2026-10-22): magic state cultivation
  (Rosenfeld et al., Science, DOI:10.1126/science.aee7961) entered by DOI
  and read in its free preprint arXiv:2512.13908v1 (the Science license
  starts 2027-10-15): 1 paper at `read`, 6 assertions under `qc`, all LOW
  (5 HW, 1 SIM projection). The abstracts' difference ("at least
  0.9999(1)" in Science only) is carried. A fresh-eyes review corrected
  three scope errors (the 8% filter, the 76(3)% baseline's circuit, the
  distance-5 code not being a surface code) before commit. Intake section
  35; `tests/test_f91_magic_state.py` (three injections run) (Issue #118)
- **fix**: F92's three `platform:dirac-3` assertions classed "not
  addressed" against the Dirac-3S guide in
  `scripts/sprint8_f65_dirac3s_reading.py`; the F65 guard had failed the
  full suite on them (Issue #116)
- **feat**: F93 (Sprint 11 Task D, 2026-10-22): Phase 2's F108 ceiling
  validation entered by the inbound path at commit eef3349: 1 source and 4
  SIM assertions under `ml` (no method recovered the known ceiling,
  MODERATE as the pass rule was read after the run; the plug-in's 5-12%
  overstatement; the AUPRC floor tracking the model; default HGB missing a
  rare threshold). Dated amendment to
  `docs/research/ceilings-ml-and-optimization.md`; intake section 34;
  `tests/test_f93_f108_ceiling.py` (three injections run) (Issue #117)
- **feat**: F92 (Sprint 11 Task C, 2026-10-22): QCi's answers of 2026-10-20
  and 2026-10-21 entered as vendor statements: 3 email source records
  (file, SHA-256, sender, date; Phase 2 git-ignores the folder) and 18
  assertions, hedges and plans at LOW, the 954 levels with the unit "not
  stated". No relation: the fresh-eyes review found the first apply's one
  `supports` link failed ADR-0004 A8 (b), and the script withdraws it by
  name. Intake section 33; `tests/test_f92_qci_answers.py` (four
  injections run) (Issue #116)
- **process**: Sprint 11 readers (2026-10-22): each reader writes temp files
  to its own scratch folder, after one reader's files were overwritten by
  another; and checks its quotes with the repository's own extraction,
  after 10 of the first 700 quotes failed it (dashes and minus signs
  rewritten as ASCII) (Issue #120)

- **chore**: Sprint 11 opened (2026-10-21). The team lead merged PR #101
  into develop (45883ef) and PR #112 to main (5a98c36); `sprint-10`
  tagged on 5a98c36; branch `feature/20261021_Sprint_11` cut from the
  Sprint 10 branch (6.6 carry-forward). Phase 1.1 reconciliation: every
  day with commits since 2026-10-18 has entries; one commit lacked its
  own, added below under Sprint 10 (F91, 2026-10-19)
- **docs**: Backlog refinement 2026-10-21 (Sprint 11 Phase 1.4): F92
  (QCi's 2026-10-20 answers to Phase 2, Priority 40) and F93 (Phase 2's
  F108 ceiling validation result, Priority 80) carded from Phase 2 read
  at b074780 and eef3349; F91 moved from Priority 65 to 62 (step rule;
  sprints with F90). F51's hold copy re-checked: hash unchanged
- **docs**: F92 widened 2026-10-21: two later QCi emails (Wes Dyk confirms
  the classifierqboost Hamiltonian, answering P1; Charlotte Brown: integer
  solver raised to 954 levels on Dirac-3 and Dirac-3S, 9980 planned on
  3S). Provenance rule corrected: Phase 2 git-ignores `docs/qci_package/`,
  so the emails are named by file and SHA-256, not by commit
- **docs**: Sprint 11 items added (team lead, 2026-10-21): F94 (backlog
  cards redesigned from spamfilter-multi's practices); F57's release size
  raised from 74 to 200, newest paper first, one copy per sprint, and its
  Sprint 11 copy F96; F95 (permanent: ingest and read new PDFs in
  `Papers\`, 37 unnamed as of 2026-10-21) and its Sprint 11 copy F97
- **docs**: Sprint 11 scope selected (team lead, 2026-10-21): F94, F92,
  F39 (released as F99), F91, F57 (F96), F93, F95 (F97). F57's order back
  to relevance (newest-first withdrawn), up to 5 readers from one ledger
  with no record read twice. F97 carries the team lead's seven papers and
  six repositories. F98 carded (permanent from Sprint 12: Christophe
  Pere's Roadmap-to-QML list)

### 2026-10-18 to 2026-10-21 (Sprint 10, PR #101, merged to develop 2026-10-21 and to main via PR #112 the same day; tagged sprint-10)

- **docs**: F91 carded for Sprint 11 (2026-10-19, team lead's commit
  f99a9a2): the magic state cultivation paper (Science, DOI
  10.1126/science.aee7961). Entry added at Sprint 11 Phase 1.1; the
  commit carried none

- **test**: Copilot review of PR #101 -- the F87 pool test renamed to
  "three excluded remain", which is what it asserts (#111)

- **docs**: `docs/sprints/SPRINT_10_SUMMARY.md` written (with `##
  Actuals`); master plan's Past Sprint Summary and Last Completed Sprint
  rolled for Sprint 10 (awaiting merge)

- **process**: Sprint 10 retrospective I1 and I2 applied (2026-10-21; team
  lead: "do now i1 and i2. do not do i3"). I2: `require_verbatim` returns
  a `Verified`, and `store.ingest.insert_verified_assertion` /
  `sync_verified_assertion` refuse a write without the matching one. I1:
  `store.quotes.require_edit_basis` makes each coordinator edit name its
  source passages, and a replaced value's numbers and math signs must be
  in them. `tests/test_verified_writes.py` holds every new script to
  both; intake section 31. I3 (F57's closing rule) skipped. Fresh-eyes
  review fixed: a value that was only a number skipped the check (the
  page-number rule deleted it); sign flips and flipped inequalities
  passed; the scan missed aliased imports and scripts not named
  `sprint*`

- **process**: Sprint 10 Manual Validation complete (2026-10-19); the
  eight-paper hand-download list moved to Sprint 11 as F90 (Priority 60)
  at the team lead's request. Retrospective written
  (`docs/sprints/SPRINT_10_RETROSPECTIVE.md`, the team lead's words
  verbatim, Very Good in every category); improvements I1 to I3 proposed

- **feat**: Task J (F87, #111), Manual Validation Q4 = 2 and Q6
  (2026-10-19) -- the live discovery re-run's candidates enter at `seen`:
  91 of the 99 top-listed (6 excluded by the team lead, 2 Sprint 9
  exclusions back at the top), two classical-ML-on-molecules papers moved
  from the qml stream to `ml` at the team lead's request. 5 preprints
  retitled at publication entered by journal DOI. Store 2,284 papers;
  F57 count 2,060 at `seen` or `screened` (snapshot 2026-10-19).
  `scripts/sprint10_f87_enter_seen.py`, `tests/test_f87_enter_seen.py`,
  intake section 30

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
