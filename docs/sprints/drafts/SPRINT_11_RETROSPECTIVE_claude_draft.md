# Sprint 11 Retrospective: Claude Code Development Team draft

Drafted 2026-10-22, after Manual Validation, for
`docs/sprints/SPRINT_11_RETROSPECTIVE.md`. The 16 categories, Development
Team role only.

1. **Effective while as Efficient as Reasonably Possible**: All 7 tasks
   met their acceptance criteria. Rework before hand-over: Tasks F and G
   were applied twice, because the first apply ran without
   `require_edit_basis` (intake section 31) and with the figure check only
   printed. The full suite and the fresh-eyes review caught it: 7 values
   still past their quotes, 3 measured results at HIGH (5 moved to LOW in
   all). Task C's first apply linked a `supports` that failed ADR-0004
   A8(b); withdrawn by name. Rework after Manual Validation: the Q1 link and
   the Q2 list, both small.
2. **Testing Approach**: Every new guard was proven to fail by injection
   (1,131 tests at hand-over). Three gaps found by tests or review, not by
   design: the quote pattern skipped a quote with no space after ";", so
   `require_verbatim` passed it unchecked (caught by the F93 number test;
   every quote now must parse); the F11 packet went stale when a G record
   moved to `read`; and the reading script edited values without the
   section 31 check, which `test_verified_writes.py` caught only at the
   full suite, after the first apply.
3. **Effort Accuracy**: Estimated 655 minutes. From plan approval (23:41)
   to the Manual Validation hand-over (02:42) took about 181 minutes of
   wall clock, about 28 percent, with up to 5 readers in parallel. Commit
   to commit (lower bounds, G overlapping the rest): A 19m, B 10m, C, D
   and E together 44m, F and G together 93m, hand-over 15m. Task G's 325m
   assumed serial reads; the ledger and 5 readers cut it most.
4. **Planning Quality**: The plan held. Two plan statements were wrong
   and disclosed: Task F's snapshot said 37 unlinked files (38, one
   counted with G), and the NVIDIA eval repository could not be linked by
   source (asked at Q1). The hand-download list had no owner until Q2.
5. **Model Assignments**: Sonnet 5.5 readers, one ledger group each, up to
   5 at once, worked: after the prompt fix, groups g16 onward had 0 quote
   misses. The coordinator's own read, on the top tier, replaced 13 values
   and was itself the source of the HIGH grades the review corrected.
6. **Communication**: Changed commitments were disclosed in the next
   message and in the status note (37 vs 38 files, the unlinked
   repository, the second apply). One real failure: an interim message
   called the full suite passed before its output was read; it had 2
   failures. Corrected in the next message and the note.
7. **Requirements Clarity**: F57's order changed twice on 2026-10-21
   (newest first, then back to relevance), both before planning. Q2's
   "ongoing list" needed an ordering rule the team lead did not state; I
   chose one and asked.
8. **Documentation**: Intake sections 32 to 39; a dated amendment to the
   ceilings answer document (F93); BACKLOG_REFINEMENT.md's
   adopted/adapted/declined list (F94). Section 39's first draft
   hand-counted 17 records; the resolver returned 16. The
   computed-not-stored rule caught its own author.
9. **Process Issues**: The code-edit hook blocked a JSON-only edit because
   the same command ran pytest on a test file, and a JSON heredoc whose
   prose named script files; split into separate calls. Parallel readers
   shared one scratchpad and one overwrote another's temp files; the
   reader prompt now names a per-group folder. Reader stray files landed
   in the repository root and were moved out. A full suite ran while an
   injection was live; it was stopped and re-run clean.
10. **Risk Management**: arXiv traffic stayed serial at 18 s. No paywall or
    TLS failure was worked around (Macaluso's host is on the list). No
    write crossed into a sibling repository.
11. **Next Sprint Readiness**: F98 (Christophe Pere's list) is carded; F95
    names the next repository (wangy8205165/Quantum-NeuralNetwork-WhitePaper);
    F57 count 1,840 unread.
12. **Architecture Maintenance**: No ADR amended. The auto-ontology-eval
    link is the first source link whose evidence is a decision, not a
    source sentence; its evidence names the decision. If more follow,
    ADR-0005 should say so in an amendment.
13. **Minor Function Updates for the Next Sprint Plan**:
    `[DEV] Fold F62's discovery hand-download entries into the computed
    list (if the team lead chooses it) -- target: Sprint 12 plan, est: 20m`;
    `[DEV] Fix Pande 2020's citation, which carries "&amp;" from Crossref --
    target: Sprint 12 plan, est: 10m`.
14. **Function Updates for the Future Backlog**: `[DEV] A gate that runs
    the full suite's write-path tests before any --apply, not after --
    estimated: 45m, priority: 30, depends on: none`.
15. **Assigned Coding Agents Quality**: Readers' first-pass quotes were
    mostly exact; misses were typed dashes and minus signs (11 corrected).
    Their main defect was saying more than the quote (13 values replaced).
16. **Questions to be discussed before ending the sprint**: F62's
    discovery entries on the hand-download list (asked at Manual
    Validation).
