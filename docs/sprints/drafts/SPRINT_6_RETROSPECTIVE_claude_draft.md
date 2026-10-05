# Sprint 6 Retrospective: Claude Code Development Team draft

Drafted 2026-10-05 in parallel with the team lead's feedback (SPRINT_RETROSPECTIVE.md step 2).

### 1. Effective while as Efficient as Reasonably Possible
All twelve tasks shipped, and the store grew from 361 to 1,875 papers with every new field in place. Rework was real: the Task E review cycle, two back-fill re-runs (a provider regex misread "Crossref/DataCite"), three repository-linking re-runs after crashes, and a bulk load stopped and restarted twice. Most of that rework traces to one defect (the unpaced intake fetcher) that was found late.

### 2. Testing Approach
Strong where it was applied: every new guard was proven to fail by injection, and two of my own tests were caught as vacuous during that step (the rollback test that passed with the rollback removed; the first F47 regex that flagged the very record F47 names). Weak where it was missing: no test exercised arXiv pacing ACROSS intake entries, so a Sprint 4 defect survived to Sprint 6 and broke the team lead's 6 s instruction once. Tests pinned the interval constant, not the behavior.

### 3. Effort Accuracy
Coordinator tasks A-I and L landed close to estimate. Task J's runtime was planned as 82 min to 10 h and took about 6 hours of wall clock including two pauses, inside the range, but the range itself was wide because arXiv's behavior was unknown. Task K's 75 min estimate held for the code; the re-runs added about 30 min.

### 4. Planning Quality
The pre-flights paid off (F33's ids, the retraction notice, the F41 dry run). Two gaps: the plan sized Task F's computed fields for 347 records and did not say whether the 1,402 bulk records would be probed in the same sprint (now F52); and decision 4.1 assumed a missing `method` row that already existed.

### 5. Model Assignments
Top tier for the ADR and the migration was right. The two fresh-eyes reviewers (code-reviewer subagent) found real defects both times: 4 in Task E, 7 in Phase 5, including two pacing gaps. No subagent was used for the Task F queue report; the queue turned out to be a one-line query.

### 6. Communication
I reported the pacing defect plainly, including that my earlier explanation of the 429s was wrong. Misses: I closed the wrong issue once (#63 for #62, reopened at once), and Task H's commit subject carries the wrong number. Long background runs were reported by progress notes; the 10-minute burst that broke the 6 s rule was found from its runtime, not from a guard.

### 7. Requirements Clarity
The team lead's arXiv instruction (6 s, pause 2 h, DataCite on failure) had one ambiguity, retries, which I asked as a numbered question before acting. The ADR text promised a Phase 1.3 probe run that was never planned; corrected before review, carded as F53.

### 8. Documentation
CHANGELOG kept current per task. Two slips: INTAKE_WORKFLOW section 16 was appended after its manifest ran (stated in the section), and ADR-0005 A4's probe rule claimed a mechanism that did not exist until corrected at Phase 5.

### 9. Process Issues
Hooks caught four real mistakes before they landed: a piped test gate, a Python rewrite of a .py file, an unescaped Windows path, and a sibling-repo path in a generator command (a false positive, worked around without the override token). The pacing defect is the process lesson: a rule enforced by a constant is not enforced unless the object that holds the clock is shared.

### 10. Risk Management
"arXiv refuses a sustained run" was a named risk; the mitigation (serial traffic, DataCite fallback, per-entry commits) held, so nothing was lost. But the risk materialized partly because of our own defect, which the risk table did not consider.

### 11. Next Sprint Readiness
Store at 1,875 papers, 60 assertions, export byte-identical. Cards F52-F57 are written; F52 (bulk probes) should run before anything else hits arXiv, under its cap.

### 12. Architecture Maintenance
Two ADR amendments accepted; the computed-versus-stored rule held in code (derived keys never written back, probe rows as dated measurements). `parse_access` needed two fixes (GitHub names containing arXiv ids; order).

### 13. Minor Function Updates for the Next Sprint Plan
- [DT] Correct Task H's commit-subject issue number in the Sprint 6 summary -- target: Sprint 7 plan, est: 5m
- [DT] Add `2108.0131` (malformed in QMLPapers/2021/manifest.tsv) to F54's report list with the likely full id from the paper -- target: Sprint 7 plan, est: 15m

### 14. Function Updates for the Future Backlog
- [DT] A behavior test for every external-API pacer: count real waits across a multi-record run, not the constant -- estimated: 1h, priority: 30, depends on: none

### 15. Assigned Coding Agents Quality
Both review agents were accurate: every finding I checked was real, file and line exact, and the severity calls held. One Phase 5 finding (the HEAD bypassing the pacer) was in code I had written hours earlier, after the first review.

### 16. Questions to be discussed before ending the sprint
none
