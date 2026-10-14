# Sprint 8 Task G (F71): QCi's Dirac-3S material and what is new on its site

**Every count below is a snapshot as of 2026-10-13.** The lists are computed
by `scripts/sprint8_f71_qci_site_check.py` from QCi's sitemap (read
2026-10-13) against the scrape of 2026-09-24
(`D:\Data\Harold\EvidenceBasedDB\References\QCi-site\`, 546 files). The
records are written by `scripts/sprint8_f71_qci_dirac3s_reading.py`, and
every quote is checked against its local copy by
`tests/test_f71_qci_dirac3s_reading.py`. All local copies are outside the
repository: pages under `References\QCi-site_2026-10-13\`, QCi's PDFs under
`References\QCi-site\dirac-3s-technical-reference\` (team lead, 2026-10-13:
"kept with other references").

## The four items (F65's list, recovered 2026-10-13)

1. **The PR Newswire release (2026-10-01).** Read in full; entered as
   `qci-2026-dirac-3s-announcement-press-release` (QCi's own copy has the
   same body). It claims nearly 10,000 variables, "a 10x increase over
   QCi's current 1,000-variable system"; the 9,980 figure needs one
   expansion module, and the base module takes 949, the Dirac-3's figure.
   It also repeats the review's headline that the Dirac-3S was the only
   solver optimal on every planted instance, which the review's own Table 6
   does not support (item 2). First customer shipment: November 2026,
   recorded as a forecast at low certainty.
2. **The Dirac-3S Technical Reference module.** Six pages. Their content is
   QCi's documents: the Dirac-3S User Guide Rev A (byte-identical to the
   copy read in Task C, so the guide record now notes its public URL), the
   new **Continuous Solver Benchmarking review** (QCi-QMS-900-000004 Rev A,
   24 pp., read in full), and two QCi papers now on arXiv, entered at `seen`
   (arXiv:2609.38779, Motzkin-Straus max clique; arXiv:2610.01911, simplex
   formulations of Karp's 21 problems). The module's "Software Interface"
   page links a second copy of the benchmarking review, not a software
   reference.
3. **The Dirac-3 product page.** The address now serves the **Dirac-3S**
   page. The Dirac-3 specification shown on 2026-09-24 (949 variables,
   100 W, trial access) is gone; the new specification table repeats the
   Dirac-3S guide's ceilings (949 base, 9,980 with one expansion module, at
   second order). Both copies are entered, and the change is an assertion.
4. **What is new on the site since 2026-09-24.** The lists below.

## What the benchmarking review says (assertions entered)

- **The headline is contradicted by its own table**
  (`dirac3s-all-optimal-headline-contradicted-by-own-table`, high): "zero
  optimality gap across all synthetic benchmark instances" (p.6), but Table 6
  (contrast ub = 100) shows gaps of 7.56 and 9.59 percent, and section 5.2
  counts six of eight.
- **It counts the ub = 10 results two ways**
  (`dirac3s-review-counts-its-ub10-results-two-ways`, high): all eight in
  Table 5 and section 5.2; seven of eight in the conclusion; three listed
  failures where Table 6 shows two.
- **Best-of-ten hides per-sample success**
  (`dirac3s-best-of-batch-hides-low-per-sample-success`, moderate): about
  one sample in ten was optimal on some instances recorded as solved.
- **The max-clique lead is best-of-four schedules**
  (`dirac3s-max-clique-edge-is-best-of-four-schedules`, moderate): with one
  fixed schedule the three solvers are nearly identical in aggregate; half
  the graphs do not separate them.
- **Not competitive with dedicated clique algorithms**
  (`dirac3s-not-competitive-with-dedicated-clique-solvers`, moderate).
- **Slower than PGD at low contrast**
  (`dirac3s-slower-than-pgd-at-low-contrast`, moderate): 3 to 63 times at
  ub = 10; faster from 6,000 variables up at ub = 100.
- **QPLIB does not separate the solvers**
  (`dirac3s-qplib-results-do-not-separate-solvers`, moderate), consistent
  with the independent reproduction already in the store
  (`classical-solvers-match-dirac3-published-benchmarks`), not linked
  because that is a Dirac-3 claim.
- **Which device ran is not settled by QCi's documents**
  (`dirac3s-benchmark-notebook-runs-direct-and-names-dirac-3`, high): the
  review lists the interface as the cloud API; the published Dirac-3S
  notebook connects directly to a private network address and sets up a
  "Dirac-3 solver", and the review itself says "We run Dirac-3".

**Held for the team lead (Class 2):** four of these are
admission-against-interest candidates and stay at moderate:
per-sample success, best-of-four schedules, dedicated clique algorithms,
slower than PGD. Decided 2026-10-14: the team lead upgraded none of the
four; all stay at moderate.

## The site diff (computed)

- **Sitemap**: 2,854 URLs. Its `lastmod` is not a change signal (most pages,
  scraped ones included, show the day it was read).
- **Scraped pages compared**: 81 (applications, lessons, research and
  publications, systems, technology). **Unchanged**: 77, once the site's
  new "Benchmarking" menu entry and each section's own menu change are set
  aside (a difference on half or more of the pages compared, or of the
  section's pages).
- **Changed (4)**: the Dirac-3 product page (now the Dirac-3S page; item 3);
  the research-and-publications index and the landmine white paper (menu
  order and a "Next page" link only); the uQRNG page (a button moved).
- **New in the scraped sections (5)**: the "featured publication" folder
  (the old "featured-publications" page moved there, with the two papers
  of item 2 and the uQRNG white paper); and the fraud-detection application
  page, which the 2026-09-24 scrape did not hold under `QCi-site` (it was
  saved separately as `References\2026_QC-6_...` and is in the store).
- **Gone (1)**: `research-and-publications/featured-publications`, moved as
  above.
- **Sections the scrape did not cover, with a sitemap date on or after
  2026-09-24 (43)**: the new **Benchmarking** section (11 pages: the review
  and nine notebooks, Dirac-3S, Hexaly and PGD on max-clique, planted and
  QPLIB); the **Dirac-3S Technical Reference** module (6); a Dirac-3S
  software-interface page and the Dirac-3S user-guide page under developer
  resources and support (2); two press releases (the Dirac-3S announcement;
  QCi at the Maxim Growth Summit, not Dirac-related); and 22 developer and
  learning-module pages dated the day they were read, which repeat the
  application and formulation pages already scraped.
- **New software-package version (1)**: `qci-client` v5.0.3. Package pages
  are counted by version, not read.

## Sources entered

Five references at `read` (the release, the benchmarking review, both
product-page copies, the planted notebook), two papers at `seen` through the
door (one paced arXiv request each), 11 assertions under `platform:dirac-3s`,
and a note on the Dirac-3S guide record. No Dirac-3 assertion was edited.
