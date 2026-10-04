"""Rebuild the store from the committed export (Sprint 5 Task A, F30 part 1).

ADR-0004 section 2 calls the store a build output and the committed export
the artifact. That claim is only true if the export can be turned back
into a store, and until this module nothing did so: `regenerate()` went
store -> export with no path the other way. The Sprint 4 remote session
rebuilt the store by hand once, in a session that no longer exists. A
recovery path with no code is the same defect class as a guard that has
never been run.

This module is the inverse of store/export.py, and it goes through the
real door: papers enter via `insert_paper()` (every validate_paper rule
runs), assertions via `insert_assertion()`. The only rule relaxed is the
one that is a property of the MACHINE rather than the record -- that a
hand-origin paper's local file exists here -- and only when the caller
says so, so the rebuild can run on a CI runner with no material directory.

STRICT by design: an exported key this module does not know how to put
back raises `UnrestorableKey`. Silently dropping a field is exactly how an
export stops being a complete artifact without anyone noticing; the
byte-identity check in `rebuild_and_compare()` would catch the loss, but
the key check names it first.
"""
from __future__ import annotations

import json
import re
import sqlite3
import tempfile
from pathlib import Path

from store import create_store
from store.export import regenerate
from store.ingest import (HAND_MARKER, REPLAY, AssertionRecord, PaperRecord, add_source_link, insert_assertion,
                          insert_paper, record_probe)

EXPORT_FILES = ("contexts.json", "assertions.json", "acronyms.json", "terms.json", "papers.json")

_SPINE = {"id", "class", "value", "provenance", "evidence_tag", "contexts", "certainty",
          "certainty_reasons", "fidelity", "reading_level", "prerequisites", "updated", "updated_reason"}
# DERIVED keys: computed by store/export.py from stored facts on every export
# (ADR-0004 A6 (e)). Known, so the rebuild accepts them; never written back,
# so a rebuilt store recomputes them and the round trip stays byte-identical.
DERIVED_KEYS = {"assertion": {"certainty_cap", "certainty_cap_reason"}}
PROBE_KEYS = ("publication_status", "version_of", "access_status", "affiliations")
KNOWN_KEYS = {
    "assertion": _SPINE | {"units", "rounding", "citation_context", "documents", "supports", "contradicts",
                           "derivation", "claim_type", "search_scope"} | DERIVED_KEYS["assertion"],
    "acronym": _SPINE | {"expansion", "plain_definition", "visual"},
    "term": _SPINE | {"plain_definition", "visual", "see_also"},
    # A paper's spine never carries certainty/fidelity/reading_level/
    # prerequisites today; insert_paper() cannot write them, so they are
    # NOT known keys for papers and would be refused rather than lost.
    "paper": {"id", "class", "value", "provenance", "evidence_tag", "contexts", "updated", "updated_reason",
              "tier", "citation", "access", "disposition", "evidence", "mined_by",
              "checked_against_source", "applicability", "yields",
              # ADR-0005 A4 (Sprint 6 Task E)
              "metadata_provider", "coi", "found_via", "read_extent", "source_links", *PROBE_KEYS},
}
_HAND_FROM = re.compile(re.escape(HAND_MARKER) + r"\s+([^)]*)\)")


class UnrestorableKey(ValueError):
    """An exported record carries a key the rebuild cannot put back."""


def _load(export_dir: Path, name: str) -> list[dict]:
    return json.loads((export_dir / name).read_text(encoding="utf-8"))


def _check_keys(records: list[dict], record_class: str) -> None:
    for r in records:
        unknown = set(r) - KNOWN_KEYS[record_class]
        if unknown:
            raise UnrestorableKey(
                f"{record_class} {r.get('id')!r} carries {sorted(unknown)}, which the rebuild does not "
                "know how to restore. Teach store/rebuild.py the field before the export ships it, "
                "or the export is no longer a complete artifact (ADR-0004 section 2)."
            )


def _extra_contexts(conn: sqlite3.Connection, record: dict) -> None:
    # insert_paper/insert_assertion write the primary (first) context only.
    for context_id in record["contexts"][1:]:
        conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, ?)", (record["id"], context_id))


def _spine_extras(conn: sqlite3.Connection, record: dict) -> None:
    for prereq in record.get("prerequisites", []):
        conn.execute("INSERT INTO prerequisites (record_id, prerequisite_id) VALUES (?, ?)", (record["id"], prereq))


def _paper_from_export(r: dict) -> PaperRecord:
    citation = r["citation"]
    if citation != r["provenance"]:
        raise UnrestorableKey(f"paper {r['id']!r}: citation differs from provenance; the store holds one copy")
    hand = HAND_MARKER in citation
    m = _HAND_FROM.search(citation) if hand else None
    return PaperRecord(
        id=r["id"], tier=r["tier"], access=r["access"], disposition=r["disposition"],
        context=r["contexts"][0], value=r["value"], citation=citation,
        citation_origin="hand" if hand else "api",
        citation_source="" if hand else REPLAY,
        hand_transcribed_from=(m.group(1).strip() if m else None),
        evidence_tag=r["evidence_tag"], evidence=r.get("evidence"), mined_by=r.get("mined_by"),
        checked_against_source=r.get("checked_against_source"),
        updated=r["updated"], updated_reason=r["updated_reason"],
        applicability=[(a["context"], a["rationale"]) for a in r.get("applicability", [])],
        metadata_provider=r.get("metadata_provider"), coi=r.get("coi"),
        found_via=[(v["route"], v.get("cited_as")) for v in r.get("found_via", [])],
        reads=[(d["reader"], d["read_on"], d["extent"], d.get("detail", "")) for d in r.get("read_extent", [])],
    )


