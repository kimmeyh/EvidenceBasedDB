# Sprint 4 Task E: F11 Adjudication Packet for the Team Lead

Generated 2026-09-19 by `scripts/render_f11_packet.py` from the store as corrected by
Sprint 4 Task C. **Generated, never hand-edited**; re-run the script after any record change.

## What this measures, and how to run it

ADR-0004 names one number the whole design is constrained by: **minutes of
team-lead adjudication per accepted record**. Sprint 3's F7-F10 measured four
model reviewers on these same 18 records (F10, the primary-source protocol:
599 s and 150,290 tokens for the set, 93 field calls). F11 measures the team
lead on the same records, corrected, with the same primary-source access.

**Protocol (the F10 protocol; record per record whether you followed it in full):**

1. Start the clock. Open the source via the link in *Access* (arXiv/DOI page or the local PDF).
2. Citation: ACCEPT / REVISE / REJECT the authors, title, venue or arXiv version, DOI, date against the source.
3. Disposition: is it one line, true, and why the record was worth keeping?
4. Each applicability row: is the context right, and does the rationale say where it was read from?
5. Tier: does `screened` (dispositioned and applicability-derived, not yet mined; ADR-0005 A2) hold?
6. Stop the clock. Fill the row in the timing sheet: minutes, protocol followed (full / partial: which steps), calls.

F10's findings are printed under each record so the run measures adjudication,
not re-discovery. Items marked *Task F's* are applicability corrections still
pending in this sprint; adjudicate them as you find them and say so.

When done, hand the timing sheet back (edited in place or pasted). Claude records
the minutes-per-record number and the protocol in `.claude/model_assignment_heuristics.json`
(`learning_log`, the pending Sprint 4 row) and in the Sprint 4 summary.

## The 18 records F10 reviewed (snapshot as of 2026-09-19; tier shown per record)

Screened records added since F10 ran, **not part of the timed comparison** (adjudicate
them afterwards if you wish; they went through the Task B door, so they are also a
test of the door): `notton-2026-merlin-discovery-engine-photonic-hybrid`.

### 1. `arute-2019-quantum-supremacy-google-nature`

- **Title**: Quantum supremacy using a programmable superconducting processor
- **Citation**: Arute, F., Arya, K., Babbush, R., Bacon, D., Bardin, J.C., Barends, R., Biswas, R., Boixo, S., Brandao, F.G.S.L., Buell, D.A., et al., "Quantum supremacy using a programmable superconducting processor," Nature, 574(7779), 505-510, DOI:10.1038/s41586-019-1666-5, 2019-10-24
- **Access**: https://doi.org/10.1038/s41586-019-1666-5
- **Tier**: screened; **primary context**: qc
- **Disposition**: Peer-reviewed Nature paper reporting Google's quantum supremacy claim on the 53-qubit Sycamore processor; a high-value qc reference
- **Applicability**:
  - `qc`: Programmable superconducting Sycamore processor, 53 qubits; one instance of a random quantum circuit sampled a million times in about 200 seconds against an estimated 10,000 years for a classical supercomputer -- PDF p.1 abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from doi:10.1038/s41586-019-1666-5 via Crossref/DataCite (scripts/refresh_citations.py); previous citation: Arute, F., Arya, K., Babbush, R., et al. (Google AI Quantum et al.), "Quantum supremacy using a programmable superconducting processor," Nature 574:505-510, DOI | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc', 'world'] -> ['qc']; world dropped: an engineering demonstration of a device is a contested empirical claim, not mathematics/physics ground truth (context test, INTAKE_WORKFLOW.md section 8; F9 and F10 both flagged it); disposition rewritten | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider Crossref/DataCite (named in the record's history)
- **F10 found**: 'world' claimed on a contested empirical claim under a 'platform-independent' test that ADR-0004's own definition (mathematics/physics ground truth) does not support; disposition carried 'LANDMARK' and 'near-certain read-tier candidate' (tier words removed in Task C) -- context is Task F's.

### 2. `britt-humble-2017-hpc-with-qpus-acm`

