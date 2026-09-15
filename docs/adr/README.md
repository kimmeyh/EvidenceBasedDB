# Architecture Decision Records

One decision per record. Status is `Proposed`, `Accepted`, `Deprecated` or
`Superseded by ADR-NNNN`.

**Once Accepted, an ADR is not edited in place.** A changed decision gets either
a dated amendment section at the bottom, or a new superseding ADR. Which one
applies is stated in the ADR itself; the two design ADRs here carry
early-innovation status and prescribe amendments.

| ADR | Decision | Status | Date |
|---|---|---|---|
| [0001](0001-branch-and-carry-forward-model.md) | Branch model and carry-forward discipline | Accepted | 2026-09-14 (seeded) |
| [0002](0002-secrets-and-credential-handling.md) | Secrets and credential handling | Accepted | 2026-09-14 (seeded) |
| [0003](0003-store-and-schema-discipline.md) | Store and schema discipline | Accepted | 2026-09-14 (seeded) |
| [0004](0004-evidence-based-db.md) | Evidence Based DB: SQLite plus committed export, record classes, contexts, escalating reading level | **Accepted** (early innovation) | 2026-09-13 |
| [0005](0005-reference-library.md) | Reference library: papers are SOURCES OF ASSERTIONS; records not PDFs; GRADE-derived certainty | **Accepted** (early innovation) | 2026-09-14 |

ADRs 0001 to 0003 were seeded from `hsbc-quantum-fraud-2026` and renumbered.
0004 and 0005 were written there as 0014 and 0015 and MOVED here, because they
are this repository's design rather than that one's. The originals remain there
as the record of when the decision was made; this repository holds the live
copies.
