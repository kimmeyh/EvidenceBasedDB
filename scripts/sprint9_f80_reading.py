#!/usr/bin/env python3
"""Sprint 9 Task G (F80): the 76-record slice read and entered.

The slice (`manifests/sprint9_f80_slice.json`) is the 26 records the HSBC
submission cites plus the 50 most-cited unread QML records. Ten Sonnet 5.5
first-pass readers read them (`manifests/sprint9_f80_reads/group_*.json`,
kept verbatim): groups J1 to J3 the submission's sources, Q1 to Q7 the QML
papers.

HOW THE SOURCES WERE READ, as Tasks E and F (ADR-0005 A4: a subagent's read
alone never qualifies `read`): the coordinator then read each source's opening
and every passage an assertion quotes, with about 280 characters each side,
and checked selected figures against the full text. That read found the seven
values VALUE_EDITS corrects and the clause it strips from eqc-models.

ELEVEN RECORDS ARE REFUSED (REFUSE) and stay `seen`, each with its reason.
Nine QCi pages name Dirac-1 while the store tags them platform:dirac-3; there
is no Dirac-1 context, so their figures cannot be entered against the device
they describe (carded as F84). The space-logistics page has no body text. The
trade magazine PDF has no text layer, so no quote in it can be checked.

CERTAINTY follows Task E's GRADE mapping (scripts/sprint9_f78_ceiling_reading.py),
with one addition: a vendor's claim about its own product starts MODERATE as
vendor primary documentation (Sprint 7, F45) and is downgraded to LOW when it
reports a result; a description of the product (VENDOR_DESCRIPTIONS: a
version, a module, a stated limit or setup) stays MODERATE. No
admission-against-interest upgrade is made here (a Class 2 decision); the
candidates are listed in CANDIDATE_UPGRADES for Manual Validation.

THE FRESH-EYES REVIEW of 9f71f19 (2026-10-15) corrected five more values,
three grades that followed the reader's suggestion rather than the claim, one
claim type, three applicability rows, two missing conflict-of-interest
entries, and dropped one assertion that restated a determinate fact. A
re-apply now syncs every field the script sets.

DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent; a
changed value or read detail is corrected in place with the reason.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, admission_upgrade_reason, append_updated_reason,  # noqa: E402
                          insert_assertion, set_tier)

_spec = importlib.util.spec_from_file_location("f78", Path(__file__).with_name("sprint9_f78_ceiling_reading.py"))
f78 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f78)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-15"
TAG = "Sprint 9 Task G, F80"
READS_DIR = ROOT / "manifests" / "sprint9_f80_reads"
GROUPS = ("j1", "j2", "j3", "q1", "q2", "q3", "q4", "q5", "q6", "q7")
SUBAGENT_READER = f78.SUBAGENT_READER

COORDINATOR_DETAIL = ("the opening and every passage an assertion quotes, each with about 280 characters of "
                      "surrounding text, with selected figures checked against the full text; proofs, appendices "
                      "and tables beyond those passages not read by the coordinator" + f78.ABSENCE_NOTE)
COORDINATOR_DETAIL_REPO = ("the README opening and every quoted README or document passage, each with about 280 "
                           "characters of surrounding text" + f78.ABSENCE_NOTE)

EQC_DIR = Path(r"D:\Data\Harold\EvidenceBasedDB\References\eqc_models")
EQC_FILES = (EQC_DIR / "eqc-models-0.21.0_pypi-metadata.json", EQC_DIR / "eqc_models-0.21.0-py3-none-any.whl")
REPO_COMMITS = {  # the commit each clone was read at
    "kimmeyh-hsbc-quantum-fraud-github-repo": "ad9b9ec1c86fa315dadf7d11d0bae05d8a8f7e77",
    "thedaemon-wizard-global-quantum-ai-github-repo": "5055889a715a478e24a8b6407572ec4707300e2c",
}

_DIRAC1 = ("the page states its device is Dirac-1, but the store tags it platform:dirac-3 and has no Dirac-1 "
           "context, so its figures cannot be entered against the device they describe (F84)")
REFUSE = {
    "qci-applications-dimensionality-reduction-on-dirac": _DIRAC1,
    "qci-applications-feature-selection-on-dirac": _DIRAC1,
    "qci-applications-graph-partitioning-on-dirac": _DIRAC1,
    "qci-applications-max-cut-on-dirac": _DIRAC1,
    "qci-applications-portfolio-optimization-on-dirac": _DIRAC1,
    "qci-applications-set-partitioning-on-dirac": _DIRAC1,
    "qci-applications-traveling-salesman-on-dirac": _DIRAC1,
    "qci-applications-risk-based-uas-trajectory-optimization": _DIRAC1,
    "quantumcomputinginc-nd-entropy-quantum-computing-offers-an": (
        "the article names Dirac 1 as the machine behind EQC and never Dirac-3 or Dirac-3S, while the store tags "
        "it platform:dirac-3 (F84)"),
    "qci-applications-quantum-assisted-space-logistics-mission-planning": (
        "the saved page holds only site navigation and download links; no problem, formulation or result"),
    "qci-2026-entropy-computing-trade-magazine": (
        "the PDF has no text layer, so no quoted passage can be checked against it"),
}

CONTEXT_FIX = {  # record id -> context for its assertions and applicability, where the reader's was not valid
    "miri-2026-standard-quadratic-formulations-many-np": "qc",
}

VALUE_EDITS = {  # (exact reader text, replacement), from the coordinator's read
    "eqc-models-polynomial-fifth-order": [(
        ", matching the fifth-order interaction limit QCi states for Dirac-3S", "")],
    "ccc-benchmark-comparable-to-mlp-with-overfitting": [(
        "that train many more parameters,",
        "that train many more parameters (slightly worse test errors than the shallow and deep perceptrons, mixed "
        "against the linear one),")],
    "grant-gradient-variance-size-invariant-numerical": [("(up to 12 qubits, 120 layers", "(120 layers")],
    "tilly-single-register-runtime-too-large-needs-parallelism": [(
        "100 ns gates, 10^6 shots, k-UpCCGSD with k=1)",
        "100 ns gates, k-UpCCGSD with k=1, precision 10^-3 mEh for one expectation value)"),
        ("which makes parallelization essential.",
         "which makes parallelization essential. The review's text gives chemical precision as 1.6 mEH, about "
         "10^-3 EH, so Table 2's unit is inconsistent with it.")],
    "killoran-cvqnn-curve-fitting-saturates-at-six-layers": [(
        "fit quality improved with circuit depth",
        "the depth study (for sin(pi x)) showed fit quality improving with circuit depth"),
        ("and then saturated", "and then saturating")],
    "wan-qnn-learns-teleportation-in-simulation": [("about 5e-4", "5.0371 x 10^-4")],
    "perez-salinas-simulated-benchmarks-toy-problems": [(
        "comparison is to default scikit-learn models only",
        "comparison is only to simple scikit-learn models (shallow neural networks, simple support vector "
        "machines)")],
    "qml-qbm-clamping-fails-conditionals": [(
        "11-qubit generative example", "11-qubit supervised example (8 inputs, 3 outputs, trained on the joint "
                                       "distribution)")],
    # Figures restated in the source's own form (the number test found them).
    "dirac3-portfolio-255-monthly-problems-21y": [("2003-01-01 to 2024-03-31",
                                                   "January 1st, 2003, to March 31st, 2024")],
    # Fresh-eyes review of 9f71f19 (2026-10-15).
    "qci-fraud-qboost-vs-xgboost-table": [("about 3,000 transactions (80% train, 20% test)",
                                           "about 3000 transactions (80% train, the remainder test)"),
                                          ("QCi's own test; single split described, no confidence intervals.",
                                           "QCi's own test; the page reports one table and says repeated random "
                                           "sub-samples gave very similar results, with no figures; no confidence "
                                           "intervals.")],
    "grant-training-experiments-mnist-and-vqe": [("(132 layers, 200 trials)", "(132 layers)")],
    "moll-h2-vqe-ideal-simulator-needs-two-entanglers": [(
        "needed for chemical accuracy without noise.",
        "needed for chemical accuracy without noise, for the given experimental connectivity.")],
    "dirac3s-c250-9-time-vs-gpu-pgd": [(" Dirac-3S was thus slower by an order of magnitude on that instance.", "")],
}

VENDOR_START = "Started MODERATE: vendor primary documentation of its own product"

# The rest, from the fresh-eyes review of 9f71f19 (2026-10-15).
# A vendor's description of its product (a version, a module, a stated limit
# or setup) is not a result, so it is not downgraded.
VENDOR_DESCRIPTIONS = {
    "eqc-models-dirac3-cloud-solvers", "eqc-direct-package-v2-0-2", "qci-client-package-v5-0-0",
    "eqc-models-polynomial-fifth-order", "eqc-models-dirac3-sum-constraint", "eqc-models-direct-solver-python-limit",
    "dirac3-portfolio-255-monthly-problems-21y",
}
_DOC_FACT = ("Started HIGH: a statement of what the source itself says (a rule or date it sets), read in context. "
             "Graded by what the claim is, not by the first-pass suggestion")
CERTAINTY_OVERRIDES = {
    "kimmeyh-headline-null-cvqboost-trails": (
        "low", "Started LOW: an empirical result from one study (that CVQBoost trails the tuned classical "
               "detector); the absence of an advantage claim is what the source says, the trailing is measured. "
               "NOT upgraded"),
    "phase1-scored-against-published-criteria": ("high", _DOC_FACT),
    "challenge-two-stage-timeline-2026-2027": ("high", _DOC_FACT),
}
CLAIM_FIX = {  # a vendor's own result for its own platform
    "henriet-connectivity-lowers-gate-overhead-5-10x": "vendor-self-claim",  # Pasqal authors, Pasqal's platform
}
APPLIC_FIX = {  # record id -> (context, rationale), replacing what is stored
    "cao-2018-quantum-chemistry-age-quantum-computing": (
        "qc", "A review of quantum algorithms for quantum chemistry (phase estimation, VQE, NISQ methods); its "
              "subject is quantum computing for chemistry, not QML -- first-pass read"),
    "henriet-2020-quantum-computing-neutral-atoms": (
        "qc", "A Pasqal review of neutral-atom quantum processors and their applications; a hardware review, not "
              "QML -- first-pass read"),
    "miri-2026-standard-quadratic-formulations-many-np": (
        "platform:dirac-3s", "QCi lists it among its Dirac-3S technical references; the paper itself is "
                             "hardware-neutral formulation theory and never names Dirac -- QCi site placement and "
                             "the paper"),
}
DROPPED = {  # assertions not entered, and removed if a first apply stored them
    "kaggle-creditcard-fraud-284807-492": (
        "the dataset's size is a determinate fact about the dataset, already held twice in the store; a vendor "
        "page restating it adds nothing (CLAUDE.md: computed, never stored)"),
}
COI = {
    "miri-2026-standard-quadratic-formulations-many-np":
        "The authors are affiliated with Quantum Computing Inc. (QCi) -- Competing interests section",
    "wang-2026-motzkin-straus-optimization-entropy-computing":
        "All four authors are affiliated with Quantum Computing Inc. (QCi), one also with UIUC; no "
        "competing-interests statement found -- title-page affiliations",
}
# Admission-against-interest candidates for the team lead at Manual
# Validation (Class 2), as F65's CANDIDATE_UPGRADES: id -> what it costs QCi.
CANDIDATE_UPGRADES = {
    "dirac3s-c250-9-time-vs-gpu-pgd": "QCi's own table shows Dirac-3S about 12 times slower than GPU PGD on C250.9",
    "dirac3s-dimacs-best-known-33-of-75": "QCi reports Dirac-3S missed the best known clique on 42 of 75 graphs",
    "dirac3-portfolio-vs-localsolver-energies-similar": "QCi reports LocalSolver lower for some solutions",
}
# The candidates the team lead approved (Q3, 2026-10-15: "q3 1", all three).
# certainty() raises each one low -> moderate, and the sync keeps it there.
UPGRADES_APPROVED: set[str] = set(CANDIDATE_UPGRADES)
UPGRADE_DECISION = "the team lead's decision at Sprint 9 Manual Validation (Q3), 2026-10-15"
UPGRADE_NOTE = f"2026-10-15 ({TAG}): certainty UPGRADED low -> moderate for admission against interest, {UPGRADE_DECISION}"


def load_groups() -> list[tuple[str, dict]]:
    out = []
    for g in GROUPS:
        data = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))
        out += [(g, p) for p in data["papers"]]
    return out


def kept_groups() -> list[tuple[str, dict]]:
    return [(g, p) for g, p in load_groups() if p["record_id"] not in REFUSE]


def _usable(path: str | None) -> bool:
    """A quote file the reader named that still exists outside the session's scratch space."""
    return bool(path) and Path(path).is_absolute() and "scratchpad" not in path and Path(path).is_file()


