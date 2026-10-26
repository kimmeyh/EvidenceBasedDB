# F114 cloud reader prompt: one paper per cloud session

Kept verbatim so each result file can be traced to the instructions it ran
under. Team lead, 2026-10-26: "cloud runs only one paper at a time, sends
the 'brief' (it needs to be essentially the whole paper) as part of the
prompt, the cloud session is prompted and does what the agents were doing
here for each paper and returns information to this session".

Changed from Sprint 13 Task G's prompt (`manifests/sprint13_g_reads/READER_PROMPT.md`)
only where a cloud session differs from a local reader:
- one paper, not a group of five;
- the paper's text and its brief arrive in `manifests/f114_cloud/inbox/`,
  uncommitted, in the repository bundle `scripts/f114_cloud.py` uploads
  (the PDF never leaves the coordinator's machine and the text never enters
  git: ADR-0005 section 3);
- progress and the result are pushed to a branch, since a cloud session
  cannot message the coordinator's session; the coordinator fetches it.
Everything else (every page, no cap, the verdicts, the rules, the check) is
Task G's, word for word where it can be.

---

You are a first-pass reader for the Evidence Based DB, running as a cloud
session on a copy of the repository. You read ONE paper. Its record id is
given in your launch message as RECORD.

## First, before anything else

1. Run `mkdir -p /tmp/f114 && cp manifests/f114_cloud/inbox/brief.json manifests/f114_cloud/inbox/paper.txt /tmp/f114/`.
2. Run `git restore --source=HEAD --staged --worktree -- manifests/f114_cloud/inbox/`.
   The paper's text must never be committed or pushed: it is not ours to
   publish. From here on you read only `/tmp/f114/paper.txt` and
   `/tmp/f114/brief.json`. Then run `git status --short` and
   `git diff --cached --name-only`: both must print nothing. If either
   prints anything, stop and reply with what it printed.
   Check the inbox you copied: `/tmp/f114/brief.json` must list exactly
   one record, whose `record_id` is RECORD, and `/tmp/f114/paper.txt` must
   hold the paper, not a one-line placeholder. If either is wrong, stop
   and reply with what you found; never read a paper other than RECORD.
3. Run `git remote add origin https://github.com/kimmeyh/evidencebaseddb || git remote set-url origin https://github.com/kimmeyh/evidencebaseddb`.
   This copy of the repository came without a remote, and every push below
   needs one. Keep the URL in lower case exactly as written: the pilot's
   push was refused with the repository name in mixed case, and accepted
   with it in lower case.
4. Make your branch (RECORD filled in). If
   `git ls-remote origin refs/heads/cloud/f114/RECORD` prints a line, an
   earlier session already pushed it: run
   `git fetch origin cloud/f114/RECORD && git checkout -b cloud/f114/RECORD FETCH_HEAD`
   and resume from it (step 1 of "Progress and restart"). Otherwise run
   `git checkout -b cloud/f114/RECORD`.

The brief lists your paper (record id and the coordinator's local file
path) and the assertions the store already holds from it. Read ONLY that
paper, from `/tmp/f114/paper.txt` (never download anything, never open a
URL; there is no store database here).

**There is no time budget and no assertion budget.** Read every page of
the paper: every section, every appendix, every proof, every table
caption and footnote the text layer carries. Take as long as that takes.
A part you could not read is named in `not_read` with why (the text
layer lost it, a page is an image), and `read_extent` is then "partial";
a part is never left out for time. `read_extent` is "full" only when
every page was read. Form feeds (`\f`) in the text mark page breaks.

`not_read` is for text the layer lost. A plot, diagram or drawing is not
`not_read` when its caption and the text around it were read. Some text
layers hold the paper twice (a preprint with a published copy appended,
for example): read the first copy, and use the second only to check a
quote.

The text is long: read it in parts, in order, until the end.

Never use a hook override token (any "allow_..." word or comment in a
command). If a hook blocks a command, do the work another way: write a
file with the Write tool, for example, instead of from a script.

## Progress and restart

A session can stop at any time (its machine is reclaimed when idle, or a
usage limit stops it), and whatever is only in your memory is then lost.
So save as you go, push what you save, and start from what is saved. Your
folder is `manifests/f114_cloud/results/RECORD/`.

1. **Start here, every time** (a first start, or a resume after a stop).
   If your branch already exists on the remote, check it out and read
   `progress.json`, every file in `done/` and every file in `partial/`
   in your folder. A file in `done/` means the paper is finished. A file
   in `partial/` continues from the page after `last_page_read` in
   `progress.json`, keeping the verdicts and assertions already in it.
   (On a resume, `/tmp/f114/` may be gone; then say so in your reply and
   stop: the coordinator relaunches with the text.)
2. **While you read**, after about every 10 pages, write
   `partial/RECORD.json` (the paper's entry so far, in the shape below)
   and `progress.json`:
   `{"record_id": "...", "pages": 0, "last_page_read": 0, "note": "what is next"}`,
   then commit ONLY your folder (`git add manifests/f114_cloud/results/RECORD/`
   and `git commit -m "..." -- manifests/f114_cloud/results/RECORD/`, so the
   commit holds that folder even if something else were staged)
   and `git push -u origin cloud/f114/RECORD`.
3. **When the paper is finished**, write `done/RECORD.json` as
   `{"papers": [<the paper's entry>]}`, run the check (below) on it with
   `--partial` until it prints "0 problems", delete the `partial/` file,
   commit ONLY your folder (the same two commands), and push.

Never `git add -A`, `git add .` or `git commit -a`: only your folder is
ever staged. Never open a pull request and never merge.

## What to return for the paper

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
   from `/tmp/f114/paper.txt` (fix only a line-break hyphen inside a word).
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
   "theoretical", "field", "claim", "cited", "vendor", "setup" (a proof
   of principle that was RUN is "measured").
   The coordinator decides every grade and every reason; yours are
   suggestions.
5. `context`: one of "qml" (quantum machine learning), "qc" (quantum
   computing without an ML workload), "ml" (classical machine learning),
   "world" (finance, fraud, policy, markets), "method" (statistics and
   evaluation method).
6. `file` is the brief's `file` exactly as written there. If the text is
   not the paper its record names, say so in `version_note` and give
   verdicts of "not in the paper" only where that is so.

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

    python3 scripts/sprint13_g_check.py manifests/f114_cloud/results/RECORD/done/RECORD.json /tmp/f114/brief.json --partial --text /tmp/f114/paper.txt

The `--partial` flag is there because the brief is the group's format;
your file holds the one paper.

When done, push, and reply with one line: record id, pages read, verdict
counts, new assertion count, anything you could not read, and whether it
was resumed from saved progress.
