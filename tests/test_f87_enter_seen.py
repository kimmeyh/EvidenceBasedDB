"""F87 (Sprint 10 Task J), Manual Validation Q4 = 2 and Q6: the live
re-run's top-listed candidates enter at `seen`, except the eight excluded,
and the two the team lead switched enter under `ml`. The cut skips the
records the F87 filters dropped, as the review's ranking did."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _script():
    spec = importlib.util.spec_from_file_location("f87_enter", ROOT / "scripts" / "sprint10_f87_enter_seen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rows(mod) -> list[dict]:
    """Per stream: a dropped record first, 30 checked candidates titled so
    each pinned rank carries its pinned title, then 5 unchecked."""
    rows = []
    for stream in mod.STREAMS:
        # Checked, so only the dropped flag keeps it out
        rows.append({"stream": stream, "title": f"{stream} dropped", "dropped": "topic: x", "citation_check": "agree"})
        for rank in range(1, 31):
            title = {**mod.OFF_TOPIC, **mod.SWITCHED_TO_ML}.get((stream, rank), f"{stream} paper {rank}")
            rows.append({"stream": stream, "title": title, "citation_check": "agree", "arxiv": None,
                         "s2_arxiv": None, "doi": f"10.1/{stream}.{rank}", "rank_cites": 10, "rank_year": 2020,
                         "dropped": None})
        rows += [{"stream": stream, "title": f"{stream} unchecked {i}", "citation_check": "unchecked"}
                 for i in range(5)]
    return rows


def test_the_cut_is_the_top_25_less_the_8_exclusions_and_skips_dropped_records():
    """Proven to fail by injection, 2026-10-19: with top_lists() keeping
    dropped records, each stream's list shifted down one, the pinned
    titles no longer matched their ranks and chosen() raised."""
    mod = _script()
    picks = mod.chosen(mod.top_lists(_rows(mod)))
    assert len(picks) == 4 * 25 - 8 == 92
    assert all(rank <= 25 and (stream, rank) not in mod.OFF_TOPIC for stream, rank, _ in picks)
    assert not any("unchecked" in c["title"] or "dropped" in c["title"] for *_, c in picks)


def test_an_exclusion_on_a_shifted_list_stops_the_run():
    """Proven to fail by injection, 2026-10-19: with chosen() skipping the
    title check, no error was raised."""
    mod = _script()
    rows = _rows(mod)
    i, j = (rows.index(r) for r in rows if r["stream"] == "ml" and r["title"] in ("QuPath", "ml paper 19"))
    rows[i], rows[j] = rows[j], rows[i]  # QuPath moves from rank 18 to 19
    with pytest.raises(ValueError, match="ml rank 18"):
        mod.chosen(mod.top_lists(rows))


def test_a_switched_paper_on_a_shifted_list_stops_the_run():
    """The switch to ml is pinned too, so a re-ranked file cannot move
    another paper to ml. Proven to fail by injection, 2026-10-19: with
    chosen() skipping the title check, no error was raised."""
    mod = _script()
    rows = _rows(mod)
    i, j = (rows.index(r) for r in rows if r["stream"] == "qml" and r["title"] in ("FCHL revisited", "qml paper 18"))
    rows[i], rows[j] = rows[j], rows[i]
    with pytest.raises(ValueError, match="qml rank 17"):
        mod.chosen(mod.top_lists(rows))


def test_the_two_switched_papers_enter_under_ml_and_say_so():
    """Team lead, 2026-10-19: FCHL and the alchemical paper "better fit in
    ml". Proven to fail by injection, 2026-10-19: with the SWITCHED_TO_ML
    line removed from CONTEXT_BY_RANK, both entered under qml."""
    mod = _script()
    for (stream, rank), title in mod.SWITCHED_TO_ML.items():
        e = mod.entry_for(stream, rank, {"title": title, "arxiv": "1909.01946", "rank_cites": 1, "rank_year": 2019})
        assert e["context"] == "ml" and "switched to ml by the team lead" in e["disposition"]


def test_every_entry_names_a_real_context_and_its_rank():
    mod = _script()
    for stream, rank, c in mod.chosen(mod.top_lists(_rows(mod))):
        e = mod.entry_for(stream, rank, c)
        assert e["context"] in {"ml", "qml", "qc", "world"}
        assert f"{stream} stream rank {rank}" in e["disposition"] and e["tier"] == "seen"


@pytest.mark.live_store
def test_every_chosen_candidate_is_in_the_store(live_conn):
    """Manual Validation Q6: all 91 entered (86 by the first apply, the five
    retitled preprints by journal DOI). Proven to fail by injection,
    2026-10-19: with ml rank 1's identifiers and title replaced by ones the
    store lacks, this test named "ml 1"."""
    import json
    mod = _script()
    if not mod.REVIEW.exists():
        pytest.fail(f"{mod.REVIEW} is missing")
    keys = mod.disc.store_keys(live_conn)
    picks = mod.chosen(mod.top_lists(json.loads(mod.REVIEW.read_text(encoding="utf-8"))))
    assert len(picks) == 91
    missing = [f"{s} {r}" for s, r, c in picks if not mod.disc.held_by_store(c, keys)]
    assert not missing, missing
