"""PreToolUse hook blocking any tool call that reads, prints, edits or stages
the repository's secret file, `.env`.

Sprint 17 (F144, plan Q1, team lead 2026-11-07): "I will put it in the .env
file in the local repository D:\\Data\\Harold\\github\\EvidenceBasedDB and then
we can use if from there", with the key named ANTHROPIC_API_KEY. The Batch API
reader (`scripts/batch_read.py`) reads it with python-dotenv's
`dotenv_values`, which returns the values without putting them in the
environment, so Claude Code's own credential order never sees the key.
The team lead's rule from the F144 brief: the key is never printed and never
written to a file, log or commit by Claude. `.gitignore` names `.env`, so git
and ripgrep (the Grep tool) skip it; this hook covers the direct paths.

Blocked:
  1. Read / Edit / Write / NotebookEdit whose target file is named `.env`.
  2. Grep whose `path` or `glob` names `.env`.
  3. Bash / PowerShell whose command names `.env` as a word (so `.venv`,
     `ocr-venv` and `python-dotenv` pass).

Allowed: Glob (it lists names, never contents), and a script that loads the
file itself (a command that names only the script, not `.env`).

THREAT MODEL: accidental reads by this repository's own sessions, as for
the sibling-repository guard. A command that builds the name from pieces,
or a broad `grep -r` over the repository, can still reach the file; that
takes intent, and the file stays out of git by `.gitignore`.

Bypass: the literal token allow_env_mention, for a command that only
mentions the name in text (a commit message, a CHANGELOG line written by a
script) and does not open the file.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
"""
from __future__ import annotations

import json
import re
import sys

BYPASS = "allow_env_mention"
# `.env` as a name: not preceded by a word character or a dot (so `.venv`
# and `x.env` are not it), and not followed by a word character or a dot
# (so `.envrc` and `.env.example` are not it).
NAME = re.compile(r"(?<![\w.])\.env(?![\w.])")
FILE_KEYS = ("file_path", "notebook_path")


def _payload() -> dict:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _is_env_file(path: str) -> bool:
    name = re.split(r"[\\/]", path.strip().strip('"').strip("'"))[-1]
    return name == ".env"


def reason(payload: dict) -> str | None:
    """The block message for a payload, or None to allow."""
    tool = str(payload.get("tool_name") or "")
    args = payload.get("tool_input") or {}
    if not isinstance(args, dict):
        return None
    if tool in ("Read", "Edit", "Write", "NotebookEdit", "MultiEdit"):
        for key in FILE_KEYS:
            if _is_env_file(str(args.get(key) or "")):
                return f"{tool} on the secret file {args.get(key)}"
        return None
    if tool == "Grep":
        for key in ("path", "glob"):
            value = str(args.get(key) or "")
            if NAME.search(value) or _is_env_file(value):
                return f"Grep with {key} {value!r}"
        return None
    if tool in ("Bash", "PowerShell"):
        command = str(args.get("command") or "")
        if BYPASS in command:
            return None
        if NAME.search(command):
            return "a shell command that names the secret file"
        return None
    return None


def main() -> int:
    try:
        payload = _payload()
    except Exception:
        return 0  # fail open on a malformed payload
    why = reason(payload)
    if why is None:
        return 0
    print(
        f"[BLOCKED by block_env_secret_reads hook] {why}.\n"
        "\n"
        "`.env` holds the team lead's API key (Sprint 17 plan Q1). Claude "
        "never reads, prints, edits or stages it; only scripts/batch_read.py "
        "loads it, by python-dotenv's dotenv_values.\n"
        "\n"
        "If the command only MENTIONS the name in text (a commit message) and "
        f"does not open the file, add the token {BYPASS} as a shell comment.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
