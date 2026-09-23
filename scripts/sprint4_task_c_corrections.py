#!/usr/bin/env python3
"""Sprint 4 Task C (F25 B1, decision Q4): correct the seed records that the
F7-F10 adjudication reviews found defective, through the door Task B built.

One-off, kept in the repository because every change it makes is a dated
`updated_reason` and the script IS the record of what changed and why.

DRY-RUN BY DEFAULT (QUALITY_STANDARDS.md "decide, then write"): every change
is applied inside one transaction, every paper row is then pushed back
through `validate_paper()` (the door), the plan and the gate result are
printed, and the transaction is ROLLED BACK. `--apply` commits only if the
gate passes with zero refusals, then regenerates `export/` and rewrites
`scripts/seed_set_metadata.json` from the corrected store so the seed
file and the store agree.

What it does, by record class:

1. Renames `rand-2023-...` and its appendix to `rand-2022-...` (Q4): the
   report's own p.ii says "This research was published in 2022." Every
   table whose foreign key points at records(id) is updated in the same
   transaction; `PRAGMA foreign_key_check` must come back empty.
2. Gives every hand-transcribed record (no arXiv id, no registered DOI)
   the door's shape: `access` = the seed file's real path (plus the
   id-less web page where one is printed), the citation ends with the
   visible "(hand-transcribed from <page>)" marker, `value` = the title,
   audit trail moves out of the citation into `updated_reason`.
3. Switches two records to api-origin because a registered DOI exists
   after all: `rand` (10.7249/RRA1367-6, Crossref) and `freericks`
   (10.1007/978-3-031-87845-9, Springer). Their citations are then
   re-derived by `scripts/refresh_citations.py --apply`.
4. Switches `udaru` to hand-origin: its printed DOI 10.63278/ijcrcr.v8i.3419
   is not registered in the DOI system (doi.org handle lookup: no such
   handle, 2026-09-19). The printed DOI is recorded in `evidence`.
5. Removes tier words ("seen tier", "screened candidate") from every
   disposition that carries one -- the `tier` column is the resolver.
   Task F (F25 D4) does the judgment-heavy disposition rewrite; this pass
   only removes what the door refuses.
6. Appends the F10 findings that the API re-derivation resolves
   (`dupont` title, `kordzanganeh` third author, `lubinski`/`mancilla`
   duplicate-file notes, with the sha256 measurements) to `updated_reason`.

Applicability rationales are NOT validated here: the source-anchor rule
(Q3) is Task F's, which rewrites every rationale. The gate passes
`applicability=[]` and says so.

Order on the day (each step dry-run first):
    python scripts/refresh_citations.py --apply     # api rows: citations from the APIs
    python scripts/sprint4_task_c_corrections.py --apply
    python scripts/refresh_citations.py --apply --ids rand-2022-pqc-critical-infrastructure-assessment,freericks-2026-quantum-mechanics-done-right-book
The gate refuses the four api rows whose Sprint 1 citations still carry
audit-trail text until the first refresh has replaced them, which is the
point: the door does not care which script is asking.

Usage:
    python scripts/sprint4_task_c_corrections.py            # plan + gate, rollback
    python scripts/sprint4_task_c_corrections.py --apply    # commit, export, metadata
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import HAND_MARKER, PaperRecord, append_updated_reason, validate_paper  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
METADATA_PATH = ROOT / "scripts" / "seed_set_metadata.json"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
TODAY = "2026-09-19"
TAG = f"{TODAY} (Sprint 4 Task C, F25 B1)"

RENAMES = {
    "rand-2023-pqc-critical-infrastructure-assessment": "rand-2022-pqc-critical-infrastructure-assessment",
    "rand-2023-pqc-critical-infrastructure-assessment-appendix-b": "rand-2022-pqc-critical-infrastructure-assessment-appendix-b",
}


def _hand(file: str, title: str, citation: str, page: str, url: str | None = None,
          disposition: str | None = None, reason: str | None = None, evidence: str | None = None) -> dict:
    access = str(PAPERS / file) + (f" | {url}" if url else "")
    return dict(file=file, title=title, citation=f"{citation} ({HAND_MARKER} {page})", page=page,
                access=access, disposition=disposition, reason=reason, evidence=evidence)


_TP = "title page"
_TP_REASON = ("access was the bare words 'local file, no DOI/arXiv id'; now the seed file's path. "
              "Citation marked as hand-transcribed (no arXiv id, no registered DOI); value is now the title")

HAND: dict[str, dict] = {
    "bcg-2022-value-of-quantum-benchmarks": _hand(
        "Benchmarking - Value of Quantum Computing Benchmarks - BCG 202211.pdf",
        "The Race to Quantum Advantage Depends on Benchmarking",
        'Langione, M., Bobier, J-F., Krayer, L., Park, H., Kumar, A. (BCG), "The Race to Quantum Advantage Depends on Benchmarking," Boston Consulting Group, 2022-02-23',
        _TP, disposition="Consulting-firm thought-leadership article, not a research paper; an industry-perspective source on why benchmarking matters commercially"),
    "bleximo-2020s-applications-and-impact": _hand(
        "Bleximo - Applications and Impact.pdf",
        "An Overview of Bleximo's Applications",
        'Sanches, F. (Bleximo), "An Overview of Bleximo\'s Applications," internal vendor slide deck, marked confidential and proprietary, no date visible',
        _TP, disposition="Vendor internal slide deck, not a paper; low evidentiary weight as vendor self-description only"),
    "coleman-2022-guide-to-qc-benchmarking-certification": _hand(
        "Guide to Quantum Computing Benchmarking and Certification by Chris Coleman 20220813.pdf",
        "A Guide to Quantum Computing Benchmarking and Certification",
        'Coleman, C., "A Guide to Quantum Computing Benchmarking and Certification," The Quantum Insider, 2022-08-12',
        _TP, disposition="Trade-press explainer article, not a research paper; an accessible overview/glossary source of low evidentiary weight"),
    "dwave-2021-recruit-case-story": _hand(
        "recruit_case_story_v5.pdf",
        "Recruit Communications: Applying Quantum Computing to Digital Marketing",
        'D-Wave, "Recruit Communications: Applying Quantum Computing to Digital Marketing," case story, 2021', _TP),
    "dwave-2023-operational-excellence-ebook": _hand(
        "dwave_qc_ebook_2023_v10.pdf",
        "How Quantum Can Fuel Operational Excellence Today",
        'D-Wave, "How Quantum Can Fuel Operational Excellence Today," ebook v10, 2023', _TP),
    "dwave-2024-unlocking-power-of-quantum": _hand(
        "unlocking-the-power-of-quantum_v2.pdf",
        "Unlocking the Power of Quantum: Applications in Production with D-Wave",
        'D-Wave, "Unlocking the Power of Quantum: Applications in Production with D-Wave," v2, 2024', _TP),
    "dwave-pattison-food-group-case-story": _hand(
        "the-pattison-food-group_case_story_v8.pdf",
        "Quantum in Production: Optimizing E-Commerce Logistics",
        'D-Wave, "Quantum in Production: Optimizing E-Commerce Logistics," Pattison Food Group case story, undated', _TP),
    "ibm-2023-qiskit-explorer-attendee-guide": _hand(
        "IBM Qiskit Explorer 2023 Attendee Guide.pdf",
        "Qiskit | Quantum Explorers: A Self-Paced Quantum Learning Journey -- Attendee Guide",
        'IBM, "Qiskit | Quantum Explorers: A Self-Paced Quantum Learning Journey -- Attendee Guide," 2023-07 to 2024-02',
        _TP, disposition="IBM's own educational program guidebook, not a paper; a method/pedagogy reference for Qiskit-based learning paths"),
    "idq-quantis-qrng-pcie-brochure": _hand(
        "Quantis QRNG PCIe New Generation_Brochure.pdf",
        "Quantis QRNG PCIe-40M and PCIe-240M: Redefining Randomness",
        'ID Quantique, "Quantis QRNG PCIe-40M and PCIe-240M: Redefining Randomness," product brochure, undated',
        _TP, disposition="Vendor product brochure for a quantum random number generator card; marketing material outside this project's ML/optimization scope, recorded under qc as the closest available context since none in ADR-0004's list fits QRNG hardware"),
    "interviewbit-python-cheat-sheet": _hand(
        "Python language Cheat Sheet 1694531939297.pdf",
        "Python Cheat Sheet",
        'InterviewBit, "Python Cheat Sheet," undated',
        _TP, disposition="Generic Python reference unrelated to quantum/QML content; not a paper and apparently a stray item in the seed set; minimal relevance"),
    "kawchak-2023-coding-tips-cirq-qiskit-pennylane": _hand(
        "100 Coding Tips for Qiskit, Cirq, or PennyLane Event.pdf",
        "100 QML Code Tips for Cirq, Qiskit, or PennyLane: a Special Event",
        'Kawchak, K. (ChemicalQDevice), "100 QML Code Tips for Cirq, Qiskit, or PennyLane: a Special Event," Discussion #100, 2023-09-14',
        _TP, disposition="Practitioner slide deck of coding tips, not a research paper; low evidentiary weight, a tooling reference"),
    "kawchak-2023-qiskit-pennylane-qml-demos": _hand(
        "Qiskit PennyLane QML QiML Demos - Kevin Kawchak 20231124.pdf",
        "38 Qiskit, PennyLane QML/QiML Demos - Thanksgiving Eve",
        'Kawchak, K. (ChemicalQDevice), "38 Qiskit, PennyLane QML/QiML Demos - Thanksgiving Eve," Discussion #110, 2023-11-22', _TP),
    "kawchak-2023-quantum-parameter-study-qml": _hand(
        "Quantum Parameter Study for QML - Kevin Kawchak 20230926.pdf",
        "Quantum Parameter Study for Quantum Inspired Machine Learning",
        'Kawchak, K. (ChemicalQDevice), "Quantum Parameter Study for Quantum Inspired Machine Learning," 2023-09-26', _TP),
    "kawchak-2023-resnet50-quantum-transfer-learning": _hand(
        "ResNet50 Time Cost Efficiency via Transfer Learning, QTL 1691915095119.pdf",
        "Time, Cost, Efficiency: ResNet50 Quantum TL, TL Models, 2 Datasets",
        'Kawchak, K. (ChemicalQDevice), "Time, Cost, Efficiency: ResNet50 Quantum TL, TL Models, 2 Datasets," 2023-08-13', _TP),
    "loke-2026-cvqboosting-fraud-detection-smu": _hand(
        "Improving credit card transaction fraud detection using CVQBoosting - QCi Dirac-3 202603 Paul Griffin.pdf",
        "Improving credit card transaction fraud detection using CVQBoosting",
        'Loke, B.H.T., Sahoo, N., Guan, B., Xu, M., Verma, D., Griffin, P.R. (Singapore Management University), "Improving credit card transaction fraud detection using CVQBoosting," SMU Institutional Knowledge, Research Collection School of Computing and Information Systems, conference proceeding article, 2026-03',
        "p.1 cover sheet and p.2 author byline",
        url="https://ink.library.smu.edu.sg/sis_research",
        reason=("access was the bare words 'local file'; now the seed file's path plus the SMU collection URL printed on p.1 "
                "(the item's own handle is not printed on the cover sheet; no DOI or arXiv id exists, so the citation is hand-transcribed). "
                "The correction narrative formerly embedded in the citation moves here: on 2026-09-16 the author list was corrected to the six "
                "named on p.2's 'Author' byline (Loke, Sahoo, Guan, Xu, Verma, Griffin); the Sprint 1 pass had read only p.1's 'See next page "
                "for additional authors', recorded 'et al.', and missed Griffin although the seed filename named him. Re-read from the PDF 2026-09-19")),
    "mancilla-2026-spectra-datasets-substack": _hand(
        "Javier - SPECTRA datasets 20260725.pdf",
        "Four datasets built so a quantum model can demonstrate a potential win",
        'Mancilla, J., "Four datasets built so a quantum model can demonstrate a potential win," Substack (quantumfighter.substack.com), 2026-07-25',
        _TP, disposition="Blog post by the author of mancilla-2026-fourier-wall-spectra describing the SPECTRA benchmark's dataset construction; supporting/explanatory material"),
    "neven-2012-qboost-adiabatic-quantum-optimization": _hand(
        "QBoost - Large Scale Classifier Training with Adiabatic Quantum Optimization - Neven Denchev Rose Macready - ACML PMLR v25 2012.pdf",
        "QBoost: Large Scale Classifier Training with Adiabatic Quantum Optimization",
        'Neven, H. (Google Inc.), Denchev, V.S. (Purdue University), Rose, G., Macready, W.G. (D-Wave Systems Inc.), "QBoost: Large Scale Classifier Training with Adiabatic Quantum Optimization," JMLR: Workshop and Conference Proceedings 25:333-348, Asian Conference on Machine Learning (ACML), 2012',
        _TP, url="https://proceedings.mlr.press/v25/neven12/",
        disposition="SEMINAL: introduces QBoost, the adiabatic-quantum-optimization boosting algorithm that CVQBoost (the algorithm the HSBC consumer work measures on Dirac-3) directly descends from; directly relevant, high priority",
        reason=("access now follows the '<path> | <url>' form (seed file plus the PMLR page; PMLR pages carry no DOI, so hand-transcribed). "
                "The addition history formerly in the disposition moves here: added 2026-09-17 (Sprint 2 Task C spot-check) after the seed "
                "directory changed since Sprint 1's snapshot; the team lead confirmed the addition was intentional (F5's scope names QBoost)")),
    "pere-qml-github-repo-empty": _hand(
        "Christophere Pere QML Github Repo.txt",
        "Christophere Pere QML Github Repo (empty seed file)",
        'No recoverable citation: the seed file "Christophere Pere QML Github Repo.txt" is 0 bytes',
        "filename", disposition="GitHubRepos-class reference, out of scope for the paper class, and the seed file is empty (0 bytes); a data-quality finding recorded here for the team lead"),
    "qci-2024-profiling-cvqboost": _hand(
        "QCi - Profiling of CVQBoost.pdf",
        "Profiling of CVQBoost Algorithm: Fraud Detection",
        'Quantum Computing Inc., "Profiling of CVQBoost Algorithm: Fraud Detection," vendor white paper, no named authors, no venue, no DOI, December 2024',
        "cover", disposition="QCi's own internal profiling document on CVQBoost for fraud detection; vendor-authored, no named authors, no venue, no DOI; directly relevant for performance/timing claims about the algorithm the HSBC project uses",
        reason=("access was the bare words 'local file'; now the seed file's path. The citation now states explicitly (F10) that the document "
                "names no authors, venue or DOI -- read from the cover 2026-09-19 -- instead of being shaped like a peer-reviewed citation")),
    "qci-2024-unconventional-computing-medium": _hand(
        "An introduction to Unconventional Computing - QCi 202408 Medium.pdf",
        "An introduction to Unconventional Computing",
        'Quantum Computing Inc., "An introduction to Unconventional Computing," Medium, 2024-08-26',
        _TP, disposition="QCi's own vendor blog post on unconventional (non-gate) computing; a primary-source description of QCi's own framing"),
    "qci-2026-entropy-computing-trade-magazine": _hand(
        "QCi - Entropy Computing 202603.pdf",
        "Entropy Computing: A photonics-enabled quantum computing solution for optimization",
        'Unattributed, "Entropy Computing: A photonics-enabled quantum computing solution for optimization," Photonic Integrated Circuits Magazine, Issue 1 2026',
        _TP, disposition="Trade-magazine article on QCi's Entropy Computing/Dirac-3 technology; a plain-language platform description, not primary research"),
    "rand-2022-pqc-critical-infrastructure-assessment-appendix-b": _hand(
        "Homland PQC Quantum Assessment RAND_RRA1367-6.appendixB.pdf",
        "Preparing for Post-Quantum Critical Infrastructure: Appendix B",
        'Vermeer, M.J.D., Parker, E., Kochhar, A.K. (RAND Corporation / HSOAC), "Preparing for Post-Quantum Critical Infrastructure," companion Appendix B to RRA1367-6, 2022',
        "cover; year from the main report's p.ii",
        disposition="Appendix to rand-2022-pqc-critical-infrastructure-assessment; recorded as a companion reference rather than mined as an independent paper",
        reason=("id renamed from rand-2023-... (Q4): the main report's p.ii says 'This research was published in 2022'. " + _TP_REASON)),
    "udaru-2025-qml-credit-risk": _hand(
        "QML Quantum Machine Learning For Credit Risk -A Next-Generation Approach To Risk Assessment 202511.pdf",
        "Quantum Machine Learning For Credit Risk: A Next-Generation Approach To Risk Assessment",
        'Udaru, B.R., "Quantum Machine Learning For Credit Risk: A Next-Generation Approach To Risk Assessment," Journal of International Crisis and Risk Communication Research, 8(S11), 2025-11',
        "p.1",
        reason=("access was 'DOI:10.63278/ijcrcr.v8i.3419'; that DOI is not registered in the DOI system (doi.org handle lookup: no such handle; "
                "Crossref and DataCite both 404; checked 2026-09-19), so it is not an access path. Now hand-transcribed with the seed file's path; "
                "the printed DOI is recorded in evidence"),
        evidence=("The DOI printed on the paper, 10.63278/ijcrcr.v8i.3419, is not registered in the DOI system as of 2026-09-19 (doi.org handle "
                  "lookup returns no such handle; Crossref and DataCite both 404). Weigh together with the venue-quality caveat in the disposition")),
    "zapata-2025-qc-for-finance-guide": _hand(
        "Quantum Computing for Finance - Zapata 202505.pdf",
        "Quantum Computing for Finance: An Introductory Guide",
        'Zapata, O., PhD (Zapata AI), "Quantum Computing for Finance: An Introductory Guide," 2025-05', _TP),
}

# Records that turn out to have a registered DOI: access becomes the id and
# scripts/refresh_citations.py --apply derives the citation from Crossref.
API_ACCESS: dict[str, tuple[str, str]] = {
    "rand-2022-pqc-critical-infrastructure-assessment": (
        "DOI:10.7249/RRA1367-6",
        "id renamed from rand-2023-... (Q4): the report's p.ii says 'This research was published in 2022' and the hand-typed citation carried "
        "no year at all (F10). access was the bare words 'local file'; the report has a registered DOI (Crossref, resolves to "
        "www.rand.org/pubs/research_reports/RRA1367-6.html; p.iii prints www.rand.org/t/RRA1367-6), so the record is api-origin and the "
        "citation is re-derived from Crossref. Crossref's record names no contributors; the cover names Vermeer, Parker and Kochhar. "
        f"Seed file: {PAPERS / 'Homland PQC Quantum Assessment RAND_RRA1367-6.pdf'}"),
    "freericks-2026-quantum-mechanics-done-right-book": (
        "DOI:10.1007/978-3-031-87845-9",
        "the Sprint 1 record guessed 'a book-level DOI likely exists'; it does (Crossref, Springer Nature, type book), so the record is "
        "api-origin and the citation is re-derived from Crossref. "
        r"Seed file: D:\Data\Harold\EvidenceBasedDB\Books\Book - Quantum Mechanics Done Right - Springer 2026.pdf"),
}

# api-origin rows whose disposition names a tier (the door refuses it).
DISPOSITIONS: dict[str, str] = {
    "arute-2019-quantum-supremacy-google-nature": "LANDMARK peer-reviewed Nature paper (Google's quantum supremacy claim, Sycamore processor); a high-value world/qc reference",
    "britt-humble-2017-hpc-with-qpus-acm": "Peer-reviewed ACM paper on integrating QPUs into HPC architectures",
    "huynh-2023-quantum-inspired-ml-survey": "Real survey paper specifically on Quantum-Inspired ML (QiML), a subfield distinct from QML proper; relevant for establishing the qml/QiML vocabulary boundary this library needs",
    "kerger-2023-mind-the-o-distributed-quantum-algorithms": "Real theoretical paper on quantum distributed algorithms (CONGEST-CLIQUE model); moderate relevance, useful for theoretical qc grounding",
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu": "Real benchmarking paper comparing simulators and physical QPUs across four vendors; relevant for the cross-platform benchmarking angle",
    "li-2024-photon-counting-raman-spectroscopy": "Real peer-reviewed photonics/spectroscopy paper, but NOT quantum computing or QML (single-photon detection benchmarking); off-topic for this project's core scope, general background at most",
    "mandra-2021-hybridq-simulator-nasa": "Real paper introducing a hybrid quantum-circuit simulation framework; a useful method-context reference for simulation technique",
    "wang-2025-quantum-optimization-nn-compression": "Real paper on QUBO-based neural-network compression via adiabatic QC; directly relevant to the qml/optimization intersection",
    "freericks-2026-quantum-mechanics-done-right-book": "A BOOK, out of scope for the paper class per SPRINT_1_PLAN.md; recorded with this disposition rather than forced into the paper record shape; revisit when Task G's book path (F26, decision Q5) lands",
}

# F10 findings the API re-derivation resolves; appended so the row says why
# its citation changed, not just that it did.
REASON_NOTES: dict[str, str] = {
    "dupont-2023-quantum-enhanced-greedy-solver":
        "F10 (Sprint 3) found the hand-typed title wrong ('Quantum Enhanced Greedy Solver for Optimization Problems'); the citation is now the arXiv record's, including the journal reference/DOI the record carries",
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu":
        "the note formerly inside the citation moves here: the seed filename truncates the arXiv id to 2211.1563; the PDF's own arXiv banner reads 2211.15631. F10 found the third author (Basil Kyriacou) missing from the hand-typed list; the API-derived list is complete. Disposition no longer says 'seen tier' beside a tier column that says screened",
    "lubinski-2023-application-oriented-benchmarks-qedc":
        "the note formerly inside the citation moves here: two seed files carry this paper ('Application-Oriented...' and 'Benchmarking - Application-Oriented...'); sha256 b05b558d23567fc6... is identical for both (checked 2026-09-19); recorded once",
    "mancilla-2026-fourier-wall-spectra":
        "the note formerly inside the citation claimed two 'identically-content' seed files; their sha256 differ (5784f63ea04ae701... vs 4967accbbc78ca9b..., 2,224,604 vs 2,216,899 bytes; checked 2026-09-19), so they are two different files of arXiv:2607.15815 and the claim was false (F10). Recorded once; the arXiv record is the source of truth",
    "sakhnenko-2026-data-efficient-qml":
        "the Sprint 1 note about two candidate dates is superseded by the arXiv record's own published/updated dates",
}


def _fk_columns(conn) -> list[tuple[str, str]]:
    """Every (table, column) that carries a record id: foreign keys to
    records(id) AND, transitively, to any column that itself carries one
    (paper_applicability.record_id references paper_fields(record_id),
    not records(id) -- the first dry run's foreign_key_check caught it)."""
    fks = []
    for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        for fk in conn.execute(f"PRAGMA foreign_key_list({table})"):
            fks.append((table, fk["from"], fk["table"], fk["to"]))
    carriers = {("records", "id")}
    changed = True
    while changed:
        changed = False
        for table, col, target_table, target_col in fks:
            if (target_table, target_col) in carriers and (table, col) not in carriers:
                carriers.add((table, col))
                changed = True
    carriers.discard(("records", "id"))
    return sorted(carriers)


def _append_reason(conn, pid: str, note: str) -> None:
    """Thin wrapper over the ONE append-only implementation in store.ingest.

    This function used to spell the join itself, with an inverted ternary
    that destroyed 44 records' history. It now delegates, so there is one
    behavior and one behavioral test (PR #30 round-2 audit, 2026-09-23).
    """
    existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (pid,)).fetchone()[0] or ""
    if TAG in existing and note in existing:
        return
    append_updated_reason(conn, pid, f"{TAG}: {note}", TODAY)


