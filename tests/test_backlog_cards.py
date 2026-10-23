"""Backlog cards carry the fields F94 adopted from spamfilter-multi (Sprint 11 Task B).

Every card under the master plan's "Next Sprint Candidates" has: an effort
in minutes in its header (spamfilter-multi BACKLOG_REFINEMENT.md, "EFFORT IS
IN MINUTES, ALWAYS"; an hour figure invites rounding up), and the bullets
Phase, Platform, Value (spamfilter-multi's value statement: "This
enables..." or "This prevents..."), Acceptance and Depends on. The format is
`docs/BACKLOG_REFINEMENT.md`, "Item format".

Proven to fail by injection, 2026-10-22: changing F93's header effort to
"~1h" turned test_every_card_states_its_effort_in_minutes red; deleting F91's
Value bullet turned test_every_card_carries_the_standard_bullets red. Both
restored.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "ALL_SPRINTS_MASTER_PLAN.md"
HEADER = re.compile(r"^\*\*(F\d+)\. (.+?)\*\*", re.M)
MINUTES = re.compile(r"\(~\d+m\b[^)]*\) Priority (\d+|HOLD)$")
BULLETS = ("- Phase:", "- Platform:", "- Value:", "- Acceptance", "- Depends on:")


def _cards() -> dict[str, tuple[str, str]]:
    text = PLAN.read_text(encoding="utf-8")
    section = text.split("## Next Sprint Candidates", 1)[1].split("\n## ", 1)[0]
    heads = list(HEADER.finditer(section))
    out = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(section)
        out[m.group(1)] = (m.group(2), section[m.end():end])
    return out


def test_the_backlog_has_cards():
    assert len(_cards()) >= 5


def test_every_card_states_its_effort_in_minutes():
    bad = {f: head for f, (head, _) in _cards().items() if not MINUTES.search(head)}
    assert not bad, f"cards whose header effort is not '(~<n>m ...) Priority <N>': {bad}"


def test_every_card_carries_the_standard_bullets():
    missing = {}
    for f, (_, body) in _cards().items():
        lines = [line for line in body.splitlines() if line.startswith("- ")]
        gone = [b for b in BULLETS if not any(line.startswith(b) for line in lines)]
        if gone:
            missing[f] = gone
    assert not missing, f"cards missing standard bullets: {missing}"