- **Title**: High-Performance Computing with Quantum Processing Units
- **Citation**: Britt, K.A., Humble, T.S., "High-Performance Computing with Quantum Processing Units," ACM Journal on Emerging Technologies in Computing Systems, 13(3), 1-13, DOI:10.1145/3007651, 2017-07-31
- **Access**: https://doi.org/10.1145/3007651
- **Tier**: screened; **primary context**: qc
- **Disposition**: Peer-reviewed ACM paper on integrating QPUs into HPC architectures
- **Applicability**:
  - `method`: Proposes new metrics capturing the interplay between system architecture and the quantum parallelism underlying computational performance -- Crossref abstract
  - `qc`: Integration of quantum processing units into current and future HPC system architectures; two integration pathways differentiated by infrastructure constraints on the QPU and the use cases expected of the HPC system -- Crossref abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from doi:10.1145/3007651 via Crossref/DataCite (scripts/refresh_citations.py); previous citation: Britt, K.A., Humble, T.S., "High-Performance Computing with Quantum Processing Units," ACM J. Emerg. Technol. Comput. Syst. 13(3), Art. 39, DOI:10.1145/3007651, | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc'] -> ['method', 'qc']; method added for the architecture metrics; the qc rationale now states the two integration pathways (F9's tight/loose taxonomy point) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider Crossref/DataCite (named in the record's history)
- **F10 found**: Vendor-neutral HPC architecture paper that did NOT get 'world' while arute and rand did (F9's inconsistency); 'method' worth considering; 'tight/loose taxonomy' rationale incomplete -- Task F's.

### 3. `dupont-2023-quantum-enhanced-greedy-solver`

- **Title**: Quantum-Enhanced Greedy Combinatorial Optimization Solver
- **Citation**: Dupont, M., Evert, B., Hodson, M.J., Sundar, B., Jeffrey, S., Yamaguchi, Y., Feng, D., Maciejewski, F.B., Hadfield, S., Alam, M.S., et al., "Quantum-Enhanced Greedy Combinatorial Optimization Solver," arXiv:2303.05509v2, Science Advances 9, 45 (2023), DOI:10.1126/sciadv.adi0487, 2023-11-17
- **Access**: https://arxiv.org/abs/2303.05509
- **Tier**: screened; **primary context**: qc
- **Disposition**: Quantum-classical hybrid optimization on up to 72 superconducting qubits benchmarked against classical greedy; relevant to the optimization/qc intersection
- **Applicability**:
  - `qc`: Iterative quantum heuristic optimization on a programmable superconducting quantum system with up to 72 qubits, on Sherrington-Kirkpatrick spin-glass instances, systematically outperforming its classical greedy counterpart -- arXiv abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2303.05509 via arXiv (scripts/refresh_citations.py); previous citation: Dupont, M., Evert, B., Hodson, M.J., Sundar, B., Jeffrey, S., Yamaguchi, Y., Feng, D., Maciejewski, F.B., Hadfield, S., Alam, M.S., Wang, Z., Grabbe, S., Lott,  | 2026-09-19 (Sprint 4 Task C, F25 B1): F10 (Sprint 3) found the hand-typed title wrong ('Quantum Enhanced Greedy Solver for Optimization Problems'); the citation is now the arXiv record's, including the journal reference/DOI the record carries | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts unchanged, every rationale re-anchored to where it was read; qml not added: a spin-glass instance is not an ML model (qml-via-workload rule); disposition rewritten | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider arXiv (named in the record's history)
- **F10 found**: Title was wrong ('Quantum Enhanced Greedy Solver for Optimization Problems'); pinned v1 though v2 exists and the paper was published in Science Advances. Corrected by API re-derivation in Task C.

### 4. `emami-2025-financial-fraud-entropy-computing-qci`

- **Title**: Financial Fraud Detection with Entropy Computing
- **Citation**: Emami, B., Dyk, W., Haycraft, D., Spear, C., Nguyen, L., Chancellor, N., "Financial Fraud Detection with Entropy Computing," arXiv:2503.11273v1, 2025-03-14
- **Access**: https://arxiv.org/abs/2503.11273
- **Tier**: read; **primary context**: platform:dirac-3
- **Disposition**: QCi's own CVQBoost/Dirac-3 fraud-detection paper, benchmarked against XGBoost; among the most load-bearing papers for the HSBC consumer project and already cited in ADR-0004's motivating case
- **Applicability**:
  - `ml`: Benchmarked against XGBoost evaluated on up to 48 CPUs and four NVIDIA L4 GPUs with the RAPIDS AI framework -- arXiv abstract
  - `platform:dirac-3`: CVQBoost leverages early hardware implementing Quantum Computing Inc's (QCi) Entropy Quantum Computing paradigm, Dirac-3; all six authors carry the QCi affiliation on the arXiv listing -- arXiv abstract and affiliation block
  - `qml`: CVQBoost, a hybrid quantum-classical boosting classifier, applied to a fraud-detection test case -- arXiv abstract
- **Evidence**: Vendor benchmark of CVQBoost on Dirac-3 against XGBoost on the Kaggle credit-card fraud dataset (38 features) and synthetic sets to 70M rows; averages over 10 runs with two-standard-deviation bars; four balancing strategies applied to training data only; XGBoost run on up to 48 CPUs and four NVIDIA L4 GPUs. Independence: 'All authors were completely supported by Quantum Computing Inc. in writing this paper' (p.12); the byline lists QCi for all six, and Chancellor's concurrent Durham University affiliation is not on it (F10 note, Sprint 3), so the six-QCi-authors reading is correct on the byline and thinner than it looks. Code: github.com/qci-github/eqc-studies/tree/main/CVQBoost. Its Table 1 (p.14) is the same AUC table as qci-2024-profiling's Table 3 (p.11), so the two records are one dataset, not two independent measurements.
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2503.11273 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Emami, B., Dyk, W., Haycraft, D., Spear, C., Nguyen, L., Chancellor, N. (Quantum Computing Inc.), "Financial Fraud Detection with Entropy Computing," arXiv:2503 | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['platform:dirac-3', 'qml'] -> ['ml', 'platform:dirac-3', 'qml']; ml added: XGBoost head-to-head; disposition rewritten | 2026-09-19 (Sprint 4 Task H, F25 D6): promoted to read after a direct read; assertions extracted; see paper_yields | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history); read_extent transcribed from checked_against_source (1 row(s))
- **F10 found**: Preprint superseded by a Springer proceedings chapter the record did not mention; 'all six authors are QCi employees' is correct on the byline but Chancellor holds a concurrent Durham affiliation. Task H's extraction records the latter as evidence.

### 5. `huynh-2023-quantum-inspired-ml-survey`

- **Title**: Quantum-Inspired Machine Learning: a Survey
- **Citation**: Huynh, L., Hong, J., Mian, A., Suzuki, H., Wu, Y., Camtepe, S., "Quantum-Inspired Machine Learning: a Survey," arXiv:2308.11269v2, 2023-09-08
- **Access**: https://arxiv.org/abs/2308.11269
- **Tier**: screened; **primary context**: qml
- **Disposition**: Real survey paper specifically on Quantum-Inspired ML (QiML), a subfield distinct from QML proper; relevant for establishing the qml/QiML vocabulary boundary this library needs
- **Applicability**:
  - `method`: Establishes a concrete definition of QiML by analyzing prior interpretations of the term and their ambiguities, the vocabulary boundary this library uses -- arXiv abstract
  - `ml`: QiML leverages principles of quantum mechanics within classical computational frameworks (tensor network simulations, dequantized algorithms): classical ML content by its own definition -- arXiv abstract
  - `qml`: Survey of Quantum-inspired Machine Learning (QiML), positioned against the broader QML field whose review literature it says treats QiML superficially -- arXiv abstract
