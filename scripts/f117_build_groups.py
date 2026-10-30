#!/usr/bin/env python3
"""Sprint 14 Task E (F117): F114's cloud results, one file per paper, assembled into the group reader files the
applier reads (`manifests/sprint13_g_reads/group_<g>.json`, as Task G's were).

Each paper's entry is copied as its cloud session wrote it, in ledger order, with two changes:
- 22 results name a new assertion's id `id` instead of `id_suggestion` (the reader prompt's key), so `id` is
  renamed; where both are given they must agree;
- a new assertion's id that another paper in the build also suggests (each session saw only its own paper, so
  generic ids such as `conclusion-summary` repeat), or that the store already holds for another source, takes its
  paper's author and year as a prefix (`xu-2025-conclusion-summary`). The applier's ID_FIX is keyed by id across
  all groups, so it cannot tell two papers' same id apart; the rename is made here, before review, and listed.
A group is built only when every record of it has a result or is marked unread (UNREAD below); an existing group
file is never overwritten.

    python scripts/f117_build_groups.py            # list what would be built
    python scripts/f117_build_groups.py --write    # write the group files
"""
from __future__ import annotations

import functools
import importlib.util
import json
import re
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import script_paths  # noqa: E402

_, DB_PATH, _ = script_paths(__file__)
_spec = importlib.util.spec_from_file_location("f114_cloud", ROOT / "scripts" / "f114_cloud.py")
cloud = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cloud)

READS_DIR = ROOT / "manifests" / "sprint13_g_reads"
# Left out of its group, unread, with why. The team lead's mark on udaru (page images only), and four results whose
# file gave the reader nothing to read, kept unread on that precedent (the coordinator, 2026-10-30): each holds no
# assertion. abbas-2020-power-quantum-neural-networks is never launched in the cloud again (f114_cloud.UNREAD) but is
# read by Task F, so its group g079 waits for that read.
NO_TEXT = ("kept unread as udaru-2025-qml-credit-risk was (team lead, 2026-10-27), coordinator 2026-10-30 (Sprint 14 "
           "Task E): ")
UNREAD = {
    "udaru-2025-qml-credit-risk": cloud.UNREAD["udaru-2025-qml-credit-risk"],
    "mancilla-2026-spectra-datasets-substack": NO_TEXT + "its PDF's text layer carries no text (8 pages)",
    "qci-2026-entropy-computing-trade-magazine": NO_TEXT + "its PDF's text layer carries no text (6 pages)",
    "qci-research-an-open-quantum-system-for-discrete-optimization": NO_TEXT + "the saved web page holds only the "
                                                                     "site's menu and footer, not the article",
    "qci-research-white-paper-landmine-detection-using-quantum-photonic-vibrometer": NO_TEXT + "the saved web page "
                                                                     "holds only the title, menus and footer",
}


# Sprint 14 Task F (F114 at 50 papers): a paper read by a local reader is taken from its reader's group file
# (`local\reads\group_<g>.json`), the file the reader's full check passed, not its `done\` file, which a fix made
# after the check would not reach (review of 1cb63bb). Boyd's cloud result was labeled full and sampled the book (the
# team lead kept it unread, 2026-10-27), so only its local read counts. A record of a group F reads in part is left
# for F114's next release.
LOCAL = cloud.WORK / "local"
NOT_A_READ = {"boyd-2004-convex-optimization"}
NEXT_RELEASE = ("left for F114's next release: Sprint 14 Task F read 50 papers (Q1 = 2), and this group's other "
                "records were among them")


def local_reads() -> dict[str, Path]:
    """record -> the local reader's group file that holds it."""
    out: dict[str, Path] = {}
    for f in sorted((LOCAL / "reads").glob("group_g*.json")):
        for p in json.loads(f.read_text(encoding="utf-8"))["papers"]:
            if p["record_id"] in out:
                raise ValueError(f"{p['record_id']}: read by two local readers: {out[p['record_id']].name}, {f.name}")
            out[p["record_id"]] = f
    return out


def local_file(rid: str) -> Path | None:
    return local_reads().get(rid)


# A local reader's page anchors are set to the PDF page its quotes are on (review of g104: the readers' text layers
# had lost their page breaks, and anchors ran up to 15 pages off; Carlesso's cited the printed page numbers). A page
# is computed, never taken from the reader. Only quotes of 25 characters or more found on the PDF's pages count; an
# anchor each of whose found quotes is on a page it names is kept. Otherwise, an anchor with one page clause whose
# found quotes are each on one page takes those pages, listed where they are not one run; any other anchor loses its
# page clauses and keeps its sections. A "printed p.N" clause is not a PDF page and is left alone. Every change is
# listed (review of 11d443a: page lists, a range across sections, stray punctuation, an unfound quote). A list goes on
# only to a bare number that ends its clause, so "p.12, 4.3" keeps its section and "p.3, 2024 edition" its year; a
# range may say "to" or be compressed ("pp.112-15"); "Printed" and "printed:" are printed pages too (review of
# 8f2b408). A list may end its sentence with a period, and a "to" range ends its clause too, so "p.4 to 6 qubits" is
# one page and a count (review of aa8c75f).
_TO = r"(?:\s*[-–—]\s*|\s+to\s+)(?:pp?\.\s*)?"
_ENDS = r"(?!\.\d)(?=\s*(?:[,;.()\[\]]|\band\b|\bof\b|&|$))"
_PAGES = rf"\d+(?:\s*[-–—]\s*(?:pp?\.\s*)?\d+|\s+to\s+(?:pp?\.\s*)?\d+{_ENDS})?"
PAGE = re.compile(rf"(?:\b(?i:PDF|printed)[\s:]+)?(?:\b[Pp]p?\.|\b[Pp]ages?\b)\s*{_PAGES}"
                  rf"(?:\s*(?:,|\band\b|&)\s*{_PAGES}{_ENDS})*")
