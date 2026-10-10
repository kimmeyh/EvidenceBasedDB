"""Every completed sprint keeps its three documents.

SPRINT_EXECUTION_WORKFLOW.md 3.2.1 states the three-doc rule "no exceptions":
every completed sprint has SPRINT_N_PLAN.md, SPRINT_N_RETROSPECTIVE.md and
SPRINT_N_SUMMARY.md. Until Sprint 12 nothing enforced it, so a missing document
was invisible -- and Sprint 12's summary was in fact missing until the
retrospective went looking.

The rule is worth enforcing because the summary is the only document written
AFTER a sprint's consequences are known. A plan records intent and a
retrospective records process; the summary is where the sprint says what it
actually established, and it is the one a later reader reaches for first.

Scope note: the CURRENT sprint is exempt from BOTH the summary and the
retrospective, because 3.2.1 binds every "completed sprint" and the one in
flight has neither yet -- the retrospective lands at Phase 7, the summary during
N+1 planning. Only the plan is owed while a sprint is live.

That exemption was too narrow when first written (summary only), and this guard
fired against Sprint 13's own plan document the moment it was created. Fixed and
verified by injection: with the current sprint set to 13, removing COMPLETED
Sprint 11's retrospective still fails with
`assert not ['SPRINT_11_RETROSPECTIVE.md']`, and restoring it passes. The
exemption covers the live sprint only, not the rule.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPRINTS = ROOT / "docs" / "sprints"
STATUS = ROOT / ".claude" / "sprint_status.json"


# The phase NUMBER, read from either status form: "Phase 1.1 Backlog
# Refinement -- ..." (the one format since Sprint 7 retrospective I6, which
# the status footer reads) or the older "phase_1_refinement". The lookahead
# keeps "phase_10_..." and "Phase 10.1" from reading as phase 1 (caught by
# this module's own edge-case test before the rule ever ran against a real
# file).
PRE_PLANNING_PHASES = (1, 2)
PHASE_NUMBER = re.compile(r"(?i)^\s*phase[ _](\d+)(?=[._ ]|$)")
# What the status footer script parses: "Phase n.n <Name>" at the start.
FOOTER_FORMAT = re.compile(r"^Phase \d+\.\d+ [A-Za-z]")


def phase_number(status: str) -> int | None:
    m = PHASE_NUMBER.match(status)
    return int(m.group(1)) if m else None


def _current_status() -> dict | None:
    if not STATUS.exists():
        return None
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))["current_sprint"]
    except Exception:                                   # noqa: BLE001
        return None


def _current_sprint() -> int | None:
    """The sprint still in flight, which owes no summary yet."""
    st = _current_status()
    try:
        return int(st["number"]) if st else None
    except Exception:                                   # noqa: BLE001
        return None


def status_requires_plan_doc(current_sprint: dict) -> bool:
    """A sprint owes SPRINT_N_PLAN.md from Phase 3 on -- not during Phase 1
    (Backlog Refinement) or Phase 2 (Pre-Kickoff), which happen on Sprint
    N's branch BEFORE its plan exists (workflow re-homing, 2026-09-19,
    Sprint 4 Task A). Before that change, sprint_status kept the finished
    sprint's number through refinement to satisfy this test, and the
    close-out Stop hook -- which requires number == branch -- blocked the
    close-out message (F27). One rule now: the number follows the branch;
    the plan is owed from Phase 3."""
    status = str(current_sprint.get("status", ""))
    return phase_number(status) not in PRE_PLANNING_PHASES


def previous_summary_may_wait(current_sprint: dict) -> bool:
    """Sprint N-1's SUMMARY is written at N-1's Phase 7 or in N's Phase 1.2
    sweep; during N's Phase 1/2 it may not exist yet. Owed from Phase 3."""
    return not status_requires_plan_doc(current_sprint)


def _sprint_numbers() -> list[int]:
    seen = set()
    for f in SPRINTS.glob("SPRINT_*_PLAN.md"):
        m = re.match(r"SPRINT_(\d+)_PLAN\.md", f.name)
        if m:
            seen.add(int(m.group(1)))
    return sorted(seen)


@pytest.mark.skipif(not SPRINTS.exists(), reason="no sprint docs directory")
def test_every_completed_sprint_has_all_three_documents():
    """Plan, retrospective and summary, for every sprint that has finished."""
    current = _current_sprint()
    missing: list[str] = []
    for n in _sprint_numbers():
        for kind in ("PLAN", "RETROSPECTIVE", "SUMMARY"):
            # 3.2.1 binds every COMPLETED sprint. The sprint in flight has a
            # plan and owes the other two at its own close-out: the
            # retrospective at Phase 7, the summary during N+1 planning.
            # Demanding either mid-sprint fails the moment a plan is written,
            # which is how this guard first fired against Sprint 13's own plan.
            if n == current and kind in ("SUMMARY", "RETROSPECTIVE"):
                continue
            st = _current_status()
            if st and n == (current or 0) - 1 and kind == "SUMMARY" and previous_summary_may_wait(st):
                continue
            f = SPRINTS / f"SPRINT_{n}_{kind}.md"
            if not f.exists():
                missing.append(f.name)
    assert not missing, (
        f"the three-doc rule (workflow 3.2.1, 'no exceptions') is unmet: "
        f"{missing}. A sprint's summary is the only document written after its "
        f"consequences are known; write it rather than deleting this test.")


