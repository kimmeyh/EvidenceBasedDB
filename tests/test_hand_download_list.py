"""The hand-download list (intake sections 39 and 40): computed from the
store, in priority order. A record leaves it when its newest list segment
takes it off, when it is read, or when its access names a local copy.
Groups come first (named for a question, fraud, QML or QC, other), then
citation count; each entry names its target file and why it matters."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script(name="hand_download_list.py"):
    spec = importlib.util.spec_from_file_location(name[:-3], ROOT / "scripts" / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ON = "2026-10-18 (Sprint 10 Task I, F89): selected for reading and NOT read: Springer, closed; on the hand-download list"


def _conn(rows):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, value TEXT, provenance TEXT, updated_reason TEXT)")
    conn.execute("CREATE TABLE paper_fields (record_id TEXT, tier TEXT, access TEXT, disposition TEXT)")
    conn.execute("CREATE TABLE record_contexts (record_id TEXT, context_id TEXT)")
    for rid, reason, tier, access, contexts, disposition in rows:
        conn.execute("INSERT INTO records VALUES (?, ?, ?, ?)", (rid, f"Title {rid}", f"Smith, J., \"T\", 2020-05",
                                                                  reason))
        conn.execute("INSERT INTO paper_fields VALUES (?, ?, ?, ?)", (rid, tier, access, disposition))
        conn.executemany("INSERT INTO record_contexts VALUES (?, ?)", [(rid, c) for c in contexts])
    return conn


def test_who_is_on_the_list_and_in_what_order():
    """Proven to fail by injection, 2026-10-22: with the `tier == "read"`
    exclusion removed from ranked(), the read record appeared and this test
    went red; and with group() returning 3 for every record, the fraud
    record fell below the qml ones and it went red again."""
    hdl = _script()
    q3 = "2026-10-22 (Sprint 11 Manual Validation, Q3 = 1): F62 discovery found no free copy; on the hand-download list"
    conn = _conn([
        ("low", ON, "seen", "DOI:10.1/a", ["qml"], ""),
        ("high", ON, "seen", "DOI:10.1/b", ["qml"], ""),
        ("named", "2026-10-15 (Sprint 9 Task E, F78): On the team lead's hand-download list", "seen", "DOI:10.1/c",
         ["world"], ""),
        ("fraud", q3, "seen", "DOI:10.1/h", ["ml"], "from F62 discovery, fraud stream rank 9 (3 citations, 2018)"),
        ("other", q3, "seen", "DOI:10.1/i", ["ml"], "from F62 discovery, ml stream rank 2 (9000 citations, 2015)"),
        ("retracted", "x | 2026-10-22: NOT read and NOT for the hand-download list: RETRACTED", "seen", "DOI:10.1/d",
         ["qml"], ""),
        ("was-read", ON, "read", "DOI:10.1/e", ["qml"], ""),
        ("has-copy", ON, "seen", r"DOI:10.1/f | D:\Data\Harold\EvidenceBasedDB\Papers\f.pdf", ["qml"], ""),
        ("never", "added by intake", "seen", "DOI:10.1/g", ["qml"], ""),
    ])
    items = hdl.ranked(conn, {"low": 5, "high": 50})
    assert [i["id"] for i in items] == ["named", "fraud", "high", "low", "other"]
    fraud = items[1]
    assert fraud["cited_by_count"] == 3, "the count comes from F62's disposition when no slice recorded one"
    assert "fraud stream, rank 9" in fraud["selected_by"]


def test_a_newer_segment_takes_a_record_off():
    hdl = _script()
    assert hdl.on_list("a; on the hand-download list | b; NOT for the hand-download list") is None
    assert hdl.on_list("added by intake") is None
    assert hdl.on_list("x | y; on the hand-download list").endswith("on the hand-download list")


def test_a_slice_with_no_counts_is_read_past(tmp_path):
    """Task G's slice (F113, Sprint 13) has no cited_by_count field and
    matches the "*_slice.json" glob. Proven to fail, 2026-10-25: before the
    fix, this test raised KeyError: 'cited_by_count'."""
    hdl = _script()
    (tmp_path / "a_slice.json").write_text(json.dumps({"slice": [{"record_id": "x", "cited_by_count": 7}]}),
                                           encoding="utf-8")
    (tmp_path / "b_slice.json").write_text(json.dumps({"slice": [{"record_id": "x"}, {"record_id": "y"}]}),
                                           encoding="utf-8")
    assert hdl.slice_counts(tmp_path) == {"x": 7}


def test_target_names_follow_the_papers_convention():
    """Intake section 3, as F62 builds it; a book goes to Books."""
    hdl = _script()
    assert hdl.target("A quantum deep convolutional neural network for image recognition",
                      "Li, Y., Zhou, R.G., \"A quantum...\", DOI:10.1088/x, 2020-10-01", ON) == \
        r"Papers\2020-10_Li_A-quantum-deep-convolutional-neural-network-for-image.pdf"
    assert hdl.target("Classical and superposed learning", "da Silva, A.J., \"C\", DOI:10.1/x, 2012-01", ON) == \
        r"Papers\2012-01_da-Silva_Classical-and-superposed-learning.pdf"
    book = "2026-10-18 (F89): selected for reading and NOT read: a Springer book; no free copy; on the hand-download list"
    assert hdl.target("Supervised Learning with Quantum Computers", "Schuld, M., \"S\", DOI:10.1007/978, 2018", book) \
        == r"Books\Book - Supervised Learning with Quantum Computers - Springer 2018.pdf"


def test_the_skill_runs_the_script():
    """The skill only wraps the script; a renamed script would leave it
    pointing at nothing. Proven to fail by injection, 2026-10-22: with the
    skill naming scripts/hand_download.py, this test went red."""
    skill = (ROOT / ".claude" / "skills" / "hand-download-list" / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: hand-download-list\n")
    assert "python scripts/hand_download_list.py" in skill
    assert (ROOT / "scripts" / "hand_download_list.py").exists()


@pytest.mark.live_store
def test_the_live_list(live_conn):
    """Snapshot 2026-10-22: 38 records, Te Sun 1994 first (named for the
    F78 ceiling question), then the fraud group; Chen 2025 (read) and the
    two retracted items off. The count is not asserted: the list shrinks
    as files arrive."""
    hdl = _script()
    items = hdl.ranked(live_conn, hdl.slice_counts(ROOT / "manifests"))
    ids = [item["id"] for item in items]
    assert ids[0] == "te-sun-1994-generalizing-fano-inequality"
    for gone in ("chen-2025-efficient-bayes-error-rate-estimation", "mezquita-2021-retracted-chapter-review-k-nn",
                 "valdez-2023-retracted-article-review-quantum-computing"):
        assert gone not in ids
    groups = [item["group"] for item in items]
    assert groups == sorted(groups)
    for g in set(groups) - {0}:
        # Sprint 13's slice records 389 uncounted records (intake section 51); they come after every counted one.
        counts = [i["cited_by_count"] for i in items if i["group"] == g]
        counted = [n for n in counts if n is not None]
        assert counts == counted + [None] * (len(counts) - len(counted)), g
        assert counted == sorted(counted, reverse=True)
    assert all(i["target"].startswith(("Papers\\", "Books\\")) and i["target"].endswith(".pdf") for i in items)


@pytest.mark.live_store
def test_q3_second_apply_writes_nothing(live_copy):
    """Section 40: the F62 marks are in the store, so a second apply lists
    nothing new."""
    from store import connect
    q3 = _script("sprint11_q3_f62_hand_download.py")
    conn = connect(live_copy)
    try:
        log = q3.apply_changes(conn, apply=True)
    finally:
        conn.close()
    assert not [x for x in log if x.startswith("listed")]
    assert sum(x.startswith("exists") for x in log) == 23
