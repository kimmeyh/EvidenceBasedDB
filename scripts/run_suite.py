"""Run the test suite and record one verdict for the tree it ran on
(Sprint 11 retrospective I2, 2026-10-23).

Sprint 11 read the suite's verdict by eye from scrolling output twice:
an interim message called the full suite passed when it had 2 failures,
and a full suite ran while an injection was still in the code, so its
result described neither tree. This runner:

  - fingerprints the working tree (tracked and untracked files, ignored
    ones and reader telemetry, NOT_FINGERPRINTED, left out) before and
    after the run, as a git tree id;
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
stem, as a word), a script that imports a changed `store/` module, or a
changed non-Python file (its name); and the document guards when a
document changed. A deleted or renamed file counts under its old name
too. A change to a file every test depends on (`tests/conftest.py`, any
other non-test file under `tests/`, `store/__init__.py`, the pytest and
requirements files) runs the full suite, and so does a change no test
names: an empty pick is not proof that nothing reads it. The changes are
the working tree's against HEAD, plus the commits since `--since REF`
when given. CI's set
(`-m "not live_store"`) still runs on the PR; the full suite runs twice a
sprint.

A store write changes no repository file, so `--changed` alone never saw
one (Sprint 12 retrospective I1). The verdict file also records the
store's stamp (`evidence.db` and its `-wal`, size and modification time)
as of the last PASSED run that covered the store's tests: the full suite,
or a `--changed` run that added them. When the store's stamp differs from
that one, `--changed` adds every test file that carries the `live_store`
marker.
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


# Reader telemetry (F139's per-group files): a reader's check writes its group's file while it works, and no test
# reads these files (the manifest guards read top-level manifests only), so they are left out of the fingerprint.
# Sprint 16: two gates (130 minutes) came back INVALID because a reader wrote telemetry during the run (F142 part 1).
NOT_FINGERPRINTED = (":(glob)manifests/*/telemetry/**",)


def working_tree(repo: Path) -> str:
    """The git tree id of the working tree as `git add -A` would stage it,
    computed in a scratch index so the real one is untouched, without the
    paths in NOT_FINGERPRINTED."""
    index = Path(_git(repo, "rev-parse", "--git-path", "index"))
    index = index if index.is_absolute() else repo / index
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "index"
        if index.exists():
            shutil.copyfile(index, scratch)  # its stat cache makes `add -A` fast
        env = dict(os.environ, GIT_INDEX_FILE=str(scratch))
        _git(repo, "add", "-A", env=env)
        _git(repo, "rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", *NOT_FINGERPRINTED, env=env)
        return _git(repo, "write-tree", env=env)


# Run whenever a document changes: they read every document, so no file
# name ties them to the one that changed. test_us_english joined on 2026-10-25 (Manual Validation Q3): without
# it, 6cfc137's "whilst" passed --changed at the desk and turned CI red.
DOC_GUARDS = ("tests/test_no_em_dashes.py", "tests/test_changelog_currency.py", "tests/test_sprint_documents.py",
              "tests/test_us_english.py")
DOC_SUFFIXES = (".md", ".json")
# Tests that read every file of a kind, so no file name ties them to the one that changed (the fresh-eyes reviews of
# b0b41a3 and b6cdcd0). A manifest: test_intake reads every manifests/*.json, each read-ledger test every reader
# file. A script: these scan every scripts/*.py. A test file: test_guard_discipline reads every test.
MANIFEST_GUARDS = ("tests/test_intake.py", "tests/test_sprint11_read_ledger.py", "tests/test_sprint12_read_ledger.py",
                   "tests/test_sprint13_read_ledger.py", "tests/test_reader_prompts.py")
SCRIPT_GUARDS = ("tests/test_verified_writes.py", "tests/test_schema.py", "tests/test_store_durability.py",
                 "tests/test_qpu_balance_not_stored.py")
# test_test_inventory: a test file's docstring or markers change its inventory row (F140; review of the format change).
TEST_GUARDS = ("tests/test_guard_discipline.py", "tests/test_test_inventory.py")
# Files every test depends on, so a change to one runs the full suite.
EVERYTHING = ("tests/conftest.py", "store/__init__.py", "pytest.ini", "pyproject.toml", "setup.cfg")


def changed_files(repo: Path, since: str | None = None) -> list[str]:
    """Repository paths changed in the working tree (staged, unstaged or
    untracked) against HEAD, plus those changed since `since` if given.
    A deleted file counts, and a rename counts as both of its names
    (`--no-renames`); `-z` keeps every path unquoted and whole."""
    def names(*args: str) -> set[str]:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout
        return {p.decode("utf-8") for p in out.split(b"\0") if p}

    out = {entry[3:] for entry in names("status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all")}
    if since:
        out |= names("diff", "--name-only", "-z", "--no-renames", f"{since}...HEAD")
    return sorted(out)


def full_suite_due(changed: list[str]) -> str | None:
    """Why `changed` needs the full suite, or None when a targeted set will do."""
    for path in changed:
        if path in EVERYTHING or Path(path).name.startswith("requirements"):
            return f"{path} changed"
        if path.startswith("tests/") and not re.fullmatch(r"tests/test_[^/]*\.py", path):
            return f"{path} changed: a helper or fixture that tests may read"
    return None


def targeted_tests(repo: Path, changed: list[str]) -> list[str] | None:
    """The test files for `changed`, or None when the full suite is due:
    a shared file changed (`full_suite_due`), or nothing was picked, since
    a change no test names is not proof that no test reads it."""
    if full_suite_due(changed):
        return None
    tests = {p: (repo / p).read_text(encoding="utf-8", errors="replace")
             for p in (f"tests/{f.name}" for f in sorted((repo / "tests").glob("test_*.py")))}
    picked = {p for p in changed if p in tests}
    if picked:
        picked.update(TEST_GUARDS)
    scripts = {f.stem: f.read_text(encoding="utf-8", errors="replace")
               for f in sorted((repo / "scripts").glob("*.py"))}
    for path in changed:
        if path.startswith("tests/"):
            continue  # a test file picks itself above; a deleted one has nothing to run
        stem = Path(path).stem
        if path.endswith(".py"):
            # The tests that name the module, or name a script that imports it.
            word = re.compile(rf"\b{re.escape(stem)}\b")
            stems = [stem, *(s for s, text in scripts.items() if path.startswith("store/") and word.search(text))]
            needle = re.compile(rf"\b(?:{'|'.join(map(re.escape, stems))})\b")
        else:
            needle = re.compile(re.escape(Path(path).name))
        picked.update(t for t, text in tests.items() if needle.search(text))
        if path.endswith(DOC_SUFFIXES):
            picked.update(DOC_GUARDS)
        if path.startswith("manifests/"):
            picked.update(MANIFEST_GUARDS)
        if path.startswith("scripts/") and path.endswith(".py"):
            picked.update(SCRIPT_GUARDS)
    picked &= set(tests)  # a deleted test file is not run
    return sorted(picked) or None


def store_stamp(folder: Path | None = None) -> str | None:
    """Size and modification time of the store and its write-ahead log, or
    None where there is no store (CI). Imported late: the commit hook loads
    this file and must not import the store package."""
    if folder is None:
        sys.path.insert(0, str(ROOT))
        from store import store_dir
        try:
            folder = store_dir()
        except RuntimeError:
            return None
    parts = [f"{p.name}:{s.st_size}:{s.st_mtime_ns}" for p in (folder / "evidence.db", folder / "evidence.db-wal")
             if p.exists() and (s := p.stat())]
    return " ".join(parts) or None


def store_tests(repo: Path) -> list[str]:
    """The test files that carry the `live_store` marker."""
    return sorted(f"tests/{f.name}" for f in (repo / "tests").glob("test_*.py")
                  if "live_store" in f.read_text(encoding="utf-8", errors="replace"))


def store_checked(record: dict | None) -> str | None:
    """The store stamp the store's tests last passed on, from a verdict record."""
    return (record or {}).get("store_checked")


