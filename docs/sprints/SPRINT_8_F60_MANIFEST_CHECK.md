# Sprint 8 Task E (F60): QMLPapers manifest rows against their files

Run 2026-10-12 by `scripts/sprint8_f60_manifest_check.py` (read-only; the
folder `D:\Data\Harold\EvidenceBasedDB\QMLPapers\` is outside the
repository and was not changed). **Every count below is a snapshot as of
2026-10-12.**

## Result

- 13 manifests, 1440 rows; 28 more PDFs that no row names.
- 1397 rows: the file's first-page arXiv stamp names the row's id.
- **1 mismatch**: `2021/Asfaw-et-al._2021_Building-a-Quantum-Engineering-Undergraduate-Program__2108.0131.pdf`.
  The row's id `2108.0131` is one digit short. The file's stamp is
  `arXiv:2108.00131` (Radhakrishnan, Stefanakis, Belkin and Uhler), already
  entered in Sprint 7 Task E. The Asfaw paper itself is
  **arXiv:2108.01311**, "Building a Quantum Engineering Undergraduate
  Program" (its abstract page read 2026-10-12, one request, v1). The store
  already holds it correctly: `asfaw-2021-building-quantum-engineering-undergraduate-program`,
  access `arXiv:2108.01311`, tier `seen` (entered 2026-10-04). Only the
  folder is wrong: the file under the Asfaw name is another paper, and the
  Asfaw PDF was never downloaded. Whether to download it is the team
  lead's decision at Manual Validation.
- 38 rows: the first page carries no arXiv stamp (a journal
  version or a typeset copy), so the file's identity was not checked by
  stamp. In every one the file name's id equals the row's id, and all 38
  are in the store. Listed, not guessed.
- 4 rows with no arXiv id (`NonArxiv`): not checked by stamp.
- No row's file is missing, and no file name's id differs from its row's id.
- 28 PDFs have no manifest row: added to the folders by hand after
  the manifests were written (the Dirac-3 and tensor papers among them).
  27 are in the store by arXiv id. The one without an id,
  `NonArxiv/Cerezo_2020_Key-questions-for-the-quantum-machine-learner-to-ask-themselves.pdf`,
  is **not in the store** (no record by id, access or title); entering it
  is a candidate for the team lead, not done here (outside F60's scope).

## Rows with no first-page stamp

- `2007-2017/Sgarbas_2007_The-road-to-Quantum-Artificial-Intelligence__0705.3360.pdf`
- `2020/Tang-et-al._2020_CutQC-Using-Small-Quantum-Computers-for-Large-Quantum-Circuit-Evaluations__2012.02333.pdf`
- `2021/Ezhov_2021_On-quantum-Neural-Networks__2104.07106.pdf`
- `2022/Zhan-2022_Variational-Quantum-Search-with-Exponential-Speedup__2212.09505.pdf`
- `2023/Akter-et-al._2023_Software-Supply-Chain-Vulnerabilities-Detection-in-Source-Code-Performance__2306.08060.pdf`
- `2023/Ganguly_2023_Implementing-Quantum-Generative-Adversarial-Network-qGAN-and-QCBM-in-Finance__2308.08448.pdf`
- `2023/Gheisarnejad-Khooban_2023_Quantum-Power-Electronics-From-Theory-to-Implementation__2303.04763.pdf`
- `2023/Jain_2023_CQural-A-Novel-CNN-based-Hybrid-Architecture-for-Quantum-Continual-Machine-Learning__2305.09738.pdf`
- `2023/Lawrie-Tanner-Chronopoulos_2023_A-quantum-graph-approach-to-metamaterial-design__2306.05890.pdf`
- `2023/Mangini_2023_Variational-quantum-algorithms-for-machine-learning__2306.09984.pdf`
- `2023/Ren-et-al._2023_Towards-Quantum-Federated-Learning__2306.09912.pdf`
- `2023/Santi-Mishra-Mohanty_2023_Quantum-Text-Classifier-A-Synchronistic-Approach-Towards-Classical__2305.12783.pdf`
- `2023/Schetakis-et-al._2023_Quantum-Machine-Learning-for-Credit-Scoring__2308.03575.pdf`
- `2023/Shi-et-al._2023_Hybrid-quantum-classical-convolutional-neural-network-for-phytoplankton__2303.03707.pdf`
- `2023/Soltaninia-Shan_2023_Comparison-of-Quantum-Simulators-for-Variational-Quantum-Search-A__2309.05924.pdf`
- `2023/Suzuki-Hasebe-Miyazaki_2023_Quantum-support-vector-machines-for-classification-and-regression__2307.02091.pdf`
- `2023/Zeng-et-al._2023_Quantum-Neural-Network-Inspired-Hardware-Adaptable-Ansatz-for-Efficient__2301.07542.pdf`
- `2024/Akpinar-Islam-Oduncuoglu_2024_Evaluating-the-Impact-of-Different-Quantum-Kernels-on-the__2407.09930.pdf`
- `2024/Amani-Kargarian_2024_Quantum-Optimization-for-Energy-Management-A-Coherent-Variational__2412.14095.pdf`
- `2024/Aminpour-Sharif_2024_Strategic-Data-Re-Uploads-A-Pathway-to-Improved-Quantum-Classification__2405.09377.pdf`
- `2024/Lourenco-et-al._2024_Exploring-Quantum-Active-Learning-for-Materials-Design-and-Discovery__2407.18731.pdf`
- `2024/Silveira-de-Borba-Maziero_2024_Hybrid-model-of-the-kernel-method-for-quantum-computers__2410.23315.pdf`
- `2024/Singh_2024_Optimised-Hybrid-Classical-Quantum-Algorithm-for-Accelerated-Solution-of-Sparse__2410.02408.pdf`
- `2025/Ashok-Attisara-Kumar_2025_Quantum-Machine-Learning-for-Optimizing-Entanglement-Distribution__2508.21252.pdf`
- `2025/DAmore-et-al._2025_Assessing-Projected-Quantum-Kernels-for-the-Classification-of-IoT-Data__2505.14593.pdf`
- `2025/Fleury-Lacomme_2025_Quantum-circuit-for-exponentiation-of-Hamiltonians-an-algorithmic__2501.17780.pdf`
- `2025/Niu-et-al._2025_Quantum-Computing-in-Transport-Science-A-Review__2503.21302.pdf`
- `2025/Romero-Rocha-et-al._2025_Quantum-Simulation-and-Optimization-of-Water-Distribution-Networks__2507.06862.pdf`
- `2025/Shahriyar-Tanbhir_2025_Advancements-and-Challenges-in-Quantum-Machine-Learning-for-Medical__2504.13910.pdf`
- `2025/Tomar-Tripathi-Kumar_2025_Comprehensive-Survey-of-QML-From-Data-Analysis-to-Algorithmic__2501.09528.pdf`
- `2025/Vasques-Paik-Cif_2025_Application-of-quantum-machine-learning-using-quantum-kernel-algorithms__2502.06281.pdf`
- `2025/Zhang-Kamenev_2025_How-to-Train-Your-Dragon-Quantum-Neural-Networks__2506.05244.pdf`
- `2026/Lim-et-al._2026_Scalable-Memory-Sharing-in-Photonic-Quantum-Memristors-for-Reservoir-Computing__2601.23044.pdf`
- `2026/Wu-Goan_2026_Quantum-Recurrent-Unit-A-Parameter-Efficient-Quantum-Neural-Network-Component__2601.18164.pdf`
- `Reviews/Ferrie_2024_What-You-Shouldnt-Know-About-Quantum-Computers__2405.15838.pdf`
- `Reviews/Dalzell-et-al._2023_Quantum-algorithms-A-survey-of-applications-and-end-to-end-complexities__2310.03011.pdf`
- `Workforce/Blanchette-et-al._2024_The-Design-and-Implementation-of-a-Quantum-Information-Science__2412.01874.pdf`
- `Workforce/Rosenberg-Holincheck-Colandene_2024_Science_Technology_Engineering_and-Mathematics__2404.03439.pdf`

## PDFs with no manifest row

- `2022/Sannia-et-al._2022_Dissipation-as-a-resource-for-Quantum-Reservoir-Computing__2212.12078.pdf`
- `2023/Sannia-et-al._2023_Engineered-dissipation-to-mitigate-barren-plateaus__2310.15037.pdf`
- `2023/Wurtz-et-al._2023_Aquila-QuEra-s-256-qubit-neutral-atom-quantum-computer__2306.11727.pdf`
- `2024/Kim-Choi_2024_Dequantizability-from-inputs__2405.13273.pdf`
- `2024/Nguyen-et-al._2024_Entropy-Computing-A-Paradigm-for-Optimization-in-Open-Photonic-Systems__2407.04512.pdf`
- `2024/Wu-et-al._2024_No-Free-Lunch-Theories-for-Tensor-Network-Machine-Learning-Models__2412.05674.pdf`
- `2025/Berezutskii-et-al._2025_Tensor-networks-for-quantum-computing__2503.08626.pdf`
- `2025/Chowdhury-et-al._2025_Gottesman-Knill-Limit-on-One-way-Communication-Complexity-Tracing-the__2506.19369.pdf`
- `2025/Hohenfeld-et-al._2025_Explaining-Anomalies-with-Tensor-Networks__2505.03911.pdf`
- `2025/Huang-Hu_2025_Noise-Reversal-by-Entropy-Quantum-Computing__2502.08591.pdf`
- `2025/Mandl-et-al._2025_Loss-Behavior-in-Supervised-Learning-with-Entangled-States__2509.10141.pdf`
- `2025/Orquin-Marques-et-al._2025_Analog-Quantum-Feature-Selection-with-Neutral-Atom-Quantum-Processors__2510.20798.pdf`
- `2025/Sweke-et-al._2025_Kernel-based-dequantization-of-variational-QML-without-Random-Fourier-Features__2503.23931.pdf`
- `2025/Thio-et-al._2025_Kirkwood-Dirac-Nonpositivity-is-a-Necessary-Resource-for-Quantum-Computing__2506.08092.pdf`
- `2026/Ballin-Barcaroli_2026_Optimal-Stratification-of-a-Sampling-Frame-A-Comparative-Study-of__2608.10787.pdf`
- `2026/Chaves-et-al._2026_A-Mixture-of-Experts-Framework-for-Practical-Hybrid-Quantum-Models__2603.06473.pdf`
- `2026/Faryad_2026_The-Input-Problem-A-Permanent-Bottleneck-for-Quantum-Machine-Learning__2608.08433.pdf`
- `2026/Innan-et-al._2026_Q-SYNTH-Hybrid-Quantum-Classical-Adversarial-Augmentation-for-Imbalanced-Fraud__2605.21164.pdf`
- `2026/Markidis_2026_Practical-Considerations-for-Processing-Massive-Classical-Data-via-Quantum-Oracle__2609.13549.pdf`
- `2026/Miri-et-al._2026_Zeno-Blockade-Enabling-Photonic-Quantum-Optimization__2604.13032.pdf`
- `2026/Moosavian-Ravan_2026_A-Critical-Comment-on-Entropy-Computing-A-Paradigm-for-Optimization__2605.03612.pdf`
- `2026/Nuatho-et-al._2026_Quantum-Enhanced-Synthetic-Data-Generation-Using-Quantum-Circuit-Born-Machines__2607.09113.pdf`
- `2026/Svozil_2026_Answer-Partitions-and-Oracle-Access-Determine-Quantum-Query-Complexity__2605.12675.pdf`
- `2026/Valverde-et-al._2026_Quantum-inspired-tensor-networks-in-machine-learning-models__2604.14287.pdf`
- `2026/Yao-et-al._2026_A-Variational-Dissipative-Framework-for-Quantum-Algorithms__2605.25841.pdf`
- `2026/Zhang-et-al._2026_A-Theory-of-Finite-Noise-Optima-and-Generalization-in-Quantum__2608.24229.pdf`
- `2026/Zhu-et-al._2026_Rethinking-Noise-in-Quantum-Machine-Learning-When-Noise-Improves-Learning__2601.13275.pdf`
- `NonArxiv/Cerezo_2020_Key-questions-for-the-quantum-machine-learner-to-ask-themselves.pdf`
