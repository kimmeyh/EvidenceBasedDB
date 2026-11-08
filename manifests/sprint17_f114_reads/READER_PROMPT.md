# Sprint 17 Task E reader prompt: F114's local reads, nothing left for later

Sprint 17 (2026-11-07): Sprint 16 Task F's prompt
(`manifests/sprint16_f114_reads/READER_PROMPT.md`), unchanged except that
every script it runs is the Sprint 17 worktree's
(`D:\Data\Harold\github\EvidenceBasedDB-sprint17`), which holds Task C's
fixes. The main checkout is on another branch during Sprint 17.

Sprint 16 (2026-11-06): Sprint 15 Task H's prompt below, with F139's
changes (Task B): each figure page is rendered through the shared render
cache, so the reviewer opens the same image, and the check records its
run in the group's telemetry file. Task C (F134): a quote through table
cells that hold only a number is now found, so quote such a row as it
reads. Task D (F135): a stated limit on a measured result keeps the type
"measured" (in the grading fields below).

Kept verbatim so each reader file can be traced to the instructions it ran
under. `{GROUP}` is a group of `manifests/sprint13_g_ledger.json`, or a
re-entry group `<g>-r<n>` (F125, Sprint 15 Task C) that holds the records a
reviewed group left unread.

This is Sprint 14 Task F's prompt (`manifests/sprint14_f114_reads/READER_PROMPT.md`,
kept as it ran) with Sprint 14's lessons added, 2026-11-01 (Sprint 15 Task H,
step 1). The rules that carry over: the whole paper is read, every section,
appendix and proof; there is no cap on assertions; each stored assertion
gets a verdict; each theorem is entered with its statement and conditions
quoted. What changes, each from a finding:

- figures and images are read, not skipped (F116): the caption-only
  exemption is removed;
- image-only pages are read from their OCR text, and each quote from them
  is marked "OCR" (F115);
- a "full" read lists the sections and appendices read and every figure
  read (a Sprint 13 cloud reader labeled Boyd "full" after sampling it);
- a reader never changes a stored assertion's context (Sprint 14: a
  reader's nearest-fit context replaced two stored contexts no review had
  decided);
- anchors are PDF pages, and each quote is on the page it cites (F126);
- one claim per assertion (F117 found three assertions that each held two
  claims of different grades);
- a textbook-standard result is background, never by itself a reason for
  a low suggestion (F129);
- a paper that bears on no context is still read in full; its `why_not` is
  a suggestion, and whether it enters is the team lead's decision (Sprint
  14 Manual Validation Q2).

**Amended 2026-11-01, 6:45pm, after Task G's pilot (g114)**: step 2 of
"Reading figures and images" gains the crop command for small panels, and
step 1 says a table in the text layer is entered too. Groups g062-r1,
g064-r1, g076-r1, g113-r1 and g114 to g118 ran on the text before this
amendment; every later group runs on it.

`tests/test_reader_prompts.py` fails if a prompt from Task G's on names a
part-read or a cap, and if a prompt from Sprint 15's on does not require
figures to be read or does not name the OCR text. The check script's
`--sprint15` option checks the new rules.

---

