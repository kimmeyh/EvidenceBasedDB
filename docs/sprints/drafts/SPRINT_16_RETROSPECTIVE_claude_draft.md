# Sprint 16 Retrospective: Claude's draft (Development Team)

Drafted 2026-11-07 while the team lead writes the PO, SM and LD feedback.
Counts are a snapshot as of 2026-11-07.

### 1. Effective while as Efficient as Reasonably Possible

All eight tasks (A to H) delivered. F114's 20 papers were read in full
and applied in six groups, each with a trial, a verified backup, a live
apply and a second apply that wrote nothing; assertions went from 34,897
to 36,209. The "once" work held for the scripts: 0 text-cache misses,
and every second apply checked no quote. It did not lower the agents'
cost: per page, readers rose 27% in tokens and 70% in minutes, and
reviewers 92% and 74%, against Sprint 15. Rework: two reviewers were
sent back (Monaco's supplement, Heimann's appendices), and the gate ran
INVALID while readers wrote telemetry.

### 2. Testing Approach

Every new guard was proven red by injection, including the seventh
assertion's reason check. The full suite before Manual Validation
failed 1 of 1,578 on a test that pinned a tier the planned reads
changed: a stale data pin, not a defect. The suite itself is the larger
finding: 199 s warm in Sprint 12, about 25 minutes in Sprint 14, and
68:43 now. `--changed` ran 82 files (45:49) after a store write. F140
carries the analysis.

### 3. Effort Accuracy

Not yet measured; the Actuals go in SPRINT_16_SUMMARY.md from the
telemetry files, the commit times and the task notes. The F114 reads
have no estimate by rule (no reading budget). The suite runs and the
two reviewer re-runs are the main unplanned time.

### 4. Planning Quality

The plan put Task B's measure on the first group before the others,
which gave a clean falsifier: the premise that "once" would lower agent
cost was false. The plan did not foresee that every reader check writes
telemetry into the repository, so no gate could run while a reader
worked.

### 5. Model Assignments

Sonnet readers read every page with 0 check problems. Two Sonnet
reviewers fell short on long proof appendices: one graded Monaco's
70-page supplement from statements, one left 7 Heimann appendices
unread. Splitting Monaco across two fresh reviewers by page worked
(13 of 94 decisions changed). Fresh-eyes reviewers found a real defect
each time, including the seventh assertion's misplaced caveat.

### 6. Communication

The Manual Validation hand-over carried every step and question in
full; the team lead's follow-up (assertions cut off in the paper view)
was answered with a working command and carded as F141. Weak points:
the "CI is green" message referred to an older commit, which needed a
correction, and the status field took two commits to reach Phase 5.3.

### 7. Requirements Clarity

The scope was clear. The hidden requirement: a paper that gives two
reasons in one stored value needs a split, which the pipeline had no
table for; the coordinator added the item to the read by hand (MV
Q1 = 3).

### 8. Documentation

INTAKE sections 72 to 74, the CHANGELOG and the sprint status were
updated with each commit, with snapshot dates on counts. F140 and F141
carded. The seventh assertion's no-`contradicts` choice is stated the
same way in the script, the reason, INTAKE and the test.

### 9. Process Issues

- Reader telemetry writes into the repository block every gate (INVALID
  verdicts).
- A telemetry save failed under a file lock, left a .partial file and
  lost one g155 render step.
- `read_telemetry.totals` counted trials and empty re-applies (fixed).
- The pipeline has no sign-off table to add an assertion, so a split
  edits reader output by hand.
- `current_sprint.status` and the top-level `status` are two fields; the
  footer reads the first.

### 10. Risk Management

The trial-then-live-then-second-apply pattern held on every write, and
every escalation waited for the team lead. Materialized: reviewer depth
on long appendices (mitigated by re-review), and gate blocking by
telemetry (worked around by waiting). Disclosed slip from Task A to H:
F, G and H were applied before their fresh-eyes reviews.

### 11. Next Sprint Readiness

F114's next 30 papers, F140 and F141 are carded. F140 should run first:
every Sprint 17 gate pays the slow suite.

### 12. Architecture Maintenance

No schema change and no ADR amendment this sprint. Task E's merge of
the two Dunjko records went through a shared `store/merges.py`, used by
both appliers.

### 13. Minor Function Updates for the Next Sprint Plan

- [DEV] Write reader telemetry outside the repository (or out of the
  tree fingerprint) so a reader never blocks a gate -- target: Sprint 17
  plan, est: 30m
- [DEV] A sign-off table to add or split an assertion, so a split never
  edits reader output by hand -- target: Sprint 17 plan, est: 45m
- [DEV] Split a proof appendix over 30 pages across reviewers by page
  from the start, in the review prompt -- target: Sprint 17 plan, est: 15m
- [DEV] Set both status fields in one step at each phase change -- target:
  Sprint 17 plan, est: 15m

### 14. Function Updates for the Future Backlog

- [DEV] Find why per-page agent cost rose (proof-heavy papers, figure
  pages viewed as images, re-reviews), measured per paper kind --
  estimated: 90m [no-history], priority: 30, depends on: F139's telemetry

### 15. Assigned Coding Agents Quality

Readers: first-pass correct (0 check problems over 531 pages). Reviewers:
two of six needed a second pass for depth. Fresh-eyes reviewers: high
value, every report had a real finding or a clean bill with evidence.

### 16. Questions to be discussed before ending the sprint

none
