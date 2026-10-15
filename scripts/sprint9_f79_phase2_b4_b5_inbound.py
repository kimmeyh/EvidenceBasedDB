#!/usr/bin/env python3
"""Sprint 9 Task A (F79): the first Phase 2 result entered by the inbound path.

hsbc-qfraud-phase2's `docs/B4_B5_HARDWARE_RESULT.md` (B4: CVQBoost on the
SPECTRA cells; B5: QSVM on ULB; both run on Dirac-3 on 2026-10-06), read
directly on 2026-10-15 at Phase 2 commit 139fa13, the last commit touching
the file (identical at Phase 2's HEAD 07f44f3 that day). Team lead,
2026-10-14: the two repositories read each other freely and never write to
each other, so the source is read from Phase 2's own git history, never
copied into it or edited there.

The document corrects itself twice. Only the corrected material is
asserted: the "Proxy's edge" column is declared not like-for-like and is not
used; the in-pocket table is. The off-repository 2026-10-03 result the
document calls unverified is not imported.

Certainty as in the Phase 1 precedent
(`dirac3-matches-exact-optimum-on-convex-cvqboost`): the consumer project's
own hardware measurement, read directly, starts HIGH. Every quote is checked
by `tests/test_f79_phase2_inbound.py` against the file as stored at the
pinned commit. DRY-RUN BY DEFAULT; `--apply` takes a verified backup first.
Idempotent: an existing record or assertion is skipped.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, insert_assertion, insert_paper  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-15"
TAG = "Sprint 9 Task A, F79"
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit 139fa13, read directly on {TODAY}"

PHASE2 = r"D:\Data\Harold\github\hsbc-qfraud-phase2"
COMMIT = "139fa133265254521b24c0c425099796b425c558"
FILE = "docs/B4_B5_HARDWARE_RESULT.md"
# The file as stored at COMMIT; a different blob stops the script.
SHA256 = "28b98c3db1227bfdb0445d2cab6aaace299fab4ffb313e4349b1df70b035c90a"
REPO_URL = "https://github.com/kimmeyh/hsbc-qfraud-phase2"

SRC = "hsbc-qfraud-phase2-b4-b5-hardware-result"
PRIOR = "dirac3-matches-exact-optimum-on-convex-cvqboost"


def source_bytes() -> bytes:
    """The result document exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{FILE}"],
                          capture_output=True, check=True).stdout


def source_text() -> str:
    return source_bytes().decode("utf-8")


SOURCE = {
    "id": SRC, "kind": "reference", "context": "hsbc-2026", "tier": "read",
    "title": "B4 and B5 on Dirac-3: the result",
    "citation": ('hsbc-qfraud-phase2, "B4 and B5 on Dirac-3: the result," docs/B4_B5_HARDWARE_RESULT.md, commit '
                 "139fa13, 2026-10-07; run 2026-10-06, Sprint 21 (F90) (hand-transcribed from the document's title and "
                 "first line and the repository's git log)"),
    "transcribed_from": "the heading \"B4 and B5 on Dirac-3: the result\" and the line \"Run 2026-10-06 from 07:30 local, "
                        "Sprint 21 (F90)\"",
    "disposition": ("Reference: the HSBC Phase 2 project's own Dirac-3 hardware result: B4 (CVQBoost on two SPECTRA "
                    "cells, five seeds, against a matched random-segment control and the classical proxy) and B5 "
                    "(sign-augmented primal QSVM on ULB, 12 fits)"),
    "access": f"{PHASE2}\\docs\\B4_B5_HARDWARE_RESULT.md | {REPO_URL}/blob/{COMMIT}/{FILE}",
    "evidence": (f"A living document in an active repository: this record cites commit 139fa13 (2026-10-07), whose blob "
                 f"has SHA-256 {SHA256}; the working copy and Phase 2's HEAD 07f44f3 matched it on {TODAY}. The "
                 "figures are in Phase 2's experiments/results/results.json (blocks B4 and B5). The document's two "
                 "corrections stand inside it: its 'Proxy's edge' column is not like-for-like and is not used here; "
                 "its stored device samples were truncated, which it says affects no AUPRC figure. The private "
                 "repository's URL is the citation's pointer; the record depends on the commit. Read-only from this "
                 "repository (F79)."),
    "found_via": "team lead, 2026-10-15 (Sprint 9 plan Q9 = 1: Phase 2's B4 and B5 result as F79's inbound trial)",
    "cited_as": "docs/B4_B5_HARDWARE_RESULT.md",
    "checked_against_source": f"{TODAY}, Claude, read the whole document at commit 139fa13 via git show",
    "reads": [["Claude", TODAY, "full", "the whole document at commit 139fa13"]],
    "applicability": [
        ["hsbc-2026", "Phase 2's own hardware test of the CVQBoost replication and the QSVM arm -- the whole document"],
        ["platform:dirac-3", "Dirac-3 against its exact classical proxy inside the pocket, and B5's Hamiltonian "
                             "resolution -- the in-pocket table and the B5 section"],
    ],
    "updated_reason": f"{TODAY}: added by scripts/sprint9_f79_phase2_b4_b5_inbound.py ({TAG}); read in full",
}


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "HW")
    kw.setdefault("context", "platform:dirac-3")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    return AssertionRecord(**kw)


