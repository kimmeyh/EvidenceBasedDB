#!/usr/bin/env python3
"""Sprint 12 Task A (F101): HTML entities out of stored citations, and the
Cyc quote made whole. INTAKE_WORKFLOW.md section 42.

(1) Every text field holding an HTML entity is unescaped: 4 records as of
2026-10-23, all "&amp;" from Crossref or DataCite (titles in `value`,
citations in `provenance`). The ids are keys and are not renamed. The
records are found by a scan, not by a list, so a record that gained an
entity later is caught too; `store.citations` now unescapes at the source.

(2) Every stored quote the quote pattern never parsed, made whole (Sprint
11 retrospective I1a's check over the whole store): `cyc-2007-eight-tactic-types`,
whose first quote held the source's own `"split" (`, and three Sprint 1
and 2 assertions whose quotes carried no anchor. Each is re-quoted from
its source with anchors, plus a quote for any figure the value states;
the values are unchanged. Lenat and Marcus 2023 had no local copy; `--fetch`
saves its free arXiv PDF (one paced request) and `--apply` adds it to the
record's access.

DRY RUN BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import html
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import AssertionRecord, append_updated_reason, sync_verified_assertion  # noqa: E402
from store.quotes import require_edit_basis, require_verbatim, source_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-23"
NOTE = f"{TODAY} (Sprint 12 Task A, F101): INTAKE_WORKFLOW.md section 42"

ENTITY = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")
# The record columns that hold source-derived text; ids and dates are keys.
ENTITY_COLUMNS = ("value", "provenance")

LENAT = "lenat-marcus-2023-trustworthy-ai"
LENAT_ARXIV = "2308.04445"
LENAT_PDF = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers"
                 r"\2023-08_Lenat_Getting-from-Generative-AI-to-Trustworthy-AI-What-LLMs-might.pdf")
TAYLOR_PDF = r"D:\Data\Harold\EvidenceBasedDB\Papers\2007-03_Taylor_Guiding-Inference-with-Policy-Search-Reinforcement-Learning.pdf"
PREREGISTRATION = r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\experiments\PREREGISTRATION.md"

# Each quote the quote pattern never parsed (section 42), made whole: record
# id -> (its source, [(passage, anchor), ...]). Every passage is verbatim in
# the source and is the edit's basis; the values are unchanged.
QUOTE_FIXES = {
    "cyc-2007-eight-tactic-types": (TAYLOR_PDF, [
        ("There are eight tactic types which describes the kind of operation to be performed, such as",
         "p.147; quoted in two parts around the source's own quoted word split, whose quotation marks would "
         "end the quote"),
        ("(i.e. split a conjunction into two sub-problems).", "p.147"),
        ("Of the eight tactic types available in ResearchCyc, the RL Tactician currently only handles five.",
         'p.148; the "fi" ligature normalized'),
        ("2007, American Association for Artificial Intelligence", "p.147, the copyright line; the year in the value"),
    ]),
    "cyc-general-prover-disabled": (str(LENAT_PDF), [
        ("over a million queries in a row that called on it, as a last resort, just timed out.", "p.14, footnote 9"),
        ("So, about one decade ago, we quietly turned the general theorem prover off, so it never gets called on!",
         "p.14, footnote 9"),
        ("July 31, 2023", "p.1, the paper's date; the year in the value"),
    ]),
    "heuristics-over-general-reasoning": (str(LENAT_PDF), [
        ("Cyc addresses this by separating the epistemological problem -- what does the system know? -- from the "
         "heuristic problem -- how can it reason efficiently?", "p.13"),
        ("Cyc also allows multiple redundant representations for each assertion, and in practice it uses multiple "
         "redundant, specialized reasoners -- Heuristic Level (HL) modules -- each of which is much faster than "
         "general theorem-proving when it applies.", "p.13"),
        ("By 1989, Cyc had 20 such high-level reasoners [Lenat&Guha 1990]; today it has over 1,100.", "p.13"),
        ("July 31, 2023", "p.1, the paper's date; the year in the value"),
    ]),
    "hsbc-b1-variable-count": (PREREGISTRATION, [
        ("B1's variable count read 78 in three places and 91 in two -- B1 ran the FULL pair build at k=13, which is "
         "91; 78 is the SEQUENTIAL count and belongs to the IEEE-CIS arm, and the B2/B1 ratio is 9.2x not 10.7x.",
         "PREREGISTRATION.md, amendment A30 of 2026-09-10"),
    ]),
}


def context_of(passages: list[tuple[str, str]]) -> str:
    return "; ".join(f'"{q}" ({anchor})' for q, anchor in passages)


def fetch_lenat() -> str:
    """The free arXiv copy of Lenat and Marcus 2023, through the door's paced
    fetcher (one request, 18 s rule); an existing file is never overwritten."""
    if LENAT_PDF.exists():
        return f"exists  {LENAT_PDF.name}"
    data = citations.PacedFetcher()(f"https://arxiv.org/pdf/{LENAT_ARXIV}", "application/pdf")
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"not a PDF: arXiv {LENAT_ARXIV}")
    LENAT_PDF.write_bytes(data)
    return f"saved   {LENAT_PDF.name}  SHA-256 {hashlib.sha256(data).hexdigest()}  {len(data):,} bytes"


def entity_rows(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(record id, column, stored text) for every record column holding an entity."""
    out = []
    for column in ENTITY_COLUMNS:
        for rid, text in conn.execute(f"SELECT id, {column} FROM records WHERE {column} LIKE '%&%;%'"):
            if text and ENTITY.search(text):
                out.append((rid, column, text))
    return out


