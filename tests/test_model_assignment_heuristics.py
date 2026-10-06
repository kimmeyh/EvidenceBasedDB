"""The model-assignment heuristics file (Sprint 4 Task K, F18) exists,
parses, carries protocol as a first-class field, and its seed row matches
the source it cites.

F18's card: the static role table in docs/SPRINT_PLANNING.md names tiers
but tracks nothing; this file records task patterns with a recommended
tier AND a required protocol, escalation triggers, a rubric, and a
learning_log of real outcomes. The F7-F10 row is the first real data
point, and its numbers are pinned here against the Sprint 3 summary's
Actuals so the file cannot drift from the document it cites (CLAUDE.md:
a number in a document must be traceable).

Verified by injection: (1) deleting the "protocol" key from the Haiku
outcome fails test_every_learning_log_outcome_names_its_protocol;
(2) changing the Fable-tier tokens from 150290 to 150000 fails
test_f7_f10_row_matches_the_sprint_3_actuals; (3) setting a task
pattern's success_rate to 0.9 while its sample_size is 0 fails
test_no_success_rate_without_a_sample. Each restored and green again.

What these tests would NOT catch: a heuristics file that is accurate but
never consulted, or a learning_log row whose numbers are internally
consistent with the summary while the summary itself was wrong.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEURISTICS = ROOT / ".claude" / "model_assignment_heuristics.json"
SUMMARY = ROOT / "docs" / "sprints" / "SPRINT_3_SUMMARY.md"
PLANNING = ROOT / "docs" / "SPRINT_PLANNING.md"


def _load() -> dict:
    assert HEURISTICS.exists(), f"{HEURISTICS} is missing (F18)"
    return json.loads(HEURISTICS.read_text(encoding="utf-8"))


def test_file_parses_and_has_the_required_sections():
    d = _load()
    for key in ("tiers", "protocols", "task_patterns", "escalation_triggers", "scoring_rubric", "learning_log"):
        assert key in d, f"missing top-level section {key!r}"
    assert d["learning_log"], "learning_log must carry at least the F7-F10 row"


def test_every_task_pattern_names_a_required_protocol_and_a_known_tier():
    d = _load()
    tiers = set(d["tiers"])
    for p in d["task_patterns"]:
        assert p.get("required_protocol"), f"pattern {p.get('pattern')!r} has no required_protocol"
        assert p["recommended_tier"] in tiers, f"pattern {p.get('pattern')!r} names unknown tier {p['recommended_tier']!r}"


def test_every_learning_log_outcome_names_its_protocol():
    """Protocol is the first-class field beside tier (F18 card, Sprint 3
    retrospective improvement 4)."""
    d = _load()
    protocols = set(d["protocols"]) - {"_comment"}
    for entry in d["learning_log"]:
        for o in entry["outcomes"]:
            assert o.get("protocol") in protocols, (
                f"learning_log entry {entry['task'][:40]!r}: outcome for tier {o.get('tier')!r} "
                f"has protocol {o.get('protocol')!r}, not one of {sorted(protocols)}")
            assert o.get("tier") in d["tiers"]


def test_no_success_rate_without_a_sample():
    d = _load()
    for p in d["task_patterns"]:
        if p["sample_size"] == 0:
            assert p["success_rate"] is None, (
                f"pattern {p['pattern']!r} claims success_rate {p['success_rate']} with no samples; "
                "a rate with no outcomes behind it is an invented number")


def test_f7_f10_row_matches_the_sprint_3_actuals():
    """The seed row's tokens and seconds are the ones SPRINT_3_SUMMARY.md's
    Actuals record; read from that document, not retyped here."""
    d = _load()
    row = next(e for e in d["learning_log"] if e["sprint"] == 3)
    actuals = SUMMARY.read_text(encoding="utf-8")
    expected = {}
    for tier, label in (("haiku", "Haiku"), ("sonnet", "Sonnet"), ("opus", "Opus"), ("fable", "Fable-tier Opus")):
        m = re.search(label + r"\s+([\d,]+)(?:\s+tokens)?\s+/\s+(\d+)\s+s", actuals)
        assert m, f"SPRINT_3_SUMMARY.md Actuals no longer carry the {label} figures"
        expected[tier] = (int(m.group(1).replace(",", "")), int(m.group(2)))
    got = {o["tier"]: (o["tokens"], o["seconds"]) for o in row["outcomes"]}
    assert got == expected, f"learning_log F7-F10 row {got} != SPRINT_3_SUMMARY.md Actuals {expected}"


def test_planning_doc_points_at_the_heuristics_file():
    assert ".claude/model_assignment_heuristics.json" in PLANNING.read_text(encoding="utf-8"), (
        "docs/SPRINT_PLANNING.md's role table must reference the heuristics file (F18 card: Platform)")


# ---- F39/F40 (Sprint 6 Task A, 2026-10-03): model facts are verified, dated and current

from datetime import date as _date

MODEL_TIERS = ("haiku", "sonnet", "opus", "fable")
REQUIRED = ("model", "model_id", "agent_alias", "price_per_mtok", "context_tokens",
            "retirement_not_before", "verified", "source")


def test_every_model_tier_carries_verified_facts_regression():
    """F40's acceptance: a tier names a model, not just a role, and says
    when and where it was checked. Proven to fail by injection: deleting
    "verified" from the sonnet tier turns this red."""
    tiers = _load()["tiers"]
    missing = {t: [k for k in REQUIRED if not tiers[t].get(k)] for t in MODEL_TIERS}
    assert not any(missing.values()), f"tiers missing verified facts: {missing}"
    for t in MODEL_TIERS:
        _date.fromisoformat(tiers[t]["verified"])
        _date.fromisoformat(tiers[t]["retirement_not_before"])
        assert tiers[t]["source"].startswith("https://"), t


def test_no_tier_is_past_retirement_without_a_successor_regression():
    """A tier whose model has reached its retirement date must name a
    successor tier, or the assignment table points at nothing. Proven to
    fail by injection: setting haiku's retirement_not_before to a past date
    and its successor to null turns this red. NOTE: this test is meant to
    go red over time -- that is the signal to run the next F39 release."""
    tiers = _load()["tiers"]
    today = _date.today()
    stale = [t for t in MODEL_TIERS
             if _date.fromisoformat(tiers[t]["retirement_not_before"]) <= today
             and tiers[t].get("successor") not in MODEL_TIERS]
    assert not stale, f"tiers past retirement with no successor: {stale}"


def test_planning_role_table_names_the_verified_versions_regression():
    """The static role table in SPRINT_PLANNING.md must not drift from the
    verified file (it named "Fable 5" until F40). Proven to fail by
    injection: restoring "Fable 5 preferred" turns this red."""
    tiers = _load()["tiers"]
    text = PLANNING.read_text(encoding="utf-8")
    role_lines = [line for line in text.splitlines()
                  if line.startswith(("| Lead Developer", "| Senior Developers", "| Developers"))]
    joined = " ".join(role_lines)
    for t in MODEL_TIERS:
        version = tiers[t]["model"].removeprefix("Claude ")
        assert version in joined, f"role table does not name {version!r} (tier {t})"
