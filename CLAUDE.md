# CLAUDE.md

Guidance for Claude Code sessions in this repository. The authoritative process
docs are `docs/SPRINT_EXECUTION_WORKFLOW.md` and the set it names; the
authoritative design is `docs/adr/0004-evidence-based-db.md` and
`docs/adr/0005-reference-library.md`, both ACCEPTED with early-innovation
status.

**This repository is written in US English.** Team lead, 2026-09-17: this was
left ambiguous before (unlike `hsbc-quantum-fraud-2026`, which states it
explicitly, since HSBC is UK-based and the team lead is not). Applies to this
repository's own process and design docs -- ADRs, sprint plans,
`CLAUDE.md`, `docs/*.md` -- not to text quoted or cited verbatim from a paper
or book, which keeps whatever spelling its source used. See F13
(`docs/ALL_SPRINTS_MASTER_PLAN.md`) for the guard that will enforce this.

## What this repository is

The **Evidence Based DB**: a store of assertions, acronyms, technical terms and
papers, each carrying provenance and a derived certainty. Its first consumer is
the HSBC quantum fraud submission
(`github.com/kimmeyh/hsbc-quantum-fraud-2026`), but the target scope is a domain
knowledge base over quantum machine learning, machine learning, quantum
computing, and the major QC platforms.

**It is private.** That has a consequence recorded in ADR-0005: while it is
private, no citation from the public consumer repository may depend on this one
resolving. Citations there carry their claim and provenance inline.

## What this repository is NOT

Not a paper archive. **ADR-0005 section 3: records, never the PDFs.** Most
published papers are not redistributable and several in the seed set are vendor
or conference material. The `access` field points at a DOI, an arXiv id, or a
local path outside version control.

### The two directories, and which is which

