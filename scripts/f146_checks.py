#!/usr/bin/env python3
"""F146 (Sprint 18 Task C): the HIGH audit and the agreement map, run by Claude Code subagents (team lead q1 = c,
2026-11-19: no API spend). This script never sends anything anywhere and never writes the store: it opens the store
read-only, writes each subagent's input file, and checks each result file the subagent writes. The coordinator runs
the subagents. Results are proposals, kept outside the store and outside git; nothing is applied without the team
lead's decision.

Part 2, the HIGH audit (`audit`): each HIGH assertion's value against its own quotes: "held", "held in part" or "not
held", with why. A HIGH assertion with no quotes cannot be checked by a reader and is listed, never sent.

Part 1, the agreement map (`map`): pairs of assertions from different papers that share a context, kept by a script
screen (it replaces the Haiku 5.5 screen of the card, q1 = c): each assertion's nearest neighbors by idf-weighted word
and number overlap. Each kept pair is judged "supports", "contradicts" or "unrelated", with the quotes that decide it
and whether the two papers are independent (a listing's abstract and its paper, two versions or one group's papers
are not). The dry run prints how many of the store's own judged cross-paper relations the screen keeps (its recall
on the only labelled pairs there are).

F144's rules, as they apply here (q1 = c):
- dry run by default: `--write` writes input files, at most `--max-runs` of them (a cap on work handed out);
- a forecast before any write: items, runs and characters;
- a saved result is never run again: an item whose result is saved is never written into a new input; an item a
  result left out is written again;
- a failing result is kept and flagged, never dropped or overwritten;
- each input carries control items whose answer is known (an assertion paired with another's value, which its quotes
  cannot hold; two assertions from unrelated contexts): a result that gets a control wrong is flagged whole;
- not applicable under q1 = c: the dollar cap, the stop date and the key. No API client is imported; no key is read.

Usage:
  f146_checks.py audit [--size N] [--write] [--max-runs K]
  f146_checks.py map [--top K] [--floor F] [--size N] [--write] [--max-runs K]
  f146_checks.py check <run>          (a result file at WORK/<part>/out/<run>.json)
  f146_checks.py record <run> <tokens> <minutes>
  f146_checks.py status
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from store import script_paths  # noqa: E402
from store.assertion_ids import near_miss  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f146")
AUDIT_VERDICTS = ("held", "held in part", "not held")
MAP_VERDICTS = ("supports", "contradicts", "unrelated")
CONTROLS_PER_RUN = 3
MIN_QUOTE = 15  # characters: a deciding quote is a phrase, not a word ("91" or "e" decides nothing)
STOP = set("""this that with from which their there these those have been were also into than then when where while
each such only over under more most less least between within without about after before other some many much very
paper authors author show shows shown used using uses based both same different given across they them state states
stated report reports reported value values number table figure section appendix page entry dated listed""".split())
TOKEN = re.compile(r"[a-z][a-z0-9\-]{2,}|\d+(?:\.\d+)?%?")
MAX_DF = 300  # a word in more than 300 assertions names no topic


def read_only(db_path=None) -> sqlite3.Connection:
    """The store, opened so that no write can succeed (F146 writes nothing to it)."""
    path = Path(db_path or DB_PATH).resolve()
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


# ---------------------------------------------------------------- state

def state_path() -> Path:
    return WORK / "state.json"


def load_state() -> dict:
    p = state_path()
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"items": {}, "runs": {}}


def save_state(state: dict) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    tmp = state_path().with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(state_path())


def sha(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]


def next_run(state: dict, part: str) -> str:
    """The next run name, past every run in the state and every input file on disk (a write that stopped part way
    must not leave a file that blocks every later write)."""
    prefix = "a" if part == "audit" else "m"
    taken = [int(r[1:]) for r in state["runs"] if r.startswith(prefix)]
    taken += [int(p.stem[1:]) for p in (WORK / part / "in").glob(f"{prefix}[0-9][0-9][0-9].json")]
    return f"{prefix}{(max(taken) if taken else 0) + 1:03d}"


def paths(part: str, run: str) -> tuple[Path, Path]:
    return WORK / part / "in" / f"{run}.json", WORK / part / "out" / f"{run}.json"


# ---------------------------------------------------------------- the store

def assertions(conn) -> dict[str, dict]:
    rows = conn.execute("""SELECT r.id, r.value, r.provenance, r.certainty, COALESCE(f.citation_context, ''),
                                  COALESCE(f.derivation, '')
                           FROM records r LEFT JOIN assertion_fields f ON f.record_id = r.id
                           WHERE r.class = 'assertion'""").fetchall()
    out = {rid: {"id": rid, "value": v, "provenance": p, "certainty": c, "quotes": q, "derivation": d,
                 "contexts": set(), "papers": set()} for rid, v, p, c, q, d in rows}
    for rid, cx in conn.execute("SELECT record_id, context_id FROM record_contexts"):
        if rid in out:
            out[rid]["contexts"].add(cx)
    for pid, aid in conn.execute("SELECT paper_id, assertion_id FROM paper_yields"):
        if aid in out:
            out[aid]["papers"].add(pid)
    return out


def card(a: dict) -> dict:
    return {"id": a["id"], "value": a["value"], "quotes": a["quotes"], "provenance": a["provenance"]}


# ---------------------------------------------------------------- the screen (part 1)

def tokens(text: str) -> set[str]:
    return {t for t in TOKEN.findall(text.lower()) if t not in STOP}


def screen(A: dict[str, dict], top: int, floor: float) -> dict[tuple[str, str], float]:
    """Each assertion's `top` nearest neighbors from another paper that shares a context, by idf-weighted overlap of
    words and numbers (cosine), at or above `floor`. A pair is keyed by its two ids sorted."""
    toks = {rid: tokens(a["value"]) for rid, a in A.items()}
    df = Counter(t for ts in toks.values() for t in ts)
    n = max(len(A), 1)
    idf = {t: math.log(n / d) for t, d in df.items()}
    norm = {rid: math.sqrt(sum(idf[t] ** 2 for t in ts)) or 1.0 for rid, ts in toks.items()}
    post = defaultdict(list)
    for rid, ts in toks.items():
        for t in ts:
            if 2 <= df[t] <= MAX_DF:
                post[t].append(rid)
    kept: dict[tuple[str, str], float] = {}
    for rid in sorted(toks):
        score = Counter()
        for t in toks[rid]:
            if 2 <= df[t] <= MAX_DF:
                for other in post[t]:
                    if other != rid:
                        score[other] += idf[t] ** 2
        near = []
        for other, s in score.items():
            a, b = A[rid], A[other]
            if a["papers"] & b["papers"] or not (a["contexts"] & b["contexts"]) or not a["papers"] or not b["papers"]:
                continue
            near.append((round(s / (norm[rid] * norm[other]), 6), other))
        near.sort(key=lambda x: (-x[0], x[1]))
        for s, other in near[:top]:
            if s >= floor:
                kept[tuple(sorted((rid, other)))] = s
    return kept


def known_pairs(conn, A: dict[str, dict]) -> set[tuple[str, str]]:
    """The store's own judged relations between extracted assertions of two different papers: the recall check."""
    out = set()
    for f, t in conn.execute("SELECT from_assertion_id, to_assertion_id FROM assertion_relations"):
        a, b = A.get(f), A.get(t)
        if a and b and a["derivation"] == b["derivation"] == "extracted" and a["papers"] and b["papers"] \
                and not a["papers"] & b["papers"]:
            out.add(tuple(sorted((f, t))))
    return out


