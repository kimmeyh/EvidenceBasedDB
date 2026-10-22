#!/usr/bin/env python3
"""Sprint 11 Task D (F93): Phase 2's F108 ceiling validation, entered by the inbound path.

hsbc-qfraud-phase2's `docs/phase2/F108_CEILING_VALIDATION.md` (Sprint 27
Task K, 2026-10-18), read directly on 2026-10-22 at Phase 2 commit eef3349,
the last commit touching the file (Phase 2's HEAD dbfa4da holds the same
blob that day). Phase 2 built a fraud simulator whose Bayes error is known
exactly and tested four ceiling methods against it on five seeds.

Four SIM assertions under `ml`. Certainty as in Sprint 10's F85: the
consumer project's own measurement, read directly, starts HIGH, each value
carrying Phase 2's own limits (one simulator, five seeds, causes inferred
and unverified). The verdict is MODERATE: Phase 2 states that what
"validated" means was read after the run, and under the entry as written
the plug-in passes two arms. Relations: none is linked (ADR-0004 A8 (b)).
The learning-curve result agrees with `ding-floor-c-is-model-and-config-
specific` but confirms only its "per model" half, so the value names it
instead.

Every quote is checked by `require_verbatim` against the file as committed
at COMMIT before anything is written, and written only through the
verified write path (intake sections 26 and 31);
`tests/test_f93_f108_ceiling.py` checks the same. Markdown bold is dropped
first. DRY-RUN BY DEFAULT; `--apply` takes a verified backup first.
Idempotent.
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
from store.ingest import (AssertionRecord, insert_paper, insert_verified_assertion,  # noqa: E402
                          sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
TAG = "Sprint 11 Task D, F93"
PHASE2 = r"D:\Data\Harold\github\hsbc-qfraud-phase2"
COMMIT = "eef334917a24322cfa683059c462ea54452bfb88"
FILE = "docs/phase2/F108_CEILING_VALIDATION.md"
SHA256 = "828693e0aa79e0be64fff7201ef71f6824a9c1dd535deb487f19082a06766033"
REPO_URL = "https://github.com/kimmeyh/hsbc-qfraud-phase2"
RUN = ("Sprint 27 Task K (F108), 2026-10-18, seeds 42-46; rows experiments/phase2/results/f108_ceiling.json, "
       "pilot f108_ceiling_pilot.json")
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit eef3349, read directly on {TODAY}"
SRC = "hsbc-qfraud-phase2-f108-ceiling-validation"


def source_bytes() -> bytes:
    """The document exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{FILE}"], capture_output=True, check=True).stdout


def source_text() -> str:
    return source_bytes().decode("utf-8")


SOURCE = {
    "id": SRC, "kind": "reference", "context": "hsbc-2026", "tier": "read",
    "title": "F108: ceiling validation on a simulator with hidden state",
    "citation": ('hsbc-qfraud-phase2, "F108: ceiling validation on a simulator with hidden state," '
                 "docs/phase2/F108_CEILING_VALIDATION.md, commit eef3349, 2026-10-18; Sprint 27 Task K "
                 "(hand-transcribed from the document's heading and first line and the repository's git log)"),
    "transcribed_from": "the heading \"F108: ceiling validation on a simulator with hidden state\" and the line "
                        "\"Sprint 27 Task K, 2026-10-18\"",
    "disposition": ("Reference: the HSBC Phase 2 project's test of four ML ceiling methods against a fraud "
                    "simulator whose Bayes error is known exactly (five seeds); none recovered the ceiling on the "
                    "main arm"),
    "access": f"{PHASE2}\\docs\\phase2\\F108_CEILING_VALIDATION.md | {REPO_URL}/blob/{COMMIT}/{FILE}",
    "evidence": (f"Working copy SHA-256 {SHA256} (the committed blob at eef3349, the last commit to touch the file; "
                 f"Phase 2's HEAD dbfa4da held the same blob on {TODAY}), which the local-file check compares "
                 f"against, so it reports any later edit in Phase 2. Run: {RUN}. The card (F93) was written "
                 "against eef3349. The private repository's URL is the citation's pointer; the record depends on "
                 "the commit. Read-only from this repository (F79)."),
    "found_via": "read from Phase 2 at Sprint 11 Phase 1.4, 2026-10-21 (carded as F93)",
    "cited_as": "docs/phase2/F108_CEILING_VALIDATION.md",
    "checked_against_source": f"{TODAY}, Claude, read the whole document at commit eef3349 via git show",
    "reads": [["Claude", TODAY, "full", "the whole document at commit eef3349"]],
    "applicability": [
        ["ml", "four ML ceiling methods tested against a simulator's known Bayes error -- BLUF and Results"],
        ["hsbc-2026", "Phase 2's ceiling work (F114) and its HGB baselines -- Reading and What follows"],
    ],
    "updated_reason": f"{TODAY}: added by scripts/sprint11_f93_f108_ceiling.py ({TAG}); read in full",
}

