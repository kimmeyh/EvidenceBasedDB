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
"""
from __future__ import annotations

from dataclasses import dataclass

BASES = ("setup", "scope", "definition", "proved result", "stated limit")


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
