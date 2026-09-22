"""`updated_reason` is APPEND-ONLY. A correction pass may add to a record's
account of itself; it may never replace it.

PR #30 review finding 1 (2026-09-22). Three Sprint 4 scripts carried an
inverted ternary that appended only when the row had been touched the SAME
DAY and replaced the text otherwise -- so the normal case (a row carrying
history from an earlier date) was destruction. It ran: prior
`updated_reason` survived on 0 of 44 paper records, and 43 lost "Sprint 1
Task F: 46-paper seed set loaded at seen tier". Recovered by
`scripts/recover_updated_reason_history.py`.

Why this file exists rather than a note in a docstring: CLAUDE.md, "a rule
that lives only in a document decays; a rule with a failing test does not."
And the dry-run gate those scripts run did NOT catch it, because
`validate_paper()` checks the door's shape rules and has no rule about
preserving existing content. A green gate on a destructive write is the
false confidence the injection standard exists against.

Two layers here, deliberately:
  1. the append-only PROPERTY of each script's reason-joining logic, tested
     directly against the real source;
  2. the committed export, which must still carry the Sprint 1 provenance.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAPERS_EXPORT = ROOT / "export" / "papers.json"

# Every place a Sprint 4 script joins a new reason onto an existing one.
JOIN_SITES = [
    ROOT / "scripts" / "sprint4_task_c_corrections.py",
    ROOT / "scripts" / "sprint4_task_f_refiling.py",
    ROOT / "scripts" / "sprint4_task_h_extraction.py",
]

# The defect's signature: a conditional that decides whether to keep the
# existing text by testing the DATE rather than by testing whether text
# exists. `existing.startswith(TODAY)` as the condition for appending means
# older history takes the other branch, which dropped it.
DATE_GATED_JOIN = re.compile(r"if\s+(?:not\s+)?existing\.startswith\(TODAY\)")


@pytest.mark.parametrize("script", JOIN_SITES, ids=lambda p: p.name)
def test_no_script_decides_to_keep_history_by_looking_at_the_date(script):
    """The bug in one line. Appending must be conditional on the text
    EXISTING, never on when it was written."""
    source = script.read_text(encoding="utf-8")
    offenders = [line.strip() for line in source.splitlines()
                 if DATE_GATED_JOIN.search(line) and "joined" in line]
    assert not offenders, (
        f"{script.name} decides whether to preserve updated_reason by comparing "
        f"dates: {offenders}. Append when `existing` is non-empty, never when it "
        "happens to be from today -- the older text is the irreplaceable part.")


@pytest.mark.parametrize("script", JOIN_SITES, ids=lambda p: p.name)
def test_every_join_keeps_the_existing_text_on_both_branches(script):
    """Each `joined = ...` ternary must carry `{existing}` in the branch it
    takes when text is present, and must not be able to reach a branch that
    silently drops it while text exists."""
    source = script.read_text(encoding="utf-8")
    joins = [line.strip() for line in source.splitlines()
             if re.match(r"joined\s*=", line.strip())]
    assert joins, f"{script.name}: no `joined =` site found; has the script changed shape?"
    for join in joins:
        assert "if existing" in join, (
            f"{script.name}: `{join}` does not condition on `existing` being non-empty")
        before_else = join.split(" else ")[0]
        assert "{existing}" in before_else, (
            f"{script.name}: `{join}` drops the existing text on the branch taken when it exists")


def _append_only(existing: str, addition: str) -> str:
    """The correct shape, stated once so the property test can exercise it."""
    return f"{existing} | {addition}" if existing else addition


@pytest.mark.parametrize("existing,addition", [
    ("Sprint 1 Task F: 46-paper seed set loaded at seen tier", "2026-09-19: citation re-derived"),
    ("2026-09-19: an earlier pass the same day", "2026-09-19: a second pass"),
    ("", "2026-09-19: the first thing this row ever said"),
    ("a | b | c", "d"),
])
def test_the_append_only_property_holds_for_any_pair(existing, addition):
    result = _append_only(existing, addition)
    assert addition in result
    if existing:
        assert existing in result, "the prior account of the record must survive"
        assert result.startswith(existing), "history reads oldest-first"


def test_the_committed_export_still_carries_the_sprint_1_provenance():
    """The data check, not the code check. 43 papers arrived in the Sprint 1
    seed load and one in the Task E premise-falsifier run; the export must
    still say so. This is what went wrong in the live store, so this is what
    is asserted about the live artifact."""
    papers = json.loads(PAPERS_EXPORT.read_text(encoding="utf-8"))
    seeded = [p for p in papers if "Sprint 1 Task F" in (p.get("updated_reason") or "")]
    assert len(seeded) >= 43, (
        f"only {len(seeded)} papers still record the Sprint 1 seed load in "
        "updated_reason; a correction pass has erased history again. Recover with "
        "scripts/recover_updated_reason_history.py")
    lenat = next(p for p in papers if p["id"] == "lenat-marcus-2023-trustworthy-ai")
    assert "Sprint 1 Task E" in lenat["updated_reason"], (
        "the premise-falsifier record lost its own origin note")


def test_no_paper_lost_the_updated_reason_it_had_on_develop():
    """The general form: whatever a record said on `develop`, it must still
    say. Reads the last merged export from git rather than restating it here,
    so this guard keeps working as the store grows."""
    raw = subprocess.run(["git", "show", "develop:export/papers.json"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8")
    if raw.returncode != 0:
        pytest.skip("no develop:export/papers.json to compare against")
    renames = {
        "rand-2023-pqc-critical-infrastructure-assessment": "rand-2022-pqc-critical-infrastructure-assessment",
        "rand-2023-pqc-critical-infrastructure-assessment-appendix-b": "rand-2022-pqc-critical-infrastructure-assessment-appendix-b",
    }
    current = {p["id"]: (p.get("updated_reason") or "") for p in json.loads(PAPERS_EXPORT.read_text(encoding="utf-8"))}
    lost = []
    for rec in json.loads(raw.stdout):
        pid = renames.get(rec["id"], rec["id"])
        was = (rec.get("updated_reason") or "").strip()
        if not was or pid not in current:  # deleted records are a separate, deliberate decision
            continue
        if was not in current[pid]:
            lost.append(pid)
    assert not lost, (
        f"{len(lost)} record(s) lost the updated_reason they carried on develop: {lost[:5]}. "
        "updated_reason is append-only.")
