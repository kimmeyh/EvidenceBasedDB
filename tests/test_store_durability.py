"""Store durability (Sprint 5 Task A, F30): rebuild, backup, retention, restore.

Every guard here carries its own injection: the test builds the broken
case and asserts it is caught, so "proven to fail" is re-proven on every
run rather than once in a terminal.

Since ADR-0004 A7 (Sprint 7 Task B, 2026-10-06) there is no committed
export. The mechanism tests run on a small synthetic store (conftest.py
`build_synthetic_store`) and its on-demand dump, everywhere, CI included;
one `live_store` test keeps the round trip over the real data, locally.
"""
from __future__ import annotations

import json
import re
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

from conftest import build_synthetic_store  # noqa: E402


def _store(tmp_path: Path, name: str = "evidence.db") -> Path:
    """A small store exercising every record shape the door writes."""
    return build_synthetic_store(tmp_path / name)


def _dump(tmp_path: Path, name: str = "export") -> Path:
    """An on-demand dump of a fresh synthetic store, in its own folder."""
    db = _store(tmp_path, f"{name}_source.db")
    conn = connect(db)
    try:
        regenerate(conn, tmp_path / name)
    finally:
        conn.close()
    return tmp_path / name


# ---------------------------------------------------------------- rebuild

def test_a_dump_rebuilds_byte_identically(tmp_path):
    """The dump is a complete copy of the store: rebuilt, it dumps the same
    bytes. Proven to fail by test_rebuild_detects_a_deliberately_lost_field
    below, which drops a field and watches this same comparison go red."""
    assert rebuild_and_compare(_dump(tmp_path), check_local_paths=False) == []


@pytest.mark.live_store
def test_the_live_store_round_trips_through_a_dump(live_export):
    """ADR-0004 A7 (c): the on-demand dump stays a proven recovery path for
    the REAL data: dump the live store, rebuild from the dump, dump again,
    compare bytes."""
    assert rebuild_and_compare(live_export, check_local_paths=False) == []


def test_rebuild_detects_a_deliberately_lost_field(tmp_path, monkeypatch):
    """Injection: a paper exports a field the rebuild is told it knows but
    cannot actually write (insert_paper has no reading_level). The
    byte-identity comparison must report papers.json."""
    export = _dump(tmp_path)
    papers = json.loads((export / "papers.json").read_text(encoding="utf-8"))
    papers[0]["reading_level"] = 12
    (export / "papers.json").write_text(json.dumps(papers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setitem(KNOWN_KEYS, "paper", KNOWN_KEYS["paper"] | {"reading_level"})
    assert rebuild_and_compare(export, check_local_paths=False) == ["papers.json"]


def test_rebuild_refuses_an_unrestorable_key(tmp_path):
    export = _dump(tmp_path)
    papers = json.loads((export / "papers.json").read_text(encoding="utf-8"))
    papers[0]["kind"] = "paper"  # a field the store has no column for
    (export / "papers.json").write_text(json.dumps(papers, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(UnrestorableKey, match="kind"):
        rebuild(export, tmp_path / "x.db", check_local_paths=False)
    assert not (tmp_path / "x.db").exists(), "a failed rebuild must not leave a half-built store"


def test_rebuild_never_overwrites_an_existing_store(tmp_path):
    db = _store(tmp_path)
    with pytest.raises(FileExistsError):
        rebuild(_dump(tmp_path), db, check_local_paths=False)


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
}


_OPENS_STORE = re.compile(r"connect\((?:\w+\.)?DB_PATH\)")
_WRITES_STORE = re.compile(r"insert_paper\(|insert_assertion\(|set_tier\(|append_updated_reason\(|INSERT INTO|"
                           r"UPDATE \w+ SET|DELETE FROM|[^_]intake\(conn")


def test_every_live_write_script_backs_up_before_apply():
    """Coverage, not behavior: every script under scripts/ that opens the
    store AND calls a write primitive either calls backup_before_write or
    is a named historical one-off. The behavior itself is executed by
    test_a_failed_backup_blocks_the_intake_write.

    First version matched the TEXT "--apply" plus "connect(DB_PATH)"; the
    fresh-eyes review (2026-09-24) called that loose, and it proved so the
    same day, flagging read-only learnings.py for an error message that
    mentions --apply while a writer using `connect(bib.DB_PATH)` would have
    slipped past. It now asks what it means: does the script write?
    Proven to fail by reverting the refresh_citations.py call (reported as
    missing) and, for this version, by the same revert re-run."""
    missing = []
    for f in sorted((ROOT / "scripts").glob("*.py")):
        text = f.read_text(encoding="utf-8")
        if _OPENS_STORE.search(text) and _WRITES_STORE.search(text) and f.name not in HISTORICAL_ONE_OFFS:
            if "backup_before_write(" not in text:
                missing.append(f.name)
    assert missing == [], f"write scripts with no verified backup before --apply: {missing}"


# ---------------------------------------------------------------- retention

def _fake_backup(src: Path, d: Path, when: datetime, sprint: int) -> Path:
    d.mkdir(exist_ok=True)
    p = d / f"evidence-{when.strftime(backup_mod._STAMP)}-sprint{sprint}-t.db"
    shutil.copy2(src, p)
    return p


def test_retention_deletes_only_what_all_three_rules_allow(tmp_path):
    """ADR-0004 A7 (d): deleted only when older than 32 days AND not the
    newest of one of the last 5 sprints AND not one of the 10 newest."""
    db = _store(tmp_path)
    d = tmp_path / "backups"
    now = datetime(2026, 12, 1, 12, 0, 0)
    recent = _fake_backup(db, d, now - timedelta(days=3), 12)
    s11 = _fake_backup(db, d, now - timedelta(days=60), 11)          # oldest, but its sprint is recent
    s5 = [_fake_backup(db, d, now - timedelta(days=41, hours=i), 5) for i in range(11)]
    deleted, kept = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12)
    reasons = {p.name: r for p, r in kept}
    # Ten newest: `recent` and s5[0..8]. Deletable: s5[9] and s5[10].
    assert [p.name for p in deleted] == [s5[10].name, s5[9].name]
    assert "32 days" in reasons[recent.name]
    assert "last 5 sprints" in reasons[s11.name]          # sprint 11 is within 12-4..12
    assert "10 newest" in reasons[s5[0].name]
    assert all(p.exists() for p in (recent, s11, *s5[:9]))


def test_the_ten_newest_backups_survive_whatever_their_age_regression(tmp_path, monkeypatch):
    """Rule 3 since ADR-0004 A7: at least ten backups survive, so a long
    pause can never prune every copy. Proven to fail by injection, inside
    this test: with KEEP_NEWEST set to 0, all twelve old backups go."""
    db = _store(tmp_path)
    d = tmp_path / "backups"
    now = datetime(2026, 12, 1)
    olds = [_fake_backup(db, d, now - timedelta(days=100, hours=i), 1) for i in range(12)]
    deleted, _ = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12, apply=False)
    assert sorted(p.name for p in deleted) == sorted(p.name for p in olds[10:])
    monkeypatch.setattr(backup_mod, "KEEP_NEWEST", 0)
    deleted, _ = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12, apply=False)
    assert len(deleted) == 12


