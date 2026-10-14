# Sprint 8 Retrospective: Claude Code Development Team draft

Drafted 2026-10-13 in Phase 7 step 2, while the team lead writes the Product
Owner, Scrum Master and Lead Developer feedback. Times are from `git log`
(local time). Commit-to-commit times are lower bounds: work done before a
task's first commit does not show in git.

### 1. Effective while as Efficient as Reasonably Possible

- **Claude Code Development Team**: All six tasks met their acceptance
  criteria; CI is green on PR #77 and PR #84. Rework: the fresh-eyes
  reviews of C and D found 8 and 7 defects (all real, all fixed before
  hand-over); CI failed once on Linux (a POSIX path, c256d8c); F61's dry
  run kept file suffixes on seven DOIs; and the F60 report said the Asfaw
  PDF was never downloaded, which was wrong: it was in `Workforce`. That
  last one reached the team lead as a decision (Q6) that was not needed.
  After Manual Validation: the first Q7 apply wrote upgrade reasons
  without saying what each claim cost QCi; the F47 guard caught it, the
  pre-apply backup was restored and the corrected script re-applied.

### 2. Testing Approach

- **Claude Code Development Team**: Every new guard was proven to fail by
  injection, including the Q7 upgrade sync added after Manual Validation.
  Quotes are checked against the local PDFs, not against my
  transcription. Two gaps: the local suite runs on Windows only, so the
  POSIX path case was first seen by CI; and F60's "not downloaded"
  conclusion had no check behind it: it searched the mismatched row's
  folder, not the collection.

### 3. Effort Accuracy

- **Claude Code Development Team**: Estimated 792 minutes (A 60, B 30,
  C 240 + 72 allowance, D 240, E 30, F 120). Commit to commit, from plan
  approval (23:01) to the Phase 5.3 status (00:06): B 3m, C 12m plus 15m
  of review fixes, D 11m plus fixes, E 5m, F 20m. These are lower bounds
  and still show the estimates far too high for reading and scripted
  intake. The fresh-eyes reviews, not the first build, set the real end
  of C and D.

### 4. Planning Quality

- **Claude Code Development Team**: The plan's decisions held, with one
  exception: F66 as carded asked for CI on PRs into main, and the plan
  carried it without a reason for or against; the team lead declined it at
  Manual Validation. Task E's acceptance said "the Asfaw paper's real arXiv
  id found", which was met, but nothing asked whether its PDF was already
  elsewhere in the collection.

### 5. Model Assignments

- **Claude Code Development Team**: F67 moved the doc-only pattern and the
  Developers role to Haiku 5.5 on the release evidence. The top tier did
  C (certainty work), as planned. The fresh-eyes reviewers earned their
  cost: 15 findings, none false.

### 6. Communication

- **Claude Code Development Team**: The hand-over disclosed the accidental
  dry run, the two `sed` edits and the CI failure up front. Two of its
  decision questions were badly formed. Q5 had a yes/no header ("Should
  the 7 past release merges be tagged too?") over numbered options, so
  "yes" had to be interpreted. Q7 had no recommendation line, so "as
  recommended" could not bind to anything, and Q7 had to be asked again.
  Both break CLAUDE.md's question rules.

### 7. Requirements Clarity

- **Claude Code Development Team**: F65's 11-line item list never arrived,
  across two sprints; C used the card's scope. The F66 instructions were
  clear and phased; the one change (no CI on main) came at the decision
  point, as designed.

### 8. Documentation

- **Claude Code Development Team**: Three dated amendments (ADR-0004 A8,
  ADR-0005 A7, ADR-0001 A2), each re-read against the code. The I5 sweep
  updated the restatements of A7 (workflow 1.3, checklist 1.3). The F60
  report needed a dated correction after Manual Validation.

### 9. Process Issues

- **Claude Code Development Team**: Two code lines were edited with `sed`,
  against the Edit/Write rule; disclosed, and every later edit used Edit.
  A `--due` dry run was started by mistake and may have sent a few paced
  arXiv requests: a dry run of a probe still probes. The shell-metacharacter
  hook caught `${PIPESTATUS}` in a pytest command; the fix was to capture
  the exit code without it. The branch-from-develop hook's bypass token
  must sit in a shell comment, not as a git argument.

### 10. Risk Management

- **Claude Code Development Team**: The Class 2 risk was handled as
  planned: the five admission upgrades were held for the team lead, and
  the script now cannot silently undo one once approved. The arXiv risk
  materialized only in the mistaken dry run, inside the cap.

### 11. Next Sprint Readiness

- **Claude Code Development Team**: Two PRs into develop: #84 (F66) then
  #77. Q7 and F65's list are open. F68 and F69 are carded. The first due
  re-check (F64) is 2027-08-16, so Phase 1.3 has nothing due for months.

### 12. Architecture Maintenance

- **Claude Code Development Team**: A new context (`platform:dirac-3s`)
  came in by amendment, and the vocabulary guard was taught to read
  contexts that an amendment adds, instead of editing the ADR's table in
  place. The re-check computes every date from stored ones; nothing new
  is stored.

### 13. Minor Function Updates for the Next Sprint Plan

- **Claude Code Development Team**: [Claude] Every Manual Validation
  decision question carries a "Recommend N" line, and a question with
  numbered options never has a yes/no header; add both to the workflow's
  Phase 5 hand-over rules -- target: Sprint 9 plan, est: 15m
- **Claude Code Development Team**: [Claude] A "not found" finding about a
  local file searches the whole collection (by id and by title) before it
  is reported; note it in the workflow -- target: Sprint 9 plan, est: 10m

### 14. Function Updates for the Future Backlog

- **Claude Code Development Team**: none beyond F68 and F69, carded during
  the sprint.

### 15. Assigned Coding Agents Quality

- **Claude Code Development Team**: The two fresh-eyes reviewers returned
  15 findings; each was verified against the code or the guide before it
  was fixed, and none was a false positive. Their findings included real
  defects (a crash on a folder path, findings lost on resume, false "newly
  published" entries).

### 16. Questions to be discussed before ending the sprint

- **Claude Code Development Team**: Q7 is answered (all five, applied
  2026-10-13, with the two F63 reasons naming Dirac-3). Open: F65's 11-line
  list. #84 and #77 now merge in either order.
