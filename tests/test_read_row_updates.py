"""Sprint 13 retrospective I2 (team lead, 2026-10-28): every UPDATE of a
paper_reads row names the row's own detail.

Task G's apply matched read rows by reader, day and extent alone and rewrote
the detail of 114 Task F rows written the same day (full suite, 2026-10-27).
The table's key holds the detail, so two scripts' rows can share reader, day
and extent; an UPDATE that leaves the detail out rewrites every one of them.
Seven older scripts carried the same match; their UPDATEs now name the row's
stored detail. Reads parsed code, so a statement in a comment or docstring is
not counted. Proven to fail, 2026-10-28: with `AND detail = ?` removed from
`sprint12_reading.py`'s UPDATE, the test named that file and line.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATE = re.compile(r"^\s*UPDATE\s+paper_reads\b", re.IGNORECASE)
DETAIL_IN_WHERE = re.compile(r"\bWHERE\b.*\bdetail\s*=\s*\?", re.IGNORECASE | re.DOTALL)


def key_only_updates(paths) -> list[str]:
    found = []
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str) and UPDATE.match(node.value)
                    and not DETAIL_IN_WHERE.search(node.value)):
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
                    '# UPDATE paper_reads SET detail = ? WHERE record_id = ?\n', encoding="utf-8")
    assert key_only_updates([bad, good]) == ["bad.py:1"]
