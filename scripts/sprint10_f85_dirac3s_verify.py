#!/usr/bin/env python3
"""Sprint 10 Task G (F85): Phase 2's Dirac-3S verification, entered by the inbound path.

hsbc-qfraud-phase2's `docs/phase2/F142_DIRAC3S_VERIFY.md` (Sprint 26 Task
D, five Dirac-3S fits on 2026-10-14 and 2026-10-15), read directly on
2026-10-18 at Phase 2 commit e126dbd, the last commit touching the file
(the same blob at Phase 2's HEAD 98f9671 that day). The card (F85) was
written against c141a57; the document was revised after it (PR #21
review), so this script reads the current text, not the card's summary.

Four HW assertions under platform:dirac-3s. Certainty as in Sprint 9's
inbound trial: the consumer project's own hardware measurement, read
directly, starts HIGH; each value carries Phase 2's own limits (two fits
for the twin, descriptive not a test; the post-processing cause inferred
and unverified; three sizes for cost). Relations: none is linked. A8 (b)
links `supports` only when a whole claim is confirmed and `contradicts`
only when both cannot hold. The returned weights' fineness concerns
OUTPUT values, while the guide's 200:1 is about INPUT coefficients; the
post-processing explanation is Phase 2's inference; the guide's time per
sample is for 50 variables, Phase 2's for 91, 560 and 833. Each value
names the related assertion instead.

Every quote is checked by `tests/test_f85_dirac3s_verify.py` against the
file as committed at COMMIT. DRY-RUN BY DEFAULT; `--apply` takes a
verified backup first. Idempotent; a re-apply syncs every field.
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
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
TAG = "Sprint 10 Task G, F85"
PHASE2 = r"D:\Data\Harold\github\hsbc-qfraud-phase2"
COMMIT = "e126dbd97b3a3335d0e4fcc7c41df52ba0b63a8f"
FILE = "docs/phase2/F142_DIRAC3S_VERIFY.md"
# The file as committed at COMMIT (LF); the working copy hashed the same on TODAY.
SHA256 = "2c2fa0b577d8e818541bf80e3cf01f95364395fac63d60810c512cf0a4cb605c"
REPO_URL = "https://github.com/kimmeyh/hsbc-qfraud-phase2"
RUN = ("Sprint 26 Task D (F142), stops 1 to 3, 2026-10-14 and 2026-10-15; rows "
       "experiments/phase2/results/f142_dirac3s_verify.json, readout experiments/phase2/results/f142_readout.json")
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit e126dbd, read directly on {TODAY}"
SRC = "hsbc-qfraud-phase2-f142-dirac3s-verify"


def source_bytes() -> bytes:
    """The document exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{FILE}"], capture_output=True, check=True).stdout


def source_text() -> str:
    return source_bytes().decode("utf-8")


