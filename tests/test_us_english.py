"""Tracked living markdown uses US English spellings (Sprint 3 Task C, F13).

CLAUDE.md, 2026-09-17: "this repository is written in US English."

WHAT IS DELIBERATELY EXEMPT, and the exemption matters more than the rule:

  - Every ADR (`docs/adr/0001-*.md` through `docs/adr/0005-*.md`):
    ADR-0004's own standing rule is "revisions are recorded as dated
    amendments... never as edits in place." A first version of
    scripts/us_english_fix.py (2026-09-18) shipped WITHOUT this exclusion
    and rewrote frozen amendment prose before being caught in Task C's
    own smoke test and reverted uncommitted -- this test's exclusion list
    exists so that mistake cannot recur silently.
  - Every sprint doc under `docs/sprints/` (plan, retrospective, summary):
    same reasoning -- a point-in-time record of what was decided or
    found, never rewritten after the fact.
  - `docs/adr/README.md` and `docs/adr/template.md` stay IN SCOPE: they
    are living process docs about how to write an ADR, not ADRs
    themselves.

`scripts/us_english_fix.py` applies the conversion this test enforces.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_PREFIXES = ("docs/sprints/",)
EXCLUDE_FILES = tuple(
    f"docs/adr/{n:04d}-{name}.md"
    for n, name in [
        (1, "branch-and-carry-forward-model"),
        (2, "secrets-and-credential-handling"),
        (3, "store-and-schema-discipline"),
        (4, "evidence-based-db"),
        (5, "reference-library"),
    ]
)

# Same list as scripts/us_english_fix.py; kept in sync manually since the
# two files' shared PAIRS list would otherwise be a THIRD place this exact
# word list is restated (CLAUDE.md's own "determinate facts are computed,
# never stored" caution against restating one value more than once).
BRITISH = (
    "behaviour", "behaviours", "colour", "colours", "favour", "favours",
    "favoured", "favourable", "favourite", "labour", "neighbour", "neighbours",
    "honour", "honoured", "rumour", "organise", "organised", "organising",
    "organisation", "organisations", "recognise", "recognised", "recognising",
    "realise", "realised", "minimise", "minimised", "maximise", "maximised",
    "optimise", "optimised", "optimising", "optimisation", "optimiser",
    "emphasise", "emphasised", "prioritise", "prioritised", "prioritising",
    "summarise", "summarised", "categorise", "categorised", "apologise",
    "analyse", "analysed", "analysing", "paralyse", "centre", "centres",
    "centred", "metre", "metres", "theatre", "licence", "licences",
    "defence", "offence", "pretence", "travelling", "travelled",
    "modelling", "modelled", "labelling", "labelled", "cancelled",
    "cancelling", "signalling", "signalled", "totalled", "levelled",
    "fuelled", "marvelled", "fulfil", "fulfilment", "enrol", "skilful",
    "wilful", "grey", "aluminium", "programme", "programmes", "whilst",
    "amongst", "towards", "learnt", "spelt", "burnt", "dreamt",
    "judgement", "judgements", "acknowledgement", "acknowledgements",
    "ageing", "cheque", "storey", "tyre", "kerb", "plough", "draught",
    "sceptical", "sceptic", "sceptics", "scepticism", "manoeuvre",
    "artefact", "artefacts", "generalise", "generalised", "generalising",
    "specialise", "specialised", "specialising", "normalise", "normalised",
    "normalising", "utilise", "utilised", "utilising", "penalise",
    "penalised", "penalising", "characterise", "characterised",
    "characterising", "criticise", "criticised", "criticising",
    "memorise", "memorised", "memorising", "randomise", "randomised",
    "randomising", "standardise", "standardised", "standardising",
    "visualise", "visualised", "visualising", "practise", "practised",
    "practising", "flavour", "flavours", "rigour", "vigour", "endeavour",
    "saviour", "sizeable", "moustache", "mould", "smoulder",
)

# Spans that legitimately carry a non-US spelling because they are quoted
# or cited VERBATIM from a paper or book. Extend as real quotations are
# found -- deliberately empty today since none has been found yet, and an
# empty tuple is not the same defect as an unmaintained one: it means "no
# exemption has been NEEDED", checked by the parametrized test below
# actually running against every tracked file.
PROTECTED: tuple[str, ...] = ()

PATTERN = re.compile(r"\b(" + "|".join(BRITISH) + r")\b", re.IGNORECASE)


def _tracked_markdown() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    files = []
    for rel in out.stdout.splitlines():
        if rel in EXCLUDE_FILES:
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        p = ROOT / rel
        if p.is_file():
            files.append(p)
    return files


FILES = _tracked_markdown()


def test_the_file_list_is_not_empty():
    """A guard with an empty population passes trivially -- if `git
    ls-files` fails, every parametrized case below vanishes and the suite
    stays green while checking nothing."""
    assert len(FILES) > 15, (
        f"expected a real population of tracked living markdown, found {len(FILES)}. "
        "The guard below would be vacuous.")


def test_the_frozen_documents_are_actually_excluded():
    """The exemption must hold, or a sweep could rewrite an ADR's frozen
    amendment or a sprint's own historical record.

    Checked against a HARDCODED prefix, not the module's own
    EXCLUDE_PREFIXES constant -- checking a broken exclusion list against
    itself can never fail (`str.startswith(())` is always False for an
    empty tuple), which is exactly the vacuous-guard shape this
    repository's own CLAUDE.md names as a recurring class. Caught by
    injection: emptying EXCLUDE_PREFIXES to `()` and re-running a version
    of this test that checked `r.startswith(EXCLUDE_PREFIXES)` still
    passed, silently, because the check and the break shared the same
    broken constant."""
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True)
    all_tracked = set(out.stdout.splitlines())
    rels = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES}
    for excluded in EXCLUDE_FILES:
        assert excluded in all_tracked, f"{excluded} no longer exists -- update EXCLUDE_FILES"
        assert excluded not in rels, f"{excluded} is in scope but must be excluded (frozen ADR)"
    leaked = [r for r in rels if r.startswith("docs/sprints/")]
    assert not leaked, f"sprint docs are in scope but must be excluded (frozen record): {leaked}"


def test_adr_readme_and_template_stay_in_scope():
    """The two non-ADR files under docs/adr/ are living process docs, not
    frozen decision records, and must NOT be swept into the exclusion by
    an over-broad prefix match on 'docs/adr/'."""
    rels = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES}
    assert "docs/adr/README.md" in rels
    assert "docs/adr/template.md" in rels


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_british_spellings(path: Path):
    text = path.read_text(encoding="utf-8")

    for span in PROTECTED:
        text = text.replace(span, " " * len(span))

    offenders = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in PATTERN.finditer(line):
            offenders.append(f"  line {lineno}: {m.group(0)!r} in {line.strip()[:70]!r}")

    assert not offenders, (
        f"{path.relative_to(ROOT)} uses British spellings; this repository "
        "writes US English (CLAUDE.md, 2026-09-17):\n"
        + "\n".join(offenders[:10])
        + "\n\nRun scripts/us_english_fix.py to convert.")