def apply_changes(conn) -> list[str]:
    log: list[str] = []
    for old, new in RENAMES.items():
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (old,)).fetchone() is None:
            continue
        for table, col in _fk_columns(conn):
            n = conn.execute(f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (new, old)).rowcount
            if n:
                log.append(f"rename {old} -> {new}: {table}.{col} x{n}")
        conn.execute("UPDATE records SET id = ? WHERE id = ?", (new, old))
        log.append(f"rename {old} -> {new}: records.id")
    for pid, h in HAND.items():
        row = conn.execute("SELECT provenance FROM records WHERE id = ?", (pid,)).fetchone()
        if row is None:
            raise SystemExit(f"error: {pid} not in the store")
        conn.execute("UPDATE records SET value = ?, provenance = ? WHERE id = ?", (h["title"], h["citation"], pid))
        conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (h["access"], pid))
        if h["disposition"]:
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (h["disposition"], pid))
        if h["evidence"]:
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?", (h["evidence"], pid))
        _append_reason(conn, pid, h["reason"] or _TP_REASON)
        log.append(f"hand  {pid}: access -> {Path(h['access'].split(' | ')[0]).name}" + (" | url" if " | " in h["access"] else ""))
    for pid, (access, reason) in API_ACCESS.items():
        conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (access, pid))
        _append_reason(conn, pid, reason)
        log.append(f"api   {pid}: access -> {access} (citation via refresh_citations.py --apply)")
    for pid, disposition in DISPOSITIONS.items():
        conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (disposition, pid))
        _append_reason(conn, pid, "disposition no longer names a tier; the tier column is the resolver")
        log.append(f"disp  {pid}")
    for pid, note in REASON_NOTES.items():
        _append_reason(conn, pid, note)
        log.append(f"note  {pid}")
    return log


