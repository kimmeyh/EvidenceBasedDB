# Sprint 5 Summary: Make the Store Durable, Then Fill It

**Dates**: 2026-09-23 to 2026-09-25. **Branch**: `feature/20260923_Sprint_5`.
**PR**: #43. **Issues**: #44 to #52, all closed. Sources: the plan
(`SPRINT_5_PLAN.md`), `git log`, the issues, the retrospective
(`SPRINT_5_RETROSPECTIVE.md`). Every count below is a snapshot as of
2026-09-25.

## What shipped

- **F30, store durability (Task A, #44).** `scripts/rebuild_store_from_export.py`
  rebuilds the store from the committed export through the real door and
  proves the regenerated export byte-identical (it was, at 48 papers and
  again at 347). `store/backup.py` takes a SQLite-API backup before every
  live `--apply`, verified at creation or the write does not happen, with
  three-rule retention. `scripts/restore_store.py` restores and verifies.
  A backup preceded every one of the sprint's store writes.
- **F31, the HSBC Phase 2 bibliography (Tasks B-D, #45-#47).** 120 entries
  parsed; 96 files downloaded (64 arXiv PDFs), 11 found already on disk and
  3 already in the store, none fetched twice; 14 items on a manual list with
  reasons. 121 records entered at `seen`, 0 refused. F36 carded: nine (now
  ten) per-reference fields the store lacks, each classed as computed or
  stored, with a back-fill path.
- **F5, QCi (Tasks E-H, #48-#51).** 18 QCi-affiliated people identified from
  the papers' own author lines. Author search: 191 acceptances by a
  co-authorship rule written first; 108 new records; 39 PDFs. QCi's site:
  544 pages and `eqc-models` 0.21.0 saved, 52 reference records. At the team
  lead's revised Q1, 392 unresolved hits screened on their abstracts for
  QML, ML or the Zeno effect: 21 entered, then 3 removed (Q8); 18 remain,
  marked "authorship not confirmed". `[QC-8]`, which the bibliography could
  not supply, arrived through the author search.
- **F28, learning from the papers (Task I, #52).** `docs/LEARNING_SYNTHESIS.md`
  and `scripts/learnings.py`: a key learning is an assertion with "synthesis
  of" provenance whose evidence is computed from `supports`/`contradicts`.
  Pilot: six papers to `read`, seven assertions, three learnings. The
  existing primitives sufficed; F37 carded for an explicit derivation marker.

**Store**: 48 papers at sprint start, 347 at close (321 `seen`, 14
`screened`, 12 `read`); assertions 13 -> 23 (plus 3 learnings counted among
them). **Suite**: 458 -> 505 tests. **Closed without implementation**: F19,
F29. **Carded**: F32-F35 (Sprint 6, the team lead's), F36, F37.

## Actuals

Wall clock is commit-to-commit from `git log` (local time); delegated
agents' figures are the tokens and seconds each reported. Plan estimate:
780 Claude-side minutes, every card `[no-history]`.

- Planning: selection to plan draft 2026-09-23 evening; plan approved and
  issues opened 08:19 on 2026-09-24.
- Task A (#44): 08:19 to 08:28 commit, 9 min coordinator time after the
  design reading. Estimate 120 min.
- Task B (#45): committed 08:55; the download run itself about 11 min
  (64 PDFs serial) after a 16-min metadata pass on the refusal path.
- Task E (#48): committed 08:59; ran beside Task B on local PDFs.
- Task C (#46): committed 09:27; two 25-min intake runs (dry run and apply)
  on the refusal path dominated.
- Task D (#47): committed 09:28. Task G (#50): committed 09:28 (scrape about
  12 min in the background). Task I (#52): committed 09:33. Task H (#51)
  part 1: 09:39. Task F (#49): 09:50. Phase 5 review fixes: 09:58. Task H
  part 2: 10:07.
- **Execution total: about 108 min** of coordinator wall clock, approval to
  last task commit, against a 780-min estimate.
- Manual Validation fixes and decisions: 08:45 to 10:51 on 2026-09-25,
  about 126 min, including the revised-Q1 topic screen.
- Delegated agents: evidence gathering (QML papers) 105,183 tokens / 287 s;
  evidence gathering (ML papers) 133,613 tokens / 505 s; fresh-eyes code
  review 85,446 tokens / 187 s. All read-only; every quote used and every
  finding verified before use.
- arXiv metadata: 13.1 s per id on the refusal path (planning pre-flight)
  and the same in every run; DataCite answered 73 of 75 at planning.

## Findings surfaced

- arXiv's API refused this client for the whole sprint (HTTP 429 and 406)
  while arxiv.org served every PDF; DataCite carried the metadata, and the
  door now records when it did.
- The bibliography cites six entries differently from their registries (two
  with another paper's title for their id).
- The fresh-eyes review found four defects in Task A's code after it had
  already guarded nine writes; all fixed with tests. Retrospective
  improvement 5 moves that review to the task's commit.
- The author-search rule, as written, cannot reach a prolific author's
  pre-QCi career (Miri 139 of 144 unresolved); reported, then partly
  resolved by the team lead's topic screen.

## Verification

- Suite 505 passed at the retrospective-improvements commit (5be2402).
- `python scripts/rebuild_store_from_export.py` byte-identical at 347 papers,
  with the door's local-path and hollow-page checks on.
- `gh issue list --label sprint --state open`: empty.
