# CLAUDE.md

Guidance for Claude Code sessions in this repository. The authoritative process
docs are `docs/SPRINT_EXECUTION_WORKFLOW.md` and the set it names; the
authoritative design is `docs/adr/0004-evidence-based-db.md` and
`docs/adr/0005-reference-library.md`, both ACCEPTED with early-innovation
status.

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

The seed PDFs live at `D:\Data\Harold\EvidenceBasedDB\Papers` and are
deliberately outside this repository. Read them; do not commit them.

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
