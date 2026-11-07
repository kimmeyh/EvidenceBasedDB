#!/usr/bin/env python3
"""Sprint 16 Task G (F57, Q2 = 2, Q3 = 1): the two papers the team lead named, entered at `seen` through the door
so Task F reads them as two of its 20. INTAKE_WORKFLOW.md section 72.

- the QBoost regression paper, arXiv 2108.13346 (v1, the only version), api-origin;
- the wangy8205165 white paper `Quantum_NeuralNetwork.pdf`, hand-origin (it has no DOI or arXiv id), linked to its
  repository record by a `code-of` source link: the repository holds the paper's LaTeX source and the PDF.

The entries are `manifests/sprint16_f57_named.json`; each runs through `scripts/intake.py`'s `build_record`, as a
`--manifest` run would. The link and the repository record's note are the two things the door does not do.

    python scripts/sprint16_f57_named.py           # dry run
    python scripts/sprint16_f57_named.py --apply   # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_source_link, append_updated_reason, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

ROOT, DB_PATH, _ = script_paths(__file__)
MANIFEST = ROOT / "manifests" / "sprint16_f57_named.json"
TODAY = "2026-11-06"
TAG = "Sprint 16 Task G, F57"
REPO = "wangy8205165-quantum-neuralnetwork-whitepaper-github-repo"
WHITE_PAPER = "wangy8205165-2026-quantum-neural-networks-theory-architectures"
LINK_EVIDENCE = ("The repository holds the white paper's LaTeX source, Quantum_NeuralNetwork.tex, and its PDF, "
                 "Quantum_NeuralNetwork.pdf (git blob 8f800932c0 at commit 920c11c, 2026-10-26), which is the paper "
                 "record's local copy (listed 2026-11-06)")


def entries() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


_spec103 = importlib.util.spec_from_file_location("f103", Path(__file__).with_name("sprint12_f103_intake.py"))
f103 = importlib.util.module_from_spec(_spec103)
_spec103.loader.exec_module(f103)
# The repository record is F103's; its disposition is held in one place, there (its test checks the store against it)
REPO_DISPOSITION = f103.repo_entry()["disposition"]
if WHITE_PAPER not in REPO_DISPOSITION:
    raise ValueError("sprint12_f103_intake.py's repository disposition does not name the white paper record")


def held(conn, entry: dict) -> str | None:
    """The record that already holds the entry, found by its id or by its first access item, so a re-run sends no
    metadata request and a provider's different id cannot enter the paper twice (fresh-eyes review)."""
    key = entry["access"].split(" | ", 1)[0]
    row = conn.execute("SELECT record_id FROM paper_fields WHERE record_id = ? OR access = ? OR access LIKE ?",
                       (entry.get("id", ""), key, f"{key} |%")).fetchone()
    return row[0] if row else None


def apply_changes(conn, apply: bool) -> list[str]:
    log = []
    for entry in entries():
        if rid := held(conn, entry):
            log.append(f"exists {rid}")
            continue
        paper = intake.build_record(entry, today=TODAY)
        if apply:
            insert_paper(conn, paper)
        log.append(f"paper  {paper.id} [{paper.tier}, {paper.citation_origin}]  {paper.value[:60]}")
    if not conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = 'code-of'",
                        (REPO, WHITE_PAPER)).fetchone():
        if apply:
            add_source_link(conn, REPO, WHITE_PAPER, "code-of", LINK_EVIDENCE)
            append_updated_reason(conn, REPO, f"{TODAY} ({TAG}): its white paper entered as {WHITE_PAPER}, linked "
                                  "code-of; the disposition's 'linked to no paper' no longer holds", TODAY)
        log.append(f"link   {REPO} code-of {WHITE_PAPER}")
    if conn.execute("SELECT disposition FROM paper_fields WHERE record_id = ?", (REPO,)).fetchone()[0] \
            != REPO_DISPOSITION:
        if apply:
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (REPO_DISPOSITION, REPO))
            append_updated_reason(conn, REPO, f"{TODAY} ({TAG}): disposition corrected: its white paper is now "
                                  f"entered and linked ({WHITE_PAPER})", TODAY)
        log.append(f"disposition {REPO}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    why = intake.unrecorded_manifest(MANIFEST)
    if apply and why:
        print(why)
        return 1
    if apply:
        backup_before_write(DB_PATH, "F57 named papers entered")
    conn = connect(DB_PATH)
    try:
        log = apply_changes(conn, apply)
        if apply:
            conn.commit()
        else:
            conn.rollback()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
