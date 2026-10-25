"""The common name, in parentheses, after a source's own spelling of a term
in an assertion's value (Sprint 13 Manual Validation Q4).

Team lead, 2026-10-25: "keep how the paper does them and then put in
parenthasses the more common name for them so that we can query the
database and still find all occurances of R2, R squared". A value keeps the
paper's spelling ("R2", as the text layer prints R with a superscript 2)
and gains the common name after it, so a search for either finds it.
Quotes are never touched: they stay verbatim.

`store.ingest` applies `with_common_names` to every value it writes, so a
reading script needs nothing of its own, and a second apply writes nothing.
"""
from __future__ import annotations

import re

# (the source's spelling, the common name). Each pattern skips a spelling that
# already has its common name after it, so the function is idempotent.
COMMON_NAMES: tuple[tuple[str, str], ...] = (
    (r"\bR2\b(?!-)", "R squared"),  # the coefficient of determination; not "R2-" as in a model name
    (r"\bD2-sampling\b", "D squared sampling"),  # k-means++ seeding, sampling by squared distance
)


def with_common_names(value: str) -> str:
    for pattern, common in COMMON_NAMES:
        value = re.sub(pattern + rf"(?! \({re.escape(common)}\))", lambda m: f"{m.group(0)} ({common})", value)
    return value
