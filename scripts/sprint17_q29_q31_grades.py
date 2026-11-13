#!/usr/bin/env python3
"""Sprint 17 Manual Validation, the two grades the fresh-eyes review of the q23 apply asked (INTAKE_WORKFLOW.md
section 76, findings M1 and M2). Team lead, 2026-11-10: "q30 a q31 a", where q30 = a confirmed that the earlier
"q20 b" meant q29 = b.

- q29 = b: albash-grover-local-condition-not-proof goes back to HIGH, "stated limit", as its two siblings from the
  same review are (albash-glued-trees-pagerank-caveats, albash-pagerank-average-case-numerical). q23 had made it LOW,
  "field statement"; the team lead chose the siblings' grade.
- q31 = a: chance-level-and-signature-control stays LOW, "authors' claim" (q30's answer b to the earlier question),
  and its reason says why: the fixed LOW reasons in `store.grading` cannot be reworded by a script.

Value and quotes are unchanged; the quote check runs again before the write, as every write requires.

    python scripts/sprint17_q29_q31_grades.py           # dry run: quotes checked, nothing written
    python scripts/sprint17_q29_q31_grades.py --apply   # verified backup first; a second apply writes nothing
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import high_grades, low_grade  # noqa: E402
from store.ingest import sync_verified_assertion  # noqa: E402
from store.quotes import require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, _ = script_paths(__file__)
_spec = importlib.util.spec_from_file_location("q23", ROOT / "scripts" / "sprint17_q23_corrections.py")
q23 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q23)

TODAY = "2026-11-10"
NOTE = (f"{TODAY} (Sprint 17 Manual Validation, q29 = b and q31 = a): grade decided by the team lead after the "
        "fresh-eyes review of the q23 apply (INTAKE_WORKFLOW.md section 76); scripts/sprint17_q29_q31_grades.py")
ALBASH = q23.ALBASH
PERE = q23.PERE
ALBASH_WHY = ("Section III.A.2, footnote 16, p.11: the review states that the square-root scaling reported by Roland "
              "and Cerf rests on a heuristic local adiabatic condition, is not a proof, and that the evidence for it "
              "is numerical; graded as the review's other stated limits are, by the team lead (q29 = b)")
PERE_WHY = "a limit the authors state on their own null result, kept LOW by the team lead (q31 = a)"
IDS = (ALBASH, PERE)


def wanted(conn, rid: str, texts: dict[str, str]):
    """The regraded assertion and the quote check that licenses its write."""
    a = q23.stored_assertion(conn, rid)
    pdf = q23.paper_pdf(conn, a.provenance)
    text = texts.setdefault(pdf, source_text(pdf))
    if rid == ALBASH:
        a.certainty, a.certainty_reasons = "high", high_grades({rid: ("stated limit", ALBASH_WHY)})[rid].reason()
    else:
        a.certainty, a.certainty_reasons = low_grade("authors' claim", PERE_WHY)
    return a, require_verbatim(rid, a.citation_context, text, value=a.value)


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    texts: dict[str, str] = {}
    with connect(DB_PATH) as conn:
        plan = [wanted(conn, rid, texts) for rid in IDS]  # every check before any write
    print(f"{len(plan)} assertions checked: every quote verbatim in its PDF")
    for a, _ in plan:
        print(f"{'sync' if apply else 'would sync'} {a.id}: {a.certainty}, {a.certainty_reasons}")
    if not apply:
        return 0
    backup_before_write(DB_PATH, "Sprint 17 q29 and q31 grades")
    with connect(DB_PATH) as conn:
        for a, verified in plan:
            changed = sync_verified_assertion(conn, a, verified, NOTE, TODAY)
            print(f"{a.id}: {', '.join(changed) if changed else 'already as wanted'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
