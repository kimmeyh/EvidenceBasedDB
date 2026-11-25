"""Free assertion ids by construction (F155, Sprint 19 Task C; Sprint 18 retrospective i3, team lead "i3. a").

In Sprint 18 five reader ids (`data-availability-on-request`, `review-scope`, `vqe-definition`,
`qaoa-definition`, `schwinger-model-definition`) were already other sources' and were renamed after review, and
audit runs a018 and a030 each mistyped one given id. The store refuses a duplicate (`records.id` is the PRIMARY
KEY) and `scripts/f117_build_groups.py` renames a taken id before review (`prefixed`), but neither ran when the
reader chose the id. These functions run then: in the read checker, and in the audit and map checkers.

`unique_assertion_id` keeps `prefixed`'s rule: the paper's author and year (the record id's first two words), then
more of the record id, before the name, until it is free.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable


def unique_assertion_id(record_id: str, name: str, taken: set[str]) -> str:
    """`name` when no record and no other group holds it; else the record id's first words before it, as
    `f117_build_groups.prefixed` does, until free."""
    if name not in taken:
        return name
    words = record_id.split("-")
    for n in range(2, len(words) + 1):
        new = f"{'-'.join(words[:n])}-{name}"
        if new not in taken:
            return new
    raise ValueError(f"{record_id}: no free id for {name}")


def store_ids(db_path: Path) -> set[str]:
    """Every record id in the store, read only. A missing store is an error: an empty answer would call every id
    free (F127's rule)."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"{db_path}: no store, so no id can be checked against it")
    conn = sqlite3.connect(f"{Path(db_path).as_uri()}?mode=ro", uri=True)
    try:
        return {r[0] for r in conn.execute("SELECT id FROM records")}
    finally:
        conn.close()


def group_file_ids(files: Iterable[Path]) -> set[str]:
    """The new assertion ids (`id_suggestion`, else `id`) in reader group files."""
    out = set()
    for f in files:
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for p in data.get("papers", []) if isinstance(data, dict) else []:
            out |= {a.get("id_suggestion") or a.get("id") for a in p.get("assertions", []) if isinstance(a, dict)}
    return out - {None, ""}


def one_edit_apart(a: str, b: str) -> bool:
    """True when one insertion, deletion or substitution turns `a` into `b`."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    i = 0
    while i < len(short) and short[i] == long_[i]:
        i += 1
    return short[i:] == long_[i + 1:]


def near_miss(answered: str, given: Iterable[str]) -> str | None:
    """The given id one edit away from an answered id that was not given, or None."""
    hits = sorted(g for g in given if one_edit_apart(answered, g))
    return hits[0] if hits else None
