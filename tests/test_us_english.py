"""Tracked living markdown uses US English spellings (Sprint 3 Task C, F13).

CLAUDE.md, 2026-09-17: "this repository is written in US English."

WHAT IS DELIBERATELY EXEMPT, and the exemption matters more than the rule:

  - Every ADR (`docs/adr/0001-*.md` through `docs/adr/0005-*.md`):
    ADR-0004's own standing rule is "revisions are recorded as dated
    amendments... never as edits in place." A first version of
    scripts/us_english_fix.py (2026-09-18) shipped WITHOUT this exclusion
    and rewrote frozen amendment prose before being caught in Task C's
    own smoke test and reverted uncommitted -- this test's exclusion list
    exists so that mistake cannot recur silently.
  - Every sprint doc under `docs/sprints/` (plan, retrospective, summary):
    same reasoning -- a point-in-time record of what was decided or
    found, never rewritten after the fact.
  - `docs/adr/README.md` and `docs/adr/template.md` stay IN SCOPE: they
    are living process docs about how to write an ADR, not ADRs
    themselves.

`scripts/us_english_fix.py` applies the conversion this test enforces.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "us_english_fix.py"


def _load_fixer():
    """The word list, the exclusions and the protected spans are imported
    FROM the script, not restated here (PR #20 review, 2026-09-19). An
    earlier version of this file carried its own copies of all four; the
    reviewer emptied the script's exclusion lists and the suite stayed
    green while a dry run planned 18 rewrites inside frozen ADRs -- the
    exact 2026-09-18 incident the exclusions exist to prevent, silent
    because the test was checking its own copy. One source of truth, and
    the tests below exercise the script's own values."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("us_english_fix", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_FIXER = _load_fixer()
EXCLUDE_PREFIXES = _FIXER.EXCLUDE_PREFIXES
EXCLUDE_FILES = _FIXER.EXCLUDE_FILES
BRITISH = tuple(brit for brit, _ in _FIXER.PAIRS)
PROTECTED = _FIXER.PROTECTED

# The five ADRs and the sprints directory, HARDCODED here as the expected
# exclusion set. Checking the script's exclusion lists against themselves
# cannot fail; checking them against this independent statement of what
# must be frozen can.
FROZEN_ADRS = (
    "docs/adr/0001-branch-and-carry-forward-model.md",
    "docs/adr/0002-secrets-and-credential-handling.md",
    "docs/adr/0003-store-and-schema-discipline.md",
    "docs/adr/0004-evidence-based-db.md",
    "docs/adr/0005-reference-library.md",
)
FROZEN_PREFIX = "docs/sprints/"

PATTERN = re.compile(r"\b(" + "|".join(BRITISH) + r")\b", re.IGNORECASE)


def _tracked_markdown() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    files = []
    for rel in out.stdout.splitlines():
        if rel in EXCLUDE_FILES:
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        p = ROOT / rel
        if p.is_file():
            files.append(p)
    return files


FILES = _tracked_markdown()


def test_the_file_list_is_not_empty():
    """A guard with an empty population passes trivially -- if `git
    ls-files` fails, every parametrized case below vanishes and the suite
    stays green while checking nothing."""
    assert len(FILES) > 15, (
        f"expected a real population of tracked living markdown, found {len(FILES)}. "
        "The guard below would be vacuous.")


def test_the_frozen_documents_are_actually_excluded():
    """The exemption must hold, or a sweep could rewrite an ADR's frozen
    amendment or a sprint's own historical record.

    Checked against a HARDCODED prefix, not the module's own
    EXCLUDE_PREFIXES constant -- checking a broken exclusion list against
    itself can never fail (`str.startswith(())` is always False for an
    empty tuple), which is exactly the vacuous-guard shape this
    repository's own CLAUDE.md names as a recurring class. Caught by
    injection: emptying EXCLUDE_PREFIXES to `()` and re-running a version
    of this test that checked `r.startswith(EXCLUDE_PREFIXES)` still
    passed, silently, because the check and the break shared the same
    broken constant."""
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True)
    all_tracked = set(out.stdout.splitlines())
    rels = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES}
    for excluded in FROZEN_ADRS:
        assert excluded in all_tracked, f"{excluded} no longer exists -- update FROZEN_ADRS and the script"
        assert excluded not in rels, f"{excluded} is in scope but must be excluded (frozen ADR)"
    leaked = [r for r in rels if r.startswith(FROZEN_PREFIX)]
    assert not leaked, f"sprint docs are in scope but must be excluded (frozen record): {leaked}"


