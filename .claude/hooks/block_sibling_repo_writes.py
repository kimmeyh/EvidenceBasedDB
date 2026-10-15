"""PreToolUse hook blocking writes into spamfilter-multi,
hsbc-quantum-fraud-2026 or hsbc-qfraud-phase2 -- their repos, their .claude
directories, and their Claude Code memory directories.

hsbc-qfraud-phase2 added 2026-10-15 (Sprint 9 Task A, F79). Team lead,
2026-10-14: "they are both consumers of each other and reads are permitted
without direct prompts from the other - so each could read from each
other, but cannot write to each other". A change wanted in Phase 2 goes as
a prompt the team lead pastes into a Phase 2 session.

Team lead, 2026-09-15: "from here on out, the activities in this repo
should not write/update files in either spamfilter-multi or hsbc repo...
It is OK to read from them upon request, but not write to them." Prompted
by a Sprint 1 session that read both repositories' process docs and
memory files while porting question-format conventions and backlog items
into EvidenceBasedDB -- reading was correct and intended; writing back
into either source repository was never asked for and must not become a
side effect of a future session doing the same kind of research.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_sibling_repo_write, for the rare case where the
team lead explicitly asks for a change to be made in one of those
repositories from an EvidenceBasedDB session rather than switching to a
session already working there.

Covers two tool shapes:
  1. Write / Edit / NotebookEdit -- tool_input.file_path is the target,
     read directly, no parsing needed.
  2. Bash / PowerShell -- tool_input.command is a shell string; there is no
     single authoritative "target path" for an arbitrary command, so this
     scans for any of the guarded path prefixes appearing anywhere in the
     command. This can over-block (a command that merely MENTIONS a guarded
     path in a comment or an echoed string), which is an acceptable
     trade-off given what a false negative here would cost -- silently
     writing into someone else's repository is a materially worse outcome
     than an occasional bypass-token round-trip for a read-only command
     that happens to name a guarded path.
"""
from __future__ import annotations

import json
import re
import sys

GUARDED_ROOTS = (
    r"D:\Data\Harold\github\spamfilter-multi",
    r"D:\Data\Harold\github\hsbc-quantum-fraud-2026",
    r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-spamfilter-multi",
    r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-hsbc-quantum-fraud-2026",
    r"D:\Data\Harold\github\hsbc-qfraud-phase2",
    r"C:\Users\kimme\.claude\projects\D--Data-Harold-github-hsbc-qfraud-phase2",
    r"C:\Users\kimme\.claude\projects\D--Data-Harold-hsbc-quantum-fraud-2026-Phase-2-Planning",
)

# Matched case-insensitively and with either slash direction, since a Bash
# command on this Windows host may spell the same path with forward
# slashes (Git Bash) or backslashes (native tools invoked from Bash).
_GUARDED_PATTERNS = [
    re.compile(re.escape(root).replace(r"\\", r"[\\\\/]"), re.IGNORECASE)
    for root in GUARDED_ROOTS
]

# Commands that write, as opposed to merely reading. A read-only command
# (cat, type, git log, git diff, grep, ls, Get-Content) that happens to
# mention a guarded path is allowed through, since the team lead's own
# instruction says reading stays fine -- blocking every mention would make
# routine research (which motivated this hook in the first place) into a
# constant bypass-token exercise, training the same disable-by-friction
# failure this project's other hooks are written to avoid.
#
# Widened 2026-10-15 (Sprint 9 Task A review): `git -C <repo> commit` passed,
# because `commit` had to follow `git` directly, and INTAKE_WORKFLOW.md
# section 19 tells sessions to read Phase 2 with `git -C`, which makes that
# the likeliest slip. Git's global options (-C <path>, -c <key=value>) may
# now come first, and the git verbs that change a working tree or history
# (checkout, restore, stash, apply, tag, switch, clean, cherry-pick) count.
# Remove-Item, Copy-Item, Move-Item, Rename-Item, tee and sed -i passed too.
#
# Git is FAIL-CLOSED since the same day (automated security review of that
# fix): a list of git write verbs is never complete (pull, revert, am,
# config, update-ref, worktree, gc...), and global options such as
# --no-pager could sit before the verb. So when a guarded path appears,
# every git invocation must name a read subcommand from _GIT_READS; any
# other subcommand blocks. See _git_writes.
_GIT_READS = frozenset({
    "show", "log", "diff", "status", "grep", "ls-files", "ls-tree", "rev-parse", "blame",
    "cat-file", "describe", "shortlog", "rev-list", "help", "version",
})
_GIT_OPTION_WITH_VALUE = frozenset({"-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"})
# A read subcommand can still write through these (second security review,
# 2026-10-15): `--output`/`-O` write a file, `--open-files-in-pager` runs a
# program, and `-c`/`--config-env` can set a pager, an editor or a hook
# path. With a guarded path present, any of them blocks.
_GIT_WRITING_OPTION = re.compile(r"^(?:-c|--config-env.*|--output.*|-O.*|--open-files-in-pager.*)$")
# `git` after any non-word character (a quote, a backtick, a brace, a path
# separator), not only after whitespace or a shell operator.
_GIT_CALL = re.compile(r"(?:^|[^\w.-])git(?:\.exe)?(?=[\s\"'`)}]|$)", re.IGNORECASE)
_TOKEN = re.compile(r"\"[^\"]*\"|'[^']*'|[^\s;&|()]+|[;&|()]")


