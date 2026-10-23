#!/usr/bin/env python3
"""Sprint 12 Task A (F101): HTML entities out of stored citations, and the
Cyc quote made whole. INTAKE_WORKFLOW.md section 42.

(1) Every text field holding an HTML entity is unescaped: 4 records as of
2026-10-23, all "&amp;" from Crossref or DataCite (titles in `value`,
citations in `provenance`). The ids are keys and are not renamed. The
records are found by a scan, not by a list, so a record that gained an
entity later is caught too; `store.citations` now unescapes at the source.

(2) Every stored quote the quote pattern never parsed, made whole (Sprint
11 retrospective I1a's check over the whole store): `cyc-2007-eight-tactic-types`,
whose first quote held the source's own `"split" (`, and three Sprint 1
and 2 assertions whose quotes carried no anchor. Each is re-quoted from
its source with anchors, plus a quote for any figure the value states;
the values are unchanged. Lenat and Marcus 2023 had no local copy; `--fetch`
saves its free arXiv PDF (one paced request) and `--apply` adds it to the
record's access.

DRY RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import html
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, append_updated_reason, sync_verified_assertion  # noqa: E402
from store.quotes import plain, require_edit_basis, require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
NOTE = f"{TODAY} (Sprint 12 Task A, F101): INTAKE_WORKFLOW.md section 42"

ENTITY = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")
# The record columns that hold source-derived text; ids and dates are keys.
ENTITY_COLUMNS = ("value", "provenance")

PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
LENAT = "lenat-marcus-2023-trustworthy-ai"
LENAT_PDF = PAPERS / "2023-08_Lenat_Getting-from-Generative-AI-to-Trustworthy-AI-What-LLMs-might.pdf"
DE_LORENZIS_PDF = PAPERS / "2025-09_De-Lorenzis_Entanglement-and-Classical-Simulability-in-Quantum-Extreme-Learning.pdf"
KAKAVAND_PDF = PAPERS / "2026-04_Kakavand_Benchmarking-Quantum-Kernel-Support-Vector-Machines-Against-Classical.pdf"
SWEKE_PDF = PAPERS / "2023-09_Sweke_Potential-and-limitations-of-random-Fourier-features-for.pdf"
# Papers with no local copy that a re-quoted assertion needs: record id ->
# (arXiv id, local path). `--fetch` saves each free arXiv PDF, one paced
# request apiece; `--apply` adds the path to the record's access.
LOCAL_COPIES = {
    LENAT: ("2308.04445", LENAT_PDF),
    "de-lorenzis-2026-entanglement-classical-simulability-quantum-extreme": ("2509.06873v3", DE_LORENZIS_PDF),
    "kakavand-2026-benchmarking-quantum-kernel-support-vector": ("2604.18837v1", KAKAVAND_PDF),
    "sweke-2025-potential-limitations-random-fourier-features": ("2309.11647v4", SWEKE_PDF),
}
TAYLOR_PDF = r"D:\Data\Harold\EvidenceBasedDB\Papers\2007-03_Taylor_Guiding-Inference-with-Policy-Search-Reinforcement-Learning.pdf"
MCDERMOTT_PDF = str(PAPERS / "2024-01_McDermott_A-Closer-Look-at-AUROC-and-AUPRC-under.pdf")
ELOR_PDF = str(PAPERS / "2022-01_Elor_To-SMOTE-or-not-to-SMOTE.pdf")
LIU_PDF = str(PAPERS / "2026-06_Liu_The-Hidden-Cost-of-Resampling-How-Imbalance-Correction.pdf")
# Read at the file's last commit, not from the working copy, so a later
# checkout there cannot change what the check reads (fresh-eyes review).
PREREGISTRATION = ("git", r"D:\Data\Harold\github\hsbc-quantum-fraud-2026", "7261e4e", "experiments/PREREGISTRATION.md")

# Each quote the quote pattern never parsed (section 42), made whole: record
# id -> (its source, [(passage, anchor), ...]). Every passage is verbatim in
# the source and is the edit's basis; the values are unchanged.
QUOTE_FIXES = {
    "cyc-2007-eight-tactic-types": (TAYLOR_PDF, [
        ("There are eight tactic types which describes the kind of operation to be performed, such as",
         "p.147; quoted in two parts around the source's own quoted word split, whose quotation marks would "
         "end the quote"),
        ("(i.e. split a conjunction into two sub-problems).", "p.147"),
        ("Of the eight tactic types available in ResearchCyc, the RL Tactician currently only handles five.",
         'p.148; the "fi" ligature normalized'),
        ("2007, American Association for Artificial Intelligence", "p.146, the copyright line; the year in the value"),
    ]),
    "cyc-general-prover-disabled": (str(LENAT_PDF), [
        ("over a million queries in a row that called on it, as a last resort, just timed out.", "p.14, footnote 9"),
        ("So, about one decade ago, we quietly turned the general theorem prover off, so it never gets called on!",
         "p.14, footnote 9"),
        ("July 31, 2023", "p.1, the paper's date; the year in the value"),
    ]),
    "heuristics-over-general-reasoning": (str(LENAT_PDF), [
        ("Cyc addresses this by separating the epistemological problem -- what does the system know? -- from the "
         "heuristic problem -- how can it reason efficiently?", "p.13"),
        ("Cyc also allows multiple redundant representations for each assertion, and in practice it uses multiple "
         "redundant, specialized reasoners -- Heuristic Level (HL) modules -- each of which is much faster than "
         "general theorem-proving when it applies.", "p.13"),
        ("By 1989, Cyc had 20 such high-level reasoners [Lenat&Guha 1990]; today it has over 1,100.", "p.13"),
        ("July 31, 2023", "p.1, the paper's date; the year in the value"),
    ]),
    "hsbc-b1-variable-count": (PREREGISTRATION, [
        ("B1's variable count read 78 in three places and 91 in two -- B1 ran the FULL pair build at k=13, which is "
         "91; 78 is the SEQUENTIAL count and belongs to the IEEE-CIS arm, and the B2/B1 ratio is 9.2x not 10.7x.",
         "PREREGISTRATION.md at hsbc-quantum-fraud-2026 commit 7261e4e, amendment A30 of 2026-09-10"),
    ]),
    # The 7 Sprint 5 Task I contexts that held a passage with no quote marks
    # at all, so no check ever read them (fresh-eyes review of 5466953).
    # Anchors are PDF page indexes; where a paper prints page numbers, they
    # are the same.
    "auprc-not-generally-superior-under-imbalance": (MCDERMOTT_PDF, [
        ("AUROC and AUPRC only differ with respect to model-dependent parameters in that AUROC weighs all false "
         "positives equally, whereas AUPRC weighs false positives at a threshold τ with the inverse of the model's "
         "likelihood of outputting any scores greater than τ", "p.2 section 1, contribution 1, citing Theorem 1"),
        ("AUPRC prioritizes high-score mistakes, AUROC treats all mistakes equally", "p.4 section 2.2 heading, Theorem 2"),
        ("If the model f is calibrated and the rate at which y = 1 for population a = 0 is sufficiently low relative "
         "to the rate at which y = 1 for population a = 1, then the mistake that, were it fixed, would maximally "
         "improve the AUPRC of f will be a mistake purely in population a = 1. This demonstrates that AUPRC provably "
         "favors higher prevalence subpopulations", "p.5 section 2.3, Theorem 3"),
        ("establishing clearly that AUPRC is not generally superior in cases of class imbalance", "p.1 abstract"),
        ("we have shown that AUPRC is not universally superior in cases of class imbalance", "p.8 section 4"),
    ]),
    "oversampling-helps-weak-not-strong-boosters": (ELOR_PDF, [
        ("imbalanced binary classification in tabular data", "p.1 abstract"),
        ("Finally, we experimented with the remaining 73 datasets.", "p.2 section 3.1"),
        ("Random Oversampling (Random), where minority samples are randomly duplicated. SMOTE [6]. SVM-SMOTE (SVM-SM) "
         "[30], a SMOTE variant", "p.3 section 3.3"),
        ("ADASYN [15], an adaptive synthetic oversampling approach", "p.3 section 3.3"),
        ("Polynomfit SMOTE (Poly) [12], a variant of SMOTE", "p.3 section 3.3"),
        ("we use AUC, the proper (and popular) metric", "p.4 section 4.1"),
        ("Considering validation HPs, presented in Figure 1(b), balancing significantly improved prediction for the "
         "weak classifiers: MLP, SVM, decision tree, Adaboost and LGBM. However, for the stronger classifiers, "
         "XGBoost and Catboost, it did not.", "p.4 section 4.1"),
        ("To summarize, except for very weak classifiers (MLP and SVM), balancing the data and optimizing the "
         "decision threshold yield comparable prediction performance.",
         "p.5 section 4.3 (F1), after Table 3; the text layer garbles the italic F1"),
        ("The decision threshold could not be optimized for SVM as it outputs only class predictions",
         "p.4 footnote 5"),
    ]),
    "qelm-local-dynamics-match-haar-classically-simulable": (str(DE_LORENZIS_PDF), [
        ("Our architecture combines dimensionality reduction (via PCA or Autoencoders), quantum state encoding, "
         "evolution under an XX Hamiltonian", "p.1 abstract"),
        ("Remarkably, the saturated performance is comparable to that obtained using Haar-random unitaries that "
         "generate maximally complex dynamics, even though the XX model is integrable and local.", "p.1 abstract"),
        ("For the image-classification tasks studied here, namely MNIST, Fashion-MNIST, and CIFAR-10",
         "p.1 abstract"),
        ("This suggests that QELM performance in this regime relies only on limited entanglement and remains "
         "compatible with efficient classical simulation.", "p.1 abstract"),
        ("For the simpler datasets, such as MNIST and Fashion-MNIST, we employed between 6 and 10 qubits, whereas "
         "for the more complex dataset CIFAR-10, results were plotted for 6 to 11 qubits.", "p.5 section 4"),
        ("the limited depth and moderate entanglement observed in this regime suggest compatibility with efficient "
         "classical simulation, though larger-scale studies would be needed to assess the generality of this "
         "conclusion.", "p.11 section 8 Conclusions and Outlook"),
    ]),
    "qksvm-classical-kernels-better-on-uci-tabular": (str(KAKAVAND_PDF), [
        ("We evaluate on nine binary classification datasets from the UCI Machine Learning Repository [Dua and "
         "Graff, 2017] and OpenML [Vanschoren et al., 2014]", "p.7 section 4.1"),
        ("All experiments use stratified nested cross-validation", "p.10 section 4.6"),
        ("Classical kernels dominate on 8/9 datasets; haberman is the sole exception.", "p.14 Figure 1 caption"),
        ("None of the 29 pairwise comparisons reach statistical significance at α = 0.05.", "p.14 section 6.2"),
        ("With 16 paired observations (vs. 5 in Phase 1), Wilcoxon tests now achieve sufficient statistical power: "
         "all 7 datasets show significant differences at α = 0.05.", "p.19 section 6.5"),
        ("On 6/7 datasets, classical kernels are significantly better (p < 0.001). On haberman, quantum kernels are "
         "significantly better (p = 0.004), winning on 14/16 seeds.", "p.19 section 6.5"),
        ("The quantum advantage on haberman (+1.9 pp mean, p = 0.004, 87.5% win rate) persists across random seed "
         "perturbation", "p.19 section 6.5"),
        ("Table 9 reports the stability of balanced accuracy across 16 random seeds", "p.19 section 6.5"),
    ]),
    "resampling-degrades-calibration-recalibration-repairs": (LIU_PDF, [
        ("Across five public datasets (imbalance ratio 1.9–70) and two ensemble models (random forest, gradient "
         "boosting)", "p.1 abstract"),
        ("We use five real public binary-classification datasets from OpenML", "p.2 section IV-A"),
        ("Models are scikit-learn's random forest", "p.3 section IV-B"),
        ("and histogram gradient boosting", "p.3 section IV-B"),
        ("The effect is small-to-moderate for SMOTE (0.052 → 0.061, δ = +0.27) and random oversampling (→ 0.064, "
         "δ = +0.26), but large for random undersampling (→ 0.186, δ = +0.77).", "p.3 section V-B"),
        ("The class-weight control moves ECE only marginally (→ 0.058), indicating the harm comes specifically from "
         "altering the training data, not merely from rebalancing the objective", "p.3 section V-B"),
        ("One post-hoc step repairs the damage", "p.3 section V-C heading"),
        ("Platt and isotonic recalibration reduce the SMOTE model's ECE from 0.061 to 0.021 and 0.025 respectively",
         "p.3 section V-C"),
        ("below even the unsampled baseline", "p.3 section V-C"),
    ]),
    "rff-not-generic-dequantizer-but-matches-some-pqcs": (str(SWEKE_PDF), [
        ("RFF-based linear regression cannot be a generic dequantization technique.", "p.3 section 1, main result 1"),
        ("There exist practically relevant PQCs, and regression problems, for which RFF-based linear regression can "
         "be guaranteed to efficiently produce output models which perform as well as the best possible output of "
         "PQC based optimization.", "p.3 section 1, main result 2"),
        ("the true risk of the output hypothesis of RFF-based linear regression is no more than ϵ worse than the "
         "true risk of the best possible function realizable by the PQC architecture",
         "p.13 section 4.2, before Theorem 1"),
        ("in this case Theorem 1 guarantees that Algorithm 3 (RFF-based linear regression) provides an efficient "
         "dequantization of variational QML.", "p.14 section 4.2, after Theorem 1"),
    ]),
    "wilcoxon-n5-floor-is-not-parity": (str(KAKAVAND_PDF), [
        ("The minimum achievable two-sided p-value for the exact Wilcoxon signed-rank test with n = 5 paired "
         "observations is p = 0.0625, which places a fundamental floor on statistical power.", "p.14 section 6.2"),
        ("None of the 29 pairwise comparisons reach statistical significance at α = 0.05.", "p.14 section 6.2"),
        ("The lack of Wilcoxon significance is thus a sample-size limitation (n = 5), not an absence of performance "
         "differences.", "p.14 section 6.2"),
    ]),
}

# Values the re-quoting showed to say more or less than their source (the
# quote agent's reading, checked here): each is replaced, and its passages
# above are the edit's basis (`require_edit_basis` with the new value).
VALUE_FIXES = {
    "oversampling-helps-weak-not-strong-boosters": (
        "Across 73 tabular datasets with validation-tuned hyperparameters, oversampling (random, SMOTE and three "
        "variants) improved AUC for weak classifiers (MLP, SVM, decision tree, AdaBoost, LightGBM) but not for "
        "XGBoost or CatBoost; for F1, tuning the decision threshold matched balancing except for the very weak MLP "
        "and SVM, whose threshold could not be tuned because it outputs only class predictions"),
    "qelm-local-dynamics-match-haar-classically-simulable": (
        "For quantum extreme learning machines on PCA- or autoencoder-reduced MNIST and Fashion-MNIST (6 to 10 "
        "qubits) and CIFAR-10 (6 to 11 qubits), a local integrable XX evolution reached accuracy comparable to "
        "Haar-random unitaries, with limited entanglement that the authors suggest is compatible with efficient "
        "classical simulation, though larger-scale studies would be needed"),
    "qksvm-classical-kernels-better-on-uci-tabular": (
        "On nine binary tabular datasets from UCI and OpenML with nested cross-validation, classical kernel SVMs "
        "had higher balanced accuracy than the best quantum-kernel SVM on 8 of 9, though none of the 29 five-fold "
        "comparisons was significant; with 16 paired seeds, classical kernels were significantly better on 6 of 7 "
        "datasets (p < 0.001) and a quantum kernel was significantly better only on haberman (+1.9 percentage "
        "points balanced accuracy, p = 0.004)"),
    "resampling-degrades-calibration-recalibration-repairs": (
        "On five OpenML datasets (imbalance ratio 1.9 to 70) with random forest and histogram gradient boosting, "
        "SMOTE and random oversampling raised expected calibration error by a small-to-moderate amount and random "
        "undersampling by a large one; one Platt or isotonic recalibration step brought the SMOTE model's ECE from "
        "0.061 to 0.021 or 0.025, below the unsampled baseline"),
}


def context_of(passages: list[tuple[str, str]]) -> str:
    return "; ".join(f'"{q}" ({anchor})' for q, anchor in passages)


def fetch_copies() -> list[str]:
    """The free arXiv copy of each paper in LOCAL_COPIES, through one paced
    fetcher (serial, 18 s rule); an existing file is never overwritten."""
    fetch, log = citations.PacedFetcher(), []
    for arxiv, path in LOCAL_COPIES.values():
        if path.exists():
            log.append(f"exists  {path.name}")
            continue
        data = fetch(f"https://arxiv.org/pdf/{arxiv}", "application/pdf")
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"not a PDF: arXiv {arxiv}")
        path.write_bytes(data)
        log.append(f"saved   {path.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes")
    return log


def entity_rows(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(record id, column, stored text) for every record column holding an entity."""
    out = []
    for column in ENTITY_COLUMNS:
        for rid, text in conn.execute(f"SELECT id, {column} FROM records WHERE {column} LIKE '%&%;%'"):
            if text and ENTITY.search(text):
                out.append((rid, column, text))
    return out


