"""Source links read from either end (ADR-0005 A10, Sprint 9 Task H, F55).

A link is stored once, from one record to another: `cites` goes from the
citing paper to the cited one. Storing the reverse as well would be a copy
of a determinate fact, so a record's incoming links are a query, not a row.
"""
from __future__ import annotations

import sqlite3


def links_of(conn: sqlite3.Connection, record_id: str, link_type: str | None = None) -> dict[str, list[dict]]:
    """{"out": links from record_id, "in": links to it}; each link is
    {"type", "other", "evidence"}, sorted by type and then the other id."""
    typed = " AND link_type = ?" if link_type else ""
    args = (record_id, link_type) if link_type else (record_id,)
    out = [{"type": t, "other": o, "evidence": e} for t, o, e in conn.execute(
        f"SELECT link_type, to_id, evidence FROM source_links WHERE from_id = ?{typed} ORDER BY link_type, to_id",
        args)]
    inc = [{"type": t, "other": o, "evidence": e} for t, o, e in conn.execute(
        f"SELECT link_type, from_id, evidence FROM source_links WHERE to_id = ?{typed} ORDER BY link_type, from_id",
        args)]
    return {"out": out, "in": inc}
