# Sprint 13 Retrospective: Claude Code Development Team draft

Drafted 2026-10-28, after Manual Validation, for
`docs/sprints/SPRINT_13_RETROSPECTIVE.md`. The 16 categories, Development
Team role only. Counts are a snapshot as of 2026-10-28.

1. **Effective while as Efficient as Reasonably Possible**: Tasks A to F
   met their acceptance criteria by the first hand-over (2026-10-25 07:12).
   Task G (F113), added at Manual Validation, read 210 records whole in
   groups g001 to g042 and applied them; groups g043 on went to the F114
   cloud readers, which stopped at $0 credit with 302 results fetched and
   not yet reviewed (F117, Sprint 14). Rework after the apply: two store
   defects (the sync's one-column writes, eb3941a; Task G's apply
   rewriting 114 Task F read rows, 5e10948), then the extent change of
   Manual Validation Q7 (2bab87b). Most of the F114 launcher's 11 fix
   commits came from launching it, not from planning it.
2. **Testing Approach**: Every new guard was proven red by injection. The
   full suite found the Task F overwrite after the apply (6 failures);
   `--changed` had not, because it ran before the store write that caused
   it. The trial apply's log showed 114 "update read" lines, and nobody,
   me included, asked why a first apply updated rows. A trial log needs a
   check, not only a read: an apply of new reads that logs an update is
   a stop.
3. **Effort Accuracy**: Tasks A to F were estimated at about 1,490
   minutes; plan approval (2026-10-25 00:47) to the first hand-over (07:12)
   was 385 minutes of wall clock, with reader time in the background (about
   26 percent; Sprint 12: 24 percent). Task G carried no estimate as a
   limit (no reading budget); its forecast of 20 to 40 hours of reader
   time for 1,991 records was not tested, since 210 were read locally and
   302 in the cloud before the pause and the credit stop.
4. **Planning Quality**: The plan for A to F held. Task G entered at
   Manual Validation without a plan of its own for how its read rows share
   a day with Task F's; the key collision (reader, day, extent) was a
   planning gap that a pre-flight query would have shown: 57 of its
   records had Task F rows dated 2026-10-25.
5. **Model Assignments**: Sonnet 5.5 readers did the first pass, with
   every quote checked in the write path and the coordinator at the top
   tier; the fresh-eyes reviewers found real defects in most code
   commits (Task G: 4 review cycles, each with a finding). F117 now splits
   the review by protocol across Haiku 5.5, Sonnet 5.5 and Opus 5.5; its
   evidence is still to come.
6. **Communication**: The Task F overwrite was disclosed at Manual
   Validation with its cause, its repair and the unquestioned trial log.
   Manual Validation ran to 13 questions over four days, because Task G
   and the PHI-OMEGA intake arrived inside it; each message re-presented
   every open question in full.
7. **Requirements Clarity**: Two requirements surfaced mid-sprint: no
   reading budget (2026-10-25) and the read extent wording (Q7: `full`
   when the paper was read whole). Both are now in tests. "Process" in Q11
   (later Q13) meant the coordinator's review of the cloud results; I
   echoed it with a time and a recommendation before acting.
8. **Documentation**: INTAKE section 53 records the apply, both defects
   and their repairs; its first counts were wrong twice (208 whole and 2
   with exceptions, not 210; 306 read rows, not 153; 200 plus 8 for the
   slice), each caught by a fresh-eyes review. CHANGELOG lagged 19 commits
   from 2026-10-26 to 2026-10-28 and was caught up at close
   (71705d8); the same-commit policy slipped during the F114 launch.
9. **Process Issues**: Seven older scripts still UPDATE read rows by key
   alone (sprint9_f78:527, sprint9_f80:387, sprint10_f83:208,
   sprint10_f84:214, sprint10_f89:358, sprint11:558, sprint12:1515); none
   runs again as written, but a re-run on a day another script wrote
   would repeat the Task F overwrite. Machine memory pressure gave 2
   MemoryError failures that pass alone.
10. **Risk Management**: The pre-apply backup made the repair exact (a
    diff showed 0 rows missing). The risk that materialized was one script
    owning another's rows; the mitigation (ownership by wording, tested
    both ways) covers Task F and Task G only.
11. **Next Sprint Readiness**: F119 (PHI-OMEGA, Priority 10) is carded
    with its files in the library and two references (Q12 = 1); F117 (the
    302 cloud results) at 20, F118 at 22. One file is owed by the team
    lead: the third image, from the 2026-09-23 post.
12. **Architecture Maintenance**: No ADR amendment this sprint. The
    `paper_reads` key (record, reader, day, extent, detail) allowed two
    scripts' rows to look alike; ownership is now by wording in the
    scripts, not in the schema. Worth a look at the F75 checkpoint.
13. **Minor Function Updates for the Next Sprint Plan**:
    - [Dev] An apply's trial log that shows an "update" where only new
      rows are expected stops the apply, by a check in the apply script --
      target: Sprint 14 plan, est: 30m
    - [Dev] The seven older scripts' key-only read-row UPDATEs scoped by
      their own detail, or the scripts marked not to re-run -- target:
      Sprint 14 plan, est: 45m
    - [Dev] Save the third PHI-OMEGA image and add it to the reference --
      target: Sprint 14 plan, est: 5m
14. **Function Updates for the Future Backlog**:
    - [Dev] Read-row ownership in the schema (a writer column on
      `paper_reads`), so no script matches another's rows by wording --
      estimated: 120m, priority: 40, depends on: F75 checkpoint
15. **Assigned Coding Agents Quality**: The Sonnet 5.5 readers' quotes
    passed the write-path check; the coordinator replaced values where the
    meaning drifted. The fresh-eyes reviewers were the most productive
    agents of the sprint: each review of a store or script commit found
    at least one real problem. The F114 cloud readers produced 302 results;
    their quality is unknown until F117.
16. **Questions to be discussed before ending the sprint**: none.