PAGE_NOTES: list[str] = []


def _numbers(clause: str) -> set[int]:
    out = set()
    for lo, hi in re.findall(rf"(\d+)(?:{_TO}(\d+))?", clause):
        if hi and int(hi) < int(lo):  # a compressed range: "112-15" is 112 to 115
            hi = lo[:len(lo) - len(hi)] + hi
        out.update(range(int(lo), int(hi or lo) + 1))
    return out


def _page_text(pages: list[int]) -> str:
    runs: list[list[int]] = []
    for n in pages:
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    parts = [f"{r[0]}-{r[-1]}" if len(r) > 1 else f"{r[0]}" for r in runs]
    return f"p.{parts[0]}" if len(pages) == 1 else f"pp.{', '.join(parts)}"


def _without_pages(anchor: str, clauses: list[re.Match]) -> str:
    s = anchor
    for m in reversed(clauses):  # a preposition that led into a page goes with it ("Theorem 2 on p.4")
        s = re.sub(r"\s+\b(?:on|at|in|see)\s*$", "", s[:m.start()]) + s[m.end():]
    s = re.sub(r"(?:\(\s*[,;]?\s*\)|\[\s*[,;]?\s*\])", "", s)
    s = re.sub(r"([(\[])\s*[,;]\s*", r"\1", s)
    s = re.sub(r"\s*[,;]\s*([)\]])", r"\1", s)
    s = re.sub(r"\s+([,;:)\]])", r"\1", s)
    s = re.sub(r"([,;])(?:\s*[,;])+", lambda m: ";" if ";" in m.group(0) else ",", s)
    s = re.sub(r"[,;]\s*\(", " (", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,;")
    return re.sub(r"(?:\s*\b(?:and|&)\s*)+$", "", s).strip(" ,;")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


@functools.cache
def pdf_pages(path: str) -> tuple[str, ...]:
    """The PDF's pages as pdftotext splits them (form feeds), each normalized."""
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, check=True).stdout
    return tuple(_norm(p) for p in out.decode("utf-8", "replace").split("\f"))


def fix_pages(rid: str, a: dict, pages: tuple[str, ...]) -> None:
    anchor = a.get("anchor") or ""
    clauses = [m for m in PAGE.finditer(anchor) if not m.group(0).lower().startswith("printed")]
    qs = [q for q in (_norm(x) for x in a.get("quotes") or []) if len(q) >= 25]
    every = [{i + 1 for i, t in enumerate(pages) if q[:80] in t} for q in qs]
    on = [s for s in every if s]
    if not clauses or not on:  # a quote not found is no evidence against the page
        return
    want = set().union(*(_numbers(m.group(0)) for m in clauses))
    if all(s & want for s in on):
        return
    aid = a.get("id_suggestion") or a.get("id")
    if len(clauses) == 1 and all(len(s) == 1 for s in on):
        m = clauses[0]
        pdf = "PDF " if m.group(0).lower().startswith("pdf") else ""
        # A quote not found may be on the pages named, so they are kept beside the computed ones.
        keep = want if len(on) < len(every) else set()
        new = anchor[:m.start()] + pdf + _page_text(sorted(set().union(*on) | keep)) + anchor[m.end():]
        a["anchor"] = new
        PAGE_NOTES.append(f"{rid}: {aid}: {anchor!r} -> {new!r}")
        return
    # No page can be computed for the anchor as written: its pages are dropped and it keeps its sections; an anchor
    # that would name nothing is left for the coordinator.
    bare = _without_pages(anchor, clauses)
    if not re.search(r"[A-Za-z]{3}", bare):
        PAGE_NOTES.append(f"{rid}: {aid}: anchor {anchor!r}, quotes on pages {[sorted(s) for s in on]}: left for "
                          "the coordinator")
        return
    a["anchor"] = bare
    PAGE_NOTES.append(f"{rid}: {aid}: {anchor!r} -> {bare!r} (pages dropped: quotes on {[sorted(s) for s in on]})")


def local_pdf(path: Path, rid: str) -> str:
    brief = LOCAL / "briefs" / f"{path.stem.removeprefix('group_')}.json"
    return next(r["file"] for r in json.loads(brief.read_text(encoding="utf-8"))["records"] if r["record_id"] == rid)


