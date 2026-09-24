"""Store durability (Sprint 5 Task A, F30): rebuild, backup, retention, restore.

Every guard here carries its own injection: the test builds the broken
case and asserts it is caught, so "proven to fail" is re-proven on every
run rather than once in a terminal. The rebuild tests run on CI too: they
need only the committed export, not store/evidence.db, which is why the
door's local-path rule is switched off explicitly for them.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import backup as backup_mod  # noqa: E402
from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import PaperRecord, validate_paper  # noqa: E402
from store.rebuild import (  # noqa: E402
    EXPORT_FILES, KNOWN_KEYS, UnrestorableKey, compare_exports, rebuild, rebuild_and_compare,
)

EXPORT_DIR = ROOT / "export"


def _copy_export(tmp_path: Path) -> Path:
    dst = tmp_path / "export"
    dst.mkdir()
    for name in EXPORT_FILES:
        shutil.copy2(EXPORT_DIR / name, dst / name)
    return dst


def _store(tmp_path: Path, name: str = "evidence.db") -> Path:
    """A realistic store: the committed export, rebuilt."""
    db = tmp_path / name
    rebuild(EXPORT_DIR, db, check_local_paths=False).close()
    return db


# ---------------------------------------------------------------- rebuild

def test_committed_export_rebuilds_byte_identically():
    """ADR-0004 section 2's claim, executed: the export is a complete
    artifact. Proven to fail by test_rebuild_detects_a_deliberately_lost_field
    below, which drops a field and watches this same comparison go red."""
    assert rebuild_and_compare(EXPORT_DIR, check_local_paths=False) == []


def test_rebuild_detects_a_deliberately_lost_field(tmp_path, monkeypatch):
    """Injection: a paper exports a field the rebuild is told it knows but
    cannot actually write (insert_paper has no reading_level). The
    byte-identity comparison must report papers.json."""
    export = _copy_export(tmp_path)
    papers = json.loads((export / "papers.json").read_text(encoding="utf-8"))
    papers[0]["reading_level"] = 12
    (export / "papers.json").write_text(json.dumps(papers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setitem(KNOWN_KEYS, "paper", KNOWN_KEYS["paper"] | {"reading_level"})
    assert rebuild_and_compare(export, check_local_paths=False) == ["papers.json"]


def test_rebuild_refuses_an_unrestorable_key(tmp_path):
    export = _copy_export(tmp_path)
    papers = json.loads((export / "papers.json").read_text(encoding="utf-8"))
    papers[0]["kind"] = "paper"  # a field the store has no column for
    (export / "papers.json").write_text(json.dumps(papers, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(UnrestorableKey, match="kind"):
        rebuild(export, tmp_path / "x.db", check_local_paths=False)
    assert not (tmp_path / "x.db").exists(), "a failed rebuild must not leave a half-built store"


def test_rebuild_never_overwrites_an_existing_store(tmp_path):
    db = _store(tmp_path)
    with pytest.raises(FileExistsError):
        rebuild(EXPORT_DIR, db, check_local_paths=False)


def test_local_path_rule_stays_on_by_default(tmp_path):
    """The rebuild's exception is opt-in. Injection: a hand-origin paper
    whose file does not exist must still be refused by default."""
    paper = PaperRecord(
        id="x-2026-t", tier="seen", access=str(tmp_path / "missing.pdf"), disposition="Test.",
        context="method", value="T", citation="X. T. (hand-transcribed from cover)",
        citation_origin="hand", hand_transcribed_from="cover", updated="2026-09-24", updated_reason="t",
    )
    with pytest.raises(ValueError, match="not an existing local path"):
        validate_paper(paper)
    validate_paper(paper, check_local_paths=False)  # every other rule still ran and passed


# ---------------------------------------------------------------- backup

def test_backup_is_verified_and_counts_match(tmp_path):
    db = _store(tmp_path)
    path = backup_mod.backup_store(db, tmp_path / "backups", "unit test", 5)
    assert backup_mod.parse_name(path)[1] == 5
    src, dst = sqlite3.connect(db), sqlite3.connect(path)
    try:
        source_counts = backup_mod._class_counts(src)
        assert source_counts and backup_mod._class_counts(dst) == source_counts
        assert dst.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        src.close()
        dst.close()


def test_backup_verification_detects_a_deliberately_corrupted_backup(tmp_path):
    """Injection: overwrite the middle of a real backup with garbage; the
    verification must raise, never report ok."""
    db = _store(tmp_path)
    path = backup_mod.backup_store(db, tmp_path / "backups", "corrupt me", 5)
    data = bytearray(path.read_bytes())
    for i in range(4096, min(len(data), 4096 * 6)):
        data[i] = 0xAB
    path.write_bytes(bytes(data))
    with pytest.raises(backup_mod.BackupVerificationError):
        backup_mod.verify_backup(path, {"paper": 48})


def test_backup_verification_detects_a_count_mismatch(tmp_path):
    db = _store(tmp_path)
    path = backup_mod.backup_store(db, tmp_path / "backups", "count", 5)
    with pytest.raises(backup_mod.BackupVerificationError, match="record counts"):
        backup_mod.verify_backup(path, {"paper": 999})


def test_a_failed_backup_blocks_the_intake_write(tmp_path, monkeypatch):
    """intake.py --apply must take the backup BEFORE it opens the store for
    writing. Injection: the backup raises; the store must never be opened."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("intake_mod", ROOT / "scripts" / "intake.py")
    intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(intake)
    db = _store(tmp_path)
    monkeypatch.setattr(intake, "DB_PATH", db)

    def boom(*a, **k):
        raise backup_mod.BackupVerificationError("injected")
    opened = []
    monkeypatch.setattr(intake, "backup_before_write", boom)
    monkeypatch.setattr(intake, "connect", lambda p: opened.append(p))
    with pytest.raises(backup_mod.BackupVerificationError):
        intake.main(["arXiv:2602.11092", "--context", "qml", "--disposition", "t", "--apply"])
    assert opened == []


