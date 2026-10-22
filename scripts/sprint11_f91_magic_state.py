#!/usr/bin/env python3
"""Sprint 11 Task E (F91): Google Quantum AI's magic state cultivation experiment, entered and read.

Rosenfeld, Gidney, Roberts et al., "Magic state cultivation on a
superconducting quantum processor", Science, published online 2026-10-15,
DOI 10.1126/science.aee7961 (team lead, 2026-10-19). Crossref lists the
license as starting 2027-10-15, so the publisher's copy is not used; the
free preprint arXiv:2512.13908v1 is the local copy and the text read.

`--fetch` saves the preprint to the Papers folder (ONE arXiv request, through the
paced fetcher, under intake section 3's name convention). `--apply` enters
the record by its DOI with the preprint as its local copy and as its
`version_of` (a hand probe, anchored: Crossref lists no relation), then the
headline assertions, each quote checked against the preprint by
`require_verbatim` before the write and written only through the verified
write path (intake sections 26 and 31). Where the published abstract's
wording differs from the preprint's (Crossref's abstract, read
2026-10-22), the value says so. DRY-RUN BY DEFAULT; `--apply` takes a
verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, append_updated_reason, insert_paper, insert_verified_assertion,  # noqa: E402
                          record_probe,
                          sync_verified_assertion, validate_assertion)
from store.quotes import pdf_text, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
TAG = "Sprint 11 Task E, F91"
DOI = "10.1126/science.aee7961"
ARXIV = "2512.13908"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
PDF = PAPERS / "2025-12_Rosenfeld_Magic-state-cultivation-on-a-superconducting-quantum-processor.pdf"


def fetch() -> int:
    if PDF.exists():
        print(f"exists  {PDF.name}  SHA-256 {hashlib.sha256(PDF.read_bytes()).hexdigest()}")
        return 0
    citations.assume_recent_arxiv_request()  # a run started right after another waits the full interval
    data = citations.PacedFetcher()(f"https://arxiv.org/pdf/{ARXIV}v1", "application/pdf")
    if not data.startswith(b"%PDF"):
        print("FAILED: not a PDF")
        return 1
    PDF.write_bytes(data)
    first = subprocess.run(["pdftotext", "-l", "1", str(PDF), "-"], capture_output=True).stdout.decode("utf-8",
                                                                                                         "replace")
    print(f"saved   {PDF.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes  "
          f"{'stamp ok' if ARXIV in first else 'NO STAMP: check the first page by hand'}")
    return 0


PUBLISHED_ABSTRACT = ("Cultivation reduces the error by a factor of 40, with a state fidelity of at least 0.9999(1) "
                      "(retaining 8% of attempts).")  # Crossref's abstract for the DOI, read 2026-10-22

ENTRY = {
    "access": f"DOI:{DOI} | {PDF}",
    "context": "qc", "tier": "read",
    "disposition": ("A device experiment in quantum error correction: magic state cultivation in a distance-3 "
                    "color code on a Google Willow processor, with a fault-tolerant measurement (kickback "
                    "tomography) bounding the T state's fidelity, and grafting into a distance-5 encoding "
                    "compatible with the surface code"),
    "evidence": (f"Local copy is the free preprint arXiv:{ARXIV}v1, SHA-256 {{sha}} (saved {TODAY} through the "
                 "paced fetcher), the text every quote is checked against. Crossref lists the publisher's license "
                 "as starting 2027-10-15, so the Science copy was not used. The abstracts differ: the Science "
                 "abstract (Crossref, read 2026-10-22) says the fidelity is \"at least\" 0.9999(1); the preprint "
                 "v1 abstract omits \"at least\". Data: DOI:10.5281/zenodo.17872003 (not read)."),
    "found_via": "the team lead, 2026-10-19: \"Can you add this paper to the backlog for the next sprint\"",
    "cited_as": "DOI: 10.1126/science.aee7961 (a screenshot)",
    "checked_against_source": f"{TODAY}, Claude, the preprint read against its quotes; abstract compared with Crossref's",
    "reads": [["Claude", TODAY, "partial",
               "abstract, introduction, results (Figs. 2 to 4), outlook, and the supplement's sections on RL "
               "calibration, kickback tomography validation and the grafted-code memory experiment"]],
    "applicability": [["qc", "a hardware demonstration of magic state preparation for fault-tolerant quantum "
                             "computing, with error rates, post-selection rates and a fidelity bound -- abstract "
                             "and Figs. 2 to 4"]],
    "updated_reason": f"{TODAY}: added by scripts/sprint11_f91_magic_state.py ({TAG}); read in part",
}

ONE = ("LOW: one study's hardware measurement, by the device's maker, not independently replicated; read "
       "directly in the preprint")


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", f"{TODAY} ({TAG}): extracted from the preprint arXiv:{ARXIV}v1, read {TODAY}")
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "HW")
    kw.setdefault("context", "qc")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw.setdefault("certainty", "low")
    kw.setdefault("certainty_reasons", ONE)
    return AssertionRecord(**kw)


def assertions(src: str) -> list[AssertionRecord]:
    return [
        A(id="msc-cultivation-cuts-t-state-error-about-40x",
          value=("On a Google Willow processor, starting from a distance-3 color code, adding magic state "
                 "cultivation to state preparation reduced the full circuit's logical error probability (an upper "
                 "bound on the T state's error) by about a factor of 40 relative to state injection: from 4.4(2) × "
                 "10−3 with injection only to between 1 × 10−4 and 2 × 10−4 near the T state, measured by kickback "
                 "tomography after post-selection. Removing the circuit's QEC cycles makes the error about 100 "
                 "times worse"),
          provenance=f"{src}, abstract, Introduction and Results (Figs. 1 and 3); preprint arXiv:{ARXIV}v1",
          citation_context=('"Cultivation reduces the error by a factor of 40" (abstract); "using a Willow '
                            'processor" (Introduction); "We begin cultivation in a distance-3 color code" (Fig. 1 '
                            'caption); "the logical error probability when injecting θ = π/4 is 4.4(2) × 10−3" '
                            '(Results, kickback tomography); "the logical error probability of the full circuit '
                            'hovers between 1 × 10−4 and 2 × 10−4" (Results, Fig. 3); "removing the QEC cycles makes '
                            'the error about 100 times worse" (Results, Fig. 3)')),
        A(id="msc-t-state-fidelity-bound-0-9999",
          value=("The experiment bounds the cultivated T state's fidelity at 0.9999(1), an upper bound of 1(1) × "
                 "10−4 on its error (the uncertainty is as large as the error), retaining 8% of attempts; the "
                 "method gives a lower bound on the fidelity, not the fidelity itself. Device drift varies the "
                 "logical error by about 1×10−4 over about an hour. The authors call the fidelity similar to recent "
                 "trapped-ion demonstrations. The preprint v1 abstract says \"a state fidelity of 0.9999(1)\"; the "
                 "published Science abstract says \"at least 0.9999(1)\""),
          provenance=f"{src}, abstract, Introduction, Results and Conclusion; preprint arXiv:{ARXIV}v1; Science "
                     "abstract via Crossref",
          citation_context=('"with a state fidelity of 0.9999(1) (retaining 8% of attempts)" (preprint abstract); '
                            '"corresponding to an upper bound of 1(1) × 10−4 error" (Introduction); "we can arrive '
                            'at a precise lower bound on the magic state fidelity" (Conclusion); "device drift '
                            'results in logical error variation on the order of 1×10−4 over about an hour" '
                            '(Results); "fidelity is similar to recent demonstrations in trapped ions" '
                            '(Introduction)')),
        A(id="msc-post-selection-keeps-8-percent",
          value=("The fidelity result keeps about 8% of the data, at θ = π/4, after discarding every attempt with "
                 "any detection event anywhere in the kickback tomography circuit, a circuit that includes two "
                 "extra rounds of cultivation and three QEC cycles. In the shorter Fig. 2 circuit (injection and "
                 "logical tomography, no cultivation) 76(3)% of the data was kept; the paper gives no injection-only "
                 "rate for the Fig. 3 circuit"),
          provenance=f"{src}, Introduction and Results (Figs. 2 and 3); preprint arXiv:{ARXIV}v1",
          citation_context=('"About 8% of data is retained in this case, which includes two extra rounds of '
                            'cultivation and three quantum error correction (QEC) cycles." (Introduction); '
                            '"Filtering for any detection events in the entire circuit, the data retainment rate is '
                            'maximized again at 8% at θ = π/4" (Results, Fig. 3); "For the injection case (Fig. '
                            '2(b)), we retain 76(3)% of the data" (Results, Fig. 2)')),
        A(id="msc-rl-calibration-was-crucial",
          value=("The authors state that reinforcement-learning calibration was crucial for the fidelity and "
                 "post-selection rates they report; it improved both the logical error and the data retainment "
                 "by about an order of magnitude"),
          provenance=f"{src}, Supplement (RL calibration, Fig. S13); preprint arXiv:{ARXIV}v1",
          citation_context=('"In our experiment, RL calibration was crucial for observing the magic state fidelity '
                            'and post selection rates reported in the main text." (Fig. S13 caption); "Both metrics '
                            'are improved by about an order of magnitude by the RL agent." (Supplement)')),
        A(id="msc-grafted-code-error-7x-above-simulation",
          value=("After grafting the cultivated state into a distance-5 encoding compatible with the surface code "
                 "(a grafted code that is not itself matchable, holding color-code and surface-code stabilizers), "
                 "the measured logical error rate was about seven times higher than simulated. The authors call "
                 "leakage the likely main cause; the circuits had no leakage removal units and the simulations "
                 "leave leakage out. They call the grafting a proof-of-principle demonstration"),
          provenance=f"{src}, Results (section III) and Supplement (grafted-code memory experiment, Fig. S22); "
                     f"preprint arXiv:{ARXIV}v1",
          citation_context=('"grafting our magic states into a distance-5 encoding compatible with the surface code" '
                            '(section III); "The grafted code is not matchable, as it contains stabilizers similar to '
                            'the color code as well as surface code" (section III); "We observe that the LER in our '
                            'experiment is about seven times higher than expected from simulations" (Supplement); '
                            '"It is likely that the main source of disagreement is population leakage." '
                            '(Supplement); "Our circuits did not contain the leakage removal units described in '
                            'previous work" (Supplement); "principle demonstration of non-Clifford state escape into '
                            'an advantageous code" (section III, after the words proof-of; the text layer drops the line-break '
                            'hyphen)')),
        A(id="msc-projection-halving-noise-2e-5",
          value=("The authors project, without demonstrating it, that the magic state infidelity should scale as "
                 "p^3 in the processor noise strength p, so that halving p should give T state infidelity upper "
                 "bounds of about 2 × 10−5 with a distance-3 cultivation code"),
          provenance=f"{src}, Conclusion and outlook; preprint arXiv:{ARXIV}v1",
          citation_context=('"the magic state infidelity should drastically scale as p3" (Conclusion); "improving '
                            'the noise strength by a factor of two should result in |T ⟩ state infidelity upper '
                            'bounds of ∼ 2 × 10−5" (Conclusion); "while using only a distance-3 code for the '
                            'cultivation step" (Conclusion)'),
          evidence_tag="SIM",
          certainty_reasons=("LOW: the authors' projection from simulation, not measured; one study, by the "
                             "device's maker")),
    ]


def build(fetcher=None):
    entry = dict(ENTRY, evidence=ENTRY["evidence"].replace("{sha}", hashlib.sha256(PDF.read_bytes()).hexdigest()))
    return intake.build_record(entry, fetcher=fetcher, today=TODAY)


def verify_all(src: str) -> list:
    text = pdf_text(str(PDF))
    return [(a, require_verbatim(a.id, a.citation_context, text)) for a in assertions(src)]


def apply_changes(conn, paper) -> list[str]:
    checked = verify_all(paper.id)
    log = []
    if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (paper.id,)).fetchone() is None:
        insert_paper(conn, paper)
        log.append(f"paper  {paper.id} [read]")
    else:
        log.append(f"exists {paper.id}")
        stored = conn.execute("SELECT disposition FROM paper_fields WHERE record_id = ?", (paper.id,)).fetchone()[0]
        if stored != ENTRY["disposition"]:  # the fresh-eyes review's scope correction, 2026-10-22
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?",
                         (ENTRY["disposition"], paper.id))
            append_updated_reason(conn, paper.id, f"{TODAY} ({TAG}): disposition corrected to the device and "
                                  "code the paper names", TODAY)
            log.append(f"update {paper.id} [disposition]")
    record_probe(conn, paper.id, "version_of", f"arXiv:{ARXIV}", "hand", TODAY,
                 anchor="the preprint's title and first authors match Crossref's record; Crossref lists no relation")
    for a, verified in checked:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=paper.id)
            log.append(f"assert {a.id} <- {paper.id} [{a.certainty}, {a.evidence_tag}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, f"{TODAY} ({TAG}): corrected to the script's current "
                                          "text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        return fetch()
    if not PDF.exists():
        print(f"{PDF.name} is missing: run --fetch first")
        return 1
    paper = build()  # one Crossref request; nothing written
    if "--apply" not in args:
        print(f"paper  {paper.id} [read]  {paper.citation}")
        for a, _ in verify_all(paper.id):
            validate_assertion(a)  # the checks insert_assertion runs; nothing written
            print(f"assert {a.id} <- {paper.id} [{a.certainty}, {a.evidence_tag}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F91 magic state cultivation")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, paper)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