- **Last change** (2026-10-04): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2308.11269 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Huynh, L., Hong, J., Mian, A., Suzuki, H., Wu, Y., Camtepe, S., "Quantum-Inspired Machine Learning: a Survey," arXiv:2308.11269v2, 2023-09-08 | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qml'] -> ['method', 'ml', 'qml']; ml added: QiML runs in classical frameworks by the paper's own definition; method added for the vocabulary it defines (F9, F10: ml had zero users across the store) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history) | 2026-10-04 (Sprint 6 Task J): also found via QMLPapers/2023/manifest.tsv | 2026-10-04 (Sprint 6 Task J): also found via QMLPapers/Reviews/manifest.tsv
- **F10 found**: Says its subject is 'distinct from QML proper' twice and files under qml alone while 'ml' has zero users across all 46 papers -- Task F's.

### 6. `kordzanganeh-2022-benchmarking-simulated-physical-qpu`

- **Title**: Benchmarking simulated and physical quantum processing units using quantum and hybrid algorithms
- **Citation**: Kordzanganeh, M., Buchberger, M., Kyriacou, B., Povolotskii, M., Fischer, W., Kurkin, A., Somogyi, W., Sagingalieva, A., Pflitsch, M., Melnikov, A., "Benchmarking simulated and physical quantum processing units using quantum and hybrid algorithms," arXiv:2211.15631v2, DOI:10.1002/qute.202300043, 2023-06-15
- **Access**: https://arxiv.org/abs/2211.15631
- **Tier**: screened; **primary context**: qc
- **Disposition**: Real benchmarking paper comparing simulators and physical QPUs across four vendors; relevant for the cross-platform benchmarking angle
- **Applicability**:
  - `method`: A cross-platform benchmarking methodology for simulated versus physical quantum processing units -- arXiv abstract
  - `platform:braket`: The AWS SV1 simulator is one of the benchmarked back ends -- arXiv abstract
  - `qc`: Benchmarks runtime and accuracy across simulated and physical QPUs: the QMware and AWS SV1 simulators, Rigetti's Aspen-M2 and IonQ's Harmony -- arXiv abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2211.15631 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Kordzanganeh, M., Buchberger, M., Povolotskii, M., Fischer, W., Kurkin, A., Somogyi, W., Sagingalieva, A., Pflitsch, M., Melnikov, A. (Terra Quantum AG / QMware | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task C, F25 B1): the note formerly inside the citation moves here: the seed filename truncates the arXiv id to 2211.1563; the PDF's own arXiv banner reads 2211.15631. F10 found the third author (Basil Kyriacou) missing from the hand-typed list; the API-derived list is complete. Disposition no longer says 'seen tier' beside a tier column that says screened | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc', 'qml'] -> ['method', 'platform:braket', 'qc']; qml dropped: the abstract names no QNN workload and F10 asked for evidence or drop; restore at read tier if the body shows one. method and platform:braket added from the abstract (benchmarking methodology; AWS SV1 back end) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history)
- **F10 found**: Third author (Basil Kyriacou) missing; pinned v1; published in Advanced Quantum Technologies; disposition said 'seen tier' beside a tier column saying screened; 'workload is QNNs' rationale stated without evidence. Citation and disposition corrected in Task C; the rationale is Task F's.

### 7. `loke-2026-cvqboosting-fraud-detection-smu`

- **Title**: Improving credit card transaction fraud detection using CVQBoosting
- **Citation**: Loke, B.H.T., Sahoo, N., Guan, B., Xu, M., Verma, D., Griffin, P.R. (Singapore Management University), "Improving credit card transaction fraud detection using CVQBoosting," SMU Institutional Knowledge, Research Collection School of Computing and Information Systems, conference proceeding article, 2026-03 (hand-transcribed from p.1 cover sheet and p.2 author byline)
- **Access**: D:\Data\Harold\EvidenceBasedDB\Papers\Improving credit card transaction fraud detection using CVQBoosting - QCi Dirac-3 202603 Paul Griffin.pdf | https://ink.library.smu.edu.sg/sis_research
- **Tier**: read; **primary context**: platform:dirac-3
- **Disposition**: Same CVQBoost/Dirac-3 fraud-detection subject as the HSBC consumer project, and the same Loke et al. group ADR-0005 cites for the 0.8108 AUPRC figure; all six authors SMU or NTU affiliated per the byline, none QCi, so F5's affiliation check must read the paper rather than assume from the topic
- **Applicability**:
  - `ml`: Weak classifiers K-nearest neighbours, linear discriminant analysis, logistic regression and XGBoost; mean AUC-PR over 0.8, about 9% over the best published classical baseline -- PDF p.3 abstract
  - `platform:dirac-3`: Keywords name 'Photonic Quantum Processor, Dirac-3'; CVQBoost executed on QCi's photonic Dirac-3 processor -- PDF p.3 keywords and abstract
  - `qml`: Keywords name 'Quantum Machine Learning (QML), CVQBoost, Quantum Boosting'; a hybrid quantum-classical boosting ensemble -- PDF p.3 keywords and abstract
