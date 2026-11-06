"""F135 (Sprint 16 Task D): a limit the paper states on its own measured result keeps the type "measured" and may be
suggested high on "stated limit"; the reader check and the reader prompt say the same. Opens no store or PDF."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from store import quotes

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "manifests" / "sprint16_f114_reads" / "READER_PROMPT.md"
TEXT = quotes.plain("Our results hold only for 8 qubits and were not tested on hardware.")


def _check():
    spec = importlib.util.spec_from_file_location("sprint13_g_check", ROOT / "scripts" / "sprint13_g_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _limit(**changes) -> dict:
    a = {"value": "The results hold only for 8 qubits", "anchor": "Section 5, p.9",
         "quotes": ["Our results hold only for 8 qubits"], "result_type": "measured", "kind": "shown",
         "claim_type": "absence", "context": "qml", "certainty_suggestion": "high", "high_basis": "stated limit",
         "certainty_reason": "Section 5 states the limit of the authors' own experiment"}
    a.update(changes)
    return a


def test_a_stated_limit_on_a_measured_result_keeps_its_type():
    """Proven to fail by injection, 2026-11-06: with the "stated limit" exception removed from the check, the limit
    typed "measured" was refused; with the exception widened to every basis, the measured result on "scope" passed."""
    check = _check()
    assert check.assertion_problems("t", _limit(), TEXT) == []
    found = check.assertion_problems("t", _limit(high_basis="scope"), TEXT)
    assert any("a measured result is never high" in x for x in found), found
    assert check.assertion_problems("t", _limit(certainty_suggestion="low", high_basis=""), TEXT) == []


def test_the_prompt_and_the_check_agree():
    """The prompt names the type and the basis the check accepts, and does not tell a reader to change the type.
    Proven to fail by injection, 2026-11-06: with the prompt's paragraph removed, the rule was not found."""
    text = " ".join(PROMPT.read_text(encoding="utf-8").split())
    rule = re.search(r"A stated limit on a measured result keeps the type \"measured\"\.\*\* (.+?)\*\*", text + "**")
    assert rule, "the reader prompt does not name a stated limit's type"
    body = rule[1]
    assert '`result_type` "measured"' in body and '`high_basis` "stated limit"' in body
    assert "Never change the type" in body
