"""Sprint 1 Task H (F1): guard against hsbc-quantum-fraud-2026 process
content re-entering this repository's own governing docs.

This repository was seeded from hsbc-quantum-fraud-2026 and, for a while,
its process docs (SPRINT_EXECUTION_WORKFLOW.md, SPRINT_STOPPING_CRITERIA.md,
QUALITY_STANDARDS.md, SPRINT_PLANNING.md, SPRINT_PROCESS.md,
SPRINT_RETROSPECTIVE.md, TESTING_STRATEGY.md, WINDOWS_POWERSHELL_GUIDE.md,
BACKLOG_REFINEMENT.md, and ADRs 0001-0003) described that repository's own
Dirac-3 hardware-approval process, its experiments/src test path, its
results.json/prereg-freeze artifacts, and its own submission calendar, as
though they were this repository's own live rules. Task H removed that
content (2026-09-16).

This test is NOT a blanket ban on the pattern strings -- accurate history
("this repository was seeded from hsbc-quantum-fraud-2026 on 2026-09-14")
is correct and expected in several places (CLAUDE.md, CHANGELOG.md,
README.md, docs/ALL_SPRINTS_MASTER_PLAN.md, the ADRs' own Amendments
sections, this file, and the sibling-repo-write-guard hook and its tests,
which correctly name the guarded repository). What it guards against is
these patterns reappearing in the GOVERNING PROCESS DOCS specifically,
where they would read as live instruction rather than history.

Verified by injection: temporarily adding "run pytest experiments/src -q"
to SPRINT_EXECUTION_WORKFLOW.md makes this test fail, naming the file and
line; removing it restores green.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The governing process docs Task H actually rewrote. A hit in one of
# these files is presumed to be live instruction unless the surrounding
# line is recognisably historical (see _is_allowed_context below).
GOVERNED_DOCS = [
    ROOT / "docs" / "SPRINT_EXECUTION_WORKFLOW.md",
    ROOT / "docs" / "SPRINT_STOPPING_CRITERIA.md",
    ROOT / "docs" / "QUALITY_STANDARDS.md",
    ROOT / "docs" / "SPRINT_PLANNING.md",
    ROOT / "docs" / "SPRINT_PROCESS.md",
    ROOT / "docs" / "SPRINT_RETROSPECTIVE.md",
    ROOT / "docs" / "TESTING_STRATEGY.md",
    ROOT / "docs" / "WINDOWS_POWERSHELL_GUIDE.md",
    ROOT / "docs" / "BACKLOG_REFINEMENT.md",
    ROOT / "docs" / "adr" / "0001-branch-and-carry-forward-model.md",
    ROOT / "docs" / "adr" / "0002-secrets-and-credential-handling.md",
    ROOT / "docs" / "adr" / "0003-store-and-schema-discipline.md",
]

# Patterns naming hsbc-quantum-fraud-2026 process/artifacts that have no
# equivalent in this repository. Deliberately narrower than a bare
# "hsbc" match, which would also flag the repository's own name in
# accurate provenance sentences ("seeded from hsbc-quantum-fraud-2026").
LEAKAGE_PATTERNS = [
    re.compile(r"Criterion H\b"),
    re.compile(r"experiments[/\\]src"),
    re.compile(r"prereg-freeze"),
    re.compile(r"\bresults\.json\b"),
    re.compile(r"[Mm]etered Dirac-3"),
    re.compile(r"QCi letter"),
    re.compile(r"IEEE-CIS|SPECTRA|QFE\b"),
    re.compile(r"frozen [Pp]reregistration"),
]

# A line containing one of these markers is presumed to be describing
# HISTORY (what was inherited, what changed, when) rather than live
# instruction, and is allowed even if it also matches a leakage pattern.
_HISTORY_MARKERS = re.compile(
    r"REWORKED|Amendment|AMENDMENT|seeded from|inherited (at|from)|"
    r"Task H|consumer repository|source repository|"
    r"was ported|converted from|no equivalent|does not (exist|apply)"
)


def _paragraphs(lines: list[str]) -> list[tuple[int, int]]:
    """(start_index, end_index) pairs, 0-based half-open, one per blank-line-
    delimited paragraph. A markdown paragraph -- including one that spans a
    bold lead-in and several wrapped lines, as every amendment note in this
    repository's ADRs does -- is the right unit for "is this the same
    thought as the nearby history marker", not an arbitrary fixed window."""
    paragraphs = []
    start = None
    for i, line in enumerate(lines):
        if line.strip():
            if start is None:
                start = i
        else:
            if start is not None:
                paragraphs.append((start, i))
                start = None
    if start is not None:
        paragraphs.append((start, len(lines)))
    return paragraphs


def _scan(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    violations = []
    for start, end in _paragraphs(lines):
        paragraph_text = "\n".join(lines[start:end])
        if _HISTORY_MARKERS.search(paragraph_text):
            continue
        for lineno in range(start, end):
            line = lines[lineno]
            for pattern in LEAKAGE_PATTERNS:
                if pattern.search(line):
                    violations.append(f"{path.relative_to(ROOT)}:{lineno + 1}: {line.strip()[:120]}")
    return violations


@pytest.mark.parametrize("doc", GOVERNED_DOCS, ids=lambda p: p.name)
def test_governing_doc_has_no_unmarked_source_repository_leakage(doc):
    if not doc.exists():
        pytest.skip(f"{doc} does not exist")
    violations = _scan(doc)
    assert not violations, (
        "hsbc-quantum-fraud-2026 process content found presented as this "
        f"repository's own live rule, with no history marker nearby: {violations}. "
        "If this is genuine history, add one of the recognised markers "
        "(REWORKED, Amendment, 'seeded from', 'Task H', 'no equivalent', "
        "'does not exist/apply', etc.) to the line. If it is live "
        "instruction, it does not belong in this repository."
    )
