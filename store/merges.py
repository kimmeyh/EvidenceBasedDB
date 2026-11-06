"""Records merged into another record: one paper held as one record (F137, Sprint 16 Task E).

A record closed as a duplicate keeps its own history (its reads, applicability and found-via rows), but its
assertions are held by the record it was merged into. Every applier that re-enters an older read asks this module
which record holds a row, and never sets a merged record's tier back to read. `scripts/sprint16_f137_dunjko.py`
performed the one merge so far; docs/INTAKE_WORKFLOW.md section 71.
"""
from __future__ import annotations

MERGED_INTO: dict[str, str] = {
    "dunjko-2017-machine-learning-artificial-intelligence-quantum":
        "dunjko-2018-machine-learning-amp-artificial-intelligence",
}


def holder(rid: str) -> str:
    """The record that holds a paper's assertions: itself, or the record it was merged into."""
    return MERGED_INTO.get(rid, rid)


def promotes(rid: str, tier: str) -> bool:
    """A read sets a record's tier to read, except a duplicate closed by a merge, which stays closed."""
    return tier != "read" and rid not in MERGED_INTO
