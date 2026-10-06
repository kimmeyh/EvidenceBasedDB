#!/usr/bin/env python3
"""The one door: add a paper, book, reference or repository to the store
(Sprint 4 Task G, F25 C4/C5; design in docs/INTAKE_WORKFLOW.md).

Every source type converges on the same store-update step -- insert_paper()
with validate_paper()'s rules -- so the guards Task B built stand in front
of everything that enters, whether one record from the command line or
1,200 from a manifest.

DRY-RUN BY DEFAULT (QUALITY_STANDARDS.md): the record is derived from the
source of record (arXiv / Crossref / DataCite / GitHub) and pushed through
the door, and what WOULD be written is printed. `--apply` writes it and
regenerates export/.

    # one record, api-origin (id derived from the metadata unless --id is given)
    python scripts/intake.py arXiv:2602.11092 --context qml --tier screened \
        --disposition "Open-source framework paper ..." \
        --applicability qml="... -- arXiv abstract" --applicability method="... -- arXiv abstract"

    # a repository (kind inferred from the URL; disposition must start with "Code repository:")
    python scripts/intake.py https://github.com/merlinquantum/merlin --context qml \
        --disposition "Code repository: ..." --applicability qml="... -- GitHub repository description"

    # hand-origin (no resolvable id): a real local path, the visible marker, the page it was read from
    python scripts/intake.py "D:\\Data\\Harold\\EvidenceBasedDB\\References\\x.pdf | https://example.org/post" \
        --id author-2026-slug --kind reference --context qml --title "..." \
        --hand-citation 'Author, A., "Title," Site, 2026-09-01' --transcribed-from "p.1" \
        --disposition "Reference: ..."

    # bulk: a JSON list of the same fields; per-entry commit so a failure at
    # entry 700 keeps 699 and the re-run skips what already landed
    python scripts/intake.py --manifest intake.json [--apply]

    # the first-try check on an existing record (F10 protocol, mechanized)
    python scripts/intake.py --verify notton-2026-merlin-discovery-engine-photonic-hybrid

Kinds: paper (default) | book | reference | repo. Until `paper_fields.kind`
exists (a Class 1 schema decision recorded in docs/INTAKE_WORKFLOW.md), a
non-paper kind is named at the start of the disposition -- "Book:",
"Reference:", "Code repository:" -- and this script enforces that prefix.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import citations, connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.export import regenerate  # noqa: E402
from store.ingest import (  # noqa: E402
    DERIVED_BY_DOOR, HAND_MARKER, PaperRecord, _ANCHOR, _TIER_IN_TEXT, insert_paper, validate_paper,
)  # noqa: E402

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
FETCHER = None  # tests inject; the real run paces arXiv


def _fetcher():
    """FETCHER if a test injected one, else a PacedFetcher.

    Sprint 6 Task J (2026-10-04) found that a new pacer per entry never
    waited: 684 entries went to arXiv in 10 minutes against the team lead's
    6 s spacing. The fix that stays (retrospective I1 and I6, 2026-10-05) is
    in store/citations.py: every pacer shares ONE process-wide clock, so
    building a new one here is safe and no caller needs to hold a pacer."""
    return FETCHER if FETCHER is not None else citations.PacedFetcher()

# Sprint 6 Task J: with output redirected to a file, Windows encodes stdout as
# cp1252 and the first author named with a character outside it ("ś")
# stopped the sample dry run at entry 107 of 115.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

KIND_PREFIX = {"paper": None, "book": "Book:", "reference": "Reference:", "repo": "Code repository:"}
_STOP = {"a", "an", "the", "of", "for", "and", "in", "on", "with", "to", "using", "via", "from", "by", "at", "is", "are", "its"}
_DATE = None  # set per run


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def _slug(text: str, words: int) -> str:
    toks = [t for t in re.sub(r"[^a-z0-9]+", " ", _ascii(text).lower()).split() if t not in _STOP]
    return "-".join(toks[:words])


def make_id(md: citations.Metadata) -> str:
    """Deterministic id from the source of record: <family>-<year>-<five title words>;
    for a repository <owner>-<name>-github-repo."""
    if md.kind == "github":
        owner, _, name = md.ident.partition("/")
        return f"{_slug(owner, 3)}-{_slug(name, 3)}-github-repo"
    family = md.authors[0].split(",")[0] if md.authors else (md.extra.get("publisher") or "unattributed")
    return f"{_slug(family, 2)}-{md.year or 'nd'}-{_slug(md.title, 5)}"


def _parse_applicability(items) -> list[tuple[str, str]]:
    out = []
    for item in items or []:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            out.append((item[0], item[1]))
        elif isinstance(item, dict):
            out.append((item["context"], item["rationale"]))
        elif isinstance(item, str) and "=" in item:
            ctx, rationale = item.split("=", 1)
            out.append((ctx.strip(), rationale.strip()))
        else:
            raise ValueError(f"applicability entry {item!r}: expected CONTEXT=\"rationale -- anchor\"")
    return out


def build_record(entry: dict, fetcher=None, today: str = "") -> PaperRecord:
    """Entry -> validated PaperRecord (nothing written). Raises ValueError with the door's message."""
    access = entry["access"]
    kind = entry.get("kind") or ("repo" if (citations.parse_access(access) or ("",))[0] == "github" else "paper")
    if kind not in KIND_PREFIX:
        raise ValueError(f"kind must be one of {sorted(KIND_PREFIX)}, got {kind!r}")
    disposition = entry.get("disposition", "")
    prefix = KIND_PREFIX[kind]
    if prefix and not disposition.startswith(prefix):
        raise ValueError(f"a {kind} record's disposition must start with {prefix!r} until paper_fields.kind exists (docs/INTAKE_WORKFLOW.md)")
    common = dict(
        tier=entry.get("tier", "seen"), access=access, disposition=disposition, context=entry["context"],
        evidence=entry.get("evidence"), mined_by=entry.get("mined_by"), checked_against_source=entry.get("checked_against_source"),
        updated=today, updated_reason=entry.get("updated_reason") or f"{today}: added through scripts/intake.py ({kind})",
        applicability=_parse_applicability(entry.get("applicability")),
        # ADR-0005 A4 fields 1 and 8: the collection and locator this entry
        # came from, and how that collection cited it.
        found_via=[(entry["found_via"], entry.get("cited_as"))] if entry.get("found_via") else [],
        # ADR-0005 A4 (c): an entry at `read` carries how far it was read,
        # as [reader, read_on, extent, detail] rows.
        reads=[(r[0], r[1], r[2], r[3] if len(r) > 3 else "") for r in entry.get("reads", [])],
    )
    if citations.parse_access(access):
        md, rendered = citations.resolve(access, fetcher=fetcher or _fetcher())
        provider = md.extra.get("provider")
        if provider and md.kind == "arxiv" and not entry.get("updated_reason"):
            # Sprint 5 Task C: arXiv refused 73 of 75 paced requests and DataCite
            # answered; the render differs slightly by provider (no journal_ref),
            # so which source of record answered is part of the provenance.
            common["updated_reason"] += f"; metadata from {provider} (arXiv API did not answer)"
        paper = PaperRecord(id=entry.get("id") or make_id(md), value=entry.get("title") or md.title,
                            citation=rendered, citation_origin="api",
                            # This citation came from citations.resolve() one line above,
                            # so it carries the door's own marker, not a self-declaration.
                            citation_source=DERIVED_BY_DOOR, metadata_provider=citations.provider_of(md),
                            **common)
    else:
        if not entry.get("id"):
            raise ValueError("a hand-origin record needs --id (nothing to derive it from)")
        paper = PaperRecord(id=entry["id"], value=entry.get("title", ""), citation=entry.get("citation"),
                            citation_origin="hand", hand_transcribed_from=entry.get("transcribed_from"), **common)
    validate_paper(paper)
    return paper


