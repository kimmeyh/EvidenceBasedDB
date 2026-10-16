#!/usr/bin/env python3
"""Sprint 9 Task F (F46): the 20 remaining pending facts, each checked against
its primary source and entered, merged or refused with the reason.

The facts are from the October handoff
(`Handoff-2026-10\\ebdb-handoff\\07-assertion-candidates-pending.md`): World
(F-001 to F-008), Entanglement (F-402), the April 2026 claim (F-501 to F-504)
and Classical fraud (F-601 to F-607). They were written from second-hand
reads, so none is entered in its handoff wording: each source was read and
only what it supports is asserted.

HOW THE SOURCES WERE READ, as Task E (ADR-0005 A4: a subagent's read alone
never qualifies `read`): three Sonnet 5.5 first-pass readers
(`manifests/sprint9_f46_reads/group_*.json`, kept verbatim), then the
coordinator read each source's opening and every quoted passage in context.
Zhao et al. was read in part even at first pass (main text and theorem in
full; the 130-page appendix searched), and its absence assertion carries that
search as its scope.

QUOTE_FIX replaces six quotes whose reader extraction differed from the
coordinator's (a hyphen split, spaces before superscripts, the "ffi"
ligature) with verbatim spans of the same passage. CERTAINTY follows Task E's
GRADE mapping (scripts/sprint9_f78_ceiling_reading.py). DRY-RUN BY DEFAULT;
`--apply` takes a verified backup first. Idempotent; a changed value or read
detail is corrected in place with the reason.
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
from store.ingest import AssertionRecord, add_read, append_updated_reason, insert_assertion, set_tier  # noqa: E402

_spec = importlib.util.spec_from_file_location("f78", Path(__file__).with_name("sprint9_f78_ceiling_reading.py"))
f78 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f78)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-15"
TAG = "Sprint 9 Task F, F46"
READS_DIR = ROOT / "manifests" / "sprint9_f46_reads"
GROUPS = "ghi"

SUBAGENT_READER = f78.SUBAGENT_READER
SUBAGENT_DETAIL = {
    "g": "first pass, the whole paper (Sonnet 5.5 reader, group G)",
    "h": "first pass, the whole source (Sonnet 5.5 reader, group H)",
    "i": "first pass, the whole source (Sonnet 5.5 reader, group I)",
}

QUOTE_FIX = {  # (assertion id, reader's quote) -> verbatim span in the coordinator's extraction
    ("faryad-state-prep-omega-2n-dimension-count",
     "The argument is a dimension count. The target manifold of normalized states has 2n+1 − 2 real parameters."):
        "The argument is a dimension count.",
    ("faryad-quantum-kernel-gram-theta-m2-preparations",
     "On M training points this is Θ(M 2 ) state preparations to fill the Gram matrix, each with its own circuit and "
     "its own shot budget."):
        "On M training points this is Θ(M 2) state preparations to fill the Gram matrix, each with its own circuit and "
        "its own shot budget.",
    ("howard-psim-equals-nonnegative-discrete-wigner-states",
     "By prior results34,39 , we know that the set of states PSIM coincides exactly with the set of states that are "
     "nonnegatively represented within a distinguished quasiprobability representation—a discrete Wigner function "
     "(DWF)40–42 ."):
        "By prior results34,39, we know that the set of states PSIM coincides exactly with the set of states that are "
        "nonnegatively represented within a distinguished quasiprobability representation",
    ("howard-contextuality-not-sufficient-qubits-open-for-qudits",
     "For qubits, the mere presence of contextuality cannot be sufficient to promote stabilizer circuits to "
     "universality"):
        "For qubits, the mere presence of contextuality cannot be",
    ("howard-contextuality-not-sufficient-qubits-open-for-qudits",
     "While substantial progress in this direction has been made18 , it is still an open problem."):
        "While substantial progress in this direction has been made18, it is still an open problem.",
    ("howard-stabilizer-subtheory-efficiently-simulable",
     "These operations define a closed subtheory of quantum theory, the stabilizer subtheory, which is not universal "
     "and in fact admits an efficient classical simulation30 ."):
        "These operations define a closed subtheory of quantum theory, the stabilizer subtheory, which is not "
        "universal and in fact admits an",
}

REMOVE = {  # (exact text, replacement); figures restated in the source's own form
    "blog-300-qubits-every-atom-comparison": [("post of 2026-04-09", "post of April 9, 2026")],
    "ieee-cis-uid-from-card1-addr1-d1": [("divided by 86400", "divided by 24*60*60")],
    "tabpfn-v2-degrades-on-f1-balanced-accuracy-majority-bias": [(
        " and use the phrase statistically significant without showing a test in the main text", "")],
}

FACT_DISPOSITIONS = {
    "F-001": ("not entered", [], "the Holevo bound needs its 1973 paper or a textbook; the handoff's stated "
                                 "restatement does not exist (Faryad 2026 never mentions Holevo)"),
    "F-002": ("entered", ["faryad-state-prep-omega-2n-dimension-count"],
              "stated with a dimension-count sketch for a fixed continuous-parameter gate set"),
    "F-003": ("entered, corrected", ["faryad-generic-data-loading-theta-n-with-preprocessing",
                                     "faryad-qae-9p6e9-gates-vs-1e10-samples"],
              "Theta(N) is for generic data only; the 9.6e9 figure is an extrapolation, not a measurement"),
    "F-004": ("entered", ["faryad-quantum-kernel-gram-theta-m2-preparations"], "stated in prose, without proof"),
    "F-005": ("entered, corrected", ["chowdhury-gottesman-knill-restated-stabilizer-simulable",
                                     "chowdhury-non-stabilizer-resource-called-magic",
                                     "howard-contextuality-necessary-for-msd-speedup",
                                     "howard-contextuality-not-sufficient-qubits-open-for-qudits"],
              "contextuality is proved necessary for magic, not equivalent to it; neither paper mentions interference"),
    "F-006": ("entered, corrected", ["ortiz-2design-visible-observables-near-maximally-mixed",
                                     "ortiz-volume-law-predictions-no-better-than-random",
                                     "ortiz-lipschitz-gradient-bound-scales-with-hidden-dimension",
                                     "ortiz-area-law-tolerable-but-not-shown-gradient-preserving"],
              "the paper assumes 2-design behavior and derives that volume law is typical (the fact had the direction "
              "reversed); the decay is in hidden units; the area-law threshold claim is not shown"),
    "F-007": ("entered (Task E)", ["boyd-theorem2-min-aucpr-formula"], "Boyd read in full; the closed form is Theorem 2"),
    "F-008": ("not entered", [], "the 'vacuous at 0.17 percent' part is the handoff's own arithmetic (H(Y) about "
                                 "0.018 bits), and the generalization it calls for (Han and Verdu 1994) is not "
                                 "obtainable (team lead, 2026-10-16); per Q6 = 1 its content is entered from free "
                                 "sources (scarlett-fano-data-processing-form-holds-for-any-prior and "
                                 "chen-2016-bayes-risk-lower-bounds); Scarlett's binary remark assumes a uniform label "
                                 "(fano-binary-case-uses-exact-form-not-simplified)"),
    "F-402": ("merged", ["qelm-local-dynamics-match-haar-classically-simulable"],
              "De Lorenzis was already read directly and yields the same judgement; nothing re-entered"),
    "F-501": ("entered, corrected", ["zhao-thm3-classification-space-separation", "zhao-thm-f11-formal-classification",
                                     "zhao-runtime-dominated-by-data-loading"],
              "the fact dropped the O~(N) sample count and the condition under which loading is unavoidable"),
    "F-502": ("entered", ["zhao-separation-reaches-ultimate-limit"],
              "'memory-restricted' is a fair consequence, not the paper's word"),
    "F-503": ("entered", ["zhao-fewer-than-60-logical-qubits", "zhao-extrapolation-ignores-runtime-overhead",
                          "zhao-no-300-qubit-universe-atom-claim", "blog-300-qubits-every-atom-comparison",
                          "blog-universe-scale-caveat"],
              "the absence is scoped to the extracted text and a stated search"),
    "F-504": ("entered, corrected", ["markidis-compiled-circuits-too-deep", "markidis-offline-loses-size-advantage"],
              "'too deep' is for the author's offline variant, on one synthetic DNA case"),
    "F-601": ("entered, corrected", ["ieee-cis-uid-from-card1-addr1-d1",
                                     "ieee-cis-uid-aggregates-local-auc-0-9363-to-0-9472",
                                     "ieee-cis-uid-column-not-used-in-training"],
              "the blog never calls day - D1 the account-open date; 0.9363 and 0.9472 are local validation; the "
              "count 45 is not stated"),
    "F-602": ("entered in part", ["ieee-cis-final-score-public-0-9677-private-0-9459"],
              "the 0.9677 and 0.9459 leaderboard scores are the final ensemble's; the naive 0.88 to 0.90 range has no "
              "source here and is not entered"),
    "F-603": ("not entered", [], "the benchmark repository behind the temporal-split numbers was never identified"),
    "F-604": ("merged", ["oversampling-helps-weak-not-strong-boosters"],
              "Elor was already read directly and yields the same statement"),
    "F-605": ("entered, corrected", ["leaky-smote-mlp-reaches-99-9-recall-european-card-data",
                                     "leak-in-case-study-is-smote-before-split",
                                     "minimal-leaky-network-outperforms-published-methods-claim"],
              "the 99.9 percent recall is a deliberate leakage demonstration (SMOTE before the split), compared with "
              "other papers' reported numbers"),
    "F-606": ("entered, corrected", ["full-graph-features-may-include-future-edges",
                                     "look-ahead-leakage-can-inflate-metrics-claim"],
              "stated conditionally and never measured; no clustering coefficients; Elliptic data, not card data"),
    "F-607": ("entered, corrected", ["tabpfn-v2-suited-small-covariate-shifted-balanced-tasks",
                                     "tabpfn-v2-degrades-on-f1-balanced-accuracy-majority-bias",
                                     "open-env-average-rank-catboost-best-tabpfn-v2-third",
                                     "tabpfn-v2-dataset-size-limit-background-and-50k-subsample",
                                     "tabpfn-2-5-win-rate-against-default-xgboost",
                                     "tabpfn-2-5-also-claims-to-beat-tuned-trees-with-fewer-configs"],
              "the 10^4-row limit is background or a recommendation, not a cap; TabPFN-2.5 also claims wins over tuned "
              "trees, so 'default XGBoost only' was wrong"),
}


def load_groups() -> list[tuple[str, dict]]:
    out = []
    for g in GROUPS:
        data = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))
        out += [(g, p) for p in data["papers"]]
    return out


def edited_value(aid: str, value: str) -> str:
    for old, new in REMOVE.get(aid, []):
        if old not in value:
            raise ValueError(f"{aid}: the text to remove is not in the reader's value: {old[:60]!r}")
        value = value.replace(old, new)
    return " ".join(value.split())


def quotes(aid: str, raw: list[str]) -> list[str]:
    return [QUOTE_FIX.get((aid, q), q) for q in raw]


def assertions() -> list[tuple[str, AssertionRecord, str]]:
    out = []
    for g, p in load_groups():
        rid = p["record_id"]
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            cert, reasons = f78.certainty(aid, a["kind"], a.get("certainty_suggestion", ""), False,
                                          a.get("certainty_reason", ""))
            absence = a.get("claim_type") == "absence"
            out.append((g, AssertionRecord(
                id=aid, value=edited_value(aid, a["value"]), provenance=f"{rid}, {a['anchor']}",
                citation_context="; ".join(f'"{q}" ({a["anchor"]})' for q in quotes(aid, a["quotes"])),
                evidence_tag="N/A", context=a.get("context") or "ml", certainty=cert, certainty_reasons=reasons,
                fidelity=a.get("fidelity") or "scoped", derivation="extracted",
                claim_type="absence" if absence else "positive",
                search_scope=(a.get("search_scope") if absence else None),
                updated=TODAY, updated_reason=f"{TODAY} ({TAG}): extracted from {rid}; first-pass read by a subagent, "
                                              "every quoted passage read in context by the coordinator"), rid))
    return out


def sha_note(path: str) -> str:
    data = Path(path).read_bytes()
    return f"Local copy SHA-256 {hashlib.sha256(data).hexdigest()}, {len(data):,} bytes, recorded {TODAY} (F46)"


def apply_changes(conn) -> list[str]:
    log = []
    for g, p in load_groups():
        rid = p["record_id"]
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        local = p["file"].replace("/", "\\")
        if not recheck.local_paths(access or ""):
            conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (f"{access} | {local}", rid))
            note = sha_note(local)
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?",
                         (f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): local copy added to access", TODAY)
            log.append(f"access {rid} += {local}")
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            ctx = next((a.get("context") for a in p["assertions"] if a.get("context")), "ml")
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, f"{p['what_it_is'].rstrip('.')} -- abstract"))
            log.append(f"applic {rid} [{ctx}]")
        partial = p.get("read_extent") == "partial"
        sub_detail = (f"first pass, in part: {p['partial_detail']} (Sonnet 5.5 reader, group {g.upper()})"
                      if partial else SUBAGENT_DETAIL[g])
        coord = (f78.COORDINATOR_DETAIL_PAGE.replace("the handbook's Foreword", "the blog post")
                 if p["file"].lower().endswith(".html") and "quantumfrontiers" in rid else f78.COORDINATOR_DETAIL)
        have = {(r[0], r[1], r[2]) for r in conn.execute(
            "SELECT reader, read_on, extent FROM paper_reads WHERE record_id = ?", (rid,))}
        for reader, extent, detail in ((SUBAGENT_READER, "subagent", sub_detail), ("Claude", "partial", coord)):
            if (reader, TODAY, extent) not in have:
                add_read(conn, rid, reader, TODAY, extent, detail)
                log.append(f"read   {rid} [{reader}, {extent}]")
        if tier != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{TODAY}, Claude, read the opening and every quoted passage in context; first pass by a subagent"))
            log.append(f"tier   {rid} -> read")
    for g, a, rid in assertions():
        stored = conn.execute("SELECT value, certainty, certainty_reasons FROM records WHERE id = ?",
                              (a.id,)).fetchone()
        if stored and tuple(stored) != (a.value, a.certainty, a.certainty_reasons):
            conn.execute("UPDATE records SET value = ?, certainty = ?, certainty_reasons = ? WHERE id = ?",
                         (a.value, a.certainty, a.certainty_reasons, a.id))
            append_updated_reason(conn, a.id, f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
            log.append(f"update {a.id}")
            continue
        if stored:
            log.append(f"exists {a.id}")
            continue
        insert_assertion(conn, a, yielded_by=rid)
        log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kept = assertions()
    if len({a.id for _, a, _ in kept}) != len(kept):
        print("duplicate assertion ids")
        return 1
    if "--apply" not in args:
        for _, a, rid in kept:
            print(f"assert {a.id} <- {rid} [{a.certainty}, {a.claim_type}]")
        print(f"{len(kept)} assertions. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F46 pending facts checked and entered")
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
