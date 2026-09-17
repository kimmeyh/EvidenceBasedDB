# Quality Standards

**Purpose**: Documentation, code, and automation standards for this repository.
**Audience**: Claude Code sessions; the team lead.
**Last Updated**: 2026-09-16 (Sprint 1 Task H, F1 -- reworked from the version inherited at seeding)

**REWORKED 2026-09-16.** The version inherited from hsbc-quantum-fraud-2026
at seeding illustrated most of its rules with that repository's own
Dirac-3/PDF-rendering/frozen-protocol history (`experiments/src`,
`results.json`, `prereg-freeze`, QCi letters, `run_h6.py`). None of that
exists in this repository. The PRINCIPLES behind several of those rules are
real and worth keeping; this rewrite keeps the principle and drops or
replaces the illustration with this repository's own equivalent where one
exists, per Sprint 1 Task H (F1).

**What gets version-controlled is decided by REGENERATION COST, not file
size**: an artifact that can be rebuilt for free by running a script belongs
in `.gitignore`; an artifact whose regeneration costs real effort, real
money, or depends on an external service that may change belongs in git,
however small. This repository applies it directly: `store/evidence.db` is
gitignored (rebuildable from the ingestion scripts and the seed set), while
`export/*.json` is committed (it is the artifact ADR-0004 section 2 names,
and its diff is the review mechanism the whole design depends on).

**Verify the artifact you ship, not a proxy for it**: a check that reads
something OTHER than the delivered artifact can report success while the
artifact is broken, which is worse than having no check, because it consumes
the attention a real check would have earned. `tests/test_export_currency.py`
implements this here: it regenerates the export from the real store into a
temp directory and diffs against the real committed `export/`, rather than
trusting that a prior regeneration is still current.

**Re-read before write**: when a file may have been touched by another
process, a background job, or an earlier in-flight write, RE-READ it
immediately before writing. A stale-write overwrite is a defect class, not
an accident. Whole-file writes to shared documents (the master plan, the
sprint plan, `CLAUDE.md`) are the highest-risk case.

**A number in a document must be traceable to a committed generator**: a
value that reaches a document but whose generator was never committed
cannot be checked by a reviewer, cannot be recomputed after a fix, and
cannot be defended when asked how it was produced. This is the concrete
argument for `store/resolvers.py` (Sprint 1 Task G): the consumer
repository's amendment count is computed live from its own document, not
typed into this repository as a remembered number that can drift.

## Documentation standards

- Every doc in `docs/` opens with **Purpose**, **Audience**, **Last Updated**.
- File size cap ~40,000 characters; beyond it, extract sections to their own doc and cross-reference. Table of contents required above ~20,000 characters. (These docs are read by Claude every session; size is a cost.)
- No contractions in formal docs; no emoji; bracketed markers ([OK], [FAIL], [WARNING]) where a status glyph is needed; no em dashes.
- Templates are authoritative: read the template section in the same turn before producing its deliverable (workflow invariant 5).
- **Full-accounting-first rule**: when summarizing research or review output, state the complete accounting FIRST (totals and per-category counts), then present the triaged subset. A compressed summary that makes 30 findings read as 4 forces the team lead to challenge to surface the rest.

## Code standards (KISS / YAGNI)

- The simplest implementation that satisfies ADR-0004 and ADR-0005's spine wins. No speculative abstraction: build for the schema as accepted, not imagined future record classes. Complexity budget goes to provenance and schema correctness, not architecture.
- Single implementation per concept: one schema, one export path, one ingestion path per record class. Duplication of schema-bearing code is a defect.
- Type hints on signatures; module docstrings state which ADR section the file implements; no debugging prints left behind; known failure modes documented in the header of long-running scripts.
- An ACCEPTED ADR's spine (the schema fields ADR-0004 section 3 and ADR-0005 section 2 define) changes only with a dated amendment at the bottom of the ADR, never a silent edit (CLAUDE.md "Early innovation: expect revision").

## Automation standards (PowerShell-native)

- Automation scripts on this machine are PowerShell (`.ps1`), executed natively, never wrapped in bash (wrapping loses toolchain context on this exact host; a lesson this repository inherits from its own process history). POSIX scripts only where a tool demands them.
- Long jobs run in the background with output files; per-unit persistence so interruption loses one unit, not the run.
- `--no-verify` is banned; hooks are part of the quality system.

