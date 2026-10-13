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
    (date(2026, 12, 31), 21, date(2027, 11, 1)),
    (date(2026, 12, 31), 20, date(2028, 10, 16)),  # October 16 is before October 31
    (date(2026, 7, 31), 7, date(2028, 4, 1)),      # 10 months on is 2027-05-31, after April 1
    (date(2026, 6, 1), 7, date(2027, 4, 1)),       # exactly 10 months: the start itself counts
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
                       "probed_on TEXT, PRIMARY KEY (record_id, field))")
    return conn


def test_last_check_skips_hand_readings_and_falls_back_to_updated():
    """Q4: a record with no probe takes its `updated` date, by the same rule."""
    conn = _mini_store()
    conn.executemany("INSERT INTO records VALUES (?, ?)", [("a", "2026-09-20"), ("b", "2026-09-21")])
    conn.executemany("INSERT INTO paper_fields VALUES (?, ?, NULL)", [("a", "arXiv:1"), ("b", "D:\\x.pdf")])
    conn.executemany("INSERT INTO paper_probes VALUES (?, ?, ?, ?, ?)", [
        ("a", "publication_status", "preprint", "arXiv", "2026-10-03"),
        ("a", "access_status", "open (HTTP 200)", "HTTP probe", "2026-10-05"),
        ("a", "affiliations", "QCi", "hand", "2026-10-09")])
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
    no_copy, a_copy = (lambda ident: None), (lambda ident: Path("x.pdf"))
    prf.recheck_findings(lists, "r1", "arXiv:2407.04512", "arxiv", found, "preprint", {"latest_version": 4},
                         local_version_of=lambda ident: 2, local_copy_of=a_copy)
    assert lists["re-pull"] == ["r1: local copy v2, arXiv shows v4"]
    assert lists["newly published"] == ["r1: 10.1/x"]
    prf.recheck_findings(lists, "r2", "arXiv:2407.04512", "arxiv", found, "published", {"latest_version": 4},
                         local_version_of=lambda ident: 4, local_copy_of=a_copy)
    prf.recheck_findings(lists, "r3", "arXiv:2407.04512", "arxiv", found, "published", {"latest_version": 9},
                         local_version_of=lambda ident: None, local_copy_of=no_copy)
    assert lists["re-pull"] == ["r1: local copy v2, arXiv shows v4"], "same version, or no local copy, is not re-pulled"
    assert lists["newly published"] == ["r1: 10.1/x"], "already published is not new"
    assert lists["version unread"] == []
    prf.recheck_findings(lists, "r4", "arXiv:2401.00001", "arxiv", [("publication_status", "withdrawn", "x")], "preprint",
                         {"latest_version": None}, local_copy_of=no_copy)
    assert lists["withdrawn"] == ["r4: withdrawn"]
    assert lists["version unread"] == ["r4: the abstract page showed no version"]


def test_findings_do_not_report_what_did_not_change():
    """A recorded withdrawal stays (keeps_terminal_status), so neither a
    second `withdrawn` nor a `published` over it is news; a status with no
    earlier value is listed as such. Proven to fail by injection,
    2026-10-12: with `before not in TERMINAL` removed, r1 was listed."""
    prf = _probe_script()
    lists = {name: [] for name in prf.FINDING_LISTS}
    no_copy = lambda ident: None  # noqa: E731
    no_version = lambda ident: None  # noqa: E731
    prf.recheck_findings(lists, "r1", "arXiv:2401.00001", "arxiv", [("publication_status", "withdrawn", "x")],
                         "withdrawn", {"latest_version": 1}, local_version_of=no_version, local_copy_of=no_copy)
    prf.recheck_findings(lists, "r2", "arXiv:2401.00001", "arxiv", [("publication_status", "published", "x")],
                         "retracted", {"latest_version": 1}, local_version_of=no_version, local_copy_of=no_copy)
    prf.recheck_findings(lists, "r3", "doi:10.1/y", "doi", [("publication_status", "published", "Crossref")], None,
                         {})
    assert lists["withdrawn"] == []
    assert lists["newly published"] == ["r3: no DOI given (no status was recorded before)"]


