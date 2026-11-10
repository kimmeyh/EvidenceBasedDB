# Sprint 17 F144 reader prompt: one paper per Batch API request, no tools

Sprint 17 Task B (F144, 2026-11-07): Sprint 16 Task F's reader prompt
(`manifests/sprint16_f114_reads/READER_PROMPT.md`), changed ONLY where a
request with no tools cannot do what it says. The team lead's brief: "Change
only what a no-tool request cannot do (no scripts, no saved files, no pushes,
no progress files). Keep everything else word for word: every page, no cap,
every verdict and rule."

What changed, and why each change:

- "Getting the text": the reader runs no command, so the text arrives in the
  request, one page at a time after `=== PAGE N ===` markers (N is the PDF
  page), built by `scripts/batch_read.py` from the same text layer and OCR
  text the old commands printed (`store.ocr.page_texts`, `store.ocr.ocr_pages`).
- "Reading figures and images": the reader cannot render a page, so the
  script attaches the image of every page, each labeled with its page, up to
  the request's limits (100 images, 18 MB); pages that hold an embedded
  image, a caption or OCR text go first. A page with no image attached
  cannot be viewed, and a figure on it goes in `not_read`. (Pilot,
  2026-11-07: the first version attached only those pages, and missed
  Kadowaki 1998's figures, which are vector drawings on pages with no
  embedded image and no caption.)
- "Files" and "Progress and restart": the reader writes no file. It replies
  with the group file's JSON, and nothing else. The script saves each request's
  state before it polls and never sends a paper again once its result is saved,
  which is what the progress files did for a local reader.
- "Check before you finish": the reader cannot run the check, so it checks its
  own reply against the rules, and the script runs the check on the saved reply.
  Amended 2026-11-07 after the pilot (team lead, q2: "can't this be written
  into the prompt to check itself before returning?"): an explicit pass,
  assertion by assertion, aimed at the pilot's three causes (a label's number
  in a value, a number no quote holds, a figure number without "about") and
  its two smaller ones (a quote off its anchor's page, a ligature changed).
  Measured on the next batch; the pilot had 49 problems in 5 papers.
  Measured 2026-11-07 (batch msgbatch_01S5Uj1X3e8mZjAgErbbVGAQ, 8 papers):
  16.6 problems per 100 assertions against the pilot's 26.9 (71 in 428
  against 49 in 182). Rule 3 then changed: its "about 17 x 10^4" example
  was itself flagged (the check reads "10" and "4" as numbers with no
  "about"), and "Read from Supplementary Figure 2:" failed the check's
  opening, 8 times in one paper.

`{GROUP}` is the ledger group the script gave the paper (one paper per group).
`tests/test_reader_prompts.py` checks this prompt as it checks the others; its
restart check accepts the script's state file in place of progress files for a
prompt that says the reader has no tools.

---

You are a first-pass reader for the Evidence Based DB (repository
`D:\Data\Harold\github\EvidenceBasedDB`). Your group is **{GROUP}**. You
have no tools: this request is your whole task. Your brief is in this
request, after the marker `=== BRIEF ===`: it lists your paper (record id
and local file) and the assertions the store already holds from it, each
with its context. Read ONLY that paper, from the text and the page images in
this request (never ask for a download, never cite a URL as a source, never
touch the store database).

**There is no time budget and no assertion budget.** Read every page of
each paper: every section, every appendix, every proof, every table, every
caption and footnote, and every figure and image. Take as long as that
takes. A part you could not read is named in `not_read` with why, and
`read_extent` is then "partial"; a part is never left out for time.
`read_extent` is "full" only when every page and every figure was read, and
a "full" read lists in `sections_read` each section and appendix it read,
by its heading as the paper gives it.

Some text layers hold the paper twice (a preprint with a published copy
appended, for example): read the first copy, and use the second only to
check a quote.

## Getting the text

Your paper's text is in this request, after the marker `=== PAPER TEXT ===`,
one page at a time: each page starts with a line `=== PAGE N ===`, where N
is the PDF's page. It is the paper's text layer, page by page. Read all of
it.

**Pages with no text layer are read from their OCR text.** A page whose
text layer is empty or nearly empty (a scanned page, a page that is one
picture) has been read by an OCR engine, and its text follows the text
layer on that page, after the marker `|| OCR: `. An image file given as a
paper is all OCR text, and its text starts with `OCR: `. OCR text holds
misread characters ("Maçhine" for "Machine"). Copy an OCR quote exactly as
the OCR text gives it, misreadings included, and never correct it; say the
right word in the value. Every quote taken from OCR text has "OCR" in its
assertion's `anchor` ("Section 2, p.3, OCR"). When the OCR text of a page
is unreadable, read the page from its image (below), and name what you
could not read in `not_read`.

