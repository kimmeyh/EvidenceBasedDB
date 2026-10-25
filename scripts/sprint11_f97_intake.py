#!/usr/bin/env python3
"""Sprint 11 Task F (F97, the F95 release for Sprint 11): new papers in
`Papers\\` and the team lead's list, entered and linked before they are read.

Two parts, both through the door (`scripts/intake.py`):

1. LOCAL_COPIES: the 38 PDFs in `Papers\\` that no record's `access` named,
   for 36 records (two pairs of duplicate files), as of 2026-10-22 with
   Task G's 9 copies held out (the planning snapshot said 37; one file was
   counted with G; intake section 36). Each was matched to its
   record by the arXiv id in its file name or first-page stamp, or by the
   DOI on its first pages, and the record's title was checked against the
   PDF's first two pages (three differ in form only: Kerger's title is
   LaTeX, Dupont's arXiv v1 title differs from the published one, and
   RAND's DOI is printed as a rand.org short link). The path is appended to
   `access`, never replacing it, with the file's SHA-256 in `evidence`.
2. The team lead's list (2026-10-21): five arXiv preprints and the one
   LimiX's repository cites, NBER Working Paper w35905 (copied into
   `Papers\\`; the original in Downloads is left as is), the NVIDIA blog
   article (a local copy saved to `References\\`), and six GitHub
   repositories, each linked `code-of` to its paper.

Everything enters at `seen` (or keeps its tier); reading is the readers'
work, by the Sprint 11 ledger, entered by `scripts/sprint11_reading.py --task F`.

    python scripts/sprint11_f97_intake.py --fetch    # arXiv serial at 18 s, NBER copy, blog page
    python scripts/sprint11_f97_intake.py            # dry run: resolves every entry; nothing written
    python scripts/sprint11_f97_intake.py --apply    # verified backup first
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, recheck, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_source_link, append_updated_reason, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
TAG = "Sprint 11 Task F, F97"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
REFERENCES = Path(r"D:\Data\Harold\EvidenceBasedDB\References")

NEW_ARXIV = ("2610.24426", "2610.10629", "2610.00841", "2509.03505", "2609.17488")
PERE_ARXIV = "2509.16410"  # in the store at `seen` (pere-2025-data-complexity-threshold-between-classical), no copy
NBER_SOURCE = Path(r"D:\Data\Temp\Downloads\w35905.pdf")
NBER_COPY = PAPERS / "2026-10_Farboodi_Credit-Markets-with-New-Screening-Technologies-NBER-w35905.pdf"
BLOG_URL = "https://blogs.nvidia.com/blog/enterprise-platforms-agent-toolkit/"
BLOG_COPY = REFERENCES / "2026_nvidia_enterprise-platforms-agent-toolkit.html"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arxiv_file(ident: str) -> Path | None:
    hits = [p for p in PAPERS.glob("*.pdf") if ident in p.name]
    return hits[0] if hits else None


def arxiv_name(ident: str, md) -> str:
    surname = re.sub(r"[^A-Za-z]", "", (md.authors[0].split(",")[0] if md.authors else "Unattributed"))
    words = re.sub(r"[^A-Za-z0-9 ]", " ", md.title).split()[:9]
    return f"20{ident[:2]}-{ident[2:4]}_{surname}_{'-'.join(words)}_{ident}.pdf"


def fetch() -> int:
    failed = 0
    todo = [i for i in (*NEW_ARXIV, PERE_ARXIV) if arxiv_file(i) is None]
    for i in sorted(set((*NEW_ARXIV, PERE_ARXIV)) - set(todo)):
        print(f"exists  arXiv:{i}  {arxiv_file(i).name}")
    if todo:
        citations.assume_recent_arxiv_request()  # a run started right after another waits the full interval
        fetcher = citations.PacedFetcher()
        meta = citations.fetch_arxiv_batch(todo, fetcher)
        for ident in todo:
            md = meta.get(ident)
            if md is None:
                print(f"FAILED  arXiv:{ident}: no metadata")
                failed += 1
                continue
            target = PAPERS / arxiv_name(ident, md)
            data = fetcher(f"https://arxiv.org/pdf/{ident}", "application/pdf")
            if not data.startswith(b"%PDF"):
                print(f"FAILED  arXiv:{ident}: not a PDF")
                failed += 1
                continue
            target.write_bytes(data)
            first = subprocess.run(["pdftotext", "-l", "1", str(target), "-"], capture_output=True).stdout.decode(
                "utf-8", "replace")
            print(f"saved   arXiv:{ident}  {target.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  "
                  f"{len(data):,} bytes  {'stamp ok' if ident in first else 'NO STAMP: check by hand'}  "
                  f"title: {md.title}")
    if NBER_COPY.exists():
        print(f"exists  {NBER_COPY.name}")
    else:
        shutil.copy2(NBER_SOURCE, NBER_COPY)  # a copy: the original stays where the team lead put it
        print(f"copied  {NBER_COPY.name}  SHA-256 {sha(NBER_COPY)}  (source {sha(NBER_SOURCE)})")
    if BLOG_COPY.exists():
        print(f"exists  {BLOG_COPY.name}")
    else:
        req = urllib.request.Request(BLOG_URL, headers={"User-Agent": "Mozilla/5.0 (EvidenceBasedDB)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        BLOG_COPY.write_bytes(data)
        print(f"saved   {BLOG_COPY.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes")
    return 1 if failed else 0


LOCAL_COPIES = {  # file in Papers\ -> the record it is a copy of (checked by title, 2026-10-22)
    '2020-05_Hoppner_Instance-Dependent-Cost-Sensitive-Learning-for-Detecting-Transfer.pdf':
        'hoppner-2020-instance-dependent-cost-sensitive-learning',
    '2022-01_Elor_To-SMOTE-or-not-to-SMOTE.pdf':
        'elor-2022-smote-or-not-smote',
    '2023-12_Alves_FiFAR-A-Fraud-Detection-Dataset-for-Learning-to.pdf':
        'alves-2023-fifar-fraud-detection-dataset-learning',
    '2023-12_Fey_Relational-Deep-Learning-Graph-Representation-Learning-on-Relational.pdf':
        'fey-2023-relational-deep-learning-graph-representation',
    '2024-01_McDermott_A-Closer-Look-at-AUROC-and-AUPRC-under.pdf':
        'mcdermott-2025-closer-look-auroc-auprc-under',
    '2024-11_Cheng_Graph-Neural-Networks-for-Financial-Fraud-Detection-A.pdf':
        'cheng-2024-graph-neural-networks-financial-fraud',
    '2024-12_Kabane_Impact-of-Sampling-Techniques-and-Data-Leakage-on.pdf':
        'kabane-2024-impact-sampling-techniques-data-leakage',
    '2025-02_Lyu_A-statistical-theory-of-overfitting-for-imbalanced-classification.pdf':
        'lyu-2025-statistical-theory-overfitting-imbalanced-classification',
    '2025-02_Qu_TabICL-A-Tabular-Foundation-Model-for-In-Context.pdf':
        'qu-2025-tabicl-tabular-foundation-model-context',
    '2025-04_Lachi_Boosting-Relational-Deep-Learning-with-Pretrained-Tabular-Models.pdf':
        'lachi-2025-boosting-relational-deep-learning-pretrained',
    '2025-09_Aminian_FraudTransformer-Time-Aware-GPT-for-Transaction-Fraud-Detection.pdf':
        'aminian-2025-fraudtransformer-time-aware-gpt-transaction',
    '2025-10_Vandervorst_Inductive-inference-of-gradient-boosted-decision-trees-on.pdf':
        'vandervorst-2026-inductive-inference-gradient-boosted-decision',
    '2025-10_Xie_Conformal-Inference-for-Open-Set-and-Imbalanced-Classification.pdf':
        'xie-2025-conformal-inference-open-set-imbalanced',
    '2026-04_Cortes_Optimized-Deferral-for-Imbalanced-Settings.pdf':
        'cortes-2026-optimized-deferral-imbalanced-settings',
    '2026-05_Costa_High-Performance-Low-Reliability-Uncertainty-Benchmarking-for-Tabular.pdf':
        'costa-2026-high-performance-low-reliability-uncertainty',
    '2026-06_Liu_The-Hidden-Cost-of-Resampling-How-Imbalance-Correction.pdf':
        'liu-2026-hidden-cost-resampling-how-imbalance',
    'Application-Oriented Performance Benchmarks for Quantum Computing 2110.03137 20230110.pdf':
        'lubinski-2023-application-oriented-benchmarks-qedc',
    'Benchmarking - Application-Oriented Performance Benchmarks for Quantum Computing 2110.03137 20230110.pdf':
        'lubinski-2023-application-oriented-benchmarks-qedc',
    'Benchmarking - Quantum Volume in Practice What Users Can Expect From NISQ Devices - Elijah Pelofske - IEEE '
    '20220610.pdf':
        'pelofske-2022-quantum-volume-nisq-ieee',
    'Benchmarking_simulated_and_physical_quantum_process 2211.1563.pdf':
        'kordzanganeh-2022-benchmarking-simulated-physical-qpu',
    'data-efficient-qml-2508.19437.pdf':
        'sakhnenko-2026-data-efficient-qml',
    'fourier-wall-2607.15815.pdf':
        'mancilla-2026-fourier-wall-spectra',
    'High-Performance Computing with Quantum Processing Units 3007651 2017.pdf':
        'britt-humble-2017-hpc-with-qpus-acm',
    'Homland PQC Quantum Assessment RAND_RRA1367-6.pdf':
        'rand-2022-pqc-critical-infrastructure-assessment',
    'HybridQ - HybridSimulatorforQuantumCircuits arXiv 2111.06868.pdf':
        'mandra-2021-hybridq-simulator-nasa',
    'inverse-born-rule-2602.21350v2.pdf':
        'zajac-2026-inverse-born-rule-equivalence',
    'Mindthe O asymptoticallybetter,butstillimpractical,quantum distributedalgorithms 2304.02825.pdf':
        'kerger-2023-mind-the-o-distributed-quantum-algorithms',
    'Neural Network 2505.16332v1.pdf':
        'wang-2025-quantum-optimization-nn-compression',
    'Photon counting Raman spectroscopy - a benchmarking study vs surface plasmon enhancement oe-32-10-16657 '
    '20240429.pdf':
        'li-2024-photon-counting-raman-spectroscopy',
    'QCI - Financial Fraud Detection with Entropy Computing 2503.11273v1.pdf':
        'emami-2025-financial-fraud-entropy-computing-qci',
    'QML Quantum and Classical Machine Learning in Decentralized Finance 2510.15903v1.pdf':
        'chen-2025-qml-classical-defi',
    'QML Quantum Machine Learning methods for Fourier-based distribution estimation 2510.19494v1.pdf':
        'alonso-2025-qml-fourier-distribution-option-pricing',
    'qstar-2607.21411.pdf':
        'rehman-2026-qstar-adaptive-routing',
    'Quantum Enhanced Greedy Solver for Optimization Problems 2303.05509.pdf':
        'dupont-2023-quantum-enhanced-greedy-solver',
    'Quantum Meta-Learning for Encoding Selection in Quantum Kernel Methods 2609.04652v1.pdf':
        'tung-2026-qmes-quantum-meta-learning-kernel-encoding',
    'Quantum supremacy using a programmable superconducting processor s41586-019-1666-5.pdf':
        'arute-2019-quantum-supremacy-google-nature',
    'Quantum-Inspired Machine Learning - Survey 2308.11269.pdf':
        'huynh-2023-quantum-inspired-ml-survey',
    'The Fourier Wall Why Public Tabular Datasets Refuse Quantum Advantage 2607.15815v1.pdf':
        'mancilla-2026-fourier-wall-spectra',
}

FOUND_VIA = "the team lead, 2026-10-21: \"Can you add these papers to the paper repository and read them as part of F95\""
NEW_PAPERS = [  # (arXiv id or None, entry); the path is filled in by entries()
    ("2610.24426", {"context": "qml", "cited_as": "arXiv 2610.24426 + jyryu98/margin-gen-qml-classical-encoding",
                    "disposition": "A theory paper: margin-based generalization bounds for quantum machine "
                                   "learning with classical data encoding; not yet read"}),
    ("2610.10629", {"context": "ml", "cited_as": "arXiv 2610.10629 + rav11l/cace-bench",
                    "disposition": "LLM agents in credit pipelines that may change only their harness, with a "
                                   "measured admission gate (CACE-Bench); not yet read"}),
    ("2610.00841", {"context": "qml", "cited_as": "arXiv 2610.00841v1",
                    "disposition": "Neural Fourier surrogates for data re-uploading quantum neural networks; not "
                                   "yet read"}),
    ("2509.03505", {"context": "ml", "cited_as": "arXiv 2509.03505 + limix-ldm-ai/LimiX",
                    "disposition": "LimiX, a tabular (structured-data) foundation model; not yet read"}),
    ("2609.17488", {"context": "ml", "cited_as": "LimiX's repository description (pre-flight, 2026-10-21)",
                    "disposition": "LimiX-2, the successor model the LimiX repository cites; not yet read"}),
]
NBER_ENTRY = {"access": f"DOI:10.3386/w35905 | {NBER_COPY}", "context": "ml",
              "cited_as": "D:\\Data\\Temp\\Downloads\\w35905.pdf",
              "disposition": "NBER Working Paper 35905: an economics model of credit markets when lenders adopt "
                             "new screening technologies; not yet read"}
BLOG_ENTRY = {
    "id": "pounds-2026-nvidia-agent-toolkit-enterprise-agents-blog",
    "title": "NVIDIA Agent Toolkit Expands, Grounding Enterprise Agents in Company Data",
    "citation": ("Pounds, E., \"NVIDIA Agent Toolkit Expands, Grounding Enterprise Agents in Company Data,\" NVIDIA "
                 f"Blog, 2026-10-21, {BLOG_URL} (hand-transcribed from the saved page's og:title, author and "
                 "article:published_time tags)"),
    "transcribed_from": (f"the page's own meta tags (og:title, author, article:published_time), local copy "
                         f"{BLOG_COPY}, saved {TODAY}"),
    "access": f"{BLOG_COPY} | {BLOG_URL}", "context": "ml", "kind": "paper",
    "cited_as": BLOG_URL,
    "disposition": "Vendor announcement: the NVIDIA Agent Toolkit and its new Auto-Ontology library, which maps "
                   "company data to business concepts; not yet read",
}
EVAL_DECISION = ("team lead, 2026-10-22, Sprint 11 Manual Validation Q1 = 2: link it to the blog record. No source "
                 "names it as the article's code: the article does not mention it, and GitHub describes it as a "
                 "Text-to-SQL evaluation toolkit. The link rests on the team lead's decision")
EVAL_DISPOSITION = ("Code repository: named with the NVIDIA blog article in the team lead's list; the article does "
                    "not name it; linked to the article on the team lead's decision (2026-10-22); not yet screened")
EVAL_UNLINKED = "it is linked to no paper"
REPOS = [  # (owner/name as the team lead gave it, the paper it is code of, evidence for the link)
    ("NVIDIA/auto-ontology", "blog",
     f"the blog article links https://github.com/NVIDIA/auto-ontology from \"the new Auto-Ontology library\" "
     f"(local copy {BLOG_COPY.name})"),
    # Entered unlinked at first: the blog article never names it, and GitHub
    # describes it as a Text-to-SQL evaluation toolkit. Linked at Manual
    # Validation on the team lead's decision, which the evidence names.
    ("NVIDIA/auto-ontology-eval", "blog", EVAL_DECISION),
    ("jyryu98/margin-gen-qml-classical-encoding", "2610.24426",
     "\"The code can be found in the following repository: https://github.com/jyryu98/margin-gen-qml-classical"
     "encoding\" (Code Availability; the hyphen falls at a line break)"),
    ("Christophe-pere/data_complexity_framework", "2509.16410",
     "\"All code, specifications, frozen dataset registry, logged deviations and raw results are released at "
     "https://github.com/Christophe-pere/data_complexity_framework\" (Data and code availability)"),
    ("rav11l/cace-bench", "2610.10629",
     "\"All code, configuration and per-run outputs, including every gate log, are available in the CACE-Bench "
     "repository at https://github.com/rav11l/cace-bench\" (availability of data and materials)"),
    ("limix-ldm-ai/LimiX", "2509.03505",
     "the title page prints https://github.com/limix-ldm/LimiX/ (GitHub answers limix-ldm-ai/LimiX)"),
    ("limix-ldm-ai/LimiX", "2609.17488",
     "the title page prints https://github.com/limix-ldm/LimiX/; the repository's description cites this paper"),
]


def entries() -> list[dict]:
    out = []
    for ident, extra in NEW_PAPERS:
        path = arxiv_file(ident)
        out.append(dict(extra, access=f"arXiv:{ident} | {path}", found_via=FOUND_VIA,
                        evidence=f"Local copy {path.name}, SHA-256 {sha(path)}, fetched {TODAY} (paced fetcher)",
                        updated_reason=f"{TODAY}: added by scripts/sprint11_f97_intake.py ({TAG})"))
    out.append(dict(NBER_ENTRY, found_via=FOUND_VIA,
                    evidence=f"Local copy {NBER_COPY.name}, SHA-256 {sha(NBER_COPY)}, copied {TODAY} from "
                             f"{NBER_SOURCE} (left in place)",
                    updated_reason=f"{TODAY}: added by scripts/sprint11_f97_intake.py ({TAG})"))
    out.append(dict(BLOG_ENTRY, found_via=FOUND_VIA,
                    evidence=f"Local copy {BLOG_COPY.name}, SHA-256 {sha(BLOG_COPY)}, saved {TODAY}",
                    updated_reason=f"{TODAY}: added by scripts/sprint11_f97_intake.py ({TAG})"))
    return out


def counts(conn) -> str:
    tiers = dict(conn.execute("SELECT tier, COUNT(*) FROM paper_fields GROUP BY tier").fetchall())
    n = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'assertion'").fetchone()[0]
    return f"papers {sum(tiers.values())} ({', '.join(f'{k} {v}' for k, v in sorted(tiers.items()))}); assertions {n}"


def link_copy(conn, rid: str, path: Path, log: list[str], apply: bool) -> None:
    access, evidence = conn.execute("SELECT access, evidence FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
    if str(path).lower() in {s.lower() for s in recheck.local_paths(access or "")}:
        log.append(f"exists copy {rid}: {path.name}")
        return
    note = f"Local copy {path.name}, SHA-256 {sha(path)}, linked {TODAY} (F97)"
    if apply:
        conn.execute("UPDATE paper_fields SET access = ?, evidence = ? WHERE record_id = ?",
                     (f"{access} | {path}" if access else str(path),
                      f"{evidence.rstrip()}; {note}" if evidence and evidence.strip() else note, rid))
        append_updated_reason(conn, rid, f"{TODAY} ({TAG}): local copy added to access", TODAY)
    log.append(f"copy   {rid}: {path.name}")


def existing(conn, access: str) -> str | None:
    """The record whose access holds this arXiv id or URL as a whole token,
    if one does (case-insensitive: GitHub answers in its own case; whole,
    so NVIDIA/auto-ontology never finds NVIDIA/auto-ontology-eval)."""
    want = access.lower().rstrip("/")
    for rid, held in conn.execute("SELECT record_id, access FROM paper_fields WHERE lower(access) LIKE ?",
                                  (f"%{want}%",)):
        if want in {token.strip().lower().rstrip("/") for token in held.split(" | ")}:
            return rid
    return None


def apply_changes(conn, apply: bool) -> list[str]:
    log = [f"before: {counts(conn)}"]
    for name, rid in LOCAL_COPIES.items():
        if not conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (rid,)).fetchone():
            raise LookupError(f"{rid}: not in the store")
        link_copy(conn, rid, PAPERS / name, log, apply)
    pere = conn.execute("SELECT record_id FROM paper_fields WHERE access LIKE ?", (f"%{PERE_ARXIV}%",)).fetchone()[0]
    link_copy(conn, pere, arxiv_file(PERE_ARXIV), log, apply)
    ids = {}
    for entry in entries():
        key = "blog" if entry.get("id") == BLOG_ENTRY["id"] else (
            entry["access"].split(" | ")[0].removeprefix("arXiv:"))
        # An entry already in the store is found by its access before it is
        # resolved: a second apply otherwise asked arXiv and GitHub again,
        # 18 s apart, about 80 s of the suite (F100, Sprint 12).
        held = existing(conn, entry["access"].split(" | ")[0])
        if held:
            ids[key] = held
            log.append(f"exists {held}")
            continue
        record = intake.build_record(entry, today=TODAY)
        ids[key] = record.id
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (record.id,)).fetchone():
            log.append(f"exists {record.id}")
            continue
        if apply:
            insert_paper(conn, record)
        log.append(f"paper  {record.id} [{record.tier}, {record.citation_origin}]  {record.value[:70]}")
    ids[PERE_ARXIV] = pere
    repo_ids = {}
    for owner_name, paper_key, evidence in REPOS:
        if owner_name not in repo_ids and (held := existing(conn, f"https://github.com/{owner_name}")):
            repo_ids[owner_name] = held
            log.append(f"exists {held}")
        if owner_name not in repo_ids:
            record = intake.build_record({"access": f"https://github.com/{owner_name}", "kind": "repo",
                                          "context": "ml" if paper_key in (None, "blog", "2610.10629", "2509.03505")
                                          else "qml",
                                          "disposition": (EVAL_DISPOSITION if evidence == EVAL_DECISION else
                                                          f"Code repository: named with {paper_key} in the team "
                                                          "lead's list; not yet screened"),
                                          "found_via": FOUND_VIA, "cited_as": f"github.com/{owner_name}"}, today=TODAY)
            repo_ids[owner_name] = record.id
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (record.id,)).fetchone():
                log.append(f"exists {record.id}")
            else:
                if apply:
                    insert_paper(conn, record)
                log.append(f"repo   {record.id}  ({record.value[:60]})")
        rid, paper = repo_ids[owner_name], ids[paper_key]
        if evidence == EVAL_DECISION:
            old = conn.execute("SELECT disposition FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()
            if old and EVAL_UNLINKED in (old[0] or ""):
                if apply:
                    conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?",
                                 (EVAL_DISPOSITION, rid))
                    append_updated_reason(conn, rid, f"{TODAY} (Sprint 11 Manual Validation, Q1 = 2): linked "
                                          "code-of the NVIDIA blog record on the team lead's decision; no source "
                                          "names it as the article's code", TODAY)
                log.append(f"disp   {rid}: linked on the team lead's decision")
        if conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = 'code-of'",
                        (rid, paper)).fetchone():
            log.append(f"exists link {rid} code-of {paper}")
            continue
        if apply:
            add_source_link(conn, rid, paper, "code-of", evidence)
        log.append(f"link   {rid} code-of {paper}")
    if apply:
        log.append(f"after:  {counts(conn)}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        return fetch()
    missing = [n for n in LOCAL_COPIES if not (PAPERS / n).exists()]
    missing += [i for i in (*NEW_ARXIV, PERE_ARXIV) if arxiv_file(i) is None]
    missing += [str(p) for p in (NBER_COPY, BLOG_COPY) if not p.exists()]
    if missing:
        print("missing local copies (run --fetch):\n" + "\n".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F97 new papers and the team lead's list")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn, apply)
        if apply:
            conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
