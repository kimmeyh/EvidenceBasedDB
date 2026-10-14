-- Domain-scale contexts (Sprint 1 Task D), added on top of the three pilot
-- contexts seeded in schema.sql (hsbc-2026, world, method).
--
-- ADR-0004 section 3b names these explicitly as the domain-scale set: "A
-- domain base needs at least: world, ml, qc, qml, platform:dirac-3,
-- platform:braket, platform:classiq, platform:ibm-q, platform:ionq, ...
-- as needed, method." The pilot deliberately started with three and the
-- ADR's own rule is to add a context only when assertions genuinely need
-- one the existing set does not cover -- but Sprint 1's own scope (team
-- lead, 2026-09-15) confirmed the domain-scale set will be needed by the
-- end of this sprint or shortly after, so it is seeded now rather than
-- added piecemeal mid-ingestion.
--
-- Only the platforms the ADR names CONCRETELY are seeded here
-- (dirac-3, braket, classiq). `platform:ibm-q`, `platform:ionq`, and
-- others stay genuinely "as needed" -- the ADR itself does not commit to
-- them, and seeding a platform context with no paper or assertion behind
-- it yet would be exactly the "context per project, a tag wearing a
-- costume" failure mode section 3b warns against.
--
-- `world` and `method` already exist from schema.sql; INSERT OR IGNORE
-- guards against re-running this script against an already-seeded store.

INSERT OR IGNORE INTO contexts (id, description) VALUES
    ('ml',               'Machine learning generally'),
    ('qc',               'Quantum computing generally'),
    ('qml',               'The intersection of ml and qc, which is NOT their union -- a fact can hold in qml without holding in either alone'),
    ('platform:dirac-3', 'QCi''s continuous-variable optimizer'),
    ('platform:dirac-3s', 'QCi''s Dirac-3S modular optimization system (ADR-0004 A8, 2026-10-12)'),
    ('platform:braket',  'AWS gate-based quantum access'),
    ('platform:classiq', 'Circuit synthesis platform');
