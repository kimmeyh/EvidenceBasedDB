"""The shape of improvements, questions and decisions put to the team lead (team lead, 2026-11-07): one
authoritative section in `docs/SPRINT_RETROSPECTIVE.md`, with every field; the surfaces that tell Claude how to ask
point at it; and no rule surface (CLAUDE.md, the top-level docs, everything under .claude/) states the old form as a
current rule. The old form may appear only as dated history, in a paragraph that names 2026-11-07.

Proven red 2026-11-07: with the "- Evidence:" line removed from the section (INJECTED), the first test named it;
with the backlog-refinement skill's pointer reverted to "a plain numbered list ... typing a digit" (INJECTED), the
second named the skill; with the Stop hook's message put back to "with a plain numbered list" (INJECTED; the review
of the format change found it, and the first version of this test scanned four files and missed it), the third
named the hook. Each restored and green. With the Effort line's "cost to run" removed (INJECTED), the first test
named it again.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Presenting improvements, questions and decisions"
FIELDS = ("What it is:", "What it prevents:", "What it catches:", "Prevention or control:", "Long-term value:",
          "Evidence:", "Effort:", "Options:", "(Recommendation)", "all as recommended", "i1. a",
          "cost to build", "cost to run", "is a control")  # the q13 and q11 definitions, 2026-11-07
POINTERS = ("CLAUDE.md", "docs/SPRINT_EXECUTION_WORKFLOW.md", ".claude/skills/backlog-refinement/SKILL.md",
            ".claude/hooks/block_ask_user_question.py", ".claude/hooks/block_procedural_question_stop.py",
            ".claude/model_assignment_heuristics.json")
OLD_FORM = re.compile(r"plain numbered list|typing a( single)? digit|\"Recommend N\"|Recommend N line", re.IGNORECASE)
HISTORY = "2026-11-07"


def _flat(text: str) -> str:
    return " ".join(text.split())  # a title wrapped across lines still counts


def _section() -> str:
    text = (ROOT / "docs" / "SPRINT_RETROSPECTIVE.md").read_text(encoding="utf-8")
    start = text.index(f"## {TITLE} (AUTHORITATIVE)")
    return text[start:text.index("\n## ", start + 1)]


def _rule_surfaces() -> list[Path]:
    files = [ROOT / "CLAUDE.md", *sorted((ROOT / "docs").glob("*.md"))]
    files += sorted(p for p in (ROOT / ".claude").rglob("*") if p.suffix in (".md", ".py", ".json") and p.is_file()
                    and "__pycache__" not in p.parts)
    return files


def test_the_authoritative_section_carries_every_field():
    section = _section()
    missing = [f for f in FIELDS if f not in section]
    assert missing == [], f"docs/SPRINT_RETROSPECTIVE.md '{TITLE}' lacks: {missing}"


def test_every_surface_that_says_how_to_ask_points_at_the_section():
    bad = [name for name in POINTERS if TITLE not in _flat((ROOT / name).read_text(encoding="utf-8"))]
    assert bad == [], f"these do not name '{TITLE}': {bad}"


def test_no_rule_surface_states_the_old_form_as_a_current_rule():
    bad = []
    for path in _rule_surfaces():
        text = path.read_text(encoding="utf-8", errors="replace")
        for para in re.split(r"\n\s*\n", text):
            m = OLD_FORM.search(_flat(para))
            if m and HISTORY not in para:
                bad.append(f"{path.relative_to(ROOT).as_posix()}: {m[0]!r}")
    assert bad == [], f"the old question form, stated as a current rule: {bad}"
