# Sprint 18 Task C (F146) HIGH audit prompt

Sprint 18 (2026-11-21), team lead q1 = c: Claude Code Sonnet 5.5 subagents
run F146 on the subscription, with no API spend. Kept verbatim so each
result can be traced to the instructions it ran under. The coordinator
writes each run's input with `scripts/f146_checks.py audit --write` and
checks each result with `scripts/f146_checks.py check <run>`.

---

You check HIGH assertions of the Evidence Based DB against their own
quotes. Each item is one assertion: its `value` (what the store says),
its `quotes` (the verbatim passages it rests on, each with its page) and
its `provenance`. Your job is one judgment per item: do the quotes, as
they stand, hold the value?

RUN is given in your task message. Read
`D:\Data\Harold\EvidenceBasedDB\work\f146\audit\in\RUN.json` with the Read
tool (read all of it; it is long), and write only
`D:\Data\Harold\EvidenceBasedDB\work\f146\audit\out\RUN.json`, with the
Write tool. Write nothing else, and nothing in the repository. Never use a
hook override token.

For each item, decide one verdict:

- **"held"**: every claim the value makes is stated by the quotes. A
  paraphrase is fine; a number, a unit, a condition, a scope and a
  direction must match.
- **"held in part"**: some of the value is held and some is not. Name the
  part the quotes do not hold.
- **"not held"**: the quotes do not state the value's claim, state a
  different one, or contradict it.

Judge each item yourself, by reading its value and its quotes side by
side. Do not write or run a script that compares words, numbers or
overlaps for you: a word-overlap check misses a dropped condition and a
changed direction, which are the defects this audit exists to find. Some
items are controls whose answer is known; a scripted judgment fails them.

`why` is one or two sentences naming what the quotes say and, for "held
in part" or "not held", what the value adds or changes. Never leave it
empty.

The output is one JSON object, keyed by item id, with every item of the
input (controls included):

```json
{"<item id>": {"verdict": "held" | "held in part" | "not held", "why": "..."}}
```

Use only the item ids of the input: any other key flags the whole run.
The result is checked once and is never rewritten, so write it once,
complete.

There is no budget: decide every item from its own value and quotes.
Reply with the counts of each verdict, the ids you found hardest, and any
item you decided without reading its quotes (there should be none).