- **Evidence**: Empirical study on the MLG-ULB Kaggle credit-card fraud dataset (70/30 split, SMOTE on the training fold only, test fold untouched), N = 10 runs with different seeds; CVQBoost on Dirac-3 with a heterogeneous weak-classifier pool (KNN, LDA, logistic regression, shallow XGBoost); the classical comparator (CAD, Gao et al. 2025) is a published figure, not a model re-run in the same lineup. Funded by OCBC with in-kind support from QCi (p.8). The authors' own limitations (p.7): benchmark datasets may not capture real banking transactions; KNN weak classifiers cost about 378 s each; remote solver overhead and third-party hardware access are bottlenecks.
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19 (Sprint 4 Task C, F25 B1): access was the bare words 'local file'; now the seed file's path plus the SMU collection URL printed on p.1 (the item's own handle is not printed on the cover sheet; no DOI or arXiv id exists, so the citation is hand-transcribed). The correction narrative formerly embedded in the citation moves here: on 2026-09-16 the author list was corrected to the six named on p.2's 'Author' byline (Loke, Sahoo, Guan, Xu, Verma, Griffin); the Sprint 1 pass had read only p.1's 'See next page for additional authors', recorded 'et al.', and missed Griffin although the seed filename named him. Re-read from the PDF 2026-09-19 | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['platform:dirac-3', 'qml'] -> ['ml', 'platform:dirac-3', 'qml']; ml added: named classical weak classifiers and baseline; disposition rewritten | 2026-09-19 (Sprint 4 Task H, F25 D6): promoted to read after a direct read; assertions extracted; see paper_yields | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); read_extent transcribed from checked_against_source (1 row(s))
- **F10 found**: A 700-character correction narrative lived inside the citation (moved to updated_reason); access was the bare words 'local file' (now the real path plus the SMU collection URL). Rationales already named their anchors (p.1 keywords) -- the model Task F applies elsewhere.

### 8. `lubinski-2023-application-oriented-benchmarks-qedc`

- **Title**: Application-Oriented Performance Benchmarks for Quantum Computing
- **Citation**: Lubinski, T., Johri, S., Varosy, P., Coleman, J., Zhao, L., Necaise, J., Baldwin, C.H., Mayer, K., Proctor, T., "Application-Oriented Performance Benchmarks for Quantum Computing," arXiv:2110.03137v3, DOI:10.1109/tqe.2023.3253761, 2023-01-10
- **Access**: https://arxiv.org/abs/2110.03137
- **Tier**: screened; **primary context**: qc
- **Disposition**: Real QED-C benchmarking-suite paper across multiple platforms. Directly useful methodology reference for how this project should think about cross-platform benchmarking
- **Applicability**:
  - `method`: A benchmarking methodology this library can apply to cross-platform claims -- arXiv abstract
  - `qc`: Open-source suite of application-oriented benchmarks measuring quantum hardware effectiveness as circuit width and depth vary, in the volumetric-benchmarking framework -- arXiv abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2110.03137 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Lubinski, T., Johri, S., Varosy, P., Coleman, J., Zhao, L., Necaise, J., Baldwin, C.H., Mayer, K., Proctor, T. (QED-C), "Application-Oriented Performance Benchm | 2026-09-19 (Sprint 4 Task C, F25 B1): the note formerly inside the citation moves here: two seed files carry this paper ('Application-Oriented...' and 'Benchmarking - Application-Oriented...'); sha256 b05b558d23567fc6... is identical for both (checked 2026-09-19); recorded once | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts unchanged, every rationale re-anchored to where it was read; qc rationale no longer lists vendors the abstract does not name (F10: the old list omitted D-Wave on the author list) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history)
- **F10 found**: Preprint superseded by IEEE TQE (DOI 10.1109/TQE.2023.3253761); v3 date is 2023-01-10 not -11; duplicate-file note lived inside the citation (moved; the two files are byte-identical). Rationale 'gate-based hardware: IonQ, Quantinuum' omits that D-Wave is on the author list -- Task F's.

### 9. `mancilla-2026-fourier-wall-spectra`

- **Title**: The Fourier Wall: Why Public Tabular Datasets Refuse Quantum Advantage, and a Certified Recipe for Where It Lives
- **Citation**: Mancilla, J., Tagliani, T., "The Fourier Wall: Why Public Tabular Datasets Refuse Quantum Advantage, and a Certified Recipe for Where It Lives," arXiv:2607.15815v1, 2026-07-17
- **Access**: https://arxiv.org/abs/2607.15815
- **Tier**: read; **primary context**: qml
- **Disposition**: Introduces the SPECTRA certificate for whether and when QML has genuine advantage on tabular data, a central question for this project
- **Applicability**:
  - `method`: SPECTRA, a two-tier certificate: a simulator-free structural screen, then a matched quantum model against five tuned classical twins with paired-bootstrap confidence bounds -- arXiv abstract
  - `ml`: Gradient-boosted trees reach a held-out ROC-AUC of 0.999 on the real smart-meter target SPECTRA refuses -- arXiv abstract
  - `qml`: Conditions under which an angle-encoded quantum neural network (a partial Fourier series) can beat classical baselines on tabular data -- arXiv abstract
- **Evidence**: Methods paper (preprint v1) introducing the SPECTRA certificate; one industrial smart-meter dataset with a real peak-load target (refused) and a semi-synthetic positive control (real covariates, label generated by a quantum process; the authors label it as such, p.12); the classical bar includes an order-matched twin and the exact simulator of the process family, which ties the accuracy (p.12); simulations at 14 qubits or fewer, no hardware run (p.12, 'Bounded, not provable'). Two authors, one company (Falcondale LLC). F10 notes filed here so they are not lost: (i) rehman-2026's confidence-thresholded quantum fallback and this paper's 'deploy as a routed specialist, never as a replacement' (p.12) are the same deployment pattern, a candidate `supports` once rehman yields; (ii) tung-2026's circuit recommendation 'without quantum evaluation at inference time' and SPECTRA's simulator-free tier-1 screen are both cheap pre-screens for whether quantum is worth attempting, a theme the library should be able to query.
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2607.15815 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Mancilla, J., Tagliani, T. (Falcondale LLC), "The Fourier Wall: Why Public Tabular Datasets Refuse Quantum Advantage, and a Certified Recipe for Where It Lives, | 2026-09-19 (Sprint 4 Task C, F25 B1): the note formerly inside the citation claimed two 'identically-content' seed files; their sha256 differ (5784f63ea04ae701... vs 4967accbbc78ca9b..., 2,224,604 vs 2,216,899 bytes; checked 2026-09-19), so they are two different files of arXiv:2607.15815 and the claim was false (F10). Recorded once; the arXiv record is the source of truth | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qml'] -> ['method', 'ml', 'qml']; method added (SPECTRA is a certificate methodology) and ml added (gradient-boosted trees on the public tabular target) (F9); disposition rewritten | 2026-09-19 (Sprint 4 Task H, F25 D6): promoted to read after a direct read; assertions extracted; see paper_yields | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history); read_extent transcribed from checked_against_source (1 row(s)) | 2026-10-03 (Sprint 6 Task G): checked_against_source extended to the full 16-page read of 2026-09-22
- **F10 found**: Claimed two seed files were 'identically-content'; hashing showed they differ. Note moved to updated_reason with the sha256 measurement in Task C.

