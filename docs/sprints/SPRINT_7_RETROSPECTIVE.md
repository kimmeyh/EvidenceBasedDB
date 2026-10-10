# Sprint 7 Retrospective: Move the Data Out, Then Measure arXiv Safely

**Date**: 2026-10-09. **PR**: #68. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "Manual Validation complete".

## Sprint 7 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All seven tasks met their acceptance
  criteria and CI stayed green. Rework: Task F's first apply failed its
  quote check (pdftotext's curly quotes and ligatures), so the pre-apply
  backup was restored and the script re-applied; the Phase 5 I4 re-read
  found two sentences in ADR-0004 A7 that did not match the code. The
  largest waste was Task D: the per-cycle refresh was built as planned and
  then not adopted at Manual Validation (Q12), because the cost of running
  it each cycle (36 hours measured) was known only after it was built.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Every new guard was proven to fail by
  injection (the cap, the stale report, the hash test, the quote tests, the
  read and yields test). The F45 quote test checks all 25 quotes that have
  a local copy, in both pdftotext modes, so a quote is verified against the
  source and not against my transcription. The `live_store` marker split
  real-data checks from mechanism checks cleanly. Gap: nothing checks that
  `sprint_status.json`'s `updated` field is current; it read 2026-10-06 for
  two days.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Task C's runtime was the miss: the plan
  said 5.8 hours (one site request at 15 s), and the run took 36 hours. The
  plan's runtime was computed before Q5 and Q7 were decided; Q5 = 1 (the API
  first, the page parsed too) doubled the requests and Q7 moved the spacing
  to 18 s, and the runtime was not recomputed after approval. Commit to
  commit: A 2m (est 45m), B 40m (est 210m), D 4m (est 60m), E about 80m
  across three commits, with the F61 and F62 cards in between (est 60m), F 15m (est 90m), G 18m (est 120m). F's and
  G's figures are commit to commit only; part of their reading may have
  happened earlier, and git cannot show it, so treat them as lower bounds.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Task D carried "probes each cycle" from
  ADR-0005 A4 without a cost check; one line of arithmetic (1,500 papers at
  two requests and 18 s) would have shown it was a two-night job every
  sprint, and the team lead would have chosen the yearly re-check at
  planning. Task B's acceptance still named a "full export" and a
  "committed fixture" after Q1 = 2 removed them; the plan was not rewritten
  to match its own decisions.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Task A moved the Developers tier to
  Sonnet 5.5 on evidence. The fresh-eyes reviewers on B and C were worth
  it: they found the Windows path used off Windows and refused records
  never retried, both fixed before the bulk run.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The two-hourly status reports during C
  worked. Two misses. At 12:28am I said I would re-probe the 107 records
  the abstract page answered; I dropped that after measuring a 1% yield
  and disclosed it only at Manual Validation, when it should have been
  said when it was dropped. And Q12 was first framed around the mechanism
  (site mode against API mode), which the team lead could not decide from;
  the decision was really how often to re-check, which only surfaced from
  the team lead's answer.

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The hidden requirement was how often a
  paper needs re-checking (yearly, staggered, never 1,000+ in one sprint);
  it surfaced only at Manual Validation. The reading pass also found two
  second-hand figures wrong in the source critique (F-301's "80 percent"
  and F-302's 122% gap), so the assertions say what the papers say.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Four ADR amendments, all approved; A6
  was revised before approval to carry Q12. CHANGELOG entries for C, F and
  G. One stale line remains: `CLAUDE.md` says CI deselects the `live_store`
  tests "by name", while ADR-0004 A7 (e) and CI use the marker.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Friction, all worked around: the hooks
  that block `$(...)` in python commands and python rewriting `.py` files
  (injections done with Edit plus a copy and restore); cp1252 encoding
  errors on Windows (`PYTHONIOENCODING`, or `sys.stdout.reconfigure` under
  `python -I`); pdftotext's typographic characters (normalized in the quote
  test, with anchors that say so).

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The arXiv risk materialized as an
  outage, not a refusal: the API gave no answer from about 20:00 on 10-07
  to 00:33 on 10-08, the abstract page answered all 107 papers, and the cap
  and pacing held for 12 sessions with 0 errors. The store risk of moving
  the data was covered by a verified backup and the live round trip.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Sprint 8 candidates are carded: F60,
  F61, F62 (with the pilot report), F63 and F64; Q9 kept the existing
  priorities. `SPRINT_7_SUMMARY.md` is still to write (Phase 7 or Sprint 8
  Phase 1.2). No blockers.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The store left the repository with the
  three ADRs amended together (ADR-0004 A7, ADR-0003 A2, ADR-0005 A5), so
  no ADR describes a committed export any more. Edits in place went only to
  amendments not yet approved (A7 at I4, A6 at Manual Validation).

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [DEV] `CLAUDE.md`: "deselects them by
  name" to "by their marker" -- target: Sprint 8 plan, est: 5m. [DEV]
  Recompute every task's runtime after the approval decisions and before
  Phase 4 (a plan template line) -- target: Sprint 8 plan, est: 15m.

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [DEV] Already carded at Manual
  Validation: F63 (two Dirac-3 admissions) and F64 (the staggered 12-month
  re-check). [DEV] A guard that `sprint_status.json`'s `updated` date is
  not older than the newest commit that changed the file -- estimated: 30m,
  priority: 60, depends on: none.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Only the fresh-eyes reviewers were
  delegated. Both reports were accurate on first pass and were verified
  against the code before the fixes; no rework came from them.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Improvement Decisions

Team lead, 2026-10-10: "Q21 1" (all seven now, as recommended). Every
improvement prevents its problem at the source first, and extends an
existing mechanism.

- **I1. Every decision option states its cost** (now, 0747a9b): extends
  the planning check of what tools can do in `docs/SPRINT_PLANNING.md`
  (Sprint 6 I5): runtime per run, and per recurrence when the option adds
  a recurring step.
- **I2. The plan absorbs its decisions at 3.7** (now, 0747a9b): extends
  workflow step 3.7; each task's runtime and acceptance lines that a
  decision changed are rewritten in the commit that records the decisions.
- **I3. Decision options lead with the outcome** (now, 0747a9b): extends
  the numbered-question rule in `CLAUDE.md` and its memory file.
- **I4. A dropped or changed commitment is disclosed in the next message**
  (now, 0747a9b): `CLAUDE.md` "Things Claude Should NOT Do", with a memory
  file.
- **I5. The Phase 5 amendment re-read covers every restatement** (now,
  0747a9b): extends Sprint 6 I4; `CLAUDE.md`'s "by name" corrected.
- **I6. No stored `updated` date; one status format** (now): the
  `updated` field is removed from `sprint_status.json` (0747a9b; `git log`
  answers it, and nothing read it). The status format is "Phase n.n Name
  -- detail" everywhere: the Phase 4 Stop hook and
  `tests/test_sprint_documents.py` read the phase number from it (either
  form), and a test fails on a live status the footer cannot read; both
  new guards proven to fail by injection. The first attempt at the hook
  edit was refused by the session's permission classifier on 2026-10-10;
  the hook was restored unchanged, and the team lead switched to manual
  permissions (Q22 = 1) for the edit.
- **I7. Task start times in the note** (now, 0747a9b): extends the Phase 4
  rule that the note is written at every task boundary.
