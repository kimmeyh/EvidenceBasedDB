"""F104 (Sprint 12 Task F): Roadmap-to-QML's first release, its new arXiv
papers entered at `seen` (INTAKE_WORKFLOW.md section 46). The list's copy
and the PDFs live outside the repository, so every test here is
live_store."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f104", ROOT / "scripts" / "sprint12_f104_roadmap.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F104 = _script()
MANIFEST = json.loads(F104.MANIFEST.read_text(encoding="utf-8"))


def test_the_manifest_names_the_copy_it_read():
    assert MANIFEST["commit"] == F104.COMMIT
    assert set(MANIFEST["files"]) == set(F104.FILES)
    for name, digest in MANIFEST["files"].items():
        assert hashlib.sha256(F104.copy_of(name).read_bytes()).hexdigest() == digest, name


def test_every_entered_paper_is_in_the_store_once(live_conn):
    """Each entered id is one record under `qml`, its access the id, and no
    other record holds the id. It entered at `seen` and stays there unless
    a Sprint 12 ledger group read it (section 47 then moved it to `read`).
    Proven to fail by injection, 2026-10-23: run against the backup taken
    before the apply, it named the first entered record."""
    assert MANIFEST["entered"] and MANIFEST["arxiv_ids_new"] == len(MANIFEST["entered"])
    ledger = json.loads((ROOT / "manifests" / "sprint12_read_ledger.json").read_text(encoding="utf-8"))
    read = {r["record_id"] for g in ledger["groups"].values() for r in g["records"]}
    holders: dict[str, list[str]] = {}
    for rid, a, e, p in live_conn.execute("SELECT f.record_id, f.access, f.evidence, r.provenance "
                                          "FROM paper_fields f JOIN records r ON r.id = f.record_id"):
        for ident in set(F104._HELD_ARXIV.findall(f"{a or ''} {e or ''} {p or ''}")):
            holders.setdefault(ident, []).append(rid)
    for e in MANIFEST["entered"]:
        row = live_conn.execute("SELECT tier, access FROM paper_fields WHERE record_id = ?",
                                (e["record_id"],)).fetchone()
        assert row is not None and row[0] == ("read" if e["record_id"] in read else "seen"), e["record_id"]
        assert [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                                (e["record_id"],))] == ["qml"], e["record_id"]
        assert re.match(rf"arXiv:{re.escape(e['arxiv'])}(?: \| |$)", row[1]), e["record_id"]
        assert holders.get(e["arxiv"]) == [e["record_id"]], e["record_id"]


def test_every_listed_paper_is_held_and_carries_the_route(live_conn):
    """No listed id is left unentered, and every record that holds a
    listed id names the list in its found_via (the second apply, fresh-eyes
    review of f99139e). Proven to fail by injection, 2026-10-23: run
    against the backup taken before the second apply, it named the first
    held record with no route."""
    routed = {r[0] for r in live_conn.execute("SELECT record_id FROM paper_found_via WHERE route LIKE ?",
                                              (f"{F104.FOUND_VIA}%",))}
    hold = F104.holders(live_conn)
    ids, bad = F104.split_ids(live_conn)
    assert ids == []
    for ident in sorted(F104.listed()):
        for rid in [r for i in (bad[ident] if ident in bad else [ident]) for r in hold.get(i, [])]:
            assert rid in routed, (ident, rid)
    # F137 (Sprint 16 Task E): a record merged into another passed its route to the record that holds it now.
    from store.merges import MERGED_INTO
    copied = {new for old, new in MERGED_INTO.items() if old in routed and new in routed}
    assert len(routed) == MANIFEST["arxiv_ids_new"] + MANIFEST["routes_added_to_held_papers"] + len(copied)


def test_a_second_apply_enters_nothing(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        log, manifest = F104.apply_changes(conn, apply=True, fetcher=F104.CachedFetcher())
    finally:
        conn.close()
    assert not log and manifest["entered"] == [] and manifest["arxiv_ids_new"] == 0
    # Not vacuous: the list was read, and the malformed link was still found.
    assert manifest["arxiv_ids_listed"] == MANIFEST["arxiv_ids_listed"] == 1418
    assert [m["listed_as"] for m in manifest["malformed_links"]] == ["2108.0131"]
