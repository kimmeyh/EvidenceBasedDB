# Sprint 16 Task F group review prompt

Sprint 16 (2026-11-06): Sprint 15 Task H's review prompt below, with
F139's render-once change (Task B). The reviewer still reads the whole
paper (Sprint 16 plan, Q5 = 2).

Kept verbatim so each review can be traced to the instructions it ran
under. This is Sprint 14's review prompt (`manifests/f117_reviews/REVIEW_PROMPT.md`,
kept as it ran) with the rules Sprint 15's reads need, added 2026-11-01
(Sprint 15 Task H, step 1). One Sonnet 5.5 reviewer per group; the
coordinator (Opus 5.5) signs off and runs the cross-group pass; the team
lead decides every certainty change on a stored assertion.

What is added:

- the cross-group rule F117 used (2026-10-30): a textbook-standard
  result is background and is never by itself the reason for LOW (F129);
- a value read by eye from a figure (`from_figure`) is never HIGH on the
  figure alone (F116);
- OCR text from a page of a stored PDF grades as text-layer text; OCR
  text from an image file that is not inside a PDF is HIGH only when
  another source corroborates it, otherwise MEDIUM at most (plan Q3,
  F115);
- the paper texts are page by page, and a thin page carries its OCR text.

Amended 2026-11-01, 7:45pm, after g113-r1's review (groups g062-r1,
g064-r1, g076-r1 and g113-r1 ran on the text before it): the reviewer of
g113-r1 read the textbook rule as allowing HIGH on "proved result" for a
textbook identity the paper states without proving it. The rule's last
paragraph below now says it does not. That case is F129's, which waits for
the team lead.

Amended again 2026-11-01, 8:40pm, after g115's review (g116 and g117 were
already running): its reviewer graded HIGH a theorem whose proof uses
another paper's theorem as a step, because the proof is in the paper.
The "proved result" basis below now says that such a proof is LOW.

---

You review one group of F114's first-pass reads before they enter the
Evidence Based DB. A reader read each paper in full, every figure
included, and proposed assertions, each with quotes, an anchor, a result
type and a suggested certainty. Every quote is already verified verbatim
against the paper by script. Your job is judgment: does the passage
settle each grade the item asks about?

GROUP is given in your task message. Read these, and write only the one
output file:

- `D:\Data\Harold\EvidenceBasedDB\work\f114\review\items\GROUP.json`:
  the items to decide.
- `D:\Data\Harold\EvidenceBasedDB\work\f114\texts\<record>.txt`: each
  paper's full text, the same text its reader had. Pages are separated by
  form feeds; a page whose text layer is empty starts "[OCR text of page
  N]" and holds the OCR text instead.
- The paper's PDF, at the path in the group's reader file
  `D:\Data\Harold\github\EvidenceBasedDB\manifests\sprint13_g_reads\group_GROUP.json`
  (`file`), when an item rests on a figure: get the page's image with
  `python -X utf8 D:\Data\Harold\github\EvidenceBasedDB\scripts\render_page.py "<file>" <page> --group GROUP`
  and view the image at the path it prints with the Read tool. It is the
  image the reader rendered when there is one (F139, Sprint 16: render
  once); add `--dpi 150` when the labels are too small to read. Keep any
  other scratch file in a folder of your own under
  `D:\Data\Harold\EvidenceBasedDB\work\f114\review\tmp_GROUP\`.
- Output: `D:\Data\Harold\EvidenceBasedDB\work\f114\review\decisions\GROUP.json`.

Write nothing else, and nothing in the repository. Never use a hook
override token (any "allow_..." word or comment in a command).

Read every item's passage in the paper text, in context: find the quotes
(Grep is quickest), then read the surrounding paragraph, and for a
theorem, its statement, its conditions and whether the paper proves it.
There is no budget: every item gets a decision from the passage, never
from the reader's suggestion alone. Setup items too: a quote that is
verbatim can still be lifted from a passage that says something else.
In your reply, name any item decided without reading its passage (there
should be none).

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
  only cited is not this basis. A proof in the paper that uses a
  specific other paper's theorem or lemma as a step ("we use the
  following theorem from [64]") is not this basis either: decide it
  `"low"` and name the cited result. A textbook-standard tool (Hoeffding,
  a union bound) used as a step does not make it LOW. A bound argued
  informally is not this basis.
- **stated limit**: a limitation or caveat the paper itself states about
  its own work: what its results do not cover. What a measurement found,
  even a negative finding or a failure ("did not improve", "failed on
  the larger instances"), is a measured result, not a stated limit
  (Sprint 16, F135: the reader prompt says the same).

Everything else is LOW: a measured result (an experiment or simulation
outcome), the authors' claim or interpretation, a cited result, a field
statement, a vendor's claim about its own product, a theoretical result
that is not proved in this paper or whose conditions the quotes drop.

**A textbook-standard result is background.** When a paper restates a
standard result (the no-cloning theorem, Hoeffding's inequality, the
QFT's gate count, the cost of contracting a matrix product state), that
it is standard is never by itself the reason for LOW. Grade it on how
the paper states it. A specific paper's lemma or derivation taken by
citation does make an item LOW. The rule does not supply a basis: a
textbook identity the paper states without proving it is not a "proved
result". Decide it `"low"`, and start its `why` with "textbook, stated
not proved (F129)"; the team lead decides that class.

**A stated limit keeps its true type.** A limit the paper states on its
own measured result is HIGH on "stated limit" whatever its
`result_type`; a Sprint 15 reader changed the type to pass the reader
check (F135). From Sprint 16 the reader keeps it "measured"; name the
type it should have in `why` when it does not.

**A value read from a figure** (the reader marked it `from_figure`; its
value starts "Read from Figure N") is never HIGH on the figure alone,
however clear the plot. Check its reading against the rendered page: if
the value misreads the figure, say so in `why` and decide `"low"`.

**OCR text.** A quote from a stored PDF's page that had no text layer
(its anchor says "OCR") grades as text-layer text. A claim from an image
file that is not inside a PDF is HIGH only when another source
corroborates it, named in `why` as "corroborated by <record>"; otherwise
decide `"low"` (the coordinator records MEDIUM at most).

## Item kinds and what to decide

Each item has `kind`, `id`, `record`, `anchor`, `value`, `quotes`,
`result_type`, `suggested`, `suggested_basis`, `reader_reason`. A
`changed` or `stored-high` item also has `stored_value` and
`stored_quotes`: the assertion as the store holds it now. A reader who
confirmed a stored assertion may leave `value` and `quotes` empty; then
decide on `stored_value` and `stored_quotes`.

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
`"keep"` for a changed item). If a value holds two claims that the
passage settles differently, say so in `why`, and grade it by the
weaker.

## Output

One JSON object, keyed by item id, every item present:

```json
{
 "some-id": {"decision": "high", "basis": "proved result", "why": "Theorem 2, Section 3, p.6: stated with its conditions and proved in Appendix B"},
 "other-id": {"decision": "low", "why": "a simulation outcome on one dataset, a measured result"},
 "changed-id": {"decision": "accept", "grade": "low", "why": "the narrowed value matches Table 2; a measured result"}
}
```

Write the output file with the Write tool. `why` names where the paper
settles it (section, theorem, page) or what it lacks. Short sentences.
Then reply with one line: the counts of high, low, accept and keep, and
the minutes you took.
