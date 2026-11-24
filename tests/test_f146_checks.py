"""F146 (Sprint 18 Task C): the HIGH audit and the agreement map, run by Claude Code subagents (team lead q1 = c).
`scripts/f146_checks.py` writes each subagent's input and checks each result; it never writes the store and never
imports an API client. Each of F144's rules that applies under q1 = c has a test here, on a small store built in a
temporary folder.

Proven to fail by injection, 2026-11-21, each restored (a grep for INJECTED in scripts/f146_checks.py finds nothing):
- `read_only` opening the store without `?mode=ro` (`return sqlite3.connect(path)  # INJECTED`):
  test_the_store_is_opened_so_no_write_can_succeed went red;
- `todo` handing out every item (`out.append(key)  # INJECTED`, the status test removed):
  test_a_saved_result_is_never_handed_out_again went red (a second run was written);
- `check` marking a failing run "done" (`status = "done"  # INJECTED`): test_a_failing_result_is_kept_and_flagged
  and test_a_wrong_control_flags_the_whole_run went red;
- the control check removed from `problems` (`if False and k in controls  # INJECTED`):
  test_a_wrong_control_flags_the_whole_run went red;
- the verbatim check removed (`if False  # INJECTED` on the quote list): test_a_map_verdict_needs_verbatim_quotes_
  and_an_independence_answer went red;
- `import anthropic  # INJECTED` added to the script: test_no_api_client_is_imported_and_no_key_is_read went red.
After the fresh-eyes review's fixes, 2026-11-21, each restored:
- the each-side check in `problems` replaced by `if False:`: test_a_map_verdict_needs_a_quote_from_each_side_and_
  plain_strings went red;
- the plain-string check removed: the same test went red (AttributeError, the crash the review found);
- the same-paper filter removed from `screen`: test_the_screen_pairs_only_two_papers_that_share_a_context went red
  (a1|a3 kept);
- the audit control id set back to `control-{run}-N`: test_a_control_is_not_named_as_one_and_is_never_a_real_item
  went red;
- `save_state` moved after the loop: test_a_write_that_stops_part_way_blocks_no_later_write went red;
- the input-file scan removed from `next_run`: test_a_write_hands_out_at_most_max_runs_and_never_rewrites_an_input
  went red (REFUSED on the stray a003).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "f146_checks.py"

ROWS = [  # id, paper, context, certainty, value, quotes
    ("a1", "p1", "qml", "high", "Kernel alignment raised accuracy on credit fraud data to 91 percent",
     '"kernel alignment raised accuracy to 91 percent" (p.3)'),
    ("b1", "p2", "qml", "high", "Kernel alignment raised accuracy on credit fraud data to 91 percent in a rerun",
     '"a rerun of kernel alignment reached 91 percent" (p.5)'),
    ("a2", "p1", "qml", "high", "The ansatz uses eight qubits", '"the ansatz uses eight qubits" (p.2)'),
    ("a3", "p1", "qml", "low", "Kernel alignment raised accuracy on credit fraud data to 91 percent again",
     '"again 91 percent" (p.9)'),  # a same-paper restatement the screen must never pair with a1
    ("b2", "p3", "ml", "high", "Gradient boosting trains in four minutes", '"trains in four minutes" (p.4)'),
    ("c1", "p4", "ml", "high", "Random forests overfit small tabular sets", '"overfit small tabular sets" (p.6)'),
    ("c2", "p4", "world", "low", "Fraud costs banks billions", '"costs banks billions" (p.1)'),
    ("d1", "p5", "world", "high", "Card fraud losses rose in 2024", '"losses rose in 2024" (p.2)'),
    ("e1", "p6", "qml", "high", "No quotes here", ""),
]


def _script(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("f146_checks", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    db = tmp_path / "evidence.db"
    c = sqlite3.connect(db)
    c.executescript("""
        CREATE TABLE records (id TEXT PRIMARY KEY, class TEXT, value TEXT, provenance TEXT, certainty TEXT);
        CREATE TABLE assertion_fields (record_id TEXT PRIMARY KEY, citation_context TEXT, derivation TEXT);
        CREATE TABLE record_contexts (record_id TEXT, context_id TEXT);
        CREATE TABLE paper_yields (paper_id TEXT, assertion_id TEXT);
        CREATE TABLE assertion_relations (from_assertion_id TEXT, to_assertion_id TEXT, relation TEXT);""")
    for rid, paper, ctx, cert, value, quotes in ROWS:
        c.execute("INSERT INTO records VALUES (?, 'assertion', ?, ?, ?)", (rid, value, f"{paper}, p.1", cert))
        c.execute("INSERT INTO assertion_fields VALUES (?, ?, 'extracted')", (rid, quotes))
        c.execute("INSERT INTO record_contexts VALUES (?, ?)", (rid, ctx))
        c.execute("INSERT INTO paper_yields VALUES (?, ?)", (paper, rid))
    c.commit()
    c.close()
    monkeypatch.setattr(mod, "DB_PATH", db)
    monkeypatch.setattr(mod, "WORK", tmp_path / "work")
    return mod, db


def _result(mod, part, run, answer):
    """A result for every item of a run's input, `answer(item)` giving each one's entry (None leaves it out)."""
    src, out = mod.paths(part, run)
    items = json.loads(src.read_text(encoding="utf-8"))["items"]
    out.parent.mkdir(parents=True, exist_ok=True)
    body = {i["id"]: answer(i) for i in items}
    out.write_text(json.dumps({k: v for k, v in body.items() if v is not None}), encoding="utf-8")
    return items


def _good_audit(mod, run):
    controls = mod.load_state()["runs"][run]["controls"]
    return lambda i: {"verdict": controls.get(i["id"], "held"), "why": "the quote states it"}


def test_a_dry_run_writes_nothing(tmp_path, monkeypatch, capsys):
    mod, db = _script(tmp_path, monkeypatch)
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    assert mod.audit([]) == 0 and mod.map_(["--floor", "0.1"]) == 0
    assert not (tmp_path / "work").exists()
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before
    out = capsys.readouterr().out
    assert "with no quotes (listed, never sent): 1" in out and out.count("DRY RUN: nothing written") == 2


def test_the_store_is_opened_so_no_write_can_succeed(tmp_path, monkeypatch):
    mod, db = _script(tmp_path, monkeypatch)
    conn = mod.read_only(db)
    try:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("INSERT INTO records VALUES ('x', 'assertion', 'v', 'p', 'high')")
    finally:
        conn.close()


def test_no_api_client_is_imported_and_no_key_is_read():
    """q1 = c: no API spend. The script names no API client, no key and no batch_read (whose sends and key it would
    bring in)."""
    import ast
    names = set()
    for n in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            names |= {a.name.split(".")[0] for a in n.names} | {(getattr(n, "module", None) or "").split(".")[0]}
        elif isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            names |= {w for w in ("ANTHROPIC_API_KEY", ".env") if w in n.value}
    banned = {"anthropic", "batch_read", "requests", "httpx", "urllib", "http", "api_key", "make_client",
              "ANTHROPIC_API_KEY", ".env"}
    assert names & banned == set()


def test_a_saved_result_is_never_handed_out_again(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    assert mod.audit(["--write", "--size", "10"]) == 0
    (run,) = mod.load_state()["runs"]
    _result(mod, "audit", run, _good_audit(mod, run))
    assert mod.check([run]) == 0
    assert mod.audit(["--write", "--size", "10"]) == 0
    assert list(mod.load_state()["runs"]) == [run]  # nothing new to hand out
    assert mod.check([run]) == 1  # and a result is checked once


def test_a_left_out_item_is_handed_out_again_and_only_it(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "10"])
    (run,) = mod.load_state()["runs"]
    good = _good_audit(mod, run)
    _result(mod, "audit", run, lambda i: None if i["id"] == "a2" else good(i))
    assert mod.check([run]) == 0
    mod.audit(["--write", "--size", "10"])
    runs = mod.load_state()["runs"]
    assert list(runs) == ["a001", "a002"] and runs["a002"]["items"] == ["a2"]


def test_a_failing_result_is_kept_and_flagged(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "10"])
    good = _good_audit(mod, "a001")
    _result(mod, "audit", "a001", lambda i: {"verdict": "probably", "why": "x"} if i["id"] == "a1" else good(i))
    assert mod.check(["a001"]) == 1
    state = mod.load_state()
    assert state["runs"]["a001"]["result"] == "flagged"
    assert any("a1: verdict 'probably'" in p for p in state["runs"]["a001"]["problems"])
    assert state["items"]["audit:a1"]["status"] == "flagged"
    assert mod.paths("audit", "a001")[1].is_file()  # kept
    mod.audit(["--write", "--size", "10"])
    assert list(mod.load_state()["runs"]) == ["a001"]  # a flagged result is not run again either


def test_a_wrong_control_flags_the_whole_run(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "10"])
    _result(mod, "audit", "a001", lambda i: {"verdict": "held", "why": "words overlap"})
    assert mod.check(["a001"]) == 1
    state = mod.load_state()
    assert state["runs"]["a001"]["result"] == "flagged"
    assert any("a control whose answer is 'not held'" in p for p in state["runs"]["a001"]["problems"])
    assert {s["status"] for s in state["items"].values()} == {"flagged"}


def test_a_map_verdict_needs_verbatim_quotes_and_an_independence_answer(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    assert mod.map_(["--write", "--floor", "0.1"]) == 0
    (run,) = mod.load_state()["runs"]
    controls = mod.load_state()["runs"][run]["controls"]

    def answer(i):
        if i["id"] in controls:
            return {"verdict": "unrelated", "why": "different questions"}
        return {"verdict": "supports", "why": "same result", "quotes": ["91 percent", "raised accuracy to 92"],
                "independent": "yes"}
    items = _result(mod, "map", run, answer)
    assert any(i["id"] == "a1|b1" for i in items)
    assert mod.check([run]) == 1
    found = mod.load_state()["runs"][run]["problems"]
    assert any("quote not verbatim in the pair: 'raised accuracy to 92'" in p for p in found)
    assert any("under 15 characters: '91 percent'" in p for p in found)
    assert any("say whether the two papers are independent" in p for p in found)
    assert any("no independence_why" in p for p in found)


def _pair(mod):
    """a1|b1 as the map gives it, for calling `problems` directly."""
    with mod.read_only() as conn:
        A = mod.assertions(conn)
    return {"id": "a1|b1", "a": mod.card(A["a1"]), "b": mod.card(A["b1"])}


def test_a_map_verdict_needs_a_quote_from_each_side_and_plain_strings(tmp_path, monkeypatch):
    """Fresh-eyes review of Task C: two quotes from one side passed, and a quote that was not a string crashed `check`
    before the run was flagged."""
    mod, _ = _script(tmp_path, monkeypatch)
    item = _pair(mod)
    ok = {"verdict": "supports", "why": "same", "independent": False, "independence_why": "same authors"}
    both = {**ok, "quotes": ["kernel alignment raised accuracy to 91 percent", "a rerun of kernel alignment"]}
    assert mod.problems("map", [item], {"a1|b1": both}, {})[0] == []
    one = {**ok, "quotes": ["kernel alignment raised accuracy to 91 percent", "raised accuracy to 91 percent"]}
    assert any("one deciding quote from each side" in p for p in mod.problems("map", [item], {"a1|b1": one}, {})[0])
    odd = {**ok, "quotes": [{"text": "a rerun"}, "a rerun of kernel alignment"]}
    assert any("plain strings" in p for p in mod.problems("map", [item], {"a1|b1": odd}, {})[0])


def test_a_control_is_not_named_as_one_and_is_never_a_real_item(tmp_path, monkeypatch):
    """Fresh-eyes review of Task C: "control-a001-0" told the subagent which items were controls."""
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "10"])
    mod.map_(["--write", "--floor", "0.1"])
    for run, info in mod.load_state()["runs"].items():
        assert len(info["controls"]) == mod.CONTROLS_PER_RUN
        for cid in info["controls"]:
            assert "control" not in cid and cid not in info["items"]
            assert ("|" in cid) == (info["part"] == "map")


def test_a_write_that_stops_part_way_blocks_no_later_write(tmp_path, monkeypatch):
    """Fresh-eyes review of Task C: the state was saved only after the last run, so a failure part way left input
    files the state did not know, and every later write was refused."""
    mod, _ = _script(tmp_path, monkeypatch)
    real = mod.audit_controls
    calls = []

    def fail_second(A, run):
        calls.append(run)
        if len(calls) == 2:
            raise SystemExit("stopped")
        return real(A, run)
    monkeypatch.setattr(mod, "audit_controls", fail_second)
    with pytest.raises(SystemExit, match="stopped"):
        mod.audit(["--write", "--size", "2", "--max-runs", "3"])
    assert list(mod.load_state()["runs"]) == ["a001"]  # the first run is known
    monkeypatch.setattr(mod, "audit_controls", real)
    assert mod.audit(["--write", "--size", "2", "--max-runs", "1"]) == 0
    assert list(mod.load_state()["runs"]) == ["a001", "a002"]


def test_a_pending_item_is_not_handed_out_twice(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "2", "--max-runs", "1"])
    mod.audit(["--write", "--size", "2", "--max-runs", "1"])
    runs = mod.load_state()["runs"]
    assert len(runs) == 2 and not set(runs["a001"]["items"]) & set(runs["a002"]["items"])


def test_the_screen_pairs_only_two_papers_that_share_a_context(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    with mod.read_only() as conn:
        A = mod.assertions(conn)
    kept = mod.screen(A, top=3, floor=0.0)
    assert ("a1", "b1") in kept and ("a1", "a3") not in kept
    assert all(not A[a]["papers"] & A[b]["papers"] and A[a]["contexts"] & A[b]["contexts"] for a, b in kept)


def test_a_write_hands_out_at_most_max_runs_and_never_rewrites_an_input(tmp_path, monkeypatch):
    mod, _ = _script(tmp_path, monkeypatch)
    mod.audit(["--write", "--size", "2", "--max-runs", "2"])
    assert list(mod.load_state()["runs"]) == ["a001", "a002"]
    stray = mod.paths("audit", "a003")[0]
    stray.write_text("{}", encoding="utf-8")  # an input the state does not know: passed over, never rewritten
    mod.audit(["--write", "--size", "2", "--max-runs", "1"])
    assert list(mod.load_state()["runs"]) == ["a001", "a002", "a004"] and stray.read_text(encoding="utf-8") == "{}"
