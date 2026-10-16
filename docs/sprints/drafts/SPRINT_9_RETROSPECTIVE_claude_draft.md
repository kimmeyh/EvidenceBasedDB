# Sprint 9 Retrospective: Claude Code Development Team draft

Drafted 2026-10-16, after Manual Validation, for
`docs/sprints/SPRINT_9_RETROSPECTIVE.md`. The 16 categories, Development
Team role only.

1. **Effective while as Efficient as Reasonably Possible**: All 11 tasks
   met their acceptance criteria. Every task's fresh-eyes review found
   real defects, and each was fixed before hand-over. Rework after Manual
   Validation: five preprints were refused by the title check (published
   under a new title) and entered by journal DOI; five Chen quotes and the
   shared normalizer needed fixes; the Task E sync never compared quotes;
   and a re-apply wrote a wrong date into three records' history, undone
   from the verified pre-apply backup.
2. **Testing Approach**: Every new guard was proven to fail by injection
   (880 tests at hand-over, 887 at close). Two gaps. The quote normalizer
   lives in a test module and grows one character class at a time (en
   space, then ligatures), found only when a new source arrived. And
   `test_a_second_apply_writes_nothing` could not see a field the sync
   never compared, so the quote sync gap passed it.
3. **Effort Accuracy**: Estimated 780 minutes. From plan approval (00:05)
   to the Manual Validation hand-over (04:56) took 291 minutes of wall
   clock, about 37 percent, with subagents running in parallel. Commit to
   commit (lower bounds): A 14m plus 19m of review fixes, B 2m, C 4m, D 5m,
   E 35m plus 15m, F 7m, G 58m plus 29m, J 34m plus 46m. The Sprint 9 cut
   by 3 was still about 2.7 times high. Reviews, not builds, set the end
   of E, G and J; Task J's review took longer than its build.
4. **Planning Quality**: The plan's decisions held. Two plan statements
   were wrong and disclosed: Task E said "read in full" (the reads were a
   subagent's full pass plus a coordinator's partial read), and Task H
   counted 214 DOIs where 807 were asked (35 minutes, not 8). Task G's 11
   refusals were not foreseen by the slice rule.
5. **Model Assignments**: Sonnet 5.5 first-pass readers on E, F, G and the
   Chen and JMLR reads, with every quote checked by the coordinator, worked.
   The readers' own inferences were the main defect class: the Task E review
   cut false and unlabeled reader text, and the Chen read lost five reader
   judgments. The top tier kept certainty and ADR work, as planned.
6. **Communication**: Changed commitments were disclosed in the next
   message and in the status note (Task E's read extent, 30 not 31
   sources, Task G's 11 refusals, Task H's runtime). One real failure:
   two status footers (about 3:48 and 3:58) were typed by hand and wrong;
   the script gave 3:37. That is the exact failure the footer script was
   built to stop.
7. **Requirements Clarity**: F79 was corrected at refinement (free reads
   both ways, no writes) before any work began. Q6 (how to cover a closed
   paper) arose from a download that was not free; asked once, answered
   once.
8. **Documentation**: Three amendments (ADR-0005 A9 and A10, ADR-0004 A9)
   approved as proposed; the answer document got a dated addendum rather
   than an in-place edit; INTAKE_WORKFLOW sections 19 to 25 added.
9. **Process Issues**: The shell-metacharacter hook blocked `${PIPESTATUS}`
   in a pytest command again (also in Sprint 8). The code-file hook blocked
   `sed -n` on a .py (carded F81). `python -I` ignores PYTHONIOENCODING, so a
   cp1252 error needed `sys.stdout.reconfigure`. The Task E script carried a
   literal TODAY, so a re-run on the next day dated new history to the day
   before.
10. **Risk Management**: arXiv traffic stayed serial and inside the cap.
    Semantic Scholar rate limits materialized (52 errors on the first
    discovery run) and were mitigated by backoff and an arXiv fallback. The
    never-write hook went through three security reviews; the third's
    evasion forms were carded (F82) against the accidental-write threat
    model rather than chased. Every store write took a verified backup
    first, and that backup is what made the date error recoverable.
11. **Next Sprint Readiness**: F81 to F86 are carded. F57 releases 74
    records per sprint from Sprint 10. Han and Verdu 1994 stays at `seen`,
    not obtainable. The Phase 2 prompt is with the team lead.
12. **Architecture Maintenance**: The cites link came in by amendment with a
    schema migration and backup; the corroborated flag is computed, never
    stored; the discovery ranks are computed from the review file. No ADR
    spine diverged.
13. **Minor Function Updates for the Next Sprint Plan**: [Claude] Split each
    task estimate into build and review, calibrated from Sprint 8 and 9
    actuals -- target: Sprint 10 plan, est: 15m
14. **Function Updates for the Future Backlog**: none beyond F81 to F86,
    carded during the sprint.
15. **Assigned Coding Agents Quality**: First-pass readers were accurate on
    quotes and numbers; their weakness was conclusions the source does not
    state. Fresh-eyes reviewers found real defects on every task (Task E: 18
    assertions and 30 read details; Task G: five values, three grades, two
    conflicts of interest); each finding was verified against the source or
    the code before it was fixed.
16. **Questions to be discussed before ending the sprint**: none.
