#!/usr/bin/env python3
"""Sprint 7 Task F (F44): the eight pending Cycorp papers, and T07's two
assertions. `docs/INTAKE_WORKFLOW.md` section 18 records the decisions.

The PDFs were downloaded on 2026-10-08 with the team lead's approval of
2026-10-06 ("each download is approved"): seven from cdn.aaai.org, cyc.com
and cogsci.northwestern.edu, and S16 from arxiv.org (one request at 09:56,
seven minutes after Task C's bulk run sent its last). They sit in
`Papers\\` under section 3's naming convention. This script reads them
there and refuses to write if a file's SHA-256 differs from the one
measured at download.

ARXIV: one request (the door's paced fetcher) for S16's metadata, inside
F52's cap. S19 and L10 resolve on Crossref. DRY-RUN BY DEFAULT; `--apply`
takes a verified backup first. Idempotent: an existing record, link or
note is skipped.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (  # noqa: E402
    AssertionRecord, add_read, append_updated_reason, insert_assertion, insert_paper, set_tier,
)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
TAG = "Sprint 7 Task F, F44"
ROUTE = "2026-10 Cyc handoff (04-pending-sources.md)"
DOWNLOADED = "2026-10-08"
T07 = "taylor-2007-guiding-inference-policy-search-reinforcement"

# key: (file, sha256, bytes, url, how the handoff cited it, entry fields)
PAPERS_IN = {
    "T07": ("2007-03_Taylor_Guiding-Inference-with-Policy-Search-Reinforcement-Learning.pdf",
            "329ea861cbb7857378a2ad79ac107c6c28407cfdf30e0a44859ec861fd80794b", 115054,
            "https://cdn.aaai.org/FLAIRS/2007/FLAIRS07-027.pdf",
            "T07. Taylor, Matuszek, Smith, Witbrock. FLAIRS 2007.",
            {"id": T07, "title": "Guiding Inference with Policy Search Reinforcement Learning",
             "citation": ('Taylor, M.E. (The University of Texas at Austin), Matuszek, C., Smith, P.R., Witbrock, M. '
                          '(Cycorp, Inc.), "Guiding Inference with Policy Search Reinforcement Learning," Proceedings of '
                          'FLAIRS 2007, pp. 146-151, AAAI, 2007 (hand-transcribed from p.146 and the page footers)'),
             "transcribed_from": "p.146 byline and the printed page numbers 146 to 151",
             "disposition": ("Policy search RL (NEAT) learns to order inference tactics in ResearchCyc and beats the "
                             "hand-tuned Balanced Tactician at median time to first answer; the source of the 2007 "
                             "inference-module and tactic-type counts"),
             "venue": "the venue from the AAAI URL path cdn.aaai.org/FLAIRS/2007; the month in the file name from the "
                      "PDF's creation date (2007-03-15)"}),
    "R05": ("2005-05_Ramachandran_First-Orderized-ResearchCyc-Expressivity-and-Efficiency.pdf",
            "272a25c7836a7167a77256005e8a62bcab5d1e3da25f1db7adb664f90a9f19c6", 94912,
            "https://cyc.com/wp-content/uploads/2019/07/First-Orderized-1.pdf",
            "R05. Ramachandran, Reagan, Goolsbey. AAAI Workshop 2005.",
            {"id": "ramachandran-2005-first-orderized-researchcyc-expressivity-efficiency",
             "title": "First-Orderized ResearchCyc: Expressivity and Efficiency in a Common-Sense Ontology",
             "citation": ('Ramachandran, D. (University of Illinois at Urbana-Champaign), Reagan, P., Goolsbey, K. '
                          '(Cycorp Inc.), "First-Orderized ResearchCyc: Expressivity and Efficiency in a Common-Sense '
                          'Ontology," Papers from the AAAI Workshop on Contexts and Ontologies: Theory, Practice and '
                          'Applications, AAAI, 2005 (hand-transcribed from p.1)'),
             "transcribed_from": "p.1 title and byline",
             "disposition": ("How ResearchCyc's higher-order ontology is translated to first-order logic, and what "
                             "that costs in expressivity and gains in efficiency; not yet screened"),
             "venue": "the workshop from T07's reference list (p.151); the month in the file name from the PDF's "
                      "creation date (2005-05-13)"}),
    "S16": ("2016-03_Sharma_Controlling-Search-in-Very-Large-Commonsense-Knowledge-Bases.pdf",
            "4c010a72fbc2a03036bd3c17ade3c54b7da0b2c75666c4e4461875127c346421", 697378,
            "https://arxiv.org/pdf/1603.04402",
            "S16. Sharma, Goolsbey, Witbrock. arXiv:1603.04402.",
            {"access_id": "arXiv:1603.04402",
             "disposition": ("Machine learning to control search in very large commonsense knowledge bases (Cyc); "
                             "not yet screened")}),
    "S19": ("2019-07_Sharma_Simulation-Based-Approach-to-Efficient-Commonsense-Reasoning.pdf",
            "e91147dacf108f5d99ab313703dad05b97df17b53459554c5e7be6eedbf3afbc", 292774,
            "https://www.cyc.com/wp-content/uploads/2019/07/AAAI-SharmaA.1646.pdf",
            "S19. Sharma, Goolsbey. 2019.",
            {"access_id": "DOI:10.1609/aaai.v33i01.33011360",
             "disposition": ("Simulation-based search control for commonsense reasoning in very large knowledge bases "
                             "(Cyc); not yet screened")}),
    "M06": ("2006-07_Matuszek_An-Introduction-to-the-Syntax-and-Content-of-Cyc.pdf",
            "f315a930f92d39f5abc9026f1dae031869cdde358252505847d57e4650b751d0", 60754,
            "https://cdn.aaai.org/Symposia/Spring/2006/SS-06-05/SS06-05-007.pdf",
            "M06. Matuszek, Cabral, Witbrock, DeOliveira. AAAI Spring Symposium 2006.",
            {"id": "matuszek-2006-introduction-syntax-content-cyc",
             "title": "An Introduction to the Syntax and Content of Cyc",
             "citation": ('Matuszek, C., Cabral, J., Witbrock, M., DeOliveira, J. (Cycorp, Incorporated), "An '
                          'Introduction to the Syntax and Content of Cyc," AAAI Spring Symposium SS-06-05, AAAI, 2006 '
                          '(hand-transcribed from p.1)'),
             "transcribed_from": "p.1 title and byline",
             "disposition": "CycL's syntax and the knowledge base's content and ontology structure as of 2006; not yet screened",
             "venue": "the symposium from S19's reference list and the AAAI URL path (SS-06-05); the month in the file "
                      "name from the PDF's creation date (2006-07-01)"}),
    "OV19": ("2019-12_Cycorp_Technology-Overview.pdf",
             "9fe1ddf71d4055591a91a9280b7ccd20c3be482c33159e82179ff799a4ff47dd", 880097,
             "https://cyc.com/wp-content/uploads/2021/04/Cyc-Technology-Overview.pdf",
             'OV19. Cycorp, "Technology Overview", PDF dated December 2019.',
             {"id": "cycorp-2019-cyc-technology-overview", "kind": "reference", "title": "Technology Overview",
              "citation": ('Cycorp, "Technology Overview," vendor document, cyc.com, 2019 (hand-transcribed from the '
                           'cover and contents)'),
              "transcribed_from": "cover and contents page",
              "disposition": ("Reference: Cycorp's own overview of current Cyc, its knowledge base, reasoning and "
                              "commercial use; not yet screened"),
              "venue": "the page prints no date; the year and the month in the file name from the PDF's creation "
                       "date (2019-12-11), which the handoff also gives"}),
    "PH20": ("2020-04_Parisi_Bayesian-Networks-Are-Not-the-Solution.pdf",
             "73a4496c1cc3de3c92667a737c20ecfc4b3834a7707027f3dd9657f2832aea40", 83169,
             "https://cyc.com/wp-content/uploads/2021/04/bayesnetspaper.pdf",
             "PH20. Parisi and Hart, Cycorp, April 2020.",
             {"id": "parisi-2020-bayesian-networks-not-solution-opening", "kind": "reference",
              "title": "Bayesian Networks Are Not the Solution to Opening Machine Learning's Black Box",
              "citation": ('Parisi, A., Hart, C., "Bayesian Networks Are Not the Solution to Opening Machine '
                           'Learning\'s Black Box," cyc.com, April 2020 (hand-transcribed from p.1)'),
              "transcribed_from": "p.1 title, byline and date",
              "disposition": ("Reference: a Cycorp white paper arguing that CycL, not Bayesian networks, gives "
                              "transparent causal reasoning; not yet screened"),
              "venue": "no venue printed; hosted at cyc.com"}),
    "L10": ("2010-09_Lenat_Harnessing-Cyc-to-Answer-Clinical-Researchers-Ad-Hoc-Queries.pdf",
            "0608b25af6f7543a850df771f94980fba04638257b4fe249988629723e752c09", 795729,
            "https://cogsci.northwestern.edu/documents/LenatEtAl_2010.pdf",
            "L10. Lenat et al., AI Magazine 2010 (a university mirror, not the publisher).",
            {"access_id": "DOI:10.1609/aimag.v31i3.2299",
             "disposition": ("Cyc extended by about 2% to answer Cleveland Clinic researchers' ad hoc queries; the "
                             "local copy is a 27-page university mirror, not the publisher's PDF; not yet screened")}),
}

T07_CHECKED = ("2026-10-08, Claude, read all six pages (proceedings pp. 146-151) directly, text extracted from the "
               "local PDF with pdftotext")
T07_READ = ("Claude", "2026-10-08", "full", "all six pages, pp. 146-151")
T07_APPLICABILITY = [
    ("method", "How Cyc's inference harness splits work among the Strategist, Tactician and Worker and scores "
               "tactics -- section Inference in Cyc, pp. 146-147"),
    ("ml", "Policy search reinforcement learning (NEAT) trained on 382 queries and tested on 381 to order "
           "inference tactics -- Abstract and section RL Tactician, pp. 146-147"),
]
REASON = f"{DOWNLOADED} ({TAG}): extracted from T07, read in full; INTAKE_WORKFLOW.md section 18"

ASSERTIONS = [
    AssertionRecord(
        id="cyc-2007-about-a-thousand-inference-modules",
        value=("In 2007 Cyc's inference engine was composed of approximately a thousand specialized reasoners, called "
               "inference modules, from general ones such as subsumption reasoning to modules for a single predicate"),
        provenance=f"{T07}, p.146, section Inference in Cyc",
        evidence_tag="N/A", context="method",
        citation_context=('"Cyc\'s inference engine is composed of approximately a thousand specialized reasoners, '
                          'called inference modules, designed to handle commonly occurring classes of problem and '
                          'sub-problem." (p.146; the typographic apostrophe normalized)'),
        certainty="low",
        certainty_reasons=("Started LOW: a round count by Cycorp authors of Cycorp's own system, with no list and no "
                           "definition of what counts as a module, as for cyc-hl-module-count. NOT upgraded: favorable "
                           "to the authors, so the admission-against-interest upgrade does not apply"),
        fidelity="exact", updated=DOWNLOADED, updated_reason=REASON,
        derivation="extracted", claim_type="vendor-self-claim"),
    AssertionRecord(
        id="cyc-2007-eight-tactic-types",
        value=("In 2007 ResearchCyc's Balanced Tactician scored tactics by tactic type, productivity, and completeness "
               "or preference; the paper counts eight tactic types, with split as its example, of which its RL "
               "Tactician handled five, a sixth needed an engine code change, and the last two were transformations"),
        provenance=f"{T07}, pp. 147-148, sections Inference in Cyc and Experimental Methodology",
        evidence_tag="N/A", context="method",
        citation_context=('"There are eight tactic types which describes the kind of operation to be performed, such '
                          'as "split" (i.e. split a conjunction into two sub-problems)." (p.147; the typographic '
                          'quotation marks normalized); "Of the eight tactic '
                          'types available in ResearchCyc, the RL Tactician currently only handles five." (p.148; the '
                          '"fi" ligature normalized)'),
        certainty="moderate",
        certainty_reasons=("Started MODERATE: Cycorp authors describing their own engine's design, as the 2002 manual "
                           "pages are. Unreconciled: the 2009 LarKC source's *TACTIC-TYPES* lists six (removal, "
                           "meta-removal, transformation, rewrite, structural, removal-conjunctive; "
                           "inference_datastructures_enumerated_types.java line 2574) and puts SPLIT, T07's example, "
                           "among the generalized tactic types (inference_datastructures_problem.java line 1592). The "
                           "two sources appear to count at different granularities, two years apart; no line in either "
                           "settles it"),
        fidelity="exact", updated=DOWNLOADED, updated_reason=REASON,
        derivation="extracted", claim_type="vendor-self-claim"),
]
HL_MODULE_NOTE = (f"{DOWNLOADED} ({TAG}): T07 is now read directly from a local copy; p.146 says \"approximately a "
                  "thousand specialized reasoners, called inference modules\" (2007), entered as "
                  "cyc-2007-about-a-thousand-inference-modules. Sprint 6's \"not verified here\" note is settled")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_files() -> list[str]:
    """Every file present, with the size and SHA-256 measured at download."""
    problems = []
    for key, (name, sha, size, *_rest) in PAPERS_IN.items():
        path = PAPERS / name
        if not path.exists():
            problems.append(f"{key}: {path} is missing")
        elif path.stat().st_size != size or sha256_of(path) != sha:
            problems.append(f"{key}: {path} differs from the download (size or SHA-256)")
    return problems


def entry_for(key: str) -> dict:
    name, sha, size, url, cited_as, fields = PAPERS_IN[key]
    local = str(PAPERS / name)
    entry = {"context": "method", "tier": "seen", "found_via": ROUTE, "cited_as": cited_as,
             "evidence": (f"Local copy downloaded {DOWNLOADED} from {url} (team lead approved the download "
                          f"2026-10-06); SHA-256 {sha}; {size:,} bytes")}
    for k in ("id", "title", "citation", "transcribed_from", "disposition", "kind"):
        if k in fields:
            entry[k] = fields[k]
    entry["access"] = f"{local} | {fields.get('access_id', url)}"
    reason = f"{DOWNLOADED}: added by scripts/sprint7_f44_cycorp_papers.py ({TAG})"
    if "venue" in fields:
        reason += f"; {fields['venue']}"
    entry["updated_reason"] = reason
    return entry


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    apply = "--apply" in args
    problems = check_files()
    if problems:
        print("\n".join(problems))
        return 1
    citations.assume_recent_arxiv_request()  # S16's PDF came from arxiv.org minutes earlier
    fetcher = citations.PacedFetcher()
    records = {key: intake.build_record(entry_for(key), fetcher=fetcher, today=DOWNLOADED) for key in PAPERS_IN}
    for key, rec in records.items():
        print(f"{key:5} {rec.id} [{rec.citation_origin}]\n      {rec.citation}")
    for a in ASSERTIONS:
        print(f"assert {a.id} <- {T07} [{a.certainty}, {a.claim_type}]")
    if not apply:
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F44 eight Cycorp papers")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        for rec in records.values():
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (rec.id,)).fetchone() is None:
                insert_paper(conn, rec, fetcher=fetcher)
        for a in ASSERTIONS:
            if conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone() is None:
                insert_assertion(conn, a, yielded_by=T07)
        if conn.execute("SELECT tier FROM paper_fields WHERE record_id = ?", (T07,)).fetchone()[0] != "read":
            for ctx, rationale in T07_APPLICABILITY:
                conn.execute("INSERT OR IGNORE INTO paper_applicability (record_id, context_id, rationale) "
                             "VALUES (?, ?, ?)", (T07, ctx, rationale))
            add_read(conn, T07, *T07_READ)
            set_tier(conn, T07, "read", checked_against_source=T07_CHECKED)
            append_updated_reason(conn, T07, f"{DOWNLOADED} ({TAG}): read in full and promoted; yields "
                                  + ", ".join(a.id for a in ASSERTIONS), DOWNLOADED)
        prior = conn.execute("SELECT updated_reason FROM records WHERE id = 'cyc-hl-module-count'").fetchone()[0]
        if HL_MODULE_NOTE not in prior:
            append_updated_reason(conn, "cyc-hl-module-count", HL_MODULE_NOTE, DOWNLOADED)
        conn.commit()
    finally:
        conn.close()
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
