# QCi-affiliated people in the store and the bibliography (F5 sub-part 1)

Sprint 5 Task E (Issue #48), 2026-09-24. Every name below was read from
the paper's own author and affiliation lines, not recalled; the page is
cited. Names are as printed, including initials where the paper prints
an initial. This is the input to Task F (every paper each person
co-authored).

## Sources read

- `emami-2025-financial-fraud-entropy-computing-qci` (arXiv:2503.11273v1),
  p.1: six authors, each with "Quantum Computing Inc (QCi) 5 Marine View
  Plaza Hoboken NJ" and a `@quantumcomputinginc.com` address for four.
- `[QC-1]` Nguyen et al., arXiv:2407.04512v4 (2025-10-01), p.1: 17
  authors followed by ONE affiliation line, "Quantum Computing Inc (QCi),
  5 Marine View Plaza, Hoboken". The paper marks no second affiliation,
  so all 17 are QCi-affiliated as printed. Corresponding authors Nguyen
  and Miri with QCi addresses.
- `[QC-3]` Miri, Chukwu, Chancellor, arXiv:2604.13032v1, p.1: all three
  at QCi.
- `[QC-4]` Huang and Hu, arXiv:2502.08591v1, p.1: Yu-Ping Huang at QCi
  (`yhuang@quantumcomputinginc.com`); Yongxiang Hu at NASA Langley
  Research Center, NOT QCi.
- `loke-2026-cvqboosting-fraud-detection-smu` (SMU InK, March 2026), p.2
  author list and p.3 address block: Bethel Hui Ting Loke, Nirvik Sahoo,
  Bingyan Guan, Minrui Xu, Dev Verma, Paul R. Griffin, all at Singapore
  Management University or NTU. **None is QCi-affiliated**; QCi appears
  only as the maker of Dirac-3 and, in the acknowledgements, as an
  in-kind contributor. This confirms the Sprint 3 note already in
  `scripts/apply_paper_applicability.py`.
- `qci-2024-profiling-cvqboost`, `qci-2024-unconventional-computing-medium`,
  `qci-2026-entropy-computing-trade-magazine`: no named authors.
- `[QC-8]` Emami et al. (Scientific Reports, June 2026): not read; no PDF
  and no DOI in the bibliography (on the manual-download list).

## The 18 people

| # | Name as printed | Verified in |
|---|---|---|
| 1 | Babak Emami | emami-2025 p.1 |
| 2 | Wesley Dyk | emami-2025 p.1; QC-1 p.1 |
| 3 | David Haycraft | emami-2025 p.1; QC-1 p.1 |
| 4 | Carrie Spear | emami-2025 p.1; QC-1 p.1 |
| 5 | Lac Nguyen | emami-2025 p.1; QC-1 p.1 |
| 6 | Nicholas Chancellor | emami-2025 p.1; QC-1 p.1; QC-3 p.1 |
| 7 | Mohammad-Ali Miri | QC-1 p.1; QC-3 p.1 |
| 8 | Uchenna Chukwu | QC-1 p.1; QC-3 p.1 |
| 9 | Yu-Ping Huang | QC-1 p.1; QC-4 p.1 |
| 10 | R. Joseph Rupert | QC-1 p.1 |
| 11 | Sam Wu | QC-1 p.1 |
| 12 | Nick Vrahoretis | QC-1 p.1 |
| 13 | Irwin Huang | QC-1 p.1 |
| 14 | Milan Begliarbekov | QC-1 p.1 |
| 15 | Pranav Mahamuni | QC-1 p.1 |
| 16 | Cesar Martinez-Delgado | QC-1 p.1 |
| 17 | Joel Russell Huffman | QC-1 p.1 |
| 18 | Yong Meng Sua | QC-1 p.1 |

## Observations for Task F

- **Collision risk is uneven.** "Sam Wu" and "Irwin Huang" are common name
  forms; "Yu-Ping Huang" is a prolific academic (a long publication record
  predating QCi). Task F's disambiguation rule applies per person, and a
  person whose hits cannot be split is reported with counts, not
  downloaded.
- **Affiliation is time-bound.** A person affiliated with QCi in 2025 may
  have published elsewhere before joining. The card asks for papers "on
  ANY topic", so earlier papers count, but each hit must be tied to the
  SAME person (co-author network, subject continuity), not merely to the
  name.
- **A bibliography citation error found on the way**: `[IC-1]` cites its
  second author as "Ravan, M."; the paper prints "Bahram Abedi Ravan"
  (arXiv:2605.03612v1 p.1). The store derives authors from the registry,
  so no record inherits the error.

## Task F's disambiguation rule (written 2026-09-24, BEFORE any search hit was read)

A name is a query, not a key. For each person P, a search hit (a paper
whose author list carries P's name) is ACCEPTED as P's only when:

1. **Seed**: the hit's author list also carries another of the 18 people
   above (a QCi co-authorship, the tie that put P on this list); or
2. **Network**: the hit shares at least TWO co-authors (other than P)
   with P's already-accepted hits. Applied repeatedly until nothing new
   is accepted, so a long-running collaboration (a former group, a PhD
   lab) is followed outward from the QCi papers one step at a time.
   Two, not one: a single shared co-author with a common name would
   re-admit the collision the rule exists to stop.

Everything else is UNRESOLVED and reported with counts per person, not
downloaded. Name matching itself is on family name plus given name or
its initial as the source prints it. Search order per the card (team
lead, 2026-09-16): arXiv, then DOI registries (DataCite for arXiv's own
DOIs, then Crossref), then Google Scholar. **Google Scholar has no public
API, and its `robots.txt` disallows `/scholar` for every user agent
(checked 2026-09-24)**, so it is not used by the script; a person whose search leaves many unresolved hits is named for a
manual Scholar check instead.

**Premise falsifier (plan premise c)**: a person whose seed set is empty
or whose unresolved count dwarfs the accepted count is one for whom name
plus network does NOT disambiguate; the result says so per person rather
than downloading the name's hits.
