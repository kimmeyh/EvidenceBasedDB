"""The ADR-0004 A6 and ADR-0005 A4 fields (Sprint 6 Task E, F34/F36/F37/F47).

Real-data checks run against the live store (ADR-0004 A7: no committed
export): `conn` is a COPY taken with the SQLite backup API, since several
tests write probe rows; those tests are live_store (local only, deselected
on CI). The strict-key check runs on a synthetic dump, everywhere.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import connect  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import add_found_via, add_read, add_source_link, record_probe  # noqa: E402
from store.rebuild import EXPORT_FILES, KNOWN_KEYS, UnrestorableKey, rebuild, rebuild_and_compare  # noqa: E402
from store.resolvers import certainty_caps, synthesis_input_problems  # noqa: E402

QML = "learning-qml-no-reliable-tabular-accuracy-gain"


@pytest.fixture
def conn(live_copy):
    """A copy of the live store; the live file is never written."""
    c = connect(live_copy)
    yield c
    c.close()


# ------------------------------------------------- F47: admission against interest

# Case-sensitive on purpose, and never after NOT: the store writes an applied
# upgrade as "UPGRADED" and a withheld one as "NOT upgraded". The first
# version ignored case and flagged fourier-wall-incomplete-bar-manufactures-
# advantage, the very record F47 names as NOT qualifying (Task G, 2026-10-03).
_APPLIES = re.compile(r"(?<!NOT )UPGRADED[^.]*?admission against interest")
_COST = re.compile(r"\bcostly to\b", re.I)


def admission_problems(assertions: list[dict]) -> list[str]:
    """ADR-0005 A4 (e): every reason that APPLIES the upgrade says what the
    claim cost its author. A reason that only mentions the upgrade (to
    withhold it) is not checked."""
    return [a["id"] for a in assertions
            if _APPLIES.search(a.get("certainty_reasons") or "") and not _COST.search(a["certainty_reasons"])]


@pytest.mark.live_store
def test_every_applied_admission_against_interest_names_its_cost_regression(live_export):
    """F47 over the live store's assertions. Proven to fail by injection: the
    second half of this test strips "costly to disclose" from
    cyc-general-prover-disabled's reason and the same check reports it."""
    assertions = json.loads((live_export / "assertions.json").read_text(encoding="utf-8"))
    applied = [a["id"] for a in assertions if _APPLIES.search(a.get("certainty_reasons") or "")]
    assert applied, "the check would be vacuous: no reason applies the upgrade"
    assert admission_problems(assertions) == []
    broken = [dict(a) for a in assertions]
    for a in broken:
        if a["id"] == "cyc-general-prover-disabled":
            a["certainty_reasons"] = a["certainty_reasons"].replace("costly to disclose", "worth noting")
    assert admission_problems(broken) == ["cyc-general-prover-disabled"]


def test_the_shared_upgrade_reason_always_names_the_cost():
    """Sprint 8 retrospective I3: `admission_upgrade_reason` is the one
    place an upgrade reason is built, and its output passes F47. Proven to
    fail by injection, 2026-10-13: with "costly to disclose" removed from
    the builder, admission_problems named the record."""
    from store.ingest import admission_upgrade_reason
    reason = admission_upgrade_reason("Started MODERATE: vendor guide", "QCi disclaims a guarantee", "the team lead, Q7")
    assert _APPLIES.search(reason), "the built reason does not read as an applied upgrade"
    assert admission_problems([{"id": "r", "certainty_reasons": reason}]) == []
    with pytest.raises(ValueError):
        admission_upgrade_reason("Started MODERATE", "  ")
    assert ".." not in admission_upgrade_reason("Started MODERATE: vendor guide.", "a cost")


