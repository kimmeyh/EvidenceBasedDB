"""Run the test suite and record one verdict for the tree it ran on
(Sprint 11 retrospective I2, 2026-10-23).

Sprint 11 read the suite's verdict by eye from scrolling output twice:
an interim message called the full suite passed when it had 2 failures,
and a full suite ran while an injection was still in the code, so its
result described neither tree. This runner:

  - fingerprints the working tree (tracked and untracked files, ignored
    ones left out) before and after the run, as a git tree id;
  - prints ONE verdict line, from pytest's exit code, never from its
    output: PASSED, FAILED, or INVALID when the tree changed during the
    run (an edit, an injection, a stray file);
  - records the verdict in .claude/suite_verdict.json (not committed).

The commit hook (`.claude/hooks/block_commit_with_piped_tests.py`) reads
that file and refuses a commit of a tree whose recorded verdict is FAILED
or INVALID. It does not require a verdict: when the full suite must run
before a commit is the team lead's decision, under F100.

    python scripts/run_suite.py                 # the full suite
    python scripts/run_suite.py tests/test_x.py # any pytest arguments
    python scripts/run_suite.py --changed       # the tests for what changed (F100)
    python scripts/run_suite.py --changed --since origin/develop

`--changed` is the per-commit set (workflow Phase 4, F100, Sprint 12):
the changed test files; every test file that names a changed module (its
stem, as a word) or a changed non-Python file (its name); and the document
guards when a document changed. A change to `tests/conftest.py` touches
every test, so it runs the full suite. The changes are the working tree's
against HEAD, plus the commits since `--since REF` when given. CI's set
(`-m "not live_store"`) still runs on the PR; the full suite runs twice a
sprint.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERDICT = Path(".claude") / "suite_verdict.json"
LOG = Path(".claude") / "suite_last.log"


def _git(repo: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True,
                          env=env).stdout.strip()


def working_tree(repo: Path) -> str:
    """The git tree id of the working tree as `git add -A` would stage it,
    computed in a scratch index so the real one is untouched."""
    index = Path(_git(repo, "rev-parse", "--git-path", "index"))
    index = index if index.is_absolute() else repo / index
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "index"
        if index.exists():
            shutil.copyfile(index, scratch)  # its stat cache makes `add -A` fast
        env = dict(os.environ, GIT_INDEX_FILE=str(scratch))
        _git(repo, "add", "-A", env=env)
        return _git(repo, "write-tree", env=env)


# Run whenever a document changes: they read every document, so no file
# name ties them to the one that changed.
DOC_GUARDS = ("tests/test_no_em_dashes.py", "tests/test_changelog_currency.py", "tests/test_sprint_documents.py")
DOC_SUFFIXES = (".md", ".json")
EVERYTHING = "tests/conftest.py"


def changed_files(repo: Path, since: str | None = None) -> list[str]:
    """Repository paths changed in the working tree (staged, unstaged or
    untracked) against HEAD, plus those changed since `since` if given."""
    out = set()
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True, check=True).stdout  # not _git: its strip eats " M"
    for line in status.splitlines():
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        out.add(path.replace("\\", "/"))
    if since:
        out.update(p for p in _git(repo, "diff", "--name-only", f"{since}...HEAD").splitlines() if p)
    return sorted(out)


def targeted_tests(repo: Path, changed: list[str]) -> list[str] | None:
    """The test files for `changed`, or None when the full suite is due."""
    if EVERYTHING in changed:
        return None
    tests = {p: (repo / p).read_text(encoding="utf-8", errors="replace")
             for p in (f"tests/{f.name}" for f in sorted((repo / "tests").glob("test_*.py")))}
    picked = {p for p in changed if p in tests}
    for path in changed:
        name = Path(path).name
        if path.startswith("tests/") or not (repo / path).is_file():
            continue
        needle = (re.compile(rf"\b{re.escape(Path(path).stem)}\b") if path.endswith(".py")
                  else re.compile(re.escape(name)))
        picked.update(t for t, text in tests.items() if needle.search(text))
        if path.endswith(DOC_SUFFIXES):
            picked.update(DOC_GUARDS)
    return sorted(picked)


def verdict(rc: int, before: str, after: str) -> str:
    if before != after:
        return "INVALID"
    return "PASSED" if rc == 0 else "FAILED"


def main(argv: list[str]) -> int:
    if "--changed" in argv:
        argv = list(argv)
        argv.remove("--changed")
        since = None
        if "--since" in argv:
            i = argv.index("--since")
            since = argv[i + 1]
            del argv[i:i + 2]
        picked = targeted_tests(ROOT, changed_files(ROOT, since))
        if picked == []:
            print("SUITE SKIPPED: no test covers what changed")
            return 0
        if picked is None:
            print(f"--changed: {EVERYTHING} changed, so the full suite runs")
        else:
            print(f"--changed: {len(picked)} test files: {' '.join(Path(p).stem for p in picked)}")
        argv = [*(picked or []), *argv]
    before = working_tree(ROOT)
    started = datetime.now()
    log = ROOT / LOG
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8") as out:
        rc = subprocess.run([sys.executable, "-m", "pytest", "-q", *argv], cwd=ROOT, stdout=out,
                            stderr=subprocess.STDOUT).returncode
    after = working_tree(ROOT)
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    summary = next((ln.strip("= ") for ln in reversed(lines) if re.search(r"\d+ (passed|failed|error)", ln)),
                   "no pytest summary line")
    result = verdict(rc, before, after)
    record = {"verdict": result, "rc": rc, "tree": before, "tree_after": after, "args": argv,
              "summary": summary, "head": _git(ROOT, "rev-parse", "HEAD"),
              "started": started.isoformat(timespec="seconds"),
              "finished": datetime.now().isoformat(timespec="seconds")}
    (ROOT / VERDICT).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    scope = "full suite" if not argv else "pytest " + " ".join(argv)
    why = " (files changed during the run; re-run on a still tree)" if result == "INVALID" else ""
    print(f"SUITE {result}: {summary}, rc={rc}, {scope}, tree {before[:10]}{why}")
    return 0 if result == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