def source_file(paper: dict, a: dict | None = None) -> str:
    """The file an assertion's quotes were taken from (eqc-models excepted: EQC_FILES)."""
    for cand in ((a or {}).get("quote_file"), paper.get("quote_file_default"), paper["file"]):
        if _usable(cand):
            return cand
    raise FileNotFoundError(f"{paper['record_id']}: no readable source file")


def edited_value(aid: str, value: str) -> str:
    for old, new in VALUE_EDITS.get(aid, []):
        if old not in value:
            raise ValueError(f"{aid}: the text to replace is not in the reader's value: {old[:60]!r}")
        value = value.replace(old, new)
    return " ".join(value.split())


def claim_type(aid: str, a: dict) -> str:
    return CLAIM_FIX.get(aid) or a.get("claim_type") or "positive"


def certainty(aid: str, a: dict) -> tuple[str, str]:
    """(certainty, certainty_reasons) as graded, or one level up where the
    team lead approved an admission-against-interest upgrade."""
    level, reasons = _graded(aid, a)
    if aid not in UPGRADES_APPROVED:
        return level, reasons
    if level != "low":
        raise ValueError(f"{aid}: an upgrade starts from low, not {level}")
    return "moderate", admission_upgrade_reason(reasons, CANDIDATE_UPGRADES[aid], UPGRADE_DECISION)