def _describe(paper: PaperRecord) -> str:
    lines = [f"  id          : {paper.id}", f"  tier        : {paper.tier}", f"  origin      : {paper.citation_origin}",
             f"  title       : {paper.value}", f"  citation    : {paper.citation}", f"  access      : {paper.access}",
             f"  context     : {paper.context}", f"  disposition : {paper.disposition}"]
    for ctx, rationale in paper.applicability:
        lines.append(f"  applicability {ctx}: {rationale}")
    return "\n".join(lines)


def intake(conn, entries: list[dict], apply: bool, today: str, fetcher=None) -> tuple[int, int, list[str]]:
    """Returns (written_or_planned, skipped_existing, failures). Per-entry commit in --apply."""
    done = skipped = 0
    failures: list[str] = []
    for i, entry in enumerate(entries):
        label = entry.get("id") or entry.get("access", f"entry {i}")
        try:
            paper = build_record(entry, fetcher, today)
        except (ValueError, LookupError, KeyError, OSError) as ex:
            failures.append(f"{label}: {ex}")
            print(f"REFUSED {label}: {str(ex)[:200]}")
            continue
        if conn.execute("SELECT 1 FROM records WHERE id = ?", (paper.id,)).fetchone():
            skipped += 1
            print(f"PRESENT {paper.id} (skipped)")
            continue
        print(("WRITE  " if apply else "PLANNED") + f" {paper.id}")
        print(_describe(paper))
        if apply:
            insert_paper(conn, paper, fetcher=fetcher)  # citation already derived; validate runs again, cheaply
            conn.commit()
        done += 1
    return done, skipped, failures


