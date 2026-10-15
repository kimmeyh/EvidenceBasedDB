# Sprint 9 Task A (F79): prompt for the team lead to paste into hsbc-qfraud-phase2

Drafted 2026-10-15. This repository never writes to `hsbc-qfraud-phase2`
(team lead, 2026-10-14), so a change wanted there goes as this prompt, pasted
by the team lead into a Phase 2 session. The team lead reviews it first and
may edit it.

## What was checked here before drafting (read-only)

- Phase 2's `.claude/hooks/block_cross_repo_write.py` already blocks
  writes into `EvidenceBasedDB` by folder name. Called directly on
  2026-10-15 (bytecode writing off, so nothing landed in Phase 2):
  `D:\Data\Harold\github\EvidenceBasedDB\CLAUDE.md` is blocked, and
  `D:\Data\Harold\EvidenceBasedDB\store\evidence.db` is blocked.
- **The gap, for the Edit, Write and NotebookEdit tools only:** a write to
  `C:\Users\kimme\.claude\projects\D--Data-Harold-github-EvidenceBasedDB\memory\x.md`
  is NOT blocked. Shell commands are already blocked there, because
  `check_command` matches the name as a substring (fresh-eyes review,
  2026-10-15). `check_path` matches whole folder names, and the Claude
  Code project folder is named `D--Data-Harold-github-EvidenceBasedDB`,
  which is not the folder name `EvidenceBasedDB`.
- Phase 2's `CLAUDE.md` says the sibling repositories are read-only from
  there "and only when asked". The team lead's 2026-10-14 rule makes reads
  of EvidenceBasedDB free, with no request needed.

## The prompt

```
Two changes from the EvidenceBasedDB session (F79 there; team lead
2026-10-14: "they are both consumers of each other and reads are permitted
without direct prompts from the other - so each could read from each other,
but cannot write to each other").

1. Close a gap in .claude/hooks/block_cross_repo_write.py. check_path
   (the Edit, Write and NotebookEdit path) matches whole folder names, so an
   Edit or Write into EvidenceBasedDB's Claude Code project directory is not
   blocked. Shell commands there are already blocked, because check_command
   matches the name as a substring; change only check_path:
     C:\Users\kimme\.claude\projects\D--Data-Harold-github-EvidenceBasedDB\memory\x.md
   (checked 2026-10-15: check_path returns None for it; the repository and
   D:\Data\Harold\EvidenceBasedDB\store\evidence.db are blocked correctly).
   Block the Claude Code project directories of every forbidden repository
   too: a folder under .claude\projects whose name ends with
   "-<forbidden name>" (for example D--Data-Harold-github-EvidenceBasedDB,
   D--Data-Harold-github-spamfilter-multi). Add a test for that path, and
   prove it fails by injection before restoring. Keep this repository's own
   project directory (D--Data-Harold-github-hsbc-qfraud-phase2) allowed,
   with a test.

2. Update the CLAUDE.md wording for EvidenceBasedDB only. Today it says the
   sibling repositories are read-only "and only when asked". For
   EvidenceBasedDB the rule is now: read it freely, with no request needed
   (its repository, its docs and its store at
   D:\Data\Harold\EvidenceBasedDB\store\evidence.db); never write to it; a
   change wanted there goes as a prompt the team lead pastes into an
   EvidenceBasedDB session. spamfilter-multi and the Phase 1 repository keep
   their current wording.

For information: EvidenceBasedDB now reads Phase 2 results from Phase 2's
git history at a named commit (git show, a read). Its first inbound record
is docs/B4_B5_HARDWARE_RESULT.md at commit 139fa13. Nothing was written in
this repository.
```
