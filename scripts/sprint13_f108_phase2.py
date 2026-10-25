#!/usr/bin/env python3
"""Sprint 13 Task E (F108): Phase 2's later Sprint 28 work, by the inbound path.

Read at Phase 2 commit 9cbe5ba, the head of PR #46 (merged 2026-10-25) and
the commit current when the task started; no document under `docs/phase2/`
changed between 9993ab6 (the plan's) and 9cbe5ba. Read only (F79), through
`git show`, never a fetch. INTAKE_WORKFLOW.md section 50.

Two parts:

- F162, new: one reference record and 2 SIM assertions under `hsbc-2026`
  (section 43's rule: a result about the project's own CVQBoost lanes; the
  plan said `ml`). No relation is linked (ADR-0004 A8 (b)): F162 measures
  the proxy, not the device, so it confirms none of the stored pocket
  claims whole; each value or reason names the claims it bears on.
- The F102 values whose documents changed since 10086da, compared by name.
  Three no longer carry what their source says and are corrected here
  (CORRECTED); every other stored F102 value is confirmed by name in
  section 50. `scripts/sprint12_f102_phase2_sprint28.py` stays the record
  of the read at 10086da; its store test takes these three from this
  script.

Every quote is checked by `require_verbatim`, with the value, against the
blob at COMMIT before anything is written. DRY-RUN BY DEFAULT; `--apply`
takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_paper,  # noqa: E402
                          insert_verified_assertion, sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("f102", Path(__file__).with_name("sprint12_f102_phase2_sprint28.py"))
f102 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f102)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-25"
TAG = "Sprint 13 Task E, F108"
PHASE2 = f102.PHASE2
COMMIT = "9cbe5ba0f6946db550d6d8018bdb4ebb012130c8"
OWN = ("Started HIGH: the consumer project's own measurement, read directly at Phase 2 commit 9cbe5ba "
       "(PR #46, merged 2026-10-25)")
REASON = f"{TODAY} ({TAG}): extracted from hsbc-qfraud-phase2 at commit 9cbe5ba, read directly on {TODAY}"
SYNC_REASON = (f"{TODAY} ({TAG}): corrected against the document at 9cbe5ba, where Phase 2 changed what the "
               "stored value carried (INTAKE_WORKFLOW.md section 50)")
READ_DETAIL = "the whole document at commit 9cbe5ba, to compare the stored values with Phase 2's later edits (F108)"

# key -> (file, SHA-256 of the blob at COMMIT)
BLOBS = {
    "f110": ("docs/phase2/F110_SCALING.md", "b56a4d7c7f109d02cb3a3d0b68849cfa3f3c849b13b07add57a9ace96b53c81d"),
    "f111": ("docs/phase2/F111_LOKE_PROTOCOL.md", "94054fa6fbd89a892949bad13a04648fac3b6d610196589fabe36c6a5442f60f"),
    "f114": ("docs/phase2/F114_CALIBRATED_PLUGIN.md",
             "402651e4bb270a38b502a880d8cff80272509722d17d52eceb1d38989319c196"),
    "f162": ("docs/phase2/F162_IN_POCKET.md", "4eb4e2de8b358e960c1d59a15e112f86aad6ab420720bddffa883c239eaff087"),
}
F162_ID = "hsbc-qfraud-phase2-f162-sprint28-result"
F162_HEADING = "F162: Inside the SPECTRA Pocket, CVQBoost Proxy Against HGB and XGBoost"
F162_FIRST = "Sprint 28 Task M (#59)"


def source_bytes(key: str) -> bytes:
    """The document exactly as committed at COMMIT (a read: git show)."""
    return subprocess.run(["git", "-C", PHASE2, "show", f"{COMMIT}:{BLOBS[key][0]}"], capture_output=True,
                          check=True).stdout


def source_text(key: str) -> str:
    return plain(source_bytes(key).decode("utf-8").replace("**", ""))


def f162_entry() -> dict:
    file = BLOBS["f162"][0]
    return {
        "id": F162_ID, "kind": "reference", "context": "hsbc-2026", "tier": "read",
        "title": F162_HEADING,
        "citation": (f'hsbc-qfraud-phase2, "{F162_HEADING}," {file}, commit cbe3950, 2026-10-23; {F162_FIRST} '
                     "(hand-transcribed from the document's heading and first line and the repository's git log)"),
        "transcribed_from": f'the heading "{F162_HEADING}" and the line "{F162_FIRST}"',
        "disposition": ("Reference: the HSBC Phase 2 project's preregistered ten-seed test of its CVQBoost proxy "
                        "against HGB and XGBoost inside the SPECTRA pocket, on three cells"),
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {f102.REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 {BLOBS['f162'][1]} at Phase 2 commit 9cbe5ba (the last commit to "
                     "touch the file is cbe3950). Run: experiments/phase2/results/f162_in_pocket.json, seeds 42-51, "
                     "three cells. The private repository's URL is the citation's pointer; the record depends on the "
                     "commit. Read-only from this repository (F79)."),
        "found_via": "read from Phase 2 at Sprint 13 Phase 1.2, 2026-10-25 (carded as F108)",
        "cited_as": file,
        "checked_against_source": f"{TODAY}, Claude, read the whole document at commit 9cbe5ba via git show",
        "reads": [["Claude", TODAY, "full", "the whole document at commit 9cbe5ba"]],
        "applicability": [["hsbc-2026", "the CVQBoost proxy against HGB and XGBoost inside the SPECTRA pocket -- "
                                        "Bottom line and Results"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint13_f108_phase2.py ({TAG}); read in full",
    }


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "SIM")
    kw.setdefault("context", "hsbc-2026")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "high")
    kw["provenance"] = f"{F162_ID}, {kw['provenance']}"
    return AssertionRecord(**kw)


F162 = [
    A(id="f162-cvqboost-proxy-not-above-classical-in-spectra-pocket",
      value=("Inside the SPECTRA pocket, over ten seeds (42-51) on three cells, Phase 2's CVQBoost proxy was not "
             "reliably better than HGB or XGBoost on any cell, so the entry's falsifier fires on all three. Where a "
             "difference was reliable the proxy was below: XGBoost beat it on energy_steel (by 0.024 AUPRC, "
             "p = 0.0020) and oilgas_gasturbine (by 0.011, p = 0.0059), under the family level 0.0083. Against HGB "
             "on energy_steel the proxy was lower by 0.020 with an interval excluding zero, but p = 0.0098 is above "
             "0.0083, so the rule reads no reliable difference. On telecom_churn the proxy was ahead on average "
             "(+0.013 against HGB, p = 0.16; +0.033 against XGBoost, p = 0.049), not reliably; the pocket holds 46 "
             "to 58 frauds per seed, and Phase 2 infers that a telecom-only entry with more seeds would decide it. "
             "Over the whole test set, outside the pocket too, the proxy is below both classical models on every "
             "cell. Phase 2: nothing here justifies a device run. Its limits: XGBoost at library defaults, one "
             "proxy configuration, the proxy and not the device, the label target only"),
      provenance="Bottom line, Results, Reading and Limits",
      citation_context=('"The proxy is not reliably better than either classical model inside the pocket on any '
                        'cell." (Bottom line, markdown bold dropped); "so the entry\'s falsifier fires on all three '
                        'cells" (Bottom line); "Ten seeds (42-51)" (Results); "XGBoost beats the proxy on '
                        'energy_steel (by 0.024 AUPRC, Wilcoxon p = 0.0020) and on oilgas_gasturbine (by 0.011, '
                        'p = 0.0059), both under the family level 0.0083" (Bottom line); "Proxy minus HGB +0.013 '
                        '(p = 0.16), proxy minus XGBoost +0.033 (p = 0.049); both intervals span zero." (Bottom '
                        'line); "proxy minus HGB: -0.020, p = 0.0098, [-0.036, -0.003]. No reliable difference '
                        'under the rule: the interval excludes zero but the Wilcoxon p is above 0.0083." (Results, '
                        'markdown bold dropped); "The pocket holds 46 to 58 frauds per seed." (Bottom line); '
                        '"Inferred: a telecom-only entry (m = 2, more seeds) is what would decide it" (Reading, '
                        'markdown bold dropped); "Label `target` only." (Limits, markdown bold dropped); '
                        '"Overall, the proxy is below both classical models on every cell" (Reading, '
                        'markdown bold dropped); "For a device run: nothing here justifies one." (Bottom line, '
                        'markdown bold dropped); "XGBoost at library defaults" (Limits, markdown bold dropped); '
                        '"One proxy configuration" (Limits, markdown bold dropped); "The proxy, not the device." '
                        '(Limits, markdown bold dropped)'),
      certainty_reasons=(OWN + ". HIGH for the measured in-pocket comparisons under the entry's rule. Scope: three "
                         "cells, ten seeds, the proxy and not Dirac hardware. Bears on "
                         "dirac3-matches-classical-proxy-in-pocket-spectra-b4, "
                         "cvqboost-in-segment-edge-negative-on-device-spectra-b4 and "
                         "cvqboost-device-below-classical-bar-spectra-b4 (device results on the same cells); not "
                         "linked (ADR-0004 A8 (b)): a proxy result confirms none of them whole")),
    A(id="f162-fourierwall2-single-run-pocket-wins-do-not-repeat",
      value=("FourierWall2's single run had Phase 2's CVQBoost proxy above XGBoost in the SPECTRA pocket on all "
             "three cells (+0.091, +0.018, +0.021 AUPRC). Over ten seeds, two of those three reverse reliably and "
             "the third is not reliable. Phase 2 infers that one stochastic run sits inside the seed-to-seed "
             "spread; not ruled out: FourierWall2's XGBoost settings and split differ from Phase 2's and are not "
             "on record"),
      provenance="Bottom line",
      citation_context=('"The FourierWall2 single-run wins do not repeat." (Bottom line, markdown bold dropped); '
                        '"That run had the proxy above XGBoost in the pocket on all three cells (+0.091, +0.018, '
                        '+0.021 AUPRC" (Bottom line); "Over ten seeds, two of those three reverse reliably and the '
                        'third is not reliable." (Bottom line); "Inferred: one stochastic run sits inside the '
                        'seed-to-seed spread." (Bottom line, markdown bold dropped); "The leading alternative not '
                        'ruled out: FourierWall2\'s XGBoost settings and split differ from ours, and are not on '
                        'record here." (Bottom line)'),
      certainty_reasons=(OWN + ". HIGH for the measured ten-seed reversal; why the single run differed is Phase 2's "
                         "inference, attributed as such. Bears on "
                         "fourier-wall-incomplete-bar-manufactures-advantage (an in-pocket advantage that a fuller "
                         "classical bar removes); not linked (ADR-0004 A8 (b)): a different model and bar")),
]


def _corrected(aid: str, value: str, old_quote: str, new_quotes: str) -> tuple[str, AssertionRecord]:
    key, a = next((k, x) for k, x in f102.ASSERTIONS if x.id == aid)
    if old_quote not in a.citation_context:
        raise ValueError(f"{aid}: the quote to replace is not in the stored context")
    reasons = a.certainty_reasons.replace(f102.OWN, OWN)
    return key, dataclasses.replace(a, value=value, citation_context=a.citation_context.replace(old_quote, new_quotes),
                                    certainty_reasons=reasons, updated=TODAY, updated_reason=SYNC_REASON)


_f110 = next(a for _, a in f102.ASSERTIONS if a.id == "f110-proxy-solve-flat-paper-2s-not-like-for-like")
_f114 = next(a for _, a in f102.ASSERTIONS if a.id == "f114-calibrated-plugin-misses-known-ceiling")
_f111 = next(a for _, a in f102.ASSERTIONS
             if a.id == "f111-cvqboost-knn-lane-below-published-value-under-loke-protocol")

# The three F102 values Phase 2 changed underneath, each against the document at COMMIT.
CORRECTED: list[tuple[str, AssertionRecord]] = [
    _corrected("f110-proxy-solve-flat-paper-2s-not-like-for-like",
               _f110.value.replace(
                   "at 91 variables the solve took 0 to 4 ms and could not be read (9 of 20 below the timer's "
                   "resolution)",
                   "at 91 variables the solve took 0 to 4 ms after subtracting a separately timed J build and could "
                   "not be read: 9 of 20 solves clamp, because the J build came out longer than the whole call (Phase "
                   "2 first blamed the timer's resolution; corrected 2026-10-23)"),
               '"At 91 variables it takes 0 to 4 ms, and 9 of 20 solves are below the timer\'s resolution." (BLUF)',
               '"At 91 variables it takes 0 to 4 ms after subtraction, and 9 of 20 solves clamp" (BLUF); "the J '
               'build came out longer than the whole call" (BLUF); "(Corrected 2026-10-23, PR review: this '
               'paragraph first blamed the timer\'s resolution, which is far finer than these times.)" (BLUF)'),
    _corrected("f114-calibrated-plugin-misses-known-ceiling",
               _f114.value.replace(
                   "every seed overestimated the Bayes error by about 3% to 13%, and calibration moved the estimate "
                   "by less than 0.0002.",
                   "every estimate was above the Bayes error, the calibrated by about 3% to 13% and the uncalibrated "
                   "by about 4% to 14%; on the main arm calibration moved the estimate by less than 0.0002, and on "
                   "the other two arms it moves some estimates."),
               '"Every seed\'s estimate is above the Bayes error, by about 3% to 13%" (Results, markdown bold '
               'dropped)',
               '"Every estimate is above the Bayes error: calibrated by about 3% to 13%, uncalibrated by about 4% '
               'to 14%" (Results, markdown bold dropped); "On the main arm, calibration did not move the estimate" '
               '(BLUF); "On the other two arms it does move some estimates" (BLUF)'),
    _corrected("f111-cvqboost-knn-lane-below-published-value-under-loke-protocol",
               _f111.value.replace("(range 0.683-0.829)", "(range 0.683-0.828)"),
               '"KNN lane AUC-PR: A mean 0.760 (range 0.683-0.829)"',
               '"KNN lane AUC-PR: A mean 0.760 (range 0.683-0.828)"'),
]


# The fresh-eyes review of 88bd065: the three corrected values quote text their paper records did not point at
# (access, evidence and checked_against_source named 10086da). Each is repointed at COMMIT, the earlier read kept in
# the evidence. Every other stored quote from these three documents is verbatim at COMMIT too (that review ran
# require_verbatim on all 9).
LAST_COMMIT = "28bdbcd"
REPOINT_NOTE = (f"{TODAY} ({TAG}): access, evidence and checked_against_source repointed at Phase 2 commit 9cbe5ba, "
                "where the corrected values are read (the fresh-eyes review of 88bd065; INTAKE_WORKFLOW.md section 50)")
F162_REVIEW = (f"{TODAY} ({TAG}): the value carries the energy_steel HGB case, the frauds per seed, the inferred "
               "telecom-only entry and the label limit, and says what \"overall\" covers (the fresh-eyes review of "
               "88bd065)")


def repointed(key: str) -> dict[str, str]:
    file, _, old_sha, _, _, run, _, _ = f102.DOCS[key]
    return {
        "access": f"{PHASE2}\\{file.replace('/', chr(92))} | {f102.REPO_URL}/blob/{COMMIT}/{file}",
        "evidence": (f"Committed blob SHA-256 {BLOBS[key][1]} at Phase 2 commit 9cbe5ba (the last commit to touch "
                     f"the file is {LAST_COMMIT}). Run: {run}. Read first on 2026-10-23 at commit 10086da (blob "
                     f"SHA-256 {old_sha}); re-read whole on {TODAY} at 9cbe5ba after Phase 2 changed it, and the "
                     "stored values corrected or confirmed by name (F108). The private repository's URL is the "
                     "citation's pointer; the record depends on the commit. Read-only from this repository (F79)."),
        "checked_against_source": f"{TODAY}, Claude, read the whole document at commit 9cbe5ba via git show",
    }


def check_hashes() -> list[str]:
    return [f"{k}: blob at {COMMIT[:7]} has changed" for k, (_, sha) in BLOBS.items()
            if hashlib.sha256(source_bytes(k)).hexdigest() != sha]


def verify_all() -> list:
    """Every quote verbatim in its document at COMMIT BEFORE anything is
    written (INTAKE_WORKFLOW.md sections 26, 31 and 41)."""
    texts = {k: source_text(k) for k in BLOBS}
    return ([("f162", a, require_verbatim(a.id, a.citation_context, texts["f162"], value=a.value)) for a in F162]
            + [(k, a, require_verbatim(a.id, a.citation_context, texts[k], value=a.value)) for k, a in CORRECTED])


def apply_changes(conn) -> list[str]:
    checked = verify_all()
    log = []
    if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (F162_ID,)).fetchone() is None:
        insert_paper(conn, f102.intake.build_record(f162_entry(), today=TODAY))
        log.append(f"paper  {F162_ID}")
    for key in sorted({k for k, _ in CORRECTED}):
        rid = f102.src_id(key)
        if not conn.execute("SELECT 1 FROM paper_reads WHERE record_id = ? AND read_on = ? AND detail = ?",
                            (rid, TODAY, READ_DETAIL)).fetchone():
            add_read(conn, rid, "Claude", TODAY, "full", READ_DETAIL)
            log.append(f"read   {rid}")
        want = repointed(key)
        row = conn.execute("SELECT access, evidence, checked_against_source FROM paper_fields WHERE record_id = ?",
                           (rid,)).fetchone()
        if tuple(row) != (want["access"], want["evidence"], want["checked_against_source"]):
            conn.execute("UPDATE paper_fields SET access = ?, evidence = ?, checked_against_source = ? "
                         "WHERE record_id = ?", (want["access"], want["evidence"], want["checked_against_source"], rid))
            append_updated_reason(conn, rid, REPOINT_NOTE, TODAY)
            log.append(f"repoint {rid}")
    for key, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            insert_verified_assertion(conn, a, verified, yielded_by=F162_ID)
            log.append(f"assert {a.id}")
        else:
            changed = sync_verified_assertion(conn, a, verified, F162_REVIEW if key == "f162" else SYNC_REASON,
                                              TODAY)
            if changed:
                log.append(f"synced {a.id}: {', '.join(changed)}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_hashes()
    if bad:
        print("\n".join(bad))
        return 1
    if "--apply" not in args:
        f102.intake.build_record(f162_entry(), today=TODAY)  # validates the entry; nothing written
        print(f"paper  {F162_ID} [read]")
        for key, a, _ in verify_all():
            validate_assertion(a)
            print(f"{'assert' if key == 'f162' else 'correct'} {a.id} [{a.certainty}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F108 Phase 2 later Sprint 28 work")
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
