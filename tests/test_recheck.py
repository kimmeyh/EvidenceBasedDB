"""F64 (Sprint 8 Task D, ADR-0005 A7): the staggered 12-month re-check.
Sections, dates and the version read run on synthetic ids and saved page
markup; no test sends a request."""
from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import recheck  # noqa: E402

# The submission-history block of arxiv.org/abs/2407.04512, saved
# 2026-10-12 (one request), trimmed to the markup the parser reads.
ABS_PAGE = """<meta name="citation_arxiv_id" content="2407.04512" />
    <div class="submission-history">
      <h2>Submission history</h2> From: Nicholas Chancellor [<a href="/show-email/b3e349ae/2407.04512" rel="nofollow">view email</a>]      <br/>            <strong><a href="/abs/2407.04512v1" rel="nofollow">[v1]</a></strong>
        Fri, 5 Jul 2024 13:54:04 UTC (18,650 KB)<br/>
            <strong><a href="/abs/2407.04512v2" rel="nofollow">[v2]</a></strong>
        Mon, 10 Mar 2025 21:48:23 UTC (19,371 KB)<br/>
            <strong><a href="/abs/2407.04512v3" rel="nofollow">[v3]</a></strong>
        Wed, 24 Sep 2025 13:01:58 UTC (3,039 KB)<br/>
    <strong>[v4]</strong>
        Wed, 1 Oct 2025 05:33:38 UTC (3,039 KB)<br/>
</div>"""


