#!/usr/bin/env python3
"""Sprint 10 Task H (F83): primary sources for per-instance optimization bounds.

The ceilings answer document (`docs/research/ceilings-ml-and-optimization.md`,
section 5 point 5) stated the standard per-instance certificate (a bound
from a relaxation or a dual, and the gap an exact solver reports) as
general practice with no source in the store. Two free primary sources:

- Boyd and Vandenberghe, Convex Optimization (Cambridge University Press,
  2004), from the authors' own free copy (web.stanford.edu/~boyd/cvxbook),
  chapter 5: weak duality (section 5.2.2), the dual bound for the nonconvex
  two-way partitioning problem (section 5.1.5 and 5.2.2), and the duality
  gap as a certificate of suboptimality (section 5.5.1). Read by the
  coordinator on 2026-10-18: those sections in full; the rest of the book
  not read.
- Gurobi's Optimizer Reference Manual 13.0, parameter MIPGap: the gap a
  commercial exact solver reports and stops on. Read 2026-10-18: the
  MIPGap entry in full.

Certainty: a result proved in a standard textbook, read in context, and a
product's own definition of its own parameter, both start HIGH and are
not graded down (DOC_FACT in Sprint 9's GRADE mapping). Context `world`:
mathematics and a definition, true independent of any platform.

Every quote is checked by `tests/test_f83_optimization_bounds.py` against
the local copies. DRY-RUN BY DEFAULT; `--apply` takes a verified backup
first. Idempotent; a re-apply syncs every assertion field.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, insert_assertion, insert_paper, sync_assertion  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-18"
TAG = "Sprint 10 Task H, F83"

BOYD = "boyd-2004-convex-optimization"
BOYD_PDF = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers\2004_Boyd-Vandenberghe_Convex-Optimization.pdf")
BOYD_SHA = "40d976c83c18cce1900eff8c41bd5ad408c102b813af39d05ff85678ccf8d76e"
BOYD_URL = "https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf"
GUROBI = "gurobi-13-0-parameter-reference-mipgap"
GUROBI_HTML = Path(r"D:\Data\Harold\EvidenceBasedDB\References\Gurobi\2026-10-18_Gurobi_Optimizer-Reference-Parameters.html")
GUROBI_SHA = "09226fe902d92d79e4f1309cf01bbcbf54cb9f5fa4972a49ea03df2e95378749"
GUROBI_URL = "https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html"

SOURCES = [
    {
        "id": BOYD, "kind": "book", "context": "world", "tier": "read",
        "title": "Convex Optimization",
        "citation": ("S. Boyd and L. Vandenberghe, Convex Optimization. Cambridge, UK: Cambridge University Press, "
                     "2004, ISBN 978-0-521-83378-3 (hand-transcribed from the title and copyright pages of the "
                     "authors' free copy)"),
        "transcribed_from": "the title page (\"Convex Optimization\", Stephen Boyd, Lieven Vandenberghe) and the "
                            "copyright page (\"Cambridge University Press 2004\", ISBN 978-0-521-83378-3)",
        "disposition": ("Book: the standard convex optimization text; chapter 5 (duality) gives the per-instance "
                        "lower bound and certificate of suboptimality the ceilings answer document needed (F83)"),
        "access": f"{BOYD_PDF} | {BOYD_URL}",
        "evidence": (f"Local copy SHA-256 {BOYD_SHA}, 6,881,335 bytes, 714 pages, downloaded {TODAY} from the "
                     f"authors' own free copy at {BOYD_URL}; its copyright page reads \"First published 2004 Seventh "
                     "printing with corrections 2009\""),
        "found_via": "Sprint 10 Task H (F83): a primary source for the duality bound in the ceilings answer document",
        "cited_as": "Boyd and Vandenberghe, Convex Optimization, 2004",
        "checked_against_source": f"{TODAY}, Claude, read sections 5.1.5, 5.2.2 and 5.5.1 in the local copy",
        "reads": [["Claude", TODAY, "partial",
                   "sections 5.1.5 (two-way partitioning), 5.2.2 (weak duality) and 5.5.1 (certificate of "
                   "suboptimality) in full; the rest of the book not read"]],
        "applicability": [["world", "Lagrange duality: lower bounds on the optimal value of any problem, convex or "
                                    "not, and the duality gap as a certificate -- chapter 5"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint10_f83_optimization_bounds.py ({TAG}); read in part",
    },
    {
        "id": GUROBI, "kind": "reference", "context": "world", "tier": "read",
        "title": "Parameter Reference - Gurobi Optimizer Reference Manual (13.0)",
        "citation": ('Gurobi Optimization, "Parameter Reference," Gurobi Optimizer Reference Manual, version 13.0, '
                     f"{GUROBI_URL}, accessed {TODAY} (hand-transcribed from the page title and its version label)"),
        "transcribed_from": "the page title \"Parameter Reference - Gurobi Optimizer Reference Manual\" and the "
                            "manual's version label 13.0",
        "disposition": ("Reference: Gurobi's own definition of the relative MIP optimality gap its exact solver "
                        "reports and stops on (parameter MIPGap)"),
        "access": f"{GUROBI_HTML} | {GUROBI_URL}",
        "evidence": (f"Local copy SHA-256 {GUROBI_SHA}, saved {TODAY} from {GUROBI_URL} (the 'current' manual, "
                     "version 13.0 that day); a living page, so the local copy is the record of what was read"),
        "found_via": "Sprint 10 Task H (F83): a solver's own definition of its reported gap",
        "cited_as": "Gurobi Optimizer Reference Manual 13.0, MIPGap",
        "checked_against_source": f"{TODAY}, Claude, read the MIPGap entry in full in the local copy",
        "reads": [["Claude", TODAY, "partial", "the MIPGap entry in full; the other parameters not read"]],
        "applicability": [["world", "How an exact MIP solver states the gap between its incumbent and its proven "
                                    "bound -- the MIPGap entry"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint10_f83_optimization_bounds.py ({TAG}); read in part",
    },
]

THEOREM = "Started HIGH: a result proved in a standard textbook, read in context"
DEFINITION = ("Started HIGH: the product's own documentation defining its own parameter, read in context. A "
              "definition, not a performance claim, so not graded down")
REASON = f"{TODAY} ({TAG}): extracted, read directly by the coordinator"


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", "world")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    kw.setdefault("certainty_reasons", THEOREM)
    return AssertionRecord(**kw)


ASSERTIONS: list[tuple[AssertionRecord, str]] = [
    (A(id="weak-duality-lower-bound-holds-without-convexity",
       value=("The optimal value of the Lagrange dual problem is a lower bound on the optimal value of the original "
              "(primal) minimization problem, even when that problem is not convex (weak duality); since the dual "
              "problem is always convex, it can sometimes give a lower bound for a problem that is difficult to "
              "solve. The optimal duality gap, primal optimum minus dual optimum, is never negative"),
       provenance=f"{BOYD}, section 5.2.2, pp. 225-226",
       citation_context=('"which holds even if the original problem is not convex. This property is called weak '
                         'duality." (section 5.2.2, p. 225); "The bound (5.23) can sometimes be used to find a lower '
                         'bound on the optimal value of a problem that is difficult to solve, since the dual problem '
                         'is always convex" (section 5.2.2, p. 226); "The optimal duality gap is always nonnegative." '
                         '(section 5.2.2, p. 226)')), BOYD),
    (A(id="two-way-partitioning-dual-sdp-lower-bound",
       value=("For the two-way partitioning problem (minimize x^T W x with every x_i equal to 1 or -1; nonconvex, and "
              "very difficult to solve beyond about 50 variables), the Lagrange dual gives lower bounds on the "
              "optimal value: a simple one is n times the smallest eigenvalue of W, and the best Lagrange dual "
              "bound is the optimal value of a semidefinite program (SDP) that can be solved efficiently even for "
              "n around 1000, and is always at least as good as the simple one"),
       provenance=f"{BOYD}, section 5.1.5 (pp. 219-220) and section 5.2.2 (p. 226)",
       citation_context=('"In general (and for n larger than, say, 50) the problem (5.7) is very difficult to '
                         'solve." (section 5.1.5, p. 220); "This dual function provides lower bounds on the optimal '
                         'value of the difficult problem (5.7)." (section 5.1.5, p. 220); "This problem can be solved '
                         'efficiently, even for relatively large values of n, such as n = 1000. Its optimal value is '
                         'a lower bound on the optimal value of the two-way partitioning problem, and is always at '
                         'least as good as the lower bound (5.8)" (section 5.2.2, p. 226)')), BOYD),
    (A(id="duality-gap-certifies-suboptimality",
       value=("A primal feasible point and a dual feasible point together bound how far the primal point is from "
              "optimal without knowing the optimal value: the primal point is within the duality gap (its objective "
              "minus the dual objective) of the optimum, and the pair places the optimal value in an interval whose "
              "width is that gap; a zero gap proves both points optimal"),
       provenance=f"{BOYD}, section 5.5.1, p. 241",
       citation_context=('"Dual feasible points allow us to bound how suboptimal a given feasible point is, without '
                         'knowing the exact value of" (section 5.5.1, p. 241); "the width of which is the duality '
                         'gap." (section 5.5.1, p. 241)')), BOYD),
    (A(id="gurobi-mipgap-relative-gap-definition",
       value=("Gurobi's exact MIP solver reports a relative optimality gap |z_P - z_D| / |z_P|, where z_P is the "
              "incumbent objective (the upper bound when minimizing) and z_D the dual objective bound (the lower "
              "bound), and stops with an optimal result when the gap falls below the MIPGap parameter (default "
              "1e-4); when z_P and z_D have opposite signs the relative gap can rise after a new incumbent, even "
              "though the absolute gap fell (Gurobi 13.0)"),
       provenance=f"{GUROBI}, parameter MIPGap",
       citation_context=('"The MIP solver will terminate (with an optimal result) when the gap between the lower '
                         'and upper objective bound is less than MIPGap times the absolute value of the incumbent '
                         'objective value." (MIPGap); "the relative gap may increase after finding a new incumbent '
                         'solution, even though the absolute gap" (MIPGap)'),
       certainty_reasons=DEFINITION), GUROBI),
]


def apply_changes(conn) -> list[str]:
    log = []
    for src in SOURCES:
        if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (src["id"],)).fetchone() is None:
            insert_paper(conn, intake.build_record(src, today=TODAY))
            log.append(f"paper  {src['id']} [read]")
        else:
            log.append(f"exists {src['id']}")
    for a, src_id in ASSERTIONS:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_assertion(conn, a, yielded_by=src_id)
            log.append(f"assert {a.id} <- {src_id} [{a.certainty}]")
            continue
        changed = sync_assertion(conn, a, f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    for path, sha in ((BOYD_PDF, BOYD_SHA), (GUROBI_HTML, GUROBI_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            print(f"{path} differs from the copy read on {TODAY}")
            return 1
    if "--apply" not in args:
        for src in SOURCES:
            intake.build_record(src, today=TODAY)  # validates the entry; nothing written
            print(f"paper  {src['id']} [read]")
        for a, src_id in ASSERTIONS:
            print(f"assert {a.id} <- {src_id} [{a.certainty}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F83 optimization bounds sources")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
