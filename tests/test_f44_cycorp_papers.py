"""F44 (Sprint 7 Task F): the eight Cycorp papers each point at a local
copy whose SHA-256 the record carries, and T07's two assertions quote it
verbatim (INTAKE_WORKFLOW.md section 18)."""
from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.live_store


def _script():
    spec = importlib.util.spec_from_file_location("f44", ROOT / "scripts" / "sprint7_f44_cycorp_papers.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _normalized(text: str) -> str:
    """Whitespace collapsed, and the typographic forms the quotes' anchors
    name (curly apostrophe and quotation marks, the fi ligature) made plain."""
    for typographic, plain in (("’", "'"), ("“", '"'), ("”", '"'), ("ﬁ", "fi")):
        text = text.replace(typographic, plain)
    return re.sub(r"\s+", " ", text)


def test_every_paper_has_a_local_copy_whose_hash_the_record_carries(live_conn):
    """Proven to fail by injection, 2026-10-08: with the file hashed by
    SHA-1 instead of SHA-256, no record carried the digest and this test
    went red."""
    f44 = _script()
    ids = [f44.entry_for(k).get("id") for k in f44.PAPERS_IN]
    rows = live_conn.execute(
        "SELECT p.record_id, p.access, p.evidence FROM paper_fields p JOIN paper_found_via v USING (record_id) "
        "WHERE v.route = ?", (f44.ROUTE,)).fetchall()
    assert len(rows) == len(f44.PAPERS_IN) == 8
    assert {i for i in ids if i} <= {r[0] for r in rows}
    for record_id, access, evidence in rows:
        local = Path(access.split(" | ")[0])
        assert local.parent == f44.PAPERS and local.exists(), f"{record_id}: no local copy at {local}"
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        assert f"SHA-256 {digest}" in evidence, f"{record_id}: the record does not carry its file's SHA-256"


def test_t07_is_read_in_full_and_its_two_assertions_quote_it(live_conn):
    """Proven to fail by injection, 2026-10-08: with the curly quotation
    marks no longer made plain, the p.147 quote (straight quotes around
    "split") was not found in T07's text and this test went red."""
    f44 = _script()
    tier, checked = live_conn.execute("SELECT tier, checked_against_source FROM paper_fields WHERE record_id = ?",
                                      (f44.T07,)).fetchone()
    assert tier == "read" and checked
    assert live_conn.execute("SELECT extent FROM paper_reads WHERE record_id = ?", (f44.T07,)).fetchone()[0] == "full"
    pdf = f44.PAPERS / f44.PAPERS_IN["T07"][0]
    text = _normalized(subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"], capture_output=True,
                                      check=True).stdout.decode("utf-8"))
    yields = {r[0] for r in live_conn.execute("SELECT assertion_id FROM paper_yields WHERE paper_id = ?", (f44.T07,))}
    assert yields == {a.id for a in f44.ASSERTIONS}
    for a in f44.ASSERTIONS:
        claim_type, stored = live_conn.execute(
            "SELECT claim_type, citation_context FROM assertion_fields WHERE record_id = ?", (a.id,)).fetchone()
        assert claim_type == "vendor-self-claim"
        quotes = re.findall(r'"((?:[^"]|"[a-z]+")+?)" \(p\.', stored)
        assert quotes, f"{a.id}: no quote found"
        for q in quotes:
            assert q in text, f"{a.id}: not verbatim in T07: {q[:60]}"


def test_the_sprint_6_module_count_note_is_settled(live_conn):
    reason = live_conn.execute("SELECT updated_reason FROM records WHERE id = 'cyc-hl-module-count'").fetchone()[0]
    assert "Not verified here" in reason and _script().HL_MODULE_NOTE in reason
