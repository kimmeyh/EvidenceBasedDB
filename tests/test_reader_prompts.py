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
# The fresh-eyes review of a3b8074: "at most 5 assertions", "up to 4 assertions" and "read the abstract and
# conclusion" passed the first pattern.
BUDGET = re.compile(r"at least the abstract|assertions per paper|\b(at most|up to|no more than|\d+ to)\s+\w+\s+"
                    r"(assertions|claims)|read (only )?the abstract|\bskim|minutes? (per|a|each) (paper|record)",
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
    """The check itself, on Task F's prompt, the last one with a budget, and
    on the wordings the fresh-eyes review of a3b8074 found passing."""
    old = instructions(ROOT / "manifests" / "sprint13_reads" / "READER_PROMPT.md")
    problems = budget_problems(old)
    assert "at least the abstract" in problems and "2 to 4 assertions" in problems, problems
    assert 'no "every page"' in problems and 'no "no cap" on assertions' in problems
    clean = "Read every page. There is no cap on assertions."
    assert budget_problems(clean) == []
    for budget in ("Return at most 5 assertions.", "Give up to 4 claims.", "Read the abstract and conclusion.",
                   "Spend about 2 minutes per paper.", "Skim the appendices."):
        assert budget_problems(f"{clean} {budget}"), budget
