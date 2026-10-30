# Sprint 14 Task F reader prompt: F114's local reads

Kept verbatim so each reader file can be traced to the instructions it ran
under. `{GROUP}` is a group of `manifests/sprint13_g_ledger.json`.

This is Sprint 13 Task G's prompt (`manifests/sprint13_g_reads/READER_PROMPT.md`,
kept as it ran) with one change, made 2026-10-30 (Sprint 14 Task F): every
path now points under `D:\Data\Harold\EvidenceBasedDB\work\f114\local\`.
F114's work folder moved out of Temp in Sprint 14 (Q3 = 1), and the old
`s13g` folders are empty. A group's brief here lists only the papers this
reader reads: a group whose other papers were read in F114's cloud sessions
(g079, g103) or are left for a later release (g113) is trimmed to Task F's
papers. The rules, the shape and the check are Task G's, unchanged:

- the whole paper is read, every section, appendix and proof;
- there is no cap on assertions;
- the record's stored assertions are given to the reader, who confirms,
  corrects, narrows, widens or contradicts each from the whole paper;
- each theorem, lemma and proposition is entered with its own statement
  and conditions quoted, so the coordinator can grade it on them.
`tests/test_reader_prompts.py` fails if a prompt from Task G's on names a
part-read or a cap.

---

You are a first-pass reader for the Evidence Based DB (repository
`D:\Data\Harold\github\EvidenceBasedDB`). Your group is **{GROUP}**. Your
brief is
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\briefs\{GROUP}.json`:
it lists your papers (record id and local file) and, for each, the
assertions the store already holds from it. Read ONLY those papers, from
the local files given (never download anything, never open a URL, never
touch the store database).

**There is no time budget and no assertion budget.** Read every page of
each paper: every section, every appendix, every proof, every table
caption and footnote the text layer carries. Take as long as that takes.
A part you could not read is named in `not_read` with why (the text
layer lost it, a page is an image), and `read_extent` is then "partial";
a part is never left out for time. `read_extent` is "full" only when
every page was read.

`not_read` is for text the layer lost. A plot, diagram or drawing in the
page is not `not_read` when its caption and the text around it were read;
a reader who needs a plot's data views that page with the Read tool on the
PDF. Some text layers hold the paper twice (a preprint with a published
copy appended, for example): read the first copy, and use the second only
to check a quote.

Get each paper's text with
`python -X utf8 -c "import sys; sys.path.insert(0, r'D:\Data\Harold\github\EvidenceBasedDB'); from store.quotes import source_text; print(source_text(sys.argv[1]))" "<file>"`
(it handles PDF and HTML). Save it to a file in your scratch folder and
read the file in full, in parts if it is long.

Write ONE file only:
`D:\Data\Harold\EvidenceBasedDB\work\f114\local\reads\group_{GROUP}.json`.
Put temporary files in
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
   keeping the verdicts and assertions already in that file. Say in your
   final reply which records you resumed and from which page.
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
   the whole paper:
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
2. **Every claim the stored assertions miss goes in `assertions`.**
   There is no cap on the number of assertions. Enter, each as its own
   assertion:
   - each theorem, lemma, proposition and corollary: its statement and
     its conditions (assumptions, regime, constants) quoted from where
     the paper states them, not from the abstract's summary of them;
     `anchor` names it ("Theorem 2, Section 4, p.9");
   - each proof's result where the paper proves something without
     naming a theorem;
   - each measured result: what was run, on what, with what outcome;
   - each definition the paper's results depend on;
   - the setup and scope that limit the results;
   - each limitation and open problem the paper states;
   - the paper's conclusions.
   A paper that bears on none of the contexts below gets
   `"bears_on_context": ""`, a reason in `why_not`, and verdicts on any
   stored assertions.

## Rules (checked by script after you finish; a broken rule costs a rewrite)

1. **Quotes are verbatim.** Every quote is copied character for character
   from the text output (fix only a line-break hyphen inside a word).
   10 to 300 characters each; use several quotes for a long statement. A
   quote you cannot copy exactly, cut before the character that differs.
   Never write an em dash as "--", a minus sign as "-", or a superscript
   as a plain digit.
2. **Every number and math sign in a value appears in that assertion's
   quotes.** A figure only in a table image or a figure is named in
   `anchor`, and the value keeps to what the quotes hold.
3. **The value says only what the source says.** Your own conclusion,
   comparison or judgment goes in `reader_inference`, never in `value`.
   Write values as "The authors report ...", "The paper proves ...", "The
   authors state ...". An exponent the text layer printed flat ("n2" for
   n squared) is said in words in the value.
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
   result is never "high", however strong.
   `result_type`, on EVERY assertion, exactly one of: "measured",
   "theoretical", "field", "claim", "cited", "vendor", "setup" (as in
   Task F: a proof of principle that was RUN is "measured").
   The coordinator decides every grade and every reason; yours are
   suggestions.
5. `context`: one of "qml" (quantum machine learning), "qc" (quantum
   computing without an ML workload), "ml" (classical machine learning),
   "world" (finance, fraud, policy, markets), "method" (statistics and
   evaluation method).
6. If the file is not the paper its record names, say so in
   `version_note` and give verdicts of "not in the paper" only where that
   is so.

Shape:

```json
{"papers": [{
  "record_id": "...", "file": "...", "title_in_file": "...",
  "version_note": "", "pages": 0,
  "read_extent": "full", "not_read": "",
  "what_it_is": "one sentence",
  "bears_on_context": "qml", "why_not": "",
  "existing": [{
    "id": "<stored id>", "verdict": "confirmed", "note": "",
    "value": "", "anchor": "", "quotes": [],
    "kind": "shown", "claim_type": "positive", "fidelity": "exact",
    "certainty_suggestion": "low", "high_basis": "", "certainty_reason": "",
    "result_type": "measured", "context": "qml", "reader_inference": ""}],
  "assertions": [{
    "id_suggestion": "short-kebab-id", "value": "...",
    "anchor": "section and page", "quotes": ["...", "..."],
    "kind": "shown", "claim_type": "positive", "fidelity": "exact",
    "certainty_suggestion": "low", "high_basis": "", "certainty_reason": "...",
    "result_type": "measured",
    "context": "qml", "reader_inference": ""}]}]}
```

## Check before you finish

Run, and fix every problem it prints, until it prints "0 problems":

    python -X utf8 D:\Data\Harold\github\EvidenceBasedDB\scripts\sprint13_g_check.py <your group file> D:\Data\Harold\EvidenceBasedDB\work\f114\local\briefs\{GROUP}.json

For one finished paper in `done\`, add `--partial` after the brief: it
checks that paper and does not ask for the others.

When done, reply with one line per paper: record id, pages read, verdict
counts, new assertion count, anything you could not read, and whether it
was resumed from saved progress.