def _git_writes(command: str) -> bool:
    """True when some git invocation in the command names a subcommand that
    is not a known read. Global options (and their values) before the
    subcommand are skipped."""
    for call in _GIT_CALL.finditer(command):
        tokens = _TOKEN.findall(command[call.end():])
        tokens = tokens[:next((n for n, t in enumerate(tokens) if t in (";", "&", "|", "(", ")")), len(tokens))]
        if any(_GIT_WRITING_OPTION.match(t.strip("\"'")) for t in tokens):
            return True
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok in _GIT_OPTION_WITH_VALUE:
                i += 2
                continue
            if tok.startswith("-"):
                i += 1
                continue
            if tok.strip("\"'").lower() not in _GIT_READS:
                return True
            break
    return False


_WRITE_VERBS = re.compile(
    r"(?:^|[\s;&|(])(?:"
    r"rm|mv|cp|copy|del|erase|ren|rename|tee"
    r"|sed(?:\s+-\S+)*\s+-i\S*"
    r"|touch|mkdir|New-Item|Set-Content|Add-Content|Out-File"
    r"|Remove-Item|Copy-Item|Move-Item|Rename-Item|Clear-Content"
    r"|>|>>"
    r")(?:\s|$)",
    re.IGNORECASE,
)


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _matches_guarded_root(path: str) -> bool:
    return any(pattern.search(path) for pattern in _GUARDED_PATTERNS)


def main() -> int:
    try:
        payload = _read_payload()
    except Exception:
        return 0  # fail open on malformed payload

    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    if tool_name in ("Write", "Edit", "NotebookEdit"):
        file_path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if not file_path:
            return 0
        if "allow_sibling_repo_write" in file_path:
            return 0
        if _matches_guarded_root(file_path):
            _block(f"{tool_name} targeting {file_path!r}")
            return 2
        return 0

    if tool_name in ("Bash", "PowerShell"):
        command = str(tool_input.get("command") or "")
        if not command:
            return 0
        if "allow_sibling_repo_write" in command:
            return 0
        if not _matches_guarded_root(command):
            return 0
        if not _WRITE_VERBS.search(command) and not _git_writes(command):
            return 0  # a guarded path appears, but nothing in the command writes
        _block(f"{tool_name} command referencing a guarded path and a write verb: {command!r}")
        return 2

    return 0


def _block(detail: str) -> None:
    print(
        "[BLOCKED] This session must not write into spamfilter-multi, "
        "hsbc-quantum-fraud-2026 (team lead, 2026-09-15) or "
        "hsbc-qfraud-phase2 (team lead, 2026-10-14).\n"
        "\n"
        f"Detail: {detail}\n"
        "\n"
        "Reading from either repository -- its docs, its memory files, its "
        "backlog -- stays fine and is expected when researching what should "
        "carry over into this repository. Writing, editing, or running a "
        "command that modifies either repository from an EvidenceBasedDB "
        "session is not.\n"
        "\n"
        "If the team lead has explicitly asked for a change to be made in "
        "one of those repositories from here, re-run with the literal token "
        "allow_sibling_repo_write in the command or file path. Otherwise, "
        "make the change from a session already working in that repository; "
        "for hsbc-qfraud-phase2, draft a prompt the team lead pastes there.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    sys.exit(main())
