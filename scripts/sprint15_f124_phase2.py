#!/usr/bin/env python3
"""Sprint 15 Task K (F124): Phase 2's F151, F153 and F154 source records repointed at develop af03165.

The three records point at Phase 2 commit 10086da; Phase 2 changed each document after it (by 28bdbcd, the PR 46
review), so the local-file check read all three as changed. Each document is re-read whole at af03165, Phase 2's
develop head on 2026-11-01 (read through `git show` on the team lead's clone, which holds the commit; no fetch). Read
only (F79). INTAKE_WORKFLOW.md section 62.

What changed in each document between 10086da and af03165, and what it does to the stored values:
- F151: the l2_regularization=0.1 row now fails on level as well as SD; a note that the range threshold cannot
  decide at five seeds; the list of tasks that use the setting. Neither stored value (the default's instability and
  the proxies against the stable HGB) states any of these: both confirmed by name.
- F153: "close to 1" became "between 0.8 and 1 (0.80-0.92 at weight 2)", and the data term "is at most 0.33%" of
  it. Neither stored value states the magnitude: both confirmed by name.
- F154: the CVQBoost proxy against logistic regression names its `deep` configuration; 16 exempt runs remain after
  the DV4 backfill. The stored value states neither: confirmed by name.

Every stored quote of the three records is checked verbatim, with its value, against its document at af03165 before
anything is written. DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_read, append_updated_reason  # noqa: E402
from store.quotes import plain, require_verbatim  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, _ = script_paths(__file__)
TODAY = "2026-11-01"
TAG = "Sprint 15 Task K, F124"
PHASE2 = r"D:\Data\Harold\github\hsbc-qfraud-phase2"
REPO_URL = "https://github.com/kimmeyh/hsbc-qfraud-phase2"
COMMIT = "af03165b208b2dc80b1e7494e26bc4edf88ed0c2"
LAST = "28bdbcd"  # the last commit to touch each of the three documents at COMMIT
# key -> (record, file, SHA-256 of the blob at COMMIT, run, first read on, blob SHA-256 at 10086da, what changed)
DOCS = {
    "f151": ("hsbc-qfraud-phase2-f151-sprint28-result", "docs/phase2/F151_HGB_COMPARATOR.md",
             "32790782a7f06a1d8a463c4fa827a05b9c0275c81ea0582b6c45f9673c3800f9",
             "experiments/phase2/results/f151_hgb_cause.json, seeds 42-46", "2026-10-22",
             "caa8d3a641e1a43e878d1ecf571da45c38585d484a40c2d0ca20b431848afea3",
             "Phase 2's PR 46 review added the 0.1 row's level shortfall, a note that the range threshold cannot "
             "decide at five seeds, and the tasks that use the setting; both stored values confirmed by name"),
    "f153": ("hsbc-qfraud-phase2-f153-sprint28-result", "docs/phase2/F153_EXP3_DESIGN.md",
             "3baa40cee8f2c6eaf8a3af7b2f89324c34428916b13497f7c46d59f5c75a6b49",
             "experiments/phase2/results/f153_exp3_design.json, six instances", "2026-10-22",
             "e4d924f8a2feff9d2cd6e1c904f2b749a456d5f07de0cbfc56f0ba16f90c7598",
             "Phase 2's PR 46 review stated the ridge term's size (between 0.8 and 1) and the data term's share (at "
             "most 0.33%); both stored values confirmed by name"),
    "f154": ("hsbc-qfraud-phase2-f154-sprint28-result", "docs/phase2/F154_WHERE_MODELS_WIN.md",
             "ed08c5580efc92370c6c8dc55c61bd888cc7740f127acca306b806e1d045444a",
             "experiments/phase2/results/f154_confusion.json, ten seeds 42-51", "2026-10-22",
             "07f39e2bf43098fd7e843d708ec75cdad76014b9fcef773cb9325bb3346b3ed6",
             "Phase 2's PR 46 review named the proxy's deep configuration and the 16 runs still exempt; the stored "
             "value confirmed by name"),
}
READ_DETAIL = "the whole document at commit af03165, to compare the stored values with Phase 2's later edits (F124)"
REPOINT_NOTE = (f"{TODAY} ({TAG}): access, evidence and checked_against_source repointed at Phase 2 commit af03165 "
                "(develop), where the document was re-read whole (INTAKE_WORKFLOW.md section 62)")


def blob(path: str) -> bytes:
    """A file exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{path}"], capture_output=True, check=True).stdout


def repointed(key: str) -> dict[str, str]:
    _, file, sha, run, first_on, old_sha, why = DOCS[key]
    return {
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 {sha} at Phase 2 commit af03165 (the last commit to touch the file is "
                     f"{LAST}). Run: {run}. Read first on {first_on} at commit 10086da (blob SHA-256 {old_sha}); "
                     f"re-read whole on {TODAY} at af03165: {why}. The private repository's URL is the citation's "
                     "pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "checked_against_source": f"{TODAY}, Claude, read the whole document at commit af03165 via git show",
    }


def check_hashes() -> list[str]:
    return [f"{k}: blob at af03165 has changed" for k, (_, file, sha, *_) in DOCS.items()
            if hashlib.sha256(blob(file)).hexdigest() != sha]


def stored(conn, rid: str) -> list[tuple[str, str, str]]:
    return conn.execute("SELECT r.id, r.value, f.citation_context FROM paper_yields y JOIN records r ON "
                        "r.id = y.assertion_id JOIN assertion_fields f ON f.record_id = r.id WHERE y.paper_id = ? "
                        "ORDER BY r.id", (rid,)).fetchall()


def verify_all(conn) -> list[str]:
    """Every stored quote of the three records verbatim in its document at COMMIT, with its value. Raises on the
    first that is not, before anything is written."""
    out = []
    for key, (rid, file, *_) in DOCS.items():
        text = plain(blob(file).decode("utf-8").replace("**", ""))
        rows = stored(conn, rid)
        if not rows:
            raise ValueError(f"{rid}: no stored assertion")
        for aid, value, cc in rows:
            require_verbatim(aid, cc, text, value=value)
            out.append(f"confirm {aid} ({key}, verbatim at af03165)")
    return out


def apply_changes(conn) -> list[str]:
    log = []
    for key, (rid, *_) in DOCS.items():
        if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND read_on = ? AND detail = ?",
                            (rid, TODAY, READ_DETAIL)).fetchone():
            add_read(conn, rid, "Claude", TODAY, "full", READ_DETAIL)
            log.append(f"read   {rid}")
        want = repointed(key)
        row = conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                           (rid,)).fetchone()
        if tuple(row) != (want["access"], want["evidence"], want["checked_against_source"]):
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ?, checked_against_source = ? "
                         "WHERE record_id = ?", (want["access"], want["evidence"], want["checked_against_source"], rid))
            append_updated_reason(conn, rid, REPOINT_NOTE, TODAY)
            log.append(f"repoint {rid}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_hashes()
    if bad:
        print("\n".join(bad))
        return 1
    conn = connect(DB_PATH)
    try:
        print("\n".join(verify_all(conn)))
        if "--apply" not in args:
            print("DRY RUN: nothing written. Re-run with --apply.")
            return 0
    finally:
        conn.close()
    backup_before_write(DB_PATH, "F124 Phase 2 F151, F153, F154 repoint")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log) or "nothing to write")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
