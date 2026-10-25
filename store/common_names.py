"""The common name, in parentheses, after a source's own spelling of a term
in an assertion's value (Sprint 13 Manual Validation Q4).

Team lead, 2026-10-25: "keep how the paper does them and then put in
parenthasses the more common name for them so that we can query the
database and still find all occurances of R2, R squared". A value keeps the
paper's spelling ("R2", as the text layer prints R with a superscript 2)
and gains the common name after it, so a search for either finds it.
Quotes are never touched: they stay verbatim.

A bare "R2" is also a label ("rule R2", "research R2", "R1, R2, R4", "R2:",
"Cloudflare R2", "Table R2"), and a label glossed as R squared would be a
false statement. "R^2" and "R²" also name the real plane. So these gain the
name only when the statistic is next to them: a number reached through
connecting words only ("R2 of 0.93", "R2 above 0.8", "R2: 0.93"), a
statistic noun after them ("R2 score", "R2 values"), or a statistic word
before them ("predictive R2", "pooled R2", "by R2"); and never next to a
label marker. The other spellings ("R-squared", "R2-score", "R2_score",
"R2adj", "coefficient of determination") are never labels, and always gain
it. The name goes after the whole token ("R^2_adj (R squared)", "$R^2$ (R
squared)"), never inside it, so the paper's token stays searchable.

`store.ingest` applies `with_common_names` to every value it writes, so a
reading script needs nothing of its own, and a second apply writes nothing.
"""
from __future__ import annotations

import re

_GLOSSED = r"\s*(?:\(R squared\)\s*)?"
# A number reached from the spelling through connecting words only.
_NUMBER_AFTER = re.compile(
    _GLOSSED + r"(?:(?:of|is|was|were|=|:|≈|~|>|<|≥|≤|above|below|over|under|exceed\w*|reach\w*|"
    r"(?:fell|falls?|drops?|dropped|rose|rises?|improved|increased|decreased)(?: from| to)?|"
    r"approximately|about|around|near|only|just|from|to)\s*)*[-+−]?\d", re.IGNORECASE)
_NOUN_AFTER = re.compile(_GLOSSED + r"(?:values?|scores?|statistics?|coefficients?)\b", re.IGNORECASE)
_WORD_BEFORE = re.compile(
    r"(?:\b(?:predictive|adjusted|saturated|pooled|base|test|train|training|validation|out-of-sample|negative|"
    r"positive|mean|average|median|best|worst|high|low|higher|lower|reached|exceeded|achieved|by)|%\s+in)\s+$",
    re.IGNORECASE)
# A spelling next to one of these is a label, never the statistic.
_LABEL_BEFORE = re.compile(
    r"(?:\b(?:rule|research|requirement|criterion|hypothesis|question|item|step|case|scenario|table|row|column|"
    r"figure|section|node|round|region|run|experiment|bucket|register|cloudflare|lemma|theorem|assumption)|"
    r"R\d+\s*,|R\d+\s+(?:and|or))\s*$", re.IGNORECASE)
_LABEL_AFTER = re.compile(r"^(?:\s*,\s*R\d|\s+(?:and|or)\s+R\d|\s*[-+]\s*R\d)")


def _is_statistic(value: str, m: re.Match) -> bool:
    before, after = value[:m.start()], value[m.end():]
    if _LABEL_BEFORE.search(before) or _LABEL_AFTER.match(after):
        return False
    return bool(_NUMBER_AFTER.match(after) or _NOUN_AFTER.match(after) or _WORD_BEFORE.search(before))


_SQUARED = r"(?:2|\^\{?2\}?|²)"
# (the source's spelling, the common name, the test a match must pass, or None).
# Each pattern skips a spelling that already has its common name after it, so the
# function is idempotent.
COMMON_NAMES = (
    # bare: also a label or the real plane, so the context decides
    (re.compile(rf"(?<![\w^$])\$?R{_SQUARED}\$?(?![\w^²{{}}$-])"), "R squared", _is_statistic),
    (re.compile(rf"(?<![\w^$])\$?R{_SQUARED}(?:[-_]?(?:adj(?:usted)?|scores?))\$?(?![\w-])"), "R squared", None),
    (re.compile(r"(?<![\w-])r2_score\b", re.IGNORECASE), "R squared", None),
    (re.compile(r"(?<![\w-])R-squared?\b(?!-)", re.IGNORECASE), "R squared", None),
    (re.compile(r"\bcoefficient of determination\b", re.IGNORECASE), "R squared", None),
    (re.compile(r"\bD(?:2|²)[- ]sampling\b(?!-)"), "D squared sampling", None),  # k-means++ seeding
)


def _unglossed(pattern: re.Pattern, common: str) -> re.Pattern:
    return re.compile(pattern.pattern + rf"(?! ?\({re.escape(common)}\))", pattern.flags)


def bare(value: str) -> list[str]:
    """The paper spellings in `value` that should carry a common name and do not."""
    found = []
    for pattern, common, test in COMMON_NAMES:
        for m in _unglossed(pattern, common).finditer(value):
            if test is None or test(value, m):
                found.append(m.group(0))
    return found


def with_common_names(value: str) -> str:
    for pattern, common, test in COMMON_NAMES:
        value = _unglossed(pattern, common).sub(
            lambda m: m.group(0) + f" ({common})" if test is None or test(m.string, m) else m.group(0), value)
    return value
