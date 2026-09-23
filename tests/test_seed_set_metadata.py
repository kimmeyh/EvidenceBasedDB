"""scripts/seed_set_metadata.json carries exactly what the door accepts
(Sprint 4 Task C, F25 C1: "retire the hand-typed source explicitly").

Since Task B the seed file is the hand-authored INPUT to
scripts/ingest_seed_set.py, not the output of a generator, and the rules
below are the door's own shape rules restated for a file that has not been
inserted yet. They need no filesystem and no network, so they run in CI;
the one rule they cannot check -- that a hand entry's local path exists on
this machine -- is the door's at insert time.

Proven to fail by injection 2026-09-19: an entry given `"citation_origin":
"api"` with the access `"local file"` went red on
test_api_entries_carry_a_resolvable_id_and_no_citation; a hand entry with
its marker removed went red on test_hand_entries_are_visibly_hand_transcribed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from store.citations import parse_access  # noqa: E402
from store.ingest import HAND_MARKER, _AUDIT_MARKERS, _TIER_IN_TEXT  # noqa: E402

METADATA = ROOT / "scripts" / "seed_set_metadata.json"


@pytest.fixture(scope="module")
def entries() -> list[dict]:
    return json.loads(METADATA.read_text(encoding="utf-8"))


def test_ids_are_unique_and_the_renamed_rand_id_is_gone(entries):
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids))
    assert not any(i.startswith("rand-2023-") for i in ids), "Q4 renamed rand-2023-* to rand-2022-*"


def test_every_entry_declares_its_citation_origin(entries):
    bad = [e["id"] for e in entries if e.get("citation_origin") not in ("api", "hand")]
    assert bad == []


def test_api_entries_carry_a_resolvable_id_and_no_citation(entries):
    for e in entries:
        if e["citation_origin"] != "api":
            continue
        assert parse_access(e["access"]), f"{e['id']}: api origin but access {e['access']!r} has no arXiv id or DOI"
        assert "citation" not in e, f"{e['id']}: an api entry must not carry a hand-typed citation"


def test_hand_entries_are_visibly_hand_transcribed(entries):
    for e in entries:
        if e["citation_origin"] != "hand":
            continue
        assert parse_access(e["access"]) is None, f"{e['id']}: hand origin but the access carries a resolvable id"
        assert e.get("title", "").strip(), f"{e['id']}: hand entry needs a title (records.value)"
        assert e.get("transcribed_from", "").strip(), f"{e['id']}: hand entry needs transcribed_from"
        assert HAND_MARKER in e.get("citation", ""), f"{e['id']}: citation must carry '{HAND_MARKER} <page>'"
        assert "local file" not in e["access"], f"{e['id']}: access is the bare words 'local file' (ADR-0005 section 3)"
        assert re.match(r"^[A-Za-z]:\\", e["access"]), f"{e['id']}: hand access must start with a local path"


def test_no_citation_carries_audit_trail(entries):
    for e in entries:
        cit = e.get("citation", "")
        hits = [m for m in _AUDIT_MARKERS if m.lower() in cit.lower()]
        assert hits == [], f"{e['id']}: citation carries {hits}; that belongs in updated_reason/evidence"


def test_dispositions_are_one_line_and_name_no_tier(entries):
    for e in entries:
        assert "\n" not in e["disposition"], f"{e['id']}: multi-line disposition"
        assert not _TIER_IN_TEXT.search(e["disposition"]), f"{e['id']}: disposition names a tier; the tier column is the resolver"