def local_unread() -> dict[str, str]:
    """The records of a group F's local briefs trim that have no cloud result."""
    ledger = json.loads(cloud.LEDGER.read_text(encoding="utf-8"))["groups"]
    cloud_have = {p.stem for p in (cloud.WORK / "results").glob("*.json")} - NOT_A_READ
    out = {}
    for brief in sorted((LOCAL / "briefs").glob("g*.json")):
        mine = {r["record_id"] for r in json.loads(brief.read_text(encoding="utf-8"))["records"]}
        for r in ledger.get(brief.stem, {}).get("records", []):
            if r["record_id"] not in mine and r["record_id"] not in cloud_have:
                out[r["record_id"]] = NEXT_RELEASE
    return out


UNREAD.update(local_unread())


def waiting() -> set[str]:
    """The groups with a local brief whose reader's group file does not exist yet, so a group is never built from a
    reader still at work."""
    return {b.stem for b in (LOCAL / "briefs").glob("g*.json")
            if not (LOCAL / "reads" / f"group_{b.stem}.json").exists()}


def entry(rid: str) -> dict:
    local = local_file(rid)
    path = local or cloud.WORK / "results" / f"{rid}.json"
    papers = json.loads(path.read_text(encoding="utf-8"))["papers"]
    if local:
        papers = [p for p in papers if p["record_id"] == rid]
    if [p["record_id"] for p in papers] != [rid]:
        raise ValueError(f"{rid}: its result holds {[p['record_id'] for p in papers]}")
    p = papers[0]
    if local:
        pages = pdf_pages(local_pdf(local, rid))
        for a in p.get("assertions", []) + p.get("existing", []):
            fix_pages(rid, a, pages)
    for a in p.get("assertions", []):
        if "id" in a:
            if a.setdefault("id_suggestion", a["id"]) != a["id"]:
                raise ValueError(f"{rid}: an assertion names two ids, {a['id']} and {a['id_suggestion']}")
            del a["id"]
    return p


def buildable(exclude: set[str] = frozenset()) -> dict[str, list[str]]:
    """group -> its records with a result, for every group from FIRST_GROUP whose records all have a result or
    are unread; groups in `exclude` are left out."""
    have = ({p.stem for p in (cloud.WORK / "results").glob("*.json")} - NOT_A_READ) | set(local_reads())
    wait = waiting()
    out = {}
    for g, v in sorted(json.loads(cloud.LEDGER.read_text(encoding="utf-8"))["groups"].items()):
        if g < cloud.FIRST_GROUP or g in exclude or g in wait:
            continue
        rids = [r["record_id"] for r in v["records"]]
        if all(r in have or r in UNREAD for r in rids) and any(r in have for r in rids):
            out[g] = [r for r in rids if r in have and r not in UNREAD]
    return out


def held_elsewhere(ids: set[str]) -> dict[str, str]:
    """id -> provenance, for each id the store holds as a record."""
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    try:
        return {i: row[0] or "" for i in ids
                if (row := conn.execute("SELECT provenance FROM records WHERE id = ?", (i,)).fetchone())}
    finally:
        conn.close()


def prefixed(rid: str, aid: str, taken: set[str]) -> str:
    """The paper's author and year before the id, with more of the record id until it is free."""
    words = rid.split("-")
    for n in range(2, len(words) + 1):
        new = f"{'-'.join(words[:n])}-{aid}"
        if new not in taken:
            return new
    raise ValueError(f"{rid}: no free id for {aid}")


def assemble(groups: dict[str, list[str]]) -> tuple[dict[str, list[dict]], list[str]]:
    """Every group's entries, with repeated and taken ids prefixed; the renames listed."""
    built = {g: [entry(r) for r in rids] for g, rids in groups.items()}
    count = Counter(a["id_suggestion"] for ps in built.values() for p in ps for a in p.get("assertions", []))
    stored = held_elsewhere(set(count))
    taken = set(count) | set(stored)
    renames = []
    for ps in built.values():
        for p in ps:
            rid = p["record_id"]
            for a in p.get("assertions", []):
                aid = a["id_suggestion"]
                if count[aid] > 1 or (aid in stored and rid not in stored[aid]):
                    a["id_suggestion"] = prefixed(rid, aid, taken)
                    taken.add(a["id_suggestion"])
                    renames.append(f"{rid}: {aid} -> {a['id_suggestion']}")
    return built, renames


def main(argv: list[str]) -> int:
    groups = buildable()
    built, renames = assemble(groups)
    for g, papers in built.items():
        path = READS_DIR / f"group_{g}.json"
        if path.exists():
            print(f"exists {path.name}")
            continue
        if "--write" in argv:
            path.write_text(json.dumps({"papers": papers}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{'wrote' if '--write' in argv else 'would write'} {path.name} ({len(papers)} records)")
    print("\n".join(f"rename {x}" for x in renames))
    print("\n".join(f"page   {x}" for x in PAGE_NOTES))
    print(f"{len(groups)} groups, {sum(map(len, groups.values()))} records, {len(renames)} ids prefixed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
