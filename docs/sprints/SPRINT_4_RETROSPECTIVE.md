# Sprint 4 Retrospective: Fix the Path, Fix the Records, Measure the Cost

Held 2026-09-22, after Manual Validation and the F11 timing run. Team-lead
feedback (Product Owner, Scrum Master, Lead Developer combined) given
verbatim; Development Team feedback written before the team lead's was
read on the categories where it differs, and left as written.

## Sprint 4 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Eleven tasks across two sessions on one branch, closed in one day of execution (12:02 to 20:03 local) plus validation items and the timing run. Two read-only Sonnet agents carried the reading for Tasks F and H (199,780 tokens / 472 s and 133,883 / 183 s) while the coordinator wrote the scripts, which is why two 90-to-120-minute estimates landed in 3 and 8 minutes of coordinator wall clock. One real inefficiency: about 90 minutes went into diagnosing arXiv's HTTP 406, and probing in bursts extended the very block being measured.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good, not Very Good. 255 tests to 362 at hand-over (395 after the improvements), 22 test files to 36, and every new guard broken and watched go red -- 16 in Task B, 12 in Task C, 7 in Task G, 5 in the seed-metadata guard. Two lapses on the Development Team's side, both mechanical rather than conceptual. First, a commit landed with the suite red because pytest was piped through `tail`, which discarded its exit code; caught one commit later and now hook-enforced (improvement 1). Second, the two CHANGELOG guards had been parsing one heading of five since Sprint 1 and passed on their own defect for three sprints; they failed only when the calendar moved five days past the seed date, which is luck, not detection. That is the second vacuous-guard failure in this file's own history and it produced the general rule in improvement 2: a guard that parses a file must fail when it parses nothing.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. Plan 785 minutes, all `[no-history]`; actual work came in under that overall, but the distribution was wrong in an instructive way. Task C ran about 1.7x its 90-minute estimate, almost entirely the arXiv diagnosis. Tasks F, G and H came in at a fraction of theirs because delegation overlapped the reading with the writing -- an effect the estimates did not model at all. Estimates that do not distinguish "coordinator wall clock" from "total work including agents" will keep mispredicting in both directions; the Actuals section now records both.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Deciding Q1 through Q5 at approval meant the auto-advance window held for eleven tasks with no stop. The named cut line after Task G was never needed. The sequence (door before any correction passes through it) was right and made Task C's gate meaningful: the door refused four records until the refresh had replaced their Sprint 1 citations, which is the door doing its job on its own authors.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Top tier for the door, the amendments, the context tests and the assertion certainty; Sonnet for read-only evidence gathering, with judgment retained. Both agent reports were verified against the PDFs before use, and one self-flagged a gap it could not reach (two reference-list pages), which the coordinator then read directly to settle the Neven lineage question. The heuristics file now carries these as real outcomes rather than zeros (improvement 8), and the lesson it records is the one worth keeping: reading parallelises, judgment does not.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The status footer held every turn and is now script-generated after last sprint's stale-timestamp correction. Two misses, both corrected by the team lead in the moment. The first Manual Validation list contained six steps that were the Development Team's own verification work (test runs, dry runs, spot-checks) and two that were genuinely the team lead's; the rule that followed is now in the workflow and the checklist (improvement 7). And Q7 asked the team lead for a URL as though from perfect recall, when the right move was to state what the repository held first -- which, when asked properly, produced the answer in one turn.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. F25's framing -- "not just the DB entries need to be fixed, but a plan to ensure that the next paper is incorporated correctly on first try" -- settled every scope question inside the sprint without a further ask. The first-try proof exists because the requirement named it.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Three dated ADR amendments (ADR-0005 A2 and A3, ADR-0004 A5), none an edit in place, every count time-scoped. `docs/INTAKE_WORKFLOW.md` is a real design document that governs a real script, and its section 8 context tests were written before the pass they governed, which is the order that makes a test a test. The one documentation defect: the CHANGELOG sat oldest-first for three sprints against its own stated policy, unnoticed because its guard could not read it.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Good. The remote session's Criterion 2 stop was handled exactly as written: it documented the block on the issue with evidence, continued the unblocked tasks, and named what would unblock it. The gap was on the other side -- this session discovered the parallel work only when its push was rejected, and then had to reconstruct four tasks' worth of state from commits and an issue comment. The status note turned out to be the hand-off channel and is now read at every task start, not after a collision (improvement 4). Separately, three repository hooks blocked legitimate commands and cost about six turns; one of them (the escape hook) was blocking on a pattern that matched ordinary prose, now fixed with tests pinning all three false positives (improvement 5).

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Every write-shaped script ran dry by default and printed its plan; the correction script pushed all 48 records back through the door's validator inside the transaction and rolled back on any refusal; the schema change was one migration with a byte-identical export as its acceptance test; `--verify` gave the first-try claim something to mean. Nothing was written to the live store this sprint without a dry run first.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. The bulk set is on disk with per-year manifests and the intake design says how it loads; the two Class 1 decisions are recorded where the next planner will find them; F28 (learning from the papers) and F29 (cold-mode timing) are carded with their dependencies stated.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. `paper_fields.citation` dropped and the read-tier CHECK added in a single rebuild with the foreign-key closure walked; the export layer's N+1 queries batched without changing a byte of output; the citation module gained a third provider kind without the callers changing. The store's founding defect -- one value restated in three columns -- is now zero of 48 rows.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none beyond the eight improvements, all implemented this sprint.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: F29 (cold-mode adjudication timing) carded from the F11 result. The `paper_fields.kind` column and the ISBN resolver were already recorded as Class 1 decisions in the intake design.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Very Good. Both evidence agents returned exactly the structure requested, with page anchors, stayed read-only, and flagged rather than papered over what they could not reach. The remote session delivered four tasks with tests and injection proofs and stopped correctly on the fifth. No agent report was taken on trust; each was checked against the files or the repository state before use.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Combined summary

