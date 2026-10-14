# Sprint 8 Task F (F61): the Massoli et al. survey list

Run 2026-10-12 by `scripts/sprint8_f61_massoli_list.py` against
`allPapers.md` in github.com/fvmassoli/survey-quantum-computation (last
commit 2022-02-10; read through the GitHub API). **Every count below is a
snapshot as of 2026-10-12.**

## Result: every one of the 184 entries is accounted for

- **28 already in the store**: 27 matched before any request (arXiv id, DOI,
  or normalized title with the first author's surname), and 1 more after its
  identifier resolved to an existing record.
- **137 entered** through the door at `seen`, each with `found_via` naming
  the list, its section, year and topic tags, and `cited_as` the entry's own
  line. Context `qml` when a tag names neural networks, learning,
  perceptrons, classification or kernels; otherwise `qc`.
- **1 duplicate within the list** (the same paper listed twice).
- **18 refused**, each with the reason (below): 10 with no arXiv id, no DOI
  and no exact-title match on Crossref (4 of them IEEE Xplore links, which
  carry no DOI in the list); 3 ACM `10.5555` identifiers that are not
  registered DOIs; and 5 the door cannot read yet, carded as **F68**
  (3 old-style arXiv ids such as `quant-ph/0405098`, 2 DOIs containing
  parentheses).
- The list's repository is entered as
  `fvmassoli-survey-quantum-computation-github-repo` and linked to the survey
  (`massoli-2022-leap-among-quantum-computing-quantum`) as `dataset-of`,
  quoting its README.

No PDF was fetched. Requests: Crossref for DOIs and title searches; arXiv
through the door's paced fetcher (18 s apart, inside F52's cap), about 24
in the dry run and 24 in the apply.

## Derived fields on the new records (SPRINT_PLANNING.md, Sprint 6 I5)

The 138 new records carry no probe rows. Under ADR-0005 A7 a record with no
probe takes its `updated` date (2026-10-12) as its last check, so each
comes due in its own section 10 to 22 months from now, with the rest of the
store; no separate probe run is planned.

## Refused entries

- Machine Learning Algorithms in Quantum Computing: A Survey (Surveys 2020; https://ieeexplore.ieee.org/abstract/document/9207714/?casa_token=086g): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum machine learning (Surveys 2018; https://academic.oup.com/nsr/article/6/1/26/5222655?login=true): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum algorithms for deep convolutional neural networks (Papers 2020; https://openreview.net/pdf?id=Hygab1rKDS): no arXiv id, no DOI, and no exact-title match on Crossref
- Adiabatic Quantum Computation and Quantum Annealing: Theory and Practice (Papers 2014; https://ieeexplore.ieee.org/document/7055969): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum computing Defining and detecting quantum speedup (Papers 2014; https://pubmed.ncbi.nlm.nih.gov/25061205/): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum state discrimination (Papers 2009; https://www.osapublishing.org/abstract.cfm?uri=aop-1-2-238): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum RAM based neural networks (Papers 2009; https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.227.4363&rep): no arXiv id, no DOI, and no exact-title match on Crossref
- Quantum Reinforcement Learning (Papers 2008; https://ieeexplore.ieee.org/document/4579244): no arXiv id, no DOI, and no exact-title match on Crossref
- A quantum dot neural network (Papers 1996; http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.56.1507&rep=r): no arXiv id, no DOI, and no exact-title match on Crossref
- Optimization by Simulated Annealing (Papers 1983; http://wexler.free.fr/library/files/kirkpatrick%20(1983)%20optimizatio): no arXiv id, no DOI, and no exact-title match on Crossref
- `DOI:10.5555/2871393.2871400`: DOI 10
- `DOI:10.5555/2016985.2016987`: DOI 10
- `arXiv:quant-ph/0405098`: a hand-origin record needs --id (nothing to derive it from)
- `DOI:10.5555/2981345.2981472`: DOI 10
- `arXiv:quant-ph/0107012`: a hand-origin record needs --id (nothing to derive it from)
- `arXiv:quant-ph/0001106`: a hand-origin record needs --id (nothing to derive it from)
- `DOI:10.1016/s0020-0255(00)00055-4`: DOI 10
- `DOI:10.1016/0304-4149(89)90040-9`: DOI 10