def with_store_tests(repo: Path, picked: list[str], stamp: str | None, last: dict | None) -> tuple[list[str], int]:
    """`picked` plus the store's test files when the store changed since
    they last passed, and how many were added."""
    if not stamp or stamp == store_checked(last):
        return picked, 0
    added = set(store_tests(repo)) - set(picked)
    return sorted(set(picked) | added), len(added)


def covers_the_store(picked: list[str] | None, extra: list[str], store_files: list[str]) -> bool:
    """Whether a run of `picked` (None: the full suite) with pytest
    arguments `extra` ran every store test. A filter (-k, -m) may deselect
    them, so only a run with no extra arguments counts (review of 7b65d12)."""
    return not extra and (picked is None or set(store_files) <= set(picked))


def verdict(rc: int, before: str, after: str, summary: str = "") -> str:
    """PASSED needs rc 0 AND a summary line that counts passed tests. 2026-11-07: `run_suite.py --help` reached
    pytest, exited 0 with no tests run, and was recorded PASSED for the tree, which a commit could have used."""
    if before != after:
        return "INVALID"
    return "PASSED" if rc == 0 and re.search(r"\b[1-9]\d* passed", summary) else "FAILED"


def main(argv: list[str]) -> int:
    try:
        last = json.loads((ROOT / VERDICT).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        last = None
    stamp = store_stamp()
    covers_store = not argv
    if "--changed" in argv:
        argv = list(argv)
        argv.remove("--changed")
        since = None
        if "--since" in argv:
            i = argv.index("--since")
            since = argv[i + 1]
            del argv[i:i + 2]
        changed = changed_files(ROOT, since)
        picked = targeted_tests(ROOT, changed)
        if picked is None:
            why = full_suite_due(changed) or "no test names what changed"
            print(f"--changed: {why}, so the full suite runs")
        else:
            print(f"--changed: {len(picked)} test files: {' '.join(Path(p).stem for p in picked)}")
            picked, added = with_store_tests(ROOT, picked, stamp, last)
            if added:
                print(f"--changed: the store changed since its tests last passed, so {added} more "
                      "test files with the live_store marker run too")
        covers_store = covers_the_store(picked, argv, store_tests(ROOT))
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
    result = verdict(rc, before, after, summary)
    record = {"verdict": result, "rc": rc, "tree": before, "tree_after": after, "args": argv,
              "summary": summary, "head": _git(ROOT, "rev-parse", "HEAD"),
              "store_checked": stamp if result == "PASSED" and covers_store else store_checked(last),
              "started": started.isoformat(timespec="seconds"),
              "finished": datetime.now().isoformat(timespec="seconds")}
    (ROOT / VERDICT).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    scope = "full suite" if not argv else "pytest " + " ".join(argv)
    why = " (files changed during the run; re-run on a still tree)" if result == "INVALID" else ""
    print(f"SUITE {result}: {summary}, rc={rc}, {scope}, tree {before[:10]}{why}")
    return 0 if result == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
