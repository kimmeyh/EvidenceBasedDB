"""The common name, in parentheses, after a source's own spelling of a term
in an assertion's value (Sprint 13 Manual Validation Q4).

Team lead, 2026-10-25: "keep how the paper does them and then put in
parenthasses the more common name for them so that we can query the
database and still find all occurances of R2, R squared". A value keeps the
paper's spelling ("R2", as the text layer prints R with a superscript 2)
and gains the common name after it, so a search for either finds it.
Quotes are never touched: they stay verbatim.

A bare "R2" is also a label ("rule R2", "research R2", "R1, R2, R4", "R2:",
"Cloudflare R2", "Table R2", "S3 and R2"), and a label glossed as R squared
would be a false statement. "R^2" and "R²" also name the real plane ("in
R² 3 points", "R^2 is 2-dimensional"), but "in R²" alone cannot say so: "an
increase in R² of 0.05" is the statistic. So these gain the name only when the
statistic is next to them: a value reached through connecting words or a
short phrase ("R2 of 0.93", "R2 above .8", "R2 (0.93)", "the R2 of the
model was 0.9", "R2 and RMSE of 0.9 and 0.1"), a statistic noun or verb
after them ("R2 score", "R2 metric", "R2 improved"), or a statistic word
before them ("predictive R2", "pooled R2", "by R2"); and never next to a
label marker. The statistic has no unit, so a number followed by a unit or
a count ("3 qubits", "2-dimensional", "5 GB", "1st"), and a whole number
above 100 (a year), is not one. The other spellings ("R-squared", "R-sq",
"R2-score", "R2adj", "adjR2", "coefficient of determination") are never
labels, and always gain it. The name goes after the whole token ("R^2_adj
(R squared)", "$R^2$ (R squared)", "\\(R^2\\) (R squared)"), never inside
it, so the paper's token stays searchable. A spelling right after a gloss
("coefficient of determination (R squared) R2") gains no second one, and
code ("r2_score(y, yhat)") is left as written.

`store.ingest` applies `with_common_names` to every value it writes, so a
reading script needs nothing of its own, and a second apply writes nothing.
Review of 44e2512 (2026-10-26) found each case named above; each has a test.
"""
from __future__ import annotations

import re

_GLOSSED = r"\s*(?:\\\)|\$)?\s*(?:\(R squared\)\s*)?"
# Other metrics reported beside R2 ("R2 and RMSE of 0.9 and 0.1", "R2, RMSE and MAE were ...", "R2/RMSE of
# 0.9/0.1"). A list closes with "and" (or a slash): "In R2, accuracy was 0.9" is a label, not a list.
_METRIC = (r"(?:RMSE|MAE|MSE|MAPE|RMSD|accuracy|AUC|F1|Pearson'?s?(?: r)?|Spearman'?s?|correlation|bias|"
           r"error)")
_SIBLING_METRICS = rf"(?:(?:\s*,\s*{_METRIC})*\s*(?:and|&|/)\s*{_METRIC})?"
# A short phrase before the value ("of the model was", "for the test set was", "on test data of").
_PHRASE = r"(?:(?:of|for|on|in|across|over|with)\s+(?:[\w'-]+\s+){1,4}?(?:was|were|is|are|of|=|:)\s*)?"
_CONNECT = (r"(?:(?:of|is|was|were|are|=|:|≈|~|>|<|≥|≤|\(|above|below|over|under|between|equal(?:s| to)?|"
            r"exceed\w*|reach\w*|(?:fell|falls?|drops?|dropped|rose|rises?|improved|increased|decreased)"
            r"(?: from| to)?|approximately|about|around|near|only|just|from|to|values? of|scores? of)\s*)*")
_NUMBER = r"[-+−]?(?:\d+(?:\.\d+)?|\.\d+)"
# The statistic has no unit: a number followed by one of these is a count, a size, an order or a dimension.
_UNIT = re.compile(r"\s*(?:-\s*)?(?:st|nd|rd|th|[a-z]?b\b|ms\b|s\b|d\b|D\b|dimension\w*|dim\b|qubits?|points?|"
                   r"layers?|nodes?|times|fold|x\b|×|years?|days?|hours?|minutes?|seconds?|items?|samples?|"
                   r"features?|classes|bits?|gb|mb|kb|tb)", re.IGNORECASE)
_NUMBER_AFTER = re.compile(_GLOSSED + _SIBLING_METRICS + r"\s*" + _PHRASE + _CONNECT + f"({_NUMBER})",
                           re.IGNORECASE)
