# Sprint Execution Workflow

Adapted 2026-08-30 from spamfilter-multi's SPRINT_EXECUTION_WORKFLOW.md via hsbc-quantum-fraud-2026 (each adaptation kept the hard-won rules and replaced the previous project's specifics with its own). This is the authoritative step-by-step sprint process for **this repository, EvidenceBasedDB**.

**REWORKED 2026-09-16 (Sprint 1 Task H, F1).** The version inherited at seeding still described itself as hsbc-quantum-fraud-2026's own process and carried that repository's Dirac-3 hardware-approval rule, its `experiments/src` test path, its `results.json`/`prereg-freeze` artifacts, and its submission-document approval gate -- none of which exist or apply here. The sprint MECHANICS (issue-per-task, draft-PR discipline, carry-forward, retrospective protocol, backlog format) are this repository's own real process and are unchanged; what changed is removing content that told a session to wait for approvals, run commands, and check artifacts that do not exist in this repository.

## SPRINT EXECUTION Documentation

| Document | Purpose |
|---|---|
| **ALL_SPRINTS_MASTER_PLAN.md** | Master plan: past sprint summary, last completed sprint, next sprint candidates, item details |
| **SPRINT_EXECUTION_WORKFLOW.md** (this doc) | Step-by-step execution checklist (Phases 1-8) |
| **SPRINT_CHECKLIST.md** | Single-page phase checklist consulted at every boundary |
| **SPRINT_STOPPING_CRITERIA.md** | When and why to stop working |
| **SPRINT_RETROSPECTIVE.md** | Retrospective protocol and the 16x4 template |
| **BACKLOG_REFINEMENT.md** | Refinement passes and the authoritative presentation format |
| **SPRINT_PROCESS.md** | One-page overlay: branch model, carry-forward, standing rules |
| **CHECKLIST-Phase2-pre.md** (repo root) | The submission-wide task ledger (Phase 1 deliverable map) |
| **experiments/PREREGISTRATION.md** | FROZEN protocol; amendment discipline overrides everything here |

## Phase Cheat Sheet

Consult this line at the START and END of every phase; state which steps were done. Crossing a boundary by "just doing the next work" is how steps get missed.

| Phase | Top actions | Done when |
|---|---|---|
| **1. Backlog Refinement** | MANDATORY every sprint, no request needed. Read master plan + CHECKLIST-Phase2-pre.md; present candidates in BACKLOG_REFINEMENT.md format (read its format section IN THE SAME TURN first); capture selection | Team lead has picked items; no scope questions open |
| **2. Sprint Pre-Kickoff** | Verify previous PR merged; sprint issues closed; working tree clean; develop current; tests green (`pytest -q`) | All gates green |
| **3. Kickoff & Planning** | Draft `docs/sprints/SPRINT_N_PLAN.md`; verify plan against branch state (3.2.2.1); create GitHub issue per task + DRAFT PR (3.3.1); get explicit 3.7 approval | Team lead says "plan approved" -- durable authorization for Phases 4-7 |
| **4. Execution** | Implement tasks in plan order; run `pytest -q` after each; commit with issue number; every record carries provenance | All acceptance criteria met; tests green |
| **5. Review & Validation** | Full test suite; committed export matches a fresh regeneration from the store (`tests/test_export_currency.py`); walk plan acceptance criteria line by line with evidence; hand to team lead for manual validation | Team-lead validation feedback addressed |
| **6. Push & Finalize PR** | Push branch; UPDATE the draft PR body (keep DRAFT); on merge notification, IMMEDIATELY create next sprint branch FROM THE CURRENT FEATURE BRANCH (6.6) | PR updated, still draft; next branch created on merge |
| **7. Retrospective** | 7-step protocol per SPRINT_RETROSPECTIVE.md (16 categories x 4 roles); apply-now improvements committed; THEN `gh pr ready` (the ONE place); notify team lead for final approval | Retro doc committed; PR ready; team lead notified |
| **8. Delivery Cycle** | After develop merge: team lead merges develop->main in parallel with Refinement Pass 1 (completeness sweep); submission-artifact refresh if due (see below); Refinement Pass 2 (scope selection) | Master plan rolled; next scope selected |

