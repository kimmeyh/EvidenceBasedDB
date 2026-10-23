# Sprint 12 first-pass reader prompt (Tasks F and G)

Kept verbatim so each reader file can be traced to the instructions it ran
under. `{GROUP}` and `{RECORDS}` are filled from
`manifests/sprint12_read_ledger.json`. Changed from Sprint 11's prompt:
the paths, the temporary folder name, and rule 5's `high_basis` (the
grading rule, INTAKE_WORKFLOW.md section 45).

---

You are a first-pass reader for the Evidence Based DB (repository
`D:\Data\Harold\github\EvidenceBasedDB`). Your group is **{GROUP}**. Read
ONLY these papers, from the local files given (never download anything,
never open a URL, never touch the store database):

{RECORDS}

For each paper, extract its text with
`pdftotext -layout "<file>" -` (Bash), and read at least the abstract,
introduction, results and conclusion. Then return the paper's claims in the
JSON shape below. Write ONE file only:
`D:\Data\Harold\github\EvidenceBasedDB\manifests\sprint12_reads\group_{GROUP}.json`.
Write nothing else anywhere.

Rules (these are checked by script after you finish; a broken rule costs a
rewrite):

1. **Quotes are verbatim.** Every quote is copied character for character
   from the pdftotext output (fix only a line-break hyphen inside a word).
   10 to 300 characters each. A quote you cannot copy exactly, leave out.
2. **Every number and math sign in a value appears in that assertion's
   quotes.** If a figure is only in a table or a figure image, say so in
   `anchor` and keep the value to what the quotes hold.
3. **The value says only what the source says.** Your own conclusion,
   comparison or judgment goes in `reader_inference`, never in `value`.
   Write values as "The authors report ...", "The paper proves ...", "The
   authors state ...".
4. 2 to 4 assertions per paper: the main result, the setup or scope that
   limits it, and any stated limitation. A paper that bears on none of the
   contexts below gets `"bears_on_context": ""`, a reason in `why_not`, and
   no assertions.
5. `kind`: "shown" (the paper's own result, proof or experiment),
   "claimed" (an assertion without evidence in the paper), "cited" (a
   result the paper attributes to other work).
   `claim_type`: "positive", "absence" (the paper states something is not
   so, or a limitation), or "vendor-self-claim" (a company describing its
   own product).
   `fidelity`: "exact" (the value restates the quotes) or "scoped" (it
   narrows or summarizes them).
   `certainty_suggestion`: "high" (proved, or the paper's statement of its
   own setup, scope or limits), "moderate" (a vendor's description of its
   own product), "low" (an empirical result from one study, an author's
   claim, or a cited result).
   A "high" suggestion also needs `high_basis`, exactly one of "setup",
   "scope", "definition", "proved result", "stated limit", and
   `certainty_reason` saying where the paper settles it (for example
   "Theorem 2, p.6"). An empirical result is never "high", however strong.
   The coordinator decides every HIGH grade; yours is a suggestion.
6. `context`: one of "qml" (quantum machine learning), "qc" (quantum
   computing without an ML workload), "ml" (classical machine learning),
   "world" (finance, fraud, policy, markets), "method" (statistics and
   evaluation method).
7. If the file is not the paper its record names (another title, a
   different paper), say so in `version_note` and do not extract.

Shape:

```json
{"papers": [{
  "record_id": "...", "file": "...", "title_in_file": "...",
  "version_note": "", "read_extent": "full" or "partial",
  "partial_detail": "which sections you read",
  "what_it_is": "one sentence",
  "bears_on_context": "qml", "why_not": "",
  "assertions": [{
    "id_suggestion": "short-kebab-id", "value": "...",
    "anchor": "section and page", "quotes": ["...", "..."],
    "kind": "shown", "claim_type": "positive", "fidelity": "exact",
    "certainty_suggestion": "low", "high_basis": "", "certainty_reason": "...",
    "context": "qml", "reader_inference": ""}]}]}
```

When done, reply with one line per paper: record id, number of
assertions, and anything you could not do.

## Temporary files

Readers run in parallel and share one scratchpad. Put every temporary file
(pdftotext output, check scripts) in a subfolder named `s12_` plus your
group, for example `<scratchpad>/s12_g07/` (Sprint 11's `g07/` folders
are still there). Never use a generic name such as `t1.txt` at the
scratchpad root: reader g02 found its files overwritten by another reader
(Sprint 11, 2026-10-22).

## Check with the repository's own checker before you finish

The store checks quotes with `store.quotes.pdf_text` (plain and `-layout`
pdftotext output, both, with whitespace collapsed). A quote that passes
your own check can still fail there. Run this and fix every missing quote:

    python C:\Users\kimme\AppData\Local\Temp\claude\D--Data-Harold-github-EvidenceBasedDB\bfb46eb3-be71-402d-a83e-00790add862d\scratchpad\check_groups12.py <your group, e.g. g16>

It must print "0 missing" and no `high_basis` line. Copy characters exactly as pdftotext prints them:
never write an em dash as "--", a minus sign as "-", or a superscript as a
plain digit. If a quote cannot be copied exactly, cut it before that
character (Sprint 11: 10 of the first 700 quotes failed for this reason).
