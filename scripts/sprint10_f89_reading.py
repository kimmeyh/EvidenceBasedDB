#!/usr/bin/env python3
"""Sprint 10 Task I (F89, the F57 release for Sprint 10): the 74-record slice read and entered.

The slice (`manifests/sprint10_f89_slice.json`) is the 74 most-cited `qml`
records with no read row. 65 have a free copy (local, or fetched by
`scripts/sprint10_f89_downloads.py`); nine have none (NO_COPY) and stay
`seen` with that reason, for the hand-download list at Manual Validation.
Nine Sonnet 5.5 first-pass readers read the 65 (`manifests/sprint10_f89_reads/
group_r1.json` to `group_r9.json`, kept verbatim) under the protocol F88
tightened: a reader's own conclusions go in `reader_inference`, never in a
value.

HOW THE SOURCES WERE READ (ADR-0005 A4: a subagent's read alone never
qualifies `read`): the coordinator checked every quote against the source
text and every figure in a value against the full text by script, then
read every value against its quoted passages with about 220 characters each
side (2026-10-18). That read changed what QUOTE_EDITS, VALUE_EDITS,
CONTEXT_FIX and REFUSE record, and checked three figures the readers asked
about (Aimeur's n^(3/2), Jager's O(kn^3), Willsch's bias wording).

CERTAINTY follows the store's GRADE mapping as Tasks E and G used it
(`sprint9_f78_ceiling_reading.py`, `sprint9_f80_reading.py`): a result
proved in the paper, or the paper's own statement of its setup, scope or
limits, starts HIGH; an empirical result from one study starts LOW and is
not upgraded; an author's claim, or a claim the source cites from other
work, starts LOW; a vendor's description of its own product starts MODERATE
and a vendor's result LOW. No admission-against-interest upgrade is made.

DRY-RUN BY DEFAULT; `--apply` takes a verified backup first, after every
quote is checked (INTAKE_WORKFLOW.md section 26). Idempotent; a re-apply
syncs every assertion field.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, add_read, append_updated_reason, insert_assertion, set_tier,  # noqa: E402
                          sync_assertion)
from store.quotes import plain, require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("f80", Path(__file__).with_name("sprint9_f80_reading.py"))
f80 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f80)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-18"
TAG = "Sprint 10 Task I, F89"
READS_DIR = ROOT / "manifests" / "sprint10_f89_reads"
GROUPS = tuple(f"r{i}" for i in range(1, 10))
SUBAGENT_READER = f80.SUBAGENT_READER

COORDINATOR_DETAIL = ("every quoted passage with about 220 characters each side, every quote checked verbatim and "
                      "every figure in a value checked against the full text by script; the rest of the paper not "
                      "read by the coordinator" + f80.f78.ABSENCE_NOTE)

NO_COPY = {  # no free copy known to OpenAlex or found by an arXiv title search, 2026-10-18
    "schuld-2018-supervised-learning-quantum-computers": "a Springer book; no free copy",
    "li-2020-quantum-deep-convolutional-neural-network": "IOP, closed; no arXiv version found by title",
    "narayanan-2000-quantum-artificial-neural-network-architectures": "Elsevier, closed; no arXiv version found",
    "aimeur-2006-machine-learning-quantum-world": "Springer conference paper, closed; no arXiv version found",
    "ruan-2017-quantum-algorithm-k-nearest-neighbors": "Springer, closed; no arXiv version found by title",
    "aimeur-2007-quantum-clustering-algorithms": "ACM, closed; no arXiv version found by title",
    "duan-2020-survey-hhl-algorithm-theory-application": "Elsevier, closed; no arXiv version found by title",
    "panella-2011-neural-networks-quantum-architecture-quantum": "Wiley, closed; no arXiv version found by title",
    "valdez-2023-retracted-article-review-quantum-computing": ("Springer, a RETRACTED article (title); no free copy "
                                                              "listed by OpenAlex"),
}
REFUSE = {  # read at first pass and NOT entered
    "kaur-2022-defining-quantum-workforce-landscape-review": (
        "a review of quantum education and the job market (QURECA); it bears on no context of this store, and its "
        "job-market counts are not mathematics or physics, so they are not filed under world"),
}

# Exact source characters the readers' quotes missed (an em dash or a minus
# sign typed as a hyphen), or a stray square-root glyph inside the span.
QUOTE_EDITS = {
    "qperceptron-sublinear-in-data-points": [(
        "The first algorithm exploits quantum information processing to determine a separating hyperplane using a "
        "number of steps sublinear in the number of data points N",
        "using a number of steps sublinear in the number of data points N")],
    "cerezo-bp-free-models-classically-simulable": [("evidence--on a case-by-case basis--that",
                                                     "evidence—on a case-by-case basis—that")],
    "quadratic-ode-lower-bound-strong-nonlinearity": [
        ("We also provide a lower bound on the worst-case complexity of quantum algorithms for general quadratic "
         "differential equations, showing that the problem is intractable for",
         "for general quadratic differential equations, showing that the problem is intractable for R ≥ 2"),
        ("Whereas there is an efficient quantum algorithm for R < 1 (as shown in Theorem 1), we show here that the "
         "problem is intractable for",
         "for R < 1 (as shown in Theorem 1), we show here that the problem is intractable for R ≥ 2")],
    "dwave-mps-extrapolation-millions-of-years": [("applies to MPS--the only", "applies to MPS—the only"),
                                                  ("quench times--and is", "quench times—and is")],
    "qrnn-outclassed-by-classical-rnns": [("models--even simple RNNs--outclass", "models—even simple RNNs—outclass")],
    "qrnn-dna-task-training-steps-vs-lstm": [("steady increase--starting", "steady increase—starting")],
    "zuchongzhi-vqe-f2-above-chemical-accuracy": [("around 10-2 to 10-1", "around 10−2 to 10−1")],
    "schuld-kernel-training-scaling-and-small-scale-speed": [("with 10 - 20 parameters", "with 10 − 20 parameters")],
}
EXTRA_QUOTES = {
    "aimeur-mst-quantum-optimal-n32": ["can build the minimum spanning tree of a graph in Θ(n3/2) time, where n is "
                                       "the number of vertices of the graph"],
    "qgnn-pr-auc-085": ["and the false positive rate (FPR) for the GraphSAGE model"],
}
VALUE_REPLACE = {  # the coordinator's read; each replacement says only what its quotes say
    "aimeur-mst-quantum-optimal-n32": (
        "The paper states that the quantization of Boruvka's algorithm due to Durr et al. (2004) builds a minimum "
        "spanning tree in Theta(n^(3/2)) time, n the number of vertices, and that this is optimal: for a complete "
        "graph no quantum algorithm can find the minimum spanning tree in less than Omega(n^(3/2)) time."),
    "qgnn-pr-auc-085": (
        "The authors state the precision-recall AUC for the QGNN is estimated to be roughly 0.85; for the GraphSAGE "
        "model they report an AUC of 0.77 from its true positive and false positive rates (a ROC curve)."),
}
CONTEXT_FIX = {  # an assertion's context where the reader's did not fit
    "qumolgan-scope-qm9": "qml",
    "sagingalieva-hyperparameters-chosen-on-test-set": "qml",
    "krenn-review-scope-selective": "qml",
}
VENDOR_DESCRIPTIONS = {"pennylane-core-feature-autodiff-hybrid", "pennylane-gradient-method-fallback-order"}
EMPIRICAL_OVERRIDE = {"zuchongzhi-vqe-f2-above-chemical-accuracy"}  # a measured figure the reader marked high

PROVED_OR_OWN = ("Started HIGH: a result proved in the paper, or the paper's own statement of its setup, scope or "
                 "limits, read in context")
EMPIRICAL = "Started LOW: an empirical result from one study. NOT upgraded"
AUTHOR_CLAIM = "Started LOW: the authors' own claim, not tested in the paper. NOT upgraded"
CITED = "Started LOW: a claim the source cites from other work, not tested in it. NOT upgraded"


def load_groups() -> list[tuple[str, dict]]:
    out = []
    for g in GROUPS:
        data = json.loads((READS_DIR / f"group_{g}.json").read_text(encoding="utf-8"))
        out += [(g, p) for p in data["papers"]]
    return out


def kept_groups() -> list[tuple[str, dict]]:
    return [(g, p) for g, p in load_groups() if p["record_id"] not in REFUSE]


def quotes_of(a: dict) -> list[str]:
    qs = list(a["quotes"])
    for old, new in QUOTE_EDITS.get(a["id_suggestion"], []):
        hits = [i for i, q in enumerate(qs) if old in q]
        if not hits:
            raise ValueError(f"{a['id_suggestion']}: the quote text to replace is not there: {old[:60]!r}")
        qs[hits[0]] = qs[hits[0]].replace(old, new)
    return qs + EXTRA_QUOTES.get(a["id_suggestion"], [])


def certainty(aid: str, a: dict) -> tuple[str, str]:
    kind, ctype, sugg = a["kind"], a["claim_type"], a["certainty_suggestion"]
    if ctype == "vendor-self-claim":
        if aid in VENDOR_DESCRIPTIONS:
            return "moderate", f"{f80.VENDOR_START}. Not upgraded: a description of the product, not a result"
        return "low", (f"{f80.VENDOR_START}. DOWNGRADED one level: a result or claim the vendor reports about its "
                       "own product, not independently checked")
    if kind == "cited":
        return "low", CITED
    if kind == "shown":
        if sugg == "high" and aid not in EMPIRICAL_OVERRIDE:
            return "high", PROVED_OR_OWN
        return "low", EMPIRICAL
    if sugg == "high":  # claimed: the authors' own stated scope or limits (each checked 2026-10-18)
        return "high", PROVED_OR_OWN
    return "low", AUTHOR_CLAIM


def assertions() -> list[tuple[str, AssertionRecord, str, dict]]:
    out = []
    for g, p in kept_groups():
        rid = p["record_id"]
        for a in p["assertions"]:
            aid = a["id_suggestion"]
            cert, reasons = certainty(aid, a)
            value = " ".join((VALUE_REPLACE.get(aid) or a["value"]).split())
            out.append((g, AssertionRecord(
                id=aid, value=value, provenance=f"{rid}, {a['anchor']}",
                citation_context="; ".join(f'"{q}" ({a["anchor"]})' for q in quotes_of(a)),
                evidence_tag="N/A", context=CONTEXT_FIX.get(aid) or a["context"], certainty=cert,
                certainty_reasons=reasons, fidelity=a.get("fidelity") or "scoped", derivation="extracted",
                claim_type=a["claim_type"],
                search_scope=("the paper's own text, as read" if a["claim_type"] == "absence" else None),
                updated=TODAY, updated_reason=f"{TODAY} ({TAG}): extracted from {rid}; first-pass read by a subagent, "
                                              "every quoted passage read in context by the coordinator"), rid, p))
    return out


def check_quotes() -> None:
    """Every quote verbatim in its source BEFORE anything is written (section 26)."""
    texts: dict[str, str] = {}
    for _, a, _, p in assertions():
        text = texts.setdefault(p["file"], plain(source_text(p["file"])))
        require_verbatim(a.id, a.citation_context, text)


def _note(p: dict) -> tuple[list[str], str]:
    path = p["file"].replace("/", "\\")
    return [path], f"Local copy {f80._sha(Path(path))}, recorded {TODAY} (F89)"


def apply_changes(conn) -> list[str]:
    check_quotes()
    log = []
    contexts = {r[0] for r in conn.execute("SELECT id FROM contexts")}
    for rid, why in sorted(NO_COPY.items()):
        reason = f"{TODAY} ({TAG}): selected for reading and NOT read: {why}; on the hand-download list"
        stored = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (rid,)).fetchone()[0]
        if reason not in stored:
            append_updated_reason(conn, rid, reason, TODAY)
            log.append(f"no copy {rid}")
        else:
            log.append(f"exists no copy {rid}")
    for g, p in load_groups():
        rid = p["record_id"]
        detail = (f"first pass, in part: {p['partial_detail']}" if p.get("read_extent") == "partial"
                  else "first pass, the whole source") + f" (Sonnet 5.5 reader, group {g.upper()})"
        if p.get("version_note"):
            detail += f"; version: {p['version_note']}"
        have = {(r[0], r[1], r[2]): r[3] for r in conn.execute(
            "SELECT reader, read_on, extent, detail FROM paper_reads WHERE record_id = ?", (rid,))}
        if rid in REFUSE:
            if (SUBAGENT_READER, TODAY, "subagent") not in have:
                add_read(conn, rid, SUBAGENT_READER, TODAY, "subagent", detail)
                append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read at first pass and NOT entered: "
                                                 f"{REFUSE[rid]}", TODAY)
                log.append(f"refuse {rid}")
            else:
                log.append(f"exists refused {rid}")
            continue
        access, evidence, tier = conn.execute("SELECT access, evidence, tier FROM paper_fields WHERE record_id = ?",
                                              (rid,)).fetchone()
        paths, note = _note(p)
        present = {s.lower() for s in recheck.local_paths(access or "")}
        new = [s for s in paths if s.lower() not in present]
        if new:
            conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?",
                         (" | ".join([access, *new]) if access else " | ".join(new), rid))
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?",
                         (f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): local copy added to access", TODAY)
            log.append(f"access {rid}")
        if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (rid,)).fetchone():
            ctx = p["bears_on_context"]
            if ctx not in contexts:
                raise ValueError(f"{rid}: applicability context {ctx!r} is not a context")
            conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) VALUES (?, ?, ?)",
                         (rid, ctx, f"{p['what_it_is'].rstrip('.')} -- first-pass read"))
            log.append(f"applic {rid} [{ctx}]")
        for reader, extent, det in ((SUBAGENT_READER, "subagent", detail), ("Claude", "partial", COORDINATOR_DETAIL)):
            if (reader, TODAY, extent) not in have:
                add_read(conn, rid, reader, TODAY, extent, det)
                log.append(f"read   {rid} [{reader}, {extent}]")
            elif have[(reader, TODAY, extent)] != det:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? AND read_on = ? "
                             "AND extent = ?", (det, rid, reader, TODAY, extent))
                log.append(f"update read {rid} [{reader}]")
        if tier != "read":
            set_tier(conn, rid, "read", checked_against_source=(
                f"{TODAY}, Claude, read every quoted passage in context and checked every quote and figure against "
                "the full text; first pass by a subagent"))
            log.append(f"tier   {rid} -> read")
    for _, a, rid, _ in assertions():
        if a.context not in contexts:
            raise ValueError(f"{a.id}: context {a.context!r} is not a context")
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_assertion(conn, a, yielded_by=rid)
            log.append(f"assert {a.id} <- {rid} [{a.certainty}]")
            continue
        changed = sync_assertion(conn, a, f"{TODAY} ({TAG}): corrected to the script's current text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kept = assertions()
    if len({a.id for _, a, _, _ in kept}) != len(kept):
        print("duplicate assertion ids")
        return 1
    slice_ids = {r["record_id"] for r in json.loads(
        (ROOT / "manifests" / "sprint10_f89_slice.json").read_text(encoding="utf-8"))["slice"]}
    read_ids = {p["record_id"] for _, p in load_groups()}
    if read_ids | set(NO_COPY) != slice_ids or read_ids & set(NO_COPY):
        print("the reads and NO_COPY do not partition the slice")
        return 1
    if "--apply" not in args:
        check_quotes()
        from collections import Counter
        print(Counter(a.certainty for _, a, _, _ in kept), Counter(a.context for _, a, _, _ in kept))
        print(f"{len(kept)} assertions from {len(kept_groups())} records; {len(REFUSE)} refused; "
              f"{len(NO_COPY)} with no copy. Every quote verbatim. DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F89 slice read and entered")
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
