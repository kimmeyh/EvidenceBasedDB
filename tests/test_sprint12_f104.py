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
    for name, digest in MANIFEST["files"].items():
        assert hashlib.sha256(F104.copy_of(name).read_bytes()).hexdigest() == digest, name


def test_every_entered_paper_is_in_the_store_once(live_conn):
    """Each entered id is one record at `seen` under `qml`, its access the
    id, and no other record holds the id. Proven to fail by injection,
    2026-10-23: run against the backup taken before the apply, it named
    the first entered record."""
    assert MANIFEST["entered"] and MANIFEST["arxiv_ids_new"] == len(MANIFEST["entered"])
    holders: dict[str, list[str]] = {}
    for rid, a, e, p in live_conn.execute("SELECT f.record_id, f.access, f.evidence, r.provenance "
                                          "FROM paper_fields f JOIN records r ON r.id = f.record_id"):
        for ident in set(F104._HELD_ARXIV.findall(f"{a or ''} {e or ''} {p or ''}")):
            holders.setdefault(ident, []).append(rid)
    for e in MANIFEST["entered"]:
        row = live_conn.execute("SELECT tier, access FROM paper_fields WHERE record_id = ?",
                                (e["record_id"],)).fetchone()
        assert row is not None and row[0] == "seen", e["record_id"]
        assert [r[0] for r in live_conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?",
                                                (e["record_id"],))] == ["qml"], e["record_id"]
        assert re.match(rf"arXiv:{re.escape(e['arxiv'])}(?: \| |$)", row[1]), e["record_id"]
        assert holders.get(e["arxiv"]) == [e["record_id"]], e["record_id"]


def test_a_second_apply_enters_nothing(live_copy):
    from store import connect
    conn = connect(live_copy)
    try:
        log, manifest = F104.apply_changes(conn, apply=True, fetcher=F104.CachedFetcher())
    finally:
        conn.close()
    assert not log and manifest["entered"] == [] and manifest["arxiv_ids_new"] == 0
