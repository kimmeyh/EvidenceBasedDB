"""ADR-0005 A11 (Sprint 12 Task D, F106): a source link's evidence is either
its source's own pointer or sentence, or a named team-lead decision.

The rule is in `evidence_problem`, which the CI tests check on fixed
strings; the live test applies it to every stored link. Whether a text is
its source's own sentence cannot be told mechanically (24 Sprint 7 links
quote a sentence such as "Code to reproduce our results can be found in
Ref. [19]." with no quote marks or URL), so the test checks what it can:
the evidence is not empty, and a decision-backed one names all A11 asks."""
from __future__ import annotations

import re

import pytest

_DECIDED = re.compile(r"\bdecision\b", re.I)
_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
_WHERE = re.compile(r"\bSprint \d+\b")


def evidence_problem(link_type: str, evidence: str) -> str | None:
    """None when the evidence meets A11 (b); else what is missing."""
    evidence = evidence or ""
    if _DECIDED.search(evidence) and "team lead" in evidence:
        checks = (("the date", _DATE.search(evidence)), ("where it is recorded", _WHERE.search(evidence)),
                  ("that the link rests on it", "rests on the team lead's decision" in evidence))
        missing = [name for name, ok in checks if not ok]
        return f"decision-backed, but missing: {', '.join(missing)}" if missing else None
    if not evidence.strip():
        return f"a {link_type} link with no evidence"
    return None


def test_the_rule_on_fixed_strings():
    """Proven to fail by injection, 2026-10-23: with the date check removed
    from `evidence_problem`, the second assertion here failed; with the
    empty-evidence check removed, the fourth failed. Restored."""
    decided = ("team lead, 2026-10-22, Sprint 11 Manual Validation Q1 = 2: link it. No source names it. "
               "The link rests on the team lead's decision")
    assert evidence_problem("code-of", decided) is None
    assert evidence_problem("code-of", decided.replace("2026-10-22, ", "")) == "decision-backed, but missing: the date"
    assert evidence_problem("code-of", "Code to reproduce our results can be found in Ref. [19].") is None
    assert evidence_problem("code-of", "  ") == "a code-of link with no evidence"
    assert evidence_problem("cites", "a reference list entry") is None


@pytest.mark.live_store
def test_every_stored_source_link_meets_a11(live_conn):
    """Proven to fail by injection, 2026-10-23: the live auto-ontology-eval
    evidence with its date removed, passed through the same rule, was
    named. 1 decision-backed link as of 2026-10-23; A11 says to revisit
    the rule when they pass a handful."""
    rows = live_conn.execute("SELECT from_id, to_id, link_type, evidence FROM source_links").fetchall()
    bad = [f"{f} -> {t} ({k}): {p}" for f, t, k, e in rows if (p := evidence_problem(k, e))]
    assert not bad, bad
    decided = [f for f, _, k, e in rows if _DECIDED.search(e or "") and "team lead" in (e or "")]
    assert "nvidia-auto-ontology-eval-github-repo" in decided
    assert len(decided) <= 5, f"{len(decided)} decision-backed links: revisit ADR-0005 A11"