SOURCE = {
    "id": SRC, "kind": "reference", "context": "hsbc-2026", "tier": "read",
    "title": "F142: The First Dirac-3S Fits, Cost and a B4 Twin",
    "citation": ('hsbc-qfraud-phase2, "F142: The First Dirac-3S Fits, Cost and a B4 Twin," '
                 "docs/phase2/F142_DIRAC3S_VERIFY.md, commit e126dbd, 2026-10-17; run 2026-10-14 and 2026-10-15, "
                 "Sprint 26 Task D (hand-transcribed from the document's heading and first line and the repository's "
                 "git log)"),
    "transcribed_from": "the heading \"F142: The First Dirac-3S Fits, Cost and a B4 Twin\" and the line "
                        "\"Sprint 26 Task D, 2026-10-14 and 2026-10-15\"",
    "disposition": ("Reference: the HSBC Phase 2 project's first Dirac-3S hardware result: five fits (B1, B2 for cost; "
                    "B4 twin on two seeds) against reference QP solves, with per-sample cost at relaxation schedule 2"),
    "access": f"{PHASE2}\\docs\\phase2\\F142_DIRAC3S_VERIFY.md | {REPO_URL}/blob/{COMMIT}/{FILE}",
    "evidence": (f"Working copy SHA-256 {SHA256} (as checked out on {TODAY}; the committed blob at e126dbd hashes the "
                 "same), which the local-file check compares against, so it reports any later edit in Phase 2. A "
                 "living document in an active repository: this record cites commit e126dbd (2026-10-17), the last "
                 f"to touch the file; Phase 2's HEAD 98f9671 held the same blob on {TODAY}. Run: {RUN}. The card (F85) "
                 "was written against c141a57 (2026-10-15); the PR #21 review revised the document after it. The "
                 "private repository's URL is the citation's pointer; the record depends on the commit. Read-only "
                 "from this repository (F79)."),
    "found_via": "Phase 2's share-back, 2026-10-15 (Sprint 9 Manual Validation Q5 = 2: carded as F85)",
    "cited_as": "docs/phase2/F142_DIRAC3S_VERIFY.md",
    "checked_against_source": f"{TODAY}, Claude, read the whole document at commit e126dbd via git show",
    "reads": [["Claude", TODAY, "full", "the whole document at commit e126dbd"]],
    "applicability": [
        ["hsbc-2026", "Phase 2's own Dirac-3S hardware test of its CVQBoost twin and its cost -- the whole document"],
        ["platform:dirac-3s", "Dirac-3S returned weights, their fineness, accuracy and per-sample cost against "
                              "reference solves -- Bottom line items 1 to 6"],
    ],
    "updated_reason": f"{TODAY}: added by scripts/sprint10_f85_dirac3s_verify.py ({TAG}); read in full",
}

OWN = "Started HIGH: the consumer project's own hardware measurement, read directly at Phase 2 commit e126dbd"


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "HW")
    kw.setdefault("context", "platform:dirac-3s")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    return AssertionRecord(**kw)