# Scripts that write to the store under --apply but are historical one-offs
# (a sprint's own correction pass, a migration already applied). Each would
# be wrong to re-run; wiring a backup into them adds nothing. A NEW write
# script is not on this list, so the test below makes it back up.
HISTORICAL_ONE_OFFS = {
    "apply_paper_applicability.py": "Sprint 3 Task D one-off, applied",
    "ingest_lenat_marcus.py": "Sprint 1 one-off, applied",
    "ingest_seed_set.py": "Sprint 1 seed loader, retired by Sprint 4 Task C",
    "ingest_hsbc_b1_variable_count.py": "Sprint 2 one-off, applied",
    "migrate_paper_fields_drop_citation.py": "Sprint 4 Task B migration, applied",
    "recover_updated_reason_history.py": "PR #30 round-2 recovery, applied",
    "sprint4_remove_pere_placeholder.py": "Sprint 4 Manual Validation one-off, applied",
    "sprint4_task_c_corrections.py": "Sprint 4 Task C one-off, applied",
    "sprint4_task_f_refiling.py": "Sprint 4 Task F one-off, applied",
    "sprint4_task_h_extraction.py": "Sprint 4 Task H one-off, applied",
    "us_english_fix.py": "Sprint 3 doc fixer; does not open the store",
    # Opens the store READ-ONLY (which arXiv ids are already records); its
    # --apply writes downloads to D:/Data/Harold/EvidenceBasedDB, never the
    # store. Caught by this test on 2026-09-24 and listed deliberately.
    "sprint5_bibliography.py": "reads the store only; --apply downloads outside the repository",
}


def test_every_live_write_script_backs_up_before_apply():
    """Coverage, not behavior: every script under scripts/ that accepts
    --apply and opens the store either calls backup_before_write or is a
    named historical one-off. The behavior itself is executed by
    test_a_failed_backup_blocks_the_intake_write. Proven to fail by
    reverting the refresh_citations.py call during development (it was
    reported as missing)."""
    missing = []
    for f in sorted((ROOT / "scripts").glob("*.py")):
        text = f.read_text(encoding="utf-8")
        if "--apply" in text and "connect(DB_PATH)" in text and f.name not in HISTORICAL_ONE_OFFS:
            if "backup_before_write(" not in text:
                missing.append(f.name)
    assert missing == [], f"write scripts with no verified backup before --apply: {missing}"


# ---------------------------------------------------------------- retention

def _fake_backup(src: Path, d: Path, when: datetime, sprint: int) -> Path:
    d.mkdir(exist_ok=True)
    p = d / f"evidence-{when.strftime(backup_mod._STAMP)}-sprint{sprint}-t.db"
    shutil.copy2(src, p)
    return p


