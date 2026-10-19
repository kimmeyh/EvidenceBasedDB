# Sprint 10 Retrospective: Claude Code Development Team draft

Drafted 2026-10-19, in parallel with the team lead's feedback. Copied into
`docs/sprints/SPRINT_10_RETROSPECTIVE.md`.

1. **Effective while as Efficient as Reasonably Possible**: All ten tasks
   met their acceptance criteria, three with a disclosed change (E, I, J).
   Every task's fresh-eyes review found real defects, all fixed before
   hand-over. The costliest rework was my own: four coordinator reads were
   wrong (F84 cut QCi's own "better than O(n^3)" conclusion; F85
   attributed the B4 band to Dirac-3; F89 passed "polylogarithmic" for
   Carleman's complexity and lost the root-2 threshold). Reviews caught
   each. Intake rule 26 (quotes checked before any write) was missed by
   three scripts at first apply. Manual Validation step 5 was the wrong
   kind of step and was rejected.
2. **Testing Approach**: 1,053 tests at hand-over, 1,059 at close; every
   new guard proven to fail by injection. Reviews found three weak tests
   (figure tests over a whole-document haystack, a test comparing a set
   with itself, F89 HIGH grades passing unchecked); each was rewritten.
   One near miss: I wrote an injection claim into a docstring before
   running the injection. I caught it before the commit, ran the
   injection, and wrote what it actually showed.
3. **Effort Accuracy**: Estimated 375 minutes. Plan approval (15:56) to
   the Manual Validation hand-over (19:14) took about 200 minutes, about
   53 percent, against Sprint 9's 37 percent: the Sprint 9 cut brought the
   estimate closer. Reviews and fix cycles again set the end of A, E, F,
   G, I and J. Manual Validation added work in no estimate: the
   live re-run (Q4 = 2) and the 91 entries (Q6), about 70 minutes of
   runtime.
4. **Planning Quality**: The plan's decisions held. Three commitments
   changed and were disclosed in the next message and the status note:
   E's `--ext-diff`/`--textconv` block was removed because it guarded
   nothing; I read 65 of 74 (9 no free copy); J was measured on Sprint 9's
   saved pool instead of a re-run.
5. **Model Assignments**: Right. Sonnet 5.5 first-pass readers on F89 were
   accurate on quotes and numbers under the new reader_inference rule; the
   defects this sprint came from the coordinator (me), not the readers.
   Fresh-eyes and automated security reviews were worth their cost: three
   rounds on Task A and three on Task E each found a real bypass.
6. **Communication**: Changed commitments were disclosed on time. Two
   misses: MV step 5 asked for a terminal command that could not test a
   hook, and one message went out while CI was still running (the Sprint 9
   I7b Stop hook blocked it, as designed, and I re-sent after green).
7. **Requirements Clarity**: Clear. The open questions went to Manual
   Validation as Q1 to Q6 and were answered in one pass each.
8. **Documentation**: ADR-0004 A10 and its same-day correction, approved;
   intake sections 27 to 30; dated amendments with same-day corrections in
   two research documents; the workflow's Manual Validation rule extended
   to hook checks; CHANGELOG current at every commit.
9. **Process Issues**: Intake rule 26 depended on each script remembering
   to call `require_verbatim`, and three did not. The code-edit hook
   correctly blocked two shell writes to code files. Smaller: a stray 404
   page saved as a PDF in `Papers\` by an ad-hoc command (removed), a
   heredoc backslash collapse, an untracked manifest that `git checkout`
   could not restore.
10. **Risk Management**: The coordinator read is a single point of failure
    for every value: four errors in one sprint, all caught by review, one
    (F85's band) in the store for about 15 minutes. No paywall was
    crossed, arXiv stayed serial at 18 s, and no key was logged.
11. **Next Sprint Readiness**: Ready. F90 (the eight hand-downloads)
    carded at the team lead's request; F57 at 2,057 never read (snapshot
    2026-10-19); F51 still HOLD.
12. **Architecture Maintenance**: ADR-0004 A10 approved as written; the
    ADR-0005 question on registry answers with nothing recordable left as
    is (Q2 = 1). No schema change.
13. **Minor Function Updates for the Next Sprint Plan**: [Dev Team] F57's
    closing rule rewritten to "no record left without a read row" (Q5 =
    1) -- target: Sprint 11 plan, est: 5m (proposed below as I3, to apply
    now).
14. **Function Updates for the Future Backlog**: [Dev Team] F90, read the
    eight F89 papers once downloaded -- estimated: 45m, priority: 60,
    depends on: the team lead's downloads.
15. **Assigned Coding Agents Quality**: High. Readers' quotes needed nine
    character-level corrections in 216 assertions, and two values were
    rewritten; the two wrong values the review found in F89 were mine.
    Reviewers found defects in every structural task.
16. **Questions to be discussed before ending the sprint**: none.