def stored_assertion(conn: sqlite3.Connection, rid: str) -> AssertionRecord:
    r = conn.execute("SELECT value, provenance, evidence_tag, certainty, certainty_reasons, fidelity, reading_level "
                     "FROM records WHERE id = ? AND class = 'assertion'", (rid,)).fetchone()
    f = conn.execute("SELECT units, rounding, citation_context, derivation, claim_type, search_scope "
                     "FROM assertion_fields WHERE record_id = ?", (rid,)).fetchone()
    context = conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ? ORDER BY context_id",
                           (rid,)).fetchone()[0]
    return AssertionRecord(id=rid, value=r[0], provenance=r[1], evidence_tag=r[2], context=context,
                           certainty=r[3], certainty_reasons=r[4], fidelity=r[5], reading_level=r[6],
                           units=f[0], rounding=f[1], citation_context=f[2], derivation=f[3], claim_type=f[4],
                           search_scope=f[5])


def text_of(source) -> str:
    """A local file's text, or a file's text at a named commit of a repository."""
    if isinstance(source, tuple):
        _, repo, commit, name = source
        raw = subprocess.run(["git", "-C", repo, "show", f"{commit}:{name}"], capture_output=True, check=True,
                             encoding="utf-8").stdout
        return plain(raw)
    return source_text(source)


