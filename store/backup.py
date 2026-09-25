"""Verified backups of the store, taken before every write (Sprint 5 Task A, F30 part 2).

Premise check 2026-09-23: there was NO backup of store/evidence.db
anywhere. The committed export made the data recoverable in principle;
store/rebuild.py makes it recoverable in fact. Backups cover the gap
between a write and the commit of its export -- until that commit, the
backup is the only other copy.

Mechanism (team lead, 2026-09-23: "if it is [sqlite], then backups and
restores are part of the sqlite package"): `sqlite3.Connection.backup()`,
never a file copy. The API is safe against a concurrent writer; a copy of
a live file can capture a torn write. The result is NOT byte-identical to
the source (the API writes a freshly packed file), so a backup is
verified by CONTENT: integrity_check, then per-class record counts equal
to the source's. A backup that fails verification raises and the caller's
write does not happen -- an unverified backup is the guard-never-run class.

On write, not on a clock: at about 15 ms there is nothing to schedule.
Every write-shaped script calls `backup_before_write()` inside `--apply`,
before it opens its transaction.

Retention (team lead's decision 2026-09-23, option 2a). A backup is
deleted only when ALL THREE rules allow it:
  1. it is older than RETENTION_DAYS (32);
  2. it is not the newest backup of one of the last KEEP_SPRINTS (5)
     sprints -- the state at each recent sprint boundary;
  3. its content IS in a committed export (every file of the export
     regenerated from it exists as a blob somewhere in git history under
     export/), OR an export commit landed after it was taken, so its state
     was superseded and committed onward (see prune()). Until one of those
     holds the backup may be the only copy.
Any doubt (git unavailable, the backup unreadable) keeps the backup.
"""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

RETENTION_DAYS = 32
KEEP_SPRINTS = 5
_NAME = re.compile(r"^evidence-(\d{8}T\d{6}\d{6})-sprint(\d+)-([a-z0-9-]+)\.db$")
_STAMP = "%Y%m%dT%H%M%S%f"


class BackupVerificationError(RuntimeError):
    """A backup was taken but does not check out; the write must not proceed."""


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_backups_dir(db_path: str | Path) -> Path:
    """Backups live beside the database they protect: store/backups/ for the
    real store (gitignored), <tmp>/backups/ for a test's temporary store, so
    a test never writes into the repository."""
    return Path(db_path).resolve().parent / "backups"


def current_sprint(root: Path | None = None) -> int:
    status = (root or _root()) / ".claude" / "sprint_status.json"
    return int(json.loads(status.read_text(encoding="utf-8"))["current_sprint"]["number"])


def _class_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {row[0]: row[1] for row in conn.execute("SELECT class, COUNT(*) FROM records GROUP BY class")}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "write"


def backup_store(db_path: str | Path, backups_dir: str | Path, reason: str, sprint: int,
                 now: datetime | None = None) -> Path:
    """Back up db_path with SQLite's backup API, verify it, return its path."""
    db_path, backups_dir = Path(db_path), Path(backups_dir)
    if not db_path.exists():
        raise FileNotFoundError(f"{db_path} does not exist; nothing to back up")
    backups_dir.mkdir(parents=True, exist_ok=True)
    now = now or datetime.now()
    target = backups_dir / f"evidence-{now.strftime(_STAMP)}-sprint{sprint}-{_slug(reason)}.db"
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
        expected = _class_counts(src)
    finally:
        dst.close()
        src.close()
    verify_backup(target, expected)
    return target


def verify_backup(path: str | Path, expected_counts: dict[str, int]) -> None:
    conn = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        counts = _class_counts(conn)
    except sqlite3.DatabaseError as ex:
        raise BackupVerificationError(f"backup {path} cannot be read: {ex}") from ex
    finally:
        conn.close()
    if result != "ok":
        raise BackupVerificationError(f"backup {path}: integrity_check returned {result!r}")
    if counts != expected_counts:
        raise BackupVerificationError(f"backup {path}: record counts {counts} differ from the source's {expected_counts}")


def parse_name(path: Path) -> tuple[datetime, int] | None:
    m = _NAME.match(path.name)
    if not m:
        return None
    return datetime.strptime(m.group(1), _STAMP), int(m.group(2))


