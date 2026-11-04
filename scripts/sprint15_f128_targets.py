#!/usr/bin/env python3
"""Sprint 15 Task J (F128): the reading targets for the gaps F118's memo found
(`docs/spikes/F118_WHAT_THE_STORE_SAYS.md`). INTAKE_WORKFLOW.md section 63.

Each target with a free arXiv copy is fetched by F104's paced fetcher into `Papers\\` and entered through the door
(`scripts/intake.py`) at `seen`, naming the gap it fills; F114's readers then read it in full under Sprint 15's
prompt. A target with no free copy (a book, a paywalled paper, vendor documentation) goes on the hand-download list
with its reason (`HAND`), never fetched from a site that is not its publisher.

    python scripts/sprint15_f128_targets.py --fetch   # arXiv metadata and PDFs, 18 s apart
    python scripts/sprint15_f128_targets.py           # dry run: nothing written to the store
    python scripts/sprint15_f128_targets.py --apply   # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("f104", Path(__file__).with_name("sprint12_f104_roadmap.py"))
f104 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f104)

ROOT, DB_PATH = f104.ROOT, f104.DB_PATH
TODAY = "2026-11-01"
TAG = "Sprint 15 Task J, F128"
MANIFEST = ROOT / "manifests" / "sprint15_f128_targets.json"
MEMO = "docs/spikes/F118_WHAT_THE_STORE_SAYS.md"
f104.API_CACHE = Path(r"D:\Data\Harold\EvidenceBasedDB\References") / "sprint15_f128_arxiv_api"

# arXiv id -> (context, the gap it fills)
TARGETS = {
    "1905.09749": ("qc", "qubit counts per use case: Gidney and Ekera's resource estimate for RSA-2048, to settle the "
                         "store's conflicting RSA-2048 figures"),
    "2011.03494": ("qc", "qubit counts per use case: a primary chemistry resource estimate (Lee et al., tensor "
                         "hypercontraction)"),
    "1806.06893": ("qc", "qubit counts per use case and an amplitude-estimation risk model: Woerner and Egger"),
    "2012.03819": ("qc", "fault-tolerant resource estimates: Chakrabarti et al. on derivative pricing"),
    "2011.04149": ("qc", "fault-tolerant resource estimates: Babbush et al. 2021, 'Focus beyond quadratic speedups'"),
    "1605.05775": ("qml", "tensor-network classifiers: Stoudenmire and Schwab"),
    "1603.02754": ("ml", "production-scale timing: XGBoost's scaling sections"),
    "2305.10310": ("qc", "QRAM feasibility and cost: a critical review beyond those already stored"),
}
# Held already, with a local copy, under another access: never fetched again. The bucket-brigade QRAM architecture
# (0708.1879) is held under its PRL DOI; the 2026-11-01 run fetched it once before this was known, and that copy was
# deleted (INTAKE_WORKFLOW.md section 63).
HELD = {"0708.1879": "giovannetti-2008-quantum-random-access-memory"}
# No free copy found by this script: the hand-download list, each with why.
HAND = {
    "LightGBM (Ke et al., NeurIPS 2017)": "production-scale timing: LightGBM's scaling sections; not on arXiv, the "
                                          "proceedings PDF is the publisher's",
    "Ferrari Dacrema et al., quantum feature selection": "penalty weights for a cardinality constraint and a tuned "
                                                         "feature-selection comparison; cited by "
                                                         "dacrema-comparison-cited, not in the store",
    "Nielsen and Chuang, Quantum Computation and Quantum Information": "gate theory: a book",
    "Vendor native-gate documentation (IBM, IonQ, Quantinuum)": "native gate sets: vendor pages, current versions",
    "A concept-drift and delayed-label source for card fraud": "drift and delayed labels: no source chosen yet",
    "Tuned anomaly-detection baselines on fraud (isolation forest, LOF, one-class SVM)": "no source chosen yet",
    "Dal Pozzolo et al. 2014, Learned lessons in credit card fraud detection": "stored, unread "
        "(dal-pozzolo-2014-learned-lessons-credit-card-fraud); Elsevier, DOI only, no local copy",
}


def entry(ident: str) -> dict:
    ctx, gap = TARGETS[ident]
    out = f104.entry(ident, (MEMO, f"arxiv.org/abs/{ident}"))
    out.update(context=ctx, disposition=f"A reading target for a gap F118 found ({gap}); not yet read",
               found_via=f"F118 memo ({MEMO}), F128", cited_as=f"arxiv.org/abs/{ident}",
               updated_reason=f"{TODAY}: added by scripts/sprint15_f128_targets.py ({TAG})")
    if out.get("evidence"):
        out["evidence"] = out["evidence"].replace(f104.TODAY, TODAY)
    return out


def held(conn) -> set[str]:
    text = f104.held_text(conn)
    return {i for i in TARGETS if i in text}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    f104.TODAY = TODAY
    fetcher = f104.CachedFetcher()
    conn = connect(DB_PATH)
    try:
        have = held(conn)
    finally:
        conn.close()
    todo = [i for i in TARGETS if i not in have]
    if "--fetch" in args:
        return 1 if f104.fetch_papers(todo, fetcher) else 0
    missing = [i for i in todo if f104.arxiv_file(i) is None]
    if missing:
        print(f"no local copy (run --fetch): {missing}")
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F128 gap reading targets")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    entered = []
    try:
        for ident in todo:
            record = f104.intake.build_record(entry(ident), fetcher=fetcher, today=TODAY)
            # Held under another access (Giovannetti et al. under its PRL DOI): read from the copy saved here.
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (record.id,)).fetchone():
                have.add(f"{ident} as {record.id}")
                print(f"held   {record.id} (arXiv:{ident}, under another access)")
                continue
            if apply:
                insert_paper(conn, record)
            entered.append({"arxiv": ident, "record_id": record.id, "local_copy": f104.arxiv_file(ident).name,
                            "gap": TARGETS[ident][1]})
            print(f"paper  {record.id} [seen]  {record.value[:70]}")
        if apply:
            conn.commit()
    finally:
        conn.close()
    record_entered(entered, have, apply)
    print("APPLIED" if apply else "DRY RUN: nothing written to the store. Re-run with --apply.")
    return 0


def record_entered(entered: list[dict], have: set[str], apply: bool, path: Path = MANIFEST) -> None:
    # Only an apply writes the manifest, and it adds to what an earlier apply entered: a dry run listed records the
    # store did not hold, and a later apply replaced the list j_records reads (fresh-eyes review, 2026-11-02).
    if not (entered and apply):
        return
    earlier = json.loads(path.read_text(encoding="utf-8"))["entered"] if path.exists() else []
    known = {e["record_id"] for e in entered}
    entered = [e for e in earlier if e["record_id"] not in known] + entered
    path.write_text(json.dumps({"release": TAG, "on": TODAY, "entered": entered, "held_before": sorted(have),
                                "hand_download": HAND}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
