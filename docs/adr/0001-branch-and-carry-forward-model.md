# ADR-0001: Branch and carry-forward model for sprint work

## Status

Accepted

## Date

2026-08-30

## Context

The project runs the sprint process adapted from spamfilter-multi, across many AI sessions, with a solo team lead holding release authority. Process decisions evaporate fastest in exactly this setup; the source repo's experience (its ADR-0015) shows that writing the branch policy down is what keeps an AI-assisted workflow safe.

## Decision

- Three tiers: `main` (stable; team-lead-only merges from develop), `develop` (integration, repository default; all PRs target it), `feature/YYYYMMDD_Sprint_N` (one per sprint).
- One DRAFT PR per sprint, created when the plan is drafted, kept draft through the retrospective, marked ready at exactly one point (workflow Phase 7.7). Draft status suppresses per-commit Copilot review noise.
- Carry-forward: on PR-merge notification, the next sprint branch is created FROM the just-merged branch's head, never from develop; post-merge work commits there. Stash is banned; recovery is cherry-pick.
- Sprint branches are never deleted.
- An ACCEPTED ADR's spine changes only with a dated amendment at the bottom of the ADR, never a silent edit, on any branch (CLAUDE.md "Early innovation: expect revision").
- Scope is DEFINED, never additive: the team lead's selection list is the complete sprint scope (SPRINT_PLANNING.md defined-scope rule, 2026-08-30).
- Team-lead-owned tasks blocked at sprint close carry per stopping Criterion 2 without holding the sprint.

## Alternatives Considered

### Trunk-based development (commit to main)
- **Pros**: Less ceremony for a solo project.
- **Cons**: No integration buffer, no PR surface for Copilot review, no draft/ready lifecycle, diverges from the team lead's established practice.
- **Why Rejected**: The team lead's proven model transfers wholesale and its guard rails have already caught real mistakes here.

## Consequences

### Positive
- Every sprint has an auditable PR trail; nothing strands on merged branches.
### Negative
- Solo-project ceremony overhead, accepted deliberately for auditability.
### Neutral
- This repository stays private while ADR-0005's citation constraint applies, so branch history here does not need to satisfy a public audience.

## Related design documents

None directly. ADR-0004 (Evidence Based DB) and ADR-0005 (reference library) govern the schema and record classes this repository stores; this ADR records the branch/process model only, independent of the schema.

## References

`docs/SPRINT_PROCESS.md`; `docs/SPRINT_EXECUTION_WORKFLOW.md` 3.3.1 and 6.6; `docs/SPRINT_PLANNING.md` defined-scope rule; spamfilter-multi ADR-0015.

## Amendments

**2026-09-16 (A1): Removed hsbc-quantum-fraud-2026 process leakage
(Sprint 1 Task H, F1).** This ADR's title heading read "ADR-0004" (its
number in some earlier draft or the consumer repository's own sequence)
while the filename and this repository's ADR README both call it ADR-0001
-- corrected to match. The "Preregistration touchpoints" section, which
referenced a frozen preregistration this repository does not have, is
replaced with "Related design documents" naming this repository's own
ADR-0004 and ADR-0005. The `experiments/src/` reference in the Decision
section is replaced with the general ACCEPTED-ADR-amendment rule
CLAUDE.md already states.

**2026-10-13 (A2): The GitHub default branch now matches this ADR, and
each release to main is tagged (Sprint 8 Task A, F66).** The Decision
section has named develop the "repository default" since this ADR was
written, but the GitHub setting was still `main` until 2026-10-13. Two
effects followed, and both are corrected:
*(a)* **The setting.** `gh repo edit --default-branch develop`, then
`git remote set-head origin -a`, on 2026-10-13. New PRs now open against
develop by default, and `Closes #N` in a PR merged into develop closes the
issue (GitHub closes linked issues only on a merge into the default
branch). Workflow 2.3 and Phase 5 said the opposite and are corrected; the
open-issue check stays as a backstop.
*(b)* **The release step.** PR develop -> main, merged by the owner, then
tag the merge: an annotated tag `sprint-N` on main's merge commit, which
Claude creates and pushes on the main-merge notification (workflow 8.1).
The seven earlier releases were tagged `sprint-1` to `sprint-7` the same
day (PRs #10, #19, #29, #42, #53, #67, #76; each carried exactly one
sprint's PR).
*(c)* **Not changed, by decision.** CI keeps running on PRs into develop
only. F66's card asked for CI on PRs into develop and main; the team lead
declined that change and a test guarding it (Sprint 8 Manual Validation,
2026-10-13). No branch protection was added: on this private repository's plan GitHub
answers 403 to the protection API.
*Revisit when* a release to main is made from anything other than develop,
or the repository becomes public (then branch protection becomes
available).
