#!/usr/bin/env python3
"""Sprint 14 Task A (F119): Brighindi's PHI-OMEGA paper, with its posts, comments, images and code.
INTAKE_WORKFLOW.md section 54.

Four source records, all under `ml` (team lead, 2026-10-28: "the paper is ML-related as it is rlated to
predictions/solvers"):

- the paper (3 pages, 2026-09-25, self-published), read in full: its text through `source_text`, and its three
  pages viewed as images, since the text layer is where the quote check reads and the pages show the symbols
  and Figure 1;
- the LinkedIn posts and the comment thread, as the team lead pasted them (the PHI-OMEGA reference in
  `References\\`), read in full; the three images, read by eye (F116 does not exist yet), restate the posts'
  claims and carry no data, so they are described in the reference record and in the post's assertion, never
  quoted as checked text;
- the author's own repositories `phi-infinity-runtime` (4ee4ea3) and `m-omnia-validation` (d3e45f3), read
  only where they bear on the paper's claims (Sprint 13 Manual Validation Q11 = 1): the stress-test summary,
  the research status note of 27 September, the README, `src/` and `validation/` searched for the paper's
  mechanisms, and THEORY.md. The status note was missed at the first apply and found by its fresh-eyes review
  (2026-10-30); both repositories' read rows are corrected in place by `correct_reads`.

The Zenodo archive DOI:10.5281/zenodo.19857066 bears on none of the paper's claims: none of its 610 file
entries holds PHI-OMEGA, M-OMNIA, "dS = 0", arc-length, the seed 20260925, symplectic or Hamiltonian
(searched 2026-10-30; the reference said 608 files). It is named in the absence claim's search scope, not
entered.

Grades come from store.grading. The paper's own definitions and setup are graded on their basis; whether
its axioms hold is the author's claim. The author's own repository states the limits the paper leaves out:
that one seed shows no absolute immunity, and that the test is a simulator result, not a general proof. The
first cannot hold beside the paper's claim that the test demonstrates absolute immunity, so it is linked
`contradicts` (ADR-0004 A8 (b): both cannot hold for the same test). The second can (a result may be absolute
inside its simulator), so it is not linked; the link the first correction gave it is withdrawn.

Every quote is checked by `require_verbatim`, with the value, against its source before anything is
written. DRY-RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.grading import grade, high_grades, low_grade  # noqa: E402
from store.ingest import (AssertionRecord, append_updated_reason, insert_paper,  # noqa: E402
                          insert_verified_assertion, sync_verified_assertion, validate_assertion)
from store.quotes import require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-30"
TAG = "Sprint 14 Task A, F119"
DATA = Path(r"D:\Data\Harold\EvidenceBasedDB")
PAPER_PDF = DATA / "Papers" / "2026-09_Brighindi_From-Open-Heuristics-to-Native-Runtime-Invariance.pdf"
POSTS_MD = DATA / "References" / "2026-09_Brighindi_PHI-OMEGA_LinkedIn-post-and-comments.md"
REPOS = DATA / "GitHubRepos"
RUNTIME = REPOS / "phi-infinity-runtime"
STRESS_MD = RUNTIME / "docs" / "validation" / "ADVERSARIAL_STRESS_TEST_2026-09-25.md"
STATUS_MD = RUNTIME / "docs" / "M_OMNIA_STATO_RICERCA_2026-09-27.md"
RUNTIME_README = RUNTIME / "README.md"
OMNIA = REPOS / "m-omnia-validation"
OMNIA_README = OMNIA / "README.md"
OMNIA_THEORY = OMNIA / "THEORY.md"
POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7509241891494866944/"
IMAGES = ("Phi-Omega Invariant Substrate vs. Legacy Solvers.jpeg",
          "Towards a Physics fo Structural Coherence 20261028.jpeg",
          "United Fallacy of Physical AI - Massimiliano Brighindi 20261028.jpeg")
FOUND_VIA = ("the team lead, 2026-10-28, Sprint 13 Manual Validation: \"add the following text and paper to the "
             "paper repository and terget read for next sprint - highest priority\" (F119)")
REASON = f"{TODAY} ({TAG}): extracted from the source, read on {TODAY}"
SYNC_REASON = f"{TODAY} ({TAG}): corrected against the source (INTAKE_WORKFLOW.md section 54)"

PAPER_ID = "brighindi-2026-phi-omega-substrate-mechanics"
POSTS_ID = "brighindi-2026-phi-omega-linkedin-posts-and-comments"
RUNTIME_ID = "phiomegaruntime-rgb-phi-infinity-runtime-github-repo"
OMNIA_ID = "phiomegaruntime-rgb-m-omnia-validation-github-repo"

# key -> (local file the quotes are read in, the record that yields the assertion)
TEXTS = {
    "paper": (PAPER_PDF, PAPER_ID),
    "posts": (POSTS_MD, POSTS_ID),
    "stress": (STRESS_MD, RUNTIME_ID),
    "status": (STATUS_MD, RUNTIME_ID),
    "runtime": (RUNTIME_README, RUNTIME_ID),
    "omnia": (OMNIA_README, OMNIA_ID),
    "theory": (OMNIA_THEORY, OMNIA_ID),
}
COMMITS = {RUNTIME_ID: "4ee4ea3", OMNIA_ID: "d3e45f3"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paper_entry() -> dict:
    return {
        "id": PAPER_ID, "kind": "paper", "context": "ml", "tier": "read",
        "title": "From Open Heuristics to Native Runtime Invariance: The PHI-OMEGA Substrate Mechanics",
        "citation": ("Brighindi, M., \"From Open Heuristics to Native Runtime Invariance: The PHI-OMEGA Substrate "
                     "Mechanics,\" self-published (Independent Researcher, PHI-OMEGA Runtime), 3 pages, "
                     "September 25, 2026 (hand-transcribed from the paper's title block)"),
        "transcribed_from": "the paper's title, author line, affiliation line and date on page 1",
        "disposition": ("A self-published 3-page paper proposing 'Relational Substrate Mechanics (PHI-OMEGA)': "
                        "three axioms, a conservation closure (sum of dS = 0) and a deterministic runtime gate "
                        "(M_gate) in the execution kernel, and one fixed-seed stress test against an "
                        "'open heuristic' control. It states its claims; it gives no theorem, proof or data"),
        "access": str(PAPER_PDF),
        "evidence": (f"Local copy {PAPER_PDF.name}, SHA-256 {sha(PAPER_PDF)}; pdfTeX, created 2026-09-25. "
                     "Self-published; no DOI or arXiv id found (2026-10-28)."),
        "found_via": FOUND_VIA, "cited_as": PAPER_PDF.name,
        "checked_against_source": f"{TODAY}, Claude, read the whole paper (3 pages), each page also viewed as an image",
        "reads": [["Claude", TODAY, "full",
                   "the whole paper, 3 pages: the text through the quote check's extractor, and pages 1 to 3 viewed "
                   "as images for the symbols and Figure 1"]],
        "applicability": [["ml", "a claimed solver and prediction substrate (team lead, 2026-10-28: \"the paper is "
                                 "ML-related as it is rlated to predictions/solvers\") -- read in full"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint14_f119_reading.py ({TAG}); read in full",
    }


def posts_entry() -> dict:
    return {
        "id": POSTS_ID, "kind": "reference", "context": "ml", "tier": "read",
        "title": "PHI-OMEGA: LinkedIn posts, comment thread and images (Brighindi, 2026)",
        "citation": ("Brighindi, M., LinkedIn posts \"The End of Patchwork Physics\" (Sep 25, 2026) and \"The Unified "
                     f"Fallacy of Physical AI\" (2026-09-23, per the team lead), with a comment thread, {POST_URL} "
                     "(hand-transcribed from the text the team lead pasted on 2026-10-28; not checked against "
                     "LinkedIn, which needs a login)"),
        "transcribed_from": "the posts' first lines and dates as the team lead pasted them",
        "disposition": ("Reference: the author's own posts about PHI-OMEGA, one reader's comment and the author's "
                        "reply, and three images read by eye (each restates the posts' claims; none carries data)"),
        "access": f"{POSTS_MD} | {POST_URL}",
        "evidence": (f"Local copy {POSTS_MD.name}, SHA-256 {sha(POSTS_MD)}, the team lead's paste of 2026-10-28. "
                     "Images read by eye on 2026-10-30, each in ImagesAndVideo\\: "
                     + "; ".join(f"{n}, SHA-256 {sha(DATA / 'ImagesAndVideo' / n)}" for n in IMAGES)
                     + ". The first restates the 25 September post (\"zero energy drift\", \"mathematically "
                     "impossible to violate conservation laws\") over curves drawn without data; the second places "
                     "M_gate and the closure at the center of five fields, each naming a person, and does not say "
                     "whether they endorse it; the third restates the 23 September post, with garbled panel text."),
        "found_via": FOUND_VIA, "cited_as": POST_URL,
        "checked_against_source": f"{TODAY}, Claude, read the whole paste and viewed the three images",
        "reads": [["Claude", TODAY, "full", "the whole paste (two posts and the comment thread) and the three images"]],
        "applicability": [["ml", "the author's own claims for PHI-OMEGA as a solver substrate, and one reader's "
                                 "challenge to them -- read in full"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint14_f119_reading.py ({TAG}); read in full",
    }


def read_detail(rid: str, detail: str) -> str:
    return f"{detail} at {COMMITS[rid]}; the rest not read (Q11 = 1: only what bears on the paper's claims)"


def repo_entry(rid: str, name: str, disposition: str, detail: str) -> dict:
    return {
        "id": rid, "kind": "repo", "context": "ml", "tier": "read",
        "access": f"https://github.com/phiomegaruntime-rgb/{name}",
        "disposition": disposition,
        "evidence": (f"Cloned to {REPOS / name} at {COMMITS[rid]} (2026-10-28). Read only where it bears on the "
                     "PHI-OMEGA paper's claims (Sprint 13 Manual Validation Q11 = 1)."),
        "found_via": ("found 2026-10-28 by searching the GitHub account that holds m-domain-independent-core, "
                      "named by the team lead with the paper"),
        "cited_as": f"github.com/phiomegaruntime-rgb/{name}",
        "checked_against_source": f"{TODAY}, Claude, read {detail} at {COMMITS[rid]}",
        "reads": [["Claude", TODAY, "partial", read_detail(rid, detail)]],
        "applicability": [["ml", "the author's own code and validation notes for the PHI-OMEGA paper's stress test "
                                 "and claims -- read where they bear on them"]],
        "updated_reason": f"{TODAY}: added by scripts/sprint14_f119_reading.py ({TAG})",
    }


# What the first apply recorded: "the rest bears on none of the paper's claims". For the runtime it was wrong (it
# missed docs/M_OMNIA_STATO_RICERCA_2026-09-27.md); for m-omnia no search was recorded behind it. correct_reads
# replaces each, matched on its exact first text.
RUNTIME_READ_FIRST = ("docs/validation/ADVERSARIAL_STRESS_TEST_2026-09-25.md and README.md in full, with src/ and "
                      "validation/ searched for the paper's mechanisms (sum of dS, conservation, M_gate, arc-length) "
                      "at 4ee4ea3; the rest bears on none of the paper's claims (Q11 = 1)")
OMNIA_READ_FIRST = "README.md and THEORY.md in full at d3e45f3; the rest bears on none of the paper's claims (Q11 = 1)"
RUNTIME_DETAIL = ("docs/validation/ADVERSARIAL_STRESS_TEST_2026-09-25.md, docs/M_OMNIA_STATO_RICERCA_2026-09-27.md "
                  "and README.md in full, with src/ and validation/ searched for the paper's mechanisms (sum of dS, "
                  "conservation, M_gate, arc-length)")
OMNIA_DETAIL = ("README.md and THEORY.md in full, with all 30 tracked files searched for PHI-OMEGA, the sum of dS, "
                "dS = 0, M_gate, the seed 20260925 and immunity (no hits, 2026-10-30)")
READ_CORRECTIONS = {RUNTIME_ID: (RUNTIME_READ_FIRST, RUNTIME_DETAIL), OMNIA_ID: (OMNIA_READ_FIRST, OMNIA_DETAIL)}

# Links an earlier apply wrote that fail ADR-0004 A8 (b), each with why (sync only ever adds a link).
WITHDRAWN = [
    ("phi-infinity-runtime-calls-the-closure-a-hypothesis-and-the-test-no-general-proof",
     "phi-omega-paper-claims-closure-makes-structural-failure-impossible", "contradicts",
     "contradicts withdrawn (second fresh-eyes review): \"a result in the defined simulator, not a general physical "
     "proof\" can hold beside a claim of absolute immunity inside that simulator, and a closure stated as an axiom "
     "is already a hypothesis, so both can hold (ADR-0004 A8 (b))"),
]

ENTRIES = {
    PAPER_ID: paper_entry,
    POSTS_ID: posts_entry,
    RUNTIME_ID: lambda: repo_entry(
        RUNTIME_ID, "phi-infinity-runtime",
        ("Code repository: Brighindi's PHI-INFINITY runtime (no license file). Its validation notes hold the "
         "PHI-OMEGA paper's 25 September stress test, which they say is a fixed-seed simulation separate from "
         "the repository's src/ engine, with the raw files and the generator unpublished"),
        RUNTIME_DETAIL),
    OMNIA_ID: lambda: repo_entry(
        OMNIA_ID, "m-omnia-validation",
        ("Code repository: Brighindi's evidence-first validation of Relational Substrate Mechanics "
         "(M-OMNIA / Phi-Infinity), a preregistration that claims no empirically verified result"),
        OMNIA_DETAIL),
}

# The coordinator's HIGH grades, each with its basis (store.grading).
HIGH = high_grades({
    "phi-omega-paper-defines-three-axioms-and-a-fail-closed-gate": (
        "definition", "Sections 2 and 3 define the paper's own terms; whether they hold is a separate claim"),
    "phi-omega-paper-stress-test-setup": (
        "setup", "Section 4 states the test's seed, cycle count and the three measures it tracks"),
    "phi-omega-paper-gives-no-proof-for-its-closure-claim": (
        "scope", "the whole paper, 3 pages, read: Sections 2 and 3 state the closure as an axiom and give no "
                 "theorem, proof or derivation"),
    "phi-infinity-stress-test-not-reproducible-and-no-immunity-inferred": (
        "stated limit", "the author's own repository, docs/validation/ADVERSARIAL_STRESS_TEST_2026-09-25.md at "
                        "4ee4ea3, states it"),
    "m-omnia-validation-claims-no-empirically-verified-result": (
        "stated limit", "the author's own repository, README.md and THEORY.md at d3e45f3, state it"),
    "phi-infinity-runtime-calls-the-closure-a-hypothesis-and-the-test-no-general-proof": (
        "stated limit", "the author's own repository, docs/M_OMNIA_STATO_RICERCA_2026-09-27.md at 4ee4ea3, "
                        "states it"),
})


def A(key: str, **kw) -> tuple[str, AssertionRecord]:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", "ml")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    otherwise = kw.pop("otherwise", None) or low_grade("authors' claim")
    kw["certainty"], kw["certainty_reasons"] = grade(kw["id"], HIGH, otherwise=otherwise)
    kw["provenance"] = f"{TEXTS[key][1]}, {kw['provenance']}"
    return key, AssertionRecord(**kw)


NOT_SHOWN = ("the paper states it and gives no theorem, proof, derivation or data for it; the author's own "
             "repositories say the stress test is not reproducible from them and that no absolute immunity "
             "follows from one seed")

ASSERTIONS: list[tuple[str, AssertionRecord]] = [
    A("paper", id="phi-omega-paper-claims-closure-makes-structural-failure-impossible",
      value=("Brighindi's paper claims that embedding an algebraic metric closure (the sum of dS = 0) and "
             "deterministic runtime gates (M_gate) in the execution kernel lets PHI-OMEGA eliminate state "
             "divergence at the root, and that this renders structural failure mathematically impossible; its "
             "abstract says the stress test demonstrates absolute structural immunity to unconstrained drift"),
      provenance="Abstract and Section 5 (Conclusion)",
      citation_context=('"By embedding a conservative algebraic metric closure (ΣdS = 0) and intrinsic '
                        'Deterministic Runtime Gates (Mgate) directly into the core execution kernel, PHI- OMEGA '
                        'eliminates state divergence at the root." (Abstract); "demonstrating absolute structural '
                        'immunity to unconstrained drift" (Abstract); "by rendering structural failure '
                        'mathematically impossible via native runtime invariance" (Section 5)'),
      otherwise=low_grade("authors' claim", NOT_SHOWN)),
    A("paper", id="phi-omega-paper-defines-three-axioms-and-a-fail-closed-gate",
      value=("The paper defines PHI-OMEGA by three axioms: Primary Geometric Invariance (the execution "
             "environment as a projection of closed manifold invariants), Algebraic Metric Closure (every state "
             "transition bound by the conservation equation sum of dS = 0, unconserved exchanges inadmissible) "
             "and Internal Relational Time (progression anchored to validated relational state changes, not an "
             "external clock dt); and a Deterministic Runtime Gate (M_gate) in the substrate transition layer "
             "that monitors residual entropic stress R_i and, at critical thresholds, executes an immediate "
             "stop instead of a probabilistic recovery. These are its definitions, not results"),
      provenance="Section 2 (Theoretical Foundations) and Section 3 (Execution Architecture)",
      citation_context=('"The architecture of Relational Substrate Mechanics is governed by three primary '
                        'axioms" (Section 2); "The execution environment is a direct projection of closed manifold '
                        'invariants" (Section 2); "Algebraic Metric Closure (ΣdS = 0)" (Section 2); "Every state '
                        'transition is bound by a strict conservation equation" (Section 2); "Unconserved exchanges are syntactically and executably '
                        'inadmissible" (Section 2); "System progression is anchored exclusively to vali- dated '
                        'relational state changes" (Section 2); "Hardcoded into the substrate transition layer, '
                        'Mgate continuously monitors residual entropic stress (Ri)." (Section 3); "Upon reaching '
                        'critical thresholds, instead of attempting proba- bilistic recovery, the gate executes an '
                        'immediate geometric stop" (Section 3)')),
    A("paper", id="phi-omega-paper-stress-test-setup",
      value=("The paper's stress test puts an open heuristic control and the PHI-OMEGA substrate through the same "
             "deterministic sequence of non-linear adversarial shocks from one fixed seed (SEED = 20260925) over "
             "N = 100 cycles, tracking trajectory drift (the control's cumulative error against PHI-OMEGA's "
             "residual stress R_i), the failure mode (silent corruption against a clean M_gate stop) and the "
             "count of non-conservative transitions the closure rejects"),
      provenance="Section 4 (Experimental Design)",
      citation_context=('"both the open heuristic control group and the PHI-OMEGA substrate are subjected to an '
                        'identical, deterministic sequence of non-linear adversarial shocks governed by a fixed '
                        'seed (SEED = 20260925)." (Section 4); "across N = 100 discrete execution cycles" (Section '
                        '4); "Trajectory Drift: The cumulative unmanaged error in the open heuristic model versus '
                        'the bounded residual entropic stress (Ri) in the PHI-OMEGA kernel." (Section 4); "Failure '
                        'Mode and State Integrity" (Section 4); "Algebraic Rejections: The frequency of '
                        'non-conservative state transitions intercepted" (Section 4)')),
    A("paper", id="phi-omega-paper-control-corrupts-at-cycle-16",
      value=("In the paper's Figure 1 (SEED = 20260925), the open heuristic control's cumulative drift crosses "
             "its corruption threshold at cycle 16, while PHI-OMEGA's residual R_i stays below its M_gate "
             "threshold to the last cycle plotted with no fail-closed stop, by rejecting non-conservative "
             "transitions. The two curves are different metrics, so their gap does not measure an improvement on "
             "one error (the author's own repository says so)"),
      provenance="Figure 1 and its caption, page 3 (the curves read by eye)",
      citation_context=('"Figure 1: Comparative adversarial stress test under identical disturbance sequence '
                        '(SEED = 20260925)." (Figure 1 caption); "The open heuristic control model accumulates '
                        'unmanaged drift, triggering critical '
                        'corruption at cycle 16, whereas the PHI-OMEGA substrate maintains metric bounds via alge- '
                        'braic rejections" (Figure 1 caption); "without requiring a hard fail-closed stop" (Figure '
                        '1 caption); "sono metriche diverse" (the repository\'s stress-test summary)'),
      evidence_tag="SIM",
      otherwise=low_grade("measured result",
                          "one seed and a control the author built; the raw files and the generator are not "
                          "published (phi-infinity-stress-test-not-reproducible-and-no-immunity-inferred)")),
    A("paper", id="phi-omega-paper-claims-full-reproducibility",
      value=("The paper says its generated logs, cycle-by-cycle metrics and comparative plots ensure full "
             "reproducibility and provide empirical proof of structural immunity; it publishes none of them, "
             "and names no repository or data location"),
      provenance="Section 4, last paragraph",
      citation_context=('"Generated logs, cycle-by-cycle metrics, and comparative visual plots ensure full '
                        'reproducibil- ity and provide empirical proof of structural immunity." (Section 4)'),
      otherwise=low_grade("authors' claim", NOT_SHOWN)),
    A("paper", id="phi-omega-paper-gives-no-proof-for-its-closure-claim",
      value=("The paper gives no theorem, proof or derivation that its closure (the sum of dS = 0) keeps energy "
             "or any other invariant for any class of systems: it states the closure as an axiom, and its claim "
             "that failure is mathematically impossible rests on that statement and on one fixed-seed test. A "
             "reader of the author's post asked for exactly that theorem (\"If that theorem exists, that would "
             "be the real smoking gun\"); none was given in the thread"),
      provenance="the whole paper, read in full; the comment thread",
      citation_context=('"The architecture of Relational Substrate Mechanics is governed by three primary '
                        'axioms" (Section 2); "Algebraic Metric Closure (ΣdS = 0)" (Section 2); "Every state '
                        'transition is bound by a strict conservation equation" (Section 2); "If that theorem '
                        'exists, that would be the real smoking gun." (comment)'),
      claim_type="absence",
      search_scope=("the whole paper (3 pages, text and page images); phi-infinity-runtime at 4ee4ea3 (src/ and "
                    "validation/ searched for the sum of dS, conservation, M_gate and arc-length; the stress-test "
                    "summary, the research status note docs/M_OMNIA_STATO_RICERCA_2026-09-27.md and README read); "
                    "m-omnia-validation at d3e45f3 (README.md, THEORY.md); the Zenodo archive "
                    "10.5281/zenodo.19857066 (610 file entries searched; the repositories' own Zenodo deposits "
                    "not searched); GitHub repository search for PHI-OMEGA, M-OMNIA and Brighindi, 2026-10-28; "
                    "the status note read 2026-10-30")),
    A("posts", id="brighindi-post-claims-energy-drift-mathematically-impossible",
      value=("In his LinkedIn post \"The End of Patchwork Physics\", Brighindi claims that any scheme using an external time "
             "step dt inevitably violates intrinsic conservation, and that enforcing the algebraic metric closure "
             "(sum dS = 0) and configuration arc-length evolution in the execution kernel makes energy drift and "
             "spurious entropy mathematically impossible. The post's image restates it as zero energy drift over "
             "curves drawn without data (read by eye). A reader replied that geometric and symplectic integrators "
             "were developed to preserve invariants over long integrations, and asked which class of systems the "
             "closure preserves exactly"),
      provenance="the 25 September post, its image, and the comment thread",
      citation_context=('"Any scheme relying on an external parametric time step (dt) inevitably violates '
                        'intrinsic conservation." (post); "by enforcing strict algebraic metric closure (sum dS = 0) '
                        'and configuration arc-length evolution directly at the execution kernel level, energy '
                        'drift and spurious entropy become mathematically impossible." (post); "Geometric and '
                        'symplectic integrators were developed precisely to preserve important invariants or the '
                        'underlying phase-space structure over long integrations." (comment); "which class of '
                        'dynamical systems does the algebraic metric closure preserve exactly" (comment)'),
      otherwise=low_grade("authors' claim", NOT_SHOWN)),
    A("posts", id="brighindi-post-separation-of-powers-runtime-gates",
      value=("In his earlier LinkedIn post \"The Unified Fallacy of Physical AI\", Brighindi proposes an architectural separation of powers "
             "for physical AI: probabilistic models (VLAs, neural operators) propose policies, and deterministic "
             "runtime gates (M_gate) evaluate passivity (P = F * v) and algebraic invariants on the control bus at "
             "kHz rates, failing closed before damage. He cites Northwestern's ManiGuard (23k+ rollouts) as "
             "showing 6-21% of successful robot tasks violate safety constraints, a third-party figure not checked "
             "here"),
      provenance="the 23 September post",
      citation_context=('"Probabilistic Models (VLAs, Neural Operators) propose exploratory policies and '
                        'heuristics." (post); "Deterministic Runtime Gates (M_gate) evaluate passivity (P = F * v) '
                        'and algebraic invariants on the control bus at kHz frequencies, failing closed before '
                        'damage occurs." (post); "Northwestern\'s ManiGuard (23k+ rollouts on pi0, GR00T) shows '
                        '6-21% of successful tasks violate safety constraints." (post)'),
      otherwise=low_grade("authors' claim", "a proposal with no implementation or measurement in the post")),
    A("stress", id="phi-infinity-stress-test-not-reproducible-and-no-immunity-inferred",
      value=("The author's own repository says the paper's stress test is a fixed-seed comparative "
             "simulation, not a physical observation and not a test of the repository's src/ engine; that the "
             "raw files and the original simulation.py are not published there, so the counts are not "
             "reproducible from the repository; that the rejections also record an availability limit (80 "
             "proposals not executed) and are not a solution of the task; and that no absolute immunity, "
             "physical performance or universal superiority is inferred from one seed and an ad hoc control (in "
             "Italian; translated here)"),
      provenance="docs/validation/ADVERSARIAL_STRESS_TEST_2026-09-25.md at 4ee4ea3",
      citation_context=('"simulazione comparativa a seed fissato, non osservazione fisica e non test del motore" '
                        '(Classe di evidenza); "non sono pubblicati in questo repository" (on the raw files and '
                        'simulation.py); "i conteggi non sono pertanto riproducibili da questo checkout" '
                        '(introduction); "registrano anche una limitazione di disponibilità (80 proposte non '
                        'eseguite)" (results); "I rifiuti non equivalgono a una soluzione del compito" (results); '
                        '"Non si inferiscono immunità assoluta, prestazioni fisiche o '
                        'superiorità universale da un singolo seed e da un controllo costruito ad hoc." (results)'),
      contradicts=["phi-omega-paper-claims-full-reproducibility",
                   "phi-omega-paper-claims-closure-makes-structural-failure-impossible"]),
    A("status", id="phi-infinity-runtime-calls-the-closure-a-hypothesis-and-the-test-no-general-proof",
      value=("The author's own runtime repository, in its research status note of 27 September, calls the closure "
             "(the sum of dS = 0) a formalization hypothesis whose variables and boundary must be declared in each "
             "test; calls the 25 September manuscript on runtime invariance and its comparison a result in the "
             "defined simulator, not a general physical proof, and the comparison not reproducible from the "
             "repository; and says the executable definition, derivation and proof of its proposed projection "
             "and threshold for extreme states remain open (in Italian; translated here). It is not linked "
             "`contradicts` to the paper's central claim: a result that holds only in its simulator can still be "
             "absolute there"),
      provenance="docs/M_OMNIA_STATO_RICERCA_2026-09-27.md at 4ee4ea3",
      citation_context=('"stato della ricerca al 27 settembre 2026" (title); "\\(\\sum dS=0\\)" (section C table); '
                        '"Ipotesi di formalizzazione; le variabili e il confine vanno dichiarati nel singolo test." '
                        '(section C table); "il confronto del 25 settembre" (section C table); "Manoscritto '
                        'sull\'invarianza runtime" (version table); "Risultato nel simulatore definito; non '
                        'dimostrazione fisica generale." (version table); "il risultato non è riproducibile da '
                        'esso" (Confini della prova); "definizione eseguibile, derivazione e prova restano aperte" '
                        '(section C table)')),
    A("stress", id="phi-infinity-stress-test-counts-20-commits-80-rejections",
      value=("By the author's repository's reading of the stress test's CSV (SEED = 20260925): 100 cycles; the open "
             "control first corrupted at step 16 with drift 177.08721760057597; the PHI-OMEGA simulator accepted "
             "20 transitions, rejected 80 as REJECT_NON_CONSERVATIVE and never halted (phi_halted = 1 in 0 "
             "cycles), ending with residual 20.696045734309212"),
      provenance="docs/validation/ADVERSARIAL_STRESS_TEST_2026-09-25.md at 4ee4ea3, results table",
      citation_context=('"riporta `SEED = 20260925`" (introduction); "Prima corruzione del controllo aperto | '
                        'Passo 16" (table); "Drift del controllo al passo '
                        '16 | 177.08721760057597" (table); "Transizioni accettate nel sistema PHI del simulatore | '
                        '20" (table); "Transizioni `REJECT_NON_CONSERVATIVE` | 80" (table); "Cicli con '
                        '`phi_halted=1` | 0" (table); "Residuo PHI finale del simulatore | 20.696045734309212" '
                        '(table); "Cicli registrati | 100" (table)'),
      evidence_tag="SIM",
      otherwise=low_grade("measured result",
                          "read from files the repository does not publish, so not re-run here")),
    A("omnia", id="m-omnia-validation-claims-no-empirically-verified-result",
      value=("The author's M-OMNIA validation repository is a preregistration that claims no empirically "
             "verified result; its theory note calls its central identity, coordinate time recovered from "
             "intrinsic arc length (dt = kappa * d_tau), a hypothesis until its definitions, calibration and "
             "unseen-regime predictions hold, and separates conceptual completeness, numerical agreement, "
             "reproducibility and empirical validity as distinct claims"),
      provenance="README.md and THEORY.md at d3e45f3",
      citation_context=('"no empirically verified result is claimed" (README); "dt = kappa * d_tau" (THEORY); "This '
                        'identity is a hypothesis until its operational definitions uniquely determine `d_tau`" '
                        '(THEORY); "Conceptual completeness, numerical agreement, reproducibility, and empirical '
                        'validity are separate claims." (THEORY)')),
]

# Assertions quoting more than one file: every quote is checked against the files named here.
SPLIT = {
    "m-omnia-validation-claims-no-empirically-verified-result": ("omnia", "theory"),
    "phi-omega-paper-control-corrupts-at-cycle-16": ("paper", "stress"),
    "phi-omega-paper-gives-no-proof-for-its-closure-claim": ("paper", "posts"),
}


def text_of(key: str) -> str:
    return source_text(str(TEXTS[key][0]))


def verify_all() -> list:
    """Every quote verbatim in its source, with the value's figures, BEFORE anything is written."""
    texts = {k: text_of(k) for k in TEXTS}
    out = []
    for key, a in ASSERTIONS:
        keys = SPLIT.get(a.id, (key,))
        out.append((key, a, require_verbatim(a.id, a.citation_context, " ".join(texts[k] for k in keys),
                                             value=a.value)))
    return out