### 10. `mandra-2021-hybridq-simulator-nasa`

- **Title**: HybridQ: A Hybrid Simulator for Quantum Circuits
- **Citation**: Mandrà, S., Marshall, J., Rieffel, E.G., Biswas, R., "HybridQ: A Hybrid Simulator for Quantum Circuits," arXiv:2111.06868v1, DOI:10.1109/qcs54837.2021.00015, 2021-11-12
- **Access**: https://arxiv.org/abs/2111.06868
- **Tier**: screened; **primary context**: qc
- **Disposition**: Real paper introducing a hybrid quantum-circuit simulation framework; a useful method-context reference for simulation technique
- **Applicability**:
  - `method`: A common framework integrating multiple state-of-the-art simulation techniques; a tool for evaluating circuits without hardware -- arXiv abstract
  - `qc`: HybridQ, an extensible hybrid simulator for quantum circuits on CPUs and GPUs with HPC workload balancing across nodes -- arXiv abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2111.06868 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Mandrà, S., Marshall, J., Rieffel, E.G., Biswas, R. (NASA QuAIL), "HybridQ: A Hybrid Simulator for Quantum Circuits," arXiv:2111.06868, 2021-11-12 | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts unchanged, every rationale re-anchored to where it was read | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history)
- **F10 found**: Preprint superseded by IEEE/ACM QCS 2021 (DOI 10.1109/QCS54837.2021.00015), now carried by the API-derived citation.

### 11. `neven-2012-qboost-adiabatic-quantum-optimization`

- **Title**: QBoost: Large Scale Classifier Training with Adiabatic Quantum Optimization
- **Citation**: Neven, H. (Google Inc.), Denchev, V.S. (Purdue University), Rose, G., Macready, W.G. (D-Wave Systems Inc.), "QBoost: Large Scale Classifier Training with Adiabatic Quantum Optimization," JMLR: Workshop and Conference Proceedings 25:333-348, Asian Conference on Machine Learning (ACML), 2012 (hand-transcribed from title page)
- **Access**: D:\Data\Harold\EvidenceBasedDB\Papers\QBoost - Large Scale Classifier Training with Adiabatic Quantum Optimization - Neven Denchev Rose Macready - ACML PMLR v25 2012.pdf | https://proceedings.mlr.press/v25/neven12/
- **Tier**: screened; **primary context**: qml
- **Disposition**: SEMINAL: introduces QBoost, the adiabatic-quantum-optimization boosting algorithm that CVQBoost (the algorithm the HSBC consumer work measures on Dirac-3) directly descends from; directly relevant, high priority
- **Applicability**:
  - `ml`: A boosting framework for large-scale binary classifiers; keywords 'machine learning, supervised learning, boosting' -- PDF p.1 keywords
  - `qc`: Training cast into the format required by existing adiabatic quantum hardware (D-Wave), for which no platform context exists -- PDF p.1 abstract
  - `qml`: QBoost: weak-classifier selection for boosting cast as the discrete optimization adiabatic quantum hardware solves; the algorithm CVQBoost descends from -- PDF p.1 abstract and keywords
- **Last change** (2026-10-03): 2026-09-19 (Sprint 4 Task C, F25 B1): access now follows the '<path> | <url>' form (seed file plus the PMLR page; PMLR pages carry no DOI, so hand-transcribed). The addition history formerly in the disposition moves here: added 2026-09-17 (Sprint 2 Task C spot-check) after the seed directory changed since Sprint 1's snapshot; the team lead confirmed the addition was intentional (F5's scope names QBoost) | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc', 'qml'] -> ['ml', 'qc', 'qml']; ml added for the boosting formulation; qc kept because no platform context exists for D-Wave (qc-subsumption rule) | 2026-09-19 (Sprint 4 Task H, F25 D6): lineage confirmed -- emami-2025's reference list (p.13) cites this exact paper (ACML 2012, PMLR volume 25, proceedings.mlr.press/v25/neven12.html) as QBoost's source; qci-2024-profiling cites 'Neven et al. (2009)' in text (p.2) with no reference list in its 11 pages, presumably the arXiv precursor of the same line, not verified | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 2 Task C spot-check (seed directory)' (from "added 2026-09-17 (Sprint 2 Task C spot-check)")
- **F10 found**: Keeps a generic 'qc' beside its specific context while Dirac-3 papers drop it (the unstated qc-subsumption rule); 'ml' for the boosting formulation -- Task F's. Also: QCi cites 'Neven et al. 2009' while the store holds the 2012 paper; Task H confirms which one CVQBoost's lineage rests on.

### 12. `pelofske-2022-quantum-volume-nisq-ieee`

- **Title**: Quantum Volume in Practice: What Users Can Expect From NISQ Devices
- **Citation**: Pelofske, E., Bärtschi, A., Eidenbenz, S., "Quantum Volume in Practice: What Users Can Expect From NISQ Devices," IEEE Transactions on Quantum Engineering, 3, 1-19, DOI:10.1109/tqe.2022.3184764, 2022
- **Access**: https://doi.org/10.1109/TQE.2022.3184764
- **Tier**: screened; **primary context**: qc
- **Disposition**: Peer-reviewed IEEE benchmarking paper measuring quantum volume on 24 NISQ devices across five vendors
- **Applicability**:
  - `method`: Quantum volume as the de-facto NISQ benchmark, reproduced independently rather than taken from provider reports -- PDF p.1 abstract
  - `qc`: Quantum volume measured on 24 NISQ devices from IBM Q, IonQ, Rigetti, Oxford Quantum Circuits and Quantinuum; achieved values lag officially reported ones and depend on compilation effort -- PDF p.1 abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from doi:10.1109/TQE.2022.3184764 via Crossref/DataCite (scripts/refresh_citations.py); previous citation: Pelofske, E., Bärtschi, A., Eidenbenz, S., "Quantum Volume in Practice: What Users Can Expect From NISQ Devices," IEEE Trans. Quantum Eng., DOI:10.1109/TQE.2022 | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc'] -> ['method', 'qc']; disposition rewritten | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider Crossref/DataCite (named in the record's history)
