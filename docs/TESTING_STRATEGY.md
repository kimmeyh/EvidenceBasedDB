# Testing Strategy

**Purpose**: What gets tested, how, and why, for the Evidence Based DB.
**Audience**: Claude Code sessions; the team lead.
**Last Updated**: 2026-09-16 (Sprint 1 Task H, F1 -- reworked from the version inherited at seeding)

**REWORKED 2026-09-16.** The version inherited from hsbc-quantum-fraud-2026
at seeding was written for that repository's statistical/ML evidence
pipeline: BCa bootstrap vs `scipy.stats.bootstrap`, FISTA QP vs
`scipy.optimize`, the IEEE-CIS leakage control, `results.json`. None of that
exists in this repository, which tests a schema, an export pipeline, and
ingestion paths, not a statistical model. The PRINCIPLES this project's
testing culture has already proven (known-answer testing, injection-verified
guards, testing the shipped artifact rather than the code that produced it)
are real and generalize; this rewrite keeps them and replaces every
illustration with this repository's own equivalent.

## The known-answer principle

Every schema constraint or export transformation is tested against a KNOWN
expected output, never merely against "the code ran without error":

- A CHECK constraint is tested for both the value it must accept AND the
  value it must reject (`tests/test_schema.py`) -- accepting alone proves
  nothing about whether the constraint is actually enforced.
- A deterministic transformation (the export) is tested against its exact
  expected bytes, not just "produced valid JSON" (`tests/test_export.py`'s
  byte-identical-re-export tests).
- A resolver that computes a value live is tested by injection: change the
  source, confirm the resolved value changes by exactly the expected amount
  (`tests/test_resolvers.py`).

## Guards as tests

A guard exists only if a test can make it fire. `tests/test_hook_
registration.py` and `tests/test_sibling_repo_write_guard.py` are the
worked examples here: every hook is exercised directly against a
subprocess with a controlled payload proving both the block case and the
allow case, not just that the hook file exists and parses.

## Injection verification: prove the guard fails

**Mandatory for any test whose purpose is to fail.** Write the guard, then
BREAK the thing it guards and confirm it goes red. Restore, confirm green.
Record in the test's docstring (or the commit that added it) that it was
verified by injection.

This is not ceremony. During Sprint 1 Task B, weakening the
`assertion_relations` CHECK constraint to accept a third relation value was
used to confirm `test_assertion_relations_rejects_a_relation_outside_the_two_named`
actually goes red on that exact defect, not merely that it happens to pass
today. A guard that has never been seen to fail is a guard nobody has
tested.

## Every script that writes a committed artifact needs a test that reads its shipped output

Guarding the CODE that produces an artifact is not the same as guarding the
ARTIFACT. `tests/test_export_currency.py` is the worked example: it
regenerates the export from the real store into a temp directory and diffs
against the real committed `export/`, rather than trusting that a prior
regeneration is still current. A test that only calls `export_class()` and
checks its return value would not catch a stale committed file.

## What is deliberately not tested

One-shot scripts (verified by use, e.g. `scripts/generate_seed_set_metadata.py`,
whose real output was reviewed directly rather than covered by a test suite),
and sprint/process documentation. The store's schema is validated by its own
CHECK constraints plus `tests/test_schema.py`'s injection-verified tests,
not by a test double.

## Running

```powershell
.\.venv\Scripts\python.exe -m pytest -q     # full suite
```

```bash
python -m pytest -q     # full suite (POSIX)
```
