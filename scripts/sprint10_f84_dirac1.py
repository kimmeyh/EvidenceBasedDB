#!/usr/bin/env python3
"""Sprint 10 Task F (F84): the nine Dirac-1 records, under platform:dirac-1.

Sprint 9 Task G (F80) refused nine QCi sources because they describe
Dirac-1 while the store tagged them platform:dirac-3 and had no Dirac-1
context. ADR-0004 A10 (team lead Q1 = 1, 2026-10-18) adds that context.
This script adds it to the live store, retags the nine, and enters their
twelve first-pass assertions from F80's read groups
(`manifests/sprint9_f80_reads/group_j3.json`, and `group_j2.json` for the
QC-7 article). They do not count toward F89's 74 (Q3 = 1).

HOW THE SOURCES WERE READ: a Sonnet 5.5 first-pass reader read each whole
saved page in Sprint 9 (its row is already stored). On 2026-10-18 the
coordinator read each page's opening, every quoted passage with about 300
characters each side, and the passage behind every figure a value states
(sample counts, instance sizes, the BMW constraints). That read found two
reader conclusions the sources do not state (VALUE_EDITS): "scales better
than cubic" (the page fits polynomials of order 2, 3 and 4 and says
"within polynomial time"; "cubic" is not on the page), and "64 binary
variables" (the reader's own 8 x 8; the page states no count).

CERTAINTY follows F80's rule for a vendor's claim about its own product:
it starts MODERATE as vendor primary documentation; a description of the
product or of the tutorial's setup stays MODERATE (DESCRIPTIONS); a result
the vendor reports is downgraded to LOW. No upgrade is made.

DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent; a
re-apply syncs every assertion field through the shared sync.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_assertion,  # noqa: E402
                          set_tier, sync_assertion)

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-18"
TAG = "Sprint 10 Task F, F84"
CTX = "platform:dirac-1"
CTX_DESCRIPTION = ("QCi's Dirac-1 system, named as the device on its earlier application pages "
                   "(ADR-0004 A10, 2026-10-18)")
OLD_CTX = "platform:dirac-3"

NINE = (
    "qci-applications-dimensionality-reduction-on-dirac",
    "qci-applications-feature-selection-on-dirac",
    "qci-applications-graph-partitioning-on-dirac",
    "qci-applications-max-cut-on-dirac",
    "qci-applications-portfolio-optimization-on-dirac",
    "qci-applications-set-partitioning-on-dirac",
    "qci-applications-traveling-salesman-on-dirac",
    "qci-applications-risk-based-uas-trajectory-optimization",
    "quantumcomputinginc-nd-entropy-quantum-computing-offers-an",
)
WHY_DIRAC1 = {rid: "the page's header states \"Device: Dirac-1\"" for rid in NINE[:7]}
WHY_DIRAC1["qci-applications-risk-based-uas-trajectory-optimization"] = (
    "the case study ran on Dirac-1 and names Dirac-3 only as future work")
WHY_DIRAC1["quantumcomputinginc-nd-entropy-quantum-computing-offers-an"] = (
    "the article names Dirac 1 as QCi's quantum photonic computing system and never names Dirac-3 or Dirac-3S")

VALUE_EDITS = {  # (exact reader text, replacement), from the coordinator's read
    "dirac1-uas-10364-vars-13852s-polynomial-claim": [(
        "and concludes from polynomial fits that time-to-solution scales better than cubic.",
        "fits polynomials of order 2, 3 and 4 through its timings, and concludes that Dirac-1 solved this "
        "NP-complete problem within polynomial time.")],
    "dirac1-tsp-8-cities-qap-formulation": [("(64 binary variables, 5 samples, penalty multiplier 20)",
                                             "(5 samples, penalty multiplier 20)")],
    "dirac1-graph-partition-two-small-graphs": [(
        "it states no objective value or optimality check.",
        "it states no objective value or optimality check, although its introduction calls the plotted split "
        "optimal.")],
    "qci-web-eqc-30000-qubit-limit-estimate": [(
        "This is a vendor estimate, not a measured result.",
        "This is a vendor estimate, not a measured result; the article names Dirac 1 as the system EQC runs on.")],
    "qci-web-bmw-sensor-six-minutes": [(
        "No classical baseline is given.",
        "No classical baseline is given. The article names Dirac 1 as its EQC system but does not say which "
        "device ran these tests.")],
}
EXTRA_QUOTES = {  # a quote the coordinator's read adds for an edited value
    "dirac1-graph-partition-two-small-graphs": ["we aim to execute and plot the optimal split of two small graph "
                                                "instances"],
    "qci-web-eqc-30000-qubit-limit-estimate": ["The technology is the engineering marvel behind Dirac 1"],
    "qci-web-bmw-sensor-six-minutes": ["The technology is the engineering marvel behind Dirac 1"],
}
CLAIM_FIX = {"dirac1-pca-not-np-hard-demo": "vendor-self-claim"}  # QCi's statement about its own tutorial
DESCRIPTIONS = {  # the tutorial's setup or scope, not a result
    "dirac1-pca-qubo-medicare-93-to-3", "dirac1-pca-not-np-hard-demo", "dirac1-feature-selection-10-of-93",
    "dirac1-graph-partition-two-small-graphs", "dirac1-portfolio-select-30-stocks-binary",
    "dirac1-tsp-8-cities-qap-formulation",
}
COORDINATOR_DETAIL = ("the opening, every passage an assertion quotes with about 300 characters each side, and the "
                      "passage behind every figure an entered value states" + f80.f78.ABSENCE_NOTE)


def papers() -> list[tuple[str, dict]]:
    by_id = {p["record_id"]: (g, p) for g, p in f80.load_groups()}
    missing = [rid for rid in NINE if rid not in by_id]
    if missing:
        raise ValueError(f"not in F80's read groups: {missing}")
    return [by_id[rid] for rid in NINE]


def edited_value(aid: str, value: str) -> str:
    for old, new in VALUE_EDITS.get(aid, []):
        if old not in value:
            raise ValueError(f"{aid}: the text to replace is not in the reader's value: {old[:60]!r}")
        value = value.replace(old, new)
    return " ".join(value.split())


def certainty(aid: str) -> tuple[str, str]:
    if aid in DESCRIPTIONS:
        return "moderate", f"{f80.VENDOR_START}. Not upgraded: a description of the tutorial's setup or scope, not a result"
    return "low", (f"{f80.VENDOR_START}. DOWNGRADED one level: a result the vendor reports about its own product, "
                   "not independently checked")


def assertions() -> list[tuple[AssertionRecord, str]]:
    out = []
    for _, p in papers():
        rid = p["record_id"]
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            cert, reasons = certainty(aid)
            quotes = list(a["quotes"]) + EXTRA_QUOTES.get(aid, [])
            out.append((AssertionRecord(
                id=aid, value=edited_value(aid, a["value"]), provenance=f"{rid}, {a['anchor']}",
                citation_context="; ".join(f'"{q}" ({a["anchor"]})' for q in quotes),
                evidence_tag="N/A", context=CTX, certainty=cert, certainty_reasons=reasons,
                fidelity=a.get("fidelity") or "scoped", derivation="extracted",
                claim_type=CLAIM_FIX.get(aid) or a.get("claim_type") or "positive",
                updated=TODAY, updated_reason=(f"{TODAY} ({TAG}): extracted from {rid}; first-pass read by a "
                                               "subagent (Sprint 9), every quoted passage and stated figure read "
                                               "in context by the coordinator")), rid))
    return out


def apply_changes(conn) -> list[str]:
    log = []
    if conn.execute("SELECT 1 FROM contexts WHERE id = ?", (CTX,)).fetchone() is None:
        conn.execute("INSERT INTO contexts (id, description) VALUES (?, ?)", (CTX, CTX_DESCRIPTION))
        log.append(f"context {CTX}")
    elif conn.execute("SELECT description FROM contexts WHERE id = ?", (CTX,)).fetchone()[0] != CTX_DESCRIPTION:
        conn.execute("UPDATE contexts SET description = ? WHERE id = ?", (CTX_DESCRIPTION, CTX))
        log.append(f"update context {CTX}")
    for _, p in papers():
        rid = p["record_id"]
        ctxs = {r[0] for r in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))}
        if OLD_CTX in ctxs or CTX not in ctxs:
            conn.execute("DELETE FROM record_contexts WHERE record_id = ? AND context_id = ?", (rid, OLD_CTX))
            conn.execute("INSERT OR IGNORE INTO record_contexts (record_id, context_id) VALUES (?, ?)", (rid, CTX))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): retagged {OLD_CTX} -> {CTX} (ADR-0004 A10): "
                                             f"{WHY_DIRAC1[rid]}", TODAY)
            log.append(f"retag  {rid}")
        rationale = f"{p['what_it_is'].rstrip('.')} -- first-pass read; {WHY_DIRAC1[rid]}"
        rows = [tuple(r) for r in conn.execute(
            "SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (rid,))]
        if rows != [(CTX, rationale)]:
            conn.execute("DELETE FROM paper_applicability WHERE record_id = ?", (rid,))
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, CTX, rationale))
            log.append(f"applic {rid} [{CTX}]")
        have = {(r[0], r[1], r[2]): r[3] for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,))}
        if ("Claude", TODAY, "partial") not in have:
            add_read(conn, rid, "Claude", TODAY, "partial", COORDINATOR_DETAIL)
            log.append(f"read   {rid} [Claude, partial]")
        elif have[("Claude", TODAY, "partial")] != COORDINATOR_DETAIL:
            conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = 'Claude' "
                         "AND read_on = ? AND extent = 'partial'", (COORDINATOR_DETAIL, rid, TODAY))
            log.append(f"update read {rid}")
        if conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{TODAY}, Claude, read the opening, every quoted passage and every stated figure in context; "
                "first pass by a subagent (Sprint 9)"))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read and entered under {CTX}; Sprint 9's refusal "
                                             "(no Dirac-1 context) no longer applies", TODAY)
            log.append(f"tier   {rid} -> read")
    for a, rid in assertions():
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_assertion(conn, a, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        changed = sync_assertion(conn, a, f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kept = assertions()
    if len({a.id for a, _ in kept}) != len(kept):
        print("duplicate assertion ids")
        return 1
    if "--apply" not in args:
        for a, rid in kept:
            print(f"assert {a.id} <- {rid} [{a.certainty}, {a.claim_type}]\n    {a.value}")
        print(f"{len(kept)} assertions from {len(NINE)} records. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F84 Dirac-1 context, nine records retagged and entered")
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
