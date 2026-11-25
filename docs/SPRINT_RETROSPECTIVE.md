# Sprint Retrospective Guide

Adapted 2026-08-30 from spamfilter-multi's SPRINT_RETROSPECTIVE.md via hsbc-quantum-fraud-2026. The source's 14-category x 4-role structure and 7-step protocol are preserved in shape and EXTENDED to 16 categories; examples are adapted to this repository (Sprint 1 Task H, F1, 2026-09-16).

## Rules

- Retrospectives are MANDATORY for every sprint, conducted after Phase 6 (PR updated) and BEFORE the PR is marked ready.
- **A retrospective is NEVER complete unless ALL 16 categories are addressed by ALL 4 roles.** The team lead wears Product Owner, Scrum Master, and Lead Developer; Claude provides the Development Team perspective. A role with nothing to say writes `No issues -- expectations met.` explicitly; silence is not acceptable.
- Record the team lead's words VERBATIM; never paraphrase or substitute Claude's draft for them.

## The 7-Step Protocol (run in order; do not collapse, reorder, or skip)

1. **Send the prompt**: ask the team lead for PO/SM/LD feedback across all 16 categories (combined per-category lines acceptable), noting that Claude is drafting its own role's feedback in parallel.
2. **Draft in parallel**: Claude writes its Development Team feedback for all 16 categories into `docs/sprints/drafts/SPRINT_N_RETROSPECTIVE_claude_draft.md` while waiting.
3. **Record verbatim**: paste the template into `docs/sprints/SPRINT_N_RETROSPECTIVE.md`; the team lead's exact words per category; Claude's lines from the draft. Exit gate: 16 categories, 4 roles, no placeholders.
4. **Combine and display** in chat, both feedback sets together per category.
5. **Propose improvements** from the combined feedback, each as `i1` to `iN` in the shape of "Presenting improvements, questions and decisions" below. Display; do NOT auto-apply.
6. **Team lead disposes each**: "i1. a i2. c ..." or "all as recommended". Record in an "Improvement Decisions" section.
7. **Apply**: now-items as commits on the sprint branch; backlog-items to ALL_SPRINTS_MASTER_PLAN.md; skips noted. Then the mandatory completion updates (master plan Last Completed Sprint, summary doc scheduling; the CHECKLIST reconciliation ended after Sprint 18, team lead q19 = a, 2026-11-24). THEN `gh pr ready`.

## Presenting improvements, questions and decisions (AUTHORITATIVE)

Team lead, 2026-11-07. It applies to retrospective improvements, and to
every other question or decision put to the team lead (a plan question, a
Manual Validation decision, an F140-style recommendation). The goal it
serves: effective long-term, as efficient as reasonably possible, and in
line with this repository's architecture, its agile practice and its
risk-based, automated testing.