Team lead: Very Good on all thirteen categories scored. Development Team:
Very Good on nine, Good on four (Testing Approach, Effort Accuracy,
Communication, Process Issues), each Good attached to a specific named
lapse rather than a theme.

What the sprint delivered against its own title: the path fixed (a single
guarded door, one intake for every source type, a mechanized first-try
check), the records fixed (48 papers, 87 anchored rationales, 6 at `read`,
the first `contradicts` relation), and the cost measured (1.08 team-lead
minutes per corrected record, with the confirm-mode caveat recorded rather
than glossed). What it found on the way: two guards that had never
guarded, an API that refuses the batch shape its own documentation
offers, and a 1,618-file bulk set arriving a sprint early.

## Improvement Decisions

All eight proposed improvements were approved by the team lead on
2026-09-22 ("all 8 now") and implemented the same day in `6037bc9`.

1. **Commit gate on the suite's exit code** -- IMPLEMENTED.
   `.claude/hooks/block_commit_with_piped_tests.py`, registered
   structurally on the `Bash|PowerShell` matcher, 15 tests, the real
   offending command as its first case. Blocks only when a test run, a
   pipe on that run, and a `git commit` appear in one command.
2. **Guards that read nothing must fail** -- IMPLEMENTED.
   `test_every_section_heading_carries_a_parsable_date` makes the parse
   itself the assertion. Injection: an undated heading turns the new test
   red while both guards it protects stay green.
3. **Pre-flight the production request shape** -- IMPLEMENTED.
   `docs/SPRINT_PLANNING.md`, with the arXiv batch-refusal as the worked
   example and the pacing rule for follow-up probes.
4. **Two-session protocol** -- IMPLEMENTED.
   `docs/SPRINT_EXECUTION_WORKFLOW.md` Phase 4: fetch and read the other
   session's status note at every task start; a rejected push is a
   hand-off signal, not a git problem.
5. **Hook precision** -- IMPLEMENTED. `block_unraw_escape.py` now requires
   a real drive letter; 9 tests pin the true positive, the three Sprint 4
   false positives and every correct form. Worth recording how it was
   found: two plausible diagnoses (a quote-boundary bug, then a
   segment-scoping bug) were both wrong and both were caught by re-running
   the probe rather than by reasoning; the fix came from printing the
   literal the hook actually flagged.
6. **Timing runs as a tool, and the open number** -- IMPLEMENTED.
   `scripts/adjudication_timing.py` with 8 tests, recording the protocol
   mode because confirm and cold are different numbers; F29 cards the cold
   measurement.
7. **Checklist line for Manual Validation scope** -- IMPLEMENTED.
   `docs/SPRINT_CHECKLIST.md` Phase 5 now mirrors the workflow rule.
8. **Heuristics learning_log** -- IMPLEMENTED. Sprint 4's delegation
   outcomes recorded with tokens and seconds; two protocols defined
   properly after the file's own guard refused inline names; three
   task_patterns raised from sample_size 0 to real outcomes.

Suite 362 to 395 passed. Every new guard proven to fail by injection.
