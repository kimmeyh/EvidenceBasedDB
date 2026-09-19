#!/usr/bin/env python3
"""Render the F11 adjudication packet for the team lead (Sprint 4 Task E).

F11 is the number ADR-0004 says the whole design is constrained by:
minutes of team-lead adjudication per accepted record. The packet gives
the team lead the SAME primary-source access the F10 protocol used (the
local PDF or the arXiv/DOI page), the record as corrected by Task C, and
F10's own source-verified findings for that record, so the timing
measures adjudication and not the re-finding of defects F10 already
found (SPRINT_3_RETROSPECTIVE.md improvement 4; F11 card in the master
plan).

The packet is GENERATED from the store -- determinate facts are computed,
never stored (CLAUDE.md) -- and committed under docs/sprints/ so the
timing run is reproducible against the exact records it saw. Re-run
after any record change and commit the diff.

Usage:
    python scripts/render_f11_packet.py            # writes docs/sprints/SPRINT_4_F11_ADJUDICATION_PACKET.md
    python scripts/render_f11_packet.py --stdout   # print instead
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
OUT_PATH = ROOT / "docs" / "sprints" / "SPRINT_4_F11_ADJUDICATION_PACKET.md"
GENERATED_ON = "2026-09-19"

# F10's source-verified findings per record, from
# docs/sprints/SPRINT_3_F7-F10_REVIEW_RESULTS.md (F10 section) and the
# master plan's F25 Part A1. Each is what Task C acted on; the team lead
# is timing whether the CORRECTED record now holds, not re-finding these.
F10_FINDINGS = {
    "dupont-2023-quantum-enhanced-greedy-solver":
        "Title was wrong ('Quantum Enhanced Greedy Solver for Optimization Problems'); pinned v1 though v2 exists and the paper was published in Science Advances. Corrected by API re-derivation in Task C.",
    "kordzanganeh-2022-benchmarking-simulated-physical-qpu":
        "Third author (Basil Kyriacou) missing; pinned v1; published in Advanced Quantum Technologies; disposition said 'seen tier' beside a tier column saying screened; 'workload is QNNs' rationale stated without evidence. Citation and disposition corrected in Task C; the rationale is Task F's.",
    "rand-2022-pqc-critical-infrastructure-assessment":
        "Citation carried no year and the id said 2023; the report's p.ii says 2022. Access was the bare words 'local file'. Renamed rand-2022 and switched to the registered DOI 10.7249/RRA1367-6 in Task C (Crossref names no contributors; the cover names Vermeer, Parker, Kochhar). 'world' claimed on a policy report -- Task F's.",
    "mancilla-2026-fourier-wall-spectra":
        "Claimed two seed files were 'identically-content'; hashing showed they differ. Note moved to updated_reason with the sha256 measurement in Task C.",
    "emami-2025-financial-fraud-entropy-computing-qci":
        "Preprint superseded by a Springer proceedings chapter the record did not mention; 'all six authors are QCi employees' is correct on the byline but Chancellor holds a concurrent Durham affiliation. Task H's extraction records the latter as evidence.",
    "lubinski-2023-application-oriented-benchmarks-qedc":
        "Preprint superseded by IEEE TQE (DOI 10.1109/TQE.2023.3253761); v3 date is 2023-01-10 not -11; duplicate-file note lived inside the citation (moved; the two files are byte-identical). Rationale 'gate-based hardware: IonQ, Quantinuum' omits that D-Wave is on the author list -- Task F's.",
    "mandra-2021-hybridq-simulator-nasa":
        "Preprint superseded by IEEE/ACM QCS 2021 (DOI 10.1109/QCS54837.2021.00015), now carried by the API-derived citation.",
    "wang-2025-quantum-optimization-nn-compression":
        "v2 exists ('submitted to Elsevier'); rationale 'uses quantum annealing hardware directly' is true but incomplete in the wrong direction: the D-Wave Advantage ran only the two smallest models, the larger ones ran on a classical Fujitsu Digital Annealer -- Task F's.",
    "pelofske-2022-quantum-volume-nisq-ieee":
        "Complete on DOI but omitted volume/pages and the LANL affiliation; API-derived citation now carries IEEE TQE volume 3, pages 1-19.",
    "rehman-2026-qstar-adaptive-routing":
        "NYU Abu Dhabi affiliation asserted but not verifiable from the arXiv page (dropped from the API-derived citation); rationale describes an asymmetric confidence-thresholded fallback as symmetric routing -- Task F's.",
    "zajac-2026-inverse-born-rule-equivalence":
        "Title punctuation differed from arXiv (corrected by API); the one mathematical theorem in the set, which 'world' (mathematics/physics ground truth) fits and which got nothing -- Task F's.",
    "qci-2024-profiling-cvqboost":
        "Formatted like a peer-reviewed citation while having no authors, venue or DOI, and did not say so; access was the bare words 'local file'. Citation now states the absence explicitly; access is the real path. Its 'covers performance' rationale was the weakest of the CVQBoost cluster (F9 and F10 independently) -- Task F's.",
    "loke-2026-cvqboosting-fraud-detection-smu":
        "A 700-character correction narrative lived inside the citation (moved to updated_reason); access was the bare words 'local file' (now the real path plus the SMU collection URL). Rationales already named their anchors (p.1 keywords) -- the model Task F applies elsewhere.",
    "arute-2019-quantum-supremacy-google-nature":
        "'world' claimed on a contested empirical claim under a 'platform-independent' test that ADR-0004's own definition (mathematics/physics ground truth) does not support; disposition carried 'LANDMARK' and 'near-certain read-tier candidate' (tier words removed in Task C) -- context is Task F's.",
    "britt-humble-2017-hpc-with-qpus-acm":
        "Vendor-neutral HPC architecture paper that did NOT get 'world' while arute and rand did (F9's inconsistency); 'method' worth considering; 'tight/loose taxonomy' rationale incomplete -- Task F's.",
    "huynh-2023-quantum-inspired-ml-survey":
        "Says its subject is 'distinct from QML proper' twice and files under qml alone while 'ml' has zero users across all 46 papers -- Task F's.",
    "neven-2012-qboost-adiabatic-quantum-optimization":
        "Keeps a generic 'qc' beside its specific context while Dirac-3 papers drop it (the unstated qc-subsumption rule); 'ml' for the boosting formulation -- Task F's. Also: QCi cites 'Neven et al. 2009' while the store holds the 2012 paper; Task H confirms which one CVQBoost's lineage rests on.",
    "tung-2026-qmes-quantum-meta-learning-kernel-encoding":
        "'method' candidate (meta-learned encoding selection is an evaluation-methodology contribution) -- Task F's. No citation defect found.",
}


def _source_link(access: str) -> str:
    parsed = citations.parse_access(access)
    if parsed and parsed[0] == "arxiv":
        return f"https://arxiv.org/abs/{parsed[1]}"
    if parsed and parsed[0] == "doi":
        return f"https://doi.org/{parsed[1]}"
    return access  # a local path, optionally "| url"


def render(conn) -> str:
    screened = conn.execute(
        "SELECT r.id, r.value, r.provenance, r.updated, r.updated_reason, p.tier, p.access, p.disposition, p.evidence "
        "FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE p.tier = 'screened' ORDER BY r.id"
    ).fetchall()
    # The timed set is the 18 records F10 reviewed (the comparison is
    # apples to apples); screened records added since are listed apart.
    rows = [r for r in screened if r["id"] in F10_FINDINGS]
    added_since = [r for r in screened if r["id"] not in F10_FINDINGS]
    out: list[str] = []
    w = out.append
    w("# Sprint 4 Task E: F11 Adjudication Packet for the Team Lead")
    w("")
    w(f"Generated {GENERATED_ON} by `scripts/render_f11_packet.py` from the store as corrected by")
    w("Sprint 4 Task C. **Generated, never hand-edited**; re-run the script after any record change.")
    w("")
    w("## What this measures, and how to run it")
    w("")
    w("ADR-0004 names one number the whole design is constrained by: **minutes of")
    w("team-lead adjudication per accepted record**. Sprint 3's F7-F10 measured four")
    w("model reviewers on these same 18 records (F10, the primary-source protocol:")
    w("599 s and 150,290 tokens for the set, 93 field calls). F11 measures the team")
    w("lead on the same records, corrected, with the same primary-source access.")
    w("")
    w("**Protocol (the F10 protocol; record per record whether you followed it in full):**")
    w("")
    w("1. Start the clock. Open the source via the link in *Access* (arXiv/DOI page or the local PDF).")
    w("2. Citation: ACCEPT / REVISE / REJECT the authors, title, venue or arXiv version, DOI, date against the source.")
    w("3. Disposition: is it one line, true, and why the record was worth keeping?")
    w("4. Each applicability row: is the context right, and does the rationale say where it was read from?")
    w("5. Tier: does `screened` (dispositioned and applicability-derived, not yet mined; ADR-0005 A2) hold?")
    w("6. Stop the clock. Fill the row in the timing sheet: minutes, protocol followed (full / partial: which steps), calls.")
    w("")
    w("F10's findings are printed under each record so the run measures adjudication,")
    w("not re-discovery. Items marked *Task F's* are applicability corrections still")
    w("pending in this sprint; adjudicate them as you find them and say so.")
    w("")
    w("When done, hand the timing sheet back (edited in place or pasted). Claude records")
    w("the minutes-per-record number and the protocol in `.claude/model_assignment_heuristics.json`")
    w("(`learning_log`, the pending Sprint 4 row) and in the Sprint 4 summary.")
    w("")
    w(f"## The {len(rows)} `screened` records F10 reviewed (snapshot as of {GENERATED_ON})")
    w("")
    if added_since:
        w("Screened records added since F10 ran, **not part of the timed comparison** (adjudicate")
        w("them afterwards if you wish; they went through the Task B door, so they are also a")
        w("test of the door): " + ", ".join(f"`{r['id']}`" for r in added_since) + ".")
        w("")
    for i, r in enumerate(rows, 1):
        contexts = [c[0] for c in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ? ORDER BY context_id", (r["id"],))]
        app = conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ? ORDER BY context_id", (r["id"],)).fetchall()
        w(f"### {i}. `{r['id']}`")
        w("")
        w(f"- **Title**: {r['value']}")
        w(f"- **Citation**: {r['provenance']}")
        w(f"- **Access**: {_source_link(r['access'])}")
        w(f"- **Tier**: {r['tier']}; **primary context**: {', '.join(contexts)}")
        w(f"- **Disposition**: {r['disposition']}")
        if app:
            w("- **Applicability**:")
            for a in app:
                w(f"  - `{a['context_id']}`: {a['rationale']}")
        else:
            w("- **Applicability**: none recorded")
        if r["evidence"]:
            w(f"- **Evidence**: {r['evidence']}")
        w(f"- **Last change** ({r['updated']}): {r['updated_reason']}")
        w(f"- **F10 found**: {F10_FINDINGS.get(r['id'], 'no per-record finding named in the results document; per-field calls are in the F10 review transcript.')}")
        w("")
    w("## Timing sheet")
    w("")
    w("Fill one row per record. *Protocol* is `full` (all six steps with the source open) or")
    w("`partial: <steps skipped>`. *Calls* is your ACCEPT/REVISE/REJECT per field, or one word for the record.")
    w("")
    w("| # | Record | Start | End | Minutes | Protocol | Calls | Notes |")
    w("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        w(f"| {i} | `{r['id']}` |  |  |  |  |  |  |")
    w("")
    w("**Totals**: records adjudicated ____ ; total minutes ____ ; minutes per record ____ ;")
    w("records where the corrected citation still needed a REVISE ____ .")
    w("")
    w("## Comparison row (filled by Claude from the sheet)")
    w("")
    w("| Reviewer | Protocol | Records | Time | Findings |")
    w("|---|---|---|---|---|")
    w("| F7 Haiku | per-record-internal-consistency | 18 | 182 s | 18/18 confirm |")
    w("| F8 Sonnet | per-record-with-certainty-check | 18 | 155 s | 18/18 confirm; certainty step n/a |")
    w("| F9 Opus | set-level-cross-record | 18 | 208 s | 7 cross-record inconsistencies |")
    w("| F10 Fable-tier | full-adjudication-primary-source | 18 | 599 s | 38 accept / 43 revise / 12 reject; 4 citation defects |")
    w("| **Team lead** | team-lead-adjudication (this packet) | 18 | ____ | ____ |")
    w("")
    w("Source for the four model rows: `.claude/model_assignment_heuristics.json` learning_log[0].")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1
    conn = connect(DB_PATH)
    try:
        text = render(conn)
    finally:
        conn.close()
    if "--stdout" in args:
        sys.stdout.write(text)
        return 0
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_PATH} ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