- **F10 found**: Complete on DOI but omitted volume/pages and the LANL affiliation; API-derived citation now carries IEEE TQE volume 3, pages 1-19.

### 13. `qci-2024-profiling-cvqboost`

- **Title**: Profiling of CVQBoost Algorithm: Fraud Detection
- **Citation**: Quantum Computing Inc., "Profiling of CVQBoost Algorithm: Fraud Detection," vendor white paper, no named authors, no venue, no DOI, December 2024 (hand-transcribed from cover)
- **Access**: D:\Data\Harold\EvidenceBasedDB\Papers\QCi - Profiling of CVQBoost.pdf
- **Tier**: read; **primary context**: platform:dirac-3
- **Disposition**: QCi's own internal profiling document on CVQBoost for fraud detection; vendor-authored, no named authors, no venue, no DOI; directly relevant for performance/timing claims about the algorithm the HSBC project uses
- **Applicability**:
  - `ml`: XGBoost as the classical comparator: higher accuracy when balancing is minimal, CVQBoost catching up under ADASYN/SMOTE balancing, and superior runtime as data and feature counts grow -- PDF p.2 abstract
  - `platform:dirac-3`: CVQBoost on QCi's Dirac-3, benchmarked against XGBoost on the imbalanced Kaggle credit-card fraud dataset across dataset sizes, feature counts and class-imbalance ratios -- PDF p.2 abstract
  - `qml`: CVQBoost, an extension of the QBoost algorithm leveraging quadratic optimization solvers -- PDF p.2 abstract
- **Evidence**: Vendor profiling report (no named authors, no venue, no DOI) whose Table 3 (p.11) carries the same 24 AUC rows as emami-2025's Table 1; the arXiv paper is the write-up of this report. Same dataset and same controls as emami-2025; not an independent measurement. Cites 'Neven et al. (2009)' in text (p.2) with no reference list.
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19 (Sprint 4 Task C, F25 B1): access was the bare words 'local file'; now the seed file's path. The citation now states explicitly (F10) that the document names no authors, venue or DOI -- read from the cover 2026-09-19 -- instead of being shaped like a peer-reviewed citation | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['platform:dirac-3', 'qml'] -> ['ml', 'platform:dirac-3', 'qml']; ml added and the rationale carries the abstract's specific, hedged results (F9, F10: the weakest rationale in the CVQBoost cluster) | 2026-09-19 (Sprint 4 Task H, F25 D6): promoted to read after a direct read; assertions extracted; see paper_yields | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); read_extent transcribed from checked_against_source (1 row(s))
- **F10 found**: Formatted like a peer-reviewed citation while having no authors, venue or DOI, and did not say so; access was the bare words 'local file'. Citation now states the absence explicitly; access is the real path. Its 'covers performance' rationale was the weakest of the CVQBoost cluster (F9 and F10 independently) -- Task F's.

### 14. `rand-2022-pqc-critical-infrastructure-assessment`

- **Title**: Preparing for Post-Quantum Critical Infrastructure: Assessments of Quantum Computing Vulnerabilities of National Critical Functions
- **Citation**: RAND Corporation, "Preparing for Post-Quantum Critical Infrastructure: Assessments of Quantum Computing Vulnerabilities of National Critical Functions," DOI:10.7249/rra1367-6, 2022
- **Access**: https://doi.org/10.7249/RRA1367-6
- **Tier**: screened; **primary context**: qc
- **Disposition**: Institutional RAND/DHS policy report on post-quantum-crypto transition risk to critical infrastructure. Treated as a paper-equivalent source per ADR-0005's broad framing of any mined source; genuinely relevant institutional research
- **Applicability**:
  - `qc`: Assesses quantum computing's cryptographic threat to the 55 national critical functions for CISA, the post-quantum transition -- PDF p.1 title page and p.iii About This Report
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19 (Sprint 4 Task C, F25 B1): id renamed from rand-2023-... (Q4): the report's p.ii says 'This research was published in 2022' and the hand-typed citation carried no year at all (F10). access was the bare words 'local file'; the report has a registered DOI (Crossref, resolves to www.rand.org/pubs/research_reports/RRA1367-6.html; p.iii prints www.rand.org/t/RRA1367-6), so the record is api-origin and the citation is re-derived from Crossref. Crossref's record names no contributors; the cover names Vermeer, Parker and Kochhar. Seed file: D:\Data\Harold\EvidenceBasedDB\Papers\Homland PQC Quantum Assessment RAND_RRA1367-6.pdf | 2026-09-19: citation and title re-derived from doi:10.7249/RRA1367-6 via Crossref/DataCite (scripts/refresh_citations.py); previous citation: Vermeer, M.J.D., Parker, E., Kochhar, A.K. (RAND / HSOAC), "Preparing for Post-Quantum Critical Infrastructure: Assessments of Quantum Computing Vulnerabilities | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc', 'world'] -> ['qc']; world dropped: a policy report is not mathematics/physics ground truth (F9, F10) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider Crossref/DataCite (named in the record's history)
- **F10 found**: Citation carried no year and the id said 2023; the report's p.ii says 2022. Access was the bare words 'local file'. Renamed rand-2022 and switched to the registered DOI 10.7249/RRA1367-6 in Task C (Crossref names no contributors; the cover names Vermeer, Parker, Kochhar). 'world' claimed on a policy report -- Task F's.