_MARKER_RE = re.compile(re.escape(HAND_MARKER) + r"\s+([^)]+)\)")


def gate(conn) -> list[str]:
    """Every paper row back through the door.

    WHAT THIS DOES AND DOES NOT VERIFY (PR #30 review, 2026-09-22). The
    origin below is DERIVED from `parse_access`, which makes validate_paper's
    two origin-versus-access rules tautologies: an api row is api because its
    access resolves, so "api without a resolvable id" can never fire here.
    That is unavoidable while the store has no `citation_origin` column --
    the declared origin is not persisted, only inferable -- and it is stated
    rather than left implied, because the printed "0 refusal(s)" otherwise
    reads as a stronger claim than it is.

    What the gate DOES check on every row: audit-trail text in the citation,
    a non-empty title, a one-line disposition naming no tier, the read-tier
    obligation, and for hand-origin rows the visible marker, the
    transcribed-from field and that the local path exists.

    What it does NOT check: whether an api row's citation matches the API.
    That is `scripts/refresh_citations.py`'s job, which this script's own
    run order puts FIRST for exactly that reason (see the module docstring).
    """
    refusals = []
    rows = conn.execute(
        "SELECT r.id, r.value, r.provenance, r.updated, r.updated_reason, p.tier, p.access, p.disposition, "
        "p.evidence, p.mined_by, p.checked_against_source, "
        "(SELECT context_id FROM record_contexts c WHERE c.record_id = r.id LIMIT 1) AS context "
        "FROM records r JOIN paper_fields p ON p.record_id = r.id ORDER BY r.id"
    ).fetchall()
    for r in rows:
        origin = "api" if citations.parse_access(r["access"]) else "hand"
        m = _MARKER_RE.search(r["provenance"] or "")
        paper = PaperRecord(
            id=r["id"], tier=r["tier"], access=r["access"], disposition=r["disposition"], context=r["context"] or "",
            value=r["value"], citation=r["provenance"], citation_origin=origin,
            hand_transcribed_from=m.group(1) if m else None, evidence=r["evidence"], mined_by=r["mined_by"],
            checked_against_source=r["checked_against_source"], updated=r["updated"], updated_reason=r["updated_reason"],
        )
        try:
            validate_paper(paper)
        except ValueError as ex:
            refusals.append(str(ex))
    return refusals


