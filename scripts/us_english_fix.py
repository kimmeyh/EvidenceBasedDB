#!/usr/bin/env python3
"""Convert British spellings to US English in this repository's own LIVING
process/design markdown (Sprint 3 Task C, F13).

Ported from hsbc-quantum-fraud-2026's scripts/us_english_fix.py (read-only
source). CLAUDE.md, 2026-09-17: "this repository is written in US English."

THE FIRST ADAPTATION THAT IS NOT A COPY-PASTE: the sibling repository
excludes whole FILES (docs/paper/, docs/submission/, PREREGISTRATION.md)
because those are a frozen, already-SUBMITTED filing -- editing them after
the fact would falsify a document of record. This repository's own
equivalent frozen-record class is different in KIND but real: ADR-0004's
own standing rule is "revisions are recorded as dated amendments... never
as edits in place," and this repository's own sprint retrospective/
summary/plan docs are the same shape -- a point-in-time record of what
was decided or found, never rewritten after the fact. A first version of
this script (2026-09-18) shipped WITHOUT this exclusion and rewrote
"authorised" to "authorized" etc. inside ADR-0004/0005's own frozen
amendment sections and every sprint doc, before being caught during
Task C's own smoke test and reverted uncommitted. EXCLUDE_FILES below is
the fix: every ADR (frozen except its own dated-amendment append
mechanism, which this script must never perform automatically) and every
sprint plan/retrospective/summary doc.

THE SECOND ADAPTATION: text quoted or cited verbatim from a paper or book
keeps that source's own spelling wherever it appears (a `citation`
string, a direct quotation), same principle as the file-level exclusion
above but at SPAN granularity for content that lives inside an otherwise
in-scope file.

SCOPE DECISION (Sprint 3 Task C, resolving the question F13's own card
raised): `export/*.json` is NOT swept. ADR-0004 section 2: "the export is
generated, never hand-edited" -- a guard that rewrites generated output
would be immediately overwritten by the next `regenerate()` call and
would be testing the wrong layer. If a citation string in the export
carries a British spelling, that spelling came from the SOURCE data
(scripts/seed_set_metadata.json, the hand-authored dicts in
scripts/generate_seed_set_metadata.py and scripts/apply_paper_
applicability.py) -- but those sources hold citation TEXT copied verbatim
from real paper titles and author-written abstracts, which is exactly the
"verbatim quotation" case this script must NOT rewrite. Swept: this
repository's own LIVING tracked markdown only -- process docs, README,
CLAUDE.md, docs/research/* -- never frozen historical records.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / ".git").exists():
    raise SystemExit(f"not a git repository: {ROOT}")

# Frozen once written: every ADR (revisions land as a dated amendment
# APPENDED by a human/reviewed decision, never a mechanical sweep) and
# every sprint plan/retrospective/summary doc (a point-in-time record of
# what was decided or found). `docs/adr/README.md` and `docs/adr/
# template.md` are living PROCESS docs about how to write an ADR, not
# ADRs themselves, and stay in scope.
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

# British -> US. Same list as the sibling repository's own (read-only
# source), since the word-pair class does not depend on which repository
# is doing the writing.
PAIRS = [
    ("behaviour", "behavior"), ("behaviours", "behaviors"),
    ("colour", "color"), ("colours", "colors"),
    ("favour", "favor"), ("favours", "favors"), ("favoured", "favored"),
    ("favourable", "favorable"), ("favourite", "favorite"),
    ("labour", "labor"), ("neighbour", "neighbor"), ("neighbours", "neighbors"),
    ("honour", "honor"), ("honoured", "honored"),
    ("rumour", "rumor"),
    ("organise", "organize"), ("organised", "organized"),
    ("organising", "organizing"), ("organisation", "organization"),
    ("organisations", "organizations"),
    ("recognise", "recognize"), ("recognised", "recognized"),
    ("recognising", "recognizing"),
    ("realise", "realize"), ("realised", "realized"),
    ("minimise", "minimize"), ("minimised", "minimized"),
    ("maximise", "maximize"), ("maximised", "maximized"),
    ("optimise", "optimize"), ("optimised", "optimized"),
    ("optimising", "optimizing"), ("optimisation", "optimization"),
    ("optimiser", "optimizer"),
    ("emphasise", "emphasize"), ("emphasised", "emphasized"),
    ("prioritise", "prioritize"), ("prioritised", "prioritized"),
    ("prioritising", "prioritizing"),
    ("summarise", "summarize"), ("summarised", "summarized"),
    ("categorise", "categorize"), ("categorised", "categorized"),
    ("apologise", "apologize"),
    ("analyse", "analyze"), ("analysed", "analyzed"), ("analysing", "analyzing"),
    ("paralyse", "paralyze"),
    ("centre", "center"), ("centres", "centers"), ("centred", "centered"),
    ("metre", "meter"), ("metres", "meters"),
    ("theatre", "theater"),
    ("licence", "license"), ("licences", "licenses"),
    ("defence", "defense"), ("offence", "offense"), ("pretence", "pretense"),
    ("travelling", "traveling"), ("travelled", "traveled"),
    ("modelling", "modeling"), ("modelled", "modeled"),
    ("labelling", "labeling"), ("labelled", "labeled"),
    ("cancelled", "canceled"), ("cancelling", "canceling"),
    ("signalling", "signaling"), ("signalled", "signaled"),
    ("totalled", "totaled"), ("levelled", "leveled"),
    ("fuelled", "fueled"), ("marvelled", "marveled"),
    ("fulfil", "fulfill"), ("fulfilment", "fulfillment"),
    ("enrol", "enroll"), ("skilful", "skillful"), ("wilful", "willful"),
    ("grey", "gray"),
    ("aluminium", "aluminum"),
    ("programme", "program"), ("programmes", "programs"),
    ("whilst", "while"), ("amongst", "among"), ("towards", "toward"),
    ("learnt", "learned"), ("spelt", "spelled"), ("burnt", "burned"),
    ("dreamt", "dreamed"),
    ("judgement", "judgment"), ("judgements", "judgments"),
    ("acknowledgement", "acknowledgment"),
    ("acknowledgements", "acknowledgments"),
    ("ageing", "aging"),
    ("cheque", "check"), ("storey", "story"), ("tyre", "tire"),
    ("kerb", "curb"), ("plough", "plow"), ("draught", "draft"),
    ("sceptical", "skeptical"), ("sceptic", "skeptic"),
    ("sceptics", "skeptics"), ("scepticism", "skepticism"),
    ("manoeuvre", "maneuver"),
    ("artefact", "artifact"), ("artefacts", "artifacts"),
    ("generalise", "generalize"), ("generalised", "generalized"),
    ("generalising", "generalizing"),
    ("specialise", "specialize"), ("specialised", "specialized"),
    ("specialising", "specializing"),
    ("normalise", "normalize"), ("normalised", "normalized"),
    ("normalising", "normalizing"),
    ("utilise", "utilize"), ("utilised", "utilized"), ("utilising", "utilizing"),
    ("penalise", "penalize"), ("penalised", "penalized"),
    ("penalising", "penalizing"),
    ("characterise", "characterize"), ("characterised", "characterized"),
    ("characterising", "characterizing"),
    ("criticise", "criticize"), ("criticised", "criticized"),
    ("criticising", "criticizing"),
    ("memorise", "memorize"), ("memorised", "memorized"),
    ("memorising", "memorizing"),
    ("randomise", "randomize"), ("randomised", "randomized"),
    ("randomising", "randomizing"),
    ("standardise", "standardize"), ("standardised", "standardized"),
    ("standardising", "standardizing"),
    ("visualise", "visualize"), ("visualised", "visualized"),
    ("visualising", "visualizing"),
    ("practise", "practice"), ("practised", "practiced"),
    ("practising", "practicing"),
    ("flavour", "flavor"), ("flavours", "flavors"),
    ("rigour", "rigor"), ("vigour", "vigor"),
    ("endeavour", "endeavor"), ("saviour", "savior"),
    ("sizeable", "sizable"), ("moustache", "mustache"),
    ("mould", "mold"), ("smoulder", "smolder"),
]

# Spans that legitimately carry a non-US spelling because they are quoted
# or cited VERBATIM from a paper or book -- protected regardless of which
# file they appear in (team lead, 2026-09-17: "the exemption here is
# narrower and different in kind" than the sibling repo's frozen-file
# exclusion). Extend this list as real quotations are found; a paper
# title or abstract snippet containing British spelling is exactly the
# case this list exists for.
PROTECTED: tuple[str, ...] = ()

# An empty string in PROTECTED would silently disable the whole sweep:
# `"" in text` is always True, `text.replace("", token)` inserts a token
# between every character, every `\b` match dies, and unmasking restores
# the input byte-for-byte -- exit 0, nothing rewritten, no error (PR #20
# review, 2026-09-19). Fail at import instead.
if not all(PROTECTED):
    raise SystemExit("PROTECTED contains an empty span, which would disable every replacement")


def match_case(src: str, repl: str) -> str:
    if src.isupper():
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    files = []
    for rel in out.stdout.splitlines():
        if rel in EXCLUDE_FILES:
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        files.append(ROOT / rel)
    return files


def sweep(apply: bool) -> list[tuple[str, int]]:
    """Compute every replacement; write files only when `apply` is True.

    Dry-run is the DEFAULT (Sprint 3 retrospective improvement 1). The
    first run of this script, 2026-09-18, wrote straight to the live tree
    and rewrote frozen ADR amendments and sprint docs before the exclusion
    list existed; it was caught only because nothing was staged yet. A
    write-shaped one-off script shows its diff first and writes on an
    explicit flag -- docs/QUALITY_STANDARDS.md records the convention.
    """
    touched: list[tuple[str, int]] = []
    for path in tracked_markdown():
        text = path.read_text(encoding="utf-8")
        original = text

        masks: dict[str, str] = {}
        for i, span in enumerate(PROTECTED):
            token = f"\x00PROT{i}\x00"
            if span in text:
                masks[token] = span
                text = text.replace(span, token)

        count = 0
        for brit, us in PAIRS:
            pattern = re.compile(r"\b" + brit + r"\b", re.IGNORECASE)

            def sub(m: re.Match) -> str:
                nonlocal count
                count += 1
                return match_case(m.group(0), us)

            text = pattern.sub(sub, text)

        for token, span in masks.items():
            text = text.replace(token, span)

        if text != original:
            if apply:
                path.write_text(text, encoding="utf-8")
            touched.append((str(path.relative_to(ROOT)), count))
    return touched


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    apply = "--apply" in args
    touched = sweep(apply)
    total = sum(n for _, n in touched)
    for rel, n in sorted(touched, key=lambda x: -x[1]):
        print(f"{n:4d}  {rel}")
    verb = "applied" if apply else "PLANNED (dry run; re-run with --apply to write)"
    print(f"\n{total} replacements across {len(touched)} files -- {verb}")
    # Exit 0 even when a dry run has pending replacements: this script is a
    # converter, not the check. tests/test_us_english.py is the check, and
    # it is what fails CI when a British spelling lands in a living doc.
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
