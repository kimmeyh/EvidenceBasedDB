-- Evidence Based DB schema (Sprint 1 Task B).
--
-- Implements the spine and class-specific fields from ADR-0004 section 3
-- (as amended: certainty/certainty_reasons per A2, class gains `paper` per
-- A3) and the paper-record fields from ADR-0005 section 2. This file is the
-- store of record; store/export.py regenerates the committed text export
-- from it (Task C). Nothing here is hand-edited after the store is queried
-- through it -- SCHEMA changes land here, DATA changes land through the
-- ingestion path built in Task E/F.
--
-- Foreign keys are OFF by default in SQLite and must be enabled per
-- connection (`PRAGMA foreign_keys = ON`); the store module does this on
-- every connect.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Contexts (ADR-0004 section 3b): the partitioning mechanism, never tags.
-- Seeded with the three pilot contexts from ADR-0005 section 2b; more are
-- added only when assertions genuinely share an assumption none of the
-- existing contexts already hold (ADR-0004 section 3b "Rule for adding a
-- context").
-- ---------------------------------------------------------------------

CREATE TABLE contexts (
    id          TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO contexts (id, description) VALUES
    ('hsbc-2026', 'Assertions specific to the HSBC quantum fraud submission: amendment counts, campaign totals, measured results'),
    ('world',     'True independent of any project: mathematics, physics, standard acronym expansions'),
    ('method',    'How this library and its consumers build and reason, including about the library itself');

-- ---------------------------------------------------------------------
-- Records: the common spine (ADR-0004 section 3), carried by every class.
-- `class` is constrained to the four values ADR-0004 amendment A3 settles:
-- assertion, acronym, term, paper.
--
-- `certainty` replaces the percentage `confidence` field per ADR-0004
-- amendment A2 and ADR-0005 section 2e (GRADE-style: four levels, derived,
-- never chosen directly). `certainty_reasons` is required whenever
-- certainty is not the class's starting level -- enforced at the
-- application layer, not by a CHECK constraint, since "the starting level"
-- depends on the evidence_tag and is not expressible as a column-only rule.
-- ---------------------------------------------------------------------

CREATE TABLE records (
    id                TEXT PRIMARY KEY,
    class             TEXT NOT NULL CHECK (class IN ('assertion', 'acronym', 'term', 'paper')),
    value             TEXT NOT NULL,
    provenance        TEXT NOT NULL,
    evidence_tag      TEXT NOT NULL CHECK (evidence_tag IN ('HW', 'SIM', 'PROJ', 'N/A')),
    certainty         TEXT CHECK (certainty IN ('high', 'moderate', 'low', 'very-low')),
    certainty_reasons TEXT,
    fidelity          TEXT CHECK (fidelity IN ('exact', 'scoped', 'consequence')),
    reading_level     INTEGER CHECK (reading_level IS NULL OR (reading_level BETWEEN 8 AND 20)),
    updated           TEXT NOT NULL,
    updated_reason    TEXT NOT NULL
);

-- Records claim contexts many-to-many (a term can belong to `qml`, which is
-- not the union of `ml` and `qc` per ADR-0004 section 3b -- a record may
-- need to be filed under an intersection context explicitly).
CREATE TABLE record_contexts (
    record_id  TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    context_id TEXT NOT NULL REFERENCES contexts(id),
    PRIMARY KEY (record_id, context_id)
);

-- Prerequisites: ids of records a reader needs first (ADR-0004 section 5).
-- Self-referencing, many-to-many, because the escalation ladder's rungs are
-- a DAG (checked, not merely trusted -- see store/checks.py in a later
-- task if a cycle-detection query is needed).
CREATE TABLE prerequisites (
    record_id       TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    prerequisite_id TEXT NOT NULL REFERENCES records(id),
    PRIMARY KEY (record_id, prerequisite_id),
    CHECK (record_id != prerequisite_id)
);

-- ---------------------------------------------------------------------
-- Class-specific fields (ADR-0004 section 3, plus ADR-0005 section 2 for
-- the paper class). One table per class rather than a wide, mostly-NULL
-- `records` table -- ADR-0004 section 2b names exactly this divergence as
-- the trigger for a document store, and a class-specific table is the
-- relational answer that avoids needing one.
-- ---------------------------------------------------------------------

CREATE TABLE assertion_fields (
    record_id        TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    units            TEXT,
    rounding         TEXT,
    -- The sentence in the source making the claim (ADR-0005 section 2,
    -- worked example: "citation_context: the sentence making the claim").
    -- Added 2026-09-16 (Copilot PR #1 review): AssertionRecord.citation_
    -- context was accepted by the ingestion dataclass and populated by
    -- scripts/ingest_lenat_marcus.py with real quoted source text, but had
    -- no column anywhere and was silently dropped on every ingest.
    citation_context TEXT,
    -- ADR-0004 A6 (2026-10-03, Sprint 6 Task E). Every assertion carries
    -- these, so since A6 every assertion has an assertion_fields row.
    -- `derivation`: extracted (a source yields it), synthesized (a
    -- generalization over the assertions that `supports` it), project (a
    -- fact about this project, sourced from its own documents).
    derivation       TEXT NOT NULL CHECK (derivation IN ('extracted', 'synthesized', 'project')),
    -- `claim_type`: an absence claim is only as good as the search behind
    -- it, so it must say what was searched and when (`search_scope`).
    claim_type       TEXT NOT NULL DEFAULT 'positive'
                     CHECK (claim_type IN ('positive', 'absence', 'vendor-self-claim')),
    search_scope     TEXT,
    CHECK (claim_type <> 'absence' OR (search_scope IS NOT NULL AND trim(search_scope) <> ''))
);

-- Documents that cite an assertion (ADR-0004 section 3: "the `documents`
-- that cite it"). Many-to-many since one assertion can be cited by several
-- documents and the field is a list on the assertion record.
--
-- REFERENCES records(id), not assertion_fields(record_id) (fixed 2026-09-16,
-- Copilot PR #1 review). `units`/`rounding` (assertion_fields) and
-- `documents` are unrelated concerns per ADR-0004 section 3's own field
-- list; the original FK forced an assertion_fields row to exist before any
-- document citation could be attached, so an assertion with no units/
-- rounding (most assertions) could never record a citing document.
CREATE TABLE assertion_documents (
    record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    document  TEXT NOT NULL,
    PRIMARY KEY (record_id, document)
);

CREATE TABLE acronym_fields (
    record_id       TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    expansion       TEXT NOT NULL,
    plain_definition TEXT NOT NULL,
    visual          TEXT
);

CREATE TABLE term_fields (
    record_id        TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    plain_definition TEXT NOT NULL,
    visual           TEXT
);

-- `see_also` is a list on the term record (ADR-0004 section 3); modelled as
-- a join to other records rather than a delimited text column so it stays
-- queryable and referentially valid.
CREATE TABLE term_see_also (
    record_id     TEXT NOT NULL REFERENCES term_fields(record_id) ON DELETE CASCADE,
    see_also_id   TEXT NOT NULL REFERENCES records(id),
    PRIMARY KEY (record_id, see_also_id)
);

-- Paper fields (ADR-0005 section 2). A paper record is PROVENANCE plus
-- screening state; the claims themselves live in the assertion class and
-- are linked in via paper_yields (ADR-0005 section 2b2).
-- `citation` is NOT a column here (dropped 2026-09-19, Sprint 4 Task B,
-- F25 B4 / decision Q2). It was a byte-identical copy of records.provenance
-- on 46/46 papers -- this project's founding defect ("one value restated in
-- five documents drifted in three") reproduced inside every row. The
-- citation lives once, in records.provenance; store/export.py renders it
-- from there. The live store was migrated by
-- scripts/migrate_paper_fields_drop_citation.py (table rebuild).
CREATE TABLE paper_fields (
    record_id               TEXT PRIMARY KEY REFERENCES records(id) ON DELETE CASCADE,
    tier                    TEXT NOT NULL CHECK (tier IN ('seen', 'screened', 'read')),
    access                  TEXT NOT NULL,
    disposition             TEXT NOT NULL,
    evidence                TEXT,
    mined_by                TEXT,
    -- REQUIRED at tier 'read' (ADR-0005 section 2), enforced BOTH by
    -- store/ingest.py validate_paper()/set_tier() (which also reject a blank
    -- string and explain what to do) AND by the table-level CHECK below
    -- (added 2026-09-19 with the same migration, after the Copilot PR #20
    -- review corrected this comment's earlier claim that SQLite could not
    -- express the rule without a trigger). The literal string 'never' is a
    -- valid, meaningful value -- distinct from NULL, which means "not yet
    -- tiered to require it."
    checked_against_source  TEXT,
    -- ADR-0005 A4 (2026-10-03, Sprint 6 Task E), fields 10 and 7. Which
    -- registry answered (set by the door), and a DISCLOSED conflict of
    -- interest with its anchor (" -- p.12 competing interests").
    -- Affiliations are computed (paper_probes), never typed here.
    metadata_provider       TEXT,
    coi                     TEXT,
    CHECK (tier <> 'read' OR checked_against_source IS NOT NULL)
);

-- `applicability`: context ids the paper bears on, per ADR-0005 section 2d
-- ("points at contexts; it is not its own vocabulary"). Many-to-many,
-- reusing the same contexts table records themselves claim.
CREATE TABLE paper_applicability (
    record_id  TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    context_id TEXT NOT NULL REFERENCES contexts(id),
    rationale  TEXT NOT NULL,
    PRIMARY KEY (record_id, context_id)
);

-- `yields`: the assertion ids extracted from this paper (ADR-0005 section
-- 2, 2b2). The field that makes a paper a source rather than a summary.
CREATE TABLE paper_yields (
    paper_id     TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    assertion_id TEXT NOT NULL REFERENCES records(id),
    PRIMARY KEY (paper_id, assertion_id)
);

-- ---------------------------------------------------------------------
-- ADR-0005 A4 (2026-10-03, Sprint 6 Task E): the reference fields.
-- ---------------------------------------------------------------------

-- Field 1 and 8: how the source was found, one row per route, and how that
-- route cited it (so comparing a collection's citation with the registry
-- is a query, not a re-read).
CREATE TABLE paper_found_via (
    record_id TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    route     TEXT NOT NULL CHECK (trim(route) <> ''),
    cited_as  TEXT,
    PRIMARY KEY (record_id, route)
);

-- Field 2: how far a reader read the source, per reader and date. `read`
-- needs a `full` or `partial` row (enforced in store/ingest.py set_tier).
-- `detail` is '' rather than NULL so the primary key stays unique.
CREATE TABLE paper_reads (
    record_id TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    reader    TEXT NOT NULL CHECK (trim(reader) <> ''),
    read_on   TEXT NOT NULL CHECK (read_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    extent    TEXT NOT NULL CHECK (extent IN ('full', 'partial', 'abstract', 'html-render', 'summary', 'grep', 'subagent')),
    detail    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (record_id, reader, read_on, extent, detail),
    CHECK (extent <> 'partial' OR trim(detail) <> '')
);

-- Fields 3, 4, 5 and affiliations: COMPUTED facts, kept only as the last
-- result of their probe, with its date and the provider that answered (the
-- probe rule). A dated measurement, not a copy: the resolver stays
-- authoritative and refresh_citations.py re-runs it each cycle. A
-- hand-origin record's status has provider 'hand' and must carry an anchor.
CREATE TABLE paper_probes (
    record_id TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    field     TEXT NOT NULL CHECK (field IN ('publication_status', 'version_of', 'access_status', 'affiliations')),
    value     TEXT NOT NULL CHECK (trim(value) <> ''),
    provider  TEXT NOT NULL CHECK (trim(provider) <> ''),
    probed_on TEXT NOT NULL CHECK (probed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    anchor    TEXT,
    PRIMARY KEY (record_id, field),
    CHECK (field <> 'publication_status' OR value IN ('published', 'preprint', 'withdrawn', 'retracted')),
    CHECK (provider <> 'hand' OR (anchor IS NOT NULL AND trim(anchor) <> ''))
);

-- Field 6: typed links between SOURCE records, each carrying the sentence
-- that establishes it. Support and contradiction stay between assertions.
CREATE TABLE source_links (
    from_id   TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    to_id     TEXT NOT NULL REFERENCES paper_fields(record_id) ON DELETE CASCADE,
    link_type TEXT NOT NULL CHECK (link_type IN ('code-of', 'dataset-of', 'version-of', 'superseded-by', 'responds-to')),
    evidence  TEXT NOT NULL CHECK (trim(evidence) <> ''),
    PRIMARY KEY (from_id, to_id, link_type),
    CHECK (from_id != to_id)
);

-- ---------------------------------------------------------------------
-- Relations between assertions (ADR-0005 section 2f): `supports` and
-- `contradicts`, with papers as provenance via paper_yields above rather
-- than stored again here.
-- ---------------------------------------------------------------------

CREATE TABLE assertion_relations (
    from_assertion_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    to_assertion_id   TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    relation          TEXT NOT NULL CHECK (relation IN ('supports', 'contradicts')),
    PRIMARY KEY (from_assertion_id, to_assertion_id, relation),
    CHECK (from_assertion_id != to_assertion_id)
);

-- ---------------------------------------------------------------------
-- Indexes for the queries the export and the store's own tooling will run
-- most often: by class, by context, and by paper tier.
-- ---------------------------------------------------------------------

CREATE INDEX idx_records_class ON records(class);
CREATE INDEX idx_record_contexts_context ON record_contexts(context_id);
CREATE INDEX idx_paper_fields_tier ON paper_fields(tier);
