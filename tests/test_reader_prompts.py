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


def test_every_reader_prompt_from_task_g_on_forbids_hook_override_tokens():
    """Sprint 13 Task G: the g007 reader used a hook override token in its
    scratch folder. An override is the team lead's and the coordinator's,
    never a reader's. Proven to fail, 2026-10-25: on the prompt as g001 to
    g014 ran it, before the "never use a hook override token" paragraph."""
    missing = [p for p in prompts() if "never use a hook override token" not in instructions(p).lower()]
    assert missing == [], f"reader prompts that do not forbid hook override tokens: {missing}"


RESTART = ("## Progress and restart", "progress.json", "done/", "partial/", "last_page_read", "start here, every time",
           "--partial")  # a local reader's paths use "\", F114's cloud reader's "/"; both are compared as "/"
# Sprint 17 F144: a reader with no tools (one Batch API request) keeps no files; the script that sends it keeps the
# state, and the prompt must say so: the script saves its state before it waits, saves the reply the moment it
# arrives, and never sends a paper again once its reply is saved.
NO_TOOLS = "you have no tools"
NO_TOOL_RESTART = ("## Progress and restart", "saves its state before it waits", "saves your reply the moment it arrives",
                   "is never sent again", "give your whole reply in one piece")


def restart_problems(text: str) -> list[str]:
    flat = " ".join(text.lower().replace("\\", "/").split())
    wanted = NO_TOOL_RESTART if NO_TOOLS in flat else RESTART
    return [w for w in wanted if w.lower() not in flat]


def test_every_reader_prompt_from_task_g_on_saves_its_progress_and_starts_from_it():
    """Team lead, 2026-10-26: readers g016 to g019 stopped at a usage limit
    with their work only in memory; "make future agent runs setup to not
    loose anything if we cross current or weekly session limits". Proven to
    fail, 2026-10-26: run on Task G's instructions with the "Progress and
    restart" section and the --partial paragraph cut, the check named all
    seven phrases missing. Sprint 17 F144's no-tool branch proven to fail,
    2026-11-07: with the F144 prompt's "Progress and restart" section cut
    (INJECTED), the check named its five phrases; and a tool reader's prompt
    is still held to the seven (the second assertion below)."""
    missing = {p: restart_problems(instructions(p)) for p in prompts()}
    assert {p: m for p, m in missing.items() if m} == {}
    old = restart_problems(instructions(ROOT / "manifests" / "sprint13_reads" / "READER_PROMPT.md"))
    assert "progress.json" in old and "saves its state before it waits" not in old, old


# Sprint 15 Task H (F114, F115, F116, F126, F129): what a reader prompt from Sprint 15 on carries.
SPRINT15 = ("every figure", "its caption alone is not a read of it", '"figures"', '"from_figure"',
            "never suggested \"high\"", "ocr text", "has \"ocr\" in its assertion's `anchor`",
            "never change a stored assertion's context", "anchors are pdf pages", "one claim per assertion",
            "a textbook-standard result is background", "is still read in", "--sprint15")
CAPTION_ONLY = re.compile(r"not `not_read` when its caption", re.IGNORECASE)


def sprint15_on() -> list[Path]:
    return [p for p in prompts() if (m := re.match(r"sprint(\d+)_", p.parent.name)) and int(m[1]) >= 15]


def sprint15_problems(text: str) -> list[str]:
    flat = " ".join(text.lower().split())
    return [w for w in SPRINT15 if w not in flat] + [m.group(0) for m in CAPTION_ONLY.finditer(text)]


def test_every_reader_prompt_from_sprint_15_on_reads_figures_and_ocr_text():
    """Sprint 15 Task H step 1: figures are read (the caption-only exemption is gone), image-only pages are read from
    their OCR text and marked "OCR", and Sprint 14's lessons are in the prompt. Proven to fail by injection,
    2026-11-01: with "One claim per assertion" cut from Sprint 15's prompt, the test went red naming it; on Sprint
    14's instructions (the last assertion) the check names the figure and OCR rules and the caption-only exemption."""
    found = sprint15_on()
    assert found, "no reader prompt from Sprint 15 on: manifests/sprint15_f114_reads/READER_PROMPT.md is gone"
    assert {p: sprint15_problems(instructions(p)) for p in found if sprint15_problems(instructions(p))} == {}
    old = sprint15_problems(instructions(ROOT / "manifests" / "sprint14_f114_reads" / "READER_PROMPT.md"))
    assert "every figure" in old and "ocr text" in old and "not `not_read` when its caption" in old, old