ASSERTIONS: list[AssertionRecord] = [
    A(id="dirac3s-returned-b4-reference-optimum-two-seeds",
      value=("On Phase 2's B4 twin (CVQBoost, oilgas_gasturbine, 560 variables), Dirac-3S returned the reference QP "
             "optimum in every sample: weight cosine 0.999993 and 0.9999999 on seeds 42 and 43, the same in all 8 "
             "samples of each job, against Dirac-3's 0.895 and 0.901, both outside the band [0.8832, 0.9095] set "
             "before the call. Phase 2 calls this descriptive, not a test (2 fits); the Dirac-3 figures come from "
             "different, unseeded pools, and seed 42's cosine is limited by the reference solve, not the device"),
      provenance=f"{SRC}, Bottom line items 1 and 5; {RUN}",
      citation_context=('"On B4, Dirac-3S returned the reference optimum in every sample; Dirac-3 did not." '
                        '(Bottom line 1, markdown bold dropped); "0.999993 and 0.9999999 on seeds 42 and 43, the same '
                        'in all 8 samples of each job, against Dirac-3\'s 0.895 and 0.901." (Bottom line 1); '
                        '"With 2 fits this is descriptive, not a test." (Bottom line 1); "Seed 42\'s 0.999993 is '
                        'limited by the reference, not the device." (Bottom line 5)'),
      certainty_reasons=(OWN + ". Scope: two fits on one dataset; the source itself says descriptive, not a test. "
                         "Same project as the Dirac-3 rows compared, so not independent")),
    A(id="dirac3s-returned-weights-finer-than-0005-step",
      value=("On Phase 2's B4 twin every Dirac-3S weight was within 0.000094 (seed 42) and 0.0000062 (seed 43) of the "
             "reference, far finer than the 0.005 output step Phase 2 had derived from 200:1; samples agreed to "
             "0.0000005 or better on all five jobs and every value sat on a 0.0000001 grid. Phase 2 infers a "
             "post-processing step (such as normalization, or QCi's stated error correction) rather than an analog "
             "output resolution of 1 part in 10 million, and marks the cause unverified. The guide's 200:1 "
             "(dirac3s-analog-resolution-about-200-to-1) concerns input coefficients, which this does not test"),
      provenance=f"{SRC}, Bottom line item 3 and the introduction's 'Two kinds of resolution'; {RUN}",
      citation_context=('"The returned weights are far finer than the 0.005 output step." (Bottom line 3, markdown '
                        'bold dropped); "every returned value on all five jobs is a multiple of 0.0000001" (Bottom '
                        'line 3); "these weigh toward post-processing" (Bottom line 3); "Unverified which." (Bottom '
                        'line 3, markdown bold dropped)'),
      certainty_reasons=(OWN + ". HIGH for the measured fineness only; the cause is Phase 2's inference, stated as "
                         "unverified, and is not asserted here")),
    A(id="dirac3s-b4-twin-auprc-unchanged",
      value=("On the same seeded pools, Phase 2's reference solve and Dirac-3S scored the same B4 test AUPRC: 0.85224 "
             "and 0.85225 (seed 42), 0.84180 and 0.84180 (seed 43); both devices stay far below the random control "
             "(0.974-0.976). Phase 2: it does not make CVQBoost better"),
      provenance=f"{SRC}, Bottom line item 4 and 'What this changes'; {RUN}",
      citation_context=('"On the same seeded pools, the reference solve and the device score the same test AUPRC: '
                        '0.85224 and 0.85225 (seed 42), 0.84180 and 0.84180 (seed 43)" (Bottom line 4); "Both devices '
                        'remain far below the random control (0.974-0.976), as in Phase 1." (Bottom line 4); "It does '
                        'not make CVQBoost better." (What this changes, markdown bold dropped)'),
      certainty_reasons=OWN + ". Scope: two seeds, one dataset", context="hsbc-2026"),
    A(id="dirac3s-time-per-sample-schedule-2-by-size",
      value=("Phase 2 measured Dirac-3S per-sample time at relaxation schedule 2 as about 0.75 s at 91 variables, "
             "2.6 s at 560 and 3.83 s at 833, with billed seconds equal to the per-sample times summed and rounded "
             "up on every job where both were recorded (4 of 5). Three sizes, one or two fits each, late-night "
             "queues; not a rate for other schedules. The guide's own figure for schedule 2 "
             "(dirac3s-time-per-sample-by-schedule) is for a smaller problem, without pre- and post-processing, so "
             "the two are not the same measurement"),
      provenance=f"{SRC}, Bottom line item 6 and 'What this changes'; {RUN}",
      citation_context=('"Per sample at relaxation schedule 2: about 0.75 s at 91 variables, 2.6 s at 560 and 3.83 s '
                        'at 833." (Bottom line 6); "Billed seconds equal the per-sample run times summed and rounded up '
                        'on every job where both were recorded (4 of 5; stop 1 predates the timing field)" (Bottom '
                        'line 6); "Three sizes, one or two fits each; not a rate for other schedules." (What this '
                        'changes)'),
      certainty_reasons=OWN + ". Scope: three sizes, one or two fits each, every queue taken late at night"),
]


def apply_changes(conn) -> list[str]:
    log = []
    if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (SRC,)).fetchone() is None:
        insert_paper(conn, intake.build_record(SOURCE, today=TODAY))
        log.append(f"paper  {SRC} [read]")
    else:
        log.append(f"exists {SRC}")
    for a in ASSERTIONS:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_assertion(conn, a, yielded_by=SRC)
            log.append(f"assert {a.id} <- {SRC} [{a.certainty}, {a.evidence_tag}]")
            continue
        changed = sync_assertion(conn, a, f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
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
            print(f"assert {a.id} <- {SRC} [{a.certainty}, {a.evidence_tag}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F85 Phase 2 Dirac-3S verification")
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
