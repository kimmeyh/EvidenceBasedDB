"""F150 (Sprint 19 Task B): the full suite runs once per sprint, before the Manual Validation hand-over.

Team lead, 2026-11-21: "all the other repositories have converted to only running the full suite once per
sprint - once after development is complete and before the PR runs, prior to manual validation. At the end all
that runs is a CI suite run." And 2026-11-24: "This changes the standard process so that F150 does not need to
be included in future sprints." Until Sprint 19 the rule was Sprint 11 retrospective I2's two runs.

The three places that state the rule must say once, and the workflow must keep naming `--changed` as the gate
after the hand-over: CI runs `-m "not live_store"` only, so a store write after the hand-over is checked only
because `--changed` adds the `live_store` tests (Sprint 12 retrospective I1).

Proven red by injection, 2026-11-25: with "runs once per sprint" in the workflow changed back to "runs twice per
sprint", the first test failed (the "twice" found); with the gate sentence changed to "is checked by CI only",
the second test failed. Restored, green.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACES = (ROOT / "docs" / "SPRINT_EXECUTION_WORKFLOW.md", ROOT / "docs" / "SPRINT_CHECKLIST.md",
          ROOT / "scripts" / "run_suite.py")
TWICE = re.compile(r"(?i)(full suite|full run)[^\n.]{0,40}\btwice\b|\btwice\b[^\n.]{0,40}(full suite|full run)")


def test_no_place_says_the_full_suite_runs_twice_and_each_says_once():
    twice = {p.name: m.group(0) for p in PLACES if (m := TWICE.search(p.read_text(encoding="utf-8")))}
    assert not twice, f"F150: the full suite runs once per sprint, but {twice}"
    lacking = [p.name for p in PLACES if not re.search(r"(?i)\bonce\b", p.read_text(encoding="utf-8"))]
    assert not lacking, f"F150: these do not state the one full run: {lacking}"
    workflow = PLACES[0].read_text(encoding="utf-8")
    assert "runs once per sprint, before the Manual Validation hand-over" in workflow


def test_the_workflow_names_changed_as_the_gate_after_the_hand_over():
    workflow = PLACES[0].read_text(encoding="utf-8")
    assert re.search(r"After the hand-over, every commit[^\n]*is gated by `python scripts/run_suite.py --changed`",
                     workflow), "F150: after the hand-over the gate is `run_suite.py --changed`"
