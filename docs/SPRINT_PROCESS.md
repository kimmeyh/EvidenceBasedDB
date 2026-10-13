# Sprint Process (one-page overlay)

The full sprint execution doc set governs this repository, EvidenceBasedDB: **SPRINT_EXECUTION_WORKFLOW.md** (phases 1-8), **SPRINT_CHECKLIST.md** (per-boundary single-pager), **SPRINT_STOPPING_CRITERIA.md**, **SPRINT_RETROSPECTIVE.md** (16x4 protocol), **BACKLOG_REFINEMENT.md** (two passes + presentation format), **ALL_SPRINTS_MASTER_PLAN.md** (backlog + history). This page keeps only the always-loaded essentials.

**REWORKED 2026-09-16 (Sprint 1 Task H, F1).** Removed a Criterion H hardware
override with no equivalent here, decision classes referencing the consumer
repository's frozen preregistration rather than this repository's own ADRs,
and an entire "Sprint calendar" section that was hsbc-quantum-fraud-2026's
own competition-deadline schedule (Aug 30 - Sep 14, referencing IEEE-CIS,
QFE, SPECTRA evidence and a QCi draft package) with no meaning in this
repository, which has no deadline (SPRINT_1_PLAN.md: "No deadline").

## Branch and push model

```
main      (stable release branch; team lead merges develop -> main during Phase 8; each merge tagged sprint-N)
  ^
develop   (integration + repository default; every sprint PR targets it)
  ^
feature/YYYYMMDD_Sprint_N   (one branch per sprint; DRAFT PR from creation; ready only at Phase 7.7)
```

**Release step (F66, ADR-0001 A2, 2026-10-13):** PR develop -> main, merged by the team lead, then tag the merge (`sprint-N`, annotated, created and pushed by Claude on the main-merge notification; workflow 8.1). develop has been the GitHub default branch since the same date, so `Closes #N` closes issues when a PR merges into develop. CI runs on PRs into develop only (team lead, 2026-10-13).

**Merges are team-lead-only, at every level**: Claude never merges any PR -- feature to develop included. Claude's responsibility ends at ready-for-review plus notification; the team lead merges and says when done.

**Carry-forward (workflow 6.6):** on PR-merge notification, create the next sprint branch FROM the just-merged branch's head, never from develop; commit post-merge work there; never stash; recovery is cherry-pick. Sprint branches are never deleted.

Remote: private (`kimmeyh/EvidenceBasedDB`) while ADR-0005's citation constraint applies -- no citation from the public consumer repository may depend on this one resolving while it stays private (CLAUDE.md).

## The window

Auto-advance (no permission-asking) runs from Phase 3.7 plan approval to the start of Phase 5 team-lead validation.

## Decision classes (never covered by sprint approval)

1. Design-decision changes: anything amending an ACCEPTED ADR's spine (record classes, contexts, certainty model).
2. Evidence-claim changes: asserting a certainty level or fidelity higher than a record's provenance supports.
3. Scope changes (de-scoping/deferring approved work).
Surface with the template phrasing; wait.

## Standing rules

- `--no-verify` is banned.
- Repo-root `CHECKLIST-Phase2-pre.md` is the live deliverable ledger, reconciled at every sprint close; ALL_SPRINTS_MASTER_PLAN.md is the sprint-scoping view.
- Every record's `provenance` field is set before commit; determinate facts resolve rather than being stored (CLAUDE.md).
- Team-lead `0*` working files at repo root: commit neutrally, never read.
- **`spamfilter-multi` and `hsbc-quantum-fraud-2026` are READ-ONLY from this repository** (team lead, 2026-09-15): research freely, never write. Hook-enforced by `block_sibling_repo_writes.py`.