def stored_assertion(conn: sqlite3.Connection, rid: str) -> AssertionRecord:
    r = conn.execute("SELECT value, provenance, evidence_tag, certainty, certainty_reasons, fidelity, reading_level "
                     "FROM records WHERE id = ? AND class = 'assertion'", (rid,)).fetchone()
    f = conn.execute("SELECT units, rounding, citation_context, derivation, claim_type, search_scope "
                     "FROM assertion_fields WHERE record_id = ?", (rid,)).fetchone()
    context = conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ? ORDER BY context_id",
                           (rid,)).fetchone()[0]
    return AssertionRecord(id=rid, value=r[0], provenance=r[1], evidence_tag=r[2], context=context,
                           certainty=r[3], certainty_reasons=r[4], fidelity=r[5], reading_level=r[6],
                           units=f[0], rounding=f[1], citation_context=f[2], derivation=f[3], claim_type=f[4],
                           search_scope=f[5])


def whole(conn: sqlite3.Connection, rid: str):
    """The assertion with its quotes made whole, and the check that licenses the write."""
    source, passages = QUOTE_FIXES[rid]
    wanted = stored_assertion(conn, rid)
    wanted.citation_context = context_of(passages)
    text = source_text(source)
    require_edit_basis(rid, None, [q for q, _ in passages], text)
    return wanted, require_verbatim(rid, wanted.citation_context, text, value=wanted.value)


def lenat_access(conn: sqlite3.Connection) -> str | None:
    """The Lenat and Marcus record's access with its local copy, or None when it already names it."""
    access = conn.execute("SELECT access FROM paper_fields WHERE record_id = ?", (LENAT,)).fetchone()[0]
    return None if str(LENAT_PDF) in access else f"{LENAT_PDF} | {access}"


def apply_changes(conn: sqlite3.Connection) -> list[str]:
    log = []
    for rid, column, text in entity_rows(conn):
        conn.execute(f"UPDATE records SET {column} = ? WHERE id = ?", (html.unescape(text), rid))
        append_updated_reason(conn, rid, f"{NOTE}: HTML escapes in {column} undone (from the metadata provider)",
                              TODAY)
        log.append(f"unescaped {rid}.{column}")
    access = lenat_access(conn)
    if access:
        conn.execute("UPDATE paper_fields SET access = ? WHERE record_id = ?", (access, LENAT))
        append_updated_reason(conn, LENAT, f"{NOTE}: local copy added to access", TODAY)
        log.append(f"{LENAT}: local copy added to access")
    for rid in QUOTE_FIXES:
        wanted, verified = whole(conn, rid)
        changed = sync_verified_assertion(conn, wanted, verified, f"{NOTE}: quote made whole", TODAY)
        log.append(f"{rid}: {', '.join(changed) if changed else 'already whole'}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        print(fetch_lenat())
        return 0
    conn = connect(DB_PATH)
    if "--apply" not in args:
        try:
            for rid, column, text in entity_rows(conn):
                print(f"would unescape {rid}.{column}: {text[:90]!r}")
            if lenat_access(conn):
                print(f"would add the local copy to {LENAT}'s access")
            for rid in QUOTE_FIXES:
                wanted, _ = whole(conn, rid)  # the checks the write runs; nothing written
                stored = stored_assertion(conn, rid).citation_context
                print(f"{rid}: {'already whole' if stored == wanted.citation_context else 'would sync citation_context'}")
        finally:
            conn.close()
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    conn.close()
    backup_before_write(DB_PATH, "F101 entities and the unparsed quotes")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