@pytest.mark.skipif(not SPRINTS.exists(), reason="no sprint docs directory")
def test_sprint_documents_are_not_placeholders():
    """A file that exists but says nothing satisfies the letter and not the rule.

    The retrospective template ships with `[feedback]` placeholders, and its own
    exit gate requires all 16 categories filled by all 4 roles. A retrospective
    still holding placeholders has not been conducted.
    """
    thin: list[str] = []
    for f in sorted(SPRINTS.glob("SPRINT_*.md")):
        body = f.read_text(encoding="utf-8")
        if len(body.strip()) < 400:
            thin.append(f"{f.name} (only {len(body.strip())} chars)")
        if "[feedback]" in body:
            thin.append(f"{f.name} (unfilled [feedback] placeholder)")
    assert not thin, f"sprint documents present but not written: {thin}"


@pytest.mark.skipif(not STATUS.exists(), reason="no sprint_status.json")
def test_sprint_status_points_at_a_real_sprint():
    """The status file is how tooling knows which sprint is live.

    Sprint 12 ran with this file reading `phase_4_execution` and `pr: null`
    against a sprint that had already merged two PRs, and an automated reviewer
    read the stale value and called the work "Sprint 13's". A status file nobody
    updates is worse than none, because it is quoted.
    """
    st = json.loads(STATUS.read_text(encoding="utf-8"))["current_sprint"]
    n = int(st["number"])
    if status_requires_plan_doc(st):
        assert (SPRINTS / f"SPRINT_{n}_PLAN.md").exists(), (
            f"sprint_status.json names sprint {n} at {st.get('status')!r}, which has no plan document")
        plan = st.get("plan_doc")
        if plan:
            assert (ROOT / plan).exists(), f"plan_doc {plan} does not exist"
    else:
        # Phase 1/2 on Sprint N's branch, before its plan exists: the number
        # must still be a REAL next sprint (N-1 has a plan) and plan_doc must
        # be null rather than pointing at the previous sprint's plan.
        assert (SPRINTS / f"SPRINT_{n - 1}_PLAN.md").exists(), (
            f"sprint_status.json names sprint {n} in a pre-planning phase, but sprint {n - 1} "
            "has no plan document -- the number skipped a sprint")
        assert st.get("plan_doc") in (None, ""), (
            f"pre-planning status {st.get('status')!r} must carry plan_doc null, not {st.get('plan_doc')!r}")


def test_status_requires_plan_doc_only_from_phase_3():
    """Pure-function check of the rule, plus its edges, so the exemption
    cannot silently widen: phase_1/phase_2 exempt, everything else owes
    the plan, an empty or missing status owes it too."""
    assert not status_requires_plan_doc({"status": "phase_1_refinement"})
    assert not status_requires_plan_doc({"status": "phase_2_pre_kickoff"})
    assert status_requires_plan_doc({"status": "phase_3_plan_drafted"})
    assert status_requires_plan_doc({"status": "phase_4_execution"})
    assert status_requires_plan_doc({"status": "phase_8_delivery_cycle"})
    assert status_requires_plan_doc({"status": ""})
    assert status_requires_plan_doc({})
    assert status_requires_plan_doc({"status": "phase_10_made_up"})  # startswith("phase_1") must not match
    assert not status_requires_plan_doc({"status": "Phase 1.1 Backlog Refinement"})
    assert not status_requires_plan_doc({"status": "Phase 2.3 Pre-Kickoff -- issues closed"})
    assert status_requires_plan_doc({"status": "Phase 4.1 Execution"})
    assert status_requires_plan_doc({"status": "Phase 10.1 Made Up"})


@pytest.mark.skipif(not STATUS.exists(), reason="no sprint_status.json")
def test_the_live_status_is_in_the_footer_format():
    """Sprint 7 retrospective I6: the status footer reads the phase from
    "Phase n.n <Name>" at the start of the status, and printed no phase at
    all for "Phase 7 Retrospective" (2026-10-09) or for the older
    "phase_4_execution" form. Proven to fail by injection, 2026-10-10: with
    the live status set to "phase_7_retrospective", this test went red.
    The pre-planning value is "Phase 1.1 Backlog Refinement" (workflow
    8.2)."""
    st = json.loads(STATUS.read_text(encoding="utf-8"))["current_sprint"]
    status = str(st.get("status", ""))
    assert FOOTER_FORMAT.match(status), (
        f"sprint_status.json status {status!r} does not start with 'Phase n.n <Name>'; "
        "the footer cannot read its phase")
    assert "updated" not in json.loads(STATUS.read_text(encoding="utf-8")), (
        "'updated' is a stored copy of what git log answers; it was removed in Sprint 7 (I6)")