### 15. `rehman-2026-qstar-adaptive-routing`

- **Title**: QSTAR: Quantum Selective Transfer with Adaptive Routing
- **Citation**: Rehman, S., Innan, N., Shafique, M., "QSTAR: Quantum Selective Transfer with Adaptive Routing," arXiv:2607.21411v1, 2026-07-23
- **Access**: https://arxiv.org/abs/2607.21411
- **Tier**: screened; **primary context**: qml
- **Disposition**: Real paper on selective/adaptive routing between classical and quantum transfer-learning heads. Relevant to qml methodology, includes real benchmarked accuracy figures
- **Applicability**:
  - `ml`: Parameter-matched classical heads as baselines; the strongest fixed classical head stays highest at 81.6% accuracy -- arXiv abstract
  - `qml`: Quantum transfer-learning heads (manual and KetGPT-designed) on a frozen ResNet18; selective routing sends uncertain inputs to the quantum branch as a targeted fallback, not a uniform replacement -- arXiv abstract
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2607.21411 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Rehman, S., Innan, N., Shafique, M. (NYU Abu Dhabi), "QSTAR: Quantum Selective Transfer with Adaptive Routing," arXiv:2607.21411v1, 2026-07-23 | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qml'] -> ['ml', 'qml']; qml rationale now describes the asymmetric confidence-thresholded fallback the abstract describes (F10) | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history)
- **F10 found**: NYU Abu Dhabi affiliation asserted but not verifiable from the arXiv page (dropped from the API-derived citation); rationale describes an asymmetric confidence-thresholded fallback as symmetric routing -- Task F's.

### 16. `tung-2026-qmes-quantum-meta-learning-kernel-encoding`

- **Title**: Qmes: Quantum Meta-Learning for Encoding Selection in Quantum Kernel Methods
- **Citation**: Tung, D.D., Nguyen, Q.C., Hai, V.T., Ho, L.B., Tran, L.N., "Qmes: Quantum Meta-Learning for Encoding Selection in Quantum Kernel Methods," arXiv:2609.04652v1, 2026-09-04
- **Access**: https://arxiv.org/abs/2609.04652
- **Tier**: screened; **primary context**: qml
- **Disposition**: Real paper introducing an open-source meta-learning package for quantum kernel encoding selection. Directly relevant to qml methodology
- **Applicability**:
  - `method`: Qmes, an open-source package recommending circuits by meta-learning without quantum evaluation at inference, validated on 105 classification and 86 regression datasets -- arXiv abstract
  - `ml`: Datasets characterized with classical complexity measures and a pre-trained recommender model; meta-learning is classical ML -- arXiv abstract
  - `qml`: Encoding-circuit selection for quantum kernel methods -- arXiv abstract
- **Last change** (2026-10-04): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2609.04652 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Tung, D.D., Nguyen, Q.C., Hai, V.T., Ho, L.B., Tran, L.N., "Qmes: Quantum Meta-Learning for Encoding Selection in Quantum Kernel Methods," arXiv:2609.04652v1, 2 | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qml'] -> ['method', 'ml', 'qml'] | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history) | 2026-10-04 (Sprint 6 Task J): also found via QMLPapers/2026/manifest.tsv
- **F10 found**: 'method' candidate (meta-learned encoding selection is an evaluation-methodology contribution) -- Task F's. No citation defect found.

### 17. `wang-2025-quantum-optimization-nn-compression`

- **Title**: Is Quantum Optimization Ready? An Effort Towards Neural Network Compression using Adiabatic Quantum Computing
- **Citation**: Wang, Z., Choong, B.C.M., Huang, T., Gerlinghoff, D., Goh, R.S.M., Liu, C., Luo, T., "Is Quantum Optimization Ready? An Effort Towards Neural Network Compression using Adiabatic Quantum Computing," arXiv:2505.16332v2, 2025-08-14
- **Access**: https://arxiv.org/abs/2505.16332
- **Tier**: screened; **primary context**: qml
- **Disposition**: Real paper on QUBO-based neural-network compression via adiabatic QC; directly relevant to the qml/optimization intersection
- **Applicability**:
  - `ml`: CNN model compression compared against genetic algorithms and reinforcement learning -- arXiv abstract
  - `qc`: Assesses the solution space of commercial quantum annealing devices -- arXiv abstract; F10's body read: the D-Wave Advantage ran only the two smallest models and the larger ones ran on a classical Fujitsu Digital Annealer -- docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md
  - `qml`: Pruning-quantization of convolutional neural networks formulated as a QUBO and solved by adiabatic quantum computing; the optimized target is an ML model -- arXiv abstract
- **Last change** (2026-10-04): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2505.16332 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Wang, Z., Choong, B.C.M., Huang, T., Gerlinghoff, D., Goh, R.S.M., Liu, C., Luo, T., "Is Quantum Optimization Ready? An Effort Towards Neural Network Compressio | 2026-09-19 (Sprint 4 Task C, F25 B1): disposition no longer names a tier; the tier column is the resolver | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qc', 'qml'] -> ['ml', 'qc', 'qml']; qc rationale now carries F10's body-read fact that the larger models ran on a classical Fujitsu Digital Annealer; ml added | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history) | 2026-10-04 (Sprint 6 Task J): also found via QMLPapers/2025/manifest.tsv
- **F10 found**: v2 exists ('submitted to Elsevier'); rationale 'uses quantum annealing hardware directly' is true but incomplete in the wrong direction: the D-Wave Advantage ran only the two smallest models, the larger ones ran on a classical Fujitsu Digital Annealer -- Task F's.

### 18. `zajac-2026-inverse-born-rule-equivalence`

