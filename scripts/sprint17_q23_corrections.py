#!/usr/bin/env python3
"""Sprint 17 Manual Validation q23 = a (team lead, 2026-11-09): the 8 Task E assertions the fresh-eyes review of
24b05d7 found, corrected in the store. INTAKE_WORKFLOW.md section 76.

The signed reviews (`manifests/sprint13_g_reviews/g230.json`, `g295.json`, `g296.json`, `g348.json`) are never
rewritten; this script is the later correction, and each record's history names it.

- Five HIGH values said more than their quotes; the paper holds each, so the value stays and the passages it rests on
  are added as quotes: sar-vqc-components, sar-qcnn-architecture, sar-metric-families, aharonov-model-definition,
  alarfaj-dataset-description.
- albash-grover-local-condition-not-proof was HIGH as "the paper's own stated limit"; it is the review's statement
  about another paper's result (Roland and Cerf's), so it is LOW, "field statement" (`store.grading`).
- chance-level-and-signature-control joined claims that Pere v2's read also entered one by one
  (quantum-accuracy-distribution, parity-control-edge-0-42, parity-control-generic-models-fail,
  parity-control-not-a-separation-result); it is narrowed to the one claim none of them holds, the abstract's
  "the null result is not evidence that quantum-sensitive structure cannot exist", LOW, "authors' claim".
- random-instance-distribution-scope was typed `absence`; it states the instance distribution the paper uses, a
  positive setup statement.

Every quote is checked verbatim against the paper's PDF before any write; a changed value also names its passage.

    python scripts/sprint17_q23_corrections.py           # dry run: every quote checked, nothing written
    python scripts/sprint17_q23_corrections.py --apply   # verified backup first; a second apply writes nothing
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import low_grade  # noqa: E402
from store.ingest import AssertionRecord, sync_verified_assertion  # noqa: E402
from store.quotes import require_edit_basis, require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, _ = script_paths(__file__)
TODAY = "2026-11-09"
NOTE = (f"{TODAY} (Sprint 17 Manual Validation, q23 = a): corrected after the fresh-eyes review of Task E's apply "
        "(24b05d7, INTAKE_WORKFLOW.md section 76); scripts/sprint17_q23_corrections.py")


def q(text: str, anchor: str) -> str:
    return f'"{text}" ({anchor})'


VQC, QCNN, METRICS = "Section II-B-1, p.7", "Section II-B-2, p.8", "Section V-C, p.27"
INTRO = "Introduction, p.2"
ALARFAJ = "Section III.A, p.5"

# id -> the quotes added after the stored ones
ADD_QUOTES = {
    "sar-vqc-components": [
        q("Parameterized Quantum layers: Gates with tunable parameters", VQC),
        q("Entanglement layers: Here, gates like CNOT are used for entangling qubits", VQC),
        q("Measurement: Here, qubits are collapsed to classical bits", VQC),
        q("Cost function: The output probabilities from measurements are passed to the cost function", VQC),
    ],
    "sar-qcnn-architecture": [
        q("Convolutional layer localised entangling operation simulating feature extraction.", QCNN),
        q("Fully connected layer entangles the remaining qubits and measures to produce the final output.", QCNN),
    ],
    "aharonov-model-definition": [
        q("of Hinit is required to be an easy to prepare state", INTRO),
        q("We require the Hamiltonians to be local", INTRO),
        q("The running time of the adiabatic computation is determined by the minimal spectral gap", INTRO),
        q("straight line connecting Hinit and Hﬁnal", INTRO),
    ],
    # Fresh-eyes review of the q23 apply, H1: the value names Roland and Cerf and the numerical evidence; neither was
    # quoted. Footnote 16 holds both.
    "albash-grover-local-condition-not-proof": [
        q("reported in (Roland and Cerf, 2002)", "Section III.A.2, p.11"),
        q("suffices to achieve a small adiabatic error for the schedule (29) is numerical.", "Section III.A.2, p.11"),
    ],
    "alarfaj-dataset-description": [
        q("Because disclosing a consumer’s transaction details is considered a problem of conﬁdentiality, the main "
          "component analysis is applied to the majority of the dataset’s features", ALARFAJ),
    ],
}
# id -> its whole new quote list (replacing the stored one)
SET_QUOTES = {
    "sar-metric-families": [
        q("These metrics span classification (e.g., accuracy, precision, recall, F1-score, AUC-ROC), segmentation "
          "(e.g., Dice coefficient, IoU, Hausdorff distance), and regression (e.g., MAE, MSE, RMSE, R2 score), along "
          "with hardware-aware efficiency indicators such as training time, inference time, memory footprint, and "
          "model-specific complexity measures", METRICS),
    ],
}
PERE = "chance-level-and-signature-control"
PERE_PAPER = "pere-2025-data-complexity-threshold-between-classical"
PERE_QUOTE = "Thus the null result is not evidence that quantum-sensitive structure cannot exist."
PERE_VALUE = "The authors state that the null result is not evidence that quantum-sensitive structure cannot exist."
ALBASH = "albash-grover-local-condition-not-proof"
RANDOM = "random-instance-distribution-scope"
IDS = tuple(dict.fromkeys((*ADD_QUOTES, *SET_QUOTES, ALBASH, PERE, RANDOM)))


def stored_assertion(conn: sqlite3.Connection, rid: str) -> AssertionRecord:
    r = conn.execute("SELECT value, provenance, evidence_tag, certainty, certainty_reasons, fidelity, reading_level "
                     "FROM records WHERE id = ? AND class = 'assertion'", (rid,)).fetchone()
    if r is None:
        raise ValueError(f"{rid}: no such assertion in the store")
    f = conn.execute("SELECT units, rounding, citation_context, derivation, claim_type, search_scope "
                     "FROM assertion_fields WHERE record_id = ?", (rid,)).fetchone()
    context = conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ? ORDER BY context_id",
                           (rid,)).fetchone()[0]
    return AssertionRecord(id=rid, value=r[0], provenance=r[1], evidence_tag=r[2], context=context,
                           certainty=r[3], certainty_reasons=r[4], fidelity=r[5], reading_level=r[6],
                           units=f[0], rounding=f[1], citation_context=f[2], derivation=f[3], claim_type=f[4],
                           search_scope=f[5])


def paper_pdf(conn: sqlite3.Connection, rid: str) -> str:
    """The local PDF the assertion's paper names in its access (the paper id leads the provenance)."""
    paper = rid.split(",")[0]
    access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (paper,)).fetchone()
    pdfs = [a.strip() for a in (access[0] if access else "").split("|") if a.strip().lower().endswith(".pdf")]
    if len(pdfs) != 1 or not Path(pdfs[0]).is_file():
        raise ValueError(f"{paper}: no single local PDF in its access ({pdfs})")
    return pdfs[0]


