# F143: why the agents' cost per page rose (Sprint 17 Task F)

Every count here is a snapshot as of 2026-11-08. Sources: the per-group
telemetry files (`manifests/sprint16_f114_reads/telemetry/`, F139), the
group read files (`manifests/sprint13_g_reads/`), the review item files
(`D:\Data\Harold\EvidenceBasedDB\work\f114\review\items\`), and each
PDF's page count (`pdfinfo`). Sprint 15's per-page baseline (readers
3,645 tokens and 0.44 minutes; reviewers 1,676 and 0.14) is F139's,
from INTAKE section 73.

## Summary

The cause is named. Sprint 16 readers did not read pages less
efficiently. They wrote more assertions per page. Reviewers then had
more items per page to decide, and a larger share of those items were
theory items. The tokens spent per assertion did not rise. The share of
each paper kind in a group sets how dense its assertions are, so the kind
of paper is what drives the cost per page.

- **Readers, tokens:** +27% per page (3,645 to 4,633). New assertions per
  page went from 1.83 (Sprint 15: 207 papers, 6,108 pages) to 2.47
  (Sprint 16: 20 papers, 531 pages), +35%. Tokens per assertion stayed
  flat: about 1,880 in Sprint 15, about 1,820 in Sprint 16 (stored
  verdicts counted with the new assertions).
- **Readers, minutes:** +70% per page (0.44 to 0.75). Minutes per
  assertion rose about 30% (0.23 to 0.29). The rest of the rise cannot be
  split from the data held. Sprint 16 rendered 0.31 to 0.51 pages as
  images per page read, and each group ran the full check 3 to 11 times.
  Sprint 15 recorded neither, so neither can be compared.
- **Reviewers, tokens:** +92% per page (1,676 to 3,224). Decision items
  per page went from 0.79 (47 Sprint 15 groups) to 1.35 (6 Sprint 16
  groups), +71%. Theory items, which take the longest to decide, went
  from 0.094 to 0.179 per page (x1.9). One re-review adds the rest:
  g333 had 3 reviewers (the first graded Monaco's 70-page supplement from
  its statements, F142 part 3). Without g333, Sprint 16's reviewers spent
  2,617 tokens per page (+56%).

## Per group, by paper kind

Per page: reader tokens and minutes, reviewer tokens, new assertions,
pages rendered as images, figures listed, and theory assertions.

| Group | Kind | Pages | Reader tok | Reader min | Reviewer tok | Assertions | Rendered | Figures | Theory |
|---|---|---|---|---|---|---|---|---|---|
| g333 | proof-heavy (2 of 5 are 68 and 70 pages of proofs) | 181 | 4,769 | 0.75 | 4,396 (3 reviewers) | 2.85 | 0.31 | 0.34 | 1.40 |
| g334 | mixed | 68 | 4,526 | 0.72 | 3,156 | 2.91 | 0.37 | 0.38 | 0.81 |
| g133-r1 | experiment | 64 | 4,036 | 0.63 | 2,586 | 1.92 | 0.47 | 0.48 | 0.14 |
| g154-r1 | experiment, figure-heavy | 94 | 4,327 | 0.54 | 2,398 | 1.78 | 0.49 | 0.61 | 0.01 |
| g155 | figure-heavy | 90 | 5,033 | 1.10 | 2,646 | 2.76 | 0.51 | 0.86 | 0.09 |
| g156 | experiment | 34 | 5,037 | 0.65 | 2,128 | 1.76 | 0.44 | 0.50 | 0.03 |
| g230 (S17) | experiment (Pere v2) | 69 | 4,376 | 0.49 | 2,859 | 2.83 | 0.12 | 0.39 | 0.06 |
| g296 (S17) | theory-heavy (Altshuler, Amaro) | 28 | 8,089 | 1.12 | 5,137 | 5.86 | 0.43 | 0.54 | 1.57 |
| g348 (S17) | survey and web article | 52 | 5,956 | 0.63 | 1,623 | 4.62 | 0.42 | 0.62 | 0.00 |
| g295 (S17) | proof-heavy review and theory (Albash, Aharonov) | 160 | 4,888 | 0.52 | 3,109 | 3.75 | 0.24 | 0.39 | 0.91 |

What the table shows:

- **Theory-heavy papers cost the most per page**, for readers and for
  reviewers: g296 (1.57 theory assertions per page) is the highest on
  both, and g333 (1.40) next. Each theorem is entered with its statement
  and conditions (the full-read rule), and each theory item is decided
  against its proof.
- **Figure-heavy papers cost the most minutes per page** (g155: 0.86
  figures per page, 1.10 minutes), but not the most tokens.
- **A survey writes many assertions per page and few review items**
  (g348: 4.62 assertions per page, 19 items in 52 pages), so its reviewer
  cost per page is the lowest.
- **Repeated checks cost minutes, not tokens.** g295's reader ran the
  full check 48 times (Sprint 16 groups: 3 to 11), yet its tokens per
  assertion (1,304) are the lowest measured.
- **The tokens per assertion stay in one band** (about 1,300 to 2,900)
  across every kind. The cost per page follows the assertions per page.

## The cause

The cost per page rose because each page now yields more assertions and
more decisions, most of all in theory-heavy papers. This is the
full-read rule working as intended (team lead, 2026-10-25: "far more
important to read them all, get all the conclusions, profs,
assertions... than some budget"). It is not waste, and no fix here
lowers what a read extracts.

What can be lowered without reading less:

- the repeated re-reviews (g333's three reviewers; g155's reviewer sent
  back). F142 part 3 (Sprint 17) splits a proof appendix over 30 pages
  across reviewers from the start.
- the cost forecast: a plan that prices reads by pages alone is wrong by
  up to about 2x for a theory-heavy group.

## What the data cannot say

- Tokens are recorded per agent, and an agent reads a whole group, so no
  single paper's cost is measured. The split by kind above is by group
  mix.
- Sprint 15 recorded no renders and no check runs, so their share of the
  minutes rise cannot be measured.

The fixes are asked as numbered questions in the Sprint 17 messages
(q21 onward). Team lead, 2026-11-09: q21 and q22 "not needed". No
change follows from this analysis; it stays as the record of why the
cost per page rose.
