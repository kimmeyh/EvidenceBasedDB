#!/usr/bin/env python3
"""Sprint 6 Manual Validation follow-up (team lead, 2026-10-05): the hsbc
repository's Dirac-3 runs as evidence on Dirac-3's raw solution quality.

Team lead: "I think we can look at the hsbc repo for answers to this
question as I believe it is settled by the Dirac-3 runs in the repo. Find
and add as evidence as needed."

Enters ONE source record, the hsbc Phase 1 results memo pinned at commit
203881e (read-only from this repository), and the TWO assertions it yields
on this question, quoted from its "What the evidence says" section:
1. on the Phase 1 formulation, Dirac-3 matched the exact classical optimum
   within measurement error;
2. that formulation cannot test hard problems: it is strictly convex and
   nearly degenerate, so any solver reproduces it.
Neither source sentence mentions error correction; the assertions state
what was measured, nothing more.

DRY-RUN BY DEFAULT. `--apply` takes a verified backup first.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, insert_assertion, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-05"
TAG = "Sprint 6 Manual Validation follow-up"
MEMO = "hsbc-quantum-fraud-2026-results-memo-phase-1"
SIBLING = "D:\\Data\\Harold\\github\\" + "hsbc-quantum-fraud-2026"  # read-only

SOURCE = {
    "id": MEMO, "kind": "reference",
    "access": SIBLING + "\\docs\\RESULTS_MEMO.md",
    "title": "Phase 1 results memo",
    "citation": ("hsbc-quantum-fraud-2026, \"Phase 1 results memo,\" docs/RESULTS_MEMO.md, commit 203881e, 2026-09-03 "
                 "(hand-transcribed from the document's title and the repository's git log)"),
    "transcribed_from": "the document's title and the repository's git log",
    "context": "hsbc-2026", "tier": "read",
    "disposition": ("Reference: the HSBC submission's Phase 1 results memo: baselines, Dirac-3 solver fidelity against "
                    "the exact classical proxy, and the preregistered null"),
    "evidence": ("A living document: this record cites commit 203881e (2026-09-03), and the working copy matched it on "
                 "2026-10-05. docs/QCI_EQC_MODELS_FEEDBACK.md (149dbfd) restates the same measurement; it is the same "
                 "evidence, not a second source. Read-only from this repository."),
    "checked_against_source": ("2026-10-05, Claude, read 'What the evidence says (plain terms)' (lines 50 to 62) "
                               "at commit 203881e directly"),
    "reads": [["Claude", "2026-10-05", "partial", "'What the evidence says (plain terms)', lines 50 to 62 (203881e)"]],
    "applicability": [
        ["hsbc-2026", "The submission's own Phase 1 measured results -- 'What the evidence says' section"],
        ["platform:dirac-3", "Dirac-3 hardware against the exact classical solve of the same Hamiltonian -- "
                             "'What the evidence says' section, solver fidelity bullet"]],
    "found_via": "team lead, Sprint 6 Manual Validation, 2026-10-05 (the Dirac-3 error-correction question)",
}

REASON = f"{TODAY} ({TAG}): extracted from the hsbc results memo at 203881e, read directly; team lead's request"
ASSERTIONS = [
    AssertionRecord(
        id="dirac3-matches-exact-optimum-on-convex-cvqboost",
        value=("On the HSBC Phase 1 CVQBoost formulation, Dirac-3 hardware minus the exact classical solve of the "
               "identical Hamiltonian was -0.0010 AUPRC (CI -0.0032 to +0.0012, inside the minimum detectable "
               "effect), with weight cosine 0.975 to 0.999; the hardware objective was always above the exact "
               "minimum, by 0.013 to 0.413 percent"),
        provenance=f"{MEMO}, 'What the evidence says (plain terms)', solver fidelity bullet",
        evidence_tag="HW", context="platform:dirac-3",
        citation_context=('"Dirac-3 minus its exact classical proxy on identical Hamiltonians = -0.0010 AUPRC '
                          '[CI -0.0032, +0.0012], inside the MDE; weight cosine 0.975-0.999; hardware objective always '
                          'above (worse than) the exact minimum by 0.013% to 0.413%." (markdown bold dropped)'),
        certainty="high",
        certainty_reasons=("Started HIGH: the project's own hardware measurement against an exact solve of the same "
                           "Hamiltonian, with a confidence interval. NOT generalized: one formulation, which the same "
                           "source calls nearly degenerate (see dirac3-fidelity-test-is-near-trivial-on-convex-formulation)"),
        fidelity="scoped", derivation="extracted", claim_type="positive",
        updated=TODAY, updated_reason=REASON),
    AssertionRecord(
        id="dirac3-fidelity-test-is-near-trivial-on-convex-formulation",
        value=("The Phase 1 match does not test Dirac-3 on hard problems: the formulation is strictly convex on the "
               "simplex and nearly degenerate (uniform weights even at lambda = 0), so any solver reproduces its "
               "optimum; the non-convex formulation, where no exact classical proxy exists, was not run in Phase 1"),
        provenance=f"{MEMO}, 'What the evidence says (plain terms)', 'Why fidelity is near-trivial here'",
        evidence_tag="PROJ", context="platform:dirac-3",
        citation_context=('"on this formulation the optimization problem itself is nearly degenerate, which is why any '
                          'solver reproduces it, and why the interesting Phase 2 direction is a non-convex formulation" '
                          '(line 58)'),
        certainty="high",
        certainty_reasons=("Started HIGH: a property of the objective (strict convexity on the simplex), plus a "
                           "zero-cost proxy sweep over eight lambda values that the source reports. NOT downgraded"),
        fidelity="scoped", derivation="extracted", claim_type="positive",
        updated=TODAY, updated_reason=REASON),
]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "sprint6 MV dirac3 fidelity")
    conn = connect(DB_PATH)
    try:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (MEMO,)).fetchone():
            print(f"{MEMO} already present; nothing to do")
            return 0
        record = intake.build_record(SOURCE, today=TODAY)
        print(f"{'WRITE' if apply else 'PLAN '} {record.id} (tier {record.tier}, reads {record.reads})")
        for a in ASSERTIONS:
            print(f"{'WRITE' if apply else 'PLAN '} {a.id} <- {MEMO} [{a.certainty}]")
        if apply:
            insert_paper(conn, record)
            for a in ASSERTIONS:
                insert_assertion(conn, a, yielded_by=MEMO)
            conn.commit()
            print("APPLIED")
        else:
            print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
