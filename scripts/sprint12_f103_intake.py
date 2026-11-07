#!/usr/bin/env python3
"""Sprint 12 Task E (F103, the F95 release for Sprint 12): the Classiq
Quantum Circuit Challenge pages, the repository the team lead named, and
any PDF in `Papers\\` no record names. INTAKE_WORKFLOW.md section 44.

Three web source records under `qc`, entered as Sprint 11 entered the
NVIDIA blog: a hand citation from the page's own heading, author and date,
a local copy, `tier` `read`. Part 2's 19-page PDF is its second local
copy. Only each author's own measurements enter as assertions; Part 1's
survey of other work does not. The series (Part 1 of 2, Part 2 of 2) is
stated in each record, not linked: `cites` is computed from Crossref
reference lists only (ADR-0005 A10), and no other link type fits.

The repository the team lead named (wangy8205165/Quantum-NeuralNetwork-
WhitePaper) enters as a GitHub repository record, unlinked: no source
names it as a paper's code.

Every quote is checked by `require_verbatim`, with the value, against the
saved copy before anything is written, and written only through the
verified write path.

    python scripts/sprint12_f103_intake.py --fetch    # the three pages and Part 2's PDF; never overwrites
    python scripts/sprint12_f103_intake.py            # dry run
    python scripts/sprint12_f103_intake.py --apply    # verified backup first
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, append_updated_reason, insert_paper,  # noqa: E402
                          insert_verified_assertion, sync_verified_assertion, validate_assertion)
from store.quotes import require_verbatim, source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
TAG = "Sprint 12 Task E, F103"
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
REFERENCES = Path(r"D:\Data\Harold\EvidenceBasedDB\References")

PART1_URL = "https://nez0b.github.io/blog/2026/quantum-circuit-compilers-field-guide/"
PART2_URL = "https://nez0b.github.io/blog/2026/classiq-logo-phase-oracle-depth-95/"
PART2_PDF_URL = "https://nez0b.github.io/assets/pdf/classiq-depth95/logo-oracle-depth-95-explainer.pdf"
CLASSIQ_URL = "https://www.classiq.io/insights/wrapping-up-the-classiq-quantum-circuit-challenge"
PART1_COPY = REFERENCES / "2026-10_PoJen-Wang_A-field-guide-to-quantum-circuit-compilers.html"
PART2_COPY = REFERENCES / "2026-10_PoJen-Wang_A-depth-95-phase-oracle-for-the-Classiq-logo.html"
PART2_PDF = PAPERS / "2026-10_Wang_How-we-built-a-depth-95-phase-oracle-for.pdf"
CLASSIQ_COPY = REFERENCES / "2026-10_Classiq_Wrapping-up-the-Classiq-Quantum-Circuit-Challenge.html"
COPIES = ((PART1_URL, PART1_COPY), (PART2_URL, PART2_COPY), (PART2_PDF_URL, PART2_PDF), (CLASSIQ_URL, CLASSIQ_COPY))


REPO = "wangy8205165/Quantum-NeuralNetwork-WhitePaper"
FOUND_VIA = ("the team lead, 2026-10-23, Sprint 12 Phase 1.4: \"add this to the papers/repo for this sprint ... "
             "determine how best to include\", then \"include with the above\" for Part 1")
REPO_FOUND_VIA = "the team lead, 2026-10-22: named for the next F95 release (master plan, F95 card)"
REASON = f"{TODAY} ({TAG}): extracted from the saved copy, read in full on {TODAY}"
SYNC_REASON = (f"{TODAY} ({TAG}): corrected against the saved page (fresh-eyes reviews of c80c195 and 77beaa0; "
               "INTAKE_WORKFLOW.md section 44, third and fourth applies)")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# key -> the source record's entry, less what entries() fills in
SOURCES = {
    "part1": {
        "id": "wang-2026-field-guide-quantum-circuit-compilers-blog",
        "title": "A field guide to quantum circuit compilers",
        "citation": (f"Wang, P., \"A field guide to quantum circuit compilers,\" blog post, Quantum circuit "
                     f"optimization, Part 1 of 2, 2026-10-08, {PART1_URL} (hand-transcribed from the saved page's "
                     "title, author tag and \"Last updated\" line)"),
        "transcribed_from": "the page's <title>, its author meta tag and its \"Last updated: October 08, 2026\" line",
        "copies": (PART1_COPY,), "url": PART1_URL,
        "disposition": ("Reference: PoJen Wang's field guide to what quantum compilers do, with his own run of three "
                        "tools on the Classiq challenge's baseline circuit (six versions of the circuit); Part 1 of "
                        "2, the second "
                        "being wang-2026-depth-95-phase-oracle-classiq-logo-blog. Its survey of other work is "
                        "second-hand and not entered as its claims"),
        "applicability": [["qc", "what quantum circuit compilers do, and the author's own run of compiler versions "
                                 "on the challenge's baseline circuit -- read in full"]],
    },
    "part2": {
        "id": "wang-2026-depth-95-phase-oracle-classiq-logo-blog",
        "title": "A depth-95 phase oracle for the Classiq logo",
        "citation": (f"Wang, P., \"A depth-95 phase oracle for the Classiq logo,\" blog post, Quantum circuit "
                     f"optimization, Part 2 of 2, 2026-10-08, {PART2_URL}; with the write-up \"How we built a "
                     f"depth-95 phase oracle for the Classiq logo\" (PDF, 19 pages), {PART2_PDF_URL} "
                     "(hand-transcribed from the page's title, author tag and \"Last updated\" line, and the PDF's "
                     "title and author)"),
        "transcribed_from": ("the page's <title>, its author meta tag and its \"Last updated: October 08, 2026\" "
                             "line; the PDF's title and author fields"),
        "copies": (PART2_COPY, PART2_PDF), "url": PART2_URL,
        "disposition": ("Reference: PoJen Wang's own account of his Classiq Quantum Circuit Challenge entry, a "
                        "phase oracle of depth 95 and 272 CNOTs; Part 2 of 2, the first being "
                        "wang-2026-field-guide-quantum-circuit-compilers-blog. The page says it \"finished in the "
                        "top five\"; Classiq's wrap-up places it first"),
        "applicability": [["qc", "a hand-built phase oracle's depth and CNOT count, and where its reduction came "
                                 "from -- read in full"]],
    },
    "classiq": {
        "id": "gramolin-2026-wrapping-up-classiq-quantum-circuit-challenge",
        "title": "Wrapping up the Classiq Quantum Circuit Challenge",
        "citation": (f"Gramolin, A., \"Wrapping up the Classiq Quantum Circuit Challenge,\" Classiq Insights, "
                     f"2026-10-06, {CLASSIQ_URL} (hand-transcribed from the saved page's heading, byline and "
                     "\"Date 06 Oct 2026\"; a second date, 9 October 2026, also appears on the page)"),
        "transcribed_from": "the page's heading, its byline and its \"Date 06 Oct 2026\" line",
        "copies": (CLASSIQ_COPY,), "url": CLASSIQ_URL,
        "disposition": ("Reference: the organiser's account of its Quantum Circuit Challenge (participation, "
                        "scoring rules, the five winners and their methods)"),
        "applicability": [["qc", "a circuit-optimization challenge's rules, participation and placings, as its "
                                 "organiser reports them -- read in full"]],
    },
}


def entries() -> list[tuple[str, dict]]:
    out = []
    for key, s in SOURCES.items():
        hashes = "; ".join(f"Local copy {p.name}, SHA-256 {sha(p)}, saved {TODAY}" for p in s["copies"])
        extra = (". The page names its circuit file (logo-oracle-95-272.qasm) and a companion notebook bundle "
                 "(zip); neither is copied" if key == "part2" else "")
        out.append((key, {
            "id": s["id"], "kind": "reference", "context": "qc", "tier": "read", "title": s["title"],
            "citation": s["citation"], "transcribed_from": s["transcribed_from"],
            "access": " | ".join([*(str(p) for p in s["copies"]), s["url"]]),
            "disposition": s["disposition"], "evidence": hashes + extra, "applicability": s["applicability"],
            "found_via": FOUND_VIA, "cited_as": s["url"],
            "checked_against_source": f"{TODAY}, Claude, read the whole saved page",
            "reads": [["Claude", TODAY, "full", "the whole saved page"]],
            "updated_reason": f"{TODAY}: added by scripts/sprint12_f103_intake.py ({TAG}); read in full",
        }))
    return out


def repo_entry() -> dict:
    return {"access": f"https://github.com/{REPO}", "kind": "repo", "context": "qml",
            # Sprint 16 Task G (F57, 2026-11-06): the white paper is now entered and linked, so "linked to no paper"
            # no longer held. This script owns the disposition; scripts/sprint16_f57_named.py reads it from here.
            "disposition": ("Repository named by the team lead for the F95 release (2026-10-22). It holds no code: "
                            "its files (listed 2026-10-23) are the LaTeX source and PDF of a white paper, \"Quantum "
                            "Neural Networks: Theory, Architectures, and Applications\", entered as "
                            "wangy8205165-2026-quantum-neural-networks-theory-architectures and linked code-of "
                            "(Sprint 16 Task G, 2026-11-06)"),
            "found_via": REPO_FOUND_VIA, "cited_as": f"github.com/{REPO}"}


def A(key: str, **kw) -> tuple[str, AssertionRecord]:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", REASON)
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", "qc")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "positive")
    kw["provenance"] = f"{SOURCES[key]['id']}, {kw['provenance']}"
    return key, AssertionRecord(**kw)


# The store's GRADE mapping (sprint10_f89_reading.py, sprint11_reading.py): an empirical result from one
# study, or an author's own claim, starts LOW (fresh-eyes review of c80c195: these started MODERATE).
OWN_BLOG = ("Started LOW: the author's own measurement in his own blog post, one study, not peer reviewed, and not "
            "re-run here")
ORGANISER = ("Started MODERATE: the organiser's own account of its own competition. Not upgraded: its counts are "
             "not checkable from outside")

ASSERTIONS: list[tuple[str, AssertionRecord]] = [
    A("part1", id="wang-2026-compiler-winner-depends-on-cost-classiq-baseline",
      value=("Running Qiskit 2.5.2 (level 3), pytket 2.18.1 and PyZX 0.10.6 on his own reproduction of the "
             "Classiq challenge's 18-qubit baseline circuit (depth 5329, 3502 CNOTs; it scores the same), PoJen "
             "Wang found that which tool wins depends on the cost: Qiskit at level 3, and tket followed by Qiskit, "
             "lowered depth by about 6 percent "
             "and the CNOT count by about 4 percent, while PyZX cut the T-count, as PyZX counts T gates, from 4247 "
             "to about 3160 with either of two methods and its full_reduce raised the CNOTs to 8576. He notes that "
             "merging one-qubit gates accounts for much of the T-count drop of the first rows of his chart, and that a fault-tolerant compiler "
             "would need more T gates than PyZX counts. He judges the tket result the one to run on today's noisy "
             "hardware, and a redesign of the same oracle was 56 times shorter than the baseline"),
      provenance="the cost-models section and its figure caption, and the introduction",
      citation_context=('"I ran three tools on the baseline circuit from Part 2, an 18-qubit circuit with depth 5329 '
                        'and 3502 CNOT gates (CX in the figures)." (What counts as better); "Which tool wins depends '
                        'on the cost." (figure caption); "Qiskit and tket lower depth by about 6 percent and the CNOT '
                        'count by about 4." (figure caption); "Versions: Qiskit 2.5.2, pytket 2.18.1, PyZX 0.10.6." '
                        '(figure caption); "Qiskit at level 3 and tket followed by Qiskit improve depth and CNOT '
                        'count a little." (What counts as better); "cuts the T-count from 4247 to about 3160 with '
                        'either of two methods, and one of them, full_reduce, pays for it with 8576 CNOTs instead of '
                        '3502." (What counts as better); "For today\'s noisy hardware the tket result is the one to '
                        'run." (What counts as better); "When I ran the best off-the-shelf compilers on the '
                        'challenge\'s baseline circuit, they made it about 6 percent shorter, while a redesign of '
                        'the same oracle was 56 times shorter." (introduction); "I used my own reproduction of it, '
                        'which scores the same" (What counts as better); "Merging neighbouring one-qubit gates, which '
                        'every tool does, accounts for much of the T-count drop of the first rows." (What counts as '
                        'better); "PyZX counts every phase that is not a multiple of" (What counts as better); '
                        '"every circuit here would need more T gates than the chart shows." (What counts as '
                        'better)'),
      certainty="low", certainty_reasons=OWN_BLOG + ". Scope: one circuit, three tools, all-to-all connectivity"),
    A("part2", id="wang-2026-classiq-logo-oracle-depth-95-272-cnots",
      value=("PoJen Wang's entry to the Classiq Quantum Circuit Challenge is a phase oracle on 18 qubits with "
             "depth 95 and 272 CNOTs, against the organisers' baseline of depth 5329 and 3502 CNOTs, a 56-fold "
             "drop in depth. He writes that it finished in the top five (the placing is the organiser's: "
             "gramolin-2026-classiq-challenge-five-winners-and-placings). The circuit is published as an OpenQASM "
             "2 file with the post"),
      provenance="the opening, the challenge section and Reproduce it",
      citation_context=('"The organisers\' baseline circuit has depth 5329. My entry has depth 95 with 272 CNOTs, and '
                        'it finished in the top five." (opening); "That makes 18 qubits in all" (The challenge); '
                        '"I did that on my own reproduction of the baseline, which scores the same 5329 and 3502." '
                        '(Why not just run a compiler); "Of the 56-fold drop from 5329 to 95" (The code design does '
                        'the work, not the compiler); "the final circuit, OpenQASM 2 with u3 and cx gates on 18 '
                        'qubits (depth 95, 272 cx" (Reproduce it)'),
      certainty="moderate",
      certainty_reasons=(OWN_BLOG + ". UPGRADED one level: the organiser scored the same circuit independently, "
                         "and its wrap-up gives the same depth 95 and 272 CX "
                         "(gramolin-2026-classiq-challenge-top-two-cx-counts); not linked, ADR-0004 A8 (b)")),
    A("part2", id="wang-2026-depth-95-came-from-redesign-not-compilers",
      value=("On the Classiq logo oracle, off-the-shelf compilers shortened the baseline (depth 5329) by about 6 "
             "percent (tket then Qiskit: depth 5004 with 3347 CNOTs; Qiskit level 3: 5021 and 3355) and Wang's "
             "gate-reordering rescheduler by 12.5 percent (4665), while PyZX's full_reduce lengthened it, to depth "
             "8950 with 8576 CNOTs, more than twice the CNOTs. A generic "
             "truth-table encoding reached 1886, logic networks shaped by hand 468 then 345, his row and column "
             "codes with a search over them 107, and gate-level polishing 95. By his account, gate-level tools "
             "gave a few percent at the start and the last 12 layers; the rest came from changing what the "
             "circuit computes"),
      provenance="Why not just run a compiler, and The code design does the work, not the compiler",
      citation_context=('"Qiskit, optimization level 3 5021 3355 tket\'s FullPeepholeOptimise, then Qiskit 5004 3347 '
                        'PyZX\'s full_reduce, then extraction 8950 8576 my rescheduler, which only reorders gates '
                        '4665 3502" (Why not just run a compiler, the table); "The off-the-shelf tools shorten the '
                        'baseline by about 6 percent, and my own rescheduler by 12.5 percent." (Why not just run a '
                        'compiler); "returned a correct circuit with more than twice the CNOTs." (Why not just run a '
                        'compiler, on PyZX); "the pixel function\'s truth table written as an XOR of products 1886" (The code '
                        'design does the work, the ladder); "logic networks shaped to the logo by hand 468, then '
                        '345" (the ladder); "the row and column codes of this post, then a search over the codes '
                        '107" (the ladder); "gate-level polishing of that circuit 95" (the ladder); "Of the 56-fold '
                        'drop from 5329 to 95, gate-level tools account for a few percent at the start and the last '
                        '12 layers at the end. Everything in between came from changing what the circuit computes." '
                        '(The code design does the work, not the compiler)'),
      certainty="low",
      certainty_reasons=OWN_BLOG + ". The attribution of the drop is the author's reading of his own path"),
    A("classiq", id="classiq-2026-quantum-circuit-challenge-rules-and-participation",
      value=("The Classiq Quantum Circuit Challenge (August 28 to September 30) asked for a phase oracle marking a "
             "rasterized 64x64 Classiq logo, scored by circuit depth in the U3/CX basis with all-to-all "
             "connectivity and at most 18 qubits (12 coordinate qubits and at most six ancillas), CX count "
             "breaking ties; the organiser's unoptimized baseline had depth 5,329 and 3,502 CX. Classiq reports "
             "387 registered participants from 40 countries, 6,091 unique circuits, 101 participants with a valid "
             "solution, 25 below depth 200 (which it had not expected) and two at depth 95"),
      provenance="the opening, The challenge and its metrics, and An international community of participants",
      citation_context=('"The task was to encode a rasterized 64×64 version of the Classiq logo as a quantum phase '
                        'oracle." (The challenge and its metrics); "The primary score was circuit depth in the U3/CX '
                        'gate basis" (The challenge and its metrics); "all-to-all connectivity was assumed" (The '
                        'challenge and its metrics); "CX count broke ties, and the width limit was 18 qubits: 12 '
                        'coordinate qubits and at most six ancillas." (The challenge and its metrics); "Our '
                        'intentionally simple, unoptimized baseline had depth 5,329 and 3,502 CX gates" (The '
                        'challenge and its metrics); "The challenge ran from August 28 to September 30 and attracted '
                        '387 registered participants from 40 countries." (participants); "Participants synthesized '
                        '6,091 unique circuits, and 101 people submitted valid solutions." (participants); "After '
                        'internal benchmarking, we did not expect submissions with depth below 200. In the end, 25 '
                        'participants submitted circuits below that threshold, and two reached a depth of 95." '
                        '(opening)'),
      certainty="moderate", certainty_reasons=ORGANISER),
    A("classiq", id="gramolin-2026-classiq-challenge-five-winners-and-placings",
      value=("Classiq names five winners of its Quantum Circuit Challenge, each receiving a $2,000 prize: first "
             "PoJen Wang (USA), second Daksh Shami (USA), third Jayachandiran U (India), fourth Andrei Diaconu "
             "(Romania) and fifth Sourabh Nirvani (India)"),
      provenance="The five winning solutions",
      citation_context=('"Congratulations to PoJen Wang, Daksh Shami, Jayachandiran U, Andrei Diaconu, and Sourabh '
                        'Nirvani on their outstanding results! Each will receive a $2,000 prize from Classiq." (The '
                        'five winning solutions); "First place (PoJen Wang, USA)" (The five winning solutions); '
                        '"Second place (Daksh Shami, USA)" (The five winning solutions); "Third place '
                        '(Jayachandiran U, India)" (The five winning solutions); "Fourth place (Andrei Diaconu, '
                        'Romania)" (The five winning solutions); "Fifth place (Sourabh Nirvani, India)" (The five '
                        'winning solutions)'),
      certainty="high",
      certainty_reasons=("Started HIGH: the placings are the organiser's to decide, so its page is their primary "
                         "record. Its counts are a separate assertion at the organiser's grade "
                         "(gramolin-2026-classiq-challenge-top-two-cx-counts)")),
    A("classiq", id="gramolin-2026-classiq-challenge-top-two-cx-counts",
      value=("Classiq reports the two best circuits of its Quantum Circuit Challenge at the same depth, 95: PoJen "
             "Wang's with 272 CX gates, the lowest CX count on the leaderboard, and Daksh Shami's with 410. It puts "
             "that depth at about a 56-fold reduction from its deliberately unoptimized baseline"),
      provenance="The five winning solutions, and An international community of participants",
      citation_context=('"His final circuit achieves depth 95 with 272 CX gates, the lowest CX count on the '
                        'leaderboard." (First place); "The circuit matches the first-place depth of 95 with 410 CX '
                        'gates." (Second place); "the best depth of 95 represents approximately a 56-fold reduction '
                        'in depth relative to our deliberately unoptimized baseline" (participants)'),
      certainty="moderate",
      certainty_reasons=("Started MODERATE: the organiser's own account of its own competition. Not upgraded: "
                         "the winner's depth and CX count agree with the entrant's own account "
                         "(wang-2026-classiq-logo-oracle-depth-95-272-cnots), but the entrant is an interested "
                         "party, not an independent check, and the published circuit was not re-run here; not "
                         "linked, ADR-0004 A8 (b)")),
]


def unnamed_pdfs(conn) -> list[str]:
    """PDFs in Papers\\ that no record's access names (the release's step 1)."""
    held = " ".join(a or "" for (a,) in conn.execute("SELECT access FROM paper_fields")).lower()
    return sorted(p.name for p in PAPERS.glob("*.pdf") if p.name.lower() not in held)


def counts(conn) -> str:
    tiers = dict(conn.execute("SELECT tier, COUNT(*) FROM paper_fields GROUP BY tier").fetchall())
    n = conn.execute("SELECT COUNT(*) FROM records WHERE class = 'assertion'").fetchone()[0]
    return f"papers {sum(tiers.values())} ({', '.join(f'{k} {v}' for k, v in sorted(tiers.items()))}); assertions {n}"


def text_of(key: str) -> str:
    """The quoted page's text: the saved HTML copy (Part 2's PDF is its second copy, not quoted)."""
    return source_text(str(SOURCES[key]["copies"][0]))


def verify_all() -> list:
    """Every quote verbatim in its saved page, with the value's figures, BEFORE anything is written."""
    texts = {k: text_of(k) for k in SOURCES}
    return [(k, a, require_verbatim(a.id, a.citation_context, texts[k], value=a.value)) for k, a in ASSERTIONS]


