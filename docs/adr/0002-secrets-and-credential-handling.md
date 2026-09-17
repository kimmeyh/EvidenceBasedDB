# ADR-0002: Secrets and credential handling

## Status

Accepted

## Date

2026-08-30 (records practice established Aug 29-30; content reworked 2026-09-16, Sprint 1 Task H, F1 -- see Amendments)

## Context

This repository touches at least one credentialed service directly (GitHub,
`gh` CLI) and may touch others as record-ingestion tooling grows (a paper
database API, an arXiv/DOI resolution service). A leaked credential in a
repository whose visibility may change (CLAUDE.md: private while ADR-0005's
citation constraint applies, revisit if it ever goes public) is a real
exposure even while private, since git history persists past a visibility
change.

## Decision

- Credentials NEVER live in the repository. Locations of record: OS user
  environment or OAuth caches in the user profile (`gh` keyring); project
  `.env` (gitignored) only for run-scoped variables, loaded via
  python-dotenv, if a future ingestion script needs one.
- `.gitignore` pins the credential file names (`.env`, `credentials.json`);
  a pre-commit hook hard-blocks staged `.env` files and content matching a
  gitignored secrets-pattern file, so patterns never enter history.
- Credential VALUES are never pasted into chat, logs, commit messages, or
  committed records; scripts log key NAMES and presence booleans only.
- One credential system per service: legacy and new-style credentials must
  not coexist for the same service, since a silently-overriding legacy
  credential is a defect class that costs real debugging time to diagnose
  (an incident of this exact shape cost the consumer repository two failed
  download cycles before the legacy pair was found and removed).
- Before this repository's visibility could ever change from private to
  public, a confidentiality scan re-verifies all of this repo-wide first.

## Alternatives Considered

### Committed encrypted secrets (git-crypt or SOPS)
- **Pros**: Reproducible environments from clone.
- **Cons**: Key management burden for a solo maintainer; encrypted blobs in a to-be-public repo invite scrutiny; no need since only one machine runs the work.
- **Why Rejected**: Out-of-repo storage is simpler and strictly safer for this project's shape.

## Consequences

### Positive
- A public snapshot of the repo at any commit contains zero credential material by construction, not by cleanup.
### Negative
- Fresh-environment setup requires manual credential provisioning (documented per service in README).
### Neutral
- The hook's text patterns need occasional curation (one false positive already handled by moving filename guards to .gitignore).

## References

`.gitignore`; `.git/hooks/pre-commit`.

## Amendments

**2026-09-16 (A1): Removed hsbc-quantum-fraud-2026 process leakage
(Sprint 1 Task H, F1).** This ADR's title heading read "ADR-0011" (its
number in the consumer repository) while the filename and this
repository's ADR README both call it ADR-0002 -- corrected to match. The
Context and Decision sections named QCi Dirac-3, Kaggle, "the challenge
portal," and a reserved-numbering note for consumer-repository sprint
candidates, none of which exist or apply here; rewritten to describe this
repository's own credential surface (currently just GitHub/`gh`) and the
GENERALIZABLE discipline (no credentials in-repo, one credential system
per service, a pre-commit secret scan) without the consumer-specific
service names. "Stage 7 confidentiality scan" and "Preregistration
touchpoints" -- both referring to that repository's own submission
timeline -- are replaced with this repository's own private-to-public
visibility-change trigger (CLAUDE.md, ADR-0005's citation constraint).
