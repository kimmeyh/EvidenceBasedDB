# Sprint 10 Retrospective: Fix the Hooks and the Dirac Records, Then Read the Next 74

**Date**: 2026-10-19. **PR**: #101. Protocol: `docs/SPRINT_RETROSPECTIVE.md` (16 categories x 4 roles).
The team lead's feedback is recorded verbatim (combined Product Owner, Scrum Master and Lead Developer,
given as one line per category, and so repeated under each of the three roles). The team lead's
message opened: "can you push the download list of #5 to the next sprint." and then "Manual
Validation complete".

## Sprint 10 Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: All ten tasks met their acceptance criteria, three with a disclosed change (E, I, J). Every task's fresh-eyes review found real defects, all fixed before hand-over. The costliest rework was my own: four coordinator reads were wrong (F84 cut QCi's own "better than O(n^3)" conclusion; F85 attributed the B4 band to Dirac-3; F89 passed "polylogarithmic" for Carleman's complexity and lost the root-2 threshold). Reviews caught each. Intake rule 26 (quotes checked before any write) was missed by three scripts at first apply. Manual Validation step 5 was the wrong kind of step and was rejected.

### 2. Testing Approach

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: 1,053 tests at hand-over, 1,059 at close; every new guard proven to fail by injection. Reviews found three weak tests (figure tests over a whole-document haystack, a test comparing a set with itself, F89 HIGH grades passing unchecked); each was rewritten. One near miss: I wrote an injection claim into a docstring before running the injection. I caught it before the commit, ran the injection, and wrote what it actually showed.

### 3. Effort Accuracy

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Estimated 375 minutes. Plan approval (15:56) to the Manual Validation hand-over (19:14) took about 200 minutes, about 53 percent, against Sprint 9's 37 percent: the Sprint 9 cut brought the estimate closer. Reviews and fix cycles again set the end of A, E, F, G, I and J. Manual Validation added work in no estimate: the live re-run (Q4 = 2) and the 91 entries (Q6), about 70 minutes of runtime.

### 4. Planning Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The plan's decisions held. Three commitments changed and were disclosed in the next message and the status note: E's `--ext-diff`/`--textconv` block was removed because it guarded nothing; I read 65 of 74 (9 no free copy); J was measured on Sprint 9's saved pool instead of a re-run.

### 5. Model Assignments

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Right. Sonnet 5.5 first-pass readers on F89 were accurate on quotes and numbers under the new reader_inference rule; the defects this sprint came from the coordinator (me), not the readers. Fresh-eyes and automated security reviews were worth their cost: three rounds on Task A and three on Task E each found a real bypass.

### 6. Communication

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Changed commitments were disclosed on time. Two misses: MV step 5 asked for a terminal command that could not test a hook, and one message went out while CI was still running (the Sprint 9 I7b Stop hook blocked it, as designed, and I re-sent after green).

### 7. Requirements Clarity

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Clear. The open questions went to Manual Validation as Q1 to Q6 and were answered in one pass each.

### 8. Documentation

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: ADR-0004 A10 and its same-day correction, approved; intake sections 27 to 30; dated amendments with same-day corrections in two research documents; the workflow's Manual Validation rule extended to hook checks; CHANGELOG current at every commit.

### 9. Process Issues

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Intake rule 26 depended on each script remembering to call `require_verbatim`, and three did not. The code-edit hook correctly blocked two shell writes to code files. Smaller: a stray 404 page saved as a PDF in `Papers\` by an ad-hoc command (removed), a heredoc backslash collapse, an untracked manifest that `git checkout` could not restore.

### 10. Risk Management

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: The coordinator read is a single point of failure for every value: four errors in one sprint, all caught by review, one (F85's band) in the store for about 15 minutes. No paywall was crossed, arXiv stayed serial at 18 s, and no key was logged.

### 11. Next Sprint Readiness

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: Ready. F90 (the eight hand-downloads) carded at the team lead's request; F57 at 2,057 never read (snapshot 2026-10-19); F51 still HOLD.

### 12. Architecture Maintenance

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: ADR-0004 A10 approved as written; the ADR-0005 question on registry answers with nothing recordable left as is (Q2 = 1). No schema change.

### 13. Minor Function Updates for the Next Sprint Plan

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] F57's closing rule rewritten to "no record left without a read row" (Q5 = 1) -- target: Sprint 11 plan, est: 5m (proposed below as I3, to apply now).

### 14. Function Updates for the Future Backlog

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: [Dev Team] F90, read the eight F89 papers once downloaded -- estimated: 45m, priority: 60, depends on: the team lead's downloads.

### 15. Assigned Coding Agents Quality

- **Product Owner**: Very Good
- **Scrum Master**: Very Good
- **Lead Developer**: Very Good
- **Claude Code Development Team**: High. Readers' quotes needed nine character-level corrections in 216 assertions, and two values were rewritten; the two wrong values the review found in F89 were mine. Reviewers found defects in every structural task.

### 16. Questions to be discussed before ending the sprint

- **Product Owner**: none
- **Scrum Master**: none
- **Lead Developer**: none
- **Claude Code Development Team**: none.

## Improvement Decisions

Proposed 2026-10-19 (I1 to I3, prevention first, extending an existing
prevention where one is connected). Team lead, 2026-10-21: "do now i1 and
i2. do not do i3". The hook-check rule was applied at the team lead's
instruction during Manual Validation (c0e8c22) and needed no decision.

| # | Improvement | Type | Disposition | Commit |
|---|---|---|---|---|
| I1 | `store.quotes.require_edit_basis`: each coordinator edit to a reader's work names its source passages, verbatim; a replaced value's numbers and math signs must be in them, or listed as read from the page | Prevention (extends the quote check, intake rule 26) | Now, applied | 74049f0 and the review fix after it |
| I2 | `require_verbatim` returns a `Verified`; `store.ingest.insert_verified_assertion` and `sync_verified_assertion` refuse a write without the matching one; a test holds every script but the 18 earlier writers to them | Prevention (extends `store.ingest` and rule 26) | Now, applied | 74049f0 and the review fix after it |
| I3 | F57's closing rule rewritten to "no record left without a read row" | Prevention | Skip (team lead) | none |
| (rule) | A hook check is never a Manual Validation step | Prevention (extends the Manual Validation rule) | Applied during Manual Validation | c0e8c22 |

I3 skipped: the F57 card keeps "The item closes when the count is 0". Its
count (records at `seen` or `screened`) includes refused records, which
stay `seen`, so the rule as written cannot be met while any refused record
exists (3 as of 2026-10-19). This changes Manual Validation Q5 = 1 ("fix at
the retrospective"); the card stays as it is.

Measured while applying I1 (snapshot as of 2026-10-21): on Sprint 10's F89
coordinator edits, the rule flags the root-2 value and four more whose
figures are in the source but not in their quotes. No stored value is
wrong; under I1 each would have named one more passage.