def counts(conn) -> str:
    tiers = dict(conn.execute("SELECT tier, COUNT(*) FROM paper_fields GROUP BY tier").fetchall())
    n = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'assertion'").fetchone()[0]
    return f"papers {sum(tiers.values())} ({', '.join(f'{k} {v}' for k, v in sorted(tiers.items()))}); assertions {n}"


def correct_reads(conn, apply: bool) -> list[str]:
    """Replace each repository's first read row, matched on its exact detail; the old text is kept in the
    record's updated_reason. A row already corrected is left alone."""
    log = []
    for rid, (first, detail) in READ_CORRECTIONS.items():
        new = read_detail(rid, detail)
        rows = {r[0] for r in conn.execute("SELECT detail FROM paper_reads WHERE record_id = ? AND reader = 'Claude' "
                                           "AND read_on = ?", (rid, TODAY))}
        if first not in rows:
            continue
        if apply:
            if new in rows:
                conn.execute("DELETE FROM paper_reads WHERE record_id = ? AND reader = 'Claude' AND read_on = ? "
                             "AND detail = ?", (rid, TODAY, first))
            else:
                conn.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = 'Claude' "
                             "AND read_on = ? AND detail = ?", (new, rid, TODAY, first))
            conn.execute("UPDATE paper_fields SET checked_against_source = ? WHERE record_id = ?",
                         (f"{TODAY}, Claude, read {detail} at {COMMITS[rid]}", rid))
            append_updated_reason(conn, rid, f"{TODAY} ({TAG}): read row corrected after the fresh-eyes reviews "
                                             f"(INTAKE_WORKFLOW.md section 54); it said: \"{first}\"", TODAY)
        log.append(f"read {rid}: corrected")
    return log


