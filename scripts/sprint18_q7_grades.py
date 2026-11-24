#!/usr/bin/env python3
"""Sprint 18 Manual Validation q7 = a (team lead, 2026-11-22: "q4-q10 as recommended"): g361 (Boixo 2014) gives the
device temperature twice, 20 mK (Supp. III.B, p.9, and Methods, 0.4 GHz) and 17 mK (Supp. VII, p.22). A paper that
contradicts itself does not settle the figure, so both items are LOW, and each reason names the contradiction.

- dw1-temperature-20mk-p9: HIGH ("the paper's own setup") becomes LOW, "authors' claim", with the contradiction.
- dw1-temperature-17mk-p22: stays LOW, "authors' claim"; its reason now names the contradiction too.

Only certainty and certainty_reasons are decided; F147's `sync_decided_assertion` refuses any other changed field.
Value and quotes are unchanged; the quote check runs again before the write, as every write requires.

    python scripts/sprint18_q7_grades.py           # dry run: quotes checked, nothing written
    python scripts/sprint18_q7_grades.py --apply   # verified backup first; a second apply writes nothing
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import low_grade  # noqa: E402
from store.ingest import sync_decided_assertion  # noqa: E402
from store.quotes import require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, _ = script_paths(__file__)
_spec = importlib.util.spec_from_file_location("q23", ROOT / "scripts" / "sprint17_q23_corrections.py")
q23 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q23)

TODAY = "2026-11-22"
NOTE = (f"{TODAY} (Sprint 18 Manual Validation, q7 = a): the paper gives two device temperatures, so neither is "
        "HIGH (INTAKE_WORKFLOW.md section 81); scripts/sprint18_q7_grades.py")
T20 = "dw1-temperature-20mk-p9"
T17 = "dw1-temperature-17mk-p22"
IDS = (T20, T17)
WHY = {
    T20: ("the paper contradicts itself: Supp. III.B, p.9, and Methods give 20 mK (0.4 GHz), Supp. VII, p.22, gives "
          "17 mK (dw1-temperature-17mk-p22); a self-contradicting paper does not settle the figure (team lead, q7 = a)"),
    T17: ("the paper contradicts itself: Supp. VII, p.22, gives 17 mK, Supp. III.B, p.9, and Methods give 20 mK "
          "(dw1-temperature-20mk-p9); a self-contradicting paper does not settle the figure (team lead, q7 = a)"),
}
DECIDED = {"certainty", "certainty_reasons"}


def wanted(conn, rid: str, texts: dict[str, str]):
    """The regraded assertion and the quote check that licenses its write."""
    a = q23.stored_assertion(conn, rid)
    pdf = q23.paper_pdf(conn, a.provenance)
    text = texts.setdefault(pdf, source_text(pdf))
    a.certainty, a.certainty_reasons = low_grade("authors' claim", WHY[rid])
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
    backup_before_write(DB_PATH, "Sprint 18 q7 grades")
    with connect(DB_PATH) as conn:
        for a, verified in plan:
            changed = sync_decided_assertion(conn, a, verified, NOTE, TODAY, DECIDED)
            print(f"{a.id}: {', '.join(changed) if changed else 'already as wanted'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