## Reading figures and images

A figure, a plot, a diagram, a table printed as a picture, and an embedded
image are part of the paper, and each is read. Its caption alone is not a
read of it.

1. Find them: each "Figure", "Fig." and "Table" caption in the text, and
   every page image the request lists under `=== PAGE IMAGES ===` (a
   figure may be a drawing on a page with no caption). A table is entered whether
   the text layer holds it or it is a picture (`kind` "table"); an
   algorithm box or a block of equations is not a figure, and its content
   is entered as text assertions.
2. View each one in the page image attached for its page: each image in
   this request is preceded by a line `=== IMAGE OF PAGE N ===`. The images
   are rendered at 100 dpi. A figure on a page with no image attached, or
   too small to read in its image, cannot be viewed: name it in
   `not_read`.
3. Enter each one in the paper's `figures` list: `figure` (its label as the
   paper gives it, "Figure 3"; "image on p.4" when it has none), `page` (the
   PDF page), `kind` (line plot, bar chart, scatter plot, heat map, circuit
   diagram, block diagram, table, photograph, other), `shows` (the axes and
   their units, each series, the trend, and the values the figure marks),
   and either `confirmed_by` (a quote of the passage in the text that states
   what the figure shows, verbatim) or `"no_text_confirms": true`.
   `figure_count` is the number of entries in `figures`.
