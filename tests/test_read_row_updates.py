"""Sprint 13 retrospective I2 (team lead, 2026-10-28): every UPDATE of a
paper_reads row names the row's own detail.

Task G's apply matched read rows by reader, day and extent alone and rewrote
the detail of 114 Task F rows written the same day (full suite, 2026-10-27).
The table's key holds the detail, so two scripts' rows can share reader, day
and extent; an UPDATE that leaves the detail out rewrites every one of them.
Seven older scripts carried the same match; their UPDATEs now name the row's
stored detail. Reads parsed code, so a statement in a comment or docstring is
not counted. Proven to fail, 2026-10-28: with `AND detail = ?` removed from
`sprint12_reading.py`'s UPDATE, the test named that file and line; with "+"
joins not read, the check missed a split statement (review of c978e50).

WHAT IT DOES NOT CLOSE (review of c978e50). The older scripts pick the row
they compare from a dict keyed by reader, day and extent, so when another
script's row shares that key and the script's own row is missing, the
foreign row is the one compared and rewritten. Only Task F's and Task G's
scripts filter by their own wording. No such collision exists on the older
scripts' days (live store, 2026-10-28: the only shared keys are on
2026-10-25, Task F and Task G); do not re-run those scripts on a day
another script wrote without adding the filter.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATE = re.compile(r"^\s*(UPDATE\s+paper_reads|DELETE\s+FROM\s+paper_reads)\b", re.IGNORECASE)
DETAIL_IN_WHERE = re.compile(r"\bWHERE\b.*\bAND\s+detail\s*=\s*\?", re.IGNORECASE | re.DOTALL)


def _text(node) -> str:
    """A statement's literal text: a string, or the string parts of a "+" join or an f-string (review of c978e50)."""
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else ""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _text(node.left) + _text(node.right)
    if isinstance(node, ast.JoinedStr):
        return "".join(_text(v) for v in node.values)
    return ""


def key_only_updates(paths) -> list[str]:
    found = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        inner = {id(c) for n in ast.walk(tree) if isinstance(n, (ast.BinOp, ast.JoinedStr)) for c in ast.walk(n)
                 if c is not n}
        for node in ast.walk(tree):
            text = _text(node) if id(node) not in inner else ""
            if UPDATE.match(text) and not DETAIL_IN_WHERE.search(text):
                found.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}")
    return found


def test_every_read_row_update_names_the_rows_detail():
    paths = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "store").glob("*.py"))
    assert paths
    assert key_only_updates(paths) == []


def test_the_check_names_a_key_only_update(tmp_path, monkeypatch):
    """The check itself, on a file it must name and one it must pass."""
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    bad, good = tmp_path / "bad.py", tmp_path / "good.py"
    bad.write_text('c.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND reader = ? "\n'
                   '          "AND read_on = ? AND extent = ?", args)\n', encoding="utf-8")
    good.write_text('c.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? AND detail = ?", args)\n'
                    'c.execute("UPDATE paper_reads SET x = ? WHERE record_id = ? " + "AND detail = ?", args)\n'
                    '# UPDATE paper_reads SET detail = ? WHERE record_id = ?\n', encoding="utf-8")
    joined = tmp_path / "joined.py"
    joined.write_text('c.execute("UPDATE " + "paper_reads SET detail = ? WHERE record_id = ?", args)\n'
                      'c.execute(f"DELETE FROM paper_reads WHERE record_id = {rid!r}")\n'
                      'c.execute("UPDATE paper_reads SET detail = ? WHERE record_id = ? OR detail = ?", args)\n',
                      encoding="utf-8")
    assert key_only_updates([bad, good, joined]) == ["bad.py:1", "joined.py:1", "joined.py:2", "joined.py:3"]
