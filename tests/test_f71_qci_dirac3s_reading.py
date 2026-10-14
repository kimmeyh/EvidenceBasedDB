"""F71 (Sprint 8 Task G): every quote in the Dirac-3S release, benchmarking
review and product-page assertions is in its source's local copy; the
admission-against-interest candidates stay un-upgraded until the team lead
decides (Class 2); the site check's lists are computed, not hand-made."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_f45_dirac3_reading import _QUOTE, _text  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.live_store
def test_every_quote_is_in_a_yielding_source(live_conn):
    """Proven to fail by injection, 2026-10-13: with one digit of the
    "7.56" Table 6 row changed in the stored citation_context of a copy,
    this test named dirac3s-all-optimal-headline-contradicted-by-own-table."""
    f71 = _load("sprint8_f71_qci_dirac3s_reading")
    checked = 0
    for assertion, yielded_by in f71.ASSERTIONS:
        row = live_conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?",
                                (assertion.id,)).fetchone()
        assert row, f"{assertion.id}: not in the store"
        quotes = _QUOTE.findall(row[0])
        assert quotes, f"{assertion.id}: no quote found"
        texts = [_text(f71.LOCAL[r]) for r in yielded_by]
        for q in quotes:
            assert any(q in t for t in texts), f"{assertion.id}: not verbatim in its sources: {q[:70]}"
            checked += 1
    assert checked >= 20


@pytest.mark.live_store
def test_the_candidates_are_held_for_the_team_lead(live_conn):
    """Plan, Task G risks: an admission-against-interest upgrade is the team
    lead's decision; nothing in this task raises one."""
    f71 = _load("sprint8_f71_qci_dirac3s_reading")
    by_id = {a.id: a for a, _ in f71.ASSERTIONS}
    for rid in f71.CANDIDATE_UPGRADES:
        assert rid in by_id, rid
        certainty, reasons = live_conn.execute("SELECT certainty, certainty_reasons FROM records WHERE id = ?",
                                               (rid,)).fetchone()
        assert certainty == "moderate" and "UPGRADED" not in reasons, f"{rid}: {certainty}"


def test_the_site_check_separates_menu_changes_from_page_changes():
    """A difference found on half or more of the compared pages (the site's
    new "Benchmarking" menu entry) is not a page change. Proven to fail by
    injection, 2026-10-13: with site_wide returning an empty set, the
    menu-only page was counted as changed."""
    g = _load("sprint8_f71_qci_site_check")
    menu = g.word_changes("Home Lessons Qudits are levels", "Home Lessons Benchmarking Qudits are levels")
    real = g.word_changes("Introducing Dirac-3 949 Variables", "Introducing Dirac-3S 9,980 Variables")
    diffs = {"a": menu, "b": menu, "c": menu | real}
    chrome = g.site_wide(diffs)
    assert [u for u, d in diffs.items() if d - chrome] == ["c"]


def test_a_small_section_keeps_its_own_change():
    """PR #77 review: a section with one or two compared pages read its own
    change as that section's menu, so the Dirac-3 product page could be
    reported unchanged. Proven to fail by injection, 2026-10-13: with
    MIN_CHROME_PAGES set to 1, both the one-page and the two-page cases
    went unchanged."""
    g = _load("sprint8_f71_qci_site_check")
    site = g.SITE
    menu = g.word_changes("Home Lessons Qudits", "Home Lessons Benchmarking Qudits")
    real = g.word_changes("Introducing Dirac-3 949 Variables", "Introducing Dirac-3S 9,980 Variables")
    lessons = {f"{site}/learn/lessons/l{i}": menu for i in range(3)}
    one = {**lessons, f"{site}/products/systems/dirac-3": menu | real}
    assert g.split_changed(one)[0] == [f"{site}/products/systems/dirac-3"]
    two = {**lessons, f"{site}/technology/a": menu | real, f"{site}/technology/b": menu}
    assert g.split_changed(two)[0] == [f"{site}/technology/a"]


def test_an_ambiguous_match_is_listed_not_guessed(tmp_path):
    g = _load("sprint8_f71_qci_site_check")
    (tmp_path / "lessons").mkdir()
    (tmp_path / "lessons" / "intro.html").write_text("x", encoding="utf-8")
    scraped = g.scraped_pages(tmp_path)
    urls = [f"{g.SITE}/learn/lessons/a/intro", f"{g.SITE}/learn/lessons/b/intro"]
    matched, gone, ambiguous = g.resolve(scraped, urls)
    assert matched == {} and gone == [] and ambiguous and "a/intro" in ambiguous[0] and "b/intro" in ambiguous[0]


def test_failed_fetches_and_undated_pages_are_not_lost(tmp_path):
    g = _load("sprint8_f71_qci_site_check")
    log = tmp_path / "fetch-log.tsv"
    log.write_text("t\tHTTP 503\thttps://x/a\nt\t200\thttps://x/a\nt\tredirected to https://x/\thttps://x/b\n",
                   encoding="utf-8")
    assert g.fetch_failures(log) == {"https://x/b": "redirected to https://x/"}
    index = tmp_path / "sitemap.xml"
    index.write_text('<?xml version="1.0"?><sitemapindex><sitemap><loc>u</loc></sitemap></sitemapindex>',
                     encoding="utf-8")
    with pytest.raises(ValueError):
        g.sitemap_entries(index)
    plain = tmp_path / "plain.xml"
    plain.write_text("<urlset><url><loc>https://quantumcomputinginc.com/news/x</loc></url></urlset>", encoding="utf-8")
    entries = g.sitemap_entries(plain)
    assert entries == {"https://quantumcomputinginc.com/news/x": ""}
    assert g.main(["--fetc"]) == 2


def test_recent_includes_the_scrape_day_and_undated_pages(monkeypatch):
    """PR #77 review: the cutoff is a string comparison with no boundary
    test, and a page with no `lastmod` was in no list."""
    g = _load("sprint8_f71_qci_site_check")
    monkeypatch.setattr(g, "scraped_pages", lambda old=None: {})
    news = f"{g.SITE}/news/"
    entries = {news + "on": g.SCRAPED_ON, news + "before": "2026-09-23", news + "undated": ""}
    *_, recent = g.wanted_lists(entries)
    assert recent == [news + "on", news + "undated"]


@pytest.mark.live_store
def test_a_second_apply_writes_nothing(live_copy):
    """PR #77 review: the script's idempotence was claimed, not tested."""
    from store import connect
    f71 = _load("sprint8_f71_qci_dirac3s_reading")
    conn = connect(live_copy)
    try:
        log = f71.apply_changes(conn)
    finally:
        conn.close()
    assert log and all(line.startswith("exists") for line in log), [x for x in log if not x.startswith("exists")]
