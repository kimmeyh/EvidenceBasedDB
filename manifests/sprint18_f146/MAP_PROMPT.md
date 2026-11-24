# Sprint 18 Task C (F146) agreement map prompt

Sprint 18 (2026-11-21), team lead q1 = c: Claude Code Sonnet 5.5 subagents
run F146 on the subscription, with no API spend. Kept verbatim so each
result can be traced to the instructions it ran under. The coordinator
writes each run's input with `scripts/f146_checks.py map --write` and
checks each result with `scripts/f146_checks.py check <run>`.

---

You judge pairs of assertions from two different papers in the Evidence
Based DB. A script kept each pair because the two share a context and
much of their wording. Each item holds `a` and `b`, each with its `value`,
its `quotes` (verbatim passages from its paper, with pages) and its
`provenance` (its paper first).

RUN is given in your task message. Read
`D:\Data\Harold\EvidenceBasedDB\work\f146\map\in\RUN.json` with the Read
tool (read all of it), and write only
`D:\Data\Harold\EvidenceBasedDB\work\f146\map\out\RUN.json`, with the Write
tool. Write nothing else, and nothing in the repository. Never use a hook
override token.

For each pair, decide one verdict:

- **"supports"**: the two state the same result, or one states a result
  that makes the other more likely, on the same question.
- **"contradicts"**: on the same question, they cannot both hold (a
  different number for the same quantity under the same conditions, an
  opposite finding).
- **"unrelated"**: they share words but not a question. Most pairs a word
  screen keeps are this, and saying so is a full answer.

For "supports" and "contradicts":

- `quotes`: a list of plain strings. At least one deciding passage from
  each side, each 15 characters or more, copied exactly from that side's
  `value` or `quotes` (the script checks each is verbatim in one side, and
  that both sides have one).
- `independent`: true or false. False when the two are not independent
  evidence: the same work under two records (a listing's abstract and its
  paper, two versions, a survey and its guest column), the same authors
  reporting the same experiment, or one citing the other for this result.
- `independence_why`: one sentence for that answer.

`why` is one or two sentences for every verdict. Judge each pair yourself;
do not write or run a script to judge for you. Some items are controls
whose answer is known.

The output is one JSON object, keyed by item id, with every item of the
input (controls included):

```json
{"<item id>": {"verdict": "supports" | "contradicts" | "unrelated", "why": "...",
               "quotes": ["...", "..."], "independent": true, "independence_why": "..."}}
```

(`quotes`, `independent` and `independence_why` only for "supports" and
"contradicts".) Use only the item ids of the input: any other key flags
the whole run. The result is checked once and is never rewritten, so
write it once, complete. There is no budget. Reply with the counts of each verdict
and of independent ones, and the pairs you found hardest.
