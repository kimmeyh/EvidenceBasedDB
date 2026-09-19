"""The backlog-refinement skill exists, reads the format doc first, and
carries Task A's phase numbering (Sprint 4 Task J, F20).

F20's card names the gap this closes: docs/BACKLOG_REFINEMENT.md's
format was already current; what was missing was an invocation contract
that makes "read the format doc IN THIS TURN" the first step rather than
a habit. A skill that drifted back to "Phase 8" refinement, or whose
first step no longer names the same-turn read, would silently undo Task
A and F20 together, so both are pinned here.

Verified by injection: (1) renaming the skill directory fails
test_skill_exists_with_frontmatter; (2) rewriting the Step 1 heading to
"Step 1: gather the inputs" fails test_first_step_is_reading_the_format_
doc_in_the_same_turn; (3) inserting the phrase "prior sprint's Phase 8
refinement" as a bare rule fails
test_skill_uses_task_a_phase_numbering_not_phase_8. Each restored and
green again.

What these tests would NOT catch: a skill whose Step 1 says the right
words but whose later steps contradict them, or a session that has the
skill and does not invoke it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "backlog-refinement" / "SKILL.md"
FORMAT_DOC = ROOT / "docs" / "BACKLOG_REFINEMENT.md"


def _body() -> str:
    assert SKILL.exists(), f"{SKILL} is missing (F20)"
    return SKILL.read_text(encoding="utf-8")


def test_skill_exists_with_frontmatter():
    body = _body()
    assert body.startswith("---\nname: backlog-refinement\n"), "SKILL.md must open with the name frontmatter"
    assert re.search(r"^description: .+", body, re.M), "SKILL.md must carry a description line"
    assert FORMAT_DOC.exists(), "the doc the skill wraps must exist"


def test_first_step_is_reading_the_format_doc_in_the_same_turn():
    body = _body()
    steps = re.findall(r"^### Step (\d+): (.+)$", body, re.M)
    assert steps and steps[0][0] == "1", f"expected a '### Step 1:' heading first, got {steps[:1]}"
    first_heading = steps[0][1].lower()
    assert "read the format doc" in first_heading and "this turn" in first_heading, (
        f"Step 1 must be reading docs/BACKLOG_REFINEMENT.md in the same turn; got {steps[0][1]!r}")
    assert "docs/BACKLOG_REFINEMENT.md" in body
    assert re.search(r"earlier turn.{0,80}does not count", body, re.S), (
        "the skill must state that a read from an earlier turn does not count")


def test_skill_uses_task_a_phase_numbering_not_phase_8():
    """Backlog Refinement is Sprint N's Phase 1 on Sprint N's branch
    (Sprint 4 Task A). The skill must name Phase 1.2 and 1.4 and must not
    present Phase 8 as where refinement lives (a historical mention that
    says it is NOT there is allowed)."""
    body = _body()
    assert "Phase 1.2" in body and "Phase 1.4" in body
    for line in body.splitlines():
        if "Phase 8" in line:
            assert re.search(r"never|not |re-hom", line, re.I), (
                f"the skill homes refinement in Phase 8 again: {line!r}")
    assert "Candidates at a glance" in body


def test_skill_has_no_em_dashes():
    assert chr(8212) not in _body(), "SKILL.md contains an em dash (QUALITY_STANDARDS.md)"
