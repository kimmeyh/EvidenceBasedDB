# F117 group review prompt (Sprint 14 Task E)

The Sonnet 5.5 tier of F117's review. One reviewer per group. The
coordinator (Opus 5.5) reads the decisions, signs off the group, and the
team lead decides every certainty change on a stored assertion. Written
2026-10-30.

---

You review one group of F114's first-pass reads before they enter the
Evidence Based DB. A cloud reader read each paper in full and proposed
assertions, each with quotes, an anchor, a result type and a suggested
certainty. Every quote is already verified verbatim against the paper by
script. Your job is judgment: does the passage settle each grade the
item asks about?

GROUP is given in your task message. Read these, and write only the one
output file:

- `D:\Data\Harold\EvidenceBasedDB\work\f114\review\items\GROUP.json`:
  the items to decide.
- `D:\Data\Harold\EvidenceBasedDB\work\f114\texts\<record>.txt`: each
  paper's full text, the same text its reader had. Pages are separated by
  form feeds.
- Output: `D:\Data\Harold\EvidenceBasedDB\work\f114\review\decisions\GROUP.json`.

Read every item's passage in the paper text, in context: find the quotes
(Grep is quickest), then read the surrounding paragraph, and for a
theorem, its statement, its conditions and whether the paper proves it.
There is no budget: every item gets a decision from the passage, never
from the reader's suggestion alone.

## The five bases for HIGH

HIGH means the paper itself settles the statement. Only these bases:

- **setup**: the paper's own experimental or computational setup, as it
  states it (devices, datasets, sizes, parameters, protocol). Not a
  result.
- **scope**: what the paper itself covers or does not cover, as it
  states it.
- **definition**: a term or object the paper defines.
- **proved result**: a theorem, lemma, proposition or corollary the
  paper states AND proves (the proof is in the paper or its appendix),
  with the conditions the quotes carry. A result proved elsewhere and
  only cited is not this basis. A bound argued informally is not this
  basis.
- **stated limit**: a limitation, caveat or failure the paper itself
  states about its own work.

Everything else is LOW: a measured result (an experiment or simulation
outcome), the authors' claim or interpretation, a cited result, a field
statement, a vendor's claim about its own product, a theoretical result
that is not proved in this paper or whose conditions the quotes drop.

## Item kinds and what to decide

Each item has `kind`, `id`, `record`, `anchor`, `value`, `quotes`,
`result_type`, `suggested`, `suggested_basis`, `reader_reason`.

- **new-high**: the reader suggested HIGH. Decide `"high"` with a basis
  and why, or `"low"` with why.
- **new-theory**: a theoretical result the reader did not suggest HIGH.
  Decide `"low"` with its cause (for example "a sketch, not a proof",
  "proved in reference [12], cited here", "the conditions are lost in
  the text layer"), or `"high"` with basis "proved result" and why.
- **changed**: a stored assertion the reader corrected, narrowed,
  widened or contradicted. `stored` is its current certainty. First,
  `"decision"`: `"accept"` if the reader's new value is right by the
  passage, or `"keep"` if the stored one is better, with why. If you
  accept, also give `"grade"`: `"high"` with basis and why, or `"low"`
  with why.
- **stored-high**: a stored HIGH the reader confirmed. Decide `"high"`
  with basis and why if the passage settles it, or `"low"` with why if
  it does not. A `"low"` here is a certainty change the team lead
  decides, so say exactly what the passage lacks.

The value must say only what its quotes and passage say. If an item's
value overstates its passage, say so in `why` and decide `"low"` (or
`"keep"` for a changed item).

## Output

One JSON object, keyed by item id, every item present:

```json
{
 "some-id": {"decision": "high", "basis": "proved result", "why": "Theorem 2, Section 3, p.6: stated with its conditions and proved in Appendix B"},
 "other-id": {"decision": "low", "why": "a simulation outcome on one dataset, a measured result"},
 "changed-id": {"decision": "accept", "grade": "low", "why": "the narrowed value matches Table 2; a measured result"}
}
```

`why` names where the paper settles it (section, theorem, page) or what
it lacks. Short sentences. Then reply with one line: the counts of high,
low, accept and keep, and the minutes you took.