## Invariants (all phases)

1. **Auto-advance window**: between Phase 3.7 approval and the start of Phase 5's team-lead validation, do NOT ask permission at task or phase boundaries; state the next action in one sentence and execute. Before approval, asking is REQUIRED. From validation onward, asking is CORRECT. Commits, pushes, PR-body updates, and test runs are within standing approval.
2. **Stop only** for the criteria in SPRINT_STOPPING_CRITERIA.md; never for implementation choices, approach uncertainty, or "confirming the next step".
3. **Open-the-file verification**: before reporting any checklist section, phase, or close-out complete, OPEN the governing checklist in the same turn and walk it line by line: `DONE (<evidence>)`, `N/A (<why>)`, or `NOT DONE -> doing it now`. "I believe I did that" is not verification.
4. **User-request inventory**: a message with multiple asks is a CHECKLIST, not a theme. Enumerate every discrete ask before starting; restate each with its status before ending the turn. A terminal condition ("continue until X") is itself an ask.
   - **A repeated instruction means MY READING is wrong, not the instruction.** If the team lead issues an instruction I believe I have already satisfied, do not execute the same interpretation again. State the reading back in one sentence and act on the other plausible reading.
5. **Read the format doc before producing its output**: retrospective template, backlog presentation format, plan template. Mirror exactly; never reproduce from memory.
6. **Decision-Class Checkpoint Protocol**: sprint-plan approval is NOT authorization for (Class 1) design-decision changes -- anything amending an ACCEPTED ADR's spine (record classes, contexts, certainty model); (Class 2) evidence-claim changes -- asserting a certainty level or fidelity higher than a record's provenance supports; (Class 3) scope changes -- de-scoping or deferring approved work. STOP, surface with the template phrasing ("This would change ...: [what]. Should I proceed?"), WAIT. Anti-pattern signals: "it is just a small change", "I will mention it in the retrospective", "we are running out of time, I will defer Z".
7. **VERIFY BEFORE AMENDING.** A review finding -- internal or external, from a person or a model -- is NOT actionable until independently verified against the code or the artifact it describes. Corrections to an ACCEPTED ADR are recorded as dated amendments at the bottom, never as edits in place (CLAUDE.md "Early innovation: expect revision").
   - Corollary: **correcting a document does not correct its generator.** When an amendment corrects a claim, check the code that produces that claim's evidence, not only the prose stating it.
8. **If Phase 1 was skipped for a sprint, STOP and return to it** before any Phase 4 work.

## Phase detail (adaptations from the source; consult spamfilter's doc for rationale history)

