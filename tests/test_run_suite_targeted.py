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
        "scripts/sprint9_y.py": "from store import quotes_extra\n",
        "store/gone.py": "g = 1\n",
        "store/café.py": "c = 1\n",
        "tests/helpers.py": "\n",
        "tests/test_gone.py": "from store import gone\n",
        "tests/test_cafe.py": "import importlib; importlib.import_module('store.café')\n",
        "tests/test_y.py": "# runs scripts/sprint9_y.py\n",
        "docs/UNREAD.md": "nobody reads this\n",
        "docs/GUIDE.md": "guide\n",
        "tests/conftest.py": "\n",
        "tests/test_quotes.py": "from store.quotes import x\n",
        "tests/test_extra.py": "from store import quotes_extra\n",
        "tests/test_x.py": "# reads scripts/sprint9_x.py and docs/GUIDE.md\n",
        "tests/test_other.py": "\n",
        "tests/test_no_em_dashes.py": "\n",
        "tests/test_changelog_currency.py": "\n",
        "tests/test_sprint_documents.py": "\n",
        "tests/test_us_english.py": "\n",
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


def test_a_document_change_in_this_repository_runs_the_spelling_and_dash_guards():
    """Manual Validation Q3 (team lead, 2026-10-25: "q3 do now"): 6cfc137
    put "whilst" in two documents, --changed did not run test_us_english,
    and CI went red. The check runs on this repository's own tests, so a
    guard renamed or dropped from DOC_GUARDS fails here. Proven to fail by
    injection, 2026-10-25: with test_us_english.py taken out of DOC_GUARDS,
    this test went red. Restored."""
    rs = _runner()
    for doc in ("CHANGELOG.md", "docs/INTAKE_WORKFLOW.md"):
        picked = rs.targeted_tests(ROOT, [doc])
        assert {"tests/test_us_english.py", "tests/test_no_em_dashes.py"} <= set(picked), (doc, picked)
    # the fresh-eyes review of b0b41a3: test_intake reads every manifest. Proven to fail by injection,
    # 2026-10-25: with the manifests/ branch removed from targeted_tests, a new manifest picked no test_intake.
    assert "tests/test_intake.py" in rs.targeted_tests(ROOT, ["manifests/a_new_manifest.json"])
    # the fresh-eyes review of b6cdcd0: the other tests that read every file of a kind. Proven to fail by
    # injection, 2026-10-25: with each of the three branches removed in turn, its assertion went red.
    reader_file = rs.targeted_tests(ROOT, ["manifests/sprint13_reads/group_g09.json"])
    assert "tests/test_sprint13_read_ledger.py" in reader_file, reader_file
    script = set(rs.targeted_tests(ROOT, ["scripts/sprint13_read_ledger.py"]))
    assert set(rs.SCRIPT_GUARDS) <= script, script
    picked = rs.targeted_tests(ROOT, ["tests/test_reader_prompts.py"])
    assert "tests/test_guard_discipline.py" in picked
    # F140: a changed test file changes its inventory row, so the inventory check runs too. Proven red 2026-11-07:
    # with test_test_inventory left out of TEST_GUARDS (INJECTED), this assertion failed.
    assert "tests/test_test_inventory.py" in picked


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


def test_a_deleted_or_renamed_module_picks_the_tests_that_still_name_it(repo):
    """The review of fdedff9: a deleted file was skipped before its name
    was searched, so the tests it breaks never ran. Proven to fail by
    injection, 2026-10-23: with the deleted-file skip put back, test_gone
    was not picked. Restored."""
    rs = _runner()
    (repo / "store" / "gone.py").unlink()
    assert rs.changed_files(repo) == ["store/gone.py"]
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == ["tests/test_gone.py"]
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--", "store/gone.py"], check=True)
    subprocess.run(["git", "-C", str(repo), "mv", "store/gone.py", "store/kept.py"], check=True)  # staged rename
    assert rs.changed_files(repo) == ["store/gone.py", "store/kept.py"]
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == ["tests/test_gone.py"]


def test_a_non_ascii_path_is_read_whole(repo):
    """Porcelain without -z quotes and escapes it, so it was dropped."""
    rs = _runner()
    (repo / "store" / "café.py").write_text("c = 2\n", encoding="utf-8")
    assert rs.changed_files(repo) == ["store/café.py"]
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == ["tests/test_cafe.py"]


def test_a_store_module_picks_the_tests_of_the_scripts_that_import_it(repo):
    rs = _runner()
    (repo / "store" / "quotes_extra.py").write_text("y = 2\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == ["tests/test_extra.py", "tests/test_y.py"]


def test_a_store_write_adds_the_store_tests(repo, tmp_path_factory):
    """Sprint 12 retrospective I1: a store write changes no repository
    file, so `--changed` never ran the store's tests after an apply.
    Proven to fail by injection, 2026-10-24: with `with_store_tests`
    returning `picked` unchanged, this test failed at the first `added`.
    Restored."""
    rs = _runner()
    (repo / "tests" / "test_live.py").write_text("@pytest.mark.live_store\n", encoding="utf-8")
    store = tmp_path_factory.mktemp("store")
    assert rs.store_stamp(store) is None
    (store / "evidence.db").write_bytes(b"one")
    before = rs.store_stamp(store)
    picked = ["tests/test_quotes.py"]
    # never checked, then checked at this stamp, then written again
    assert rs.with_store_tests(repo, picked, before, None) == (["tests/test_live.py", "tests/test_quotes.py"], 1)
    assert rs.with_store_tests(repo, picked, before, {"store_checked": before}) == (picked, 0)
    (store / "evidence.db-wal").write_bytes(b"a write")
    after = rs.store_stamp(store)
    assert after != before
    assert rs.with_store_tests(repo, picked, after, {"store_checked": before})[1] == 1
    assert rs.with_store_tests(repo, picked, None, None) == (picked, 0)  # no store, as on CI


def test_a_filtered_run_does_not_mark_the_store_checked():
    """The review of 7b65d12: `--changed -m "not live_store"` after a store
    write added the store tests, pytest deselected them, and the PASSED run
    recorded the store as checked. Proven to fail by injection, 2026-10-24:
    with `not extra and` removed, the filtered run counted. Restored."""
    rs = _runner()
    store = ["tests/test_live.py"]
    assert rs.covers_the_store(None, [], store)
    assert rs.covers_the_store(["tests/test_live.py", "tests/test_x.py"], [], store)
    assert not rs.covers_the_store(["tests/test_x.py"], [], store)
    assert not rs.covers_the_store(["tests/test_live.py"], ["-m", "not live_store"], store)
    assert not rs.covers_the_store(None, ["-k", "foo"], store)


def test_a_helper_or_an_unnamed_change_runs_the_full_suite(repo):
    """Never "nothing to run": the runner said SUITE SKIPPED and exited 0
    for a change no test named (review of fdedff9). Proven to fail by
    injection, 2026-10-23: with `or None` removed from the return, the
    new data file gave []. Restored."""
    rs = _runner()
    (repo / "docs" / "UNREAD.md").write_text("changed\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) == sorted(rs.DOC_GUARDS)
    (repo / "docs" / "UNREAD.md").write_text("nobody reads this\n", encoding="utf-8")
    (repo / "data.txt").write_text("new\n", encoding="utf-8")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) is None
    (repo / "data.txt").unlink()
    (repo / "tests" / "helpers.py").write_text("# changed\n", encoding="utf-8")
    assert rs.full_suite_due(rs.changed_files(repo)) == (
        "tests/helpers.py changed: a helper or fixture that tests may read")
    assert rs.targeted_tests(repo, rs.changed_files(repo)) is None