_NOUN_AFTER = re.compile(_GLOSSED + r"(?:values?|scores?|statistics?|coefficients?|metrics?|measures?)\b",
                         re.IGNORECASE)
_VERB_AFTER = re.compile(_GLOSSED + r"(?:improv|increas|decreas|drop|fell|rose|declin|degrad)\w*\b", re.IGNORECASE)
_WORD_BEFORE = re.compile(
    r"(?:\b(?:predictive|adjusted|saturated|pooled|base|test|train|training|validation|out-of-sample|negative|"
    r"positive|mean|average|median|best|worst|high|low|higher|lower|reached|exceeded|achieved|by)|%\s+in)\s+$",
    re.IGNORECASE)
# A spelling next to one of these is a label, never the statistic.
_LABEL_BEFORE = re.compile(
    r"(?:\b(?:rule|research|requirement|criterion|criteria|hypothes[ie]s|question|item|step|case|scenario|table|"
    r"row|column|figure|fig\.|section|subsection|appendix|panel|node|round|region|run|experiment|bucket|register|"
    r"cloudflare|lemma|theorem|assumption|constraint|condition|equation|eq\.|site|zone|server|storage|level|"
    r"layer|room|reaction|residue|reference)s?|[A-Z]\d+\s*[,;/]|[A-Z]\d+\s+(?:and|or|&))\s*$", re.IGNORECASE)
_LABEL_AFTER = re.compile(r"^(?:\s*[,;/]\s*[A-Z]\d|\s+(?:and|or|&)\s+[A-Z]\d|\s*[-+]\s*[A-Z]\d)")
_AFTER_GLOSS = re.compile(r"\(R squared\)\s*(?:\\\(|\$)?$")


def _is_statistic(value: str, m: re.Match) -> bool:
    before, after = value[:m.start()], value[m.end():]
    if _AFTER_GLOSS.search(before):
        return False
    if _LABEL_BEFORE.search(before) or _LABEL_AFTER.match(after):
        return False
    number = _NUMBER_AFTER.match(after)
    if number:
        figure = number.group(1).lstrip("+-−")
        rest = after[number.end():]
        if _UNIT.match(rest) or (re.fullmatch(r"\d+", figure) and int(figure) > 100):
            return False
        return True
    return bool(_NOUN_AFTER.match(after) or _VERB_AFTER.match(after) or _WORD_BEFORE.search(before))


_SQUARED = r"(?:2|\^\{?2\}?|²)"
_OPEN, _CLOSE = r"(?:\\\()?\$?", r"\$?(?:\\\))?"
# (the source's spelling, the common name, the test a match must pass, or None).
# Each pattern skips a spelling that already has its common name after it, so the
# function is idempotent. The named spellings run first, so a bare R2 right after
# their gloss is left alone.
COMMON_NAMES = (
    (re.compile(r"\bcoefficients? of determination\b", re.IGNORECASE), "R squared", None),
    (re.compile(r"(?<![\w-])R-(?:squared?|sq)\b(?!-)", re.IGNORECASE), "R squared", None),
    (re.compile(r"(?<![\w-])r2_score\b(?!\s*\()", re.IGNORECASE), "R squared", None),
    (re.compile(rf"(?<![\w^$\\]){_OPEN}adj(?:usted)?[-_ ]?R{_SQUARED}{_CLOSE}(?![\w^²{{}}$\\-])"), "R squared", None),
    (re.compile(rf"(?<![\w^$\\]){_OPEN}R{_SQUARED}(?:[-_]?(?:adj(?:usted)?|scores?))\b{_CLOSE}(?![\w(\\$-])"),
     "R squared", None),
    # bare: also a label or the real plane, so the context decides
    (re.compile(rf"(?<![\w^$\\]){_OPEN}R{_SQUARED}{_CLOSE}(?![\w^²{{}}$\\-])"), "R squared", _is_statistic),
    (re.compile(rf"\bD{_SQUARED}[- ]sampling(?:-[\w]+)*(?:'s)?(?![\w'-])"), "D squared sampling", None),  # k-means++
    # (each token is matched whole: the lookaheads stop a second pass from backtracking to a shorter one)
)


def _unglossed(pattern: re.Pattern, common: str) -> re.Pattern:
    return re.compile(pattern.pattern + rf"(?!\s*\({re.escape(common)}\))", pattern.flags)


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
