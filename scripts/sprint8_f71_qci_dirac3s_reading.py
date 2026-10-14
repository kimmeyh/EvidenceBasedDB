#!/usr/bin/env python3
"""Sprint 8 Task G (F71): F65's four recovered items, read on 2026-10-13.

(1) The PR Newswire release of 2026-10-01 announcing the Dirac-3S (QCi's own
press release carries the same text); (2) QCi's Dirac-3S Technical
Reference module, whose content is the Continuous Solver Benchmarking
review (QCi-QMS-900-000004 Rev A, 24 pp.), the Dirac-3S User Guide Rev A
(byte-identical to the copy Task C read, now with a public URL) and two QCi
papers on arXiv; (3) the Dirac-3 product page, which now serves the
Dirac-3S; (4) what is new on the site since the 2026-09-24 scrape, computed
by `scripts/sprint8_f71_qci_site_check.py` and reported in
`docs/sprints/SPRINT_8_F71_QCI_SITE_CHECK.md`.

Certainty as in F65: vendor documentation starts MODERATE; a statement
about what a document itself says, checked against the local copy, starts
HIGH. The admission-against-interest candidates are listed in
CANDIDATE_UPGRADES for the team lead (Class 2) and are not upgraded here.
No Dirac-3 assertion is edited; `supports` links go only between Dirac-3S
assertions here.

Every quote was located in the local copy and is checked by
`tests/test_f71_qci_dirac3s_reading.py`. DRY-RUN BY DEFAULT; `--apply`
takes a verified backup first. Idempotent: an existing record, read or
yield is skipped. The two arXiv papers go through the door, one paced
arXiv request each, inside the cap.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, append_updated_reason, insert_assertion, insert_paper  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-13"
TAG = "Sprint 8 Task G, F71"
REASON = f"{TODAY} ({TAG}): extracted from a source read directly on {TODAY}"
CTX = "platform:dirac-3s"

REFS = r"D:\Data\Harold\EvidenceBasedDB\References"
NEW = REFS + r"\QCi-site_2026-10-13"
TECH = REFS + r"\QCi-site\dirac-3s-technical-reference"

PRN = "qci-2026-dirac-3s-announcement-press-release"
BENCH = "qci-2026-dirac-3s-continuous-solver-benchmarking-rev-a"
PROD = "qci-2026-10-13-dirac-3s-product-page"
PROD_OLD = "qci-2026-09-24-dirac-3-product-page"
NB = "qci-2026-dirac-3s-planted-benchmarking-notebook"
NB_URL = "https://quantumcomputinginc.com/learn/benchmarking/planted/dirac-3s-planted-benchmarking"
D3S = "qci-2026-dirac-3s-user-guide-rev-a"

PRN_URL = ("https://www.prnewswire.com/news-releases/quantum-computing-inc-announces-dirac-3s-scaling-to-nearly-"
           "10-000-variables-302895913.html")
QCI_PR_URL = ("https://quantumcomputinginc.com/news/press-releases/2026/quantum-computing-inc.-announces-dirac-3s-"
              "advancing-speed-scale-and-solutions-for-quantum-optimization")
BENCH_URL = ("https://images.ctfassets.net/i1dyhzbyi8ad/4RB85lp462hwxVlZeU8HAq/29abae2661809867dc42dbfaa6b6239b/"
             "Dirac_3S_Continuous_Solver_Benchmarking.pdf")
PROD_URL = "https://quantumcomputinginc.com/products/systems/dirac-3"
GUIDE_URL = ("https://images.ctfassets.net/i1dyhzbyi8ad/2VeAf10vbdBBmVTpsuXdHt/8a48612546bf80fe0a30538d77bc60f3/"
             "Dirac_3S_Users_Guide_Rev_A-1.pdf")

LOCAL = {
    PRN: NEW + r"\prnewswire\quantum-computing-inc-announces-dirac-3s-scaling-to-nearly-10-000-variables-302895913.html",
    BENCH: TECH + r"\Dirac_3S_Continuous_Solver_Benchmarking__4RB85lp462hwxVlZeU8HAq.pdf",
    PROD: NEW + r"\products\systems\dirac-3.html",
    PROD_OLD: REFS + r"\QCi-site\systems\dirac-3.html",
    NB: NEW + r"\learn\benchmarking\planted\dirac-3s-planted-benchmarking.html",
}
MS_FILE = TECH + r"\Motzkin-Straus_Optimization_on_an_Entropy-Computing_Platform__4mfcL8t2byM8pEIsLXl6oH.pdf"
SQ_FILE = TECH + r"\Standard_Quadratic_Formulations_of_Many_NP_Problems__MDdq4hP69ryoXR78JqaYE.pdf"
# Every local copy as read on 2026-10-13; a copy that changes stops the
# script (PR #77 review: only the review PDF was checked at first).
SHA256 = {
    BENCH: "37f63ee29c690685becc783d86796352d10277bc27d51a103b59cf2204dc3373",
    PRN: "e5c72f74fbccef0b59324f4fe6a3f62c40b66df5cf2668f6ecd10abc1cdc9547",
    PROD: "870fc66447997f951d8298a519165a16b2dcaf3a920a7f5951b5e4e8700f2c2f",
    PROD_OLD: "54fbaf311b061e39cd8c6684893f9a0d9d3d1c3c92e240ff17f07bd9a83950c3",
    NB: "798ed16a5874808c070c5162f5cd4d53631c5ad1e1e4756e0453426f9ab155bb",
}
FILE_SHA256 = {
    MS_FILE: "a150a95d2222acdf4a59b93616319da450df3a7852bbcbb1ee4dfffc6b233d06",
    SQ_FILE: "1b6fbb0d0911d79b29c2a9cc80053cb96ee49e13ceeecbcf351fd9f4a933ccca",
}


def sha256_of(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _ref(rid, title, citation, transcribed_from, disposition, access, evidence, cited_as, applicability, reads):
    return {"id": rid, "kind": "reference", "context": applicability[0][0], "tier": "read", "title": title, "citation": citation,
            "transcribed_from": transcribed_from, "disposition": disposition, "access": access, "evidence": evidence,
            "found_via": "team lead, 2026-10-10 (F65's item list, recovered 2026-10-13; F71)", "cited_as": cited_as,
            "checked_against_source": f"{TODAY}, Claude, read the local copy in full",
            "reads": reads, "applicability": applicability,
            "updated_reason": f"{TODAY}: added by scripts/sprint8_f71_qci_dirac3s_reading.py ({TAG}); read in full"}


SOURCES = [
    _ref(PRN, "Quantum Computing Inc. Announces Dirac-3S, Scaling to Nearly 10,000 Variables",
         'Quantum Computing Inc., "Quantum Computing Inc. Announces Dirac-3S, Scaling to Nearly 10,000 Variables," '
         "press release, PR Newswire, Hoboken, N.J., Oct. 1, 2026 (hand-transcribed from the release's headline and "
         "dateline)",
         "the headline and the dateline \"HOBOKEN, N.J. , Oct. 1, 2026 /PRNewswire/\"",
         "Reference: QCi's press release announcing the Dirac-3S (variable count, modules, first shipment, the "
         "Technical Review's headline results); QCi's own site carries the same text",
         f"{LOCAL[PRN]} | {PRN_URL} | {QCI_PR_URL}",
         f"Saved {TODAY} from PR Newswire (HTTP 200); QCi's own copy saved the same day under "
         r"QCi-site_2026-10-13\news\press-releases\2026\ carries the same body text",
         "F65 item 1 (the PR Newswire link)",
         [[CTX, "QCi's announcement of the Dirac-3S: variable counts, expansion modules, first shipment and the "
                "benchmark headline -- the release body"]],
         [["Claude", TODAY, "full", "the whole release"]]),
    _ref(BENCH, "Dirac-3S Technical Reference: Continuous Solver Benchmarking and Performance Characterization, "
                "September 2026, Revision A",
         'Quantum Computing Inc., "Dirac-3S Technical Reference: Continuous Solver Benchmarking and Performance '
         'Characterization," September 2026, Revision A, document QCi-QMS-900-000004 (hand-transcribed from p.1 '
         "and the page header)",
         "p.1 title page and the header line \"QCi-QMS-900-000004 | Rev A\" on every page",
         "Reference: QCi's benchmarking review of the Dirac-3S continuous solver against Hexaly and projected "
         "gradient descent on QPLIB, planted StQP and DIMACS max-clique instances",
         f"{LOCAL[BENCH]} | {BENCH_URL}",
         f"Saved {TODAY} from the link on QCi's Dirac-3S Benchmarking page (HTTP 200); SHA-256 {SHA256[BENCH]}; "
         "1,083,305 bytes; 24 pages. The Software Interface page of the same module links a byte-identical copy "
         "under another asset id",
         "F65 item 2 (the Dirac-3S Technical Reference module)",
         [[CTX, "QCi's own benchmark of the Dirac-3S against Hexaly and PGD: QPLIB, planted StQP up to 9,980 "
                "variables and DIMACS max-clique -- sections 4 to 7, pp. 10-22"]],
         [["Claude", TODAY, "full", "all 24 pages"]]),
    _ref(PROD, "Dirac-3S product page, as served at QCi's Dirac-3 product URL on 2026-10-13",
         "Quantum Computing Inc., Dirac-3S product page, quantumcomputinginc.com/products/systems/dirac-3, read "
         "2026-10-13 (hand-transcribed from the page title)",
         "the page title \"Dirac-3S - Quantum Computing Inc\"",
         "Reference: QCi's product page for the Dirac-3S, which on 2026-10-13 replaced the Dirac-3 page at the "
         "same address (specification table, benchmark headline)",
         f"{LOCAL[PROD]} | {PROD_URL}",
         f"Saved {TODAY} (HTTP 200); the page renders the specification table and text in its HTML",
         "F65 item 3 (the Dirac-3 product page link)",
         [[CTX, "QCi's Dirac-3S product page: specification table by configuration and the benchmark headline "
                "-- the whole page"]],
         [["Claude", TODAY, "full", "the whole page"]]),
    _ref(PROD_OLD, "Dirac-3 product page, as scraped on 2026-09-24",
         "Quantum Computing Inc., Dirac-3 product page, quantumcomputinginc.com/products/systems/dirac-3, scraped "
         "2026-09-24 (hand-transcribed from the page title)",
         "the page title and its heading \"Introducing Dirac-3\"",
         "Reference: QCi's Dirac-3 product page as it stood before the Dirac-3S replaced it (specification "
         "highlights, access options)",
         f"{LOCAL[PROD_OLD]} | {PROD_URL}",
         "The 2026-09-24 scrape's copy; the address now serves the Dirac-3S page (see "
         f"{PROD})",
         "F65 item 3, the baseline for the comparison",
         [["platform:dirac-3", "QCi's Dirac-3 product page before the Dirac-3S: 949 variables, 100 W, access "
                               "options -- the whole page"]],
         [["Claude", TODAY, "full", "the whole page, compared with the 2026-10-13 copy"]]),
    _ref(NB, "Dirac-3S Planted Benchmarking (notebook page)",
         "Quantum Computing Inc., \"Dirac-3S Planted Benchmarking,\" notebook page in QCi's Benchmarking section, "
         "read 2026-10-13 (hand-transcribed from the page heading)",
         "the page heading \"Dirac-3S Planted Benchmarking\"",
         "Reference: QCi's published notebook for the planted-StQP runs of its Dirac-3S benchmarking review "
         "(client set-up, solver call, data loading)",
         f"{LOCAL[NB]} | {NB_URL}",
         f"Saved {TODAY} (HTTP 200); one of nine notebook pages in the section (Dirac-3S, Hexaly and PGD on "
         "max-clique, planted and QPLIB); the three Dirac-3S notebooks set up the client the same way",
         "F65 item 4 (the site's new Benchmarking section)",
         [[CTX, "How QCi ran the Dirac-3S for its planted benchmark: the client and solver set-up -- the notebook's "
                "first cells"]],
         [["Claude", TODAY, "full", "the whole notebook page"]]),
]

# The two QCi papers linked from the module enter at `seen` through the
# door (arXiv ids from each PDF's first-page stamp).
PAPERS = [
    {"access": f"arXiv:2609.38779 | {MS_FILE}", "context": CTX, "tier": "seen",
     "disposition": ("QCi paper linked from the Dirac-3S Technical Reference: max clique and constraint "
                     "satisfaction as Motzkin-Straus simplex programs solved on the Dirac-3S, benchmarked on DIMACS"),
     "found_via": "QCi's Dirac-3S Technical Reference module, 2026-10-13 (F71)",
     "cited_as": "Motzkin-Straus Optimization on an Entropy-Computing Platform",
     "applicability": [[CTX, "Max clique on the Dirac-3S via Motzkin-Straus; DIMACS benchmarks -- abstract"]],
     "updated_reason": f"{TODAY}: added by scripts/sprint8_f71_qci_dirac3s_reading.py ({TAG}); abstract read"},
    {"access": f"arXiv:2610.01911 | {SQ_FILE}", "context": CTX, "tier": "seen",
     "disposition": ("QCi paper linked from the Dirac-3S Technical Reference: standard quadratic (simplex) "
                     "formulations of Karp's 21 problems, the input form the Dirac-3S solves natively"),
     "found_via": "QCi's Dirac-3S Technical Reference module, 2026-10-13 (F71)",
     "cited_as": "Standard Quadratic Formulations of Many NP Problems",
     "applicability": [[CTX, "How NP problems map to the simplex-constrained form the Dirac-3S solves -- abstract"]],
     "updated_reason": f"{TODAY}: added by scripts/sprint8_f71_qci_dirac3s_reading.py ({TAG}); abstract read"},
]


def A(**kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", CTX)
    kw.setdefault("fidelity", "exact")
    return AssertionRecord(**kw)


VENDOR = "Started MODERATE: vendor primary documentation of its own device. Not upgraded"
DOC_FACT = ("Started HIGH: a statement about what QCi's own documents say, each figure checked directly against "
            "the local copies")
CANDIDATE = " here (an admission-against-interest candidate for the team lead, Class 2)"

ASSERTIONS: list[tuple[AssertionRecord, list[str]]] = [
    (A(id="dirac3s-all-optimal-headline-contradicted-by-own-table",
       value=("QCi's benchmarking review and its press release say the Dirac-3S reached the optimum on every planted "
              "instance from 2,000 to 9,980 variables, but the review's own Table 6 (contrast ub = 100) records gaps "
              "of 7.56 percent at n = 2,000 and 9.59 percent at n = 4,000, and its discussion counts six of eight"),
       provenance=f"{BENCH}, p.6 (Key Findings), p.14 (Table 6) and p.18 (section 5.2); {PRN}, release body",
       citation_context=('"Dirac-3S was the only solver among the evaluated methods to achieve zero optimality gap '
                         'across all synthetic benchmark instances with known global optima, spanning problem sizes '
                         'from 2,000 to 9,980 variables." (review p.6); "n2000_k43 2000 43 7.56 13" (review p.14, '
                         'Table 6 row); "n4000_k55 4000 55 9.59 14" (review p.14, Table 6 row); "At ub = 100 '
                         '(Table 6) Dirac-3S reaches it on six of eight" (review p.18); "Dirac-3S was the only '
                         'evaluated solver to achieve the optimal solution across all tested instances" (press '
                         'release)'),
       certainty="high", certainty_reasons=DOC_FACT + ". The headline holds only for the ub = 10 table",
       claim_type="positive"), [BENCH, PRN]),
    (A(id="dirac3s-review-counts-its-ub10-results-two-ways",
       value=("QCi's benchmarking review gives two counts for the Dirac-3S at contrast ub = 10: Table 5 and section "
              "5.2 say it reached the planted optimum on all eight instances, while the conclusion says seven of "
              "eight; section 5.2 also lists three Dirac-3S failures where Table 6 shows two"),
       provenance=f"{BENCH}, p.12 (Table 5), p.18 (section 5.2) and p.20 (section 6)",
       citation_context=('"At ub = 10 (Table 5) Dirac-3S reaches the planted optimum on all the instances" (p.18); '
                         '"reaching the planted optimum on seven of eight instances at ub = 10" (p.20); "for the '
                         'three Dirac-3S failures, at supports 16, 13 and 14 against planted sizes 55, 43 and 55" '
                         '(p.18)'),
       certainty="high", certainty_reasons=DOC_FACT + ". The review does not say which count is right",
       claim_type="positive"), [BENCH]),
    (A(id="dirac3s-best-of-batch-hides-low-per-sample-success",
       value=("QCi's own review warns that its best-of-ten tables hide how often a single Dirac-3S sample is optimal: "
              "on instances recorded as solved, the share of the ten samples at the optimum ranged from nearly all to "
              "about one in ten, and a 0.1 per-sample rate would not survive a batch of two"),
       provenance=f"{BENCH}, p.19, section 5.2 (Figure 4 discussion)",
       citation_context=('"Figure 4 shows that what degrades on the harder instances is not the device\'s best answer '
                         'but the probability of obtaining it." (p.19); "A best-of-batch table therefore reports the '
                         'same value, 0.0, for a per-sample success probability of 1.0 and for one of 0.1, and the '
                         'second of those would not survive a batch of two." (p.19)'),
       certainty="moderate", certainty_reasons=VENDOR + CANDIDATE + ". Consistent with dirac3s-not-an-exact-solver, "
       "which it supports", claim_type="vendor-self-claim",
       supports=["dirac3s-not-an-exact-solver"]), [BENCH]),
    (A(id="dirac3s-max-clique-edge-is-best-of-four-schedules",
       value=("QCi's headline that the Dirac-3S was strongest across the DIMACS max-clique suite takes, per graph, the "
              "best of its four relaxation schedules; the review states that with one fixed schedule the three "
              "solvers perform nearly identically in aggregate, and that half the graphs do not separate them"),
       provenance=f"{BENCH}, p.17 (Benchmark Highlight) and pp.20-21 (section 6)",
       citation_context=('"Dirac-3S achieved the strongest overall performance across the DIMACS benchmark suite" '
                         '(p.17); "First, the maximum-clique advantage is a best-of-four-relaxation-schedules '
                         'advantage. When restricted to a single fixed schedule, the three solvers exhibit nearly '
                         'identical aggregate performance." (p.21); "the three solvers return identical clique '
                         'sizes on 40 of the 80 graphs" (p.20)'),
       certainty="moderate", certainty_reasons=VENDOR + CANDIDATE + ". The product page repeats the headline without "
       "the qualification", claim_type="vendor-self-claim"), [BENCH]),
    (A(id="dirac3s-not-competitive-with-dedicated-clique-solvers",
       value=("QCi's review states that none of the three solvers it compared, the Dirac-3S included, is competitive "
              "with a dedicated maximum-clique algorithm, and that its max-clique margins are one or two vertices"),
       provenance=f"{BENCH}, p.20, section 5.3",
       citation_context=('"these margins are one or two vertices on graphs whose best known cliques number in the '
                         'tens, and that none of the three solvers is competitive with a dedicated combinatorial '
                         'maximum-clique algorithm." (p.20)'),
       certainty="moderate", certainty_reasons=VENDOR + CANDIDATE, claim_type="vendor-self-claim"), [BENCH]),
    (A(id="dirac3s-slower-than-pgd-at-low-contrast",
       value=("In QCi's planted benchmark at contrast ub = 10, projected gradient descent with ten restarts ran 3 to "
              "63 times faster than a ten-sample Dirac-3S batch while solving fewer instances; at ub = 100 the "
              "Dirac-3S was faster from 6,000 variables up, its ten-sample time staying between 376 and 1,015 s"),
       provenance=f"{BENCH}, p.19, section 5.2",
       citation_context=('"PGD is between 3 and 63 times faster at ub = 10, but solves one instance to optimality '
                         'where Dirac-3S solves seven." (p.19); "from n = 6000 upward Dirac-3S is faster and better" '
                         '(p.19); "Dirac-3S\'s 10-sample time at ub = 100 stays between 376 and 1015 seconds across a '
                         'fivefold range of n" (p.19)'),
       certainty="moderate", certainty_reasons=VENDOR + CANDIDATE + " for the ub = 10 part. \"solves seven\" is the "
       "conclusion's count, not Table 5's (see dirac3s-review-counts-its-ub10-results-two-ways)",
       claim_type="vendor-self-claim"), [BENCH]),
    (A(id="dirac3s-qplib-results-do-not-separate-solvers",
       value=("On QCi's three QPLIB instances the Dirac-3S, Hexaly and projected gradient descent all reached the "
              "published best-known objectives to about five significant figures, so the review itself says QPLIB "
              "does not separate the solvers by best objective; its method sentence for this run names Dirac-3"),
       provenance=f"{BENCH}, p.10 (section 4.1) and p.18 (section 5.1)",
       citation_context=('"The three QPLIB instances do not meaningfully differentiate the solvers based on best '
                         'objective value." (p.18); "We run Dirac-3 on relaxation_schedule = 1 with 100 samples." '
                         '(p.10)'),
       certainty="moderate", certainty_reasons=VENDOR + ". Consistent with classical-solvers-match-dirac3-published-"
       "benchmarks (an independent group solved QPLIB_0018 classically in a fraction of a second), which is a "
       "Dirac-3 claim, so it is not linked (ADR-0004 A8 (b))", claim_type="vendor-self-claim"), [BENCH]),
    (A(id="dirac3s-ten-times-claim-compares-two-units-with-one",
       value=("QCi's announcement calls the Dirac-3S's nearly 10,000 variables a 10x increase over its 1,000-variable "
              "system, but the 9,980 figure needs one expansion module; the base Dirac-3S module takes 949 variables, "
              "the Dirac-3's figure"),
       provenance=f"{PRN}, release body; {PROD}, specification table",
       citation_context=('"a 10x increase over QCi\'s current 1,000-variable system" (press release subhead); "with '
                         'QCi demonstrating configurations supporting up to 9,980 variables with one Expansion '
                         'Module" (press release); "Max number of variables 2nd Order 949 9980" (product page, '
                         'specification table)'),
       certainty="high", certainty_reasons=DOC_FACT + ". dirac3s-power-and-size-by-configuration gives the two-unit "
       "configuration (under 1,500 W against 100 W for the base)", claim_type="positive"), [PRN, PROD]),
    (A(id="dirac3s-replaced-dirac-3-on-qci-product-page",
       value=("By 2026-10-13 QCi's Dirac-3 product address served the Dirac-3S page; the Dirac-3 specification shown "
              "there on 2026-09-24 (949 variables, 100 W) is gone, and the new page's specification table repeats the "
              "Dirac-3S guide's ceilings for the base and the one-expansion configurations"),
       provenance=f"{PROD_OLD} and {PROD}, the whole pages compared",
       citation_context=('"In a league of its own 949 Variables" (2026-09-24 page); "Solve 1st 2nd 3rd 4th 5th order '
                         'problems, with up to 9,980 variables" (2026-10-13 page); "Max number of variables 3rd Order '
                         '135 580" (2026-10-13 page, specification table)'),
       certainty="high", certainty_reasons=DOC_FACT + ". The table restates dirac3s-variable-ceiling-by-configuration, "
       "which it supports (a second QCi source, not independent)", claim_type="positive",
       supports=["dirac3s-variable-ceiling-by-configuration"]), [PROD_OLD, PROD]),
    (A(id="dirac3s-benchmark-notebook-runs-direct-and-names-dirac-3",
       value=("QCi's benchmarking review lists the Dirac-3S interface as its cloud API, but QCi's published Dirac-3S "
              "planted notebook connects directly to a device at a private network address and sets up a "
              "\"Dirac-3 solver\"; with the review's own \"We run Dirac-3\", QCi's documents do not settle which "
              "device produced the results"),
       provenance=f"{BENCH}, p.8 (Table 2) and p.10 (section 4.1); {NB}, the first cells",
       citation_context=('"Interface cloud API Python API NumPy" (review p.8, Table 2, read as a table); '
                         '"ip_address= "172.18.15.110" client = EqcClient(ip_address=ip_address)" (notebook); "Set '
                         'up Dirac-3 solver" (notebook); "We run Dirac-3 on relaxation_schedule = 1 with 100 '
                         'samples." (review p.10)'),
       certainty="high", certainty_reasons=DOC_FACT + ". What the documents say, not a finding about which machine "
       "ran: \"Dirac-3\" may be a name carried over, as in the Dirac-3S guide "
       "(dirac3s-guide-reuses-dirac-3-text-and-figures)", claim_type="positive"), [BENCH, NB]),
    (A(id="dirac3s-first-shipment-expected-november-2026",
       value="QCi expected the first customer shipment of the Dirac-3S in November 2026, as of its 2026-10-01 release",
       provenance=f"{PRN}, release body",
       citation_context='"The first customer shipment of Dirac-3S is expected in November 2026." (press release)',
       certainty="low", certainty_reasons=("Started MODERATE: vendor primary statement. DOWNGRADED one level: a "
       "forecast the release marks as a forward-looking statement"), claim_type="vendor-self-claim"), [PRN]),
]

# Admission-against-interest candidates, for the team lead (Class 2): id ->
# why the statement costs QCi something. None is upgraded by this task.
CANDIDATE_UPGRADES = {
    "dirac3s-best-of-batch-hides-low-per-sample-success": ("QCi concedes that its own best-of-ten tables overstate "
                                                           "how often one sample is optimal"),
    "dirac3s-max-clique-edge-is-best-of-four-schedules": ("QCi concedes that its max-clique headline disappears "
                                                          "with a single fixed schedule"),
    "dirac3s-not-competitive-with-dedicated-clique-solvers": ("QCi concedes that a dedicated classical algorithm "
                                                              "beats its device on max clique"),
    "dirac3s-slower-than-pgd-at-low-contrast": "QCi concedes that a simple classical baseline ran up to 63 times faster",
}

GUIDE_NOTE = (f"{TODAY} ({TAG}): a public copy is now linked from QCi's Dirac-3S Technical Reference module "
              f"({GUIDE_URL}); its SHA-256 equals the local copy's, so the evidence's \"No public URL found on "
              "2026-10-12\" no longer holds")


def apply_changes(conn) -> list[str]:
    log = []
    for entry in SOURCES:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (entry["id"],)).fetchone() is None:
            insert_paper(conn, intake.build_record(entry, today=TODAY))
            log.append(f"paper  {entry['id']} [read]")
        else:
            log.append(f"exists {entry['id']}")
    for entry in PAPERS:
        ident = entry["access"].split(" | ")[0]
        # The id as a whole access segment, never a prefix (PR #77 review:
        # LIKE 'arXiv:2101.0001%' also matched arXiv:2101.00011).
        row = next((r for r in conn.execute("SELECT record_id, access FROM paper_fields WHERE access LIKE ?",
                                            (f"%{ident}%",))
                    if ident.lower() in (s.strip().lower() for s in r[1].split("|"))), None)
        if row is None:
            paper = intake.build_record(entry, today=TODAY)
            insert_paper(conn, paper)
            log.append(f"paper  {paper.id} [seen] ({ident})")
        else:
            log.append(f"exists {row[0]} ({ident})")
    existing = conn.execute("SELECT updated_reason FROM records WHERE id = ?", (D3S,)).fetchone()[0] or ""
    if GUIDE_URL not in existing:
        append_updated_reason(conn, D3S, GUIDE_NOTE, TODAY)
        log.append(f"note   {D3S} (public URL found)")
    for assertion, yielded_by in ASSERTIONS:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (assertion.id,)).fetchone():
            log.append(f"exists {assertion.id}")
            continue
        insert_assertion(conn, assertion, yielded_by=yielded_by[0])
        for extra in yielded_by[1:]:
            conn.execute("INSERT OR IGNORE INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)",
                         (extra, assertion.id))
        log.append(f"assert {assertion.id} <- {', '.join(yielded_by)} [{assertion.certainty}, {assertion.claim_type}]")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    missing = [p for p in [*LOCAL.values(), MS_FILE, SQ_FILE] if not Path(p).exists()]
    if missing:
        print("missing local copies:\n" + "\n".join(missing))
        return 1
    for path, digest in [*((LOCAL[r], d) for r, d in SHA256.items()), *FILE_SHA256.items()]:
        if sha256_of(path) != digest:
            print(f"{path} differs from the copy read on {TODAY} (SHA-256)")
            return 1
    if "--apply" not in args:
        for entry in SOURCES:
            intake.build_record(entry, today=TODAY)  # validates the entry; nothing written
            print(f"paper  {entry['id']} [read]")
        for entry in PAPERS:
            print(f"paper  {entry['access'].split(' | ')[0]} [seen] (the door resolves it at --apply)")
        for a, by in ASSERTIONS:
            print(f"assert {a.id} <- {', '.join(by)} [{a.certainty}, {a.claim_type}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F71 Dirac-3S release, benchmarking review and product page")
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