def _probe_script():
    spec = importlib.util.spec_from_file_location("prf", ROOT / "scripts" / "probe_reference_fields.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sections_spread_a_bulk_load_evenly():
    """10,000 synthetic ids land within 15% of the mean in every section.
    Proven to fail by injection, 2026-10-12: with section_of returning a
    constant, every id fell in one section and this test went red."""
    counts = Counter(recheck.section_of(f"paper-{n}") for n in range(10_000))
    assert set(counts) == set(range(1, 25))
    mean = 10_000 / 24
    assert all(abs(c - mean) / mean < 0.15 for c in counts.values()), counts


def test_section_is_the_hash_of_the_id_and_never_changes():
    rid = "nguyen-2025-entropy-computing-paradigm-optimization-open"
    expected = int(hashlib.sha256(rid.encode()).hexdigest()[:8], 16) % 24 + 1
    assert recheck.section_of(rid) == recheck.section_of(rid) == expected


@pytest.mark.parametrize("section, start", [(1, date(2027, 1, 1)), (2, date(2027, 1, 16)),
                                            (15, date(2027, 8, 1)), (16, date(2027, 8, 16)),
                                            (24, date(2027, 12, 16))])
def test_section_starts(section, start):
    assert recheck.section_start(2027, section) == start


@pytest.mark.parametrize("last, section, expected", [
    (date(2026, 10, 3), 16, date(2027, 8, 16)),   # first start after 2027-08-03
    (date(2026, 10, 3), 15, date(2028, 8, 1)),    # 2027-08-01 is two days short of 10 months
    (date(2026, 10, 3), 11, date(2028, 6, 1)),
    (date(2026, 10, 3), 17, date(2027, 9, 1)),
    (date(2026, 12, 31), 21, date(2027, 11, 1)),  # the 31st of a 30-day month: October 31 is fine
    (date(2026, 4, 30), 5, date(2027, 3, 1)),     # 10 months lands on February 28
    (date(2026, 4, 30), 4, date(2028, 2, 16)),    # February 16 is before February 28
    (date(2027, 8, 16), 16, date(2028, 8, 16)),   # one year later in the same section
])
def test_next_recheck_is_the_first_section_start_at_least_ten_months_on(last, section, expected):
    assert recheck.next_recheck(last, section) == expected
    assert (expected.year - last.year) * 12 + expected.month - last.month >= 10


def _mini_store() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("CREATE TABLE records (id TEXT PRIMARY KEY, updated TEXT);"
                       "CREATE TABLE paper_fields (record_id TEXT PRIMARY KEY, access TEXT, evidence TEXT);"
                       "CREATE TABLE paper_probes (record_id TEXT, field TEXT, value TEXT, provider TEXT, "
                       "probed_on TEXT)")
    return conn


def test_last_check_skips_hand_readings_and_falls_back_to_updated():
    """Q4: a record with no probe takes its `updated` date, by the same rule."""
    conn = _mini_store()
    conn.executemany("INSERT INTO records VALUES (?, ?)", [("a", "2026-09-20"), ("b", "2026-09-21")])
    conn.executemany("INSERT INTO paper_fields VALUES (?, ?, NULL)", [("a", "arXiv:1"), ("b", "D:\\x.pdf")])
    conn.executemany("INSERT INTO paper_probes VALUES (?, ?, ?, ?, ?)", [
        ("a", "publication_status", "preprint", "arXiv", "2026-10-03"),
        ("a", "access_status", "open (HTTP 200)", "HTTP probe", "2026-10-05"),
        ("a", "publication_status", "withdrawn", "hand", "2026-10-09")])
    assert recheck.last_check(conn, "a") == date(2026, 10, 5)
    assert recheck.last_check(conn, "b") == date(2026, 9, 21)


def test_due_selects_only_records_past_their_date():
    conn = _mini_store()
    ids = [f"p{n}" for n in range(200)]
    conn.executemany("INSERT INTO records VALUES (?, '2026-10-03')", [(i,) for i in ids])
    conn.executemany("INSERT INTO paper_fields VALUES (?, 'arXiv:1', NULL)", [(i,) for i in ids])
    assert recheck.due(conn, date(2027, 8, 15)) == []
    first = recheck.due(conn, date(2027, 8, 16))
    assert first and all(recheck.section_of(i) == 16 for i, _, _ in first)
    assert len(recheck.due(conn, date(2028, 8, 1))) == 200


def test_latest_version_is_read_from_the_submission_history():
    assert recheck.latest_version(ABS_PAGE) == 4
    assert recheck.latest_version(ABS_PAGE.replace("submission-history", "something-else")) is None


def test_stamp_version_names_the_right_paper():
    text = "arXiv:2407.04512v2 [quant-ph] 10 Mar 2025\nEntropy Computing"
    assert recheck.stamp_version(text, "2407.04512") == 2
    assert recheck.stamp_version(text, "2108.00131") is None


def test_local_check_reports_present_changed_and_missing(tmp_path):
    f = tmp_path / "paper.pdf"
    f.write_bytes(b"%PDF one")
    good = f"SHA-256 {hashlib.sha256(b'%PDF one').hexdigest()}"
    assert recheck.check_local(f"{f} | https://x", good)[0] == "local copy present (SHA-256 unchanged)"
    assert recheck.check_local(str(f), None)[0] == "local copy present (no SHA-256 recorded)"
    f.write_bytes(b"%PDF two")
    assert recheck.check_local(str(f), good)[0] == "local copy changed (SHA-256 differs)"
    f.unlink()
    assert recheck.check_local(str(f), good)[0] == "local copy missing"


def test_findings_sort_a_record_into_the_three_lists():
    """ADR-0005 A7 (d). Proven to fail by injection, 2026-10-12: with the
    comparison `latest > local` reversed, the re-pull case went red."""
    prf = _probe_script()
    lists = {name: [] for name in prf.FINDING_LISTS}
    found = [("publication_status", "published", "arXiv abstract page"), ("version_of", "10.1/x", "arXiv abstract page")]
    prf.recheck_findings(lists, "r1", "arXiv:2407.04512", "arxiv", found, "preprint", {"latest_version": 4},
                         local_version_of=lambda ident: 2)
    assert lists["re-pull"] == ["r1: local copy v2, arXiv shows v4"]
    assert lists["newly published"] == ["r1: 10.1/x"]
    prf.recheck_findings(lists, "r2", "arXiv:2407.04512", "arxiv", found, "published", {"latest_version": 4},
                         local_version_of=lambda ident: 4)
    prf.recheck_findings(lists, "r3", "arXiv:2407.04512", "arxiv", found, "published", {"latest_version": 9},
                         local_version_of=lambda ident: None)
    assert lists["re-pull"] == ["r1: local copy v2, arXiv shows v4"], "same version, or no local copy, is not re-pulled"
    assert lists["newly published"] == ["r1: 10.1/x"], "already published is not new"
    prf.recheck_findings(lists, "r4", "arXiv:1", "arxiv", [("publication_status", "withdrawn", "x")], "preprint",
                         {"latest_version": None})
    assert lists["withdrawn"] == ["r4: withdrawn"]
    assert lists["version unread"] == ["r4"]


def test_a_local_only_record_is_checked_and_recorded_as_a_probe(tmp_path):
    """Q5 = 1, all papers: the file check is an access_status probe, so its
    last-check date moves like any other."""
    prf = _probe_script()
    f = tmp_path / "book.pdf"
    f.write_bytes(b"x")
    found, notes, answered = prf.probe("r", str(f), "hand-local", fetcher=None, extra={"evidence": None})
    assert found == [("access_status", "local copy present (no SHA-256 recorded)", recheck.LOCAL_FILE_PROVIDER)]
    assert answered is None


@pytest.mark.live_store
def test_view_shows_the_computed_schedule(live_conn):
    spec = importlib.util.spec_from_file_location("view", ROOT / "scripts" / "view.py")
    view = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(view)
    live_conn.row_factory = sqlite3.Row
    rid = "nguyen-2025-entropy-computing-paradigm-optimization-open"
    shown = view.cmd_paper(live_conn, rid)["recheck"]
    section, last, nxt = recheck.schedule(live_conn, rid)
    assert shown == {"section": str(section), "last_check": str(last), "next_recheck": str(nxt)}


@pytest.mark.live_store
def test_the_live_store_spreads_over_all_24_sections(live_conn):
    """Plan premise (b): no section more than 50% above the mean."""
    ids = [r[0] for r in live_conn.execute("SELECT record_id FROM paper_fields")]
    counts = Counter(recheck.section_of(i) for i in ids)
    assert len(counts) == 24 and max(counts.values()) < 1.5 * len(ids) / 24
