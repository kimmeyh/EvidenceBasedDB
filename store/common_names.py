"""The common name, in parentheses, after a source's own spelling of a term
in an assertion's value (Sprint 13 Manual Validation Q4).

Team lead, 2026-10-25: "keep how the paper does them and then put in
parenthasses the more common name for them so that we can query the
database and still find all occurances of R2, R squared". A value keeps the
paper's spelling ("R2", as the text layer prints R with a superscript 2)
and gains the common name after it, so a search for either finds it.
Quotes are never touched: they stay verbatim.

A bare "R2" is also a label ("rule R2", "research R2", "R1, R2, R4", "R2:"
in hsbc-qfraud-phase2's documents), and a label glossed as R squared would
be a false statement. So a bare R2 gains the name only when the words around
it speak of a statistic (a number, a comparison, "score", "value", "test"
and the like) and no label marker is next to it. The other spellings
("R-squared", "R^2", "R²", "R2-score") are never labels, and always gain it.

`store.ingest` applies `with_common_names` to every value it writes, so a
reading script needs nothing of its own, and a second apply writes nothing.
"""
from __future__ import annotations

import re

# Words near a bare R2 that mark it as the coefficient of determination.
_STATISTIC = re.compile(r"\d+\.\d+|\d+ ?%|[=<>≥≤]|score|value|fit|regression|predictive|test|train|exceed|above|"
                        r"below|saturat|coefficient|determination|pooled", re.IGNORECASE)
# A bare R2 next to one of these is a label, never the statistic.
_LABEL_BEFORE = re.compile(r"(?:rule|research|requirement|criterion|hypothesis|question|item|step|R\d+,)\s*$",
                           re.IGNORECASE)
_LABEL_AFTER = re.compile(r"^(?::|,\s*R\d)")
_WINDOW = 40


def _is_statistic(value: str, m: re.Match) -> bool:
    before, after = value[:m.start()], value[m.end():]
    if _LABEL_BEFORE.search(before) or _LABEL_AFTER.match(after):
        return False
    return bool(_STATISTIC.search(before[-_WINDOW:] + " " + after[:_WINDOW]))


# (the source's spelling, the common name, the test a match must pass, or None).
# Each pattern skips a spelling that already has its common name after it, so the
# function is idempotent.
COMMON_NAMES = (
    (r"\bR2\b(?![-^])", "R squared", _is_statistic),  # bare: also a label, so the context decides
    (r"\bR2-score\b", "R squared", None),
    (r"\bR-squared\b", "R squared", None),
    (r"\bR\^2(?!\d)", "R squared", None),
    (r"\bR²", "R squared", None),
    (r"\bD2-sampling\b(?!-)", "D squared sampling", None),  # k-means++ seeding, sampling by squared distance
)


def bare(value: str) -> list[str]:
    """The paper spellings in `value` that should carry a common name and do not."""
    found = []
    for pattern, common, test in COMMON_NAMES:
        for m in re.finditer(pattern + rf"(?! ?\({re.escape(common)}\))", value):
            if test is None or test(value, m):
                found.append(m.group(0))
    return found


def with_common_names(value: str) -> str:
    for pattern, common, test in COMMON_NAMES:
        value = re.sub(pattern + rf"(?! ?\({re.escape(common)}\))",
                       lambda m: m.group(0) + f" ({common})" if test is None or test(m.string, m) else m.group(0),
                       value)
    return value