def withdraw_links(conn, apply: bool) -> list[str]:
    log = []
    for from_id, to_id, relation, why in WITHDRAWN:
        if not conn.execute("SELECT 1 FROM assertion_relations WHERE from_assertion_id = ? AND to_assertion_id = ? "
                            "AND relation = ?", (from_id, to_id, relation)).fetchone():
            continue
        if apply:
            conn.execute("DELETE FROM assertion_relations WHERE from_assertion_id = ? AND to_assertion_id = ? "
                         "AND relation = ?", (from_id, to_id, relation))
            append_updated_reason(conn, from_id, f"{TODAY} ({TAG}): {why}", TODAY)
        log.append(f"unlink {from_id} -{relation}-> {to_id}")
    return log


def apply_changes(conn, apply: bool) -> list[str]:
    checked = verify_all()
    log = []
    for rid, entry in ENTRIES.items():
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (rid,)).fetchone():
            continue
        record = intake.build_record(entry(), today=TODAY)
        if apply:
            insert_paper(conn, record)
        log.append(f"source {record.id} [{record.tier}]")
    log += correct_reads(conn, apply)
    log += withdraw_links(conn, apply)
    for key, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            if apply:
                insert_verified_assertion(conn, a, verified, yielded_by=TEXTS[key][1])
            else:
                validate_assertion(a)
            log.append(f"assert {a.id} [{a.certainty}]")
        elif apply:
            changed = sync_verified_assertion(conn, a, verified, SYNC_REASON, TODAY)
            if changed:
                log.append(f"synced {a.id}: {', '.join(changed)}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F119 PHI-OMEGA paper, posts and code")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        before = counts(conn)
        log = apply_changes(conn, apply)
        if apply:
            conn.commit()
        after = counts(conn)
    finally:
        conn.close()
    print(f"before: {before}")
    print("\n".join(log) or "nothing to write")
    print(f"after:  {after}")
    print("APPLIED" if apply else "DRY RUN: nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
