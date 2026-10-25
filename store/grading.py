"""HIGH certainty only with a named basis, per assertion (Sprint 11
retrospective I3, built in Sprint 12 Task G, F105).

Until Sprint 12 each reading script kept its own `HIGH_REVIEWED` set of ids
the coordinator had read and judged HIGH, with no reason per id: a later
reader could not tell why one empirical-looking value was HIGH and its
neighbor LOW. The store's GRADE mapping (sprint10_f89_reading.py,
sprint11_reading.py) starts HIGH only for what a paper itself settles: its
own setup, its own scope, a definition, a result it proves, or a limit it
states. A HIGH grade now names which, and why, and this module refuses any
other basis.

    HIGH = high_grades({
        "some-assertion-id": ("proved result", "Theorem 2, p.6, read in context"),
    })
    certainty, reason = grade("some-assertion-id", HIGH, otherwise=("low", "Started LOW: ..."))

`store/write_path.py` requires new reading scripts to grade through this
module.

A LOW names its reason too (Sprint 12 retrospective I2, built in Sprint 13
Task F, F112). Until then a reader's kind "shown" took "an empirical result"
by default, so a theorem kept LOW stored the reason of a measurement (the
fresh-eyes review of 6c6f0ac found 8 in Sprint 12's reads). The coordinator
picks the reason; `theory_words` is the guard a reading script's test runs
over every "measured result", never the grader.

    certainty, reason = low_grade("theoretical result", "Theorem 2, not checked by the coordinator")
"""
from __future__ import annotations

import re
from dataclasses import dataclass

BASES = ("setup", "scope", "definition", "proved result", "stated limit")

# Each LOW reason, by name. The texts are the ones the store already holds
# (sprint12_reading.py's EMPIRICAL, AUTHOR_CLAIM, CITED and FIELD), so a
# script moved onto this module writes nothing new.
LOW_BASES = {
    "measured result": "an empirical result from one study",
    "authors' claim": "the authors' own claim, not tested in the paper",
    "cited claim": "a claim the source cites from other work, not tested in it",
    "field statement": "a statement about the field, its devices or its literature, not about the paper's own work",
    "theoretical result": "a theoretical result (proof, derivation or proposition)",
}
# A theoretical result kept LOW says why it was not upgraded: what was not
# checked, or what the value leaves out.
LOW_NEEDS_WHY = {"theoretical result"}

# Words in a value or its quotes that say a result was proved, derived or
# counted analytically. "Proof of principle" and "proof of concept" are runs.
_THEORY = re.compile(r"\b(theorems?|lemmas?|propositions?|corollar(?:y|ies)|we prove|proved|proves|provably|proofs?"
                     r"|derived?|derivation|asymptotic(?:ally)?|(?:gate|time|query|sample) complexity|O\()", re.I)
_RUN = re.compile(r"\bproofs?[- ]of[- ](?:principle|concept)", re.I)


@dataclass(frozen=True)
class HighBasis:
    basis: str
    why: str

    def reason(self) -> str:
        return f"Started HIGH: the paper's own {self.basis} ({self.why}), read in context by the coordinator"


def high_grades(reviewed: dict[str, tuple[str, str]]) -> dict[str, HighBasis]:
    """The coordinator's HIGH grades, each with its basis and why; refuses
    a basis outside BASES or an empty why."""
    out = {}
    for aid, (basis, why) in reviewed.items():
        if basis not in BASES:
            raise ValueError(f"{aid}: HIGH basis {basis!r} is not one of {', '.join(BASES)}")
        if not why.strip():
            raise ValueError(f"{aid}: a HIGH grade names why its basis holds")
        out[aid] = HighBasis(basis, why.strip())
    return out


def grade(aid: str, high: dict[str, HighBasis], otherwise: tuple[str, str]) -> tuple[str, str]:
    """(certainty, certainty_reasons): HIGH with its basis when the
    coordinator named one for `aid`, else `otherwise`. A HIGH passed as
    `otherwise` is refused, so HIGH has one door."""
    if otherwise[0] == "high":
        raise ValueError(f"{aid}: HIGH comes only from high_grades, with a basis")
    if aid in high:
        return "high", high[aid].reason()
    return otherwise


def low_grade(basis: str, why: str = "") -> tuple[str, str]:
    """("low", certainty_reasons) for a LOW with its named reason; refuses
    a reason outside LOW_BASES, and a theoretical result with no why."""
    if basis not in LOW_BASES:
        raise ValueError(f"LOW reason {basis!r} is not one of {', '.join(LOW_BASES)}")
    why = why.strip()
    if basis in LOW_NEEDS_WHY and not why:
        raise ValueError(f"a LOW {basis} names why it was not upgraded")
    return "low", f"Started LOW: {LOW_BASES[basis]}{': ' + why if why else ''}. NOT upgraded"


def theory_words(text: str) -> list[str]:
    """The words in `text` that say a result was proved, derived or counted
    analytically, after dropping "proof of principle" and "proof of
    concept". A reading script's test requires every "measured result"
    whose value or quotes hold one to be named by the coordinator."""
    return [m.group(0) for m in _THEORY.finditer(_RUN.sub(" ", text))]
