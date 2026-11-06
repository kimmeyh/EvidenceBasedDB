---
name: hand-download-list
description: Show the hand-download list (papers with no free copy, in priority order, each with its target file name and why it matters), computed from the store. Use when the team lead asks for the hand-download list, the papers to download, or what to save into Papers.
---

# Hand-download list (wrapper for scripts/hand_download_list.py)

Sprint 11 Manual Validation, 2026-10-22 (intake sections 39 and 40). This
skill adds no content of its own. The list is computed from the store each
time, so it is never stale and never kept by hand.

## Procedure

1. Run, from the repository root:

   ```
   python scripts/hand_download_list.py
   ```

2. Show the output to the team lead as printed. Do not reorder, trim or
   retype it: every line comes from the store, and a retyped list is the
   copy that drifts.
3. Add one line after it: the number of records, and that a file saved
   at its target path is linked and read by the next F114 release (F95
   was folded into F114 on 2026-11-05).

## Rules

- Read only. The script writes nothing; never edit the store to change
  the list. To move a paper up, the team lead names it and its id goes in
  `PRIORITY_FIRST` in the script, by commit.
- Never fetch a listed paper around a paywall or a failed TLS check.
