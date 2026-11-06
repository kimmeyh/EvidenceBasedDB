#!/usr/bin/env python3
"""Sprint 16 Task H (F51, released from HOLD, team lead Q4 = 1): the CVQBoost findings record and its six assertions.
INTAKE_WORKFLOW.md section 74.

The source is FourierWall2's working document "Maximizing Predictions from CVQBoost: Cumulative Findings", last
updated 2026-08-04 (SHA-256 425358a7b4cec71f...; the copy in References and FourierWall2's own are identical, checked
2026-11-06). It was read in full on 2026-11-06. The six assertions are the Cyc and CVQBoost handoff's
(`Handoff-2026-10\\ebdb-handoff\\05-sprint-script-draft.py`), each value rewritten so that every figure in it is in its
own quotes, and each graded by what the document shows: each is one study's run (single runs on one seed), so each
is LOW, "measured result" (`store.grading`; the handoff's 2026-09 HIGH grades predate it).

Authorship (the handoff's decision 1, still open): the document names no author, and F51's card says the authorship
is settled by provenance, not by attribution. So the record cites the FourierWall2 campaign and names no person, and
its id carries no author's name (the handoff's draft id did).

Two Phase 2 records bear on the document's in-segment wins (sections 6, 10 and 11): B4's Dirac-3 replication
(cvqboost-in-segment-edge-negative-on-device-spectra-b4: no in-segment advantage on any scoreable cell) and F162
(the proxy, not the device, over ten seeds on three cells: no in-pocket win repeats). None of the six states a win, so
no relation is written; the record's evidence names both. The shallow-learner assertion assumes a win at the default
configuration, the kind both records question; its certainty reason says so.

    python scripts/sprint16_f51_cvqboost.py           # dry run: every quote checked, nothing written
    python scripts/sprint16_f51_cvqboost.py --apply   # verified backup first
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import low_grade  # noqa: E402
from store.ingest import (AssertionRecord, append_updated_reason, insert_paper,  # noqa: E402
                          insert_verified_assertion, sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

ROOT, DB_PATH, _ = script_paths(__file__)
TODAY = "2026-11-06"
TAG = "Sprint 16 Task H, F51"
DOC = Path(r"D:\Data\Harold\EvidenceBasedDB\References\2026-08_Kimmey_CVQBoost-Findings.md")
COPIES = (DOC, Path(r"D:\Data\Harold\github\FourierWall2\docs\CVQBoost_Findings.md"))
SHA = "425358a7b4cec71f124d9b0b85fe34c4611ddd23a1705a7f84f151c903be2c23"
RID = "fourierwall2-2026-maximizing-predictions-cvqboost-cumulative-findings"
F162 = "f162-cvqboost-proxy-not-above-classical-in-spectra-pocket"
B4 = "cvqboost-in-segment-edge-negative-on-device-spectra-b4"
REASON = f"{TODAY} ({TAG}): extracted from {RID}, read in full by the coordinator; every quote checked verbatim"
READ = "the whole document, sections 1 to 12, every table"
SYNC_REASON = f"{TODAY} ({TAG}): corrected to the script's current text after the fresh-eyes review"

ENTRY = {
    "id": RID,
    "kind": "reference",
    "access": str(DOC),
    "title": "Maximizing Predictions from CVQBoost: Cumulative Findings",
    "citation": ("FourierWall2 campaign, \"Maximizing Predictions from CVQBoost: Cumulative Findings,\" working "
                 "document docs/CVQBoost_Findings.md, last updated 2026-08-04 (hand-transcribed from the document's "
                 "title and first paragraph; the document names no author)"),
    "transcribed_from": "the document's title and first paragraph",
    "context": "platform:dirac-3",
    "tier": "read",
    "disposition": ("Reference: the FourierWall2 campaign's tuning record for CVQBoost on Dirac-3 against XGBoost over "
                    "the four SPECTRA datasets: parameter sweeps, QPU costs, the variable ceiling, the tuned rollout and "
                    "the in-segment overfitting analysis"),
    "evidence": (f"Identical copies, SHA-256 {SHA}: {COPIES[0]} and {COPIES[1]} (FourierWall2 is not a git "
                 "repository; its CHANGELOG 0.1.0, 2026-08-04, names the document). Runs on Dirac-3 with pinned seed "
                 "20260804, single runs. The hsbc preregistration calls it \"a prior exploratory sweep (FourierWall2 "
                 "campaign, 2026-08-04)\". The References copy's file name is the collector's label, not an "
                 "attribution: the document names no author. Two Phase 2 records bear on the in-segment wins of "
                 "sections 6, 10 and 11: " + B4 + " (B4's Dirac-3 replication: no in-segment advantage on any "
                 "scoreable cell) and " + F162 + " (a proxy, not the device, over ten seeds on three cells, label "
                 "target only: no in-pocket win repeats reliably). No re-run of this document exists (checked "
                 "2026-11-05)."),
    "found_via": "the Cyc and CVQBoost handoff, 2026-10 (03-manifest-sources.json); F51, released 2026-11-05",
    "cited_as": "Maximizing Predictions from CVQBoost: Cumulative Findings",
    "checked_against_source": f"{TODAY}, Claude, read the whole document, sections 1 to 12, every table",
    "reads": [["Claude", TODAY, "full", READ]],
    "applicability": [
        ["platform:dirac-3", "How CVQBoost's QUBO parameters on Dirac-3 affect accuracy and metered cost -- section 3 "
                             "parameter table and section 4 cost table"],
        ["method", "How to recognize label leakage in a benchmark: identical, near-perfect models from both families "
                   "-- section 2"],
    ],
    "updated_reason": f"{TODAY}: added by scripts/sprint16_f51_cvqboost.py ({TAG}); read in full",
}

WHY = "one study's single run on Dirac-3 with a pinned seed (the document's own caveat: single stochastic runs)"


def A(note: str = "", **kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "HW")
    kw.setdefault("context", "platform:dirac-3")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw["certainty"], kw["certainty_reasons"] = low_grade("measured result", WHY if not note else f"{WHY}. {note}")
    kw["provenance"] = f"{RID}, {kw['provenance']}"
    return AssertionRecord(**kw)


ASSERTIONS = [
    A(id="cvqboost-ridge-must-scale-with-record-count",
      value=("CVQBoost's ridge coefficient lambda_coef is added to a QUBO diagonal of order n_records, so small values "
             "(0.1, 1, 10) are no-ops; on oilgas/target (N about 25,700) the sweep 0, 2,500, 25,000, 50,000, 100,000 "
             "improved overall AUROC 0.8817, 0.8837, 0.8878, 0.8885, 0.8887, monotonic but flattening, plateauing by "
             "about 2 to 4 times N; the document sets lambda_coef to about 2 x n_records per dataset"),
      provenance="section 3 parameter table",
      citation_context=(
          '"Ridge added to `J`\'s diagonal, which is of order `n_records`" (section 3); '
          '"Small values (0.1, 1, 10) are no-ops" (section 3); '
          '"On oilgas/target (N≈25,700) the sweep 0 -> 2,500 -> 25,000 -> 50,000 -> 100,000 improved overall AUROC '
          '0.8817 -> 0.8837 -> 0.8878 -> 0.8885 -> 0.8887" (section 3); '
          '"monotonic but flattening" (section 3); "overall plateaus by ~2-4x N" (section 3); '
          '"Use **≈ 2 x n_records**, scaled **per dataset**" (section 3)')),
    A(id="cvqboost-relaxation-schedule-4-no-gain-3-8x-cost",
      value=("On Dirac-3, raising CVQBoost's relaxation_schedule from 2 to 4 gave no measurable accuracy change but cost "
             "about 3.8 times more QPU per sample (oilgas/target)"),
      provenance="section 3 parameter table",
      citation_context=('"2 -> 4 gave **no measurable accuracy change** but cost ~3.8x more QPU per sample. Pure waste '
                        'here." (section 3)')),
    A(id="cvqboost-16-samples-no-better-than-8",
      value=("CVQBoost with num_samples 16 showed no discernible difference from 8 (8 was marginally better, within "
             "noise) at about half the QPU, since solve() keeps only the lowest-energy sample and driving QUBO energy "
             "lower does not improve generalization"),
      provenance="section 3 parameter table",
      citation_context=('"16 vs 8 -> **no discernible difference** (8 was marginally better, within noise) at ~half '
                        'the QPU. `solve()` keeps only the min-energy sample, and driving QUBO energy lower does not '
                        'improve generalization." (section 3)')),
    A(id="cvqboost-shallow-weak-learners-hurt",
      value=("Making CVQBoost's weak learners shallower (max_depth 2, 50 trees) cut overall AUROC from 0.8878 to 0.8391 "
             "on oilgas/target and turned its in-segment result back into a loss against XGBoost"),
      provenance="section 3 parameter table and section 9 run 7",
      note=("Its in-segment loss is against a win at the default configuration, the kind Phase 2's B4 (on the device) "
            "and F162 (a proxy) did not find"),
      citation_context=('"(`max_depth=2, n_estimators=50`) **hurt badly**: overall AUROC 0.8878 -> 0.8391, and '
                        'in-segment flipped back to a loss vs XGBoost." (section 3)')),
    A(id="cvqboost-in-segment-overfit-exceeds-xgboost",
      value=("On the tuned SPECTRA rollout, CVQBoost's in-segment ROC-AUC train-to-test gap exceeded XGBoost's on all "
             "four target cells: energy_steel 0.083 against 0.001, maintenance 0.389 against 0.051 (CVQBoost 0.981 "
             "train, 0.592 test), oilgas 0.212 against 0.026, telecom 0.135 against 0.080"),
      provenance="section 11 table",
      note=("The value states the table, not the section's summary: the summary says the gap is 3-8x XGBoost's on "
            "every target cell, but the table's ratios are about 83, 7.6, 8.2 and 1.7"),
      citation_context=('"0.978->0.895 (0.083) | 0.839->0.838 (0.001)" (section 11, energy_steel / target); '
                        '"0.981->0.592 (**0.389**) | 0.626->0.574 (0.051)" (section 11, maintenance_ai4i / target); '
                        '"0.880->0.668 (0.212) | 0.659->0.633 (0.026)" (section 11, oilgas_gasturbine / target); '
                        '"0.997->0.863 (0.135) | 0.869->0.789 (0.080)" (section 11, telecom_churn / target); '
                        '"i.e. CVQBoost is mostly memorizing there." (section 11)')),
    A(id="spectra-label-leak-signature-identical-perfect-models",
      value=("Using SPECTRA's target_real or in_pocket column as a feature when predicting target leaks the answer, with "
             "a recognizable signature: precision 1.000 and both models near-perfect and identical, because both copied "
             "the leaked column"),
      provenance="section 2",
      evidence_tag="N/A", context="method",  # scoped: the value leaves out the document's "(or vice versa)"
      citation_context=('"Using `target_real` (or `in_pocket`) as a feature when predicting `target` (or vice '
                        'versa) **leaks the answer**. Symptom: precision = 1.000, both models near-perfect and **identical** '
                        '(they just copied the leaked column)." (section 2)')),
]


def check_copies() -> list[str]:
    return [f"{p}: SHA-256 {h[:16]}..., not {SHA[:16]}..." for p in COPIES
            if (h := hashlib.sha256(p.read_bytes()).hexdigest()) != SHA]


def verify() -> list:
    text = plain(DOC.read_text(encoding="utf-8"))
    return [(a, require_verbatim(a.id, a.citation_context, text, value=a.value)) for a in ASSERTIONS]


def apply_changes(conn) -> list[str]:
    checked, log = verify(), []
    if conn.execute("SELECT 1 FROM records WHERE id = ?", (RID,)).fetchone() is None:
        insert_paper(conn, intake.build_record(ENTRY, today=TODAY))
        log.append(f"record {RID} [read]")
    else:  # the first apply's record, brought to the script's current evidence and route citation (fresh-eyes review)
        if conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?", (RID,)).fetchone()[0] \
                != ENTRY["evidence"]:
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?", (ENTRY["evidence"], RID))
            append_updated_reason(conn, RID, SYNC_REASON + ": evidence names B4 and F162 under their limits, and the "
                                  "file name as a label", TODAY)
            log.append(f"synced {RID}: evidence")
        if conn.execute("UPDATE paper_found_via SET cited_as = ? WHERE record_id = ? AND route = ? AND cited_as != ?",
                        (ENTRY["cited_as"], RID, ENTRY["found_via"], ENTRY["cited_as"])).rowcount:
            append_updated_reason(conn, RID, SYNC_REASON + ": the route cites the title, not a name-bearing id", TODAY)
            log.append(f"synced {RID}: cited_as")
    for a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            insert_verified_assertion(conn, a, verified, yielded_by=RID)
            log.append(f"assert {a.id} [{a.certainty}, {a.context}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, SYNC_REASON, TODAY)
        log.append(f"synced {a.id}: {', '.join(changed)}" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_copies()
    if bad:
        print("\n".join(bad))
        return 1
    checked = verify()
    if "--apply" not in args:
        intake.build_record(ENTRY, today=TODAY)  # validates the entry; nothing written
        for a, _ in checked:
            validate_assertion(a)
            print(f"assert {a.id} [{a.certainty}, {a.context}]")
        print(f"record {RID} [read]; every quote verbatim. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F51 CVQBoost findings record")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log) or "nothing to write")
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