# ---------------------------------------------------------------- controls

def _apart(a: dict, b: dict) -> bool:
    """Two assertions no reading could relate: different papers and no context in common."""
    return not a["papers"] & b["papers"] and not a["contexts"] & b["contexts"] and a["value"] != b["value"]


def _controls(A: dict[str, dict], run: str, part: str, pool: list[str], make) -> list[tuple[dict, str]]:
    """CONTROLS_PER_RUN controls, each drawn from `pool` by the run's name. A control's id looks like any item's (fresh-
    eyes review of Task C: "control-a001-0" told the subagent which items were controls); only the state knows them."""
    out, tries = [], 0
    while len(out) < CONTROLS_PER_RUN and tries < 50 * CONTROLS_PER_RUN:
        h = int(sha(run, part, str(tries)), 16)
        tries += 1
        first = A[pool[h % len(pool)]]
        second = next((A[pool[(h // 7 + k) % len(pool)]] for k in range(min(len(pool), 500))
                       if _apart(first, A[pool[(h // 7 + k) % len(pool)]])), None)
        if second is not None:
            item, want = make(first, second, h)
            if item["id"] not in A and all(item["id"] != c["id"] for c, _ in out):
                out.append((item, want))
    if len(out) < CONTROLS_PER_RUN:
        raise SystemExit(f"REFUSED: {run}: no {CONTROLS_PER_RUN} controls could be drawn; nothing written")
    return out


def audit_controls(A: dict[str, dict], run: str) -> list[tuple[dict, str]]:
    """An assertion's quotes under the value of an assertion from another paper and another context: no quote can hold
    it. Its id is the value's assertion id with a short suffix."""
    pool = sorted(r for r, a in A.items() if a["certainty"] == "high" and a["quotes"].strip())
    return _controls(A, run, "audit", pool, lambda q, v, h: (
        {"id": f"{v['id']}-{h % 97 + 2}", "value": v["value"], "quotes": q["quotes"], "provenance": q["provenance"]},
        "not held"))


def map_controls(A: dict[str, dict], run: str) -> list[tuple[dict, str]]:
    """Two assertions from two papers with no context in common: unrelated. Its id is the pair's, as every item's."""
    pool = sorted(r for r, a in A.items() if a["papers"] and a["contexts"])
    return _controls(A, run, "map", pool, lambda a, b, h: (
        {"id": "|".join(sorted((a["id"], b["id"]))), "a": card(a), "b": card(b)}, "unrelated"))


# ---------------------------------------------------------------- writing inputs

def todo(state: dict, part: str, wanted: dict[str, str]) -> list[str]:
    """Items not yet handed out, or handed out and left out of their result. A saved result is never run again: an
    item with status "done" or "flagged" is not written, whatever its text has become (a changed text is listed)."""
    out = []
    for key in sorted(wanted):
        s = state["items"].get(f"{part}:{key}")
        if s is None or s["status"] == "missing":
            out.append(key)
    return out


def write_inputs(state: dict, part: str, items: dict[str, dict], texts: dict[str, str], A: dict[str, dict],
                 size: int, max_runs: int, today: str) -> list[str]:
    keys = todo(state, part, texts)
    written = []
    for start in range(0, len(keys), size):
        if len(written) >= max_runs:
            break
        run = next_run(state, part)
        chunk = keys[start:start + size]
        controls = audit_controls(A, run) if part == "audit" else map_controls(A, run)
        body = [items[k] for k in chunk] + [c for c, _ in controls]
        order = sorted(body, key=lambda x: sha(run, x["id"]))  # the controls are not at the end
        src, _ = paths(part, run)
        src.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            raise SystemExit(f"REFUSED: {src} exists; a run's input is never rewritten")
        if any(c["id"] in items for c, _ in controls):
            raise SystemExit(f"REFUSED: {run}: a control's id is a real item's; nothing written")
        src.write_text(json.dumps({"run": run, "part": part, "as_of": today, "items": order}, indent=1,
                                  ensure_ascii=False), encoding="utf-8")
        state["runs"][run] = {"part": part, "written": today, "items": chunk,
                              "controls": {c["id"]: want for c, want in controls}, "result": None}
        for k in chunk:
            state["items"][f"{part}:{k}"] = {"run": run, "text": texts[k], "status": "pending"}
        save_state(state)  # after each run, so a later failure leaves no input the state does not know
        written.append(run)
    return written


def forecast(label: str, n_todo: int, size: int, chars: int, max_runs: int) -> None:
    runs = math.ceil(n_todo / size) if n_todo else 0
    print(f"{label}: {n_todo} items to hand out in {runs} runs of up to {size} (+{CONTROLS_PER_RUN} controls each); "
          f"about {chars:,} characters of input in all, about {chars // max(runs, 1):,} per run")
    if max_runs < runs:
        print(f"a write hands out at most {max_runs} runs")


def _opt(args: list[str], name: str, default, kind=int):
    return kind(args[args.index(name) + 1]) if name in args else default


def audit(args: list[str], today: str | None = None) -> int:
    today = today or date.today().isoformat()
    # 200, not 300: a run of 300 came to about 227 KB, near the subagent's 256 KB limit on one Read (review of Task C)
    size, max_runs = _opt(args, "--size", 200), _opt(args, "--max-runs", 5)
    with read_only() as conn:
        A = assertions(conn)
    high = {r: a for r, a in A.items() if a["certainty"] == "high"}
    unquoted = sorted(r for r, a in high.items() if not a["quotes"].strip())
    checkable = {r: a for r, a in high.items() if a["quotes"].strip()}
    texts = {r: sha(a["value"], a["quotes"]) for r, a in checkable.items()}
    state = load_state()
    keys = todo(state, "audit", texts)
    changed = sorted(k for k, t in texts.items() if state["items"].get(f"audit:{k}", {}).get("text") not in (None, t))
    print(f"HIGH assertions: {len(high)}; with no quotes (listed, never sent): {len(unquoted)}; "
          f"already handed out or saved: {len(checkable) - len(keys)}; changed since their result: {len(changed)}")
    forecast("audit", len(keys), size, sum(len(json.dumps(card(checkable[k]))) for k in keys), max_runs)
    if "--write" not in args:
        print("DRY RUN: nothing written. Re-run with --write.")
        return 0
    runs = write_inputs(state, "audit", {k: card(a) for k, a in checkable.items()}, texts, A, size, max_runs, today)
    print(f"written: {runs}")
    return 0


def map_(args: list[str], today: str | None = None) -> int:
    today = today or date.today().isoformat()
    size, max_runs = _opt(args, "--size", 100), _opt(args, "--max-runs", 5)
    top, floor = _opt(args, "--top", 1), _opt(args, "--floor", 0.35, float)
    with read_only() as conn:
        A = assertions(conn)
        known = known_pairs(conn, A)
        held = {tuple(sorted(r)) for r in conn.execute("SELECT from_assertion_id, to_assertion_id FROM "
                                                        "assertion_relations")}
    kept = screen(A, top, floor)
    pairs = {f"{a}|{b}": {"id": f"{a}|{b}", "a": card(A[a]), "b": card(A[b])} for a, b in kept if (a, b) not in held}
    texts = {k: sha(p["a"]["value"], p["a"]["quotes"], p["b"]["value"], p["b"]["quotes"]) for k, p in pairs.items()}
    state = load_state()
    keys = todo(state, "map", texts)
    print(f"screen top {top} at floor {floor}: {len(kept)} pairs ({len(kept) - len(pairs)} already related in the "
          f"store); recall on the store's {len(known)} judged cross-paper relations: {len(known & set(kept))}")
    forecast("map", len(keys), size, sum(len(json.dumps(pairs[k])) for k in keys), max_runs)
    if "--write" not in args:
        print("DRY RUN: nothing written. Re-run with --write.")
        return 0
    runs = write_inputs(state, "map", pairs, texts, A, size, max_runs, today)
    print(f"written: {runs}")
    return 0


# ---------------------------------------------------------------- checking results

def problems(part: str, given: list[dict], result, controls: dict[str, str]) -> tuple[list[str], set[str]]:
    """The result's problems, and the ids it answered. A missing id is not a problem of the result: it is listed and
    handed out again."""
    if not isinstance(result, dict):
        return ["the result is not a JSON object keyed by item id"], set()
    by_id = {x["id"]: x for x in given}
    # F155: an answered id one character off a given id is named (Sprint 18's a018 and a030 each mistyped one)
    out = [f"{k}: not an item of this run" + (f"; one character from the given id {g}" if (g := near_miss(k, by_id))
                                              else "")
           for k in sorted(set(result) - set(by_id))]
    vocab = AUDIT_VERDICTS if part == "audit" else MAP_VERDICTS
    for k in sorted(set(result) & set(by_id)):
        r = result[k]
        if not isinstance(r, dict):
            out.append(f"{k}: not an object")
            continue
        v = r.get("verdict")
        if v not in vocab:
            out.append(f"{k}: verdict {v!r} is not one of {vocab}")
        if not str(r.get("why") or "").strip():
            out.append(f"{k}: no why")
        if part == "map" and v in ("supports", "contradicts"):
            item = by_id[k]
            sides = [item[s]["value"] + "\n" + item[s]["quotes"] for s in ("a", "b")]
            qs = r.get("quotes")
            if not isinstance(qs, list) or not all(isinstance(q, str) for q in qs):
                out.append(f"{k}: quotes must be a list of plain strings")
            else:
                short = [q for q in qs if len(q.strip()) < MIN_QUOTE]
                out += [f"{k}: a deciding quote of under {MIN_QUOTE} characters: {q!r}" for q in short]
                out += [f"{k}: quote not verbatim in the pair: {q[:60]!r}" for q in qs
                        if q not in short and not any(q in s for s in sides)]
                if not all(any(len(q.strip()) >= MIN_QUOTE and q in s for q in qs) for s in sides):
                    out.append(f"{k}: a {v} verdict names at least one deciding quote from each side")
            if not isinstance(r.get("independent"), bool):
                out.append(f"{k}: say whether the two papers are independent: true or false")
            if not str(r.get("independence_why") or "").strip():
                out.append(f"{k}: no independence_why")
        if k in controls and v != controls[k]:
            out.append(f"{k}: a control whose answer is {controls[k]!r} was answered {v!r}")
    answered = set(result) & set(by_id)
    out += [f"{k}: a control was left out" for k in sorted(set(controls) - answered)]
    return out, answered


def check(args: list[str]) -> int:
    run = args[0]
    state = load_state()
    info = state["runs"].get(run)
    if not info:
        print(f"{run}: no such run")
        return 1
    if info["result"] is not None:
        print(f"{run}: its result was already checked ({info['result']}); a saved result is never checked again")
        return 1
    src, out = paths(info["part"], run)
    if not out.is_file():
        print(f"{run}: no result file at {out}")
        return 1
    given = json.loads(src.read_text(encoding="utf-8"))["items"]
    try:
        result = json.loads(out.read_text(encoding="utf-8"))
    except ValueError as e:
        result = f"not JSON: {e}"
    found, answered = problems(info["part"], given, result, info["controls"])
    missing = [k for k in info["items"] if k not in answered]
    status = "flagged" if found else "done"
    for k in info["items"]:
        state["items"][f"{info['part']}:{k}"]["status"] = "missing" if k in missing else status
    # the result's hash, so a later rewrite of the kept file shows
    info.update(result=status, problems=found, missing=missing,
                result_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
    save_state(state)
    for p in found:
        print(p)
    print(f"{run}: {status}; {len(set(info['items']) & answered)} items answered, {len(missing)} left out "
          f"(handed out again at the next write); the result file is kept")
    return 1 if found else 0


def record(args: list[str]) -> int:
    run, tokens_used, minutes = args[0], int(args[1]), float(args[2])
    state = load_state()
    state["runs"][run].update(tokens=tokens_used, minutes=minutes)
    save_state(state)
    return 0


def status(args: list[str]) -> int:
    state = load_state()
    for part in ("audit", "map"):
        c = Counter(s["status"] for k, s in state["items"].items() if k.startswith(part + ":"))
        runs = [r for r, i in state["runs"].items() if i["part"] == part]
        print(f"{part}: {dict(c)}; runs {len(runs)}, tokens {sum(state['runs'][r].get('tokens', 0) for r in runs):,}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    commands = {"audit": audit, "map": map_, "check": check, "record": record, "status": status}
    if not args or args[0] not in commands:
        print(__doc__)
        return 1
    return commands[args[0]](args[1:])


if __name__ == "__main__":
    sys.exit(main())
