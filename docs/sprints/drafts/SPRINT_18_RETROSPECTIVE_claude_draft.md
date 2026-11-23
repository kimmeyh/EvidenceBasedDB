# Sprint 18 Retrospective: Claude Code Development Team draft

Drafted 2026-11-23 while the team lead's feedback is asked (protocol step 2). Counts are a snapshot as of the
date each names.

### 1. Effective while as Efficient as Reasonably Possible

All six tasks (A to F) delivered, and every Manual Validation decision applied (q4 to q18, intake section 81).
F146 ran on Claude Code subagents as q1 = c decided: 69 runs, about 9.19 million tokens, no API spend. The waste,
in order of cost: the hand-set status (one failed full suite and a rerun); readers and reviewers that wrote or
edited results by script, each found and checked; and audit run a063 (36 minutes for 126 items, against about 3
for the others).

### 2. Testing Approach

Every new guard was proven red by injection (F147, F148, F149, F145, q7). The gates caught a missing inventory row
again (q7's new test), and `tests/test_set_status.py` caught the hand-set status as built to. The full suite ran
once before the hand-over (1,744 passed); F140 q7 skipped the planned second run, since nothing had changed.
`--changed` after a store write runs about 1,150 tests in 9 to 11 minutes, longer than the full suite (about 6).
`scripts/test_inventory.py --write` wipes the recorded timings, so a scratch merge was used each time.

### 3. Effort Accuracy

The plan forecast about 677 minutes at the cards' estimates (about 850 at Sprint 17's 1.25 times). The task
commits ran from 00:10 to 08:06 on 2026-11-21; the start of execution on 2026-11-20 is not in a commit, so the
actual is not exact. F146's audit grew from 59 to 63 runs because Task D's papers added HIGH assertions during the
run.

### 4. Planning Quality

The order held: F147's apply function existed before D's apply and E's intake used it. The plan did not foresee
that D's new HIGHs would enter F146's audit while it ran; the checker handed them out, but the plan's count was
stale. The plan said "full suite twice", which other repositories had already dropped (F150).

### 5. Model Assignments

Readers ran on Sonnet as general-purpose agents. The answers were right on every control (189 of 189 audit, 18 of
18 map), but reader strictness on "held in part" varied from about 50 to about 90 of each 200 (F153 measures
it). One reader miscounted its own run (222 for 200 plus controls); the checker's count was used.

### 6. Communication

The Manual Validation hand-over first went out while CI was pending; the Stop hook blocked it, and it was re-sent
after CI passed. The hand-over carried 14 questions; the team lead asked for fewer: "just do as recommended", now
a memory, and F151 stores every question in one file. q14 to q17 offered Phase 2 adoptions, which this repository
does not propose (now a memory).

### 7. Requirements Clarity

q12's rule was clear and testable; applied by reading each pair's content, not its label, it changed no grade.
"Do as recommended" needed a scope: I applied it to q11, and the team lead confirmed it (q11 = a).

### 8. Documentation

Intake sections 78 to 81 record Tasks D, C, E and the Manual Validation decisions. Section 78 was written after
the list release was applied, not before; the intake test caught it. The counts block is now printed from the
store (F148) and was rewritten after the q7 apply.

### 9. Process Issues

The sprint status was set by hand once and failed `test_set_status`; `scripts/set_status.py` is the only way. A CI
poll loop used `$(...)`, which the hook blocks; `gh pr checks --watch` is the way.

### 10. Risk Management

F144's rules held: the audit and the map wrote nothing to the store; failing results were kept and flagged
(a018, a030), never dropped. Every store write (D's apply, E's intake and its correction, q7) had a verified
backup first and a second run that wrote nothing.

### 11. Next Sprint Readiness

Cards ready for Sprint 19: F150 (full suite once), F151 (questions stored in full), F152 (re-quote 20), F153
(sample triage), F154 (semantic screen, with the q12 rule). F114 continues.

### 12. Architecture Maintenance

F147 makes `sync_decided_assertion` the one apply path from Sprint 18 on; the old appliers are frozen by a test.
No ADR amendment this sprint: q12's rule changed no grade, so its ADR-0004 amendment waits for F154.

### 13. Minor Function Updates for the Next Sprint Plan

- Reader and reviewer prompts: forbid writing or editing a result by script; one Write, no Edit (q9).
- `scripts/test_inventory.py --write` keeps the recorded timings of files already listed.
- The local read checker also flags an id that another source already holds.

### 14. Function Updates for the Future Backlog

F152, F153 and F154 as carded. A reader id typo was caught only because the item was re-handed; the checker could
name a near-miss id (an edit distance of 1) in its problems.

### 15. Assigned Coding Agents Quality

Agents' answers were checked, not trusted: every result passed the checker, and all 207 controls were right. Rule
breaks: g350, g361 and g511 wrote by script; a008 edited its result; a018 and a030 each mistyped one id.

### 16. Questions to be discussed before ending the sprint

None open: q4 to q18 are answered (q11 and q14 confirmed 2026-11-23).