def with_added(stored: str, added: list[str]) -> str:
    """The stored quotes with each added quote once, at the end. Idempotent: an added quote already present (from an
    earlier apply, once or more) is taken out first (the first version appended them on every apply, so the second
    apply of 2026-11-09 wrote each of them twice into 4 records; this puts them back to once)."""
    for quote in added:
        while f"; {quote}" in stored:
            stored = stored.replace(f"; {quote}", "", 1)
    return "; ".join([stored, *added])


def wanted(conn: sqlite3.Connection, rid: str, texts: dict[str, str]):
    """The corrected assertion and the quote check that licenses its write."""
    a = stored_assertion(conn, rid)
    pdf = paper_pdf(conn, a.provenance)
    text = texts.setdefault(pdf, source_text(pdf))
    if rid in ADD_QUOTES:
        a.citation_context = with_added(a.citation_context, ADD_QUOTES[rid])
    elif rid in SET_QUOTES:
        a.citation_context = "; ".join(SET_QUOTES[rid])
    if rid == ALBASH:
        a.certainty, a.certainty_reasons = low_grade("field statement")
    elif rid == PERE:
        require_edit_basis(rid, PERE_VALUE, [PERE_QUOTE], text)
        a.value = PERE_VALUE
        a.provenance = f"{PERE_PAPER}, Abstract, p.1"
        a.citation_context = q(PERE_QUOTE, "Abstract, p.1")
        a.certainty, a.certainty_reasons = low_grade("authors' claim")
    elif rid == RANDOM:
        a.claim_type, a.search_scope = "positive", None
    return a, require_verbatim(rid, a.citation_context, text, value=a.value)


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    texts: dict[str, str] = {}
    with connect(DB_PATH) as conn:
        plan = [wanted(conn, rid, texts) for rid in IDS]  # every check before any write
    print(f"{len(plan)} assertions checked: every quote verbatim in its PDF")
    if not apply:
        for a, _ in plan:
            print(f"would sync {a.id}")
        return 0
    backup_before_write(DB_PATH, "Sprint 17 q23 corrections")
    with connect(DB_PATH) as conn:
        for a, verified in plan:
            changed = sync_verified_assertion(conn, a, verified, NOTE, TODAY)
            print(f"{a.id}: {', '.join(changed) if changed else 'already as wanted'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
