"""PreToolUse hook blocking the AskUserQuestion tool call in this repository.

Team lead feedback (CLAUDE.md "Things Claude Should NOT Do"): decision
questions are written in the response text in the shape of
docs/SPRINT_RETROSPECTIVE.md "Presenting improvements, questions and
decisions" (team lead, 2026-11-07; until then a numbered list answered by a
digit), never the AskUserQuestion tool's multiple-choice UI. This was violated
twice in Sprint 2 (2026-09-17), the second time immediately after already
being corrected for the identical thing earlier in the SAME session, with the
rule present in CLAUDE.md and memory the whole time. A rule that lives only in
a document decays (this repository's own stated pattern,
`tests/test_guard_discipline.py` and others); this hook makes the block
mechanical instead of relying on remembering to apply a rule already known.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
No bypass token: unlike the sibling-repo write guard, there is no legitimate
case where AskUserQuestion is the right tool call in this repository. If a
decision question is genuinely needed, ask it as text in the response body
instead -- that path is unaffected by this hook, since it is
not a tool call at all.
"""
from __future__ import annotations

import json
import sys


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    try:
        payload = _read_payload()
    except Exception:
        return 0  # fail open on malformed payload

    tool_name = str(payload.get("tool_name") or "")
    if tool_name != "AskUserQuestion":
        return 0

    print(
        "[BLOCKED] AskUserQuestion is banned in this repository, full stop "
        "(CLAUDE.md \"Things Claude Should NOT Do\").\n"
        "\n"
        "Ask it in the response text instead, in the shape of "
        "docs/SPRINT_RETROSPECTIVE.md \"Presenting improvements, questions and "
        "decisions\": numbered q1 (i1 for an improvement), lettered options, one "
        "marked (Recommendation), answered as \"q1. a\". "
        "There is no case in this repository where the tool call is the "
        "right move; do not re-evaluate whether this particular question "
        "'fits' it.\n"
        "\n"
        "Violated twice in Sprint 2 (2026-09-17), the second time "
        "immediately after already being corrected for the same thing in "
        "the same session. This hook exists so the rule holds without "
        "depending on remembering it.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