def sync_disposition(conn, rid: str, disposition: str, apply: bool, log: list[str]) -> None:
    """A held record's disposition made the script's (fresh-eyes review of c80c195)."""
    if conn.execute("SELECT disposition FROM paper_fields WHERE record_id = ?", (rid,)).fetchone()[0] != disposition:
        if apply:
            conn.execute("UPDATE paper_fields SET disposition = ? WHERE record_id = ?", (disposition, rid))
            append_updated_reason(conn, rid, f"{SYNC_REASON}: disposition", TODAY)
        log.append(f"synced {rid}: disposition")


def apply_changes(conn, apply: bool) -> list[str]:
    checked = verify_all()
    log = [f"before: {counts(conn)}"]
    for key, entry in entries():
        record = intake.build_record(entry, today=TODAY)
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (record.id,)).fetchone():
            log.append(f"exists {record.id}")
            sync_disposition(conn, record.id, entry["disposition"], apply, log)
            # The first apply entered these at `read` with no applicability, which every read paper
            # carries (test_paper_applicability, found by the full suite before the commit).
            if not conn.execute("SELECT 1 FROM paper_applicability WHERE record_id = ?", (record.id,)).fetchone():
                if apply:
                    for ctx, rationale in entry["applicability"]:
                        conn.execute("INSERT INTO paper_applicability (record_id, context_id, rationale) "
                                     "VALUES (?, ?, ?)", (record.id, ctx, rationale))
                    append_updated_reason(conn, record.id, f"{TODAY} ({TAG}): applicability added", TODAY)
                log.append(f"applic {record.id}")
        else:
            if apply:
                insert_paper(conn, record)
            log.append(f"paper  {record.id} [{record.tier}]")
    held = conn.execute("SELECT record_id FROM paper_fields WHERE lower(access) LIKE ?",
                        (f"%github.com/{REPO.lower()}%",)).fetchone()
    if held:
        log.append(f"exists {held[0]}")
        sync_disposition(conn, held[0], repo_entry()["disposition"], apply, log)
    else:
        record = intake.build_record(repo_entry(), today=TODAY)  # one GitHub REST call
        if apply:
            insert_paper(conn, record)
        log.append(f"repo   {record.id}  ({record.value[:60]})")
    for key, a, verified in checked:
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
            if apply:
                insert_verified_assertion(conn, a, verified, yielded_by=SOURCES[key]["id"])
            else:
                validate_assertion(a)
            log.append(f"assert {a.id} [{a.certainty}]")
        elif apply:
            changed = sync_verified_assertion(conn, a, verified, SYNC_REASON, TODAY)
            log.append(f"synced {a.id}: {', '.join(changed)}" if changed else f"exists {a.id}")
    log += [f"unnamed PDF in Papers: {name}" for name in unnamed_pdfs(conn)]
    if apply:
        log.append(f"after:  {counts(conn)}")
    return log


def fetch() -> int:
    for url, path in COPIES:
        if path.exists():
            print(f"exists  {path.name}")
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EvidenceBasedDB)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if path.suffix == ".pdf" and not data.startswith(b"%PDF"):
            raise RuntimeError(f"not a PDF: {url}")
        path.write_bytes(data)
        print(f"saved   {path.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        return fetch()
    missing = [str(p) for _, p in COPIES if not p.exists()]
    if missing:
        print("missing local copies (run --fetch):\n" + "\n".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F103 Classiq challenge pages and the named repository")
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