def test_a_reason_that_withholds_the_upgrade_is_not_flagged():
    withheld = [{"id": "x", "certainty_reasons": "NOT upgraded: favourable to the author, so the "
                 "admission-against-interest upgrade does not apply"},
                {"id": "y", "certainty_reasons": "two authors at a vendor, which here argues against their interest"},
                {"id": "z", "certainty_reasons": "Started LOW: single-group preprint. NOT upgraded for admission against "
                 "interest: the counterfactual argues for the authors' own bar-completeness requirement"},
                {"id": "w", "certainty_reasons": "NOT UPGRADED for admission against interest: it costs nothing"}]
    assert admission_problems(withheld) == []


# ------------------------------------------------- A6: derivation and the caps

@pytest.mark.live_store
def test_every_assertion_carries_derivation_and_claim_type(live_export):
    assertions = json.loads((live_export / "assertions.json").read_text(encoding="utf-8"))
    assert all(a.get("derivation") in ("extracted", "synthesized", "project") for a in assertions)
    assert all(a.get("claim_type") in ("positive", "absence", "vendor-self-claim") for a in assertions)
    assert all(a.get("search_scope") for a in assertions if a["claim_type"] == "absence")


@pytest.mark.live_store
def test_every_synthesis_has_at_least_two_supporting_inputs(conn):
    assert synthesis_input_problems(conn) == []


@pytest.mark.live_store
def test_synthesis_input_check_reports_a_deliberately_thin_synthesis_regression(conn):
    """Proven to fail by injection: removing every `supports` row into one
    learning but one makes the check report it."""
    keep = conn.execute("SELECT MIN(from_assertion_id) FROM assertion_relations WHERE to_assertion_id = ? "
                        "AND relation = 'supports'", (QML,)).fetchone()[0]
    conn.execute("DELETE FROM assertion_relations WHERE to_assertion_id = ? AND relation = 'supports' "
                 "AND from_assertion_id <> ?", (QML, keep))
    assert synthesis_input_problems(conn) == [f"{QML}: 1 supporting input(s), at least 2 required"]


@pytest.mark.live_store
def test_synthesis_cap_lowers_the_qml_learning_and_only_it(conn):
    """ADR-0004 A6 (c), as reported in the amendment: the QML learning is
    stored moderate and capped low; the other two learnings are unchanged."""
    caps = certainty_caps(conn)
    assert caps[QML][0] == "low" and "synthesis cap" in caps[QML][1]
    assert "learning-ml-resampling-not-the-lever-for-strong-trees" not in caps
    assert "learning-method-check-metric-and-power-before-reading-a-difference" not in caps
    stored = conn.execute("SELECT certainty FROM records WHERE id = ?", (QML,)).fetchone()[0]
    assert stored == "moderate", "the cap is computed beside the stored judgment, never written into it"


def _retract_both_sources(conn) -> None:
    record_probe(conn, "emami-2025-financial-fraud-entropy-computing-qci", "publication_status", "withdrawn",
                 "arXiv", "2026-10-03")
    record_probe(conn, "qci-2024-profiling-cvqboost", "publication_status", "retracted", "hand", "2026-10-03",
                 anchor="fixture -- not a real retraction")


@pytest.mark.live_store
def test_retraction_floor_applies_only_when_every_source_is_unusable_regression(conn, monkeypatch):
    """ADR-0004 A6 (d): before any probe the floor is absent; one withdrawn
    source of two leaves it absent; both withdrawn or retracted computes
    very-low with each source named. Proven to fail by injection: the last
    step empties the set of unusable statuses and the floor disappears."""
    import store.resolvers as resolvers
    target = "cvqboost-vs-xgboost-auc-under-balancing"  # yielded by two papers
    assert target not in certainty_caps(conn)
    record_probe(conn, "emami-2025-financial-fraud-entropy-computing-qci", "publication_status", "withdrawn",
                 "arXiv", "2026-10-03")
    assert target not in certainty_caps(conn)
    _retract_both_sources(conn)
    cap, why = certainty_caps(conn)[target]
    assert cap == "very-low" and "emami-2025-financial-fraud-entropy-computing-qci: withdrawn" in why
    monkeypatch.setattr(resolvers, "_UNUSABLE", ())
    assert target not in certainty_caps(conn)