def test_retention_deletes_only_what_all_three_rules_allow(tmp_path, monkeypatch):
    db = _store(tmp_path)
    d = tmp_path / "backups"
    now = datetime(2026, 12, 1, 12, 0, 0)
    old = now - timedelta(days=40)
    recent = _fake_backup(db, d, now - timedelta(days=3), 12)
    old_s5_a = _fake_backup(db, d, old - timedelta(hours=1), 5)
    old_s5_newest = _fake_backup(db, d, old, 5)
    old_s11_newest = _fake_backup(db, d, old, 11)
    uncommitted = _fake_backup(db, d, old - timedelta(hours=2), 5)
    committed = {old_s5_a.name, old_s5_newest.name, old_s11_newest.name}
    monkeypatch.setattr(backup_mod, "committed_export_blobs", lambda repo: {"x"})
    monkeypatch.setattr(backup_mod, "content_is_committed", lambda p, blobs, repo=None: p.name in committed)
    deleted, kept = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12)
    reasons = {p.name: r for p, r in kept}
    assert [p.name for p in deleted] == [old_s5_a.name, old_s5_newest.name]
    assert "32 days" in reasons[recent.name]
    assert "last 5 sprints" in reasons[old_s11_newest.name]   # sprint 11 is within 12-4..12
    assert "not yet in a committed export" in reasons[uncommitted.name]
    assert all(p.exists() for p in (recent, old_s11_newest, uncommitted))


def test_retention_keeps_everything_when_git_cannot_answer(tmp_path, monkeypatch):
    db = _store(tmp_path)
    d = tmp_path / "backups"
    now = datetime(2026, 12, 1)
    p = _fake_backup(db, d, now - timedelta(days=90), 1)
    monkeypatch.setattr(backup_mod, "committed_export_blobs", lambda repo: None)
    deleted, _ = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12)
    assert deleted == [] and p.exists()


def test_rule_three_recognizes_committed_content_and_rejects_a_deliberately_changed_store(tmp_path):
    """Rule 3 against real git history. A store rebuilt from the committed
    export IS committed content; the same store with one record changed is
    NOT (injection). Hashes through git so CRLF/LF normalization matches a
    commit (autocrlf: the working copy and the blob differ)."""
    db = _store(tmp_path)
    blobs = backup_mod.committed_export_blobs(ROOT)
    assert blobs, "git history under export/ must be readable here"
    assert backup_mod.content_is_committed(db, blobs, ROOT) is True
    conn = sqlite3.connect(db)
    conn.execute("UPDATE records SET updated_reason = updated_reason || ' x' WHERE class = 'paper' "
                 "AND id = (SELECT MIN(id) FROM records WHERE class = 'paper')")
    conn.commit()
    conn.close()
    assert backup_mod.content_is_committed(db, blobs, ROOT) is False


# ---------------------------------------------------------------- restore

def test_restore_brings_back_the_backed_up_content(tmp_path):
    """Back up, damage the store (delete a paper), restore, and prove the
    regenerated export matches the committed one. Proven to fail by the
    damaged state itself: the comparison is asserted non-empty before the
    restore runs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("restore_mod", ROOT / "scripts" / "restore_store.py")
    restore_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(restore_mod)

    db = _store(tmp_path)
    saved = backup_mod.backup_store(db, tmp_path / "backups", "before damage", 5)
    conn = connect(db)
    victim = conn.execute("SELECT id FROM records WHERE class='paper' ORDER BY id LIMIT 1").fetchone()[0]
    conn.execute("DELETE FROM paper_applicability WHERE record_id = ?", (victim,))
    conn.execute("DELETE FROM paper_yields WHERE paper_id = ?", (victim,))
    conn.execute("DELETE FROM records WHERE id = ?", (victim,))
    conn.commit()
    damaged = tmp_path / "damaged"
    regenerate(conn, damaged)
    conn.close()
    assert "papers.json" in compare_exports(EXPORT_DIR, damaged)

    restore_mod.restore(saved, db)
    conn = connect(db)
    try:
        regenerate(conn, tmp_path / "restored")
    finally:
        conn.close()
    assert compare_exports(EXPORT_DIR, tmp_path / "restored") == []