### Phase 1: Backlog Refinement (mandatory, every sprint)
- 1.1 Read ALL_SPRINTS_MASTER_PLAN.md and repo-root CHECKLIST-Phase2-pre.md; identify stale/obsolete items; re-prioritize.
- 1.2 Present candidates in the BACKLOG_REFINEMENT.md "Backlog Presentation Format" -- Summary Index first, `**<ID>. <Title> (~<effort>) Priority <N>**` items, phase-group headers, HOLD one-liners, no grid tables, real registered IDs (F#/Issue #N). Read the format section in the same turn before producing it.
- 1.3 Record selection; update master plan; commit.

### Phase 2: Sprint Pre-Kickoff
- 2.2 Previous sprint PR merged to develop (`git log origin/develop --oneline -1`). Branch retention: NEVER delete sprint branches, local or remote.
- 2.3 Previous sprint's GitHub issues all closed (`gh issue list --label sprint --state open`); `Closes #N` does NOT fire on feature->develop merges, so close manually.
- 2.4 Working tree clean. 2.5 develop current.
- 2.6 Dependency check: `uv pip list --outdated` scan; security-relevant bumps become scope or backlog items.

### Phase 3: Kickoff & Planning
- 3.2.1 **Three-doc rule, no exceptions**: every completed sprint has SPRINT_N_PLAN.md, SPRINT_N_RETROSPECTIVE.md, AND SPRINT_N_SUMMARY.md. The summary is created during Sprint N+1 planning (sources: retrospective, git history, PR; never the already-rolled master plan) and its absence blocks close-out. **The summary carries an `## Actuals` section** (Sprint 3 retrospective improvement 2): per task, wall-clock from the previous task's commit to this task's commit (derived from `git log`, not remembered), and for any delegated subagent its reported tokens and duration. Three sprints ran with every estimate `[no-history]` because actuals were never written down in a form the next plan could read; SPRINT_PLANNING.md's "record actuals at task completion" was a rule with no artifact behind it.
- 3.2.2 Plan doc with objective, tasks, acceptance criteria (quantifiable), risk, estimates in MINUTES.
- 3.2.2.1 **Plan-to-branch-state verification**: before committing the plan, verify each task against the repo (artifact exists? already shipped? cited paths current?). 3.2.2.2 Re-estimate after findings.
- 3.3 Branch `feature/YYYYMMDD_Sprint_N` -- normally ALREADY CREATED by the previous sprint's 6.6 carry-forward; verify, do not duplicate.
- 3.3.1 **Draft PR immediately after the plan is drafted, before approval. The PR STAYS DRAFT through Phase 7.7.** Draft status suppresses Copilot per-commit reviews; marking ready early = review noise on every push. `gh pr ready` happens at exactly one place: end of 7.7.
- 3.4 One GitHub issue per task (`sprint` label), created in the SAME turn as approval acknowledgment, before any task file is touched. 3.4.1 Verify each issue is still real. 3.5 All cards OPEN.
- 3.7 Explicit approval; update PR body to approved plan (keep draft).

### Phase 4: Execution
- Tasks in plan order; `pytest -q` after each change; commit referencing the issue (`#N`).
- `git status --short` before every staging; account for every entry. Team-lead working files (`0*` at root) are EXPECTED to change and be committed with a neutral message; never read, paraphrase, or exclude them.
- Provenance discipline: every record's `provenance` field is set before the record is committed; a record that cannot say where its value came from is the defect this whole system exists against (CLAUDE.md).
- **A delegated task's report is verified against repository state before it is trusted OR dismissed** (Sprint 3 retrospective improvement 3). Check `git log`, the files it names, and the issue it closes; a subagent or fork cannot commit under this session's identity, so a claimed commit either exists or the report is wrong. In Sprint 3 a fork's accurate completion report was briefly distrusted after a context compaction hid the turn in which its work had been committed -- the fix was `git show <hash>`, not a judgment about the messenger.
- **Write-shaped one-off scripts run dry by default** (Sprint 3 retrospective improvement 1; convention in QUALITY_STANDARDS.md). Show the diff or the planned change list first; write only on an explicit `--apply`. Review the dry-run output against the frozen-document rules (ADR amendments, sprint docs) before applying.

### Phase 5: Review & Validation
- **Before declaring Manual Validation ready, run `gh issue list --label sprint --state open` and account for every result.** Added 2026-09-17 (Sprint 2 retrospective improvement 1) after issues #13 and #15 stayed open despite `Closes #N`-style commit messages referencing them on the feature branch -- `Closes #N` only auto-fires on merge to develop, a gap this document already named (2.3) before it recurred anyway. Documenting a gap is not the same as checking for it; this step makes the check mechanical rather than triggered only if the team lead happens to ask.
- Full test suite; committed export matches a fresh regeneration from the store (`tests/test_export_currency.py`) -- the export is the artifact (ADR-0004 section 2), and a stale export is the same defect class as an unrun regeneration.
- **Evidence-generating steps invalidate their own verification.** Any checklist walk, memo, or summary is generated AFTER the last piece of evidence lands, never before. A verification artifact written mid-task is stale by construction and must be regenerated, not referenced.
- **Fresh-eyes review before a major structural change lands** (schema, contexts, resolvers): a fresh-context reviewer (subagent or fresh session with no task context) reads the raw change with an open prompt ("describe; any useful observations?"); findings attach to the validation package. The invested session knows what a change is supposed to mean; fresh context describes what it actually does.
- Walk the sprint plan's acceptance criteria line by line with evidence (invariant 3).
- Hand deliverables to the team lead for manual validation; from here on, questions are correct.

### Phase 6: Push & Finalize PR
- 6.3 Update the existing draft PR (never create a second). 6.5 interim status to the team lead, NOT "ready".
- 6.6 **Carry-forward**: on merge notification, immediately `git checkout -b feature/<date>_Sprint_<N+1>` FROM the current feature branch; commit post-merge work there; push. NEVER stash to carry forward; never branch from develop after the merge (loses uncommitted work; the recovery is cherry-pick onto a develop-cut branch and reset the merged branch to its pushed head).
  - **Both clauses are hook-enforced** (`.claude/hooks/`): `block_carry_forward_stash.py` blocks `git stash`, `block_branch_from_develop.py` blocks a `checkout -b`/`switch -c` that names develop, main or master as the start point. Bare `git checkout -b <name>` is the prescribed form and passes; both hooks carry a sanctioned bypass token for the genuine exception. (Converted from `.ps1` to `.py` 2026-09-14; see QUALITY_STANDARDS.md amendment.)
  - **A clean result does not mean the cut was right.** At the Sprint 9 close-out the branch was cut from `origin/develop`; no commits were lost, because the merge had already carried everything and the uncommitted work followed the checkout. The violation was invisible in `git status` and surfaced only on re-reading this rule. Verify the flow, not the outcome.

### Phase 7: Retrospective (mandatory before merge-ready)
- Follow SPRINT_RETROSPECTIVE.md's 7-step protocol: prompt to team lead -> Claude drafts its role's feedback in parallel (`docs/sprints/drafts/`) -> record team lead's words verbatim -> combine and display -> propose improvements (Title/Source/Type/Effort/Recommendation) -> team lead disposes each (now/backlog/skip) -> apply now-items as commits, backlog-items to master plan.
- Exit gate: 16 categories x 4 roles, no placeholders; Category 13 feeds Sprint N+1's plan; Category 14 feeds the master plan.
- **Merge-readiness definition (team lead, 2026-09-04)**: a PR is handed to the team lead as merge-ready ONLY when EVERY review has COMPLETED and EVERY finding is addressed and its thread resolved. A review still running means the PR is not ready, no matter how clean it looks; never describe it as "yours to merge" while an agent is mid-review. State review status explicitly instead: which reviews are complete, which are running, how many findings are open.
- End of 7.7: `gh pr ready` (the only place). 7.7.5 final gate: manual validation + retro + improvements + Copilot review all complete -> notify team lead for final approval.
- **Requesting the Copilot review (CORRECTED 2026-09-12, F66).** This has three independent silent-failure modes, and the earlier note in this document recorded the workaround while misdiagnosing the cause.
  - **The actor name is `copilot-pull-request-reviewer[bot]`** (node id `BOT_kgDOCnlnWA`). NOT `Copilot`, and NOT `copilot-swe-agent`, which is a different bot. `gh pr edit --add-reviewer Copilot` reports success and attaches nothing, because it resolves a user named Copilot that does not exist on the repository.
  - **`requestedReviewers` cannot confirm a bot request.** The REST field returns USERS only, so a bot reviewer that attached correctly still reads back as an empty list. Verifying there produces a false negative every time, which is what made the first failure mode look like a second one.
  - **Verify on the TIMELINE instead**: the PR shows "Copilot started reviewing" / "Copilot reviewed", or `gh pr view <N> --comments` shows the review body. That is the only reliable confirmation.
  - **Consequence, recorded because it actually happened**: PR #73 never received a Copilot review. The request was issued, reported as successful, verified against a field that cannot show it, and nobody noticed until PR #75 was being set up. A review step that silently does not happen is worse than one that visibly fails.
  - **The working request path, verified 2026-09-14 on PR #94**: the GraphQL `requestReviews` mutation with the bot id in `botIds`, NOT `userIds`. `userIds` fails loudly with "Could not resolve to User node", which is at least honest. **The REST call fails SILENTLY**: `POST /pulls/{n}/requested_reviewers` with the bot login returns HTTP 200 and a full PR object, and attaches nothing. That is a fourth silent-failure mode beyond the three already listed.
    ```
    gh api graphql -f query='mutation($pr:ID!){requestReviews(input:{pullRequestId:$pr, botIds:["BOT_kgDOCnlnWA"], union:true}){pullRequest{number}}}' -f pr="<PR node id>"
    ```
  - **Verify with GraphQL `reviewRequests`, never REST.** REST's `requested_reviewers` showed an EMPTY array while GraphQL showed `Bot: copilot-pull-request-reviewer` attached. The timeline also showed no `review_requested` event for the bot, so the timeline check in the line above is necessary but NOT sufficient. A cross-repository skill holds the full procedure; this note exists so the workflow does not depend on that skill being loaded.
- Update `.claude/sprint_status.json` `current_sprint.status` at every phase transition (it is how future tooling knows which side of the auto-advance window applies).

### Phase 8: Delivery Cycle (after every merge to develop)
- 8.1 Team lead merges develop -> main (do not wait on it; do not block Refinement Pass 1 on it).
- 8.1.1 **CHANGELOG reconciliation, BEFORE refinement (F70, Sprint 14).** Walk the days since the last entry and write one per day with commits, sourced from git history, the sprint summaries, the amendment log and the merged PRs. A day that cannot be reconstructed with confidence says so rather than being invented.
  - **Why this step exists and why it sits here.** The policy at the top of CHANGELOG.md says entries are written in the SAME commit as the change they describe. That policy held for six days and then silently stopped: the file ran from 2026-08-29 to 2026-09-04 and then nothing, while Sprints 7 through 13 delivered the entire hardware campaign, three external reviews, the public-repository flip and the submission itself. Eight days missing, and nobody noticed for eight days.
  - A same-commit policy depends on remembering at the moment of committing, which is exactly the class of rule this workflow keeps having to replace with a step. The reconciliation is cheap when it runs every cycle and expensive once it has lapsed -- the F70 backfill cost about ninety minutes for eight days.
  - It is placed BEFORE Refinement Pass 1 deliberately: the sweep reads the sprint's own record, and a record with a hole in it is what the sweep is meant to catch.
- 8.2 **Refinement Pass 1, completeness sweep**: verify cards closed, docs triad exists, master plan rolled, sprint_status current, shipped items pruned. Corrections only; NEVER selects scope.
  - **Prune shipped cards BY HAND. Do not write a pruning script.** An ad-hoc prune script destroyed a master plan's roadmap section TWICE in the consumer repository's own history, by walking from a card header to the next card header and consuming a `## ` section heading that fell inside the span (a lesson this repository inherits without inheriting the incident's own commit hashes). Pruning is a handful of cards per cycle; the script has negative value at that volume. Delete the card block with an editor, then run `pytest -q` before committing.
- 8.3 **Design-document currency check**: if the sprint changed anything ADR-0004 or ADR-0005 describe, verify the ADRs still match the actual schema and export -- and if they do not, that is a finding for the 20-paper checkpoint (F75), not a silent doc edit.
- 8.4 **Refinement Pass 2, scope selection**: present the slate per BACKLOG_REFINEMENT.md; the team lead selects; feed Phase 3.