- **Title**: The Inverse Born Rule Equivalence. On the Informational Limits of Real-Valued Amplitude Encodings and the Measurement of Quantum Advantage in Data Embeddings
- **Citation**: Zając, S., Cybulski, J.L., Dziewit, B., Kulpa, T., "The Inverse Born Rule Equivalence. On the Informational Limits of Real-Valued Amplitude Encodings and the Measurement of Quantum Advantage in Data Embeddings," arXiv:2602.21350v2, 2026-06-14
- **Access**: https://arxiv.org/abs/2602.21350
- **Tier**: read; **primary context**: qml
- **Disposition**: Real theoretical paper proving real-valued amplitude encodings collapse to classical quadratic forms (no quantum advantage). Highly relevant to the Fourier-Wall/QML-advantage theme running through several other seed papers
- **Applicability**:
  - `qml`: Real-valued amplitude encodings of classical data; the Inverse Born Rule Fallacy of reading such models as evidence of quantum computational power -- arXiv abstract
  - `world`: Proves an Equivalence Theorem: any real-valued amplitude encoding composed with a data-independent unitary and computational-basis measurement yields exactly the class of classical quadratic forms; information-geometric excess identically 0 -- arXiv abstract
- **Evidence**: Theoretical paper (preprint v2) with a proof and small simulator experiments (NumPy state vector, 2-3 qubits, 5 seeds; agent-read p.11). The core step of Theorem 1 -- a real state vector makes the expectation a real quadratic form, so only Re(M) contributes -- was checked independently by the reader: for Hermitian M and real c, c^T Im(M) c = 0 because Im(M) is antisymmetric. Scope per the authors (p.15): data-independent ansatz only; complex-valued encodings escape the bound (Remark 4, p.6); trainability and NISQ noise not addressed.
- **Last change** (2026-10-03): Sprint 1 Task F: 46-paper seed set loaded at seen tier | 2026-09-19: citation and title re-derived from arxiv:2602.21350 via DataCite (arXiv API refused) (scripts/refresh_citations.py); previous citation: Zając, S., Cybulski, J.L., Dziewit, B., Kulpa, T., "The Inverse Born Rule Equivalence: On the Informational Limits of Real-Valued Amplitude Encodings and the Me | 2026-09-19 (Sprint 4 Task F, F25 D4 re-filing): contexts ['qml'] -> ['qml', 'world']; world added: a proved Equivalence Theorem, the one theorem in the set (F9, F10) | 2026-09-19 (Sprint 4 Task H, F25 D6): promoted to read after a direct read; assertions extracted; see paper_yields | 2026-10-03: Sprint 6 Task F back-fill (ADR-0005 A4): found_via 'Sprint 1 seed set (46 papers)' (from "Sprint 1 Task F: 46-paper seed set"); metadata_provider DataCite (named in the record's history); read_extent transcribed from checked_against_source (1 row(s))
- **F10 found**: Title punctuation differed from arXiv (corrected by API); the one mathematical theorem in the set, which 'world' (mathematics/physics ground truth) fits and which got nothing -- Task F's.

## Timing sheet

Fill one row per record. *Protocol* is `full` (all six steps with the source open) or
`partial: <steps skipped>`. *Calls* is your ACCEPT/REVISE/REJECT per field, or one word for the record.

| # | Record | Start | End | Minutes | Protocol | Calls | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `arute-2019-quantum-supremacy-google-nature` |  |  |  |  |  |  |
| 2 | `britt-humble-2017-hpc-with-qpus-acm` |  |  |  |  |  |  |
| 3 | `dupont-2023-quantum-enhanced-greedy-solver` |  |  |  |  |  |  |
| 4 | `emami-2025-financial-fraud-entropy-computing-qci` |  |  |  |  |  |  |
| 5 | `huynh-2023-quantum-inspired-ml-survey` |  |  |  |  |  |  |
| 6 | `kordzanganeh-2022-benchmarking-simulated-physical-qpu` |  |  |  |  |  |  |
| 7 | `loke-2026-cvqboosting-fraud-detection-smu` |  |  |  |  |  |  |
| 8 | `lubinski-2023-application-oriented-benchmarks-qedc` |  |  |  |  |  |  |
| 9 | `mancilla-2026-fourier-wall-spectra` |  |  |  |  |  |  |
| 10 | `mandra-2021-hybridq-simulator-nasa` |  |  |  |  |  |  |
| 11 | `neven-2012-qboost-adiabatic-quantum-optimization` |  |  |  |  |  |  |
| 12 | `pelofske-2022-quantum-volume-nisq-ieee` |  |  |  |  |  |  |
| 13 | `qci-2024-profiling-cvqboost` |  |  |  |  |  |  |
| 14 | `rand-2022-pqc-critical-infrastructure-assessment` |  |  |  |  |  |  |
| 15 | `rehman-2026-qstar-adaptive-routing` |  |  |  |  |  |  |
| 16 | `tung-2026-qmes-quantum-meta-learning-kernel-encoding` |  |  |  |  |  |  |
| 17 | `wang-2025-quantum-optimization-nn-compression` |  |  |  |  |  |  |
| 18 | `zajac-2026-inverse-born-rule-equivalence` |  |  |  |  |  |  |

**Totals**: records adjudicated ____ ; total minutes ____ ; minutes per record ____ ;
records where the corrected citation still needed a REVISE ____ .

## Comparison row (filled by Claude from the sheet)

| Reviewer | Protocol | Records | Time | Findings |
|---|---|---|---|---|
| F7 Haiku | per-record-internal-consistency | 18 | 182 s | 18/18 confirm |
| F8 Sonnet | per-record-with-certainty-check | 18 | 155 s | 18/18 confirm; certainty step n/a |
| F9 Opus | set-level-cross-record | 18 | 208 s | 7 cross-record inconsistencies |
| F10 Fable-tier | full-adjudication-primary-source | 18 | 599 s | 38 accept / 43 revise / 12 reject; 4 citation defects |
| **Team lead** | team-lead-adjudication (this packet) | 18 | ____ | ____ |

Source for the four model rows: `.claude/model_assignment_heuristics.json` learning_log[0].
