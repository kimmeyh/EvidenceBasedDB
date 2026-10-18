"""F62 (Sprint 9 Task J), Manual Validation Q4 = 1: the top-listed discovery
candidates enter at `seen`, except the 13 the team lead's answer excluded.
The cut follows the review's ranking, each exclusion is pinned to its title,
and access prefers an arXiv id over OpenAlex's DOI."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f62_enter", ROOT / "scripts" / "sprint9_f62_enter_seen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rows(mod) -> list[dict]:
    """30 checked candidates per stream, then 5 unchecked, titled so each
    excluded rank carries its pinned title."""
    rows = []
    for stream in mod.STREAMS:
        for rank in range(1, 31):
            title = mod.OFF_TOPIC.get((stream, rank), f"{stream} paper {rank}")
            rows.append({"stream": stream, "title": title, "citation_check": "agree", "arxiv": None,
                         "s2_arxiv": None, "doi": f"10.1/{stream}.{rank}", "rank_cites": 10, "rank_year": 2020})
        rows += [{"stream": stream, "title": f"{stream} unchecked {i}", "citation_check": "unchecked"} for i in range(5)]
    return rows


def test_the_cut_is_the_top_25_checked_less_the_13_exclusions():
    """Proven to fail by injection, 2026-10-15: with one OFF_TOPIC entry
    removed, the count was 88, not 87."""
    mod = _script()
    picks = mod.chosen(mod.top_lists(_rows(mod)))
    assert len(picks) == 4 * 25 - 13 == 87
    assert all(rank <= 25 and (stream, rank) not in mod.OFF_TOPIC for stream, rank, _ in picks)
    assert not any("unchecked" in c["title"] for *_, c in picks)


def test_an_exclusion_on_a_shifted_list_stops_the_run():
    """A re-ranked file must not exclude the wrong paper. Proven to fail by
    injection, 2026-10-15: with chosen() skipping the title check, no error
    was raised."""
    mod = _script()
    rows = _rows(mod)
    i, j = (rows.index(r) for r in rows if r["stream"] == "ml" and r["title"] in ("SciPy 1.0", "ml paper 7"))
    rows[i], rows[j] = rows[j], rows[i]  # SciPy moves from rank 6 to 7
    with pytest.raises(ValueError, match="ml rank 6"):
        mod.chosen(mod.top_lists(rows))


def test_access_prefers_arxiv_over_openalex_doi():
    """'Attention Is All You Need' carries a preprint mirror's DOI in
    OpenAlex. Proven to fail by injection, 2026-10-15: with access_of()
    checking the DOI first, this test got the mirror's DOI."""
    mod = _script()
    assert mod.access_of({"title": "t", "arxiv": None, "s2_arxiv": "1706.03762", "doi": "10.65215/2q58a426"}) \
        == "arXiv:1706.03762"
    assert mod.access_of({"title": "t", "arxiv": None, "s2_arxiv": None, "doi": "10.1038/nature14236"}) \
        == "DOI:10.1038/nature14236"
    with pytest.raises(ValueError):
        mod.access_of({"title": "t", "arxiv": None, "s2_arxiv": None, "doi": None})
    # A preprint retitled at publication enters by its journal DOI.
    assert mod.access_of({"title": "t", "arxiv": "1904.08128", "doi": "10.1038/s41592-020-01008-z"}, True) \
        == "DOI:10.1038/s41592-020-01008-z"


@pytest.mark.live_store
def test_every_chosen_candidate_is_in_the_store(live_conn):
    """Manual Validation Q4 = 1: all 87 entered (82 by the first apply, the
    five retitled preprints by DOI). Proven to fail by injection, 2026-10-15:
    with ml rank 1's identifiers and title replaced by ones the store lacks,
    this test named "ml 1"."""
    import json
    mod = _script()
    if not mod.REVIEW.exists():
        pytest.fail(f"{mod.REVIEW} is missing")
    keys = mod.disc.store_keys(live_conn)
    picks = mod.chosen(mod.top_lists(json.loads(mod.REVIEW.read_text(encoding="utf-8"))))
    assert len(picks) == 87
    missing = [f"{s} {r}" for s, r, c in picks if not mod.disc.held_by_store(c, keys)]
    assert not missing, missing


def test_every_entry_names_a_real_context_and_its_rank():
    mod = _script()
    for stream, rank, c in mod.chosen(mod.top_lists(_rows(mod))):
        e = mod.entry_for(stream, rank, c)
        assert e["context"] in {"ml", "qml", "qc", "world"}
        assert f"{stream} stream rank {rank}" in e["disposition"] and e["tier"] == "seen"