**AMENDMENT, 2026-09-14: Claude Code hooks in `.claude/hooks/` are Python, not
PowerShell.** The PowerShell-native rule above was written for automation that
runs ONLY on this machine, where cross-OS portability buys nothing and
wrapping across shells has cost real defects. `.claude/hooks/`
scripts are different: Claude Code invokes them as plain commands over a
documented stdin/stdout/exit-code contract, so the language is not tied to
this host at all, and this repository's origin (`kimmeyharold`) may be cloned
onto a non-Windows machine even though today it only runs here. The five
hooks seeded from hsbc-quantum-fraud-2026 (`block_carry_forward_stash.py`,
`block_branch_from_develop.py`, `block_unraw_escape.py`,
`block_shell_metachar_expansion.py`, `verify_closeout_complete.py`) were
converted from `.ps1` to `.py` this date. Converting also let their command
strings in `.claude/settings.json` use forward slashes instead of Windows
backslashes, which removes the doubled-backslash JSON-escape hazard that
`test_hook_registration.py` exists to catch (F68) -- the hazard is gone by
construction rather than guarded against, though the test itself is
unchanged and still passes. This amendment covers `.claude/hooks/` only; the
PowerShell-native rule stands unchanged for everything else, including
`scripts/` and any future automation outside the hooks directory.

**AMENDMENT, 2026-09-15: a sixth hook, `block_sibling_repo_writes.py`, guards
against writing into `spamfilter-multi` or `hsbc-quantum-fraud-2026`.** Team
lead: "from here on out, the activities in this repo should not
write/update files in either spamfilter-multi or hsbc repo... It is OK to
read from them upon request, but not write to them." Registered on both the
`Bash|PowerShell` and `Write|Edit|NotebookEdit` PreToolUse matchers, since
either tool shape can target a file outside this repository. See CLAUDE.md
"Standing rules" for the full statement of the rule this hook enforces.

## Testing standards (summary; full doc is docs/TESTING_STRATEGY.md)

- `pytest -q` green before any commit.
- Known-answer tests for schema and export logic (a determinate transformation has a determinate expected output).
- Guard tests are proven to fail by injection before they are trusted to pass (CLAUDE.md "Don't claim a guard works because the suite is green. Prove it FAILS").
- Scratch probes never enter the repo.

**Every script that writes a committed artifact needs a test that reads its
SHIPPED OUTPUT**, not merely that the code that produced it ran without
error. `store/export.py`'s tests exercise this directly: they check the
actual bytes of the exported JSON files, not just that `export_class()`
returned something. Guarding the code alone would not catch a determinism
regression; guarding the artifact does.

**Verify a tool distinguishes good from bad BEFORE trusting its verdict.**
Before iterating against any measurement, confirm the instrument reports
differently for a known-good and a known-bad case. Familiarity with a tool
is not verification that it still measures what it claims to.

**New code inherits no schema enforcement it does not call.** A script that
writes directly to the `records` table rather than through
`store/ingest.py`'s `insert_paper`/`insert_assertion` functions can silently
skip the contexts, applicability, or relations a real record needs. Reuse
the ingestion path; do not hand-roll a second one that happens to look
similar.

**A number in a document must be traceable to a committed generator** (see
above): if a figure or count reaches a sprint document, the code or query
that produced it is committed in the same change, not computed inline and
only its output recorded.

**AMENDMENT, 2026-09-16 (Sprint 1 retrospective improvement 1): hook and
script smoke tests use `subprocess.run()` with a programmatically built
JSON payload, never a shell pipe (`echo '...' | python hook.py`).** Sprint
1 hit three false negatives from this exact pattern -- `block_unraw_
escape.py`, `block_sibling_repo_writes.py`, and (worst) `test_ingest_
seed_set.py`'s first version, whose bash-quoted synthetic payload masked
a real bug and, separately, whose un-isolated `EXPORT_DIR` silently
overwrote the committed `export/` directory. In every case the CODE under
test was correct; the SHELL was mangling the test's own input before the
code ever saw it. `tests/test_sibling_repo_write_guard.py` is the worked
example of the fix: every case calls `subprocess.run([sys.executable,
str(HOOK)], input=json.dumps(payload), ...)` with a real Python dict, so
the JSON is never hand-quoted through a shell at all.