| Path | What it is |
|---|---|
| `D:\Data\Harold\github\EvidenceBasedDB\` | **This repository.** Everything here is version-controlled |
| `D:\Data\Harold\EvidenceBasedDB\` | **Not a repository.** Material connected to the solution that does not belong in git |

The second holds `Papers` (46), `Books` (38), `GitHubRepos` (8) and
`References`. Read from it freely; **never copy its contents into this
repository.** The `access` field on a paper record points there, or at a DOI or
arXiv id.

Every repository on this machine lives under `D:\Data\Harold\github\`. The
first attempt at seeding this one put the git repository inside the non-repo
directory, which conflated the two; corrected 2026-09-14 by cloning to the right
place and removing the misplaced copy.

## Early innovation: expect revision

Both ADRs are Accepted AND early-innovation. That pair is deliberate and the
distinction matters: **Accepted means the decision is made; early-innovation
means it is expected to change.** After roughly 20 papers, review both ADRs
against what actually happened, using the six questions each one carries.

Revisions are recorded as **dated amendments at the bottom of the ADR**, never
as edits in place. A document that silently becomes correct teaches nobody why
it was wrong.

## Standing rules (see docs/SPRINT_EXECUTION_WORKFLOW.md for the full set)

- All PR merges are the team lead's action, at every level. Claude never merges.
- `--no-verify` is banned.
- Every assertion originates in a source with provenance. **A record that cannot
  say where its value came from is the defect this whole system exists against.**
- **Determinate facts are COMPUTED, never stored.** If a command or an artifact
  can answer it, the database holds a resolver, not a copy. This is the rule the
  consumer repository learned the hard way: one value restated in five documents
  drifted in three of them.
- Reading level escalates ONE grade at a time from 8 toward a PhD ceiling, and
  the level achieved is recorded. Grades 13 to 16 are acceptable; a CLUSTER at
  17 or above is a finding about the source document, not about the glossary.
- **This repository's sessions may READ `spamfilter-multi` and
  `hsbc-quantum-fraud-2026` (their repos and their Claude Code memory
  directories) but must never WRITE to either.** Team lead, 2026-09-15:
  research into those repositories -- porting a convention, checking a
  backlog item, reading a memory file -- is expected and stays fine; writing,
  editing, or running a write-shaped command against either from an
  EvidenceBasedDB session is not, and needs a session already working in
  that repository instead. Hook-enforced:
  `.claude/hooks/block_sibling_repo_writes.py`, on both the `Bash|PowerShell`
  and `Write|Edit|NotebookEdit` PreToolUse matchers.

## Things Claude Should NOT Do

Added 2026-09-15. These carry forward preferences Harold has stated
repeatedly in other repositories (spamfilter-multi) that never made it into
hsbc-quantum-fraud-2026's own `CLAUDE.md` and so could not have carried
further into this one at seeding. Also recorded as memory files (see
`feedback_*.md` in this repository's memory index) -- kept in both places
deliberately: `CLAUDE.md` is read in full every session, memory is recalled
selectively, and a rule that lives only in memory has already been missed
once for exactly that reason.

- **Don't ask a decision question except as a PLAIN NUMBERED LIST Harold can
  answer by typing a digit.** Not the AskUserQuestion tool's multiple-choice
  UI, and not prose. The test is mechanical: if Harold cannot answer by
  typing `1`, it is formatted wrong. Applies to yes/no ("1. Yes  2. No"),
  option comparisons, and path selection, inside or outside any auto-advance
  window -- only the FORMAT is at issue, not whether asking is allowed.
  **Treat AskUserQuestion as a banned tool call in this project, full stop
  -- do not evaluate whether a given question "fits" it.** Violated in this
  repository in Sprint 2 (2026-09-17) immediately after already being
  corrected for the same thing earlier in the SAME session, with this rule
  present the whole time: "This is not how to ask question, please
  research, update as needed to prevent in the future." Checking that the
  rule exists is not the same as stopping to apply it before the tool
  call -- there is no case where the tool call is the right move here.
- **Don't phrase a decision question so "yes" could mean two different
  things.** Each question needs one unambiguous answer form: yes/no, or
  select 1/2/3/.../all. A compound question carrying two decisions ("approve
  the text? And where should it be hosted?") is two numbered questions, not
  one.
- **Don't point Harold back to something he would have to scroll for.**
  "The plan from earlier," "as listed above," "per my previous message" all
  point at content that may be many screens back, behind tool output and
  test runs. Re-present the full instructions in every message that asks him
  to act -- validation steps, manual steps, unanswered questions with their
  options intact. This binds hardest at Phase 5.3 Manual Validation, handed
  over once and then followed by hours of review and fixes before he
  actually validates: re-present the full validation plan every time, not a
  reference to it.
- **Don't touch more than one file/surface on a request without echoing the
  requirement back first.** One sentence: "I understand you want X to happen
  on Y, with Z behavior. Correct?" Wait for confirmation, then proceed
  without asking again for the same task. Skip this for trivial one-line
  fixes and doc-only edits with no scope ambiguity.
- **Don't use grid/ASCII tables for terminal task summaries or manual
  validation checklists.** Use bullet lists. Markdown tables inside committed
  doc files are fine; this is about terminal output readability only.
- **Don't report a batch of completed tasks mid-sprint as though it were a
  stopping point.** Before ending any turn: is every approved task DONE, or
  does a specifically named `docs/SPRINT_STOPPING_CRITERIA.md` criterion
  apply to EACH remaining one? If no, continue with the next task.
- **Don't invent "context window running low" as a stopping reason.** The
  only valid stopping reasons are the named criteria in
  `docs/SPRINT_STOPPING_CRITERIA.md`. If genuinely uncertain whether an
  upcoming task fits, do the task first; a failure for that reason is itself
  the stopping signal, not a guess made in advance.
- **Don't claim a guard works because the suite is green. Prove it FAILS.** A
  test that cannot fail is worse than no test, because it buys false confidence.
  Break the thing it guards, watch it go red, then restore. This is not
  hypothetical here: `tests/test_guard_discipline.py` shipped INTO this
  repository resolving its path one directory above the repo root, so it
  reported a file that exists as absent and skipped. It was fixed 2026-09-14 by
  removing the skip branch entirely, and verified by hiding the document and
  watching the test go red. The Inherited section below records this class as
  history; this entry is the rule.

- **Don't stage a commit without reading what you are staging.** Run
  `git status --short` first and account for every entry. `git add -A` is fine
  once you have. It happened here: a review-findings commit swept in an
  unrelated, uncommitted PowerShell-to-Python hook conversion whose message
  described none of it. The commit was unwound and split.

- **Don't act on a recalled memory without checking it against current repo
  state first.** Compare its date and claims against git log, sprint status,
  and the docs it references before trusting its "next steps" -- a memory
  that was true when written can be stale by the time it is recalled.

## Inherited from the consumer repository, and why

The sprint methodology, the hooks and several tests were copied from
`hsbc-quantum-fraud-2026` at seeding. They are carried because they encode
failures that were paid for once:

- **`test_hook_registration.py`** -- two hooks there were registered with a
  single backslash before `block-`, which JSON parses as U+0008, so they pointed
  at nonexistent files and were skipped SILENTLY for the whole of their life. A
  retrospective recorded one of them as working.
- **`test_guard_discipline.py`** -- a guard named for catching a regression must
  say how it was proven to fail. Three guards there shipped vacuous; two were
  caught by review rather than by the injection their docstrings claimed.
- **`test_no_em_dashes.py`** -- a documented style rule decayed the moment
  attention moved, and a reviewer found fourteen violations.
- **`test_changelog_currency.py`** -- its own threshold was wider than the lapse
  it was written to catch, so it passed on its own defect.
- **`test_sprint_documents.py`** -- the three-doc rule, unenforced for twelve
  sprints.

The pattern across all five: **a rule that lives only in a document decays; a
rule with a failing test does not.** Write the test.
