#!/usr/bin/env python3
"""F54 (Sprint 7 Task E): recover the 30 repository notes that did not link
in Sprint 6 Task K.

Each note's own URL failed: 23 returned HTTP 404 (most were cut short or
lost a hyphen or underscore at a line wrap in the note extractor), 6 were
not GitHub links (Zenodo, Gitee, a malformed URL), and one belongs to the
malformed `2108.0131`. Every resolution below says how it was found, and
that sentence is appended to the link's evidence, after the paper's own
sentence the note quotes (team lead, 2026-10-05: a match found by search
is recorded as found by search, with the query):

- OWNER LIST: the owner's public repositories (GitHub API
  users/<owner>/repos, 2026-10-06) hold exactly one repository with the
  note's name once punctuation is ignored.
- PAPER TEXT: the paper's own PDF (QMLPapers, read with pdftotext,
  2026-10-06) prints the full name; an underscore extracts as a space.
- SEARCH: GitHub repository search, with the query.
- ZENODO: the note's Zenodo record, entered by its DOI (DataCite), with
  DataCite's resource type deciding code-of or dataset-of.

Reported again, with what was tried: see UNRESOLVED.

DRY-RUN BY DEFAULT. `--apply` takes a verified backup, then writes per note
(repository record if absent, then the link) and commits each.

    python scripts/sprint7_f54_recover_repo_notes.py
    python scripts/sprint7_f54_recover_repo_notes.py --apply
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import add_found_via, add_source_link, insert_paper  # noqa: E402

_spec = importlib.util.spec_from_file_location("link_code_repositories",
                                               Path(__file__).with_name("link_code_repositories.py"))
linker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(linker)
intake = linker.intake

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)

OWNER_LIST = ("the note's URL lost punctuation at a line wrap; the owner's public repositories (GitHub API "
              "users/{owner}/repos, 2026-10-06) hold exactly one with this name ignoring punctuation")
PAPER_TEXT = "the paper's own PDF prints the full name ({printed}), read 2026-10-06; the note's URL was cut short"

# note file prefix -> [(access, link_type, how found)]
RESOLVED: dict[str, list[tuple[str, str, str]]] = {
    "Acedo-et-al._2025": [("https://github.com/nacedob/Pulsed-Data-Reuploading-Quantum-Models", "code-of", OWNER_LIST)],
    "Ahmed-et-al._2022": [("https://github.com/quantshah/quantum-implicit-differentiation", "code-of", OWNER_LIST)],
    "Brunet-et-al._2023": [("https://github.com/QuantumRadioAstronomy/MA2-project_QuantumRadioImage", "code-of", OWNER_LIST)],
    "Casse-et-al._2024": [("https://github.com/LeaCasse/QRU_Calorimetry_Optimization", "code-of", OWNER_LIST)],
    "Lubinski-et-al._2024": [("https://github.com/SRI-International/QC-App-Oriented-Benchmarks", "code-of", OWNER_LIST)],
    "Matsumoto-et-al._2025": [("https://github.com/FujitsuResearch/Iterative-Quantum-Feature-Maps", "code-of", OWNER_LIST)],
    "Ptacek-Lewandowska-Kukulski_2025": [
        ("https://github.com/Weliras/RESOURCE-EFFICIENT-VARIATIONAL-QUANTUM-CLASSIFIER", "code-of", OWNER_LIST)],
    "Vijendran-et-al._2023": [("https://github.com/vijeycreative/XQAOA-Dataset", "code-of", OWNER_LIST)],
    "Zia-et-al._2025": [("https://github.com/salvatore-lorenzo/arXiv-2502.18361-QELM_WITNESS", "code-of", OWNER_LIST)],
    "Heimann-Schonhoff-Franck-Kirchner_2022": [
        ("https://github.com/dfki-ric-quantum/learning_capability", "code-of",
         PAPER_TEXT.format(printed="github.com/dfki-ric-quantum/learning_capability"))],
    "Incudini-Martini-Di-Pierro_2022": [
        ("https://github.com/Dan-LB/Quantum_Kernel_Discovery_AD_HEP", "code-of",
         PAPER_TEXT.format(printed="github.com/Dan-LB/Quantum Kernel Discovery AD HEP"))],
    "Mao-Shresthamali-Kondo_2023": [
        ("https://github.com/yikaimao/Q_fid", "code-of", PAPER_TEXT.format(printed="github.com/yikaimao/Q fid"))],
    "Novak-et-al._2025": [
        ("https://github.com/VojtechNovak/qnn_leak", "code-of", PAPER_TEXT.format(printed="github.com/VojtechNovak/qnn leak"))],
    "Park-et-al._2022": [
        ("https://github.com/yukwangmin/QMP_GS", "code-of", PAPER_TEXT.format(printed="github.com/yukwangmin/QMP GS"))],
    "Wilkie-et-al._2025": [
        ("https://github.com/Vilcius/constraint_gadgets", "code-of",
         PAPER_TEXT.format(printed="github.com/Vilcius/constraint gadgets"))],
    "Zhang-et-al._2024": [
        ("https://github.com/zhihan-z/MCM_Learnability", "code-of",
         PAPER_TEXT.format(printed="github.com/zhihan-z/MCM_Learnability"))],
    # The paper prints two code repositories for its QNN and QSVC; the note's
    # cut-short "Data" matches both. (Its third, a dataset generator, is not
    # this note's link.)
    "Ravindra-Shinde-Nurminen_2025": [
        ("https://github.com/AakashShindeHelsinki/Data_Reduction_and_QCNN", "code-of",
         PAPER_TEXT.format(printed="QNN: github.com/AakashShindeHelsinki/Data Reduction and QCNN")),
        ("https://github.com/AakashShindeHelsinki/Data_Reduction_Q-SVM", "code-of",
         PAPER_TEXT.format(printed="QSVC: github.com/AakashShindeHelsinki/Data Reduction Q-SVM.git"))],
    "Peham-Burgholzer_2022": [
        ("https://github.com/cda-tum/qcec", "code-of",
         "the note's URL carried the sentence's following text (\")--with\"); the paper prints github.com/cda-tum/qcec")],
    "Delilbasic-et-al._2026": [
        ("https://github.com/ArturMiroszewski/Large_scale_QSVM", "code-of",
         "found by GitHub search, query \"Large_scale_QSVM in:name\" (2026-10-06, 1 result); the paper cites "
         "github.com/shelky/Large scale QSVM.git, whose owner no longer exists (HTTP 404); the repository found "
         "has that exact name and belongs to A. Miroszewski, a co-author of the paper")],
    "Carles-et-al._2025": [
        ("doi:10.5281/zenodo.15745370", "dataset-of",
         "the note's Zenodo record, entered by its DOI; DataCite resource type Dataset (the paper says data and code)")],
    "Jamadagni-Lauchli-Hempel_2024": [
        ("doi:10.5281/zenodo.10376217", "code-of",
         "the note's Zenodo record, entered by its DOI; DataCite resource type Workflow")],
    "Jin-et-al._2023": [
        ("doi:10.5281/zenodo.10895710", "code-of",
         "the note's Zenodo record, entered by its DOI; DataCite resource type Software (VQE_Tetris artifact)")],
    "Shaydulin-et-al._2023": [
        ("doi:10.5281/zenodo.10935810", "code-of",
         "the note's Zenodo record (cut short in the note at 10.5281), entered by its full DOI as the paper "
         "prints it; DataCite resource type Software")],
}

UNRESOLVED = {
    "Acosta-et-al._2024": "eacostam/adiabaticVQA (the paper prints it so): HTTP 404; the owner has 2 public "
                          "repositories, neither matching; search \"adiabaticVQA in:name\": 0 results",
    "Chen_2023": "MarkCodering/Deep-ReinforcementLearning-using-quDNN (the paper prints it so): HTTP 404; none of the "
                 "owner's 143 repositories matches; search \"Deep-ReinforcementLearning-using-quDNN in:name\": 0; "
                 "\"quDNN in:name\": 1 unrelated (meti2912/qudnn, created 2026-09-25, no tie to the paper)",
    "Park-et-al._2025": "JHPark9090/MultiChip-QML (the paper prints it so): HTTP 404; none of the owner's 60 "
                        "repositories matches; search \"MultiChip-QML in:name\": 0 results",
    "Pan-et-al.-2022": "luzd19/Deep-quantum-neural-networks_equipped-with-backpropagation (the paper prints it so): "
                       "the owner no longer exists (HTTP 404); search for the full name: 0; "
                       "\"Deep-quantum-neural-networks in:name\": 4 results, none by these authors",
    "Bettaque-Swingle_2023": "vbettaque/qstab (the paper prints it so, Python 3.10.4): HTTP 404; the owner's "
                             "QStab.jl is Julia, so not the code the paper describes; not linked",
    "MindSpore-Quantum-Developers_2022": "gitee.com/mindspore/mindquantum: the door has no Gitee route",
    "Asfaw-et-al._2021": "the PDF filed as Asfaw et al. 2108.0131 is a different paper: its first page reads "
                         "arXiv:2108.00131v2 (Radhakrishnan, Stefanakis, Belkin, Uhler; infinite-width networks for "
                         "matrix completion), whose code the note names (uhlerlab/ntk_matrix_). Entering it needs an "
                         "arXiv request, so it waits for a pause in Task C's capped run",
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist", file=sys.stderr)
        return 1
    today = date.today().isoformat()
    notes = {p.name: p for p in linker.REPOS.glob("*_repo.md")}
    if apply:
        backup_before_write(DB_PATH, "F54 recover repository notes")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")  # Task C's probe run writes meanwhile
    counts = {"linked": 0, "new records": 0, "already linked": 0, "failed": 0}
    try:
        for prefix, targets in RESOLVED.items():
            names = [n for n in notes if n.startswith(prefix)]
            if len(names) != 1:
                print(f"FAILED {prefix}: {len(names)} note files match")
                counts["failed"] += 1
                continue
            text = notes[names[0]].read_text(encoding="utf-8")
            arxiv = linker._ARXIV.search(text).group(1)
            quote_m = linker._QUOTE.search(text)
            quote = " ".join(line.lstrip("> ").strip() for line in quote_m.group(1).splitlines()).strip()
            cited = linker._REPO.search(text).group(1)
            paper = linker.paper_for(conn, arxiv)
            if paper is None:
                print(f"FAILED {prefix}: paper arXiv:{arxiv} is not in the store")
                counts["failed"] += 1
                continue
            route = f"QMLPapers/Repos/{names[0]}"
            for access, link_type, how in targets:
                is_github = access.startswith("https://github.com/")
                existing = linker.repo_record(conn, access.split("github.com/")[1]) if is_github else None
                if existing is None and not is_github:
                    row = conn.execute("SELECT record_id FROM paper_fields WHERE lower(access) = lower(?)",
                                       (access,)).fetchone()
                    existing = row[0] if row else None
                if existing is None:
                    try:
                        record = intake.build_record({
                            "access": access, "kind": "repo", "context": "qml",
                            "disposition": f"Code repository: released with {paper} (arXiv:{arxiv}), per the "
                                           "paper's own sentence; not yet screened",
                            "found_via": route, "cited_as": cited}, today=today)
                    except (ValueError, LookupError, OSError) as ex:
                        print(f"FAILED {prefix}: {access} did not resolve ({str(ex)[:160]})")
                        counts["failed"] += 1
                        continue
                    existing = record.id
                    if conn.execute("SELECT 1 FROM records WHERE id = ?", (existing,)).fetchone() is None:
                        if apply:
                            insert_paper(conn, record)
                        counts["new records"] += 1
                elif apply and not conn.execute("SELECT 1 FROM paper_found_via WHERE record_id = ? AND route = ?",
                                                (existing, route)).fetchone():
                    add_found_via(conn, existing, route, cited)
                if conn.execute("SELECT 1 FROM source_links WHERE from_id = ? AND to_id = ? AND link_type = ?",
                                (existing, paper, link_type)).fetchone():
                    counts["already linked"] += 1
                    continue
                evidence = f"{quote} [How found (Sprint 7 F54): {how}.]"
                if apply:
                    add_source_link(conn, existing, paper, link_type, evidence)
                    conn.commit()
                counts["linked"] += 1
                print(f"{'LINK' if apply else 'PLAN'} {existing} {link_type} {paper}")
        for prefix, why in UNRESOLVED.items():
            print(f"REPORT {prefix}: {why}")
        print(f"\n{counts}; reported again {len(UNRESOLVED)}")
        print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
        return 1 if counts["failed"] else 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