def _graded(aid: str, a: dict) -> tuple[str, str]:
    if aid in CERTAINTY_OVERRIDES:
        return CERTAINTY_OVERRIDES[aid]
    if claim_type(aid, a) == "vendor-self-claim":
        if aid in VENDOR_DESCRIPTIONS:
            return ("moderate", f"{VENDOR_START}. Not upgraded: a description of the product, not a result")
        return ("low", f"{VENDOR_START}. DOWNGRADED one level: a result the vendor reports about its own product, "
                       "not independently checked")
    return f78.certainty(aid, a["kind"], a.get("certainty_suggestion", ""), False, a.get("certainty_reason", ""))


def context_of(rid: str, a: dict) -> str:
    if rid in APPLIC_FIX and APPLIC_FIX[rid][0] in ("qc", "qml", "ml"):
        return APPLIC_FIX[rid][0]
    return CONTEXT_FIX.get(rid) or a.get("context") or "qml"


def assertions() -> list[tuple[str, AssertionRecord, str]]:
    out = []
    for g, p in kept_groups():
        rid = p["record_id"]
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            if aid in DROPPED:
                continue
            cert, reasons = certainty(aid, a)
            absence = a.get("claim_type") == "absence"
            out.append((g, AssertionRecord(
                id=aid, value=edited_value(aid, a["value"]), provenance=f"{rid}, {a['anchor']}",
                citation_context="; ".join(f'"{q}" ({a["anchor"]})' for q in a["quotes"]),
                evidence_tag="N/A", context=context_of(rid, a), certainty=cert, certainty_reasons=reasons,
                fidelity=a.get("fidelity") or "scoped", derivation="extracted",
                claim_type=claim_type(aid, a),
                search_scope=(a.get("search_scope") if absence else None),
                updated=TODAY, updated_reason=f"{TODAY} ({TAG}): extracted from {rid}; first-pass read by a subagent, "
                                              "every quoted passage read in context by the coordinator"), rid))
    return out