def whole(conn: sqlite3.Connection, rid: str):
    """The assertion with its quotes made whole, and the check that licenses the write."""
    source, passages = QUOTE_FIXES[rid]
    wanted = stored_assertion(conn, rid)
    wanted.citation_context = context_of(passages)
    wanted.value = VALUE_FIXES.get(rid, wanted.value)
    text = text_of(source)
    require_edit_basis(rid, VALUE_FIXES.get(rid), [q for q, _ in passages], text)
    return wanted, require_verbatim(rid, wanted.citation_context, text, value=wanted.value)


def access_with_copy(conn: sqlite3.Connection, rid: str) -> str | None:
    """The paper's access with its local copy added, or None when it already names it."""
    access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0]
    path = LOCAL_COPIES[rid][1]
    return None if str(path) in access else f"{access} | {path}"


def evidence_with_hash(conn: sqlite3.Connection, rid: str) -> str | None:
    """The paper's evidence with its local copy's SHA-256 added (F48: every
    local file carries one; the first apply left Lenat's out), or None when
    it already holds it."""
    evidence = conn.execute("SELECT evidence FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] or ""
    path = LOCAL_COPIES[rid][1]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest in evidence:
        return None
    note = f"Local copy {path.name}, SHA-256 {digest}, fetched from arXiv {LOCAL_COPIES[rid][0]} on {TODAY} (F101)"
    return f"{evidence.rstrip()}; {note}" if evidence.strip() else note


def apply_changes(conn: sqlite3.Connection) -> list[str]:
    log = []
    for rid, column, text in entity_rows(conn):
        conn.execute(f"UPDATE records SET {column} = ? WHERE id = ?", (html.unescape(text), rid))
        append_updated_reason(conn, rid, f"{NOTE}: HTML escapes in {column} undone (from the metadata provider)",
                              TODAY)
        log.append(f"unescaped {rid}.{column}")
    for paper in LOCAL_COPIES:
        access = access_with_copy(conn, paper)
        if access:
            conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (access, paper))
            append_updated_reason(conn, paper, f"{NOTE}: local copy added to access", TODAY)
            log.append(f"{paper}: local copy added to access")
        evidence = evidence_with_hash(conn, paper)
        if evidence:
            conn.execute("UPDATE paper_fields SET evidence = ? WHERE record_id = ?", (evidence, paper))
            append_updated_reason(conn, paper, f"{NOTE}: local copy's SHA-256 added to evidence", TODAY)
            log.append(f"{paper}: SHA-256 added to evidence")
    for rid in QUOTE_FIXES:
        wanted, verified = whole(conn, rid)
        changed = sync_verified_assertion(conn, wanted, verified, f"{NOTE}: quote made whole", TODAY)
        log.append(f"{rid}: {', '.join(changed) if changed else 'already whole'}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        print("\n".join(fetch_copies()))
        return 0
    conn = connect(DB_PATH)
    if "--apply" not in args:
        try:
            for rid, column, text in entity_rows(conn):
                print(f"would unescape {rid}.{column}: {text[:90]!r}")
            for paper in LOCAL_COPIES:
                if access_with_copy(conn, paper):
                    print(f"would add the local copy to {paper}'s access")
                if evidence_with_hash(conn, paper):
                    print(f"would add the local copy's SHA-256 to {paper}'s evidence")
            for rid in QUOTE_FIXES:
                wanted, _ = whole(conn, rid)  # the checks the write runs; nothing written
                stored = stored_assertion(conn, rid).citation_context
                fixed = " and value" if rid in VALUE_FIXES else ""
                print(f"{rid}: {'already whole' if stored == wanted.citation_context else 'would sync citation_context' + fixed}")
        finally:
            conn.close()
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    conn.close()
    backup_before_write(DB_PATH, "F101 entities and the unparsed quotes")
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