def committed_export_blobs(repo: Path) -> set[str] | None:
    """Every blob id that has ever been committed under export/, or None if
    git cannot answer (then nothing counts as committed, and nothing is
    deleted under rule 3)."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-list", "--all", "--objects", "--", "export"],
                             capture_output=True, text=True, check=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return {line.split()[0] for line in out.splitlines() if line.startswith(tuple("0123456789abcdef"))}


def _git_blob_id(repo: Path, name: str, data: bytes) -> str | None:
    """The blob id git WOULD store for these bytes at export/<name>.

    Not a raw SHA-1 of the bytes: with core.autocrlf=true the working copy
    is CRLF while the committed blob is LF-normalized (checked 2026-09-24:
    export/papers.json hashes to 0a74... raw and 79f7... committed). Asking
    git to hash with --path applies the same filters a commit would."""
    try:
        return subprocess.run(["git", "-C", str(repo), "hash-object", "--path", f"export/{name}", "--stdin"],
                              input=data, capture_output=True, check=True, timeout=30).stdout.decode().strip()
    except (OSError, subprocess.SubprocessError):
        return None


def content_is_committed(backup: Path, blobs: set[str] | None, repo: Path | None = None) -> bool:
    if not blobs:
        return False
    repo = repo or _root()
    from store import connect
    from store.export import regenerate
    from store.rebuild import EXPORT_FILES
    try:
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(backup)
            try:
                regenerate(conn, tmp)
            finally:
                conn.close()
            return all(_git_blob_id(repo, name, (Path(tmp) / name).read_bytes()) in blobs for name in EXPORT_FILES)
    except (sqlite3.DatabaseError, OSError):
        return False


def last_export_commit(repo: Path) -> datetime | None:
    """When the newest commit touching export/ was made, or None."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%ct", "--", "export"],
                             capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return datetime.fromtimestamp(int(out)) if out else None


def prune(backups_dir: str | Path, repo: Path | None = None, now: datetime | None = None,
          sprint: int | None = None, apply: bool = True,
          protect: tuple[Path, ...] = ()) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Apply the three retention rules. Returns (deleted, kept_with_reason).

    Rule 3 is met when the backup's own content is in a committed export OR
    an export commit landed AFTER the backup was taken. The second clause
    was added 2026-09-24 after a fresh-eyes review found that a backup of
    an intermediate state (two --apply runs committed together) can never
    match any committed export, so rule 3 as first written kept it forever;
    the same happened to every old backup after any change to the export
    format. A later committed export means the backup's state was
    superseded and committed onward, not that it is the only copy.
    Accepted by the team lead at Sprint 5 Manual Validation (Q2 = 1,
    2026-09-25).

    `protect` names backups that must survive this call whatever their age
    (restore_store.py protects the backup it is about to restore)."""
    backups_dir = Path(backups_dir)
    protect = tuple(Path(p).resolve() for p in protect)
    repo = repo or _root()
    now = now or datetime.now()
    sprint = current_sprint(repo) if sprint is None else sprint
    parsed = sorted((p for p in backups_dir.glob("evidence-*.db") if parse_name(p)), key=lambda p: parse_name(p)[0])
    newest_per_sprint: dict[int, Path] = {}
    for p in parsed:
        newest_per_sprint[parse_name(p)[1]] = p
    protected = {p for s, p in newest_per_sprint.items() if s > sprint - KEEP_SPRINTS}
    blobs = None
    deleted, kept = [], []
    last_commit = None
    for p in parsed:
        stamp, _ = parse_name(p)
        if p.resolve() in protect:
            kept.append((p, "protected by the caller"))
            continue
        if now - stamp <= timedelta(days=RETENTION_DAYS):
            kept.append((p, f"within {RETENTION_DAYS} days"))
            continue
        if p in protected:
            kept.append((p, f"newest backup of one of the last {KEEP_SPRINTS} sprints"))
            continue
        if blobs is None:
            blobs = committed_export_blobs(repo) or set()  # None -> empty -> keep everything
            last_commit = last_export_commit(repo) if blobs else None
        superseded = last_commit is not None and last_commit > stamp
        if not superseded and not content_is_committed(p, blobs, repo):
            kept.append((p, "content not yet in a committed export"))
            continue
        if apply:
            try:
                p.unlink()
            except OSError as ex:  # a locked file must not abort the caller's write
                kept.append((p, f"could not delete: {ex}"))
                continue
        deleted.append(p)
    return deleted, kept


def backup_before_write(db_path: str | Path, reason: str, backups_dir: str | Path | None = None,
                        protect: tuple[Path, ...] = ()) -> Path:
    """The one call every write-shaped script makes inside --apply, before
    its transaction. Takes a verified backup (raising if it does not check
    out), then prunes by the retention rules, never touching `protect`.
    Returns the backup's path."""
    backups_dir = Path(backups_dir) if backups_dir is not None else default_backups_dir(db_path)
    path = backup_store(db_path, backups_dir, reason, current_sprint())
    prune(backups_dir, protect=protect)
    print(f"BACKUP {path} (verified: integrity ok, record counts match)")
    return path
