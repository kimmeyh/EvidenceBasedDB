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
  only as the maker of Dirac-3 and, in the acknowledgments, as an
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

## Task F result (2026-09-24; counts are a snapshot as of this date)

`scripts/sprint5_qci_authors.py`. arXiv's API refused every author query
(HTTP 406) as it had refused metadata requests all sprint; DataCite's
index of arXiv DOIs answered with full author lists, and Crossref added
journal papers. The first run capped the family-name query at 5,000
records, which truncated the three common families; the rerun adds a
full-name query for them (Yu-Ping Huang: 115 hits against 48).

| Person | Hits | Accepted (seed / network) | Unresolved |
|---|---|---|---|
| Babak Emami | 17 | 3 (3 / 0) | 14 |
| Wesley Dyk | 6 | 4 (4 / 0) | 2 |
| David Haycraft | 5 | 5 (5 / 0) | 0 |
| Carrie Spear | 5 | 3 (3 / 0) | 2 |
| Lac Nguyen | 14 | 6 (6 / 0) | 8 |
| Nicholas Chancellor | 74 | 6 (6 / 0) | 68 |
| Mohammad-Ali Miri | 144 | 5 (5 / 0) | 139 |
| Uchenna Chukwu | 14 | 4 (4 / 0) | 10 |
| Yu-Ping Huang | 115 | 44 (26 / 18) | 71 |
| R. Joseph Rupert | 3 | 2 (2 / 0) | 1 |
| Sam Wu | 27 | 1 (1 / 0) | 26 |
| Nick Vrahoretis | 5 | 5 (5 / 0) | 0 |
| Irwin Huang | 10 | 6 (6 / 0) | 4 |
| Milan Begliarbekov | 20 | 4 (3 / 1) | 16 |
| Pranav Mahamuni | 6 | 5 (5 / 0) | 1 |
| Cesar Martinez-Delgado | 1 | 1 (1 / 0) | 0 |
| Joel Russell Huffman | 12 | 1 (1 / 0) | 11 |
| Yong Meng Sua | 102 | 86 (86 / 0) | 16 |

191 acceptances, 124 distinct papers, 3 already records, **121 entered**
(39 arXiv, downloaded to `QCiAuthorsPapers/<person>/`; 82 journal DOIs,
recorded through the DOI and not downloaded). Sua's 86 seeds are his
long collaboration with Yu-Ping Huang at Stevens, each verified by a
full-name match; the network rule added 19 papers, 18 of them Huang's.

**Premise (c) falsified for several people, as the plan said it might
be.** The network rule can only reach outward from QCi collaborators, so
a prolific person's pre-QCi career, which shares no co-authors with the
QCi papers, stays unresolved: Miri 139 of 144, Chancellor 68 of 74, Sam
Wu 26 of 27, Emami 14 of 17. Those papers were NOT downloaded or entered.
Whether to accept them needs a looser rule, and choosing one is the team
lead's decision (Manual Validation). The names most likely to be single
people (Miri, Chancellor, Begliarbekov, Vrahoretis) are the strongest
candidates for an exact-full-name rule; Sam Wu is the weakest.

**Decided 2026-09-25 (team lead, Manual Validation Q1 = 2)**: they stay
unresolved; no looser rule.

## Q1 revised by the team lead (2026-09-25): topic screening of the unresolved hits

Team lead, during Manual Validation: "can you pull any of the papers from
the authors IF they are related to QML, ML or the Zeno effect (can you
screen the abstracts to determine)". This replaces Q1 = 2 for the
unresolved hits. Rule, written BEFORE any abstract was screened:

1. **Topic test on the registry abstract** (DataCite for arXiv records,
   Crossref where it carries one), case-insensitive:
   - QML or ML: "machine learning", "neural network", "deep learning",
     "reinforcement learning", "supervised", "unsupervised", "classifier",
     "classification", "reservoir computing", "extreme learning",
     "kernel method", "support vector", "boosting", "feature selection",
     "clustering", "generative model", "transformer", "large language
     model", "training data";
   - Zeno: "zeno".
   A hit with no abstract is tested on its title with the same terms.
2. **Claude reads every keyword-positive abstract** and rejects any whose
   match is incidental (for example "classification" of optical modes,
   not of data). Kept and rejected lists are recorded with one line each.
3. **Identity is NOT established by this rule.** Each admitted record's
   disposition says "topic-screened; authorship not confirmed by
   co-authorship". Admissions under a common family name (Wu, Huang,
   Nguyen) are listed separately for the team lead.

### Result of the topic screen (2026-09-25; counts are a snapshot as of this date)

`scripts/sprint5_qci_topic_screen.py`. The search was re-run to keep every
unresolved hit with its registry abstract; the accepted set came out
identical to the 2026-09-24 run. Of 392 unresolved hits (225 with an
abstract, 167 tested on the title), 25 matched a term; Claude's reading
rejected 4 (recorded with reasons in the script's `REJECTED`: an
error-correction paper using "machine learning" as an analogy, two
astronomy papers, and a journal duplicate of a kept arXiv paper). **21
entered at `seen`**, each disposition saying "topic-screened ...;
authorship not confirmed by co-authorship": Chancellor 6 (Zeno
computation, quantum Boltzmann machines, QNN training), Miri 3, Chukwu 1,
Yu-Ping Huang 10 (5 on the quantum Zeno blockade), Sam Wu 1. 15 PDFs
downloaded to `QCiAuthorsPapers/<person>/topic-screened/`; 2 were already
on disk.

**Weakest on identity, for the team lead**: three admissions whose topic
passes but whose authorship is least likely to be the QCi person --
`arXiv:2405.02958` (MRI reconstruction) and `DOI:10.1101/2021.05.04.21256502`
(dental deep learning) under "Yu-Ping Huang", and `arXiv:2603.15546`
(human-motion generation) under "Sam Wu". The Zeno-blockade papers are
Yu-Ping Huang's own line of work and are not in doubt.
