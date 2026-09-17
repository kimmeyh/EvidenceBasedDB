# Windows PowerShell Guide

**Purpose**: PowerShell and Windows-environment practices for this repository: shell selection, error patterns observed in this project's own sprints, and conventions adapted from spamfilter-multi's WINDOWS_DEVELOPMENT_GUIDE.md and TROUBLESHOOTING.md via hsbc-quantum-fraud-2026.
**Audience**: Claude Code sessions executing commands on this Windows 11 host.
**Last Updated**: 2026-09-16 (Sprint 1 Task H, F1 -- removed content specific to the consumer repository's WSL/hardware pipeline; see the WSL interop section's removal note below for what changed and why)

## Shell selection

PowerShell 7+ is the primary shell. Bash (Git Bash POSIX sh) is available for POSIX-only tooling. Decision rule: PowerShell by default; bash only when a tool demands POSIX syntax. Never mix syntaxes (`&&` works in PowerShell 7 but heredocs, `[ -f x ]`, and backslash-path handling do not transfer between shells). Never wrap PowerShell in bash or vice versa (ADR-0017 lesson: wrapping loses toolchain context on this exact host).

## Error patterns OBSERVED IN THIS PROJECT (with fixes)

1. **Cmdlet failures poison the exit code even when suppressed.** `Get-ChildItem <empty-or-missing> -ErrorAction SilentlyContinue` still exits 1 (observed listing empty `datasets/` dirs). Fix: promote to terminating and swallow: `try { Get-ChildItem $p -ErrorAction Stop } catch {}` , or end the command with an expression that always succeeds (a summary string).
2. **`Select-String` with zero matches** contributes a failure-looking result. Fix: capture to a variable and test `if ($m) {...}`; never let a possibly-empty match be the last statement of a command whose exit code matters.
3. **NEVER edit JSON with `-replace`.** `.claude/sprint_status.json` regex-edited is fragile and ordering-dependent. Fix: `ConvertFrom-Json` round-trip, or a Python one-liner. Applies to any structured file: parse, mutate, serialize.
4. **uv-created venvs have no pip.** `python -m pip` fails with "No module named pip". Fix: `uv pip install <pkg> --python .venv\Scripts\python.exe`.
5. **Here-string closers must sit at column 0.** `'@` indented is a parse error. Git commit messages use `git commit -m @'... '@` with the closer unindented; `--%` stop-parsing token for arguments containing `%` or `@`.
6. **Legacy vs new credentials shadowing**: user-level env vars silently override OAuth caches. One credential system per service (ADR-0002); when auth misbehaves, print key NAMES present in the environment first.
7. **Python Unicode on the Windows console** (cp1252): set `$env:PYTHONIOENCODING = 'utf-8'` before any Python that prints non-ASCII; better, keep script output ASCII with bracketed markers ([OK]/[FAIL]) per QUALITY_STANDARDS.

## Adapted practices

- **Quote every path** (spaces in this tree are real); `cd "D:\..."` quoted always.
- **Command chaining**: `;` for sequence, `&&` only in PowerShell 7 contexts; separate dependent steps into separate calls when exit codes matter.
- **Process management**: `Stop-Process -Name x -Force -ErrorAction SilentlyContinue` then `Start-Sleep -Seconds 2` before rebuilding anything file-locked.
- **Long-running work**: background execution with output files; per-unit persistence so interruption loses one unit; never edit a job's inputs while it runs.
- **Known-failure triage**: before investigating a failing script, read its header and this guide; the failure may already be documented.

## WSL interop -- REMOVED 2026-09-16 (Sprint 1 Task H, F1)

This section described the consumer repository's own need to run parts of
its pipeline under WSL for Linux-only scientific-computing dependencies
(sklearn version pinning, hardware-runner scripts). This repository has no
such dependency: it is pure Python and SQLite, runs natively on Windows,
and has no WSL requirement. Removed rather than generalized, since there
is no equivalent need here to generalize it into. If a future dependency
genuinely requires WSL, re-add this section against that dependency's own
actual requirements rather than restoring this text.

## Hooks (assessment from spamfilter .claude/hooks)

| Source hook | Purpose there | Applicability here | Plan |
|---|---|---|---|
| block-carry-forward-stash.ps1 | Hard-block `git stash` (carry-forward protection) | Direct: stash is banned here too | Ported in F1 sprint as `block_carry_forward_stash.py` |
| verify-closeout-complete.ps1 | Stop hook blocking completion claims contradicted by artifacts | High value once sprint cadence is steady | Ported in F1 sprint as `verify_closeout_complete.py` (adapted to our checklist paths) |
| require-sprint-cards.ps1 | Blocks task work before cards exist | Concept adopted in workflow 3.4; hook port optional | Backlog |
| sprint-auto-advance.ps1 | Enforces the auto-advance window bounds | Tied to spamfilter's status schema; ours differs | Backlog, revisit Phase 2 |

**AMENDMENT, 2026-09-14**: the two ported hooks above, plus
`block-branch-from-develop.ps1`, `block-unraw-escape.ps1` and
`block-shell-metachar-expansion.ps1` (seeded here directly, not from this
table), were converted from PowerShell to Python. See the QUALITY_STANDARDS.md
"Automation standards" amendment of the same date for why: hooks are invoked
by Claude Code over a documented, language-agnostic contract, so the
PowerShell-native rule that governs this repository's OTHER automation does
not apply to `.claude/hooks/` specifically. The `.ps1` names in this table are
left as originally written, describing the source repository's files at the
time of the Sprint 2 assessment; the files that actually exist in THIS
repository's `.claude/hooks/` now carry a `.py` extension and underscores
rather than hyphens.

The pre-commit confidentiality hook (this repo's own, `.git/hooks/pre-commit`) remains active and verified.

## Quick reference for this repo

```powershell
# Tests
python -m pytest -q

# Regenerate the export after a data change
python scripts\regenerate_export.py

# Ingest the seed set (idempotent; skips records already present)
python scripts\ingest_seed_set.py --promote
```

## Background python: always pass `-u`

Python buffers stdout when its output is piped or redirected, which every
`run_in_background` invocation does. A long-running job therefore writes NOTHING
to its output file until it exits, so the file looks empty while the job is
healthy.

```powershell
# WRONG: output invisible until exit
.\.venv\Scripts\python.exe scripts\ingest_seed_set.py

# RIGHT: line-buffered, progress visible as it happens
.\.venv\Scripts\python.exe -u scripts\ingest_seed_set.py
```

Use `-u` for anything that runs longer than a few seconds -- a background
ingestion pass over dozens of papers is the case in this repository where
watching progress is the difference between catching a problem early and
finding it only after the run finishes.
