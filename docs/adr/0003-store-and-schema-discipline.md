# ADR-0003: Store and schema discipline

## Status

Accepted

## Date

2026-09-02 (seeded from hsbc-quantum-fraud-2026's own results.json design, 2026-09-14; content rewritten 2026-09-16, Sprint 1 Task H, F1 -- see Amendments)

## Context

A store that holds provenance-bearing records needs discipline independent
of any one schema's specific fields: how writes happen, how the store stays
diffable and reviewable, and how the boundary between the store and its
committed artifact is drawn. ADR-0004 fixes the actual schema (the four
record classes, contexts, certainty model); this ADR states the discipline
that governs how ANY schema in this repository's store is written to and
exported, independent of what that schema's fields are.

## Decision

- **SQLite is the store of record; a deterministic text export is the
  artifact** (ADR-0004 section 2). The store is queryable and
  transactional; the export is what a reader or a reviewer actually reads,
  and its diff is the review mechanism.
- **Every record is schema-complete at commit time.** A record's spine
  fields (`id`, `class`, `value`, `provenance`, `evidence_tag`) are set
  when the record is inserted, not backfilled later. `store/ingest.py`'s
  `insert_paper`/`insert_assertion` enforce this by construction: there is
  no code path that inserts a record missing its required fields.
- **Writes go through the ingestion path, never a hand-rolled INSERT.**
  Reusing `store/ingest.py` is what keeps every record's contexts,
  applicability, and relations consistent; a script that writes directly
  to `records` can silently skip them.
- **The export regenerates deterministically from the store**
  (`store/export.py`): fixed record order (by id), fixed key order, one
  trailing newline per file. A re-export of unchanged data is
  byte-identical (`tests/test_export.py`); the committed export is checked
  against a fresh regeneration (`tests/test_export_currency.py`).
- **The store itself is a build output and is gitignored.** Nothing in
  this repository depends on `store/evidence.db` being present in a fresh
  clone; the export is what a reader consumes, and the ingestion scripts
  under `scripts/` are what rebuild the store from the seed set and the
  sprint's own committed metadata (`scripts/seed_set_metadata.json`).

## Alternatives Considered

### Hand-edited JSON/Markdown files, no database
- **Pros**: no dependency; trivially diffable; no export step.
- **Cons**: no referential integrity, no query, and hand-editing at domain scale invites the drift this store exists to prevent.
- **Why Rejected**: kept as the EXPORT format, which is where its diffability is worth having (ADR-0004 "Alternatives considered").

### A document store or graph database from the start
- **Pros**: contexts and prerequisite chains are graph-shaped; a graph engine expresses them natively.
- **Cons**: prices in a need not yet measured. SQLite handles the pilot's three-deep context hierarchy via recursive CTEs.
- **Why Rejected FOR NOW, with named triggers**: see ADR-0004 section 2b. Both remain live options with the conditions for adopting them written down rather than left to judgement.

## Consequences

### Positive
- A record's provenance is checkable by construction, not by convention -- the schema's CHECK constraints (`tests/test_schema.py`) reject a record missing a required field rather than accepting an incomplete one.
- The export's diff is the review mechanism: a fact changing value shows up in a PR review, which is the property this whole system exists to provide (ADR-0004 section 2).

### Negative
- Every schema change requires updating both `store/schema.sql` and `store/export.py` in the same commit, or the export silently drops a field. No test currently catches a field that exists in the schema but is never exported; this is a real gap, not yet carded.

### Neutral
- The store engine (SQLite today) is replaceable without touching the export format, since the export is the durable artifact and the store is a build output (ADR-0004 section 2b: "migration is cheap by construction").

## References

`docs/adr/0004-evidence-based-db.md` (the actual schema this discipline governs); `store/schema.sql`, `store/ingest.py`, `store/export.py`; `tests/test_schema.py`, `tests/test_export.py`, `tests/test_export_currency.py`.

## Amendments

**2026-09-16 (A1): Content rewritten from the consumer repository's
results.json design.** This ADR was seeded 2026-09-14 as ADR-0008 from
hsbc-quantum-fraud-2026, renumbered 0003, and its content described that
repository's own `experiments/results/results.json` schema (arm, dataset,
protocol, seed, config_hash) -- a schema with no equivalent in this
repository. Team lead, 2026-09-16 (Sprint 1 Task H, F1): rewrite rather
than delete or mark superseded, since this repository genuinely has its
own store-and-schema discipline distinct from ADR-0004's specific field
list, and the discipline (schema-complete writes, deterministic export,
store-as-build-output) is what this ADR now states. The original
results.json content is preserved in this repository's git history at the
commit that seeded it, and remains live in hsbc-quantum-fraud-2026 itself.
