"""`updated_reason` is APPEND-ONLY. A correction pass may add to a record's
account of itself; it may never replace it.

THE DEFECT. PR #30 review finding 1 (2026-09-22): three Sprint 4 scripts
carried an inverted ternary that appended only when the row had been touched
the SAME DAY and replaced the text otherwise -- so the normal case, a row
carrying history from an earlier date, was destruction. It ran: prior
`updated_reason` survived on 0 of 44 paper records, and 43 lost "Sprint 1
Task F: 46-paper seed set loaded at seen tier". Recovered by
`scripts/recover_updated_reason_history.py`.

WHY THIS FILE LOOKS THE WAY IT DOES, WHICH IS THE SECOND LESSON. The first
version of this guard SCANNED THE SCRIPTS' SOURCE for the bad phrasing: a
regex for `existing.startswith(TODAY)`, and a check that each `joined =`
line mentioned `{existing}`. The round-2 audit (2026-09-23) defeated it with
three rewrites that destroy history while keeping the shape, each leaving
all 433 tests green:

  A. compact the history first --
     `existing = " | ".join(p for p in existing.split(" | ") if p.startswith(TODAY))`
  B. never read the prior text at all -- `existing = ""`
  C. the same date gate, spelled `existing[:10] == TODAY` instead of
     `.startswith`

All three were reproduced against the real scripts before this file was
rewritten. A guard that pins a PHRASING pins nothing; the repository's own
standard is that a test executes the thing it guards.

So: there is now ONE implementation, `store.ingest.append_updated_reason`,
every script calls it, and the tests below RUN it against a real sqlite row.
Injections A, B and C are impossible to express in the delegating scripts,
and would be caught here if written into the shared function.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from store import create_store  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402



SEED_NOTE = "Sprint 1 Task F: 46-paper seed set loaded at seen tier"
LATER_NOTE = "2026-09-19 (Sprint 4 Task C): citation re-derived from the API"

# Every script that writes an updated_reason. Each must DELEGATE rather than
# spell the join itself: one behavior, one place to test it.
DELEGATING_SCRIPTS = [
    ROOT / "scripts" / "sprint4_task_c_corrections.py",
    ROOT / "scripts" / "sprint4_task_f_refiling.py",
    ROOT / "scripts" / "sprint4_task_h_extraction.py",
]


@pytest.fixture
def db(tmp_path):
    conn = create_store(tmp_path / "t.db")
    conn.execute(
        "INSERT INTO records (id, class, value, provenance, evidence_tag, updated, updated_reason) "
        "VALUES ('p1', 'paper', 'A paper', 'A citation', 'N/A', '2026-09-16', ?)", (SEED_NOTE,))
    conn.commit()
    yield conn
    conn.close()


def reason(conn, pid="p1") -> str:
    return conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()[0]


# --- the behavioral core: run the function, read the row --------------------

def test_the_prior_account_survives_an_append(db):
    """The exact shape of the 43-record loss: a row whose history is OLDER
    than today gets a new note, and the old text must still be there."""
    append_updated_reason(db, "p1", LATER_NOTE, "2026-09-19")
    got = reason(db)
    assert SEED_NOTE in got, "the prior account of the record was destroyed"
    assert LATER_NOTE in got
    assert got.startswith(SEED_NOTE), "history reads oldest-first"


def test_appending_twice_keeps_both_and_the_original(db):
    append_updated_reason(db, "p1", LATER_NOTE, "2026-09-19")
    append_updated_reason(db, "p1", "2026-09-22: a third pass", "2026-09-22")
    got = reason(db)
    for part in (SEED_NOTE, LATER_NOTE, "a third pass"):
        assert part in got
    assert got.index(SEED_NOTE) < got.index(LATER_NOTE) < got.index("a third pass")


def test_a_same_day_note_appends_rather_than_replacing(db):
    """The original bug kept text ONLY on the same day. Same-day appends must
    work too, but they are not the interesting case -- this pins that the
    date plays no part in the decision at all."""
    append_updated_reason(db, "p1", "2026-09-16: an earlier pass", "2026-09-16")
    append_updated_reason(db, "p1", "2026-09-16: a later pass", "2026-09-16")
    got = reason(db)
    assert SEED_NOTE in got and "an earlier pass" in got and "a later pass" in got


def test_an_empty_prior_reason_is_not_prefixed_with_a_separator(db):
    db.execute("UPDATE records SET updated_reason = '' WHERE id = 'p1'")
    append_updated_reason(db, "p1", LATER_NOTE, "2026-09-19")
    assert reason(db) == LATER_NOTE


def test_the_date_is_written_alongside(db):
    append_updated_reason(db, "p1", LATER_NOTE, "2026-09-19")
    assert db.execute("SELECT updated FROM records WHERE id = 'p1'").fetchone()[0] == "2026-09-19"


def test_a_missing_record_is_an_error_not_a_silent_no_op(db):
    with pytest.raises(ValueError, match="does not exist"):
        append_updated_reason(db, "nobody", LATER_NOTE, "2026-09-19")


@pytest.mark.parametrize("prior", [
    SEED_NOTE,
    "a | b | c",
    "2026-09-19: touched today already",
    "text with 'quotes' and | pipes",
])
def test_no_prior_text_is_ever_lost_whatever_its_shape(db, prior):
    db.execute("UPDATE records SET updated_reason = ? WHERE id = 'p1'", (prior,))
    append_updated_reason(db, "p1", LATER_NOTE, "2026-09-19")
    assert prior in reason(db)


# --- the scripts must DELEGATE, so there is only one behavior to test -------

@pytest.mark.parametrize("script", DELEGATING_SCRIPTS, ids=lambda p: p.name)
def test_no_script_spells_the_join_itself(script):
    """A script that re-implements the join is a second behavior this file
    does not execute, which is exactly how the first version of this guard
    was defeated. They must all call append_updated_reason."""
    source = script.read_text(encoding="utf-8")
    assert "append_updated_reason" in source, (
        f"{script.name} does not use the shared append-only helper")
    offenders = [line.strip() for line in source.splitlines()
                 if "updated_reason = ?" in line and "append_updated_reason" not in line
                 and "SELECT" not in line]
    assert not offenders, (
        f"{script.name} writes updated_reason directly: {offenders}. Call "
        "store.ingest.append_updated_reason so there is one behavior and one test.")


# --- the shipped artifact ---------------------------------------------------

@pytest.mark.live_store
def test_the_committed_export_still_carries_the_sprint_1_provenance(live_export):
    """The data check. 43 papers arrived in the Sprint 1 seed load and one in
    the Task E premise-falsifier run; the export must still say so.

    Pinned as an ID SET rather than a count (round-2 audit): a count with no
    slack turns red on any legitimate deletion and invites someone to lower
    the number, which would hide a real erasure. Reads the live store
    (ADR-0004 A7: no committed export)."""
    papers = json.loads((live_export / "papers.json").read_text(encoding="utf-8"))
    by_id = {p["id"]: (p.get("updated_reason") or "") for p in papers}
    seeded = {pid for pid, r in by_id.items() if "Sprint 1 Task F" in r}
    assert len(seeded) >= 43, (
        f"only {len(seeded)} papers still record the Sprint 1 seed load; a correction "
        "pass has erased history again. Recover with "
        "scripts/recover_updated_reason_history.py")
    assert "Sprint 1 Task E" in by_id["lenat-marcus-2023-trustworthy-ai"], (
        "the premise-falsifier record lost its own origin note")


# Two fixed anchors, both with export/ in their tree (history kept, Q3 = 1):
# - BASELINE_COMMIT (0044a44, Sprint 6 plan approval, 2026-10-03): from
#   before later correction passes, so the current reasons DIFFER from it and
#   the vacuity check below has something to see.
# - LAST_EXPORT_COMMIT (3bf2eda, 2026-10-06): the parent of the commit that
#   removed export/ under ADR-0004 A7. Every record Sprint 6 added or changed
#   is checked against it (Task B review, 2026-10-06: with the first anchor
#   alone, those records were outside the check).
BASELINE_COMMIT = "0044a44"
LAST_EXPORT_COMMIT = "3bf2eda"
_RENAMES = {
    "rand-2023-pqc-critical-infrastructure-assessment": "rand-2022-pqc-critical-infrastructure-assessment",
    "rand-2023-pqc-critical-infrastructure-assessment-appendix-b": "rand-2022-pqc-critical-infrastructure-assessment-appendix-b",
}


def _reasons_at(commit: str) -> dict[str, str]:
    ref = f"{commit}:export/papers.json"
    raw = subprocess.run(["git", "show", ref], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8")
    assert raw.returncode == 0, f"the baseline {ref} must be readable from git history"
    return {_RENAMES.get(p["id"], p["id"]): (p.get("updated_reason") or "").strip()
            for p in json.loads(raw.stdout)}


@pytest.mark.live_store
@pytest.mark.parametrize("commit", [BASELINE_COMMIT, LAST_EXPORT_COMMIT])
def test_no_paper_lost_the_updated_reason_it_had_before_the_corrections(live_export, commit):
    """Whatever a record said at each anchor, it must still say.

    Anchored to FIXED commits. The first version read
    `develop:export/papers.json`, which went vacuous the moment a PR merged
    (round-2 audit, 2026-09-23); the second read the merge-base with
    develop, which would have skipped silently once ADR-0004 A7 removed the
    export from develop (Sprint 7 Task B, 2026-10-06). Fixed commits with
    the export in them keep a real baseline, and the live store is compared
    against each.
    """
    current = {p["id"]: (p.get("updated_reason") or "")
               for p in json.loads((live_export / "papers.json").read_text(encoding="utf-8"))}
    baseline = _reasons_at(commit)

    comparable = {pid: was for pid, was in baseline.items() if was and pid in current}
    assert comparable, "no comparable records: this guard would assert nothing"
    if commit == BASELINE_COMMIT:
        # The guard must not be vacuous: the older anchor has to differ from
        # what we compare it against, or "nothing lost" means "nothing
        # checked". The newest anchor may legitimately equal the store.
        assert any(was != current[pid] for pid, was in comparable.items()), (
            "every baseline reason is identical to the current one, so this guard is "
            "vacuous -- it is comparing the export against itself. Anchor it to a "
            "commit from before the correction passes.")

    lost = [pid for pid, was in comparable.items() if was not in current[pid]]
    assert not lost, (
        f"{len(lost)} record(s) lost the updated_reason they carried at {commit}: "
        f"{lost[:5]}. updated_reason is append-only.")