def test_an_unreadable_local_stamp_and_a_bad_local_file_are_reported():
    prf = _probe_script()
    lists = {name: [] for name in prf.FINDING_LISTS}
    prf.recheck_findings(lists, "r1", "arXiv:0705.3360", "arxiv", [], "preprint", {"latest_version": 2},
                         local_version_of=lambda ident: None, local_copy_of=lambda ident: Path("x.pdf"))
    prf.recheck_findings(lists, "r2", "D:\\x.pdf | https://x", "hand-url", [], None,
                         {"local": ("local copy missing", "D:\\x.pdf not found")})
    assert lists["version unread"] == ["r1: the local copy's first page has no readable stamp"]
    assert lists["local copy missing or changed"] == ["r2: local copy missing (D:\\x.pdf not found)"]


def test_a_due_run_passes_the_state_through_and_keeps_its_report(tmp_path, monkeypatch):
    """The plumbing in run(): site mode forced, the stored status read
    before the probe, the page's version handed back, the report written
    as it grows and reloaded by a resumed run."""
    prf = _probe_script()
    conn = sqlite3.connect(":memory:")
    conn.executescript("CREATE TABLE paper_fields (record_id TEXT PRIMARY KEY, access TEXT, evidence TEXT);"
                       "CREATE TABLE paper_probes (record_id TEXT, field TEXT, value TEXT, provider TEXT, "
                       "probed_on TEXT, PRIMARY KEY (record_id, field))")
    conn.execute("INSERT INTO paper_fields VALUES ('r1', 'arXiv:2407.04512', NULL)")
    conn.execute("INSERT INTO paper_probes VALUES ('r1', 'publication_status', 'preprint', 'arXiv', '2026-10-03')")
    seen = {}

    def fake_probe(rid, access, kind, fetcher, mode="api", extra=None):
        seen["mode"], seen["extra"] = mode, extra
        extra["latest_version"] = 5
        return [("publication_status", "published", prf.SITE_PROVIDER)], [], True

    monkeypatch.setattr(prf, "probe", fake_probe)
    monkeypatch.setattr(prf.recheck, "local_version", lambda ident, root=None: 3)
    monkeypatch.setattr(prf.recheck, "local_copy", lambda ident, root=None: Path("x.pdf"))
    monkeypatch.setattr(prf.citations, "assume_recent_arxiv_request", lambda: None)
    report = tmp_path / "report.txt"
    rc = prf.run(conn, [("r1", "arXiv:2407.04512", "arxiv")], fetcher=object(), apply=False, sessions=False,
                 progress=None, heartbeat=None, recheck_mode=True, report=report)
    assert rc == 0 and seen["mode"] == "site" and "evidence" in seen["extra"]
    text = report.read_text(encoding="utf-8")
    assert "r1: local copy v3, arXiv shows v5" in text and "newly published: 1" in text
    assert prf.load_findings(report)["re-pull"] == ["r1: local copy v3, arXiv shows v5"]


def test_due_alone_lists_and_sends_no_request(tmp_path, monkeypatch, capsys):
    """Sprint 8 retrospective I4 (ADR-0005 A8): `--due` without `--probe`
    lists from stored dates; no fetcher is built, no probe runs, no backup
    is taken. `--due --apply` without `--probe` is refused; `--due --probe`
    reaches the check. Proven to fail by injection, 2026-10-13: with the
    `--probe` gate removed from main(), the first call built the fetcher."""
    prf = _probe_script()
    db = tmp_path / "store.db"
    sqlite3.connect(db).close()
    monkeypatch.setattr(prf, "DB_PATH", db)
    monkeypatch.setattr(prf, "select", lambda conn, args: [("r1", "arXiv:2407.04512", "arxiv")])
    monkeypatch.setattr(prf.recheck, "schedule", lambda conn, rid: (7, None, None))

    def no_network(*a, **k):
        raise AssertionError("a request path was reached")

    monkeypatch.setattr(prf.citations, "PacedFetcher", no_network)
    monkeypatch.setattr(prf, "run", no_network)
    monkeypatch.setattr(prf, "backup_before_write", no_network)
    assert prf.main(["--due", "2027-09-01"]) == 0
    assert "r1  section 7" in capsys.readouterr().out
    assert prf.main(["--due", "--apply"]) == 1
    reached = []
    monkeypatch.setattr(prf.citations, "PacedFetcher", lambda: object())
    monkeypatch.setattr(prf, "run", lambda *a, **k: reached.append(k["recheck_mode"]) or 0)
    assert prf.main(["--due", "--probe"]) == 0 and reached == [True]


def test_a_folder_or_an_unreadable_file_does_not_stop_the_check(tmp_path):
    folder = tmp_path / "release"
    folder.mkdir()
    good = "SHA-256 " + "0" * 64
    assert recheck.check_local(str(folder), good)[0] == "local copy present (a folder; not hashed)"


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
