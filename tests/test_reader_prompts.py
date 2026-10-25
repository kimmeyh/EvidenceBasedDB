"""No reading budget (team lead, 2026-10-25, at Sprint 13 Manual Validation:
"remove the budget ... ensure that all future paper reads have no budget").

Until then each sprint's reader prompt asked for "at least the abstract,
introduction, results and conclusion" and "2 to 4 assertions per paper", and
551 of Sprint 13's 795 first-pass reads were partial. Every reader prompt
from Sprint 13 Task G on must ask for the whole paper and set no cap on
assertions. The prompts that ran before keep their text: each reader file
is traced to the instructions it ran under.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAN_BEFORE = {"sprint11_reads", "sprint12_reads", "sprint13_reads"}
BUDGET = re.compile(r"at least the abstract|\b\d+ to \d+ assertions per paper|assertions per paper|skim",
                    re.IGNORECASE)


def instructions(path: Path) -> str:
    """The part a reader runs under: everything after the first "---" line."""
    text = path.read_text(encoding="utf-8")
    return text.split("\n---\n", 1)[1] if "\n---\n" in text else text


def budget_problems(text: str) -> list[str]:
    out = [m.group(0) for m in BUDGET.finditer(text)]
    if "every page" not in text.lower():
        out.append('no "every page"')
    if "no cap" not in text.lower():
        out.append('no "no cap" on assertions')
    return out


def prompts() -> list[Path]:
    return sorted(p for p in (ROOT / "manifests").glob("*/READER_PROMPT.md") if p.parent.name not in RAN_BEFORE)


def test_every_reader_prompt_from_task_g_on_reads_the_whole_paper_with_no_cap():
    """Proven to fail by injection, 2026-10-25: with Task F's instructions
    put in Task G's place, the test went red on "at least the abstract",
    "assertions per paper", the missing "every page" and "no cap"."""
    found = prompts()
    assert found, "no reader prompt from Task G on: manifests/sprint13_g_reads/READER_PROMPT.md is gone"
    assert {p: budget_problems(instructions(p)) for p in found if budget_problems(instructions(p))} == {}


def test_the_budget_check_names_each_budget():
    """The check itself, on Task F's prompt, the last one with a budget."""
    old = instructions(ROOT / "manifests" / "sprint13_reads" / "READER_PROMPT.md")
    problems = budget_problems(old)
    assert "at least the abstract" in problems and any("per paper" in p for p in problems), problems
    assert 'no "every page"' in problems and 'no "no cap" on assertions' in problems