def test_adr_readme_and_template_stay_in_scope():
    """The two non-ADR files under docs/adr/ are living process docs, not
    frozen decision records, and must NOT be swept into the exclusion by
    an over-broad prefix match on 'docs/adr/'."""
    rels = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES}
    assert "docs/adr/README.md" in rels
    assert "docs/adr/template.md" in rels


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_british_spellings(path: Path):
    text = path.read_text(encoding="utf-8")

    for span in PROTECTED:
        text = text.replace(span, " " * len(span))

    offenders = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in PATTERN.finditer(line):
            offenders.append(f"  line {lineno}: {m.group(0)!r} in {line.strip()[:70]!r}")

    assert not offenders, (
        f"{path.relative_to(ROOT)} uses British spellings; this repository "
        "writes US English (CLAUDE.md, 2026-09-17):\n"
        + "\n".join(offenders[:10])
        + "\n\nRun scripts/us_english_fix.py --apply to convert.")


BRITISH_LINE = "The colour of the behaviour.\n"


def _run_fixer_in_temp_repo(
    tmp_path: Path, args: list[str], files: dict[str, str] | None = None
) -> tuple[subprocess.CompletedProcess, Path]:
    """Run the REAL scripts/us_english_fix.py against a throwaway git repo
    holding the given tracked markdown files (default: one NOTES.md with a
    British spelling), by monkeypatching the loaded module's ROOT (same
    wrapper pattern as tests/test_ingest_seed_set.py). Never runs against
    this repository's own tree -- the first version of the fixer did
    exactly that and rewrote frozen documents. Returns (process, repo)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    for rel, text in (files or {"NOTES.md": BRITISH_LINE}).items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=repo, check=True)
    wrapper = (
        "import sys, importlib.util\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('usfix', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        f"mod.ROOT = Path({str(repo)!r})\n"
        f"raise SystemExit(mod.main({args!r}))\n"
    )
    proc = subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True)
    return proc, repo


def test_fixer_is_dry_run_by_default(tmp_path):
    """Sprint 3 retrospective improvement 1: a write-shaped one-off script
    shows its plan and writes nothing unless told to. The fixer's first
    run (2026-09-18) had no such mode and rewrote frozen ADR amendments
    before the exclusion list existed."""
    proc, repo = _run_fixer_in_temp_repo(tmp_path, [])
    assert proc.returncode == 0, proc.stderr
    assert "2 replacements across 1 files" in proc.stdout
    assert "dry run" in proc.stdout
    assert (repo / "NOTES.md").read_text(encoding="utf-8") == BRITISH_LINE


def test_fixer_writes_only_with_apply(tmp_path):
    proc, repo = _run_fixer_in_temp_repo(tmp_path, ["--apply"])
    assert proc.returncode == 0, proc.stderr
    assert "applied" in proc.stdout
    assert (repo / "NOTES.md").read_text(encoding="utf-8") == "The color of the behavior.\n"


def test_fixer_never_rewrites_frozen_documents_even_with_apply(tmp_path):
    """PR #20 review (2026-09-19): the SCRIPT's own exclusion lists were
    untested -- emptying them left the suite green. This runs the real
    script with --apply against a repo holding a British spelling in a
    frozen ADR, a sprint doc, and a living README, and asserts only the
    README changed. Proven by injection: with EXCLUDE_FILES and
    EXCLUDE_PREFIXES emptied in the script, all three files change and
    this test fails."""
    files = {
        "docs/adr/0004-evidence-based-db.md": BRITISH_LINE,
        "docs/sprints/SPRINT_9_PLAN.md": BRITISH_LINE,
        "README.md": BRITISH_LINE,
    }
    proc, repo = _run_fixer_in_temp_repo(tmp_path, ["--apply"], files)
    assert proc.returncode == 0, proc.stderr
    assert (repo / "docs/adr/0004-evidence-based-db.md").read_text(encoding="utf-8") == BRITISH_LINE
    assert (repo / "docs/sprints/SPRINT_9_PLAN.md").read_text(encoding="utf-8") == BRITISH_LINE
    assert (repo / "README.md").read_text(encoding="utf-8") == "The color of the behavior.\n"
    assert "2 replacements across 1 files" in proc.stdout
