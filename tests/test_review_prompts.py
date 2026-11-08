"""F142 part 3 (Sprint 17 Task C): every review prompt from Sprint 17 on splits a proof appendix over 30 pages
across reviewers by page from the start, each part writing its own `decisions/GROUP.pN.json`, which
`f117_review.decisions_of` merges (Sprint 16: Monaco's 70-page supplement was graded from its statements, and two
fresh reviewers then changed 13 of 94 decisions).

Proven red 2026-11-07: with the split section's "over 30 pages" line changed (INJECTED), the test named the Sprint 17
prompt. It first PASSED that injection twice: the whole-file check found the phrase in the header, then the
section check found it in the section's last line; hence the section-only text and the specific phrase. with the Sprint 17 prompt folder renamed so no prompt from Sprint 17 on was found (INJECTED), the floor check
failed instead of passing on an empty list. Each restored and green.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = "## A long proof appendix"
RULE = ("holds a proof appendix over 30 pages", "by page from the start", "GROUP.pN.json", "refuses an item decided in two parts")


def _rule_text(path: Path) -> str:
    """The split section only: the prompt's header names the rule too, and a check of the whole file passed with the
    section's own line injected (first red proof, 2026-11-07)."""
    text = path.read_text(encoding="utf-8")
    if SECTION not in text:
        return ""
    start = text.index(SECTION)
    end = text.find("\n## ", start + 1)
    return " ".join(text[start:end if end > 0 else None].split())


def _prompts_from_sprint_17() -> list[Path]:
    found = []
    for path in sorted((ROOT / "manifests").glob("sprint*/REVIEW_PROMPT.md")):
        m = re.match(r"sprint(\d+)_", path.parent.name)
        if m and int(m.group(1)) >= 17:
            found.append(path)
    return found


def test_every_review_prompt_from_sprint_17_on_splits_a_long_proof_appendix_by_page():
    prompts = _prompts_from_sprint_17()
    assert prompts, "no review prompt from Sprint 17 on was found; the check would pass on nothing"
    bad = {p.relative_to(ROOT).as_posix(): [r for r in RULE if r not in _rule_text(p)] for p in prompts}
    bad = {k: v for k, v in bad.items() if v}
    assert bad == {}, f"review prompts without the F142 part 3 split rule: {bad}"
