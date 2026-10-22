"""The hand-download list (intake section 39): computed from the store, in
priority order. A record leaves it when its newest list segment takes it
off, when it is read, or when its access names a local copy; records named
for a question come before the ranked ones, which go by citation count."""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("hdl", ROOT / "scripts" / "hand_download_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _conn(rows):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE records (id TEXT, provenance TEXT, updated_reason TEXT)")
    conn.execute("CREATE TABLE paper_fields (record_id TEXT, tier TEXT, access TEXT)")
    for rid, reason, tier, access in rows:
        conn.execute("INSERT INTO records VALUES (?, ?, ?)", (rid, f"cite {rid}", reason))
        conn.execute("INSERT INTO paper_fields VALUES (?, ?, ?)", (rid, tier, access))
    return conn


def test_who_is_on_the_list_and_in_what_order():
    """Proven to fail by injection, 2026-10-22: with the `tier == "read"`
    exclusion removed from ranked(), the read record appeared and this test
    went red."""
    hdl = _script()
    on = "2026-10-18 (F89): selected and NOT read: closed; on the hand-download list"
    conn = _conn([
        ("low", on, "seen", "DOI:10.1/a"),
        ("high", on, "seen", "DOI:10.1/b"),
        ("named", "2026-10-15 (F78): On the team lead's hand-download list", "seen", "DOI:10.1/c"),
        ("retracted", "x | 2026-10-22: NOT read and NOT for the hand-download list: RETRACTED", "seen", "DOI:10.1/d"),
        ("was-read", on, "read", "DOI:10.1/e"),
        ("has-copy", on, "seen", r"DOI:10.1/f | D:\Data\Harold\EvidenceBasedDB\Papers\f.pdf"),
        ("never", "added by intake", "seen", "DOI:10.1/g"),
    ])
    ids = [item["id"] for item in hdl.ranked(conn, {"low": 5, "high": 50})]
    assert ids == ["named", "high", "low"]


def test_a_newer_segment_takes_a_record_off():
    hdl = _script()
    assert hdl.on_list("a; on the hand-download list | b; NOT for the hand-download list") is None
    assert hdl.on_list("added by intake") is None
    assert hdl.on_list("x | y; on the hand-download list").endswith("on the hand-download list")


@pytest.mark.live_store
def test_the_live_list(live_conn):
    """Snapshot 2026-10-22: 16 records, Te Sun 1994 first (named for the
    F78 ceiling question); Chen 2025 (read) and the two retracted items off.
    The count is not asserted: the list shrinks as files arrive."""
    hdl = _script()
    items = hdl.ranked(live_conn, hdl.slice_counts(ROOT / "manifests"))
    ids = [item["id"] for item in items]
    assert ids[0] == "te-sun-1994-generalizing-fano-inequality"
    for gone in ("chen-2025-efficient-bayes-error-rate-estimation", "mezquita-2021-retracted-chapter-review-k-nn",
                 "valdez-2023-retracted-article-review-quantum-computing"):
        assert gone not in ids
    counts = [item["cited_by_count"] for item in items[1:]]
    assert None not in counts and counts == sorted(counts, reverse=True)