OWN = ("Started HIGH: the consumer project's own measurement on its own simulator, read directly at Phase 2 "
       "commit eef3349")


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "SIM")
    kw.setdefault("context", "ml")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    return AssertionRecord(**kw)


ASSERTIONS: list[AssertionRecord] = [
    A(id="f108-no-ceiling-method-recovered-known-ceiling",
      value=("On Phase 2's fraud simulator, whose Bayes error is known exactly (the Bayes classifier's realized "
             "error within 0.00002 of it on every seed), no ceiling method recovered the known ceiling on the "
             "main, no-noise arm in the required 4 of 5 seeds: the HGB plug-in on 2 of 5, the learning-curve "
             "floor on error 1 of 5, the AUPRC floor 1 of 5, the Cover-Hart interval 3 of 5. Phase 2 states that "
             "the rule requiring the main arm was read after the run; under the entry as written the plug-in "
             "meets 4 of 5 on the noise arm (5 of 5) and on the reference arm (5 of 5), the reference pass only "
             "through the absolute margin. One simulator, five seeds"),
      provenance=f"{SRC}, BLUF and Results; {RUN}",
      citation_context=('"No ceiling method recovered the known ceiling on the main, no-noise arm, so none is '
                        'validated for real data" (BLUF, markdown bold dropped); "Bayes error to within 0.00002" '
                        '(BLUF); "2 of 5 within the 10% margin" (Results, main arm, markdown bold dropped); '
                        '"learning-curve floor on error 0.0064-0.0071: 1 of 5" (Results, main arm, markdown bold '
                        'dropped); "against 0.296-0.318: 1 of 5" (Results, main arm, markdown bold dropped); '
                        '"Cover-Hart interval: 3 of 5" (Results, main arm, markdown bold dropped); "The entry needs '
                        '4 of 5." (BLUF); "means here was read after the run" (BLUF, markdown bold dropped); "the '
                        'plug-in meets 4 of 5 on the noise arm (5 of 5) and on the reference arm (5 of 5)" (BLUF); '
                        '"plug-in 5 of 5, but only through the absolute margin" (Results, zero-ceiling reference)'),
      certainty="moderate",
      certainty_reasons=(OWN + ". MODERATE for the verdict: Phase 2 states the rule that requires the main arm was "
                         "read after the run, and the plug-in passes the other two arms under the entry as written")),
    A(id="f108-hgb-plugin-overstates-bayes-error-5-to-12-percent",
      value=("On Phase 2's simulator (main labels, no noise, fraud rate 0.83% in the test window), the HGB plug-in "
             "estimate of the Bayes error was 0.0064-0.0070 against the true 0.0060-0.0063, ratios 1.053 to 1.118: "
             "it overstates the Bayes error by 5-12%. The three misses fall 0.5-1.8 points past the 10% margin, "
             "so the verdict turns on that margin. Phase 2 infers the gap is the model's: the fitted model is "
             "about 10% short of the posterior on the error scale"),
      provenance=f"{SRC}, BLUF, The world, Results and Reading; {RUN}",
      citation_context=('"the HGB plug-in overstates the Bayes error by 5-12%" (BLUF); "three misses are by 0.5-1.8 '
                        'points past the 10% margin, so the verdict turns on that margin" (BLUF); "main-label fraud '
                        'rate 0.83% in the test window" (The world); "plug-in 0.0064-0.0070 against 0.0060-0.0063, '
                        'ratios 1.053, 1.097, 1.105, 1.114 and 1.118" (Results, main arm); "the model is about 10% '
                        'short of the posterior on the error scale" (Reading)'),
      certainty_reasons=(OWN + ". HIGH for the measured overstatement; the cause is Phase 2's inference and is "
                         "attributed as such. Scope: one simulator, five seeds")),
    A(id="f108-auprc-learning-curve-floor-tracks-the-model",
      value=("On Phase 2's simulator the learning-curve floor fitted to AUPRC recovered the known ceiling on 1 of "
             "5 seeds on the main arm: it gave 0.255-0.312 on four seeds and 0.87 on seed 43 (true 0.300), and "
             "it understates the attainable AUPRC by about 0.04 and is unstable. The full-data HGB reached "
             "0.250-0.268, so the floor mostly tracked the model, not the ceiling. Phase 2: not usable as "
             "specified, a three-parameter fit to six points at extreme imbalance being ill-conditioned"),
      provenance=f"{SRC}, Results and Reading; {RUN}",
      citation_context=('"against 0.296-0.318: 1 of 5" (Results, main arm, markdown bold dropped); "ceiling '
                        '0.255-0.312 on four seeds" (Results, main arm); "and 0.87 on seed 43 (true 0.300)" (Results, '
                        'main arm); "the AUPRC floor understates the attainable AUPRC by about 0.04 and is unstable" '
                        '(BLUF); "The full-data HGB reaches 0.250-0.268, so the '
                        'floor mostly tracks the model, not the ceiling." (Results, main arm); "The AUPRC floor is not '
                        'usable as specified." (Reading, markdown bold dropped); "A three-parameter fit to six points '
                        'at extreme imbalance is ill-conditioned" (Reading)'),
      certainty_reasons=(OWN + ". Scope: one simulator, five seeds. Consistent with "
                         "ding-floor-c-is-model-and-config-specific (the floor is per model); not linked, as this "
                         "confirms only its per-model half (ADR-0004 A8 (b))")),
    A(id="f108-default-hgb-misses-rare-sharp-threshold",
      value=("On Phase 2's zero-ceiling reference label (fraud if and only if amount > 220, the top 0.05% of "
             "amounts), default HGB reached AUPRC 0.008-0.026 where the Bayes AUPRC is 1.0. Phase 2's cause, "
             "inferred and not verified: the 255 quantile bins put the threshold inside one bin, possibly "
             "compounded by early stopping on so few positives. Whether the positives of Phase 2's real-data HGB "
             "baselines contain such a threshold is unverified"),
      provenance=f"{SRC}, Results (HGB fails the reference) and Reading; {RUN}",
      citation_context=('"fraud iff amount > 220" (Results, zero-ceiling reference); "default HGB reaches AUPRC '
                        '0.008-0.026 where the Bayes AUPRC is 1.0" (Results, HGB fails the reference); "The positives '
                        'are the top 0.05% of amounts." (Results); "Cause, Inferred and not verified: the 255 quantile '
                        'bins put the threshold inside one bin, possibly compounded by early stopping on so few '
                        'positives." (Results); "Whether their positives contain such a threshold is Unverified" '
                        '(Reading, markdown bold dropped)'),
      certainty_reasons=(OWN + ". HIGH for the measured AUPRC; the cause and the transfer to real data are Phase 2's "
                         "inference, stated as unverified, and are attributed as such")),
]


def verify_all() -> list:
    """Every quote verbatim in the document at COMMIT BEFORE anything is
    written (INTAKE_WORKFLOW.md sections 26 and 31). Markdown bold is
    dropped first, as each quote that crosses it says."""
    text = plain(source_text().replace("**", ""))
    return [(a, require_verbatim(a.id, a.citation_context, text)) for a in ASSERTIONS]


def apply_changes(conn) -> list[str]:
    checked = verify_all()
    log = []
    if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (SRC,)).fetchone() is None:
        insert_paper(conn, intake.build_record(SOURCE, today=TODAY))
        log.append(f"paper  {SRC} [read]")
    else:
        log.append(f"exists {SRC}")
    for a, verified in checked:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=SRC)
            log.append(f"assert {a.id} <- {SRC} [{a.certainty}, {a.evidence_tag}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, f"{TODAY} ({TAG}): corrected to the script's current "
                                          "text", TODAY)
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
        for a, _ in verify_all():
            validate_assertion(a)  # the checks insert_assertion runs; nothing written
            print(f"assert {a.id} <- {SRC} [{a.certainty}, {a.evidence_tag}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F93 Phase 2 F108 ceiling validation")
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