# ---------------------------------------------------------------- restore

def test_restore_brings_back_the_backed_up_content(tmp_path):
    """Back up, damage the store (delete a paper), restore, and prove the
    restored store dumps exactly what it dumped before the damage. Proven to
    fail by the damaged state itself: the comparison is asserted non-empty
    before the restore runs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("restore_mod", ROOT / "scripts" / "restore_store.py")
    restore_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(restore_mod)

    db = _store(tmp_path)
    before = tmp_path / "before"
    conn = connect(db)
    regenerate(conn, before)
    conn.close()
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
    assert "papers.json" in compare_exports(before, damaged)

    restore_mod.restore(saved, db)
    conn = connect(db)
    try:
        regenerate(conn, tmp_path / "restored")
    finally:
        conn.close()
    assert compare_exports(before, tmp_path / "restored") == []


# ------------------------------------------- fresh-eyes review fixes (2026-09-24)

def _restore_mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("restore_mod2", ROOT / "scripts" / "restore_store.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_restore_recovers_a_deliberately_corrupted_live_store(tmp_path, monkeypatch):
    """The main reason to restore. Injection: garbage over the live store's
    pages; the first version raised BackupVerificationError from the
    pre-restore backup and never restored. The corrupt file is kept aside,
    never deleted."""
    m = _restore_mod()
    db = _store(tmp_path)
    before = tmp_path / "before"
    conn = connect(db)
    regenerate(conn, before)
    conn.close()
    saved = backup_mod.backup_store(db, tmp_path / "backups", "good state", 5)
    data = bytearray(db.read_bytes())
    for i in range(4096, min(len(data), 4096 * 8)):
        data[i] = 0xCD
    db.write_bytes(bytes(data))
    monkeypatch.setattr(m, "DB_PATH", db)
    assert m.main([str(saved), "--apply"]) == 0
    assert list((tmp_path / "backups").glob("*unverified-live-store-before-restore.db")), "corrupt store kept aside"
    conn = connect(db)
    try:
        regenerate(conn, tmp_path / "restored")
    finally:
        conn.close()
    assert compare_exports(before, tmp_path / "restored") == []


def test_prune_never_deletes_a_protected_backup(tmp_path, monkeypatch):
    """restore_store.py protects the backup it restores from the prune in
    its own pre-restore backup. Injection: the same old backup, which no
    rule keeps (beyond the ten newest, sprint long past), IS deleted
    without `protect`."""
    db = _store(tmp_path)
    d = tmp_path / "backups"
    now = datetime(2026, 12, 1)
    old = _fake_backup(db, d, now - timedelta(days=90), 1)
    for i in range(10):   # ten newer backups, so `old` is not among the ten newest
        _fake_backup(db, d, now - timedelta(days=80, hours=i), 1)
    deleted, _ = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12, apply=False, protect=(old,))
    assert old not in deleted
    deleted, _ = backup_mod.prune(d, repo=tmp_path, now=now, sprint=12, apply=False)
    assert old in deleted