OWN = "Started HIGH: the consumer project's own hardware measurement, read directly at Phase 2 commit 139fa13"

ASSERTIONS: list[AssertionRecord] = [
    A(id="dirac3-matches-classical-proxy-in-pocket-spectra-b4",
      value=("On Phase 2's B4 SPECTRA cells (oilgas_gasturbine and telecom_churn, 8 scoreable seeds), Dirac-3 and its "
             "exact classical proxy scored the identical in-pocket rows within 0.0072 AUPRC of each other, the device "
             "better on 4 of 8 cells and worse by 0.0009 on average"),
      provenance=f"{SRC}, the in-pocket table and the paragraph under it (B4 section)",
      citation_context=('"The device is better on 4 of 8 cells, with a mean difference of -0.0009 and no difference '
                        'larger than 0.0072." (B4 section); "Inside the pocket, the device and its classical proxy are '
                        'indistinguishable." (B4 section)'),
      certainty_reasons=(OWN + ". NOT generalized: two cells, the frozen configuration. The document's 'Proxy's edge' "
                         "column is not like-for-like by its own correction and is not used. Same project as the "
                         "Phase 1 result it supports, so not independent"),
      supports=[PRIOR]),
    A(id="cvqboost-in-segment-edge-negative-on-device-spectra-b4",
      value=("Phase 2's B4 replication on Dirac-3 found no in-segment advantage: on every one of the 8 scoreable "
             "SPECTRA cells the pocket scored worse than a matched random segment of the same size and fraud rate; "
             "energy_steel, where prior work reported its win, could not be scored under the frozen control"),
      provenance=f"{SRC}, B4 section: the lead sentence, 'What it says' and 'What it does not say'",
      citation_context=('"The in-segment edge against the matched random-segment control is negative on every one of '
                        'the 8 scoreable cells." (B4 section, markdown bold dropped); "The pocket scores worse than a '
                        'random segment of the same size and fraud rate on all 8 scoreable cells." (What it says); '
                        '"It also says nothing about energy_steel, the cell where the prior work reported its overall '
                        'win, because that cell cannot be scored under the frozen control." (What it does not say)'),
      certainty_reasons=(OWN + ". Scope: the frozen cells on Phase 2's splits, seeds and matched control; telecom_churn "
                         "seeds 42 and 45 fall below the 50-positive floor and are unscoreable")),
    A(id="cvqboost-device-below-classical-bar-spectra-b4",
      value=("On Phase 2's B4 SPECTRA cells the Dirac-3 CVQBoost reached a mean test AUPRC of 0.839 on "
             "oilgas_gasturbine and 0.733 on telecom_churn, below the 0.874 and 0.867 of Phase 2's classical "
             "HistGradientBoosting bar (F100)"),
      provenance=f"{SRC}, B4 section, 'What it says', third bullet",
      citation_context=('"F100\'s HistGradientBoosting reaches 0.874 on oilgas_gasturbine and 0.867 on telecom_churn" '
                        '(What it says); "the device reaches 0.839 and 0.733" (What it says)'),
      certainty_reasons=OWN + ". The bar's own figures come from Phase 2's docs/F100_CLASSICAL_BAR.md, not read here",
      context="hsbc-2026"),
    A(id="qsvm-on-dirac3-weak-on-ulb-b5",
      value=("Phase 2's B5 sign-augmented primal QSVM on Dirac-3 reached test AUPRC 0.068 to 0.260 (mean 0.212) on the "
             "ULB credit-card data over 12 fits, against 0.767 for B1's CVQBoost on the same data; 11 of 12 "
             "Hamiltonians exceeded the device's ~23 dB resolution limit, a plausible but untested contributor"),
      provenance=f"{SRC}, B5 section",
      citation_context=('"Test AUPRC 0.068-0.260, mean 0.212" (B5 section, markdown bold dropped); "B1\'s CVQBoost on '
                        'the same data reaches 0.767." (B5 section); "This is not established as the cause, and nothing '
                        'in this sprint tested it." (B5 section)'),
      certainty_reasons=OWN + ". The resolution limit is offered by the source as a plausible cause only"),
]


def apply_changes(conn) -> list[str]:
    log = []
    if conn.execute("SELECT 1 FROM records WHERE id = ?", (SRC,)).fetchone() is None:
        insert_paper(conn, intake.build_record(SOURCE, today=TODAY))
        log.append(f"paper  {SRC} [read]")
    else:
        log.append(f"exists {SRC}")
    for assertion in ASSERTIONS:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (assertion.id,)).fetchone():
            log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, assertion, yielded_by=SRC)
        log.append(f"assert {assertion.id} <- {SRC} [{assertion.certainty}, {assertion.evidence_tag}]")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    digest = hashlib.sha256(source_bytes()).hexdigest()
    if digest != SHA256:
        print(f"{FILE} at {COMMIT[:7]} differs from the copy read on {TODAY} (SHA-256 {digest})")
        return 1
    if "--apply" not in args:
        intake.build_record(SOURCE, today=TODAY)  # validates the entry; nothing written
        print(f"paper  {SRC} [read]")
        for a in ASSERTIONS:
            print(f"assert {a.id} <- {SRC} [{a.certainty}, {a.evidence_tag}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F79 inbound trial: Phase 2 B4 and B5 hardware result")
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