You are a first-pass reader for the Evidence Based DB (repository
`D:\Data\Harold\github\EvidenceBasedDB-sprint17`). Your group is **{GROUP}**. Your
brief is
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\briefs\{GROUP}.json`:
it lists your papers (record id and local file) and, for each, the
assertions the store already holds from it, each with its context. Read
ONLY those papers, from the local files given (never download anything,
never open a URL, never touch the store database).

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

Get each paper's text with
`python -X utf8 -c "import sys; sys.path.insert(0, r'D:\Data\Harold\github\EvidenceBasedDB-sprint17'); from store.quotes import source_text; print(source_text(sys.argv[1]))" "<file>"`
(it handles PDF, HTML and image files). Save it to a file in your scratch
folder and read the file in full, in parts if it is long.

**Pages with no text layer are read from their OCR text.** A page whose
text layer is empty or nearly empty (a scanned page, a page that is one
picture) has been read by an OCR engine, and its text follows the text
layer, after the marker `|| OCR: `. An image file given as a paper is all
OCR text, and its text starts with `OCR: `. To list a PDF's OCR pages and
their text, page by page, run
`python -X utf8 -c "import sys; sys.path.insert(0, r'D:\Data\Harold\github\EvidenceBasedDB-sprint17'); from store.ocr import ocr_pages; t = ocr_pages(sys.argv[1]); [print(f'--- page {n} ---', t.pages[n], sep='\n') for n in sorted(t.pages)]" "<file>"`.
OCR text holds misread characters ("Maçhine" for "Machine"). Copy an OCR
quote exactly as the OCR text gives it, misreadings included, and never
correct it; say the right word in the value. Every quote taken from OCR
text has "OCR" in its assertion's `anchor` ("Section 2, p.3, OCR"). When
the OCR text of a page is unreadable, view the page as a figure (below),
and name what you could not read in `not_read`.

## Reading figures and images

A figure, a plot, a diagram, a table printed as a picture, and an embedded
image are part of the paper, and each is read. Its caption alone is not a
read of it.

1. Find them: each "Figure", "Fig." and "Table" caption in the text, and
   the embedded images `pdfimages -list "<file>"` lists (its `page` column).
   A table is entered whether the text layer holds it or it is a picture
   (`kind` "table"); an algorithm box or a block of equations is not a
   figure, and its content is entered as text assertions.
2. Render each page that holds one, with
   `python -X utf8 D:\Data\Harold\github\EvidenceBasedDB-sprint17\scripts\render_page.py "<file>" <page> --group {GROUP}`,
   and view the image at the path it prints with the Read tool. It renders
   at 100 dpi once per page and keeps the image, so the reviewer opens the
   same one. Add `--dpi 150` when the labels are too small to read. For
   one small panel, render a crop at
   220 dpi: `pdftoppm -r 220 -f <page> -l <page> -x <left> -y <top> -W <width> -H <height> -png -singlefile "<file>" "<your scratch folder>\crop<page>"`,
   where the four numbers are pixels at 220 dpi (the full page at 220 dpi
   is about 1870 by 2420 pixels for US Letter).
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

## Files

Write ONE file only:
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\reads\group_{GROUP}.json`.
Put temporary files, page images among them, in
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\tmp_{GROUP}\`
and nowhere else. Write nothing in the repository.

Never use a hook override token (any "allow_..." word or comment in a
command). If a hook blocks a command, do the work another way: write a
file with the Write tool, for example, instead of from a script.

## Progress and restart

A usage limit can stop you at any time, and whatever is only in your
memory is then lost. So save as you go, and start from what is saved.
Every file below is in your scratch folder,
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\tmp_{GROUP}\`.

1. **Start here, every time** (a first start, a resume, or a new reader
   after a stop). Read `progress.json`, every file in `done\`, and every
   file in `partial\`, if they exist. A record with a file in `done\` is
   finished: do not read it again. A record with a file in `partial\`
   continues from the page after `last_page_read` in `progress.json`,
   keeping the verdicts, assertions and figures already in that file. Say
   in your final reply which records you resumed and from which page.
2. **While you read a paper**, after about every 10 pages, write
   `partial\<record id>.json` (the paper's entry so far, in the shape
   below) and `progress.json`:
   `{"record_id": "...", "pages": 0, "last_page_read": 0, "text_file": "<your text file>", "note": "what is next"}`.
   A short paper is saved at least once, when its last page is read.
3. **When a paper is finished**, write it to `done\<record id>.json` as
   `{"papers": [<the paper's entry>]}` and run the check on that file
   alone, with `--partial` (see "Check before you finish"). Fix it until
   it prints "0 problems". Then delete its `partial\` file.
4. **When every paper is in `done\`**, write the group file from them,
   with the papers in the brief's order, and run the full check.

Write each of these files with the Write tool. Never keep finished work
only in memory.

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
printed on the page. Never count form feeds to find a page: some text
layers hold a form feed inside a page (one paper had 103 parts for 23
pages). Find a quote's page with
`python -X utf8 -c "import sys; sys.path.insert(0, r'D:\Data\Harold\github\EvidenceBasedDB-sprint17'); from store.ocr import page_texts; [print(f'--- page {n} ---', t, sep='\n') for n, t in enumerate(page_texts(sys.argv[1]), 1)]" "<file>"`
(the text layer page by page), or check it with
`pdftotext -f N -l N "<file>" -`. Each quote is on a page its
anchor names (or runs from it onto the next page): an assertion with
quotes from two pages names both ("Section 3, p.4; Section 5, p.9"). The
check fails a quote that is not on a page its anchor names.

## Rules (checked by script after you finish; a broken rule costs a rewrite)

1. **Quotes are verbatim.** Every quote is copied character for character
   from the text output (fix only a line-break hyphen inside a word).
   10 to 300 characters each; use several quotes for a long statement. A
   quote you cannot copy exactly, cut before the character that differs.
   Never write an em dash as "--", a minus sign as "-", or a superscript
   as a plain digit. A quote from OCR text keeps the OCR's misreadings.
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

## Check before you finish

Run, and fix every problem it prints, until it prints "0 problems":

    python -X utf8 D:\Data\Harold\github\EvidenceBasedDB-sprint17\scripts\sprint13_g_check.py <your group file> D:\Data\Harold\EvidenceBasedDB\work\f114\local\briefs\{GROUP}.json --sprint15 --telemetry

For one finished paper in `done\`, add `--partial` after `--sprint15`: it
checks that paper and does not ask for the others.

When done, reply with one line per paper: record id, pages read, sections
read, figures read, verdict counts, new assertion count, anything you could
not read, and whether it was resumed from saved progress.
