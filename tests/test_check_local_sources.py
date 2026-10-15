"""F48 (Sprint 9 Task D): local source paths stay honest. A moved file is
reported, a changed hash is never overwritten, and every local file in the
store carries a SHA-256."""
from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("cls", ROOT / "scripts" / "check_local_sources.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _store(rows) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("CREATE TABLE paper_fields (record_id TEXT PRIMARY KEY, access TEXT, evidence TEXT);"
                       "CREATE TABLE records (id TEXT PRIMARY KEY, updated TEXT, updated_reason TEXT);")
    conn.executemany("INSERT INTO paper_fields VALUES (?, ?, ?)", rows)
    conn.executemany("INSERT INTO records VALUES (?, '2026-10-01', 'added')", [(r[0],) for r in rows])
    return conn


def test_a_moved_file_is_reported(tmp_path):
    """The card's acceptance test. Proven to fail by injection, 2026-10-15:
    with "local copy missing" removed from PROBLEMS, the moved file was not
    reported and the check exited 0."""
    cls = _script()
    f = tmp_path / "paper.pdf"
    f.write_bytes(b"%PDF-1.4 x")
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    conn = _store([("p", str(f), f"Local copy SHA-256 {digest}")])
    assert [r[2] for r in cls.statuses(conn)] == ["local copy present (SHA-256 unchanged)"]
    f.rename(tmp_path / "moved.pdf")
    [(rid, _, status, _)] = cls.statuses(conn)
    assert (rid, status) == ("p", "local copy missing") and status in cls.PROBLEMS


def test_a_changed_hash_is_reported_and_never_overwritten(tmp_path, monkeypatch):
    """Proven to fail by injection, 2026-10-15: with record_hashes taking
    every present file instead of only the unhashed ones, the changed
    file's recorded hash was replaced."""
    cls = _script()
    monkeypatch.setattr(cls, "append_updated_reason", lambda *a, **k: None)
    changed, fresh = tmp_path / "a.pdf", tmp_path / "b.pdf"
    changed.write_bytes(b"new bytes")
    fresh.write_bytes(b"never hashed")
    old = "Local copy SHA-256 " + "0" * 64
    conn = _store([("a", str(changed), old), ("b", str(fresh), None)])
    rows = cls.statuses(conn)
    assert {r[0]: r[2] for r in rows}["a"] == "local copy changed (SHA-256 differs)"
    assert cls.record_hashes(conn, rows, "2026-10-15") == ["hashed b"]
    assert conn.execute("SELECT evidence FROM paper_fields WHERE record_id = 'a'").fetchone()[0] == old
    assert hashlib.sha256(b"never hashed").hexdigest() in conn.execute(
        "SELECT evidence FROM paper_fields WHERE record_id = 'b'").fetchone()[0]


@pytest.mark.live_store
def test_every_local_file_in_the_store_carries_a_sha256(live_conn):
    """F48's acceptance: SHA-256 recorded for every local-access source (a
    folder excepted). A new local record entered without one fails here.
    Missing or changed files are reported by the script on the re-check's
    schedule, not here: a file another repository edits would otherwise
    turn the suite red for a change made outside it."""
    cls = _script()
    unhashed = [r[0] for r in cls.statuses(live_conn) if r[2] == cls.NO_HASH]
    assert not unhashed, f"local files with no SHA-256: {unhashed}"
