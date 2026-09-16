"""Determinate-fact resolvers (Sprint 1 Task G).

CLAUDE.md standing rule: "Determinate facts are COMPUTED, never stored. If
a command or an artifact can answer it, the database holds a resolver, not
a copy." ADR-0004's own motivating evidence names the amendment count
specifically: A19 records that "the amendment count changed and had to be
corrected in every document that named it." Storing it as a value in this
store would reproduce the exact defect this system exists against --
resolving it live from the consumer repository's own amendment log is the
alternative.

READ-ONLY. Per CLAUDE.md's 2026-09-15 standing rule, this repository's
sessions may read hsbc-quantum-fraud-2026 but never write to it; every
function here only reads files under that repository, never writes.
"""
from __future__ import annotations

import re
from pathlib import Path

CONSUMER_REPO_PREREGISTRATION = Path(
    r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\experiments\PREREGISTRATION.md"
)

# Matches the amendment log's actual line format, e.g.
# "- 2026-08-30 (A1): Freeze recorded. ..." -- verified against the live
# file rather than assumed, since an earlier guess at the format
# ("**A#**") matched zero lines against the real document.
_AMENDMENT_LINE = re.compile(r"^- \d{4}-\d{2}-\d{2} \(A\d+\):", re.MULTILINE)


def consumer_amendment_count(path: Path = CONSUMER_REPO_PREREGISTRATION) -> int:
    """Count the amendment log entries in the consumer repository's frozen
    preregistration, computed live from the document rather than stored.

    Raises FileNotFoundError if the consumer repository is not present on
    this machine (e.g. a fresh clone of EvidenceBasedDB elsewhere) --
    callers that need a value regardless should catch this and report the
    resolver as unavailable, never substitute a remembered number.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. This resolver reads the consumer repository "
            "live and does not cache a fallback value -- a remembered "
            "number is exactly the defect (A19) this resolver exists to "
            "avoid reproducing."
        )
    text = path.read_text(encoding="utf-8")
    return len(_AMENDMENT_LINE.findall(text))
