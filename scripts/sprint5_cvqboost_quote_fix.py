#!/usr/bin/env python3
"""Sprint 5 Manual Validation, decision Q6 (team lead, 2026-09-25: "add the
row it rests on").

`cvqboost-vs-xgboost-auc-under-balancing` supports the F28 learning that
tabular QML shows no reliable gain: XGBoost leads in 23 of 24 rows of
Table 3. Its citation_context (Sprint 4 Task H) is the vendor's summary
sentence, "comparable accuracy ... can even exceed", which read the other
way under a SUPPORTS line. The sentence is KEPT; the table rows the claim
names are ADDED after it.

Rows read 2026-09-25 from emami-2025 p.14, Table 3, whose text extraction
keeps the columns in order (24 strategy labels, the ratio column 0.01 0.02
0.05 0.1 0.5 1.0 per strategy, then the CVQBoost and XGBoost columns). The
QCi profiling report prints the same values on p.11, but its `-layout`
rendering misaligns the labels and was not used to assign rows.

DRY RUN BY DEFAULT; `--apply` takes a verified backup (F30), commits,
regenerates export/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import append_updated_reason  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-09-25"
ID = "cvqboost-vs-xgboost-auc-under-balancing"
ROWS = (" | The rows the claim rests on, Table 3 (emami-2025 p.14; same values in qci-2024-profiling p.11): "
        "ADASYN, ratio 0.01: CVQBoost AUC 0.7105 +/- 0.0, XGBoost AUC 0.9003 +/- 0.0; "
        "ADASYN, ratio 1.0: CVQBoost AUC 0.8855 +/- 0.0019, XGBoost AUC 0.8826 +/- 0.0 "
        "(the only one of the 24 rows in which CVQBoost leads)")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "cvqboost quote fix --apply")
    conn = connect(DB_PATH)
    try:
        conn.execute("BEGIN")
        old = conn.execute("SELECT citation_context FROM assertion_fields WHERE record_id = ?", (ID,)).fetchone()[0]
        if ROWS in old:
            raise SystemExit("already applied")
        conn.execute("UPDATE assertion_fields SET citation_context = ? WHERE record_id = ?", (old + ROWS, ID))
        append_updated_reason(conn, ID, f"{TODAY} (Sprint 5 Manual Validation Q6): added the Table 3 rows the claim "
                                        "rests on after the vendor's summary sentence, which is kept", TODAY)
        print(f"NEW citation_context:\n{old + ROWS}")
        if not apply:
            conn.execute("ROLLBACK")
            print("PLANNED (dry run; rolled back). Re-run with --apply.")
            return 0
        conn.execute("COMMIT")
        print("COMMITTED")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
