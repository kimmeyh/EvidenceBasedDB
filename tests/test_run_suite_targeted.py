"""F100 (Sprint 12 Task B): `scripts/run_suite.py --changed`, the tests for
what a commit changed, in a scratch repository."""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _runner():
    spec = importlib.util.spec_from_file_location("run_suite", ROOT / "scripts" / "run_suite.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def repo(tmp_path):
    files = {
        "store/quotes.py": "x = 1\n",
        "store/quotes_extra.py": "y = 1\n",
        "scripts/sprint9_x.py": "z = 1\n",
        "docs/GUIDE.md": "guide\n",
        "tests/conftest.py": "\n",
        "tests/test_quotes.py": "from store.quotes import x\n",
        "tests/test_extra.py": "from store import quotes_extra\n",
        "tests/test_x.py": "# reads scripts/sprint9_x.py and docs/GUIDE.md\n",
        "tests/test_other.py": "\n",
        "tests/test_no_em_dashes.py": "\n",
        "tests/test_changelog_currency.py": "\n",
        "tests/test_sprint_documents.py": "\n",
    }
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text, encoding="utf-8")
    git = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    return tmp_path


def test_a_changed_module_picks_the_tests_that_name_it_as_a_word(repo):
    """`quotes` must not pick the test of `quotes_extra`. Proven to fail by
    injection, 2026-10-23: with the word boundaries removed from the
    pattern, test_extra was picked too. Restored."""
    rs = _runner()
    (repo / "store" / "quotes.py").write_text("x = 2\n", encoding="utf-8")
    changed = rs.changed_files(repo)
    assert changed == ["store/quotes.py"]  # the first status line keeps its path whole
    assert rs.targeted_tests(repo, changed) == ["tests/test_quotes.py"]


def test_a_document_picks_its_readers_and_the_document_guards(repo):
    rs = _runner()
    (repo / "docs" / "GUIDE.md").write_text("changed\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == sorted(["tests/test_x.py", *rs.DOC_GUARDS])


def test_a_new_test_file_runs_itself_and_conftest_runs_everything(repo):
    rs = _runner()
    (repo / "tests" / "test_new.py").write_text("\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == ["tests/test_new.py"]
    (repo / "tests" / "conftest.py").write_text("# changed\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) is None


def test_since_adds_committed_changes(repo):
    rs = _runner()
    base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    (repo / "scripts" / "sprint9_x.py").write_text("z = 2\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "x"],
                   check=True)
    assert rs.changed_files(repo) == []
    assert rs.changed_files(repo, base) == ["scripts/sprint9_x.py"]
    assert rs.targeted_tests(repo, rs.changed_files(repo, base)) == ["tests/test_x.py"]