@pytest.mark.live_store
def test_a_synthesis_inherits_its_inputs_retraction_floor(conn):
    """Fresh-eyes review, 2026-10-03: the cap read each input's STORED
    certainty, so a learning resting on a retracted input kept its level.
    The QML learning's moderate input, once both its sources are
    unusable, is read at very-low."""
    _retract_both_sources(conn)
    cap, why = certainty_caps(conn)[QML]
    assert cap == "very-low" and "cvqboost-vs-xgboost-auc-under-balancing" in why


# ------------------------------------------------- the round trip, with every new field populated

@pytest.mark.live_store
def test_new_fields_round_trip_byte_identically(conn, tmp_path):
    """The committed export carries none of the A4 child rows yet (Task F
    back-fills them), so the CI rebuild test alone would pass without the
    rebuild knowing how to restore them. Populate one of each, export,
    and rebuild that export: it must come back byte-identical."""
    # A read paper that does not already hold the fixture's routes: Sprint 12's reads made the first read paper
    # one the QMLPapers manifest found, and adding its route again broke the unique key, not the round trip.
    paper = conn.execute(
        "SELECT record_id FROM paper_fields WHERE tier = 'read' AND record_id NOT IN (SELECT record_id FROM "
        "paper_found_via WHERE route IN ('QMLPapers/2024/manifest.tsv', 'a second fixture route')) "
        "ORDER BY record_id").fetchone()[0]
    other = conn.execute("SELECT record_id FROM paper_fields WHERE record_id <> ? ORDER BY record_id",
                         (paper,)).fetchone()[0]
    add_found_via(conn, paper, "QMLPapers/2024/manifest.tsv", "a cited-as string")
    add_found_via(conn, paper, "a second fixture route")
    add_read(conn, paper, "Claude", "2026-10-03", "partial", "pp.1-3")
    add_read(conn, paper, "read-only agent", "2026-10-03", "subagent")
    record_probe(conn, paper, "publication_status", "published", "Crossref", "2026-10-03")
    record_probe(conn, paper, "access_status", "open", "probe", "2026-10-03")
    record_probe(conn, paper, "version_of", "10.1000/fixture", "arXiv", "2026-10-03")
    record_probe(conn, paper, "affiliations", "Somewhere University", "hand", "2026-10-03", anchor="p.1 byline")
    add_source_link(conn, other, paper, "responds-to", "the sentence that says so")
    conn.execute("UPDATE paper_fields SET metadata_provider = 'arXiv', coi = 'none declared -- p.9' "
                 "WHERE record_id = ?", (paper,))
    conn.commit()
    out = tmp_path / "export"
    regenerate(conn, out)
    record = next(p for p in json.loads((out / "papers.json").read_text(encoding="utf-8")) if p["id"] == paper)
    assert {"found_via", "read_extent", "publication_status", "access_status", "version_of", "affiliations",
            "metadata_provider", "coi"} <= set(record)
    assert record["affiliations"]["anchor"] == "p.1 byline"
    assert rebuild_and_compare(out, check_local_paths=False) == []


def test_rebuild_refuses_a_new_field_it_was_not_taught(synthetic_dump, tmp_path, monkeypatch):
    """The F30 strict-key rule extended to the new fields: with `found_via`
    taken out of KNOWN_KEYS, a record carrying it is refused, not dropped.
    Runs on a synthetic dump, everywhere."""
    export = synthetic_dump
    papers = json.loads((export / "papers.json").read_text(encoding="utf-8"))
    papers[0]["found_via"] = [{"route": "x"}]
    (export / "papers.json").write_text(json.dumps(papers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setitem(KNOWN_KEYS, "paper", KNOWN_KEYS["paper"] - {"found_via"})
    with pytest.raises(UnrestorableKey, match="found_via"):
        rebuild(export, tmp_path / "x.db", check_local_paths=False)