def _sha(path: Path) -> str:
    data = path.read_bytes()
    return f"SHA-256 {hashlib.sha256(data).hexdigest()}, {len(data):,} bytes"


def local_additions(p: dict) -> tuple[list[str], str]:
    """(local paths to add to access, evidence note) for a kept record."""
    rid = p["record_id"]
    if rid in REPO_COMMITS:
        path = p["file"].replace("/", "\\")
        return [path], f"Local clone read at commit {REPO_COMMITS[rid]}, {TODAY} (F80)"
    if rid == "qci-package-eqc-models":
        return ([str(f) for f in EQC_FILES],
                "; ".join(f"{f.name} {_sha(f)}" for f in EQC_FILES) + f", recorded {TODAY} (F80)")
    path = p["file"].replace("/", "\\")
    return [path], f"Local copy {_sha(Path(path))}, recorded {TODAY} (F80)"


def apply_changes(conn) -> list[str]:
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    for g, p in load_groups():
        rid = p["record_id"]
        reason = REFUSE.get(rid)
        partial = p.get("read_extent") == "partial"
        sub_detail = (f"first pass, in part: {p['partial_detail']} (Sonnet 5.5 reader, group {g.upper()})"
                      if partial else f"first pass, the whole source (Sonnet 5.5 reader, group {g.upper()})")
        have = {(r[0], r[1], r[2], r[3]) for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,))}
        if reason:
            # Keyed without the detail: a reworded detail must not add a second row.
            if (SUBAGENT_READER, TODAY, "subagent") not in {h[:3] for h in have}:
                add_read(conn, rid, SUBAGENT_READER, TODAY, "subagent", sub_detail)
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read at first pass and NOT entered: {reason}",
                                      TODAY)
                log.append(f"refuse {rid}")
            else:
                log.append(f"exists refused {rid}")
            continue
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        paths, note = local_additions(p)
        present = {s.lower() for s in recheck.local_paths(access or "")}
        new = [s for s in paths if s.lower() not in present]
        if new:
            conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?",
                         (" | ".join([access, *new]) if access else " | ".join(new), rid))
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?",
                         (f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): local copy added to access", TODAY)
            log.append(f"access {rid} += {', '.join(new)}")
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            rationale = f"{p['what_it_is'].rstrip('.')} -- first-pass read"
            ctx = CONTEXT_FIX.get(rid) or p.get("bears_on_context")
            if ctx not in contexts:
                # The reader judged the source as a whole off-context; only its assertions bear on one.
                ctx = context_of(rid, p["assertions"][0])
                rationale += f"; only its assertions bear on {ctx}: {p.get('why_not', '').rstrip('.')}"
            if ctx not in contexts:
                raise ValueError(f"{rid}: applicability context {ctx!r} is not a context")
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, rationale))
            log.append(f"applic {rid} [{ctx}]")
        if rid in APPLIC_FIX:
            ctx, rationale = APPLIC_FIX[rid]
            rows_now = conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?",
                                    (rid,)).fetchall()
            if [tuple(r) for r in rows_now] != [(ctx, rationale)]:
                conn.execute("DELETE FROM paper_applicability WHERE record_id = ?", (rid,))
                conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                             (rid, ctx, rationale))
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}, review): applicability corrected to {ctx}", TODAY)
                log.append(f"update applic {rid} [{ctx}]")
        if rid in COI:
            stored_coi = conn.execute("SELECT coi FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
            if stored_coi != COI[rid]:
                conn.execute("UPDATE paper_fields SET coi = ? WHERE record_id = ?", (COI[rid], rid))
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}, review): disclosed conflict of interest recorded",
                                      TODAY)
                log.append(f"update coi {rid}")
        coord = COORDINATOR_DETAIL_REPO if rid in REPO_COMMITS else COORDINATOR_DETAIL
        rows = {(r[0], r[1], r[2]): r[3] for r in have}
        for reader, extent, detail in ((SUBAGENT_READER, "subagent", sub_detail), ("Claude", "partial", coord)):
            if (reader, TODAY, extent) not in rows:
                add_read(conn, rid, reader, TODAY, extent, detail)
                log.append(f"read   {rid} [{reader}, {extent}]")
            elif rows[(reader, TODAY, extent)] != detail:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? AND read_on = ? "
                             "AND extent = ?", (detail, rid, reader, TODAY, extent))
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read detail corrected", TODAY)
                log.append(f"update read {rid} [{reader}]")
        if tier != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{TODAY}, Claude, read the opening and every quoted passage in context; first pass by a subagent"))
            log.append(f"tier   {rid} -> read")
    for aid in sorted(DROPPED):
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (aid,)).fetchone():
            conn.execute("DELETE FROM paper_yields WHERE assertion_id = ?", (aid,))  # no cascade on this side
            conn.execute("DELETE FROM records WHERE id = ?", (aid,))
            log.append(f"drop   {aid}")
    for g, a, rid in assertions():
        if a.context not in contexts:
            raise ValueError(f"{a.id}: context {a.context!r} is not a context")
        stored = conn.execute(
            "SELECT r.value, r.certainty, r.certainty_reasons, r.provenance, f.citation_context, f.claim_type "
            "FROM records r JOIN assertion_fields f ON f.record_id = r.id WHERE r.id = ?", (a.id,)).fetchone()
        if not stored:
            insert_assertion(conn, a, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        # Every field the script sets is compared, so a changed quote, context
        # or claim type is synced too (review of 9f71f19: only three were).
        stored_ctx = sorted(r[0] for r in conn.execute(
            "SELECT context_id FROM record_contexts WHERE record_id = ?", (a.id,)))
        want = (a.value, a.certainty, a.certainty_reasons, a.provenance, a.citation_context, a.claim_type)
        if tuple(stored) == want and stored_ctx == [a.context]:
            log.append(f"exists {a.id}")
            continue
        conn.execute("UPDATE records SET value = ?, certainty = ?, certainty_reasons = ?, provenance = ? WHERE id = ?",
                     (a.value, a.certainty, a.certainty_reasons, a.provenance, a.id))
        conn.execute("UPDATE assertion_fields SET citation_context = ?, claim_type = ? WHERE record_id = ?",
                     (a.citation_context, a.claim_type, a.id))
        if stored_ctx != [a.context]:
            conn.execute("DELETE FROM record_contexts WHERE record_id = ?", (a.id,))
            conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, ?)", (a.id, a.context))
        upgraded = stored[1] == "low" and a.certainty == "moderate" and a.id in UPGRADES_APPROVED
        append_updated_reason(conn, a.id, UPGRADE_NOTE if upgraded else
                              f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
        log.append(f"{'upgrade' if upgraded else 'update'} {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kept = assertions()
    if len({a.id for _, a, _ in kept}) != len(kept):
        print("duplicate assertion ids")
        return 1
    if "--apply" not in args:
        for _, a, rid in kept:
            print(f"assert {a.id} <- {rid} [{a.certainty}, {a.claim_type}, {a.context}]")
        print(f"{len(kept)} assertions from {len(kept_groups())} records; {len(REFUSE)} refused. "
              "DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F80 slice read and entered")
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