**Stored in full before it is shown (F151, Sprint 19; team lead
2026-11-22: "please store all quesitons, decisions and Improvement in
full ... always re-ask with the full contents every time").** From Sprint
19 on, every item is written first to `docs/sprints/SPRINT_N_DECISIONS.md`
as a `## qN.` or `## iN.` entry, with an `- Asked:` date and every field
below. The answer goes under it, verbatim, as `- **Answer** (team lead,
YYYY-MM-DD): "..."`, the date read from the clock; a fact that changes
after asking goes in a dated `- Changed since asked` line, never an edit.
Every message that needs an answer re-shows EVERY open entry, pasted from
the file unchanged. `tests/test_sprint_documents.py` fails on an entry
without a field, without exactly one "(Recommendation)", or with a reused
id; the Stop hook blocks a reply that asks an unstored item, leaves out an
open entry, or changes an entry's text. A retrospective's i items are
stored there too; the retrospective's Improvement Decisions table names
them.

Each item:

```
iN. <brief title>          (qN for a question or decision outside a retrospective)
- What it is: <the change, in one or two sentences>
- What it prevents: <the defect or waste it stops, and at which point:
  the sprint process, a backlog item, a sprint card, development, or
  testing; the earlier, the better>
  AND/OR What it catches: <what it finds once it has happened>
- Prevention or control: <prevention (preferred) or control>. Prevention
  keeps the defect from ever being made: a better requirement or card, a
  design that makes it impossible by construction, a better development
  method. A test, check or review that finds the defect after it is made
  is a control, however early it runs (team lead, 2026-11-07, q11).
- Long-term value: <what it keeps giving, sprint after sprint>
- Evidence: <how many times it happened, the time it cost, the
  efficiency it would gain, and how that was measured>
- Extends: <the rule, checklist item or test it builds on> (when one does)
- Effort: <cost to build (minutes, files)> AND <cost to run, and how
  often: per commit, per gate, per apply, per sprint, per CI run> (team
  lead, 2026-11-07, q13)
- Options:
  - a. (Recommendation) <option>. Pro: <...>. Con: <...>.
  - b. <option>. Pro: <...>. Con: <...>.
  - ...
```

The options usually come from this set, in order of preference:

- the best option done now, or carded, by its effort;
- the best option carded for the next or a later sprint, because of its
  time or the number of files it changes;
- the next-best alternative, and the one after it;
- skip this sprint, but track it in case it happens again;
- skip.

Exactly one option is marked "(Recommendation)". A yes/no decision is
`a. Yes` and `b. No`, never a question titled yes/no over its options.
The team lead answers "i1. a i2. c q1. b" or "all as recommended", so
every item needs a number and every option a letter.

The team lead's example (2026-11-07, verbatim):

```
  i1. A refusal test stubs what the refusal protects
  - What it is: a Phase 4 checklist line: a test of a refusal replaces the action the refusal blocks (a run, a write, a device client) with a stub that
    fails at once.
  - What it prevents: a red proof that removes the refusal and then does the real action. The --tests proof started test runs inside test runs from
    16:29 to 17:52. Two runner refusal tests still run against real paths, so their proofs would write into experiments/phase2/results/ or open a device
    client.
  - Long-term value: every future refusal proof is safe to run, locally and in CI. It protects evidence files and metered seconds.
  - Prevention or control: prevention.
  - Extends: the Phase 4 per-term item.
  - Effort: about 5 minutes, one file.
  - Alternatives:
    - a. (Recommendation) A checklist line (the proposal). Pro: 5 minutes, and it applies from the next task. Con: nothing enforces it.
    - b. A test that fails a refusal test that has no stub. Pro: enforced. Con: about 60 minutes. A source scan cannot tell which action a refusal
      blocks, so it would give false results.
    - c. A time limit on each proof run. Pro: stops a run that does not end. Con: it is a control, not prevention. It does not stop a write or a device
      call that happens before the limit.
```

Until 2026-11-07 a proposal was Title / Source / Type / Effort /
Recommendation and a decision was a numbered list answered by a digit
with a "Recommend N" line; Sprints 1 to 16 used that form.

## The 16 Mandatory Categories

1. **Effective while as Efficient as Reasonably Possible** -- right outcome, least reasonable effort, workflow followed, rework counted.
2. **Testing Approach** -- did automated tests catch problems before validation; coverage adequate for the scope (for this project: schema CHECK-constraint tests proven to fail by injection, export-determinism tests, ingestion-path tests).
3. **Effort Accuracy** -- estimates vs actuals per task; variance patterns.
4. **Planning Quality** -- task clarity, acceptance-criteria sufficiency, dependencies, scope fit.
5. **Model Assignments** -- were subagent/model choices right (reviews, research agents, main-loop work); escalations needed.
6. **Communication** -- narration, timely blocker reporting, commit/PR clarity.
7. **Requirements Clarity** -- ambiguity encountered; hidden requirements surfaced mid-sprint.
8. **Documentation** -- docs updated with the work; prereg amendments recorded properly; reference docs current.
9. **Process Issues** -- errors, blockers, tooling friction, anything that belongs in a troubleshooting note or hook.
10. **Risk Management** -- risks identified vs materialized (schema/provenance correctness, team-lead adjudication cost per record, context/session continuity); mitigation effectiveness.
11. **Next Sprint Readiness** -- blockers for next sprint; master plan current.
12. **Architecture Maintenance** -- for this project: ADR integrity (does anything in the schema or export diverge from an ACCEPTED ADR's spine; are amendments logged), export-determinism adherence.
13. **Minor Function Updates for the Next Sprint Plan** -- sub-hour items to fold inline into Sprint N+1. Format: `[ROLE] <one-line> -- target: Sprint N+1 plan, est: <Xm>`.
14. **Function Updates for the Future Backlog** -- larger items for ALL_SPRINTS_MASTER_PLAN.md "Next Sprint Candidates" with a new F#. Format: `[ROLE] <title> -- estimated: <X>, priority: <N>, depends on: <list>`.
15. **Assigned Coding Agents Quality** (team lead addition, Sprint 2) -- quality of delegated subagent/background-agent output: first-pass correctness, spec adherence, rework required.
16. **Questions to be discussed before ending the sprint** (team lead addition, Sprint 2) -- open items requiring discussion before close; `none` is an acceptable and explicit answer.

## Mandatory Feedback Template (copy verbatim into `docs/sprints/SPRINT_N_RETROSPECTIVE.md`)

```markdown
## Sprint N Retrospective Feedback

### 1. Effective while as Efficient as Reasonably Possible

- **Product Owner**: [feedback]
- **Scrum Master**: [feedback]
- **Lead Developer**: [feedback]
- **Claude Code Development Team**: [feedback]

### 2. Testing Approach
[same four-role block]

### 3. Effort Accuracy
[same four-role block]

### 4. Planning Quality
[same four-role block]

### 5. Model Assignments
[same four-role block]

### 6. Communication
[same four-role block]

### 7. Requirements Clarity
[same four-role block]

### 8. Documentation
[same four-role block]

### 9. Process Issues
[same four-role block]

### 10. Risk Management
[same four-role block]

### 11. Next Sprint Readiness
[same four-role block]

### 12. Architecture Maintenance
[same four-role block]

### 13. Minor Function Updates for the Next Sprint Plan
[same four-role block]

### 14. Function Updates for the Future Backlog
[same four-role block]

### 15. Assigned Coding Agents Quality
[same four-role block]

### 16. Questions to be discussed before ending the sprint
[same four-role block]

## Improvement Decisions

| # | Title | Source | Type | Effort | Decision (now/backlog/skip) |
|---|---|---|---|---|---|
```

## Transition note

**REWORKED 2026-09-16 (Sprint 1 Task H, F1).** This note originally
described the consumer repository's OWN Sprint 1 (closed 2026-08-30 under
an earlier lightweight retro before this guide was adopted there) --
misleading here, since this repository's own Sprint 1 has not yet closed
and never ran under that earlier lightweight form. The full 16-category
protocol applies to this repository's Sprint 1 and every sprint after it,
with no transition exception.