def write_metadata(conn) -> int:
    """Rewrite scripts/seed_set_metadata.json from the store, in the file's
    existing order, so the seed file carries exactly what the door accepts."""
    existing = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    order = [RENAMES.get(e["id"], e["id"]) for e in existing]
    out = []
    for pid in order:
        r = conn.execute(
            "SELECT r.id, r.value, r.provenance, p.tier, p.access, p.disposition, "
            "(SELECT context_id FROM record_contexts c WHERE c.record_id = r.id LIMIT 1) AS context "
            "FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?", (pid,)
        ).fetchone()
        if r is None:
            raise SystemExit(f"error: metadata id {pid} not in the store")
        api = citations.parse_access(r["access"]) is not None
        entry = {"id": r["id"]}
        if not api:
            m = _MARKER_RE.search(r["provenance"])
            entry.update(title=r["value"], citation=r["provenance"], transcribed_from=m.group(1) if m else "")
        entry.update(citation_origin="api" if api else "hand", access=r["access"], context=r["context"],
                     disposition=r["disposition"], promote=r["tier"] != "seen")
        out.append(entry)
    METADATA_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(out)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    do_apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    missing = [h["file"] for h in HAND.values() if not (PAPERS / h["file"]).exists()]
    if missing:
        print("error: seed files not found under " + str(PAPERS) + ":\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")  # the id rename updates parent and children together
        conn.execute("BEGIN")
        log = apply_changes(conn)
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        refusals = gate(conn)
        for line in log:
            print(line)
        for row in fk:
            print("  FK PROBLEM", tuple(row))
        print(f"\n{len(log)} change(s); foreign_key_check: {len(fk)} problem(s); door gate: {len(refusals)} refusal(s) "
              "(shape rules only: applicability rationales are Task F's, and an api row's citation is NOT "
              "compared against the API here -- that is refresh_citations.py, run first; see gate() docstring)")
        for r in refusals:
            print("  REFUSED", r[:220])
        if fk or refusals or not do_apply:
            conn.execute("ROLLBACK")
            if not do_apply:
                print("PLANNED (dry run; nothing written). Re-run with --apply to commit.")
                return 0
            print("NOT APPLIED: the gate or the foreign-key check failed; nothing written.", file=sys.stderr)
            return 1
        conn.execute("COMMIT")
        conn.execute("PRAGMA foreign_keys = ON")
        regenerate(conn, EXPORT_DIR)
        n = write_metadata(conn)
        print(f"applied. export regenerated; {n} entries written to {METADATA_PATH.name}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