def rebuild(export_dir: str | Path, db_path: str | Path, check_local_paths: bool = True) -> sqlite3.Connection:
    """Create a NEW store at db_path from the export in export_dir.

    create_store() refuses an existing path, so this never overwrites a
    store. All-or-nothing: one transaction, committed at the end."""
    export_dir = Path(export_dir)
    data = {name: _load(export_dir, name) for name in EXPORT_FILES}
    for name, record_class in (("assertions.json", "assertion"), ("acronyms.json", "acronym"),
                               ("terms.json", "term"), ("papers.json", "paper")):
        _check_keys(data[name], record_class)

    conn = create_store(db_path)
    try:
        # Contexts: the export is authoritative for the set and descriptions.
        exported = {c["id"]: c["description"] for c in data["contexts.json"]}
        for cid, desc in exported.items():
            conn.execute("INSERT INTO contexts (id, description) VALUES (?, ?) "
                         "ON CONFLICT(id) DO UPDATE SET description = excluded.description", (cid, desc))
        for (cid,) in conn.execute("SELECT id FROM contexts").fetchall():
            if cid not in exported:
                conn.execute("DELETE FROM contexts WHERE id = ?", (cid,))

        # Assertions first (papers yield them), relations after all exist.
        for r in data["assertions.json"]:
            insert_assertion(conn, AssertionRecord(
                id=r["id"], value=r["value"], provenance=r["provenance"], evidence_tag=r["evidence_tag"],
                context=r["contexts"][0], citation_context=r.get("citation_context"), units=r.get("units"),
                rounding=r.get("rounding"), documents=r.get("documents", []), certainty=r.get("certainty"),
                certainty_reasons=r.get("certainty_reasons"), fidelity=r.get("fidelity"),
                reading_level=r.get("reading_level"), updated=r["updated"], updated_reason=r["updated_reason"],
                derivation=r.get("derivation", ""), claim_type=r.get("claim_type", "positive"),
                search_scope=r.get("search_scope"),
            ))
            _extra_contexts(conn, r)
        for r in data["acronyms.json"] + data["terms.json"]:
            conn.execute(
                "INSERT INTO records (id, class, value, provenance, evidence_tag, certainty, certainty_reasons, "
                "fidelity, reading_level, updated, updated_reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (r["id"], r["class"], r["value"], r["provenance"], r["evidence_tag"], r.get("certainty"),
                 r.get("certainty_reasons"), r.get("fidelity"), r.get("reading_level"), r["updated"],
                 r["updated_reason"]))
            for context_id in r["contexts"]:
                conn.execute("INSERT INTO record_contexts (record_id, context_id) VALUES (?, ?)", (r["id"], context_id))
            if r["class"] == "acronym":
                conn.execute("INSERT INTO acronym_fields (record_id, expansion, plain_definition, visual) "
                             "VALUES (?, ?, ?, ?)", (r["id"], r["expansion"], r["plain_definition"], r.get("visual")))
            else:
                conn.execute("INSERT INTO term_fields (record_id, plain_definition, visual) VALUES (?, ?, ?)",
                             (r["id"], r["plain_definition"], r.get("visual")))
        for r in data["papers.json"]:
            insert_paper(conn, _paper_from_export(r), check_local_paths=check_local_paths)
            _extra_contexts(conn, r)
            for assertion_id in r.get("yields", []):
                conn.execute("INSERT INTO paper_yields (paper_id, assertion_id) VALUES (?, ?)", (r["id"], assertion_id))
            for key in PROBE_KEYS:
                if key in r:
                    p = r[key]
                    record_probe(conn, r["id"], key, p["value"], p["provider"], p["probed_on"], p.get("anchor"))

        # Cross-record links, now that every record exists.
        for r in data["assertions.json"]:
            for relation in ("supports", "contradicts"):
                for target in r.get(relation, []):
                    conn.execute("INSERT INTO assertion_relations (from_assertion_id, to_assertion_id, relation) "
                                 "VALUES (?, ?, ?)", (r["id"], target, relation))
        for r in data["papers.json"]:
            for link in r.get("source_links", []):
                add_source_link(conn, r["id"], link["to"], link["type"], link["evidence"])
        for r in data["terms.json"]:
            for target in r.get("see_also", []):
                conn.execute("INSERT INTO term_see_also (record_id, see_also_id) VALUES (?, ?)", (r["id"], target))
        for name in ("assertions.json", "acronyms.json", "terms.json", "papers.json"):
            for r in data[name]:
                _spine_extras(conn, r)
        conn.commit()
    except BaseException:
        conn.close()
        Path(db_path).unlink(missing_ok=True)
        raise
    return conn


def compare_exports(a: str | Path, b: str | Path) -> list[str]:
    """Names of export files that are not byte-identical between two dirs."""
    diffs = []
    for name in EXPORT_FILES:
        pa, pb = Path(a) / name, Path(b) / name
        if not pa.exists() or not pb.exists() or pa.read_bytes() != pb.read_bytes():
            diffs.append(name)
    return diffs


def rebuild_and_compare(export_dir: str | Path, check_local_paths: bool = True) -> list[str]:
    """Rebuild into a throwaway store, regenerate, and return the files that
    differ from export_dir. Empty list = the export is a complete artifact."""
    with tempfile.TemporaryDirectory() as tmp:
        conn = rebuild(export_dir, Path(tmp) / "rebuilt.db", check_local_paths=check_local_paths)
        try:
            regenerate(conn, Path(tmp) / "export")
        finally:
            conn.close()
        return compare_exports(export_dir, Path(tmp) / "export")