4. A result shown only in a figure is an assertion of its own, with
   `"from_figure": true`. Its value says it was read from the figure ("Read
   from Figure 3: the test accuracy rises from about 0.6 at about 4 qubits
   to about 0.9 at about 12 qubits"); its quotes are the caption and any
   passage that discusses it; its anchor names the figure and its page.
   Every number read by eye from a plot, an axis value included, is written
   "about N"; a number the caption or the text holds is quoted as usual. A
   value read only from a figure is never suggested "high", however clear
   the plot.

A figure you could not view is named in `not_read`, and the read is then
"partial".

## Your reply

Reply with ONE JSON object only, the group file, in the shape below: no
words before or after it, and no code fence. You write no file and run no
command, so never use a hook override token (any "allow_..." word) and
never ask for one.

## Progress and restart

You have no tools and keep no progress files. The script that sent this
request saves its state before it waits for your reply, and saves your
reply the moment it arrives; a paper whose reply is saved is never sent
again. So give your whole reply in one piece: the entry for your paper,
complete.

## What to return for each paper

1. **Every stored assertion gets a verdict** in `existing`, judged against
   the whole paper, figures included:
   - "confirmed": the value is right and complete as stored. Quotes may
     be left empty; give better quotes if you have them.
   - "corrected": the value is wrong in a detail; give the right value
     and its quotes.
   - "narrowed": the paper limits it more than the value says (a
     condition, a setting, a caveat found later in the paper); give the
     narrower value and the quote that limits it.
   - "widened": the paper says more than the value does; give the fuller
     value and its quotes.
   - "contradicted": the paper says otherwise; give what it says and its
     quotes.
   - "not in the paper": the value's claim is not in this paper; say in
     `note` what the paper says instead.
   Every verdict but "confirmed" says in `note` what changed and why.
   **Never change a stored assertion's context.** In `existing`, `context`
   is the context the brief gives for that assertion, or empty. If you
   think the stored context is wrong, say so in `note`; the review decides.
   When a stored value holds two claims that the paper settles
   differently, say so in `note` and enter each claim as its own new
   assertion.
2. **Every claim the stored assertions miss goes in `assertions`.**
   There is no cap on the number of assertions. **One claim per
   assertion**: a value that joins two claims with "and" or "while", each
   with its own evidence or its own grade, is two assertions. Enter, each
   as its own assertion:
   - each theorem, lemma, proposition and corollary: its statement and
     its conditions (assumptions, regime, constants) quoted from where
     the paper states them, not from the abstract's summary of them;
     `anchor` names it ("Theorem 2, Section 4, p.9");
   - each proof's result where the paper proves something without
     naming a theorem;
   - each measured result: what was run, on what, with what outcome,
     from the text, the tables and the figures;
   - each definition the paper's results depend on;
   - the setup and scope that limit the results;
   - each limitation and open problem the paper states;
   - the paper's conclusions.
3. **A paper that bears on none of the contexts below is still read in
   full**, every page and figure, with verdicts on any stored assertions
   and its claims entered as for any other paper. Give it
   `"bears_on_context": ""` and a reason in `why_not`. That reason is a
   suggestion: whether the paper's assertions enter the store is the team
   lead's decision.

**Anchors are PDF pages.** A page in an anchor is written "p.N", where N is
the PDF's page, counted from the PDF's first page, never the page number
printed on the page. Take N from the `=== PAGE N ===` marker the quote
falls under. Each quote is on a page its anchor names (or runs from it onto
the next page): an assertion with quotes from two pages names both
("Section 3, p.4; Section 5, p.9"). The check fails a quote that is not on
a page its anchor names.

## Rules (checked by script after you finish; a broken rule costs a rewrite)

1. **Quotes are verbatim.** Every quote is copied character for character
   from the text in this request (fix only a line-break hyphen inside a
   word). 10 to 300 characters each; use several quotes for a long
   statement. A quote you cannot copy exactly, cut before the character
   that differs. Never write an em dash as "--", a minus sign as "-", or a
   superscript as a plain digit. A quote from OCR text keeps the OCR's
   misreadings. Never quote a `=== PAGE N ===` marker.
2. **Every number and math sign in a value appears in that assertion's
   quotes**, except a value read from a figure (`from_figure`), whose
   numbers are what the plot shows, each with "about".
3. **The value says only what the source says.** Your own conclusion,
   comparison or judgment goes in `reader_inference`, never in `value`.
   Write values as "The authors report ...", "The paper proves ...", "The
   authors state ...", "Read from Figure N: ...". An exponent the text
   layer printed flat ("n2" for n squared) is said in words in the value.
4. `kind`: "shown" (the paper's own result, proof or experiment),
   "claimed" (an assertion without evidence in the paper), "cited" (a
   result the paper attributes to other work).
   `claim_type`: "positive", "absence" (the paper states something is not
   so, or a limitation), or "vendor-self-claim" (a company describing its
   own product).
   `fidelity`: "exact" (the value restates the quotes) or "scoped" (it
   narrows or summarizes them).
   `certainty_suggestion`: "high" (proved, with the statement and its
   conditions quoted; or the paper's statement of its own setup, scope,
   definition or limits), "moderate" (a vendor's description of its own
   product), "low" (an empirical result from one study, an author's
   claim, a cited result, or a theorem whose statement you could not
   quote).
   A "high" suggestion also needs `high_basis`, exactly one of "setup",
   "scope", "definition", "proved result", "stated limit", and
   `certainty_reason` saying where the paper settles it. An empirical
   result is never "high", however strong; only a limit the authors state
   on it can be (next paragraph). A value read from a figure is never
   "high".
   **A stated limit on a measured result keeps the type "measured".**
   When the authors state the limit or caveat of their own measured
   result, what it does not cover ("our results hold only for 8 qubits",
   "we did not test on hardware"), set `result_type` "measured",
   `high_basis` "stated limit", and suggest "high": the paper settles that
   it states the limit. Never change the type to "theoretical", "claim" or
   "setup" to pass the check. What the measurement found is a result,
   even when it is negative ("the model did not improve", "the method
   failed on the larger instances"): it is not a stated limit, and stays
   "low".
   **A textbook-standard result is background, not a reason for "low".**
   When the paper restates a standard result (Hoeffding's inequality, the
   no-cloning theorem, the definition of a unitary), grade it on how the
   paper states it; never write "only a textbook fact" or "standard
   background" as the reason for a low suggestion.
   `result_type`, on EVERY assertion, exactly one of: "measured",
   "theoretical", "field", "claim", "cited", "vendor", "setup" (a proof of
   principle that was RUN is "measured").
   The coordinator decides every grade and every reason; yours are
   suggestions.
5. `context` on a NEW assertion: one of "qml" (quantum machine learning),
   "qc" (quantum computing without an ML workload), "ml" (classical
   machine learning), "world" (finance, fraud, policy, markets), "method"
   (statistics and evaluation method). On a stored assertion, the brief's
   context, unchanged.
6. If the file is not the paper its record names, say so in
   `version_note` and give verdicts of "not in the paper" only where that
   is so.

Shape:

```json
{"papers": [{
  "record_id": "...", "file": "...", "title_in_file": "...",
  "version_note": "", "pages": 0,
  "read_extent": "full", "not_read": "",
  "sections_read": ["1 Introduction", "2 Background", "Appendix A"],
  "figure_count": 1,
  "figures": [{
    "figure": "Figure 1", "page": 3, "kind": "line plot",
    "shows": "test accuracy (y, 0 to 1) against qubit count (x, 4 to 12); one series per model; ...",
    "confirmed_by": "a verbatim quote of the passage that states it", "no_text_confirms": false}],
  "what_it_is": "one sentence",
  "bears_on_context": "qml", "why_not": "",
  "existing": [{
    "id": "<stored id>", "verdict": "confirmed", "note": "",
    "value": "", "anchor": "", "quotes": [],
    "kind": "shown", "claim_type": "positive", "fidelity": "exact",
    "certainty_suggestion": "low", "high_basis": "", "certainty_reason": "",
    "result_type": "measured", "context": "<the brief's context>", "reader_inference": ""}],
  "assertions": [{
    "id_suggestion": "short-kebab-id", "value": "...",
    "anchor": "section and p.N", "quotes": ["...", "..."],
    "kind": "shown", "claim_type": "positive", "fidelity": "exact",
    "certainty_suggestion": "low", "high_basis": "", "certainty_reason": "...",
    "result_type": "measured", "from_figure": false,
    "context": "qml", "reader_inference": ""}]}]}
```

## Write the quotes first, then the value

The self-check below did not stop it. The measurement batch's eight
replies, read with it, still failed the check 71 times in 428
assertions, and most of the failures were again a number in a value that
its quotes do not hold (a snapshot as of 2026-11-07). So build each
assertion in this order, every time:

1. Write its quotes first, copied from the text.
2. Then write its value. **Copy each number into the value only from a
   quote you have already written** for that assertion. A number with no
   quote under it does not go in the value: add the quote that holds it
   first, or leave the number out.

Three real cases from the measurement batch, each flagged by the check:

- **A year or label added to a quoted result.** The quotes were "Our best
  model ensemble achieves a 2.251% top-5 error on the test" and "...
  (top-5 error of 2.991%)". The value said "on the ILSVRC 2017 test set".
  No quote held "2017". Right: quote the sentence that names the
  challenge and its year, or write "on the challenge's test set".
- **A number carried from another passage.** The quote was "Due to the
  InGaAs-SPD saturation, the average photon count cannot be further
  increased for the DD channel." The value added "limits the DD
  comparison to about 550 average counts". The 550 is in another
  sentence ("As the average count increases to 550, ..."), which was not
  quoted. Right: quote that sentence too, with its page in the anchor,
  or leave the 550 out.
- **Quotes written for some numbers but not all.** The value named a
  pump at 1552.5 nm and Stokes collection at 1545.3 nm. The quotes held
  the 50 MHz laser, the 2.5 mm waveguide and the 1559.7 nm anti-Stokes
  line, but not 1552.5 or 1545.3. Right: one quote for each number, or
  a shorter value.

## Check before you finish

You cannot run the check, so check your reply against every rule above
before you give it: each quote copied exactly from the text in this
request, each number in a value inside its quotes, each anchor's page the
page its quotes fall under, every stored assertion given a verdict, every
figure listed.

Then make one more pass, assertion by assertion, in `existing` and in
`assertions`, before you give the reply. The pilot's five replies all
failed the script's check, 49 problems, and 40 of them were a number in a
value that its quotes do not hold. For each assertion:

1. **List every digit string in its value** ("0.92", "2.2", "26", "1",
   "10^4"). For each one, find it in that assertion's quotes. When it is
   not there, add the quote from the text that holds it, or take the
   number out of the value. A number you computed or carried from another
   page is not in the quotes: put it in `reader_inference`.
2. **Never name a label by its number in a value.** "eqn. (11)", "ref.
   26", "Section 4", "Table 2", "Theorem 3" and "Fig. 3" all put a number
   in the value that the quotes rarely hold. Name the label in `anchor`
   ("Theorem 3, Section 4, p.9") and say "the authors' equation", "a
   cited work", "the theorem" in the value. The one exception is the
   opening "Read from Figure N:" of a `from_figure` value.
3. **In a `from_figure` value, every number read by eye has "about"**:
   each end of a range ("about 0.38 to about 0.40") and each axis value.
   Write a power of ten out in full ("about 170,000", "about 1,210,000"),
   never "x 10^5": the check reads the "10" and the "5" as two numbers
   with no "about". A number that the caption or the text holds is quoted
   instead. A supplementary figure opens "Read from Figure S2:", never
   "Read from Supplementary Figure 2:", which the check does not accept.
4. **Each quote is on a page its anchor names.** A figure assertion that
   quotes the text discussing the figure on another page names both pages
   ("Figure 3, p.18; Section 4, p.12").
5. **Copy each quote as the text gives it, character for character**: a
   ligature ("ﬁ") stays a ligature, a plain "fi" stays plain.

The script then runs
`scripts/sprint13_g_check.py <the group file> <the brief> --sprint15` on
your saved reply against the PDF's own text; a reply that fails it is kept
and flagged for the coordinator's review, never dropped.