def verify(conn, record_id: str, fetcher=None) -> list[tuple[str, bool, str]]:
    """The F10 protocol, mechanized: each check named, PASS or FAIL with a reason."""
    r = conn.execute(
        "SELECT r.id, r.value, r.provenance, r.updated, r.updated_reason, p.tier, p.access, p.disposition, p.evidence, "
        "p.mined_by, p.checked_against_source, (SELECT context_id FROM record_contexts c WHERE c.record_id = r.id LIMIT 1) AS context "
        "FROM records r JOIN paper_fields p ON p.record_id = r.id WHERE r.id = ?", (record_id,)
    ).fetchone()
    if r is None:
        return [("record exists", False, f"{record_id} not in the store")]
    checks: list[tuple[str, bool, str]] = [("record exists", True, record_id)]
    parsed = citations.parse_access(r["access"])
    if parsed:
        try:
            md, rendered = citations.resolve(r["access"], fetcher=fetcher or _fetcher())
            checks.append(("citation matches the source of record", rendered == r["provenance"],
                           "SAME" if rendered == r["provenance"] else f"DIFFERS: {rendered[:120]}"))
            checks.append(("title matches the source of record", md.title == r["value"], md.title[:80]))
        except Exception as ex:  # noqa: BLE001
            checks.append(("citation matches the source of record", False, f"could not resolve: {ex}"))
    else:
        checks.append(("hand-transcribed marker present", HAND_MARKER in (r["provenance"] or ""), r["provenance"][-60:]))
        local = r["access"].split(" | ", 1)[0]
        checks.append(("access is an existing local path", Path(local).exists(), local))
    checks.append(("disposition is one line and names no tier",
                   "\n" not in r["disposition"] and not _TIER_IN_TEXT.search(r["disposition"]), r["disposition"][:80]))
    app = conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?", (record_id,)).fetchall()
    unanchored = [a["context_id"] for a in app if not _ANCHOR.search(a["rationale"] or "")]
    checks.append(("every applicability rationale names its source anchor", not unanchored,
                   f"{len(app)} row(s)" + (f", unanchored: {unanchored}" if unanchored else "")))
    yields = conn.execute("SELECT COUNT(*) FROM paper_yields WHERE paper_id = ?", (record_id,)).fetchone()[0]
    if r["tier"] == "read":
        ok = bool((r["checked_against_source"] or "").strip()) and yields >= 1
        checks.append(("read tier: checked_against_source set and yields >= 1", ok, f"checked={r['checked_against_source']!r}, yields={yields}"))
    elif r["tier"] == "screened":
        checks.append(("screened tier: applicability derived (>= 1 row)", len(app) >= 1, f"{len(app)} row(s)"))
    else:
        checks.append(("seen tier: no further obligation", True, ""))
    checks.append(("value is the title, not the citation", bool((r["value"] or "").strip()) and r["value"] != r["provenance"], r["value"][:80]))
    return checks


def main(argv: list[str] | None = None) -> int:
    from datetime import date
    args = list(sys.argv[1:] if argv is None else argv)
    today = date.today().isoformat()
    apply = "--apply" in args
    if not DB_PATH.exists():
        print(f"error: {DB_PATH} does not exist.", file=sys.stderr)
        return 1

    def opt(name, default=None, multi=False):
        vals = []
        i = 0
        while i < len(args):
            if args[i] == name and i + 1 < len(args):
                vals.append(args[i + 1])
                del args[i:i + 2]
                continue
            i += 1
        return vals if multi else (vals[-1] if vals else default)

    verify_id = opt("--verify")
    manifest = opt("--manifest")
    if apply and not verify_id:
        backup_before_write(DB_PATH, "intake --apply")  # F30: verified backup, or no write at all
    conn = connect(DB_PATH)
    try:
        if verify_id:
            checks = verify(conn, verify_id)
            for name, ok, detail in checks:
                print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
            failed = [c for c in checks if not c[1]]
            print(f"\n{verify_id}: {len(checks) - len(failed)}/{len(checks)} checks passed")
            return 0 if not failed else 1
        if manifest:
            entries = json.loads(Path(manifest).read_text(encoding="utf-8"))
        else:
            entry = {
                "access": None, "id": opt("--id"), "kind": opt("--kind"), "context": opt("--context"),
                "tier": opt("--tier", "seen"), "disposition": opt("--disposition", ""), "title": opt("--title"),
                "citation": opt("--hand-citation"), "transcribed_from": opt("--transcribed-from"),
                "evidence": opt("--evidence"), "checked_against_source": opt("--checked-against-source"),
                "applicability": opt("--applicability", multi=True),
            }
            positional = [a for a in args if not a.startswith("--")]
            if len(positional) != 1 or not entry["context"]:
                print("usage: intake.py <access> --context CTX --disposition TEXT [--id ID] [--tier T] [--kind K] "
                      "[--applicability CTX=\"why -- anchor\"]... [--title T] [--hand-citation C --transcribed-from PAGE] [--apply]\n"
                      "       intake.py --manifest FILE [--apply]\n       intake.py --verify ID", file=sys.stderr)
                return 2
            entry["access"] = positional[0]
            entries = [entry]
        done, skipped, failures = intake(conn, entries, apply, today)
        if apply and done:
            regenerate(conn, EXPORT_DIR)
        verb = "written" if apply else "planned"
        print(f"\n{done} {verb}, {skipped} already present, {len(failures)} refused" + ("; export regenerated" if apply and done else ""))
        if not apply:
            print("PLANNED (dry run; nothing written). Re-run with --apply to write.")
        return 1 if failures else 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
